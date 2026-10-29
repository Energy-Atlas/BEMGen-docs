# ADR-026: Multiplied rooms

Status: Accepted (by the controller under D-098; provisional pending the owner's reading); the owner's decision O5 of 2026-10-25 is cited here, not made here

Date: 2026-10-25

Decisions: D-032, D-046 (which supersedes D-040), D-069, D-072, D-075, D-098, D-123, D-161, D-162; S8 of [ADR-025](ADR-025-doe-reference-geometry-generators.md); the owner's O5 (design note §1); new: one decision-log entry for stage P5a, added by the controller. Applies [ADR-004](ADR-004-tolerances.md), [ADR-009](ADR-009-vertical-aggregation.md), [ADR-013](ADR-013-vertical-aggregation-methods.md), and [ADR-015](ADR-015-plans-per-storey.md)

Design note: [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md) (stage P5a, decision S8) · Issue: Energy-Atlas/archetype-atlas#13

## Context

[ADR-025](ADR-025-doe-reference-geometry-generators.md) summarises the rule for multiplied rooms as S8 and leaves its rationale and mechanism to this ADR, written in the phase that builds it. Two DOE types need it, the large hotel and the hospital (stage P5b). The owner decided (O5) that zone multipliers inside a floor keep the DOE form: the repeated room is drawn once, with its multiplier.

**What the sources do** (the read-only inspection of 2026-10-25; the records are in [doe-layouts.md](../architecture/doe-layouts.md)).

- The large hotel's typical floor (a floor multiplier of 4) draws two guest-room zones that each stand for 19 rooms, so each stands for 76 rooms over the four floors; its top floor draws a zone of 9. The five other zones of the typical floor are drawn once.
- The hospital draws 17 room zones once each, with multipliers from 4 to 10, in storeys of 9, 11, 13, 13, and 8 zones. The plates have gaps where the copies would be, and the ground storey draws one room apart from the plate, so its drawn zones are two polygons (D-161).
- The sources isolate the multiplied rooms. Every interior surface of a multiplied zone is either self-referencing, a `Surface` boundary that names the surface itself, so that zones exchange no heat through it, or paired with a zone of the same multiplier. On the large hotel's ×4 floor, the ×1 rooms and the ×1 corridor are paired: each is a ×1 zone on a ×4 floor, a multiplier of 4 in the source. The counts of self-referencing surfaces:

| Type | Self-referencing | Multiplied zones |
| --- | --- | --- |
| Hospital | 138 of 218 interzone walls, and every floor and ceiling | 17 rooms, ×4 to ×10 |
| Large hotel | 23 of 75 walls, and 30 of 46 floors and ceilings | rooms ×19 (×76 with the floor) and ×9 |
| Large office | 12 floors and ceilings around the ×10 middle floor | none (the floor entry is ×10) |
| Outpatient | 398 of 448 walls, and every floor and ceiling | none |

**What BEMGen did before stage P5a.**

- Only a floor entry carried a multiplier (`FloorEntry`, D-032), a whole number (D-072). *Stacked Floor Zone Multiplier* gave every zone of a group the group's storey count as `Zone.Multiplier` ([ADR-013](ADR-013-vertical-aggregation-methods.md)); the totals and the converters counted it. The storeys of a multi-storey generator are floor entries too, and a multiplier repeats a storey as for any floor ([ADR-015](ADR-015-plans-per-storey.md)). A planned zone had no multiplier.
- A multiplier multiplies every surface of a storey, so D-046 (which superseded D-040) keeps exposure from being multiplied: a storey of a multiplied type with an exposed floor or ceiling is split off as a ×1 storey.
- Every wall two zones shared became a pair of interzone surfaces. `InterzoneMultiplierMismatch` is a *Convert2IDF* rule only (`IdfGeometry`; [convert2idf.md](../architecture/convert2idf.md#heat-transfer-between-zones)): with the export option for interzone heat transfer on, it writes a pair between zones with different `Zone.Multiplier` adiabatic on both sides, with a warning. The coupling BEMGen adds is between pairs of equal multiplier, such as the outpatient's ×1 zones, where the source has self-referencing surfaces: with the options on, they are paired and exchange heat.
- The DOE layout block (`GridPlanLayout`) returned `NotSupported` for a storey whose footprint is not one polygon (D-161), and a footprint was the union of the zones, so a gap in a plate was a hole or a notch in it.

## Options considered

### How a repeated room is modelled (O5)

1. **Draw every copy.** Excluded by O5: the source draws each repeated room once, and the copies are not in it.
2. **Multiply floors only (before P5a, D-046).** A floor entry repeats a whole storey. It cannot say that one room stands for 19 on a floor, and the large hotel's ×76 needs both.
3. **Keep the DOE form (chosen, O5).** A multiplier on the planned zone. Its combination with the floor entry's by product is this ADR's own choice.

### What the interior surfaces of a multiplied room are

1. **Pair them with the zone beyond, as before.** A ×19 room faces 19 sections of corridor and the ×1 corridor zone has one. The pair has no physical counterpart, which is the objection ADR-013 raised to pairing a zone with a represented but unmodelled storey (its option b).
2. **Write them adiabatic, as `InterzoneMultiplierMismatch` does in *Convert2IDF*.** In this ADR's reading the same thermal result, but a repair with a warning for what the source states on purpose, and the source's own boundary is lost: the self-referencing walls in the answer keys (T2, T4) would have nothing to be compared with.
3. **A boundary of their own, `SelfAdjacent` (chosen).**

### How a plan holds the room's undrawn copies

1. **A footprint of several polygons.** The footprint is the union of the drawn zones, and the gaps are outside it. This was the rule this ADR first stated. A wall toward a gap is then the same geometry as a wall toward the outdoors, so a plan would have to carry which of its edges face the copies as data apart from its geometry.
2. **One plate with a copy space (chosen, P5a's choice, adopted here).** On a storey with a multiplied zone the footprint is the whole plate, one polygon, and the copy space is the footprint less the drawn zones. The geometry itself says which edges face the copies.

### What the merging steps do with a multiplied zone

1. **Merge across multipliers, with a combined multiplier.** The merged zone has the drawn geometry of its sources, and the copies of the zone with the larger multiplier are not drawn. Geometry and exposure would be scaled outside the conserving merge, the objection ADR-013 raised to its single-zone proxy (its option iii).
2. **Merge only zones of equal multiplier, and refuse where a step re-zones the whole plan (chosen).** S8 fixes it for *Semantic Merge* and the refusals; the controller extends the merge rule to *Conditioned Merge*.

## Decision

These refine S8 of ADR-025, the controller's planning decision, accepted under D-098; the owner may overrule any of them. Stage P5a built them, and this ADR is amended to match what it built, so the sections below say what is built.

- **The owner's O5:** the repeated room is drawn once, with its multiplier.
- **S8 (the controller's planning decision):** the multiplier on planned zones, the `SelfAdjacent` boundary, pairing only between equal multipliers, *Semantic Merge*, and the `NotSupported` cases.
- **This ADR's own choices:** the product with the floor entry's multiplier, the drawn-area rule, which surfaces are self-adjacent, and the thermal reading.
- **P5a's choices, adopted here:** one plate with a copy space, in place of the several-polygon footprint this ADR first stated, which the controller adopted under D-098, provisionally; the names and mechanisms under "As built".
- **The controller's:** the rule for *Conditioned Merge*.
- **The session above the controller's:** the walls on nothing (below), decided in its message to the controller on 2026-10-25.

### The multiplier

A planned zone has a zone multiplier, a whole number from 1 (D-072), 1 by default (below 1 is `InvalidParameter`). A plan whose zones all have multiplier 1 is exactly the plan of before, snapshots included. The multiplier says how many identical rooms the drawn zone stands for. The geometry is the drawn zone's only.

The zone multiplier and the floor entry's multiplier combine by product, this ADR's own choice: a ×19 room on a ×4 floor is ×76. `Stack` repeats the storey and each copy keeps ×19; *Stacked Floor Zone Multiplier* gives the representative zone 19 × 4 = 76; both count 76 rooms. `Stack` of the same entries stays the reference of validation (ADR-009).

A zone multiplier multiplies every surface of the zone, exterior ones included, as the EnergyPlus zone multiplier does, which is the source's form. D-046 concerns the storeys that a floor entry repeats and is unchanged; nothing is split off for a multiplied room.

### Totals

Every total counts each zone times its multiplier: floor area, volume, wall, window, and skylight area, ground, roof, and exposed area, and the installed and scheduled loads. ADR-009 already counted `Zone.Multiplier` in the validation totals, and the count now includes the multiplier of a planned zone, a room multiplier times a floor entry's on a *Stacked Floor Zone Multiplier* storey. A zone's self-adjacent surfaces are neither exterior walls nor ground, roof, or exposed area.

### One plate with a copy space

This is P5a's choice, adopted here; it replaces the several-polygon footprint this ADR first stated.

- On a storey that has a zone of multiplier above 1, `GridPlanLayout` puts every grid cell in the footprint, so the footprint is one polygon, the hospital's ground storey included. The drawn zones may still be several polygons on that plate.
- The copy space is the footprint less the drawn zones (`CopySpace.Of`), where the undrawn copies stand. The drawn zones plus the copy space must make the footprint's area; otherwise the error is `CopySpaceAreaMismatch`.
- Every placed storey carries its copy space (`PlacedStorey.CopySpace`, set by `Storeys.PlaceAt`), so a floor or ceiling over it is never outdoors.
- The plan is the DOE drawing, not the building: the drawn area is below the multiplied area. A check that compares areas uses the zone's area times its multiplier on both sides, and the footprint holds the copy space as well. No tolerance changes ([ADR-004](ADR-004-tolerances.md)). T1 compares the drawn outline, the union of the zones, which the answer key records, not the footprint.
- A storey without a multiplied zone is unchanged: cells in no zone lie outside the footprint, and a footprint of several pieces stays `NotSupported`.

### The `SelfAdjacent` boundary

`SelfAdjacent` is a new boundary of a surface (S8). It marks a surface of a zone whose other side is the zone itself, with no adjacent zone. It is written in an IDF as an EnergyPlus `Surface` that names itself. It is neither ground, roof, nor exposed, and it is not an exterior wall.

Which surfaces are self-adjacent is this ADR's own choice, built by P5a, and it comes from the footprint, not from a field of the source:

- A zone edge on the copy space, other than on the plate's outline, is `SelfAdjacent` (an outline edge is `Outdoors`).
- An edge between zones of different multipliers is `SelfAdjacent` on both sides.
- In a building, a floor or ceiling piece between zones of different multipliers is `SelfAdjacent` on both sides, and so is a piece over or under the copy space of the storey beyond. Under *Stacked Floor Zone Multiplier* every piece between storeys is adiabatic, a self-adjacent one too (D-075).
- An F-factor ground floor's edge toward the ground storey's copy space is not exposed perimeter (`ExposedPerimeter.GroundCopySpace`): the copies stand there, and only the edges on the plate's outline are exposed, which EnergyPlus multiplies by the zone multiplier as the copies' own outer edges.

The rule is the sources': on every storey of the hospital and the large hotel, every wall of a zone toward an empty cell is a self-referencing `Surface` in the reference IDF (`selfAdjacentWallLength` in the answer key), and the answer key's figure is compared with the walls the layout makes self-adjacent.

The export options (D-069, [Convert2IDF](../architecture/convert2idf.md#heat-transfer-between-zones)) decide what is written for a surface between two zones. A `SelfAdjacent` surface is between none, so they do not change it. A plan with room multipliers never gives an interzone pair across different multipliers, because the plan builder, the simplifiers, and the stacking make those surfaces self-adjacent. `InterzoneMultiplierMismatch` stays *Convert2IDF*'s guard for such a pair from any other building.

**The IDF form.** A `SelfAdjacent` surface is a `Surface` whose boundary object is the surface itself; each piece of a split floor or ceiling names itself. It takes the interior construction of its kind (a ceiling the reversed interior floor), is not sun or wind exposed, never carries windows, and is not split into convex pieces. The IDF parse-back check counts the surfaces that name themselves against the building's self-adjacent pieces and keeps them out of the partner checks. *Convert2BEM* lists the boundary as `SelfAdjacent` for walls, floors, and ceilings.

### Walls on nothing

A source wall that the source does not mark Outdoors, with nothing beyond it (no zone and no copy), is a true outdoor wall: geometry decides, as in D-162. `SelfAdjacent` is only for walls facing a copy or a zone of another multiplier. Over the fifteen records there is one case: the hospital's `OR_NurseSat_Flr_2_Wall_1_East`, 16.764 m of the plate's east façade, which is a self-referencing `Surface` in the reference IDF, so the source treats it as adiabatic although nothing stands beyond it. BEMGen draws it outdoors, the answer key lists it as a true outdoor wall of `OR_NurseStn_Lobby_Flr_2` (`nonOutdoorExteriorWalls`), and T2 agrees. It is a source boundary artifact like those of D-162, decided by the session above the controller in its message to the controller on 2026-10-25. An energy comparison with the source must name it.

### Pairing only between zones of equal multiplier

Interzone surfaces are paired only between zones of equal multiplier, as in the source (S8). Equal means equal `Zone.Multiplier` of the building, the product, which is what the *Convert2IDF* writer compares; within a storey this is the comparison of the planned multipliers, since the floor entry's factor is common. A shared surface of zones of different multipliers is not paired; it is `SelfAdjacent` on both sides. Surfaces between zones of equal multiplier stay `Interzone` and are written under the export options as before. Validation enforces it: `MultiplierPairing` (floor and building) checks that every interzone surface lies between zones of one multiplier, exactly, and only when a source plan has multiplied rooms, so the reports of every other plan are unchanged.

### The thermal reading of self-referencing surfaces

The source says only that zones exchange no heat through its self-referencing surfaces. This ADR reads them thus: the space beyond a self-referencing surface is at the zone's own conditions, so the zone exchanges no heat with another zone through it, and both faces of its construction see the zone's own conditions. D-162 recorded the source's boundary artifacts and handed the thermal reading to P5a. It applies as follows.

- **Multiplied rooms.** A multiplied room is not coupled to its neighbours of another multiplier, which is the source's own choice, kept by S8. This is why the gaps left by multiplied rooms carry no heat flow.
- **Zones of equal multiplier.** The sources also make surfaces self-referencing between zones of equal multiplier: the outpatient, whose zones are all ×1, has 398 of 448 walls and every floor and ceiling so. S8 does not extend `SelfAdjacent` to them: BEMGen draws them as shared surfaces, `Interzone`, which the export options write adiabatic by default, which in this ADR's reading is the same result. With the options on, BEMGen couples zones that the source keeps apart.
- **The artifacts of D-162.** The stretches where the source exposes a wall to outdoor air although a zone adjoins it, such as the outpatient reception hall's 26.5 m of south wall, remain corrected geometrically, as D-162 recorded. This ADR does not change them.
- **The wall on nothing.** The source treats the hospital's 16.764 m east wall as adiabatic; BEMGen draws it outdoors (above).

An energy comparison against a DOE source must know these four differences.

### *Semantic Merge* and *Conditioned Merge* merge only zones of equal multiplier

*Semantic Merge* groups by space type and program key (S4), and now by multiplier too (S8), also with *Join Pieces*. The merged zone has the multiplier of its sources, so the sum of area times multiplier is conserved, every total with it. Zones of different multipliers are never merged, because the other zone's copies have no drawn geometry to merge with.

*Conditioned Merge* (D-123) merges zones by conditioning class, and S8 does not name it. The reason above holds for it as well, so the controller decided, Provisionally, that it takes the same rule: it merges only zones of equal multiplier, and the merged zone has their multiplier.

### `NotSupported` until a later decision

*Perimeter Core*, *Single Zone per Floor*, and the single-zone aggregators (*Single Zone per Floor Type*, *Single Zone Building*) return `NotSupported` for a plan with room multipliers (for the single-zone aggregators, floors with them) until a later decision. Each re-zones the whole plan or the whole floor, so a room of ×19 would have to be placed in a band, a core, or a single zone with no drawn geometry for its copies. *Conditioned Merge* is not among them: it merges zones of equal multiplier. The steps that do not merge zones carry the multiplier unchanged: *No Simplification* and *Transform Plan* keep multipliers and boundaries, `Stack` keeps each zone's own, and *Stacked Floor Zone Multiplier* multiplies it by the group's storey count.

### As built (stage P5a)

P5a's names and mechanisms, within the decisions above; its decision-log entry records them, and the developer documents describe them ([doe-layouts.md](../architecture/doe-layouts.md), [pipeline.md](../architecture/pipeline.md), [domain-model.md](../architecture/domain-model.md), [validation.md](../architecture/validation.md), [convert2idf.md](../architecture/convert2idf.md)).

- `PlannedZone`, `TargetZone`, and `LayoutZone` carry a `Multiplier`, 1 by default; the plan builder gives it to the `Zone`, `Transform` keeps it, and `Storeys.PlaceAt` multiplies it by the storey count of a *Stacked Floor Zone Multiplier* group.
- `BoundaryCondition.SelfAdjacent`; `CopySpace.Of`; `CopySpaceAreaMismatch`; `PlacedStorey.CopySpace`; `ExposedPerimeter.GroundCopySpace`; the validation check `MultiplierPairing`.
- The surface builder, both merge simplifiers (also with *Join Pieces*), the stacking, and the heat-transfer options carry `SelfAdjacent` surfaces through the splitting of a surface, the merging of zones, and placement.
- *Convert2IDF* writes the surfaces that name themselves, and its parse-back checks and construction roles treat them as above.

### Not in this stage

Drawing the copies; merging zones of different multipliers with weights; fractional multipliers (D-072); multipliers in *Perimeter Core*, *Single Zone per Floor*, and the single-zone aggregators; `SelfAdjacent` for the source's self-referencing surfaces between zones of equal multiplier (the outpatient's stay shared `Interzone` walls); the hospital and large hotel generators (stage P5b).

## Consequences

- A planned zone gains a multiplier and a surface gains a boundary value. Every consumer of boundaries (surfaces, validation, *Convert2BEM*, *Convert2IDF*) handles `SelfAdjacent`. Plans whose zones all have multiplier 1 are unchanged, and so are the existing snapshots and icons.
- The quantities that were pending S8 and P5a in [D-161 and D-162](decision-log.md) are compared since P5a and pass: the hospital's ground storey and totals, the large hotel's 8 and the hospital's 58 T4 quantities (46 before the ground storey), and the T2 true outdoor walls toward multiplied rooms (ADR-025, acceptance tests, phase P5; [doe-layouts.md](../architecture/doe-layouts.md)).
- A building with room multipliers counts each zone times its multiplier in every total; *Semantic Merge* and *Conditioned Merge* never merge zones of different multipliers; the `NotSupported` cases are tested (ADR-025, phase P5).
- A plan with room multipliers cannot yet go through *Perimeter Core*, *Single Zone per Floor*, or the single-zone aggregators.
- The thermal differences of the four kinds above stay documented for every comparison with the source.
- S8 and the details P5a settled are provisional. If the owner overrules one, a new decision-log entry supersedes it and this ADR is updated.
