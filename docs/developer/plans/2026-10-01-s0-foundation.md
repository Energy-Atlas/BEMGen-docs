# S0 — Foundation Implementation Plan

> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S0](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A building, testable .NET solution with a Grasshopper plugin that loads in Rhino 8.19 or later on its default .NET Core runtime and reports its version, plus the accepted foundation ADRs (ADR-001 to ADR-005, ADR-007) and the research-brief updates every later stage relies on.

**Architecture:** `Lod.Core` (`netstandard2.0`, no Rhino reference) holds domain code; in S0 it only exposes `BuildInfo`, the version string with commit SHA. `Lod.Grasshopper` (`net7.0` only, output one `BEMGen.gha` for Rhino 8's default .NET Core runtime) is a thin plugin shell with one *BEMGen Info* component that reads `BuildInfo`. `tests/Lod.Core.Tests` runs on `net8.0` only, and `scripts/verify.ps1` is the local merge gate (no CI, D-005).

**Tech Stack:** C# 12 (`LangVersion` 12.0) · .NET SDK 8.0.100 or later via `global.json` (`rollForward: latestMajor`; the code was verified with SDK 10.0.x) · `Lod.Core` on `netstandard2.0` · `Lod.Grasshopper` on `net7.0` against RhinoCommon 8.19.25132.1001 and Grasshopper 8.19.25132.1001 (compile-only) · tests on `net8.0` with xunit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1 · Clipper2 2.0.0 pinned in central package management but first referenced in S2 · Windows PowerShell 5.1 for `scripts/verify.ps1`.

## Global Constraints

- Before Task 1, this plan is reviewed and committed to `main` (`docs(plans): add s0 foundation plan`); tasks are executed in order.
- Rhino 8 only (D-003); minimum supported Rhino is 8.19 (ADR-001).
- Target frameworks (ADR-001, D-053): core libraries `netstandard2.0`, the plugin `net7.0` only (Rhino 8's default .NET Core runtime, which runs it on .NET 8), test projects `net8.0` only. There is no second plugin build for another Rhino runtime.
- `Lod.Core` has no RhinoCommon or Grasshopper reference; its tests run with plain `dotnet test`, without Rhino.
- Nullable reference types enabled; warnings are errors in every project, including `.editorconfig` style rules (`EnforceCodeStyleInBuild`) and missing XML docs in `Lod.Core` (CS1591).
- Every code block in this plan is copied verbatim: no renaming, reformatting, or reordering.
- Grasshopper GUIDs in this plan are fixed literals and never change once merged (GLOBAL.md quality rule 2).
- No CI (D-005). From Slice B on, `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` must print `VERIFY PASSED` before any merge to `main`. `pwsh` is not installed and not required.
- Branches are short-lived and integrated by rebase and fast-forward merge only; no merge commits, no force push to `main` (D-004).
- Commit messages: `type(scope): imperative summary in lower case`; no `Co-Authored-By`, no "Generated with", no agent, model, or tool names, no attribution of any kind (D-001, D-002, AGENTS.md rule 15).
- Research equivalence rules change only together with the research brief (GLOBAL.md scientific rule 7): Tasks 5 to 7 edit `docs/LOD_geometric_zoning_equivalence_research_brief.md` in the same commit as the rule.
- Generated build output (`bin/`, `obj/`) is never committed; the existing `.gitignore` already excludes it.
- Steps marked **manual (person)** need Rhino 8 and a person at the keyboard; an agent stops there and asks the person to perform them and report the observed values.
- Commands run from the repository root on Windows. NuGet restore needs network access to nuget.org the first time.

## Files

| Path | Created / modified | Responsibility |
| --- | --- | --- |
| `docs/decisions/ADR-001-toolchain.md` | Created (Task 1) | SDK, frameworks, packages, plugin build, GUID policy, verification gate |
| `docs/decisions/ADR-002-geometry.md` | Created (Task 2) | 2.5D geometry, polygons, zones, walls, explicit windows and their re-hosting, Clipper2, Rhino boundary |
| `docs/decisions/ADR-003-schedules.md` | Created (Task 3) | 8760-hour schedules, kinds, profiles, aggregation records |
| `docs/decisions/ADR-004-tolerances.md` | Created (Task 4) | `ToleranceSettings` values, comparison rule, overrides |
| `docs/decisions/ADR-005-conditioning-and-setpoints.md` | Created (Task 5) | Conditioning from presets and setpoint aggregation (D-038) |
| `docs/decisions/ADR-007-load-basis-aggregation.md` | Created (Task 6) | Unified magnitude rule for all load bases, applied per load type and basis (D-019, D-041, D-047) |
| `docs/LOD_geometric_zoning_equivalence_research_brief.md` | Modified (Tasks 5, 6, 7) | "Rule adopted for this project" paragraphs in §7, §9, §10 |
| `tests/Lod.Core.Tests/Lod.Core.Tests.csproj` | Created (Task 8) | Core test project, `net8.0` |
| `tests/Lod.Core.Tests/Common/BuildInfoTests.cs` | Created (Task 8) | Smoke test of `BuildInfo` |
| `global.json` | Created (Task 8) | SDK pin with roll-forward |
| `Directory.Build.props` | Created (Task 8) | Shared build properties, version, polyfill link |
| `Directory.Packages.props` | Created (Task 8) | Central package versions |
| `src/Shared/IsExternalInit.cs` | Created (Task 8) | Polyfill for records and `init` on `netstandard2.0` |
| `src/Lod.Core/Lod.Core.csproj` | Created (Task 8) | Core library project (S0 version: no package references) |
| `src/Lod.Core/Common/BuildInfo.cs` | Created (Task 8) | Informational version with commit SHA |
| `BEMGen.sln` | Created by `dotnet new sln` (Task 8), modified by `dotnet sln add` (Task 10) | Solution |
| `scripts/verify.ps1` | Created (Task 9) | Local build + test gate |
| `AGENTS.md` | Modified (Tasks 9, 12) | "Project state" and "Commands" |
| `src/Lod.Grasshopper/Lod.Grasshopper.csproj` | Created (Task 10) | Plugin project, `BEMGen.gha` for `net7.0` |
| `src/Lod.Grasshopper/BemGenAssemblyInfo.cs` | Created (Task 10) | Grasshopper plugin metadata and plugin GUID |
| `src/Lod.Grasshopper/ComponentCategories.cs` | Created (Task 10) | Toolbar tab and panel names for all stages |
| `src/Lod.Grasshopper/Components/BemGenInfoComponent.cs` | Created (Task 10) | *BEMGen Info* component |
| `src/Lod.Grasshopper/Properties/launchSettings.json` | Created (Task 10) | Launch profile that starts Rhino 8 with Grasshopper and the build loaded (D-052, D-053) |
| `docs/development/grasshopper-smoke-test.md` | Created (Task 11) | Manual Rhino smoke test and per-stage checklists |
| `README.md` | Modified (Task 12) | "Status" |
| `docs/plans/2026-09-30-implementation-roadmap.md` | Modified (Task 12) | Dated progress line |
| `docs/decisions/decision-log.md` | Modified (Task 12) | D-042 (foundation ADRs accepted) |
| `docs/plans/2026-10-01-s0-foundation.md` | Modified (Task 12) | This plan's status set to Done |

---

## Slice A — `docs/decisions-foundation-adrs`

Documentation only: six ADRs and three research-brief edits, one commit per task. `scripts/verify.ps1` does not exist yet, so the merge at the end of this slice checks the diff instead of running the gate.

### Task 1: ADR-001 Toolchain

**Files:** Create `docs/decisions/ADR-001-toolchain.md`
**Interfaces:** Consumes: D-003, D-004, D-005. / Produces: the toolchain that Tasks 8 to 10 implement; referenced by `AGENTS.md` (Task 9) and D-042 (Task 12).

- [x] **Step 1: Create the slice branch**

```bash
git switch main
git pull --ff-only
git switch -c docs/decisions-foundation-adrs main
```

Expected: `Switched to a new branch 'docs/decisions-foundation-adrs'`.

- [x] **Step 2: Write `docs/decisions/ADR-001-toolchain.md`**

````markdown
# ADR-001: Toolchain

Status: Accepted

Date: 2026-10-01

Decisions: D-003, D-004, D-005, D-053

## Context

BEMGen is a Grasshopper plugin for Rhino 8 only (D-003). Its domain logic lives in plain C# libraries that must build and test with `dotnet test` on a machine without Rhino (AGENTS.md; GLOBAL.md architecture rules 1 and 2). There is no CI (D-005): a local script is the only gate before a rebase merge to `main` (D-004). Roadmap v1 and v2 proposed a toolchain to be ratified here: C# with the latest language version, .NET SDK 8, `netstandard2.0` core libraries, the RhinoCommon and Grasshopper NuGet packages, Clipper2, System.Collections.Immutable, and xUnit. Roadmap v3 already reflects the decision below.

Facts that constrain the choice, established while setting up the solution:

- Rhino 8 runs plugins on the .NET 8 runtime by default (.NET Core mode; Rhino's runtime configuration targets `net7.0` and runs on framework 8.0.0). The `SetDotNetRuntime` command switches Rhino to .NET Framework 4.8, where plugins must be `net48` assemblies.
- The RhinoCommon and Grasshopper NuGet packages contain `net7.0` assemblies only from version 8.19.25132.1001 on.
- `net7.0` is end-of-life for current .NET SDKs, which report warning NETSDK1138 for projects targeting it.
- The `net7.0` Grasshopper package brings a Windows Forms (Windows desktop) framework reference.
- Rhino 8 ships its own `System.Collections.Immutable.dll`, `System.Memory.dll`, and `System.Text.Json.dll` for .NET Framework mode; in .NET Core mode the .NET 8 shared framework provides them. A plugin that depends on other versions of these assemblies risks version conflicts inside Rhino.
- A `net7.0` project cannot reference a `net8.0` library.
- An S0 build of the plugin passed the manual smoke test in Rhino's default .NET Core runtime (D-053).
- The development machine has .NET SDK 10.0.x only (no SDK 8), the .NET 8 runtime, .NET Framework 4.8, and Windows PowerShell 5.1; PowerShell 7 (`pwsh`) is not installed.
- `netstandard2.0` lacks `System.Runtime.CompilerServices.IsExternalInit`, which the C# compiler needs for records and `init` accessors.

## Options considered

### Target framework of the core libraries

1. **`netstandard2.0` with an `IsExternalInit` polyfill.** One binary serves the `net7.0` plugin in Rhino and the `net8.0` test host. Costs: no language features that need runtime support and no BCL APIs newer than .NET Standard 2.0.
2. **`net8.0`.** Newer APIs and no polyfill, but the `net7.0` plugin cannot reference a `net8.0` library.
3. **`net7.0`.** Newer APIs, but every core library then carries an end-of-life target framework and must suppress NETSDK1138, and the core needs no API that `netstandard2.0` lacks.

### Immutable collections

1. **System.Collections.Immutable.** Convenient immutable types, but an extra package whose version has to match the copy already loaded in Rhino's process.
2. **`IReadOnlyList<T>` over private arrays (`Array.AsReadOnly`).** No dependency. Immutability comes from encapsulation: a type copies its inputs into a private array and never exposes the array.

### RhinoCommon and Grasshopper package version

1. **The latest Rhino 8 packages.** Raises the minimum Rhino version to whatever release was current at build time, without a feature that needs it.
2. **8.19.25132.1001, the first release with `net7.0` assemblies.** The lowest version a `net7.0` plugin can compile against; minimum supported Rhino 8.19.

### C# language version

1. **`latest`** (the proposal in roadmap v1 and v2). The language version then depends on the installed SDK (C# 14 on SDK 10, C# 12 on SDK 8), so code that compiles on one machine can fail on another.
2. **`12.0`**, the highest version SDK 8 supports. The same language on every SDK from 8 up.

### Plugin target frameworks

1. **`net48` only.** Loads only in .NET Framework mode, not in Rhino's default runtime.
2. **`net7.0` only.** Loads only in the default .NET Core mode. One build, one test framework, and one manual check per stage.
3. **`net7.0;net48`.** One `.gha` per runtime from the same sources. Rhino sessions in either mode can load BEMGen, but every build, test run, and manual smoke test is doubled.

### Verification gate

1. **A CI service.** Rejected by D-005.
2. **A local script on Windows PowerShell 5.1.** Present on every Windows machine; the `pwsh scripts/verify.ps1` example in roadmap v1 and v2 would require installing PowerShell 7.

## Decision

**SDK and language.** `global.json` pins SDK `8.0.100` with `rollForward: latestMajor`, so any .NET SDK 8 or later builds the solution. `Directory.Build.props` sets `LangVersion` 12.0 for every project. The solution is a classic `BEMGen.sln`: `dotnet new sln --name BEMGen --format sln` on SDK 9.0.200 or later; on SDK 8 the `--format` option does not exist and `.sln` is the default.

**Build properties** (`Directory.Build.props`, all projects): `Nullable` enabled, `ImplicitUsings` disabled, `TreatWarningsAsErrors`, `EnforceCodeStyleInBuild` (so `.editorconfig` rules at warning severity are build errors), `Deterministic`, `Version` (0.0.1 in S0, raised at each stage close-out), `Authors`, and `Product`. `Lod.Core`, and `Lod.Generators` once it exists (S2), set `GenerateDocumentationFile`, so a public member without XML documentation is a build error (CS1591).

**Version with commit.** The .NET SDK's built-in Source Link appends `+` and the full commit SHA to the assembly informational version when building from a git checkout, for example `0.0.1+` followed by 40 hexadecimal characters. `Lod.Core.Common.BuildInfo.InformationalVersion` exposes this string; the *BEMGen Info* component shows it, and provenance records it from S2 on.

**Core libraries** (`Lod.Core`, `Lod.Generators`, `Lod.Export`) target `netstandard2.0`. `src/Shared/IsExternalInit.cs` defines the polyfill once, and `Directory.Build.props` links it into every build whose target framework is not .NET Core (that is, `netstandard2.0`), so records and `init` accessors work everywhere. `netstandard2.0` is chosen because the `net7.0` plugin cannot reference a `net8.0` library, because it keeps the end-of-life `net7.0` off the core libraries, and because one core binary serves both the plugin and the `net8.0` tests.

**No System.Collections.Immutable.** Collections exposed by core types are `IReadOnlyList<T>` (or another read-only interface) over private arrays wrapped with `Array.AsReadOnly`.

**Plugin.** `Lod.Grasshopper` targets `net7.0` only and produces one `BEMGen.gha` for Rhino 8's default .NET Core runtime, which runs it on .NET 8 (`AssemblyName` BEMGen, `TargetExt` .gha, `EnableDynamicLoading` true). It references RhinoCommon and Grasshopper 8.19.25132.1001 with `ExcludeAssets="runtime"`: the plugin compiles against Rhino's assemblies, but they are never copied to the output, because Rhino supplies them at load time. `CheckEolTargetFramework` is false in this project only, because NETSDK1138 for `net7.0` would otherwise be a build error. The minimum supported Rhino version is 8.19.

`net7.0;net48` was considered and rejected (D-053): Rhino 8's default runtime is .NET Core, the S0 smoke test passed there, and a second runtime doubles builds, test runs, and manual checks. A Rhino switched to .NET Framework with `SetDotNetRuntime` cannot load BEMGen.

**Packages.** Central package management (`Directory.Packages.props` with `ManagePackageVersionsCentrally`) holds exact versions; project files reference packages without versions. A version change is a `build` commit of its own, made after `scripts/verify.ps1` passes.

| Package | Version | Used by |
| --- | --- | --- |
| RhinoCommon | 8.19.25132.1001 | `Lod.Grasshopper`, compile only |
| Grasshopper | 8.19.25132.1001 | `Lod.Grasshopper`, compile only |
| Clipper2 | 2.0.0 | `Lod.Core` from S2 on, for polygon boolean operations (ADR-002); Boost Software License 1.0, `netstandard2.0`, no dependencies |
| xunit | 2.9.3 | test projects |
| xunit.runner.visualstudio | 3.1.5 | test projects |
| Microsoft.NET.Test.Sdk | 17.14.1 | test projects |

Clipper2's version is pinned from S0 on; no project references it before S2.

**Tests.** xUnit. Test projects target `net8.0` only, so every test runs on the .NET 8 runtime that Rhino uses by default.

**Component GUIDs.** The plugin's `GH_AssemblyInfo.Id` and every component's `ComponentGuid` are literal GUIDs in the source. A GUID never changes once merged to `main` (GLOBAL.md quality rule 2), because saved Grasshopper definitions refer to components by GUID. A new component gets a newly generated GUID; the GUID of a removed component is never reused. The plugin GUID is `6f0f5d0e-2a8b-4c55-9a51-0a7b3d2c9e41`.

**Naming.** Grasshopper wrapper (Goo) classes do not use the `GH_` prefix of Grasshopper's own types, because the `.editorconfig` PascalCase naming rule, enforced in the build, rejects it.

**Verification gate.** `scripts/verify.ps1` builds `BEMGen.sln` in Release with warnings as errors and runs every test project on `net8.0`; it prints `VERIFY PASSED`, or stops with a non-zero exit code. It runs on Windows PowerShell 5.1:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

It must pass before every merge to `main` (D-004, D-005). The roadmap's merge procedure (§3) uses this command.

## Consequences

- One `Lod.Core.dll` serves the plugin in Rhino and the `net8.0` tests.
- BEMGen loads only in Rhino's default .NET Core runtime. A Rhino session switched to .NET Framework, for example for another plugin that needs it, cannot use BEMGen. If a downstream plugin such as ClimateStudio needs .NET Framework mode, this decision is revisited.
- Core code cannot use language features that need runtime support or polyfills other than `IsExternalInit`, such as default interface implementations, static abstract interface members, and `required` members. Multi-targeting stays available if a real need appears (roadmap risk table).
- Core types copy their inputs into private arrays, so callers cannot mutate them, and no immutable-collection package can conflict with Rhino's.
- Rhino 8.0 to 8.18 are not supported.
- The solution is built and tested on Windows; the `net7.0` plugin needs the Windows desktop framework reference.
- The plugin output folder contains `BEMGen.gha`, `Lod.Core.dll`, their `.pdb` files, `Lod.Core.xml`, `BEMGen.deps.json`, and `BEMGen.runtimeconfig.json`; it never contains `RhinoCommon.dll` or `Grasshopper.dll`.
- `net7.0` remains the plugin target only because RhinoCommon 8 ships `net7.0` assemblies. If a later Rhino version changes its plugin target framework, a new ADR revisits this one.
- Every build carries its commit SHA, so provenance and the *BEMGen Info* component identify the exact code (roadmap §3, reproducibility).
- Without CI, `main` stays healthy only if `scripts/verify.ps1` passes before every merge; linear history (D-004) keeps bisecting simple.
````

- [x] **Step 3: Check that only the new ADR changed**

```bash
git status --short
```

Expected: `?? docs/decisions/ADR-001-toolchain.md`

- [x] **Step 4: Commit**

```bash
git add docs/decisions/ADR-001-toolchain.md
git commit -m "docs(decisions): add adr-001 toolchain"
```

### Task 2: ADR-002 Geometry representation

**Files:** Create `docs/decisions/ADR-002-geometry.md`
**Interfaces:** Consumes: D-009, D-021, D-026, D-039; ADR-001 (Clipper2). / Produces: the geometry model that S2 implements (`Polygon2`, `ZonePart`, `WallSurface` with its `Windows`, `HorizontalSurface`, `Window.At`, `Window.Centered`, `PolygonOps`, `Orientation`) and the re-hosting rule that S3 implements (`WindowRehosting`, error `WindowNotHosted`); referenced by ADR-004 and research brief §10.

- [x] **Step 1: Write `docs/decisions/ADR-002-geometry.md`**

````markdown
# ADR-002: Geometry representation

Status: Accepted

Date: 2026-10-01

Decisions: D-009, D-021, D-026, D-039

## Context

The pipeline (D-018) produces plans, floors, and buildings whose zones, surfaces, and windows feed `Convert2BEM` and later `Convert2IDF` (S6). The core libraries cannot use Rhino geometry (GLOBAL.md architecture rules 1, 2, and 4), yet they must compute floor areas, volumes, wall areas, orientations, adjacencies, and source-target overlaps precisely enough for the conservation checks (ADR-004). Residential plans in this study are storeys of constant height with vertical walls. Zones stop at the dwelling unit (D-009), and `SingleZoneMerged` turns the whole building into one zone (D-021). Window representation is an experimental axis of its own (research brief §10, levels W0 to W5), independent of zoning: walls carry explicit windows (D-039), the first plan generator places them from the program preset's window-to-wall ratio (WWR, D-026), and window transformations are a later stage (S5).

## Options considered

### Dimensionality

1. **A full 3D boundary representation in the core.** General, but it needs a geometry kernel: RhinoCommon is not allowed in the core, and a custom 3D kernel is far beyond what the study needs.
2. **2.5D: plan polygons with elevations and heights.** Exact areas and volumes from polygon formulas; covers extruded storeys with vertical walls. Cannot represent sloped roofs, non-vertical walls, or curved surfaces.

### Window representation

1. **Centered windows only, at every LoD** (the former D-022, with the glazing rule of the former D-025): one centered window per exterior wall, sized from the WWR at Z0 and from the inherited façade glazing at simplified levels. One number per wall fixes size and position. Rejected by D-039 because it removes the window-LoD axis: the window representation would be fixed by the rule, and every simplified zoning level would also redistribute the glazing, so window and zoning effects could not be separated.
2. **A glazing quantity per wall (area or WWR) without window geometry.** Enough for area conservation, but it cannot express the window positions that W0 keeps, and converters need window geometry.
3. **Explicit windows:** each window has an offset along its wall, a sill height, a width, and a height, and a wall may carry any number. Supports W0 at every zoning level and leaves W1 to W5 to explicit transformations.

### Window placement rule of the first plan generator

1. **A full-width strip with height WWR × wall height.** Always fits, but its proportions differ from the wall's and it touches both wall ends.
2. **The wall rectangle scaled about its centre by √(glazed area / wall area).** One number fixes size and position, the window keeps the wall's proportions, and it lies strictly inside the wall for any WWR below 1.

### Polygon boolean operations

1. **An own implementation.** High risk in degenerate cases.
2. **RhinoCommon curve booleans.** Not allowed in the core.
3. **Clipper2** (`ClipperD` on `PathsD`, double coordinates rounded to a fixed number of decimals). Mature, managed, `netstandard2.0`, no dependencies.

### Matching the shared edges of adjacent zones

1. **Exact floating-point equality.** Fails for coordinates that differ in the last bits.
2. **Snapping vertices to the distance-tolerance grid.** Shared edges match exactly after snapping, and the grid is the same as the Clipper2 precision.

## Decision

**2.5D model in metres.** Plans live in a building-local XY frame in metres; +Y is plan north. A plan stores its orientation as the clockwise rotation of plan north from true north, in degrees.

**Polygons.** `Polygon2` is an immutable polygon with holes. The outer ring is counter-clockwise, holes are clockwise, and rings are stored open (the first point is not repeated). Construction normalises ring orientation, drops repeated consecutive points, and rejects rings with fewer than three distinct points or zero area, as well as polygons whose holes cover the outer ring. The area is the outer ring's area minus the holes' areas.

**Zones.** A zone is one or more prisms, `ZonePart(Footprint, Elevation, Height)`, each with volume = footprint area × height. Only `SingleZoneMerged` (D-021) creates zones with several parts, one per storey; every other zone has exactly one part. A zone's floor area and volume are the sums over its parts.

**Walls.** Walls are vertical rectangles generated from polygon edges. A wall runs from `Start` to `End` with its zone on the left, has a bottom elevation and a height, and its area is length × height. Its outward azimuth is measured in degrees clockwise from north, in [0°, 360°). The azimuth is computed in the plan frame (plan azimuth) and becomes a true azimuth by adding the plan orientation. Orientation bins are applied to the true azimuth:

| Bin | Azimuth |
| --- | --- |
| North | [315°, 45°) |
| East | [45°, 135°) |
| South | [135°, 225°) |
| West | [225°, 315°) |

**Floors and ceilings** are horizontal polygons at an elevation. Every surface has a boundary condition: outdoors, ground, adiabatic, interzone (naming the adjacent zone), or unresolved (the floors and ceilings of a plan or floor before floors are stacked).

**Windows (D-039).** A window is an explicit rectangle in its wall, given by its `Offset` (the distance along the wall from the wall's start point to the window's near edge), its `SillHeight` above the wall's bottom edge, its `Width`, and its `Height`, all in metres. Offsets and sill heights are not negative; widths and heights are positive. A wall carries any number of windows, ordered by offset, and its glazed area is the sum of their areas. The operations that create or re-host windows keep every window within its wall.

**Placement rule of the first plan generator.** The S2 plan generator places one centered window on each outdoor wall (`Window.Centered`). For glazed area `A_g = WWR × A_w` (D-026) on a wall of length `L`, height `H`, and area `A_w = L × H`, the window is the wall rectangle scaled about its centre by `k = √(A_g / A_w)`: width `k × L`, height `k × H`, offset `(L − k × L) / 2`, and sill height `(H − k × H) / 2`. `A_g = 0` gives no window; `A_g < 0` or `A_g ≥ A_w` is an error. This is that generator's placement rule, not a property of windows; generators derived from the precedent study (S7, S8) may place windows differently.

**Windows through simplification (W0).** Plan simplifiers and `SingleZoneMerged` keep every source window unchanged. Each window of a source outdoor wall is re-hosted on the target outdoor wall on the same façade line that contains it entirely, at the same position along the façade, with the same sill height and size; only its offset is re-expressed from the target wall's start point. A window that no single target wall contains is an error; windows are never moved, resized, or split silently. Window transformations W1 to W5 are stage S5 (ADR-012).

**Boolean operations.** Intersection, union, and difference use Clipper2 2.0.0 (`ClipperD` with a `PolyTreeD`, which keeps the hole hierarchy) at a precision of 6 decimals, which is the 1e-6 m `Distance` grid of ADR-004. Results therefore lie on that grid. The inward offset used by the perimeter/core simplifier is specified with that simplifier in S3, not here.

**Edge matching.** Building the surfaces of a zoned plan snaps every vertex to the `Distance` grid, splits zone edges at other zones' vertices, pairs reversed edges of two zones as interzone walls, and marks edges on the plan boundary as outdoors. Any other edge indicates a gap or an overlap and is an error; geometry is never repaired silently (GLOBAL.md quality rule 6). Consecutive collinear segments with the same boundary merge into one wall.

**Rhino geometry.** RhinoCommon types (Breps, points, curves) appear only in `Lod.Grasshopper`. The core works in metres; the plugin converts core geometry to Rhino geometry for previews and `Convert2BEM` output, scaled from metres to the active document's model units.

**Out of scope:** sloped roofs, non-vertical walls, and curved geometry. Footprints with holes are supported by the types, but the perimeter/core simplifier rejects them until S8 (courtyard plans).

## Consequences

- Areas and volumes are closed-form; validation compares sums of polygon areas.
- Snapping moves a vertex by at most half a grid step (5e-7 m), which changes the area of a 10 m zone by a relative amount of the order of 1e-7; ADR-004 sets the relative area tolerance accordingly.
- Walls and their windows are rectangles in one vertical plane, so converters can build them directly.
- Window and zoning effects stay separable: at W0 every zoning level keeps the Z0 windows where they are, so glazed area per façade position, per orientation, and per building does not change with zoning.
- A zoning that cuts a façade inside a window cannot keep that window at W0 and fails. ADR-011 (S8) and the window levels (S5) decide how such windows are treated (roadmap risk table).
- Very short wall fragments can host very small windows. Minimum wall and window geometry is decided in ADR-011 before S8.
- Sloped roofs or non-vertical walls would require a new geometry ADR.
````

- [x] **Step 2: Check the working tree**

```bash
git status --short
```

Expected: `?? docs/decisions/ADR-002-geometry.md`

- [x] **Step 3: Commit**

```bash
git add docs/decisions/ADR-002-geometry.md
git commit -m "docs(decisions): add adr-002 geometry representation"
```

### Task 3: ADR-003 Schedules

**Files:** Create `docs/decisions/ADR-003-schedules.md`
**Interfaces:** Consumes: D-024, D-038; ADR-001 (read-only arrays). / Produces: the schedule model S1 implements (`Schedule`, `ScheduleKind`, `Schedule.FromDailyProfiles`, `AggregationRecord`); referenced by ADR-005 and ADR-007.

- [x] **Step 1: Write `docs/decisions/ADR-003-schedules.md`**

````markdown
# ADR-003: Schedules

Status: Accepted

Date: 2026-10-01

Decisions: D-024, D-038

## Context

Program presets carry load schedules and, for conditioned spaces, heating and cooling setpoint schedules (D-024, D-038). The equivalence principle (research brief §7) conserves scheduled loads at every timestep, and GLOBAL.md scientific rule 2 requires each derived schedule to record its sources, aggregation method, and weights. The research brief asks for a common normalised representation over a fixed timestep (§6); the repository spec asks for immutable schedules (§4.7). Setpoints are temperatures, not load fractions (GLOBAL.md scientific rule 5).

## Options considered

### Time base

1. **Rule-based day and week schedules.** Compact, but a weighted combination of different rule sets is in general not expressible as another rule set, so aggregated schedules would need a second representation.
2. **Explicit hourly values for one year.** Input and aggregated schedules have the same form, and per-timestep conservation is an element-wise comparison.
3. **Sub-hourly values.** More values with no benefit while presets are defined hourly.

### Year length

1. **8760 hours, a non-leap year.**
2. **8784 hours, or a configurable year.** A second length would make schedules of different lengths incomparable.

### Value meaning

1. **Untyped values.** Nothing would prevent a temperature from being used as a load fraction.
2. **A schedule kind:** `Fraction` in [0, 1] or `Temperature` in °C. Loads accept only fractions, setpoints only temperatures.

### Creation from daily profiles

1. **Seven daily profiles plus a holiday calendar.** More input than the presets need.
2. **One weekday and one weekend 24-hour profile, with the weekday of 1 January given explicitly; no holidays.**

## Decision

- A `Schedule` has a name, a `ScheduleKind`, and exactly 8760 hourly values for a non-leap year; value 0 is the hour starting at 00:00 on 1 January. Schedules are immutable: the values sit in a private array exposed as `IReadOnlyList<double>` (ADR-001).
- `ScheduleKind.Fraction` is a dimensionless multiplier of a load's design value; every value lies in [0, 1]. `ScheduleKind.Temperature` is in °C and is used for heating and cooling setpoints; any finite value is allowed.
- Creating a schedule validates the length (8760), finiteness, and the fraction range, and reports violations as diagnostics in a result type rather than as exceptions (GLOBAL.md quality rule 5).
- Schedules are created from 8760 values, as a constant, or from a weekday and a weekend 24-hour profile repeated Monday to Friday and Saturday to Sunday, with the weekday of 1 January as an explicit input. Holidays are not modelled.
- Loads use fraction schedules; setpoints use temperature schedules.
- A derived schedule carries an `AggregationRecord`: the aggregation method (magnitude weighted for load schedules, ADR-007; floor-area weighted for the setpoints of conditioned zones, ADR-005), the source zones, and one weight per source. Input schedules carry no record.

## Consequences

- Schedules from different sources combine and compare hour by hour; ADR-004 defines the tolerances for those comparisons.
- Because the weekday of 1 January is part of every profile-based schedule, presets are reproducible without reference to any calendar year.
- Calendar effects beyond the weekday/weekend split, such as holidays, are absent from presets. Adding them later changes preset values, not the representation.
- Leap years or sub-hourly timesteps would change the representation and require a new ADR.
````

- [x] **Step 2: Check the working tree**

```bash
git status --short
```

Expected: `?? docs/decisions/ADR-003-schedules.md`

- [x] **Step 3: Commit**

```bash
git add docs/decisions/ADR-003-schedules.md
git commit -m "docs(decisions): add adr-003 schedule representation"
```

### Task 4: ADR-004 Tolerances

**Files:** Create `docs/decisions/ADR-004-tolerances.md`
**Interfaces:** Consumes: ADR-002 (Clipper2 precision). / Produces: the values and comparison rule S1 implements in `Lod.Core.Common.ToleranceSettings` (`Distance`, `RelativeArea`, `RelativeLoad`, `AbsoluteSchedule`, `Angle`, `Default`, `DecimalPrecision`, `AreaEquals`, `LoadEquals`, `ScheduleEquals`).

- [x] **Step 1: Write `docs/decisions/ADR-004-tolerances.md`**

````markdown
# ADR-004: Numerical tolerances

Status: Accepted

Date: 2026-10-01

Decisions: none earlier; this ADR supersedes the relative area tolerance proposed in roadmap v1 and v2.

## Context

Tolerances are defined in one central configuration and nowhere else (GLOBAL.md quality rule 4, AGENTS.md working rule 14); the repository spec names the categories distance, area, load, schedule, and angle (§19). AGENTS.md working rule 12 forbids widening a tolerance to make a test pass, so each value must be justified before tests rely on it. Roadmap v1 and v2 proposed distance 1e-6 m, relative area 1e-9, relative load 1e-9, absolute schedule 1e-9, and angle 1e-6 rad; roadmap v3 lists the values decided here. Polygon boolean operations run on Clipper2 at 6 decimals (ADR-002), so their results lie on a 1e-6 m grid.

## Options considered

### Where tolerances live

1. **Constants where they are used.** Forbidden by GLOBAL.md.
2. **One immutable settings object passed to every service that compares numbers.**

### Comparison form

1. **Absolute:** `|a − b| ≤ tol`. Scale-dependent: one number cannot serve m², W, and m³/h alike.
2. **Purely relative:** `|a − b| ≤ rel × max(|a|, |b|)`. Degenerates near zero: two values that should both be 0, such as the glazing of a windowless zone or a load with zero design value, fail on any rounding noise.
3. **Relative with a floor of 1:** `|a − b| ≤ rel × max(1, |a|, |b|)`. Relative for magnitudes above 1, absolute at the level of `rel` below 1.

### Relative area tolerance

1. **1e-9 (proposed in roadmap v1 and v2).** Clipper2 rounds every vertex to the 1e-6 m grid, moving it by up to 5e-7 m. For zones of about 10 m this gives relative area errors of the order of 1e-7, far above 1e-9, although the geometry is correct.
2. **1e-6.** Above that rounding effect; for a 100 m² zone it allows 1e-4 m² (1 cm²), far below any modelling difference that matters.

### Relative load tolerance

1. **1e-9.** Achievable because transfer fractions are normalised per source: each source's fractions sum to exactly 1, so extensive quantities (installed and scheduled magnitudes, occupants, air flow) are conserved to floating-point precision regardless of polygon rounding.
2. **A looser value such as 1e-6.** Would hide real aggregation errors without being needed.

### Other values

- **Distance 1e-6 m.** One micrometre, far below construction precision; it doubles as the snapping grid and the Clipper2 precision (6 decimals).
- **Absolute schedule 1e-9.** Schedule values are fractions in [0, 1] or temperatures of tens of °C, computed as weighted means in double precision.
- **Angle 1e-6 rad.** For parallelism tests, such as whether two walls lie on the same façade line.

## Decision

`Lod.Core.Common.ToleranceSettings` is the only place where tolerances are defined: an immutable class with five values, each of which must be positive and finite (the constructor rejects zero, negative, NaN, and infinite values).

| Setting | Default | Unit | Used for |
| --- | --- | --- | --- |
| `Distance` | 1e-6 | m | vertex snapping and matching; Clipper2 precision (`DecimalPrecision` = round(−log₁₀ `Distance`) = 6 decimals) |
| `RelativeArea` | 1e-6 | — | area and volume comparisons and façade coverage lengths (D-041); also the threshold below which an overlap counts as a sliver, and the slack on fraction range checks |
| `RelativeLoad` | 1e-9 | — | design and hourly scheduled magnitudes of loads, occupancy, and air flow |
| `AbsoluteSchedule` | 1e-9 | unit of the schedule | schedule values |
| `Angle` | 1e-6 | rad | parallelism and collinearity tests |

- `ToleranceSettings.Default` holds these values. Services receive a `ToleranceSettings` through their constructor; nothing reads tolerances from global state.
- Relative comparisons use a floor of 1: `|a − b| ≤ rel × max(1, |a|, |b|)` (`AreaEquals` with `RelativeArea`, `LoadEquals` with `RelativeLoad`). Schedule values compare absolutely: `|a − b| ≤ AbsoluteSchedule` (`ScheduleEquals`).
- Overrides: Grasshopper components use `ToleranceSettings.Default` and expose no tolerance input. A non-default instance may be used only in a research test or through a future explicit input, and its values must then be recorded in the provenance of every object it produced. No override path exists in stages S0 to S4.
- The relative area tolerance proposed in roadmap v1 and v2 (1e-9) is superseded by 1e-6; the other proposed values stand.
- A default changes only through a new ADR with a decision-log entry, never to make a test pass (AGENTS.md working rule 12).

## Consequences

- One object is passed to services and, when it differs from the default, recorded; tests that probe tolerance behaviour construct their own instances.
- Area checks tolerate Clipper2 rounding, while load checks stay tight because normalised transfer fractions make load conservation independent of polygon rounding.
- Values near zero compare absolutely at the tolerance level, so zero glazing and zero loads compare cleanly.
- Source-target mapping (S3) drops overlaps smaller than `RelativeArea` × the source's area as slivers. Because fractions are normalised per source, a dropped sliver's share moves to the source's other targets instead of being lost.
````

- [x] **Step 2: Check the working tree**

```bash
git status --short
```

Expected: `?? docs/decisions/ADR-004-tolerances.md`

- [x] **Step 3: Commit**

```bash
git add docs/decisions/ADR-004-tolerances.md
git commit -m "docs(decisions): add adr-004 numerical tolerances"
```

### Task 5: ADR-005 Conditioning and setpoint aggregation, and research brief §7

**Files:** Create `docs/decisions/ADR-005-conditioning-and-setpoints.md`; Modify `docs/LOD_geometric_zoning_equivalence_research_brief.md` (§7)
**Interfaces:** Consumes: D-038 (superseding D-027, D-028, D-029); ADR-003. / Produces: the rule S1 implements: `Thermostat` (heating and cooling setpoint schedules), `ZoneProgram.Thermostat` (`null` for an unconditioned zone) and `ZoneProgram.IsConditioned`; in `EquivalentPropertyAggregator`, "any conditioned wins" over sources with a positive area fraction, setpoints with `AggregationMethod.FloorAreaWeighted` and weights `fᵢ·Aᵢ` over the conditioned sources, and error `ZeroSetpointWeight`. Also the reported (not enforced) conditioned-floor-area check of S3 validation.

- [x] **Step 1: Write `docs/decisions/ADR-005-conditioning-and-setpoints.md`**

````markdown
# ADR-005: Conditioning and setpoint aggregation

Status: Accepted

Date: 2026-10-01

Decisions: D-038 (superseding D-027, D-028, and D-029)

## Context

When a plan simplifier or floor aggregator merges zones, the target zone needs one conditioning status and, if it is conditioned, one heating and one cooling setpoint schedule. Setpoints are controls, not additive loads (GLOBAL.md scientific rule 5): averaging them conserves no physical quantity, so the rule is a modelling choice that must be explicit and recorded. The research brief §7 lists candidate rules: the dominant source schedule, an area-weighted temperature schedule, a load-weighted schedule, or prohibiting merges of zones with incompatible setpoints.

The decision went through several steps. D-010 made the aggregation method a parameter with two options, floor-area weighting and exposed-surface-area weighting, and D-014 settled its details: the method was a required input; exposed area counted exterior walls (with their windows) and roofs; and when the exposed-area weights summed to zero, the weights fell back to floor area with a warning. D-027 replaced both entries with floor-area weighting only. D-028 treated every space as conditioned, and D-029 framed that as an intentional homogenisation. Plan review then found that with every space conditioned, every source has a thermostat, so the setpoint rule is never exercised, and Z0 loses the distinction between dwelling units and unconditioned corridors, stairs, or other spaces. D-038 supersedes D-027, D-028, and D-029.

## Options considered

### Conditioning status

1. **Every space conditioned (D-028, D-029).** Keeps conditioning out of the LoD variables, but the setpoint rule is never exercised and Z0 cannot represent unconditioned spaces.
2. **Conditioning from the program preset (D-038).** Each program is conditioned, with a thermostat, or unconditioned, without setpoints.

### Conditioning of a merged zone

1. **Conditioned only if every source is conditioned.** Merging a dwelling unit with an unconditioned stair would drop the dwelling unit's thermostat.
2. **Conditioned if any source contributing floor area is conditioned ("any conditioned wins", D-038).** Conditioned floor area never ends up without setpoints; in exchange, unconditioned floor area merged into a conditioned target becomes conditioned.
3. **Never merging conditioned with unconditioned spaces.** Would constrain perimeter/core and one-zone-per-floor zoning, which merge different space types by design.

### Setpoint weighting

1. **The dominant source schedule.** Ignores every other source, and small geometric changes can flip which source dominates, so the result jumps.
2. **Prohibiting merges of zones with incompatible setpoints.** Perimeter/core and one-zone-per-floor zoning merge different space types by design; they would be impossible whenever presets differ.
3. **Load weighting.** No single load is the natural weight, and the control assumption would change whenever an internal gain changes.
4. **Exposed-surface-area weighting (D-010, D-014).** Rejected for the reasons recorded in D-027, which D-038 keeps:
   - It makes the control assumption depend on geometry, which confounds the experiment: simplification should change geometry, not the thermostat assumption.
   - Split source zones carry floor area by overlap, but no well-defined share of exposure.
   - The zero-exposure fallback to floor area is discontinuous: a target whose sources have a tiny exposed area is weighted by exposure, one whose sources have none by floor area.
   - Exposure varies across typologies with the same program, so the same program would get different setpoints by typology.
5. **A method parameter (D-010, D-014).** More freedom, but every result would depend on a choice outside the LoD variables under study.
6. **Floor-area weighting over the conditioned sources.** Depends only on the floor area each conditioned source contributes, is continuous, and is defined for split zones.

### Conditioned floor area

1. **Enforce its conservation.** Every zoning that merges conditioned and unconditioned spaces would fail validation.
2. **Report the change without enforcing it (D-038).** The enlargement is a consequence of the zoning simplification under study, and it stays visible.

## Decision

**Conditioning comes from the program preset.** A conditioned program has a thermostat: a heating and a cooling setpoint schedule, both `Temperature` schedules (ADR-003). An unconditioned program has no setpoints.

**Any conditioned wins.** A target zone is conditioned if any source zone contributing floor area to it (area fraction above 0) is conditioned. A source that contributes only façade (area fraction 0) does not condition the target. If no contributing source is conditioned, the target is unconditioned and has no setpoints.

**Setpoints.** The heating and the cooling setpoint schedule of a conditioned target are each aggregated hour by hour by floor-area weighting over the conditioned contributing sources `C`:

```text
T*(t) = Σᵢ∈C wᵢ · Tᵢ(t) / Σᵢ∈C wᵢ        wᵢ = fᵢ · Aᵢ
```

`Aᵢ` is the floor area of source zone `i` and `fᵢ` the fraction of it transferred to the target, so `wᵢ` is the transferred floor area: the whole source area for a merged zone, and the part mapped to the target (its overlap) for a split zone.

- There is no method input, no exposed-area definition, and no fallback.
- The result is a `Temperature` schedule whose `AggregationRecord` holds the method `FloorAreaWeighted`, the conditioned source zones, and the weights `wᵢ` (ADR-003). This record, together with the provenance of the producing operation, is the experiment metadata the research brief §7 requires.
- A total weight of zero is an error (`ZeroSetpointWeight`). It occurs only when the conditioned contributing sources have zero floor area.
- Setpoint aggregation is a prescribed control rule, not a conservation invariant. Validation does not check setpoints for conservation; tests check the definition instead: the result equals the weighted mean over the conditioned sources at every hour; a single source returns its own schedule; the order of sources does not change the result; unconditioned sources carry no weight; a target whose contributing sources are all unconditioned is unconditioned; and façade-only sources do not condition a target.
- **Conditioned floor area.** Merging conditioned and unconditioned sources enlarges the conditioned floor area. Validation reports the conditioned floor area of source and target but does not enforce their equality.
- Exposed-surface-area weighting stays rejected for the reasons in D-027.
- D-027, D-028, and D-029 are superseded by D-038; D-010 and D-014 had already been superseded by D-027.

## Consequences

- The setpoint rule is exercised whenever conditioned zones with different setpoints merge, and Z0 keeps the distinction between conditioned and unconditioned spaces.
- A target zone's thermostat depends only on the conditioned floor area it receives, not on its façades, so simplification does not tie the control assumption to geometry.
- Conditioning itself can change with zoning: unconditioned floor area merged into a conditioned target becomes conditioned. The validation report shows the change, so results can be read with it in mind.
- Example with illustrative values: merging 30 m² conditioned at 21 °C, 10 m² conditioned at 17 °C, and 5 m² unconditioned gives a conditioned target at (30 × 21 + 10 × 17) / 40 = 20 °C for that hour; the conditioned floor area grows from 40 m² to 45 m², and validation reports it.
- Conditioning values come from the program presets. The example presets of S1 are illustrative; sourced conditioning for the DOE prototype is an open research input (roadmap §7).
- Converters handle unconditioned zones: `Convert2BEM` carries a conditioned flag (S2), and ADR-010 covers unconditioned zones for `Convert2IDF` (S6).
- The research brief §7 records the rule in the same change.
````

- [x] **Step 2: Append the adopted rule to research brief §7**

In `docs/LOD_geometric_zoning_equivalence_research_brief.md`, section `## 7. Equivalence Principle`, find this exact anchor text (line 269, the last line of §7):

```text
The chosen rule must be recorded in experiment metadata.
```

Replace it with (the anchor line stays; a blank line and the new paragraphs follow, before the `---` that closes §7):

```markdown
The chosen rule must be recorded in experiment metadata.

Rule adopted for this project (ADR-005, D-038): conditioning comes from the program preset, and an unconditioned zone has no setpoints. A simplified zone is conditioned if any source zone contributing floor area to it is conditioned ("any conditioned wins"). Its heating and cooling setpoint schedules are each aggregated hour by hour by floor-area weighting over the conditioned contributing sources \(C\) only,

\[
T^\*(t) = \frac{\sum_{i \in C} w_i T_i(t)}{\sum_{i \in C} w_i}, \qquad w_i = f_i A_i
\]

where \(w_i\) is the floor area of source zone \(i\) transferred to the target zone: its area fraction \(f_i\) times its floor area \(A_i\), which is the overlap area when a source zone is split between targets. There is no method parameter and no fallback; exposed-surface-area weighting was rejected because it would make the control assumption depend on geometry. This is a prescribed control rule, not a conservation invariant, so validation checks it against its definition rather than against a conserved total. Merging conditioned and unconditioned sources enlarges the conditioned floor area; validation reports this change without enforcing it, because it is a consequence of the zoning simplification under study. Each aggregated setpoint schedule records its source zones, the method, and the weights.
```

- [x] **Step 3: Check the diff**

```bash
git diff --stat
git status --short
```

Expected: the research brief shows only insertions (`1 file changed, 8 insertions(+)`), and `git status --short` lists ` M docs/LOD_geometric_zoning_equivalence_research_brief.md` and `?? docs/decisions/ADR-005-conditioning-and-setpoints.md`.

- [x] **Step 4: Commit**

```bash
git add docs/decisions/ADR-005-conditioning-and-setpoints.md docs/LOD_geometric_zoning_equivalence_research_brief.md
git commit -m "docs(decisions): add adr-005 conditioning and setpoint aggregation and record it in the research brief"
```

### Task 6: ADR-007 Load-basis aggregation and research brief §9

**Files:** Create `docs/decisions/ADR-007-load-basis-aggregation.md`; Modify `docs/LOD_geometric_zoning_equivalence_research_brief.md` (§9)
**Interfaces:** Consumes: D-019, D-041, D-047; ADR-003. / Produces: the load rule S1 implements (`LoadType`, `LoadBasis`, `DesignMagnitudes`, `EquivalentPropertyAggregator`, `AggregationMethod.MagnitudeConserved`/`MagnitudeWeighted`), the per-source normalisation S3 implements in `TransferMatrix`, and the façade-coverage precondition S3 implements (`FacadeAttribution.CoverageGaps`, error `FacadeNotCovered`, validation check `FacadeCoverage`).

- [x] **Step 1: Write `docs/decisions/ADR-007-load-basis-aggregation.md`**

````markdown
# ADR-007: Load-basis aggregation

Status: Accepted

Date: 2026-10-01

Decisions: D-019, D-041, D-047

ADR-006 is reserved for the plan generation mechanism (S7).

## Context

The research brief §7 conserves installed and per-timestep scheduled load with `p* = Σ Aᵢpᵢ / Σ Aᵢ` and `s*(t) = Σ Aᵢpᵢsᵢ(t) / Σ Aᵢpᵢ`. §9 treats rezoning as a mapping with transfer fractions, conserving extensive quantities `Q_j = Σᵢ f_ji Q_i` and weighting intensive quantities by "the appropriate basis". The repository spec (§4.6) lists load bases: area density, per person, absolute, façade-area based, and air-change based. D-019 requires air-change loads to be volume weighted. Plan simplifiers split source zones across several targets (S3), so the rule must work with fractions, not only with whole-zone merges. D-041 adds that fractions normalised per source wall are safe only when the target façades cover each source façade completely. One program may express a load type in more than one basis (ASHRAE 62.1 ventilation is per person plus per floor area), and simplified zones merge programs that express the same load type in different bases, e.g. ventilation per person in one and per floor area in another (D-047).

## Options considered

1. **One formula per basis** (area weighting, occupancy weighting, summation, façade weighting, volume weighting). Five code paths, each to be proven conservative separately, each needing its own rule for split zones.
2. **One magnitude rule for every basis.** Convert each source value to an absolute design magnitude, transfer a fraction of it, sum, and re-express the sum in the same basis. The per-basis rules follow as special cases.
3. **Express every target load as an absolute magnitude.** Conservation is trivial, but the target program would no longer be expressed like the source program (GLOBAL.md scientific rule 3).
4. **Several bases for one load type, within a program or among the sources of a target.**
   - *Aggregate each (load type, basis) component separately; components of one type add up* (adopted, D-047). Every component is conserved exactly by the rule of option 2, and no basis is converted.
   - *Reject mixed bases* (rejected). It blocks legitimate program combinations: ventilation per person plus per floor area within one program, or merging a zone with per-person ventilation into one with per-area ventilation.
   - *Convert them to one basis* (rejected). It would choose a basis silently and change program assumptions (GLOBAL.md scientific rule 3).
5. **The exterior-area basis: walls and roofs, or walls only.** Plan simplifiers work on one storey before floors are stacked, so whether a ceiling becomes a roof is unknown when loads are aggregated. Counting walls only keeps the basis well defined at every pipeline step.

## Decision

**Units of design magnitudes.** Occupancy in people; lighting, electric equipment, and gas equipment in W; domestic hot water, ventilation, and infiltration in m³/h.

**Bases.** A load value is expressed per a basis quantity `B`; its design magnitude is `Q = value × B`.

| Basis | Basis quantity `B` |
| --- | --- |
| `PerFloorArea` | floor area, m² |
| `PerPerson` | design occupants of the zone, the summed magnitude of its occupancy components |
| `Absolute` | 1 |
| `PerExteriorWallArea` | gross area of the zone's walls with an outdoor boundary, windows included, m²; walls only, no roofs |
| `AirChangesPerHour` | zone volume, m³, so `Q = ACH × V` in m³/h |

Occupancy may only be `PerFloorArea` or `Absolute`. A program with a `PerPerson` load must also contain an occupancy load.

**Components (D-047).** A program holds at most one load per load type and basis; a load type expressed in several bases has several components, which add up (ventilation per person plus per floor area). Occupancy may have components too: the zone's design occupants are their sum, and every `PerPerson` component uses that sum.

**One rule for every basis.** Each component (load type and basis) is aggregated on its own. For each component of a target zone, every source zone `i` that has the component transfers

```text
Tᵢ = fᵢ · Qᵢ
```

where `fᵢ` is the exterior-wall fraction (the share of the source's exterior wall area that becomes the target's exterior wall area) for `PerExteriorWallArea` loads, and the area fraction (the share of the source's floor area, and with it of its volume, occupants, and absolute loads) for every other basis. A source without the component contributes nothing to it. Then

```text
Q*     = Σᵢ Tᵢ
value* = Q* / B*                 B* = the target's quantity of the component's basis
s*(t)  = Σᵢ Tᵢ · sᵢ(t) / Q*
```

Occupancy components are aggregated first, so the `B*` of a `PerPerson` component is the target's design occupants summed over all its occupancy components.

For whole-zone merges (`fᵢ = 1`) this gives area weighting for `PerFloorArea` (`value* = Σ Aᵢpᵢ / Σ Aᵢ`, the research brief §7 formulation), occupancy weighting for `PerPerson`, summation for `Absolute`, exterior-wall-area weighting for `PerExteriorWallArea`, and volume weighting for `AirChangesPerHour` (`ACH* = Σ VᵢACHᵢ / Σ Vᵢ`, D-019).

**Errors and the zero-magnitude rule.** Sources of one target that define the same load type in different bases are not an error: each basis is its own component. Per component:

- `Q* > 0` while the target's basis quantity `B*` is 0: error, because the magnitude cannot be expressed in the target.
- `Q* = 0`: value 0, a constant-zero fraction schedule, and an informational diagnostic. This is the zero-denominator guard of the schedule formula.

**Traceability.** Every aggregated load component records its method (`MagnitudeConserved`), source zones, and transferred magnitudes `Tᵢ` as weights; its schedule records `MagnitudeWeighted` with the same sources and weights (ADR-003).

**Transfer fractions.** Area fractions are normalised per source, `f_ji = overlap_ji / Σⱼ overlap_ji`, so each source's fractions sum to exactly 1 and every extensive quantity is conserved to floating-point precision regardless of polygon rounding; how well the targets cover each source is a separate validation check. Exterior-wall fractions come from matching source and target outdoor walls that lie on the same façade line and are normalised per source wall in the same way (S3).

**Façade coverage first (D-041).** Normalisation alone would hand the whole wall area of a source wall to a target façade that covers only part of it. `PerExteriorWallArea` transfers therefore use exterior-wall fractions only after façade coverage is proven: for every source outdoor wall `i`, the target outdoor walls on the same façade line must cover its full length, `Σⱼ Lᵢⱼ ≈ Lᵢ` within the relative tolerance of ADR-004, checked before any normalisation. Plan simplifiers and `SingleZoneMerged` fail when it does not hold, and floor validation enforces it as a separate check.

**Invariants.** For each load component (load type and basis), the installed magnitude `Σ Q` and the scheduled magnitude `Σ Q · s(t)` at each of the 8760 hours are conserved within `RelativeLoad` (ADR-004); the totals of each load type, the sums of its components, are therefore conserved too. Occupancy and air flows are load types, so the same checks cover them, and the design occupants, the sum of the occupancy components, are conserved.

## Worked example

Lighting in two source zones merged whole into one target (`f = 1` for both):

| Zone | Floor area | Value | Magnitude `Q = value × area` |
| --- | --- | --- | --- |
| A | 10 m² | 5 W/m² | 50 W |
| B | 30 m² | 1 W/m² | 30 W |
| Target | 40 m² | 80 W / 40 m² = 2 W/m² | 80 W |

The target schedule is `s*(t) = (50 · s_A(t) + 30 · s_B(t)) / 80`: the source schedules are weighted 50:30. In an hour with `s_A = 1` and `s_B = 0`, `s* = 0.625`, and the target's scheduled magnitude 2 W/m² × 40 m² × 0.625 = 50 W equals the sources' 50 W × 1 + 30 W × 0. Weighting the schedules by floor area instead, (10 · 1 + 30 · 0) / 40 = 0.25, would give only 20 W in that hour: floor-area weighting is right for the value, magnitude weighting for the schedule.

Mixed bases (D-047): source A (100 m², 0.1 people/m², so 10 people) has ventilation 30 m³/h per person; source B (100 m², no occupancy) has ventilation 2 m³/h per m². Merged whole into a 200 m² target, the target has 10 people and two ventilation components: per person, 300 m³/h / 10 people = 30 m³/h per person with A's schedule; per floor area, 200 m³/h / 200 m² = 1 m³/h per m² with B's schedule. Each component conserves its source magnitude at every hour, and the target's total ventilation is their sum.

## Consequences

- One code path implements every basis, so conservation is proven once.
- Bases survive simplification: a per-floor-area load stays per floor area in the target.
- Programs that express a load type in different bases can be merged; each basis stays a separate component in the target, so a target may carry several components of one type, each with its own schedule.
- A positive magnitude that cannot be expressed in the target's basis fails instead of being dropped.
- A zoning whose target façades leave part of a source façade uncovered fails, instead of shifting that façade's wall-based loads silently.
- The research brief §9 records the rule in the same change.
````

- [x] **Step 2: Append the adopted rule to research brief §9**

In `docs/LOD_geometric_zoning_equivalence_research_brief.md`, section `## 9. Rezoning as Spatial Remapping`, find this exact anchor text (line 378, the last line of §9):

```text
The transfer matrix should be retained as part of the output metadata so every simplified model can be traced back to its source model.
```

Replace it with:

```markdown
The transfer matrix should be retained as part of the output metadata so every simplified model can be traced back to its source model.

Rule adopted for this project (ADR-007, D-019, D-041, D-047): loads are aggregated per component, one per load type and basis; a program may express a load type in several bases (e.g. ventilation per person plus per floor area), and its components add up. Every component is converted to its absolute design magnitude \(Q_i\) = value × basis quantity, where the basis quantity is the floor area, the design occupants (the sum of the zone's occupancy components), 1 for absolute loads, the gross exterior wall area (walls with an outdoor boundary, windows included), or the zone volume for air changes per hour. Source zone \(i\) transfers \(T_{ji} = f_{ji} Q_i\) to target zone \(j\), where \(f_{ji}\) is the exterior-wall fraction for loads per exterior wall area and the floor-area fraction otherwise; a source without the component contributes nothing to it. The target magnitude \(Q_j = \sum_i T_{ji}\) is re-expressed in the component's basis as \(v_j = Q_j / B_j\), and the target schedule is

\[
s_j(t) = \frac{\sum_i T_{ji} s_i(t)}{Q_j}
\]

This yields area weighting for densities, occupancy weighting for per-person loads, summation for absolute loads, exterior-wall-area weighting for loads per exterior wall area, and volume weighting for air changes per hour, \(ACH^\* = \sum_i V_i ACH_i / \sum_i V_i\) (D-019). Transfer fractions are normalised per source, \(\sum_j f_{ji} = 1\), so every extensive quantity is conserved to floating-point precision regardless of polygon rounding; how well the target zones cover each source is checked separately. Exterior-wall fractions are used only after the target façades are shown to cover every source outdoor wall over its full length, checked before any normalisation (D-041). Loads of one type with different bases are neither rejected nor converted to one basis: each basis is aggregated as its own component and conserved exactly, so no program assumption changes (D-047). A positive magnitude cannot be expressed in a target whose basis quantity is zero; this is an error. A zero total magnitude gives the value 0 and a constant-zero schedule.
```

- [x] **Step 3: Check the diff**

```bash
git diff --stat
git status --short
```

Expected: the research brief shows only insertions (`1 file changed, 8 insertions(+)`), and `git status --short` lists ` M docs/LOD_geometric_zoning_equivalence_research_brief.md` and `?? docs/decisions/ADR-007-load-basis-aggregation.md`.

- [x] **Step 4: Commit**

```bash
git add docs/decisions/ADR-007-load-basis-aggregation.md docs/LOD_geometric_zoning_equivalence_research_brief.md
git commit -m "docs(decisions): add adr-007 load-basis aggregation and record it in the research brief"
```

### Task 7: Research brief §10 window rule

**Files:** Modify `docs/LOD_geometric_zoning_equivalence_research_brief.md` (§10)
**Interfaces:** Consumes: D-026, D-039; ADR-002 (explicit windows, the first generator's placement rule, re-hosting). / Produces: the window rule that S2 (the generator's centered windows), S3, and S4 (`WindowRehosting`, error `WindowNotHosted`) implement; W1 to W5 follow in S5.

- [x] **Step 1: Insert the adopted rule after the §10 intro sentence**

In `docs/LOD_geometric_zoning_equivalence_research_brief.md`, section `## 10. Window Representation Levels`, find this exact anchor text (line 384):

```text
Window treatment should form an independent experimental axis.
```

Replace it with (the paragraph goes between the intro sentence and `### W0 — Explicit Ground-Truth Windows`):

```markdown
Window treatment should form an independent experimental axis.

Rule adopted for this project (D-039, D-026): walls carry explicit windows, each with a position along the wall, a sill height, a width, and a height, and a wall may carry any number of windows (ADR-002). The first plan generator uses one simple deterministic rule: one window per outdoor wall, centered on it and sized from the window-to-wall ratio of the zone's program preset, \(A_\text{glazing} = \text{WWR} \times A_\text{wall}\) (D-026); this is that generator's placement rule, not a property of windows. Plan simplifiers and floor aggregators keep every window unchanged, so every zoning and vertical level is at W0: where walls are rebuilt, each source window is re-hosted on the target outdoor wall that contains it, at the same position, sill height, and size. A window that no single target wall contains is an error; windows are never moved, resized, or split silently. The levels W1 to W5 below are separate window transformations, planned as roadmap stage S5 with their own decision record (ADR-012), so window effects can be varied independently of zoning.
```

- [x] **Step 2: Check the diff**

```bash
git diff --stat
```

Expected: `1 file changed, 2 insertions(+)` for the research brief only.

- [x] **Step 3: Commit**

```bash
git add docs/LOD_geometric_zoning_equivalence_research_brief.md
git commit -m "docs(research): record the explicit window rule in the research brief"
```

- [ ] **Step 4: Merge the slice (D-004, adapted: no gate script exists yet)**

`scripts/verify.ps1` arrives in Slice B, and this slice contains no code, so the gate is replaced by a diff check.

```bash
git fetch origin
git rebase origin/main
git diff --name-only origin/main...HEAD
```

Expected: exactly these seven paths:

```text
docs/LOD_geometric_zoning_equivalence_research_brief.md
docs/decisions/ADR-001-toolchain.md
docs/decisions/ADR-002-geometry.md
docs/decisions/ADR-003-schedules.md
docs/decisions/ADR-004-tolerances.md
docs/decisions/ADR-005-conditioning-and-setpoints.md
docs/decisions/ADR-007-load-basis-aggregation.md
```

```bash
git switch main
git pull --ff-only
git merge --ff-only docs/decisions-foundation-adrs
git push origin main
git branch -d docs/decisions-foundation-adrs
```

Expected: `git merge` reports `Fast-forward`. If it refuses because `main` moved, switch back to the branch and repeat this step from `git fetch origin`.

---

## Slice B — `build/solution-skeleton`

### Task 8: Solution skeleton with the first test

**Files:** Test `tests/Lod.Core.Tests/Lod.Core.Tests.csproj`, `tests/Lod.Core.Tests/Common/BuildInfoTests.cs`; Create `global.json`, `Directory.Build.props`, `Directory.Packages.props`, `src/Shared/IsExternalInit.cs`, `src/Lod.Core/Lod.Core.csproj`, `src/Lod.Core/Common/BuildInfo.cs`, `BEMGen.sln` (generated)
**Interfaces:** Consumes: ADR-001. / Produces: `namespace Lod.Core.Common; public static class BuildInfo { public static string InformationalVersion { get; } }`, used by `BemGenAssemblyInfo` and `BemGenInfoComponent` (Task 10) and by `Provenance` (S2). Also the shared build settings every later project inherits.

The test is written first. Because the test project must compile before it can fail on the missing type, the build infrastructure and an empty `Lod.Core` project are created next; the only thing missing at the first run is `BuildInfo`.

- [x] **Step 1: Check prerequisites**

```bash
dotnet --list-sdks
dotnet --list-runtimes
```

Expected: at least one SDK of version 8.0.100 or later (for example `10.0.401`), and a `Microsoft.NETCore.App 8.0.x` runtime (the `net8.0` tests run on it).

- [x] **Step 2: Create the slice branch**

```bash
git switch main
git pull --ff-only
git switch -c build/solution-skeleton main
```

- [x] **Step 3: Write the test project `tests/Lod.Core.Tests/Lod.Core.Tests.csproj`**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" />
    <PackageReference Include="xunit" />
    <PackageReference Include="xunit.runner.visualstudio" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\Lod.Core\Lod.Core.csproj" />
  </ItemGroup>

</Project>
```

- [x] **Step 4: Write the failing test `tests/Lod.Core.Tests/Common/BuildInfoTests.cs`**

```csharp
using System;
using Lod.Core.Common;
using Xunit;

namespace Lod.Core.Tests.Common;

public sealed class BuildInfoTests
{
    [Fact]
    public void InformationalVersionStartsWithTheAssemblyVersion()
    {
        Version version = typeof(BuildInfo).Assembly.GetName().Version!;

        Assert.StartsWith($"{version.Major}.{version.Minor}.{version.Build}", BuildInfo.InformationalVersion);
    }
}
```

- [x] **Step 5: Write `global.json`**

```json
{
  "sdk": {
    "version": "8.0.100",
    "rollForward": "latestMajor"
  }
}
```

- [x] **Step 6: Write `Directory.Build.props`**

```xml
<Project>
  <PropertyGroup>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <Deterministic>true</Deterministic>
    <Version>0.0.1</Version>
    <Authors>Environmental Systems Lab</Authors>
    <Product>BEMGen</Product>
  </PropertyGroup>

  <!-- Records and init accessors on netstandard2.0 (ADR-001). -->
  <ItemGroup Condition="'$(TargetFrameworkIdentifier)' != '.NETCoreApp'">
    <Compile Include="$(MSBuildThisFileDirectory)src\Shared\IsExternalInit.cs" Link="Polyfills\IsExternalInit.cs" />
  </ItemGroup>
</Project>
```

- [x] **Step 7: Write `Directory.Packages.props`**

Clipper2 is pinned here already; no project references it until S2 (ADR-001). An unused central version produces no warning.

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="Clipper2" Version="2.0.0" />
    <PackageVersion Include="Grasshopper" Version="8.19.25132.1001" />
    <PackageVersion Include="RhinoCommon" Version="8.19.25132.1001" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="17.14.1" />
    <PackageVersion Include="xunit" Version="2.9.3" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="3.1.5" />
  </ItemGroup>
</Project>
```

- [x] **Step 8: Write `src/Shared/IsExternalInit.cs`**

```csharp
namespace System.Runtime.CompilerServices;

/// <summary>
/// Enables <c>init</c> accessors and records on netstandard2.0, which does not ship this type.
/// </summary>
internal static class IsExternalInit
{
}
```

- [x] **Step 9: Write `src/Lod.Core/Lod.Core.csproj` (S0 version, no package references)**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <RootNamespace>Lod.Core</RootNamespace>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

</Project>
```

- [x] **Step 10: Create the solution and add both projects**

```bash
dotnet new sln --name BEMGen --format sln
dotnet sln BEMGen.sln add src/Lod.Core/Lod.Core.csproj tests/Lod.Core.Tests/Lod.Core.Tests.csproj
dotnet sln BEMGen.sln list
```

On SDK 8, omit `--format sln` (the option needs SDK 9.0.200 or later; SDK 8 creates `.sln` by default). Without it, SDK 10 would create `BEMGen.slnx`.

Expected:

```text
The template "Solution File" was created successfully.
Project `src\Lod.Core\Lod.Core.csproj` added to the solution.
Project `tests\Lod.Core.Tests\Lod.Core.Tests.csproj` added to the solution.
Project(s)
----------
src\Lod.Core\Lod.Core.csproj
tests\Lod.Core.Tests\Lod.Core.Tests.csproj
```

`dotnet sln add` also creates the solution folders `src` and `tests`.

- [x] **Step 11: Run the test and watch it fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: restore succeeds, `Lod.Core` builds, and the test project fails to compile because `BuildInfo` does not exist yet:

```text
...\tests\Lod.Core.Tests\Common\BuildInfoTests.cs(2,16): error CS0234: The type or namespace name 'Common' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?) [...Lod.Core.Tests.csproj]
```

- [x] **Step 12: Implement `src/Lod.Core/Common/BuildInfo.cs`**

```csharp
using System.Reflection;

namespace Lod.Core.Common;

/// <summary>
/// Version information of the running BEMGen code, recorded in provenance so results can be traced to a commit.
/// </summary>
public static class BuildInfo
{
    /// <summary>
    /// The informational version of <c>Lod.Core</c>, e.g. <c>0.0.1+3f2c1a9...</c>; the part after <c>+</c> is the commit SHA when built from a git checkout.
    /// </summary>
    public static string InformationalVersion { get; } =
        typeof(BuildInfo).Assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion
        ?? typeof(BuildInfo).Assembly.GetName().Version?.ToString()
        ?? "unknown";
}
```

- [x] **Step 13: Run the test and watch it pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected (durations vary):

```text
Passed!  - Failed:     0, Passed:     1, Skipped:     0, Total:     1, Duration: 79 ms - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 14: Confirm the commit SHA reaches the informational version**

```bash
git log -1 --format=%H
dotnet msbuild src/Lod.Core -t:Build -p:Configuration=Release -getProperty:InformationalVersion
```

Expected: the second command prints `0.0.1+` followed by the SHA printed by the first command (the current `HEAD`; the SDK's built-in Source Link adds it, ADR-001). The `dotnet msbuild -t:Build` form matters: `dotnet build -getProperty:InformationalVersion` prints an empty value. The same string appears in the `AssemblyInformationalVersionAttribute` line of `src/Lod.Core/obj/Release/netstandard2.0/Lod.Core.AssemblyInfo.cs`.

- [x] **Step 15: Check that only sources will be committed**

```bash
git status --porcelain -uall
```

Expected (no `bin/` or `obj/` paths):

```text
?? BEMGen.sln
?? Directory.Build.props
?? Directory.Packages.props
?? global.json
?? src/Lod.Core/Common/BuildInfo.cs
?? src/Lod.Core/Lod.Core.csproj
?? src/Shared/IsExternalInit.cs
?? tests/Lod.Core.Tests/Common/BuildInfoTests.cs
?? tests/Lod.Core.Tests/Lod.Core.Tests.csproj
```

- [x] **Step 16: Commit**

```bash
git add BEMGen.sln global.json Directory.Build.props Directory.Packages.props src/Shared/IsExternalInit.cs src/Lod.Core/Lod.Core.csproj src/Lod.Core/Common/BuildInfo.cs tests/Lod.Core.Tests/Lod.Core.Tests.csproj tests/Lod.Core.Tests/Common/BuildInfoTests.cs
git commit -m "build(repo): add solution skeleton with core library and test project"
```

### Task 9: Verification gate and AGENTS.md commands

**Files:** Create `scripts/verify.ps1`; Modify `AGENTS.md` ("Project state", "Commands")
**Interfaces:** Consumes: `BEMGen.sln` (Task 8). / Produces: the gate command `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` (prints `VERIFY PASSED`, exit code 0; otherwise `BUILD FAILED` or `TESTS FAILED` and a non-zero exit code), used before every later merge.

- [x] **Step 1: Run the gate before it exists**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: `The argument 'scripts/verify.ps1' to the -File parameter does not exist. Provide the path to an existing '.ps1' file as an argument to the -File parameter.`

- [x] **Step 2: Write `scripts/verify.ps1`**

The file is plain ASCII (Windows PowerShell 5.1 reads BOM-less files in the system code page) and is checked out with CRLF line endings (`.gitattributes`).

```powershell
# Local verification gate (replaces CI, see D-005). Run before every merge to main:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host '== Build (Release, warnings as errors) =='
dotnet build BEMGen.sln -c Release
if ($LASTEXITCODE -ne 0) { Write-Host 'BUILD FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host '== Test (net8.0) =='
dotnet test BEMGen.sln -c Release --no-build
if ($LASTEXITCODE -ne 0) { Write-Host 'TESTS FAILED' -ForegroundColor Red; exit $LASTEXITCODE }

Write-Host 'VERIFY PASSED' -ForegroundColor Green
```

- [x] **Step 3: Run the gate**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected (paths shortened):

```text
== Build (Release, warnings as errors) ==
  Lod.Core -> ...\src\Lod.Core\bin\Release\netstandard2.0\Lod.Core.dll
  Lod.Core.Tests -> ...\tests\Lod.Core.Tests\bin\Release\net8.0\Lod.Core.Tests.dll

Build succeeded.
    0 Warning(s)
    0 Error(s)
== Test (net8.0) ==
Passed!  - Failed:     0, Passed:     1, Skipped:     0, Total:     1, Duration: 7 ms - Lod.Core.Tests.dll (net8.0)
VERIFY PASSED
```

- [x] **Step 4: Prove that the gate blocks a warning, then revert**

Temporarily insert the line `        int unused;` as the first statement of `InformationalVersionStartsWithTheAssemblyVersion` in `tests/Lod.Core.Tests/Common/BuildInfoTests.cs` (above `Version version = ...`), then run:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: `error CS0168: The variable 'unused' is declared but never used` for `net8.0`, `Build FAILED.`, then the script's own `BUILD FAILED` line, and exit code 1 (`echo $?` in Git Bash, `$LASTEXITCODE` in PowerShell). Revert the change:

```bash
git restore tests/Lod.Core.Tests/Common/BuildInfoTests.cs
git status --short
```

Expected: `git status --short` lists only `?? scripts/`.

- [x] **Step 5: Commit the gate**

```bash
git add scripts/verify.ps1
git commit -m "build(repo): add local verification gate script"
```

- [x] **Step 6: Replace the "Project state" section of `AGENTS.md`**

Find this exact text:

```markdown
## Project state

The repository is pre-implementation: only documentation exists. There is no solution, build, or test command yet. When the first projects are added, record the exact build and test commands in the **Commands** section below in the same change.
```

Replace it with:

```markdown
## Project state

The solution exists: `BEMGen.sln` with `src/Lod.Core` (`netstandard2.0`) and `tests/Lod.Core.Tests` (`net8.0`); the toolchain is fixed in [ADR-001](docs/decisions/ADR-001-toolchain.md). The Grasshopper plugin project `src/Lod.Grasshopper` follows in the next S0 slice. Projects are added when a stage first needs them: `src/Lod.Generators`, `tests/Lod.Generators.Tests`, and `tests/Lod.Integration.Tests` arrive in S2, and `src/Lod.Export` with its tests in S6. Keep the **Commands** section below in sync with `scripts/verify.ps1` in the same change.
```

- [x] **Step 7: Replace the "Commands" section of `AGENTS.md`**

Find this exact text:

````markdown
## Commands

_None yet._ Expected shape once the solution exists:

```bash
dotnet build
dotnet test
```

Tests for `Lod.Core`, `Lod.Generators`, and `Lod.Export` must run with plain `dotnet test`, without Rhino or Grasshopper installed.
````

Replace it with:

````markdown
## Commands

Run from the repository root on Windows. Any .NET SDK 8 or later works (`global.json` rolls forward); Rhino is not needed to build or test.

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

- `dotnet build` treats warnings as errors, including `.editorconfig` style rules and missing XML documentation in `Lod.Core`.
- `dotnet test` runs every test project on `net8.0`. One test class: `dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.BuildInfoTests"`.
- `scripts/verify.ps1` is the local merge gate (D-005, no CI): Release build plus all tests. It prints `VERIFY PASSED` and must pass before every merge to `main`. It runs on Windows PowerShell 5.1; `pwsh` is not required.

Tests for `Lod.Core`, `Lod.Generators`, and `Lod.Export` must run with plain `dotnet test`, without Rhino or Grasshopper installed.
````

- [x] **Step 8: Commit the AGENTS.md update**

```bash
git diff --stat
git add AGENTS.md
git commit -m "docs(repo): record build, test, and verify commands in agents guide"
```

Expected from `git diff --stat`: only `AGENTS.md` changed.

- [ ] **Step 9: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only build/solution-skeleton
git push origin main
git branch -d build/solution-skeleton
```

Expected: `VERIFY PASSED` (1 test passed on `net8.0`), then `Fast-forward`. If `git merge --ff-only` refuses because `main` moved, switch back to the branch and repeat from `git fetch origin`.

---

## Slice C — `feature/grasshopper-plugin-shell`

### Task 10: Plugin shell with the BEMGen Info component

**Files:** Create `src/Lod.Grasshopper/Lod.Grasshopper.csproj`, `src/Lod.Grasshopper/BemGenAssemblyInfo.cs`, `src/Lod.Grasshopper/ComponentCategories.cs`, `src/Lod.Grasshopper/Components/BemGenInfoComponent.cs`, `src/Lod.Grasshopper/Properties/launchSettings.json`; Modify `BEMGen.sln`
**Interfaces:** Consumes: `Lod.Core.Common.BuildInfo.InformationalVersion` (Task 8). / Produces: `internal static class ComponentCategories` with `Category = "BEMGen"` and panel constants `Info = "0 Info"`, `Program = "1 Program"`, `Generate = "2 Generate"`, `Simplify = "3 Simplify"`, `Aggregate = "4 Aggregate"`, `Convert = "5 Convert"`, `Inspect = "6 Inspect"` (used by every later component); plugin GUID `6f0f5d0e-2a8b-4c55-9a51-0a7b3d2c9e41`; component GUID `b1d4f0a2-6c3e-4f7a-8e21-5a9c0d7e3b14`. Both GUIDs are permanent once merged.

Grasshopper code cannot be unit tested without Rhino; this task is "write code, build with 0 warnings, commit", and Task 11 adds the manual check.

- [x] **Step 1: Create the slice branch**

```bash
git switch main
git pull --ff-only
git switch -c feature/grasshopper-plugin-shell main
```

- [x] **Step 2: Write `src/Lod.Grasshopper/Lod.Grasshopper.csproj` (S0 version: references `Lod.Core` only)**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net7.0</TargetFramework>
    <AssemblyName>BEMGen</AssemblyName>
    <RootNamespace>Lod.Grasshopper</RootNamespace>
    <TargetExt>.gha</TargetExt>
    <EnableDynamicLoading>true</EnableDynamicLoading>
    <!-- Rhino 8 loads net7.0 plugins on its .NET 8 runtime; net7.0 is end-of-life for the SDK but required by RhinoCommon 8. -->
    <CheckEolTargetFramework>false</CheckEolTargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="RhinoCommon" ExcludeAssets="runtime" />
    <PackageReference Include="Grasshopper" ExcludeAssets="runtime" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\Lod.Core\Lod.Core.csproj" />
  </ItemGroup>

</Project>
```

- [x] **Step 3: Write `src/Lod.Grasshopper/BemGenAssemblyInfo.cs`**

```csharp
using System;
using System.Drawing;
using Grasshopper.Kernel;
using Lod.Core.Common;

namespace Lod.Grasshopper;

public sealed class BemGenAssemblyInfo : GH_AssemblyInfo
{
    public override string Name => "BEMGen";

    public override Bitmap? Icon => null;

    public override string Description => "Parametric residential plans and LoD simplification for building energy models.";

    public override Guid Id => new("6f0f5d0e-2a8b-4c55-9a51-0a7b3d2c9e41");

    public override string AuthorName => "Environmental Systems Lab, Cornell University";

    public override string AuthorContact => "https://github.com/EnvironmentalSystemsLab/BEMGen";

    public override string AssemblyVersion => BuildInfo.InformationalVersion;
}
```

- [x] **Step 4: Write `src/Lod.Grasshopper/ComponentCategories.cs`**

It already lists the panels of later stages; the numeric prefixes keep Grasshopper's alphabetical panel order aligned with the pipeline.

```csharp
namespace Lod.Grasshopper;

/// <summary>Toolbar tab and panels, ordered along the pipeline.</summary>
internal static class ComponentCategories
{
    public const string Category = "BEMGen";

    public const string Info = "0 Info";

    public const string Program = "1 Program";

    public const string Generate = "2 Generate";

    public const string Simplify = "3 Simplify";

    public const string Aggregate = "4 Aggregate";

    public const string Convert = "5 Convert";

    public const string Inspect = "6 Inspect";
}
```

- [x] **Step 5: Write `src/Lod.Grasshopper/Components/BemGenInfoComponent.cs`**

```csharp
using System;
using System.Drawing;
using Grasshopper.Kernel;
using Lod.Core.Common;

namespace Lod.Grasshopper.Components;

public sealed class BemGenInfoComponent : GH_Component
{
    public BemGenInfoComponent()
        : base("BEMGen Info", "Info", "Version of the loaded BEMGen plugin, including the commit it was built from.", ComponentCategories.Category, ComponentCategories.Info)
    {
    }

    public override Guid ComponentGuid => new("b1d4f0a2-6c3e-4f7a-8e21-5a9c0d7e3b14");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddTextParameter("Version", "V", "Informational version; the part after '+' is the commit SHA.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        DA.SetData(0, BuildInfo.InformationalVersion);
    }
}
```

- [x] **Step 6: Write `src/Lod.Grasshopper/Properties/launchSettings.json`**

Launch profile for Visual Studio and Rider (D-052, D-053). It starts Rhino 8 in its default .NET Core runtime (`/netcore`), runs the `Grasshopper` command, and points `RHINO_PACKAGE_DIRS` at the `net7.0` build folder, so Rhino loads the plugin from there without a library-folder setting. `executablePath` is Rhino's default install location; a different location is changed locally and not committed. The SDK does not copy this file to the build output.

```json
{
  "profiles": {
    "Rhino 8 (.NET Core)": {
      "commandName": "Executable",
      "executablePath": "C:\\Program Files\\Rhino 8\\System\\Rhino.exe",
      "commandLineArgs": "/netcore /runscript=\"_Grasshopper\"",
      "environmentVariables": {
        "RHINO_PACKAGE_DIRS": "$(ProjectDir)bin\\$(Configuration)\\net7.0\\"
      }
    }
  }
}
```

- [x] **Step 7: Add the project to the solution**

```bash
dotnet sln BEMGen.sln add src/Lod.Grasshopper/Lod.Grasshopper.csproj
```

Expected: ``Project `src\Lod.Grasshopper\Lod.Grasshopper.csproj` added to the solution.``

- [x] **Step 8: Build the plugin with 0 warnings**

```bash
dotnet build src/Lod.Grasshopper -c Release
```

Expected (paths shortened):

```text
  Lod.Core -> ...\src\Lod.Core\bin\Release\netstandard2.0\Lod.Core.dll
  Lod.Grasshopper -> ...\src\Lod.Grasshopper\bin\Release\net7.0\BEMGen.gha

Build succeeded.
    0 Warning(s)
    0 Error(s)
```

- [x] **Step 9: Check the output folder**

```bash
ls src/Lod.Grasshopper/bin/Release/net7.0
```

Expected: `net7.0` contains exactly `BEMGen.deps.json`, `BEMGen.gha`, `BEMGen.pdb`, `BEMGen.runtimeconfig.json`, `Lod.Core.dll`, `Lod.Core.pdb`, `Lod.Core.xml`. It does not contain `RhinoCommon.dll` or `Grasshopper.dll` (`ExcludeAssets="runtime"`; Rhino supplies them).

- [x] **Step 10: Run the gate**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: the build lists `Lod.Core`, `BEMGen.gha`, and `Lod.Core.Tests.dll` with `0 Warning(s)`; then `Passed!` with `Passed:     1` for `Lod.Core.Tests.dll (net8.0)`; then `VERIFY PASSED`.

- [x] **Step 11: Commit**

```bash
git status --porcelain -uall
git add BEMGen.sln src/Lod.Grasshopper/Lod.Grasshopper.csproj src/Lod.Grasshopper/BemGenAssemblyInfo.cs src/Lod.Grasshopper/ComponentCategories.cs src/Lod.Grasshopper/Components/BemGenInfoComponent.cs src/Lod.Grasshopper/Properties/launchSettings.json
git commit -m "feature(grasshopper): add plugin shell with bemgen info component"
```

Expected from `git status --porcelain -uall` before adding: ` M BEMGen.sln` and the five `src/Lod.Grasshopper/...` files, nothing under `bin/` or `obj/`.

### Task 11: Smoke-test guide and the manual Rhino check

**Files:** Create `docs/development/grasshopper-smoke-test.md`
**Interfaces:** Consumes: the plugin from Task 10. / Produces: the "Stage checklists" section that S2, S3, and S4 append to, and the recording rule used by every stage close-out.

- [x] **Step 1: Write `docs/development/grasshopper-smoke-test.md`**

````markdown
# Grasshopper smoke test

A manual check that the BEMGen plugin loads in Rhino and its components work. Grasshopper code cannot be unit tested without Rhino (roadmap §6), so **a person** performs this check at the end of every stage that changes `Lod.Grasshopper`; an agent cannot. Each such stage appends its checklist under [Stage checklists](#stage-checklists).

## Requirements

- Windows with Rhino 8.19 or later (ADR-001). Check the version with Rhino's `About` command (Help > About Rhinoceros).
- A Release build from a git checkout whose changes are committed, so that the version shown identifies the code under test. From the repository root:

```bash
dotnet build BEMGen.sln -c Release
git rev-parse HEAD
```

Note the SHA that `git rev-parse HEAD` prints.

The build produces one plugin, for Rhino's .NET Core runtime:

| Rhino runtime | Build folder |
| --- | --- |
| .NET Core (Rhino 8 default) | `src/Lod.Grasshopper/bin/Release/net7.0/` |

The folder contains `BEMGen.gha` and `Lod.Core.dll` (with `.pdb` files, `Lod.Core.xml`, `BEMGen.deps.json`, and `BEMGen.runtimeconfig.json`). It never contains `RhinoCommon.dll` or `Grasshopper.dll`; Rhino supplies them.

## Load the plugin

Close Rhino before building or copying files: Grasshopper loads plugins only when it starts.

Use one of the methods below with one build folder only. Two copies of `BEMGen.gha` would register the same component GUIDs twice.

### Option A: add the build folder as a library folder (recommended during development)

1. Start Rhino and run the command `GrasshopperDeveloperSettings`.
2. Add the absolute path of the build folder (`<repository>\src\Lod.Grasshopper\bin\Release\net7.0`) to the library folders and confirm.
3. Restart Rhino. Later builds into the same folder are picked up at the next start.

### Option B: copy the build to the Grasshopper libraries folder

1. Create the folder `%APPDATA%\Grasshopper\Libraries\BEMGen\`.
2. Copy the contents of the build folder into it.
3. If the files were downloaded (for example as a zip) rather than built on this machine, unblock them: right-click each file, choose Properties, and tick Unblock; or run in PowerShell:

   ```powershell
   Get-ChildItem "$env:APPDATA\Grasshopper\Libraries\BEMGen" -Recurse | Unblock-File
   ```

   Windows marks downloaded files as blocked, and blocked plugin files may fail to load.
4. Restart Rhino.

### Option C: start Rhino from the IDE with a launch profile

`src/Lod.Grasshopper/Properties/launchSettings.json` defines one launch profile for Visual Studio and Rider, **Rhino 8 (.NET Core)** (D-052, D-053). It starts Rhino from its default install location (`C:\Program Files\Rhino 8\System\Rhino.exe`) in the .NET Core runtime, runs the `Grasshopper` command, and sets `RHINO_PACKAGE_DIRS` to the build folder (`bin\<configuration>\net7.0\`), so Rhino loads the plugin from there without a library-folder setting.

1. If Option A or B was used before, remove the build folder from the library folders and delete `%APPDATA%\Grasshopper\Libraries\BEMGen\`.
2. Select `Lod.Grasshopper` as the startup project, choose the Release configuration (the build that [Requirements](#requirements) describes), and choose the **Rhino 8 (.NET Core)** profile.
3. Start it. The IDE builds first, then starts Rhino with Grasshopper.

If Rhino is installed elsewhere, change `executablePath` locally and do not commit the change.

### Rhino runtime

BEMGen loads only in Rhino's .NET Core runtime, the Rhino 8 default (D-053); there is no build for the .NET Framework runtime. If Rhino was switched to .NET Framework with the `SetDotNetRuntime` command, switch it back to .NET Core the same way and restart Rhino before loading BEMGen. The Option C profile always starts Rhino in .NET Core.

## Run the check

1. Start Rhino and run the `Grasshopper` command.
2. Work through the checklist of the stage under test, ticking each item.
3. Record the result as described below.

## Recording the result

Rebase merges (D-004) create no merge commit, so the result goes into the body of the stage close-out commit: who tested and when, the Rhino version and runtime, the SHA that was built, the version text shown by *BEMGen Info*, and pass or fail for each checklist item. A failed item blocks the stage close-out until it is fixed.

## Stage checklists

### S0 — Plugin shell

Build: the commit being closed out. Runtime: .NET Core (the Rhino 8 default).

Component under test:

| Component | Tab / panel | Inputs | Outputs | GUID |
| --- | --- | --- | --- | --- |
| BEMGen Info (nickname `Info`) | BEMGen / 0 Info | none | Version (`V`, text): the informational version; the part after `+` is the commit SHA | `b1d4f0a2-6c3e-4f7a-8e21-5a9c0d7e3b14` |

- [ ] Rhino reports version 8.19 or later.
- [ ] Grasshopper starts without an error message about BEMGen or `BEMGen.gha`.
- [ ] The component toolbar has a **BEMGen** tab with a panel **0 Info**.
- [ ] **BEMGen Info** can be placed from that panel. It has no inputs and one output, **Version** (`V`), and shows Grasshopper's generic icon (icons arrive in S9).
- [ ] The placed component shows no warning or error (it is neither orange nor red).
- [ ] A Panel connected to **Version** shows text that starts with `0.0.1`.
- [ ] The text after `+` equals the SHA printed by `git rev-parse HEAD` for the build.
````

- [x] **Step 2: Commit the guide**

```bash
git status --short
git add docs/development/grasshopper-smoke-test.md
git commit -m "docs(grasshopper): add plugin smoke-test guide with s0 checklist"
```

Expected from `git status --short`: `?? docs/development/`.

- [x] **Step 3: Manual (person): perform the S0 checklist**

On a machine with Rhino 8.19 or later, build this branch (`dotnet build BEMGen.sln -c Release`), load the `net7.0` build as described in `docs/development/grasshopper-smoke-test.md`, and work through the S0 checklist. Write down: tester, date, Rhino version, runtime, the SHA from `git rev-parse HEAD`, the exact text of the **Version** output, and pass/fail per item. These values go into the close-out commit (Task 12). If an item fails, fix it on this branch (new commit, `dotnet build` with 0 warnings) and repeat the checklist before merging.

- [ ] **Step 4: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/grasshopper-plugin-shell
git push origin main
git branch -d feature/grasshopper-plugin-shell
```

Expected: `VERIFY PASSED`, then `Fast-forward`. If `git rebase` rewrote commits because `main` had moved, the tested SHA differs from the merged one; record both in the close-out commit.

---

## Stage close-out

### Task 12: S0 close-out, decision log, and tag

**Files:** Modify `AGENTS.md` ("Project state"), `README.md` ("Status"), `docs/plans/2026-09-30-implementation-roadmap.md` (progress line), `docs/decisions/decision-log.md` (D-042), `docs/plans/2026-10-01-s0-foundation.md` (status); `Directory.Build.props` unchanged (S0 keeps version 0.0.1)
**Interfaces:** Consumes: all S0 slices merged; the smoke-test record from Task 11 Step 3. / Produces: tag `v0.0.1`; decision-log entry D-042 (D-043 and D-044 are reserved for the S3 and S4 plans).

The texts below are dated 2026-10-01. If the close-out happens on a later day, use that day's date in the roadmap progress line and in the D-042 entry.

- [x] **Step 1: Create the close-out branch and run the gate**

```bash
git switch main
git pull --ff-only
git switch -c docs/repo-s0-close-out main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: `VERIFY PASSED`, with `Passed:     1` for `Lod.Core.Tests.dll (net8.0)`.

- [x] **Step 2: Confirm the version**

S0's version stays 0.0.1, so `Directory.Build.props` is not changed. `BuildInfoTests` compares the informational version with the assembly version, so it passes for any version.

```bash
git grep -n "<Version>" Directory.Build.props
```

Expected: `Directory.Build.props:9:    <Version>0.0.1</Version>`

- [x] **Step 3: Replace the "Project state" section of `AGENTS.md`**

Find this exact text (written in Task 9):

```markdown
## Project state

The solution exists: `BEMGen.sln` with `src/Lod.Core` (`netstandard2.0`) and `tests/Lod.Core.Tests` (`net8.0`); the toolchain is fixed in [ADR-001](docs/decisions/ADR-001-toolchain.md). The Grasshopper plugin project `src/Lod.Grasshopper` follows in the next S0 slice. Projects are added when a stage first needs them: `src/Lod.Generators`, `tests/Lod.Generators.Tests`, and `tests/Lod.Integration.Tests` arrive in S2, and `src/Lod.Export` with its tests in S6. Keep the **Commands** section below in sync with `scripts/verify.ps1` in the same change.
```

Replace it with:

```markdown
## Project state

S0 (Foundation) is complete (tag `v0.0.1`); next is S1, program presets and the equivalence engine. `BEMGen.sln` contains `src/Lod.Core` (`netstandard2.0`), `src/Lod.Grasshopper` (the plugin `BEMGen.gha` for Rhino 8.19 or later, `net7.0`), and `tests/Lod.Core.Tests` (`net8.0`). Toolchain, geometry, schedules, tolerances, conditioning and setpoint aggregation, and load-basis aggregation are fixed in ADR-001 to ADR-005 and ADR-007 in `docs/decisions/`. Projects are added when a stage first needs them: `src/Lod.Generators`, `tests/Lod.Generators.Tests`, and `tests/Lod.Integration.Tests` arrive in S2, and `src/Lod.Export` with its tests in S6. Manual checks in Rhino follow [docs/development/grasshopper-smoke-test.md](docs/development/grasshopper-smoke-test.md). Keep the **Commands** section below in sync with `scripts/verify.ps1` in the same change.
```

The "Commands" section written in Task 9 stays as it is.

- [x] **Step 4: Replace the "Status" paragraph of `README.md`**

Find this exact text (the paragraph under `## Status`):

```markdown
Pre-implementation. The repository currently holds the research brief and the repository specification; no code has been written yet. Work proceeds in the stages of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) (derived from the spec's milestones), starting with Stage 0 (foundation). Target: Rhino 8; downstream energy modelling is provisionally ClimateStudio in Grasshopper.
```

Replace it with:

```markdown
S0 (Foundation) is complete (tag `v0.0.1`): the solution builds and passes `scripts/verify.ps1`, and the Grasshopper plugin loads in Rhino 8.19 or later with a *BEMGen Info* component that shows the plugin version and commit. The foundation decisions are recorded in ADR-001 to ADR-005 and ADR-007 in [docs/decisions](docs/decisions/). Next: S1, program presets and the equivalence engine. Work proceeds in the stages of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md). Target: Rhino 8.19 or later; downstream energy modelling is provisionally ClimateStudio in Grasshopper.
```

- [x] **Step 5: Add the dated progress line to the roadmap**

In `docs/plans/2026-09-30-implementation-roadmap.md`, find this exact text (lines 5 and 6):

```markdown
> **Checkpoint 1:** completion of S0–S4 (D-030).
>
```

Replace it with:

```markdown
> **Checkpoint 1:** completion of S0–S4 (D-030).
>
> **Progress:** 2026-10-01 · S0 Foundation complete (tag `v0.0.1`); next: S1. ADR-001 and ADR-004 ratify the tech stack and tolerances listed in this roadmap: C# 12 rather than the latest language version, no System.Collections.Immutable, minimum Rhino 8.19, relative area tolerance 1e-6, and the verify gate on Windows PowerShell 5.1 (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1`).
>
```

- [x] **Step 6: Append D-042 to `docs/decisions/decision-log.md`**

Append at the end of the file, after the last entry (`### D-041 — Façade coverage is an enforced invariant`), separated by one blank line. D-035 to D-037 are not used, D-038 to D-041 are taken, and D-043 and D-044 are reserved for the S3 and S4 plans, so this entry is D-042. If other entries have been added after D-041 in the meantime, check that D-042 is still free before appending.

```markdown
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
```

- [x] **Step 7: Mark this plan as done**

In `docs/plans/2026-10-01-s0-foundation.md`, change the status value in the first line of the header block (currently `Draft for review`, `Approved`, or `In progress`) to `Done`, keeping the rest of the line:

```markdown
> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S0](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
```

- [x] **Step 8: Run the gate and review the diff**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git diff --stat
```

Expected: `VERIFY PASSED`; the diff lists exactly `AGENTS.md`, `README.md`, `docs/decisions/decision-log.md`, `docs/plans/2026-09-30-implementation-roadmap.md`, and `docs/plans/2026-10-01-s0-foundation.md`.

- [x] **Step 9: Commit with the smoke-test record**

Replace every angle-bracket field with the values observed in Task 11 Step 3 (they are records of the manual check, not placeholders to keep):

```bash
git add AGENTS.md README.md docs/decisions/decision-log.md docs/plans/2026-09-30-implementation-roadmap.md docs/plans/2026-10-01-s0-foundation.md
git commit -m "docs(repo): close out s0 foundation" -m "S0 exit criteria: verify.ps1 passes; ADR-001 to ADR-005 and ADR-007 accepted; research brief sections 7, 9, and 10 updated; D-042 recorded." -m "Smoke test (docs/development/grasshopper-smoke-test.md, S0 checklist) by <tester> on <date>: Rhino <version>, .NET Core runtime, build <sha>, Version output '<version text>', all items passed."
```

- [ ] **Step 10: Merge the close-out branch (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only docs/repo-s0-close-out
git push origin main
git branch -d docs/repo-s0-close-out
```

Expected: `VERIFY PASSED`, then `Fast-forward`.

- [ ] **Step 11: Verify on a clean clone**

```bash
git clone https://github.com/EnvironmentalSystemsLab/BEMGen.git ../BEMGen-clean-clone
powershell -NoProfile -ExecutionPolicy Bypass -File ../BEMGen-clean-clone/scripts/verify.ps1
```

Expected: `VERIFY PASSED` (the script changes to its own repository root, so it builds the clone). Then delete the `../BEMGen-clean-clone` folder (for example `rm -rf ../BEMGen-clean-clone` in Git Bash). Do not tag if this fails.

- [ ] **Step 12: Tag the stage**

```bash
git switch main
git tag -a v0.0.1 -m "S0 Foundation complete"
git push origin v0.0.1
```

Expected: `git show v0.0.1 --stat` shows the close-out commit; the tag exists on `origin`.

## Exit criteria (copied from the roadmap, refined)

- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` prints `VERIFY PASSED` on a fresh clone of `main`: Release build with 0 warnings, `Lod.Core.Tests` 1 passed on `net8.0` (Task 12 Step 11).
- [x] The plugin loads in Rhino 8.19 or later (.NET Core runtime, the Rhino 8 default), and *BEMGen Info* shows a version that starts with `0.0.1` and ends with the built commit's SHA; the result is recorded in the close-out commit body (Task 11 Step 3, Task 12 Step 9).
- [x] ADR-001 to ADR-005 and ADR-007 exist in `docs/decisions/` with `Status: Accepted`, and D-042 records them in the decision log.
- [x] The research brief §7, §9, and §10 contain their "Rule adopted for this project" paragraphs.
- [ ] `AGENTS.md` "Project state" and "Commands", the README "Status", and the roadmap progress line describe the S0 state; tag `v0.0.1` is pushed.

## Notes for the reviewer

1. **Clipper2 already in `Directory.Packages.props`.** The verified S0 file pins `Clipper2 2.0.0` although no project references it until S2. It is kept verbatim; an unused central `PackageVersion` produces no warning (the S0 build has 0 warnings). ADR-001 states that the version is pinned from S0 and first referenced in S2.
2. **Test-first order in Task 8.** The test files are written first, but the build infrastructure and an empty `Lod.Core` project must exist before the test can fail on the missing type. The verified failing output is `error CS0234: The type or namespace name 'Common' does not exist in the namespace 'Lod.Core'` (the `using` directive fails first; no CS0246 is reported), on SDK 10.0.401.
3. **Slice A has no gate.** `scripts/verify.ps1` arrives in Slice B, so Slice A's D-004 merge replaces the gate with a docs-only diff check (Task 7 Step 4). Doing Slice B first would avoid this but contradicts the stage outline.
4. **Revision after plan review (D-038 to D-041).** ADR-002 now records explicit windows and their unchanged re-hosting through simplification (W0, D-039); the centered √(glazed area / wall area) rule is only the first generator's placement rule (`Window.Centered`), and the rejected option "centered windows only at every LoD" (former D-022) is listed. ADR-005 became "Conditioning and setpoint aggregation" (D-038) and its file is now `ADR-005-conditioning-and-setpoints.md`; no other document links the old file name. ADR-007 and the research brief §9 add the façade-coverage precondition (D-041), and ADR-004 lists façade coverage lengths under `RelativeArea`. The research brief §7 and §10 paragraphs are rewritten. Stage references follow the D-039 renumbering: S5 window transformations (ADR-012), S6 Convert2IDF, S7 precedent study (ADR-006), S8 typologies (ADR-011, perimeter/core with holes), S9 UX and release.
5. **Roadmap v3 and the progress line.** Roadmap v3 already lists C# 12, no System.Collections.Immutable, Rhino 8.19 or later, relative area tolerance 1e-6, and the `powershell` gate command. The progress line therefore says that ADR-001 and ADR-004 ratify these values instead of superseding the roadmap, and the ADRs call the earlier values proposals of roadmap v1 and v2. Creating only `Lod.Core`, `Lod.Core.Tests`, and `Lod.Grasshopper` in S0 matches roadmap v3 ("Further projects are created by the stage that first needs them").
6. **Tolerance overrides.** ADR-004 requires non-default tolerances to be recorded in provenance. In the S4 code every component uses `ToleranceSettings.Default` and `Provenance` records no tolerances; there is no override path, so the rule holds vacuously. A future tolerance input must implement the recording with it.
7. **Decision-log numbering.** The S0 close-out adds D-042, following the allocation in the stage brief: D-035 to D-037 are unused, D-038 to D-041 are taken, D-043 is reserved for S3 (ADR-008) and D-044 for S4. Task 12 Step 6 tells the executor to confirm that D-042 is still free.
8. **Window bounds are not checked by the wall type.** ADR-002 states that the operations that create or re-host windows keep every window within its wall. In the S2 code, `Window.At` rejects only negative offsets or sills and non-positive sizes, and the `WallSurface` constructor does not check that windows fit the wall or do not overlap; `Window.Centered` and `WindowRehosting` guarantee the fit. ADR-012 (S5) or ADR-011 (S8) could make this an explicit check.
9. **Unverified Rhino UI details.** The commands `GrasshopperDeveloperSettings` and `SetDotNetRuntime` come from the stage brief; the exact labels inside their dialogs were not checked, so the smoke-test guide describes them generically. When the plan was written, the plugin had not yet been loaded in Rhino; that is the manual step in Task 11, which first passed on 2026-10-01 (Rhino 8.25, .NET Core runtime).
10. **Small zones and `RelativeArea`.** The 1e-6 justification uses 10 m zones (brief and ADR-004). For much smaller zones, worst-case rounding approaches the tolerance; the S3 tests on the linear plan are the evidence that 1e-6 suffices in practice.
11. **Public Grasshopper types without XML docs.** `BemGenAssemblyInfo` and `BemGenInfoComponent` have no XML comments. This builds because only `Lod.Core` (and later `Lod.Generators`) set `GenerateDocumentationFile`; AGENTS.md's code-style line asks for XML docs on public APIs, so a reviewer may want this stated as an accepted exception for component classes.
12. **Revision after plan review (D-047).** ADR-007 and the research brief §9 now aggregate loads per component (load type and basis): mixed bases are no longer an error, components of one type add up, and design occupants are the sum of the occupancy components. The ADR lists the per-component option as adopted and rejecting or converting mixed bases as rejected, and gains a mixed-basis worked example. The S0 code is unchanged; the research brief insertion is still 8 lines.
13. **Launch profile added during execution (D-052).** `src/Lod.Grasshopper/Properties/launchSettings.json` (Task 10 Step 6) and the smoke-test guide's Option C were added after the handoff, at the person's request, when Tasks 10 and 11 had already been committed; in that execution they arrived as follow-up commits on the plugin-shell slice. The reference archive was updated to match (the file is in `reference/S0` to `reference/S4` and in `stage_manifest.py`'s S0 list). The file first held a second profile for the .NET Framework runtime, removed with that target (D-053, note 14); the remaining **Rhino 8 (.NET Core)** profile relies on Rhino 8's `/netcore` and `/runscript` start-up switches and on `RHINO_PACKAGE_DIRS`, and on the IDE expanding `$(ProjectDir)` and `$(Configuration)` in launch settings (Visual Studio and Rider do; `dotnet run` does not run `Executable` profiles). It is first exercised in the Task 11 manual check.
14. **`net48` dropped after the S0 smoke test (D-053).** After the S0 plugin passed the smoke test in Rhino 8's default .NET Core runtime, the person decided to drop the .NET Framework 4.8 target. Changed in this plan and in the reference archive (`reference/S0` to `reference/S4`, rebuilt with the same test counts): `Lod.Grasshopper.csproj` targets `net7.0` only (`<TargetFramework>`, singular; `CheckEolTargetFramework` stays false) and `Lod.Core.Tests.csproj` `net8.0` only; the `Directory.Build.props` polyfill comment names only `netstandard2.0`; the `verify.ps1` test header is `== Test (net8.0) ==`; `launchSettings.json` keeps only the **Rhino 8 (.NET Core)** profile. ADR-001 is revised in place, which is allowed because it is accepted only at the S0 close-out: `net7.0;net48` is a rejected option, `netstandard2.0` for the core libraries is justified by the `net7.0` plugin and the `net8.0` tests, and the consequences state that a Rhino switched to .NET Framework with `SetDotNetRuntime` cannot load BEMGen. The expected build and test outputs, the smoke-test guide (build-folder table, Option C, Rhino runtime, S0 checklist), the AGENTS.md texts, D-042, the close-out commit template, and the exit criteria lose their `net48` parts. Unchanged: core libraries on `netstandard2.0` with the `IsExternalInit` polyfill and its `Directory.Build.props` link, no System.Collections.Immutable, and every test count, now reported for `net8.0` only.
