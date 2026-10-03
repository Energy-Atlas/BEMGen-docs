# S1 — Program presets and equivalence engine Implementation Plan

> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S1](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validated schedules, loads, zone programs (conditioned with a thermostat, or unconditioned), and program presets, plus an equivalent-property aggregator whose conservation of installed and hourly scheduled load magnitudes (people, W, m³/h) and whose conditioning and floor-area setpoint rules are proven by tests before any geometry exists.

**Architecture:** All S1 code is plain C# in `Lod.Core` (`netstandard2.0`, BCL only) under the namespaces `Common`, `Schedules`, `Loads`, `Programs`, and `Aggregation`, tested by `Lod.Core.Tests` on `net8.0` without Rhino. The aggregator is a service behind `IEquivalentPropertyAggregator` that receives the target's measures and one `SourceZoneContribution` per source (with transfer fractions supplied by the caller), so it is independent of geometry and of any rezoning method; it returns an ordinary `ZoneProgram` whose derived loads and schedules carry `AggregationRecord`s. Expected failures are `Result<T>` values with structured `Diagnostic`s.

**Tech Stack:** C# 12 (`LangVersion` 12.0) · `Lod.Core` on `netstandard2.0` with no package references · tests on `net8.0` (ADR-001, D-053) with xUnit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1 · any .NET SDK ≥ 8 (`global.json` pins 8.0.100 with `rollForward: latestMajor`) · Windows PowerShell 5.1 for `scripts/verify.ps1` · no new packages in S1 (Clipper2 2.0.0 is first referenced in S2; RhinoCommon/Grasshopper 8.19.25132.1001 stay confined to the unchanged `Lod.Grasshopper`).

## Global Constraints

- Rhino 8 only (D-003); `Lod.Core` has no RhinoCommon or Grasshopper reference and its tests run with plain `dotnet test` (GLOBAL.md architecture rules 1–2).
- Nullable reference types on, warnings are errors, `EnforceCodeStyleInBuild` on: an `.editorconfig` rule at warning severity fails the build.
- `GenerateDocumentationFile` is on for `Lod.Core`: every public type and member needs XML docs (CS1591 is an error) and every `cref` must resolve.
- Numerical tolerances live only in `ToleranceSettings` (GLOBAL.md quality rule 4, ADR-004); tests compare through `ToleranceSettings.Default`.
- Expected failures return `Result<T>` with `Diagnostic`s and stable codes from `DiagnosticCodes`; exceptions are for programming errors only (GLOBAL.md quality rule 5).
- Immutability: private arrays exposed as `IReadOnlyList<T>` via `Array.AsReadOnly`; no `System.Collections.Immutable` (Rhino 8 ships its own copy, and a core library referencing another version risks assembly conflicts inside Rhino).
- Determinism: no global random state; property tests use `new System.Random(seed)` with explicit seeds; outputs ordered by `LoadType` (then `LoadBasis`) and `SpaceType` (GLOBAL.md quality rule 3).
- Loads aggregate by conserving transferred design magnitude (ADR-007), separately for each load type and basis (D-047); air-change loads are volume weighted (D-019).
- Conditioning comes from the program preset: a conditioned program has a `Thermostat`, an unconditioned one has none and therefore no setpoints. A target zone is conditioned if any source contributing floor area is ("any conditioned wins"); its setpoints are floor-area weighted over those conditioned sources only, a prescribed control rule, not a conservation invariant (D-038, ADR-005).
- Every derived load and schedule records sources, method, and weights (GLOBAL.md scientific rule 2).
- `ExampleResidentialPresets` hold illustrative round numbers, not DOE prototype values, and which spaces are conditioned is illustrative too (stair unconditioned); sourcing DOE values is an open research input (roadmap §7, open point 4; documented in Task 7).
- Never widen a tolerance or relax a validation to make a test pass (AGENTS.md working rule 12).
- Commits: `type(scope): imperative summary in lower case`, no Co-Authored-By, no agent/model/tool names, no attribution (D-001, D-002). One branch per slice, rebase-merged after `scripts/verify.ps1` passes (D-004, D-005).
- Touch only the files listed in each task (AGENTS.md working rule 7). Source files are UTF-8 without BOM, LF line endings, final newline (`.editorconfig`).

## Files

| Path | Created / modified | Responsibility |
| --- | --- | --- |
| `src/Lod.Core/Common/ToleranceSettings.cs` | Created (Task 1) | Central tolerances and comparison helpers (ADR-004) |
| `src/Lod.Core/Common/Diagnostic.cs` | Created (Task 2) | `DiagnosticSeverity`, `Diagnostic` |
| `src/Lod.Core/Common/DiagnosticCodes.cs` | Created (Task 2) | Stable diagnostic codes, complete S1 set (16 codes) |
| `src/Lod.Core/Common/Result.cs` | Created (Task 2) | `Result<T>` and the `Result` factory |
| `src/Lod.Core/Common/Ids.cs` | Created (Task 2) | `ZoneId` |
| `src/Lod.Core/Aggregation/AggregationRecord.cs` | Created (Task 3) | `AggregationMethod`, `AggregationRecord` (traceability) |
| `src/Lod.Core/Schedules/Schedule.cs` | Created (Task 3) | `ScheduleKind`, immutable 8760-hour `Schedule` (ADR-003) |
| `src/Lod.Core/Loads/LoadDefinition.cs` | Created (Task 4) | `LoadType`, `LoadBasis`, `LoadDefinition` |
| `src/Lod.Core/Programs/ZoneProgram.cs` | Created (Task 5) | `SpaceType`, `Thermostat`, `ZoneProgram` (D-038, D-047) |
| `src/Lod.Core/Programs/ProgramPreset.cs` | Created (Task 6) | `ProgramPreset`, `ProgramPresetSet` (D-024, D-026) |
| `src/Lod.Core/Programs/ExampleResidentialPresets.cs` | Created (Task 6) | Illustrative dwelling-unit, corridor, and stair presets |
| `src/Lod.Core/Aggregation/ZoneMeasures.cs` | Created (Task 8) | `ZoneMeasures`, `SourceZoneContribution` |
| `src/Lod.Core/Aggregation/IEquivalentPropertyAggregator.cs` | Created (Task 8) | Aggregator interface |
| `src/Lod.Core/Aggregation/DesignMagnitudes.cs` | Created (Task 8) | Value ↔ design magnitude conversion (ADR-007) |
| `src/Lod.Core/Aggregation/EquivalentPropertyAggregator.cs` | Created (Task 8) | Load (ADR-007, per load type and basis, D-047), conditioning, and setpoint (ADR-005, D-038) aggregation |
| `tests/Lod.Core.Tests/Common/ToleranceSettingsTests.cs` | Created (Task 1) | Tolerance defaults and comparisons |
| `tests/Lod.Core.Tests/Common/ResultTests.cs` | Created (Task 2) | Result success/failure rules |
| `tests/Lod.Core.Tests/Aggregation/AggregationRecordTests.cs` | Created (Task 3) | Aggregation record alignment and count check |
| `tests/Lod.Core.Tests/Schedules/ScheduleTests.cs` | Created (Task 3) | Schedule validation, immutability, daily profiles |
| `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs` | Created (Task 4), modified (Task 5) | Test builders for schedules, loads, programs |
| `tests/Lod.Core.Tests/Programs/ProgramTests.cs` | Created (Task 4), modified (Tasks 5, 6) | Load, thermostat, program, preset validation |
| `tests/Lod.Core.Tests/Aggregation/EquivalentPropertyAggregatorTests.cs` | Created (Task 8) | Aggregation and conditioning rules, edge cases, seeded property tests |
| `docs/research/program-presets.md` | Created (Task 7) | What a preset is, conditioning, example values, open DOE sourcing, assumptions not reproduced |
| `docs/architecture/domain-model.md` | Created (Task 9) | S1 domain types, conditioning rule, units, immutability, traceability |
| `Directory.Build.props` | Modified (close-out) | `<Version>` 0.0.1 → 0.1.0 |
| `AGENTS.md` | Modified (close-out) | "Project state" |
| `README.md` | Modified (close-out) | "Status" |
| `docs/plans/2026-09-30-implementation-roadmap.md` | Modified (close-out) | S1 progress line in the header |

## Conventions used in this plan

- Run every command from the repository root `C:\github\BEMGen`. Commands are one per line and work in Git Bash or PowerShell.
- A "red" run fails at compile time. The expected errors are listed with paths relative to the repository root; the build may print further follow-on errors (for example `CS0103` or `CS0619`) for the same missing types. The listed errors must be among them.
- A "green" run prints one `Passed!` line, for `net8.0`. Durations vary; counts must match exactly:

  ```text
  Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Core.Tests.dll (net8.0)
  ```

- Core test counts after each task (whole `Lod.Core.Tests` project, on `net8.0`): S0 end 1 · Task 1: 10 · Task 2: 15 · Task 3: 27 · Task 4: 30 · Task 5: 36 · Task 6: 40 · Task 8: 65.
- Copy code blocks exactly. Do not reformat, rename, or reorder; the code was built with 0 warnings and all tests passing on `net8.0`.

---

## Slice A — `feature/core-common`

Roadmap slice 1. Delivers tolerances, diagnostics, results, and the zone identifier.

- [x] **Start the slice**

```bash
git switch main
git pull --ff-only
git switch -c feature/core-common main
```

### Task 1: ToleranceSettings

**Files:**
- Create: `src/Lod.Core/Common/ToleranceSettings.cs`
- Test: `tests/Lod.Core.Tests/Common/ToleranceSettingsTests.cs`

**Interfaces:**
- Consumes: the S0 projects `src/Lod.Core/Lod.Core.csproj` and `tests/Lod.Core.Tests/Lod.Core.Tests.csproj`; the namespace `Lod.Core.Common` (exists since S0 through `BuildInfo`).
- Produces (namespace `Lod.Core.Common`):
  - `public sealed class ToleranceSettings`
  - `public ToleranceSettings(double distance, double relativeArea, double relativeLoad, double absoluteSchedule, double angle)` — throws `ArgumentOutOfRangeException` unless every value is positive and finite
  - `public static ToleranceSettings Default { get; }` — 1e-6 m, 1e-6, 1e-9, 1e-9, 1e-6 rad
  - `public double Distance { get; }`, `RelativeArea`, `RelativeLoad`, `AbsoluteSchedule`, `Angle`
  - `public int DecimalPrecision { get; }` — `round(-log10(Distance))`, 6 by default
  - `public bool AreaEquals(double expected, double actual)`, `public bool LoadEquals(double expected, double actual)` — `|a − b| ≤ rel · max(1, |a|, |b|)`
  - `public bool ScheduleEquals(double expected, double actual)` — `|a − b| ≤ AbsoluteSchedule`

- [x] **Step 1: Write the failing test**

Create `tests/Lod.Core.Tests/Common/ToleranceSettingsTests.cs`:

```csharp
using System;
using Lod.Core.Common;
using Xunit;

namespace Lod.Core.Tests.Common;

public sealed class ToleranceSettingsTests
{
    [Fact]
    public void DefaultsMatchAdr004()
    {
        ToleranceSettings t = ToleranceSettings.Default;

        Assert.Equal(1e-6, t.Distance);
        Assert.Equal(1e-6, t.RelativeArea);
        Assert.Equal(1e-9, t.RelativeLoad);
        Assert.Equal(1e-9, t.AbsoluteSchedule);
        Assert.Equal(1e-6, t.Angle);
        Assert.Equal(6, t.DecimalPrecision);
    }

    [Theory]
    [InlineData(1000.0, 1000.0005, true)]
    [InlineData(1000.0, 1000.002, false)]
    [InlineData(0.0, 0.0000005, true)]
    public void AreaEqualsIsRelativeWithUnitFloor(double expected, double actual, bool equal)
    {
        Assert.Equal(equal, ToleranceSettings.Default.AreaEquals(expected, actual));
    }

    [Fact]
    public void LoadEqualsIsTighterThanAreaEquals()
    {
        Assert.True(ToleranceSettings.Default.AreaEquals(1000.0, 1000.0005));
        Assert.False(ToleranceSettings.Default.LoadEquals(1000.0, 1000.0005));
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(-1e-6)]
    [InlineData(double.NaN)]
    [InlineData(double.PositiveInfinity)]
    public void RejectsNonPositiveTolerances(double distance)
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new ToleranceSettings(distance, 1e-6, 1e-9, 1e-9, 1e-6));
    }
}
```

- [x] **Step 2: Run the test to verify it fails**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.ToleranceSettingsTests"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Common\ToleranceSettingsTests.cs(12,9): error CS0246: The type or namespace name 'ToleranceSettings' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Implement `ToleranceSettings`**

The defaults are those of ADR-004. `RelativeArea` is 1e-6, not 1e-9: from S2, polygon operations snap to a 1e-6 m grid, so per-vertex rounding of up to 5e-7 m gives relative area errors around 1e-7 for 10 m zones. `RelativeLoad` can stay at 1e-9 because transfer fractions are normalised per source, so extensive quantities are conserved to floating-point precision regardless of polygon rounding. Relative comparisons use a floor of 1 so that values near zero are compared absolutely.

Create `src/Lod.Core/Common/ToleranceSettings.cs`:

```csharp
using System;

namespace Lod.Core.Common;

/// <summary>
/// The single place where numerical tolerances are defined (GLOBAL.md, quality rule 4; ADR-004).
/// </summary>
public sealed class ToleranceSettings
{
    /// <summary>
    /// Creates tolerance settings; every value must be positive and finite.
    /// </summary>
    /// <param name="distance">Geometric distance tolerance in metres; also the snapping grid for polygon operations.</param>
    /// <param name="relativeArea">Relative tolerance for area and volume comparisons.</param>
    /// <param name="relativeLoad">Relative tolerance for load, occupancy, and air-flow comparisons.</param>
    /// <param name="absoluteSchedule">Absolute tolerance for schedule values.</param>
    /// <param name="angle">Angular tolerance in radians.</param>
    public ToleranceSettings(double distance, double relativeArea, double relativeLoad, double absoluteSchedule, double angle)
    {
        Distance = RequirePositive(distance, nameof(distance));
        RelativeArea = RequirePositive(relativeArea, nameof(relativeArea));
        RelativeLoad = RequirePositive(relativeLoad, nameof(relativeLoad));
        AbsoluteSchedule = RequirePositive(absoluteSchedule, nameof(absoluteSchedule));
        Angle = RequirePositive(angle, nameof(angle));
    }

    /// <summary>
    /// Project defaults from ADR-004.
    /// </summary>
    public static ToleranceSettings Default { get; } = new(distance: 1e-6, relativeArea: 1e-6, relativeLoad: 1e-9, absoluteSchedule: 1e-9, angle: 1e-6);

    /// <summary>Geometric distance tolerance in metres.</summary>
    public double Distance { get; }

    /// <summary>Relative tolerance for area and volume comparisons.</summary>
    public double RelativeArea { get; }

    /// <summary>Relative tolerance for load, occupancy, and air-flow comparisons.</summary>
    public double RelativeLoad { get; }

    /// <summary>Absolute tolerance for schedule values.</summary>
    public double AbsoluteSchedule { get; }

    /// <summary>Angular tolerance in radians.</summary>
    public double Angle { get; }

    /// <summary>
    /// Number of decimal places that corresponds to <see cref="Distance"/>; used as the polygon-clipping precision.
    /// </summary>
    public int DecimalPrecision => (int)Math.Round(-Math.Log10(Distance));

    /// <summary>Whether two areas or volumes agree within <see cref="RelativeArea"/>.</summary>
    /// <param name="expected">Reference value.</param>
    /// <param name="actual">Value under test.</param>
    /// <returns><c>true</c> when the values agree.</returns>
    public bool AreaEquals(double expected, double actual) => RelativeEquals(expected, actual, RelativeArea);

    /// <summary>Whether two load magnitudes agree within <see cref="RelativeLoad"/>.</summary>
    /// <param name="expected">Reference value.</param>
    /// <param name="actual">Value under test.</param>
    /// <returns><c>true</c> when the values agree.</returns>
    public bool LoadEquals(double expected, double actual) => RelativeEquals(expected, actual, RelativeLoad);

    /// <summary>Whether two schedule values agree within <see cref="AbsoluteSchedule"/>.</summary>
    /// <param name="expected">Reference value.</param>
    /// <param name="actual">Value under test.</param>
    /// <returns><c>true</c> when the values agree.</returns>
    public bool ScheduleEquals(double expected, double actual) => Math.Abs(expected - actual) <= AbsoluteSchedule;

    private static bool RelativeEquals(double expected, double actual, double relative)
    {
        double scale = Math.Max(1.0, Math.Max(Math.Abs(expected), Math.Abs(actual)));
        return Math.Abs(expected - actual) <= relative * scale;
    }

    private static double RequirePositive(double value, string name)
    {
        if (!(value > 0) || double.IsInfinity(value))
        {
            throw new ArgumentOutOfRangeException(name, value, "Tolerances must be positive and finite.");
        }

        return value;
    }
}
```

- [x] **Step 4: Run the test to verify it passes**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.ToleranceSettingsTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 5: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 10, … Total: 10` on `net8.0`.

- [x] **Step 6: Commit**

```bash
git add src/Lod.Core/Common/ToleranceSettings.cs tests/Lod.Core.Tests/Common/ToleranceSettingsTests.cs
git commit -m "feature(core): add central tolerance settings"
```

### Task 2: Diagnostics, results, and zone IDs

**Files:**
- Create: `src/Lod.Core/Common/Diagnostic.cs`
- Create: `src/Lod.Core/Common/DiagnosticCodes.cs`
- Create: `src/Lod.Core/Common/Result.cs`
- Create: `src/Lod.Core/Common/Ids.cs`
- Test: `tests/Lod.Core.Tests/Common/ResultTests.cs`

`DiagnosticCodes` is created here with the complete S1 set of 16 codes, because `Diagnostic`'s XML docs reference it through `cref` (an unresolved `cref` fails the build) and later S1 tasks use the codes. `ZoneId` is a pure data type with no behaviour of its own; it is introduced here so that Task 3 can use it.

**Interfaces:**
- Consumes: nothing new.
- Produces (namespace `Lod.Core.Common`):
  - `public enum DiagnosticSeverity { Info, Warning, Error }`
  - `public sealed record Diagnostic(DiagnosticSeverity Severity, string Code, string Message, string? Subject = null)` with `public static Diagnostic Error(string code, string message, string? subject = null)`, `Warning(...)`, `Info(...)` (same parameters), and `ToString()` → `"{Severity} {Code} [{Subject}]: {Message}"` (without ` [{Subject}]` when `Subject` is `null`)
  - `public static class DiagnosticCodes` — `public const string` fields `EmptyName`, `ScheduleLength`, `ScheduleValue`, `ScheduleKindMismatch`, `LoadValue`, `LoadBasisNotAllowed`, `DuplicateLoadType`, `PerPersonWithoutOccupancy`, `WindowToWallRatio`, `DuplicateSpaceType`, `NoSources`, `FractionOutOfRange`, `ZeroBasisQuantity`, `ZeroLoadSchedule`, `ZeroSetpointWeight`, `InvalidMeasures` (each value equals its name)
  - `public sealed class Result<T>` with `public bool IsSuccess { get; }`, `public IReadOnlyList<Diagnostic> Diagnostics { get; }`, `public T Value { get; }` (throws `InvalidOperationException` listing the diagnostics on failure)
  - `public static class Result` with `public static Result<T> Success<T>(T value, IEnumerable<Diagnostic>? diagnostics = null)`, `public static Result<T> Failure<T>(IEnumerable<Diagnostic> diagnostics)`, `public static Result<T> Failure<T>(Diagnostic error)`, `public static Result<T> FromDiagnostics<T>(Func<T> createValue, IReadOnlyCollection<Diagnostic> diagnostics)`
  - `public readonly record struct ZoneId(string Value)` with `ToString()` → `Value`

- [x] **Step 1: Write the failing test**

Create `tests/Lod.Core.Tests/Common/ResultTests.cs`:

```csharp
using System;
using Lod.Core.Common;
using Xunit;

namespace Lod.Core.Tests.Common;

public sealed class ResultTests
{
    [Fact]
    public void SuccessCarriesValueAndWarnings()
    {
        Result<int> result = Result.Success(42, new[] { Diagnostic.Warning("Code", "careful") });

        Assert.True(result.IsSuccess);
        Assert.Equal(42, result.Value);
        Assert.Single(result.Diagnostics);
    }

    [Fact]
    public void SuccessRejectsErrors()
    {
        Assert.Throws<ArgumentException>(() => Result.Success(1, new[] { Diagnostic.Error("Code", "broken") }));
    }

    [Fact]
    public void FailureRequiresAnError()
    {
        Assert.Throws<ArgumentException>(() => Result.Failure<int>(new[] { Diagnostic.Warning("Code", "only a warning") }));
    }

    [Fact]
    public void ValueOfFailureThrowsWithTheErrors()
    {
        Result<int> result = Result.Failure<int>(Diagnostic.Error("Code", "broken", "Z1"));

        InvalidOperationException exception = Assert.Throws<InvalidOperationException>(() => result.Value);
        Assert.Contains("broken", exception.Message);
        Assert.Contains("Z1", exception.Message);
    }

    [Fact]
    public void FromDiagnosticsDoesNotBuildTheValueOnError()
    {
        bool built = false;
        Result<int> result = Result.FromDiagnostics(
            () =>
            {
                built = true;
                return 1;
            },
            new[] { Diagnostic.Error("Code", "broken") });

        Assert.False(result.IsSuccess);
        Assert.False(built);
    }
}
```

- [x] **Step 2: Run the test to verify it fails**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.ResultTests"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Common\ResultTests.cs(12,9): error CS0246: The type or namespace name 'Result<>' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Common\ResultTests.cs(12,57): error CS0103: The name 'Diagnostic' does not exist in the current context
```

(A follow-on `error CS0619: 'Assert.Throws<T>(Func<Task>)' is obsolete` also appears while the types are missing; it disappears with them.)

- [x] **Step 3: Create `Diagnostic` and `DiagnosticSeverity`**

Create `src/Lod.Core/Common/Diagnostic.cs`:

```csharp
namespace Lod.Core.Common;

/// <summary>Severity of a <see cref="Diagnostic"/>.</summary>
public enum DiagnosticSeverity
{
    /// <summary>Informational; no action required.</summary>
    Info,

    /// <summary>The result is usable but deserves attention.</summary>
    Warning,

    /// <summary>The operation failed; no usable result.</summary>
    Error,
}

/// <summary>
/// A structured message produced by a pipeline step (GLOBAL.md, quality rule 5).
/// </summary>
/// <param name="Severity">How serious the message is.</param>
/// <param name="Code">A stable identifier from <see cref="DiagnosticCodes"/>.</param>
/// <param name="Message">Human-readable explanation with actionable context.</param>
/// <param name="Subject">The object the message is about (e.g. a zone ID), if any.</param>
public sealed record Diagnostic(DiagnosticSeverity Severity, string Code, string Message, string? Subject = null)
{
    /// <summary>Creates an error diagnostic.</summary>
    /// <param name="code">Code from <see cref="DiagnosticCodes"/>.</param>
    /// <param name="message">Actionable explanation.</param>
    /// <param name="subject">Object the message is about.</param>
    /// <returns>The diagnostic.</returns>
    public static Diagnostic Error(string code, string message, string? subject = null) => new(DiagnosticSeverity.Error, code, message, subject);

    /// <summary>Creates a warning diagnostic.</summary>
    /// <param name="code">Code from <see cref="DiagnosticCodes"/>.</param>
    /// <param name="message">Actionable explanation.</param>
    /// <param name="subject">Object the message is about.</param>
    /// <returns>The diagnostic.</returns>
    public static Diagnostic Warning(string code, string message, string? subject = null) => new(DiagnosticSeverity.Warning, code, message, subject);

    /// <summary>Creates an informational diagnostic.</summary>
    /// <param name="code">Code from <see cref="DiagnosticCodes"/>.</param>
    /// <param name="message">Explanation.</param>
    /// <param name="subject">Object the message is about.</param>
    /// <returns>The diagnostic.</returns>
    public static Diagnostic Info(string code, string message, string? subject = null) => new(DiagnosticSeverity.Info, code, message, subject);

    /// <inheritdoc />
    public override string ToString() => Subject is null ? $"{Severity} {Code}: {Message}" : $"{Severity} {Code} [{Subject}]: {Message}";
}
```

- [x] **Step 4: Create `DiagnosticCodes` (complete S1 set)**

Codes are stable: later stages only append (never rename or reuse). Create `src/Lod.Core/Common/DiagnosticCodes.cs`:

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
}
```

- [x] **Step 5: Create `Result<T>` and `Result`**

A success never carries errors; a failure always carries at least one. `FromDiagnostics` builds the value only when no error was collected, so factories can validate first and construct afterwards. Create `src/Lod.Core/Common/Result.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

namespace Lod.Core.Common;

/// <summary>
/// The outcome of an operation whose failure is expected (GLOBAL.md, quality rule 5): a value plus diagnostics, or diagnostics with at least one error.
/// </summary>
/// <typeparam name="T">The value type.</typeparam>
public sealed class Result<T>
{
    private readonly T? _value;

    private Result(T? value, bool isSuccess, IReadOnlyList<Diagnostic> diagnostics)
    {
        _value = value;
        IsSuccess = isSuccess;
        Diagnostics = diagnostics;
    }

    /// <summary>Whether a value is available.</summary>
    public bool IsSuccess { get; }

    /// <summary>All diagnostics, including warnings and info on success.</summary>
    public IReadOnlyList<Diagnostic> Diagnostics { get; }

    /// <summary>The value; throws when the result is a failure.</summary>
    public T Value
    {
        get
        {
            if (!IsSuccess)
            {
                throw new InvalidOperationException("Result has no value: " + string.Join("; ", Diagnostics));
            }

            return _value!;
        }
    }

    internal static Result<T> CreateSuccess(T value, IEnumerable<Diagnostic> diagnostics)
    {
        Diagnostic[] list = diagnostics.ToArray();
        if (list.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            throw new ArgumentException("A successful result cannot contain errors.", nameof(diagnostics));
        }

        return new Result<T>(value, true, Array.AsReadOnly(list));
    }

    internal static Result<T> CreateFailure(IEnumerable<Diagnostic> diagnostics)
    {
        Diagnostic[] list = diagnostics.ToArray();
        if (!list.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            throw new ArgumentException("A failed result needs at least one error.", nameof(diagnostics));
        }

        return new Result<T>(default, false, Array.AsReadOnly(list));
    }
}

/// <summary>
/// Factory methods for <see cref="Result{T}"/>.
/// </summary>
public static class Result
{
    /// <summary>Creates a successful result; <paramref name="diagnostics"/> must not contain errors.</summary>
    /// <typeparam name="T">The value type.</typeparam>
    /// <param name="value">The value.</param>
    /// <param name="diagnostics">Warnings or info to carry along.</param>
    /// <returns>The result.</returns>
    public static Result<T> Success<T>(T value, IEnumerable<Diagnostic>? diagnostics = null) =>
        Result<T>.CreateSuccess(value, diagnostics ?? Array.Empty<Diagnostic>());

    /// <summary>Creates a failed result; <paramref name="diagnostics"/> must contain at least one error.</summary>
    /// <typeparam name="T">The value type.</typeparam>
    /// <param name="diagnostics">The diagnostics, at least one an error.</param>
    /// <returns>The result.</returns>
    public static Result<T> Failure<T>(IEnumerable<Diagnostic> diagnostics) => Result<T>.CreateFailure(diagnostics);

    /// <summary>Creates a failed result from a single error.</summary>
    /// <typeparam name="T">The value type.</typeparam>
    /// <param name="error">The error.</param>
    /// <returns>The result.</returns>
    public static Result<T> Failure<T>(Diagnostic error) => Result<T>.CreateFailure(new[] { error });

    /// <summary>Success built by <paramref name="createValue"/> when <paramref name="diagnostics"/> has no errors, otherwise failure.</summary>
    /// <typeparam name="T">The value type.</typeparam>
    /// <param name="createValue">Builds the value; only called when there are no errors.</param>
    /// <param name="diagnostics">Diagnostics collected so far.</param>
    /// <returns>The result.</returns>
    public static Result<T> FromDiagnostics<T>(Func<T> createValue, IReadOnlyCollection<Diagnostic> diagnostics) =>
        diagnostics.Any(d => d.Severity == DiagnosticSeverity.Error) ? Failure<T>(diagnostics) : Success(createValue(), diagnostics);
}
```

- [x] **Step 6: Create `ZoneId`**

Create `src/Lod.Core/Common/Ids.cs`:

```csharp
namespace Lod.Core.Common;

/// <summary>Identifies a zone within a plan, floor, or building.</summary>
/// <param name="Value">The identifier text.</param>
public readonly record struct ZoneId(string Value)
{
    /// <inheritdoc />
    public override string ToString() => Value;
}
```

- [x] **Step 7: Run the test to verify it passes**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Common.ResultTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     5, Skipped:     0, Total:     5, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 8: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 15, … Total: 15` on `net8.0`.

- [x] **Step 9: Commit**

```bash
git add src/Lod.Core/Common/Diagnostic.cs src/Lod.Core/Common/DiagnosticCodes.cs src/Lod.Core/Common/Result.cs src/Lod.Core/Common/Ids.cs tests/Lod.Core.Tests/Common/ResultTests.cs
git commit -m "feature(core): add diagnostics, results, and zone ids"
```

- [x] **Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/core-common
git push origin main
git branch -d feature/core-common
```

Expected from `verify.ps1`: build with `0 Warning(s)` and `0 Error(s)`, `Passed: 15` on `net8.0`, then `VERIFY PASSED`. Do not merge if it fails.

---

## Slice B — `feature/schedules-model`

Roadmap slice 2: an immutable schedule with validated length and kind (ADR-003).

- [x] **Start the slice**

```bash
git switch main
git pull --ff-only
git switch -c feature/schedules-model main
```

### Task 3: Schedules and aggregation records

**Files:**
- Create: `src/Lod.Core/Aggregation/AggregationRecord.cs`
- Create: `src/Lod.Core/Schedules/Schedule.cs`
- Test: `tests/Lod.Core.Tests/Aggregation/AggregationRecordTests.cs`
- Test: `tests/Lod.Core.Tests/Schedules/ScheduleTests.cs`

`AggregationRecord` belongs to the aggregation namespace but is created here because `Schedule.Create` takes an optional `AggregationRecord` (every derived schedule records its sources, method, and weights; GLOBAL.md scientific rule 2). Its own tests check that sources and weights stay aligned by index and that a record with different numbers of sources and weights is rejected.

**Interfaces:**
- Consumes: `ZoneId`, `Diagnostic`, `DiagnosticCodes` (`EmptyName`, `ScheduleLength`, `ScheduleValue`), `Result` (Task 2).
- Produces:
  - Namespace `Lod.Core.Aggregation`: `public enum AggregationMethod { MagnitudeConserved, MagnitudeWeighted, FloorAreaWeighted }`; `public sealed class AggregationRecord` with `public AggregationRecord(AggregationMethod method, IEnumerable<ZoneId> sources, IEnumerable<double> weights)` (throws `ArgumentException` when the counts differ), `public AggregationMethod Method { get; }`, `public IReadOnlyList<ZoneId> Sources { get; }`, `public IReadOnlyList<double> Weights { get; }`
  - Namespace `Lod.Core.Schedules`: `public enum ScheduleKind { Fraction, Temperature }`; `public sealed class Schedule` with `public const int HoursPerYear = 8760`, `public string Name { get; }`, `public ScheduleKind Kind { get; }`, `public IReadOnlyList<double> Values { get; }`, `public AggregationRecord? Aggregation { get; }`, `public double this[int hour] { get; }`, `public static Result<Schedule> Create(string name, ScheduleKind kind, IEnumerable<double> values, AggregationRecord? aggregation = null)`, `public static Result<Schedule> Constant(string name, ScheduleKind kind, double value)`, `public static Result<Schedule> FromDailyProfiles(string name, ScheduleKind kind, IReadOnlyList<double> weekday, IReadOnlyList<double> weekend, DayOfWeek firstDayOfYear)`

- [x] **Step 1: Write the failing aggregation-record tests**

Create `tests/Lod.Core.Tests/Aggregation/AggregationRecordTests.cs`:

```csharp
using System;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Xunit;

namespace Lod.Core.Tests.Aggregation;

public sealed class AggregationRecordTests
{
    [Fact]
    public void KeepsSourcesAndWeightsAligned()
    {
        var record = new AggregationRecord(AggregationMethod.FloorAreaWeighted, new[] { new ZoneId("A"), new ZoneId("B") }, new[] { 10.0, 30.0 });

        Assert.Equal(AggregationMethod.FloorAreaWeighted, record.Method);
        Assert.Equal("B", record.Sources[1].Value);
        Assert.Equal(30.0, record.Weights[1]);
    }

    [Fact]
    public void RejectsMismatchedSourcesAndWeights()
    {
        Assert.Throws<ArgumentException>(() => new AggregationRecord(AggregationMethod.MagnitudeWeighted, new[] { new ZoneId("A") }, new[] { 1.0, 2.0 }));
    }
}
```

- [x] **Step 2: Write the failing schedule tests**

Create `tests/Lod.Core.Tests/Schedules/ScheduleTests.cs`:

```csharp
using System;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Schedules;
using Xunit;

namespace Lod.Core.Tests.Schedules;

public sealed class ScheduleTests
{
    [Fact]
    public void CreateAcceptsAFullYearOfFractions()
    {
        Result<Schedule> result = Schedule.Create("Lights", ScheduleKind.Fraction, Enumerable.Repeat(0.5, Schedule.HoursPerYear));

        Assert.True(result.IsSuccess);
        Assert.Equal(Schedule.HoursPerYear, result.Value.Values.Count);
        Assert.Equal(0.5, result.Value[8759]);
        Assert.Null(result.Value.Aggregation);
    }

    [Fact]
    public void CreateRejectsWrongLength()
    {
        Result<Schedule> result = Schedule.Create("Short", ScheduleKind.Fraction, new double[24]);

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ScheduleLength);
    }

    [Theory]
    [InlineData(1.1)]
    [InlineData(-0.1)]
    [InlineData(double.NaN)]
    public void CreateRejectsInvalidFractions(double value)
    {
        double[] values = Enumerable.Repeat(0.5, Schedule.HoursPerYear).ToArray();
        values[100] = value;

        Result<Schedule> result = Schedule.Create("Bad", ScheduleKind.Fraction, values);

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ScheduleValue && d.Message.Contains("hour 100"));
    }

    [Fact]
    public void TemperaturesMayExceedOne()
    {
        Assert.True(Schedule.Constant("Heating", ScheduleKind.Temperature, 21.0).IsSuccess);
    }

    [Fact]
    public void CreateRejectsEmptyName()
    {
        Assert.Contains(Schedule.Constant(" ", ScheduleKind.Fraction, 1.0).Diagnostics, d => d.Code == DiagnosticCodes.EmptyName);
    }

    [Fact]
    public void ValuesCannotBeMutatedThroughTheList()
    {
        Schedule schedule = Schedule.Constant("Always", ScheduleKind.Fraction, 1.0).Value;

        Assert.IsNotType<double[]>(schedule.Values);
    }

    [Fact]
    public void DailyProfilesFollowTheWeekStartingOnTheGivenDay()
    {
        double[] weekday = Enumerable.Repeat(0.25, 24).ToArray();
        double[] weekend = Enumerable.Repeat(0.75, 24).ToArray();
        weekday[9] = 0.5;

        Schedule schedule = Schedule.FromDailyProfiles("Occ", ScheduleKind.Fraction, weekday, weekend, DayOfWeek.Monday).Value;

        Assert.Equal(0.25, schedule[0]);
        Assert.Equal(0.5, schedule[9]);
        Assert.Equal(0.25, schedule[(4 * 24) + 3]);
        Assert.Equal(0.75, schedule[(5 * 24) + 3]);
        Assert.Equal(0.75, schedule[(6 * 24) + 3]);
        Assert.Equal(0.25, schedule[(7 * 24) + 3]);
    }

    [Fact]
    public void DailyProfilesNeedTwentyFourValues()
    {
        Result<Schedule> result = Schedule.FromDailyProfiles("Occ", ScheduleKind.Fraction, new double[23], new double[24], DayOfWeek.Monday);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ScheduleLength);
    }
}
```

- [x] **Step 3: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Schedules|FullyQualifiedName~Lod.Core.Tests.Aggregation.AggregationRecordTests"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Aggregation\AggregationRecordTests.cs(2,16): error CS0234: The type or namespace name 'Aggregation' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\Schedules\ScheduleTests.cs(4,16): error CS0234: The type or namespace name 'Schedules' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
```

- [x] **Step 4: Create `AggregationRecord`**

Create `src/Lod.Core/Aggregation/AggregationRecord.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;

namespace Lod.Core.Aggregation;

/// <summary>How a derived value was computed from its sources.</summary>
public enum AggregationMethod
{
    /// <summary>A load value: the absolute design magnitude transferred from the sources is conserved and re-expressed in the load's basis (ADR-007).</summary>
    MagnitudeConserved,

    /// <summary>A load schedule: weighted by each source's transferred design magnitude (ADR-007).</summary>
    MagnitudeWeighted,

    /// <summary>A setpoint schedule: weighted by each conditioned source's transferred floor area (ADR-005, D-038).</summary>
    FloorAreaWeighted,
}

/// <summary>
/// Traceability record attached to every derived load and schedule (GLOBAL.md, scientific rule 2).
/// </summary>
public sealed class AggregationRecord
{
    /// <summary>Creates a record; <paramref name="sources"/> and <paramref name="weights"/> must have equal length.</summary>
    /// <param name="method">The aggregation method.</param>
    /// <param name="sources">Source zones, in the order of <paramref name="weights"/>.</param>
    /// <param name="weights">Weight of each source in the method's unit (transferred magnitude or floor area).</param>
    public AggregationRecord(AggregationMethod method, IEnumerable<ZoneId> sources, IEnumerable<double> weights)
    {
        ZoneId[] sourceArray = sources.ToArray();
        double[] weightArray = weights.ToArray();
        if (sourceArray.Length != weightArray.Length)
        {
            throw new ArgumentException("Every source needs exactly one weight.", nameof(weights));
        }

        Method = method;
        Sources = Array.AsReadOnly(sourceArray);
        Weights = Array.AsReadOnly(weightArray);
    }

    /// <summary>The aggregation method.</summary>
    public AggregationMethod Method { get; }

    /// <summary>Source zones.</summary>
    public IReadOnlyList<ZoneId> Sources { get; }

    /// <summary>Weight of each source, aligned with <see cref="Sources"/>.</summary>
    public IReadOnlyList<double> Weights { get; }
}
```

- [x] **Step 5: Create `Schedule` and `ScheduleKind`**

8760 hourly values for a non-leap year (ADR-003). Fractions must lie in [0, 1]; temperatures must be finite. The values are copied into a private array and exposed through `Array.AsReadOnly`, so callers cannot mutate them (`ValuesCannotBeMutatedThroughTheList`). `FromDailyProfiles` repeats a weekday profile Monday to Friday and a weekend profile on Saturday and Sunday; holidays are not modelled. Create `src/Lod.Core/Schedules/Schedule.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Common;

namespace Lod.Core.Schedules;

/// <summary>What a schedule's values mean (ADR-003).</summary>
public enum ScheduleKind
{
    /// <summary>Dimensionless fraction in [0, 1] multiplying a load's design value.</summary>
    Fraction,

    /// <summary>Temperature in °C, used for setpoints.</summary>
    Temperature,
}

/// <summary>
/// An immutable hourly schedule over a non-leap year (ADR-003).
/// </summary>
public sealed class Schedule
{
    /// <summary>Number of hourly values in every schedule.</summary>
    public const int HoursPerYear = 8760;

    private const int HoursPerDay = 24;

    private readonly double[] _values;

    private Schedule(string name, ScheduleKind kind, double[] values, AggregationRecord? aggregation)
    {
        Name = name;
        Kind = kind;
        _values = values;
        Values = Array.AsReadOnly(values);
        Aggregation = aggregation;
    }

    /// <summary>Schedule name.</summary>
    public string Name { get; }

    /// <summary>What the values mean.</summary>
    public ScheduleKind Kind { get; }

    /// <summary>The <see cref="HoursPerYear"/> hourly values.</summary>
    public IReadOnlyList<double> Values { get; }

    /// <summary>How this schedule was derived, or <c>null</c> for an input schedule.</summary>
    public AggregationRecord? Aggregation { get; }

    /// <summary>Value at an hour of the year, 0-based.</summary>
    /// <param name="hour">Hour index in [0, <see cref="HoursPerYear"/>).</param>
    public double this[int hour] => _values[hour];

    /// <summary>Creates a schedule from exactly <see cref="HoursPerYear"/> values.</summary>
    /// <param name="name">Non-empty name.</param>
    /// <param name="kind">Value meaning; fractions must lie in [0, 1].</param>
    /// <param name="values">Hourly values.</param>
    /// <param name="aggregation">Derivation record for aggregated schedules.</param>
    /// <returns>The schedule or validation errors.</returns>
    public static Result<Schedule> Create(string name, ScheduleKind kind, IEnumerable<double> values, AggregationRecord? aggregation = null)
    {
        double[] array = values.ToArray();
        var diagnostics = new List<Diagnostic>();
        if (string.IsNullOrWhiteSpace(name))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.EmptyName, "A schedule needs a name."));
        }

        if (array.Length != HoursPerYear)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.ScheduleLength, $"Expected {HoursPerYear} hourly values, got {array.Length}.", name));
        }

        int firstInvalid = Array.FindIndex(array, v => !IsValid(kind, v));
        if (firstInvalid >= 0)
        {
            diagnostics.Add(Diagnostic.Error(
                DiagnosticCodes.ScheduleValue,
                $"Value {array[firstInvalid]} at hour {firstInvalid} is not valid for a {kind} schedule.",
                name));
        }

        return Result.FromDiagnostics(() => new Schedule(name, kind, array, aggregation), diagnostics);
    }

    /// <summary>Creates a schedule with the same value every hour.</summary>
    /// <param name="name">Non-empty name.</param>
    /// <param name="kind">Value meaning.</param>
    /// <param name="value">The constant value.</param>
    /// <returns>The schedule or validation errors.</returns>
    public static Result<Schedule> Constant(string name, ScheduleKind kind, double value) =>
        Create(name, kind, Enumerable.Repeat(value, HoursPerYear));

    /// <summary>
    /// Creates a schedule by repeating a 24-hour weekday profile Monday to Friday and a weekend profile on Saturday and Sunday. Holidays are not modelled.
    /// </summary>
    /// <param name="name">Non-empty name.</param>
    /// <param name="kind">Value meaning.</param>
    /// <param name="weekday">24 hourly values for Monday to Friday.</param>
    /// <param name="weekend">24 hourly values for Saturday and Sunday.</param>
    /// <param name="firstDayOfYear">Weekday of 1 January.</param>
    /// <returns>The schedule or validation errors.</returns>
    public static Result<Schedule> FromDailyProfiles(string name, ScheduleKind kind, IReadOnlyList<double> weekday, IReadOnlyList<double> weekend, DayOfWeek firstDayOfYear)
    {
        if (weekday.Count != HoursPerDay || weekend.Count != HoursPerDay)
        {
            return Result.Failure<Schedule>(Diagnostic.Error(
                DiagnosticCodes.ScheduleLength,
                $"Daily profiles need {HoursPerDay} values each, got {weekday.Count} (weekday) and {weekend.Count} (weekend).",
                name));
        }

        var values = new double[HoursPerYear];
        for (int hour = 0; hour < HoursPerYear; hour++)
        {
            int day = hour / HoursPerDay;
            var dayOfWeek = (DayOfWeek)(((int)firstDayOfYear + day) % 7);
            bool isWeekend = dayOfWeek == DayOfWeek.Saturday || dayOfWeek == DayOfWeek.Sunday;
            values[hour] = (isWeekend ? weekend : weekday)[hour % HoursPerDay];
        }

        return Create(name, kind, values);
    }

    private static bool IsValid(ScheduleKind kind, double value)
    {
        if (double.IsNaN(value) || double.IsInfinity(value))
        {
            return false;
        }

        return kind != ScheduleKind.Fraction || (value >= 0.0 && value <= 1.0);
    }
}
```

- [x] **Step 6: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Schedules|FullyQualifiedName~Lod.Core.Tests.Aggregation.AggregationRecordTests"
```

Expected (10 schedule tests and 2 aggregation-record tests):

```text
Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 7: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 27, … Total: 27` on `net8.0`.

- [x] **Step 8: Commit**

```bash
git add src/Lod.Core/Aggregation/AggregationRecord.cs src/Lod.Core/Schedules/Schedule.cs tests/Lod.Core.Tests/Aggregation/AggregationRecordTests.cs tests/Lod.Core.Tests/Schedules/ScheduleTests.cs
git commit -m "feature(schedules): add immutable hourly schedules and aggregation records"
```

- [x] **Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/schedules-model
git push origin main
git branch -d feature/schedules-model
```

Expected from `verify.ps1`: `0 Warning(s)`, `0 Error(s)`, `Passed: 27` on `net8.0`, `VERIFY PASSED`.

---

## Slice C — `feature/loads-model`

Roadmap slice 3: load types, bases, and the load definition, with units and bases as in ADR-007.

- [x] **Start the slice**

```bash
git switch main
git pull --ff-only
git switch -c feature/loads-model main
```

### Task 4: Load definitions

**Files:**
- Create: `src/Lod.Core/Loads/LoadDefinition.cs`
- Create: `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs` (first version)
- Test: `tests/Lod.Core.Tests/Programs/ProgramTests.cs` (first version: the three load tests)

**Choice for the shared test builders:** `TestPrograms` is introduced here **without** `Program(...)`, `Unconditioned(...)`, and `using Lod.Core.Programs;`, because `ZoneProgram` does not exist until Task 5. Task 5 adds them and shows the full final file. Likewise, `ProgramTests.cs` starts with the three load tests and neither `using System.Linq;` nor `using Lod.Core.Programs;`; Task 5 and Task 6 extend it, and Task 6 shows the full final file.

**Interfaces:**
- Consumes: `Schedule`, `ScheduleKind` (Task 3), `AggregationRecord` (Task 3), `Result`, `Diagnostic`, `DiagnosticCodes` (`LoadValue`, `LoadBasisNotAllowed`, `ScheduleKindMismatch`).
- Produces:
  - Namespace `Lod.Core.Loads`: `public enum LoadType { Occupancy, Lighting, ElectricEquipment, GasEquipment, DomesticHotWater, Ventilation, Infiltration }` (magnitudes in people; W; W; W; m³/h; m³/h; m³/h); `public enum LoadBasis { PerFloorArea, PerPerson, Absolute, PerExteriorWallArea, AirChangesPerHour }`; `public sealed class LoadDefinition` with `public LoadType Type { get; }`, `public LoadBasis Basis { get; }`, `public double Value { get; }`, `public Schedule Schedule { get; }`, `public AggregationRecord? Aggregation { get; }`, `public static Result<LoadDefinition> Create(LoadType type, LoadBasis basis, double value, Schedule schedule, AggregationRecord? aggregation = null)`
  - Test support (namespace `Lod.Core.Tests.TestSupport`, `internal static class TestPrograms`): `Schedule Fraction(double value, string name = "Fraction")`, `Schedule FractionAt(int hour, double value, double otherwise, string name = "Profile")`, `Schedule Temperature(double value, string name = "Setpoint")`, `LoadDefinition Load(LoadType type, LoadBasis basis, double value, Schedule? schedule = null)` (default schedule: constant fraction 1.0)

- [x] **Step 1: Create the test builders (first version)**

Create `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs`:

```csharp
using System.Linq;
using Lod.Core.Loads;
using Lod.Core.Schedules;

namespace Lod.Core.Tests.TestSupport;

/// <summary>Builders for schedules, loads, and programs used across tests.</summary>
internal static class TestPrograms
{
    public static Schedule Fraction(double value, string name = "Fraction") =>
        Schedule.Constant(name, ScheduleKind.Fraction, value).Value;

    public static Schedule FractionAt(int hour, double value, double otherwise, string name = "Profile")
    {
        double[] values = Enumerable.Repeat(otherwise, Schedule.HoursPerYear).ToArray();
        values[hour] = value;
        return Schedule.Create(name, ScheduleKind.Fraction, values).Value;
    }

    public static Schedule Temperature(double value, string name = "Setpoint") =>
        Schedule.Constant(name, ScheduleKind.Temperature, value).Value;

    public static LoadDefinition Load(LoadType type, LoadBasis basis, double value, Schedule? schedule = null) =>
        LoadDefinition.Create(type, basis, value, schedule ?? Fraction(1.0)).Value;
}
```

- [x] **Step 2: Write the failing tests**

Create `tests/Lod.Core.Tests/Programs/ProgramTests.cs`:

```csharp
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Programs;

public sealed class ProgramTests
{
    [Fact]
    public void LoadRejectsNegativeValues()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, -1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadValue);
    }

    [Fact]
    public void OccupancyCannotBePerPerson()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Occupancy, LoadBasis.PerPerson, 1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadBasisNotAllowed);
    }

    [Fact]
    public void LoadNeedsAFractionSchedule()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, TestPrograms.Temperature(21.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.ScheduleKindMismatch);
    }
}
```

- [x] **Step 3: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Programs\ProgramTests.cs(2,16): error CS0234: The type or namespace name 'Loads' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\TestSupport\TestPrograms.cs(2,16): error CS0234: The type or namespace name 'Loads' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
```

- [x] **Step 4: Implement `LoadType`, `LoadBasis`, and `LoadDefinition`**

A load's design magnitude is value × basis quantity (ADR-007): floor area, occupants, 1, gross exterior wall area (walls with an outdoor boundary, windows included; walls only, because roofs are unknown until floors are stacked), or volume. Occupancy may only be per floor area or absolute, because per-person occupancy would be circular. Loads multiply a fraction schedule. Create `src/Lod.Core/Loads/LoadDefinition.cs`:

```csharp
using System.Collections.Generic;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Lod.Core.Schedules;

namespace Lod.Core.Loads;

/// <summary>
/// Kind of internal load or air exchange. Design magnitudes are in people (occupancy), W (lighting, equipment), and m³/h (hot water, ventilation, infiltration).
/// </summary>
public enum LoadType
{
    /// <summary>People.</summary>
    Occupancy,

    /// <summary>Lighting power, W.</summary>
    Lighting,

    /// <summary>Electric equipment power, W.</summary>
    ElectricEquipment,

    /// <summary>Gas equipment power, W.</summary>
    GasEquipment,

    /// <summary>Domestic hot water peak flow, m³/h.</summary>
    DomesticHotWater,

    /// <summary>Outdoor-air ventilation, m³/h.</summary>
    Ventilation,

    /// <summary>Infiltration, m³/h.</summary>
    Infiltration,
}

/// <summary>
/// The quantity a load value is expressed per (ADR-007). The design magnitude is value × basis quantity.
/// </summary>
public enum LoadBasis
{
    /// <summary>Per m² of floor area.</summary>
    PerFloorArea,

    /// <summary>Per occupant; requires an occupancy load in the same program.</summary>
    PerPerson,

    /// <summary>Absolute magnitude per zone.</summary>
    Absolute,

    /// <summary>Per m² of gross exterior wall area (walls with an outdoor boundary, windows included).</summary>
    PerExteriorWallArea,

    /// <summary>Air changes per hour; magnitude = value × zone volume, in m³/h.</summary>
    AirChangesPerHour,
}

/// <summary>
/// One load of a program: design value in its basis and a fraction schedule.
/// </summary>
public sealed class LoadDefinition
{
    private LoadDefinition(LoadType type, LoadBasis basis, double value, Schedule schedule, AggregationRecord? aggregation)
    {
        Type = type;
        Basis = basis;
        Value = value;
        Schedule = schedule;
        Aggregation = aggregation;
    }

    /// <summary>Load type.</summary>
    public LoadType Type { get; }

    /// <summary>Basis the value is expressed per.</summary>
    public LoadBasis Basis { get; }

    /// <summary>Design value in the basis' unit.</summary>
    public double Value { get; }

    /// <summary>Fraction schedule multiplying the design magnitude.</summary>
    public Schedule Schedule { get; }

    /// <summary>How this load was derived, or <c>null</c> for an input load.</summary>
    public AggregationRecord? Aggregation { get; }

    /// <summary>Creates a load definition.</summary>
    /// <param name="type">Load type.</param>
    /// <param name="basis">Basis; occupancy allows only <see cref="LoadBasis.PerFloorArea"/> and <see cref="LoadBasis.Absolute"/>.</param>
    /// <param name="value">Non-negative design value.</param>
    /// <param name="schedule">A <see cref="ScheduleKind.Fraction"/> schedule.</param>
    /// <param name="aggregation">Derivation record for aggregated loads.</param>
    /// <returns>The load or validation errors.</returns>
    public static Result<LoadDefinition> Create(LoadType type, LoadBasis basis, double value, Schedule schedule, AggregationRecord? aggregation = null)
    {
        var diagnostics = new List<Diagnostic>();
        if (double.IsNaN(value) || double.IsInfinity(value) || value < 0)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.LoadValue, $"{type} value must be finite and non-negative, got {value}."));
        }

        if (type == LoadType.Occupancy && basis != LoadBasis.PerFloorArea && basis != LoadBasis.Absolute)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.LoadBasisNotAllowed, $"Occupancy must be per floor area or absolute, got {basis}."));
        }

        if (schedule.Kind != ScheduleKind.Fraction)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.ScheduleKindMismatch, $"{type} needs a fraction schedule, got {schedule.Kind}.", schedule.Name));
        }

        return Result.FromDiagnostics(() => new LoadDefinition(type, basis, value, schedule, aggregation), diagnostics);
    }
}
```

- [x] **Step 5: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     3, Skipped:     0, Total:     3, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 6: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 30, … Total: 30` on `net8.0`.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Loads/LoadDefinition.cs tests/Lod.Core.Tests/TestSupport/TestPrograms.cs tests/Lod.Core.Tests/Programs/ProgramTests.cs
git commit -m "feature(loads): add load types, bases, and validated load definitions"
```

- [x] **Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/loads-model
git push origin main
git branch -d feature/loads-model
```

Expected from `verify.ps1`: `0 Warning(s)`, `0 Error(s)`, `Passed: 30` on `net8.0`, `VERIFY PASSED`.

---

## Slice D — `feature/programs-presets`

Roadmap slice 4: space types, thermostats and zone programs (conditioned or unconditioned, D-038), program presets (D-024, D-026), the illustrative example presets, and `docs/research/program-presets.md`. The example presets hold round numbers, and the stair is unconditioned as an illustrative choice; they are **not** DOE prototype values. Sourcing DOE mid-rise apartment values with citations is an open research input for the researcher (roadmap §7, open point 4); the v2 roadmap had planned DOE values as the starting point, and Task 7 records this deviation. `SpaceType` includes `Mixed` for simplified zones that combine several space types.

- [x] **Start the slice**

```bash
git switch main
git pull --ff-only
git switch -c feature/programs-presets main
```

### Task 5: Space types, thermostats, and zone programs

**Files:**
- Create: `src/Lod.Core/Programs/ZoneProgram.cs`
- Modify: `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs` (final version)
- Modify: `tests/Lod.Core.Tests/Programs/ProgramTests.cs` (second version: + six program tests)

`SpaceType` is a pure data type in the same file; it is first used in Task 6. `Thermostat` lives in the same file because a program is conditioned exactly when it has one (D-038).

**Interfaces:**
- Consumes: `LoadDefinition`, `LoadType`, `LoadBasis` (Task 4), `Schedule`, `ScheduleKind` (Task 3), `Result`, `DiagnosticCodes` (`ScheduleKindMismatch`, `DuplicateLoadType`, `PerPersonWithoutOccupancy`).
- Produces (namespace `Lod.Core.Programs`):
  - `public enum SpaceType { DwellingUnit, Corridor, Stair, Core, Lobby, Service, Mechanical, Other, Mixed }`
  - `public sealed class Thermostat` with `public Schedule HeatingSetpoint { get; }`, `public Schedule CoolingSetpoint { get; }`, `public static Result<Thermostat> Create(Schedule heatingSetpoint, Schedule coolingSetpoint)` (both must be temperature schedules)
  - `public sealed class ZoneProgram` with `public IReadOnlyList<LoadDefinition> Loads { get; }` (ordered by `LoadType`, then `LoadBasis`; at most one per type and basis, D-047), `public Thermostat? Thermostat { get; }` (`null` for an unconditioned zone), `public bool IsConditioned { get; }`, `public LoadDefinition? Find(LoadType type, LoadBasis basis)`, `public static Result<ZoneProgram> Create(IEnumerable<LoadDefinition> loads, Thermostat? thermostat)`
  - Test support: `ZoneProgram TestPrograms.Program(double heating = 21.0, double cooling = 24.0, params LoadDefinition[] loads)` (conditioned; setpoint schedules named `Heating` and `Cooling`) and `ZoneProgram TestPrograms.Unconditioned(params LoadDefinition[] loads)`

- [x] **Step 1: Full file after this task: `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs`**

Add `using Lod.Core.Programs;` and the builders `Program(...)` (a conditioned program with a thermostat) and `Unconditioned(...)`: replace the content of `tests/Lod.Core.Tests/TestSupport/TestPrograms.cs` with the following. This is the last change to the file.

```csharp
using System.Linq;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;

namespace Lod.Core.Tests.TestSupport;

/// <summary>Builders for schedules, loads, and programs used across tests.</summary>
internal static class TestPrograms
{
    public static Schedule Fraction(double value, string name = "Fraction") =>
        Schedule.Constant(name, ScheduleKind.Fraction, value).Value;

    public static Schedule FractionAt(int hour, double value, double otherwise, string name = "Profile")
    {
        double[] values = Enumerable.Repeat(otherwise, Schedule.HoursPerYear).ToArray();
        values[hour] = value;
        return Schedule.Create(name, ScheduleKind.Fraction, values).Value;
    }

    public static Schedule Temperature(double value, string name = "Setpoint") =>
        Schedule.Constant(name, ScheduleKind.Temperature, value).Value;

    public static LoadDefinition Load(LoadType type, LoadBasis basis, double value, Schedule? schedule = null) =>
        LoadDefinition.Create(type, basis, value, schedule ?? Fraction(1.0)).Value;

    public static ZoneProgram Program(double heating = 21.0, double cooling = 24.0, params LoadDefinition[] loads) =>
        ZoneProgram.Create(loads, Thermostat.Create(Temperature(heating, "Heating"), Temperature(cooling, "Cooling")).Value).Value;

    public static ZoneProgram Unconditioned(params LoadDefinition[] loads) => ZoneProgram.Create(loads, null).Value;
}
```

- [x] **Step 2: Write the failing program tests**

Replace the content of `tests/Lod.Core.Tests/Programs/ProgramTests.cs` (adds `using System.Linq;`, `using Lod.Core.Programs;`, and the tests `ProgramOrdersLoadsByType`, `ProgramRejectsTheSameLoadTypeAndBasisTwice`, `ProgramAcceptsOneComponentPerBasis`, `PerPersonLoadsNeedOccupancy`, `SetpointsNeedTemperatureSchedules`, `ProgramWithoutThermostatIsUnconditioned`):

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Programs;

public sealed class ProgramTests
{
    [Fact]
    public void LoadRejectsNegativeValues()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, -1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadValue);
    }

    [Fact]
    public void OccupancyCannotBePerPerson()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Occupancy, LoadBasis.PerPerson, 1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadBasisNotAllowed);
    }

    [Fact]
    public void LoadNeedsAFractionSchedule()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, TestPrograms.Temperature(21.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.ScheduleKindMismatch);
    }

    [Fact]
    public void ProgramOrdersLoadsByType()
    {
        ZoneProgram program = TestPrograms.Program(
            loads: new[]
            {
                TestPrograms.Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.3),
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0),
            });

        Assert.Equal(LoadType.Lighting, program.Loads[0].Type);
        Assert.Equal(LoadType.Infiltration, program.Loads[1].Type);
        Assert.Null(program.Find(LoadType.Occupancy, LoadBasis.PerFloorArea));
    }

    [Fact]
    public void ProgramRejectsTheSameLoadTypeAndBasisTwice()
    {
        Result<ZoneProgram> result = ZoneProgram.Create(
            new[]
            {
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0),
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 2.0),
            },
            null);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.DuplicateLoadType);
    }

    [Fact]
    public void ProgramAcceptsOneComponentPerBasis()
    {
        ZoneProgram program = ZoneProgram.Create(
            new[]
            {
                TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerFloorArea, 1.0),
                TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.05),
                TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 10.0),
            },
            null).Value;

        Assert.Equal(
            new[] { (LoadType.Occupancy, LoadBasis.PerFloorArea), (LoadType.Ventilation, LoadBasis.PerFloorArea), (LoadType.Ventilation, LoadBasis.PerPerson) },
            program.Loads.Select(l => (l.Type, l.Basis)));
        Assert.Equal(10.0, program.Find(LoadType.Ventilation, LoadBasis.PerPerson)!.Value);
    }

    [Fact]
    public void PerPersonLoadsNeedOccupancy()
    {
        Result<ZoneProgram> result = ZoneProgram.Create(
            new[] { TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 30.0) },
            null);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.PerPersonWithoutOccupancy);
    }

    [Fact]
    public void SetpointsNeedTemperatureSchedules()
    {
        Result<Thermostat> result = Thermostat.Create(TestPrograms.Fraction(1.0), TestPrograms.Temperature(24.0));

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ScheduleKindMismatch);
    }

    [Fact]
    public void ProgramWithoutThermostatIsUnconditioned()
    {
        ZoneProgram program = TestPrograms.Unconditioned(TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 3.0));

        Assert.False(program.IsConditioned);
        Assert.Null(program.Thermostat);
        Assert.True(TestPrograms.Program().IsConditioned);
    }
}
```

- [x] **Step 3: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Programs\ProgramTests.cs(4,16): error CS0234: The type or namespace name 'Programs' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\TestSupport\TestPrograms.cs(3,16): error CS0234: The type or namespace name 'Programs' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\TestSupport\TestPrograms.cs(27,19): error CS0246: The type or namespace name 'ZoneProgram' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\TestSupport\TestPrograms.cs(30,19): error CS0246: The type or namespace name 'ZoneProgram' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 4: Implement `SpaceType`, `Thermostat`, and `ZoneProgram`**

A program holds at most one load per load type and basis (D-047): a load type may appear in several bases, for example ventilation per person plus per floor area, and these components add up. Loads are ordered by `LoadType`, then `LoadBasis`, so that output order never depends on input order. Per-person loads need an occupancy load to define their basis. Conditioning comes from the program (D-038): a conditioned zone has a `Thermostat` whose heating and cooling setpoints must both be temperature schedules; an unconditioned zone has no thermostat (`Thermostat == null`, `IsConditioned == false`) and therefore no setpoints. Create `src/Lod.Core/Programs/ZoneProgram.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Schedules;

namespace Lod.Core.Programs;

/// <summary>Semantic category of a space (spec §7). Rooms are never modelled (D-009).</summary>
public enum SpaceType
{
    /// <summary>One dwelling unit; never subdivided.</summary>
    DwellingUnit,

    /// <summary>Circulation corridor.</summary>
    Corridor,

    /// <summary>Stair.</summary>
    Stair,

    /// <summary>Service or circulation core.</summary>
    Core,

    /// <summary>Entrance lobby.</summary>
    Lobby,

    /// <summary>Service space.</summary>
    Service,

    /// <summary>Mechanical space.</summary>
    Mechanical,

    /// <summary>Anything else.</summary>
    Other,

    /// <summary>A simplified zone combining several space types.</summary>
    Mixed,
}

/// <summary>Heating and cooling setpoints of a conditioned zone.</summary>
public sealed class Thermostat
{
    private Thermostat(Schedule heatingSetpoint, Schedule coolingSetpoint)
    {
        HeatingSetpoint = heatingSetpoint;
        CoolingSetpoint = coolingSetpoint;
    }

    /// <summary>Heating setpoint, °C.</summary>
    public Schedule HeatingSetpoint { get; }

    /// <summary>Cooling setpoint, °C.</summary>
    public Schedule CoolingSetpoint { get; }

    /// <summary>Creates a thermostat.</summary>
    /// <param name="heatingSetpoint">A temperature schedule.</param>
    /// <param name="coolingSetpoint">A temperature schedule.</param>
    /// <returns>The thermostat or validation errors.</returns>
    public static Result<Thermostat> Create(Schedule heatingSetpoint, Schedule coolingSetpoint)
    {
        Diagnostic[] diagnostics = new[] { heatingSetpoint, coolingSetpoint }
            .Where(s => s.Kind != ScheduleKind.Temperature)
            .Select(s => Diagnostic.Error(DiagnosticCodes.ScheduleKindMismatch, "Setpoints need temperature schedules.", s.Name))
            .ToArray();
        return Result.FromDiagnostics(() => new Thermostat(heatingSetpoint, coolingSetpoint), diagnostics);
    }
}

/// <summary>
/// The energy-relevant program of a zone: its loads and, for conditioned zones, its thermostat. Conditioning comes from the program preset (D-038).
/// </summary>
public sealed class ZoneProgram
{
    private ZoneProgram(LoadDefinition[] loads, Thermostat? thermostat)
    {
        Loads = Array.AsReadOnly(loads);
        Thermostat = thermostat;
    }

    /// <summary>Loads ordered by <see cref="LoadType"/>, then <see cref="LoadBasis"/>; at most one per type and basis (D-047).</summary>
    public IReadOnlyList<LoadDefinition> Loads { get; }

    /// <summary>Setpoints of a conditioned zone; <c>null</c> for an unconditioned zone.</summary>
    public Thermostat? Thermostat { get; }

    /// <summary>Whether the zone is conditioned.</summary>
    public bool IsConditioned => Thermostat is not null;

    /// <summary>The load of a type expressed in a basis, or <c>null</c> when the program has none.</summary>
    /// <param name="type">Load type.</param>
    /// <param name="basis">Load basis.</param>
    /// <returns>The load or <c>null</c>.</returns>
    public LoadDefinition? Find(LoadType type, LoadBasis basis) => Loads.FirstOrDefault(l => l.Type == type && l.Basis == basis);

    /// <summary>
    /// Creates a program. A load type may appear once per basis, e.g. ventilation per person plus per floor area; its components add up (D-047).
    /// </summary>
    /// <param name="loads">Loads; at most one per type and basis; per-person loads need an occupancy load.</param>
    /// <param name="thermostat">Setpoints for a conditioned zone, or <c>null</c> for an unconditioned zone.</param>
    /// <returns>The program or validation errors.</returns>
    public static Result<ZoneProgram> Create(IEnumerable<LoadDefinition> loads, Thermostat? thermostat)
    {
        LoadDefinition[] ordered = loads.OrderBy(l => l.Type).ThenBy(l => l.Basis).ToArray();
        var diagnostics = new List<Diagnostic>();
        foreach (IGrouping<(LoadType Type, LoadBasis Basis), LoadDefinition> group in ordered.GroupBy(l => (l.Type, l.Basis)).Where(g => g.Count() > 1))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.DuplicateLoadType, $"Load type {group.Key.Type} {group.Key.Basis} appears {group.Count()} times."));
        }

        if (ordered.Any(l => l.Basis == LoadBasis.PerPerson) && ordered.All(l => l.Type != LoadType.Occupancy))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.PerPersonWithoutOccupancy, "Per-person loads need an occupancy load in the same program."));
        }

        return Result.FromDiagnostics(() => new ZoneProgram(ordered, thermostat), diagnostics);
    }
}
```

- [x] **Step 5: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 6: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 36, … Total: 36` on `net8.0`.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Programs/ZoneProgram.cs tests/Lod.Core.Tests/TestSupport/TestPrograms.cs tests/Lod.Core.Tests/Programs/ProgramTests.cs
git commit -m "feature(programs): add space types, thermostats, and zone programs"
```

### Task 6: Program presets and example presets

**Files:**
- Create: `src/Lod.Core/Programs/ProgramPreset.cs`
- Create: `src/Lod.Core/Programs/ExampleResidentialPresets.cs`
- Modify: `tests/Lod.Core.Tests/Programs/ProgramTests.cs` (final version: + three preset tests)

`tests/Lod.Core.Tests/TestSupport/TestPrograms.cs` is used but not changed; its final content is in Task 5.

**Interfaces:**
- Consumes: `ZoneProgram`, `SpaceType` (Task 5), `LoadDefinition`, `LoadType`, `LoadBasis` (Task 4), `Schedule`, `ScheduleKind` (Task 3), `Result`, `DiagnosticCodes` (`EmptyName`, `WindowToWallRatio`, `DuplicateSpaceType`).
- Produces (namespace `Lod.Core.Programs`):
  - `public sealed class ProgramPreset` with `public string Name { get; }`, `public SpaceType SpaceType { get; }`, `public ZoneProgram Program { get; }`, `public double WindowToWallRatio { get; }`, `public static Result<ProgramPreset> Create(string name, SpaceType spaceType, ZoneProgram program, double windowToWallRatio)` (WWR in [0, 1))
  - `public sealed class ProgramPresetSet` with `public IReadOnlyList<ProgramPreset> Presets { get; }` (ordered by space type), `public ProgramPreset? Find(SpaceType spaceType)`, `public static Result<ProgramPresetSet> Create(IEnumerable<ProgramPreset> presets)`
  - `public static class ExampleResidentialPresets` with `public static ProgramPreset DwellingUnit { get; }` (conditioned), `Corridor` (conditioned), `Stair` (unconditioned), and `public static ProgramPresetSet All { get; }`

- [x] **Step 1: Full file after this task: `tests/Lod.Core.Tests/Programs/ProgramTests.cs`**

Write the failing preset tests: append `PresetRejectsWwrOutsideRange`, `PresetSetRejectsDuplicateSpaceTypes`, and `ExamplePresetsCoverTheLinearPlanSpaceTypes` (which also checks that the dwelling unit and corridor are conditioned and the stair is not), so that the file reads exactly as follows. This is the last change to the file.

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Programs;

public sealed class ProgramTests
{
    [Fact]
    public void LoadRejectsNegativeValues()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, -1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadValue);
    }

    [Fact]
    public void OccupancyCannotBePerPerson()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Occupancy, LoadBasis.PerPerson, 1.0, TestPrograms.Fraction(1.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.LoadBasisNotAllowed);
    }

    [Fact]
    public void LoadNeedsAFractionSchedule()
    {
        Assert.Contains(
            LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, TestPrograms.Temperature(21.0)).Diagnostics,
            d => d.Code == DiagnosticCodes.ScheduleKindMismatch);
    }

    [Fact]
    public void ProgramOrdersLoadsByType()
    {
        ZoneProgram program = TestPrograms.Program(
            loads: new[]
            {
                TestPrograms.Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.3),
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0),
            });

        Assert.Equal(LoadType.Lighting, program.Loads[0].Type);
        Assert.Equal(LoadType.Infiltration, program.Loads[1].Type);
        Assert.Null(program.Find(LoadType.Occupancy, LoadBasis.PerFloorArea));
    }

    [Fact]
    public void ProgramRejectsTheSameLoadTypeAndBasisTwice()
    {
        Result<ZoneProgram> result = ZoneProgram.Create(
            new[]
            {
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0),
                TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 2.0),
            },
            null);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.DuplicateLoadType);
    }

    [Fact]
    public void ProgramAcceptsOneComponentPerBasis()
    {
        ZoneProgram program = ZoneProgram.Create(
            new[]
            {
                TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerFloorArea, 1.0),
                TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.05),
                TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 10.0),
            },
            null).Value;

        Assert.Equal(
            new[] { (LoadType.Occupancy, LoadBasis.PerFloorArea), (LoadType.Ventilation, LoadBasis.PerFloorArea), (LoadType.Ventilation, LoadBasis.PerPerson) },
            program.Loads.Select(l => (l.Type, l.Basis)));
        Assert.Equal(10.0, program.Find(LoadType.Ventilation, LoadBasis.PerPerson)!.Value);
    }

    [Fact]
    public void PerPersonLoadsNeedOccupancy()
    {
        Result<ZoneProgram> result = ZoneProgram.Create(
            new[] { TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 30.0) },
            null);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.PerPersonWithoutOccupancy);
    }

    [Fact]
    public void SetpointsNeedTemperatureSchedules()
    {
        Result<Thermostat> result = Thermostat.Create(TestPrograms.Fraction(1.0), TestPrograms.Temperature(24.0));

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ScheduleKindMismatch);
    }

    [Fact]
    public void ProgramWithoutThermostatIsUnconditioned()
    {
        ZoneProgram program = TestPrograms.Unconditioned(TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 3.0));

        Assert.False(program.IsConditioned);
        Assert.Null(program.Thermostat);
        Assert.True(TestPrograms.Program().IsConditioned);
    }

    [Theory]
    [InlineData(-0.1)]
    [InlineData(1.0)]
    public void PresetRejectsWwrOutsideRange(double wwr)
    {
        Result<ProgramPreset> result = ProgramPreset.Create("Unit", SpaceType.DwellingUnit, TestPrograms.Program(), wwr);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.WindowToWallRatio);
    }

    [Fact]
    public void PresetSetRejectsDuplicateSpaceTypes()
    {
        ProgramPreset a = ProgramPreset.Create("A", SpaceType.Corridor, TestPrograms.Program(), 0.2).Value;
        ProgramPreset b = ProgramPreset.Create("B", SpaceType.Corridor, TestPrograms.Program(), 0.2).Value;

        Assert.Contains(ProgramPresetSet.Create(new[] { a, b }).Diagnostics, d => d.Code == DiagnosticCodes.DuplicateSpaceType);
    }

    [Fact]
    public void ExamplePresetsCoverTheLinearPlanSpaceTypes()
    {
        ProgramPresetSet set = ExampleResidentialPresets.All;

        Assert.NotNull(set.Find(SpaceType.DwellingUnit));
        Assert.NotNull(set.Find(SpaceType.Corridor));
        Assert.NotNull(set.Find(SpaceType.Stair));
        Assert.Equal(0.3, set.Find(SpaceType.DwellingUnit)!.WindowToWallRatio);
        Assert.True(set.Find(SpaceType.DwellingUnit)!.Program.IsConditioned);
        Assert.True(set.Find(SpaceType.Corridor)!.Program.IsConditioned);
        Assert.False(set.Find(SpaceType.Stair)!.Program.IsConditioned);
    }
}
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Programs\ProgramTests.cs(116,16): error CS0246: The type or namespace name 'ProgramPreset' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Programs\ProgramTests.cs(127,25): error CS0103: The name 'ProgramPresetSet' does not exist in the current context
tests\Lod.Core.Tests\Programs\ProgramTests.cs(133,32): error CS0103: The name 'ExampleResidentialPresets' does not exist in the current context
```

- [x] **Step 3: Implement `ProgramPreset` and `ProgramPresetSet`**

A preset is the program of one space type plus its window-to-wall ratio (D-024, D-026). The WWR must be below 1: the S2 generator's centred window is the wall rectangle scaled about its centre by √WWR, which stays inside the wall only for WWR < 1 (D-026, D-039). A set holds at most one preset per space type, so a plan generator can look a zone's preset up by its space type. Create `src/Lod.Core/Programs/ProgramPreset.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;

namespace Lod.Core.Programs;

/// <summary>
/// A program preset for one space type (D-024): its zone program and window-to-wall ratio (D-026).
/// </summary>
public sealed class ProgramPreset
{
    private ProgramPreset(string name, SpaceType spaceType, ZoneProgram program, double windowToWallRatio)
    {
        Name = name;
        SpaceType = spaceType;
        Program = program;
        WindowToWallRatio = windowToWallRatio;
    }

    /// <summary>Preset name.</summary>
    public string Name { get; }

    /// <summary>The space type this preset applies to.</summary>
    public SpaceType SpaceType { get; }

    /// <summary>Loads and setpoints.</summary>
    public ZoneProgram Program { get; }

    /// <summary>Window-to-wall ratio in [0, 1) used by the plan generator to size the window on every exterior wall of the space (D-026, D-039).</summary>
    public double WindowToWallRatio { get; }

    /// <summary>Creates a preset.</summary>
    /// <param name="name">Non-empty name.</param>
    /// <param name="spaceType">Space type.</param>
    /// <param name="program">Loads and setpoints.</param>
    /// <param name="windowToWallRatio">WWR in [0, 1).</param>
    /// <returns>The preset or validation errors.</returns>
    public static Result<ProgramPreset> Create(string name, SpaceType spaceType, ZoneProgram program, double windowToWallRatio)
    {
        var diagnostics = new List<Diagnostic>();
        if (string.IsNullOrWhiteSpace(name))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.EmptyName, "A program preset needs a name."));
        }

        if (double.IsNaN(windowToWallRatio) || windowToWallRatio < 0 || windowToWallRatio >= 1)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.WindowToWallRatio, $"WWR must be in [0, 1), got {windowToWallRatio}.", name));
        }

        return Result.FromDiagnostics(() => new ProgramPreset(name, spaceType, program, windowToWallRatio), diagnostics);
    }
}

/// <summary>
/// Program presets indexed by space type; a plan generator assigns each zone the preset of its space type.
/// </summary>
public sealed class ProgramPresetSet
{
    private ProgramPresetSet(ProgramPreset[] presets)
    {
        Presets = Array.AsReadOnly(presets);
    }

    /// <summary>Presets ordered by space type.</summary>
    public IReadOnlyList<ProgramPreset> Presets { get; }

    /// <summary>The preset of a space type, or <c>null</c>.</summary>
    /// <param name="spaceType">Space type.</param>
    /// <returns>The preset or <c>null</c>.</returns>
    public ProgramPreset? Find(SpaceType spaceType) => Presets.FirstOrDefault(p => p.SpaceType == spaceType);

    /// <summary>Creates a set; each space type may appear once.</summary>
    /// <param name="presets">The presets.</param>
    /// <returns>The set or validation errors.</returns>
    public static Result<ProgramPresetSet> Create(IEnumerable<ProgramPreset> presets)
    {
        ProgramPreset[] ordered = presets.OrderBy(p => p.SpaceType).ToArray();
        Diagnostic[] diagnostics = ordered
            .GroupBy(p => p.SpaceType)
            .Where(g => g.Count() > 1)
            .Select(g => Diagnostic.Error(DiagnosticCodes.DuplicateSpaceType, $"Space type {g.Key} has {g.Count()} presets: {string.Join(", ", g.Select(p => p.Name))}."))
            .ToArray();
        return Result.FromDiagnostics(() => new ProgramPresetSet(ordered), diagnostics);
    }
}
```

- [x] **Step 4: Implement `ExampleResidentialPresets`**

These presets are **illustrative round numbers for development and tests, NOT DOE prototype values and not taken from any standard** (Task 7 documents them). They cover the space types the S2 linear plan generator places: dwelling unit, corridor, and stair. The dwelling unit and corridor are conditioned (21 °C heating, 24 °C cooling) and the stair is unconditioned; this choice is illustrative as well, made so that later stages exercise the conditioning rule of D-038 (for example, S3 reports the change in conditioned floor area when the stair is merged). The static arrays are declared before the presets that use them, because static initialisers run in textual order. Create `src/Lod.Core/Programs/ExampleResidentialPresets.cs`:

```csharp
using System;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Schedules;

namespace Lod.Core.Programs;

/// <summary>
/// Illustrative residential presets for development and tests. The values, and which spaces are conditioned, are round-number choices for
/// testing; they are NOT taken from the DOE prototypes or any standard. Sourced presets are a separate research input
/// (see docs/research/program-presets.md).
/// </summary>
public static class ExampleResidentialPresets
{
    private const DayOfWeek FirstDayOfYear = DayOfWeek.Monday;

    private static readonly double[] DwellingOccupancyWeekday =
    {
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.5, 0.3, 0.2, 0.2, 0.2,
        0.3, 0.2, 0.2, 0.3, 0.5, 0.7, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0,
    };

    private static readonly double[] DwellingOccupancyWeekend =
    {
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.7, 0.6, 0.6,
        0.6, 0.6, 0.6, 0.7, 0.8, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0,
    };

    private static readonly double[] DwellingLightingWeekday =
    {
        0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.4, 0.2, 0.1, 0.1, 0.1,
        0.1, 0.1, 0.1, 0.1, 0.2, 0.5, 0.8, 0.9, 0.9, 0.7, 0.4, 0.2,
    };

    private static readonly double[] DwellingLightingWeekend =
    {
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.3, 0.4, 0.3, 0.2, 0.2,
        0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.8, 0.9, 0.9, 0.7, 0.4, 0.2,
    };

    /// <summary>Dwelling unit: conditioned; occupancy, lighting, equipment, infiltration; WWR 0.3.</summary>
    public static ProgramPreset DwellingUnit { get; } = Build(
        "Example Dwelling Unit",
        SpaceType.DwellingUnit,
        0.3,
        conditioned: true,
        Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.03, Profile("Example Dwelling Occupancy", DwellingOccupancyWeekday, DwellingOccupancyWeekend)),
        Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, Profile("Example Dwelling Lighting", DwellingLightingWeekday, DwellingLightingWeekend)),
        Load(LoadType.ElectricEquipment, LoadBasis.PerFloorArea, 5.0, Constant("Example Dwelling Equipment", 0.5)),
        Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.3, Constant("Example Always On", 1.0)));

    /// <summary>Corridor: conditioned; lighting always on, infiltration; WWR 0.2.</summary>
    public static ProgramPreset Corridor { get; } = Build(
        "Example Corridor",
        SpaceType.Corridor,
        0.2,
        conditioned: true,
        Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, Constant("Example Always On", 1.0)),
        Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.3, Constant("Example Always On", 1.0)));

    /// <summary>Stair: unconditioned; lighting always on, infiltration; WWR 0.1.</summary>
    public static ProgramPreset Stair { get; } = Build(
        "Example Stair",
        SpaceType.Stair,
        0.1,
        conditioned: false,
        Load(LoadType.Lighting, LoadBasis.PerFloorArea, 3.0, Constant("Example Always On", 1.0)),
        Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.3, Constant("Example Always On", 1.0)));

    /// <summary>All example presets as a set.</summary>
    public static ProgramPresetSet All { get; } = ProgramPresetSet.Create(new[] { DwellingUnit, Corridor, Stair }).Value;

    private static ProgramPreset Build(string name, SpaceType spaceType, double windowToWallRatio, bool conditioned, params LoadDefinition[] loads)
    {
        Thermostat? thermostat = conditioned
            ? Thermostat.Create(
                Constant("Example Heating Setpoint", 21.0, ScheduleKind.Temperature),
                Constant("Example Cooling Setpoint", 24.0, ScheduleKind.Temperature)).Value
            : null;
        return ProgramPreset.Create(name, spaceType, ZoneProgram.Create(loads, thermostat).Value, windowToWallRatio).Value;
    }

    private static LoadDefinition Load(LoadType type, LoadBasis basis, double value, Schedule schedule) =>
        LoadDefinition.Create(type, basis, value, schedule).Value;

    private static Schedule Constant(string name, double value, ScheduleKind kind = ScheduleKind.Fraction) =>
        Schedule.Constant(name, kind, value).Value;

    private static Schedule Profile(string name, double[] weekday, double[] weekend) =>
        Schedule.FromDailyProfiles(name, ScheduleKind.Fraction, weekday, weekend, FirstDayOfYear).Value;
}
```

- [x] **Step 5: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Programs"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    13, Skipped:     0, Total:    13, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 6: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 40, … Total: 40` on `net8.0`.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Programs/ProgramPreset.cs src/Lod.Core/Programs/ExampleResidentialPresets.cs tests/Lod.Core.Tests/Programs/ProgramTests.cs
git commit -m "feature(programs): add program presets and illustrative example presets"
```

### Task 7: Program presets research document

**Files:**
- Create: `docs/research/program-presets.md`

The document defines a program preset (D-024), tabulates every example value from `ExampleResidentialPresets.cs`, states prominently that these values are illustrative and **not** DOE or standard values, states each preset's conditioning (the unconditioned stair is an illustrative choice; D-038), records that sourcing DOE mid-rise apartment values with citations is an open research input for the researcher and a deviation from the v2 roadmap's wording (roadmap v3 §7, open point 4), lists the prototype assumptions deliberately not reproduced, and explains how to build custom presets (the Grasshopper *Schedule*, *Load*, and *Program Preset* components arrive in S2).

**Interfaces:**
- Consumes: the types and values of Tasks 3 to 6.
- Produces: `docs/research/program-presets.md`, linked from `docs/architecture/domain-model.md` (Task 9).

- [x] **Step 1: Write the document**

Create `docs/research/program-presets.md` with exactly this content:

````markdown
# Program Presets

> **Status:** Current as of S1 (`v0.1.0`) · **Date:** 2026-10-01 · **Decisions:** D-009, D-024, D-026, D-038, D-039, D-047
>
> **Read this first:** the presets that ship with BEMGen (`ExampleResidentialPresets`) hold **illustrative round numbers chosen for development and tests, and which of them are conditioned is an illustrative choice too. They are NOT taken from the DOE prototype buildings or from any standard.** Sourced presets are an open research input (§3).

A program preset describes the energy-relevant program of one space type. This document defines what a preset contains, lists the example presets and their values, records how S1 deviates from the original plan for sourced values, states which prototype assumptions BEMGen deliberately does not reproduce, and explains how to build custom presets.

## 1. What a program preset is

A program preset carries everything BEMGen assigns to a space of one type: its loads with their schedules, whether it is conditioned and, if so, its heating and cooling setpoints, and its window parameter (D-024, D-038). There is one preset per space type. Rooms are never modelled: at the most detailed level (Z0) a dwelling unit is one zone (D-009).

In code a preset is a `ProgramPreset` ([`src/Lod.Core/Programs/ProgramPreset.cs`](../../src/Lod.Core/Programs/ProgramPreset.cs)):

| Member | Meaning | Rejected with diagnostic |
| --- | --- | --- |
| `Name` | Display name | `EmptyName` when empty or white space |
| `SpaceType` | The space type the preset applies to: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, or `Other`. (`Mixed` denotes a simplified zone that combines several space types.) | — |
| `Program` | A `ZoneProgram`: at most one load per load type and basis, each with a fraction schedule, plus a `Thermostat` (heating and cooling setpoint schedules in °C) for a conditioned space, or no thermostat for an unconditioned one (§1.1, §1.2) | see §1.1 |
| `WindowToWallRatio` | Window-to-wall ratio, the single window parameter (D-026) | `WindowToWallRatio` when outside [0, 1) |

Presets are grouped in a `ProgramPresetSet`, which holds at most one preset per space type (`DuplicateSpaceType` otherwise) and orders them by space type. From S2 on, the plan generator gives each zone the preset of its space type from such a set.

**Windows.** Walls carry explicit windows (D-039). The S2 linear plan generator uses the preset's WWR for one simple rule: one window centred on each outdoor wall of a zone, with area = WWR × wall area (D-026). Plan simplifiers keep every window unchanged and re-host it on the target wall that contains it (W0); window transformations (W1–W5) are a later stage, S5.

### 1.1 Loads, bases, and schedules

A load is a `LoadDefinition`: a `LoadType`, a `LoadBasis`, a non-negative design value expressed per that basis, and a fraction schedule. Its **design magnitude** is value × basis quantity, and its scheduled magnitude at hour *t* is design magnitude × *s*(*t*) (ADR-007).

| `LoadType` | Design magnitude |
| --- | --- |
| `Occupancy` | people |
| `Lighting` | W |
| `ElectricEquipment` | W |
| `GasEquipment` | W |
| `DomesticHotWater` | m³/h (peak flow) |
| `Ventilation` | m³/h |
| `Infiltration` | m³/h |

| `LoadBasis` | Value is expressed per | Basis quantity of a zone | Example value units |
| --- | --- | --- | --- |
| `PerFloorArea` | m² of floor area | floor area, m² | W/m², people/m² |
| `PerPerson` | occupant | design occupants (the summed magnitude of the zone's occupancy loads) | m³/h per person |
| `Absolute` | zone | 1 | W, people |
| `PerExteriorWallArea` | m² of gross exterior wall | area of walls with an outdoor boundary, windows included, m² | m³/h per m² |
| `AirChangesPerHour` | zone air volume per hour | volume, m³ | 1/h |

Validation, with the diagnostic code each rule raises:

- A load value must be finite and non-negative (`LoadValue`).
- Occupancy is expressed only `PerFloorArea` or `Absolute` (`LoadBasisNotAllowed`).
- A load needs a fraction schedule (`ScheduleKindMismatch`); a thermostat's setpoints need temperature schedules (`ScheduleKindMismatch`, from `Thermostat.Create`).
- A program has at most one load per load type and basis (`DuplicateLoadType`). A load type may appear in several bases, for example ventilation per person plus per floor area; these components add up (D-047).
- A per-person load needs an occupancy load in the same program (`PerPersonWithoutOccupancy`).

Schedules hold 8760 hourly values for a non-leap year (ADR-003). A `Fraction` schedule's values lie in [0, 1]; a `Temperature` schedule holds finite values in °C. `Schedule.FromDailyProfiles` builds a year from one 24-hour weekday profile (Monday to Friday) and one weekend profile (Saturday and Sunday), given the weekday of 1 January; holidays are not modelled.

### 1.2 Conditioning

Conditioning comes from the program preset (D-038). A preset whose program has a `Thermostat` is conditioned, with the thermostat's heating and cooling setpoint schedules; a preset without one is unconditioned and has no setpoints (`ZoneProgram.IsConditioned` is `false`).

When a plan simplifier merges zones, the merged zone is conditioned if any source contributing floor area to it is conditioned ("any conditioned wins"). Its setpoints are floor-area weighted over the conditioned sources only, `T*(t) = Σ wᵢTᵢ(t) / Σ wᵢ` with `wᵢ` the transferred floor area of conditioned source *i*: a prescribed control rule, not a conservation invariant (ADR-005). Merging conditioned and unconditioned spaces can therefore enlarge the conditioned floor area; from S3 on, validation reports that change without enforcing it, because it is a consequence of the zoning simplification under study (D-038).

## 2. Example presets

> **The values below, and the choice of which spaces are conditioned, are illustrative and chosen for development and tests. They are NOT taken from the DOE prototype buildings, from any standard, or from measured data. Do not use them as research inputs, and do not present results obtained with them as representative of any prototype or real building.**

[`ExampleResidentialPresets`](../../src/Lod.Core/Programs/ExampleResidentialPresets.cs) defines one preset for each space type that the S2 linear plan generator places: dwelling unit, corridor, and stair. `ExampleResidentialPresets.All` returns them as a `ProgramPresetSet`. Tests in S1 and in later stages use these presets, so changing a value changes test expectations and snapshots.

| Preset (`Name`) | Space type | Conditioning | Heating setpoint | Cooling setpoint | WWR |
| --- | --- | --- | --- | --- | --- |
| `Example Dwelling Unit` | `DwellingUnit` | conditioned | 21 °C, constant (`Example Heating Setpoint`) | 24 °C, constant (`Example Cooling Setpoint`) | 0.3 |
| `Example Corridor` | `Corridor` | conditioned | 21 °C, constant | 24 °C, constant | 0.2 |
| `Example Stair` | `Stair` | unconditioned | none | none | 0.1 |

The stair is unconditioned as an illustrative choice, so that the conditioning rule of §1.2 is exercised by the pipeline's tests (for example, merging the stair with conditioned zones in S3). It says nothing about how any prototype conditions its stairs.

| Preset | Load type | Basis | Value | Schedule |
| --- | --- | --- | --- | --- |
| Dwelling unit | `Occupancy` | `PerFloorArea` | 0.03 people/m² | `Example Dwelling Occupancy`: weekday and weekend profiles below |
| Dwelling unit | `Lighting` | `PerFloorArea` | 5.0 W/m² | `Example Dwelling Lighting`: weekday and weekend profiles below |
| Dwelling unit | `ElectricEquipment` | `PerFloorArea` | 5.0 W/m² | `Example Dwelling Equipment`: constant 0.5 |
| Dwelling unit | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |
| Corridor | `Lighting` | `PerFloorArea` | 5.0 W/m² | `Example Always On`: constant 1.0 |
| Corridor | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |
| Stair | `Lighting` | `PerFloorArea` | 3.0 W/m² | `Example Always On`: constant 1.0 |
| Stair | `Infiltration` | `AirChangesPerHour` | 0.3 1/h | `Example Always On`: constant 1.0 |

No example preset defines `GasEquipment`, `DomesticHotWater`, or `Ventilation`, and the corridor and stair presets have no occupancy load.

The dwelling-unit profiles are fractions per hour of the day (hour 0 is the first hour of the day). The year starts on a Monday; Monday to Friday use the weekday profile, Saturday and Sunday the weekend profile.

| Hour of day | Occupancy, weekday | Occupancy, weekend | Lighting, weekday | Lighting, weekend |
| --- | --- | --- | --- | --- |
| 0 | 1.0 | 1.0 | 0.1 | 0.1 |
| 1 | 1.0 | 1.0 | 0.1 | 0.1 |
| 2 | 1.0 | 1.0 | 0.1 | 0.1 |
| 3 | 1.0 | 1.0 | 0.1 | 0.1 |
| 4 | 1.0 | 1.0 | 0.1 | 0.1 |
| 5 | 1.0 | 1.0 | 0.2 | 0.1 |
| 6 | 0.8 | 1.0 | 0.4 | 0.2 |
| 7 | 0.5 | 1.0 | 0.4 | 0.3 |
| 8 | 0.3 | 0.8 | 0.2 | 0.4 |
| 9 | 0.2 | 0.7 | 0.1 | 0.3 |
| 10 | 0.2 | 0.6 | 0.1 | 0.2 |
| 11 | 0.2 | 0.6 | 0.1 | 0.2 |
| 12 | 0.3 | 0.6 | 0.1 | 0.2 |
| 13 | 0.2 | 0.6 | 0.1 | 0.2 |
| 14 | 0.2 | 0.6 | 0.1 | 0.2 |
| 15 | 0.3 | 0.7 | 0.1 | 0.2 |
| 16 | 0.5 | 0.8 | 0.2 | 0.3 |
| 17 | 0.7 | 0.9 | 0.5 | 0.5 |
| 18 | 0.9 | 0.9 | 0.8 | 0.8 |
| 19 | 0.9 | 1.0 | 0.9 | 0.9 |
| 20 | 1.0 | 1.0 | 0.9 | 0.9 |
| 21 | 1.0 | 1.0 | 0.7 | 0.7 |
| 22 | 1.0 | 1.0 | 0.4 | 0.4 |
| 23 | 1.0 | 1.0 | 0.2 | 0.2 |

## 3. Sourced presets: an open research input

The v2 roadmap (§4, S1, slice `feature/programs-presets`) planned a `DefaultResidentialPresets` class "with DOE mid-rise apartment values as the starting point", with sources cited in this document. **S1 deviates from that plan.** It ships `ExampleResidentialPresets` with the illustrative values and conditioning choices of §2 instead, and the class name says so, so that no result can be mistaken for one based on prototype values. Roadmap v3 records sourced presets as open point 4 of its §7.

Sourcing preset values from the DOE mid-rise apartment prototype, with citations, is an **open research input for the researcher**: loads, schedules, and which spaces are conditioned. It does not block S2 to S4: their tests check geometry and conservation invariants, which hold for any valid preset values. When sourced presets are added, they must:

1. cite, for every value and for each space type's conditioning status, the source document or model file, its version, and where in it the value is found (table, object, or field);
2. state every conversion applied, including unit conversions to people, W, and m³/h, the mapping from the prototype's space types to BEMGen's `SpaceType`, and the mapping of the prototype's conditioning to conditioned or unconditioned (§4, item 1);
3. be added alongside `ExampleResidentialPresets` (a new presets class, or presets built with the S2 components), leaving the example presets unchanged so existing tests keep their meaning;
4. be recorded in the decision log (D-007) and in this document.

## 4. Prototype assumptions deliberately not reproduced

Even with sourced values, BEMGen deliberately does not reproduce the following assumptions of a DOE prototype. Results must not be presented as if it did.

1. **Conditioning detail (D-038).** A preset is either conditioned, with one heating and one cooling setpoint schedule, or unconditioned, with no setpoints. Any other conditioning arrangement a source describes must be mapped to one of these two, and the mapping stated (§3). HVAC systems themselves are not part of a preset (item 5).
2. **Zoning inside dwelling units (D-009).** Rooms are never modelled. Z0 has at most one zone per dwelling unit; non-dwelling spaces are their own zones.
3. **Window layout (D-026, D-039).** The S2 generator places one window centred on each outdoor wall, sized by the preset's WWR, not the prototype's window geometry.
4. **Calendar.** Schedules are 8760 hourly values over a non-leap year (ADR-003). Schedules built from daily profiles use one weekday and one weekend profile; holidays and special days are not modelled.
5. **Systems and envelope.** A program preset holds loads, schedules, conditioning with setpoints, and WWR only: no HVAC system, construction, or material data. The pipeline ends at Grasshopper-ready inputs without simulation (D-016); what the IDF export contains is decided in ADR-010 (S6).

## 5. Building custom presets

### In C# (available from S1)

Every factory returns a `Result<T>`. Check `IsSuccess` and read `Diagnostics` before using a value built from unvalidated input: `Value` throws an `InvalidOperationException` that lists the errors. The numbers below are placeholders, like the example presets.

```csharp
using System;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;

double[] weekday = Enumerable.Repeat(0.5, 24).ToArray();
double[] weekend = Enumerable.Repeat(0.8, 24).ToArray();
Schedule occupied = Schedule.FromDailyProfiles("My Occupancy", ScheduleKind.Fraction, weekday, weekend, DayOfWeek.Monday).Value;
Schedule alwaysOn = Schedule.Constant("My Always On", ScheduleKind.Fraction, 1.0).Value;

// A conditioned dwelling unit: its program has a thermostat.
Result<Thermostat> thermostat = Thermostat.Create(
    Schedule.Constant("My Heating Setpoint", ScheduleKind.Temperature, 20.0).Value,
    Schedule.Constant("My Cooling Setpoint", ScheduleKind.Temperature, 25.0).Value);

Result<ZoneProgram> unitProgram = ZoneProgram.Create(
    new[]
    {
        LoadDefinition.Create(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.02, occupied).Value,
        LoadDefinition.Create(LoadType.Ventilation, LoadBasis.PerPerson, 30.0, occupied).Value,
        LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 4.0, alwaysOn).Value,
    },
    thermostat.Value);

// An unconditioned lobby: no thermostat, so no setpoints.
Result<ZoneProgram> lobbyProgram = ZoneProgram.Create(
    new[] { LoadDefinition.Create(LoadType.Lighting, LoadBasis.PerFloorArea, 3.0, alwaysOn).Value },
    null);

Result<ProgramPreset> unit = ProgramPreset.Create("My Dwelling Unit", SpaceType.DwellingUnit, unitProgram.Value, 0.25);
Result<ProgramPreset> lobby = ProgramPreset.Create("My Lobby", SpaceType.Lobby, lobbyProgram.Value, 0.4);

Result<ProgramPresetSet> presets = ProgramPresetSet.Create(
    new[] { unit.Value, lobby.Value, ExampleResidentialPresets.Corridor, ExampleResidentialPresets.Stair });
```

### In Grasshopper (from S2)

S2 adds components that wrap the same factories: *Schedule* (an 8760-hour schedule from a 24-hour weekday and weekend profile), *Load*, *Program Preset* (with a *Conditioned* input; conditioned presets need both setpoints), and *Example Residential Presets*. Their inputs and outputs are documented with S2. Invalid inputs surface the diagnostics listed in §1 as component runtime messages.
````

- [x] **Step 2: Check the document against the code**

Compare every number in §2 with `src/Lod.Core/Programs/ExampleResidentialPresets.cs`: per space type the load types, bases, values, schedule names and profiles, the conditioning (dwelling unit and corridor conditioned at 21 °C heating and 24 °C cooling, stair unconditioned), and the WWRs 0.3, 0.2, 0.1. Check that the relative links resolve:

```bash
git ls-files src/Lod.Core/Programs/ProgramPreset.cs src/Lod.Core/Programs/ExampleResidentialPresets.cs
```

Expected: both paths are printed.

- [x] **Step 3: Commit**

```bash
git add docs/research/program-presets.md
git commit -m "docs(research): document program presets and the illustrative example values"
```

- [x] **Merge the slice (D-004)**

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

Expected from `verify.ps1`: `0 Warning(s)`, `0 Error(s)`, `Passed: 40` on `net8.0`, `VERIFY PASSED`.

---

## Slice E — `feature/aggregation-engine`

Roadmap slice 5: `IEquivalentPropertyAggregator` implementing ADR-005 and ADR-007, with every result recording source IDs, method, and weights, and the S1 exit document `docs/architecture/domain-model.md`.

- [x] **Start the slice**

```bash
git switch main
git pull --ff-only
git switch -c feature/aggregation-engine main
```

### Task 8: Equivalent property aggregator

**Files:**
- Create: `src/Lod.Core/Aggregation/ZoneMeasures.cs`
- Create: `src/Lod.Core/Aggregation/IEquivalentPropertyAggregator.cs`
- Create: `src/Lod.Core/Aggregation/DesignMagnitudes.cs`
- Create: `src/Lod.Core/Aggregation/EquivalentPropertyAggregator.cs`
- Test: `tests/Lod.Core.Tests/Aggregation/EquivalentPropertyAggregatorTests.cs`

This is one task: the test file's helpers (`Whole`, `Measures`, `RandomSource`, `Transferred`) need `ZoneMeasures`, `SourceZoneContribution`, and `DesignMagnitudes`, so a split would not leave compiling code. Write the full test file first, watch it fail, then add the four source files.

**The rule for loads (ADR-007).** Each source *i* has design magnitude `Qᵢ = valueᵢ · Bᵢ` (people, W, or m³/h; `Bᵢ` is its basis quantity) and transfers `Tᵢ = fᵢ · Qᵢ`, where `fᵢ` is the `ExteriorWallFraction` for `PerExteriorWallArea` loads and the `AreaFraction` otherwise. The rule applies to each load component, one per load type and basis (D-047); a source without the component contributes nothing to it. The target magnitude `Q* = Σ Tᵢ` is conserved and re-expressed in the component's basis, `value* = Q* / B*`, with schedule `s*(t) = Σ Tᵢ · sᵢ(t) / Q*`, so that `Q* · s*(t) = Σ Tᵢ · sᵢ(t)` at every hour. This one rule is area weighting for per-floor-area loads (the roadmap's `p* = Σ Aᵢpᵢ / Σ Aᵢ` when the target area is the sum of the transferred areas), volume weighting for air changes per hour (D-019), occupancy weighting for per-person loads, summation for absolute loads, and exterior-wall-area weighting for per-exterior-wall loads. Occupancy is aggregated first (it is the first `LoadType`, and occupancy is never per person), so the target's occupants, summed over its occupancy components, are complete before they become the basis of per-person loads. Sources that express one load type in different bases are not an error: each basis becomes its own target component, conserved on its own (`EachBasisIsAggregatedAsItsOwnComponent`), and occupancy components add up (`OccupancyComponentsAddUp`). A positive `Q*` with a zero target basis quantity is an error (`ZeroBasisQuantity`); `Q* = 0` gives value 0, a constant-zero schedule, and an `Info` diagnostic (`ZeroLoadSchedule`), the roadmap's "density 0, flat-zero schedule, and a diagnostic".

**The rule for conditioning and setpoints (ADR-005, D-038).** A target zone is conditioned when at least one conditioned source (one with a `Thermostat`) contributes floor area to it, that is, has `AreaFraction > 0` ("any conditioned wins"); otherwise it is unconditioned and gets no thermostat. Its heating and cooling setpoints are each `θ*(t) = Σ wᵢ · θᵢ(t) / Σ wᵢ`, summed over those conditioned sources only, with `wᵢ = AreaFraction · FloorAreaᵢ`, the transferred floor area. Unconditioned sources still contribute their loads, but never weigh the setpoints. This is a prescribed control rule, not a conservation invariant, so its tests check the definition: `SetpointsAreFloorAreaWeighted`, `SetpointWeightsUseTheTransferredFloorArea`, `UnconditionedSourcesDoNotWeighSetpoints`, `OnlyUnconditionedSourcesGiveAnUnconditionedTarget`, and `ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget` (a source that contributes only exterior wall area brings no conditioned floor area). When the conditioned sources' weights sum to zero, the aggregation fails (`ZeroSetpointWeight`, tested by `ZeroSetpointWeightIsAnError` with a conditioned source of zero floor area). Merging conditioned and unconditioned sources can enlarge the conditioned floor area; from S3 validation reports that change without enforcing it (D-038).

**Traceability.** Every aggregated load carries an `AggregationRecord` (`MagnitudeConserved`, weights = transferred magnitudes `Tᵢ`), its schedule one with `MagnitudeWeighted` and the same weights, and each setpoint schedule one with `FloorAreaWeighted`, listing only the conditioned sources that contribute floor area, with weights `wᵢ` (GLOBAL.md scientific rule 2).

**Why the property tests look the way they do.** The conservation invariants (GLOBAL.md scientific rule 1) concern absolute magnitudes, not values in a basis: the installed magnitude `Q` and the scheduled magnitude `Q · s(t)` at every hour, per load component (load type and basis). A basis value legitimately changes when zones merge, so `ConservesMagnitudesAtEveryHourForRandomSources` recomputes the magnitudes on both sides with `DesignMagnitudes` and compares them with `ToleranceSettings.LoadEquals` (relative 1e-9). Every random source carries six loads that together use all five bases (occupancy and lighting per floor area, electric equipment absolute, ventilation per person, infiltration in air changes per hour, domestic hot water per exterior wall area), and alternate sources add a second component in another basis (occupancy absolute for even indices, ventilation per floor area for odd ones; every case has at least two sources, so both appear), so one test covers installed power, occupancy, and air volume flow for every basis and for mixed bases among the sources of one target (D-047). Random inputs (2 to 6 sources with random areas, heights, exterior wall areas, fractions, values, and schedules) catch weighting mistakes that hand-picked round numbers can hide; the target measures are the sums of the transferred source measures, so the target basis quantities are consistent. Each case uses `new System.Random(seed)` with an explicit seed from 1 to 5 (no global random state), so a failure names its seed and reproduces exactly. The hourly check samples every 97th hour; since 97 = 4 · 24 + 1, consecutive samples move one hour later in the day, so every hour of the day is covered. `SourceOrderDoesNotChangeTheResult` guards against results that depend on the order in which a simplifier lists its sources; floating-point sums may differ in the last bits, so it compares within tolerance, not bit for bit. `SingleWholeSourceReproducesItsProgram` checks that a single whole source returns its own loads, load schedules, and heating and cooling setpoints, hour by hour. `InvalidMeasuresAreAnError` and `ZeroSetpointWeightIsAnError` cover the remaining error paths, so every weighted average's zero-denominator guard is tested (AGENTS.md testing expectations).

**Interfaces:**
- Consumes: `ToleranceSettings` (Task 1), `ZoneId`, `Result`, `Diagnostic`, `DiagnosticCodes` (Task 2), `AggregationRecord`, `AggregationMethod`, `Schedule` (Task 3), `LoadDefinition`, `LoadType`, `LoadBasis` (Task 4), `Thermostat`, `ZoneProgram` (Task 5), `ExampleResidentialPresets` (Task 6, in a test), `TestPrograms` including `Unconditioned(...)` (Task 5).
- Produces (namespace `Lod.Core.Aggregation`):
  - `public sealed record ZoneMeasures(double FloorArea, double Volume, double ExteriorWallArea)` with `public bool IsValid { get; }`
  - `public sealed record SourceZoneContribution(ZoneId Zone, ZoneProgram Program, ZoneMeasures Measures, double AreaFraction, double ExteriorWallFraction)`
  - `public interface IEquivalentPropertyAggregator { Result<ZoneProgram> Aggregate(ZoneId target, ZoneMeasures targetMeasures, IReadOnlyList<SourceZoneContribution> sources); }`
  - `public static class DesignMagnitudes` with `public static double BasisQuantity(LoadBasis basis, ZoneMeasures measures, double occupants)`, `public static double Occupants(ZoneProgram program, ZoneMeasures measures)`, `public static double Of(LoadDefinition load, ZoneMeasures measures, double occupants)`
  - `public sealed class EquivalentPropertyAggregator : IEquivalentPropertyAggregator` with `public EquivalentPropertyAggregator(ToleranceSettings tolerances)`
  - Aggregated schedule names: `"<target> <LoadType> <LoadBasis>"`, `"<target> Heating Setpoint"`, `"<target> Cooling Setpoint"`

- [x] **Step 1: Write the failing tests**

Create `tests/Lod.Core.Tests/Aggregation/EquivalentPropertyAggregatorTests.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Aggregation;

public sealed class EquivalentPropertyAggregatorTests
{
    private static readonly ZoneId Target = new("T");
    private readonly EquivalentPropertyAggregator _aggregator = new(ToleranceSettings.Default);

    [Fact]
    public void AreaDensityIsAreaWeighted()
    {
        SourceZoneContribution a = Whole("A", 10.0, TestPrograms.Program(loads: TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0)));
        SourceZoneContribution b = Whole("B", 30.0, TestPrograms.Program(loads: TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 1.0)));

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(40.0), new[] { a, b }).Value;

        LoadDefinition lighting = result.Find(LoadType.Lighting, LoadBasis.PerFloorArea)!;
        Assert.Equal(LoadBasis.PerFloorArea, lighting.Basis);
        Assert.Equal((50.0 + 30.0) / 40.0, lighting.Value, 12);
        Assert.Equal(AggregationMethod.MagnitudeConserved, lighting.Aggregation!.Method);
        Assert.Equal(new[] { 50.0, 30.0 }, lighting.Aggregation.Weights);
    }

    [Fact]
    public void SchedulesAreMagnitudeWeighted()
    {
        LoadDefinition onAtNine = TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 5.0, TestPrograms.FractionAt(9, 1.0, 0.0));
        LoadDefinition halfAlways = TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, 1.0, TestPrograms.Fraction(0.5));
        SourceZoneContribution a = Whole("A", 10.0, TestPrograms.Program(loads: onAtNine));
        SourceZoneContribution b = Whole("B", 30.0, TestPrograms.Program(loads: halfAlways));

        LoadDefinition lighting = _aggregator.Aggregate(Target, Measures(40.0), new[] { a, b }).Value.Find(LoadType.Lighting, LoadBasis.PerFloorArea)!;

        Assert.Equal(((50.0 * 1.0) + (30.0 * 0.5)) / 80.0, lighting.Schedule[9], 12);
        Assert.Equal((30.0 * 0.5) / 80.0, lighting.Schedule[10], 12);
        Assert.Equal(AggregationMethod.MagnitudeWeighted, lighting.Schedule.Aggregation!.Method);
    }

    [Fact]
    public void AirChangesAreVolumeWeighted()
    {
        SourceZoneContribution a = Whole("A", 40.0, TestPrograms.Program(loads: TestPrograms.Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 0.5)), height: 2.5);
        SourceZoneContribution b = Whole("B", 100.0, TestPrograms.Program(loads: TestPrograms.Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, 1.0)), height: 3.0);

        LoadDefinition infiltration = _aggregator
            .Aggregate(Target, new ZoneMeasures(140.0, 100.0 + 300.0, 0.0), new[] { a, b })
            .Value.Find(LoadType.Infiltration, LoadBasis.AirChangesPerHour)!;

        Assert.Equal(((100.0 * 0.5) + (300.0 * 1.0)) / 400.0, infiltration.Value, 12);
    }

    [Fact]
    public void PerPersonLoadsAreOccupancyWeighted()
    {
        ZoneProgram dense = TestPrograms.Program(loads: new[]
        {
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.1),
            TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 30.0),
        });
        ZoneProgram sparse = TestPrograms.Program(loads: new[]
        {
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.01),
            TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 10.0),
        });

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(200.0), new[] { Whole("A", 100.0, dense), Whole("B", 100.0, sparse) }).Value;

        Assert.Equal(11.0 / 200.0, result.Find(LoadType.Occupancy, LoadBasis.PerFloorArea)!.Value, 12);
        Assert.Equal(((10.0 * 30.0) + (1.0 * 10.0)) / 11.0, result.Find(LoadType.Ventilation, LoadBasis.PerPerson)!.Value, 12);
    }

    [Fact]
    public void ExteriorWallLoadsUseTheExteriorWallFraction()
    {
        ZoneProgram program = TestPrograms.Program(loads: TestPrograms.Load(LoadType.Infiltration, LoadBasis.PerExteriorWallArea, 2.0));
        var source = new SourceZoneContribution(new ZoneId("A"), program, new ZoneMeasures(50.0, 150.0, 30.0), AreaFraction: 0.2, ExteriorWallFraction: 1.0);

        LoadDefinition infiltration = _aggregator.Aggregate(Target, new ZoneMeasures(10.0, 30.0, 30.0), new[] { source }).Value.Find(LoadType.Infiltration, LoadBasis.PerExteriorWallArea)!;

        Assert.Equal(2.0, infiltration.Value, 12);
    }

    [Fact]
    public void PositiveLoadWithoutBasisQuantityIsAnError()
    {
        ZoneProgram program = TestPrograms.Program(loads: TestPrograms.Load(LoadType.Infiltration, LoadBasis.PerExteriorWallArea, 2.0));
        var source = new SourceZoneContribution(new ZoneId("A"), program, new ZoneMeasures(50.0, 150.0, 30.0), AreaFraction: 0.5, ExteriorWallFraction: 0.5);

        Result<ZoneProgram> result = _aggregator.Aggregate(Target, new ZoneMeasures(25.0, 75.0, 0.0), new[] { source });

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ZeroBasisQuantity && d.Subject == "T");
    }

    [Fact]
    public void EachBasisIsAggregatedAsItsOwnComponent()
    {
        ZoneProgram perPerson = TestPrograms.Program(loads: new[]
        {
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.1),
            TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 30.0, TestPrograms.FractionAt(9, 1.0, 0.0)),
        });
        ZoneProgram perArea = TestPrograms.Program(loads: TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerFloorArea, 2.0, TestPrograms.Fraction(0.5)));

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(200.0), new[] { Whole("A", 100.0, perPerson), Whole("B", 100.0, perArea) }).Value;

        // A: 10 people x 30 m³/h = 300 m³/h at hour 9 only. B: 100 m² x 2 m³/h = 200 m³/h, always at half.
        LoadDefinition person = result.Find(LoadType.Ventilation, LoadBasis.PerPerson)!;
        LoadDefinition area = result.Find(LoadType.Ventilation, LoadBasis.PerFloorArea)!;
        Assert.Equal(300.0 / 10.0, person.Value, 12);
        Assert.Equal(200.0 / 200.0, area.Value, 12);
        Assert.Equal(1.0, person.Schedule[9], 12);
        Assert.Equal(0.0, person.Schedule[10], 12);
        Assert.Equal(0.5, area.Schedule[10], 12);
        Assert.Equal(new[] { new ZoneId("A") }, person.Aggregation!.Sources);
        Assert.Equal(new[] { new ZoneId("B") }, area.Aggregation!.Sources);
    }

    [Fact]
    public void OccupancyComponentsAddUp()
    {
        ZoneProgram program = TestPrograms.Program(loads: new[]
        {
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, 0.1),
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.Absolute, 5.0),
            TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, 10.0),
        });

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(100.0), new[] { Whole("A", 100.0, program) }).Value;

        Assert.Equal(15.0, DesignMagnitudes.Occupants(program, Measures(100.0)), 12);
        Assert.Equal(15.0, DesignMagnitudes.Occupants(result, Measures(100.0)), 12);
        Assert.Equal(10.0, result.Find(LoadType.Ventilation, LoadBasis.PerPerson)!.Value, 12);
    }

    [Fact]
    public void ZeroLoadGivesZeroValueAndZeroSchedule()
    {
        SourceZoneContribution a = Whole("A", 10.0, TestPrograms.Program(loads: TestPrograms.Load(LoadType.GasEquipment, LoadBasis.PerFloorArea, 0.0)));

        Result<ZoneProgram> result = _aggregator.Aggregate(Target, Measures(10.0), new[] { a });

        LoadDefinition gas = result.Value.Find(LoadType.GasEquipment, LoadBasis.PerFloorArea)!;
        Assert.Equal(0.0, gas.Value);
        Assert.All(gas.Schedule.Values, v => Assert.Equal(0.0, v));
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ZeroLoadSchedule && d.Severity == DiagnosticSeverity.Info);
    }

    [Fact]
    public void SetpointsAreFloorAreaWeighted()
    {
        SourceZoneContribution a = Whole("A", 10.0, TestPrograms.Program(heating: 20.0, cooling: 26.0));
        SourceZoneContribution b = Whole("B", 30.0, TestPrograms.Program(heating: 24.0, cooling: 22.0));

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(40.0), new[] { a, b }).Value;

        Assert.Equal(23.0, result.Thermostat!.HeatingSetpoint[0], 12);
        Assert.Equal(23.0, result.Thermostat!.CoolingSetpoint[100], 12);
        Assert.Equal(AggregationMethod.FloorAreaWeighted, result.Thermostat!.HeatingSetpoint.Aggregation!.Method);
        Assert.Equal(new[] { 10.0, 30.0 }, result.Thermostat.HeatingSetpoint.Aggregation.Weights);
    }

    [Fact]
    public void SetpointWeightsUseTheTransferredFloorArea()
    {
        SourceZoneContribution a = new(new ZoneId("A"), TestPrograms.Program(heating: 20.0), new ZoneMeasures(100.0, 300.0, 0.0), 0.1, 0.0);
        SourceZoneContribution b = Whole("B", 10.0, TestPrograms.Program(heating: 24.0));

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(20.0), new[] { a, b }).Value;

        Assert.Equal(22.0, result.Thermostat!.HeatingSetpoint[0], 12);
    }

    [Fact]
    public void NoSourcesIsAnError()
    {
        Assert.Contains(_aggregator.Aggregate(Target, Measures(10.0), new SourceZoneContribution[0]).Diagnostics, d => d.Code == DiagnosticCodes.NoSources);
    }

    [Fact]
    public void FractionsOutsideZeroToOneAreAnError()
    {
        var source = new SourceZoneContribution(new ZoneId("A"), TestPrograms.Program(), Measures(10.0), 1.5, 0.0);

        Assert.Contains(_aggregator.Aggregate(Target, Measures(10.0), new[] { source }).Diagnostics, d => d.Code == DiagnosticCodes.FractionOutOfRange);
    }

    [Fact]
    public void InvalidMeasuresAreAnError()
    {
        Result<ZoneProgram> result = _aggregator.Aggregate(Target, new ZoneMeasures(-1.0, 30.0, 0.0), new[] { Whole("A", 10.0, TestPrograms.Program()) });

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.InvalidMeasures && d.Subject == "T");
    }

    [Fact]
    public void UnconditionedSourcesDoNotWeighSetpoints()
    {
        SourceZoneContribution conditioned = Whole("A", 10.0, TestPrograms.Program(heating: 20.0, cooling: 26.0));
        SourceZoneContribution stair = Whole("B", 30.0, TestPrograms.Unconditioned());

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(40.0), new[] { conditioned, stair }).Value;

        Assert.True(result.IsConditioned);
        Assert.Equal(20.0, result.Thermostat!.HeatingSetpoint[0], 12);
        Assert.Equal(new[] { new ZoneId("A") }, result.Thermostat.HeatingSetpoint.Aggregation!.Sources);
    }

    [Fact]
    public void OnlyUnconditionedSourcesGiveAnUnconditionedTarget()
    {
        ZoneProgram result = _aggregator.Aggregate(Target, Measures(40.0), new[] { Whole("A", 10.0, TestPrograms.Unconditioned()), Whole("B", 30.0, TestPrograms.Unconditioned()) }).Value;

        Assert.False(result.IsConditioned);
    }

    [Fact]
    public void ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget()
    {
        // A source contributing only exterior wall area brings no conditioned floor area (D-038).
        var facadeOnly = new SourceZoneContribution(new ZoneId("A"), TestPrograms.Program(), new ZoneMeasures(10.0, 30.0, 12.0), AreaFraction: 0.0, ExteriorWallFraction: 1.0);

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(10.0), new[] { facadeOnly, Whole("B", 10.0, TestPrograms.Unconditioned()) }).Value;

        Assert.False(result.IsConditioned);
    }

    [Fact]
    public void ZeroSetpointWeightIsAnError()
    {
        // A conditioned source with zero floor area contributes area fraction 1 but weight 0.
        SourceZoneContribution empty = Whole("A", 0.0, TestPrograms.Program());

        Result<ZoneProgram> result = _aggregator.Aggregate(Target, Measures(10.0), new[] { empty });

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.ZeroSetpointWeight);
    }

    [Fact]
    public void SingleWholeSourceReproducesItsProgram()
    {
        ZoneProgram program = ExampleResidentialPresets.DwellingUnit.Program;

        ZoneProgram result = _aggregator.Aggregate(Target, Measures(60.0), new[] { Whole("A", 60.0, program) }).Value;

        Assert.Equal(program.Loads.Select(l => (l.Type, l.Basis)), result.Loads.Select(l => (l.Type, l.Basis)));
        foreach (LoadDefinition expected in program.Loads)
        {
            LoadDefinition actual = result.Find(expected.Type, expected.Basis)!;
            Assert.Equal(expected.Value, actual.Value, 12);
            for (int hour = 0; hour < Schedule.HoursPerYear; hour++)
            {
                Assert.Equal(expected.Schedule[hour], actual.Schedule[hour], 12);
            }
        }

        for (int hour = 0; hour < Schedule.HoursPerYear; hour++)
        {
            Assert.Equal(program.Thermostat!.HeatingSetpoint[hour], result.Thermostat!.HeatingSetpoint[hour], 12);
            Assert.Equal(program.Thermostat!.CoolingSetpoint[hour], result.Thermostat!.CoolingSetpoint[hour], 12);
        }
    }

    [Theory]
    [InlineData(1)]
    [InlineData(2)]
    [InlineData(3)]
    [InlineData(4)]
    [InlineData(5)]
    public void ConservesMagnitudesAtEveryHourForRandomSources(int seed)
    {
        ToleranceSettings tolerances = ToleranceSettings.Default;
        var random = new System.Random(seed);
        SourceZoneContribution[] sources = Enumerable.Range(0, random.Next(2, 7)).Select(i => RandomSource(random, i)).ToArray();
        var target = new ZoneMeasures(
            sources.Sum(s => s.AreaFraction * s.Measures.FloorArea),
            sources.Sum(s => s.AreaFraction * s.Measures.Volume),
            sources.Sum(s => s.ExteriorWallFraction * s.Measures.ExteriorWallArea));

        ZoneProgram result = _aggregator.Aggregate(Target, target, sources).Value;

        double targetOccupants = DesignMagnitudes.Occupants(result, target);
        Assert.True(tolerances.LoadEquals(sources.Sum(s => s.AreaFraction * DesignMagnitudes.Occupants(s.Program, s.Measures)), targetOccupants));
        foreach (LoadDefinition load in result.Loads)
        {
            List<(double Transferred, LoadDefinition Load)> inputs = sources
                .Where(s => s.Program.Find(load.Type, load.Basis) is not null)
                .Select(s => (Transferred(s, s.Program.Find(load.Type, load.Basis)!), s.Program.Find(load.Type, load.Basis)!))
                .ToList();
            double magnitude = DesignMagnitudes.Of(load, target, targetOccupants);
            Assert.True(tolerances.LoadEquals(inputs.Sum(x => x.Transferred), magnitude), $"{load.Type} {load.Basis} installed magnitude");
            for (int hour = 0; hour < Schedule.HoursPerYear; hour += 97)
            {
                double expected = inputs.Sum(x => x.Transferred * x.Load.Schedule[hour]);
                Assert.True(tolerances.LoadEquals(expected, magnitude * load.Schedule[hour]), $"{load.Type} {load.Basis} hour {hour}");
            }
        }
    }

    [Fact]
    public void SourceOrderDoesNotChangeTheResult()
    {
        var random = new System.Random(7);
        SourceZoneContribution[] sources = Enumerable.Range(0, 4).Select(i => RandomSource(random, i)).ToArray();
        var target = new ZoneMeasures(500.0, 1500.0, 200.0);

        ZoneProgram forward = _aggregator.Aggregate(Target, target, sources).Value;
        ZoneProgram reversed = _aggregator.Aggregate(Target, target, sources.Reverse().ToArray()).Value;

        foreach (LoadDefinition load in forward.Loads)
        {
            LoadDefinition other = reversed.Find(load.Type, load.Basis)!;
            Assert.True(ToleranceSettings.Default.LoadEquals(load.Value, other.Value));
            Assert.True(ToleranceSettings.Default.ScheduleEquals(load.Schedule[4000], other.Schedule[4000]));
        }

        Assert.True(ToleranceSettings.Default.ScheduleEquals(forward.Thermostat!.HeatingSetpoint[10], reversed.Thermostat!.HeatingSetpoint[10]));
    }

    private static double Transferred(SourceZoneContribution source, LoadDefinition load)
    {
        double fraction = load.Basis == LoadBasis.PerExteriorWallArea ? source.ExteriorWallFraction : source.AreaFraction;
        return fraction * DesignMagnitudes.Of(load, source.Measures, DesignMagnitudes.Occupants(source.Program, source.Measures));
    }

    private static SourceZoneContribution RandomSource(System.Random random, int index)
    {
        double area = 10.0 + (random.NextDouble() * 90.0);
        double height = 2.5 + random.NextDouble();
        var measures = new ZoneMeasures(area, area * height, 5.0 + (random.NextDouble() * 40.0));
        var loads = new List<LoadDefinition>
        {
            TestPrograms.Load(LoadType.Occupancy, LoadBasis.PerFloorArea, random.NextDouble() * 0.1, TestPrograms.FractionAt(random.Next(8760), random.NextDouble(), random.NextDouble())),
            TestPrograms.Load(LoadType.Lighting, LoadBasis.PerFloorArea, random.NextDouble() * 10.0, TestPrograms.FractionAt(random.Next(8760), random.NextDouble(), random.NextDouble())),
            TestPrograms.Load(LoadType.ElectricEquipment, LoadBasis.Absolute, random.NextDouble() * 500.0, TestPrograms.Fraction(random.NextDouble())),
            TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerPerson, random.NextDouble() * 30.0, TestPrograms.Fraction(random.NextDouble())),
            TestPrograms.Load(LoadType.Infiltration, LoadBasis.AirChangesPerHour, random.NextDouble(), TestPrograms.Fraction(random.NextDouble())),
            TestPrograms.Load(LoadType.DomesticHotWater, LoadBasis.PerExteriorWallArea, random.NextDouble(), TestPrograms.Fraction(random.NextDouble())),
        };

        // Alternate sources add a second component in another basis (D-047).
        loads.Add(index % 2 == 0
            ? TestPrograms.Load(LoadType.Occupancy, LoadBasis.Absolute, random.NextDouble() * 5.0, TestPrograms.Fraction(random.NextDouble()))
            : TestPrograms.Load(LoadType.Ventilation, LoadBasis.PerFloorArea, random.NextDouble() * 3.0, TestPrograms.Fraction(random.NextDouble())));
        ZoneProgram program = TestPrograms.Program(
            heating: 18.0 + (random.NextDouble() * 4.0),
            cooling: 23.0 + (random.NextDouble() * 4.0),
            loads: loads.ToArray());
        return new SourceZoneContribution(new ZoneId($"S{index}"), program, measures, random.NextDouble(), random.NextDouble());
    }

    private static SourceZoneContribution Whole(string id, double area, ZoneProgram program, double height = 3.0) =>
        new(new ZoneId(id), program, new ZoneMeasures(area, area * height, 0.0), AreaFraction: 1.0, ExteriorWallFraction: 1.0);

    private static ZoneMeasures Measures(double area) => new(area, area * 3.0, 0.0);
}
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Aggregation.EquivalentPropertyAggregatorTests"
```

Expected: the build fails (the namespace `Lod.Core.Aggregation` exists since Task 3, so the errors name the missing types), including:

```text
tests\Lod.Core.Tests\Aggregation\EquivalentPropertyAggregatorTests.cs(16,22): error CS0246: The type or namespace name 'EquivalentPropertyAggregator' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Aggregation\EquivalentPropertyAggregatorTests.cs(330,39): error CS0246: The type or namespace name 'SourceZoneContribution' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Aggregation\EquivalentPropertyAggregatorTests.cs(365,20): error CS0246: The type or namespace name 'ZoneMeasures' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Create `ZoneMeasures` and `SourceZoneContribution`**

Measures are validated by the aggregator (`InvalidMeasures`), not on construction, so that an invalid input becomes a diagnostic instead of an exception. Create `src/Lod.Core/Aggregation/ZoneMeasures.cs`:

```csharp
using Lod.Core.Common;
using Lod.Core.Programs;

namespace Lod.Core.Aggregation;

/// <summary>
/// The geometric quantities that load bases refer to (ADR-007).
/// </summary>
/// <param name="FloorArea">Floor area, m².</param>
/// <param name="Volume">Air volume, m³.</param>
/// <param name="ExteriorWallArea">Gross area of walls with an outdoor boundary, windows included, m².</param>
public sealed record ZoneMeasures(double FloorArea, double Volume, double ExteriorWallArea)
{
    /// <summary>Whether every measure is finite and non-negative.</summary>
    public bool IsValid => IsNonNegative(FloorArea) && IsNonNegative(Volume) && IsNonNegative(ExteriorWallArea);

    private static bool IsNonNegative(double value) => !double.IsNaN(value) && !double.IsInfinity(value) && value >= 0;
}

/// <summary>
/// What one source zone contributes to one target zone.
/// </summary>
/// <param name="Zone">Source zone.</param>
/// <param name="Program">Source program.</param>
/// <param name="Measures">Measures of the whole source zone.</param>
/// <param name="AreaFraction">Share of the source's floor area (and volume, occupants, and absolute loads) assigned to the target, in [0, 1].</param>
/// <param name="ExteriorWallFraction">Share of the source's exterior wall area assigned to the target's exterior walls, in [0, 1].</param>
public sealed record SourceZoneContribution(ZoneId Zone, ZoneProgram Program, ZoneMeasures Measures, double AreaFraction, double ExteriorWallFraction);
```

- [x] **Step 4: Create the aggregator interface**

The interface knows nothing about geometry or rezoning methods (spec §9); callers supply the fractions. Create `src/Lod.Core/Aggregation/IEquivalentPropertyAggregator.cs`:

```csharp
using System.Collections.Generic;
using Lod.Core.Common;
using Lod.Core.Programs;

namespace Lod.Core.Aggregation;

/// <summary>
/// Computes a target zone's program from the source zones mapped into it (spec §9). Independent of any rezoning method.
/// </summary>
public interface IEquivalentPropertyAggregator
{
    /// <summary>Aggregates the contributions of <paramref name="sources"/> into one program for <paramref name="target"/>.</summary>
    /// <param name="target">Target zone ID, used for naming and traceability.</param>
    /// <param name="targetMeasures">Measures of the target zone.</param>
    /// <param name="sources">Contributions of the source zones.</param>
    /// <returns>The target program, or errors when a load cannot be expressed in the target.</returns>
    public Result<ZoneProgram> Aggregate(ZoneId target, ZoneMeasures targetMeasures, IReadOnlyList<SourceZoneContribution> sources);
}
```

- [x] **Step 5: Create `DesignMagnitudes`**

Create `src/Lod.Core/Aggregation/DesignMagnitudes.cs`:

```csharp
using System;
using System.Linq;
using Lod.Core.Loads;
using Lod.Core.Programs;

namespace Lod.Core.Aggregation;

/// <summary>
/// Converts between a load's value in its basis and its absolute design magnitude (ADR-007): magnitude = value × basis quantity.
/// </summary>
public static class DesignMagnitudes
{
    /// <summary>The basis quantity of a zone: floor area, volume, exterior wall area, occupants, or 1 for absolute loads.</summary>
    /// <param name="basis">Load basis.</param>
    /// <param name="measures">Zone measures.</param>
    /// <param name="occupants">Design occupants of the zone, used by <see cref="LoadBasis.PerPerson"/>.</param>
    /// <returns>The basis quantity.</returns>
    public static double BasisQuantity(LoadBasis basis, ZoneMeasures measures, double occupants) => basis switch
    {
        LoadBasis.PerFloorArea => measures.FloorArea,
        LoadBasis.PerPerson => occupants,
        LoadBasis.Absolute => 1.0,
        LoadBasis.PerExteriorWallArea => measures.ExteriorWallArea,
        LoadBasis.AirChangesPerHour => measures.Volume,
        _ => throw new ArgumentOutOfRangeException(nameof(basis), basis, "Unknown load basis."),
    };

    /// <summary>Design occupants of a zone: the summed magnitude of its occupancy loads, or 0 without one.</summary>
    /// <param name="program">Zone program.</param>
    /// <param name="measures">Zone measures.</param>
    /// <returns>Number of people at design occupancy.</returns>
    public static double Occupants(ZoneProgram program, ZoneMeasures measures) =>
        program.Loads.Where(l => l.Type == LoadType.Occupancy).Sum(l => l.Value * BasisQuantity(l.Basis, measures, occupants: 0.0));

    /// <summary>Absolute design magnitude of a load in a zone.</summary>
    /// <param name="load">The load.</param>
    /// <param name="measures">Zone measures.</param>
    /// <param name="occupants">Design occupants of the zone.</param>
    /// <returns>Magnitude in people, W, or m³/h depending on <see cref="LoadDefinition.Type"/>.</returns>
    public static double Of(LoadDefinition load, ZoneMeasures measures, double occupants) =>
        load.Value * BasisQuantity(load.Basis, measures, occupants);
}
```

- [x] **Step 6: Implement `EquivalentPropertyAggregator`**

Create `src/Lod.Core/Aggregation/EquivalentPropertyAggregator.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;

namespace Lod.Core.Aggregation;

/// <summary>
/// The project's aggregation rules (ADR-005, ADR-007).
/// <list type="bullet">
/// <item>Loads are aggregated per component, one per load type and basis (D-047); a source without a component contributes nothing to it.
/// Each source transfers <c>Tᵢ = fᵢ·Qᵢ</c> of its design magnitude <c>Qᵢ</c>, where <c>fᵢ</c> is the exterior-wall fraction for
/// <see cref="LoadBasis.PerExteriorWallArea"/> loads and the area fraction otherwise. The target magnitude <c>Q* = ΣTᵢ</c> is conserved and
/// re-expressed in the component's basis: <c>value* = Q* / B*</c>. This gives area weighting for per-area loads, volume weighting for ACH (D-019),
/// and occupancy weighting for per-person loads.</item>
/// <item>Load schedules: <c>s*(t) = ΣTᵢ·sᵢ(t) / Q*</c>, so the scheduled magnitude is conserved at every hour. A zero <c>Q*</c> gives value 0 and a constant zero schedule.</item>
/// <item>Conditioning and setpoints (D-038): the target is conditioned when any source contributing floor area is conditioned; its setpoints are
/// floor-area weighted over those conditioned sources, <c>T*(t) = Σwᵢ·Tᵢ(t) / Σwᵢ</c> with <c>wᵢ = fᵢ·Aᵢ</c>. A prescribed control rule, not a
/// conservation invariant.</item>
/// </list>
/// </summary>
public sealed class EquivalentPropertyAggregator : IEquivalentPropertyAggregator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances for fraction range checks.</param>
    public EquivalentPropertyAggregator(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <inheritdoc />
    public Result<ZoneProgram> Aggregate(ZoneId target, ZoneMeasures targetMeasures, IReadOnlyList<SourceZoneContribution> sources)
    {
        var diagnostics = new List<Diagnostic>();
        ValidateInputs(target, targetMeasures, sources, diagnostics);
        if (diagnostics.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            return Result.Failure<ZoneProgram>(diagnostics);
        }

        double[] sourceOccupants = sources.Select(s => DesignMagnitudes.Occupants(s.Program, s.Measures)).ToArray();
        double targetOccupants = 0.0;
        var loads = new List<LoadDefinition>();
        // Occupancy sorts first and is never per person, so the target's occupants are complete before any per-person component.
        (LoadType Type, LoadBasis Basis)[] components = sources
            .SelectMany(s => s.Program.Loads)
            .Select(l => (l.Type, l.Basis))
            .Distinct()
            .OrderBy(c => c.Type)
            .ThenBy(c => c.Basis)
            .ToArray();
        foreach ((LoadType type, LoadBasis basis) in components)
        {
            LoadDefinition? load = AggregateLoad(target, targetMeasures, sources, sourceOccupants, targetOccupants, type, basis, diagnostics);
            if (load is null)
            {
                continue;
            }

            if (type == LoadType.Occupancy)
            {
                targetOccupants += DesignMagnitudes.Of(load, targetMeasures, occupants: 0.0);
            }

            loads.Add(load);
        }

        SourceZoneContribution[] conditioned = sources.Where(s => s.Program.Thermostat is not null && s.AreaFraction > 0.0).ToArray();
        Thermostat? thermostat = null;
        if (conditioned.Length > 0)
        {
            Schedule? heating = AggregateSetpoint(target, "Heating Setpoint", conditioned, s => s.Program.Thermostat!.HeatingSetpoint, diagnostics);
            Schedule? cooling = AggregateSetpoint(target, "Cooling Setpoint", conditioned, s => s.Program.Thermostat!.CoolingSetpoint, diagnostics);
            thermostat = heating is null || cooling is null ? null : Thermostat.Create(heating, cooling).Value;
        }

        if (diagnostics.Any(d => d.Severity == DiagnosticSeverity.Error))
        {
            return Result.Failure<ZoneProgram>(diagnostics);
        }

        Result<ZoneProgram> program = ZoneProgram.Create(loads, thermostat);
        return program.IsSuccess
            ? Result.Success(program.Value, diagnostics.Concat(program.Diagnostics))
            : Result.Failure<ZoneProgram>(diagnostics.Concat(program.Diagnostics));
    }

    private void ValidateInputs(ZoneId target, ZoneMeasures targetMeasures, IReadOnlyList<SourceZoneContribution> sources, List<Diagnostic> diagnostics)
    {
        if (sources.Count == 0)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.NoSources, "A target zone needs at least one source zone.", target.Value));
        }

        if (!targetMeasures.IsValid)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.InvalidMeasures, $"Target measures are invalid: {targetMeasures}.", target.Value));
        }

        foreach (SourceZoneContribution source in sources)
        {
            if (!source.Measures.IsValid)
            {
                diagnostics.Add(Diagnostic.Error(DiagnosticCodes.InvalidMeasures, $"Source measures are invalid: {source.Measures}.", source.Zone.Value));
            }

            if (!IsFraction(source.AreaFraction) || !IsFraction(source.ExteriorWallFraction))
            {
                diagnostics.Add(Diagnostic.Error(
                    DiagnosticCodes.FractionOutOfRange,
                    $"Fractions must be in [0, 1], got area {source.AreaFraction} and exterior wall {source.ExteriorWallFraction}.",
                    source.Zone.Value));
            }
        }
    }

    private bool IsFraction(double value) =>
        !double.IsNaN(value) && value >= -_tolerances.RelativeArea && value <= 1.0 + _tolerances.RelativeArea;

    private static LoadDefinition? AggregateLoad(
        ZoneId target,
        ZoneMeasures targetMeasures,
        IReadOnlyList<SourceZoneContribution> sources,
        double[] sourceOccupants,
        double targetOccupants,
        LoadType type,
        LoadBasis basis,
        List<Diagnostic> diagnostics)
    {
        var contributing = new List<(SourceZoneContribution Source, LoadDefinition Load, double Transferred)>();
        for (int i = 0; i < sources.Count; i++)
        {
            LoadDefinition? load = sources[i].Program.Find(type, basis);
            if (load is null)
            {
                continue;
            }

            double fraction = load.Basis == LoadBasis.PerExteriorWallArea ? sources[i].ExteriorWallFraction : sources[i].AreaFraction;
            contributing.Add((sources[i], load, fraction * DesignMagnitudes.Of(load, sources[i].Measures, sourceOccupants[i])));
        }

        double magnitude = contributing.Sum(c => c.Transferred);
        double basisQuantity = DesignMagnitudes.BasisQuantity(basis, targetMeasures, targetOccupants);
        var record = new AggregationRecord(AggregationMethod.MagnitudeConserved, contributing.Select(c => c.Source.Zone), contributing.Select(c => c.Transferred));
        string scheduleName = $"{target.Value} {type} {basis}";

        if (magnitude <= 0.0)
        {
            diagnostics.Add(Diagnostic.Info(DiagnosticCodes.ZeroLoadSchedule, $"{type} {basis} has zero design magnitude; schedule set to constant 0.", target.Value));
            Schedule zero = Schedule.Create(
                scheduleName,
                ScheduleKind.Fraction,
                new double[Schedule.HoursPerYear],
                new AggregationRecord(AggregationMethod.MagnitudeWeighted, record.Sources, record.Weights)).Value;
            return LoadDefinition.Create(type, basis, 0.0, zero, record).Value;
        }

        if (basisQuantity <= 0.0)
        {
            diagnostics.Add(Diagnostic.Error(
                DiagnosticCodes.ZeroBasisQuantity,
                $"{type} of {magnitude} cannot be expressed {basis} because the target's basis quantity is 0.",
                target.Value));
            return null;
        }

        var values = new double[Schedule.HoursPerYear];
        foreach ((SourceZoneContribution _, LoadDefinition load, double transferred) in contributing)
        {
            for (int hour = 0; hour < values.Length; hour++)
            {
                values[hour] += transferred * load.Schedule[hour];
            }
        }

        for (int hour = 0; hour < values.Length; hour++)
        {
            // A weighted mean of fractions stays in [0, 1]; clamping only removes floating-point noise.
            values[hour] = Math.Min(1.0, Math.Max(0.0, values[hour] / magnitude));
        }

        Schedule schedule = Schedule.Create(
            scheduleName,
            ScheduleKind.Fraction,
            values,
            new AggregationRecord(AggregationMethod.MagnitudeWeighted, record.Sources, record.Weights)).Value;
        return LoadDefinition.Create(type, basis, magnitude / basisQuantity, schedule, record).Value;
    }

    private static Schedule? AggregateSetpoint(
        ZoneId target,
        string label,
        IReadOnlyList<SourceZoneContribution> sources,
        Func<SourceZoneContribution, Schedule> select,
        List<Diagnostic> diagnostics)
    {
        double[] weights = sources.Select(s => s.AreaFraction * s.Measures.FloorArea).ToArray();
        double total = weights.Sum();
        if (total <= 0.0)
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.ZeroSetpointWeight, $"{label}: conditioned source floor-area weights sum to 0.", target.Value));
            return null;
        }

        var values = new double[Schedule.HoursPerYear];
        for (int i = 0; i < sources.Count; i++)
        {
            Schedule schedule = select(sources[i]);
            for (int hour = 0; hour < values.Length; hour++)
            {
                values[hour] += weights[i] * schedule[hour];
            }
        }

        for (int hour = 0; hour < values.Length; hour++)
        {
            values[hour] /= total;
        }

        var record = new AggregationRecord(AggregationMethod.FloorAreaWeighted, sources.Select(s => s.Zone), weights);
        return Schedule.Create($"{target.Value} {label}", ScheduleKind.Temperature, values, record).Value;
    }
}
```

- [x] **Step 7: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Aggregation.EquivalentPropertyAggregatorTests"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    25, Skipped:     0, Total:    25, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 8: Run the whole core test project**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected:

```text
Passed!  - Failed:     0, Passed:    65, Skipped:     0, Total:    65, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 9: Commit**

```bash
git add src/Lod.Core/Aggregation/ZoneMeasures.cs src/Lod.Core/Aggregation/IEquivalentPropertyAggregator.cs src/Lod.Core/Aggregation/DesignMagnitudes.cs src/Lod.Core/Aggregation/EquivalentPropertyAggregator.cs tests/Lod.Core.Tests/Aggregation/EquivalentPropertyAggregatorTests.cs
git commit -m "feature(aggregation): add equivalent property aggregator conserving load magnitudes"
```

### Task 9: Domain model document

**Files:**
- Create: `docs/architecture/domain-model.md`

The roadmap's S1 exit criterion. It describes the S1 types and how they relate (with a text diagram), the aggregation rules, units, diagnostics, the immutability approach and why `System.Collections.Immutable` is not used, traceability through `AggregationRecord`, what arrives in S2, and the names that differ from the roadmap and the specification.

**Interfaces:**
- Consumes: all S1 types; `docs/research/program-presets.md` (Task 7).
- Produces: `docs/architecture/domain-model.md`, to be extended by later stages.

- [x] **Step 1: Write the document**

Create `docs/architecture/domain-model.md` with exactly this content:

````markdown
# Domain Model

> **Status:** Current as of S1 (`v0.1.0`) · **Date:** 2026-10-01 · **Scope:** `Lod.Core.Common`, `Lod.Core.Schedules`, `Lod.Core.Loads`, `Lod.Core.Programs`, `Lod.Core.Aggregation`

This document describes the domain types that exist after stage S1 of the [implementation roadmap](../plans/2026-09-30-implementation-roadmap.md) and how they relate. S1 deliberately has no geometry: a zone appears only as a `ZoneId` and three measures (floor area, volume, exterior wall area). That is enough to define and test the aggregation rules (ADR-005, ADR-007) before any plan exists. Geometry, zones, surfaces, and the pipeline types arrive in S2 (§10).

All types live in `Lod.Core` (`netstandard2.0`, base class library only, no Rhino or Grasshopper reference) and are tested by `Lod.Core.Tests` on `net8.0` without Rhino.

## 1. Overview

```text
 Programs ─────────────────────────────────────────────────────────────────────────────
 ProgramPresetSet ─1..*─► ProgramPreset ─1─► ZoneProgram ─0..*─► LoadDefinition ─1─► Schedule (Fraction)
 (one per SpaceType)      Name, SpaceType,   │                   Type, Basis, Value
                          WindowToWallRatio  └─0..1─► Thermostat ─┬─1─► Schedule (Temperature)  heating setpoint
                                                                  └─1─► Schedule (Temperature)  cooling setpoint
                                              none = unconditioned zone, no setpoints

 Traceability ─────────────────────────────────────────────────────────────────────────
 LoadDefinition.Aggregation ─┐
 Schedule.Aggregation ───────┴─0..1─► AggregationRecord: Method, Sources (ZoneId[]), Weights (double[])

 Aggregation ──────────────────────────────────────────────────────────────────────────
 target ZoneId + target ZoneMeasures ──┐
 SourceZoneContribution[] ─────────────┼─► IEquivalentPropertyAggregator.Aggregate ─► Result<ZoneProgram>
   Zone (ZoneId), Program (ZoneProgram)│     implemented by EquivalentPropertyAggregator(ToleranceSettings),
   Measures (ZoneMeasures),            │     which uses DesignMagnitudes (value ↔ magnitude)
   AreaFraction, ExteriorWallFraction ─┘

 Common ───────────────────────────────────────────────────────────────────────────────
 Result<T>: Value + Diagnostics (Info, Warning)  |  Diagnostics with at least one Error
 Diagnostic: Severity, Code (DiagnosticCodes), Message, Subject
 ToleranceSettings: Distance, RelativeArea, RelativeLoad, AbsoluteSchedule, Angle
```

Inputs flow left to right: schedules build loads and thermostats, loads and an optional thermostat build a zone program (conditioned when it has a thermostat), and a zone program and a window-to-wall ratio build a program preset. The aggregator takes the programs of several source zones and returns the program of one target zone, built from the same types, with every derived load and schedule carrying an `AggregationRecord`.

## 2. Common (`Lod.Core.Common`)

**`ToleranceSettings`** is the only place where numerical tolerances are defined (GLOBAL.md quality rule 4, ADR-004). Its constructor rejects values that are not positive and finite with an `ArgumentOutOfRangeException`. `ToleranceSettings.Default`:

| Property | Default | Used for |
| --- | --- | --- |
| `Distance` | 1e-6 m | Geometric distances. `DecimalPrecision` (6) is the matching number of decimal places, the polygon-clipping precision from S2. |
| `RelativeArea` | 1e-6 | Area and volume comparisons (`AreaEquals`); also the slack allowed on transfer fractions by the aggregator. |
| `RelativeLoad` | 1e-9 | Load, occupancy, and air-flow comparisons (`LoadEquals`). |
| `AbsoluteSchedule` | 1e-9 | Schedule value comparisons (`ScheduleEquals`). |
| `Angle` | 1e-6 rad | Angular comparisons. |

Relative comparisons use a floor of 1, `|a − b| ≤ rel · max(1, |a|, |b|)`, so values near zero are compared absolutely.

**`Diagnostic`** is a structured message (GLOBAL.md quality rule 5): `Severity` (`Info`, `Warning`, `Error`), a stable `Code` from `DiagnosticCodes`, an actionable `Message`, and an optional `Subject` (for example a zone ID). Codes are never reused or renamed; later stages only append codes. §8 lists the S1 codes.

**`Result<T>`** is the outcome of an operation whose failure is expected. A success carries a value and may carry `Info` and `Warning` diagnostics, never errors; a failure carries at least one `Error` and no value. Reading `Value` on a failure throws an `InvalidOperationException` listing the diagnostics. The static `Result` class creates results: `Success`, `Failure`, and `FromDiagnostics`, which builds the value only when the collected diagnostics contain no error. Every S1 factory that validates input (`Schedule.Create`, `Schedule.Constant`, `Schedule.FromDailyProfiles`, `LoadDefinition.Create`, `Thermostat.Create`, `ZoneProgram.Create`, `ProgramPreset.Create`, `ProgramPresetSet.Create`) returns a `Result<T>`, and so does the aggregator.

**`ZoneId`** is a strongly typed zone identifier (`readonly record struct` over a string). It is the only identifier in S1; S2 adds identifiers for surfaces.

## 3. Schedules (`Lod.Core.Schedules`)

**`Schedule`** is an immutable series of `Schedule.HoursPerYear` = 8760 hourly values for a non-leap year (ADR-003), with a `Name`, a `ScheduleKind`, and an optional `AggregationRecord`.

- `ScheduleKind.Fraction`: dimensionless values in [0, 1] that multiply a load's design magnitude.
- `ScheduleKind.Temperature`: finite values in °C, used for setpoints.

`Schedule.Create` validates the name (`EmptyName`), the length (`ScheduleLength`), and the values (`ScheduleValue`, reporting the first invalid hour). `Schedule.Constant` repeats one value. `Schedule.FromDailyProfiles` repeats a 24-hour weekday profile Monday to Friday and a weekend profile on Saturday and Sunday, starting from a given weekday for 1 January; holidays are not modelled. Values are read with the indexer `schedule[hour]` (0-based) or as `Values`.

## 4. Loads (`Lod.Core.Loads`)

**`LoadDefinition`** is one load of a program: a `LoadType`, a `LoadBasis`, a design `Value` in that basis, a fraction `Schedule`, and an optional `AggregationRecord`. Its design magnitude is `Value` × basis quantity (ADR-007).

| `LoadType` | Design magnitude |
| --- | --- |
| `Occupancy` | people |
| `Lighting`, `ElectricEquipment`, `GasEquipment` | W |
| `DomesticHotWater` (peak flow), `Ventilation`, `Infiltration` | m³/h |

| `LoadBasis` | Basis quantity of a zone |
| --- | --- |
| `PerFloorArea` | floor area, m² |
| `PerPerson` | design occupants, the summed magnitude of the zone's occupancy loads |
| `Absolute` | 1 |
| `PerExteriorWallArea` | gross area of walls with an outdoor boundary, windows included, m². Walls only: roofs are unknown until floors are stacked. |
| `AirChangesPerHour` | air volume, m³ (value in 1/h, magnitude in m³/h) |

`LoadDefinition.Create` rejects negative or non-finite values (`LoadValue`), occupancy expressed other than `PerFloorArea` or `Absolute` (`LoadBasisNotAllowed`), and non-fraction schedules (`ScheduleKindMismatch`).

## 5. Programs (`Lod.Core.Programs`)

**`SpaceType`** is the semantic category of a space: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, and `Mixed` for a simplified zone that combines several space types. Semantics are explicit data, never encoded in layer names, colours, or wire structure (AGENTS.md).

**`Thermostat`** holds the `HeatingSetpoint` and `CoolingSetpoint` schedules of a conditioned zone. `Thermostat.Create` rejects setpoints that are not temperature schedules (`ScheduleKindMismatch`).

**`ZoneProgram`** is the energy-relevant program of a zone: `Loads`, ordered by `LoadType`, then `LoadBasis`, with at most one load per type and basis, and an optional `Thermostat`. A load type may appear in several bases, for example ventilation per person plus per floor area; these components add up (D-047). Conditioning comes from the program (D-038): a program with a thermostat is conditioned (`IsConditioned`); one without a thermostat is unconditioned and has no setpoints. `Find(LoadType, LoadBasis)` returns a load or `null`. `ZoneProgram.Create(loads, thermostat)` rejects the same load type in the same basis twice (`DuplicateLoadType`) and per-person loads without an occupancy load (`PerPersonWithoutOccupancy`). The same type describes an input program and an aggregated one; only the `AggregationRecord`s on its loads and schedules tell them apart.

**`ProgramPreset`** is the program of one space type (D-024): `Name`, `SpaceType`, `Program`, and `WindowToWallRatio` in [0, 1) (D-026; `EmptyName`, `WindowToWallRatio`). **`ProgramPresetSet`** holds at most one preset per space type (`DuplicateSpaceType`), ordered by space type, with `Find(SpaceType)`.

**`ExampleResidentialPresets`** provides illustrative presets for dwelling unit, corridor, and stair; the dwelling unit and corridor are conditioned and the stair is not. Their values and conditioning are round-number choices for development and tests, not DOE prototype values; see [program presets](../research/program-presets.md).

## 6. Aggregation (`Lod.Core.Aggregation`)

### 6.1 Inputs

**`ZoneMeasures`** holds the quantities that load bases refer to: `FloorArea` (m²), `Volume` (m³), and `ExteriorWallArea` (m², gross, windows included). `IsValid` is true when all three are finite and non-negative.

**`SourceZoneContribution`** describes what one source zone gives to one target zone: the source's `Zone` ID, `Program`, and whole-zone `Measures`, plus two fractions in [0, 1]:

- `AreaFraction`: the share of the source's floor area assigned to the target. It also transfers the same share of volume, occupants, absolute loads, and every load that is not per exterior wall area.
- `ExteriorWallFraction`: the share of the source's exterior wall area assigned to the target's exterior walls. It transfers `PerExteriorWallArea` loads.

The aggregator does not compute these fractions. The caller supplies them, so the aggregator is independent of geometry and of any rezoning method (spec §9); from S3 the transfer matrix and the façade attribution compute them.

**`DesignMagnitudes`** converts between a load's value and its absolute design magnitude: `BasisQuantity(basis, measures, occupants)`, `Occupants(program, measures)` (the summed magnitude of the occupancy loads, 0 without one), and `Of(load, measures, occupants)`.

### 6.2 Rules

`IEquivalentPropertyAggregator.Aggregate(target, targetMeasures, sources)` returns the target's `ZoneProgram`. `EquivalentPropertyAggregator` implements ADR-007 for loads and ADR-005 for setpoints. Loads are aggregated per component, a load type in one basis (D-047). For each component defined by at least one source, with *i* running over the sources that define it:

```text
Qᵢ     = valueᵢ · Bᵢ                 design magnitude of source i (people, W, or m³/h); Bᵢ is its basis quantity
Tᵢ     = fᵢ · Qᵢ                     transferred magnitude; fᵢ = ExteriorWallFraction for PerExteriorWallArea,
                                     AreaFraction otherwise
Q*     = Σ Tᵢ                        target design magnitude (conserved)
value* = Q* / B*                     B* is the target's quantity of the component's basis, from targetMeasures
s*(t)  = Σ Tᵢ · sᵢ(t) / Q*           target schedule, so that Q* · s*(t) = Σ Tᵢ · sᵢ(t) at every hour t
```

One rule covers every basis: it is area weighting for per-floor-area loads, volume weighting for air changes per hour (D-019), occupancy weighting for per-person loads, summation for absolute loads, and exterior-wall-area weighting for per-exterior-wall loads. Occupancy is aggregated first (it is the first `LoadType`, and occupancy is never per person), and the target's design occupants (the sum of its conserved occupancy components) are the basis quantity of per-person loads. The target program contains the union of the sources' components, ordered by `LoadType`, then `LoadBasis`. Sources that express one load type in different bases are not an error: each basis is aggregated as its own component, neither rejected nor converted to another basis, and a source without a component contributes nothing to it.

Conditioning and setpoints follow ADR-005 and D-038. The target is conditioned when at least one conditioned source contributes floor area to it (`AreaFraction > 0`): "any conditioned wins". Otherwise the target is unconditioned and gets no thermostat. Heating and cooling setpoints are aggregated separately over the conditioned contributing sources only, weighted by transferred floor area (θ is a setpoint temperature):

```text
C      = { i : source i has a Thermostat and AreaFractionᵢ > 0 }
wᵢ     = AreaFractionᵢ · FloorAreaᵢ        for i in C
θ*(t)  = Σᵢ∈C wᵢ · θᵢ(t) / Σᵢ∈C wᵢ
```

Unconditioned sources still contribute their loads; they never weigh the setpoints. Setpoint aggregation is a prescribed control rule, not a conservation invariant. Merging conditioned and unconditioned sources can enlarge the conditioned floor area; validation reports that change from S3 on and does not enforce it (D-038).

Special cases:

| Situation | Result |
| --- | --- |
| No sources | Error `NoSources` |
| Target or source measures negative or not finite | Error `InvalidMeasures` |
| A fraction outside [0, 1] by more than `RelativeArea` | Error `FractionOutOfRange` |
| Sources define one load type with different bases | One target component per basis, each aggregated on its own (D-047) |
| `Q* = 0` | Value 0, a constant-zero fraction schedule, and `Info` `ZeroLoadSchedule` |
| `Q* > 0` and `B* = 0` (for example a per-exterior-wall load in a target without exterior walls) | Error `ZeroBasisQuantity` |
| No conditioned source contributes floor area | Unconditioned target: no thermostat, no setpoints |
| Conditioned sources contribute, but `Σ wᵢ = 0` (zero floor area) | Error `ZeroSetpointWeight` |

Apart from one clamp, the aggregator never adjusts a quantity to make it fit: aggregated fraction schedule values are clamped to [0, 1] only to remove floating-point noise, because a weighted mean of fractions already lies in [0, 1].

### 6.3 What the tests prove

| Property | Tests (`EquivalentPropertyAggregatorTests`) |
| --- | --- |
| Installed magnitude conserved per load type and basis, including occupancy and air volume flow | `ConservesMagnitudesAtEveryHourForRandomSources` (seeds 1 to 5) |
| Scheduled magnitude conserved hour by hour | `ConservesMagnitudesAtEveryHourForRandomSources`, `SchedulesAreMagnitudeWeighted` |
| Basis-specific weightings | `AreaDensityIsAreaWeighted`, `AirChangesAreVolumeWeighted`, `PerPersonLoadsAreOccupancyWeighted`, `ExteriorWallLoadsUseTheExteriorWallFraction` |
| Mixed bases: one component per basis; occupancy components add up (D-047) | `EachBasisIsAggregatedAsItsOwnComponent`, `OccupancyComponentsAddUp` |
| Setpoints floor-area weighted by transferred area | `SetpointsAreFloorAreaWeighted`, `SetpointWeightsUseTheTransferredFloorArea` |
| Conditioning: any conditioned wins; only conditioned sources weigh setpoints | `UnconditionedSourcesDoNotWeighSetpoints`, `OnlyUnconditionedSourcesGiveAnUnconditionedTarget`, `ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget` |
| A single whole source reproduces its loads, schedules, and setpoints | `SingleWholeSourceReproducesItsProgram` |
| Source order does not change the result | `SourceOrderDoesNotChangeTheResult` |
| Edge cases and errors | `ZeroLoadGivesZeroValueAndZeroSchedule`, `PositiveLoadWithoutBasisQuantityIsAnError`, `ZeroSetpointWeightIsAnError`, `NoSourcesIsAnError`, `FractionsOutsideZeroToOneAreAnError`, `InvalidMeasuresAreAnError` |

## 7. Units

| Quantity | Unit | Where |
| --- | --- | --- |
| Floor area, exterior wall area | m² | `ZoneMeasures` |
| Volume | m³ | `ZoneMeasures` |
| Occupancy magnitude | people | `LoadType.Occupancy` |
| Lighting, electric equipment, gas equipment magnitude | W | `LoadType` |
| Domestic hot water, ventilation, infiltration magnitude | m³/h | `LoadType` |
| Load value | magnitude unit per basis unit: per m² floor area, per person, per zone, per m² exterior wall, or 1/h for air changes | `LoadDefinition.Value` |
| Fraction schedule value | dimensionless, [0, 1] | `ScheduleKind.Fraction` |
| Temperature schedule value | °C | `ScheduleKind.Temperature` |
| Window-to-wall ratio | dimensionless, [0, 1) | `ProgramPreset.WindowToWallRatio` |
| Time step | 1 h, 8760 per (non-leap) year | `Schedule.HoursPerYear` |
| Distance tolerance | m | `ToleranceSettings.Distance` |
| Angle tolerance | rad | `ToleranceSettings.Angle` |
| Aggregation weights | transferred magnitude (people, W, m³/h) or transferred floor area (m²) | `AggregationRecord.Weights` |

## 8. Validation and diagnostic codes

Invalid input is an expected failure: factories return a failed `Result<T>` with error diagnostics instead of throwing. Exceptions signal programming errors only: invalid tolerances, an `AggregationRecord` with a different number of sources and weights, a successful `Result` built with errors or a failed one without, reading `Value` of a failed result, and an unknown `LoadBasis`.

| Code | Severity | Raised by |
| --- | --- | --- |
| `EmptyName` | Error | `Schedule.Create`, `ProgramPreset.Create` |
| `ScheduleLength` | Error | `Schedule.Create`, `Schedule.FromDailyProfiles` |
| `ScheduleValue` | Error | `Schedule.Create` |
| `ScheduleKindMismatch` | Error | `LoadDefinition.Create`, `Thermostat.Create` |
| `LoadValue` | Error | `LoadDefinition.Create` |
| `LoadBasisNotAllowed` | Error | `LoadDefinition.Create` |
| `DuplicateLoadType` | Error | `ZoneProgram.Create` |
| `PerPersonWithoutOccupancy` | Error | `ZoneProgram.Create` |
| `WindowToWallRatio` | Error | `ProgramPreset.Create` |
| `DuplicateSpaceType` | Error | `ProgramPresetSet.Create` |
| `NoSources` | Error | `EquivalentPropertyAggregator` |
| `FractionOutOfRange` | Error | `EquivalentPropertyAggregator` |
| `ZeroBasisQuantity` | Error | `EquivalentPropertyAggregator` |
| `ZeroLoadSchedule` | Info | `EquivalentPropertyAggregator` |
| `ZeroSetpointWeight` | Error | `EquivalentPropertyAggregator` |
| `InvalidMeasures` | Error | `EquivalentPropertyAggregator` |

## 9. Immutability and traceability

**Immutability.** Every S1 type is immutable after construction. Classes are `sealed` and expose get-only properties (`Thermostat`, `ZoneProgram`, and the others); those that validate user input hide their constructors behind factories that return `Result<T>`. Small value types are positional records (`Diagnostic`, `ZoneMeasures`, `SourceZoneContribution`) or a record struct (`ZoneId`). Collections are copied into a private array when an object is created and exposed as `IReadOnlyList<T>` through `Array.AsReadOnly`, which wraps the array in a `ReadOnlyCollection<T>`: callers cannot cast the list back to an array and change it (`ScheduleTests.ValuesCannotBeMutatedThroughTheList`).

`Lod.Core` deliberately does not use `System.Collections.Immutable`. Rhino 8 ships its own `System.Collections.Immutable.dll` (with `System.Memory` and `System.Text.Json`); a core library that references a different version risks assembly version conflicts inside Rhino. Read-only wrappers over private arrays give the same guarantee with the base class library only, which also keeps `Lod.Core` within its dependency boundary (AGENTS.md: BCL only). Records and `init` accessors on `netstandard2.0` need the `IsExternalInit` polyfill in `src/Shared/IsExternalInit.cs`, which `Directory.Build.props` links into every non-.NET Core build (ADR-001).

**Traceability.** Every derived load and schedule records how it was computed (GLOBAL.md scientific rule 2). An `AggregationRecord` holds the `AggregationMethod`, the source `ZoneId`s, and one weight per source, aligned by index; its constructor rejects different numbers of sources and weights (`AggregationRecordTests`):

| Derived value | Method | Sources | Weights |
| --- | --- | --- | --- |
| Aggregated load (`LoadDefinition.Aggregation`) | `MagnitudeConserved` | sources that define the load type in that basis | transferred magnitudes `Tᵢ` (people, W, or m³/h); their sum is the target magnitude `Q*` |
| Its schedule (`Schedule.Aggregation`) | `MagnitudeWeighted` | same as the load | same as the load |
| Heating and cooling setpoint schedules (`Thermostat`) | `FloorAreaWeighted` | conditioned sources with `AreaFraction > 0` | transferred floor areas `wᵢ` (m²) |

Input loads and schedules have `Aggregation == null`. Aggregated schedules are named `"<target> <LoadType> <LoadBasis>"`, `"<target> Heating Setpoint"`, and `"<target> Cooling Setpoint"`. Together with the source programs and the target's measures, a record is enough to recompute the derived value. Zone-level traceability (which source zones a target zone was built from) arrives with `Zone` in S2.

## 10. What arrives in S2

S2 consumes the S1 types; it does not replace them.

- **Geometry** (`Lod.Core.Geometry`): points and polygons with holes in a building-local frame, polygon operations over Clipper2 at the `ToleranceSettings.DecimalPrecision` precision, wall orientation bins, and explicit windows with the first generator's centred-window rule (ADR-002, D-026, D-039).
- **Zones and surfaces** (`Lod.Core.Model`): `Zone` (one or more prisms, a `SpaceType`, a `ZoneProgram`, the source `ZoneId`s it was derived from, and a multiplier), wall surfaces carrying explicit windows and horizontal surfaces, both with boundary conditions, and surface identifiers. Zone measures computed from this geometry become the `ZoneMeasures` of the aggregator.
- **Pipeline types**: `IGeneratedPlan`, `IFloor`, `IGeneratedBuilding`, `IPlanSimplifier`, `IFloorAggregator`, the `PlanGenerator` base with `LinearPlanGenerator` (in `Lod.Generators`), `NoSimplification`, `Stack`, and provenance records of each operation, its parameters, and the code version.
- **Grasshopper components** for schedules, loads, program presets (with a *Conditioned* input), and the example presets.

From S3, plan simplifiers compute each `SourceZoneContribution` from zone overlaps and façade coverage and call `IEquivalentPropertyAggregator` once per target zone.

## 11. Names that differ from the repository specification

The roadmap (v3) uses the names of the code. The [repository specification](../LOD_grasshopper_plugin_repository_spec.md) predates them:

| Specification | Code | Note |
| --- | --- | --- |
| Load type `DHW` (§8) | `LoadType.DomesticHotWater` | Spelled out. |
| Control schedules `HeatingSetpoint`, `CoolingSetpoint` (§8) | `Thermostat.HeatingSetpoint`, `Thermostat.CoolingSetpoint` | Present only on conditioned programs (D-038). |
| `AggregatedZoneProperties`, `AggregationContext` (§9) | `Result<ZoneProgram>`; target `ZoneId` and `ZoneMeasures` | The aggregator returns an ordinary zone program. |
| Semantic categories (§7) | `SpaceType` | Adds `Mixed` for simplified zones that combine several space types. |
````

- [x] **Step 2: Check the document against the code**

Check every type, member, and diagnostic code named in the document against `src/Lod.Core`, and check that the relative links resolve:

```bash
git ls-files docs/research/program-presets.md docs/plans/2026-09-30-implementation-roadmap.md
```

Expected: both paths are printed.

- [x] **Step 3: Commit**

```bash
git add docs/architecture/domain-model.md
git commit -m "docs(architecture): describe the s1 domain model"
```

- [x] **Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/aggregation-engine
git push origin main
git branch -d feature/aggregation-engine
```

Expected from `verify.ps1`: `0 Warning(s)`, `0 Error(s)`, `Passed: 65` on `net8.0`, `VERIFY PASSED`.

---

## Stage close-out

**Files:**
- Modify: `Directory.Build.props`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/plans/2026-09-30-implementation-roadmap.md`

The close-out runs on its own short branch, `chore/repo-s1-close-out` (not a roadmap slice), so that `main` only receives verified, rebase-merged commits (D-004).

- [x] **Step 1: Start the branch**

```bash
git switch main
git pull --ff-only
git switch -c chore/repo-s1-close-out main
```

- [x] **Step 2: Run the verification gate**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected (tail):

```text
Passed!  - Failed:     0, Passed:    65, Skipped:     0, Total:    65, Duration: … - Lod.Core.Tests.dll (net8.0)
VERIFY PASSED
```

- [x] **Step 3: Full file after this task: `Directory.Build.props`**

Bump the version: change `<Version>0.0.1</Version>` to `<Version>0.1.0</Version>`. Nothing else changes; the file then reads:

```xml
<Project>
  <PropertyGroup>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <Deterministic>true</Deterministic>
    <Version>0.1.0</Version>
    <Authors>Environmental Systems Lab</Authors>
    <Product>BEMGen</Product>
  </PropertyGroup>

  <!-- Records and init accessors on netstandard2.0 (ADR-001). -->
  <ItemGroup Condition="'$(TargetFrameworkIdentifier)' != '.NETCoreApp'">
    <Compile Include="$(MSBuildThisFileDirectory)src\Shared\IsExternalInit.cs" Link="Polyfills\IsExternalInit.cs" />
  </ItemGroup>
</Project>
```

- [x] **Step 4: Run the tests again**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed: 65, … Total: 65` on `net8.0`. `BuildInfoTests.InformationalVersionStartsWithTheAssemblyVersion` compares the informational version with the assembly version, so it keeps passing after the bump.

- [x] **Step 5: Commit the version bump**

```bash
git add Directory.Build.props
git commit -m "build(repo): bump version to 0.1.0"
```

- [x] **Step 6: Update AGENTS.md "Project state"**

In `AGENTS.md`, replace the whole body of the `## Project state` section (every line between the `## Project state` heading and the `## Commands` heading, as left by S0) with:

```text
Stage S1 (program presets and equivalence engine) is complete and tagged `v0.1.0`. `Lod.Core` holds tolerances, diagnostics and results, schedules, loads, zone programs (conditioned with a thermostat, or unconditioned), program presets, and the equivalent-property aggregator, with conservation and conditioning tests that run on `net8.0`; `Lod.Grasshopper` holds the plugin shell with the *BEMGen Info* component. The example presets hold illustrative values, not DOE prototype values, and their stair is unconditioned as an illustrative choice ([docs/research/program-presets.md](docs/research/program-presets.md)). The domain model is described in [docs/architecture/domain-model.md](docs/architecture/domain-model.md). There is no geometry or pipeline yet; that is stage S2 of the [roadmap](docs/plans/2026-09-30-implementation-roadmap.md).

S0–S4 are executed as described in [docs/plans/2026-10-01-execution-handoff.md](docs/plans/2026-10-01-execution-handoff.md) (D-048, D-049). A verified reference implementation may be unpacked in `.handoff/` (git-ignored); use it only to check results, and never stage anything under it.
```

Keep one blank line after the heading and one before `## Commands`. The `## Commands` section does not change in S1.

- [x] **Step 7: Update README.md "Status"**

In `README.md`, replace the whole body of the `## Status` section (every line between the `## Status` heading and the `## What it does` heading) with:

```text
Stage S1 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) is complete (`v0.1.0`): program presets and the equivalence engine that aggregates loads, schedules, conditioning, and setpoints, with tests proving conservation of installed and hourly scheduled loads, occupancy, and air volume flow. The example presets hold illustrative values, not DOE prototype values; sourcing prototype values is an open research input ([program presets](docs/research/program-presets.md)). Geometry and the end-to-end Grasshopper pipeline follow in stage S2. Target: Rhino 8; downstream energy modelling is provisionally ClimateStudio in Grasshopper.
```

Keep one blank line after the heading and one before `## What it does`.

- [x] **Step 8: Add the S1 progress line to the roadmap**

In `docs/plans/2026-09-30-implementation-roadmap.md`, find S0's progress line in the header blockquote, the line that starts with

```text
> **Progress:** 2026-10-01 · S0 Foundation complete (tag `v0.0.1`); next: S1.
```

Directly below it, insert the following two lines (a blank blockquote line, then the S1 progress line in the convention S0 set: `> **Progress:** <date> · <stage> complete (tag …); next: …`). The blank blockquote line that S0 placed after its own progress line then follows the S1 line, so each progress line stays a separate paragraph:

```text
>
> **Progress:** 2026-10-01 · S1 Program presets and equivalence engine complete (tag `v0.1.0`); next: S2. The example presets are illustrative (stair unconditioned), not DOE values; sourced presets remain open point 4 of §7.
```

Do not change any other roadmap text.

- [x] **Step 9: Decision log**

No new entry. S1 implements decisions that already exist (D-009, D-019, D-024, D-026, D-038, D-047, ADR-003 to ADR-005, ADR-007), and roadmap v3 already records the illustrative presets and the open sourcing question (§4 S1, §7). See Notes for the reviewer if the owner wants a decision entry anyway.

- [x] **Step 10: Commit the documentation updates**

```bash
git add AGENTS.md README.md docs/plans/2026-09-30-implementation-roadmap.md
git commit -m "docs(repo): record s1 completion in agents, readme, and roadmap"
```

- [ ] **Step 11: Merge the branch (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only chore/repo-s1-close-out
git push origin main
git branch -d chore/repo-s1-close-out
```

Expected from `verify.ps1`: `0 Warning(s)`, `0 Error(s)`, `Passed: 65` on `net8.0`, `VERIFY PASSED`.

- [ ] **Step 12: Tag the stage**

```bash
git tag -a v0.1.0 -m "S1 Program presets and equivalence engine complete"
git push origin v0.1.0
```

- [ ] **Step 13 (optional manual check): plugin version in Rhino 8**

S1 changes no Grasshopper code. To confirm the bump reaches the plugin, build `src/Lod.Grasshopper`, load it in Rhino 8 with its default .NET Core runtime (the only runtime BEMGen supports, D-053) as described in S0's `docs/development/grasshopper-smoke-test.md`, and check that *BEMGen Info* outputs a version starting with `0.1.0+`.

## Exit criteria (copied from the roadmap, refined)

1. **All conservation tests pass:** `dotnet test tests/Lod.Core.Tests -c Release` reports `Passed: 65, Failed: 0` on `net8.0`, including `ConservesMagnitudesAtEveryHourForRandomSources` for seeds 1 to 5 (installed and hourly scheduled magnitude per load type and basis, occupancy, air volume flow, with mixed bases among the sources), `EachBasisIsAggregatedAsItsOwnComponent` and `OccupancyComponentsAddUp` (D-047), `SourceOrderDoesNotChangeTheResult`, `SingleWholeSourceReproducesItsProgram` (loads, schedules, and setpoints), the setpoint and conditioning definition tests (`UnconditionedSourcesDoNotWeighSetpoints`, `OnlyUnconditionedSourcesGiveAnUnconditionedTarget`, `ConditionedSourceWithoutFloorAreaDoesNotConditionTheTarget`), and every zero-denominator and invalid-input case (`ZeroLoadGivesZeroValueAndZeroSchedule`, `PositiveLoadWithoutBasisQuantityIsAnError`, `ZeroSetpointWeightIsAnError`, `InvalidMeasuresAreAnError`); `scripts/verify.ps1` prints `VERIFY PASSED`.
2. **Public types have XML docs:** enforced by the build. `Lod.Core` has `GenerateDocumentationFile` with warnings as errors, so a missing doc comment (CS1591) or an unresolved `cref` fails `verify.ps1`; the build reports `0 Warning(s)`.
3. **`docs/architecture/domain-model.md` written** (Task 9), and `docs/research/program-presets.md` written (Task 7), stating each preset's conditioning (D-038), that the example values and conditioning choices are illustrative and not DOE or standard values, that DOE sourcing is an open research input, and which prototype assumptions are not reproduced.
4. Every type is validated by tests (schedule length and kind, aggregation-record alignment, negative values, occupancy basis, thermostat schedule kinds, programs without a thermostat, the same load type and basis twice, one component per basis, duplicate space types, per-person loads without occupancy, WWR in [0, 1), the example presets' conditioning, invalid zone measures).
5. `Lod.Core` still has no package or Rhino/Grasshopper reference; `Lod.Grasshopper` is unchanged and builds.
6. Version 0.1.0 in `Directory.Build.props`; AGENTS.md, README.md, and the roadmap updated; annotated tag `v0.1.0` pushed.

## Notes for the reviewer

1. **Illustrative presets instead of DOE values.** The v2 roadmap asked for `DefaultResidentialPresets` "with DOE mid-rise apartment values as the starting point". The verified code ships `ExampleResidentialPresets` with illustrative round numbers and an illustrative conditioning choice (stair unconditioned). Roadmap v3 already records this (§4 S1, slice 4; §7, open point 4), and `docs/research/program-presets.md` §3 documents the deviation, so the close-out adds no decision-log entry. If the owner wants a decision entry anyway, append it as the next free D-number, for example:

   ```text
   ### D-NNN — Example presets instead of DOE values in S1

   - **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
   - S1 ships `ExampleResidentialPresets` with illustrative round numbers and an illustrative conditioning choice (stair unconditioned) for development and tests, instead of DOE mid-rise apartment values. Sourcing DOE values and conditioning with citations is an open research input for the researcher; until then no result may be presented as based on prototype values. Documented in `docs/research/program-presets.md`.
   ```

2. **Differences from the repository specification** (code kept verbatim; roadmap v3 already uses the code's names): `LoadType.DomesticHotWater` (spec `DHW`); setpoints live on `Thermostat`, present only for conditioned programs (spec lists `HeatingSetpoint` and `CoolingSetpoint` as control schedules); the spec's `AggregatedZoneProperties` and `AggregationContext` become `Result<ZoneProgram>` plus target `ZoneId` and `ZoneMeasures`; `SpaceType.Mixed` is added. All are listed in `docs/architecture/domain-model.md` §11.

3. **"Any conditioned wins" uses a strict `AreaFraction > 0`.** `EquivalentPropertyAggregator` treats a conditioned source as contributing floor area as soon as its area fraction is positive, however small, while the fraction range check allows a slack of `RelativeArea` (1e-6). A conditioned source with a sliver of overlap therefore conditions the whole target; if it is the only conditioned source, the target takes its setpoints unchanged. Whether such slivers can reach the aggregator depends on S3's overlap mapping; if they can, a threshold belongs in ADR-005 and `ToleranceSettings`, not in the aggregator. Kept verbatim.

4. **Fraction slack reuses an area tolerance.** `EquivalentPropertyAggregator.IsFraction` accepts fractions in `[-RelativeArea, 1 + RelativeArea]` (±1e-6) and does not clamp them. This suits S3's overlap fractions from snapped polygons, but it applies an area tolerance to a dimensionless fraction; ADR-004 could state this use explicitly.

5. **Hourly sampling in the property test.** In `ConservesMagnitudesAtEveryHourForRandomSources` the hourly check samples every 97th hour, so the one random "spike" hour that `FractionAt` puts into the occupancy and lighting schedules is usually not sampled. Spikes are covered deterministically by `SchedulesAreMagnitudeWeighted`, so this is a remark, not a gap. The random sources are all conditioned (`TestPrograms.Program`); conditioning is covered by the dedicated tests listed in Task 8.

6. **Fragile initialisation order.** `ExampleResidentialPresets` relies on the static profile arrays being declared above the preset properties (static initialisers run in textual order). Moving the arrays below the properties would make the type initialiser fail with a null reference. Kept verbatim; Task 6 mentions it.

7. **Intermediate file versions were built and run.** The first versions of `TestPrograms.cs` (Task 4) and `ProgramTests.cs` (Tasks 4 and 5) are the final files minus `Program(...)`, `Unconditioned(...)`, `using Lod.Core.Programs;` (and, in Task 4's `ProgramTests.cs`, `using System.Linq;`), and the later tests. `TestPrograms`' XML summary already says "and programs" in Task 4, to avoid changing that line in Task 5. Every red error and every pass count in this plan comes from replaying the tasks in order on a copy of the S0 state (Release build, .NET SDK 10.0.x); the end state is identical to the verified S1 code (65 core tests on `net8.0`, and also on `net48` before D-053 dropped that target), and `verify.ps1` passed with the version bumped to 0.1.0. The C# example in `docs/research/program-presets.md` §5 was compiled and run against the S1 code.

8. **Text that depends on S0.** The close-out edits AGENTS.md "Project state", README "Status", and the roadmap header, whose exact wording after S0 depends on the S0 plan. The steps therefore replace whole section bodies, and the roadmap progress line follows S0's convention (`> **Progress:** <date> · … complete (tag …); next: …`), inserted below S0's progress line. ADRs are cited by number (ADR-003 to ADR-005, ADR-007) without links, because the S0 plan fixes their file names; links can be added once S0 has merged.

9. **Close-out branch.** The close-out uses its own branch `chore/repo-s1-close-out` (not a roadmap slice) and two commits (`build` for the version, `docs` for the status text), to keep one logical change per commit.

10. **Revision after plan review (D-047).** Loads are aggregated per load type and basis. `ZoneProgram` holds one load per type and basis, ordered by type then basis, and `Find` takes both; `DuplicateLoadType` now means the same type and basis twice; `DesignMagnitudes.Occupants` sums the occupancy components; `EquivalentPropertyAggregator` aggregates each component separately, accumulates the target's occupants over its occupancy components before any per-person component, and names load schedules `"<target> <LoadType> <LoadBasis>"`. `MixedLoadBasis` is removed, so S1 has 16 diagnostic codes; no code has been merged yet, so no stored result refers to it. Tests: `ProgramRejectsDuplicateLoadTypes` became `ProgramRejectsTheSameLoadTypeAndBasisTwice`, `ProgramAcceptsOneComponentPerBasis` is new (Task 5), `MixedBasesAreAnError` is replaced by `EachBasisIsAggregatedAsItsOwnComponent` and `OccupancyComponentsAddUp`, and the random sources add a second component in another basis (Task 8). The core count rises from 63 to 65; the intermediate counts follow (Task 5: 36, Task 6: 40). ADR-007 and the research brief §9, written in S0, describe the same rule.
