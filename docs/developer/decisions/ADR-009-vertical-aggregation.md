# ADR-009: Vertical aggregation geometry

Status: Accepted; superseded in part by [ADR-013](ADR-013-vertical-aggregation-methods.md) and by [ADR-012](ADR-012-centred-windows.md) (windows on rebuilt walls)

Date: 2026-10-01

Decisions: D-031, D-032, D-034, D-045, D-046; applies D-021, D-038, D-039, D-041, D-047

## Context

Vertical simplification lives in `IFloorAggregator` (D-018). An aggregator turns floors, listed bottom to top as `FloorEntry(IFloor Floor, int Multiplier)`, into an `IGeneratedBuilding`. S2 implemented `Stack`: it repeats every entry `Multiplier` times, places each storey at its floor-to-floor height, splits floors and ceilings by overlap with the storeys below and above into interzone pieces, lets uncovered parts face outdoors, puts the lowest floors on the ground, and makes the highest ceilings roofs. `Stack` keeps every storey explicit (V0 and V1 in the research brief §11) and is the reference that simplified buildings are compared with.

S4 adds the two other aggregators named in D-018:

- `FloorAreaMultiplier`: representative floors that each stand for several storeys (bottom / middle / top floors, a typical floor, a floor multiplier: V2 to V4 in the research brief §11). The roadmap asks what the representative floors' floors and ceilings face, and how the multiplier reaches `Convert2BEM`.
- `SingleZoneMerged`: the whole building as one thermal zone (D-021). When every storey belongs to one zone, the slabs between storeys no longer separate two zones, and the outdoor walls of each storey must be rebuilt for the single zone. The roadmap asks what happens to the slabs, and whether ClimateStudio can represent the choice.

Merging zones also removes the walls between them (partitions). The S3 plan simplifiers (Z1–Z3) already discard them, as the research brief §8 (Z2) describes for rezoning; D-034 confirms this for every merge and asks this ADR to record that partitions and slabs are treated differently.

Since the plan review, walls carry explicit windows and every zoning level keeps them in place (W0, D-039); target façades must cover every source façade over its full length (D-041); and conditioning comes from the program presets, with a merged zone conditioned if any source contributing floor area is (D-038); loads are aggregated per load type and basis (D-047). The aggregators follow the same rules. The review also settled two questions about representative floors: they sit at their true elevations (D-045), and exposure is never multiplied while floor types with different footprints stay possible (D-046, superseding D-040).

GLOBAL.md constrains the choice: simplified models preserve their invariants (scientific rule 1), every transformation is traceable (rule 2), geometry effects are not confounded with loads or schedules (rule 4), and validation failures block conversion unless an override is recorded (rule 6).

Two things are unknown when this ADR is written: the inputs a ClimateStudio definition expects (D-023, provisional), and how EnergyPlus objects will be written (Convert2IDF, S6, ADR-010). Neither aggregator may depend on them.

## Options considered

### Representative floors and their boundary conditions (FloorAreaMultiplier)

1. **Fixed bottom / middle × (N−2) / top scheme.** Three floors: the bottom floor on the ground, the top ceiling a roof, everything between adiabatic. Ground and roof exposure match the stack; heat exchange between storeys is removed. It cannot express more than three distinct floors.
2. **One typical floor × N with an adiabatic floor and ceiling.** The simplest input. Ground and roof exposure disappear from the model.
3. **One typical floor × N with a ground floor and a roof.** The simplest input that keeps both exposures, but multiplies both by N.
4. **Per-type inputs.** Each floor type carries a floor and a ceiling boundary condition chosen by the user. The most flexible: it adds two inputs per type, admits combinations no physical stack has (a ground floor above a roof), and makes the boundary assumption a free parameter of every experiment.
5. **Configurable floor types with boundary conditions from their order, any multiplier (D-032 with D-033).** A list of floor types, bottom to top, each an `IFloor` with its own multiplier Nᵢ; the order decides which floors touch the ground and which ceilings are roofs. A first or last type with Nᵢ > 1 multiplies the ground or roof exposure; D-033 answered this with a warning and reported, unenforced ground and roof areas.
6. **Configurable floor types with boundary conditions from their order, bottom and top types ×1 (D-032 with D-040).** As option 5, but the first and the last type must stand for exactly one storey, otherwise the aggregation fails with an error; every floor and ceiling between two types is adiabatic. Ground and roof exposure are never multiplied, and ground and roof areas are enforced. A single type × N and a multiplied bottom or top type are rejected, and where neighbouring types have different footprints the uncovered part of a ceiling (a setback roof) or of a floor (an overhang) becomes adiabatic, so such a building fails the enforced roof-area check.
7. **Boundary conditions resolved geometrically; a multiplied type with exposure is rejected.** Floors and ceilings are resolved against the representative storeys below and above: overlap is adiabatic, uncovered parts are exposed. A type with Nᵢ > 1 whose floor or ceiling is exposed is an error. Exposure is correct and never multiplied, but the user must split every such type by hand: always the bottom and the top type, and both types at every setback or overhang.
8. **Boundary conditions resolved geometrically; exposed storeys split off automatically (D-046).** As option 7, but a storey of a multiplied type with an exposed floor or ceiling becomes its own ×1 storey at its true position, and the split is reported. No input is rejected for exposure, and floor types with different footprints are supported.

The multiplier can reach the converter by repeating geometry (what `Stack` does) or as a zone multiplier on every zone of a floor type. Only the second keeps one modelled storey per group of identical storeys.

### Vertical position of the representative storeys (FloorAreaMultiplier)

A. **Stacked directly on each other**, one storey per floor type at its own floor-to-floor height (the S4 draft before D-045). A 1 / 8 / 1 building with 3 m storeys is 9 m tall instead of 30 m; vertical position, which matters for shading, wind exposure, and façade position, is lost.
B. **At the bottom of the storeys it stands for** (storey `first`). A whole storey of the stacked building, but biased to the lower end of the group.
C. **At the exact mid-height of the storeys it stands for.** Centred, but in general at a fractional storey (for storeys 1–8 of 3 m, its floor at 13.5 m), so it coincides with no storey of the stacked building and its zones cannot share IDs with it.
D. **At the whole storey nearest the middle (D-045):** storey `first + ⌊N/2⌋` at its true elevation, with the storeys in between left empty.

### Slabs between storeys in one merged zone (SingleZoneMerged)

a. **Removed.** The zone loses the slabs' thermal storage and their area for convective and radiant exchange. The simplified building then has less thermal mass than the stacked reference, so a geometry simplification also changes thermal mass.
b. **Internal mass of the zone, both faces exposed.** The slab area is kept, and with it thermal storage and exchange area. The slab loses its place in the zone geometry: how solar and radiant gains reach it depends on how the simulation engine treats internal mass, which is not known yet.
c. **Paired floor and ceiling surfaces inside the same zone.** Geometry and both faces are kept, but each pair becomes an interzone surface whose adjacent zone is its own zone. None of the existing boundary conditions (Outdoors, Ground, Adiabatic, Interzone with another zone) describes that, and whether the converters and engines accept such surfaces is not known.

Whether ClimateStudio can represent (b) or (c) cannot be checked until a ClimateStudio reference definition exists (D-023).

### Partitions between merged zones

i. **Discarded**, as the research brief describes for rezoning and as the S3 simplifiers do.
ii. **Converted to internal mass**, like slabs in (b).

## Decision

### FloorAreaMultiplier (D-032, D-045, D-046)

Option 8 for boundary conditions and option D for the vertical position. A configurable list of floor types (D-032) whose exposure is never multiplied (D-046) and whose representative storeys sit at their true elevations (D-045). D-046 supersedes D-040 (option 6), which had superseded D-033 (option 5): multiplying a storey multiplies every surface of it, so exposure (ground, roof, setback roofs, overhanging floors) must never be multiplied, and floor types with different footprints must be allowed, because the study includes buildings whose plan varies with height. Splitting exposed storeys off automatically (option 8) is preferred to rejecting them (option 7) because it gives the same model without making the user split every exposed type by hand. The whole storey nearest the middle (option D) is preferred to the bottom storey (B), which biases the group downwards, and to the exact mid-height (C), which is in general a fractional storey that matches no storey of the stacked building. There is no mode that multiplies exposure and no typical-floor-only mode: a single type × N is modelled as × 1 / × (N − 2) / × 1 for N ≥ 3, and × 2 as × 1 / × 1.

- **Input:** `FloorEntry` list, bottom to top. Each entry is one floor type with multiplier Nᵢ ≥ 1, the number of storeys it stands for. `Storeys.Validate` requires at least one floor, multipliers from 1, and one orientation for all floors.
- **Storeys:** type `i` occupies Nᵢ consecutive storeys of the fully stacked building, from storey `firstᵢ = N₀ + … + Nᵢ₋₁`. Storey `k` sits at the sum of the floor-to-floor heights of the storeys below it, as in `Stack`.
- **Exposure and split (D-046):** a type's floor is exposed if it is the first type or if the footprints of the type below do not cover its zone footprints (the uncovered area is compared with zero by `ToleranceSettings.AreaEquals`); its ceiling is exposed if it is the last type or if the type above does not cover it. If Nᵢ > 1 and the floor is exposed, the type's bottom storey is split off as a ×1 storey; if the ceiling is exposed and more than one storey is left, the type's top storey is split off as a ×1 storey. The remaining storeys form one group. Each split is reported with the info diagnostic `FloorTypeSplit`, which names the type, its multiplier, and the parts (for a single type × 10: `x1 + x8 + x1`). No input is rejected for exposure.
- **Placement (D-045):** a group of n storeys starting at storey `first` is represented by storey `first + ⌊n/2⌋`, the whole storey nearest the group's middle, placed at its true elevation (`Storeys.PlaceAt`). Zone and wall IDs get the prefix `L{k}/`, where `k` is that storey's index in the fully stacked building, so they match the zones of the stacked reference (1 / 8 / 1 with 3 m storeys: `L0/`, `L5/`, `L9/` at 0, 15, and 27 m). The storeys between representative storeys stay empty; the building keeps its true height. Walls keep their windows.
- **Multiplier:** every zone of a group carries `Zone.Multiplier = n`. The validation totals count each zone and its walls n times. `Convert2BEM` outputs the multiplier per zone (`Multipliers`, S2).
- **Floors and ceilings (`Storeys.ResolveRepresentative`):** each zone's floor is split by overlap with the zones of the representative storey below, its ceiling by overlap with the representative storey above (`…/F{n}`, `…/C{n}`). Overlapping pieces are `Adiabatic` (no adjacent zone); uncovered pieces face `Outdoors`; the lowest storey's floors face the ground (`Ground`) and the highest storey's ceilings are roofs (`Outdoors`). There are no interzone surfaces between storeys. Because every storey with an exposed floor or ceiling has multiplier 1, no exposed surface is multiplied.
- No internal mass. Provenance: operation `FloorAreaMultiplier`; parameters `Multipliers` (the input) and `Storeys` (each representative storey with its multiplier, e.g. `L0x1,L5x8,L9x1`); the floors' provenance as inputs.

### SingleZoneMerged (D-021, D-031, D-034, D-038, D-039, D-041)

Option (b) for slabs (D-031) and option (i) for partitions (D-034).

- **Source:** the fully stacked building, `Stack` of the same entries, so a multiplier means explicit repetition.
- **Zone:** one zone, ID `BUILDING`, name "Building". Its space type is the sources' shared space type, or `Mixed` when they differ.
- **Parts:** one `ZonePart` per storey outline, the union of the storey's zone footprints at the storey's elevation and height. A storey whose zones form several disjoint polygons gets one part per polygon.
- **Walls:** rebuilt from each outline (`LayoutSurfaceBuilder` with the outline as the only zone), so every wall faces outdoors; IDs `S{k}/BUILDING/W{n}` with `k` the part index.
- **Façade coverage (D-041):** the rebuilt walls must cover every outdoor wall of the stacked building over its full length (`FacadeAttribution.CoverageGaps`, evaluated before any normalisation). Otherwise the aggregation fails with `FacadeNotCovered` for each partly covered source wall.
- **Windows (D-039):** every window of the stacked building's outdoor walls is kept unchanged (position, sill, width, height) and re-hosted on the rebuilt wall on the same façade line that contains it entirely (`WindowRehosting`). A window that no single rebuilt wall contains is the error `WindowNotHosted`; windows are never moved, resized, or split silently.
- **Partitions:** walls between merged zones are discarded (D-034).
- **Slabs:** for every elevation at which the stacked building has interzone floor pieces, one `InternalMass` with `Zone = BUILDING`; `SlabArea` = the sum of the interzone floor pieces at that elevation (one face); `ExposedFaces = 2`, because both faces lie inside the zone; `Elevation`; and `SourceSurfaces` = the IDs of the floor and ceiling pieces it replaces (D-031).
- **Envelope:** floors on the ground, roofs, and floors or ceilings exposed to outdoors (the uncovered parts at setbacks) are kept with their IDs and assigned to `BUILDING`.
- **Program:** `EquivalentPropertyAggregator` over every stacked zone with area fraction 1 and exterior-wall fraction 1 (ADR-005, ADR-007). The zone is conditioned if any source zone is, and its setpoints are floor-area weighted over the conditioned sources (D-038). The target measures are the parts' total floor area and volume and the rebuilt walls' total area.
- Provenance: operation `SingleZoneMerged`, parameter `Multipliers`, the floors' provenance as inputs.

### Partitions and slabs are treated differently on purpose

Partitions between merged zones are discarded; slabs between storeys become internal mass. The asymmetry is deliberate (D-034): partitions follow the research brief's rezoning rule, slabs follow D-031. Consequence: the thermal mass of partitions is not represented at Z1–Z3 or in `SingleZoneMerged`, while the slab area is kept as internal mass in `SingleZoneMerged`. A comparison between levels of detail in which thermal mass matters must state this.

### Validation

`BuildingValidator` (S3) validates every distinct source floor against its plan, then compares the building with the fully stacked reference built by `Stack` from the same entries. S4 adds no validation code.

- **Enforced** (a failure blocks `Convert2BEM` unless overridden): floor area, volume, exterior wall area, glazing in total and per orientation, installed magnitude and hourly scheduled magnitude per load type (summed over its bases, D-047), all counting zone multipliers; for every aggregator, `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea` (floors facing outdoors, D-046), and `Building.Height` (D-045), all added to `BuildingValidator` in S3; and, for each source floor, façade coverage (D-041).
- **Reported only** (`CheckResult.Enforced = false`): conditioned floor area (D-038). Merging an unconditioned stair into a conditioned zone enlarges it; that is a consequence of the simplification under study.
- Internal mass is not compared; the reference has none.

### Resolved later

- **How internal mass reaches the engines,** as one object with twice the slab area or as one two-sided object: decided for EnergyPlus when Convert2IDF is written (S6, ADR-010), and for ClimateStudio when a reference definition exists (D-023). Until then `Convert2BEM` outputs, per zone, the exposed internal-mass area `SlabArea × ExposedFaces` (provisional, see `docs/architecture/convert2bem.md`).
- **The slab construction:** the model has no constructions yet. `InternalMass` carries area, exposed faces, elevation, and source surfaces; the construction is assigned once ADR-010 decides where constructions come from (S6).
- **How a downstream engine applies `Zone.Multiplier`:** S6 for EnergyPlus, D-023 for ClimateStudio.
- **Window transformations (W1–W5)** are stage S5 (D-039, gated on ADR-012); the roadmap's working assumption places them on floors after the plan simplifier, before aggregation. Both aggregators keep whatever windows their floors carry.

## Consequences

- Both aggregators conserve every quantity the building validation enforces, ground, roof, and exposed floor area and building height included, measured against the stacked reference; for the linear plan this is tested for every plan simplifier (S4 matrix test). What changes is the representation of storeys, slabs, and partitions, which are the geometry effects under study (GLOBAL.md scientific rules 1 and 4).
- `FloorAreaMultiplier` accepts every list of floor types and multipliers that `Storeys.Validate` accepts. The number of modelled storeys depends on the footprints, not only on the number of floor types: a single type × 10 becomes three storeys (`L0x1,L5x8,L9x1`), and every split is reported (`FloorTypeSplit`) and recorded (`Storeys`).
- `FloorAreaMultiplier` with floor types of different footprints (setbacks, overhangs): the uncovered part of a ceiling is a roof and the uncovered part of a floor faces outdoors, both on ×1 storeys at their true elevations, so ground, roof, and exposed floor area match the stack's. The tests cover a setback and an overhang of the linear plan.
- The storeys a representative storey stands for are not modelled, and the space between representative storeys is empty. Heat exchange between storeys is removed (adiabatic overlap), as in every option with representative floors. What the empty gaps mean for solar exposure and shading in a simulation is part of the geometry effect under study; this ADR claims no engine behaviour.
- `SingleZoneMerged` keeps the ground, the roof, exposed floors, the outdoor walls, and every window per storey and per orientation. Its zone has one part per storey outline, and its slabs appear as internal mass. When the stacked building has unconditioned zones, its conditioned floor area grows, and validation reports this.
- The thermal mass of partitions is not represented at Z1–Z3 or in `SingleZoneMerged`.
- The repository spec §13 (vertical representation) is covered by `IGeneratedBuilding.Sources` (the floor entries bottom to top), the ID prefix `L{k}/` (the storey index in the fully stacked building, for `Stack` and `FloorAreaMultiplier`), the provenance parameter `Storeys` (which storey represents how many, `FloorAreaMultiplier`), `Zone.Multiplier`, and `Provenance.Operation` (the transformation mode). Floors have no IDs of their own.
- One new diagnostic code: the info `FloorTypeSplit` (`FloorAreaMultiplier`). `SingleZoneMerged` uses the S3 codes `FacadeNotCovered` and `WindowNotHosted`. The S2 helper `Storeys` gains `PlaceAt` and `ResolveRepresentative`; `Stack` is unchanged.
- Changing the slab rule, the partition rule, the vertical position of representative storeys, or the exposure rule later needs a decision-log entry superseding D-031, D-034, D-045, or D-046 and an update of this ADR.
