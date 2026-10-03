# ADR-014: Program types and department zoning

Status: Accepted (by the controller under D-098; provisional pending the owner's reading)

Date: 2026-10-02

Decisions: D-009, D-023, D-024, D-026, D-038, D-047, D-061, D-065, D-085, D-093, D-094, D-096, D-097, D-098, D-108, D-109; applies [ADR-005](ADR-005-conditioning-and-setpoints.md), [ADR-006](ADR-006-plan-generation-mechanism.md), and [ADR-007](ADR-007-load-basis-aggregation.md)

## Context

Through S8.3 every plan generator placed housing: dwelling units, stairs, and corridors, with the illustrative presets `ExampleResidentialPresets` (D-023, D-061). The four-source precedent set (D-093, [syn-typologies.md](../research/precedents/syn-typologies.md)) adds non-residential families, and D-094 puts every program type of the set in scope: retail, an operating suite, food service, office, elder care, and assembly or community uses. Each new space type needs its own typed program preset with explicit, documented assumptions (D-094), and D-097 zones a non-residential floor at its most detailed level per department: a contiguous group of rooms of one program in one part of the floor, not one zone per room or tenancy. This ADR fixes the new space types, one illustrative preset per type, and, for every new family, which rooms form one zone and which space type that zone has.

## Options considered

### Space types

1. **One generic `NonResidential` type with a program name.** Few enum values, but the program would be carried by a name, which D-061 and AGENTS.md forbid (semantics are explicit data, never encoded in names).
2. **Reuse `Other` with different presets.** A generator could not say which preset each zone takes: one slot per space type (D-061) needs distinct types.
3. **One space type per department program that a family places (chosen).** Explicit data, one typed preset slot per type, and the existing default-preset pattern (D-061, D-065) extends unchanged. Existing types are reused where they mean the same thing.

### Zoning of non-residential floors (settled by D-097)

Rooms or tenancies as zones would need a room layout the precedents do not give and would break the parity with housing, where a dwelling is never subdivided (D-009). One zone per department is the most detailed level; the simplifiers and aggregators coarsen it as for housing.

### A preset without a space type (S8.8, D-108)

D-108 asks for a preset that every program input of every plan generator accepts, made from any preset, built-in or general, while a preset that keeps its space type must still match its input.

1. **A `SpaceType` value `Any`.** One enum value, but `SpaceType` is the semantic category of a zone, and no zone would ever have this one; every switch over space types (preview colours, *Semantic Merge* grouping, *Convert2BEM*) would have to handle a value that never occurs on a zone, and `Other` and `Mixed` already mean something else.
2. **A flag beside a kept space type.** The preset would keep, say, `Kitchen` and say that it fits every input: two sources of truth, and a preset that reads `Kitchen` while it programs a dwelling.
3. **No space type (chosen).** `ProgramPreset.SpaceType` becomes `SpaceType?`, `null` meaning that the preset has no space type; `AsAnyProgram()` returns the preset without it. The absence is explicit data, nothing is inferred from a name (D-061), and the slot check needs one condition more.
4. **Matching by name or by a list of compatible types.** Names are descriptive only (D-061), and a compatibility table would be a research rule that no source supports.

## Decision

### Space types

`SpaceType` gets twelve values, appended after the existing ones so that existing values keep their order: `Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, `ActivityHall`. Three existing values gain a non-residential use without changing meaning: `Core` (an office service core: lifts, stairs, toilets, risers), `Lobby` (a public foyer), and `Service` (the support rooms of a foyer family: changing rooms, stores, toilets).

| Space type | Department it zones | Why its own type |
| --- | --- | --- |
| `Office` | an office work area | the work-area program of `017` |
| `Core` (reused) | an office service core | already "service or circulation core"; distinct from `Stair`, which stays the housing core |
| `Retail` | the shops of one mall wing, or one anchor store | shop program of `014`; anchors are shops with the same program |
| `Mall` | the public mall route | a conditioned public route with shop-hour occupancy, unlike a residential `Corridor` |
| `Kitchen` | food preparation and servery as one department | high equipment and extract ventilation (`016`) |
| `Dining` | the dining field | dense lunchtime occupancy (`016`) |
| `OperatingTheatre` | one bank of operating theatres | high equipment and ventilation (`015`) |
| `CleanCorridor` | the clean route of an operating suite | the separation of routes is the family's defining relation (`015-R002`), so the two routes are distinct data |
| `DirtyCorridor` | the dirty route | as above |
| `ClinicalSupport` | the support rooms of an operating suite | scrub, anaesthesia, stores, recovery, sluice (`015`) |
| `CareBedroom` | one group of care bedrooms | 24-hour occupied, warmer setpoints (`018`) |
| `CareCommunal` | the communal and service hub of a care home | day-long communal use with meal peaks (`018`) |
| `ActivityHall` | one activity hall | evening and weekend use, lower heating setpoint (`019`) |
| `Lobby` (reused) | a public foyer | already "entrance lobby" |
| `Service` (reused) | the support rooms of a foyer family | already "service space" |

`Mechanical`, `Other`, and `Mixed` are unchanged; `Mixed` remains the type of a simplified zone that combines several types. Names were checked against shorter alternatives: `OperatingTheatre` rather than `Surgery` (which also names a clinic), `CareBedroom` and `CareCommunal` rather than `Bedroom` (a room of a dwelling, never modelled, D-009).

### Presets: `ExampleNonResidentialPresets`

A new static class in `Lod.Core.Programs`, following `ExampleResidentialPresets`: for each of the fifteen types above a `…Values` (`PresetValues`) and the `ProgramPreset` built from it, named `Example <Type>` (`Example Office`, `Example Operating Theatre`, …). **The values are illustrative round numbers chosen to be plausible for development and tests (D-023). They are not taken from the DOE prototype buildings, from any standard, or from measured data**, and they are not research inputs; sourced presets remain an open research input ([program-presets.md](../research/program-presets.md) §3). Every preset is conditioned: each space is one that people occupy or pass through and that is normally heated (the residential stair is the only unconditioned example). The year starts on a Monday, as for the residential presets.

| Preset | WWR | Heating / cooling °C | Occupancy, people/m² | Lighting, W/m² | Equipment, W/m² | Ventilation, 1/h | Infiltration, 1/h |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Office | 0.4 | 21 / 24 | 0.10 office | 10 office lighting | 10 office equipment | — | 0.3 always on |
| Core | 0.0 | 21 / 24 | — | 5 office lighting | 3 office equipment | — | 0.3 always on |
| Retail | 0.3 | 20 / 24 | 0.20 retail | 15 retail lighting | 5 retail equipment | — | 0.5 always on |
| Mall | 0.2 | 20 / 24 | 0.10 retail | 10 retail lighting | — | — | 0.8 always on |
| Kitchen | 0.1 | 18 / 26 | 0.05 kitchen staff | 12 kitchen hours | 30 electric (kitchen electric), 40 gas (kitchen gas) | 15 kitchen hours | 0.3 always on |
| Dining | 0.4 | 21 / 24 | 0.60 dining | 10 dining hours | 2 dining hours | — | 0.3 always on |
| Operating theatre | 0.0 | 20 / 22 | 0.10 theatre sessions | 25 theatre services | 30 theatre services | 20 theatre ventilation | 0.1 always on |
| Clean corridor | 0.1 | 20 / 24 | — | 8 always on | — | — | 0.3 always on |
| Dirty corridor | 0.1 | 20 / 24 | — | 8 always on | — | — | 0.3 always on |
| Clinical support | 0.2 | 21 / 24 | 0.05 theatre sessions | 12 theatre services | 10 theatre services | — | 0.3 always on |
| Care bedroom | 0.3 | 22 / 25 | 0.04 care bedroom | 6 care bedroom lighting | 3 care bedroom equipment | — | 0.3 always on |
| Care communal | 0.4 | 22 / 25 | 0.15 care communal | 10 care communal hours | 5 care communal hours | — | 0.3 always on |
| Lobby | 0.5 | 20 / 24 | 0.10 community | 10 community hours | — | — | 0.6 always on |
| Activity hall | 0.2 | 18 / 25 | 0.10 community | 12 community hours | 2 community hours | — | 0.3 always on |
| Service | 0.1 | 18 / 26 | — | 6 community hours | — | — | 0.3 always on |

Every load is expressed per floor area except ventilation and infiltration, which are air changes per hour (ADR-007; the magnitude is m³/h = value × zone volume). Equipment is `ElectricEquipment` except the kitchen's 40 W/m² of `GasEquipment`. Ventilation (`LoadType.Ventilation`) is given only where the program clearly needs mechanical air beyond infiltration: the kitchen's extract hoods and the operating theatres' air changes. No preset defines `DomesticHotWater`.

**Reasons for the values.**

- **Office.** A typical open-plan density (one person per 10 m²), lighting and small-power densities of an office floor, and the glazing of a curtain-walled plate. **Core:** no occupancy of its own (people pass through, as in the residential corridor); lifts and riser fans as small equipment; WWR 0 because a core is enclosed by shafts and service rooms, so a core on a façade gets no window by default.
- **Retail and mall.** Shop-floor densities with display lighting; the mall is less dense and has no equipment. Heating 20 °C because customers keep their coats on. Higher infiltration for frequently opened entrances, highest for the mall, whose ends are the building's entrances.
- **Kitchen and dining.** The kitchen carries the cooking load (gas ranges, electric ovens, refrigeration and dishwashing) and a hood extract of 15 air changes while it operates; a wide 18–26 °C band because cooking heat dominates. The dining field is densely occupied around lunch.
- **Operating suite.** Theatres hold a team of about six in 60 m², high equipment and lighting, a tight 20–22 °C band, 20 air changes during sessions with a setback to half at night and at weekends, and very low infiltration because theatres are kept at positive pressure; WWR 0 because theatres are usually windowless. The clean and dirty corridors have the same values: their difference is the route, not the program, and two types keep the routes apart as data. Support rooms have a light, session-hour occupancy.
- **Elder care.** Residents are older and less active, so both setpoints are 1 °C warmer than for dwellings. Bedrooms are occupied at night and partly by day, every day; the communal hub is busy all day with meal peaks, and a care station keeps a little light and occupancy at night.
- **Community.** The foyer and halls are used for daytime classes and mostly in the evenings and at weekends; a sports hall is heated to 18 °C, and the foyer is glazed (WWR 0.5) with an entrance's infiltration. Support rooms (changing rooms, stores, toilets) are heated to a wide 18–26 °C band and have no occupancy of their own.

**Schedules.** Fractions per hour of the day (hour 0 is the first hour); Monday to Friday use the weekday profile, Saturday and Sunday the weekend profile, except the retail schedules, which have their own Saturday and Sunday profiles because shops trade longest on Saturday.

| Schedule (`Example …`) | Weekday | Weekend |
| --- | --- | --- |
| `Office Occupancy` | 0 until 7:00; 0.1, 0.5 (7–9); 0.95 (9–12); 0.5 (12–13); 0.95 (13–17); 0.5, 0.2, 0.1 (17–20); then 0 | 0 |
| `Office Lighting` | 0.05 until 7:00; 0.3, 0.8; 0.9 (9–12); 0.8; 0.9 (13–17); 0.6, 0.3, 0.2; then 0.05 | 0.05 |
| `Office Equipment` | 0.2 until 7:00; 0.4, 0.7; 0.9 (9–12); 0.7; 0.9 (13–17); 0.6, 0.4, 0.3; then 0.2 | 0.2 |
| `Retail Occupancy` | 0 until 9:00; 0.3, 0.5, 0.6, 0.8, 0.8, 0.6, 0.6, 0.7, 0.8, 0.7, 0.4 (9–20); then 0 | Saturday 0 until 9:00; 0.5, 0.8, 1.0 (11–16), 0.9, 0.8, 0.6, 0.3 (9–20); Sunday 0 until 11:00; 0.4, 0.6, 0.7, 0.7, 0.6, 0.4 (11–17); then 0 |
| `Retail Lighting` | 0.1 until 8:00; 0.5; 1.0 (9–20); 0.5; then 0.1 | Saturday as the weekday; Sunday 0.1 until 10:00; 0.5; 1.0 (11–17); 0.5; then 0.1 |
| `Retail Equipment` | 0.3 until 8:00; 0.6; 0.9 (9–20); 0.6; then 0.3 | Saturday as the weekday; Sunday 0.3 until 10:00; 0.6; 0.9 (11–17); 0.6; then 0.3 |
| `Kitchen Staff` | 0 until 6:00; 0.3, 0.8; 1.0 (8–15); 0.5; then 0 | 0 |
| `Kitchen Hours` | 1.0 from 6:00 to 16:00, else 0 | 0 |
| `Kitchen Electric` | 0.2 until 6:00; 0.4; 0.6 (7–11); 0.9, 1.0, 0.9 (11–14); 0.6, 0.4; then 0.2 | 0.2 |
| `Kitchen Gas` | 0 until 7:00; 0.3 (7–10); 0.6, 1.0, 1.0, 0.6, 0.2 (10–15); then 0 | 0 |
| `Dining Occupancy` | 0 until 7:00; 0.1, 0.2, 0.1, 0.1 (7–11); 0.4, 1.0, 0.8, 0.3, 0.1 (11–16); then 0 | 0 |
| `Dining Hours` | 1.0 from 7:00 to 16:00, else 0 | 0 |
| `Theatre Sessions` | 0 until 7:00; 0.5; 1.0 (8–18); 0.5; then 0 | 0 |
| `Theatre Services` | 0.2 until 7:00; 0.6; 1.0 (8–18); 0.6; then 0.2 | 0.2 |
| `Theatre Ventilation` | 0.5 until 7:00; 1.0 (7–19); then 0.5 | 0.5 |
| `Care Bedroom Occupancy` (every day) | 1.0 until 7:00; 0.8, 0.5; 0.3 (9–12); 0.2; 0.4 (13–16); 0.3, 0.2, 0.4, 0.6, 0.8 (16–21); then 1.0 | as the weekday |
| `Care Bedroom Lighting` (every day) | 0.05 until 6:00; 0.3, 0.6, 0.4; 0.1 (9–16); 0.2, 0.4, 0.6, 0.8, 0.8, 0.6, 0.3, 0.1 (16–24) | as the weekday |
| `Care Bedroom Equipment` | constant 0.5 | constant 0.5 |
| `Care Communal Occupancy` (every day) | 0.05 until 7:00; 0.3, 0.9, 0.6, 0.7, 0.7, 1.0, 0.6, 0.7, 0.7, 0.7, 1.0, 0.8, 0.6, 0.4, 0.2 (7–22); then 0.05 | as the weekday |
| `Care Communal Hours` (every day) | 0.2 until 7:00; 1.0 (7–22); then 0.2 | as the weekday |
| `Community Occupancy` | 0 until 9:00; 0.2 (9–17); 0.6; 0.9 (18–21); 0.6, 0.2; then 0 | 0 until 9:00; 0.8 (9–20); 0.4; then 0 |
| `Community Hours` | 1.0 from 8:00 to 23:00, else 0 | 1.0 from 8:00 to 21:00, else 0 |
| `Always On` | constant 1.0 (the residential presets' schedule) | constant 1.0 |

The exact hourly values are in `ExampleNonResidentialPresets` and listed in [program-presets.md](../research/program-presets.md) §2.2.

**Default preset components (D-061, D-065).** One per type in panel *1 Program* (since S8.8 in panel *1 Program Presets*, with *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset*, D-108), each visible on the toolbar and built on `DefaultPresetComponent`, with these values as input defaults and the remark that they are illustrative: *Office Preset*, *Core Preset*, *Retail Preset*, *Mall Preset*, *Kitchen Preset*, *Dining Preset*, *Operating Theatre Preset*, *Clean Corridor Preset*, *Dirty Corridor Preset*, *Clinical Support Preset*, *Care Bedroom Preset*, *Care Communal Preset*, *Lobby Preset*, *Activity Hall Preset*, and *Service Preset*. The existing label and unit mapping of `DefaultPresetComponent` already covers every load above (*Gas Equipment* in W/m², *Ventilation* and *Infiltration* in 1/h); no component is special-cased.

### Department zoning per family (D-097)

At the most detailed level each family below places these zones. "One zone" means one polygon that may surround other zones (a ring) but is never split into rooms or tenancies. Housing families keep one zone per dwelling and storey (D-009, D-085), and their stairs and corridors are their own zones.

| Family | Zones and their space types | Not zoned separately |
| --- | --- | --- |
| `SYN-TYP-010` Radial lobes (housing) | the point-access core (`Stair`); each dwelling of each lobe (`DwellingUnit`), one zone per dwelling and storey | rooms of a dwelling |
| `SYN-TYP-011` Court cluster (housing) | each stair (`Stair`) and each dwelling (`DwellingUnit`) of every wing | rooms; the courts, which are outside the building |
| `SYN-TYP-012` Stepped bands (housing) | the stair (`Stair`), the shared circulation edge (`Corridor`), each dwelling (`DwellingUnit`), per storey | rooms; the terraces, which are outdoor roofs |
| `SYN-TYP-014` Branching mall | the public mall, hub and branches together (`Mall`); the shops on each side of each branch, one zone per side (`Retail`); each anchor store (`Retail`) | individual shops and tenancies |
| `SYN-TYP-015` Operating suite | each bank of operating theatres (`OperatingTheatre`); each clean corridor (`CleanCorridor`); each dirty corridor (`DirtyCorridor`); the support rooms together (`ClinicalSupport`) | individual theatres, scrub and anaesthetic rooms, stores, recovery, sluice |
| `SYN-TYP-016` Cafeteria | the kitchen and servery as one department (`Kitchen`); the dining field (`Dining`) | the servery counter, stores, wash-up, queue |
| `SYN-TYP-017` Office plate | the office work area, one ring around the core (`Office`); the service core (`Core`) | individual work areas, meeting rooms, lifts, stairs, toilets |
| `SYN-TYP-018` Care hub | the communal and service hub (`CareCommunal`); the bedrooms on each side of each wing corridor, one zone per side (`CareBedroom`); each wing corridor (`Corridor`) | individual bedrooms and en-suites, the care station |
| `SYN-TYP-019` Foyer and halls | the foyer (`Lobby`); each activity hall (`ActivityHall`); the support rooms together (`Service`) | individual changing rooms, stores, toilets |

`SYN-TYP-013` has no generator (D-096). The `001`–`009` families are unchanged (ADR-006).

### Any-program presets (S8.8, D-108)

- **Model.** `ProgramPreset.SpaceType` is `SpaceType?`; `IsAnyProgram` is `true` when it is `null`. A preset is always created with a space type (`ProgramPreset.Create`, `PresetValues.ToPreset`, every default preset component, *Program Preset*); `AsAnyProgram()` returns a copy without it that keeps everything else: the name, the same `ZoneProgram` (loads, their schedules, conditioning, setpoints), and the WWR. Casting an any-program preset again returns it unchanged.
- **Plan generators.** The slot check of every generator, single-plan and multi-storey (`PlanBuilder`), accepts an any-program preset on any slot; a preset with a space type must still have its slot's (`PresetSpaceTypeMismatch`, unchanged). A zone keeps the space type the generator's layout gives it (`PlannedZone.SpaceType`) and takes its program and the WWR of its windows from its slot's preset, as for a typed preset.
- **Provenance (GLOBAL.md scientific rule 3).** The plan's `Presets` parameter lists `{slot space type}:{preset name}` per slot, which for a typed preset is its own space type, as before. For each slot that received an any-program preset the plan also records `AnyProgramPreset.{Input}` = the preset's name (`PlanPresets.AnyProgramPresetKeyPrefix`), for example `AnyProgramPreset.Corridor=Example Office`; every floor and building made from the plan carries it in its provenance inputs. A plan of typed presets records no such key, so its output is unchanged.
- **Downstream.** Zones carry their space type and program, never their preset, so simplifiers, aggregators, validation, the mapping, *Inspect*, and *Convert2BEM* are unchanged: a dwelling zone with an office program is a `DwellingUnit` zone with that program, it is coloured and grouped by *Semantic Merge* as a dwelling, and *Convert2BEM* reports its space type `DwellingUnit`. Integration tests run a linear plan and a stepped band with any-program presets through every simplifier and aggregator, and every result validates.
- **Grasshopper.** The parameter *Any Program Preset* (AnyP, `AnyProgramPresetParameter`, `24bc6a12-ad06-4c25-bc9d-4e8318b8744c`) in panel *1 Program* is a floating data node like Grasshopper's *Geometry* parameter: wire any preset into it (a default preset component, *Program Preset*, or a *Program Preset* parameter), and it outputs the any-program cast (`AnyProgramPresetGoo`, shown as `Preset <name> (any program, no space type, WWR <ratio>)`). It holds no data of its own. Every preset input of every generator, a *Program Preset* parameter, takes it; the input's description says so.

## Consequences

- The enum grows by twelve values at its end; existing values, snapshots, and diagnostics are unchanged. *Semantic Merge* groups by space type as before, so a non-residential floor merges departments of the same type that touch; *Perimeter Core* and the single-zone methods give `Mixed` zones as before.
- Fifteen illustrative presets and fifteen default preset components; `ExampleResidentialPresets` is unchanged. Tests check that every preset builds, its space type, conditioning, setpoints, WWR, and the design value and annual fraction of every load.
- Non-residential zones are departments, so the detailed model has fewer and larger zones than a room-level model would; comparisons with room-level reference models must state this.
- The presets are not representative of any building or standard; results computed with them are development results only (D-023).
- Changing a value changes the snapshots of the families that use it and is recorded in this ADR and in [program-presets.md](../research/program-presets.md).
- An any-program preset lets a zone's program differ from its space type (D-108). This is always the user's explicit choice and always in the plan's provenance; a typed preset still cannot be given to another type's input.
