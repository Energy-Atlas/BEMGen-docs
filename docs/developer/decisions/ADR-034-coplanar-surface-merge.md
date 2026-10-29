# ADR-034: Coplanar surface merge in the IDF writer

- **Status:** Accepted (the owner's decision of 2026-10-29, "Fix in BEMGen", D-191); the controller's realisation Provisional, pending the owner's reading
- **Date:** 2026-10-29
- **Context:** D-187, D-189, D-190, [ADR-010](ADR-010-convert2idf.md), [ADR-019](ADR-019-simulation-ready-idf-and-runner.md) (convex outdoor surfaces), [run plan](../plans/2026-10-29-lod-study-run-plan.md) §4 and §8
- **Numbering:** ADR-032 is the DOE prototype suites (D-185) and ADR-033 is reserved for parallel work, so this is ADR-034.

## Context

EnergyPlus's approximate view factors treat two coplanar surfaces of a zone as unable to see each other. A zone that keeps many coplanar pieces
beside a large internal mass then misses the completeness of its view factors and warns `FixViewFactors: View factors not complete` (D-187):

- the single-zone stackers over *No Simplification* and *Semantic Merge* keep every room's floor and ceiling (51 surfaces in one zone of the
  medium office, 23 floor and 24 ceiling pieces);
- the small hotel's top corridor `L3/CorridorFlr4` (D-190) has one T-shaped roof, which the convex split of ADR-019 cut into three rectangles,
  with a 4.8 m² wall-transfer mass; EnergyPlus prints its warning without the reciprocity line that D-189's expected-warning entry bounds.

D-189 accepted the warning within limits. D-187 named the alternative: write fewer pieces. The owner chose it on 2026-10-29: "Fix in BEMGen".

## Decision

1. **Merge before writing.** `IdfSurfaceMerge` runs on the building's surfaces before the writer splits, pairs, or names anything. A zone's floors,
   ceilings, and roofs of one kind, elevation (within the distance tolerance), boundary, and adjacent zone are merged pairwise in building order
   while two of them have a union that is one simple ring without holes and of their summed area (`IdfPolygons.Merge`); pieces that only touch at
   a vertex, overlap, or would enclose a court stay apart. Boundary and adjacent zone decide the construction role (`ConstructionRoles`), and
   with it the construction and the sun and wind exposure, so merged pieces share all of them.
2. **Both sides alike.** An interzone group merges only with its mirror (the adjacent zone's pieces toward this zone, of the other kind, at the
   same elevation): each piece is matched to its equal piece across, and each merged group's partners must merge into one polygon too; otherwise
   neither side merges. Pieces toward different zones never merge.
3. **Walls** of one zone, boundary, adjacent zone, elevation, and height without windows are merged in maximal straight runs, where each starts at
   the end of the previous one; the two sides of an interzone run are the same runs reversed.
4. **Not merged:** surfaces with windows or skylights, self-adjacent surfaces (ADR-026), unresolved surfaces, surfaces with holes, and a union
   with an edge shorter than, or a vertex nearer the line through its neighbours than, the 0.01 m at which EnergyPlus merges vertices that no
   piece had (pieces of rotated plans whose vertices lie a little more than the tolerance off a common line, which the convex split would cut
   into slivers).
5. **Names and records.** A merged surface keeps its first member's ID. The IDF header lists each merge (`Coplanar merge (D-191): …`, then
   `<written name> <- <members>`), provenance gains `MERGED: …`, and the info `SurfacesMerged` reports the count. Files without a merge are
   unchanged byte for byte.
6. **Outdoor surfaces stay convex (ADR-019).** A merged roof that is not convex is still split into convex pieces. The split now takes, of the
   cuts at a reflex vertex, the one that leaves the fewest reflex vertices in its two pieces, then the shortest: a T is cut along its bar's edge
   from one reflex vertex to the other into two pieces, where the shortest cuts gave three. The small hotel's corridor roof is therefore written
   as two convex pieces, not one polygon.

## Consequences

- Areas, volumes, glazing, loads, the infiltration's exterior areas, and the mass ledger (from the building, not the written surfaces) do not
  change; every invariant of the IDF checks holds (`IdfChecks`, the export matrices). An F-factor ground floor of merged pieces takes the union's
  area and exposed perimeter, whose sums equal the pieces'.
- The written model changes where pieces merge: the small hotel's corridor loses EnergyPlus's view-factor correction (annual sensible heating
  −1.18 % in that zone, −0.43 % for the building; cooling −0.97 % and +0.005 %, Buffalo 5A, 90.1-2019), and two convex pieces give exactly the
  results of one polygon there.
- `ExpectedWarnings.MergedZoneViewFactors` and `ToleranceSettings.ViewFactorReciprocity` are removed: a `FixViewFactors` warning fails a run
  again, and one that appears is a geometry question, not an accepted warning.
- Two IDF snapshots change (the canonical plan under *No Simplification* + *Single Zone Building* and *Perimeter Core* + *Single Zone per Floor
  Type*): their floors, ceilings, and roofs merge and the header lists the merges; no other line changes.

## Alternatives considered

- **Keep D-189's accepted warning** and add a bare `FixViewFactors` entry for the corridor: rejected by the owner ("Fix in BEMGen").
- **Merge the roof into one non-convex polygon**, as the owner's words read: it removes the warning in the corridor, but a non-convex roof that
  casts shadows is a severe error in EnergyPlus (ADR-019, design note 2026-10-11 part D.2). The two-piece convex split gives the same results
  there and keeps ADR-019.
- **Merge in the stackers** (D-187): it would change the pipeline's buildings and every converter; the merge is a property of how EnergyPlus
  computes view factors, so it belongs to the IDF writer.
