# BEMGen Implementation Roadmap

> **Status:** Approved (D-030) · **Date:** 2026-09-30 · **Owner:** Cheng Xuan Li
>
> **Checkpoint 1:** completion of S0–S4 (D-030).
>
> **Progress:** 2026-10-01 · S0 Foundation complete (tag `v0.0.1`); next: S1. ADR-001 and ADR-004 ratify the tech stack and tolerances listed in this roadmap: C# 12 rather than the latest language version, no System.Collections.Immutable, minimum Rhino 8.19, relative area tolerance 1e-6, and the verify gate on Windows PowerShell 5.1 (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`).
>
> **Progress:** 2026-10-01 · S1 Program presets and equivalence engine complete (tag `v0.1.0`); next: S2. The example presets are illustrative (stair unconditioned), not DOE values; sourced presets remain open point 4 of §7.
>
> **Progress:** 2026-10-01 · S2 End-to-end pipeline skeleton complete (tag `v0.2.0`); next: S3. Presets → `LinearPlanGenerator` → `NoSimplification` → `Stack` → neutral *Convert2BEM* (D-023) runs in Grasshopper with previews; explicit windows (one centered window per outdoor wall from the generator, D-039, D-026) and preset conditioning (stair unconditioned, D-038) appear in every report and preview; 94 core, 17 generator, and 9 integration tests pass on net8.0. *Convert2BEM* has no validation gate until S3.
>
> **Progress:** 2026-10-01 · S3 Plan simplifiers and validation complete (tag `v0.3.0`); next: S4. Plan simplifiers Z1 semantic merge, Z2 perimeter/core (corner rule in ADR-008), and Z3 single zone per floor keep every window in place (D-039) and require full façade coverage (D-041); floor and building validation, with conditioned floor area reported (D-038) and ground, roof, and exposed floor area and building height enforced (D-045, D-046); the *Convert2BEM* validation gate with a recorded override; 104 core, 17 generator, and 38 integration tests pass on net8.0.
>
> **Progress:** 2026-10-01 · S4 Floor aggregators complete (tag `v0.4.0`); Checkpoint 1 reached (S0–S4 complete, D-044); next: S5, S6, and S7. `FloorAreaMultiplier` (representative storeys at their true elevations, exposed storeys split off as × 1, D-045, D-046) and `SingleZoneMerged` (windows in place, façade coverage checked, slabs as internal mass) follow ADR-009; every simplifier × aggregator combination of the linear plan validates and converts; 104 core, 17 generator, and 63 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-01 · S4.1 Grasshopper inputs, presets, and icons complete (tag `v0.4.1`); next: S5, S6, and S7. The *Linear Plan Generator* takes one preset per space type (*Dwelling Unit*, *Corridor*, *Stair*; `LinearPlanPresets`, mismatches are `PresetSpaceTypeMismatch`) from the new default preset components, which replace *Example Residential Presets* (D-061); generator, simplifier, and aggregator components have a *Preview Location* input (D-062); every component and parameter has an icon drawn by `scripts/make_icons.py` (D-063); all seven snapshots unchanged; 120 core, 19 generator, and 63 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-01 · S4.2 Vertical aggregation methods, plan transform, and heat-transfer options complete (tag `v0.4.2`, local until the owner pushes it, D-075); next: S5, S6, and S7. Every floor aggregator designates floors and ceilings on the assembled stack (D-068) and warns about unsupported storeys (D-074); the aggregators are `Stack`, `StackedFloorZoneMultiplier` (formerly `FloorAreaMultiplier`), `SingleZonePerFloorType` (one zone per floor entry, behind the former *Single Zone Merged* component), and `SingleZoneBuilding` (formerly `SingleZoneMerged`, D-071), following ADR-013; *Transform Plan* rotates and moves a plan, and every simplifier and aggregator validates on rotated plans (D-070, D-076); *Convert2BEM* writes heat transfer between zones only when asked (D-069); existing buildings unchanged, two snapshots renamed with identical content; 136 core, 19 generator, and 163 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S5 Centred windows on rebuilt walls complete (tag `v0.5.0`; `main`, `v0.4.2`, and `v0.5.0` are pushed after the fresh-clone gate, D-080); next: S6 and S7. `CentredWindows` gives every outdoor wall rebuilt by *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* one window centred by the generator's rule with the glazed area of the source windows it covers (D-079, ADR-012); glazing per wall, façade, orientation, and building and every validation report unchanged; new error `GlazingExceedsWall`; six snapshots changed in their window entries only; 142 core, 19 generator, and 187 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.1 Plan generation mechanism and bar typologies complete (tag `v0.8.0`, local until the owner pushes it, D-084); next: S6 and S8.2. ADR-006 fixes one `PlanGenerator` subclass per *High-Density Housing* family, with typed parameter and preset records and design defaults for all nine families; ADR-011 adds `GeometryLimits` (no window on an outdoor wall shorter than 1 m or for a window narrower or lower than 0.3 m, info `WindowOmitted`); `LinearPlanGenerator` checked as `HDHM-TYP-009` and kept; new generators and components *Stair Bay Bar* (001), *Stair Pair* (008), *Gallery Bar* (002, gallery not modelled), and *Terrace Row* (006, one zone per plot and storey, D-085); every bar family validates with every simplifier and aggregator, also rotated and moved; existing snapshots byte-identical, four new; 152 core, 91 generator, and 319 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.2 Non-rectangular typologies without holes complete (tag `v0.8.1`, local until the owner pushes it, D-084); next: S6 and S8.3. New generators and components *Point Plate* (007, a square plate whose core has no outdoor wall), *Winged Band* (003, a comb), and *Open Court* (004, a U), their wings on the shared stair-bay layout; *Semantic Merge* unites its groups as tiles, the surface builder tests vertices on edges at their original positions, and unions of tiles keep the tiles' own vertices, which repairs rotated plans released up to `v0.8.0` (D-088); *Perimeter Core* states its width precondition in `PlanTooNarrow` (D-087); every non-rectangular family validates with every simplifier and aggregator, also rotated and moved; existing snapshots byte-identical, three new; 154 core, 159 generator, and 474 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.3 Enclosed courtyard and footprints with holes complete (tag `v0.8.2`, local until the owner pushes it, D-084); next: S6 and S9. New generator and component *Enclosed Court* (005, four wings of stair bays around a court closed on all four sides), the first footprint with a hole; the surface builder requires every footprint edge, court edges included, to be covered by outdoor zone edges; *Perimeter Core* zones the court façades in their own zones `P-Court-<Bin>` around a ring core, with its width precondition on every wing (D-087); *No Simplification*, *Semantic Merge*, *Single Zone per Floor*, the four floor aggregators, and validation needed no change; every simplifier and aggregator validates the enclosed court, also rotated and moved; zone solids are outward-oriented and surfaces and windows face out of their zones in *Convert2BEM*, which repairs every plan released up to `v0.8.1` (D-091); existing snapshots byte-identical, one new; 158 core, 181 generator, and 601 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.4 Non-residential programs, office plate and cafeteria complete (tag `v0.8.3`; `main` and the tag pushed after the fresh-clone gate, D-098); next: S8.5. The four-source records are pinned (`v0.3.1-research`, `7538ed3`) and paraphrased in `syn-typologies.md`, and BEMGen documents use the `SYN-TYP-*` IDs (D-099); the study covers every program type (D-094) in the brief, spec, README, AGENTS.md, and roadmap; ADR-014 adds twelve non-residential space types (`Core`, `Lobby`, and `Service` reused), fifteen illustrative presets in `ExampleNonResidentialPresets`, their default preset components, and the department zoning of every new family (D-097); ADR-006 specifies all nine new families, the hub-and-arms families with at most four arms (D-100); new generators and components *Office Plate* (017, the first zone with a hole in a footprint without one, needing no pipeline change) and *Cafeteria* (016); existing snapshots byte-identical, two new; 193 core, 224 generator, and 704 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.5 Branching plans on a shared hub-and-arms layout complete (tag `v0.8.4`; `main` and the tag pushed after the fresh-clone gate, D-098); next: S8.6. `HubArmsLayout` lays out a square hub with up to four arms (D-100, D-102) for four new generators and components: *Radial Lobes* (010), *Branching Mall* (014, one mall zone through every branch), *Care Hub* (018), and *Foyer Halls* (019); *Perimeter Core* keeps the footprint's own vertices, which repairs short façades on rotated plans (ADR-008); existing snapshots byte-identical, four new; 193 core, 360 generator, and 1184 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.6 Operating suite and court clusters complete (tag `v0.8.5`; `main` and the tag pushed after the fresh-clone gate, D-098); next: S8.7. Two new generators and components: *Operating Suite* (015, theatre banks between alternating clean and dirty corridors beside the support rooms) and *Court Cluster* (011, stair-bay wings around a row of courts, the first footprint with several holes, which every step already handles; D-104); existing snapshots byte-identical, two new; 193 core, 427 generator, and 1385 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.7 Plans per storey and the stepped band complete (tag `v0.8.6`; `main` and the tag pushed after the fresh-clone gate, D-098); S8 is complete with 18 plan generators; next: S6. ADR-015 decides plans per storey (D-095, D-106): a `MultiStoreyPlanGenerator` returns one plan per storey, bottom-up, sharing every rule of `PlanGenerator`, and every simplifier and floor aggregator takes the storeys unchanged, the terraces designated on the assembled stack (D-068); new generator and component *Stepped Band* (012, a dwelling band stepping back storey by storey, with a *Plan* list); existing snapshots byte-identical, one new; 210 core, 463 generator, and 1485 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S8.8 Storey previews, the any-program preset, and the preset panel complete (tag `v0.8.7`; pushing waits for the owner, D-108); next: S6. Floors of a storey plan previewed at the storey's height (`StoreyElevation`, ADR-015), the *Any Program Preset* parameter (`24bc6a12-ad06-4c25-bc9d-4e8318b8744c`) accepted on every preset input (ADR-014), and the panel *1 Program Presets* (D-109); no GUID changed; existing snapshots byte-identical; 243 core, 518 generator, and 1518 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · S6 Convert2IDF complete (version 0.9.0, D-113; tagging and pushing wait for the owner); next: S9. An envelope preset shared by *Convert2BEM* and *Convert2IDF*, `Lod.Export` with the IDF writer (EnergyPlus 25.2, ADR-010), the *Envelope Preset* and *Convert2IDF* components, `scripts/rhino-smoke/` and `scripts/idd-check/`; every converted IDF of the tests and of the Rhino run passes the IDD check; existing snapshots and icons byte-identical; 294 core, 518 generator, 475 export, and 1518 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-02 · Process (D-111): from S6 on, stages are planned in a short design note, built once test-first on feature branches (independent parts in parallel), reviewed by a second agent, checked headless in Rhino from `scripts/rhino-smoke/`, and recorded in one decision-log entry; the execution handoff, its `.handoff/` archive and tools, and the reference-and-replay method are retired.
>
> **Progress:** 2026-10-03 · Zero-width artefacts fixed (D-114; no version change, the controller decides on a tag); next: S9. Floors and ceilings between storeys are clipped from conformed footprints (`PolygonOps.Conform`, ADR-002), so rotated and moved plans carry no slivers, spikes, or excursions (a sweep of 14,400 buildings: 1,249 with artefacts before, none after); *Convert2IDF*'s sliver handling stays as a guard; rotated setback stacks are no longer split by rounding slivers under *Stacked Floor Zone Multiplier*; snapshots unchanged; 346 core, 518 generator, 635 export, and 1573 integration tests pass on `net8.0`.
>
> **Progress:** 2026-10-03 · S9 Release complete (version 1.0.0, D-116; the tag `v1.0.0` is set at the fresh-clone gate and pushing waits for the owner). A local MkDocs docs site (user part and developer part, served on localhost, never published), the component reference generated from the plugin's metadata with icons and screenshots, 19 example definitions built by the headless harness (one per plan generator and the end-to-end example), the `sync-docs` project skill, a local Yak build (`scripts/package-yak.ps1`), and the MIT license. The headless check found a Grasshopper freeze: BEMGen's Goo types lacked a public parameterless constructor, so a wire of the wrong type, the "Data conversion failed" message, or component help opened Grasshopper's modal assert dialog in every version up to `v0.9.1`; fixed, and the smoke check now asserts expected errors. `scripts/verify.ps1` and `mkdocs build --strict` pass; all 12 rhino-smoke specs pass and all 19 examples reopen and solve; 346 core, 518 generator, 635 export, and 1573 integration tests pass on `net8.0`. Open for a person: the examples on screen, the Yak install, the toolbar icons, and a first EnergyPlus run (D-112). Next: the first EnergyPlus run and sourced presets (D-112, D-023).
>
> **Revisions:** v1 (2026-09-30) initial draft · v2 (2026-09-30) pipeline-first restructure after D-015 to D-024: Grasshopper objects instead of JSON, the D-018 pipeline vocabulary, ClimateStudio output without simulation, precedent study moved after the pipeline works · v3 (2026-10-01) plan review: conditioning from presets (D-038), explicit windows and a separate window-transformation stage S5 with later stages renumbered (D-039), multiplier without multiplied ground or roof (D-040), enforced façade coverage (D-041); facts established while writing the S0–S4 plans · v4 (2026-10-01) plan review: representative storeys at their true elevations (D-045), exposed storeys of multiplied floor types split off automatically so floor types may differ in footprint (D-046, supersedes D-040), loads aggregated per load type and basis (D-047) · v5 (2026-10-01) Checkpoint 1 review: revision stage S4.1 before S5 (D-061 to D-064) · v6 (2026-10-01) S4.1 review: revision stage S4.2 before S5 (D-068 to D-077) · v7 (2026-10-01) windows of merged zones: one centred window per rebuilt wall with the wall's glazed area, window levels W1–W5 dropped, S5 renamed "Centred windows on rebuilt walls" (D-079, ADR-012) · v8 (2026-10-02) precedent source *High-Density Housing*, studied in a separate repository, replaces the S7 research (D-082); one plan generator per typology family (D-083); S8 split into S8.1–S8.3 (D-084) · v9 (2026-10-02) four-source precedent set `SYN-TYP-001`–`019` (D-093), non-residential programs in scope (D-094), plans per storey (D-095), `013` set aside (D-096), department zoning (D-097), sub-stages S8.4–S8.7 before S6 (D-098).
>
> **For agentic workers:** this is a stage-level roadmap, not an executable task list. Before starting a stage, write its detailed test-first plan as `docs/plans/YYYY-MM-DD-sN-<stage-name>.md` (bite-sized tasks, exact files, test code, commands), using superpowers:writing-plans, then execute it with superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** A Rhino 8 Grasshopper plugin that generates detailed plans of residential and non-residential building typologies (D-094) from program presets, simplifies them into lower-LoD buildings that satisfy prescribed conservation invariants, checks those invariants numerically, and outputs Grasshopper objects ready for visualization and for a ClimateStudio definition.

**Architecture:** All logic lives in plain C# libraries (`Lod.Core`, `Lod.Generators`, later `Lod.Export`) and is tested with `dotnet test` without Rhino. `Lod.Grasshopper` wraps the pipeline types in Goo, exposes one component per pipeline step, previews every object, and hosts `Convert2BEM`. The pipeline (D-018):

```text
program presets (x, y, ...)
  → PlanGenerator (LinearPlanGenerator, ...)        → IGeneratedPlan      Z0: one zone per dwelling unit or department, explicit windows
  → PlanTransform (optional, D-070)                 → IGeneratedPlan      rotation about z, translation in x and y
  → IPlanSimplifier                                  → IFloor              one centred window per rebuilt wall (D-079)
       NoSimplification | SemanticMerge | PerimeterCore | SingleZonePerFloor
  → IFloorAggregator (IFloor[])                      → IGeneratedBuilding
       Stack | StackedFloorZoneMultiplier | SingleZonePerFloorType | SingleZoneBuilding (whole building = 1 zone)
  → Convert2BEM                                      → ClimateStudio-ready Grasshopper inputs
  → Convert2IDF (S6)                                 → EnergyPlus-ready IDF
```

**Tech stack (ratified in ADR-001 during S0):** C# 12, .NET SDK ≥ 8, `netstandard2.0` core libraries, Rhino 8 RhinoCommon + Grasshopper NuGet packages ≥ 8.19 (plugin targets `net7.0` only, one `BEMGen.gha` for Rhino 8's default .NET Core runtime; D-053), Clipper2 for polygon operations, xUnit on `net8.0` only. No System.Collections.Immutable (Rhino 8 ships a conflicting copy).

## Global constraints

- Rhino 8 (8.19 or later) only (D-003). BEMGen is a Grasshopper plugin; stages exchange Grasshopper objects, not JSON (D-017).
- `Lod.Core`, `Lod.Generators`, `Lod.Export` have no RhinoCommon/Grasshopper reference; their tests run without Rhino.
- Nullable reference types enabled; warnings as errors in all projects.
- Generation is deterministic; randomness only via an explicit seed stored in metadata.
- Numerical tolerances live only in `ToleranceSettings`.
- Z0 has at most one zone per dwelling unit and storey; rooms are never modelled (D-009, D-085). A non-residential floor has one zone per department, a contiguous group of rooms of one program (D-097, ADR-014).
- Walls carry explicit windows (position, sill, width, height; any number per wall). The first generator places one centered window per outdoor wall sized from the preset's WWR (D-026); wherever zones are merged and walls rebuilt, every outdoor wall carries one centred window, shaped by the same rule, with the glazed area of the source windows it covers, so glazing is conserved per wall, façade, orientation, and building; steps that do not rebuild walls keep their input's windows (D-079, ADR-012). There are no window levels W1–W5.
- Conditioning comes from the program preset; unconditioned zones have no setpoints. A simplified zone is conditioned if any source contributing floor area is; its setpoints are floor-area weighted over the conditioned sources, a prescribed control rule, not a conservation invariant (D-038).
- Air-change-based loads are volume weighted (D-019).
- Façade coverage is enforced: target façades must cover every source façade over its full length (D-041).
- Floor multipliers never multiply exposure: storeys with exposed floors or ceilings (ground, roof, setbacks, overhangs) are split off as ×1 storeys automatically, so floor types may differ in footprint; representative storeys sit at their true elevations (D-045, D-046).
- A program may express a load type in several bases (e.g. ventilation per person plus per area); each (type, basis) component is aggregated and conserved on its own (D-047).
- Validation failures block conversion unless an override is explicitly recorded.
- No simulation inside the pipeline (D-016). No CI/CD (D-005); `scripts/verify.ps1` must pass locally before merging to `main`.
- Commits: `type(scope): summary`, no tool attribution (D-001, D-002). Chat decisions go to `docs/decisions/decision-log.md` (D-007).

---

## 1. Stage overview

| Stage | Name | Depends on | Tag |
| --- | --- | --- | --- |
| S0 | Foundation | — | `v0.0.1` |
| S1 | Program presets and equivalence engine | S0 | `v0.1.0` |
| S2 | End-to-end pipeline skeleton | S1 | `v0.2.0` |
| S3 | Plan simplifiers and validation | S2 | `v0.3.0` |
| S4 | Floor aggregators | S3 | `v0.4.0` |
| S4.1 | Grasshopper inputs, presets, and icons (revision, D-064) | S4 | `v0.4.1` |
| S4.2 | Vertical aggregation methods, plan transform, and heat-transfer options (revision, D-073) | S4.1 | `v0.4.2` |
| S5 | Centred windows on rebuilt walls | S4.2 | `v0.5.0` |
| S6 | Convert2IDF | S8.8 (D-098, D-108) | `v0.9.0` |
| S7 | Precedent study — replaced by the external study of D-082 | — | — |
| S8.1 | Plan generation mechanism and bar typologies (ADR-006, ADR-011; families 009 check, 001, 008, 002, 006) | S5 | `v0.8.0` |
| S8.2 | Non-rectangular typologies without holes (families 007, 003, 004) | S8.1 | `v0.8.1` |
| S8.3 | Enclosed courtyard (family 005), footprints with holes in every simplifier and aggregator | S8.2 | `v0.8.2` |
| S8.4 | Non-residential programs, office plate and cafeteria (pinned four-source records, scope alignment, ADR-014; families 017, 016) | S8.3 | `v0.8.3` |
| S8.5 | Branching plans on a shared hub-and-arms layout (families 010, 014, 018, 019) | S8.4 | `v0.8.4` |
| S8.6 | Operating suite and linked court clusters (families 015, 011) | S8.5 | `v0.8.5` |
| S8.7 | Plans that differ by storey (D-095, with an ADR) and stepped bands with terraces (family 012) | S8.6 | `v0.8.6` |
| S8.8 | Storey previews, any-program preset, and the preset panel (revision stage, D-108) | S8.7 | `v0.8.7` |
| S9 | Release: docs site, examples, Yak package (D-115) | S6, S8.8 | `v1.0.0` |

```text
S0 ── S1 ── S2 ── S3 ── S4 ── S4.1 ── S4.2 ── S5 Windows ── S8.1 ── S8.2 ── S8.3 ── S8.4 ── S8.5 ── S8.6 ── S8.7 ── S8.8 ── S6 Convert2IDF ── S9 Release
            (S7 precedents: done outside this repository, D-082)
```

The pipeline is complete for the linear plan at the end of S4 (D-015); only then do the centred-window rule (S5), precedents, and new typologies begin. The revision stage S4.1 (D-061 to D-064) changes the Grasshopper inputs after the Checkpoint 1 review (one preset input per space type with default preset components, a *Preview Location* input, icons) and runs before S5. The revision stage S4.2 (D-068 to D-077) follows it, also before S5: floors and ceilings designated on the assembled stack, four floor aggregation methods, *Transform Plan*, and heat transfer between zones as an export option. S6 depends on S4.2 for that option (D-077) and follows S8.7 (D-098) and the revision stage S8.8 (D-108). The precedent research of S7 was done in a separate repository (D-082); S8 builds one plan generator per typology family in three sub-stages (D-083, D-084); the four-source precedent set (D-093) adds nine families of every program type (D-094), built in S8.4–S8.7 before S6 (D-098). Simulation, batch experiments, and error analysis are outside this repository (D-016).

### Detailed stage plans

Test-first plans for S0–S4, written on 2026-10-01 from code that was built (warnings as errors) and tested on net8.0 and net48 stage by stage before the plans were written; `net48` was dropped after S0's smoke test (D-053), so the counts below are for `net8.0`:

| Stage | Plan | Tests at stage end (`net8.0`) |
| --- | --- | --- |
| S0 | [2026-10-01-s0-foundation.md](2026-10-01-s0-foundation.md) | 1 core |
| S1 | [2026-10-01-s1-presets-equivalence.md](2026-10-01-s1-presets-equivalence.md) | 65 core |
| S2 | [2026-10-01-s2-pipeline-skeleton.md](2026-10-01-s2-pipeline-skeleton.md) | 94 core, 17 generators, 9 integration |
| S3 | [2026-10-01-s3-plan-simplifiers.md](2026-10-01-s3-plan-simplifiers.md) | 104 core, 17 generators, 38 integration |
| S4 | [2026-10-01-s4-floor-aggregators.md](2026-10-01-s4-floor-aggregators.md) | 104 core, 17 generators, 63 integration |
| S4.1 | [2026-10-01-s4.1-presets-preview-icons.md](2026-10-01-s4.1-presets-preview-icons.md) | 120 core, 19 generators, 63 integration |
| S4.2 | [2026-10-01-s4.2-aggregation-transform-heat-transfer.md](2026-10-01-s4.2-aggregation-transform-heat-transfer.md) | 136 core, 19 generators, 163 integration |
| S5 | [2026-10-01-s5-centred-windows.md](2026-10-01-s5-centred-windows.md) | 142 core, 19 generators, 187 integration |
| S8.1 | [2026-10-02-s8.1-bar-typologies.md](2026-10-02-s8.1-bar-typologies.md) | 152 core, 91 generators, 319 integration |
| S8.2 | [2026-10-02-s8.2-non-rectangular-typologies.md](2026-10-02-s8.2-non-rectangular-typologies.md) | 154 core, 159 generators, 474 integration |
| S8.3 | [2026-10-02-s8.3-enclosed-courtyard.md](2026-10-02-s8.3-enclosed-courtyard.md) | 158 core, 181 generators, 601 integration |
| S8.4 | [2026-10-02-s8.4-non-residential-programs.md](2026-10-02-s8.4-non-residential-programs.md) | 193 core, 224 generators, 704 integration |
| S8.5 | [2026-10-02-s8.5-hub-and-arms-typologies.md](2026-10-02-s8.5-hub-and-arms-typologies.md) | 193 core, 360 generators, 1184 integration |
| S8.6 | [2026-10-02-s8.6-operating-suite-court-cluster.md](2026-10-02-s8.6-operating-suite-court-cluster.md) | 193 core, 427 generators, 1385 integration |
| S8.7 | [2026-10-02-s8.7-per-storey-plans-stepped-band.md](2026-10-02-s8.7-per-storey-plans-stepped-band.md) | 210 core, 463 generators, 1485 integration |
| S8.8 | [2026-10-02-s8.8-previews-any-preset-panel.md](2026-10-02-s8.8-previews-any-preset-panel.md) | 243 core, 518 generators, 1518 integration |
| S6 | [2026-10-02-s6-convert2idf.md](2026-10-02-s6-convert2idf.md) (design note, D-111) | 294 core, 518 generators, 475 export, 1518 integration |
| S9 | [2026-10-03-s9-release.md](2026-10-03-s9-release.md) (design note, D-111) | 346 core, 518 generators, 635 export, 1573 integration |
| Docs move | [2026-10-03-docs-site-move.md](2026-10-03-docs-site-move.md) (D-117 to D-119), version 1.0.1 | unchanged; developer-page export: 8 unit tests |

Where a stage plan and this roadmap differ, the stage plan and its ADRs are authoritative; each plan lists its deviations under "Notes for the reviewer".

---

## 2. Target repository layout

Created incrementally; each stage adds only what it needs.

```text
BEMGen.sln
global.json                        SDK ≥ 8
Directory.Build.props              LangVersion 12, Nullable, TreatWarningsAsErrors, code style in build, polyfill link, version
Directory.Packages.props           central NuGet versions
scripts/verify.ps1                 local build + test gate (replaces CI)
src/
  Shared/          IsExternalInit polyfill for netstandard2.0
  Lod.Core/
    Common/        ToleranceSettings, GeometryLimits, Result<T>, Diagnostic, DiagnosticCodes, ZoneId, BuildInfo
    Schedules/     ScheduleKind, Schedule
    Loads/         LoadType, LoadBasis, LoadDefinition
    Programs/      SpaceType, Thermostat, ZoneProgram, ProgramPreset, PresetValues, ExampleResidentialPresets
    Aggregation/   IEquivalentPropertyAggregator, EquivalentPropertyAggregator, SourceZoneContribution, ZoneMeasures, AggregationRecord
    Geometry/      Point2, Polygon2 (outer ring + holes), PolygonOps (Clipper2), Orientation, Window, PlanMotion
    Model/         surfaces, zones, provenance, IGeneratedPlan, IFloor, IGeneratedBuilding, TextReport
    Layout/        LayoutSurfaceBuilder, LayoutMeasures
    Plans/         PlanGenerator (abstract), PlanParameters, PlanTransform
    Simplification/ IPlanSimplifier, NoSimplification, OverlapMapper, TransferMatrix, FacadeAttribution, WindowRehosting, CentredWindows, SemanticMerge, PerimeterCore, SingleZonePerFloor
    Buildings/     IFloorAggregator, Storeys, Stack, StackedFloorZoneMultiplier, SingleZonePerFloorType, SingleZoneBuilding
    Validation/    Totals, FloorValidator, BuildingValidator, ValidationReport
    Conversion/    HeatTransferOptions (export options shared by the converters)
  Lod.Generators/
    Linear/        LinearPlanGenerator, LinearPlanParameters      (HDHM-TYP-009)
    StairBayBar/ StairPair/ GalleryBar/ TerraceRow/                (S8.1: 001, 008, 002, 006)
    PointPlate/ WingedBand/ OpenCourt/                             (S8.2: 007, 003, 004)
    EnclosedCourt/                                                 (S8.3: 005)
    OfficePlate/ Cafeteria/                                        (S8.4: SYN-TYP-017, 016)
    HubArms/ RadialLobes/ BranchingMall/ CareHub/ FoyerHalls/      (S8.5: 010, 014, 018, 019)
    OperatingSuite/ CourtCluster/                                  (S8.6: 015, 011)
    SteppedBand/                                                   (S8.7: 012)
  Lod.Export/
    Idf/           Convert2IDF                         (S6)
  Lod.Grasshopper/
    Goo/           ScheduleGoo, LoadGoo, ProgramPresetGoo, PlanGoo, FloorGoo, BuildingGoo (with preview)
    Parameters/    matching Grasshopper params
    Components/    one component per pipeline step, plus inspect/validate
    Convert/       Rhino geometry conversion
tests/
  Shared/ Lod.Core.Tests/ Lod.Generators.Tests/ Lod.Integration.Tests/ (Lod.Export.Tests/ in S6)
docs/
  decisions/ plans/ research/ architecture/ development/
examples/
  grasshopper/    example definitions (.gh), saved from Rhino 8 by a person
```

---

## 3. Branching, merging, and release workflow

Per D-004 and D-005.

- **Branches:** `<type>/<scope>-<short-description>` from `main`, e.g. `feature/programs-presets`, `feature/simplifiers-perimeter-core`, `build/solution-skeleton`. One logical change per branch, a few days at most. A stage is several branches, never one long-lived stage branch.
- **Before merging:** rebase on `origin/main`, then run `scripts/verify.ps1` (restore, build with warnings as errors, run all tests).
- **Merging (rebase merge, self-merge allowed):**

  ```bash
  git fetch origin
  git rebase origin/main
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
  git switch main
  git pull --ff-only
  git merge --ff-only feature/programs-presets
  git push origin main
  git branch -d feature/programs-presets
  ```

  Opening a GitHub PR and using **Rebase and merge** is equally valid and leaves a visible record for collaborators.
- **GitHub settings (no CI involved):** protect `main` against force pushes and deletion; require linear history; enable "Rebase and merge" only.
- **Tags:** annotated `v0.N.0` when a stage's exit criteria are met; `v1.0.0` after S9.
- **Reproducibility:** every `IGeneratedBuilding` carries a provenance record (generator parameters and presets, simplifier, floor aggregator, plugin version with commit SHA). Tagged history is never rewritten.
- **Stage method (D-111):** a short design note in `docs/plans/` before the build (scope, decisions, acceptance criteria, task list, no copied code); one test-first build on feature branches in a worktree, independent parts in parallel worktrees; a review of the diff by a second agent before each merge; `scripts/verify.ps1` before each merge; the headless Rhino check `scripts/rhino-smoke/` once per stage on the merge candidate; a fresh clone of the tag passing `scripts/verify.ps1`; pushes only with the owner's approval.
- **Stage bookkeeping:** at each stage end, one decision-log entry (choices and completion), the README status, a dated progress line at the top of this roadmap, and a row in the detailed-plans table; AGENTS.md "Project state" only when its summary changes (D-111).

---

## 4. Stages

### S0 — Foundation

**Goal:** a building, testable solution with a plugin that loads in Rhino 8, plus the decisions every later stage relies on.

**Work slices (one branch each):**

1. `docs/decisions-foundation-adrs` — ADRs, each listing options, decision, and consequences:
   - **ADR-001 Toolchain:** C# 12 and SDK ≥ 8; core libraries `netstandard2.0` with a shared `IsExternalInit` polyfill; plugin `net7.0` only against RhinoCommon/Grasshopper 8.19.25132.1001 (the first packages with `net7.0` builds), loaded by Rhino 8's default .NET Core runtime (D-053); tests `net8.0` only; xUnit; central package management; no System.Collections.Immutable; component GUID policy.
   - **ADR-002 Geometry:** 2.5D. Plans are planar polygons with holes; zones are prisms of floor polygon × floor-to-floor height; walls are vertical rectangles carrying explicit windows (position along the wall, sill, width, height; D-039); floors and ceilings are polygons. Clipper2 (`PathsD`) handles intersection, union, and difference. Rhino conversion only in `Lod.Grasshopper`.
   - **ADR-003 Schedules:** immutable 8760-value hourly arrays (non-leap year); `ScheduleKind.Fraction` (0–1) vs `ScheduleKind.Temperature` (°C).
   - **ADR-004 Tolerances:** one `ToleranceSettings`: distance 1e-6 m, relative area 1e-6 (Clipper2 snaps to a 1e-6 m grid), relative load 1e-9, absolute schedule 1e-9, angle 1e-6 rad.
   - **ADR-005 Conditioning and setpoint aggregation** (D-038): conditioning from presets; "any conditioned wins"; setpoints floor-area weighted over conditioned sources; exposed-area weighting rejected (reasons in D-027). Updates the research brief §7.
   - **Research brief §10 update:** explicit windows; the first generator's centered-window rule; simplifiers keep windows in place (W0); window transformations are S5 (D-039).
   - **ADR-007 Load-basis aggregation:** one magnitude rule for all bases (area, per person, absolute, exterior wall area, air changes — volume weighted, D-019); each (type, basis) component aggregated on its own, so mixed bases are not an error (D-047); schedules weighted by transferred magnitude. Updates the research brief §9. (ADR-006, the plan generation mechanism, was written in S8.1; D-082, D-084.)
2. `build/solution-skeleton` — `BEMGen.sln`, `global.json`, `Directory.Build.props`, `Directory.Packages.props`, `Lod.Core` with its test project and one smoke test, `scripts/verify.ps1`, AGENTS.md "Commands" and "Project state" updated. Further projects are created by the stage that first needs them.
3. `feature/grasshopper-plugin-shell` — `Lod.Grasshopper` plugin with assembly info and one *BEMGen Info* component (version, commit SHA); `docs/development/grasshopper-smoke-test.md` (how to load the plugin in Rhino 8 and what to check).

**Exit criteria:** `scripts/verify.ps1` passes on a clean clone; the plugin loads in Rhino 8 and *BEMGen Info* shows the version; ADR-001 to ADR-005 and ADR-007 accepted.

### S1 — Program presets and equivalence engine

**Goal:** the aggregation rules before any geometry exists: conservation of loads, scheduled loads, occupancy, and air volume flow proven by tests. Setpoint aggregation is a prescribed control rule, tested against its definition, not a conservation invariant.

**Work slices:**

1. `feature/core-common` — `ToleranceSettings`, `Result<T>`, `Diagnostic` and `DiagnosticCodes`, `ZoneId`.
2. `feature/schedules-model` — `Schedule` (immutable, validated length and kind), `AggregationRecord`.
3. `feature/loads-model` — `LoadType` (Occupancy, Lighting, ElectricEquipment, GasEquipment, DomesticHotWater, Ventilation, Infiltration), `LoadBasis` (PerFloorArea, PerPerson, Absolute, PerExteriorWallArea, AirChangesPerHour), `LoadDefinition`.
4. `feature/programs-presets` — `SpaceType`, `Thermostat`, `ZoneProgram` (conditioned with a thermostat, or unconditioned), `ProgramPreset` (space type, program, WWR), `ProgramPresetSet`, and `ExampleResidentialPresets`: illustrative round numbers for testing, with the stair unconditioned — NOT DOE prototype values. Sourcing DOE mid-rise apartment values is an open research input (§7). `docs/research/program-presets.md` documents both.
5. `feature/aggregation-engine` — `IEquivalentPropertyAggregator` implementing ADR-005 and ADR-007. Every result records source IDs, method, and weights. Zero magnitude gives value 0 and a constant-zero schedule with a diagnostic.

**Tests:** validation of every type; seeded property tests for installed and hourly scheduled magnitude, occupancy, and air volume flow; single source returns itself (loads and setpoints); source order does not change the result; conditioning rules (unconditioned sources do not weigh setpoints, all-unconditioned gives an unconditioned target, façade-only sources do not condition a target); zero-load, zero-weight, invalid-measure edge cases.

**Exit criteria:** all tests pass; public types have XML docs; `docs/architecture/domain-model.md` written.

### S2 — End-to-end pipeline skeleton

**Goal:** the whole pipeline runs in Grasshopper for the simplest case: presets → linear plan → no simplification → stacked floors → Convert2BEM, previewed at every step.

**Work slices:**

1. `feature/geometry-ops` — `Polygon2`, `PolygonOps` over Clipper2, orientation bins (N/E/S/W), explicit `Window` (plus the centered placement rule).
2. `feature/plans-model` — pipeline model types (surfaces with explicit windows, zones, provenance, plan/floor/building interfaces) and the layout surface builder.
3. `feature/generators-linear-plan` — `PlanGenerator` base and `LinearPlanGenerator`: rectangular footprint, west stair, double-loaded corridor, one zone per dwelling unit (D-009); one centered window per outdoor wall from each zone's preset WWR (D-039, D-026); deterministic. Refined in S8 from the precedent study.
4. `feature/pipeline-no-simplification-stack` — `IPlanSimplifier`, `NoSimplification`, `IFloorAggregator`, and `Stack` (ground at the bottom, roof at the top, interzone between storeys by polygon overlap).
5. `feature/grasshopper-pipeline-components` — Goo and params; components *Schedule*, *Load*, *Program Preset* (with *Conditioned*), *Example Residential Presets*, *Linear Plan Generator*, *No Simplification*, *Stack Floors*, *Inspect*; preview on every object.
6. `feature/convert-bem-neutral` — `Convert2BEM` (provisional, D-023): per zone Breps, name, space type, multiplier, conditioned flag, loads, schedules, setpoints, surfaces with boundaries, explicit windows, internal mass, as data trees. Documented in `docs/architecture/convert2bem.md`.

**Tests:** zones tile the plan; every outdoor wall of the rectangular generator has one centered window with area = WWR × wall area (valid only for this generator; see ADR-011 in S8); determinism; stacked boundary conditions; integration test presets → generator → `NoSimplification` → `Stack`; snapshots.

**Manual check:** the smoke-test checklist in Rhino 8, plus `examples/grasshopper/pipeline-skeleton.gh` saved by a person.

**Exit criteria:** the example definition runs from presets to `Convert2BEM` outputs, all previews show, and all tests pass.

### S3 — Plan simplifiers and validation

**Goal:** the zoning LoDs, each proven to satisfy the prescribed conservation invariants. Zoning, heat transfer, controls, and window placement are deliberately approximated where the LoD says so; those differences are what the study measures.

**Work slices:**

1. `feature/mapping-overlap` — `OverlapMapper`, `TransferMatrix` (fractions normalised per source), `FacadeAttribution` with coverage gaps (D-041), `WindowRehosting` (D-039).
2. `docs/decisions-perimeter-corner-rule` — ADR-008 perimeter/core corners (bisector trapezoids).
3. `feature/simplifiers` — shared pipeline (propose zones → surfaces → mapping → façade coverage check → window re-hosting → aggregation; partitions between merged sources disappear, D-034); `SemanticMerge` (Z1, by space type and adjacency), `PerimeterCore` (Z2), `SingleZonePerFloor` (Z3).
4. `feature/validation-invariants` — floor and building validation: floor area, volume, exterior wall area, glazing total and per orientation, installed and hourly scheduled magnitude per load type, façade coverage, no overlap, source coverage, traceability (enforced); conditioned floor area (reported, D-038). `Convert2BEM` refuses invalid input unless an override is recorded.
5. `feature/grasshopper-simplifier-components` — *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Map Source to Target*, *Validate*; the validation gate in *Convert2BEM*.

**Tests:** mapping and façade attribution (including partial coverage); window re-hosting (positions kept, windows across two walls rejected); every simplifier passes every invariant for seeded random plans; validation catches a changed program and an uncovered façade; conditioned area reported when the unconditioned stair is merged; snapshots per simplifier.

**Exit criteria:** linear plan at Z0–Z3 validated, previewed, and converted.

### S4 — Floor aggregators

**Goal:** the vertical LoDs; after this stage the pipeline is complete for the linear plan (Checkpoint 1).

**Work slices:**

1. `docs/decisions-vertical-aggregation` — **ADR-009 Vertical aggregation geometry. Gate: accepted before any S4 code.** Records D-031 (slabs become internal mass in `SingleZoneMerged`), D-032 (floor types with multipliers), D-034 (partitions discarded), D-045 (representative storeys at their true elevations), and D-046 (exposed storeys split off as ×1, overlap between storeys adiabatic, floor types may differ in footprint).
2. `feature/aggregators` — `FloorAreaMultiplier` (representative storey nearest the middle of the storeys it stands for; exposed storeys split off as ×1; overlap adiabatic, uncovered parts exposed) and `SingleZoneMerged` (one zone, one part per storey, walls rebuilt with windows kept in place and façade coverage checked, slabs as internal mass).
3. `feature/grasshopper-aggregator-components` — *Floor Area Multiplier*, *Single Zone Merged*.

**Tests:** each aggregator conserves floor area, volume, exterior wall area, glazing, installed and hourly magnitudes, ground, roof, and exposed floor area, and building height against the fully stacked reference; exposed storeys of multiplied types are split off; setbacks and overhangs validate; every simplifier × aggregator combination validates; snapshots.

**Exit criteria:** every simplifier × aggregator combination for the linear plan validates and converts; `docs/architecture/pipeline.md` describes the complete pipeline; a full example definition is saved.

### S5 — Centred windows on rebuilt walls

**Goal:** wherever zones are merged and walls are rebuilt (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, *Single Zone Building*), every outdoor wall of a target zone carries exactly one window, centred on it and shaped by the generator's rule (D-026), whose area is the total glazed area of the source windows that wall covers (D-079). Window level of detail is not a separate axis: the window levels W1–W5 are dropped. Steps that do not rebuild walls (*No Simplification*, *Stack Floors*, *Stacked Floor Zone Multiplier*) keep their input's windows.

**Gate: ADR-012 Centred windows on rebuilt walls, accepted before any S5 code.** It records the rule, where it applies, what is conserved (glazed area per wall, and so per façade, orientation, and building; not window positions), and the guards that hold by construction but still fail loudly: a source window not contained by one target wall (`WindowNotHosted`), a target wall whose glazed area is not smaller than its area (`GlazingExceedsWall`), never a cap or a silent move.

**Work slices:** ADR-012 and the research brief §10; `CentredWindows` in `Lod.Core` (attribution by `WindowRehosting`, shape by `Window.Centered`) used by the shared simplifier pipeline and by `SingleZoneMerge`; Grasshopper descriptions; documentation. No new components; GUIDs unchanged.

**Tests:** per target wall, one centred window whose area is the sum of the covered source windows, none on a wall without glazing; the guards; glazing per orientation unchanged; on the canonical and on rotated and moved plans; snapshots of merged zones change in window geometry only.

### S6 — Convert2IDF

**Goal:** an EnergyPlus-ready IDF from `IGeneratedBuilding` (D-020).

**Scope and plan:** EnergyPlus 25.x, an envelope preset shared with *Convert2BEM*, ideal loads, and no simulation runs yet (D-112); realised as [ADR-010](../decisions/ADR-010-convert2idf.md) sets out and built from the [S6 design note](2026-10-02-s6-convert2idf.md) (D-111).

**Work slices:** ADR-010 for the scope (EnergyPlus version, ideal-loads HVAC, constructions and materials source, schedule representation, internal mass and zone multipliers, unconditioned zones); `feature/convert-idf` in `Lod.Export` as a pure C# text writer; a *Convert2IDF* component that writes the file, with the inputs *EnableInternalWallHeatTransfer* and *EnableFloorHeatTransfer* (both default `False`) from its first version, using the shared `HeatTransferOptions` and `ExportedBoundary` from S4.2 (D-069, D-077).

**Tests:** snapshot IDFs for each simplifier × aggregator combination of the canonical linear plan; object counts and references consistent. Running EnergyPlus is not required.

**First slice (D-111):** move the headless Rhino check from the controller's scratch folder into `scripts/rhino-smoke/` (the harness, a run script that builds the plugin and starts Rhino 8 headless, and one spec per family or feature, with results written outside the repository), so every later stage runs it from the repository.

### S7 — Precedent study (replaced, D-082)

S7 is not run in this repository. The precedent research was carried out in the separate repository `typology-synthesizer` on *High-Density Housing* (DETAIL) instead of *Floor Plan Manual Housing* (D-082, superseding D-011): nine typology families with topological rules, paraphrased in [docs/research/precedents/hdhm-typologies.md](../research/precedents/hdhm-typologies.md). Its third slice, ADR-006, is written in S8.1. The original plan is kept below for reference.

**Goal (original):** base the generators on documented housing-design knowledge (D-011, D-015).

**Source:** Heckmann & Schneider, *Floor Plan Manual Housing* (`heckmann-fpm`). Further sources are decided later. Copies stay outside the repository; only paraphrases, page references, and short attributed quotes are committed.

**Work slices:**

1. `docs/research-precedent-index` — `docs/research/precedents/README.md` (bibliography) and `docs/research/precedents/heckmann-fpm.md`: chapters and pages read; a rules table (rule, value/range, typology, page, confidence); figures referenced by page, never reproduced.
2. `docs/research-floor-plan-synthesis` — `docs/research/floor-plan-generation.md`: typology taxonomy by access system; comparison of generation mechanisms; parameter catalogue; validity rules; per-typology algorithm with diagrams; window placement rules for detailed plans. Unit-internal layout is used only to size units, never to generate rooms (D-009).
3. `docs/decisions-generation-mechanism` — **ADR-006 Plan generation mechanism**, with parameter record signatures for linear, point, and courtyard plans.

**Exit criteria (original):** the synthesis is reviewed and ADR-006 accepted.

### S8 — Typologies (S8.1–S8.7, D-083, D-084, D-098)

**Goal:** one plan generator per *High-Density Housing* family `HDHM-TYP-001` to `HDHM-TYP-009` (D-083, S8.1–S8.3), and from S8.4 one per family of the four-source set `SYN-TYP-010` to `SYN-TYP-019` except `013` (D-093, D-096, D-098), each a `PlanGenerator` subclass with typed parameter and preset records ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)), and a Grasshopper component per generator in panel 2 Generate. Dimensions and counts are design defaults recorded in ADR-006; the gallery of 002 is not modelled. Each sub-stage follows the S5 method (D-080): verified reference, headless Rhino check, plan, per-task execution, local merge and tag; nothing is pushed during the run.

**Gate: ADR-006 and ADR-011 accepted before any S8 code.** [ADR-011](../decisions/ADR-011-minimum-wall-and-window-geometry.md) defines the minimum wall and window geometry (`GeometryLimits`): a generator's outdoor wall shorter than 1 m, or a window narrower or lower than 0.3 m, gets no window and the info `WindowOmitted`, never invalid geometry; rebuilt walls keep the centred-window rule of ADR-012; a window that would straddle target walls stays the error `WindowNotHosted`.

- **S8.1 Plan generation mechanism and bar typologies (`v0.8.0`).** The precedent page, ADR-006 (all nine families specified), ADR-011 and its limits in the generator base; `LinearPlanGenerator` checked as `HDHM-TYP-009` and kept; new generators *Stair Bay Bar* (001), *Stair Pair* (008, one bay of 001's layout), *Gallery Bar* (002, gallery omitted), and *Terrace Row* (006, one dwelling zone per plot and storey).
- **S8.2 Non-rectangular typologies without holes (`v0.8.1`).** *Point Plate* (007), *Winged Band* (003), *Open Court* (004); short façade fragments under ADR-011. Their rotated plans showed that *Semantic Merge* and the unions of tiles must unite zones exactly; the fixes also repair rotated linear and bar plans released up to `v0.8.0` (D-088). *Perimeter Core* states its precondition, that every part of a footprint be wider than twice the perimeter depth (D-087).
- **S8.3 Enclosed courtyard (`v0.8.2`).** *Enclosed Court* (005): footprints with holes supported by every plan simplifier (perimeter/core included) and floor aggregator. The court is outside the building: its edges are outdoor walls, and the surface builder requires every footprint edge, court edges included, to be covered by outdoor zone edges; *Perimeter Core* zones the court façades separately (`P-Court-<Bin>`), and its width precondition applies to the wings between the outer and the court façades (D-087). The headless Rhino check of the reference found the *Convert2BEM* zone solids inward-oriented and the floors facing up on every plan released up to `v0.8.1`; S8.3 applies the orientation rule of D-091.
- **S8.4 Non-residential programs, office plate and cafeteria (`v0.8.3`).** The four-source records pinned (D-093, [syn-typologies.md](../research/precedents/syn-typologies.md)); the scope of D-094 in the research brief, spec, README, AGENTS.md, and this roadmap; [ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md) (the non-residential space types, one typed illustrative preset each, and the departments of every new family, D-097); ADR-006 extended to all nine new families; the default preset components of the new space types; *Office Plate* (`SYN-TYP-017`, a core inside one ring-shaped work-area zone) and *Cafeteria* (`SYN-TYP-016`, a kitchen and servery edge beside the dining field).
- **S8.5 Branching plans (`v0.8.4`).** A shared hub-and-arms layout for *Radial Lobes* (010), *Branching Mall* (014), *Care Hub* (018), and *Foyer Halls* (019).
- **S8.6 Operating suite and court clusters (`v0.8.5`).** *Operating Suite* (015, separate clean and dirty corridors) and *Court Cluster* (011, a footprint with several courts).
- **S8.7 Plans per storey (`v0.8.6`).** A plan generator that returns one plan per storey (D-095, with its ADR: the interface, how the four floor aggregators treat storeys that differ, and how a terrace is designated) and *Stepped Band* (012).

**Tests (every sub-stage):** per generator, zones tile the footprint, every outdoor wall above the ADR-011 minimum has one centred window sized by its preset, zone IDs, determinism, invalid parameters, and a canonical snapshot; every generator × simplifier × aggregator combination validates, also on a plan rotated and moved by *Transform Plan*.

### S9 — Release (D-115)

**Status:** Done (D-116), version 1.0.0.

**Scope:** a local MkDocs docs site with a user part (getting started, concepts, workflow guide, one end-to-end example, typologies, a component reference generated from the plugin with icons and screenshots) clearly separated from a developer part (architecture, ADRs, decision log, assembled from `docs/` at build time); a `sync-docs` project skill; one example `.gh` definition per typology built by the headless harness; a local Yak package build; an MIT license; version 1.0.0. The Grasshopper polish first planned here was done in S4.1, S8.8, and along the way. Built from the [S9 design note](2026-10-03-s9-release.md) (D-111).

**Exit criteria:** a new user can follow the site from presets to `Convert2BEM` and `Convert2IDF` for each typology; `mkdocs build --strict` passes; the examples open and solve; the Yak package builds; `v1.0.0` tagged.

---

## 5. Cross-cutting practices

- **Test-first** for everything in `Lod.Core`, `Lod.Generators`, and `Lod.Export`. Components stay thin enough that the manual smoke test covers them.
- **Snapshots** are small, human-readable text; changing one requires a commit that explains why the output changed.
- **Research rules** (aggregation, setpoints, conditioning, window rules) change only together with `docs/research/` and a decision-log entry.
- **`.gh` example files** are built, saved, and reopened by the headless harness (D-115); a person opens them in Rhino 8 to check the canvas and the viewport.
- **Agents** follow AGENTS.md; a stage's design note names the parts built in parallel and the files each touches, so parallel worktrees do not collide (D-111).

## 6. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| ClimateStudio's real input format differs from the neutral `Convert2BEM` output | Rework of the converter | Converter isolated behind `IGeneratedBuilding`; neutral output documented; revisit D-023 as soon as a reference definition exists |
| `netstandard2.0` limits modern C# features | Friction in core code | Polyfills (`IsExternalInit`); multi-target later if needed (ADR-001) |
| Polygon precision in overlaps | Spurious conservation failures | Clipper2 `PathsD` with fixed precision; tolerances in `ToleranceSettings`; tests at realistic building scales |
| Rounding on the clipping grid on rotated plans | A very small zone of a rotated plan can fail validation (for example `SourceCoverage`) although its quantities are conserved | Tolerances stay central and are never widened (ADR-004); zones are united as tiles that keep their sources' vertices, and vertices on edges are tested at their original positions (S8.2, D-088); every family's defaults validate at the tested placements; a remaining failure is reported, not repaired, and needs its own decision (D-090: zones about 1 m wide) |
| No CI | Broken `main` | `scripts/verify.ps1` before every merge; linear history makes bisecting easy |
| Grasshopper code cannot be unit tested without Rhino | Component regressions | Thin components; smoke-test checklist per stage |
| Future zoning strategies split a source window between target walls | Simplification fails with `WindowNotHosted` | Deliberate: no silent moves; ADR-011 (S8.1) keeps `WindowNotHosted` as an error: a strategy must cut façades at source wall ends; the centred-window rule (S5, D-079) needs every source window on one target wall |
| Illustrative presets mistaken for sourced values | Results not representative | Presets are named `Example…`, labelled in code and docs; sourced presets are an open research input (§7) |
| Copyrighted reference books | Licence | Copies never committed; paraphrase with page references only |

## 7. Open points

Resolved: the plan generation mechanism (ADR-006) and minimum wall and window geometry (ADR-011), S8.1; the window parameter is WWR (D-026); conditioning from presets with "any conditioned wins" (D-038); explicit windows (D-039); one centred window per rebuilt wall with the wall's glazed area, no window-LoD stage (D-079, ADR-012); façade coverage enforced (D-041); representative storeys at true elevations and automatic split of exposed storeys (D-045, D-046, superseding D-040); loads per type and basis (D-047).

Deferred, with gates in the stage that needs them:

1. ADR-009 vertical aggregation geometry — before S4.
2. ADR-012 centred windows on rebuilt walls — before S5 (D-079).
3. ADR-011 minimum wall and window geometry — before S8 (written in S8.1).
4. Sourced program presets (DOE mid-rise apartment loads, schedules, and conditioning, with citations) — a research input from the researcher; the example presets stay illustrative until then. Check that every sourced load maps onto a `LoadBasis` (D-047 allows several bases per load type, but a basis the model lacks, e.g. flow per total exterior surface area including roofs, needs a decision first).
