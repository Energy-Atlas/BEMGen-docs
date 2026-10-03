# ADR-013: Vertical aggregation methods

Status: Accepted (by the controller under D-075; provisional pending the owner's reading); superseded in part by [ADR-012](ADR-012-centred-windows.md) (windows on rebuilt walls); footprints with holes noted in S8.3; storeys that differ (plans per storey, [ADR-015](ADR-015-plans-per-storey.md)) noted in S8.7

Date: 2026-10-01

Decisions: D-068, D-069, D-070, D-071, D-072, D-074, D-075, D-076; supersedes [ADR-009](ADR-009-vertical-aggregation.md) where it differs; applies D-031, D-034, D-038, D-039, D-041, D-045, D-046, D-047

## Context

[ADR-009](ADR-009-vertical-aggregation.md) (S4) fixed the geometry of the three floor aggregators of Checkpoint 1: `Stack`, `FloorAreaMultiplier`, and `SingleZoneMerged`. The review of S4.1 changed four things about vertical aggregation:

- **Where exposure is decided (D-068).** `FloorAreaMultiplier` resolved the floors and ceilings of its representative storeys against the representative storey below and above (`Storeys.ResolveRepresentative`), and decided which storeys to split off (D-046) by comparing neighbouring floor types. Whether a floor touches the ground, a ceiling is a roof, or a piece is exposed at a setback or overhang is a property of the whole building, not of the storeys a method chooses to model.
- **Which methods exist (D-071).** `FloorAreaMultiplier` is renamed `StackedFloorZoneMultiplier`. `SingleZoneMerged` (the whole building as one zone, D-021) becomes `SingleZoneBuilding`, and a new method `SingleZonePerFloorType` makes one zone per floor entry. In Grasshopper the *Single Zone Merged* component becomes *Single Zone per Floor Type* and keeps its GUID (D-064); *Single Zone Building* is a new component with a new GUID.
- **Heat transfer between zones (D-069).** Whether walls between zones and floors and ceilings between storeys exchange heat becomes a choice of the converter, not of the building model.
- **Moved and rotated plans (D-070, D-074).** *Transform Plan* moves and rotates a plan's geometry before it is simplified and stacked, so storeys can overhang the storey below without being a setback of the same footprint, and plans can be rotated by angles other than multiples of 90°.

Multipliers stay whole numbers (D-072). Validation keeps the rules of ADR-009: every building is compared with the fully stacked reference built by `Stack` from the same floor entries.

## Options considered

### Where floors and ceilings are designated (D-068)

1. **Per method, against the modelled neighbours (ADR-009).** Each method resolves the storeys it models against each other. A method that leaves storeys out (the zone multiplier) resolves against storeys that are not physically adjacent, and needs its own exposure test for the D-046 split.
2. **Once, on the assembled stack.** Every aggregator first assembles every storey of the building (each entry repeated by its multiplier, at its true elevation) and designates every floor and ceiling piece there: the lowest storey's floors face the ground, the uncovered parts of a floor or ceiling face outdoors, and the overlaps with the storey below or above lie between storeys. Each method then takes the designation of the storeys it models from that one resolution.

Option 1 gives the same numbers as option 2 for every building ADR-009 allows, because the representative storey below always has the floor of the storey physically below. Option 2 states the rule once, makes the D-046 split and the D-074 warning read the same designation, and does not depend on which storeys a method models.

### Pieces facing a represented but unmodelled storey (zone multiplier)

a. **Always adiabatic (ADR-009, D-075 default).** The modelled storey exchanges no heat with the storeys it stands for or with the storeys between representative storeys.
b. **Follow *EnableFloorHeatTransfer*.** Pair the piece with the representative zone of the storey it faces. That zone is not the physical neighbour, and it is multiplied differently, so the pairing has no physical counterpart.

### Zones of a single-zone method

i. **One zone for the building (`SingleZoneMerged`, D-021).**
ii. **One zone per floor entry (D-071).** Each entry (one floor type and the number of storeys it stands for) becomes one zone spanning those storeys; neighbouring entries stay separate zones.
iii. **One zone per floor type with area-based quantities multiplied by the number of storeys** (the "single-zone proxy" of the review). It is not a stack of real storeys: geometry, ground, and roof would no longer correspond to the building, and the quantities would be scaled outside the conserving aggregator. Rejected in D-071.

### A storey that the storey below does not carry (D-074)

- **Error.** Rejects every overhang, including the overhangs of plans that differ in length, which S4 accepts and tests.
- **Silent.** The uncovered part faces outdoors and nothing is said.
- **Warning.** The building is produced, the uncovered part faces outdoors as before, and the user is told which storey overhangs by how much.

### Heat transfer between zones (D-069)

- **In the building model.** Each aggregator would turn interzone surfaces into adiabatic ones on request, so the building and its validation would depend on a converter's choice.
- **As an export option.** The building keeps its interzone surfaces; each converter writes them as adiabatic or paired, by one shared rule.

### Multipliers

- **Whole numbers (D-072).** As since S2; the EnergyPlus `Zone` multiplier takes whole numbers only.
- **Fractional.** Rejected in D-072.

## Decision

### One designation on the assembled stack (D-068)

`Storeys.Assemble` stacks every entry `Multiplier` times, bottom to top, at the floor-to-floor heights, with the storey prefix `L{k}/` on zone and surface IDs (`k` the storey index in the fully stacked building, as since S2). It designates every horizontal piece as `Stack` did since S2 (`Storeys.ResolveStacked`): each zone's floor is split by overlap with the zones of the storey below and its ceiling by overlap with the zones of the storey above (`…/F{n}`, `…/C{n}`); overlapping pieces are `Interzone` with the zone on the other side; uncovered pieces face `Outdoors`; the floors of storey 0 face the `Ground`; the ceilings of the highest storey are roofs (`Outdoors`). Plans and floors keep their floors and ceilings `Unresolved` (since S2). Every aggregator starts from this assembly; the four methods differ only in what they do with it.

### Unsupported storeys (D-074)

A storey `k > 0` is unsupported when the part of its floor covered by storey `k − 1` (its floor area minus its floor pieces facing outdoors) differs from its floor area by more than the relative area tolerance (`ToleranceSettings.AreaEquals(floor area, covered area)`, as every area check compares). Every aggregator reports one warning `UnsupportedStorey` per such storey, naming the storey and the uncovered floor area in m², and still produces the building; the uncovered part faces outdoors. Storey 0 stands on the ground and is never unsupported. The overhang of a longer plan on a shorter one is an unsupported storey too. The comparison is relative to the storey's floor area, not with zero, because the floors of rotated plans can leave slivers of the order of 1e-5 m² uncovered where rounding on the distance grid moves a shared façade line by less than the distance tolerance; such a sliver is not an overhang. The D-046 split below keeps comparing the exposed area with zero, so that not even a sliver is multiplied. *(2026-10-03: the pieces are clipped from conformed footprints, [ADR-002](ADR-002-geometry.md), so rotated storeys no longer leave such slivers; the rotated setback of the tests is fully covered and its lowest storey is no longer split off. Both comparisons are unchanged.)*

### The four methods (D-071)

| Method | Zones and IDs | Multiplier | Floors and ceilings | Walls, windows, slabs |
| --- | --- | --- | --- | --- |
| `Stack` (*Stack Floors*) | every storey of the assembly, `L{k}/…` | 1 | as designated on the stack | as in the floors |
| `StackedFloorZoneMultiplier` (*Stacked Floor Zone Multiplier*) | one representative storey per group, `L{k}/…` (D-045) | `Zone.Multiplier = n`, the group's storey count | the representative storeys' pieces from the stack: ground, roof, and exposed pieces kept; every piece between two storeys `Adiabatic` | as in the floors |
| `SingleZonePerFloorType` (*Single Zone per Floor Type*) | one zone `E{i}` per floor entry `i` (from 0, bottom to top), name "Floor type i" | 1 | ground, roof, and exposed pieces kept; pieces between two entries `Interzone` between `E{i}` and `E{i+1}`; slabs within an entry become internal mass | rebuilt per storey outline, windows re-hosted, partitions discarded |
| `SingleZoneBuilding` (*Single Zone Building*) | one zone `BUILDING`, name "Building" | 1 | ground, roof, and exposed pieces kept; every slab between storeys becomes internal mass | rebuilt per storey outline, windows re-hosted, partitions discarded |

**`StackedFloorZoneMultiplier`** is `FloorAreaMultiplier` renamed; it models what it modelled before. Floor type `i` stands for its Nᵢ storeys of the assembly. A storey of a multiplied type is split off as its own × 1 storey (D-046, info `FloorTypeSplit`) when the type's bottom storey's floor, or its top storey's ceiling, has pieces on the stack that are not between storeys (ground, roof, or exposed) with an area that is not zero within `AreaEquals` (as in ADR-009); the remaining storeys form one group. A group of n storeys from storey `first` is represented by storey `first + ⌊n/2⌋` at its true elevation (D-045), with the IDs of that storey of the assembly. Its floor and ceiling pieces are the stacked pieces of that storey, with every piece between two storeys turned `Adiabatic` (option a), whether the storey on the other side is modelled or not, and whatever *EnableFloorHeatTransfer* says (D-075). Ground, roof, and exposed pieces are kept and always lie on × 1 storeys, so exposure is never multiplied. Provenance: operation `StackedFloorZoneMultiplier`, parameters `Multipliers` and `Storeys` (e.g. `L0x1,L5x8,L9x1`). The storeys that are represented but not modelled are given by `StackedFloorZoneMultiplier.UnmodelledStoreys` (the assembly's storeys outside the representative ones) for the viewport preview, which draws them transparent grey (D-071, D-075).

**`SingleZonePerFloorType`** and **`SingleZoneBuilding`** share one merge (`SingleZoneMerge`) over groups of consecutive storeys of the assembly: one group per floor entry, or one group of every storey. For each group:

- **Zone:** one zone with one `ZonePart` per storey outline (the union of the storey's zone footprints; a storey whose zones form several polygons gets one part per polygon). The union treats the footprints as tiles (`PolygonOps.UnionTiles`): vertices in one cell of the distance grid are unified and every vertex lying on another footprint's edge (a T-junction) is inserted into that edge before clipping, as `LayoutSurfaceBuilder` splits walls, so shared edges cancel exactly, and the result keeps the footprints' own vertices ([ADR-002](ADR-002-geometry.md), S8.2). A plain union of rotated footprints leaves slits or splits the outline where rounding on the clipping grid moves a T-junction off its edge. Its space type is the sources' shared space type, or `Mixed`. Its source zones are the stacked zones of the group, storey by storey.
- **Walls:** rebuilt from each outline (`LayoutSurfaceBuilder` with the outline as the only zone), all `Outdoors`, IDs `S{p}/<zone>/W{n}` with `p` the part index within the zone. The rebuilt walls must cover every outdoor wall of the assembly over its full length (D-041, `FacadeNotCovered`); every window is re-hosted unchanged on the rebuilt wall that contains it (D-039, `WindowNotHosted`); walls between merged zones are discarded (D-034).
- **Slabs:** for every elevation at which the group has interzone floor pieces between two of its own storeys, one `InternalMass` with the slab area (one face), `ExposedFaces = 2`, the elevation, and the replaced floor and ceiling pieces as source surfaces (D-031).
- **Floors and ceilings:** every other piece of the group's storeys keeps its stacked ID, polygon, elevation, and boundary and is assigned to the group's zone; a piece between two groups stays `Interzone`, with the other group's zone as its adjacent zone, so the pieces between `E{i}` and `E{i+1}` come in matching pairs.
- **Program:** `EquivalentPropertyAggregator` over the group's stacked zones with area fraction 1 and exterior-wall fraction 1; the target measures are the parts' floor area and volume and the rebuilt walls' area. Every invariant is conserved, and the zone is conditioned if any source is (D-038).

`SingleZoneBuilding` is exactly the former `SingleZoneMerged` (provenance operation `SingleZoneBuilding`). `SingleZonePerFloorType` with a single entry gives the same geometry as `SingleZoneBuilding` with zone `E0` instead of `BUILDING`. Both record the parameter `Multipliers`. The viewport preview draws each zone as one merged volume instead of one solid per part; the data and the *Convert2BEM* outputs keep one part per storey outline.

### Footprints with holes (S8.3)

The four methods need no rule of their own for a footprint with holes (a court, [ADR-002](ADR-002-geometry.md)). The court lies outside every zone footprint, so the designation on the stack gives it no floor or ceiling piece: the ground and roof areas are the footprint's area without the court, and a storey with the same court as the storey below is fully supported. The storey outlines of the single-zone methods are unions of tiles that keep the hole, one part per outline with an inner ring per court, and their rebuilt walls include the court walls of every storey, which must cover the source court façades (D-041) and get one centred window each with the glazed area they cover (D-079). Every combination of a plan simplifier and a floor aggregator validates for the enclosed court of `HDHM-TYP-005`, canonical and at the two rotated placements of the test suite.

### Storeys that differ (S8.7)

A generator may return one plan per storey (D-095, [ADR-015](ADR-015-plans-per-storey.md)); its storeys are floor entries with multiplier 1, bottom to top, and the four methods need no rule of their own. The designation on the stack makes the part of a lower storey's ceiling that the storey above does not cover an outdoor roof piece (a terrace) and the covered part a piece between the storeys: `Interzone` in `Stack`, `Adiabatic` in `StackedFloorZoneMultiplier`, `Interzone` between `E{k}` and `E{k+1}` in `SingleZonePerFloorType`, which makes one zone per storey, and internal mass in `SingleZoneBuilding`. `Building.RoofArea` counts terraces with the top roof, so for storeys that each stand on the storey below it equals the ground area, and no storey is unsupported. A multiplier above 1 repeats its storey as for any floor and is allowed; `StackedFloorZoneMultiplier` then splits every storey with a terrace off as × 1 (D-046). `TerraceTests` (`Lod.Core.Tests`) and the stepped band of `SYN-TYP-012` through every simplifier and aggregator, canonical and at the two rotated placements, confirm this; nothing in this ADR changed for it.

### Heat transfer is a conversion rule (D-069)

`HeatTransferOptions(EnableInternalWallHeatTransfer, EnableFloorHeatTransfer)`, both `false` by default, lives in `Lod.Core` so that *Convert2BEM* (S4.2) and *Convert2IDF* (S6) apply the same rule. `HeatTransferOptions.Exported(surface)` gives the boundary a converter writes: an `Interzone` wall becomes `Adiabatic` unless `EnableInternalWallHeatTransfer`; an `Interzone` floor or ceiling becomes `Adiabatic` unless `EnableFloorHeatTransfer`; every other surface keeps its boundary. The building is not changed, its validation does not depend on the options, and each converter records the values it used.

### Moved and rotated plans (D-070)

`PlanTransform.Apply` rotates a plan about the world origin by an angle about +z (counter-clockwise seen from above, degrees) and then translates it in x and y (metres). Footprint, zone parts, walls, and floors and ceilings move rigidly; windows keep their offsets, sills, and sizes, and zone and surface IDs stay. Wall facing follows the rotated geometry because it is computed from the wall's end points; the plan's orientation (true north) is unchanged. Provenance: operation `TransformPlan`, parameters `RotationDegrees`, `TranslationX`, `TranslationY`, the source plan's provenance as input. Non-finite values are `InvalidParameter`. Whole quarter turns use exact cosines and sines, so an axis-aligned plan stays axis-aligned. Every plan simplifier and floor aggregator works on transformed plans; storeys from differently transformed plans stack, and where a storey overhangs the storey below it is reported as unsupported (D-074).

Two rules make the downstream steps independent of the rotation; neither changes a tolerance:

- **Same façade line.** Two walls lie on the same façade line (`FacadeAttribution.Interval`, used for façade coverage, D-041, and window re-hosting, D-039) when they face the same way within `Angle`, share elevation and height within `Distance`, overlap, and are within `Distance` of each other over their overlap, measured at its two ends. Through S4.1 the end points of the second wall had to lie within `Distance` of the first wall's infinite line, which extrapolates a short wall's direction: a 4 m wall whose end carries 0.4 µm of grid rounding leaves a 24 m wall's line by 2.4 µm at the far end, although the two walls are 0.4 µm apart where they overlap. For axis-aligned plans both rules give the same result.
- **Storey outlines** of the single-zone methods are unions of tiles (above).

### Validation

Unchanged in principle (ADR-009): `BuildingValidator` validates every distinct source floor against its plan and compares the building with the fully stacked reference `Stack` of the same entries, counting zone multipliers. Enforced: floor area, volume, exterior wall area, glazing in total and per orientation, installed and hourly scheduled magnitude per load type, ground, roof, and exposed floor area, building height, and façade coverage per source floor. Reported only: conditioned floor area. Interzone pieces between `E{i}` and `E{i+1}` are neither ground, roof, nor exposed, like the stack's pieces between storeys. Internal mass is not compared.

## Consequences

- Every existing building is numerically unchanged: areas, boundary areas, multipliers, surface IDs, and validation reports. The snapshots of the renamed methods only change their file names (`aggregator-StackedFloorZoneMultiplier.txt`, `aggregator-SingleZoneBuilding.txt`); the report text holds no operation name.
- `Storeys.ResolveRepresentative` is deleted; `Storeys.Assemble` and `AssembledStack` replace the per-method resolution. `SingleZoneMerged` is renamed `SingleZoneBuilding` and keeps the zone ID `BUILDING`.
- One new warning code, `UnsupportedStorey`, appended to `DiagnosticCodes`. The overhang tests of S4 now expect it.
- Plans rotated by any angle and moved anywhere go through every plan simplifier and every floor aggregator and validate; the test suite checks all 16 combinations at four placements, a setback of a rotated plan, and storeys from differently moved plans; overhangs are tested on axis-aligned and moved plans, not on rotated ones.
- Heat exchange between storeys in `StackedFloorZoneMultiplier` stays removed, as in ADR-009. In `SingleZonePerFloorType` it is kept in the model between entries and written by the converters as *EnableFloorHeatTransfer* says; within an entry the slabs are internal mass.
- The thermal mass of partitions is still not represented at Z1–Z3 or in the single-zone methods (D-034); the slabs within a single-zone group are internal mass (D-031).
- Storeys that differ, from a generator that returns one plan per storey, are ordinary floor entries; their terraces are designated by the rule above ([ADR-015](ADR-015-plans-per-storey.md), S8.7).
- Changing the designation rule, the pieces facing unmodelled storeys, the single-zone grouping, the unsupported-storey rule, or the heat-transfer rule needs a decision-log entry and an update of this ADR.
