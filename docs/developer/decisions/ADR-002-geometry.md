# ADR-002: Geometry representation

Status: Accepted; superseded in part by [ADR-012](ADR-012-centred-windows.md) (windows through simplification); placement rule refined by [ADR-011](ADR-011-minimum-wall-and-window-geometry.md) (minimum wall and window); unions of zones refined in S8.2; footprints with holes supported by every step and the boundary coverage of edge matching added in S8.3; perimeter zones keep the footprint vertices since S8.5; floors and ceilings between storeys clipped as conformed polygons since 2026-10-03

Date: 2026-10-01

Decisions: D-009, D-021, D-026, D-039

## Context

The pipeline (D-018) produces plans, floors, and buildings whose zones, surfaces, and windows feed `Convert2BEM` and later `Convert2IDF` (S6). The core libraries cannot use Rhino geometry (GLOBAL.md architecture rules 1, 2, and 4), yet they must compute floor areas, volumes, wall areas, orientations, adjacencies, and source-target overlaps precisely enough for the conservation checks (ADR-004). Residential plans in this study are storeys of constant height with vertical walls. Zones stop at the dwelling unit (D-009), and `SingleZoneMerged` turns the whole building into one zone (D-021). Window representation is an experimental axis of its own (research brief §10, levels W0 to W5), independent of zoning: walls carry explicit windows (D-039), the first plan generator places them from the program preset's window-to-wall ratio (WWR, D-026), and window transformations are a later stage (S5).

## Options considered

### Dimensionality

1. **A full 3D boundary representation in the core.** General, but it needs a geometry kernel: RhinoCommon is not allowed in the core, and a custom 3D kernel is far beyond what the study needs.
2. **2.5D: plan polygons with elevations and heights.** Exact areas and volumes from polygon formulas; covers extruded storeys with vertical walls. Cannot represent sloped roofs, non-vertical walls, or curved surfaces.

### Window representation

1. **Centered windows only, at every LoD** (the former D-022, with the glazing rule of the former D-025): one centered window per exterior wall, sized from the WWR at Z0 and from the inherited façade glazing at simplified levels. One number per wall fixes size and position. Rejected by D-039 because it removes the window-LoD axis: the window representation would be fixed by the rule, and every simplified zoning level would also redistribute the glazing, so window and zoning effects could not be separated.
2. **A glazing quantity per wall (area or WWR) without window geometry.** Enough for area conservation, but it cannot express the window positions that W0 keeps, and converters need window geometry.
3. **Explicit windows:** each window has an offset along its wall, a sill height, a width, and a height, and a wall may carry any number. Supports W0 at every zoning level and leaves W1 to W5 to explicit transformations.

### Window placement rule of the first plan generator

1. **A full-width strip with height WWR × wall height.** Always fits, but its proportions differ from the wall's and it touches both wall ends.
2. **The wall rectangle scaled about its centre by √(glazed area / wall area).** One number fixes size and position, the window keeps the wall's proportions, and it lies strictly inside the wall for any WWR below 1.

### Polygon boolean operations

1. **An own implementation.** High risk in degenerate cases.
2. **RhinoCommon curve booleans.** Not allowed in the core.
3. **Clipper2** (`ClipperD` on `PathsD`, double coordinates rounded to a fixed number of decimals). Mature, managed, `netstandard2.0`, no dependencies.

### Matching the shared edges of adjacent zones

1. **Exact floating-point equality.** Fails for coordinates that differ in the last bits.
2. **Snapping vertices to the distance-tolerance grid.** Shared edges match exactly after snapping, and the grid is the same as the Clipper2 precision.

## Decision

**2.5D model in metres.** Plans live in a building-local XY frame in metres; +Y is plan north. A plan stores its orientation as the clockwise rotation of plan north from true north, in degrees.

**Polygons.** `Polygon2` is an immutable polygon with holes. The outer ring is counter-clockwise, holes are clockwise, and rings are stored open (the first point is not repeated). Construction normalises ring orientation, drops repeated consecutive points, and rejects rings with fewer than three distinct points or zero area, as well as polygons whose holes cover the outer ring. The area is the outer ring's area minus the holes' areas.

**Zones.** A zone is one or more prisms, `ZonePart(Footprint, Elevation, Height)`, each with volume = footprint area × height. Only `SingleZoneMerged` (D-021) creates zones with several parts, one per storey; every other zone has exactly one part. A zone's floor area and volume are the sums over its parts.

**Walls.** Walls are vertical rectangles generated from polygon edges. A wall runs from `Start` to `End` with its zone on the left, has a bottom elevation and a height, and its area is length × height. Its outward azimuth is measured in degrees clockwise from north, in [0°, 360°). The azimuth is computed in the plan frame (plan azimuth) and becomes a true azimuth by adding the plan orientation. Orientation bins are applied to the true azimuth:

| Bin | Azimuth |
| --- | --- |
| North | [315°, 45°) |
| East | [45°, 135°) |
| South | [135°, 225°) |
| West | [225°, 315°) |

**Floors and ceilings** are horizontal polygons at an elevation. Every surface has a boundary condition: outdoors, ground, adiabatic, interzone (naming the adjacent zone), or unresolved (the floors and ceilings of a plan or floor before floors are stacked).

**Windows (D-039).** A window is an explicit rectangle in its wall, given by its `Offset` (the distance along the wall from the wall's start point to the window's near edge), its `SillHeight` above the wall's bottom edge, its `Width`, and its `Height`, all in metres. Offsets and sill heights are not negative; widths and heights are positive. A wall carries any number of windows, ordered by offset, and its glazed area is the sum of their areas. The operations that create or re-host windows keep every window within its wall.

**Placement rule of the first plan generator.** The S2 plan generator places one centered window on each outdoor wall (`Window.Centered`). For glazed area `A_g = WWR × A_w` (D-026) on a wall of length `L`, height `H`, and area `A_w = L × H`, the window is the wall rectangle scaled about its centre by `k = √(A_g / A_w)`: width `k × L`, height `k × H`, offset `(L − k × L) / 2`, and sill height `(H − k × H) / 2`. `A_g = 0` gives no window; `A_g < 0` or `A_g ≥ A_w` is an error. This is that generator's placement rule, not a property of windows; generators derived from the precedent study (S7, S8) may place windows differently.

**Windows through simplification (W0).** Plan simplifiers and `SingleZoneMerged` keep every source window unchanged. Each window of a source outdoor wall is re-hosted on the target outdoor wall on the same façade line that contains it entirely, at the same position along the façade, with the same sill height and size; only its offset is re-expressed from the target wall's start point. A window that no single target wall contains is an error; windows are never moved, resized, or split silently. Window transformations W1 to W5 are stage S5 (ADR-012).

**Boolean operations.** Intersection, union, and difference use Clipper2 2.0.0 (`ClipperD` with a `PolyTreeD`, which keeps the hole hierarchy) at a precision of 6 decimals, which is the 1e-6 m `Distance` grid of ADR-004. Results therefore lie on that grid. The inward offset used by the perimeter/core simplifier is specified with that simplifier in S3, not here.

**Edge matching.** Building the surfaces of a zoned plan snaps every vertex to the `Distance` grid, splits zone edges at other zones' vertices, pairs reversed edges of two zones as interzone walls, and marks edges on the plan boundary as outdoors. Any other edge indicates a gap or an overlap and is an error; geometry is never repaired silently (GLOBAL.md quality rule 6). Consecutive collinear segments with the same boundary merge into one wall. Whether a vertex lies on an edge, to split the edge there or to put a segment on the plan boundary, is measured between the original positions of the vertices against the `Distance` tolerance, not between their grid cells (S8.2): snapping a T-junction and both ends of its edge independently can move it up to √2 grid units off the snapped edge, so on a rotated plan a zone corner exactly on the boundary, such as a stair corner on a façade, was not recognised and the rebuilt surfaces of *Semantic Merge* failed with `UnmatchedEdge`. The plan boundary is every ring of the footprint: the edges of a hole (a court) are outdoor walls whose outward side faces into the court. Every edge of the boundary, outer ring and holes, must also be covered by outdoor zone edges over its full length, within the relative tolerance with which façade coverage is compared (S8.3); otherwise the error is `UnmatchedEdge`. Edge matching alone cannot see a zone outside the footprint whose every edge is shared with another zone, such as a zone filling a court: the court's edges are then interzone walls and no edge is left unmatched.

**Unions of zones (S8.2).** Wherever zones are united into one zone, their footprints are united as tiles (`PolygonOps.UnionTiles`, [ADR-013](ADR-013-vertical-aggregation-methods.md)): the groups of *Semantic Merge* (Z1) as well as the storey outlines of the single-zone floor aggregators. A plain union of footprints that meet at T-junctions, such as the pinwheel dwellings of the point plate (`HDHM-TYP-007`, [ADR-006](ADR-006-plan-generation-mechanism.md)), splits the group or leaves slits once the plan is rotated off the axes, because rounding on the clipping grid moves the T-junction off its edge. A united zone may have holes, where it surrounds zones of another type (the point plate's dwellings around the core). The union keeps the tiles' own vertices: clipping rounds every vertex to the grid, up to 0.7 grid units off its true position, so each vertex of the result is replaced by the tile vertex of its grid cell. United zones therefore lie on their sources' façade lines, and uniting zones that were themselves united, as the single-zone aggregators do with a *Semantic Merge* floor, adds no rounding; without this, a rotated *Semantic Merge* floor could fail *Single Zone per Floor Type* and *Single Zone Building* with `FacadeNotCovered` (S8.2). *Perimeter Core* (Z2) unites the trapezoids of one orientation bin with a plain union, because they meet edge to edge on the bisectors, and then replaces every vertex in the grid cell of a footprint vertex by that vertex, so its zones lie on the footprint's own vertices too; without this, a footprint edge shorter than about 1 m, such as a hub corner beside a narrower arm, could fail the same check on a rotated plan (S8.5, [ADR-008](ADR-008-perimeter-core-corners.md)).

**Floors and ceilings between storeys (2026-10-03).** The floors and ceilings designated on the assembled stack ([ADR-013](ADR-013-vertical-aggregation-methods.md)) are clipped from the zone footprints of each pair of adjacent storeys prepared together as conformed polygons (`PolygonOps.Conform`): vertices in the same grid cell are unified, every vertex lying on another footprint's edge within the `Distance` tolerance (a T-junction) is inserted into that edge, as for the union of tiles, and every result vertex is replaced by the footprint vertex of its grid cell. Within one grid cell the first registered vertex wins, the lower storey's before the upper storey's, so a piece may take the other storey's vertex where both storeys have one in the same cell, and two vertices up to √2 × `Distance` apart (the diagonal of a cell) can merge into one; the union of tiles has done the same since S8.2. Such a merge moves a piece's boundary by at most √2 × 1e-6 m, which changes the area of a 10 m piece by a relative amount of the order of 1e-7, far below the relative area tolerance of [ADR-004](ADR-004-tolerances.md). The same conformed pair, built once per pair of storeys, serves the ceilings of the lower storey and the floors of the upper one, so both sides of a slab are clipped from identical polygons and their pieces have the same vertices and area. Inserted vertices lie on their edges within the tolerance and clipping removes them again where they are collinear; apart from the merges within a cell, every piece vertex is a footprint vertex or an intersection of footprint edges. Without this, a T-junction between rotated storeys (a partition of one storey ending on a wall line of the other, a setback façade over a perimeter zone) rounded off its edge on the clipping grid and left zero-width artefacts in the pieces: spikes, excursions through a repeated vertex, and slivers about 1e-6 m wide, accepted by validation because they lie below the area tolerance and omitted by *Convert2IDF* with `SliverOmitted` (D-090, [ADR-010](ADR-010-convert2idf.md)). Axis-aligned results and every snapshot are unchanged; a sweep of 50 placements of the 18 families through every simplifier and aggregator found the artefacts in 1249 of 14400 buildings before and in none after. No tolerance changed.

**Rhino geometry.** RhinoCommon types (Breps, points, curves) appear only in `Lod.Grasshopper`. The core works in metres; the plugin converts core geometry to Rhino geometry for previews and `Convert2BEM` output, scaled from metres to the active document's model units.

**Footprints with holes (S8.3).** A court is a hole of the footprint, outside the building: its edges are outdoor walls with windows by the generator's rule, it has no zone, and no floor or ceiling covers it, so it adds neither ground nor roof area. Every plan simplifier and floor aggregator supports such footprints ([ADR-008](ADR-008-perimeter-core-corners.md) for *Perimeter Core*, [ADR-013](ADR-013-vertical-aggregation-methods.md) for the floor aggregators). In Grasshopper a polygon with holes is one planar face with an inner loop per hole, and a zone part one closed extrusion of that face. A zone may also have a hole inside a footprint without one: the office work area of `SYN-TYP-017` (S8.4, [ADR-006](ADR-006-plan-generation-mechanism.md)) is a ring around the core; the hole's edges are interzone walls with the zone inside it, and no step needed a change for it. A footprint may have several holes: the court cluster of `SYN-TYP-011` (S8.6) has one per court, and no step needed a change for them either.

**Out of scope:** sloped roofs, non-vertical walls, and curved geometry.

## Consequences

- Areas and volumes are closed-form; validation compares sums of polygon areas.
- Snapping moves a vertex by at most half a grid step (5e-7 m), which changes the area of a 10 m zone by a relative amount of the order of 1e-7; ADR-004 sets the relative area tolerance accordingly.
- Walls and their windows are rectangles in one vertical plane, so converters can build them directly.
- Window and zoning effects stay separable: at W0 every zoning level keeps the Z0 windows where they are, so glazed area per façade position, per orientation, and per building does not change with zoning.
- A zoning that cuts a façade inside a window cannot keep that window at W0 and fails. ADR-011 (S8) and the window levels (S5) decide how such windows are treated (roadmap risk table).
- Very short wall fragments can host very small windows. Minimum wall and window geometry is decided in ADR-011 before S8.
- Sloped roofs or non-vertical walls would require a new geometry ADR.
