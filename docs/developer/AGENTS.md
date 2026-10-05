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

- **Done:** S0–S9, tags `v0.0.1` to `v0.9.1` (S6 is `v0.9.0`, D-113; the zero-width fix is `v0.9.1`, D-114), `v1.0.0` for S9 (D-116), `v1.0.1`, which moved the docs site to the public repository `energy-atlas/BEMGen-docs` (D-117 to D-119), and `v1.0.2`, which adds the enum inputs' right-click values and dropdown (D-120, D-121). The pipeline (program presets → plan generator → plan simplifier → floor aggregator → validation → `Convert2BEM` or `Convert2IDF`, [docs/architecture/pipeline.md](architecture/pipeline.md)) runs end to end in Rhino 8 for 18 plan generators, one per family of the four-source precedent set except the set-aside `SYN-TYP-013` ([syn-typologies.md](research/precedents/syn-typologies.md), D-093, D-096), housing and non-residential ([ADR-006](decisions/ADR-006-plan-generation-mechanism.md), [ADR-014](decisions/ADR-014-program-types-and-department-zoning.md), [ADR-015](decisions/ADR-015-plans-per-storey.md)).
- **Next:** the first EnergyPlus run once a weather file and outputs are chosen (D-112), and sourced presets in place of the illustrative ones (D-023).
- **Known limits:** a zone only about 1 m wide on a rotated plan can fail validation after a merging simplifier (D-090); the Yak package server is not used (D-115); the release files go only to the docs repository's GitHub Releases (D-118); the example presets hold illustrative values, not DOE values, and the `Convert2BEM` layout stays provisional until a ClimateStudio reference exists (D-023).
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
- `dotnet test` runs every test project on `net8.0`: `Lod.Core.Tests`, `Lod.Generators.Tests`, `Lod.Integration.Tests`, and since S6 `Lod.Export.Tests` (the IDF writer, its snapshots, and its parse-back checks). One test class: `dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.BuildInfoTests"`.
- `scripts/verify.ps1` is the local merge gate (D-005, no CI): Release build plus all tests. It prints `VERIFY PASSED` and must pass before every merge to `main`. It runs on Windows PowerShell 5.1; `pwsh` is not required.
- `python scripts/idd-check/idd_check.py <Energy+.idd> <file.idf | folder>` checks IDF files against the EnergyPlus IDD, kept outside the repository; with `BEMGEN_IDF_OUT` set, the export tests write every IDF they convert to that folder (`scripts/idd-check/README.md`).
- `python scripts/make_icons.py` redraws the Grasshopper icons into `src/Lod.Grasshopper/Icons/` (Python 3.10+ with Pillow, D-063). Run it after adding a component or parameter class and add a motif for it; it fails when a component or parameter class has no icon.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/rhino-smoke/run.ps1 [-Spec <name>]` runs the headless Rhino 8 smoke check, all specs by default, with results outside the repository (`scripts/rhino-smoke/README.md`).
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-export/export.ps1 -OutDir <folder outside the repository>` writes the docs export for the public site (https://energy-atlas.github.io/BEMGen-docs/): component metadata, screenshots, icons, and the developer pages made from `docs/`, `GLOBAL.md`, and `AGENTS.md`. It needs Rhino 8 (`scripts/docs-export/README.md`, D-118). `python scripts/docs-export/developer_pages.py --check` checks the developer pages' links without Rhino.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/package-release.ps1` builds a version's release files into `dist/release/<version>/` (git-ignored): the plugin zip, the `.yak` (from `scripts/package-yak.ps1`, which builds into `dist/yak/`), the examples zip, and checksums. Neither script publishes anything (D-115, D-118).

Tests for `Lod.Core`, `Lod.Generators`, and `Lod.Export` must run with plain `dotnet test`, without Rhino or Grasshopper installed.

## Architecture boundaries

| Project | May depend on | Must not depend on |
| --- | --- | --- |
| `Lod.Core` | BCL and Clipper2 (polygon clipping, from S2; ADR-001, ADR-002) | RhinoCommon, Grasshopper, UI, exporters |
| `Lod.Generators` | `Lod.Core` | Grasshopper |
| `Lod.Export` (`Convert2IDF`, S6) | `Lod.Core` | RhinoCommon, Grasshopper |
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
