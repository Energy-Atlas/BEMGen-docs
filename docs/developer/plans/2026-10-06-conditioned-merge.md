# Conditioned Merge, and joined pieces for both merge simplifiers (design note)

> **Status:** Done (D-123; released in version 1.1.0, D-125) · **Date:** 2026-10-06 · **Decisions:** D-034, D-038, D-041, D-047, D-064, D-079, D-111, D-123 · **Branch:** `feature/conditioned-merge`

A revision stage run as D-111 sets out:
- one test-first build on the branch in the worktree `D:\worktrees\conditioned-merge`;
- a review by a second agent;
- the headless Rhino check, once;
- `scripts/verify.ps1` before the merge;
- one decision-log entry.

The branch starts from `main` (`af9ac65`), independent of the unmerged S10 branch. Its decision is numbered D-123 so that the two branches do not collide; whichever merges second rebases its log entry.

## Problem

The plan simplifiers trade detail for zone count in fixed steps:
- *No Simplification* (Z0) keeps every zone.
- *Semantic Merge* (Z1) merges zones of one space type that share walls.
- *Perimeter Core* (Z2) makes orientation bands and a core.
- *Single Zone per Floor* (Z3) makes one zone.

No step removes the semantic partitions inside conditioned space while keeping the boundary between conditioned and unconditioned space. Z2 and Z3 enlarge the conditioned floor area whenever they cover an unconditioned zone.

The owner asked for two changes:

1. **A new simplifier, *Conditioned Merge*.** It merges the conditioned zones of a floor and, separately, the unconditioned ones.
2. **A choice of how separate pieces are treated, on both merge simplifiers.** A class's zones often form several pieces that share no wall: the stairs of a floor are usually several separate cores, and the stair bays of a *Stair Bay Bar* cut its dwellings into blocks. A boolean, *Join Pieces*, decides how these pieces are zoned:
   - **false** (the default) gives one zone per connected piece. This is today's *Semantic Merge* behaviour.
   - **true** gives one zone per class on the floor, made of all its pieces.

| Simplifier | Class | *Join Pieces* false (default) | *Join Pieces* true |
| --- | --- | --- | --- |
| *Semantic Merge* | space type | one zone per connected piece of each type (unchanged) | one zone per space type on the floor |
| *Conditioned Merge* | conditioned / unconditioned | one zone per connected piece of each class | at most two zones on the floor |

On the tested plans with the example presets, where only *Stair* is unconditioned:

| Plan | *Semantic Merge* false | *Semantic Merge* true | *Conditioned Merge* false | *Conditioned Merge* true |
| --- | --- | --- | --- | --- |
| Linear plan | `Stair-1`, `Corridor-1`, `DwellingUnit-1`, `DwellingUnit-2` | `Stair-1`, `Corridor-1`, `DwellingUnit-1` (2 pieces) | `Conditioned-1`, `Unconditioned-1` | the same 2 |
| Stair Bay Bar | 4 dwelling and 3 stair zones | `Stair-1` (3 pieces), `DwellingUnit-1` (4 pieces) | 4 conditioned and 3 unconditioned zones | `Conditioned-1` (4 pieces), `Unconditioned-1` (3 pieces) |

The names and orders are those that `SimplifierTests` and `MergeSimplifierFamilyTests` check.

## Decisions

1. **What "conditioned" means.** A source zone is conditioned when its program has a thermostat (`ZoneProgram.IsConditioned`). That comes from its preset (D-038). No other property decides it, such as the space type, the name, or the setpoint values.
2. **Connected means sharing a wall,** as *Semantic Merge* defines it today: an interzone wall between the two zones. Zones that touch only at a point are not connected.
3. **Zones made of several pieces.** With *Join Pieces* true, a zone may have several disjoint pieces on one storey. EnergyPlus accepts this, because a zone is a set of surfaces. It needs a small extension of the floor model. `Zone.Parts` already holds several parts for the building-level single-zone aggregators, but the floor-level code reads only `Parts[0]`. The changes:
   - `TargetZone` holds one or more polygons.
   - `LayoutSurfaceBuilder` builds the walls of every piece under the zone's ID. Two pieces never share a wall, or they would be one piece.
   - `PlanSimplifier` makes one `ZonePart` per piece and sums the zone's measures over them.
   - `Storeys` (floors and ceilings between storeys), `SingleZoneMerge`, the floor validators, and the floor and storey previews read every part.

   With *Join Pieces* false, every simplifier still makes single-piece zones. No existing result, snapshot, or test may change, and that is the acceptance check for the extension.
4. **Target zones.** Each zone is numbered `{Class}-{n}` in plan order of its first source zone, the same scheme as *Semantic Merge*.
   - *Semantic Merge* names zones by space type: `DwellingUnit-1`, `Stair-1`.
   - *Conditioned Merge* names them `Conditioned-n` first, then `Unconditioned-n`. With *Join Pieces* true that is `Conditioned-1` and `Unconditioned-1`.
   - A class with no source zone gives no zone, so a floor without stairs gets one conditioned zone. That is the shape of *Single Zone per Floor*, with no conditioned area added.
   - A *Conditioned Merge* zone takes the space type its sources share, or `Mixed` when they differ. For example, an unconditioned zone made only of stairs is `Stair`.
   - Each piece's footprint is the union of its sources as tiles (`PolygonOps.UnionTiles`), which keeps their vertices. A piece may have holes.
5. **Aggregation is unchanged** (ADR-005, ADR-007, D-047). Installed and per-timestep scheduled loads, occupancy, and air flows are conserved per target.
   - A conditioned target's setpoints are floor-area weighted over conditioned sources only.
   - An unconditioned target has no thermostat, and its loads stay in it.
   - **Conditioned floor area is conserved exactly by *Conditioned Merge*, in both modes.** This is its defining invariant. Validation already reports a change of conditioned area, and for this method it must report none.
6. **Geometry rules are unchanged.** Walls between targets stay `Interzone`, and walls inside a target disappear (D-034). The target façades must cover every source façade (D-041). Every rebuilt outdoor wall gets one centred window with the glazed area it covers (D-079).
7. **Parameters and provenance.**
   - *Join Pieces* is a property of the simplifier, passed to its constructor; it is never inferred.
   - Provenance records `JoinPieces=true` only when it is true. That keeps every existing *Semantic Merge* output byte-identical, the same pattern as non-default `GeometryLimits`. *Conditioned Merge* follows the same rule.
8. **Grasshopper.**
   - *Semantic Merge* gains the input *Join Pieces* (J, boolean, default false) before *Preview Location*. Its GUID does not change; D-064 allows changing inputs.
   - *Conditioned Merge* goes in panel *3 Simplify*, after *Semantic Merge*, with a new GUID, the inputs *Plan*, *Join Pieces*, and *Preview Location*, the output *Floor*, and a new icon motif.
   - No existing GUID changes.
9. **Research placement.** In the research brief §8, *Join Pieces* is a variant within Z1, and *Conditioned Merge* is Z1c, "conditioning merge": a merge by a known semantic relationship, conditioning, rather than by space type. Neither is a new level number. Its invariant goes into the table of what each level conserves (GLOBAL.md scientific rule 7).
10. **Out of scope.** A vertical (building-level) counterpart, and changes to the example definitions.

## Tests (written first)

- **`Lod.Core.Tests`, the model extension.** A floor zone with two parts at one elevation:
  - its area, volume, and exterior wall area are summed over the parts;
  - the floor validator's overlap and coverage checks handle it;
  - `Storeys` gives each part its floor and ceiling, split by the storeys above and below;
  - `SingleZoneMerge` unites all its parts.
- **`Lod.Core.Tests`, both simplifiers in both modes.**
  - **Classification:** only the thermostat decides (*Conditioned Merge*); class order and numbering.
  - **Pieces:**
    - separate pieces with *Join Pieces* false and joined with true;
    - an all-conditioned floor, and an all-unconditioned floor;
    - a shared space type is kept, otherwise `Mixed`;
    - a piece with a hole;
    - pieces that meet only at a point.
  - **Conservation:**
    - conditioned floor area is exact for *Conditioned Merge*;
    - loads, schedules, and occupancy are conserved per target;
    - setpoints come from conditioned sources only, and the unconditioned target has no thermostat.
  - **Walls and windows:** interzone walls between targets; centred windows with the glazed area conserved per wall and façade.
  - **Provenance and mapping:** `JoinPieces` is recorded only when true, and the mapping lists every source with its fraction.
  - **Determinism:** the same result whatever the order of the source zones.
- **`Lod.Integration.Tests`.**
  - Add `ConditionedMerge` and the `true` modes (`SemanticMerge:JoinPieces`, `ConditionedMerge:JoinPieces`) to every family's simplifier set. Every family × every aggregator must validate with the existing conservation checks.
  - The existing `SemanticMergeJoinsOnlyConnectedZonesOfOneType` expectations stay as they are, and new rows give the joined results.
  - One snapshot per new mode for the linear plan.
- **`Lod.Export.Tests`.**
  - A joined *Conditioned Merge* building through `Convert2Idf`: the multi-part zones are written as one `Zone` with every piece's surfaces, the interzone walls are paired, and the IDF parses back.
  - One IDF snapshot.
- **Headless Rhino.**
  - `linear-and-aggregators` adds *Conditioned Merge* and *Join Pieces* true to its every-simplifier scenarios.
  - A stair-bay-bar scenario checks the multi-piece zones in the floor preview and through *Convert2BEM* (one Brep per part) and *Convert2IDF*.
  - Icons are checked as usual.

## Documentation

- `pipeline.md` (step 3, the component table), `domain-model.md` (floor zones with several parts at one elevation), `validation.md` (the conditioned-area invariant), and `convert2bem.md` and `convert2idf.md` where the multi-part floor zones need a note.
- The research brief §8.
- The smoke checklist.
- `AGENTS.md` and the README, only where they list the simplifiers.
- D-123, and `sync-docs` at the close-out.

## Acceptance criteria

- Every new test passes and `scripts/verify.ps1` passes. With *Join Pieces* false, every existing snapshot and test is unchanged.
- On every family with the example presets, *Conditioned Merge* with *Join Pieces* true gives at most two zones per floor. In both modes it conserves conditioned floor area exactly, and every mode validates with every aggregator.
- The headless Rhino specs pass. No component GUID changes.

## Task list

1. The floor-model extension for multi-part floor zones, test-first. Every existing test stays unchanged.
2. *Join Pieces* on `SemanticMerge`, and the new `ConditionedMerge`, test-first.
3. The integration and export tests.
4. The components, the icon, and the smoke scenarios.
5. A review by a second agent, then fixes.
6. The docs (with the research brief), D-123, verify, the headless Rhino check, and `sync-docs`.

## Outcome

The build followed the decisions above. Where the code settled something the note did not say:

- **Determinism holds up to numbering.** Targets are numbered in plan order of their first source zone (decision 4), so reordering the source zones can renumber the separate pieces of a class. Each target's sources, class, area, and part count stay the same, and with joined pieces so do the names (`ReorderingTheSourceZonesGivesTheSameTargetsUpToTheirNumbering`).
- **Two diagnostic codes are new.** `TouchingPieces` is the error for two pieces of one zone that share an edge, reported once per edge by `LayoutSurfaceBuilder`. `DuplicateZoneId` is the error for two target zones, or two zones of a layout, with one ID, because the surface builder would read them as one zone of several pieces; `PlanSimplifier` and `PlanBuilder` raise it.
- **A target with no pieces is `InvalidParameter`.**
- **Pieces are named `F1`/`C1`.** A zone of several pieces has its walls numbered on across the pieces and one floor and one ceiling per piece, `F1`, `F2`, … and `C1`, `C2`, …; a zone of one piece keeps `F` and `C` until floors are stacked. `Storeys` numbers the floor pieces of a kind on across a zone's parts.
- **Previews draw one solid per same-storey piece.** Uniting the pieces of a zone fused pieces that meet at a corner into one solid, which the headless run found; the pieces of one storey are never united. Zones that span storeys keep the merged preview of D-071.
- **Old two-input *Semantic Merge* files are read with *Join Pieces* at its default.** Grasshopper restores inputs by position, so the saved *Preview Location* would otherwise be read into *Join Pieces* and the component would give no output.
- **The stair-bay-bar floor snapshot replaces the linear joined one.** The linear plan has one piece per class, so joined *Conditioned Merge* gives there the floor that separate pieces give; the snapshot of the Stair Bay Bar shows the multi-piece zones. The IDF snapshot is of the same building.
