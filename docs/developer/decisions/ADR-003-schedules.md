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
