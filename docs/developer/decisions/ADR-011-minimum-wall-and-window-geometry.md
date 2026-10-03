# ADR-011: Minimum wall and window geometry

Status: Accepted (by the controller under D-084; provisional pending the owner's reading)

Date: 2026-10-02

Decisions: D-026, D-039, D-041, D-079, D-084; refines [ADR-002](ADR-002-geometry.md) (placement rule of the plan generators); applies [ADR-004](ADR-004-tolerances.md) and [ADR-012](ADR-012-centred-windows.md)

## Context

Every plan generator places one window centred on each outdoor wall, the wall rectangle scaled by `√(WWR)` (D-026, ADR-002). The linear plan's walls are all metres long, so this never produced a degenerate window. The families of S8 ([ADR-006](ADR-006-plan-generation-mechanism.md)) can give a zone short wall fragments: where a wing meets a band, where a bay boundary meets a re-entrant corner, or simply when a user sets a small width. The D-026 rule would put a window of a few centimetres on such a fragment: valid geometry, but no window anyone would build, and a needless detail for every converter. ADR-002 and the roadmap left this to ADR-011, together with how simplifiers treat windows that would straddle target walls (`WindowNotHosted`, D-079).

## Options considered

1. **Keep the D-026 rule on every wall.** Simple and conserves WWR × wall area exactly, but gives arbitrarily small windows on fragments.
2. **Reject plans with short walls.** Forces users and layouts to avoid fragments that are legitimate geometry (a wall of 0.4 m between two re-entrant corners is a real wall).
3. **Merge short fragments into a neighbouring wall's window.** Moves glazing to another wall or orientation, which the D-041/D-079 rules would then have to undo; a silent repair (GLOBAL.md quality rule 6).
4. **No window on a wall or window below a minimum, with an info diagnostic (chosen).** The wall stays as it is; the generator's glazing on that wall is zero and says so. Every later step conserves whatever glazing the generator placed.

## Decision

**Limits.** `GeometryLimits` in `Lod.Core.Common`, next to `ToleranceSettings`, is the only place where these limits are defined (GLOBAL.md quality rule 4). It is immutable; every value must be positive and finite.

| Limit | Default | Reason |
| --- | --- | --- |
| `MinimumWindowWallLength` | 1.0 m | a wall shorter than a metre is a fragment between corners, not a façade bay that would hold a window |
| `MinimumWindowWidth` | 0.3 m | below a frame-and-sash width a window has no glazed area worth modelling |
| `MinimumWindowHeight` | 0.3 m | as the width |

- `GeometryLimits.Default` holds these values. A generator receives limits through the `PlanGenerator` constructor; the one-argument constructor uses `GeometryLimits.Default`, and Grasshopper components use the defaults and expose no input. Non-default limits are recorded in the plan's provenance (`MinimumWindowWallLength`, `MinimumWindowWidth`, `MinimumWindowHeight`); the defaults are not, so existing provenance is unchanged.
- A default changes only through an update of this ADR with a decision-log entry, never to make a test pass.

**Generator rule (all plan generators, in the base `PlanGenerator`).** For every outdoor wall of a generated plan, with glazed area `A_g = WWR × A_w` from its zone's preset (D-026):

1. `A_g = 0`: no window, no diagnostic (as before).
2. The wall is shorter than `MinimumWindowWallLength`: no window.
3. Otherwise the D-026 window is computed (`Window.Centered`); if its width is below `MinimumWindowWidth` or its height below `MinimumWindowHeight`: no window.
4. Otherwise the wall gets that window.

A comparison counts a value as below a limit only when it is smaller than the limit by more than the distance tolerance, so a wall or window exactly at a limit keeps its window despite grid rounding (ADR-004). Each omitted window is the info `WindowOmitted` (subject: the wall's surface ID; the message gives the wall length or the window size, the limit, and the glazed area not placed). The plan is produced; the wall, its zone, and every other surface are unchanged; geometry is never invalid and never repaired.

**Consequences for WWR.** A plan with omitted windows has less glazing than WWR × outdoor wall area. That is the detailed model's glazing; it is reported, not corrected. Validation compares every later model with the plan's actual glazing, so nothing downstream depends on the preset's WWR.

**Simplifiers and single-zone aggregators (D-079).** The limits apply only where a generator places windows. Wherever walls are rebuilt, each target outdoor wall gets one centred window with the glazed area of the source windows it covers (ADR-012), whatever its size, because glazed area is an invariant (GLOBAL.md scientific rule 1); a source wall without a window contributes nothing. With every current zoning strategy a target wall that carries glazing contains at least one whole source wall with a window (see below), so it is never shorter than `MinimumWindowWallLength`; its window may be smaller than the minimum size when a little glazing is spread over a long wall, which is accepted and not reported.

**Windows across target walls.** A window always lies within one source wall, and windows are never split, moved, or capped. Every current zoning strategy cuts the façade only at source wall ends (semantic merge unions source zones; perimeter/core and single-zone cut at footprint vertices), so every source window lies on exactly one target wall, as D-079 requires. A future strategy that cuts a source wall inside a window fails with the error `WindowNotHosted`; it must cut at source wall ends or come with its own ADR. `WindowNotHosted` and `GlazingExceedsWall` stay guards.

## Consequences

- No existing plan changes: every outdoor wall of the linear plan at its canonical and tested parameters exceeds the limits (its shortest outdoor wall is the 2 m corridor end with a 0.89 m × 1.34 m window), so every snapshot is byte-identical.
- One new info code, `WindowOmitted`, appended to `DiagnosticCodes`. Generator components show it as a remark.
- Window and wall limits are central and injectable, like tolerances; tests that probe them construct their own `GeometryLimits`.
- The research brief §10 states the exception to the generator rule.
- ADR-002's placement rule stands, with this exception; its consequence on short fragments is settled here.
