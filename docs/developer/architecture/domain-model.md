# Domain Model

> **Status:** Current as of S1 (`v0.1.0`); program presets updated in S4.1 (`v0.4.1`, D-061); envelope presets added in S6 (§5.1); program mix and building-level infiltration in D-124 ([ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)); end uses, heat fractions, people properties, thermostat sides, hot-water temperatures, the calendar, and dwelling counts in D-126 ([ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md)) · **Date:** 2026-10-02 · **Scope:** `Lod.Core.Common`, `Lod.Core.Schedules`, `Lod.Core.Loads`, `Lod.Core.Programs`, `Lod.Core.Envelope`, `Lod.Core.Aggregation`

This document describes the domain types that exist after stage S1 of the [implementation roadmap](../plans/2026-09-30-implementation-roadmap.md) and how they relate. S1 deliberately has no geometry: a zone appears only as a `ZoneId` and two measures (floor area and volume; S1 had a third, the exterior wall area, which left with infiltration in D-124). That is enough to define and test the aggregation rules (ADR-005, ADR-007) before any plan exists. Geometry, zones, surfaces, and the pipeline types arrive in S2 (§10).

All types live in `Lod.Core` (`netstandard2.0`, base class library only, no Rhino or Grasshopper reference) and are tested by `Lod.Core.Tests` on `net8.0` without Rhino.

## 1. Overview

```text
 Programs ─────────────────────────────────────────────────────────────────────────────
 PresetValues ─ToPreset()─► ProgramPreset ─1─► ZoneProgram ─0..*─► LoadDefinition ─1─► Schedule (Fraction)
 (plain values, S4.1)       Name, SpaceType?,  │                   Type, EndUse, Basis, Value   ├─0..1─► HeatFractions   (lighting, equipment)
                            WindowToWallRatio, │                   (D-126)                      └─0..1─► WaterTemperatures: Target, Inlet
                            Source?, Calendar? │                                                          (hot water; Schedule Temperature each)
                                               ├─1─► PeopleProperties: Activity (Schedule Activity), RadiantFraction, SensibleFraction
                                               ├─0..1─► ScheduleCalendar: Year, Holidays    (none for BEMGen's own presets)
                                               └─0..1─► Thermostat ─┬─0..1─► Schedule (Temperature)  heating setpoint
                                                                    └─0..1─► Schedule (Temperature)  cooling setpoint (at least one)
                                                none = unconditioned zone, no setpoints
 ProgramMix.Mix(presets, weights, ...) ─► ProgramPreset          (D-124: zone merge of a virtual unit-area zone)
 No infiltration here: it is an input of the envelope preset (§5.1).

 Traceability ─────────────────────────────────────────────────────────────────────────
 LoadDefinition.Aggregation ─┐
 Schedule.Aggregation ───────┴─0..1─► AggregationRecord: Method, Sources (ZoneId[]), Weights (double[])
                                      sources are zones, or for a program mix its inputs Input.k (§9)

 Aggregation ──────────────────────────────────────────────────────────────────────────
 target ZoneId + target ZoneMeasures ──┐
 SourceZoneContribution[] ─────────────┼─► IEquivalentPropertyAggregator.Aggregate ─► Result<ZoneProgram>
   Zone (ZoneId), Program (ZoneProgram)│     implemented by EquivalentPropertyAggregator(ToleranceSettings),
   Measures (ZoneMeasures),            │     which uses DesignMagnitudes (value ↔ magnitude)
   AreaFraction ───────────────────────┘

 Common ───────────────────────────────────────────────────────────────────────────────
 Result<T>: Value + Diagnostics (Info, Warning)  |  Diagnostics with at least one Error
 Diagnostic: Severity, Code (DiagnosticCodes), Message, Subject
 ToleranceSettings: Distance, RelativeArea, RelativeLoad, AbsoluteSchedule, Angle, AbsoluteFraction (D-126)
 GeometryLimits: MinimumWindowWallLength, MinimumWindowWidth, MinimumWindowHeight (S8.1)
```

Inputs flow left to right: schedules build loads, thermostats, and people properties, loads, people properties, and an optional thermostat build a zone program (conditioned when it has a thermostat), and a zone program and a window-to-wall ratio build a program preset. The aggregator takes the programs of several source zones and returns the program of one target zone, built from the same types, with every derived load and schedule carrying an `AggregationRecord`.

## 2. Common (`Lod.Core.Common`)

**`ToleranceSettings`** is the only place where numerical tolerances are defined (GLOBAL.md quality rule 4, ADR-004). Its constructor rejects values that are not positive and finite with an `ArgumentOutOfRangeException`. `ToleranceSettings.Default`:

| Property | Default | Used for |
| --- | --- | --- |
| `Distance` | 1e-6 m | Geometric distances. `DecimalPrecision` (6) is the matching number of decimal places, the polygon-clipping precision from S2. |
| `RelativeArea` | 1e-6 | Area and volume comparisons (`AreaEquals`); also the slack allowed on transfer fractions by the aggregator. |
| `RelativeLoad` | 1e-9 | Load, occupancy, and air-flow comparisons (`LoadEquals`). |
| `AbsoluteSchedule` | 1e-9 | Schedule value comparisons (`ScheduleEquals`). |
| `Angle` | 1e-6 rad | Angular comparisons. |
| `AbsoluteFraction` | 1e-9 | Sums of dimensionless fractions, compared absolutely: a load's heat fractions sum to at most 1 (D-126, [ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md)). |

Relative comparisons use a floor of 1, `|a − b| ≤ rel · max(1, |a|, |b|)`, so values near zero are compared absolutely.

**`GeometryLimits`** (S8.1, ADR-011) is the only place where the minimum wall and window geometry of the plan generators is defined: `MinimumWindowWallLength` 1 m, `MinimumWindowWidth` 0.3 m, and `MinimumWindowHeight` 0.3 m in `GeometryLimits.Default`. It is an immutable record whose constructor rejects values that are not positive and finite with an `ArgumentOutOfRangeException`. `PlanGenerator` takes it through its constructor (the default when omitted) and records non-default limits in the plan's provenance. An outdoor wall or window below a limit gets no window and the info `WindowOmitted`; the limits do not apply to rebuilt walls (ADR-012).

**`Diagnostic`** is a structured message (GLOBAL.md quality rule 5): `Severity` (`Info`, `Warning`, `Error`), a stable `Code` from `DiagnosticCodes`, an actionable `Message`, and an optional `Subject` (for example a zone ID). Codes are never reused or renamed; a removed code's name is not reused (S4.1 removed `DuplicateSpaceType`, D-064). §8 lists the S1 codes.

**`Result<T>`** is the outcome of an operation whose failure is expected. A success carries a value and may carry `Info` and `Warning` diagnostics, never errors; a failure carries at least one `Error` and no value. Reading `Value` on a failure throws an `InvalidOperationException` listing the diagnostics. The static `Result` class creates results: `Success`, `Failure`, and `FromDiagnostics`, which builds the value only when the collected diagnostics contain no error. Every S1 factory that validates input (`Schedule.Create`, `Schedule.Constant`, `Schedule.FromDailyProfiles`, `LoadDefinition.Create`, `Thermostat.Create`, `ZoneProgram.Create`, `ProgramPreset.Create`) returns a `Result<T>`, and so do `PresetValues.ToPreset` (S4.1) and the aggregator.

**`ZoneId`** is a strongly typed zone identifier (`readonly record struct` over a string). It is the only identifier in S1; S2 adds identifiers for surfaces.

## 3. Schedules (`Lod.Core.Schedules`)

**`Schedule`** is an immutable series of `Schedule.HoursPerYear` = 8760 hourly values for a non-leap year (ADR-003), with a `Name`, a `ScheduleKind`, and an optional `AggregationRecord`.

- `ScheduleKind.Fraction`: dimensionless values in [0, 1] that multiply a load's design magnitude.
- `ScheduleKind.Temperature`: finite values in °C, used for setpoints and hot-water temperatures.
- `ScheduleKind.Activity` (D-126): finite values of at least 0 in W per person, the activity level of the occupants; appended, so the earlier kinds keep their values.

`Schedule.Create` validates the name (`EmptyName`), the length (`ScheduleLength`), and the values (`ScheduleValue`, reporting the first invalid hour). `Schedule.Constant` repeats one value. `Schedule.FromDailyProfiles` repeats a 24-hour weekday profile Monday to Friday and a weekend profile on Saturday and Sunday, starting from a given weekday for 1 January; holidays are not modelled by this factory. Values are read with the indexer `schedule[hour]` (0-based) or as `Values`.

**`ScheduleCalendar`** (D-126) is the calendar a program's schedules were expanded on: a non-leap `Year` (1 to 9999; a leap year is `CalendarYear`, since schedules hold 8760 values) and its distinct `Holidays` as `MonthDay` values, in date order (a date the year lacks, or a repeated one, is `CalendarHoliday`). `FirstDayOfYear` is the weekday of 1 January and `IsHoliday(dayOfYear)` tests a 0-based day. Two calendars are equal when their years and holidays are. BEMGen's own presets have no calendar (`null`) and assume a year whose 1 January is a Monday (`DefaultFirstDayOfYear`, with `DefaultYear` 2007 for the one the IDF writer then uses). `Agree(...)` gives the one calendar a set of programs shares: all non-null calendars equal, and a `null` calendar agreeing only with one that starts on a Monday; otherwise `CalendarMismatch` naming the subjects. `Describe()` prints it, for example `2007 (1 January a Monday), holidays 01-01, 12-25`.

## 4. Loads (`Lod.Core.Loads`)

**`LoadDefinition`** is one load of a program: a `LoadType`, an `EndUse`, a `LoadBasis`, a design `Value` in that basis, a fraction `Schedule`, for lighting and equipment loads their `HeatFractions`, for hot-water loads their `WaterTemperatures`, and an optional `AggregationRecord`. Its design magnitude is `Value` × basis quantity (ADR-007).

| `LoadType` | Design magnitude |
| --- | --- |
| `Occupancy` | people |
| `Lighting`, `ElectricEquipment`, `GasEquipment` | W |
| `DomesticHotWater` (peak flow), `Ventilation` | m³/h |

Infiltration is not a program load (D-124, [ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)): its magnitude follows the envelope, which a program does not know, so it is an input of the envelope preset (§5.1). `LoadType.Infiltration` and `LoadBasis.PerExteriorWallArea` no longer exist.

| `LoadBasis` | Basis quantity of a zone |
| --- | --- |
| `PerFloorArea` | floor area, m² |
| `PerPerson` | design occupants, the summed magnitude of the zone's occupancy loads |
| `Absolute` | 1 |
| `AirChangesPerHour` | air volume, m³ (value in 1/h, magnitude in m³/h) |
| `PerDwellingUnit` (D-126) | the zone's dwelling count (`ZoneMeasures.DwellingUnits`) |

`LoadDefinition.Create` rejects a load type or basis that is not defined, such as a value cast from the removed infiltration type or exterior-wall basis (`UndefinedLoadKind`; the message says to set infiltration on the envelope preset), negative or non-finite values (`LoadValue`), occupancy expressed other than `PerFloorArea`, `Absolute`, or `PerDwellingUnit` (`LoadBasisNotAllowed`), non-fraction schedules (`ScheduleKindMismatch`), an end use that is empty or white space (`EmptyName`), heat fractions on a type that has none or with a non-zero field its EnergyPlus object lacks (`HeatFractionNotSupported`), and water temperatures on a type other than hot water (`WaterTemperaturesNotAllowed`).

**`LoadEndUses`** (D-126) names the default end use of each type, the names the program JSON contract uses: `occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water`, `ventilation`. `LoadDefinition.EndUse` is the default of its type unless given (for example `additional_lighting`), and `HasDefaultEndUse` tells which. End uses are compared ignoring case wherever they are keys (`LoadEndUses.Comparer`: a program's uniqueness, the aggregator's components, which keep the spelling of the first source, conservation, the IDF names, and the importer's override matching), so `Lighting` and `lighting` are one end use. **`LoadComponent`** is the key of a load: type, end use, and basis, ordered in that sequence (end uses ignoring case, then ordinally); a program holds at most one load per component, the aggregator merges and the validator checks each component on its own, and the IDF names a load with its end use when the zone holds more than one end use of its type.

**`HeatFractions`** (D-126) are the fractions of a lighting, electric equipment, or gas equipment load's heat that are radiant, latent, lost, visible, and return air; `Convective` is what remains. Each lies in [0, 1] (`HeatFractionValue`) and the sum is at most 1 within `ToleranceSettings.AbsoluteFraction` (`HeatFractionsExceedOne`). EnergyPlus `Lights` has no latent or lost field and `ElectricEquipment` and `GasEquipment` no visible or return-air field, so a non-zero value there is `HeatFractionNotSupported`. `DefaultFor(type)` gives the values the IDF writer always used (lighting radiant 0.42 and visible 0.18; electric equipment radiant 0.5; gas equipment radiant 0.3; every other fraction 0), which a load takes when none is given, and `WithOverrides` builds fractions from optional per-field values for the components' inputs.

**`WaterTemperatures`** (D-126) hold the target (mixed-water) and the inlet (cold-water supply) temperature of a hot-water load as `Temperature` schedules in °C, the target never below the inlet in any hour by more than `ToleranceSettings.AbsoluteSchedule` (`WaterTargetBelowInlet`; `Create` and `WithOverrides` take the tolerances, `ToleranceSettings.Default` when not given). The default is constant 60 and 10 °C, named `BEMGen Hot Water Target Temperature` and `BEMGen Hot Water Inlet Temperature`. `WithOverrides` builds them from optional schedules for the components' inputs.

## 5. Programs (`Lod.Core.Programs`)

**`SpaceType`** is the semantic category of a space: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, `Mixed` for a simplified zone that combines several space types, and since S8.4 the non-residential departments `Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, and `ActivityHall`, appended so that existing values keep their order ([ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md)). A non-residential zone is one department, never a room (D-097). Semantics are explicit data, never encoded in layer names, colours, or wire structure (AGENTS.md).

**`Thermostat`** holds the `HeatingSetpoint` and `CoolingSetpoint` schedules of a conditioned zone; since D-126 each is optional (`null` is a side that is off, `HasHeating` and `HasCooling` tell which), at least one is needed (`NoSetpoint`), and where both exist the heating setpoint never exceeds the cooling setpoint at any hour by more than `AbsoluteSchedule` (`SetpointsCross`; `Create` and `ForSides` take the tolerances, `ToleranceSettings.Default` when not given). `Thermostat.Create` also rejects setpoints that are not temperature schedules (`ScheduleKindMismatch`). `Thermostat.ForSides(conditioned, heatingOn, heating, coolingOn, cooling)` builds the thermostat from a preset component's inputs: a side is on when the space is conditioned, its switch is on, and it has a schedule; a switch that is on without a schedule gives an info, and both sides off in a conditioned space is `NoSetpoint`.

**`ZoneProgram`** is the energy-relevant program of a zone: `Loads`, ordered by `LoadType`, then end use, then `LoadBasis`, with at most one load per type, end use, and basis (D-126; D-047 said type and basis), the occupants' `People`, an optional `Thermostat`, and the optional `Calendar` its schedules were expanded on. A load type may appear in several bases, for example ventilation per person plus per floor area, and in several end uses, for example lighting and additional lighting; these components add up (D-047). Conditioning comes from the program (D-038): a program with a thermostat is conditioned (`IsConditioned`); one without a thermostat is unconditioned and has no setpoints. `Find(LoadType, LoadBasis, endUse)` returns a load (the type's default end use when none is named) or `null`. `ZoneProgram.Create(loads, thermostat, people, calendar)` rejects the same load type with the same end use in the same basis twice (`DuplicateLoadType`) and per-person loads without an occupancy load (`PerPersonWithoutOccupancy`); `people` and `calendar` are optional. The same type describes an input program and an aggregated one; only the `AggregationRecord`s on its loads and schedules tell them apart.

**`PeopleProperties`** (D-126) hold how the occupants of a zone give off heat: `Activity`, an `Activity` schedule in W per person; `RadiantFraction` of the sensible heat in [0, 1]; and `SensibleFraction`, a `SensibleHeatFraction` that is a number in [0, 1] or `autocalculate` (`PeopleFraction` for a value outside, or text that is neither). `PeopleProperties.Default` holds what the IDF writer always used: constant 120 W per person named `BEMGen Activity Level`, 0.3, and `autocalculate`; every `ZoneProgram` has people properties, the default unless given. `SensibleHeatFraction.Parse` reads the text of a component input, and `ToString()` gives the number or `autocalculate`.

**`ProgramPreset`** is the program of one space type (D-024): `Name`, `SpaceType`, `Program`, `WindowToWallRatio` in [0, 1) (D-026; `EmptyName`, `WindowToWallRatio`), `Calendar` (the program's), and `Source` (`Provenance?`, D-124, D-126), where the values came from: `null` for a preset built from plain values, such as the examples, and the record of the source, the conversions, or the mix for others. A plan records the distinct sources of its presets among its provenance inputs, and `AsAnyProgram()` keeps the source. `SpaceType` is `SpaceType?` since S8.8 (D-108, ADR-014): `Create` always gives a space type, and `AsAnyProgram()` returns the same preset without one (`IsAnyProgram`), keeping the name, the same `Program`, and the WWR; a plan generator accepts such a preset on every preset input, and its zones keep the generator's space type. The name is descriptive only: it appears in reports, provenance, and messages and is never used for matching (D-061). Until S4.1 a `ProgramPresetSet` grouped presets by space type; since S4.1 a plan generator takes a typed record with one preset per space type instead (`PlanPresets`, see [pipeline](pipeline.md#2-plan-generation)), and the set and its code `DuplicateSpaceType` are gone.

**`PresetValues`** (S4.1) holds the plain values a preset is built from: `Name`, `SpaceType`, `WindowToWallRatio`, `Conditioned`, constant `HeatingSetpoint` and `CoolingSetpoint` in °C, the switches `HeatingOn` and `CoolingOn` (default true, D-126), and `Loads`, each a **`PresetLoadValue`** (`Type`, `Basis`, `Value`, fraction `Schedule`). Change a value with a `with` expression. `ToPreset()` builds the loads (with the default end uses, heat fractions, and water temperatures), a thermostat of constant temperature schedules named `"{Name} Heating Setpoint"` and `"{Name} Cooling Setpoint"`, one for each side that is on, when `Conditioned` (the setpoints are ignored otherwise; both sides off is `NoSetpoint`), the zone program, and the preset, and returns every error of these factories together.

**`ExampleResidentialPresets`** provides illustrative presets for dwelling unit, corridor, and stair; the dwelling unit and corridor are conditioned and the stair is not. Each is available as `PresetValues` (`DwellingUnitValues`, `CorridorValues`, `StairValues`) and as the `ProgramPreset` built from them (`DwellingUnit`, `Corridor`, `Stair`). Their values and conditioning are round-number choices for development and tests, not DOE prototype values; see [program presets](../research/program-presets.md). Since D-124 they have no infiltration load.

**`ExampleNonResidentialPresets`** (S8.4) provides illustrative presets, all conditioned, for the fifteen space types of the non-residential departments (ADR-014): `OfficeValues`/`Office`, `CoreValues`/`Core`, … `ServiceValues`/`Service`; `SpaceTypes` lists the types and `ValuesOf` and `PresetOf` look a type up (`ArgumentOutOfRangeException` for any other type). The retail schedules have their own Saturday and Sunday profiles. The values are illustrative, not sourced (D-023).

**`ProgramMix`** (D-124, [ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)) mixes program presets by floor-area share: `ProgramMix.Mix(presets, weights, name, spaceType, windowToWallRatio, tolerances)` returns a `Result<ProgramPreset>` and is the service behind *Mix Programs*. It is the zone merge of §6 applied to one virtual zone of floor area 1 and volume 1: input *i* is a source of floor area and volume ŵᵢ, its normalised weight, with area fraction 1, so every basis follows the rule zone merges use (the table is in [program presets](../research/program-presets.md#6-mixed-presets-d-124) §6). Weights are one per preset, each finite and greater than 0 (`MixWeight`), and are normalised to sum to 1; absolute loads are summed raw; the result is conditioned when any input is, with setpoints over the conditioned inputs only. `name` defaults to `Mix of A 0.7, B 0.3` (names and normalised weights, three significant digits); `spaceType` defaults to that of the input with the largest weight, the first on a tie, and an any-program input chosen so gives an any-program mix; `windowToWallRatio` defaults to the weighted mean Σ ŵᵢ·WWRᵢ. Per-dwelling loads mix like per-floor-area loads, each weight standing for the input's share of dwellings (the virtual zone has ŵᵢ dwellings per input); heat fractions, people properties, and water temperatures follow the zone-merge rules of §6.2; the inputs' calendars must agree (`CalendarMismatch`) and the mix carries the shared one. A per-person load beside absolute occupancy in any inputs is the error `PerPersonWithAbsoluteOccupancy`; occupancy in more than one basis (per floor area, per dwelling unit, absolute) with a per-person load in any input, or with different people properties among the inputs with occupants, is the error `MixedOccupancyBases`; and conditioned beside unconditioned inputs the info `MixedConditioning`. The result's `Source` is the operation `MixPrograms` with one parameter `Input.k` per input (its name, given weight, and normalised weight), the chosen space type and WWR with how each was chosen, and the inputs' own sources as its inputs.

### 5.1 Envelope (`Lod.Core.Envelope`, S6)

The envelope is separate from the programs: it is the same at every level of detail, so geometry effects are not confounded with envelope changes (GLOBAL.md scientific rule 4, [ADR-010](../decisions/ADR-010-convert2idf.md)). Values and reasons: [envelope presets](../research/envelope-presets.md).

```text
 EnvelopeValues ─ToPreset()─► EnvelopePreset ─7─► Construction (one per ConstructionRole) ─1..10─► Layer
 (plain values)               Name             ├─1─► GlazingSpec (the window)
                                               └─1─► Infiltration: DesignRate, Basis, Schedule (Fraction), D-124
 Surface + ExportedBoundary ─ConstructionRoles.Of─► ConstructionAssignment(Role, Reversed) ─EnvelopePreset.For─► Construction
```

- **`Layer`** (record): `Name`, `Thickness` (m), `Conductivity` (W/(m·K)), `Density` (kg/m³), `SpecificHeat` (J/(kg·K)); `ThermalResistance` = thickness / conductivity.
- **`Construction`**: `Name` and `Layers` from the outside to the inside (copied when created); `ThermalResistance` (layers only, no surface films), `IsSymmetric`, and `Reversed()`, the layers in reverse order named `"{Name} Reversed"`, or the construction itself when it is symmetric.
- **`GlazingSpec`** (record): `Name`, `UFactor` (W/(m²·K)), `SolarHeatGainCoefficient`, `VisibleTransmittance` of a simple glazing system.
- **`ConstructionRole`**: `ExteriorWall`, `Roof`, `GroundFloor`, `ExposedFloor`, `InteriorWall`, `InteriorFloor`, `InternalMass`. **`ConstructionAssignment`**: a role and whether the surface uses the role's construction reversed (the ceiling below an interior floor).
- **`Infiltration`** (record, D-124): the building's infiltration, the same for every zone: `DesignRate` (finite, not negative), `Basis` (`InfiltrationBasis`), and a fraction `Schedule`. `PerExteriorSurfaceArea` is m³/h per m² of the zone's outdoor walls, roofs, and exposed floors, windows included (EnergyPlus `Flow/ExteriorArea`); `PerExteriorWallArea` is m³/h per m² of its outdoor walls (`Flow/ExteriorWallArea`); `AirChangesPerHour` is 1/h of its volume (`AirChanges/Hour`). It is not part of a program because a program has no walls or roofs, and no zone merge aggregates it: each converter applies it to each target zone's own surfaces or volume. `Check()` reports a negative or non-finite rate or an undefined basis (`InfiltrationValue`) and a schedule that is not a fraction schedule (`ScheduleKindMismatch`).
- **`ZoneInfiltration`** in `Lod.Core.Conversion` (D-124) gives the quantities the infiltration is applied to in one zone, the ones EnergyPlus uses: `ExteriorSurfaceArea` (the gross area of the zone's surfaces with boundary `Outdoors`: walls, roofs, and exposed floors; not ground or adiabatic surfaces), `ExteriorWallArea`, and `DesignFlow(infiltration, zone, surfaces)`, the design flow of one instance of the zone in m³/h at a schedule fraction of 1 (before the zone multiplier). *Convert2BEM* outputs it.
- **`EnvelopeValues`** (record): the preset name, one construction per role, the window, and the infiltration; `ToPreset()` calls `EnvelopePreset.Create`, which reports every error at once: `EmptyName`, `EnvelopeValue` (a layer property not positive and finite; a U-factor not in (0, 7], an SHGC or visible transmittance not in (0, 1)), `InfiltrationValue` (and `ScheduleKindMismatch` for its schedule), `ConstructionLayers` (not 1 to 10 layers), `DuplicateEnvelopeName` (a material or construction name, compared ignoring case, given to two different materials or constructions; the glazing name counts as both), and `EnvelopeName` (a name longer than 100 characters, the generated reverses included, or with `,` `;` `!`). A layer used by several constructions is checked once.
- **`EnvelopePreset`**: the values, `For(role)` and `For(assignment)`, `Constructions` (each once: the roles' constructions, then the reverses of the interior wall and floor where they differ), and `Materials` (each layer once). **`ExampleEnvelopePresets`** holds one illustrative preset, `Values` and `Example`, not taken from any standard (D-023); its infiltration is 0.3 air changes per hour, always on.
- **`ConstructionRoles.Of(surface, boundary)`** in `Lod.Core.Conversion` maps a surface and the boundary a converter writes for it to a `Result<ConstructionAssignment>`: the wall between two zones whose zone ID sorts after the adjacent zone's (ordinal) is reversed, as is every ceiling between storeys, so the two sides of a surface between zones list the layers in opposite order; an unresolved boundary and a wall or ceiling on the ground, which no floor aggregator produces, give the error `NoConstructionRole`.

## 6. Aggregation (`Lod.Core.Aggregation`)

### 6.1 Inputs

**`ZoneMeasures`** holds the quantities that load bases refer to: `FloorArea` (m²), `Volume` (m³), and, since D-126, `DwellingUnits` (default 0): the number of dwellings, 1 for a generated zone of space type `DwellingUnit` (a dwelling is one zone, never subdivided, D-009), 0 for any other generated zone, and Σ fᵢ·Nᵢ of its sources for a target zone, so fractional after a split (`Zone.DwellingUnits` holds it for zones). `IsValid` is true when all are finite and non-negative. No load basis depends on the envelope any more, so the exterior wall area of S1 to S8 is gone (D-124).

**`SourceZoneContribution`** describes what one source zone gives to one target zone: the source's `Zone` ID, `Program`, and whole-zone `Measures`, plus one fraction in [0, 1]:

- `AreaFraction`: the share of the source's floor area assigned to the target. It also transfers the same share of volume, occupants, and absolute loads.

The aggregator does not compute this fraction. The caller supplies it, so the aggregator is independent of geometry and of any rezoning method (spec §9); from S3 the transfer matrix computes it for the plan simplifiers. Through S8 a second fraction, `ExteriorWallFraction`, transferred loads per exterior wall area, computed by the façade attribution; it left with infiltration (D-124), and the façade attribution now only checks the façade coverage. `ProgramMix` supplies one source per input, with area fraction 1 (§5).

**`DesignMagnitudes`** converts between a load's value and its absolute design magnitude: `BasisQuantity(basis, measures, occupants)`, `Occupants(program, measures)` (the summed magnitude of the occupancy loads, 0 without one), and `Of(load, measures, occupants)`.

### 6.2 Rules

`IEquivalentPropertyAggregator.Aggregate(target, targetMeasures, sources)` returns the target's `ZoneProgram`. `EquivalentPropertyAggregator` implements ADR-007 for loads and ADR-005 for setpoints, and the rules of D-126 (ADR-018) for the properties that came with program JSON. Loads are aggregated per component, a load type with one end use in one basis (D-047, D-126). For each component defined by at least one source, with *i* running over the sources that define it:

```text
Qᵢ     = valueᵢ · Bᵢ                 design magnitude of source i (people, W, or m³/h); Bᵢ is its basis quantity
Tᵢ     = fᵢ · Qᵢ                     transferred magnitude; fᵢ = AreaFraction
Q*     = Σ Tᵢ                        target design magnitude (conserved)
value* = Q* / B*                     B* is the target's quantity of the component's basis, from targetMeasures
s*(t)  = Σ Tᵢ · sᵢ(t) / Q*           target schedule, so that Q* · s*(t) = Σ Tᵢ · sᵢ(t) at every hour t
```

One rule covers every basis: it is area weighting for per-floor-area loads, volume weighting for air changes per hour (D-019), occupancy weighting for per-person loads, dwelling-count weighting for per-dwelling loads (value* = Σ fᵢ·Nᵢ·vᵢ / Σ fᵢ·Nᵢ, because B* is the target's dwelling count), and summation for absolute loads. Occupancy is aggregated first (it is the first `LoadType`, and occupancy is never per person), and the target's design occupants (the sum of its conserved occupancy components) are the basis quantity of per-person loads. The target program contains the union of the sources' components, ordered by `LoadType`, then end use, then `LoadBasis`; components with different end uses are never merged with each other. Sources that express one load type in different bases are not an error: each basis is aggregated as its own component, neither rejected nor converted to another basis, and a source without a component contributes nothing to it.

Conditioning and setpoints follow ADR-005 and D-038. The target is conditioned when at least one conditioned source contributes floor area to it (`AreaFraction > 0`): "any conditioned wins". Otherwise the target is unconditioned and gets no thermostat. Heating and cooling setpoints are aggregated separately, each over the contributing sources that have that side only (since D-126 a side can be off), weighted by transferred floor area (θ is a setpoint temperature); a side is on in the target when any such source has it:

```text
C      = { i : source i has the side (heating or cooling) and AreaFractionᵢ > 0 }
wᵢ     = AreaFractionᵢ · FloorAreaᵢ        for i in C
θ*(t)  = Σᵢ∈C wᵢ · θᵢ(t) / Σᵢ∈C wᵢ
```

Unconditioned sources still contribute their loads; they never weigh the setpoints. A merged heating setpoint above the merged cooling setpoint in any hour is the error `SetpointsCross` naming the sources. Setpoint aggregation is a prescribed control rule, not a conservation invariant. Merging conditioned and unconditioned sources can enlarge the conditioned floor area; validation reports that change from S3 on and does not enforce it (D-038).

The properties of D-126 are aggregated with the same transferred quantities (the derivations are in [the research brief, §7](../LOD_geometric_zoning_equivalence_research_brief.md#extended-program-properties-d-126)); each result carries an `AggregationRecord`:

```text
heat fractions   φᵏ* = Σ Tᵢ · φᵢᵏ / Q*             k = radiant, latent, lost, visible, return air; weights fᵢ·Aᵢ when Q* = 0
activity         a*(t) = Σ oᵢ(t) · aᵢ(t) / Σ oᵢ(t)    oᵢ(t) = transferred scheduled occupants; people heat conserved every hour
                                                     an hour without occupants: weights Dᵢ (transferred design occupants); none at all: fᵢ·Aᵢ
radiant fraction of people     weighted by Dᵢ (fᵢ·Aᵢ without occupants)
sensible fraction of people    all autocalculate: autocalculate;  all numbers: weighted by Dᵢ;
                               a mixture: autocalculate and the warning MixedSensibleFraction (only sources with a positive weight count)
water target, inlet  ϑ*(t) = Σ qᵢ(t) · ϑᵢ(t) / Σ qᵢ(t)    qᵢ(t) = Tᵢ · sᵢ(t); the same weights for both, so water heat is conserved every hour
                                                     an hour without flow: weights Tᵢ; no flow at all: fᵢ·Aᵢ
calendar         the sources' calendars must agree (ScheduleCalendar.Agree); the target carries the non-null one
```

A weighted mean of equal values is that value exactly (also hour by hour for the setpoints, so equal heating and cooling setpoints merged over different sources do not cross by rounding), and an activity or water-temperature schedule that is the same (name, kind, and values) in every source keeps its name and values, so merging default presets leaves `BEMGen Activity Level` and the default hot-water temperature schedules unchanged. Load schedules and setpoints are always named after the target.

Special cases:

| Situation | Result |
| --- | --- |
| No sources | Error `NoSources` |
| Target or source measures negative or not finite | Error `InvalidMeasures` |
| A fraction outside [0, 1] by more than `RelativeArea` | Error `FractionOutOfRange` |
| Sources define one load type with different bases | One target component per basis, each aggregated on its own (D-047) |
| `Q* = 0` | Value 0, a constant-zero fraction schedule, and `Info` `ZeroLoadSchedule` |
| `Q* > 0` and `B* = 0` (for example an air-change load in a target of zero volume) | Error `ZeroBasisQuantity` |
| No conditioned source contributes floor area | Unconditioned target: no thermostat, no setpoints |
| Conditioned sources contribute, but `Σ wᵢ = 0` (zero floor area) | Error `ZeroSetpointWeight` |
| Heat fractions, water temperatures, or people properties whose weights are all zero (no magnitude, flow, or occupants, and no floor area) | Error `ZeroAggregationWeight` |
| The merged heating setpoint exceeds the merged cooling setpoint in some hour | Error `SetpointsCross`, naming the sources |
| Sources on different calendars | Error `CalendarMismatch`, naming the sources |
| Numbers and `autocalculate` among the weighted sources' sensible fractions | `autocalculate` and the warning `MixedSensibleFraction` |

Apart from one clamp, the aggregator never adjusts a quantity to make it fit: aggregated fraction schedule values are clamped to [0, 1] only to remove floating-point noise, because a weighted mean of fractions already lies in [0, 1].

### 6.3 What the tests prove

| Property | Tests (`EquivalentPropertyAggregatorTests`) |
| --- | --- |
| Installed magnitude conserved per load type and basis, including occupancy and air volume flow | `ConservesMagnitudesAtEveryHourForRandomSources` (seeds 1 to 5) |
| Scheduled magnitude conserved hour by hour | `ConservesMagnitudesAtEveryHourForRandomSources`, `SchedulesAreMagnitudeWeighted` |
| Basis-specific weightings | `AreaDensityIsAreaWeighted`, `AirChangesAreVolumeWeighted`, `PerPersonLoadsAreOccupancyWeighted` (`ExteriorWallLoadsUseTheExteriorWallFraction` was removed in D-124) |
| Mixed bases: one component per basis; occupancy components add up (D-047) | `EachBasisIsAggregatedAsItsOwnComponent`, `OccupancyComponentsAddUp` |
| Setpoints floor-area weighted by transferred area | `SetpointsAreFloorAreaWeighted`, `SetpointWeightsUseTheTransferredFloorArea` |
| Per-dwelling loads weighted by dwelling count, installed power conserved; end uses stay separate (`ProgramPropertyAggregationTests`) | `PerDwellingLoadsAreWeightedByDwellingCount`, `ASplitDwellingKeepsItsValuePerDwelling`, `EndUsesStaySeparateComponents` |
| Heat fractions weighted by magnitude, installed heat power conserved per component | `HeatFractionsAreWeightedByTransferredMagnitude`, `InstalledHeatPowerIsConservedPerComponent`, `HeatFractionsOfAZeroComponentAreFloorAreaWeighted`, `EqualHeatFractionsMergeExactly` |
| People heat (occupants × activity) and water heat (flow × (target − inlet)) conserved every hour, with random sources | `PeopleHeatIsConservedEveryHour`, `WaterHeatIsConservedEveryHour` (seeds), `ActivityIsWeightedByScheduledOccupantsEveryHour`, `WaterTemperaturesAreWeightedByScheduledFlowEveryHour` |
| The sensible-fraction rule and the zero-weight fallbacks | `PeopleFractionsAreWeightedByDesignOccupants`, `AutocalculatedSensibleFractionsStayAutocalculated`, `MixingANumberWithAutocalculateGivesAutocalculateAndAWarning`, `WithoutOccupantsPeoplePropertiesAreFloorAreaWeighted`, `WaterTemperaturesWithoutFlowAreFloorAreaWeighted` |
| Each thermostat side over the sources that have it; crossed merged setpoints; calendars | `EachSetpointSideIsAveragedOverTheSourcesThatHaveIt`, `ASideOffInEverySourceStaysOff`, `MergedSetpointsThatCrossAreAnErrorNamingTheSources`, `CalendarsPassThroughWhenTheyAgree`, `DifferentCalendarsAreAnError` |
| Conditioning: any conditioned wins; only conditioned sources weigh setpoints | `UnconditionedSourcesDoNotWeighSetpoints`, `OnlyUnconditionedSourcesGiveAnUnconditionedTarget`, `ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget` |
| A single whole source reproduces its loads, schedules, and setpoints | `SingleWholeSourceReproducesItsProgram` |
| Source order does not change the result | `SourceOrderDoesNotChangeTheResult` |
| Edge cases and errors | `ZeroLoadGivesZeroValueAndZeroSchedule`, `PositiveLoadWithoutBasisQuantityIsAnError`, `ZeroSetpointWeightIsAnError`, `NoSourcesIsAnError`, `FractionsOutsideZeroToOneAreAnError`, `InvalidMeasuresAreAnError` |

## 7. Units

| Quantity | Unit | Where |
| --- | --- | --- |
| Floor area | m² | `ZoneMeasures` |
| Volume | m³ | `ZoneMeasures` |
| Occupancy magnitude | people | `LoadType.Occupancy` |
| Dwelling count | dwellings (fractional after a split) | `ZoneMeasures.DwellingUnits`, `Zone.DwellingUnits` |
| Lighting, electric equipment, gas equipment magnitude | W | `LoadType` |
| Domestic hot water, ventilation magnitude | m³/h | `LoadType` |
| Load value | magnitude unit per basis unit: per m² floor area, per person, per zone, per dwelling, or 1/h for air changes | `LoadDefinition.Value` |
| Heat fraction | dimensionless, [0, 1]; sum at most 1 | `HeatFractions` |
| Activity level | W per person | `ScheduleKind.Activity`, `PeopleProperties.Activity` |
| Radiant and sensible fraction of people | dimensionless, [0, 1] (sensible: or `autocalculate`) | `PeopleProperties` |
| Infiltration design rate | m³/h per m² of exterior surface or of exterior wall, or 1/h for air changes | `Infiltration.DesignRate` |
| Fraction schedule value | dimensionless, [0, 1] | `ScheduleKind.Fraction` |
| Temperature schedule value | °C (setpoints, hot-water target and inlet) | `ScheduleKind.Temperature` |
| Calendar year | a non-leap year, 1 to 9999 (default 2007) | `ScheduleCalendar.Year` |
| Window-to-wall ratio | dimensionless, [0, 1) | `ProgramPreset.WindowToWallRatio` |
| Time step | 1 h, 8760 per (non-leap) year | `Schedule.HoursPerYear` |
| Distance tolerance | m | `ToleranceSettings.Distance` |
| Angle tolerance | rad | `ToleranceSettings.Angle` |
| Aggregation weights | transferred magnitude (people, W, m³/h) or transferred floor area (m²); for a mix the magnitude or the share in the virtual unit-area zone | `AggregationRecord.Weights` |

## 8. Validation and diagnostic codes

Invalid input is an expected failure: factories return a failed `Result<T>` with error diagnostics instead of throwing. Exceptions signal programming errors only: invalid tolerances, an `AggregationRecord` with a different number of sources and weights, a successful `Result` built with errors or a failed one without, reading `Value` of a failed result, and an unknown `LoadBasis`.

| Code | Severity | Raised by |
| --- | --- | --- |
| `EmptyName` | Error | `Schedule.Create`, `ProgramPreset.Create`, `LoadDefinition.Create` (an empty end use, D-126) |
| `ScheduleLength` | Error | `Schedule.Create`, `Schedule.FromDailyProfiles` |
| `ScheduleValue` | Error | `Schedule.Create` |
| `ScheduleKindMismatch` | Error | `LoadDefinition.Create`, `Thermostat.Create`, `PeopleProperties.Create`, `WaterTemperatures.Create` |
| `LoadValue` | Error | `LoadDefinition.Create` |
| `UndefinedLoadKind` | Error | `LoadDefinition.Create` (D-124) |
| `LoadBasisNotAllowed` | Error | `LoadDefinition.Create` |
| `DuplicateLoadType` | Error | `ZoneProgram.Create` (one load per type, end use, and basis) |
| `NoSetpoint` | Error, or Info | `Thermostat.Create`, `Thermostat.ForSides` (D-126; the info says a switched-on side has no schedule) |
| `SetpointsCross` | Error | `Thermostat.Create`, `Thermostat.ForSides`, `EquivalentPropertyAggregator`, `ProgramMix.Mix` (D-126) |
| `HeatFractionValue`, `HeatFractionsExceedOne`, `HeatFractionNotSupported` | Error | `HeatFractions.Create`, `HeatFractions.WithOverrides`, `LoadDefinition.Create` (D-126) |
| `WaterTargetBelowInlet`, `WaterTemperaturesNotAllowed` | Error | `WaterTemperatures.Create`, `WaterTemperatures.WithOverrides`, `LoadDefinition.Create` (D-126) |
| `PeopleFraction` | Error | `SensibleHeatFraction.Of`, `SensibleHeatFraction.Parse`, `PeopleProperties.Create` (D-126) |
| `CalendarYear`, `CalendarHoliday` | Error | `ScheduleCalendar.Create` (D-126) |
| `CalendarMismatch` | Error | `ScheduleCalendar.Agree`, so `EquivalentPropertyAggregator`, `ProgramMix.Mix`, plan generation, validation, and `Convert2IDF` (D-126) |
| `PerDwellingWithoutDwellings` | Error | plan generation and validation (`ProgramChecks.PerDwellingLoads`, D-126) |
| `MixedSensibleFraction` | Warning | `EquivalentPropertyAggregator`, `ProgramMix.Mix` (D-126) |
| `ZeroAggregationWeight` | Error | `EquivalentPropertyAggregator` (D-126) |
| `PerPersonWithoutOccupancy` | Error | `ZoneProgram.Create` |
| `MixWeight` | Error | `ProgramMix.Mix` (D-124) |
| `PerPersonWithAbsoluteOccupancy` | Error | `ProgramMix.Mix` (D-124) |
| `MixedOccupancyBases` | Error | `ProgramMix.Mix` (D-126) |
| `MixedConditioning` | Info | `ProgramMix.Mix` (D-124) |
| `WindowToWallRatio` | Error | `ProgramPreset.Create` |
| `NoSources` | Error | `EquivalentPropertyAggregator`, `ProgramMix.Mix` |
| `FractionOutOfRange` | Error | `EquivalentPropertyAggregator` |
| `ZeroBasisQuantity` | Error | `EquivalentPropertyAggregator` |
| `ZeroLoadSchedule` | Info | `EquivalentPropertyAggregator` |
| `ZeroSetpointWeight` | Error | `EquivalentPropertyAggregator` |
| `InvalidMeasures` | Error | `EquivalentPropertyAggregator` |
| `EnvelopeValue` | Error | `EnvelopePreset.Create` (S6) |
| `InfiltrationValue` | Error | `EnvelopePreset.Create`, through `Infiltration.Check` (D-124) |
| `ConstructionLayers` | Error | `EnvelopePreset.Create` (S6) |
| `DuplicateEnvelopeName` | Error | `EnvelopePreset.Create` (S6) |
| `EnvelopeName` | Error | `EnvelopePreset.Create` (S6) |
| `NoConstructionRole` | Error | `ConstructionRoles.Of` (S6) |

## 9. Immutability and traceability

**Immutability.** Every S1 type is immutable after construction. Classes are `sealed` and expose get-only properties (`Thermostat`, `ZoneProgram`, and the others); those that validate user input hide their constructors behind factories that return `Result<T>`. Small value types are positional records (`Diagnostic`, `ZoneMeasures`, `SourceZoneContribution`) or a record struct (`ZoneId`). Collections are copied into a private array when an object is created and exposed as `IReadOnlyList<T>` through `Array.AsReadOnly`, which wraps the array in a `ReadOnlyCollection<T>`: callers cannot cast the list back to an array and change it (`ScheduleTests.ValuesCannotBeMutatedThroughTheList`).

`Lod.Core` deliberately does not use `System.Collections.Immutable`. Rhino 8 ships its own `System.Collections.Immutable.dll` (with `System.Memory` and `System.Text.Json`); a core library that references a different version risks assembly version conflicts inside Rhino. Read-only wrappers over private arrays give the same guarantee with the base class library only, which also keeps `Lod.Core` within its dependency boundary (AGENTS.md: BCL only). Records and `init` accessors on `netstandard2.0` need the `IsExternalInit` polyfill in `src/Shared/IsExternalInit.cs`, which `Directory.Build.props` links into every non-.NET Core build (ADR-001).

**Traceability.** Every derived load and schedule records how it was computed (GLOBAL.md scientific rule 2). An `AggregationRecord` holds the `AggregationMethod`, the source `ZoneId`s, and one weight per source, aligned by index; its constructor rejects different numbers of sources and weights (`AggregationRecordTests`):

| Derived value | Method | Sources | Weights |
| --- | --- | --- | --- |
| Aggregated load (`LoadDefinition.Aggregation`) | `MagnitudeConserved` | sources that define the load type in that basis | transferred magnitudes `Tᵢ` (people, W, or m³/h); their sum is the target magnitude `Q*` |
| Its schedule (`Schedule.Aggregation`) | `MagnitudeWeighted` | same as the load | same as the load |
| Heating and cooling setpoint schedules (`Thermostat`) | `FloorAreaWeighted` | the sources that have that side, with `AreaFraction > 0` | transferred floor areas `wᵢ` (m²) |
| Heat fractions of a load (`HeatFractions.Aggregation`, D-126) | `MagnitudeWeighted`; `FloorAreaWeighted` when `Q* = 0` | same as the load | transferred magnitudes `Tᵢ`, or floor areas `fᵢ·Aᵢ` |
| People properties and the activity schedule (`PeopleProperties.Aggregation`, `Activity.Aggregation`, D-126) | `OccupantWeighted`; `FloorAreaWeighted` without occupants | all sources | transferred design occupants `Dᵢ`, or floor areas |
| Hot-water target and inlet schedules (`WaterTemperatures`, D-126) | `FlowWeighted`; `FloorAreaWeighted` without flow | same as the load | transferred design flows `Tᵢ`, or floor areas |

**Program mixes (D-124).** The sources of a mix are not zones: its inputs are the sources, each identified by the key `Input.k` of the provenance parameter that names it with its given and normalised weight (`Input.1`, `Input.2`, ..., zero-padded to the width of the input count so that the keys sort in input order), carried as a `ZoneId`. A mixed load and its schedule have the same methods as above over the inputs that define the component, with the transferred magnitudes of the virtual unit-area zone as weights; a mixed setpoint is `FloorAreaWeighted` over the conditioned inputs with their normalised weights ŵᵢ.

Input loads and schedules have `Aggregation == null`. Aggregated schedules are named `"<target> <LoadType> <LoadBasis>"` (with the end use before the basis when it is not the type's default), `"<target> Heating Setpoint"`, `"<target> Cooling Setpoint"`, `"<target> Activity"`, and, for hot water, the load's schedule name plus ` Target Temperature` or ` Inlet Temperature`; a schedule that is the same in every source keeps its own name. Together with the source programs and the target's measures, a record is enough to recompute the derived value. Zone-level traceability (which source zones a target zone was built from) arrives with `Zone` in S2.

## 10. What arrives in S2

S2 consumes the S1 types; it does not replace them.

- **Geometry** (`Lod.Core.Geometry`): points and polygons with holes in a building-local frame, polygon operations over Clipper2 at the `ToleranceSettings.DecimalPrecision` precision, wall orientation bins, and explicit windows with the first generator's centred-window rule (ADR-002, D-026, D-039).
- **Zones and surfaces** (`Lod.Core.Model`): `Zone` (one or more prisms, a `SpaceType`, a `ZoneProgram`, the source `ZoneId`s it was derived from, and a multiplier), wall surfaces carrying explicit windows and horizontal surfaces, both with boundary conditions, and surface identifiers. Zone measures computed from this geometry become the `ZoneMeasures` of the aggregator.
- **Pipeline types**: `IGeneratedPlan`, `IFloor`, `IGeneratedBuilding`, `IPlanSimplifier`, `IFloorAggregator`, the `PlanGenerator` base with `LinearPlanGenerator` (in `Lod.Generators`), `NoSimplification`, `Stack`, and provenance records of each operation, its parameters, and the code version.
- **Plans per storey (S8.7, [ADR-015](../decisions/ADR-015-plans-per-storey.md))**: `MultiStoreyPlanGenerator<TParameters, TPresets>` (`Lod.Core.Plans`) is the sibling of `PlanGenerator` for a family whose plan differs per storey: `Generate` returns `Result<IReadOnlyList<IGeneratedPlan>>`, one ordinary plan per storey, bottom-up, each with the provenance parameters `Storey` (from 0) and `StoreyElevation` (S8.8, the storey's base elevation in m, read by the previews through `StoreyProvenance.ElevationOf`, which follows operations of one input and is 0 otherwise, D-108); the two bases share the preset checks, surfaces, windows, and provenance (`PlanBuilder`, internal). `SteppedBandGenerator` (`SYN-TYP-012`) is the first such generator. The floor aggregators take the storeys as floor entries with multiplier 1; no pipeline type changes.
- **Floor zones of several pieces (D-123, [design note](../plans/2026-10-06-conditioned-merge.md))**: a floor zone may have several parts at one elevation, one per piece, where until then a zone had several parts only to span storeys (the single-zone aggregators, one part per storey outline). The pieces of a zone are disjoint and share no wall. `TargetZone` (`Lod.Core.Simplification`) holds `Pieces`, one polygon or several, and `PlanSimplifier` makes one `ZonePart` per piece and sums floor area and volume over them (the zone's `ZoneMeasures`); the exterior areas of the envelope's infiltration (D-124) are taken from the outdoor surfaces of every piece (`ZoneInfiltration`). `LayoutSurfaceBuilder` takes one `LayoutZone` per piece, all with the zone's ID, and builds them as one zone: the walls are numbered on across the pieces (`W1`, `W2`, …) and there is one floor and one ceiling per piece, `F1`, `F2`, … and `C1`, `C2`, … (a zone of one piece keeps `F` and `C` until floors are stacked, then `F1` and `C1`). Two pieces of one zone that share an edge are the error `TouchingPieces`, and two target zones, or two zones of a layout, with one ID the error `DuplicateZoneId`. A mapping row is one row per source and target, summed over the pieces of the target and the parts of the source, and its target fraction is taken of the area of all the pieces. `Storeys` gives every part its floor and ceiling pieces, split by the parts of the storeys below and above, and the single-zone aggregators unite all the parts of every zone of a storey. Only *Semantic Merge* and *Conditioned Merge* with *Join Pieces* true make such zones ([pipeline](pipeline.md#3-plan-simplification)).
- **Grasshopper components** for schedules, loads, program presets (with a *Conditioned* input), and the example presets (replaced in S4.1 by one default preset component per space type, D-061).

From S3, plan simplifiers compute each `SourceZoneContribution` from zone overlaps and façade coverage and call `IEquivalentPropertyAggregator` once per target zone.

## 11. Names that differ from the repository specification

The roadmap (v3) uses the names of the code. The [repository specification](../LOD_grasshopper_plugin_repository_spec.md) predates them:

| Specification | Code | Note |
| --- | --- | --- |
| Load type `DHW` (§8) | `LoadType.DomesticHotWater` | Spelled out. |
| Control schedules `HeatingSetpoint`, `CoolingSetpoint` (§8) | `Thermostat.HeatingSetpoint`, `Thermostat.CoolingSetpoint` | Present only on conditioned programs (D-038). |
| `AggregatedZoneProperties`, `AggregationContext` (§9) | `Result<ZoneProgram>`; target `ZoneId` and `ZoneMeasures` | The aggregator returns an ordinary zone program. |
| Semantic categories (§7) | `SpaceType` | Adds `Mixed` for simplified zones that combine several space types. |
