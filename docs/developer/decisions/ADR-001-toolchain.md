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
