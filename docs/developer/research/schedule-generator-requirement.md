# Schedule generator: requirement

> **Status:** Designed and implemented (stage B2, D-194 to D-196, [ADR-033](../decisions/ADR-033-schedule-draw-external-generator.md)); the requirement below is the owner's of 2026-10-12 · **Decisions:** D-133, D-134 · **Applies to:** test suites ([design note](../plans/2026-10-12-test-suite-generator.md)), *Schedule Draw* ([architecture](../architecture/schedule-draw.md)) · **Related:** [experiment outputs](experiment-outputs.md), [program presets](program-presets.md)

This page records what the owner asked of a schedule generator. The design is [ADR-033](../decisions/ADR-033-schedule-draw-external-generator.md): the atlas generator `atlas_schedules` 3.0.0 called as an external command, *Schedule Draw* in Grasshopper, and the test-suite spec's optional `schedules:` section. Without a draw, every program is used with the schedules its program JSON defines.

## What the owner asked (2026-10-12)

1. **Inputs and output.** Three inputs give one output:
   - a **program setting**: a program JSON whose schedules carry generation parameters;
   - a **schedule-generator setting**: a JSON naming the generator and its settings, ResStock/ComStock-like;
   - a **seed**.

   The output is one program JSON with generated schedules.
2. **The spec names** the program setting, the schedule generator, its parameters, and the seed.
3. **A draw is part of a test case.** A program setting drawn several times makes several test cases. Each draw is like another version of the program's settings. Seeded sampling happens only here; the suite's other axes are full factorial.
4. **All sites of a test case share the same schedule sources.** A simplified site's actual schedules may still differ from the reference's, because its merges aggregate the drawn zone schedules.
5. **Schedules are generated per zone.** Zones take shifted seeds, so that dwellings or other units of the same type do not all get the same schedule.
6. **The generator runs once per test case.**

## What BEMGen must keep

- **Loads and occupancy conserved** (GLOBAL scientific rule 1). Installed loads, scheduled loads hour by hour, and occupancy must be equal between a test case's reference site and each test site.
- **Geometry not confounded with schedules** (scientific rule 4). Within a test case, sites differ only in zoning (D-133).
- **Traceable** (scientific rule 2). Each target zone's schedules record their sources, method, and weights. The generator, its setting, and each zone's seed are recorded in provenance and in the test case's row.
- **Deterministic** (quality rule 3). The same inputs and seed always give the same schedules, with no process-global random state.

## How the requirements fit together

The generator runs once per test case, on the zones of the generated plan: the reference site's zones, each with its own shifted seed (requirements 5 and 6). Every test site then derives its zones from those same zones through its simplifier and stacker.

- A merged zone's schedules are the aggregate of its source zones' drawn schedules, made by the existing aggregation, as differing programs are aggregated today. A merged zone never gets a draw of its own.
- Installed loads, hourly scheduled loads, and occupancy are therefore conserved between a test case's reference and each test site (requirement 4; scientific rules 1 and 4).
- Each zone's provenance records its seed, and each merged zone's records the sources it aggregates (rule 2).

## Also to settle at the design (settled by ADR-033)

- **Which schedules are drawn:** occupancy, lighting, equipment, hot water, setpoints, ventilation. *Settled:* occupancy, lighting, electric and gas equipment, hot water (flow and target temperature), activity, and the heating and cooling setpoints, all by default, narrowed by the setting's `draw`; ventilation is not a schedule the generator draws (ADR-033 decision 3).
- **Where the generator runs:** in C#, or as an external command (Python, for ResStock/ComStock tooling) with files in and out. *Settled:* an external command, `python -m atlas_schedules` by default, files in and out, a timeout, captured standard error, pinned versions (decisions 1, 2).
- **The calendar.** Draws use the suite's calendar (D-133), year 2007 by default. *Settled:* the generator's 2007; a suite with schedules must use 2007, and its holidays apply to the schedules not drawn (decision 5).
- **Seeds.** How zones' seeds are derived from the test case's seed: from the zone ID, the suite seed, and the sample index. *Settled:* the test case's seed is the master seed; each zone is its own operating group keyed `<plan index>.<zone ID>`, whose seed the generator derives from the master seed and the key (`atlas_conditional_seeded_v1`), recorded per zone; the sample index is the seed's place in the spec's list (decision 6).
