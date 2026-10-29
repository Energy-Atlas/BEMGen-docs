# DOE layout records and the grid plan layout

> **Status:** Provisional (stages P0a and P5a of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md), pending the owner's reading) · **Code:** `src/Lod.Generators/Doe/`, `scripts/doe-geometry/`, the harness in `tests/Lod.Generators.Tests/Doe/Harness/` · **Data:** `src/Lod.Generators/Doe/Layouts/*.json`, `tests/fixtures/doe/*.answer.json`

Stage P0a lays the foundation the DOE generator families (P1 to P6) build on: the layout of every non-apartment DOE type as data, a shared
layout block that turns a storey of that data into a plan, the S3 size rule, program keys with the program map, and a harness that compares a
generated model with the source figures. It adds no generator and no Grasshopper component; those came with the family stages ([below](#the-generator-families)).

## Layout records

One record per type, fifteen in all: `small-office`, `medium-office`, `large-office`, `full-service-restaurant`, `quick-service-restaurant`,
`strip-mall`, `stand-alone-retail`, `supermarket`, `warehouse`, `primary-school`, `secondary-school`, `small-hotel`, `large-hotel`, `hospital`,
`outpatient` (the note's "14" counted one fewer; its §4 table lists these fifteen). `scripts/doe-geometry/extract.py` writes them from the DOE
reference buildings and openstudio-standards (its README (`scripts/doe-geometry/README.md`)); they are embedded in `Lod.Generators` and loaded
with `DoeLayoutRecords.Load(DoeBuildingType)`, which checks the format and fails with an `InvalidDataException` naming the record and the reason.
`Lod.Generators` reads them with its own small JSON reader (`DoeJson`), since it depends on `Lod.Core` only.

| Field | Meaning |
| --- | --- |
| `type`, `sources` | the record's name; each source file with its role and SHA-256 (the reference IDF, the openstudio-standards OSM, and the prototype inputs that name it) |
| `gaps`, `gapConventions` | the gaps G1–G5 that apply (S7), found from the data |
| `sourceCeilingHeight` | the zone height under a plenum where G1 applies (S6: 2.7432 m in the medium office, 2.744 m in the large office) |
| `planOrigin` | the source coordinates of the plan origin, the building's south-west corner over all storeys |
| `storeys` | bottom-up: `elevation` (the source's), `floorHeight` (zone and plenum, G1), `multiplier` (the large office's x10 floor, the large hotel's x4 floor), `xCuts`, `yCuts`, `zones` |
| zone | `id`, `name` (the source zone's), `programKey` (standards space type), `standardsBuildingType`, `programKeyLink` (the rule that linked the key: `office_room`, `spc_typ`, `osm_space`, `osm_tiling`), `programKeySpaces` (the OSM spaces the rule used), `programKeySource` (the file it read, with its SHA-256), `multiplier` within the storey (hospital and large-hotel rooms; carried onto the planned zone since P5a, S8), `cells` (rectangles `[x0, y0, x1, y1)` of cell indices), and for a zone under G4 `gap` and, when it is repeated on a storey it spans, `sourceStorey` |
| `programGlazingRule`, `programGlazing` | since format version 2 (stage P7): every program key of the record once, in ordinal order, with the source's WWR per orientation (`N`, `E`, `S`, `W`) and skylight ratio and their `basis`: `true_outdoor_wall` (the answer key's per-key inputs, [below](#answer-keys-and-the-comparison-harness)), `office_reference` (the office reference ratio of every orientation, `officeGlazing`), `gap_source_wall` (every zone of the key under a gap: the same true-outdoor-wall rule with the gap zones and orientations counted, and the skylight over the source roof, from the source only), or `interior` (no counted outdoor wall or roof, no ratio); `null` where the key has no counted wall of that orientation or no counted roof. The loader checks the keys against the zones, each ratio in [0, 1), and the basis against the ratios (an `interior` key has none, every other key one at least); [`DoeProgramPresets`](doe-components.md#doe-program-presets) reads it |
| `notices` | the DOE credit (a US government work, public domain, attribution requested) and the openstudio-standards BSD-3 licence |

The offices take their rooms from the openstudio-standards detailed offices on the reference plates and elevations (O6, O8): the large office's
storeys stand at 0, 19.816 (x10), and 43.5952 m, not at the OSM's 16.77 and 33.54 m, and keep their data-centre zones. Every other type takes its
zones from the reference IDF. Zones per storey (source zones; the outpatient's upper storeys add four G4 copies): small office 17; medium office
23/21/21; large office 26/26/26; restaurants 2; strip mall 10; stand-alone retail 5; supermarket 6; warehouse 3; primary school 25; secondary
school 25/21; small hotel 19/16/16/16; large hotel 7/7/7; hospital 9/11/13/13/8; outpatient 59/37/22, the note's figures. The outpatient
record therefore has 59/41/26 zones per storey: the note's 59/37/22 plus, on each upper storey, the copies of the three stairs (north-east, north-west, south-west) and the lift that span all three storeys (G4).

The record tests check the elevations, floor heights, and multipliers against figures from the same extraction and the note; from P1 on, each
generator stage checks them against its own parameters as well (T1 through the harness).

## The generator families

Eleven generators build the fifteen records (design note §4). Each family document states its parameters, limits, gaps, source facts, and
acceptance results, and [doe-components.md](doe-components.md) the Grasshopper components, their icons, and the program map.

| Generator | Records | Family document |
| --- | --- | --- |
| `RingOfficeGenerator` | `small-office`, `medium-office`, `large-office` | [doe-ring-office.md](doe-ring-office.md) |
| `RestaurantGenerator` | `full-service-restaurant`, `quick-service-restaurant` | [doe-single-storey.md](doe-single-storey.md) |
| `StoreRowGenerator` | `strip-mall` | [doe-single-storey.md](doe-single-storey.md) |
| `RetailBoxGenerator` | `stand-alone-retail` | [doe-single-storey.md](doe-single-storey.md) |
| `SupermarketGenerator` | `supermarket` | [doe-single-storey.md](doe-single-storey.md) |
| `WarehouseGenerator` | `warehouse` | [doe-single-storey.md](doe-single-storey.md) |
| `SchoolGenerator` | `primary-school`, `secondary-school` | [doe-school.md](doe-school.md) |
| `CorridorHotelGenerator` | `small-hotel` | [doe-corridor-hotel.md](doe-corridor-hotel.md) |
| `TowerHotelGenerator` | `large-hotel` | [doe-tower-hotel.md](doe-tower-hotel.md) |
| `HospitalGenerator` | `hospital` | [doe-hospital.md](doe-hospital.md) |
| `OutpatientGenerator` | `outpatient` | [doe-outpatient.md](doe-outpatient.md) |

## The grid plan layout

`GridPlanLayout.Layout(xCuts, yCuts, zones)` (internal, S1) lays out a storey: every zone is a union of grid cells, cells in no zone lie outside
the footprint, and the footprint is the union of every zone's cells, so outlines that are not rectangles and footprints with holes (a court, the
gaps left by multiplied rooms) come out of the cells alone. Each polygon is traced exactly from its cells' edges on the cut coordinates, with
collinear vertices dropped; where two rings meet at a vertex the tracing turns most to the left, so cells touching only at a corner stay apart.
A boundary that still passes one vertex twice, such as a court that touches the outline at a corner, is split there into simple rings, so the
court is a hole of its own that shares that vertex with the outer ring (and the surface builder takes it as it takes any hole). It returns a
`PlanLayout` of `PlannedZone`s with their program keys, or errors: `DuplicateZoneId` (two zones with one ID), `InvalidParameter` (cuts that do not
increase, a zone without cells, cells outside the grid), `OverlappingZones` (a cell in two zones), `DisconnectedGroup` (a zone that is not one
polygon), and `NotSupported` (a footprint that is not one polygon). `DoeStoreyRecord.Layout()` lays out a record storey at its default size.

**Multiplied rooms (P5a, S8, ADR-026).** Each zone carries its record `multiplier` onto its `PlannedZone` (below 1 is `InvalidParameter`). On a
storey with a multiplied zone, every cell of the grid is in the footprint: the cells no zone holds are the copy space, where the undrawn copies of
the multiplied rooms stand (O5). The drawn zones may then be several polygons on one plate, as on the hospital's ground storey, whose
`ER_Trauma2_Flr_1` stands apart from the rest with the copies of the ×4 triage and exam rooms between them. The rule is the sources': on every
storey of the hospital and the large hotel, every wall of a zone toward an empty cell is a self-referencing `Surface` in the reference IDF (its
`selfAdjacentWallLength` in the answer key). The surface builder makes those walls, and every wall between zones of
different multipliers, `SelfAdjacent`. A storey without a multiplied zone keeps the rule above: cells in no zone lie outside the footprint, and a
footprint of several polygons is `NotSupported`.

## Size variation (S3)

`GridAxis` is one axis of a building's grid: the union of its storeys' cuts (`GridAxis.Union`), so a coordinate several storeys share moves alike
on all of them (`Map`), and one flag per interval, fixed or flexible (`WithFixed`). `Resize(length, parameter, tolerances)` keeps fixed intervals
and shares the change among the flexible ones in proportion to their slack, their default length less 1 m (`GridAxis.MinimumFlexibleInterval`),
when the axis shrinks and when it grows (S3 as amended in stage P1, decided above the controller; P0a shared it by default length). Every
flexible interval therefore reaches 1 m at the same length, the shortest valid one (`MinimumLength`: the fixed intervals plus 1 m per flexible
interval, or its own length under 1 m); an interval of 1 m or less has no slack and keeps its length, which replaces P0a's rule that such an interval may grow but not shrink.
A length within `ToleranceSettings.Distance` of the default is the default (the same axis), so the defaults stay exact. A length shorter than
`MinimumLength` (by more than the distance tolerance), any other length of an axis whose flexible intervals have no slack (a total slack within the
distance tolerance counts as none), and any other length of
an axis without flexible intervals are `InvalidParameter`. Which intervals are fixed (perimeter depth, corridor width, room bay) is each family's
choice; repeated units (store counts, room bays, wings) are left to the families as well. A fixed band that a family's size parameter sets (a
corridor width, a perimeter depth) must be at least `GridAxis.MinimumFixedBand`, 0.5 m (the controller's minor parameter limit under D-098, stage
P1); each family checks its own bands and reports a narrower one as `InvalidParameter`. The minimum applies per band a parameter sets, a side's
whole band (the large office's south perimeter of 5.486, 0.610, and 6.066 m intervals is one band), not to each grid interval within it; later
families apply it the same way.

## Program keys and the program map (S4)

A zone's `ProgramKey` is the standards space type from source data, never parsed from a zone name (D-061). For the offices it is each OSM
room's standards space type (`MediumOffice - OpenOffice`, link `office_room`). For every other type the extraction applies the controller's rules
in order, and each zone records the rule, the OSM spaces it used, and the file it read with its SHA-256:

1. `spc_typ`: the zone's name equals a standards space type of the OSM's standards building type in the pinned
   `doe_ref_1980_2004.spc_typ.json` (both restaurants, the supermarket's six zones, the warehouse's office, the stand-alone retail's back space);
2. `osm_space`: the geometry OSM that `doe_ref_1980_2004.prototype_inputs.json` names for the DOE Ref 1980-2004 template has a space of the zone's
   name, and the key is that space's standards space type; the floor areas are not part of the rule, and a difference above 0.1 m² would be
   recorded (`programKeyAreaMismatch`) and reported, of which there is none;
3. `osm_tiling`: OSM spaces of exactly one standards space type tile the zone, their union equal to its floor within the ADR-004 distance
   tolerance and their summed area to its area within the relative area tolerance (the warehouse's bulk and fine storage);
4. otherwise the extraction stops with exit code 2 and a message naming the type and the zone; no zone of any record is one.

The OSM only names the type; the geometry stays the reference's (O8). Every zone of the fifteen records has a key. Programs for these keys come
from the atlas (A1), which is not yet checked here.

`DoeSpaceTypes.Of(key)` is the fixed table from key to BEMGen `SpaceType`, by whole key, unmapped keys `Other`: offices (`OpenOffice`,
`ClosedOffice`, `Office`, the small and medium office variants) `Office`; corridors (`Corridor`, `Corridor2`, `Hall`, `Hall_infil`) `Corridor`;
`Stair`; `Lobby` and `Entry`; `Mechanical` and `Elec/MechRoom`; `Kitchen`; `Dining`, `Cafeteria`, `Cafe`; retail and the strip-mall stores
`Retail`; `OR` `OperatingTheatre`; restrooms, toilets, storage, janitor, and locker rooms `Service`; `Gym`, `Gym - audience`, `Auditorium`
`ActivityHall`. No key is a `DwellingUnit`. `DoeProgramMap` is the presets record of the DOE generators: one preset per key, a slot per key
of the table's space type (a typed preset must have it, an any-program preset fits every key), a zone's preset found by its key
(`PlanPresets.PresetFor`), a key without a preset `MissingPreset`.

## Answer keys and the comparison harness

Every type has an answer key, `tests/fixtures/doe/<type>.answer.json`, with every quantity of the note's §5 T1–T4 (and T7 for the offices) as
BEMGen builds it under the gap conventions, computed from the source polygons independently of the record's grid: storey count, elevations,
floor heights, multipliers, and outlines (T1); per storey the zones with their program keys, floor areas, and outdoor wall lengths per orientation,
and the walls each pair of zones shares (T2); the floor area in total and per program key, with the source value and the adjustments between
them (T3); the window and skylight areas with the source's WWR per orientation and skylight ratio per zone, the T4 program inputs (T4); the
reference's perimeter-core areas and depth (T7).

**Office T4 inputs** (the controller's decision, a test fixture until the atlas gives WWR per orientation, A2): each office room's WWR per
orientation is the reference's glazing of that orientation, windows and glass doors as the note's §5 figures count them, over the reference's
outdoor wall area of that orientation: in the medium and large offices the conditioned zones' walls, below the 2.74 m source ceiling height
(S6), in the small office, which has no plenum, the full 3.05 m walls. It applies to every room facing that orientation, on its walls at that
height, so the rooms' glazing adds up to the reference's: small office 16.73, 11.16, 20.64, and 11.16 m² (north, east, south, west; the south
includes the 3.91 m² glass door), medium office 195.85 and 130.57 m², large office 1,390.85 and 927.23 m². The answer key keeps the ratios,
the height, and the reference figures (`officeGlazing`), each room's wall area at that height (`glazingWallArea`), and the detailed office's own
windows (`roomsWindowArea`; the small office's has no door, 16.73 m² south).

The harness (`DoeComparison` in `Lod.Generators.Tests`) compares a generated plan or floor per storey with an answer key and reports every
quantity as a finding, with the tolerances of `ToleranceSettings.Acceptance` ([ADR-004](../decisions/ADR-004-tolerances.md)): 0.01 m for T1,
0.1 m² and 0.05 m for T2, 0.1 % for T3, 1 % for T4, and 0.1 m² for T7. A quantity of a zone the key marks with a gap (G4), and floor heights
under G5, are reported as excluded, not failed, and the T4 building totals leave the same zones out on both sides (the key's source glazing
of those zones and the generated glazing of them), so the secondary school's tall zones and the outpatient's stair and lift copies do not fail
the totals. Since P0b the harness measures skylights through a callback; `DoeGlazingAcceptanceTests` measures them on the roofs of `Stack` of the
storeys, so a covered ceiling counts none.

Every record, rendered through `GridPlanLayout` at its defaults with fixture programs, matches its answer key on T1, T2, and T3, the hospital's
ground storey and T3 total included since P5a. On a storey with multiplied rooms T1 compares
the drawn outline, the union of the zones, which the key records, not the footprint, which holds the copy space too. T2 splits the key's walls
on no other zone into the self-adjacent walls toward the copy space (`selfAdjacentWallLength`, compared with the walls the layout makes
self-adjacent and that no other zone's wall stands against) and the outdoor rest, and counts the walls two zones of different multipliers share
back to back as shared, as the key does. *Perimeter Core* at the reference's perimeter depth gives the reference's five zones per storey of the
three offices within 0.1 m² (T7).

**T4 (P0b, on the generators' path since P5a).** `DoeGlazingAcceptanceTests` lays out every record with one program per program key, the
`DoeProgramMap` the DOE generators take, each with its key's WWR per orientation and skylight ratio from the answer key (`programGlazing`, the
atlas input A2), the record's `sourceCeilingHeight` as the glazing reference height where G1 applies (S6), and compares with the key within 1 %:
window area in total per orientation and per program key and orientation, skylight area in total and per key, and window and skylight area per
zone where every zone of the key shares its ratio.

- **Per-key inputs** (`programGlazing`, P5a, decided by the session above the controller). For each program key and orientation, the source
  glazing over the wall it is a ratio of (the true outdoor wall; under G1 the wall below the source ceiling, `glazingWallArea`), each summed over
  the key's zones times their storey's and own multipliers, without the zones and orientations under a gap; the skylight ratio is the skylight
  area over the source roof area on the same rule. A key whose every zone is under a gap has none, and the harness gives it no glazing.
- **Zones whose ratio differs from their key's** (`glazingRatioDifferences`): every zone and orientation (`roof` for skylights) where the key's
  ratio times the zone's wall misses the zone's source glazing by more than T4's 1 % (`GLAZING_RELATIVE`, ADR-004
  `Acceptance.RelativeGlazingArea`, as `ToleranceSettings.RelativeEquals` reads it). Their per-zone quantities are reported, not failed (`reported:
  the zone's ratio differs from its program key's`), and a test checks that the list is exact: each listed quantity misses the source, every other
  passes. Per record: small hotel 43 (`GuestRoom206_208` S 0.1908 against its key's 0.1578, and its floors' repeats), outpatient 38, hospital 6,
  every other record 0. The key totals count every zone, so they still match.

- **Basis** (review rounds 2 and 3, A). A zone's WWR of an orientation is its source glazing over its *true outdoor wall*: its source walls
  marked Outdoors less every stretch that coincides with a wall of another zone on the same plane, back to back, whatever that wall's boundary,
  since a stretch with a zone on its other side is not outside (the façade-line test of D-041 within the ADR-004 distance and angle tolerances,
  `COINCIDE_DISTANCE` and `COINCIDE_ANGLE` of `extract.py`). A stretch counts over the height both walls share: its area is the plan overlap
  times the height overlap, its length that area over the zone wall's height. `extract.py` computes it from the source only
  (`trueOutdoorWallLength`, `trueOutdoorWallArea` per zone) and lists every stretch in the key (`coincidingOutdoorWalls`: storey, zone, partner,
  orientation, length, area, and the partner wall's boundary class `partnerBoundary`: `Outdoors`, `Surface paired`, `Surface self-referencing`,
  or `other`). Since P5a a stretch of a wall not marked Outdoors with no zone behind it is a true outdoor wall too, whatever its source boundary
  (geometry decides, as D-162), unless it faces the copy space of a multiplied room (`selfAdjacentWallLength`, the rule of `GridPlanLayout`, read
  `PROBE` = 0.01 m outside the stretch); the key lists each with its source boundary (`nonOutdoorExteriorWalls`). For the offices the reference
  basis is reduced the same way (`officeGlazing.referenceCoincidingWalls`). T2 checks the true
  outdoor wall per zone and orientation against what BEMGen draws (`true outdoor wall`), where the two meet; every record passes it.
  The partners are the counted zones only: plenums, attics, and basements are left out, consistent with G1; a probe found no stretch against
  them in the fifteen reference files and the three office OSMs.
- **Stretches found:** 18. Outdoors: 8, all in the secondary school (each bathroom and main corridor against the tall auditorium, 11 m and
  15 m, both ways). Surface paired: 2, the small office's `Corridor_1` against the lobby (south, 0.544 m) and the large office's `Lobby_Bot_ZN_2`
  against `Corridor_Bot_ZN_1` (west, 0.049 m). Surface self-referencing: 8, the outpatient's `Floor_2_Reception_Hall` against eight rooms
  (south, 26.518 m of its 28.651 m). Other: none. The eleven other records have none.
- **Source boundary artifacts.** The stretches against a non-Outdoors wall are walls the source exposes to outdoor air although a zone adjoins
  them, such as the outpatient reception hall's 26.5 m of south wall against the X-ray and exam rooms; BEMGen draws them between the zones.
  An energy comparison with the source must know that these walls differ. P5a (ADR-026) does not change them, and keeps the source's
  self-referencing walls between zones of equal multiplier (the outpatient's) as shared `Interzone` walls; `SelfAdjacent` is only for
  multiplied rooms.
- **Excluded, not failed:** zones under a gap and, per orientation, walls against a tall zone (G4) drawn on its own storey only
  (`gapOrientations`: five first-floor zones of the secondary school, against its tall auditorium and gyms); the warehouse's office (G4, under the
  fine-storage floor the storey height drops) and fine storage (its dropped floor); nothing else since P5a. The orientations with self-adjacent
  source walls toward multiplied rooms (`selfAdjacentWallLength`), pending S8 and P5a until then, are compared: in T4 the large hotel's 8 and the
  hospital's 58 quantities (46 before, without the ground storey) all agree, the large hotel's corridors included, whose walls toward the ×19 and
  ×9 rooms are self-adjacent and so take no glazing; in T2 their true outdoor walls agree too, and the hospital's ground storey and totals are
  compared and pass (`DoeGlazingAcceptanceTests`).
- **Walls on nothing that the source does not mark Outdoors (P5a).** Over the fifteen records there is one: the hospital's
  `OR_NurseSat_Flr_2_Wall_1_East`, 16.764 m of the plate's east façade (x = 70.104 m, y from 0 to 16.764 m), a self-referencing `Surface` in the
  reference IDF, so the source treats it as adiabatic, although no zone and no copy stands beyond it. Geometry decides: it is a true outdoor wall
  of `OR_NurseStn_Lobby_Flr_2` in the key, BEMGen draws it outdoors, and T2 agrees. An energy comparison with the source must name it.
- **Roofs and exposed floors per zone (P5a).** T2 compares, for the hospital and the large hotel, each zone's roof and exposed floor area on
  `Stack` of the storeys with the key's `sourceRoofArea` and `sourceExposedFloorArea` within 0.1 m²; a floor or ceiling on the copy space of the
  storey below or above is neither. Without the copy space the check fails for both records.
- **Result:** every record passes T4 on every compared quantity, the secondary school's bathrooms included, and the primary school's 13.38 m² of
  skylights per zone and in total. The secondary school's skylit zones are its G4 gyms, which the totals leave out.

## Source facts reported

- The large office's 46,320 m² of the note (§5 P1, "above grade") includes the basement: above grade it is 42,757.25 m² (12 plates of
  3,563.1 m²), and the basement (G3) adds 3,563.1 m².
- T7 runs at the reference's exact perimeter depth, the core's mean inset: 5.0 m (small office), 4.5733 m (medium), and 4.5732 m (large), which
  the note rounds to 4.57 m; at 4.57 m the cores differ from the reference's by 0.43 and 0.65 m², outside T7's 0.1 m².
- The small office has no plenum, so G1 does not apply to it (the note's §4 lists G1 for every office); its gaps are G2 only.
- The small office's detailed rooms have no glass door, so their own south glazing is 16.73 m², not the reference's 20.64 m²; the office T4
  inputs above take the reference's ratio, glass door included, so T4 reproduces 20.64 m² without a looser check.
- The outpatient has 59/41/26 zones per storey in its record: the note's 59/37/22 plus the G4 copies of its stairs and lift.
- The hospital's fifth storey has two zones that overlap by 2 mm in the source; the extraction puts their edges on one cut (an area change of
  0.018 m², recorded as an adjustment).
