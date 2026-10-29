# Runner progress lines and a status row for every site (design note)

> **Status:** Done on `feature/runner-site-status` (built, reviewed, verified, D-152); merged into `main` and pushed (D-154); released in `v1.5.0` (D-175) · **Decisions:** D-132, D-133, D-151; new: D-152 · **Branch:** `feature/runner-site-status`, from `main` `1ba4840` (D-151 fast-forwarded into `main` on 2026-10-21)

The first mock test suite (2026-10-19, 1,024 sites, results outside the repository) showed two gaps in `scripts/IdfBatchRunner`. This note fixes both. It changes no research definition, pipeline type, or Grasshopper component.

**Stop line.** The build ends with the branch verified, reviewed, and documented. It does not merge, tag, push, or release.

## 1. Progress lines when a site finishes

**What happened.** The runner simulates sites in parallel but writes them one at a time, in plan order: both databases, the site files, and then the progress line. With 16 EnergyPlus processes at a time the writer fell behind. EnergyPlus had nearly finished after 9.5 minutes (the sites' wall-clock times sum to 8.3 minutes at 16 at a time), while the log showed about 290 written sites. The log was correct about what was written, but useless for watching a run.

**The change.**

- **Report at completion.** Each site's progress line is printed when its simulation finishes, outside the ordered writer, with two counters:

  ```text
  [ 312/1024 simulated,  289 written] OK    203a3b163998287c/1c88bcfc  variant  heating … kWh, cooling … kWh, total … kWh  E+ 4.3 s, wall 4.6 s
  ```

  The line's verdict is the run's (`OK`, `WARN`, or `FAIL`). A site the writer later rejects (its hours are not the batch's) is reported again by the writer.
- **Flush each line**, so that any writer passed to the runner shows it at once.
- **The databases, `batch.json`, the site files, and the final summary keep their plan order** (working rule 9). Only the order of the console's progress lines depends on timing.

Writer throughput under load is not changed here; it is a follow-up.

## 2. A status row for every site in the central database

**What happened.** The central database's `sites` table holds only sites that succeeded. Status, verdict, and warnings were only in the batch database, which `discard_ep_results` deletes, so a suite run's failures could be counted only from `batch.json`.

**The change.** A new table `site_status` with one row per site of the run, whatever happened to it:

| Column | Meaning |
| --- | --- |
| `batch_key`, `site_key`, `site_name`, `site_id`, `energyplus_build` | identity; `site_key` is the site's key in `sites` when it succeeded |
| `test_case_id`, `reference_site_name`, `is_reference` | its place in its test case |
| `status`, `message`, `succeeded` | `Completed`, `RunFailed`, `ReadFailed`, `Pending`, or a not-run reason (`ReferenceFailed`, `NoReferenceSite`, `ModifiedSinceWritten`, …) |
| `verdict_passed`, `closure_passed`, `exit_code`, `severe_count`, `warning_count`, `unexpected_warning_count`, `unexpected_warnings` | the run's outcome, `NULL` when it did not run |
| `energyplus_elapsed_s`, `wall_clock_s` | runtime, `NULL` when it did not run |

- **`sites` and `site_results` do not change.** They keep the useful results only, so an analysis query cannot pick up failed rows by accident.
- **A view `site_overview`:** `site_status` left-joined to `site_results`, every site with its results where it has them.
- **Merge.** A site is one row in a database, as in `sites`: identified by its site ID and EnergyPlus build (a site without a site ID, whose IDF could not be read, by its name and run).
  - a site the source adds to `sites` brings its status row, and replaces any status row of the target that says it did not succeed;
  - a site that did not succeed in the source is added only when the target has no row for it;
  - a run is recorded in `batches` when it brings a site or a status row.
- **Resume and discard** keep the table: resume writes it again, and discard keeps `central.duckdb` whole.
- **Schema version 4.** A merge refuses a central database of version 3 or earlier.

## Tests, first

- **Progress:** on the scripted EnergyPlus, a slow first site; the lines of later sites come before its line, every line is flushed, and the databases' order is unchanged.
- **Status:**
  - a run whose reference fails: `site_status` holds every site, its test sites `ReferenceFailed`, the failed reference with its unexpected warning; `sites` holds the successes only;
  - a suite run with `discard_ep_results`: `site_status` holds all its sites;
  - `--resume`: the same rows as a run that was not interrupted;
  - merge: a site that failed in one run and succeeded in another is one `Completed` row; a run merged twice adds nothing; a failure-only run adds its batch and status rows; version 3 is refused.

## Documentation

The runner README (the central database's tables and the progress line), D-152.
