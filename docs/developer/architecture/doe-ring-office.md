# The ring office generator (DOE geometry P1)

> **Status:** Provisional (stage P1 of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md), pending the owner's reading) · **Code:** `src/Lod.Generators/Doe/RingOffice/` · **Data:** the `small-office`, `medium-office`, and `large-office` layout records ([doe-layouts.md](doe-layouts.md)) · **Tests:** `tests/Lod.Generators.Tests/Doe/RingOffice/`, `tests/Lod.Integration.Tests/RingOfficeTypologyTests.cs`

`RingOfficeGenerator` builds the three DOE offices: the openstudio-standards detailed office rooms on the DOE reference plates and elevations
(O6, O8). Each office is a ring of perimeter rooms around a corridor ring and a core. The generator lays out every record storey through
`GridPlanLayout` (S1), one plan per storey (`MultiStoreyPlanGenerator`, [ADR-015](../decisions/ADR-015-plans-per-storey.md)). Every zone carries
its standards space type as its program key and takes its preset from a `DoeProgramMap` (S4). Its Grasshopper components are described in
[doe-components.md](doe-components.md).

## Records

`RingOfficeRecord` chooses the default plan; `RingOfficeParameters.Default(record)` reproduces it.

| Record | Layout record | Storeys drawn | Zones per storey | Storeys | Floor height | Gaps (S7) |
| --- | --- | --- | --- | --- | --- | --- |
| `Small` | `small-office` | 1 | 17 | 1 | 3.05 m | G2: a flat roof at the zone top |
| `Medium` | `medium-office` | 3 | 23, 21, 21 | 3 | 3.9624 m | G1: the plenum inside the zone |
| `Large` | `large-office` | 3 | 26, 26, 26 | 12 (1, 10, 1) | 3.9632 m | G1; G3: no basement |

Zone IDs and names are the source rooms' (`OpenOffice_Mid_ZN_1`); the floor aggregators prefix them with the storey (`L{k}/`). The small office
has no plenum, so G1 does not apply to it (D-161).

## Parameters

| Parameter | Meaning | Small | Medium | Large |
| --- | --- | --- | --- | --- |
| `Record` | the default plan | `Small` | `Medium` | `Large` |
| `PlateLength` | plate length along plan x, m | 27.690763 | 49.911 | 73.10755 |
| `PlateDepth` | plate depth along plan y, m | 18.45945 | 33.274 | 48.737837 |
| `Storeys` | number of storeys | 1 | 3 | 12 |
| `FloorHeight` | floor-to-floor height, m | 3.05 | 3.9624 | 3.9632 |
| `PerimeterDepth` | the top storey's south perimeter, façade to corridor, m | 4.572 | 5.341938 | 12.161838 |
| `CorridorWidth` | the top storey's south corridor, m | 1.2192 | 1.2192 | 1.523999 |
| `OrientationDegrees` | clockwise rotation of plan north from true north | 0 | 0 | 0 |

The family has no repeated-unit count (note §4). The defaults are the records' figures rounded to 1e-6 m (`RecordDecimals`, tied to `extract.py`); `PerimeterDepth` and `CorridorWidth` are the top storey's south bands.

### Size variation (S3)

Both axes are the union of the record storeys' cuts (`GridAxis.Union`), so a coordinate the storeys share moves alike on all of them. Each interval
takes its class from the record's typical storey, the top one. The corridor ring is that storey's corridor zones (space type `Corridor` from the
program key): on each side, its outer edge is the outermost cut of a corridor cell and its inner edge the nearest inner cut of a cell on that edge.

| Class | Intervals | Under a change |
| --- | --- | --- |
| perimeter | between the façade and the corridor ring | scaled by `PerimeterDepth` over its default, fixed under a plate change |
| corridor | within the corridor ring | scaled by `CorridorWidth` over its default, fixed under a plate change |
| core | the rest | flexible: share a change of the plate length or depth in proportion to their slack, their length less 1 m (S3 as amended in P1); a core interval of 1 m or less (wall offsets, such as the small office's 0.495 m) has no slack and keeps its source length |

`PerimeterDepth` is the top storey's south perimeter exactly, and every other perimeter side, on every storey, scales by the same ratio;
`CorridorWidth` likewise sets the south corridor and scales the other three sides. A plate shorter than its limit, or a ring too deep for the
plate, is `InvalidParameter` (`GridAxis.Resize`); the message names the plate parameter and, when they differ from the defaults,
`PerimeterDepth` and `CorridorWidth`. Lengths that are not positive and finite, and fewer storeys than the record draws, are `InvalidParameter`
too. The other storeys follow the typical storey's grid: the large office's ground-floor corridor, which lies elsewhere, keeps its place on the
grid and changes with the core.

`RingOfficeGenerator.Limits(parameters)` gives the limits for the other parameters as given. At a limit every core interval is 1 m (or its own
length under 1 m) on the axis concerned, and the plan keeps every zone and adjacency. At the defaults:

| Record | `PlateLength` | `PlateDepth` | `PerimeterDepth` | `CorridorWidth` | `FloorHeight` | `Storeys` |
| --- | --- | --- | --- | --- | --- | --- |
| `Small` | ≥ 16.573 m (0.60 of the default) | ≥ 13.582 m (0.74) | 0.5 m (0.11) to 7.011 m (1.53) | 0.5 m (0.41) to 3.658 m (3.00) | > 0 | ≥ 1 |
| `Medium` | ≥ 23.994 m (0.48) | ≥ 17.121 m (0.51) | 0.593 m (0.11) to 13.420 m (2.51) | 0.5 m (0.41) to 9.296 m (7.62) | > 0 | ≥ 3 |
| `Large` | ≥ 49.107 m (0.67) | ≥ 34.402 m (0.71) | 0.5 m (0.04) to 19.321 m (1.59) | 0.5 m (0.33) to 8.692 m (5.70) | > 0 | ≥ 3 |

Plates have no upper limit. Every perimeter and corridor band of every side is at least `GridAxis.MinimumFixedBand`, 0.5 m (the controller's
limit under D-098), so the shallowest perimeter and the narrowest corridor are where the narrowest side reaches it: the medium office's west and
east perimeters are 4.504 m against its 5.342 m south one, so its `PerimeterDepth` stops at 0.593 m. Below it is `InvalidParameter`, naming the
side. Every size reaches at least ±20 % of its default. T5
tests every size at 0.5×, 1×, and 2× of its default; a factor beyond its limit is `InvalidParameter`, and the limit itself and a value 0.01 m
beyond it are tested in its place: half the plate length of the small and large offices, half the plate depth of all three, and twice the
perimeter depth of the small and large offices.

## Storeys and the storey multiplier

A record of one storey repeats it: the small office with `Storeys = 2` is one plan that stands for two storeys. A record of three storeys draws
its bottom and top storey once, and its middle storey stands for the rest: `Storeys − 2` storeys. `RingOfficeGenerator.Storeys(parameters)` gives
for each plan the first storey it stands for, its multiplier, its base elevation, and the elevation of the storey the reference draws for it. The
plans record the multiplier as `StoreyMultiplier` and their base elevation as `StoreyElevation` (ADR-015). The multipliers are the floor entries'
multipliers: `Stack` with them gives the whole building, and the Grasshopper component outputs them for the aggregators' *Multipliers*.

| Large office plan | First storey | Multiplier | Base elevation | Reference's storey |
| --- | --- | --- | --- | --- |
| ground | 0 | 1 | 0 m | 0 m |
| middle | 1 | 10 | 3.9632 m | 19.816 m (storey 5) |
| top | 11 | 1 | 43.5952 m | 43.5952 m |

The DOE reference draws a group of storeys at its lower middle storey, first + ⌊(N − 1)/2⌋. T1 checks those elevations against the generator's
parameters within 0.01 m. *Stacked Floor Zone Multiplier* represents a group at the storey D-045 chooses, first + ⌊N/2⌋, so it models the large
office's middle floor at storey 6 (23.779 m), one storey above the reference's. The two rules agree for an odd N and differ by one storey for an
even N; this is reported to the controller and left as D-045 decides.

## Windows (S6)

Where G1 applies, the plans take the record's source ceiling height as `GlazingReferenceHeight`: 2.7432 m (medium) and 2.744 m (large), so each
outdoor wall's window area is its WWR × length × that height. At another floor height the reference height keeps the source's share of the floor
height (2.7432 / 3.9624 for the medium office). A `GlazingReferenceHeight` set on the parameters is used as given. The small office's windows are
sized from its whole 3.05 m walls.

## Provenance

Every plan records `Record`, `LayoutRecord` (the record's name), `LayoutSources` (each source file with its role and SHA-256), `Gaps`, the size
parameters, `FloorHeight`, `OrientationDegrees`, `GlazingReferenceHeight` where set, the presets by key, `Storey`, `StoreyElevation`, and
`StoreyMultiplier` where it is not 1. The notices (the DOE credit and the openstudio-standards BSD-3 licence) stay with the records
([doe-layouts.md](doe-layouts.md#layout-records)).

## Acceptance (note §5)

`RingOfficeGeneratorTests` checks the three records at their defaults against their answer keys through the harness:

- T1: storey count, elevations (the reference's storeys, from the parameters), floor heights, storey multipliers, and outlines.
- T2: zones, program keys, floor areas, shared walls, outdoor and true outdoor walls per orientation.
- T3: conditioned area in total and per program key, 511.2, 4,982.2, and 42,757.25 m² above grade (D-161: the note's 46,320 m² includes the
  basement).
- T4: window area per zone and orientation, per program key, and in total, with each key's glazing from the answer key (`programGlazing`, the
  harness's per-key T4 inputs of P5a) as the program map's glazing. The offices' per-key ratios are their `officeGlazing` ratio of each
  orientation within the key's 1e-6 rounding, and no office zone's ratio differs from its key's. The atlas's WWR per orientation (A2) is missing,
  so the sourced-program part is a skipped test.
- T5: every size at 0.5×, 1×, and 2× and the storey count at its minimum and twice its default keep every storey's zones and adjacencies; a
  factor beyond its limit is `InvalidParameter`, and the limit, which keeps them, and a value just beyond it are tested instead (above).
- T7: *Perimeter Core* at the reference's own depth (5.0, 4.5733, and 4.5732 m) gives the reference's five zones per storey within 0.1 m².

`RingOfficeTypologyTests` runs T6: every simplifier and aggregator, canonical and at the test suite's two rotated placements, validates, with
the storey multipliers as the floor entries' multipliers.
