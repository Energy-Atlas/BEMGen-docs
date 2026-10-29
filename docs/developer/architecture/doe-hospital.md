# The DOE hospital generator (`Hospital`)

> **Status:** Accepted (stage P5b of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md); the owner, with PR #1, D-176) · **Code:** `src/Lod.Generators/Doe/Hospital/`, shared with the tower hotel in `src/Lod.Generators/Doe/MultipliedRooms/` · **Tests:** `tests/Lod.Generators.Tests/Doe/Hospital/`, `tests/Lod.Integration.Tests/MultipliedRoomTypologyTests.cs` · **Decisions:** [ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md), [ADR-026](../decisions/ADR-026-multiplied-rooms.md), [ADR-015](../decisions/ADR-015-plans-per-storey.md), D-163

`HospitalGenerator` builds the DOE hospital (record `hospital`, [doe-layouts.md](doe-layouts.md)): five storeys of 9, 11, 13, 13, and 8 zones,
one plan per storey, bottom-up (ADR-015), every storey 4.2683 m high, so G5 does not apply. Every zone has its standards space type as program
key and takes its preset from a `DoeProgramMap` (S4). Its 17 repeated rooms (×4 to ×10) are drawn once with their multiplier (O5, S8), each storey
one plate whose copy space is where the copies stand (ADR-026); the ground storey's drawn zones are two polygons on that plate
(`ER_Trauma2_Flr_1` stands apart). Zone IDs and names are the source zones'.

## Parameters

`HospitalParameters`, counts first; `Default` reproduces the record. `RoomMultipliers` is a read-only copy of the values given, so
neither the caller's array nor `Default` can be changed through it; equality compares the multipliers item by item.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `RoomMultipliers` | 4, 4, 4, 4, 5, 6, 5, 10 × 8, 5, 6 | one per repeated room of `HospitalGenerator.MultipliedRooms`, bottom-up in the record's order; each at least 2 |
| `PlateLength` | 70.104 m | plate length along plan x (S3, below) |
| `PlateDepth` | 53.34 m | plate depth along plan y (S3, below) |
| `CorridorWidth` | 4.572 m | the narrowest corridor leg, the patient floors' west and east corridors; every corridor band scales with it |
| `FloorHeight` | 4.2683 m | every storey's floor-to-floor height |
| `OrientationDegrees` | 0 | clockwise rotation of plan north from true north |

The repeated rooms are `ER_Exam1_Mult4_Flr_1`, `ER_Exam3_Mult4_Flr_1`, `ER_Triage_Mult4_Flr_1`, `Office1_Mult4_Flr_1` (ground);
`IC_PatRoom1_Mult5_Flr_2`, `IC_PatRoom3_Mult6_Flr_2`, `OR2_Mult5_Flr_2` (first); `PatRoom1`, `PatRoom3`, `PatRoom5`, `PatRoom7` ×10 on each patient
floor (second and third); `Office2_Mult5_Flr_5`, `Office4_Mult6_Flr_5` (top). A multiplier changes how many rooms a zone stands for, not the
drawing (ADR-026); the source itself does not tie the copy space to the copies (D-163: the ×4 office leaves room for four copies, not three).

## Size variation (S3)

The axes are the union of the five storeys' cuts (`GridAxis.Union`). The fixed intervals are the corridor bands: the span across each corridor
leg, a cell rectangle of a corridor zone at least `HospitalGrid.LegAspect` (3) times as long as it is wide, which leaves out the short stubs that
join the legs to the façade (their ratio is 2.3 to 2.7, the legs' 5 to 10). Along x: the north-south spine of the ground and first storeys
(10.668 m), the patient floors' west and east legs (4.572 m), and the top storey's west leg (6.096 m); along y: the patient floors' south leg and
the north leg of the patient floors and the top storey (6.096 m). `CorridorWidth` scales every band by its ratio to the narrowest (4.572 m); then
each axis is resized to its plate, the flexible intervals taking the change.

**Valid ranges** at the defaults (`HospitalGenerator.Limits`, the S3 rule as amended in P1, D-164: flexible intervals share a change by their
slack; found by bisection of the generator's own check). Every band a size parameter sets is at least `GridAxis.MinimumFixedBand` (0.5 m,
D-164), per band, not per grid interval; `CorridorWidth` is the narrowest band, so it is at least 0.5 m.

| Parameter | Default | Valid range | 0.5× / 2× |
| --- | --- | --- | --- |
| `PlateLength` | 70.104 m | at least 35.908 m (0.51×: 25.908 m of bands and ten intervals at 1 m) | 0.5× invalid, the limit tested; 2× valid |
| `PlateDepth` | 53.34 m | at least 24.192 m (0.45×: 12.192 m of bands and twelve intervals at 1 m) | both valid |
| `CorridorWidth` | 4.572 m | 0.5 m to 10.607 m (0.11× to 2.32×; at the top every flexible interval along x is 1 m) | both valid |
| `FloorHeight` | 4.2683 m | any positive | both valid |
| `RoomMultipliers` | 4 to 10 | each at least 2 | each at 2 and at twice its default valid |

Every size parameter reaches ±20 % of its default. Under P0a's rule the limits were 54.908 m, 39.290 m, and at most 7.254 m with no minimum band,
so `PlateDepth` at 0.5× and `CorridorWidth` at 2× were invalid as well.

## Source boundary artifact

`OR_NurseSat_Flr_2_Wall_1_East` (x = 70.104 m, y 0 to 16.764 m) names itself in the reference IDF, so the source treats 16.764 m of the plate's
east façade as adiabatic, although no zone and no copy stands beyond it. Geometry decides (D-163): BEMGen draws it as an outdoor wall of
`OR_NurseStn_Lobby_Flr_2`, with its windows, and T2 agrees with the answer key (`nonOutdoorExteriorWalls`). An energy comparison with the source
must name it.

## Provenance

`LayoutRecord` (`hospital`), `LayoutSources` (each source file with its SHA-256), `Gaps` (`G3`), `RoomMultipliers` (`id=multiplier`, in order),
`PlateLength`, `PlateDepth`, `CorridorWidth`, with the parameters every plan records (ADR-015).

## Acceptance (design note §5)

| Check | Test | Result |
| --- | --- | --- |
| T1 | outlines (the drawn outline, two polygons on the ground storey), storey count, elevations k × 4.2683 m, floor heights | pass |
| T2 | zones, program keys, areas, shared and self-adjacent walls, outdoor and true outdoor walls (the east plate edge included), roofs and exposed floors per zone | pass |
| T3 | 18,682.874 m² in total and per program key | pass |
| T4 | one program per key at its `programGlazing` ratio: window area per orientation in total and per key, skylights, and per zone | pass, 210 per-zone window findings; the six zone quantities of `glazingRatioDifferences` (the offices and nurse stations whose own ratio differs from their key's) reported, exactly those |
| T5 | sizes at 0.5×, 1×, 2× or their limits; each of the 17 multipliers at 2 and at twice its default | same zones and adjacencies; beyond the limits `InvalidParameter` |
| T6 | every supported simplifier × aggregator, canonical and at two rotated placements; the rest `NotSupported` | validates |

G3: the 3,739.35 m² basement is omitted; the answer key's totals are above grade, so nothing is excluded. Phase P5: every total (floor area,
volume, outdoor wall, glazing, roof, every load) counts each zone times its multiplier; *Semantic Merge* and *Conditioned Merge*, with and without
*Join Pieces*, never merge zones of different multipliers; *Perimeter Core* and *Single Zone per Floor* are `NotSupported` on every storey,
*Single Zone per Floor Type* and *Single Zone Building* on the building.

## Component

*DOE Hospital* (DoeHosp, `HospitalComponent`, `da2d1dab-1994-420f-87d6-8cae8ea567a4`) on the `DoeGeneratorComponent` base
([doe-components.md](doe-components.md)): *Room Multipliers* (a list of 17 integers, the defaults above, in the order of
`HospitalGenerator.MultipliedRooms`, which the input's description lists as `index: zone ID`; another count is `InvalidParameter` naming the
count), *Plate Length* (70.104), *Plate Depth* (53.34), *Corridor Width* (4.572), *Floor Height* (4.2683), *Orientation* (0), *Program Map*,
*Preview Location*; outputs *Plan* (five plans), *Multipliers* (1 each), *Program Keys* (18). The limits in the input descriptions come from
`Limits`. Smoke spec: `scripts/rhino-smoke/specs/doe-multiplied-rooms.py`.

## Pending

Sourced programs wait on the atlas (A1–A3); the tests use fixture programs. For a person in Rhino 8: the look of the toolbar icon (a square plate crossed by two corridors, one room solid, its copies dashed) and the viewport
preview.
