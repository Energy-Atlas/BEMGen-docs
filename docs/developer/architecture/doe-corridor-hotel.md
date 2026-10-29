# DOE corridor hotel generator

> **Status:** Accepted (stage P4 of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md); the owner, with PR #1, D-176) · **Code:** `src/Lod.Generators/Doe/CorridorHotel/` · **Tests:** `tests/Lod.Generators.Tests/Doe/CorridorHotel/`, `tests/Lod.Integration.Tests/CorridorHotelTypologyTests.cs` · **Record:** `small-hotel` ([DOE layout records](doe-layouts.md))

`CorridorHotelGenerator` builds the DOE small hotel, four storeys of 19, 16, 16, and 16 zones, from its layout record, one plan per storey
through `MultiStoreyPlanGenerator` ([ADR-015](../decisions/ADR-015-plans-per-storey.md)) because the ground storey differs, and `GridPlanLayout`
([ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md), S1). At its defaults every storey is the record's storey through
`GridPlanLayout`, vertex for vertex. Geometry only: each zone's program comes from a `DoeProgramMap` by its program key (S4,
`CorridorHotelGenerator.ProgramKeys`, 14 keys). The Grasshopper component is *DOE Small Hotel* (below).

## Structure

The hotel is a double-loaded bar along plan x, 54.8646 × 18.2886 m: a south row of guest rooms 8.2302 m deep, a corridor 1.8288 m wide, and a
north row 8.2296 m deep, on every storey. Guest rooms sit on the source's 13 ft (3.9624 m) bay. The ground storey holds the front lounge,
offices, exercise room, meeting room, laundry, staff lounge, and five guest rooms; each upper storey holds 24 guest rooms in 10 zones (grouped
rooms such as `GuestRoom202_205` are one zone), the stairs and storage at both ends, the lift, and the corridor with its stub to the lift lobby.
Grouped source zones with several floor polygons are contiguous, so each is one polygon per storey.

`CorridorHotelTemplate` reads this structure from the record's cells and program keys, never from a zone name (D-061):

- the bar's x axis is the union of every storey's x cuts (14 intervals; S3, `GridAxis.Union`), with bay cuts that no storey uses added inside
  every interval of several bays (11.8872 and 15.8496 m), so that **each bay is one flexible interval** (16 intervals, 11 of them bays);
- an interval is a **guest-room bay interval** when the zone over it in the typical (top) storey's north row has the key `GuestRoom`; every other
  interval is a **service interval** (front stairs 2.4384 m, front storage 1.524 m, lift lobby 3.048 m, lift 1.8288 m, rear stairs 2.439 m;
  11.2782 m in all);
- the source's bay width is the narrowest bay interval of the union (3.9624 m); every bay interval of the union is a whole number of bays (11 in
  all: 224, 220–223, 219, 215–218, 214 on the typical storey);
- the **undivided run** is the union's bay interval of the most bays, the three bays from 7.9248 m to 19.812 m that no storey divides (under the
  front lounge and office on the ground storey, `GuestRoom202_205` and `GuestRoom220_223` above).

Every bay has the same default length, so the same slack (length less 1 m) under the amended S3 (D-164), so the same share of a length change: the
bays stay equally wide, and all reach 1 m together at the shortest valid length, which is S3's own limit (`GridAxis.MinimumLength`). With the run
as one interval of three bays its slack would be 10.887 m against 2.962 m for a single bay, and the bays would part: at 22 bays a single bay
would be 2.311 m wide instead of 1.981 m.

S3's wording lists the room bay among the fixed dimensions; this generator makes the bays flexible and the service intervals fixed, the only reading
that keeps both `Length` and `GuestRoomBays` as parameters (a deviation from S3's wording, accepted by the controller under D-098).

A record without this form (fewer than two storeys, storeys of different y cuts, upper storeys of different heights, a zone without a key or with a
multiplier, no north guest room, a bay interval that is not a whole number of bays) fails with an `InvalidDataException` naming the reason.
The record is analysed with the generator's tolerances (`CorridorHotelTemplate.Of`, once per tolerances); `Default`, `ProgramKeys`,
`MinimumGuestRoomBays`, and `SourceBayWidth` read it with the default tolerances.

## Parameters

`CorridorHotelParameters(StoreyCount, GuestRoomBays, Length, RoomDepth, CorridorWidth, FloorHeight, OrientationDegrees)`; `Default` reads the
values from the record and reproduces it.

| Parameter | Default | Rule |
| --- | --- | --- |
| `StoreyCount` | 4 | at least 2 (`MinimumStoreys`: the ground storey and one guest-room storey); the record's storeys bottom-up, then copies of its top storey |
| `GuestRoomBays` | 11 | at least 9 (`MinimumGuestRoomBays`: one bay left in the undivided run), at most the bays the length holds at 1 m each; the change of the count adds bays to the undivided run or removes them from it |
| `Length` | 54.8646 m | plan x of every storey (S3): the service intervals keep their length, the bays share the rest by their equal slack (`BayWidth`), each at least 1 m |
| `RoomDepth` | 8.2299 m | the mean of the two rows, which keep the source's ratio (8.2302 : 8.2296); each row a fixed band of at least 0.5 m (`GridAxis.MinimumFixedBand`) |
| `CorridorWidth` | 1.8288 m | the corridor along the bar; a fixed band of at least 0.5 m |
| `FloorHeight` | 2.7432 m | every storey (G5); positive; storey *k* stands at *k* × `FloorHeight` |

**Limits** (`CorridorHotelGenerator.SizeLimits`, the other parameters as given; every limit keeps every zone and adjacency, and just beyond it is
`InvalidParameter`):

| Parameter | Default | Valid range at the defaults | Rule | 0.5× and 2× |
| --- | --- | --- | --- | --- |
| `Length` | 54.8646 m | ≥ 22.2782 m (−59 %) | 11.2782 m of service intervals and 1 m per bay (`GuestRoomBays` + 11.2782) | both valid |
| `RoomDepth` | 8.2299 m | ≥ 0.500018 m (−94 %) | the north row, the narrower, at 0.5 m: 0.5 × 8.2299 / 8.2296 | both valid |
| `CorridorWidth` | 1.8288 m | ≥ 0.5 m (−73 %) | the corridor band at 0.5 m | both valid (0.9144 m and 3.6576 m) |
| `FloorHeight` | 2.7432 m | > 0 | positive (the base class) | both valid |
| `GuestRoomBays` | 11 | 9 to 43 | one bay in the undivided run; `Length` − 11.2782 m at 1 m per bay | 9 and 22 valid |
| `StoreyCount` | 4 | ≥ 2 | the ground storey and one guest-room storey | 2 and 8 valid |

No size parameter has an upper limit, and every one reaches ±20 % of its default.

**Bays.** Every bay is (`Length` − 11.2782 m) / `GuestRoomBays` wide. The count adds bay intervals to the undivided run or removes them from it,
at the source's bay width, before the axis is resized to `Length`, so every zone keeps its neighbours: at 22 bays `GuestRoom220_223` spans 15
bays and every other guest-room zone keeps its number of bays, at 9 it spans two. `GridAxis.Map` maps each storey's cuts onto the axis of the new
count through an index remap (a run cut the count removes has no place; no storey uses one). The count is at a fixed length: at 22 bays the bays
are 1.98 m wide. The zones keep their source IDs and names (`GuestRoom202_205` stands for whatever number of rooms its bays hold). A length
under 11.2782 m + 1 m per bay is `InvalidParameter` (S3), with a message naming `Length`, `GuestRoomBays`, and the shortest length they need.

**Rows and corridor.** They are fixed bands their parameters set, so S3's 1 m minimum, which is for flexible intervals, does not apply; each band
is at least 0.5 m (`GridAxis.MinimumFixedBand`, D-164): the corridor, and each guest-room row, so `RoomDepth` stops where the north row is 0.5 m.
Half the default corridor (0.9144 m) is valid, as T5 requires.

**Storeys.** The record's storeys come first: two storeys are the ground storey and the record's first floor. Every storey above the record's four
repeats its top storey. A copy's zone ID is the top storey's without the source floor suffix `Flr4`, followed by `_Flr{n}`, `n` the floor
number from 1: `CorridorFlr4` becomes `Corridor_Flr5`, `FrontStairsFlr4` becomes `FrontStairs_Flr5`. The guest rooms, whose IDs carry the
floor in their room number instead, keep it and take the suffix only (`GuestRoom401_Flr5`, `GuestRoom402_405_Flr5`). Names are the source's
with `(floor 5)` after them.
Each plan records `Storey` and `StoreyElevation` (*k* × `FloorHeight`) as every multi-storey generator does.

**Provenance** records `Record=small-hotel`, the six parameters, and `Gaps=G5`.

## Gap G5

The generator has one floor height, the typical upper storey's 2.7432 m. The source's ground storey is 3.3528 m, so G5 changes exactly these
quantities, and the acceptance tests exclude them with the reason `G5` and check what G5 makes of them instead:

| Quantity | What G5 makes of it | Checked |
| --- | --- | --- |
| floor height of the ground storey | 2.7432 m instead of 3.3528 m | each plan's `FloorHeight` is the parameter; the upper storeys' floor heights are the source's and are compared (the harness excludes every storey's under G5; the hotel's test compares storeys 1 to 3 again) |
| elevation of storeys 1 to 3 | *k* × 2.7432 m, each 0.6096 m below the source's | the source's elevation equals the generator's plus 3.3528 − 2.7432 m |
| ground-storey windows, per zone and orientation, where the zone shares its key's ratio | the source's × 2.7432 / 3.3528 (the walls are lower) | each within the 1 % of T4 |
| window totals per program key and orientation, where the key glazes the ground storey | the source's, less 1 − 2.7432 / 3.3528 of the key's ground-storey share (its ratio times its ground zones' true outdoor wall areas) | each within 1 %; the key's ratio times its zones' true outdoor wall areas is its window area, every key and orientation |
| window totals per orientation | the sum of the keys' totals under G5 | each within 1 % |

Plate outlines, zones, program keys, floor areas, shared walls, outdoor wall lengths (true outdoor walls included), and skylights are not changed
by G5 and are compared as they are. Volumes and wall areas of the ground storey are smaller than the source's by the same ratio; they are not
acceptance quantities.

## Acceptance (note §5)

- **T1–T3** (`CorridorHotelAcceptanceTests`): the default plans against `small-hotel.answer.json` through the harness, elevations from each plan's
  provenance. No failure; T1's excluded findings are exactly the ground storey's floor height and the three elevations above it (G5); T2 and T3
  exclude nothing; T3 gives 4,013.59 m² in total and per program key.
- **T4** through the generator's own path (D-163): one program per key from the answer key's `programGlazing` (`HarnessFixtures.KeyGlazing`),
  through `DoeProgramMap`. The window area per orientation in total and per key passes within 1 % (as G5 makes them where the ground storey
  glazes); per zone, every zone orientation that shares its key's ratio passes, and the others are reported (below). Skylights (none in the
  source) pass per zone and in total.
- **T5** (`CorridorHotelVariationTests`): `Length`, `RoomDepth`, `CorridorWidth`, and `FloorHeight` at 0.5×, 1×, and 2×, `GuestRoomBays` at 9 and
  22, and `StoreyCount` at 2 and 8 each give plans that validate with the default's zones, program keys, and adjacencies on every storey (copies
  with their copy IDs); values below the limits are `InvalidParameter`.
- **T6** (`CorridorHotelTypologyTests`): every simplifier × aggregator combination validates, canonical, at the suite's two rotated and translated
  placements, and with the fewest (2 storeys, 9 bays) and the most tested (8 storeys, 22 bays) counts. Determinism and the canonical snapshot
  (`small-hotel-canonical.txt`) are in `CorridorHotelGeneratorTests`.

Programs are the harness's fixture programs until the atlas gives them (A1–A3).

## Grasshopper component

*DOE Small Hotel* (DoeSHot, `SmallHotelComponent` in `src/Lod.Grasshopper/Components/DoeCorridorHotelComponents.cs`, GUID
`7b31e279-617d-4a06-a7c9-e8824b7ae396`) is a thin adaptor over `CorridorHotelGenerator` on P1's `DoeGeneratorComponent`
([doe-components.md](doe-components.md)), one component for the family's one record. Inputs in the order every DOE generator has, with the
record's defaults: *Storeys* (4), *Guest Room Bays* (11), *Length* (54.8646), *Room Depth* (8.2299), *Corridor Width* (1.8288), *Floor Height*
(2.7432), *Orientation* (0), *Program Map*, *Preview Location*. Outputs: *Plan* (the four storeys, bottom-up), *Multipliers* (1 for every
storey), *Program Keys* (the 14 keys, listed even without a map). The headless smoke spec is `scripts/rhino-smoke/specs/doe-hotel.py`.

## Glazing per zone through a program map

Through a program map, one ratio per program key and orientation serves every zone of the key (O3, as worded in D-164). The hotel's guest rooms
and corridors do not share one ratio in the source, so **their per-zone window areas are not the source's; only the per-key totals per orientation
are**. The guest rooms' source ratios are 0.124 on the ground storey (its 3.3528 m walls) and 0.151 on the upper storeys, north and south,
and 0.191 south for the grouped rooms 206 to 208 (and 306 to 308, 406 to 408), against the key's 0.149 north and 0.158 south; the corridors'
east and west end walls differ from their key's 0.313 and 0.395. The answer key lists them (`glazingRatioDifferences`, 43 zone orientations), and T4 reports
each of them rather than failing it:

| Storey | Zone | Key | Orientation | Source ratio | Key ratio |
| --- | --- | --- | --- | --- | --- |
| 0 | `CorridorFlr1` | Corridor | E | 0.438 | 0.313 |
| 0 | `CorridorFlr1` | Corridor | W | 0.724 | 0.395 |
| 0 | `GuestRoom101` | GuestRoom | S | 0.124 | 0.158 |
| 0 | `GuestRoom102` | GuestRoom | S | 0.124 | 0.158 |
| 0 | `GuestRoom103` | GuestRoom | S | 0.124 | 0.158 |
| 0 | `GuestRoom104` | GuestRoom | N | 0.124 | 0.149 |
| 0 | `GuestRoom105` | GuestRoom | N | 0.124 | 0.149 |
| 1 | `CorridorFlr2` | Corridor | E | 0.261 | 0.313 |
| 1 | `CorridorFlr2` | Corridor | W | 0.261 | 0.395 |
| 1 | `GuestRoom201` | GuestRoom | S | 0.151 | 0.158 |
| 1 | `GuestRoom202_205` | GuestRoom | S | 0.151 | 0.158 |
| 1 | `GuestRoom206_208` | GuestRoom | S | 0.191 | 0.158 |
| 1 | `GuestRoom209_212` | GuestRoom | S | 0.151 | 0.158 |
| 1 | `GuestRoom213` | GuestRoom | S | 0.151 | 0.158 |
| 1 | `GuestRoom214` | GuestRoom | N | 0.151 | 0.149 |
| 1 | `GuestRoom215_218` | GuestRoom | N | 0.151 | 0.149 |
| 1 | `GuestRoom219` | GuestRoom | N | 0.151 | 0.149 |
| 1 | `GuestRoom220_223` | GuestRoom | N | 0.151 | 0.149 |
| 1 | `GuestRoom224` | GuestRoom | N | 0.151 | 0.149 |
| 2 | `CorridorFlr3` | Corridor | E | 0.261 | 0.313 |
| 2 | `CorridorFlr3` | Corridor | W | 0.261 | 0.395 |
| 2 | `GuestRoom301` | GuestRoom | S | 0.151 | 0.158 |
| 2 | `GuestRoom302_305` | GuestRoom | S | 0.151 | 0.158 |
| 2 | `GuestRoom306_308` | GuestRoom | S | 0.191 | 0.158 |
| 2 | `GuestRoom309_312` | GuestRoom | S | 0.151 | 0.158 |
| 2 | `GuestRoom313` | GuestRoom | S | 0.151 | 0.158 |
| 2 | `GuestRoom314` | GuestRoom | N | 0.151 | 0.149 |
| 2 | `GuestRoom315_318` | GuestRoom | N | 0.151 | 0.149 |
| 2 | `GuestRoom319` | GuestRoom | N | 0.151 | 0.149 |
| 2 | `GuestRoom320_323` | GuestRoom | N | 0.151 | 0.149 |
| 2 | `GuestRoom324` | GuestRoom | N | 0.151 | 0.149 |
| 3 | `CorridorFlr4` | Corridor | E | 0.261 | 0.313 |
| 3 | `CorridorFlr4` | Corridor | W | 0.261 | 0.395 |
| 3 | `GuestRoom401` | GuestRoom | S | 0.151 | 0.158 |
| 3 | `GuestRoom402_405` | GuestRoom | S | 0.151 | 0.158 |
| 3 | `GuestRoom406_408` | GuestRoom | S | 0.191 | 0.158 |
| 3 | `GuestRoom409_412` | GuestRoom | S | 0.151 | 0.158 |
| 3 | `GuestRoom413` | GuestRoom | S | 0.151 | 0.158 |
| 3 | `GuestRoom414` | GuestRoom | N | 0.151 | 0.149 |
| 3 | `GuestRoom415_418` | GuestRoom | N | 0.151 | 0.149 |
| 3 | `GuestRoom419` | GuestRoom | N | 0.151 | 0.149 |
| 3 | `GuestRoom420_423` | GuestRoom | N | 0.151 | 0.149 |
| 3 | `GuestRoom424` | GuestRoom | N | 0.151 | 0.149 |
