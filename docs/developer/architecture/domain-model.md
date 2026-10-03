# Domain Model

> **Status:** Current as of S1 (`v0.1.0`); program presets updated in S4.1 (`v0.4.1`, D-061); envelope presets added in S6 (§5.1) · **Date:** 2026-10-02 · **Scope:** `Lod.Core.Common`, `Lod.Core.Schedules`, `Lod.Core.Loads`, `Lod.Core.Programs`, `Lod.Core.Envelope`, `Lod.Core.Aggregation`

This document describes the domain types that exist after stage S1 of the [implementation roadmap](../plans/2026-09-30-implementation-roadmap.md) and how they relate. S1 deliberately has no geometry: a zone appears only as a `ZoneId` and three measures (floor area, volume, exterior wall area). That is enough to define and test the aggregation rules (ADR-005, ADR-007) before any plan exists. Geometry, zones, surfaces, and the pipeline types arrive in S2 (§10).

All types live in `Lod.Core` (`netstandard2.0`, base class library only, no Rhino or Grasshopper reference) and are tested by `Lod.Core.Tests` on `net8.0` without Rhino.

## 1. Overview

```text
 Programs ─────────────────────────────────────────────────────────────────────────────
 PresetValues ─ToPreset()─► ProgramPreset ─1─► ZoneProgram ─0..*─► LoadDefinition ─1─► Schedule (Fraction)
 (plain values, S4.1)       Name, SpaceType?,  │                   Type, Basis, Value
                            WindowToWallRatio  └─0..1─► Thermostat ─┬─1─► Schedule (Temperature)  heating setpoint
                                                                    └─1─► Schedule (Temperature)  cooling setpoint
                                                none = unconditioned zone, no setpoints

 Traceability ─────────────────────────────────────────────────────────────────────────
 LoadDefinition.Aggregation ─┐
 Schedule.Aggregation ───────┴─0..1─► AggregationRecord: Method, Sources (ZoneId[]), Weights (double[])

 Aggregation ──────────────────────────────────────────────────────────────────────────
 target ZoneId + target ZoneMeasures ──┐
 SourceZoneContribution[] ─────────────┼─► IEquivalentPropertyAggregator.Aggregate ─► Result<ZoneProgram>
   Zone (ZoneId), Program (ZoneProgram)│     implemented by EquivalentPropertyAggregator(ToleranceSettings),
   Measures (ZoneMeasures),            │     which uses DesignMagnitudes (value ↔ magnitude)
   AreaFraction, ExteriorWallFraction ─┘

 Common ───────────────────────────────────────────────────────────────────────────────
 Result<T>: Value + Diagnostics (Info, Warning)  |  Diagnostics with at least one Error
 Diagnostic: Severity, Code (DiagnosticCodes), Message, Subject
 ToleranceSettings: Distance, RelativeArea, RelativeLoad, AbsoluteSchedule, Angle
 GeometryLimits: MinimumWindowWallLength, MinimumWindowWidth, MinimumWindowHeight (S8.1)
```

Inputs flow left to right: schedules build loads and thermostats, loads and an optional thermostat build a zone program (conditioned when it has a thermostat), and a zone program and a window-to-wall ratio build a program preset. The aggregator takes the programs of several source zones and returns the program of one target zone, built from the same types, with every derived load and schedule carrying an `AggregationRecord`.

## 2. Common (`Lod.Core.Common`)

**`ToleranceSettings`** is the only place where numerical tolerances are defined (GLOBAL.md quality rule 4, ADR-004). Its constructor rejects values that are not positive and finite with an `ArgumentOutOfRangeException`. `ToleranceSettings.Default`:

| Property | Default | Used for |
| --- | --- | --- |
| `Distance` | 1e-6 m | Geometric distances. `DecimalPrecision` (6) is the matching number of decimal places, the polygon-clipping precision from S2. |
| `RelativeArea` | 1e-6 | Area and volume comparisons (`AreaEquals`); also the slack allowed on transfer fractions by the aggregator. |
| `RelativeLoad` | 1e-9 | Load, occupancy, and air-flow comparisons (`LoadEquals`). |
| `AbsoluteSchedule` | 1e-9 | Schedule value comparisons (`ScheduleEquals`). |
| `Angle` | 1e-6 rad | Angular comparisons. |

Relative comparisons use a floor of 1, `|a − b| ≤ rel · max(1, |a|, |b|)`, so values near zero are compared absolutely.

**`GeometryLimits`** (S8.1, ADR-011) is the only place where the minimum wall and window geometry of the plan generators is defined: `MinimumWindowWallLength` 1 m, `MinimumWindowWidth` 0.3 m, and `MinimumWindowHeight` 0.3 m in `GeometryLimits.Default`. It is an immutable record whose constructor rejects values that are not positive and finite with an `ArgumentOutOfRangeException`. `PlanGenerator` takes it through its constructor (the default when omitted) and records non-default limits in the plan's provenance. An outdoor wall or window below a limit gets no window and the info `WindowOmitted`; the limits do not apply to rebuilt walls (ADR-012).

**`Diagnostic`** is a structured message (GLOBAL.md quality rule 5): `Severity` (`Info`, `Warning`, `Error`), a stable `Code` from `DiagnosticCodes`, an actionable `Message`, and an optional `Subject` (for example a zone ID). Codes are never reused or renamed; a removed code's name is not reused (S4.1 removed `DuplicateSpaceType`, D-064). §8 lists the S1 codes.

**`Result<T>`** is the outcome of an operation whose failure is expected. A success carries a value and may carry `Info` and `Warning` diagnostics, never errors; a failure carries at least one `Error` and no value. Reading `Value` on a failure throws an `InvalidOperationException` listing the diagnostics. The static `Result` class creates results: `Success`, `Failure`, and `FromDiagnostics`, which builds the value only when the collected diagnostics contain no error. Every S1 factory that validates input (`Schedule.Create`, `Schedule.Constant`, `Schedule.FromDailyProfiles`, `LoadDefinition.Create`, `Thermostat.Create`, `ZoneProgram.Create`, `ProgramPreset.Create`) returns a `Result<T>`, and so do `PresetValues.ToPreset` (S4.1) and the aggregator.

**`ZoneId`** is a strongly typed zone identifier (`readonly record struct` over a string). It is the only identifier in S1; S2 adds identifiers for surfaces.

## 3. Schedules (`Lod.Core.Schedules`)

**`Schedule`** is an immutable series of `Schedule.HoursPerYear` = 8760 hourly values for a non-leap year (ADR-003), with a `Name`, a `ScheduleKind`, and an optional `AggregationRecord`.

- `ScheduleKind.Fraction`: dimensionless values in [0, 1] that multiply a load's design magnitude.
- `ScheduleKind.Temperature`: finite values in °C, used for setpoints.

`Schedule.Create` validates the name (`EmptyName`), the length (`ScheduleLength`), and the values (`ScheduleValue`, reporting the first invalid hour). `Schedule.Constant` repeats one value. `Schedule.FromDailyProfiles` repeats a 24-hour weekday profile Monday to Friday and a weekend profile on Saturday and Sunday, starting from a given weekday for 1 January; holidays are not modelled. Values are read with the indexer `schedule[hour]` (0-based) or as `Values`.

## 4. Loads (`Lod.Core.Loads`)

**`LoadDefinition`** is one load of a program: a `LoadType`, a `LoadBasis`, a design `Value` in that basis, a fraction `Schedule`, and an optional `AggregationRecord`. Its design magnitude is `Value` × basis quantity (ADR-007).

| `LoadType` | Design magnitude |
| --- | --- |
| `Occupancy` | people |
| `Lighting`, `ElectricEquipment`, `GasEquipment` | W |
| `DomesticHotWater` (peak flow), `Ventilation`, `Infiltration` | m³/h |

| `LoadBasis` | Basis quantity of a zone |
| --- | --- |
| `PerFloorArea` | floor area, m² |
| `PerPerson` | design occupants, the summed magnitude of the zone's occupancy loads |
| `Absolute` | 1 |
| `PerExteriorWallArea` | gross area of walls with an outdoor boundary, windows included, m². Walls only: roofs are unknown until floors are stacked. |
| `AirChangesPerHour` | air volume, m³ (value in 1/h, magnitude in m³/h) |

`LoadDefinition.Create` rejects negative or non-finite values (`LoadValue`), occupancy expressed other than `PerFloorArea` or `Absolute` (`LoadBasisNotAllowed`), and non-fraction schedules (`ScheduleKindMismatch`).

## 5. Programs (`Lod.Core.Programs`)

**`SpaceType`** is the semantic category of a space: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, `Mixed` for a simplified zone that combines several space types, and since S8.4 the non-residential departments `Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, and `ActivityHall`, appended so that existing values keep their order ([ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md)). A non-residential zone is one department, never a room (D-097). Semantics are explicit data, never encoded in layer names, colours, or wire structure (AGENTS.md).

**`Thermostat`** holds the `HeatingSetpoint` and `CoolingSetpoint` schedules of a conditioned zone. `Thermostat.Create` rejects setpoints that are not temperature schedules (`ScheduleKindMismatch`).

**`ZoneProgram`** is the energy-relevant program of a zone: `Loads`, ordered by `LoadType`, then `LoadBasis`, with at most one load per type and basis, and an optional `Thermostat`. A load type may appear in several bases, for example ventilation per person plus per floor area; these components add up (D-047). Conditioning comes from the program (D-038): a program with a thermostat is conditioned (`IsConditioned`); one without a thermostat is unconditioned and has no setpoints. `Find(LoadType, LoadBasis)` returns a load or `null`. `ZoneProgram.Create(loads, thermostat)` rejects the same load type in the same basis twice (`DuplicateLoadType`) and per-person loads without an occupancy load (`PerPersonWithoutOccupancy`). The same type describes an input program and an aggregated one; only the `AggregationRecord`s on its loads and schedules tell them apart.

**`ProgramPreset`** is the program of one space type (D-024): `Name`, `SpaceType`, `Program`, and `WindowToWallRatio` in [0, 1) (D-026; `EmptyName`, `WindowToWallRatio`). `SpaceType` is `SpaceType?` since S8.8 (D-108, ADR-014): `Create` always gives a space type, and `AsAnyProgram()` returns the same preset without one (`IsAnyProgram`), keeping the name, the same `Program`, and the WWR; a plan generator accepts such a preset on every preset input, and its zones keep the generator's space type. The name is descriptive only: it appears in reports, provenance, and messages and is never used for matching (D-061). Until S4.1 a `ProgramPresetSet` grouped presets by space type; since S4.1 a plan generator takes a typed record with one preset per space type instead (`PlanPresets`, see [pipeline](pipeline.md#2-plan-generation)), and the set and its code `DuplicateSpaceType` are gone.

**`PresetValues`** (S4.1) holds the plain values a preset is built from: `Name`, `SpaceType`, `WindowToWallRatio`, `Conditioned`, constant `HeatingSetpoint` and `CoolingSetpoint` in °C, and `Loads`, each a **`PresetLoadValue`** (`Type`, `Basis`, `Value`, fraction `Schedule`). Change a value with a `with` expression. `ToPreset()` builds the loads, a thermostat of constant temperature schedules named `"{Name} Heating Setpoint"` and `"{Name} Cooling Setpoint"` when `Conditioned` (the setpoints are ignored otherwise), the zone program, and the preset, and returns every error of these factories together.

**`ExampleResidentialPresets`** provides illustrative presets for dwelling unit, corridor, and stair; the dwelling unit and corridor are conditioned and the stair is not. Each is available as `PresetValues` (`DwellingUnitValues`, `CorridorValues`, `StairValues`) and as the `ProgramPreset` built from them (`DwellingUnit`, `Corridor`, `Stair`). Their values and conditioning are round-number choices for development and tests, not DOE prototype values; see [program presets](../research/program-presets.md).

**`ExampleNonResidentialPresets`** (S8.4) provides illustrative presets, all conditioned, for the fifteen space types of the non-residential departments (ADR-014): `OfficeValues`/`Office`, `CoreValues`/`Core`, … `ServiceValues`/`Service`; `SpaceTypes` lists the types and `ValuesOf` and `PresetOf` look a type up (`ArgumentOutOfRangeException` for any other type). The retail schedules have their own Saturday and Sunday profiles. The values are illustrative, not sourced (D-023).

### 5.1 Envelope (`Lod.Core.Envelope`, S6)

The envelope is separate from the programs: it is the same at every level of detail, so geometry effects are not confounded with envelope changes (GLOBAL.md scientific rule 4, [ADR-010](../decisions/ADR-010-convert2idf.md)). Values and reasons: [envelope presets](../research/envelope-presets.md).

```text
 EnvelopeValues ─ToPreset()─► EnvelopePreset ─7─► Construction (one per ConstructionRole) ─1..10─► Layer
 (plain values)               Name             └─1─► GlazingSpec (the window)
 Surface + ExportedBoundary ─ConstructionRoles.Of─► ConstructionAssignment(Role, Reversed) ─EnvelopePreset.For─► Construction
```

- **`Layer`** (record): `Name`, `Thickness` (m), `Conductivity` (W/(m·K)), `Density` (kg/m³), `SpecificHeat` (J/(kg·K)); `ThermalResistance` = thickness / conductivity.
- **`Construction`**: `Name` and `Layers` from the outside to the inside (copied when created); `ThermalResistance` (layers only, no surface films), `IsSymmetric`, and `Reversed()`, the layers in reverse order named `"{Name} Reversed"`, or the construction itself when it is symmetric.
- **`GlazingSpec`** (record): `Name`, `UFactor` (W/(m²·K)), `SolarHeatGainCoefficient`, `VisibleTransmittance` of a simple glazing system.
- **`ConstructionRole`**: `ExteriorWall`, `Roof`, `GroundFloor`, `ExposedFloor`, `InteriorWall`, `InteriorFloor`, `InternalMass`. **`ConstructionAssignment`**: a role and whether the surface uses the role's construction reversed (the ceiling below an interior floor).
- **`EnvelopeValues`** (record): the preset name, one construction per role, and the window; `ToPreset()` calls `EnvelopePreset.Create`, which reports every error at once: `EmptyName`, `EnvelopeValue` (a layer property not positive and finite; a U-factor not in (0, 7], an SHGC or visible transmittance not in (0, 1)), `ConstructionLayers` (not 1 to 10 layers), `DuplicateEnvelopeName` (a material or construction name, compared ignoring case, given to two different materials or constructions; the glazing name counts as both), and `EnvelopeName` (a name longer than 100 characters, the generated reverses included, or with `,` `;` `!`). A layer used by several constructions is checked once.
- **`EnvelopePreset`**: the values, `For(role)` and `For(assignment)`, `Constructions` (each once: the roles' constructions, then the reverses of the interior wall and floor where they differ), and `Materials` (each layer once). **`ExampleEnvelopePresets`** holds one illustrative preset, `Values` and `Example`, not taken from any standard (D-023).
- **`ConstructionRoles.Of(surface, boundary)`** in `Lod.Core.Conversion` maps a surface and the boundary a converter writes for it to a `Result<ConstructionAssignment>`: the wall between two zones whose zone ID sorts after the adjacent zone's (ordinal) is reversed, as is every ceiling between storeys, so the two sides of a surface between zones list the layers in opposite order; an unresolved boundary and a wall or ceiling on the ground, which no floor aggregator produces, give the error `NoConstructionRole`.

## 6. Aggregation (`Lod.Core.Aggregation`)

### 6.1 Inputs

**`ZoneMeasures`** holds the quantities that load bases refer to: `FloorArea` (m²), `Volume` (m³), and `ExteriorWallArea` (m², gross, windows included). `IsValid` is true when all three are finite and non-negative.

**`SourceZoneContribution`** describes what one source zone gives to one target zone: the source's `Zone` ID, `Program`, and whole-zone `Measures`, plus two fractions in [0, 1]:

- `AreaFraction`: the share of the source's floor area assigned to the target. It also transfers the same share of volume, occupants, absolute loads, and every load that is not per exterior wall area.
- `ExteriorWallFraction`: the share of the source's exterior wall area assigned to the target's exterior walls. It transfers `PerExteriorWallArea` loads.

The aggregator does not compute these fractions. The caller supplies them, so the aggregator is independent of geometry and of any rezoning method (spec §9); from S3 the transfer matrix and the façade attribution compute them.

**`DesignMagnitudes`** converts between a load's value and its absolute design magnitude: `BasisQuantity(basis, measures, occupants)`, `Occupants(program, measures)` (the summed magnitude of the occupancy loads, 0 without one), and `Of(load, measures, occupants)`.

### 6.2 Rules

`IEquivalentPropertyAggregator.Aggregate(target, targetMeasures, sources)` returns the target's `ZoneProgram`. `EquivalentPropertyAggregator` implements ADR-007 for loads and ADR-005 for setpoints. Loads are aggregated per component, a load type in one basis (D-047). For each component defined by at least one source, with *i* running over the sources that define it:

```text
Qᵢ     = valueᵢ · Bᵢ                 design magnitude of source i (people, W, or m³/h); Bᵢ is its basis quantity
Tᵢ     = fᵢ · Qᵢ                     transferred magnitude; fᵢ = ExteriorWallFraction for PerExteriorWallArea,
                                     AreaFraction otherwise
Q*     = Σ Tᵢ                        target design magnitude (conserved)
value* = Q* / B*                     B* is the target's quantity of the component's basis, from targetMeasures
s*(t)  = Σ Tᵢ · sᵢ(t) / Q*           target schedule, so that Q* · s*(t) = Σ Tᵢ · sᵢ(t) at every hour t
```

One rule covers every basis: it is area weighting for per-floor-area loads, volume weighting for air changes per hour (D-019), occupancy weighting for per-person loads, summation for absolute loads, and exterior-wall-area weighting for per-exterior-wall loads. Occupancy is aggregated first (it is the first `LoadType`, and occupancy is never per person), and the target's design occupants (the sum of its conserved occupancy components) are the basis quantity of per-person loads. The target program contains the union of the sources' components, ordered by `LoadType`, then `LoadBasis`. Sources that express one load type in different bases are not an error: each basis is aggregated as its own component, neither rejected nor converted to another basis, and a source without a component contributes nothing to it.

Conditioning and setpoints follow ADR-005 and D-038. The target is conditioned when at least one conditioned source contributes floor area to it (`AreaFraction > 0`): "any conditioned wins". Otherwise the target is unconditioned and gets no thermostat. Heating and cooling setpoints are aggregated separately over the conditioned contributing sources only, weighted by transferred floor area (θ is a setpoint temperature):

```text
C      = { i : source i has a Thermostat and AreaFractionᵢ > 0 }
wᵢ     = AreaFractionᵢ · FloorAreaᵢ        for i in C
θ*(t)  = Σᵢ∈C wᵢ · θᵢ(t) / Σᵢ∈C wᵢ
```

Unconditioned sources still contribute their loads; they never weigh the setpoints. Setpoint aggregation is a prescribed control rule, not a conservation invariant. Merging conditioned and unconditioned sources can enlarge the conditioned floor area; validation reports that change from S3 on and does not enforce it (D-038).

Special cases:

| Situation | Result |
| --- | --- |
| No sources | Error `NoSources` |
| Target or source measures negative or not finite | Error `InvalidMeasures` |
| A fraction outside [0, 1] by more than `RelativeArea` | Error `FractionOutOfRange` |
| Sources define one load type with different bases | One target component per basis, each aggregated on its own (D-047) |
| `Q* = 0` | Value 0, a constant-zero fraction schedule, and `Info` `ZeroLoadSchedule` |
| `Q* > 0` and `B* = 0` (for example a per-exterior-wall load in a target without exterior walls) | Error `ZeroBasisQuantity` |
| No conditioned source contributes floor area | Unconditioned target: no thermostat, no setpoints |
| Conditioned sources contribute, but `Σ wᵢ = 0` (zero floor area) | Error `ZeroSetpointWeight` |

Apart from one clamp, the aggregator never adjusts a quantity to make it fit: aggregated fraction schedule values are clamped to [0, 1] only to remove floating-point noise, because a weighted mean of fractions already lies in [0, 1].

### 6.3 What the tests prove

| Property | Tests (`EquivalentPropertyAggregatorTests`) |
| --- | --- |
| Installed magnitude conserved per load type and basis, including occupancy and air volume flow | `ConservesMagnitudesAtEveryHourForRandomSources` (seeds 1 to 5) |
| Scheduled magnitude conserved hour by hour | `ConservesMagnitudesAtEveryHourForRandomSources`, `SchedulesAreMagnitudeWeighted` |
| Basis-specific weightings | `AreaDensityIsAreaWeighted`, `AirChangesAreVolumeWeighted`, `PerPersonLoadsAreOccupancyWeighted`, `ExteriorWallLoadsUseTheExteriorWallFraction` |
| Mixed bases: one component per basis; occupancy components add up (D-047) | `EachBasisIsAggregatedAsItsOwnComponent`, `OccupancyComponentsAddUp` |
| Setpoints floor-area weighted by transferred area | `SetpointsAreFloorAreaWeighted`, `SetpointWeightsUseTheTransferredFloorArea` |
| Conditioning: any conditioned wins; only conditioned sources weigh setpoints | `UnconditionedSourcesDoNotWeighSetpoints`, `OnlyUnconditionedSourcesGiveAnUnconditionedTarget`, `ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget` |
| A single whole source reproduces its loads, schedules, and setpoints | `SingleWholeSourceReproducesItsProgram` |
| Source order does not change the result | `SourceOrderDoesNotChangeTheResult` |
| Edge cases and errors | `ZeroLoadGivesZeroValueAndZeroSchedule`, `PositiveLoadWithoutBasisQuantityIsAnError`, `ZeroSetpointWeightIsAnError`, `NoSourcesIsAnError`, `FractionsOutsideZeroToOneAreAnError`, `InvalidMeasuresAreAnError` |

## 7. Units

| Quantity | Unit | Where |
| --- | --- | --- |
| Floor area, exterior wall area | m² | `ZoneMeasures` |
| Volume | m³ | `ZoneMeasures` |
| Occupancy magnitude | people | `LoadType.Occupancy` |
| Lighting, electric equipment, gas equipment magnitude | W | `LoadType` |
| Domestic hot water, ventilation, infiltration magnitude | m³/h | `LoadType` |
| Load value | magnitude unit per basis unit: per m² floor area, per person, per zone, per m² exterior wall, or 1/h for air changes | `LoadDefinition.Value` |
| Fraction schedule value | dimensionless, [0, 1] | `ScheduleKind.Fraction` |
| Temperature schedule value | °C | `ScheduleKind.Temperature` |
| Window-to-wall ratio | dimensionless, [0, 1) | `ProgramPreset.WindowToWallRatio` |
| Time step | 1 h, 8760 per (non-leap) year | `Schedule.HoursPerYear` |
| Distance tolerance | m | `ToleranceSettings.Distance` |
| Angle tolerance | rad | `ToleranceSettings.Angle` |
| Aggregation weights | transferred magnitude (people, W, m³/h) or transferred floor area (m²) | `AggregationRecord.Weights` |

## 8. Validation and diagnostic codes

Invalid input is an expected failure: factories return a failed `Result<T>` with error diagnostics instead of throwing. Exceptions signal programming errors only: invalid tolerances, an `AggregationRecord` with a different number of sources and weights, a successful `Result` built with errors or a failed one without, reading `Value` of a failed result, and an unknown `LoadBasis`.

| Code | Severity | Raised by |
| --- | --- | --- |
| `EmptyName` | Error | `Schedule.Create`, `ProgramPreset.Create` |
| `ScheduleLength` | Error | `Schedule.Create`, `Schedule.FromDailyProfiles` |
| `ScheduleValue` | Error | `Schedule.Create` |
| `ScheduleKindMismatch` | Error | `LoadDefinition.Create`, `Thermostat.Create` |
| `LoadValue` | Error | `LoadDefinition.Create` |
| `LoadBasisNotAllowed` | Error | `LoadDefinition.Create` |
| `DuplicateLoadType` | Error | `ZoneProgram.Create` |
| `PerPersonWithoutOccupancy` | Error | `ZoneProgram.Create` |
| `WindowToWallRatio` | Error | `ProgramPreset.Create` |
| `NoSources` | Error | `EquivalentPropertyAggregator` |
| `FractionOutOfRange` | Error | `EquivalentPropertyAggregator` |
| `ZeroBasisQuantity` | Error | `EquivalentPropertyAggregator` |
| `ZeroLoadSchedule` | Info | `EquivalentPropertyAggregator` |
| `ZeroSetpointWeight` | Error | `EquivalentPropertyAggregator` |
| `InvalidMeasures` | Error | `EquivalentPropertyAggregator` |
| `EnvelopeValue` | Error | `EnvelopePreset.Create` (S6) |
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
| Heating and cooling setpoint schedules (`Thermostat`) | `FloorAreaWeighted` | conditioned sources with `AreaFraction > 0` | transferred floor areas `wᵢ` (m²) |

Input loads and schedules have `Aggregation == null`. Aggregated schedules are named `"<target> <LoadType> <LoadBasis>"`, `"<target> Heating Setpoint"`, and `"<target> Cooling Setpoint"`. Together with the source programs and the target's measures, a record is enough to recompute the derived value. Zone-level traceability (which source zones a target zone was built from) arrives with `Zone` in S2.

## 10. What arrives in S2

S2 consumes the S1 types; it does not replace them.

- **Geometry** (`Lod.Core.Geometry`): points and polygons with holes in a building-local frame, polygon operations over Clipper2 at the `ToleranceSettings.DecimalPrecision` precision, wall orientation bins, and explicit windows with the first generator's centred-window rule (ADR-002, D-026, D-039).
- **Zones and surfaces** (`Lod.Core.Model`): `Zone` (one or more prisms, a `SpaceType`, a `ZoneProgram`, the source `ZoneId`s it was derived from, and a multiplier), wall surfaces carrying explicit windows and horizontal surfaces, both with boundary conditions, and surface identifiers. Zone measures computed from this geometry become the `ZoneMeasures` of the aggregator.
- **Pipeline types**: `IGeneratedPlan`, `IFloor`, `IGeneratedBuilding`, `IPlanSimplifier`, `IFloorAggregator`, the `PlanGenerator` base with `LinearPlanGenerator` (in `Lod.Generators`), `NoSimplification`, `Stack`, and provenance records of each operation, its parameters, and the code version.
- **Plans per storey (S8.7, [ADR-015](../decisions/ADR-015-plans-per-storey.md))**: `MultiStoreyPlanGenerator<TParameters, TPresets>` (`Lod.Core.Plans`) is the sibling of `PlanGenerator` for a family whose plan differs per storey: `Generate` returns `Result<IReadOnlyList<IGeneratedPlan>>`, one ordinary plan per storey, bottom-up, each with the provenance parameters `Storey` (from 0) and `StoreyElevation` (S8.8, the storey's base elevation in m, read by the previews through `StoreyProvenance.ElevationOf`, which follows operations of one input and is 0 otherwise, D-108); the two bases share the preset checks, surfaces, windows, and provenance (`PlanBuilder`, internal). `SteppedBandGenerator` (`SYN-TYP-012`) is the first such generator. The floor aggregators take the storeys as floor entries with multiplier 1; no pipeline type changes.
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
