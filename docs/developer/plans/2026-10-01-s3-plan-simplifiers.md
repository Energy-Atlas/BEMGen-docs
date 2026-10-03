# S3 — Plan Simplifiers and Validation Implementation Plan

> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S3](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the detailed linear plan into Z1 (semantic merge), Z2 (perimeter/core), and Z3 (one zone per floor) floors through one shared, traceable pipeline that keeps every source window in place, prove numerically that every simplified floor and building keeps the prescribed conservation invariants, and block `Convert2BEM` on a failed validation unless an override is recorded.

**Architecture:** A strategy (`SemanticMerge`, `PerimeterCore`, `SingleZonePerFloor`) only proposes target footprints; the shared `PlanSimplifier` base rebuilds surfaces with the S2 `LayoutSurfaceBuilder`, maps sources to targets by polygon overlap (`OverlapMapper`, `TransferMatrix`), checks that the target façades cover every source façade and shares exterior-wall area by covered length (`FacadeAttribution`, D-041), moves every source window unchanged onto the target wall that contains it (`WindowRehosting`, D-039), and aggregates programs with the S1 `EquivalentPropertyAggregator` (ADR-005, ADR-007, D-038). `FloorValidator` and `BuildingValidator` (`Lod.Core/Validation`) compare extensive totals with the source plan or the fully stacked reference. `Lod.Grasshopper` adds thin components for the simplifiers, the mapping, and validation, and gates `Convert2BEM` on the validation result.

**Tech Stack:** C# 12 (`LangVersion` 12.0), any .NET SDK ≥ 8 (`global.json` pins 8.0.100 with `rollForward: latestMajor`), `Lod.Core`/`Lod.Generators` on `netstandard2.0`, Clipper2 2.0.0, `Lod.Grasshopper` on `net7.0` with RhinoCommon and Grasshopper 8.19.25132.1001 (`ExcludeAssets="runtime"`), tests on `net8.0` with xUnit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1. No new packages in S3.

## Global Constraints

- Rhino 8 (8.19 or later) only (D-003); stages exchange Grasshopper objects, not JSON (D-017).
- `Lod.Core` and `Lod.Generators` reference neither RhinoCommon nor Grasshopper; their tests run with plain `dotnet test`.
- Nullable on, warnings as errors, `EnforceCodeStyleInBuild`; every public member of `Lod.Core` has XML docs (CS1591 is an error there).
- Deterministic output: stable zone, surface, window, and mapping order; randomness only through the explicit seeds in tests.
- Tolerances come only from `ToleranceSettings` (ADR-004): Distance 1e-6 m, RelativeArea 1e-6, RelativeLoad 1e-9, Angle 1e-6 rad; never widened to make a test pass (AGENTS.md rule 12).
- Expected failures are `Result<T>` diagnostics; geometry is never repaired silently (GLOBAL.md quality rules 5 and 6): too-narrow plans fail with `PlanTooNarrow`, uncovered façades with `FacadeNotCovered`, windows without a host wall with `WindowNotHosted`.
- Windows are explicit (position along the wall, sill, width, height). Simplifiers keep every source window unchanged and re-host it on the target outdoor wall that contains it (W0 at every zoning level, D-039); window transformations W1–W5 are stage S5.
- Façade coverage is enforced: target outdoor walls must cover every source outdoor wall over its full length, checked before any normalisation (D-041).
- Walls between merged source zones are discarded, not turned into internal mass (D-034).
- Conditioning comes from the program preset: a target zone is conditioned if any source contributing floor area is; its setpoints are floor-area weighted over the conditioned sources, a prescribed control rule that validation does not compare; the change in conditioned floor area is reported, not enforced (D-038).
- Ground area, roof area, exposed floor area, and building height are enforced building checks for every floor aggregator, against the fully stacked reference (D-045, D-046).
- Validation failures block conversion unless an override is explicitly recorded (GLOBAL.md scientific rule 6).
- Grasshopper components are thin adaptors; their GUIDs never change once merged.
- No simulation in the pipeline (D-016); no CI (D-005): `scripts/verify.ps1` must print `VERIFY PASSED` before every merge to `main`.
- Commits `type(scope): summary` in lower case, without agent, model, or tool names, attribution footers, or `Co-Authored-By` trailers (D-001, D-002); branches are rebase-merged (D-004).

## Files

| Path | Created / modified | Responsibility |
| --- | --- | --- |
| `src/Lod.Core/Common/DiagnosticCodes.cs` | modified (Task 1) | Seven new codes: `DisconnectedGroup`, `PlanTooNarrow`, `NotSupported`, `FacadeNotCovered`, `WindowNotHosted`, `ValidationFailed`, `ValidationOverridden` |
| `src/Lod.Core/Simplification/TransferMatrix.cs` | created (Task 1) | `OverlapMapper` (source × target overlap rows) and `TransferMatrix` (area fractions normalised per source) |
| `src/Lod.Core/Simplification/FacadeAttribution.cs` | created (Task 2) | Overlap of source and target outdoor walls on one façade line; coverage gaps before normalisation (D-041); exterior-wall fractions by covered length |
| `src/Lod.Core/Simplification/WindowRehosting.cs` | created (Task 3) | Moves every source window unchanged onto the target outdoor wall that contains it (D-039) |
| `src/Lod.Core/Simplification/PlanSimplifier.cs` | created (Task 5) | `TargetZone` record and the shared `PlanSimplifier` pipeline |
| `src/Lod.Core/Simplification/Strategies.cs` | created (Tasks 5–7) | `SemanticMerge` (Z1), `PerimeterCore` (Z2, ADR-008), `SingleZonePerFloor` (Z3) |
| `src/Lod.Core/Validation/Totals.cs` | created (Task 8) | Extensive totals of zones and surfaces, multipliers counted, including conditioned floor area |
| `src/Lod.Core/Validation/Validators.cs` | created (Task 8) | `CheckResult`, `ValidationReport`, `FloorValidator`, `BuildingValidator`, internal `Conservation` |
| `tests/Lod.Core.Tests/TestSupport/TestZones.cs` | created (Task 1) | Rectangle zone and outdoor wall builders (walls with any number of windows, at any elevation) |
| `tests/Lod.Core.Tests/Simplification/MappingTests.cs` | created (Tasks 1–2) | Overlap mapping, transfer matrix, façade coverage and attribution (7 tests) |
| `tests/Lod.Core.Tests/Simplification/WindowRehostingTests.cs` | created (Task 3) | Window re-hosting (3 tests) |
| `tests/Lod.Integration.Tests/SimplifierTests.cs` | created (Tasks 5–9) | Simplifier behaviour, invariants on seeded plans, validation, determinism, snapshots (29 tests) |
| `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt` | created (Task 9) | Canonical Z1 snapshot |
| `tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt` | created (Task 9) | Canonical Z2 snapshot |
| `tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt` | created (Task 9) | Canonical Z3 snapshot |
| `src/Lod.Grasshopper/Components/SimplifierComponents.cs` | created (Task 10) | *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*, *Map Source to Target*, *Validate* |
| `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` | modified (Task 10) | Validation gate: `Override` input, `Provenance` output |
| `docs/decisions/ADR-008-perimeter-core-corners.md` | created (Task 4) | Perimeter/core corner rule |
| `docs/decisions/decision-log.md` | modified (Task 4) | D-043 (ADR-008) |
| `docs/architecture/validation.md` | created (Task 10) | Checks, references, tolerances, enforcement, override recording |
| `docs/architecture/convert2bem.md` | modified (Task 10) | `Override` input, `Provenance` output, blocking behaviour |
| `docs/development/grasshopper-smoke-test.md` | modified (Task 11) | S3 checklist |
| `Directory.Build.props` | modified (close-out) | Version 0.3.0 |
| `AGENTS.md`, `README.md`, `docs/plans/2026-09-30-implementation-roadmap.md` | modified (close-out) | Project state, status, progress line |

## Branches

The slices are the five work slices of roadmap S3 (v3), one branch each:

| Slice | Branch | Tasks |
| --- | --- | --- |
| A | `feature/mapping-overlap` | 1–3 |
| B | `docs/decisions-perimeter-corner-rule` | 4 |
| C | `feature/simplifiers` | 5–7 |
| D | `feature/validation-invariants` | 8–9 |
| E | `feature/grasshopper-simplifier-components` | 10–11 |
| — | `chore/repo-s3-close-out` | close-out |

Test counts at the start of S3 (end of S2): 94 core, 17 generators, 9 integration on `net8.0`. At the end: 104 core, 17 generators, 38 integration.

---

## Slice A — `feature/mapping-overlap`

### Task 1: Diagnostic codes, overlap mapper, and transfer matrix

**Files:**
- Modify: `src/Lod.Core/Common/DiagnosticCodes.cs`
- Create: `src/Lod.Core/Simplification/TransferMatrix.cs`
- Create: `tests/Lod.Core.Tests/TestSupport/TestZones.cs`
- Test: `tests/Lod.Core.Tests/Simplification/MappingTests.cs`

**Interfaces:**
- Consumes: `ZoneMapping(ZoneId Source, ZoneId Target, double OverlapArea, double SourceFraction, double TargetFraction)` (S2, `Model/Pipeline.cs`); `Zone`, `ZonePart`, `Polygon2.Rectangle`, `PolygonOps.IntersectionArea`, `WallSurface(SurfaceId, ZoneId, Point2, Point2, double elevation, double height, BoundaryCondition, ZoneId?, IEnumerable<Window>)`, `Window` (S2); `ToleranceSettings.RelativeArea` (S1); `TestPrograms.Program()` (S1 test support).
- Produces:
  - `public sealed class OverlapMapper { public OverlapMapper(ToleranceSettings tolerances); public IReadOnlyList<ZoneMapping> Map(IReadOnlyList<Zone> sources, IReadOnlyList<(ZoneId Id, Polygon2 Footprint)> targets); }`
  - `public sealed class TransferMatrix { public static TransferMatrix FromMapping(IEnumerable<ZoneMapping> mapping); public double AreaFraction(ZoneId source, ZoneId target); public IReadOnlyList<ZoneId> SourcesOf(ZoneId target); }`
  - `DiagnosticCodes.DisconnectedGroup`, `.PlanTooNarrow`, `.NotSupported`, `.FacadeNotCovered`, `.WindowNotHosted`, `.ValidationFailed`, `.ValidationOverridden`
  - test support: `TestZones.Rectangle(string id, double x0, double y0, double x1, double y1, double height = 3.0)`, `TestZones.Wall(string id, string zone, double x0, double y0, double x1, double y1, params Window[] windows)`, and `TestZones.WallAt(string id, string zone, double x0, double y0, double x1, double y1, double elevation, params Window[] windows)` (outdoor walls, 3 m high)

**Why fractions are normalised per source.** The research brief (§9) transfers every extensive quantity with `Q_j = Σ_i f_ji Q_i`. Summed over all targets, `Σ_j Q_j = Σ_i (Σ_j f_ji) Q_i`, which equals the source total exactly only if every source's fractions sum to exactly 1. The raw `SourceFraction = overlap / source area` sums to 1 only as well as the polygon arithmetic allows: Clipper2 snaps to the 1e-6 m grid (relative area errors around 1e-7 for 10 m zones), and slivers below `RelativeArea × source area` are dropped. Using raw fractions would make load conservation only as good as the geometry, far outside `RelativeLoad` = 1e-9. `TransferMatrix` therefore uses `f_ji = overlap_ji / Σ_j overlap_ji`: loads, occupancy, and air flow are conserved to floating-point precision whatever the rounding, and whether the overlaps really cover each source is a separate geometric question, answered by the `SourceCoverage` validation check (Task 8) at `RelativeArea`. The third test below uses overlaps 30 + 69.9 = 99.9 m² (0.1 % missing) to show the fractions still sum to 1. The same split between an exact normalised transfer and a separate coverage check applies to façades (Task 2, D-041).

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c feature/mapping-overlap main
```

- [x] **Step 2: Append the S3 diagnostic codes**

In `src/Lod.Core/Common/DiagnosticCodes.cs`, insert the following after the last S2 constant (`public const string NoFloors = "NoFloors";`), before the class's closing brace, with one blank line before the first new comment. These are constants with no behaviour of their own; Tasks 2–10 use them.

```csharp
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
```

- [x] **Step 3: Full file after this task: `src/Lod.Core/Common/DiagnosticCodes.cs`**

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
}
```

- [x] **Step 4: Add the zone and wall test builders**

Create `tests/Lod.Core.Tests/TestSupport/TestZones.cs` (`Wall` and `WallAt` are used from Task 2):

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Tests.TestSupport;

/// <summary>Builders for zones and walls used across tests.</summary>
internal static class TestZones
{
    public static Zone Rectangle(string id, double x0, double y0, double x1, double y1, double height = 3.0) =>
        new(new ZoneId(id), id, SpaceType.DwellingUnit, new[] { new ZonePart(Polygon2.Rectangle(x0, y0, x1, y1), 0.0, height) }, TestPrograms.Program(), Enumerable.Empty<ZoneId>());

    public static WallSurface Wall(string id, string zone, double x0, double y0, double x1, double y1, params Window[] windows) =>
        WallAt(id, zone, x0, y0, x1, y1, 0.0, windows);

    public static WallSurface WallAt(string id, string zone, double x0, double y0, double x1, double y1, double elevation, params Window[] windows) =>
        new(new SurfaceId(id), new ZoneId(zone), new Point2(x0, y0), new Point2(x1, y1), elevation, 3.0, BoundaryCondition.Outdoors, null, windows);
}
```

- [x] **Step 5: Write the failing mapping tests**

Create `tests/Lod.Core.Tests/Simplification/MappingTests.cs`:

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Simplification;

public sealed class MappingTests
{
    [Fact]
    public void OverlapsAreRecordedWithBothFractions()
    {
        Zone source = TestZones.Rectangle("A", 0, 0, 10, 10);
        var targets = new[] { (new ZoneId("L"), Polygon2.Rectangle(0, 0, 4, 10)), (new ZoneId("R"), Polygon2.Rectangle(4, 0, 20, 10)) };

        ZoneMapping[] rows = new OverlapMapper(ToleranceSettings.Default).Map(new[] { source }, targets).ToArray();

        Assert.Equal(2, rows.Length);
        Assert.Equal(40.0, rows[0].OverlapArea, 9);
        Assert.Equal(0.4, rows[0].SourceFraction, 9);
        Assert.Equal(1.0, rows[0].TargetFraction, 9);
        Assert.Equal(0.6, rows[1].SourceFraction, 9);
        Assert.Equal(60.0 / 160.0, rows[1].TargetFraction, 9);
    }

    [Fact]
    public void TouchingZonesAreNotMapped()
    {
        Zone source = TestZones.Rectangle("A", 0, 0, 10, 10);

        Assert.Empty(new OverlapMapper(ToleranceSettings.Default).Map(new[] { source }, new[] { (new ZoneId("T"), Polygon2.Rectangle(10, 0, 20, 10)) }));
    }

    [Fact]
    public void TransferFractionsAreNormalisedPerSource()
    {
        TransferMatrix matrix = TransferMatrix.FromMapping(new[]
        {
            new ZoneMapping(new ZoneId("A"), new ZoneId("X"), 30.0, 0.3, 1.0),
            new ZoneMapping(new ZoneId("A"), new ZoneId("Y"), 69.9, 0.699, 1.0),
        });

        Assert.Equal(1.0, matrix.AreaFraction(new ZoneId("A"), new ZoneId("X")) + matrix.AreaFraction(new ZoneId("A"), new ZoneId("Y")), 15);
        Assert.Equal(0.0, matrix.AreaFraction(new ZoneId("A"), new ZoneId("Z")));
        Assert.Equal(new[] { new ZoneId("A") }, matrix.SourcesOf(new ZoneId("X")));
    }
}
```

- [x] **Step 6: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected: the build fails (reported for `net8.0`) with

```text
tests\Lod.Core.Tests\Simplification\MappingTests.cs(19,34): error CS0246: The type or namespace name 'OverlapMapper' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Simplification\MappingTests.cs(34,26): error CS0246: The type or namespace name 'OverlapMapper' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Simplification\MappingTests.cs(40,33): error CS0103: The name 'TransferMatrix' does not exist in the current context
tests\Lod.Core.Tests\Simplification\MappingTests.cs(40,9): error CS0246: The type or namespace name 'TransferMatrix' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 7: Implement the mapper and the matrix**

Create `src/Lod.Core/Simplification/TransferMatrix.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>Computes source-to-target overlaps (spec §11).</summary>
public sealed class OverlapMapper
{
    private readonly ToleranceSettings _tolerances;
    private readonly PolygonOps _ops;

    /// <summary>Creates the mapper.</summary>
    /// <param name="tolerances">Tolerances; overlaps smaller than <see cref="ToleranceSettings.RelativeArea"/> of the source are dropped as slivers.</param>
    public OverlapMapper(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
        _ops = new PolygonOps(tolerances);
    }

    /// <summary>One row per overlapping source-target pair, in source then target order.</summary>
    /// <param name="sources">Source zones (single part).</param>
    /// <param name="targets">Target zone footprints.</param>
    /// <returns>Mapping rows.</returns>
    public IReadOnlyList<ZoneMapping> Map(IReadOnlyList<Zone> sources, IReadOnlyList<(ZoneId Id, Polygon2 Footprint)> targets)
    {
        var rows = new List<ZoneMapping>();
        foreach (Zone source in sources)
        {
            double sourceArea = source.FloorArea;
            foreach ((ZoneId id, Polygon2 footprint) in targets)
            {
                double overlap = _ops.IntersectionArea(source.Parts[0].Footprint, footprint);
                if (overlap > _tolerances.RelativeArea * sourceArea)
                {
                    rows.Add(new ZoneMapping(source.Id, id, overlap, overlap / sourceArea, overlap / footprint.Area));
                }
            }
        }

        return rows;
    }
}

/// <summary>
/// Area transfer fractions normalised per source: <c>f_ji = overlap_ji / Σ_j overlap_ji</c>. Because every source's fractions sum to exactly 1,
/// extensive quantities are conserved exactly; how well the overlaps cover each source is checked separately by validation.
/// </summary>
public sealed class TransferMatrix
{
    private readonly Dictionary<(ZoneId Source, ZoneId Target), double> _fractions;

    private TransferMatrix(Dictionary<(ZoneId, ZoneId), double> fractions)
    {
        _fractions = fractions;
    }

    /// <summary>Builds the matrix from mapping rows.</summary>
    /// <param name="mapping">Mapping rows.</param>
    /// <returns>The matrix.</returns>
    public static TransferMatrix FromMapping(IEnumerable<ZoneMapping> mapping)
    {
        var fractions = new Dictionary<(ZoneId, ZoneId), double>();
        foreach (IGrouping<ZoneId, ZoneMapping> source in mapping.GroupBy(m => m.Source))
        {
            double total = source.Sum(m => m.OverlapArea);
            foreach (ZoneMapping row in source)
            {
                fractions[(row.Source, row.Target)] = row.OverlapArea / total;
            }
        }

        return new TransferMatrix(fractions);
    }

    /// <summary>Normalised area fraction of a source assigned to a target; 0 when they do not overlap.</summary>
    /// <param name="source">Source zone.</param>
    /// <param name="target">Target zone.</param>
    /// <returns>The fraction.</returns>
    public double AreaFraction(ZoneId source, ZoneId target) => _fractions.TryGetValue((source, target), out double f) ? f : 0.0;

    /// <summary>Sources overlapping a target, in mapping order.</summary>
    /// <param name="target">Target zone.</param>
    /// <returns>Source zone IDs.</returns>
    public IReadOnlyList<ZoneId> SourcesOf(ZoneId target) => _fractions.Keys.Where(k => k.Target == target).Select(k => k.Source).ToArray();
}
```

Notes: rows come in source order, then target order, so the mapping is deterministic. Only the first part of a source is used: plan zones are single-storey and have exactly one part. Touching zones (shared edge only) have zero overlap and produce no row.

- [x] **Step 8: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected (durations vary):

```text
Passed!  - Failed:     0, Passed:     3, Skipped:     0, Total:     3, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 9: Run the whole core suite**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    97, Skipped:     0, Total:    97` for `net8.0`.

- [x] **Step 10: Commit**

```bash
git add src/Lod.Core/Common/DiagnosticCodes.cs src/Lod.Core/Simplification/TransferMatrix.cs tests/Lod.Core.Tests/TestSupport/TestZones.cs tests/Lod.Core.Tests/Simplification/MappingTests.cs
git commit -m "feature(mapping): add overlap mapper and per-source normalised transfer matrix"
```

### Task 2: Façade coverage and exterior-wall attribution

**Files:**
- Create: `src/Lod.Core/Simplification/FacadeAttribution.cs`
- Test: `tests/Lod.Core.Tests/Simplification/MappingTests.cs` (add four tests)

**Interfaces:**
- Consumes: `WallSurface` (`Start`, `End`, `Elevation`, `Height`, `Length`, `Area`, `Zone`, `Boundary`), `Surface`, `SurfaceId`, `BoundaryCondition.Outdoors` (S2); `ToleranceSettings.Distance`, `.Angle`, `.AreaEquals`; `TestZones.Wall` (Task 1).
- Produces: `public sealed class FacadeAttribution { public static FacadeAttribution Compute(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces, ToleranceSettings tolerances); public IReadOnlyList<(WallSurface Wall, double CoveredLength)> CoverageGaps(); public double ExteriorWallFraction(ZoneId sourceZone, ZoneId targetZone); public static double OverlapLength(WallSurface a, WallSurface b, ToleranceSettings tolerances); public static (double Start, double End)? Interval(WallSurface a, WallSurface b, ToleranceSettings tolerances); }`

**How it works (D-041).** Only walls with an `Outdoors` boundary take part.

1. `Interval(a, b)` places wall `b` along wall `a` when both lie on one façade line: they run in the same direction (the dot product of their unit directions is at least `cos(Angle)`), have the same elevation and the same height within `Distance`, and both endpoints of `b` lie within `Distance` of `a`'s line. It returns the start and end of `b` measured from `a`'s start, or `null`. Walls facing the other way or on a parallel line never match. `OverlapLength` clips that interval to `a`. `WindowRehosting` (Task 3) uses `Interval` to place windows.
2. `Compute` records the raw overlap length `Lᵢⱼ` of every target wall `j` on every source wall `i` (overlaps shorter than `Distance` are ignored).
3. `CoverageGaps()` compares `Σⱼ Lᵢⱼ` with the source wall length `Lᵢ` within the relative geometric tolerance (`AreaEquals`, ADR-004), **before any normalisation**, and lists every source wall that is not fully covered with its covered length. The simplifier pipeline turns each entry into the error `FacadeNotCovered` (Task 5), and floor validation enforces the same condition as the check `FacadeCoverage` (Task 8).
4. `ExteriorWallFraction(sourceZone, targetZone)` = (Σ over the source zone's covered walls of wall area × length covered by the target zone's walls / covered length) / (Σ of those walls' areas): the fraction `fᵢ` used for `PerExteriorWallArea` loads (ADR-007). It is normalised by covered length, which equals the wall length once `CoverageGaps()` is empty, so the transfer is exact.

Why coverage comes first: normalisation alone would hide a gap. In `PartialCoverageIsReportedBeforeAnyNormalisation` the only target covers 16 m of a 20 m source wall; a normalised share would still hand it the whole wall. Glazing is no longer attributed here: windows move unchanged with `WindowRehosting` (D-039).

- [x] **Step 1: Write the failing façade tests**

Add these four tests to `MappingTests`, after `TransferFractionsAreNormalisedPerSource` and before the class's closing brace (one blank line between methods):

```csharp
    [Fact]
    public void OneTargetWallSpanningTwoSourceWallsCoversBoth()
    {
        WallSurface left = TestZones.Wall("A/W1", "A", 0, 0, 10, 0);
        WallSurface right = TestZones.Wall("B/W1", "B", 10, 0, 20, 0);
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 20, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { left, right }, new Surface[] { merged }, ToleranceSettings.Default);

        Assert.Empty(facade.CoverageGaps());
        Assert.Equal(1.0, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("M")), 12);
    }

    [Fact]
    public void PartialCoverageIsReportedBeforeAnyNormalisation()
    {
        // The target covers only 16 m of a 20 m source wall: without the coverage check, normalisation would hide the missing 4 m (D-041).
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0);
        WallSurface target = TestZones.Wall("P/W1", "P", 0, 0, 16, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { target }, ToleranceSettings.Default);

        (WallSurface wall, double covered) = Assert.Single(facade.CoverageGaps());
        Assert.Equal(source.Id, wall.Id);
        Assert.Equal(16.0, covered, 9);
    }

    [Fact]
    public void SourceWallSplitAcrossTargetsSharesItsAreaByLength()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0);
        WallSurface first = TestZones.Wall("P/W1", "P", 0, 0, 5, 0);
        WallSurface second = TestZones.Wall("Q/W1", "Q", 5, 0, 20, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { first, second }, ToleranceSettings.Default);

        Assert.Empty(facade.CoverageGaps());
        Assert.Equal(0.25, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("P")), 12);
        Assert.Equal(0.75, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("Q")), 12);
    }

    [Fact]
    public void WallsOnParallelLinesOrFacingAwayDoNotCover()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 10, 0);
        WallSurface parallel = TestZones.Wall("B/W1", "B", 0, 1, 10, 1);
        WallSurface reversed = TestZones.Wall("C/W1", "C", 10, 0, 0, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { parallel, reversed }, ToleranceSettings.Default);

        Assert.Equal(0.0, Assert.Single(facade.CoverageGaps()).CoveredLength);
    }
```

- [x] **Step 2: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected: the build fails with

```text
tests\Lod.Core.Tests\Simplification\MappingTests.cs(58,36): error CS0103: The name 'FacadeAttribution' does not exist in the current context
tests\Lod.Core.Tests\Simplification\MappingTests.cs(58,9): error CS0246: The type or namespace name 'FacadeAttribution' could not be found (are you missing a using directive or an assembly reference?)
```

and the same pair for lines 71, 85, and 99.

- [x] **Step 3: Implement the attribution**

Create `src/Lod.Core/Simplification/FacadeAttribution.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>
/// Matches source and target outdoor walls lying on the same façade line, by projected overlap length. Coverage is checked first (D-041):
/// every source wall must be covered over its full length; only then are the overlaps normalised per source wall to transfer exterior-wall-based
/// loads exactly.
/// </summary>
public sealed class FacadeAttribution
{
    private readonly Dictionary<(SurfaceId Source, SurfaceId Target), double> _overlaps = new();
    private readonly Dictionary<SurfaceId, WallSurface> _sources;
    private readonly Dictionary<SurfaceId, WallSurface> _targets;
    private readonly ToleranceSettings _tolerances;

    private FacadeAttribution(Dictionary<SurfaceId, WallSurface> sources, Dictionary<SurfaceId, WallSurface> targets, ToleranceSettings tolerances)
    {
        _sources = sources;
        _targets = targets;
        _tolerances = tolerances;
    }

    /// <summary>Matches outdoor source walls with outdoor target walls.</summary>
    /// <param name="sourceSurfaces">Source surfaces; only outdoor walls are used.</param>
    /// <param name="targetSurfaces">Target surfaces; only outdoor walls are used.</param>
    /// <param name="tolerances">Tolerances; walls are on the same line within <see cref="ToleranceSettings.Distance"/>.</param>
    /// <returns>The attribution.</returns>
    public static FacadeAttribution Compute(IEnumerable<Surface> sourceSurfaces, IEnumerable<Surface> targetSurfaces, ToleranceSettings tolerances)
    {
        Dictionary<SurfaceId, WallSurface> sources = Outdoor(sourceSurfaces).ToDictionary(w => w.Id);
        Dictionary<SurfaceId, WallSurface> targets = Outdoor(targetSurfaces).ToDictionary(w => w.Id);
        var attribution = new FacadeAttribution(sources, targets, tolerances);
        foreach (WallSurface source in sources.Values)
        {
            foreach (WallSurface target in targets.Values)
            {
                double length = OverlapLength(source, target, tolerances);
                if (length > tolerances.Distance)
                {
                    attribution._overlaps[(source.Id, target.Id)] = length;
                }
            }
        }

        return attribution;
    }

    /// <summary>
    /// Source outdoor walls whose length is not fully covered by target outdoor walls: <c>Σⱼ Lᵢⱼ ≠ Lᵢ</c> within the relative geometric
    /// tolerance (ADR-004). Must be empty before the attribution is used (D-041).
    /// </summary>
    /// <returns>The uncovered or partly covered source walls with their covered length.</returns>
    public IReadOnlyList<(WallSurface Wall, double CoveredLength)> CoverageGaps() =>
        _sources.Values
            .Select(w => (Wall: w, CoveredLength: _overlaps.Where(o => o.Key.Source == w.Id).Sum(o => o.Value)))
            .Where(c => !_tolerances.AreaEquals(c.Wall.Length, c.CoveredLength))
            .ToArray();

    /// <summary>
    /// Share of a source zone's exterior wall area that becomes a target zone's exterior wall area. Each source wall's overlaps are normalised to
    /// its covered length, which equals its length once <see cref="CoverageGaps"/> is empty.
    /// </summary>
    /// <param name="sourceZone">Source zone.</param>
    /// <param name="targetZone">Target zone.</param>
    /// <returns>Fraction in [0, 1].</returns>
    public double ExteriorWallFraction(ZoneId sourceZone, ZoneId targetZone)
    {
        double total = 0.0;
        double toTarget = 0.0;
        foreach (WallSurface wall in _sources.Values.Where(w => w.Zone == sourceZone))
        {
            KeyValuePair<(SurfaceId Source, SurfaceId Target), double>[] overlaps = _overlaps.Where(o => o.Key.Source == wall.Id).ToArray();
            double covered = overlaps.Sum(o => o.Value);
            if (covered <= 0.0)
            {
                continue;
            }

            total += wall.Area;
            toTarget += wall.Area * overlaps.Where(o => _targets[o.Key.Target].Zone == targetZone).Sum(o => o.Value) / covered;
        }

        return total > 0.0 ? toTarget / total : 0.0;
    }

    /// <summary>Overlap length of <paramref name="b"/> on <paramref name="a"/> when both lie on one façade line, face the same way, and share an elevation.</summary>
    /// <param name="a">Reference wall.</param>
    /// <param name="b">Other wall.</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>Overlap length along <paramref name="a"/>, m; 0 when they are not on the same façade line.</returns>
    public static double OverlapLength(WallSurface a, WallSurface b, ToleranceSettings tolerances)
    {
        (double start, double end)? interval = Interval(a, b, tolerances);
        return interval is { } i ? Math.Max(0.0, Math.Min(a.Length, i.end) - Math.Max(0.0, i.start)) : 0.0;
    }

    /// <summary>
    /// Where <paramref name="b"/> lies along <paramref name="a"/>: the start and end of <paramref name="b"/> measured from <paramref name="a"/>'s start,
    /// or <c>null</c> when the walls are not on the same façade line, facing the same way, at the same elevation and height.
    /// </summary>
    /// <param name="a">Reference wall.</param>
    /// <param name="b">Other wall.</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>The interval along <paramref name="a"/>, m, or <c>null</c>.</returns>
    public static (double Start, double End)? Interval(WallSurface a, WallSurface b, ToleranceSettings tolerances)
    {
        double length = a.Length;
        double ux = (a.End.X - a.Start.X) / length;
        double uy = (a.End.Y - a.Start.Y) / length;
        double bx = (b.End.X - b.Start.X) / b.Length;
        double by = (b.End.Y - b.Start.Y) / b.Length;
        if ((ux * bx) + (uy * by) < Math.Cos(tolerances.Angle)
            || Math.Abs(a.Elevation - b.Elevation) > tolerances.Distance
            || Math.Abs(a.Height - b.Height) > tolerances.Distance)
        {
            return null;
        }

        double DistanceFromLine(double x, double y) => Math.Abs((ux * (y - a.Start.Y)) - (uy * (x - a.Start.X)));
        if (DistanceFromLine(b.Start.X, b.Start.Y) > tolerances.Distance || DistanceFromLine(b.End.X, b.End.Y) > tolerances.Distance)
        {
            return null;
        }

        double Along(double x, double y) => (ux * (x - a.Start.X)) + (uy * (y - a.Start.Y));
        return (Along(b.Start.X, b.Start.Y), Along(b.End.X, b.End.Y));
    }

    private static IEnumerable<WallSurface> Outdoor(IEnumerable<Surface> surfaces) =>
        surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors);
}
```

- [x] **Step 4: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected: `Passed!  - Failed:     0, Passed:     7, Skipped:     0, Total:     7` for `net8.0`.

- [x] **Step 5: Run the whole core suite**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:   101, Skipped:     0, Total:   101` for `net8.0`.

- [x] **Step 6: Full file after this task: `tests/Lod.Core.Tests/Simplification/MappingTests.cs`**

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Simplification;

public sealed class MappingTests
{
    [Fact]
    public void OverlapsAreRecordedWithBothFractions()
    {
        Zone source = TestZones.Rectangle("A", 0, 0, 10, 10);
        var targets = new[] { (new ZoneId("L"), Polygon2.Rectangle(0, 0, 4, 10)), (new ZoneId("R"), Polygon2.Rectangle(4, 0, 20, 10)) };

        ZoneMapping[] rows = new OverlapMapper(ToleranceSettings.Default).Map(new[] { source }, targets).ToArray();

        Assert.Equal(2, rows.Length);
        Assert.Equal(40.0, rows[0].OverlapArea, 9);
        Assert.Equal(0.4, rows[0].SourceFraction, 9);
        Assert.Equal(1.0, rows[0].TargetFraction, 9);
        Assert.Equal(0.6, rows[1].SourceFraction, 9);
        Assert.Equal(60.0 / 160.0, rows[1].TargetFraction, 9);
    }

    [Fact]
    public void TouchingZonesAreNotMapped()
    {
        Zone source = TestZones.Rectangle("A", 0, 0, 10, 10);

        Assert.Empty(new OverlapMapper(ToleranceSettings.Default).Map(new[] { source }, new[] { (new ZoneId("T"), Polygon2.Rectangle(10, 0, 20, 10)) }));
    }

    [Fact]
    public void TransferFractionsAreNormalisedPerSource()
    {
        TransferMatrix matrix = TransferMatrix.FromMapping(new[]
        {
            new ZoneMapping(new ZoneId("A"), new ZoneId("X"), 30.0, 0.3, 1.0),
            new ZoneMapping(new ZoneId("A"), new ZoneId("Y"), 69.9, 0.699, 1.0),
        });

        Assert.Equal(1.0, matrix.AreaFraction(new ZoneId("A"), new ZoneId("X")) + matrix.AreaFraction(new ZoneId("A"), new ZoneId("Y")), 15);
        Assert.Equal(0.0, matrix.AreaFraction(new ZoneId("A"), new ZoneId("Z")));
        Assert.Equal(new[] { new ZoneId("A") }, matrix.SourcesOf(new ZoneId("X")));
    }

    [Fact]
    public void OneTargetWallSpanningTwoSourceWallsCoversBoth()
    {
        WallSurface left = TestZones.Wall("A/W1", "A", 0, 0, 10, 0);
        WallSurface right = TestZones.Wall("B/W1", "B", 10, 0, 20, 0);
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 20, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { left, right }, new Surface[] { merged }, ToleranceSettings.Default);

        Assert.Empty(facade.CoverageGaps());
        Assert.Equal(1.0, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("M")), 12);
    }

    [Fact]
    public void PartialCoverageIsReportedBeforeAnyNormalisation()
    {
        // The target covers only 16 m of a 20 m source wall: without the coverage check, normalisation would hide the missing 4 m (D-041).
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0);
        WallSurface target = TestZones.Wall("P/W1", "P", 0, 0, 16, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { target }, ToleranceSettings.Default);

        (WallSurface wall, double covered) = Assert.Single(facade.CoverageGaps());
        Assert.Equal(source.Id, wall.Id);
        Assert.Equal(16.0, covered, 9);
    }

    [Fact]
    public void SourceWallSplitAcrossTargetsSharesItsAreaByLength()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0);
        WallSurface first = TestZones.Wall("P/W1", "P", 0, 0, 5, 0);
        WallSurface second = TestZones.Wall("Q/W1", "Q", 5, 0, 20, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { first, second }, ToleranceSettings.Default);

        Assert.Empty(facade.CoverageGaps());
        Assert.Equal(0.25, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("P")), 12);
        Assert.Equal(0.75, facade.ExteriorWallFraction(new ZoneId("A"), new ZoneId("Q")), 12);
    }

    [Fact]
    public void WallsOnParallelLinesOrFacingAwayDoNotCover()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 10, 0);
        WallSurface parallel = TestZones.Wall("B/W1", "B", 0, 1, 10, 1);
        WallSurface reversed = TestZones.Wall("C/W1", "C", 10, 0, 0, 0);

        FacadeAttribution facade = FacadeAttribution.Compute(new Surface[] { source }, new Surface[] { parallel, reversed }, ToleranceSettings.Default);

        Assert.Equal(0.0, Assert.Single(facade.CoverageGaps()).CoveredLength);
    }
}
```

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Simplification/FacadeAttribution.cs tests/Lod.Core.Tests/Simplification/MappingTests.cs
git commit -m "feature(mapping): check facade coverage and share exterior wall area by covered length"
```

### Task 3: Window re-hosting

**Files:**
- Create: `src/Lod.Core/Simplification/WindowRehosting.cs`
- Test: `tests/Lod.Core.Tests/Simplification/WindowRehostingTests.cs`

**Interfaces:**
- Consumes: `Window.At(double offset, double width, double sillHeight, double height)`, `Window.MovedTo(double offset)`, `Window.Offset`, `.Width`, `.SillHeight`, `WallSurface.Windows`, `WallSurface.WithWindows(IEnumerable<Window>)`, `WallSurface.GlazedArea`, `Result.FromDiagnostics` (S2); `FacadeAttribution.Interval` (Task 2); `DiagnosticCodes.WindowNotHosted` (Task 1); `TestZones.Wall`, `TestZones.WallAt` (Task 1).
- Produces: `public static class WindowRehosting { public static Result<IReadOnlyList<Surface>> Rehost(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances); }`

**Rule (D-039).** Zoning simplification keeps the window representation at W0: every window of every source outdoor wall keeps its sill, width, and height and its position on the façade. For each window, the first target outdoor wall (in target surface order) whose line contains the source wall (`FacadeAttribution.Interval(host, source)`) and that contains the whole window, from `interval.Start + offset` to that plus the width, within `Distance`, becomes its host; the new offset is measured from the host's start (clamped to the host only to remove floating-point noise below `Distance`). A window that no single target wall contains is the error `WindowNotHosted` with the source wall as subject; windows are never moved, resized, or split silently. Target walls lose any windows they had and receive exactly the re-hosted ones. Glazing per wall, orientation, and building is therefore conserved by construction; validation still checks the totals (Task 8). Window transformations (W1–W5) are stage S5 (D-039).

- [x] **Step 1: Write the failing re-hosting tests**

Create `tests/Lod.Core.Tests/Simplification/WindowRehostingTests.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Tests.TestSupport;
using Xunit;

namespace Lod.Core.Tests.Simplification;

public sealed class WindowRehostingTests
{
    [Fact]
    public void WindowsKeepTheirPositionOnTheCoveringWall()
    {
        WallSurface left = TestZones.Wall("A/W1", "A", 0, 0, 10, 0, Window.At(1.0, 2.0, 0.5, 1.0));
        WallSurface right = TestZones.Wall("B/W1", "B", 10, 0, 20, 0, Window.At(2.0, 3.0, 1.0, 1.5));
        WallSurface merged = TestZones.Wall("M/W1", "M", 0, 0, 20, 0);

        IReadOnlyList<Surface> result = WindowRehosting.Rehost(new Surface[] { left, right }, new Surface[] { merged }, ToleranceSettings.Default).Value;

        WallSurface host = Assert.IsType<WallSurface>(Assert.Single(result));
        Assert.Equal(new[] { 1.0, 12.0 }, host.Windows.Select(w => w.Offset));
        Assert.Equal(new[] { 2.0, 3.0 }, host.Windows.Select(w => w.Width));
        Assert.Equal(new[] { 0.5, 1.0 }, host.Windows.Select(w => w.SillHeight));
        Assert.Equal(left.GlazedArea + right.GlazedArea, host.GlazedArea, 12);
    }

    [Fact]
    public void WindowAcrossTwoTargetWallsIsAnError()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 20, 0, Window.At(8.0, 4.0, 1.0, 1.0));
        WallSurface first = TestZones.Wall("P/W1", "P", 0, 0, 10, 0);
        WallSurface second = TestZones.Wall("Q/W1", "Q", 10, 0, 20, 0);

        Result<IReadOnlyList<Surface>> result = WindowRehosting.Rehost(new Surface[] { source }, new Surface[] { first, second }, ToleranceSettings.Default);

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.WindowNotHosted && d.Subject == "A/W1");
    }

    [Fact]
    public void WindowsOnlyMoveToWallsAtTheSameElevation()
    {
        WallSurface source = TestZones.Wall("A/W1", "A", 0, 0, 10, 0, Window.At(1.0, 2.0, 0.5, 1.0));
        WallSurface upstairs = TestZones.WallAt("B/W1", "B", 0, 0, 10, 0, 3.0);

        Assert.False(WindowRehosting.Rehost(new Surface[] { source }, new Surface[] { upstairs }, ToleranceSettings.Default).IsSuccess);
    }
}
```

The first test merges two 10 m source walls into one 20 m target wall: the right-hand window moves from offset 2 m on its own wall to 12 m on the merged wall, sizes and sills unchanged. The second puts a 4 m window across the boundary of two target walls (8–12 m): no single wall contains it. The third offers only a wall one storey higher.

- [x] **Step 2: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected: the build fails with

```text
tests\Lod.Core.Tests\Simplification\WindowRehostingTests.cs(21,41): error CS0103: The name 'WindowRehosting' does not exist in the current context
tests\Lod.Core.Tests\Simplification\WindowRehostingTests.cs(37,49): error CS0103: The name 'WindowRehosting' does not exist in the current context
tests\Lod.Core.Tests\Simplification\WindowRehostingTests.cs(49,22): error CS0103: The name 'WindowRehosting' does not exist in the current context
```

- [x] **Step 3: Implement the re-hosting**

Create `src/Lod.Core/Simplification/WindowRehosting.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>
/// Keeps every source window unchanged when walls are rebuilt (W0 at every zoning level, D-039): each window of a source outdoor wall moves to
/// the target outdoor wall on the same façade line that contains it entirely, at the same position, sill, and size. A window that no single target
/// wall contains is an error; windows are never moved, resized, or split silently.
/// </summary>
public static class WindowRehosting
{
    /// <summary>Re-hosts the windows of the source outdoor walls on the target outdoor walls.</summary>
    /// <param name="sourceSurfaces">Source surfaces with windows.</param>
    /// <param name="targetSurfaces">Target surfaces; their outdoor walls receive the windows (any windows they already have are replaced).</param>
    /// <param name="tolerances">Tolerances.</param>
    /// <returns>The target surfaces with windows, or <see cref="DiagnosticCodes.WindowNotHosted"/> errors.</returns>
    public static Result<IReadOnlyList<Surface>> Rehost(IEnumerable<Surface> sourceSurfaces, IReadOnlyList<Surface> targetSurfaces, ToleranceSettings tolerances)
    {
        WallSurface[] hosts = targetSurfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors).ToArray();
        var hosted = hosts.ToDictionary(h => h.Id, _ => new List<Window>());
        var diagnostics = new List<Diagnostic>();
        foreach (WallSurface source in sourceSurfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors))
        {
            foreach (Window window in source.Windows)
            {
                (WallSurface Host, double Offset)? placement = Place(source, window, hosts, tolerances);
                if (placement is { } p)
                {
                    hosted[p.Host.Id].Add(window.MovedTo(p.Offset));
                }
                else
                {
                    diagnostics.Add(Diagnostic.Error(
                        DiagnosticCodes.WindowNotHosted,
                        $"No single target wall contains the window at offset {window.Offset:0.###} m (width {window.Width:0.###} m).",
                        source.Id.Value));
                }
            }
        }

        return Result.FromDiagnostics<IReadOnlyList<Surface>>(
            () => targetSurfaces.Select(s => s is WallSurface w && hosted.TryGetValue(w.Id, out List<Window>? windows) ? w.WithWindows(windows) : s).ToArray(),
            diagnostics);
    }

    private static (WallSurface Host, double Offset)? Place(WallSurface source, Window window, IEnumerable<WallSurface> hosts, ToleranceSettings tolerances)
    {
        foreach (WallSurface host in hosts)
        {
            if (FacadeAttribution.Interval(host, source, tolerances) is not { } interval)
            {
                continue;
            }

            double start = interval.Start + window.Offset;
            double end = start + window.Width;
            if (start >= -tolerances.Distance && end <= host.Length + tolerances.Distance)
            {
                // Clamping only removes floating-point noise below the distance tolerance.
                return (host, Math.Min(Math.Max(0.0, start), host.Length - window.Width));
            }
        }

        return null;
    }
}
```

- [x] **Step 4: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Simplification"
```

Expected: `Passed!  - Failed:     0, Passed:    10, Skipped:     0, Total:    10` for `net8.0`.

- [x] **Step 5: Run the whole core suite**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:   104, Skipped:     0, Total:   104` for `net8.0` (the final S3 core count).

- [x] **Step 6: Commit**

```bash
git add src/Lod.Core/Simplification/WindowRehosting.cs tests/Lod.Core.Tests/Simplification/WindowRehostingTests.cs
git commit -m "feature(windows): re-host source windows unchanged on covering target walls"
```

- [x] **Step 7: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/mapping-overlap
git push origin main
git branch -d feature/mapping-overlap
```

Expected from `verify.ps1`: `Build succeeded.` with `0 Warning(s)`, then `Passed!` lines with 104 core, 17 generators, and 9 integration tests for `net8.0`, then `VERIFY PASSED`.

---

## Slice B — `docs/decisions-perimeter-corner-rule`

### Task 4: ADR-008 perimeter/core corner rule

**Files:**
- Create: `docs/decisions/ADR-008-perimeter-core-corners.md`
- Modify: `docs/decisions/decision-log.md`

**Interfaces:**
- Consumes: research brief §8 (Z2) and §9; D-034, D-038, D-039, D-041; ADR-002 (geometry, Clipper2), ADR-004 (tolerances), ADR-005 and ADR-007 (aggregation).
- Produces: the rule Task 7 implements (`PerimeterCore`), its zone IDs (`P-North`, `P-East`, `P-South`, `P-West`, suffixes `-1`, `-2`, …, `CORE`), its errors (`InvalidParameter`, `NotSupported`, `PlanTooNarrow`), and decision D-043.

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c docs/decisions-perimeter-corner-rule main
```

- [x] **Step 2: Write the ADR**

Create `docs/decisions/ADR-008-perimeter-core-corners.md` with exactly this content:

````markdown
# ADR-008: Perimeter/core corner rule

Status: Accepted
Date: 2026-10-01
Decisions: D-043; applies D-034, D-039, D-041

## Context

Z2 in the research brief (§8) re-zones a floor plate into north, east, south, and west perimeter zones and a core, and admits other perimeter schemes. The roadmap (S3) asks for an inward offset by a perimeter depth, a perimeter split by orientation, a core, a corner rule recorded in this ADR, and a diagnostic, never a silent repair, for plans too narrow for a core.

Near a corner, floor area lies within the perimeter depth of two façades. The rule that assigns it decides:

- how much floor area, and therefore how much of each source zone's loads and occupancy (area fractions, ADR-007), each perimeter zone receives;
- whether each perimeter zone spans its whole façade, so that one zone holds all the windows of one orientation (source windows stay in place on the wall that contains them, D-039);
- which interzone walls appear between perimeter zones.

A perimeter or core zone mixes dwelling units, corridor, and stair, so it also needs a space type.

In S3 the only generator is the rectangular linear plan (S2). Footprints with holes (courtyards) and irregular outlines arrive with the typologies in S8.

## Options considered

1. **Bisector trapezoids.** Offset every footprint edge inward by the depth with mitred joints. Each edge owns the trapezoid between the edge and its offset edge; neighbouring trapezoids meet on the angle bisector of the corner, the usual perimeter/core convention. The offset ring is the core.
   - For: symmetric, no tie-breaking; every perimeter zone spans its whole façade, so it holds exactly the windows of its orientation; one formula for any simple outline; the pieces are exact polygons whose tiling can be checked.
   - Against: diagonal interzone walls at the corners; at a sharp corner the core vertex lies far from the footprint vertex (`d / sin(θ/2)` for interior angle θ), and on non-convex outlines trapezoids can overlap, so validity must be checked.
2. **Rectangular strips with corner squares assigned to one orientation** (for example, corners go to the longer façades).
   - For: only orthogonal walls; simple for rectangles.
   - Against: an arbitrary, asymmetric choice that moves `d²` of floor area per corner between orientations; the zone that receives a corner square also receives a piece of the neighbouring façade, so one perimeter zone holds walls and windows of two orientations; defined only for orthogonal outlines.
3. **Straight skeleton.** Partition the footprint by its straight skeleton, which also handles non-convex outlines and holes; for convex outlines its first events coincide with the bisector trapezoids.
   - For: the general answer for S8 shapes.
   - Against: needs an algorithm the project does not have (the project uses Clipper2 for Boolean operations only, ADR-002), so a skeleton would have to be written and tested; much more code for no difference on the S3 plans.

## Decision

`PerimeterCore` (Z2) uses bisector trapezoids (option 1):

1. The perimeter depth `d` must be positive and finite; otherwise the error `InvalidParameter`.
2. Footprints with holes fail with `NotSupported` until S8 adds courtyard plans.
3. For the counter-clockwise outer ring `v₀ … vₙ₋₁`, the core vertex of `vᵢ` is its mitred inward offset `oᵢ = vᵢ + (a + b)·d / (1 + a·b)`, where `a` and `b` are the inward unit normals of the edges entering and leaving `vᵢ`. `oᵢ` lies on the bisector of the corner, at distance `d` from both edges. The offset is computed directly from this formula, not by a general polygon offset, so core vertex `i` belongs to footprint vertex `i` (ADR-002 leaves the inward offset to this ADR).
4. Edge `i` owns the trapezoid `vᵢ, vᵢ₊₁, oᵢ₊₁, oᵢ`. The trapezoid is binned by the true azimuth of the edge's outward normal (plan azimuth plus plan orientation) into North [315°, 45°), East [45°, 135°), South [135°, 225°), or West [225°, 315°), the bins used for glazing.
5. Validity checks, all required. Any failure is the error `PlanTooNarrow`, and no zones are produced: no repair, no reduced depth.
   - The offset ring `o₀ … oₙ₋₁` is a valid polygon and counter-clockwise (positive signed area).
   - Every offset edge keeps the direction of its footprint edge (positive dot product). A reversed edge means the depth exceeds what the edge's length and corner angles allow.
   - The trapezoids and the core tile the footprint: the sum of their areas equals the footprint area within `RelativeArea` (ADR-004). This catches overlapping trapezoids on non-convex outlines.
6. Trapezoids of the same bin are united. A bin that unites into one polygon becomes zone `P-<Bin>` ("Perimeter <Bin>"); a bin that yields several polygons becomes `P-<Bin>-1`, `P-<Bin>-2`, … in union output order, so every zone is one polygon. Zones are listed North, East, South, West, then the core `CORE` ("Core").
7. Perimeter and core zones get space type `Mixed`. Their programs, including conditioning and setpoints, come only from aggregating the source zones (ADR-005, ADR-007, D-038), never from a preset.
8. Everything after the footprints is the shared simplification pipeline: surfaces are rebuilt from the target footprints, so walls between merged sources disappear (D-034); the target façades must cover every source façade (D-041); every source window moves unchanged onto the perimeter wall that contains it (D-039); the core has no outdoor walls and no windows.
9. The depth is recorded in provenance as `PerimeterDepth`. The *Perimeter Core* Grasshopper component offers 4.57 m as the default of its `Depth` input. This default is an input convenience, not a sourced value and not a research rule; experiments set the depth explicitly.

## Consequences

- At a right-angled corner each of the two façades receives a triangle of `d²/2`. For the canonical 24 m × 18 m linear plan with `d` = 4.57 m: P-North and P-South 88.7951 m² each, P-East and P-West 61.3751 m² each, and a 14.86 m × 8.86 m core of 131.6596 m².
- Each corner gets a diagonal interzone wall between two perimeter zones (canonical plan: 4.57 m × √2 = 6.462956 m long, 19.388868 m² at a 3 m storey height). The Z0 plan has no such walls; their effect is part of what Z2 measures.
- Each footprint edge becomes the outdoor wall of exactly one perimeter zone, so the façade is covered and every source window, which lies on one footprint edge, finds its host wall. On the canonical plan P-South keeps the three south windows at their positions (19.2 m² of glazing).
- Source zones at corners are split between up to three targets (on the canonical plan the stair maps 8 m² to P-North, 8 m² to P-South, and 56 m² to P-West). Area fractions are normalised per source, so loads stay conserved exactly. Because the stair is unconditioned in the example presets and every perimeter zone also receives conditioned sources, the conditioned floor area grows; validation reports this (D-038).
- A plan narrower than `2d` fails: the canonical plan with `d` = 10 m returns `PlanTooNarrow`. The user chooses a smaller depth; the simplifier never chooses one.
- Non-convex outlines that pass the checks are supported; those that fail are rejected, not repaired. A bin with two separate façade runs (for example two south-facing steps) becomes two zones. If S8 typologies need more, a straight-skeleton rule would supersede this ADR.
- Footprints with holes are rejected until S8, which must extend this rule to courtyard façades or supersede it.
- Every Z2 zone reports space type `Mixed` in `Convert2BEM`.
- This ADR changes no equivalence rule: research brief §8 already admits other perimeter schemes, and the aggregation (ADR-005, ADR-007, D-038) and window (D-039) rules are unchanged, so the research documentation needs no edit (GLOBAL.md scientific rule 7).
````

- [x] **Step 3: Record the decision**

Append at the end of `docs/decisions/decision-log.md`, after the last entry (S0's `### D-042 — Foundation ADRs accepted`, unless later entries were added), with one blank line before it. D-043 is reserved for this ADR; check that it is still free before appending.

```markdown
### D-043 — Perimeter/core corners are split on the bisectors

- **Date:** 2026-10-01 · **Decided by:** Cheng Xuan Li · **Status:** Accepted
- `PerimeterCore` (Z2) gives each footprint edge the trapezoid between the edge and its inward mitred offset by the perimeter depth, so corners are split along the angle bisectors. Trapezoids in the same orientation bin merge into one perimeter zone (suffixes `-1`, `-2` when they do not form one polygon); the offset ring is the core. Perimeter and core zones have space type `Mixed`.
- Footprints too narrow for a valid core fail with `PlanTooNarrow` and are never repaired; footprints with holes are not supported until S8. The 4.57 m default depth of the Grasshopper component is an input default, not a research rule.
- Written up in [ADR-008](ADR-008-perimeter-core-corners.md).
```

- [x] **Step 4: Commit**

```bash
git add docs/decisions/ADR-008-perimeter-core-corners.md docs/decisions/decision-log.md
git commit -m "docs(decisions): add adr-008 perimeter/core corner rule"
```

- [x] **Step 5: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only docs/decisions-perimeter-corner-rule
git push origin main
git branch -d docs/decisions-perimeter-corner-rule
```

Expected from `verify.ps1`: 104 core, 17 generators, 9 integration tests passed on `net8.0`, then `VERIFY PASSED`.

---

## Slice C — `feature/simplifiers`

`Strategies.cs` grows over Tasks 5–7 (Task 7 shows the full file); `SimplifierTests.cs` grows over Tasks 5–9 (Task 9 shows the full file).

### Task 5: Shared simplification pipeline and SingleZonePerFloor (Z3)

**Files:**
- Create: `src/Lod.Core/Simplification/PlanSimplifier.cs`
- Create: `src/Lod.Core/Simplification/Strategies.cs` (first class: `SingleZonePerFloor`)
- Test: `tests/Lod.Integration.Tests/SimplifierTests.cs`

**Interfaces:**
- Consumes: `IPlanSimplifier.Simplify(IGeneratedPlan)`, `IGeneratedPlan`, `IFloor`, `Floor`, `Zone`, `ZonePart`, `LayoutSurfaceBuilder.Build(Polygon2, IReadOnlyList<LayoutZone>, double)`, `LayoutZone`, `LayoutMeasures.Of`, `LayoutMeasures.ExteriorWallArea`, `Provenance.Of`, `Result.FromDiagnostics` (S2); `ZoneMeasures`, `SourceZoneContribution(ZoneId Zone, ZoneProgram Program, ZoneMeasures Measures, double AreaFraction, double ExteriorWallFraction)`, `EquivalentPropertyAggregator.Aggregate`, `ZoneProgram.Thermostat`, `Thermostat.HeatingSetpoint` (S1); `OverlapMapper`, `TransferMatrix`, `FacadeAttribution`, `WindowRehosting`, `DiagnosticCodes.FacadeNotCovered` (Tasks 1–3); test helper `Pipeline` (`Plan`, `Floor`, `DetailedFloor`, `Tolerances`, `Canonical`) from S2.
- Produces:
  - `public sealed record TargetZone(ZoneId Id, string Name, SpaceType SpaceType, Polygon2 Footprint);`
  - `public abstract class PlanSimplifier : IPlanSimplifier { protected PlanSimplifier(ToleranceSettings tolerances); public abstract string Name { get; } protected ToleranceSettings Tolerances { get; } public Result<IFloor> Simplify(IGeneratedPlan plan); protected abstract Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan); protected abstract IEnumerable<KeyValuePair<string, string>> Describe(); }`
  - `public sealed class SingleZonePerFloor : PlanSimplifier { public SingleZonePerFloor(ToleranceSettings tolerances); }`: one zone `FLOOR` ("Floor") with the plan footprint; its space type is the plan's single space type, or `Mixed` when the plan has several.

**The shared pipeline (`PlanSimplifier.Simplify`).** A strategy only proposes target footprints; everything else is shared, so all simplifiers obey the same rules:

1. **Propose zones.** `ProposeZones(plan)` returns `TargetZone`s that must tile the plan footprint, or errors (returned unchanged).
2. **Rebuild surfaces.** `LayoutSurfaceBuilder.Build(plan.Footprint, targets, plan.FloorHeight)` builds walls, floors, and ceilings from the *target* footprints. Proposals with gaps or overlaps fail here with the S2 errors. Because surfaces come from target footprints, walls between source zones merged into one target do not exist any more (D-034); they are not converted into internal mass.
3. **Map sources to targets.** `OverlapMapper.Map` gives the overlap rows (kept on the floor as `IFloor.Mapping`, research brief §9); `TransferMatrix.FromMapping` gives the per-source normalised area fractions.
4. **Check façade coverage (D-041).** `FacadeAttribution.Compute(plan.Surfaces, rebuilt surfaces)`; every entry of `CoverageGaps()` becomes an error `FacadeNotCovered` with the source wall as subject, and the simplifier returns no floor.
5. **Re-host windows (D-039).** `WindowRehosting.Rehost(plan.Surfaces, rebuilt surfaces)` moves every source window unchanged onto its target wall; `WindowNotHosted` errors return no floor.
6. **Aggregate programs (ADR-005, ADR-007, D-038).** For each target, every source with a positive area fraction or exterior-wall fraction contributes `SourceZoneContribution(source, program, source measures, matrix.AreaFraction, facade.ExteriorWallFraction)`. `EquivalentPropertyAggregator` conserves each load's design magnitude and hourly scheduled magnitude, makes the target conditioned if any source contributing floor area is, and floor-area weights the setpoints over the conditioned sources only. The target zone records the contributing sources as `SourceZones`.
7. **Assemble.** The floor keeps the plan as `Source`, the zones, the surfaces with their windows, the mapping, and provenance `Provenance.Of(Name, Describe(), plan.Provenance)`. Any aggregation error makes the whole result a failure (`Result.FromDiagnostics`); warnings and info travel with a successful result.

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c feature/simplifiers main
```

- [x] **Step 2: Write the failing Z3 tests**

Create `tests/Lod.Integration.Tests/SimplifierTests.cs`. The constant `PerimeterDepth` (4.57 m, the default of the *Perimeter Core* component's `Depth` input, not a sourced value) and the usings `System.Collections.Generic` and `Lod.Core.Geometry` are used from Task 7; `using Lod.Core.Validation;` and the private helpers `Simplifier` and `RandomParameters` are added in Task 8, when that namespace and all three strategies exist.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;
using Lod.Generators.Linear;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class SimplifierTests
{
    private const double PerimeterDepth = 4.57;

    [Fact]
    public void SingleZonePerFloorHasOnlyOutdoorWalls()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Zone zone = Assert.Single(floor.Zones);
        Assert.Equal(SpaceType.Mixed, zone.SpaceType);
        Assert.Equal(6, zone.SourceZones.Count);
        Assert.All(floor.Surfaces.OfType<WallSurface>(), w => Assert.Equal(BoundaryCondition.Outdoors, w.Boundary));
        Assert.Equal(4, floor.Surfaces.OfType<WallSurface>().Count());
    }

    [Fact]
    public void SetpointsAreFloorAreaWeightedAndRecorded()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Thermostat thermostat = floor.Zones[0].Program.Thermostat!;
        Assert.Equal(21.0, thermostat.HeatingSetpoint[0], 9);
        Assert.Equal(Lod.Core.Aggregation.AggregationMethod.FloorAreaWeighted, thermostat.HeatingSetpoint.Aggregation!.Method);
        Assert.DoesNotContain(new ZoneId("ST"), thermostat.HeatingSetpoint.Aggregation.Sources);
        Assert.Equal(5, thermostat.HeatingSetpoint.Aggregation.Sources.Count);
    }
}
```

The canonical plan (S2 `Pipeline.Canonical`: 24 m × 18 m, 4 m stair, 2 m corridor, two 10 m × 8 m units per row, 3 m storeys) has six zones (`ST`, `CO`, `US1`, `US2`, `UN1`, `UN2`) of three space types, so Z3 gives one `Mixed` zone with six sources and four outdoor walls. In the example presets the stair is unconditioned (illustrative, D-038), so the setpoints are weighted over the five conditioned sources only; all of them use 21 °C heating, so the result is 21 °C.

- [x] **Step 3: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: the build fails with

```text
tests\Lod.Integration.Tests\SimplifierTests.cs(23,43): error CS0246: The type or namespace name 'SingleZonePerFloor' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(35,43): error CS0246: The type or namespace name 'SingleZonePerFloor' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 4: Implement the shared pipeline**

Create `src/Lod.Core/Simplification/PlanSimplifier.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Simplification;

/// <summary>A target zone proposed by a simplification strategy.</summary>
/// <param name="Id">Zone ID.</param>
/// <param name="Name">Display name.</param>
/// <param name="SpaceType">Space type, <see cref="SpaceType.Mixed"/> when the target combines several types.</param>
/// <param name="Footprint">Zone polygon.</param>
public sealed record TargetZone(ZoneId Id, string Name, SpaceType SpaceType, Polygon2 Footprint);

/// <summary>
/// Shared simplification pipeline (S3). A strategy only proposes target footprints; this class maps sources to targets, rebuilds surfaces
/// (partitions between merged sources disappear, D-034), checks that the target façades cover every source façade (D-041), keeps every source
/// window in place on the target wall that contains it (D-039), and aggregates programs (ADR-005, ADR-007, D-038).
/// </summary>
public abstract class PlanSimplifier : IPlanSimplifier
{
    /// <summary>Initialises the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    protected PlanSimplifier(ToleranceSettings tolerances)
    {
        Tolerances = tolerances;
    }

    /// <summary>Operation name recorded in provenance.</summary>
    public abstract string Name { get; }

    /// <summary>Tolerances.</summary>
    protected ToleranceSettings Tolerances { get; }

    /// <inheritdoc />
    public Result<IFloor> Simplify(IGeneratedPlan plan)
    {
        Result<IReadOnlyList<TargetZone>> proposed = ProposeZones(plan);
        if (!proposed.IsSuccess)
        {
            return Result.Failure<IFloor>(proposed.Diagnostics);
        }

        IReadOnlyList<TargetZone> targets = proposed.Value;
        Result<IReadOnlyList<Surface>> built = new LayoutSurfaceBuilder(Tolerances)
            .Build(plan.Footprint, targets.Select(t => new LayoutZone(t.Id, t.Footprint)).ToArray(), plan.FloorHeight);
        if (!built.IsSuccess)
        {
            return Result.Failure<IFloor>(built.Diagnostics);
        }

        IReadOnlyList<ZoneMapping> mapping = new OverlapMapper(Tolerances).Map(plan.Zones, targets.Select(t => (t.Id, t.Footprint)).ToArray());
        TransferMatrix matrix = TransferMatrix.FromMapping(mapping);
        FacadeAttribution facade = FacadeAttribution.Compute(plan.Surfaces, built.Value, Tolerances);
        Diagnostic[] gaps = facade.CoverageGaps()
            .Select(g => Diagnostic.Error(
                DiagnosticCodes.FacadeNotCovered,
                $"Target façades cover {g.CoveredLength:0.######} m of this {g.Wall.Length:0.######} m wall (D-041).",
                g.Wall.Id.Value))
            .ToArray();
        if (gaps.Length > 0)
        {
            return Result.Failure<IFloor>(gaps);
        }

        Result<IReadOnlyList<Surface>> rehosted = WindowRehosting.Rehost(plan.Surfaces, built.Value, Tolerances);
        if (!rehosted.IsSuccess)
        {
            return Result.Failure<IFloor>(rehosted.Diagnostics);
        }

        IReadOnlyList<Surface> surfaces = rehosted.Value;
        var diagnostics = new List<Diagnostic>(proposed.Diagnostics);
        var aggregator = new EquivalentPropertyAggregator(Tolerances);
        var zones = new List<Zone>();
        foreach (TargetZone target in targets)
        {
            var part = new ZonePart(target.Footprint, 0.0, plan.FloorHeight);
            var targetMeasures = new ZoneMeasures(part.Footprint.Area, part.Volume, LayoutMeasures.ExteriorWallArea(target.Id, surfaces));
            SourceZoneContribution[] contributions = plan.Zones
                .Select(s => new SourceZoneContribution(
                    s.Id,
                    s.Program,
                    LayoutMeasures.Of(s, plan.Surfaces),
                    matrix.AreaFraction(s.Id, target.Id),
                    facade.ExteriorWallFraction(s.Id, target.Id)))
                .Where(c => c.AreaFraction > 0.0 || c.ExteriorWallFraction > 0.0)
                .ToArray();
            Result<ZoneProgram> program = aggregator.Aggregate(target.Id, targetMeasures, contributions);
            diagnostics.AddRange(program.Diagnostics);
            if (program.IsSuccess)
            {
                zones.Add(new Zone(target.Id, target.Name, target.SpaceType, new[] { part }, program.Value, contributions.Select(c => c.Zone)));
            }
        }

        var provenance = Provenance.Of(Name, Describe(), plan.Provenance);
        return Result.FromDiagnostics<IFloor>(() => new Floor(plan, zones, surfaces, mapping, provenance), diagnostics);
    }

    /// <summary>Proposes target zones tiling the plan footprint.</summary>
    /// <param name="plan">The detailed plan.</param>
    /// <returns>Target zones, or errors.</returns>
    protected abstract Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan);

    /// <summary>Strategy parameters for provenance.</summary>
    /// <returns>Key-value pairs.</returns>
    protected abstract IEnumerable<KeyValuePair<string, string>> Describe();
}
```

- [x] **Step 5: Implement SingleZonePerFloor**

Create `src/Lod.Core/Simplification/Strategies.cs` with the final using block (the `System` and `Lod.Core.Geometry` usings are needed from Tasks 6–7; unused usings do not warn):

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Simplification;

/// <summary>Z3: the whole floor as one zone.</summary>
public sealed class SingleZonePerFloor : PlanSimplifier
{
    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SingleZonePerFloor(ToleranceSettings tolerances)
        : base(tolerances)
    {
    }

    /// <inheritdoc />
    public override string Name => nameof(SingleZonePerFloor);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        SpaceType[] types = plan.Zones.Select(z => z.SpaceType).Distinct().ToArray();
        SpaceType type = types.Length == 1 ? types[0] : SpaceType.Mixed;
        return Result.Success<IReadOnlyList<TargetZone>>(new[] { new TargetZone(new ZoneId("FLOOR"), "Floor", type, plan.Footprint) });
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() => Enumerable.Empty<KeyValuePair<string, string>>();
}
```

- [x] **Step 6: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: `Passed!  - Failed:     0, Passed:     2, Skipped:     0, Total:     2` for `net8.0`.

- [x] **Step 7: Run the whole integration suite**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    11, Skipped:     0, Total:    11` for `net8.0`.

- [x] **Step 8: Commit**

```bash
git add src/Lod.Core/Simplification/PlanSimplifier.cs src/Lod.Core/Simplification/Strategies.cs tests/Lod.Integration.Tests/SimplifierTests.cs
git commit -m "feature(rezoning): add shared plan simplifier pipeline and single zone per floor"
```

### Task 6: SemanticMerge (Z1)

**Files:**
- Modify: `src/Lod.Core/Simplification/Strategies.cs` (add `SemanticMerge`)
- Test: `tests/Lod.Integration.Tests/SimplifierTests.cs` (add two tests)

**Interfaces:**
- Consumes: `PlanSimplifier`, `TargetZone` (Task 5); `PolygonOps.Union` (S2); `DiagnosticCodes.DisconnectedGroup` (Task 1).
- Produces: `public sealed class SemanticMerge : PlanSimplifier { public SemanticMerge(ToleranceSettings tolerances); }`. Zone IDs `<SpaceType>-<n>` (names `<SpaceType> <n>`), numbered per space type in discovery order; error `DisconnectedGroup`.

**Rule.** Starting from each not-yet-visited plan zone in plan order, a breadth-first search follows interzone walls to neighbours of the same space type; each connected group becomes one target whose footprint is the union of its members. A group whose union is not exactly one polygon fails with `DisconnectedGroup`. On the canonical plan: `ST` → `Stair-1`, `CO` → `Corridor-1`, `US1`+`US2` → `DwellingUnit-1` (160 m²), `UN1`+`UN2` → `DwellingUnit-2`; the two unit rows stay separate because the corridor lies between them. The south row loses its shared partition and keeps two outdoor walls (south and east). `Stair-1` stays unconditioned, so Z1 does not change the conditioned floor area.

- [x] **Step 1: Write the failing Z1 tests**

In `SimplifierTests`, insert these tests between the constant `PerimeterDepth` (and its following blank line) and the `[Fact]` of `SingleZonePerFloorHasOnlyOutdoorWalls`, followed by one blank line:

```csharp
    [Fact]
    public void SemanticMergeJoinsConnectedZonesOfTheSameType()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.Equal(new[] { "Stair-1", "Corridor-1", "DwellingUnit-1", "DwellingUnit-2" }, floor.Zones.Select(z => z.Id.Value));
        Zone south = floor.Zones.Single(z => z.Id.Value == "DwellingUnit-1");
        Assert.Equal(160.0, south.FloorArea, 6);
        Assert.Equal(new[] { "US1", "US2" }, south.SourceZones.Select(s => s.Value));
        Assert.Equal(5.0, south.Program.Find(LoadType.Lighting, LoadBasis.PerFloorArea)!.Value, 9);
    }

    [Fact]
    public void MergedZonesLoseTheirSharedPartition()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.DoesNotContain(floor.Surfaces, s => s.Zone == s.AdjacentZone);
        Assert.Equal(2, floor.Surfaces.OfType<WallSurface>().Count(w => w.Zone.Value == "DwellingUnit-1" && w.Boundary == BoundaryCondition.Outdoors));
    }
```

- [x] **Step 2: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: the build fails with

```text
tests\Lod.Integration.Tests\SimplifierTests.cs(23,43): error CS0246: The type or namespace name 'SemanticMerge' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(35,43): error CS0246: The type or namespace name 'SemanticMerge' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Implement SemanticMerge**

In `src/Lod.Core/Simplification/Strategies.cs`, insert this class directly after `namespace Lod.Core.Simplification;` and its blank line, before `/// <summary>Z3: the whole floor as one zone.</summary>`, followed by one blank line:

```csharp
/// <summary>
/// Z1: merges zones of the same space type that are connected through shared walls. Each connected group becomes one zone.
/// </summary>
public sealed class SemanticMerge : PlanSimplifier
{
    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SemanticMerge(ToleranceSettings tolerances)
        : base(tolerances)
    {
    }

    /// <inheritdoc />
    public override string Name => nameof(SemanticMerge);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        Dictionary<ZoneId, Zone> byId = plan.Zones.ToDictionary(z => z.Id);
        ILookup<ZoneId, ZoneId> neighbours = plan.Surfaces
            .Where(s => s.Boundary == BoundaryCondition.Interzone)
            .ToLookup(s => s.Zone, s => s.AdjacentZone!.Value);
        var ops = new PolygonOps(Tolerances);
        var visited = new HashSet<ZoneId>();
        var targets = new List<TargetZone>();
        var counters = new Dictionary<SpaceType, int>();
        foreach (Zone seed in plan.Zones.Where(z => !visited.Contains(z.Id)))
        {
            var group = new List<Zone>();
            var queue = new Queue<Zone>(new[] { seed });
            visited.Add(seed.Id);
            while (queue.Count > 0)
            {
                Zone current = queue.Dequeue();
                group.Add(current);
                foreach (ZoneId next in neighbours[current.Id].Where(n => !visited.Contains(n) && byId[n].SpaceType == seed.SpaceType))
                {
                    visited.Add(next);
                    queue.Enqueue(byId[next]);
                }
            }

            IReadOnlyList<Polygon2> union = ops.Union(group.Select(z => z.Parts[0].Footprint));
            if (union.Count != 1)
            {
                return Result.Failure<IReadOnlyList<TargetZone>>(Diagnostic.Error(
                    DiagnosticCodes.DisconnectedGroup,
                    $"Merged group {string.Join(",", group.Select(z => z.Id.Value))} is not one polygon.",
                    seed.Id.Value));
            }

            int number = counters.TryGetValue(seed.SpaceType, out int n) ? n + 1 : 1;
            counters[seed.SpaceType] = number;
            targets.Add(new TargetZone(new ZoneId($"{seed.SpaceType}-{number}"), $"{seed.SpaceType} {number}", seed.SpaceType, union[0]));
        }

        return Result.Success<IReadOnlyList<TargetZone>>(targets);
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() => Enumerable.Empty<KeyValuePair<string, string>>();
}
```

- [x] **Step 4: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: `Passed!  - Failed:     0, Passed:     4, Skipped:     0, Total:     4` for `net8.0`.

- [x] **Step 5: Run the whole integration suite**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    13, Skipped:     0, Total:    13` for `net8.0`.

- [x] **Step 6: Commit**

```bash
git add src/Lod.Core/Simplification/Strategies.cs tests/Lod.Integration.Tests/SimplifierTests.cs
git commit -m "feature(rezoning): add semantic merge simplifier"
```

### Task 7: PerimeterCore (Z2)

**Files:**
- Modify: `src/Lod.Core/Simplification/Strategies.cs` (add `PerimeterCore`)
- Test: `tests/Lod.Integration.Tests/SimplifierTests.cs` (add five test methods with six test cases, and the private `ToleranceComparer`)

**Interfaces:**
- Consumes: ADR-008 (Task 4); `PlanSimplifier`, `TargetZone` (Task 5); `Polygon2.Create`, `Polygon2.SignedArea`, `Polygon2.Outer`, `Polygon2.Holes`, `Point2.DistanceTo`, `Orientation.Bin`, `Orientation.OutwardAzimuth`, `PolygonOps.Union`, `ToleranceSettings.AreaEquals`, `Provenance.Format` (S2); `DiagnosticCodes.InvalidParameter` (S2), `.NotSupported`, `.PlanTooNarrow` (Task 1); in the tests also `GeneratedPlan(Polygon2, double, double, IEnumerable<Zone>, IEnumerable<Surface>, Provenance)`, `Point2`, `Provenance.Of`, and `WallSurface.Windows` (S2).
- Produces: `public sealed class PerimeterCore : PlanSimplifier { public PerimeterCore(ToleranceSettings tolerances, double perimeterDepth); }`. Zone IDs `P-North`, `P-East`, `P-South`, `P-West` (with `-1`, `-2`, … when a bin yields several polygons) and `CORE`, all `SpaceType.Mixed`; provenance parameter `PerimeterDepth`.

**Rule.** Exactly ADR-008: mitred inward offset `oᵢ = vᵢ + (a + b)·d / (1 + a·b)`, one trapezoid per edge, binned by true outward azimuth, united per bin; `PlanTooNarrow` when the offset ring is invalid or clockwise, an offset edge reverses, or the pieces do not tile the footprint within `RelativeArea`; `NotSupported` for holes (until S8); `InvalidParameter` for a depth that is not positive and finite. The tests use the constant `PerimeterDepth` = 4.57 m (the Grasshopper input default, ADR-008), 10 m (more than half the 18 m plan depth, so `PlanTooNarrow`), 0 and −1 m (`InvalidParameter`), and a 30 m × 30 m footprint with a 10 m × 10 m courtyard hole, built directly as a `GeneratedPlan` without zones (`NotSupported`, checked before any geometry is computed).

`PerimeterSouthKeepsTheSouthFacadeWindowsInPlace` checks D-039 on the canonical plan. The south façade (y = 0) has three generator windows: the stair's (wall 4 m, WWR 0.1: width 1.264911 m centered, offset 1.367544 m), and one per south unit (wall 10 m, WWR 0.3: width 5.477226 m, offsets 4 + 2.261387 = 6.261387 m and 14 + 2.261387 = 16.261387 m). The P-South outdoor wall runs from (0, 0) to (24, 0), so it must hold exactly these three windows at offsets 1.367544, 6.261387, and 16.261387 m, with 1.2 + 9 + 9 = 19.2 m² of glazing. The private `ToleranceComparer` compares the offsets with `AreaEquals`.

- [x] **Step 1: Write the failing Z2 tests**

In `SimplifierTests`:

1. Insert these tests after `MergedZonesLoseTheirSharedPartition` and before the `[Fact]` of `SingleZonePerFloorHasOnlyOutdoorWalls`, with one blank line on each side:

```csharp
    [Fact]
    public void PerimeterCoreHasFourPerimeterZonesAndACore()
    {
        IFloor floor = Pipeline.Floor(new PerimeterCore(Pipeline.Tolerances, PerimeterDepth));

        Assert.Equal(new[] { "P-North", "P-East", "P-South", "P-West", "CORE" }, floor.Zones.Select(z => z.Id.Value));
        Assert.Equal((24.0 - (2 * PerimeterDepth)) * (18.0 - (2 * PerimeterDepth)), floor.Zones.Single(z => z.Id.Value == "CORE").FloorArea, 6);
        Assert.DoesNotContain(floor.Surfaces.OfType<WallSurface>(), w => w.Zone.Value == "CORE" && w.Boundary == BoundaryCondition.Outdoors);
    }

    [Fact]
    public void PerimeterSouthKeepsTheSouthFacadeWindowsInPlace()
    {
        IGeneratedPlan plan = Pipeline.Plan();
        IFloor floor = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(plan).Value;

        double[] expected = plan.Surfaces.OfType<WallSurface>()
            .Where(w => w.Start.Y == 0.0 && w.End.Y == 0.0 && w.Boundary == BoundaryCondition.Outdoors)
            .SelectMany(w => w.Windows.Select(window => w.Start.X + window.Offset))
            .OrderBy(x => x)
            .ToArray();
        WallSurface south = floor.Surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "P-South" && w.Boundary == BoundaryCondition.Outdoors);
        Assert.Equal(3, south.Windows.Count);
        Assert.Equal(expected, south.Windows.Select(w => w.Offset).ToArray(), new ToleranceComparer());
        Assert.Equal(1.2 + 9.0 + 9.0, south.GlazedArea, 9);
    }

    [Fact]
    public void PerimeterDepthTooLargeIsAnError()
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, 10.0).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.PlanTooNarrow);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(-1.0)]
    public void NonPositivePerimeterDepthIsAnError(double depth)
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, depth).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.InvalidParameter);
    }

    [Fact]
    public void FootprintsWithHolesAreNotSupportedYet()
    {
        Polygon2 courtyard = Polygon2.Create(
            new[] { new Point2(0, 0), new Point2(30, 0), new Point2(30, 30), new Point2(0, 30) },
            new[] { new[] { new Point2(10, 10), new Point2(20, 10), new Point2(20, 20), new Point2(10, 20) } }).Value;
        var plan = new GeneratedPlan(courtyard, 3.0, 0.0, new Zone[0], new Surface[0], Provenance.Of("Test", new KeyValuePair<string, string>[0]));

        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(plan);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.NotSupported);
    }
```

2. Insert this nested class before the class's closing brace, with one blank line before it:

```csharp
    private sealed class ToleranceComparer : IEqualityComparer<double>
    {
        public bool Equals(double x, double y) => Pipeline.Tolerances.AreaEquals(x, y);

        public int GetHashCode(double obj) => 0;
    }
```

- [x] **Step 2: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: the build fails with

```text
tests\Lod.Integration.Tests\SimplifierTests.cs(44,43): error CS0246: The type or namespace name 'PerimeterCore' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(55,28): error CS0246: The type or namespace name 'PerimeterCore' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(71,37): error CS0246: The type or namespace name 'PerimeterCore' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(81,37): error CS0246: The type or namespace name 'PerimeterCore' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Integration.Tests\SimplifierTests.cs(94,37): error CS0246: The type or namespace name 'PerimeterCore' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Implement PerimeterCore**

In `src/Lod.Core/Simplification/Strategies.cs`, insert this class after `SemanticMerge` and before `/// <summary>Z3: the whole floor as one zone.</summary>`, with one blank line on each side:

```csharp
/// <summary>
/// Z2: perimeter zones of a configurable depth plus a core (ADR-008). Each footprint edge owns the trapezoid between the edge and its inward
/// mitred offset, so corners are split along the bisectors; trapezoids in the same orientation bin are merged. Footprints with holes are not supported yet.
/// </summary>
public sealed class PerimeterCore : PlanSimplifier
{
    private readonly double _depth;

    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    /// <param name="perimeterDepth">Perimeter zone depth, m.</param>
    public PerimeterCore(ToleranceSettings tolerances, double perimeterDepth)
        : base(tolerances)
    {
        _depth = perimeterDepth;
    }

    /// <inheritdoc />
    public override string Name => nameof(PerimeterCore);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        if (!(_depth > 0) || double.IsInfinity(_depth))
        {
            return Fail(DiagnosticCodes.InvalidParameter, $"Perimeter depth must be positive, got {_depth}.");
        }

        if (plan.Footprint.Holes.Count > 0)
        {
            return Fail(DiagnosticCodes.NotSupported, "Perimeter/core of footprints with holes is not supported yet (S8, typologies).");
        }

        IReadOnlyList<Point2> v = plan.Footprint.Outer;
        int n = v.Count;
        Point2[] offset = Enumerable.Range(0, n).Select(i => Mitre(v[(i + n - 1) % n], v[i], v[(i + 1) % n])).ToArray();
        Result<Polygon2> core = Polygon2.Create(offset);
        bool keepsDirections = Enumerable.Range(0, n).All(i =>
        {
            Point2 a = v[i];
            Point2 b = v[(i + 1) % n];
            Point2 c = offset[i];
            Point2 d = offset[(i + 1) % n];
            return ((b.X - a.X) * (d.X - c.X)) + ((b.Y - a.Y) * (d.Y - c.Y)) > 0;
        });
        if (!core.IsSuccess || !keepsDirections || Polygon2.SignedArea(offset) <= 0)
        {
            return Fail(DiagnosticCodes.PlanTooNarrow, $"Perimeter depth {_depth} m leaves no valid core for this footprint.");
        }

        var ops = new PolygonOps(Tolerances);
        var trapezoids = new List<(OrientationBin Bin, Polygon2 Shape)>();
        for (int i = 0; i < n; i++)
        {
            Polygon2 shape = Polygon2.Create(new[] { v[i], v[(i + 1) % n], offset[(i + 1) % n], offset[i] }).Value;
            trapezoids.Add((Orientation.Bin(Orientation.OutwardAzimuth(v[i], v[(i + 1) % n]) + plan.OrientationDegrees), shape));
        }

        double tiled = trapezoids.Sum(t => t.Shape.Area) + core.Value.Area;
        if (!Tolerances.AreaEquals(plan.Footprint.Area, tiled))
        {
            return Fail(DiagnosticCodes.PlanTooNarrow, $"Perimeter zones and core cover {tiled:0.###} m² of a {plan.Footprint.Area:0.###} m² footprint.");
        }

        var targets = new List<TargetZone>();
        foreach (IGrouping<OrientationBin, (OrientationBin Bin, Polygon2 Shape)> bin in trapezoids.GroupBy(t => t.Bin).OrderBy(g => g.Key))
        {
            IReadOnlyList<Polygon2> merged = ops.Union(bin.Select(t => t.Shape));
            for (int k = 0; k < merged.Count; k++)
            {
                string suffix = merged.Count == 1 ? string.Empty : $"-{k + 1}";
                targets.Add(new TargetZone(new ZoneId($"P-{bin.Key}{suffix}"), $"Perimeter {bin.Key}{suffix}", SpaceType.Mixed, merged[k]));
            }
        }

        targets.Add(new TargetZone(new ZoneId("CORE"), "Core", SpaceType.Mixed, core.Value));
        return Result.Success<IReadOnlyList<TargetZone>>(targets);
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() =>
        new[] { new KeyValuePair<string, string>("PerimeterDepth", Provenance.Format(_depth)) };

    private Point2 Mitre(Point2 previous, Point2 vertex, Point2 next)
    {
        (double X, double Y) a = InwardNormal(previous, vertex);
        (double X, double Y) b = InwardNormal(vertex, next);
        double scale = _depth / (1.0 + (a.X * b.X) + (a.Y * b.Y));
        return new Point2(vertex.X + ((a.X + b.X) * scale), vertex.Y + ((a.Y + b.Y) * scale));
    }

    private static (double X, double Y) InwardNormal(Point2 from, Point2 to)
    {
        double length = from.DistanceTo(to);
        return (-(to.Y - from.Y) / length, (to.X - from.X) / length);
    }

    private static Result<IReadOnlyList<TargetZone>> Fail(string code, string message) =>
        Result.Failure<IReadOnlyList<TargetZone>>(Diagnostic.Error(code, message));
}
```

- [x] **Step 4: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: `Passed!  - Failed:     0, Passed:    10, Skipped:     0, Total:    10` for `net8.0`.

- [x] **Step 5: Run the whole integration suite**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    19, Skipped:     0, Total:    19` for `net8.0`.

- [x] **Step 6: Full file after this task: `src/Lod.Core/Simplification/Strategies.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Simplification;

/// <summary>
/// Z1: merges zones of the same space type that are connected through shared walls. Each connected group becomes one zone.
/// </summary>
public sealed class SemanticMerge : PlanSimplifier
{
    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SemanticMerge(ToleranceSettings tolerances)
        : base(tolerances)
    {
    }

    /// <inheritdoc />
    public override string Name => nameof(SemanticMerge);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        Dictionary<ZoneId, Zone> byId = plan.Zones.ToDictionary(z => z.Id);
        ILookup<ZoneId, ZoneId> neighbours = plan.Surfaces
            .Where(s => s.Boundary == BoundaryCondition.Interzone)
            .ToLookup(s => s.Zone, s => s.AdjacentZone!.Value);
        var ops = new PolygonOps(Tolerances);
        var visited = new HashSet<ZoneId>();
        var targets = new List<TargetZone>();
        var counters = new Dictionary<SpaceType, int>();
        foreach (Zone seed in plan.Zones.Where(z => !visited.Contains(z.Id)))
        {
            var group = new List<Zone>();
            var queue = new Queue<Zone>(new[] { seed });
            visited.Add(seed.Id);
            while (queue.Count > 0)
            {
                Zone current = queue.Dequeue();
                group.Add(current);
                foreach (ZoneId next in neighbours[current.Id].Where(n => !visited.Contains(n) && byId[n].SpaceType == seed.SpaceType))
                {
                    visited.Add(next);
                    queue.Enqueue(byId[next]);
                }
            }

            IReadOnlyList<Polygon2> union = ops.Union(group.Select(z => z.Parts[0].Footprint));
            if (union.Count != 1)
            {
                return Result.Failure<IReadOnlyList<TargetZone>>(Diagnostic.Error(
                    DiagnosticCodes.DisconnectedGroup,
                    $"Merged group {string.Join(",", group.Select(z => z.Id.Value))} is not one polygon.",
                    seed.Id.Value));
            }

            int number = counters.TryGetValue(seed.SpaceType, out int n) ? n + 1 : 1;
            counters[seed.SpaceType] = number;
            targets.Add(new TargetZone(new ZoneId($"{seed.SpaceType}-{number}"), $"{seed.SpaceType} {number}", seed.SpaceType, union[0]));
        }

        return Result.Success<IReadOnlyList<TargetZone>>(targets);
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() => Enumerable.Empty<KeyValuePair<string, string>>();
}

/// <summary>
/// Z2: perimeter zones of a configurable depth plus a core (ADR-008). Each footprint edge owns the trapezoid between the edge and its inward
/// mitred offset, so corners are split along the bisectors; trapezoids in the same orientation bin are merged. Footprints with holes are not supported yet.
/// </summary>
public sealed class PerimeterCore : PlanSimplifier
{
    private readonly double _depth;

    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    /// <param name="perimeterDepth">Perimeter zone depth, m.</param>
    public PerimeterCore(ToleranceSettings tolerances, double perimeterDepth)
        : base(tolerances)
    {
        _depth = perimeterDepth;
    }

    /// <inheritdoc />
    public override string Name => nameof(PerimeterCore);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        if (!(_depth > 0) || double.IsInfinity(_depth))
        {
            return Fail(DiagnosticCodes.InvalidParameter, $"Perimeter depth must be positive, got {_depth}.");
        }

        if (plan.Footprint.Holes.Count > 0)
        {
            return Fail(DiagnosticCodes.NotSupported, "Perimeter/core of footprints with holes is not supported yet (S8, typologies).");
        }

        IReadOnlyList<Point2> v = plan.Footprint.Outer;
        int n = v.Count;
        Point2[] offset = Enumerable.Range(0, n).Select(i => Mitre(v[(i + n - 1) % n], v[i], v[(i + 1) % n])).ToArray();
        Result<Polygon2> core = Polygon2.Create(offset);
        bool keepsDirections = Enumerable.Range(0, n).All(i =>
        {
            Point2 a = v[i];
            Point2 b = v[(i + 1) % n];
            Point2 c = offset[i];
            Point2 d = offset[(i + 1) % n];
            return ((b.X - a.X) * (d.X - c.X)) + ((b.Y - a.Y) * (d.Y - c.Y)) > 0;
        });
        if (!core.IsSuccess || !keepsDirections || Polygon2.SignedArea(offset) <= 0)
        {
            return Fail(DiagnosticCodes.PlanTooNarrow, $"Perimeter depth {_depth} m leaves no valid core for this footprint.");
        }

        var ops = new PolygonOps(Tolerances);
        var trapezoids = new List<(OrientationBin Bin, Polygon2 Shape)>();
        for (int i = 0; i < n; i++)
        {
            Polygon2 shape = Polygon2.Create(new[] { v[i], v[(i + 1) % n], offset[(i + 1) % n], offset[i] }).Value;
            trapezoids.Add((Orientation.Bin(Orientation.OutwardAzimuth(v[i], v[(i + 1) % n]) + plan.OrientationDegrees), shape));
        }

        double tiled = trapezoids.Sum(t => t.Shape.Area) + core.Value.Area;
        if (!Tolerances.AreaEquals(plan.Footprint.Area, tiled))
        {
            return Fail(DiagnosticCodes.PlanTooNarrow, $"Perimeter zones and core cover {tiled:0.###} m² of a {plan.Footprint.Area:0.###} m² footprint.");
        }

        var targets = new List<TargetZone>();
        foreach (IGrouping<OrientationBin, (OrientationBin Bin, Polygon2 Shape)> bin in trapezoids.GroupBy(t => t.Bin).OrderBy(g => g.Key))
        {
            IReadOnlyList<Polygon2> merged = ops.Union(bin.Select(t => t.Shape));
            for (int k = 0; k < merged.Count; k++)
            {
                string suffix = merged.Count == 1 ? string.Empty : $"-{k + 1}";
                targets.Add(new TargetZone(new ZoneId($"P-{bin.Key}{suffix}"), $"Perimeter {bin.Key}{suffix}", SpaceType.Mixed, merged[k]));
            }
        }

        targets.Add(new TargetZone(new ZoneId("CORE"), "Core", SpaceType.Mixed, core.Value));
        return Result.Success<IReadOnlyList<TargetZone>>(targets);
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() =>
        new[] { new KeyValuePair<string, string>("PerimeterDepth", Provenance.Format(_depth)) };

    private Point2 Mitre(Point2 previous, Point2 vertex, Point2 next)
    {
        (double X, double Y) a = InwardNormal(previous, vertex);
        (double X, double Y) b = InwardNormal(vertex, next);
        double scale = _depth / (1.0 + (a.X * b.X) + (a.Y * b.Y));
        return new Point2(vertex.X + ((a.X + b.X) * scale), vertex.Y + ((a.Y + b.Y) * scale));
    }

    private static (double X, double Y) InwardNormal(Point2 from, Point2 to)
    {
        double length = from.DistanceTo(to);
        return (-(to.Y - from.Y) / length, (to.X - from.X) / length);
    }

    private static Result<IReadOnlyList<TargetZone>> Fail(string code, string message) =>
        Result.Failure<IReadOnlyList<TargetZone>>(Diagnostic.Error(code, message));
}

/// <summary>Z3: the whole floor as one zone.</summary>
public sealed class SingleZonePerFloor : PlanSimplifier
{
    /// <summary>Creates the simplifier.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public SingleZonePerFloor(ToleranceSettings tolerances)
        : base(tolerances)
    {
    }

    /// <inheritdoc />
    public override string Name => nameof(SingleZonePerFloor);

    /// <inheritdoc />
    protected override Result<IReadOnlyList<TargetZone>> ProposeZones(IGeneratedPlan plan)
    {
        SpaceType[] types = plan.Zones.Select(z => z.SpaceType).Distinct().ToArray();
        SpaceType type = types.Length == 1 ? types[0] : SpaceType.Mixed;
        return Result.Success<IReadOnlyList<TargetZone>>(new[] { new TargetZone(new ZoneId("FLOOR"), "Floor", type, plan.Footprint) });
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe() => Enumerable.Empty<KeyValuePair<string, string>>();
}
```

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Simplification/Strategies.cs tests/Lod.Integration.Tests/SimplifierTests.cs
git commit -m "feature(rezoning): add perimeter/core simplifier with bisector corners"
```

- [x] **Step 8: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/simplifiers
git push origin main
git branch -d feature/simplifiers
```

Expected from `verify.ps1`: 104 core, 17 generators, 19 integration tests passed on `net8.0`, then `VERIFY PASSED`.

---

## Slice D — `feature/validation-invariants`

### Task 8: Floor and building validation

**Files:**
- Create: `src/Lod.Core/Validation/Totals.cs`
- Create: `src/Lod.Core/Validation/Validators.cs`
- Test: `tests/Lod.Integration.Tests/SimplifierTests.cs` (add five test methods, one `using`, two helpers)

**Interfaces:**
- Consumes: `IFloor` (`Source`, `Zones`, `Surfaces`, `Mapping`, `Footprint`, `OrientationDegrees`), `IGeneratedBuilding` (`Sources`, `Zones`, `Surfaces`, `OrientationDegrees`), `FloorEntry`, `Stack.Aggregate`, `Zone.Multiplier`, `HorizontalSurface`, `HorizontalKind`, `TextReport.F`, `LayoutMeasures.Of` (S2); `DesignMagnitudes.Occupants`, `DesignMagnitudes.Of`, `ZoneProgram.IsConditioned`, `ZoneProgram.Thermostat`, `AggregationRecord` via `LoadDefinition.Aggregation` and `Schedule.Aggregation` (S1); `ToleranceSettings.AreaEquals`, `.LoadEquals`, `.RelativeArea`, `.Distance`; `FacadeAttribution.CoverageGaps` (Task 2); the three strategies (Tasks 5–7); `LinearPlanParameters` (S2).
- Produces:
  - `public sealed class Totals { public double FloorArea { get; } public double Volume { get; } public double ConditionedFloorArea { get; } public double ExteriorWallArea { get; } public double Glazing { get; } public IReadOnlyDictionary<OrientationBin, double> GlazingByOrientation { get; } public double GroundArea { get; } public double RoofArea { get; } public double ExposedFloorArea { get; } public double Height { get; } public IReadOnlyDictionary<LoadType, double> Magnitude { get; } public IReadOnlyDictionary<LoadType, double[]> Scheduled { get; } public static Totals Of(IEnumerable<Zone> zones, IReadOnlyList<Surface> surfaces, double orientationDegrees); }` (setters private)
  - `public sealed record CheckResult(string Check, bool Passed, string Detail, bool Enforced = true);`
  - `public sealed class ValidationReport { public ValidationReport(IEnumerable<CheckResult> checks); public IReadOnlyList<CheckResult> Checks { get; } public bool Passed { get; } public string Describe(); }`
  - `public sealed class FloorValidator { public FloorValidator(ToleranceSettings tolerances); public ValidationReport Validate(IFloor floor); }`
  - `public sealed class BuildingValidator { public BuildingValidator(ToleranceSettings tolerances); public ValidationReport Validate(IGeneratedBuilding building); }`
  - `internal static class Conservation { public static IEnumerable<CheckResult> Compare(Totals expected, Totals actual, ToleranceSettings tolerances); }`

**Every check.** `Totals` sums over zones and surfaces with zone multipliers. `ValidationReport.Passed` is true when every *enforced* check passed. Relative comparisons are `|a − b| ≤ tol × max(1, |a|, |b|)` (ADR-004).

| Check | Compares (reference → actual) | Tolerance | Enforced |
| --- | --- | --- | --- |
| `FloorArea` | Σ multiplier × zone floor area | RelativeArea | yes |
| `Volume` | Σ multiplier × zone volume | RelativeArea | yes |
| `ConditionedFloorArea` | Σ multiplier × floor area of conditioned zones | RelativeArea | no, reported only (D-038) |
| `ExteriorWallArea` | Σ multiplier × gross area of `Outdoors` walls, windows included | RelativeArea | yes |
| `Glazing` | Σ multiplier × glazed area of `Outdoors` walls | RelativeArea | yes |
| `Glazing.<Bin>` | the same per North/East/South/West bin of the wall's true azimuth; one check per bin present in either total | RelativeArea | yes |
| `Installed.<LoadType>` | design magnitude per load type, summed over all its bases (people, W, m³/h; ADR-007, D-047); one check per load type present in either total, so occupancy and air volume flow (infiltration, ventilation, hot water) are covered here | RelativeLoad | yes |
| `Scheduled.<LoadType>` | magnitude × schedule fraction for each of the 8760 hours; every hour must agree; the detail names the worst hour | RelativeLoad per hour | yes |
| `FacadeCoverage` (floor only) | every source outdoor wall is covered over its full length by target outdoor walls, before any normalisation (`CoverageGaps`, D-041) | RelativeArea on lengths | yes |
| `NoTargetOverlap` (floor only) | Σ pairwise intersection area of the target zones | ≤ RelativeArea × footprint area | yes |
| `SourceCoverage` (floor only) | each source zone's floor area vs the sum of its mapping overlaps | RelativeArea | yes |
| `Traceability` (floor only) | every target zone has a mapping row; an identity zone (no `SourceZones`) needs an identity row with source fraction 1; a derived zone needs aggregation records on every load value and load schedule and, if it is conditioned, on both setpoint schedules | exact | yes |
| `Building.Reference` | the fully stacked reference could not be built (only on failure) | — | yes |
| `Building.GroundArea` | ground-contact floor area vs the stacked reference | RelativeArea | yes (D-046) |
| `Building.RoofArea` | outdoor ceiling area vs the stacked reference | RelativeArea | yes (D-046) |
| `Building.ExposedFloorArea` | area of floors facing `Outdoors` (overhangs) vs the stacked reference, so exposure is never multiplied | RelativeArea | yes (D-046) |
| `Building.Height` | elevation of the highest zone top vs the stacked reference, so representative storeys sit at their true elevations | Distance (absolute) | yes (D-045) |

`FloorValidator` compares a floor with its source plan (`IFloor.Source`). `BuildingValidator` validates each distinct source floor (check names prefixed `Floor0.`, `Floor1.`, …), then compares the building with `Stack.Aggregate(building.Sources)`, the fully stacked reference built from the same floor entries (check names prefixed `Building.`, including `Building.ConditionedFloorArea`, reported only). Setpoints are not compared: they are a prescribed control rule (D-038), not an invariant.

- [x] **Step 1: Write the failing validation tests**

In `SimplifierTests`:

1. Add `using Lod.Core.Validation;` after `using Lod.Core.Simplification;`.
2. Insert these tests after `SetpointsAreFloorAreaWeightedAndRecorded`, with one blank line before them:

```csharp
    [Theory]
    [InlineData("SemanticMerge", 1)]
    [InlineData("SemanticMerge", 2)]
    [InlineData("SemanticMerge", 3)]
    [InlineData("PerimeterCore", 1)]
    [InlineData("PerimeterCore", 2)]
    [InlineData("PerimeterCore", 3)]
    [InlineData("PerimeterCore", 4)]
    [InlineData("SingleZonePerFloor", 1)]
    [InlineData("SingleZonePerFloor", 2)]
    public void EverySimplifierSatisfiesTheInvariantsForRandomPlans(string simplifier, int seed)
    {
        LinearPlanParameters parameters = RandomParameters(new Random(seed));

        IFloor floor = Simplifier(simplifier).Simplify(Pipeline.Plan(parameters)).Value;
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(floor);

        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported()
    {
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances)));

        CheckResult conditioned = report.Checks.Single(c => c.Check == "ConditionedFloorArea");
        Assert.False(conditioned.Passed);
        Assert.False(conditioned.Enforced);
        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void ValidationCatchesAnUncoveredFacade()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Surface[] withoutSouthWall = floor.Surfaces.Where(s => !(s is WallSurface w && w.Start.Y == 0.0 && w.End.Y == 0.0)).ToArray();
        var broken = new Floor(floor.Source, floor.Zones, withoutSouthWall, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.Contains(report.Checks, c => c.Check == "FacadeCoverage" && !c.Passed && c.Enforced);
        Assert.False(report.Passed);
    }

    [Fact]
    public void NoSimplificationPassesValidation()
    {
        Assert.True(new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.DetailedFloor()).Passed);
    }

    [Fact]
    public void ValidationCatchesAChangedProgram()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Zone zone = floor.Zones[0];
        var tampered = new Zone(zone.Id, zone.Name, zone.SpaceType, zone.Parts, ExampleResidentialPresets.DwellingUnit.Program, zone.SourceZones);
        var broken = new Floor(floor.Source, new[] { tampered }, floor.Surfaces, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.False(report.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Installed.Lighting" && !c.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Traceability" && !c.Passed);
    }
```

3. Insert these helpers after the nested `ToleranceComparer` class and before the class's closing brace, with one blank line before them:

```csharp
    private static IPlanSimplifier Simplifier(string name) => name switch
    {
        "SemanticMerge" => new SemanticMerge(Pipeline.Tolerances),
        "PerimeterCore" => new PerimeterCore(Pipeline.Tolerances, PerimeterDepth),
        "SingleZonePerFloor" => new SingleZonePerFloor(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown simplifier."),
    };

    private static LinearPlanParameters RandomParameters(Random random) => new(
        Length: 18.0 + (random.NextDouble() * 42.0),
        UnitDepth: 6.0 + (random.NextDouble() * 4.0),
        CorridorWidth: 1.5 + (random.NextDouble() * 1.5),
        TargetUnitWidth: 5.0 + (random.NextDouble() * 7.0),
        StairLength: 3.0 + (random.NextDouble() * 3.0),
        FloorHeight: 2.8 + (random.NextDouble() * 0.7),
        OrientationDegrees: random.NextDouble() * 360.0);
```

The theory draws plans from `new Random(seed)` with explicit seeds (length 18–60 m, unit depth 6–10 m, corridor 1.5–3 m, unit width 5–12 m, stair 3–6 m, storey height 2.8–3.5 m, any orientation), so it covers unit rows of several widths, rotated plans, and source zones split across several targets. The `PerimeterCore` cases use 4.57 m, which fits every drawn plan (minimum depth 2 × 6 + 1.5 = 13.5 m > 9.14 m). `MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported` shows the D-038 report: Z3 makes the whole 432 m² floor conditioned where the plan had 360 m² (432 m² minus the 72 m² stair), so `ConditionedFloorArea` fails but is not enforced and the report still passes. `ValidationCatchesAnUncoveredFacade` removes the south wall from a Z3 floor, so the enforced `FacadeCoverage` check fails. `ValidationCatchesAChangedProgram` replaces the Z3 program with the dwelling-unit preset: the installed lighting changes and the zone loses its aggregation records, so both `Installed.Lighting` and `Traceability` fail.

- [x] **Step 2: Run the tests and watch them fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: the build fails with

```text
tests\Lod.Integration.Tests\SimplifierTests.cs(10,16): error CS0234: The type or namespace name 'Validation' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
```

- [x] **Step 3: Implement the totals**

Create `src/Lod.Core/Validation/Totals.cs`:

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Schedules;

namespace Lod.Core.Validation;

/// <summary>
/// Extensive totals of a set of zones and surfaces, counting zone multipliers: the quantities the conservation checks compare.
/// </summary>
public sealed class Totals
{
    private Totals()
    {
    }

    /// <summary>Floor area, m².</summary>
    public double FloorArea { get; private set; }

    /// <summary>Volume, m³.</summary>
    public double Volume { get; private set; }

    /// <summary>Floor area of conditioned zones, m² (D-038).</summary>
    public double ConditionedFloorArea { get; private set; }

    /// <summary>Gross outdoor wall area, m².</summary>
    public double ExteriorWallArea { get; private set; }

    /// <summary>Glazed area, m².</summary>
    public double Glazing { get; private set; }

    /// <summary>Glazed area per orientation bin, m².</summary>
    public IReadOnlyDictionary<OrientationBin, double> GlazingByOrientation { get; private set; } = new Dictionary<OrientationBin, double>();

    /// <summary>Area of floors on the ground, m².</summary>
    public double GroundArea { get; private set; }

    /// <summary>Area of ceilings facing outdoors (roofs), m².</summary>
    public double RoofArea { get; private set; }

    /// <summary>Area of floors facing outdoors (overhangs), m².</summary>
    public double ExposedFloorArea { get; private set; }

    /// <summary>Elevation of the highest zone top, m: the building height when the lowest storey starts at 0.</summary>
    public double Height { get; private set; }

    /// <summary>Design magnitude per load type: people, W, or m³/h.</summary>
    public IReadOnlyDictionary<LoadType, double> Magnitude { get; private set; } = new Dictionary<LoadType, double>();

    /// <summary>Scheduled magnitude per load type and hour.</summary>
    public IReadOnlyDictionary<LoadType, double[]> Scheduled { get; private set; } = new Dictionary<LoadType, double[]>();

    /// <summary>Computes the totals.</summary>
    /// <param name="zones">Zones.</param>
    /// <param name="surfaces">Surfaces of the zones.</param>
    /// <param name="orientationDegrees">Orientation used to bin glazing.</param>
    /// <returns>The totals.</returns>
    public static Totals Of(IEnumerable<Zone> zones, IReadOnlyList<Surface> surfaces, double orientationDegrees)
    {
        Zone[] zoneArray = zones.ToArray();
        Dictionary<Common.ZoneId, int> multiplier = zoneArray.ToDictionary(z => z.Id, z => z.Multiplier);
        int M(Surface s) => multiplier.TryGetValue(s.Zone, out int m) ? m : 1;
        WallSurface[] outdoorWalls = surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors).ToArray();
        var magnitude = new Dictionary<LoadType, double>();
        var scheduled = new Dictionary<LoadType, double[]>();
        foreach (Zone zone in zoneArray)
        {
            ZoneMeasures measures = LayoutMeasures.Of(zone, surfaces);
            double occupants = DesignMagnitudes.Occupants(zone.Program, measures);
            foreach (LoadDefinition load in zone.Program.Loads)
            {
                double q = zone.Multiplier * DesignMagnitudes.Of(load, measures, occupants);
                magnitude[load.Type] = (magnitude.TryGetValue(load.Type, out double sum) ? sum : 0.0) + q;
                if (!scheduled.TryGetValue(load.Type, out double[]? hours))
                {
                    hours = new double[Schedule.HoursPerYear];
                    scheduled[load.Type] = hours;
                }

                for (int h = 0; h < hours.Length; h++)
                {
                    hours[h] += q * load.Schedule[h];
                }
            }
        }

        return new Totals
        {
            FloorArea = zoneArray.Sum(z => z.Multiplier * z.FloorArea),
            Volume = zoneArray.Sum(z => z.Multiplier * z.Volume),
            ConditionedFloorArea = zoneArray.Where(z => z.Program.IsConditioned).Sum(z => z.Multiplier * z.FloorArea),
            ExteriorWallArea = outdoorWalls.Sum(w => M(w) * w.Area),
            Glazing = outdoorWalls.Sum(w => M(w) * w.GlazedArea),
            GlazingByOrientation = outdoorWalls
                .GroupBy(w => Orientation.Bin(w.PlanAzimuth + orientationDegrees))
                .ToDictionary(g => g.Key, g => g.Sum(w => M(w) * w.GlazedArea)),
            GroundArea = surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary == BoundaryCondition.Ground).Sum(h => M(h) * h.Area),
            RoofArea = surfaces.OfType<HorizontalSurface>().Where(h => h.Kind == HorizontalKind.Ceiling && h.Boundary == BoundaryCondition.Outdoors).Sum(h => M(h) * h.Area),
            ExposedFloorArea = surfaces.OfType<HorizontalSurface>().Where(h => h.Kind == HorizontalKind.Floor && h.Boundary == BoundaryCondition.Outdoors).Sum(h => M(h) * h.Area),
            Height = zoneArray.SelectMany(z => z.Parts).Select(p => p.Elevation + p.Height).DefaultIfEmpty(0.0).Max(),
            Magnitude = magnitude,
            Scheduled = scheduled,
        };
    }
}
```

- [x] **Step 4: Implement the validators**

Create `src/Lod.Core/Validation/Validators.cs`:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Schedules;
using Lod.Core.Simplification;

namespace Lod.Core.Validation;

/// <summary>Outcome of one check.</summary>
/// <param name="Check">Check name.</param>
/// <param name="Passed">Whether the check passed.</param>
/// <param name="Detail">Reference and actual values.</param>
/// <param name="Enforced">Whether a failure blocks conversion; reported-only checks never do (e.g. conditioned floor area, D-038).</param>
public sealed record CheckResult(string Check, bool Passed, string Detail, bool Enforced = true);

/// <summary>Result of validating a floor or building against its prescribed conservation invariants.</summary>
public sealed class ValidationReport
{
    /// <summary>Creates a report.</summary>
    /// <param name="checks">Check results.</param>
    public ValidationReport(IEnumerable<CheckResult> checks)
    {
        Checks = Array.AsReadOnly(checks.ToArray());
    }

    /// <summary>All check results.</summary>
    public IReadOnlyList<CheckResult> Checks { get; }

    /// <summary>Whether every enforced check passed.</summary>
    public bool Passed => Checks.All(c => c.Passed || !c.Enforced);

    /// <summary>One line per check.</summary>
    /// <returns>The text.</returns>
    public string Describe()
    {
        var builder = new StringBuilder();
        builder.Append(Passed ? "PASSED" : "FAILED").Append('\n');
        foreach (CheckResult check in Checks)
        {
            builder.Append(check.Passed ? "  ok   " : check.Enforced ? "  FAIL " : "  note ")
                .Append(check.Check).Append(": ").Append(check.Detail).Append('\n');
        }

        return builder.ToString();
    }
}

/// <summary>
/// Checks a floor against its source plan: the prescribed conservation invariants (area, volume, exterior wall area, installed and hourly
/// scheduled magnitude per load type, glazing in total and per orientation), façade coverage (D-041), tiling, and traceability. Setpoints are a
/// prescribed rule (D-038), not an invariant, and are not compared; the change in conditioned floor area is reported, not enforced.
/// </summary>
public sealed class FloorValidator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the validator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public FloorValidator(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <summary>Validates a floor.</summary>
    /// <param name="floor">The floor.</param>
    /// <returns>The report.</returns>
    public ValidationReport Validate(IFloor floor)
    {
        var checks = new List<CheckResult>();
        Totals source = Totals.Of(floor.Source.Zones, floor.Source.Surfaces, floor.OrientationDegrees);
        Totals target = Totals.Of(floor.Zones, floor.Surfaces, floor.OrientationDegrees);
        checks.AddRange(Conservation.Compare(source, target, _tolerances));
        checks.Add(FacadeCoverage(floor));
        checks.Add(NoOverlap(floor));
        checks.Add(Coverage(floor));
        checks.Add(Traceability(floor));
        return new ValidationReport(checks);
    }

    private CheckResult FacadeCoverage(IFloor floor)
    {
        string[] gaps = FacadeAttribution.Compute(floor.Source.Surfaces, floor.Surfaces, _tolerances)
            .CoverageGaps()
            .Select(g => $"{g.Wall.Id.Value} {TextReport.F(g.CoveredLength)} of {TextReport.F(g.Wall.Length)} m")
            .ToArray();
        return new CheckResult("FacadeCoverage", gaps.Length == 0, gaps.Length == 0 ? "every source façade fully covered" : $"partly covered: {string.Join("; ", gaps)}");
    }

    private CheckResult NoOverlap(IFloor floor)
    {
        var ops = new PolygonOps(_tolerances);
        double overlap = 0.0;
        for (int i = 0; i < floor.Zones.Count; i++)
        {
            for (int j = i + 1; j < floor.Zones.Count; j++)
            {
                overlap += ops.IntersectionArea(floor.Zones[i].Parts[0].Footprint, floor.Zones[j].Parts[0].Footprint);
            }
        }

        bool passed = overlap <= _tolerances.RelativeArea * floor.Footprint.Area;
        return new CheckResult("NoTargetOverlap", passed, $"pairwise overlap {TextReport.F(overlap)} m²");
    }

    private CheckResult Coverage(IFloor floor)
    {
        string[] uncovered = floor.Source.Zones
            .Where(s => !_tolerances.AreaEquals(s.FloorArea, floor.Mapping.Where(m => m.Source == s.Id).Sum(m => m.OverlapArea)))
            .Select(s => s.Id.Value)
            .ToArray();
        return new CheckResult("SourceCoverage", uncovered.Length == 0, uncovered.Length == 0 ? "every source fully mapped" : $"not fully mapped: {string.Join(",", uncovered)}");
    }

    private static CheckResult Traceability(IFloor floor)
    {
        var problems = new List<string>();
        foreach (Zone zone in floor.Zones)
        {
            if (!floor.Mapping.Any(m => m.Target == zone.Id))
            {
                problems.Add($"{zone.Id.Value} has no source");
                continue;
            }

            bool identity = zone.SourceZones.Count == 0 && floor.Mapping.Any(m => m.Target == zone.Id && m.Source == zone.Id && m.SourceFraction == 1.0);
            bool derived = zone.SourceZones.Count > 0
                && zone.Program.Loads.All(l => l.Aggregation is not null && l.Schedule.Aggregation is not null)
                && (zone.Program.Thermostat is null
                    || (zone.Program.Thermostat.HeatingSetpoint.Aggregation is not null && zone.Program.Thermostat.CoolingSetpoint.Aggregation is not null));
            if (!identity && !derived)
            {
                problems.Add($"{zone.Id.Value} lacks aggregation records");
            }
        }

        return new CheckResult("Traceability", problems.Count == 0, problems.Count == 0 ? "every zone traceable to its sources" : string.Join("; ", problems));
    }
}

/// <summary>
/// Checks a building: every source floor against its plan, then the building against the fully stacked reference built from the same floor
/// entries, including ground, roof, and exposed floor area and the building height (D-045, D-046).
/// </summary>
public sealed class BuildingValidator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the validator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public BuildingValidator(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <summary>Validates a building.</summary>
    /// <param name="building">The building.</param>
    /// <returns>The report.</returns>
    public ValidationReport Validate(IGeneratedBuilding building)
    {
        var checks = new List<CheckResult>();
        var floorValidator = new FloorValidator(_tolerances);
        int index = 0;
        foreach (IFloor floor in building.Sources.Select(e => e.Floor).Distinct())
        {
            checks.AddRange(floorValidator.Validate(floor).Checks.Select(c => c with { Check = $"Floor{index}.{c.Check}" }));
            index++;
        }

        Result<IGeneratedBuilding> reference = new Stack(_tolerances).Aggregate(building.Sources);
        if (!reference.IsSuccess)
        {
            checks.Add(new CheckResult("Building.Reference", false, string.Join("; ", reference.Diagnostics)));
            return new ValidationReport(checks);
        }

        Totals expected = Totals.Of(reference.Value.Zones, reference.Value.Surfaces, building.OrientationDegrees);
        Totals actual = Totals.Of(building.Zones, building.Surfaces, building.OrientationDegrees);
        checks.AddRange(Conservation.Compare(expected, actual, _tolerances).Select(c => c with { Check = $"Building.{c.Check}" }));
        checks.Add(new CheckResult("Building.GroundArea", _tolerances.AreaEquals(expected.GroundArea, actual.GroundArea), Pair(expected.GroundArea, actual.GroundArea)));
        checks.Add(new CheckResult("Building.RoofArea", _tolerances.AreaEquals(expected.RoofArea, actual.RoofArea), Pair(expected.RoofArea, actual.RoofArea)));
        checks.Add(new CheckResult("Building.ExposedFloorArea", _tolerances.AreaEquals(expected.ExposedFloorArea, actual.ExposedFloorArea), Pair(expected.ExposedFloorArea, actual.ExposedFloorArea)));
        checks.Add(new CheckResult("Building.Height", Math.Abs(expected.Height - actual.Height) <= _tolerances.Distance, Pair(expected.Height, actual.Height)));
        return new ValidationReport(checks);
    }

    private static string Pair(double expected, double actual) => $"reference {TextReport.F(expected)}, actual {TextReport.F(actual)}";
}

/// <summary>Comparisons shared by floor and building validation.</summary>
internal static class Conservation
{
    public static IEnumerable<CheckResult> Compare(Totals expected, Totals actual, ToleranceSettings tolerances)
    {
        yield return Area("FloorArea", expected.FloorArea, actual.FloorArea, tolerances);
        yield return Area("Volume", expected.Volume, actual.Volume, tolerances);
        yield return Area("ConditionedFloorArea", expected.ConditionedFloorArea, actual.ConditionedFloorArea, tolerances) with { Enforced = false };
        yield return Area("ExteriorWallArea", expected.ExteriorWallArea, actual.ExteriorWallArea, tolerances);
        yield return Area("Glazing", expected.Glazing, actual.Glazing, tolerances);
        foreach (OrientationBin bin in expected.GlazingByOrientation.Keys.Union(actual.GlazingByOrientation.Keys).OrderBy(b => b))
        {
            yield return Area($"Glazing.{bin}", Get(expected.GlazingByOrientation, bin), Get(actual.GlazingByOrientation, bin), tolerances);
        }

        foreach (LoadType type in expected.Magnitude.Keys.Union(actual.Magnitude.Keys).OrderBy(t => t))
        {
            double e = Get(expected.Magnitude, type);
            double a = Get(actual.Magnitude, type);
            yield return new CheckResult($"Installed.{type}", tolerances.LoadEquals(e, a), Pair(e, a));
            yield return Hourly(type, expected, actual, tolerances);
        }
    }

    private static CheckResult Hourly(LoadType type, Totals expected, Totals actual, ToleranceSettings tolerances)
    {
        double[] e = expected.Scheduled.TryGetValue(type, out double[]? x) ? x : new double[Schedule.HoursPerYear];
        double[] a = actual.Scheduled.TryGetValue(type, out double[]? y) ? y : new double[Schedule.HoursPerYear];
        int worst = Enumerable.Range(0, Schedule.HoursPerYear).OrderByDescending(h => Math.Abs(e[h] - a[h])).First();
        bool passed = Enumerable.Range(0, Schedule.HoursPerYear).All(h => tolerances.LoadEquals(e[h], a[h]));
        return new CheckResult($"Scheduled.{type}", passed, $"worst hour {worst}: {Pair(e[worst], a[worst])}");
    }

    private static CheckResult Area(string name, double expected, double actual, ToleranceSettings tolerances) =>
        new(name, tolerances.AreaEquals(expected, actual), Pair(expected, actual));

    private static double Get<TKey>(IReadOnlyDictionary<TKey, double> values, TKey key) => values.TryGetValue(key, out double v) ? v : 0.0;

    private static string Pair(double expected, double actual) => $"reference {TextReport.F(expected)}, actual {TextReport.F(actual)}";
}
```

- [x] **Step 5: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected: `Passed!  - Failed:     0, Passed:    23, Skipped:     0, Total:    23` for `net8.0`.

- [x] **Step 6: Run the whole integration suite**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    32, Skipped:     0, Total:    32` for `net8.0`.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Validation/Totals.cs src/Lod.Core/Validation/Validators.cs tests/Lod.Integration.Tests/SimplifierTests.cs
git commit -m "feature(validation): check floors and buildings against conservation invariants"
```

### Task 9: Determinism and canonical snapshots

**Files:**
- Test: `tests/Lod.Integration.Tests/SimplifierTests.cs` (add two theories)
- Create: `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt`
- Create: `tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt`
- Create: `tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt`

**Interfaces:**
- Consumes: `TextReport.Describe(IFloorLayout)` (S2), `Snapshot.Match(string actual, string name)` (S2, `tests/Shared/Snapshot.cs`), the `Simplifier` helper (Task 8).
- Produces: the three accepted snapshots; the final `SimplifierTests.cs` (29 tests).

- [x] **Step 1: Write the determinism and snapshot tests**

Insert these theories after `ValidationCatchesAChangedProgram` and before the nested `ToleranceComparer` class, with one blank line on each side:

```csharp
    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void SimplifiersAreDeterministic(string simplifier)
    {
        Assert.Equal(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))));
    }

    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void CanonicalSnapshots(string simplifier)
    {
        Snapshot.Match(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), $"simplifier-{simplifier}");
    }
```

- [x] **Step 2: Run the tests: determinism passes, snapshots fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release --filter "FullyQualifiedName~Lod.Integration.Tests.SimplifierTests"
```

Expected, for `net8.0`: the three `SimplifiersAreDeterministic` cases pass at once (determinism is a property of Tasks 5–7; these tests guard it), and the three snapshot cases fail:

```text
  Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "SemanticMerge") [… ms]
   Snapshot 'simplifier-SemanticMerge' is missing or differs. Review Snapshots/simplifier-SemanticMerge.received.txt and rename it to simplifier-SemanticMerge.txt to accept.
  Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "PerimeterCore") [… ms]
   Snapshot 'simplifier-PerimeterCore' is missing or differs. Review Snapshots/simplifier-PerimeterCore.received.txt and rename it to simplifier-PerimeterCore.txt to accept.
  Failed Lod.Integration.Tests.SimplifierTests.CanonicalSnapshots(simplifier: "SingleZonePerFloor") [… ms]
   Snapshot 'simplifier-SingleZonePerFloor' is missing or differs. Review Snapshots/simplifier-SingleZonePerFloor.received.txt and rename it to simplifier-SingleZonePerFloor.txt to accept.
Failed!  - Failed:     3, Passed:    26, Skipped:     0, Total:    29, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

The runs write `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.received.txt`, `simplifier-PerimeterCore.received.txt`, and `simplifier-SingleZonePerFloor.received.txt` (git-ignored by `*.received.*`).

- [x] **Step 3: Review and accept `simplifier-SemanticMerge`**

Review the received file against the expected content below; it must be identical. Then rename it:

```bash
mv tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt
```

Expected `tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone Stair-1 Stair "Stair 1" area=72.000000 volume=216.000000 parts=1 multiplier=1 sources=[ST]
  load Lighting PerFloorArea value=3.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  unconditioned
zone Corridor-1 Corridor "Corridor 1" area=40.000000 volume=120.000000 parts=1 multiplier=1 sources=[CO]
  load Lighting PerFloorArea value=5.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone DwellingUnit-1 DwellingUnit "DwellingUnit 1" area=160.000000 volume=480.000000 parts=1 multiplier=1 sources=[US1,US2]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone DwellingUnit-2 DwellingUnit "DwellingUnit 2" area=160.000000 volume=480.000000 parts=1 multiplier=1 sources=[UN1,UN2]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface Stair-1/W1 Outdoors area=12.000000 wall (4.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface Stair-1/W2 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface Stair-1/W3 Outdoors area=12.000000 wall (0.000000,0.000000)-(4.000000,0.000000) z=0.000000 facing=South glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface Stair-1/W4 Interzone adjacent=DwellingUnit-1 area=24.000000 wall (4.000000,0.000000)-(4.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/W5 Interzone adjacent=Corridor-1 area=6.000000 wall (4.000000,8.000000)-(4.000000,10.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/W6 Interzone adjacent=DwellingUnit-2 area=24.000000 wall (4.000000,10.000000)-(4.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface Stair-1/F Unresolved area=72.000000 Floor z=0.000000
surface Stair-1/C Unresolved area=72.000000 Ceiling z=3.000000
surface Corridor-1/W1 Interzone adjacent=DwellingUnit-2 area=60.000000 wall (24.000000,10.000000)-(4.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface Corridor-1/W2 Interzone adjacent=Stair-1 area=6.000000 wall (4.000000,10.000000)-(4.000000,8.000000) z=0.000000 facing=West glazing=0.000000
surface Corridor-1/W3 Interzone adjacent=DwellingUnit-1 area=60.000000 wall (4.000000,8.000000)-(24.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface Corridor-1/W4 Outdoors area=6.000000 wall (24.000000,8.000000)-(24.000000,10.000000) z=0.000000 facing=East glazing=1.200000 window(offset=0.552786 sill=0.829180 0.894427x1.341641)
surface Corridor-1/F Unresolved area=40.000000 Floor z=0.000000
surface Corridor-1/C Unresolved area=40.000000 Ceiling z=3.000000
surface DwellingUnit-1/W1 Outdoors area=24.000000 wall (24.000000,0.000000)-(24.000000,8.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface DwellingUnit-1/W2 Interzone adjacent=Corridor-1 area=60.000000 wall (24.000000,8.000000)-(4.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface DwellingUnit-1/W3 Interzone adjacent=Stair-1 area=24.000000 wall (4.000000,8.000000)-(4.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface DwellingUnit-1/W4 Outdoors area=60.000000 wall (4.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=18.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168)
surface DwellingUnit-1/F Unresolved area=160.000000 Floor z=0.000000
surface DwellingUnit-1/C Unresolved area=160.000000 Ceiling z=3.000000
surface DwellingUnit-2/W1 Outdoors area=24.000000 wall (24.000000,10.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface DwellingUnit-2/W2 Outdoors area=60.000000 wall (24.000000,18.000000)-(4.000000,18.000000) z=0.000000 facing=North glazing=18.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168)
surface DwellingUnit-2/W3 Interzone adjacent=Stair-1 area=24.000000 wall (4.000000,18.000000)-(4.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface DwellingUnit-2/W4 Interzone adjacent=Corridor-1 area=60.000000 wall (4.000000,10.000000)-(24.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface DwellingUnit-2/F Unresolved area=160.000000 Floor z=0.000000
surface DwellingUnit-2/C Unresolved area=160.000000 Ceiling z=3.000000
```

- [x] **Step 4: Review and accept `simplifier-PerimeterCore`**

Review the received file against the expected content below; it must be identical. Then rename it:

```bash
mv tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt
```

Expected `tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone P-North Mixed "Perimeter North" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,UN1,UN2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-East Mixed "Perimeter East" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[CO,US2,UN2]
  load Occupancy PerFloorArea value=0.025532 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=3541.009233
  load ElectricEquipment PerFloorArea value=4.255398 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-South Mixed "Perimeter South" area=88.795100 volume=266.385300 parts=1 multiplier=1 sources=[ST,US1,US2]
  load Occupancy PerFloorArea value=0.027297 annual=6391.400000
  load Lighting PerFloorArea value=4.819810 annual=2971.681367
  load ElectricEquipment PerFloorArea value=4.549525 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone P-West Mixed "Perimeter West" area=61.375100 volume=184.125300 parts=1 multiplier=1 sources=[ST,CO,US1,UN1]
  load Occupancy PerFloorArea value=0.002070 annual=6391.400000
  load Lighting PerFloorArea value=3.175156 annual=8093.664821
  load ElectricEquipment PerFloorArea value=0.345018 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone CORE Mixed "Core" area=131.659600 volume=394.978800 parts=1 multiplier=1 sources=[CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.023228 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=4012.043792
  load ElectricEquipment PerFloorArea value=3.871332 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface P-North/W1 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface P-North/W2 Interzone adjacent=P-West area=19.388868 wall (0.000000,18.000000)-(4.570000,13.430000) z=0.000000 facing=West glazing=0.000000
surface P-North/W3 Interzone adjacent=CORE area=44.580000 wall (4.570000,13.430000)-(19.430000,13.430000) z=0.000000 facing=South glazing=0.000000
surface P-North/W4 Interzone adjacent=P-East area=19.388868 wall (19.430000,13.430000)-(24.000000,18.000000) z=0.000000 facing=South glazing=0.000000
surface P-North/F Unresolved area=88.795100 Floor z=0.000000
surface P-North/C Unresolved area=88.795100 Ceiling z=3.000000
surface P-East/W1 Interzone adjacent=P-North area=19.388868 wall (24.000000,18.000000)-(19.430000,13.430000) z=0.000000 facing=North glazing=0.000000
surface P-East/W2 Interzone adjacent=CORE area=26.580000 wall (19.430000,13.430000)-(19.430000,4.570000) z=0.000000 facing=West glazing=0.000000
surface P-East/W3 Interzone adjacent=P-South area=19.388868 wall (19.430000,4.570000)-(24.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface P-East/W4 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface P-East/F Unresolved area=61.375100 Floor z=0.000000
surface P-East/C Unresolved area=61.375100 Ceiling z=3.000000
surface P-South/W1 Interzone adjacent=CORE area=44.580000 wall (19.430000,4.570000)-(4.570000,4.570000) z=0.000000 facing=North glazing=0.000000
surface P-South/W2 Interzone adjacent=P-West area=19.388868 wall (4.570000,4.570000)-(0.000000,0.000000) z=0.000000 facing=North glazing=0.000000
surface P-South/W3 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
surface P-South/W4 Interzone adjacent=P-East area=19.388868 wall (24.000000,0.000000)-(19.430000,4.570000) z=0.000000 facing=North glazing=0.000000
surface P-South/F Unresolved area=88.795100 Floor z=0.000000
surface P-South/C Unresolved area=88.795100 Ceiling z=3.000000
surface P-West/W1 Interzone adjacent=CORE area=26.580000 wall (4.570000,4.570000)-(4.570000,13.430000) z=0.000000 facing=East glazing=0.000000
surface P-West/W2 Interzone adjacent=P-North area=19.388868 wall (4.570000,13.430000)-(0.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface P-West/W3 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface P-West/W4 Interzone adjacent=P-South area=19.388868 wall (0.000000,0.000000)-(4.570000,4.570000) z=0.000000 facing=South glazing=0.000000
surface P-West/F Unresolved area=61.375100 Floor z=0.000000
surface P-West/C Unresolved area=61.375100 Ceiling z=3.000000
surface CORE/W1 Interzone adjacent=P-South area=44.580000 wall (4.570000,4.570000)-(19.430000,4.570000) z=0.000000 facing=South glazing=0.000000
surface CORE/W2 Interzone adjacent=P-East area=26.580000 wall (19.430000,4.570000)-(19.430000,13.430000) z=0.000000 facing=East glazing=0.000000
surface CORE/W3 Interzone adjacent=P-North area=44.580000 wall (19.430000,13.430000)-(4.570000,13.430000) z=0.000000 facing=North glazing=0.000000
surface CORE/W4 Interzone adjacent=P-West area=26.580000 wall (4.570000,13.430000)-(4.570000,4.570000) z=0.000000 facing=West glazing=0.000000
surface CORE/F Unresolved area=131.659600 Floor z=0.000000
surface CORE/C Unresolved area=131.659600 Ceiling z=3.000000
```

- [x] **Step 5: Review and accept `simplifier-SingleZonePerFloor`**

Review the received file against the expected content below; it must be identical. Then rename it:

```bash
mv tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.received.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt
```

Expected `tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt`:

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone FLOOR Mixed "Floor" area=432.000000 volume=1296.000000 parts=1 multiplier=1 sources=[ST,CO,US1,US2,UN1,UN2]
  load Occupancy PerFloorArea value=0.022222 annual=6391.400000
  load Lighting PerFloorArea value=4.666667 annual=3893.174603
  load ElectricEquipment PerFloorArea value=3.703704 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface FLOOR/W1 Outdoors area=72.000000 wall (0.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=19.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 sill=0.678416 5.477226x1.643168)
surface FLOOR/W2 Outdoors area=54.000000 wall (24.000000,0.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=15.600000 window(offset=1.809110 sill=0.678416 4.381780x1.643168) window(offset=8.552786 sill=0.829180 0.894427x1.341641) window(offset=11.809110 sill=0.678416 4.381780x1.643168)
surface FLOOR/W3 Outdoors area=72.000000 wall (24.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=19.200000 window(offset=2.261387 sill=0.678416 5.477226x1.643168) window(offset=12.261387 sill=0.678416 5.477226x1.643168) window(offset=21.367544 sill=1.025658 1.264911x0.948683)
surface FLOOR/W4 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface FLOOR/F Unresolved area=432.000000 Floor z=0.000000
surface FLOOR/C Unresolved area=432.000000 Ceiling z=3.000000
```

- [x] **Step 6: Check a few snapshot values by hand**

Canonical plan: stair 4 m × 18 m (72 m², lighting 3 W/m², WWR 0.1, unconditioned), corridor 20 m × 2 m (40 m², lighting 5 W/m², WWR 0.2), four units 10 m × 8 m (80 m² each, 320 m² in total, lighting 5 W/m², occupancy 0.03 people/m², equipment 5 W/m², WWR 0.3), storey height 3 m, infiltration 0.3 ACH everywhere. These are the illustrative `ExampleResidentialPresets`, not DOE values. A generator window on a wall of length `L` and height `H` with ratio `r` is `L√r` wide and `H√r` high, centered.

| Value | Hand calculation | Snapshot |
| --- | --- | --- |
| P-South windows | stair wall 0–4 m: width 4√0.1 = 1.264911, offset (4 − 1.264911)/2 = 1.367544, height 3√0.1 = 0.948683, sill (3 − 0.948683)/2 = 1.025658; unit walls 4–14 m and 14–24 m: width 10√0.3 = 5.477226, offsets 4 + 2.261387 = 6.261387 and 16.261387, height 3√0.3 = 1.643168, sill 0.678416 | `P-South/W3 … window(offset=1.367544 sill=1.025658 1.264911x0.948683) window(offset=6.261387 sill=0.678416 5.477226x1.643168) window(offset=16.261387 …)` |
| P-South glazing | 1.264911 × 0.948683 + 2 × 5.477226 × 1.643168 = 1.2 + 9 + 9 = 19.2 m² | `glazing=19.200000` |
| Façade glazing E / W | E: units 2 × (8 × 3 × 0.3) + corridor 2 × 3 × 0.2 = 7.2 + 7.2 + 1.2 = 15.6; W: stair 18 × 3 × 0.1 = 5.4 m² | `FLOOR/W2 … glazing=15.600000`, `FLOOR/W4 … glazing=5.400000` |
| Z3 lighting density | (72 × 3 + 40 × 5 + 320 × 5) / 432 = 2016 / 432 = 4.666667 W/m² | `load Lighting PerFloorArea value=4.666667` |
| Z3 occupancy density | 320 × 0.03 / 432 = 9.6 / 432 = 0.022222 people/m² | `load Occupancy PerFloorArea value=0.022222` |
| Z3 lighting schedule (annual full-load hours) | (216 × 8760 + 200 × 8760 + 1600 × 2627.8) / 2016 = 3893.174603 h, where 2627.8 h is the unit lighting schedule's annual sum shown in the Z1 snapshot | `annual=3893.174603` |
| Z3 setpoints | five conditioned sources (stair excluded, D-038), all at 21 °C / 24 °C | `setpoints heatingMean=21.000000 coolingMean=24.000000` |
| Z2 P-North area | (24 + 14.86) / 2 × 4.57 = 88.7951 m² | `area=88.795100` |
| Z2 core area | (24 − 9.14) × (18 − 9.14) = 14.86 × 8.86 = 131.6596 m² | `area=131.659600` |
| Z1 Stair-1 | the stair alone, unconditioned | `unconditioned` |

- [x] **Step 7: Run the tests and watch them pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: `Passed!  - Failed:     0, Passed:    38, Skipped:     0, Total:    38` for `net8.0` (the final S3 integration count).

- [x] **Step 8: Full file after this task: `tests/Lod.Integration.Tests/SimplifierTests.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Lod.Generators.Linear;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class SimplifierTests
{
    private const double PerimeterDepth = 4.57;

    [Fact]
    public void SemanticMergeJoinsConnectedZonesOfTheSameType()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.Equal(new[] { "Stair-1", "Corridor-1", "DwellingUnit-1", "DwellingUnit-2" }, floor.Zones.Select(z => z.Id.Value));
        Zone south = floor.Zones.Single(z => z.Id.Value == "DwellingUnit-1");
        Assert.Equal(160.0, south.FloorArea, 6);
        Assert.Equal(new[] { "US1", "US2" }, south.SourceZones.Select(s => s.Value));
        Assert.Equal(5.0, south.Program.Find(LoadType.Lighting, LoadBasis.PerFloorArea)!.Value, 9);
    }

    [Fact]
    public void MergedZonesLoseTheirSharedPartition()
    {
        IFloor floor = Pipeline.Floor(new SemanticMerge(Pipeline.Tolerances));

        Assert.DoesNotContain(floor.Surfaces, s => s.Zone == s.AdjacentZone);
        Assert.Equal(2, floor.Surfaces.OfType<WallSurface>().Count(w => w.Zone.Value == "DwellingUnit-1" && w.Boundary == BoundaryCondition.Outdoors));
    }

    [Fact]
    public void PerimeterCoreHasFourPerimeterZonesAndACore()
    {
        IFloor floor = Pipeline.Floor(new PerimeterCore(Pipeline.Tolerances, PerimeterDepth));

        Assert.Equal(new[] { "P-North", "P-East", "P-South", "P-West", "CORE" }, floor.Zones.Select(z => z.Id.Value));
        Assert.Equal((24.0 - (2 * PerimeterDepth)) * (18.0 - (2 * PerimeterDepth)), floor.Zones.Single(z => z.Id.Value == "CORE").FloorArea, 6);
        Assert.DoesNotContain(floor.Surfaces.OfType<WallSurface>(), w => w.Zone.Value == "CORE" && w.Boundary == BoundaryCondition.Outdoors);
    }

    [Fact]
    public void PerimeterSouthKeepsTheSouthFacadeWindowsInPlace()
    {
        IGeneratedPlan plan = Pipeline.Plan();
        IFloor floor = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(plan).Value;

        double[] expected = plan.Surfaces.OfType<WallSurface>()
            .Where(w => w.Start.Y == 0.0 && w.End.Y == 0.0 && w.Boundary == BoundaryCondition.Outdoors)
            .SelectMany(w => w.Windows.Select(window => w.Start.X + window.Offset))
            .OrderBy(x => x)
            .ToArray();
        WallSurface south = floor.Surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "P-South" && w.Boundary == BoundaryCondition.Outdoors);
        Assert.Equal(3, south.Windows.Count);
        Assert.Equal(expected, south.Windows.Select(w => w.Offset).ToArray(), new ToleranceComparer());
        Assert.Equal(1.2 + 9.0 + 9.0, south.GlazedArea, 9);
    }

    [Fact]
    public void PerimeterDepthTooLargeIsAnError()
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, 10.0).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.PlanTooNarrow);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(-1.0)]
    public void NonPositivePerimeterDepthIsAnError(double depth)
    {
        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, depth).Simplify(Pipeline.Plan());

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.InvalidParameter);
    }

    [Fact]
    public void FootprintsWithHolesAreNotSupportedYet()
    {
        Polygon2 courtyard = Polygon2.Create(
            new[] { new Point2(0, 0), new Point2(30, 0), new Point2(30, 30), new Point2(0, 30) },
            new[] { new[] { new Point2(10, 10), new Point2(20, 10), new Point2(20, 20), new Point2(10, 20) } }).Value;
        var plan = new GeneratedPlan(courtyard, 3.0, 0.0, new Zone[0], new Surface[0], Provenance.Of("Test", new KeyValuePair<string, string>[0]));

        Result<IFloor> result = new PerimeterCore(Pipeline.Tolerances, PerimeterDepth).Simplify(plan);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.NotSupported);
    }

    [Fact]
    public void SingleZonePerFloorHasOnlyOutdoorWalls()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Zone zone = Assert.Single(floor.Zones);
        Assert.Equal(SpaceType.Mixed, zone.SpaceType);
        Assert.Equal(6, zone.SourceZones.Count);
        Assert.All(floor.Surfaces.OfType<WallSurface>(), w => Assert.Equal(BoundaryCondition.Outdoors, w.Boundary));
        Assert.Equal(4, floor.Surfaces.OfType<WallSurface>().Count());
    }

    [Fact]
    public void SetpointsAreFloorAreaWeightedAndRecorded()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));

        Thermostat thermostat = floor.Zones[0].Program.Thermostat!;
        Assert.Equal(21.0, thermostat.HeatingSetpoint[0], 9);
        Assert.Equal(Lod.Core.Aggregation.AggregationMethod.FloorAreaWeighted, thermostat.HeatingSetpoint.Aggregation!.Method);
        Assert.DoesNotContain(new ZoneId("ST"), thermostat.HeatingSetpoint.Aggregation.Sources);
        Assert.Equal(5, thermostat.HeatingSetpoint.Aggregation.Sources.Count);
    }

    [Theory]
    [InlineData("SemanticMerge", 1)]
    [InlineData("SemanticMerge", 2)]
    [InlineData("SemanticMerge", 3)]
    [InlineData("PerimeterCore", 1)]
    [InlineData("PerimeterCore", 2)]
    [InlineData("PerimeterCore", 3)]
    [InlineData("PerimeterCore", 4)]
    [InlineData("SingleZonePerFloor", 1)]
    [InlineData("SingleZonePerFloor", 2)]
    public void EverySimplifierSatisfiesTheInvariantsForRandomPlans(string simplifier, int seed)
    {
        LinearPlanParameters parameters = RandomParameters(new Random(seed));

        IFloor floor = Simplifier(simplifier).Simplify(Pipeline.Plan(parameters)).Value;
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(floor);

        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported()
    {
        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances)));

        CheckResult conditioned = report.Checks.Single(c => c.Check == "ConditionedFloorArea");
        Assert.False(conditioned.Passed);
        Assert.False(conditioned.Enforced);
        Assert.True(report.Passed, report.Describe());
    }

    [Fact]
    public void ValidationCatchesAnUncoveredFacade()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Surface[] withoutSouthWall = floor.Surfaces.Where(s => !(s is WallSurface w && w.Start.Y == 0.0 && w.End.Y == 0.0)).ToArray();
        var broken = new Floor(floor.Source, floor.Zones, withoutSouthWall, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.Contains(report.Checks, c => c.Check == "FacadeCoverage" && !c.Passed && c.Enforced);
        Assert.False(report.Passed);
    }

    [Fact]
    public void NoSimplificationPassesValidation()
    {
        Assert.True(new FloorValidator(Pipeline.Tolerances).Validate(Pipeline.DetailedFloor()).Passed);
    }

    [Fact]
    public void ValidationCatchesAChangedProgram()
    {
        IFloor floor = Pipeline.Floor(new SingleZonePerFloor(Pipeline.Tolerances));
        Zone zone = floor.Zones[0];
        var tampered = new Zone(zone.Id, zone.Name, zone.SpaceType, zone.Parts, ExampleResidentialPresets.DwellingUnit.Program, zone.SourceZones);
        var broken = new Floor(floor.Source, new[] { tampered }, floor.Surfaces, floor.Mapping, floor.Provenance);

        ValidationReport report = new FloorValidator(Pipeline.Tolerances).Validate(broken);

        Assert.False(report.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Installed.Lighting" && !c.Passed);
        Assert.Contains(report.Checks, c => c.Check == "Traceability" && !c.Passed);
    }

    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void SimplifiersAreDeterministic(string simplifier)
    {
        Assert.Equal(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))));
    }

    [Theory]
    [InlineData("SemanticMerge")]
    [InlineData("PerimeterCore")]
    [InlineData("SingleZonePerFloor")]
    public void CanonicalSnapshots(string simplifier)
    {
        Snapshot.Match(TextReport.Describe(Pipeline.Floor(Simplifier(simplifier))), $"simplifier-{simplifier}");
    }

    private sealed class ToleranceComparer : IEqualityComparer<double>
    {
        public bool Equals(double x, double y) => Pipeline.Tolerances.AreaEquals(x, y);

        public int GetHashCode(double obj) => 0;
    }

    private static IPlanSimplifier Simplifier(string name) => name switch
    {
        "SemanticMerge" => new SemanticMerge(Pipeline.Tolerances),
        "PerimeterCore" => new PerimeterCore(Pipeline.Tolerances, PerimeterDepth),
        "SingleZonePerFloor" => new SingleZonePerFloor(Pipeline.Tolerances),
        _ => throw new ArgumentOutOfRangeException(nameof(name), name, "Unknown simplifier."),
    };

    private static LinearPlanParameters RandomParameters(Random random) => new(
        Length: 18.0 + (random.NextDouble() * 42.0),
        UnitDepth: 6.0 + (random.NextDouble() * 4.0),
        CorridorWidth: 1.5 + (random.NextDouble() * 1.5),
        TargetUnitWidth: 5.0 + (random.NextDouble() * 7.0),
        StairLength: 3.0 + (random.NextDouble() * 3.0),
        FloorHeight: 2.8 + (random.NextDouble() * 0.7),
        OrientationDegrees: random.NextDouble() * 360.0);
}
```

- [x] **Step 9: Commit**

```bash
git status --short
git add tests/Lod.Integration.Tests/SimplifierTests.cs tests/Lod.Integration.Tests/Snapshots/simplifier-SemanticMerge.txt tests/Lod.Integration.Tests/Snapshots/simplifier-PerimeterCore.txt tests/Lod.Integration.Tests/Snapshots/simplifier-SingleZonePerFloor.txt
git commit -m "test(rezoning): add simplifier determinism and canonical snapshots"
```

`git status --short` must list only the test file and the three `.txt` snapshots; no `.received.txt` file may remain.

- [x] **Step 10: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/validation-invariants
git push origin main
git branch -d feature/validation-invariants
```

Expected from `verify.ps1`: 104 core, 17 generators, 38 integration tests passed on `net8.0`, then `VERIFY PASSED`.

---

## Slice E — `feature/grasshopper-simplifier-components`

### Task 10: Simplifier, mapping, and validation components; Convert2BEM validation gate

Grasshopper code cannot be unit-tested without Rhino: this task is write code → `dotnet build` with 0 warnings → commit; Task 11 adds the manual check.

**Files:**
- Create: `src/Lod.Grasshopper/Components/SimplifierComponents.cs`
- Modify: `src/Lod.Grasshopper/Components/Convert2BemComponent.cs`
- Create: `docs/architecture/validation.md`
- Modify: `docs/architecture/convert2bem.md`

**Interfaces:**
- Consumes: `PlanGoo`, `FloorGoo`, `BuildingGoo`, `PlanParameter`, `FloorParameter`, `BuildingParameter`, `ComponentSupport.Unwrap`, `ComponentSupport.Report`, `ComponentCategories.Simplify` (`3 Simplify`), `.Inspect` (`6 Inspect`), `.Convert` (`5 Convert`) (S2); the three strategies (Tasks 5–7); `FloorValidator`, `BuildingValidator`, `ValidationReport` (Task 8); `DiagnosticCodes.ValidationFailed`, `.ValidationOverridden` (Task 1).
- Produces: `public abstract class PlanSimplifierComponent : GH_Component` (protected `RegisterOptions(GH_InputParamManager)`, abstract `IPlanSimplifier? CreateSimplifier(IGH_DataAccess DA)`) and the components below.

| Component | Nickname | Panel | Inputs | Outputs | GUID |
| --- | --- | --- | --- | --- | --- |
| Semantic Merge | Z1 | 3 Simplify | Plan (Plan, item) | Floor (Floor, item) | `7d36f1d3-2708-4b69-b1a7-cf294c186e9a` |
| Perimeter Core | Z2 | 3 Simplify | Plan (Plan, item); Depth (D, number, item, default 4.57 m) | Floor (Floor, item) | `6a86b976-c838-427f-93a7-344dcc2c18ce` |
| Single Zone per Floor | Z3 | 3 Simplify | Plan (Plan, item) | Floor (Floor, item) | `4ff83222-5b7d-4d1b-8f26-fd580893a5db` |
| Map Source to Target | Map | 6 Inspect | Floor (Floor, item) | Source (S), Target (T), Overlap (A, m²), Source Fraction (SF), Target Fraction (TF); all lists, one entry per mapping row | `eee37e01-28a2-4b5a-9c7d-7566cb9d93d4` |
| Validate | Validate | 6 Inspect | Object (O, generic, item): a floor or a building | Passed (P, boolean); Report (R, text) | `03558c0b-83e8-417d-b122-96ebde64c147` |
| Convert2BEM (modified) | 2BEM | 5 Convert | adds input 1 Override (Ovr, boolean, item, default false) | adds output 15 Provenance (P, text, item) | `d091d70c-4de3-4f29-a900-ea4c9b777ba3` (unchanged) |

Simplifier errors (for example `Error PlanTooNarrow: …` or `Error FacadeNotCovered [<wall>]: …`) appear as runtime messages through `ComponentSupport.Unwrap`, and the `Floor` output stays empty. *Validate* adds an error for any other input type and a warning when validation fails.

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c feature/grasshopper-simplifier-components main
```

- [x] **Step 2: Write the components**

Create `src/Lod.Grasshopper/Components/SimplifierComponents.cs`:

```csharp
using System;
using System.Drawing;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Core.Validation;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;

namespace Lod.Grasshopper.Components;

/// <summary>Shared inputs and solving of the plan simplifier components.</summary>
public abstract class PlanSimplifierComponent : GH_Component
{
    protected PlanSimplifierComponent(string name, string nickname, string description)
        : base(name, nickname, description, ComponentCategories.Category, ComponentCategories.Simplify)
    {
    }

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new PlanParameter(), "Plan", "Plan", "Detailed plan.", GH_ParamAccess.item);
        RegisterOptions(pManager);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floor", "Floor", "The simplified floor.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        PlanGoo? plan = null;
        if (!DA.GetData(0, ref plan) || plan is null)
        {
            return;
        }

        IPlanSimplifier? simplifier = CreateSimplifier(DA);
        IFloor? floor = simplifier is null ? null : ComponentSupport.Unwrap(this, simplifier.Simplify(plan.Value));
        if (floor is not null)
        {
            DA.SetData(0, new FloorGoo(floor));
        }
    }

    protected virtual void RegisterOptions(GH_InputParamManager pManager)
    {
    }

    protected abstract IPlanSimplifier? CreateSimplifier(IGH_DataAccess DA);
}

public sealed class SemanticMergeComponent : PlanSimplifierComponent
{
    public SemanticMergeComponent()
        : base("Semantic Merge", "Z1", "Merges connected zones of the same space type (Z1).")
    {
    }

    public override Guid ComponentGuid => new("7d36f1d3-2708-4b69-b1a7-cf294c186e9a");

    protected override IPlanSimplifier CreateSimplifier(IGH_DataAccess DA) => new SemanticMerge(ToleranceSettings.Default);
}

public sealed class PerimeterCoreComponent : PlanSimplifierComponent
{
    public PerimeterCoreComponent()
        : base("Perimeter Core", "Z2", "Perimeter zones per orientation plus a core (Z2); corners split on the bisectors (ADR-008).")
    {
    }

    public override Guid ComponentGuid => new("6a86b976-c838-427f-93a7-344dcc2c18ce");

    protected override void RegisterOptions(GH_InputParamManager pManager)
    {
        pManager.AddNumberParameter("Depth", "D", "Perimeter zone depth, m.", GH_ParamAccess.item, 4.57);
    }

    protected override IPlanSimplifier? CreateSimplifier(IGH_DataAccess DA)
    {
        double depth = 0.0;
        return DA.GetData(1, ref depth) ? new PerimeterCore(ToleranceSettings.Default, depth) : null;
    }
}

public sealed class SingleZonePerFloorComponent : PlanSimplifierComponent
{
    public SingleZonePerFloorComponent()
        : base("Single Zone per Floor", "Z3", "The whole floor as one zone (Z3).")
    {
    }

    public override Guid ComponentGuid => new("4ff83222-5b7d-4d1b-8f26-fd580893a5db");

    protected override IPlanSimplifier CreateSimplifier(IGH_DataAccess DA) => new SingleZonePerFloor(ToleranceSettings.Default);
}

public sealed class MapSourceToTargetComponent : GH_Component
{
    public MapSourceToTargetComponent()
        : base("Map Source to Target", "Map", "The source-to-target overlap rows of a floor (spec §11).", ComponentCategories.Category, ComponentCategories.Inspect)
    {
    }

    public override Guid ComponentGuid => new("eee37e01-28a2-4b5a-9c7d-7566cb9d93d4");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floor", "Floor", "A simplified floor.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddTextParameter("Source", "S", "Source zone of each row.", GH_ParamAccess.list);
        pManager.AddTextParameter("Target", "T", "Target zone of each row.", GH_ParamAccess.list);
        pManager.AddNumberParameter("Overlap", "A", "Overlap area, m².", GH_ParamAccess.list);
        pManager.AddNumberParameter("Source Fraction", "SF", "Overlap / source area.", GH_ParamAccess.list);
        pManager.AddNumberParameter("Target Fraction", "TF", "Overlap / target area.", GH_ParamAccess.list);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        FloorGoo? floor = null;
        if (!DA.GetData(0, ref floor) || floor is null)
        {
            return;
        }

        ZoneMapping[] rows = floor.Value.Mapping.ToArray();
        DA.SetDataList(0, rows.Select(r => r.Source.Value));
        DA.SetDataList(1, rows.Select(r => r.Target.Value));
        DA.SetDataList(2, rows.Select(r => r.OverlapArea));
        DA.SetDataList(3, rows.Select(r => r.SourceFraction));
        DA.SetDataList(4, rows.Select(r => r.TargetFraction));
    }
}

public sealed class ValidateComponent : GH_Component
{
    public ValidateComponent()
        : base("Validate", "Validate", "Checks a floor or building against its prescribed conservation invariants.", ComponentCategories.Category, ComponentCategories.Inspect)
    {
    }

    public override Guid ComponentGuid => new("03558c0b-83e8-417d-b122-96ebde64c147");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddGenericParameter("Object", "O", "A floor or building.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddBooleanParameter("Passed", "P", "Whether every enforced check passed.", GH_ParamAccess.item);
        pManager.AddTextParameter("Report", "R", "One line per check.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        IGH_Goo? goo = null;
        if (!DA.GetData(0, ref goo) || goo is null)
        {
            return;
        }

        ValidationReport? report = goo switch
        {
            FloorGoo floor => new FloorValidator(ToleranceSettings.Default).Validate(floor.Value),
            BuildingGoo building => new BuildingValidator(ToleranceSettings.Default).Validate(building.Value),
            _ => null,
        };
        if (report is null)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Expected a floor or building, got {goo.TypeName}.");
            return;
        }

        if (!report.Passed)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Validation failed; see Report.");
        }

        DA.SetData(0, report.Passed);
        DA.SetData(1, report.Describe());
    }
}
```

- [x] **Step 3: Build**

```bash
dotnet build src/Lod.Grasshopper -c Release
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)` (`net7.0`).

- [x] **Step 4: Commit**

```bash
git add src/Lod.Grasshopper/Components/SimplifierComponents.cs
git commit -m "feature(grasshopper): add simplifier, mapping, and validate components"
```

- [x] **Step 5: Add the validation gate to Convert2BEM**

Edit `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` (S2 version) as follows.

1. Usings: add `using Lod.Core.Common;` after `using Grasshopper.Kernel.Data;`, and `using Lod.Core.Validation;` after `using Lod.Core.Model;`.
2. Class summary: replace

```csharp
/// in building zone order. The output layout is documented in docs/architecture/convert2bem.md.
```

with

```csharp
/// in building zone order. The output layout is documented in docs/architecture/convert2bem.md. The building is validated first; a failed
/// validation blocks conversion unless Override is set, and the override is recorded in the Provenance output (GLOBAL.md, scientific rule 6).
```

3. Inputs: after the `Building` parameter line add

```csharp
        pManager.AddBooleanParameter("Override", "Ovr", "Convert even if validation fails; the override is recorded.", GH_ParamAccess.item, false);
```

4. Outputs: after the `Internal Mass` parameter line (output 14) add

```csharp
        pManager.AddTextParameter("Provenance", "P", "Building provenance, validation report, and any override.", GH_ParamAccess.item);
```

5. `SolveInstance`: replace

```csharp
        BuildingGoo? goo = null;
        if (!DA.GetData(0, ref goo) || goo is null)
        {
            return;
        }

        IGeneratedBuilding building = goo.Value;
```

with

```csharp
        BuildingGoo? goo = null;
        bool overrideValidation = false;
        if (!DA.GetData(0, ref goo) || goo is null || !DA.GetData(1, ref overrideValidation))
        {
            return;
        }

        IGeneratedBuilding building = goo.Value;
        ValidationReport report = new BuildingValidator(ToleranceSettings.Default).Validate(building);
        string record = building.Provenance.Describe() + report.Describe();
        if (!report.Passed && !overrideValidation)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Error(DiagnosticCodes.ValidationFailed, "Validation failed; conversion blocked. See Provenance, or set Override.") });
            DA.SetData(15, record);
            return;
        }

        if (!report.Passed)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Warning(DiagnosticCodes.ValidationOverridden, "Validation failed; converted because Override is set. The override is recorded in Provenance.") });
            record += "OVERRIDE: converted despite failed validation\n";
        }
```

followed by one blank line before `var zones = new DataTree<Brep>();`.

6. After `DA.SetDataTree(14, mass);` (the last line of `SolveInstance`) add

```csharp
        DA.SetData(15, record);
```

Behaviour: the building is validated with `BuildingValidator` on every solve. Passed: conversion as in S2, plus `Provenance` = provenance tree + report. Failed without `Override`: error `ValidationFailed`, only `Provenance` is set, outputs 0–14 stay empty. Failed with `Override`: warning `ValidationOverridden`, conversion runs, and `Provenance` ends with `OVERRIDE: converted despite failed validation` (GLOBAL.md scientific rule 6).

- [x] **Step 6: Full file after this task: `src/Lod.Grasshopper/Components/Convert2BemComponent.cs`**

```csharp
using System;
using System.Drawing;
using System.Linq;
using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Lod.Core.Common;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Validation;
using Lod.Grasshopper.Convert;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;
using Rhino.Geometry;
using Surface = Lod.Core.Model.Surface;

namespace Lod.Grasshopper.Components;

/// <summary>
/// Converts a building into neutral Grasshopper data for a ClimateStudio definition (D-023, provisional): one tree branch per zone,
/// in building zone order. The output layout is documented in docs/architecture/convert2bem.md. The building is validated first; a failed
/// validation blocks conversion unless Override is set, and the override is recorded in the Provenance output (GLOBAL.md, scientific rule 6).
/// </summary>
public sealed class Convert2BemComponent : GH_Component
{
    public Convert2BemComponent()
        : base(
            "Convert2BEM",
            "2BEM",
            "Building to zone geometry, programs, and surfaces as data trees (branch {i} = zone i), ready to wire into a ClimateStudio definition. Provisional layout (D-023).",
            ComponentCategories.Category,
            ComponentCategories.Convert)
    {
    }

    public override Guid ComponentGuid => new("d091d70c-4de3-4f29-a900-ea4c9b777ba3");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new BuildingParameter(), "Building", "Bldg", "The building.", GH_ParamAccess.item);
        pManager.AddBooleanParameter("Override", "Ovr", "Convert even if validation fails; the override is recorded.", GH_ParamAccess.item, false);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddBrepParameter("Zones", "Z", "{i}: closed Brep of each part of zone i, model units.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Names", "N", "{i}: zone ID.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Space Types", "ST", "{i}: space type.", GH_ParamAccess.tree);
        pManager.AddIntegerParameter("Multipliers", "M", "{i}: zone multiplier.", GH_ParamAccess.tree);
        pManager.AddBooleanParameter("Conditioned", "Cd", "{i}: whether zone i is conditioned (D-038).", GH_ParamAccess.tree);
        pManager.AddTextParameter("Load Types", "LT", "{i}: load types, aligned with Load Values.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Load Bases", "LB", "{i}: load bases.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Load Values", "LV", "{i}: design values in their basis.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Load Schedules", "LS", "{i;k}: 8760 fractions of load k of zone i.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Heating Setpoints", "HS", "{i}: 8760 heating setpoints, °C; empty for unconditioned zones.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Cooling Setpoints", "CS", "{i}: 8760 cooling setpoints, °C; empty for unconditioned zones.", GH_ParamAccess.tree);
        pManager.AddBrepParameter("Surfaces", "S", "{i}: walls, floors, and ceilings of zone i.", GH_ParamAccess.tree);
        pManager.AddTextParameter("Boundaries", "B", "{i}: boundary of each surface: Outdoors, Ground, Adiabatic, or Interzone:<zone ID>.", GH_ParamAccess.tree);
        pManager.AddBrepParameter("Windows", "W", "{i}: explicit windows of zone i, at their positions.", GH_ParamAccess.tree);
        pManager.AddNumberParameter("Internal Mass", "IM", "{i}: exposed internal-mass area of zone i (slab area × exposed faces), m².", GH_ParamAccess.tree);
        pManager.AddTextParameter("Provenance", "P", "Building provenance, validation report, and any override.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        BuildingGoo? goo = null;
        bool overrideValidation = false;
        if (!DA.GetData(0, ref goo) || goo is null || !DA.GetData(1, ref overrideValidation))
        {
            return;
        }

        IGeneratedBuilding building = goo.Value;
        ValidationReport report = new BuildingValidator(ToleranceSettings.Default).Validate(building);
        string record = building.Provenance.Describe() + report.Describe();
        if (!report.Passed && !overrideValidation)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Error(DiagnosticCodes.ValidationFailed, "Validation failed; conversion blocked. See Provenance, or set Override.") });
            DA.SetData(15, record);
            return;
        }

        if (!report.Passed)
        {
            ComponentSupport.Report(this, new[] { Diagnostic.Warning(DiagnosticCodes.ValidationOverridden, "Validation failed; converted because Override is set. The override is recorded in Provenance.") });
            record += "OVERRIDE: converted despite failed validation\n";
        }

        var zones = new DataTree<Brep>();
        var names = new DataTree<string>();
        var spaceTypes = new DataTree<string>();
        var multipliers = new DataTree<int>();
        var conditioned = new DataTree<bool>();
        var loadTypes = new DataTree<string>();
        var loadBases = new DataTree<string>();
        var loadValues = new DataTree<double>();
        var loadSchedules = new DataTree<double>();
        var heating = new DataTree<double>();
        var cooling = new DataTree<double>();
        var surfaces = new DataTree<Brep>();
        var boundaries = new DataTree<string>();
        var windows = new DataTree<Brep>();
        var mass = new DataTree<double>();

        for (int i = 0; i < building.Zones.Count; i++)
        {
            Zone zone = building.Zones[i];
            var path = new GH_Path(i);
            zones.AddRange(RhinoGeometry.ZoneBreps(zone), path);
            names.Add(zone.Id.Value, path);
            spaceTypes.Add(zone.SpaceType.ToString(), path);
            multipliers.Add(zone.Multiplier, path);
            conditioned.Add(zone.Program.IsConditioned, path);
            for (int k = 0; k < zone.Program.Loads.Count; k++)
            {
                LoadDefinition load = zone.Program.Loads[k];
                loadTypes.Add(load.Type.ToString(), path);
                loadBases.Add(load.Basis.ToString(), path);
                loadValues.Add(load.Value, path);
                loadSchedules.AddRange(load.Schedule.Values, new GH_Path(i, k));
            }

            heating.EnsurePath(path);
            cooling.EnsurePath(path);
            if (zone.Program.Thermostat is { } thermostat)
            {
                heating.AddRange(thermostat.HeatingSetpoint.Values, path);
                cooling.AddRange(thermostat.CoolingSetpoint.Values, path);
            }
            foreach (Surface surface in building.Surfaces.Where(s => s.Zone == zone.Id))
            {
                foreach (Brep brep in SurfaceBreps(surface))
                {
                    surfaces.Add(brep, path);
                    boundaries.Add(surface.AdjacentZone is { } adjacent ? $"{surface.Boundary}:{adjacent.Value}" : surface.Boundary.ToString(), path);
                }

                if (surface is WallSurface wall)
                {
                    windows.AddRange(RhinoGeometry.WindowBreps(wall), path);
                }
            }

            mass.Add(building.InternalMasses.Where(m => m.Zone == zone.Id).Sum(m => m.SlabArea * m.ExposedFaces), path);
        }

        DA.SetDataTree(0, zones);
        DA.SetDataTree(1, names);
        DA.SetDataTree(2, spaceTypes);
        DA.SetDataTree(3, multipliers);
        DA.SetDataTree(4, conditioned);
        DA.SetDataTree(5, loadTypes);
        DA.SetDataTree(6, loadBases);
        DA.SetDataTree(7, loadValues);
        DA.SetDataTree(8, loadSchedules);
        DA.SetDataTree(9, heating);
        DA.SetDataTree(10, cooling);
        DA.SetDataTree(11, surfaces);
        DA.SetDataTree(12, boundaries);
        DA.SetDataTree(13, windows);
        DA.SetDataTree(14, mass);
        DA.SetData(15, record);
    }

    private static Brep[] SurfaceBreps(Surface surface) => surface switch
    {
        WallSurface wall => RhinoGeometry.WallBrep(wall) is { } brep ? new[] { brep } : new Brep[0],
        HorizontalSurface horizontal => RhinoGeometry.HorizontalBreps(horizontal).ToArray(),
        _ => new Brep[0],
    };
}
```

- [x] **Step 7: Build**

```bash
dotnet build src/Lod.Grasshopper -c Release
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`.

- [x] **Step 8: Write `docs/architecture/validation.md`**

Create `docs/architecture/validation.md` with exactly this content:

````markdown
# Validation

Applies from v0.3.0 (S3). Code: `src/Lod.Core/Validation/Totals.cs` and `src/Lod.Core/Validation/Validators.cs`. Rules: GLOBAL.md scientific rules 1, 2, and 6; research brief §17; D-038 (conditioning), D-041 (façade coverage), D-045 (building height), D-046 (ground, roof, and exposed floor area); roadmap S3 slice `feature/validation-invariants`.

## Purpose

Simplification deliberately changes zoning, heat transfer between zones, and controls where the LoD says so; those differences are what the study measures. It must not change the prescribed conservation invariants: floor area, volume, exterior wall area, glazed area in total and per orientation, and the installed and hourly scheduled magnitude of every load type; for a building also ground, roof, and exposed floor area and the building height (D-045, D-046); and the target façades must cover the source façades. Validation checks these numerically, together with tiling and traceability, before a model is converted.

Validation applies to objects that exist. A simplifier that cannot produce a valid floor fails earlier, with its own diagnostics (`PlanTooNarrow`, `NotSupported`, `DisconnectedGroup`, `FacadeNotCovered`, `WindowNotHosted`, gaps and overlaps from the surface builder, aggregation errors), and returns no floor.

## References

| Validator | Validates | Compared with |
| --- | --- | --- |
| `FloorValidator` | an `IFloor` from any plan simplifier | its source plan, `IFloor.Source` (the detailed Z0 plan) |
| `BuildingValidator` | an `IGeneratedBuilding` from any floor aggregator | 1. every distinct source floor against its plan, as `FloorValidator` does; check names prefixed `Floor0.`, `Floor1.`, … in floor order. 2. the fully stacked reference `Stack.Aggregate(building.Sources)`: the same floor entries with every storey explicit; check names prefixed `Building.` |

If the stacked reference cannot be built, `BuildingValidator` adds the failed check `Building.Reference` with the stacking diagnostics and stops.

## Totals

`Totals.Of(zones, surfaces, orientationDegrees)` computes the extensive quantities of a set of zones, counting zone multipliers.

| Total | Definition |
| --- | --- |
| Floor area | Σ multiplier × zone floor area, m² |
| Volume | Σ multiplier × zone volume, m³ |
| Conditioned floor area | Σ multiplier × floor area of zones whose program has a thermostat, m² (D-038) |
| Exterior wall area | Σ multiplier × gross area of walls with boundary `Outdoors`, windows included, m² |
| Glazing | Σ multiplier × glazed area of those walls (all their windows), m² |
| Glazing per orientation | the same per bin North [315°, 45°), East [45°, 135°), South [135°, 225°), West [225°, 315°) of the wall's true azimuth (plan azimuth + orientation) |
| Ground area | Σ multiplier × area of horizontal surfaces with boundary `Ground`, m² |
| Roof area | Σ multiplier × area of ceilings with boundary `Outdoors`, m² |
| Exposed floor area | Σ multiplier × area of floors with boundary `Outdoors` (overhangs, floors not covered by the storey below), m² |
| Height | elevation of the highest zone top (part elevation + part height), m; 0 without zones. This is the building height when the lowest storey starts at 0 |
| Installed magnitude | per load type, summed over all bases of the type (D-047), Σ multiplier × design magnitude (ADR-007): people for occupancy; W for lighting, electric and gas equipment; m³/h for hot water, ventilation, and infiltration |
| Scheduled magnitude | per load type and hour (8760 values), Σ multiplier × design magnitude × schedule fraction |

## Checks

Relative comparisons are `|a − b| ≤ tol × max(1, |a|, |b|)` (ADR-004).

| Check | Compares | Tolerance | Enforced |
| --- | --- | --- | --- |
| `FloorArea` | floor area | `RelativeArea` | yes |
| `Volume` | volume | `RelativeArea` | yes |
| `ConditionedFloorArea` | conditioned floor area | `RelativeArea` | no: reported only (D-038) |
| `ExteriorWallArea` | exterior wall area | `RelativeArea` | yes |
| `Glazing` | total glazed area | `RelativeArea` | yes |
| `Glazing.<Bin>` | glazed area per orientation bin; one check per bin present in either total | `RelativeArea` | yes |
| `Installed.<LoadType>` | installed magnitude; one check per load type present in either total, all bases of the type together (D-047) | `RelativeLoad` | yes |
| `Scheduled.<LoadType>` | scheduled magnitude at each of the 8760 hours; the detail names the worst hour | `RelativeLoad` at every hour | yes |
| `FacadeCoverage` (floor) | every source outdoor wall is covered over its full length by target outdoor walls on the same façade line, before any normalisation | `RelativeArea`, applied to lengths | yes (D-041) |
| `NoTargetOverlap` (floor) | Σ pairwise intersection area of the target zones | at most `RelativeArea` × footprint area | yes |
| `SourceCoverage` (floor) | each source zone's floor area vs the sum of its mapping overlaps | `RelativeArea` | yes |
| `Traceability` (floor) | every target zone has a mapping row; an identity zone (no source zones, `NoSimplification`) has an identity row with source fraction 1; a derived zone has aggregation records on every load value and every load schedule and, if it is conditioned, on both setpoint schedules | exact | yes |
| `Building.Reference` | the stacked reference could not be built | — | yes |
| `Building.GroundArea` | ground area vs the stacked reference | `RelativeArea` | yes (D-046) |
| `Building.RoofArea` | roof area vs the stacked reference | `RelativeArea` | yes (D-046) |
| `Building.ExposedFloorArea` | exposed floor area vs the stacked reference: a floor aggregator must not multiply overhanging floors | `RelativeArea` | yes (D-046) |
| `Building.Height` | building height vs the stacked reference: representative storeys must sit at their true elevations | `Distance`, absolute | yes (D-045) |

Occupancy and air volume flow are not separate checks: occupancy is the load type `Occupancy` (people), and air-change loads are compared as m³/h magnitudes (ADR-007, D-019).

Not compared:

- Setpoints. Floor-area weighting over the conditioned sources is a prescribed control rule, not a conservation invariant (D-038).
- Window positions and sizes. Simplifiers keep every window unchanged by construction (`WindowRehosting`, D-039; covered by its unit tests); validation compares the glazed areas.
- Floor and ceiling boundaries of a floor. They stay `Unresolved` until a floor aggregator stacks the floors.

The conditioned floor area is reported because merging conditioned and unconditioned sources makes the merged zone conditioned ("any conditioned wins", D-038). With the example presets, Z2 and Z3 turn the 72 m² stair into conditioned area: `note ConditionedFloorArea: reference 360.000000, actual 432.000000`.

A program changed by mistake is caught through the totals: `ValidationCatchesAChangedProgram` replaces a Z3 program with a preset and fails both `Installed.Lighting` and `Traceability`.

## Tolerances

All tolerances come from `ToleranceSettings.Default` (ADR-004); validation defines none of its own.

| Setting | Value | Used for |
| --- | --- | --- |
| `RelativeArea` | 1e-6 | floor area, conditioned floor area, volume, wall area, glazing, façade coverage (lengths), source coverage, overlap, ground, roof, exposed floor |
| `Distance` | 1e-6 m | building height |
| `RelativeLoad` | 1e-9 | installed and hourly scheduled magnitudes |

Loads can be held to 1e-9 while areas need 1e-6 because transfer fractions are normalised per source (`TransferMatrix`) and per source wall (`FacadeAttribution`): extensive quantities are conserved to floating-point precision whatever the polygon rounding, whereas areas pass through Clipper2 on a 1e-6 m grid. Normalisation is safe only because coverage is checked separately and before it (`SourceCoverage`, `FacadeCoverage`). Tolerances are never widened to make a check pass (AGENTS.md rule 12).

## Report

`ValidationReport.Passed` is true when every enforced check passed. `ValidationReport.Describe()` writes `PASSED` or `FAILED` on the first line, then one line per check: `ok` for a passed check, `FAIL` for a failed enforced check, `note` for a failed reported-only check, followed by the check name and the reference and actual values with six decimals.

## Where validation runs

- *Validate* component (`6 Inspect`): takes a floor or a building and outputs `Passed` and the report; a failed validation adds a warning.
- *Convert2BEM* (`5 Convert`): validates the building with `BuildingValidator` before converting it. Passed: the conversion runs and `Provenance` (output 15) holds the provenance tree followed by the report. Failed with `Override` false (the default): error `ValidationFailed`, no conversion (outputs 0–14 stay empty), and only `Provenance` is set so the failing checks can be read. Failed with `Override` true: warning `ValidationOverridden`, the conversion runs, and `Provenance` ends with the line `OVERRIDE: converted despite failed validation`. The override is recorded only in that text, so keep `Provenance` with any result produced from an overridden model.

## Tests

- `EverySimplifierSatisfiesTheInvariantsForRandomPlans`: each simplifier on linear plans drawn from explicit seeds (9 cases, including rotated plans and source zones split across several targets).
- `MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported`: the conditioned-area change is reported, not enforced.
- `ValidationCatchesAnUncoveredFacade`: a missing target wall fails `FacadeCoverage`.
- `NoSimplificationPassesValidation`: the identity floor passes.
- `ValidationCatchesAChangedProgram`: a tampered program fails.
````

- [x] **Step 9: Update `docs/architecture/convert2bem.md`**

This file was created in S2 (S2 plan, Task 9 Step 4). Make four edits.

1. In the table under `## Input`, after the row

```markdown
| 0 | Building | Bldg | item | An `IGeneratedBuilding` from a floor aggregator; in S2 from *Stack Floors*. |
```

add the row

```markdown
| 1 | Override | Ovr | item | Boolean, default `false`. Convert even if validation fails; the override is recorded in *Provenance*. |
```

2. Replace the paragraph below that table,

```markdown
In S2 the building is converted as given; no validation exists yet. From S3 the component validates the building first and blocks conversion when validation fails, unless an override is set, which is then recorded in a provenance output (GLOBAL.md, scientific rule 6). That change adds an input and an output and updates this document.
```

with

```markdown
From S3 (`v0.3.0`) the component validates the building before converting it; see [Validation gate](#validation-gate).
```

3. Insert this section directly before the heading `## Zone order and tree paths`, followed by one blank line:

```markdown
## Validation gate

From S3 (`v0.3.0`) *Convert2BEM* validates the building before converting it (GLOBAL.md, scientific rule 6; checks and tolerances in [validation.md](validation.md)).

1. `BuildingValidator` with `ToleranceSettings.Default` runs on every solve.
2. Passed: the conversion runs, outputs 0–14 are filled, and *Provenance* holds the building's provenance tree followed by the validation report.
3. Failed and *Override* `false` (the default): the component shows the error `ValidationFailed`, outputs 0–14 stay empty, and only *Provenance* is set, so the failing checks can be read.
4. Failed and *Override* `true`: the component shows the warning `ValidationOverridden`, the conversion runs, and *Provenance* ends with the line `OVERRIDE: converted despite failed validation`.

Only enforced checks decide the outcome. The conditioned floor area is reported as a `note` line and never blocks (D-038); ground, roof, and exposed floor area (D-046) and building height (D-045) are enforced. The override is recorded only in *Provenance*, not in the building, so keep that text with any result produced from an overridden model.
```

4. In the table under `## Outputs`, after the row that starts with `| 14 | Internal Mass | IM |`, add the row

```markdown
| 15 | Provenance | P | item: one text | The building's provenance tree, then the validation report (`PASSED` or `FAILED`, then one line per check), then the line `OVERRIDE: converted despite failed validation` when *Override* was used. Set on every solve that has a building, including blocked ones. | — |
```

- [x] **Step 10: Commit**

```bash
git add src/Lod.Grasshopper/Components/Convert2BemComponent.cs docs/architecture/validation.md docs/architecture/convert2bem.md
git commit -m "feature(grasshopper): block convert2bem on failed validation unless overridden"
```

### Task 11: Manual smoke test in Rhino 8

**Files:**
- Modify: `docs/development/grasshopper-smoke-test.md`

**Interfaces:**
- Consumes: the plugin built from this branch; the guide's "Recording the result" rule and the S2 checklist in the same document.
- Produces: the S3 checklist, run by a person in Rhino 8; the smoke-test record for the close-out commit.

- [x] **Step 1: Append the S3 checklist**

Add the following at the end of `docs/development/grasshopper-smoke-test.md`, after the S2 checklist (separated by one blank line), so it nests under the guide's `## Stage checklists` section:

````markdown
### S3 checklist — plan simplifiers and validation (`v0.3.0`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings), close Rhino, and start it again with the plugin loaded as described above.

#### Toolbar

- [ ] *3 Simplify*: No Simplification, Semantic Merge, Perimeter Core, Single Zone per Floor. *6 Inspect*: Inspect, Map Source to Target, Validate.
- [ ] *Convert2BEM* has the inputs *Building* and *Override* (default `False`) and 16 outputs, the last one *Provenance*.

#### Simplifiers

1. Place *Example Residential Presets* and *Linear Plan Generator* with every number input at its default, and connect *Presets* (the canonical 24 m × 18 m plan of the S2 checklist).
2. Connect the plan to *No Simplification*, *Semantic Merge*, *Perimeter Core* (*Depth* 4.57, the default), and *Single Zone per Floor*.
   - [ ] None of the four shows a warning or error.
   - [ ] The *Floor* outputs read `Floor (6 zones, NoSimplification)`, `Floor (4 zones, SemanticMerge)`, `Floor (5 zones, PerimeterCore)`, and `Floor (1 zones, SingleZonePerFloor)` (hover over the output or use a panel).
   - [ ] Semantic Merge previews the stair, the corridor, and one dwelling-unit zone per row; the partition between the two units of a row is gone.
   - [ ] Perimeter Core previews four trapezoidal perimeter zones that meet on the diagonals at the corners, and a rectangular core, all in the *Mixed* colour (green); the core has no window.
   - [ ] Single Zone per Floor previews one *Mixed* zone.
   - [ ] Every simplified floor shows the same windows as the *No Simplification* floor, at the same positions and sizes: three on the south façade, three on the north, three on the east, and one on the west (D-039).
3. Connect *Inspect* to each simplified floor.
   - [ ] Each *Report* equals the matching snapshot in `tests/Lod.Integration.Tests/Snapshots/` (`simplifier-SemanticMerge.txt`, `simplifier-PerimeterCore.txt`, `simplifier-SingleZonePerFloor.txt`); for example `surface P-South/W3 … glazing=19.200000 window(offset=1.367544 …)`, and `unconditioned` under `zone Stair-1`.
4. Connect *Map Source to Target* to the Perimeter Core floor.
   - [ ] It lists 18 rows. The rows with source `ST` have the targets `P-North`, `P-South`, and `P-West`, overlaps 8, 8, and 56 m², and source fractions 0.111111, 0.111111, and 0.777778.
5. Connect *Validate* to each simplified floor.
   - [ ] *Passed* is `True`, and *Report* starts with `PASSED`.
   - [ ] Semantic Merge: every line starts with `ok`. Perimeter Core and Single Zone per Floor: one line reads `note ConditionedFloorArea: reference 360.000000, actual 432.000000` (the unconditioned stair is merged into conditioned zones, D-038); every other line starts with `ok`.
   - [ ] Connected to the plan instead, *Validate* shows the error `Expected a floor or building, got Plan.`

#### Conversion

6. Connect each simplified floor in turn to *Stack Floors* (no multipliers), and the building to *Validate* and to *Convert2BEM*.
   - [ ] *Validate* reports `PASSED`; the `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` lines read `ok` (enforced, D-045, D-046).
   - [ ] *Convert2BEM* shows no warning or error and fills outputs 0–14 as in the S2 checklist. *Conditioned* is `False` only for `L0/Stair-1` of the Semantic Merge building; every zone of the Perimeter Core and Single Zone per Floor buildings is `True`.
   - [ ] *Provenance* starts with the provenance tree (`Stack`, then the simplifier, then `LinearPlanGenerator`), followed by `PASSED` and the `Floor0.` and `Building.` check lines, and has no `OVERRIDE` line.

#### Errors

- [ ] Set the *Perimeter Core* *Depth* to 10: the component turns red with `Error PlanTooNarrow: Perimeter depth 10 m leaves no valid core for this footprint.` and produces no floor. Set it back to 4.57.
- [ ] Set *Depth* to 0: the component shows `Error InvalidParameter: Perimeter depth must be positive, got 0.` Set it back to 4.57.

The blocked and overridden paths of *Convert2BEM* cannot be reached with valid pipeline components, because every simplifier and *Stack Floors* output validates; they are covered by code review of the gate and by the validator tests.
````

- [x] **Step 2: Commit**

```bash
git add docs/development/grasshopper-smoke-test.md
git commit -m "docs(grasshopper): add s3 smoke-test checklist"
```

- [x] **Step 3: Run the checklist in Rhino 8 (manual, by a person)**

Close Rhino, build the plugin from this branch (`dotnet build src/Lod.Grasshopper -c Release`), start Rhino with the plugin loaded as the smoke-test guide describes, and work through every item of the S3 checklist. Agents cannot do this step. Following the guide's "Recording the result" rule, write down the tester, the date, the Rhino version and runtime (.NET Core), the SHA that was built (`git rev-parse HEAD`), the version text shown by *BEMGen Info*, and pass or fail per item; these values go into the close-out commit. A failed item is fixed on this branch before merging.

- [x] **Step 4: Merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/grasshopper-simplifier-components
git push origin main
git branch -d feature/grasshopper-simplifier-components
```

Expected from `verify.ps1`: 104 core, 17 generators, 38 integration tests passed on `net8.0`, then `VERIFY PASSED`. If `git rebase` rewrote commits because `main` had moved, the tested SHA differs from the merged one; record both in the close-out commit.

---

## Stage close-out

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c chore/repo-s3-close-out main
```

- [x] **Step 2: Verify the stage**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected:

```text
Passed!  - Failed:     0, Passed:   104, Skipped:     0, Total:   104, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    17, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    38, Skipped:     0, Total:    38, Duration: … - Lod.Integration.Tests.dll (net8.0)
VERIFY PASSED
```

(line order may differ).

- [x] **Step 3: Bump the version**

In `Directory.Build.props` replace

```xml
    <Version>0.2.0</Version>
```

with

```xml
    <Version>0.3.0</Version>
```

`BuildInfoTests` compares against the assembly version, so it keeps passing.

- [x] **Step 4: Verify again**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: the same counts as Step 2 and `VERIFY PASSED`.

- [x] **Step 5: Commit the version**

```bash
git add Directory.Build.props
git commit -m "build(repo): set version 0.3.0"
```

- [x] **Step 6: Update AGENTS.md "Project state"**

Replace everything between the heading `## Project state` and the heading `## Commands` with the following (keep one blank line after the heading and one before `## Commands`; the `## Commands` section does not change in S3):

```markdown
Stages S0–S3 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.3.0`). The pipeline runs for the linear plan at Z0–Z3: program presets → `LinearPlanGenerator` → `NoSimplification`, `SemanticMerge`, `PerimeterCore` ([ADR-008](docs/decisions/ADR-008-perimeter-core-corners.md)), or `SingleZonePerFloor` → `Stack` → *Convert2BEM*. Simplifiers keep every window in place (D-039) and require full façade coverage (D-041). Every floor and building is validated against the prescribed conservation invariants ([docs/architecture/validation.md](docs/architecture/validation.md)); *Convert2BEM* blocks conversion on a failed validation unless *Override* is set, and records the override in its *Provenance* output.

Projects: `Lod.Core`, `Lod.Generators`, `Lod.Grasshopper`. Tests: `Lod.Core.Tests`, `Lod.Generators.Tests`, `Lod.Integration.Tests` (all run without Rhino). Manual checks in Rhino follow [docs/development/grasshopper-smoke-test.md](docs/development/grasshopper-smoke-test.md). Next: S4, floor aggregators (gated on ADR-009).

S0–S4 are executed as described in [docs/plans/2026-10-01-execution-handoff.md](docs/plans/2026-10-01-execution-handoff.md) (D-048, D-049). A verified reference implementation may be unpacked in `.handoff/` (git-ignored); use it only to check results, and never stage anything under it.
```

- [x] **Step 7: Update the README "Status"**

Replace everything between the heading `## Status` and the heading `## What it does` with the following (keep one blank line after the heading and one before `## What it does`):

```markdown
Stage S3 (plan simplifiers and validation) is complete and tagged `v0.3.0`. In Rhino 8 the Grasshopper plugin simplifies the linear plan to any zoning level from Z0 to Z3 (no simplification, semantic merge, perimeter/core, one zone per floor) while keeping every window in place, validates every floor and building against the prescribed conservation invariants, and converts it with *Convert2BEM*, which refuses a model that fails validation unless an override is recorded. The example presets hold illustrative round numbers for testing, not DOE prototype values. The *Convert2BEM* output is provisional until a ClimateStudio reference definition exists (D-023). Next is S4 (floor aggregators) of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md).
```

- [x] **Step 8: Add the S3 progress line to the roadmap**

The roadmap's progress lines live in its header blockquote (convention set by the S0 close-out: `> **Progress:** <date> · <stage> complete (tag …); next: …`, one line per stage, each below the previous stage's). In `docs/plans/2026-09-30-implementation-roadmap.md`, find S2's progress line, the line that starts with

```text
> **Progress:** 2026-10-01 · S2 End-to-end pipeline skeleton complete (tag `v0.2.0`); next: S3.
```

Directly below it, insert the following two lines. The bare `>` line keeps each stage's entry on its own line; the blank blockquote line that already followed the S2 line then follows the S3 line. Use the date on which the stage is closed (this plan assumes 2026-10-01):

```text
>
> **Progress:** 2026-10-01 · S3 Plan simplifiers and validation complete (tag `v0.3.0`); next: S4. Plan simplifiers Z1 semantic merge, Z2 perimeter/core (corner rule in ADR-008), and Z3 single zone per floor keep every window in place (D-039) and require full façade coverage (D-041); floor and building validation, with conditioned floor area reported (D-038) and ground, roof, and exposed floor area and building height enforced (D-045, D-046); the *Convert2BEM* validation gate with a recorded override; 104 core, 17 generator, and 38 integration tests pass on net8.0.
```

Do not change any other roadmap text.

- [x] **Step 9: Decision log**

No further entries: S3's only new decision, D-043 (ADR-008), was recorded in Task 4.

- [x] **Step 10: Commit the documentation with the smoke-test record**

`docs/development/grasshopper-smoke-test.md` ("Recording the result") requires the result of the manual check in the body of the stage close-out commit. Fill the angle-bracket fields with the values written down in Task 11, Step 3; they are records of the manual check, filled at execution time:

```bash
git add AGENTS.md README.md docs/plans/2026-09-30-implementation-roadmap.md
git commit -m "docs(repo): record s3 completion" -m "Smoke test (docs/development/grasshopper-smoke-test.md, S3 checklist) by <tester> on <date>: Rhino <version>, .NET Core runtime, build <sha>, BEMGen Info version '<version text>', all items passed."
```

- [ ] **Step 11: Merge (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only chore/repo-s3-close-out
git push origin main
git branch -d chore/repo-s3-close-out
```

Expected: `VERIFY PASSED`, then `Fast-forward`.

- [ ] **Step 12: Tag**

Only after every exit criterion below is met, including the S3 smoke-test checklist in Rhino 8:

```bash
git tag -a v0.3.0 -m "S3 Plan simplifiers and validation complete"
git push origin v0.3.0
```

## Exit criteria (from the roadmap, refined)

- The linear plan at Z0–Z3 is **validated**: `FloorValidator` passes for `NoSimplification`, `SemanticMerge`, `PerimeterCore` (4.57 m), and `SingleZonePerFloor` on the canonical plan and on nine seeded random plans, including rotated plans and source zones split across several targets (`EverySimplifierSatisfiesTheInvariantsForRandomPlans`, `NoSimplificationPassesValidation`).
- **Previewed**: the S3 smoke-test checklist passes in Rhino 8 (each simplifier on the canonical plan previews with its windows in place, *Validate* shows `PASSED`, *Perimeter Core* with Depth 10 shows the `PlanTooNarrow` error), and its record is in the close-out commit.
- **Converted**: *Stack Floors* → *Convert2BEM* converts each simplified floor, and its `Provenance` output contains the validation report.
- Roadmap tests: mapping and façade attribution including partial coverage (`MappingTests`, `PartialCoverageIsReportedBeforeAnyNormalisation`); window re-hosting with positions kept and windows across two walls rejected (`WindowRehostingTests`, `PerimeterSouthKeepsTheSouthFacadeWindowsInPlace`); every simplifier passes every invariant for seeded random plans; validation catches a changed program and an uncovered façade (`ValidationCatchesAChangedProgram`, `ValidationCatchesAnUncoveredFacade`); conditioned area reported when the unconditioned stair is merged (`MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported`); narrow-plan and invalid-input diagnostics (`PerimeterDepthTooLargeIsAnError`, `NonPositivePerimeterDepthIsAnError`, `FootprintsWithHolesAreNotSupportedYet`); snapshots per simplifier (`CanonicalSnapshots`).
- Test counts: 104 core, 17 generators, 38 integration, on `net8.0`; `scripts/verify.ps1` prints `VERIFY PASSED`.
- ADR-008 accepted and D-043 logged; `docs/architecture/validation.md` written; `docs/architecture/convert2bem.md` documents `Override` and `Provenance`.
- Version 0.3.0; tag `v0.3.0` pushed.

## Notes for the reviewer

1. **Where the test helpers enter.** `SimplifierTests.cs` is built over Tasks 5–9. The `Simplifier(string)` and `RandomParameters` helpers construct all three strategies and are first used by the validation theory, so they enter in Task 8 together with `using Lod.Core.Validation;` (that namespace does not exist before Task 8). The nested `ToleranceComparer` enters in Task 7 with `PerimeterSouthKeepsTheSouthFacadeWindowsInPlace`, its first user. Task 5 adds the constant `PerimeterDepth` and the usings `System.Collections.Generic` and `Lod.Core.Geometry`, which are first used in Task 7. All intermediate states in this plan were built and run from `stage-build\S2`; the error lines and counts stated per step are the observed ones. After D-045 to D-047 the verified S3 state was rebuilt and its tests rerun (104 core, 17 generators, 38 integration); the core counts include the two tests that D-047 adds in S1.
2. **Untested paths.** No automated test triggers `DisconnectedGroup`, `Building.Reference`, or the blocked and overridden paths of `Convert2BEM`; the linear generator cannot produce these cases and Grasshopper code is not unit-testable. In S3 every building comes from `Stack`, which equals its own reference, so `Building.ExposedFloorArea` and `Building.Height` cannot fail yet; they guard S4's `FloorAreaMultiplier` (D-045, D-046). The `FacadeNotCovered` and `WindowNotHosted` errors are tested where they arise (`FacadeAttribution.CoverageGaps`, `WindowRehosting`, the `FacadeCoverage` check) but never reached through `PlanSimplifier.Simplify`, because the three strategies always tile the footprint.
3. **ADR-008 beyond the stage references.** Besides moving holes and typologies to S8, ADR-008 replaces the superseded window references (D-022, D-025) with D-039 and D-041 in its context, decision item 8, and consequences, and cites D-038 for conditioning; the corner rule itself is unchanged.
4. **Decision number.** D-043 is reserved for ADR-008 (S0 appends D-042, S4 D-044). Task 4, Step 3 asks to check that it is still free.
5. **Anchors taken from the S2 plan.** The `convert2bem.md` edits quote the revised S2 text (S2 Task 9, Step 4): the *Building* input row, the paragraph below the input table, the heading `## Zone order and tree paths`, and the row starting `| 14 | Internal Mass | IM |`. The S3 checklist uses the levels S0 and S2 set (`###` under `## Stage checklists`, `####` subsections). The close-out follows the S2 conventions: version and status in separate `build` and `docs` commits, the smoke-test record in the `docs` commit body, and the progress line below S2's after a bare `>` line.
6. **Determinism detail.** `TransferMatrix.SourcesOf` and the sums in `FacadeAttribution` enumerate `Dictionary` entries, whose order is insertion order in practice on .NET but not a documented guarantee. `SourcesOf` is used only by a test, and the façade sums affect only floating-point summation order; window order is fixed by `WallSurface`, which sorts windows by offset. The determinism and snapshot tests pass on `net8.0`.
7. **Traceability depth.** The `Traceability` check confirms that aggregation records exist; it does not recompute their weights. The `Scheduled.*` detail names the hour with the largest difference, which can change with floating-point noise even when the check passes; it is not snapshotted.
8. **Override semantics.** GLOBAL.md scientific rule 6 allows an explicit, recorded override. Here the override is a Grasshopper input whose use is recorded in the `Provenance` output text (not in the building object), which satisfies that rule.
9. **`net48` dropped (D-053).** BEMGen dropped the `net48` target after S0 (ADR-001, D-053): the plugin targets `net7.0` only and the tests `net8.0` only. Test counts are unchanged and the code is unchanged; only the expected outputs, which no longer list `net48`, changed.
10. **Intermediate core counts corrected during execution.** Tasks 1 and 2 expected 95 and 99 core tests, figures computed from an earlier S2 end count of 92. S2 ends at 94 core tests (S2 file map, roadmap), so Task 1 ends at 97 and Task 2 at 101; Task 3's 104 and the stage total were already right.
