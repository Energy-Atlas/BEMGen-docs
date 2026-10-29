# The DOE tower hotel generator (`TowerHotel`)

> **Status:** Provisional (stage P5b of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md), pending the owner's reading) · **Code:** `src/Lod.Generators/Doe/TowerHotel/`, shared with the hospital in `src/Lod.Generators/Doe/MultipliedRooms/` · **Tests:** `tests/Lod.Generators.Tests/Doe/TowerHotel/`, `tests/Lod.Integration.Tests/MultipliedRoomTypologyTests.cs` · **Decisions:** [ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md), [ADR-026](../decisions/ADR-026-multiplied-rooms.md), [ADR-015](../decisions/ADR-015-plans-per-storey.md)

`TowerHotelGenerator` builds the DOE large hotel (record `large-hotel`, [doe-layouts.md](doe-layouts.md)): a podium storey under a
double-loaded guest-room tower. It returns one plan per record storey, bottom-up (ADR-015): the ground storey (7 zones), the typical floor
(7 zones), which stands for every storey between the ground and the top one, and the top storey (7 zones). Every zone has its standards space
type as program key and takes its preset from a `DoeProgramMap` (S4). The typical floor's two repeated guest rooms are drawn once with their
multiplier (O5, S8), and so is the top storey's; each storey with a repeated room is one plate whose copy space is where the copies stand
(ADR-026). Zone IDs and names are the source zones'.

## Parameters

`TowerHotelParameters`, counts first; `Default` reproduces the record.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `Storeys` | 6 | the ground storey, the typical floor, and the top storey; at least 3 (each record storey drawn once). The typical floor stands for `Storeys − 2`. |
| `GuestRoomsPerRow` | 19 | the multiplier of the typical floor's two repeated guest rooms (`Room_3_Mult19_Flr_3`, `Room_4_Mult19_Flr_3`); at least 2 |
| `Length` | 86.563 m | plate length along plan x (S3, below) |
| `Depth` | 22.86 m | plate depth along plan y, the ground storey's (S3, below) |
| `FloorHeight` | 3.048 m | every storey's floor-to-floor height (G5) |
| `OrientationDegrees` | 0 | clockwise rotation of plan north from true north |

The top storey's repeated room keeps the source's ×9: `GuestRoomsPerRow` counts the typical floor's rooms only. A count changes the multiplier,
not the drawing: the plan is the DOE drawing, not the building (ADR-026). `Length` changes only the run of copies, so on the typical floor the copy
space follows the count when `Length` adds one guest-room bay (`TowerHotelGenerator.SourceBayWidth`, Room_3's 3.657 m) per room added. Even then
it is not exact: in the source the typical floor's copy space exceeds (rooms − 1) × the drawn rooms by 0.027 m², and each room added changes that
by 0.0067 m², because Room_4 is 1 mm wider than the bay. The top storey's copy space grows with `Length` too, while its room keeps ×9, so there
the copies no longer fill it.

## Size variation (S3)

The axes are the union of the three storeys' cuts (`GridAxis.Union`), so a coordinate several storeys share moves alike on all of them.

- **x.** The flexible intervals are those inside the typical floor's run of copies, its widest interval (14.021 m to 76.2 m), which is copy space
  on both guest-room rows; the record checks it. Every other interval is fixed: the drawn guest-room bays, the corner rooms, and the stair and
  corridor ends. A change of `Length` goes into the run of copies on every storey alike.
- **y.** The fixed intervals are the typical floor's corridor band, between the two repeated rooms' rows (12.497 m to 16.154 m); the podium's
  setback and the guest-room rows are flexible.

**Valid ranges** at the defaults (`TowerHotelGenerator.Limits()`, the S3 rule as amended in P1, D-164: flexible intervals share a change by their
slack, the length less 1 m, so all reach 1 m together; found by bisection of the generator's own check, so they are exactly what it accepts):

| Parameter | Default | Valid range | 0.5× / 2× |
| --- | --- | --- | --- |
| `Length` | 86.563 m | at least 30.384 m (0.35×: 24.384 m fixed and the run's six intervals at 1 m) | both valid |
| `Depth` | 22.86 m | at least 7.657 m (0.33×: the 3.657 m corridor band and four intervals at 1 m) | both valid |
| `FloorHeight` | 3.048 m | any positive | both valid |
| `Storeys` | 6 | at least 3 | 3 and 12 valid |
| `GuestRoomsPerRow` | 19 | at least 2 | 2 and 38 valid |

The hotel has no fixed band that a size parameter sets, so `GridAxis.MinimumFixedBand` does not apply. Every size parameter reaches ±20 % of its
default. Under P0a's rule the limits were 37.133 m and 9.957 m.

## Storeys, multipliers, and G5

`TowerHotelGenerator.Storeys(parameters)` gives each plan's first storey, storey multiplier, base elevation, and reference elevation:

| Plan | First | Multiplier | Elevation | Reference elevation |
| --- | --- | --- | --- | --- |
| ground | 0 | 1 | 0 | 0 |
| typical | 1 | `Storeys − 2` (4) | `FloorHeight` (3.048 m) | its lower middle storey, 1 + ⌊(N − 1)/2⌋ (6.096 m) |
| top | `Storeys − 1` (5) | 1 | 15.24 m | 15.24 m |

The generator overrides `MultiStoreyPlanGenerator.StoreyMultiplier` with these multipliers (ADR-015, D-164), so the typical plan records
`StoreyMultiplier` (4) in its provenance and the top plan's `StoreyElevation` counts it (15.24 m). The multipliers are the floor entries'
multipliers that rebuild the generator's building; the component outputs them as *Multipliers*. The reference elevation still comes from the
parameters (T1). A ×19 room on the ×4 floor counts 76 rooms in every
total (ADR-026), under `Stack` and *Stacked Floor Zone Multiplier* alike.

**G5.** One floor height per generator, the typical floor's 3.048 m; the source's ground storey is 3.9624 m. G5 changes the ground storey's floor
height, the elevations above it (each 0.9144 m lower than the source's, within T1's 0.01 m of it once that difference is added back), and the
ground storey's windows (its walls are 3.048 m high, so each window is the source's × 3.048 / 3.9624), with the window totals and the totals of
the ground storey's program keys, none of which is on another storey. The acceptance tests exclude exactly these quantities and check what G5
makes of them. **G3.** The 1,978.83 m² basement is omitted; the answer key's totals are above grade.

**Open for the owner: D-045 and the reference's storey.** The reference draws the ×4 floor's representative at its lower middle storey (storey 2
of storeys 1 to 4, elevation 7.008 m in the source); *Stacked Floor Zone Multiplier* represents the group at first + ⌊N/2⌋ (D-045), storey 3.
T1 checks the reference elevations from the generator's parameters; D-045 is unchanged, since changing it would alter existing snapshots. Stage
P1 records the same difference for the large office's ×10 floor.

## Provenance

`LayoutRecord` (`large-hotel`), `LayoutSources` (each source file with its SHA-256), `Gaps` (`G3,G5`), `Storeys`, `GuestRoomsPerRow`, `Length`,
`Depth`, with the parameters every plan records (ADR-015).

## Acceptance (design note §5)

| Check | Test | Result |
| --- | --- | --- |
| T1 | outlines, storey count, multipliers, upper floor heights; reference elevations from the parameters plus G5's 0.9144 m | pass; G5 excludes 3 quantities |
| T2 | zones, program keys, areas, shared and self-adjacent walls, outdoor and true outdoor walls, roofs and exposed floors per zone | pass, nothing excluded |
| T3 | 9,366.457 m² in total and per program key | pass |
| T4 | one program per key at its `programGlazing` ratio: window area per zone, per orientation in total and per key, skylights | pass on the upper storeys; the ground storey's windows and totals are the source's × 3.048 / 3.9624 (G5) |
| T5 | `Length`, `Depth`, `FloorHeight` at 0.5×, 1×, 2×; `Storeys` at 3 and 12; `GuestRoomsPerRow` at 2 and 38; the limits and just below | same zones and adjacencies; below the limits `InvalidParameter` |
| T6 | every supported simplifier × aggregator, canonical and at two rotated placements; the rest `NotSupported` | validates |

Phase P5: every total (floor area, volume, outdoor wall, glazing, every load) counts each zone times its multiplier; *Semantic Merge* and
*Conditioned Merge*, with and without *Join Pieces*, never merge zones of different multipliers; *Perimeter Core* and *Single Zone per Floor*
are `NotSupported` on the typical and top storeys, *Single Zone per Floor Type* and *Single Zone Building* on the building. The answer key lists
no zone whose ratio differs from its key's (`glazingRatioDifferences` is empty).

## Component

*DOE Large Hotel* (DoeLHtl, `LargeHotelComponent`, `8b61c4c7-2d19-4a1a-b83d-cea9254b634a`) on the `DoeGeneratorComponent` base
([doe-components.md](doe-components.md)): *Storeys* (6), *Guest Rooms Per Row* (19), *Length* (86.563), *Depth* (22.86), *Floor Height* (3.048),
*Orientation* (0), *Program Map*, *Preview Location*; outputs *Plan* (three plans), *Multipliers* (1, `Storeys − 2`, 1), *Program Keys* (15).
The limits in the input descriptions come from `Limits()`. Smoke spec: `scripts/rhino-smoke/specs/doe-multiplied-rooms.py`.

## Pending

Sourced programs wait on the atlas (A1–A3); the tests use fixture programs. For a person in Rhino 8: the look of the toolbar icon (a tall slab tower on a wider podium, one room bay solid, its copies dashed) and the viewport
preview.
