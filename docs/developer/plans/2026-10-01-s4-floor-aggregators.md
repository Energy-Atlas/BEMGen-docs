# S4 — Floor aggregators Implementation Plan

> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S4](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the vertical levels of detail (`FloorAreaMultiplier` and `SingleZoneMerged`, ruled by ADR-009), prove that every simplifier × aggregator combination of the linear plan validates, expose both aggregators in Grasshopper, document the complete pipeline, and close Checkpoint 1 (D-030).

**Architecture:** Both aggregators implement the S2 interface `IFloorAggregator` in `src/Lod.Core/Buildings` and reuse the S2 helpers `Storeys` and `Stack`; S4 extends `Storeys` with `PlaceAt` and `ResolveRepresentative` and adds the info code `FloorTypeSplit`. `FloorAreaMultiplier` lets each floor type stand for Nᵢ storeys of the full stack: it splits storeys with an exposed floor or ceiling off a multiplied type as × 1 storeys (D-046), places one representative storey per remaining group at its true elevation, the whole storey nearest the group's middle (D-045), carries the group's storey count as the zone multiplier, and resolves floors and ceilings against the representative storeys below and above (overlap adiabatic, uncovered parts exposed). `SingleZoneMerged` stacks all storeys and merges them into one zone: outdoor walls are rebuilt per storey with façade coverage checked and every window kept in place (S3 `FacadeAttribution` and `WindowRehosting`), and inter-storey slabs become internal mass. The S3 `BuildingValidator` checks every result against the fully stacked reference; the Grasshopper components are thin subclasses of the S2 `FloorAggregatorComponent`.

**Tech Stack:** C# 12 (`LangVersion` 12.0); .NET SDK ≥ 8 (`global.json` pins 8.0.100 with `rollForward: latestMajor`); `netstandard2.0` core libraries; Clipper2 2.0.0; RhinoCommon and Grasshopper 8.19.25132.1001 (plugin targets `net7.0`); xUnit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1 (tests target `net8.0`); Windows PowerShell 5.1 for `scripts/verify.ps1`.

## Global Constraints

- **Gate:** ADR-009 is accepted and merged to `main` (Slice A) before any S4 code is written (roadmap S4).
- Rhino 8 (8.19 or later) only (D-003); stages exchange Grasshopper objects, not JSON (D-017).
- `Lod.Core` and `Lod.Generators` have no RhinoCommon or Grasshopper reference; their tests run with plain `dotnet test`.
- Nullable reference types on; warnings are errors; `.editorconfig` rules are enforced in the build; every public member of `Lod.Core` has XML docs (CS1591 is an error).
- Generation is deterministic; outputs have a stable order.
- Numerical tolerances come only from `ToleranceSettings` (ADR-004).
- Windows are explicit and stay in place at every zoning level (W0): the S2 generator places one centered window per outdoor wall from the preset WWR (D-026); simplifiers and `SingleZoneMerged` re-host every window unchanged on the target wall that contains it, otherwise `WindowNotHosted` (D-039). Window transformations W1–W5 are stage S5.
- Façade coverage is enforced: target outdoor walls cover every source outdoor wall over its full length, otherwise `FacadeNotCovered` (D-041).
- Conditioning comes from the presets; a merged zone is conditioned if any source contributing floor area is, and its setpoints are floor-area weighted over the conditioned sources, a prescribed control rule, not a conservation invariant; the change in conditioned floor area is reported, not enforced (D-038).
- Representative storeys sit at their true elevations: a floor type standing for N storeys is represented by storey `first + ⌊N/2⌋` of its storeys, and the building keeps its true height (D-045).
- Floor multipliers never multiply exposure: a storey of a multiplied floor type whose floor or ceiling is not fully covered by the neighbouring type (always the case for the bottom and the top type) is split off as a × 1 storey, reported with the info `FloorTypeSplit`; floor types may have different footprints. Ground area, roof area, exposed floor area, and building height are enforced checks for every aggregator (D-046, superseding D-040).
- Loads are aggregated per load type and basis (D-047); `SingleZoneMerged` uses the S1 `EquivalentPropertyAggregator` unchanged.
- Partitions between merged zones are discarded; only inter-storey slabs in `SingleZoneMerged` become internal mass (D-031, D-034).
- Validation failures block conversion unless an override is explicitly recorded (GLOBAL.md scientific rule 6).
- Nothing in this stage claims how EnergyPlus or ClimateStudio treat internal mass or zone multipliers; that is decided in S6 (ADR-010) and when a ClimateStudio reference definition exists (D-023).
- No simulation inside the pipeline (D-016). No CI (D-005): `scripts/verify.ps1` passes locally before every merge to `main`.
- Commits: `type(scope): summary` in lower case, no agent, model, or tool attribution and no `Co-Authored-By` trailers (D-001, D-002).
- Grasshopper component GUIDs are fixed in code and never change once merged.
- `.gh` example definitions are made and saved by a person in Rhino 8; agents never write or check them.
- S4 changes two earlier code files, both in Task 2: `src/Lod.Core/Buildings/Storeys.cs` (S2) gains `PlaceAt` and `ResolveRepresentative`, while `Place` and `ResolveStacked` behave as before; `src/Lod.Core/Common/DiagnosticCodes.cs` (S1, last changed in S3) gains `FloorTypeSplit`. Apart from these it changes no S0–S3 file except the close-out documents. It adds no validation code: `Building.Height` and `Building.ExposedFloorArea` exist since S3.

## Files

| Path | Change | Responsibility |
| --- | --- | --- |
| `docs/decisions/ADR-009-vertical-aggregation.md` | Create | Vertical aggregation geometry: D-031, D-032, D-034, D-045, D-046 and how the code realises them |
| `src/Lod.Core/Buildings/Storeys.cs` | Modify (S2 file) | `PlaceAt` places a floor as any storey of the building; `ResolveRepresentative` resolves floors and ceilings of representative storeys (overlap adiabatic); `Place` and `ResolveStacked` unchanged in behaviour |
| `src/Lod.Core/Common/DiagnosticCodes.cs` | Modify (S1 file) | Append the info code `FloorTypeSplit` (D-046) |
| `src/Lod.Core/Buildings/FloorAreaMultiplier.cs` | Create | Representative storeys with zone multipliers at their true elevations (D-045); exposed storeys of multiplied types split off as × 1 (D-046) |
| `src/Lod.Core/Buildings/SingleZoneMerged.cs` | Create | Whole building as one zone; walls rebuilt with façade coverage checked and windows kept in place; slabs as internal mass; partitions discarded |
| `tests/Lod.Integration.Tests/AggregatorTests.cs` | Create | Aggregator behaviour, the 4 × 3 validation matrix, two snapshots |
| `tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.txt` | Create | Snapshot: PerimeterCore floor as types 1 / 2 / 1 (storeys `L0/`, `L2/` × 2, `L3/`) |
| `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.txt` | Create | Snapshot: detailed floor × 2 merged into one zone, windows in place |
| `src/Lod.Grasshopper/Components/AggregatorComponents.cs` | Create | *Floor Area Multiplier* and *Single Zone Merged* components |
| `docs/architecture/pipeline.md` | Create | The complete Checkpoint 1 pipeline |
| `docs/development/grasshopper-smoke-test.md` | Modify | Append the S4 checklist |
| `examples/grasshopper/checkpoint-1-pipeline.gh` | Create (person, Rhino 8) | Every simplifier wired into every aggregator, validation, and conversion |
| `Directory.Build.props` | Modify | Version 0.4.0 |
| `AGENTS.md` | Modify | "Project state" at Checkpoint 1 |
| `README.md` | Modify | "Status" at Checkpoint 1 |
| `docs/plans/2026-09-30-implementation-roadmap.md` | Modify | Progress line: S4 complete, Checkpoint 1 reached |
| `docs/decisions/decision-log.md` | Modify | D-044 "Checkpoint 1 reached" (date and name filled at execution) |

Test counts on `net8.0` at the start of S4: 104 core, 17 generators, 38 integration. At the end: 104 core, 17 generators, 63 integration (25 new in `AggregatorTests`: 6 facts, 3 + 2 + 12 theory cases, 2 snapshots).

---

## Slice A — `docs/decisions-vertical-aggregation`

### Task 1: ADR-009 Vertical aggregation geometry

**Files:**
- Create: `docs/decisions/ADR-009-vertical-aggregation.md`

**Interfaces:**
- Consumes: decisions D-018, D-021, D-031, D-032, D-033, D-034, D-038, D-039, D-040, D-041, D-045, D-046, D-047; S2 types `IFloorAggregator`, `FloorEntry`, `Stack`, `Storeys`, `Zone.Multiplier`, `InternalMass`; S3 types `BuildingValidator`, `CheckResult.Enforced`, `FacadeAttribution.CoverageGaps`, `WindowRehosting`.
- Produces: the accepted rules that Tasks 2–4 implement (names `FloorAreaMultiplier`, `SingleZoneMerged`, `SingleZoneMerged.BuildingZone = "BUILDING"`; helpers `Storeys.PlaceAt` and `Storeys.ResolveRepresentative`; the info `FloorTypeSplit` and the provenance parameter `Storeys`; errors `FacadeNotCovered`, `WindowNotHosted`).

- [x] **Step 1: Create the branch**

```bash
git switch -c docs/decisions-vertical-aggregation main
```

- [x] **Step 2: Write `docs/decisions/ADR-009-vertical-aggregation.md` with exactly this content**

````markdown
# ADR-009: Vertical aggregation geometry

Status: Accepted

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
````

- [x] **Step 3: Check that every cited decision exists**

```bash
git grep -n -E "^### D-0(18|21|31|32|33|34|38|39|40|41|45|46|47) " docs/decisions/decision-log.md
```

Expected: thirteen lines, one for each of D-018, D-021, D-031, D-032, D-033, D-034, D-038, D-039, D-040, D-041, D-045, D-046, and D-047; the D-033 entry is marked `Superseded by D-040` and the D-040 entry `Superseded by D-046`.

- [x] **Step 4: Commit**

```bash
git add docs/decisions/ADR-009-vertical-aggregation.md
git commit -m "docs(decisions): add adr-009 vertical aggregation geometry"
```

- [ ] **Step 5: Gate — acceptance by the decision owner**

The decision owner (Cheng Xuan Li) reads ADR-009. If changes are requested, make them on this branch as further commits and repeat this step. Slice B starts only after this branch is merged.

- [x] **Step 6: Merge (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only docs/decisions-vertical-aggregation
git push origin main
git branch -d docs/decisions-vertical-aggregation
```

Expected: verify ends with `VERIFY PASSED`; its test lines show 104 core, 17 generators, and 38 integration tests passed on net8.0 (S3 state; this slice changes no code).

---

## Slice B — `feature/aggregators`

Roadmap slice 2: both aggregators and the Checkpoint 1 matrix test, which needs both and shares `AggregatorTests.cs` with their tests.

### Task 2: `FloorAreaMultiplier`

**Files:**
- Modify: `src/Lod.Core/Buildings/Storeys.cs` (S2 file): add `PlaceAt` and `ResolveRepresentative`
- Modify: `src/Lod.Core/Common/DiagnosticCodes.cs` (S1 file, last changed in S3): append `FloorTypeSplit`
- Create: `src/Lod.Core/Buildings/FloorAreaMultiplier.cs`
- Test: `tests/Lod.Integration.Tests/AggregatorTests.cs` (created here)

**Interfaces:**
- Consumes (S2): `Storeys.Validate(IReadOnlyList<FloorEntry> floors, ToleranceSettings tolerances) : IReadOnlyList<Diagnostic>`; `Storeys.Place(IEnumerable<(IFloor Floor, int ZoneMultiplier)> storeys) : IReadOnlyList<PlacedStorey>`; `Storeys.ResolveStacked(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops) : IReadOnlyList<HorizontalSurface>`; `PlacedStorey(int Index, double Elevation, double Height, IReadOnlyList<Zone> Zones, IReadOnlyList<WallSurface> Walls)`; `Zone.Relocate(ZoneId id, double dz, int multiplier)`; `WallSurface.Relocate(Func<ZoneId, ZoneId> rename, string idPrefix, double dz)`; `HorizontalSurface(SurfaceId id, ZoneId zone, HorizontalKind kind, Polygon2 polygon, double elevation, BoundaryCondition boundary, ZoneId? adjacentZone)`; `PolygonOps(ToleranceSettings)` with `Intersect(Polygon2 a, Polygon2 b)` and `Difference(Polygon2 subject, IEnumerable<Polygon2> clips)`; `GeneratedBuilding(double orientationDegrees, IEnumerable<Zone> zones, IEnumerable<Surface> surfaces, IEnumerable<InternalMass> internalMasses, IEnumerable<FloorEntry> sources, Provenance provenance)`; `Provenance.Of(string operation, IEnumerable<KeyValuePair<string, string>> parameters, params Provenance[] inputs)`. (S1): `Result.Success<T>(T value, IEnumerable<Diagnostic>? diagnostics = null)`, `Result.Failure<T>`, `Diagnostic.Info`, `ToleranceSettings.AreaEquals`. Test support (S2): `Pipeline.DetailedFloor(LinearPlanParameters? parameters = null)`, `Pipeline.Canonical`, `Pipeline.Tolerances`. Validation (S3): `BuildingValidator(ToleranceSettings).Validate(IGeneratedBuilding) : ValidationReport`, `ValidationReport.Passed`, `ValidationReport.Checks`, `ValidationReport.Describe()`, `CheckResult(string Check, bool Passed, string Detail, bool Enforced = true)`, `Totals.Of(IEnumerable<Zone> zones, IReadOnlyList<Surface> surfaces, double orientationDegrees).Height`.
- Produces:
  - `Storeys.PlaceAt(IFloor floor, int index, double elevation, int zoneMultiplier) : PlacedStorey`, which places a floor as storey `index` of the building with the ID prefix `L{index}/`; `Storeys.Place` now delegates to it.
  - `Storeys.ResolveRepresentative(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops) : IReadOnlyList<HorizontalSurface>`: overlap with the representative storey below or above is `Adiabatic`, uncovered parts face `Outdoors`, the lowest floors `Ground`, and the highest ceilings are roofs (D-046). `ResolveStacked` keeps its behaviour (overlap `Interzone` with the adjacent zone).
  - `DiagnosticCodes.FloorTypeSplit` (info, D-046).
  - `public sealed class FloorAreaMultiplier : IFloorAggregator` with `public FloorAreaMultiplier(ToleranceSettings tolerances)` and `public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors)`: representative storeys at their true elevations (D-045); exposed storeys of multiplied types split off as × 1 storeys, with one `FloorTypeSplit` info per split type (D-046); provenance parameters `Multipliers` and `Storeys`.

- [x] **Step 1: Create the branch**

```bash
git switch -c feature/aggregators main
```

- [x] **Step 2: Write the failing tests — create `tests/Lod.Integration.Tests/AggregatorTests.cs`**

The canonical detailed floor (`Pipeline.DetailedFloor()`) is 24 m × 18 m (432 m²) with six zones (`ST`, `CO`, `US1`, `US2`, `UN1`, `UN2`) and 3 m storeys. With floor types 1 / 8 / 1 the representative storeys are storeys 0, 5 (the whole storey nearest the middle of storeys 1–8, D-045), and 9, at 0, 15, and 27 m, and the building is 30 m tall; the ground floors of `L0/` and the roofs of `L9/` are the only 12 non-adiabatic horizontal surfaces, and every building check passes against the stack of 10 storeys. The multipliers {5}, {2, 1}, and {1, 8, 2} each multiply a bottom or top type: its exposed storeys are split off as × 1 storeys (D-046), reported with the info `FloorTypeSplit`, and recorded in the provenance parameter `Storeys`, and every building check passes. The last theory varies the footprint. The narrow floor is the canonical plan with Length 14 m (the stair and one unit per row, 252 m²), which leaves 180 m² of the wide floor uncovered. A setback (wide × 1, wide × 4, narrow × 3) and an overhang (narrow × 2, wide × 3) must validate, keep every non-adiabatic horizontal surface on a × 1 storey, and expose exactly those 180 m² below the roof (the setback roof at 15 m, the overhanging floor at 6 m).

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Validation;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class AggregatorTests
{
    [Fact]
    public void FloorAreaMultiplierCarriesMultipliersAndOrderedBoundaries()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
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

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;

        // Storeys 1-8 are represented by storey 5, the whole storey nearest their middle (D-045); the top storey stays storey 9.
        Assert.Equal(new[] { "L0/", "L5/", "L9/" }, building.Zones.Select(z => z.Id.Value.Substring(0, 3)).Distinct());
        Assert.Equal(new[] { 0.0, 15.0, 27.0 }, building.Zones.Select(z => z.Parts[0].Elevation).Distinct());
        Assert.Equal(30.0, Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height, 9);
        Assert.Equal("L0x1,L5x8,L9x1", building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
    }

    [Theory]
    [InlineData(new[] { 5 }, "L0x1,L2x3,L4x1")]
    [InlineData(new[] { 2, 1 }, "L0x1,L1x1,L2x1")]
    [InlineData(new[] { 1, 8, 2 }, "L0x1,L5x8,L9x1,L10x1")]
    public void ExposedStoreysOfMultipliedTypesAreSplitOff(int[] multipliers, string storeys)
    {
        IFloor floor = Pipeline.DetailedFloor();

        Result<IGeneratedBuilding> result = new FloorAreaMultiplier(Pipeline.Tolerances).Aggregate(multipliers.Select(n => new FloorEntry(floor, n)).ToArray());
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(result.Value);

        Assert.Equal(storeys, result.Value.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.FloorTypeSplit && d.Severity == DiagnosticSeverity.Info);
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }

    [Theory]
    [InlineData("setback", "wide x1, wide x4, narrow x3", "L0x1,L2x3,L4x1,L6x2,L7x1")]
    [InlineData("overhang", "narrow x2, wide x3", "L0x1,L1x1,L2x1,L3x1,L4x1")]
    public void VaryingFootprintsKeepExposedAreasWithoutMultiplyingThem(string name, string types, string storeys)
    {
        // Wide: 24 m x 18 m, two units per row. Narrow: 14 m x 18 m from the same west end, one unit per row. Either way 180 m² is exposed.
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });
        FloorEntry[] entries = types.Split(',')
            .Select(t => t.Trim().Split(new[] { " x" }, StringSplitOptions.None))
            .Select(t => new FloorEntry(t[0] == "wide" ? wide : narrow, int.Parse(t[1], System.Globalization.CultureInfo.InvariantCulture)))
            .ToArray();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances).Aggregate(entries).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.Equal(storeys, building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.All(report.Checks, c => Assert.True(c.Passed, $"{name}: {c.Check}"));
        Dictionary<ZoneId, int> multiplier = building.Zones.ToDictionary(z => z.Id, z => z.Multiplier);
        HorizontalSurface[] exposed = building.Surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary != BoundaryCondition.Adiabatic).ToArray();
        Assert.All(exposed, h => Assert.Equal(1, multiplier[h.Zone]));
        double roof = Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height;
        Assert.Equal(180.0, exposed.Where(h => h.Boundary == BoundaryCondition.Outdoors && h.Elevation < roof - 1.0).Sum(h => h.Area), 6);
    }

    [Fact]
    public void BottomMiddleTopMultiplierMatchesTheStackExactly()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }
}
```

- [x] **Step 3: Run the tests and see them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected: the build fails, because `FloorAreaMultiplier` does not exist yet (CS0246) and `DiagnosticCodes` has no `FloorTypeSplit` (CS0117). Each error is reported once, for the `net8.0` target:

```text
tests\Lod.Integration.Tests\AggregatorTests.cs(19,43): error CS0246: The type or namespace name 'FloorAreaMultiplier' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(37,43): error CS0246: The type or namespace name 'FloorAreaMultiplier' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(55,49): error CS0246: The type or namespace name 'FloorAreaMultiplier' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(59,76): error CS0117: 'DiagnosticCodes' does not contain a definition for 'FloorTypeSplit'
tests\Lod.Integration.Tests\AggregatorTests.cs(76,43): error CS0246: The type or namespace name 'FloorAreaMultiplier' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(93,43): error CS0246: The type or namespace name 'FloorAreaMultiplier' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 4: Generalise `Storeys` — replace `src/Lod.Core/Buildings/Storeys.cs` (full file)**

Three changes to the S2 file, none of which changes what `Stack` produces:

1. `Place` delegates each storey to the new public `PlaceAt(IFloor floor, int index, double elevation, int zoneMultiplier)`, which places one floor as storey `index` of the building at the given elevation, with the ID prefix `L{index}/`. `FloorAreaMultiplier` uses it to put a representative storey at its true storey index and elevation (D-045). The `Index` of `PlacedStorey` is now documented as the storey's index in the building.
2. `ResolveStacked` and the new `ResolveRepresentative` share the private `Resolve`. Both split each floor and ceiling by overlap with the storey below and above; uncovered pieces face outdoors, the lowest floors face the ground, and the highest ceilings are roofs. They differ only in the boundary of the overlapping pieces: `Interzone` with the adjacent zone for `ResolveStacked`, as before, and `Adiabatic` without an adjacent zone for `ResolveRepresentative` (D-046).
3. The private `Split` takes that overlap boundary as a parameter.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>A floor placed at its elevation with storey-prefixed zone and surface IDs.</summary>
/// <param name="Index">Index of the storey in the building, from 0 at the bottom.</param>
/// <param name="Elevation">Floor elevation, m.</param>
/// <param name="Height">Floor-to-floor height, m.</param>
/// <param name="Zones">Relocated zones.</param>
/// <param name="Walls">Relocated walls.</param>
public sealed record PlacedStorey(int Index, double Elevation, double Height, IReadOnlyList<Zone> Zones, IReadOnlyList<WallSurface> Walls);

/// <summary>Shared steps of the floor aggregators: input validation, vertical placement, and horizontal boundary resolution.</summary>
public static class Storeys
{
    /// <summary>Checks that there is at least one floor, multipliers are positive, and all floors share one orientation.</summary>
    /// <param name="floors">Floor entries.</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>Errors, if any.</returns>
    public static IReadOnlyList<Diagnostic> Validate(IReadOnlyList<FloorEntry> floors, ToleranceSettings tolerances)
    {
        var diagnostics = new List<Diagnostic>();
        if (floors.Count == 0)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.NoFloors, "A building needs at least one floor."));
            return diagnostics;
        }

        foreach (FloorEntry entry in floors.Where(e => e.Multiplier < 1))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.InvalidParameter, $"Multipliers start at 1, got {entry.Multiplier}."));
        }

        double orientation = floors[0].Floor.OrientationDegrees;
        double toleranceDegrees = tolerances.Angle * 180.0 / Math.PI;
        if (floors.Any(e => Math.Abs(e.Floor.OrientationDegrees - orientation) > toleranceDegrees))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.OrientationMismatch, "All floors of a building must have the same orientation."));
        }

        return diagnostics;
    }

    /// <summary>Stacks floors bottom to top, one storey each, prefixing IDs with <c>L{index}/</c>.</summary>
    /// <param name="storeys">Floors in vertical order with the zone multiplier to apply.</param>
    /// <returns>The placed storeys.</returns>
    public static IReadOnlyList<PlacedStorey> Place(IEnumerable<(IFloor Floor, int ZoneMultiplier)> storeys)
    {
        var placed = new List<PlacedStorey>();
        double elevation = 0.0;
        foreach ((IFloor floor, int multiplier) in storeys)
        {
            placed.Add(PlaceAt(floor, placed.Count, elevation, multiplier));
            elevation += floor.FloorHeight;
        }

        return placed;
    }

    /// <summary>Places a floor as storey <paramref name="index"/> of the building, prefixing IDs with <c>L{index}/</c>.</summary>
    /// <param name="floor">The floor.</param>
    /// <param name="index">Storey index in the building, from 0 at the bottom.</param>
    /// <param name="elevation">Elevation of the storey, m.</param>
    /// <param name="zoneMultiplier">Zone multiplier to apply.</param>
    /// <returns>The placed storey.</returns>
    public static PlacedStorey PlaceAt(IFloor floor, int index, double elevation, int zoneMultiplier)
    {
        string prefix = $"L{index}/";
        ZoneId Rename(ZoneId id) => new(prefix + id.Value);
        Zone[] zones = floor.Zones.Select(z => z.Relocate(Rename(z.Id), elevation, zoneMultiplier)).ToArray();
        WallSurface[] walls = floor.Surfaces.OfType<WallSurface>().Select(w => w.Relocate(Rename, prefix, elevation)).ToArray();
        return new PlacedStorey(index, elevation, floor.FloorHeight, zones, walls);
    }

    /// <summary>
    /// Floors and ceilings of physically stacked storeys: split by overlap with the zones below and above into interzone pieces;
    /// uncovered parts face outdoors; the lowest floors face the ground and the highest ceilings are roofs.
    /// </summary>
    /// <param name="storeys">Placed storeys, bottom to top.</param>
    /// <param name="ops">Polygon operations.</param>
    /// <returns>Horizontal surfaces.</returns>
    public static IReadOnlyList<HorizontalSurface> ResolveStacked(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops) =>
        Resolve(storeys, BoundaryCondition.Interzone, ops);

    /// <summary>
    /// Floors and ceilings of representative storeys (D-046): overlap with the representative storey below or above is adiabatic; uncovered parts face
    /// outdoors; the lowest floors face the ground and the highest ceilings are roofs.
    /// </summary>
    /// <param name="storeys">Representative storeys, bottom to top.</param>
    /// <param name="ops">Polygon operations.</param>
    /// <returns>Horizontal surfaces.</returns>
    public static IReadOnlyList<HorizontalSurface> ResolveRepresentative(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops) =>
        Resolve(storeys, BoundaryCondition.Adiabatic, ops);

    private static IReadOnlyList<HorizontalSurface> Resolve(IReadOnlyList<PlacedStorey> storeys, BoundaryCondition overlap, PolygonOps ops)
    {
        var surfaces = new List<HorizontalSurface>();
        for (int k = 0; k < storeys.Count; k++)
        {
            PlacedStorey storey = storeys[k];
            PlacedStorey? below = k > 0 ? storeys[k - 1] : null;
            PlacedStorey? above = k < storeys.Count - 1 ? storeys[k + 1] : null;
            foreach (Zone zone in storey.Zones)
            {
                Polygon2 footprint = zone.Parts[0].Footprint;
                surfaces.AddRange(Split(zone.Id, HorizontalKind.Floor, footprint, storey.Elevation, below, BoundaryCondition.Ground, overlap, ops));
                surfaces.AddRange(Split(zone.Id, HorizontalKind.Ceiling, footprint, storey.Elevation + storey.Height, above, BoundaryCondition.Outdoors, overlap, ops));
            }
        }

        return surfaces;
    }

    private static IEnumerable<HorizontalSurface> Split(
        ZoneId zone,
        HorizontalKind kind,
        Polygon2 footprint,
        double elevation,
        PlacedStorey? neighbour,
        BoundaryCondition exposed,
        BoundaryCondition overlap,
        PolygonOps ops)
    {
        string tag = kind == HorizontalKind.Floor ? "F" : "C";
        if (neighbour is null)
        {
            yield return new HorizontalSurface(new SurfaceId($"{zone.Value}/{tag}1"), zone, kind, footprint, elevation, exposed, null);
            yield break;
        }

        int number = 1;
        foreach (Zone other in neighbour.Zones)
        {
            foreach (Polygon2 piece in ops.Intersect(footprint, other.Parts[0].Footprint))
            {
                ZoneId? adjacent = overlap == BoundaryCondition.Interzone ? other.Id : null;
                yield return new HorizontalSurface(new SurfaceId($"{zone.Value}/{tag}{number++}"), zone, kind, piece, elevation, overlap, adjacent);
            }
        }

        foreach (Polygon2 piece in ops.Difference(footprint, neighbour.Zones.Select(z => z.Parts[0].Footprint)))
        {
            yield return new HorizontalSurface(new SurfaceId($"{zone.Value}/{tag}{number++}"), zone, kind, piece, elevation, BoundaryCondition.Outdoors, null);
        }
    }
}
```

- [x] **Step 5: Append `FloorTypeSplit` to `src/Lod.Core/Common/DiagnosticCodes.cs`**

Insert the following after the last S3 constant (`public const string ValidationOverridden = "ValidationOverridden";`), before the class's closing brace, with one blank line before the new comment:

```csharp
    /// <summary>A multiplied floor type had exposed floors or ceilings; its exposed storeys were split off as x1 storeys (D-046).</summary>
    public const string FloorTypeSplit = "FloorTypeSplit";
```

Full file after this step:

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

    /// <summary>Two presets share a space type.</summary>
    public const string DuplicateSpaceType = "DuplicateSpaceType";

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

    /// <summary>No program preset exists for a space type the generator needs.</summary>
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

    /// <summary>No single target wall contains a source window (D-039).</summary>
    public const string WindowNotHosted = "WindowNotHosted";

    /// <summary>Validation failed and conversion was blocked.</summary>
    public const string ValidationFailed = "ValidationFailed";

    /// <summary>Validation failed and conversion continued because an override was given.</summary>
    public const string ValidationOverridden = "ValidationOverridden";

    /// <summary>A multiplied floor type had exposed floors or ceilings; its exposed storeys were split off as x1 storeys (D-046).</summary>
    public const string FloorTypeSplit = "FloorTypeSplit";
}
```

- [x] **Step 6: Build the core library and run its tests**

```bash
dotnet build src/Lod.Core -c Release
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`; `Passed!  - Failed:     0, Passed:   104, Skipped:     0, Total:   104` for net8.0. The integration tests still do not build: the five `FloorAreaMultiplier` errors of Step 3 remain; the `FloorTypeSplit` error is gone.

- [x] **Step 7: Implement `FloorAreaMultiplier` — create `src/Lod.Core/Buildings/FloorAreaMultiplier.cs` (full file)**

For each floor type the loop decides whether its floor and ceiling are exposed (`IsExposed`: the footprints of the neighbouring type leave a non-zero area of this type's zone footprints uncovered; the first type's floor and the last type's ceiling always count as exposed), splits the exposed bottom and top storeys of a multiplied type off as × 1 groups, and reports each split type. `StoreyElevations` gives the elevation of every storey of the full stack; each group is placed at storey `First + Count / 2` (integer division, D-045), and the floors and ceilings of the placed storeys come from `Storeys.ResolveRepresentative`.

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>
/// Representative storeys with zone multipliers (D-032). Floor types are listed bottom to top; type <c>i</c> stands for <c>Nᵢ</c> storeys.
/// <list type="bullet">
/// <item>Exposure is never multiplied (D-046): a storey of a multiplied type whose floor or ceiling is not fully covered by the neighbouring type
/// (ground, roof, setback, overhang) is split off as its own ×1 storey, reported with an info diagnostic.</item>
/// <item>The remaining storeys of a type become one storey with their count as zone multiplier, placed at the whole storey nearest the middle
/// of the storeys it stands for (D-045). Every storey sits at its true elevation and the building keeps its true height.</item>
/// <item>Floors and ceilings: overlap with the representative storey below or above is adiabatic; uncovered parts face the ground (lowest
/// storey) or outdoors.</item>
/// </list>
/// </summary>
public sealed class FloorAreaMultiplier : IFloorAggregator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public FloorAreaMultiplier(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <inheritdoc />
    public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors)
    {
        IReadOnlyList<Diagnostic> errors = Storeys.Validate(floors, _tolerances);
        if (errors.Count > 0)
        {
            return Result.Failure<IGeneratedBuilding>(errors);
        }

        var ops = new PolygonOps(_tolerances);
        var diagnostics = new List<Diagnostic>();
        var groups = new List<(IFloor Floor, int First, int Count)>();
        int next = 0;
        for (int i = 0; i < floors.Count; i++)
        {
            FloorEntry entry = floors[i];
            bool floorExposed = i == 0 || IsExposed(entry.Floor, floors[i - 1].Floor, ops);
            bool ceilingExposed = i == floors.Count - 1 || IsExposed(entry.Floor, floors[i + 1].Floor, ops);
            int bottom = floorExposed && entry.Multiplier > 1 ? 1 : 0;
            int top = ceilingExposed && entry.Multiplier - bottom > 1 ? 1 : 0;
            int middle = entry.Multiplier - bottom - top;
            if (bottom + top > 0)
            {
                string parts = string.Join(" + ", new[] { bottom, middle, top }.Where(n => n > 0).Select(n => $"x{n}"));
                diagnostics.Add(Diagnostic.Info(
                    DiagnosticCodes.FloorTypeSplit,
                    $"Floor type {i} (x{entry.Multiplier}) has an exposed {(bottom > 0 ? "floor" : "ceiling")}{(bottom > 0 && top > 0 ? " and ceiling" : string.Empty)}; split into {parts} so exposure is not multiplied (D-046)."));
            }

            if (bottom > 0)
            {
                groups.Add((entry.Floor, next, 1));
            }

            groups.Add((entry.Floor, next + bottom, middle));
            if (top > 0)
            {
                groups.Add((entry.Floor, next + bottom + middle, 1));
            }

            next += entry.Multiplier;
        }

        double[] elevations = StoreyElevations(floors);
        int[] representative = groups.Select(g => g.First + (g.Count / 2)).ToArray();
        PlacedStorey[] storeys = groups
            .Select((g, k) => Storeys.PlaceAt(g.Floor, representative[k], elevations[representative[k]], g.Count))
            .ToArray();
        IEnumerable<Surface> surfaces = storeys.SelectMany(s => s.Walls).Cast<Surface>().Concat(Storeys.ResolveRepresentative(storeys, ops));
        var provenance = Provenance.Of(
            nameof(FloorAreaMultiplier),
            new[]
            {
                new KeyValuePair<string, string>("Multipliers", string.Join(",", floors.Select(e => e.Multiplier))),
                new KeyValuePair<string, string>("Storeys", string.Join(",", groups.Select((g, k) => $"L{representative[k]}x{g.Count}"))),
            },
            floors.Select(e => e.Floor.Provenance).ToArray());
        IGeneratedBuilding building = new GeneratedBuilding(
            floors[0].Floor.OrientationDegrees,
            storeys.SelectMany(s => s.Zones),
            surfaces,
            Enumerable.Empty<InternalMass>(),
            floors,
            provenance);
        return Result.Success(building, diagnostics);
    }

    private bool IsExposed(IFloor floor, IFloor neighbour, PolygonOps ops)
    {
        Polygon2[] cover = neighbour.Zones.Select(z => z.Parts[0].Footprint).ToArray();
        double uncovered = floor.Zones.Sum(z => ops.Difference(z.Parts[0].Footprint, cover).Sum(p => p.Area));
        return !_tolerances.AreaEquals(0.0, uncovered);
    }

    private static double[] StoreyElevations(IReadOnlyList<FloorEntry> floors)
    {
        var elevations = new List<double>();
        double elevation = 0.0;
        foreach (FloorEntry entry in floors)
        {
            for (int k = 0; k < entry.Multiplier; k++)
            {
                elevations.Add(elevation);
                elevation += entry.Floor.FloorHeight;
            }
        }

        return elevations.ToArray();
    }
}
```

- [x] **Step 8: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected (3 facts and 5 theory cases):

```text
Passed!  - Failed:     0, Passed:     8, Skipped:     0, Total:     8, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

Then the whole integration project:

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    46, Skipped:     0, Total:    46` for net8.0 (38 from S3 plus 8). The S2 `Stack` tests, including the snapshot `stack-two-storeys`, still pass, which confirms that the `Storeys` change of Step 4 leaves `Stack` unchanged.

- [x] **Step 9: Commit**

```bash
git add src/Lod.Core/Buildings/Storeys.cs src/Lod.Core/Common/DiagnosticCodes.cs src/Lod.Core/Buildings/FloorAreaMultiplier.cs tests/Lod.Integration.Tests/AggregatorTests.cs
git commit -m "feature(core): add floor area multiplier aggregator"
```

### Task 3: `SingleZoneMerged`

**Files:**
- Create: `src/Lod.Core/Buildings/SingleZoneMerged.cs`
- Test: `tests/Lod.Integration.Tests/AggregatorTests.cs` (three methods added)

**Interfaces:**
- Consumes (S2): `Stack(ToleranceSettings).Aggregate(IReadOnlyList<FloorEntry>)`; `PolygonOps(ToleranceSettings).Union(IEnumerable<Polygon2>) : IReadOnlyList<Polygon2>`; `LayoutSurfaceBuilder(ToleranceSettings).Build(Polygon2 footprint, IReadOnlyList<LayoutZone> zones, double height) : Result<IReadOnlyList<Surface>>`; `LayoutZone(ZoneId Id, Polygon2 Footprint)`; `WallSurface.Relocate(Func<ZoneId, ZoneId> rename, string idPrefix, double dz)`; `WallSurface.Windows`, `WallSurface.GlazedArea`; `ZonePart(Polygon2 Footprint, double Elevation, double Height)`; `Zone(ZoneId id, string name, SpaceType spaceType, IEnumerable<ZonePart> parts, ZoneProgram program, IEnumerable<ZoneId> sourceZones, int multiplier = 1)`; `InternalMass(ZoneId Zone, double SlabArea, int ExposedFaces, double Elevation, IReadOnlyList<SurfaceId> SourceSurfaces)`; `LayoutMeasures.Of(Zone zone, IEnumerable<Surface> surfaces) : ZoneMeasures`. (S1): `ZoneMeasures(double FloorArea, double Volume, double ExteriorWallArea)`; `SourceZoneContribution(ZoneId Zone, ZoneProgram Program, ZoneMeasures Measures, double AreaFraction, double ExteriorWallFraction)`; `EquivalentPropertyAggregator(ToleranceSettings).Aggregate(ZoneId target, ZoneMeasures targetMeasures, IReadOnlyList<SourceZoneContribution> sources) : Result<ZoneProgram>`. (S3): `FacadeAttribution.Compute(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces, ToleranceSettings tolerances)`, `FacadeAttribution.CoverageGaps() : IReadOnlyList<(WallSurface Wall, double CoveredLength)>`; `WindowRehosting.Rehost(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances) : Result<IReadOnlyList<Surface>>`; `DiagnosticCodes.FacadeNotCovered`, `DiagnosticCodes.WindowNotHosted`.
- Produces: `public sealed class SingleZoneMerged : IFloorAggregator` with `public static readonly ZoneId BuildingZone` (`"BUILDING"`), `public SingleZoneMerged(ToleranceSettings tolerances)`, and `public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors)`.

- [x] **Step 1: Write the failing tests — add three methods to `AggregatorTests`**

Insert after `BottomMiddleTopMultiplierMatchesTheStackExactly`, before the closing brace of the class, separated by a blank line. With the detailed floor × 3 the merged zone has three parts (3 × 432 m² × 3 m), 18 source zones, no interzone surface, two slab levels (z = 3 m and 6 m) of 432 m² each replacing 6 floor and 6 ceiling pieces, and 4 outdoor walls per storey. Every enforced check passes, including the enforced ground area, roof area (D-046), and height (D-045) checks, and the building has three times the floor's glazing and windows (D-039).

```csharp
    [Fact]
    public void SingleZoneMergedHasOneZoneWithOnePartPerStorey()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Zone zone = Assert.Single(building.Zones);
        Assert.Equal(3, zone.Parts.Count);
        Assert.Equal(3 * 432.0 * 3.0, zone.Volume, 6);
        Assert.Equal(18, zone.SourceZones.Count);
        Assert.DoesNotContain(building.Surfaces, s => s.Boundary == BoundaryCondition.Interzone);
    }

    [Fact]
    public void SingleZoneMergedTurnsSlabsIntoInternalMass()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Assert.Equal(new[] { 3.0, 6.0 }, building.InternalMasses.Select(m => m.Elevation));
        Assert.All(building.InternalMasses, m => Assert.Equal(432.0, m.SlabArea, 6));
        Assert.All(building.InternalMasses, m => Assert.Equal(2, m.ExposedFaces));
        Assert.All(building.InternalMasses, m => Assert.Equal(12, m.SourceSurfaces.Count));
    }

    [Fact]
    public void SingleZoneMergedKeepsGroundRoofAndGlazing()
    {
        IFloor floor = Pipeline.DetailedFloor();
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(floor, 3) }).Value;

        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks.Where(c => c.Enforced), c => Assert.True(c.Passed, c.Check));
        Assert.Contains(report.Checks, c => c.Check == "Building.GroundArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.RoofArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.Height" && c.Passed && c.Enforced);
        Assert.Equal(3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), building.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), 6);
        Assert.Equal(3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.Windows.Count), building.Surfaces.OfType<WallSurface>().Sum(w => w.Windows.Count));
        Assert.Equal(12, building.Surfaces.OfType<WallSurface>().Count());
    }
```

- [x] **Step 2: Run the tests and see them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected: the build fails, reported once for the `net8.0` target:

```text
tests\Lod.Integration.Tests\AggregatorTests.cs(104,43): error CS0246: The type or namespace name 'SingleZoneMerged' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(116,43): error CS0246: The type or namespace name 'SingleZoneMerged' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\AggregatorTests.cs(128,43): error CS0246: The type or namespace name 'SingleZoneMerged' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Implement `SingleZoneMerged` — create `src/Lod.Core/Buildings/SingleZoneMerged.cs` (full file)**

```csharp
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

/// <summary>
/// The whole building as one zone (D-021), built from the fully stacked building: one zone part per storey; outdoor walls rebuilt per storey,
/// required to cover every source façade (D-041), keeping every source window in place (D-039); walls between merged zones discarded (D-034); slabs between storeys turned
/// into internal mass with both faces exposed, one entry per slab level (D-031, ADR-009); ground, roof, and exposed floors kept.
/// </summary>
public sealed class SingleZoneMerged : IFloorAggregator
{
    /// <summary>ID of the single zone.</summary>
    public static readonly ZoneId BuildingZone = new("BUILDING");

    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SingleZoneMerged(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <inheritdoc />
    public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors)
    {
        Result<IGeneratedBuilding> stacked = new Stack(_tolerances).Aggregate(floors);
        if (!stacked.IsSuccess)
        {
            return stacked;
        }

        IGeneratedBuilding source = stacked.Value;
        var ops = new PolygonOps(_tolerances);
        var builder = new LayoutSurfaceBuilder(_tolerances);
        var parts = new List<ZonePart>();
        var walls = new List<Surface>();
        foreach (IGrouping<double, Zone> storey in source.Zones.GroupBy(z => z.Parts[0].Elevation).OrderBy(g => g.Key))
        {
            double height = storey.First().Parts[0].Height;
            IReadOnlyList<Polygon2> outlines = ops.Union(storey.Select(z => z.Parts[0].Footprint));
            for (int k = 0; k < outlines.Count; k++)
            {
                parts.Add(new ZonePart(outlines[k], storey.Key, height));
                Result<IReadOnlyList<Surface>> built = builder.Build(outlines[k], new[] { new LayoutZone(BuildingZone, outlines[k]) }, height);
                if (!built.IsSuccess)
                {
                    return Result.Failure<IGeneratedBuilding>(built.Diagnostics);
                }

                string prefix = $"S{parts.Count - 1}/";
                walls.AddRange(built.Value.OfType<WallSurface>().Select(w => w.Relocate(id => id, prefix, storey.Key)));
            }
        }

        FacadeAttribution facade = FacadeAttribution.Compute(source.Surfaces, walls, _tolerances);
        Diagnostic[] gaps = facade.CoverageGaps()
            .Select(g => Diagnostic.Error(DiagnosticCodes.FacadeNotCovered, $"Rebuilt façades cover {g.CoveredLength:0.######} m of this {g.Wall.Length:0.######} m wall (D-041).", g.Wall.Id.Value))
            .ToArray();
        if (gaps.Length > 0)
        {
            return Result.Failure<IGeneratedBuilding>(gaps);
        }

        Result<IReadOnlyList<Surface>> rehosted = WindowRehosting.Rehost(source.Surfaces, walls, _tolerances);
        if (!rehosted.IsSuccess)
        {
            return Result.Failure<IGeneratedBuilding>(rehosted.Diagnostics);
        }

        IReadOnlyList<Surface> glazedWalls = rehosted.Value;
        var diagnostics = new List<Diagnostic>();
        HorizontalSurface[] horizontal = source.Surfaces.OfType<HorizontalSurface>().ToArray();
        InternalMass[] masses = horizontal
            .Where(h => h.Kind == HorizontalKind.Floor && h.Boundary == BoundaryCondition.Interzone)
            .GroupBy(h => h.Elevation)
            .OrderBy(g => g.Key)
            .Select(level => new InternalMass(
                BuildingZone,
                level.Sum(h => h.Area),
                ExposedFaces: 2,
                level.Key,
                level.Select(h => h.Id).Concat(horizontal.Where(c => c.Kind == HorizontalKind.Ceiling && c.Boundary == BoundaryCondition.Interzone && c.Elevation == level.Key).Select(c => c.Id)).ToArray()))
            .ToArray();
        IEnumerable<Surface> envelope = horizontal
            .Where(h => h.Boundary != BoundaryCondition.Interzone)
            .Select(h => new HorizontalSurface(h.Id, BuildingZone, h.Kind, h.Polygon, h.Elevation, h.Boundary, null));

        var measures = new ZoneMeasures(parts.Sum(p => p.Footprint.Area), parts.Sum(p => p.Volume), glazedWalls.Sum(w => w.Area));
        SourceZoneContribution[] contributions = source.Zones
            .Select(z => new SourceZoneContribution(z.Id, z.Program, LayoutMeasures.Of(z, source.Surfaces), 1.0, 1.0))
            .ToArray();
        Result<ZoneProgram> program = new EquivalentPropertyAggregator(_tolerances).Aggregate(BuildingZone, measures, contributions);
        diagnostics.AddRange(program.Diagnostics);
        if (!program.IsSuccess || diagnostics.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            return Result.Failure<IGeneratedBuilding>(diagnostics);
        }

        SpaceType[] types = source.Zones.Select(z => z.SpaceType).Distinct().ToArray();
        var zone = new Zone(BuildingZone, "Building", types.Length == 1 ? types[0] : SpaceType.Mixed, parts, program.Value, source.Zones.Select(z => z.Id));
        var provenance = Provenance.Of(
            nameof(SingleZoneMerged),
            new[] { new KeyValuePair<string, string>("Multipliers", string.Join(",", floors.Select(e => e.Multiplier))) },
            floors.Select(e => e.Floor.Provenance).ToArray());
        IGeneratedBuilding building = new GeneratedBuilding(source.OrientationDegrees, new[] { zone }, glazedWalls.Concat(envelope), masses, floors, provenance);
        return Result.Success(building, diagnostics);
    }
}
```

- [x] **Step 4: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    11, Skipped:     0, Total:    11, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

Then:

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    49, Skipped:     0, Total:    49` for net8.0.

- [x] **Step 5: Commit**

```bash
git add src/Lod.Core/Buildings/SingleZoneMerged.cs tests/Lod.Integration.Tests/AggregatorTests.cs
git commit -m "feature(core): add single zone merged aggregator"
```

### Task 4: Every simplifier × aggregator combination validates; aggregator snapshots

This is the Checkpoint 1 exit criterion in code: 4 simplifiers × 3 aggregators = 12 cases, each with the floor entries 1 / 3 / 1, validated against the fully stacked reference (ground area, roof area, exposed floor area, and height enforced). For `FloorAreaMultiplier` the middle type covers and is covered by its neighbours, so nothing is split; its representative storey is storey 2 (`L0x1,L2x3,L4x1`).

**Files:**
- Create: `tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.txt`, `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.txt`
- Test: `tests/Lod.Integration.Tests/AggregatorTests.cs` (completed)

**Interfaces:**
- Consumes: `Pipeline.Floor(IPlanSimplifier simplifier, LinearPlanParameters? parameters = null)` (S2 test support); `NoSimplification` (S2); `SemanticMerge(ToleranceSettings)`, `PerimeterCore(ToleranceSettings, double perimeterDepth)`, `SingleZonePerFloor(ToleranceSettings)` (S3); `Stack` (S2); `FloorAreaMultiplier`, `SingleZoneMerged` (Tasks 2–3); `TextReport.Describe(IGeneratedBuilding) : string` (S2); `Snapshot.Match(string actual, string name)` (S2, `tests/Shared/Snapshot.cs`).
- Produces: tests only.

- [x] **Step 1: Add the matrix test**

Add `using Lod.Core.Simplification;` between `using Lod.Core.Model;` and `using Lod.Core.Validation;` at the top of `AggregatorTests.cs`. The `using` block then reads:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Xunit;
```

Then insert after `SingleZoneMergedKeepsGroundRoofAndGlazing`, before the closing brace of the class, separated by a blank line:

```csharp
    public static IEnumerable<object[]> Matrix() =>
        from simplifier in new[] { "NoSimplification", "SemanticMerge", "PerimeterCore", "SingleZonePerFloor" }
        from aggregator in new[] { "Stack", "FloorAreaMultiplier", "SingleZoneMerged" }
        select new object[] { simplifier, aggregator };

    [Theory]
    [MemberData(nameof(Matrix))]
    public void EverySimplifierAndAggregatorCombinationValidates(string simplifier, string aggregator)
    {
        IFloor floor = Pipeline.Floor(Simplifier(simplifier));
        FloorEntry[] entries = { new(floor, 1), new(floor, 3), new(floor, 1) };

        IGeneratedBuilding building = Aggregator(aggregator).Aggregate(entries).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
    }

    private static IPlanSimplifier Simplifier(string name) => name switch
    {
        "NoSimplification" => new NoSimplification(),
        "SemanticMerge" => new SemanticMerge(Pipeline.Tolerances),
        "PerimeterCore" => new PerimeterCore(Pipeline.Tolerances, 4.57),
        "SingleZonePerFloor" => new SingleZonePerFloor(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown simplifier."),
    };

    private static IFloorAggregator Aggregator(string name) => name switch
    {
        "Stack" => new Stack(Pipeline.Tolerances),
        "FloorAreaMultiplier" => new FloorAreaMultiplier(Pipeline.Tolerances),
        "SingleZoneMerged" => new SingleZoneMerged(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown aggregator."),
    };
```

- [x] **Step 2: Run the matrix**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    23, Skipped:     0, Total:    23, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

Then:

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    61, Skipped:     0, Total:    61` for net8.0.

This is an acceptance test over code that already exists (S2, S3, Tasks 2–3), so it passes on its first run; there is no red phase. If any case fails, stop: the defect is in Task 2 or 3 (or earlier), and the test must not be changed to pass.

- [x] **Step 3: Add the snapshot tests**

Add `using Lod.Tests.Shared;` between `using Lod.Core.Validation;` and `using Xunit;`. Then insert after the closing brace of `EverySimplifierAndAggregatorCombinationValidates`, before `private static IPlanSimplifier Simplifier`, separated by blank lines:

```csharp
    [Fact]
    public void MultiplierSnapshot()
    {
        IFloor floor = Pipeline.Floor(Simplifier("PerimeterCore"));
        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 2), new FloorEntry(floor, 1) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-FloorAreaMultiplier");
    }

    [Fact]
    public void SingleZoneMergedSnapshot()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-SingleZoneMerged");
    }
```

- [x] **Step 4: Run the tests and see the snapshots fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected on net8.0:

```text
Failed!  - Failed:     2, Passed:    23, Skipped:     0, Total:    25, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

with the messages

```text
Snapshot 'aggregator-FloorAreaMultiplier' is missing or differs. Review Snapshots/aggregator-FloorAreaMultiplier.received.txt and rename it to aggregator-FloorAreaMultiplier.txt to accept.
Snapshot 'aggregator-SingleZoneMerged' is missing or differs. Review Snapshots/aggregator-SingleZoneMerged.received.txt and rename it to aggregator-SingleZoneMerged.txt to accept.
```

and the files `tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.received.txt` and `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.received.txt` (git-ignored by `*.received.*`).

- [x] **Step 5: Review the received files**

Review each received file against the expected content in Steps 6 and 7; it must be identical. What to look for: in `aggregator-FloorAreaMultiplier`, the sources line `1,2,1`; zones on storeys `L0/`, `L2/`, and `L3/` only, with `multiplier=2` on the `L2/` zones (the middle type stands for storeys 1 and 2 and is represented by storey 1 + ⌊2/2⌋ = 2, D-045) and no `L1/` zone; walls at z = 0 (`L0/`), z = 6 (`L2/`), and z = 9 (`L3/`), the perimeter zones' outdoor walls with the plan's windows (`window(offset=… sill=… width×height)`); `Ground` floors only on `L0/`, `Outdoors` ceilings only on `L3/` (z = 12), every other floor and ceiling `Adiabatic` (single `…/F1` and `…/C1` pieces, since the storeys have identical footprints); and no `mass` line. Nothing is split, because the middle type is covered by its neighbours. In `aggregator-SingleZoneMerged`, one zone `BUILDING` with `parts=2` and 12 sources, four outdoor walls per storey (`S0/…` at z = 0, `S1/…` at z = 3) carrying the detailed floor's windows at the same offsets (three on the east, three on the north, one on the west, and three on the south wall; glazing North 19.2, East 15.6, South 19.2, West 5.4 m²), six ground floors, six roofs at z = 6, and one `mass BUILDING area=432.000000 faces=2 z=3.000000`. Then accept them:

```powershell
Move-Item tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.received.txt tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.txt
Move-Item tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.received.txt tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.txt
```

- [x] **Step 6: Expected content of `tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.txt`**

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
surface L0/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface L0/P-North/W2 Interzone adjacent=L0/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=0.000000 facing=West glazing=0.000000
surface L0/P-North/W3 Interzone adjacent=L0/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=0.000000 facing=South glazing=0.000000
surface L0/P-North/W4 Interzone adjacent=L0/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=0.000000 facing=South glazing=0.000000
surface L0/P-East/W1 Interzone adjacent=L0/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=0.000000 facing=North glazing=0.000000
surface L0/P-East/W2 Interzone adjacent=L0/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=0.000000 facing=West glazing=0.000000
surface L0/P-East/W3 Interzone adjacent=L0/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface L0/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface L0/P-South/W1 Interzone adjacent=L0/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=0.000000 facing=North glazing=0.000000
surface L0/P-South/W2 Interzone adjacent=L0/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=0.000000 facing=North glazing=0.000000
surface L0/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
surface L0/P-South/W4 Interzone adjacent=L0/P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=0.000000 facing=North glazing=0.000000
surface L0/P-West/W1 Interzone adjacent=L0/CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=0.000000 facing=East glazing=0.000000
surface L0/P-West/W2 Interzone adjacent=L0/P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface L0/P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L0/P-West/W4 Interzone adjacent=L0/P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=0.000000 facing=South glazing=0.000000
surface L0/CORE/W1 Interzone adjacent=L0/P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=0.000000 facing=South glazing=0.000000
surface L0/CORE/W2 Interzone adjacent=L0/P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=0.000000 facing=East glazing=0.000000
surface L0/CORE/W3 Interzone adjacent=L0/P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=0.000000 facing=North glazing=0.000000
surface L0/CORE/W4 Interzone adjacent=L0/P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=0.000000 facing=West glazing=0.000000
surface L2/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=6.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface L2/P-North/W2 Interzone adjacent=L2/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=6.000000 facing=West glazing=0.000000
surface L2/P-North/W3 Interzone adjacent=L2/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=6.000000 facing=South glazing=0.000000
surface L2/P-North/W4 Interzone adjacent=L2/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=6.000000 facing=South glazing=0.000000
surface L2/P-East/W1 Interzone adjacent=L2/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=6.000000 facing=North glazing=0.000000
surface L2/P-East/W2 Interzone adjacent=L2/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=6.000000 facing=West glazing=0.000000
surface L2/P-East/W3 Interzone adjacent=L2/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=6.000000 facing=West glazing=0.000000
surface L2/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=6.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface L2/P-South/W1 Interzone adjacent=L2/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=6.000000 facing=North glazing=0.000000
surface L2/P-South/W2 Interzone adjacent=L2/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=6.000000 facing=North glazing=0.000000
surface L2/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=6.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
surface L2/P-South/W4 Interzone adjacent=L2/P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=6.000000 facing=North glazing=0.000000
surface L2/P-West/W1 Interzone adjacent=L2/CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=6.000000 facing=East glazing=0.000000
surface L2/P-West/W2 Interzone adjacent=L2/P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=6.000000 facing=East glazing=0.000000
surface L2/P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=6.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L2/P-West/W4 Interzone adjacent=L2/P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=6.000000 facing=South glazing=0.000000
surface L2/CORE/W1 Interzone adjacent=L2/P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=6.000000 facing=South glazing=0.000000
surface L2/CORE/W2 Interzone adjacent=L2/P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=6.000000 facing=East glazing=0.000000
surface L2/CORE/W3 Interzone adjacent=L2/P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=6.000000 facing=North glazing=0.000000
surface L2/CORE/W4 Interzone adjacent=L2/P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=6.000000 facing=West glazing=0.000000
surface L3/P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=9.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface L3/P-North/W2 Interzone adjacent=L3/P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=9.000000 facing=West glazing=0.000000
surface L3/P-North/W3 Interzone adjacent=L3/CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=9.000000 facing=South glazing=0.000000
surface L3/P-North/W4 Interzone adjacent=L3/P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=9.000000 facing=South glazing=0.000000
surface L3/P-East/W1 Interzone adjacent=L3/P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=9.000000 facing=North glazing=0.000000
surface L3/P-East/W2 Interzone adjacent=L3/CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=9.000000 facing=West glazing=0.000000
surface L3/P-East/W3 Interzone adjacent=L3/P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=9.000000 facing=West glazing=0.000000
surface L3/P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=9.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface L3/P-South/W1 Interzone adjacent=L3/CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=9.000000 facing=North glazing=0.000000
surface L3/P-South/W2 Interzone adjacent=L3/P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=9.000000 facing=North glazing=0.000000
surface L3/P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=9.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
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

- [x] **Step 7: Expected content of `tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.txt`**

```text
building orientation=0.000000 sources=2
zone BUILDING Mixed "Building" area=864.000000 volume=2592.000000 parts=2 multiplier=1 sources=[L0/ST,L0/CO,L0/US1,L0/US2,L0/UN1,L0/UN2,L1/ST,L1/CO,L1/US1,L1/US2,L1/UN1,L1/UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface S0/BUILDING/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface S0/BUILDING/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface S0/BUILDING/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S0/BUILDING/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
surface S1/BUILDING/W1 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=3.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface S1/BUILDING/W2 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=3.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface S1/BUILDING/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=3.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface S1/BUILDING/W4 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=3.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
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

- [x] **Step 8: Full file after this task: `tests/Lod.Integration.Tests/AggregatorTests.cs`**

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
    public void FloorAreaMultiplierCarriesMultipliersAndOrderedBoundaries()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
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

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;

        // Storeys 1-8 are represented by storey 5, the whole storey nearest their middle (D-045); the top storey stays storey 9.
        Assert.Equal(new[] { "L0/", "L5/", "L9/" }, building.Zones.Select(z => z.Id.Value.Substring(0, 3)).Distinct());
        Assert.Equal(new[] { 0.0, 15.0, 27.0 }, building.Zones.Select(z => z.Parts[0].Elevation).Distinct());
        Assert.Equal(30.0, Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height, 9);
        Assert.Equal("L0x1,L5x8,L9x1", building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
    }

    [Theory]
    [InlineData(new[] { 5 }, "L0x1,L2x3,L4x1")]
    [InlineData(new[] { 2, 1 }, "L0x1,L1x1,L2x1")]
    [InlineData(new[] { 1, 8, 2 }, "L0x1,L5x8,L9x1,L10x1")]
    public void ExposedStoreysOfMultipliedTypesAreSplitOff(int[] multipliers, string storeys)
    {
        IFloor floor = Pipeline.DetailedFloor();

        Result<IGeneratedBuilding> result = new FloorAreaMultiplier(Pipeline.Tolerances).Aggregate(multipliers.Select(n => new FloorEntry(floor, n)).ToArray());
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(result.Value);

        Assert.Equal(storeys, result.Value.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.FloorTypeSplit && d.Severity == DiagnosticSeverity.Info);
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }

    [Theory]
    [InlineData("setback", "wide x1, wide x4, narrow x3", "L0x1,L2x3,L4x1,L6x2,L7x1")]
    [InlineData("overhang", "narrow x2, wide x3", "L0x1,L1x1,L2x1,L3x1,L4x1")]
    public void VaryingFootprintsKeepExposedAreasWithoutMultiplyingThem(string name, string types, string storeys)
    {
        // Wide: 24 m x 18 m, two units per row. Narrow: 14 m x 18 m from the same west end, one unit per row. Either way 180 m² is exposed.
        IFloor wide = Pipeline.DetailedFloor();
        IFloor narrow = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });
        FloorEntry[] entries = types.Split(',')
            .Select(t => t.Trim().Split(new[] { " x" }, StringSplitOptions.None))
            .Select(t => new FloorEntry(t[0] == "wide" ? wide : narrow, int.Parse(t[1], System.Globalization.CultureInfo.InvariantCulture)))
            .ToArray();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances).Aggregate(entries).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.Equal(storeys, building.Provenance.Parameters.Single(p => p.Key == "Storeys").Value);
        Assert.All(report.Checks, c => Assert.True(c.Passed, $"{name}: {c.Check}"));
        Dictionary<ZoneId, int> multiplier = building.Zones.ToDictionary(z => z.Id, z => z.Multiplier);
        HorizontalSurface[] exposed = building.Surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary != BoundaryCondition.Adiabatic).ToArray();
        Assert.All(exposed, h => Assert.Equal(1, multiplier[h.Zone]));
        double roof = Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees).Height;
        Assert.Equal(180.0, exposed.Where(h => h.Boundary == BoundaryCondition.Outdoors && h.Elevation < roof - 1.0).Sum(h => h.Area), 6);
    }

    [Fact]
    public void BottomMiddleTopMultiplierMatchesTheStackExactly()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 8), new FloorEntry(floor, 1) }).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks, c => Assert.True(c.Passed, c.Check));
    }

    [Fact]
    public void SingleZoneMergedHasOneZoneWithOnePartPerStorey()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Zone zone = Assert.Single(building.Zones);
        Assert.Equal(3, zone.Parts.Count);
        Assert.Equal(3 * 432.0 * 3.0, zone.Volume, 6);
        Assert.Equal(18, zone.SourceZones.Count);
        Assert.DoesNotContain(building.Surfaces, s => s.Boundary == BoundaryCondition.Interzone);
    }

    [Fact]
    public void SingleZoneMergedTurnsSlabsIntoInternalMass()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 3) }).Value;

        Assert.Equal(new[] { 3.0, 6.0 }, building.InternalMasses.Select(m => m.Elevation));
        Assert.All(building.InternalMasses, m => Assert.Equal(432.0, m.SlabArea, 6));
        Assert.All(building.InternalMasses, m => Assert.Equal(2, m.ExposedFaces));
        Assert.All(building.InternalMasses, m => Assert.Equal(12, m.SourceSurfaces.Count));
    }

    [Fact]
    public void SingleZoneMergedKeepsGroundRoofAndGlazing()
    {
        IFloor floor = Pipeline.DetailedFloor();
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(floor, 3) }).Value;

        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
        Assert.All(report.Checks.Where(c => c.Enforced), c => Assert.True(c.Passed, c.Check));
        Assert.Contains(report.Checks, c => c.Check == "Building.GroundArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.RoofArea" && c.Passed && c.Enforced);
        Assert.Contains(report.Checks, c => c.Check == "Building.Height" && c.Passed && c.Enforced);
        Assert.Equal(3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), building.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea), 6);
        Assert.Equal(3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.Windows.Count), building.Surfaces.OfType<WallSurface>().Sum(w => w.Windows.Count));
        Assert.Equal(12, building.Surfaces.OfType<WallSurface>().Count());
    }

    public static IEnumerable<object[]> Matrix() =>
        from simplifier in new[] { "NoSimplification", "SemanticMerge", "PerimeterCore", "SingleZonePerFloor" }
        from aggregator in new[] { "Stack", "FloorAreaMultiplier", "SingleZoneMerged" }
        select new object[] { simplifier, aggregator };

    [Theory]
    [MemberData(nameof(Matrix))]
    public void EverySimplifierAndAggregatorCombinationValidates(string simplifier, string aggregator)
    {
        IFloor floor = Pipeline.Floor(Simplifier(simplifier));
        FloorEntry[] entries = { new(floor, 1), new(floor, 3), new(floor, 1) };

        IGeneratedBuilding building = Aggregator(aggregator).Aggregate(entries).Value;
        ValidationReport report = new BuildingValidator(Pipeline.Tolerances).Validate(building);

        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void MultiplierSnapshot()
    {
        IFloor floor = Pipeline.Floor(Simplifier("PerimeterCore"));
        IGeneratedBuilding building = new FloorAreaMultiplier(Pipeline.Tolerances)
            .Aggregate(new[] { new FloorEntry(floor, 1), new FloorEntry(floor, 2), new FloorEntry(floor, 1) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-FloorAreaMultiplier");
    }

    [Fact]
    public void SingleZoneMergedSnapshot()
    {
        IGeneratedBuilding building = new SingleZoneMerged(Pipeline.Tolerances).Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;

        Snapshot.Match(TextReport.Describe(building), "aggregator-SingleZoneMerged");
    }

    private static IPlanSimplifier Simplifier(string name) => name switch
    {
        "NoSimplification" => new NoSimplification(),
        "SemanticMerge" => new SemanticMerge(Pipeline.Tolerances),
        "PerimeterCore" => new PerimeterCore(Pipeline.Tolerances, 4.57),
        "SingleZonePerFloor" => new SingleZonePerFloor(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown simplifier."),
    };

    private static IFloorAggregator Aggregator(string name) => name switch
    {
        "Stack" => new Stack(Pipeline.Tolerances),
        "FloorAreaMultiplier" => new FloorAreaMultiplier(Pipeline.Tolerances),
        "SingleZoneMerged" => new SingleZoneMerged(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown aggregator."),
    };
}
```

- [x] **Step 9: Run the tests and see them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.AggregatorTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    25, Skipped:     0, Total:    25, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

Then the whole solution:

```bash
dotnet test BEMGen.sln -c Release
```

Expected, on net8.0:

```text
Passed!  - Failed:     0, Passed:   104, Skipped:     0, Total:   104, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    17, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    63, Skipped:     0, Total:    63, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

(The order of the lines may differ.)

- [x] **Step 10: Commit**

```bash
git status --short
git add tests/Lod.Integration.Tests/AggregatorTests.cs tests/Lod.Integration.Tests/Snapshots/aggregator-FloorAreaMultiplier.txt tests/Lod.Integration.Tests/Snapshots/aggregator-SingleZoneMerged.txt
git commit -m "test(validation): check every simplifier and aggregator combination and add aggregator snapshots"
```

Expected before `git add`: only these three paths are listed (no `*.received.txt`).

- [x] **Step 11: Merge Slice B (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/aggregators
git push origin main
git branch -d feature/aggregators
```

Expected: `VERIFY PASSED`, with 104 core, 17 generators, and 63 integration tests passed on net8.0.

---

## Slice C — `feature/grasshopper-aggregator-components`

### Task 5: *Floor Area Multiplier* and *Single Zone Merged* components

Grasshopper code cannot be unit-tested without Rhino: write, build with 0 warnings, commit, smoke-test by hand. Building-level validation needs no new component: the S3 *Validate* component already accepts buildings and *Convert2BEM* already validates them.

**Files:**
- Create: `src/Lod.Grasshopper/Components/AggregatorComponents.cs`

**Interfaces:**
- Consumes (S2, `src/Lod.Grasshopper/Components/PipelineComponents.cs`): `public abstract class FloorAggregatorComponent : GH_Component` with `protected FloorAggregatorComponent(string name, string nickname, string description)` (category `BEMGen`, panel `4 Aggregate`), `protected abstract string MultiplierDescription { get; }`, `protected abstract IFloorAggregator CreateAggregator()`; inputs Floors (`F`, list, bottom to top) and Multipliers (`N`, optional integer list, one per floor or none for all 1); output Building (`Bldg`); aggregator diagnostics become runtime messages. Core: `FloorAreaMultiplier`, `SingleZoneMerged`, `ToleranceSettings.Default`.
- Produces: `FloorAreaMultiplierComponent`, `SingleZoneMergedComponent` with the GUIDs below.

| Component | Nickname | Class | GUID | Description (from the code) | Multipliers input means |
| --- | --- | --- | --- | --- | --- |
| *Floor Area Multiplier* | Mult | `FloorAreaMultiplierComponent` | `e4b44821-c9ed-49b9-9c4e-7c08355254dd` | "Representative storeys with zone multipliers (D-032). Each floor type stands for N storeys; its storeys with exposed floors or ceilings (ground, roof, setbacks) are split off as x1 storeys so exposure is never multiplied (D-046). Storeys keep their true elevations (D-045); overlap between storeys is adiabatic." | How many storeys each floor type stands for (D-032). Storeys with an exposed floor or ceiling are split off as × 1 storeys and reported as a remark (`FloorTypeSplit`, D-046); the remaining storeys of the type become one storey at the whole storey nearest their middle, whose zones carry their count as multiplier (D-045). Default 1. |
| *Single Zone Merged* | 1Zone | `SingleZoneMergedComponent` | `506d5037-de93-4aee-a6c4-47dcc97509e1` | "The whole building as one zone (D-021): slabs become internal mass (D-031), walls between merged zones are discarded (D-034)." | How many storeys each floor stands for; the storeys are stacked explicitly (as in *Stack Floors*) before they are merged into one zone. Default 1. |

For comparison, *Stack Floors* (S2) reads Multipliers as explicit repetition.

- [x] **Step 1: Create the branch**

```bash
git switch -c feature/grasshopper-aggregator-components main
```

- [x] **Step 2: Create `src/Lod.Grasshopper/Components/AggregatorComponents.cs` (full file)**

```csharp
using System;
using Lod.Core.Buildings;
using Lod.Core.Common;

namespace Lod.Grasshopper.Components;

public sealed class FloorAreaMultiplierComponent : FloorAggregatorComponent
{
    public FloorAreaMultiplierComponent()
        : base(
            "Floor Area Multiplier",
            "Mult",
            "Representative storeys with zone multipliers (D-032). Each floor type stands for N storeys; its storeys with exposed floors or ceilings (ground, roof, setbacks) are split off as x1 storeys so exposure is never multiplied (D-046). Storeys keep their true elevations (D-045); overlap between storeys is adiabatic.")
    {
    }

    public override Guid ComponentGuid => new("e4b44821-c9ed-49b9-9c4e-7c08355254dd");

    protected override string MultiplierDescription => "How many storeys each floor type stands for. Default 1.";

    protected override IFloorAggregator CreateAggregator() => new FloorAreaMultiplier(ToleranceSettings.Default);
}

public sealed class SingleZoneMergedComponent : FloorAggregatorComponent
{
    public SingleZoneMergedComponent()
        : base(
            "Single Zone Merged",
            "1Zone",
            "The whole building as one zone (D-021): slabs become internal mass (D-031), walls between merged zones are discarded (D-034).")
    {
    }

    public override Guid ComponentGuid => new("506d5037-de93-4aee-a6c4-47dcc97509e1");

    protected override string MultiplierDescription => "How many storeys each floor stands for (stacked explicitly before merging). Default 1.";

    protected override IFloorAggregator CreateAggregator() => new SingleZoneMerged(ToleranceSettings.Default);
}
```

- [x] **Step 3: Build**

```bash
dotnet build BEMGen.sln -c Release
```

Expected: `Build succeeded.`, `0 Warning(s)`, `0 Error(s)`, and the plugin written for `net7.0`:

```text
Lod.Grasshopper -> …\src\Lod.Grasshopper\bin\Release\net7.0\BEMGen.gha
```

- [x] **Step 4: Manual check in Rhino 8 (person)**

Load the freshly built plugin as described in `docs/development/grasshopper-smoke-test.md`. The **BEMGen › 4 Aggregate** panel shows *Stack Floors*, *Floor Area Multiplier*, and *Single Zone Merged*; hovering each component shows the description in the table above, and hovering each Multipliers input shows its `MultiplierDescription`. The full S4 checklist follows in Task 7.

- [x] **Step 5: Commit**

```bash
git add src/Lod.Grasshopper/Components/AggregatorComponents.cs
git commit -m "feature(grasshopper): add floor area multiplier and single zone merged components"
```

### Task 6: `docs/architecture/pipeline.md`

**Files:**
- Create: `docs/architecture/pipeline.md`

**Interfaces:**
- Consumes: every component file under `src/Lod.Grasshopper` (names, panels, inputs, outputs, GUIDs); `docs/architecture/domain-model.md` (S1), `docs/architecture/convert2bem.md` (S2), `docs/architecture/validation.md` (S3), ADR-008 (S3), ADR-009 (Task 1).
- Produces: the pipeline reference that README and AGENTS.md link to in the close-out.

- [x] **Step 1: Write `docs/architecture/pipeline.md` with exactly this content**

````markdown
# BEMGen pipeline

At Checkpoint 1 (stages S0–S4, D-030) the pipeline is complete for the linear plan. This document describes each step, the rules it applies, where results are validated, and the Grasshopper components that expose it. The domain types are described in [domain-model.md](domain-model.md), the validation checks in [validation.md](validation.md), and the `Convert2BEM` output layout in [convert2bem.md](convert2bem.md).

## Overview

```text
program presets          ProgramPreset, ProgramPresetSet                    one preset per space type, conditioned or not
  → plan generator       LinearPlanGenerator : PlanGenerator<...>           → IGeneratedPlan        Z0: one zone per dwelling unit, explicit windows
  → IPlanSimplifier      NoSimplification | SemanticMerge |                 → IFloor                Z0 | Z1 | Z2 | Z3, windows kept in place (W0)
                         PerimeterCore | SingleZonePerFloor
  (window transformation W1–W5: stage S5, not in Checkpoint 1)
  → IFloorAggregator     Stack | FloorAreaMultiplier | SingleZoneMerged     → IGeneratedBuilding    floors bottom to top as FloorEntry(IFloor, Multiplier)
  → validation           FloorValidator, BuildingValidator                  → ValidationReport
  → Convert2BEM          Grasshopper component                              → data trees for a ClimateStudio definition (provisional, D-023)
```

- All logic lives in `Lod.Core` and `Lod.Generators`, which reference neither Rhino nor Grasshopper; their tests run with `dotnet test`. `Lod.Grasshopper` wraps each pipeline type in a Goo with a viewport preview and exposes one component per step (D-017, D-018).
- Every step returns `Result<T>`: a value or errors, plus warnings and info diagnostics with stable codes (`DiagnosticCodes`). Components show diagnostics as runtime messages (error, warning, remark); after an error there is no output.
- Pipeline objects are immutable. Every plan, floor, and building carries a `Provenance` record (operation, parameters, inputs, code version), which the *Inspect* component prints.
- Numerical tolerances come only from `ToleranceSettings` (ADR-004). The same inputs always give the same output.
- At Checkpoint 1 every zoning level keeps the generator's windows unchanged (W0). The window axis W1–W5 of the research brief is stage S5 (D-039).

## Steps

### 1. Program presets

| | |
| --- | --- |
| Types | `Schedule`, `LoadDefinition`, `Thermostat`, `ZoneProgram`, `ProgramPreset`, `ProgramPresetSet`, `ExampleResidentialPresets` |
| Components | *Schedule*, *Load*, *Program Preset* (input *Conditioned*), *Example Residential Presets* |
| Decisions | D-024, D-026, D-038, D-047; ADR-003, ADR-005, ADR-007 |

- A program preset holds the zone program of one space type and the window-to-wall ratio in [0, 1) that the plan generator uses (D-024, D-026). A preset set holds at most one preset per space type.
- Conditioning comes from the preset (D-038): a conditioned program has a thermostat (heating and cooling setpoint schedules); an unconditioned program has no setpoints.
- Schedules have 8760 hourly values, either fractions or temperatures (ADR-003).
- Load types: Occupancy, Lighting, ElectricEquipment, GasEquipment, DomesticHotWater, Ventilation, Infiltration. Each load has one basis: PerFloorArea, PerPerson, Absolute, PerExteriorWallArea, or AirChangesPerHour (ADR-007). A program holds at most one load per type and basis, so a load type may have components in several bases, which add up; a zone's design occupants are the sum of its occupancy components (D-047). Magnitudes are people, W, or m³/h.
- `ExampleResidentialPresets` hold illustrative round numbers for development and tests, not DOE prototype values: dwelling unit and corridor conditioned, stair unconditioned.

### 2. Plan generation

| | |
| --- | --- |
| Type | `LinearPlanGenerator : PlanGenerator<LinearPlanParameters>` → `IGeneratedPlan` |
| Component | *Linear Plan Generator* |
| Decisions | D-009, D-015, D-026, D-039; ADR-002 |

- Linear block: a full-depth stair at the west end (`ST`), a double-loaded corridor (`CO`), and one row of equal dwelling units on each side (`US1…`, `UN1…`); one zone per dwelling unit (D-009). Lengths are metres.
- Surfaces come from `LayoutSurfaceBuilder`: an edge shared by two zones becomes an interzone wall, an edge on the plan boundary an outdoor wall; any other edge (a gap or an overlap) is an error. Floors and ceilings stay `Unresolved` until floors are aggregated.
- Walls carry explicit windows (position along the wall, sill, width, height; any number per wall, D-039). This generator's rule: one centered window per outdoor wall with area = the zone preset's WWR × wall area (D-026).

### 3. Plan simplification

| | |
| --- | --- |
| Type | `IPlanSimplifier.Simplify(IGeneratedPlan)` → `IFloor` (with `Source` and `Mapping`) |
| Components | *No Simplification* (Z0), *Semantic Merge* (Z1), *Perimeter Core* (Z2, input Depth, default 4.57 m), *Single Zone per Floor* (Z3); *Map Source to Target* lists the mapping |
| Decisions | D-019, D-034, D-038, D-039, D-041, D-047; ADR-005, ADR-007, [ADR-008](../decisions/ADR-008-perimeter-core-corners.md) |

- `NoSimplification` keeps the plan's zones and surfaces with an identity mapping.
- The other simplifiers share one procedure (`PlanSimplifier`). A strategy proposes target footprints; source zones are mapped to targets by overlap area (`ZoneMapping`); surfaces are rebuilt, so walls between merged sources disappear (D-034); the target outdoor walls must cover every source outdoor wall over its full length (D-041, error `FacadeNotCovered`); every source window is re-hosted unchanged on the target wall that contains it (D-039, `WindowRehosting`, error `WindowNotHosted`); programs are aggregated through the transfer fractions.
- Aggregation (ADR-005, ADR-007): each (load type, basis) component is aggregated on its own (D-047). Each source with the component transfers Tᵢ = fᵢ·Qᵢ of its design magnitude; the component's target magnitude is Q* = ΣTᵢ and its value Q*/B* in that component's basis; its schedule is s*(t) = ΣTᵢ·sᵢ(t)/Q*. Sources without the component contribute nothing to it, and mixed bases are not an error. Air-change loads are therefore volume weighted (D-019). A target is conditioned if any source contributing floor area is; its setpoints are floor-area weighted over the conditioned sources, a prescribed control rule (D-038).
- *Semantic Merge* merges connected zones of the same space type. *Perimeter Core* makes one perimeter zone per orientation plus a core, with corners split on the bisectors (ADR-008). *Single Zone per Floor* makes the floor one zone.

### 4. Floor aggregation

| | |
| --- | --- |
| Type | `IFloorAggregator.Aggregate(IReadOnlyList<FloorEntry>)` → `IGeneratedBuilding` |
| Components | *Stack Floors*, *Floor Area Multiplier*, *Single Zone Merged*; inputs Floors (bottom to top) and Multipliers (optional, one per floor, default 1) |
| Decisions | D-018, D-021, D-031, D-032, D-034, D-039, D-041, D-045, D-046; [ADR-009](../decisions/ADR-009-vertical-aggregation.md) |

All aggregators reject an empty list (`NoFloors`), multipliers below 1 (`InvalidParameter`), and floors with different orientations (`OrientationMismatch`). Floor types may have different footprints. `Stack` and `FloorAreaMultiplier` give zone and surface IDs the storey prefix `L{k}/`, where `k` is the storey's index in the fully stacked building.

| Aggregator | Storeys | Multiplier Nᵢ | Floors and ceilings | Walls and windows | Internal mass |
| --- | --- | --- | --- | --- | --- |
| `Stack` | every entry repeated Nᵢ times, all storeys explicit | explicit repetition | split by overlap with the storeys below and above: interzone between storeys, uncovered parts outdoors, lowest floors ground, highest ceilings roof | as in the floors | none |
| `FloorAreaMultiplier` | type `i` stands for Nᵢ storeys; storeys of a multiplied type with an exposed floor or ceiling are split off as × 1 storeys (info `FloorTypeSplit`, D-046); each remaining group of n storeys from storey `first` is one representative storey, storey `first + ⌊n/2⌋`, at its true elevation; the storeys between stay empty and the building keeps its true height (D-045) | `Zone.Multiplier = n` on every zone of the group; exposure is never multiplied; provenance parameter `Storeys`, e.g. `L0x1,L5x8,L9x1` | split by overlap with the representative storeys below and above: overlap adiabatic, uncovered parts outdoors (setback roofs, overhanging floors), lowest floors ground, highest ceilings roof (D-046) | as in the floors | none |
| `SingleZoneMerged` | `Stack` of the entries, then one zone `BUILDING` with one part per storey outline | explicit repetition | ground floors, roofs, and floors or ceilings exposed to outdoors kept; slabs between storeys are no longer surfaces | rebuilt per storey outline, all outdoors, covering every source façade (D-041); every window kept in place (D-039); partitions discarded (D-034) | one per slab level: slab area, 2 exposed faces (D-031) |

### 5. Validation

| | |
| --- | --- |
| Types | `FloorValidator`, `BuildingValidator` → `ValidationReport` (`Passed`, `Checks`, `Describe()`) |
| Component | *Validate* (a floor or a building) |
| Decisions | D-038, D-041, D-045, D-046; ADR-004; GLOBAL.md scientific rules 1 and 6 |

See [What is validated where](#what-is-validated-where) below; every check, its reference, and its tolerance are listed in [validation.md](validation.md).

### 6. Convert2BEM

| | |
| --- | --- |
| Type | Grasshopper component only (`Lod.Grasshopper`) |
| Component | *Convert2BEM* |
| Decisions | D-016, D-023, D-038, D-039; GLOBAL.md scientific rule 6 |

- Validates the building with `BuildingValidator` first. A failed enforced check blocks conversion (`ValidationFailed`) unless *Override* is true; then the component converts, warns (`ValidationOverridden`), and writes the override into its *Provenance* output.
- Outputs one data-tree branch per zone: zone Breps, names, space types, multipliers, the conditioned flag, loads (types, bases, values, schedules), heating and cooling setpoints (empty for unconditioned zones), surfaces with their boundaries, the explicit windows at their positions, and the exposed internal-mass area (slab area × exposed faces). The layout is neutral and provisional until a ClimateStudio reference definition exists (D-023); see [convert2bem.md](convert2bem.md).
- No simulation runs inside the pipeline (D-016).

## What is validated where

| Where | What | Effect of a failure |
| --- | --- | --- |
| Program types (schedules, loads, programs, presets) | Schedule length, values, and kind; load values and allowed bases; one load per type and basis (D-047); per-person loads need an occupancy load; setpoints are temperature schedules; WWR in [0, 1); one preset per space type | Error; no object |
| Plan generator | Parameters (`InvalidParameter`); a preset for every space type used (`MissingPreset`); zones tile the footprint (`OverlappingZones`, `UnmatchedEdge`); polygons (`DegeneratePolygon`) | Error; no plan |
| Property aggregation (plan simplifiers, `SingleZoneMerged`) | Fractions in [0, 1]; a positive load component needs a positive target basis quantity (`ZeroBasisQuantity`); valid measures; positive setpoint weights | Error; a zero load only gives the info `ZeroLoadSchedule` |
| Plan simplifiers | Strategy preconditions (`InvalidParameter`, `PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`); façade coverage (`FacadeNotCovered`); every window hosted by one target wall (`WindowNotHosted`) | Error; no floor |
| Floor aggregators | At least one floor (`NoFloors`); multipliers from 1 (`InvalidParameter`); one orientation (`OrientationMismatch`); façade coverage and window hosting (`FacadeNotCovered`, `WindowNotHosted`, `SingleZoneMerged`). `FloorAreaMultiplier` rejects no input for exposure: it splits exposed storeys of multiplied types off and reports the info `FloorTypeSplit` (D-046) | Error; no building (`FloorTypeSplit` is a remark; the building is produced) |
| `FloorValidator`: a floor against its source plan | Enforced: `FloorArea`, `Volume`, `ExteriorWallArea`, `Glazing`, `Glazing.<orientation>`, `Installed.<load type>`, `Scheduled.<load type>` (every hour), `FacadeCoverage`, `NoTargetOverlap`, `SourceCoverage`, `Traceability`. Reported: `ConditionedFloorArea` (D-038). Setpoints are a prescribed rule and are not compared | The report fails on enforced checks only; reported checks show as `note` when they differ |
| `BuildingValidator`: a building | `Floor{i}.*`: the floor checks for every distinct source floor. `Building.*`: the conservation checks against `Stack` of the same entries, counting zone multipliers, including `Building.GroundArea`, `Building.RoofArea`, and `Building.ExposedFloorArea` (enforced, D-046), `Building.Height` (enforced, D-045), and `Building.ConditionedFloorArea` (reported, D-038) | The report fails on enforced checks only |
| *Convert2BEM* | Runs `BuildingValidator` | Conversion blocked unless *Override*; the override is recorded |

Area and volume checks use the relative area tolerance, load checks the relative load tolerance (ADR-004).

## Grasshopper components through S4

All components are on the **BEMGen** tab. Component icons come in S9. GUIDs never change once merged.

| Panel | Component (nickname) | Inputs → outputs | Class | GUID | Since |
| --- | --- | --- | --- | --- | --- |
| 0 Info | *BEMGen Info* (Info) | — → Version | `BemGenInfoComponent` | `b1d4f0a2-6c3e-4f7a-8e21-5a9c0d7e3b14` | S0 |
| 1 Program | *Schedule* (Sch) | Name, Kind, Weekday, Weekend, First Day → Schedule | `ScheduleComponent` | `1be96980-e9eb-4636-9ce6-4e5b6a301d1f` | S2 |
| 1 Program | *Load* (Load) | Type, Basis, Value, Schedule → Load | `LoadComponent` | `c07304be-fe9c-4810-ba1d-1cac1710c386` | S2 |
| 1 Program | *Program Preset* (Preset) | Name, Space Type, Loads, Conditioned, Heating, Cooling, WWR → Preset | `ProgramPresetComponent` | `56ca1eba-abed-4dbb-a9a7-09d8b5806231` | S2 |
| 1 Program | *Example Residential Presets* (ExPresets) | — → Presets | `ExampleResidentialPresetsComponent` | `0239f4c9-0f19-4cf1-9d90-08db878eac8a` | S2 |
| 2 Generate | *Linear Plan Generator* (Linear) | Length, Unit Depth, Corridor Width, Unit Width, Stair Length, Floor Height, Orientation, Presets → Plan | `LinearPlanGeneratorComponent` | `a4a9131e-0a0f-49e0-99a4-f26760f6810f` | S2 |
| 3 Simplify | *No Simplification* (Z0) | Plan → Floor | `NoSimplificationComponent` | `83270abe-a13f-4f4c-a893-79739ad6e006` | S2 |
| 3 Simplify | *Semantic Merge* (Z1) | Plan → Floor | `SemanticMergeComponent` | `7d36f1d3-2708-4b69-b1a7-cf294c186e9a` | S3 |
| 3 Simplify | *Perimeter Core* (Z2) | Plan, Depth → Floor | `PerimeterCoreComponent` | `6a86b976-c838-427f-93a7-344dcc2c18ce` | S3 |
| 3 Simplify | *Single Zone per Floor* (Z3) | Plan → Floor | `SingleZonePerFloorComponent` | `4ff83222-5b7d-4d1b-8f26-fd580893a5db` | S3 |
| 4 Aggregate | *Stack Floors* (Stack) | Floors, Multipliers → Building | `StackFloorsComponent` | `6ce6524d-09b0-49fc-9b88-4c15bdcc8797` | S2 |
| 4 Aggregate | *Floor Area Multiplier* (Mult) | Floors, Multipliers → Building | `FloorAreaMultiplierComponent` | `e4b44821-c9ed-49b9-9c4e-7c08355254dd` | S4 |
| 4 Aggregate | *Single Zone Merged* (1Zone) | Floors, Multipliers → Building | `SingleZoneMergedComponent` | `506d5037-de93-4aee-a6c4-47dcc97509e1` | S4 |
| 5 Convert | *Convert2BEM* (2BEM) | Building, Override → Zones, Names, Space Types, Multipliers, Conditioned, Load Types, Load Bases, Load Values, Load Schedules, Heating Setpoints, Cooling Setpoints, Surfaces, Boundaries, Windows, Internal Mass, Provenance | `Convert2BemComponent` | `d091d70c-4de3-4f29-a900-ea4c9b777ba3` | S2 (validation gate S3) |
| 6 Inspect | *Inspect* (Inspect) | Object → Report, Provenance | `InspectComponent` | `1d56a553-7a66-451f-90e2-81e744b43bdd` | S2 |
| 6 Inspect | *Map Source to Target* (Map) | Floor → Source, Target, Overlap, Source Fraction, Target Fraction | `MapSourceToTargetComponent` | `eee37e01-28a2-4b5a-9c7d-7566cb9d93d4` | S3 |
| 6 Inspect | *Validate* (Validate) | Object → Passed, Report | `ValidateComponent` | `03558c0b-83e8-417d-b122-96ebde64c147` | S3 |

The Multipliers input of the three aggregators means: explicit repetition for *Stack Floors* and *Single Zone Merged* (the storeys are stacked before they are merged), the number of storeys each floor type stands for in *Floor Area Multiplier*, which models them as representative storeys with zone multipliers at their true elevations and splits storeys with an exposed floor or ceiling off as × 1 storeys, so exposure is never multiplied (D-045, D-046).

Parameters (hidden from the toolbar, registered in panel 0 Info, all since S2; they carry and preview the pipeline objects):

| Parameter (nickname) | Class | GUID |
| --- | --- | --- |
| Schedule (Sch) | `ScheduleParameter` | `a4ae84ac-36d6-41b8-9b3d-c77cca52a2df` |
| Load (L) | `LoadParameter` | `9e9fbc12-9b81-42b7-8c5d-a4f8397a4487` |
| Program Preset (P) | `ProgramPresetParameter` | `56578999-825c-4926-afdd-ce897b53221a` |
| Plan (Plan) | `PlanParameter` | `fca85387-7aaf-41fe-9654-382b2980f18f` |
| Floor (Floor) | `FloorParameter` | `15a085fa-f308-46b7-93e6-88a7a85e6a89` |
| Building (Bldg) | `BuildingParameter` | `d6726442-189d-4c44-b043-b56417a3826a` |

The plugin assembly (`BemGenAssemblyInfo`, name BEMGen) has the GUID `6f0f5d0e-2a8b-4c55-9a51-0a7b3d2c9e41`.

## Not in Checkpoint 1

| Item | Stage | Gate |
| --- | --- | --- |
| Window transformations W1–W5 (equivalent windows, WWR per façade, redistributed windows, orientation-level and building-level WWR), with glazing validation scoped by the declared W-level | S5 | ADR-012 |
| Convert2IDF: an EnergyPlus-ready IDF from `IGeneratedBuilding`, including constructions, unconditioned zones, and how zone multipliers and internal mass are written | S6 | ADR-010 |
| Precedent study (*Floor Plan Manual Housing*) and the plan generation mechanism | S7 | ADR-006 |
| Typologies: refined linear, point, and courtyard plans (footprints with holes included), minimum wall and window geometry | S8 | ADR-011 |
| Grasshopper UX (naming, input order, tooltips, icons), example definitions per typology, user guide, Yak package | S9 | — |

Also open: the ClimateStudio-specific form of the `Convert2BEM` output (D-023), sourced program preset values including conditioning (an open research input), and simulation, which stays outside the pipeline (D-016).

## Related documents

- [Validation](validation.md)
- [ADR-008 Perimeter/core corner rule](../decisions/ADR-008-perimeter-core-corners.md)
- [ADR-009 Vertical aggregation geometry](../decisions/ADR-009-vertical-aggregation.md)
- [Decision log](../decisions/decision-log.md)
- [Implementation roadmap](../plans/2026-09-30-implementation-roadmap.md)
- [Grasshopper smoke test](../development/grasshopper-smoke-test.md)
````

- [x] **Step 2: Check the linked files exist**

```bash
git ls-files docs/architecture/domain-model.md docs/architecture/convert2bem.md docs/architecture/validation.md docs/decisions/ADR-008-perimeter-core-corners.md docs/decisions/ADR-009-vertical-aggregation.md docs/decisions/decision-log.md docs/development/grasshopper-smoke-test.md docs/plans/2026-09-30-implementation-roadmap.md
```

Expected: all eight paths are listed (`domain-model.md` from S1, `convert2bem.md` from S2, `validation.md` and ADR-008 from S3). If one of them has another name in the repository, correct the link in `pipeline.md` to the actual file before committing.

- [x] **Step 3: Check the component table against the code**

```bash
git grep -n -E "ComponentGuid => new\(" src/Lod.Grasshopper
git grep -n -E "Add[A-Za-z]*Parameter\(\"Conditioned\"" src/Lod.Grasshopper
```

Expected: 23 lines for the first command (17 components, 6 parameters), each GUID appearing once in the tables of `pipeline.md`; 2 lines for the second (the *Program Preset* input and the *Convert2BEM* output named Conditioned, both listed in the component table).

- [x] **Step 4: Commit**

```bash
git add docs/architecture/pipeline.md
git commit -m "docs(repo): describe the complete checkpoint 1 pipeline"
```

### Task 7: S4 smoke-test checklist and the Checkpoint 1 example definition

**Files:**
- Modify: `docs/development/grasshopper-smoke-test.md` (append)
- Create (person, Rhino 8): `examples/grasshopper/checkpoint-1-pipeline.gh`

**Interfaces:**
- Consumes: the plugin built in Task 5; component names from `pipeline.md`.
- Produces: the manual evidence for the Checkpoint 1 exit criteria.

- [x] **Step 1: Append the S4 checklist at the end of `docs/development/grasshopper-smoke-test.md`**

Append this section after the last line of the file (after the S3 checklist), separated by one blank line, so that it nests under the guide's `## Stage checklists` section like the S2 and S3 checklists:

````markdown
### S4 checklist — floor aggregators (`v0.4.0`)

Floor aggregators and the complete Checkpoint 1 pipeline. Prerequisite: the plugin built from this stage is loaded in Rhino 8 as described above, and the S3 checklist passes. The canonical floors are: *Example Residential Presets* → *Linear Plan Generator* with its default inputs (24 m × 18 m, 3 m storeys) → each of *No Simplification*, *Semantic Merge*, *Perimeter Core* (Depth 4.57), and *Single Zone per Floor*. To give an aggregator the same floor three times, pass the floor through *Duplicate Data* (Sets › List) with Number = 3. Give Multipliers as a panel with the three lines `1`, `3`, `1`.

- [ ] The **BEMGen › 4 Aggregate** panel shows *Stack Floors* (Stack), *Floor Area Multiplier* (Mult), and *Single Zone Merged* (1Zone).
- [ ] **Floor Area Multiplier on each canonical floor** (Multipliers 1, 3, 1): no runtime message; the preview shows three storeys with the plan's windows on every storey, with floors at 0, 6, and 12 m and empty gaps at 3 and 9 m (the building is 15 m tall, D-045); *Inspect* lists zones `L0/…`, `L2/…`, and `L4/…` with `multiplier=3` on the `L2/` zones, `Ground` floors on `L0/`, `Outdoors` ceilings on `L4/` (z = 15), and `Adiabatic` for every other floor and ceiling; its Provenance output starts with `FloorAreaMultiplier Multipliers=1,3,1 Storeys=L0x1,L2x3,L4x1`.
- [ ] **True elevations (D-045):** *Floor Area Multiplier* with the *No Simplification* floor three times and Multipliers 1, 8, 1: no runtime message; the preview shows storeys at 0, 15, and 27 m; *Inspect* lists zones `L0/…`, `L5/…` (`multiplier=8`), and `L9/…`, the top storey's ceilings `Outdoors` at z = 30; *Validate* gives Passed = True with the line `ok   Building.Height: reference 30.000000, actual 30.000000`.
- [ ] **Exposed storeys are split off (D-046):** *Floor Area Multiplier* with one floor (*No Simplification*) and Multipliers = 10 shows the remark `Info FloorTypeSplit: Floor type 0 (x10) has an exposed floor and ceiling; split into x1 + x8 + x1 so exposure is not multiplied (D-046).` and outputs a building, not an error. *Inspect* lists zones `L0/…` (`multiplier=1`), `L5/…` (`multiplier=8`), and `L9/…` (`multiplier=1`) at 0, 15, and 27 m, and its Provenance output starts with `FloorAreaMultiplier Multipliers=10 Storeys=L0x1,L5x8,L9x1`. *Validate* gives Passed = True.
- [ ] **Setback (D-046):** a second *Linear Plan Generator* with Length = 14 (other inputs at their defaults) → *No Simplification* gives a narrow floor (stair and one unit per row). *Merge* (Sets › Tree) the canonical floor, the canonical floor again, and the narrow floor into the Floors of a *Floor Area Multiplier* with Multipliers 1, 4, 3. It shows two remarks, `Info FloorTypeSplit: Floor type 1 (x4) has an exposed ceiling; split into x3 + x1 so exposure is not multiplied (D-046).` and `Info FloorTypeSplit: Floor type 2 (x3) has an exposed ceiling; split into x2 + x1 so exposure is not multiplied (D-046).`; its Provenance output starts with `FloorAreaMultiplier Multipliers=1,4,3 Storeys=L0x1,L2x3,L4x1,L6x2,L7x1`; *Inspect* shows `Outdoors` ceilings on `L4/` at z = 15 over the eastern part that the narrow floor leaves uncovered (180 m² in total) and on `L7/` at z = 24. *Validate* gives Passed = True with `ok` lines for `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` (reference 24.000000).
- [ ] **Mismatched multipliers:** three floors with two multipliers give the error `Give one multiplier per floor (3), or none for all 1.` on each of the three aggregators.
- [ ] **Single Zone Merged on each canonical floor** (Multipliers 1, 3, 1): the preview shows one zone in the Mixed colour across all five storeys (0 to 15 m), with no interior partitions and, on every storey, the windows at the same positions as in the detailed plan. *Inspect* shows a single zone line starting `zone BUILDING Mixed "Building" area=2160.000000 volume=6480.000000 parts=5 multiplier=1`, a `setpoints heatingMean=21.000000 coolingMean=24.000000` line (the zone is conditioned), and four lines `mass BUILDING area=432.000000 faces=2` at z = 3, 6, 9, and 12.
- [ ] **Convert2BEM on a Single Zone Merged building** (Multipliers 1, 3, 1): *Internal Mass* has one branch {0} with the value 3456 (4 slabs × 432 m² × 2 faces), not zero; *Windows* {0} holds 50 Breps (10 per storey); *Conditioned* {0} is True. For *Stack Floors* and *Floor Area Multiplier* buildings every *Internal Mass* branch is 0.
- [ ] **Single Zone Merged on the No Simplification floor:** *Validate* gives Passed = True; the Report has `ok` lines for `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` and the line `note Building.ConditionedFloorArea: reference 1800.000000, actual 2160.000000` (the unconditioned stair becomes part of the conditioned zone, reported only, D-038).
- [ ] **All 12 combinations** (Multipliers 1, 3, 1): for every simplifier × aggregator pair, *Validate* gives Passed = True with a Report that starts with `PASSED` and has no `FAIL` line, and *Convert2BEM* with Override = False converts without an error. Expected `note` lines: `Floor0.ConditionedFloorArea: reference 360.000000, actual 432.000000` for every building made from the Perimeter Core or Single Zone per Floor floor, and `Building.ConditionedFloorArea: reference 1800.000000, actual 2160.000000` for Single Zone Merged with the No Simplification or Semantic Merge floor; no other `note` lines.

| Simplifier \ Aggregator | Stack Floors | Floor Area Multiplier | Single Zone Merged |
| --- | --- | --- | --- |
| No Simplification | [ ] | [ ] | [ ] |
| Semantic Merge | [ ] | [ ] | [ ] |
| Perimeter Core | [ ] | [ ] | [ ] |
| Single Zone per Floor | [ ] | [ ] | [ ] |

- [ ] `examples/grasshopper/checkpoint-1-pipeline.gh` opens in a fresh Rhino 8 session and solves without errors. It wires every simplifier into every aggregator, *Validate*, and *Convert2BEM*, and reproduces the 12 combinations above.
````

- [x] **Step 2: Commit the checklist**

```bash
git add docs/development/grasshopper-smoke-test.md
git commit -m "docs(grasshopper): add s4 smoke-test checklist"
```

- [x] **Step 3: Run the S4 checklist in Rhino 8 (person)**

Build (`dotnet build BEMGen.sln -c Release`), load the plugin as the smoke-test document describes, and tick every item of the S4 checklist. Agents cannot do this step. Any failure stops the stage: fix it on this branch with a test (core) or a build plus smoke test (Grasshopper) before continuing. Following the document's "Recording the result" section, write down who tested and when, the Rhino version and runtime (.NET Core), the SHA that was built (`git rev-parse HEAD`), the version text shown by *BEMGen Info* (it still starts with `0.3.0`; the bump to 0.4.0 comes in Task 8), and pass or fail for each checklist item. These values go into the body of the close-out commit (Task 8, Step 8).

- [ ] **Step 4: Build and save the example definition (person, Rhino 8)**

In a new Grasshopper document:

1. *Example Residential Presets* → Presets of *Linear Plan Generator* (all other inputs at their defaults).
2. Plan → *No Simplification*, *Semantic Merge*, *Perimeter Core* (Depth 4.57), and *Single Zone per Floor*.
3. For each of the four floors: *Duplicate Data* (Number = 3) → Floors of one *Stack Floors*, one *Floor Area Multiplier*, and one *Single Zone Merged*. One panel with the three lines `1`, `3`, `1` feeds every Multipliers input.
4. Each of the 12 buildings → its own *Validate* (with a panel on Report) and its own *Convert2BEM* (Override = False).
5. One *Inspect* on the *Single Zone Merged* building of the *No Simplification* row.
6. Group each simplifier's row and label the groups with the simplifier name; label the three aggregator columns.
7. No internalised Rhino geometry and no references to files outside the definition.
8. Save as `examples/grasshopper/checkpoint-1-pipeline.gh` (Rhino 8, binary `.gh`).

Before committing, close Rhino, start a fresh Rhino 8 session, open the file, and confirm: it solves without errors (the *Example Residential Presets* remark is expected); all 12 *Validate* outputs are True; no *Convert2BEM* shows an error; the *Single Zone Merged* buildings show Internal Mass 3456 and 50 windows, the others Internal Mass 0.

- [ ] **Step 5: Commit the example definition**

```bash
git add examples/grasshopper/checkpoint-1-pipeline.gh
git commit -m "docs(examples): add checkpoint 1 pipeline example definition"
```

`.gitattributes` already marks `*.gh` as binary.

- [x] **Step 6: Merge Slice C (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/grasshopper-aggregator-components
git push origin main
git branch -d feature/grasshopper-aggregator-components
```

Expected: `VERIFY PASSED`, with 104 core, 17 generators, and 63 integration tests passed on net8.0.

---

## Stage close-out

### Task 8: Version 0.4.0, Checkpoint 1 records, tag `v0.4.0`

**Files:**
- Modify: `Directory.Build.props`, `AGENTS.md`, `README.md`, `docs/plans/2026-09-30-implementation-roadmap.md`, `docs/decisions/decision-log.md`

**Interfaces:**
- Consumes: the merged Slices A–C; `BuildInfoTests.InformationalVersionStartsWithTheAssemblyVersion` (S0), which compares the informational version with the assembly version and therefore keeps passing after the bump.
- Produces: tag `v0.4.0`; the Checkpoint 1 records.

The decision-log entry in Step 7 has two fields that are filled in at execution time, when this task runs: `<date>`, the date on which Checkpoint 1 is confirmed (ISO format, `YYYY-MM-DD`), and `<name>`, the person who confirms it. They are not placeholders in this plan's instructions: neither can be known when the plan is written. The roadmap Progress line of Step 6 carries the same `<date>`. The smoke-test record in the commit body of Step 8 uses the values written down in Task 7, Step 3, in the form the S0 smoke-test document prescribes. The close-out uses its own branch, as the S1–S3 close-outs do.

- [x] **Step 1: Create the branch and run the gate**

```bash
git switch -c chore/repo-s4-close-out main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: `VERIFY PASSED`, with 104 core, 17 generators, and 63 integration tests passed on net8.0.

- [x] **Step 2: Bump the version in `Directory.Build.props`**

Replace

```xml
    <Version>0.3.0</Version>
```

with

```xml
    <Version>0.4.0</Version>
```

Full file after this step (identical to `stage-build\S4\Directory.Build.props` except the version):

```xml
<Project>
  <PropertyGroup>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <Deterministic>true</Deterministic>
    <Version>0.4.0</Version>
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
git commit -m "build(repo): set version 0.4.0"
```

- [x] **Step 5: Update `AGENTS.md` and `README.md`**

In `AGENTS.md`, replace everything between the heading `## Project state` and the heading `## Commands` (both headings stay) with:

```markdown

Checkpoint 1 (D-030) is reached: stages S0–S4 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.4.0`). The pipeline runs end to end for the linear plan: program presets → `LinearPlanGenerator` → plan simplifiers (`NoSimplification`, `SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`) → floor aggregators (`Stack`, `FloorAreaMultiplier`, `SingleZoneMerged`) → validation → `Convert2BEM`, as described in [docs/architecture/pipeline.md](docs/architecture/pipeline.md). Every zoning level keeps the generator's windows in place (W0, D-039); vertical aggregation follows [ADR-009](docs/decisions/ADR-009-vertical-aggregation.md).

Not implemented yet: window transformations W1–W5 (S5), `Lod.Export` and Convert2IDF (S6), the precedent study (S7), the refined linear, point, and courtyard typologies (S8), and Grasshopper UX and release (S9). The example program presets hold illustrative values, not DOE prototype values, and the `Convert2BEM` output layout stays provisional until a ClimateStudio reference definition exists (D-023).

```

In `README.md`, replace everything between the heading `## Status` and the heading `## What it does` (both headings stay) with:

```markdown

Checkpoint 1 reached: stages S0–S4 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.4.0`). In Rhino 8 the plugin runs the whole pipeline for a linear plan: program presets with conditioning, the linear plan generator with explicit windows, four plan simplifiers (Z0–Z3) that keep every window in place, three floor aggregators (Stack, FloorAreaMultiplier, SingleZoneMerged), invariant validation, and `Convert2BEM`. The pipeline is described in [docs/architecture/pipeline.md](docs/architecture/pipeline.md), and [examples/grasshopper/checkpoint-1-pipeline.gh](examples/grasshopper/checkpoint-1-pipeline.gh) wires every simplifier into every aggregator. Next: window transformations (S5), Convert2IDF (S6), and the precedent study (S7). The `Convert2BEM` output stays provisional until a ClimateStudio reference definition exists (D-023), and the example program presets hold illustrative values, not DOE prototype values.

```

- [x] **Step 6: Add the Progress line to the roadmap**

In `docs/plans/2026-09-30-implementation-roadmap.md`, the header blockquote holds one `> **Progress:**` line per closed stage (convention set by the S0 close-out). Insert these two lines directly below the S3 Progress line (the last `> **Progress:**` line), so that a `>` separator line stays between consecutive lines:

```markdown
>
> **Progress:** <date> · S4 Floor aggregators complete (tag `v0.4.0`); Checkpoint 1 reached (S0–S4 complete, D-044); next: S5, S6, and S7. `FloorAreaMultiplier` (representative storeys at their true elevations, exposed storeys split off as × 1, D-045, D-046) and `SingleZoneMerged` (windows in place, façade coverage checked, slabs as internal mass) follow ADR-009; every simplifier × aggregator combination of the linear plan validates and converts; 104 core, 17 generator, and 63 integration tests pass on `net8.0`.
```

`<date>` is the same date as in the decision-log entry of Step 7, and the decision number is the same as in Step 7.

- [x] **Step 7: Append the decision-log entry (template; fill `<date>` and `<name>` now)**

Append at the end of `docs/decisions/decision-log.md`, after a blank line. D-044 follows D-042 (S0, foundation ADRs) and D-043 (S3, ADR-008). If the log ends with another number, use the next free number, here and in the roadmap line of Step 6.

```markdown
### D-044 — Checkpoint 1 reached

- **Date:** <date> · **Decided by:** <name> · **Status:** Accepted
- Checkpoint 1 (D-030) is reached: stages S0–S4 are complete and tagged `v0.0.1`, `v0.1.0`, `v0.2.0`, `v0.3.0`, and `v0.4.0`.
- The pipeline runs for the linear plan from program presets through every plan simplifier (`NoSimplification`, `SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`) and every floor aggregator (`Stack`, `FloorAreaMultiplier`, `SingleZoneMerged`) to `Convert2BEM`, with every window kept in place (W0, D-039). All 12 combinations pass building validation in the test suite (`EverySimplifierAndAggregatorCombinationValidates`) and were validated and converted in Rhino 8 with `examples/grasshopper/checkpoint-1-pipeline.gh` (S4 smoke-test checklist).
- The pipeline is described in [docs/architecture/pipeline.md](../architecture/pipeline.md); vertical aggregation in [ADR-009](ADR-009-vertical-aggregation.md), with representative storeys at their true elevations (D-045) and exposure never multiplied (D-046). Loads are aggregated per load type and basis at every zoning level (D-047).
- S5 (window transformations, gated on ADR-012), S6 (Convert2IDF), and S7 (precedent study) can start (D-015, D-039, roadmap §1).
```

Before committing, check that no `<date>` or `<name>` is left:

```bash
git grep -n -F -e "<date>" -e "<name>" -- docs/decisions/decision-log.md docs/plans/2026-09-30-implementation-roadmap.md
```

Expected: no output.

- [x] **Step 8: Commit the records**

The second `-m` records the smoke test as `docs/development/grasshopper-smoke-test.md` prescribes ("Recording the result": the result goes into the body of the stage close-out commit), in the form the S0 close-out uses. Fill `<tester>`, `<date>`, `<version>`, `<sha>`, and `<version text>` with the values written down in Task 7, Step 3.

```bash
git add AGENTS.md README.md docs/plans/2026-09-30-implementation-roadmap.md docs/decisions/decision-log.md
git commit -m "docs(repo): record s4 completion and checkpoint 1" -m "Smoke test (docs/development/grasshopper-smoke-test.md, S4 checklist) by <tester> on <date>: Rhino <version>, .NET Core runtime, build <sha>, Version output '<version text>', all items passed, including all 12 simplifier x aggregator combinations and examples/grasshopper/checkpoint-1-pipeline.gh."
```

- [ ] **Step 9: Merge (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only chore/repo-s4-close-out
git push origin main
git branch -d chore/repo-s4-close-out
```

Expected: `VERIFY PASSED`, with 104 core, 17 generators, and 63 integration tests passed on net8.0.

- [ ] **Step 10: Tag**

```bash
git tag -a v0.4.0 -m "S4 Floor aggregators complete"
git push origin v0.4.0
```

## Exit criteria (copied from the roadmap, refined)

- ADR-009 was accepted and merged before any S4 code (Slice A gate).
- Every simplifier × aggregator combination for the linear plan validates: `EverySimplifierAndAggregatorCombinationValidates` passes its 12 cases (NoSimplification, SemanticMerge, PerimeterCore, SingleZonePerFloor × Stack, FloorAreaMultiplier, SingleZoneMerged; entries 1 / 3 / 1) on net8.0.
- Every combination converts: in Rhino 8, *Convert2BEM* converts all 12 buildings with Override = False (S4 smoke-test checklist).
- Each aggregator conserves, against the fully stacked reference and counting zone multipliers: floor area, volume, exterior wall area, glazing (total and per orientation), installed magnitude and hourly scheduled magnitude per load type (occupancy included, summed over the bases, D-047), and ground area, roof area, exposed floor area, and building height (enforced, D-045, D-046). The change in conditioned floor area is reported (D-038).
- `FloorAreaMultiplier` places representative storeys at their true elevations (`RepresentativeStoreysKeepTheirTrueElevations`, D-045), splits exposed storeys of multiplied types off as × 1 storeys (`ExposedStoreysOfMultipliedTypesAreSplitOff`, D-046), and keeps setbacks and overhangs exposed without multiplying them (`VaryingFootprintsKeepExposedAreasWithoutMultiplyingThem`, D-046). `SingleZoneMerged` keeps every window in place (D-039), checks façade coverage (D-041), turns slabs into internal mass (D-031), and discards partitions (D-034).
- Snapshots `aggregator-FloorAreaMultiplier.txt` and `aggregator-SingleZoneMerged.txt` are committed.
- `docs/architecture/pipeline.md` describes the complete pipeline.
- `examples/grasshopper/checkpoint-1-pipeline.gh` is saved by a person and committed.
- `scripts/verify.ps1` prints `VERIFY PASSED`; tests: 104 core, 17 generators, 63 integration on `net8.0`.
- Version 0.4.0, tag `v0.4.0`; AGENTS.md, README, the roadmap Progress line, the "Checkpoint 1 reached" decision-log entry (D-044), and the smoke-test record in the close-out commit are written.

## Notes for the reviewer

1. **Slices and branches.** Slices A–C match roadmap v3 §4 S4 (`docs/decisions-vertical-aggregation`, `feature/aggregators`, `feature/grasshopper-aggregator-components`). The close-out runs on `chore/repo-s4-close-out`, a branch the roadmap does not name, following the S1–S3 plans.
2. **Two earlier code files change; no validation code.** S4 modifies `src/Lod.Core/Buildings/Storeys.cs` (S2: `PlaceAt` and `ResolveRepresentative` added, `Place` and `ResolveStacked` unchanged in behaviour, confirmed by the S2 `Stack` tests and snapshot in Task 2, Step 8) and `src/Lod.Core/Common/DiagnosticCodes.cs` (S1: `FloorTypeSplit` appended). Both are shown in full in Task 2, and the appended constant also on its own, as the S3 plan does for its codes. Building validation with enforced ground area, roof area, exposed floor area, and height (D-045, D-046), reported conditioned floor area (D-038), façade coverage (D-041), the *Validate* component's building input, and the *Convert2BEM* gate all exist since S3. `SingleZoneMerged` uses the S3 codes `FacadeNotCovered` and `WindowNotHosted`.
3. **The matrix test has no red phase.** `EverySimplifierAndAggregatorCombinationValidates` covers code from S2, S3, and Tasks 2–3, so it passes on its first run (Task 4, Step 2). The plan says so instead of inventing a failure.
4. **`SingleZoneMerged` failure paths are not exercised.** No S4 test triggers `FacadeNotCovered` or `WindowNotHosted` in `SingleZoneMerged`; with tiled floors the rebuilt walls are the storey outline's straight runs, which always contain the source walls and their windows. Both paths reuse `FacadeAttribution.CoverageGaps` and `WindowRehosting`, which the S3 tests cover.
5. **`FloorAreaMultiplier` with floor types of different footprints** is supported (D-046) and tested with a setback and an overhang of the linear plan (`VaryingFootprintsKeepExposedAreasWithoutMultiplyingThem`). Exposure is decided per floor type against its neighbouring types, not per zone: `IsExposed` compares the uncovered area of the type's zone footprints with zero through `ToleranceSettings.AreaEquals`, whose scale is at least 1, so an uncovered area up to `RelativeArea` × 1 m² counts as covered. A type whose footprint is only partly uncovered is split off as a whole storey; the covered part of that storey then stands for one storey only, which is exact but models more storeys than a per-zone split would.
6. **Exact floating-point equality for elevations in `SingleZoneMerged`.** Storeys are grouped by `z.Parts[0].Elevation`, slab levels by `h.Elevation`, and ceiling pieces matched with `c.Elevation == level.Key`, not through `ToleranceSettings`. It works because `Storeys.Place` computes each storey's elevation and the ceiling elevation below it with the same arithmetic. It would become fragile if elevations were ever computed differently (AGENTS.md rule 14). Kept verbatim.
7. **D-031 says the slab construction is kept, but the model has no constructions yet.** `InternalMass` carries area, exposed faces, elevation, and source surfaces only. ADR-009 states that the construction is assigned once ADR-010 decides where constructions come from (S6).
8. **`InternalMass.SourceSurfaces` points to IDs of the stacked reference** (`L{i}/…/F{n}`, `L{i}/…/C{n}`), which are not surfaces of the `SingleZoneMerged` building. They can be traced by rebuilding `Stack` from `IGeneratedBuilding.Sources`, as `BuildingValidator` does.
9. **Internal mass and zone multipliers downstream are unknown.** ADR-009 defers both to S6 (ADR-010) and D-023 and claims no EnergyPlus or ClimateStudio behaviour. The roadmap gate asks whether ClimateStudio can represent the chosen slab option; ADR-009 answers that this cannot be checked until a reference definition exists.
10. **Component texts.** The *Floor Area Multiplier* description cites D-032, D-045, and D-046, and its Multipliers tooltip (`MultiplierDescription`) reads "How many storeys each floor type stands for. Default 1." (both copied verbatim). The split itself shows at runtime as the `FloorTypeSplit` remark.
11. **Execution-time values.** The decision-log entry D-044 "Checkpoint 1 reached" uses `<date>` and `<name>`, filled when Task 8 runs, as requested; the roadmap Progress line reuses the same `<date>`. The close-out commit body records the smoke test (`<tester>`, `<date>`, `<version>`, `<sha>`, `<version text>`) because the S0 smoke-test document prescribes it ("Recording the result"); the wording mirrors the S0 close-out commit. ADR-009 carries `Date: 2026-10-01` as the brief prescribes.
12. **Decision numbers.** S0 adds D-042, S3 adds D-043 (ADR-008), and the Checkpoint 1 entry is D-044. Step 7 says how to renumber if the log ends elsewhere; the roadmap Progress line must use the same number.
13. **Conventions shared with the S0–S3 plans.** The roadmap gets one `> **Progress:**` line per stage in the header blockquote, directly below the previous stage's line (set by S0). The S4 checklist is `### S4 checklist — floor aggregators (`v0.4.0`)`, a level-3 section nested under the guide's `## Stage checklists`, because the current S2 and S3 plans use that level (resolved in their review); an earlier review note asked for level 2, which no longer matches them. AGENTS.md "Project state" and README "Status" are replaced between fixed headings, as in S1–S3. Links in `pipeline.md` assume the file names in those plans (`domain-model.md`, `convert2bem.md`, `validation.md`, `ADR-008-perimeter-core-corners.md`); Task 6, Step 2 checks them.
14. **Test helper limit.** `FloorAreaMultiplierCarriesMultipliersAndOrderedBoundaries` groups zones by the first two characters of their ID (`L0`, `L5`, `L9`), which only works while every storey index is below 10; with types 1 / 8 / 1 the top storey is `L9`. Fine for this test; kept verbatim.
15. **Every intermediate state was built and run** on a copy of the regenerated S3 code (104 core, 17 generators, 38 integration on `net8.0`). The Task 2, Task 3, and Task 4 (Step 1) versions of `AggregatorTests.cs` were replayed from the plan's own code blocks, with the Task 2 code files applied in the plan's order (tests, `Storeys.cs`, `DiagnosticCodes.cs`, `FloorAreaMultiplier.cs`): the red errors (including line and column numbers), the core result after Task 2, Step 6 (build with 0 warnings, 104 core tests), the pass counts (`AggregatorTests` 8, 11, 23, 25; integration 46, 49, 61, 63), the snapshot failure messages, and the received snapshots (byte-identical to the expected files) are observed results. The end state is identical to the verified S4 code: 104 core, 17 generators, 63 integration on net8.0, 0 warnings. The values in the S4 smoke-test checklist (remark and error texts, `Storeys` provenance, storey elevations, `note` and `ok` lines, Inspect lines, internal mass 3456, 50 windows, `PASSED` for all 12 combinations and the 1 / 8 / 1, × 10, and setback buildings) were computed by running the core code; their appearance in Rhino was not checked.
16. **`net48` dropped (D-053).** BEMGen dropped the `net48` target after S0 (ADR-001, D-053): the plugin targets `net7.0` only and the tests `net8.0` only. Test counts are unchanged and the code is unchanged; only the expected outputs, which no longer list `net48`, changed. The `Directory.Build.props` comment in Task 8 follows the S0 file.
