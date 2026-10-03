# GLOBAL.md — Non-Negotiable Project Rules

These rules apply to every change, by any contributor or agent. If a task seems to require breaking one, stop and raise it instead of working around it.

## Scientific rules

1. Simplified models must preserve their explicitly defined invariants (area, installed power, scheduled power per timestep, occupancy, and the glazing quantities required by the chosen window level).
2. Every transformation is traceable: each target zone references its source zones, and each transformed schedule records its source schedules, aggregation method, and weights.
3. Source and target representations must not silently change program assumptions.
4. Geometry effects must not be confounded with changes to internal loads or schedules.
5. Setpoints are controls, not additive loads. Their aggregation rule is explicit and recorded in experiment metadata.
6. Validation failures block conversion (`Convert2BEM`, `Convert2IDF`) unless explicitly overridden, and the override is recorded.
7. Research equivalence rules change only together with the research documentation in `docs/`.

## Architecture rules

1. Core logic is independent of Rhino and Grasshopper wherever possible.
2. `Lod.Core` has no dependency on Grasshopper or on any UI code.
3. Grasshopper components are thin adaptors over domain and service classes; they contain no research workflow.
4. Pipeline objects (`IGeneratedPlan`, `IFloor`, `IGeneratedBuilding`, program presets) are plain C# types. RhinoCommon/Grasshopper types appear only in `Lod.Grasshopper`: Goo wrappers, previews, and `Convert2BEM`.
5. Tool-specific formats (ClimateStudio inputs, IDF) appear only in the converters, which consume `IGeneratedBuilding`.
6. Plan generation, plan simplification, floor aggregation, equivalent-property aggregation, validation, and conversion are separate, independently replaceable services.

## Quality rules

1. Behavioral changes require tests; core transformations are developed test-first.
2. Public pipeline types and Grasshopper component inputs/outputs are documented in `docs/`; breaking changes get a decision-log entry. Component GUIDs never change once merged.
3. Generation is deterministic: randomness requires an explicit seed that is stored in metadata; no process-global random state.
4. Numerical tolerances are defined centrally in a tolerance configuration, never as scattered constants.
5. Expected failures use structured result types; exceptions carry actionable context.
6. Geometry is never repaired silently. Any repair is deterministic, documented, and returned as a warning.
7. Core libraries do not write to the console.

## Git rules

1. Focused commits: one logical change per commit.
2. Commit messages use `type(scope): summary` (see [AGENTS.md](AGENTS.md#commits)).
3. No secrets, credentials, or `.env` files.
4. No generated build artifacts, caches, simulation outputs, or user-specific IDE state.
5. No agent, model, provider, or tool identification in commit messages, and no attribution footers or co-author trailers for tools.
6. No force pushes to shared branches unless explicitly authorized.
