# ADR-031: Default-off registered-floor exact identity preflight

Date: 2026-10-28. Status: Accepted bounded implementation on the isolated feature branch; not merged or released.

## Context

Production floor validation checks conservation and mapping, not exact contact/window/topology identity. The opt-in program research gate deliberately leaves those geometry contracts unverified. A total glazing or floor-area match can coexist with a missing reciprocal contact, a moved equal-area window or a spatially exchanged program. These differences need inspectable outcomes before any broader geometry adoption.

## Decision

Add an explicit Core-only `ExactCompositionPreflight`, default disabled. It compares actual source and target records of one already registered floor. Identity and exact-composition declarations are distinct from simplification; this increment does not implement a composer, arbitrary placement registration or vertical composition. Production validation, simplification, aggregation, generators, GUIDs and exporter defaults are unchanged. The preflight is a backend caller API, not automatic IDF/Grasshopper enforcement.

Each invariant returns Preserved, Failed or Unavailable. Supported geometry and program outcomes are separate from full exact-composition eligibility. Compare complete one-to-one identity mapping, source/target footprint/parts, reciprocal directed contacts, exposure, no internal-contact windows, independent true orientation and placed-window geometry/host. Windows have no stable model ID, so this bounded screen uses their mapped surface host and ordered ordinal plus offset/sill/width/height and host placement. Reuse existing spatial program/control/configured-partition checks and central geometric/angular tolerances; define no new energy tolerance or automatic geometry repair.

Explicit caller ownership declarations may establish declaration identity/coverage and retain evidence IDs. They do not authenticate physical bay/stair/court semantics; unknown ownership is Unavailable and is never inferred from names, space types or program keys. Core surfaces do not contain full construction assignments, so construction remains Unavailable. A geometry/input-preserved result cannot be presented as full exact-composition eligibility while required evidence is unavailable.

## Verification and consequences

Use the actual OpenCourt, EnclosedCourt and CourtCluster generators at 0 and 37 degrees through NoSimplification. Positive fixtures must retain unavailable evidence distinctly. Independent negative mutations change a reciprocal contact, exposure, internal glazing, independent orientation, window placement while holding total glazing, spatial programs with matched controls/totals, and explicit ownership. Invalid identities or mappings must be reported rather than converted into a pass.

All execution uses the reviewed source-inventory guard and an inspected narrow adapter. Engine/weather activations are absent and fixed exclusions are ANDed with a positive software selector. A successful narrow adapter run does not claim that the default full-solution runner has been exercised. Unreviewed build/runtime injection or new activation paths stop execution. Actual test counts and retained failures belong to the external evidence record.

This screen does not certify construction equivalence, physical ownership authenticity, vertical coupling/multipliers/shading, native discovery/archive/viewport behavior, annual energy response or measured accuracy. It changes no legacy acceptance rule and starts no simulation, installation, push, merge or publication.

See [implementation plan](../plans/2026-10-28-exact-composition-preflight.md) and [research usage](../research/reference-program-contract.md).
