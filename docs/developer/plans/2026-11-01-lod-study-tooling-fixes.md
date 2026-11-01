# LOD study tooling fixes after the 2026-10-31 review (design note)

> **Status:** Done: E1 to E8 and F4 (D-219 to D-223, PR #20); the R4 small-hotel rerun after BG1 (D-224) · **Date:** 2026-11-01 · **Stage:** LOD1 of the owner-approved fix programme of the 2026-10-31 review (issues E1 to E8 and F4, accepted 2026-11-01) · **Decisions:** D-185, D-188, D-193, D-200 to D-203; new: D-219 to D-224 · **Branch:** `fix/lod1-study-tooling`

The review of the end-to-end LOD study workflow (subject 5, findings S5-01 to S5-13) found that the published R6 drop regenerates except its repeat timing check, whose run folder is gone, and that the recommendation rule, the kept-twin order, the cost medians, and the published files' self-provenance answer the study question less well than they should. The owner accepted every fix with the choices below. Nothing here changes BEMGen's pipeline, a simulation, or a stored metric: the changes are in `scripts/lod-study/` (the report, the R6 tables, the driver), the published files in `research/lod-study/results/`, and the study documents.

## 1. Choices

| Issue | Choice (owner, 2026-11-01) | Decision |
| --- | --- | --- |
| E1 `study_tables.py --check` reads the deleted `D:/bgdiag` | Defaults move to durable locations under `D:/bemgen-results/lod-study/`; the lost repeat-check evidence is archived as published and marked not re-derivable; a re-time step is left for an idle machine (not run now: other agents load the machine). | D-219 |
| E2 "coarsest" can be finer than the reference | Candidates are the zonings with at most the reference's zone count; a cell where only finer zonings meet the threshold has no recommendation and `finer_than_reference: true`. | D-220 |
| E5 zonings excluded before simulation are absent | Every planned zoning is an entry of `zonings`; an `Invalid` one has `succeeded: false`, `status: "Invalid"`, and a `reason` (`Invalid: MultipliedRooms`, `Invalid: PlanTooNarrow`), and its simplifier spelled as the runner spells the written ones (`PerimeterCore PerimeterDepth=3`). A 1.2.0 document must carry the members 1.2.0 adds (the schema's `allOf`). | D-220 |
| E3 the kept twin is the string-sort first | Within a duplicate group the kept site is the one closest to the reference's heat-transfer setting: both on, then IWHT on and FHT off, then IWHT off and FHT on, then both off; then the simplifier by name (without its options), join pieces (unset, off, on), the perimeter depth as a number, and the stacker by name. | D-221 |
| F4 cost medians pool twins and weight prototypes by site count | Duplicate twins (R3's `duplicate_of`) are dropped; costs are reported per prototype; a zoning's across-prototype figure, and the overall one, is the median of its prototype medians (equal weight). | D-222 |
| E4 analysis entry points untested and ungated | A fixture end-to-end test runs `report.main` on a small central database and suite written by the test; `scripts/verify.ps1` runs the lod-study tests and `make_specs.py --check`, and `study_tables.py --check` when `BEMGEN_LOD_STAGES` names the stage folders. | D-223 |
| E6 heating unjudged in many cells; no sensitivity | The methodology and the report state the unjudged counts; the published file carries them (`judged_loads`, and `judged` per entry) and a threshold sensitivity table (`sensitivity`: error limits × 0.5, 0.8, 1.2, 2.0, the area limit unchanged). | D-223 |
| E7 OS-dependent digests and weak self-provenance | `report.py` writes LF; `source` names the suites and runs, and `suites` and `runs` list them; the R3/R4 gate strings are derived from the status counts; `run.ps1` refuses a dirty working tree, records the commit, and refuses an EnergyPlus whose build differs from the pin in `study.json`. | D-223 |
| E8 second-person gaps | `scripts/lod-study/README.md` gains "Running a stage on another machine". | D-223 |
| (later) BG1's heat-transfer rule | After BG1 merges, R4's small-hotel cells run again with that commit (D-224, reserved). | D-224 |

## 2. Schema 1.2.0 (additive)

`lod-recommendations-v1.schema.json` accepts 1.0.0, 1.1.0, and 1.2.0. 1.2.0 adds only members:

- top level: `suites` and `runs` (the IDs `source` names), `deduplication` (the rule, the energy tolerance, the kept-site order), and, in the consolidated main file, `judged_loads` and `sensitivity`;
- an entry: `judged` (`sensible_heating`, `sensible_cooling`: whether the reference's load is judged) and `finer_than_reference`;
- a zoning: `status` (the site's status in the suite or the run) and `reason` (null when it succeeded).

`coarseness` states the bounded rule. A reader of 1.x that ignores unknown members reads 1.2.0, but two readings change meaning: `zonings` now holds the excluded zonings too (`succeeded: false` was "ran and failed"; it is now "did not succeed", with `status` telling `Invalid` from `RunFailed`), and an empty `recommended` can carry `finer_than_reference`. The atlas site (ADR 0050 §4 import, stage REL-A) should show excluded zonings as not generated, not as failed, and show the flag; the sidecar's "the 24 main zonings each" becomes true.

## 3. Durable sources (E1)

- The stage folders `D:/bemgen-results/lod-study/{main,ht,timing}` and the suites in `D:/bemgen-suites` stay read-only.
- `report.py` of this change writes R3's and R4's reports into `D:/bemgen-results/lod-study/r6/{main,ht}-report` (commands in the README); these are `study_tables.py`'s defaults.
- The repeat check of D-202 (`D:/bgdiag/r6-retime`, run `run_20261029-144634`) was deleted before 2026-10-31 with no copy. Its summary, as published at `137db0e` (the `timing.recheck` block and the per-site table of the report §5.5), is archived in `research/lod-study/archive/r5-repeat-check-20261029.json` with the SHA-256 of the files it was taken from; `study_tables.py` reads that archive when `D:/bemgen-results/lod-study/recheck` holds no run, and marks the published block `evidence: "archived"`, `rederivable: false`. `scripts/lod-study/recheck.py` prepares the re-time (the 34 IDFs and `sites.csv`); running it needs an idle machine and is open.

## 4. Tests first

Each change starts with a failing test in `scripts/lod-study/tests/`: the bounded candidate rule and the flag, the kept-twin order, the excluded zonings, LF output and `source`, the cost medians, the sensitivity and judged counts, the archived recheck, and the end-to-end `report.main` fixture.
