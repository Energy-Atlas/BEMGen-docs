# Sourced reference programs and research comparison contract

Status: **Done: backend implementation and aggregate verification; native/manual checks unresolved**. Owner approved 2026-10-28: sourced program presets, separated energy quantities, and checks blocking unintended conditioning/control changes; DOE 1.4_7.2 baseline, 1.3_5.0 selectable. Office height changes remain named controlled variants. No new annual/batch runs, feature-branch merge, push, PR, publication, deployment, trust change or memory update.

## Scope and evidence

The completed source audit, design checkpoint and two independent artifact reviews are preserved outside the repository in `BEMGen_reference_audit_2026-10-27_234625`. Those inventories are not repeated here. Source baseline: main `98aa569cdb16a797a336a62bf12f0cd9e3b57233` on the Razer Windows device. Existing main and 5R1C worktrees and the two untracked planning files stay untouched.

The first packet is the actual DOE new-2004 MidriseApartment Chicago/5A source, with both approved versions, because it serves the selected historical residential diagnosis without requiring an unverified detailed-office room allocation. Chicago/5A provenance tests are not a substitution for JFK weather or a New York validation. Fixed geometry comes from existing services/records; no new typology generator is in this stage.

## Interfaces and ownership

1. **Reference packet worker:** only `src/Lod.ProgramJson/Reference/`, its minimal resource/project registration, `tests/Lod.ProgramJson.Tests/Reference/`, reference fixtures and a scoped extraction tool. Reuse existing Core program/schedule/import structures. Provide a typed, immutable, provenance-bearing source catalog and explicit representability/departure results; make source program selection by original source zone/use, never Office/Service fallback. Keep original source metadata and counts separate from accepted departures. Publish the public API to the integrator before final integration.
2. **Research/reporting worker:** only new Core research-validation files/tests plus new Simulation comparison-reporting files/tests and the minimum parser/output changes genuinely needed. Reuse existing FloorValidator, ZoneMapping, schedules, tolerances and SimulationResultReader. Packet-independent generic APIs avoid a dependency cycle.
3. **Integrator:** plan/ADR/decision log/docs, end-to-end program-to-IDF tests and reviewed integration of worker commits. No concurrent shared-checkout edits. Workers use separate worktrees and may commit only owned files; no pushes or recursive delegation.

## Task 1: one source packet and representability matrix

- Write source-authentication, explicit version/climate/zone selection and no-fallback tests; witness RED before implementation.
- Independently extract a deterministic packet from the preserved original IDFs. Record archive/member/input SHA-256 and exact source object identities; retain notices and units. Do not commit original archives, outputs or generated binaries.
- Preserve use-specific gains, heat fractions, annual schedules and thermostat controls in supported Core structures. Fail explicit unsupported selection/mapping. Unknown/nonfinite/ambiguous source data must not silently receive example defaults.
- Keep ventilation/infiltration, humidity, geometry, constructions, shared services and design-day rules in a representability matrix: implemented, explicitly departed, or unsupported. A load-only import must not certify a complete DOE building. Any chosen calendar, scalar glazing representation or geometry adaptation is visible and opt-in where it loses source fidelity.
- Supply the baseline version by default and the approved older version as an explicit option. All fixtures remain Chicago/5A, not silently JFK.
- Run focused ProgramJson tests and the full affected ProgramJson suite; save RED/GREEN logs outside the repository.

## Task 2: reusable opt-in research and reporting contracts

- Write failing spatial-control tests: changed conditioned area, compensating equal-area conditioning swaps, one-hour schedule differences, changed target controls, missing/duplicate/nonfinite mappings, geometrically false source assignment, and compatible source splitting.
- Keep the production validation report separate; do not change existing simplifiers or weaken tolerances. Compare all contributing source controls and target controls by values over 8,760 hours. Enforce actual overlap/coverage and source identity rather than totals alone. Reciprocal contacts, internal-contact glazing and orientation contracts must be checked or reported explicitly unsupported, never inferred from a footprint union.
- Reuse/adapt the existing opt-in Batch 1 floor eligibility concept where it fits current types; do not import an old branch wholesale.
- Write reporting tests distinguishing sensible, latent and total thermal demand from measured/purchased energy, fixed-COP electricity estimates and monetary cost. Missing quantities remain unavailable, not zero. Constant-COP comparison defaults to 3 for both sides and cannot reverse a ratio on the same basis. Costs require explicit rates/boundary/currency and cannot be guessed.
- Use existing result-reader/series infrastructure. Do not change the existing paired sensible-load metric definitions or batch schema unnecessarily.
- Run focused Core and Simulation tests plus their affected aggregate suites, preserving actual logs.

## Task 3: integration, review and verification

- Inspect each worker diff and RED/GREEN evidence; bring only scoped commits into the isolated integrator branch. Resolve interfaces explicitly.
- Add integration tests importing a selected source program and propagating its values through existing generator/IDF services, with any non-source geometry/glazing assumptions labelled. No EnergyPlus execution.
- Review source authentication, representation honesty, immutability, full schedule/calendar/control behavior, missing-value reporting, dimensional tolerances and API boundaries. Run a fresh independent implementation review and fix material findings through tests.
- Run `scripts/verify.ps1` with real-engine opt-ins cleared, affected aggregate tests, docs links and appropriate native smoke coverage if safely available. Do not infer smoke outcomes from exit codes alone.
- Update source docs, an ADR and the decision log. Leave a tested patch on the feature branch; no merge/push/release. Report actual tests, omissions and limitations.

## Completion evidence

Tasks 1 and 2 were implemented test-first in isolated worker worktrees and integrated into `feature/reference-program-contract`. Task 3 adds eight existing-service caller tests and an independent archive/schedule checker. The combined Release build has zero warnings/errors; all nine test projects completed with 7,885 passed, 18 explicit engine/weather skips and zero failed. The source checker matched 54 source zones, 150 loads and 227,760 hourly values across both versions, and rejected a one-hour negative control. A bounded independent Sol review found no important/critical findings.

The independent source check corrected an initial mistaken interpretation of weather-file flags: ten explicit source holidays and explicit daylight saving still apply. Holidays are now retained; the unsupported DST-to-standard-time transformation requires its own acknowledgement. Full dated IDF schedule reconstruction replaced an incorrect test assumption that the existing writer must emit SpecialDays objects. Failed evidence is retained, and production writer schedule behavior was not changed to satisfy that assumption.

The native Program JSON harness launched but is blocked at a Grasshopper duplicate-file dialog before scenarios. No native pass, viewport appearance or full DOE/ClimateStudio energy equivalence is established. The external stage evidence record carries actual logs, versions, review limits, source checks and final preservation status. Source documentation and links are updated; public export/publication is deferred to the next approved tag.

## Deferred work and non-goals

No DOE geometry-branch integration, office generator duplication, generic courtyard replacement, annual simulation campaign or parameter tuning to force heating above cooling. Office adoption later requires a DOE-zone-to-detailed-room crosswalk, directional glazing/Core dependency reconciliation and separate original-source versus G1–G5 departure targets. Shared-service and design-day departures must stay explicit. Existing exact historical glazing mismatch remains recorded; no tolerance increase resolves it.
