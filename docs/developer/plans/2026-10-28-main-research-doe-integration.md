# Main, research and DOE geometry integration

**Status:** Done for integration and software verification; new-branch push approved by the owner on 2026-10-28 and its remote confirmation recorded separately.

**Goal:** Preserve current remote main and combine the saved research chain with the complete DOE geometry branch on a separate integration branch.

**Inputs:** main `98aa569cdb16a797a336a62bf12f0cd9e3b57233`, research `fd9ac3b9c054b0c8d02bf1c47674853ff5f2a253`, DOE geometry `a527da5d0ffeb6de0d1c549dff2ab2568dde8738`. Main is already an ancestor of both tips. The seven saved research checkpoints occur once in the research chain; merge the DOE tip without replaying them. Preserve both histories for this new integration branch; this is not integration into main.

## Steps and checks

- [x] Verify the configured existing remote, fetch its current main and DOE tips, inspect ancestry, and create a new isolated branch/worktree without changing the original checkout.
- [x] Retain the research README notice and both decision-log histories when resolving the two textual merge conflicts.
- [x] Pin the cross-branch skylight identity regression with unchanged and same-area placement/host/shape mutations. Compare explicit skylight outlines on their registered ceiling hosts using existing numerical tolerances; do not change production generation, conservation or acceptance tolerances.
- [x] Review all new executable/build source, dependency and initialization routes before explicitly refreshing the fail-closed software-only source policy. Keep engine/weather opt-ins absent in the child process and combine positive narrow test selectors with every mandatory exclusion.
- [x] Run the harmless guard regressions and affected software test projects; record actual verdicts, failures and coverage limits. Do not run the unreviewed default full-solution runner or any real engine/native harness.
- [x] Independently review the combined source and integration compatibility change. Resolve important findings and repeat only affected checks when necessary.
The authorized operational close-out is to commit the reviewed integration, refresh the remote to detect races, verify current main ancestry, push only the new branch without force, and verify its remote SHA equals the tested commit. The external verification record carries the actual publication result. Keep the worktree.

## Boundaries

The complete DOE branch includes all 15 commercial reference geometry types, shared orientation glazing, skylights, room/storey multipliers and illustrative program-map presets. Its inclusion does not authenticate new source data or establish energy equivalence. Existing DOE departures and gaps remain visible.

`ProgramsPreserved` continues to compare configured thermal input signatures; it does not certify the semantic meaning or physical authenticity of a source `ProgramKey`. The DOE branch's key-based grouping remains unchanged. Exact identity still refuses zone multipliers above one. A retained `SelfAdjacent` label is not evidence authenticating its physical justification. Full construction and bay/stair/court ownership evidence remain unavailable; no full exact-composition claim follows.

No original worktree, untracked planning document, incident output, user Rhino process or persistent setting may be changed. No EnergyPlus, annual/batch/production simulation, PR, main update, force-push, release or publication. Native/viewport checks remain pending under this software-only scope. The separate 5R1C feature branch is outside these explicitly selected integration inputs.

## Verified software scope

The combined tree passed 11,092 tests with zero failures: Core 1,020; Generators 3,051 (one pre-existing A2 atlas-input placeholder skipped); Integration 3,629 including six skylight compatibility cases; Export 3,114; ProgramJson 214; synthetic Comparison 18 and Results 46. All 11 harmless guard regressions passed. The complete solution built with zero warnings/errors through an inspected build-only guard adapter whose test callback is a no-op. This does not establish default full-solution test-runner safety or execution. The compatibility RED run retained one positive pass and five expected failures before the fix. Documentation links were checked separately. No engine or native run was performed.
