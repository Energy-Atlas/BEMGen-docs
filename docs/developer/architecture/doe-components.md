# DOE generator components and the program map

> **Status:** Accepted (stages P1 to P7 and the close-out of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md); the owner, with PR #1, D-176) · **Code:** `src/Lod.Grasshopper/Components/DoeComponentSupport.cs`, `DoeProgramMapComponent.cs`, `Doe<Family>Components.cs`, `src/Lod.Grasshopper/Goo/DoeGoo.cs`, `src/Lod.Grasshopper/Parameters/DoeParameters.cs`; `DoeProgramMap.Create` in `src/Lod.Generators/Doe/DoeProgramMap.cs`; `DoeProgramPresetsComponents.cs` and `src/Lod.Generators/Doe/DoeProgramPresets.cs` (P7) · **Smoke specs:** `scripts/rhino-smoke/specs/doe-offices.py` and one spec per family ([below](#all-doe-generator-components))

Stage P1 builds the Grasshopper support that every DOE generator component uses (P1 to P6): how a definition gives a DOE generator its
presets, one per program key (S4), and the outputs every DOE generator has. The DOE generators are a set of their own in panel *2 Generate*
(S9), apart from the precedent generators.

## The program map

A DOE zone takes the preset of its program key, its standards space type, such as `MediumOffice - OpenOffice` ([doe-layouts.md](doe-layouts.md),
S4). A DOE generator therefore has one presets input, *Program Map*, instead of one input per space type.

*DOE Program Map* (DoeMap, panel *1 Program*) makes the map from two lists:

| Input | Access | Meaning |
| --- | --- | --- |
| *Keys* (K) | list of text | the program keys, each once, whole standards space types matched exactly |
| *Presets* (P) | list of program presets | one preset per key in the same order, or one preset for every key; any-program presets too |

Its output *Program Map* (Map) is a `DoeProgramMap` in the hidden parameter *Program Map* (`ProgramMapParameter`, `ProgramMapGoo`). The rules
are `DoeProgramMap.Create` in `Lod.Generators`, so the component only reads and reports: a different number of presets than keys (other than
one), no key, an empty key or one with white space at its start or end (never trimmed: a key is matched exactly), and a repeated key are
`InvalidParameter`, all reported at once; an empty item in *Presets* (an upstream preset that failed) is an error naming its position. The space type of a typed preset is checked by the generator, as for every generator: it must be the
space type the fixed table gives the key (`DoeSpaceTypes`), and an any-program preset fits every key (D-108). A key of the plans without a preset
is `MissingPreset` per zone, named by the key; a key of the map that no zone has is unused.

**Why lists, and not presets that carry their key.** A program preset has no key field today, and the key belongs to the source zone, not to the
program: one preset may serve several keys, and the atlas input A3 (a program key in each program record) is not there yet. When A3 lands, a
preset from *Program JSON* may carry its key and the map may be made from presets alone; the lists stay valid.

**Building a map in a definition.** Place the DOE generator without a map: it lists the keys it needs in *Program Keys* and ends with an error
naming their number. Wire *Program Keys* into *DOE Program Map*'s *Keys* (through a second copy of the generator, since a definition cannot
feed a component its own output), and the presets in the same order, or one any-program preset for all of them, into *Presets*.

## The DOE generator component base

`DoeGeneratorComponent` is the base of every DOE generator component. It has the secondary exposure (the DOE group in *2 Generate*), the icon
of its class (D-063), and its description ends with the note that lengths are in metres and that each zone takes the preset of its key.

Every DOE family registers its inputs in this one order, with the defaults of its `Default` record (ADR-006, ADR-015, as *Stepped Band* does):

| Position | Inputs | |
| --- | --- | --- |
| 1 | the counts, integers: storeys first, then repeated units (store, guest-room bay, classroom wing counts) | the subclass's |
| 2 | the sizes (plate, ring, bays, depths), in the order of the family's parameter record | the subclass's |
| 3 | *Floor Height*, then *Orientation* | the subclass's |
| 4 | *Program Map* (Map, optional item) | `AddProgramMap` |
| 5 | *Preview Location* (D-062), last | `ComponentSupport.PreviewLocationParameter` |

| Output | Access | Meaning |
| --- | --- | --- |
| *Plan* (Plan) | list | the plan of every storey, bottom-up; one item for a family of one storey |
| *Multipliers* (N) | list of integers | how many storeys each plan stands for (ADR-015's `StoreyMultiplier`): the floor entries' multipliers |
| *Program Keys* (Keys) | list of text | every program key of the plans, in ordinal order; given before the map is read, so even without one |

A subclass marks its count and size inputs with `MarkReadInSolve` (optional, so Grasshopper still solves the component when one is wired to a
source without data; each keeps its record's default when unconnected). Its `SolveInstance` first calls `SetProgramKeys(DA, keys)`, so the keys
show even when an input does not read, then reads its inputs through `Read`, which names an input without a value in an error,
calls `TryProgramMap(DA, index, keyCount, out map)`, which fails with the error above when the map is missing, then calls its generator and
`Output(DA, result, multipliers)` for a multi-storey generator or `Output(DA, result)` for a generator of one plan (multiplier 1). The base never holds domain logic: the keys, the multipliers, and the plans come
from the generator.

**Wiring.** *Plan* → a plan simplifier (once per storey) → a floor aggregator's *Floors*; *Multipliers* → the same aggregator's *Multipliers*.
*Stack Floors* then builds every storey, and *Stacked Floor Zone Multiplier* models a plan of several storeys once with a zone multiplier
(D-045). Leaving *Multipliers* unconnected gives every plan one storey, which is another building than the generator's for a plan that stands for
several (the large office of P1).

**Every family.** P2, P3, P4, P5b, and P6 added `Doe<Family>Components.cs` with one sealed component per record or per family, derived from
`DoeGeneratorComponent`, using `MarkReadInSolve`, `Read`, `SetProgramKeys`, `AddProgramMap`, `TryProgramMap`, and `Output` unchanged. A family whose records have different defaults takes the
record as an abstract property of the sealed class, not a field set in the constructor: Grasshopper registers the inputs from the base
constructor, before a field of the subclass is set (`RingOfficeComponent`).

## The DOE office components (P1)

One component per record, so each input shows its record's default ([doe-ring-office.md](doe-ring-office.md)):

| Component (nickname) | Inputs, with defaults | GUID |
| --- | --- | --- |
| *DOE Small Office* (DoeSOff) | Storeys (1), Plate Length (27.690763), Plate Depth (18.45945), Perimeter Depth (4.572), Corridor Width (1.2192), Floor Height (3.05), Orientation (0), Program Map, Preview Location | `c8f1e87b-b238-4b4f-a6de-c510d1e5d02b` |
| *DOE Medium Office* (DoeMOff) | Storeys (3), Plate Length (49.911), Plate Depth (33.274), Perimeter Depth (5.341938), Corridor Width (1.2192), Floor Height (3.9624), Orientation (0), Program Map, Preview Location | `e7998061-adad-41d7-a08f-aeb372863442` |
| *DOE Large Office* (DoeLOff) | Storeys (12), Plate Length (73.10755), Plate Depth (48.737837), Perimeter Depth (12.161838), Corridor Width (1.523999), Floor Height (3.9632), Orientation (0), Program Map, Preview Location | `8bb8e1b0-83e8-4cdf-b36b-3364315e6006` |
| *DOE Program Map* (DoeMap) | Keys, Presets → Program Map | `0e471c68-8cb1-4375-b82a-71b36d797b94` |

## The DOE multiplied-room components (P5b)

One component per family, each with one record ([doe-tower-hotel.md](doe-tower-hotel.md), [doe-hospital.md](doe-hospital.md)):

| Component (nickname) | Inputs, with defaults | GUID |
| --- | --- | --- |
| *DOE Large Hotel* (DoeLHtl) | Storeys (6), Guest Rooms Per Row (19), Length (86.563), Depth (22.86), Floor Height (3.048), Orientation (0), Program Map, Preview Location | `8b61c4c7-2d19-4a1a-b83d-cea9254b634a` |
| *DOE Hospital* (DoeHosp) | Room Multipliers (list of 17, in `HospitalGenerator.MultipliedRooms` order), Plate Length (70.104), Plate Depth (53.34), Corridor Width (4.572), Floor Height (4.2683), Orientation (0), Program Map, Preview Location | `da2d1dab-1994-420f-87d6-8cae8ea567a4` |

The large hotel outputs three plans with *Multipliers* 1, *Storeys* − 2, 1; the hospital five plans of multiplier 1. Their repeated rooms keep
their zone multipliers through *No Simplification*, *Semantic Merge*, *Conditioned Merge*, *Stack Floors*, and *Stacked Floor Zone Multiplier*;
*Perimeter Core*, *Single Zone per Floor*, and the single-zone aggregators end with `NotSupported` (S8, ADR-026), and *Convert2BEM* lists the walls
toward the copy space as `SelfAdjacent`.

The parameter *Program Map* (`ProgramMapParameter`) has the GUID `ec21d323-a3c1-41d7-aed8-b1e13dab50df`. Each office outputs *Plan*,
*Multipliers*, and *Program Keys* as above: the small office one plan (multiplier *Storeys*), the medium and large offices three (1, *Storeys* − 2,
1). The storeys are previewed at their base elevations (`StoreyElevation`), so the large office's top plan is drawn at 43.5952 m.

## All DOE generator components

Fifteen generator components, one per layout record, in the DOE group of panel *2 Generate*, and *DOE Program Map* with its parameter in panel
*1 Program*. Each family document gives its components' inputs, defaults, and limits; the headless spec of each family is in
`scripts/rhino-smoke/specs/`.

| Component (nickname) | Class | Generator | Family document | Spec | GUID |
| --- | --- | --- | --- | --- | --- |
| *DOE Small Office* (DoeSOff) | `SmallOfficeComponent` | `RingOfficeGenerator` | [doe-ring-office.md](doe-ring-office.md) | `doe-offices` | `c8f1e87b-b238-4b4f-a6de-c510d1e5d02b` |
| *DOE Medium Office* (DoeMOff) | `MediumOfficeComponent` | `RingOfficeGenerator` | [doe-ring-office.md](doe-ring-office.md) | `doe-offices` | `e7998061-adad-41d7-a08f-aeb372863442` |
| *DOE Large Office* (DoeLOff) | `LargeOfficeComponent` | `RingOfficeGenerator` | [doe-ring-office.md](doe-ring-office.md) | `doe-offices` | `8bb8e1b0-83e8-4cdf-b36b-3364315e6006` |
| *DOE Full-Service Restaurant* (DoeFSR) | `FullServiceRestaurantComponent` | `RestaurantGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `b4ca8365-a4dc-4af7-a6b5-0fc68cdb37a9` |
| *DOE Quick-Service Restaurant* (DoeQSR) | `QuickServiceRestaurantComponent` | `RestaurantGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `cf72627b-3035-4f91-858c-f51772989c07` |
| *DOE Strip Mall* (DoeSMall) | `StripMallComponent` | `StoreRowGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `94be46f9-90c9-49ec-8104-8d572004856e` |
| *DOE Stand-alone Retail* (DoeRet) | `StandAloneRetailComponent` | `RetailBoxGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `1bf76d74-0917-4acc-8d9c-e0eaa36adcbe` |
| *DOE Supermarket* (DoeSMkt) | `SupermarketComponent` | `SupermarketGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `2f12351b-adfd-40aa-a763-be4394bd814b` |
| *DOE Warehouse* (DoeWare) | `WarehouseComponent` | `WarehouseGenerator` | [doe-single-storey.md](doe-single-storey.md) | `doe-single-storey` | `814d27a4-8483-4aba-bf78-2bf4daa62f46` |
| *DOE Primary School* (DoePSch) | `PrimarySchoolComponent` | `SchoolGenerator` | [doe-school.md](doe-school.md) | `doe-schools` | `4f67ab4c-7c7e-4a27-afbe-8e76cd48097d` |
| *DOE Secondary School* (DoeSSch) | `SecondarySchoolComponent` | `SchoolGenerator` | [doe-school.md](doe-school.md) | `doe-schools` | `913bc6e4-ba40-4f81-949d-fc7d616ee1db` |
| *DOE Small Hotel* (DoeSHot) | `SmallHotelComponent` | `CorridorHotelGenerator` | [doe-corridor-hotel.md](doe-corridor-hotel.md) | `doe-hotel` | `7b31e279-617d-4a06-a7c9-e8824b7ae396` |
| *DOE Large Hotel* (DoeLHtl) | `LargeHotelComponent` | `TowerHotelGenerator` | [doe-tower-hotel.md](doe-tower-hotel.md) | `doe-multiplied-rooms` | `8b61c4c7-2d19-4a1a-b83d-cea9254b634a` |
| *DOE Hospital* (DoeHosp) | `HospitalComponent` | `HospitalGenerator` | [doe-hospital.md](doe-hospital.md) | `doe-multiplied-rooms` | `da2d1dab-1994-420f-87d6-8cae8ea567a4` |
| *DOE Outpatient* (DoeOutP) | `OutpatientComponent` | `OutpatientGenerator` | [doe-outpatient.md](doe-outpatient.md) | `doe-outpatient` | `5d0c7a3e-9b41-4f6e-a8d2-3c1e7b590f64` |
| *DOE Program Map* (DoeMap) | `DoeProgramMapComponent` | `DoeProgramMap.Create` | this document | `doe-offices` | `0e471c68-8cb1-4375-b82a-71b36d797b94` |

The records and the generators that build them are listed in [doe-layouts.md](doe-layouts.md#the-generator-families).

## DOE program presets

Stage P7 ([design note §9](../plans/2026-10-25-doe-geometry-generators.md#9-stage-p7-doe-program-map-presets-owner-request-2026-10-26), the
owner's request and values) gives every DOE generator a ready program map, so that each runs and can be tested without a map assembled by hand.
`DoeProgramPresets.For(DoeBuildingType)` in `Lod.Generators/Doe/` builds the map of a record's generator, once per record and shared:

- **Keys.** One preset per program key of the generator (`DoeProgramPresets.ProgramKeys`, the generator's own `ProgramKeys`), in ordinal order.
- **Loads and setpoints.** The illustrative example preset of the key's BEMGen space type (`DoeSpaceTypes.Of(key)`): a non-residential example
  (`ExampleNonResidentialPresets`), or for `Corridor` and `Stair` the residential examples (the stair unconditioned). Its program is taken
  unchanged; the values are illustrative, not DOE or standard values, and are replaced when the atlas programs (A1, A2) land.
- **Name.** The key; descriptive only, never used for matching.
- **Glazing.** The source's own for the key, shipped in the layout record (`programGlazing`, [doe-layouts.md](doe-layouts.md#layout-records)):
  the WWR per orientation and the skylight ratio of the key's zones on the true-outdoor-wall basis, as the answer keys' per-key inputs; for the
  three offices the reference ratio of every orientation (`officeGlazing`), which the ring office generator applies at its glazing reference
  height (G1, S6). An orientation where the key has no counted wall and a key with no counted roof take 0; a key with neither (`interior`)
  has no glazing.
- **Keys under a gap (the controller's decision).** A key whose every zone is under a gap (G4: the warehouse's `Fine` and `Office`, the
  secondary school's `Auditorium`, `Gym`, and `Gym - audience`, the outpatient's `Stair`) keeps the source's own glazing of those zones
  (`gap_source_wall`): the source glazing over the true outdoor wall without the gap exclusion, and the skylight over the source roof, from
  the source only. The generator draws those zones differently, so their window area differs from the source's by what the gap changes,
  described per record in the family documents' terms: the warehouse office, lower than its storey in the source (4.267 m) under a floor of the
  fine storage, is drawn to the 8.534 m storey height, which about doubles its walls and windows (south 11.15 to 22.31 m², west 6.51 to
  13.01 m²), and the fine-storage floor above it is dropped; the secondary school's gym, auxiliary gym, and auditorium, 8 m high in the source,
  take the 4 m storey height, which about halves theirs; the outpatient's three stairs and lift, 9.144 m tall zones spanning three storeys, are
  drawn one zone per storey at 3.048 m. The T4 harness keeps excluding them. `DoeProgramPresets.GapKeys` lists them, and a remark and the
  shared source (`GapGlazing`) name them with that record's description. The loader checks that every zone of a `gap_source_wall` key is
  under a gap.
- **Fallback (the controller's decision).** A key whose space type has no example preset (`Mechanical`, `Other`, or any other uncovered type;
  no key maps to `Mixed` or `DwellingUnit`) takes the example *Service* preset as an any-program preset, named `<key> (Example Service)`. The
  zone keeps the space type of the generator's layout, and each plan records the use as `AnyProgramPreset.<key>` = that name, the any-program
  mechanism of every generator.
- **Provenance.** Every preset of a map carries one shared source (operation `DoeProgramPresets`): `Record`, `Reference` (the reference IDF and
  its SHA-256), `Loads`, `Glazing`, `ServiceFallback` (the keys that took the fallback, or `none`), and `GapGlazing` (the keys under a gap
  with the gap's convention, or `none`); a plan records it among its inputs. `DoeProgramPresets.Create` builds a map without the shared
  instance (internal, for the determinism test).

Fifteen output-only components, one per record and so one per DOE generator component, in their own group (secondary exposure) of panel
*1 Program Presets* beside the built-in presets, each a thin adaptor over `DoeProgramPresets` (`DoeProgramPresetsComponents.cs`). Each shows a
remark that the loads and setpoints are illustrative example values and the glazing is the DOE reference's for each key's zones (differing from
the source's where a gap changes the zones), a second remark naming the keys that took the fallback, and a third naming the keys under a gap.
Outputs:

| Output | Access | Meaning |
| --- | --- | --- |
| *Program Map* (Map) | item | the map; wire it into the generator's *Program Map* |
| *Keys* (K) | list of text | the program keys, in ordinal order |
| *Presets* (P) | list of program presets | the preset of each key, in the order of *Keys*; to change one, wire *Keys* and the edited *Presets* into *DOE Program Map* |

| Component (nickname) | Class | For | Keys | Keys with the Service fallback | Keys under a gap (the source's own glazing) | GUID |
| --- | --- | --- | --- | --- | --- | --- |
| *DOE Small Office Programs* (DoeSOffP) | `SmallOfficeProgramsComponent` | *DOE Small Office* | 9 | 2: `SmallOffice - Conference`, `SmallOffice - Elec/MechRoom` | none | `cc7deb8a-becc-451c-8733-c47fb5132ccc` |
| *DOE Medium Office Programs* (DoeMOffP) | `MediumOfficeProgramsComponent` | *DOE Medium Office* | 11 | 3: `MediumOffice - Classroom`, `MediumOffice - Conference`, `MediumOffice - Elec/MechRoom` | none | `37d576b9-c1eb-496a-8fda-5f80ffb9dd41` |
| *DOE Large Office Programs* (DoeLOffP) | `LargeOfficeProgramsComponent` | *DOE Large Office* | 13 | 5: `BreakRoom`, `Classroom`, `Conference`, `Elec/MechRoom`, `OfficeLarge Data Center` | none | `5c1b1c67-a1c3-48e2-a8f9-3a235949b7d3` |
| *DOE Full-Service Restaurant Programs* (DoeFSRP) | `FullServiceRestaurantProgramsComponent` | *DOE Full-Service Restaurant* | 2 | 0 | none | `0efa0bdc-0cfb-4dbb-b735-7a9453fec942` |
| *DOE Quick-Service Restaurant Programs* (DoeQSRP) | `QuickServiceRestaurantProgramsComponent` | *DOE Quick-Service Restaurant* | 2 | 0 | none | `93d7a80c-5cca-4e59-9a0f-0246caf79f9f` |
| *DOE Strip Mall Programs* (DoeSMallP) | `StripMallProgramsComponent` | *DOE Strip Mall* | 3 | 0 | none | `d488e69d-540b-419c-b8f0-fa0244661e09` |
| *DOE Stand-alone Retail Programs* (DoeRetP) | `StandAloneRetailProgramsComponent` | *DOE Stand-alone Retail* | 4 | 1: `Back_Space` | none | `538a2a8a-2a3b-414e-a1bc-c1d3c5109a18` |
| *DOE Supermarket Programs* (DoeSMktP) | `SupermarketProgramsComponent` | *DOE Supermarket* | 6 | 5: `Bakery`, `Deli`, `DryStorage`, `Produce`, `Sales` | none | `c4ced2e2-e69c-47ac-8a7a-d7fa01453b51` |
| *DOE Warehouse Programs* (DoeWareP) | `WarehouseProgramsComponent` | *DOE Warehouse* | 3 | 2: `Bulk`, `Fine` | `Fine`, `Office` | `fae396e6-ec9e-46e2-b9bd-660bd6579d23` |
| *DOE Primary School Programs* (DoePSchP) | `PrimarySchoolProgramsComponent` | *DOE Primary School* | 9 | 2: `Classroom`, `Mechanical` | none | `5f8262ad-b46c-466f-abcb-d3493099c93a` |
| *DOE Secondary School Programs* (DoeSSchP) | `SecondarySchoolProgramsComponent` | *DOE Secondary School* | 12 | 3: `Classroom`, `Library`, `Mechanical` | `Auditorium`, `Gym`, `Gym - audience` | `cdacf7bc-11c9-4d8a-8213-ac9b6edceb0d` |
| *DOE Small Hotel Programs* (DoeSHotP) | `SmallHotelProgramsComponent` | *DOE Small Hotel* | 14 | 9: `Elec/MechRoom`, `ElevatorCore`, `Exercise`, `GuestLounge`, `GuestRoom`, `Laundry`, `Mechanical`, `Meeting`, `StaffLounge` | none | `6606b09c-74fd-4f5e-8419-29bdd3ff484e` |
| *DOE Large Hotel Programs* (DoeLHtlP) | `LargeHotelProgramsComponent` | *DOE Large Hotel* | 15 | 7: `Banquet`, `GuestRoom`, `GuestRoom2`, `GuestRoom3`, `GuestRoom4`, `Laundry`, `Mechanical` | none | `68514a63-fb87-479a-99da-31daaa34f3c8` |
| *DOE Hospital Programs* (DoeHospP) | `HospitalProgramsComponent` | *DOE Hospital* | 18 | 12: `ER_Exam`, `ER_NurseStn`, `ER_Trauma`, `ER_Triage`, `ICU_NurseStn`, `ICU_Open`, `ICU_PatRm`, `Lab`, `NurseStn`, `PatRoom`, `PhysTherapy`, `Radiology` | none | `8d1911ba-c454-4c22-a36f-139bfb46a1e5` |
| *DOE Outpatient Programs* (DoeOutPP) | `OutpatientProgramsComponent` | *DOE Outpatient* | 32 | 22: `Anesthesia`, `BioHazard`, `CleanWork`, `Conference`, `DressingRoom`, `Elec/MechRoom`, `ElevatorPumpRoom`, `Exam`, `IT_Room`, `Lounge`, `MRI`, `MRI_Control`, `MedGas`, `NurseStation`, `PACU`, `PhysicalTherapy`, `PreOp`, `ProcedureRoom`, `Reception`, `Soil Work`, `Undeveloped`, `Xray` | `Stair` | `97748b7e-1c74-4c39-8baa-0245333d1480` |

Tests: `tests/Lod.Generators.Tests/Doe/Presets/DoeProgramPresetsTests.cs` checks for every record that the map's keys are the generator's, each
preset's space type and program (or the fallback), its glazing against the record and the answer key, that the generator at its defaults
validates with the map and records the fallback, that every supported simplifier and aggregator validates, and determinism; every family's T4
acceptance test runs a second time through the shipped map. The headless spec is `scripts/rhino-smoke/specs/doe-presets.py`.

## Icons

Every component above and the parameter *Program Map* has a 24 × 24 icon, drawn by `scripts/make_icons.py` (D-063) in the accent of its panel: orange
for *DOE Program Map*, its parameter, and the fifteen program-preset components, green for the generators. Each generator's motif is drawn from its reference building, and none repeats the
motif of a precedent generator (*Office Plate*, *Cafeteria*, *Branching Mall*, *Operating Suite*, *Care Hub*, *Foyer Halls*):

| Icon | Motif |
| --- | --- |
| *DOE Program Map* | a short key list, each key with an arrow to its coloured preset swatch |
| *Program Map* (parameter) | a key tag joined to a preset swatch, in the parameter hexagon |
| *DOE Small Office* | a square plan: a thin perimeter ring, a dark corridor ring around the core, one storey |
| *DOE Medium Office* | the same square ring plan on three plates offset diagonally |
| *DOE Large Office* | the ring plan on a tall stack of five plates offset diagonally, the middle one white, a cross beside the stack (its ×10) |
| *DOE Full-Service Restaurant* | a square split by one line, a large lower part and a smaller upper part with a plate |
| *DOE Quick-Service Restaurant* | a smaller square split in half, a cup in the upper half |
| *DOE Strip Mall* | a long bar of one wide cell, four narrow, one wide, four narrow |
| *DOE Stand-alone Retail* | a box with a dark back strip on top, a thin front strip, and a small centred notch (the entry) |
| *DOE Supermarket* | a large field with an L-shaped band along the top and the right and a dark square where they meet |
| *DOE Warehouse* | a tall box with a deeper lower band and a small dark office cell at its bottom-left corner |
| *DOE Primary School* | three parallel wings, each split by a corridor line, joined at their east ends by one tall spine block |
| *DOE Secondary School* | the same with the outline of a second, smaller storey over the spine |
| *DOE Small Hotel* | a long bar split by a thin dark corridor, equal room cells above and below, a three-storey stack at one end |
| *DOE Large Hotel* | a tall slab tower on a wider low podium, one guest-room bay solid and its copies dashed beside it |
| *DOE Hospital* | a square plate crossed by two dark corridors, one room solid and its copies dashed along a wing |
| *DOE Outpatient* | a three-storey block, the ground storey longer to the north, a dark stair shaft through all three, a cross on the upper storey |
| *DOE … Programs* (each of the 15) | its generator's motif at two-thirds size in the top right, in the orange accent, and a preset tag with its hole in the bottom left over the motif's corner (`programs` in the script) |
