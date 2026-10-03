# S5 — Centred windows on rebuilt walls Implementation Plan

> **Status:** Done (controller, D-080; pending the owner's reading) · **Date:** 2026-10-01 · **Roadmap:** [S5](2026-09-30-implementation-roadmap.md#s5--centred-windows-on-rebuilt-walls) · **Decisions:** D-026, D-039, D-041, D-079, D-080; [ADR-012](../decisions/ADR-012-centred-windows.md) (Task 1)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement D-079: wherever zones are merged and walls are rebuilt (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, *Single Zone Building*), every outdoor wall of a target zone carries exactly one window, centred on it and shaped by the generator's rule (D-026), whose area is the total glazed area of the source windows that wall covers; a wall without glazing gets none. Glazed area is conserved per wall, and so per façade, orientation, and building; every area, load, boundary, and validation report stays unchanged. The window levels W1–W5 are dropped from the research brief and the roadmap. S5 ends with version 0.5.0, the local tag `v0.5.0`, and, after a fresh clone of the tag passes the gate, the push of `main`, `v0.4.2`, and `v0.5.0` (D-080).

**Architecture:** One shared step in `Lod.Core.Simplification`, `CentredWindows.Place`, attributes every source window to the rebuilt outdoor wall that contains it (the existing `WindowRehosting.Rehost`, D-039) and then replaces the windows of each rebuilt outdoor wall by one window from `Window.Centered` (the S2 generator's rule) with the summed glazed area. A window that no single target wall contains stays the error `WindowNotHosted`; a wall whose glazed area is not smaller than its area is the new error `GlazingExceedsWall`. Both are guards that hold by construction for the current zoning strategies. The shared simplifier pipeline `PlanSimplifier` and the single-zone merge `SingleZoneMerge` call `CentredWindows.Place` where they called `WindowRehosting.Rehost`. *No Simplification*, *Stack Floors*, and *Stacked Floor Zone Multiplier* do not rebuild walls and keep their input's windows. In `Lod.Grasshopper` only component descriptions change.

**Tech Stack:** C# 12 (`LangVersion` 12.0); .NET SDK ≥ 8 (`global.json` pins 8.0.100 with `rollForward: latestMajor`); `netstandard2.0` core libraries; Clipper2 2.0.0; RhinoCommon and Grasshopper 8.19.25132.1001 (plugin targets `net7.0`); xUnit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1 (tests target `net8.0`); Windows PowerShell 5.1 for `scripts/verify.ps1`. Python and Pillow are not needed: S5 draws no icon.

## Global Constraints

- **Gate:** D-079 and D-080 are recorded on `main` (`cdd021a`), and this plan is committed to `main` together with the roadmap's S5 stage edits (see [Roadmap edits](#roadmap-edits)) before Task 1 starts. ADR-012 (Task 1) is written and accepted before any code task (D-079); in this run the controller accepts it under D-080, provisional pending the owner's reading. S5 depends on S4.2, which is tagged `v0.4.2`.
- Rhino 8 (8.19 or later) only (D-003); stages exchange Grasshopper objects, not JSON (D-017).
- `Lod.Core` and `Lod.Generators` have no RhinoCommon or Grasshopper reference; their tests run with plain `dotnet test`.
- Nullable reference types on; warnings are errors; `.editorconfig` rules are enforced in the build; every public member of `Lod.Core` and `Lod.Generators` has XML docs (CS1591 is an error).
- Generation is deterministic; outputs have a stable order.
- Numerical tolerances come only from `ToleranceSettings` (ADR-004); S5 adds none and changes none. Attribution keeps the distance tolerance of `WindowRehosting`; `GlazingExceedsWall` compares the glazed area with the wall area directly, as D-079 states it ("smaller than its area").
- **Only window geometry changes.** For every input that S4.2 accepts, zones, surfaces, areas, boundary conditions, surface IDs, the glazed area of every wall (`glazing=` in the reports), loads, internal mass, multipliers, and validation reports are unchanged. Snapshots: `linear-plan-canonical` and `stack-two-storeys` stay byte-identical; `simplifier-SemanticMerge`, `simplifier-PerimeterCore`, `simplifier-SingleZonePerFloor`, `aggregator-StackedFloorZoneMultiplier` (it stacks a *Perimeter Core* floor), `aggregator-SingleZonePerFloorType`, and `aggregator-SingleZoneBuilding` change in their `window(…)` entries only.
- **Guards, never repairs (GLOBAL.md quality rule 6).** A window is never capped, split, or moved to make the rule hold: `WindowNotHosted` and `GlazingExceedsWall` are errors and the step returns no floor or building.
- **No backward compatibility (D-064).** S5 adds and removes no component, input, or output; no GUID and no icon changes, and `scripts/make_icons.py` is not run. Saved definitions keep working; merged walls show one window where they showed several.
- Grasshopper components are thin adaptors (AGENTS.md): the rule lives in `Lod.Core`; S5 changes only description strings in `Lod.Grasshopper`.
- Research equivalence rules change only together with the research documentation (GLOBAL.md scientific rule 7): the research brief §10 is rewritten in Task 1, before any code.
- No simulation inside the pipeline (D-016). No CI (D-005): `scripts/verify.ps1` passes locally before every merge to `main`.
- Commits: `type(scope): summary` in lower case, no agent, model, or tool attribution and no `Co-Authored-By` trailers (D-001, D-002); author identity per D-050.
- **Pushes (D-080).** Nothing is pushed while the stage runs: slices are rebased onto local `main`, and the stage is tagged `v0.5.0` locally. Task 10 pushes `main` and the tags `v0.4.2` and `v0.5.0` after a fresh clone of `v0.5.0` passes `scripts/verify.ps1`; never a force push.
- `.gh` example definitions are made and saved by a person in Rhino 8; agents never write or check them (D-058). S5 adds none.
- S5 changes these earlier files: `DiagnosticCodes.cs` (S1, last changed in S4.2: `GlazingExceedsWall` appended), `Window.cs` (S2), `WindowRehosting.cs`, `PlanSimplifier.cs`, `SimplifierTests.cs` and the three `simplifier-*.txt` snapshots (S3), `SingleZoneMerge.cs`, `SingleZoneBuilding.cs`, `SingleZonePerFloorType.cs`, and the snapshots `aggregator-StackedFloorZoneMultiplier.txt`, `aggregator-SingleZoneBuilding.txt`, `aggregator-SingleZonePerFloorType.txt` (S4.2), `AggregatorTests.cs` (S4, last changed in S4.2), `AggregatorComponents.cs` (S4, last changed in S4.2), `Convert2BemComponent.cs` (S2, last changed in S4.2), `SimplifierComponents.cs` (S3, last changed in S4.1).

## Files

| Path | Change | Responsibility |
| --- | --- | --- |
| `docs/decisions/ADR-012-centred-windows.md` | Create | The rule, where it applies, what is conserved, the guards (D-079) |
| `docs/decisions/ADR-002-geometry.md`, `docs/decisions/ADR-009-vertical-aggregation.md`, `docs/decisions/ADR-013-vertical-aggregation-methods.md` | Modify (status lines) | "superseded in part by ADR-012" |
| `docs/LOD_geometric_zoning_equivalence_research_brief.md` | Modify | §10 rewritten without W1–W5; research questions 3 and 4, configuration space, pipeline, metadata, invariants, and deliverables without a window axis |
| `src/Lod.Core/Simplification/CentredWindows.cs` | Create | `CentredWindows.Place`: attribution, one centred window per rebuilt outdoor wall, the two guards |
| `src/Lod.Core/Common/DiagnosticCodes.cs` | Modify (S1 file, last changed in S4.2) | Append `GlazingExceedsWall`; `WindowNotHosted` described as a guard |
| `src/Lod.Core/Geometry/Window.cs` | Modify (S2 file) | Doc comment of `Window.Centered`: also used for rebuilt walls |
| `src/Lod.Core/Simplification/WindowRehosting.cs` | Modify (S3 file) | Doc comment: the attribution step of `CentredWindows` |
| `tests/Lod.Core.Tests/Simplification/CentredWindowsTests.cs` | Create | Merged wall, glazing split over three walls, walls left alone, rotated wall, the two guards |
| `src/Lod.Core/Simplification/PlanSimplifier.cs` | Modify (S3 file) | Calls `CentredWindows.Place` |
| `tests/Lod.Integration.Tests/CentredWindowTests.cs` | Create | Merging simplifiers and single-zone aggregators on the canonical and on rotated and moved plans; the steps that keep windows |
| `tests/Lod.Integration.Tests/SimplifierTests.cs` | Modify (S3 file) | The south perimeter wall has one centred window |
| `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt`, `simplifier-PerimeterCore.txt`, `simplifier-SingleZonePerFloor.txt` | Modify (S3 files) | `window(…)` entries of rebuilt walls |
| `tests/Lod.Integration.Tests/Snapshots/aggregator-StackedFloorZoneMultiplier.txt` | Modify (S4.2 file) | `window(…)` entries of the stacked *Perimeter Core* floor |
| `src/Lod.Core/Buildings/SingleZoneMerge.cs` | Modify (S4.2 file) | Calls `CentredWindows.Place` |
| `src/Lod.Core/Buildings/SingleZoneBuilding.cs`, `src/Lod.Core/Buildings/SingleZonePerFloorType.cs` | Modify (S4.2 files) | Doc comments |
| `tests/Lod.Integration.Tests/AggregatorTests.cs` | Modify (S4 file, last changed in S4.2) | Every rebuilt wall has exactly one window |
| `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.txt`, `aggregator-SingleZonePerFloorType.txt` | Modify (S4.2 files) | `window(…)` entries of rebuilt walls |
| `src/Lod.Grasshopper/Components/SimplifierComponents.cs`, `src/Lod.Grasshopper/Components/AggregatorComponents.cs`, `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` | Modify | Descriptions of the five components that rebuild walls and of the *Windows* output |
| `docs/architecture/pipeline.md`, `docs/architecture/validation.md`, `docs/architecture/convert2bem.md`, `docs/research/program-presets.md` | Modify | The rule, the guards, the *Windows* output, the component table through S5 |
| `docs/development/grasshopper-smoke-test.md` | Modify | Append the S5 checklist |
| `Directory.Build.props` | Modify | Version 0.5.0 |
| `AGENTS.md`, `README.md` | Modify | "Project state" and "Status" after S5; README pipeline block |
| `docs/plans/2026-09-30-implementation-roadmap.md` | Modify | Progress line, detailed-plans row, pipeline block, window constraint, repository layout (the S5 stage edits are committed with this plan) |
| `docs/decisions/decision-log.md` | Modify | S5 completion entry D-081 |

Test counts on `net8.0` at the start of S5: 136 core, 19 generators, 163 integration. After Task 2: 142 / 19 / 163. After Task 3: 142 / 19 / 173. After Task 4 and at the end: 142 core, 19 generators, 187 integration (core: +6 `CentredWindowsTests`; integration: +10 and +14 `CentredWindowTests`). Tests changed, none removed: `SimplifierTests.PerimeterSouthKeepsTheSouthFacadeWindowsInPlace` becomes `PerimeterSouthHasOneCentredWindowWithTheSouthFacadeGlazing`; `AggregatorTests.SingleZonePerFloorTypeConservesEveryInvariant` and `SingleZoneBuildingKeepsGroundRoofAndGlazing` check one window per wall instead of the source window count. Grasshopper code has no unit tests; Task 5 is checked by a 0-warning build and the smoke test of Task 8.

### Roadmap edits

The roadmap edits that describe S5 as the planned stage are committed together with this plan, before Task 1: the revision note v7 in the header, the S5 row of the stage table ("Centred windows on rebuilt walls"), the sentence below the stage diagram, the S5 section (goal, gate, work slices, tests), the S8 test line without window levels, the risk row on windows split between target walls, and the resolved and deferred lists of §7. The close-out (Task 9) adds the Progress line and the S5 row of the detailed-plans table and updates the pipeline block, the window constraint, and the repository layout, which describe the implemented code. After both, the roadmap equals the reference's apart from the Progress line and the detailed-plans row.

### Task assignment (D-048, execution handoff §6)

| Task | Agent | Why |
| --- | --- | --- |
| 1 ADR-012 and the research brief | `bemgen-bounded` | Documents fully given by the plan; accepted by the controller under D-080 |
| 2 Shared centred-window step | `bemgen-complex` | Wall geometry and a conservation invariant; a new error code |
| 3 Plan simplifiers | `bemgen-complex` | Plan simplifiers (handoff §6); four snapshots change in window entries only |
| 4 Single-zone floor aggregators | `bemgen-complex` | Floor aggregators on rotated plans; two snapshots change in window entries only |
| 5 Component descriptions | `bemgen-bounded` | Thin Grasshopper text, no behaviour |
| 6 Architecture and research documents | `bemgen-bounded` | Documents |
| 7 S5 smoke-test checklist | `bemgen-bounded` | Documents |
| 8 Smoke test in Rhino 8 | Manual (person), or the controller headless (D-056) | Needs Rhino 8 |
| 9 Close-out | `bemgen-bounded` | Bookkeeping |
| 10 Fresh-clone gate and push | Controller | D-080; a push is never delegated to a subagent |

The end-of-stage review is done by `bemgen-complex`. A bounded task escalates to `bemgen-complex` after two failures or any deviation from this plan's expected output.

---

## Slice A — `docs/decisions-adr-012`

### Task 1: ADR-012 Centred windows on rebuilt walls

**Files:**
- Create: `docs/decisions/ADR-012-centred-windows.md`
- Modify: `docs/decisions/ADR-002-geometry.md`, `docs/decisions/ADR-009-vertical-aggregation.md`, `docs/decisions/ADR-013-vertical-aggregation-methods.md` (status lines), `docs/LOD_geometric_zoning_equivalence_research_brief.md`

**Interfaces:**
- Consumes: decisions D-026, D-034, D-039, D-041, D-079, D-080; ADR-002 ("Windows through simplification (W0)"), ADR-009, ADR-013; S2–S4.2 types `Window.Centered`, `WindowRehosting`, `PlanSimplifier`, `SingleZoneMerge`.
- Produces: the accepted rule that Tasks 2–7 implement: `CentredWindows.Place` in `Lod.Core.Simplification`; the attribution by `WindowRehosting.Rehost` and the shape by `Window.Centered`; the guards `WindowNotHosted` (existing) and `GlazingExceedsWall` (new); where the rule applies and where windows are kept.

- [x] **Step 1: Create the branch**

```bash
git switch -c docs/decisions-adr-012 main
```

- [x] **Step 2: Write `docs/decisions/ADR-012-centred-windows.md` with exactly this content**

```markdown
# ADR-012: Centred windows on rebuilt walls

Status: Accepted (by the controller under D-080; provisional pending the owner's reading)

Date: 2026-10-01

Decisions: D-079, D-080; applies D-026, D-034, D-041; supersedes in part [ADR-002](ADR-002-geometry.md) ("Windows through simplification (W0)"), [ADR-009](ADR-009-vertical-aggregation.md), and [ADR-013](ADR-013-vertical-aggregation-methods.md) where they keep windows in place on rebuilt walls

## Context

Models are built from the bottom up. The plan generator creates the most detailed model, windows included: one centred window on every outdoor wall, sized from the preset's window-to-wall ratio (D-026, `Window.Centered`). Every later step only simplifies or aggregates.

Since D-039 (S2–S4.2), the steps that merge zones and rebuild walls (`SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`, and the single-zone floor aggregators `SingleZonePerFloorType` and `SingleZoneBuilding`) keep every source window unchanged and re-host it on the rebuilt wall that contains it (W0 at every zoning level, `WindowRehosting`). A merged wall therefore carries several windows, one per source wall it covers. The research brief (§10) and the roadmap planned window levels W1–W5 as a separate experimental axis in stage S5, gated on this ADR.

D-079 settles that window level of detail is not a separate axis: a rebuilt wall gets windows by the same rule the generator uses for its walls.

## Options considered

1. **Keep the source windows in place (W0, D-039).** Exact window positions at every zoning level. A merged wall carries the windows of its source walls; the model of a merged zone mixes the detail of the generator's walls with the coarseness of the merged zone, which is not what a modeller building that zone would draw.
2. **Window levels W1–W5 as transformations of their own (research brief §10 before this ADR).** Varies window representation independently of zoning. Adds an experimental axis, five transformations, and their validation, while the study's question is zoning and vertical simplification of a model built from the bottom up.
3. **One centred window per rebuilt wall with the wall's glazed area (chosen, D-079).** A rebuilt wall is treated like a wall of the generator: one window, centred, shaped by the generator's rule, with the glazed area of the source windows it covers. Glazed area is conserved per wall, and therefore per façade, orientation, and building.

## Decision

**Where it applies.** Wherever zones are merged and walls are rebuilt: the plan simplifiers *Semantic Merge*, *Perimeter Core*, and *Single Zone per Floor* (the shared `PlanSimplifier` pipeline) and the floor aggregators *Single Zone per Floor Type* and *Single Zone Building* (`SingleZoneMerge`, per storey outline). This is the only behaviour; there is no option to keep the windows in place. Steps that do not rebuild walls (*No Simplification*, *Stack Floors*, *Stacked Floor Zone Multiplier*) keep the windows of their input, which are already one centred window per wall when the input comes from the generator or from a step above.

**Rule.** One shared step, `CentredWindows.Place` in `Lod.Core.Simplification`, runs after the façade-coverage check (D-041):

1. Every window of a source outdoor wall is attributed to the target outdoor wall on the same façade line that contains it entirely (`WindowRehosting.Rehost`, the attribution of D-039, unchanged).
2. The glazed area of a target outdoor wall is the sum of the areas of the windows attributed to it: \(A_g = \sum A_\text{window,source}\).
3. The target wall gets exactly one window, centred on it and shaped by the generator's rule (D-026, `Window.Centered`): for a wall of length \(L\), height \(H\), and area \(A_w = L H\), the window is the wall rectangle scaled about its centre by \(k = \sqrt{A_g / A_w}\): width \(kL\), height \(kH\), offset \((L - kL)/2\), sill height \((H - kH)/2\). A target wall with \(A_g = 0\) gets no window.

**Conservation.** Glazed area is conserved per target wall, and therefore per façade, orientation, and building. Validation keeps checking glazing in total and per orientation; individual window positions, widths, and heights are no longer conserved and are not checked.

**Guards.** Because every target wall covers its source walls (D-041), every source window lies on exactly one target wall, and a target wall's glazed area is smaller than its area (the source walls it covers do not overlap along it, and each carries glazing below its own area, WWR < 1). Both hold by construction; the code still checks them and fails loudly, never caps or moves silently:

- a source window that no single target wall contains is the error `WindowNotHosted` (existing code);
- a target wall whose attributed glazed area is not smaller than its area is the error `GlazingExceedsWall` (new code).

## Consequences

- The snapshots of merged zones change in window geometry only (`window(...)` entries of rebuilt outdoor walls); every area, the glazing total per wall (`glazing=`), every load, and every boundary stay identical. Snapshots built on a floor of a merging simplifier change in the same way even when the aggregator does not rebuild walls (`aggregator-StackedFloorZoneMultiplier.txt` stacks a *Perimeter Core* floor).
- Glazing totals per wall, façade, orientation, and building are unchanged, so validation reports are unchanged; validation still checks glazing in total and per orientation.
- `WindowNotHosted` stays only as a guard; it cannot occur for floors and buildings that pass façade coverage. One new error code, `GlazingExceedsWall`, appended to `DiagnosticCodes`.
- A merged wall carries one wide window where its source walls carried several; window positions within a façade are not a variable of the study.
- The research brief §10 drops W1–W5 and describes this rule; the roadmap drops the window levels and names S5 "Centred windows on rebuilt walls".
- Changing the rule (window shape, where it applies, an option to keep windows in place) needs a decision-log entry, an update of this ADR, and an update of the research brief (GLOBAL.md scientific rule 7).
```

- [x] **Step 3: Mark ADR-002, ADR-009, and ADR-013 as superseded in part**

In `docs/decisions/ADR-002-geometry.md` make this replacement; the "Replace" text occurs exactly once in the file.

1. Replace

```markdown
Status: Accepted
```

   with

```markdown
Status: Accepted; superseded in part by [ADR-012](ADR-012-centred-windows.md) (windows through simplification)
```

In `docs/decisions/ADR-009-vertical-aggregation.md` make this replacement; the "Replace" text occurs exactly once in the file.

1. Replace

```markdown
Status: Accepted; superseded in part by [ADR-013](ADR-013-vertical-aggregation-methods.md)
```

   with

```markdown
Status: Accepted; superseded in part by [ADR-013](ADR-013-vertical-aggregation-methods.md) and by [ADR-012](ADR-012-centred-windows.md) (windows on rebuilt walls)
```

In `docs/decisions/ADR-013-vertical-aggregation-methods.md` make this replacement; the "Replace" text occurs exactly once in the file.

1. Replace

```markdown
Status: Accepted (by the controller under D-075; provisional pending the owner's reading)
```

   with

```markdown
Status: Accepted (by the controller under D-075; provisional pending the owner's reading); superseded in part by [ADR-012](ADR-012-centred-windows.md) (windows on rebuilt walls)
```

- [x] **Step 4: Update the research brief**

GLOBAL.md scientific rule 7: the research equivalence rules for windows change together with the brief. In `docs/LOD_geometric_zoning_equivalence_research_brief.md` make these replacements, in order; each "Replace" text occurs exactly once in the file. They add a note to research questions 3 and 4, rewrite §10 without the levels W1–W5, and remove the window level from the configuration space, the pipeline, the metadata, the invariants, the case record, and the deliverables.

1. Replace

```markdown
4. How sensitive are results to redistributing or aggregating windows after zones are merged?
```

   with

```markdown
4. How sensitive are results to redistributing or aggregating windows after zones are merged?

Questions 3 and 4 are not pursued as a separate window axis in this project: windows follow one rule at every level (§10, D-079), and their effect is part of the zoning and vertical simplification under study.
```

2. Replace

```markdown
## 10. Window Representation Levels

Window treatment should form an independent experimental axis.

Rule adopted for this project (D-039, D-026): walls carry explicit windows, each with a position along the wall, a sill height, a width, and a height, and a wall may carry any number of windows (ADR-002). The first plan generator uses one simple deterministic rule: one window per outdoor wall, centered on it and sized from the window-to-wall ratio of the zone's program preset, \(A_\text{glazing} = \text{WWR} \times A_\text{wall}\) (D-026); this is that generator's placement rule, not a property of windows. Plan simplifiers and floor aggregators keep every window unchanged, so every zoning and vertical level is at W0: where walls are rebuilt, each source window is re-hosted on the target outdoor wall that contains it, at the same position, sill height, and size. A window that no single target wall contains is an error; windows are never moved, resized, or split silently. The levels W1 to W5 below are separate window transformations, planned as roadmap stage S5 with their own decision record (ADR-012), so window effects can be varied independently of zoning.

### W0 — Explicit Ground-Truth Windows

Windows are represented using explicit:

- position,
- width,
- height,
- sill height,
- façade assignment,
- zone assignment.

### W1 — Equivalent Window Area by Source Zone

Replace explicit windows with simplified windows while preserving the total glazed area assigned to each zone and orientation.

### W2 — Window-to-Wall Ratio by Target Zone

After rezoning, determine equivalent WWR for each target zone façade.

The total glazed area should satisfy:

\[
A_{\text{window,target}} =
\sum A_{\text{window,source}}
\]

within the corresponding façade/orientation mapping.

### W3 — Redistributed Windows

Redistribute the same total window area across the available exterior façade of the target zones.

Possible redistribution rules:

- uniform by wall length,
- uniform by façade area,
- proportional by source window area,
- centered per façade,
- module-based distribution.

### W4 — Orientation-Level WWR

Preserve only total glazed area by orientation, independent of original zone ownership.

### W5 — Building-Level WWR

Preserve total glazed area only at building level.

This represents a highly simplified model suitable for testing the effect of losing local façade-window relationships.
```

   with

```markdown
## 10. Window Representation

Window representation is not a separate experimental axis. Models are built from the bottom up: the plan generator creates the most detailed model, windows included, and every later step only simplifies or aggregates, so windows follow the zoning and vertical levels (D-079, ADR-012).

Rule adopted for this project (D-026, D-039, D-079): walls carry explicit windows, each with a position along the wall, a sill height, a width, and a height (ADR-002). The first plan generator uses one simple deterministic rule: one window per outdoor wall, centred on it and sized from the window-to-wall ratio of the zone's program preset, \(A_\text{glazing} = \text{WWR} \times A_\text{wall}\) (D-026); the window is the wall rectangle scaled about its centre by \(\sqrt{A_\text{glazing} / A_\text{wall}}\). This is that generator's placement rule, not a property of windows.

Wherever zones are merged and walls are rebuilt (Z1–Z3, and the single-zone vertical methods), every outdoor wall of a target zone carries exactly one window, centred on the wall by the same rule, whose glazed area is the total glazed area of the source windows that wall covers:

\[
A_{\text{window,target wall}} =
\sum_{\text{source windows on the wall}} A_{\text{window,source}}
\]

A target wall without glazed area gets no window. Glazed area is therefore conserved per target wall, and so per façade, orientation, and building; individual window positions are not. Because every target façade covers every source façade over its full length (D-041), every source window lies on exactly one target wall and a target wall's glazed area is smaller than its area; both are checked and fail loudly if they ever do not hold, and windows are never capped or moved silently. Steps that do not rebuild walls (Z0, stacking, the floor multiplier) keep the windows of their input, which already follow the rule.

The window levels W1 to W5 planned earlier (equivalent window area by source zone, WWR by target zone, redistributed windows, orientation-level and building-level WWR) are dropped (D-079).
```

3. Replace

```markdown
- window LoD,
- vertical LoD,
- climate/weather file,
- orientation,
- internal-load scenario if later needed.

A model configuration may therefore be represented as:

`Typology × GeometrySeed × Z-Level × W-Level × V-Level × Weather`
```

   with

```markdown
- vertical LoD,
- climate/weather file,
- orientation,
- internal-load scenario if later needed.

A model configuration may therefore be represented as:

`Typology × GeometrySeed × Z-Level × V-Level × Weather`

Windows are not a factor of their own (§10, D-079).
```

4. Replace

```markdown
9. transform window representation,
```

   with

```markdown
9. rebuild windows on merged walls (one centred window per wall, §10),
```

5. Replace

```markdown
### Transformation Metadata

- zoning LoD,
- window LoD,
```

   with

```markdown
### Transformation Metadata

- zoning LoD,
```

6. Replace

```markdown
Depending on the chosen window LoD:

- total window area conserved,
- orientation-specific area conserved where required,
- target windows remain on exterior walls.
```

   with

```markdown
- total window area conserved,
- window area per orientation conserved,
- target windows remain on exterior walls (by construction, §10).
```

7. Replace

```markdown
- zoning level,
- window level,
```

   with

```markdown
- zoning level,
```

8. Replace

```markdown
6. window transformation tools,
7. common intermediate model representation,
8. validation and invariant checks,
9. automated export interface,
10. batch simulation configurations,
11. comparative simulation dataset,
12. analysis of error by zoning, window, vertical LoD, typology, and weather,
```

   with

```markdown
6. window rebuilding on merged walls,
7. common intermediate model representation,
8. validation and invariant checks,
9. automated export interface,
10. batch simulation configurations,
11. comparative simulation dataset,
12. analysis of error by zoning, vertical LoD, typology, and weather,
```

- [x] **Step 5: Check the result**

```bash
git grep -n -E "W-Level|window LoD|W1 —|W5 —" -- docs/LOD_geometric_zoning_equivalence_research_brief.md
git grep -n -E "^Status: .*ADR-012" -- docs/decisions
```

Expected: no output for the first command; three lines for the second, the status lines of ADR-002, ADR-009, and ADR-013 (ADR-012's own status line does not name itself).

- [x] **Step 6: Commit**

```bash
git add docs/decisions/ADR-012-centred-windows.md docs/decisions/ADR-002-geometry.md docs/decisions/ADR-009-vertical-aggregation.md docs/decisions/ADR-013-vertical-aggregation-methods.md docs/LOD_geometric_zoning_equivalence_research_brief.md
git commit -m "docs(decisions): add adr-012 on centred windows on rebuilt walls"
```

- [x] **Step 7: Gate — acceptance (controller under D-080)**

D-079 gates S5 on ADR-012. In this run the controller accepts it under D-080, after checking it against D-026, D-039, D-041, D-079, ADR-002, ADR-009, and ADR-013; its status line already says so ("Accepted (by the controller under D-080; provisional pending the owner's reading)"). The owner's reading stays open; requested changes are made in a later change, with code changes if the ADR's rules change. If the check finds a contradiction with a decision, stop and report it instead of merging. Slice B starts only after this branch is merged.

- [x] **Step 8: Merge Slice A (D-004)**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch docs/decisions-adr-012
git rebase main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git merge --ff-only docs/decisions-adr-012
git branch -d docs/decisions-adr-012
```

Expected: verify ends with `VERIFY PASSED`; its test lines show 136 core, 19 generators, and 163 integration tests passed on net8.0 (this slice changes no code). `git pull --ff-only` reports `Already up to date.` or fast-forwards; it fails only if `origin/main` has commits that local `main` does not, and then the controller stops and reports. Do not push (D-080: pushes come in Task 10).

---

## Slice B — `feature/windows-centred-windows`

### Task 2: The shared centred-window step

**Files:**
- Create: `src/Lod.Core/Simplification/CentredWindows.cs`
- Modify: `src/Lod.Core/Common/DiagnosticCodes.cs` (S1 file, last changed in S4.2), `src/Lod.Core/Geometry/Window.cs` (S2 file), `src/Lod.Core/Simplification/WindowRehosting.cs` (S3 file)
- Test: create `tests/Lod.Core.Tests/Simplification/CentredWindowsTests.cs`

**Interfaces:**
- Consumes (S2–S4.2): `WindowRehosting.Rehost(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances) : Result<IReadOnlyList<Surface>>` (each source window moved, unchanged, to the target outdoor wall on the same façade line that contains it; `WindowNotHosted` otherwise); `Window.Centered(double wallLength, double wallHeight, double glazedArea) : Window?` (the wall rectangle scaled about its centre by √(glazed area / wall area); `null` for zero glazing); `Window.At(double offset, double width, double sillHeight, double height)`; `WallSurface.Area`, `Length`, `Height`, `GlazedArea`, `Windows`, `WithWindows(IEnumerable<Window>)`; `Result.FromDiagnostics<T>(Func<T>, IReadOnlyCollection<Diagnostic>)`; `Diagnostic.Error(string code, string message, string? subject)`; test support `TestZones.Wall(string id, string zone, double x0, double y0, double x1, double y1, params Window[] windows)` (height 3 m, outdoors).
- Produces:
  - `public static class CentredWindows` with `public static Result<IReadOnlyList<Surface>> Place(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances)`: the target surfaces in their order, every outdoor wall with exactly one window `Window.Centered(wall.Length, wall.Height, glazing)` where `glazing` is the area of the source windows attributed to it, or none when that is zero; other surfaces unchanged (the same instances). Errors: those of `Rehost` (`WindowNotHosted`, subject the source wall), else one `GlazingExceedsWall` per wall whose glazing is not smaller than its area (subject the target wall ID, message `The windows attributed to this wall have {glazing:0.######} m² of glazing, not less than its {wall.Area:0.######} m² (D-079).`).
  - `DiagnosticCodes.GlazingExceedsWall = "GlazingExceedsWall"`.

- [x] **Step 1: Create the branch**

```bash
git switch -c feature/windows-centred-windows main
```

- [x] **Step 2: Write the failing tests — create `tests/Lod.Core.Tests/Simplification/CentredWindowsTests.cs` (full file)**

Six tests: two source walls merged into one wall give one centred window of 6.5 m² with the generator's proportions; a 30 m source wall with three windows split over three 10 m target walls gives 4, 5, and 0 m² (the third wall gets no window); a wall on another façade and an interzone partition are left alone (the partition is the same instance); a wall at 30° gets the centred window too; a window across two target walls is `WindowNotHosted` for the source wall; two source walls on the same span (impossible in a valid plan) carrying 50.4 m² on a 30 m² wall give exactly one error `GlazingExceedsWall` for the target wall.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Simplification;

public sealed class CentredWindowsTests
{
    [Fact]
    public void MergedWallGetsOneCentredWindowWithTheGlazingItCovers()
    {
        WallSurface left = TestZones.Wall("A/W1", "A", 0, 0, 10, 0, Window.At(1.0, 2.0, 0.5, 1.0));
        WallSurface right = TestZones.Wall("B/W1", "B", 10, 0, 20, 0, Window.At(2.0, 3.0, 1.0, 1.5));
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 20, 0);

        IReadOnlyList<Surface> result = CentredWindows.Place(new Surface[] { left, right }, new Surface[] { merged }, ToleranceSettings.Default).Value;

        WallSurface host = Assert.IsType<WallSurface>(Assert.Single(result));
        Window window = Assert.Single(host.Windows);
        double scale = Math.Sqrt(6.5 / 60.0);
        Assert.Equal(6.5, window.Area, 12);
        Assert.Equal(20.0 * scale, window.Width, 12);
        Assert.Equal(3.0 * scale, window.Height, 12);
        Assert.Equal((20.0 - window.Width) / 2.0, window.Offset, 12);
        Assert.Equal((3.0 - window.Height) / 2.0, window.SillHeight, 12);
    }

    [Fact]
    public void EachTargetWallReceivesTheGlazingOfTheWindowsItContains()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 30, 0, Window.At(2.0, 4.0, 1.0, 1.0), Window.At(13.0, 3.0, 1.0, 1.0), Window.At(16.0, 2.0, 1.0, 1.0));
        WallSurface first = TestZones.Wall("P/W1", "P", 0, 0, 10, 0);
        WallSurface second = TestZones.Wall("Q/W1", "Q", 10, 0, 20, 0);
        WallSurface third = TestZones.Wall("R/W1", "R", 20, 0, 30, 0);

        IReadOnlyList<Surface> result = CentredWindows.Place(new Surface[] { source }, new Surface[] { first, second, third }, ToleranceSettings.Default).Value;

        WallSurface[] walls = result.OfType<WallSurface>().ToArray();
        Assert.Equal(new[] { 4.0, 5.0, 0.0 }, walls.Select(w => Math.Round(w.GlazedArea, 12)));
        Assert.Equal(new[] { 1, 1, 0 }, walls.Select(w => w.Windows.Count));
        Assert.All(walls.Take(2), w => Assert.Equal((w.Length - w.Windows[0].Width) / 2.0, w.Windows[0].Offset, 12));
    }

    [Fact]
    public void TargetWallsOnAnotherFacadeOrInsideAreUnchanged()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 10, 0, Window.At(1.0, 2.0, 0.5, 1.0));
        WallSurface host = TestZones.Wall("M/W1", "M", 0, 0, 10, 0);
        WallSurface otherFacade = TestZones.Wall("M/W2", "M", 10, 0, 10, 8);
        var partition = new WallSurface(new SurfaceId("M/W3"), new ZoneId("M"), new Point2(10, 8), new Point2(0, 8), 0.0, 3.0, BoundaryCondition.Interzone, new ZoneId("N"), Array.Empty<Window>());

        IReadOnlyList<Surface> result = CentredWindows.Place(new Surface[] { source }, new Surface[] { host, otherFacade, partition }, ToleranceSettings.Default).Value;

        Assert.Equal(new[] { 1, 0, 0 }, result.OfType<WallSurface>().Select(w => w.Windows.Count));
        Assert.Same(partition, result[2]);
    }

    [Fact]
    public void RotatedWallsGetTheCentredWindowToo()
    {
        double c = Math.Cos(Math.PI / 6.0);
        double s = Math.Sin(Math.PI / 6.0);
        WallSurface left = TestZones.Wall("A/W1", "A", 0, 0, 10 * c, 10 * s, Window.At(1.0, 2.0, 0.5, 1.0));
        WallSurface right = TestZones.Wall("B/W1", "B", 10 * c, 10 * s, 20 * c, 20 * s, Window.At(2.0, 3.0, 1.0, 1.5));
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 20 * c, 20 * s);

        WallSurface host = Assert.IsType<WallSurface>(Assert.Single(CentredWindows.Place(new Surface[] { left, right }, new Surface[] { merged }, ToleranceSettings.Default).Value));

        Window window = Assert.Single(host.Windows);
        Assert.Equal(6.5, window.Area, 12);
        Assert.Equal((host.Length - window.Width) / 2.0, window.Offset, 12);
    }

    [Fact]
    public void WindowAcrossTwoTargetWallsIsAnError()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0, Window.At(8.0, 4.0, 1.0, 1.0));
        WallSurface first = TestZones.Wall("P/W1", "P", 0, 0, 10, 0);
        WallSurface second = TestZones.Wall("Q/W1", "Q", 10, 0, 20, 0);

        Result<IReadOnlyList<Surface>> result = CentredWindows.Place(new Surface[] { source }, new Surface[] { first, second }, ToleranceSettings.Default);

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.WindowNotHosted && d.Subject == "A/W1");
    }

    [Fact]
    public void GlazingNotSmallerThanTheTargetWallIsAnError()
    {
        // Two source walls on the same span of one façade line cannot come from a valid plan; together they carry 50.4 m² on a 30 m² wall.
        WallSurface first = TestZones.Wall("A/W1", "A", 0, 0, 10, 0, Window.At(0.5, 9.0, 0.1, 2.8));
        WallSurface second = TestZones.Wall("B/W1", "B", 0, 0, 10, 0, Window.At(0.5, 9.0, 0.1, 2.8));
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 10, 0);

        Result<IReadOnlyList<Surface>> result = CentredWindows.Place(new Surface[] { first, second }, new Surface[] { merged }, ToleranceSettings.Default);

        Assert.False(result.IsSuccess);
        Diagnostic error = Assert.Single(result.Diagnostics);
        Assert.Equal(DiagnosticCodes.GlazingExceedsWall, error.Code);
        Assert.Equal(DiagnosticSeverity.Error, error.Severity);
        Assert.Equal("M/W1", error.Subject);
    }
}
```

- [x] **Step 3: Run the tests and see them fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification.CentredWindowsTests"
```

Expected: the build fails because the code does not exist yet, each error reported once, for the `net8.0` target:

```text
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(22,41): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(42,41): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(58,41): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(73,69): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(87,49): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(101,49): error CS0103: The name 'CentredWindows' does not exist in the current context
tests\Lod.Core.Tests\Simplification\CentredWindowsTests.cs(105,38): error CS0117: 'DiagnosticCodes' does not contain a definition for 'GlazingExceedsWall'
```

- [x] **Step 4: Append the code — replace `src/Lod.Core/Common/DiagnosticCodes.cs` (full file)**

`GlazingExceedsWall` is appended at the end; the summary of `WindowNotHosted` now calls it a guard. No code is renamed or reused.

```csharp
namespace Lod.Core.Common;

/// <summary>
/// Stable diagnostic codes. Add new codes here; never reuse or rename a published code.
/// </summary>
public static class DiagnosticCodes
{
    /// <summary>A required name is empty.</summary>
    public const string EmptyName = "EmptyName";

    /// <summary>A schedule does not have exactly <c>Schedule.HoursPerYear</c> values.</summary>
    public const string ScheduleLength = "ScheduleLength";

    /// <summary>A schedule value is not finite or outside the range allowed by its kind.</summary>
    public const string ScheduleValue = "ScheduleValue";

    /// <summary>A schedule has the wrong kind for its use (fraction vs temperature).</summary>
    public const string ScheduleKindMismatch = "ScheduleKindMismatch";

    /// <summary>A load value is negative or not finite.</summary>
    public const string LoadValue = "LoadValue";

    /// <summary>A load uses a basis that is not allowed for its type.</summary>
    public const string LoadBasisNotAllowed = "LoadBasisNotAllowed";

    /// <summary>A program contains the same load type in the same basis twice.</summary>
    public const string DuplicateLoadType = "DuplicateLoadType";

    /// <summary>A per-person load is defined without an occupancy load.</summary>
    public const string PerPersonWithoutOccupancy = "PerPersonWithoutOccupancy";

    /// <summary>A window-to-wall ratio is outside [0, 1).</summary>
    public const string WindowToWallRatio = "WindowToWallRatio";

    /// <summary>An aggregation received no source zones.</summary>
    public const string NoSources = "NoSources";

    /// <summary>A transfer fraction is outside [0, 1].</summary>
    public const string FractionOutOfRange = "FractionOutOfRange";

    /// <summary>A positive load cannot be expressed because the target's basis quantity is zero.</summary>
    public const string ZeroBasisQuantity = "ZeroBasisQuantity";

    /// <summary>An aggregated load is zero; its schedule is set to a constant zero.</summary>
    public const string ZeroLoadSchedule = "ZeroLoadSchedule";

    /// <summary>Setpoint weights of the conditioned sources sum to zero.</summary>
    public const string ZeroSetpointWeight = "ZeroSetpointWeight";

    /// <summary>Zone measures are negative or not finite.</summary>
    public const string InvalidMeasures = "InvalidMeasures";

    /// <summary>A polygon ring has fewer than three distinct points or no area.</summary>
    public const string DegeneratePolygon = "DegeneratePolygon";

    /// <summary>Two zones overlap.</summary>
    public const string OverlappingZones = "OverlappingZones";

    /// <summary>A zone edge is neither shared with another zone nor on the plan boundary.</summary>
    public const string UnmatchedEdge = "UnmatchedEdge";

    /// <summary>A generator, simplifier, or aggregator parameter is invalid.</summary>
    public const string InvalidParameter = "InvalidParameter";

    /// <summary>No program preset is given for a preset input, or for a space type the generator's layout places.</summary>
    public const string MissingPreset = "MissingPreset";

    /// <summary>Floors with different orientations cannot form one building.</summary>
    public const string OrientationMismatch = "OrientationMismatch";

    /// <summary>A floor aggregator received no floors.</summary>
    public const string NoFloors = "NoFloors";

    /// <summary>Zones grouped for merging do not form one connected polygon.</summary>
    public const string DisconnectedGroup = "DisconnectedGroup";

    /// <summary>The perimeter depth leaves no valid core.</summary>
    public const string PlanTooNarrow = "PlanTooNarrow";

    /// <summary>The input is valid but not supported by this implementation yet.</summary>
    public const string NotSupported = "NotSupported";

    /// <summary>Target outdoor walls do not cover a source outdoor wall over its full length (D-041).</summary>
    public const string FacadeNotCovered = "FacadeNotCovered";

    /// <summary>No single target wall contains a source window (D-039); a guard that cannot fail once the target façades cover the source façades (D-041, D-079).</summary>
    public const string WindowNotHosted = "WindowNotHosted";

    /// <summary>Validation failed and conversion was blocked.</summary>
    public const string ValidationFailed = "ValidationFailed";

    /// <summary>Validation failed and conversion continued because an override was given.</summary>
    public const string ValidationOverridden = "ValidationOverridden";

    /// <summary>A multiplied floor type had exposed floors or ceilings; its exposed storeys were split off as x1 storeys (D-046).</summary>
    public const string FloorTypeSplit = "FloorTypeSplit";

    /// <summary>A preset given to a generator's preset input has a different space type than the input feeds (D-061).</summary>
    public const string PresetSpaceTypeMismatch = "PresetSpaceTypeMismatch";

    /// <summary>Part of a storey's floor is not covered by the storey below; the part faces outdoors (D-074).</summary>
    public const string UnsupportedStorey = "UnsupportedStorey";

    /// <summary>The glazed area attributed to a rebuilt wall is not smaller than the wall's area, so no centred window can carry it (D-079).</summary>
    public const string GlazingExceedsWall = "GlazingExceedsWall";
}
```

- [x] **Step 5: Implement — create `src/Lod.Core/Simplification/CentredWindows.cs` (full file)**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>
/// Windows of rebuilt walls (D-079, ADR-012): every source window is attributed to the target outdoor wall on the same façade line that contains it
/// (<see cref="WindowRehosting"/>), and each target outdoor wall then carries exactly one window, centred on it by the generator's rule
/// (<see cref="Window.Centered"/>, D-026), whose area is the total glazed area attributed to it. A target wall without glazing gets no window.
/// Glazed area is conserved per target wall, and so per façade, orientation, and building; window positions are not.
/// </summary>
public static class CentredWindows
{
    /// <summary>Gives every target outdoor wall one centred window with the glazed area of the source windows it contains.</summary>
    /// <param name="sourceSurfaces">Source surfaces with windows.</param>
    /// <param name="targetSurfaces">Target surfaces; their outdoor walls receive the windows (any windows they already have are replaced).</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>
    /// The target surfaces with windows, or errors: <see cref="DiagnosticCodes.WindowNotHosted"/> when no single target wall contains a source window,
    /// <see cref="DiagnosticCodes.GlazingExceedsWall"/> when a target wall's glazed area is not smaller than its area. Both hold by construction once
    /// the target façades cover the source façades (D-041); they are checked, never capped or repaired.
    /// </returns>
    public static Result<IReadOnlyList<Surface>> Place(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances)
    {
        Result<IReadOnlyList<Surface>> attributed = WindowRehosting.Rehost(sourceSurfaces, targetSurfaces, tolerances);
        if (!attributed.IsSuccess)
        {
            return attributed;
        }

        var diagnostics = new List<Diagnostic>();
        Surface[] placed = attributed.Value
            .Select(s => s is WallSurface { Boundary: BoundaryCondition.Outdoors } wall ? Centre(wall, diagnostics) : s)
            .ToArray();
        return Result.FromDiagnostics<IReadOnlyList<Surface>>(() => placed, diagnostics);
    }

    private static WallSurface Centre(WallSurface wall, List<Diagnostic> diagnostics)
    {
        double glazing = wall.GlazedArea;
        if (glazing >= wall.Area)
        {
            diagnostics.Add(Diagnostic.Error(
                DiagnosticCodes.GlazingExceedsWall,
                $"The windows attributed to this wall have {glazing:0.######} m² of glazing, not less than its {wall.Area:0.######} m² (D-079).",
                wall.Id.Value));
            return wall;
        }

        return wall.WithWindows(Window.Centered(wall.Length, wall.Height, glazing) is { } window ? new[] { window } : Array.Empty<Window>());
    }
}
```

- [x] **Step 6: Update the doc comments — replace `src/Lod.Core/Geometry/Window.cs` and `src/Lod.Core/Simplification/WindowRehosting.cs` (full files)**

Only the summaries change: `Window.Centered` is also used for rebuilt walls (D-079); `WindowRehosting` is the attribution step and points to `CentredWindows`. Its code is unchanged.

`src/Lod.Core/Geometry/Window.cs`:

```csharp
using System;

namespace Lod.Core.Geometry;

/// <summary>
/// An explicit rectangular window in a wall (D-039): its position along the wall, its sill height above the wall's bottom edge, and its size.
/// </summary>
public sealed class Window
{
    private Window(double offset, double width, double sillHeight, double height)
    {
        Offset = offset;
        Width = width;
        SillHeight = sillHeight;
        Height = height;
    }

    /// <summary>Distance from the wall's start point to the window's near edge, along the wall, m.</summary>
    public double Offset { get; }

    /// <summary>Window width along the wall, m.</summary>
    public double Width { get; }

    /// <summary>Height of the window's bottom edge above the wall's bottom edge, m.</summary>
    public double SillHeight { get; }

    /// <summary>Window height, m.</summary>
    public double Height { get; }

    /// <summary>Glazed area, m².</summary>
    public double Area => Width * Height;

    /// <summary>A window at an explicit position.</summary>
    /// <param name="offset">Distance from the wall start to the near edge, m; not negative.</param>
    /// <param name="width">Width, m; positive.</param>
    /// <param name="sillHeight">Sill height above the wall's bottom edge, m; not negative.</param>
    /// <param name="height">Height, m; positive.</param>
    /// <returns>The window.</returns>
    /// <exception cref="ArgumentOutOfRangeException">A dimension is out of range.</exception>
    public static Window At(double offset, double width, double sillHeight, double height)
    {
        if (!(offset >= 0) || !(sillHeight >= 0) || !(width > 0) || !(height > 0) || double.IsInfinity(width + height + offset + sillHeight))
        {
            throw new ArgumentOutOfRangeException(nameof(width), $"Invalid window: offset {offset}, width {width}, sill {sillHeight}, height {height}.");
        }

        return new Window(offset, width, sillHeight, height);
    }

    /// <summary>
    /// The window centered on a wall with a given glazed area: the wall rectangle scaled about its centre by √(glazed area / wall area); <c>null</c>
    /// for zero glazing. This is the S2 generator's placement rule (D-026, D-039), also used for every rebuilt wall (D-079), not a property of windows
    /// in general.
    /// </summary>
    /// <param name="wallLength">Wall length, m.</param>
    /// <param name="wallHeight">Wall height, m.</param>
    /// <param name="glazedArea">Glazed area, m²; must be less than the wall area.</param>
    /// <returns>The window or <c>null</c>.</returns>
    /// <exception cref="ArgumentOutOfRangeException">The glazed area is negative or does not fit the wall.</exception>
    public static Window? Centered(double wallLength, double wallHeight, double glazedArea)
    {
        double wallArea = wallLength * wallHeight;
        if (glazedArea < 0 || glazedArea >= wallArea)
        {
            throw new ArgumentOutOfRangeException(nameof(glazedArea), glazedArea, $"Glazed area must be in [0, {wallArea}).");
        }

        if (glazedArea == 0)
        {
            return null;
        }

        double scale = Math.Sqrt(glazedArea / wallArea);
        double width = wallLength * scale;
        double height = wallHeight * scale;
        return new Window((wallLength - width) / 2.0, width, (wallHeight - height) / 2.0, height);
    }

    /// <summary>The same window at another position along a wall.</summary>
    /// <param name="offset">New offset, m.</param>
    /// <returns>The moved window.</returns>
    public Window MovedTo(double offset) => At(offset, Width, SillHeight, Height);
}
```

`src/Lod.Core/Simplification/WindowRehosting.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>
/// Attributes source windows to rebuilt walls (D-039): each window of a source outdoor wall moves to the target outdoor wall on the same façade
/// line that contains it entirely, at the same position, sill, and size. A window that no single target wall contains is an error; windows are
/// never moved, resized, or split silently. <see cref="CentredWindows"/> then replaces the windows of each rebuilt wall by one centred window (D-079).
/// </summary>
public static class WindowRehosting
{
    /// <summary>Re-hosts the windows of the source outdoor walls on the target outdoor walls.</summary>
    /// <param name="sourceSurfaces">Source surfaces with windows.</param>
    /// <param name="targetSurfaces">Target surfaces; their outdoor walls receive the windows (any windows they already have are replaced).</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>The target surfaces with windows, or <see cref="DiagnosticCodes.WindowNotHosted"/> errors.</returns>
    public static Result<IReadOnlyList<Surface>> Rehost(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances)
    {
        WallSurface[] hosts = targetSurfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors).ToArray();
        var hosted = hosts.ToDictionary(h => h.Id, _ => new List<Window>());
        var diagnostics = new List<Diagnostic>();
        foreach (WallSurface source in sourceSurfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors))
        {
            foreach (Window window in source.Windows)
            {
                (WallSurface Host, double Offset)? placement = Place(source, window, hosts, tolerances);
                if (placement is { } p)
                {
                    hosted[p.Host.Id].Add(window.MovedTo(p.Offset));
                }
                else
                {
                    diagnostics.Add(Diagnostic.Error(
                        DiagnosticCodes.WindowNotHosted,
                        $"No single target wall contains the window at offset {window.Offset:0.###} m (width {window.Width:0.###} m).",
                        source.Id.Value));
                }
            }
        }

        return Result.FromDiagnostics<IReadOnlyList<Surface>>(
            () => targetSurfaces.Select(s => s is WallSurface w && hosted.TryGetValue(w.Id, out List<Window>? windows) ? w.WithWindows(windows) : s).ToArray(),
            diagnostics);
    }

    private static (WallSurface Host, double Offset)? Place(WallSurface source, Window window, IEnumerable<WallSurface> hosts, ToleranceSettings tolerances)
    {
        foreach (WallSurface host in hosts)
        {
            if (FacadeAttribution.Interval(host, source, tolerances) is not { } interval)
            {
                continue;
            }

            double start = interval.Start + window.Offset;
            double end = start + window.Width;
            if (start >= -tolerances.Distance && end <= host.Length + tolerances.Distance)
            {
                // Clamping only removes floating-point noise below the distance tolerance.
                return (host, Math.Min(Math.Max(0.0, start), host.Length - window.Width));
            }
        }

        return null;
    }
}
```

- [x] **Step 7: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification.CentredWindowsTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     6, Skipped:     0, Total:     6, Duration: … - Lod.Core.Tests.dll (net8.0)
```

Then the solution:

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
git status --short
```

Expected: `Build succeeded.`, `0 Warning(s)`, `0 Error(s)`; on net8.0 (the order of the lines may differ):

```text
Passed!  - Failed:     0, Passed:   142, Skipped:     0, Total:   142, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    19, Skipped:     0, Total:    19, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:   163, Skipped:     0, Total:   163, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

`git status --short` lists exactly the five files of this task (three modified, two new), and no `*.received.txt`: nothing uses the new step yet, so every snapshot is unchanged.

- [x] **Step 8: Commit**

```bash
git add src/Lod.Core/Simplification/CentredWindows.cs src/Lod.Core/Common/DiagnosticCodes.cs src/Lod.Core/Geometry/Window.cs src/Lod.Core/Simplification/WindowRehosting.cs tests/Lod.Core.Tests/Simplification/CentredWindowsTests.cs
git commit -m "feature(windows): add the shared centred-window step for rebuilt walls"
```

### Task 3: Plan simplifiers give every rebuilt outdoor wall one centred window

**Files:**
- Modify: `src/Lod.Core/Simplification/PlanSimplifier.cs` (S3 file)
- Test: create `tests/Lod.Integration.Tests/CentredWindowTests.cs`; modify `tests/Lod.Integration.Tests/SimplifierTests.cs` (S3 file)
- Snapshots: modify `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt`, `simplifier-PerimeterCore.txt`, `simplifier-SingleZonePerFloor.txt` (S3 files), `aggregator-StackedFloorZoneMultiplier.txt` (S4.2 file)

**Interfaces:**
- Consumes: `CentredWindows.Place` (Task 2); `PlanSimplifier.Simplify(IGeneratedPlan) : Result<IFloor>` (S3; the façade-coverage check of D-041 runs before the windows are placed); test support `Pipeline.Plan()`, `Pipeline.Simplifier(string name)`, `Pipeline.Floor(IPlanSimplifier)`, `Pipeline.Tolerances` (S4.2); `PlanTransform.Apply(IGeneratedPlan plan, double rotationDegrees, double translationX, double translationY)` (S4.2); `FacadeAttribution.Interval(WallSurface a, WallSurface b, ToleranceSettings tolerances) : (double Start, double End)?` (S4.2: where wall `b` lies along wall `a`); `Totals.Of(IEnumerable<Zone>, IReadOnlyList<Surface>, double orientationDegrees).GlazingByOrientation` (S3); `TextReport.Describe` (S2).
- Produces: *Semantic Merge*, *Perimeter Core*, and *Single Zone per Floor* give every target outdoor wall one centred window with the glazed area of the source windows it covers (D-079); *No Simplification* is unchanged. `CentredWindowTests.AssertCentredWindowsCarryTheCoveredGlazing(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces)` (internal test helper, reused in Task 4): for every target outdoor wall, the source windows whose centre lies on it give the expected glazed area; one window with that area, centred (offset = (length − width) / 2, sill = (height − window height) / 2, width / length = window height / height), or none when the area is zero.

- [x] **Step 1: Write the failing tests — create `tests/Lod.Integration.Tests/CentredWindowTests.cs` (full file)**

Ten tests: the three merging simplifiers on three placements of the canonical plan (unmoved; rotated 30° and moved by (5.3, −2.1) m; rotated 131.4° and moved by (15.08, −153.9) m, all through `PlanTransform`), each checked with `AssertCentredWindowsCarryTheCoveredGlazing` and with the glazing per orientation of the plan; and *No Simplification*, whose surface lines must equal the plan's.

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Plans;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Xunit;

namespace Lod.Integration.Tests;

/// <summary>Rebuilt walls carry one centred window with the glazed area of the source windows they cover (D-079, ADR-012).</summary>
public sealed class CentredWindowTests
{
    public static IEnumerable<object[]> MergingSimplifiers() =>
        from placement in new[] { (0.0, 0.0, 0.0), (30.0, 5.3, -2.1), (131.4, 15.08, -153.9) }
        from simplifier in new[] { "SemanticMerge", "PerimeterCore", "SingleZonePerFloor" }
        select new object[] { placement.Item1, placement.Item2, placement.Item3, simplifier };

    [Theory]
    [MemberData(nameof(MergingSimplifiers))]
    public void SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(double degrees, double x, double y, string simplifier)
    {
        IGeneratedPlan plan = PlanTransform.Apply(Pipeline.Plan(), degrees, x, y).Value;

        IFloor floor = Pipeline.Simplifier(simplifier).Simplify(plan).Value;

        AssertCentredWindowsCarryTheCoveredGlazing(plan.Surfaces, floor.Surfaces);
        Assert.Equal(
            Totals.Of(plan.Zones, plan.Surfaces, plan.OrientationDegrees).GlazingByOrientation.OrderBy(g => g.Key).Select(g => g.Value),
            Totals.Of(floor.Zones, floor.Surfaces, floor.OrientationDegrees).GlazingByOrientation.OrderBy(g => g.Key).Select(g => g.Value),
            new AreaComparer());
    }

    [Fact]
    public void NoSimplificationKeepsTheGeneratorWindows()
    {
        IGeneratedPlan plan = Pipeline.Plan();

        IFloor floor = new NoSimplification().Simplify(plan).Value;

        Assert.Equal(TextReport.Describe(plan).Split('\n').Where(l => l.StartsWith("surface ")), TextReport.Describe(floor).Split('\n').Where(l => l.StartsWith("surface ")));
    }

    /// <summary>
    /// Every target outdoor wall carries the glazed area of the source windows whose centre lies on it, as one window shaped by the generator's rule,
    /// or no window when that area is zero.
    /// </summary>
    internal static void AssertCentredWindowsCarryTheCoveredGlazing(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces)
    {
        WallSurface[] sources = Outdoor(sourceSurfaces).ToArray();
        WallSurface[] targets = Outdoor(targetSurfaces).ToArray();
        Assert.NotEmpty(targets);
        foreach (WallSurface wall in targets)
        {
            double expected = sources.Sum(source => FacadeAttribution.Interval(wall, source, Pipeline.Tolerances) is { } interval
                ? source.Windows.Where(w => interval.Start + w.Offset + (w.Width / 2.0) is var centre && centre > 0.0 && centre < wall.Length).Sum(w => w.Area)
                : 0.0);
            if (expected == 0.0)
            {
                Assert.Empty(wall.Windows);
                continue;
            }

            Window window = Assert.Single(wall.Windows);
            Assert.Equal(expected, window.Area, 9);
            Assert.Equal((wall.Length - window.Width) / 2.0, window.Offset, 9);
            Assert.Equal((wall.Height - window.Height) / 2.0, window.SillHeight, 9);
            Assert.Equal(window.Width / wall.Length, window.Height / wall.Height, 12);
        }
    }

    private static IEnumerable<WallSurface> Outdoor(IEnumerable<Surface> surfaces) =>
        surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors);

    private sealed class AreaComparer : IEqualityComparer<double>
    {
        public bool Equals(double x, double y) => Pipeline.Tolerances.AreaEquals(x, y);

        public int GetHashCode(double obj) => 0;
    }
}
```

- [x] **Step 2: Change the perimeter test — replace `tests/Lod.Integration.Tests/SimplifierTests.cs` (full file)**

Changes: `PerimeterSouthKeepsTheSouthFacadeWindowsInPlace` becomes `PerimeterSouthHasOneCentredWindowWithTheSouthFacadeGlazing`: the outdoor wall of `P-South` has one window of 1.2 + 9 + 9 = 19.2 m², centred on the 24 m × 3 m wall with the generator's proportions, instead of the three source windows at their offsets. The private `ToleranceComparer`, which only that test used, is removed. Every other test is unchanged.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Lod.Generators.Linear;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class SimplifierTests
{
    private const double PerimeterDepth = 4.57;

    [Fact]
    public void SemanticMergeJoinsConnectedZonesOfTheSameType()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.Equal(new[] { "Stair-1", "Corridor-1", "DwellingUnit-1", "DwellingUnit-2" }, floor.Zones.Select(z => z.Id.Value));
        Zone south = floor.Zones.Single(z => z.Id.Value == "DwellingUnit-1");
        Assert.Equal(160.0, south.FloorArea, 6);
        Assert.Equal(new[] { "US1", "US2" }, south.SourceZones.Select(s => s.Value));
        Assert.Equal(5.0, south.Program.Find(LoadType.Lighting, LoadBasis.PerFloorArea)!.Value, 9);
    }

    [Fact]
    public void MergedZonesLoseTheirSharedPartition()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.DoesNotContain(floor.Surfaces, s => s.Zone == s.AdjacentZone);
        Assert.Equal(2, floor.Surfaces.OfType<WallSurface>().Count(w => w.Zone.Value == "DwellingUnit-1" && w.Boundary == BoundaryCondition.Outdoors));
    }

    [Fact]
    public void PerimeterCoreHasFourPerimeterZonesAndACore()
    {
        IFloor floor = Pipeline.Floor(new PerimeterCore(Pipeline.Tolerances, PerimeterDepth));

        Assert.Equal(new[] { "P-North", "P-East", "P-South", "P-West", "CORE" }, floor.Zones.Select(z => z.Id.Value));
        Assert.Equal((24.0 - (2 * PerimeterDepth)) * (18.0 - (2 * PerimeterDepth)), floor.Zones.Single(z => z.Id.Value == "CORE").FloorArea, 6);
        Assert.DoesNotContain(floor.Surfaces.OfType<WallSurface>(), w => w.Zone.Value == "CORE" && w.Boundary == BoundaryCondition.Outdoors);
    }

    [Fact]
    public void PerimeterSouthHasOneCentredWindowWithTheSouthFacadeGlazing()
    {
        IFloor floor = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(Pipeline.Plan()).Value;

        WallSurface south = floor.Surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "P-South" && w.Boundary == BoundaryCondition.Outdoors);
        Window window = Assert.Single(south.Windows);
        Assert.Equal(1.2 + 9.0 + 9.0, window.Area, 9);
        Assert.Equal((24.0 - window.Width) / 2.0, window.Offset, 9);
        Assert.Equal((3.0 - window.Height) / 2.0, window.SillHeight, 9);
        Assert.Equal(window.Width / 24.0, window.Height / 3.0, 12);
    }

    [Fact]
    public void PerimeterDepthTooLargeIsAnError()
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, 10.0).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.PlanTooNarrow);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(-1.0)]
    public void NonPositivePerimeterDepthIsAnError(double depth)
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, depth).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.InvalidParameter);
    }

    [Fact]
    public void FootprintsWithHolesAreNotSupportedYet()
    {
        Polygon2 courtyard = Polygon2.Create(
            new[] { new Point2(0, 0), new Point2(30, 0), new Point2(30, 30), new Point2(0, 30) },
            new[] { new[] { new Point2(10, 10), new Point2(20, 10), new Point2(20, 20), new Point2(10, 20) } }).Value;
        var plan = new GeneratedPlan(courtyard, 3.0, 0.0, new Zone[0], new Surface[0], Provenance.Of("Test", new KeyValuePair<string, string>[0]));

        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(plan);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.NotSupported);
    }

    [Fact]
    public void SingleZonePerFloorHasOnlyOutdoorWalls()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Zone zone = Assert.Single(floor.Zones);
        Assert.Equal(SpaceType.Mixed, zone.SpaceType);
        Assert.Equal(6, zone.SourceZones.Count);
        Assert.All(floor.Surfaces.OfType<WallSurface>(), w => Assert.Equal(BoundaryCondition.Outdoors, w.Boundary));
        Assert.Equal(4, floor.Surfaces.OfType<WallSurface>().Count());
    }

    [Fact]
    public void SetpointsAreFloorAreaWeightedAndRecorded()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Thermostat thermostat = floor.Zones[0].Program.Thermostat!;
        Assert.Equal(21.0, thermostat.HeatingSetpoint[0], 9);
        Assert.Equal(Lod.Core.Aggregation.AggregationMethod.FloorAreaWeighted, thermostat.HeatingSetpoint.Aggregation!.Method);
        Assert.DoesNotContain(new ZoneId("ST"), thermostat.HeatingSetpoint.Aggregation.Sources);
        Assert.Equal(5, thermostat.HeatingSetpoint.Aggregation.Sources.Count);
    }

    [Theory]
    [InlineData("SemanticMerge", 1)]
    [InlineData("SemanticMerge", 2)]
    [InlineData("SemanticMerge", 3)]
    [InlineData("PerimeterCore", 1)]
    [InlineData("PerimeterCore", 2)]
    [InlineData("PerimeterCore", 3)]
    [InlineData("PerimeterCore", 4)]
    [InlineData("SingleZonePerFloor", 1)]
    [InlineData("SingleZonePerFloor", 2)]
    public void EverySimplifierSatisfiesTheInvariantsForRandomPlans(string simplifier, int seed)
    {
        LinearPlanParameters parameters = RandomParameters(new Random(seed));

        IFloor floor = Simplifier(simplifier).Simplify(Pipeline.Plan(parameters)).Value;
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(floor);

        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported()
    {
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances)));

        CheckResult conditioned = report.Checks.Single(c => c.Check == "ConditionedFloorArea");
        Assert.False(conditioned.Passed);
        Assert.False(conditioned.Enforced);
        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void ValidationCatchesAnUncoveredFacade()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Surface[] withoutSouthWall = floor.Surfaces.Where(s => !(s is WallSurface w && w.Start.Y == 0.0 && w.End.Y == 0.0)).ToArray();
        var broken = new Floor(floor.Source, floor.Zones, withoutSouthWall, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.Contains(report.Checks, c => c.Check == "FacadeCoverage" && !c.Passed && c.Enforced);
        Assert.False(report.Passed);
    }

    [Fact]
    public void NoSimplificationPassesValidation()
    {
        Assert.True(new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.DetailedFloor()).Passed);
    }

    [Fact]
    public void ValidationCatchesAChangedProgram()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Zone zone = floor.Zones[0];
        var tampered = new Zone(zone.Id, zone.Name, zone.SpaceType, zone.Parts, ExampleResidentialPresets.DwellingUnit.Program, zone.SourceZones);
        var broken = new Floor(floor.Source, new[] { tampered }, floor.Surfaces, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.False(report.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Installed.Lighting" && !c.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Traceability" && !c.Passed);
    }

    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void SimplifiersAreDeterministic(string simplifier)
    {
        Assert.Equal(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))));
    }

    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void CanonicalSnapshots(string simplifier)
    {
        Snapshot.Match(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), $"simplifier-{simplifier}");
    }

    private static IPlanSimplifier Simplifier(string name) => name switch
    {
        "SemanticMerge" => new SemanticMerge(Pipeline.Tolerances),
        "PerimeterCore" => new PerimeterCore(Pipeline.Tolerances, PerimeterDepth),
        "SingleZonePerFloor" => new SingleZonePerFloor(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown simplifier."),
    };

    private static LinearPlanParameters RandomParameters(Random random) => new(
        Length: 18.0 + (random.NextDouble() * 42.0),
        UnitDepth: 6.0 + (random.NextDouble() * 4.0),
        CorridorWidth: 1.5 + (random.NextDouble() * 1.5),
        TargetUnitWidth: 5.0 + (random.NextDouble() * 7.0),
        StairLength: 3.0 + (random.NextDouble() * 3.0),
        FloorHeight: 2.8 + (random.NextDouble() * 0.7),
        OrientationDegrees: random.NextDouble() * 360.0);
}
```

- [x] **Step 3: Run the tests and see them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.CentredWindowTests|FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected on net8.0 (29 `SimplifierTests` and 10 `CentredWindowTests`; the *No Simplification* test and every other simplifier test already pass):

```text
Failed!  - Failed:    10, Passed:    29, Skipped:     0, Total:    39, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

with the failing tests and the first lines of their messages, in any order; each `Assert.Single()` message continues with a `Collection:` line that lists the windows still kept in place:

```text
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 0, x: 0, y: 0, simplifier: "SemanticMerge")
  Assert.Single() Failure: The collection contained 2 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 0, x: 0, y: 0, simplifier: "PerimeterCore")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 0, x: 0, y: 0, simplifier: "SingleZonePerFloor")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "SemanticMerge")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 1.367544568 (rounded from 1.3675445675866009)
  Actual:   1.367544667 (rounded from 1.3675446672068996)
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "PerimeterCore")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "SingleZonePerFloor")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "SemanticMerge")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 1.367544211 (rounded from 1.3675442109753764)
  Actual:   1.367544468 (rounded from 1.367544467966324)
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "PerimeterCore")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "SingleZonePerFloor")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.SimplifierTests.PerimeterSouthHasOneCentredWindowWithTheSouthFacadeGlazing
  Assert.Single() Failure: The collection contained 3 items
```

The two `Assert.Equal()` failures are *Semantic Merge* on rotated plans: there the stair's walls are rebuilt one to one, so they keep a single window, but in place, which on a rebuilt rotated wall is off-centre by 1e-7 to 3e-7 m (grid rounding of the rebuilt wall); the centring check works to 9 decimal places.

- [x] **Step 4: Implement — replace `src/Lod.Core/Simplification/PlanSimplifier.cs` (full file)**

`Simplify` calls `CentredWindows.Place` where it called `WindowRehosting.Rehost`, after the façade-coverage check; the class summary names the rule.

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Simplification;

/// <summary>A target zone proposed by a simplification strategy.</summary>
/// <param name="Id">Zone ID.</param>
/// <param name="Name">Display name.</param>
/// <param name="SpaceType">Space type, <see cref="SpaceType.Mixed"/> when the target combines several types.</param>
/// <param name="Footprint">Zone polygon.</param>
public sealed record TargetZone(ZoneId Id, string Name, SpaceType SpaceType, Polygon2 Footprint);

/// <summary>
/// Shared simplification pipeline (S3). A strategy only proposes target footprints; this class maps sources to targets, rebuilds surfaces
/// (partitions between merged sources disappear, D-034), checks that the target façades cover every source façade (D-041), gives every target
/// outdoor wall one centred window with the glazed area of the source windows it covers (D-079, <see cref="CentredWindows"/>), and aggregates
/// programs (ADR-005, ADR-007, D-038).
/// </summary>
public abstract class PlanSimplifier : IPlanSimplifier
{
    /// <summary>Initialises the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    protected PlanSimplifier(ToleranceSettings tolerances)
    {
        Tolerances = tolerances;
    }

    /// <summary>Operation name recorded in provenance.</summary>
    public abstract string Name { get; }

    /// <summary>Tolerances.</summary>
    protected ToleranceSettings Tolerances { get; }

    /// <inheritdoc />
    public Result<IFloor> Simplify(IGeneratedPlan plan)
    {
        Result<IReadOnlyList<TargetZone>> proposed = ProposeZones(plan);
        if (!proposed.IsSuccess)
        {
            return Result.Failure<IFloor>(proposed.Diagnostics);
        }

        IReadOnlyList<TargetZone> targets = proposed.Value;
        Result<IReadOnlyList<Surface>> built = new LayoutSurfaceBuilder(Tolerances)
            .Build(plan.Footprint, targets.Select(t => new LayoutZone(t.Id, t.Footprint)).ToArray(), plan.FloorHeight);
        if (!built.IsSuccess)
        {
            return Result.Failure<IFloor>(built.Diagnostics);
        }

        IReadOnlyList<ZoneMapping> mapping = new OverlapMapper(Tolerances).Map(plan.Zones, targets.Select(t => (t.Id, t.Footprint)).ToArray());
        TransferMatrix matrix = TransferMatrix.FromMapping(mapping);
        FacadeAttribution facade = FacadeAttribution.Compute(plan.Surfaces, built.Value, Tolerances);
        Diagnostic[] gaps = facade.CoverageGaps()
            .Select(g => Diagnostic.Error(
                DiagnosticCodes.FacadeNotCovered,
                $"Target façades cover {g.CoveredLength:0.######} m of this {g.Wall.Length:0.######} m wall (D-041).",
                g.Wall.Id.Value))
            .ToArray();
        if (gaps.Length > 0)
        {
            return Result.Failure<IFloor>(gaps);
        }

        Result<IReadOnlyList<Surface>> glazed = CentredWindows.Place(plan.Surfaces, built.Value, Tolerances);
        if (!glazed.IsSuccess)
        {
            return Result.Failure<IFloor>(glazed.Diagnostics);
        }

        IReadOnlyList<Surface> surfaces = glazed.Value;
        var diagnostics = new List<Diagnostic>(proposed.Diagnostics);
        var aggregator = new EquivalentPropertyAggregator(Tolerances);
        var zones = new List<Zone>();
        foreach (TargetZone target in targets)
        {
            var part = new ZonePart(target.Footprint, 0.0, plan.FloorHeight);
            var targetMeasures = new ZoneMeasures(part.Footprint.Area, part.Volume, LayoutMeasures.ExteriorWallArea(target.Id, surfaces));
            SourceZoneContribution[] contributions = plan.Zones
                .Select(s => new SourceZoneContribution(
                    s.Id,
                    s.Program,
                    LayoutMeasures.Of(s, plan.Surfaces),
                    matrix.AreaFraction(s.Id, target.Id),
                    facade.ExteriorWallFraction(s.Id, target.Id)))
                .Where(c => c.AreaFraction > 0.0 || c.ExteriorWallFraction > 0.0)
                .ToArray();
            Result<ZoneProgram> program = aggregator.Aggregate(target.Id, targetMeasures, contributions);
            diagnostics.AddRange(program.Diagnostics);
            if (program.IsSuccess)
            {
                zones.Add(new Zone(target.Id, target.Name, target.SpaceType, new[] { part }, program.Value, contributions.Select(c => c.Zone)));
            }
        }

        var provenance = Provenance.Of(Name, Describe(), plan.Provenance);
        return Result.FromDiagnostics<IFloor>(() => new Floor(plan, zones, surfaces, mapping, provenance), diagnostics);
    }

    /// <summary>Proposes target zones tiling the plan footprint.</summary>
    /// <param name="plan">The detailed plan.</param>
    /// <returns>Target zones, or errors.</returns>
    protected abstract Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan);

    /// <summary>Strategy parameters for provenance.</summary>
    /// <returns>Key-value pairs.</returns>
    protected abstract IEnumerable<KeyValuePair<string, string>> Describe();
}
```

- [x] **Step 5: Run the integration tests and see the snapshots fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected on net8.0:

```text
Failed!  - Failed:     4, Passed:   169, Skipped:     0, Total:   173, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

with the failing tests and their messages, in any order:

```text
Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "SemanticMerge")
  Snapshot 'simplifier-SemanticMerge' is missing or differs. Review Snapshots/simplifier-SemanticMerge.received.txt and rename it to simplifier-SemanticMerge.txt to accept.
Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "PerimeterCore")
  Snapshot 'simplifier-PerimeterCore' is missing or differs. Review Snapshots/simplifier-PerimeterCore.received.txt and rename it to simplifier-PerimeterCore.txt to accept.
Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "SingleZonePerFloor")
  Snapshot 'simplifier-SingleZonePerFloor' is missing or differs. Review Snapshots/simplifier-SingleZonePerFloor.received.txt and rename it to simplifier-SingleZonePerFloor.txt to accept.
Failed Lod.Integration.Tests.AggregatorTests.MultiplierSnapshot
  Snapshot 'aggregator-StackedFloorZoneMultiplier' is missing or differs. Review Snapshots/aggregator-StackedFloorZoneMultiplier.received.txt and rename it to aggregator-StackedFloorZoneMultiplier.txt to accept.
```

and the four files `tests/Lod.Integration.Tests/Snapshots/*.received.txt` (git-ignored by `*.received.*`). `MultiplierSnapshot` fails although the zone multiplier rebuilds no wall: it stacks the *Perimeter Core* floor, whose windows changed.

- [x] **Step 6: Review and accept the received files**

Review each received file against Step 7; it must be identical. Only `window(…)` entries of outdoor walls change, each wall going from several windows to one; every other line, including `glazing=` of every wall, is byte-identical:

- `simplifier-SemanticMerge`: lines 39 (`DwellingUnit-1/W4`) and 43 (`DwellingUnit-2/W2`), two windows of 9 m² → one 18 m² window on the 20 m × 3 m wall, `window(offset=4.522774 sill=0.678416 10.954451x1.643168)`.
- `simplifier-PerimeterCore`: lines 32 (`P-North/W1`), 41 (`P-East/W4`), and 46 (`P-South/W3`), three windows → one: north and south 19.2 m² on 72 m², `window(offset=5.803227 sill=0.725403 12.393547x1.549193)`; east 15.6 m² on 54 m², `window(offset=4.162645 sill=0.693774 9.674709x1.612452)`. `P-West` (one source window, 5.4 m²) and the core (no window) are unchanged.
- `simplifier-SingleZonePerFloor`: lines 8–10 (`FLOOR/W1`, `W2`, `W3`), three windows → one, with the north, east, and south windows of *Perimeter Core*.
- `aggregator-StackedFloorZoneMultiplier`: lines 92, 99, 102, 112, 119, 122, 132, 139, and 142 (`P-North/W1`, `P-East/W4`, `P-South/W3` of the modelled storeys `L0`, `L2`, and `L3`), the same windows as `simplifier-PerimeterCore`.

Accept the files, then check that only window entries changed:

```powershell
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/aggregator-StackedFloorZoneMultiplier.received.txt tests/Lod.Integration.Tests/Snapshots/aggregator-StackedFloorZoneMultiplier.txt
```

```bash
git diff --numstat -- tests/Lod.Integration.Tests/Snapshots
git diff -U0 -- tests/Lod.Integration.Tests/Snapshots | grep -c -E '^[-+][a-z]'
git diff -U0 -- tests/Lod.Integration.Tests/Snapshots | grep -E '^[-+][a-z]' | sed -E 's/ window\([^)]*\)//g; s/^[-+]//' | sort | uniq -u
```

Expected: the numstat lines `9	9	…/aggregator-StackedFloorZoneMultiplier.txt`, `3	3	…/simplifier-PerimeterCore.txt`, `2	2	…/simplifier-SemanticMerge.txt`, and `3	3	…/simplifier-SingleZonePerFloor.txt`; the count `34`; and no output from the last command (with the window entries removed, every changed line equals the line it replaces).

- [x] **Step 7: Expected content of the four snapshots**

`tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone Stair-1 Stair "Stair 1" area=72.000000 volume=216.000000 parts=1 multiplier=1 sources=[ST]
  load Lighting PerFloorArea value=3.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  unconditioned
zone Corridor-1 Corridor "Corridor 1" area=40.000000 volume=120.000000 parts=1 multiplier=1 sources=[CO]
  load Lighting PerFloorArea value=5.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone DwellingUnit-1 DwellingUnit "DwellingUnit 1" area=160.000000 volume=480.000000 parts=1 multiplier=1 sources=[US1,US2]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone DwellingUnit-2 DwellingUnit "DwellingUnit 2" area=160.000000 volume=480.000000 parts=1 multiplier=1 sources=[UN1,UN2]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface Stair-1/W1 Outdoors area=12.000000 wall (4.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface Stair-1/W2 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface Stair-1/W3 Outdoors area=12.000000 wall (0.000000,0.000000)-(4.000000,0.000000) z=0.000000 facing=South glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface Stair-1/W4 Interzone adjacent=DwellingUnit-1 area=24.000000 wall (4.000000,0.000000)-(4.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/W5 Interzone adjacent=Corridor-1 area=6.000000 wall (4.000000,8.000000)-(4.000000,10.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/W6 Interzone adjacent=DwellingUnit-2 area=24.000000 wall (4.000000,10.000000)-(4.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/F Unresolved area=72.000000 Floor z=0.000000
surface Stair-1/C Unresolved area=72.000000 Ceiling z=3.000000
surface Corridor-1/W1 Interzone adjacent=DwellingUnit-2 area=60.000000 wall (24.000000,10.000000)-(4.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface Corridor-1/W2 Interzone adjacent=Stair-1 area=6.000000 wall (4.000000,10.000000)-(4.000000,8.000000) z=0.000000 facing=West glazing=0.000000
surface Corridor-1/W3 Interzone adjacent=DwellingUnit-1 area=60.000000 wall (4.000000,8.000000)-(24.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface Corridor-1/W4 Outdoors area=6.000000 wall (24.000000,8.000000)-(24.000000,10.000000) z=0.000000 facing=East glazing=1.200000 window(offset=0.552786 sill=0.829180 0.894427x1.341641)
surface Corridor-1/F Unresolved area=40.000000 Floor z=0.000000
surface Corridor-1/C Unresolved area=40.000000 Ceiling z=3.000000
surface DwellingUnit-1/W1 Outdoors area=24.000000 wall (24.000000,0.000000)-(24.000000,8.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface DwellingUnit-1/W2 Interzone adjacent=Corridor-1 area=60.000000 wall (24.000000,8.000000)-(4.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface DwellingUnit-1/W3 Interzone adjacent=Stair-1 area=24.000000 wall (4.000000,8.000000)-(4.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface DwellingUnit-1/W4 Outdoors area=60.000000 wall (4.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=18.000000 window(offset=4.522774 sill=0.678416 10.954451x1.643168)
surface DwellingUnit-1/F Unresolved area=160.000000 Floor z=0.000000
surface DwellingUnit-1/C Unresolved area=160.000000 Ceiling z=3.000000
surface DwellingUnit-2/W1 Outdoors area=24.000000 wall (24.000000,10.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface DwellingUnit-2/W2 Outdoors area=60.000000 wall (24.000000,18.000000)-(4.000000,18.000000) z=0.000000 facing=North glazing=18.000000 window(offset=4.522774 sill=0.678416 10.954451x1.643168)
surface DwellingUnit-2/W3 Interzone adjacent=Stair-1 area=24.000000 wall (4.000000,18.000000)-(4.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface DwellingUnit-2/W4 Interzone adjacent=Corridor-1 area=60.000000 wall (4.000000,10.000000)-(24.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface DwellingUnit-2/F Unresolved area=160.000000 Floor z=0.000000
surface DwellingUnit-2/C Unresolved area=160.000000 Ceiling z=3.000000
```

`tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone P-North Mixed "Perimeter North" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,UN1,UN2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-East Mixed "Perimeter East" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[CO,US2,UN2]
  load Occupancy PerFloorArea value=0.025532 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=3541.009233
  load ElectricEquipment PerFloorArea value=4.255398 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-South Mixed "Perimeter South" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,US1,US2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-West Mixed "Perimeter West" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[ST,CO,US1,UN1]
  load Occupancy PerFloorArea value=0.002070 annual=6391.400000
  load Lighting PerFloorArea value=3.175156 annual=8093.664821
  load ElectricEquipment PerFloorArea value=0.345018 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone CORE Mixed "Core" area=131.659600 volume=394.978800 parts=1 multiplier=1 sources=[CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.023228 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=4012.043792
  load ElectricEquipment PerFloorArea value=3.871332 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface P-North/W2 Interzone adjacent=P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=0.000000 facing=West glazing=0.000000
surface P-North/W3 Interzone adjacent=CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=0.000000 facing=South glazing=0.000000
surface P-North/W4 Interzone adjacent=P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=0.000000 facing=South glazing=0.000000
surface P-North/F Unresolved area=88.795100 Floor z=0.000000
surface P-North/C Unresolved area=88.795100 Ceiling z=3.000000
surface P-East/W1 Interzone adjacent=P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=0.000000 facing=North glazing=0.000000
surface P-East/W2 Interzone adjacent=CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=0.000000 facing=West glazing=0.000000
surface P-East/W3 Interzone adjacent=P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface P-East/F Unresolved area=61.375100 Floor z=0.000000
surface P-East/C Unresolved area=61.375100 Ceiling z=3.000000
surface P-South/W1 Interzone adjacent=CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=0.000000 facing=North glazing=0.000000
surface P-South/W2 Interzone adjacent=P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=0.000000 facing=North glazing=0.000000
surface P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface P-South/W4 Interzone adjacent=P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=0.000000 facing=North glazing=0.000000
surface P-South/F Unresolved area=88.795100 Floor z=0.000000
surface P-South/C Unresolved area=88.795100 Ceiling z=3.000000
surface P-West/W1 Interzone adjacent=CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=0.000000 facing=East glazing=0.000000
surface P-West/W2 Interzone adjacent=P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface P-West/W4 Interzone adjacent=P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=0.000000 facing=South glazing=0.000000
surface P-West/F Unresolved area=61.375100 Floor z=0.000000
surface P-West/C Unresolved area=61.375100 Ceiling z=3.000000
surface CORE/W1 Interzone adjacent=P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=0.000000 facing=South glazing=0.000000
surface CORE/W2 Interzone adjacent=P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=0.000000 facing=East glazing=0.000000
surface CORE/W3 Interzone adjacent=P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=0.000000 facing=North glazing=0.000000
surface CORE/W4 Interzone adjacent=P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=0.000000 facing=West glazing=0.000000
surface CORE/F Unresolved area=131.659600 Floor z=0.000000
surface CORE/C Unresolved area=131.659600 Ceiling z=3.000000
```

`tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone FLOOR Mixed "Floor" area=432.000000 volume=1296.000000 parts=1 multiplier=1 sources=[ST,CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface FLOOR/W1 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface FLOOR/W2 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface FLOOR/W3 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface FLOOR/W4 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface FLOOR/F Unresolved area=432.000000 Floor z=0.000000
surface FLOOR/C Unresolved area=432.000000 Ceiling z=3.000000
```

`tests/Lod.Integration.Tests/Snapshots/aggregator-StackedFloorZoneMultiplier.txt`:

```text
building orientation=0.000000 sources=1,2,1
zone L0/P-North Mixed "Perimeter North" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,UN1,UN2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/P-East Mixed "Perimeter East" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[CO,US2,UN2]
  load Occupancy PerFloorArea value=0.025532 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=3541.009233
  load ElectricEquipment PerFloorArea value=4.255398 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/P-South Mixed "Perimeter South" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,US1,US2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/P-West Mixed "Perimeter West" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[ST,CO,US1,UN1]
  load Occupancy PerFloorArea value=0.002070 annual=6391.400000
  load Lighting PerFloorArea value=3.175156 annual=8093.664821
  load ElectricEquipment PerFloorArea value=0.345018 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/CORE Mixed "Core" area=131.659600 volume=394.978800 parts=1 multiplier=1 sources=[CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.023228 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=4012.043792
  load ElectricEquipment PerFloorArea value=3.871332 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L2/P-North Mixed "Perimeter North" area=88.795100 volume=266.385300 parts=1 multiplier=2 sources=[ST,UN1,UN2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L2/P-East Mixed "Perimeter East" area=61.375100 volume=184.125300 parts=1 multiplier=2 sources=[CO,US2,UN2]
  load Occupancy PerFloorArea value=0.025532 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=3541.009233
  load ElectricEquipment PerFloorArea value=4.255398 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L2/P-South Mixed "Perimeter South" area=88.795100 volume=266.385300 parts=1 multiplier=2 sources=[ST,US1,US2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L2/P-West Mixed "Perimeter West" area=61.375100 volume=184.125300 parts=1 multiplier=2 sources=[ST,CO,US1,UN1]
  load Occupancy PerFloorArea value=0.002070 annual=6391.400000
  load Lighting PerFloorArea value=3.175156 annual=8093.664821
  load ElectricEquipment PerFloorArea value=0.345018 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L2/CORE Mixed "Core" area=131.659600 volume=394.978800 parts=1 multiplier=2 sources=[CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.023228 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=4012.043792
  load ElectricEquipment PerFloorArea value=3.871332 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L3/P-North Mixed "Perimeter North" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,UN1,UN2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L3/P-East Mixed "Perimeter East" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[CO,US2,UN2]
  load Occupancy PerFloorArea value=0.025532 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=3541.009233
  load ElectricEquipment PerFloorArea value=4.255398 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L3/P-South Mixed "Perimeter South" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,US1,US2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L3/P-West Mixed "Perimeter West" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[ST,CO,US1,UN1]
  load Occupancy PerFloorArea value=0.002070 annual=6391.400000
  load Lighting PerFloorArea value=3.175156 annual=8093.664821
  load ElectricEquipment PerFloorArea value=0.345018 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L3/CORE Mixed "Core" area=131.659600 volume=394.978800 parts=1 multiplier=1 sources=[CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.023228 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=4012.043792
  load ElectricEquipment PerFloorArea value=3.871332 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface L0/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L0/P-North/W2 Interzone adjacent=L0/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=0.000000 facing=West glazing=0.000000
surface L0/P-North/W3 Interzone adjacent=L0/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=0.000000 facing=South glazing=0.000000
surface L0/P-North/W4 Interzone adjacent=L0/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=0.000000 facing=South glazing=0.000000
surface L0/P-East/W1 Interzone adjacent=L0/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=0.000000 facing=North glazing=0.000000
surface L0/P-East/W2 Interzone adjacent=L0/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=0.000000 facing=West glazing=0.000000
surface L0/P-East/W3 Interzone adjacent=L0/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface L0/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface L0/P-South/W1 Interzone adjacent=L0/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=0.000000 facing=North glazing=0.000000
surface L0/P-South/W2 Interzone adjacent=L0/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=0.000000 facing=North glazing=0.000000
surface L0/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L0/P-South/W4 Interzone adjacent=L0/P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=0.000000 facing=North glazing=0.000000
surface L0/P-West/W1 Interzone adjacent=L0/CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=0.000000 facing=East glazing=0.000000
surface L0/P-West/W2 Interzone adjacent=L0/P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface L0/P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L0/P-West/W4 Interzone adjacent=L0/P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=0.000000 facing=South glazing=0.000000
surface L0/CORE/W1 Interzone adjacent=L0/P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=0.000000 facing=South glazing=0.000000
surface L0/CORE/W2 Interzone adjacent=L0/P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=0.000000 facing=East glazing=0.000000
surface L0/CORE/W3 Interzone adjacent=L0/P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=0.000000 facing=North glazing=0.000000
surface L0/CORE/W4 Interzone adjacent=L0/P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=0.000000 facing=West glazing=0.000000
surface L2/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=6.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L2/P-North/W2 Interzone adjacent=L2/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=6.000000 facing=West glazing=0.000000
surface L2/P-North/W3 Interzone adjacent=L2/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=6.000000 facing=South glazing=0.000000
surface L2/P-North/W4 Interzone adjacent=L2/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=6.000000 facing=South glazing=0.000000
surface L2/P-East/W1 Interzone adjacent=L2/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=6.000000 facing=North glazing=0.000000
surface L2/P-East/W2 Interzone adjacent=L2/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=6.000000 facing=West glazing=0.000000
surface L2/P-East/W3 Interzone adjacent=L2/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=6.000000 facing=West glazing=0.000000
surface L2/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=6.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface L2/P-South/W1 Interzone adjacent=L2/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=6.000000 facing=North glazing=0.000000
surface L2/P-South/W2 Interzone adjacent=L2/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=6.000000 facing=North glazing=0.000000
surface L2/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=6.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L2/P-South/W4 Interzone adjacent=L2/P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=6.000000 facing=North glazing=0.000000
surface L2/P-West/W1 Interzone adjacent=L2/CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=6.000000 facing=East glazing=0.000000
surface L2/P-West/W2 Interzone adjacent=L2/P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=6.000000 facing=East glazing=0.000000
surface L2/P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=6.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L2/P-West/W4 Interzone adjacent=L2/P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=6.000000 facing=South glazing=0.000000
surface L2/CORE/W1 Interzone adjacent=L2/P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=6.000000 facing=South glazing=0.000000
surface L2/CORE/W2 Interzone adjacent=L2/P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=6.000000 facing=East glazing=0.000000
surface L2/CORE/W3 Interzone adjacent=L2/P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=6.000000 facing=North glazing=0.000000
surface L2/CORE/W4 Interzone adjacent=L2/P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=6.000000 facing=West glazing=0.000000
surface L3/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=9.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L3/P-North/W2 Interzone adjacent=L3/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=9.000000 facing=West glazing=0.000000
surface L3/P-North/W3 Interzone adjacent=L3/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=9.000000 facing=South glazing=0.000000
surface L3/P-North/W4 Interzone adjacent=L3/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=9.000000 facing=South glazing=0.000000
surface L3/P-East/W1 Interzone adjacent=L3/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=9.000000 facing=North glazing=0.000000
surface L3/P-East/W2 Interzone adjacent=L3/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=9.000000 facing=West glazing=0.000000
surface L3/P-East/W3 Interzone adjacent=L3/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=9.000000 facing=West glazing=0.000000
surface L3/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=9.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface L3/P-South/W1 Interzone adjacent=L3/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=9.000000 facing=North glazing=0.000000
surface L3/P-South/W2 Interzone adjacent=L3/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=9.000000 facing=North glazing=0.000000
surface L3/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=9.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L3/P-South/W4 Interzone adjacent=L3/P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=9.000000 facing=North glazing=0.000000
surface L3/P-West/W1 Interzone adjacent=L3/CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=9.000000 facing=East glazing=0.000000
surface L3/P-West/W2 Interzone adjacent=L3/P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=9.000000 facing=East glazing=0.000000
surface L3/P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=9.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L3/P-West/W4 Interzone adjacent=L3/P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=9.000000 facing=South glazing=0.000000
surface L3/CORE/W1 Interzone adjacent=L3/P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=9.000000 facing=South glazing=0.000000
surface L3/CORE/W2 Interzone adjacent=L3/P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=9.000000 facing=East glazing=0.000000
surface L3/CORE/W3 Interzone adjacent=L3/P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=9.000000 facing=North glazing=0.000000
surface L3/CORE/W4 Interzone adjacent=L3/P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=9.000000 facing=West glazing=0.000000
surface L0/P-North/F1 Ground area=88.795100 Floor z=0.000000
surface L0/P-North/C1 Adiabatic area=88.795100 Ceiling z=3.000000
surface L0/P-East/F1 Ground area=61.375100 Floor z=0.000000
surface L0/P-East/C1 Adiabatic area=61.375100 Ceiling z=3.000000
surface L0/P-South/F1 Ground area=88.795100 Floor z=0.000000
surface L0/P-South/C1 Adiabatic area=88.795100 Ceiling z=3.000000
surface L0/P-West/F1 Ground area=61.375100 Floor z=0.000000
surface L0/P-West/C1 Adiabatic area=61.375100 Ceiling z=3.000000
surface L0/CORE/F1 Ground area=131.659600 Floor z=0.000000
surface L0/CORE/C1 Adiabatic area=131.659600 Ceiling z=3.000000
surface L2/P-North/F1 Adiabatic area=88.795100 Floor z=6.000000
surface L2/P-North/C1 Adiabatic area=88.795100 Ceiling z=9.000000
surface L2/P-East/F1 Adiabatic area=61.375100 Floor z=6.000000
surface L2/P-East/C1 Adiabatic area=61.375100 Ceiling z=9.000000
surface L2/P-South/F1 Adiabatic area=88.795100 Floor z=6.000000
surface L2/P-South/C1 Adiabatic area=88.795100 Ceiling z=9.000000
surface L2/P-West/F1 Adiabatic area=61.375100 Floor z=6.000000
surface L2/P-West/C1 Adiabatic area=61.375100 Ceiling z=9.000000
surface L2/CORE/F1 Adiabatic area=131.659600 Floor z=6.000000
surface L2/CORE/C1 Adiabatic area=131.659600 Ceiling z=9.000000
surface L3/P-North/F1 Adiabatic area=88.795100 Floor z=9.000000
surface L3/P-North/C1 Outdoors area=88.795100 Ceiling z=12.000000
surface L3/P-East/F1 Adiabatic area=61.375100 Floor z=9.000000
surface L3/P-East/C1 Outdoors area=61.375100 Ceiling z=12.000000
surface L3/P-South/F1 Adiabatic area=88.795100 Floor z=9.000000
surface L3/P-South/C1 Outdoors area=88.795100 Ceiling z=12.000000
surface L3/P-West/F1 Adiabatic area=61.375100 Floor z=9.000000
surface L3/P-West/C1 Outdoors area=61.375100 Ceiling z=12.000000
surface L3/CORE/F1 Adiabatic area=131.659600 Floor z=9.000000
surface L3/CORE/C1 Outdoors area=131.659600 Ceiling z=12.000000
```

- [x] **Step 8: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
dotnet test BEMGen.sln -c Release
git status --short
```

Expected:

```text
Passed!  - Failed:     0, Passed:   173, Skipped:     0, Total:   173, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

and on net8.0:

```text
Passed!  - Failed:     0, Passed:   142, Skipped:     0, Total:   142, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    19, Skipped:     0, Total:    19, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:   173, Skipped:     0, Total:   173, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

`git status --short` lists `PlanSimplifier.cs`, `SimplifierTests.cs`, and the four snapshots as modified and `CentredWindowTests.cs` as new; no `*.received.txt`. `linear-plan-canonical.txt`, `stack-two-storeys.txt`, and the two single-zone aggregator snapshots are unchanged (Task 4 changes the latter).

- [x] **Step 9: Commit**

```bash
git add src/Lod.Core/Simplification/PlanSimplifier.cs tests/Lod.Integration.Tests/CentredWindowTests.cs tests/Lod.Integration.Tests/SimplifierTests.cs tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt tests/Lod.Integration.Tests/Snapshots/aggregator-StackedFloorZoneMultiplier.txt
git commit -m "feature(simplifiers): give every rebuilt outdoor wall one centred window"
```

### Task 4: Single-zone floor aggregators give every rebuilt storey wall one centred window

**Files:**
- Modify: `src/Lod.Core/Buildings/SingleZoneMerge.cs`, `src/Lod.Core/Buildings/SingleZoneBuilding.cs`, `src/Lod.Core/Buildings/SingleZonePerFloorType.cs` (S4.2 files)
- Test: modify `tests/Lod.Integration.Tests/CentredWindowTests.cs` (Task 3), `tests/Lod.Integration.Tests/AggregatorTests.cs` (S4 file, last changed in S4.2)
- Snapshots: modify `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.txt`, `aggregator-SingleZonePerFloorType.txt` (S4.2 files)

**Interfaces:**
- Consumes: `CentredWindows.Place` (Task 2); `SingleZoneMerge.Merge(string operation, IReadOnlyList<FloorEntry> floors, Func<int, MergedZone> zoneOfEntry, ToleranceSettings tolerances)` (S4.2, internal; rebuilds the outdoor walls per storey outline and checks façade coverage against the stacked walls); `FloorEntry(IFloor Floor, int Multiplier)`, `Stack` (S2), `Pipeline.Aggregator(string name)`, `Pipeline.DetailedFloor()` (S4.2); `CentredWindowTests.AssertCentredWindowsCarryTheCoveredGlazing` (Task 3).
- Produces: *Single Zone per Floor Type* and *Single Zone Building* give every rebuilt storey wall one centred window with the glazed area of the stacked source windows it covers (D-079); *Stack Floors* and *Stacked Floor Zone Multiplier* keep their floors' windows.

- [x] **Step 1: Write the failing tests — replace `tests/Lod.Integration.Tests/CentredWindowTests.cs` (full file)**

Changes: 14 tests added. `MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover` (12 cases): the *No Simplification* and *Perimeter Core* floors of the three placements of Task 3, given three times with multipliers 1, 3, 1 to each single-zone aggregator, checked against the walls of `Stack` on the same entries; `AggregatorsThatDoNotRebuildWallsKeepTheFloorWindows` (2 cases): every storey of `Stack` and `StackedFloorZoneMultiplier` carries exactly the floor's windows, wall by wall.

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Plans;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Xunit;

namespace Lod.Integration.Tests;

/// <summary>Rebuilt walls carry one centred window with the glazed area of the source windows they cover (D-079, ADR-012).</summary>
public sealed class CentredWindowTests
{
    public static IEnumerable<object[]> MergingSimplifiers() =>
        from placement in new[] { (0.0, 0.0, 0.0), (30.0, 5.3, -2.1), (131.4, 15.08, -153.9) }
        from simplifier in new[] { "SemanticMerge", "PerimeterCore", "SingleZonePerFloor" }
        select new object[] { placement.Item1, placement.Item2, placement.Item3, simplifier };

    [Theory]
    [MemberData(nameof(MergingSimplifiers))]
    public void SimplifiedWallsCarryOneCentredWindowWithTheGlazingTheyCover(double degrees, double x, double y, string simplifier)
    {
        IGeneratedPlan plan = PlanTransform.Apply(Pipeline.Plan(), degrees, x, y).Value;

        IFloor floor = Pipeline.Simplifier(simplifier).Simplify(plan).Value;

        AssertCentredWindowsCarryTheCoveredGlazing(plan.Surfaces, floor.Surfaces);
        Assert.Equal(
            Totals.Of(plan.Zones, plan.Surfaces, plan.OrientationDegrees).GlazingByOrientation.OrderBy(g => g.Key).Select(g => g.Value),
            Totals.Of(floor.Zones, floor.Surfaces, floor.OrientationDegrees).GlazingByOrientation.OrderBy(g => g.Key).Select(g => g.Value),
            new AreaComparer());
    }

    public static IEnumerable<object[]> SingleZoneAggregators() =>
        from placement in new[] { (0.0, 0.0, 0.0), (30.0, 5.3, -2.1), (131.4, 15.08, -153.9) }
        from simplifier in new[] { "NoSimplification", "PerimeterCore" }
        from aggregator in new[] { "SingleZonePerFloorType", "SingleZoneBuilding" }
        select new object[] { placement.Item1, placement.Item2, placement.Item3, simplifier, aggregator };

    [Theory]
    [MemberData(nameof(SingleZoneAggregators))]
    public void MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(double degrees, double x, double y, string simplifier, string aggregator)
    {
        IFloor floor = Pipeline.Simplifier(simplifier).Simplify(PlanTransform.Apply(Pipeline.Plan(), degrees, x, y).Value).Value;
        FloorEntry[] entries = { new(floor, 1), new(floor, 3), new(floor, 1) };
        IGeneratedBuilding stacked = new Stack(Pipeline.Tolerances).Aggregate(entries).Value;

        IGeneratedBuilding building = Pipeline.Aggregator(aggregator).Aggregate(entries).Value;

        AssertCentredWindowsCarryTheCoveredGlazing(stacked.Surfaces, building.Surfaces);
    }

    [Theory]
    [InlineData("Stack")]
    [InlineData("StackedFloorZoneMultiplier")]
    public void AggregatorsThatDoNotRebuildWallsKeepTheFloorWindows(string aggregator)
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = Pipeline.Aggregator(aggregator).Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 3), new FloorEntry(floor, 1) }).Value;

        string[] expected = floor.Surfaces.OfType<WallSurface>().Select(w => Describe(w.Windows)).ToArray();
        Assert.All(
            building.Surfaces.OfType<WallSurface>().GroupBy(w => w.Elevation),
            storey => Assert.Equal(expected, storey.Select(w => Describe(w.Windows))));
    }

    [Fact]
    public void NoSimplificationKeepsTheGeneratorWindows()
    {
        IGeneratedPlan plan = Pipeline.Plan();

        IFloor floor = new NoSimplification().Simplify(plan).Value;

        Assert.Equal(TextReport.Describe(plan).Split('\n').Where(l => l.StartsWith("surface ")), TextReport.Describe(floor).Split('\n').Where(l => l.StartsWith("surface ")));
    }

    /// <summary>
    /// Every target outdoor wall carries the glazed area of the source windows whose centre lies on it, as one window shaped by the generator's rule,
    /// or no window when that area is zero.
    /// </summary>
    internal static void AssertCentredWindowsCarryTheCoveredGlazing(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces)
    {
        WallSurface[] sources = Outdoor(sourceSurfaces).ToArray();
        WallSurface[] targets = Outdoor(targetSurfaces).ToArray();
        Assert.NotEmpty(targets);
        foreach (WallSurface wall in targets)
        {
            double expected = sources.Sum(source => FacadeAttribution.Interval(wall, source, Pipeline.Tolerances) is { } interval
                ? source.Windows.Where(w => interval.Start + w.Offset + (w.Width / 2.0) is var centre && centre > 0.0 && centre < wall.Length).Sum(w => w.Area)
                : 0.0);
            if (expected == 0.0)
            {
                Assert.Empty(wall.Windows);
                continue;
            }

            Window window = Assert.Single(wall.Windows);
            Assert.Equal(expected, window.Area, 9);
            Assert.Equal((wall.Length - window.Width) / 2.0, window.Offset, 9);
            Assert.Equal((wall.Height - window.Height) / 2.0, window.SillHeight, 9);
            Assert.Equal(window.Width / wall.Length, window.Height / wall.Height, 12);
        }
    }

    private static string Describe(IEnumerable<Window> windows) =>
        string.Join(";", windows.Select(w => $"{w.Offset:R},{w.SillHeight:R},{w.Width:R},{w.Height:R}"));

    private static IEnumerable<WallSurface> Outdoor(IEnumerable<Surface> surfaces) =>
        surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors);

    private sealed class AreaComparer : IEqualityComparer<double>
    {
        public bool Equals(double x, double y) => Pipeline.Tolerances.AreaEquals(x, y);

        public int GetHashCode(double obj) => 0;
    }
}
```

- [x] **Step 2: Change two aggregator tests — replace `tests/Lod.Integration.Tests/AggregatorTests.cs` (full file)**

Changes: `SingleZonePerFloorTypeConservesEveryInvariant` and `SingleZoneBuildingKeepsGroundRoofAndGlazing` no longer expect the number of windows of the stacked floors (2 × wide + 3 × narrow, and 3 × the floor's); they expect exactly one window on every wall. Their glazing-total and validation assertions are unchanged.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class AggregatorTests
{
    [Fact]
    public void ZoneMultiplierCarriesMultipliersAndOrderedBoundaries()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new StackedFloorZoneMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;

        Assert.Equal(new[] { 1, 8, 1 }, building.Zones.GroupBy(z => z.Id.Value.Substring(0, 2)).Select(g => g.First().Multiplier));
        HorizontalSurface[] horizontal = building.Surfaces.OfType<HorizontalSurface>().ToArray();
        Assert.All(horizontal.Where(h => h.Zone.Value.StartsWith("L0/") && h.Kind == HorizontalKind.Floor), h => Assert.Equal(BoundaryCondition.Ground, h.Boundary));
        Assert.All(horizontal.Where(h => h.Zone.Value.StartsWith("L9/") && h.Kind == HorizontalKind.Ceiling), h => Assert.Equal(BoundaryCondition.Outdoors, h.Boundary));
        Assert.Equal(
            horizontal.Length - 12,
            horizontal.Count(h => h.Boundary == BoundaryCondition.Adiabatic));
        Assert.Equal(10 * floor.Zones.Sum(z => z.FloorArea), building.Zones.Sum(z => z.Multiplier * z.FloorArea), 6);
    }

    [Fact]
    public void RepresentativeStoreysKeepTheirTrueElevations()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new StackedFloorZoneMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;

        // Storeys 1-8 are represented by storey 5, the whole storey nearest their middle (D-045); the top storey stays storey 9.
        Assert.Equal(new[] { "L0/", "L5/", "L9/" }, building.Zones.Select(z => z.Id.Value.Substring(0, 3)).Distinct());
        Assert.Equal(new[] { 0.0, 15.0, 27.0 }, building.Zones.Select(z => z.Parts[0].Elevation).Distinct());
        Assert.Equal(30.0, Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height, 9);
        Assert.Equal("L0x1,L5x8,L9x1", building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
    }

    [Fact]
    public void ZoneMultiplierListsTheStoreysItRepresentsButDoesNotModel()
    {
        IFloor floor = Pipeline.DetailedFloor();
        FloorEntry[] entries = { new(floor, 1), new(floor, 8), new(floor, 1) };

        IReadOnlyList<PlacedStorey> unmodelled = new StackedFloorZoneMultiplier(Pipeline.Tolerances).UnmodelledStoreys(entries).Value;

        // Storey 5 represents storeys 1-8 (D-045); the other seven are represented but not modelled, at their true elevations.
        Assert.Equal(new[] { 1, 2, 3, 4, 6, 7, 8 }, unmodelled.Select(s => s.Index));
        Assert.Equal(new[] { 3.0, 6.0, 9.0, 12.0, 18.0, 21.0, 24.0 }, unmodelled.Select(s => s.Elevation));
        Assert.All(unmodelled, s => Assert.Equal(floor.Zones.Select(z => z.FloorArea), s.Zones.Select(z => z.FloorArea)));
        Assert.All(unmodelled.SelectMany(s => s.Zones), z => Assert.Equal(1, z.Multiplier));
    }

    [Fact]
    public void ZoneMultiplierWithoutMultipliedStoreysModelsEveryStorey()
    {
        IFloor floor = Pipeline.DetailedFloor();

        Assert.Empty(new StackedFloorZoneMultiplier(Pipeline.Tolerances).UnmodelledStoreys(new[] { new FloorEntry(floor, 2), new FloorEntry(floor, 1) }).Value);
        Assert.Contains(new StackedFloorZoneMultiplier(Pipeline.Tolerances).UnmodelledStoreys(new FloorEntry[0]).Diagnostics, d => d.Code == DiagnosticCodes.NoFloors);
    }

    [Theory]
    [InlineData(new[] { 5 }, "L0x1,L2x3,L4x1")]
    [InlineData(new[] { 2, 1 }, "L0x1,L1x1,L2x1")]
    [InlineData(new[] { 1, 8, 2 }, "L0x1,L5x8,L9x1,L10x1")]
    public void ExposedStoreysOfMultipliedTypesAreSplitOff(int[] multipliers, string storeys)
    {
        IFloor floor = Pipeline.DetailedFloor();

        Result<IGeneratedBuilding> result = new StackedFloorZoneMultiplier(Pipeline.Tolerances).Aggregate(multipliers.Select(n => new FloorEntry(floor, n)).ToArray());
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(result.Value);

        Assert.Equal(storeys, result.Value.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.FloorTypeSplit && d.Severity == DiagnosticSeverity.Info);
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }

    [Theory]
    [InlineData("setback", "wide x1, wide x4, narrow x3", "L0x1,L2x3,L4x1,L6x2,L7x1", "")]
    [InlineData("overhang", "narrow x2, wide x3", "L0x1,L1x1,L2x1,L3x1,L4x1", "L2")]
    public void VaryingFootprintsKeepExposedAreasWithoutMultiplyingThem(string name, string types, string storeys, string unsupported)
    {
        // Wide: 24 m x 18 m, two units per row. Narrow: 14 m x 18 m from the same west end, one unit per row. Either way 180 m² is exposed.
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });
        FloorEntry[] entries = types.Split(',')
            .Select(t => t.Trim().Split(new[] { " x" }, StringSplitOptions.None))
            .Select(t => new FloorEntry(t[0] == "wide" ? wide : narrow, int.Parse(t[1], System.Globalization.CultureInfo.InvariantCulture)))
            .ToArray();

        Result<IGeneratedBuilding> result = new StackedFloorZoneMultiplier(Pipeline.Tolerances).Aggregate(entries);
        IGeneratedBuilding building = result.Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.Equal(storeys, building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.Equal(unsupported, string.Join(",", result.Diagnostics.Where(d => d.Code == DiagnosticCodes.UnsupportedStorey).Select(d => d.Subject)));
        Assert.All(report.Checks, c => Assert.True(c.Passed, $"{name}: {c.Check}"));
        Dictionary<ZoneId, int> multiplier = building.Zones.ToDictionary(z => z.Id, z => z.Multiplier);
        HorizontalSurface[] exposed = building.Surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary != BoundaryCondition.Adiabatic).ToArray();
        Assert.All(exposed, h => Assert.Equal(1, multiplier[h.Zone]));
        double roof = Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height;
        Assert.Equal(180.0, exposed.Where(h => h.Boundary == BoundaryCondition.Outdoors && h.Elevation < roof - 1.0).Sum(h => h.Area), 6);
    }

    [Fact]
    public void MultiplierTakesTheDesignationsOfItsStoreysFromTheStack()
    {
        // D-068: every floor and ceiling piece of a modelled storey is the stacked piece with the same ID; pieces between storeys become adiabatic.
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });
        FloorEntry[] entries = { new(wide, 1), new(wide, 4), new(narrow, 3), new(wide, 2) };

        Dictionary<SurfaceId, HorizontalSurface> stacked = new Stack(Pipeline.Tolerances).Aggregate(entries).Value
            .Surfaces.OfType<HorizontalSurface>().ToDictionary(h => h.Id);
        HorizontalSurface[] modelled = new StackedFloorZoneMultiplier(Pipeline.Tolerances).Aggregate(entries).Value
            .Surfaces.OfType<HorizontalSurface>().ToArray();

        Assert.NotEmpty(modelled);
        Assert.All(modelled, h =>
        {
            HorizontalSurface source = stacked[h.Id];
            Assert.Equal(source.Boundary == BoundaryCondition.Interzone ? BoundaryCondition.Adiabatic : source.Boundary, h.Boundary);
            Assert.Null(h.AdjacentZone);
            Assert.Equal(source.Zone, h.Zone);
            Assert.Equal(source.Kind, h.Kind);
            Assert.Equal(source.Elevation, h.Elevation);
            Assert.Equal(source.Area, h.Area, 9);
        });
    }

    [Theory]
    [InlineData("Stack")]
    [InlineData("StackedFloorZoneMultiplier")]
    [InlineData("SingleZonePerFloorType")]
    [InlineData("SingleZoneBuilding")]
    public void AnOverhangingStoreyIsReportedAsUnsupported(string aggregator)
    {
        // Narrow (14 m) x2 below wide (24 m) x1: storey 2 overhangs storey 1 by 10 m x 18 m (D-074). The building is still produced and validates.
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });

        Result<IGeneratedBuilding> result = Pipeline.Aggregator(aggregator).Aggregate(new[] { new FloorEntry(narrow, 2), new FloorEntry(wide, 1) });

        Diagnostic warning = Assert.Single(result.Diagnostics, d => d.Code == DiagnosticCodes.UnsupportedStorey);
        Assert.Equal(DiagnosticSeverity.Warning, warning.Severity);
        Assert.Equal("L2", warning.Subject);
        Assert.Contains("storey 2", warning.Message);
        Assert.Contains("180.000000 m²", warning.Message);
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(result.Value);
        Assert.True(report.Passed, report.Describe());
    }

    [Theory]
    [InlineData("Stack")]
    [InlineData("StackedFloorZoneMultiplier")]
    [InlineData("SingleZonePerFloorType")]
    [InlineData("SingleZoneBuilding")]
    public void SetbacksAndIdenticalStoreysAreSupported(string aggregator)
    {
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });

        Result<IGeneratedBuilding> result = Pipeline.Aggregator(aggregator).Aggregate(new[] { new FloorEntry(wide, 3), new FloorEntry(narrow, 2) });

        Assert.True(result.IsSuccess);
        Assert.DoesNotContain(result.Diagnostics, d => d.Code == DiagnosticCodes.UnsupportedStorey);
    }

    [Fact]
    public void BottomMiddleTopMultiplierMatchesTheStackExactly()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new StackedFloorZoneMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }

    [Fact]
    public void SingleZonePerFloorTypeHasOneZonePerFloorEntry()
    {
        IGeneratedBuilding building = new SingleZonePerFloorType(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 1), new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Assert.Equal(new[] { "E0", "E1" }, building.Zones.Select(z => z.Id.Value));
        Assert.Equal(new[] { "Floor type 0", "Floor type 1" }, building.Zones.Select(z => z.Name));
        Assert.Equal(new[] { 1, 3 }, building.Zones.Select(z => z.Parts.Count));
        Assert.Equal(new[] { 6, 18 }, building.Zones.Select(z => z.SourceZones.Count));
        Assert.All(building.Zones, z => Assert.Equal(1, z.Multiplier));
        Assert.Equal(3 * 432.0 * 3.0, building.Zones[1].Volume, 6);
        Assert.Equal(new[] { 0.0, 3.0, 6.0, 9.0 }, building.Zones.SelectMany(z => z.Parts).Select(p => p.Elevation));
    }

    [Fact]
    public void SingleZonePerFloorTypeKeepsTheSlabsBetweenEntriesAsInterzonePairs()
    {
        IGeneratedBuilding building = new SingleZonePerFloorType(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 1), new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        // Within E1 the slabs at 6 m and 9 m become internal mass (D-031); the slab at 3 m lies between E0 and E1 (D-068, D-071).
        Assert.Equal(new[] { ("E1", 6.0), ("E1", 9.0) }, building.InternalMasses.Select(m => (m.Zone.Value, m.Elevation)));
        Assert.All(building.InternalMasses, m => Assert.Equal(432.0, m.SlabArea, 6));
        HorizontalSurface[] interzone = building.Surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary == BoundaryCondition.Interzone).ToArray();
        Assert.All(interzone, h => Assert.Equal(3.0, h.Elevation));
        Assert.Equal(432.0, interzone.Where(h => h.Zone.Value == "E0" && h.Kind == HorizontalKind.Ceiling && h.AdjacentZone!.Value.Value == "E1").Sum(h => h.Area), 6);
        Assert.Equal(432.0, interzone.Where(h => h.Zone.Value == "E1" && h.Kind == HorizontalKind.Floor && h.AdjacentZone!.Value.Value == "E0").Sum(h => h.Area), 6);
        Assert.Equal(interzone.Length, interzone.Count(h => h.Kind == HorizontalKind.Ceiling) * 2);
        Assert.DoesNotContain(building.Surfaces.OfType<WallSurface>(), w => w.Boundary != BoundaryCondition.Outdoors);
    }

    [Fact]
    public void SingleZonePerFloorTypeConservesEveryInvariant()
    {
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });

        IGeneratedBuilding building = new SingleZonePerFloorType(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(wide, 2), new FloorEntry(narrow, 3) }).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.All(report.Checks.Where(c => c.Enforced), c => Assert.True(c.Passed, c.Check));
        Assert.All(building.Surfaces.OfType<WallSurface>(), w => Assert.Single(w.Windows));
    }

    [Fact]
    public void OneFloorEntryGivesTheSingleZoneBuildingUnderAnotherName()
    {
        FloorEntry[] entries = { new(Pipeline.DetailedFloor(), 3) };

        string perType = TextReport.Describe(new SingleZonePerFloorType(Pipeline.Tolerances).Aggregate(entries).Value);
        string building = TextReport.Describe(new SingleZoneBuilding(Pipeline.Tolerances).Aggregate(entries).Value);

        Assert.Equal(building.Replace("BUILDING", "E0").Replace("\"Building\"", "\"Floor type 0\""), perType);
    }

    [Fact]
    public void SingleZoneBuildingHasOneZoneWithOnePartPerStorey()
    {
        IGeneratedBuilding building = new SingleZoneBuilding(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Zone zone = Assert.Single(building.Zones);
        Assert.Equal(3, zone.Parts.Count);
        Assert.Equal(3 * 432.0 * 3.0, zone.Volume, 6);
        Assert.Equal(18, zone.SourceZones.Count);
        Assert.DoesNotContain(building.Surfaces, s => s.Boundary == BoundaryCondition.Interzone);
    }

    [Fact]
    public void SingleZoneBuildingTurnsSlabsIntoInternalMass()
    {
        IGeneratedBuilding building = new SingleZoneBuilding(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Assert.Equal(new[] { 3.0, 6.0 }, building.InternalMasses.Select(m => m.Elevation));
        Assert.All(building.InternalMasses, m => Assert.Equal(432.0, m.SlabArea, 6));
        Assert.All(building.InternalMasses, m => Assert.Equal(2, m.ExposedFaces));
        Assert.All(building.InternalMasses, m => Assert.Equal(12, m.SourceSurfaces.Count));
    }

    [Fact]
    public void SingleZoneBuildingKeepsGroundRoofAndGlazing()
    {
        IFloor floor = Pipeline.DetailedFloor();
        IGeneratedBuilding building = new SingleZoneBuilding(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(floor, 3) }).Value;

        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks.Where(c => c.Enforced), c => Assert.True(c.Passed, c.Check));
        Assert.Contains(report.Checks, c => c.Check == "Building.GroundArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.RoofArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.Height" && c.Passed && c.Enforced);
        Assert.Equal(3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), building.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), 6);
        Assert.Equal(12, building.Surfaces.OfType<WallSurface>().Count());
        Assert.All(building.Surfaces.OfType<WallSurface>(), w => Assert.Single(w.Windows));
    }

    public static IEnumerable<object[]> Matrix() =>
        from simplifier in new[] { "NoSimplification", "SemanticMerge", "PerimeterCore", "SingleZonePerFloor" }
        from aggregator in new[] { "Stack", "StackedFloorZoneMultiplier", "SingleZonePerFloorType", "SingleZoneBuilding" }
        select new object[] { simplifier, aggregator };

    [Theory]
    [MemberData(nameof(Matrix))]
    public void EverySimplifierAndAggregatorCombinationValidates(string simplifier, string aggregator)
    {
        IFloor floor = Pipeline.Floor(Pipeline.Simplifier(simplifier));
        FloorEntry[] entries = { new(floor, 1), new(floor, 3), new(floor, 1) };

        IGeneratedBuilding building = Pipeline.Aggregator(aggregator).Aggregate(entries).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void MultiplierSnapshot()
    {
        IFloor floor = Pipeline.Floor(Pipeline.Simplifier("PerimeterCore"));
        IGeneratedBuilding building = new StackedFloorZoneMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 2), new FloorEntry(floor, 1) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-StackedFloorZoneMultiplier");
    }

    [Fact]
    public void SingleZoneBuildingSnapshot()
    {
        IGeneratedBuilding building = new SingleZoneBuilding(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-SingleZoneBuilding");
    }

    [Fact]
    public void SingleZonePerFloorTypeSnapshot()
    {
        IFloor floor = Pipeline.DetailedFloor();
        IGeneratedBuilding building = new SingleZonePerFloorType(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 2) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-SingleZonePerFloorType");
    }
}
```

- [x] **Step 3: Run the tests and see them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.CentredWindowTests|FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected on net8.0 (45 `AggregatorTests` and 24 `CentredWindowTests`):

```text
Failed!  - Failed:    12, Passed:    57, Skipped:     0, Total:    69, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

with the failing tests and the first lines of their messages, in any order; each `Assert.Single()` message continues with a `Collection:` line that lists the windows still kept in place, and each `Assert.All()` message with the walls that failed:

```text
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 0, x: 0, y: 0, simplifier: "NoSimplification", aggregator: "SingleZonePerFloorType")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 0, x: 0, y: 0, simplifier: "NoSimplification", aggregator: "SingleZoneBuilding")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "NoSimplification", aggregator: "SingleZonePerFloorType")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "NoSimplification", aggregator: "SingleZoneBuilding")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "NoSimplification", aggregator: "SingleZonePerFloorType")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "NoSimplification", aggregator: "SingleZoneBuilding")
  Assert.Single() Failure: The collection contained 3 items
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "PerimeterCore", aggregator: "SingleZonePerFloorType")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 4.1626452350000003 (rounded from 4.1626452349215501)
  Actual:   4.1626455059999996 (rounded from 4.1626455056076059)
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 30, x: 5.2999999999999998, y: -2.1000000000000001, simplifier: "PerimeterCore", aggregator: "SingleZoneBuilding")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 4.1626452350000003 (rounded from 4.1626452349215501)
  Actual:   4.1626455059999996 (rounded from 4.1626455056076059)
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "PerimeterCore", aggregator: "SingleZonePerFloorType")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 5.8032268460000003 (rounded from 5.8032268462012668)
  Actual:   5.8032266459999997 (rounded from 5.8032266460681372)
Failed Lod.Integration.Tests.CentredWindowTests.MergedStoreyWallsCarryOneCentredWindowWithTheGlazingTheyCover(degrees: 131.40000000000001, x: 15.08, y: -153.90000000000001, simplifier: "PerimeterCore", aggregator: "SingleZoneBuilding")
  Assert.Equal() Failure: Values are not within 9 decimal places
  Expected: 5.8032268460000003 (rounded from 5.8032268462012668)
  Actual:   5.8032266459999997 (rounded from 5.8032266460681372)
Failed Lod.Integration.Tests.AggregatorTests.SingleZonePerFloorTypeConservesEveryInvariant
  Assert.All() Failure: 15 out of 20 items in the collection did not pass.
Failed Lod.Integration.Tests.AggregatorTests.SingleZoneBuildingKeepsGroundRoofAndGlazing
  Assert.All() Failure: 9 out of 12 items in the collection did not pass.
```

The two canonical *Perimeter Core* cases and the two `AggregatorsThatDoNotRebuildWallsKeepTheFloorWindows` cases already pass: the *Perimeter Core* floor has one centred window per wall since Task 3, and the merge keeps it in place on the identical canonical storey walls; on rotated plans the kept window is off-centre by about 2e-7 to 3e-7 m (grid rounding of the rebuilt storey wall), which the 9-decimal centring check catches.

- [x] **Step 4: Implement — replace `src/Lod.Core/Buildings/SingleZoneMerge.cs` (full file)**

`Merge` calls `CentredWindows.Place` with the stacked source walls and the rebuilt storey walls where it called `WindowRehosting.Rehost`, after the façade-coverage check; the summary names the rule.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;

namespace Lod.Core.Buildings;

/// <summary>A zone that a single-zone method merges storeys into.</summary>
/// <param name="Id">Zone ID.</param>
/// <param name="Name">Display name.</param>
internal sealed record MergedZone(ZoneId Id, string Name);

/// <summary>
/// The merge shared by the single-zone methods (ADR-013): the storeys of the assembled stack are grouped by floor entry into zones. Each zone gets one
/// part per storey outline (the union of the storey's zone footprints as tiles, <see cref="PolygonOps.UnionTiles"/>); its outdoor walls are rebuilt per
/// outline, must cover every source façade (D-041), and carry one centred window each with the glazed area of the source windows they cover (D-079,
/// <see cref="CentredWindows"/>); walls between merged zones are discarded (D-034); slabs between two storeys of the same zone become internal mass
/// with both faces exposed, one entry per slab level (D-031); every other floor and ceiling piece keeps its stacked designation (D-068), and a piece between two
/// zones stays interzone. Programs are aggregated from the stacked zones with fractions 1, so every invariant is conserved (ADR-005, ADR-007).
/// </summary>
internal static class SingleZoneMerge
{
    /// <summary>Merges the stacked storeys of <paramref name="floors"/> into the zones given per floor entry.</summary>
    /// <param name="operation">Operation name recorded in provenance.</param>
    /// <param name="floors">Floor entries, bottom to top.</param>
    /// <param name="zoneOfEntry">The zone each floor entry's storeys merge into; equal zones are merged together.</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>The building, or errors.</returns>
    public static Result<IGeneratedBuilding> Merge(string operation, IReadOnlyList<FloorEntry> floors, Func<int, MergedZone> zoneOfEntry, ToleranceSettings tolerances)
    {
        Result<AssembledStack> assembled = Storeys.Assemble(floors, tolerances);
        if (!assembled.IsSuccess)
        {
            return Result.Failure<IGeneratedBuilding>(assembled.Diagnostics);
        }

        AssembledStack stack = assembled.Value;
        MergedZone[] zoneOfStorey = stack.Entries.Select(zoneOfEntry).ToArray();
        MergedZone[] targets = zoneOfStorey.Distinct().ToArray();
        Dictionary<ZoneId, ZoneId> targetOf = stack.Storeys
            .SelectMany((s, k) => s.Zones.Select(z => (Source: z.Id, Target: zoneOfStorey[k].Id)))
            .ToDictionary(p => p.Source, p => p.Target);
        var ops = new PolygonOps(tolerances);
        var builder = new LayoutSurfaceBuilder(tolerances);
        Dictionary<ZoneId, List<ZonePart>> parts = targets.ToDictionary(t => t.Id, _ => new List<ZonePart>());
        var walls = new List<Surface>();
        for (int k = 0; k < stack.Storeys.Count; k++)
        {
            PlacedStorey storey = stack.Storeys[k];
            ZoneId target = zoneOfStorey[k].Id;
            foreach (Polygon2 outline in ops.UnionTiles(storey.Zones.Select(z => z.Parts[0].Footprint).ToArray()))
            {
                parts[target].Add(new ZonePart(outline, storey.Elevation, storey.Height));
                Result<IReadOnlyList<Surface>> built = builder.Build(outline, new[] { new LayoutZone(target, outline) }, storey.Height);
                if (!built.IsSuccess)
                {
                    return Result.Failure<IGeneratedBuilding>(built.Diagnostics);
                }

                string prefix = $"S{parts[target].Count - 1}/";
                walls.AddRange(built.Value.OfType<WallSurface>().Select(w => w.Relocate(id => id, prefix, storey.Elevation)));
            }
        }

        WallSurface[] sourceWalls = stack.Storeys.SelectMany(s => s.Walls).ToArray();
        FacadeAttribution facade = FacadeAttribution.Compute(sourceWalls, walls, tolerances);
        Diagnostic[] gaps = facade.CoverageGaps()
            .Select(g => Diagnostic.Error(DiagnosticCodes.FacadeNotCovered, $"Rebuilt façades cover {g.CoveredLength:0.######} m of this {g.Wall.Length:0.######} m wall (D-041).", g.Wall.Id.Value))
            .ToArray();
        if (gaps.Length > 0)
        {
            return Result.Failure<IGeneratedBuilding>(gaps);
        }

        Result<IReadOnlyList<Surface>> glazed = CentredWindows.Place(sourceWalls, walls, tolerances);
        if (!glazed.IsSuccess)
        {
            return Result.Failure<IGeneratedBuilding>(glazed.Diagnostics);
        }

        IReadOnlyList<Surface> glazedWalls = glazed.Value;
        HorizontalSurface[] horizontal = stack.Horizontal.SelectMany(h => h).ToArray();
        bool Within(HorizontalSurface h) => h.Boundary == BoundaryCondition.Interzone && targetOf[h.Zone] == targetOf[h.AdjacentZone!.Value];
        InternalMass[] masses = targets
            .SelectMany(t => horizontal
                .Where(h => h.Kind == HorizontalKind.Floor && Within(h) && targetOf[h.Zone] == t.Id)
                .GroupBy(h => h.Elevation)
                .OrderBy(g => g.Key)
                .Select(level => new InternalMass(
                    t.Id,
                    level.Sum(h => h.Area),
                    ExposedFaces: 2,
                    level.Key,
                    level.Select(h => h.Id)
                        .Concat(horizontal.Where(c => c.Kind == HorizontalKind.Ceiling && Within(c) && targetOf[c.Zone] == t.Id && c.Elevation == level.Key).Select(c => c.Id))
                        .ToArray())))
            .ToArray();
        IEnumerable<Surface> envelope = horizontal
            .Where(h => !Within(h))
            .Select(h => new HorizontalSurface(h.Id, targetOf[h.Zone], h.Kind, h.Polygon, h.Elevation, h.Boundary, h.AdjacentZone is { } adjacent ? targetOf[adjacent] : null));

        var diagnostics = new List<Diagnostic>(assembled.Diagnostics);
        var aggregator = new EquivalentPropertyAggregator(tolerances);
        var zones = new List<Zone>();
        foreach (MergedZone target in targets)
        {
            Zone[] sources = stack.Storeys.Where((_, k) => zoneOfStorey[k] == target).SelectMany(s => s.Zones).ToArray();
            List<ZonePart> zoneParts = parts[target.Id];
            var measures = new ZoneMeasures(
                zoneParts.Sum(p => p.Footprint.Area),
                zoneParts.Sum(p => p.Volume),
                glazedWalls.Where(w => w.Zone == target.Id).Sum(w => w.Area));
            SourceZoneContribution[] contributions = sources
                .Select(z => new SourceZoneContribution(z.Id, z.Program, LayoutMeasures.Of(z, sourceWalls), 1.0, 1.0))
                .ToArray();
            Result<ZoneProgram> program = aggregator.Aggregate(target.Id, measures, contributions);
            diagnostics.AddRange(program.Diagnostics);
            if (program.IsSuccess)
            {
                SpaceType[] types = sources.Select(z => z.SpaceType).Distinct().ToArray();
                zones.Add(new Zone(target.Id, target.Name, types.Length == 1 ? types[0] : SpaceType.Mixed, zoneParts, program.Value, sources.Select(z => z.Id)));
            }
        }

        if (diagnostics.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            return Result.Failure<IGeneratedBuilding>(diagnostics);
        }

        var provenance = Provenance.Of(
            operation,
            new[] { new KeyValuePair<string, string>("Multipliers", string.Join(",", floors.Select(e => e.Multiplier))) },
            floors.Select(e => e.Floor.Provenance).ToArray());
        IGeneratedBuilding building = new GeneratedBuilding(floors[0].Floor.OrientationDegrees, zones, glazedWalls.Concat(envelope), masses, floors, provenance);
        return Result.Success(building, diagnostics);
    }
}
```

- [x] **Step 5: Update the doc comments — replace `src/Lod.Core/Buildings/SingleZoneBuilding.cs` and `src/Lod.Core/Buildings/SingleZonePerFloorType.cs` (full files)**

Only the summaries change.

`src/Lod.Core/Buildings/SingleZoneBuilding.cs`:

```csharp
using System.Collections.Generic;
using Lod.Core.Common;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>
/// The whole building as one zone (D-021, D-071), built from the assembled stack: one zone part per storey outline; outdoor walls rebuilt per
/// storey, required to cover every source façade (D-041), each carrying one centred window with the glazed area of the source windows it covers
/// (D-079); walls between merged zones discarded
/// (D-034); slabs between storeys turned into internal mass with both faces exposed, one entry per slab level (D-031); ground, roof, and exposed
/// floors kept (D-068). Formerly <c>SingleZoneMerged</c>.
/// </summary>
public sealed class SingleZoneBuilding : IFloorAggregator
{
    /// <summary>ID of the single zone.</summary>
    public static readonly ZoneId BuildingZone = new("BUILDING");

    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SingleZoneBuilding(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <inheritdoc />
    public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors) =>
        SingleZoneMerge.Merge(nameof(SingleZoneBuilding), floors, _ => new MergedZone(BuildingZone, "Building"), _tolerances);
}
```

`src/Lod.Core/Buildings/SingleZonePerFloorType.cs`:

```csharp
using System.Collections.Generic;
using Lod.Core.Common;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>
/// One zone per floor entry (D-071): the Nᵢ storeys of entry <c>i</c>, stacked as in <see cref="Stack"/>, merge into one zone
/// <c>E{i}</c> with one part per storey outline. Outdoor walls are rebuilt per storey outline, required to cover every source façade (D-041),
/// each carrying one centred window with the glazed area of the source windows it covers (D-079); walls between merged zones are discarded (D-034); slabs between storeys of the same entry become
/// internal mass (D-031); the floors and ceilings between two entries stay interzone between their zones, and ground, roof, and exposed pieces are
/// kept as designated on the assembled stack (D-068).
/// </summary>
public sealed class SingleZonePerFloorType : IFloorAggregator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SingleZonePerFloorType(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <summary>ID of the zone of floor entry <paramref name="entry"/>.</summary>
    /// <param name="entry">Index of the floor entry, from 0 at the bottom.</param>
    /// <returns>The zone ID, <c>E{entry}</c>.</returns>
    public static ZoneId ZoneOf(int entry) => new($"E{entry}");

    /// <inheritdoc />
    public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors) =>
        SingleZoneMerge.Merge(nameof(SingleZonePerFloorType), floors, i => new MergedZone(ZoneOf(i), $"Floor type {i}"), _tolerances);
}
```

- [x] **Step 6: Run the integration tests and see the snapshots fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected on net8.0:

```text
Failed!  - Failed:     2, Passed:   185, Skipped:     0, Total:   187, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

with the failing tests and their messages, in any order:

```text
Failed Lod.Integration.Tests.AggregatorTests.SingleZoneBuildingSnapshot
  Snapshot 'aggregator-SingleZoneBuilding' is missing or differs. Review Snapshots/aggregator-SingleZoneBuilding.received.txt and rename it to aggregator-SingleZoneBuilding.txt to accept.
Failed Lod.Integration.Tests.AggregatorTests.SingleZonePerFloorTypeSnapshot
  Snapshot 'aggregator-SingleZonePerFloorType' is missing or differs. Review Snapshots/aggregator-SingleZonePerFloorType.received.txt and rename it to aggregator-SingleZonePerFloorType.txt to accept.
```

and the two files `tests/Lod.Integration.Tests/Snapshots/*.received.txt`.

- [x] **Step 7: Review and accept the received files**

Review each received file against Step 8; it must be identical. Only `window(…)` entries change, three windows → one on the east, south, and north walls of every storey; the west wall keeps its single 5.4 m² window, and every other line is byte-identical:

- `aggregator-SingleZoneBuilding`: lines 8, 9, 11 (`S0/BUILDING/W1`, `W2`, `W4`) and 12, 13, 15 (`S1/BUILDING/W1`, `W2`, `W4`): east 15.6 m² `window(offset=4.162645 sill=0.693774 9.674709x1.612452)`, south and north 19.2 m² `window(offset=5.803227 sill=0.725403 12.393547x1.549193)`.
- `aggregator-SingleZonePerFloorType`: lines 14, 15, 17 (`S0/E0/…`), 18, 19, 21 (`S0/E1/…`), and 22, 23, 25 (`S1/E1/…`), the same windows.

Accept the files, then check that only window entries changed:

```powershell
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.received.txt tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.txt
Move-Item -Force tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZonePerFloorType.received.txt tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZonePerFloorType.txt
```

```bash
git diff --numstat -- tests/Lod.Integration.Tests/Snapshots
git diff -U0 -- tests/Lod.Integration.Tests/Snapshots | grep -c -E '^[-+][a-z]'
git diff -U0 -- tests/Lod.Integration.Tests/Snapshots | grep -E '^[-+][a-z]' | sed -E 's/ window\([^)]*\)//g; s/^[-+]//' | sort | uniq -u
```

Expected: the numstat lines `6	6	…/aggregator-SingleZoneBuilding.txt` and `9	9	…/aggregator-SingleZonePerFloorType.txt`; the count `30`; no output from the last command.

- [x] **Step 8: Expected content of the two snapshots**

`tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.txt`:

```text
building orientation=0.000000 sources=2
zone BUILDING Mixed "Building" area=864.000000 volume=2592.000000 parts=2 multiplier=1 sources=[L0/ST,L0/CO,L0/US1,L0/US2,L0/UN1,L0/UN2,L1/ST,L1/CO,L1/US1,L1/US2,L1/UN1,L1/UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface S0/BUILDING/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface S0/BUILDING/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S0/BUILDING/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S0/BUILDING/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S1/BUILDING/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=3.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface S1/BUILDING/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=3.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S1/BUILDING/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=3.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S1/BUILDING/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=3.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L0/ST/F1 Ground area=72.000000 Floor z=0.000000
surface L0/CO/F1 Ground area=40.000000 Floor z=0.000000
surface L0/US1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/US2/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN2/F1 Ground area=80.000000 Floor z=0.000000
surface L1/ST/C1 Outdoors area=72.000000 Ceiling z=6.000000
surface L1/CO/C1 Outdoors area=40.000000 Ceiling z=6.000000
surface L1/US1/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/US2/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/UN1/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/UN2/C1 Outdoors area=80.000000 Ceiling z=6.000000
mass BUILDING area=432.000000 faces=2 z=3.000000
```

`tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZonePerFloorType.txt`:

```text
building orientation=0.000000 sources=1,2
zone E0 Mixed "Floor type 0" area=432.000000 volume=1296.000000 parts=1 multiplier=1 sources=[L0/ST,L0/CO,L0/US1,L0/US2,L0/UN1,L0/UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone E1 Mixed "Floor type 1" area=864.000000 volume=2592.000000 parts=2 multiplier=1 sources=[L1/ST,L1/CO,L1/US1,L1/US2,L1/UN1,L1/UN2,L2/ST,L2/CO,L2/US1,L2/US2,L2/UN1,L2/UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface S0/E0/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface S0/E0/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S0/E0/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S0/E0/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S0/E1/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=3.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface S0/E1/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=3.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S0/E1/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=3.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S0/E1/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=3.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S1/E1/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=6.000000 facing=East glazing=15.600000 window(offset=4.162645 sill=0.693774 9.674709x1.612452)
surface S1/E1/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=6.000000 facing=North glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface S1/E1/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=6.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S1/E1/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=6.000000 facing=South glazing=19.200000 window(offset=5.803227 sill=0.725403 12.393547x1.549193)
surface L0/ST/F1 Ground area=72.000000 Floor z=0.000000
surface L0/ST/C1 Interzone adjacent=E1 area=72.000000 Ceiling z=3.000000
surface L0/CO/F1 Ground area=40.000000 Floor z=0.000000
surface L0/CO/C1 Interzone adjacent=E1 area=40.000000 Ceiling z=3.000000
surface L0/US1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/US1/C1 Interzone adjacent=E1 area=80.000000 Ceiling z=3.000000
surface L0/US2/F1 Ground area=80.000000 Floor z=0.000000
surface L0/US2/C1 Interzone adjacent=E1 area=80.000000 Ceiling z=3.000000
surface L0/UN1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN1/C1 Interzone adjacent=E1 area=80.000000 Ceiling z=3.000000
surface L0/UN2/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN2/C1 Interzone adjacent=E1 area=80.000000 Ceiling z=3.000000
surface L1/ST/F1 Interzone adjacent=E0 area=72.000000 Floor z=3.000000
surface L1/CO/F1 Interzone adjacent=E0 area=40.000000 Floor z=3.000000
surface L1/US1/F1 Interzone adjacent=E0 area=80.000000 Floor z=3.000000
surface L1/US2/F1 Interzone adjacent=E0 area=80.000000 Floor z=3.000000
surface L1/UN1/F1 Interzone adjacent=E0 area=80.000000 Floor z=3.000000
surface L1/UN2/F1 Interzone adjacent=E0 area=80.000000 Floor z=3.000000
surface L2/ST/C1 Outdoors area=72.000000 Ceiling z=9.000000
surface L2/CO/C1 Outdoors area=40.000000 Ceiling z=9.000000
surface L2/US1/C1 Outdoors area=80.000000 Ceiling z=9.000000
surface L2/US2/C1 Outdoors area=80.000000 Ceiling z=9.000000
surface L2/UN1/C1 Outdoors area=80.000000 Ceiling z=9.000000
surface L2/UN2/C1 Outdoors area=80.000000 Ceiling z=9.000000
mass E1 area=432.000000 faces=2 z=6.000000
```

- [x] **Step 9: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.CentredWindowTests|FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
git status --short
git grep -n -E "in place|W0 at" -- src tests
```

Expected:

```text
Passed!  - Failed:     0, Passed:    69, Skipped:     0, Total:    69, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

then `Build succeeded.`, `0 Warning(s)`, `0 Error(s)`, and on net8.0:

```text
Passed!  - Failed:     0, Passed:   142, Skipped:     0, Total:   142, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    19, Skipped:     0, Total:    19, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:   187, Skipped:     0, Total:   187, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

`git status --short` lists the three classes, the two test files, and the two snapshots as modified; no `*.received.txt`. `git grep` prints nothing: no code comment says that windows are kept in place any more.

- [x] **Step 10: Commit**

```bash
git add src/Lod.Core/Buildings/SingleZoneMerge.cs src/Lod.Core/Buildings/SingleZoneBuilding.cs src/Lod.Core/Buildings/SingleZonePerFloorType.cs tests/Lod.Integration.Tests/CentredWindowTests.cs tests/Lod.Integration.Tests/AggregatorTests.cs tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneBuilding.txt tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZonePerFloorType.txt
git commit -m "feature(aggregators): give every rebuilt storey wall one centred window"
```

- [x] **Step 11: Merge Slice B (D-004)**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch feature/windows-centred-windows
git rebase main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git merge --ff-only feature/windows-centred-windows
git branch -d feature/windows-centred-windows
```

Expected: `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0. Do not push (D-080).

---

## Slice C — `docs/grasshopper-centred-windows`

### Task 5: Component descriptions

Grasshopper code cannot be unit-tested without Rhino: Task 5 is written, built with 0 warnings, committed, and checked in Rhino by the smoke test of Task 8.

**Files:**
- Modify: `src/Lod.Grasshopper/Components/SimplifierComponents.cs` (S3 file, last changed in S4.1), `src/Lod.Grasshopper/Components/AggregatorComponents.cs` (S4 file, last changed in S4.2), `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` (S2 file, last changed in S4.2)

**Interfaces:**
- Consumes: the rule of Tasks 3 and 4; `PlanSimplifierComponent(string name, string nickname, string description)` (S3, S4.1) and `FloorAggregatorComponent(string name, string nickname, string description)` (S2, S4.2).
- Produces: descriptions only. *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* end their descriptions with the sentence on one centred window per rebuilt outdoor wall (D-079); the *Windows* output of *Convert2BEM* reads `{i}: windows of zone i, one centred window per glazed outdoor wall (D-026, D-079), at their positions in the walls.` No name, nickname, GUID, input, output, exposure, or icon changes.

- [x] **Step 1: Create the branch**

```bash
git switch -c docs/grasshopper-centred-windows main
```

- [x] **Step 2: Replace `src/Lod.Grasshopper/Components/SimplifierComponents.cs` (full file)**

```csharp
using System;
using System.Drawing;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;

namespace Lod.Grasshopper.Components;

/// <summary>Shared inputs and solving of the plan simplifier components.</summary>
public abstract class PlanSimplifierComponent : GH_Component
{
    protected PlanSimplifierComponent(string name, string nickname, string description)
        : base(name, nickname, description, ComponentCategories.Category, ComponentCategories.Simplify)
    {
    }

    protected override Bitmap? Icon => IconLibrary.For(this);

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new PlanParameter(), "Plan", "Plan", "Detailed plan.", GH_ParamAccess.item);
        RegisterOptions(pManager);
        pManager.AddParameter(ComponentSupport.PreviewLocationParameter());
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floor", "Floor", "The simplified floor.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        PlanGoo? plan = null;
        if (!DA.GetData(0, ref plan) || plan is null)
        {
            return;
        }

        IPlanSimplifier? simplifier = CreateSimplifier(DA);
        IFloor? floor = simplifier is null ? null : ComponentSupport.Unwrap(this, simplifier.Simplify(plan.Value));
        if (floor is not null)
        {
            DA.SetData(0, new FloorGoo(floor, ComponentSupport.PreviewLocation(this, DA)));
        }
    }

    /// <summary>Registers inputs after Plan; Preview Location is added after them.</summary>
    protected virtual void RegisterOptions(GH_InputParamManager pManager)
    {
    }

    protected abstract IPlanSimplifier? CreateSimplifier(IGH_DataAccess DA);
}

public sealed class SemanticMergeComponent : PlanSimplifierComponent
{
    public SemanticMergeComponent()
        : base("Semantic Merge", "Z1", "Merges connected zones of the same space type (Z1). Every outdoor wall gets one centred window with the glazed area of the windows it covers (D-079).")
    {
    }

    public override Guid ComponentGuid => new("7d36f1d3-2708-4b69-b1a7-cf294c186e9a");

    protected override IPlanSimplifier CreateSimplifier(IGH_DataAccess DA) => new SemanticMerge(ToleranceSettings.Default);
}

public sealed class PerimeterCoreComponent : PlanSimplifierComponent
{
    public PerimeterCoreComponent()
        : base("Perimeter Core", "Z2", "Perimeter zones per orientation plus a core (Z2); corners split on the bisectors (ADR-008). Every outdoor wall gets one centred window with the glazed area of the windows it covers (D-079).")
    {
    }

    public override Guid ComponentGuid => new("6a86b976-c838-427f-93a7-344dcc2c18ce");

    protected override void RegisterOptions(GH_InputParamManager pManager)
    {
        pManager.AddNumberParameter("Depth", "D", "Perimeter zone depth, m.", GH_ParamAccess.item, 4.57);
    }

    protected override IPlanSimplifier? CreateSimplifier(IGH_DataAccess DA)
    {
        double depth = 0.0;
        return DA.GetData(1, ref depth) ? new PerimeterCore(ToleranceSettings.Default, depth) : null;
    }
}

public sealed class SingleZonePerFloorComponent : PlanSimplifierComponent
{
    public SingleZonePerFloorComponent()
        : base("Single Zone per Floor", "Z3", "The whole floor as one zone (Z3). Every outdoor wall gets one centred window with the glazed area of the windows it covers (D-079).")
    {
    }

    public override Guid ComponentGuid => new("4ff83222-5b7d-4d1b-8f26-fd580893a5db");

    protected override IPlanSimplifier CreateSimplifier(IGH_DataAccess DA) => new SingleZonePerFloor(ToleranceSettings.Default);
}

public sealed class MapSourceToTargetComponent : GH_Component
{
    public MapSourceToTargetComponent()
        : base("Map Source to Target", "Map", "The source-to-target overlap rows of a floor (spec §11).", ComponentCategories.Category, ComponentCategories.Inspect)
    {
    }

    public override Guid ComponentGuid => new("eee37e01-28a2-4b5a-9c7d-7566cb9d93d4");

    protected override Bitmap? Icon => IconLibrary.For(this);

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floor", "Floor", "A simplified floor.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddTextParameter("Source", "S", "Source zone of each row.", GH_ParamAccess.list);
        pManager.AddTextParameter("Target", "T", "Target zone of each row.", GH_ParamAccess.list);
        pManager.AddNumberParameter("Overlap", "A", "Overlap area, m².", GH_ParamAccess.list);
        pManager.AddNumberParameter("Source Fraction", "SF", "Overlap / source area.", GH_ParamAccess.list);
        pManager.AddNumberParameter("Target Fraction", "TF", "Overlap / target area.", GH_ParamAccess.list);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        FloorGoo? floor = null;
        if (!DA.GetData(0, ref floor) || floor is null)
        {
            return;
        }

        ZoneMapping[] rows = floor.Value.Mapping.ToArray();
        DA.SetDataList(0, rows.Select(r => r.Source.Value));
        DA.SetDataList(1, rows.Select(r => r.Target.Value));
        DA.SetDataList(2, rows.Select(r => r.OverlapArea));
        DA.SetDataList(3, rows.Select(r => r.SourceFraction));
        DA.SetDataList(4, rows.Select(r => r.TargetFraction));
    }
}

public sealed class ValidateComponent : GH_Component
{
    public ValidateComponent()
        : base("Validate", "Validate", "Checks a floor or building against its prescribed conservation invariants.", ComponentCategories.Category, ComponentCategories.Inspect)
    {
    }

    public override Guid ComponentGuid => new("03558c0b-83e8-417d-b122-96ebde64c147");

    protected override Bitmap? Icon => IconLibrary.For(this);

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddGenericParameter("Object", "O", "A floor or building.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddBooleanParameter("Passed", "P", "Whether every enforced check passed.", GH_ParamAccess.item);
        pManager.AddTextParameter("Report", "R", "One line per check.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        IGH_Goo? goo = null;
        if (!DA.GetData(0, ref goo) || goo is null)
        {
            return;
        }

        ValidationReport? report = goo switch
        {
            FloorGoo floor => new FloorValidator(ToleranceSettings.Default).Validate(floor.Value),
            BuildingGoo building => new BuildingValidator(ToleranceSettings.Default).Validate(building.Value),
            _ => null,
        };
        if (report is null)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Expected a floor or building, got {goo.TypeName}.");
            return;
        }

        if (!report.Passed)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Validation failed; see Report.");
        }

        DA.SetData(0, report.Passed);
        DA.SetData(1, report.Describe());
    }
}
```

- [x] **Step 3: Replace `src/Lod.Grasshopper/Components/AggregatorComponents.cs` (full file)**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;

namespace Lod.Grasshopper.Components;

public sealed class StackedFloorZoneMultiplierComponent : FloorAggregatorComponent
{
    public StackedFloorZoneMultiplierComponent()
        : base(
            "Stacked Floor Zone Multiplier",
            "ZMult",
            "Representative storeys with zone multipliers (D-071, formerly Floor Area Multiplier). Each floor type stands for N storeys; floors and ceilings are designated on the whole stack (D-068), storeys with exposed floors or ceilings (ground, roof, setbacks, overhangs) are split off as x1 storeys so exposure is never multiplied (D-046), and storeys keep their true elevations (D-045). Pieces between storeys are adiabatic.")
    {
    }

    public override Guid ComponentGuid => new("e4b44821-c9ed-49b9-9c4e-7c08355254dd");

    protected override string MultiplierDescription => "How many storeys each floor type stands for. Default 1.";

    protected override IFloorAggregator CreateAggregator() => new StackedFloorZoneMultiplier(ToleranceSettings.Default);

    /// <summary>The represented but unmodelled storeys, from <see cref="StackedFloorZoneMultiplier.UnmodelledStoreys"/>, drawn transparent grey.</summary>
    protected override IReadOnlyList<ZonePart> UnmodelledParts(IReadOnlyList<FloorEntry> entries)
    {
        Result<IReadOnlyList<PlacedStorey>> storeys = new StackedFloorZoneMultiplier(ToleranceSettings.Default).UnmodelledStoreys(entries);
        return storeys.IsSuccess ? storeys.Value.SelectMany(s => s.Zones).SelectMany(z => z.Parts).ToArray() : new ZonePart[0];
    }
}

public sealed class SingleZonePerFloorTypeComponent : FloorAggregatorComponent
{
    public SingleZonePerFloorTypeComponent()
        : base(
            "Single Zone per Floor Type",
            "1ZType",
            "One zone per floor entry (D-071): the storeys of entry i merge into zone E{i}. Slabs within an entry become internal mass (D-031), walls between merged zones are discarded (D-034), and floors and ceilings between entries stay between two zones (D-068). Every rebuilt outdoor wall gets one centred window with the glazed area of the windows it covers (D-079).")
    {
    }

    public override Guid ComponentGuid => new("506d5037-de93-4aee-a6c4-47dcc97509e1");

    protected override string MultiplierDescription => "How many storeys each floor stands for (stacked explicitly before merging). Default 1.";

    protected override IFloorAggregator CreateAggregator() => new SingleZonePerFloorType(ToleranceSettings.Default);
}

public sealed class SingleZoneBuildingComponent : FloorAggregatorComponent
{
    public SingleZoneBuildingComponent()
        : base(
            "Single Zone Building",
            "1ZBldg",
            "The whole building as one zone, BUILDING (D-021, D-071): slabs become internal mass (D-031), walls between merged zones are discarded (D-034). Every rebuilt outdoor wall gets one centred window with the glazed area of the windows it covers (D-079).")
    {
    }

    public override Guid ComponentGuid => new("50965154-e31e-4730-b61c-15a6f40bee6f");

    protected override string MultiplierDescription => "How many storeys each floor stands for (stacked explicitly before merging). Default 1.";

    protected override IFloorAggregator CreateAggregator() => new SingleZoneBuilding(ToleranceSettings.Default);
}
```

- [x] **Step 4: Replace `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` (full file)**

```csharp
using System;
using System.Drawing;
using System.Linq;
using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Lod.Core.Common;
using Lod.Core.Conversion;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Validation;
using Lod.Grasshopper.Convert;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;
using Rhino.Geometry;
using Surface = Lod.Core.Model.Surface;

namespace Lod.Grasshopper.Components;

/// <summary>
/// Converts a building into neutral Grasshopper data for a ClimateStudio definition (D-023, provisional): one tree branch per zone,
/// in building zone order. The output layout is documented in docs/architecture/convert2bem.md. The building is validated first; a failed
/// validation blocks conversion unless Override is set, and the override is recorded in the Provenance output (GLOBAL.md, scientific rule 6).
/// Interzone surfaces are written as adiabatic unless the heat-transfer options say otherwise (D-069, <see cref="HeatTransferOptions"/>); the
/// building itself is not changed, and the options are recorded in the Provenance output.
/// </summary>
public sealed class Convert2BemComponent : GH_Component
{
    public Convert2BemComponent()
        : base(
            "Convert2BEM",
            "2BEM",
            "Building to zone geometry, programs, and surfaces as data trees (branch {i} = zone i), ready to wire into a ClimateStudio definition. Provisional layout (D-023).",
            ComponentCategories.Category,
            ComponentCategories.Convert)
    {
    }

    public override Guid ComponentGuid => new("d091d70c-4de3-4f29-a900-ea4c9b777ba3");

    protected override Bitmap? Icon => IconLibrary.For(this);

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new BuildingParameter(), "Building", "Bldg", "The building.", GH_ParamAccess.item);
        pManager.AddBooleanParameter("Override", "Ovr", "Convert even if validation fails; the override is recorded.", GH_ParamAccess.item, false);
        pManager.AddBooleanParameter(
            nameof(HeatTransferOptions.EnableInternalWallHeatTransfer),
            "IWHT",
            "Write walls between two zones paired with the adjacent zone (Interzone:<zone ID>); when false they are written as Adiabatic (D-069).",
            GH_ParamAccess.item,
            false);
        pManager.AddBooleanParameter(
            nameof(HeatTransferOptions.EnableFloorHeatTransfer),
            "FHT",
            "Write floors and ceilings between two zones paired with the adjacent zone (Interzone:<zone ID>); when false they are written as Adiabatic (D-069).",
            GH_ParamAccess.item,
            false);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddBrepParameter("Zones", "Z", "{i}: closed Brep of each part of zone i, model units.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Names", "N", "{i}: zone ID.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Space Types", "ST", "{i}: space type.", GH_ParamAccess.tree);
        pManager.AddIntegerParameter("Multipliers", "M", "{i}: zone multiplier.", GH_ParamAccess.tree);
        pManager.AddBooleanParameter("Conditioned", "Cd", "{i}: whether zone i is conditioned (D-038).", GH_ParamAccess.tree);
        pManager.AddTextParameter("Load Types", "LT", "{i}: load types, aligned with Load Values.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Load Bases", "LB", "{i}: load bases.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Load Values", "LV", "{i}: design values in their basis.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Load Schedules", "LS", "{i;k}: 8760 fractions of load k of zone i.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Heating Setpoints", "HS", "{i}: 8760 heating setpoints, °C; empty for unconditioned zones.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Cooling Setpoints", "CS", "{i}: 8760 cooling setpoints, °C; empty for unconditioned zones.", GH_ParamAccess.tree);
        pManager.AddBrepParameter("Surfaces", "S", "{i}: walls, floors, and ceilings of zone i.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Boundaries", "B", "{i}: boundary written for each surface: Outdoors, Ground, Adiabatic, or Interzone:<zone ID>; interzone surfaces are Adiabatic unless their heat-transfer option is on (D-069).", GH_ParamAccess.tree);
        pManager.AddBrepParameter("Windows", "W", "{i}: windows of zone i, one centred window per glazed outdoor wall (D-026, D-079), at their positions in the walls.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Internal Mass", "IM", "{i}: exposed internal-mass area of zone i (slab area × exposed faces), m².", GH_ParamAccess.tree);
        pManager.AddTextParameter("Provenance", "P", "Building provenance, validation report, heat-transfer options, and any override.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        BuildingGoo? goo = null;
        bool overrideValidation = false;
        bool internalWalls = false;
        bool floors = false;
        if (!DA.GetData(0, ref goo) || goo is null || !DA.GetData(1, ref overrideValidation) || !DA.GetData(2, ref internalWalls) || !DA.GetData(3, ref floors))
        {
            return;
        }

        IGeneratedBuilding building = goo.Value;
        var options = new HeatTransferOptions(internalWalls, floors);
        ValidationReport report = new BuildingValidator(ToleranceSettings.Default).Validate(building);
        string record = building.Provenance.Describe() + report.Describe() + "OPTIONS: " + options.Describe() + "\n";
        if (!report.Passed && !overrideValidation)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Error(DiagnosticCodes.ValidationFailed, "Validation failed; conversion blocked. See Provenance, or set Override.") });
            DA.SetData(15, record);
            return;
        }

        if (!report.Passed)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Warning(DiagnosticCodes.ValidationOverridden, "Validation failed; converted because Override is set. The override is recorded in Provenance.") });
            record += "OVERRIDE: converted despite failed validation\n";
        }

        var zones = new DataTree<Brep>();
        var names = new DataTree<string>();
        var spaceTypes = new DataTree<string>();
        var multipliers = new DataTree<int>();
        var conditioned = new DataTree<bool>();
        var loadTypes = new DataTree<string>();
        var loadBases = new DataTree<string>();
        var loadValues = new DataTree<double>();
        var loadSchedules = new DataTree<double>();
        var heating = new DataTree<double>();
        var cooling = new DataTree<double>();
        var surfaces = new DataTree<Brep>();
        var boundaries = new DataTree<string>();
        var windows = new DataTree<Brep>();
        var mass = new DataTree<double>();

        for (int i = 0; i < building.Zones.Count; i++)
        {
            Zone zone = building.Zones[i];
            var path = new GH_Path(i);
            zones.AddRange(RhinoGeometry.ZoneBreps(zone), path);
            names.Add(zone.Id.Value, path);
            spaceTypes.Add(zone.SpaceType.ToString(), path);
            multipliers.Add(zone.Multiplier, path);
            conditioned.Add(zone.Program.IsConditioned, path);
            for (int k = 0; k < zone.Program.Loads.Count; k++)
            {
                LoadDefinition load = zone.Program.Loads[k];
                loadTypes.Add(load.Type.ToString(), path);
                loadBases.Add(load.Basis.ToString(), path);
                loadValues.Add(load.Value, path);
                loadSchedules.AddRange(load.Schedule.Values, new GH_Path(i, k));
            }

            heating.EnsurePath(path);
            cooling.EnsurePath(path);
            if (zone.Program.Thermostat is { } thermostat)
            {
                heating.AddRange(thermostat.HeatingSetpoint.Values, path);
                cooling.AddRange(thermostat.CoolingSetpoint.Values, path);
            }
            foreach (Surface surface in building.Surfaces.Where(s => s.Zone == zone.Id))
            {
                foreach (Brep brep in SurfaceBreps(surface))
                {
                    surfaces.Add(brep, path);
                    ExportedBoundary boundary = options.Exported(surface);
                    boundaries.Add(boundary.AdjacentZone is { } adjacent ? $"{boundary.Boundary}:{adjacent.Value}" : boundary.Boundary.ToString(), path);
                }

                if (surface is WallSurface wall)
                {
                    windows.AddRange(RhinoGeometry.WindowBreps(wall), path);
                }
            }

            mass.Add(building.InternalMasses.Where(m => m.Zone == zone.Id).Sum(m => m.SlabArea * m.ExposedFaces), path);
        }

        DA.SetDataTree(0, zones);
        DA.SetDataTree(1, names);
        DA.SetDataTree(2, spaceTypes);
        DA.SetDataTree(3, multipliers);
        DA.SetDataTree(4, conditioned);
        DA.SetDataTree(5, loadTypes);
        DA.SetDataTree(6, loadBases);
        DA.SetDataTree(7, loadValues);
        DA.SetDataTree(8, loadSchedules);
        DA.SetDataTree(9, heating);
        DA.SetDataTree(10, cooling);
        DA.SetDataTree(11, surfaces);
        DA.SetDataTree(12, boundaries);
        DA.SetDataTree(13, windows);
        DA.SetDataTree(14, mass);
        DA.SetData(15, record);
    }

    private static Brep[] SurfaceBreps(Surface surface) => surface switch
    {
        WallSurface wall => RhinoGeometry.WallBrep(wall) is { } brep ? new[] { brep } : new Brep[0],
        HorizontalSurface horizontal => RhinoGeometry.HorizontalBreps(horizontal).ToArray(),
        _ => new Brep[0],
    };
}
```

- [x] **Step 5: Build and check that only descriptions changed**

```bash
dotnet build BEMGen.sln -c Release
git diff --stat
git grep -n "D-079" -- src/Lod.Grasshopper
git grep -n -E "ComponentGuid => new\(" src/Lod.Grasshopper
```

Expected: `Build succeeded.`, `0 Warning(s)`, `0 Error(s)`; `3 files changed, 6 insertions(+), 6 deletions(-)`; six `D-079` lines (three in `SimplifierComponents.cs`, two in `AggregatorComponents.cs`, one in `Convert2BemComponent.cs`); 27 GUID lines (21 components, 6 parameters), the same as on `main`.

- [x] **Step 6: Commit**

```bash
git add src/Lod.Grasshopper/Components/SimplifierComponents.cs src/Lod.Grasshopper/Components/AggregatorComponents.cs src/Lod.Grasshopper/Components/Convert2BemComponent.cs
git commit -m "docs(grasshopper): describe centred windows on rebuilt walls"
```

- [x] **Step 7: Merge Slice C (D-004)**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch docs/grasshopper-centred-windows
git rebase main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git merge --ff-only docs/grasshopper-centred-windows
git branch -d docs/grasshopper-centred-windows
```

Expected: `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0. Do not push (D-080).

---

## Slice D — `docs/windows-centred-windows`

### Task 6: Architecture and research documents

**Files:**
- Modify: `docs/architecture/pipeline.md` (S4, last changed in S4.2), `docs/architecture/validation.md` (S3, last changed in S4.2), `docs/architecture/convert2bem.md` (S2, last changed in S4.2), `docs/research/program-presets.md` (S1, last changed in S4.1)

**Interfaces:**
- Consumes: Tasks 1–5 (rule, guards, types, descriptions).
- Produces: the pipeline, validation, *Convert2BEM*, and preset descriptions after S5; the heading `## Grasshopper components through S5` (anchor `#grasshopper-components-through-s5`), which the overview of `pipeline.md` and `program-presets.md` link to.

- [x] **Step 1: Create the branch**

```bash
git switch -c docs/windows-centred-windows main
```

- [x] **Step 2: Edit `docs/architecture/pipeline.md`**

Make these replacements, in order; each "Replace" text occurs exactly once in the file. Replacement 3 also points the *Preview Location* link at the renamed heading (it pointed at `#grasshopper-components-through-s41`, a heading S4.2 had already renamed).

1. Replace

```markdown
At Checkpoint 1 (stages S0–S4, D-030) the pipeline is complete for the linear plan; the revision stage S4.1 (D-061 to D-064) gave the plan generator one preset input per space type and added default preset components, a *Preview Location* input, and component icons; the revision stage S4.2 (D-068 to D-075, [ADR-013](../decisions/ADR-013-vertical-aggregation-methods.md)) added *Transform Plan*, made the floor aggregators designate floors and ceilings on the assembled stack, turned them into four methods, and made heat transfer between zones a conversion option. This document describes each step, the rules it applies, where results are validated, and the Grasshopper components that expose it. The domain types are described in [domain-model.md](domain-model.md), the validation checks in [validation.md](validation.md), and the `Convert2BEM` output layout in [convert2bem.md](convert2bem.md).
```

   with

```markdown
At Checkpoint 1 (stages S0–S4, D-030) the pipeline is complete for the linear plan; the revision stage S4.1 (D-061 to D-064) gave the plan generator one preset input per space type and added default preset components, a *Preview Location* input, and component icons; the revision stage S4.2 (D-068 to D-075, [ADR-013](../decisions/ADR-013-vertical-aggregation-methods.md)) added *Transform Plan*, made the floor aggregators designate floors and ceilings on the assembled stack, turned them into four methods, and made heat transfer between zones a conversion option; stage S5 (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)) gives every rebuilt outdoor wall one centred window with the glazed area it covers. This document describes each step, the rules it applies, where results are validated, and the Grasshopper components that expose it. The domain types are described in [domain-model.md](domain-model.md), the validation checks in [validation.md](validation.md), and the `Convert2BEM` output layout in [convert2bem.md](convert2bem.md).
```

2. Replace

```text
  → IPlanSimplifier      NoSimplification | SemanticMerge |                 → IFloor                Z0 | Z1 | Z2 | Z3, windows kept in place (W0)
                         PerimeterCore | SingleZonePerFloor
  (window transformation W1–W5: stage S5, not in Checkpoint 1)
```

   with

```text
  → IPlanSimplifier      NoSimplification | SemanticMerge |                 → IFloor                Z0 | Z1 | Z2 | Z3, one centred window per rebuilt wall (D-079)
                         PerimeterCore | SingleZonePerFloor
```

3. Replace

```markdown
- All logic lives in `Lod.Core` and `Lod.Generators`, which reference neither Rhino nor Grasshopper; their tests run with `dotnet test`. `Lod.Grasshopper` wraps each pipeline type in a Goo with a viewport preview and exposes one component per step (D-017, D-018). Every component that previews a plan, floor, or building has a last input *Preview Location* that moves only its preview (D-062, [below](#grasshopper-components-through-s41)).
```

   with

```markdown
- All logic lives in `Lod.Core` and `Lod.Generators`, which reference neither Rhino nor Grasshopper; their tests run with `dotnet test`. `Lod.Grasshopper` wraps each pipeline type in a Goo with a viewport preview and exposes one component per step (D-017, D-018). Every component that previews a plan, floor, or building has a last input *Preview Location* that moves only its preview (D-062, [below](#grasshopper-components-through-s5)).
```

4. Replace

```markdown
- At Checkpoint 1 every zoning level keeps the generator's windows unchanged (W0). The window axis W1–W5 of the research brief is stage S5 (D-039).
```

   with

```markdown
- Windows are not a separate axis (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)). Wherever zones are merged and walls are rebuilt (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, *Single Zone Building*), every outdoor wall carries exactly one window, centred on it by the generator's rule (D-026), whose area is the glazed area of the source windows it covers; a wall without glazing has none. Glazed area is conserved per wall, and so per façade, orientation, and building; window positions are not. *No Simplification*, *Stack Floors*, and *Stacked Floor Zone Multiplier* keep their input's windows. The window levels W1–W5 of the earlier research brief are dropped.
```

5. Replace

```markdown
| Decisions | D-019, D-034, D-038, D-039, D-041, D-047; ADR-005, ADR-007, [ADR-008](../decisions/ADR-008-perimeter-core-corners.md) |
```

   with

```markdown
| Decisions | D-019, D-034, D-038, D-039, D-041, D-047, D-079; ADR-005, ADR-007, [ADR-008](../decisions/ADR-008-perimeter-core-corners.md), [ADR-012](../decisions/ADR-012-centred-windows.md) |
```

6. Replace

```markdown
- The other simplifiers share one procedure (`PlanSimplifier`). A strategy proposes target footprints; source zones are mapped to targets by overlap area (`ZoneMapping`); surfaces are rebuilt, so walls between merged sources disappear (D-034); the target outdoor walls must cover every source outdoor wall over its full length (D-041, error `FacadeNotCovered`); every source window is re-hosted unchanged on the target wall that contains it (D-039, `WindowRehosting`, error `WindowNotHosted`); programs are aggregated through the transfer fractions.
```

   with

```markdown
- The other simplifiers share one procedure (`PlanSimplifier`). A strategy proposes target footprints; source zones are mapped to targets by overlap area (`ZoneMapping`); surfaces are rebuilt, so walls between merged sources disappear (D-034); the target outdoor walls must cover every source outdoor wall over its full length (D-041, error `FacadeNotCovered`); every source window is attributed to the target outdoor wall that contains it (`WindowRehosting`, D-039), and every target outdoor wall then gets one window centred on it with the total area of the windows attributed to it (`CentredWindows`, D-079), shaped like the generator's windows (`Window.Centered`, D-026) and none when that area is zero; a window that no single target wall contains (`WindowNotHosted`) and a wall whose glazed area is not smaller than its area (`GlazingExceedsWall`) are errors that hold by construction once the façades are covered, checked rather than repaired; programs are aggregated through the transfer fractions.
```

7. Replace

```markdown
| Decisions | D-018, D-021, D-031, D-032, D-034, D-039, D-041, D-045, D-046, D-068, D-071, D-072, D-074, D-075; [ADR-009](../decisions/ADR-009-vertical-aggregation.md), [ADR-013](../decisions/ADR-013-vertical-aggregation-methods.md) |
```

   with

```markdown
| Decisions | D-018, D-021, D-031, D-032, D-034, D-039, D-041, D-045, D-046, D-068, D-071, D-072, D-074, D-075, D-079; [ADR-009](../decisions/ADR-009-vertical-aggregation.md), [ADR-013](../decisions/ADR-013-vertical-aggregation-methods.md) |
```

8. Replace

```markdown
| `SingleZonePerFloorType` | one zone `E{i}` ("Floor type i") per floor entry, spanning its Nᵢ storeys, one part per storey outline | explicit repetition | ground, roof, and exposed pieces kept; pieces between two entries `Interzone` between `E{i}` and `E{i+1}` | rebuilt per storey outline, all outdoors, covering every source façade (D-041); every window kept in place (D-039); partitions discarded (D-034) | one per slab level within an entry: slab area, 2 exposed faces (D-031) |
```

   with

```markdown
| `SingleZonePerFloorType` | one zone `E{i}` ("Floor type i") per floor entry, spanning its Nᵢ storeys, one part per storey outline | explicit repetition | ground, roof, and exposed pieces kept; pieces between two entries `Interzone` between `E{i}` and `E{i+1}` | rebuilt per storey outline, all outdoors, covering every source façade (D-041); one centred window per wall with the glazed area it covers (D-079); partitions discarded (D-034) | one per slab level within an entry: slab area, 2 exposed faces (D-031) |
```

9. Replace

```markdown
| Plan simplifiers | Strategy preconditions (`InvalidParameter`, `PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`); façade coverage (`FacadeNotCovered`); every window hosted by one target wall (`WindowNotHosted`) | Error; no floor |
| Floor aggregators | At least one floor (`NoFloors`); multipliers from 1 (`InvalidParameter`); one orientation (`OrientationMismatch`); façade coverage and window hosting (`FacadeNotCovered`, `WindowNotHosted`, single-zone methods). A storey not carried by the storey below is the warning `UnsupportedStorey` (D-074). `StackedFloorZoneMultiplier` rejects no input for exposure: it splits exposed storeys of multiplied types off and reports the info `FloorTypeSplit` (D-046) | Error; no building (`UnsupportedStorey` is a warning and `FloorTypeSplit` a remark; the building is produced) |
```

   with

```markdown
| Plan simplifiers | Strategy preconditions (`InvalidParameter`, `PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`); façade coverage (`FacadeNotCovered`); guards of the centred-window rule, which hold by construction once the façades are covered (D-079): every window contained by one target wall (`WindowNotHosted`), glazing of each target wall smaller than its area (`GlazingExceedsWall`) | Error; no floor |
| Floor aggregators | At least one floor (`NoFloors`); multipliers from 1 (`InvalidParameter`); one orientation (`OrientationMismatch`); façade coverage and the centred-window guards (`FacadeNotCovered`, `WindowNotHosted`, `GlazingExceedsWall`, single-zone methods). A storey not carried by the storey below is the warning `UnsupportedStorey` (D-074). `StackedFloorZoneMultiplier` rejects no input for exposure: it splits exposed storeys of multiplied types off and reports the info `FloorTypeSplit` (D-046) | Error; no building (`UnsupportedStorey` is a warning and `FloorTypeSplit` a remark; the building is produced) |
```

10. Replace

```markdown
## Grasshopper components through S4.2
```

   with

```markdown
## Grasshopper components through S5
```

11. Replace

```markdown
- **Aggregator previews (D-071, D-075).** *Stacked Floor Zone Multiplier* previews the whole stacked building: the modelled storeys as before and the storeys that are represented but not modelled in transparent grey (`StackedFloorZoneMultiplier.UnmodelledStoreys`). A zone with several parts (*Single Zone per Floor Type*, *Single Zone Building*) is previewed as one merged volume, with its windows. Only the preview changes: the building and the *Convert2BEM* outputs keep one part per storey outline.
```

   with

```markdown
- **Aggregator previews (D-071, D-075).** *Stacked Floor Zone Multiplier* previews the whole stacked building: the modelled storeys as before and the storeys that are represented but not modelled in transparent grey (`StackedFloorZoneMultiplier.UnmodelledStoreys`). A zone with several parts (*Single Zone per Floor Type*, *Single Zone Building*) is previewed as one merged volume, with its windows. Only the preview changes: the building and the *Convert2BEM* outputs keep one part per storey outline.
- **Windows (S5, D-079).** No component was added or removed and no GUID changed. The descriptions of *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* state that every rebuilt outdoor wall gets one centred window with the glazed area it covers, and the *Windows* output of *Convert2BEM* is described as one centred window per glazed outdoor wall.
```

12. Replace

```markdown
| --- | --- | --- |
| Window transformations W1–W5 (equivalent windows, WWR per façade, redistributed windows, orientation-level and building-level WWR), with glazing validation scoped by the declared W-level | S5 | ADR-012 |
```

   with

```markdown
| --- | --- | --- |
```

- [x] **Step 3: Edit `docs/architecture/validation.md`**

Make these replacements, in order; each "Replace" text occurs exactly once in the file.

1. Replace

```markdown
Validation applies to objects that exist. A simplifier that cannot produce a valid floor fails earlier, with its own diagnostics (`PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`, `FacadeNotCovered`, `WindowNotHosted`, gaps and overlaps from the surface builder, aggregation errors), and returns no floor.
```

   with

```markdown
Validation applies to objects that exist. A simplifier that cannot produce a valid floor fails earlier, with its own diagnostics (`PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`, `FacadeNotCovered`, the centred-window guards `WindowNotHosted` and `GlazingExceedsWall` (D-079), gaps and overlaps from the surface builder, aggregation errors), and returns no floor.
```

2. Replace

```markdown
- Window positions and sizes. Simplifiers keep every window unchanged by construction (`WindowRehosting`, D-039; covered by its unit tests); validation compares the glazed areas.
```

   with

```markdown
- Window positions and sizes. Where walls are rebuilt, each outdoor wall gets one window centred on it with the glazed area of the source windows it covers (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)), so individual windows are not conserved by design; the rule is covered by the unit tests of `CentredWindows` and the integration tests `CentredWindowTests`. Validation compares the glazed areas in total and per orientation, which the rule conserves per wall. Every window is checked per wall when it is built, not by validation: a source window must lie on one target wall (`WindowNotHosted`) and a wall's glazed area must be smaller than its area (`GlazingExceedsWall`); both hold by construction once the façades are covered (D-041) and are kept as guards.
```

- [x] **Step 4: Edit `docs/architecture/convert2bem.md`**

Make this replacement; the "Replace" text occurs exactly once in the file.

1. Replace

```markdown
| 13 | Windows | W | `{i}`: Breps | Every explicit window of the zone's walls, as a rectangle in the wall's plane at its offset along the wall and its sill height (D-039). For S2 buildings that is one centered window per outdoor wall, as the generator placed it (D-026). | model units |
```

   with

```markdown
| 13 | Windows | W | `{i}`: Breps | Every explicit window of the zone's walls, as a rectangle in the wall's plane at its offset along the wall and its sill height (D-039). That is one centred window per glazed outdoor wall: as the generator placed it (D-026) where walls are not rebuilt, and with the glazed area of the source windows the wall covers where zones are merged (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)). | model units |
```

- [x] **Step 5: Edit `docs/research/program-presets.md`**

Make these replacements, in order; each "Replace" text occurs exactly once in the file. Replacement 3 points the link at the renamed heading of `pipeline.md`.

1. Replace

```markdown
> **Status:** Current as of S4.1 (`v0.4.1`) · **Date:** 2026-10-01 · **Decisions:** D-009, D-024, D-026, D-038, D-039, D-047, D-061
```

   with

```markdown
> **Status:** Current as of S4.1 (`v0.4.1`) · **Date:** 2026-10-01 · **Decisions:** D-009, D-024, D-026, D-038, D-039, D-047, D-061, D-079
```

2. Replace

```markdown
**Windows.** Walls carry explicit windows (D-039). The S2 linear plan generator uses the preset's WWR for one simple rule: one window centred on each outdoor wall of a zone, with area = WWR × wall area (D-026). Plan simplifiers keep every window unchanged and re-host it on the target wall that contains it (W0); window transformations (W1–W5) are a later stage, S5.
```

   with

```markdown
**Windows.** Walls carry explicit windows (D-039). The S2 linear plan generator uses the preset's WWR for one simple rule: one window centred on each outdoor wall of a zone, with area = WWR × wall area (D-026). Where zones are merged and walls are rebuilt, each outdoor wall gets one window centred on it with the glazed area of the source windows it covers, shaped by the same rule, so the preset's glazing is conserved per wall, façade, orientation, and building (D-079, S5).
```

3. Replace

```markdown
S4.1 adds one default preset component per space type of the linear plan, *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset*, and deletes *Example Residential Presets* (D-061). Every input of a default preset component has a default, the values of §2, so the component works with nothing connected: Name, WWR, Conditioned, Heating (°C), Cooling (°C), and per load a value input (people/m², W/m², or 1/h, as in its description) and an optional schedule input that replaces the built-in schedule when connected. Each shows the remark "Illustrative values; not sourced from DOE prototypes or standards." Their inputs and outputs are listed in [pipeline.md](../architecture/pipeline.md#grasshopper-components-through-s41).
```

   with

```markdown
S4.1 adds one default preset component per space type of the linear plan, *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset*, and deletes *Example Residential Presets* (D-061). Every input of a default preset component has a default, the values of §2, so the component works with nothing connected: Name, WWR, Conditioned, Heating (°C), Cooling (°C), and per load a value input (people/m², W/m², or 1/h, as in its description) and an optional schedule input that replaces the built-in schedule when connected. Each shows the remark "Illustrative values; not sourced from DOE prototypes or standards." Their inputs and outputs are listed in [pipeline.md](../architecture/pipeline.md#grasshopper-components-through-s5).
```

- [x] **Step 6: Check the documents**

```bash
git grep -n -E "kept in place|W1–W5: stage|window transformation|#grasshopper-components-through-s4" -- docs/architecture docs/research
git grep -n "^## Grasshopper components through" -- docs/architecture/pipeline.md
```

Expected: no output for the first command; one line, `## Grasshopper components through S5`, for the second.

- [x] **Step 7: Commit**

```bash
git add docs/architecture/pipeline.md docs/architecture/validation.md docs/architecture/convert2bem.md docs/research/program-presets.md
git commit -m "docs(windows): describe centred windows on rebuilt walls"
```

### Task 7: S5 smoke-test checklist

**Files:**
- Modify: `docs/development/grasshopper-smoke-test.md` (append)

**Interfaces:**
- Consumes: the plugin built from Slices A–C.
- Produces: the checklist that Task 8 runs.

- [x] **Step 1: Append the S5 checklist at the end of `docs/development/grasshopper-smoke-test.md`**

Append this section after the last line of the file (after the S4.2 checklist), separated by one blank line, so that it nests under `## Stage checklists` like the S2–S4.2 checklists:

```markdown
### S5 checklist — centred windows on rebuilt walls (`v0.5.0`)

S5 changes no component, input, output, icon, or GUID; only the windows of merged zones change (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)). Where earlier checklists expect the simplified or single-zone floors to show the plan's windows in place (S3 *Simplifiers* step 2, S4.2 *Aggregation methods* step 2), this checklist replaces those expectations.

#### Simplifiers

1. Connect the canonical plan (default *Linear Plan Generator* with the three default preset components) to the four plan simplifiers (*Perimeter Core* with *Depth* 4.57).
   - [x] *No Simplification* shows the generator's ten windows: three on the south façade, three on the north, three on the east, and one on the west.
   - [x] *Semantic Merge* shows one window per glazed outdoor wall, eight in all: the stair keeps its three, the corridor its one on the east, each dwelling-unit zone one on its long façade (`DwellingUnit-1/W4 … glazing=18.000000 window(offset=4.522774 sill=0.678416 10.954451x1.643168)` in *Inspect*) and one on the east.
   - [x] *Perimeter Core* and *Single Zone per Floor* show one window per façade, four in all, each centred on its wall: south and north 12.393547 m × 1.549193 m at sill 0.725403 m (the south one from x = 5.803227 to 18.196773 m), east 9.674709 m × 1.612452 m at sill 0.693774 m (y = 4.162645 to 13.837355 m), west 5.692100 m × 0.948683 m at sill 1.025658 m (y = 6.153950 to 11.846050 m). The core has no window.
   - [x] Each *Inspect* report equals the matching snapshot in `tests/Lod.Integration.Tests/Snapshots/`; every outdoor wall line ends with at most one `window(…)` entry.
   - [x] *Validate* on each simplified floor gives Passed = True, and the lines `Glazing` and `Glazing.<orientation>` read `ok` with the same values as *Validate* on the *No Simplification* floor (59.4 m² in total: 19.2 south, 19.2 north, 15.6 east, 5.4 west).

#### Single-zone aggregators

2. Connect the *No Simplification* floor three times with Multipliers 1, 3, 1 to *Single Zone per Floor Type* and to *Single Zone Building*.
   - [x] Every storey shows four windows, one centred on each façade, with the sizes of step 1 (*Single Zone Building*: 20 windows on 5 storeys).
   - [x] *Stack Floors* and *Stacked Floor Zone Multiplier* on the same floors still show the generator's ten windows per modelled storey.
   - [x] *Validate* on each building gives Passed = True with `Building.Glazing` = 297 m² (5 × 59.4).
   - [x] *Convert2BEM*: *Windows* {0} holds 20 Breps for *Single Zone Building*.

#### Rotated plan

3. Put the canonical plan through *Transform Plan* with the 30° rotation and the move by 5.3, −2.1, 0 of the S4.2 checklist, then through each simplifier and each aggregator (Multipliers 1, 3, 1).
   - [x] The merged walls carry one window each, centred on the rotated wall (in *Inspect*, `offset` equals (wall length − window width) / 2 for every window).
   - [x] *Validate* gives Passed = True for all 16 combinations, with the same `Glazing.<orientation>` values as the rotated *No Simplification* floor, and no aggregator shows a runtime message.
```

- [x] **Step 2: Commit**

```bash
git add docs/development/grasshopper-smoke-test.md
git commit -m "docs(development): add the s5 smoke-test checklist"
```

### Task 8: Smoke test in Rhino 8 (manual, person; or the controller headless, D-056)

**Files:** none (the result goes into the body of the close-out commit, Task 9, Step 8)

- [x] **Step 1: Build the branch**

```bash
dotnet build BEMGen.sln -c Release
git rev-parse HEAD
```

Expected: `Build succeeded.`, `0 Warning(s)`, `0 Error(s)`. Note the SHA.

- [x] **Step 2: Run the S5 checklist (person in Rhino 8, or the controller headless)**

Load the plugin as `docs/development/grasshopper-smoke-test.md` describes and tick every item of the S5 checklist. In this run (D-080, under the rules of D-066) the controller runs the checks that do not need a viewport as a scripted headless Grasshopper session (D-056: Rhino 8 `/nosplash /netcore` with `RHINO_PACKAGE_DIRS` pointing at `src/Lod.Grasshopper/bin/Release/net7.0/`, components placed by GUID, states, messages, outputs, data trees, and the Breps of *Convert2BEM*'s *Windows* output with their areas and bounding boxes written to a file). The following values are expected; they were observed in such a session on the verified reference (Rhino 8.25.25314.11001, .NET 8.0.31; *BEMGen Info* version text `0.4.2+<sha>`, since the bump to 0.5.0 comes in Task 9). The canonical plan is the three default preset components → *Linear Plan Generator* with its default inputs; "1, 3, 1" means a simplified floor given three times to an aggregator with those multipliers.

1. **Registration.** Unchanged from S4.2: 21 components and 6 parameters, each with a 24 × 24 icon, plus a 24 × 24 assembly icon, with their S4.2 panels, names, nicknames, GUIDs, and exposures (*3 Simplify*: *No Simplification* Z0 `83270abe-a13f-4f4c-a893-79739ad6e006`, *Semantic Merge* Z1 `7d36f1d3-2708-4b69-b1a7-cf294c186e9a`, *Perimeter Core* Z2 `6a86b976-c838-427f-93a7-344dcc2c18ce`, *Single Zone per Floor* Z3 `4ff83222-5b7d-4d1b-8f26-fd580893a5db`; *4 Aggregate*: *Stack Floors* `6ce6524d-09b0-49fc-9b88-4c15bdcc8797`, *Stacked Floor Zone Multiplier* `e4b44821-c9ed-49b9-9c4e-7c08355254dd`, *Single Zone per Floor Type* `506d5037-de93-4aee-a6c4-47dcc97509e1`, *Single Zone Building* `50965154-e31e-4730-b61c-15a6f40bee6f`; *Convert2BEM* `d091d70c-4de3-4f29-a900-ea4c9b777ba3`).
2. **Canonical plan through every combination.** Each of the four simplifiers, its floor given 1, 3, 1 to each of the four aggregators, each building to *Convert2BEM* and *Validate*: no runtime message on any simplifier, aggregator, *Convert2BEM*, or *Validate* (the preset components show only their remark), and *Validate* Passed = `True` for all 16 buildings. *Convert2BEM* *Windows* (Breps in branches):

   | Simplifier | *Stack Floors* | *Stacked Floor Zone Multiplier* | *Single Zone per Floor Type* | *Single Zone Building* |
   | --- | --- | --- | --- | --- |
   | *No Simplification* | 50 in 30 | 30 in 18 | 20 in 3 (4, 12, 4) | 20 in 1 |
   | *Semantic Merge* | 40 in 20 | 24 in 12 | 20 in 3 (4, 12, 4) | 20 in 1 |
   | *Perimeter Core* | 20 in 25 (core branches empty) | 12 in 15 | 20 in 3 (4, 12, 4) | 20 in 1 |
   | *Single Zone per Floor* | 20 in 5 | 12 in 3 | 20 in 3 (4, 12, 4) | 20 in 1 |

   The windows span z = 0.678416 to 14.321584 m where generator windows remain (*Stack Floors* and *Stacked Floor Zone Multiplier* on the *No Simplification* and *Semantic Merge* floors) and z = 0.693774 to 14.306226 m everywhere else.
3. **Rotated plan.** The canonical plan through *Transform Plan* with the transform of a 30° rotation about the world z axis followed by a move by (5.3, −2.1, 0), then the 16 combinations of item 2: no runtime message (including *Transform Plan*), *Validate* Passed = `True` for all 16, and the same *Windows* counts and branches as item 2.
4. **Window shapes, one storey.** Each simplified canonical floor given once to *Stack Floors*, then *Convert2BEM* *Windows*: *No Simplification* 10 Breps in 6 branches (3, 1, 1, 2, 1, 2); *Semantic Merge* 8 in 4 (3, 1, 2, 2), the dwelling-unit south window 18 m² from x = 8.522774 to 19.477226 m at y = 0, z = 0.678416 to 2.321584 m; *Perimeter Core* 4 in 5 (1, 1, 1, 1, and the empty core) and *Single Zone per Floor* 4 in 1, the same four windows: north 19.2 m², x = 5.803227 to 18.196773 m at y = 18, z = 0.725403 to 2.274597 m; east 15.6 m², y = 4.162645 to 13.837355 m at x = 24, z = 0.693774 to 2.306226 m; south 19.2 m², the north window's x and z at y = 0; west 5.4 m², y = 6.153950 to 11.846050 m at x = 0, z = 1.025658 to 1.974342 m.

Items that a headless session cannot observe stay open for a person (D-056, D-058): the windows in the viewport preview of each simplifier and aggregator, the toolbar and canvas icons, the *Inspect* reports compared with the snapshots and the `offset` check on the rotated walls (the core and integration tests of Tasks 2–4 check both), the `Glazing` and `Glazing.<orientation>` lines of *Validate* (only Passed was recorded; `CentredWindowTests` checks the glazing per orientation), and *Duplicate Data* for the repeated floor (the headless session uses separate floors). No example definition is part of S5; the pending S4 definition (`examples/grasshopper/checkpoint-1-pipeline.gh`) stays person-only (D-058).

Any failure stops the stage: fix it on this branch with a test (core) or a build plus smoke test (Grasshopper) before continuing. Write down, following the guide's "Recording the result": who tested and how (person in Rhino, or the controller headless per D-056), when, the Rhino version and runtime, the SHA, the *BEMGen Info* version text, pass or fail for each item, and the items not performed.

- [x] **Step 3: Merge Slice D (D-004)**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch docs/windows-centred-windows
git rebase main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git merge --ff-only docs/windows-centred-windows
git branch -d docs/windows-centred-windows
```

Expected: `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0. Do not push (D-080).

---

## Stage close-out

### Task 9: Version 0.5.0, S5 records, tag `v0.5.0`

**Files:**
- Modify: `Directory.Build.props`, `AGENTS.md`, `README.md`, `docs/plans/2026-09-30-implementation-roadmap.md`, `docs/decisions/decision-log.md`, `docs/plans/2026-10-01-s5-centred-windows.md` (this plan: checkboxes and status, D-051)

**Interfaces:**
- Consumes: the merged Slices A–D; the smoke-test record of Task 8; `BuildInfoTests.InformationalVersionStartsWithTheAssemblyVersion` (S0), which keeps passing after the bump.
- Produces: the local tag `v0.5.0`; the S5 records.

The decision-log entry in Step 7 has one field filled in when this task runs: `<date>`, the date the stage is closed (ISO format, `YYYY-MM-DD`). It is decided by the controller (unsupervised run, D-080) and Provisional. The roadmap Progress line of Step 6 carries the same `<date>`. The commit body of Step 8 uses the values written down in Task 8. The close-out uses its own branch, as the S1–S4.2 close-outs do.

- [x] **Step 1: Create the branch and run the gate**

```bash
git switch -c chore/repo-s5-close-out main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0.

- [x] **Step 2: Bump the version in `Directory.Build.props`**

Replace

```xml
    <Version>0.4.2</Version>
```

with

```xml
    <Version>0.5.0</Version>
```

Full file after this step:

```xml
<Project>
  <PropertyGroup>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <Deterministic>true</Deterministic>
    <Version>0.5.0</Version>
    <Authors>Environmental Systems Lab</Authors>
    <Product>BEMGen</Product>
  </PropertyGroup>

  <!-- Records and init accessors on netstandard2.0 (ADR-001). -->
  <ItemGroup Condition="'$(TargetFrameworkIdentifier)' != '.NETCoreApp'">
    <Compile Include="$(MSBuildThisFileDirectory)src\Shared\IsExternalInit.cs" Link="Polyfills\IsExternalInit.cs" />
  </ItemGroup>
</Project>
```

- [x] **Step 3: Check the version test**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.BuildInfoTests"
```

Expected: `Passed!  - Failed:     0, Passed:     1, Skipped:     0, Total:     1` for net8.0.

- [x] **Step 4: Commit the version**

```bash
git add Directory.Build.props
git commit -m "build(repo): set version 0.5.0"
```

- [x] **Step 5: Update `AGENTS.md` and `README.md`**

In `AGENTS.md`, replace everything between the heading `## Project state` and the heading `## Commands` (both headings stay) with:

```markdown
Checkpoint 1 (D-030) is reached: stages S0–S4 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.4.0`), and so are the revision stages S4.1 (tag `v0.4.1`, D-064) and S4.2 (tag `v0.4.2`, D-073) and stage S5 (tag `v0.5.0`, D-079). The pipeline runs end to end for the linear plan: program presets → `LinearPlanGenerator` (one typed preset per space type, D-061; optionally rotated and moved by `PlanTransform`, D-070) → plan simplifiers (`NoSimplification`, `SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`) → floor aggregators (`Stack`, `StackedFloorZoneMultiplier`, `SingleZonePerFloorType`, `SingleZoneBuilding`, D-071; floors and ceilings designated on the assembled stack, D-068) → validation → `Convert2BEM` (heat transfer between zones an export option, off by default, D-069), as described in [docs/architecture/pipeline.md](docs/architecture/pipeline.md). Wherever zones are merged and walls are rebuilt (`SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`, `SingleZonePerFloorType`, `SingleZoneBuilding`), every outdoor wall carries one centred window with the glazed area of the source windows it covers (`CentredWindows`, D-079, [ADR-012](docs/decisions/ADR-012-centred-windows.md)); the other steps keep their input's windows. Vertical aggregation follows [ADR-013](docs/decisions/ADR-013-vertical-aggregation-methods.md), which supersedes [ADR-009](docs/decisions/ADR-009-vertical-aggregation.md) where it differs. ADR-012, ADR-013, and the S4.2 and S5 plans were accepted by the controller and await the owner's reading (D-075, D-080). In Grasshopper every component has an icon drawn by `scripts/make_icons.py` (D-063), and the generator, *Transform Plan*, simplifier, and aggregator components have a *Preview Location* input that moves only their preview (D-062). Until the owner says otherwise, changes need not keep backward compatibility, but component GUIDs never change (D-064).

Not implemented yet: `Lod.Export` and Convert2IDF (S6), the precedent study (S7), the refined linear, point, and courtyard typologies (S8), and Grasshopper UX and release (S9). The example program presets hold illustrative values, not DOE prototype values, and the `Convert2BEM` output layout stays provisional until a ClimateStudio reference definition exists (D-023).

```

In `README.md`, replace everything between the heading `## Status` and the heading `## What it does` (both headings stay) with:

```markdown
Checkpoint 1 reached: stages S0–S4 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.4.0`), followed by the revision stages S4.1 (tag `v0.4.1`) and S4.2 (tag `v0.4.2`) and stage S5 (tag `v0.5.0`). In Rhino 8 the plugin runs the whole pipeline for a linear plan: program presets with conditioning (a default preset component per space type), the linear plan generator with one preset input per space type and explicit windows, *Transform Plan* to rotate and move a plan, four plan simplifiers (Z0–Z3), four floor aggregators (Stack, StackedFloorZoneMultiplier, SingleZonePerFloorType, SingleZoneBuilding) that designate floors and ceilings on the assembled stack and warn about unsupported storeys, invariant validation, and `Convert2BEM`, which writes heat transfer between zones only when asked (off by default). Wherever zones are merged and walls are rebuilt, every outdoor wall carries one centred window with the glazed area of the windows it covers, so glazing is conserved per wall, façade, orientation, and building (D-079). Every component has an icon, and every component with a viewport preview has a *Preview Location* input that moves only its preview. The pipeline is described in [docs/architecture/pipeline.md](docs/architecture/pipeline.md); the example definition `examples/grasshopper/checkpoint-1-pipeline.gh`, which wires every simplifier into every aggregator, is still to be built by a person. Next: Convert2IDF (S6) and the precedent study (S7). The `Convert2BEM` output stays provisional until a ClimateStudio reference definition exists (D-023), and the example program presets hold illustrative values, not DOE prototype values.

```

In `README.md`, make these replacements; each "Replace" text occurs exactly once in the file.

1. Replace

```text
  → IPlanSimplifier (NoSimplification, SemanticMerge, PerimeterCore, SingleZonePerFloor)   → IFloor   windows kept in place
  → window transformation (W1–W5, stage S5)   → IFloor
```

   with

```text
  → IPlanSimplifier (NoSimplification, SemanticMerge, PerimeterCore, SingleZonePerFloor)   → IFloor   one centred window per rebuilt wall
```

2. Replace

```markdown
Walls carry explicit windows: the first generator places one centered window per exterior wall from the preset's window-to-wall ratio, simplifiers keep every window where it is, and window transformations are a separate axis.
```

   with

```markdown
Walls carry explicit windows: the first generator places one centered window per exterior wall from the preset's window-to-wall ratio, and wherever zones are merged and walls are rebuilt, each outdoor wall gets one centred window with the glazed area of the windows it covers.
```

- [x] **Step 6: Update the roadmap**

In `docs/plans/2026-09-30-implementation-roadmap.md`, insert these two lines directly below the S4.2 Progress line (the last `> **Progress:**` line), so that a `>` separator line stays between consecutive lines:

```markdown
>
> **Progress:** <date> · S5 Centred windows on rebuilt walls complete (tag `v0.5.0`; `main`, `v0.4.2`, and `v0.5.0` are pushed after the fresh-clone gate, D-080); next: S6 and S7. `CentredWindows` gives every outdoor wall rebuilt by *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* one window centred by the generator's rule with the glazed area of the source windows it covers (D-079, ADR-012); glazing per wall, façade, orientation, and building and every validation report unchanged; new error `GlazingExceedsWall`; six snapshots changed in their window entries only; 142 core, 19 generator, and 187 integration tests pass on `net8.0`.
```

Then make these replacements, in order; each "Replace" text occurs exactly once in the file. The first adds the S5 row to the detailed-plans table; the others update the pipeline block, the window constraint of the global constraints, and the `Simplification/` line of §2 (target repository layout).

1. Replace

```markdown
| S4.2 | [2026-10-01-s4.2-aggregation-transform-heat-transfer.md](2026-10-01-s4.2-aggregation-transform-heat-transfer.md) | 136 core, 19 generators, 163 integration |
```

   with

```markdown
| S4.2 | [2026-10-01-s4.2-aggregation-transform-heat-transfer.md](2026-10-01-s4.2-aggregation-transform-heat-transfer.md) | 136 core, 19 generators, 163 integration |
| S5 | [2026-10-01-s5-centred-windows.md](2026-10-01-s5-centred-windows.md) | 142 core, 19 generators, 187 integration |
```

2. Replace

```text
  → IPlanSimplifier                                  → IFloor              windows kept in place (W0)
       NoSimplification | SemanticMerge | PerimeterCore | SingleZonePerFloor
  → window transformation (S5, W1–W5)                → IFloor
```

   with

```text
  → IPlanSimplifier                                  → IFloor              one centred window per rebuilt wall (D-079)
       NoSimplification | SemanticMerge | PerimeterCore | SingleZonePerFloor
```

3. Replace

```markdown
- Walls carry explicit windows (position, sill, width, height; any number per wall). The first generator places one centered window per outdoor wall sized from the preset's WWR (D-026); simplifiers and floor aggregators keep every window in place (W0); window transformations W1–W5 are stage S5 (D-039).
```

   with

```markdown
- Walls carry explicit windows (position, sill, width, height; any number per wall). The first generator places one centered window per outdoor wall sized from the preset's WWR (D-026); wherever zones are merged and walls rebuilt, every outdoor wall carries one centred window, shaped by the same rule, with the glazed area of the source windows it covers, so glazing is conserved per wall, façade, orientation, and building; steps that do not rebuild walls keep their input's windows (D-079, ADR-012). There are no window levels W1–W5.
```

4. Replace

```text
    Simplification/ IPlanSimplifier, NoSimplification, OverlapMapper, TransferMatrix, FacadeAttribution, WindowRehosting, SemanticMerge, PerimeterCore, SingleZonePerFloor
```

   with

```text
    Simplification/ IPlanSimplifier, NoSimplification, OverlapMapper, TransferMatrix, FacadeAttribution, WindowRehosting, CentredWindows, SemanticMerge, PerimeterCore, SingleZonePerFloor
```

The S5 row of the stage table, the S5 section, the sentence below the stage diagram, the S8 test line, the risk row, §7, and the revision note v7 were committed with this plan and stay as they are.

- [x] **Step 7: Append the decision-log entry (template; fill `<date>` now)**

Append at the end of `docs/decisions/decision-log.md`, after a blank line. The log ends with D-080 when this plan is approved, so the entry is D-081; if the log ends with another number, use the next free number and say so in the commit body.

```markdown
### D-081 — S5 complete

- **Date:** <date> · **Decided by:** controller (unsupervised run, D-080) · **Status:** Provisional
- Stage S5 (D-079) is complete and tagged `v0.5.0`. [ADR-012](ADR-012-centred-windows.md), accepted by the controller under D-080 and pending the owner's reading, supersedes in part ADR-002 ("Windows through simplification (W0)"), ADR-009, and ADR-013 where they keep windows in place on rebuilt walls; the research brief §10 drops W1–W5 and describes the rule. `CentredWindows.Place` in `Lod.Core.Simplification` attributes the source windows with `WindowRehosting.Rehost` and gives every target outdoor wall one window shaped by `Window.Centered` (D-026) with the glazed area attributed to it, none when that area is zero; `PlanSimplifier` (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*) and `SingleZoneMerge` (*Single Zone per Floor Type*, *Single Zone Building*) use it. `WindowNotHosted` stays as a guard, and the new error `GlazingExceedsWall` guards a wall whose glazed area is not smaller than its area; neither caps nor moves a window. No component, input, output, icon, or GUID changed; the descriptions of the five components that rebuild walls and of the *Windows* output of *Convert2BEM* state the rule.
- Glazing per wall, façade, orientation, and building and every validation report are unchanged. Six snapshots changed in their `window(…)` entries only: `simplifier-SemanticMerge`, `simplifier-PerimeterCore`, `simplifier-SingleZonePerFloor`, `aggregator-SingleZonePerFloorType`, `aggregator-SingleZoneBuilding`, and `aggregator-StackedFloorZoneMultiplier`, which stacks a *Perimeter Core* floor although the zone multiplier itself rebuilds no wall; `linear-plan-canonical` and `stack-two-storeys` are byte-identical. 142 core, 19 generator, and 187 integration tests pass on `net8.0`, including every merging simplifier and both single-zone aggregators on the canonical plan and on plans rotated and moved by two placements.
- D-079's guards hold by construction for the four current zoning strategies. Façade coverage (D-041) alone does not guarantee that every source window lies on one target wall: a future strategy that cuts a source wall inside a window fails with `WindowNotHosted` (roadmap risk table; ADR-011, S8).
- The S5 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058). After `scripts/verify.ps1` passes on a fresh clone of `v0.5.0`, `main` and the tags `v0.4.2` and `v0.5.0` are pushed (D-080).
- S6 (Convert2IDF) and S7 (precedent study) can start.
```

Before committing, check that no `<date>` is left:

```bash
git grep -n -F -e "<date>" -- docs/decisions/decision-log.md docs/plans/2026-09-30-implementation-roadmap.md
```

Expected: no output.

- [x] **Step 8: Tick this plan and commit the records**

Tick every completed checkbox of this plan and set its status line to `> **Status:** Done (controller, D-080; pending the owner's reading) · …` (D-051). Leave unticked the steps that run after this commit (Steps 9 and 10 below and Task 10), and name them in the commit body. The second `-m` records the smoke test as `docs/development/grasshopper-smoke-test.md` prescribes ("Recording the result"); fill `<tester and method>`, `<date>`, `<version>`, `<sha>`, `<version text>`, and `<items>` with the values written down in Task 8.

```bash
git add AGENTS.md README.md docs/plans/2026-09-30-implementation-roadmap.md docs/decisions/decision-log.md docs/plans/2026-10-01-s5-centred-windows.md
git commit -m "docs(repo): record s5 completion" -m "Smoke test (docs/development/grasshopper-smoke-test.md, S5 checklist) by <tester and method> on <date>: Rhino <version>, .NET Core runtime, build <sha>, Version output '<version text>', all performed items passed. Not performed, pending a person (D-058): <items>."
```

- [ ] **Step 9: Merge (D-004)**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch chore/repo-s5-close-out
git rebase main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git merge --ff-only chore/repo-s5-close-out
git branch -d chore/repo-s5-close-out
```

Expected: `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0.

- [ ] **Step 10: Tag (local)**

```bash
git tag -a v0.5.0 -m "S5 centred windows on rebuilt walls complete"
git describe --tags
```

Expected: `v0.5.0`.

### Task 10: Fresh-clone gate and push (controller, D-080)

**Files:** none

D-080: when S5 is complete and its gate passes, and a fresh clone of the tag passes `scripts/verify.ps1`, the controller pushes `main` and the tags `v0.4.2` and `v0.5.0`; never a force push. This task is the controller's own; it is not delegated.

- [ ] **Step 1: Check the state to push**

```bash
git status --short
git fetch origin
git rev-parse main v0.5.0^{commit}
git merge-base --is-ancestor origin/main main && echo fast-forward
git tag --list "v0.4.2" "v0.5.0"
```

Expected: no output from `git status --short`; the two SHAs are equal (the tag points at the tip of `main`); `fast-forward` (local `main` contains `origin/main`); the two tags. If `origin/main` has commits that local `main` does not, stop and report: nothing is pushed, and no rebase or force push is attempted.

- [ ] **Step 2: Verify a fresh clone of the tag**

```bash
git clone --branch v0.5.0 . ../BEMGen-v0.5.0-clone
powershell -NoProfile -ExecutionPolicy Bypass -File ../BEMGen-v0.5.0-clone/scripts/verify.ps1
git -C ../BEMGen-v0.5.0-clone describe --tags
```

Expected: the clone reports a detached `HEAD` at `v0.5.0`; verify builds the clone with `0 Warning(s)` and `0 Error(s)` and ends with `VERIFY PASSED`, with 142 core, 19 generators, and 187 integration tests passed on net8.0 (the script changes to its own repository root); `describe` prints `v0.5.0`. Then delete the clone (`rm -rf ../BEMGen-v0.5.0-clone` in Git Bash). If verify fails, stop: nothing is pushed.

- [ ] **Step 3: Push (no force)**

```bash
git push origin main
git push origin v0.4.2
git push origin v0.5.0
git ls-remote --tags origin v0.4.2 v0.5.0
git status -sb
```

Expected: each push succeeds without `--force` (`main` as a fast-forward, each tag as `[new tag]`); `ls-remote` lists both tags (with their peeled `^{}` lines); `git status -sb` shows `## main...origin/main` with nothing ahead or behind. A rejected push is not retried with force: stop and report.

## Exit criteria

- ADR-012 exists, is accepted by the controller under D-080 (pending the owner's reading), and ADR-002, ADR-009, and ADR-013 point to it in their status lines; the research brief §10 describes the rule and no longer lists W1–W5, and no window level remains in its configuration space, pipeline, metadata, invariants, or deliverables.
- `CentredWindows.Place` attributes source windows with `WindowRehosting.Rehost` and gives every rebuilt outdoor wall exactly one window from `Window.Centered` with the attributed glazed area, none when it is zero; `WindowNotHosted` and the new `GlazingExceedsWall` are errors, never caps (`CentredWindowsTests`, six tests).
- *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* use it, on the canonical plan and on plans rotated and moved by two placements (`CentredWindowTests`, 24 tests); *No Simplification*, *Stack Floors*, and *Stacked Floor Zone Multiplier* keep their input's windows.
- Glazing per wall, façade, orientation, and building and every validation report unchanged; all 64 rotated simplifier × aggregator cases of S4.2 still validate.
- Snapshots: `linear-plan-canonical` and `stack-two-storeys` byte-identical; six snapshots changed in `window(…)` entries only (`simplifier-SemanticMerge`, `simplifier-PerimeterCore`, `simplifier-SingleZonePerFloor`, `aggregator-StackedFloorZoneMultiplier`, `aggregator-SingleZoneBuilding`, `aggregator-SingleZonePerFloorType`).
- No component, input, output, icon, or GUID changed; five component descriptions and the *Windows* output description state the rule.
- `scripts/verify.ps1` prints `VERIFY PASSED`; tests: 142 core, 19 generators, 187 integration on `net8.0`; 0 warnings.
- The S5 smoke test is recorded in the close-out commit, with the items left for a person named.
- Version 0.5.0, tag `v0.5.0`; AGENTS.md, README, the roadmap Progress line, detailed-plans row, pipeline block, window constraint, and layout, and the decision-log entry D-081 are written; this plan is ticked and marked Done.
- A fresh clone of `v0.5.0` passes `scripts/verify.ps1`, and `main`, `v0.4.2`, and `v0.5.0` are pushed without force (D-080).

## Notes for the reviewer

1. **Source.** Every code block was taken from a verified reference implementation built on `main` at `cdd021a` (D-079, D-080), six commits in the order of Tasks 1–6. Its last commit, which changed every document, is split here: the architecture and research documents into Task 6, the smoke-test checklist into Task 7, the roadmap's stage description into the plan commit, and the roadmap's pipeline block, window constraint, and layout into the close-out (Task 9). Every task was then replayed on a clone of `cdd021a` from this plan's file contents and replacements: the red errors of Task 2 (with line and column numbers), the failing tests and messages of Tasks 3 and 4 (before and after the implementation), the six received snapshots (byte-identical to the expected contents), the counts after every task, a 0-warning build after every task, the close-out edits, and `VERIFY PASSED` on a fresh clone of the replayed `v0.5.0` are observed results; the replayed end state equals the reference apart from line endings and the version.
2. **Slices and branches.** The roadmap names no slices for S5; this plan uses four slices and a close-out, named after D-004: `docs/decisions-adr-012`, `feature/windows-centred-windows`, `docs/grasshopper-centred-windows`, `docs/windows-centred-windows`, and `chore/repo-s5-close-out`. Merges rebase onto local `main`. Unlike S4.2, this run ends with a push (D-080, Task 10), only after the fresh-clone gate; `v0.4.2`, tagged locally in S4.2, is pushed with it.
3. **ADR-012 is accepted by the controller (D-080), not by the owner.** D-079 gates S5 on ADR-012; D-080 lets the controller accept it, provisionally. Task 1, Step 7 records the check; the owner's reading stays open, as for ADR-013 (D-075).
4. **The zone-multiplier snapshot changes.** `aggregator-StackedFloorZoneMultiplier.txt` was expected to stay byte-identical, since the zone multiplier rebuilds no wall. It changes in Task 3 because `MultiplierSnapshot` stacks a *Perimeter Core* floor, whose walls the simplifier rebuilt; the multiplier itself keeps its floors' windows (`AggregatorsThatDoNotRebuildWallsKeepTheFloorWindows`). Nine lines change, in window entries only.
5. **"By construction" holds for the current strategies only.** D-079 and ADR-012 say that every source window lies on exactly one target wall because the target façades cover the source façades (D-041). Coverage alone does not imply it: a strategy whose target walls end inside a source window covers the source wall and still cuts the window. No current strategy does this on the linear plan: no test, including the 64 rotated cases of S4.2 and the 24 cases of `CentredWindowTests`, and no combination of the smoke test reports `WindowNotHosted`. A future strategy that splits a source wall inside a window fails with `WindowNotHosted` instead of moving the window; the roadmap risk row says so, D-081 records it, and ADR-011 (S8) decides how such windows are treated.
6. **`GlazingExceedsWall`.** The only new diagnostic code; appended to `DiagnosticCodes`, an error whose subject is the target wall. It is checked after the attribution, so `WindowNotHosted` takes precedence, and every offending wall is reported. It compares the glazed area with the wall area directly (`glazing >= wall.Area`), with no tolerance: D-079 requires the glazed area to be smaller, and with WWR < 1 on every source wall it is smaller by a finite margin. It can be reached only with source walls that overlap along a façade line, which no valid plan has; `GlazingNotSmallerThanTheTargetWallIsAnError` constructs that case.
7. **Spelling.** The new class and the documents use "centred" (D-079, ADR-012); `Window.Centered`, the S2 generator's API, keeps its US spelling, since renaming it is unrelated to this stage. The roadmap's window constraint therefore says "one centered window per outdoor wall" for the generator and "one centred window" for rebuilt walls in the same sentence.
8. **Tests changed, not weakened.** `PerimeterSouthKeepsTheSouthFacadeWindowsInPlace` asserted the in-place rule that D-079 replaces; its successor asserts the single window's area (the same 19.2 m²), centring, and proportions. The two aggregator tests replace the source window count by "exactly one window per wall" and keep their glazing-total and validation assertions. The sub-micrometre failures in the red phases of Tasks 3 and 4 are windows kept in place on rebuilt rotated walls (grid rounding of 1e-7 to 3e-7 m), which the 9-decimal centring check detects; no tolerance was added or widened.
9. **Documents.** `pipeline.md`'s heading becomes "Grasshopper components through S5"; the two links that still pointed at `#grasshopper-components-through-s41` (broken since S4.2 renamed that heading) now point at the new anchor. The repository spec (`docs/LOD_grasshopper_plugin_repository_spec.md`) is not edited: it still describes a window-transformation module (§12) and milestone, and is superseded there by D-079, ADR-012, and the roadmap. ADR-002, ADR-009, and ADR-013 get status lines only; their bodies are accepted history. `docs/research/program-presets.md` keeps its status line "Current as of S4.1" with D-079 added to its decisions. The S3 and S4.2 smoke-test checklists keep their in-place window expectations; the S5 checklist's preamble says it replaces them. In the research brief, the note on questions 3 and 4 sits between items 4 and 5 of the numbered list, so the list renders as two lists numbered 1–4 and 5–8.
10. **Not changed, for the owner.** GLOBAL.md scientific rule 1 ("the glazing quantities required by the chosen window level") and the AGENTS.md testing expectation ("window area conserved at the level the W-level requires") still speak of window levels. They are project rules outside this stage's scope; with D-079 the required glazing quantities are the glazed area per wall, orientation, and building. README's opening sentence still lists window representation among what the study varies.
11. **Grasshopper commit type.** Task 5 changes only description strings, so its commit is `docs(grasshopper)`; no behaviour, input, or output changes.
12. **Smoke-test values.** The expected values of Task 8 were observed in one scripted headless Rhino 8.25 session (D-056) on the reference's last commit: registration, the 16 canonical and 16 rotated combinations (states, *Validate* Passed, *Windows* trees and bounding boxes), and the window Breps of each simplifier on one storey. *Inspect* texts, *Validate* line values, and the viewport were not observed there.
13. **`check_plans.py` false positives.** The Global Constraints line that states the no-attribution rule is flagged as a possible attribution; it states the rule.
