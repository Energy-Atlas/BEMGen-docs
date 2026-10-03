# Grasshopper Plugin Repository Specification
## Parametric Geometry, Rezoning, and Equivalent Load Transformation for Building Energy LoD Research

## 1. Repository Purpose

This repository will contain the Grasshopper/Rhino-side implementation required for the geometric Level of Detail and zoning-equivalence research project.

The repository is responsible for:

- parametric floor plan generation for residential and non-residential building typologies (D-094),
- semantic spatial zoning,
- explicit façade and window generation,
- source-to-target zone mapping,
- semantic zone merging,
- perimeter/core and other rezoning operations,
- equivalent scalar-load transformation,
- equivalent schedule transformation,
- window redistribution and equivalent WWR calculation,
- validation of transformation invariants,
- serialization into a common intermediate representation,
- interfaces to downstream EnergyPlus/IDF generation APIs.

The repository is **not** responsible for implementing a complete EnergyPlus model-generation stack unless specifically added later.

Existing EnergyPlus, IDF, simulation, or Building Energy Model APIs should be treated as downstream dependencies.

---

## 2. Primary Architectural Principle

The codebase must separate:

1. **geometry generation**,
2. **semantic assignment**,
3. **spatial transformation**,
4. **energy-property transformation**,
5. **validation**,
6. **serialization/export**.

No Grasshopper component should contain an entire research workflow internally.

Grasshopper components should be thin UI/adaptor layers over reusable C# domain and service classes.

The core transformation logic must be testable without launching Rhino or Grasshopper wherever possible.

---

## 3. Recommended Repository Structure

```text
/
├─ src/
│  ├─ Lod.Core/
│  │  ├─ Geometry/
│  │  ├─ Semantics/
│  │  ├─ Loads/
│  │  ├─ Schedules/
│  │  ├─ Mapping/
│  │  ├─ Rezoning/
│  │  ├─ Windows/
│  │  ├─ Validation/
│  │  ├─ Serialization/
│  │  └─ Common/
│  │
│  ├─ Lod.Generators/
│  │  ├─ LinearBlock/
│  │  ├─ PointBlock/
│  │  ├─ CourtyardBlock/
│  │  └─ Common/
│  │
│  ├─ Lod.Grasshopper/
│  │  ├─ Components/
│  │  ├─ Parameters/
│  │  ├─ Goo/
│  │  ├─ Preview/
│  │  ├─ Icons/
│  │  └─ Integration/
│  │
│  └─ Lod.Export/
│     ├─ IntermediateModel/
│     ├─ Json/
│     └─ EnergyModelApi/
│
├─ tests/
│  ├─ Lod.Core.Tests/
│  ├─ Lod.Generators.Tests/
│  ├─ Lod.Export.Tests/
│  └─ Lod.Integration.Tests/
│
├─ docs/
│  ├─ research/
│  ├─ architecture/
│  ├─ schemas/
│  ├─ examples/
│  ├─ decisions/
│  └─ development/
│
├─ examples/
│  ├─ grasshopper/
│  ├─ json/
│  └─ expected-output/
│
├─ scripts/
├─ temp/
├─ AGENTS.md
├─ GLOBAL.md
├─ README.md
├─ .gitignore
├─ .editorconfig
└─ <solution file>
```

Names may be adjusted to match the existing organization, but the separation of responsibilities should remain.

---

## 4. Core Domain Objects

The following concepts should be represented as explicit C# types.

### 4.1 BuildingDefinition

Suggested fields:

- `Id`
- `Typology`
- `Orientation`
- `FloorToFloorHeight`
- `Floors`
- `Metadata`

### 4.2 FloorDefinition

Suggested fields:

- `Id`
- `Index`
- `Elevation`
- `Boundary`
- `Zones`
- `Surfaces`
- `Windows`
- `Metadata`

### 4.3 ZoneDefinition

Suggested fields:

- `Id`
- `Geometry`
- `Area`
- `Volume`
- `SemanticType`
- `ProgramGroup`
- `SourceZoneIds`
- `Loads`
- `Schedules`
- `Metadata`

### 4.4 SurfaceDefinition

Suggested fields:

- `Id`
- `ZoneId`
- `Geometry`
- `SurfaceType`
- `Orientation`
- `Area`
- `BoundaryCondition`
- `SourceSurfaceIds`

### 4.5 WindowDefinition

Suggested fields:

- `Id`
- `HostSurfaceId`
- `Geometry`
- `Area`
- `SourceWindowIds`
- `RepresentationMethod`

### 4.6 LoadDefinition

Suggested fields:

- `LoadType`
- `Basis`
- `DesignValue`
- `ScheduleId`
- `Units`
- `SourceLoadIds`

Possible `Basis` values:

- area density,
- per-person,
- absolute,
- façade-area based,
- air-change based.

### 4.7 ScheduleDefinition

Suggested fields:

- `Id`
- `Timestep`
- `Values`
- `Units`
- `SourceScheduleIds`
- `AggregationMethod`
- `Weights`

Schedules should be represented in an immutable or effectively immutable form.

### 4.8 ZoneMapping

Represents source-to-target spatial correspondence.

Suggested fields:

- `SourceZoneId`
- `TargetZoneId`
- `OverlapArea`
- `SourceFraction`
- `TargetFraction`

A mapping collection should be able to form the transfer matrix required by the research methodology.

---

## 5. Floor Plan Generator Interface

All floor plan generators should implement a common interface.

Conceptually:

```csharp
public interface IFloorPlanGenerator
{
    FloorDefinition Generate(FloorPlanParameters parameters);
}
```

The exact API may differ, but all generators must return the common semantic representation.

Required initial generators:

- Linear Block
- Point Block / Tower
- Courtyard Block

Each generator should:

- generate valid planar geometry,
- create semantic spaces,
- identify exterior surfaces,
- assign orientation,
- create circulation and service areas,
- attach source identifiers,
- optionally generate explicit windows.

Generation must be deterministic from input parameters and random seed.

---

## 6. Floor Plan Parameter Model

Use typed parameter records/classes rather than generic dictionaries.

Common parameters may include:

- footprint dimensions,
- gross floor area target,
- floor height,
- unit depth,
- unit width,
- corridor width,
- core dimensions,
- orientation,
- number of units,
- window dimensions,
- WWR,
- plan variation seed.

Typology-specific parameters should extend or compose the common parameter model.

Do not build a single unbounded parameter class containing every parameter for every typology.

---

## 7. Semantic Assignment

Space semantics must be explicit and machine-readable.

Initial categories may include:

- DwellingUnit
- Corridor
- Stair
- Core
- Lobby
- Service
- Mechanical
- Other

Since D-094 the categories also cover non-residential programs: `Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, and `ActivityHall`, with `Core`, `Lobby`, and `Service` reused for office cores, public foyers, and support rooms ([ADR-014](decisions/ADR-014-program-types-and-department-zoning.md)). A non-residential floor is zoned per department, a dwelling per storey (D-097, D-085).

Avoid encoding semantic meaning only through layer names, object names, colors, or Grasshopper wire structure.

Semantic data must survive:

- serialization,
- zone merging,
- rezoning,
- export.

---

## 8. Load and Schedule Assignment

The repository should support assigning abstract energy properties to semantic zones without constructing complete EnergyPlus objects.

Initial load types:

- Occupancy
- Lighting
- ElectricEquipment
- GasEquipment
- DHW
- Ventilation
- Infiltration

Initial control schedules:

- Occupancy
- Lighting
- Equipment
- HeatingSetpoint
- CoolingSetpoint
- DHW

The values may be defined through:

- program templates,
- direct component inputs,
- JSON configuration,
- test fixtures.

---

## 9. Equivalent Aggregation Engine

Implement a reusable aggregation service.

Conceptually:

```csharp
public interface IEquivalentPropertyAggregator
{
    AggregatedZoneProperties Aggregate(
        IReadOnlyList<SourceZoneContribution> sources,
        AggregationContext context);
}
```

The aggregation engine should not depend on a specific rezoning method.

It should support:

- area-weighted intensive values,
- summation of extensive values,
- load-weighted schedules,
- occupancy-weighted schedules,
- façade-weighted values,
- configurable setpoint aggregation rules.

For installed load:

\[
P_{\mathrm{design}} = \sum_i A_i p_i
\]

Equivalent density:

\[
p^\* =
\frac{\sum_i A_i p_i}
{\sum_i A_i}
\]

Equivalent schedule:

\[
s^\*(t)=
\frac{\sum_i A_i p_i s_i(t)}
{\sum_i A_i p_i}
\]

The implementation must guard against zero denominators.

---

## 10. Rezoning Engine

Rezoning should be implemented independently from load aggregation.

Conceptually:

```csharp
public interface IRezoningStrategy
{
    RezoningResult Rezone(
        FloorDefinition source,
        RezoningParameters parameters);
}
```

`RezoningResult` should include:

- target-zone geometry,
- source-to-target mapping,
- warnings,
- transformation metadata.

Initial strategies:

### 10.1 Identity

No transformation.

Used for testing and reference export.

### 10.2 Semantic Merge

Merge based on source semantic groups or explicit grouping rules.

### 10.3 Perimeter/Core

Generate thermal zones from floor-plate geometry using configurable perimeter depth.

### 10.4 Single Zone per Floor

Collapse the floor into one target thermal zone.

### 10.5 Future Strategies

Possible later additions:

- orientation-only perimeter zones,
- strip zoning,
- adjacency clustering,
- graph-based merging,
- user-defined target polygons.

---

## 11. Spatial Transfer Mapping

The mapping engine must calculate geometric overlap between source zones and target zones.

For each overlap:

- source zone ID,
- target zone ID,
- intersection area,
- fraction of source area,
- fraction of target area.

Mapping must be independent of semantic aggregation.

This mapping should be reusable for:

- occupancy,
- loads,
- schedules,
- façade ownership,
- source traceability.

The implementation should define numerical tolerances centrally.

---

## 12. Window Transformation Module

Window logic should be independent from zone geometry generation.

Required initial transformations:

- preserve explicit windows,
- preserve total window area per source zone,
- generate target-zone WWR,
- redistribute windows over target façades,
- preserve orientation-level glazed area,
- preserve building-level glazed area.

The window module should retain traceability to source windows whenever practical.

Required invariants should be configurable by transformation method.

Examples:

- total glazed area,
- glazed area by orientation,
- glazed area by target zone,
- host surface validity.

---

## 13. Vertical Representation Module

The repository should define the information required to describe vertical simplification even if EnergyPlus export is delegated downstream.

Potential modes:

- all floors explicit,
- repeated typical floors,
- bottom/middle/top representative floors,
- one typical floor,
- floor multiplier.

The common intermediate representation must carry:

- source floor ID,
- representative floor ID,
- multiplier if present,
- transformation mode.

---

## 14. Intermediate Export Schema

The repository should export a common model representation, preferably JSON.

The export should contain:

- building,
- floors,
- zones,
- surfaces,
- windows,
- loads,
- schedules,
- source-target mappings,
- transformation metadata,
- validation results.

The export schema must be versioned.

Example:

```json
{
  "schemaVersion": "0.1",
  "building": {},
  "transform": {
    "zoningLevel": "Z2",
    "windowLevel": "W2",
    "verticalLevel": "V0"
  }
}
```

Do not expose RhinoCommon or Grasshopper-specific object serialization as the external schema.

Geometry should be converted to a portable representation.

---

## 15. Energy Model API Boundary

Downstream IDF/EnergyPlus generation is outside the primary responsibility of this repository.

Create an explicit interface boundary.

Conceptually:

```csharp
public interface IEnergyModelExporter
{
    ExportResult Export(IntermediateBuildingModel model);
}
```

An implementation may:

- call an existing REST API,
- call an existing .NET library,
- write an intermediate JSON file,
- invoke an existing EnergyPlus model-generation service.

Grasshopper components should depend on this interface rather than on one fixed exporter.

---

## 16. Grasshopper Components

Grasshopper components should be grouped by function.

### 16.1 Generate

- Generate Linear Block
- Generate Point Block
- Generate Courtyard Block

### 16.2 Semantics

- Assign Program
- Assign Loads
- Assign Schedules
- Inspect Zone Metadata

### 16.3 Transform

- Merge Zones
- Generate Perimeter/Core Zones
- One Zone per Floor
- Map Source to Target
- Aggregate Equivalent Properties

### 16.4 Windows

- Generate Explicit Windows
- Calculate Equivalent WWR
- Redistribute Windows
- Inspect Window Conservation

### 16.5 Validate

- Validate Geometry
- Validate Load Conservation
- Validate Schedule Equivalence
- Validate Windows
- Validate Full Model

### 16.6 Export

- Build Intermediate Model
- Serialize JSON
- Send to Energy Model API
- Batch Configuration Export

Each component should expose warnings and errors clearly.

---

## 17. Grasshopper UX Rules

Components should:

- use consistent naming,
- use consistent parameter ordering,
- distinguish required and optional inputs,
- provide useful tooltips,
- avoid hidden state,
- avoid modifying input objects,
- expose deterministic outputs,
- expose validation messages.

Components must not rely on canvas execution order beyond normal Grasshopper dependency resolution.

Avoid components that perform unrelated tasks such as:

`Generate + Rezone + Aggregate + Export + Simulate`

These should remain separate composable operations.

---

## 18. Testing Strategy

Development should follow test-driven or test-first principles for core logic.

Every major transformation should have tests written before or alongside implementation.

### 18.1 Unit Tests

Required for:

- schedule aggregation,
- load conservation,
- area weighting,
- transfer matrices,
- geometry tolerances,
- semantic grouping,
- WWR calculation,
- parameter validation.

### 18.2 Property / Invariant Tests

Examples:

- sum of target area ≈ source area,
- sum of installed load is conserved,
- equivalent scheduled load matches source scheduled load,
- total window area is conserved,
- mapping fractions sum to one,
- no target zone has negative area.

### 18.3 Golden Tests

Store representative expected outputs for:

- linear block,
- point block,
- courtyard block,
- merged zoning,
- perimeter/core zoning,
- single-zone floor.

Golden outputs should be small and human-inspectable.

### 18.4 Integration Tests

Integration tests should cover:

- generator → semantics → rezoning → aggregation → validation → serialization.

Where possible, integration tests must run without Grasshopper.

---

## 19. Numerical Tolerances

Numerical tolerances should be defined centrally.

Example categories:

- geometry distance tolerance,
- area conservation tolerance,
- load conservation tolerance,
- schedule equivalence tolerance,
- angular/orientation tolerance.

Do not scatter arbitrary constants through the codebase.

A tolerance configuration object is preferred.

---

## 20. C# Coding Conventions

Use modern, readable C#.

Required conventions:

- nullable reference types enabled,
- file-scoped namespaces where appropriate,
- explicit access modifiers,
- `PascalCase` for public types and members,
- `camelCase` for locals and parameters,
- interfaces prefixed with `I`,
- async methods suffixed with `Async`,
- immutable records/value objects where practical,
- dependency injection for external services,
- no global mutable state,
- no static service locators,
- avoid magic strings,
- avoid reflection unless strongly justified.

Prefer composition over deep inheritance.

Avoid creating large multipurpose manager classes.

Domain logic should not live inside Grasshopper component classes.

---

## 21. Documentation Requirements

All major architecture decisions should be documented.

Recommended structure:

```text
docs/
├─ research/
│  └─ experimental-method.md
├─ architecture/
│  ├─ overview.md
│  ├─ domain-model.md
│  ├─ rezoning-pipeline.md
│  └─ grasshopper-boundary.md
├─ schemas/
│  └─ intermediate-model.md
├─ decisions/
│  ├─ ADR-001-geometry-representation.md
│  ├─ ADR-002-schedule-aggregation.md
│  └─ ...
├─ examples/
└─ development/
   ├─ testing.md
   └─ contributing.md
```

Public APIs and non-obvious algorithms should have XML documentation comments.

Do not add comments that merely restate the code.

---

## 22. `AGENTS.md`

The repository must contain an `AGENTS.md` file at the root.

It should instruct coding agents to:

1. read `GLOBAL.md`, `README.md`, and relevant `docs/` before modifying architecture;
2. inspect existing patterns before introducing new abstractions;
3. prefer extension of existing patterns over duplicate implementations;
4. preserve separation between domain logic and Grasshopper UI;
5. add or update tests for behavioral changes;
6. run the relevant test suite before completion;
7. update documentation when changing schemas or public APIs;
8. avoid modifying unrelated files;
9. never commit generated binaries, caches, or user-specific IDE state;
10. preserve deterministic behavior;
11. surface assumptions explicitly;
12. never fabricate test results;
13. never silently relax validation invariants;
14. never alter research equivalence rules without updating the research documentation;
15. never include the agent name, model name, provider name, model version, or similar AI-identifying text in commit messages.

The last rule applies to all commits made or proposed by agents.

Disallowed commit-message examples include references such as:

- generated by `<agent name>`,
- implemented with `<model name>`,
- assisted by `<provider>`,
- model/version identifiers.

Commit messages should describe only the code or documentation change.

---

## 23. `GLOBAL.md`

The repository must contain a `GLOBAL.md` defining non-negotiable project rules.

Suggested contents:

### Scientific Rules

- simplified models must preserve explicitly defined invariants;
- transformations must be traceable to source zones;
- source and target representations must not silently change program assumptions;
- geometry effects must not be confounded with changes to internal loads or schedules;
- validation failures block export unless explicitly overridden in a research test.

### Architecture Rules

- core logic is independent of Grasshopper wherever possible;
- external simulation APIs are behind interfaces;
- domain objects are serializable;
- no dependency from `Lod.Core` to Grasshopper;
- no dependency from `Lod.Core` to UI code.

### Quality Rules

- behavioral changes require tests;
- public schemas are versioned;
- deterministic generation is required;
- numerical tolerances are centralized;
- exceptions must contain actionable context.

### Git Rules

- focused commits,
- no secrets,
- no generated build artifacts,
- no agent/model/provider identification in commit messages,
- no force pushes to shared branches unless explicitly authorized.

---

## 24. `.gitignore`

The repository should ignore at least:

```gitignore
# .NET
bin/
obj/
*.user
*.suo
*.userosscache
*.sln.docstates

# Visual Studio / Rider
.vs/
.idea/
_ReSharper*/
*.DotSettings.user

# NuGet
packages/
*.nupkg

# Grasshopper / Rhino local artifacts
*.ghuser
*.gha.bak
*.rui
*.autosave*

# Test results
TestResults/
coverage/
coverage.*
*.trx

# Build / packaging
dist/
artifacts/
out/

# Temporary
temp/*
tmp/
*.tmp
*.log

# OS
.DS_Store
Thumbs.db

# Environment / secrets
.env
.env.*
secrets.*
*.secret.json
```

Do not ignore intentionally versioned example `.gh` files if the repository uses them as reproducible examples.

---

## 25. Git and Commit Rules

Commit messages should be short, descriptive, and implementation-focused.

Examples:

- `Add perimeter-core rezoning strategy`
- `Preserve equipment schedules during zone aggregation`
- `Add courtyard block generator tests`
- `Version intermediate model schema`
- `Validate orientation-level window area`

Do not include:

- personal signatures,
- agent names,
- model names,
- AI providers,
- model versions,
- tool branding,
- automated attribution.

No generated attribution footer should be appended to commits.

---

## 26. Pull Request / Change Requirements

A change affecting transformation logic should include:

- summary of behavior changed,
- tests added or updated,
- invariant impact,
- schema impact if any,
- documentation impact,
- example before/after when useful.

A change should not be considered complete if it changes scientific behavior without documenting the behavior.

---

## 27. Error Handling

Use structured result types where failures are expected.

Examples:

- invalid generator parameters,
- zone overlap,
- incomplete source-target coverage,
- incompatible setpoint schedules,
- invalid host surface for windows,
- failed conservation checks.

Do not silently repair geometry unless the repair is deterministic, documented, and returned as a warning.

---

## 28. Logging

Logging should distinguish:

- diagnostic information,
- warnings,
- validation failures,
- export failures.

Core libraries should not write directly to the console.

Grasshopper components may adapt structured diagnostics into runtime messages.

---

## 29. Determinism

All generators must be reproducible.

If randomness is used:

- require an explicit seed,
- store the seed in metadata,
- avoid process-global random state,
- test deterministic regeneration.

The same configuration and code revision should produce the same model representation within numerical tolerance.

---

## 30. Performance

Performance is secondary to correctness during the initial implementation, but the architecture should support batch studies.

Avoid:

- repeated expensive geometric intersections,
- unnecessary deep copies,
- recomputing mappings when geometry has not changed.

Potential later optimizations:

- cached zone intersections,
- parallel generation,
- parallel serialization,
- batching API requests.

Correctness and traceability take priority over premature optimization.

---

## 31. Initial Development Milestones

### Milestone 1 — Domain Model and Tests

Deliver:

- domain types,
- schedules,
- loads,
- semantic zones,
- serialization skeleton,
- test projects,
- repository rules.

### Milestone 2 — First Parametric Generator

Deliver:

- Linear Block generator,
- semantic spaces,
- exterior surfaces,
- explicit windows,
- deterministic tests.

### Milestone 3 — Zone Mapping and Merge

Deliver:

- source-target intersection mapping,
- semantic merge strategy,
- equivalent loads,
- equivalent schedules,
- conservation validation.

### Milestone 4 — Perimeter/Core Rezoning

Deliver:

- configurable perimeter depth,
- core generation,
- transfer mapping,
- equivalent properties.

### Milestone 5 — Window Transformations

Deliver:

- explicit windows,
- equivalent target-zone WWR,
- redistributed windows,
- conservation tests.

### Milestone 6 — Additional Typologies

Deliver:

- Point Block generator,
- Courtyard Block generator,
- common generator abstractions,
- generators for the non-residential typologies of the precedent set (D-094).

### Milestone 7 — Export Boundary

Deliver:

- versioned intermediate schema,
- JSON serializer,
- interface/adaptor to existing EnergyPlus generation APIs.

### Milestone 8 — Grasshopper UX

Deliver:

- stable components,
- previews,
- validation messages,
- example `.gh` files,
- user documentation.

---

## 32. Definition of Done

A feature is complete only when:

- implementation is present,
- tests cover expected behavior,
- relevant invariants pass,
- public API changes are documented,
- schema changes are versioned,
- Grasshopper behavior is deterministic,
- no unrelated code is modified,
- repository rules are respected.

For transformation features, the feature is not complete until equivalence can be demonstrated numerically.

---

## 33. Core Research Invariants

The implementation should treat the following as first-class validation targets.

### Area

\[
\sum A_{\mathrm{target}}
\approx
\sum A_{\mathrm{source}}
\]

### Installed Power

\[
\sum P_{\mathrm{target,design}}
\approx
\sum P_{\mathrm{source,design}}
\]

### Scheduled Power

For every simulation timestep \(t\):

\[
\sum P_{\mathrm{target}}(t)
\approx
\sum P_{\mathrm{source}}(t)
\]

### Occupancy

\[
N_{\mathrm{target}}(t)
\approx
N_{\mathrm{source}}(t)
\]

### Window Area

Depending on the experiment:

\[
A_{\mathrm{window,target}}
\approx
A_{\mathrm{window,source}}
\]

possibly constrained additionally by orientation or zone.

All tolerances must be explicit.

---

## 34. Final Architectural Goal

The final system should allow a researcher to construct a workflow equivalent to:

```text
Parametric Plan Generator
        ↓
Detailed Semantic Floor Plan
        ↓
Semantic Loads + Schedules + Windows
        ↓
Choose Zoning Transformation
        ↓
Source → Target Spatial Mapping
        ↓
Equivalent Property Aggregation
        ↓
Choose Window Transformation
        ↓
Validation
        ↓
Common Intermediate Model
        ↓
Existing Energy Model / IDF API
        ↓
EnergyPlus Batch Simulation
```

The repository should make each transformation explicit, testable, traceable, and independently replaceable.

The research value of the tool depends on ensuring that different Levels of Detail represent the same underlying building assumptions before they are compared.
