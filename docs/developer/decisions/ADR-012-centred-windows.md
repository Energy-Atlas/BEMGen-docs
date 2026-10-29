# ADR-012: Centred windows on rebuilt walls

Status: Accepted (by the controller under D-080; provisional pending the owner's reading); skylights added in DOE geometry stage P0b (D-162)

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

## Skylights (DOE geometry P0b)

Added by the DOE geometry stage P0b ([design note](../plans/2026-10-25-doe-geometry-generators.md), S5, S6, O3); provisional, pending the owner's reading.

**Context.** The DOE reference buildings glaze roofs as well as walls, and the atlas gives a skylight ratio per program (O3). A skylight lies on a roof, a ceiling facing outdoors, but whether a ceiling is a roof is known only once the storeys are stacked (D-068): a plan's and a floor's ceilings are `Unresolved`, and a storey's ceiling may be covered in part by the storey above (a terrace, [ADR-015](ADR-015-plans-per-storey.md)). The question was where a ceiling becomes a roof and gets its skylight.

**Options.** (1) Only the generator places skylights, and every later step re-hosts them like windows: a skylight on a ceiling covered by the storey above would have to be dropped, and one straddling a perimeter/core cut split or refused. (2) Only the floor aggregator places them, from a ratio carried per zone: a merged zone has no single ratio, so a terrace over part of it would take the mixed one. (3) **Both, with the detailed zones' ratio (chosen).** The generator places one skylight on every zone ceiling, as on a roof; every later step that rebuilds ceilings or designates roofs gives each piece the skylight area of the detailed ceilings under it.

**Rule.**

1. **Placement.** A ceiling or roof piece with skylight area \(A_s > 0\) gets exactly one skylight, centred in its largest grid rectangle (`Skylights.LargestGridRectangle`: of the axis-aligned rectangles, in the polygon's frame, whose edges lie on the polygon's own vertex coordinates and which lie inside it, the one of largest area, ties to the first in grid order), the rectangle scaled about its centre by \(k = \sqrt{A_s / A_\text{rect}}\), like `Window.Centered`. The frame is the plan's when every edge is parallel to a plan axis, otherwise that of the polygon's longest outer edge, so a rotated rectilinear roof keeps its grid. A polygon that is not rectilinear in its frame also takes its edges' midpoints into the grid, so a triangle, such as the corner piece of a *Perimeter Core* zone under a terrace, holds the rectangle of half its legs; a sweep of the 18 families with skylights through every simplifier and aggregator, upright and at two placements, found no roof piece without one (`SkylightFamilyTests`). \(A_s \ge A_\text{rect}\), or a piece without a grid rectangle, is the error `SkylightDoesNotFit`; nothing is capped. An area within the area tolerance of zero gives no skylight.
2. **Generator.** Every zone ceiling gets \(A_s = r \times A_\text{ceiling}\), \(r\) the zone preset's skylight ratio (`LayoutMeasures.PlaceSkylightsByRatio`); floors never carry skylights.
3. **Rebuilt ceilings and roofs** (`CentredSkylights.Place`). A piece gets \(A_s = \sum_c r_c A(c \cap \text{piece})\) over the detailed plan's ceilings \(c\), \(r_c\) the ceiling's skylight area over its area. The plan simplifiers (*Semantic Merge*, *Conditioned Merge*, *Perimeter Core*, *Single Zone per Floor*) apply it to every target ceiling: skylight area is conserved per floor, and each target zone has that of the detailed zones under it. `Storeys.Assemble`, where every floor aggregator designates its roofs, applies it to each storey's ceiling pieces facing outdoors against the floor's source plan, and gives every other piece none: a covered ceiling has no skylight, a terrace or the top roof has the ratio of each detailed zone under it × its area. *Stack* and *Stacked Floor Zone Multiplier* keep those pieces, and *Single Zone per Floor Type* and *Single Zone Building* keep them on their merged zones, so every method conserves skylight area per zone as it conserves window area, and the roofs' skylight area does not depend on the simplifier.
4. **Guard.** The target pieces tile the detailed ceilings, so together they receive the detailed skylight area; otherwise the error `SkylightNotHosted` (a guard, like `WindowNotHosted`).
5. **Validation.** `Skylights` compares a floor with its plan and a building with `Stack` of the same entries; `Building.SkylightsOnRoofs` checks that every skylight lies on a roof. Both appear only when skylights exist, so every report without them is unchanged.

**Consequences.** Without skylight ratios nothing changes: every snapshot, report, and IDF is byte-identical. Skylight positions are not conserved, only their areas. The window rule per orientation (S5) conserves glazed area per wall, so per orientation, unchanged by this section.
