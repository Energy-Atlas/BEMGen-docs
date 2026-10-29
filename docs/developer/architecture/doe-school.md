# DOE school generator

> **Status:** Provisional (stage P3 of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md), pending the owner's reading) · **Code:** `src/Lod.Generators/Doe/School/` · **Tests:** `tests/Lod.Generators.Tests/Doe/School/` · **Components:** `src/Lod.Grasshopper/Components/DoeSchoolComponents.cs` · **Smoke spec:** `scripts/rhino-smoke/specs/doe-schools.py` · **Records:** `primary-school`, `secondary-school` ([DOE layout records](doe-layouts.md))

`SchoolGenerator` builds the DOE primary school (one storey of 25 zones) and secondary school (two storeys of 25 and 21 zones) from their layout
records, one plan per storey through `MultiStoreyPlanGenerator` ([ADR-015](../decisions/ADR-015-plans-per-storey.md)) and `GridPlanLayout`
([ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md), S1). At its defaults every storey is the record's storey through
`GridPlanLayout`, vertex for vertex. Geometry only: each zone's program comes from a `DoeProgramMap` by its program key (S4).

## Structure

Both schools are a row of classroom wings (the source's pods) west of a spine of shared rooms. `SchoolTemplate` finds the structure from the
record's cells and program keys, never from a zone name (D-061):

- a **wing corridor** is a zone whose key maps to `Corridor` and that starts at the grid's west edge; its **classroom rows** are the rows on either
  side of it whose west cell is in a zone, up to an empty cell or the grid's edge;
- the wings span the columns west of the corridors' east edge; every zone there lies in one wing, and every cell there outside the wings is empty
  (the courts between wings, open to the west);
- every other zone is the **spine**: lobby, offices, main corridor, gym, kitchen, cafeteria, and the rest.

Each school has three wings of a 9 m classroom row, a corridor (3 m primary, 5 m secondary), and a 9 m classroom row; the courts between them are
9 and 10 m (primary) and 17 and 18 m (secondary). A school needs at least three wings (a first, a middle, and a last). Every storey of the
secondary school has the same grid and the same wings, and every cell of its first floor lies over a cell of the ground storey, so storey 1 stands
on storey 0. A record that is not of this form fails to load with an `InvalidDataException` naming the reason. The record is analysed with the
generator's tolerances.

## Parameters

`SchoolParameters(Type, WingCount, Length, CorridorWidth, ClassroomDepth, FloorHeight, OrientationDegrees)`; `SchoolParameters.For(type)` reads the
defaults from the record (`Primary`, `Secondary`; `Default` is the primary school).

| Parameter | Primary | Secondary | Rule |
| --- | --- | --- | --- |
| `WingCount` | 3 | 3 | at least 2 (`MinimumWingCount`) |
| `Length` | 104 m | 141 m | plan x of every storey (S3 as amended, D-164): the main corridor's column (13 m, 15 m) keeps its width, every other column shares the change by slack (its length less 1 m); at least 18 m (primary) or 19 m (secondary) |
| `CorridorWidth` | 3 m | 5 m | every wing's corridor; at least `GridAxis.MinimumFixedBand`, 0.5 m |
| `ClassroomDepth` | 9 m | 9 m | every classroom row of every wing; at least 0.5 m, and a row holding the spine's cuts at least 1 m per interval between them: 2 m in the secondary school at every count; 2 m in the primary school from three wings up, 0.5 m at two wings (no middle wing, and its end-wing rows hold no spine cut) |
| `FloorHeight` | 4 m | 4 m | every storey, positive; storey *k* stands at *k* × `FloorHeight` |

**Valid ranges** (at the other defaults; no parameter has an upper limit):

| Parameter | Primary | Secondary | Why the lower limit |
| --- | --- | --- | --- |
| `Length` | ≥ 18 m (−83 %) | ≥ 19 m (−87 %) | the main corridor's column and 1 m per other column |
| `CorridorWidth` | ≥ 0.5 m (−83 %) | ≥ 0.5 m (−90 %) | `MinimumFixedBand` |
| `ClassroomDepth` | ≥ 2 m (−78 %) from three wings, ≥ 0.5 m at two | ≥ 2 m (−78 %) at every count | the primary school's middle-wing rows 30–38–39 and 42–46–51 m (only with a middle wing), the secondary school's last-wing row 95–101–104 m, each holding a spine cut; else `MinimumFixedBand` |
| `FloorHeight` | > 0 | > 0 | positive |
| `WingCount` | ≥ 2 | ≥ 2 | the source's first and last wing |

Every size parameter reaches ±20 % of its default; 0.5×, 1×, and 2× are all valid.

There is no plate-depth parameter: the depth follows from the wings (two classroom rows and a corridor each) and the source's courts, as a strip
mall's length follows from its stores. Courts keep their depth.

**Wings.** `WingAxis` lays out `WingCount` wings south to north: the source's first wing, then the source's middle wing with the court that follows
it, repeated, then the source's last wing. Two wings are the first and the last with the first court between them; three are the source; six are
the first, the middle four times, and the last. A wing's zones use its row edges only, so they take the new row depths exactly; the spine's cuts inside a row move by slack (S3, below). A repeated
wing's zones keep the source's IDs at the first use of the source wing and take the suffix `_Wing{n}` after it, `n` the wing's place from 1 south
(`Corridor_Pod_2_ZN_1_FLR_1_Wing4`), with names `… (wing 4)`. The last wing keeps the source's last wing's IDs (`…_Pod_3_…`) at any count.

**Spine.** The spine's cuts move by the S3 rule of `GridAxis` (D-164). Within a row of the first or the last wing, the spine's cuts inside that
row share the row's change by slack; in the first and the last court they keep their place. Inside the source's middle wing each row does the same
at the new sizes, and then the spine's cuts along the middle wing share, by slack, the stretch to the span of every middle wing and the courts
between them. So a spine zone that reaches a middle wing's edge in the source reaches the same edge of the last copy: in the primary school at six
wings the main corridor runs from 9 m to the last middle wing's north edge at 144 m, the gym, kitchen, and cafeteria share the stretch
(30–38–46–51 m becomes 30–74.17–118.33–144 m), and the bathroom that faces the last court keeps its 10 m (190 m²); in the secondary school the
mechanical rooms and the kitchen keep their 9 m in the last court, so the first floor's mechanical room still joins the main corridor to the
library. Every wing therefore adjoins the spine zones its source wing adjoins, zone by zone: the first wing the lobby and the main corridor, every
middle wing the main corridor, the last wing the library (primary) or the main corridor and the bathrooms (secondary). With two wings there is no
middle wing and one court: the spine's cuts of the source's whole middle are resized onto that court by slack (the primary school's 21–38–46–51–61 m
becomes 21–24.22–26.19–27.75–30 m). At the source's count nothing is stretched, so every size parameter keeps the zones and all their
adjacencies. A row or span shorter than 1 m per interval of the spine's cuts in it is `InvalidParameter`, which sets the classroom-depth limit.

Coordinates that come out within the distance tolerance of one another are one cut of the grid, so no sliver interval is made.

## Gaps and provenance

- **G4** (secondary school): the gym, the auxiliary gym, and the auditorium are 8 m high in the source; they take the 4 m storey height and are
  drawn on the ground storey only. The first floor's walls that stand against them are outdoor walls here (D-162). No other gap applies.
- Provenance: `Record` (`primary-school`, `secondary-school`), `WingCount`, `Length`, `CorridorWidth`, `ClassroomDepth`, `Gaps` (`none`, `G4`),
  with the parameters, `Storey`, and `StoreyElevation` every multi-storey generator records.

## Programs and glazing

`SchoolGenerator.ProgramKeys(type)` lists the keys a school's map needs: `Cafeteria`, `Classroom`, `Corridor`, `Gym`, `Kitchen`, `Lobby`,
`Mechanical`, `Office`, `Restroom`, and for the secondary school also `Auditorium`, `Gym - audience`, and `Library`. A zone whose key has no preset
is `MissingPreset`. Windows and skylights come from each key's preset (S5); the primary school's gym takes one centred skylight of the source's
area, where the source has nine.

## Acceptance (design note §5)

All through the harness of [DOE layout records](doe-layouts.md), with the tolerances of `ToleranceSettings.Acceptance`:

- **T1–T3**: both records pass at the defaults; the elevations and floor heights are the generator's (k × `FloorHeight`) and equal the source's.
- **T4**: on the generators' path (D-163), one program per key from the answer key's per-key glazing (`programGlazing`, through the harness's
  `KeyGlazing`), as the atlas will give them (A2; fixture programs until then). Window area per orientation in total and per program key within
  1 %; per zone too, since no zone of either school differs from its key's ratio (`glazingRatioDifferences` is empty). Every zone, orientation, and total passes, the primary school's
  13.38 m² of skylights per zone and in total included. Excluded by G4: the secondary school's three tall zones and the first-floor walls against
  them (the answer key's `gapOrientations`).
- **T5**: `Length`, `CorridorWidth`, `ClassroomDepth`, and `FloorHeight` at 0.5×, 1×, and 2×, and the first three at their limits, keep every
  storey's zones and adjacencies, and just below their limits are `InvalidParameter`;
  `WingCount` 2 and 6 keep every wing's zones and inner adjacencies, every wing zone's links to the spine zones its source zone adjoins (pinned
  per wing from the sources), no link between wings, and the spine's zones and adjacencies; the secondary school's storeys stack into a valid
  building at 2 and 6 wings and at every size variation, storey 1 standing on storey 0; values below the limits are `InvalidParameter`.
- **T6**: every simplifier × aggregator validates, canonical and at the two rotated and translated placements; determinism and snapshots
  (`primary-school-canonical`, `secondary-school-canonical`).

**Perimeter Core.** The secondary school's first floor has a part 9 m wide, the mechanical room between the main corridor's column and the
library, so *Perimeter Core* at the suites' 4.57 m is `PlanTooNarrow` there (D-087); the T6 matrix runs it at 4 m on the secondary school and
at 4.57 m on the primary school.

## Grasshopper components

One component per record, as for the offices, on the `DoeGeneratorComponent` base ([DOE generator components](doe-components.md)), so each
input shows its record's default. Inputs in the DOE order: *Wing Count* (W), *Length* (L), *Corridor Width* (CW), *Classroom Depth* (CD), *Floor
Height* (FH), *Orientation* (O), *Program Map* (Map), *Preview Location*; the counts and sizes are optional and keep their record's default when
unconnected. Outputs *Plan* (one plan per storey), *Multipliers* (1 for every storey), and *Program Keys*.

| Component (nickname) | Defaults | Program keys | GUID |
| --- | --- | --- | --- |
| *DOE Primary School* (DoePSch) | 3 wings, 104 m, 3 m, 9 m, 4 m, 0° | 9 | `4f67ab4c-7c7e-4a27-afbe-8e76cd48097d` |
| *DOE Secondary School* (DoeSSch) | 3 wings, 141 m, 5 m, 9 m, 4 m, 0° | 12 | `913bc6e4-ba40-4f81-949d-fc7d616ee1db` |

Presets come through *DOE Program Map*: wire a first copy's *Program Keys* into its *Keys* and the presets, or one any-program preset for every
key, into *Presets*. *Perimeter Core* at its 4.57 m default is `PlanTooNarrow` on the secondary school's first floor; give it a depth below 4.5 m.
Each component has its icon, drawn in the close-out by `scripts/make_icons.py`: three parallel wings joined by one tall spine block, and for the secondary school the outline of a second, smaller storey over the spine ([doe-components.md](doe-components.md#icons)).
