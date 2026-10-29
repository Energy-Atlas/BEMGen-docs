# Exact-composition preflight implementation plan

Status: Bounded implementation and guarded software verification complete. Preserve stage-five `d80b094db46336c79192ac71436c0e834e302ba5`. Missing ownership/construction and wider physical/native/thermal contracts remain open.

Goal: Screen actual source/target floor layouts for exact geometry/program identity and independently mutated courtyard failures. This is not a composer, permissive simplifier or thermal equivalence certificate.

Architecture: Core-only inspectable preflight with explicit Preserved/Failed/Unavailable statuses and default-off options. Reuse existing source mappings, program signatures and central tolerances. Missing ownership or construction evidence remains unavailable; distinguish supported geometry preservation from full claimed eligibility. Do not change production validation, generators, simplification, GUIDs or installed settings.

Tech stack: existing Core netstandard2.0, Integration net8.0 and three courtyard generators. No new package or engine dependency.

Spec: coordinator-approved `BEMGen_guard_stage5_2026-10-28/exact-composition-contract-proposal.json` and existing research contracts. Scope is registered one-floor identity; no general placement/composition engine.

- [x] Root inspected actual ledger test methods, whole Integration initialization/source, project/transitive source references, build properties, activation attributes and inherited injection names. A guarded Integration-only adapter ran exactly the existing three ledger tests: 3 passed, zero skipped, build zero warnings/errors. It ANDs the positive selector with all fixed engine/weather exclusions and keeps activations absent. Default full-solution runner is not claimed exercised.
- [x] One bounded implementer owns only new Core preflight/type file(s) and `tests/Lod.Integration.Tests/Reference/ExactCourtCompositionTests.cs`. Provide precise API first, then RED tests and minimal compiling unavailable-report scaffold. No tests, dotnet, engine, native actions or policy refresh by implementer; root inspects new code and runs all guarded tests after explicitly refreshing the reviewed inventory.
- [x] Six canonical OpenCourt/EnclosedCourt/CourtCluster cases at 0/37 degrees through actual generators and NoSimplification. Supported positive geometry/input checks preserve identity, missing ownership remains unavailable. Independent reciprocal contact, exposure/internal-window, true-orientation, placed-window, program and explicit ownership mutations exercise public preflight behavior; do not mirror an isolated helper.
- [x] Root records actual RED, authorizes minimal implementation, re-inspects activation paths and source diff, refreshes reviewed policy explicitly, and records guarded GREEN. No unguarded or inherited-env test command.
- [x] One bounded independent source review, affected reviewed guarded Core/Generators/Integration software tests and docs/D-182 completed. Exact commit/evidence/preservation are recorded externally after the local source commit. No engine-bearing project or full solution runner without a new explicit audit.

Review focus: duplicate/missing identities and invalid mapping cannot throw or appear preserved; source and target orientation compared independently in radians using central Angle; missing semantic ownership/construction never inferred from IDs or program keys; window offset/sill/width/height/host changes detected even when glazing totals match; reciprocal geometry/exposure checked independently of floor conservation totals. Source and target footprints/parts must be checked without silently repairing geometry.

Known boundary: Surface records do not contain full construction assignments, and canonical generator records do not establish all physical bay/stair/court ownership. Expose those as unavailable. A geometry-only preserved result is not labelled full exact-composition eligibility.

## Verification checkpoint

The six canonical identities and independent mutations observed 23 RED assertion failures before implementation, then 23 GREEN. A separate actual glazing/baseline attribution regression observed one RED beside those 23 passes, then all 24 passed. Its program-input preservation remains independent from the failed production geometry baseline. The equal-area spatial-swap fixture additionally verifies production conservation passes while the new program identity check fails.

Affected inspected software projects ran only through the guard: Core 853, Generators 518, Integration 2,801; 4,172 passed, zero skipped/failed. The final test-only conservation oracle was then verified by the 24-case guarded selector without production source changes. No engine-bearing test project or full solution runner was selected. One bounded independent review found no important/critical findings; it preceded the final additional test-only oracle and final outcome wording. Original interrupted RED stderr handling and all complete outcomes are retained externally. No new engine/native/user-process action occurred.
