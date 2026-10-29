# DOE outpatient generator

> **Status:** Accepted (stage P6 of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md); the owner, with PR #1, D-176) · **Code:** `src/Lod.Generators/Doe/Outpatient/` · **Tests:** `tests/Lod.Generators.Tests/Doe/Outpatient/`, `tests/Lod.Integration.Tests/OutpatientTypologyTests.cs` · **Record:** `outpatient` ([DOE layout records](doe-layouts.md))

`OutpatientGenerator` builds the DOE outpatient health-care building, three storeys of 59, 41, and 26 zones, from its layout record, one plan per
storey through `MultiStoreyPlanGenerator` ([ADR-015](../decisions/ADR-015-plans-per-storey.md)) because the storeys differ, and `GridPlanLayout`
([ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md), S1). At its defaults every storey is the record's storey through
`GridPlanLayout`, vertex for vertex. Geometry only: each zone keeps its source ID, name, and standards space type as program key, and takes its
program from a `DoeProgramMap` by that key (S4, `OutpatientGenerator.ProgramKeys`, 32 keys). The Grasshopper component is *DOE Outpatient* (below), on the
shared DOE component support of P1 ([doe-components.md](doe-components.md)).

## Structure

The plate is 51.816 × 35.3568 m on the ground storey. The ground storey (59 zones: surgery, recovery, MRI, lobby, cafe, offices, services) has an
outline of 18 vertices and reaches 4.57 m further north than the upper storeys, to the north-east stair; the second storey (exam rooms, reception,
offices, X-ray) and the third (physical therapy, offices, undeveloped space) are 51.816 × 30.7848 m with outlines of 14 vertices. No storey has a
court. The note's 59/37/22 zones per storey are the source's; the record, and so the generator, has 59/41/26: each upper storey adds its copy of
the three stairs (north-east, north-west, south-west) and the lift (G4, D-161).

`OutpatientGrid` reads the S3 structure from the record's cells and program keys, never from a zone name (D-061):

- each axis is the union of every storey's cuts (42 intervals along x, 36 along y; `GridAxis.Union`), so a coordinate several storeys share moves
  alike on all of them;
- a **corridor strip** is a zone of space type `Corridor` (keys `Hall` and `Hall_infil`) of one cell rectangle whose long side is at least
  `OutpatientGrid.MinimumCorridorAspect` = 3 times its short side. The record has 17: 11 running north–south (the ground storey's pre-op, sterile,
  and utility halls; the second storey's six exam halls and office hall; the third storey's mechanical hall) and 6 running east–west (the ground
  storey's IT, locker-room, and nurse halls; the second storey's reception and work halls; the third storey's office hall). They are 4 to 23
  times as long as wide; the other seven halls (lobby, MRI, and ground-floor reception halls, scrub, sub-sterile, vestibule, third-floor elevator
  hall) are at most 2.3 times as long as wide or not one rectangle, and are rooms for S3;
- an interval inside a strip's width is a **corridor band** (11 along x, 10.668 m; 10 along y, 8.5344 m);
- any other interval shorter than 1 m is **short** and keeps its source length (14 along x, 7.3152 m; 17 along y, 8.8392 m); under the
  amended S3 such an interval has no slack anyway (D-164);
- every other interval is **flexible** (17 along x, 33.8328 m; 9 along y, 17.9832 m; the shortest 1.2192 m on both axes).

A record without this form (storeys of different heights or with a multiplier, a zone without a key or with a multiplier, no strip along one of
the axes) fails with an `InvalidDataException` naming the reason.

## Parameters

`OutpatientParameters(PlateLength, PlateDepth, CorridorWidth, FloorHeight, OrientationDegrees)`; `Default` reads the values from the record and
reproduces it. There are no counts: the building has no repeated unit, and always has the record's three storeys (`OutpatientGenerator.StoreyCount`).

| Parameter | Default | Rule | Valid range at the other defaults (D-164) |
| --- | --- | --- | --- |
| `PlateLength` | 51.816 m | The x axis's flexible intervals share the change in proportion to their slack (length less 1 m); corridor bands and short intervals keep their length. | 34.9832 m (0.675 ×) and longer |
| `PlateDepth` | 35.3568 m | The same along y; the ground storey's depth, the upper storeys keep their share. | 26.3736 m (0.746 ×) and deeper |
| `CorridorWidth` | 1.8288 m | The most common strip width (11 of 17 strips); every corridor band scales by `CorridorWidth` / 1.8288, so the 2.4384 m and 1.524 m strips keep their ratio; every strip at least `GridAxis.MinimumFixedBand` (0.5 m); then both axes are resized to the plate. | 0.6 m (0.328 ×) to 3.7538 m (2.053 ×) |
| `FloorHeight` | 3.048 m | Every storey; the source's storeys are all 3.048 m (no G5). | above 0 |
| `OrientationDegrees` | 0 | Clockwise rotation of plan north from true north. | any |

`OutpatientGenerator.SizeLimits(parameters)` gives the limits for any other parameters (`OutpatientLimits`): the shortest plate is the corridor
bands (10.668 m along x, 8.5344 m along y, times `CorridorWidth` / 1.8288) plus the short intervals (7.3152 m, 8.8392 m) plus 1 m per flexible
interval (17, 9); the widest corridor leaves every flexible interval at 1 m on the axis that reaches it first (y at the default plate; x, at
4.7144 m, on a plate deeper than 39.84 m); the narrowest corridor makes the narrowest strip, the ground storey's 1.524 m IT hall, 0.5 m wide.

A plate below its limit, or a corridor above its widest, is `InvalidParameter` naming the shortest valid length and, for a changed corridor, the
corridor width (at 4 m corridors: `PlateDepth (with CorridorWidth 4 m) 35.357 m is shorter than the shortest valid …`); a corridor below its
narrowest names the strip (`CorridorWidth 0.5999 m makes the corridor strip Floor_1_IT_Hall 0.499917 m wide; a fixed band must be at least 0.5 m (S3),
so CorridorWidth must be at least 0.6 m.`). A length that is not positive and finite is `InvalidParameter` too.

**T5 (D-164).** Every size parameter at 0.5×, 1×, and 2× of its default keeps every storey's zones, program keys, and adjacencies, except 0.5×
`PlateLength` and 0.5× `PlateDepth`, which lie below their limits and are `InvalidParameter`. Each of the four limits in the table is computed by
`SizeLimits`, equals the generator's own boundary found by bisection on its checks within 0.1 mm, keeps the topology at the limit, and is
`InvalidParameter` 1 mm beyond it; the narrowest corridor is also tested 0.1 mm either side. Both plates grow without limit. Every limit is more
than 20 % from its default: the plate shortens by up to 32.5 % (x) and 25.4 % (y), the corridor narrows by 67.2 % and widens by 105.3 %.

**What the amended S3 changed (D-164).** Under P0a's rule (flexible intervals in proportion to their length) the limits were 45.7332 m,
32.1236 m, and corridors up to 2.5216 m, with 2× `CorridorWidth` invalid and neither plate able to shorten by 20 %; sharing by slack lets all
17 (x) and 9 (y) flexible intervals reach 1 m together. The corridor had no lower limit before the fixed-band minimum: 1e-4 m validated, 1e-6 m
gave `OverlappingZones`, and 1e-8 m `DisconnectedGroup`.

## Gaps and source facts

- **G4 (S7).** The three stairs and the lift are 9.144 m tall zones on the ground storey of the source, spanning all three storeys. The record
  draws one zone of each per storey at the storey height, with the ground storey's ID (`NE_Stair`, `NW_Elevator`, `NW_Stair`, `SW_Stair`,
  `OutpatientGenerator.G4Zones`), footprint, and key; the floor aggregators prefix them with the storey (`L{k}/`). The answer key marks them `G4`
  on every storey, and the acceptance tests exclude exactly their quantities: on the ground storey their true outdoor walls (T2) and windows and
  skylights (T4), whose source values are those of 9.144 m walls. Every `Stair` zone is under G4, so the key's per-key glazing has no ratio for
  `Stair` and the stairs and lift take no windows; both sides of the T4 totals leave their source windows out. The copies' areas and outdoor wall
  lengths are compared and agree.
- **Source boundary artifacts (D-162).** The source exposes 26.52 m of the second-floor reception hall's 28.65 m south wall to outdoor air,
  although eight rooms adjoin it (exam rooms 1 to 3, exam halls 1 to 3, dictation, lounge) and their own walls name themselves. The generator draws
  those 26.52 m as interzone walls; the hall's outdoor wall is its true outdoor wall of 2.13 m. Likewise every self-referencing source wall between
  zones of multiplier 1 is an ordinary interzone wall here (ADR-026, D-162); in the Chicago new2004 reference file 398 of the 448 walls with a
  `Surface` boundary name themselves, and every zone has multiplier 1: every wall of the plans is `Outdoors` or `Interzone`, and no zone has a
  multiplier. An energy comparison with the source must know these walls differ.
- **The note's figures.** The note gives 59/37/22 zones per storey (the source's; the record has 59/41/26 with the G4 copies) and the brief gives
  outlines of 18 and 12 vertices; the record and the answer key have 18 and 14 (the upper storeys' outline includes the north-west stair's bay,
  3.9624 to 11.2776 m east, 28.3464 to 30.7848 m north).

## Acceptance

`OutpatientAcceptanceTests` compares the generator at its defaults with the answer key through the harness (`DoeComparison`,
`ToleranceSettings.Acceptance`):

- **T1:** three storeys, outlines, elevations 0, 3.048, and 6.096 m (the generator's k × `FloorHeight`, from provenance), floor heights, and
  multipliers; nothing excluded.
- **T2:** zones per storey, program keys, areas, outdoor walls per orientation, true outdoor walls, shared walls; excluded only the ground
  storey's stair and lift true outdoor walls (G4, 16 quantities).
- **T3:** 3,914.75 m² in total (the source's 3,804.01 m² plus the 110.74 m² of the G4 copies) and per program key, 32 keys; nothing excluded.
- **T4 (D-163):** on the generator's path, one program per key from the answer key's per-key glazing (`HarnessFixtures.KeyGlazing`,
  `programGlazing`; until atlas input A2): window area per orientation in total and per key (window area per orientation and skylight area of
  each of the 31 glazed keys) agree within 1 %; the source has no skylights. Per-zone glazing agrees wherever a key's zones share one ratio.
  Excluded: the ground stairs' and lift's windows and skylights (G4, 20 quantities). Reported, not failed: the 38 zone quantities the answer key
  lists in `glazingRatioDifferences`, whose own source ratio misses their key's by more than 1 % (zones of one key glazed differently in the
  source); a test checks the reported set is exactly the listed one.

T5 is `OutpatientVariationTests` (above). T6 is `OutpatientTypologyTests`: every simplifier × aggregator combination validates, canonical, at the
test suite's two rotated and translated placements, and at three sizes: the shortest plate on both axes (34.9832 × 26.3736 m), the narrowest
corridor (0.6 m), and a plate of twice the default with 2.5 m corridors. *Perimeter Core* needs a depth under half the north–south extent of the
plate's east bay (x 50.5968 to 51.816 m, y 26.2128 to 28.3464 m, on every storey: a 0.6096 m short and a 1.524 m flexible interval). By default
that is 2.1336 m, so the depth must stay under 1.0668 m, the pipeline's 4.57 m is `PlanTooNarrow` (ADR-008), and the matrix runs it at 1 m; on the shortest plate it is 1.6096 m (depth under 0.8048 m), and the
matrix runs it at 0.8 m. A test asserts each depth and that 1.0669 m and 0.8049 m are `PlanTooNarrow`. Determinism and the canonical snapshot
(`outpatient-canonical`) are in `OutpatientGeneratorTests`.

## Component

*DOE Outpatient* (DoeOutP, panel *2 Generate*, the DOE group; `src/Lod.Grasshopper/Components/DoeOutpatientComponents.cs`, GUID
`5d0c7a3e-9b41-4f6e-a8d2-3c1e7b590f64`) is a thin adaptor on `DoeGeneratorComponent` over `OutpatientGenerator`, one component for the family's
one record. Its inputs, in the DOE order (no counts): *Plate Length* (51.816), *Plate Depth* (35.3568), *Corridor Width* (1.8288), *Floor Height*
(3.048), *Orientation* (0), *Program Map*, *Preview Location*; each size input's description gives its limits at the defaults. Its outputs are
*Plan* (three plans, bottom-up), *Multipliers* (1, 1, 1), and *Program Keys* (the 32 keys, listed even without a map). The presets come through
*DOE Program Map*, one per key or one for every key. The headless check is `scripts/rhino-smoke/specs/doe-outpatient.py`.

## Provenance

Every plan records `Record=outpatient`, `Sources` (each source file with its role and SHA-256), `PlateLength`, `PlateDepth`, `CorridorWidth`,
`Gaps=G4`, the floor height and orientation, the presets, and its `Storey` and `StoreyElevation`.
