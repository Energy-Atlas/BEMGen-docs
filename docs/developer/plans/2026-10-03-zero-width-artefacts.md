# Zero-width artefacts in rotated plans (design note)

> **Status:** Done (D-114) · **Date:** 2026-10-03 · **Decisions:** D-088, D-090, D-111, D-113, D-114; [ADR-002](../decisions/ADR-002-geometry.md), [ADR-004](../decisions/ADR-004-tolerances.md), [ADR-010](../decisions/ADR-010-convert2idf.md)

A revision after S6, run as D-111 sets out: built once, test-first, on a feature branch in a worktree; reviewed by a second agent; `scripts/verify.ps1` before the merge; the headless Rhino check once; recorded in one decision-log entry. No version change or tag unless the fix changes output; pushing waits for the owner.

## Problem

Rotated and moved plans can carry zero-width artefacts in zone parts and surfaces: spikes (a vertex going out and straight back), excursions through a repeated vertex, and slivers about 1e-6 m wide that have no partner on the adjacent side. S6 found them when the stepped band (`SYN-TYP-012`) was rotated and moved by *Transform Plan* (131.4° + (15.08, −153.9), 30° + (5.3, −2.1)) and passed through every simplifier and aggregator. Validation accepts them; *Convert2IDF* drops them with `SliverOmitted` before pairing surfaces (ADR-010). They come from clipping on the integer grid (the D-090 limit) somewhere in `Lod.Core`.

## Tasks

1. **Reproduce.** Failing tests in `tests/Lod.Integration.Tests` that detect the artefacts directly on zone parts and surfaces (a spike, a repeated vertex, a ring or piece narrower than `ToleranceSettings.Distance` relative to its perimeter), for the rotated stepped band and at least one other family, with every simplifier × aggregator at the two placements.
2. **Locate.** For each artefact, the step that creates it (`PolygonOps`, `VertexGrid`/`UnionTiles`, `LayoutSurfaceBuilder`, `Storeys`, `SingleZoneMerge`, `PerimeterCore`, or the transform).
3. **Fix at the source,** test-first: remove spikes and zero-area excursions where they arise, identically on both sides of a shared edge, without moving any real vertex; documented in ADR-002 (and ADR-004 if a rule about the grid changes).
4. **Downstream.** If the pipeline no longer produces them, *Convert2IDF*'s sliver handling stays as a guard; its warning should then not fire on any generated plan (assert it in the export tests).

## Acceptance criteria

- The reproduction tests pass; no generated, rotated plan carries a spike, repeated vertex, or sliver in any zone part or surface.
- No tolerance is widened and no validation check relaxed (AGENTS.md rules 12 and 14); existing snapshots stay byte-identical unless a documented change forces it.
- `scripts/verify.ps1` passes; the rhino-smoke specs and the IDD check of the export tests still report no problems.
