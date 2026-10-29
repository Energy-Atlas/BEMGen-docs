# ADR-028: Sourced reference programs and an opt-in research comparison contract

Status: Accepted; first-stage backend implementation on the feature branch, not merged or released

Date: 2026-10-28

Decision: D-177. This adds an explicit research workflow; it does not supersede production conditioning rules D-038 or change the paired sensible metrics of D-156/D-157.

## Context

The example presets are illustrative. The DOE geometry branch has sourced layouts and glazing but still uses illustrative programs, including service fallbacks. A matched source-file hash authenticates the geometry input, not a hybrid detailed-office program allocation. Existing production validation conserves loads and envelope quantities but intentionally reports conditioned area without enforcing equality. These contracts cannot establish a controlled comparison that holds spatial controls fixed.

Reporting also has several boundaries: zone sensible loads, zone total loads, district/supply energy, genuinely reported electricity or fuel, fixed-COP electricity estimates, monetary cost and computational cost. A valid number at one boundary must not silently stand in for a missing number at another.

## Decision

1. Provide a separate, provenance-bearing reference-program catalog. DOE 1.4_7.2 is the explicit baseline; 1.3_5.0 remains selectable. Keep illustrative examples unchanged. Unknown source uses or missing mappings fail rather than receiving Office or Service defaults.
2. Start with the actual new-2004 MidriseApartment Chicago/5A source packet. Preserve original source zone/use identity, source archive/member/file hashes, units, raw assumptions and notices. Climate and any expansion calendar are explicit; Chicago reference provenance is not JFK simulation weather or New York validation.
3. Separate imported program values from a representability matrix. Ventilation/infiltration, humidity, envelope, geometry, shared services and source design-day behavior are either represented, explicitly departed, or unsupported. A source-program preset cannot certify a complete DOE reference building. Geometry/glazing substitutions require explicit acknowledgement and provenance.
4. Add a floor-level research preflight beside the unchanged production validator. It validates complete/unique source assignments, actual spatial overlap, source/target conditioning and enabled thermostat sides, and full-year schedule values. Equal totals cannot excuse a spatial exchange of incompatible regions or independently changed target controls. Compatible splits are allowed. The report carries production validation separately and states any unverified geometry/whole-building contracts.
5. Add a comparison-reporting contract using the existing simulation reader and series types. Zone sensible/latent/total loads remain distinct from district/supply quantities and purchased energy. Missing observations stay unavailable. Fixed-COP electricity defaults to 3 for heating and cooling and is labelled an estimate with its boundary. Monetary cost needs explicit rates/currency/boundary; existing processor/memory cost metrics remain computational cost.
6. Reuse existing generators, geometry and parsers. Do not merge the DOE geometry branch wholesale or introduce duplicate office/courtyard generators in this stage. Office height changes are named controlled variants. Detailed-office adoption later requires a source-zone-to-room program crosswalk and reconciliation of shared Core/importer/directional-glazing dependencies.

## Acceptance boundaries

- Preserve ten explicit source holidays on the declared 2006 Sunday calendar. Explicit source daylight saving is retained but unsupported in annual expansion; preset creation requires a separate daylight-saving departure acknowledgement as well as the geometry acknowledgement. Values are source local-clock schedules, not standard-time observations.
- Raw source objects are an authenticated subset with explicit retained/omitted coverage, not a complete source file. Absolute shared elevator equipment remains unsupported and is never copied into every corridor program.
- `IdfOptions.RequireFloorResearchEligibility` enforces the floor control/mapping gate in the existing writer. Production override flags cannot bypass it; its default is false. It certifies neither vertical aggregation nor whole-building equivalence.

- Keep original-source measurements separate from accepted-departure targets; G1–G5 answer-key acceptance alone is not thermal equivalence to an original reference.
- Explicitly record shared-service omissions and design-day substitutions; annual schedule equality cannot establish design-day correctness.
- A floor research result does not establish reciprocal contacts, internal-contact window realization, geometry orientation, court/access semantics, whole-building equivalence or native thermal accuracy unless those checks are actually implemented and evidenced. Reports must identify unsupported contracts.
- Preserve the distinction between orientation metadata and geometric rotation. Shared-composer work later must rebuild reciprocal contacts, prevent internal-contact windows, preserve court identities and access/bay semantics, and use the existing dimensional tolerances.
- The historical tiny window-coordinate mismatch remains recorded. No tolerance is widened to turn it into exact geometry equality.

## Consequences

The first stage provides explicit program and comparison APIs while leaving existing Grasshopper components and illustrative defaults usable. New program catalog selection and research eligibility are opt-in; old simplifiers keep their documented behavior. A future user interface must expose source identity and departures rather than imply that an example or a modified height variant is an original DOE reference.

Tests must verify source identity and both versions, unsupported/missing selections, full-year schedules and controls, equal-area spatial swaps, compatible splits, source-map geometry, missing reporting quantities and COP/cost boundary rules. An existing generator/IDF integration test verifies parameter propagation without running EnergyPlus. No annual/batch campaign is authorized by this implementation decision.
