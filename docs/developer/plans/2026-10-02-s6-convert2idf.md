# S6 — Convert2IDF (design note)

> **Status:** Done (D-113; tagged `v0.9.0`) · **Date:** 2026-10-02 · **Roadmap:** [S6](2026-09-30-implementation-roadmap.md#s6--convert2idf) · **Decisions:** D-069, D-077, D-111, D-112; [ADR-010](../decisions/ADR-010-convert2idf.md)

Run as D-111 sets out: built once, test-first, on feature branches in worktrees; parts B and C in parallel after A; each part's diff reviewed by a second agent before it is merged; `scripts/verify.ps1` before each merge; the headless Rhino check once on the merge candidate; one decision-log entry at the end. Version 0.9.0, tag `v0.9.0`. Pushing waits for the owner.

## Scope

An EnergyPlus 25.2 IDF from any `IGeneratedBuilding`, as ADR-010 specifies: an envelope preset shared with *Convert2BEM*, ideal-loads HVAC for conditioned zones, exact schedules, loads, internal mass, zone multipliers, the two heat-transfer options (default off), surfaces without holes, and the minimum simulation objects. No EnergyPlus run, no weather, outputs, or climates (D-112).

## Parts and tasks

**A. Rhino check in the repository** (`chore/scripts-rhino-smoke`, first, D-111)
1. Move the controller's headless harness into `scripts/rhino-smoke/`: the harness, a run script that builds the plugin and starts Rhino 8 headless against a chosen checkout, and the S8 specs, with results written outside the repository; a short README.
2. Run every spec once on `main` and confirm the S8 results.

**B. Envelope preset** (`feature/programs-envelope-preset`, parallel with C)
1. `EnvelopePreset`, `Construction`, `Layer`, `GlazingSpec` in `Lod.Core` with validation (positive thicknesses and properties, U-value, SHGC and VT in range) — test-first.
2. `ExampleEnvelopePresets`: one illustrative set, values and reasons in `docs/research/program-presets.md` (or a new `envelope-presets.md`).
3. *Envelope Preset* default component (panel *1 Program Presets*) with an icon; *Convert2BEM* gains an *Envelope* input (default the example preset) and a *Constructions* output parallel to its surfaces and windows.

**C. IDF writer** (`feature/convert-idf`, in `Lod.Export`, parallel with B; it uses B's types once merged)
1. Object model and text writer (invariant culture, stable order, unique names ≤ 100 characters, provenance header) — test-first with a minimal building.
2. Geometry: zones, surfaces with boundary conditions from `HeatTransferOptions`, partners for interzone surfaces, windows, collinear-vertex removal, hole-free splitting of horizontal polygons (area-conserving, partners split identically), the multiplier rule for partners.
3. Programs: loads per ADR-010, thermostats and ideal loads, unconditioned zones, exact schedules (year/week/day), ground temperatures, internal mass.
4. Simulation objects (version, control, timestep, run period, geometry rules, meters).
5. Tests: snapshots of the minimal linear plan and of four combinations of the canonical linear plan that cover each simplifier, each aggregator, and both heat-transfer settings (ADR-010; one file per combination would be tens of thousands of lines); all 32 combinations parsed back with the checks of ADR-010 (counts, references, partners, geometry, invariants); the enclosed court, the court cluster, the office plate, and the stepped band the same way, also rotated and moved; the IDD check of every converted file (`scripts/idd-check`).

**D. Grasshopper and close-out** (`feature/grasshopper-convert-idf`, after B and C)
1. *Convert2IDF* component in *5 Convert*: Building, Envelope, EnableInternalWallHeatTransfer, EnableFloorHeatTransfer (both default `False`), Override, Path, Write (default `False`), Overwrite (default `False`); outputs: IDF text, Provenance, Written. Thin: it calls the writer and reports diagnostics. Icon.
2. Docs: `docs/architecture/convert2idf.md`, `pipeline.md`, `domain-model.md`, the smoke-test checklist, README and AGENTS.md summary, roadmap progress line and row; one decision-log entry for S6 (choices and completion).
3. A `scripts/rhino-smoke` spec for S6: the component writes a file to a temporary folder for every simplifier × aggregator of two plans; the file parses back and its invariants hold; Write off writes nothing; a validation failure blocks unless overridden.

## Acceptance criteria

- `scripts/verify.ps1` passes with 0 warnings; existing snapshots and icons unchanged except where B changes *Convert2BEM* outputs (documented).
- The minimal plan and four combinations of the canonical plan are kept as snapshots; all 32 combinations and every typology conversion parse back with consistent references, paired partners, and the floor area, glazing per orientation, installed loads, and multiplier × area totals of the building; no surface has a hole; every converted file passes the IDD check against EnergyPlus 25.2.
- With both options off, every surface between zones is adiabatic; with them on, every pair is mutual, except pairs across different multipliers (adiabatic, warned).
- The headless Rhino check of D passes; a fresh clone of `v0.9.0` passes `scripts/verify.ps1`.

## Open for later

Weather, climates, outputs, and running EnergyPlus (D-112); sourced envelope and program values (D-023); metabolic rate and load fractions as preset fields.
