# IdfBatchRunner: batch simulation and building-level results (design note)

> **Status:** Done (D-132; built 2026-10-12, not merged). Approved 2026-10-12 (the owner) · **Date:** 2026-10-12 · **Decisions:** D-016, D-111, D-130, ADR-019; new: D-132 · **Branch:** `feature/idf-batch-runner` (from `main` `9dcc5d5`, `v1.3.0`) · **Definitions:** [experiment outputs](../research/experiment-outputs.md) · **Runner:** [energyplus-runner.md](../architecture/energyplus-runner.md)

This is one stage run as D-111 sets out: this note first; one test-first build on the branch; a review of the diff by a second agent; `scripts/verify.ps1` before the merge; one decision-log entry. No component and no pipeline type changes, so the headless Rhino check is not needed. No GUID changes.

**Stop line.** The build ends with the branch verified, reviewed, and its documentation synchronised. It does not merge, tag, push, or release. There is no release for this tool for now (the owner, 2026-10-12): no version bump, no tag, nothing in the release files.

## The owner's answers (2026-10-12)

1. **No release** for now.
2. **Location:** `scripts/IdfBatchRunner/`, a C# project named like the other C# projects, not shipped with `src/` or the release files.
3. **Hourly results:** a **long table** in a **DuckDB** database, because other programs open it directly (Python, R, Java, Node, the DuckDB command line). Checked: DuckDB.NET (MIT) writes it from C#, and Python's `duckdb` 1.5.5 is installed on the development machine to read it back.
4. **No case without a reference is run.**
5. **`runs/<case>/`** is kept, for now.
6. **A central database** that collects, across all batches, only the useful results of every case, its hourly loads by fuel, and its hourly loads by end use. The per-batch artefacts (the batch database, `summary.csv`, `runs/<case>/`) are built as described, but are expected to be discarded later, so the central database must stand on its own.

## Goal

A C# command-line tool, **IdfBatchRunner**, that takes a set of IDFs written by *Convert2IDF* (version 1.3.0 or later), runs EnergyPlus on each that has a reference in the set, and writes one DuckDB database with, for every case:

1. the **building-level hourly time series** (8760 hours) as a long table: every end use by fuel, every fuel, the total load, the sensible diagnostics, and the building temperatures of experiment outputs §5;
2. one **summary row** with the case record (§7), the run status, both floor areas, the annual end uses and fuels, and every metric of experiment outputs §2 to §6, the comparison metrics against the case's reference.

It then adds every completed case to a **central database** that accumulates across batches: the useful results, the hourly loads by fuel, and the hourly loads by end use (see [The central database](#the-central-database)).

The Grasshopper run component that ADR-019 deferred stays deferred; nothing here touches Grasshopper.

## What exists (version 1.3.0)

- **The IDF** already requests what is needed: the hourly meters of experiment outputs §1, each only when its source exists (`IdfOutputs.Research`), `Zone Mean Air Temperature` hourly for every zone, `AllSummary` in comma style, and the case record in the header (`! Case building:`, `! Case zoning:`, `! Case weather:`, `! Case envelope:`).
- **`Lod.Simulation`** runs one case (`EnergyPlusRunner`), judges it (`RunVerdict`, `ExpectedWarnings`), reads it (`SimulationResultReader` → `SimulationResult`: the twelve meters of `ResearchMeters.All` as 8760-hour series in W, the zones with their temperatures, both floor areas, the runtime, the case record), and computes the metrics (`ExperimentMetrics.Compute(variant, reference)` → `CaseMetrics`).
- **`scripts/eplus-check`** runs many IDFs in parallel and only judges the error files.
- **The end-to-end tests** pair cases with their reference, write a metrics CSV (`tests/Lod.Simulation.Tests/EndToEnd/MetricsReport.cs`), and check that the end uses sum to the total every hour (`EndToEndChecks.EndUses`). Both live in the tests, so nothing outside them can use them.

What is missing is the batch: finding each case's reference among the files before running, the end-use-by-fuel view, the hourly timestamps, and the database.

## End uses and fuels

The meters the IDF writes form a complete end-use-by-fuel matrix. Ideal loads have no fans (`ZoneVentilation:DesignFlowRate` is written with a fan pressure rise of 0), and BEMGen writes no exterior equipment, so each fuel is exactly the sum of its end uses:

| End use | Electricity | NaturalGas | DistrictHeatingWater | DistrictCooling |
| --- | --- | --- | --- | --- |
| Heating | | | `Heating:DistrictHeatingWater` | |
| Cooling | | | | `Cooling:DistrictCooling` |
| InteriorLights | `InteriorLights:Electricity` | | | |
| InteriorEquipment | `InteriorEquipment:Electricity` | `InteriorEquipment:NaturalGas` | | |
| WaterSystems | | | `WaterSystems:DistrictHeatingWater` | |
| **Fuel total** | `Electricity:Facility` | `NaturalGas:Facility` | `DistrictHeatingWater:Facility` | `DistrictCooling:Facility` |

- The **total load** is the sum of the four fuel meters (experiment outputs §1), as `SimulationResult.Total` already computes.
- `Heating:EnergyTransfer` and `Cooling:EnergyTransfer` (sensible only) are kept as diagnostics.
- **Closure check, per case:** Σ end uses of each fuel = the fuel meter, and Σ fuels = the total, every hour within `ToleranceSettings.LoadEquals`. A case that fails it is kept and reported (the `closure_passed` and `closure_max_residual_w` columns and a console warning). This is the check the end-to-end tests make, moved into the library so that the tool and the tests share it.

## Planning the batch: references first, no case without one

The metrics of §3 (peak duration) and §4 (comparison) need the case's reference (experiment outputs, "Reference case"). The tool pairs the cases **before running anything**, from the case records in the IDF headers, without any naming convention:

- **Group key:** the building line, the envelope line, and the weather file's SHA-256 from the header.
- **Reference:** the case of the group whose zoning line is exactly `simplifier NoSimplification; aggregator Stack; IWHT=true FHT=true`, the line `IdfCaseRecord` writes for the reference. The constant lives in `Lod.Simulation` (which may not depend on `Lod.Export`); a test in `Lod.Simulation.Tests`, which already references `Lod.Export`, checks that the two agree.
- **Not run** (the owner: no case without a reference), each with a status in the `cases` table and a console line:
  - `NoReferenceCase`: the group has no reference;
  - `IncompleteCaseRecord`: the header lacks the building, zoning, weather, or envelope line, so the case cannot be grouped;
  - `WeatherNotFound` / `WeatherMismatch`: the weather file cannot be resolved, or its name or SHA-256 differs from the header's (as `CaseRecord` checks it);
  - `DuplicateCase`: the same case ID (the same IDF and weather bytes) given twice; the first in name order runs;
  - `AmbiguousReference`: two different files in one group both carry the reference zoning line (for example written by two code versions); no case of that group runs, since the comparison would depend on which is chosen.
- **Two phases.** Phase 1 runs the references; phase 2 runs the variants whose reference completed and was read. A variant whose reference failed is not run (`ReferenceFailed`).
- A reference is its own reference, so its comparison metrics are 0 (experiment outputs, "Reference case").
- Groups and cases are ordered by name, so the plan, the run order within each phase, and the database rows are deterministic whatever the input order.

## The tool

`scripts/IdfBatchRunner/IdfBatchRunner.csproj` (`net8.0`, console, assembly `IdfBatchRunner`), in `BEMGen.sln` so that the verify gate builds it. It is a development tool, like `eplus-check`: it is not in `src/`, not packaged, and not released.

```powershell
dotnet run --project scripts/IdfBatchRunner -c Release -- `
  --energyplus D:\EnergyPlusV26-2-0 `
  --weather D:\EnergyPlusV26-2-0\WeatherData `
  [--root D:\bemgen-results] [--parallel N] [--timeout <minutes>] [--allow-version-mismatch] [--plan-only] `
  <file.idf | folder>...

dotnet run --project scripts/IdfBatchRunner -c Release -- --resume D:\bemgen-results\run_20261012-143005 [--parallel N] [--timeout <minutes>]

dotnet run --project scripts/IdfBatchRunner -c Release -- merge --out D:\bemgen-results\all.duckdb <run folder | central.duckdb>...
```

- **Inputs:** IDF files and folders (each folder stands for its `*.idf` files, in name order), as `eplus-check` takes them.
- **`--weather`:** a file, used for every IDF; or a folder, in which each IDF's `! Case weather:` file name is looked up. EnergyPlus needs the weather file at run time (ADR-019), so it cannot come from the IDF alone.
- **`--root`:** the results root; when omitted, the environment variable `BEMGEN_RESULTS_ROOT`; with neither, a usage error (the owner, 2026-10-12). A root inside the repository is refused (GLOBAL.md git rule 4), as `eplus-check` does. Every run makes a new folder `run_<yyyyMMdd-HHmmss>` in it (local time; `-2`, `-3` if two runs start in the same second).
- **`--parallel`:** default half the logical cores. Runtimes are recorded with their concurrency and marked comparable only for `--parallel 1` (experiment outputs §6).
- **`--resume <run folder>`** (the owner, 2026-10-12): continues an interrupted run in its own folder, with the inputs, weather, installation, and options that its `batch.json` recorded (only `--parallel` and `--timeout` may be given again). A case whose folder holds a completed run of the same case ID (its `bemgen-run.json`) is read again, not rerun; a case folder without one is emptied and run again. Both databases are rebuilt.
- **`merge`:** combines the `central.duckdb` of several runs (or run folders) into one central file, new or existing, skipping cases it already holds; see [The central database](#the-central-database).
- **`--plan-only`:** prints the groups, the references, and the cases that would not run, with their reasons, and writes nothing.
- **Exit code:** 0 when every case given ran, completed, passed its verdict, and passed its closure check; 1 when any did not; 2 for a usage error.

### Output folder

The owner's layout (2026-10-12): one folder per run, holding the run's central database; one folder per case inside it.

```text
<root>/
  run_<yyyyMMdd-HHmmss>/
    central.duckdb             this run's central database: useful results, hourly by fuel, hourly by end use (kept)
    results.duckdb             the full batch database (discardable)
    batch.json                 the batch: options, versions, machine, start and end time, counts by status (resume reads it)
    <case>/                    EnergyPlus's own output folder for the case (eplusout.*, eplusout.sql included)
      bemgen-run.json          the run's case ID, exit code, wall clock, written after EnergyPlus finishes (resume reads it)
      bemgen-hourly.csv        the case's hourly series as a long table: hour, month, day, hour_of_day, series, value (discardable)
      bemgen-summary.csv       the case's row of the cases table (discardable)
```

`<case>` is the IDF's file name without extension; a name that repeats gets `-2`, `-3`, as in `eplus-check`. A case that was not run has no folder; its status is in `results.duckdb` and `batch.json`. The `bemgen-` prefix keeps the tool's files apart from EnergyPlus's.

### The batch database

`results.duckdb`, written by the tool alone through one connection, a case at a time as it finishes (DuckDB allows one writer). Loads are in W (the hour's energy / 3600 s, so a series' sum / 1000 is its annual kWh); temperatures in °C, standard deviations in K.

| Table | Rows | Columns |
| --- | --- | --- |
| `batch` | 1 | the tool's code version, the EnergyPlus version and build, processor, logical cores, concurrency, the command line, start and end time (UTC), and the number of cases by status |
| `cases` | one per IDF given, run or not | **identity:** `case_key` (integer, in name order, the key of `hourly`), `case_id` (the SHA-256 of §7), `case_name`, `idf_path`, `building`, `zoning`, and the zoning line split into `simplifier`, `aggregator`, `iwht`, `fht`, `envelope`, `weather_file`, `weather_sha256`, `code_version`, `energyplus_version`, `energyplus_build`, `group_id`, `reference_case_key`, `reference_case_name`, `reference_case_id`, `is_reference`; **status:** `status` (`Completed`, `RunFailed`, `ReadFailed`, or a not-run reason above), `message`, `verdict_passed`, `exit_code`, `severe_count`, `warning_count`, `unexpected_warnings`, `closure_passed`, `closure_max_residual_w`, `meters_written`; **areas:** conditioned and total floor area, zone count, Σ multipliers; **annual (§2):** kWh of every end use × fuel, every fuel, and the total, and EUI per conditioned and per total floor area of heating, cooling, and total; **peaks (§3):** maximum, P99, P95, P90 of heating, cooling, and total in W and per both floor areas, the reference's thresholds and the hours above them; **comparison (§4):** CV(RMSE), quantile NRMSE, Kolmogorov–Smirnov of heating, cooling, and total; **temperature (§5):** the annual mean of the hourly mean and of the hourly SD, over all and over conditioned zones; **runtime (§6):** EnergyPlus elapsed, wall clock, concurrency, comparable |
| `series` | 17 | `series` (the key: the meter name, `Total`, or a temperature series such as `TemperatureMean:AllZones`), `kind` (`EndUse`, `Fuel`, `Total`, `Diagnostic`, `Temperature`), `end_use`, `fuel`, `zone_set`, `statistic`, `unit` |
| `hours` | 8760 | `hour` (1–8760), `month`, `day`, `hour_of_day` (1–24, hour ending), from the run period's own timestamps; every case's timestamps must equal them, or the case is `ReadFailed` |
| `hourly` | 17 × 8760 per completed case | `case_key`, `series`, `hour`, `value`: the long table |
| `hourly_long` (view) | | `hourly` joined with `cases` (name, building, zoning, envelope, weather), `series`, and `hours`, for analysis without joins |

- A metric without a value is `NULL`, with its `MetricFlag` in a `<column>_flag` column, never 0 or infinity (experiment outputs, zero guards).
- A meter EnergyPlus did not write is zero every hour (experiment outputs §1) and its rows are written; `meters_written` says which were written.
- A temperature over conditioned zones without a conditioned zone (`NoConditionedZone`) has no rows; its flag is in `cases`.

Reading it back, as the README will show:

```python
import duckdb
con = duckdb.connect(r"D:\bemgen-results\run_20261012-143005\results.duckdb", read_only=True)
con.sql("select case_name, zoning, hour, value from hourly_long where series = 'Total'").df()
```

**Dependency.** `DuckDB.NET.Data.Full` (MIT, bundles the native DuckDB library) at **1.5.5**, matching the Python `duckdb` 1.5.5 on the development machine, in `Directory.Packages.props`. Only the tool and its tests reference it; `Lod.Simulation` stays BCL-only, as ADR-019 requires for the deferred component. The README states the DuckDB versions that open the file (DuckDB reads files written by the same or an older storage version).

### The central database

`central.duckdb` in each run folder (the owner, 2026-10-12): the run's completed cases with only what the analysis uses. It holds no paths, warning texts, or not-run cases, so it stands on its own when the rest of the run folder is discarded. `merge` combines the central files of several runs into one, so that the study's results can live in one file.

**What goes in.** A case is added when it ran, completed, passed its verdict, and passed its closure check. A variant runs only when its reference did all of that (phase 2), so every variant's reference is in the same central file.

| Table | Rows | Columns |
| --- | --- | --- |
| `meta` | 1 | the central schema version (the tool refuses to merge a file of another version rather than guess), creation time |
| `batches` | one per run | `batch_key`, the run folder's name, the tool's code version, EnergyPlus version and build, processor, logical cores, concurrency, start and end time |
| `cases` | one per case | **identity:** `case_key` (integer, the key the hourly tables use), `batch_key`, `case_id` (SHA-256, §7), `case_name`, `building`, `zoning`, `simplifier`, `aggregator`, `iwht`, `fht`, `envelope`, `weather_file`, `weather_sha256`, `code_version`, `energyplus_version`, `energyplus_build`, `group_id`, `reference_case_key`, `is_reference`; **areas**, **annual (§2)**, **peaks (§3)**, **peak duration (§3)**, **comparison (§4)**, the **annual temperature summaries (§5)**, and **runtime (§6)**, as in the batch database, with their `_flag` columns |
| `hours` | 8760 | `hour`, `month`, `day`, `hour_of_day` |
| `hourly_fuel` | 4 × 8760 per case | `case_key`, `fuel` (enum: Electricity, NaturalGas, DistrictHeatingWater, DistrictCooling), `hour`, `value_w` (double): EnergyPlus's four facility meters, stored, never derived from the end uses (the owner, 2026-10-12) |
| `hourly_end_use` | 6 × 8760 per case | `case_key`, `end_use` (enum: Heating, Cooling, InteriorLights, InteriorEquipment, WaterSystems), `fuel` (enum), `hour`, `value_w` (double): the six end-use meters of the table in [End uses and fuels](#end-uses-and-fuels) |
| `hourly_fuel_long`, `hourly_end_use_long` (views) | | the hourly tables joined with the case identity and `hours`, for analysis without joins |
| `hourly_total` (view) | | the sum of the four fuel meters per case and hour: the total load of §1 as experiment outputs defines it |

- **Merging.** A case is the same case when its `case_id` and its EnergyPlus build are the same (the case ID covers the IDF and the weather file, not the simulation engine). `merge` skips a case the target already holds, renumbers `batch_key` and `case_key`, and maps `reference_case_key` to the target's key; each source file is merged in one transaction, so a failed merge leaves the target as it was.
- **Hourly temperatures, the sensible diagnostics, and the stored total** stay in the batch database only (the owner: by fuel and by end use only). Their annual summaries are in `cases`.
- **One writer.** DuckDB lets one process write a file; a merge target open read-write elsewhere is reported, with exit code 1. Readers should open it `read_only=True`.

**Size per case, measured.** The 110 cases of the 1.3.0 end-to-end run (`%TEMP%\bemgen-simulation-e2e\20261011-055056`, real `eplusout.mtr` files) were loaded into DuckDB 1.5.5 from Python in the layout above, and the file size after a checkpoint divided by 110:

| Layout of the two hourly tables | Per case | 1 000 cases | 10 000 cases |
| --- | --- | --- | --- |
| long, 64-character `case_id` in every row, double | 436 kB | 0.44 GB | 4.4 GB |
| **long, integer `case_key`, enum fuel and end use, double** (planned) | **308 kB** | **0.31 GB** | **3.1 GB** |
| long, integer key, enum, single-precision float | 205 kB | 0.21 GB | 2.1 GB |
| wide (one column per fuel or end use), integer key, double | 267 kB | 0.27 GB | 2.7 GB |
| raw values without compression (10 × 8760 × 8 bytes) | 701 kB | | |

- The keys, enums, and hours cost almost nothing (run-length and bit-packed); the size is the values. Series that are zero all year are stored as constants: in these cases gas equipment and hot water were absent, so 7 of the 10 series had values. A building with all 10 non-zero would take about 308 × 10 / 7 ≈ **440 kB**. So **0.3 to 0.45 MB per case** is the estimate; a `cases` row adds about 2 kB.
- Single precision would save a third but keeps about 7 significant digits, which breaks the exact closure of the end uses and fuels; double is planned.
- The fuel table repeats information (each fuel is the sum of its end uses), but it is stored: EnergyPlus's own facility meter is the reference value, and the owner ruled out a view over the end uses (2026-10-12).
- The build repeats this measurement on the tool's own output and records it in the README.

## Where the code goes

Library code that a later Grasshopper component would also need goes into `Lod.Simulation` (`netstandard2.0`, BCL only, no console, test-first in `Lod.Simulation.Tests`); the database and the console stay in the tool.

| Part | Project | Contents |
| --- | --- | --- |
| A. End uses and fuels | `Lod.Simulation` | `ResearchMeters.EndUses` (end use, fuel, meter) and `ResearchMeters.Fuels` (fuel, meter), the table above; `EndUseClosure.Check(result)`: the largest hourly residual per fuel and of the total, and whether each is within `LoadEquals`. The end-to-end tests switch to it. |
| A2. Timestamps | `Lod.Simulation` | `EsoReader` keeps the month, day, and hour of each hourly code-2 timestamp of the run period (today it only counts them); `SimulationResult.Hours` exposes the 8760 of the meter file. |
| B. Batch plan | `Lod.Simulation` | `ReferenceCase.Zoning` (the constant); `BatchPlan.Create(cases)` over (name, `CaseRecord`, weather resolution) → the groups, each case's reference, the two phases, and the not-run reasons above. Pure and deterministic. |
| C. Batch inputs | `Lod.Simulation` | the expansion of files and folders and the unique run folder names, now private to `eplus-check`; `eplus-check` switches to them, with no change in its behaviour. |
| D. The tool | `scripts/IdfBatchRunner` | options; weather resolution; the plan; the two phases of parallel runs (`EnergyPlusRunner`, `RunVerdict`, `SimulationResultReader`); `ExperimentMetrics` and `EndUseClosure`; the run folder and `batch.json`; the batch database writer (schema, appenders, the view) and the case files (`bemgen-run.json`, `bemgen-hourly.csv`, `bemgen-summary.csv`); `--resume`, `--plan-only`. |
| B2. Zoning line | `Lod.Simulation` | `CaseZoning.Parse(zoning)` → simplifier, aggregator, IWHT, FHT, for the central `cases` columns; a line it cannot split is kept whole and the parts are `NULL`. |
| E. Tool tests | `tests/IdfBatchRunner.Tests` (`net8.0`, in the solution) | see below |
| F. The central database | `scripts/IdfBatchRunner` | the central schema and its version check, the selection of the cases to add, written a case at a time during the run; the `merge` command: duplicate skipping, key renumbering, one transaction per source. |

Parts A to C come first and are independent; D, F, and E follow. `Lod.Simulation` gains no dependency, and `SimulationResult` changes only by the added `Hours`, so the existing tests and metrics are unaffected.

## Tests first

- **A:** the catalogue covers `ResearchMeters.All` except the diagnostics, every end use has one fuel, the fuels sum to `Total`; closure passes on the synthetic year and fails, naming the fuel and the hour, when one end use is perturbed beyond `LoadEquals`.
- **A2:** the timestamps of a fixture year (1 January hour 1 to 31 December hour 24); a timestep-frequency timestamp is not an hour; a design-day environment contributes none.
- **B:** one group with a reference and two variants; two groups (two buildings; one building with two envelopes; one building with two weather files); a group without a reference (not run); an incomplete record; a weather mismatch; a duplicate case; an ambiguous reference; phase 2 dropping the variants of a failed reference; the same plan for any input order. The reference constant equals `IdfCaseRecord`'s line for *No Simplification*, *Stack*, both options on.
- **C:** the current `eplus-check` behaviour, now as unit tests: folders expand to sorted `*.idf`, duplicates removed ignoring case, repeated names get `-2`, `-3`.
- **E, always** (fake process runner writing the synthetic year of `Lod.Simulation.Tests`, its support files linked, not copied): options and usage errors; weather resolution from a file and from a folder; a batch of a reference, two variants, and an orphan, read back through DuckDB.NET: the tables and the view exist, `hourly` has 17 × 8760 rows per completed case and none for the orphan, the orphan's status is `NoReferenceCase`, each series' sum equals its annual column, the flag columns hold the flags; the reference's comparison metrics are 0; the run folder layout and the case files; `--resume` reruns only the unfinished cases and rebuilds the same databases; `--plan-only` writes nothing; `--root` from the environment variable, and refused inside the repository; exit codes.
- **B2:** the zoning lines of the export snapshots, a line with two simplifiers, a line it cannot split.
- **F, always:** a run's central database: only its completed cases, 4 × 8760 and 6 × 8760 rows each, `hourly_total` equal to the batch's `Total`, the fuel rows equal to the facility meters, the reference key set; `merge` of two runs accumulates; the same run merged twice adds nothing; the same case under another EnergyPlus build is a separate case; a failed merge (an injected fault) leaves the target as it was; a central file of another schema version is refused.
- **E, opt-in** (`[EnergyPlusFact]`, `BEMGEN_ENERGYPLUS`): the linear plan under the reference and two variants, plus one orphan, with the Chicago file: three runs, the orphan not run, closure passed, the hourly sums equal to the annual columns, and the three cases in a central database. The build log also records a manual read of both databases from Python `duckdb` 1.5.5.

Plain `dotnet test` needs no EnergyPlus (GLOBAL.md architecture rule 7). The DuckDB native library is in the package, so the tests need no install beyond the restore.

## Documentation

- `docs/research/experiment-outputs.md`, "Where the work happens": running batches and storing their results in a database is now in the repository (the tool); analysis stays outside (D-016 as refined by D-132). Research definitions do not change.
- `docs/architecture/energyplus-runner.md`: the new library types (A to C) and a section on the tool.
- `scripts/IdfBatchRunner/README.md`: usage, the not-run reasons, the output folder, both schemas, the measured size per case, how to open the databases from Python, R, and the DuckDB command line.
- `AGENTS.md` (Commands; the test projects; the architecture table gains the tool), the roadmap's progress log.
- `docs/decisions/decision-log.md`: **D-132**, the batch runner in the repository with a DuckDB batch database and a central DuckDB database across batches (refines D-016 and the last line of experiment outputs, "Where the work happens"; keeps the Grasshopper run component deferred; no release). No ADR: no research rule, pipeline type, or component changes.
- The `sync-docs` skill at close-out; since there is no release, it records that the public site does not follow yet.

## Settled with the owner (2026-10-12)

1. `scripts/eplus-check/` keeps its name.
2. The results root comes from `--root`, else `BEMGEN_RESULTS_ROOT`; each run has its own folder with its own `central.duckdb`; `merge` combines runs.
3. The fuel table is stored, never a view over the end uses.
4. `--resume <run folder>` continues an interrupted run.
5. The build commits on the branch and stops at the stop line: no merge, no push.

## Build log (2026-10-12)

Built on `feature/idf-batch-runner` from `main` `9dcc5d5`, test-first, in the order of [Where the code goes](#where-the-code-goes).

**What differs from the note, and why:**

- **Batch database keys.** `hourly` is keyed by the integer `case_key` (as the central database is), not by the 64-character `case_id`; `cases` carries both. The measured layouts showed the key costs about 40 % of the hourly size when it is the long string.
- **No `summary.csv` at the run folder's root.** The owner put the discardable artefacts in each case folder (`bemgen-summary.csv`, `bemgen-hourly.csv`), and the run's `cases` table is in `results.duckdb`.
- **`merge` replaces `import`.** Each run writes its own central database, so the tool needs no `--central` or `import`; `merge` combines the central files of runs (the owner's layout of 2026-10-12).
- **Not-run order.** A record that lacks a line or records no weather file is `IncompleteCaseRecord` even when no weather file was found, because the record is the cause. A weather folder cannot hold the file of an IDF written without one.
- **`CaseRecord.RecordedWeatherFileName`** was added to `Lod.Simulation`, so that a weather folder can be searched before the full record, which needs the weather bytes, is read.
- **Writes in name order.** Cases are written to both databases and their folders in name order within each phase, as `eplus-check` prints its lines, so two runs of the same inputs write the same files whichever EnergyPlus process finishes first.
- **DuckDB.NET appends.** DuckDB.NET 1.5.5 writes the wrong bytes when a plain `int` is passed to `AppendValue` (it resolves to another overload), so every numeric value goes through a typed nullable overload (`Duck.Append`).
- **Merge statement order.** Each merge statement re-reads the key map, so the hourly rows are inserted before the case rows, which mark a case as present.

**Checks:**

- `scripts/verify.ps1`: 629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, 176 simulation, and 41 batch-runner tests; the 6 opt-in EnergyPlus tests skipped; 0 warnings.
- The opt-in test (`BEMGEN_ENERGYPLUS=D:\EnergyPlusV26-2-0`, EnergyPlus 26.2.0 build `4bd7a1f26f`) passed. The linear plan's reference and two variants ran, completed, passed their verdicts, and closed, and the orphan was not run.
- The tool on the 110 IDFs of the 1.3.0 end-to-end set (`%TEMP%\bemgen-simulation-e2e\20261011-055056`, the Chicago TMY3 file, 14 runs at a time):
  - 4 groups with a reference; 80 cases ran, completed, passed, and closed;
  - 30 were not run, all `NoReferenceCase`: the 28 Medium Office cases were written with the default heat-transfer options, so none is the reference, and the two overhanging stair-bay-bar cases are *Conditioned Merge* only.
- **Size** of that run: `central.duckdb` 28.8 MB for 80 cases, **361 kB per case**, against 308 kB estimated from the bare hourly tables; the rest is the cases table and file blocks. `results.duckdb` came to 101 MB, 1.27 MB per case. A case folder held about 29 MB, most of it `eplusout.sql` and `eplusout.eso`, with 7 MB of `bemgen-hourly.csv`.
- Python `duckdb` 1.5.5 opened both databases read-only, and the views and the enum columns read as expected.
- **The review by a second agent** found eleven points. Each was fixed or recorded here, with tests where behaviour changed:
  1. A case read again on `--resume` took the resumption's concurrency, which made a run of 8 at a time look comparable. `bemgen-run.json` now records the concurrency, and a case read again keeps it.
  2. `--resume` depended on the current folder. The installation, weather, inputs, and root are now stored as full paths.
  3. A file-system error inside a case stopped the whole batch. It now makes that case `RunFailed`. A file-system or DuckDB error while writing stops the run with exit code 1 and a `batch.json` with no finish time, ready for `--resume`.
  4. `CaseNames` could give two files the same name (`a`, `a`, `a-2`), which crashed the plan. Taken names are now skipped (`a`, `a-2`, `a-2-2`). `eplus-check` had the same fault, so two of its cases could share a folder.
  5. A failed merge into a new target left an empty file. It is now deleted.
  6. The merge inserted rows by position. It now inserts `BY NAME`.
  7. The merge could add a batch row with no new case. It now adds a batch only with a new case.
  8. `WeatherMismatch` covers another file name as well as another SHA-256, because that is what `CaseRecord` checks (D-130). The note and the README now say so. Accepting a renamed weather file would be the owner's call.
  9. Two small behaviour changes are now documented in [energyplus-runner.md](../architecture/energyplus-runner.md):
     - a run-period timestamp whose month, day, or hour does not parse is a format error;
     - `BatchInputs.Expand` keeps only `.idf` files, where Windows' `*.idf` pattern also matched `*.idfx`.
  10. New tests: a case of another run period, a reference of another run period stopping its variants, a file-system error in one case, the concurrency on resume, full paths, a failed merge into a new target, and a run whose cases are all present.
  11. On `--resume`, the folder of a case that no longer runs is deleted, so that its old `bemgen-summary.csv` cannot contradict its status.

**Open:**

- The Medium Office end-to-end set has no reference under the default heat-transfer options. To compare its variants, write its reference with both options on.
- The runner's temperatures over conditioned zones have no rows when a building has none; the flag is in `cases`.
