# The results folder: a light central database, hourly Parquet per site, and raw and failure folders (design note)

> **Status:** Done on `feature/runner-site-status` (built, reviewed, verified, D-153); merged into `main` and pushed (D-154); released in `v1.5.0` (D-175) · **Date:** 2026-10-22 · **Decisions:** D-132, D-133, D-151, D-152; new: D-153, superseding D-132's hourly tables in the central database and D-133's `discard_ep_results` spec setting · **Branch:** `feature/runner-site-status` (D-152, not merged)

The owner's decisions of 2026-10-22, after the writer measurement below. This is one stage, run as D-111 sets out: this note; one test-first build; a review by a second agent; `scripts/verify.ps1` before the merge; a decision-log entry. It changes `scripts/IdfBatchRunner`, the generator's spec (one setting removed), and the documentation of what a run keeps (experiment outputs §8). It changes no metric definition, pipeline type, or Grasshopper component.

**Stop line.** The build ends with the branch verified, reviewed, and documented. It does not merge, tag, push, or release.

## Why

The writer was measured on 128 sites of the first mock suite (2026-10-21), with timers that were not committed:

| Per site | ms, with 16 EnergyPlus runs | ms, alone |
| --- | --- | --- |
| central database: site row + 11 hourly series | 31.5 | 27.2 |
| batch database: site row + 18 hourly series | 29.4 | 27.7 |
| `bemgen-hourly.csv` | 26.0 | 22.4 |
| metrics against the reference | 5.0 | 4.8 |
| `site_status` row, `bemgen-summary.csv` | 2.2 | 1.9 |

- **The hourly rows are almost all of the writer's work** (about 86 of 94 ms per site), on one thread, in plan order.
- **They are stored three times:** central, batch database, CSV.
- **The central database is almost all hourly rows:** 331 MB for 896 sites. The same 11 series as one Parquet file per site are 213 kB, about 40 % smaller.

## The run folder

```text
<results root>/run_<timestamp>/           --root or BEMGEN_RESULTS_ROOT
  batch.json                              settings, versions, machine, times; every site's name, IDF and weather paths, and status
  central.duckdb                          metric-relevant columns, with suite, test case, and site identifiers (below); no hourly rows
  hourly/<test case id>/<site code>.parquet   succeeded sites: the 18 series × 8760 hours, written by the worker that ran the site
  raw/<test case id>/<site code>/         sites that ran: eplusout.err; with --keep-raw, the whole EnergyPlus folder
  failure/<test case id>/<site code>/     sites that ran and did not succeed: the whole EnergyPlus folder
```

A run of plain IDF files has no test case IDs or site codes; its files and folders are named by the site's name (its file name): `hourly/<site name>.parquet`, `raw/<site name>/`, `failure/<site name>/`.

**Removed:** `results.duckdb` (the batch database), `bemgen-hourly.csv`, `bemgen-summary.csv`, `bemgen-run.json`, the central tables `hourly_fuel`, `hourly_end_use`, `hourly_ground`, and their views (`hourly_*_long`, `hourly_total`).

## 1. The central database

It keeps what the metrics need, with the identifiers to join it to the suite. Schema version 5.

- **`sites`** (succeeded sites):
  - **identity:** `site_key`, `site_name`, `site_id`, `energyplus_build` (kept for merge, which knows a site by site ID and build), `test_case_id`, `reference_site_key`, `reference_site_name`, `reference_site_id`, `is_reference`;
  - **zoning:** `simplifier`, `aggregator`, `iwht`, `fht`;
  - **areas, annual values, peaks, comparisons, temperatures, ground heat transfer, runtime** (`energyplus_elapsed_s`, `wall_clock_s`), as now;
  - **new:** `unmet_hours_heating`, `unmet_hours_cooling`, from `eplustbl.csv` before it is discarded (experiment outputs §8 lists the unmet hours as a sanity check).
  - **Dropped:**
    - `building`, `zoning`, `envelope`: the raw header lines; the suite tables carry the typed values;
    - `code_version`, `energyplus_version`: in `batches`;
    - `weather_file`, `weather_sha256`: the weather is the test case's; `test_cases` has its ID and SHA-256;
    - `concurrency`, `runtime_comparable`: moved to `site_status`.
- **`site_status`** (every site):
  - as in D-152, without the `unexpected_warnings` text, since `raw/…/eplusout.err` is kept;
  - **adds** `closure_max_residual_w`, `meters_written`, `concurrency`, `runtime_comparable`, `idf_version`, `run_warnings`, and `finished_utc`, which were in the batch database or `bemgen-run.json`.
- **Unchanged:** `batches`, `hours`, `suites`, `test_cases` (with `climate_zone`, the ASHRAE zone of the weather registry), `test_case_parameters`, `suite_sites`, and the views `site_results` and `site_overview`.
- **Climate zone.** A suite's test cases carry it. A run of plain IDF files has none, because the IDF header records only the weather file's name and SHA-256. It stays so unless a later change records it.

## 2. Hourly Parquet per site

- **Contents:** one file per succeeded site with the 18 series of the batch database today:
  - the six end uses by fuel;
  - the four fuels (EnergyPlus's facility meters, stored, D-132);
  - the total;
  - the two sensible diagnostics;
  - the four building temperatures;
  - the ground heat transfer.
- **Layout: a long table**, as D-132 chose: `site_id`, `energyplus_build`, `series`, `kind`, `end_use`, `fuel`, `zone_set`, `statistic`, `unit`, `hour`, `value`. ZSTD compression.
- **Written by the worker thread** right after its simulation and metrics, so the single writer keeps only the site and status rows. Each worker uses its own in-memory DuckDB connection and `COPY … TO … (FORMAT parquet)`, so there is no new dependency.
- **Named like the suite's IDFs** (the owner, 2026-10-22): `hourly/<test case id>/<site code>.parquet`, unique in a run, since every run has its own folder.
- **Joined to `sites` by `site_id` and `energyplus_build`, never by `site_key`,** which a merge renumbers; both are in every row. The README gives the query pattern:

  ```sql
  SELECT s.site_name, h.series, h.hour, h.value
  FROM sites s JOIN read_parquet('<run folder>/hourly/**/*.parquet') h USING (site_id, energyplus_build);
  ```

  No view is stored for it. DuckDB resolves a relative path in a view against the working directory, not the database's folder, so a stored view would break when the folder moves. The build checks this.
- **Size:** about 0.2–0.35 MB per site, so about 200–350 MB for the 1,024-site mock suite. The central database drops to a few MB.

## 3. `raw/` and `failure/`

- **Default:** after a site's rows and Parquet file are written, its EnergyPlus folder is cut down to `raw/<test case id>/<site code>/eplusout.err` (about 1 kB).
- **`--keep-raw`** keeps the whole folder there instead, as `discard_ep_results: false` did.
- **Failed sites.** A site that ran and did not succeed (`RunFailed`, `ReadFailed`, or completed without passing its verdict or closure) is moved whole to `failure/<test case id>/<site code>/`. A site that did not run (`ReferenceFailed`, `NoReferenceSite`, …) has no folder.
- **Where discard lives.** It moves from the suite spec to the runner. `settings.discard_ep_results` is removed from the spec schema and the generator; a spec that still has it is refused with a message (D-064).
- **What a run keeps.** Experiment outputs §8 says every site keeps its raw outputs or can rebuild them. That changes:
  - by default a site keeps its metrics, its hourly series, and `eplusout.err`;
  - the other EnergyPlus files are kept only with `--keep-raw` or on failure.

  §8 and "What the IDF requests" are updated to say this. No metric changes.

## 4. Resume, merge, progress

- **Resume is incremental.**
  - A site whose status row is in `central.duckdb` is done, whatever its status; a succeeded site's Parquet file is written before its row. Every other site runs.
  - The central database is opened, not rebuilt.
  - A reference that finished before the interruption gives its test sites' metrics from its Parquet file, so the comparison series must be readable back from it.
- **Merge.**
  - `merge --out <folder>` writes a folder: `central.duckdb` plus `hourly/` in the same layout, copying the Parquet files of the sites it adds.
  - Only there can two files want one name: the same test case and site code under two EnergyPlus builds. A merge refuses that pair with a message naming the site and the two builds. Before, `merge` kept both as two sites (D-132); a study uses one build.
  - `raw/` and `failure/` stay with their runs.
  - A central database of schema version 4 or earlier is refused.
- **Progress.** The D-152 lines stay.
  - Sites start in plan order: a shared queue instead of `Parallel.For`'s blocks, so that the `written` count follows the `simulated` count.
  - Measured on the 128 sites: the written frontier stayed at 0–8 until the last simulations, because each worker began in another block of the plan.

## Tests, first

- **Layout:** a run on the scripted EnergyPlus gives exactly:
  - `batch.json`, `central.duckdb`, `hourly/` with one file per succeeded site, and `raw/…/eplusout.err` per site that ran;
  - a failed site's whole folder in `failure/`;
  - none of the removed files.
- **`--keep-raw`:** whole folders in `raw/`.
- **Central:** the dropped columns are absent, the added ones present, `unmet_hours_*` read from `eplustbl.csv`, schema version 5.
- **Parquet:** 18 series × 8760 rows per file; joined to `sites` by `site_id` and build; values equal to those the runner computed.
- **Resume:**
  - an interrupted run continues without rerunning the sites with a status row;
  - a remaining test site's metrics against a reference read back from Parquet equal those of an uninterrupted run.
- **Merge:** the folder target copies the new sites' files only; merging the same run twice copies nothing; version 4 is refused.
- **Scheduling:** runs start in plan order.
- **Spec:** `discard_ep_results` is refused.
- **Opt-in:** the mock suite again on EnergyPlus, reporting the run time and the sizes of the central database and `hourly/`.

## Decided with the owner (2026-10-22)

1. **Hourly file names:** `hourly/<test case id>/<site code>.parquet`, as the suite's `idf/`; each run has its own folder, so names need be unique only in a run.
2. **Plan-order scheduling:** included in this stage.
