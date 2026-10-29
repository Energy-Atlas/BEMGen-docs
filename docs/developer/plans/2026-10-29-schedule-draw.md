# Schedule Draw: the atlas's stochastic schedules as an optional add-on

> **Status:** Done (stage B2, D-194 to D-196); released in `v1.6.0` with the released generator 3.0.0 (D-197, D-198) · **Date:** 2026-10-29 · **Decisions:** D-133, D-134 (the owner's requirement), D-172 (program JSON 5.4.0), [ADR-033](../decisions/ADR-033-schedule-draw-external-generator.md) · **Requirement:** [schedule-generator-requirement.md](../research/schedule-generator-requirement.md) · **Architecture:** [schedule-draw.md](../architecture/schedule-draw.md)

## Goal

BEMGen ships the atlas's stochastic schedules next to the deterministic ruleset schedules, by calling the atlas generator (`atlas_schedules`, generator 3.0.0, request and bundle schema 3.0.0) as an external command. Without a draw, nothing changes: every program keeps the schedules its program JSON defines.

## Inputs and output (the owner's requirement 1)

- **Program setting:** a program JSON 5.4.0 and the `generator.json` of its release folder (atlas release 2.0.0 ships one beside each prototype's programs, keyed by release program ID, with the `source` and, for 90.1, `reviewed` recipe).
- **Schedule-generator setting:** a small BEMGen JSON (`schedule_draw_setting` 1.0.0) naming the generator, its pinned version, the recipe view, the roles drawn, how operating hours are shared, and the generator's occupancy option.
- **Seed:** an unsigned 64-bit master seed.
- **Output:** one program JSON 5.4.0 per drawn instance, whose drawn schedules are `annual` 8,760-hour series with `metadata.schedule_draw` provenance.

## Parts

1. **Core** (`Lod.ProgramJson.ScheduleDraw`): `ScheduleDrawSetting`, `GeneratorRecipes`, `ScheduleDrawer` (request, run, bundle, drawn documents), `IScheduleGenerator` with `ProcessScheduleGenerator` (files in and out, timeout, captured standard error, no network on BEMGen's side). Test-first, with a recorded request and bundle.
2. **Grasshopper:** *Schedule Draw* (`SDraw`, panel *1 Program*), a thin adaptor with a *Run* toggle; its output goes into *Program JSON*.
3. **Test suites:** the optional spec section `schedules:`; each seed is a test case; one generator run per test case, on the zones of its generated plans; absent, nothing changes.
4. **Integration test** gated by `BEMGEN_ATLAS_GENERATOR` (an atlas checkout); software-only tests use the recorded fixture.

## Settled here (the requirement's "also to settle")

Recorded in ADR-033 and D-194: the roles drawn, the external command, the calendar, the seeds, where the draw happens in a suite, and the recipe kinds supported. Cross-checked against the requirement's invariants: loads and occupancy conserved between a test case's reference and its test sites (the existing aggregation of drawn zone schedules), geometry not confounded (the draw is fixed per test case), traceable (provenance per zone and per test case), deterministic (two runs give byte-identical documents).

## Not in this stage

Apartment units (ResStock end uses that program JSON does not hold), composition parents (another slot vocabulary), and a mixed slot under `schedules:` are refused with a diagnostic; see ADR-033 *Consequences*.
