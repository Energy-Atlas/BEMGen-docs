# S2 — End-to-end pipeline skeleton Implementation Plan

> **Status:** Done · **Date:** 2026-10-01 · **Roadmap:** [S2](2026-09-30-implementation-roadmap.md) · **Checkpoint:** 1 (S0–S4, D-030)
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the whole pipeline in Grasshopper for the simplest case (example presets → linear plan → no simplification → stacked floors → *Convert2BEM*), previewed at every step, with all core behaviour proven by tests that run without Rhino.

**Architecture:** Polygon geometry (over Clipper2), the pipeline model (zones, surfaces, provenance, plan/floor/building interfaces), the layout surface builder, the plan generator base, `NoSimplification`, and `Stack` live in `Lod.Core`; the linear plan generator lives in the new `Lod.Generators` project. They are tested by `Lod.Core.Tests` and the new `Lod.Generators.Tests` and `Lod.Integration.Tests`. `Lod.Grasshopper` adds Goo wrappers with previews, hidden parameters, Rhino geometry conversion, one thin component per pipeline step, *Inspect*, and a provisional, neutral *Convert2BEM* (D-023).

**Tech Stack:** C# 12 (`LangVersion` 12.0); .NET SDK ≥ 8 (`global.json` pins 8.0.100 with `rollForward: latestMajor`; the development machine has SDK 10 only); `netstandard2.0` for `Lod.Core` and `Lod.Generators`; **Clipper2 2.0.0** (new reference in S2; version already pinned in `Directory.Packages.props` since S0; Boost Software License 1.0, no dependencies); RhinoCommon and Grasshopper 8.19.25132.1001 (`Lod.Grasshopper`, `net7.0`, `ExcludeAssets="runtime"`); xUnit 2.9.3, xunit.runner.visualstudio 3.1.5, Microsoft.NET.Test.Sdk 17.14.1 (test projects `net8.0`); Windows PowerShell 5.1 for `scripts/verify.ps1`.

## Global Constraints

- Code is copied verbatim from this plan. Do not rename, reformat, re-order, or "improve" it; raise doubts with the reviewer instead.
- Rhino 8 only; pipeline stages exchange typed Grasshopper objects, not JSON (D-003, D-017).
- `Lod.Core` and `Lod.Generators` reference no RhinoCommon/Grasshopper; their tests run with plain `dotnet test`.
- Nullable on, warnings as errors, `.editorconfig` rules enforced in the build; every public member of `Lod.Core` and `Lod.Generators` needs XML docs (CS1591 is an error there).
- No `System.Collections.Immutable` (Rhino 8 ships its own copy): immutable types expose `IReadOnlyList<T>` over private arrays via `Array.AsReadOnly`.
- Numerical tolerances only in `ToleranceSettings` (ADR-004); polygon clipping and vertex matching use `ToleranceSettings.Distance` (1e-6 m, 6 decimals).
- Generation is deterministic. S2 uses no randomness, so the linear generator has no seed parameter.
- Z0 has one zone per dwelling unit; rooms are never modelled (D-009).
- Walls carry explicit windows (offset along the wall, sill, width, height; any number per wall; D-039, ADR-002). The S2 generator's rule: one centered window per outdoor wall, glazed area = the zone preset's WWR × wall area (D-026). `NoSimplification` and `Stack` keep every window unchanged (W0); window transformations W1–W5 are stage S5.
- No property aggregation happens in S2: `NoSimplification` and `Stack` copy zone programs unchanged. Load and setpoint aggregation (ADR-005, ADR-007) is first used by the S3 simplifiers.
- Conditioning comes from the program preset; unconditioned zones have no setpoints (D-038). The example presets condition dwelling units and corridors and leave the stair unconditioned (illustrative choices).
- Expected failures are `Result<T>` values carrying `Diagnostic`s with codes from `DiagnosticCodes`; never reuse or rename a published code.
- Grasshopper components are thin adaptors (GLOBAL.md architecture rule 3); component and parameter GUIDs never change once merged.
- *Convert2BEM* output is provisional and neutral (D-023); there is no simulation in the pipeline (D-016).
- The validation gate in front of *Convert2BEM* (GLOBAL.md scientific rule 6) arrives in S3; the S2 component converts without validation.
- `.gh` example definitions are saved by a person in Rhino 8; agents never write them.
- No CI: `scripts/verify.ps1` must print `VERIFY PASSED` before every merge to `main` (D-005); branches are rebase-merged (D-004).
- Commit messages: `type(scope): imperative summary in lower case`; no agent, model, or tool names, no attribution footers, no `Co-Authored-By` trailers (D-001, D-002).

## Files

| Path | Created / modified | Responsibility | Task |
| --- | --- | --- | --- |
| `src/Lod.Core/Lod.Core.csproj` | Modified | Adds the Clipper2 package reference | 1 |
| `src/Lod.Core/Common/DiagnosticCodes.cs` | Modified | Appends the 7 S2 diagnostic codes | 1 |
| `AGENTS.md` | Verified, unchanged | Architecture table already allows Clipper2 in `Lod.Core` | 1 |
| `src/Lod.Core/Geometry/Polygon2.cs` | Created | `Point2`, `Polygon2` (outer ring + holes, normalised orientation, area) | 1 |
| `src/Lod.Core/Geometry/PolygonOps.cs` | Created | Intersection, union, difference, intersection area over Clipper2 | 1 |
| `src/Lod.Core/Geometry/Orientation.cs` | Created | `OrientationBin`, outward azimuth of a wall, azimuth bins | 1 |
| `src/Lod.Core/Geometry/Window.cs` | Created | Explicit window (offset, sill, size) and the generator's centered placement rule | 1 |
| `tests/Lod.Core.Tests/Geometry/GeometryTests.cs` | Created | 22 geometry tests | 1 |
| `src/Lod.Core/Model/Surfaces.cs` | Created | `BoundaryCondition`, `SurfaceId`, `Surface`, `WallSurface`, `HorizontalKind`, `HorizontalSurface` | 2 |
| `src/Lod.Core/Model/Zone.cs` | Created | `ZonePart`, `Zone` | 2 |
| `src/Lod.Core/Model/Provenance.cs` | Created | Reproducibility record of every pipeline object | 2 |
| `src/Lod.Core/Model/Pipeline.cs` | Created | `IFloorLayout`, `IGeneratedPlan`, `IFloor`, `FloorEntry`, `InternalMass`, `IGeneratedBuilding`, default implementations, `ZoneMapping` | 2 |
| `src/Lod.Core/Layout/LayoutSurfaceBuilder.cs` | Created | Walls, floors, ceilings of a single-storey layout; gap/overlap errors | 3 |
| `src/Lod.Core/Layout/LayoutMeasures.cs` | Created | Zone measures; Z0 window placement by WWR | 3 |
| `tests/Lod.Core.Tests/Layout/LayoutSurfaceBuilderTests.cs` | Created | 7 surface-builder tests | 3 |
| `src/Lod.Core/Plans/PlanGenerator.cs` | Created | `PlanParameters`, `PlannedZone`, `PlanLayout`, `PlanGenerator<T>` | 4 |
| `src/Lod.Core/Model/TextReport.cs` | Created | Deterministic text report for *Inspect* and snapshots | 4 |
| `src/Lod.Generators/Lod.Generators.csproj` | Created | New generator library | 4 |
| `src/Lod.Generators/Linear/LinearPlanGenerator.cs` | Created | `LinearPlanParameters`, `LinearPlanGenerator` | 4 |
| `tests/Shared/Snapshot.cs` | Created | Snapshot assertion linked into test projects | 4 |
| `tests/Lod.Generators.Tests/Lod.Generators.Tests.csproj` | Created | New test project | 4 |
| `tests/Lod.Generators.Tests/Linear/LinearPlanGeneratorTests.cs` | Created | 17 generator tests | 4 |
| `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.txt` | Created | Snapshot of the canonical plan | 4 |
| `src/Lod.Core/Simplification/NoSimplification.cs` | Created | `IPlanSimplifier`, `NoSimplification` | 5 |
| `tests/Lod.Integration.Tests/Lod.Integration.Tests.csproj` | Created | New test project | 5 |
| `tests/Lod.Integration.Tests/Pipeline.cs` | Created | Shared pipeline steps for integration tests | 5 |
| `tests/Lod.Integration.Tests/SkeletonPipelineTests.cs` | Created (5), completed (6) | 9 integration tests | 5, 6 |
| `src/Lod.Core/Buildings/Storeys.cs` | Created | Floor-aggregator input checks, storey placement, floor/ceiling resolution | 6 |
| `src/Lod.Core/Buildings/Stack.cs` | Created | `IFloorAggregator`, `Stack` | 6 |
| `tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.txt` | Created | Snapshot of a two-storey stacked building | 6 |
| `BEMGen.sln` | Modified (via `dotnet sln add`) | Adds the three new projects | 4, 5 |
| `src/Lod.Grasshopper/Convert/RhinoGeometry.cs` | Created | Pipeline geometry → Rhino Breps in model units | 7 |
| `src/Lod.Grasshopper/Goo/BemGoo.cs` | Created | Goo wrappers; previews of plans, floors, buildings | 7 |
| `src/Lod.Grasshopper/Parameters/BemParameters.cs` | Created | Hidden Grasshopper parameters for the Goo types | 7 |
| `src/Lod.Grasshopper/Lod.Grasshopper.csproj` | Modified | Adds the `Lod.Generators` project reference | 8 |
| `src/Lod.Grasshopper/Components/ComponentSupport.cs` | Created | Diagnostics → runtime messages; enum input parsing | 8 |
| `src/Lod.Grasshopper/Components/ProgramComponents.cs` | Created | *Schedule*, *Load*, *Program Preset*, *Example Residential Presets* | 8 |
| `src/Lod.Grasshopper/Components/PipelineComponents.cs` | Created | *Linear Plan Generator*, *No Simplification*, *Stack Floors*, *Inspect* | 8 |
| `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` | Created (S2 version, no validation) | *Convert2BEM* | 9 |
| `docs/architecture/convert2bem.md` | Created | Documentation of the *Convert2BEM* output | 9 |
| `docs/development/grasshopper-smoke-test.md` | Modified | Appends the S2 checklist | 10 |
| `examples/grasshopper/pipeline-skeleton.gh` | Created by a person in Rhino 8 | Example definition of the S2 pipeline | 10 |
| `Directory.Build.props` | Modified | `<Version>` 0.1.0 → 0.2.0 | 11 |
| `AGENTS.md`, `README.md`, `docs/plans/2026-09-30-implementation-roadmap.md` | Modified | Stage bookkeeping ("Project state", "Status", S2 progress line) | 11 |

Test counts after each task (on net8.0):

| After task | `Lod.Core.Tests` | `Lod.Generators.Tests` | `Lod.Integration.Tests` |
| --- | --- | --- | --- |
| Start of S2 | 65 | — | — |
| 1 | 87 | — | — |
| 2 | 87 | — | — |
| 3 | 94 | — | — |
| 4 | 94 | 17 | — |
| 5 | 94 | 17 | 1 |
| 6–11 | 94 | 17 | 9 |

---

## Slice A — `feature/geometry-ops`

### Task 1: Polygons, polygon operations, orientation, and explicit windows

**Files:**
- Modify: `src/Lod.Core/Lod.Core.csproj`
- Modify: `src/Lod.Core/Common/DiagnosticCodes.cs`
- Verify (unchanged): `AGENTS.md` (architecture table)
- Create: `src/Lod.Core/Geometry/Polygon2.cs`
- Create: `src/Lod.Core/Geometry/PolygonOps.cs`
- Create: `src/Lod.Core/Geometry/Orientation.cs`
- Create: `src/Lod.Core/Geometry/Window.cs`
- Test: `tests/Lod.Core.Tests/Geometry/GeometryTests.cs`

**Interfaces:**
- Consumes (S1): `Result<T>`, `Result.Success`, `Result.Failure`, `Diagnostic.Error`, `ToleranceSettings.Default`, `ToleranceSettings.DecimalPrecision`.
- Produces (namespace `Lod.Core.Geometry`):
  - `readonly record struct Point2(double X, double Y)` with `double DistanceTo(Point2 other)`.
  - `sealed class Polygon2`: `IReadOnlyList<Point2> Outer`, `IReadOnlyList<IReadOnlyList<Point2>> Holes`, `double Area`, `IEnumerable<IReadOnlyList<Point2>> Rings`, `static Result<Polygon2> Create(IEnumerable<Point2> outer, IEnumerable<IEnumerable<Point2>>? holes = null)`, `static Polygon2 Rectangle(double minX, double minY, double maxX, double maxY)`, `Polygon2 Translate(double dx, double dy)`, `static double SignedArea(IReadOnlyList<Point2> ring)`.
  - `sealed class PolygonOps` (constructor `PolygonOps(ToleranceSettings tolerances)`): `IReadOnlyList<Polygon2> Intersect(Polygon2 a, Polygon2 b)`, `IReadOnlyList<Polygon2> Union(IEnumerable<Polygon2> polygons)`, `IReadOnlyList<Polygon2> Difference(Polygon2 subject, IEnumerable<Polygon2> clips)`, `double IntersectionArea(Polygon2 a, Polygon2 b)`.
  - `enum OrientationBin { North, East, South, West }`; `static class Orientation`: `double OutwardAzimuth(Point2 start, Point2 end)`, `double Normalise(double degrees)`, `OrientationBin Bin(double trueAzimuth)`.
  - `sealed class Window`: `double Offset`, `double Width`, `double SillHeight`, `double Height`, `double Area`, `static Window At(double offset, double width, double sillHeight, double height)`, `static Window? Centered(double wallLength, double wallHeight, double glazedArea)`, `Window MovedTo(double offset)`.
  - `DiagnosticCodes.DegeneratePolygon`, `OverlappingZones`, `UnmatchedEdge`, `InvalidParameter`, `MissingPreset`, `OrientationMismatch`, `NoFloors`.

**Design (ADR-002, ADR-004, D-039, D-026):**
- `Polygon2` is immutable. `Create` drops consecutive repeated points and a repeated closing point, rejects rings with fewer than three distinct points or zero area (`DegeneratePolygon`), and normalises the outer ring to counter-clockwise and holes to clockwise, so `Area` (the sum of signed ring areas) is the outer area minus the holes.
- `PolygonOps` runs `ClipperD` with the precision `ToleranceSettings.DecimalPrecision` (6 decimals for the 1e-6 m distance tolerance), fill rule `NonZero`, into a `PolyTreeD`, so results keep their hole hierarchy and are snapped to the 1e-6 m grid. A result polygon that `Polygon2.Create` rejects after snapping is dropped. Touching polygons have no intersection.
- Azimuths are degrees clockwise from north. On a counter-clockwise ring the zone lies to the left of each edge, so the outward normal of `start → end` is `(dy, −dx)`; `OutwardAzimuth` returns its plan-frame azimuth. A façade's true azimuth is the plan azimuth plus the plan's `OrientationDegrees`; `Bin` maps it to North [315°, 45°), East [45°, 135°), South [135°, 225°), West [225°, 315°).
- `Window` is an explicit rectangle in a wall (D-039): `Offset` from the wall's start point to the window's near edge along the wall, `SillHeight` above the wall's bottom edge, `Width`, and `Height`. A wall may hold any number of windows. `Window.At` creates one and throws `ArgumentOutOfRangeException` for a negative offset or sill, a non-positive width or height, or an infinite value. `MovedTo` returns the same window at another offset; S3 uses it to re-host source windows on target walls.
- `Window.Centered` is the S2 generator's placement rule (D-039 keeps D-026), not a property of windows in general: it scales the wall rectangle about its centre by `s = √(glazedArea / wallArea)`, giving width `L·s`, height `H·s`, offset `(L − L·s) / 2`, and sill `(H − H·s) / 2`. Zero glazing gives no window (`null`). Glazing that does not fit (≥ wall area) or is negative throws `ArgumentOutOfRangeException`; for the generator this cannot happen, because preset WWR is validated to [0, 1) in S1.

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/geometry-ops main
```

- [x] **Step 2: Write the failing tests** — create `tests/Lod.Core.Tests/Geometry/GeometryTests.cs` (11 facts and two theories with 4 and 7 cases: 22 tests):

```csharp
using System;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Xunit;

namespace Lod.Core.Tests.Geometry;

public sealed class GeometryTests
{
    private readonly PolygonOps _ops = new(ToleranceSettings.Default);

    [Fact]
    public void PolygonNormalisesOrientationAndComputesAreaWithHoles()
    {
        Polygon2 polygon = Polygon2.Create(
            new[] { new Point2(0, 0), new Point2(0, 10), new Point2(10, 10), new Point2(10, 0) },
            new[] { new[] { new Point2(2, 2), new Point2(4, 2), new Point2(4, 4), new Point2(2, 4) } }).Value;

        Assert.True(Polygon2.SignedArea(polygon.Outer) > 0);
        Assert.True(Polygon2.SignedArea(polygon.Holes[0]) < 0);
        Assert.Equal(96.0, polygon.Area, 12);
    }

    [Fact]
    public void PolygonDropsClosingAndRepeatedPoints()
    {
        Polygon2 polygon = Polygon2.Create(new[] { new Point2(0, 0), new Point2(1, 0), new Point2(1, 0), new Point2(1, 1), new Point2(0, 0) }).Value;

        Assert.Equal(3, polygon.Outer.Count);
    }

    [Fact]
    public void PolygonRejectsDegenerateRings()
    {
        Assert.Contains(
            Polygon2.Create(new[] { new Point2(0, 0), new Point2(1, 0), new Point2(2, 0) }).Diagnostics,
            d => d.Code == DiagnosticCodes.DegeneratePolygon);
    }

    [Fact]
    public void IntersectionOfOverlappingRectangles()
    {
        double area = _ops.IntersectionArea(Polygon2.Rectangle(0, 0, 10, 10), Polygon2.Rectangle(5, 5, 15, 15));

        Assert.Equal(25.0, area, 9);
    }

    [Fact]
    public void TouchingRectanglesDoNotIntersect()
    {
        Assert.Empty(_ops.Intersect(Polygon2.Rectangle(0, 0, 10, 10), Polygon2.Rectangle(10, 0, 20, 10)));
    }

    [Fact]
    public void UnionOfAdjacentRectanglesIsOnePolygon()
    {
        Polygon2 union = Assert.Single(_ops.Union(new[] { Polygon2.Rectangle(0, 0, 10, 5), Polygon2.Rectangle(10, 0, 20, 5) }));

        Assert.Equal(100.0, union.Area, 9);
    }

    [Fact]
    public void DifferenceKeepsHoles()
    {
        Polygon2 ring = Assert.Single(_ops.Difference(Polygon2.Rectangle(0, 0, 10, 10), new[] { Polygon2.Rectangle(3, 3, 7, 7) }));

        Assert.Single(ring.Holes);
        Assert.Equal(84.0, ring.Area, 9);
    }

    [Theory]
    [InlineData(0, 0, 10, 0, 180.0)]
    [InlineData(10, 0, 10, 10, 90.0)]
    [InlineData(10, 10, 0, 10, 0.0)]
    [InlineData(0, 10, 0, 0, 270.0)]
    public void OutwardAzimuthOfCounterClockwiseRectangleEdges(double x1, double y1, double x2, double y2, double azimuth)
    {
        Assert.Equal(azimuth, Orientation.OutwardAzimuth(new Point2(x1, y1), new Point2(x2, y2)), 9);
    }

    [Theory]
    [InlineData(0.0, OrientationBin.North)]
    [InlineData(44.9, OrientationBin.North)]
    [InlineData(45.0, OrientationBin.East)]
    [InlineData(180.0, OrientationBin.South)]
    [InlineData(270.0, OrientationBin.West)]
    [InlineData(315.0, OrientationBin.North)]
    [InlineData(-90.0, OrientationBin.West)]
    public void OrientationBins(double azimuth, OrientationBin bin)
    {
        Assert.Equal(bin, Orientation.Bin(azimuth));
    }

    [Fact]
    public void CenteredWindowScalesTheWallRectangle()
    {
        Window window = Window.Centered(10.0, 3.0, 0.25 * 30.0)!;

        Assert.Equal(5.0, window.Width, 12);
        Assert.Equal(1.5, window.Height, 12);
        Assert.Equal(0.75, window.SillHeight, 12);
        Assert.Equal(7.5, window.Area, 12);
    }

    [Fact]
    public void ZeroGlazingHasNoWindow()
    {
        Assert.Null(Window.Centered(10.0, 3.0, 0.0));
    }

    [Fact]
    public void GlazingMustBeSmallerThanTheWall()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => Window.Centered(10.0, 3.0, 30.0));
    }

    [Fact]
    public void TranslateMovesEveryRing()
    {
        Polygon2 moved = Polygon2.Rectangle(0, 0, 1, 1).Translate(2, 3);

        Assert.Equal(2.0, moved.Outer.Min(p => p.X));
        Assert.Equal(3.0, moved.Outer.Min(p => p.Y));
    }
}
```

- [x] **Step 3: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Geometry"
```

Expected: the build fails (paths shortened; each error is reported for net8.0), including:

```text
tests\Lod.Core.Tests\Geometry\GeometryTests.cs(4,16): error CS0234: The type or namespace name 'Geometry' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\Geometry\GeometryTests.cs(11,22): error CS0246: The type or namespace name 'PolygonOps' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Geometry\GeometryTests.cs(90,49): error CS0246: The type or namespace name 'OrientationBin' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 4: Reference Clipper2** — replace `src/Lod.Core/Lod.Core.csproj` with the following. The version (2.0.0) is already pinned in `Directory.Packages.props` (S0), so only the reference is added:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <RootNamespace>Lod.Core</RootNamespace>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Clipper2" />
  </ItemGroup>

</Project>
```

- [x] **Step 5: Confirm that the architecture table allows Clipper2** — `Lod.Core` now depends on a package beyond the BCL (ADR-001 pins it, ADR-002 chooses it). The `AGENTS.md` boundary table already allows this (the row was updated together with the stage plans, before S0), so nothing is edited here; confirm it:

```bash
git grep -n "BCL" AGENTS.md
```

Expected: exactly one line, the `Lod.Core` row of the architecture table, reading

```markdown
| `Lod.Core` | BCL and Clipper2 (polygon clipping, from S2; ADR-001, ADR-002) | RhinoCommon, Grasshopper, UI, exporters |
```

If it still says `BCL only`, stop and raise it with the maintainer: the plans assume the row was committed before S0 started.

- [x] **Step 6: Append the S2 diagnostic codes** — in `src/Lod.Core/Common/DiagnosticCodes.cs`, insert these constants after the last S1 constant (`InvalidMeasures`) and before the closing brace of the class:

```csharp
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
```

- [x] **Step 7: Full file after this task: `src/Lod.Core/Common/DiagnosticCodes.cs`**

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
}
```

- [x] **Step 8: Create `src/Lod.Core/Geometry/Polygon2.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;

namespace Lod.Core.Geometry;

/// <summary>A point in the building-local plan frame, metres. +Y is plan north before the plan's orientation is applied.</summary>
/// <param name="X">X coordinate.</param>
/// <param name="Y">Y coordinate.</param>
public readonly record struct Point2(double X, double Y)
{
    /// <summary>Euclidean distance to another point.</summary>
    /// <param name="other">The other point.</param>
    /// <returns>The distance.</returns>
    public double DistanceTo(Point2 other)
    {
        double dx = other.X - X;
        double dy = other.Y - Y;
        return Math.Sqrt((dx * dx) + (dy * dy));
    }
}

/// <summary>
/// An immutable planar polygon with holes (ADR-002). The outer ring is counter-clockwise, holes are clockwise, and rings are stored open (the first point is not repeated).
/// </summary>
public sealed class Polygon2
{
    private Polygon2(Point2[] outer, Point2[][] holes)
    {
        Outer = Array.AsReadOnly(outer);
        Holes = Array.AsReadOnly(holes.Select(h => (IReadOnlyList<Point2>)Array.AsReadOnly(h)).ToArray());
        Area = SignedArea(outer) + holes.Sum(SignedArea);
    }

    /// <summary>Outer ring, counter-clockwise.</summary>
    public IReadOnlyList<Point2> Outer { get; }

    /// <summary>Hole rings, clockwise.</summary>
    public IReadOnlyList<IReadOnlyList<Point2>> Holes { get; }

    /// <summary>Area of the outer ring minus the holes, m².</summary>
    public double Area { get; }

    /// <summary>All rings: the outer ring first, then the holes.</summary>
    public IEnumerable<IReadOnlyList<Point2>> Rings => new[] { Outer }.Concat(Holes);

    /// <summary>Creates a polygon, normalising ring orientation and dropping repeated points.</summary>
    /// <param name="outer">Outer ring.</param>
    /// <param name="holes">Optional hole rings.</param>
    /// <returns>The polygon, or an error for rings with fewer than three distinct points or zero area.</returns>
    public static Result<Polygon2> Create(IEnumerable<Point2> outer, IEnumerable<IEnumerable<Point2>>? holes = null)
    {
        Point2[]? outerRing = Normalise(outer, counterClockwise: true);
        Point2[]?[] holeRings = (holes ?? Enumerable.Empty<IEnumerable<Point2>>()).Select(h => Normalise(h, counterClockwise: false)).ToArray();
        if (outerRing is null || holeRings.Any(h => h is null))
        {
            return Result.Failure<Polygon2>(Diagnostic.Error(DiagnosticCodes.DegeneratePolygon, "Polygon rings need at least three distinct points and a non-zero area."));
        }

        var polygon = new Polygon2(outerRing, holeRings.Select(h => h!).ToArray());
        return polygon.Area > 0
            ? Result.Success(polygon)
            : Result.Failure<Polygon2>(Diagnostic.Error(DiagnosticCodes.DegeneratePolygon, "Holes cover the whole outer ring."));
    }

    /// <summary>An axis-aligned rectangle.</summary>
    /// <param name="minX">Minimum X.</param>
    /// <param name="minY">Minimum Y.</param>
    /// <param name="maxX">Maximum X, greater than <paramref name="minX"/>.</param>
    /// <param name="maxY">Maximum Y, greater than <paramref name="minY"/>.</param>
    /// <returns>The rectangle.</returns>
    public static Polygon2 Rectangle(double minX, double minY, double maxX, double maxY) =>
        Create(new[] { new Point2(minX, minY), new Point2(maxX, minY), new Point2(maxX, maxY), new Point2(minX, maxY) }).Value;

    /// <summary>The polygon moved by an offset.</summary>
    /// <param name="dx">X offset.</param>
    /// <param name="dy">Y offset.</param>
    /// <returns>The translated polygon.</returns>
    public Polygon2 Translate(double dx, double dy) =>
        new(Outer.Select(p => new Point2(p.X + dx, p.Y + dy)).ToArray(), Holes.Select(h => h.Select(p => new Point2(p.X + dx, p.Y + dy)).ToArray()).ToArray());

    /// <summary>Signed area of a ring; positive when counter-clockwise.</summary>
    /// <param name="ring">An open ring.</param>
    /// <returns>The signed area.</returns>
    public static double SignedArea(IReadOnlyList<Point2> ring)
    {
        double sum = 0.0;
        for (int i = 0; i < ring.Count; i++)
        {
            Point2 a = ring[i];
            Point2 b = ring[(i + 1) % ring.Count];
            sum += (a.X * b.Y) - (b.X * a.Y);
        }

        return sum / 2.0;
    }

    private static Point2[]? Normalise(IEnumerable<Point2> ring, bool counterClockwise)
    {
        var points = new List<Point2>();
        foreach (Point2 p in ring)
        {
            if (points.Count == 0 || points[points.Count - 1] != p)
            {
                points.Add(p);
            }
        }

        if (points.Count > 1 && points[0] == points[points.Count - 1])
        {
            points.RemoveAt(points.Count - 1);
        }

        if (points.Count < 3)
        {
            return null;
        }

        double area = SignedArea(points);
        if (area == 0)
        {
            return null;
        }

        if ((area > 0) != counterClockwise)
        {
            points.Reverse();
        }

        return points.ToArray();
    }
}
```

- [x] **Step 9: Create `src/Lod.Core/Geometry/PolygonOps.cs`**

```csharp
using System.Collections.Generic;
using System.Linq;
using Clipper2Lib;
using Lod.Core.Common;

namespace Lod.Core.Geometry;

/// <summary>
/// Polygon boolean operations on Clipper2 (ADR-002). Results are snapped to the <see cref="ToleranceSettings.Distance"/> grid.
/// </summary>
public sealed class PolygonOps
{
    private readonly int _precision;

    /// <summary>Creates the operations with the clipping precision of <paramref name="tolerances"/>.</summary>
    /// <param name="tolerances">Tolerances; <see cref="ToleranceSettings.DecimalPrecision"/> sets the snapping grid.</param>
    public PolygonOps(ToleranceSettings tolerances)
    {
        _precision = tolerances.DecimalPrecision;
    }

    /// <summary>Intersection of two polygons.</summary>
    /// <param name="a">First polygon.</param>
    /// <param name="b">Second polygon.</param>
    /// <returns>Zero or more polygons.</returns>
    public IReadOnlyList<Polygon2> Intersect(Polygon2 a, Polygon2 b) => Execute(ClipType.Intersection, new[] { a }, new[] { b });

    /// <summary>Union of polygons.</summary>
    /// <param name="polygons">Polygons to merge.</param>
    /// <returns>Disjoint polygons covering the union.</returns>
    public IReadOnlyList<Polygon2> Union(IEnumerable<Polygon2> polygons) => Execute(ClipType.Union, polygons, Enumerable.Empty<Polygon2>());

    /// <summary>Part of <paramref name="subject"/> not covered by <paramref name="clips"/>.</summary>
    /// <param name="subject">Polygon to cut.</param>
    /// <param name="clips">Polygons to remove.</param>
    /// <returns>Zero or more polygons.</returns>
    public IReadOnlyList<Polygon2> Difference(Polygon2 subject, IEnumerable<Polygon2> clips) => Execute(ClipType.Difference, new[] { subject }, clips);

    /// <summary>Area of the intersection of two polygons.</summary>
    /// <param name="a">First polygon.</param>
    /// <param name="b">Second polygon.</param>
    /// <returns>Overlap area, m².</returns>
    public double IntersectionArea(Polygon2 a, Polygon2 b) => Intersect(a, b).Sum(p => p.Area);

    private IReadOnlyList<Polygon2> Execute(ClipType clipType, IEnumerable<Polygon2> subjects, IEnumerable<Polygon2> clips)
    {
        var clipper = new ClipperD(_precision);
        clipper.AddSubject(ToPaths(subjects));
        clipper.AddClip(ToPaths(clips));
        var tree = new PolyTreeD();
        clipper.Execute(clipType, FillRule.NonZero, tree);
        var result = new List<Polygon2>();
        Collect(tree, result);
        return result;
    }

    private static PathsD ToPaths(IEnumerable<Polygon2> polygons)
    {
        var paths = new PathsD();
        foreach (IReadOnlyList<Point2> ring in polygons.SelectMany(p => p.Rings))
        {
            var path = new PathD(ring.Count);
            path.AddRange(ring.Select(p => new PointD(p.X, p.Y)));
            paths.Add(path);
        }

        return paths;
    }

    private static void Collect(PolyPathD parent, List<Polygon2> result)
    {
        for (int i = 0; i < parent.Count; i++)
        {
            PolyPathD outer = parent[i];
            var holes = new List<IEnumerable<Point2>>();
            for (int j = 0; j < outer.Count; j++)
            {
                PolyPathD hole = outer[j];
                holes.Add(ToPoints(hole.Polygon!));
                Collect(hole, result);
            }

            Result<Polygon2> polygon = Polygon2.Create(ToPoints(outer.Polygon!), holes);
            if (polygon.IsSuccess)
            {
                result.Add(polygon.Value);
            }
        }
    }

    private static IEnumerable<Point2> ToPoints(PathD path) => path.Select(p => new Point2(p.x, p.y));
}
```

- [x] **Step 10: Create `src/Lod.Core/Geometry/Orientation.cs`**

```csharp
using System;

namespace Lod.Core.Geometry;

/// <summary>Façade orientation bin of an exterior wall.</summary>
public enum OrientationBin
{
    /// <summary>Azimuth in [315°, 45°).</summary>
    North,

    /// <summary>Azimuth in [45°, 135°).</summary>
    East,

    /// <summary>Azimuth in [135°, 225°).</summary>
    South,

    /// <summary>Azimuth in [225°, 315°).</summary>
    West,
}

/// <summary>Azimuth helpers. Azimuths are degrees clockwise from north, in [0, 360).</summary>
public static class Orientation
{
    /// <summary>Azimuth of the outward normal of a wall running from <paramref name="start"/> to <paramref name="end"/> on a counter-clockwise ring, in the plan frame.</summary>
    /// <param name="start">Wall start.</param>
    /// <param name="end">Wall end.</param>
    /// <returns>Plan-frame azimuth, degrees.</returns>
    public static double OutwardAzimuth(Point2 start, Point2 end)
    {
        double nx = end.Y - start.Y;
        double ny = -(end.X - start.X);
        return Normalise(Math.Atan2(nx, ny) * 180.0 / Math.PI);
    }

    /// <summary>Normalises an angle to [0, 360).</summary>
    /// <param name="degrees">Angle in degrees.</param>
    /// <returns>The equivalent angle in [0, 360).</returns>
    public static double Normalise(double degrees)
    {
        double value = degrees % 360.0;
        return value < 0 ? value + 360.0 : value;
    }

    /// <summary>The orientation bin of a true azimuth.</summary>
    /// <param name="trueAzimuth">Azimuth in degrees clockwise from true north.</param>
    /// <returns>The bin.</returns>
    public static OrientationBin Bin(double trueAzimuth)
    {
        double a = Normalise(trueAzimuth);
        if (a >= 45.0 && a < 135.0)
        {
            return OrientationBin.East;
        }

        if (a >= 135.0 && a < 225.0)
        {
            return OrientationBin.South;
        }

        if (a >= 225.0 && a < 315.0)
        {
            return OrientationBin.West;
        }

        return OrientationBin.North;
    }
}
```

- [x] **Step 11: Create `src/Lod.Core/Geometry/Window.cs`**

```csharp
using System;

namespace Lod.Core.Geometry;

/// <summary>
/// An explicit rectangular window in a wall (D-039): its position along the wall, its sill height above the wall's bottom edge, and its size.
/// </summary>
public sealed class Window
{
    private Window(double offset, double width, double sillHeight, double height)
    {
        Offset = offset;
        Width = width;
        SillHeight = sillHeight;
        Height = height;
    }

    /// <summary>Distance from the wall's start point to the window's near edge, along the wall, m.</summary>
    public double Offset { get; }

    /// <summary>Window width along the wall, m.</summary>
    public double Width { get; }

    /// <summary>Height of the window's bottom edge above the wall's bottom edge, m.</summary>
    public double SillHeight { get; }

    /// <summary>Window height, m.</summary>
    public double Height { get; }

    /// <summary>Glazed area, m².</summary>
    public double Area => Width * Height;

    /// <summary>A window at an explicit position.</summary>
    /// <param name="offset">Distance from the wall start to the near edge, m; not negative.</param>
    /// <param name="width">Width, m; positive.</param>
    /// <param name="sillHeight">Sill height above the wall's bottom edge, m; not negative.</param>
    /// <param name="height">Height, m; positive.</param>
    /// <returns>The window.</returns>
    /// <exception cref="ArgumentOutOfRangeException">A dimension is out of range.</exception>
    public static Window At(double offset, double width, double sillHeight, double height)
    {
        if (!(offset >= 0) || !(sillHeight >= 0) || !(width > 0) || !(height > 0) || double.IsInfinity(width + height + offset + sillHeight))
        {
            throw new ArgumentOutOfRangeException(nameof(width), $"Invalid window: offset {offset}, width {width}, sill {sillHeight}, height {height}.");
        }

        return new Window(offset, width, sillHeight, height);
    }

    /// <summary>
    /// The window centered on a wall with a given glazed area: the wall rectangle scaled about its centre by √(glazed area / wall area); <c>null</c>
    /// for zero glazing. This is the S2 generator's placement rule (D-039), not a property of windows in general.
    /// </summary>
    /// <param name="wallLength">Wall length, m.</param>
    /// <param name="wallHeight">Wall height, m.</param>
    /// <param name="glazedArea">Glazed area, m²; must be less than the wall area.</param>
    /// <returns>The window or <c>null</c>.</returns>
    /// <exception cref="ArgumentOutOfRangeException">The glazed area is negative or does not fit the wall.</exception>
    public static Window? Centered(double wallLength, double wallHeight, double glazedArea)
    {
        double wallArea = wallLength * wallHeight;
        if (glazedArea < 0 || glazedArea >= wallArea)
        {
            throw new ArgumentOutOfRangeException(nameof(glazedArea), glazedArea, $"Glazed area must be in [0, {wallArea}).");
        }

        if (glazedArea == 0)
        {
            return null;
        }

        double scale = Math.Sqrt(glazedArea / wallArea);
        double width = wallLength * scale;
        double height = wallHeight * scale;
        return new Window((wallLength - width) / 2.0, width, (wallHeight - height) / 2.0, height);
    }

    /// <summary>The same window at another position along a wall.</summary>
    /// <param name="offset">New offset, m.</param>
    /// <returns>The moved window.</returns>
    public Window MovedTo(double offset) => At(offset, Width, SillHeight, Height);
}
```

- [x] **Step 12: Run the geometry tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Geometry"
```

Expected:

```text
Passed!  - Failed:     0, Passed:    22, Skipped:     0, Total:    22, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 13: Build the solution and run all tests**

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release --no-build
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`, then:

```text
Passed!  - Failed:     0, Passed:    87, Skipped:     0, Total:    87, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 14: Commit**

```bash
git add src/Lod.Core/Lod.Core.csproj src/Lod.Core/Common/DiagnosticCodes.cs src/Lod.Core/Geometry tests/Lod.Core.Tests/Geometry
git commit -m "feature(core): add polygon operations, orientation bins, and explicit windows"
```

- [x] **Step 15: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/geometry-ops
git push origin main
git branch -d feature/geometry-ops
```

Expected from `verify.ps1`: `Passed!` with 87 tests for `Lod.Core.Tests.dll` on net8.0, then `VERIFY PASSED`.

---

## Slice B — `feature/plans-model`

Roadmap slice 2: the pipeline model types (Task 2) and the layout surface builder (Task 3), which the plan generator in Slice C needs.

### Task 2: Pipeline model types (build-only)

**Files:**
- Create: `src/Lod.Core/Model/Surfaces.cs`
- Create: `src/Lod.Core/Model/Zone.cs`
- Create: `src/Lod.Core/Model/Provenance.cs`
- Create: `src/Lod.Core/Model/Pipeline.cs`

**Interfaces:**
- Consumes: `ZoneId` (S1, `Lod.Core.Common`), `SpaceType`, `ZoneProgram` with its optional `Thermostat` (S1, `Lod.Core.Programs`; D-038), `BuildInfo.InformationalVersion` (S0), `Point2`, `Polygon2`, `Window`, `Orientation` (Task 1).
- Produces (namespace `Lod.Core.Model`):
  - `enum BoundaryCondition { Outdoors, Ground, Adiabatic, Interzone, Unresolved }`; `readonly record struct SurfaceId(string Value)`.
  - `abstract class Surface`: `SurfaceId Id`, `ZoneId Zone`, `BoundaryCondition Boundary`, `ZoneId? AdjacentZone`, `abstract double Area`; the constructor throws `ArgumentException` unless `AdjacentZone` is set exactly for `Interzone`.
  - `sealed class WallSurface : Surface`: `WallSurface(SurfaceId id, ZoneId zone, Point2 start, Point2 end, double elevation, double height, BoundaryCondition boundary, ZoneId? adjacentZone, IEnumerable<Window> windows)`; `Point2 Start`, `Point2 End`, `double Elevation`, `double Height`, `IReadOnlyList<Window> Windows` (ordered by offset), `double Length`, `double GlazedArea` (sum over the windows), `double PlanAzimuth`, `WallSurface WithWindows(IEnumerable<Window> windows)`, `WallSurface Relocate(Func<ZoneId, ZoneId> rename, string idPrefix, double dz)`.
  - `enum HorizontalKind { Floor, Ceiling }`; `sealed class HorizontalSurface : Surface`: `HorizontalSurface(SurfaceId id, ZoneId zone, HorizontalKind kind, Polygon2 polygon, double elevation, BoundaryCondition boundary, ZoneId? adjacentZone)`; `Kind`, `Polygon`, `Elevation`.
  - `sealed record ZonePart(Polygon2 Footprint, double Elevation, double Height)` with `double Volume`.
  - `sealed class Zone`: `Zone(ZoneId id, string name, SpaceType spaceType, IEnumerable<ZonePart> parts, ZoneProgram program, IEnumerable<ZoneId> sourceZones, int multiplier = 1)`; `Id`, `Name`, `SpaceType`, `Parts`, `Program`, `SourceZones`, `Multiplier`, `FloorArea`, `Volume`, `Zone Relocate(ZoneId id, double dz, int multiplier)`.
  - `sealed class Provenance`: `Operation`, `Parameters` (ordered by key), `Inputs`, `CodeVersion`, `static Provenance Of(string operation, IEnumerable<KeyValuePair<string, string>> parameters, params Provenance[] inputs)`, `static string Format(double value)`, `string Describe()`.
  - `interface IFloorLayout` (`Footprint`, `FloorHeight`, `OrientationDegrees`, `Zones`, `Surfaces`, `Provenance`); `interface IGeneratedPlan : IFloorLayout`; `interface IFloor : IFloorLayout` (`IGeneratedPlan Source`, `IReadOnlyList<ZoneMapping> Mapping`); `sealed record FloorEntry(IFloor Floor, int Multiplier)`; `sealed record InternalMass(ZoneId Zone, double SlabArea, int ExposedFaces, double Elevation, IReadOnlyList<SurfaceId> SourceSurfaces)`; `interface IGeneratedBuilding` (`OrientationDegrees`, `Zones`, `Surfaces`, `InternalMasses`, `Sources`, `Provenance`); `GeneratedPlan`, `Floor`, `GeneratedBuilding` default implementations; `sealed record ZoneMapping(ZoneId Source, ZoneId Target, double OverlapArea, double SourceFraction, double TargetFraction)`.

**Design:**
- **Pipeline vocabulary (D-018).** A generator produces an `IGeneratedPlan`, a plan simplifier an `IFloor`, a floor aggregator an `IGeneratedBuilding`. Plans and floors share `IFloorLayout`: one storey in plan coordinates at elevation 0, whose floors and ceilings are `Unresolved` until a floor aggregator stacks them. A floor keeps its source plan and the source-to-target `ZoneMapping`; a building keeps its `FloorEntry` sources (bottom to top, each with a multiplier).
- **Immutability.** Every type is immutable: get-only properties, collections exposed as `IReadOnlyList<T>` over private arrays (`Array.AsReadOnly`), and copies instead of mutation (`WallSurface.WithWindows`, `WallSurface.Relocate`, `Zone.Relocate`). No dependency on `System.Collections.Immutable`, because Rhino 8 ships its own copy and a second version loaded by the plugin could conflict with it.
- **Surfaces.** `WallSurface` is a vertical rectangle on a plan segment with the zone to the left of `Start → End`, so `PlanAzimuth` is its outward azimuth; it carries any number of explicit windows, kept ordered by offset, and its `GlazedArea` is their total area (D-039). `HorizontalSurface` is a floor or ceiling polygon. The base constructor enforces that an adjacent zone is given for, and only for, `Interzone` surfaces. There is no separate roof condition: a roof is an `Outdoors` ceiling.
- **Zones.** A zone has an ID, a display name, a `SpaceType`, one or more `ZonePart` prisms, its `ZoneProgram`, the IDs of the zones it was derived from (traceability, GLOBAL.md scientific rule 2; empty for generated zones), and a multiplier ≥ 1. Multi-part zones exist only for `SingleZoneMerged` (S4, D-021), which merges all storeys into one zone with one part per storey; every other zone has exactly one part.
- **Provenance.** Each pipeline object records the operation, its parameters as invariant-culture text ordered by key, the provenance of its inputs, and `BuildInfo.InformationalVersion` (version plus commit SHA), so any building can be traced back to the generator call that produced it (roadmap §3, reproducibility).
- **Defined now for later stages.** `InternalMass` (D-031) is part of `IGeneratedBuilding` from the start so the interface stays stable; `Stack` produces none, `SingleZoneMerged` (S4) fills it, and *Convert2BEM* outputs it. `ZoneMapping` is needed now for the identity mapping of `NoSimplification` (Task 5); S3's transfer matrix produces real overlaps.

**Why build-only:** these files are data definitions with only constructor guards and copy helpers. They are exercised by the tests of Task 3 (surfaces), Task 4 (zones, provenance, `GeneratedPlan`), and Tasks 5–6 (`Floor`, `ZoneMapping`, `FloorEntry`, `GeneratedBuilding`). `InternalMass` is first produced in S4.

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/plans-model main
```

- [x] **Step 2: Create `src/Lod.Core/Model/Surfaces.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;

namespace Lod.Core.Model;

/// <summary>What is on the other side of a surface.</summary>
public enum BoundaryCondition
{
    /// <summary>Outdoor air.</summary>
    Outdoors,

    /// <summary>Ground contact.</summary>
    Ground,

    /// <summary>No heat transfer.</summary>
    Adiabatic,

    /// <summary>Another zone, given by <see cref="Surface.AdjacentZone"/>.</summary>
    Interzone,

    /// <summary>Floor or ceiling of a plan or floor that has not been stacked yet.</summary>
    Unresolved,
}

/// <summary>Identifies a surface.</summary>
/// <param name="Value">The identifier text.</param>
public readonly record struct SurfaceId(string Value)
{
    /// <inheritdoc />
    public override string ToString() => Value;
}

/// <summary>A planar surface bounding a zone.</summary>
public abstract class Surface
{
    /// <summary>Initialises the common properties.</summary>
    /// <param name="id">Surface ID.</param>
    /// <param name="zone">Zone the surface belongs to.</param>
    /// <param name="boundary">Boundary condition.</param>
    /// <param name="adjacentZone">Zone on the other side; required for <see cref="BoundaryCondition.Interzone"/>, otherwise <c>null</c>.</param>
    protected Surface(SurfaceId id, ZoneId zone, BoundaryCondition boundary, ZoneId? adjacentZone)
    {
        if ((boundary == BoundaryCondition.Interzone) != adjacentZone.HasValue)
        {
            throw new ArgumentException("An adjacent zone is required for, and only for, interzone surfaces.", nameof(adjacentZone));
        }

        Id = id;
        Zone = zone;
        Boundary = boundary;
        AdjacentZone = adjacentZone;
    }

    /// <summary>Surface ID.</summary>
    public SurfaceId Id { get; }

    /// <summary>Zone the surface belongs to.</summary>
    public ZoneId Zone { get; }

    /// <summary>Boundary condition.</summary>
    public BoundaryCondition Boundary { get; }

    /// <summary>Zone on the other side of an interzone surface.</summary>
    public ZoneId? AdjacentZone { get; }

    /// <summary>Gross area, m².</summary>
    public abstract double Area { get; }
}

/// <summary>A vertical rectangular wall from <see cref="Start"/> to <see cref="End"/>; the zone lies to the left of that direction.</summary>
public sealed class WallSurface : Surface
{
    /// <summary>Creates a wall.</summary>
    /// <param name="id">Surface ID.</param>
    /// <param name="zone">Owning zone.</param>
    /// <param name="start">Start point in plan.</param>
    /// <param name="end">End point in plan.</param>
    /// <param name="elevation">Bottom edge elevation, m.</param>
    /// <param name="height">Wall height, m.</param>
    /// <param name="boundary">Boundary condition.</param>
    /// <param name="adjacentZone">Zone on the other side of an interzone wall.</param>
    /// <param name="windows">Explicit windows in this wall, ordered by offset (D-039).</param>
    public WallSurface(SurfaceId id, ZoneId zone, Point2 start, Point2 end, double elevation, double height, BoundaryCondition boundary, ZoneId? adjacentZone, IEnumerable<Window> windows)
        : base(id, zone, boundary, adjacentZone)
    {
        Start = start;
        End = end;
        Elevation = elevation;
        Height = height;
        Windows = Array.AsReadOnly(windows.OrderBy(w => w.Offset).ToArray());
    }

    /// <summary>Start point in plan.</summary>
    public Point2 Start { get; }

    /// <summary>End point in plan.</summary>
    public Point2 End { get; }

    /// <summary>Bottom edge elevation, m.</summary>
    public double Elevation { get; }

    /// <summary>Wall height, m.</summary>
    public double Height { get; }

    /// <summary>Explicit windows, ordered by offset.</summary>
    public IReadOnlyList<Window> Windows { get; }

    /// <summary>Wall length, m.</summary>
    public double Length => Start.DistanceTo(End);

    /// <inheritdoc />
    public override double Area => Length * Height;

    /// <summary>Glazed area of all windows, m².</summary>
    public double GlazedArea => Windows.Sum(w => w.Area);

    /// <summary>Plan-frame azimuth of the outward normal, degrees.</summary>
    public double PlanAzimuth => Orientation.OutwardAzimuth(Start, End);

    /// <summary>A copy with different windows.</summary>
    /// <param name="windows">The new windows.</param>
    /// <returns>The copy.</returns>
    public WallSurface WithWindows(IEnumerable<Window> windows) => new(Id, Zone, Start, End, Elevation, Height, Boundary, AdjacentZone, windows);

    /// <summary>A copy placed at another elevation with re-keyed IDs.</summary>
    /// <param name="rename">Maps old zone IDs to new ones.</param>
    /// <param name="idPrefix">Prefix for the surface ID.</param>
    /// <param name="dz">Elevation offset, m.</param>
    /// <returns>The copy.</returns>
    public WallSurface Relocate(Func<ZoneId, ZoneId> rename, string idPrefix, double dz) =>
        new(new SurfaceId(idPrefix + Id.Value), rename(Zone), Start, End, Elevation + dz, Height, Boundary, AdjacentZone.HasValue ? rename(AdjacentZone.Value) : null, Windows);
}

/// <summary>Whether a horizontal surface is a zone's floor or ceiling.</summary>
public enum HorizontalKind
{
    /// <summary>Floor; faces down.</summary>
    Floor,

    /// <summary>Ceiling or roof; faces up.</summary>
    Ceiling,
}

/// <summary>A horizontal floor or ceiling polygon.</summary>
public sealed class HorizontalSurface : Surface
{
    /// <summary>Creates a horizontal surface.</summary>
    /// <param name="id">Surface ID.</param>
    /// <param name="zone">Owning zone.</param>
    /// <param name="kind">Floor or ceiling.</param>
    /// <param name="polygon">Plan polygon.</param>
    /// <param name="elevation">Elevation, m.</param>
    /// <param name="boundary">Boundary condition.</param>
    /// <param name="adjacentZone">Zone on the other side of an interzone surface.</param>
    public HorizontalSurface(SurfaceId id, ZoneId zone, HorizontalKind kind, Polygon2 polygon, double elevation, BoundaryCondition boundary, ZoneId? adjacentZone)
        : base(id, zone, boundary, adjacentZone)
    {
        Kind = kind;
        Polygon = polygon;
        Elevation = elevation;
    }

    /// <summary>Floor or ceiling.</summary>
    public HorizontalKind Kind { get; }

    /// <summary>Plan polygon.</summary>
    public Polygon2 Polygon { get; }

    /// <summary>Elevation, m.</summary>
    public double Elevation { get; }

    /// <inheritdoc />
    public override double Area => Polygon.Area;
}
```

- [x] **Step 3: Create `src/Lod.Core/Model/Zone.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Programs;

namespace Lod.Core.Model;

/// <summary>One prism of a zone: a floor polygon extruded by a height.</summary>
/// <param name="Footprint">Floor polygon.</param>
/// <param name="Elevation">Floor elevation, m.</param>
/// <param name="Height">Floor-to-floor height, m.</param>
public sealed record ZonePart(Polygon2 Footprint, double Elevation, double Height)
{
    /// <summary>Air volume, m³.</summary>
    public double Volume => Footprint.Area * Height;
}

/// <summary>
/// A thermal zone. Most zones have one part; a zone spanning storeys (<c>SingleZoneMerged</c>) has one part per storey.
/// </summary>
public sealed class Zone
{
    /// <summary>Creates a zone.</summary>
    /// <param name="id">Zone ID.</param>
    /// <param name="name">Display name.</param>
    /// <param name="spaceType">Space type; <see cref="SpaceType.Mixed"/> for zones combining several types.</param>
    /// <param name="parts">One or more prisms.</param>
    /// <param name="program">Loads and setpoints.</param>
    /// <param name="sourceZones">Zones this zone was derived from; empty for generated zones.</param>
    /// <param name="multiplier">Zone multiplier, at least 1.</param>
    public Zone(ZoneId id, string name, SpaceType spaceType, IEnumerable<ZonePart> parts, ZoneProgram program, IEnumerable<ZoneId> sourceZones, int multiplier = 1)
    {
        ZonePart[] partArray = parts.ToArray();
        if (partArray.Length == 0)
        {
            throw new ArgumentException("A zone needs at least one part.", nameof(parts));
        }

        if (multiplier < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(multiplier), multiplier, "Multipliers start at 1.");
        }

        Id = id;
        Name = name;
        SpaceType = spaceType;
        Parts = Array.AsReadOnly(partArray);
        Program = program;
        SourceZones = Array.AsReadOnly(sourceZones.ToArray());
        Multiplier = multiplier;
    }

    /// <summary>Zone ID.</summary>
    public ZoneId Id { get; }

    /// <summary>Display name.</summary>
    public string Name { get; }

    /// <summary>Space type.</summary>
    public SpaceType SpaceType { get; }

    /// <summary>Prisms making up the zone.</summary>
    public IReadOnlyList<ZonePart> Parts { get; }

    /// <summary>Loads and setpoints.</summary>
    public ZoneProgram Program { get; }

    /// <summary>Zones this zone was derived from.</summary>
    public IReadOnlyList<ZoneId> SourceZones { get; }

    /// <summary>Zone multiplier.</summary>
    public int Multiplier { get; }

    /// <summary>Floor area of one instance, m².</summary>
    public double FloorArea => Parts.Sum(p => p.Footprint.Area);

    /// <summary>Volume of one instance, m³.</summary>
    public double Volume => Parts.Sum(p => p.Volume);

    /// <summary>A copy with a new ID, translated vertically, with another multiplier.</summary>
    /// <param name="id">New ID.</param>
    /// <param name="dz">Elevation offset, m.</param>
    /// <param name="multiplier">New multiplier.</param>
    /// <returns>The copy.</returns>
    public Zone Relocate(ZoneId id, double dz, int multiplier) =>
        new(id, Name, SpaceType, Parts.Select(p => p with { Elevation = p.Elevation + dz }), Program, SourceZones, multiplier);
}
```

- [x] **Step 4: Create `src/Lod.Core/Model/Provenance.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Lod.Core.Common;

namespace Lod.Core.Model;

/// <summary>
/// Reproducibility record (brief §18): the operation that produced an object, its parameters, the provenance of its inputs, and the code version.
/// </summary>
public sealed class Provenance
{
    private Provenance(string operation, KeyValuePair<string, string>[] parameters, Provenance[] inputs, string codeVersion)
    {
        Operation = operation;
        Parameters = Array.AsReadOnly(parameters);
        Inputs = Array.AsReadOnly(inputs);
        CodeVersion = codeVersion;
    }

    /// <summary>Operation name, e.g. <c>LinearPlanGenerator</c>.</summary>
    public string Operation { get; }

    /// <summary>Parameters, ordered by key.</summary>
    public IReadOnlyList<KeyValuePair<string, string>> Parameters { get; }

    /// <summary>Provenance of the inputs.</summary>
    public IReadOnlyList<Provenance> Inputs { get; }

    /// <summary>The <see cref="BuildInfo.InformationalVersion"/> of the code that ran the operation.</summary>
    public string CodeVersion { get; }

    /// <summary>Records an operation.</summary>
    /// <param name="operation">Operation name.</param>
    /// <param name="parameters">Parameters as invariant-culture text.</param>
    /// <param name="inputs">Provenance of the inputs.</param>
    /// <returns>The record.</returns>
    public static Provenance Of(string operation, IEnumerable<KeyValuePair<string, string>> parameters, params Provenance[] inputs) =>
        new(operation, parameters.OrderBy(p => p.Key, StringComparer.Ordinal).ToArray(), inputs, BuildInfo.InformationalVersion);

    /// <summary>Formats a number for a parameter value: invariant culture, round-trippable.</summary>
    /// <param name="value">The number.</param>
    /// <returns>The text.</returns>
    public static string Format(double value) => value.ToString("R", CultureInfo.InvariantCulture);

    /// <summary>Indented multi-line description.</summary>
    /// <returns>The text.</returns>
    public string Describe()
    {
        var builder = new StringBuilder();
        Append(builder, 0);
        return builder.ToString();
    }

    private void Append(StringBuilder builder, int depth)
    {
        builder.Append(' ', depth * 2).Append(Operation);
        foreach (KeyValuePair<string, string> parameter in Parameters)
        {
            builder.Append(' ').Append(parameter.Key).Append('=').Append(parameter.Value);
        }

        builder.Append(" [").Append(CodeVersion).Append("]\n");
        foreach (Provenance input in Inputs)
        {
            input.Append(builder, depth + 1);
        }
    }
}
```

- [x] **Step 5: Create `src/Lod.Core/Model/Pipeline.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;

namespace Lod.Core.Model;

/// <summary>A single-storey zoned layout in plan coordinates; floors and ceilings are <see cref="BoundaryCondition.Unresolved"/>.</summary>
public interface IFloorLayout
{
    /// <summary>Plan boundary.</summary>
    public Polygon2 Footprint { get; }

    /// <summary>Floor-to-floor height, m.</summary>
    public double FloorHeight { get; }

    /// <summary>Clockwise rotation of plan north from true north, degrees.</summary>
    public double OrientationDegrees { get; }

    /// <summary>Zones at elevation 0.</summary>
    public IReadOnlyList<Zone> Zones { get; }

    /// <summary>Walls, floors, and ceilings of the zones.</summary>
    public IReadOnlyList<Surface> Surfaces { get; }

    /// <summary>How the layout was produced.</summary>
    public Provenance Provenance { get; }
}

/// <summary>A detailed plan from a plan generator: one zone per dwelling unit (Z0, D-009).</summary>
public interface IGeneratedPlan : IFloorLayout
{
}

/// <summary>A plan after a plan simplifier, with its source and the source-to-target mapping.</summary>
public interface IFloor : IFloorLayout
{
    /// <summary>The detailed plan this floor was derived from.</summary>
    public IGeneratedPlan Source { get; }

    /// <summary>Source-to-target zone overlaps.</summary>
    public IReadOnlyList<ZoneMapping> Mapping { get; }
}

/// <summary>A floor used by a floor aggregator, with the number of storeys it stands for.</summary>
/// <param name="Floor">The floor.</param>
/// <param name="Multiplier">Number of storeys, at least 1.</param>
public sealed record FloorEntry(IFloor Floor, int Multiplier);

/// <summary>Internal mass of a zone (D-031): a slab whose both faces lie inside the same zone.</summary>
/// <param name="Zone">Owning zone.</param>
/// <param name="SlabArea">Area of the slab, m² (one face).</param>
/// <param name="ExposedFaces">Number of slab faces exposed to the zone air.</param>
/// <param name="Elevation">Slab elevation, m.</param>
/// <param name="SourceSurfaces">The floor and ceiling surfaces the slab replaces.</param>
public sealed record InternalMass(ZoneId Zone, double SlabArea, int ExposedFaces, double Elevation, IReadOnlyList<SurfaceId> SourceSurfaces);

/// <summary>A building from a floor aggregator.</summary>
public interface IGeneratedBuilding
{
    /// <summary>Clockwise rotation of plan north from true north, degrees.</summary>
    public double OrientationDegrees { get; }

    /// <summary>Zones at their final elevations.</summary>
    public IReadOnlyList<Zone> Zones { get; }

    /// <summary>All surfaces with resolved boundary conditions.</summary>
    public IReadOnlyList<Surface> Surfaces { get; }

    /// <summary>Internal mass objects.</summary>
    public IReadOnlyList<InternalMass> InternalMasses { get; }

    /// <summary>The floors the building was aggregated from, bottom to top.</summary>
    public IReadOnlyList<FloorEntry> Sources { get; }

    /// <summary>How the building was produced.</summary>
    public Provenance Provenance { get; }
}

/// <summary>Default implementation of <see cref="IGeneratedPlan"/>.</summary>
public sealed class GeneratedPlan : IGeneratedPlan
{
    /// <summary>Creates a plan.</summary>
    /// <param name="footprint">Plan boundary.</param>
    /// <param name="floorHeight">Floor-to-floor height, m.</param>
    /// <param name="orientationDegrees">Plan orientation, degrees.</param>
    /// <param name="zones">Zones.</param>
    /// <param name="surfaces">Surfaces.</param>
    /// <param name="provenance">Provenance.</param>
    public GeneratedPlan(Polygon2 footprint, double floorHeight, double orientationDegrees, IEnumerable<Zone> zones, IEnumerable<Surface> surfaces, Provenance provenance)
    {
        Footprint = footprint;
        FloorHeight = floorHeight;
        OrientationDegrees = orientationDegrees;
        Zones = Array.AsReadOnly(zones.ToArray());
        Surfaces = Array.AsReadOnly(surfaces.ToArray());
        Provenance = provenance;
    }

    /// <inheritdoc />
    public Polygon2 Footprint { get; }

    /// <inheritdoc />
    public double FloorHeight { get; }

    /// <inheritdoc />
    public double OrientationDegrees { get; }

    /// <inheritdoc />
    public IReadOnlyList<Zone> Zones { get; }

    /// <inheritdoc />
    public IReadOnlyList<Surface> Surfaces { get; }

    /// <inheritdoc />
    public Provenance Provenance { get; }
}

/// <summary>Default implementation of <see cref="IFloor"/>.</summary>
public sealed class Floor : IFloor
{
    /// <summary>Creates a floor.</summary>
    /// <param name="source">Source plan.</param>
    /// <param name="zones">Zones.</param>
    /// <param name="surfaces">Surfaces.</param>
    /// <param name="mapping">Source-to-target mapping.</param>
    /// <param name="provenance">Provenance.</param>
    public Floor(IGeneratedPlan source, IEnumerable<Zone> zones, IEnumerable<Surface> surfaces, IEnumerable<ZoneMapping> mapping, Provenance provenance)
    {
        Source = source;
        Zones = Array.AsReadOnly(zones.ToArray());
        Surfaces = Array.AsReadOnly(surfaces.ToArray());
        Mapping = Array.AsReadOnly(mapping.ToArray());
        Provenance = provenance;
    }

    /// <inheritdoc />
    public IGeneratedPlan Source { get; }

    /// <inheritdoc />
    public Polygon2 Footprint => Source.Footprint;

    /// <inheritdoc />
    public double FloorHeight => Source.FloorHeight;

    /// <inheritdoc />
    public double OrientationDegrees => Source.OrientationDegrees;

    /// <inheritdoc />
    public IReadOnlyList<Zone> Zones { get; }

    /// <inheritdoc />
    public IReadOnlyList<Surface> Surfaces { get; }

    /// <inheritdoc />
    public IReadOnlyList<ZoneMapping> Mapping { get; }

    /// <inheritdoc />
    public Provenance Provenance { get; }
}

/// <summary>Default implementation of <see cref="IGeneratedBuilding"/>.</summary>
public sealed class GeneratedBuilding : IGeneratedBuilding
{
    /// <summary>Creates a building.</summary>
    /// <param name="orientationDegrees">Orientation, degrees.</param>
    /// <param name="zones">Zones.</param>
    /// <param name="surfaces">Surfaces.</param>
    /// <param name="internalMasses">Internal mass objects.</param>
    /// <param name="sources">Source floors, bottom to top.</param>
    /// <param name="provenance">Provenance.</param>
    public GeneratedBuilding(double orientationDegrees, IEnumerable<Zone> zones, IEnumerable<Surface> surfaces, IEnumerable<InternalMass> internalMasses, IEnumerable<FloorEntry> sources, Provenance provenance)
    {
        OrientationDegrees = orientationDegrees;
        Zones = Array.AsReadOnly(zones.ToArray());
        Surfaces = Array.AsReadOnly(surfaces.ToArray());
        InternalMasses = Array.AsReadOnly(internalMasses.ToArray());
        Sources = Array.AsReadOnly(sources.ToArray());
        Provenance = provenance;
    }

    /// <inheritdoc />
    public double OrientationDegrees { get; }

    /// <inheritdoc />
    public IReadOnlyList<Zone> Zones { get; }

    /// <inheritdoc />
    public IReadOnlyList<Surface> Surfaces { get; }

    /// <inheritdoc />
    public IReadOnlyList<InternalMass> InternalMasses { get; }

    /// <inheritdoc />
    public IReadOnlyList<FloorEntry> Sources { get; }

    /// <inheritdoc />
    public Provenance Provenance { get; }
}

/// <summary>Overlap between a source zone and a target zone (spec §11).</summary>
/// <param name="Source">Source zone.</param>
/// <param name="Target">Target zone.</param>
/// <param name="OverlapArea">Intersection area, m².</param>
/// <param name="SourceFraction">Overlap as a fraction of the source zone's area.</param>
/// <param name="TargetFraction">Overlap as a fraction of the target zone's area.</param>
public sealed record ZoneMapping(ZoneId Source, ZoneId Target, double OverlapArea, double SourceFraction, double TargetFraction);
```

- [x] **Step 6: Build and run the core tests**

```bash
dotnet build src/Lod.Core -c Release
dotnet test tests/Lod.Core.Tests -c Release
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)` (a missing XML doc comment would fail here with CS1591), then:

```text
Passed!  - Failed:     0, Passed:    87, Skipped:     0, Total:    87, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Model
git commit -m "feature(core): add zone, surface, provenance, and pipeline model types"
```

### Task 3: Layout surface builder and Z0 window placement

**Files:**
- Create: `src/Lod.Core/Layout/LayoutSurfaceBuilder.cs`
- Create: `src/Lod.Core/Layout/LayoutMeasures.cs`
- Test: `tests/Lod.Core.Tests/Layout/LayoutSurfaceBuilderTests.cs`

**Interfaces:**
- Consumes: Task 1 geometry, Task 2 model types, `ZoneMeasures` (S1, `Lod.Core.Aggregation`), `ToleranceSettings.Distance` and `Angle`.
- Produces (namespace `Lod.Core.Layout`):
  - `sealed record LayoutZone(ZoneId Id, Polygon2 Footprint)`.
  - `sealed class LayoutSurfaceBuilder` (constructor `LayoutSurfaceBuilder(ToleranceSettings tolerances)`) with `Result<IReadOnlyList<Surface>> Build(Polygon2 footprint, IReadOnlyList<LayoutZone> zones, double height)`. Surface IDs: walls `{zone}/W{n}` (n from 1 per zone), floor `{zone}/F`, ceiling `{zone}/C`.
  - `static class LayoutMeasures`: `ZoneMeasures Of(Zone zone, IEnumerable<Surface> surfaces)`, `double ExteriorWallArea(ZoneId zone, IEnumerable<Surface> surfaces)`, `IReadOnlyList<Surface> PlaceWindowsByRatio(IEnumerable<Surface> surfaces, Func<ZoneId, double> windowToWallRatio)`.

**Algorithm of `LayoutSurfaceBuilder.Build`:**
1. **Grid snapping.** Every vertex of the footprint and of every zone ring is registered on a grid whose cell is `ToleranceSettings.Distance` (1e-6 m): the key is each coordinate divided by the cell and rounded half away from zero. The first original point registered in a cell is kept and used for output coordinates, so vertices closer than the tolerance are the same vertex.
2. **Splitting.** Each edge `a → b` of each zone ring is split at every registered vertex that lies within one grid unit of the edge's line and strictly between its end points (by more than half a grid unit), giving directed segments `(zone, ring, A, B)`. A long edge touched by two neighbours (a T-junction) therefore becomes two segments.
3. **Pairing and classification.** Segments are grouped by direction. The same directed segment used by two zones means they overlap: `OverlappingZones` error. A segment whose reverse `B → A` exists belongs to two adjacent zones: `Interzone`, adjacent to the zone owning the reverse. A segment whose two end points lie on one edge of the footprint (within one grid unit) is on the plan boundary: `Outdoors`. Anything else is a gap or partial overlap: `UnmatchedEdge` error. Any error fails the build with all diagnostics.
4. **Merging collinear runs.** Per zone and ring, consecutive segments merge into one wall when they connect, have the same boundary and adjacent zone, and are collinear and same-directed (cosine > 0, |sine| ≤ sin(`ToleranceSettings.Angle`)). The walk starts at a segment that cannot merge with its predecessor, so a run never wraps around the ring start. Walls are never merged across zones or across different neighbours. `CollinearPiecesOfOneEdgeMergeIntoOneWall` covers this step: the footprint has an extra vertex halfway along the north edge, which splits the zone's north edge in step 2, and the two outdoor pieces merge back into one wall.
5. **Output.** Per zone, in input order: its walls (`{zone}/W1`, `W2`, … in ring order, outer ring first; elevation 0; the given height; no windows), then one floor `{zone}/F` at elevation 0 and one ceiling `{zone}/C` at elevation `height`, both `Unresolved` with the zone footprint as polygon.

`LayoutMeasures.PlaceWindowsByRatio` is the S2 generator's window rule (D-039, D-026): every `Outdoors` wall gets exactly one window, `Window.Centered(length, height, WWR × wall area)` with its zone's WWR (none when the WWR is 0); interzone walls and horizontal surfaces are unchanged. `LayoutMeasures.Of` and `ExteriorWallArea` give the `ZoneMeasures` (floor area, volume, gross outdoor wall area including windows) that S3's aggregation uses (ADR-007).

- [x] **Step 1: Write the failing tests** — create `tests/Lod.Core.Tests/Layout/LayoutSurfaceBuilderTests.cs` (7 tests):

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Model;
using Xunit;

namespace Lod.Core.Tests.Layout;

public sealed class LayoutSurfaceBuilderTests
{
    private readonly LayoutSurfaceBuilder _builder = new(ToleranceSettings.Default);

    [Fact]
    public void SingleZoneHasFourOutdoorWallsAndUnresolvedFloorAndCeiling()
    {
        IReadOnlyList<Surface> surfaces = Build(Polygon2.Rectangle(0, 0, 10, 5), Zone("A", 0, 0, 10, 5)).Value;

        WallSurface[] walls = surfaces.OfType<WallSurface>().ToArray();
        Assert.Equal(4, walls.Length);
        Assert.All(walls, w => Assert.Equal(BoundaryCondition.Outdoors, w.Boundary));
        Assert.Equal(30.0 * 3.0, walls.Sum(w => w.Area), 9);
        HorizontalSurface[] horizontal = surfaces.OfType<HorizontalSurface>().ToArray();
        Assert.Equal(new[] { HorizontalKind.Floor, HorizontalKind.Ceiling }, horizontal.Select(h => h.Kind));
        Assert.All(horizontal, h => Assert.Equal(BoundaryCondition.Unresolved, h.Boundary));
        Assert.Equal(3.0, horizontal[1].Elevation);
    }

    [Fact]
    public void SharedEdgeBecomesAPairOfInterzoneWalls()
    {
        IReadOnlyList<Surface> surfaces = Build(Polygon2.Rectangle(0, 0, 20, 5), Zone("A", 0, 0, 10, 5), Zone("B", 10, 0, 20, 5)).Value;

        WallSurface ab = surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "A" && w.Boundary == BoundaryCondition.Interzone);
        WallSurface ba = surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "B" && w.Boundary == BoundaryCondition.Interzone);
        Assert.Equal("B", ab.AdjacentZone!.Value.Value);
        Assert.Equal("A", ba.AdjacentZone!.Value.Value);
        Assert.Equal(ab.Start, ba.End);
        Assert.Equal(ab.End, ba.Start);
    }

    [Fact]
    public void EdgesAreSplitWhereAnotherZoneTouchesThem()
    {
        // A long zone above two short ones: its south edge is shared with both.
        IReadOnlyList<Surface> surfaces = Build(
            Polygon2.Rectangle(0, 0, 20, 10),
            Zone("TOP", 0, 5, 20, 10),
            Zone("L", 0, 0, 12, 5),
            Zone("R", 12, 0, 20, 5)).Value;

        WallSurface[] shared = surfaces.OfType<WallSurface>().Where(w => w.Zone.Value == "TOP" && w.Boundary == BoundaryCondition.Interzone).ToArray();
        Assert.Equal(2, shared.Length);
        Assert.Equal(new[] { 12.0, 8.0 }.OrderBy(x => x), shared.Select(w => w.Length).OrderBy(x => x));
    }

    [Fact]
    public void CollinearPiecesOfOneEdgeMergeIntoOneWall()
    {
        // The plan boundary has an extra vertex halfway along the north edge, which splits the zone's edge; the pieces merge back.
        Polygon2 footprint = Polygon2.Create(new[] { new Point2(0, 0), new Point2(20, 0), new Point2(20, 5), new Point2(10, 5), new Point2(0, 5) }).Value;

        IReadOnlyList<Surface> surfaces = Build(footprint, Zone("A", 0, 0, 20, 5)).Value;

        WallSurface[] walls = surfaces.OfType<WallSurface>().ToArray();
        Assert.Equal(4, walls.Length);
        Assert.Contains(walls, w => w.Start == new Point2(20, 5) && w.End == new Point2(0, 5));
    }

    [Fact]
    public void GapsAreErrors()
    {
        Result<IReadOnlyList<Surface>> result = Build(Polygon2.Rectangle(0, 0, 20, 5), Zone("A", 0, 0, 9, 5), Zone("B", 10, 0, 20, 5));

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.UnmatchedEdge);
    }

    [Fact]
    public void OverlapsAreErrors()
    {
        Result<IReadOnlyList<Surface>> result = Build(Polygon2.Rectangle(0, 0, 10, 5), Zone("A", 0, 0, 10, 5), Zone("B", 0, 0, 10, 5));

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.OverlappingZones);
    }

    [Fact]
    public void WindowsAreSizedByEachZonesRatio()
    {
        IReadOnlyList<Surface> surfaces = LayoutMeasures.PlaceWindowsByRatio(
            Build(Polygon2.Rectangle(0, 0, 20, 5), Zone("A", 0, 0, 10, 5), Zone("B", 10, 0, 20, 5)).Value,
            id => id.Value == "A" ? 0.5 : 0.1);

        WallSurface[] outdoor = surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors).ToArray();
        Assert.All(outdoor, w => Assert.Equal((w.Zone.Value == "A" ? 0.5 : 0.1) * w.Area, w.GlazedArea, 9));
        Assert.All(surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Interzone), w => Assert.Empty(w.Windows));
    }

    private static LayoutZone Zone(string id, double x0, double y0, double x1, double y1) => new(new ZoneId(id), Polygon2.Rectangle(x0, y0, x1, y1));

    private Result<IReadOnlyList<Surface>> Build(Polygon2 footprint, params LayoutZone[] zones) => _builder.Build(footprint, zones, 3.0);
}
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Layout"
```

Expected: the build fails, including:

```text
tests\Lod.Core.Tests\Layout\LayoutSurfaceBuilderTests.cs(5,16): error CS0234: The type or namespace name 'Layout' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Core.Tests\Layout\LayoutSurfaceBuilderTests.cs(13,22): error CS0246: The type or namespace name 'LayoutSurfaceBuilder' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Core.Tests\Layout\LayoutSurfaceBuilderTests.cs(101,20): error CS0246: The type or namespace name 'LayoutZone' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Create `src/Lod.Core/Layout/LayoutSurfaceBuilder.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Layout;

/// <summary>A zone footprint to build surfaces for.</summary>
/// <param name="Id">Zone ID.</param>
/// <param name="Footprint">Zone floor polygon.</param>
public sealed record LayoutZone(ZoneId Id, Polygon2 Footprint);

/// <summary>
/// Builds the surfaces of a single-storey layout: walls split wherever another zone's vertex touches them, paired across zones
/// (interzone), or on the plan boundary (outdoors), then merged into maximal collinear runs; plus one unresolved floor and ceiling per zone.
/// Edges that are neither shared nor on the boundary indicate gaps or overlaps and are errors.
/// </summary>
public sealed class LayoutSurfaceBuilder
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the builder.</summary>
    /// <param name="tolerances">Tolerances; <see cref="ToleranceSettings.Distance"/> is the vertex matching grid.</param>
    public LayoutSurfaceBuilder(ToleranceSettings tolerances)
    {
        _tolerances = tolerances;
    }

    /// <summary>Builds walls (without windows), floors, and ceilings.</summary>
    /// <param name="footprint">Plan boundary; walls on it are outdoors.</param>
    /// <param name="zones">Zones tiling the footprint.</param>
    /// <param name="height">Floor-to-floor height, m.</param>
    /// <returns>Surfaces grouped by zone (walls, floor, ceiling), or errors for gaps and overlaps.</returns>
    public Result<IReadOnlyList<Surface>> Build(Polygon2 footprint, IReadOnlyList<LayoutZone> zones, double height)
    {
        var grid = new Grid(_tolerances.Distance);
        foreach (Point2 p in footprint.Rings.SelectMany(r => r).Concat(zones.SelectMany(z => z.Footprint.Rings.SelectMany(r => r))))
        {
            grid.Register(p);
        }

        GridPoint[] vertices = grid.Keys.OrderBy(k => k.X).ThenBy(k => k.Y).ToArray();
        var segments = new List<Segment>();
        for (int zoneIndex = 0; zoneIndex < zones.Count; zoneIndex++)
        {
            int ringIndex = 0;
            foreach (IReadOnlyList<Point2> ring in zones[zoneIndex].Footprint.Rings)
            {
                AddRingSegments(grid, vertices, zoneIndex, ringIndex++, ring, segments);
            }
        }

        var diagnostics = new List<Diagnostic>();
        Classify(grid, footprint, zones, segments, diagnostics);
        if (diagnostics.Count > 0)
        {
            return Result.Failure<IReadOnlyList<Surface>>(diagnostics);
        }

        var surfaces = new List<Surface>();
        for (int zoneIndex = 0; zoneIndex < zones.Count; zoneIndex++)
        {
            LayoutZone zone = zones[zoneIndex];
            int wallNumber = 1;
            foreach (IGrouping<int, Segment> ring in segments.Where(s => s.Zone == zoneIndex).GroupBy(s => s.Ring))
            {
                foreach (List<Segment> run in MergeRuns(ring.ToList()))
                {
                    Segment first = run[0];
                    surfaces.Add(new WallSurface(
                        new SurfaceId($"{zone.Id.Value}/W{wallNumber++}"),
                        zone.Id,
                        grid.Original(first.A),
                        grid.Original(run[run.Count - 1].B),
                        elevation: 0.0,
                        height,
                        first.Boundary,
                        first.Adjacent is int adjacent ? zones[adjacent].Id : null,
                        Array.Empty<Window>()));
                }
            }

            surfaces.Add(new HorizontalSurface(new SurfaceId($"{zone.Id.Value}/F"), zone.Id, HorizontalKind.Floor, zone.Footprint, 0.0, BoundaryCondition.Unresolved, null));
            surfaces.Add(new HorizontalSurface(new SurfaceId($"{zone.Id.Value}/C"), zone.Id, HorizontalKind.Ceiling, zone.Footprint, height, BoundaryCondition.Unresolved, null));
        }

        return Result.Success<IReadOnlyList<Surface>>(surfaces);
    }

    private static void AddRingSegments(Grid grid, GridPoint[] vertices, int zone, int ring, IReadOnlyList<Point2> points, List<Segment> segments)
    {
        for (int i = 0; i < points.Count; i++)
        {
            GridPoint a = grid.Key(points[i]);
            GridPoint b = grid.Key(points[(i + 1) % points.Count]);
            if (a == b)
            {
                continue;
            }

            GridPoint[] cuts = vertices
                .Where(v => v != a && v != b && IsStrictlyInside(a, b, v))
                .OrderBy(v => Parameter(a, b, v))
                .ToArray();
            GridPoint previous = a;
            foreach (GridPoint cut in cuts.Concat(new[] { b }))
            {
                segments.Add(new Segment(zone, ring, previous, cut));
                previous = cut;
            }
        }
    }

    private static void Classify(Grid grid, Polygon2 footprint, IReadOnlyList<LayoutZone> zones, List<Segment> segments, List<Diagnostic> diagnostics)
    {
        var byDirection = segments.GroupBy(s => (s.A, s.B)).ToDictionary(g => g.Key, g => g.ToList());
        GridPoint[][] boundaryRings = footprint.Rings.Select(r => r.Select(grid.Key).ToArray()).ToArray();
        foreach (Segment segment in segments)
        {
            string subject = zones[segment.Zone].Id.Value;
            if (byDirection[(segment.A, segment.B)].Count > 1)
            {
                diagnostics.Add(Diagnostic.Error(DiagnosticCodes.OverlappingZones, $"Edge {Describe(grid, segment)} is used by more than one zone in the same direction.", subject));
                continue;
            }

            if (byDirection.TryGetValue((segment.B, segment.A), out List<Segment>? opposite))
            {
                segment.Boundary = BoundaryCondition.Interzone;
                segment.Adjacent = opposite[0].Zone;
            }
            else if (boundaryRings.Any(ring => OnRing(ring, segment.A, segment.B)))
            {
                segment.Boundary = BoundaryCondition.Outdoors;
            }
            else
            {
                diagnostics.Add(Diagnostic.Error(DiagnosticCodes.UnmatchedEdge, $"Edge {Describe(grid, segment)} is neither shared with another zone nor on the plan boundary (gap or overlap).", subject));
            }
        }
    }

    private IEnumerable<List<Segment>> MergeRuns(List<Segment> ring)
    {
        int start = Enumerable.Range(0, ring.Count).FirstOrDefault(i => !CanMerge(ring[(i + ring.Count - 1) % ring.Count], ring[i]));
        List<Segment>? run = null;
        for (int k = 0; k < ring.Count; k++)
        {
            Segment segment = ring[(start + k) % ring.Count];
            if (run is not null && CanMerge(run[run.Count - 1], segment))
            {
                run.Add(segment);
                continue;
            }

            if (run is not null)
            {
                yield return run;
            }

            run = new List<Segment> { segment };
        }

        if (run is not null)
        {
            yield return run;
        }
    }

    private bool CanMerge(Segment previous, Segment next)
    {
        if (previous.B != next.A || previous.Boundary != next.Boundary || previous.Adjacent != next.Adjacent)
        {
            return false;
        }

        double ax = previous.B.X - previous.A.X;
        double ay = previous.B.Y - previous.A.Y;
        double bx = next.B.X - next.A.X;
        double by = next.B.Y - next.A.Y;
        double lengths = Math.Sqrt((ax * ax) + (ay * ay)) * Math.Sqrt((bx * bx) + (by * by));
        double sine = ((ax * by) - (ay * bx)) / lengths;
        double cosine = ((ax * bx) + (ay * by)) / lengths;
        return cosine > 0 && Math.Abs(sine) <= Math.Sin(_tolerances.Angle);
    }

    private static bool OnRing(GridPoint[] ring, GridPoint a, GridPoint b)
    {
        for (int i = 0; i < ring.Length; i++)
        {
            GridPoint p = ring[i];
            GridPoint q = ring[(i + 1) % ring.Length];
            if (IsOnSegment(p, q, a) && IsOnSegment(p, q, b))
            {
                return true;
            }
        }

        return false;
    }

    private static double Parameter(GridPoint a, GridPoint b, GridPoint p)
    {
        double dx = b.X - a.X;
        double dy = b.Y - a.Y;
        return (((p.X - a.X) * dx) + ((p.Y - a.Y) * dy)) / ((dx * dx) + (dy * dy));
    }

    private static double DistanceToLine(GridPoint a, GridPoint b, GridPoint p)
    {
        double dx = b.X - a.X;
        double dy = b.Y - a.Y;
        return Math.Abs((dx * (p.Y - a.Y)) - (dy * (p.X - a.X))) / Math.Sqrt((dx * dx) + (dy * dy));
    }

    /// <summary>Within one grid unit of the line and strictly between the end points (by more than half a grid unit).</summary>
    private static bool IsStrictlyInside(GridPoint a, GridPoint b, GridPoint p)
    {
        if (DistanceToLine(a, b, p) > 1.0)
        {
            return false;
        }

        double length = Math.Sqrt(Math.Pow(b.X - a.X, 2) + Math.Pow(b.Y - a.Y, 2));
        double along = Parameter(a, b, p) * length;
        return along > 0.5 && along < length - 0.5;
    }

    /// <summary>Within one grid unit of the segment, end points included.</summary>
    private static bool IsOnSegment(GridPoint a, GridPoint b, GridPoint p)
    {
        if (p == a || p == b)
        {
            return true;
        }

        double length = Math.Sqrt(Math.Pow(b.X - a.X, 2) + Math.Pow(b.Y - a.Y, 2));
        double along = Parameter(a, b, p) * length;
        return DistanceToLine(a, b, p) <= 1.0 && along >= -1.0 && along <= length + 1.0;
    }

    private static string Describe(Grid grid, Segment segment)
    {
        Point2 a = grid.Original(segment.A);
        Point2 b = grid.Original(segment.B);
        return $"({a.X:0.###}, {a.Y:0.###})-({b.X:0.###}, {b.Y:0.###})";
    }

    private readonly record struct GridPoint(long X, long Y);

    private sealed class Segment
    {
        public Segment(int zone, int ring, GridPoint a, GridPoint b)
        {
            Zone = zone;
            Ring = ring;
            A = a;
            B = b;
        }

        public int Zone { get; }

        public int Ring { get; }

        public GridPoint A { get; }

        public GridPoint B { get; }

        public BoundaryCondition Boundary { get; set; } = BoundaryCondition.Unresolved;

        public int? Adjacent { get; set; }
    }

    /// <summary>Snaps points to the tolerance grid and remembers the first original point of each grid cell.</summary>
    private sealed class Grid
    {
        private readonly double _cell;
        private readonly Dictionary<GridPoint, Point2> _originals = new();

        public Grid(double cell)
        {
            _cell = cell;
        }

        public IEnumerable<GridPoint> Keys => _originals.Keys;

        public GridPoint Key(Point2 p) => new((long)Math.Round(p.X / _cell, MidpointRounding.AwayFromZero), (long)Math.Round(p.Y / _cell, MidpointRounding.AwayFromZero));

        public void Register(Point2 p)
        {
            GridPoint key = Key(p);
            if (!_originals.ContainsKey(key))
            {
                _originals.Add(key, p);
            }
        }

        public Point2 Original(GridPoint key) => _originals[key];
    }
}
```

- [x] **Step 4: Create `src/Lod.Core/Layout/LayoutMeasures.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Aggregation;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Layout;

/// <summary>Measures and window placement derived from a zone's surfaces.</summary>
public static class LayoutMeasures
{
    /// <summary>Floor area, volume, and outdoor wall area of a zone (one instance, multiplier ignored).</summary>
    /// <param name="zone">The zone.</param>
    /// <param name="surfaces">Surfaces of the layout or building containing the zone.</param>
    /// <returns>The measures.</returns>
    public static ZoneMeasures Of(Zone zone, IEnumerable<Surface> surfaces) =>
        new(zone.FloorArea, zone.Volume, ExteriorWallArea(zone.Id, surfaces));

    /// <summary>Gross area of a zone's outdoor walls, windows included.</summary>
    /// <param name="zone">Zone ID.</param>
    /// <param name="surfaces">Surfaces containing the zone's walls.</param>
    /// <returns>Area, m².</returns>
    public static double ExteriorWallArea(Common.ZoneId zone, IEnumerable<Surface> surfaces) =>
        surfaces.OfType<WallSurface>().Where(w => w.Zone == zone && w.Boundary == BoundaryCondition.Outdoors).Sum(w => w.Area);

    /// <summary>The S2 generator's placement rule (D-039, D-026): one centered window on every outdoor wall, sized by its zone's window-to-wall ratio.</summary>
    /// <param name="surfaces">Surfaces without windows.</param>
    /// <param name="windowToWallRatio">WWR of each zone.</param>
    /// <returns>Surfaces with windows on outdoor walls.</returns>
    public static IReadOnlyList<Surface> PlaceWindowsByRatio(IEnumerable<Surface> surfaces, Func<Common.ZoneId, double> windowToWallRatio) =>
        surfaces
            .Select(s => s is WallSurface { Boundary: BoundaryCondition.Outdoors } wall
                ? wall.WithWindows(Window.Centered(wall.Length, wall.Height, windowToWallRatio(wall.Zone) * wall.Area) is { } window ? new[] { window } : Array.Empty<Window>())
                : s)
            .ToArray();
}
```

- [x] **Step 5: Run the layout tests to verify they pass**

```bash
dotnet test tests/Lod.Core.Tests -c Release --filter "FullyQualifiedName~Lod.Core.Tests.Layout"
```

Expected:

```text
Passed!  - Failed:     0, Passed:     7, Skipped:     0, Total:     7, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 6: Run all core tests**

```bash
dotnet test tests/Lod.Core.Tests -c Release
```

Expected:

```text
Passed!  - Failed:     0, Passed:    94, Skipped:     0, Total:    94, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 7: Commit**

```bash
git add src/Lod.Core/Layout tests/Lod.Core.Tests/Layout
git commit -m "feature(core): build layout surfaces with interzone pairing and z0 windows"
```

- [x] **Step 8: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/plans-model
git push origin main
git branch -d feature/plans-model
```

Expected from `verify.ps1`: `Passed!` with 94 tests for `Lod.Core.Tests.dll` on net8.0, then `VERIFY PASSED`.

---

## Slice C — `feature/generators-linear-plan`

### Task 4: Plan generator base, linear plan generator, and canonical snapshot

**Files:**
- Create: `src/Lod.Core/Plans/PlanGenerator.cs`
- Create: `src/Lod.Core/Model/TextReport.cs`
- Create: `src/Lod.Generators/Lod.Generators.csproj`
- Create: `src/Lod.Generators/Linear/LinearPlanGenerator.cs`
- Create: `tests/Shared/Snapshot.cs`
- Create: `tests/Lod.Generators.Tests/Lod.Generators.Tests.csproj`
- Test: `tests/Lod.Generators.Tests/Linear/LinearPlanGeneratorTests.cs`
- Create: `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.txt`
- Modify: `BEMGen.sln` (via `dotnet sln add`)

**Interfaces:**
- Consumes: Tasks 1–3, `ProgramPresetSet`, `ProgramPreset.WindowToWallRatio`, `ExampleResidentialPresets` (S1).
- Produces:
  - `Lod.Core.Plans`: `abstract record PlanParameters(double FloorHeight, double OrientationDegrees)`; `sealed record PlannedZone(ZoneId Id, string Name, SpaceType SpaceType, Polygon2 Footprint)`; `sealed record PlanLayout(Polygon2 Footprint, IReadOnlyList<PlannedZone> Zones)`; `abstract class PlanGenerator<TParameters> where TParameters : PlanParameters` with `abstract string Name`, `Result<IGeneratedPlan> Generate(TParameters parameters, ProgramPresetSet presets)`, and the protected members `ToleranceSettings Tolerances`, `abstract IEnumerable<Diagnostic> Validate(TParameters)`, `abstract PlanLayout Layout(TParameters)`, `abstract IEnumerable<KeyValuePair<string, string>> Describe(TParameters)`, `static bool IsPositive(double)`.
  - `Lod.Core.Model.TextReport`: `static string Describe(IFloorLayout layout)`, `static string Describe(IGeneratedBuilding building)`, `static string F(double value)`.
  - `Lod.Generators.Linear`: `sealed record LinearPlanParameters(double Length, double UnitDepth, double CorridorWidth, double TargetUnitWidth, double StairLength, double FloorHeight, double OrientationDegrees) : PlanParameters`; `sealed class LinearPlanGenerator : PlanGenerator<LinearPlanParameters>` (constructor `LinearPlanGenerator(ToleranceSettings tolerances)`) with `static int UnitsPerRow(LinearPlanParameters parameters)`.
  - Test helper `Lod.Tests.Shared.Snapshot.Match(string actual, string name)` (internal; linked into each test project that needs it).

**Design:**
- **`PlanGenerator<T>` (spec §5, §6).** A subclass only validates its typology parameters and lays out zones (`PlanLayout`). The base class validates `FloorHeight` (positive, finite) and `OrientationDegrees` (finite) with `InvalidParameter`, assigns each zone the program of the preset for its space type (`MissingPreset`, with the zone ID as subject, when none exists), builds surfaces with `LayoutSurfaceBuilder`, places one centered window per outdoor wall by each preset's WWR (D-039, D-026), and records provenance: the subclass parameters, `FloorHeight`, `OrientationDegrees`, and `Presets` as `SpaceType:Name` pairs. The result is a `GeneratedPlan`; generation is deterministic.
- **Linear plan (deliberately simple; refined in S8, typologies, from the precedent study in S7).** A rectangle `Length` × (2 × `UnitDepth` + `CorridorWidth`). A full-depth stair `ST` of length `StairLength` at the west end; a corridor `CO` running from the stair to the east façade; one row of equal dwelling units on each side of the corridor. Units per row = `(Length − StairLength) / TargetUnitWidth`, rounded half away from zero, at least 1; the actual unit width divides the row evenly. Zone order and IDs: `ST`, `CO`, `US1`…`USn` (south row, west to east), `UN1`…`UNn` (north row, west to east). One zone per dwelling unit (D-009). Parameters must be positive and `Length` must exceed `StairLength` (`InvalidParameter`).
- **`TextReport`.** A deterministic, human-readable description used by *Inspect* and by snapshots: one header line, then per zone its loads (value and annual schedule sum) and either its mean setpoints (conditioned zones) or the line `unconditioned`, then every surface with boundary, adjacent zone, area, and for walls the end points, elevation, façade bin (`Orientation.Bin(PlanAzimuth + orientation)`), glazed area, and each window as `window(offset=… sill=… W×H)`. Numbers use six decimals in invariant culture without negative zero; lines end with `\n`.
- **Snapshots.** `Snapshot.Match` compares the text with `Snapshots/<name>.txt` next to the calling test file (normalising `\r\n` to `\n`). On a mismatch it writes `Snapshots/<name>.received.txt` (git-ignored by the `*.received.*` rule in `.gitignore`) and fails. A person reviews the received file and renames it to accept it; changing a snapshot later requires a commit explaining why the output changed (roadmap §5).

**Canonical configuration** (used by the snapshot and by the integration tests): `Length` 24, `UnitDepth` 8, `CorridorWidth` 2, `TargetUnitWidth` 10, `StairLength` 4, `FloorHeight` 3, `OrientationDegrees` 0. That is a 24 m × 18 m plan with a 4 m stair and two 10 m units per row (round(20 / 10) = 2):

```text
y=18 +----+--------------+--------------+
     |    |     UN1      |     UN2      |
y=10 |    +--------------+--------------+
     | ST |            CO               |
y=8  |    +--------------+--------------+
     |    |     US1      |     US2      |
y=0  +----+--------------+--------------+
     x=0  x=4            x=14           x=24
```

Areas: `ST` 72 m², `CO` 40 m², each unit 80 m², total 432 m². With the example presets each outdoor wall gets one centered window of 0.1 × wall area on the stair, 0.2 × on the corridor's east wall, and 0.3 × on the units' walls; interzone walls have no window. The dwelling units and the corridor are conditioned (21 °C heating, 24 °C cooling); the stair is unconditioned (illustrative presets, D-038).

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/generators-linear-plan main
```

- [x] **Step 2: Create the generator project** — create `src/Lod.Generators/Lod.Generators.csproj`, then add it to the solution:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <RootNamespace>Lod.Generators</RootNamespace>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\Lod.Core\Lod.Core.csproj" />
  </ItemGroup>

</Project>
```

```bash
dotnet sln BEMGen.sln add src/Lod.Generators/Lod.Generators.csproj
```

Expected: ``Project `src\Lod.Generators\Lod.Generators.csproj` added to the solution.``

- [x] **Step 3: Create the shared snapshot helper `tests/Shared/Snapshot.cs`**

```csharp
using System.IO;
using System.Runtime.CompilerServices;
using Xunit;

namespace Lod.Tests.Shared;

/// <summary>
/// Compares text with <c>Snapshots/{name}.txt</c> next to the calling test file. On mismatch it writes <c>{name}.received.txt</c>
/// (git-ignored) and fails; review the received file and rename it to accept the change in a commit that explains why the output changed.
/// </summary>
internal static class Snapshot
{
    public static void Match(string actual, string name, [CallerFilePath] string callerFile = "")
    {
        string directory = Path.Combine(Path.GetDirectoryName(callerFile)!, "Snapshots");
        string expectedPath = Path.Combine(directory, name + ".txt");
        string normalised = Normalise(actual);
        if (File.Exists(expectedPath) && Normalise(File.ReadAllText(expectedPath)) == normalised)
        {
            return;
        }

        Directory.CreateDirectory(directory);
        File.WriteAllText(Path.Combine(directory, name + ".received.txt"), normalised);
        Assert.Fail($"Snapshot '{name}' is missing or differs. Review Snapshots/{name}.received.txt and rename it to {name}.txt to accept.");
    }

    private static string Normalise(string text) => text.Replace("\r\n", "\n");
}
```

- [x] **Step 4: Create the test project** — create `tests/Lod.Generators.Tests/Lod.Generators.Tests.csproj`, then add it to the solution:

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
    <Compile Include="..\Shared\Snapshot.cs" Link="Shared\Snapshot.cs" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\Lod.Generators\Lod.Generators.csproj" />
  </ItemGroup>

</Project>
```

```bash
dotnet sln BEMGen.sln add tests/Lod.Generators.Tests/Lod.Generators.Tests.csproj
```

Expected: ``Project `tests\Lod.Generators.Tests\Lod.Generators.Tests.csproj` added to the solution.``

- [x] **Step 5: Write the failing tests** — create `tests/Lod.Generators.Tests/Linear/LinearPlanGeneratorTests.cs` (10 facts and two theories with 4 and 3 cases: 17 tests):

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Generators.Linear;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Generators.Tests.Linear;

public sealed class LinearPlanGeneratorTests
{
    /// <summary>24 m × 18 m, 4 m stair, two 10 m units per row.</summary>
    public static readonly LinearPlanParameters Canonical = new(
        Length: 24.0,
        UnitDepth: 8.0,
        CorridorWidth: 2.0,
        TargetUnitWidth: 10.0,
        StairLength: 4.0,
        FloorHeight: 3.0,
        OrientationDegrees: 0.0);

    private readonly LinearPlanGenerator _generator = new(ToleranceSettings.Default);

    [Theory]
    [InlineData(10.0, 2)]
    [InlineData(8.0, 3)]
    [InlineData(6.0, 3)]
    [InlineData(100.0, 1)]
    public void UnitsPerRowRoundsHalfAwayFromZero(double targetWidth, int expected)
    {
        Assert.Equal(expected, LinearPlanGenerator.UnitsPerRow(Canonical with { TargetUnitWidth = targetWidth }));
    }

    [Fact]
    public void CanonicalPlanHasStairCorridorAndTwoUnitsPerRow()
    {
        IGeneratedPlan plan = Generate(Canonical);

        Assert.Equal(new[] { "ST", "CO", "US1", "US2", "UN1", "UN2" }, plan.Zones.Select(z => z.Id.Value));
        Assert.Equal(24.0 * 18.0, plan.Footprint.Area, 9);
        Assert.Equal(80.0, plan.Zones.Single(z => z.Id.Value == "US1").FloorArea, 9);
        Assert.All(plan.Zones, z => Assert.Empty(z.SourceZones));
    }

    [Fact]
    public void ZonesTileTheFootprintWithoutOverlap()
    {
        IGeneratedPlan plan = Generate(Canonical with { TargetUnitWidth = 6.0 });
        var ops = new PolygonOps(ToleranceSettings.Default);

        Assert.True(ToleranceSettings.Default.AreaEquals(plan.Footprint.Area, plan.Zones.Sum(z => z.FloorArea)));
        foreach (Zone a in plan.Zones)
        {
            foreach (Zone b in plan.Zones.Where(b => b.Id.Value.CompareTo(a.Id.Value) > 0))
            {
                Assert.Equal(0.0, ops.IntersectionArea(a.Parts[0].Footprint, b.Parts[0].Footprint), 9);
            }
        }
    }

    [Fact]
    public void EveryOutdoorWallHasOneCenteredWindowSizedByItsPreset()
    {
        IGeneratedPlan plan = Generate(Canonical);

        foreach (WallSurface wall in plan.Surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Outdoors))
        {
            Zone zone = plan.Zones.Single(z => z.Id == wall.Zone);
            double ratio = ExampleResidentialPresets.All.Find(zone.SpaceType)!.WindowToWallRatio;
            Window window = Assert.Single(wall.Windows);
            Assert.Equal(ratio * wall.Area, window.Area, 9);
            Assert.Equal((wall.Length - window.Width) / 2.0, window.Offset, 12);
            Assert.Equal((wall.Height - window.Height) / 2.0, window.SillHeight, 12);
        }
    }

    [Fact]
    public void InterzoneWallsComeInMatchingPairs()
    {
        IGeneratedPlan plan = Generate(Canonical with { TargetUnitWidth = 6.0 });
        WallSurface[] interzone = plan.Surfaces.OfType<WallSurface>().Where(w => w.Boundary == BoundaryCondition.Interzone).ToArray();

        Assert.NotEmpty(interzone);
        Assert.All(interzone, w => Assert.Contains(interzone, o => o.Zone == w.AdjacentZone && o.AdjacentZone == w.Zone && o.Start == w.End && o.End == w.Start));
    }

    [Fact]
    public void StairHasThreeOutdoorWallsAndThreeNeighbours()
    {
        IGeneratedPlan plan = Generate(Canonical);
        WallSurface[] stair = plan.Surfaces.OfType<WallSurface>().Where(w => w.Zone.Value == "ST").ToArray();

        Assert.Equal(3, stair.Count(w => w.Boundary == BoundaryCondition.Outdoors));
        Assert.Equal(new[] { "CO", "UN1", "US1" }, stair.Where(w => w.AdjacentZone.HasValue).Select(w => w.AdjacentZone!.Value.Value).OrderBy(x => x));
    }

    [Fact]
    public void OrientationRotatesFacadeBins()
    {
        IGeneratedPlan plan = Generate(Canonical with { OrientationDegrees = 90.0 });
        WallSurface south = plan.Surfaces.OfType<WallSurface>().Single(w => w.Zone.Value == "US1" && w.Boundary == BoundaryCondition.Outdoors);

        Assert.Equal(OrientationBin.West, Orientation.Bin(south.PlanAzimuth + plan.OrientationDegrees));
    }

    [Theory]
    [InlineData(0.0, 8.0, 2.0, 10.0, 4.0)]
    [InlineData(24.0, -1.0, 2.0, 10.0, 4.0)]
    [InlineData(24.0, 8.0, 2.0, 10.0, 24.0)]
    public void InvalidParametersAreErrors(double length, double unitDepth, double corridor, double unitWidth, double stair)
    {
        Result<IGeneratedPlan> result = _generator.Generate(new LinearPlanParameters(length, unitDepth, corridor, unitWidth, stair, 3.0, 0.0), ExampleResidentialPresets.All);

        Assert.False(result.IsSuccess);
        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.InvalidParameter);
    }

    [Fact]
    public void MissingPresetIsAnError()
    {
        ProgramPresetSet onlyUnits = ProgramPresetSet.Create(new[] { ExampleResidentialPresets.DwellingUnit }).Value;

        Result<IGeneratedPlan> result = _generator.Generate(Canonical, onlyUnits);

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.MissingPreset && d.Subject == "ST");
    }

    [Fact]
    public void GenerationIsDeterministic()
    {
        Assert.Equal(TextReport.Describe(Generate(Canonical)), TextReport.Describe(Generate(Canonical)));
    }

    [Fact]
    public void ProvenanceRecordsParametersAndPresets()
    {
        Provenance provenance = Generate(Canonical).Provenance;

        Assert.Equal(nameof(LinearPlanGenerator), provenance.Operation);
        Assert.Contains(provenance.Parameters, p => p.Key == "TargetUnitWidth" && p.Value == "10");
        Assert.Contains(provenance.Parameters, p => p.Key == "Presets" && p.Value.Contains("DwellingUnit:Example Dwelling Unit"));
        Assert.Equal(BuildInfo.InformationalVersion, provenance.CodeVersion);
    }

    [Fact]
    public void CanonicalPlanSnapshot()
    {
        Snapshot.Match(TextReport.Describe(Generate(Canonical)), "linear-plan-canonical");
    }

    private IGeneratedPlan Generate(LinearPlanParameters parameters) => _generator.Generate(parameters, ExampleResidentialPresets.All).Value;
}
```

- [x] **Step 6: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Generators.Tests -c Release
```

Expected: the build fails, including:

```text
tests\Lod.Generators.Tests\Linear\LinearPlanGeneratorTests.cs(6,22): error CS0234: The type or namespace name 'Linear' does not exist in the namespace 'Lod.Generators' (are you missing an assembly reference?)
tests\Lod.Generators.Tests\Linear\LinearPlanGeneratorTests.cs(15,28): error CS0246: The type or namespace name 'LinearPlanParameters' could not be found (are you missing a using directive or an assembly reference?)
tests\Lod.Generators.Tests\Linear\LinearPlanGeneratorTests.cs(24,22): error CS0246: The type or namespace name 'LinearPlanGenerator' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 7: Create `src/Lod.Core/Plans/PlanGenerator.cs`**

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Layout;
using Lod.Core.Model;
using Lod.Core.Programs;

namespace Lod.Core.Plans;

/// <summary>Parameters every plan generator needs. Typology-specific parameters extend this record (spec §6).</summary>
/// <param name="FloorHeight">Floor-to-floor height, m.</param>
/// <param name="OrientationDegrees">Clockwise rotation of plan north from true north, degrees.</param>
public abstract record PlanParameters(double FloorHeight, double OrientationDegrees);

/// <summary>A zone proposed by a generator's layout step.</summary>
/// <param name="Id">Zone ID.</param>
/// <param name="Name">Display name.</param>
/// <param name="SpaceType">Space type; selects the program preset.</param>
/// <param name="Footprint">Zone polygon.</param>
public sealed record PlannedZone(ZoneId Id, string Name, SpaceType SpaceType, Polygon2 Footprint);

/// <summary>The geometric output of a generator's layout step.</summary>
/// <param name="Footprint">Plan boundary.</param>
/// <param name="Zones">Zones tiling the footprint.</param>
public sealed record PlanLayout(Polygon2 Footprint, IReadOnlyList<PlannedZone> Zones);

/// <summary>
/// Base class of plan generators (spec §5). Subclasses only validate their parameters and lay out zones; this class assigns program presets,
/// builds surfaces, places centered windows from each preset's WWR, and records provenance. Generation is deterministic.
/// </summary>
/// <typeparam name="TParameters">The generator's parameter record.</typeparam>
public abstract class PlanGenerator<TParameters>
    where TParameters : PlanParameters
{
    /// <summary>Initialises the generator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    protected PlanGenerator(ToleranceSettings tolerances)
    {
        Tolerances = tolerances;
    }

    /// <summary>Operation name recorded in provenance.</summary>
    public abstract string Name { get; }

    /// <summary>Tolerances.</summary>
    protected ToleranceSettings Tolerances { get; }

    /// <summary>Generates a detailed plan.</summary>
    /// <param name="parameters">Generator parameters.</param>
    /// <param name="presets">Program presets; one is needed for every space type the layout uses.</param>
    /// <returns>The plan, or errors.</returns>
    public Result<IGeneratedPlan> Generate(TParameters parameters, ProgramPresetSet presets)
    {
        var diagnostics = new List<Diagnostic>();
        if (!IsPositive(parameters.FloorHeight))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.InvalidParameter, $"FloorHeight must be positive, got {parameters.FloorHeight}."));
        }

        if (double.IsNaN(parameters.OrientationDegrees) || double.IsInfinity(parameters.OrientationDegrees))
        {
            diagnostics.Add(Diagnostic.Error(DiagnosticCodes.InvalidParameter, $"OrientationDegrees must be finite, got {parameters.OrientationDegrees}."));
        }

        diagnostics.AddRange(Validate(parameters));
        if (diagnostics.Count > 0)
        {
            return Result.Failure<IGeneratedPlan>(diagnostics);
        }

        PlanLayout layout = Layout(parameters);
        var zones = new List<Zone>();
        foreach (PlannedZone planned in layout.Zones)
        {
            ProgramPreset? preset = presets.Find(planned.SpaceType);
            if (preset is null)
            {
                diagnostics.Add(Diagnostic.Error(DiagnosticCodes.MissingPreset, $"No program preset for space type {planned.SpaceType}.", planned.Id.Value));
                continue;
            }

            zones.Add(new Zone(planned.Id, planned.Name, planned.SpaceType, new[] { new ZonePart(planned.Footprint, 0.0, parameters.FloorHeight) }, preset.Program, Enumerable.Empty<ZoneId>()));
        }

        if (diagnostics.Count > 0)
        {
            return Result.Failure<IGeneratedPlan>(diagnostics);
        }

        Result<IReadOnlyList<Surface>> surfaces = new LayoutSurfaceBuilder(Tolerances)
            .Build(layout.Footprint, layout.Zones.Select(z => new LayoutZone(z.Id, z.Footprint)).ToArray(), parameters.FloorHeight);
        if (!surfaces.IsSuccess)
        {
            return Result.Failure<IGeneratedPlan>(surfaces.Diagnostics);
        }

        Dictionary<ZoneId, double> ratios = layout.Zones.ToDictionary(z => z.Id, z => presets.Find(z.SpaceType)!.WindowToWallRatio);
        IReadOnlyList<Surface> withWindows = LayoutMeasures.PlaceWindowsByRatio(surfaces.Value, id => ratios[id]);
        IEnumerable<KeyValuePair<string, string>> recorded = Describe(parameters)
            .Concat(new[]
            {
                new KeyValuePair<string, string>(nameof(PlanParameters.FloorHeight), Provenance.Format(parameters.FloorHeight)),
                new KeyValuePair<string, string>(nameof(PlanParameters.OrientationDegrees), Provenance.Format(parameters.OrientationDegrees)),
                new KeyValuePair<string, string>("Presets", string.Join(";", presets.Presets.Select(p => $"{p.SpaceType}:{p.Name}"))),
            });
        var plan = new GeneratedPlan(layout.Footprint, parameters.FloorHeight, parameters.OrientationDegrees, zones, withWindows, Provenance.Of(Name, recorded));
        return Result.Success<IGeneratedPlan>(plan);
    }

    /// <summary>Checks typology-specific parameters.</summary>
    /// <param name="parameters">Parameters.</param>
    /// <returns>Errors, if any.</returns>
    protected abstract IEnumerable<Diagnostic> Validate(TParameters parameters);

    /// <summary>Lays out zones for valid parameters.</summary>
    /// <param name="parameters">Validated parameters.</param>
    /// <returns>Footprint and zones.</returns>
    protected abstract PlanLayout Layout(TParameters parameters);

    /// <summary>Typology-specific parameters for provenance, as invariant-culture text.</summary>
    /// <param name="parameters">Parameters.</param>
    /// <returns>Key-value pairs.</returns>
    protected abstract IEnumerable<KeyValuePair<string, string>> Describe(TParameters parameters);

    /// <summary>Whether a value is finite and positive.</summary>
    /// <param name="value">The value.</param>
    /// <returns><c>true</c> when positive and finite.</returns>
    protected static bool IsPositive(double value) => value > 0 && !double.IsInfinity(value);
}
```

- [x] **Step 8: Create `src/Lod.Core/Model/TextReport.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Lod.Core.Geometry;
using Lod.Core.Loads;

namespace Lod.Core.Model;

/// <summary>
/// Deterministic, human-readable description of plans, floors, and buildings, used by the Inspect component and by snapshot tests.
/// Schedules are summarised by their annual sum (full-load hours for fractions).
/// </summary>
public static class TextReport
{
    /// <summary>Describes a plan or floor.</summary>
    /// <param name="layout">The layout.</param>
    /// <returns>Multi-line text with <c>\n</c> line endings.</returns>
    public static string Describe(IFloorLayout layout)
    {
        var builder = new StringBuilder();
        builder.Append("footprint area=").Append(F(layout.Footprint.Area))
            .Append(" floorHeight=").Append(F(layout.FloorHeight))
            .Append(" orientation=").Append(F(layout.OrientationDegrees)).Append('\n');
        AppendZones(builder, layout.Zones);
        AppendSurfaces(builder, layout.Surfaces, layout.OrientationDegrees);
        return builder.ToString();
    }

    /// <summary>Describes a building.</summary>
    /// <param name="building">The building.</param>
    /// <returns>Multi-line text with <c>\n</c> line endings.</returns>
    public static string Describe(IGeneratedBuilding building)
    {
        var builder = new StringBuilder();
        builder.Append("building orientation=").Append(F(building.OrientationDegrees))
            .Append(" sources=").Append(string.Join(",", building.Sources.Select(s => s.Multiplier))).Append('\n');
        AppendZones(builder, building.Zones);
        AppendSurfaces(builder, building.Surfaces, building.OrientationDegrees);
        foreach (InternalMass mass in building.InternalMasses)
        {
            builder.Append("mass ").Append(mass.Zone.Value)
                .Append(" area=").Append(F(mass.SlabArea))
                .Append(" faces=").Append(mass.ExposedFaces)
                .Append(" z=").Append(F(mass.Elevation)).Append('\n');
        }

        return builder.ToString();
    }

    /// <summary>Formats a number with six decimals, invariant culture, without negative zero.</summary>
    /// <param name="value">The number.</param>
    /// <returns>The text.</returns>
    public static string F(double value) => (Math.Abs(value) < 5e-7 ? 0.0 : value).ToString("F6", CultureInfo.InvariantCulture);

    private static void AppendZones(StringBuilder builder, IEnumerable<Zone> zones)
    {
        foreach (Zone zone in zones)
        {
            builder.Append("zone ").Append(zone.Id.Value)
                .Append(' ').Append(zone.SpaceType)
                .Append(" \"").Append(zone.Name).Append('"')
                .Append(" area=").Append(F(zone.FloorArea))
                .Append(" volume=").Append(F(zone.Volume))
                .Append(" parts=").Append(zone.Parts.Count)
                .Append(" multiplier=").Append(zone.Multiplier)
                .Append(" sources=[").Append(string.Join(",", zone.SourceZones.Select(s => s.Value))).Append("]\n");
            foreach (LoadDefinition load in zone.Program.Loads)
            {
                builder.Append("  load ").Append(load.Type).Append(' ').Append(load.Basis)
                    .Append(" value=").Append(F(load.Value))
                    .Append(" annual=").Append(F(load.Schedule.Values.Sum())).Append('\n');
            }

            if (zone.Program.Thermostat is { } thermostat)
            {
                builder.Append("  setpoints heatingMean=").Append(F(thermostat.HeatingSetpoint.Values.Average()))
                    .Append(" coolingMean=").Append(F(thermostat.CoolingSetpoint.Values.Average())).Append('\n');
            }
            else
            {
                builder.Append("  unconditioned\n");
            }
        }
    }

    private static void AppendSurfaces(StringBuilder builder, IEnumerable<Surface> surfaces, double orientation)
    {
        foreach (Surface surface in surfaces)
        {
            builder.Append("surface ").Append(surface.Id.Value).Append(' ').Append(surface.Boundary);
            if (surface.AdjacentZone is { } adjacent)
            {
                builder.Append(" adjacent=").Append(adjacent.Value);
            }

            builder.Append(" area=").Append(F(surface.Area));
            if (surface is WallSurface wall)
            {
                builder.Append(" wall (").Append(F(wall.Start.X)).Append(',').Append(F(wall.Start.Y))
                    .Append(")-(").Append(F(wall.End.X)).Append(',').Append(F(wall.End.Y))
                    .Append(") z=").Append(F(wall.Elevation))
                    .Append(" facing=").Append(Orientation.Bin(wall.PlanAzimuth + orientation))
                    .Append(" glazing=").Append(F(wall.GlazedArea));
                foreach (Window window in wall.Windows)
                {
                    builder.Append(" window(offset=").Append(F(window.Offset))
                        .Append(" sill=").Append(F(window.SillHeight))
                        .Append(' ').Append(F(window.Width)).Append('x').Append(F(window.Height)).Append(')');
                }
            }
            else if (surface is HorizontalSurface horizontal)
            {
                builder.Append(' ').Append(horizontal.Kind).Append(" z=").Append(F(horizontal.Elevation));
            }

            builder.Append('\n');
        }
    }
}
```

- [x] **Step 9: Create `src/Lod.Generators/Linear/LinearPlanGenerator.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Lod.Core.Plans;
using Lod.Core.Programs;

namespace Lod.Generators.Linear;

/// <summary>Parameters of the linear block plan.</summary>
/// <param name="Length">Plan length along X, m.</param>
/// <param name="UnitDepth">Depth of each dwelling unit row, m.</param>
/// <param name="CorridorWidth">Corridor width, m.</param>
/// <param name="TargetUnitWidth">Desired unit width; the actual width divides the row evenly, m.</param>
/// <param name="StairLength">Length of the stair at the west end, m.</param>
/// <param name="FloorHeight">Floor-to-floor height, m.</param>
/// <param name="OrientationDegrees">Clockwise rotation of plan north from true north, degrees.</param>
public sealed record LinearPlanParameters(
    double Length,
    double UnitDepth,
    double CorridorWidth,
    double TargetUnitWidth,
    double StairLength,
    double FloorHeight,
    double OrientationDegrees)
    : PlanParameters(FloorHeight, OrientationDegrees);

/// <summary>
/// The simplest linear block (S2): a rectangle with a full-depth stair at the west end and a double-loaded corridor running east to the
/// façade, with one row of equal dwelling units on each side. One zone per dwelling unit (D-009). Refined in S8 (typologies) from the precedent study (S7).
/// </summary>
/// <remarks>
/// Zone IDs: <c>ST</c> stair, <c>CO</c> corridor, <c>US1..USn</c> south units west to east, <c>UN1..UNn</c> north units west to east.
/// </remarks>
public sealed class LinearPlanGenerator : PlanGenerator<LinearPlanParameters>
{
    /// <summary>Creates the generator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public LinearPlanGenerator(ToleranceSettings tolerances)
        : base(tolerances)
    {
    }

    /// <inheritdoc />
    public override string Name => nameof(LinearPlanGenerator);

    /// <summary>Number of units per row: the row length divided by the target width, rounded half away from zero, at least 1.</summary>
    /// <param name="parameters">Parameters.</param>
    /// <returns>Units per row.</returns>
    public static int UnitsPerRow(LinearPlanParameters parameters) =>
        Math.Max(1, (int)Math.Round((parameters.Length - parameters.StairLength) / parameters.TargetUnitWidth, MidpointRounding.AwayFromZero));

    /// <inheritdoc />
    protected override IEnumerable<Diagnostic> Validate(LinearPlanParameters parameters)
    {
        var values = new (string Name, double Value)[]
        {
            (nameof(LinearPlanParameters.Length), parameters.Length),
            (nameof(LinearPlanParameters.UnitDepth), parameters.UnitDepth),
            (nameof(LinearPlanParameters.CorridorWidth), parameters.CorridorWidth),
            (nameof(LinearPlanParameters.TargetUnitWidth), parameters.TargetUnitWidth),
            (nameof(LinearPlanParameters.StairLength), parameters.StairLength),
        };
        foreach ((string name, double value) in values.Where(v => !IsPositive(v.Value)))
        {
            yield return Diagnostic.Error(DiagnosticCodes.InvalidParameter, $"{name} must be positive, got {value}.");
        }

        if (parameters.Length <= parameters.StairLength)
        {
            yield return Diagnostic.Error(DiagnosticCodes.InvalidParameter, $"Length ({parameters.Length}) must exceed StairLength ({parameters.StairLength}).");
        }
    }

    /// <inheritdoc />
    protected override PlanLayout Layout(LinearPlanParameters p)
    {
        int count = UnitsPerRow(p);
        double unitWidth = (p.Length - p.StairLength) / count;
        double[] xs = Enumerable.Range(0, count + 1).Select(i => i == count ? p.Length : p.StairLength + (i * unitWidth)).ToArray();
        double corridorSouth = p.UnitDepth;
        double corridorNorth = p.UnitDepth + p.CorridorWidth;
        double depth = corridorNorth + p.UnitDepth;

        var zones = new List<PlannedZone>
        {
            new(new ZoneId("ST"), "Stair", SpaceType.Stair, Polygon2.Rectangle(0.0, 0.0, p.StairLength, depth)),
            new(new ZoneId("CO"), "Corridor", SpaceType.Corridor, Polygon2.Rectangle(p.StairLength, corridorSouth, p.Length, corridorNorth)),
        };
        for (int i = 0; i < count; i++)
        {
            zones.Add(new PlannedZone(new ZoneId($"US{i + 1}"), $"Unit S{i + 1}", SpaceType.DwellingUnit, Polygon2.Rectangle(xs[i], 0.0, xs[i + 1], corridorSouth)));
        }

        for (int i = 0; i < count; i++)
        {
            zones.Add(new PlannedZone(new ZoneId($"UN{i + 1}"), $"Unit N{i + 1}", SpaceType.DwellingUnit, Polygon2.Rectangle(xs[i], corridorNorth, xs[i + 1], depth)));
        }

        return new PlanLayout(Polygon2.Rectangle(0.0, 0.0, p.Length, depth), zones);
    }

    /// <inheritdoc />
    protected override IEnumerable<KeyValuePair<string, string>> Describe(LinearPlanParameters p) => new[]
    {
        new KeyValuePair<string, string>(nameof(p.Length), Provenance.Format(p.Length)),
        new KeyValuePair<string, string>(nameof(p.UnitDepth), Provenance.Format(p.UnitDepth)),
        new KeyValuePair<string, string>(nameof(p.CorridorWidth), Provenance.Format(p.CorridorWidth)),
        new KeyValuePair<string, string>(nameof(p.TargetUnitWidth), Provenance.Format(p.TargetUnitWidth)),
        new KeyValuePair<string, string>(nameof(p.StairLength), Provenance.Format(p.StairLength)),
    };
}
```

- [x] **Step 10: Run the tests; only the snapshot test fails**

```bash
dotnet test tests/Lod.Generators.Tests -c Release
```

Expected: 16 tests pass; `CanonicalPlanSnapshot` fails on net8.0 because the snapshot does not exist yet, and `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.received.txt` is written:

```text
  Failed Lod.Generators.Tests.Linear.LinearPlanGeneratorTests.CanonicalPlanSnapshot
  Error Message:
   Snapshot 'linear-plan-canonical' is missing or differs. Review Snapshots/linear-plan-canonical.received.txt and rename it to linear-plan-canonical.txt to accept.
Failed!  - Failed:     1, Passed:    16, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
```

- [x] **Step 11: Review and accept the snapshot** — review `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.received.txt` against the expected content in Step 12; it must be identical (73 lines: header, six zones with their loads and setpoints, 36 surfaces). Check in particular: zone order `ST`, `CO`, `US1`, `US2`, `UN1`, `UN2`; areas 72/40/80 m²; `ST` reads `unconditioned` instead of setpoints; every interzone wall has its reversed twin and no window; every outdoor wall has exactly one `window(...)` whose offset and sill centre it and whose area is WWR × wall area. Then rename it:

```powershell
Move-Item tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.received.txt tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.txt
```

- [x] **Step 12: Expected snapshot `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.txt`**

```text
footprint area=432.000000 floorHeight=3.000000 orientation=0.000000
zone ST Stair "Stair" area=72.000000 volume=216.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=3.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  unconditioned
zone CO Corridor "Corridor" area=40.000000 volume=120.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=5.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone US1 DwellingUnit "Unit S1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone US2 DwellingUnit "Unit S2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone UN1 DwellingUnit "Unit N1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone UN2 DwellingUnit "Unit N2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface ST/W1 Outdoors area=12.000000 wall (0.000000,0.000000)-(4.000000,0.000000) z=0.000000 facing=South glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface ST/W2 Interzone adjacent=US1 area=24.000000 wall (4.000000,0.000000)-(4.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface ST/W3 Interzone adjacent=CO area=6.000000 wall (4.000000,8.000000)-(4.000000,10.000000) z=0.000000 facing=East glazing=0.000000
surface ST/W4 Interzone adjacent=UN1 area=24.000000 wall (4.000000,10.000000)-(4.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface ST/W5 Outdoors area=12.000000 wall (4.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface ST/W6 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface ST/F Unresolved area=72.000000 Floor z=0.000000
surface ST/C Unresolved area=72.000000 Ceiling z=3.000000
surface CO/W1 Interzone adjacent=US1 area=30.000000 wall (4.000000,8.000000)-(14.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface CO/W2 Interzone adjacent=US2 area=30.000000 wall (14.000000,8.000000)-(24.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface CO/W3 Outdoors area=6.000000 wall (24.000000,8.000000)-(24.000000,10.000000) z=0.000000 facing=East glazing=1.200000 window(offset=0.552786 sill=0.829180 0.894427x1.341641)
surface CO/W4 Interzone adjacent=UN2 area=30.000000 wall (24.000000,10.000000)-(14.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface CO/W5 Interzone adjacent=UN1 area=30.000000 wall (14.000000,10.000000)-(4.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface CO/W6 Interzone adjacent=ST area=6.000000 wall (4.000000,10.000000)-(4.000000,8.000000) z=0.000000 facing=West glazing=0.000000
surface CO/F Unresolved area=40.000000 Floor z=0.000000
surface CO/C Unresolved area=40.000000 Ceiling z=3.000000
surface US1/W1 Outdoors area=30.000000 wall (4.000000,0.000000)-(14.000000,0.000000) z=0.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface US1/W2 Interzone adjacent=US2 area=24.000000 wall (14.000000,0.000000)-(14.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface US1/W3 Interzone adjacent=CO area=30.000000 wall (14.000000,8.000000)-(4.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface US1/W4 Interzone adjacent=ST area=24.000000 wall (4.000000,8.000000)-(4.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface US1/F Unresolved area=80.000000 Floor z=0.000000
surface US1/C Unresolved area=80.000000 Ceiling z=3.000000
surface US2/W1 Outdoors area=30.000000 wall (14.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface US2/W2 Outdoors area=24.000000 wall (24.000000,0.000000)-(24.000000,8.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface US2/W3 Interzone adjacent=CO area=30.000000 wall (24.000000,8.000000)-(14.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface US2/W4 Interzone adjacent=US1 area=24.000000 wall (14.000000,8.000000)-(14.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface US2/F Unresolved area=80.000000 Floor z=0.000000
surface US2/C Unresolved area=80.000000 Ceiling z=3.000000
surface UN1/W1 Interzone adjacent=CO area=30.000000 wall (4.000000,10.000000)-(14.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface UN1/W2 Interzone adjacent=UN2 area=24.000000 wall (14.000000,10.000000)-(14.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface UN1/W3 Outdoors area=30.000000 wall (14.000000,18.000000)-(4.000000,18.000000) z=0.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface UN1/W4 Interzone adjacent=ST area=24.000000 wall (4.000000,18.000000)-(4.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface UN1/F Unresolved area=80.000000 Floor z=0.000000
surface UN1/C Unresolved area=80.000000 Ceiling z=3.000000
surface UN2/W1 Interzone adjacent=CO area=30.000000 wall (14.000000,10.000000)-(24.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface UN2/W2 Outdoors area=24.000000 wall (24.000000,10.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface UN2/W3 Outdoors area=30.000000 wall (24.000000,18.000000)-(14.000000,18.000000) z=0.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface UN2/W4 Interzone adjacent=UN1 area=24.000000 wall (14.000000,18.000000)-(14.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface UN2/F Unresolved area=80.000000 Floor z=0.000000
surface UN2/C Unresolved area=80.000000 Ceiling z=3.000000
```

- [x] **Step 13: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Generators.Tests -c Release
```

Expected:

```text
Passed!  - Failed:     0, Passed:    17, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
```

- [x] **Step 14: Build the solution and run all tests**

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release --no-build
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`; `Passed!` with 94 tests for `Lod.Core.Tests.dll` and 17 for `Lod.Generators.Tests.dll`, on net8.0.

- [x] **Step 15: Commit** (`git status` must not list any `*.received.txt` file)

```bash
git add BEMGen.sln src/Lod.Core/Plans src/Lod.Core/Model/TextReport.cs src/Lod.Generators tests/Shared tests/Lod.Generators.Tests
git commit -m "feature(generators): add linear plan generator with canonical snapshot"
```

- [x] **Step 16: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/generators-linear-plan
git push origin main
git branch -d feature/generators-linear-plan
```

Expected from `verify.ps1`: `Passed!` with 94 (`Lod.Core.Tests.dll`) and 17 (`Lod.Generators.Tests.dll`) tests on net8.0, then `VERIFY PASSED`.

---

## Slice D — `feature/pipeline-no-simplification-stack`

Roadmap slice 4: the plan simplifier interface with `NoSimplification`, and the floor aggregator interface with `Stack`. Both are small, and the first integration tests need them together; the branch keeps two commits, one for each.

### Task 5: Plan simplifier interface and `NoSimplification`

**Files:**
- Create: `src/Lod.Core/Simplification/NoSimplification.cs`
- Create: `tests/Lod.Integration.Tests/Lod.Integration.Tests.csproj`
- Create: `tests/Lod.Integration.Tests/Pipeline.cs`
- Test: `tests/Lod.Integration.Tests/SkeletonPipelineTests.cs` (first test; completed in Task 6)
- Modify: `BEMGen.sln` (via `dotnet sln add`)

**Interfaces:**
- Consumes: Tasks 2 and 4 (`IGeneratedPlan`, `Floor`, `ZoneMapping`, `Provenance`, `LinearPlanGenerator`).
- Produces (namespace `Lod.Core.Simplification`): `interface IPlanSimplifier { Result<IFloor> Simplify(IGeneratedPlan plan); }` (spec §10) and `sealed class NoSimplification : IPlanSimplifier`. Test helper `Lod.Integration.Tests.Pipeline` with `Canonical`, `Tolerances`, `Plan(…)`, `Floor(IPlanSimplifier, …)`, `DetailedFloor(…)`.

**Design:** `NoSimplification` is Z0: the floor holds exactly the plan's zone and surface instances (`Floor.Footprint`, `FloorHeight`, and `OrientationDegrees` delegate to the source plan), the mapping is the identity (source = target, overlap = zone floor area, both fractions 1), and the provenance is `NoSimplification` with no parameters and the plan's provenance as its input.

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/pipeline-no-simplification-stack main
```

- [x] **Step 2: Create the integration test project** — create `tests/Lod.Integration.Tests/Lod.Integration.Tests.csproj`, then add it to the solution:

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
    <Compile Include="..\Shared\Snapshot.cs" Link="Shared\Snapshot.cs" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\..\src\Lod.Core\Lod.Core.csproj" />
    <ProjectReference Include="..\..\src\Lod.Generators\Lod.Generators.csproj" />
  </ItemGroup>

</Project>
```

```bash
dotnet sln BEMGen.sln add tests/Lod.Integration.Tests/Lod.Integration.Tests.csproj
```

Expected: ``Project `tests\Lod.Integration.Tests\Lod.Integration.Tests.csproj` added to the solution.``

- [x] **Step 3: Create the shared pipeline helper `tests/Lod.Integration.Tests/Pipeline.cs`**

```csharp
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;
using Lod.Generators.Linear;

namespace Lod.Integration.Tests;

/// <summary>Shared pipeline steps for integration tests.</summary>
internal static class Pipeline
{
    /// <summary>24 m × 18 m, 4 m stair, two 10 m units per row, 3 m storeys.</summary>
    public static readonly LinearPlanParameters Canonical = new(24.0, 8.0, 2.0, 10.0, 4.0, 3.0, 0.0);

    public static ToleranceSettings Tolerances => ToleranceSettings.Default;

    public static IGeneratedPlan Plan(LinearPlanParameters? parameters = null) =>
        new LinearPlanGenerator(Tolerances).Generate(parameters ?? Canonical, ExampleResidentialPresets.All).Value;

    public static IFloor Floor(IPlanSimplifier simplifier, LinearPlanParameters? parameters = null) =>
        simplifier.Simplify(Plan(parameters)).Value;

    public static IFloor DetailedFloor(LinearPlanParameters? parameters = null) => Floor(new NoSimplification(), parameters);
}
```

- [x] **Step 4: Write the failing test** — create `tests/Lod.Integration.Tests/SkeletonPipelineTests.cs` with the first test (Task 6 completes the file):

```csharp
using Lod.Core.Model;
using Lod.Core.Simplification;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class SkeletonPipelineTests
{
    [Fact]
    public void NoSimplificationReproducesThePlanExactly()
    {
        IGeneratedPlan plan = Pipeline.Plan();

        IFloor floor = new NoSimplification().Simplify(plan).Value;

        Assert.Same(plan, floor.Source);
        Assert.Equal(plan.Zones, floor.Zones);
        Assert.Equal(plan.Surfaces, floor.Surfaces);
        Assert.All(floor.Mapping, m => Assert.Equal(m.Source, m.Target));
        Assert.All(floor.Mapping, m => Assert.Equal(1.0, m.SourceFraction));
        Assert.Equal(TextReport.Describe(plan), TextReport.Describe(floor));
    }
}
```

- [x] **Step 5: Run the test to verify it fails**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: the build fails, including:

```text
tests\Lod.Integration.Tests\Pipeline.cs(4,16): error CS0234: The type or namespace name 'Simplification' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Integration.Tests\SkeletonPipelineTests.cs(2,16): error CS0234: The type or namespace name 'Simplification' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Integration.Tests\Pipeline.cs(20,32): error CS0246: The type or namespace name 'IPlanSimplifier' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 6: Create `src/Lod.Core/Simplification/NoSimplification.cs`**

```csharp
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Model;

namespace Lod.Core.Simplification;

/// <summary>Turns a detailed plan into a floor (spec §10).</summary>
public interface IPlanSimplifier
{
    /// <summary>Simplifies a plan.</summary>
    /// <param name="plan">The detailed plan.</param>
    /// <returns>The floor, or errors.</returns>
    public Result<IFloor> Simplify(IGeneratedPlan plan);
}

/// <summary>Identity simplifier (Z0): the floor has exactly the plan's zones and surfaces, with an identity mapping.</summary>
public sealed class NoSimplification : IPlanSimplifier
{
    /// <inheritdoc />
    public Result<IFloor> Simplify(IGeneratedPlan plan)
    {
        ZoneMapping[] mapping = plan.Zones.Select(z => new ZoneMapping(z.Id, z.Id, z.FloorArea, 1.0, 1.0)).ToArray();
        IFloor floor = new Floor(plan, plan.Zones, plan.Surfaces, mapping, Provenance.Of(nameof(NoSimplification), Enumerable.Empty<System.Collections.Generic.KeyValuePair<string, string>>(), plan.Provenance));
        return Result.Success(floor);
    }
}
```

- [x] **Step 7: Run the test to verify it passes**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected:

```text
Passed!  - Failed:     0, Passed:     1, Skipped:     0, Total:     1, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

- [x] **Step 8: Commit**

```bash
git add BEMGen.sln src/Lod.Core/Simplification tests/Lod.Integration.Tests
git commit -m "feature(core): add plan simplifier interface and no simplification"
```

### Task 6: `Stack` floor aggregator

**Files:**
- Create: `src/Lod.Core/Buildings/Storeys.cs`
- Create: `src/Lod.Core/Buildings/Stack.cs`
- Modify: `tests/Lod.Integration.Tests/SkeletonPipelineTests.cs`
- Create: `tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.txt`

**Interfaces:**
- Consumes: Tasks 1, 2, 5 (`PolygonOps`, `Zone.Relocate`, `WallSurface.Relocate`, `HorizontalSurface`, `FloorEntry`, `GeneratedBuilding`, `Provenance`).
- Produces (namespace `Lod.Core.Buildings`):
  - `interface IFloorAggregator { Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors); }` (D-018).
  - `sealed class Stack : IFloorAggregator` (constructor `Stack(ToleranceSettings tolerances)`).
  - Shared steps (S4 reuses `Validate`, `PlacedStorey`, and `Place`, and adds true-elevation placement and representative-storey resolution for `FloorAreaMultiplier`, D-045, D-046): `sealed record PlacedStorey(int Index, double Elevation, double Height, IReadOnlyList<Zone> Zones, IReadOnlyList<WallSurface> Walls)`; `static class Storeys` with `IReadOnlyList<Diagnostic> Validate(IReadOnlyList<FloorEntry> floors, ToleranceSettings tolerances)`, `IReadOnlyList<PlacedStorey> Place(IEnumerable<(IFloor Floor, int ZoneMultiplier)> storeys)`, `IReadOnlyList<HorizontalSurface> ResolveStacked(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops)`.

**Design:**
- **Input checks (`Storeys.Validate`).** At least one floor (`NoFloors`); every multiplier ≥ 1 (`InvalidParameter`); all floors have the same orientation within `ToleranceSettings.Angle` converted to degrees (`OrientationMismatch`).
- **Multiplier means "repeat explicitly".** For `Stack`, `FloorEntry.Multiplier` is the number of storeys the entry stands for, and each entry is expanded into that many explicit storeys, in list order from the bottom. Every zone keeps multiplier 1. (S4's `FloorAreaMultiplier` interprets the same multiplier as a zone multiplier on one representative storey at its true elevation instead, D-032, D-045, D-046.)
- **Placement and IDs (`Storeys.Place`).** Storey `k` (0 at the bottom, counting expanded storeys) sits at the sum of the floor-to-floor heights below it. Zone IDs, wall IDs, and the adjacent-zone IDs of walls get the prefix `L{k}/`, e.g. `L2/US1` and `L2/US1/W1`, so IDs stay unique across storeys; display names are unchanged.
- **Floors and ceilings (`Storeys.ResolveStacked`).** The unresolved floor and ceiling of each layout are replaced. A zone's floor is intersected with every zone of the storey below: each overlap piece becomes an `Interzone` floor adjacent to that zone; the part not covered by the storey below faces `Outdoors`; floors of the bottom storey face the `Ground` (one piece). Ceilings work the same way against the storey above; ceilings of the top storey are roofs (`Outdoors`). IDs are `{zone}/F{n}` and `{zone}/C{n}` with `n` from 1.
- **Building.** Surfaces are all walls (storey by storey) followed by the resolved floors and ceilings; no internal mass; `Sources` are the entries as given; provenance `Stack` with parameter `Multipliers` (comma-separated) and each entry's floor provenance as inputs.

- [x] **Step 1: Full file after this task: `tests/Lod.Integration.Tests/SkeletonPipelineTests.cs`** — replace the file with the following. It adds the usings `System.Linq`, `Lod.Core.Buildings`, `Lod.Core.Common`, and `Lod.Tests.Shared`, the `_stack` field, and 8 tests: storey placement and boundary resolution over three storeys, matching inter-storey pairs, conservation of floor area and glazing per storey, a setback exposing part of the ceiling below (10 m × 18 m), orientation mismatch, empty input, provenance chain, and a two-storey snapshot:

```csharp
using System.Linq;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Simplification;
using Lod.Tests.Shared;
using Xunit;

namespace Lod.Integration.Tests;

public sealed class SkeletonPipelineTests
{
    private readonly Stack _stack = new(Pipeline.Tolerances);

    [Fact]
    public void NoSimplificationReproducesThePlanExactly()
    {
        IGeneratedPlan plan = Pipeline.Plan();

        IFloor floor = new NoSimplification().Simplify(plan).Value;

        Assert.Same(plan, floor.Source);
        Assert.Equal(plan.Zones, floor.Zones);
        Assert.Equal(plan.Surfaces, floor.Surfaces);
        Assert.All(floor.Mapping, m => Assert.Equal(m.Source, m.Target));
        Assert.All(floor.Mapping, m => Assert.Equal(1.0, m.SourceFraction));
        Assert.Equal(TextReport.Describe(plan), TextReport.Describe(floor));
    }

    [Fact]
    public void StackPlacesStoreysAndResolvesFloorsAndCeilings()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(floor, 3) }).Value;

        Assert.Equal(18, building.Zones.Count);
        Assert.Equal(6.0, building.Zones.Single(z => z.Id.Value == "L2/US1").Parts[0].Elevation);
        HorizontalSurface[] horizontal = building.Surfaces.OfType<HorizontalSurface>().ToArray();
        Assert.All(horizontal.Where(h => h.Kind == HorizontalKind.Floor && h.Zone.Value.StartsWith("L0/")), h => Assert.Equal(BoundaryCondition.Ground, h.Boundary));
        Assert.All(horizontal.Where(h => h.Kind == HorizontalKind.Ceiling && h.Zone.Value.StartsWith("L2/")), h => Assert.Equal(BoundaryCondition.Outdoors, h.Boundary));
        Assert.All(horizontal.Where(h => h.Zone.Value.StartsWith("L1/")), h => Assert.Equal(BoundaryCondition.Interzone, h.Boundary));
        Assert.DoesNotContain(horizontal, h => h.Boundary == BoundaryCondition.Unresolved);
    }

    [Fact]
    public void InterstoreySurfacesComeInMatchingPairs()
    {
        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;
        HorizontalSurface[] interzone = building.Surfaces.OfType<HorizontalSurface>().Where(h => h.Boundary == BoundaryCondition.Interzone).ToArray();

        Assert.Equal(12, interzone.Length);
        Assert.All(interzone, h => Assert.Contains(interzone, o => o.Zone == h.AdjacentZone && o.AdjacentZone == h.Zone && o.Kind != h.Kind && Pipeline.Tolerances.AreaEquals(o.Area, h.Area)));
    }

    [Fact]
    public void StackConservesAreaAndGlazingPerStorey()
    {
        IFloor floor = Pipeline.DetailedFloor();

        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(floor, 2), new FloorEntry(floor, 1) }).Value;

        Assert.Equal(3 * floor.Zones.Sum(z => z.FloorArea), building.Zones.Sum(z => z.FloorArea), 9);
        Assert.Equal(
            3 * floor.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea),
            building.Surfaces.OfType<WallSurface>().Sum(w => w.GlazedArea),
            9);
    }

    [Fact]
    public void SetbackExposesPartOfTheCeilingBelow()
    {
        IFloor full = Pipeline.DetailedFloor();
        IFloor shorter = Pipeline.DetailedFloor(Pipeline.Canonical with { Length = 14.0 });

        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(full, 1), new FloorEntry(shorter, 1) }).Value;

        double exposedRoofBelow = building.Surfaces.OfType<HorizontalSurface>()
            .Where(h => h.Kind == HorizontalKind.Ceiling && h.Zone.Value.StartsWith("L0/") && h.Boundary == BoundaryCondition.Outdoors)
            .Sum(h => h.Area);
        Assert.Equal(10.0 * 18.0, exposedRoofBelow, 6);
    }

    [Fact]
    public void FloorsWithDifferentOrientationsAreRejected()
    {
        IFloor north = Pipeline.DetailedFloor();
        IFloor rotated = Pipeline.DetailedFloor(Pipeline.Canonical with { OrientationDegrees = 30.0 });

        Result<IGeneratedBuilding> result = _stack.Aggregate(new[] { new FloorEntry(north, 1), new FloorEntry(rotated, 1) });

        Assert.Contains(result.Diagnostics, d => d.Code == DiagnosticCodes.OrientationMismatch);
    }

    [Fact]
    public void EmptyInputIsRejected()
    {
        Assert.Contains(_stack.Aggregate(new FloorEntry[0]).Diagnostics, d => d.Code == DiagnosticCodes.NoFloors);
    }

    [Fact]
    public void ProvenanceTracesBackToTheGenerator()
    {
        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;

        Assert.Equal("Stack", building.Provenance.Operation);
        Assert.Equal("NoSimplification", building.Provenance.Inputs[0].Operation);
        Assert.Equal("LinearPlanGenerator", building.Provenance.Inputs[0].Inputs[0].Operation);
    }

    [Fact]
    public void TwoStoreySnapshot()
    {
        IGeneratedBuilding building = _stack.Aggregate(new[] { new FloorEntry(Pipeline.DetailedFloor(), 2) }).Value;

        Snapshot.Match(TextReport.Describe(building), "stack-two-storeys");
    }
}
```

- [x] **Step 2: Run the tests to verify they fail**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: the build fails, including:

```text
tests\Lod.Integration.Tests\SkeletonPipelineTests.cs(2,16): error CS0234: The type or namespace name 'Buildings' does not exist in the namespace 'Lod.Core' (are you missing an assembly reference?)
tests\Lod.Integration.Tests\SkeletonPipelineTests.cs(13,22): error CS0246: The type or namespace name 'Stack' could not be found (are you missing a using directive or an assembly reference?)
```

- [x] **Step 3: Create `src/Lod.Core/Buildings/Storeys.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>A floor placed at its elevation with storey-prefixed zone and surface IDs.</summary>
/// <param name="Index">Storey index from 0 at the bottom.</param>
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

    /// <summary>Stacks floors bottom to top, prefixing IDs with <c>L{index}/</c>.</summary>
    /// <param name="storeys">Floors in vertical order with the zone multiplier to apply.</param>
    /// <returns>The placed storeys.</returns>
    public static IReadOnlyList<PlacedStorey> Place(IEnumerable<(IFloor Floor, int ZoneMultiplier)> storeys)
    {
        var placed = new List<PlacedStorey>();
        double elevation = 0.0;
        foreach ((IFloor floor, int multiplier) in storeys)
        {
            int index = placed.Count;
            string prefix = $"L{index}/";
            ZoneId Rename(ZoneId id) => new(prefix + id.Value);
            Zone[] zones = floor.Zones.Select(z => z.Relocate(Rename(z.Id), elevation, multiplier)).ToArray();
            WallSurface[] walls = floor.Surfaces.OfType<WallSurface>().Select(w => w.Relocate(Rename, prefix, elevation)).ToArray();
            placed.Add(new PlacedStorey(index, elevation, floor.FloorHeight, zones, walls));
            elevation += floor.FloorHeight;
        }

        return placed;
    }

    /// <summary>
    /// Floors and ceilings of physically stacked storeys: split by overlap with the zones below and above into interzone pieces;
    /// uncovered parts face outdoors; the lowest floors face the ground and the highest ceilings are roofs.
    /// </summary>
    /// <param name="storeys">Placed storeys, bottom to top.</param>
    /// <param name="ops">Polygon operations.</param>
    /// <returns>Horizontal surfaces.</returns>
    public static IReadOnlyList<HorizontalSurface> ResolveStacked(IReadOnlyList<PlacedStorey> storeys, PolygonOps ops)
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
                surfaces.AddRange(Split(zone.Id, HorizontalKind.Floor, footprint, storey.Elevation, below, BoundaryCondition.Ground, ops));
                surfaces.AddRange(Split(zone.Id, HorizontalKind.Ceiling, footprint, storey.Elevation + storey.Height, above, BoundaryCondition.Outdoors, ops));
            }
        }

        return surfaces;
    }

    private static IEnumerable<HorizontalSurface> Split(ZoneId zone, HorizontalKind kind, Polygon2 footprint, double elevation, PlacedStorey? neighbour, BoundaryCondition exposed, PolygonOps ops)
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
                yield return new HorizontalSurface(new SurfaceId($"{zone.Value}/{tag}{number++}"), zone, kind, piece, elevation, BoundaryCondition.Interzone, other.Id);
            }
        }

        foreach (Polygon2 piece in ops.Difference(footprint, neighbour.Zones.Select(z => z.Parts[0].Footprint)))
        {
            yield return new HorizontalSurface(new SurfaceId($"{zone.Value}/{tag}{number++}"), zone, kind, piece, elevation, BoundaryCondition.Outdoors, null);
        }
    }
}
```

- [x] **Step 4: Create `src/Lod.Core/Buildings/Stack.cs`**

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;

namespace Lod.Core.Buildings;

/// <summary>Turns floors into a building (D-018).</summary>
public interface IFloorAggregator
{
    /// <summary>Aggregates floors, listed bottom to top, into a building.</summary>
    /// <param name="floors">Floor entries; the multiplier is the number of storeys an entry stands for.</param>
    /// <returns>The building, or errors.</returns>
    public Result<IGeneratedBuilding> Aggregate(IReadOnlyList<FloorEntry> floors);
}

/// <summary>
/// All storeys explicit: each entry is repeated <see cref="FloorEntry.Multiplier"/> times and stacked at its floor-to-floor height.
/// Inter-storey floors and ceilings become interzone surfaces; the bottom faces the ground and the top is the roof.
/// </summary>
public sealed class Stack : IFloorAggregator
{
    private readonly ToleranceSettings _tolerances;

    /// <summary>Creates the aggregator.</summary>
    /// <param name="tolerances">Tolerances.</param>
    public Stack(ToleranceSettings tolerances)
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

        IReadOnlyList<PlacedStorey> storeys = Storeys.Place(floors.SelectMany(e => Enumerable.Repeat((e.Floor, 1), e.Multiplier)));
        IEnumerable<Surface> surfaces = storeys.SelectMany(s => s.Walls).Cast<Surface>()
            .Concat(Storeys.ResolveStacked(storeys, new PolygonOps(_tolerances)));
        var provenance = Provenance.Of(
            nameof(Stack),
            new[] { new KeyValuePair<string, string>("Multipliers", string.Join(",", floors.Select(e => e.Multiplier))) },
            floors.Select(e => e.Floor.Provenance).ToArray());
        IGeneratedBuilding building = new GeneratedBuilding(
            floors[0].Floor.OrientationDegrees,
            storeys.SelectMany(s => s.Zones),
            surfaces,
            Enumerable.Empty<InternalMass>(),
            floors,
            provenance);
        return Result.Success(building);
    }
}
```

- [x] **Step 5: Run the tests; only the snapshot test fails**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected: 8 tests pass; `TwoStoreySnapshot` fails on net8.0 and writes `tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.received.txt`:

```text
  Failed Lod.Integration.Tests.SkeletonPipelineTests.TwoStoreySnapshot
  Error Message:
   Snapshot 'stack-two-storeys' is missing or differs. Review Snapshots/stack-two-storeys.received.txt and rename it to stack-two-storeys.txt to accept.
Failed!  - Failed:     1, Passed:     8, Skipped:     0, Total:     9, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

- [x] **Step 6: Review and accept the snapshot** — review `tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.received.txt` against the expected content in Step 7; it must be identical (145 lines). Check in particular: header `sources=2`; zones `L0/…` then `L1/…` (`L0/ST` and `L1/ST` read `unconditioned`); walls of `L1` at `z=3.000000` with the same windows as `L0`; `L0` floors `Ground`, `L0` ceilings `Interzone` with the zone above, `L1` floors `Interzone` with the zone below, `L1` ceilings `Outdoors` at `z=6.000000`; no `Unresolved` surface. Then rename it:

```powershell
Move-Item tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.received.txt tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.txt
```

- [x] **Step 7: Expected snapshot `tests/Lod.Integration.Tests/Snapshots/stack-two-storeys.txt`**

```text
building orientation=0.000000 sources=2
zone L0/ST Stair "Stair" area=72.000000 volume=216.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=3.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  unconditioned
zone L0/CO Corridor "Corridor" area=40.000000 volume=120.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=5.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/US1 DwellingUnit "Unit S1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/US2 DwellingUnit "Unit S2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/UN1 DwellingUnit "Unit N1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L0/UN2 DwellingUnit "Unit N2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L1/ST Stair "Stair" area=72.000000 volume=216.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=3.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  unconditioned
zone L1/CO Corridor "Corridor" area=40.000000 volume=120.000000 parts=1 multiplier=1 sources=[]
  load Lighting PerFloorArea value=5.000000 annual=8760.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L1/US1 DwellingUnit "Unit S1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L1/US2 DwellingUnit "Unit S2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L1/UN1 DwellingUnit "Unit N1" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
zone L1/UN2 DwellingUnit "Unit N2" area=80.000000 volume=240.000000 parts=1 multiplier=1 sources=[]
  load Occupancy PerFloorArea value=0.030000 annual=6391.400000
  load Lighting PerFloorArea value=5.000000 annual=2627.800000
  load ElectricEquipment PerFloorArea value=5.000000 annual=4380.000000
  load Infiltration AirChangesPerHour value=0.300000 annual=8760.000000
  setpoints heatingMean=21.000000 coolingMean=24.000000
surface L0/ST/W1 Outdoors area=12.000000 wall (0.000000,0.000000)-(4.000000,0.000000) z=0.000000 facing=South glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface L0/ST/W2 Interzone adjacent=L0/US1 area=24.000000 wall (4.000000,0.000000)-(4.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface L0/ST/W3 Interzone adjacent=L0/CO area=6.000000 wall (4.000000,8.000000)-(4.000000,10.000000) z=0.000000 facing=East glazing=0.000000
surface L0/ST/W4 Interzone adjacent=L0/UN1 area=24.000000 wall (4.000000,10.000000)-(4.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface L0/ST/W5 Outdoors area=12.000000 wall (4.000000,18.000000)-(0.000000,18.000000) z=0.000000 facing=North glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface L0/ST/W6 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=0.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L0/CO/W1 Interzone adjacent=L0/US1 area=30.000000 wall (4.000000,8.000000)-(14.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface L0/CO/W2 Interzone adjacent=L0/US2 area=30.000000 wall (14.000000,8.000000)-(24.000000,8.000000) z=0.000000 facing=South glazing=0.000000
surface L0/CO/W3 Outdoors area=6.000000 wall (24.000000,8.000000)-(24.000000,10.000000) z=0.000000 facing=East glazing=1.200000 window(offset=0.552786 sill=0.829180 0.894427x1.341641)
surface L0/CO/W4 Interzone adjacent=L0/UN2 area=30.000000 wall (24.000000,10.000000)-(14.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface L0/CO/W5 Interzone adjacent=L0/UN1 area=30.000000 wall (14.000000,10.000000)-(4.000000,10.000000) z=0.000000 facing=North glazing=0.000000
surface L0/CO/W6 Interzone adjacent=L0/ST area=6.000000 wall (4.000000,10.000000)-(4.000000,8.000000) z=0.000000 facing=West glazing=0.000000
surface L0/US1/W1 Outdoors area=30.000000 wall (4.000000,0.000000)-(14.000000,0.000000) z=0.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L0/US1/W2 Interzone adjacent=L0/US2 area=24.000000 wall (14.000000,0.000000)-(14.000000,8.000000) z=0.000000 facing=East glazing=0.000000
surface L0/US1/W3 Interzone adjacent=L0/CO area=30.000000 wall (14.000000,8.000000)-(4.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface L0/US1/W4 Interzone adjacent=L0/ST area=24.000000 wall (4.000000,8.000000)-(4.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface L0/US2/W1 Outdoors area=30.000000 wall (14.000000,0.000000)-(24.000000,0.000000) z=0.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L0/US2/W2 Outdoors area=24.000000 wall (24.000000,0.000000)-(24.000000,8.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface L0/US2/W3 Interzone adjacent=L0/CO area=30.000000 wall (24.000000,8.000000)-(14.000000,8.000000) z=0.000000 facing=North glazing=0.000000
surface L0/US2/W4 Interzone adjacent=L0/US1 area=24.000000 wall (14.000000,8.000000)-(14.000000,0.000000) z=0.000000 facing=West glazing=0.000000
surface L0/UN1/W1 Interzone adjacent=L0/CO area=30.000000 wall (4.000000,10.000000)-(14.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface L0/UN1/W2 Interzone adjacent=L0/UN2 area=24.000000 wall (14.000000,10.000000)-(14.000000,18.000000) z=0.000000 facing=East glazing=0.000000
surface L0/UN1/W3 Outdoors area=30.000000 wall (14.000000,18.000000)-(4.000000,18.000000) z=0.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L0/UN1/W4 Interzone adjacent=L0/ST area=24.000000 wall (4.000000,18.000000)-(4.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface L0/UN2/W1 Interzone adjacent=L0/CO area=30.000000 wall (14.000000,10.000000)-(24.000000,10.000000) z=0.000000 facing=South glazing=0.000000
surface L0/UN2/W2 Outdoors area=24.000000 wall (24.000000,10.000000)-(24.000000,18.000000) z=0.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface L0/UN2/W3 Outdoors area=30.000000 wall (24.000000,18.000000)-(14.000000,18.000000) z=0.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L0/UN2/W4 Interzone adjacent=L0/UN1 area=24.000000 wall (14.000000,18.000000)-(14.000000,10.000000) z=0.000000 facing=West glazing=0.000000
surface L1/ST/W1 Outdoors area=12.000000 wall (0.000000,0.000000)-(4.000000,0.000000) z=3.000000 facing=South glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface L1/ST/W2 Interzone adjacent=L1/US1 area=24.000000 wall (4.000000,0.000000)-(4.000000,8.000000) z=3.000000 facing=East glazing=0.000000
surface L1/ST/W3 Interzone adjacent=L1/CO area=6.000000 wall (4.000000,8.000000)-(4.000000,10.000000) z=3.000000 facing=East glazing=0.000000
surface L1/ST/W4 Interzone adjacent=L1/UN1 area=24.000000 wall (4.000000,10.000000)-(4.000000,18.000000) z=3.000000 facing=East glazing=0.000000
surface L1/ST/W5 Outdoors area=12.000000 wall (4.000000,18.000000)-(0.000000,18.000000) z=3.000000 facing=North glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)
surface L1/ST/W6 Outdoors area=54.000000 wall (0.000000,18.000000)-(0.000000,0.000000) z=3.000000 facing=West glazing=5.400000 window(offset=6.153950 sill=1.025658 5.692100x0.948683)
surface L1/CO/W1 Interzone adjacent=L1/US1 area=30.000000 wall (4.000000,8.000000)-(14.000000,8.000000) z=3.000000 facing=South glazing=0.000000
surface L1/CO/W2 Interzone adjacent=L1/US2 area=30.000000 wall (14.000000,8.000000)-(24.000000,8.000000) z=3.000000 facing=South glazing=0.000000
surface L1/CO/W3 Outdoors area=6.000000 wall (24.000000,8.000000)-(24.000000,10.000000) z=3.000000 facing=East glazing=1.200000 window(offset=0.552786 sill=0.829180 0.894427x1.341641)
surface L1/CO/W4 Interzone adjacent=L1/UN2 area=30.000000 wall (24.000000,10.000000)-(14.000000,10.000000) z=3.000000 facing=North glazing=0.000000
surface L1/CO/W5 Interzone adjacent=L1/UN1 area=30.000000 wall (14.000000,10.000000)-(4.000000,10.000000) z=3.000000 facing=North glazing=0.000000
surface L1/CO/W6 Interzone adjacent=L1/ST area=6.000000 wall (4.000000,10.000000)-(4.000000,8.000000) z=3.000000 facing=West glazing=0.000000
surface L1/US1/W1 Outdoors area=30.000000 wall (4.000000,0.000000)-(14.000000,0.000000) z=3.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L1/US1/W2 Interzone adjacent=L1/US2 area=24.000000 wall (14.000000,0.000000)-(14.000000,8.000000) z=3.000000 facing=East glazing=0.000000
surface L1/US1/W3 Interzone adjacent=L1/CO area=30.000000 wall (14.000000,8.000000)-(4.000000,8.000000) z=3.000000 facing=North glazing=0.000000
surface L1/US1/W4 Interzone adjacent=L1/ST area=24.000000 wall (4.000000,8.000000)-(4.000000,0.000000) z=3.000000 facing=West glazing=0.000000
surface L1/US2/W1 Outdoors area=30.000000 wall (14.000000,0.000000)-(24.000000,0.000000) z=3.000000 facing=South glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L1/US2/W2 Outdoors area=24.000000 wall (24.000000,0.000000)-(24.000000,8.000000) z=3.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface L1/US2/W3 Interzone adjacent=L1/CO area=30.000000 wall (24.000000,8.000000)-(14.000000,8.000000) z=3.000000 facing=North glazing=0.000000
surface L1/US2/W4 Interzone adjacent=L1/US1 area=24.000000 wall (14.000000,8.000000)-(14.000000,0.000000) z=3.000000 facing=West glazing=0.000000
surface L1/UN1/W1 Interzone adjacent=L1/CO area=30.000000 wall (4.000000,10.000000)-(14.000000,10.000000) z=3.000000 facing=South glazing=0.000000
surface L1/UN1/W2 Interzone adjacent=L1/UN2 area=24.000000 wall (14.000000,10.000000)-(14.000000,18.000000) z=3.000000 facing=East glazing=0.000000
surface L1/UN1/W3 Outdoors area=30.000000 wall (14.000000,18.000000)-(4.000000,18.000000) z=3.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L1/UN1/W4 Interzone adjacent=L1/ST area=24.000000 wall (4.000000,18.000000)-(4.000000,10.000000) z=3.000000 facing=West glazing=0.000000
surface L1/UN2/W1 Interzone adjacent=L1/CO area=30.000000 wall (14.000000,10.000000)-(24.000000,10.000000) z=3.000000 facing=South glazing=0.000000
surface L1/UN2/W2 Outdoors area=24.000000 wall (24.000000,10.000000)-(24.000000,18.000000) z=3.000000 facing=East glazing=7.200000 window(offset=1.809110 sill=0.678416 4.381780x1.643168)
surface L1/UN2/W3 Outdoors area=30.000000 wall (24.000000,18.000000)-(14.000000,18.000000) z=3.000000 facing=North glazing=9.000000 window(offset=2.261387 sill=0.678416 5.477226x1.643168)
surface L1/UN2/W4 Interzone adjacent=L1/UN1 area=24.000000 wall (14.000000,18.000000)-(14.000000,10.000000) z=3.000000 facing=West glazing=0.000000
surface L0/ST/F1 Ground area=72.000000 Floor z=0.000000
surface L0/ST/C1 Interzone adjacent=L1/ST area=72.000000 Ceiling z=3.000000
surface L0/CO/F1 Ground area=40.000000 Floor z=0.000000
surface L0/CO/C1 Interzone adjacent=L1/CO area=40.000000 Ceiling z=3.000000
surface L0/US1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/US1/C1 Interzone adjacent=L1/US1 area=80.000000 Ceiling z=3.000000
surface L0/US2/F1 Ground area=80.000000 Floor z=0.000000
surface L0/US2/C1 Interzone adjacent=L1/US2 area=80.000000 Ceiling z=3.000000
surface L0/UN1/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN1/C1 Interzone adjacent=L1/UN1 area=80.000000 Ceiling z=3.000000
surface L0/UN2/F1 Ground area=80.000000 Floor z=0.000000
surface L0/UN2/C1 Interzone adjacent=L1/UN2 area=80.000000 Ceiling z=3.000000
surface L1/ST/F1 Interzone adjacent=L0/ST area=72.000000 Floor z=3.000000
surface L1/ST/C1 Outdoors area=72.000000 Ceiling z=6.000000
surface L1/CO/F1 Interzone adjacent=L0/CO area=40.000000 Floor z=3.000000
surface L1/CO/C1 Outdoors area=40.000000 Ceiling z=6.000000
surface L1/US1/F1 Interzone adjacent=L0/US1 area=80.000000 Floor z=3.000000
surface L1/US1/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/US2/F1 Interzone adjacent=L0/US2 area=80.000000 Floor z=3.000000
surface L1/US2/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/UN1/F1 Interzone adjacent=L0/UN1 area=80.000000 Floor z=3.000000
surface L1/UN1/C1 Outdoors area=80.000000 Ceiling z=6.000000
surface L1/UN2/F1 Interzone adjacent=L0/UN2 area=80.000000 Floor z=3.000000
surface L1/UN2/C1 Outdoors area=80.000000 Ceiling z=6.000000
```

- [x] **Step 8: Run the tests to verify they pass**

```bash
dotnet test tests/Lod.Integration.Tests -c Release
```

Expected:

```text
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Integration.Tests.dll (net8.0)
```

- [x] **Step 9: Build the solution and run all tests**

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release --no-build
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`, then (line order may vary):

```text
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Integration.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    17, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    94, Skipped:     0, Total:    94, Duration: … - Lod.Core.Tests.dll (net8.0)
```

- [x] **Step 10: Commit** (`git status` must not list any `*.received.txt` file)

```bash
git add src/Lod.Core/Buildings tests/Lod.Integration.Tests
git commit -m "feature(core): add stack floor aggregator with resolved floors and ceilings"
```

- [x] **Step 11: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/pipeline-no-simplification-stack
git push origin main
git branch -d feature/pipeline-no-simplification-stack
```

Expected from `verify.ps1`: the three `Passed!` lines of Step 9, then `VERIFY PASSED`.

---

## Slice E — `feature/grasshopper-pipeline-components`

Grasshopper code needs Rhino to run, so it is not unit-tested: each task is write code → `dotnet build` with 0 warnings → commit, plus a manual check in Rhino 8. All domain logic stays in `Lod.Core`/`Lod.Generators`; the components only read inputs, call a service, and convert results and diagnostics (GLOBAL.md architecture rule 3). `Lod.Grasshopper` does not generate XML documentation, so its public types need no doc comments; Goo class names avoid the `GH_` prefix because of the PascalCase naming rule.

### Task 7: Goo wrappers, parameters, and Rhino geometry conversion

**Files:**
- Create: `src/Lod.Grasshopper/Convert/RhinoGeometry.cs`
- Create: `src/Lod.Grasshopper/Goo/BemGoo.cs`
- Create: `src/Lod.Grasshopper/Parameters/BemParameters.cs`

**Interfaces:**
- Consumes: `Zone`, `ZonePart`, `WallSurface`, `HorizontalSurface`, `Polygon2`, `Window` (Tasks 1–2); `IGeneratedPlan`, `IFloor`, `IGeneratedBuilding` (Task 2); `Schedule`, `LoadDefinition`, `ProgramPreset` (S1); `ComponentCategories` (S0).
- Produces:
  - `internal static class Lod.Grasshopper.Convert.RhinoGeometry`: `double UnitScale`, `IEnumerable<Brep> ZoneBreps(Zone zone)`, `Brep? WallBrep(WallSurface wall)`, `IEnumerable<Brep> WindowBreps(WallSurface wall)`, `IEnumerable<Brep> HorizontalBreps(HorizontalSurface surface)`.
  - `Lod.Grasshopper.Goo`: `abstract class BemGoo<T> : GH_Goo<T>`; `ScheduleGoo`, `LoadGoo`, `ProgramPresetGoo`; `abstract class PreviewGoo<T> : BemGoo<T>, IGH_PreviewData`; `PlanGoo` (`IGeneratedPlan`), `FloorGoo` (`IFloor`), `BuildingGoo` (`IGeneratedBuilding`).
  - `Lod.Grasshopper.Parameters`: `abstract class BemParameter<TGoo> : GH_Param<TGoo>, IGH_PreviewObject`; `ScheduleParameter`, `LoadParameter`, `ProgramPresetParameter`, `PlanParameter`, `FloorParameter`, `BuildingParameter`.

**Design:**
- `RhinoGeometry` is the only place that creates Rhino geometry. Pipeline geometry is in metres; every Brep is scaled about the world origin by `RhinoMath.UnitScale(UnitSystem.Meters, doc.ModelUnitSystem)` of the active document (1 without a document). A zone part becomes a closed extrusion of its planar floor Brep; a wall becomes a planar rectangle from `Start` to `End`; each window becomes a rectangle in the wall's plane at its explicit offset along the wall and its sill height (D-039).
- Goo wrappers hold immutable values, so `Duplicate` shares the value. `PreviewGoo` builds its preview lazily once: zones as shaded Breps coloured by space type (dwelling unit sand, corridor grey, stair red, core purple, mixed green, others blue-grey; 60 % transparency) and every window in blue (20 % transparency), plus wires.
- Parameters are hidden from the toolbar (`GH_Exposure.hidden`, registered under panel *0 Info*) and exist only as component inputs and outputs; they draw the previews of their Goo.

Parameter GUIDs (fixed from now on):

| Parameter | Nickname | Goo | GUID |
| --- | --- | --- | --- |
| Schedule | Sch | `ScheduleGoo` | `a4ae84ac-36d6-41b8-9b3d-c77cca52a2df` |
| Load | L | `LoadGoo` | `9e9fbc12-9b81-42b7-8c5d-a4f8397a4487` |
| Program Preset | P | `ProgramPresetGoo` | `56578999-825c-4926-afdd-ce897b53221a` |
| Plan | Plan | `PlanGoo` | `fca85387-7aaf-41fe-9654-382b2980f18f` |
| Floor | Floor | `FloorGoo` | `15a085fa-f308-46b7-93e6-88a7a85e6a89` |
| Building | Bldg | `BuildingGoo` | `d6726442-189d-4c44-b043-b56417a3826a` |

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/grasshopper-pipeline-components main
```

- [x] **Step 2: Create `src/Lod.Grasshopper/Convert/RhinoGeometry.cs`**

```csharp
using System.Collections.Generic;
using System.Linq;
using Lod.Core.Common;
using Lod.Core.Geometry;
using Lod.Core.Model;
using Rhino;
using Rhino.Geometry;

namespace Lod.Grasshopper.Convert;

/// <summary>
/// Converts pipeline geometry (metres) to Rhino geometry in the active document's model units. The only place Rhino geometry is created.
/// </summary>
internal static class RhinoGeometry
{
    private static double Tolerance => ToleranceSettings.Default.Distance;

    /// <summary>Metres to model units of the active document (1 without a document).</summary>
    public static double UnitScale => RhinoDoc.ActiveDoc is { } doc ? RhinoMath.UnitScale(UnitSystem.Meters, doc.ModelUnitSystem) : 1.0;

    /// <summary>One closed Brep per zone part.</summary>
    public static IEnumerable<Brep> ZoneBreps(Zone zone)
    {
        foreach (ZonePart part in zone.Parts)
        {
            foreach (Brep planar in PlanarBreps(part.Footprint, part.Elevation))
            {
                Brep? solid = planar.Faces[0].CreateExtrusion(new LineCurve(Point3d.Origin, new Point3d(0, 0, part.Height)), true);
                if (solid is not null)
                {
                    yield return Scaled(solid);
                }
            }
        }
    }

    /// <summary>The wall as a planar rectangle.</summary>
    public static Brep? WallBrep(WallSurface wall) =>
        Rectangle(wall, offset: 0.0, width: wall.Length, bottom: wall.Elevation, height: wall.Height);

    /// <summary>Every window of a wall at its explicit position.</summary>
    public static IEnumerable<Brep> WindowBreps(WallSurface wall) =>
        wall.Windows
            .Select(w => Rectangle(wall, offset: w.Offset, width: w.Width, bottom: wall.Elevation + w.SillHeight, height: w.Height))
            .Where(b => b is not null)
            .Select(b => b!);

    /// <summary>A floor or ceiling as planar Breps.</summary>
    public static IEnumerable<Brep> HorizontalBreps(HorizontalSurface surface) => PlanarBreps(surface.Polygon, surface.Elevation).Select(Scaled);

    private static IEnumerable<Brep> PlanarBreps(Polygon2 polygon, double elevation)
    {
        Curve[] curves = polygon.Rings
            .Select(ring => (Curve)new PolylineCurve(ring.Select(p => new Point3d(p.X, p.Y, elevation)).Concat(new[] { new Point3d(ring[0].X, ring[0].Y, elevation) })))
            .ToArray();
        return Brep.CreatePlanarBreps(curves, Tolerance) ?? Enumerable.Empty<Brep>();
    }

    private static Brep? Rectangle(WallSurface wall, double offset, double width, double bottom, double height)
    {
        double length = wall.Length;
        var direction = new Vector3d((wall.End.X - wall.Start.X) / length, (wall.End.Y - wall.Start.Y) / length, 0);
        var origin = new Point3d(wall.Start.X, wall.Start.Y, bottom) + (direction * offset);
        Point3d a = origin;
        Point3d b = origin + (direction * width);
        Point3d c = b + new Vector3d(0, 0, height);
        Point3d d = a + new Vector3d(0, 0, height);
        Brep? brep = Brep.CreateFromCornerPoints(a, b, c, d, Tolerance);
        return brep is null ? null : Scaled(brep);
    }

    private static Brep Scaled(Brep brep)
    {
        double scale = UnitScale;
        if (scale != 1.0)
        {
            brep.Transform(Transform.Scale(Point3d.Origin, scale));
        }

        return brep;
    }
}
```

- [x] **Step 3: Create `src/Lod.Grasshopper/Goo/BemGoo.cs`**

```csharp
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Schedules;
using Lod.Grasshopper.Convert;
using Rhino.Display;
using Rhino.Geometry;
using Surface = Lod.Core.Model.Surface;

namespace Lod.Grasshopper.Goo;

/// <summary>Grasshopper wrapper of an immutable pipeline object. Values are never modified, so duplicates share the value.</summary>
/// <typeparam name="T">Wrapped type.</typeparam>
public abstract class BemGoo<T> : GH_Goo<T>
    where T : class
{
    protected BemGoo(T value)
        : base(value)
    {
    }

    public override bool IsValid => Value is not null;

    public override string TypeDescription => $"BEMGen {TypeName}";
}

public sealed class ScheduleGoo : BemGoo<Schedule>
{
    public ScheduleGoo(Schedule value)
        : base(value)
    {
    }

    public override string TypeName => "Schedule";

    public override IGH_Goo Duplicate() => new ScheduleGoo(Value);

    public override string ToString() => $"Schedule {Value.Name} ({Value.Kind})";
}

public sealed class LoadGoo : BemGoo<LoadDefinition>
{
    public LoadGoo(LoadDefinition value)
        : base(value)
    {
    }

    public override string TypeName => "Load";

    public override IGH_Goo Duplicate() => new LoadGoo(Value);

    public override string ToString() => $"Load {Value.Type} {Value.Value} {Value.Basis}";
}

public sealed class ProgramPresetGoo : BemGoo<ProgramPreset>
{
    public ProgramPresetGoo(ProgramPreset value)
        : base(value)
    {
    }

    public override string TypeName => "Program Preset";

    public override IGH_Goo Duplicate() => new ProgramPresetGoo(Value);

    public override string ToString() => $"Preset {Value.Name} ({Value.SpaceType}, WWR {Value.WindowToWallRatio})";
}

/// <summary>Wrapper with viewport preview: zones coloured by space type, windows in blue.</summary>
/// <typeparam name="T">Wrapped type.</typeparam>
public abstract class PreviewGoo<T> : BemGoo<T>, IGH_PreviewData
    where T : class
{
    private static readonly Color WindowColour = Color.FromArgb(70, 140, 220);
    private List<(Brep Brep, DisplayMaterial Material)>? _preview;

    protected PreviewGoo(T value)
        : base(value)
    {
    }

    public BoundingBox ClippingBox
    {
        get
        {
            BoundingBox box = BoundingBox.Empty;
            foreach ((Brep brep, DisplayMaterial _) in Preview)
            {
                box.Union(brep.GetBoundingBox(false));
            }

            return box;
        }
    }

    private List<(Brep Brep, DisplayMaterial Material)> Preview => _preview ??= BuildPreview();

    public void DrawViewportMeshes(GH_PreviewMeshArgs args)
    {
        foreach ((Brep brep, DisplayMaterial material) in Preview)
        {
            args.Pipeline.DrawBrepShaded(brep, material);
        }
    }

    public void DrawViewportWires(GH_PreviewWireArgs args)
    {
        foreach ((Brep brep, DisplayMaterial _) in Preview)
        {
            args.Pipeline.DrawBrepWires(brep, args.Color);
        }
    }

    protected abstract IEnumerable<Zone> Zones { get; }

    protected abstract IEnumerable<Surface> Surfaces { get; }

    private List<(Brep, DisplayMaterial)> BuildPreview()
    {
        var items = new List<(Brep, DisplayMaterial)>();
        foreach (Zone zone in Zones)
        {
            var material = new DisplayMaterial(SpaceTypeColour(zone.SpaceType), 0.6);
            items.AddRange(RhinoGeometry.ZoneBreps(zone).Select(b => (b, material)));
        }

        var glass = new DisplayMaterial(WindowColour, 0.2);
        foreach (WallSurface wall in Surfaces.OfType<WallSurface>())
        {
            items.AddRange(RhinoGeometry.WindowBreps(wall).Select(b => (b, glass)));
        }

        return items;
    }

    private static Color SpaceTypeColour(SpaceType type) => type switch
    {
        SpaceType.DwellingUnit => Color.FromArgb(240, 200, 120),
        SpaceType.Corridor => Color.FromArgb(180, 180, 180),
        SpaceType.Stair => Color.FromArgb(200, 120, 120),
        SpaceType.Core => Color.FromArgb(160, 120, 200),
        SpaceType.Mixed => Color.FromArgb(120, 190, 160),
        _ => Color.FromArgb(150, 170, 200),
    };
}

public sealed class PlanGoo : PreviewGoo<IGeneratedPlan>
{
    public PlanGoo(IGeneratedPlan value)
        : base(value)
    {
    }

    public override string TypeName => "Plan";

    protected override IEnumerable<Zone> Zones => Value.Zones;

    protected override IEnumerable<Surface> Surfaces => Value.Surfaces;

    public override IGH_Goo Duplicate() => new PlanGoo(Value);

    public override string ToString() => $"Plan ({Value.Zones.Count} zones, {Value.Provenance.Operation})";
}

public sealed class FloorGoo : PreviewGoo<IFloor>
{
    public FloorGoo(IFloor value)
        : base(value)
    {
    }

    public override string TypeName => "Floor";

    protected override IEnumerable<Zone> Zones => Value.Zones;

    protected override IEnumerable<Surface> Surfaces => Value.Surfaces;

    public override IGH_Goo Duplicate() => new FloorGoo(Value);

    public override string ToString() => $"Floor ({Value.Zones.Count} zones, {Value.Provenance.Operation})";
}

public sealed class BuildingGoo : PreviewGoo<IGeneratedBuilding>
{
    public BuildingGoo(IGeneratedBuilding value)
        : base(value)
    {
    }

    public override string TypeName => "Building";

    protected override IEnumerable<Zone> Zones => Value.Zones;

    protected override IEnumerable<Surface> Surfaces => Value.Surfaces;

    public override IGH_Goo Duplicate() => new BuildingGoo(Value);

    public override string ToString() => $"Building ({Value.Zones.Count} zones, {Value.Provenance.Operation})";
}
```

- [x] **Step 4: Create `src/Lod.Grasshopper/Parameters/BemParameters.cs`**

```csharp
using System;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Lod.Grasshopper.Goo;
using Rhino.Geometry;

namespace Lod.Grasshopper.Parameters;

/// <summary>A parameter carrying BEMGen objects; previews them when they support it. Hidden from the toolbar.</summary>
/// <typeparam name="TGoo">Goo type.</typeparam>
public abstract class BemParameter<TGoo> : GH_Param<TGoo>, IGH_PreviewObject
    where TGoo : class, IGH_Goo
{
    protected BemParameter(string name, string nickname, string description)
        : base(name, nickname, description, ComponentCategories.Category, ComponentCategories.Info, GH_ParamAccess.item)
    {
    }

    public override GH_Exposure Exposure => GH_Exposure.hidden;

    public bool Hidden { get; set; }

    public bool IsPreviewCapable => true;

    public BoundingBox ClippingBox => Preview_ComputeClippingBox();

    public void DrawViewportMeshes(IGH_PreviewArgs args) => Preview_DrawMeshes(args);

    public void DrawViewportWires(IGH_PreviewArgs args) => Preview_DrawWires(args);
}

public sealed class ScheduleParameter : BemParameter<ScheduleGoo>
{
    public ScheduleParameter()
        : base("Schedule", "Sch", "An 8760-hour schedule.")
    {
    }

    public override Guid ComponentGuid => new("a4ae84ac-36d6-41b8-9b3d-c77cca52a2df");
}

public sealed class LoadParameter : BemParameter<LoadGoo>
{
    public LoadParameter()
        : base("Load", "L", "A load definition.")
    {
    }

    public override Guid ComponentGuid => new("9e9fbc12-9b81-42b7-8c5d-a4f8397a4487");
}

public sealed class ProgramPresetParameter : BemParameter<ProgramPresetGoo>
{
    public ProgramPresetParameter()
        : base("Program Preset", "P", "A program preset for one space type.")
    {
    }

    public override Guid ComponentGuid => new("56578999-825c-4926-afdd-ce897b53221a");
}

public sealed class PlanParameter : BemParameter<PlanGoo>
{
    public PlanParameter()
        : base("Plan", "Plan", "A detailed generated plan (IGeneratedPlan).")
    {
    }

    public override Guid ComponentGuid => new("fca85387-7aaf-41fe-9654-382b2980f18f");
}

public sealed class FloorParameter : BemParameter<FloorGoo>
{
    public FloorParameter()
        : base("Floor", "Floor", "A simplified floor (IFloor).")
    {
    }

    public override Guid ComponentGuid => new("15a085fa-f308-46b7-93e6-88a7a85e6a89");
}

public sealed class BuildingParameter : BemParameter<BuildingGoo>
{
    public BuildingParameter()
        : base("Building", "Bldg", "An aggregated building (IGeneratedBuilding).")
    {
    }

    public override Guid ComponentGuid => new("d6726442-189d-4c44-b043-b56417a3826a");
}
```

- [x] **Step 5: Build the plugin**

```bash
dotnet build src/Lod.Grasshopper -c Release
```

Expected: `BEMGen.gha` built for `net7.0`, `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`.

- [x] **Step 6: Manual check** — nothing new is visible in Grasshopper yet (the parameters are hidden and no component uses them); the Rhino check happens in Task 8.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Grasshopper/Convert src/Lod.Grasshopper/Goo src/Lod.Grasshopper/Parameters
git commit -m "feature(grasshopper): add goo, parameters, and rhino geometry conversion"
```

### Task 8: Program, generator, simplifier, aggregator, and inspect components

**Files:**
- Modify: `src/Lod.Grasshopper/Lod.Grasshopper.csproj`
- Create: `src/Lod.Grasshopper/Components/ComponentSupport.cs`
- Create: `src/Lod.Grasshopper/Components/ProgramComponents.cs`
- Create: `src/Lod.Grasshopper/Components/PipelineComponents.cs`

**Interfaces:**
- Consumes: Task 7 Goo and parameters; `Schedule.FromDailyProfiles`, `LoadDefinition.Create`, `Thermostat.Create`, `ZoneProgram.Create`, `ProgramPreset.Create`, `ProgramPresetSet.Create`, `ExampleResidentialPresets.All` (S1); `LinearPlanGenerator` (Task 4); `NoSimplification` (Task 5); `Stack`, `IFloorAggregator` (Task 6); `TextReport`, `Provenance.Describe` (Tasks 2, 4).
- Produces: `internal static class ComponentSupport` (`Report`, `Unwrap<T>`, `TryParse<TEnum>`, `Names<TEnum>`); `public abstract class FloorAggregatorComponent : GH_Component` (shared *Floors*/*Multipliers* inputs and solving; S4 aggregator components derive from it via `MultiplierDescription` and `CreateAggregator()`); the components below.

**Design:** `ComponentSupport.Report` turns every core `Diagnostic` into a runtime message (error → red error, warning → orange warning, info → remark), so the diagnostics of the core libraries are what the user sees. Enum inputs are text, parsed case-insensitively; an invalid name gives an error that lists the valid names. The *Linear Plan Generator* takes all lengths in metres regardless of model units; its numeric inputs default to the canonical configuration. *Program Preset* builds a conditioned program with a `Thermostat` when *Conditioned* is true (the default) and both setpoints are given, reports the error `A conditioned space needs both Heating and Cooling setpoints.` when one is missing, and builds an unconditioned program (setpoints ignored) when *Conditioned* is false (D-038). *Stack Floors* takes floors bottom to top and either no multipliers (all 1) or one per floor.

Components of the S2 plugin (GUIDs fixed from now on; *BEMGen Info* is unchanged from S0):

| Component (nickname) | Panel | Inputs (nickname, access, default) | Outputs | GUID |
| --- | --- | --- | --- | --- |
| Schedule (Sch) | 1 Program | Name (N, item); Kind (K, item, `Fraction`); Weekday (Wd, list of 24); Weekend (We, list of 24); First Day (D, item, `Monday`) | Schedule (Sch) | `1be96980-e9eb-4636-9ce6-4e5b6a301d1f` |
| Load (Load) | 1 Program | Type (T, item); Basis (B, item); Value (V, item); Schedule (Sch, item) | Load (L) | `c07304be-fe9c-4810-ba1d-1cac1710c386` |
| Program Preset (Preset) | 1 Program | Name (N, item); Space Type (ST, item); Loads (L, list, optional); Conditioned (Cond, item, `true`); Heating (H, item, optional; required when conditioned); Cooling (C, item, optional; required when conditioned); WWR (WWR, item) | Preset (P) | `56ca1eba-abed-4dbb-a9a7-09d8b5806231` |
| Example Residential Presets (ExPresets) | 1 Program | — | Presets (P, list) | `0239f4c9-0f19-4cf1-9d90-08db878eac8a` |
| Linear Plan Generator (Linear) | 2 Generate | Length (L, 24); Unit Depth (UD, 8); Corridor Width (CW, 2); Unit Width (UW, 10); Stair Length (SL, 4); Floor Height (FH, 3); Orientation (O, 0); Presets (P, list) | Plan (Plan) | `a4a9131e-0a0f-49e0-99a4-f26760f6810f` |
| No Simplification (Z0) | 3 Simplify | Plan (Plan, item) | Floor (Floor) | `83270abe-a13f-4f4c-a893-79739ad6e006` |
| Stack Floors (Stack) | 4 Aggregate | Floors (F, list); Multipliers (N, list of integers, optional; none = all 1) | Building (Bldg) | `6ce6524d-09b0-49fc-9b88-4c15bdcc8797` |
| Convert2BEM (2BEM) — Task 9 | 5 Convert | Building (Bldg, item) | 15 data trees (see Task 9) | `d091d70c-4de3-4f29-a900-ea4c9b777ba3` |
| Inspect (Inspect) | 6 Inspect | Object (O, item, generic: plan, floor, or building) | Report (R); Provenance (P) | `1d56a553-7a66-451f-90e2-81e744b43bdd` |

- [x] **Step 1: Reference `Lod.Generators` from the plugin** — replace `src/Lod.Grasshopper/Lod.Grasshopper.csproj` with:

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
    <ProjectReference Include="..\Lod.Generators\Lod.Generators.csproj" />
  </ItemGroup>

</Project>
```

- [x] **Step 2: Create `src/Lod.Grasshopper/Components/ComponentSupport.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Lod.Core.Common;

namespace Lod.Grasshopper.Components;

/// <summary>Adapters between core diagnostics and Grasshopper runtime messages, and text-to-enum input parsing.</summary>
internal static class ComponentSupport
{
    /// <summary>Adds each diagnostic as a runtime message: errors as errors, warnings as warnings, info as remarks.</summary>
    public static void Report(GH_Component component, IEnumerable<Diagnostic> diagnostics)
    {
        foreach (Diagnostic diagnostic in diagnostics)
        {
            GH_RuntimeMessageLevel level = diagnostic.Severity switch
            {
                DiagnosticSeverity.Error => GH_RuntimeMessageLevel.Error,
                DiagnosticSeverity.Warning => GH_RuntimeMessageLevel.Warning,
                _ => GH_RuntimeMessageLevel.Remark,
            };
            component.AddRuntimeMessage(level, diagnostic.ToString());
        }
    }

    /// <summary>Reports the diagnostics and returns the value, or <c>null</c> on failure.</summary>
    public static T? Unwrap<T>(GH_Component component, Result<T> result)
        where T : class
    {
        Report(component, result.Diagnostics);
        return result.IsSuccess ? result.Value : null;
    }

    /// <summary>Parses an enum name case-insensitively; on failure adds an error listing the valid names.</summary>
    public static bool TryParse<TEnum>(GH_Component component, string text, out TEnum value)
        where TEnum : struct
    {
        if (Enum.TryParse(text?.Trim(), ignoreCase: true, out value) && Enum.IsDefined(typeof(TEnum), value))
        {
            return true;
        }

        component.AddRuntimeMessage(
            GH_RuntimeMessageLevel.Error,
            $"'{text}' is not a valid {typeof(TEnum).Name}. Use one of: {string.Join(", ", Enum.GetNames(typeof(TEnum)))}.");
        return false;
    }

    /// <summary>The valid names of an enum, for input descriptions.</summary>
    public static string Names<TEnum>() => string.Join(", ", Enum.GetNames(typeof(TEnum)).Select(n => n));
}
```

- [x] **Step 3: Create `src/Lod.Grasshopper/Components/ProgramComponents.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using Grasshopper.Kernel;
using Lod.Core.Loads;
using Lod.Core.Programs;
using Lod.Core.Schedules;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;

namespace Lod.Grasshopper.Components;

public sealed class ScheduleComponent : GH_Component
{
    public ScheduleComponent()
        : base("Schedule", "Sch", "An 8760-hour schedule from a 24-hour weekday and weekend profile (holidays not modelled).", ComponentCategories.Category, ComponentCategories.Program)
    {
    }

    public override Guid ComponentGuid => new("1be96980-e9eb-4636-9ce6-4e5b6a301d1f");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddTextParameter("Name", "N", "Schedule name.", GH_ParamAccess.item);
        pManager.AddTextParameter("Kind", "K", $"Value meaning: {ComponentSupport.Names<ScheduleKind>()}.", GH_ParamAccess.item, nameof(ScheduleKind.Fraction));
        pManager.AddNumberParameter("Weekday", "Wd", "24 hourly values for Monday to Friday.", GH_ParamAccess.list);
        pManager.AddNumberParameter("Weekend", "We", "24 hourly values for Saturday and Sunday.", GH_ParamAccess.list);
        pManager.AddTextParameter("First Day", "D", "Weekday of 1 January.", GH_ParamAccess.item, nameof(DayOfWeek.Monday));
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new ScheduleParameter(), "Schedule", "Sch", "The schedule.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        string name = string.Empty;
        string kindText = string.Empty;
        string dayText = string.Empty;
        var weekday = new List<double>();
        var weekend = new List<double>();
        if (!DA.GetData(0, ref name) || !DA.GetData(1, ref kindText) || !DA.GetDataList(2, weekday) || !DA.GetDataList(3, weekend) || !DA.GetData(4, ref dayText))
        {
            return;
        }

        if (!ComponentSupport.TryParse(this, kindText, out ScheduleKind kind) || !ComponentSupport.TryParse(this, dayText, out DayOfWeek firstDay))
        {
            return;
        }

        Schedule? schedule = ComponentSupport.Unwrap(this, Schedule.FromDailyProfiles(name, kind, weekday, weekend, firstDay));
        if (schedule is not null)
        {
            DA.SetData(0, new ScheduleGoo(schedule));
        }
    }
}

public sealed class LoadComponent : GH_Component
{
    public LoadComponent()
        : base("Load", "Load", "A load: design value in its basis and a fraction schedule. Magnitudes are people, W, or m³/h.", ComponentCategories.Category, ComponentCategories.Program)
    {
    }

    public override Guid ComponentGuid => new("c07304be-fe9c-4810-ba1d-1cac1710c386");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddTextParameter("Type", "T", $"Load type: {ComponentSupport.Names<LoadType>()}.", GH_ParamAccess.item);
        pManager.AddTextParameter("Basis", "B", $"Basis: {ComponentSupport.Names<LoadBasis>()}.", GH_ParamAccess.item);
        pManager.AddNumberParameter("Value", "V", "Design value in the basis' unit.", GH_ParamAccess.item);
        pManager.AddParameter(new ScheduleParameter(), "Schedule", "Sch", "A fraction schedule.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new LoadParameter(), "Load", "L", "The load.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        string typeText = string.Empty;
        string basisText = string.Empty;
        double value = 0.0;
        ScheduleGoo? schedule = null;
        if (!DA.GetData(0, ref typeText) || !DA.GetData(1, ref basisText) || !DA.GetData(2, ref value) || !DA.GetData(3, ref schedule) || schedule is null)
        {
            return;
        }

        if (!ComponentSupport.TryParse(this, typeText, out LoadType type) || !ComponentSupport.TryParse(this, basisText, out LoadBasis basis))
        {
            return;
        }

        LoadDefinition? load = ComponentSupport.Unwrap(this, LoadDefinition.Create(type, basis, value, schedule.Value));
        if (load is not null)
        {
            DA.SetData(0, new LoadGoo(load));
        }
    }
}

public sealed class ProgramPresetComponent : GH_Component
{
    public ProgramPresetComponent()
        : base("Program Preset", "Preset", "Loads, conditioning and setpoints, and window-to-wall ratio for one space type (D-024, D-038).", ComponentCategories.Category, ComponentCategories.Program)
    {
    }

    public override Guid ComponentGuid => new("56ca1eba-abed-4dbb-a9a7-09d8b5806231");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddTextParameter("Name", "N", "Preset name.", GH_ParamAccess.item);
        pManager.AddTextParameter("Space Type", "ST", $"Space type: {ComponentSupport.Names<SpaceType>()}.", GH_ParamAccess.item);
        pManager.AddParameter(new LoadParameter(), "Loads", "L", "Loads; at most one per type and basis (D-047).", GH_ParamAccess.list);
        pManager.AddBooleanParameter("Conditioned", "Cond", "Whether the space is conditioned (D-038). Conditioned spaces need both setpoints.", GH_ParamAccess.item, true);
        pManager.AddParameter(new ScheduleParameter(), "Heating", "H", "Heating setpoint, a temperature schedule (°C); conditioned spaces only.", GH_ParamAccess.item);
        pManager.AddParameter(new ScheduleParameter(), "Cooling", "C", "Cooling setpoint, a temperature schedule (°C); conditioned spaces only.", GH_ParamAccess.item);
        pManager.AddNumberParameter("WWR", "WWR", "Window-to-wall ratio in [0, 1) used by the plan generator for every exterior wall.", GH_ParamAccess.item);
        pManager[2].Optional = true;
        pManager[4].Optional = true;
        pManager[5].Optional = true;
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new ProgramPresetParameter(), "Preset", "P", "The program preset.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        string name = string.Empty;
        string typeText = string.Empty;
        var loads = new List<LoadGoo>();
        bool conditioned = true;
        ScheduleGoo? heating = null;
        ScheduleGoo? cooling = null;
        double wwr = 0.0;
        if (!DA.GetData(0, ref name) || !DA.GetData(1, ref typeText) || !DA.GetData(3, ref conditioned) || !DA.GetData(6, ref wwr))
        {
            return;
        }

        DA.GetDataList(2, loads);
        DA.GetData(4, ref heating);
        DA.GetData(5, ref cooling);
        if (!ComponentSupport.TryParse(this, typeText, out SpaceType spaceType))
        {
            return;
        }

        Thermostat? thermostat = null;
        if (conditioned)
        {
            if (heating is null || cooling is null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "A conditioned space needs both Heating and Cooling setpoints.");
                return;
            }

            thermostat = ComponentSupport.Unwrap(this, Thermostat.Create(heating.Value, cooling.Value));
            if (thermostat is null)
            {
                return;
            }
        }

        ZoneProgram? program = ComponentSupport.Unwrap(this, ZoneProgram.Create(loads.Where(l => l is not null).Select(l => l.Value), thermostat));
        ProgramPreset? preset = program is null ? null : ComponentSupport.Unwrap(this, ProgramPreset.Create(name, spaceType, program, wwr));
        if (preset is not null)
        {
            DA.SetData(0, new ProgramPresetGoo(preset));
        }
    }
}

public sealed class ExampleResidentialPresetsComponent : GH_Component
{
    public ExampleResidentialPresetsComponent()
        : base(
            "Example Residential Presets",
            "ExPresets",
            "Illustrative presets for dwelling unit, corridor, and stair. Round numbers for testing, NOT sourced from DOE prototypes or standards.",
            ComponentCategories.Category,
            ComponentCategories.Program)
    {
    }

    public override Guid ComponentGuid => new("0239f4c9-0f19-4cf1-9d90-08db878eac8a");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new ProgramPresetParameter(), "Presets", "P", "Example presets.", GH_ParamAccess.list);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Illustrative values only; not sourced from DOE prototypes.");
        DA.SetDataList(0, ExampleResidentialPresets.All.Presets.Select(p => new ProgramPresetGoo(p)));
    }
}
```

- [x] **Step 4: Create `src/Lod.Grasshopper/Components/PipelineComponents.cs`**

```csharp
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Lod.Core.Buildings;
using Lod.Core.Common;
using Lod.Core.Model;
using Lod.Core.Programs;
using Lod.Core.Simplification;
using Lod.Generators.Linear;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;

namespace Lod.Grasshopper.Components;

public sealed class LinearPlanGeneratorComponent : GH_Component
{
    public LinearPlanGeneratorComponent()
        : base(
            "Linear Plan Generator",
            "Linear",
            "Detailed linear block plan: west stair, double-loaded corridor, one zone per dwelling unit. All lengths in metres regardless of model units.",
            ComponentCategories.Category,
            ComponentCategories.Generate)
    {
    }

    public override Guid ComponentGuid => new("a4a9131e-0a0f-49e0-99a4-f26760f6810f");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddNumberParameter("Length", "L", "Plan length along X, m.", GH_ParamAccess.item, 24.0);
        pManager.AddNumberParameter("Unit Depth", "UD", "Depth of each unit row, m.", GH_ParamAccess.item, 8.0);
        pManager.AddNumberParameter("Corridor Width", "CW", "Corridor width, m.", GH_ParamAccess.item, 2.0);
        pManager.AddNumberParameter("Unit Width", "UW", "Target unit width, m; the row is divided evenly.", GH_ParamAccess.item, 10.0);
        pManager.AddNumberParameter("Stair Length", "SL", "Length of the west stair, m.", GH_ParamAccess.item, 4.0);
        pManager.AddNumberParameter("Floor Height", "FH", "Floor-to-floor height, m.", GH_ParamAccess.item, 3.0);
        pManager.AddNumberParameter("Orientation", "O", "Clockwise rotation of plan north from true north, degrees.", GH_ParamAccess.item, 0.0);
        pManager.AddParameter(new ProgramPresetParameter(), "Presets", "P", "Program presets for DwellingUnit, Corridor, and Stair.", GH_ParamAccess.list);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new PlanParameter(), "Plan", "Plan", "The detailed plan.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        double[] values = new double[7];
        for (int i = 0; i < values.Length; i++)
        {
            if (!DA.GetData(i, ref values[i]))
            {
                return;
            }
        }

        var presets = new List<ProgramPresetGoo>();
        if (!DA.GetDataList(7, presets))
        {
            return;
        }

        ProgramPresetSet? set = ComponentSupport.Unwrap(this, ProgramPresetSet.Create(presets.Where(p => p is not null).Select(p => p.Value)));
        if (set is null)
        {
            return;
        }

        var parameters = new LinearPlanParameters(values[0], values[1], values[2], values[3], values[4], values[5], values[6]);
        IGeneratedPlan? plan = ComponentSupport.Unwrap(this, new LinearPlanGenerator(ToleranceSettings.Default).Generate(parameters, set));
        if (plan is not null)
        {
            DA.SetData(0, new PlanGoo(plan));
        }
    }
}

public sealed class NoSimplificationComponent : GH_Component
{
    public NoSimplificationComponent()
        : base("No Simplification", "Z0", "Keeps the detailed plan's zones and surfaces (Z0).", ComponentCategories.Category, ComponentCategories.Simplify)
    {
    }

    public override Guid ComponentGuid => new("83270abe-a13f-4f4c-a893-79739ad6e006");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new PlanParameter(), "Plan", "Plan", "Detailed plan.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floor", "Floor", "The floor.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        PlanGoo? plan = null;
        if (!DA.GetData(0, ref plan) || plan is null)
        {
            return;
        }

        IFloor? floor = ComponentSupport.Unwrap(this, new NoSimplification().Simplify(plan.Value));
        if (floor is not null)
        {
            DA.SetData(0, new FloorGoo(floor));
        }
    }
}

/// <summary>Shared inputs and solving of the floor aggregator components: floors bottom to top and their multipliers.</summary>
public abstract class FloorAggregatorComponent : GH_Component
{
    protected FloorAggregatorComponent(string name, string nickname, string description)
        : base(name, nickname, description, ComponentCategories.Category, ComponentCategories.Aggregate)
    {
    }

    protected override Bitmap? Icon => null;

    protected abstract string MultiplierDescription { get; }

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddParameter(new FloorParameter(), "Floors", "F", "Floors, bottom to top.", GH_ParamAccess.list);
        pManager.AddIntegerParameter("Multipliers", "N", MultiplierDescription, GH_ParamAccess.list);
        pManager[1].Optional = true;
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddParameter(new BuildingParameter(), "Building", "Bldg", "The building.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        var floors = new List<FloorGoo>();
        var multipliers = new List<int>();
        if (!DA.GetDataList(0, floors) || floors.Any(f => f is null))
        {
            return;
        }

        DA.GetDataList(1, multipliers);
        if (multipliers.Count != 0 && multipliers.Count != floors.Count)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Give one multiplier per floor ({floors.Count}), or none for all 1.");
            return;
        }

        FloorEntry[] entries = floors.Select((f, i) => new FloorEntry(f.Value, multipliers.Count == 0 ? 1 : multipliers[i])).ToArray();
        IGeneratedBuilding? building = ComponentSupport.Unwrap(this, CreateAggregator().Aggregate(entries));
        if (building is not null)
        {
            DA.SetData(0, new BuildingGoo(building));
        }
    }

    protected abstract IFloorAggregator CreateAggregator();
}

public sealed class StackFloorsComponent : FloorAggregatorComponent
{
    public StackFloorsComponent()
        : base("Stack Floors", "Stack", "All storeys explicit: each floor is repeated by its multiplier and stacked; inter-storey surfaces are interzone.")
    {
    }

    public override Guid ComponentGuid => new("6ce6524d-09b0-49fc-9b88-4c15bdcc8797");

    protected override string MultiplierDescription => "How many storeys each floor stands for (repeated explicitly). Default 1.";

    protected override IFloorAggregator CreateAggregator() => new Stack(ToleranceSettings.Default);
}

public sealed class InspectComponent : GH_Component
{
    public InspectComponent()
        : base("Inspect", "Inspect", "Text report and provenance of a plan, floor, or building.", ComponentCategories.Category, ComponentCategories.Inspect)
    {
    }

    public override Guid ComponentGuid => new("1d56a553-7a66-451f-90e2-81e744b43bdd");

    protected override Bitmap? Icon => null;

    protected override void RegisterInputParams(GH_InputParamManager pManager)
    {
        pManager.AddGenericParameter("Object", "O", "A plan, floor, or building.", GH_ParamAccess.item);
    }

    protected override void RegisterOutputParams(GH_OutputParamManager pManager)
    {
        pManager.AddTextParameter("Report", "R", "Zones, loads, and surfaces.", GH_ParamAccess.item);
        pManager.AddTextParameter("Provenance", "P", "How the object was produced, with code version.", GH_ParamAccess.item);
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        IGH_Goo? goo = null;
        if (!DA.GetData(0, ref goo) || goo is null)
        {
            return;
        }

        (string Report, Provenance Provenance)? described = goo switch
        {
            PlanGoo plan => (TextReport.Describe(plan.Value), plan.Value.Provenance),
            FloorGoo floor => (TextReport.Describe(floor.Value), floor.Value.Provenance),
            BuildingGoo building => (TextReport.Describe(building.Value), building.Value.Provenance),
            _ => null,
        };
        if (described is null)
        {
            AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Expected a plan, floor, or building, got {goo.TypeName}.");
            return;
        }

        DA.SetData(0, described.Value.Report);
        DA.SetData(1, described.Value.Provenance.Describe());
    }
}
```

- [x] **Step 5: Build the solution and run all tests**

```bash
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release --no-build
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`; test counts unchanged (94, 17, 9 on net8.0). The plugin output folder `src/Lod.Grasshopper/bin/Release/net7.0/` now contains `BEMGen.gha` together with `Lod.Core.dll`, `Lod.Generators.dll`, and `Clipper2Lib.dll`.

- [x] **Step 6: Manual check in Rhino 8 (person)** — Rhino must be closed while Step 5 builds (Grasshopper loads plugins only at start-up). Then start Rhino with the freshly built plugin loaded as `docs/development/grasshopper-smoke-test.md` ("Load the plugin") describes, and confirm:
  - panels *1 Program*, *2 Generate*, *3 Simplify*, *4 Aggregate*, and *6 Inspect* show the components of the table above;
  - *Example Residential Presets* → *Linear Plan Generator* (defaults) → *No Simplification* → *Stack Floors* → *Inspect* solves without errors, the plan, floor, and building previews show in the viewport, and the *Report* output starts with `building orientation=0.000000 sources=1`.

  The complete S2 checklist runs in Task 10.

- [x] **Step 7: Commit**

```bash
git add src/Lod.Grasshopper/Lod.Grasshopper.csproj src/Lod.Grasshopper/Components/ComponentSupport.cs src/Lod.Grasshopper/Components/ProgramComponents.cs src/Lod.Grasshopper/Components/PipelineComponents.cs
git commit -m "feature(grasshopper): add program, generator, simplifier, stack, and inspect components"
```

- [x] **Step 8: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/grasshopper-pipeline-components
git push origin main
git branch -d feature/grasshopper-pipeline-components
```

Expected from `verify.ps1`: three `Passed!` lines (94, 17, 9 on net8.0), then `VERIFY PASSED`.

---

## Slice F — `feature/convert-bem-neutral`

### Task 9: *Convert2BEM* (provisional neutral output) and its documentation

**Files:**
- Create: `src/Lod.Grasshopper/Components/Convert2BemComponent.cs` (S2 version, without validation; S3 replaces it with the validating version)
- Create: `docs/architecture/convert2bem.md`

**Interfaces:**
- Consumes: `BuildingGoo`, `BuildingParameter`, `RhinoGeometry` (Task 7); `IGeneratedBuilding`, `Zone`, `Surface`, `WallSurface`, `HorizontalSurface`, `InternalMass` (Task 2); `LoadDefinition` (S1).
- Produces: component *Convert2BEM* (`2BEM`, panel *5 Convert*, GUID `d091d70c-4de3-4f29-a900-ea4c9b777ba3`) with input 0 *Building* and the 15 tree outputs (indices 0–14) documented in `docs/architecture/convert2bem.md`.

**Design:** the component loops over the building's zones in order and writes branch `{i}` of every output for zone `i`; load schedules go to `{i;k}`. *Conditioned* reports `ZoneProgram.IsConditioned`; the setpoint branches of an unconditioned zone exist but are empty (D-038). Windows are converted at their explicit positions (D-039). Geometry comes from `RhinoGeometry` (model units); all numbers are copied unchanged (SI). It computes nothing new. Its output is the neutral layout of D-023, adapted once a ClimateStudio reference definition exists.

- [x] **Step 1: Create the slice branch**

```bash
git switch -c feature/convert-bem-neutral main
```

- [x] **Step 2: Create `src/Lod.Grasshopper/Components/Convert2BemComponent.cs`**

```csharp
using System;
using System.Drawing;
using System.Linq;
using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Lod.Core.Loads;
using Lod.Core.Model;
using Lod.Grasshopper.Convert;
using Lod.Grasshopper.Goo;
using Lod.Grasshopper.Parameters;
using Rhino.Geometry;
using Surface = Lod.Core.Model.Surface;

namespace Lod.Grasshopper.Components;

/// <summary>
/// Converts a building into neutral Grasshopper data for a ClimateStudio definition (D-023, provisional): one tree branch per zone,
/// in building zone order. The output layout is documented in docs/architecture/convert2bem.md.
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
    }

    protected override void SolveInstance(IGH_DataAccess DA)
    {
        BuildingGoo? goo = null;
        if (!DA.GetData(0, ref goo) || goo is null)
        {
            return;
        }

        IGeneratedBuilding building = goo.Value;
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
    }

    private static Brep[] SurfaceBreps(Surface surface) => surface switch
    {
        WallSurface wall => RhinoGeometry.WallBrep(wall) is { } brep ? new[] { brep } : new Brep[0],
        HorizontalSurface horizontal => RhinoGeometry.HorizontalBreps(horizontal).ToArray(),
        _ => new Brep[0],
    };
}
```

- [x] **Step 3: Build the plugin**

```bash
dotnet build src/Lod.Grasshopper -c Release
```

Expected: `Build succeeded.` with `0 Warning(s)` and `0 Error(s)`.

- [x] **Step 4: Document the output** — create `docs/architecture/convert2bem.md` with exactly this content:

````markdown
# Convert2BEM output

> **Status:** Provisional (D-023) · **Since:** S2 (`v0.2.0`) · **Component:** *Convert2BEM* (`2BEM`), panel *5 Convert*, GUID `d091d70c-4de3-4f29-a900-ea4c9b777ba3`

## Purpose

*Convert2BEM* is the last step of the BEMGen pipeline (D-018). It turns an `IGeneratedBuilding` into plain Grasshopper data trees that serve the two uses of the pipeline's deliverable (D-016): visualising and checking the building in Rhino, and wiring zones, programs, and surfaces into a ClimateStudio definition. It does not run a simulation.

ClimateStudio is the downstream target (D-006, D-016), but no ClimateStudio reference definition is available yet (D-023). Until one is, the component produces the neutral layout described here: one tree branch per zone, standard Grasshopper types (Brep, text, integer, Boolean, number), and every number in a stated unit. Once a reference definition exists, the output is adapted to ClimateStudio's actual inputs; that change updates this document and the decision log.

The component is a thin adaptor (GLOBAL.md, architecture rule 3): it converts geometry to Rhino Breps through `Lod.Grasshopper.Convert.RhinoGeometry` and copies zone programs and boundary conditions. It computes no new quantities.

## Input

| Index | Name | Nickname | Access | Content |
| --- | --- | --- | --- | --- |
| 0 | Building | Bldg | item | An `IGeneratedBuilding` from a floor aggregator; in S2 from *Stack Floors*. |

In S2 the building is converted as given; no validation exists yet. From S3 the component validates the building first and blocks conversion when validation fails, unless an override is set, which is then recorded in a provenance output (GLOBAL.md, scientific rule 6). That change adds an input and an output and updates this document.

## Zone order and tree paths

- Branch `{i}` belongs to zone `i` of `IGeneratedBuilding.Zones`, in the building's zone order. For *Stack Floors* that is storey by storey from the bottom (zone IDs `L0/…`, `L1/…`, …) and, within a storey, the floor's zone order; for the linear plan `ST`, `CO`, `US1` … `USn`, `UN1` … `UNn`.
- Paths are explicit, so `{i}` means zone `i` in every output. *Names*, *Space Types*, *Multipliers*, *Conditioned*, *Heating Setpoints*, *Cooling Setpoints*, and *Internal Mass* always have a branch for every zone; the setpoint branches of an unconditioned zone are empty. Another output can lack the branch of a zone that has no items of its kind (for example a zone without windows or without loads); match branches by path, not by position.
- Loads: item `k` of branch `{i}` in *Load Types*, *Load Bases*, and *Load Values* describes the same load, and its schedule is branch `{i;k}` of *Load Schedules*. Loads are in program order: by `LoadType` (Occupancy, Lighting, ElectricEquipment, GasEquipment, DomesticHotWater, Ventilation, Infiltration), then by `LoadBasis` (PerFloorArea, PerPerson, Absolute, PerExteriorWallArea, AirChangesPerHour). A zone has at most one load per type and basis; components of the same type in different bases add up (D-047).
- *Surfaces* and *Boundaries* are aligned item by item within a branch.
- *Windows* are not aligned with *Surfaces*: branch `{i}` lists every window of zone `i`'s walls, wall by wall and, within a wall, by offset; walls without windows contribute nothing.

## Outputs

| Index | Name | Nickname | Tree layout | Content | Units |
| --- | --- | --- | --- | --- | --- |
| 0 | Zones | Z | `{i}`: one closed Brep per zone part | Zone volume: each part's floor polygon extruded by its floor-to-floor height. Zones have one part, except in `SingleZoneMerged` buildings (S4), which have one part per storey. | model units |
| 1 | Names | N | `{i}`: one text | Zone ID, e.g. `L0/US1` (the floor aggregator prefixes `L{k}/` for storey `k`). | — |
| 2 | Space Types | ST | `{i}`: one text | `SpaceType` name: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, or `Mixed`. | — |
| 3 | Multipliers | M | `{i}`: one integer | Zone multiplier; always 1 for *Stack Floors*. | — |
| 4 | Conditioned | Cd | `{i}`: one Boolean | Whether the zone is conditioned, i.e. its program has a thermostat (D-038). | — |
| 5 | Load Types | LT | `{i}`: one text per load | `LoadType` name of each load. | — |
| 6 | Load Bases | LB | `{i}`: one text per load | `LoadBasis` name of each load, aligned with *Load Types*. | — |
| 7 | Load Values | LV | `{i}`: one number per load | Design value of each load in its basis, aligned with *Load Types*. | SI, by basis (see below) |
| 8 | Load Schedules | LS | `{i;k}`: 8760 numbers | Hourly fraction schedule of load `k` of zone `i` (non-leap year). | fraction, 0–1 |
| 9 | Heating Setpoints | HS | `{i}`: 8760 numbers, or empty | Hourly heating setpoint of a conditioned zone; the branch is empty for an unconditioned zone. | °C |
| 10 | Cooling Setpoints | CS | `{i}`: 8760 numbers, or empty | Hourly cooling setpoint of a conditioned zone; the branch is empty for an unconditioned zone. | °C |
| 11 | Surfaces | S | `{i}`: Breps | The zone's surfaces in building surface order (for *Stack Floors*: its walls, then its floors and ceilings). A wall is one planar rectangle; a floor or ceiling gives the planar Breps of its polygon. | model units |
| 12 | Boundaries | B | `{i}`: one text per *Surfaces* item | Boundary condition of the surface at the same index (format below). | — |
| 13 | Windows | W | `{i}`: Breps | Every explicit window of the zone's walls, as a rectangle in the wall's plane at its offset along the wall and its sill height (D-039). For S2 buildings that is one centered window per outdoor wall, as the generator placed it (D-026). | model units |
| 14 | Internal Mass | IM | `{i}`: one number | Exposed internal-mass area: the sum of slab area × exposed faces over the zone's internal-mass objects; 0 when it has none. | m² |

### Load value units

Each load's design magnitude is its value times the basis quantity (ADR-007). Magnitudes are in people (Occupancy), W (Lighting, ElectricEquipment, GasEquipment), or m³/h (DomesticHotWater, Ventilation, Infiltration).

| Load Basis | Unit of the Load Value |
| --- | --- |
| `PerFloorArea` | magnitude per m² of zone floor area |
| `PerPerson` | magnitude per occupant |
| `Absolute` | magnitude per zone |
| `PerExteriorWallArea` | magnitude per m² of gross exterior wall area (walls with an outdoor boundary, windows included) |
| `AirChangesPerHour` | air changes per hour (1/h); the magnitude is value × zone volume, in m³/h |

Load values, conditioning, and setpoints are copied from the zone program unchanged. For Z0 buildings (*No Simplification*, *Stack Floors*) they are the program preset values; with the example presets the stair is unconditioned (illustrative, D-038).

## Boundary text format

| Text | Meaning |
| --- | --- |
| `Outdoors` | Outdoor air: exterior walls, roofs (ceilings of the top storey), the part of a ceiling not covered by the storey above (setbacks), and the part of a floor not covered by the storey below. |
| `Ground` | Ground contact: floors of the lowest storey. |
| `Adiabatic` | No heat transfer. *Stack Floors* never produces it; `FloorAreaMultiplier` (S4) uses it where the floors and ceilings of representative storeys overlap the representative storey below or above (D-046). |
| `Interzone:<zone ID>` | Another zone of the same building, e.g. `Interzone:L1/US1`: interior walls and the floors and ceilings between storeys. Every interzone surface has a matching surface in the other zone that refers back to it. |

There is no separate roof condition: a roof is an `Outdoors` ceiling. `Unresolved` marks floors and ceilings of plans and floors before stacking; a building from a floor aggregator has none.

## Units and coordinates

- Pipeline geometry is in metres in a building-local plan frame: +Y is plan north, and elevation 0 is the bottom of the lowest storey.
- *Convert2BEM* scales every Brep from metres to the model units of the active Rhino document (`RhinoMath.UnitScale(UnitSystem.Meters, doc.ModelUnitSystem)`), about the world origin. Without an active document the scale is 1.
- Only geometry is converted. *Load Values*, *Load Schedules*, setpoints, and *Internal Mass* stay in the units listed above, whatever the model units are.
- The building orientation (`IGeneratedBuilding.OrientationDegrees`, the clockwise rotation of plan north from true north) is not applied to the geometry and is not an output; see *Not yet decided*.

## Internal mass

An `InternalMass` object (D-031) describes a slab whose faces both lie inside one zone. This happens only when `SingleZoneMerged` (S4, D-021) merges all storeys into one zone: the slabs between storeys are then no longer boundaries between two zones and become internal mass of the single zone, keeping their construction and area (D-031; ADR-009 in S4). Each object records the slab area (one face) and the number of faces exposed to the zone air. *Internal Mass* gives, per zone, the sum of slab area × exposed faces: the slab surface area that exchanges heat with the zone air, in m². Walls between merged zones are discarded, not turned into internal mass (D-034).

*Stack Floors* creates no internal mass, so in S2 the output is 0 for every zone; `SingleZoneMerged` populates it from S4.

## Not yet decided

- **ClimateStudio mapping.** Which ClimateStudio components and inputs each output feeds, and in what form, is unknown until a ClimateStudio reference definition exists (D-023). This includes how loads and their schedules, conditioning and setpoints, windows, boundary conditions, zone multipliers, and internal mass are represented there. The layout above will change accordingly.
- **Orientation.** The geometry stays in the plan frame and the orientation is not output. Whether *Convert2BEM* rotates the geometry to true north or passes the orientation on is decided together with the ClimateStudio mapping.
- **Constructions.** *Convert2BEM* outputs no constructions or materials. Where they come from for ClimateStudio is not decided (for the IDF converter, ADR-010 in S6 decides it).
- **Simulation.** Not part of the pipeline: ClimateStudio or EnergyPlus runs only after the pipeline, outside BEMGen (D-016). *Convert2BEM* prepares inputs and nothing else.
````

- [x] **Step 5: Manual check in Rhino 8 (person)** — close Rhino, rebuild, and start Rhino again (Grasshopper loads plugins only at start-up); connect *Convert2BEM* (panel *5 Convert*) to the building of the Task 8 check (one storey), and confirm that every one of the 15 outputs carries data with branches `{0}` to `{5}` (`{i;k}` for *Load Schedules*), that *Names* reads `L0/ST`, `L0/CO`, `L0/US1`, `L0/US2`, `L0/UN1`, `L0/UN2`, that *Conditioned* is `False` for `{0}` (the stair) and `True` otherwise, that *Heating Setpoints* and *Cooling Setpoints* `{0}` are empty while the other branches hold 8760 values, and that every output matches the table in `docs/architecture/convert2bem.md`.

- [x] **Step 6: Commit**

```bash
git add src/Lod.Grasshopper/Components/Convert2BemComponent.cs docs/architecture/convert2bem.md
git commit -m "feature(grasshopper): add provisional neutral convert2bem output"
```

### Task 10: Manual Grasshopper smoke test and example definition

**Files:**
- Modify: `docs/development/grasshopper-smoke-test.md` (append the S2 checklist)
- Create (by a person in Rhino 8): `examples/grasshopper/pipeline-skeleton.gh`

**Interfaces:** none (documentation and a manual check). `.gitattributes` already marks `*.gh` as binary, and `.gitignore` deliberately keeps `.gh` files under `examples/` tracked (only `*_autosave.gh` is ignored).

- [x] **Step 1: Append the S2 checklist** — add the following at the end of `docs/development/grasshopper-smoke-test.md`, after the S0 checklist (separated by one blank line), so it nests under the guide's `## Stage checklists` section:

````markdown
### S2 checklist — pipeline skeleton (`v0.2.0`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings) and load it as described above. Runtime: .NET Core (Rhino 8's default). From S2 on, `BEMGen.gha` also needs `Lod.Generators.dll` and `Clipper2Lib.dll` next to it; the build puts them in `src/Lod.Grasshopper/bin/Release/net7.0/` together with `Lod.Core.dll`. Record the result as described in [Recording the result](#recording-the-result).

#### Toolbar

- [ ] The *BEMGen* tab shows the panels *0 Info*, *1 Program*, *2 Generate*, *3 Simplify*, *4 Aggregate*, *5 Convert*, and *6 Inspect*.
- [ ] *0 Info*: BEMGen Info. *1 Program*: Schedule, Load, Program Preset, Example Residential Presets. *2 Generate*: Linear Plan Generator. *3 Simplify*: No Simplification. *4 Aggregate*: Stack Floors. *5 Convert*: Convert2BEM. *6 Inspect*: Inspect.
- [ ] The BEMGen parameters (Schedule, Load, Program Preset, Plan, Floor, Building) do not appear on the toolbar; they exist only as component inputs and outputs.

#### Pipeline

1. Place *Example Residential Presets*.
   - [ ] It shows the remark "Illustrative values only; not sourced from DOE prototypes." and outputs three presets: Example Dwelling Unit (DwellingUnit, WWR 0.3), Example Corridor (Corridor, WWR 0.2), Example Stair (Stair, WWR 0.1). In these example presets the dwelling units and the corridor are conditioned and the stair is not.
2. Place *Linear Plan Generator*, keep every number input at its default (Length 24, Unit Depth 8, Corridor Width 2, Unit Width 10, Stair Length 4, Floor Height 3, Orientation 0), and connect *Presets*.
   - [ ] No warning or error.
   - [ ] The viewport previews a 24 m × 18 m plan with six zones: a stair at the west end, a corridor, and two units on each side of the corridor, coloured by space type (dwelling units sand, corridor grey, stair red).
   - [ ] Every exterior wall shows exactly one blue window, centered on the wall; interior walls have none.
3. Connect *No Simplification* to the plan.
   - [ ] The *Floor* output previews the same six zones and windows.
4. Connect *Stack Floors*: the floor into *Floors*, and a panel containing `3` into *Multipliers*.
   - [ ] The building preview shows three storeys, 9 m high, with windows on every storey.
5. Connect *Inspect* to the building, with panels on *Report* and *Provenance*.
   - [ ] The first line of *Report* is `building orientation=0.000000 sources=3`, followed by the zones `L0/ST` to `L2/UN2` (18 zones).
   - [ ] Each stair zone (`L0/ST`, `L1/ST`, `L2/ST`) is followed by its loads and the line `unconditioned`; every other zone has a `setpoints heatingMean=21.000000 coolingMean=24.000000` line.
   - [ ] Every outdoor wall line ends with one `window(offset=… sill=… W×H)` entry, e.g. `L0/ST/W1 … glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)`; interzone wall lines have none.
   - [ ] *Provenance* has three lines: `Stack Multipliers=3`, then (indented) `NoSimplification`, then (indented twice) `LinearPlanGenerator` with its parameters and `Presets=DwellingUnit:Example Dwelling Unit;Corridor:Example Corridor;Stair:Example Stair`; every line ends with the code version in brackets.
6. Connect *Convert2BEM* to the building and inspect its outputs (panels or Param Viewers).
   - [ ] All 15 outputs carry data. *Names* has 18 branches, `{0}` `L0/ST` to `{17}` `L2/UN2`.
   - [ ] *Conditioned* is `False` for the three stair branches (`{0}`, `{6}`, `{12}`) and `True` for all others.
   - [ ] *Zones* holds one closed Brep per branch.
   - [ ] *Boundaries* `{0}` reads `Outdoors`, `Interzone:L0/US1`, `Interzone:L0/CO`, `Interzone:L0/UN1`, `Outdoors`, `Outdoors`, `Ground`, `Interzone:L1/ST`, and *Surfaces* `{0}` has 8 Breps.
   - [ ] *Windows* `{0}` holds 3 Breps (the stair's south, north, and west windows).
   - [ ] *Load Schedules* has branches `{i;k}` of 8760 values; *Heating Setpoints* and *Cooling Setpoints* have 8760 values in every branch except the empty stair branches `{0}`, `{6}`, and `{12}`.
   - [ ] *Internal Mass* is 0 in every branch.

#### Changes and errors

- [ ] Change *Unit Width* from 10 to 6: the plan has three units per row (`US1`–`US3`, `UN1`–`UN3`), eight zones per storey, and the building 24 zones.
- [ ] Place a *Program Preset* with a name, *Space Type* `Corridor`, *WWR* 0.2, *Conditioned* left at `true`, and no *Heating*/*Cooling* input: it turns red with `A conditioned space needs both Heating and Cooling setpoints.` Set *Conditioned* to `false`: the error disappears and it outputs an unconditioned preset.
- [ ] Set *Length* to 3: *Linear Plan Generator* turns red with `Error InvalidParameter: Length (3) must exceed StairLength (4).` and produces no plan; the downstream components produce no output. Set *Length* back to 24.
- [ ] Change the Rhino document units to millimetres (without scaling objects) and recompute the definition (*Solution → Recompute*): the *Convert2BEM* geometry, windows included, is 1000 times larger (bounding box 24 000 × 18 000 × 9 000 mm), while *Load Values*, setpoints, and *Internal Mass* are unchanged. Set the units back to metres.

#### Example definition

`examples/grasshopper/pipeline-skeleton.gh` holds steps 1–6 of the pipeline above with default inputs and *Multipliers* = 3: *Example Residential Presets* → *Linear Plan Generator* → *No Simplification* → *Stack Floors* → *Convert2BEM*, plus *Inspect* with panels on *Report* and *Provenance*. It is saved by a person in Rhino 8 (agents cannot create or check `.gh` files).

- [ ] Opened in Rhino 8 with the S2 plugin loaded, it solves without warnings or errors (the *Example Residential Presets* remark is expected) and every preview shows.
````

- [x] **Step 2: Run the S2 checklist in Rhino 8 (person)** — close Rhino, build the plugin from the current branch (`dotnet build src/Lod.Grasshopper -c Release`), start Rhino with the plugin loaded, and work through every item of the new section except the *Example definition* item, which Step 5 checks once the file exists. Every box must be ticked; any failure is fixed in code (with tests where the core is involved) before continuing. Following the document's "Recording the result" rule, write down the tester, the date, the Rhino version and runtime, the SHA that was built (`git rev-parse HEAD`), the version text shown by *BEMGen Info*, and pass or fail per item; these values go into the close-out commit (Task 11, Step 10).

- [x] **Step 3: Commit the checklist**

```bash
git add docs/development/grasshopper-smoke-test.md
git commit -m "docs(grasshopper): add s2 pipeline smoke-test checklist"
```

- [ ] **Step 4: Save the example definition (person, Rhino 8)** — in Grasshopper, build the definition described in the checklist's *Example definition* subsection (steps 1–6 of the pipeline with default inputs and *Multipliers* = 3, *Inspect* with panels on *Report* and *Provenance*, *Convert2BEM* with its outputs visible), check that no component shows a warning or error (the *Example Residential Presets* remark is expected), then *File → Save As* `examples/grasshopper/pipeline-skeleton.gh` in the repository. An agent cannot create or check this file.

- [ ] **Step 5: Re-open check (person)** — close Rhino, start it again, and open `examples/grasshopper/pipeline-skeleton.gh` with the S2 plugin loaded: it solves without warnings or errors (apart from the expected remark) and the previews show. This ticks the checklist's *Example definition* item.

- [ ] **Step 6: Commit the example definition** (binary file)

```bash
git add examples/grasshopper/pipeline-skeleton.gh
git commit -m "docs(examples): add pipeline skeleton example definition"
```

- [x] **Step 7: Rebase-merge the slice (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only feature/convert-bem-neutral
git push origin main
git branch -d feature/convert-bem-neutral
```

Expected from `verify.ps1`: three `Passed!` lines (94, 17, 9 on net8.0), then `VERIFY PASSED`.

---

## Stage close-out

### Task 11: Close stage S2 (version 0.2.0, tag `v0.2.0`)

**Files:**
- Modify: `Directory.Build.props`
- Modify: `AGENTS.md` ("Project state")
- Modify: `README.md` ("Status")
- Modify: `docs/plans/2026-09-30-implementation-roadmap.md` (S2 progress line)

The close-out runs on its own short branch, `chore/repo-s2-close-out` (not a roadmap slice), like the S1, S3, and S4 close-outs, with one `build` commit for the version and one `docs` commit for the status text.

S2 makes no new project decision: the *Convert2BEM* layout is the neutral form of the provisional D-023, and `Stack` expanding `FloorEntry.Multiplier` into explicit storeys implements the roadmap's `Stack` (all storeys explicit, D-018), as opposed to `FloorAreaMultiplier` (D-032). The decision log therefore gets no entry. The progress line below is dated 2026-10-01; if the close-out happens on a later day, use that day's date.

- [x] **Step 1: Create the branch**

```bash
git switch main
git pull --ff-only
git switch -c chore/repo-s2-close-out main
```

- [x] **Step 2: Run the verify gate**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected (line order may differ):

```text
Passed!  - Failed:     0, Passed:    94, Skipped:     0, Total:    94, Duration: … - Lod.Core.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:    17, Skipped:     0, Total:    17, Duration: … - Lod.Generators.Tests.dll (net8.0)
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: … - Lod.Integration.Tests.dll (net8.0)
VERIFY PASSED
```

- [x] **Step 3: Bump the version** — in `Directory.Build.props`, replace

```xml
    <Version>0.1.0</Version>
```

with

```xml
    <Version>0.2.0</Version>
```

`BuildInfoTests` compares the informational version with the assembly version, so it keeps passing.

- [x] **Step 4: Verify again**

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
```

Expected: the same three `Passed!` lines as Step 2, then `VERIFY PASSED`.

- [x] **Step 5: Commit the version**

```bash
git add Directory.Build.props
git commit -m "build(repo): set version 0.2.0"
```

- [x] **Step 6: Update AGENTS.md "Project state"** — replace everything between the heading `## Project state` and the heading `## Commands` with the following (keep one blank line after the heading and one before `## Commands`; the `## Commands` section does not change in S2):

```markdown
Stages S0–S2 of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md) are complete (tag `v0.2.0`). The pipeline runs end to end for the linear plan at Z0: program presets → `LinearPlanGenerator` → `NoSimplification` → `Stack` → *Convert2BEM*, previewed at every step in Grasshopper (example definition: `examples/grasshopper/pipeline-skeleton.gh`). *Convert2BEM* produces the provisional neutral output documented in [docs/architecture/convert2bem.md](docs/architecture/convert2bem.md) (D-023) and does not validate yet.

Projects: `Lod.Core`, `Lod.Generators`, `Lod.Grasshopper`. Tests: `Lod.Core.Tests`, `Lod.Generators.Tests`, `Lod.Integration.Tests` (all run without Rhino). Manual checks in Rhino follow [docs/development/grasshopper-smoke-test.md](docs/development/grasshopper-smoke-test.md). Next: S3, plan simplifiers and validation.

S0–S4 are executed as described in [docs/plans/2026-10-01-execution-handoff.md](docs/plans/2026-10-01-execution-handoff.md) (D-048, D-049). A verified reference implementation may be unpacked in `.handoff/` (git-ignored); use it only to check results, and never stage anything under it.
```

- [x] **Step 7: Update README "Status"** — replace everything between the heading `## Status` and the heading `## What it does` with the following (keep one blank line after the heading and one before `## What it does`):

```markdown
Stage S2 (end-to-end pipeline skeleton) is complete and tagged `v0.2.0`. In Rhino 8 the Grasshopper plugin runs the whole pipeline for the simplest case — example program presets → linear plan → no simplification → stacked floors → *Convert2BEM* — with a preview at every step; see `examples/grasshopper/pipeline-skeleton.gh`. The example presets hold illustrative round numbers for testing, not DOE prototype values. The *Convert2BEM* output is provisional until a ClimateStudio reference definition exists (D-023). Next is S3 (plan simplifiers and validation) of the [implementation roadmap](docs/plans/2026-09-30-implementation-roadmap.md).
```

- [x] **Step 8: Add the S2 progress line to the roadmap** — the roadmap's progress lines live in its header blockquote (convention set by the S0 close-out: `> **Progress:** <date> · <stage> complete (tag …); next: …`, one line per stage, each below the previous stage's). In `docs/plans/2026-09-30-implementation-roadmap.md`, find S1's progress line, the line that starts with

```text
> **Progress:** 2026-10-01 · S1 Program presets and equivalence engine complete (tag `v0.1.0`); next: S2.
```

Directly below it, insert the following two lines. The bare `>` line keeps each stage's entry on its own line; the blank blockquote line that already followed the S1 line then follows the S2 line. Use the date on which the stage is closed (this plan assumes 2026-10-01):

```text
>
> **Progress:** 2026-10-01 · S2 End-to-end pipeline skeleton complete (tag `v0.2.0`); next: S3. Presets → `LinearPlanGenerator` → `NoSimplification` → `Stack` → neutral *Convert2BEM* (D-023) runs in Grasshopper with previews; explicit windows (one centered window per outdoor wall from the generator, D-039, D-026) and preset conditioning (stair unconditioned, D-038) appear in every report and preview; 94 core, 17 generator, and 9 integration tests pass on net8.0. *Convert2BEM* has no validation gate until S3.
```

Do not change any other roadmap text.

- [x] **Step 9: Decision log** — no new entry (see above).

- [x] **Step 10: Commit the documentation with the smoke-test record** — `docs/development/grasshopper-smoke-test.md` ("Recording the result") requires the result of the manual check in the body of the stage close-out commit. Fill the angle-bracket fields with the values written down in Task 10, Step 2; they are records of the manual check, filled at execution time:

```bash
git add AGENTS.md README.md docs/plans/2026-09-30-implementation-roadmap.md
git commit -m "docs(repo): record s2 completion" -m "Smoke test (docs/development/grasshopper-smoke-test.md, S2 checklist) by <tester> on <date>: Rhino <version>, .NET Core runtime, build <sha>, BEMGen Info version '<version text>', all items passed; examples/grasshopper/pipeline-skeleton.gh opens and solves."
```

- [ ] **Step 11: Rebase-merge (D-004)**

```bash
git fetch origin
git rebase origin/main
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
git switch main
git pull --ff-only
git merge --ff-only chore/repo-s2-close-out
git push origin main
git branch -d chore/repo-s2-close-out
```

Expected: `VERIFY PASSED`, then `Fast-forward`.

- [ ] **Step 12: Tag the stage** (only after every exit criterion below is met, including the committed example definition)

```bash
git tag -a v0.2.0 -m "S2 End-to-end pipeline skeleton complete"
git push origin v0.2.0
```

## Exit criteria

From the roadmap (S2), refined:

1. `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1` prints `VERIFY PASSED` on `main` with 94 `Lod.Core.Tests`, 17 `Lod.Generators.Tests`, and 9 `Lod.Integration.Tests` passing on net8.0; the build has 0 warnings.
2. The S2 tests cover the roadmap's list: zones tile the plan (`ZonesTileTheFootprintWithoutOverlap`), one centered window per outdoor wall of the rectangular generator with area = WWR × wall area (`EveryOutdoorWallHasOneCenteredWindowSizedByItsPreset`; valid only for this generator, ADR-011 in S8), deterministic generation (`GenerationIsDeterministic`; S2 uses no randomness and has no seed), stacked boundary conditions (`StackPlacesStoreysAndResolvesFloorsAndCeilings`, `InterstoreySurfacesComeInMatchingPairs`), presets → generator → `NoSimplification` → `Stack` without Grasshopper (`SkeletonPipelineTests`), and canonical snapshots (`linear-plan-canonical.txt`, `stack-two-storeys.txt`).
3. The S2 checklist in `docs/development/grasshopper-smoke-test.md` passes in Rhino 8: components in panels *1 Program* to *6 Inspect*, previews coloured by space type with one blue window per outdoor wall, *Inspect* report with the stair `unconditioned`, *Convert2BEM* with 15 outputs, *Unit Width* 6 → three units per row, invalid *Length* → red error.
4. `examples/grasshopper/pipeline-skeleton.gh`, saved by a person in Rhino 8, runs from *Example Residential Presets* to the *Convert2BEM* outputs with all previews showing.
5. `docs/architecture/convert2bem.md` documents every *Convert2BEM* output.
6. Version 0.2.0, AGENTS.md, README, and roadmap updated; annotated tag `v0.2.0` pushed.

## Notes for the reviewer

1. **Every intermediate state was compiled and run.** The plan itself was executed mechanically (every file write, `dotnet` command, snapshot rename, and `verify.ps1` run, in order) on a scratch copy of the S1 state (then 63 core tests); the error lines and test counts above come from that run (SDK 10, Release), and both received snapshots were identical to the expected files. After D-047 (one load per type and basis), the S1 state has 65 core tests; the verified S2 state was rebuilt and its tests rerun (94 core, 17 generator, 9 integration tests on net8.0), and the intermediate core counts in this plan add the 2 S1 tests to the counts of that run. The final tree is identical to the verified S2 state apart from `BEMGen.sln` project GUIDs, which `dotnet sln add` generates. The only code not in the verified state is the one-test intermediate `SkeletonPipelineTests.cs` of Task 5, which Task 6 replaces with the verified file.
2. **Roadmap v3 alignment.** The slices, branch names, and component list follow roadmap v3 §4 S2. One point the roadmap leaves implicit: `FloorEntry.Multiplier` is shared by all floor aggregators; `Stack` reads it as "repeat this floor explicitly", `FloorAreaMultiplier` (S4) as a zone multiplier on a representative storey at its true elevation (D-045, D-046). Task 11 treats this as implementing D-018 and D-032, not as a new decision; add a decision-log entry if the owner sees it differently.
3. **AGENTS.md architecture table.** The row `BCL and Clipper2 (polygon clipping, from S2; ADR-001, ADR-002)` for `Lod.Core` is committed before S0 starts, so Task 1, Step 5 only confirms it; S2 does not edit `AGENTS.md` outside the close-out.
4. **Code exercised only in later stages** (no S2 test): `Window.At` and its argument checks, and `Window.MovedTo` (first used by S3's `WindowRehosting` and its tests); `LayoutMeasures.Of` and `ExteriorWallArea` (S3 `PlanSimplifier`, S4 `SingleZoneMerged`). Never tested in any stage: the `Surface` constructor's interzone/adjacent-zone guard and `Zone`'s "at least one part" and "multiplier ≥ 1" guards. The merge of collinear wall pieces is covered by `CollinearPiecesOfOneEdgeMergeIntoOneWall`.
5. **Convert2BEM ignores the orientation.** Geometry stays in the plan frame and `OrientationDegrees` is not output, so a building generated with a non-zero orientation reaches ClimateStudio unrotated. Recorded under *Not yet decided* in `docs/architecture/convert2bem.md`; it should be settled with the D-023 revisit.
6. **No validation before conversion in S2.** GLOBAL.md scientific rule 6 and the roadmap's global constraint require a validation gate; it does not exist until S3 (`Validators.cs`, override recorded in *Convert2BEM*'s provenance). Acceptable for the Z0 + Stack skeleton, but the S2 *Convert2BEM* is not research-grade output.
7. **Provenance gaps.** Presets are recorded by `SpaceType:Name` only, so two presets with the same name but different values or conditioning cannot be told apart from the provenance; tolerances are not recorded (components always use `ToleranceSettings.Default`).
8. **Minor code observations (kept verbatim):** `NoSimplification` writes `System.Collections.Generic.KeyValuePair` fully qualified instead of adding a `using`; zone display names are not storey-prefixed (`Unit S1` on every storey), and *Convert2BEM*'s *Names* output carries zone IDs, not display names; *Windows* is not index-aligned with *Surfaces*; *Program Preset* ignores connected setpoints when *Conditioned* is false, without a message.
9. **Grasshopper data persistence.** The Goo classes do not implement `CastFrom`/`CastTo` or custom serialization. Whether internalised BEMGen data survives saving a `.gh` file is untested; the example definition keeps every BEMGen object computed from *Example Residential Presets*, so it does not depend on it.
10. **Conventions shared with the other stage plans.** The close-out follows the S1/S3/S4 plans: branch `chore/repo-s2-close-out`, a `build` commit for the version and a `docs` commit for the status text, AGENTS.md "Project state" and README "Status" replaced between fixed headings, and the roadmap progress line in the convention set by S0 (`> **Progress:** <date> · …`, directly below the S1 line, separated by a bare `>` line). Like the S0 close-out and the S4 plan, the `docs` commit body records the smoke test, as the smoke-test guide's "Recording the result" rule requires. The S2 checklist is a level-3 section (`### S2 checklist …`, subsections at level 4) nested under the guide's `## Stage checklists`, as S0 set it up. The S3 plan quotes passages of `docs/architecture/convert2bem.md` as edit anchors; the *Building* input row and the paragraph below the input table are unchanged, but the outputs are now 15 (indices 0–14) with *Conditioned* at index 4, so *Internal Mass* is row 14 and S3's *Provenance* output becomes index 15.
11. **Commit scopes.** The core tasks use the scope `core` and the example definition `examples`; AGENTS.md lists scopes only as examples, so adjust if the maintainer prefers e.g. `geometry` or `rezoning`.
12. **`net48` dropped (D-053, ADR-001).** This plan was written with `net48` targets; D-053 dropped them after S0. Test counts are unchanged and now reported for net8.0 only; the code is unchanged; only the project target lines (`Lod.Grasshopper` `net7.0`, test projects `net8.0`) and the expected outputs changed.
13. **Null floors in the floor aggregator components (D-057, found by the Task 10 smoke test).** When the plan generator fails (for example *Length* 3), Grasshopper passes a null item down the chain, and `FloorAggregatorComponent.SolveInstance` dereferenced it, so *Stack Floors* showed a solution exception instead of producing nothing. The Task 8 block now returns when the floor list contains a null, like *No Simplification* does for a null plan. The reference archive (`reference/S2` to `reference/S4`) carries the same change.
14. **Rhino modelling tolerance from `ToleranceSettings` (D-059, found by the end-of-stage review).** `RhinoGeometry` had its own `private const double Tolerance = 1e-6`, against GLOBAL.md quality rule 4. The Task 7 block now reads `ToleranceSettings.Default.Distance` (the same 1e-6 m; geometry is built in metres and scaled afterwards). The reference archive (`reference/S2` to `reference/S4`) carries the same change.
