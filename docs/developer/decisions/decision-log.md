# Decision Log

Chronological record of project decisions made in conversations, meetings, or reviews, so collaborators and agents share the same context.

- One entry per decision, newest at the bottom, numbered `D-NNN`.
- Record: date, who decided, the decision, and why (if given). Link the ADR when a decision needs a full rationale.
- Architectural decisions with trade-offs get an ADR in this folder (`ADR-NNN-<topic>.md`); the log entry links to it.
- Never rewrite a past entry. To change a decision, add a new entry that supersedes it (`Supersedes D-NNN`) and mark the old one `Superseded by D-NNN`.

| Status | Meaning |
| --- | --- |
| Accepted | In force |
| Provisional | Working assumption; revisit at the noted point |
| Superseded | Replaced by a later entry |

---

### D-001 — Commit message convention

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Commit messages use `type(scope): summary`, with `feature` (not `feat`) for new behavior. Full type list in [AGENTS.md](../AGENTS.md#commits).
- Supersedes the plain-sentence examples in the repository spec §25.

### D-002 — No tool attribution in commits

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Commits are authored by the configured human git user. No agent, model, or provider names, attribution footers, or `Co-Authored-By` trailers for tools. Matches repository spec §22 and §25.

### D-003 — Target Rhino 8 only

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The Grasshopper plugin targets Rhino 8. Rhino 7 is not supported. Exact target frameworks are fixed in the foundation ADR (Stage 0).

### D-004 — Branching and merging

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Trunk-based (GitHub Flow): `main` plus short-lived branches named `<type>/<scope>-<short-description>`, mirroring commit types.
- Branches are integrated by **rebase merge** (linear history, individual commits preserved). No merge commits, no squash.
- **No PR review is required**; authors may self-merge.
- No force pushes to `main`.

### D-005 — No CI/CD

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- No CI/CD pipelines are configured. Build and test verification runs locally before merging to `main`.

### D-006 — Downstream energy model: ClimateStudio in Grasshopper

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Provisional — revisit after the ClimateStudio capability spike (Stage 0)
- The downstream EnergyPlus model generator was not yet chosen; assume ClimateStudio running in Grasshopper. This replaces the spec's assumption of an external IDF/REST API for now. The `IEnergyModelExporter` boundary and the versioned JSON intermediate model are kept.

### D-007 — Record chat decisions in docs

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The project expects collaboration across several users and agents. Important decisions made in chat conversations are written to this log (or an ADR) in the same working session.

### D-008 — Staged roadmap with a precedent study

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted (roadmap details pending review)
- Work follows a staged roadmap derived from the spec's milestones, with a foundation stage first and an early minimal JSON export plus Grasshopper preview.
- A precedent study stage indexes reference books on housing plan design and synthesizes the parametric floor plan generation mechanism before generators are built.
- Roadmap: [docs/plans/2026-09-30-implementation-roadmap.md](../plans/2026-09-30-implementation-roadmap.md).

### D-009 — Ground-truth zoning stops at the dwelling unit

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The detailed reference model (Z0) has at most one thermal zone per dwelling unit. Rooms inside a dwelling unit are never modelled. Non-dwelling spaces (corridors, stairs, cores, service) remain their own zones.

### D-010 — Setpoint aggregation method is a parameter

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-027
- When zones with different setpoint schedules are merged, the aggregation method is a parameter of the transformation and is recorded in the model metadata.
- Initial methods: **floor-area weighted** and **exposed-surface-area weighted**, each `T*(t) = Σ wᵢTᵢ(t) / Σ wᵢ` with `wᵢ` the source zone's floor area or exposed envelope area.
- Open details (definition of "exposed", default vs required parameter, zero-weight handling) are settled in ADR-005 during Stage 1, together with an update to the research brief §7.

### D-011 — Current precedent source: Floor Plan Manual Housing

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The precedent study (Stage 2) currently looks at Heckmann & Schneider, *Floor Plan Manual Housing*. The other reference books will be decided later.
- Noted only: no precedent work is started until Stage 2 is scheduled.

### D-012 — No PI sign-off for research-rule ADRs

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- ADRs that change research rules do not require sign-off from Timur Dogan. They still require the research documentation update and a decision-log entry (GLOBAL.md, scientific rule 7).

### D-013 — No GitHub milestones or issues for now

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Progress is tracked through the roadmap in `docs/plans/` and the per-stage plans. GitHub milestones and issues are not used for now.

### D-014 — Setpoint aggregation details

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-027
- Settles the open details of D-010 (to be written up in ADR-005):
  - The setpoint aggregation method is a **required input** with no default.
  - **Exposed surface area** counts only surfaces with an outdoor boundary condition: exterior walls (including their windows) and roofs. Ground-contact, adiabatic, and inter-zone surfaces are excluded.
  - When the exposed-area weights of the merged zones sum to zero (only interior zones, e.g. corridor + core), the weights **fall back to floor area**. The fallback emits a warning diagnostic, and the method actually applied is recorded in the model metadata, so it is never silent.
  - Consequence: when the weights do not sum to zero, a source zone with no exposed area gets weight 0, so its setpoint does not affect the merged setpoint.

### D-015 — Pipeline first, typologies and precedents later

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The entire pipeline must work end to end with a simple linear plan generator before any reference-book typology work or additional typologies are attempted.
- The precedent study (D-011) moves after the working pipeline. Supersedes the ordering in D-008 ("precedent study before generators are built").

### D-016 — Pipeline ends at Grasshopper-ready inputs; no simulation in the pipeline

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted; refined by D-130 (the repository may run EnergyPlus outside the pipeline) and D-132 (batches and their results in the repository)
- The pipeline's deliverable is Grasshopper output usable for (1) visualization and (2) wiring into a ClimateStudio definition. Simulation happens only afterwards, outside the pipeline.
- ClimateStudio does not need to be run for now; the Stage 0 ClimateStudio capability spike is dropped. Refines D-006.

### D-017 — Output is Grasshopper objects, not JSON

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- BEMGen is a Grasshopper plugin. Stages exchange custom typed Grasshopper instances, not a JSON intermediate schema.
- Supersedes the JSON intermediate-model export in the repository spec §14 and research brief §16, and the JSON stages in the draft roadmap. GLOBAL.md, AGENTS.md, README, and the roadmap are updated to match.

### D-018 — Pipeline architecture and vocabulary

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted (open details in the roadmap revision)
- Reference flow given by the decision owner:

  ```text
  program presets (x, y, ...) → LinearPlanGenerator : PlanGenerator → IGeneratedPlan   (previewable, custom typed instance)
  IGeneratedPlan → IPlanSimplifier { NoSimplification, PerimeterCore, ... } → IFloor
  IFloor[] → IFloorAggregator { Stack, FloorAreaMultiplier, SingleZoneMerged } → IGeneratedBuilding
  IGeneratedBuilding → Convert2BEM → ClimateStudio-ready input(s)
  IGeneratedBuilding → Convert2IDF → EnergyPlus simulation-ready IDF
  ```

- Horizontal zoning simplification lives in `IPlanSimplifier`; vertical simplification lives in `IFloorAggregator`.

### D-019 — Air-change-based loads are volume weighted

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Loads expressed in air changes per hour (infiltration, ventilation, and similar) aggregate by zone volume: `ACH* = Σ Vᵢ·ACHᵢ / Σ Vᵢ`, which conserves total air volume flow `Σ Vᵢ·ACHᵢ`.
- Written up in ADR-007 (load-basis aggregation) together with an update to the research brief §9.

### D-020 — Convert2IDF comes after Convert2BEM

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- `Convert2IDF` is implemented in a later stage, after the full pipeline works through `Convert2BEM`.

### D-021 — SingleZoneMerged means the whole building as one zone

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The `SingleZoneMerged` floor aggregator merges the entire building into one thermal zone. One zone per floor is a plan simplifier, not a floor aggregator.

### D-022 — Windows: one parameter per program preset, centered on every exterior wall

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-039
- Windows are specified initially by a single parameter on the program preset (taken to be window-to-wall ratio).
- The plan generator distributes glazing over each zone's exterior walls from that parameter.
- Every window is centered on its wall, at all levels of detail including the most detailed one. There is no explicit window positioning.

### D-023 — Convert2BEM targets ClimateStudio; no reference definition yet

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Provisional — revisit when a ClimateStudio reference definition is available
- `Convert2BEM` must produce inputs that wire into ClimateStudio components. No ClimateStudio definition is available yet, so its output starts in a neutral, documented form and is adapted later.

### D-024 — Program presets

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- What the reference flow called "room presets" are named **program presets**: one per space type (dwelling unit, corridor, stair, ...), carrying loads, schedules, setpoints, and the window parameter. Rooms are never modelled (D-009).

### D-025 — Window conservation rule for plan simplifiers

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-039
- When a plan simplifier creates target zones, each target exterior wall receives the glazed area of the source windows on the façade portion it covers, as one centered window (D-022). Its WWR is derived from that area.
- This conserves glazed area per façade portion, per orientation, and per building. One wide window on a long merged wall is an accepted consequence.
- Recorded in the research brief §10 during Stage 0.

### D-026 — The window parameter is WWR

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Confirms the assumption in D-022: the single window parameter on a program preset is the window-to-wall ratio.

### D-027 — Setpoints are floor-area weighted only

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-038
- The base pipeline aggregates setpoint schedules by floor-area weighting only: `T*(t) = Σ Aᵢ·Tᵢ(t) / Σ Aᵢ`. There is no method input, no exposed-surface-area definition, and no fallback.
- Why (from a review of the roadmap): exposed-surface-area weighting makes the control assumption depend on geometry, which confounds the experiment. Split source zones carry floor area by overlap but not exposure, the zero-exposure fallback is discontinuous, and exposure varies across typologies with the same program. Simplification should change geometry, not the thermostat assumption.
- Exposed-area or other weightings may return later only as explicitly labelled sensitivity tests, never as part of the base pipeline.
- Setpoint aggregation is a prescribed control rule, not a conservation invariant.

### D-028 — All spaces are conditioned for now

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-038
- Every space type is treated as conditioned, so setpoint weights use total floor area. Program presets get no conditioned/unconditioned flag for now.

### D-029 — Conditioning is intentionally homogenized

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li (framing from roadmap review; keeps D-028) · **Status:** Superseded by D-038
- D-028 (every space conditioned) is an **experimental simplification**, not a property of the DOE prototype that supplies the program values. Corridors, stairs, cores, and service spaces may be unconditioned or differently conditioned in the prototype.
- Conditioning status is held identical at every LoD, so it is outside the LoD variables under study. As a consequence, Z0 does not reproduce the prototype's conditioning, and results must not be presented as if it did.
- `docs/research/program-presets.md` and the research brief state this explicitly.
- Alternative not taken: keeping prototype-specific conditioned/unconditioned status. Choosing it later would supersede D-028 and this entry, and would need a conditioned flag on program presets.

### D-030 — Roadmap approved; first checkpoint is S0–S4

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The implementation roadmap (v2 with review fixes) is approved.
- The first checkpoint is the completion of stages S0 to S4: the full pipeline for the linear plan, from program presets through plan simplifiers and floor aggregators to `Convert2BEM`.
- Detailed test-first plans are written for S0 to S4 before execution starts.

### D-031 — SingleZoneMerged slabs become internal mass

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- In `SingleZoneMerged`, slabs between storeys are no longer heat-transfer boundaries between two zones. They become internal mass of the single zone, keeping the slab construction and area, so their thermal storage and exchange area are retained. Written up in ADR-009.

### D-032 — FloorAreaMultiplier uses floor types with individual multipliers

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- `FloorAreaMultiplier` takes a configurable list of floor types, each an `IFloor` with its own multiplier `Nᵢ` ("one floor × Nᵢ for i floor types"). One typical floor × N, or bottom / middle × (N−2) / top, are special cases of this.
- Boundary conditions of each floor type's floor and ceiling are fixed in ADR-009.

### D-033 — FloorAreaMultiplier boundary conditions follow floor-type order

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-040
- Floor types are listed bottom to top. The first type's floor is ground, the last type's ceiling is roof (outdoors), and every other floor and ceiling is adiabatic.
- With a single floor type, that type gets both ground and roof, so ground and roof exposure are multiplied by N; a warning reports this.
- Ground and roof areas are compared with the fully stacked building and reported, not enforced: vertical exposure is part of the simplification under study.

### D-034 — Partitions between merged zones are discarded

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- When zones merge (plan simplifiers Z1–Z3 and `SingleZoneMerged`), walls with the same zone on both sides are discarded, as the research brief describes for rezoning. They do not become internal mass.
- Only inter-storey slabs in `SingleZoneMerged` become internal mass (D-031). Walls and slabs are therefore treated differently on purpose; ADR-009 records this asymmetry.

### D-038 — Conditioning comes from program presets

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted · **Supersedes:** D-027, D-028, D-029
- Why: with every space conditioned, every source has a thermostat and the setpoint rule is never exercised; Z0 would also lose the distinction between dwelling units and corridors, stairs, or other unconditioned spaces.
- Program presets carry conditioned or unconditioned status. Unconditioned zones have no setpoints.
- A simplified zone is conditioned if any source contributing floor area to it is conditioned ("any conditioned wins"). Its setpoints are floor-area weighted over the conditioned sources only: `T*(t) = Σ wᵢTᵢ(t) / Σ wᵢ`, `wᵢ` = transferred floor area of conditioned source i. Setpoint aggregation remains a prescribed control rule, not a conservation invariant; exposed-area weighting stays rejected (reasons in D-027).
- Merging conditioned and unconditioned sources enlarges the conditioned floor area. That change is reported by validation, not enforced: it is a consequence of the zoning simplification under study.

### D-039 — Explicit windows in the model; window LoD becomes its own stage

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted · **Supersedes:** D-022, D-025
- Why: a global "one centered window per wall at every LoD" rule removes the window-LoD axis (W0–W5 in the research brief).
- Walls carry explicit windows: each window has a position along the wall, a sill height, a width, and a height; a wall may have any number of windows.
- The first plan generator (S2) still uses one simple deterministic rule: one centered window per outdoor wall, sized from the preset's window-to-wall ratio (D-026 stays).
- Plan simplifiers and `SingleZoneMerged` keep the source windows unchanged and re-host them on the target walls that cover them (W0 at every zoning level). A window not fully covered by one target wall is an error, never silently moved.
- Window transformations (W1–W5, including the former D-025 rule "one centered window per target wall from the conserved façade glazing") become stage S5 of the roadmap, after Checkpoint 1. Later stages are renumbered: Convert2IDF S6, precedent study S7, typologies S8, Grasshopper UX and release S9.

### D-040 — Floor multiplier must not multiply ground or roof exposure

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Superseded by D-046 · **Supersedes:** D-033
- Why: multiplying ground or roof heat transfer by N creates a boundary-condition artifact that can dominate the error attributed to the vertical simplification.
- `FloorAreaMultiplier` uses the bottom / typical / top convention: floor types are listed bottom to top; the first and the last type must stand for exactly one storey (multiplier 1), otherwise the aggregation fails. The first type's floor is ground, the last type's ceiling is roof, and every other floor and ceiling is adiabatic.
- Ground and roof area conservation against the fully stacked reference are enforced validation checks for every floor aggregator. There is no typical-floor-only mode.

### D-041 — Façade coverage is an enforced invariant

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted
- Why: attribution fractions are normalised per source wall for exact conservation; without a coverage check, a target façade covering only part of a source wall would silently receive all of its glazing and wall-based loads.
- For every source outdoor wall i, the target outdoor walls on the same façade line must cover its full length: `Σⱼ Lᵢⱼ ≈ Lᵢ` within tolerance. Simplifiers and `SingleZoneMerged` fail when it does not hold, and floor validation enforces it as a separate check, evaluated before any normalisation.

### D-045 — Representative storeys sit at their true elevations

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted
- Why: placing one storey per floor type stacked the representative storeys directly on each other, so a 1 / 8 / 1 building was three storeys tall. Vertical position matters for shading, wind exposure, façade position, and any bottom / middle / top differentiation.
- In `FloorAreaMultiplier`, a floor type standing for N storeys occupies its N storeys of the fully stacked building. Its representative storey is placed at the whole storey nearest the middle of those storeys: storey `first + ⌊N/2⌋` (for 1 / 8 / 1 with 3 m storeys: storeys 0, 5, and 9 at 0, 15, and 27 m). Storeys in between are left empty. Zone IDs use the storey index (`L5/…`), so they match the zones of the fully stacked building.
- Building height is an enforced validation check for every floor aggregator, against the fully stacked reference.

### D-046 — Exposed storeys of a multiplied floor type are split off automatically

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted · **Supersedes:** D-040
- Why: multiplying a storey multiplies every surface of it. Exposure (ground, roof, setback roofs, overhanging floors) must never be multiplied, and floor types with different footprints must be allowed, because the study includes buildings whose plan varies with height.
- Floors and ceilings of the representative storeys are resolved against the representative storey below and above: overlap is adiabatic, uncovered parts face outdoors, the lowest storey's floors face the ground, and the highest storey's ceilings are roofs.
- A storey of a floor type with N > 1 whose floor or ceiling is not fully covered by the neighbouring type (always the case for the bottom and the top type) is split off as its own ×1 storey at its true position, e.g. a single type ×10 becomes ×1 / ×8 / ×1. The split is reported as an info diagnostic (`FloorTypeSplit`) and recorded in the building's provenance. Exposure is therefore never multiplied, and no user input is rejected for it.
- Ground area, roof area, exposed floor area, and building height are enforced validation checks for every floor aggregator, against the fully stacked reference. There is no mode that multiplies exposure.

### D-047 — Loads are aggregated per load type and basis

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised in plan review) · **Status:** Accepted · Superseded in part by D-126 (one load per load type, end use, and basis)
- Why: simplified zones merge different programs, and programs may express the same load type in different bases (e.g. ventilation per person in one, per floor area in another; ASHRAE 62.1 ventilation is per person plus per area within one program). Rejecting mixed bases would block legitimate combinations.
- A program may hold one load per load type and basis; components of the same type add up. Each (type, basis) component is aggregated on its own with the ADR-007 magnitude rule, so its design magnitude and its hourly scheduled magnitude are conserved exactly; sources without the component contribute nothing to it. Mixed bases are no longer an error (`MixedLoadBasis` is removed).
- Occupancy may also have several components; a zone's design occupants are their sum, and per-person components use that sum.
- Amends ADR-007 (written in S0) and the research brief §9 accordingly. Whether the eventual DOE or prototype presets fit these bases stays an open research input (roadmap §7).

### D-048 — S0–S4 are executed subagent-driven with two model tiers

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-111
- The stage plans are executed with subagent-driven development: one fresh subagent per plan task, a review after each task, and a controller session that dispatches and verifies but does not write production code.
- Complex tasks (geometry, numerical invariants, toolchain setup, the aggregation engine, simplifiers, floor aggregators, validation) and their reviews use Opus 5.5 with medium reasoning effort. Bounded tasks fully determined by the plan (documents, ADR text, model types, thin Grasshopper components, close-out bookkeeping) use Sonnet 5.5. A bounded task escalates to Opus 5.5 after two failures or any deviation from the plan's expected output.
- Task-by-task assignment and rules: the execution handoff plan §6 (retired and deleted, D-111).

### D-049 — The verified reference code travels as an untracked archive

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-111
- Why: the code verified while writing the S0–S4 plans, its build logs, and the plan-checking tools are useful to whoever executes the plans, possibly on another machine, but must not change the repository's history.
- They are packed into a zip archive with a README and a handoff message, moved between machines outside git, and unpacked into `<repo>/.handoff/checkpoint-1/`, which `.gitignore` excludes. No branch, tag, or commit holds them. The conversation transcript is not part of the archive; durable context belongs in the decision log and the plans.
- The plans stay the source of truth; the reference is used to check results, never copied to make a test pass. Details: the execution handoff plan (retired and deleted, D-111).

### D-050 — Commit author identity

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Why: a machine whose global git configuration uses another address would split the history between two author identities for the same person.
- Commits by Cheng Xuan Li use `Cheng Xuan Li <(e-mail address withheld)>`, the identity of the existing history. A machine with a different global address sets it in the repository's local git configuration (`git config --local user.email`). Unpushed commits made with another address are re-authored before they are pushed. Refines D-002.

### D-051 — Stage-plan checkboxes are ticked at stage close-out

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Why: each plan task specifies exactly which files its commit touches; ticking checkboxes in those commits, or in extra commits between tasks, would change the expected `git status` and diff output.
- During execution the controller tracks task progress in its session. The stage close-out task ticks the stage plan's completed checkboxes in its own commit, together with the plan's status change. Refines the execution model in D-048.

### D-052 — Launch profiles for the Grasshopper plugin

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (raised during S0 execution) · **Status:** Accepted; its .NET Framework profile superseded by D-053
- Why: developing and smoke-testing the plugin needs Rhino started with Grasshopper and the fresh build loaded; the S0 plan only described loading it through Grasshopper's library folders.
- `src/Lod.Grasshopper/Properties/launchSettings.json` is committed with two profiles, **Rhino 8 (.NET Core)** and **Rhino 8 (.NET Framework)**. Each starts Rhino 8 from its default install location in that runtime (`/netcore` or `/netfx`), runs `Grasshopper`, and sets `RHINO_PACKAGE_DIRS` to `bin\<Configuration>\net7.0\` or `bin\<Configuration>\net48\` of the project. A machine with Rhino elsewhere changes `executablePath` locally without committing it. The smoke-test guide describes the profiles as a third way to load the plugin (Option C).
- Added to the S0 plan (Task 10 Step 6, guide text in Task 11, reviewer note 13) after the handoff; in this execution it lands as follow-up commits on the plugin-shell slice. The untracked reference archive is updated to match, following its `tools/README.md` ("Changing a plan after the handoff").

### D-053 — The plugin targets Rhino's .NET Core runtime only; net48 is dropped

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** the `net48` targets in ADR-001 as first written in S0, and the .NET Framework launch profile in D-052
- Why: Rhino 8 runs plugins on its .NET Core runtime by default, and the S0 smoke test passed there. A second runtime doubles builds, test runs, and manual checks without a current need.
- `Lod.Grasshopper` targets `net7.0` only: one `BEMGen.gha`, which Rhino 8 runs on .NET 8. Test projects target `net8.0` only. Core libraries stay on `netstandard2.0` (a `net7.0` plugin cannot reference a `net8.0` library), with the `IsExternalInit` polyfill. The launch profile keeps only **Rhino 8 (.NET Core)**.
- Consequence: a Rhino session switched to .NET Framework (`SetDotNetRuntime`) cannot load BEMGen. If a plugin that BEMGen's output is wired into, such as ClimateStudio, turns out to need .NET Framework mode, this decision is revisited. That has not been checked yet.
- ADR-001 is revised in place, since it is accepted only at the S0 close-out (D-042). The S0 to S4 plans, the roadmap, the execution handoff plan, and the untracked reference archive are revised together. Every stage of the reference was rebuilt with 0 warnings and the same test counts, now on `net8.0` only.

### D-042 — Foundation ADRs accepted

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- ADR-001 to ADR-005 and ADR-007 are accepted at the close of S0. Beyond earlier entries, they decide:
  - [ADR-001](ADR-001-toolchain.md), revised before acceptance to drop the .NET Framework 4.8 target (D-053): core libraries on `netstandard2.0` with C# 12 (`LangVersion` 12.0, not `latest`) and an `IsExternalInit` polyfill; no System.Collections.Immutable, because Rhino ships its own copy, so read-only arrays instead; the plugin `BEMGen.gha` for `net7.0` only, for Rhino 8's default .NET Core runtime, against RhinoCommon and Grasshopper 8.19.25132.1001, making Rhino 8.19 the minimum supported version; tests on `net8.0` only; central package management with exact versions; component GUIDs fixed once merged; the local gate `scripts/verify.ps1` on Windows PowerShell 5.1.
  - [ADR-002](ADR-002-geometry.md): 2.5D geometry in metres; zones as one or more prisms; vertical rectangular walls and horizontal floors and ceilings; Clipper2 at 6 decimals for intersection, union, and difference; vertices snapped to the distance grid; sloped roofs and non-vertical walls out of scope. For windows it records D-039 (explicit windows, W0 kept through simplification) and the first generator's centered placement rule (D-026) without a new window decision.
  - [ADR-003](ADR-003-schedules.md): 8760 hourly values for a non-leap year; fraction or temperature kind; weekday and weekend profiles with an explicit weekday for 1 January; holidays not modelled.
  - [ADR-004](ADR-004-tolerances.md): one `ToleranceSettings`; relative area tolerance 1e-6 instead of the 1e-9 proposed in roadmap v1 and v2; relative comparisons with a floor of 1.
  - [ADR-007](ADR-007-load-basis-aggregation.md): one magnitude rule for every load basis, applied to each load component (load type and basis) separately, so mixed bases are aggregated per component instead of rejected (D-047); the exterior-wall-area basis counts walls only; positive loads with a zero target basis quantity are errors. Exterior-wall fractions are used only after façade coverage is proven (D-041).
  - [ADR-005](ADR-005-conditioning-and-setpoints.md) writes up D-038, with the reasons from D-027 for rejecting exposed-area weighting, and makes no new decision.
- The tech stack and tolerances proposed in roadmap v1 and v2 are superseded where these ADRs differ; roadmap v3 already reflects them.

### D-054 — Checkpoint 1 is completed in an unsupervised run

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- After the S0 close-out, S1 to S4 are executed without human review: the controller drives the subagents of D-048, records findings and minor issues as it goes, and stops only for a blocking issue it cannot resolve. Window transformations (S5) are not part of the run.
- Pushes: the controller pushes `main` and each stage tag (from `v0.0.1`) at the stage close-out, only after `scripts/verify.ps1` and the fresh-clone check pass; never a force push.
- Manual Rhino checks are performed by the controller through screen automation of Rhino 8 and recorded as such; when that is not possible, the check is recorded as not performed (unsupervised run) and left for a person.
- When a plan and the reference archive disagree, the controller investigates and fixes both together with a record, instead of stopping (refines the execution handoff plan §7).
- Decisions the controller makes during the run are logged as "Decided by: controller (unsupervised run)" with status Provisional, for later review.
- A run summary is committed to `docs/plans/` at the end of S4, or when the run stops.

### D-055 — The execution-handoff note stays in AGENTS.md until Checkpoint 1

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Superseded by D-111
- Why: the S1 to S4 close-outs replace the whole "Project state" section of `AGENTS.md`. Their texts were written before the paragraph that points to the execution handoff plan and the git-ignored `.handoff/` reference was added, so the S1 close-out removed it while S2 to S4 still use the reference.
- The paragraph is restored after the S1 text, and the S1 to S3 plans' replacement texts now end with it. The S4 close-out drops it as written, because Checkpoint 1 ends the handoff and retires the reference.

### D-056 — Manual Rhino checks run as scripted headless Grasshopper sessions

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional · Superseded in part by D-111
- Why: D-054 lets the controller perform the manual Rhino checks through screen automation, but no one was present to grant screen control. Rhino itself can still be started and observed.
- The controller starts Rhino 8 (`/nosplash /netcore`) with `RHINO_PACKAGE_DIRS` pointing at `src/Lod.Grasshopper/bin/Release/net7.0/`, runs a Python script through `-_RunPythonScript` that loads Grasshopper headless, places the stage's components by GUID, wires and sets inputs, solves, and writes the components' states, runtime messages, outputs, data trees, and bounding boxes to a file, then exits Rhino. The checklist items are evaluated from that file.
- Checklist items that need a viewport or the toolbar UI (preview colours, icons, panel layout as drawn) cannot be observed this way and are recorded as not performed; the registered category, panel, and exposure of every component are checked instead. Example `.gh` definitions are not created (agents never write them) and remain for a person.

### D-057 — Floor aggregator components ignore null floors

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional
- Why: the S2 smoke test found that when *Linear Plan Generator* fails, the null item it leaves in its output reaches *Stack Floors* through *No Simplification*, and `FloorAggregatorComponent.SolveInstance` threw a NullReferenceException.
- `FloorAggregatorComponent` returns without output when the floor list contains a null, as *No Simplification* does for a null plan. The S2 plan (Task 8 block, reviewer note 13) and the reference archive (S2 to S4) are changed together; the S4 aggregator components inherit the fix.

### D-058 — Stages close with person-only checklist items pending

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional · Superseded in part by D-115 (example definitions)
- Why: the S2 and S4 close-outs require example `.gh` definitions saved by a person in Rhino 8 (agents never write them), and some checklist items need a viewport (D-056). In the unsupervised run (D-054) no person is available, and holding the stage tags would block the later stages for no technical reason.
- In this run a stage is closed and tagged once every check that can be observed passes. The close-out commit records the checks performed (by whom and how) and lists the items not performed. Those items stay open for a person, who records the result in a later commit; any defect found then is fixed in a later change, and the stage tag is not moved.

### D-059 — Rhino geometry uses the central distance tolerance

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional
- Why: the S2 end-of-stage review found `private const double Tolerance = 1e-6` in `src/Lod.Grasshopper/Convert/RhinoGeometry.cs`, a numerical tolerance outside `ToleranceSettings` (GLOBAL.md quality rule 4).
- `RhinoGeometry` passes `ToleranceSettings.Default.Distance` (1e-6 m, unchanged) to `Brep.CreatePlanarBreps` and `Brep.CreateFromCornerPoints`; geometry is still created in metres and scaled to model units afterwards. The S2 plan (Task 7 block, reviewer note 14) and the reference archive (S2 to S4) change together.

### D-043 — Perimeter/core corners are split on the bisectors

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- `PerimeterCore` (Z2) gives each footprint edge the trapezoid between the edge and its inward mitred offset by the perimeter depth, so corners are split along the angle bisectors. Trapezoids in the same orientation bin merge into one perimeter zone (suffixes `-1`, `-2` when they do not form one polygon); the offset ring is the core. Perimeter and core zones have space type `Mixed`.
- Footprints too narrow for a valid core fail with `PlanTooNarrow` and are never repaired; footprints with holes are not supported until S8. The 4.57 m default depth of the Grasshopper component is an input default, not a research rule.
- Written up in [ADR-008](ADR-008-perimeter-core-corners.md).

### D-060 — ADR-009 merged before the owner's acceptance

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional
- Why: S4 Task 1 Step 5 gates Slice B on the decision owner reading ADR-009. In the unsupervised run (D-054) the owner is not available, and ADR-009 only writes up decisions the owner already made (D-031, D-032, D-034, D-045, D-046).
- ADR-009 is merged as written in the S4 plan after a consistency review against those decisions, and S4 continues. The owner's reading of ADR-009 remains open; requested changes are made in a later change, with code changes if the ADR's rules change.

### D-044 — Checkpoint 1 reached

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run) · **Status:** Provisional
- Checkpoint 1 (D-030) is reached: stages S0–S4 are complete and tagged `v0.0.1`, `v0.1.0`, `v0.2.0`, `v0.3.0`, and `v0.4.0`.
- The pipeline runs for the linear plan from program presets through every plan simplifier (`NoSimplification`, `SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`) and every floor aggregator (`Stack`, `FloorAreaMultiplier`, `SingleZoneMerged`) to `Convert2BEM`, with every window kept in place (W0, D-039). All 12 combinations pass building validation in the test suite (`EverySimplifierAndAggregatorCombinationValidates`) and were validated and converted in Rhino 8 in a scripted headless Grasshopper session (D-056); the example definition `examples/grasshopper/checkpoint-1-pipeline.gh` and the viewport checks are pending a person (D-058).
- The pipeline is described in [docs/architecture/pipeline.md](../architecture/pipeline.md); vertical aggregation in [ADR-009](ADR-009-vertical-aggregation.md), with representative storeys at their true elevations (D-045) and exposure never multiplied (D-046). Loads are aggregated per load type and basis at every zoning level (D-047).
- S5 (window transformations, gated on ADR-012), S6 (Convert2IDF), and S7 (precedent study) can start (D-015, D-039, roadmap §1).

### D-061 — Plan generators take one explicit preset input per space type; default preset components per space type

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of Checkpoint 1) · **Status:** Accepted
- Why: a single *Presets* list hides which presets a generator needs and which space type each wire feeds; an explicit input per space type makes the definition self-describing and lets each preset be swapped on its own.
- **Generator inputs.** A plan generator component has one preset input per space type it places instead of the single *Presets* list; for the linear plan: *Dwelling Unit*, *Corridor*, and *Stair*. The inputs are required: an unconnected input is a missing-input error, never a silent fallback, so a definition always shows which presets it uses. A preset whose space type does not match its input is an error. In `Lod.Generators`, `LinearPlanGenerator` takes a typed record with one preset per space type instead of a `ProgramPresetSet` (typed parameter records per typology, AGENTS.md). The *Linear Plan Generator* keeps its GUID; its inputs change.
- **Default preset components.** One per space type, visible on the toolbar: *Dwelling Unit Preset*, *Corridor Preset*, *Stair Preset*. Every input has a default, so each works with nothing connected, as an output-only component. Inputs: name, window-to-wall ratio, *Conditioned*, heating and cooling setpoints (°C, constant), the design value of each of the space type's loads, and an optional schedule per load that replaces the built-in schedule when connected. Defaults are today's illustrative example values (not DOE prototype values), and each component shows a remark saying so; sourced values stay a research input.
- **Dwelling units are not subdivided.** The dwelling unit is the existing `DwellingUnit` space type, one zone per unit; there is no bedroom space type and no splitting of units into rooms.
- **General *Program Preset*.** Stays, for custom presets of any space type. Its *Name* (already an input) is descriptive only: it appears in reports, provenance, and messages and is never used for matching or behaviour. The default preset components get the same *Name* input, defaulting to the component's preset name.
- ***Example Residential Presets*** (the component that outputs a list of presets) is deleted.
- Lands in the revision stage S4.1 (D-064).

### D-062 — Preview location input on every component with a viewport preview

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of Checkpoint 1) · **Status:** Accepted
- Why: several plans, floors, and buildings previewed in one model overlap at the origin; moving each preview lets them be compared side by side.
- The *Linear Plan Generator*, the four plan simplifier components, and the three floor aggregator components get an optional last input *Preview Location*: a vector in model units, default `0,0,0` (a point wired in converts to a vector). It moves only that component's viewport preview. Plan, floor, and building data, the *Inspect* and *Validate* reports, and the *Convert2BEM* outputs stay at their true coordinates, and downstream components do not inherit the move.
- *Convert2BEM* gets no such input; its outputs can be moved with Grasshopper's *Move* if needed.
- Lands in the revision stage S4.1 (D-064).

### D-063 — A bitmap icon for every component

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of Checkpoint 1) · **Status:** Accepted
- Every component has a bitmap icon that depicts its function, replacing the current `Icon => null`.
- Icons are 24 × 24 PNG pictograms, embedded as resources and drawn by a script kept in the repository, so they can be regenerated and restyled consistently: a dark glyph with one accent colour per toolbar panel (Program, Generate, Simplify, Aggregate, Inspect, Convert, Info).
- Lands in the revision stage S4.1 (D-064); S9 only polishes them.

### D-064 — Revision stage S4.1 before S5; no backward compatibility for now

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of Checkpoint 1) · **Status:** Accepted
- D-061, D-062, and D-063 are implemented in a revision stage S4.1, with its own plan in `docs/plans/` and its own tag, executed like S0–S4 (D-048), before S5 starts and before the pending example definitions (D-058) are built.
- Until the owner says otherwise, changes do not preserve backward compatibility: components may be deleted and component inputs and outputs changed without migration or obsolete stand-ins, and saved Grasshopper definitions may break. Component GUIDs still never change (GLOBAL.md); a component that changes keeps its GUID, and a deleted component's GUID is not reused.

### D-065 — An unconnected preset input is Grasshopper's missing-input warning

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of the S4.1 plan) · **Status:** Accepted · **Refines:** D-061
- Why: every required input of every BEMGen component already behaves this way; an extra error would make the preset inputs the only exception.
- The preset inputs of a plan generator component are required inputs. When one is unconnected, Grasshopper reports its own warning (`Input parameter <nickname> failed to collect data`) and the component outputs nothing. There is no fallback to default presets. D-061's "missing-input error" means this behaviour.
- `docs/architecture/domain-model.md` says that a removed diagnostic code's name is not reused, instead of "later stages only append codes", since S4.1 deletes `DuplicateSpaceType` (D-064).

### D-066 — S4.1 is executed in an unsupervised run

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The S4.1 plan is approved and executed without human supervision, following the rules of D-054 where they apply: subagent-driven execution (D-048), a review after each task, findings recorded rather than asked about, a stop only on a blocking issue that attempts cannot solve, manual Rhino checks as scripted headless Grasshopper sessions (D-056), and person-only items left open (D-058). New decisions made during the run are logged as "Decided by: controller (unsupervised run)", status Provisional.
- Nothing is pushed in this run: slices are merged and the stage is tagged `v0.4.1` locally; pushing `main` and the tag waits for the owner.

### D-067 — S4.1 complete

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run, D-066) · **Status:** Provisional
- The revision stage S4.1 (D-064) is complete and tagged `v0.4.1`. D-061: plan generators take a typed preset record with one preset per space type (`PlanPresets`, `PresetSlot`; for the linear plan `LinearPlanPresets`), and a preset of the wrong space type is the error `PresetSpaceTypeMismatch`; `ProgramPresetSet` and the code `DuplicateSpaceType` are deleted. The *Linear Plan Generator* has the inputs *Dwelling Unit*, *Corridor*, and *Stair*; *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset* build presets from `PresetValues` with the illustrative example values as defaults; *Example Residential Presets* is deleted and its GUID `0239f4c9-0f19-4cf1-9d90-08db878eac8a` retired. D-062: the generator, the four plan simplifiers, and the three floor aggregators have a *Preview Location* input that moves only their preview. D-063: every component and parameter, and the plugin, has a 24 × 24 icon drawn by `scripts/make_icons.py`.
- Plans, floors, and buildings are unchanged: all seven snapshots are byte-identical. Setpoint schedules of presets built from `PresetValues` are named `"<preset name> Heating Setpoint"` and `"<preset name> Cooling Setpoint"`. 120 core, 19 generator, and 63 integration tests pass on `net8.0`.
- The S4.1 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058).
- S5 (window transformations, gated on ADR-012) can start; S6 and S7 depend on S4 only.

### D-068 — Ground, roof, and exposure are designated on the assembled building

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted · **Refines:** ADR-009 (D-046)
- Why: whether a floor touches the ground, a ceiling is a roof, or a piece is exposed at a setback is a property of the whole building, not of one floor or of the representative storeys alone.
- Plans and floors leave every floor and ceiling unresolved (as since S2). Every floor aggregator first assembles the full stack of storeys and designates every floor and ceiling piece there: `Ground`, roof (`Outdoors`), exposed (`Outdoors`), or between storeys. A method that models fewer storeys (the zone-multiplier method, D-071) takes the designations of the storeys it models from that assembled stack instead of resolving them against its neighbouring representative storeys.
- ADR-009 is superseded where it differs, by a new ADR written in the revision stage S4.2 (D-073).

### D-069 — Heat transfer between zones is an export option, off by default

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted
- *Convert2BEM* and *Convert2IDF* (S6) get two Boolean inputs, both default `False`: **EnableInternalWallHeatTransfer** for walls between zones, and **EnableFloorHeatTransfer** for floors and ceilings between storeys. When an option is `False`, every surface of that kind that lies between two zones is written as adiabatic; when `True`, it stays paired with the adjacent zone (`Interzone:<zone>`).
- The building model itself keeps the interzone surfaces; the options only change what a converter writes, and the chosen values are recorded in the conversion provenance.
- *Convert2BEM* gets the options in S4.2 (D-073); *Convert2IDF* has them from its first version (S6).

### D-070 — *Transform Plan* moves and rotates a plan's geometry

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted
- Why: unlike *Preview Location* (D-062), a real move or rotation of a plan changes how floors stack (overhangs, setbacks, rotated storeys) and which way façades face.
- A new component *Transform Plan* takes a plan and a Grasshopper transform and outputs a new plan. Only two parts of the transform are applied: the translation in the world x-y plane and the rotation about the world z axis. Anything else the transform contains (vertical translation, rotation about another axis, scaling, shear) is not applied, and the component reports that with a warning; geometry is never changed silently (GLOBAL.md quality rule 6). No vertical translation is applied: storey elevations come from the floor aggregator.
- The core service that does it lives in `Lod.Core`, records the applied rotation and translation in the plan's provenance, and keeps area, volume, wall area, and window area unchanged. Window and wall orientations follow the rotated geometry; the plan's *Orientation* (true north) is unchanged.
- Only plans are transformed. Floors keep the geometry of the plan they were made from, and buildings keep the geometry of their floors.

### D-071 — Floor aggregators: zone multiplier, single zone per floor type, and single zone building

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted
- **Stack Floors** stays as it is: every storey modelled, multiplier 1.
- **Stacked Floor Zone Multiplier** (`StackedFloorZoneMultiplier`) is *Floor Area Multiplier* (`FloorAreaMultiplier`) renamed. It keeps its GUID `e4b44821-c9ed-49b9-9c4e-7c08355254dd` (D-064) and models what it modelled before: representative storeys with `Zone.Multiplier` (D-045), exposed storeys split off as × 1 (D-046). The converters write that multiplier as the engine's zone multiplier. Its preview shows the whole stacked building; storeys that are represented but not modelled are drawn differently from the modelled ones (proposed: transparent grey).
- **Single Zone per Floor Type** (`SingleZonePerFloorType`) is what *Single Zone Merged* becomes, keeping its GUID `506d5037-de93-4aee-a6c4-47dcc97509e1` (D-064): each floor entry (floor type and number of storeys) becomes one zone spanning its storeys, e.g. A × 1 → one zone of A's storey, B × 3 → one zone spanning B's three storeys. Within an entry, the slabs between its storeys become internal mass (D-031) and partitions are discarded (D-034); floors and ceilings between entries stay between two zones (D-068, D-069). The program of each zone is aggregated from its sources with the S1 `EquivalentPropertyAggregator`, so every invariant is conserved, as in *Single Zone Merged* today. Each zone is previewed as one merged volume, not as separate storeys.
- **Single Zone Building** (`SingleZoneBuilding`) is a new method with a new GUID: the whole building as one zone, which is what *Single Zone Merged* does today (D-021). It is previewed as one merged volume.
- The single-zone proxy discussed in the same review (one zone per floor type with area-based quantities multiplied by the number of storeys) is not adopted.

### D-072 — Floor multipliers stay whole numbers

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted
- Every floor aggregator takes whole-number multipliers from 1, as since S2. Fractional multipliers were considered in the same review, for the zone-multiplier and single-zone methods, and rejected: the EnergyPlus `Zone` multiplier field takes whole numbers only.

### D-073 — Revision stage S4.2 before S5

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li (review of S4.1) · **Status:** Accepted
- D-068 to D-071 are implemented in a revision stage S4.2 with its own plan and tag (`v0.4.2`), before S5. The parts of D-069 that concern *Convert2IDF* are requirements for S6. A new ADR on vertical aggregation, superseding ADR-009 where it differs, is written and accepted before any S4.2 code.

### D-074 — An unsupported storey is a warning

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Why: with *Transform Plan* (D-070) a storey can be moved or rotated so that the storey below no longer carries all of it.
- When part of a storey's floor is not covered by the storey below (more than the area tolerance), every floor aggregator still builds the building, treats the uncovered part as exposed (D-068), and reports a warning naming the storey and the uncovered floor area. A storey on the ground is never unsupported.

### D-075 — S4.2 is planned and executed in an unsupervised run

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The controller builds and verifies the S4.2 reference, writes ADR-013 and the S4.2 plan, and executes the plan without human supervision, under the rules of D-066. ADR-013 and the plan are accepted by the controller (Provisional, pending the owner's reading) so that execution can start; decisions made during the run are logged as "Decided by: controller (unsupervised run)", status Provisional.
- `main` and `v0.4.1` are pushed before the run. Nothing is pushed during the run: S4.2 is merged and tagged `v0.4.2` locally, and pushing waits for the owner.
- Defaults the owner did not object to: in *Stacked Floor Zone Multiplier* a surface facing a represented but unmodelled storey stays adiabatic whatever *EnableFloorHeatTransfer* says; unmodelled storeys are previewed transparent grey; *Single Zone per Floor Type* names its zones `E{i}` by floor-entry index and *Single Zone Building* keeps `BUILDING`; nicknames *Stack*, *ZMult*, *1ZType*, *1ZBldg*; *Transform Plan* records the applied rotation about the world origin and the translation; the new ADR is ADR-013.

### D-076 — Rotated plans: façade lines matched over their overlap, storey outlines unioned as tiles

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run, D-075) · **Status:** Provisional
- Why: building the S4.2 reference showed that plans rotated by a non-right angle (D-070) broke the two single-zone aggregators, although every quantity was conserved. Three rules that only held for axis-aligned geometry are generalised; no tolerance changes and axis-aligned results stay identical. Details in ADR-013.
- **Façade coverage (`FacadeAttribution`, D-041):** two walls lie on the same façade line when their separation, measured at both ends of their overlap along the line, is within the distance tolerance. Before, the end points of one wall had to lie within the tolerance of the other wall's infinite line, which failed for a short wall with rounded end points next to a long rebuilt wall (2.4 µm off the extrapolated line, 0.23 µm apart). Walls that do not overlap are not on the same façade line. This changes a validation predicate (`FacadeCoverage`); it makes it exact for rotated walls and does not relax it.
- **Storey outlines (single-zone methods):** the zones of a storey are unioned as tiles (shared grid vertices, T-junction vertices inserted) before clipping, so rotated zones give one outline without slits; a plain union added spurious wall area.
- **Unsupported storeys (D-074):** a storey is unsupported when its covered floor area differs from its floor area by more than the area tolerance (`AreaEquals`), so rounding slivers of rotated setbacks are not reported. The D-046 split still compares the uncovered area with zero, so not even a sliver is multiplied.

### D-077 — S6 depends on S4.2

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run, D-075) · **Status:** Provisional
- Why: *Convert2IDF* must offer the heat-transfer options of D-069 from its first version (D-073), and the shared rule (`HeatTransferOptions`, `ExportedBoundary` in `Lod.Core.Conversion`) is created in S4.2.
- S6 (Convert2IDF) depends on S4.2 instead of S4. S7 (precedent study) still depends on S4 only; S5 depends on S4.2 (roadmap, S4.2 plan commit).

### D-078 — S4.2 complete

- **Date:** 2026-10-01 · **Decided by:** controller (unsupervised run, D-075) · **Status:** Provisional
- The revision stage S4.2 (D-073) is complete and tagged `v0.4.2` locally; pushing `main` and the tag waits for the owner (D-075). [ADR-013](ADR-013-vertical-aggregation-methods.md), accepted by the controller under D-075 and pending the owner's reading, supersedes ADR-009 where it differs. D-068: every floor aggregator starts from `Storeys.Assemble` (`AssembledStack`), and `Storeys.ResolveRepresentative` is deleted. D-071: `FloorAreaMultiplier` is renamed `StackedFloorZoneMultiplier` (*Stacked Floor Zone Multiplier*, ZMult, GUID kept); `SingleZoneMerged` is renamed `SingleZoneBuilding` (*Single Zone Building*, 1ZBldg, new GUID `50965154-e31e-4730-b61c-15a6f40bee6f`); the new `SingleZonePerFloorType` (zones `E{i}`) is behind *Single Zone per Floor Type* (1ZType), which keeps the GUID of *Single Zone Merged*; both single-zone methods share `SingleZoneMerge`. D-074: the warning `UnsupportedStorey`. D-070: `PlanMotion`, `PlanTransform`, and *Transform Plan* (TPlan, `57c17b9c-04b4-4595-9150-bb923877d95e`). D-069: `HeatTransferOptions` in `Lod.Core.Conversion`; *Convert2BEM* has the inputs *EnableInternalWallHeatTransfer* and *EnableFloorHeatTransfer*, both `False` by default, and records them in *Provenance*. D-075 defaults: pieces between storeys of the zone multiplier stay adiabatic whatever *EnableFloorHeatTransfer* says; unmodelled storeys are previewed transparent grey. D-076: façade lines matched over their overlap, storey outlines unioned as tiles, unsupported storeys compared with their floor area.
- Every existing building is numerically unchanged: five snapshots are byte-identical, `aggregator-StackedFloorZoneMultiplier.txt` and `aggregator-SingleZoneBuilding.txt` are the S4 snapshots renamed with identical content, and `aggregator-SingleZonePerFloorType.txt` is new. 136 core, 19 generator, and 163 integration tests pass on `net8.0`, including every simplifier with every aggregator on plans rotated and moved by four placements.
- The S4.2 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058).
- S5 (window transformations, gated on ADR-012) can start. S6 (Convert2IDF, which depends on S4.2 since D-077) implements the *Convert2IDF* part of D-069 with `HeatTransferOptions`; S7 depends on S4 only.

### D-079 — Windows of merged zones: one centred window per wall with the wall's glazed area; W1–W5 dropped

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** D-039 in part (windows kept in place on rebuilt walls; window LoD as its own stage)
- Why: models are built from the bottom up. The plan generator creates windows at the highest level of detail, and every later step only simplifies or aggregates; window level of detail is not a separate experimental axis.
- Wherever zones are merged and walls are rebuilt (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, *Single Zone Building*), every outdoor wall of a target zone carries exactly one window, centred on the wall, whose area is the total glazed area of the source windows that wall covers. Its shape follows the generator's rule (D-026): the wall's rectangle scaled by the square root of glazed area over wall area. This is the only behaviour; there is no option to keep the windows in place.
- Steps that do not rebuild walls (*No Simplification*, *Stack Floors*, *Stacked Floor Zone Multiplier*) keep the generator's windows, which are already one centred window per wall.
- Glazed area is conserved per target wall, and therefore per façade, orientation, and building; validation keeps checking glazing in total and per orientation. Individual window positions are no longer conserved.
- Because every target wall covers its source walls (D-041), every source window lies on exactly one target wall and a target wall's glazed area is always smaller than its area. These hold by construction; the code still checks them and fails loudly (never caps or moves silently) if they were ever violated.
- The window levels W1–W5 are dropped from the roadmap and from the research brief (§10, updated with ADR-012). Stage S5 becomes this change, gated on a short ADR-012 that records the rule.

### D-080 — S5 is planned and executed in an unsupervised run; push after completion

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- S5 (D-079) is run like S4.2 (D-075): the controller builds and verifies the reference, writes ADR-012 and the S5 plan, accepts both (Provisional, pending the owner's reading), and executes the plan without human supervision. Decisions made during the run are logged as "Decided by: controller (unsupervised run)", status Provisional.
- Nothing is pushed during the run. When S5 is complete, its gate passes, and a fresh clone of the tag passes `scripts/verify.ps1`, the controller pushes `main` and the tags `v0.4.2` and `v0.5.0`; never a force push.

### D-081 — S5 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-080) · **Status:** Provisional
- Stage S5 (D-079) is complete and tagged `v0.5.0`. [ADR-012](ADR-012-centred-windows.md), accepted by the controller under D-080 and pending the owner's reading, supersedes in part ADR-002 ("Windows through simplification (W0)"), ADR-009, and ADR-013 where they keep windows in place on rebuilt walls; the research brief §10 drops W1–W5 and describes the rule. `CentredWindows.Place` in `Lod.Core.Simplification` attributes the source windows with `WindowRehosting.Rehost` and gives every target outdoor wall one window shaped by `Window.Centered` (D-026) with the glazed area attributed to it, none when that area is zero; `PlanSimplifier` (*Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*) and `SingleZoneMerge` (*Single Zone per Floor Type*, *Single Zone Building*) use it. `WindowNotHosted` stays as a guard, and the new error `GlazingExceedsWall` guards a wall whose glazed area is not smaller than its area; neither caps nor moves a window. No component, input, output, icon, or GUID changed; the descriptions of the five components that rebuild walls and of the *Windows* output of *Convert2BEM* state the rule.
- Glazing per wall, façade, orientation, and building and every validation report are unchanged. Six snapshots changed in their `window(…)` entries only: `simplifier-SemanticMerge`, `simplifier-PerimeterCore`, `simplifier-SingleZonePerFloor`, `aggregator-SingleZonePerFloorType`, `aggregator-SingleZoneBuilding`, and `aggregator-StackedFloorZoneMultiplier`, which stacks a *Perimeter Core* floor although the zone multiplier itself rebuilds no wall; `linear-plan-canonical` and `stack-two-storeys` are byte-identical. 142 core, 19 generator, and 187 integration tests pass on `net8.0`, including every merging simplifier and both single-zone aggregators on the canonical plan and on plans rotated and moved by two placements.
- D-079's guards hold by construction for the four current zoning strategies. Façade coverage (D-041) alone does not guarantee that every source window lies on one target wall: a future strategy that cuts a source wall inside a window fails with `WindowNotHosted` (roadmap risk table; ADR-011, S8).
- The S5 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058). After `scripts/verify.ps1` passes on a fresh clone of `v0.5.0`, `main` and the tags `v0.4.2` and `v0.5.0` are pushed (D-080).
- S6 (Convert2IDF) and S7 (precedent study) can start.

### D-082 — Precedent source: *High-Density Housing* (DETAIL), studied in a separate repository

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Superseded by D-093 · **Supersedes:** D-011
- The precedent study uses *High-Density Housing* (DETAIL) instead of *Floor Plan Manual Housing*. The study was carried out in a separate research repository, `typology-synthesizer` (local path `D:\typology-synthesizer`, commit `366ffbb`), with knowledge of the BEMGen research brief. It indexes the book's floor plans, catalogues their organisation with cited claims, and specifies nine typology families (`HDHM-TYP-001` to `HDHM-TYP-009`) as topological generator rules with an abstract validation set.
- BEMGen consumes its derived records as the contract for new plan generators: `data/derived/generators.jsonl` (SHA-256 `29700ded…`), `typologies.jsonl` (`5bb31c5c…`), and `s6_validation.jsonl` (`1ebd21d0…`). The rules are topological only; the book supports no metric or count ranges, so dimensions, counts, and façade choices are BEMGen design inputs.
- BEMGen has temporary read-only access to that repository. Nothing in it is modified, and no book content, page renders, or copied drawings enter BEMGen; BEMGen commits only paraphrased family rules with their stable IDs.
- This replaces the research work of roadmap S7 (slices 1–2); ADR-006 (plan generation mechanism) is still written in BEMGen before S8.

### D-083 — S8 builds a plan generator for every *High-Density Housing* family

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- S8 implements a plan generator for each of the nine families `HDHM-TYP-001` to `HDHM-TYP-009` (D-082). The existing `LinearPlanGenerator` is checked against `HDHM-TYP-009` (double-sided internal corridor bar) and kept as that family's generator.
- Dimensions, counts, and other choices the source does not fix are design defaults chosen by the controller, recorded with their reasons in ADR-006; the owner does not need to confirm them.
- The continuous external gallery of `HDHM-TYP-002` is left out of the energy model: no gallery zone, no gallery geometry; the bar's façade on the gallery side is modelled as an ordinary outdoor façade, and the omission is stated in the generator's documentation.
- Generators are not tested against the families' abstract validation records; each generator's documentation describes in text how it realises its family's rules, citing the family and rule IDs.
- A short page `docs/research/precedents/hdhm-typologies.md` paraphrases the nine families with their stable IDs and points to the pinned commit of the source repository (D-082). No book content is committed.

### D-084 — S8 is split into three sub-stages and run like S5

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run) · **Status:** Provisional
- Why: the families differ in what the pipeline already supports. Bars need no pipeline change; non-rectangular outlines produce short façade fragments; the enclosed courtyard needs footprints with holes in every simplifier and aggregator.
- **S8.1** (tag `v0.8.0`): ADR-006 (generation mechanism, parameter records and defaults for all nine families) and ADR-011 (minimum wall and window geometry), the precedent page, and the bar families 009 (check), 001, 008, 002, and 006. **S8.2** (`v0.8.1`): the non-rectangular families without holes, 007, 003, and 004. **S8.3** (`v0.8.2`): the enclosed courtyard 005, with footprints with holes supported by every plan simplifier and floor aggregator.
- Each sub-stage follows the S5 method (D-080): verified reference, headless Rhino check, plan, per-task execution, local merge and tag; the controller accepts its ADRs and plans provisionally, pending the owner's reading. Nothing is pushed during the run; pushing waits for the owner.

### D-085 — A dwelling that spans storeys is one zone per storey

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional · **Refines:** D-009
- Why: plans are generated one storey at a time and stacked by the floor aggregators, so a terraced house of `HDHM-TYP-006` that spans several storeys cannot be one zone of a plan.
- Such a dwelling is modelled as one zone per storey of its plot (`U1…Un` on every storey); its own internal stair is not a zone. D-009 ("one zone per dwelling unit, never subdivided") applies per storey: a dwelling is never split within a storey. The single-zone floor aggregators can merge the storeys of a floor type into one zone when a whole-house zone is wanted.
- ADR-006 records the choice; the owner may revisit it.

### D-086 — S8.1 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Sub-stage S8.1 (D-084) is complete and tagged `v0.8.0` locally; pushing `main` and the tag waits for the owner (D-084). [ADR-006](ADR-006-plan-generation-mechanism.md) and [ADR-011](ADR-011-minimum-wall-and-window-geometry.md), accepted by the controller under D-084 and pending the owner's reading, fix the plan generation mechanism (one `PlanGenerator` subclass per *High-Density Housing* family with typed parameter and preset records; design defaults, zone IDs, and realisation of the rules for all nine families, D-083) and the minimum wall and window geometry of every generator. The precedent page `docs/research/precedents/hdhm-typologies.md` paraphrases the nine families with their stable IDs and the pinned source of D-082. ADR-002's placement rule is refined by ADR-011, and the research brief §10 states the exception.
- `GeometryLimits` in `Lod.Core.Common` (`MinimumWindowWallLength` 1 m, `MinimumWindowWidth` 0.3 m, `MinimumWindowHeight` 0.3 m) is passed through the `PlanGenerator` constructor, the defaults when omitted. An outdoor wall or window below a limit by more than the distance tolerance gets no window and the new info `WindowOmitted`; only non-default limits are recorded in provenance. `LayoutMeasures.PlaceWindowsByRatio` takes the limits and tolerances and returns a `Result`. Rebuilt walls are not subject to the limits (ADR-012).
- `LinearPlanGenerator` realises `HDHM-TYP-009` and is unchanged apart from its documentation. New in `Lod.Generators`: `StairBayBarGenerator` (001, at least 2 bays), `StairPairGenerator` (008, one bay of the shared `StairBayLayout`), `GalleryBarGenerator` (002, at least 2 dwellings, the gallery not modelled, D-083), and `TerraceRowGenerator` (006, at least 2 plots, one dwelling zone per plot and storey, D-085), each with a static `Default` parameter record. New components in *2 Generate*, with icons: *Stair Bay Bar* (SBar, `911c3204-42bb-4023-bdb7-2931ea1caad3`), *Stair Pair* (SPair, `5669d39b-45e6-47ea-9250-f2304d005335`), *Gallery Bar* (GBar, `a58df462-b3c2-46b7-be3d-7ea9f4629280`), and *Terrace Row* (Terr, `f694e595-dba2-4b98-9d1e-f1492e3edf39`). *Linear Plan Generator*'s description names `HDHM-TYP-009`; its inputs and GUID are unchanged.
- The eight existing snapshots are byte-identical; four canonical snapshots are new. 152 core, 91 generator, and 319 integration tests pass on `net8.0`, including every bar family with every simplifier and aggregator on its canonical plan and on the plan rotated by 131.4° and moved by (15.08, −153.9) m.
- The S8.1 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058).
- S8.2 (families 007, 003, and 004) can start; S6 (Convert2IDF) is unaffected.

### D-087 — Perimeter Core requires parts wider than twice the perimeter depth

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Why: the non-rectangular families of S8.2 (winged band, open court) have wings; the corner rule of ADR-008 works at re-entrant corners, but a wing narrower than twice the perimeter depth leaves no valid core.
- *Perimeter Core* requires every wing, plate, and other part of a footprint to be wider than twice the perimeter depth. A narrower plan fails with `PlanTooNarrow`, whose message states this precondition and suggests a smaller depth or another simplifier. Supporting narrower wings needs another partition (for example a straight skeleton) and a new ADR. ADR-008 records the precondition.

### D-088 — Pipeline fixes for rotated plans found in S8.2

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Why: running the S8.2 families through every simplifier and aggregator at many rotated placements found failures of *Semantic Merge* that already affected the linear plan and the S8.1 bars at some rotated placements (released up to `v0.8.0`).
- *Semantic Merge* unites each group as tiles (like the single-zone methods, D-076), so a merged group may have holes (a dwelling ring around a core). The surface builder tests whether a vertex lies on an edge at the vertices' original positions against the distance tolerance, instead of comparing snapped grid cells; the tolerance value is unchanged, it is measured on unsnapped coordinates. Unions of tiles keep the tiles' own vertices instead of grid-rounded ones. Details in ADR-002 and ADR-013. Axis-aligned results and every existing snapshot are unchanged.

### D-089 — S8.2 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Sub-stage S8.2 (D-084) is complete and tagged `v0.8.1` locally; pushing `main` and the tags `v0.8.0` and `v0.8.1` waits for the owner (D-084). The three families without holes that ADR-006 specifies for S8.2 are implemented as specified, with no parameter record, default, or rule of ADR-006 changed: `PointPlateGenerator` (`HDHM-TYP-007`: a square plate with the core `ST`, a `Stair` zone without outdoor walls, and the dwellings `U1…U4` in a pinwheel), `WingedBandGenerator` (`HDHM-TYP-003`: a comb of a band and at least two wings of stair bays, zones `B-…` and `W{i}-…`), and `OpenCourtGenerator` (`HDHM-TYP-004`: a U of north, west, and east wings of stair bays around a court open to plan south, zones `N-…`, `W-…`, `E-…`); the wings share `StairBayLayout` (`Wing`, `Fit`, `FitErrors`), and the S8.1 bars are unchanged. New components in *2 Generate*, with icons: *Point Plate* (PPlate, `8ac9044a-8fbe-4964-a9de-2ef8be35094a`), *Winged Band* (WBand, `e285811d-2fdb-4d31-8b02-62c270b609cf`), and *Open Court* (OCourt, `223014ea-3c01-4d2b-b8ba-92ebdc4a7327`). ADR-006 records the details settled in S8.2 and the pipeline consequences.
- D-088 is implemented test-first: *Semantic Merge* unites each group as tiles, so a merged zone may have holes; the surface builder and the union of tiles test whether a vertex lies on an edge at the vertices' original positions against the unchanged distance tolerance; and unions of tiles keep the tiles' own vertices ([ADR-002](ADR-002-geometry.md), [ADR-013](ADR-013-vertical-aggregation-methods.md)). Each fix repairs rotated plans that already failed on `v0.8.0` (the linear plan and the S8.1 bars through *Semantic Merge*). D-087: *Perimeter Core*'s `PlanTooNarrow` message states that every part of the footprint must be wider than twice the perimeter depth ([ADR-008](ADR-008-perimeter-core-corners.md)); its checks are unchanged. No tolerance or validation check changed.
- The twelve existing snapshots are byte-identical; three canonical snapshots are new. 154 core, 159 generator, and 474 integration tests pass on `net8.0`, including every new family with every simplifier and aggregator on its canonical plan and on the plan rotated by 30° and moved by (5.3, −2.1) m and rotated by 131.4° and moved by (15.08, −153.9) m.
- The S8.2 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058).
- S8.3 (the enclosed courtyard 005, footprints with holes in every simplifier and aggregator) can start; S6 (Convert2IDF) is unaffected.

### D-090 — Very small zones on rotated plans are a known validation limit

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Why: the S8.2 sweeps found that a zone only about 1 m wide (for example a *Point Plate* core of 1 m, or the 0.5 m dwellings of an *Open Court* with a 4 m court depth) can fail `SourceCoverage` on a rotated plan after a merging simplifier: clipping on the integer grid (ADR-002) loses more than the relative area tolerance of ADR-004 on such thin zones. All defaults and every tested placement of the default plans pass.
- The limit is accepted and documented (roadmap risk table, the S8.2 plan's reviewer notes); the tolerance is not widened (AGENTS.md rule 12). A remedy (exact rational clipping for thin zones, or a size-aware tolerance) needs an ADR-004 revision decided by the owner.

### D-091 — Rhino geometry has one orientation rule

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Why: the S8.3 headless check found that every zone solid from `RhinoGeometry` was inward-oriented (negative volume) and that floors faced up like ceilings, on every plan in released versions up to `v0.8.1`; simulation tools that read the *Convert2BEM* Breps may depend on orientation.
- Zone solids are outward-oriented (positive volume); walls and windows face the outward side of their wall (court walls into the court), floors face down, and ceilings and roofs face up, interzone surfaces included. Planar faces are built unreversed, so `BrepFace.NormalAt` gives the facing directly. Only orientation changes, never geometry. Implemented in S8.3 (`RhinoGeometry`, documented in `docs/architecture/convert2bem.md`).

### D-092 — S8.3 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-084) · **Status:** Provisional
- Sub-stage S8.3 (D-084) is complete and tagged `v0.8.2` locally, and with it S8: a plan generator exists for each of the nine *High-Density Housing* families (D-083). Pushing `main` and the tags `v0.8.0`, `v0.8.1`, and `v0.8.2` waits for the owner (D-084). `EnclosedCourtGenerator` (`HDHM-TYP-005`) is implemented as ADR-006 specifies it, with no record, default, or rule of ADR-006 changed: four wings of stair bays on the shared `StairBayLayout` around one court closed on all four sides (zones `S-…` and `N-…` west to east, then `W-…` and `E-…` south to north; by default 1728 m² and 44 windows, 16 of them on the court façades); the footprint is the outer rectangle with the court as its one hole. New component in *2 Generate*, with icon: *Enclosed Court* (ECourt, `b9765cd0-a62b-483d-9470-86d5fda287e8`). ADR-006 records the details settled in S8.3 and the pipeline consequences.
- Every step supports footprints with holes. The court is outside the building: its edges are outdoor walls facing into it, and it has no zone, floor, ceiling, ground slab, or roof. The surface builder requires every footprint edge, court edges included, to be covered by outdoor zone edges over its full length (`UnmatchedEdge`), which edge matching alone missed for a zone filling a court ([ADR-002](ADR-002-geometry.md)). *Perimeter Core* offsets every ring by the bisector rule, gives the court façades their own zones `P-Court-<Bin>` after the outer zones, and leaves a core that is a ring around the court; a wing between the outer and a court façade that is not wider than twice the depth fails with `PlanTooNarrow` (D-087, [ADR-008](ADR-008-perimeter-core-corners.md)). *Perimeter Core* no longer emits `NotSupported`, and the test of that behaviour is removed. The other simplifiers, the four floor aggregators, and validation needed no change ([ADR-013](ADR-013-vertical-aggregation-methods.md)). No tolerance or validation check was relaxed.
- D-091 is implemented in `RhinoGeometry` for every plan generator: zone solids outward-oriented, walls and windows facing their wall's outward side (court walls into the court), floors down, ceilings and roofs up, interzone surfaces included; this repairs the orientation of the *Convert2BEM* Breps and previews released up to `v0.8.1` and is documented in `docs/architecture/convert2bem.md`. The limit of D-090 (zones about 1 m wide on rotated plans) is unchanged.
- The fifteen existing snapshots are byte-identical; one canonical snapshot is new. 158 core, 181 generator, and 601 integration tests pass on `net8.0`, including a ring footprint and the enclosed court with every simplifier and aggregator on the canonical plan and on the plan rotated by 30° and moved by (5.3, −2.1) m and rotated by 131.4° and moved by (15.08, −153.9) m.
- The S8.3 smoke test is recorded in the close-out commit; items it did not perform stay open for a person (D-058).
- S6 (Convert2IDF) and then S9 (Grasshopper UX and release, which depends on S6 and S8.3) can start.

### D-093 — Precedent source: the four-source family set of `typology-synthesizer`

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** D-082
- Why: `typology-synthesizer` has extended its study from *High-Density Housing* (DETAIL) to four sources: *High-Density Housing*, *Floor Plan Manual Housing* (fifth edition), *Architects' Data* (second international English edition), and *Metric Handbook: Planning and Design Data* (second edition). Its active set (records version 3.0.0, `data/four_source/`, research tag `v0.3.0-research`, commit `459dd2c` on branch `codex/handbook-integration`) has 19 families, `SYN-TYP-001` to `SYN-TYP-019`, each with ordered topological generator rules and a symbolic validation report.
- BEMGen takes all 19 families as its precedent set, of every program type, not only housing (D-094). `SYN-TYP-001` to `SYN-TYP-009` are the nine *High-Density Housing* families `HDHM-TYP-001` to `HDHM-TYP-009` that S8 implemented (D-083), carried with their organisation unchanged (`002` and `007` gain further examples), so the existing nine generators stay valid. The new families are `010` to `013` (housing, from *Floor Plan Manual Housing*) and `014` to `019` (a branching shopping mall, an operating suite with separate clean and dirty routes, a cafeteria service edge beside a dining area, an office plate around a central service core, an elder-care home with a communal hub, and a public foyer branching to activity spaces).
- The owner is updating `typology-synthesizer` for the findings of the 2026-10-02 review (work not yet on its `main`, an outdated README, a contradictory variant statement for `007`, no counterexamples for `014` and `016`–`019`, and an incomplete list of unassigned plans). BEMGen pins the tag and the SHA-256 of the records it consumes once that update has landed; whether BEMGen adopts the `SYN-TYP-*` IDs in its documents is settled in the stage plan.
- Unchanged from D-082: the rules are topological only and no source supports a metric or count range, so dimensions, counts, and façade choices remain BEMGen design inputs; BEMGen has temporary read-only access to that repository, modifies nothing in it, and commits only paraphrased family rules with their stable IDs, never book content, page renders, or copied drawings.

### D-094 — Non-residential programs are fully in scope

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- The study and the plugin cover every program type of the precedent set (D-093), not only residential buildings: retail, healthcare (operating suites), food service, office, elder care, and assembly or community uses, alongside housing. Each of the 19 families gets a plan generator.
- Consequences: research question 2 of the research brief ("by residential building typology") widens to building typologies in general, and the repository spec, README, AGENTS.md, and roadmap are aligned with it in the next stage plan; new space types need their own typed program presets (D-061) with explicit, documented assumptions (illustrative values until reference values are chosen, as for the existing presets, D-023); the semantic types and program groups are extended as explicit data, never inferred from names.

### D-095 — A plan generator may produce a different plan per storey

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Why: `SYN-TYP-012` (stepped dwelling bands whose lower roofs become terraces) has a floor plan that changes from storey to storey, which one plan repeated over every floor cannot represent.
- A plan generator may return one plan per storey. The interface change, how the floor aggregators treat storeys that differ (`Stack`, `StackedFloorZoneMultiplier`, `SingleZonePerFloorType`, `SingleZoneBuilding`), and how a terrace is designated (the exposed part of a lower storey's roof is an outdoor roof, the covered part an interzone ceiling, D-068) are designed in an ADR in the stage plan.

### D-096 — The incremental row (`SYN-TYP-013`) is set aside

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** D-094 in part
- `SYN-TYP-013` (built row-house bays alternating with bays reserved for later growth) gets no plan generator for now; the other 18 families of D-093 each get one. D-094 is otherwise unchanged.
- Why: modelling the reserved bays needs a choice the precedent does not settle (outdoor gaps, fully built bays, unconditioned shells, or the growth state as an input), and the family has a single provisional precedent. It can be taken up again by a later entry.

### D-097 — Non-residential plans are zoned per department

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted; refined by D-160 for the DOE generators
- At the most detailed level a plan generator gives a non-residential floor one zone per department: a contiguous group of rooms of one program in one part of the floor, not one zone per room or tenancy. Examples: the shops of one mall wing, an anchor store, the public mall; the bank of operating theatres, the clean corridor, the dirty corridor, the support rooms; the kitchen and servery, the dining area; the office work area, the service core; one group of care bedrooms, the communal hub; the foyer, each activity hall, the support rooms.
- Housing is unchanged: one zone per dwelling unit and storey (D-085), never split into rooms. Which rooms form a department in each family is set in the ADR of S8.4 and the family's generator documentation.

### D-098 — The new families are built in S8.4–S8.7, before S6, and pushed after each sub-stage

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li (order, pushes, unsupervised run); controller (split) · **Status:** Accepted
- The nine new families of D-093 and D-096 are built in four sub-stages, each run like S8 (D-084: verified reference, headless Rhino check, plan, per-task execution, local merge and tag), without supervision; the controller chooses default dimensions and accepts its ADRs and plans provisionally, pending the owner's reading.
- **S8.4** (tag `v0.8.3`): the pinned records (D-093), the scope alignment of D-094 in the brief, spec, README, AGENTS.md, and roadmap, the non-residential space types and typed presets with their default preset components and icons, an ADR on program types and department zoning (D-097), and the families 017 (office plate around a central core) and 016 (cafeteria service edge). **S8.5** (`v0.8.4`): branching plans with a shared hub-and-arms layout, families 010, 014, 018, and 019. **S8.6** (`v0.8.5`): 015 (operating suite with separate clean and dirty routes) and 011 (linked clusters around several courts). **S8.7** (`v0.8.6`): plans that differ by storey (D-095, with an ADR) and 012 (stepped bands with terraces).
- After each sub-stage's gate and a fresh clone of its tag pass `scripts/verify.ps1`, `main` and the tag are pushed, never forced. S6 (Convert2IDF) follows S8.7; S9 depends on S6 and S8.7.

### D-099 — BEMGen documents use the `SYN-TYP-*` family IDs

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Why: the precedent set is the four-source family set (D-093), whose IDs `SYN-TYP-001` to `SYN-TYP-019` cover every family; `SYN-TYP-001` to `SYN-TYP-009` carry the nine *High-Density Housing* families `HDHM-TYP-001` to `HDHM-TYP-009` with the same organisation and rule numbering.
- From S8.4 on, BEMGen documents name families by their `SYN-TYP-*` IDs and give the `HDHM-TYP-*` lineage for `001` to `009` ([syn-typologies.md](../research/precedents/syn-typologies.md)). `hdhm-typologies.md` stays as the issued baseline and is not updated further. Component descriptions and ADR-006 sections written in S8.1–S8.3 may keep their `HDHM-TYP-*` IDs as long as the `SYN-TYP-*` ID is also given; descriptions are updated when a component is next changed, and no GUID changes.

### D-100 — The hub-and-arms families have at most four arms

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Why: the families of S8.5 that branch from a hub (`SYN-TYP-010`, `014`, `018`, `019`) share one layout, `HubArmsLayout`, which is axis-aligned in the plan frame of ADR-002, so its arms can only leave the hub on its four sides.
- The hub-and-arms families are limited to 3–4 arms, `018` to 2–4, as [ADR-006](ADR-006-plan-generation-mechanism.md) specifies: 3–4 lobes (`010`), 3–4 branches (`014`), 2–4 bedroom wings (`018`), and 2–3 halls (`019`, whose support wing takes one more arm, so 3–4 arms in all); a larger count is `InvalidParameter`. This is a limit of BEMGen's layout, not of the families, which set no bound (ADR-006: no family has an upper bound). It is revisited in S8.5 if a family needs a radial layout with arms at other angles.

### D-101 — S8.4 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Sub-stage S8.4 (D-098) is complete and tagged `v0.8.3`; after its gate and a fresh clone of the tag pass `scripts/verify.ps1`, `main` and `v0.8.3` are pushed (D-098). The four-source records of `typology-synthesizer` are pinned at `v0.3.1-research` (`7538ed3`) with their SHA-256 and paraphrased in `docs/research/precedents/syn-typologies.md` (D-093, D-099). The scope of D-094 is in the research brief (question 2, §4), the repository spec, README, AGENTS.md, and the roadmap (S8.4–S8.7 before S6; S9 after S6 and S8.7).
- [ADR-014](ADR-014-program-types-and-department-zoning.md), accepted by the controller under D-098 and pending the owner's reading, appends twelve `SpaceType` values (`Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, `ActivityHall`), reuses `Core`, `Lobby`, and `Service`, and gives each of the fifteen types one illustrative, conditioned preset in `ExampleNonResidentialPresets` (not DOE or standard values, D-023; ventilation only for the kitchen and the operating theatre; retail schedules with their own Saturday and Sunday) and a default preset component in *1 Program*, with icons. It also sets which rooms form one zone in every new family (D-097). ADR-006 specifies all nine new families (010, 011, 012, 014–019) with controller design defaults (D-098), the hub-and-arms families with at most four arms (D-100).
- New generators and components in *2 Generate*, with icons: *Office Plate* (`OfficePlateGenerator`, `SYN-TYP-017`, OPlate, `783cefaa-b836-4dbc-b16d-8e74820ed361`): an `Office` ring around a central `Core` zone without outdoor walls, at least 3 m of work area on every side. *Cafeteria* (`CafeteriaGenerator`, `SYN-TYP-016`, Cafe, `95956724-ddbc-48ce-9874-0ec6c244c8fe`): a `Kitchen` zone along the whole north edge of a larger `Dining` zone. The office ring is the first zone with a hole in a footprint without one; the surface builder, every simplifier, and every aggregator handle it without change. No tolerance or check was relaxed.
- The sixteen existing snapshots are byte-identical; two canonical snapshots are new. 193 core, 224 generator, and 704 integration tests pass on `net8.0`, including both families with every simplifier and aggregator on the canonical plan and on the plan rotated by 30° and moved by (5.3, −2.1) m and rotated by 131.4° and moved by (15.08, −153.9) m.
- Smoke test (D-056): the controller's scripted headless Grasshopper session on the verified reference (`f841f0c`, whose `src/`, `tests/`, and `scripts/` equal the executed branch) in Rhino 8.25.25314.11001 (.NET 8.0.31) passed every performed item: the 15 preset and 2 generator components registered with their GUIDs and 24 × 24 icons; every preset with only its remark; the default office plate (1260 m², core solid of volume 410.4, office solid of 10 faces with 2 inner loops and volume 4377.6, walls toward the core facing into it) and cafeteria; all 96 combinations (both families, three placements, four simplifiers, four aggregators, 1/3/1) with *Validate* passing and no negative volume; and the error cases. It is recorded in `docs/development/grasshopper-smoke-test.md` and the close-out commit; the viewport look, the icons in the toolbar, and example definitions stay open for a person (D-058).
- S8.5 (families 010, 014, 018, 019 on the shared hub-and-arms layout) can start.

### D-102 — The layout choices of the hub-and-arms families

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Why: [ADR-006](ADR-006-plan-generation-mechanism.md) fixes the arm order of the shared hub-and-arms layout (east, north, west, south) but not which sides a family with fewer than four arms uses, and its shared zone-order rule (hub first, then arm by arm) differs from the zone order of its section on `SYN-TYP-019`; the S8.5 reference settled both and made the layout's internals visible to their tests.
- A family with *n* arms uses the first *n* sides in the arm order, so two care-hub wings (`SYN-TYP-018`) leave the hub east and north, an L, not a bar through the hub; this is the only rule consistent with the foyer with halls (hall 1 east, the support wing north, hall 2 west, hall 3 south) and with three arms whose free hub side faces south. A straight bar for two arms would change only the side selection of `HubArmsLayout` and ADR-006.
- The foyer with halls (`SYN-TYP-019`) lists its zones `FO`, `H1…Hn`, `SV`, as its ADR-006 section says: its support wing comes after the halls, the one exception to the arm-by-arm order, which ADR-006's shared paragraph records.
- `Lod.Generators.csproj` makes its internals visible to `Lod.Generators.Tests` (`InternalsVisibleTo`), the first use of the item in the repository, so the internal `HubArmsLayout` is tested directly and not only through its four generators.

### D-103 — S8.5 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Sub-stage S8.5 (D-098) is complete and tagged `v0.8.4`; after its gate and a fresh clone of the tag pass `scripts/verify.ps1`, `main` and `v0.8.4` are pushed (D-098). The four families that branch from a hub are implemented as [ADR-006](ADR-006-plan-generation-mechanism.md) specifies them on one shared, axis-aligned layout, `HubArmsLayout` (internal, `Lod.Generators/HubArms/`): a square hub with up to four arms of one width centred on its sides in the order east, north, west, south, a family with *n* arms using the first *n* sides (D-102), each arm with its own frame in which the families cut their zones; an arm wider than the hub and more than four arms are `InvalidParameter` (D-100). New generators and components in *2 Generate*, with icons: *Radial Lobes* (`RadialLobesGenerator`, `SYN-TYP-010`, RLobes, `a9f132c2-40c3-40b9-ba6a-3f3e1f2ced80`): 3–4 lobes of two dwellings each around a `Stair` core; *Branching Mall* (`BranchingMallGenerator`, `SYN-TYP-014`, BMall, `d886b33f-7b51-41f9-b160-a550e6aadd2b`): one `Mall` zone through a central court and 3–4 branches of `Retail` shop wings and anchors; *Care Hub* (`CareHubGenerator`, `SYN-TYP-018`, CHub, `7d3d1002-c695-47df-afd9-48f50c5b3e90`): 2–4 wings of a `Corridor` between two `CareBedroom` zones around a `CareCommunal` hub, whose 0.8 m corners beside the default wings get no window (ADR-011); *Foyer Halls* (`FoyerHallsGenerator`, `SYN-TYP-019`, FHalls, `6638efe7-c0e8-45b6-89b1-1e9e3f725c15`): 2–3 `ActivityHall` zones and a `Service` wing around a `Lobby` foyer, zones `FO`, `H1…Hn`, `SV` (D-102). No record or default of ADR-006 changed; ADR-006 records the details settled in S8.5.
- *Perimeter Core* keeps the footprint's own vertices in its perimeter zones: it united each orientation bin's trapezoids with a plain union, whose grid rounding turned a footprint edge shorter than about 1 m (the care hub's corners) by more than the angular tolerance on rotated plans, so the single-zone aggregators reported `FacadeNotCovered` (up to 26 of 800 combinations in a sweep, and at the test suite's 131.4° placement). Fixed test-first and documented in [ADR-008](ADR-008-perimeter-core-corners.md) and [ADR-002](ADR-002-geometry.md); no tolerance or check was relaxed, and every existing result is unchanged.
- The eighteen existing snapshots are byte-identical; four canonical snapshots are new. 193 core, 360 generator, and 1184 integration tests pass on `net8.0`, including every family with every simplifier and aggregator on the canonical plan, rotated by 30° and moved by (5.3, −2.1) m and rotated by 131.4° and moved by (15.08, −153.9) m, and with its fewest and most arms; arms not wider than twice the perimeter depth fail *Perimeter Core* with `PlanTooNarrow` (D-087).
- Smoke test (D-056): the controller's scripted headless Grasshopper session on the verified reference (`12a7e83`, whose `src/`, `tests/`, and `scripts/` equal the executed branch) in Rhino 8.25.25314.11001 (.NET 8.0.31) passed every performed item: the 4 generator components registered with their GUIDs, integer count inputs, presets in record order, *Preview Location* last, and 24 × 24 icons; the default radial lobes (624 m²), branching mall (7744 m²), care hub (1552 m², six `WindowOmitted` corners), and foyer with halls (1800 m²) with every zone a valid solid; all 320 combinations (four families, five placements and counts, four simplifiers, four aggregators, 1/3/1) with *Validate* passing and no negative volume; and the error cases. It is recorded in `docs/development/grasshopper-smoke-test.md` and the close-out commit; the viewport look, the icons in the toolbar, and example definitions stay open for a person (D-058).
- S8.6 (families 015 and 011) can start.

### D-104 — The layout choices of the operating suite and the court cluster

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Why: [ADR-006](ADR-006-plan-generation-mechanism.md) fixes the records, defaults, zone IDs, and band and wing order of `SYN-TYP-015` and `SYN-TYP-011`, but not the corridor count that follows from the band order, how *Perimeter Core* zones several courts, or whether the court cluster shares more code with the enclosed court; the S8.6 reference settled these.
- Operating suite: a corridor follows every bank and the corridors alternate from a dirty one in the south, so *n* banks have ⌈n/2⌉ clean and ⌊n/2⌋ + 1 dirty corridors, numbered separately (`DC1, TB1, CC1, TB2, DC2, TB3, CC2, …`); with an odd count the northmost band is a clean corridor. The theatre banks' only outdoor walls are their east ends, which the example theatre preset's WWR 0 leaves without a window and without `WindowOmitted` (ADR-011 rule 1). The generator tests' window check (`PlanAssertions.HasOneCentredWindowPerOutdoorWall`) now requires no window on an outdoor wall whose zone's preset has WWR 0, a stricter rule that every earlier generator test still passes.
- Court cluster: shares `StairBayLayout` with the enclosed court and nothing else, so `EnclosedCourtGenerator` and its snapshot are unchanged; middle wings are named *Middle i*; the stair bays of the south and north wings are checked only for a valid `CourtCount`.
- *Perimeter Core* with several holes is unchanged: the court trapezoids of one bin are united across all holes, so each court gives its own zone per bin, numbered `P-Court-<Bin>-1…` in the union's output order, which is west to east on the canonical plan but is not a court number on a rotated plan ([ADR-008](ADR-008-perimeter-core-corners.md)). Naming court zones per court is left to a later ADR.

### D-105 — S8.6 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Sub-stage S8.6 (D-098) is complete and tagged `v0.8.5`; after its gate and a fresh clone of the tag pass `scripts/verify.ps1`, `main` and `v0.8.5` are pushed (D-098). The two families are implemented as [ADR-006](ADR-006-plan-generation-mechanism.md) specifies them, with no record, default, or rule changed (D-104). New generators and components in *2 Generate*, with icons: *Operating Suite* (`OperatingSuiteGenerator`, `SYN-TYP-015`, OSuite, `33323afd-abf1-4ecc-bf54-5d67c411c962`): a `ClinicalSupport` zone across the west end and bands of `OperatingTheatre` banks between alternating `DirtyCorridor` and `CleanCorridor` zones, every bank between one clean and one dirty corridor, no clean corridor beside a dirty one, every band adjoining the support rooms; *Court Cluster* (`CourtClusterGenerator`, `SYN-TYP-011`, CCluster, `01fc2ca9-3ec0-4142-b827-2519a4523d36`): wings of stair bays around a row of at least two courts, each middle wing bordering two courts, the first footprint with several holes.
- No step of `Lod.Core` changed: every simplifier, aggregator, and validation handles several holes, and *Perimeter Core* gives each court its own court zones per orientation ([ADR-008](ADR-008-perimeter-core-corners.md), [ADR-002](ADR-002-geometry.md)); wings not wider than twice the perimeter depth, between two courts included, fail it with `PlanTooNarrow` (D-087). No tolerance or check was relaxed.
- The twenty-two existing snapshots are byte-identical; two canonical snapshots are new. 193 core, 427 generator, and 1385 integration tests pass on `net8.0`, including both families with every simplifier and aggregator on the canonical plan, rotated by 30° and moved by (5.3, −2.1) m and rotated by 131.4° and moved by (15.08, −153.9) m, with the fewest and the most tested counts (2 and 5 banks, 2 and 4 courts), and with the most at 131.4°; a sweep of 50 rotations for both families and, as a regression, the enclosed court and the S8.5 families found no failure in 14 400 combinations.
- Smoke test (D-056): the controller's scripted headless Grasshopper session on the verified reference (`373af00`, whose `src/`, `tests/`, and `scripts/` equal the executed branch) in Rhino 8.25.25314.11001 (.NET 8.0.31) passed every performed item: the 2 generator components registered with their GUIDs, integer count inputs first, presets in record order, *Preview Location* last, and 24 × 24 icons; the default operating suite (1046.4 m²) and court cluster (2880 m², *Perimeter Core* 13 zones, 17 with three courts), with all 92 zone Breps inspected valid solids and no negative volume anywhere; all 160 combinations (two families, five placements and counts, four simplifiers, four aggregators, 1/3/1) with *Validate* passing; and the error cases. It is recorded in `docs/development/grasshopper-smoke-test.md` and the close-out commit; the viewport look, the icons in the toolbar, and example definitions stay open for a person (D-058).
- Markup: the S8.5 close-out left a stray code-fence line after D-102 and after D-103 in this log and at the end of `docs/development/grasshopper-smoke-test.md`, so the text after it rendered as code. The S8.6 documentation commit removed the line in the smoke-test guide and the S8.6 close-out the two in this log, changing no entry's text; the close-out checks that every Markdown file it touches has balanced code fences and that no appended entry ends with a fence line.
- S8.7 (`SYN-TYP-012`, plans per storey, D-095) can start.

### D-106 — Plans per storey: a sibling generator base, list wiring, and multipliers

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Why: D-095 left the interface, the treatment of storeys that differ, and the designation of terraces to an ADR; [ADR-015](ADR-015-plans-per-storey.md) records the options and this decision.
- A family whose plan differs per storey is a `MultiStoreyPlanGenerator<TParameters, TPresets>` (`Lod.Core.Plans`) returning one ordinary `IGeneratedPlan` per storey, bottom-up, sharing the preset checks, surfaces, windows, and provenance with `PlanGenerator` through one internal helper (`PlanBuilder`), so the plans of the sixteen single-plan families are unchanged; each plan records `Storey` (from 0), and a storey's diagnostics are prefixed `Storey k: `. Rejected: every generator returning a list, a storey index parameter, and a new pipeline type for a stack of storeys.
- No floor aggregator, validation rule, or pipeline type changes: the storeys are floor entries with multiplier 1, and the designation on the assembled stack (D-068) already makes the uncovered part of a lower ceiling an outdoor roof (a terrace) and the covered part a piece between storeys, with ground and roof areas that validate (`TerraceTests`, which passed on the S8.6 code). Multipliers above 1 are allowed and repeat a storey; the generator's building is the one with every multiplier 1.
- In Grasshopper the generator's *Plan* output is a list, wired item-wise through a simplifier into an aggregator's *Floors* with *Multipliers* unconnected; each storey's preview is raised to its elevation, while the plans stay at elevation 0.
- `SteppedBandGenerator` additionally requires `Length > StairWidth` (a dwelling row of no width otherwise), a check ADR-006 did not list; its *Implemented (S8.7)* note records it.
- With four storeys of the default 14 m base depth the top storey is 7 m deep and fails *Perimeter Core* with `PlanTooNarrow` (D-087); the integration tests therefore run four storeys with a 17 m base depth and test the default-depth case as that failure, and no default changed. The core of the default band's top storey under *Perimeter Core* is 0.86 m deep, below the about 1 m of D-090, yet every combination validates, at both rotated placements and in a sweep of 50 rotations; D-090 stays the known limit.

### D-107 — S8.7 complete; S8 complete

- **Date:** 2026-10-02 · **Decided by:** controller (unsupervised run, D-098) · **Status:** Provisional
- Sub-stage S8.7 (D-098) is complete and tagged `v0.8.6`; after its gate and a fresh clone of the tag pass `scripts/verify.ps1`, `main` and `v0.8.6` are pushed (D-098). [ADR-015](ADR-015-plans-per-storey.md), accepted by the controller under D-098 and pending the owner's reading, fixes plans per storey (D-095, D-106).
- New generator and component in *2 Generate*, with icon: *Stepped Band* (`SteppedBandGenerator`, `SYN-TYP-012`, SBand, `3c685bfb-b45b-45af-98d2-8318a6314922`): a band of a west stair, dwellings, and a rear corridor that every dwelling adjoins, stepping back `StepDepth` per storey so that each lower roof keeps a terrace of `Length × StepDepth`; by default 3 storeys of 576, 468, and 360 m², 33 windows. Its *Plan* output is the list of storeys, bottom-up.
- No step of `Lod.Core` changed apart from the new base and its shared helper; no tolerance or check was relaxed. The twenty-four existing snapshots are byte-identical; one canonical snapshot is new. 210 core, 463 generator, and 1485 integration tests pass on `net8.0`, including the band with every simplifier and aggregator on the canonical plans, at the two rotated placements, with 2 and 4 storeys, and with 4 at 131.4°; a sweep of 50 rotations for four bands and, as a regression, the linear plan, the enclosed court, the court cluster, and the care hub found no failure in 6400 combinations.
- Smoke test (D-056): the controller's scripted headless Grasshopper session on the verified reference (`a98d4c5`, whose `src/`, `tests/`, and `scripts/` equal the executed branch) in Rhino 8.25.25314.11001 (.NET 8.0.31) passed every performed item: the component registered with its GUID, the integer Storey Count first, the presets in record order, *Preview Location* last, and a 24 × 24 icon; the *Plan* list of three storeys of 576, 468, and 360 m², each previewed at its elevation; every simplifier returning three floors and *Stack Floors* validating with multipliers 1 and with its *Multipliers* left at the default, roof and ground area 576 m²; the terraces facing outdoors and the covered parts between storeys; all 42 zone Breps inspected valid solids and no negative volume anywhere; all 80 combinations (five placements and counts, four simplifiers, four aggregators) with *Validate* passing; and the error cases. It is recorded in `docs/development/grasshopper-smoke-test.md` and the close-out commit; the viewport look, the icons in the toolbar, and example definitions stay open for a person (D-058).
- With S8.7, S8 is complete: 18 plan generators, one for every family of the four-source set except the set-aside `SYN-TYP-013` (D-096). S6 (Convert2IDF) can start; S9 follows S6.

### D-108 — Storey previews, an any-program preset, and a panel for built-in presets (S8.8)

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li (the three requests); controller (their realisation and the stage) · **Status:** Accepted
- Why: the owner's review of S8.4–S8.7 found the storey plans of a multi-storey generator previewed at their storey heights but the floors simplified from them previewed at height 0; asked for a data node that turns a program-specific preset into a base preset usable on every program input of every generator; and asked for the built-in presets in a panel of their own.
- **Previews.** A floor simplified from a storey plan (ADR-015) is previewed at that plan's storey height, as the plan is, so the plan generator and the simplifiers show storeys at the same heights; plans and floors that are not storeys stay at height 0. Only the preview moves (D-062): data, Breps, and *Convert2BEM* are unchanged.
- **Any-program preset.** A Grasshopper parameter (a data node like the native *Geometry* parameter) casts any preset, built-in or general, to a preset without a space type. Every program input of every plan generator accepts such a preset, and the zones keep the space type the generator's layout gives them; a preset that keeps its space type must still match its input (`PresetSpaceTypeMismatch`). The use of an any-program preset on an input is recorded in the plan's provenance, so no program assumption changes silently (GLOBAL.md scientific rule 3).
- **Panel.** The 18 built-in preset components (*Dwelling Unit*, *Corridor*, *Stair*, and the fifteen of ADR-014) move to a new panel *1 Program Presets*; *1 Program* keeps *Program Preset*, *Load*, *Schedule*, and the new parameter. No GUID changes (D-064).
- These are built in revision stage S8.8 (tag `v0.8.7`), run like S8.4–S8.7 (D-098) before S6; pushing waits for the owner.

### D-109 — How the storey previews, the any-program preset, and the preset panel are built

- **Date:** 2026-10-02 · **Decided by:** controller (D-108) · **Status:** Provisional
- Why: D-108 fixed the three requests and left their realisation to the controller; [ADR-014](ADR-014-program-types-and-department-zoning.md) and [ADR-015](ADR-015-plans-per-storey.md) record the options.
- **Any-program preset.** `ProgramPreset.SpaceType` is nullable; `AsAnyProgram()` returns the preset without a space type and with its name, program, and WWR unchanged; presets are still created typed. The slot check of every generator accepts an any-program preset on every slot, a typed preset must still match (`PresetSpaceTypeMismatch`); the zones keep the layout's space type. `Presets` records each slot's space type with the preset name, and each slot given an any-program preset adds `AnyProgramPreset.<Input>=<name>`; plans of typed presets are unchanged. Rejected: a `SpaceType.Any` value, a flag beside a kept type, matching by name.
- **Grasshopper.** The parameter *Any Program Preset* (AnyP, `AnyProgramPresetParameter`, `24bc6a12-ad06-4c25-bc9d-4e8318b8744c`) in *1 Program* casts what is wired into it through its `PreferredCast` (a preset goo, a plain preset, or a plain preset wrapped by Grasshopper, as a script gives it); the generators' preset inputs (`ProgramPresetParameter`) take its goo through theirs; one shared sentence in every preset input's description. The eighteen built-in preset components move to `1 Program Presets` and keep the Program accent.
- **Storey previews.** Storey plans record `StoreyElevation` (the floor heights below, m), one more provenance key on every plan of a `MultiStoreyPlanGenerator` such as the stepped band; `StoreyProvenance.ElevationOf` follows operations of one input, so plans, moved plans, and floors of a storey preview at its height; buildings and other plans and floors at 0. Rejected: a field on the pipeline types, `Storey × FloorHeight`.

### D-110 — S8.8 complete

- **Date:** 2026-10-02 · **Decided by:** controller (D-108) · **Status:** Provisional
- Revision stage S8.8 (D-108) is complete and tagged `v0.8.7` locally; pushing waits for the owner (D-108). Implemented as D-109 decides: the any-program preset ([ADR-014](ADR-014-program-types-and-department-zoning.md)), the parameter *Any Program Preset* (AnyP, `24bc6a12-ad06-4c25-bc9d-4e8318b8744c`, with icon) in *1 Program*, the panel *1 Program Presets* with the eighteen built-in preset components, and storey previews at `StoreyElevation` for plans, moved plans, and floors ([ADR-015](ADR-015-plans-per-storey.md)). No GUID changed; data, Breps, and *Convert2BEM* outputs unchanged.
- The twenty-five existing snapshots and sixty existing icons are byte-identical. 243 core, 518 generator, and 1518 integration tests pass on `net8.0`, including any-program presets on every input of all 18 generators and the linear plan and stepped band with any-program presets through every simplifier and aggregator, each validating.
- Smoke test (D-056): the controller's scripted headless Grasshopper session on the verified reference (`d9c3059`, whose `src/`, `tests/`, and `scripts/` equal the executed branch) in Rhino 8.25.25314.11001 (.NET 8.0.31) passed every performed item: *Any Program Preset* (AnyP, primary, 24 × 24 icon) in *1 Program* with *Program Preset*, *Load*, and *Schedule*, and the eighteen built-in presets in *1 Program Presets* with unchanged GUIDs; the cast of *Office Preset* shown as `Preset Example Office (any program, no space type, WWR 0.4)`; AnyP(Office) on the *Linear Plan Generator*'s *Corridor* input with no runtime message, `AnyProgramPreset.Corridor=Example Office` in the provenance, and *Validate* passing, while *Office Preset* wired directly still gives `PresetSpaceTypeMismatch`; AnyP(Kitchen) on both inputs of *Office Plate*; AnyP(Care Bedroom) on all three inputs of *Stepped Band* with all 16 simplifier × aggregator combinations validating; and the storeys of the default stepped band drawn at 0–3, 3–6, and 6–9 m by the generator and every simplifier, also through *Transform Plan* and with a simplifier's *Preview Location*, while the linear plan and its floors stay at 0–3 m. It is recorded in `docs/development/grasshopper-smoke-test.md` and the close-out commit; the viewport look, the toolbar panels and icons, a non-preset value wired into AnyP, and example definitions stay open for a person (D-058).
- S6 (Convert2IDF) can start.

### D-111 — Lean stage process; the handoff tradition is retired

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** D-048, D-049, D-055; D-056 in part (the harness moves into the repository)
- Why: the owner's review of S8.4–S8.8 found that every stage's code was written once in a reference build and then reproduced three more times: a plan holding it verbatim, two replays of that plan, and a re-execution task by task. About 60 % of the tokens and half the wall time went into proving that copies equal the original. Real test-first work and every substantive defect found happened in the build and the headless Rhino check, while the copying layers caused defects of their own (stray code fences, broken anchors, line endings).
- From S6 on, every stage is run this way:
  1. **Plan first, briefly.** A design note in `docs/plans/` of one or two pages, written before the build: scope, decisions, acceptance criteria, and a task list. It holds no copied code.
  2. **Build once.** One agent builds the stage test-first on feature branches in a worktree, committing focused slices. Those branches are the deliverable; they are merged after the gate. Nothing is rebuilt from a plan.
  3. **Review, not replay.** A second agent reviews the diff of each slice or of the stage (correctness, invariants, documentation) before the merge.
  4. **The headless Rhino check is a repository script** (`scripts/rhino-smoke/`, one spec per family or feature, D-056), run once per stage on the merge candidate.
  5. **No handoff archive.** The `.handoff/` archive, its reference copies, `MANIFEST.sha256`, `stage_manifest.py`, and `check_plans.py` are retired and deleted with their `.gitignore` entry, and so are the execution handoff plan and the Checkpoint 1 run summary (both remain in git history), the reference and replay worktrees and branches, and the handoff rules in the agent definitions. Completed plans and past decision-log entries keep their historical text; links to deleted files become plain text.
  6. **Lighter records.** One decision-log entry per stage (choices and completion together); AGENTS.md "Project state" is a short summary pointing to the roadmap's progress log and is not rewritten every stage; smoke-test checklists stay short.
  7. **Parallel work.** Independent parts of a stage (for example separate families) are built in parallel worktrees and merged one after another.
- Kept: test-first development, `scripts/verify.ps1` before each merge (not before every commit), the headless Rhino check, byte-identical snapshots and icons unless a change is documented, the fresh-clone gate at tags, and pushes only with the owner's approval. Agents: `bemgen-complex` builds stages and reviews geometry, numerics, and pipeline code; `bemgen-bounded` does documents, records, and bookkeeping and reviews them.

### D-112 — Convert2IDF scope: EnergyPlus 25.x, an envelope preset, ideal loads, no runs yet

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted; superseded in part by D-130 (EnergyPlus 26.2, weather and outputs chosen, EnergyPlus run in opt-in tests)
- *Convert2IDF* (S6) targets EnergyPlus 25.x (25.2), and EnergyPlus is not run, neither by tests nor by the component; the IDF is checked as text and by parsing it back.
- Constructions come from a new typed envelope preset, shared by *Convert2IDF* and *Convert2BEM* and the same at every level of detail.
- HVAC is ideal loads for conditioned zones (unconditioned zones get none).
- Simulation scope is not decided yet: no weather, climates, or output selection; the IDF holds only the minimum simulation objects. Both are taken up when simulations are run.
- The realisation is set in [ADR-010](ADR-010-convert2idf.md) (controller choices provisional), and S6 is planned in the [S6 design note](../plans/2026-10-02-s6-convert2idf.md) (D-111).

### D-113 — S6 complete

- **Date:** 2026-10-02 · **Decided by:** controller (D-111, D-112) · **Status:** Provisional
- Stage S6 (D-112) is complete as version 0.9.0; tagging `v0.9.0` and pushing wait for the owner. The planned `v0.6.0` became `v0.9.0` because the versions since S8 reached 0.8.7 and must not go back; S9 stays `v1.0.0`. Built as D-111 sets out, from the [S6 design note](../plans/2026-10-02-s6-convert2idf.md) (now Done): part A moved the headless Rhino check into `scripts/rhino-smoke/`; part B added the envelope preset (`Lod.Core.Envelope`: `EnvelopePreset`, `EnvelopeValues`, `Construction`, `Layer`, `GlazingSpec`, `ExampleEnvelopePresets`, illustrative values, [envelope presets](../research/envelope-presets.md)), the *Envelope Preset* component (`89ebd842-fc6e-4a06-95f5-2fcfe39f08b8`) and parameter (`efcbaf51-af02-44af-8d57-c4ca82c2ab3d`), and *Convert2BEM*'s *Envelope* input; part C added `Lod.Export` with the IDF writer ([ADR-010](ADR-010-convert2idf.md), [convert2idf.md](../architecture/convert2idf.md)); part D added the *Convert2IDF* component (2IDF, `56dd6611-90b2-4299-b53c-650652843a1a`, *5 Convert*, with icon) over the `Convert2Idf` service, which writes the file only when *Write* is true and an existing file only when *Overwrite* is true. Each part was reviewed by a second agent before its merge.
- Choices made in S6 beyond ADR-010's draft (recorded in ADR-010, pending the owner's reading):
  - **Coordinates:** relative coordinates with every zone origin at 0, so the vertices are the building's own, and the building orientation (`OrientationDegrees`) as the `Building` *North Axis*; the draft's world coordinates with north axis 0 would have dropped the orientation, which EnergyPlus ignores in world coordinates.
  - **Degenerate geometry from grid clipping on rotated plans (D-090):** slivers (a cleaned ring with fewer than three vertices or an area of at most the distance tolerance times its perimeter), zero-width spikes, and excursions through a repeated vertex are not written, on both sides of a pair, with the warning `SliverOmitted` naming the zone, floor or ceiling, elevation, and the areas removed; a floor or ceiling that is only slivers is omitted before partners are matched; a ring that crosses itself, so that rebuilding it would change its area, is the error `DegeneratePolygon`. Edges shorter than the 0.01 m at which EnergyPlus merges vertices give the warning `ShortEdge`; none occurs in the tests.
  - **Numbers** are written with fifteen significant digits (`G15`), formatted identically by .NET Framework 4.8 and .NET 8; the rounding is far below every tolerance.
  - **Loads** with a basis EnergyPlus has no field for (per exterior wall area, per person for infiltration, any basis of hot water) are written as the absolute design level of one zone instance, so no basis is an error.
  - **Run period:** a non-leap calendar year starting on the presets' first day of the year (2018 for Monday), without the weather file's holidays and daylight saving, so the hourly schedules fall on their days.
  - **Convert2BEM** has two new outputs, *Constructions* (aligned with *Surfaces*) and *Window Constructions* (aligned with *Windows*), appended after *Provenance*, instead of one.
  - **Envelope roles:** an exposed-floor role was added; an interior floor is listed from the zone below to the zone above, its ceiling side uses the reversed construction, and of two walls between zones the one whose zone ID sorts after the other's uses the reversed interior wall; `ConstructionRoles` is the one place that decides, for both converters, and a surface without a role is the error `NoConstructionRole`.
  - **IDD check:** every class the writer uses was compared with the EnergyPlus 25.2.0 IDD, every object is written to its `\min-fields` with the IDD defaults explicit, and `scripts/idd-check/` checks IDF files against an IDD kept outside the repository: 0 problems on the 355 files the tests convert and on the 33 files the Rhino run wrote.
  - **To verify on the first EnergyPlus run (D-112):** per-area loads in zones spanning storeys rely on EnergyPlus using the stated zone floor area; the window construction is named like its glazing material.
- Completion: the existing snapshots and icons are byte-identical; five new IDF snapshots. 294 core, 518 generator, 475 export, and 1518 integration tests pass on `net8.0` (`scripts/verify.ps1`, 0 warnings). Headless Rhino check (2026-10-02, Rhino 8.25): the new spec `convert-idf` passed (32 of 32 buildings validate, every *Convert2IDF* output written, *Write* false, *Overwrite*, and a missing path behave as specified, *Envelope Preset* and *Convert2BEM*'s envelope outputs as documented, and a connected Envelope input without an envelope preset warns in both converters), and `any-preset-and-previews` and `linear-and-aggregators` are unchanged; in Rhino the spec counts each IDF's objects and the IDD check runs on the files it wrote, while the parse-back of references and invariants runs in the unit tests (`Lod.Export.Tests`), not in Rhino; *Path* accepts only fully qualified paths; a failed validation cannot be built from the components, so blocking and *Override* are covered by unit tests only.
- Open for a person (D-058): the toolbar look of the new icons, and a first EnergyPlus run once a weather file and outputs are chosen (D-112), which also settles the two items above. Next: S9.

### D-114 — Floors and ceilings between storeys are clipped as conformed polygons

- **Date:** 2026-10-03 · **Decided by:** controller (D-111) · **Status:** Provisional
- Why: S6 found zero-width artefacts on rotated and moved plans, spikes, excursions through a repeated vertex, and slivers about 1e-6 m wide, which validation accepts and *Convert2IDF* omits with `SliverOmitted` (D-090, ADR-010). Built from the [zero-width artefacts design note](../plans/2026-10-03-zero-width-artefacts.md) (now Done) as D-111 sets out, and reviewed by a second agent.
- Root cause: every artefact lay in a floor or ceiling piece cut by `Storeys.ResolveStacked`, none in a zone part or wall. Where a vertex of one storey's zone lies on an edge of a zone of the adjacent storey (a T-junction), clipping on the 1e-6 m grid rounded it off that edge.
- Fix: the footprints of each pair of adjacent storeys are prepared together as conformed polygons (`PolygonOps.Conform`, the preparation the union of tiles already used): vertices in one grid cell are unified, T-junctions are inserted into the edges they lie on, and result vertices go back to the footprint vertex registered first in their cell. One conformed pair per pair of storeys serves the lower storey's ceilings and the upper storey's floors, so both sides of a slab have the same vertices and area. Within a cell the first registered vertex wins, so vertices up to √2 × `Distance` apart can merge, as in the union of tiles; the area effect is far below the relative area tolerance. Documented in [ADR-002](ADR-002-geometry.md), with notes in [ADR-010](ADR-010-convert2idf.md) and [ADR-013](ADR-013-vertical-aggregation-methods.md). No tolerance or validation check changed.
- Sweep (not committed): 50 placements of each of the 18 families through all 16 simplifier and aggregator combinations, 14,400 buildings: artefacts in 1,249 buildings (43,232 findings) before, none after. `ZeroWidthArtefactTests` keeps every family canonical and at the two placements of the typology tests free of spikes, repeated vertices, excursions, necks, and slivers.
- Intended behaviour change: rounding slivers no longer face outdoors, so a rotated setback stack is fully covered, and *Stacked Floor Zone Multiplier* no longer splits off its lowest setback storey for exposure (D-046): the storeys of the rotated setback test go from `L0x1,L1x1,L2x1,L3x1,L5x2,L6x1` to `L0x1,L1x1,L2x1,L4x3,L6x1`. This is correct because that storey's floor is fully covered by the storey below; the split was caused only by about 1.4e-5 m² of rounding slivers, not by exposure. Axis-aligned results and every snapshot are unchanged.
- *Convert2IDF*'s handling of slivers, spikes, and excursions stays as a guard; no generated conversion of the tests warns `SliverOmitted` any more, which the export tests now assert, also at a second placement (131.4°, (15.08, −153.9) m).
- Checks: `scripts/verify.ps1` passed with 0 warnings (346 core, 518 generator, 635 export, and 1573 integration tests on `net8.0`). On `346af8e` the controller ran all 11 `scripts/rhino-smoke` specs (every *Validate* true, no exceptions, errors only in the error scenarios) and the IDD check against the EnergyPlus 25.2.0 IDD (0 problems in all 515 IDF files the export tests write). The later commits cache the conformed pairs, which gives byte-identical floors and ceilings in all 1,152 buildings of four placements of every family, and add tests and documentation.
- Version 0.9.1, tag `v0.9.1` (controller): results on rotated plans differ from `v0.9.0` (no rounding slivers, the setback regrouping), so the change gets its own version for reproducibility; no snapshot changed.

### D-115 — S9 is the release: a local docs site, generated examples, a Yak package, MIT, v1.0.0

- **Date:** 2026-10-03 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · **Supersedes:** D-058 in part (example definitions) · Superseded in part by D-117 (where the docs site lives and whether it is published)
- Why: the Grasshopper polish S9 was planned for (2026-09-30) was done along the way (icons and preset components in S4.1, the preset panel and any-program preset in S8.8, runtime messages from diagnostics throughout), so S9 becomes the release, with the owner's additions.
- **Docs site.** A Markdown site built with MkDocs, served on localhost for now and not published (no GitHub Pages). It separates clearly a **user** part (getting started, definitions of the concepts, a workflow guide, one end-to-end example, the typologies, and a component reference with every component's inputs, outputs, defaults, icon, and screenshots) from a **developer** part (the architecture documents, ADRs, and decision log, assembled from `docs/` at build time, never copied into the repository). The component reference is generated from the plugin itself, so it cannot drift from the code.
- **`sync-docs` skill.** A project skill checked into the repository (`.claude/skills/sync-docs/`) that checks whether the docs site and the developer docs match the implementation (components, inputs and outputs, defaults, GUIDs, icons, decisions) and outlines a plan to bring them up to date; it is run on demand and as a step of every stage close-out (D-111).
- **Example definitions.** One `.gh` definition per typology and the end-to-end example, built and saved by the headless harness (`scripts/rhino-smoke`), in `examples/`; a person opens them to check. This supersedes D-058 for example definitions; other person-only items (viewport look, toolbar) stay open as D-058 says.
- **Screenshots** are captured by script inside Rhino (viewport capture, Grasshopper canvas image export); if the canvas cannot be captured that way, the controller asks the owner once for screen control of Rhino.
- **Yak package.** A local build script makes the Rhino package; it is never published to the package server without the owner's approval.
- **License:** MIT, copyright Environmental Systems Lab.
- **Version 1.0.0**, tag `v1.0.0`, marks the first complete release; backward compatibility is still not required (D-064 unchanged), and component GUIDs never change.
- Run as D-111 sets out, from the [S9 design note](../plans/2026-10-03-s9-release.md).

### D-116 — S9 complete; v1.0.0

- **Date:** 2026-10-03 · **Decided by:** controller (D-111, D-115) · **Status:** Provisional
- Stage S9 (D-115) is complete as version 1.0.0; the tag `v1.0.0` is set at the fresh-clone gate and pushing waits for the owner. Built as D-111 sets out from the [S9 design note](../plans/2026-10-03-s9-release.md) (now Done), in two parallel builds (R needs Rhino, W does not), each reviewed by a second agent.
- **Delivered:**
  - **Docs site** (MkDocs, Material theme, pinned requirements, served on localhost, never published) with a user part (getting started, concepts, workflow guide, end-to-end example, the 18 typologies) and a developer part, separated in navigation and landing pages.
  - **Component reference** generated from the plugin's own metadata (every component and parameter with icon, GUID, inputs, outputs, defaults), and **screenshots** of the canvas and viewport of every example.
  - **19 example definitions** in `examples/` (one per plan generator and `end-to-end.gh`), built and saved by the headless harness.
  - **`sync-docs`** project skill, a **local Yak build** (`scripts/package-yak.ps1`, `bemgen-<version>-rh8_19-win.yak`, nothing published), and the **MIT** `LICENSE` of Environmental Systems Lab.
- **Choices beyond D-115:**
  - The developer part is assembled at build time into a staging folder; its links that point outside `docs/` are rewritten to GitHub `main` and are not checked by `mkdocs build --strict`.
  - The build fails if the generated component reference is missing, unless `-AllowMissingReference` is passed.
  - The examples feed several floors into one input through Grasshopper's *Merge*, because Grasshopper ignores repeated wires from one output to one input.
  - The screenshots are captured by script inside Rhino; no screen control was needed.
  - The plugin version is read from the `.gha` assembly itself, so that Yak can inspect and load it (`bcc3968`).
- **The Grasshopper freeze found in S9.** BEMGen's Goo types had no public parameterless constructor. `GH_Param<T>.TypeName` and `InstantiateT` call `Activator.CreateInstance`, which threw, and Grasshopper's `Tracing.Assert` opened a modal breakpoint dialog that blocked Rhino: on a wire of the wrong type, on the "Data conversion failed" message, and on component help, in every released version up to v0.9.1. Fixed by public parameterless constructors and null-safe empty instances (`d8e0650`, `19c8e2b`); the smoke check now reads every parameter's type name, wires a plan into an aggregator's floors input, and fails when an expected runtime error is missing (`a3398d8`, `f4ed7a2`, `c86746d`).
- **Checks** (controller, on `main` at `19c8e2b`): `scripts/verify.ps1` passed with 0 warnings (346 core, 518 generator, 1573 integration, and 635 export tests on `net8.0`); `scripts/docs-site/build.ps1` with a fresh virtual environment from `requirements.txt` printed `DOCS BUILD PASSED` (`mkdocs --strict`); all 12 `scripts/rhino-smoke` specs ran in Rhino 8.25.25314.11001 headless with every *Validate* True, 0 exceptions, 0 missing components, 0 expected errors missing, and runtime errors only in the error scenarios, including the new one that wires a plan into the aggregator's floors input and requires `Data conversion failed from Plan to Floor`; all 19 example definitions reopen and solve (*Validate* True 19 of 19, 0 errors, 0 warnings).
- **Open for a person (D-058):** open the examples in Rhino 8 and look at the canvas and the viewport (window fills may show transparency-sorting artefacts); drag the `.yak` onto Rhino 8; confirm that a wrong-type wire shows only the conversion error and no dialog; the toolbar look of the icons; and a first EnergyPlus run once a weather file and outputs are chosen (D-112).

### D-117 — The docs site moves to a public repository and is deployed to GitHub Pages

- **Date:** 2026-10-03 · **Decided by:** Cheng Xuan Li (the move, public, GitHub Pages); controller (the plan and its defaults, Provisional until the owner answers the plan's questions) · **Status:** Accepted · **Supersedes:** D-115 in part (a site served on localhost only, never published, kept in this repository) · Superseded in part by D-118 (repository name, developer part, distribution)
- The MkDocs site leaves this repository for a separate public repository, proposed as `EnvironmentalSystemsLab/BEMGen-docs`, and is deployed to GitHub Pages from GitHub Actions. It is moved, not copied: `docs-site/`, `mkdocs.yml`, and `scripts/docs-site/` are removed here once the new site is live. An agent working in the new repository does the import and the deployment.
- Because BEMGen is private:
  - the public site cannot check out or link into BEMGen;
  - by default its developer part is not published, and the developer docs stay in `docs/` here;
  - the generated reference, icons, and screenshots are still made in Rhino from a BEMGen checkout, now through a docs export (`scripts/docs-export/`), and committed in the docs repository.
- `sync-docs` is split. BEMGen's skill checks the developer docs and says when the public site must follow; the docs repository's skill checks the user site against the plugin.
- Plan, owner questions with defaults, and handover material: [docs site move](../plans/2026-10-03-docs-site-move.md). The Yak package stays unpublished (D-115).

### D-118 — Docs move: the owner's answers; the developer part and the release files are public; v1.0.1

- **Date:** 2026-10-03 · **Decided by:** Cheng Xuan Li (answers 1 to 6); controller (the order of the steps and version 1.0.1, Provisional) · **Status:** Accepted · **Supersedes:** D-117 in part (repository name, developer part not published); D-115 in part (release files not published) · Superseded in part by D-119 (redaction scope)
- **Repository:** `energy-atlas/BEMGen-docs`, deployed to `https://energy-atlas.github.io/BEMGen-docs/` from GitHub Actions; MIT, with a fresh history.
- **Developer part is public.** `docs/`, `GLOBAL.md`, and `AGENTS.md` stay the sources here and are published through the docs export (`scripts/docs-export/`). Because BEMGen stays private:
  - their links to source files become plain paths;
  - e-mail addresses and local paths are redacted from the published copy only, and every redaction is listed;
  - the log here is not rewritten.
- **Typologies page:** approved by the owner for publication as it is.
- **Decision numbers** are removed from component, parameter, input, and output descriptions (text only; GUIDs unchanged), since Grasshopper users and the public reference see them.
- **Release files** are published on the docs repository's GitHub Releases for each version: the `.gha` with its libraries as a zip, the `.yak`, the example definitions as a zip, and checksums (`scripts/package-release.ps1`). The Yak package server stays unused.
- **Order:** BEMGen builds the export, the release script, and the removal of the site as version 1.0.1; then the docs repository's agent imports, deploys, and releases `v1.0.1`. Plan: [docs site move](../plans/2026-10-03-docs-site-move.md), now Approved.

### D-119 — Docs move, BEMGen side done; v1.0.1

- **Date:** 2026-10-03 · **Decided by:** controller (D-111, D-117, D-118) · **Status:** Provisional · **Supersedes:** D-118 in part (redaction scope)
- Step B of the [docs site move](../plans/2026-10-03-docs-site-move.md) is complete as version 1.0.1, tag `v1.0.1`. It was built on `feature/docs-move` and reviewed by a second agent before the merge. Step C, the import, deployment, and `v1.0.1` release in `energy-atlas/BEMGen-docs`, goes to the docs repository's agent with the [handover](../plans/2026-10-03-docs-site-move/HANDOVER.md).
- **Delivered:**
  - Decision and ADR numbers removed from every user-visible string in `src/Lod.Grasshopper` (component, parameter, input, and output descriptions, and the components' own messages). The text is otherwise unchanged, and no GUID changed.
  - `scripts/docs-export/`:
    - the two Rhino specs, moved from `scripts/docs-site/`; the screenshots now go into the export;
    - `developer_pages.py` with its unit test;
    - `export.ps1`, which writes the export folder its README describes.
  - `scripts/package-release.ps1`: the plugin zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`, built only from a clean commit tagged `v<version>`. The zips use forward-slash entries.
  - The plugin's contact link and the Yak manifest's URL now point to the public site.
  - Removed: `docs-site/`, `mkdocs.yml`, the rest of `scripts/docs-site/`, and their ignore entries.
  - BEMGen's `sync-docs` replaced by the version that checks the sources here and says when the public site must follow.
  - README, AGENTS, and the other files that mentioned the old site updated.
- **Redaction scope (supersedes D-118 in part).** The published copy redacts e-mail addresses and user-profile paths (`C:\Users\<name>`, also written `C:/Users/...` and `/c/Users/...`). Lab paths such as `D:\BEMGen` stay, because they are instructions for the lab machine and not personal data. Today the only redaction is the commit identity's address in D-050.
- **Review findings fixed before the merge:**
  - the redaction scope above;
  - portable zips, and refusing untagged or dirty release builds;
  - the docs repository's skill wording, and the private repository's URL in the shipped plugin;
  - fences closed only by a matching run, angle-bracket targets and single-quoted titles in links, and code text for links whose text is the file's stem;
  - an export folder inside any git repository refused, and the developer-page link check run before Rhino starts;
  - wording in the handover and the prompt.
- **Checks:**
  - `scripts/verify.ps1` passed with 0 warnings: 346 core, 518 generator, 1573 integration, and 635 export tests.
  - All 12 `scripts/rhino-smoke` specs passed in Rhino 8.25.25314.11001 on `4ad721a`, with every *Validate* True and runtime errors only in the error scenarios. All 19 examples solve.
  - A trial export on `4ad721a` gave 64 icons, 57 screenshots, 54 developer pages, 0 description gaps, one redaction, and no decision number left in the component metadata.
  - The developer-page unit tests pass (8).
- **Open:**
  - Diagnostic messages from `Lod.Core`, `Lod.Generators`, and `Lod.Export` still cite decision numbers in 14 strings, and these reach Grasshopper users as runtime messages. The IDF header comment cites D-112. Both are outside D-118's literal scope and are left for the owner.
  - The example definitions still carry the 1.0.0 build stamp. They solve with 1.0.1 and were not rebuilt.

### D-120 — Enum inputs: values in the right-click menu and a dropdown on Extract parameter

- **Date:** 2026-10-04 · **Decided by:** Cheng Xuan Li (the two ways to choose a value, the branch `features/dropdown-enums`); controller (the realisation, Provisional) · **Status:** Accepted
- Why: five inputs took an enum name as typed text, and only their descriptions listed the valid names: *Schedule* *Kind* and *First Day*, *Load* *Type* and *Basis*, and *Program Preset* *Space Type*. The owner asked for two things. *Extract parameter* on such an input should give a dropdown component. Its right-click menu should offer the enum's values next to Grasshopper's own items.
- Built from the [enum inputs design note](../plans/2026-10-04-dropdown-enums.md) (now Done) as D-111 sets out, test-first against a new headless Rhino spec, and reviewed by a second agent before the merge.
- **Realisation (controller, pending the owner's reading):**
  - The five inputs are `EnumParameter<TEnum>` (`src/Lod.Grasshopper/Parameters/EnumParameter.cs`), an internal generic subclass of Grasshopper's `Param_String`.
  - The data stays text. Panels, wires, saved definitions, and the components' case-insensitive parsing work as before.
  - The class keeps the *Text* parameter's `ComponentGuid`, icon, and type name. Grasshopper never registers it, because it is internal and generic.
  - No component GUID, input name, nickname, access, optional flag, or default changed. The descriptions add one sentence on how to choose a value.
  - **Right-click menu.** The names follow Grasshopper's *Set Text*, *Set Multiple Texts*, and *Manage Text collection* items, in declaration order. The current value is ticked, read as the parser reads it. The names are disabled while the input has a source. A click is one undo step.
  - **Extract parameter.** It places a *Value List* in dropdown mode left of the input, centred on it, labelled with its name, and wired into it.
    - The list has every name in declaration order, each with its quoted name as the expression, so it outputs text. It is selected on the current value, or on the first name when the value is not one.
    - Its description is the input's, without the note.
    - It moves past any object it would overlap, away from that object, so the dropdowns of neighbouring inputs keep their order.
    - The list and its wire are one undo record, built from Grasshopper's add-object and wire actions.
- **Tests.**
  - `scripts/rhino-smoke/specs/enum-inputs.py` makes 179 checks, among them: the menu, a click, undo and redo of a click and of the extraction, the dropdown's items, selection, placement, and result, the disabled state with a source, no registered enum parameter, adjacent dropdowns in both orders, and a save and reopen.
  - `run.ps1` now counts a line starting with `CHECK FAILED` as a failure of its spec.
- **Checks** (controller, on `a4ecc1a`):
  - `scripts/verify.ps1` passed with 0 warnings: 346 core, 518 generator, 1573 integration, and 635 export tests. No test changed, because `Lod.Grasshopper` has no `dotnet test` project.
  - All 13 `scripts/rhino-smoke` specs ran in Rhino 8.25.25314.11001 with every *Validate* True, no exceptions, and no failed checks. Runtime errors came only in the error scenarios. All 19 examples solve.
- **Open:**
  - A person checks the menu and the dropdown on the canvas ([smoke test](../development/grasshopper-smoke-test.md)).
  - The public site's component reference needs a new export, since the five descriptions and the parameter class changed.
  - The version for this change is the owner's choice.

### D-121 — Version 1.0.2: the enum inputs, released with a docs export

- **Date:** 2026-10-05 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- Version 1.0.2, tag `v1.0.2`, releases the enum inputs (D-120). The owner reviewed and approved them, and they were merged into `main` and pushed.
- The release goes on the docs repository's GitHub Releases, as D-118 sets out, with the files of `scripts/package-release.ps1` built from the tagged commit:
  - the plugin zip, with `BEMGen.gha` and its libraries;
  - the `.yak`;
  - the examples zip;
  - `SHA256SUMS.txt`.
- A docs export of `v1.0.2` (`scripts/docs-export/export.ps1`) carries the changed input descriptions to the public site's component reference. The docs repository imports it.
- The example definitions are not rebuilt. They still carry the 1.0.0 build stamp and solve with 1.0.2 (D-119).

### D-123 — Conditioned Merge, and joined pieces for both merge simplifiers

- **Date:** 2026-10-06 · **Decided by:** Cheng Xuan Li (a new plan simplifier that merges conditioned and unconditioned zones separately; a boolean on both merge simplifiers for separate pieces, default false; the branch `feature/conditioned-merge`); controller (the realisation, Provisional) · **Status:** Provisional — pending the owner's reading, not merged
- Numbered D-123 because the unmerged S10 branch holds D-122. Whichever branch merges second rebases its log entry.
- **Why:**
  - No plan simplifier removed the semantic partitions inside conditioned space while keeping its boundary with unconditioned space. *Perimeter Core* and *Single Zone per Floor* enlarge the conditioned floor area wherever they cover a stair.
  - *Semantic Merge* gives one zone per connected piece of a space type. Stairs and stair bays cut floors into many pieces, so "one zone per class" needs zones made of several pieces.
  - The owner asked for both modes on both merge simplifiers.
- Built from the [design note](../plans/2026-10-06-conditioned-merge.md) (now Done) as D-111 sets out: test-first on the branch, reviewed by a second agent twice (core, then Grasshopper), with every finding fixed.
- **Realisation (controller, pending the owner's reading):**
  - **Joined pieces.** `SemanticMerge(tolerances, joinPieces)` and the new `ConditionedMerge(tolerances, joinPieces)` share one grouping. Zones are connected only through a shared wall.
    - *Join Pieces* false (the default) gives one zone per connected piece, which is `SemanticMerge` unchanged.
    - True gives one zone per class on the floor, made of all its pieces.
    - Provenance records `JoinPieces=true` only when true, so every existing output is byte-identical.
  - **Conditioned Merge (Z1c).** The classes are conditioned and unconditioned, decided only by whether the source's program has a thermostat.
    - The targets are `Conditioned-n`, then `Unconditioned-n`, numbered in plan order. Each takes the space type its sources share, or `Mixed`.
    - Aggregation is the existing rule (ADR-005, ADR-007, D-047).
    - It keeps conditioned floor area exactly in both modes. With the example presets, joined, it gives at most two zones per floor on every family.
  - **Floor zones of several pieces.** A floor zone may have several parts at one elevation:
    - `TargetZone.Pieces`, and `LayoutSurfaceBuilder` builds every piece under one ID, with floors and ceilings `F1…` and `C1…` when a zone has several pieces;
    - `OverlapMapper`, `Storeys`, `SingleZoneMerge`, and the overlap validation read every part;
    - new error codes `TouchingPieces` and `DuplicateZoneId`; a target without pieces is `InvalidParameter`;
    - the IDF writes one `Zone` with every piece's surfaces, and *Convert2BEM* gives one closed Brep per part;
    - previews draw same-storey pieces as separate solids; a Boolean union had fused pieces meeting at a corner.
  - **Components.**
    - *Semantic Merge* gains the input *Join Pieces* (J, default false) before *Preview Location*. Its GUID is unchanged.
    - *Conditioned Merge* (Z1c, `4bf2f852-144c-4afb-8dcc-8c016787f571`) is in *3 Simplify*, with the same inputs and its own icon.
    - **Old files.** A *Semantic Merge* saved before *Join Pieces* is read with *Join Pieces* at its default, keeping its *Preview Location* data and wires. Without this, five shipped examples reopened with no output and no message, which D-064 does not intend. A fixture saved by the pre-change plugin keeps this tested.
  - **Research brief §8.** It gains Z1c and the *Join Pieces* variant of Z1, and a table of what each level does to conditioned floor area (GLOBAL.md scientific rule 7).
- **Checks** (on `0cebbc6`):
  - `scripts/verify.ps1` passed with 0 warnings: 412 core, 518 generator, 2620 integration, and 1024 export tests.
    - The integration and export tests run every family × aggregator × new mode, at the default placement and rotated, and validate with no warnings. Conditioned floor area is asserted exact.
    - No existing snapshot or assertion changed; the snapshot diff against `main` is additions only.
  - All 14 `scripts/rhino-smoke` specs ran in Rhino 8.25.25314.11001 on `0cebbc6` with every *Validate* True, no exceptions, no failed checks, and runtime errors only in the error scenarios. They include the new `merge-pieces` spec (four modes × four aggregators on the stair-bay bar, piece previews and *Convert2BEM* Breps per piece on three families, the pre-change fixture, a save and reopen, the *Join Pieces* descriptions) and the 19 examples, each with exactly one *Validate* True.
- **Open:**
  - **For a person in Rhino 8:** the order of *3 Simplify* (nothing in BEMGen sets it), the look of *Conditioned Merge* and its icon, the piece previews in the viewport, and a pre-change file with a wired *Preview Location* on screen.
  - **Saved tooltips.** Definitions saved with this branch's builds before `168f583` keep the short *Join Pieces* tooltip, because Grasshopper restores descriptions from the file. No released file is affected.
  - **Out of scope:** a building-level counterpart, and the example definitions.
  - **The owner's choices:** the merge, the version and tag, and the docs export that follows them.

### D-124 — Program mix by floor-area share; infiltration becomes a building-level input

- **Date:** 2026-10-06 · **Decided by:** Cheng Xuan Li. The owner decided the operation and its rules:
  - a component that mixes presets with weights, where a weight is a floor-area share;
  - absolute loads added raw;
  - setpoints mixed as zone merges mix them;
  - the space-type default and the WWR weighted mean;
  - infiltration moved wholly to the building level (option (a)), with an illustrative 0.3 ACH;
  - the branch `feature/program-mix`.

  The controller decided the realisation, which is Provisional ([ADR-017](ADR-017-program-mix-and-building-infiltration.md)). · **Status:** Provisional, pending the owner's reading; not merged.
- **Numbering.** D-122 (S10 atlas) and D-123 (Conditioned Merge) are on other unmerged branches. Whichever branch merges later rebases its log entry. `ProgramPreset.Source` is the same cherry-picked commit on this branch and on S10.
- **Why.** Mixing presets raised two problems:
  - loads in different unit bases;
  - weights that depend on geometry a preset does not know, which today is infiltration per exterior wall area.
- **How it was built.** From the [design note](../plans/2026-10-06-program-mix.md) (now Done), as D-111 sets out: test-first, then reviewed by a second agent twice, first the core and then the Grasshopper side. The core review found a blocker: one input's absolute occupancy diluted another input's per-person load about 50-fold. It and every other finding were fixed.
- **Realisation (controller, pending the owner's reading):**
  - **Infiltration**
    - `LoadType.Infiltration` and `LoadBasis.PerExteriorWallArea` leave programs. The aggregator loses its exterior-wall path, and the example presets lose their rates (mall 0.8, lobby 0.6, retail 0.5, operating theatre 0.1, the rest 0.3 ACH).
    - `EnvelopePreset` carries `Infiltration`: a rate in one basis (per exterior surface area, per exterior wall area, or air changes per hour) with a fraction schedule. The example envelope uses 0.3 ACH, always on.
    - *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` per zone, in the native EnergyPlus method. *Convert2BEM* outputs the infiltration and each zone's design flow (outputs 18–21), from `ZoneInfiltration`.
    - EnergyPlus 26.2 counts the exterior area as outdoor walls with their windows, roofs, and exposed floors, but not the ground or adiabatic surfaces. That matches what BEMGen writes.
    - Zone merges no longer aggregate infiltration; it follows each zone's own surfaces.
  - **`ProgramMix.Mix`** runs the existing zone merge on a virtual zone of unit floor area:
    - densities and ACH are weighted;
    - per-person loads are weighted by occupants;
    - absolutes are summed raw;
    - schedules are weighted by magnitude;
    - setpoints are averaged over the conditioned inputs, and the result is conditioned if any input is.
  - **Mix rules.**
    - Weights must be finite and greater than 0; they are normalised.
    - Absolute occupancy in any input beside a per-person load in any input is an error.
    - The space type and the WWR follow the owner's defaults.
    - Provenance holds `Input.k` pairs (name, given weight, normalised weight) and nests each input's own source.
  - **Equivalence.** A mix with weights 0.7/0.3 equals *Single Zone per Floor* on zones of 70 and 30 m², in every load, every hour of every schedule, and every setpoint.
  - **Components.**
    - *Mix Programs* (`744378f8-861d-4e6d-bff4-68c7fe2b62c1`) is new.
    - *Envelope Preset* gains three infiltration inputs, and *Convert2BEM* four outputs.
    - The default preset components lose their infiltration inputs.
    - *Load* explains that infiltration belongs on the envelope.
    - No existing GUID changed. The 19 examples were rebuilt.
  - **Research docs.** The research brief, `program-presets.md`, and `envelope-presets.md` record infiltration as an envelope input and the equivalence of a mix with a zone merge (GLOBAL.md scientific rule 7).
- **Checks** (on `7c4a7d0` and the record commit after it):
  - `scripts/verify.ps1` passed with 0 warnings: 417 core, 518 generator, 1624 integration, and 705 export tests.
  - 30 snapshots changed, all because of infiltration:
    - 25 lose only their infiltration lines;
    - 5 IDF snapshots gain the header line;
    - 4 of those IDF snapshots also share the envelope's single schedule instead of writing one per zone.
  - All 14 `scripts/rhino-smoke` specs ran in Rhino 8.25.25314.11001 with every *Validate* True, no exceptions, and no failed checks. The new `program-mix` spec has 17 scenarios and 76 checks: hand values, the cross-input occupancy error, the envelope bases against the Rhino geometry, and *Convert2IDF*. All 19 rebuilt examples solved, each with one *Validate* True.
  - The IDD check against the EnergyPlus 25.2.0 IDD: 579 files, all three infiltration methods, 0 problems.
- **Open.**
  - **For a person in Rhino 8:** the *Mix Programs* icon, the layouts of *Envelope Preset* and *Convert2BEM*, and the rebuilt examples in the editor.
  - **Old definitions** open with Grasshopper's IO dialog. It drops the presets' saved infiltration values, which the release notes must state.
  - **Integration with S10:** the atlas branch's infiltration handling becomes obsolete when both merge.
  - **The owner's choices:** the merge order of the three branches, the version and tag, and the docs export.

### D-125 — Version 1.1.0: Conditioned Merge and the program mix, released with a docs export

- **Date:** 2026-10-07 · **Decided by:** Cheng Xuan Li (approved the two stages; the merge, the tag, the push, and the release, on 2026-10-07) · **Status:** Accepted
- **Version.** 1.1.0, tag `v1.1.0`. It is a minor version, chosen over 2.0.0 because D-064 waives backward compatibility: the new inputs and outputs and the infiltration that left the presets need no major version.
- **What it merges.** `feature/conditioned-merge` (D-123) and `feature/program-mix` (D-124, [ADR-017](ADR-017-program-mix-and-building-infiltration.md)), rebased into one linear history (D-004), Conditioned Merge first. Their entries stay as written, with their per-branch counts and "not merged"; this entry gives what holds for the merged result.
- **The merged facts** that D-123 and D-124 give only per branch:
  - `scripts/verify.ps1` passed with 0 warnings on the integrated candidate: 484 core, 518 generator, 2695 integration, and 1148 export tests.
  - **Snapshots.** Beyond D-124's 30, the four Conditioned Merge snapshots were regenerated for infiltration:
    - three floor snapshots lose their infiltration load lines;
    - the stair-bay bar's IDF snapshot gains the header line and the envelope's schedule.
  - **IDD check.** 1016 files against the EnergyPlus 25.2.0 IDD, 0 problems, with all three infiltration methods covered ([convert2idf.md](../architecture/convert2idf.md#idd-check)).
  - **IDF names.** The export tests had named the IDFs of the joined merge modes after the simplifier, as in `ConditionedMerge:JoinPieces`. On Windows a colon makes the rest of the name an alternate data stream, so 288 files were never listed and never checked. `IdfOut.FileName` now replaces every character a file name cannot hold with `_`, and `IdfOutTests` tests it.
  - **Zones of several pieces take the envelope's infiltration over every piece:** the outdoor walls with their windows, roofs, and exposed floors of all pieces, or the volume. This is tested in the export tests, in the integration matrices that run every merge mode through every infiltration basis and the program mixes, and in the `merge-pieces` smoke spec; the architecture documents and the research brief state it.
- **Smoke result.** The 19 example definitions were rebuilt with the 1.1.0 plugin (`BEMGEN_EXAMPLES_WRITE=1`): all reopen and solve with one *Validate* True each, no warnings or errors. All 15 `scripts/rhino-smoke` specs ran in Rhino 8.25.25314.11001 on the candidate, with every *Validate* True, no exceptions, no failed checks, and runtime errors only in the error scenarios; `merge-pieces` (16 *Validate* True, with the multi-piece infiltration checks) and `program-mix` (17 scenarios) included. In the full run `hub-arms` stalled inside one scenario and wrote no result; run again on its own it passed in 45 s with its usual 54 scenarios and 324 *Validate* True.
- **What follows:**
  - The release goes on the docs repository's GitHub Releases, as D-118 sets out, with the files of `scripts/package-release.ps1` built from the tagged commit: the plugin zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`.
  - A docs export of `v1.1.0` (`scripts/docs-export/export.ps1`) carries the new components, inputs, outputs, and the changed descriptions to the public site. The docs repository imports it and runs its own `sync-docs`.
  - The release notes state that definitions saved before D-124 open with Grasshopper's IO dialog, which drops the presets' saved infiltration values (D-124).
- **Open:**
  - **The S10 atlas branch (D-122)** is not in this release. When it merges, its infiltration handling must be removed, because infiltration is no longer a program input, and its log entry rebased.
  - **For a person in Rhino 8:** the checks of the [smoke test](../development/grasshopper-smoke-test.md) that only a person can make:
    - the icons of *Conditioned Merge* and *Mix Programs*, the order of *3 Simplify*, and the piece previews in the viewport;
    - the layouts of *Envelope Preset* and *Convert2BEM*;
    - a pre-change file with a wired *Preview Location*, the rebuilt examples in the editor, and the install from the release.

### D-126 — Program presets from program JSON 2.0.0; the atlas fetch components retired

- **Date:** 2026-10-07 · **Decided by:** Cheng Xuan Li. The owner decided:
  - to retire the S10 atlas fetch components (D-122) without backward compatibility;
  - one parser component that takes the JSON text, with inputs that complete or override it: a WWR with an ordinary default (0.4), loads the JSON lacks (such as ventilation), each thermostat side and its schedule, the activity schedule, and the people fractions;
  - to extend the program model to hold what the contract describes: a per-dwelling-unit basis; an activity schedule and people fractions; two lighting loads (end uses); two setpoint schedules, each with its own on/off; a hot-water target and an inlet temperature; and heat fractions of power loads;
  - per-dwelling loads merge weighted by dwelling count, after the conflict with GLOBAL.md scientific rule 1 was raised (area weighting would not conserve installed power);
  - shared services are not added;
  - a merge of a sensible fraction that mixes a number with `autocalculate` gives `autocalculate` with a warning, and the other merge rules proposed stand;
  - an override load replaces the JSON loads of the same type and end use, or is added;
  - *Year* defaults to 2007, with a *Holidays* input, and a leap year is an error;
  - design-day rules are checked and not used;
  - the old branch is tagged `archive/archetype-data`, then deleted;
  - a JSON Schema library is bundled to validate the JSON;
  - the two atlas schemas and the Medium Office example may be committed;
  - one stage for version 1.2.0;
  - the build runs without supervision, with a stop line before the merge, the tag, the push, the docs export, and the release;
  - the agent may close Rhino when it must.

  The controller decided the realisation, which is Provisional ([ADR-018](ADR-018-program-json-and-extended-programs.md)). · **Status:** Provisional, pending the owner's reading; not merged. · **Supersedes:** D-122 (it exists only in the archive tag) · **Supersedes in part:** D-047, as to one load per type and basis (now per type, end use, and basis)
- **Numbering.** D-122 (the S10 atlas stage) and its ADR-016 exist only in the tag `archive/archetype-data` (`cf88cee`); the numbers stay unused in this log. The branch was never on `origin`. Part A of the stage archived it: an annotated local tag, the worktree removed, the branch deleted.
- **Retired identities, never to be reused:**
  - the components *Atlas Snapshot* `c231969e-a062-4f0b-a2b4-45ca60b7cc3e`, *Atlas Query* `ec2037f0-b14e-432b-a907-23a6e4566e94`, and *Atlas Program Preset* `43b5b5c4-b180-4be5-94ce-74d982640fd9`;
  - the parameter *Atlas Snapshot* `dbf8128f-fdd3-4f36-a941-89d849668161`;
  - the examples `atlas-office-plate.gh` and `atlas-explorer.gh`.

  Nothing of the atlas code was on `main` except `ProgramPreset.Source`, which stays: the JSON preset fills it. From the archive only the ruleset expansion with its calendar and the strict JSON reading were ported, adapted to the 2.0.0 shape.
- **How it was built.** From the [design note](../plans/2026-10-07-program-json.md) (Done), as D-111 sets out: test-first on `feature/program-json` in the worktree `D:\worktrees\program-json`, the library in parallel on a second branch, then reviewed by a second agent. The note's Build log holds the findings and the review.
- **Realisation (controller, pending the owner's reading)** — the details are in ADR-018, [program-json.md](../architecture/program-json.md), and the research documents:
  - **Model.** `LoadBasis.PerDwellingUnit` with a dwelling count on every zone (1 per generated dwelling-unit zone, Σ fᵢ·Nᵢ after a merge); `LoadDefinition.EndUse` with a program holding one load per type, end use, and basis; `HeatFractions` (radiant, latent, lost, visible, return air) on lighting and equipment, with a non-zero value in a field the EnergyPlus object lacks an error; `PeopleProperties` (activity schedule, radiant fraction, sensible fraction or `autocalculate`); a `Thermostat` with optional heating and cooling sides; `WaterTemperatures` (target and inlet); `ScheduleCalendar` (a non-leap year and its holidays) with `CalendarMismatch` for programs on different calendars. The defaults are the values the IDF writer used before, so BEMGen's own presets are unchanged.
  - **Aggregation.** The zone-merge rule value* = Q*/B* with the dwelling count as a basis quantity; heat fractions weighted by the transferred magnitude; the activity weighted every hour by the transferred scheduled occupants; the people fractions by design occupants; the hot-water target and inlet every hour by the transferred scheduled flow; each thermostat side over the sources that have it; a merge whose heating exceeds its cooling is an error. *Mix Programs* inherits all of it (a weight stands for a share of dwellings as well as of floor area).
  - **Library.** `Lod.ProgramJson` (a `net7.0` library): strict parse, mode, schema (JsonSchema.Net 7.2.3, MIT; the program schema embedded byte for byte), the contract's checks, expansion to 8760 values, mapping to a preset. A rule starting on 29 February starts on 1 March in a non-leap year, and one ending on it ends on 28 February, each with a warning (the contract is silent; reported to the atlas).
  - **Components.** *Program JSON* (`abb0aeb9-5a9f-40ff-b3a1-bb125cfb675c`, `PJson`, panel *1 Program*, 14 inputs and 5 outputs) is new; *Load*, *Schedule*, *Program Preset*, and the default preset components gain appended inputs; *Convert2BEM* gains appended outputs 22 to 30. No existing GUID changed. The example `examples/program-json-office.gh` and the smoke spec `program-json` are new.
  - **Export.** Heat fractions, per-dwelling levels (written as absolute levels), people properties, water temperatures, single-sided thermostats (`SingleHeating` and `SingleCooling`), and the run period from the calendar (2007 starting on a Monday without one).
  - **Validation.** The conservation checks run per load component and for the building's dwelling count; `PerDwellingLoads` and `Calendar` are new checks; the aggregation records are required for the new derived fields.
  - **New tolerance.** `ToleranceSettings.AbsoluteFraction` (1e-9), for sums of fractions ([ADR-004](ADR-004-tolerances.md) amended).
  - **Research documents** (GLOBAL.md scientific rule 7): the research brief and [program-presets.md](../research/program-presets.md) record the new rules and defaults.
- **Snapshots changed**, each with its reason (none was updated to make a test pass):
  - 28 text reports gain only lines for the new fields; a script confirmed that removing those lines restores the originals exactly;
  - 6 IDF snapshots gain the calendar header line, and their `RunPeriod` year moves from 2018 to 2007, both years starting on a Monday;
  - no IDF snapshot had a water use, so the predicted change of the water-use temperature fields did not occur in snapshots; the fields are covered by the export tests and the IDD check.
- **Two regressions found in Rhino and fixed:**
  - Grasshopper's reader opens its IO dialog for every current parameter that has no saved chunk, so all 19 examples saved with 1.1.0 stalled on reopening. The components now set the appended parameters aside while the saved ones are read, which keeps saved values and wires; the examples spec reads each archive first and fails instead of stalling.
  - Definitions saved before infiltration left the programs have trailing *Infiltration* inputs at the positions of the new *Heating On* and *Cooling On*, and were read into them. Trailing saved parameters whose name differs are no longer counted as saved.
- **Review fixes** (after the realisation above, `4d65af3` and `36b55a2`):
  - a mix with occupancy in more than one basis and a per-person load, or different people properties among the inputs with occupants, is the error `MixedOccupancyBases` (the virtual zone of a mix would weight them by a wrong split);
  - equal setpoints merged over different sources stay exactly equal, so equal heating and cooling setpoints no longer cross by rounding; `Thermostat` and `WaterTemperatures` allow `AbsoluteSchedule` of slack, as the importer does;
  - end uses are keys ignoring case, so an override *End Use* `Lighting` replaces the JSON's `lighting`.
  - concurrent schema evaluations of the one shared schema instance could report an invalid document as valid (a flaky test that failed about one run in eight); evaluations are now serialised (`fe03c32`), and a test on 16 threads that failed 15 of 15 runs before passes 15 of 15.
- **Checks** (on `fe03c32`, the last code commit, and the documentation after it):
  - `scripts/verify.ps1` passed with 0 warnings: 614 core, 518 generator, 160 `Lod.ProgramJson`, 2698 integration, and 1219 export tests.
  - The IDD check against the EnergyPlus 25.2.0 template IDD: 1073 files, 0 problems, with `SingleHeating`, `SingleCooling`, the water-use temperatures, and the people sensible fraction covered.
  - All 16 `scripts/rhino-smoke` specs ran once each in Rhino 8.25.25314.11001 on .NET 8.0.31, every one done with no failed checks. `program-json` has 16 scenarios and 57 checks. The examples spec reopened 20 of 20 definitions, each with *Validate* True. Earlier in the build, one examples run stalled on the IO dialog (the first regression below) and Rhino was ended under the owner's permission.
  - A trial docs export wrote version 1.2.0 with 60 screenshots and 0 description gaps.
  - The fresh-clone gate: a clean clone of `feature/program-json` at `3d7e19c` passed `scripts/verify.ps1` with the same counts, the atlas fixtures byte-exact.
- **Contract gaps reported to the atlas, not worked around:**
  1. 29 February in a non-leap model year is unspecified.
  2. With a non-empty holiday list, defaulted schedules without a `Hol` rule fall to the prepended `Default` rule: the Medium Office's lighting and equipment are off on holidays while its occupancy keeps its `Default` value.
  3. "Heating does not exceed cooling in the relevant active periods" is vague; BEMGen checks every hour in which both sides are on.
  4. The annual schedule's `allOf` constrains `rules`, which annual schedules lack (harmless).
  5. Design-day coverage is required by the checks, though a consumer without sizing never uses it.
- **Open.**
  - **For a person in Rhino 8:** the canvas look of `program-json-office.gh` and of the *Program JSON* icon, a definition saved with 1.1.0 opened in the editor (the headless run proved that it reads without the IO dialog, not how it looks), and the install from the `.yak`.
  - **The owner's choices:** the merge, the version and tag (`v1.2.0`), the push, the docs export, and the release. The stage stops before all of them (D-111). Only `program-json-office.gh` was rebuilt; the 19 other examples were reopened, not rebuilt.
  - **Pending the owner's reading:** ADR-018 and the design note's controller choices (the end-use default names, heat fractions in a field EnergyPlus lacks as an error, the 29 February rule, the 64 MiB size bound, the dwelling counts after a split, the water temperatures 60 and 10 °C, a crossed merge as an error, the order of the *Convert2BEM* additions).
  - **Known limits:** shared services are not modelled; design-day profiles are not used (the IDF gives design days the Sunday profile); a schema error lists every failing branch, so one wrong rule can give several messages.

### D-127 — Version 1.2.0: program JSON, released with a docs export

- **Date:** 2026-10-09 · **Decided by:** Cheng Xuan Li (asked for the merge, the tag `v1.2.0`, and the release on the docs site on 2026-10-09) · **Status:** Accepted
- **Version.** 1.2.0, tag `v1.2.0`, a minor version as D-125 reasons: D-064 waives backward compatibility, and the stage changed no GUID.
- **What it merges.** `feature/program-json` (D-126, [ADR-018](ADR-018-program-json-and-extended-programs.md)), fast-forwarded into `main` at `79e3adf`; it was 39 commits ahead of `0d301c5` and none behind. D-126 stays as written, with its "not merged"; this entry gives what holds for `main`.
- **Checks on `main`:**
  - `scripts/verify.ps1` passed with 0 warnings before the merge: 614 core, 518 generator, 160 `Lod.ProgramJson`, 2698 integration, and 1219 export tests, the counts D-126 gives.
  - **Examples.** All 20 example definitions were rebuilt with the 1.2.0 plugin at `79e3adf` (`BEMGEN_EXAMPLES_WRITE=1`, Rhino 8.25.25314.11001), as `examples/README.md` asks at a release: every one reopened and solved with one *Validate* True, no warnings, errors, or exceptions. D-126 had rebuilt only `program-json-office.gh`.
  - **Fresh-clone gate.** A clean clone of `main` at `8a64e25` (the rebuilt examples) passed `scripts/verify.ps1` with the same counts.
- **What follows:**
  - the release on the docs repository's GitHub Releases (D-118), with the files of `scripts/package-release.ps1` built from the tagged commit: the plugin zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`;
  - a docs export of `v1.2.0` carries *Program JSON*, the appended inputs and outputs, the new example, and the developer pages to the public site; the docs repository imports it and runs its own `sync-docs`;
  - the release notes say that definitions saved with 1.1.0 open with their values and wires, and that definitions saved before 1.1.0 still lose their presets' infiltration values (D-124).
- **Open:** the items D-126 leaves to a person in Rhino 8 and to the owner's reading (ADR-018 and the design note's controller choices).

### D-130 — A simulation-ready IDF, the experiment outputs, and an EnergyPlus runner

- **Date:** 2026-10-11 · **Decided by:** Cheng Xuan Li (scope, outputs, reference, ground rule, shading, convex split, the runner's rule change, version 1.3.0 without a tag); the realisation by the controller · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading
- **Numbering.** D-128 and D-129 are held by the kept, unmerged branches `feature/program-popup-window` and `feature/program-popup-web` (the owner, 2026-10-11), so this stage takes D-130. Its ADR is [ADR-019](ADR-019-simulation-ready-idf-and-runner.md), the next free number after the archived ADR-016.
- **Supersedes in part:**
  - D-112: the EnergyPlus version 25.x, "EnergyPlus is not run", and "no weather, climates, or output selection";
  - ADR-010: the fixed ground, the monthly meters, and non-convex surfaces left as they are;
  - ADR-009: the empty gaps of a multiplied storey as part of the geometry effect.
- **Refines** D-016: simulation stays outside the pipeline, but the repository can run EnergyPlus. GLOBAL.md gains architecture rule 7.
- **Decided** (design note [2026-10-11-idf-out.md](../plans/2026-10-11-idf-out.md), "Decisions at a glance"):
  1. *Convert2IDF* targets EnergyPlus 26.2.
  2. A *Weather* input takes an `.epw` path: `Site:Location` from its header, with its name and SHA-256 in the header and provenance.
  3. The outputs are the research set of [Experiment outputs](../research/experiment-outputs.md): hourly meters behind heating, cooling, and the total load, written only when used; hourly zone mean air temperature; the summary tables; SQLite; and a case record in the header. That page integrates the owner's specification "Experiment Output Variables" and refines §14 of the research brief:
     - the reference case is *No Simplification* + *Stack* with both heat-transfer options on;
     - EUI is reported per conditioned and per total floor area;
     - the total load is the four facility meters, gas equipment included;
     - peak duration is counted in hours above the reference's percentiles;
     - both load-duration-curve measures are computed;
     - the building temperature is reported over all zones and over conditioned zones;
     - the metrics are computed in `Lod.Simulation`.
  4. **Ground: "indoor minus 2 °C".** The building's floor-area-weighted monthly setpoint minus 2 °C, and 18 °C without a conditioned zone. The F-factor method was preferred but needs a sourced F-factor (D-023), and ISO 13370 was judged more than needed.
  5. **Every non-convex outdoor surface is split** into convex pieces.
  6. **The storeys a multiplied storey stands for cast shadows**, through shading surfaces at their walls, generated at converter level by *Convert2IDF* and *Convert2BEM* (the research brief's Z5 and V4 changed with it).
  7. **EnergyPlus runs only outside the pipeline:** `Lod.Simulation` with opt-in tests (`BEMGEN_ENERGYPLUS`) and the C# tool `scripts/eplus-check`; a Grasshopper run component is deferred.
  8. Finding F1 (slabs between × 1 storeys stay adiabatic under *Stacked Floor Zone Multiplier*) stays a finding.
  9. The version is 1.3.0, with no tag in this stage.
- **Built** on `feature/idf-out` (from `main` `3e46108`), as D-111 sets out:
  - four parts by separate agents (writer, shading, runner, end-to-end set), the first three in parallel worktrees, rebased one after another;
  - a review by a second agent, whose eight findings were fixed or merged;
  - the headless Rhino check;
  - the build log in the design note.
- **Components and interfaces:**
  - *Convert2IDF* gains the input *Weather*, and *Convert2BEM* the output *Shading*. Both are appended, both keep definitions saved with 1.2.0 readable, and no GUID changed.
  - A new library `Lod.Simulation` (`netstandard2.0`, depending only on `Lod.Core`) and its test project.
  - New diagnostics, among them `InvalidWeatherFile`, `NoWeatherFile`, `GroundTemperatureDefault`, `InfiltrationNotWritten`, `WindowBlocksConvexSplit`, and the runner's codes.
- **Checks:**
  - `scripts/verify.ps1` passed with 0 warnings: 629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, and 136 simulation tests, with the 5 opt-in EnergyPlus tests skipped.
  - With `BEMGEN_ENERGYPLUS=D:\EnergyPlusV26-2-0`, the 144 simulation tests passed: 110 EnergyPlus cases, each completed with 0 severe errors and only the expected warning, with zones, areas, end uses, internal loads, and the case record checked.
  - `scripts/eplus-check` passed all 1080 IDFs the export tests write.
  - `scripts/idd-check` against the EnergyPlus 26.2.0 IDD: 1080 files, 0 problems.
  - All 16 rhino-smoke specs passed, and the 20 examples reopened and solved.
  - The fresh-clone gate: a clean clone of `feature/idf-out` at `e84ab84` passed `scripts/verify.ps1` with the same counts and 0 warnings. The tag `v1.3.0` is on the commit that records this gate.
- **Findings:**
  - ADR-010's two items "to verify on the first EnergyPlus run" hold: EnergyPlus uses the stated zone floor area, and the window construction named like its glazing runs.
  - The total load's meters are complete: the end uses sum to it every hour.
  - The floor aggregators conserve area, volume, and hourly internal loads through EnergyPlus.
  - With shading, the enclosed court under the multiplier is within +0.09 % heating and +0.58 % cooling of the reference, against −2.9 % and +4.7 % without.
- **The owner's answers to the build** (2026-10-11):
  - The ground rule stays as it is. The mapping from zone setpoints to ground temperature is fixed, and that is all that is wanted; the values may differ between zonings, which is one of the differences the study characterises.
  - Minimum warm-up days stay 6.
  - The F-factor method, F1, and the run component are set aside for now.
  - The tag `v1.3.0` is set locally. The branch is not merged or pushed while the owner reviews it by hand.
- **Open for a person (D-058):** the *Weather* input and *Shading* output in Rhino, a 1.2.0 definition in the editor, and the toolbar look.

### D-131 — Version 1.3.0: the simulation-ready IDF, released with a docs export

- **Date:** 2026-10-12 · **Decided by:** Cheng Xuan Li (reviewed the branch by hand, then asked for the merge, the push, the docs export, and the release on 2026-10-12) · **Status:** Accepted
- **Version.** 1.3.0, tag `v1.3.0`, a minor version as D-125 reasons: D-064 waives backward compatibility, and the stage changed no GUID. The tag was first set on `2827656` at the owner's request (D-130), before the merge, and was moved to this entry's commit at the release, as for `v1.2.0`. It had never been pushed.
- **What it merges.** `feature/idf-out` (D-130, [ADR-019](ADR-019-simulation-ready-idf-and-runner.md)), fast-forwarded into `main` at `2827656`; it was 48 commits ahead of `3e46108` and none behind. D-130 stays as written; this entry gives what holds for `main`.
- **Checks on `main`:**
  - **Examples.** All 20 example definitions were rebuilt with the 1.3.0 plugin at `2827656` (`BEMGEN_EXAMPLES_WRITE=1`), as `examples/README.md` asks at a release (`035feff`). Every one reopened and solved with one *Validate* True and no warnings, errors, or exceptions, in the rebuild and in a separate reopen.
  - **Fresh-clone gate.** A clean clone of `main` at `035feff` passed `scripts/verify.ps1` with 0 warnings: 629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, and 136 simulation tests, with the 5 opt-in EnergyPlus tests skipped. These are the counts D-130 gives.
- **What follows:**
  - the release on the docs repository's GitHub Releases (D-118), with the files of `scripts/package-release.ps1` built from the tagged commit: the plugin zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`;
  - a docs export of `v1.3.0`, which carries the *Weather* input, the *Shading* output, the new developer pages (experiment outputs, the EnergyPlus runner, ADR-019), and the rebuilt examples to the public site; the docs repository imports it and runs its own `sync-docs`;
  - the release notes say that definitions saved with 1.2.0 open with their values and wires, and that IDFs now target EnergyPlus 26.2.
- **Open** (from D-130, unchanged):
  - The e2e set does not check that `eplusout.sql` is written.
  - `envelope-presets.md` does not yet say that the F-factor method waits for a sourced F value.
  - `experiment-outputs.md` does not mention the shading of unmodelled storeys.
  - Set aside by the owner: the F-factor method, F1, and the run component.

### D-132 — The batch runner IdfBatchRunner, with a central DuckDB database per run

- **Date:** 2026-10-12 · **Decided by:** Cheng Xuan Li (a C# command-line tool instead of the Grasshopper run component; hourly results by end use and by fuel; a long table in DuckDB; no case run without a reference; a central database of the useful results with the hourly loads by fuel and by end use, the fuel table stored and never a view over the end uses; one folder per run holding its central database, one folder per case inside it; `--root` or `BEMGEN_RESULTS_ROOT`; `--resume`; `eplus-check` keeps its name; no release); the realisation by the controller · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading
- **Refines** D-016 and D-130: running batches of cases and storing their results is now in the repository, in a development tool outside `src/` that is built and tested with the solution but not packaged or released. Analysis stays outside the repository. The Grasshopper run component that ADR-019 deferred stays deferred. No research definition changes: [experiment outputs](../research/experiment-outputs.md) §1 to §8 are computed by the existing `ExperimentMetrics`.
- **Design note:** [2026-10-12-idf-batch-runner.md](../plans/2026-10-12-idf-batch-runner.md). No ADR: no research rule, pipeline type, component, or GUID changes.
- **Decided:**
  1. `scripts/IdfBatchRunner` (`net8.0`, assembly `IdfBatchRunner`) runs a set of *Convert2IDF* files. It groups them by the building, envelope, and weather of their case records. Each group's reference is the case with the zoning line `simplifier NoSimplification; aggregator Stack; IWHT=true FHT=true`. References run first, then the variants of each reference that succeeded. A case without a reference is not run, nor is one with an incomplete record, an unresolved or mismatched weather file, a duplicate, or an ambiguous reference.
  2. Each run gets `<root>/run_<yyyyMMdd-HHmmss>/` holding `central.duckdb`, `results.duckdb`, and `batch.json`, and a folder per case with EnergyPlus's files, `bemgen-run.json`, `bemgen-hourly.csv` (long), and `bemgen-summary.csv`. The root is `--root`, else `BEMGEN_RESULTS_ROOT`, and never inside the repository.
  3. **The central database** holds, per successful case (completed, verdict passed, end uses closed), the case record split into its parts, both floor areas, the annual energy of every end use by fuel, every fuel, and the total, every metric of experiment outputs §2 to §6 with its flag, and the hourly loads by fuel (EnergyPlus's four facility meters) and by end use (the six end-use meters), in W. `merge` combines the central files of runs; a case is the same when its case ID and EnergyPlus build are. Schema version 1.
  4. **The batch database** holds every case given, run or not, with its status, and the 17 hourly series of each completed case as a long table: six end uses by fuel, four fuels, the total, the two sensible diagnostics, and the four building temperatures. It and the case files are expected to be discarded later.
  5. `DuckDB.NET.Data.Full` 1.5.5 (MIT, with the native DuckDB library) is referenced by the tool and its tests only. `Lod.Simulation` stays `netstandard2.0` and BCL-only and gains the end-use-by-fuel catalogue, the hourly closure check, the run period's timestamps, the batch plan, the zoning line's parts, and the input expansion now shared with `eplus-check`.
- **Size**, measured on 80 real cases of the 1.3.0 end-to-end set: the central database takes 361 kB per case with 7 of its 10 hourly series non-zero, up to about 0.5 MB with all ten; the batch database 1.27 MB per case.
- **Built** on `feature/idf-batch-runner` (from `main` `9dcc5d5`), as D-111 sets out: the design note, a test-first build, a review by a second agent whose eleven points were fixed or recorded (the build log of the design note), and `scripts/verify.ps1` (629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, 176 simulation, and 41 batch-runner tests; the 6 opt-in EnergyPlus tests skipped; 0 warnings). The opt-in test passed on EnergyPlus 26.2.0 build `4bd7a1f26f`: the linear plan's reference and two variants ran, and the orphan did not. A run of the tool on the 110 IDFs of the 1.3.0 end-to-end set ran 80 cases, all of which succeeded. It did not run the 30 without a reference: the Medium Office set, written with the default heat-transfer options, and the overhanging stair-bay bar. Python's `duckdb` 1.5.5 reads both databases. No merge, tag, push, or release.

### D-133 — Test suites: sites, test cases, and a generator of IDFs from a test-suite spec

- **Date:** 2026-10-12 · **Decided by:** Cheng Xuan Li · **Status:** Accepted (the terms and the answers below); the design note's realisation Draft, pending the owner's approval
- **Terms**, replacing "case" everywhere, in code, databases, the IDF header, and the docs:
  - a **site** is one building in one zoning, one IDF;
  - **zoning** is the simplifier with its options, the stacker, and the two heat-transfer options;
  - a **test case** is one reference site plus at least one test site, differing only in zoning;
  - a **test suite** is the test cases expanded from one YAML test-suite spec, each test case independent of the others.

  The reference stays *No Simplification*, *Stack*, both heat-transfer options on (D-130); it is always added and never a test site. The storey count is part of a test case, not of its zoning.
- **Refines** D-132: the batch runner adopts these terms before it merges (D-064 waives backward compatibility), reads the suite's manifest, and keeps only `central.duckdb`, `batch.json`, and the IDFs when the suite asks it to discard EnergyPlus results.
- **Decided:**
  1. A new C# tool under `scripts/` writes IDFs only, from a versioned, schema-checked spec. It replaces the Grasshopper workflow for suites.
  2. **Combination rule.** A list is an axis, combined freely; a map in a list is a fixed bundle; `range` and `zip` are allowed. The axes are combined in full factorial, with no sampling, and the plan with its counts is shown before anything is written.
  3. One plan generator per suite, with the same simplifier on every floor. Buildings with differing floors, *SteppedBand* among them, wait for a separate spec schema.
  4. **Programs.** Programs come only from program JSON, local or by URL. A slot may take a weighted mix. A program's climate zones will come from its metadata; a documented placeholder in the spec stands in until then.
  5. **Schedules.** A program setting, a schedule-generator setting, and a seed give a program with generated schedules. Draws are per zone; a draw is part of a test case, shared by all its sites; seeded sampling exists only inside the schedule generator.
  6. One calendar per suite, default year 2007. Constructions will be envelope-like files; vintage and other labels are tags only. HVAC stays ideal loads.
  7. Weather files live in a folder with a registry by climate zone and location.
  8. Test cases and sites are named by short IDs. One table holds every test case as a row, with the generation parameters as structured columns. The scale is 100 000 sites or more, queried by grouping on any parameter.
- **Design note:** [2026-10-12-test-suite-generator.md](../plans/2026-10-12-test-suite-generator.md); ADR-020 (the per-zone schedule draw as a pipeline step, and the manifest-based test cases) at the build.

### D-134 — Test suites: the owner's second answers; the schedule generator deferred to a recorded requirement

- **Date:** 2026-10-12 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- **Refines** D-133, items 5 and 6. Items 5 and 6 of D-133 stand as requirements; the generator is not designed in the test-suite stage. Programs are used with the schedules their program JSON defines, and a test-suite spec has no schedule section or seed.
- **The schedule generator's requirement** is recorded in [schedule-generator-requirement.md](../research/schedule-generator-requirement.md).
  - It runs once per test case (first recorded here as "once per site", a misreading of the owner's answer, corrected the same day before the branch merged).
  - It generates schedules per zone, with shifted seeds across zones, so that units of the same type differ.
  - It shares its draws across a test case's sites.
  - Every site of a test case shares the same schedule sources: a merged zone's schedules aggregate its source zones' draws, so loads stay conserved (GLOBAL scientific rules 1 and 4), though a simplified site's actual schedules may differ.
- **Decided for the test-suite generator** ([design note](../plans/2026-10-12-test-suite-generator.md)):
  1. The IDF header's `! Case …` lines become `! Site …`.
  2. The window-to-wall ratio is a suite axis.
  3. Labels attach to bundles; a label axis is an error.
  4. Storeys are explicit floor entries or a count N, meaning ground, N − 2 typical, and top.
  5. Constructions are the built-in example envelope only, until their schema exists.
  6. `max_sites` defaults to 20 000.
  7. The tool is `scripts/TestSuiteGenerator`.

### D-135 — The test-suite generator built, the runner on declared test cases, and the case → site rename

- **Date:** 2026-10-12 · **Decided by:** the owner's decisions in D-133 and D-134; the realisation by the controller · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading
- **What it builds** ([design note](../plans/2026-10-12-test-suite-generator.md), [ADR-020](ADR-020-test-suites.md)), on `feature/test-suite-generator`, from `feature/idf-batch-runner`; neither branch is merged:
  1. **The rename.** "Case" becomes "site" and "group" becomes "test case" across `Lod.Simulation`, `Lod.Export` (the IDF header's `! Site …` lines; 6 snapshots), the batch runner and its databases (central schema version 2), the smoke spec, and the current docs. Past records keep their words.
  2. **`scripts/TestSuiteGenerator`** writes a suite's IDFs from a YAML spec checked by an embedded schema: 17 generators by name, axes in full factorial with bundles, `range`, and `zip`, program JSON by file or pinned URL, mixes, the climate-zone placeholder, and `max_sites`. A suite folder holds `suite.json`, `suite.duckdb` (one row per test case with typed parameter columns, a long parameter table, and the sites), and `idf/<test case>/<site code>.idf`.
  3. **The runner's `--suite`** takes membership and references from `suite.json` (`BatchPlan.CreateForTestCases`). It refuses a site changed since it was written (`ModifiedSinceWritten`), copies the suite's tables into the central database with the view `site_results`, merges them across runs, and honours `discard_ep_results`.
- **Realisation choices** (ADR-020):
  - test case IDs of 16 hexadecimal digits, not the note's 10, and site codes of 8;
  - labels left out of the test case ID;
  - the site ID shared by the generator and the runner;
  - a test case that cannot generate is `GenerationFailed`.
- **Checks:** scripts/verify.ps1 passed with 0 warnings (629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, 180 simulation, 89 test-suite generator, and 52 batch-runner tests). Both opt-in EnergyPlus tests passed on 26.2.0 build `4bd7a1f26f`, among them a generated suite of 8 sites run through the runner. A review by a second agent found no blocking bug. Its eight points are fixed, with tests: constructions by content in the ID, duplicate references, one-program mixes, programs fetched and imported before writing, the zoning columns in `site_results`, failed sites kept on discard, the holidays' order, and long ranges.
- **Open:**
  - buildings whose floors differ, among them *SteppedBand*;
  - the schedule generator ([requirement](../research/schedule-generator-requirement.md));
  - constructions files and HVAC systems;
  - the leftover worktree `D:\BEMGen\.claude\worktrees\suite-rename` (branch `feature/suite-rename`), whose content is all in this branch. The owner allowed its removal (2026-10-12), and it was already gone.
- **Not merged** (the owner, 2026-10-12): `feature/test-suite-generator` and `feature/idf-batch-runner` stay unmerged until the owner says otherwise.

### D-136 — The batch runner and test suites merged into main, without a release

- **Date:** 2026-10-12 · **Decided by:** Cheng Xuan Li (asked for the merge; no release; work continues on `feature/test-suite-generator`) · **Status:** Accepted
- **What it merges.** `feature/test-suite-generator`, fast-forwarded into `main`. It holds `feature/idf-batch-runner` (D-132) and the test-suite stage (D-133 to D-135, [ADR-020](ADR-020-test-suites.md)): 29 commits ahead of `9dcc5d5` (`v1.3.0`), this record included, and none behind. D-132 to D-135 stay as written; this entry supersedes their "not merged" lines.
- **No release.** The version stays 1.3.0, with no tag, no docs export, and no release files; the public site follows at the next tagged version. Nothing is pushed: a push needs the owner's yes.
- **Check before the merge:** `scripts/verify.ps1` on the merged commit (see the roadmap's progress log).
- **What follows:** work continues on `feature/test-suite-generator` (the owner, 2026-10-12), not on a new branch from `main`. The pilot suite and the deferred designs of D-133 and D-134 come next, at the owner's direction.

### D-137 — Constructions from the atlas's construction JSON: scope, ground, mass residual, fixtures

- **Date:** 2026-10-15 · **Decided by:** Cheng Xuan Li · **Status:** Accepted · Superseded in part by D-145 (the ground rule for construction sets)
- **Scope.** A stage on `feature/construction-json` (from `main` `b64805c`) imports the atlas's construction JSON (unified first, then detailed) and connects it to *Convert2IDF* through a new *Construction JSON* component and an appended *Construction* input. Program JSON v3, test-suite wiring, and *Convert2BEM* are not part of it. Design note: [2026-10-15-construction-json](../plans/2026-10-15-construction-json.md) (Draft).
- **Ground.** The atlas's constructions have no ground floor; ground surfaces take the Example envelope's ground floor, with no new input, and the ground-temperature rule of D-130 is unchanged.
- **Mass residual.** When the geometry's explicit capacity exceeds the atlas's reference budget, no mass is added for that family, explicit mass is kept, and a warning records the overshoot.
- **Fixtures.** The limited packet the atlas prepares (two construction schemas and the pilot detailed/unified pairs, with manifest and notices) may be committed byte for byte. Nothing else from the atlas.
- **Branch (the controller's choice, Provisional).** This stage has its own branch rather than `feature/test-suite-generator`, which D-136 keeps for the pilot suite.

### D-138 — Roles a construction JSON lacks but the geometry needs take the Example envelope's construction

- **Date:** 2026-10-15 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- **Decision.** When the geometry needs a role whose component the construction JSON marks `not_applicable`, the surface takes the Example envelope's construction for that role. This is the same rule as for the ground (D-137). Each such role is recorded in provenance and raised as a warning. The handover's rule, that a role the set lacks blocks conversion, applies only to components marked `blocked`.
- **Why.** The atlas's residential pair comes from a single-family detached house, so it has no interior walls, interior floors, or exposed floors. Every BEMGen residential plan has walls and slabs between zones, so blocking would make the residential pair unusable.
- **Note:** [2026-10-15-construction-json](../plans/2026-10-15-construction-json.md), build log "Part A, the packet, and what it changes", item 6.

### D-139 — The construction JSON stage closed on the unified path, not merged

- **Date:** 2026-10-15 · **Decided by:** Cheng Xuan Li (close the stage on the unified path first; Part E later); the realisation by the controller · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading
- **What is built.** On `feature/construction-json`, Parts A to D of the [design note](../plans/2026-10-15-construction-json.md):
  - **Part A:** the pinned atlas packet, `bemgen-construction-7693e08-v1`.
  - **Part B:** typed opaque layers (massive, massless, air gap) with surface finishes, and windows of simple or layered glazing, in the envelope and the IDF.
  - **Part C:** `Lod.ConstructionJson`, which imports the unified `building_level_equivalent` 1.1.0, together with construction sets and the mass ledger in `Lod.Core`, and *Convert2IDF* taking a set.
  - **Part D:** *Construction JSON* (GUID `b2802511-fee7-49ab-bdcb-9329ce293461`), the parameter *Construction Set* (`ef90ede8-f0ff-4495-822b-11c5e61a6fe5`), and *Convert2IDF*'s appended *Construction* input.

  The rationale is in [ADR-021](ADR-021-construction-sets-and-mass-ledger.md).
- **Checks.**
  - `scripts/verify.ps1` passed.
  - All 17 headless Rhino specs passed, the new `construction-json` among them.
  - The 168 construction IDFs had 0 IDD problems against 26.2 and all completed in EnergyPlus 26.2.
  - Each part was reviewed by a second agent and its findings fixed.
  - The fresh-clone gate passed (see the roadmap's progress log).
- **Controller choices recorded in the note's build log:**
  - a zero budget is information;
  - the finish applies to both faces of a layer;
  - `InteriorCeiling` is unused;
  - removed slabs count once in the ledger;
  - the IDD check allows window names in `SurfaceProperty:IncidentSolarMultiplier`, with evidence;
  - the strict reader and the schema evaluation of `Lod.ProgramJson` are public and shared;
  - *Construction JSON* sits in panel *1 Program*.
- **Not done.** Not merged, tagged, pushed, or released, so the public site still describes 1.3.0. Part E (detailed documents) is open. The open findings are listed in ADR-021.

### D-140 — Residential construction sets: packet v2, opt-in Example fill, attic roofs, adiabatic source floors

- **Date:** 2026-10-15 · **Decided by:** Cheng Xuan Li · **Status:** Accepted. The detection rules in the last bullet are the controller's and are Provisional, pending the owner's reading. Superseded in part by D-142 (the residential rules, removed in code by D-143)
- **Fixtures.** The atlas packet `bemgen-construction-7693e08-v2` (manifest SHA-256 `5b8dd4cf…`) may be committed whole. It replaces v1, whose files it keeps byte for byte, and adds two residential pairs, `residential-multistorey-garage-4A` and `residential-raised-exposed-floor-1A`.
- **Example fill is opt-in.** Supersedes D-138's default.
  - A role or window that the construction set lacks but the building needs is an actionable error by default.
  - *Convert2IDF* gains *Fill From Example*, default false. When true, such roles take the Example envelope's construction with a warning, as D-138 did.
  - The ground stays the Example's, with a remark (D-137).
- **Attic roofs.** Where the source's roof sits over a vented attic, the roof of conditioned zones takes the set's `InteriorCeiling` recipe. This is an approximation that leaves out the attic air and the roof deck, recorded in provenance with a warning. A modelled attic zone is not planned.
- **Adiabatic source floors.** A residential `InteriorFloor` recipe comes from floors that are adiabatic in the source. With floor heat transfer on, it is still written as a conductive slab, with a warning.
- **Order.** C2 (the unified fixes) and then E1 (reading the detailed documents) run without a stop in between. E2, the detailed assignment, comes later.
- **Detection (controller, Provisional).** The unified document carries no space types, so:
  - an attic roof is read from a `whole_dwelling` set whose `InteriorCeiling` is ready;
  - a residential interior wall is read as a wall to unconditioned space (a garage), and a residential interior floor as one from adiabatic source floors, both from the `whole_dwelling` scope;
  - each is recorded as such in provenance. An explicit flag from the atlas would replace these rules.

### D-141 — C2 and E1 closed: residential construction sets converted, detailed documents read, not merged

- **Date:** 2026-10-15 · **Decided by:** the owner's decisions in D-140; the realisation by the controller · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading. Superseded in part by D-142 (the residential rules and E2)
- **What is built on `feature/construction-json`:**
  - packet v2 pinned (five pairs);
  - *Fill From Example* opt-in on *Convert2IDF* (input 10, default false), with the actionable error `ConstructionMissing`;
  - the residential rules: an attic ceiling as the roof (an approximation), the garage-wall caveat, and the warning on interior floors that are adiabatic in the source, given only when a floor is written conductive;
  - reading detailed `construction_set` documents into `DetailedConstructionDocument`, all rules, conditions, and geometry instructions kept, with unsupported assemblies as warnings, and the set refused with `ConstructionAssignmentUnavailable`.

  The rationale is in [ADR-022](ADR-022-residential-construction-sets.md).
- **Checks.**
  - `scripts/verify.ps1` passed.
  - All 17 headless Rhino specs passed; `construction-json` has 8 scenarios and 22 checks.
  - The 284 construction IDFs of C2 had 0 IDD problems and passed in EnergyPlus 26.2.
  - All ten packet documents parse.
  - C2 and E1 were each reviewed by a second agent and every finding fixed.
  - The fresh-clone gate passed (roadmap progress log).
- **Wording.** D-140's "adiabatic source floors" reads as "mostly adiabatic": the 4A interior floor blends an adiabatic floor between storeys (about 92.5%) with the floor to the garage.
- **Not done.** Not merged, tagged, pushed, or released. E2, binding detailed conditions to zones, needs its own design note. Open: whether EnergyPlus applies the incident solar multiplier with a blank schedule has not been compared numerically; the `AirGap` and `Gas` property names are assumed.


### D-142 — Construction JSON scope: unified building-scope sets only; detailed binding (E2) dropped; single-dwelling sets rejected

- **Date:** 2026-10-16 · **Decided by:** Cheng Xuan Li (answers to the E2 note's questions) · **Status:** Accepted. Supersedes the parts of D-140 and D-141 named here.
- **Unified only.** BEMGen converts only unified (`building_level_equivalent`) sets, which are space-type agnostic: one assembly per semantic for the whole building. Binding detailed rules to zones (E2) is dropped, and its draft note is superseded. Detailed documents stay readable (E1) for evidence and are never converted.
- **No single-dwelling sets.** Sets with the scope `whole_dwelling` (the ResStock single-family fixtures) are rejected. BEMGen's residential buildings are apartments, which use building-scope apartment sets, not single-dwelling ones. This supersedes D-140's residential rules (the attic ceiling as the roof, the garage-wall caveat, the adiabatic-source floor warning): with whole-dwelling sets rejected, nothing reaches them.
- **Unconditioned is unconditioned.** No garage or attic category is modelled.
- **Windows.** BEMGen windows are fixed. A unified set's window is already resolved by its source's window areas: in the packet, it is the fixed recipe at weight 1.0. So operability raises no question on the unified path.
- **Kept from D-140:** *Fill From Example* stays opt-in, for a role a building-scope set marks not applicable. The ground stays the Example's (D-137). The branch stays `feature/construction-json`.

### D-143 — Construction packet v3, D-142 in code, removed slabs written once per face, and the solar multiplier checked

- **Date:** 2026-10-16 · **Decided by:** Cheng Xuan Li (commit packet v3; "Fix: half-thickness"; an apartment set has the medium office's schema) · **Status:** Accepted. Refines how D-031 is written in an IDF; D-031's rule (merged slabs become internal mass, keeping their storage and exchange area) stands. Superseded in part by D-145 (the packet pin).
- **Packet v3 pinned.** `bemgen-construction-7693e08-v3`, manifest SHA-256 `57a71b7c675901d8e36201f6301569c0e626cbd8103fa76550de60ceca92b4f0`, seven pairs: v2's five, byte for byte, plus `midrise-apartment-2019-3B` (scope `building`) and `residential-apartment-unit-1990s-4A` (scope `whole_dwelling`).
- **The apartment set is the residential case.** The midrise apartment's unified set has the medium office's shape: every role BEMGen uses is ready, its `InteriorWindow` is not applicable with `source_reference_zero_exposure` (valid, and not listed as unused), and it has budgets, furnishings, and a floor-distributed mass. It converts the linear plan on every zoning without *Fill From Example*, and the mass ledger holds on every zoning.
- **D-142 in code.**
  - A unified set whose scope is not `building` is refused with `ConstructionJsonScopeNotSupported`. The packet's four single-dwelling sets, the apartment unit among them, are refused; their detailed documents are still read as evidence.
  - The residential rules of D-140 are removed with their codes: the attic ceiling as the roof, the garage-wall caveat, the adiabatic-source floor warning, `ConstructionApproximation`, and `AdiabaticSourceConducted`.
- **Removed slabs (the fix).**
  - EnergyPlus `InternalMass` is one-sided, with an adiabatic back. Writing a removed slab as its full construction on slab area × exposed faces gave each face the whole slab's resistance and stored twice the slab's heat capacity. The mass ledger (D-139) counts the slab's capacity once, so the IDF disagreed with the ledger wherever storeys were merged into one zone.
  - Now each exposed face is a slice of the slab, `Construction.Sliced(faces)`: a two-face slab is written on twice its area with `"{name} Half"`, whose massive layers have half their thickness and whose massless layers and air gaps have half their resistance. The IDF then holds the slab's capacity once, and each face sees the resistance to the slab's mid-plane.
  - This is exact for a symmetric slab. For an asymmetric one, such as the Example interior floor (gypsum board, concrete, screed), each half keeps every layer in order, so this is an approximation.
  - A slice whose massless layer would fall below EnergyPlus's minimum resistance (0.001 m²·K/W) is the error `EnvelopeValue`, naming the layer.
  - Two IDF snapshots changed (single-zone aggregators). *Convert2BEM*'s *Internal Mass* output is unchanged: it is the exposed area, and its construction is the converter's (D-023).
- **Solar multiplier checked.** The 5A set's IDF on the linear plan (*No Simplification*, *Stack Floors*) was run for a year in EnergyPlus 26.2 in Golden, CO (TMY3), with and without its 40 `SurfaceProperty:IncidentSolarMultiplier` objects. The windows' transmitted solar (`Surface Window Transmitted Solar Radiation Energy`, summed) was in the ratio 0.8276, the multiplier, with a blank schedule. This closes the open question of D-141 and ADR-021. An end-to-end test now checks that every window gets the set's multiplier.
- **Deferred by the owner:** Program JSON v3, the test-suite generator's construction input, and *Convert2BEM* with construction sets.
- **Not done.** Not merged, tagged, pushed, or released.

### D-144 — Version 1.4.0: construction sets from the atlas's construction JSON, released with a docs export

- **Date:** 2026-10-16 · **Decided by:** Cheng Xuan Li (tested the branch in Grasshopper and Rhino, then asked for the merge, the push, the tag, the release with the plugin files, and the docs sync on 2026-10-16) · **Status:** Accepted
- **Version.** 1.4.0, tag `v1.4.0`, a minor version as D-125 reasons: D-064 waives backward compatibility, and the stage changed no GUID. It adds one component and one parameter (*Construction JSON*, *Construction Set*) and two inputs appended to *Convert2IDF* (*Construction*, *Fill From Example*).
- **What it merges.** `feature/construction-json` (D-137 to D-143, [ADR-021](ADR-021-construction-sets-and-mass-ledger.md), [ADR-022](ADR-022-residential-construction-sets.md)), fast-forwarded into `main` at `8e03abb`. It was 61 commits ahead of `b64805c` and none behind. `main` also carries the batch runner and the test-suite generator (D-132 to D-136); they are tools, not part of the plugin, and are first tagged here.
- **Checks on `main`:**
  - **Examples.** All 20 example definitions were rebuilt with the 1.4.0 plugin (`BEMGEN_EXAMPLES_WRITE=1`, `fd32a54`). Every one reopened and solved with one *Validate* True and no warnings, errors, or exceptions, both in the rebuild and in a separate reopen.
  - **Fresh-clone gate.** A clean clone of `main` at `fd32a54` (`D:\BEMGen-gate\v1.4.0`) passed `scripts/verify.ps1` with 0 warnings. The counts are 681 core, 518 generator, 160 program JSON, 73 construction JSON, 1739 export, 2726 integration, 180 simulation, 52 batch-runner, and 89 test-suite tests; 7 opt-in EnergyPlus tests were skipped.
- **What follows:**
  - the release on the docs repository's GitHub Releases (D-118), with the files of `scripts/package-release.ps1` built from the tagged commit: the plugin zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`;
  - a docs export of `v1.4.0`, imported by the docs repository, which runs its own `sync-docs`. The owner asked for a minimal change to the hand-written pages: the new component and inputs, and the IDF change. The atlas's data and contracts are not described on the public site.
- **Release notes.**
  - Definitions saved with 1.3.0 open as they were, with *Construction* unset and *Fill From Example* false.
  - IDF files of zonings that merge storeys into one zone change: each slab inside the zone is written as twice its area of half its thickness, so its heat capacity counts once.

### D-145 — Construction packet v7: native ground methods, v3 retired, D-142 kept, ground temperatures from the source's rules

- **Date:** 2026-10-18 · **Decided by:** Cheng Xuan Li (answers in the session that took the atlas's v7 handover) · **Status:** Accepted. Supersedes D-143's packet pin and D-137's ground rule for construction sets; D-142 stands; D-130's ground rule stands for buildings converted without a construction set.
- **Packet v7 replaces v3.** `bemgen-construction-foundation-v7` (manifest SHA-256 verified on 2026-10-18; it names v6 as its parent) is pinned whole, byte for byte, in place of v3: 19 detailed 3.0.0 / unified 2.0.0 pairs, the four schemas, the notices, and the licence. v3's seven pairs are all in v7 (same source contexts, five renamed `retained-*`), with the same ordinary assemblies and components; v7 adds the foundation roles, `foundation_ground`, materials, evidence, and the shared mass contract 1.0.0. The unified 1.1.0 and detailed 2.0.0 readers are retired, with no backward compatibility (D-064).
- **D-142 kept.** *Convert2IDF* converts only unified sets of scope `building`. Detailed documents and single-dwelling sets are imported and their foundations instantiated from declared geometry (the handover's R1–R6, K1–K6, I1–I6, on both representations), but not converted. Kiva therefore runs only in importer-generated EnergyPlus smoke cases outside the pipeline.
- **Native ground in *Convert2IDF*.** For a v7 set, a ground floor takes the set's own `GroundFloor` method instead of the Example's ground floor (D-137):
  - F-factor: `Construction:FfactorGroundFloor` with the set's F, the surface's actual area, and its exposed perimeter (shared zone edges cancelled, zero allowed), on `GroundFCfactorMethod`;
  - layered ground: the set's layers on `Ground`.
- **F/C ground temperatures.** `Site:GroundTemperature:FCfactorMethod` is the weather file's monthly mean dry-bulb, delayed three months and rounded to 0.1 °C. This is OpenStudio Standards' method (the STAT file's monthly dry-bulb, `rotate(-3)`), computed from the EPW's hours because BEMGen takes no STAT file. A v7 set with F- or C-factor surfaces and no weather file is refused.
- **Layered-ground temperatures.** `Site:GroundTemperature:BuildingSurface` is 18 °C in every month for a v7 set. That is EnergyPlus's default, which the source's prototypes ran with: OpenStudio Standards writes no BuildingSurface object when it finds the STAT file. Provenance records it as the source's condition.
- **Why.** The atlas asks that native methods not take the "indoor minus 2 °C" rule. EPW ground temperatures are absent from many AMY files (16 of 157 local EPWs, ComStock's and ResStock's AMY files among them) and, where present, are undisturbed soil values that EnergyPlus advises against under a building.

### D-146 — Construction foundation v7 built: packet v7 read, foundations instantiated, native ground in Convert2IDF

- **Date:** 2026-10-18 · **Decided by:** controller (the owner's decisions in D-145) · **Status:** Accepted; the controller's realisation Provisional, pending the owner's reading. Realises D-145; rationale and alternatives in [ADR-023](ADR-023-native-ground-methods-and-packet-v7.md); design note [2026-10-18-construction-foundation-v7.md](../plans/2026-10-18-construction-foundation-v7.md) (a build log for each part).
- **Part A, packet v7 and the readers.**
  - Packet v7 is pinned whole in place of v3 (61 files, every file's SHA-256 and size checked in `PacketTests`); the four schemas are embedded byte for byte and evaluated without the network.
  - `ConstructionJsonImporter.Read` reads either representation (unified 2.0.0, detailed 3.0.0) of any scope with full closure; `Import` is `Read` plus D-142's scope refusal.
  - The foundation data are plain types in `Lod.Core.Foundations` (`FoundationData`, ground methods and model parameters, `DimensionOperand`), carried on `ConstructionSet.Foundation`; the shared readers are `FoundationReader`, `MaterialReader`, and `MassContract`.
- **Part B, instantiation** (`Lod.Core.Foundations.Instantiation`). `FoundationInstantiator.Instantiate(FoundationData, FoundationInstantiationRequest)` returns resolved surfaces and one `KivaFoundationInstance` per group; `KivaInitialization.Derive` is the source's `resstock_source_start_month_1.0.0`; `FoundationModelScope.MayShare` and `Combine` give the scoped reuse; `FoundationResourceInterner` combines several documents. The handover's R1 to R6, K1 to K6, and I1 to I6 pass on both representations.
- **Part C, native ground in *Convert2IDF*.**
  - `ExposedPerimeter` (shared edges cancelled, zero allowed); `NativeGroundFloor` through `ConstructionSet.Resolve`; `EpwDryBulb` and `NativeGroundTemperatures` for `Site:GroundTemperature:FCfactorMethod`; layered ground with a `BuildingSurface` of 18 °C.
  - New diagnostics `GroundMethodNotSupported` and `GroundTemperatureWeatherMissing`, and, after the review, `GroundAssignmentSetAside`.
  - The header and provenance (`GROUND:`, `UNUSED:`) record the rule. A conversion without a construction set is unchanged (D-130).
- **Part D, outside the pipeline.** `IdfFoundations.Write(FoundationModel)` writes `Construction:CfactorUndergroundWall`, `Construction:FfactorGroundFloor`, layered constructions, `Foundation:Kiva` with `Foundation:Kiva:Settings` and `SurfaceProperty:ExposedFoundationPerimeter`, and the ground temperature objects. *Convert2IDF* does not use it. What EnergyPlus cannot hold is `FoundationNotWritable`.
- **Review fixes.** A second agent reviewed the diff: one major, five minor, and nits, all fixed test-first.
  - Major: the user-facing descriptions of *Construction JSON* and *Convert2IDF* still described the Example's ground. *Roles* now follows `Resolve` through `ConstructionSet.DescribeGround()`, and `GroundFloor` is no longer in the unused list.
  - Minor: ground rules set aside silently (now `GroundAssignmentSetAside`); the Kiva material check ran after the construction cache was read; a start-month off-by-one that the old test did not catch (twelve distinct monthly means now); an inline layered equivalent under a layered-ground or Kiva method (refused at read time); and the written F-factor perimeters for every family.
  - The last of these found a real defect. On turned plans with courts the written pieces did not keep the footprint perimeter: 586.2 m against 456 m for *Court Cluster* and 337.6 m against 288 m for *Enclosed Court* through *Perimeter Core*, and 89.27 m against 88 m for *Point Plate* through the merging simplifiers. Edge coincidence was measured at a neighbour's far corners; it is now measured at both ends of the overlap, with the tolerance unchanged.
  - Nits: boundary keywords in one place (`IdfBoundaries`), F-factor names through `IdfNames.Unique`, the ten-block Kiva limit documented, the Kiva operand check counting errors only, and the mass contract check using the tolerances the importer is given.
- **Checks.**
  - `scripts/verify.ps1`: `VERIFY PASSED`, 0 warnings. Tests: Core 740, Generators 518, Integration 2762, Export 2830 (1 opt-in skipped), ConstructionJson 286, ProgramJson 160, Simulation 180 (12 opt-in skipped), IdfBatchRunner 52 (2 skipped), TestSuiteGenerator 89.
  - With `BEMGEN_ENERGYPLUS=D:\EnergyPlusV26-2-0`: Simulation 205 of 205 and Export 2831 of 2831.
  - `scripts/idd-check`: 0 problems on the 18 IDFs of Part D and on 458 export IDFs in Part C.
  - Headless Rhino check: all 17 specs passed; `construction-json` 23 checks ok. Results in `D:\BEMGen-smoke\foundation-v7-rhino-2`.
- **EnergyPlus 26.2 results** (Chicago O'Hare TMY3; pass means a completed run with no severe or fatal error and no unexpected warning):

  | Case | Outcome |
  | --- | --- |
  | Medium office F-factor, *No Simplification* and *Perimeter Core* | pass |
  | Warehouse F-factor, both zonings | pass |
  | Retained midrise apartment F-factor | pass |
  | Tall building F-factor (`FoundationWall` unused) | pass |
  | Small data centre layered, windowless | pass |
  | Small data centre layered, Example windows (*Fill From Example*) | fail: 6 severe errors, the run completes |
  | Legacy hospital basement layered; hospital 2019 3B layered | pass |
  | R4: C-factor walls of 2 m and 3 m, both representations | pass |
  | K4: retained 5A Kiva slab, both representations | pass |
  | K2: two equal 5A slabs, both representations | pass |
  | K1: vented crawlspace, coupled slab and walls, both representations | pass |
  | K1 crawlspace air exchange | unsupported |

  For the F-factor cases, EnergyPlus's U without films equals 1/(A/(P·F) − 0.165) for every construction, the written perimeters times multipliers sum to the footprint's 84 m, and the `.eio` ground temperatures equal those written.
- **Consumer results.** R1 to R6, K1 to K6, and I1 to I6 all pass on both representations. They check the importer and the instantiator against the atlas's contract; they do not establish that BEMGen's conversion is correct.
- **Open items** (also in ADR-023):
  - The small data centre's windowless source set with *Fill From Example* windows gives 6 severe errors (the ground floor absorbs no solar). A warning is proposed, not built.
  - A crawlspace or garage host's air exchange (SLA with the ASHRAE 62.2 weather factor, Sherman-Grimsrud) is not instantiated (unsupported).
  - Kiva start-day setpoints come from the caller, not from program schedules.
  - The 5A Kiva method gives no footing wall construction, so EnergyPlus uses its default.
  - The C-factor soil resistance appears capped (about 0.92 m²·K/W on a 3 m wall), inferred from output.
  - Part C's ground matching and Part B's instantiator are separate; a shared selection helper is a follow-up.
  - The v7 schemas' internal `$id` versions (`construction-equivalent:1.2.0`, `construction-set:2.1.0`) differ from the documents' versions 2.0.0 and 3.0.0; to report to the atlas.
  - F-factor cases of turned plans with courts were not run in EnergyPlus.
- **Not done.** Not merged, tagged, pushed, or released; no docs export. An atlas validation does not establish BEMGen's correctness.

### D-147 — A warning when Example windows go into zones whose ground floor absorbs no solar

- **Date:** 2026-10-18 · **Decided by:** Cheng Xuan Li ("Add a Convert2IDF warning when Example windows go into zones whose ground floor absorbs no solar (the data centre case)") · **Status:** Accepted. Closes the data-centre open item of D-146 and ADR-023.
- **Decision.** *Convert2IDF* gives the warning `ExampleWindowSolarNotAbsorbed` when three things hold:
  - the construction set has no window, so the building's windows are the Example's under *Fill From Example*;
  - the resolved ground floor's inside layer has an explicit solar absorptance of 0;
  - some zones with windows have only ground floors.

  The warning names those zones. The source's values are written as given; nothing is repaired. An unset absorptance is EnergyPlus's default, 0.7, which absorbs.
- **Why.** The small data centre's source has no windows, and its ground floor is one massless layer with solar absorptance 0. With the Example windows, EnergyPlus reports one severe error per such zone ("floor cannot absorb any solar gains"). The run completes, but `scripts/eplus-check` fails it. The warning tells the user beforehand to use a windowless building with that set, or a set with windows.
- **Checks.**
  - `IdfNativeGroundTests`: the warning names exactly the windowed ground-only zones of the linear plan, and is absent on a windowless building, on the office's F-factor set, and on the legacy hospital's layered ground, whose inside layer absorbs.
  - The opt-in EnergyPlus case: the warning names as many zones as EnergyPlus reports severe errors (6), and the windowless run has no warning.
- **Not covered.** A set with its own windows over such a floor; no packet set has one.

### D-148 — Turned plans with courts run in EnergyPlus: the merging simplifier passes, Perimeter Core's near-zero core perimeters stall EnergyPlus

- **Date:** 2026-10-19 · **Decided by:** controller (D-146's open item, taken up as a follow-up session) · **Status:** Provisional, pending the owner's reading. Follows up D-146's open item "F-factor cases of turned plans with courts were not run in EnergyPlus"; it does not close it.
- **Follow-up of D-146.** *Enclosed Court* and *Court Cluster*, turned 30°, with the medium office v7 set: *Conditioned Merge* passes, with Σ P × multiplier 288 m and 456 m, the footprints' outer and court perimeters. *Perimeter Core* fails: its turned core pieces are written with P ≈ 1e-6 m instead of 0, and EnergyPlus does not finish initialisation within 30 minutes. The fix to `ExposedPerimeter` is left to the stage owner. Results and diagnosis are in the [design note's build log](../plans/2026-10-18-construction-foundation-v7.md#build-log-turned-plans-with-courts-in-energyplus-d-148).

### D-149 — An uncovered stretch of a ground-floor edge no longer than the distance tolerance counts as covered, so a core's exposed perimeter is exactly 0

- **Date:** 2026-10-19 · **Decided by:** controller (D-148's finding, fixed as a follow-up session) · **Status:** Provisional, pending the owner's reading. Refines D-145's exposed-perimeter rule as D-146 realised it; closes D-148's *Perimeter Core* failures.
- **Rule.** `ExposedPerimeter` exposes what its neighbours leave of each edge stretch by stretch, and a stretch no longer than `ToleranceSettings.Distance` (a gap between two covering edges, or between a covering edge and an end of the edge) counts as covered. On a turned plan the 1e-6 m clipping grid leaves neighbours' corners a fraction of the tolerance short of a core edge's ends, and the old subtraction exposed those slivers: up to 4.5e-6 m on the bottom-storey core of every turned family through *Perimeter Core*, and floating-point remainders (2.8e-14 m where inspected) on six unturned ones. EnergyPlus takes only P = 0 as no perimeter; from a micrometre it builds an insulation layer of about 1e8 m²·K/W and stalls in initialisation. Now a piece with no edge on the footprint's boundary is written with P = 0 exactly.
- **Not changed.** No tolerance was added or widened; no positive minimum is ever added; edge coincidence (D-146, `ec4835c`) is unchanged; the per-level total keeps the footprint perimeter within the distance per edge, as the family tests already allowed. An edge itself no longer than the tolerance, which could not be matched before, now counts as covered too.
- **Tests.** Written first: `ExposedPerimeterTests` (a turned core whose neighbours' corners stop 0.4 µm short gives 0.0; a 10 µm gap stays exposed), and `FFactorPerimeterFamilyTests` now requires every written ground piece with no edge on the footprint's boundary to have P == 0 (it failed for 24 of 36 family cases before the fix). No IDF, integration, or program snapshot changed. The four opt-in turned-court EnergyPlus cases of D-148 pass. Details in the [design note's build log](../plans/2026-10-18-construction-foundation-v7.md#build-log-exact-zero-core-perimeters-d-149).

### D-150 — The construction foundation v7 stage merged into main, without a push or release

- **Date:** 2026-10-19 · **Decided by:** Cheng Xuan Li ("Rerun the Rhino check and fast-forward main to the v7 branch with a decision-log entry; leave all branches and worktrees as they are. Don't push.") · **Status:** Accepted
- **What it merges.** `claude/bemgen-construction-v7-update-bd63b1` is fast-forwarded into `main`. It is 39 commits ahead of `e6c073e` (v1.4.0), this entry included, and none behind. It holds:
  - D-145 to D-149 and ADR-023;
  - the shared assignment-selection rule (`AssignmentSelector` in `Lod.Core`), which ground-floor resolution in *Convert2IDF* and the foundation instantiation service now both use. It was built on `claude/blissful-lamport-65f6c3`, applied here by cherry-pick with its build-log section kept beside D-148's and D-149's, and changes no behaviour, snapshot, or test.

  The follow-up branches `claude/nifty-sanderson-4e38ed` (D-148) and `claude/nervous-payne-4d8585` (D-149) were fast-forwarded into the stage branch first.
- **Checks on the merge candidate:**
  - `scripts/verify.ps1`: `VERIFY PASSED`, 0 warnings. Core 753, Generators 518, Integration 2762, Export 2832 (1 opt-in skipped), ConstructionJson 286, ProgramJson 160, Simulation 180 (13 opt-in skipped), IdfBatchRunner 52 (2 skipped), TestSuiteGenerator 89.
  - With `BEMGEN_ENERGYPLUS` set: Simulation 209/209, Export 2833/2833, IdfBatchRunner 54/54. These include the four turned-court F-factor cases and the data-centre warning case.
  - Headless Rhino check: all 17 specs passed, and `construction-json` passed 23 checks.
- **Not done.** No push, tag, release, fresh-clone gate, or docs export; the version stays 1.4.0. Branches and worktrees are left as they are, on the owner's instruction.

### D-151 — Test suites take construction sets paired by climate, and the research outputs gain the hourly ground heat transfer

- **Date:** 2026-10-19 · **Decided by:** Cheng Xuan Li (the note's six questions: "test suite generators will handle the pairing; by design, climate should match construction-ground", "ok to mark as invalid and dont write it", ground heat transfer "add it"; the note "approved" with the OpenEPW Las Vegas 3B weather file), realised by the controller · **Status:** Accepted for the owner's decisions; the realisation is Provisional, pending the owner's reading
- **Design note:** [2026-10-19-suite-constructions-ground.md](../plans/2026-10-19-suite-constructions-ground.md), with its build log. Refines [ADR-020](ADR-020-test-suites.md) (its consequences record the change).
- **Test suites with construction sets** (`scripts/TestSuiteGenerator`):
  - A constructions entry is `builtin: Example` or a unified construction JSON (`construction_json`, a file or a URL pinned by `sha256`) with `fill_from_example`. The test case ID holds its content: `json:<sha256>;fill=<bool>`; the built-in text, and so every earlier built-in ID, is unchanged.
  - A set is paired only with the weather files of its climate zone; a mismatched pair is never a test case. The Example pairs with every file; a set that pairs with none is a plan error.
  - Sets are imported before anything is written. Refused: a scope other than `building`, a detailed document (D-142), a schema or closure error, a ground floor the set cannot place, and an F- or C-factor set with a weather file lacking a full year.
  - A site whose conversion warns `ExampleWindowSolarNotAbsorbed` (D-147) is `Invalid` and not written; every site keeps its conversion warnings.
  - `test_cases` gains `constructions_kind`, `constructions_sha256`, `constructions_climate_zone`, `fill_from_example`, and `ground_method` (`IndoorMinus2`, `FFactor`, `Layered`).
- **Ground heat transfer** ([experiment outputs §9](../research/experiment-outputs.md)): G(t) = Σ m_z · Q_s(t) over surfaces on `Ground` or `GroundFCfactorMethod`, with Q_s EnergyPlus's `Surface Inside Face Conduction Heat Transfer Energy` and m_z the zone multiplier from the `.eio`, in W as hourly means; positive toward the zone. Annual net, gain, and loss in kWh.
  - *Convert2IDF* requests the variable keyed per ground surface and `Output:Surfaces:List, Details`; `Lod.Simulation` reads the surfaces' zones and boundaries from the `.eio`; the batch runner stores the series, `hourly_ground`, and three annual columns, in central schema version 3. Version 1 and 2 files are refused, and a run folder from before this stage cannot be resumed (D-064).
- **Checks:**
  - `scripts/verify.ps1`: `VERIFY PASSED`. Core 753, Generators 518, Integration 2762, Export 2837 (1 skipped), ConstructionJson 286, ProgramJson 160, Simulation 198 (14 opt-in skipped), IdfBatchRunner 57 (3 skipped), TestSuiteGenerator 117.
  - Opt-in, EnergyPlus 26.2.0 `4bd7a1f26f` with the owner's Las Vegas file: the medium office F-factor set on two storeys ran with 0 warnings, its `.eio` ground surfaces equal to the IDF's (annual G net −3715.2 kWh); `scripts/eplus-check` passed with no new warning; the pilot suite (the office and warehouse F-factor sets, 2 test cases of 8 sites) ran with all 16 sites succeeding and each reference's comparison metrics 0.
  - Headless Rhino check: all 17 specs ran to the end with no exception, missing component, missing expected error, or failed check; the only unwritten IDFs are `convert-idf`'s five expected error scenarios, as in the v1.4.0 run (results in `D:\BEMGen-smoke\d151-all`).
  - A second agent reviewed the diff and found nothing blocking; its should-fix items (a test that the conversion warnings reach `site_results`, the untested invalid-test-site branch now documented) and nits were applied.
- **Next:** Program JSON 3.0.0 as its own stage, from the atlas's `codex/foundation-ground` at `e9a982d` (read only); program JSON 4.0.0's fuel-fired hot water is a research change left for a later decision. Not merged into `main`, tagged, pushed, or released.

### D-152 — D-151 merged into main; the runner reports sites as they finish and keeps a status row for every site

- **Date:** 2026-10-21 · **Decided by:** Cheng Xuan Li (after the first mock test suite: "the runner's progress log should indeed be flushed each line", "keep a status row for each site is necessary", "fast forward main first", "local cleanup agreed", "after deletion, ok to delete remote branches"), realised by the controller · **Status:** Accepted for the owner's decisions; the realisation is Provisional, pending the owner's reading
- **Design note:** [2026-10-21-runner-progress-and-site-status.md](../plans/2026-10-21-runner-progress-and-site-status.md).
- **Merge and cleanup.** `main` is fast-forwarded to `feature/test-suite-generator` at `1ba4840` (D-151), without a push. The merged worktrees and local branches are removed (`feature/ground-heat-transfer`, `feature/suite-constructions`, `claude/bemgen-construction-v7-update-bd63b1`, `feature/idf-out`, `feature/construction-json`, `feature/program-json`, `feature/idf-batch-runner`, and the agents' and controller's leftover branches), and the remote branches `feature/suite-constructions`, `feature/idf-out`, and `feature/program-json`, all merged into `main`, are deleted. `feature/program-popup-web` and `feature/program-popup-window` stay, unmerged, as the owner asked earlier.
- **Progress lines** (`scripts/IdfBatchRunner`). The mock suite showed that the runner writes sites one at a time, in plan order, and printed each line only then, so with 16 EnergyPlus processes the log fell far behind the simulations. Each site's line is now printed and flushed when its simulation finishes, with the counts simulated and written; the databases, the site files, `batch.json`, and the summary keep their plan order. Writer throughput under load is a follow-up.
- **`site_status`.** The central database gains a table with one row per site of a run, whatever happened to it (status, message, `succeeded`, verdict, closure, exit code, warnings, runtime), and the view `site_overview` (every site with its results where it succeeded). `sites` and `site_results` keep the successes only. Merge keeps one row per site, known by its site ID and EnergyPlus build. Central schema version 4; a version 3 file is refused.
- **Checks:**
  - `scripts/verify.ps1` on `a91b95f`: `VERIFY PASSED`, 0 warnings. Core 753, Generators 518, Integration 2762, Export 2837 (1 skipped), ConstructionJson 286, ProgramJson 160, Simulation 198 (14 opt-in skipped), IdfBatchRunner 66 (3 skipped), TestSuiteGenerator 117.
  - The mock suite again on EnergyPlus 26.2.0 `4bd7a1f26f`, 16 at a time, with the change before the review fixes: 9 minutes 8 seconds; progress lines from the first finished simulation on; `site_status` 1,024 rows (896 succeeded, the two 4A references completed and failed on their unexpected warning, 126 `ReferenceFailed`), `site_overview` 1,024 rows with 896 results. When the last simulation finished the writer had written 366 sites: its throughput under load is the follow-up.
  - A second agent reviewed the diff and found nothing blocking; its should-fix (the progress total kept the test sites of failed references) and its nits (stale comments, the README's status columns, one status row for a site held twice in one source, `CREATE OR REPLACE` for the temporary table) are applied.
- **Not done.** No merge of `feature/runner-site-status` into `main`, no push, tag, or release.

### D-153 — The results folder: a light central database, hourly Parquet per site, and raw and failure folders

- **Date:** 2026-10-22 · **Decided by:** Cheng Xuan Li (the layout and its revisions in conversation: "central duckdb only stores metric relevant info alongside suite, case, and site identifiers", the hourly folder "as parquet (18 series)", a `raw/` folder keeping only `eplusout.err`, discard on by default, failures in `failure/<test-case-id>/<site code>/`, `hourly/<test case id>/…` file names, plan-order scheduling, and merge refusing a name collision), realised by the controller · **Status:** Accepted for the owner's decisions; the realisation is Provisional, pending the owner's reading
- **Design note:** [2026-10-22-results-folder-redesign.md](../plans/2026-10-22-results-folder-redesign.md). **Supersedes** D-132's hourly tables in the central database and the batch database, and D-133's spec setting `discard_ep_results`.
- **Why.** Timed on 128 sites of the mock suite, the runner's single writer spent about 86 of its 94 ms per site on hourly rows written three times (central database, batch database, CSV). The run's log lagged because `Parallel.For` gave each worker a block of the plan, so the in-order writer waited for the first block; writer cost was the same with and without EnergyPlus running.
- **The run folder.** `batch.json` (with each site's IDF and weather paths and the weather SHA-256), `central.duckdb`, `hourly/<test case id>/<site code>.parquet`, `raw/<test case id>/<site code>/eplusout.err` (the whole EnergyPlus folder with `--keep-raw`), and `failure/<test case id>/<site code>/` (the whole folder of a site that ran and did not succeed). EnergyPlus runs in a short `work/<site key>` folder. Removed: `results.duckdb`, `bemgen-hourly.csv`, `bemgen-summary.csv`, `bemgen-run.json`, the central hourly tables and their views.
- **Central schema version 5.**
  - **`sites`:**
    - drops the raw header lines, the per-site EnergyPlus version, the weather name and SHA-256, the concurrency columns;
    - keeps `energyplus_build`;
    - adds all-hours heating and cooling unmet hours (System Summary, *Time Setpoint Not Met*, Facility row; the occupied-hours table depends on each zone's occupancy, so on the zoning).
  - **`site_status`:**
    - drops the warning text (`eplusout.err` is kept);
    - adds the closure residual, meters written, concurrency, runtime comparability, IDF version, run warnings, finish time, and the IDF's `code_version` (provenance: `batches.tool_version` is the runner's version, not *Convert2IDF*'s).
  - **Transactions:** a site's `sites` and `site_status` rows are written in one transaction.
- **Hourly Parquet.**
  - **Contents:** the 18 series of the batch database in a long table with `site_id` and `energyplus_build` in every row, ZSTD.
  - **Writing:** by the worker that ran the site, before its rows.
  - **Reading:** no view is stored, since DuckDB resolves a view's relative path against the reading process's working directory (checked); the README gives the `read_parquet` join.
- **Runner behaviour.**
  - Discard moves to the runner, on by default; a spec with `discard_ep_results` is refused.
  - Resume is incremental: a site with a status row is done; a reference's loads are read back from its Parquet file, and a missing or damaged one is run again.
  - `merge --out <folder>` writes `central.duckdb` and `hourly/`, copying the added sites' files, and refuses a name collision, including the same site under two EnergyPlus builds, and schema version 4 or earlier.
  - Sites start in plan order.
- **Research documentation.** Experiment outputs §8 now says what a run keeps by default: metrics, the hourly series, and `eplusout.err`; the other EnergyPlus files only with `--keep-raw` or on failure. No metric changes. `ExperimentMetrics.Compute` against a reference's three loads equals the old path exactly (tested).
- **Checks:**
  - `scripts/verify.ps1` on `aef5b56`: `VERIFY PASSED`, 0 warnings. Core 753, Generators 518, Integration 2762, Export 2837 (1 skipped), ConstructionJson 286, ProgramJson 160, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. With `BEMGEN_ENERGYPLUS` and `BEMGEN_WEATHER_3B`, the runner tests 91/91.
  - **The mock suite on EnergyPlus 26.2.0 `4bd7a1f26f`**, 16 at a time, with the code before the review fixes, which change no normal-path result:
    - **time:** 8 min 24 s (9 min 8 s with D-152's writer);
    - **writer:** 885 of 898 sites written when the last simulation finished, against 366 before;
    - **sizes:** `central.duckdb` 3.6 MB (was 331 MB), `hourly/` 383 MB for 896 files (about 430 kB per site, 18 series), `raw/` 3.7 MB, `failure/` 117 MB for the two failed Sterling references;
    - **statuses:** 896 succeeded, 2 failed, 126 `ReferenceFailed`; the documented join gives 896 × 18 × 8760 rows;
    - **unmet hours:** 0 everywhere, with ideal loads.
  - **Review:** a second agent found nothing blocking. Its should-fix items are applied:
    - one write per site even after a writer failure;
    - a Parquet write failure making only that site `RunFailed`;
    - `code_version` kept;
    - the weather SHA-256 in `batch.json`.

    So are its nits (an `.err` kept on a repeated finish, a damaged reference file rerun, merge temporary files removed, `WriteBatch` in one transaction).
- **Open.** An old `suite.json` that still has `discard_ep_results` is ignored by the runner. Not merged into `main`, pushed, tagged, or released.

### D-154 — The runner's progress, site status, and results folder stages merged into main and pushed

- **Date:** 2026-10-22 · **Decided by:** Cheng Xuan Li ("all good. merge and push", after running the small mock suite) · **Status:** Accepted
- **What.** `feature/runner-site-status` (D-152, D-153: 15 commits after `1ba4840`, this entry included) is fast-forwarded into `main`, and `main` is pushed to `origin`. `main` at `1ba4840` (D-151) was already on `origin`.
- **Checks.** `scripts/verify.ps1` passed on `aef5b56` (D-153); the commits after it change documentation only. With `BEMGEN_ENERGYPLUS` and `BEMGEN_WEATHER_3B` the runner tests passed 91/91, and the mock suite ran on EnergyPlus 26.2 (D-153).
- **Not done.** No tag, release, docs export, or fresh-clone gate; the version stays 1.4.0. The branch `feature/runner-site-status` stays until the owner asks to remove it.

### D-155 — Branch and worktree cleanup; the program JSON popup branches kept unmerged on origin

- **Date:** 2026-10-25 · **Decided by:** Cheng Xuan Li ("merge most of them (except for the popup 2 branches) and delete merged except current worktree", "for popup: keep that branch(s) do not merge. push worktree commits if not already") · **Status:** Accepted
- **Merged branches deleted.** Every branch other than the popup branches was already in `main` (D-151, D-154). Deleted: `feature/test-suite-generator`, with its worktree `idf-batch-runner-plan-859669` and its remote branch `origin/feature/test-suite-generator`. `feature/runner-site-status` and its worktree stay for now: they equal `main` and hold the session that did this cleanup. The leftover non-git folders `D:\worktrees\conditioned-merge`, `dropdown-enums`, and `program-mix` (old IDE state) are deleted.
- **Popup branches.** `feature/program-popup-window` (the JSON editor window on *Program JSON*, D-128) and `feature/program-popup-web` (the experimental atlas web view, D-129, which contains the window branch) are kept unmerged and are now pushed to `origin`, so they no longer exist on one machine only. They have no worktree. D-128 and D-129 are recorded only on those branches, which is why the log on `main` goes from D-127 to D-130. A trial merge into `main` conflicts in five documentation files (AGENTS.md, this log, the roadmap, and the two smoke-test documents); a later merge resolves them and runs `scripts/verify.ps1` and the Rhino check.
- **Untouched.** `origin/batch1-saved` and `origin/feature/reduced-order-5r1c` are a collaborator's branches and are left as they are.

### D-156 — Paired evaluation metrics: ideal sensible loads, peaks, hourly fit, temperature, and computation

- **Date:** 2026-10-26 · **Decided by:** Cheng Xuan Li (the metrics and the implementation requirements: "update the IDF simulation evaluation pipeline to compute and export the following metrics … supporting subsequent paired comparisons against a designated high-detail reference"); the realisation by the controller · **Status:** Accepted for the scope; the realisation superseded in part by D-157, which settles the rest
- **What.** A second metric set, [experiment outputs §10](../research/experiment-outputs.md#10-paired-evaluation-metrics), beside §2 to §5, which do not change. Design note: [2026-10-26-evaluation-metrics.md](../plans/2026-10-26-evaluation-metrics.md). Built on `feature/evaluation-metrics`, in its own worktree, from `main` at `b80477b`.
  - **Loads:** the ideal sensible heating and cooling, summed over the zones' ideal-loads systems apart at each hour, never netted, without latent or non-HVAC loads: annual kWh and kWh/m², the maximum, P99, and P95 in kW, each with its relative error; the hours above the reference's P99 and P95 for the site and the reference; CV(RMSE) and NMBE (site minus reference) in %; the load-duration-curve NRMSE over all ranks and the top 1, 5, and 10 % (88, 438, 876 hours), each normalised by the reference's mean within the interval; KS.
  - **Temperature:** the conditioned-floor-area-weighted mean zone air temperature's MBE and RMSE against the reference's over all hours and over the common unconditioned hours, which come from the ideal loads' availability schedules, never from zero loads.
  - **Computation:** wall-clock and EnergyPlus runtime, zone and represented zone counts, average and peak process memory (sampled every 50 ms by the process runner), and each one's ratio over the reference's.
  - **Pairing:** a site is compared with its test case's reference only (building, envelope, weather, run period, D-132, D-153), and the hourly internal-load end uses are checked against the reference's; a site that fails keeps its metrics with the problem in its status message.
- **Near-zero denominators.** `ToleranceSettings` gains `NegligibleLoadIntensity`, 0.01 W/m² of the reference's total floor area (ADR-004 amended): a metric normalised by a reference load at or below it is missing with `NearZeroReference`, never a percentage. New flags: `NearZeroReference`, `NoCommonUnconditionedHours`, `AvailabilityUnknown`, `NotMeasured`.
- **The multiplier, found in the build.** EnergyPlus 26.2 reports the ideal-loads zone variables with the zone multiplier in. In the linear plan with multipliers above 1, the plain sum of the zones' sensible heating equals `Heating:DistrictHeatingWater` to 1e-15 in all but rare hours (one hour in each of three of the 56 configurations, 1e-6 below it; in the atlas medium office 57 hours, at most 2 × 10⁻⁵), and the plain sum of their total cooling equals `Cooling:DistrictCooling` to 1e-12; the sensible cooling is never above it. The first draft multiplied them again, as §9 does for surface variables, and overcounted by up to 2.8 times; the opt-in runs caught it. `Heating:EnergyTransfer` and `Cooling:EnergyTransfer` are not the zone sensible loads (up to 0.8 % apart in an hour) and stay diagnostics.
- **Stored.** Central schema version 6: the §10 columns of `sites` with their `_flag` columns, the table `metric_definitions` (one row per evaluation column), and `batches.negligible_load_w_m2`; the hourly files gain `SensibleHeating`, `SensibleCooling`, and `ConditioningAvailable` (21 series). Resume rebuilds a reference's profile from its hourly file and its `sites` row.
- **Cannot be computed today.** The temperature over common unconditioned hours is always `NoCommonUnconditionedHours`, because *Convert2IDF* leaves the availability schedules blank (conditioning every hour; setbacks are conditioning); memory exists only for runs of the batch runner from this stage; results folders of schema version 5 are not resumed or merged.
- **Checks.** `scripts/verify.ps1` passed (2026-10-26, uncommitted tree). With `BEMGEN_ENERGYPLUS` (EnergyPlus 26.2.0, the installation's Chicago O'Hare TMY3) and without `BEMGEN_WEATHER_3B`: `Lod.Simulation.Tests` 279 passed, 1 skipped (needs 3B weather); `IdfBatchRunner.Tests` 97 passed, 1 skipped (the pilot suite, needs 3B weather). A second agent reviewed the diff: no serious finding; its fixes are in (a flag column for every metric that may be missing, the memory sampler's start-up sample dropped, a zero-weight temperature keeps its own flag, an infinite reference gives no ratio, the end-to-end availability check for unconditioned buildings, and documentation).
- **Committed** on `feature/evaluation-metrics` as six focused commits after `b80477b`, this entry the last (the owner, 2026-10-26: "commit … as focused commits (no push, no merge)").
- **Not done.** No merge, push, tag, or release; the stage close-out's `sync-docs` pass waits for the merge.

### D-157 — Evaluation metrics: the owner's decisions on signs, P90, unconditioned hours, and measuring cost in parallel

- **Date:** 2026-10-26 · **Decided by:** Cheng Xuan Li, reading D-156's open choices · **Status:** Accepted · **Supersedes in part:** D-156 (the NMBE sign, the temperature over common unconditioned hours, the memory measure alone)
- **Kept as D-156 built them:** the near-zero threshold (0.01 W/m² of the reference's total floor area), the zone ideal sensible variables, the top intervals as the first ⌈k · n / 100⌉ ranks, the working set, and the pairing check that keeps a failing site's metrics.
- **Bias sign.** NMBE uses ASHRAE Guideline 14's sign, reference minus site ("let's use the ashrae convention: reference - site"): positive when the site's load is below the reference's. The temperature MBE follows, as the same kind of bias error; the relative errors of annual and peak values stay (site − reference) / reference.
- **P90** is added beside P95 and P99 for the sensible peaks, their errors, and the exceedance hours, as experiment outputs §3 has it.
- **No temperature over unconditioned hours** ("let's not complete the conditioned hour temperatures ever. remove that part from the current code and plan"). No program is off by the hour: a zone is conditioned all year or not at all, and *Convert2IDF* writes no availability schedule. Sourced programs set back their setpoints (the atlas medium office from 21/24 °C to 15.6/26.7 °C at night, Saturday afternoons, Sundays, and holidays), which is conditioning. The availability reading, the flags `NoCommonUnconditionedHours` and `AvailabilityUnknown`, their columns, and the `ConditioningAvailable` hourly series are removed (20 hourly series); the temperature is compared over all hours.
- **Cost in parallel runs** (the owner chose the recommended "robust measures + timing pass"). Batches keep running in parallel.
  - Every run records the **processor time** (user and kernel) and the **peak committed private memory**, which other processes change far less than the wall clock and the working set; both get ratios over the reference.
  - An optional **serial timing pass** (`--timing-repeats N`, `--timing-test-cases K`) re-runs the succeeded sites of the timed test cases one at a time once every site is written, test cases in the order of their IDs' SHA-256, repeats as the outer loop, each reference just before its variants. It writes `site_timing`; the view `site_timing_summary` holds the medians and their ratios to the reference's. Resume and merge carry it.
  - Central schema version 7: D-156's version 6 existed only on this branch, and a folder of it is refused by resume and merge.
  - Recommended use: `--parallel` at most the number of physical cores, the processor-time and committed-memory ratios of every site, and a serial sample to report runtimes and to calibrate the parallel measures.
- **Built** on `feature/evaluation-metrics` after D-156, with the experiment outputs §10, the design note, and the runner's README.
- **Checks.** A second agent reviewed the diff: no serious finding; its fixes are in (schema version 7, a P90 test that tells the percentiles apart, an unknown committed memory gives no ratio, a timing run that could not start has no wall clock, documentation). `scripts/verify.ps1` passed after them. With `BEMGEN_ENERGYPLUS` (EnergyPlus 26.2.0, Chicago O'Hare TMY3), without `BEMGEN_WEATHER_3B`: `IdfBatchRunner.Tests` 105 passed and 1 skipped after the fixes (the real batch with `--timing-repeats 1` among them); `Lod.Simulation.Tests` 275 passed and 1 skipped before the last two fixes, which do not touch what the opt-in runs check.
- **Headless Rhino check** (the owner, 2026-10-26): `scripts/rhino-smoke/run.ps1` on `58d0522`, all 17 specs, Rhino 8, 2026-10-26 04:22 to 04:28: every spec done, no exception, missing component, missing expected error, or failed check; the runtime errors are the specs' error scenarios.
- **Not done.** No merge, push, tag, or release. The leftover worktree `idf-evaluation-metrics-60072b` and its branch, equal to `main`, are removed (the owner, 2026-10-26).

### D-158 — The paired evaluation metrics stage merged into main, without a push or release

- **Date:** 2026-10-26 · **Decided by:** Cheng Xuan Li ("Fast-forward main to feature/evaluation-metrics and run the sync-docs close-out; don't push") · **Status:** Accepted
- **What.** `main` is fast-forwarded from `b80477b` (D-155) to `feature/evaluation-metrics` (D-156, D-157), and then to this entry with the close-out's documentation edits. Not pushed, tagged, or released; the version stays 1.4.0.
- **Checks.** Those of D-156 and D-157: `scripts/verify.ps1`, the opt-in EnergyPlus 26.2 suites, and all 17 headless Rhino specs passed, with two reviews by a second agent.
- **Close-out (`sync-docs`).** Links and code fences checked (`developer_pages.py --check`: 80 pages, no broken link); this entry, D-156's status, the design note's status, AGENTS.md's project state, the roadmap's progress log, and README's line on the batch runner brought up to date. The public site describes 1.4.0 (`e6c073e`); it follows at the next tagged version with the docs export (D-118), which then also carries the developer pages of D-145 to D-158.

### D-159 — Main pushed with the paired evaluation metrics, without a tag or release

- **Date:** 2026-10-26 · **Decided by:** Cheng Xuan Li ("Push main to origin (no tag, no release)") · **Status:** Accepted
- **What.** `main` is pushed to `origin` as a fast-forward, `b80477b..7d3c941` (D-156 to D-158), and then with this entry. No tag, release, or docs export; the version stays 1.4.0.

### D-160 — The DOE zone is the most detailed level of a DOE generator; D-097 is relaxed for them

- **Date:** 2026-10-25 · **Decided by:** Cheng Xuan Li (owner, O4 of the DOE geometry design note); wording by the controller, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176) · **Refines:** D-097
- **Numbering.** The DOE geometry entries were written as D-156 to D-167 on `feature/doe-geom`, became D-159 to D-170 at the merge of `main` with the evaluation-metrics entries D-156 to D-158, and are D-160 to D-171 since the second merge of `main`, which added D-159 (the owner's decision to renumber after `main`'s entries, 2026-10-26). Commit subjects on the branch keep the numbers of their time.
- **Merge of `main`** (`7d3c941`, the paired evaluation metrics, D-156 to D-158) into `feature/doe-geom` as `d168942`: the conflicts in `AGENTS.md`, ADR-004's status, this log, and the roadmap's progress log keep both sides; `ToleranceSettings` takes both new optional parameters, `negligibleLoadIntensity` then `acceptance` (every caller names them). `scripts/verify.ps1`: VERIFY PASSED, 0 warnings: Core 922, Generators 3051 (1 skipped, A2), Integration 3584, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 246 (14 skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119. The headless Rhino check: all 25 specs ran, no *Validate* False, exception, missing component, failed check, or missing expected error.
- **Second merge of `main`** (`98aa569`, D-159, the push of `main`) into `feature/doe-geom`, after renumbering these entries by one more: the one conflict, in this log, keeps both sides with `main`'s entry first.
- Why (the owner's words): relax D-097 for the DOE generators: the DOE zone, whatever it covers (one room, grouped rooms, a classroom pod), is their most detailed level; *Semantic Merge* then gives the department level.
- For the DOE reference geometry generators ([ADR-025](ADR-025-doe-reference-geometry-generators.md), design note [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md)), the zone of the source (the DOE reference zone, or the detailed-office space for offices) is the most detailed level. D-097 (one zone per department, never per room or tenancy) is relaxed for these generators only.
- Unchanged: D-097 for every other non-residential generator (the six precedent generators `OfficePlate`, `Cafeteria`, `BranchingMall`, `OperatingSuite`, `CareHub`, `FoyerHalls`), and D-009 and D-085 for housing. [ADR-014](ADR-014-program-types-and-department-zoning.md)'s department table is not changed.
- A DOE zone carries its standards space type as an explicit `ProgramKey` (ADR-025, S4); the simplifiers and aggregators coarsen DOE zones as they coarsen any others.

### D-161 — DOE geometry stage P0a: ADR-025, layout records, grid plan layout, program keys, and the comparison harness

- **Date:** 2026-10-25 · **Decided by:** the controller under D-098, pending the owner's reading; the program-key rule by the coordinating session that dispatched the controller · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P0a; [ADR-025](ADR-025-doe-reference-geometry-generators.md) (S1–S10, accepted by the controller, provisional); docs: [doe-layouts.md](../architecture/doe-layouts.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p0a-adr` (`18269cc`) and `feature/doe-geom-p0a` (`ce859a7`).
- **Built:**
  - `GridPlanLayout` (S1): storeys from x-cuts, y-cuts, and zones as unions of grid cells; duplicate IDs are `DuplicateZoneId`; a court touching the outline at a corner is a hole. `GridAxis` (S3): fixed intervals keep their length, flexible ones share a change in proportion to their default length and stay at least 1 m, one axis per building, lengths compared within `ToleranceSettings.Distance`.
  - `scripts/doe-geometry/extract.py` (stdlib, `python -I`, `--check`) writes 15 layout records (`src/Lod.Generators/Doe/Layouts/`, embedded, loaded by `DoeLayoutRecords`) and 15 answer keys (`tests/fixtures/doe/`), each with its sources' SHA-256, the DOE credit, and the openstudio-standards BSD-3 licence.
  - `ProgramKey` on `PlannedZone`, `Zone`, and `TargetZone` (`null` for every earlier generator, so every snapshot is unchanged; only *Semantic Merge* sets it on new zones); *Semantic Merge* groups by space type and key; `PlanPresets.PresetFor`; the fixed table `DoeSpaceTypes`; `DoeProgramMap` (a missing key is `MissingPreset`).
  - `ToleranceSettings.Acceptance` with the §5 tolerances ([ADR-004](ADR-004-tolerances.md) amended); the comparison harness in `Lod.Generators.Tests` (gap zones excluded zone by zone and from the T4 totals).
- **Program keys:** for every reference zone, in order: (1) the zone name is a standards space type of the type's building type in openstudio-standards `doe_ref_1980_2004.spc_typ.json`; (2) the prototype geometry OSM that `prototype_inputs` names for DOE Ref 1980-2004 has a space of the zone's name, whose assigned standards space type is the key; (2b) OSM spaces of exactly one standards space type tile the zone within the ADR-004 distance and relative-area tolerances; (3) otherwise the extraction stops. Each zone records its rule, the OSM spaces used, and the file with its SHA-256; the OSM only names the type, the geometry is the reference's (O8). All zones of the 15 records resolve (rule 1: restaurants, supermarket, warehouse office, retail back space; 2b: warehouse bulk and fine storage; 2: the rest); the offices take their rooms' standards space types. Every key is pending A1 (no atlas program yet).
- **Office T4 inputs (test fixture):** per orientation, the reference's glazing (windows and glass doors) over the reference's outdoor wall area (below the 2.74 m ceiling in the medium and large offices, S6; the full 3.05 m wall in the small office), on every room facing it; the rooms reproduce the note's window areas, the small office's 20.64 m² south (3.91 m² glass door included) too.
- **Routine choices:** fifteen records (the note's "14" is one short of its own §4 table); ADR-025 written on its own docs branch; kebab-case record names and `DoeBuildingType`; source coordinates within 5 mm put on one cut (one adjustment per storey, largest 0.018 m² in the hospital); storey multiplier = smallest zone multiplier on the storey; floor height = area-weighted most common zone-plus-plenum height; G4 copies only for the outpatient stairs and lift; the warehouse's fine-storage floor above the office dropped (G4, −236.88 m²); outdoor walls in answer keys as BEMGen builds them; a flexible interval already under 1 m by default may grow but not shrink.
- **Source facts against the note:** the large office's 46,320 m² includes the 3,563.1 m² basement (42,757.25 m² above grade, G3); the offices' perimeter depth is 4.5733 m (medium) and 4.5732 m (large), not 4.57 m, so T7 takes the depth from the answer key (at 4.57 m the cores miss by 0.43 and 0.65 m²); the small office has no plenum (G2 only, not G1); the outpatient record has 59/41/26 zones per storey, the note's 59/37/22 plus the G4 stair and lift copies.
- **Checks:** `scripts/verify.ps1` on `ce859a7`: VERIFY PASSED, 0 warnings: Core 782, Generators 868, Integration 2762, Export 2837 (1 skipped), ConstructionJson 286, ProgramJson 160, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. `extract.py --check`: 30 files identical. Every record matches its answer key on T1–T3 through `GridPlanLayout`; T7 passes for the three offices. A second agent reviewed ADR-025 (two rounds) and the stage (three rounds); every finding is applied.
- **Pending:** the hospital's ground storey (a room drawn apart from the plate, two footprint polygons, `NotSupported` until P5) and the hospital's T3 total; the full T4 run until P0b; A1 for every program key.

### D-162 — DOE geometry stage P0b: glazing per orientation, skylights, and the true outdoor wall basis of T4

- **Date:** 2026-10-25 · **Decided by:** the controller under D-098, pending the owner's reading; the T4 basis by the coordinating session that dispatched the controller · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P0b (S5, S6, O3). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p0b` (`30f6df1`).
- **What.** `ProgramPreset` carries a WWR per orientation (`WindowToWallRatios`, N/E/S/W) and a `SkylightRatio`; a scalar WWR means all four and no skylight, so every existing snapshot, report, provenance, IDF, and icon is unchanged. An outdoor wall takes the WWR of the sector its true azimuth falls in (S5). `PlanParameters.GlazingReferenceHeight` (optional, (0, floor height], in provenance when set) sizes windows as WWR × length × height (S6).
- **Skylights** ([ADR-012](ADR-012-centred-windows.md#skylights-doe-geometry-p0b), extended). One centred skylight per zone ceiling, in its largest grid rectangle (vertex coordinates, plus edge midpoints when the roof is not rectilinear). Simplifiers give each target ceiling, and `Storeys.Assemble` each outdoor roof piece (terraces included), Σ ratio × overlap of the detailed ceilings: covered ceilings get none, and the result does not depend on the method. `SkylightDoesNotFit`, never capped; `SkylightNotHosted` is a guard. Validation adds `Skylights` and `Building.SkylightsOnRoofs` when skylights exist.
- **Program JSON.** Options `WindowToWallRatios` and `SkylightRatio`, and, until atlas input A2, a glazing fixture (`bemgen-program-glazing-fixture` 0.1.0, keyed by `source.program_id`, its SHA-256 in provenance).
- **Converters and Grasshopper.** *Convert2IDF* writes skylights as `FenestrationSurface:Detailed` `Window` in their roof piece; courts are cut along whichever axis keeps them whole (documented limit: a skylight covering one court's x-range and another's y-range is `DegeneratePolygon`; no generator reaches it). *Convert2BEM* lists skylights in *Windows*. The default preset components, *Program Preset*, and *Program JSON* gain *WWR North/East/South/West* and *Skylight Ratio*, appended; set inputs always win, a uniform set included; no GUID or icon changes.
- **T4 basis.** The WWR per zone and orientation is the source glazing over the source's true outdoor wall: the zone's Outdoors walls less every stretch that coincides with a wall of another counted zone, whatever its boundary, over the height both walls share, by the D-041 façade-line test within the ADR-004 tolerances. `extract.py` computes it from the source only and lists every stretch with its partner's boundary class: 18 stretches, Outdoors 8 (secondary school bathrooms and corridors against the auditorium), Surface paired 2 (small office `Corridor_1`, large office `Lobby_Bot_ZN_2`), Surface self-referencing 8 (outpatient `Floor_2_Reception_Hall`). Partners are counted zones only: plenums, attics, and basements are excluded, consistent with G1; a probe found 0 stretches against them. T2 checks the true outdoor wall against what BEMGen draws, and every record passes. Atlas input A2 must use the same basis.
- **Source boundary artifacts.** The stretches against a non-Outdoors wall are source boundary artifacts that BEMGen corrects geometrically, for example the outpatient reception hall's 26.5 m of south wall, which the source exposes to outdoor air although it adjoins the X-ray and exam rooms. Any later energy comparison against the source must know that these walls differ. How BEMGen treats self-referencing partners thermally belongs to P5a.
- **T4 exclusions by sourced rule.** G4: the warehouse office (shorter than its storey, under the dropped fine-storage floor) and fine storage; the secondary school's tall zones and the walls against a tall zone drawn on its own storey only; the outpatient's G4 copies. Pending S8/P5a: walls toward multiplied rooms (large hotel 8 quantities, 3 still disagreeing; hospital 46), ratcheted separately in T4 and T2. Pending P5: the hospital's ground storey and totals. All 15 records pass T4, skylights per zone and in total included.
- **Checks.** `scripts/verify.ps1` on `30f6df1`: VERIFY PASSED, 0 warnings: Core 862, Generators 957, Integration 2929, Export 3098 (1 skipped), ProgramJson 175, Simulation 205 (14 skipped), ConstructionJson 286, IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. `extract.py --check`: 30 files identical; `test_extract.py`: 10 tests OK. Rhino smoke on `5cd2cc5`: 18 specs, no failed check (new spec `glazing`). A second agent reviewed the stage in five rounds; every finding is applied.
- **Open.** For a person in Rhino 8: skylights in the viewport, an EnergyPlus run of a skylit IDF, the editor checklist. Sourced glazing per program waits on A2.

### D-163 — DOE geometry stage P5a: multiplied rooms, the copy space, the self-adjacent boundary, and per-key glazing inputs

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading; the *Conditioned Merge* rule and the one-plate design by the controller; the treatment of walls on nothing and the per-key glazing inputs by the coordinating session that dispatched the controller (2026-10-25) · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P5a (S8, O5); [ADR-026](ADR-026-multiplied-rooms.md) (accepted by the controller, provisional; amended to the build); docs: [doe-layouts.md](../architecture/doe-layouts.md), [pipeline.md](../architecture/pipeline.md), [domain-model.md](../architecture/domain-model.md), [validation.md](../architecture/validation.md), [convert2idf.md](../architecture/convert2idf.md), [convert2bem.md](../architecture/convert2bem.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p5a-adr` (`96a4c70`) and `feature/doe-geom-p5a` (`00404c8`).
- **Multiplier.** `PlannedZone`, `TargetZone`, and `LayoutZone` carry `Multiplier` (default 1, whole, below 1 `InvalidParameter`); the plan builder gives it to `Zone`; `Storeys.PlaceAt` multiplies it by a group's storey count (a ×19 room on a ×4 floor is ×76). Every total counts zone × multiplier.
- **One plate with a copy space.** On a storey with a multiplied zone `GridPlanLayout` puts every grid cell in the footprint, which is one polygon (the hospital's ground storey included); the copy space is the footprint less the drawn zones (`CopySpace.Of`); drawn zones plus copy space must make the footprint's area (`CopySpaceAreaMismatch`); every placed storey carries it (`PlacedStorey.CopySpace`). Without a multiplied zone, cells in no zone stay outside and a footprint of several polygons stays `NotSupported`. T1 compares the drawn outline. This replaces ADR-026's first draft (several footprint polygons).
- **`BoundaryCondition.SelfAdjacent`** (no adjacent zone), from the footprint: a zone edge on the copy space (not on the plate's outline), an edge between zones of different multipliers (both sides, never paired), and a floor or ceiling piece between different multipliers or on the copy space of the storey beyond. It is neither exterior, ground, roof, nor exposed; an F-factor ground floor's edge toward the ground copy space is not exposed perimeter. The D-069 options leave it unchanged; it takes the interior construction of its kind; *Convert2IDF* writes a `Surface` naming itself, each piece its own name; *Convert2BEM* prints `SelfAdjacent`. `InterzoneMultiplierMismatch` stays as the writer's guard for other buildings. *Stacked Floor Zone Multiplier* makes every piece between storeys adiabatic, a self-adjacent one too (D-075). The source's self-referencing walls between zones of equal multiplier stay `Interzone`.
- **Steps.** *Semantic Merge* and *Conditioned Merge* merge only zones of equal multiplier and keep it; *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* return `NotSupported` for floors with multiplied rooms. Validation adds `MultiplierPairing` and `Building.MultiplierPairing` only when a source plan has room multipliers.
- **Walls on nothing (geometry decides, as D-162).** `extract.py` counts every stretch of a source wall not marked Outdoors with no counted zone and no copy space beyond it as a true outdoor wall, whatever its source boundary, and lists it in the answer key (`nonOutdoorExteriorWalls`); a stretch toward the copy space is self-adjacent.
- **Source boundary artifacts.** The source treats 16.8 m of the hospital plate's east façade as adiabatic: `OR_NurseSat_Flr_2_Wall_1_East` (x = 70.104 m, y 0 to 16.764 m) is a self-referencing `Surface` with no zone and no copy beyond it; BEMGen draws it as an outdoor wall of `OR_NurseStn_Lobby_Flr_2`. No other wall of the fifteen records has nothing beyond it and a boundary other than Outdoors. With D-162's artifacts (the outpatient reception hall's 26.5 m of south wall, the small and large offices' short paired stretches), these are the walls an energy comparison against the source must name.
- **Per-key glazing inputs (A2 basis).** Each answer key gives each program key's WWR per orientation (source glazing over the true outdoor wall, or the wall below the source ceiling under G1, summed over the key's zones times their multipliers without gap zones and orientations) and its skylight ratio (`programGlazing`), and lists every zone whose key ratio would miss its own source glazing by more than T4's 1 % (`glazingRatioDifferences`): small hotel 43 (among them `GuestRoom206_208` S, 0.191 against the key's 0.158), outpatient 38, hospital 6, every other record 0. T4 runs on the generators' path, one program per key through `DoeProgramMap`: window area per orientation in total and per key within 1 % for every record; per-zone glazing is checked where every zone of a key shares its ratio, the listed zones are reported, and a test checks the list is exact. The 1 % threshold for "differs" is a controller routine choice tied to `Acceptance.RelativeGlazingArea`.
- **Harness.** T2 splits the key's walls on no other zone into `self-adjacent wall` and the outdoor rest, counts back-to-back self-adjacent walls as shared, and compares per zone the roof and exposed floor area with `sourceRoofArea` and `sourceExposedFloorArea`. The `pending: S8, P5a` and `pending: P5, two-polygon ground storey` exclusions of D-161 and D-162 are gone: the large hotel's 8 and the hospital's 58 T4 quantities, their T2 true outdoor walls, and the hospital's ground storey and T3 total pass.
- **Source fact.** The hospital's ×4 `Office1` leaves a 12.1975 m gap (room for four copies, not three), so copy-space area and Σ(m − 1)·area are not tied.
- **Checks.** `scripts/verify.ps1` on the merge `74cbde4`: VERIFY PASSED, 0 warnings: Core 917, Generators 1024, Integration 2929, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. `extract.py --check`: 30 files identical; `test_extract.py`: 17 tests OK. A second agent reviewed ADR-026 (four rounds) and the stage (three rounds); every finding is applied; six self-referencing IDFs passed EnergyPlus 26.2 in review (0 warnings, 0 severe).
- **Open.** For a person in Rhino 8 (after P5b's components): the *Convert2BEM* `SelfAdjacent` output and viewport.

### D-164 — DOE geometry stage P1: the ring offices, storey multipliers, the DOE program map component, S3 by slack, and the O3 wording

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading; the S3 amendment and the O3 wording by the coordinating session that dispatched the controller (2026-10-25) · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P1 (§1 O3 and §2 S3 amended in the same merge); [ADR-025](ADR-025-doe-reference-geometry-generators.md) S3 and O3 amended; [ADR-015](ADR-015-plans-per-storey.md) amended; docs: [doe-ring-office.md](../architecture/doe-ring-office.md), [doe-components.md](../architecture/doe-components.md), [doe-layouts.md](../architecture/doe-layouts.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p1` (`ca725cd`).
- **Built:** `RingOfficeGenerator` (records Small, Medium, Large; 17; 23/21/21; 26/26/26 zones) on `GridPlanLayout`, one plan per record storey, presets from a `DoeProgramMap`; gaps G1 (medium, large), G2 (small), G3 (large); `RingOfficeGenerator.Limits`. `MultiStoreyPlanGenerator.StoreyMultiplier` (default 1; provenance `StoreyMultiplier` when not 1; it counts in the elevations above): the large office's middle plan stands for `Storeys − 2` (10), so its storeys stand at the reference's 0, 19.816 (×10), and 43.5952 m. Grasshopper: *DOE Program Map* (keys and presets, or one preset for every key; `DoeProgramMap.Create`), the `DoeGeneratorComponent` base (inputs in one order for every DOE family: counts, sizes, Floor Height, Orientation, Program Map, Preview Location; outputs *Plan*, *Multipliers*, *Program Keys*, the keys listed even with no map and with an input that has no data), *DOE Small/Medium/Large Office*.
- **S3 amendment (decided above the controller).** Fixed bands keep their length; flexible intervals share a plate change in proportion to their slack (length minus 1 m), shrinking and growing alike, so all reach 1 m at the shortest valid plate (fixed bands plus 1 m per flexible interval); an interval under 1 m has no slack and keeps its length (replacing P0a's "may grow but not shrink"); a total slack within the distance tolerance is none, and then any change is `InvalidParameter`; the defaults stay exact. In `GridAxis`, for every family. Why: under the first rule the large office could not shorten by even 1 % (core intervals of 1.023 and 1.036 m). P0a tests changed accordingly (the small office's half plate is now valid; the resized primary school is checked against hand-shared cuts).
- **T5 rule (decided above the controller).** Every size parameter at 0.5×, 1×, and 2× of its default, or, where a factor is invalid under S3, at its computed limit (which keeps the topology) and just beyond it (`InvalidParameter`); each family documents its limits and reports the valid range. Ring offices (m, at the defaults): plate length ≥ 16.573 / 23.994 / 49.107; plate depth ≥ 13.582 / 17.121 / 34.402; perimeter depth 0.5–7.011 / 0.593–13.420 / 0.5–19.321; corridor width 0.5–3.658 / 0.5–9.296 / 0.5–8.692; every limit at least ±20 % of its default.
- **O3 wording (decided above the controller).** "Window-to-wall ratio per orientation (N, E, S, W) and a skylight ratio are program data from the atlas, per zone type. Window shape is not reproduced. Glazed area per orientation is reproduced in total and per program key, and per zone where a key's zones share one ratio." The owner's decision was the ratio per zone type; "glazed area per zone" in the first wording went further. A second per-zone input path is rejected; atlas input A2 is unchanged (one ratio per program and orientation, true-outdoor-wall basis).
- **Routine choices:** `GridAxis.MinimumFixedBand = 0.5` m for every band a size parameter sets (per band, not per grid interval), for every DOE family; ring defaults are the top storey's south bands, rounded to the records' 1e-6 m (`RecordDecimals`, tied to `extract.py`); the glazing reference height keeps the source's share of the floor height (a fixed 2.74 m would exceed the floor height at 0.5×); one component per record; size and count inputs optional (each keeps its record default; an input wired to no data is an error naming it); minimum storeys = the record's storeys; T6 with eight different programs over the keys; T4 through the per-key glazing (offices: no per-zone differences); GUIDs DOE Program Map `0e471c68-8cb1-4375-b82a-71b36d797b94`, DOE Small Office `c8f1e87b-b238-4b4f-a6de-c510d1e5d02b`, DOE Medium Office `e7998061-adad-41d7-a08f-aeb372863442`, DOE Large Office `8bb8e1b0-83e8-4cdf-b36b-3364315e6006`, Program Map parameter `ec21d323-a3c1-41d7-aed8-b1e13dab50df`.
- **Open, for the owner:** under D-045, *Stacked Floor Zone Multiplier* models the large office's ×10 floor at storey 6 (23.779 m), while the reference draws it at storey 5 (19.816 m), its lower middle storey; the large hotel's ×4 floor likewise (storey 3 against 2). D-045 is unchanged, because changing it would alter existing snapshots with even multipliers.
- **Checks:** `scripts/verify.ps1` on `ca725cd`: VERIFY PASSED, 0 warnings: Core 920, Generators 1161 (1 skipped, A2), Integration 3184, Export 3106 (1 skipped), ProgramJson 175, Simulation 205 (14 skipped), ConstructionJson 286, IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Rhino smoke on `36a61d8`: 19 specs, no failed check (`doe-offices` 16 scenarios, 14 checks). On the merge `4807c6e`: VERIFY PASSED with the same counts, and the full Rhino smoke check ran 19 specs with no failed check. A second agent reviewed the stage in three rounds; every finding is applied.
- **Pending:** T4 with the atlas's glazing (A2); A1 and A3; icons for the five new classes (stage C); for a person in Rhino 8, the toolbar group and the viewport previews.

### D-165 — DOE geometry stage P3: the school generator and its components

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P3; docs: [doe-school.md](../architecture/doe-school.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p3` (`536f242`).
- **Built:** `SchoolGenerator` (`Lod.Generators.Doe.School`, a `MultiStoreyPlanGenerator` over `DoeProgramMap`, ADR-015): the primary school (25 zones, one storey) and the secondary school (25/21 zones) from their records through `GridPlanLayout`; the defaults (`SchoolParameters.For`) reproduce the records vertex for vertex. The structure (classroom wings west of a spine; at least three source wings; each storey on the grid of the one below and standing on it) is found from cells and program keys, never from names (D-061), with the generator's tolerances (template cache keyed by school and distance tolerance). Grasshopper: *DOE Primary School* (`4f67ab4c-7c7e-4a27-afbe-8e76cd48097d`) and *DOE Secondary School* (`913bc6e4-ba40-4f81-949d-fc7d616ee1db`) on `DoeGeneratorComponent`, one per record; smoke spec `doe-schools`.
- **Parameters:** `WingCount` (minimum 2: the source's first and last wing; each wing between them repeats the source's middle wing with the court after it; copies are `_Wing{n}`), `Length` (S3 by slack; the main corridor's column fixed), `CorridorWidth` (the wing corridors only) and `ClassroomDepth` (every row; both at least `MinimumFixedBand`), `FloorHeight`. No plate-depth parameter: the depth follows from the wings and the source's courts (routine choice; "plate" in note §4 read as plate length).
- **Spine (S3 as amended, D-164):** the spine's cuts move through `GridAxis.Resize`: by slack within each end-wing row, kept in the first and last court, by slack within each middle-wing row and then along the span of every middle-wing copy; with two wings the source's middle is resized onto the single court. Every wing adjoins, zone by zone, the spine zones its source wing adjoins (pinned in T5 at 2, 3, and 6 wings; review round 1 found the first rule detached repeated wings from the main corridor, and it was replaced). Valid ranges: `Length` ≥ 18 m (primary) / 19 m (secondary); `CorridorWidth` ≥ 0.5 m; `ClassroomDepth` ≥ 2 m (secondary at every count; primary from three wings, 0.5 m at two); no upper limits; every limit at least ±20 % of its default.
- **Gaps:** G4 for the secondary school's gym, auxiliary gym, and auditorium (4 m storey height, ground storey only); walls against them on the first floor excluded by G4 (D-162).
- **Acceptance:** T1–T6 pass for both records. T4 runs on the generator path with one program per key (`programGlazing` via `HarnessFixtures.KeyGlazing`): totals, per key, and per zone within 1 % (no `glazingRatioDifferences`); the primary school's 13.38 m² of skylights pass per zone, per key, and in total. *Perimeter Core* at 4.57 m is `PlanTooNarrow` on the secondary school's first floor (a 9 m wide mechanical room, D-087, asserted); T6 and the smoke matrix run it at 4.0 m there.
- **Checks:** `scripts/verify.ps1` on `536f242`: VERIFY PASSED, 0 warnings: Core 920, Generators 1438 (1 skipped), Integration 3184, Export 3106 (1 skipped), ProgramJson 175, Simulation 205 (14 skipped), ConstructionJson 286, IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Full Rhino smoke on `6598d84`: 20 specs, no failed check (`doe-schools` 13 scenarios, 66 Validate True, 18 checks). On the merge `3149f94`: VERIFY PASSED (Generators 1438, 1 skipped) and the full Rhino smoke check, 20 specs with no failed check. A second agent reviewed the stage in four rounds; every finding is applied. Commit `4954e81`'s subject says "without gap exclusions"; the change leaves the gap-excluded zones out (history not rewritten).
- **Pending:** icons for the two components (stage C); A1–A3; for a person in Rhino 8, the toolbar group and the viewport previews.

### D-166 — DOE geometry stage P5b: the tower hotel and hospital generators and their components

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P5b; [ADR-025](ADR-025-doe-reference-geometry-generators.md), [ADR-026](ADR-026-multiplied-rooms.md), [ADR-015](ADR-015-plans-per-storey.md); docs: [doe-tower-hotel.md](../architecture/doe-tower-hotel.md), [doe-hospital.md](../architecture/doe-hospital.md), [doe-components.md](../architecture/doe-components.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p5b` (`7339a4c`); the smoke-test checklist, the smoke README, and `common.py` merged by keeping both stages' appended entries.
- **`TowerHotel`** (large hotel, three plans of 7 zones): `Storeys` (≥ 3; the typical plan stands for Storeys − 2 through `StoreyMultiplier`), `GuestRoomsPerRow` (the typical floor's two repeated rooms' multiplier, ≥ 2; the top floor keeps ×9), `Length`, `Depth`, `FloorHeight` (G5: the typical storey's 3.048 m). Along x only the run of copies is flexible, so one source bay (3.657 m) per added room follows the count on the typical floor (within the source's own 0.027 m², changing by 0.0067 m² per room; the top storey's copy space grows while its room stays ×9); along y the typical corridor band is fixed. Gaps G3, G5.
- **`Hospital`** (five plans, 9/11/13/13/8 zones, one plate with a copy space each): `RoomMultipliers` (17, in `MultipliedRooms` order, each ≥ 2, read-only), `PlateLength`, `PlateDepth`, `CorridorWidth` (the narrowest corridor leg, 4.572 m; every corridor band, a corridor rectangle at least 3 × as long as it is wide, scales with it; at least `MinimumFixedBand`), `FloorHeight`. Gap G3. `OR_NurseSat_Flr_2_Wall_1_East` is drawn outdoors (D-163).
- **Counts** change multipliers, not the drawing (ADR-026). **Limits** (S3 as amended, D-164), found by bisecting the generator's own check and cross-checked by hand: hotel `Length` ≥ 30.384 m, `Depth` ≥ 7.657 m; hospital `PlateLength` ≥ 35.908 m, `PlateDepth` ≥ 24.192 m, `CorridorWidth` 0.5–10.607 m; every limit at least ±20 % of its default; T5 tests the hospital's `PlateLength` at its limit in place of 0.5×.
- **Acceptance:** T1–T6 pass for both records. G5 excludes exactly the hotel's ground floor height, the elevations above it, and the ground storey's windows and their totals; each is checked against what G5 makes of it (+0.9144 m; × 3.048/3.9624). T4 runs one program per key; the hospital's six `glazingRatioDifferences` are reported, 210 per-zone window findings pass. P5: every total scales with the multipliers; *Semantic Merge* and *Conditioned Merge* never merge across multipliers and do merge zones of equal key and multiplier; *Perimeter Core*, *Single Zone per Floor*, and both single-zone aggregators are `NotSupported`.
- **Components:** *DOE Large Hotel* `8b61c4c7-2d19-4a1a-b83d-cea9254b634a`, *DOE Hospital* `da2d1dab-1994-420f-87d6-8cae8ea567a4` (one per family, on `DoeGeneratorComponent`; the room multipliers are a list input whose description names each room by index); smoke spec `doe-multiplied-rooms`.
- **Routine choices:** shared `Doe/MultipliedRooms/RecordGrid`; the hospital's leg aspect of 3; parameter equality compares the multipliers item by item; zone IDs are the source's; the source bay width and ground height read from the record.
- **Open, for the owner:** D-045 models the hotel's ×4 floor at storey 3; the reference draws storey 2. D-045 is unchanged (as D-164).
- **Checks:** `scripts/verify.ps1` on `7339a4c`: VERIFY PASSED, 0 warnings (Generators 1300, 1 skipped; Integration 3270). On the merge `e139a48`: VERIFY PASSED, 0 warnings: Core 920, Generators 1577 (1 skipped), Integration 3270, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Rhino smoke on `37a3d3e`: 20 specs, no failed check (`doe-multiplied-rooms` 12 scenarios, 31 checks). The full Rhino smoke check on `f19b6eb` (P5b and P6 merged): 22 specs, no failed check. A second agent reviewed the stage in two rounds; every finding is applied.
- **Pending:** A1–A3; icons (stage C); for a person in Rhino 8, the toolbar, the viewport previews, and the *Convert2BEM* `SelfAdjacent` output.

### D-167 — DOE geometry stage P6: the outpatient generator and its component

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P6; docs: [doe-outpatient.md](../architecture/doe-outpatient.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p6` (`f149455`); the smoke-test checklist and the smoke README merged by keeping both stages' appended entries.
- **Built:** `OutpatientGenerator` (`Lod.Generators.Doe.Outpatient`): three storeys of 59/41/26 zones (the note's 59/37/22 plus the G4 stair and lift copies) from the `outpatient` record, one plan per storey through `MultiStoreyPlanGenerator` and `GridPlanLayout`, presets by `DoeProgramMap` (32 keys). Parameters: `PlateLength`, `PlateDepth`, `CorridorWidth`, `FloorHeight`, `OrientationDegrees`; no counts. `OutpatientGenerator.SizeLimits`. Grasshopper: *DOE Outpatient* (`5d0c7a3e-9b41-4f6e-a8d2-3c1e7b590f64`) on `DoeGeneratorComponent`; smoke spec `doe-outpatient`.
- **S3 classes:** a corridor strip is a `Corridor`-type zone of one cell rectangle at least 3 times as long as wide (17 strips); its widths are fixed bands scaled by `CorridorWidth` over 1.8288 m (the most common strip width), each at least `MinimumFixedBand`; other intervals under 1 m are fixed; the rest (17 along x, 9 along y) share the plate by slack (D-164).
- **Limits (at the defaults):** plate at least 34.9832 × 26.3736 m; corridors 0.6–3.7538 m (the narrowest strip, the 1.524 m IT hall, reaches 0.5 m at 0.6 m); all reach ±20 %; T5 tests the 0.5× plates at their limits. Review found the first corridor rule had no lower limit (1e-6 m gave `OverlappingZones`); fixed.
- **Gaps and artifacts:** G4 stairs and lift drawn one zone per storey, excluded by their gap (T2 16 quantities, T4 20). The source's self-referencing walls between ×1 zones (398 of 448 `Surface` walls) and the reception hall's 26.52 m of south wall are interzone walls (D-162).
- **T4 (D-163):** one program per key; totals and 31 keys within 1 %; the 38 listed zone ratio differences reported, not failed.
- **Source facts against the note:** the outlines have 18 and 14 vertices (the upper storeys include the stair shafts), not 18 and 12. *Perimeter Core* needs a depth under half the east bay's north–south extent (1.0668 m at the defaults, 0.8048 m at the shortest plate); T6 runs it at 1 m and 0.8 m, and 4.57 m is `PlanTooNarrow` (asserted).
- **Routine choices:** `MinimumCorridorAspect = 3`; the default corridor width is the most common strip width; the G4 copies keep the ground storey's IDs; one component for the family; the smoke spec's GUID kept local to the spec.
- **Checks:** `scripts/verify.ps1` on `f149455`: VERIFY PASSED, 0 warnings (Generators 1215, 1 skipped; Integration 3356). On the merge `f19b6eb`: VERIFY PASSED, 0 warnings: Core 920, Generators 1631 (1 skipped), Integration 3442, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Rhino smoke on `3adb0de`: 20 specs, no failed check (`doe-outpatient` 11 scenarios, 16 checks). The full Rhino smoke check on `f19b6eb` (P5b and P6 merged): 22 specs, no failed check. A second agent reviewed the stage in two rounds; every finding is applied. The fixed-band tests were not written test-first (the builder's note).
- **Pending:** A1–A3; the icon (stage C); for a person in Rhino 8, the toolbar and the viewport.

### D-168 — DOE geometry stage P2: the single-storey generators and their components

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P2; docs: [doe-single-storey.md](../architecture/doe-single-storey.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p2` (`6bfb0ba`); the smoke-test checklist, the smoke README, and `common.py` merged by keeping both sides' appended entries.
- **Built:** `RestaurantGenerator` (full-service, quick-service), `StoreRowGenerator` (strip mall), `RetailBoxGenerator` (stand-alone retail), `SupermarketGenerator`, `WarehouseGenerator`, each a `PlanGenerator` on its layout record's grid with a `DoeProgramMap` and its `ProgramKeys`; parameter records with `Default` read from the record (rounded to its 1e-6 m, `RecordDecimals`, tied to `extract.py`); provenance `Record`, `Gaps`, `Source` (reference file and SHA-256; `DoeLayoutRecords.ReferenceRole`). Grasshopper: one component per record on `DoeGeneratorComponent`: *DOE Full-Service Restaurant* `b4ca8365-a4dc-4af7-a6b5-0fc68cdb37a9`, *DOE Quick-Service Restaurant* `cf72627b-3035-4f91-858c-f51772989c07`, *DOE Strip Mall* `94be46f9-90c9-49ec-8104-8d572004856e`, *DOE Stand-alone Retail* `1bf76d74-0917-4acc-8d9c-e0eaa36adcbe`, *DOE Supermarket* `2f12351b-adfd-40aa-a763-be4394bd814b`, *DOE Warehouse* `814d27a4-8483-4aba-bf78-2bf4daa62f46`; smoke spec `doe-single-storey`.
- **Parameters (two deviations from note §4, accepted by the controller because §4 as written contradicts its own T5):** restaurant `Length`, `DiningDepth`, `KitchenDepth`, the plate depth their sum, no kitchen-smaller rule (with the plate depth fixed, T5's 2× quick-service kitchen, 15.24 m, would fill the 15.24 m plate); warehouse `Length`, `Depth`, `OfficeDepth`, `FineStorageDepth`, the office width flexible (a fixed 25.91 m office cannot fit T5's 22.86 m half plate). Also: strip mall `Depth`, `LargeStoreWidth`, `SmallStoreWidth`, `Stores` (runs of size, tenancy, count, west to east; IDs `LGstore<n>`/`SMstore<n>` in row order; in Grasshopper three lists, sizes read in any case); stand-alone retail `Length`, `Depth`, `BackSpaceDepth`, `FrontDepth` (one band, the entry its source half), `EntryWidth` (centred); supermarket `Length`, `Depth`, `StorageDepth`, `PreparationDepth`.
- **S3 (D-164):** bands a parameter sets at least `MinimumFixedBand`; flexible intervals share a change by slack; a band changed past its maximum is named in its error. Every size reaches ±20 % of its default and 0.5× and 2× are valid for all six records; the range table in the family doc gives validity limits, not plausibility (the warehouse is valid down to a 2 m length with a 1 m office). The amended rule changed the warehouse office's and the supermarket's flexible shares (T5 expectations updated).
- **Gaps:** G2 restaurants (flat roof at the zone top); G4 warehouse (office to the storey height, fine-storage floor above it dropped; D-161, D-162).
- **Acceptance:** T1 (elevation and multiplier from a `Stack` of the plan), T2, T3; T4 on the generators' path with `HarnessFixtures.KeyGlazing` (totals and per key within 1 %, every zone; no ratio differences in the six records); T5 (0.5×, 1×, 2×, each limit and just beyond, bands at 0.5 m and just below, strip-mall counts at 1 and 2×; every zone's area and part height); T6 (7 simplifiers × 4 aggregators, canonical and two rotated placements; determinism; snapshots).
- **Routine choices:** one component per record; shared code in `Doe/SingleStorey/` (source and tests); a null or unknown store run, lists of different lengths, and a size other than Large/Small are `InvalidParameter`; the strip mall lists all three tenancy keys; T6 in `Lod.Generators.Tests` with one floor entry.
- **Checks:** `scripts/verify.ps1` on `c06d5a3`: VERIFY PASSED, 0 warnings (Generators 1910, 1 skipped). On the merge `011edbc`: VERIFY PASSED, 0 warnings: Core 920, Generators 2380 (1 skipped), Integration 3442, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Rhino smoke on `c06d5a3`: 20 specs, no failed check (`doe-single-storey` 28 scenarios, 134 Validate True, 41 checks). The full Rhino smoke check on the merge `011edbc`: 23 specs, no failed check. A second agent reviewed the stage in four rounds; every finding is applied.
- **Pending:** icons (stage C); for a person in Rhino 8, the toolbar group and the viewport previews; A1–A3.

### D-169 — DOE geometry stage P4: the corridor hotel generator of the small hotel, its bay axis, and the DOE Small Hotel component

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage P4; docs: [doe-corridor-hotel.md](../architecture/doe-corridor-hotel.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p4` (`824a63b`); the smoke-test checklist, the smoke README, and `common.py` merged by keeping both sides' appended entries.
- **Built:** `CorridorHotelGenerator` (one plan per storey, ADR-015) and `CorridorHotelParameters`, whose `Default` reproduces `small-hotel` (19/16/16/16 zones, 54.8646 × 18.2886 m, 4 storeys of 2.7432 m). `CorridorHotelTemplate` reads the structure from the record's cells and keys (D-061), with the generator's tolerances: bays are the x intervals under the typical storey's north `GuestRoom` zones (11 of 3.9624 m), each its own flexible interval (bay cuts no storey uses split the run of three), so S3 by slack keeps them equal; the stairs, storage, lift lobby, and lift (11.2782 m) are fixed. `GridAxis.Map` takes an optional index remap for an axis of another interval count (without it the equal-count rule holds unchanged). Grasshopper: *DOE Small Hotel* (`7b31e279-617d-4a06-a7c9-e8824b7ae396`) on `DoeGeneratorComponent`; smoke spec `doe-hotel`.
- **Parameters and limits (S3 as amended, D-164):** `Length` ≥ 11.2782 m plus 1 m per bay (22.2782 m at 11 bays); `RoomDepth` (the rows' mean, source ratio kept) ≥ 0.500018 m and `CorridorWidth` ≥ 0.5 m (`MinimumFixedBand`); `GuestRoomBays` 9 to 43 at the default length, the change added to or removed from the run of three bays no storey divides; `StoreyCount` ≥ 2, storeys above the record repeat its top storey; `FloorHeight` > 0. Every size parameter is valid at 0.5× and 2× and reaches ±20 %.
- **Deviation from S3's wording:** S3 lists the room bay as a fixed dimension; P4 makes the bays flexible and the service intervals fixed, the only reading that keeps both `Length` and `GuestRoomBays` as parameters (accepted by the controller). Review round 1 found that a run of three bays as one interval would part the bays under the amended S3; one interval per bay fixed it.
- **G5:** one floor height, the typical storey's 2.7432 m (source ground 3.3528 m). Excluded and checked against their G5 values: the ground storey's floor height (the upper storeys' are compared), the elevations above the ground (−0.6096 m), the ground storey's windows (× 2.7432/3.3528), and the window totals in all and per key where the ground storey glazes (each key's source total less (1 − 2.7432/3.3528) of its ground share, resting on a test that each key's window area is its ratio times its zones' true outdoor walls).
- **T4 (D-163):** one program per key through `DoeProgramMap`; totals per orientation and per key within 1 %. Through a program map the per-zone windows of `GuestRoom` (0.124 ground and 0.151 upper, N and S, 0.191 S for 206–208, against the key's 0.149 N and 0.158 S) and `Corridor` (E/W) are not the source's: the answer key's 43 `glazingRatioDifferences` are reported and the list is checked exact.
- **Routine choices:** bay count at a fixed length (at 22 bays the bays are 1.98 m); copy IDs drop the source floor suffix and take `_Flr{n}` (`Corridor_Flr5`; guest rooms keep their room number, `GuestRoom401_Flr5`); minimum counts 2 storeys and 9 bays; one component for the family's one record; `SizeLimits` (the base class has a `Limits`).
- **Checks:** `scripts/verify.ps1` on `824a63b`: VERIFY PASSED, 0 warnings (Generators 1231, 1 skipped; Integration 3326). On the merge `bc679c7`: VERIFY PASSED, 0 warnings: Core 920, Generators 2450 (1 skipped), Integration 3584, Export 3106 (1 skipped), ProgramJson 175, Simulation 205 (14 skipped), ConstructionJson 286, IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Rhino smoke on `266c674`: 20 specs, no failed check (`doe-hotel` 11 scenarios, 49 Validate True, 19 checks). The full Rhino smoke check on the merge `bc679c7`: 24 specs, no failed check. A second agent reviewed the stage in two rounds; every finding is applied. The merge `1534628` and `e25ca56` on the stage branch are not green on their own; `f36363d` and later are.
- **Pending:** the icon (stage C); for a person in Rhino 8, the toolbar group and the viewport previews; A1–A3.

### D-170 — DOE geometry stage C: the close-out, the icons of the DOE components, and the sync-docs pass

- **Date:** 2026-10-26 · **Decided by:** the controller under D-098, pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md), stage C (status now Done, pending the owner's reading); docs: [doe-components.md](../architecture/doe-components.md), [doe-layouts.md](../architecture/doe-layouts.md), [pipeline.md](../architecture/pipeline.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-c` (`b973cac`); the merged tree equals the stage tip.
- **Icons.** `scripts/make_icons.py` draws 17 new icons, one per new class: *DOE Program Map* and the *Program Map* parameter (*Program* accent) and the 15 DOE generator components (*Generate* accent), each from its reference building and distinct from the others and from the six precedent generators (table in doe-components.md). The 69 existing icons are byte-identical; a rerun of the script reproduces all 86 byte for byte.
- **Sync-docs pass.** README (version label 1.4.0, scope, layout, not yet released), AGENTS.md (one project-state bullet), the pipeline doc (panel rows including *DOE Program Map*, the DOE-generators bullet, open items, related documents), doe-layouts (the family table), doe-components (all 15 components with GUIDs, the icons), the family docs (checked against D-161 to D-169, gaps filled), ADR-012's status (skylights, D-162), and the smoke checklists. The public site follows at the next tag: export the tagged commit, import it in the docs repository, run its `sync-docs`.
- **Small code items.** The `GridAxis.Resize` shortest-length message leaves out the fixed length when an axis has no fixed interval (one pinned test changed, one added); the shared description text of the DOE components no longer cites a decision number (sync-docs, D-118).
- **Decision log.** D-097 is marked "Refined by D-160" in its status (its text unchanged).
- **Checks.** `scripts/verify.ps1` on `b973cac` and on the merge `f7f8b59`: VERIFY PASSED, 0 warnings: Core 920, Generators 2451 (1 skipped, A2), Integration 3584, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. The full Rhino smoke check on `6d4e331` (plugin sources equal the final commit's): 24 specs, no failed check, every icon 24 × 24; the metadata dump lists 85 objects and no gap. A second agent reviewed the stage in two rounds; every finding is applied.
- **Open, for the owner.** The reading of D-160 to D-170 and ADR-025, ADR-026; D-045's representative storey of a multiplied floor (D-164); for a person in Rhino 8: the toolbar and the icons as drawn, the viewport previews, the *Convert2BEM* `SelfAdjacent` output, skylights in the viewport and in an EnergyPlus run; atlas inputs A1–A3 (A2 on the true-outdoor-wall basis, D-162, D-163).

### D-171 — DOE geometry stage P7: the DOE program-map presets

- **Date:** 2026-10-26 · **Decided by:** Cheng Xuan Li (the request, and the values: illustrative example presets with the source's glazing per key; design note §9); the controller under D-098 (the Service fallback, the source glazing of keys under a gap, their realisation), pending the owner's reading · **Status:** Accepted by the owner's approval of PR #1 (D-176)
- **Design note:** [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md) §9, stage P7; [ADR-025](ADR-025-doe-reference-geometry-generators.md) (consequence amended); docs: [doe-components.md](../architecture/doe-components.md#doe-program-presets), [doe-layouts.md](../architecture/doe-layouts.md). Merged into `feature/doe-geom` with `--no-ff` from `feature/doe-geom-p7` (`b1e0774`); the merged tree equals the stage tip.
- **Why:** the owner accepts the program map (S4) as the current design and asks for a ready preset for every DOE plan generator, so each can be used and tested without assembling a map by hand.
- **Shipped glazing.** `extract.py` writes each record's per-key glazing into the layout record (`programGlazing`, record format version 2; answer keys byte-identical; `--check` passes): every key once, in ordinal order, its WWR N/E/S/W and skylight ratio, and its basis: `true_outdoor_wall` (the answer key's `programGlazing`, D-162, D-163), `office_reference` (the offices' `officeGlazing` on every orientation), `gap_source_wall` (every zone of the key under a gap: the same rule with the gap zones and orientations counted and the skylight over the source roof, from the source only), or `interior` (no counted outdoor wall or roof, no ratio; 4 hospital and 7 outpatient keys). The loader rejects an unknown basis, an `interior` key with a ratio, any other key without one, and a `gap_source_wall` key with a zone outside a gap.
- **Built:** `DoeProgramPresets.For(DoeBuildingType)` (cached; `Create` builds anew): one preset per key of the generator's `ProgramKeys`, the illustrative example preset of the key's space type (residential examples for Corridor and Stair) renamed to the key, with the record's glazing. A key whose space type has no example preset (Mechanical, Other) takes the example Service preset as an any-program preset named `<key> (Example Service)`, recorded by the plan as `AnyProgramPreset.<key>`. Keys under a gap (warehouse Fine and Office, secondary school Auditorium, Gym, Gym - audience, outpatient Stair) keep the source's glazing of their zones, so their window area differs from the source's by what the gap changes, described per record (the warehouse office drawn to the 8.534 m storey height doubles its walls and windows, S 11.15 to 22.31 m², W 6.51 to 13.01 m²; the secondary school's 8 m tall zones at 4 m halve theirs; the outpatient stairs and lift drawn per storey); the harness's T4 exclusions are unchanged. Each map carries one shared provenance source (`DoeProgramPresets`: record, reference SHA-256, loads, glazing, Service fallback, gap glazing). Service-fallback keys per record: small, medium, large office 2, 3, 5; restaurants 0, 0; strip mall 0; stand-alone retail 1; supermarket 5; warehouse 2; primary, secondary school 2, 3; small hotel 9; large hotel 7; hospital 12; outpatient 22.
- **Components:** fifteen output-only *DOE … Programs* in panel *1 Program Presets* (secondary exposure), one per DOE generator component, outputs *Program Map*, *Keys*, *Presets*, with remarks that the loads are illustrative example values and the glazing is the source's for each key's zones, naming the fallback keys, and naming the keys under a gap with the record's gap change; icons drawn by `make_icons.py`, the 86 existing icons byte-identical; GUIDs in doe-components.md.
- **Acceptance:** for every record the map's keys are the generator's, every preset has its space type or is the fallback, its glazing equals the record's and the answer key's, the defaults validate, every supported simplifier × aggregator validates; T4 runs through the shipped map in every family's acceptance tests with the same G4 and G5 exclusions; two maps built apart describe alike; the stacked glazing totals are pinned; no snapshot changed.
- **Routine choices:** the fallback name suffix; the shared provenance source; office keys take the reference ratio on every orientation; the `interior` basis (a key with no outdoor surface); nicknames `<generator nickname>P`.
- **Checks:** `scripts/verify.ps1` on `f74e867` and on the merge: VERIFY PASSED, 0 warnings: Core 920, Generators 3051 (1 skipped), Integration 3584, Export 3106 (1 skipped), ConstructionJson 286, ProgramJson 175, Simulation 205 (14 skipped), IdfBatchRunner 88 (3 skipped), TestSuiteGenerator 119. Full Rhino smoke on `f74e867` (the merged code): 25 specs, no failed check (`doe-presets` 93 checks, among them a preset replaced and rebuilt with *DOE Program Map*). A second agent reviewed the stage in three rounds; every finding is applied.
- **Pending:** A1–A3 (the loads stay illustrative until then); for a person in Rhino 8, the toolbar group, the icons as drawn, and the viewport.

### D-172 — Atlas release 2.0.0: program JSON 5.4.0 and constructions 4.3.0 / 3.1.0 only, daylighting controls carried as given, written only on request

- **Date:** 2026-10-28 · **Decided by:** Cheng Xuan Li (the request of 2026-10-28: move BEMGen to atlas release 2.0.0, apply the atlas's handoff note, fixtures exported from the release); the controller (the compatibility decision and the realisation), pending the owner's reading · **Status:** Provisional; refined by D-173 and D-174 · **Supersedes in part:** D-126 (the program JSON 2.0.0 reader), D-145 (the packet v7 pin; its reference material stays) · [ADR-027](ADR-027-atlas-release-2-0-0-contracts.md), [design note](../plans/2026-10-28-atlas-release-2-0-0.md)
- **Compatibility.** BEMGen reads only the release 2.0.0 contracts: program JSON 5.4.0 (`source` and `filled`), detailed constructions 4.3.0, unified 3.1.0. Program JSON 2.0.0 and the packet v7 versions (detailed 3.0.0, unified 2.0.0) are refused with a message to export again. Why: release 2.0.0 is the only atlas release and its exporters refuse 1.x; D-064 waives backward compatibility; D-126 and D-145 retired earlier readers the same way; the program contract changed shape; the construction change is additive, and the 19 packet v7 contexts re-exported from 2.0.0 have equal values (within 2e-9 relative).
- **Program JSON 5.4.0.** Both versions; *Climate Zone* and *Context* inputs appended to *Program JSON* (GUID unchanged) resolve values by climate and loads by `applies_with`; *WWR* has no default, so the JSON's `fenestration` gives the glazing when no input does; the source version's unrecorded values are left out or take BEMGen's defaults with `ProgramJsonValueNotRecorded`; exterior lighting, building-level water heating, humidity setpoints, water-use gains, and building services are listed in *Left Out*.
- **Handoff item 1, daylighting.** `lighting_controls` becomes `ZoneProgram.Daylighting` as given (never recomputed from geometry; source zero and `unknown` give none; floor fraction and zone counts are provenance); a merge conserves the controlled lighting power. *Convert2IDF* can write one reference point per glazed zone (`IdfOptions.WriteDaylighting`) but **leaves it out by default**: with the controls written, the opt-in EnergyPlus end-to-end test failed the hourly lighting pairing check (D-157, GLOBAL.md scientific rule 1) in every zoning, so the handoff note conflicts with the owner's pairing rule. The owner decides whether daylight dimming is measured as a geometry effect or held fixed.
- **Handoff item 2, IDs.** BEMGen stores no 1.x or 2.0.0 atlas ID: a scan of `feature/doe-geom` found none of the 11,507 `id-map.json` keys. The v0.x IDs in tests and the synthetic glazing fixture were re-keyed to the 2.0.0 IDs of the same program or construction context by structural matching; the DOE presets hold no atlas IDs.
- **Handoff item 3, alternates.** Read as information (`DetailedConstructionDocument.Alternates`, *Roles* lines), never assigned.
- **Water mains.** A hot-water inlet `CorrelationFromWeatherFile` is `WaterTemperatures.InletFromWeatherFile`, written with `Site:WaterMainsTemperature`.
- **Atlas defects reported:** the IECC construction sets carry mass-entry `evidence_id`s the shared mass contract forbids, and file the ground storey core's F-factor floor under `InteriorFloor`; both make BEMGen refuse them. Minor: the 5.4.0 schema's daylighting description predates L-1; some fitted values moved by one ULP; alternate area shares are rounded to six decimals.
- **Open:** the owner's decision on daylighting in the IDF; rebuilding `examples/program-json-office.gh` in Rhino; *Convert2BEM* daylighting output; the IECC zone design-flow infiltration; PNNL alternates as geometry; building services and source model constructions; the merge and the push.

### D-173 — Atlas release 2.0.0 as corrected in place: shared mass contract 1.1.0, the IECC ground slabs under GroundFloor, fixtures re-pinned to atlas `f617b30b`

- **Date:** 2026-10-28 · **Decided by:** Cheng Xuan Li (the request of 2026-10-28: take the corrected release); the controller (the realisation), pending the owner's reading · **Status:** Provisional; refined by D-174 · **Refines:** D-172 (its fixture pin and the two IECC defects it reported) · [ADR-027](ADR-027-atlas-release-2-0-0-contracts.md) (amended), [design note](../plans/2026-10-28-atlas-release-2-0-0.md) §3–§5
- **Why a new entry.** D-172's report led the atlas to correct release 2.0.0 in place (atlas PR #28, merge `f617b30b1ca1552364af648a82797d2b39854c01`; its handoff note section 4 and ADR 0046 section 11). The log's rule is not to rewrite a past entry, so this one records what changed; D-172's status says it is refined here.
- **Mass contract 1.1.0.** `construction-mass-accounting-v1.1.schema.json` (`urn:archetype-atlas:construction-mass-accounting:1.1.0`, 1.0.0 with the optional mass-entry `evidence_id` that detailed 4.3.0 and unified 3.1.0 embed) replaces 1.0.0 as the embedded schema `Lod.ConstructionJson` checks the `mass_accounting` section against, byte for byte. Nothing BEMGen reads needs 1.0.0, so it is not kept beside it. The field is still typed by the contract (a non-empty string; a test pins an empty one as `ConstructionJsonSchemaViolation`); it is provenance and is not resolved.
- **Program JSON 5.4.0 schema.** The atlas changed only the `lighting_controls.daylighting` description ("applied as given", L-1); the new file is embedded in `src/Lod.ProgramJson/Schemas/` and copied to the fixtures, byte for byte. The seven program exports are byte-identical to D-172's.
- **IECC ground-floor erratum.** In the five affected IECC types (Medium and Small Office, Outpatient, Primary and Secondary School) of every edition, the adiabatic F-factor slabs with `PerimeterExposed` 0 moved from `InteriorFloor` (with a `Ground` condition) to the `GroundFloor` building default, their selection decision rule `source_boundary_correction`; 30 set IDs changed. Of the fixture set and program IDs only `medium-office-iecc-2021-5B`'s is in the release's `id-map.json` (`iecc-2021.medium-office.construction-package.8e0c58` to `…a8a7b6`); the exporter's list takes the new ID. BEMGen had no workaround to remove: it refused the old documents and its check that only `GroundFloor` and `FoundationWall` assignments may name a ground method stays, now pinned by a synthetic test on the 90.1 office, since the IECC fixture no longer trips it. A test pins `Core_bot_ZN_5_Floor` in the `GroundFloor` assignment with its ground method and no `InteriorFloor` assignment with one; the F-factor method takes the exposed perimeter from BEMGen's geometry.
- **What the IECC fixture now does.** Both documents of `medium-office-iecc-2021-5B` are read with full closure and one diagnostic, the warning `ConstructionJsonInfiltrationMethodNotSupported`; the unified set refuses conversion (`AssignmentUnavailable`) for its source design-flow infiltration alone, and a test shows the same document with the 90.1 office's building-level infiltration converts without a warning. The atlas answered that this infiltration is the source's method, recorded faithfully, and that a building-level equivalent belongs to its deferred IECC unified representation, so BEMGen keeps the refusal (ADR-027 decision 6). The fixture joins the full-closure foundation test (42 documents); it stays out of `Packet.Names`, whose building-scope sets convert, as `Packet.NotConvertible` (was `Refused`).
- **Not changed (atlas: not defects).** Absorptances such as 0.44999999999999996 are IEEE area-weighted means (the two tests that assert them are unchanged); alternate `area_share` values are rounded to six decimals and BEMGen does not check their sum.
- **Fixtures.** `python scripts/atlas-fixtures/export_fixtures.py --atlas <checkout>` re-exported every fixture at `f617b30b` (release manifest SHA-256 `b7ce92a1694a85b42746bdc57ffa0ed1f21f11384561184af078d95a4865e40e`, checked against the file); the manifests, `PacketTests`, `SchemaTests`, both fixture READMEs, and the design note carry the new pins. Only the two IECC documents differ in value; the other 40 construction documents are equal as JSON, and 15 of them differ in bytes only by key order.
- **Exporter pins the hash seed.** The first `--check` after the re-export failed on 17 example documents and the manifest, all equal as JSON: the order of some keys in the atlas's exports follows Python's string hashing (one export run under `PYTHONHASHSEED` 0, 1, 2, 0 gave the same bytes for the two runs with seed 0 and other bytes for 1 and 2), so D-172's byte-for-byte check held only by chance. `export_fixtures.py` now runs the atlas with `PYTHONHASHSEED=0`; the comparison stays byte for byte. Reported to the atlas as a determinism finding; BEMGen does not change the atlas.
- **Unchanged:** `IdfOptions.WriteDaylighting` stays off by default (the owner's decision on D-157 pending, D-172).
- **Checks:** the new tests failed first for the expected reason (the IECC mass entries' `evidence_id` refused under 1.0.0, and the 1.1.0 schema not embedded). `export_fixtures.py --check` with the atlas at `f617b30b`: CHECK PASSED, run twice (the second from a shell with `PYTHONHASHSEED=7`). `scripts/verify.ps1` on the working tree of the commit: VERIFY PASSED, 0 warnings: Core 938, Generators 3051 (1 skipped), Integration 3584, Export 3135 (1 skipped), ConstructionJson 311, ProgramJson 200, Simulation 247 (14 skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119. `python scripts/docs-export/developer_pages.py --check`: 94 pages checked. No Rhino smoke run.
- **Open:** as D-172, less the two IECC defects: the owner's decision on daylighting in the IDF; rebuilding `examples/program-json-office.gh` in Rhino and the smoke checklist's *Construction JSON* line for the IECC set; the IECC zone design-flow infiltration; PNNL alternates as geometry; building services and source model constructions; the merge and the push.

### D-174 — No daylight dimming in IDF runs, ever: the daylighting writer removed, the controls kept as source data

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (the decision); the controller (the realisation), pending the owner's reading · **Status:** Accepted (the decision); the realisation Provisional · **Answers:** the daylighting question D-172 and D-173 left open · **Refines:** D-172, D-173 · [ADR-027](ADR-027-atlas-release-2-0-0-contracts.md) (amended), [design note](../plans/2026-10-28-atlas-release-2-0-0.md) §3, [convert2idf.md](../architecture/convert2idf.md#daylighting-d-172-d-174)
- **Decision.** The owner, 2026-10-29: "let's not include dimming for our idf runs ever". Daylight dimming is held fixed as part of the lighting load and is never measured as a geometry effect (GLOBAL.md scientific rules 1 and 4). The evaluation metrics' pairing check (D-157) stays as it is.
- **Removed, so that "never" holds in the code.** `IdfOptions.WriteDaylighting`; the writer's per-zone `Daylighting:ReferencePoint` and `Daylighting:Controls` (`IdfWriter.Daylighting`, the records `IdfDaylightingControls` and `IdfDaylightingReferencePoint`, `IdfNameKind.Daylighting`, `IdfDefaults.DaylightingReferenceHeight`); the run check's expected warning `PartialDaylightingControl` (`ExpectedWarnings.Default` is again `ZoneFloorArea` alone, so EnergyPlus's daylighting warning would fail a run); its row in `scripts/eplus-check/README.md`; and the export test that wrote the controls on request across the simplifier × aggregator matrix. `IdfDefaults`, `IdfNames`, and `RunVerdict.cs` equal their state before D-172. No opt-in EnergyPlus end-to-end variant wrote daylighting, so none was removed.
- **Nothing made inert.** No Grasshopper component had an input or output for the option (*Convert2IDF* never exposed it, D-172), so no component's parameters or GUID change.
- **Kept.** *Program JSON* still reads `lighting_controls` into `ZoneProgram.Daylighting`, and a merge or mix still conserves the controlled lighting power (D-172): source data and provenance, never written to an IDF. A building whose programs carry controls gets the header line `Daylighting: never written (D-174); n zone(s) with controls in their programs` and the info `DaylightingNotWritten` naming the zones; a building without controls is written as before, so no snapshot changes. *Convert2BEM* does not output the controls either.
- **Tests.** `IdfChecks` (the parse-back checks every export test runs) now fails any IDF with a record whose class starts with `Daylighting`; `AnIdfOfAProgramWithDaylightingControlsHasNoDaylightingObjects` converts the 90.1 medium office program, whose zones carry controls, and finds no daylighting object; `ADaylightingControlWarningIsOffTheListAndFailsTheRun` replaces D-172's test that accepted the warning. The new assertions failed first for the expected reasons (the old header and diagnostic text, the warning still on the list) before the writer was removed.
- **Docs.** convert2idf.md (the daylighting section), program-json.md, program-presets.md §7, ADR-027 (decision 4 and the consequences), the design note, the smoke checklist and the `program-json` smoke spec, the eplus-check README, AGENTS.md.
- **Checks:** `scripts/verify.ps1` on the working tree of the commit: VERIFY PASSED, 0 warnings: Core 938, Generators 3051 (1 skipped), Integration 3584, Export 3108 (1 skipped; 27 fewer than D-173: the 28 cases of the removed opt-in theory, one new test), ConstructionJson 311, ProgramJson 200, Simulation 247 (14 skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119. `python scripts/docs-export/developer_pages.py --check`: the developer pages' links. No Rhino smoke run and no EnergyPlus run.
- **Open:** for a person in Rhino 8, the smoke spec `program-json` with its new header check; whether *Convert2BEM* should ever output the controls (the decision names IDF runs; nothing is output today); the merge and the push of PR #2.

### D-175 — Version 1.5.0: DOE reference geometry, native ground, the evaluation tools, and atlas release 2.0.0, for the geometric LOD study

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (the request of 2026-10-29: "close everything up and ship a stable release" so that the geometric LOD study can start); the controller (the preparation) · **Status:** Accepted (the request); the release itself waits on the owner's tag, push, and publication
- **Version.** 1.5.0, prepared on `release/v1.5.0` from `main` at `54f990d`, a minor version as D-125 reasons: D-064 waives backward compatibility, and no component or parameter GUID changed or moved since `v1.4.0` (every one of its 69 GUIDs is still in the same source file; 32 are new). It adds components and appends inputs; nothing is removed from a component.
- **What it merges since `v1.4.0`** (273 commits on `main`):
  - **Construction foundation v7 and native ground** (D-145 to D-150, [ADR-023](ADR-023-native-ground-methods-and-packet-v7.md)): a construction set's ground floors take its own F-factor or layered ground, with ground temperatures from the weather file (F-factor) or 18 °C (layered); the warning `ExampleWindowSolarNotAbsorbed` (D-147); turned plans with courts (D-148, D-149).
  - **Evaluation tools** (D-151 to D-159): test suites with construction sets paired by climate; the hourly ground heat transfer in the research outputs; the batch runner's progress, site status, and results folder (central schema version 7, hourly Parquet per site); the paired evaluation metrics and the timing pass. These are tools, not part of the plugin.
  - **DOE reference geometry generators** (D-160 to D-171, [ADR-025](ADR-025-doe-reference-geometry-generators.md), [ADR-026](ADR-026-multiplied-rooms.md), PR #1): 11 generators for the 15 DOE commercial building types, 15 *DOE* components, *DOE Program Map*, 15 *DOE … Programs* presets (illustrative loads, the source's glazing per program key), glazing per orientation and skylights on every preset, and multiplied rooms with the `SelfAdjacent` boundary.
  - **Atlas release 2.0.0 contracts** (D-172 to D-174, [ADR-027](ADR-027-atlas-release-2-0-0-contracts.md), PR #2): *Program JSON* reads program JSON 5.4.0 (`filled` and `source`) with *Climate Zone* and *Context*; *Construction JSON* reads detailed 4.3.0 and unified 3.1.0 with the shared mass contract 1.1.0; hot water can take the weather file's water mains; daylight dimming is never written to an IDF (D-174).
- **Made in this preparation.**
  - The version in `Directory.Build.props`; the 20 example definitions rebuilt with the 1.5.0 plugin (`BEMGEN_EXAMPLES_WRITE=1`), `program-json-office.gh` now with the 5.4.0 filled export of the 90.1-2019 medium office.
  - The `construction-json` smoke spec gains the checklist's IECC line: the IECC 2021 medium office is read with only its infiltration warning, and *Convert2IDF* refuses it for its source design-flow infiltration. Its first run failed one check: *Construction JSON* also gave the warning "A detailed document: … connect the unified document of the same context" for this unified document, because the component showed it for every set that refuses assignment. The warning now shows only for a detailed document; the run then passed. The component's description now names unified 3.1.0 and detailed 4.3.0 (it still said 2.0.0 and 3.0.0). No GUID, input, or output changed.
  - The sync-docs pass (below).
- **Checks on the release candidate:**
  - **Examples.** All 20 rebuilt with the 1.5.0 plugin; each reopened and solved with one *Validate* True and no warnings, errors, or exceptions, in the rebuild and in the full run below.
  - **Definitions saved with 1.4.0.** The 20 example files as committed before the rebuild (saved with the 1.4.0 plugin) reopened with the 1.5.0 plugin: every archive read without a warning or error (no *Grasshopper IO* dialog), and 19 solved with one *Validate* True; `program-json-office.gh`, holding program JSON 2.0.0, gave the error `ProgramJsonVersionNotSupported` asking for an export from atlas release 2.0.0, as the release notes say.
  - **Rhino smoke.** All 25 specs of `scripts/rhino-smoke` in Rhino 8.25.25314.11001 on the final code: 1514 *Validate* True and none False, 911 spec checks passed and none failed (the IECC check and `program-json`'s D-174 checks among them: no daylighting object, the header `Daylighting: never written (D-174)`), no exception, missing component, or missing expected error; runtime errors only in the error scenarios and, in the DOE specs, on the component placed without a program map, as in their stage runs.
  - **`scripts/verify.ps1`** on the candidate's tree: VERIFY PASSED, 0 warnings: Core 938, Generators 3051 (1 skipped), Integration 3584, Export 3108 (1 skipped), ConstructionJson 311, ProgramJson 200, Simulation 247 (14 opt-in skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119.
  - **Fresh-clone gate.** A clean clone of `release/v1.5.0` at `4efc1a8` (`D:\BEMGen-gate\v1.5.0`) passed `scripts/verify.ps1` with 0 warnings: Core 938, Generators 3051 (1 skipped), Integration 3584, Export 3108 (1 skipped), ConstructionJson 311, ProgramJson 200, Simulation 247 (14 opt-in skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119. The commit that records this changes only this entry.
- **Sync-docs.** Applied: README (version, the 1.5.0 paragraph), AGENTS.md (the Done line and the stage bullets' release state), the statuses of the plans of D-145 to D-174, the roadmap's progress log, `examples/README.md` (the rebuilt Program JSON example), the smoke README (the IECC check), ADR-027 and the atlas design note (the example rebuilt), the *Construction JSON* description. Recorded, not done here: the public site still describes 1.4.0 (`reference-source.json` at `e6c073e`); the docs export of the tagged commit, its import in the docs repository, and that repository's own `sync-docs` follow the tag.
- **Release notes.**
  - **What opens differently.** Definitions saved with 1.4.0 open with their saved values. *Program JSON* shows two new inputs, *Climate Zone* and *Context*, unset, and its *WWR* no longer has a default: without a WWR input the JSON's `fenestration` gives the glazing, else 0.4. A *Program JSON* or *Construction JSON* holding an older atlas text (program JSON 2.0.0, unified 2.0.0, detailed 3.0.0) now gives an error asking for a release 2.0.0 export; give it the new text. The preset components show the appended inputs *WWR North*, *WWR East*, *WWR South*, *WWR West*, and *Skylight Ratio*, unset.
  - **What IDFs change.** Every IDF with ground floors requests the hourly inside-face conduction of each ground surface and `Output:Surfaces:List, Details` (D-151). With a construction set, ground floors take the set's own F-factor (`GroundFCfactorMethod`, ground temperatures from the *Weather* file, which is then required) or layered ground (18 °C) instead of the Example's ground floor. A program from *Program JSON* 5.4.0 changes its loads to the atlas's release 2.0.0 values, and a filled program's hot water takes the weather file's water mains (`Site:WaterMainsTemperature`). Presets with per-orientation glazing or skylights write those windows. An IDF written without these is unchanged.
  - **Daylighting.** Programs from the atlas may carry daylighting controls; *Convert2IDF* never writes them (no `Daylighting:Controls` or reference points; D-174): daylight dimming is held fixed as part of the lighting load. The IDF header says so and names the zones.
  - **New:** the 15 DOE generators and their presets; IECC construction sets are read but do not convert (their per-zone design-flow infiltration).
- **What follows:**
  - the owner's tag `v1.5.0`, push, and the release on the docs repository's GitHub Releases (D-118) with the files of `scripts/package-release.ps1` built again from the tagged commit (the files built here are drafts, since the commit is not tagged);
  - the docs export of `v1.5.0`, imported by the docs repository, which runs its own `sync-docs`;
  - the geometric LOD study: simulation experiments with the runner and the evaluation metrics.
- **For a person in Rhino 8:** the toolbar and the 17 DOE icons as drawn, the viewport previews of the DOE generators, the canvas of *Program JSON* with its two new inputs, installing from the release files.

### D-176 — The owner approves PR #1: the DOE geometry decisions D-160 to D-171 accepted

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (merged PR #1 of the private repository on GitHub as `15f2e58`, then "PR approved" and "Record and push") · **Status:** Accepted
- **What.** The pull request of `feature/doe-geom` into `main`, whose test plan left one item open, the owner's reading of the provisional DOE decisions, is approved and merged; D-175 already records the merge and its release in `v1.5.0`. The approval is that reading: D-160 to D-171 change from Provisional to Accepted, with every choice the controller and the coordinating session made in them as written, and so do the statuses of [ADR-025](ADR-025-doe-reference-geometry-generators.md) (S1 to S10), [ADR-026](ADR-026-multiplied-rooms.md) (S8 and P5a's choices), the [design note](../plans/2026-10-25-doe-geometry-generators.md), and the nine DOE architecture pages.
- **Unchanged:** the illustrative example loads of the *DOE … Programs* presets (D-171) stay illustrative; the owner's decisions O1 to O8 stay as the design note gives them. A later decision that overrules one of these choices supersedes it in a new entry.
- **Not changed by this entry:** code, tests, and the `v1.5.0` tag, which stays at `866da55`.

### D-177 — Sourced reference programs and explicit research comparison boundaries

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang ("Yes proceed I approve", following the proposed sourced-program, separated-energy and conditioning-preflight stage) · **Status:** Accepted; first-stage backend implemented on the feature branch, not merged or released
- **What.** Add the first source-provenance reference packet, a representability matrix and opt-in floor research/reporting APIs under [ADR-028](ADR-028-reference-programs-and-research-contract.md) and the [stage plan](../plans/2026-10-28-reference-program-contract.md). DOE 1.4_7.2 is the baseline and 1.3_5.0 remains selectable; office height variations must be explicit variants. Keep example defaults, production validation, simplifier behavior and existing sensible metric definitions unchanged.
- **First-stage packet.** The implementation starts with the actual new-2004 MidriseApartment Chicago/5A source to avoid inventing a detailed-office room/program allocation. Source hashes, use-specific schedules/loads, enabled controls, climate, expansion calendar and unsupported source features are explicit. This is not JFK weather selection or a claim of complete DOE building equivalence.
- **Research boundary.** Fixed-control experiments must check spatial conditioning/control identity and actual source assignment, not conditioned-area totals alone. Preserve separate production validation and unverified geometry/native/whole-building contracts. Report sensible, latent and total thermal loads, observed purchased energy, fixed-COP electricity and monetary cost separately; missing data remain unavailable. Default fixed-COP comparison is 3/3, not an equipment simulation.
- **Limits.** No DOE geometry-branch merge, duplicate generator, annual/batch simulation, push, PR, release or deployment is authorized by this stage. Shared-service/design-day limitations, detailed-office crosswalk and branch-wide glazing/Core dependencies stay explicit. Original-source versus departure-adjusted geometry remains separate; no historical glazing mismatch is hidden by widening tolerance.
- **Numbering.** D-160 to D-171 and ADR-025/026 are already used by the separately fetched DOE geometry branch, so this independent stage reserved D-172 and ADR-027 without adopting that branch. At the merge into `main` (D-184), after `main`'s D-172 to D-176 and ADR-027, these entries became D-177 to D-183 and ADR-028 to ADR-031; commit subjects on the branch keep the numbers of their time.
- **Verification.** Release build: zero warnings/errors. Combined verification: 7,885 passed, 18 explicit real-engine/weather skips, zero failed. Eight new caller tests cover source programs through existing generation/IDF services, independent departure acknowledgements, writer-gate enforcement and full-year dated IDF schedule reconstruction for every represented source zone in both releases. Independent original-archive evaluation checked 54 zones, 150 loads and 227,760 schedule-hour values, with an altered-hour negative control rejected. A bounded independent Sol implementation review found no important or critical issues. No new annual simulation or measured energy accuracy follows from these checks.
- **Calendar correction.** Independent source inspection found ten explicit holidays and explicit daylight saving despite the weather-file flags being No. The implementation preserves the holidays and requires a separate acknowledgement of unsupported daylight-saving alignment; raw evidence coverage declares its subset. Shared elevator equipment remains explicitly unsupported.
- **Native/manual and docs.** The native Program JSON smoke launch encountered a Grasshopper duplicate-file conflict before scenarios. Native pass and manual viewport checks remain unestablished pending resolution; this is recorded separately from passing backend checks. Source usage, architecture links, ADR and roadmap updated; developer links checked. Public docs export/import and release follow only at the next approved tag.

### D-178 — Opt-in source-program Grasshopper adapters and bounded native isolation

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (authorized overnight continuation, source-program/research API usability and an isolated retry) · **Status:** Accepted implementation on `feature/reference-gh-stage2`, not merged or released
- **What.** Add *DOE Reference Program* as a thin adapter over the existing authenticated source catalog, with catalog-only discovery defaults, explicit original zone/WWR selection and independent geometry/DST acknowledgements. Append *Require Floor Research Eligibility* to *Convert2IDF*, index 11, default false. Existing GUIDs, input indices, illustrative defaults, production validation and source scientific behavior are preserved. See [ADR-029](ADR-029-reference-program-grasshopper-adapters.md) and the [continuation plan](../plans/2026-10-28-reference-grasshopper-continuation.md).
- **Reporting boundary.** Comparison reporting stays backend-only because the existing graph has no parsed simulation-result reader/parameter path; this stage does not add a runner workflow. Source calendar, local-clock/DST, subset, multipliers and shared-service/design-day omissions remain visible.
- **Verification.** New selector tests witnessed 18 failures/4 passes before implementation, then 22 passes; complete ProgramJson suite 199 passes. Combined Release verification: 7,907 passed, 18 explicit installed-engine/weather skips, zero failed, zero build warnings/errors. A bounded independent Sol code review found no important/critical findings. Actual direct component instances and GH_Document solutions from the verified task build passed 62 native checks, including a baseline-version source-picker Office/corridor pair through existing generation and gated IDF, full-year gain/control/activity schedule reconstruction and floor-gate enforcement. This is narrower than normal startup registration or archive restoration.
- **Native diagnosis.** The laptop's discovery list contains installed BEMGen 1.1.0 and task build 1.4.0 with the same GHA filename and different hashes. Public API inspection showed the documented list-loading overload is not publicly available; it was not invoked through private reflection. Renaming only a task-owned GHA removed the filename dialog but still loaded 1.1.0, leading to missing Program JSON. This was retained as a failed isolation attempt. No installed plugin, persistent search path, global choice or security setting was changed; original Rhino/user documents were preserved. Normal discovery, viewport checks and current/synthesized previous-shape archive reopen remain open.
- **Geometry checkpoint.** Saved source-linked plans/data distinguish original DOE thermal-zone footprints from existing generated room layouts and new parameterized snapshots. Existing office/courtyard services are reused for probes; no DOE geometry branch merge or duplicate generator is adopted. Topology, reciprocal contacts, internal-window exclusion/exposure, orientation, source program/control allocation and vertical boundary/multiplier semantics require separate executable contracts. A floor control/mapping pass is not a spatial-gain or whole-building certificate.
- **Close-out boundary.** Version stays 1.4.0. Source docs and smoke inventory follow the adapter change; public export/import/release need a subsequent approved tag. No new annual/production-batch simulation, push, merge, publication or trust change is authorized by this decision.

### D-179 — Spatial program research signatures and explicit air/boundary ledgers

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (authorized overnight continuation and the accepted bounded planning ladder) · **Status:** Accepted on `feature/research-contract-stage3`, not merged or released
- **What.** Strengthen only the existing opt-in floor research gate with per-source normalized program signatures and configured hourly heat partitions. Compatible homogeneous splitting/merging remains possible; heterogeneous spatial redistribution fails with explicit source/target reasons. Production validation, aggregation, presets and central tolerances remain unchanged. See [ADR-030](ADR-030-spatial-program-signatures-and-volume-ledgers.md), [usage](../research/reference-program-contract.md) and the [approved plan](../plans/2026-10-28-spatial-program-research-contract.md).
- **Ledger boundary.** Add explicit caller-provenanced source/derived air and boundary ledgers with role quantities that distinguish absent, unavailable and known zero, explicit mappings/departures and raw nullable volume differences. The API and conceptual fixtures are implemented; populated authenticated DOE-versus-derived ledgers are not established by those fixtures.
- **Verification.** Combined Release build and software verification: 7,961 passed, 18 explicit engine/weather skips, zero failed, zero build warnings/errors. Four real writer caller tests were observed failing before integration and passing afterward. Native results and final fixture verdicts remain in the external verification record, including retained unsuccessful attempts.
- **Limits.** Automatic people thermal partition, water/HVAC response, exact contact/window/orientation/construction identity and vertical equivalence remain unverified. No annual simulation, measured energy accuracy, merge, push, publication or installation change is implied. The software review found no important or critical source/test findings before this documentation entry; actual aggregate/native results remain in the external verification record.

### D-180 — One authenticated MediumOffice evidence-ledger caller

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (authorized bounded overnight source/derived ledger continuation) · **Status:** Implemented on `feature/mediumoffice-ledger-stage4`, not merged or released
- **What.** Authenticate the actual DOE 1.4_7.2 new2004 Chicago/5A archive, nested archive and IDF, and exact stored layout bytes at DOE branch `a527da5d0ffeb6de0d1c549dff2ab2568dde8738`. Add a data-only extracted fixture and integration caller over existing Core ledger APIs; no production Core or generator changes. See [plan](../plans/2026-10-28-authenticated-mediumoffice-ledger.md) and caller usage (`scripts/research-ledgers/README.md`).
- **Evidence and limits.** Fifteen source occupied-role regions are supported by explicit People/thermostat references and three plenums by explicit ReturnPlenum references. Source geometric prism measurements are distinct from blank engine Volume fields. Sixty-five hybrid rooms retain measured cell enclosures separately from null physical occupied volumes and unavailable conditioning/boundary sets. Role placeholders and mapping gaps are explicit; no names/program-key classification or thermal allocation is inferred. Source and stored multipliers are retained without silent expansion. Basement-role absence is not measured zero. G1 is a declared representation convention, not a verified spatial crosswalk or 44.44% energy result. The internal source Building label's v1.3_5.0 text remains beside the authenticated v1.4_7.2 member identity; the original OSM bytes are not independently authenticated here.
- **Verification.** Seven initial extractor tests observed seven failures before implementation, then seven passes; final checks add nested/member byte-mutation tests for nine passes. Three integration tests exercise actual Core creation/comparison and retain unknowns, source couplings, mapping gaps and declared absorption. Bounded independent source review found no important or critical findings before this documentation entry. Corrected software-only Release verification: 7,964 passed, 18 explicit engine/weather skips, zero failed and zero build warnings/errors. Captured process exits and full logs are in the external verification record. The first aggregate mistakenly inherited `BEMGEN_ENERGYPLUS`, enabling existing annual engine tests outside authorized scope; the verified task testhost and active children were stopped and all outputs/logs retained. The separate software-only retry explicitly cleared opt-ins. Those unintended runs establish no adopted scientific result. No push, merge, publication or installed-setting change.

### D-181 — Fail-closed software-only verification after the inherited engine opt-in incident

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (authorized process-local guard, fake-only regressions, generated data handoff and contract proposal) · **Status:** Implemented guard on `feature/software-only-verification-guard`; default real runner unexecuted
- **What.** Add the software-only launcher (`scripts/software-only/README.md`) under the [bounded plan](../plans/2026-10-28-software-only-verification-guard.md). Clear process-local activation/filter/settings names and verify absence; accept only SoftwareOnly, exclude all 18 reviewed engine/installed-weather annotated methods, reject source/build/script fingerprint drift, and propagate integer failures/exceptions. No arbitrary filters or runner/settings arguments in the CLI, persistent environment edits, user-process actions or automatic policy refresh.
- **Evidence.** Actual source activation variables are `BEMGEN_ENERGYPLUS` and `BEMGEN_WEATHER_3B`; facts/theories and installed-weather reads explain the prior unfiltered gate. Incident evidence preserves only the first variable's inherited name, not its value or origin. End files do not establish successful annual completion. Keep all original logs, aborted outcomes and outputs; no energy results are adopted.
- **Verification boundary.** Eleven harmless fake-runner checks pass; semantic RED, intermediate suffix failure and checkout-newline RED/GREEN are retained. No real build, .NET test assembly, engine or native UI is executed to test this guard. Independent static review found no important/critical issues in the trusted-checkout scope; it did not execute runners or independently reproduce the digest/results. This is an operational guard for the reviewed checkout, not a security sandbox or a fresh scientific/native verification.
- **Separate artifacts.** The exact-composition contract remains a proposal for coordinator review, with required invariants, negative fixtures and missing-evidence defaults; no new composer/preflight is implemented. The compact MediumOffice handoff contains generated geometry/ledger data only, not repository source or original models. No push, merge, publication or new production phase.

### D-182 — Bounded opt-in exact-composition identity screening

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (existing overnight research authorization; coordinator approved the bounded proposal) · **Status:** Accepted implementation on `feature/exact-composition-preflight`, not merged or released
- **What.** Add a default-off Core preflight over actual registered source/target floors under [ADR-031](ADR-031-exact-composition-identity-preflight.md) and the [plan](../plans/2026-10-28-exact-composition-preflight.md). Inspect complete identity mapping, geometry/contact/exposure/window/orientation and spatial program preservation separately; each check is Preserved, Failed or Unavailable. No new composer, placement-registration engine or production validation change.
- **Evidence boundary.** Caller ownership declarations establish only declared claim identity and retain evidence; unknown physical court/bay/stair ownership is never inferred. Full construction assignments are unavailable in these surface records. Supported geometry/program preservation does not become full exact-composition eligibility while required evidence is unavailable. Native and vertical/thermal accuracy claims remain outside scope.
- **Guarded execution.** Before implementation, inspect the narrow ledger caller, Integration initialization and dependencies, build properties and activation paths. Run exactly those three data-only tests through a reviewed narrow adapter with activations absent, positive selector AND all 18 mandatory exclusions and a matching source fingerprint: three passed, zero skipped, zero build warnings/errors. The default full-solution runner remains unexecuted. Source changes require an explicitly inspected policy refresh before any subsequent test run.
- **Test-first.** Six actual canonical courtyard generator identities at 0/37 degrees and independent mutations observed 23 assertion failures against a compiling unavailable-report scaffold before implementation. The first attempt's PowerShell native-stderr interruption is retained separately from the complete RED result. Final affected test/review outcomes remain in the external verification record.
- **Verified checkpoint.** The original 23 cases passed after implementation. An additional independent production-baseline status case observed RED, then the final 24 passed. Guarded affected software verification: Core 853, Generators 518, Integration 2,801; 4,172 passed, zero skipped/failed. A final test-only oracle confirms production conservation still passes during the spatial program swap and passed in the guarded 24-case rerun. Production source was unchanged after the affected run. One bounded independent static review found no important/critical findings before that last test-only assertion/final outcome wording. No fresh full-solution/native/energy verification is claimed.
- **Limits.** No engine execution, annual/production batch simulation, installed-setting change, user-process termination, push, merge or publication is authorized by this increment. Earlier incident artifacts remain preserved and are not adopted as scientific evidence.

### D-183 — Combine current main, research checkpoints and the complete DOE geometry branch

- **Date:** 2026-10-28 · **Decided by:** Jimmy Wang (new branch and push; explicitly approved including the complete older DOE branch) · **Status:** Accepted scope; integrated and software-verified on the separate branch, no main update or release
- **Inputs:** current remote main `98aa569cdb16a797a336a62bf12f0cd9e3b57233`, research chain through `fd9ac3b9c054b0c8d02bf1c47674853ff5f2a253`, and DOE geometry `a527da5d0ffeb6de0d1c549dff2ab2568dde8738`. Main is already an ancestor of both tips. Preserve the research checkpoints once and retain both histories on a new integration branch; no main update or PR is authorized. The separate 5R1C branch is outside these selected inputs.
- **Integration compatibility:** the DOE branch adds explicit roof skylights. The exact screen must compare their outlines and list order on registered ceiling hosts; aggregate glazing conservation cannot establish placement identity. Use existing central tolerances and leave production behavior unchanged. A positive baseline and five independent negative cases pin this boundary before the fix.
- **Limits:** configured thermal-program preservation does not authenticate source program-key classifications; no ownership/construction evidence is invented. Existing multiplier and SelfAdjacent scope limits remain. No annual/batch/production simulation, native launch, persistent setting change, force-push, tag or release is authorized by this integration.
- **Verification:** inspect the merged activation/build routes and explicitly refresh the guarded source inventory, run reviewed narrow software suites with fixed exclusions, independently review the final combined tree, then verify remote main ancestry and branch SHA before and after pushing only the new branch. Exact outcomes are recorded at close-out; prior branch-native and energy results are not new integration results.
- **Plan:** [2026-10-28-main-research-doe-integration.md](../plans/2026-10-28-main-research-doe-integration.md).

- **Observed close-out:** 11,092 selected software tests passed, zero failed, one pre-existing atlas A2 placeholder skipped; 11 guard regressions passed. Full solution build: zero warnings/errors. Independent source review accepted the 684-file executable/build fingerprint; no blocking findings. The default full-solution test runner and native/energy checks were not exercised. Exact branch publication and remote SHA confirmation are retained in the external integration record.

### D-184 — The research integration branch merged into `main`: D-177 to D-183 and ADR-028 to ADR-031 renumbered after `main`

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (approved the merge on 2026-10-29); the controller (the conflict resolutions and the renumbering) · **Status:** Accepted; merged through a pull request, not released
- **What.** `integration/main-bemgen-research-20261028` (`1ddaf10`, Jimmy Wang's 18 commits of 2026-10-28) merged into `main` at `0b687e7` (D-176) as `3b03a71`: the DOE reference catalog and packets, the floor research gate, spatial program signatures, the volume ledgers, the medium-office ledger fixture, the exact-composition screen, the comparison energy report, the raw zone thermal reader, and the software-only launcher (D-177 to D-183). The branch's base `a527da5` is the DOE geometry tip that `main` already holds through PR #1.
- **Numbering.** The branch wrote its entries as D-172 to D-178 and its ADRs as ADR-027 to ADR-030, the numbers `main` had meanwhile given to the atlas release 2.0.0 contracts, the daylighting removal, version 1.5.0, and PR #1's approval (D-172 to D-176, ADR-027). Following D-160's convention, they follow `main`'s sequence: D-172 to D-178 become D-177 to D-183, ADR-027 to ADR-030 become ADR-028 to ADR-031 (files renamed), and every cross-reference in the files the branch added or changed follows, `main`'s own references unchanged. Commit subjects on the branch keep the numbers of their time.
- **Conflicts.** This log keeps `main`'s entries first; `Lod.ProgramJson.csproj` embeds the reference packets beside `main`'s program JSON 5.4.0 schema; [program-json.md](../architecture/program-json.md) keeps `main`'s 5.4.0 status line with the branch's catalog note, its "not atlas Program JSON 2.0.0" now 5.4.0. `main` wins on the contracts (program JSON 5.4.0, constructions 4.3.0 and 3.1.0, mass contract 1.1.0), the daylighting writer's removal (D-174: the branch writes no daylighting; its DOE packet handles only daylight-saving time), and version 1.5.0: [AGENTS.md](../AGENTS.md)'s two branch paragraphs saying "version remains 1.4.0", which git placed in *Stage workflow* and *Commands*, become one *Project state* bullet.
- **Merge-induced fix.** `main`'s water mains inlet (D-172) made `WaterTemperatures.Inlet` nullable, so `ResearchProgramSignature` no longer built (CS8604). A weather-file inlet is now the same input only as another weather-file inlet; a schedule against the water mains is a difference. Two tests (`AWeatherFileWaterInletIsNotTheSameInputAsAScheduledInlet`, `WeatherFileWaterInletsOnBothSidesAreTheSameInput`) failed with a null reference before the fix and pass after it.
- **Checks:** `scripts/verify.ps1` on the merge, without `BEMGEN_ENERGYPLUS` or `BEMGEN_WEATHER_3B`: VERIFY PASSED, 0 warnings: Core 1038, Generators 3051 (1 skipped), Integration 3629, Export 3116 (1 skipped), ConstructionJson 311, ProgramJson 239, Simulation 265 (14 skipped), IdfBatchRunner 103 (3 skipped), TestSuiteGenerator 119; 11,871 passed, 19 skipped, none failed. `python scripts/docs-export/developer_pages.py --check`: 106 pages checked.
- **Open:** the software-only launcher's reviewed source digest (`scripts/software-only/policy.json`, 684 files) does not cover `main`'s code, so `scripts/verify-software-only.ps1` refuses the merged tree until a person inspects the activation routes and refreshes the policy (the merged tree still has the 18 engine-annotated tests it excludes); no Rhino smoke (`reference-programs` and the others), viewport, toolbar, or example `.gh` check was run for the merge; no EnergyPlus run.

### D-185 — Tooling of the geometric LOD study: DOE prototype suites, pinned inputs and weather, a stage driver, and the deduplicating report

- **Date:** 2026-10-29 · **Decided by:** the owner (the study, its deterministic prototype schedules, and the §3 work of the [run plan](../plans/2026-10-29-lod-study-run-plan.md)); the controller (the design of [ADR-032](ADR-032-doe-prototype-suites-and-study-inputs.md)) · **Status:** Provisional; built on `claude/lod-study-scripts`, not merged or released
- **What.** The test-suite generator imports every program for its test case's climate zone and an optional `program_context`, takes `window_to_wall_ratio: program` (the JSON's `fenestration`), checks a registry file's `sha256`, reads relative inputs from `--inputs-root`, and records or requires the floor research gate (`settings.floor_research_gate`: `off`, `report`, `require`). A `doe` building block runs the 15 DOE types through the 11 DOE generators at their records' dimensions, with an atlas program (or a floor-area mix) per program key and the record's glazing per key by default (`scripts/TestSuiteGenerator/README.md`). `scripts/lod-study/` adds the weather pins (`pin_weather.py`, six EnergyPlus TMY3 files, `research/lod-study/weather.lock.json`), the atlas input export with its manifest (`export_inputs.py`, 366 files for 22 prototype-vintages from atlas `v2.0.0`, `96a2e928`), the generated stage specs (`make_specs.py`, `research/lod-study/specs/{smoke,pilot,main,ht,timing}.yaml`), the driver `run.ps1` (generate, run, merge, report, `-Resume`), and `report.py` (deduplication by zone-geometry signature and annual sensible totals, and the §10 tables beside the conditioned-area change), documented in `scripts/lod-study/README.md`.
- **Why.** Plan §3: climate-dependent program values fell back with `ProgramJsonClimateZoneNotGiven`; the DOE generators were not in the suite registry; no weather was pinned; no spec or driver existed.
- **Checks.** `scripts/verify.ps1` passed with 0 warnings before each commit; TestSuiteGenerator tests 119 → 150. `python -P -m unittest discover -s scripts/lod-study/tests`: 7 passed. `make_specs.py --check` passed; all five specs plan. R1 smoke ran (plan §4).
- **Not done.** No Rhino step is involved. The DOE suite tests that use the record's storeys and glazing were written before the code but first failed by not compiling; the report's unit tests were written after it.

### D-186 — LOD study choices the build changed or found, for the owner

- **Date:** 2026-10-29 · **Decided by:** the controller (proposals; the owner decides) · **Status:** Provisional
- **Vintages:** 90.1-2007 and 90.1-2019, since atlas 2.0.0 has no 90.1-2004 (the plan proposed 90.1-2004).
- **Zonings:** 24 main zonings (PerimeterCore at 3.0 m and 4.57 m with every stacker) in place of the plan's 18, since a spec's zonings are a full factorial.
- **Floor gate:** `report`, not `require`: `require` blocks every zoning that merges zones of different programs, 16 of the medium office's 24 in R1.
- **Program keys:** 90.1-2019 stand-alone retail `Retail` is the atlas's Front_Retail and Core_Retail mixed by represented area (150.81 and 1600.48 m²); small-hotel `GuestRoom` is `GuestRooms_Mixed`; 90.1-2019 hospital `Office` is `Office_Mixed`; the 90.1-2007 small hotel takes the set `dca6c5` of the atlas's two sets with the same metadata.
- **Glazing:** the DOE record's per key (`record`), since the atlas 90.1 programs have no `fenestration`. **Zone 7:** registered as `7A`, the atlas's label.
- **R1 finding (blocking R3 in three climates).** EnergyPlus warns once a year `Temperature out of range [-100. to 200.] (PsyPsatFnTemp)` from `PsyTwbFnTdbWPb` in the medium office reference with the 2B Tucson, 4A New York, and 7A International Falls files, and with Sterling exactly as in mock-1, at ordinary weather records; 2A, 3C, and 5A run clean. It is not a defect of the Sterling file. The single-zone stackers over many-zone floors warn `FixViewFactors` (and, for *Single Zone Building*, the floor-area warning). The runner fails these sites' verdict; accepting the warnings would change its expected-warning list, a validation decision left to the owner. Nothing was relaxed.

### D-187 — Causes of the R1 EnergyPlus warnings and a proposed runner policy, for the owner

- **Date:** 2026-10-29 · **Decided by:** the owner ("find the cause first"); the controller (the diagnosis and the proposal) · **Status:** Accepted by the owner's decision of 2026-10-29 (D-189); implemented; the `FixViewFactors` part superseded by D-191 (the IDF writer merges coplanar pieces, the alternative named below)
- **`PsyPsatFnTemp` (2B, 4A, 7A references, once a year).** EnergyPlus's outdoor wet-bulb iteration (`PsyTwbFnTdbWPb`, the site's `Site Outdoor Air Wetbulb Temperature`) at a time step whose outdoor wet-bulb is just below 0 °C. On the New York reference it stays at the same time step and input (03/12 11:50, −170.82 °C) with dehumidification control off, a lower minimum supply humidity ratio, no infiltration, no people, no tables, and no HVAC at all; the timestep moves it. The converged value is right (−0.4185 °C against an independent −0.4182 °C). Changing that record's humidity from 27 % to 28 % removes it and changes the summed ideal sensible loads by at most 1.1 × 10⁻⁴ kWh in an hour; no object of BEMGen's IDFs uses the outdoor wet-bulb. Not a BEMGen defect; no metric changes. Evidence: [run plan §8](../plans/2026-10-29-lod-study-run-plan.md#8-the-causes-of-the-r1-warnings-d-187).
- **`FixViewFactors` (single-zone stackers over *No Simplification* and *Semantic Merge*).** A merged zone keeps every room's floor and ceiling pieces (51 surfaces against 6 for the same floor simplified by *Single Zone Per Floor*) and an internal mass 2.4 times its surface area; EnergyPlus's approximate view factors then miss completeness by 0.005. Without the mass the warning goes; the geometry is closed and its areas equal the simplified zone's. Not a geometry defect. The fragmented zone's annual sensible cooling differs from the simplified zone's by about −0.45 % and heating by +1 to +2 % of 280 kWh, so they are two models. Correction to D-186: the floor-area warning of *Single Zone Building* is already expected (ADR-010); only `FixViewFactors` failed those sites.
- **Proposed runner policy (owner to decide).** Add two expected-warning entries to `ExpectedWarnings`, each matched on its text and its context line, with a count limit, and keep failing on any severe or fatal error and any other warning: (1) `OutdoorWetBulbIteration`: `Temperature out of range [-100. to 200.] (PsyPsatFnTemp)` with the routine `PsyTwbFnTdbWPb`, at most 3 per run, none during sizing; (2) `MergedZoneViewFactors`: `FixViewFactors: View factors not complete` with an enforced reciprocity tolerance of at most 0.01, at most one per zone. The alternative for (2) is a BEMGen change: stackers that coalesce coplanar floor and ceiling pieces of a merged zone, which changes those sites' results by about 0.5 % and needs its own decision. Until then the 2B, 4A, and 7A test cases and those four zonings fail the verdict.

### D-188 — Machine-readable LOD recommendations for the atlas site

- **Date:** 2026-10-29 · **Decided by:** the owner (the recommendations are published on the atlas website); the controller (the format and the default threshold) · **Status:** Provisional; the threshold is the owner's choice
- `scripts/lod-study/report.py` also writes `lod-recommendations.json` (schema `scripts/lod-study/schemas/lod-recommendations-v1.schema.json`): per test case, keyed by prototype, climate zone, vintage, and orientation and indexed by atlas program ID, the reference's benchmark values, every zoning's §10 metrics and conditioned-area change as the runner stored them, and the coarsest zonings (fewest modelled zones) meeting the threshold ([run plan §9](../plans/2026-10-29-lod-study-run-plan.md#9-publication-on-the-atlas-site)).
- **Default threshold (owner choice):** for sensible heating and cooling, |annual error| ≤ 10 %, CV(RMSE) ≤ 30 %, |NMBE| ≤ 10 % (ASHRAE Guideline 14, hourly), |conditioned-area change| ≤ 1 %; a load under 1 kWh/m² a year is not judged. `--threshold` replaces it and the file records it. The site integration is later atlas work.
- **Fix in the same slice:** the report's zone-geometry signature read the vertex count as the first coordinate (field offset); signatures now hold the vertices themselves, with a test. The R1 duplicate groups are unchanged.

### D-189 — The owner approves D-187: the two limited expected warnings, implemented; R2 next

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li ("Approve D-187: add the PsyPsatFnTemp (≤3/run, none in sizing) and FixViewFactors (≤0.01, ≤1/zone) expected-warning entries. Merge BEMGen PR #4 when verify passes, then run the R2 pilot.") · **Status:** Accepted; implemented on `claude/lod-study-scripts`; `MergedZoneViewFactors` superseded by D-191 (removed)
- **What.** `ExpectedWarnings.Default` gains `OutdoorWetBulbIteration` (`PsyPsatFnTemp` with the context line `Routine=PsyTwbFnTdbWPb`, at most 3 a run by the recurring summary's total, none during sizing) and `MergedZoneViewFactors` (`FixViewFactors … zone="…"` with an enforced reciprocity tolerance at most `ToleranceSettings.ViewFactorReciprocity`, 0.01, at most one per zone). A warning that misses its context line or its bound stays unexpected; a run over a limit fails; severe and fatal errors and every other warning still fail. The counts go into `site_status.message` (`expected warnings: OutdoorWetBulbIteration 1`), so the central schema stays at version 7.
- **Proof.** The R1 smoke suite run again: 24 of 24 sites succeed (the four `FixViewFactors` sites with `MergedZoneViewFactors 3` or `1`), and the 20 sites that succeeded before have identical sensible heating, sensible cooling, total load, and CV(RMSE). The 4A diagnosis suite (New York JFK and Sterling, 48 sites): 48 of 48 succeed, both references with `OutdoorWetBulbIteration 1`.
- **Tests.** `LimitedWarningTests` (11, Lod.Simulation) and `LimitedWarningRunTests` (2, IdfBatchRunner), written first and failing (not compiling, then on the missing status count).

### D-190 — R2 pilot run: two Convert2IDF fixes, the triage, and the small-hotel warning for the owner

- **Date:** 2026-10-29 · **Decided by:** the owner (run R2, D-189); the controller (the fixes and the triage) · **Status:** Accepted fixes; the small-hotel warning is Provisional, for the owner; closed by D-191 and D-192 (the writer merges coplanar pieces, R2 run again)
- **Fixes, test-first.** (1) *Convert2IDF* refused the hospital's reference: `L1/OR1_Flr_2/F3` is two rectangles of one floor meeting at one vertex, which the union in `IdfPolygons.Rebuild` kept as one ring that touches itself; such a ring is now split at the vertex it repeats into its simple rings, their areas summing to the ring's within the central area tolerance (`DoeReferenceConversionTests`). (2) The restaurant, primary school, and small hotel references crashed EnergyPlus (`Zero or negative surface area`, exit code 0xC0000005) on wall-transfer or floor-distributed masses of about 10⁻⁷ m²: their sets budget exactly the capacity the record represents, so the shortfall was rounding. `ConstructionMassAccounting.Plan` takes the tolerances and treats a represented capacity equal to its budget within `ToleranceSettings.RelativeArea` as no shortfall and no overshoot (`ConstructionMassAccountingTests`). Export snapshots are unchanged.
- **Results.** 22 test cases; 528 sites planned, 440 written, 88 `Invalid` by the simplifiers' and stackers' documented limits (multiplied rooms in the large hotel and the hospital, ADR-026; the outpatient's narrow wings under *Perimeter Core*); 392 of 440 succeeded (89 %), all 372 succeeded test sites paired (largest deviation 2.9 × 10⁻¹⁰ W); 210 of 372 dropped as duplicates (110 groups); a zoning meets the default threshold in 16 of 20 cells. Per-prototype times and the recommended zonings are in [the run plan §4](../plans/2026-10-29-lod-study-run-plan.md#4-stages).
- **For the owner.** The R2 gate (≥ 99 % complete) is not met: both small-hotel references give one `FixViewFactors` warning on `L3/CORRIDORFLR4`, the unmerged 24-surface corridor of the top floor, which EnergyPlus prints without the enforced-reciprocity line even with `DisplayExtraWarnings`; D-189's entry needs that line to bound the tolerance, so the warning stays unexpected and the hotel's 46 test sites were not run. Deciding to accept it (for example a bare `FixViewFactors`, at most one per zone, in a reference as in a test site) or to look into the corridor's geometry is the owner's call; nothing was relaxed.

### D-191 — The IDF writer merges a zone's coplanar surfaces, supersedes D-189's view-factor entry

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li ("Fix in BEMGen": the IDF writer merges a zone's coplanar floor, ceiling, and roof pieces); the controller (the rule, [ADR-034](ADR-034-coplanar-surface-merge.md)) · **Status:** Accepted; the realisation Provisional, pending the owner's reading · **Supersedes** D-189 in part (the `MergedZoneViewFactors` entry)
- **What.** `IdfSurfaceMerge` merges, before the writer splits or pairs anything, a zone's floors, ceilings, and roofs of one kind, elevation, boundary, and adjacent zone that share an edge, pairwise while the union is one simple ring without holes of their summed area, interzone groups only together with their mirror across; and walls without windows in straight runs. Surfaces with windows or skylights, self-adjacent, with holes, or whose union would have an edge or a nearly straight vertex within EnergyPlus's 0.01 m stay apart. The header lists each merge, provenance records `MERGED:`, the info `SurfacesMerged` counts them. The convex split of outdoor surfaces (ADR-019) stays and now takes the cut leaving the fewest reflex vertices, then the shortest: the small hotel's T-shaped corridor roof is two pieces, not three.
- **Why.** EnergyPlus's approximate view factors treat a zone's coplanar surfaces as unable to see each other; with a large internal mass the many pieces of the single-zone stackers (D-187) and the small hotel's three-piece corridor roof (D-190) missed completeness. In the small hotel reference (Buffalo 5A, 90.1-2019, run in `D:\bgdiag\d190`), the two-piece roof removes the warning with no other warning (extra warnings on) and gives the same results as one polygon: annual sensible heating −1.18 % in `L3/CorridorFlr4`, −0.43 % for the building; cooling −0.97 % and +0.005 %.
- **Departure from the owner's words.** A merged roof that is not convex is still cut into convex pieces, since a non-convex casting surface is a severe EnergyPlus error (ADR-019); in the corridor the two convex pieces give the results of one polygon.
- **Runner.** `ExpectedWarnings.MergedZoneViewFactors` and `ToleranceSettings.ViewFactorReciprocity` are removed, with their tests; `OutdoorWetBulbIteration` stays. A `FixViewFactors` warning fails a run again.
- **Tests.** `IdfSurfaceMergeTests` (13) and the T case of `IdfConvexTests`, written first: the T failed on three pieces, the merge tests on a stub that merged nothing. `LimitedWarningTests`: the three view-factor tests replaced by one that a `FixViewFactors` warning fails a run (written first, failing while the entry existed) and one that keeps the bound and key rules on a test entry. Two IDF snapshots changed on purpose (their merged floors, ceilings, and roofs and the header's merge list). `scripts/verify.ps1` passed with 0 warnings before each commit; after the second: Lod.Core 1040, Lod.Generators 3051 (1 skipped), Lod.Integration 3629, Lod.Export 3132 (1 skipped), Lod.ProgramJson 239, Lod.ConstructionJson 311, Lod.Simulation 275 (14 skipped; 276 before the runner change), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 150.

### D-192 — R1 and R2 run again with the coplanar merge: R2's gate met, D-190's small-hotel question closed

- **Date:** 2026-10-29 · **Decided by:** the owner (D-190: "Fix in BEMGen"); the controller (the runs and the comparison) · **Status:** Accepted · Closes the open question of D-190
- **R1** (`run.ps1 -Stage smoke -Parallel 20`, run `run_20261029-050006`): 24 of 24 sites succeed, all paired; no `FixViewFactors`; 11 of 23 test sites dropped as duplicates (5 before), since the single-zone stackers over *No Simplification* now write the zone *Single Zone per Floor* writes.
- **R2** (`run.ps1 -Stage pilot -Parallel 20`, suite `lod-pilot-20261029-050143`, run `run_20261029-050215`): 440 of 440 written sites succeed (89 % before), the ≥ 99 % gate is met; 418 of 418 test sites paired (largest internal-load deviation 2.9 × 10⁻¹⁰ W); no `FixViewFactors` or other unexpected warning in any site's `eplusout.err`. 79 duplicate groups, 275 of 418 dropped; a zoning meets the default threshold in 18 of 22 cells (the 16 of D-190 and both small-hotel cells).
- **Against the previous R2** (`D:/bemgen-results/lod-study/pilot-before-d191`, the 392 sites both completed): written surfaces 39 420 → 33 128 (−16 %); references change by at most 0.14 kWh (heating) and 0.36 kWh (cooling) a year; where a load is at least 1 kWh/m² a year, annual sensible heating moves by at most 2.2 % and cooling by at most 1.2 %, the largest in *Perimeter Core* with a single-zone stacker. EnergyPlus times are not comparable (a shared machine); the run took 9 min 37 s. Details in [the run plan §4](../plans/2026-10-29-lod-study-run-plan.md#4-stages).

### D-193 — R3 main and R4 heat-transfer stages run; the small hotel's IWHT-off failures for the owner

- **Date:** 2026-10-29 · **Decided by:** the owner (run the study, D-185, D-191); the controller (the runs and the triage) · **Status:** Accepted for the runs; the R4 failures Provisional, for the owner
- **Build.** Both stages ran with BEMGen `2ed856c` (main after PR #6, before `v1.6.0`), atlas inputs of release 2.0.0 (`96a2e928`), EnergyPlus 26.2.0.
- **R3** (`run.ps1 -Stage main -Parallel 20`, suite `lod-main-20261029-051941`, run `run_20261029-052718`, 1 h 47 min): 264 test cases, 6 336 sites planned, 5 280 written, 1 056 `Invalid` by documented limits (multiplied rooms, ADR-026, 864; the outpatient's narrow wings, 192); **5 280 of 5 280 succeed**, 5 016 of 5 016 test sites paired (largest deviation 5.5 × 10⁻¹⁰ W); no `FixViewFactors`, the only warnings the expected floor-area (384 sites) and `OutdoorWetBulbIteration` (2 640 sites, within its limit). Deduplication: 925 groups, 3 323 of 5 016 dropped (66 %). A zoning meets the default threshold in **218 of 264 cells**: 24 of 24 for the hospital, large hotel, medium office, outpatient, small hotel, stand-alone retail, and strip mall, 20 for the primary school, 16 for the supermarket, 12 for the full-service restaurant, 2 for the warehouse. The coarsest zonings meeting it are most often *Conditioned Merge* + *Single Zone Building* (84 cells), *Semantic Merge* + *Stack* (57), and *Conditioned Merge* + *Stacked Floor Zone Multiplier* (40); the medium office's are *Perimeter Core* with *Stack* or *Stacked Floor Zone Multiplier*.
- **R4** (`run.ps1 -Stage ht -Parallel 20`, suite `lod-ht-20261029-071714`, run `run_20261029-071919`, 33 min): 22 test cases × 96 zonings, 2 112 planned, 1 760 written, 352 `Invalid` (same limits); **1 736 of 1 760 succeed (98.6 %)**, every reference among them, 1 714 of 1 714 test sites paired; no `FixViewFactors`. 213 duplicate groups, 1 433 of 1 714 dropped; 18 of 22 cells have a recommendation, the cells of R2.
- **R4 failures (24, for the owner).** All are the small hotel's (12 in 3C, 12 in 5A): the zonings that keep the unconditioned elevator core or mechanical room as its own zone (*No Simplification*, *Semantic Merge*, *Conditioned Merge* with *Stack* or *Stacked Floor Zone Multiplier*) with IWHT off. EnergyPlus stops in warm-up (`CalcHeatBalanceInsideSurf … very far out of bounds`): the core's program carries the source's elevator equipment, 2 133 W/m² (32 kW in 15 m²) with no lost fraction, and with adiabatic interior walls the zone sheds it only through one 1.8 m exterior wall and the ground. Not a BEMGen defect (the program and the option are written as given, GLOBAL.md scientific rule 3); nothing was changed. The owner decides whether IWHT-off settings exclude such zonings or the study treats such a zone differently.
- **Not run:** R5, the serial timing pass, which needs an idle machine. EnergyPlus times per prototype are in [the run plan §4](../plans/2026-10-29-lod-study-run-plan.md#4-stages) and are not runtime results (20 runs at a time on a machine shared with other work).

### D-194 — Schedule Draw: the atlas generator as an external command, drawn per zone, the requirement's open items settled (ADR-033)

- **Date:** 2026-10-29 · **Decided by:** the owner (the goal: the atlas's stochastic schedules as an optional add-on beside the deterministic ones, by calling the atlas generator as an external command; the requirement of D-133, D-134); the controller (the settled items, [ADR-033](ADR-033-schedule-draw-external-generator.md)) · **Status:** Provisional, pending the owner's reading
- **What.** `Lod.ProgramJson.ScheduleDraw` draws program JSON 5.4.0 instances with `atlas_schedules` 3.0.0 (request and bundle schema 3.0.0): one request per draw, one run of a configurable command (default `python -m atlas_schedules`, files in and out, timeout, captured standard error, no shell, no network on BEMGen's side), the bundle checked against the pins (a pre-release such as `3.0.0.dev0` accepted with `ScheduleDrawPreRelease`), and one program JSON per instance with the drawn roles as `annual` 2007 schedules and `metadata.schedule_draw` provenance. The program setting is release 2.0.0's `generator.json`; the generator setting is BEMGen's `schedule_draw_setting` 1.0.0.
- **Settled.** Drawn: occupancy, lighting, electric and gas equipment, hot water (flow and target), activity, heating and cooling setpoints, narrowed by the setting; ventilation is not a generator schedule. Where: an external command. Calendar: the generator's 2007, never remapped (a suite with schedules must use 2007). Seeds: the test case's seed is the master seed; each zone its own operating group keyed `<plan index>.<zone ID>`, its seed the generator's `atlas_conditional_seeded_v1` of the master seed and key, computed and recorded by BEMGen. Magnitudes: the program's value must equal the generator's amplitude, and amplitude × Σ values equals the bundle's annual total within `ToleranceSettings.RelativeLoad`.
- **Refused (open).** Apartment-unit recipes (ResStock end uses program JSON does not hold) and composition parents (another slot vocabulary), `ScheduleDrawKindNotSupported`.
- **Why.** The generator is validated against native answer keys (atlas ADR 0035); a C# port would need its own validation. Drawing merged zones would break the conservation of hourly scheduled loads (GLOBAL scientific rules 1 and 4).

### D-195 — Test suites: the optional `schedules:` section, each seed a test case, one draw per test case on the plan's zones

- **Date:** 2026-10-29 · **Decided by:** the owner (requirements 2 to 6 of D-134); the controller (the spec form and records, ADR-033 decision 7) · **Status:** Provisional, pending the owner's reading
- **What.** `schedules: {generator: atlas_schedules, setting, setting_sha256?, recipes: [generator.json, ...], seeds: [...]}`; absent, every suite is unchanged (IDs, tables, folder). Each seed (0 to 2^53 − 1) is a test case of every combination of the other axes, its ID holding the setting's and program settings' SHA-256 and the seed. Per test case, one generator run on the zones of its generated plans before any zoning; each zone takes its drawn program, and the simplifiers and stackers aggregate the drawn zone programs, so merged zones never get a draw. The command and its folder are machine settings: `--schedule-command` / `--schedule-folder`, else `BEMGEN_SCHEDULE_COMMAND` / `BEMGEN_ATLAS_GENERATOR`. Records: `draws/<test case ID>.request.json` and `.provenance.txt`, the `schedule_*` columns of `test_cases`, `schedule_seed` in the long table, and the table `schedule_draws` (each zone's key, plan, zone, program, operating group, seed policy, seed). A calendar year other than 2007 and a mixed slot are plan problems.
- **Why.** Requirement 3 (seeded sampling only here, the other axes full factorial), 4 (all sites of a test case share its drawn zones), 5 (per-zone seeds), 6 (one run per test case). A floor that stands for several storeys shares its plan's draws, since a multiplier stands for identical floors.

### D-196 — Schedule Draw built: the core service, the Grasshopper component, the suite section, and the real-draw proof

- **Date:** 2026-10-29 · **Decided by:** the controller (build of D-194, D-195) · **Status:** Accepted build; the Rhino check is open
- **What.** *Schedule Draw* (`SDraw`, panel *1 Program*, GUID `740cafea-7afe-47f4-8723-b24b6ec3c836`, icon `schedule_draw`), a thin adaptor with a *Run* toggle whose *Drawn JSON* goes into *Program JSON*; [architecture page](../architecture/schedule-draw.md), [design note](../plans/2026-10-29-schedule-draw.md), the requirement page marked designed and implemented. Fixtures: `tests/Lod.ProgramJson.Tests/Fixtures/draw/` (the DOE Ref 1980–2004 medium office's `generator.json` from atlas `1bc25767`, a setting, the request BEMGen writes for two instances and seed 42, and the bundle the generator answered with). The existing icons are unchanged byte for byte.
- **Real draw.** `python -m atlas_schedules` (Python 3.14, generator `3.0.0.dev0`, atlas `1bc25767`) on the recorded request, the DOE Ref 1980–2004 medium office as instances `0.KS` (200 m²) and `0.DI` (300 m²) with their hot-water services, seed 42: the command took 1.1 s, gave the bundle SHA-256 `90ff6a71…40e2` twice (byte-identical runs), and `RealDrawTests` (with `BEMGEN_ATLAS_GENERATOR=D:/aa-gen`) passed, the whole draw with its read-backs in 15.9 s, its bundle equal to the recorded one byte for byte. The two instances of one program draw different hours, as the shifted seeds intend: annual lighting 38,212 Wh/m² for `0.KS` against 69,772 Wh/m² for `0.DI`, equipment 67,037 against 55,566 Wh/m².
- **Checks.** `scripts/verify.ps1`: VERIFY PASSED, 0 warnings, 11,984 passed and 20 skipped of 12,004 (Lod.ProgramJson.Tests 239 → 292 with 53 schedule-draw tests, one of them the opt-in real draw, skipped; TestSuiteGenerator.Tests 150 → 163). After `main` with D-191 and D-192 was merged in: VERIFY PASSED, 0 warnings, 11,997 passed and 20 skipped of 12,017. The core service was drafted before its tests, not test-first; its tests change one input at a time (a lighting value, an annual total, a fraction, a version, a seed, an owner) and check each is refused with its code, and the first run caught two of the tests' own mistakes (a fraction mutation that the binding check caught first, a stand-in script's parameter binding); the suite tests were written first and failed by not compiling (`SuiteScheduleDraw`, `TestCase.ScheduleSeed`, `SuitePlan.Schedules` missing), and the sha256 pin case first failed on YAML reading an unquoted hash as a number (the test now quotes it, as the README says).
- **Not done.** The Rhino 8 check of the component ([checklist](../development/grasshopper-smoke-test.md#schedule-draw-checklist-stage-b2-d-196)); an example `.gh`; the software-only launcher's reviewed-source policy, which a person must refresh for the changed sources (and should list `BEMGEN_ATLAS_GENERATOR`); apartment units, composition parents, and mixed slots (ADR-033 *Consequences*).

### D-197 — Version 1.6.0: Schedule Draw with the released generator, atlas release 2.1.0, the reference programs, and the LOD study tooling with the coplanar merge

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (stage B3 of the public-release plan, with blanket authority to merge, push, tag, and publish the releases once verify and the gates are green); the controller (the preparation and the routine choices below) · **Status:** Accepted
- **Version.** 1.6.0, prepared on `release/v1.6.0` from `main` at `5883da6`, a minor version as D-125 and D-175 reason: D-064 waives backward compatibility, and no component or parameter GUID changed or moved since `v1.5.0` (every one of its 101 GUIDs is still in the same source file of `src/Lod.Grasshopper`; 2 are new: *Schedule Draw* `740cafea-7afe-47f4-8723-b24b6ec3c836` and *DOE Reference Program* `9f3c8f73-4d64-4c7c-a2a2-8eb071dc7c12`). It adds components and appends one input (*Convert2IDF*'s *Require Floor Research Eligibility*, index 11); nothing is removed from a component. The existing icons are byte-identical to `v1.5.0`'s.
- **What it merges since `v1.5.0`** (45 commits on `main`):
  - **Research contracts and reference programs** (D-177 to D-184, ADR-028 to ADR-031, PR #3): *DOE Reference Program* (the authenticated DOE new2004 MidriseApartment Chicago/5A programs of DOE 1.3_5.0 and 1.4_7.2), *Convert2IDF*'s opt-in floor research gate, spatial program signatures, volume ledgers, the exact-composition screen, the comparison energy report, and the software-only launcher.
  - **LOD study tooling** (D-185 to D-190, ADR-032, PR #4): DOE prototype suites with pinned atlas inputs and weather, the stage driver and the deduplicating report with `lod-recommendations.json`, the runner's limited expected warning `OutdoorWetBulbIteration`, and two *Convert2IDF* fixes (a self-touching floor ring split at its repeated vertex; a mass shortfall within `ToleranceSettings.RelativeArea` treated as none).
  - **Coplanar surface merge** (D-191, D-192, ADR-034, PR #6): the IDF writer merges a zone's coplanar floors, ceilings, and roofs and windowless wall runs; `MergedZoneViewFactors` removed.
  - **Schedule Draw** (D-194 to D-196, ADR-033, PR #5): the component, the core service, and the test-suite `schedules:` section.
- **Made in this preparation.**
  - Atlas release 2.1.0 and the generator 3.0.0 pinned (D-198): the embedded program JSON schema is release 2.1.0's copy, the recorded bundle recorded again with the released wheel.
  - The version in `Directory.Build.props`; the smoke spec `schedule-draw` (registration, *Run* false, two error scenarios, and, with `BEMGEN_SCHEDULE_COMMAND`, the real draw through *Program JSON* to *Validate* and *Convert2IDF*, repeatability, another seed); the example `schedule-draw.gh` (routine choice: a *Stream Filter* gated by the *Run* toggle passes the program's own JSON while *Run* is false, so the saved definition solves without a generator and the examples check stays one *Validate*, True); the 21 example definitions rebuilt with the 1.6.0 plugin (`BEMGEN_EXAMPLES_WRITE=1`).
  - `reference-programs.py` (D-178), never run on this harness before (D-184), stopped with `ImportError: No module named Lod.Core.Common`: IronPython had no reference to the loaded `Lod.Core` assembly. The spec now adds it from the loaded assemblies (as `doe-presets.py` does); no check changed, and it then passed its 72 checks.
  - The release-1.6.0 checklist for a person in Rhino, appended to [grasshopper-smoke-test.md](../development/grasshopper-smoke-test.md#release-160-checklist-stage-b3-d-197).
- **Checks on the release candidate:**
  - **Examples.** All 21 rebuilt with the 1.6.0 plugin; each reopened and solved with one *Validate* True and no error; one warning, *Program JSON*'s `ProgramJsonNotInstantiated` of the DOE Ref medium office's two hot-water zone gain records in `schedule-draw.gh` (the same with *Run* false or true). With `BEMGEN_SCHEDULE_COMMAND` set to `D:\bemgen-venv-schedules\Scripts\atlas-schedules.exe`, `schedule-draw.gh` with *Run* true solved with no error, *Validate* True, and the drawn lighting schedule in the IDF.
  - **Definitions saved with 1.5.0.** The 20 example files as committed before the rebuild (saved with the 1.5.0 plugin) reopened with the 1.6.0 plugin (`1.6.0+5673d81`): every archive read without a warning or error, and all 20 solved with one *Validate* True and no runtime warning or error (60 checks passed).
  - **Rhino smoke.** All 27 specs of `scripts/rhino-smoke` in Rhino 8.25.25314.11001 on the final plugin code (`f5f70a0`), with `BEMGEN_SCHEDULE_COMMAND` set: 1519 *Validate* True and none False, 1002 spec checks passed and none failed, no missing component or missing expected error, no exception; runtime errors only in the error scenarios and, in the DOE specs, on the component placed without a program map, as in their stage runs. `reference-programs` failed in the full run on the import above and passed when run again alone after the fix (its counts are those of the second run). The `schedule-draw` spec drew with generator 3.0.0 and no `ScheduleDrawPreRelease`; nothing was `SKIPPED`. Timings are not meaningful: an EnergyPlus batch of another agent (about 14 to 17 processes) ran throughout.
  - **`scripts/verify.ps1`** on the candidate's tree: VERIFY PASSED, 0 warnings: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 299 (1 skipped), Simulation 275 (14 opt-in skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163. One earlier run on the second commit's tree failed `AGeneratorThatRunsTooLongIsStopped` (the 2 s timeout stopped the stand-in command only after 1 min 47 s on the loaded machine, against its 50 s bound); the run again passed. The test was not changed; it is load-sensitive.
  - **Fresh-clone gate.** A clean clone of `release/v1.6.0` at `be90af9` (`D:\BEMGen-gate\v1.6.0`) passed `scripts/verify.ps1` with 0 warnings: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 299 (1 skipped), Simulation 275 (14 opt-in skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163. The commit that records this changes only this entry.
- **Sync-docs.** Applied: README (version, the 1.6.0 paragraph), AGENTS.md (the Done line, the stage bullets' release state, the LOD study bullet), the statuses of the Schedule Draw and LOD study plans, the roadmap's progress log, `examples/README.md` (`schedule-draw.gh`), the smoke README (`schedule-draw`, the examples' Run-true check), ADR-033 and the Schedule Draw architecture page (the released generator), the program and construction JSON pages and the user-facing texts (release 2.1.0), the fixture README. `python scripts/docs-export/developer_pages.py --check`: 112 pages checked, the one known redaction. The public site described 1.5.0 (`reference-source.json` at `866da55`); the docs export of the tagged commit, its import in the docs repository, and that repository's own `sync-docs` follow the tag.
- **Release notes.**
  - **New:** *Schedule Draw* in *1 Program*: stochastic 8,760-hour schedules for a program JSON from the atlas generator, an optional add-on whose *Drawn JSON* goes into *Program JSON*. It needs Python 3.11 or later and `atlas-schedules` 3.0.0 installed from the wheel of the atlas release `atlas-schedules-v3.0.0` (in a virtual environment), run as an external command (*Command*: the environment's `Scripts\atlas-schedules.exe`) only while *Run* is true; drawn schedules use the calendar year 2007; apartment-unit and composition recipes are refused. *DOE Reference Program* in *1 Program*. *Program JSON* and *Construction JSON* read atlas release 2.1.0 exports (2.0.0 exports remain valid).
  - **What IDFs change:** a zone's coplanar floors, ceilings, and roofs and windowless wall runs are merged (the header lists the merges); results move slightly (D-192: at most about 2.2 % of annual sensible heating and 1.2 % of cooling where a load is at least 1 kWh/m² a year, in the R2 pilot).
  - **What opens differently:** definitions saved with 1.5.0 open with their saved values; *Convert2IDF* shows *Require Floor Research Eligibility*, false. The examples are rebuilt with 1.6.0 and `schedule-draw.gh` is new.
  - **Not yet performed by a person:** the release-1.6.0 checklist in Rhino 8.
- **What follows:** the tag `v1.6.0` on the merge commit of the pull request, the releases on `EnvironmentalSystemsLab/BEMGen` (notes) and on the docs repository (the files of `scripts/package-release.ps1` built from the tagged commit), and the docs export of `v1.6.0` imported by the docs repository.
- **For a person in Rhino 8:** the release-1.6.0 checklist (installing from the release files, the two new icons, `schedule-draw.gh` with and without *Run*, the viewport previews).

### D-198 — Atlas release 2.1.0 and the released generator 3.0.0: the 2.1.0 schema copy embedded, the recorded bundle recorded again

- **Date:** 2026-10-29 · **Decided by:** Cheng Xuan Li (stage B3 of the public-release plan: pin atlas release 2.1.0 and `atlas-schedules` 3.0.0 for version 1.6.0, contracts unchanged unless a check proves otherwise); the controller (the two changes below, each shown necessary by a check) · **Status:** Accepted
- **Atlas release 2.1.0.** A delta on 2.0.0 ([release](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/v2.1.0), `3f62e19a`): the open licence, the eight apartment folders' `generator.json`, and its manifest; contracts unchanged (program JSON 5.4.0, constructions 4.3.0 / 3.1.0, mass 1.1.0). Exported at `v2.1.0` (`python -m scripts.atlas_exports`, `PYTHONHASHSEED=0`), the 90.1-2019 and DOE Ref 1980–2004 medium offices differ from the 2.0.0 fixtures only in `source.release` (`atlas-release-2.1.0`), and the medium office's detailed and unified 3B construction sets are equal to the fixtures as JSON. The atlas widened the 5.4.0 schema in place: `source.release` admits `atlas-release-2.1.0` (two enum lines, otherwise byte-identical; the construction schemas are byte-identical). BEMGen's embedded copy refused every 2.1.0 program export (`ProgramJsonSchemaViolation` at `/source/release`): the new test `AnExportOfAtlasReleaseTwoPointOneReads` (seven fixtures with that release) failed so before the change. The embedded schema and its fixture copy are now release 2.1.0's; `AReleaseTheSchemaDoesNotNameIsRefused` keeps the enum closed. The programs and constructions stay release 2.0.0 exports: `export_fixtures.py` gains `--schema-atlas`, and its run with the atlas at `f617b30b` and the schema from `v2.1.0` rewrote every other fixture byte for byte (only the schema and the programs' `manifest.json`, which records `program_schema_atlas_commit`, changed). User-facing texts that named only release 2.0.0 (*Program JSON*'s and *Schedule Draw*'s descriptions, the reader's and *Construction JSON*'s refusal messages) name 2.1.0 too. 2.0.0 exports remain valid.
- **Generator 3.0.0.** The wheel `atlas_schedules-3.0.0-py3-none-any.whl` of [`atlas-schedules-v3.0.0`](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v3.0.0) (SHA-256 `f082bb12…229cb`, as the release lists it), installed with pip into `D:\bemgen-venv-schedules` (Python 3.14.7; numpy 2.5.4, jsonschema 4.26.0), reports `generator_version` 3.0.0. `RealDrawTests` (`BEMGEN_ATLAS_GENERATOR=D:\bemgen-venv-schedules`, `BEMGEN_ATLAS_COMMAND=D:\bemgen-venv-schedules\Scripts\atlas-schedules.exe`) first failed on the bundle SHA-256 (`a94624b0…1838` against the recorded `90ff6a71…40e2`): the two bundles differ only in `generator_version` (`3.0.0` against `3.0.0.dev0`), every schedule value equal. `Fixtures/draw/bundle.json` is recorded again with the released generator (two runs byte-identical); the tests that expected `3.0.0.dev0` expect 3.0.0, the pre-release warning test now draws a bundle mutated to `3.0.0.dev0`, and `RealDrawTests` also checks the version 3.0.0 and that no `ScheduleDrawPreRelease` is given. It then passed with the console script and with `python.exe -m atlas_schedules` (generator 3.0.0, 18.9 s and 12.0 s on a loaded machine). [ADR-033](ADR-033-schedule-draw-external-generator.md) records the pin and the install; the component's default command is unchanged.
- **Checks:** `scripts/verify.ps1` on the commit's tree (without the opt-in variables): VERIFY PASSED, 0 warnings: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 299 (1 skipped; 292 before), Simulation 275 (14 skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163.

### D-199 — The public site of 1.6.0: exported after the tag, with D-176's link to the private pull request as plain text

- **Date:** 2026-10-29 · **Decided by:** the controller (a routine choice of stage B3, under the owner's authority to publish, D-197) · **Status:** Accepted
- **What.** The import of the docs export of `v1.6.0` (`e0ccc48`) into the docs repository reported one public-content problem: D-176 links to PR #1 at a path inside the private BEMGen repository, which the public site must not hold (its AGENTS.md rule 5; generated pages are fixed here, never there). D-176's link is now the plain text "PR #1 of the private repository"; its decision and every other word are unchanged. The site is exported from this commit on `main`, which changes only this log after the tag, so `reference-source.json` names version 1.6.0 at this commit rather than at the tag; the plugin, the examples, and the release files are those of `v1.6.0`.
- **Why not a moved tag:** a pushed tag is never moved (the docs repository's rule 2 and D-004's spirit); the documents of the tag differ from the site's only in this link and this entry.
- **The tag checked.** The gate clone `D:\BEMGen-gate\v1.6.0`, checked out at the tag `v1.6.0` (`e0ccc48`, tree equal to D-197's gate commit `d0c991b`), passed `scripts/verify.ps1` again with 0 warnings and D-197's counts. The release files were built by `scripts/package-release.ps1` on the clean tagged checkout (SHA-256: `bemgen-1.6.0-examples.zip` `9c6d85c1…f904`, `bemgen-1.6.0-rh8_19-win.yak` `0b744147…88d1`, `bemgen-1.6.0-rh8-win.zip` `247d6d90…6614`).

### D-200 — R5 serial timing pass run on an idle machine; its coefficient-of-variation gate not met, for the owner

- **Date:** 2026-10-29 · **Decided by:** the owner (stage C3 of the public-release plan: run R5 under decision 14 of the [run plan](../plans/2026-10-29-lod-study-run-plan.md), on an otherwise idle machine); the controller (the waits, the guard, the analysis, and the routine choices below) · **Status:** Accepted for the run; the gate verdict Provisional, for the owner
- **Build.** BEMGen `b29931c` (main after `v1.6.0`), atlas inputs of release 2.0.0 (`96a2e928`; the R3/R4 export under `D:\bemgen-lod-inputs` reused, each file checked by its pinned SHA-256 when the suite was written), EnergyPlus 26.2.0 (`4bd7a1f26f`), i7-14700F (28 logical processors). Suite `lod-timing-20261029-080232`, run `run_20261029-083427`, `run.ps1 -Stage timing` (the runner with `--parallel 1 --timing-repeats 3 --timing-test-cases 12`; the protocol unchanged).
- **Machine state.** Before the run, `dotnet build-server shutdown`; a 30-minute wait (08:04 to 08:34) never saw the machine idle: another project's 2-worker fit (`D:\smart-meter-calibration`, `county_library.py fit --workers 2`) held about 12 %. The run started at 08:34; at 08:35 the same project started `county_calibrate.py stage1 --generations 8000 --chains 24 --workers 14`, and total load was mostly 25 to 60 % until about 13:20. Nothing of that project was stopped. The serial main phase (08:34 to 09:29) ran beside it: 440 of 440 written sites succeed, 418 of 418 test sites pair (largest deviation 2.9 × 10⁻¹⁰ W), deduplication and recommendations as R2's; its serial times in `sites` are loaded measurements (processor time a median 45 % above the timing pass's, up to 185 %), superseded evidence, not results. A guard then stopped this run's runner and its EnergyPlus (only these) at 09:29:51 as the first timing run began, before any timing row was written. Polling every 10 minutes (later every 2) for a 5-minute window with average under 5 %, maximum under 10 %, and no EnergyPlus, Rhino, or MSBuild, the machine was idle at 13:38 (4.2 %, 6.0 %), and `run.ps1 -Resume` ran the whole timing pass 13:38 to 14:31 with the guard armed (it would have stopped the runner on foreign load again; it did not trigger). Load in 30-s samples during the pass: mean 5.1 % (one EnergyPlus is 3.6 %), at most 11.9 % at 13:39–13:41 with two short foreign scripts.
- **Counts.** 12 test cases (no medium office, no primary school, by the SHA-256 order), 218 sites, 654 of 654 timing runs completed.
- **Gate (coefficient of variation of the processor time per site < 5 %): not met.** 192 of 218 sites pass, 26 miss, the largest 12.9 % (median 2.2 %, P90 5.3 %); peak committed memory varies by at most 0.55 %. Not a cold start: without repeat 1, 31 miss. 16 misses are among the 34 sites of at least 4 s: from about 14:21, late in repeat 3, every run took 13 to 24 % more processor time than in repeats 1 and 2 at unchanged total load and with no foreign process (over repeats 1 and 2, 2 of the 34 miss); the cause is not established (one candidate: the scheduler moving the single EnergyPlus thread between the 14700F's performance and efficiency cores). The other 10 misses are runs of 0.8 to 3.3 s, where the 15.6 ms tick of the processor-time count is about 2 % of the value. Whether to run R5 again (for example with the process pinned to a performance core, or with more repeats), to judge the gate on longer sites, or to accept the medians is the owner's; no tolerance or gate was changed.
- **Results.** Medians relative to the reference: over all 206 timed test sites 0.504 processor time, 0.521 wall clock, 0.985 peak committed memory; *Single Zone Building* 0.424, 0.422, 0.980 (50 sites; outpatient 0.064, small hotel 0.057, strip mall 0.256, full-service restaurant 0.787). Per prototype and per zoning in [the run plan §4](../plans/2026-10-29-lod-study-run-plan.md#4-stages); full tables in `D:/bemgen-results/lod-study/timing/timing-analysis/timing-summary.md` and `timing-sites.csv`, written by `timing_analysis.py` beside them (SHA-256 `58605220…e072`, read-only on the merged `central.duckdb`; a routine choice: kept with the results, not in the repository, since it only tabulates the runner's `site_timing`). `report.py`'s outputs are in `…/timing/report/`.
- **Not done.** No Rhino step is involved. The repeat-3 slowdown was not diagnosed further.

### D-201 — R4's small-hotel failures: such zonings are not applicable in their cells; no BEMGen change

- **Date:** 2026-10-29 · **Decided by:** the controller, under the owner's blanket authority for the public-release stages (stage C4) · **Status:** Accepted · Closes the open question of D-193
- **Decision.** The 24 R4 sites that failed (the small hotel's zonings that keep the unconditioned elevator core, the source's 32 kW elevator load in 15 m², or a mechanical room as its own zone, with IWHT off; EnergyPlus diverges in warm-up, D-193) need no BEMGen change: the program's load and the option are written as given (GLOBAL.md scientific rule 3). The study treats such zonings as not applicable in that cell: the cell's recommendation comes from the zonings that ran (as `report.py` already does: a failed site is listed and never recommended), the failures are listed in the study report with the zone EnergyPlus names, and the methodology names this as a limit of adiabatic interior walls around an isolated high-gain unconditioned zone (study report §4.3 (`research/lod-study/report/2026-10-29-lod-study-report.md`), methodology §M9 (`research/lod-study/report/2026-10-29-lod-study-methodology.md`)).
- **Why.** With IWHT on the same zones run in R2 and R3; the divergence is a property of the boundary condition with that load, not of the zoning or the writer. Nothing was relaxed.

### D-202 — R5's timing gate: costs reported as medians of site ratios; the repeat check of the long sites run once

- **Date:** 2026-10-29 · **Decided by:** the controller, under the owner's blanket authority for the public-release stages (stage C4) · **Status:** Accepted · Closes the open question of D-200
- **Decision.** 192 of 218 R5 sites meet the < 5 % processor-time CV gate; the misses are explained (10 short runs where the 15.6 ms clock step is about 2 % of the value; 16 long sites slowed 13 to 24 % late in repeat 3 for a reason not established, D-200). The study reports costs as medians of site ratios (test site over reference, each the median of its three repeats), states the per-site CV distribution (median 2.2 %, P90 5.3 %, largest 12.9 %) and the misses, and claims no per-site precision below that. The gate and the tolerances are unchanged. The medium office and the primary school were not among the 12 timed test cases; that is named as a limit.
- **Repeat check, run once.** The runner cannot select sites of a suite, but its IDF-folder mode times exactly the IDFs given: the 34 R5 sites of at least 4 s (6 test cases with their references) were copied from the R5 suite to `D:\bgdiag\r6-retime\idf` and run with `--weather D:\bemgen-weather\tmy3 --timing-repeats 3` (main phase 14 at a time, then the serial timing pass), BEMGen `d32fa2a` (only documents changed since R5's `b29931c`), run `run_20261029-144634`. The machine was idle before it (5-minute average 1.7 %, at most 4.5 %, no `smart-meter-calibration` or other Python process); during the timing pass (14:50 to 15:32 local) total load averaged 4.8 %, at most 8.1 %, in 30-s samples. **Outcome:** 102 of 102 timing runs complete; no site at or above 5 % (largest 4.8 %, median 2.05 % against R5's 3.73 % for the same sites; R5 had 16 misses among them); repeat 3 over the mean of repeats 1 and 2 has median 1.000 (largest 1.073), so R5's late slowdown did not recur. The absolute processor times are a median 15 % above R5's, and the 28 test sites' ratios to their references moved by a median of −4.5 % (−17 % to +5 %). The misses did not persist, but a session's level moves; per-site ratios are reproducible to about ±15 % between sessions, which the report states (study report §5.5 (`research/lod-study/report/2026-10-29-lod-study-report.md`)).

### D-203 — R6: the study report, the methodology, and the consolidated recommendations (schema 1.1.0)

- **Date:** 2026-10-29 · **Decided by:** the controller, under the owner's blanket authority for the public-release stages (stage C4); the routine choices below by the R6 builder · **Status:** Accepted; the documents are for the owner's review
- **What was written.** `scripts/lod-study/study_tables.py` (with `tests/test_study_tables.py`) reads the R3, R4, and R5 stage folders read-only and writes (1) the study report (`research/lod-study/report/2026-10-29-lod-study-report.md`): purpose, method, the R3 recommendations per prototype × climate zone × vintage × orientation (11 tables, 264 rows: recommended zonings, stored errors, benchmark loads, the closest zoning of the 46 cells without one), the R4 sub-study by heat-transfer setting and its 24 failures with the zone EnergyPlus names, the R5 costs by prototype, zoning, and recommended zoning, the repeat check of D-202, deduplication rates, and the limits; (2) the methodology (`research/lod-study/report/2026-10-29-lod-study-methodology.md`), §M1 to §M10, every number with its source; (3) `research/lod-study/results/`: `lod-recommendations.json` (R3's 264 entries, 218 with a recommendation, unchanged, plus the serial `cost` of the 12 timed references and 206 timed test sites and a `timing` block), `lod-recommendations-ht.json` (R4, 22 entries, 18 with a recommendation, separate), and `provenance.json` (BEMGen builds `2ed856c` for R3/R4, `b29931c` for R5, `d32fa2a` for the repeat check; suites and runs; atlas inputs 2.0.0 `96a2e928`; EnergyPlus 26.2.0 `4bd7a1f26f`; the threshold; the gate verdicts; the SHA-256 of sources and files). The tables are generated between `table:` markers; `--check` verifies them and the files.
- **Schema 1.1.0.** `lod-recommendations-v1.schema.json` accepts version 1.0.0 or 1.1.0; 1.1.0 adds only optional members (`timing`, and `cost` on a reference and a zoning), recorded in its `$comment`. A test validates the committed file and a 1.0.0 document.
- **`report.py` fix.** A site that did not complete has no row in the runner's `sites`, so its zoning was null in the recommendations; it is now taken from `suite_sites` (`fill_suite_zoning`, test-first: the two tests failed on the missing function). R4's report was written again into `D:/bgdiag/r6-ht-report` (the stage folder stays read-only); it differs from the first drop only in the 24 failed zonings' zoning (checked entry by entry; `duplicates.csv` and `metrics.csv` byte-identical).
- **Routine choices.** Costs are matched to R3's zonings by site name (test case and zoning code); the 218 timed IDFs of R5 equal R3's apart from their comment lines (build stamps), checked file by file. The consolidated JSON is written compact (7.8 MB, against 11.1 MB indented); R4's file is `report.py`'s output as written (3.6 MB). These are the published, derived recommendation files the run plan's §9 names, committed as the study's results (no IDF, database, or hourly output is committed). In R4 a recommendation "with IWHT or FHT off" is often the deduplicated twin of the both-on zoning (deduplication keeps "off" first in zoning order); the report says so rather than changing the rule. P90 of the CV is computed as type 7 (5.26 %); D-200's 5.25 % used a lower-rank estimate.
- **Checks.** `python -P -m unittest discover -s scripts/lod-study/tests`: 46 passed. `study_tables.py --check`: `TABLES CURRENT`. `scripts/verify.ps1`: see the change description.
- **Not done.** No Rhino step is involved. The atlas site's import of the consolidated drop is atlas work (run plan §9). The cause of R5's late slowdown is still not established; it did not recur in the repeat check.

### D-204 — Version 1.7.0: atlas release 2.2.0 and Schedule Draw on the released generator 4.0.0

- **Date:** 2026-10-30 · **Decided by:** Cheng Xuan Li (move BEMGen to atlas release 2.2.0 and generator 4.0.0 and release 1.7.0, with blanket authority to merge, push, tag, and publish the releases once verify and the gates are green, as for 1.6.0, D-197); the controller (the preparation and the routine choices below) · **Status:** Accepted
- **Version.** 1.7.0, prepared on `release/v1.7.0` from `main` at `38ff521`, a minor version as D-125, D-175, and D-197 reason: D-064 waives backward compatibility, and no component or parameter GUID changed or moved since `v1.6.0` (each of its 103 GUIDs is still in the same source file of `src/Lod.Grasshopper`; none is new). No component, input, or output is added or removed; *Schedule Draw*'s input descriptions change with what they take (D-205). The icons are byte-identical to `v1.6.0`'s.
- **What it holds since `v1.6.0`:** the LOD study runs and report on `main` (D-193, D-200 to D-203, PRs #9 to #11; tools and documents, no plugin change), and this preparation:
  - **Atlas release 2.2.0 and generator 4.0.0** (D-205, [ADR-035](ADR-035-schedule-draw-generator-4-0-0.md), [design note](../plans/2026-10-30-generator-4-0-0.md)): the embedded program JSON 5.4.0 schema with the release pattern, so 2.0.0, 2.1.0, 2.2.0, and later labels read; *Schedule Draw* and the suite's `schedules:` on request and bundle schema 4.0.0, release program IDs, the export's view, the release folder's `generation.json`, setting 2.0.0, and the bundle's `release` in the provenance; the recorded draws recorded again with the 4.0.0 wheel.
  - The version in `Directory.Build.props`; the 21 example definitions rebuilt with the 1.7.0 plugin (`BEMGEN_EXAMPLES_WRITE=1`), `schedule-draw.gh` with the release 2.2.0 `generation.json` and setting 2.0.0 in its panels (routine choice: the same layout and Stream Filter gate as in 1.6.0); the smoke spec `schedule-draw` checks 4.0.0 and the release in the provenance; the release-1.7.0 checklist for a person in Rhino, appended to [grasshopper-smoke-test.md](../development/grasshopper-smoke-test.md#release-170-checklist-d-204).
- **Checks on the release candidate:**
  - **Definitions saved with 1.6.0.** The 21 example files as committed before the rebuild (saved with the 1.6.0 plugin) reopened with the 1.7.0 plugin (`1.7.0+edf06a9`): every archive read without a warning or error, and all 21 solved with one *Validate* True and no runtime error (63 checks passed); the one warning, *Program JSON*'s `ProgramJsonNotInstantiated` of the two hot-water zone gain records in `schedule-draw.gh`, is 1.6.0's. Its *Run* true was not tried with the 1.6.0 panels: their setting 1.0.0 is refused by design (D-205; an item of the person-in-Rhino checklist).
  - **Examples.** All 21 rebuilt with the 1.7.0 plugin; each reopened and solved with one *Validate* True and no error; the same one warning. With `BEMGEN_SCHEDULE_COMMAND` set to `D:\bemgen-venv-schedules\Scripts\atlas-schedules.exe` (generator 4.0.0), `schedule-draw.gh` with *Run* true solved with no error, *Validate* True, and the drawn lighting schedule in the IDF (66 checks passed).
  - **Rhino smoke.** All 27 specs of `scripts/rhino-smoke` in Rhino 8.25.25314.11001 on the candidate's plugin code (`9cad338`), with `BEMGEN_SCHEDULE_COMMAND` set: 1519 *Validate* True and none False, 1003 spec checks passed and none failed (1.6.0: 1002; the new one checks the release in the draw's provenance), no missing component or missing expected error, no exception, nothing `SKIPPED`; runtime errors only in the error scenarios and, in the DOE specs, on the component placed without a program map, as in 1.6.0. The `schedule-draw` spec drew with generator 4.0.0 on atlas release 2.2.0 (manifest `67e73e55…7ece4`) and no `ScheduleDrawPreRelease`, the same text twice and another for seed 43. Another project's Python workers (about ten processes) ran throughout; no EnergyPlus batch was started.
  - **`scripts/verify.ps1`** on the candidate's tree: VERIFY PASSED, 0 warnings: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 332 (2 skipped), Simulation 275 (14 opt-in skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163.
  - **Fresh-clone gate.** A clean clone of `release/v1.7.0` at `93c9f96` from GitHub (`D:\BEMGen-gate\v1.7.0`) passed `scripts/verify.ps1` with 0 warnings and the same counts: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 332 (2 skipped), Simulation 275 (14 opt-in skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163. The commit that records this changes only this entry.
- **Sync-docs.** Applied: README (version, the 1.7.0 sentence), AGENTS.md (the Done line, the Schedule Draw bullet), the roadmap's progress log, the design note's status, `examples/README.md` (`schedule-draw.gh`), the smoke README and the Schedule Draw checklist (generator 4.0.0 and the new files), ADR-033 (amended by ADR-035) and the Schedule Draw architecture page, the program JSON, construction JSON, and pipeline pages and the schedule-generator requirement (release 2.2.0, generator 4.0.0), the fixture README, the test-suite README and spec schema. `python scripts/docs-export/developer_pages.py --check`: 114 pages checked, the one known redaction. The public site describes 1.6.0 (`reference-source.json` at `4f1b806`); the docs export of the tagged commit, its import in the docs repository, and that repository's own `sync-docs` follow the tag.
- **Release notes.**
  - **Changed:** *Schedule Draw* uses the atlas schedule generator `atlas-schedules` 4.0.0, installed from the wheel of the atlas release `atlas-schedules-v4.0.0` (check it with that release's `SHA256SUMS.txt`); the wheel brings atlas release 2.2.0 with it. Its *Generator JSON* input now takes the `generation.json` of the program's folder in atlas release 2.2.0 (`atlas-release-2.2.0.zip` of the atlas release `v2.2.0`, `v2.2.0/<family>/<template>/<type>/generation.json`) in place of the earlier `generator.json`, and its setting is version 2.0.0 (generator 4.0.0, bundle schema 4.0.0, no `view`: the program JSON's own version, filled or source, chooses the values drawn from). The draw records the atlas release and its manifest checksum.
  - **New:** *Program JSON* and *Construction JSON* read exports of atlas release 2.2.0 (the contracts did not change; 2.0.0 and 2.1.0 exports remain valid), and later releases of the same program JSON 5.4.0 contract are read without a new version of BEMGen.
  - **What a user with stored 1.6.0 draws changes:** a drawn program JSON from 1.6.0 still reads. To draw again, replace the `generator.json` panel with the release 2.2.0 `generation.json` and the setting with a 2.0.0 one (a 1.0.0 setting and a `generator.json` are refused with what to give instead); BEMGen then writes the request for generator 4.0.0 itself; a suite's stored 3.0.0 request (`draws/<test case ID>.request.json`) run by hand converts once with `atlas-schedules translate`. For the recorded DOE Ref medium-office draw the schedules are value-identical to 1.6.0's; the atlas reports the same for 263 of its 266 sampled generator 3.0.0 bundles, the other 3 being retired hotel corridor compositions, which *Schedule Draw* does not draw; the atlas's 90.1 apartment-building common-area recipes (`fixed`) now carry the release's heat fractions, so their draws can differ.
  - **What opens differently:** definitions saved with 1.6.0 open with their saved values; the examples are rebuilt with 1.7.0.
  - **Not yet performed by a person:** the release-1.7.0 checklist in Rhino 8.
- **What follows:** the merge (PR #12), the tag `v1.7.0` on the merge commit, the releases on `EnvironmentalSystemsLab/BEMGen` (notes) and on the docs repository (the files of `scripts/package-release.ps1` built from the tagged commit, with `SHA256SUMS.txt`, marked latest), and the docs export of `v1.7.0` imported by the docs repository (D-206).
- **For a person in Rhino 8:** the release-1.7.0 checklist (installing from the release files, `schedule-draw.gh` with and without *Run* on 4.0.0, a 1.6.0-saved `schedule-draw.gh`, the viewport previews).

### D-205 — Atlas release 2.2.0 and the released generator 4.0.0: the 5.4.0 schema with its release pattern, Schedule Draw on release IDs and the export's view (ADR-035), the recorded draws recorded again

- **Date:** 2026-10-30 · **Decided by:** Cheng Xuan Li (version 1.7.0: pin atlas release 2.2.0 and `atlas-schedules` 4.0.0, as the atlas's ADR 0051 §8 asks of BEMGen, under the blanket authority of D-204); the controller (the design of [ADR-035](ADR-035-schedule-draw-generator-4-0-0.md) and the routine choices below) · **Status:** Accepted
- **Atlas release 2.2.0.** A delta on 2.1.0 ([release](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/v2.2.0), atlas `2b3a6870`, `atlas-release-2.2.0.zip` checked with its `SHA256SUMS.txt`: `204675cb…f343`; its `v2.2.0/manifest.json` has the SHA-256 `67e73e55…7ece4` the atlas names): each generated folder's `generation.json` and `definition-map.json` added, every `generator.json` removed; program IDs unchanged. The seven program fixtures exported at `2b3a6870` (`python -m scripts.atlas_exports --program <ID> --version <version>`, `PYTHONHASHSEED=0`, in a `git archive` of that commit outside the atlas checkout) are equal to the release 2.0.0 fixtures as JSON apart from `source.release` (`atlas-release-2.2.0`), all seven. The atlas changed the 5.4.0 schema in place once more: `source.release` is the pattern `^atlas-release-\d+\.\d+\.\d+$` in place of the enum of four labels (two places, otherwise byte-identical). BEMGen's embedded copy refused every 2.2.0 export (`ProgramJsonSchemaViolation` at `/source/release`): the new tests `AnExportOfAtlasReleaseTwoPointTwoReads` (seven fixtures) and `ALaterReleaseLabelReads` failed so before the change. The embedded schema and its fixture copy are now `2b3a6870`'s (SHA-256 `08844cbb…503e`; the manifest's `program_schema_atlas_commit` names that commit); `AReleaseLabelOfAnotherShapeIsRefused` (five labels, among them `atlas-release-2.2` and `atlas-release-2.2.0-rc1`) replaces `AReleaseTheSchemaDoesNotNameIsRefused`, whose label 2.2.0 the contract now admits; the 2.1.0 test stays. The construction schemas (unified 3.1.0, detailed 4.3.0, mass 1.1.0, ground 1.0.0) are byte-identical at `2b3a6870` and have no release enum; nothing else needed. User-facing texts that named releases 2.0.0 and 2.1.0 name 2.2.0 too.
- **Generator 4.0.0** ([`atlas-schedules-v4.0.0`](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v4.0.0); `sha256sum -c SHA256SUMS.txt`: the wheel `atlas_schedules-4.0.0-py3-none-any.whl` `8302c0ab…7ccd3` and the sdist OK), installed with `pip install --upgrade <wheel>` into `D:\bemgen-venv-schedules` (Python 3.14.7); `atlas-schedules --version` prints `atlas-schedules 4.0.0 (request schema 4.0.0); reads atlas release 2.2.0 from …\atlas_schedules\data\atlas-release (generator view)`. Its seed policy is 3.0.0's (`commercial_group_seed(42, "zone")` and `(42, "Z1")` give the values the existing test pins). [ADR-035](ADR-035-schedule-draw-generator-4-0-0.md) amends ADR-033: the pins (generator 4.0.0, request and bundle schema 4.0.0, data release 2.2.0 by its manifest SHA-256; the pre-release logic kept), the program setting is the release folder's `generation.json`, the request names the export's `id` and its `version` as `values`, shared services come from the export's hot-water demands that name a service of the files, the methods `comstock_hours` and `fixed` only, a slot's load among several by the bound magnitude, the bundle's `release` and owners' `values` checked and recorded, and the setting 2.0.0 without `view`.
- **How an export maps to the request.** The release program ID is the export's `id` (equal to `source.program_id`; the same in exports of 2.0.0, 2.1.0, and 2.2.0). `values` is the export's `version`: a filled export asks for `filled` and a source export for `source`; where the program's generation block has no view of that name, the request asks for `source`, the generator's own default for such a block, with the information `ScheduleDrawValuesSource`. This is the case of the DOE Ref programs, whose blocks carry only `source`: generator 4.0.0 refuses `values: filled` for them (`unsupported_input at /values: … has no filled view`, observed), and under 3.0.0 their filled exports were drawn with the source recipe too. The magnitude check stays the guard.
- **Tests first.** The draw's tests were written before the code and failed by not compiling (`BundleRelease`, `ScheduleDrawResult.Release`, `DrawnInstance.Values`, `ScheduleDrawCodes.ValuesSource`, `ScheduleDrawSetting.PinnedRelease…`, `GeneratorRecipes.ServiceConfigurations`, the new `GeneratorRecipe`); after the code one test failed on its own miscount (it expected one `ScheduleDrawValuesSource` note; the draw has two instances, so two, one per instance, which the test now checks by subject). The review (D-111) found no blocking problem; its findings were applied: the load choice among several now compares within `ToleranceSettings.RelativeLoad` as the magnitude check does, and three tests pin it (another magnitude before the bound load, two loads of the bound magnitude refused as `ScheduleDrawAmbiguous`, a hot-water load without a value needing no service); a control character in a comment, stale comments, and the Schedule Draw checklist's file names were fixed. The reviewer also scanned the 734 `comstock_hours` programs of release 2.2.0 in both views and found BEMGen's shared services equal to the atlas assembler's required services for every one.
- **The recorded draws.** `Fixtures/draw/`: the DOE Ref 1980–2004 and 90.1-2019 medium offices' `generation.json` (byte for byte from the release zip, equal to `2b3a6870`'s), `setting.json` 2.0.0, `request.json` as BEMGen now writes it (`values` `source`), and `bundle.json` from the wheel (`fbdf6a5e…acfe`; three runs, the console script twice and `python -m atlas_schedules` once, byte-identical). Its schedules and owners equal the generator 3.0.0 bundle's (`a94624b0…1838`, D-198) apart from the owners' new `values`; the versions and the `release` block are new. A second recorded draw, the 90.1-2019 medium office's source export as one instance of 250 m² (`b1620ee2…ff19`, two runs identical), covers a source view, its configuration, its hot-water load, and a second lighting load without a value. `generator.doe-ref-1980-2004.medium-office.json` is gone (in git history).
- **The gated test.** `RealDrawTests` (`BEMGEN_ATLAS_GENERATOR=D:\bemgen-venv-schedules`) passed with `BEMGEN_ATLAS_COMMAND=D:\bemgen-venv-schedules\Scripts\atlas-schedules.exe` and again with `D:\bemgen-venv-schedules\Scripts\python.exe -m atlas_schedules`: both tests (the recorded DOE Ref draw drawn twice, the 90.1 source draw), generator 4.0.0, no `ScheduleDrawPreRelease`, release 2.2.0 with the pinned manifest, both bundles equal to the recorded ones byte for byte and the second run equal to the first (4.85 s and 4.45 s for one draw).
- **What a user changes.** *Schedule Draw*'s inputs, outputs, defaults, and GUID are unchanged; its descriptions name 4.0.0, `generation.json`, and setting 2.0.0. A setting 1.0.0 is refused with what to change, and a `generator.json` with the file to give instead. A suite's `schedules.recipes` lists `generation.json` files. A drawn program JSON stored by 1.6.0 still reads; to draw it again, give the 2.2.0 `generation.json` and a 2.0.0 setting.
- **Checks:** `scripts/verify.ps1` before each commit, VERIFY PASSED with 0 warnings: Core 1040, Generators 3051 (1 skipped), Integration 3629, Export 3132 (1 skipped), ConstructionJson 311, ProgramJson 312 (1 skipped) after the schema, 329 (2 skipped, the two opt-in real draws) after the draw, and 332 (2 skipped) with the review's tests, Simulation 275 (14 skipped), IdfBatchRunner 105 (3 skipped), TestSuiteGenerator 163.
- **Not done.** The software-only launcher's reviewed-source policy, which a person refreshes for changed sources (as D-196 left it).
