# DOE reference geometry generators (design note)

> **Status:** Done (accepted by the owner with PR #1, D-176; stage P7 added at the owner's request, D-171); merged into `main` (PR #1) and released in `v1.5.0` (D-175); decision entries D-160 (O4), D-161 (P0a), D-162 (P0b), D-163 (P5a), D-164 (P1), D-165 (P3), D-166 (P5b), D-167 (P6), D-168 (P2), D-169 (P4) · **Date:** 2026-10-25 · **Decisions:** D-009, D-026, D-061, D-097, D-111; [ADR-002](../decisions/ADR-002-geometry.md), [ADR-006](../decisions/ADR-006-plan-generation-mechanism.md), [ADR-011](../decisions/ADR-011-minimum-wall-and-window-geometry.md), [ADR-012](../decisions/ADR-012-centred-windows.md), [ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md), [ADR-015](../decisions/ADR-015-plans-per-storey.md); new: ADR-025 (ADR-024 is taken on `feature/reduced-order-5r1c`), ADR-026 (multiplied rooms), and one decision-log entry per phase · **Branch:** `feature/doe-geom` · **Issue:** Energy-Atlas/archetype-atlas#13
>
> **Evidence:** a read-only inspection on 2026-10-25 of the DOE commercial reference buildings (v1.4, EnergyPlus 7.2, all three vintages), the PNNL prototype buildings (ASHRAE 90.1-2004 to 2022, EnergyPlus 22.1), and the openstudio-standards detailed office geometry at `c8c1b9eb` (the commit the atlas pins). The figures below come from those files.

**Goal.** BEMGen can build the geometry of every non-apartment DOE commercial building type with a parametric plan
generator whose defaults reproduce the source plan, and whose parameters vary its size and its repeated units.
Geometry only: programs, schedules and constructions come from the atlas.

**Stop line.** Each phase ends with its branch built test-first, reviewed by a second agent, `scripts/verify.ps1`
green, and a decision-log entry (D-111). No merge, tag, push or release without the owner.

## 1. Decisions already made by the owner (2026-10-25)

| # | Decision |
| --- | --- |
| O1 | Geometry is one per type: not differentiated by vintage or by standard family. Checked: the reference vintages differ only in attics (G2) and school skylights (a program input). |
| O2 | Recorded gaps, not built in this stage: G1 plenums, G2 pitched attics, G3 basements, G4 zones taller than their storey, G5 storeys of different height in one multi-storey generator. |
| O3 | Window-to-wall ratio per orientation (N, E, S, W) and a skylight ratio are program data from the atlas, per zone type. Window shape is not reproduced. Glazed area per orientation is reproduced in total and per program key, and per zone where a key's zones share one ratio. (Wording corrected 2026-10-26, D-164: the owner's decision is the ratio per zone type; "glazed area per zone" went further than it.) |
| O4 | The DOE zone is the most detailed level of a DOE generator: D-097 is relaxed for these generators. |
| O5 | Zone multipliers inside a floor keep the DOE form: the repeated room is drawn once with its multiplier. |
| O6 | Offices take their room layout from the openstudio-standards detailed offices (a third source, kept distinct from the reference and prototype buildings), on the reference plates and elevations. |
| O7 | Only programs defined in the standards. Every detailed-office space type has a row in openstudio-standards `spc_typ.json` for both DOE reference templates; the atlas extracts them (A1). |
| O8 | Where reference and prototype geometry differ, the reference wins. After O1 and O3 the only case left is the large office stacking (x10 floor at 19.82 m, top at 43.6 m). The data-centre zones stay in the large office geometry (O1). |

## 2. Decisions settled while planning (the owner may overrule any)

| # | Decision | Why |
| --- | --- | --- |
| S1 | **One shared block, one generator per DOE layout family.** An internal `GridPlanLayout` in `Lod.Generators/Doe/` lays out a storey from x-cuts, y-cuts and zones given as unions of grid cells; eleven generators use it (§4). | Every DOE storey is axis-aligned and sits on a small grid (largest: outpatient ground floor, 32 x 30 cells; offices at most 21 x 12). ADR-006's pattern (typed records per family, a shared block like `StairBayLayout`) holds. |
| S2 | **Layouts are data, generated and pinned.** A script `scripts/doe-geometry/extract.py` (stdlib only, run with `python -I`, sources as arguments) reads the reference IDFs and the openstudio-standards OSMs as text and writes one layout record per type (`src/Lod.Generators/Doe/Layouts/<type>.json`, embedded resource) and one answer key per type (`tests/fixtures/doe/<type>.answer.json`), each with the source file's SHA-256. Only derived geometry is committed, never a source file; the openstudio-standards BSD-3 notice goes with the records derived from it, and the records derived from the reference buildings (a US government work, public domain, attribution requested) credit the DOE. | A 59-zone storey is not transcribed by hand into C#; the answer key makes exact reproduction testable without the source files on the test machine. |
| S3 | **Size and unit variation.** Each family names its parameters: fixed dimensions (perimeter depth, corridor width, room bay) keep their length; the remaining intervals are flexible and absorb a change of plate length or depth in proportion to their slack (default length minus 1 m), shrinking and growing alike, so that all reach 1 m at the shortest valid plate; an interval under 1 m has no slack and keeps its length; below the shortest plate is `InvalidParameter`. A fixed band a size parameter sets is at least 0.5 m. (Amended 2026-10-26, D-164; it first read "in proportion to their default length, each staying at least 1 m".) Families with repeated units expose a count (stores, guest-room bays, classroom wings); the default count reproduces the source. | "Exact plans, plus size and unit variations" with few, meaningful parameters. |
| S4 | **Program keys.** A DOE zone carries its standards space type as an explicit field (`ProgramKey`, for example `MediumOffice - OpenOffice`) next to its BEMGen `SpaceType`, which a fixed table maps (OpenOffice and ClosedOffice to `Office`, Corridor to `Corridor`, Stair to `Stair`, and so on; unmapped to `Other`). DOE generators take one program map keyed by `ProgramKey` instead of one input per space type; a missing key is `MissingPreset`. *Semantic Merge* groups by space type and program key. | Outpatient alone has dozens of zone types; one Grasshopper input each is unworkable. The key is data from the source, never parsed from a name (D-061). |
| S5 | **Windows and skylights.** `ProgramPreset` carries a WWR per orientation and a skylight ratio. A wall takes the WWR of the orientation it faces (sectors N [315, 45), E [45, 135), S [135, 225), W [225, 315) of true azimuth, after `OrientationDegrees`); a roof takes one centred skylight in the largest grid rectangle of the zone's roof, of area ratio x roof area. Every simplifier and aggregator conserves skylight area per zone and orientation as it conserves window area (ADR-012). | O3. |
| S6 | **Glazing reference height (G1).** Without plenums an office zone is one floor-to-floor high (3.96 m); its windows are sized from the wall area below the source ceiling height (2.74 m), so the window area per orientation equals the reference. Recorded in provenance. | The atlas WWR is relative to the conditioned zone's walls; applying it to 3.96 m walls would overstate glazing by 44 %. |
| S7 | **Gap conventions (G1-G5).** G1: zone height = floor-to-floor, plenum volume inside the zone. G2: flat roof at the zone top. G3: basements omitted; totals compare above grade. G4: tall zones take the storey height (gym 4 m, outpatient stairs one zone per storey, warehouse office 8.53 m and no fine-storage floor above it). G5: one floor height per multi-storey generator, the typical (upper) storey's. Each generator lists the gaps that apply to it in its documentation and provenance; acceptance tests exclude exactly those quantities. | O2. |
| S8 | **Multiplied rooms (phase P5).** A zone multiplier on a planned zone; its interior surfaces self-referencing (a new boundary `SelfAdjacent`, written as EnergyPlus `Surface` naming itself) or paired only with zones of the same multiplier, as in the source. *Semantic Merge* merges only zones of equal multiplier; *Perimeter Core*, *Single Zone per Floor* and the single-zone aggregators return `NotSupported` for a plan with room multipliers until a later decision. | O5; the source isolates multiplied rooms, and a merge across multipliers has no drawn geometry for the copies. |
| S9 | **Precedent generators unchanged.** The six non-residential `SYN-TYP` generators stay; the DOE generators are a separate set in panel *2 Generate*. Residential generators are not touched. | They realise precedent families (D-093), not DOE types; replacing them gains nothing. |
| S10 | **Data-centre program in the DOE reference vintages.** `OfficeLarge Data Center` is a row of `doe_ref_pre_1980` and `doe_ref_1980_2004` `spc_typ.json`, so A1 covers it. | O1, O7. |

## 3. Atlas inputs this stage needs

- **A1** Programs for the standards space types of the detailed offices: the `SmallOffice - *` and `MediumOffice - *`
  rows and the plain large-office rows, including `OfficeLarge Data Center` for the DOE reference templates.
- **A2** WWR per orientation and skylight ratio per program, in the program JSON BEMGen imports (`Lod.ProgramJson`
  today takes one WWR as an option, default 0.4).
- **A3** A program key in each program record equal to the standards space type, so S4's map resolves.

P0 and P1 can build and test with fixture programs before A1-A3 land; P1's acceptance T4 needs A2.

## 4. Families and phases

| Phase | Family (generator) | Records (default plans) | Source | Zones per storey | Parameters (size; units) | Gaps |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | `RingOffice` | small, medium, large | openstudio-standards detailed offices on reference plates | 17; 23/21/21; 26 (x10 middle floor) | plate length, depth, storeys, floor height, perimeter depth, corridor width; - | G1, G2 (small), G3 (large) |
| P2 | `Restaurant` | full-service, quick-service | reference | 2 | length, depth, kitchen depth | G2 |
| P2 | `StoreRow` | strip mall | reference | 10 | depth, large and small store width; store counts and order | - |
| P2 | `RetailBox` | stand-alone retail | reference | 5 | length, depth, back-space depth, front depth, entry width | - |
| P2 | `Supermarket` | supermarket | reference | 6 | length, depth, back-of-house depths | - |
| P2 | `Warehouse` | warehouse | reference | 3 | length, depth, office size, fine-storage depth | G4 |
| P3 | `School` | primary, secondary | reference | 25; 25/21 | plate, corridor width, classroom depth; classroom wing count | G4 (secondary) |
| P4 | `CorridorHotel` | small hotel | reference | 19/16/16/16 | length, room depth, corridor width, storeys; guest-room bays | G5 |
| P5 | multiplied rooms (S8) | - | - | - | - | - |
| P5 | `TowerHotel` | large hotel | reference | 7/7/7 (x4 floor, rooms x19) | length, depth, storeys; rooms per floor | G3, G5 |
| P5 | `Hospital` | hospital | reference | 9/11/13/13/8 | plate, corridor width; room multipliers | G3 |
| P6 | `Outpatient` | outpatient | reference | 59/37/22 | plate, corridor width | G4 |

P0 builds what every family needs:

1. ADR-025 *DOE reference geometry generators* (S1-S9) and a decision-log entry that refines D-097 for them (O4).
2. `GridPlanLayout`, the layout-record format and loader, and the S3 variation rule, with their own tests.
3. `scripts/doe-geometry/extract.py`, the records, and the answer keys for every type (all phases' data at once, so
   later phases only add generators).
4. `ProgramKey`, the space-type table, and the program-map input (S4).
5. Per-orientation WWR and skylight ratio in `ProgramPreset`, the program JSON importer, the window rule, a skylight
   rule, conservation in every simplifier and aggregator, and validation per orientation (S5, S6).
6. A comparison harness: a generated plan or building against an answer key, reporting every quantity of §5.

## 5. Acceptance tests

Every phase, for every record of its families, against its answer key (tolerances from ADR-004 unless stated):

| # | Check | Tolerance |
| --- | --- | --- |
| T1 | Plate outline per storey, storey count, elevations and floor heights equal the source, apart from the recorded gaps | +-0.01 m |
| T2 | Per storey: zone count, each zone's program key, floor area, the walls each pair of zones shares and their lengths, outdoor wall length per orientation per zone | areas +-0.1 m2, lengths +-0.05 m |
| T3 | Conditioned floor area in total and per program key | +-0.1 % |
| T4 | Window area per orientation and skylight area equal the source, with the source's WWR and skylight ratio as program inputs | +-1 % |
| T5 | Variation: every parameter at 0.5x, 1x, 2x of its default and every count at its minimum and twice its default gives a valid plan that keeps the zone topology (same zones, same adjacencies); values below the limits are `InvalidParameter` | - |
| T6 | Every simplifier x aggregator combination validates, canonical and at the test suite's rotated placements (as S8.x); determinism and snapshots | as today |

Phase-specific:

- **P1** (exact figures from the sources):
  - conditioned area 511.2, 4,982.2 and 46,320 m2 above grade (the large office's 3,563 m2 basement is G3);
  - zones per storey: small 17; medium 23 ground, 21 middle, 21 top; large 26 per storey;
  - reference elevations: medium storeys at 0, 3.96, 7.92 m; large at 0, 19.82 (x10), 43.6 m;
  - **T7, the DOE reference as one rung of the ladder:** *Perimeter Core* at 5.0 m (small) and 4.57 m (medium,
    large) on the room plan gives the reference's five zones per storey with its areas:

    | Office | Core | Long sides | Short sides |
    | --- | --- | --- | --- |
    | small | 149.66 | 113.45 each | 67.30 each |
    | medium | 983.54 | 207.34 each | 131.26 each |
    | large | 2,532.32 | 313.42 each | 201.97 each |

    Tolerance +-0.1 m2; areas in m2.
  - window area per orientation:

    | Office | N | E | S | W |
    | --- | --- | --- | --- | --- |
    | small | 16.7 | 11.2 | 20.6 | 11.2 |
    | medium | 195.8 | 130.6 | 195.8 | 130.6 |
    | large | 1,390.8 | 927.2 | 1,390.8 | 927.2 |

    Areas in m2. The medium and large offices take S6's 2.74 m glazing reference height.
- **P5:** a building with room multipliers counts each zone x multiplier in every total; *Semantic Merge* never
  merges zones of different multipliers; the S8 `NotSupported` cases are tested.

## 6. Stages, workload, and deliverables

P0 of §4 is split into P0a (data and layout) and P0b (glazing), and P5 into P5a (core) and P5b (generators), so that
each stage is one reviewable build. Workload is an estimate from the S8.4–S8.7 pace (four generator sub-stages built
unsupervised on 2026-10-02) and the code each stage touches: production lines (C# unless stated), new tests, and
agent hours of build, review and fixes. Size: S under 3 h, M 3–5 h, L over 5 h.

| Stage | Scope | Deliverables | Prod. lines | Tests | Hours | Size | Needs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P0a | Data and layout foundation | ADR-025; decision entry refining D-097 (O4); `GridPlanLayout`, record format and loader, S3 variation rule; `scripts/doe-geometry/extract.py` (Python, about 700 lines); 14 layout records and 14 answer keys (every type, so later stages only add generators); `ProgramKey` on planned and generated zones, the space-type table, a program-map preset record; the comparison harness | 1,500 | 120 | 6–8 | L | – |
| P0b | Glazing per orientation and skylights | `ProgramPreset` with WWR per orientation and a skylight ratio, a scalar WWR still meaning all four (existing snapshots byte-identical); program JSON import of both (a fixture format until A2); window rule by facing; S6 glazing reference height; skylight rule; conservation in *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor* and both single-zone aggregators; validation per orientation including skylights; skylights in *Convert2BEM* and *Convert2IDF*; preset component inputs | 1,200 changed across about 15 files | 100 | 6–8 | L | – |
| P1 | Offices | `RingOffice` generator, small, medium and large records, component, icon; T1–T7 | 400 | 70 | 3–4 | M | P0a, P0b |
| P2 | Single-storey types | `Restaurant`, `StoreRow`, `RetailBox`, `Supermarket`, `Warehouse` generators, six records, five components and icons | 1,000 | 150 | 5–6 | L | P0a, P0b |
| P3 | Schools | `School` generator (one plan per storey), primary and secondary records, wing-count variation, component, icon | 500 | 60 | 3–4 | M | P0a, P0b |
| P4 | Small hotel | `CorridorHotel` generator (ground storey differs), guest-room bay variation, component, icon | 350 | 45 | 2–3 | S | P0a, P0b |
| P5a | Multiplied rooms | ADR-026; multiplier on planned zones; `SelfAdjacent` boundary through surfaces, validation, *Convert2BEM*, *Convert2IDF*; *Semantic Merge* equal-multiplier rule; `NotSupported` in the other merging steps (S8) | 800 | 80 | 5–6 | L | P0a |
| P5b | Large hotel and hospital | `TowerHotel` and `Hospital` generators, records, components, icons | 600 | 90 | 4–5 | M | P5a, P0b |
| P6 | Outpatient | `Outpatient` generator (59/37/22 zones), record, component, icon | 350 | 50 | 3 | M | P0a, P0b |
| C | Close-out | `sync-docs` skill pass; README, roadmap, AGENTS.md; developer docs of every family; headless Rhino check of every new component; final `scripts/verify.ps1`; owner report | docs | – | 2–3 | S | all |
| | **Total** | 11 generators, 14 records, 2 ADRs, about 10 decision entries | **about 6,700 + 700 Python** | **about 765** | **40–50** | | |

**Order.** P0a and P0b run in parallel; `ProgramPreset` belongs to P0b, `PlannedZone` and `Zone` to P0a. After both, P1,
P2, P3, P4 and P6 are independent: each touches only its own `Lod.Generators/Doe/<Family>/` folder, its own test
folder, and its own component file `Lod.Grasshopper/Components/Doe<Family>Components.cs`. At most three of them run
at once, in priority order P1, P2, P3, P4, P6. P5a can run beside them, since it touches `Lod.Core` and the exporters
only; P5b follows P5a. C is last.

**Shared files.** Stages do not edit the decision log, the roadmap, README, AGENTS.md or `scripts/make_icons.py`.
Each stage states its decision entry text and its icon motifs in its final report; the controller applies them one
stage at a time when it merges.

## 7. Autonomous execution

The owner asked for all stages to run without supervision. They run as D-111 and D-098 set out, with these rules.

**Roles.**

- **Controller:** one session. It dispatches, checks, merges and reports; it writes no production code.
- **Builders:** one fresh agent per stage. `bemgen-complex` builds P0a, P0b, P1–P4, P5a, P5b and P6; `bemgen-bounded`
  writes the ADR and log text and the close-out C.
- **Reviewer:** a second fresh agent of the same type, given the diff and this note, not the builder's summary.

**Per stage.**

1. Cut `feature/doe-geom-<stage>` from the tip of `feature/doe-geom`, in its own worktree.
2. Build test-first from this note.
3. Review, fix every finding, and review again until nothing is open.
4. Run `scripts/verify.ps1`, and `scripts/rhino-smoke` when components changed.
5. The controller merges into `feature/doe-geom` with `--no-ff`, then adds the decision entry (D-160 onward,
   Provisional, pending the owner's reading) and a roadmap progress line.
6. Remove the stage worktree, and report to the owner: what landed, test counts, deviations, the ETA for the rest.

**Routine choices** are the controller's, as D-098 allows: names, IDs, file layout, minor parameter limits, test
fixtures. Each is recorded in the stage's decision entry, and all of them are listed in the final report.

**Stop and report, without working around it,** when:

- the same kind of failure happens three times;
- a change would relax a tolerance or a check, or change an existing snapshot beyond what the stage documents;
- a source fact contradicts this note, such as an area outside tolerance that G1–G5 do not explain;
- O1–O8 would have to change;
- `scripts/verify.ps1` fails on `feature/doe-geom` after a merge.

**Continue instead of stopping** when an atlas input (A1–A3) is missing: use fixture programs, mark the affected test
pending (T4 of P1), and list it in the report.

**Limits.** No push, no merge into `main`, no tag, no release. No change to the archetype-atlas repository, the
residential generators, or the six precedent generators. Nothing is deleted outside the stage's own branch and
worktree.

**End state.** `feature/doe-geom` holds every stage, verified, with its decision entries. The owner's final report
lists the Provisional decisions and pending tests, and the commands to push and to open the pull request.

## 8. Not in this stage

G1-G5; apartments; window shape (strips, punched counts, sill heights); interior shading, doors; the prototype
buildings as a geometry source (O8); choosing programs per vintage (atlas).

## 9. Stage P7: DOE program-map presets (owner request, 2026-10-26)

The owner accepts the program map (S4) as the current design and asks for a ready preset for every DOE plan
generator, so that each can be used and tested without assembling a map by hand.

- **Components.** One output-only component per record (15), in panel *1 Program Presets* beside the built-in
  presets, named with the *DOE* prefix like the generators (for example *DOE Small Office Programs*). Outputs: the
  *Program Map* for that record's generator, and its *Keys* and *Presets* lists, so a user can edit a preset and
  rebuild the map with *DOE Program Map*. Thin adaptors over a domain service in `Lod.Generators/Doe/`.
- **Values (owner's choice).** Each key takes the illustrative example preset of its BEMGen space type
  (`DoeSpaceTypes`; the built-in example presets, D-023), named by its key, with the source's own window-to-wall
  ratio per orientation and skylight ratio for that key (the extraction's per-key glazing on the true-outdoor-wall
  basis, D-162, D-163). Loads stay illustrative and are replaced when the atlas inputs A1 and A2 land. A key whose
  space type has no example preset takes a stated fallback, recorded in provenance.
- **Acceptance.** For every record: the map covers exactly the generator's program keys; the generator at its
  defaults with its DOE preset validates and passes T4 (window and skylight area per orientation, in total and per
  key, within 1 %) through the shipped presets, not test fixtures; every simplifier × aggregator the generator
  supports validates; a headless Rhino spec wires each generator to its DOE preset. Existing snapshots, icons, and
  GUIDs unchanged; new icons for the 15 components.
