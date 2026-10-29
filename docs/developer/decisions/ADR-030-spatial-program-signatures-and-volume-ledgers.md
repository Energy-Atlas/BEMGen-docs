# ADR-030: Spatial program signatures and explicit research volume ledgers

Date: 2026-10-28. Status: Accepted for the isolated research continuation; not merged or released. Supersedes ADR-028/029 only where their floor gate scope excludes configured spatial program checks.

## Context

Conserving total hourly gains at floor scale permits redistribution between source regions. Two equal equipment loads with complementary schedules and different latent fractions can conserve total watts and annual latent totals while changing each hour's latent gain. A control/mapping-only gate does not detect that experimental change. Likewise, absorption of a plenum or omission of basement air must not be hidden inside an undifferentiated floor-height comparison.

## Decision

Keep production aggregation and validation unchanged. Strengthen only the existing opt-in floor research validator and writer gate with `SpatialProgramCompatibility` and `HourlyHeatPartitions`. Compare every mapped contributing source and target, and each source pair, using actual physical normalization and existing central tolerances. Compare component identity, design and full-year input schedules, stored fractions, relevant people/activity declarations and known configured hourly partitions. Reject incompatible redistribution with source/target reasons. Compatible homogeneous merges and splits remain possible.

Automatic people heat, water and equipment/system response remain explicit unverified runtime contracts. Stored fraction values cannot reveal whether they originally came from an explicit declaration or a model default. Input preservation does not establish simulated thermal response.

Add a separate caller-supplied source/derived volume and boundary ledger API in Core. Require provenance, explicit roles and mappings; preserve absent, unavailable and known zero distinctly. Report raw nullable volume deltas, boundary/coupling changes, gaps and declared departures. Do not infer role or conditioning from names, fabricate unknown volumes, create a new geometry model or certify vertical equivalence.

## Consequences and validation

Research opt-in exports can now reject transformations still accepted by production validation. Override cannot bypass the research gate. The Grasshopper help text and IDF header describe the stricter scope without changing the existing input index, GUID or default false value. Exact composition/window/contact/orientation/construction and vertical contracts still require separate evidence.

Test-first evidence covers spatial swaps, homogeneous merging/splitting, complementary schedules with changed partitions, tiny positive loads, runtime unknowns, real writer callers, ledger invalid inputs and absence/unknown/zero distinctions. Independent bounded implementation review found no important or critical findings in source and tests; it preceded this ADR. Aggregate and native outcomes are recorded separately in the verification record. Generic ledger fixtures do not establish a populated authenticated DOE ledger. No annual simulation, measured energy accuracy, merge, push or release follows from these software checks.

See [research usage](../research/reference-program-contract.md) and the [approved continuation plan](../plans/2026-10-28-spatial-program-research-contract.md).
