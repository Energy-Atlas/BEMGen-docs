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
