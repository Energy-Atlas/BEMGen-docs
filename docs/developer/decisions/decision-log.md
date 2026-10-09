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

- **Date:** 2026-09-30 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
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

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
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

- **Date:** 2026-10-02 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
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
