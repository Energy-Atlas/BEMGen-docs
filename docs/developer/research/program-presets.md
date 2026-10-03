# Program Presets

> **Status:** Current as of S8.8 (`v0.8.7`) · **Date:** 2026-10-02 · **Decisions:** D-009, D-024, D-026, D-038, D-039, D-047, D-061, D-079, D-094, D-097, D-108; ADR-014
>
> **Read this first:** the presets that ship with BEMGen (`ExampleResidentialPresets` and, since S8.4, `ExampleNonResidentialPresets`) hold **illustrative round numbers chosen for development and tests, and which of them are conditioned is an illustrative choice too. They are NOT taken from the DOE prototype buildings or from any standard.** Sourced presets are an open research input (§3).

A program preset describes the energy-relevant program of one space type. This document defines what a preset contains, lists the example presets and their values, records how S1 deviates from the original plan for sourced values, states which prototype assumptions BEMGen deliberately does not reproduce, and explains how to build custom presets.

## 1. What a program preset is

A program preset carries everything BEMGen assigns to a space of one type: its loads with their schedules, whether it is conditioned and, if so, its heating and cooling setpoints, and its window parameter (D-024, D-038). There is one preset per space type. Rooms are never modelled: at the most detailed level (Z0) a dwelling unit is one zone per storey (D-009, D-085), and a non-residential floor has one zone per department, a contiguous group of rooms of one program (D-097, ADR-014).

In code a preset is a `ProgramPreset` (`src/Lod.Core/Programs/ProgramPreset.cs`):

| Member | Meaning | Rejected with diagnostic |
| --- | --- | --- |
| `Name` | Display name; descriptive only: it appears in reports, provenance, and messages and is never used for matching (D-061) | `EmptyName` when empty or white space |
| `SpaceType` | The space type the preset applies to: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, and since S8.4 the non-residential types `Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, and `ActivityHall` (ADR-014). (`Mixed` denotes a simplified zone that combines several space types.) | — |
| `Program` | A `ZoneProgram`: at most one load per load type and basis, each with a fraction schedule, plus a `Thermostat` (heating and cooling setpoint schedules in °C) for a conditioned space, or no thermostat for an unconditioned one (§1.1, §1.2) | see §1.1 |
| `WindowToWallRatio` | Window-to-wall ratio, the single window parameter (D-026) | `WindowToWallRatio` when outside [0, 1) |

A plan generator takes one preset per space type it places, as a typed record (D-061): the linear plan generator takes `LinearPlanPresets(DwellingUnit, Corridor, Stair)`, and in Grasshopper the *Linear Plan Generator* has the three required inputs *Dwelling Unit*, *Corridor*, and *Stair*. A preset whose space type differs from its input's is an error (`PresetSpaceTypeMismatch`); each zone gets the preset of its space type. An any-program preset (S8.8, D-108) has no space type (`SpaceType` is `null`): `preset.AsAnyProgram()` returns any preset without its space type and with every other value unchanged, and every input of every generator accepts it; the zones keep the input's space type, take the preset's program and WWR, and the plan's provenance records `AnyProgramPreset.<Input>=<name>`. (Until S4.1 presets were passed as a `ProgramPresetSet`, a list with at most one preset per space type.)

A preset can also be described by its plain values, `PresetValues`: name, space type, WWR, *Conditioned*, constant heating and cooling setpoints (°C), and loads (`PresetLoadValue`: type, basis, value, fraction schedule). `PresetValues.ToPreset()` builds the `ProgramPreset`; for a conditioned preset the setpoint schedules are constant temperature schedules named `"{Name} Heating Setpoint"` and `"{Name} Cooling Setpoint"`, and for an unconditioned preset the setpoints are ignored. Every invalid value is reported at once, with the diagnostics of §1.1.

**Windows.** Walls carry explicit windows (D-039). The S2 linear plan generator uses the preset's WWR for one simple rule: one window centred on each outdoor wall of a zone, with area = WWR × wall area (D-026). Where zones are merged and walls are rebuilt, each outdoor wall gets one window centred on it with the glazed area of the source windows it covers, shaped by the same rule, so the preset's glazing is conserved per wall, façade, orientation, and building (D-079, S5).

### 1.1 Loads, bases, and schedules

A load is a `LoadDefinition`: a `LoadType`, a `LoadBasis`, a non-negative design value expressed per that basis, and a fraction schedule. Its **design magnitude** is value × basis quantity, and its scheduled magnitude at hour *t* is design magnitude × *s*(*t*) (ADR-007).

| `LoadType` | Design magnitude |
| --- | --- |
| `Occupancy` | people |
| `Lighting` | W |
| `ElectricEquipment` | W |
| `GasEquipment` | W |
| `DomesticHotWater` | m³/h (peak flow) |
| `Ventilation` | m³/h |
| `Infiltration` | m³/h |

| `LoadBasis` | Value is expressed per | Basis quantity of a zone | Example value units |
| --- | --- | --- | --- |
| `PerFloorArea` | m² of floor area | floor area, m² | W/m², people/m² |
| `PerPerson` | occupant | design occupants (the summed magnitude of the zone's occupancy loads) | m³/h per person |
| `Absolute` | zone | 1 | W, people |
| `PerExteriorWallArea` | m² of gross exterior wall | area of walls with an outdoor boundary, windows included, m² | m³/h per m² |
| `AirChangesPerHour` | zone air volume per hour | volume, m³ | 1/h |

Validation, with the diagnostic code each rule raises:

- A load value must be finite and non-negative (`LoadValue`).
- Occupancy is expressed only `PerFloorArea` or `Absolute` (`LoadBasisNotAllowed`).
- A load needs a fraction schedule (`ScheduleKindMismatch`); a thermostat's setpoints need temperature schedules (`ScheduleKindMismatch`, from `Thermostat.Create`).
- A program has at most one load per load type and basis (`DuplicateLoadType`). A load type may appear in several bases, for example ventilation per person plus per floor area; these components add up (D-047).
- A per-person load needs an occupancy load in the same program (`PerPersonWithoutOccupancy`).

Schedules hold 8760 hourly values for a non-leap year (ADR-003). A `Fraction` schedule's values lie in [0, 1]; a `Temperature` schedule holds finite values in °C. `Schedule.FromDailyProfiles` builds a year from one 24-hour weekday profile (Monday to Friday) and one weekend profile (Saturday and Sunday), given the weekday of 1 January; holidays are not modelled.

### 1.2 Conditioning

Conditioning comes from the program preset (D-038). A preset whose program has a `Thermostat` is conditioned, with the thermostat's heating and cooling setpoint schedules; a preset without one is unconditioned and has no setpoints (`ZoneProgram.IsConditioned` is `false`).

When a plan simplifier merges zones, the merged zone is conditioned if any source contributing floor area to it is conditioned ("any conditioned wins"). Its setpoints are floor-area weighted over the conditioned sources only, `T*(t) = Σ wᵢTᵢ(t) / Σ wᵢ` with `wᵢ` the transferred floor area of conditioned source *i*: a prescribed control rule, not a conservation invariant (ADR-005). Merging conditioned and unconditioned spaces can therefore enlarge the conditioned floor area; from S3 on, validation reports that change without enforcing it, because it is a consequence of the zoning simplification under study (D-038).

## 2. Example presets

> **The values below, and the choice of which spaces are conditioned, are illustrative and chosen for development and tests. They are NOT taken from the DOE prototype buildings, from any standard, or from measured data. Do not use them as research inputs, and do not present results obtained with them as representative of any prototype or real building.**

### 2.1 Residential presets

`src/Lod.Core/Programs/ExampleResidentialPresets.cs` defines one preset for each space type that the S2 linear plan generator places: dwelling unit, corridor, and stair, each as `PresetValues` (`DwellingUnitValues`, `CorridorValues`, `StairValues`) and as the preset built from them (`DwellingUnit`, `Corridor`, `Stair`). The Grasshopper components *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset* use these values as the defaults of their inputs (§5). Tests in S1 and in later stages use these presets, so changing a value changes test expectations and snapshots.

| Preset (`Name`) | Space type | Conditioning | Heating setpoint | Cooling setpoint | WWR |
| --- | --- | --- | --- | --- | --- |
| `Example Dwelling Unit` | `DwellingUnit` | conditioned | 21 °C, constant (`Example Dwelling Unit Heating Setpoint`) | 24 °C, constant (`Example Dwelling Unit Cooling Setpoint`) | 0.3 |
| `Example Corridor` | `Corridor` | conditioned | 21 °C, constant (`Example Corridor Heating Setpoint`) | 24 °C, constant (`Example Corridor Cooling Setpoint`) | 0.2 |
| `Example Stair` | `Stair` | unconditioned | none | none | 0.1 |

The stair is unconditioned as an illustrative choice, so that the conditioning rule of §1.2 is exercised by the pipeline's tests (for example, merging the stair with conditioned zones in S3). It says nothing about how any prototype conditions its stairs.

| Preset | Load type | Basis | Value | Schedule |
| --- | --- | --- | --- | --- |
| Dwelling unit | `Occupancy` | `PerFloorArea` | 0.03 people/m² | `Example Dwelling Occupancy`: weekday and weekend profiles below |
| Dwelling unit | `Lighting` | `PerFloorArea` | 5.0 W/m² | `Example Dwelling Lighting`: weekday and weekend profiles below |
| Dwelling unit | `ElectricEquipment` | `PerFloorArea` | 5.0 W/m² | `Example Dwelling Equipment`: constant 0.5 |
| Dwelling unit | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |
| Corridor | `Lighting` | `PerFloorArea` | 5.0 W/m² | `Example Always On`: constant 1.0 |
| Corridor | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |
| Stair | `Lighting` | `PerFloorArea` | 3.0 W/m² | `Example Always On`: constant 1.0 |
| Stair | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |

No example preset defines `GasEquipment`, `DomesticHotWater`, or `Ventilation`, and the corridor and stair presets have no occupancy load.

The dwelling-unit profiles are fractions per hour of the day (hour 0 is the first hour of the day). The year starts on a Monday; Monday to Friday use the weekday profile, Saturday and Sunday the weekend profile.

| Hour of day | Occupancy, weekday | Occupancy, weekend | Lighting, weekday | Lighting, weekend |
| --- | --- | --- | --- | --- |
| 0 | 1.0 | 1.0 | 0.1 | 0.1 |
| 1 | 1.0 | 1.0 | 0.1 | 0.1 |
| 2 | 1.0 | 1.0 | 0.1 | 0.1 |
| 3 | 1.0 | 1.0 | 0.1 | 0.1 |
| 4 | 1.0 | 1.0 | 0.1 | 0.1 |
| 5 | 1.0 | 1.0 | 0.2 | 0.1 |
| 6 | 0.8 | 1.0 | 0.4 | 0.2 |
| 7 | 0.5 | 1.0 | 0.4 | 0.3 |
| 8 | 0.3 | 0.8 | 0.2 | 0.4 |
| 9 | 0.2 | 0.7 | 0.1 | 0.3 |
| 10 | 0.2 | 0.6 | 0.1 | 0.2 |
| 11 | 0.2 | 0.6 | 0.1 | 0.2 |
| 12 | 0.3 | 0.6 | 0.1 | 0.2 |
| 13 | 0.2 | 0.6 | 0.1 | 0.2 |
| 14 | 0.2 | 0.6 | 0.1 | 0.2 |
| 15 | 0.3 | 0.7 | 0.1 | 0.2 |
| 16 | 0.5 | 0.8 | 0.2 | 0.3 |
| 17 | 0.7 | 0.9 | 0.5 | 0.5 |
| 18 | 0.9 | 0.9 | 0.8 | 0.8 |
| 19 | 0.9 | 1.0 | 0.9 | 0.9 |
| 20 | 1.0 | 1.0 | 0.9 | 0.9 |
| 21 | 1.0 | 1.0 | 0.7 | 0.7 |
| 22 | 1.0 | 1.0 | 0.4 | 0.4 |
| 23 | 1.0 | 1.0 | 0.2 | 0.2 |

### 2.2 Non-residential presets (S8.4)

> **The values below are illustrative, like those of §2.1: plausible round numbers for development and tests, NOT taken from the DOE prototype buildings, from any standard, or from measured data.** Their reasons are recorded in [ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md).

`src/Lod.Core/Programs/ExampleNonResidentialPresets.cs` defines one preset for each space type that the non-residential families place (D-094, D-097): the twelve new types and `Core`, `Lobby`, and `Service`. Each is available as `PresetValues` (`OfficeValues`, …, `ServiceValues`) and as the preset built from them (`Office`, …, `Service`); `SpaceTypes`, `ValuesOf(SpaceType)`, and `PresetOf(SpaceType)` list and look them up. Every one is conditioned. The Grasshopper components *Office Preset* to *Service Preset* use these values as the defaults of their inputs (§5).

| Preset (`Name`) | Space type | Heating | Cooling | WWR |
| --- | --- | --- | --- | --- |
| `Example Office` | `Office` | 21 °C | 24 °C | 0.4 |
| `Example Core` | `Core` | 21 °C | 24 °C | 0 |
| `Example Retail` | `Retail` | 20 °C | 24 °C | 0.3 |
| `Example Mall` | `Mall` | 20 °C | 24 °C | 0.2 |
| `Example Kitchen` | `Kitchen` | 18 °C | 26 °C | 0.1 |
| `Example Dining` | `Dining` | 21 °C | 24 °C | 0.4 |
| `Example Operating Theatre` | `OperatingTheatre` | 20 °C | 22 °C | 0 |
| `Example Clean Corridor` | `CleanCorridor` | 20 °C | 24 °C | 0.1 |
| `Example Dirty Corridor` | `DirtyCorridor` | 20 °C | 24 °C | 0.1 |
| `Example Clinical Support` | `ClinicalSupport` | 21 °C | 24 °C | 0.2 |
| `Example Care Bedroom` | `CareBedroom` | 22 °C | 25 °C | 0.3 |
| `Example Care Communal` | `CareCommunal` | 22 °C | 25 °C | 0.4 |
| `Example Lobby` | `Lobby` | 20 °C | 24 °C | 0.5 |
| `Example Activity Hall` | `ActivityHall` | 18 °C | 25 °C | 0.2 |
| `Example Service` | `Service` | 18 °C | 26 °C | 0.1 |

| Preset | Load type | Basis | Value | Schedule (annual sum of fractions) |
| --- | --- | --- | --- | --- |
| Office | `Occupancy` | `PerFloorArea` | 0.1 people/m² | `Example Office Occupancy` (2231.55) |
| Office | `Lighting` | `PerFloorArea` | 10 W/m² | `Example Office Lighting` (2695.65) |
| Office | `ElectricEquipment` | `PerFloorArea` | 10 W/m² | `Example Office Equipment` (3526.8) |
| Office | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Core | `Lighting` | `PerFloorArea` | 5 W/m² | `Example Office Lighting` (2695.65) |
| Core | `ElectricEquipment` | `PerFloorArea` | 3 W/m² | `Example Office Equipment` (3526.8) |
| Core | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Retail | `Occupancy` | `PerFloorArea` | 0.2 people/m² | `Example Retail Occupancy` (2414.4) |
| Retail | `Lighting` | `PerFloorArea` | 15 W/m² | `Example Retail Lighting` (4547.5) |
| Retail | `ElectricEquipment` | `PerFloorArea` | 5 W/m² | `Example Retail Equipment` (5100) |
| Retail | `Infiltration` | `AirChangesPerHour` | 0.5 1/h | `Example Always On` (8760) |
| Mall | `Occupancy` | `PerFloorArea` | 0.1 people/m² | `Example Retail Occupancy` (2414.4) |
| Mall | `Lighting` | `PerFloorArea` | 10 W/m² | `Example Retail Lighting` (4547.5) |
| Mall | `Infiltration` | `AirChangesPerHour` | 0.8 1/h | `Example Always On` (8760) |
| Kitchen | `Occupancy` | `PerFloorArea` | 0.05 people/m² | `Example Kitchen Staff` (2244.6) |
| Kitchen | `Lighting` | `PerFloorArea` | 12 W/m² | `Example Kitchen Hours` (2610) |
| Kitchen | `ElectricEquipment` | `PerFloorArea` | 30 W/m² | `Example Kitchen Electric` (2952.6) |
| Kitchen | `GasEquipment` | `PerFloorArea` | 40 W/m² | `Example Kitchen Gas` (1122.3) |
| Kitchen | `Ventilation` | `AirChangesPerHour` | 15 1/h | `Example Kitchen Hours` (2610) |
| Kitchen | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Dining | `Occupancy` | `PerFloorArea` | 0.6 people/m² | `Example Dining Occupancy` (809.1) |
| Dining | `Lighting` | `PerFloorArea` | 10 W/m² | `Example Dining Hours` (2349) |
| Dining | `ElectricEquipment` | `PerFloorArea` | 2 W/m² | `Example Dining Hours` (2349) |
| Dining | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Operating Theatre | `Occupancy` | `PerFloorArea` | 0.1 people/m² | `Example Theatre Sessions` (2871) |
| Operating Theatre | `Lighting` | `PerFloorArea` | 25 W/m² | `Example Theatre Services` (4048.8) |
| Operating Theatre | `ElectricEquipment` | `PerFloorArea` | 30 W/m² | `Example Theatre Services` (4048.8) |
| Operating Theatre | `Ventilation` | `AirChangesPerHour` | 20 1/h | `Example Theatre Ventilation` (5946) |
| Operating Theatre | `Infiltration` | `AirChangesPerHour` | 0.1 1/h | `Example Always On` (8760) |
| Clean Corridor | `Lighting` | `PerFloorArea` | 8 W/m² | `Example Always On` (8760) |
| Clean Corridor | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Dirty Corridor | `Lighting` | `PerFloorArea` | 8 W/m² | `Example Always On` (8760) |
| Dirty Corridor | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Clinical Support | `Occupancy` | `PerFloorArea` | 0.05 people/m² | `Example Theatre Sessions` (2871) |
| Clinical Support | `Lighting` | `PerFloorArea` | 12 W/m² | `Example Theatre Services` (4048.8) |
| Clinical Support | `ElectricEquipment` | `PerFloorArea` | 10 W/m² | `Example Theatre Services` (4048.8) |
| Clinical Support | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Care Bedroom | `Occupancy` | `PerFloorArea` | 0.04 people/m² | `Example Care Bedroom Occupancy` (5803.5) |
| Care Bedroom | `Lighting` | `PerFloorArea` | 6 W/m² | `Example Care Bedroom Lighting` (2226.5) |
| Care Bedroom | `ElectricEquipment` | `PerFloorArea` | 3 W/m² | `Example Care Bedroom Equipment` (4380) |
| Care Bedroom | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Care Communal | `Occupancy` | `PerFloorArea` | 0.15 people/m² | `Example Care Communal Occupancy` (3777.75) |
| Care Communal | `Lighting` | `PerFloorArea` | 10 W/m² | `Example Care Communal Hours` (6132) |
| Care Communal | `ElectricEquipment` | `PerFloorArea` | 5 W/m² | `Example Care Communal Hours` (6132) |
| Care Communal | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Lobby | `Occupancy` | `PerFloorArea` | 0.1 people/m² | `Example Community Occupancy` (2444.5) |
| Lobby | `Lighting` | `PerFloorArea` | 10 W/m² | `Example Community Hours` (5267) |
| Lobby | `Infiltration` | `AirChangesPerHour` | 0.6 1/h | `Example Always On` (8760) |
| Activity Hall | `Occupancy` | `PerFloorArea` | 0.1 people/m² | `Example Community Occupancy` (2444.5) |
| Activity Hall | `Lighting` | `PerFloorArea` | 12 W/m² | `Example Community Hours` (5267) |
| Activity Hall | `ElectricEquipment` | `PerFloorArea` | 2 W/m² | `Example Community Hours` (5267) |
| Activity Hall | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |
| Service | `Lighting` | `PerFloorArea` | 6 W/m² | `Example Community Hours` (5267) |
| Service | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On` (8760) |

Ventilation is given only for the kitchen (hood extract) and the operating theatre; no preset defines `DomesticHotWater`. The year starts on a Monday. Monday to Friday use the weekday profile and Saturday and Sunday the weekend profile, except the three retail schedules, which have their own Saturday and Sunday profiles. Hourly fractions (hour 0 is the first hour of the day):

**Office and core.**

| Hour of day | Office Occupancy, weekday | Office Lighting, weekday | Office Equipment, weekday |
| --- | --- | --- | --- |
| 0 | 0 | 0.05 | 0.2 |
| 1 | 0 | 0.05 | 0.2 |
| 2 | 0 | 0.05 | 0.2 |
| 3 | 0 | 0.05 | 0.2 |
| 4 | 0 | 0.05 | 0.2 |
| 5 | 0 | 0.05 | 0.2 |
| 6 | 0 | 0.05 | 0.2 |
| 7 | 0.1 | 0.3 | 0.4 |
| 8 | 0.5 | 0.8 | 0.7 |
| 9 | 0.95 | 0.9 | 0.9 |
| 10 | 0.95 | 0.9 | 0.9 |
| 11 | 0.95 | 0.9 | 0.9 |
| 12 | 0.5 | 0.8 | 0.7 |
| 13 | 0.95 | 0.9 | 0.9 |
| 14 | 0.95 | 0.9 | 0.9 |
| 15 | 0.95 | 0.9 | 0.9 |
| 16 | 0.95 | 0.9 | 0.9 |
| 17 | 0.5 | 0.6 | 0.6 |
| 18 | 0.2 | 0.3 | 0.4 |
| 19 | 0.1 | 0.2 | 0.3 |
| 20 | 0 | 0.05 | 0.2 |
| 21 | 0 | 0.05 | 0.2 |
| 22 | 0 | 0.05 | 0.2 |
| 23 | 0 | 0.05 | 0.2 |

Weekend: occupancy 0, lighting 0.05, equipment 0.2 all day.

**Retail and mall** (Saturday and Sunday differ).

| Hour of day | Retail Occupancy, weekday | Saturday | Sunday | Retail Lighting, weekday and Saturday | Sunday | Retail Equipment, weekday and Saturday | Sunday |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 1 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 2 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 3 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 4 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 5 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 6 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 7 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 8 | 0 | 0 | 0 | 0.5 | 0.1 | 0.6 | 0.3 |
| 9 | 0.3 | 0.5 | 0 | 1 | 0.1 | 0.9 | 0.3 |
| 10 | 0.5 | 0.8 | 0 | 1 | 0.5 | 0.9 | 0.6 |
| 11 | 0.6 | 1 | 0.4 | 1 | 1 | 0.9 | 0.9 |
| 12 | 0.8 | 1 | 0.6 | 1 | 1 | 0.9 | 0.9 |
| 13 | 0.8 | 1 | 0.7 | 1 | 1 | 0.9 | 0.9 |
| 14 | 0.6 | 1 | 0.7 | 1 | 1 | 0.9 | 0.9 |
| 15 | 0.6 | 1 | 0.6 | 1 | 1 | 0.9 | 0.9 |
| 16 | 0.7 | 0.9 | 0.4 | 1 | 1 | 0.9 | 0.9 |
| 17 | 0.8 | 0.8 | 0 | 1 | 0.5 | 0.9 | 0.6 |
| 18 | 0.7 | 0.6 | 0 | 1 | 0.1 | 0.9 | 0.3 |
| 19 | 0.4 | 0.3 | 0 | 1 | 0.1 | 0.9 | 0.3 |
| 20 | 0 | 0 | 0 | 0.5 | 0.1 | 0.6 | 0.3 |
| 21 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 22 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |
| 23 | 0 | 0 | 0 | 0.1 | 0.1 | 0.3 | 0.3 |

**Kitchen and dining** (weekday; weekend: kitchen electric 0.2, every other schedule 0).

| Hour of day | Kitchen Staff | Kitchen Hours | Kitchen Electric | Kitchen Gas | Dining Occupancy | Dining Hours |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 6 | 0.3 | 1 | 0.4 | 0 | 0 | 0 |
| 7 | 0.8 | 1 | 0.6 | 0.3 | 0.1 | 1 |
| 8 | 1 | 1 | 0.6 | 0.3 | 0.2 | 1 |
| 9 | 1 | 1 | 0.6 | 0.3 | 0.1 | 1 |
| 10 | 1 | 1 | 0.6 | 0.6 | 0.1 | 1 |
| 11 | 1 | 1 | 0.9 | 1 | 0.4 | 1 |
| 12 | 1 | 1 | 1 | 1 | 1 | 1 |
| 13 | 1 | 1 | 0.9 | 0.6 | 0.8 | 1 |
| 14 | 1 | 1 | 0.6 | 0.2 | 0.3 | 1 |
| 15 | 0.5 | 1 | 0.4 | 0 | 0.1 | 1 |
| 16 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 20 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 21 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 22 | 0 | 0 | 0.2 | 0 | 0 | 0 |
| 23 | 0 | 0 | 0.2 | 0 | 0 | 0 |

**Operating suite** (weekday; weekend: sessions 0, services 0.2, ventilation 0.5).

| Hour of day | Theatre Sessions | Theatre Services | Theatre Ventilation |
| --- | --- | --- | --- |
| 0 | 0 | 0.2 | 0.5 |
| 1 | 0 | 0.2 | 0.5 |
| 2 | 0 | 0.2 | 0.5 |
| 3 | 0 | 0.2 | 0.5 |
| 4 | 0 | 0.2 | 0.5 |
| 5 | 0 | 0.2 | 0.5 |
| 6 | 0 | 0.2 | 0.5 |
| 7 | 0.5 | 0.6 | 1 |
| 8 | 1 | 1 | 1 |
| 9 | 1 | 1 | 1 |
| 10 | 1 | 1 | 1 |
| 11 | 1 | 1 | 1 |
| 12 | 1 | 1 | 1 |
| 13 | 1 | 1 | 1 |
| 14 | 1 | 1 | 1 |
| 15 | 1 | 1 | 1 |
| 16 | 1 | 1 | 1 |
| 17 | 1 | 1 | 1 |
| 18 | 0.5 | 0.6 | 1 |
| 19 | 0 | 0.2 | 0.5 |
| 20 | 0 | 0.2 | 0.5 |
| 21 | 0 | 0.2 | 0.5 |
| 22 | 0 | 0.2 | 0.5 |
| 23 | 0 | 0.2 | 0.5 |

**Elder care** (every day the same; `Example Care Bedroom Equipment` is constant 0.5).

| Hour of day | Care Bedroom Occupancy | Care Bedroom Lighting | Care Communal Occupancy | Care Communal Hours |
| --- | --- | --- | --- | --- |
| 0 | 1 | 0.05 | 0.05 | 0.2 |
| 1 | 1 | 0.05 | 0.05 | 0.2 |
| 2 | 1 | 0.05 | 0.05 | 0.2 |
| 3 | 1 | 0.05 | 0.05 | 0.2 |
| 4 | 1 | 0.05 | 0.05 | 0.2 |
| 5 | 1 | 0.05 | 0.05 | 0.2 |
| 6 | 1 | 0.3 | 0.05 | 0.2 |
| 7 | 0.8 | 0.6 | 0.3 | 1 |
| 8 | 0.5 | 0.4 | 0.9 | 1 |
| 9 | 0.3 | 0.1 | 0.6 | 1 |
| 10 | 0.3 | 0.1 | 0.7 | 1 |
| 11 | 0.3 | 0.1 | 0.7 | 1 |
| 12 | 0.2 | 0.1 | 1 | 1 |
| 13 | 0.4 | 0.1 | 0.6 | 1 |
| 14 | 0.4 | 0.1 | 0.7 | 1 |
| 15 | 0.4 | 0.1 | 0.7 | 1 |
| 16 | 0.3 | 0.2 | 0.7 | 1 |
| 17 | 0.2 | 0.4 | 1 | 1 |
| 18 | 0.4 | 0.6 | 0.8 | 1 |
| 19 | 0.6 | 0.8 | 0.6 | 1 |
| 20 | 0.8 | 0.8 | 0.4 | 1 |
| 21 | 1 | 0.6 | 0.2 | 1 |
| 22 | 1 | 0.3 | 0.05 | 0.2 |
| 23 | 1 | 0.1 | 0.05 | 0.2 |

**Community: foyer, activity hall, support rooms.**

| Hour of day | Community Occupancy, weekday | weekend | Community Hours, weekday | weekend |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 0 |
| 3 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 0 | 0 |
| 5 | 0 | 0 | 0 | 0 |
| 6 | 0 | 0 | 0 | 0 |
| 7 | 0 | 0 | 0 | 0 |
| 8 | 0 | 0 | 1 | 1 |
| 9 | 0.2 | 0.8 | 1 | 1 |
| 10 | 0.2 | 0.8 | 1 | 1 |
| 11 | 0.2 | 0.8 | 1 | 1 |
| 12 | 0.2 | 0.8 | 1 | 1 |
| 13 | 0.2 | 0.8 | 1 | 1 |
| 14 | 0.2 | 0.8 | 1 | 1 |
| 15 | 0.2 | 0.8 | 1 | 1 |
| 16 | 0.2 | 0.8 | 1 | 1 |
| 17 | 0.6 | 0.8 | 1 | 1 |
| 18 | 0.9 | 0.8 | 1 | 1 |
| 19 | 0.9 | 0.8 | 1 | 1 |
| 20 | 0.9 | 0.4 | 1 | 1 |
| 21 | 0.6 | 0 | 1 | 0 |
| 22 | 0.2 | 0 | 1 | 0 |
| 23 | 0 | 0 | 0 | 0 |


## 3. Sourced presets: an open research input

The v2 roadmap (§4, S1, slice `feature/programs-presets`) planned a `DefaultResidentialPresets` class "with DOE mid-rise apartment values as the starting point", with sources cited in this document. **S1 deviates from that plan.** It ships `ExampleResidentialPresets` with the illustrative values and conditioning choices of §2 instead, and the class name says so, so that no result can be mistaken for one based on prototype values. Roadmap v3 records sourced presets as open point 4 of its §7.

Sourcing preset values from the DOE mid-rise apartment prototype, with citations, is an **open research input for the researcher**: loads, schedules, and which spaces are conditioned. It does not block S2 to S4: their tests check geometry and conservation invariants, which hold for any valid preset values. When sourced presets are added, they must:

1. cite, for every value and for each space type's conditioning status, the source document or model file, its version, and where in it the value is found (table, object, or field);
2. state every conversion applied, including unit conversions to people, W, and m³/h, the mapping from the prototype's space types to BEMGen's `SpaceType`, and the mapping of the prototype's conditioning to conditioned or unconditioned (§4, item 1);
3. be added alongside `ExampleResidentialPresets` (a new presets class, or presets built with the S2 components), leaving the example presets unchanged so existing tests keep their meaning;
4. be recorded in the decision log (D-007) and in this document.

## 4. Prototype assumptions deliberately not reproduced

Even with sourced values, BEMGen deliberately does not reproduce the following assumptions of a DOE prototype. Results must not be presented as if it did.

1. **Conditioning detail (D-038).** A preset is either conditioned, with one heating and one cooling setpoint schedule, or unconditioned, with no setpoints. Any other conditioning arrangement a source describes must be mapped to one of these two, and the mapping stated (§3). HVAC systems themselves are not part of a preset (item 5).
2. **Zoning inside dwelling units (D-009).** Rooms are never modelled. Z0 has at most one zone per dwelling unit; non-dwelling spaces are their own zones.
3. **Window layout (D-026, D-039).** The S2 generator places one window centred on each outdoor wall, sized by the preset's WWR, not the prototype's window geometry.
4. **Calendar.** Schedules are 8760 hourly values over a non-leap year (ADR-003). Schedules built from daily profiles use one weekday and one weekend profile; holidays and special days are not modelled.
5. **Systems and envelope.** A program preset holds loads, schedules, conditioning with setpoints, and WWR only: no HVAC system, construction, or material data. Constructions come from a separate envelope preset, the same at every level of detail ([envelope presets](envelope-presets.md), S6, ADR-010). The pipeline ends at Grasshopper-ready inputs without simulation (D-016); what the IDF export contains is decided in ADR-010 (S6).

## 5. Building custom presets

### In C# (available from S1)

Every factory returns a `Result<T>`. Check `IsSuccess` and read `Diagnostics` before using a value built from unvalidated input: `Value` throws an `InvalidOperationException` that lists the errors. The numbers below are placeholders, like the example presets.

```csharp
using System;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;
using Lod.Generators.Linear;

double[] weekday = Enumerable.Repeat(0.5, 24).ToArray();
double[] weekend = Enumerable.Repeat(0.8, 24).ToArray();
Schedule occupied = Schedule.FromDailyProfiles("My Occupancy", ScheduleKind.Fraction, weekday, weekend, DayOfWeek.Monday).Value;
Schedule alwaysOn = Schedule.Constant("My Always On", ScheduleKind.Fraction, 1.0).Value;

// A conditioned dwelling unit: its program has a thermostat.
Result<Thermostat> thermostat = Thermostat.Create(
    Schedule.Constant("My Heating Setpoint", ScheduleKind.Temperature, 20.0).Value,
    Schedule.Constant("My Cooling Setpoint", ScheduleKind.Temperature, 25.0).Value);

Result<ZoneProgram> unitProgram = ZoneProgram.Create(
    new[]
    {
        LoadDefinition.Create(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.02, occupied).Value,
        LoadDefinition.Create(LoadType.Ventilation, LoadBasis.PerPerson, 30.0, occupied).Value,
        LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 4.0, alwaysOn).Value,
    },
    thermostat.Value);

// An unconditioned lobby: no thermostat, so no setpoints.
Result<ZoneProgram> lobbyProgram = ZoneProgram.Create(
    new[] { LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 3.0, alwaysOn).Value },
    null);

Result<ProgramPreset> unit = ProgramPreset.Create("My Dwelling Unit", SpaceType.DwellingUnit, unitProgram.Value, 0.25);
Result<ProgramPreset> lobby = ProgramPreset.Create("My Lobby", SpaceType.Lobby, lobbyProgram.Value, 0.4);

// From S4.1: change values of an example preset and build a preset from them.
Result<ProgramPreset> corridor = (ExampleResidentialPresets.CorridorValues with { Name = "My Corridor", WindowToWallRatio = 0.25 }).ToPreset();

// The linear plan generator takes one preset per space type (D-061).
var presets = new LinearPlanPresets(unit.Value, corridor.Value, ExampleResidentialPresets.Stair);
```

### In Grasshopper (from S2)

S2 adds components that wrap the same factories: *Schedule* (an 8760-hour schedule from a 24-hour weekday and weekend profile), *Load*, and *Program Preset* (any space type, with a *Conditioned* input; conditioned presets need both setpoints). Invalid inputs surface the diagnostics listed in §1 as component runtime messages.

S4.1 adds one default preset component per space type of the linear plan, *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset*, and deletes *Example Residential Presets* (D-061). Every input of a default preset component has a default, the values of §2, so the component works with nothing connected: Name, WWR, Conditioned, Heating (°C), Cooling (°C), and per load a value input (people/m², W/m², or 1/h, as in its description) and an optional schedule input that replaces the built-in schedule when connected. Each shows the remark "Illustrative values; not sourced from DOE prototypes or standards." S8.4 adds one default preset component per non-residential space type of §2.2, *Office Preset*, *Core Preset*, *Retail Preset*, *Mall Preset*, *Kitchen Preset*, *Dining Preset*, *Operating Theatre Preset*, *Clean Corridor Preset*, *Dirty Corridor Preset*, *Clinical Support Preset*, *Care Bedroom Preset*, *Care Communal Preset*, *Lobby Preset*, *Activity Hall Preset*, and *Service Preset*, with the same inputs; *Gas Equipment* is in W/m², and *Ventilation* and *Infiltration* are in 1/h. Their inputs and outputs are listed in [pipeline.md](../architecture/pipeline.md#grasshopper-components-through-s88).

S8.8 moves the eighteen default preset components to their own panel, *1 Program Presets*; *Schedule*, *Load*, and *Program Preset* stay in *1 Program*, with the new parameter *Any Program Preset* (AnyP, D-108). Wire any preset into *Any Program Preset* and its output into any preset input of any generator to apply that program to the input's space type: for example an *Office Preset* through *Any Program Preset* into the *Corridor* input of the *Linear Plan Generator* gives the corridor the office program while it stays a `Corridor` zone. The preset keeps its name, loads, schedules, conditioning, setpoints, and WWR, and the plan's provenance records the use.
