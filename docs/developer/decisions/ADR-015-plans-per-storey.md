# ADR-015: Plans per storey

Status: Accepted (by the controller under D-098; provisional pending the owner's reading)

Date: 2026-10-02

Decisions: D-018, D-068, D-070, D-071, D-072, D-074, D-085, D-095, D-098, D-106, D-108, D-109; applies [ADR-006](ADR-006-plan-generation-mechanism.md), [ADR-013](ADR-013-vertical-aggregation-methods.md), and [ADR-002](ADR-002-geometry.md)

## Context

Through S8.6 a plan generator returns one plan, a single storey; a building with several storeys repeats that plan through the multipliers of the floor aggregators, and the only vertical variation a user can make is to stack plans of different generator runs (different lengths, or plans moved by *Transform Plan*). `SYN-TYP-012` (stepped dwelling bands whose lower roofs become terraces, [ADR-006](ADR-006-plan-generation-mechanism.md)) has a plan that changes from storey to storey: storey `k + 1` is storey `k` stepped back by one terrace depth. D-095 lets a plan generator return one plan per storey and asks for this ADR: the interface, how the floor aggregators treat storeys that differ, and how a terrace is designated (the exposed part of a lower storey's roof is an outdoor roof, the covered part an interzone ceiling, D-068).

What already works, investigated before deciding:

- **The floor aggregators take storeys that differ.** `IFloorAggregator.Aggregate` takes a list of `FloorEntry(Floor, Multiplier)`, bottom to top, and the floors of the entries need not be equal: since S4 a narrower plan may stand on a wider one (a setback) and, since S4.2, a plan may overhang or be moved off the storey below ([ADR-013](ADR-013-vertical-aggregation-methods.md)).
- **Terraces are designated on the assembled stack.** `Storeys.Assemble` splits every ceiling by overlap with the zones of the storey above (D-068): the overlap is `Interzone` with the zone above, the rest faces `Outdoors`, which is a roof by `Totals.RoofArea` (a ceiling facing outdoors). A storey whose floor the storey below covers completely is supported, with no `UnsupportedStorey` warning (D-074).
- **Every method keeps that designation.** `Stack` keeps the pieces as they are; `StackedFloorZoneMultiplier` keeps ground, roof, and exposed pieces and turns the pieces between storeys adiabatic; `SingleZonePerFloorType` and `SingleZoneBuilding` keep ground, roof, and exposed pieces, keep the pieces between two of their zones `Interzone`, and turn the pieces between two storeys of one zone into internal mass (D-031). Validation compares the ground, roof, and exposed floor area of every method with `Stack` of the same entries.

A characterisation test (`TerraceTests` in `Lod.Core.Tests`) confirms this for three storeys of a band stepping back by 3 m with every aggregator: each lower storey's ceiling has a 30 m² terrace facing outdoors and its covered part between storeys (interzone, adiabatic, or internal mass by method), the roof area equals the ground area (100 m²), no floor is exposed or unsupported, and the building validates; it passes on the code of S8.6 without a change. So `Lod.Core`'s aggregation and validation need no change: what is missing is a generator that returns the storeys, and a way to carry them through Grasshopper.

## Options considered

### How a generator returns several storeys

1. **Every generator returns a list.** `PlanGenerator.Generate` returns one plan per storey for every family, a list of one for the families with one plan. One interface, but every generator, component, and test of the sixteen single-plan families changes for the sake of one family, and a list where one plan is the rule hides that those plans repeat.
2. **A storey index on the family's parameter record.** The family stays a `PlanGenerator`, and the user or component calls it once per storey. No new type, but the storeys of one building are no longer one call: the storey count, the stepping that relates them, and the check that the top storey keeps its dwellings belong to the set, and a component would need a list of storey indices as input.
3. **A sibling base class for generators of several storeys (chosen).** `MultiStoreyPlanGenerator<TParameters, TPresets>` in `Lod.Core.Plans` returns `Result<IReadOnlyList<IGeneratedPlan>>`, the plans bottom-up, one per storey. The subclass validates its parameters once and lays out every storey (`Layout` returns one `PlanLayout` per storey); the base does for each storey exactly what `PlanGenerator` does for its one plan: preset checks (D-061), surfaces, windows (D-026, ADR-011), and provenance. The two bases share that work in one internal helper, so no rule is duplicated. Each plan is an ordinary `IGeneratedPlan`, so every simplifier, *Transform Plan*, and every aggregator takes it unchanged.
4. **A new pipeline type for a stack of storeys** (`IGeneratedStack`) between generators and aggregators. It would carry the storey structure explicitly, but every simplifier and aggregator would need a second entry point, and it duplicates `FloorEntry`, which already lists storeys bottom-up.

### How Grasshopper carries the storeys

a. **A list output, wired item-wise (chosen).** The generator's *Plan* output is a list, bottom-up. Grasshopper runs a simplifier or *Transform Plan* once per item, so their *Floor* or *Plan* outputs are lists in the same order, and a floor aggregator's *Floors* input, a list, takes them as the storeys bottom-up with *Multipliers* left empty (all 1). No new parameter type, and nothing changes in the simplifier and aggregator components.

b. **A new Goo for a set of storeys.** Explicit, but a new parameter type that every simplifier would have to accept or unpack.

### Multipliers of plans that are storeys

- **Reject a multiplier above 1** for a floor of a multi-storey generator. The aggregators do not know where a floor comes from, so this would need a storey marker on floors, and it would forbid a legitimate building (a band stepping back every second storey).
- **Allow it (chosen).** A multiplier repeats its storey, as for any floor: entries `storey 0 × 2, storey 1 × 1, storey 2 × 2` are a band that steps back above its second and third storeys. The building differs from the generator's (it has more storeys, and its terraces lie higher), so the generator's building is the one with every multiplier 1, which is what the Grasshopper wiring gives by default. Exposure is never multiplied (D-046): with `StackedFloorZoneMultiplier` every storey with a terrace is split off as × 1. `TerraceTests` covers this case with every aggregator.

### Where the preview finds a storey's height (S8.8, D-108)

Through S8.7 the generator component raised each storey's preview by the floor heights below it, but a simplifier's floor of that storey is previewed at height 0, so the plans and the floors of one band were drawn at different heights.

- **Raise the floors in the simplifier components.** A simplifier component does not know which storey a plan is; the information has to travel with the data.
- **A dedicated field on `IGeneratedPlan` and `IFloor`.** Explicit, but a pipeline type change for a value that only the previews use: `GeneratedPlan`, `PlanTransform`, and every simplifier would carry it, and the data must stay at elevation 0.
- **The storey index times the floor height.** `Storey` is already recorded, and every storey has the parameters' floor height, but it would tie the previews to equal floor heights.
- **The base elevation in provenance (chosen).** The storey's plan records its base elevation, which provenance already carries through *Transform Plan* and every simplifier as their one input.

## Decision

### Interface

- `MultiStoreyPlanGenerator<TParameters, TPresets>` (`Lod.Core.Plans`), with the same constructor arguments, `Name`, `Validate`, and `Describe` as `PlanGenerator<TParameters, TPresets>`, and `Layout(TParameters)` returning `IReadOnlyList<PlanLayout>`, one layout per storey, bottom-up, at least one. `Generate(parameters, presets)` checks `FloorHeight`, `OrientationDegrees`, the family's parameters, and every preset slot once, before any storey is laid out, and fails with all of those errors at once; then it builds each storey as `PlanGenerator` builds its plan, and fails if any storey fails.
- Every storey has the same `FloorHeight` and `OrientationDegrees`, the parameters' values. A storey's plan, like every plan, lies at elevation 0; the floor aggregators place storey `k` at the sum of the floor heights below it (D-068).
- **Provenance:** the operation is the generator's `Name`; the parameters are the family's (`Describe`), `FloorHeight`, `OrientationDegrees`, `Presets` as for every plan, non-default limits (ADR-011), `Storey`, the storey index from 0 at the bottom, and `StoreyElevation` (S8.8, D-108), the storey's base elevation in metres, the sum of the floor heights below it (`StoreyProvenance.ElevationKey`).
- **Diagnostics:** errors of the parameters and presets are reported once. A diagnostic of one storey (`WindowOmitted`, or an error of its surfaces) keeps its code, severity, and subject, the surface or zone ID within that storey's plan, and its message starts with `Storey {k}: `, so the remarks of several storeys can be told apart.
- `PlanGenerator` is unchanged in behaviour: its plans, diagnostics, and provenance stay identical.

### Floor aggregators

No aggregator changes; each takes the storeys as floor entries with multiplier 1, bottom to top:

| Method | Storeys that differ |
| --- | --- |
| `Stack` | every storey its own, `L{k}/…`; the covered part of a ceiling is `Interzone` with the zone above, its terrace `Outdoors` |
| `StackedFloorZoneMultiplier` | every entry has multiplier 1, so every storey is its own group and modelled at its elevation; the result equals `Stack` with every piece between storeys `Adiabatic` (D-075); terraces and roofs kept |
| `SingleZonePerFloorType` | one zone `E{k}` per storey (one floor entry each), one part per storey outline, walls rebuilt per outline; the covered part of a slab lies between `E{k}` and `E{k+1}` (`Interzone` pairs), its terrace `Outdoors`; no internal mass |
| `SingleZoneBuilding` | one zone `BUILDING` with one part per storey outline, walls rebuilt per outline; the covered part of every slab is internal mass, its terrace `Outdoors` |

A terrace is the part of storey `k`'s ceiling that storey `k + 1` does not cover: an outdoor roof piece (D-068). Its walls are the façades of storey `k + 1` above it, outdoor walls with the generator's windows (D-026, ADR-011). Validation is unchanged: `Building.RoofArea` sums every ceiling facing outdoors, terraces included, and is compared with `Stack` of the same entries, as are `Building.GroundArea` and `Building.ExposedFloorArea`. For a band whose every storey stands on the storey below, the roof area (terraces and top roof) equals the ground area, and the exposed floor area is zero.

### Grasshopper

- A generator component of several storeys has the same inputs as the other generator components ([ADR-006](ADR-006-plan-generation-mechanism.md): its count first, the defaults of its `Default` record, the preset inputs in record order, *Preview Location* last) and one output *Plan* with list access, the storeys bottom-up. `TypologyGeneratorComponent` gains the list output for such components; no other component changes.
- **Wiring:** *Plan* (list) → a simplifier (item-wise, a list of floors) → a floor aggregator's *Floors*, with *Multipliers* unconnected (all 1). *Transform Plan* in between moves and rotates every storey alike. Grafting the list, or wiring one storey alone, gives buildings of single storeys, which is the user's choice.
- **Preview:** each storey is previewed at its storey's elevation (the sum of the floor heights below it, in model units) plus the *Preview Location*, so the generator's preview shows the stepped band; the plans' data stay at elevation 0. Since S8.8 (D-108) the height comes from the data: `StoreyProvenance.ElevationOf` reads `StoreyElevation` from an object's provenance, following an operation of exactly one input (*Transform Plan*, a plan simplifier) to its input, and is 0 for anything else, a building included. The plan and floor previews (`PlanGoo`, `FloorGoo`) are raised by it, so the generator, *Transform Plan*, and every simplifier draw a storey at the same height, each plus its own *Preview Location*. Plans and floors that are not storeys stay at 0, and buildings, which stack their storeys in their data, are unchanged. Data, Breps, and *Convert2BEM* outputs are unchanged.

## Consequences

- A family whose plan differs per storey is a `MultiStoreyPlanGenerator`; the sixteen families of one plan and their components are unchanged. `SteppedBandGenerator` (`SYN-TYP-012`, S8.7) is the first such generator.
- A building of storeys that differ is a list of floor entries with multiplier 1; every simplifier and floor aggregator works on it without change, and the terrace designation is that of D-068.
- Multipliers above 1 on such storeys are allowed and repeat a storey; they give another building than the generator's, and the Grasshopper wiring gives multiplier 1 unless the user connects multipliers.
- The narrowest storey of a stepped band is its top storey, so *Perimeter Core*'s precondition (D-087) is decided by the top storey; a band too narrow there fails that simplifier on the top storey only (`PlanTooNarrow`).
- The zone IDs of a storey's plan repeat on every storey (`U1` on each); the aggregators prefix them with `L{k}/` (D-068), so they are unique in the building, as for repeated plans.
- Changing the interface, the provenance keys `Storey` and `StoreyElevation`, the diagnostic prefix, or the multiplier rule needs a decision-log entry and an update of this ADR.
