# AGENTS.md

Instructions for coding agents (and humans) working in this repository.

## Read first

Before changing architecture, pipeline types, or transformation logic, read:

1. [GLOBAL.md](GLOBAL.md) — non-negotiable rules. They override anything below.
2. `README.md` — scope and pipeline overview.
3. [docs/LOD_grasshopper_plugin_repository_spec.md](LOD_grasshopper_plugin_repository_spec.md) — architecture, domain objects, interfaces, testing strategy, milestones.
4. [docs/LOD_geometric_zoning_equivalence_research_brief.md](LOD_geometric_zoning_equivalence_research_brief.md) — research questions, Z/W/V levels, equivalence math, required invariants.
5. [docs/decisions/decision-log.md](decisions/decision-log.md) and any ADRs in `docs/decisions/` touching the area you are changing.
6. The current roadmap and stage plan in `docs/plans/`.

## Recording decisions

Several people and agents work on this project, so decisions made in chat must not live only in a chat transcript.

- When a conversation settles scope, architecture, research rules, process, or tooling, append a `D-NNN` entry to [docs/decisions/decision-log.md](decisions/decision-log.md) in the same session, following the format at the top of that file.
- Decisions with real trade-offs also get an ADR (`docs/decisions/ADR-NNN-<topic>.md`), linked from the log entry.
- Never edit a past entry's decision; supersede it with a new entry.
- Plans live in `docs/plans/` (`YYYY-MM-DD-<name>.md`) and carry a status line (Draft, Approved, In progress, Done).

## Project state

The roadmap's progress log is the stage-by-stage record ([implementation roadmap](plans/2026-09-30-implementation-roadmap.md)); this section is a short summary and is not rewritten every stage (D-111).

- **Done:** S0–S9, tags `v0.0.1` to `v0.9.1` (S6 is `v0.9.0`, D-113; the zero-width fix is `v0.9.1`, D-114), `v1.0.0` for S9 (D-116), `v1.0.1`, which moved the docs site to the public repository `energy-atlas/BEMGen-docs` (D-117 to D-119), `v1.0.2`, which adds the enum inputs' right-click values and dropdown (D-120, D-121), and `v1.1.0` (D-125), which adds Conditioned Merge and joined pieces (D-123) and the program mix with building-level infiltration (D-124, [ADR-017](decisions/ADR-017-program-mix-and-building-infiltration.md)), and `v1.2.0` (D-127), which adds *Program JSON* and the extended program model (D-126, [ADR-018](decisions/ADR-018-program-json-and-extended-programs.md)) and retires the S10 atlas fetch components (D-122, kept only as the tag `archive/archetype-data`), and `v1.3.0` (D-131), which makes the IDF simulation-ready (EnergyPlus 26.2, a *Weather* input, the [experiment outputs](research/experiment-outputs.md), shading of unmodelled storeys) and adds the EnergyPlus runner `Lod.Simulation` (D-130, [ADR-019](decisions/ADR-019-simulation-ready-idf-and-runner.md)), and `v1.4.0` (D-144), which adds *Construction JSON* and *Convert2IDF*'s *Construction* and *Fill From Example* inputs (D-137 to D-143, [ADR-021](decisions/ADR-021-construction-sets-and-mass-ledger.md)), with the batch runner and test-suite tools of D-132 to D-136, and `v1.5.0` (D-175), which adds the DOE reference geometry generators (D-160 to D-171), native ground for construction sets (D-145 to D-149), the suite, runner, and evaluation-metric tools (D-151 to D-159), and the atlas release 2.0.0 contracts with no daylight dimming in IDF runs (D-172 to D-174), and `v1.6.0` (D-197), which adds *Schedule Draw* with the released atlas generator 3.0.0 (D-194 to D-196, D-198), the research contracts and *DOE Reference Program* (D-177 to D-184), the LOD study tooling and the IDF writer's coplanar merge (D-185 to D-192), and reads atlas release 2.1.0 exports (D-198), and `v1.7.0` (D-204), which moves *Schedule Draw* to the atlas generator 4.0.0 on atlas release 2.2.0 and reads release 2.2.0 exports (D-205, [ADR-035](decisions/ADR-035-schedule-draw-generator-4-0-0.md)). The pipeline (program presets → plan generator → plan simplifier → floor aggregator → validation → `Convert2BEM` or `Convert2IDF`, [docs/architecture/pipeline.md](architecture/pipeline.md)) runs end to end in Rhino 8 for 18 plan generators, one per family of the four-source precedent set except the set-aside `SYN-TYP-013` ([syn-typologies.md](research/precedents/syn-typologies.md), D-093, D-096), housing and non-residential ([ADR-006](decisions/ADR-006-plan-generation-mechanism.md), [ADR-014](decisions/ADR-014-program-types-and-department-zoning.md), [ADR-015](decisions/ADR-015-plans-per-storey.md)).
- **Construction JSON stage** (D-137 to D-143, [ADR-021](decisions/ADR-021-construction-sets-and-mass-ledger.md), [ADR-022](decisions/ADR-022-residential-construction-sets.md)), released in `v1.4.0` (D-144).
  - *Construction JSON* imports the atlas's unified construction JSON into a construction set, only a building-scope one: a single-dwelling set is refused (D-142).
  - *Convert2IDF* takes the set through its *Construction* input and balances internal mass against the set's reference capacity budgets; each exposed face of a removed slab is a half slice, so the IDF holds its capacity once (D-143).
  - A role the set lacks is an error unless *Fill From Example* is on.
  - Detailed documents are read as evidence and never converted (D-142).
- **Construction foundation v7 stage** (D-145, D-146, [ADR-023](decisions/ADR-023-native-ground-methods-and-packet-v7.md)), built and reviewed on `claude/bemgen-construction-v7-update-bd63b1`, merged into `main` (D-150), released in `v1.5.0` (D-175).
  - Packet v7 replaces v3 (D-145); foundation data are read and instantiated from declared geometry in `Lod.Core`.
  - *Convert2IDF* gives a v7 set's ground floors its own F-factor or layered method, with ground temperatures from the weather file (F-factor) or 18 °C (layered); Kiva and the C-factor wall are written only outside the pipeline.
- **Suite constructions and ground stage** (D-151, [design note](plans/2026-10-19-suite-constructions-ground.md)), merged into `main` (D-152), released in `v1.5.0` (D-175).
  - Test suites take unified construction JSON sets with their fill choice, each paired only with weather files of its climate zone; a site whose Example windows fill a windowless set over a non-absorbing ground floor is `Invalid` and not written.
  - The research outputs gain the hourly building-level ground heat transfer (experiment outputs §9), which *Convert2IDF* requests, `Lod.Simulation` reads, and the batch runner stores (central schema version 3).
- **Runner progress and site status** (D-152, D-153, [design note](plans/2026-10-21-runner-progress-and-site-status.md)), merged into `main` and pushed (D-154), released in `v1.5.0` (D-175): the batch runner prints each site's progress line when its simulation finishes, and the central database keeps a status row for every site (`site_status`, `site_overview`). The results folder redesign ([design note](plans/2026-10-22-results-folder-redesign.md)) followed on the same branch: central schema version 5 without hourly rows, an hourly Parquet file per site written by the worker, `raw/` and `failure/` instead of the batch database and the site files, `--keep-raw` in place of the suite setting `discard_ep_results`, incremental resume, folder merge, and sites started in plan order.
- **Paired evaluation metrics** (D-156, D-157, [design note](plans/2026-10-26-evaluation-metrics.md)), merged into `main` (D-158), released in `v1.5.0` (D-175): `Lod.Simulation` gains `EvaluationMetrics` ([experiment outputs §10](research/experiment-outputs.md#10-paired-evaluation-metrics)) on the ideal sensible heating and cooling summed over the zones, the conditioned temperature over all hours, and the cost with processor time and process memory; the runner stores them in central schema version 7 with a `metric_definitions` table and 20 hourly series, and its optional serial timing pass (`--timing-repeats`) fills `site_timing`.
- **DOE reference geometry generators** (D-160 to D-171, [design note](plans/2026-10-25-doe-geometry-generators.md), [ADR-025](decisions/ADR-025-doe-reference-geometry-generators.md), [ADR-026](decisions/ADR-026-multiplied-rooms.md)), merged into `main` (PR #1), released in `v1.5.0` (D-175): 11 generators for the 15 DOE commercial building types, one *DOE* component each in *2 Generate* with *DOE Program Map* and icons, one *DOE … Programs* preset component each in *1 Program Presets* (illustrative loads, the source's glazing per key), glazing per orientation and skylights, and multiplied rooms ([layouts](architecture/doe-layouts.md), [components](architecture/doe-components.md)); programs wait on atlas inputs A1 to A3, so tests use fixture programs. The roadmap's progress log has the stages.
- **Atlas release 2.0.0 contracts** (D-172, [ADR-027](decisions/ADR-027-atlas-release-2-0-0-contracts.md), [design note](plans/2026-10-28-atlas-release-2-0-0.md)), merged into `main` (PR #2), released in `v1.5.0` (D-175): *Program JSON* reads program JSON 5.4.0 (`filled` and `source`, by climate zone and construction context) and no longer 2.0.0; programs carry the atlas's daylighting controls as given, as source data that *Convert2IDF* never writes (the owner's decision D-174: no dimming in IDF runs); hot water can take the weather file's water mains; *Construction JSON* reads detailed 4.3.0 (alternates as information) and unified 3.1.0; the test fixtures are release 2.0.0 exports written by `scripts/atlas-fixtures/export_fixtures.py`, since D-173 from the release as the atlas corrected it in place (shared mass contract 1.1.0, the IECC ground slabs under `GroundFloor`), so the IECC sets are read and refuse conversion only for their source design-flow infiltration.
- **Research contracts and reference programs** (D-177 to D-183, [ADR-028](decisions/ADR-028-reference-programs-and-research-contract.md) to [ADR-031](decisions/ADR-031-exact-composition-identity-preflight.md)), built on `integration/main-bemgen-research-20261028`, merged into `main` (D-184), released in `v1.6.0` (D-197): the backend DOE reference catalog with authenticated MidriseApartment programs of DOE 1.3_5.0 and 1.4_7.2 ([usage and limits](research/reference-program-contract.md)), *DOE Reference Program* in Grasshopper, *Convert2IDF*'s appended input *Require Floor Research Eligibility* (index 11, false by default), the opt-in floor research gate with spatial program signatures, source and derived volume ledgers, the default-off exact-composition identity screen, the backend comparison energy report, and the software-only test launcher `scripts/verify-software-only.ps1`. Existing GUIDs, defaults, and illustrative presets are unchanged; reporting stays backend-only.
- **LOD study tooling and the coplanar merge** (D-185 to D-192, [ADR-032](decisions/ADR-032-doe-prototype-suites-and-study-inputs.md), [ADR-034](decisions/ADR-034-coplanar-surface-merge.md), [run plan](plans/2026-10-29-lod-study-run-plan.md)), merged into `main` (PRs #4 and #6), released in `v1.6.0` (D-197): DOE prototype suites with pinned atlas inputs and weather, the stage driver and the deduplicating report with `lod-recommendations.json`; the runner's limited expected warning `OutdoorWetBulbIteration`; *Convert2IDF* merges a zone's coplanar floors, ceilings, and roofs and windowless wall runs (`SurfacesMerged`), splits a self-touching floor ring, and treats a mass shortfall within the area tolerance as none.
- **Schedule Draw** (stage B2, D-194 to D-196, [ADR-033](decisions/ADR-033-schedule-draw-external-generator.md), [design note](plans/2026-10-29-schedule-draw.md), [architecture](architecture/schedule-draw.md)), released in `v1.6.0` (D-197): the atlas's stochastic schedules as an optional add-on, drawn by `atlas_schedules` run as an external command (since `v1.7.0` generator 4.0.0 on atlas release 2.2.0, D-204, D-205, [ADR-035](decisions/ADR-035-schedule-draw-generator-4-0-0.md): the released wheel of `atlas-schedules-v4.0.0` in a virtual environment, its `atlas-schedules` console script, the program folder's `generation.json` of release 2.2.0 as the program setting, and the export's own view; 3.0.0 in `v1.6.0`, D-198; the default command `python -m atlas_schedules`); *Schedule Draw* (`SDraw`) in *1 Program* and the test-suite spec's optional `schedules:` section (each seed a test case, one generator run per test case on the plan's zones, merged zones aggregating the drawn zone schedules). Apartment-unit and composition recipes and mixed slots are refused.
- **Next:** the geometric LOD study: simulation experiments with the runner and the experiment metrics (D-130, D-156), and sourced presets in place of the illustrative ones (D-023), which now means program presets without infiltration and a sourced infiltration on the envelope preset (D-124). Sourced program values now come from the atlas's program JSON through *Program JSON* (D-126).
- **Known limits:** a zone only about 1 m wide on a rotated plan can fail validation after a merging simplifier (D-090); the Yak package server is not used (D-115); the release files go only to the docs repository's GitHub Releases (D-118); the example presets hold illustrative values, not DOE values, the example envelope's 0.3 air changes per hour too, and the `Convert2BEM` layout stays provisional until a ClimateStudio reference exists (D-023); a definition saved before `v1.1.0` opens with Grasshopper's IO dialog and loses its presets' saved infiltration values (D-124); program JSON shared services are not modelled and its design-day profiles are not used (D-126).
- **Pending the owner's reading:** the controller-accepted ADRs and plans the decision log lists as Provisional.
- Until the owner says otherwise, changes need not keep backward compatibility, but component GUIDs never change (D-064).

## Stage workflow

Stages run as D-111 sets out: a short design note in `docs/plans/` written before the build; one test-first build on feature branches in a worktree, independent parts in parallel; a review of the diff by a second agent; the headless Rhino check `scripts/rhino-smoke/` once per stage; `scripts/verify.ps1` before each merge; the fresh-clone gate at tags; one decision-log entry per stage; pushes only with the owner's approval.

Every stage close-out runs the project skill `sync-docs` (`.claude/skills/sync-docs/SKILL.md`, D-115, D-118) and applies or records the edits it lists, so that the developer docs here match the implementation. The skill also says when the public site needs to follow: at a tagged version, run the docs export and build the release files, and the docs repository imports them ([its handover](plans/2026-10-03-docs-site-move/HANDOVER.md)).

## Commands

Run from the repository root on Windows. Any .NET SDK 8 or later works (`global.json` rolls forward); Rhino is not needed to build or test.

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

- `dotnet build` treats warnings as errors, including `.editorconfig` style rules and missing XML documentation in `Lod.Core`.
- `dotnet test` runs every test project on `net8.0`: `Lod.Core.Tests`, `Lod.Generators.Tests`, `Lod.Integration.Tests`, since S6 `Lod.Export.Tests` (the IDF writer, its snapshots, and its parse-back checks), since D-126 `Lod.ProgramJson.Tests` (the program JSON reader and importer), since D-130 `Lod.Simulation.Tests` (the EnergyPlus runner, its parsers, and the experiment metrics), since D-132 `IdfBatchRunner.Tests` (the batch runner on a scripted EnergyPlus), since D-133 `TestSuiteGenerator.Tests` (the test-suite generator), and since D-137 `Lod.ConstructionJson.Tests` (the pinned atlas construction fixtures, release 2.0.0 exports since D-172, and the construction JSON importer). The ground heat-transfer and pilot-suite tests (D-151) also need `BEMGEN_WEATHER_3B`, the path of a climate zone 3B weather file, and are skipped without it. The end-to-end tests that run EnergyPlus are opt-in: they run only when `BEMGEN_ENERGYPLUS` names an installation folder (for example `D:\EnergyPlusV26-2-0`) and are skipped otherwise, so plain `dotnet test` never needs EnergyPlus (GLOBAL.md architecture rule 7). The real schedule draw (`RealDrawTests`, ADR-033) runs only when `BEMGEN_ATLAS_GENERATOR` names an atlas checkout (`BEMGEN_ATLAS_COMMAND` replaces `python -m atlas_schedules`); the other draw tests replay a recorded bundle. One test class: `dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.BuildInfoTests"`.
- `scripts/verify.ps1` is the local merge gate (D-005, no CI): Release build plus all tests. It prints `VERIFY PASSED` and must pass before every merge to `main`. It runs on Windows PowerShell 5.1; `pwsh` is not required.
- `python scripts/idd-check/idd_check.py <Energy+.idd> <file.idf | folder>` checks IDF files against the EnergyPlus IDD, kept outside the repository; with `BEMGEN_IDF_OUT` set, the export tests write every IDF they convert to that folder (`scripts/idd-check/README.md`).
- `dotnet run --project scripts/eplus-check -c Release -- --energyplus <installation folder> --weather <file.epw> <file.idf | folder>` runs EnergyPlus on IDF files, results outside the repository, and fails on any severe or fatal error, a run that did not complete, or a warning not on its list of expected warnings (`scripts/eplus-check/README.md`, D-130).
- `dotnet run --project scripts/IdfBatchRunner -c Release -- --energyplus <installation folder> --weather <file.epw | folder> --root <folder> <file.idf | folder>` runs a batch of IDFs, references first and no site without one, and writes a run folder under the root (or `BEMGEN_RESULTS_ROOT`) outside the repository: `batch.json`, `central.duckdb` (every site's metrics, their definitions, and status, central schema version 7), `hourly/` (one Parquet file per succeeded site with its 20 hourly series), `raw/` (each succeeded site's `eplusout.err`, its whole EnergyPlus folder with `--keep-raw`), and `failure/` (the whole folder of each site that ran and did not succeed); EnergyPlus runs in `work/<site key>` to keep paths short; `--timing-repeats N` adds a serial timing pass for runtime and memory (D-157); `--resume <run folder>` continues an interrupted run from its central database, and `merge --out <folder> <run folders>` combines runs into a folder of the same layout; `--suite <suite folder>` (with `--energyplus`, no `--weather` or inputs) runs a test suite written by `scripts/TestSuiteGenerator` (`scripts/IdfBatchRunner/README.md`, D-132, D-133).
- `dotnet run --project scripts/TestSuiteGenerator -c Release -- <spec.yaml> [--write] --out <folder> --weather-root <folder>` reads a test-suite spec (YAML, version 1), prints the plan with its counts, and with `--write` writes the suite's IDFs, `suite.json`, and `suite.duckdb` into a new folder under `--out` (or `BEMGEN_SUITES_ROOT`) outside the repository; the weather folder is `--weather-root` or `BEMGEN_WEATHER_ROOT`. It writes IDFs only; the batch runner simulates them (`scripts/TestSuiteGenerator/README.md`, D-133). A spec with `schedules:` (ADR-033) runs the schedule generator once per test case: `--schedule-command` (else `BEMGEN_SCHEDULE_COMMAND`, else `python -m atlas_schedules`) in `--schedule-folder` (else `BEMGEN_ATLAS_GENERATOR`).
- The geometric LOD study ([run plan](plans/2026-10-29-lod-study-run-plan.md), D-185, `scripts/lod-study/README.md`): `python -I scripts/lod-study/pin_weather.py` downloads and verifies the pinned weather into `D:\bemgen-weather`, `python -I scripts/lod-study/export_inputs.py --atlas <atlas v2.0.0 checkout>` exports the pinned atlas inputs, `python -I scripts/lod-study/make_specs.py` writes `research/lod-study/specs/`, and `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/lod-study/run.ps1 -Stage <smoke|pilot|main|ht|timing> [-Resume]` generates, runs, merges, and reports a stage outside the repository; the test-suite generator's `--inputs-root <folder>` reads a spec's relative inputs from that folder.
- `python scripts/make_icons.py` redraws the Grasshopper icons into `src/Lod.Grasshopper/Icons/` (Python 3.10+ with Pillow, D-063). Run it after adding a component or parameter class and add a motif for it; it fails when a component or parameter class has no icon.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/rhino-smoke/run.ps1 [-Spec <name>]` runs the headless Rhino 8 smoke check, all specs by default, with results outside the repository (`scripts/rhino-smoke/README.md`).
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-export/export.ps1 -OutDir <folder outside the repository>` writes the docs export for the public site (https://energy-atlas.github.io/BEMGen-docs/): component metadata, screenshots, icons, and the developer pages made from `docs/`, `GLOBAL.md`, and `AGENTS.md`. It needs Rhino 8 (`scripts/docs-export/README.md`, D-118). `python scripts/docs-export/developer_pages.py --check` checks the developer pages' links without Rhino.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/package-release.ps1` builds a version's release files into `dist/release/<version>/` (git-ignored): the plugin zip, the `.yak` (from `scripts/package-yak.ps1`, which builds into `dist/yak/`), the examples zip, and checksums. Neither script publishes anything (D-115, D-118).

Tests for `Lod.Core`, `Lod.Generators`, `Lod.Export`, and `Lod.Simulation` must run with plain `dotnet test`, without Rhino, Grasshopper, or EnergyPlus installed.

## Architecture boundaries

| Project | May depend on | Must not depend on |
| --- | --- | --- |
| `Lod.Core` | BCL and Clipper2 (polygon clipping, from S2; ADR-001, ADR-002) | RhinoCommon, Grasshopper, UI, exporters |
| `Lod.Generators` | `Lod.Core` | Grasshopper |
| `Lod.Export` (`Convert2IDF`, S6) | `Lod.Core` | RhinoCommon, Grasshopper |
| `Lod.ProgramJson` (*Program JSON*, D-126; the schedule draw, ADR-033, which runs the atlas generator as an external process behind `IScheduleGenerator`) | `Lod.Core`, JsonSchema.Net | RhinoCommon, Grasshopper |
| `Lod.ConstructionJson` (the atlas construction JSON, D-137) | `Lod.Core`, `Lod.ProgramJson` (its strict reader and embedded schema), JsonSchema.Net | RhinoCommon, Grasshopper |
| `Lod.Simulation` (EnergyPlus runner and experiment metrics, D-130) | `Lod.Core` | RhinoCommon, Grasshopper, `Lod.Export`, the pipeline services |
| `scripts/IdfBatchRunner` (batch runner, D-132; a tool, not released) | `Lod.Simulation`, DuckDB.NET | RhinoCommon, Grasshopper, `Lod.Export`, the pipeline services |
| `scripts/TestSuiteGenerator` (test-suite generator, D-133; a tool, not released) | `Lod.Core`, `Lod.Generators`, `Lod.ProgramJson`, `Lod.ConstructionJson`, `Lod.Export`, YamlDotNet, JsonSchema.Net, DuckDB.NET | RhinoCommon, Grasshopper |
| `Lod.Grasshopper` | everything above, RhinoCommon, Grasshopper | — |

- Grasshopper components are thin adaptors: read inputs, call a service, convert results and diagnostics to outputs and runtime messages. No domain logic in component classes.
- The pipeline (D-018) is: program presets → `PlanGenerator` (e.g. `LinearPlanGenerator`) → `IGeneratedPlan` → `IPlanSimplifier` → `IFloor` → `IFloorAggregator` → `IGeneratedBuilding` → `Convert2BEM` (ClimateStudio-ready Grasshopper output) / `Convert2IDF`.
- Keep plan generation, plan simplification, floor aggregation, equivalent-property aggregation (`IEquivalentPropertyAggregator`), validation, and conversion as separate services. Never build a component that does generate + simplify + aggregate + convert in one step.
- Pipeline objects are plain C# types in `Lod.Core`; Grasshopper Goo wrappers carry them between components. Output is Grasshopper objects, not JSON (D-017).
- Use typed parameter records per typology, not dictionaries or one catch-all parameter class.
- Semantics are explicit data (`SemanticType`, `ProgramGroup`, ...), never encoded in layer names, colors, or wire structure.

## Working rules

1. Read `GLOBAL.md`, `README.md`, and the relevant `docs/` before modifying architecture.
2. Inspect existing patterns before introducing a new abstraction; extend an existing pattern rather than duplicating it.
3. Preserve the separation between domain logic and Grasshopper UI.
4. Add or update tests for every behavioral change. Core transformations are written test-first.
5. Run the relevant test suite before declaring a task done, and report the actual result.
6. Update documentation in the same change when altering pipeline types, public APIs, or component inputs/outputs; never change a merged component's GUID.
7. Do not modify files unrelated to the task.
8. Never commit generated binaries, caches, simulation outputs, or user-specific IDE state.
9. Preserve deterministic behavior: explicit seeds, no global random state, stable ordering of outputs.
10. Surface assumptions explicitly, in code comments, ADRs, or the change description.
11. Never fabricate test results, simulation numbers, or validation outcomes.
12. Never silently relax a validation invariant or widen a tolerance to make a test pass.
13. Never alter research equivalence rules without updating the research documentation.
14. Define numerical tolerances only in the central tolerance configuration.
15. Never include an agent name, model name, provider, model version, tool branding, or attribution footer/trailer in commit messages.

## Testing expectations

- **Unit tests:** schedule aggregation, load conservation, area weighting, transfer matrices, tolerances, semantic grouping, WWR, parameter validation.
- **Invariant tests:** target area ≈ source area; installed and per-timestep scheduled load conserved; occupancy conserved; window area conserved at the level the W-level requires; mapping fractions sum to one; no negative areas.
- **Golden tests:** small, human-inspectable text snapshots of pipeline results for each typology, simplifier, and floor aggregator, stored under `tests/**/Snapshots/`.
- **Integration tests:** program presets → plan generator → plan simplifier → floor aggregator → validation, without Grasshopper.
- Guard every weighted average against a zero denominator and test that case.

## Code style

Enforced by `.editorconfig`. Summary: nullable reference types on, file-scoped namespaces, explicit access modifiers, `PascalCase` types/members, `camelCase` locals/parameters, `_camelCase` private fields, `I`-prefixed interfaces, `Async`-suffixed async methods, immutable records where practical, composition over inheritance, dependency injection for external services, no static service locators, no magic strings, no reflection without strong justification. XML doc comments on public APIs and non-obvious algorithms; no comments that restate the code.

## Commits

Format:

```text
type(scope): imperative summary in lower case
```

Types:

| Type | Use for |
| --- | --- |
| `feature` | new behavior or capability |
| `fix` | bug fix |
| `refactor` | restructuring without behavior change |
| `test` | adding or changing tests only |
| `docs` | documentation only |
| `build` | solution, project files, packaging, CI |
| `chore` | repository maintenance (ignores, config, tooling) |
| `perf` | performance change without behavior change |

Scope is the area touched, e.g. `core`, `programs`, `generators`, `simplifiers`, `aggregators`, `mapping`, `loads`, `schedules`, `windows`, `validation`, `convert`, `grasshopper`, `research`, `repo`.

Examples:

```text
feature(simplifiers): add perimeter-core plan simplifier
fix(schedules): preserve equipment schedules during zone aggregation
test(generators): add courtyard block determinism tests
feature(aggregators): add floor area multiplier aggregator
feature(validation): check orientation-level window area
```

Keep commits focused. Describe only the code or documentation change. No personal signatures, AI/tool attribution, or `Co-Authored-By` trailers for tools. This format supersedes the plain-sentence examples in the repository spec §25.

## Change descriptions

A change to transformation logic states: the behavior changed, tests added or updated, invariant impact, pipeline-type or component interface impact, documentation impact, and a before/after example when useful. A change that alters scientific behavior is not complete until that behavior is documented and equivalence is demonstrated numerically.

## Definition of done

Implementation present; tests cover the behavior; relevant invariants pass; public API and component interface changes documented; Grasshopper behavior deterministic; no unrelated files modified; the rules in `GLOBAL.md` respected.

## Research continuation status (2026-10-28)

D-179/[ADR-030](decisions/ADR-030-spatial-program-signatures-and-volume-ledgers.md): the opt-in floor gate now checks spatial program signatures and configured hourly heat partitions. The generic source/derived ledger API preserves unknowns and explicit departures; populated authenticated DOE ledgers and exact/vertical equivalence remain separate work. Production behavior and tolerances are unchanged. See [usage](research/reference-program-contract.md).

When engine execution is outside the authorized task, use the software-only launcher (`scripts/software-only/README.md`), `scripts/verify-software-only.ps1`, instead of the inherited-environment `verify.ps1`. It removes process-local engine/weather opt-ins, rejects engine categories, fixes exclusions and refuses reviewed-source drift. Never treat an inherited installation variable as authorization for engine tests. During the guard-only increment, run only its harmless fake-runner regressions; the default real runner is intentionally unexecuted.

D-182/[ADR-031](decisions/ADR-031-exact-composition-identity-preflight.md) adds an explicit default-off backend identity screen over one registered floor. Supported geometry/program preservation is separate from production baseline and full eligibility. Missing ownership/construction is Unavailable; full exact-composition eligibility remains false. No composer, placement-registration engine, production acceptance change or energy equivalence is established. Stage-six actual tests use an inspected narrow guard adapter, with positive selectors AND fixed exclusions and explicit reviewed-source policy refresh; this does not establish that the default full-solution runner has been exercised.

D-183 combines the saved research chain and complete DOE geometry branch on a separate integration branch. Skylight identity is checked on registered ceiling hosts; configured program-input preservation does not certify source program-key semantics. See [the integration plan](plans/2026-10-28-main-research-doe-integration.md). Keep engine/weather opt-ins process-locally absent and review the combined executable/build inventory before refreshing the software-only policy. Native and scientific validation remain separate.
