# EnergyPlus runner

> **Status:** Provisional (ADR-019 and D-130, written by the stage's controller; realisation pending the owner's reading) · **Since:** version 1.3.0 · **Code:** `Lod.Simulation` (`src/Lod.Simulation/`), tests `tests/Lod.Simulation.Tests/`, tool `scripts/eplus-check/` · **Design note:** [2026-10-11-idf-out.md](../plans/2026-10-11-idf-out.md), Part E · **Definitions:** [Experiment outputs](../research/experiment-outputs.md)

## Purpose

`Lod.Simulation` runs an installed EnergyPlus on a written IDF and a weather file, reads what the run reports, and computes the experiment metrics. A run is not a pipeline step (D-130): it takes files, never an `IGeneratedBuilding`, and changes no pipeline object. The pipeline still ends at the converters.

- The library is `netstandard2.0`, so that the deferred Grasshopper run component can use it. It depends on `Lod.Core` only (`Result`, `Diagnostic`, `DiagnosticCodes`) and never on RhinoCommon, Grasshopper, or `Lod.Export`.
- It reads EnergyPlus's text files with the base class library only: no SQLite library and no native code.
- It never writes to the console (GLOBAL.md quality rule 7) and never writes outside the run's output folder.
- Plain `dotnet test` needs no EnergyPlus. Tests that run EnergyPlus are opt-in (see [Tests](#tests)).

## Interface

| Type | Role |
| --- | --- |
| `EnergyPlusInstallation.Locate(folder)` | Checks that the folder holds `energyplus.exe` and `Energy+.idd`, and reads the version from the IDD's first line (`!IDD_Version 26.2.0`) and the build from its second (`!IDD_BUILD 4bd7a1f26f`). No process is started. |
| `EnergyPlusRunRequest(IdfPath, WeatherPath, OutputFolder, Timeout)` | One run. The output folder must be missing or empty; the timeout positive. |
| `IProcessRunner`, `SystemProcessRunner` | Runs a process to its end, its timeout, or cancellation (`CancellationToken`), and stops it in the last two cases. Injected into the runner, so that tests use a fake (AGENTS.md, dependency injection). The default starts the program without a shell or window and discards its console output. |
| `EnergyPlusRunner(installationFolder, processes).Run(request, token)` | Runs `energyplus.exe -w <epw> -d <output folder> <idf>` with full paths and the output folder as working folder, and returns `Result<EnergyPlusRun>`: the request, the installation, the exit code, the wall-clock time, the parsed `eplusout.err`, and the IDF's `Version`. `Completed` is exit code 0 and "EnergyPlus Completed Successfully". |
| `SimulationResultReader.Read(run, conditions)` | Reads the raw outputs of a completed run into a `SimulationResult`. The caller gives the `RunConditions` (processor, logical cores, concurrency; `RunConditions.Detect(concurrency)` reads this machine). |
| `CaseRecord.Read(idf, weather)`, `CaseRecord.Create(bytes, bytes, name)` | The case record of experiment outputs §7 from the IDF header, and the case ID. |
| `ExperimentMetrics` | The metrics of experiment outputs §2 to §5 as pure functions. |
| `ExpectedWarnings`, `RunVerdict.Of(run, expected)` | The warnings a BEMGen IDF may give, each with a pattern and a reason, and the verdict on a run: it passes when it completed with no fatal, no severe, and only expected warnings. |

A run that did not complete is still a successful `Result`, with the warning `EnergyPlusRunFailed`, so that its error report can be read; `SimulationResultReader.Read` then refuses it with the error `EnergyPlusRunFailed`.

## Parsers

| Parser | File | What it reads |
| --- | --- | --- |
| `EnergyPlusErrorReport.Parse` | `eplusout.err` | Each `** Warning **`, `** Severe  **`, and `**  Fatal  **` with its continuation lines (`**   ~~~   **`) and its line number; the entries of the recurring error summary, marked `IsRecurringSummary`; the summary counts and `Completed` from the last line; the elapsed time (`Elapsed Time=00hr 00min  9.95sec`); the version and build from the first line. Any text parses. |
| `EsoReader.Parse`, `EsoReader.Read` | `eplusout.eso`, `eplusout.mtr` | The data dictionary to `End of Data Dictionary`: report codes 1 to 6 are the environment and timestamp layouts; every other line is `code,count,[key,]name [units] !frequency`, and only `!Hourly` lines with one value are kept (a meter has no key). Then the records: a code-1 line opens an environment, a code-2 line is an hourly timestamp, and other codes are values. Only the run-period environment counts: an environment whose timestamps carry a design-day type (`SummerDesignDay`, `WinterDesignDay`) is a sizing period and is skipped, and warm-up days are never reported. No run period, or more than one, is an error. Keys and names are compared ignoring case, as EnergyPlus upper-cases keys. Hours are counted on the code-2 timestamps that span the whole hour (start minute 0, end minute 60), so the timestamps a timestep-frequency variable adds do not count as hours. |
| `EnergyPlusZoneReport.Parse` | `eplusout.eio` | The `Zone Information` lines, with the columns located by the names of the `! <Zone Information>` header line: name, zone multiplier, zone list multiplier (the effective multiplier is their product), floor area, volume, and whether the zone is part of the total floor area. The file prints areas and volumes with two decimals. |
| `TabularReport.ParseBuildingArea` | `eplustbl.csv` | The *Building Area* table of the *Annual Building Utility Performance Summary*: *Total Building Area* and *Net Conditioned Building Area*. |

A malformed file is the error `EnergyPlusOutputFormat`, whose message names the file and the line.

## The simulation result

`SimulationResult` holds the raw outputs of experiment outputs §8:

| Member | Source | Notes |
| --- | --- | --- |
| `Heating`, `Cooling` | `eplusout.mtr`: `Heating:DistrictHeatingWater`, `Cooling:DistrictCooling` | `HourlySeries`: 8760 hourly loads in W (the meter's J / 3600); `AnnualKilowattHours` is Σ W × 1 h / 1000. |
| `Total` | the sum of `Electricity:Facility`, `NaturalGas:Facility`, `DistrictHeatingWater:Facility`, `DistrictCooling:Facility` | hour by hour |
| `Meters` | every meter of experiment outputs §1 (`ResearchMeters.All`) | A meter that is not written is zero every hour; `MetersWritten` lists those that are. A meter not in J is an error. |
| `Zones` | `eplusout.eio` and `eplusout.eso` (`Zone Mean Air Temperature`) | name, multiplier, floor area, volume, conditioned, and 8760 temperatures in °C. A zone is conditioned when the IDF has a `ZoneControl:Thermostat` for it (a zone list is expanded); names are compared ignoring case. A zone without a temperature series is an error. |
| `FloorArea` | `eplustbl.csv` | total and net conditioned |
| `Runtime` | `eplusout.err` and the runner | the EnergyPlus elapsed time, the wall-clock time, the EnergyPlus version and build, and the `RunConditions`. `Comparable` is true only for a concurrency of 1 (experiment outputs §6). |
| `Case` | the IDF header and the two files' bytes | the case record |
| `ErrorReport` | `eplusout.err` | |

Every series has exactly 8760 values; a file whose run period has another number of hours, or a series of another length, is the error `HourlySeriesLength`. A missing file is the error `EnergyPlusOutputMissing`.

### Case record

*Convert2IDF* writes the identifying lines into the IDF header, and `CaseRecord` reads them back. The header is the comment lines before the first IDF object, and the prefixes are exact:

```text
! BEMGen Convert2IDF, code version <version>
! Case building: <typology, typed parameters, seed>
! Case zoning: <simplifier and options, aggregator, heat-transfer options>
! Case weather: <file> sha256 <hex>        (or: ! Case weather: none)
! Case envelope: <envelope preset name>
```

- **Case ID**: the SHA-256, in lower-case hexadecimal, of the IDF file's bytes followed directly by the weather file's bytes, as they are on disk. Any change to either file gives another ID; the same two files always give the same ID.
- `CodeVersion` comes from the header's first line, which *Convert2IDF* always writes.
- A missing line, the code version included, is the warning `CaseRecordIncomplete`, which names the lines.
- A weather file whose name (ignoring case) or SHA-256 differs from the header's is the warning `CaseWeatherMismatch`. `none` means the IDF was written without a weather file and is not a mismatch.

## Metrics

`ExperimentMetrics` implements experiment outputs §2 to §5 as pure functions over series of any length (a `SimulationResult` gives 8760), and `Compute(variant, reference)` gathers them into `CaseMetrics` for heating, cooling, and total.

| Function | Experiment outputs | Definition |
| --- | --- | --- |
| `Annual` | §2 | annual sum, kWh; EUI per conditioned and per total floor area, kWh/m² |
| `Percentile` | §3 | Hyndman and Fan type 7: position (n − 1)·p on the sorted values, interpolated linearly; checked against NumPy's `np.quantile` |
| `Peaks` | §3 | maximum, P99, P95, P90 of all hours, zero hours included, each in W and per both floor areas |
| `Thresholds`, `HoursAbove` | §3 | the reference case's P99, P95, P90 of the total load, and the hours of a case strictly above each; the thresholds are kept with the counts |
| `CvRmse` | §4 | √(Σ (yᵢ − rᵢ)² / n) / r̄, a fraction, denominator n |
| `QuantileNrmse` | §4 | √(Σₚ (Qᵧ(p) − Qᵣ(p))² / 101) / r̄ over `QuantileGrid`, p = k / 100 for k = 0 … 100 |
| `KolmogorovSmirnov` | §4 | maxₓ \|Fᵧ(x) − Fᵣ(x)\| at every value of either series, ties allowed |
| `Temperature` | §5 | area-weighted mean and population standard deviation per hour, w = floor area × multiplier, over all zones and over conditioned zones |

A metric without a value is a `MetricValue` with `Value` null and a `MetricFlag`, never 0 or infinity:

| Flag | When |
| --- | --- |
| `ZeroReferenceMean` | r̄ = 0 for CV(RMSE) or the quantile NRMSE (for example no cooling in a cold climate) |
| `NoConditionedZone` | the temperature over conditioned zones of a building without one |
| `ZeroFloorArea` | an EUI or a normalised peak over a zero floor area (a building without conditioned floor area), or temperature weights that sum to zero |

Two all-zero series have a Kolmogorov–Smirnov D of 0, and a reference against itself has zero comparison metrics. Series of different lengths, empty series, values that are not finite, and a probability outside [0, 1] are programming errors and throw.

## Diagnostics

All codes are in `DiagnosticCodes` (`Lod.Core`):

| Code | Severity | When |
| --- | --- | --- |
| `EnergyPlusNotFound` | error | the folder, `energyplus.exe`, or `Energy+.idd` is missing, or the IDD's first line names no version |
| `SimulationInputMissing` | error | the IDF or weather file does not exist |
| `OutputFolderNotEmpty` | error | the output folder exists and is not empty; nothing runs |
| `InvalidParameter` | error | the timeout is not positive |
| `EnergyPlusTimeout` | error | EnergyPlus ran past the timeout and was stopped |
| `EnergyPlusCancelled` | error | the caller cancelled, before or during the run |
| `EnergyPlusStartFailed` | error | the process could not start |
| `EnergyPlusOutputMissing` | error | `eplusout.err` after a run, or a file or zone series the result needs, is missing |
| `EnergyPlusVersionMismatch` | warning | the IDF's `Version` differs from the installation's major and minor version, or the IDF has none |
| `EnergyPlusRunFailed` | warning on a run, error on reading its result | a non-zero exit code, or no successful completion in `eplusout.err` |
| `EnergyPlusOutputFormat` | error | a file has an unexpected layout, or a meter is not in J |
| `HourlySeriesLength` | error | a run period or series is not 8760 hours long |
| `CaseRecordIncomplete` | warning | the IDF header lacks a case record line |
| `CaseWeatherMismatch` | warning | the weather file is not the one the header records |

## The check tool

`scripts/eplus-check/` runs EnergyPlus on many IDFs in parallel and judges each run with `RunVerdict` against `ExpectedWarnings`.

A warning that EnergyPlus prints only in its recurring error summary is checked like any other; a summary entry that repeats a warning printed earlier is checked once (review of the stage, 2026-10-11).

`SystemProcessRunner` stops only the process it started when a timeout passes or the caller cancels, not its child processes, because netstandard2.0 cannot stop a process tree. `EnergyPlusRunner` passes neither `-x` nor `-r`, so EnergyPlus starts no helper program. Its usage, the expected warnings with their reasons, and how to read its summary are in its `scripts/eplus-check/README.md`.

## Tests

`tests/Lod.Simulation.Tests` (`net8.0`, run by `scripts/verify.ps1`):

- **Always:** the parsers on short fixture texts written for the tests in EnergyPlus's layouts; the installation check on a temporary folder; the runner with a fake `IProcessRunner` (arguments, timeout, cancellation, missing installation, IDF, or weather file, a failed run, a non-empty output folder, the version warning); the default process runner on Windows' own `cmd.exe` and `PING.EXE`; the result reader on a scripted run that writes a synthetic year of outputs; the case record; the verdict; and the metrics on small series worked by hand, the percentiles and the quantile NRMSE also against NumPy 2.5.3 values written into the tests as literals, with every zero guard.
- **Opt-in:** `[EnergyPlusFact]` and `[EnergyPlusTheory]` are `xunit` attributes that set `Skip` unless the environment variable `BEMGEN_ENERGYPLUS` names a valid installation folder. The end-to-end set (`tests/Lod.Simulation.Tests/EndToEnd/`) generates buildings as the export tests do, converts each case with `Convert2Idf` and the installation's own `WeatherData/USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw` (so every IDF has `Site:Location` and the case record), and runs it into a folder outside the repository: `BEMGEN_SIM_OUT` when set, otherwise a new folder under `%TEMP%\bemgen-simulation-e2e\<date-time>`. A folder inside the repository is refused. At most half the logical cores run EnergyPlus at a time across all tests, and a case is run once per test run and shared by the tests that use it. Each test gathers the problems of every case and reports them together.
  - **Every run:** it completed with no severe or fatal error and only the warnings of `ExpectedWarnings.Default`, judged by `RunVerdict` (a version mismatch is not expected), and the runner and the reader give no warning; the zones of the `.eio` equal the building's in name, multiplier, floor area, volume, and thermostat (conditioned); `SimulationResultReader` gives a complete result with 8760 hours in every series; the end uses (lighting, electric and gas equipment, hot water, heating, cooling) sum to the total load every hour within `ToleranceSettings.LoadEquals`; the *Building Area* table's total and conditioned floor area equal the building's Σ floor area × multiplier over all zones and over conditioned zones; the case record names the Chicago file with its SHA-256 and the envelope. The `.eio` and the table print two decimals, so the building's values are rounded to two decimals before the comparison with `ToleranceSettings.AreaEquals`.
  - **Across the configurations of one building:** one building line, a different zoning line per configuration, and the hourly internal-load meters (`InteriorLights:Electricity`, `InteriorEquipment:Electricity`, `InteriorEquipment:NaturalGas`, `WaterSystems:DistrictHeatingWater`) equal to the reference's every hour within `LoadEquals` (GLOBAL.md scientific rule 1 through EnergyPlus).
  - **Cases:** the canonical linear plan through every simplifier and floor aggregator with both heat-transfer settings (56 cases); the floor-aggregator set below (24 more cases, the linear plan's 8 being shared); the overhanging stair-bay bar (*Conditioned Merge* with *Join Pieces*, the upper storey moved by (5.3, −2.1) m, both settings); and the Medium Office program JSON on the office plate through every simplifier and aggregator (28 cases, the default heat-transfer options, internal loads compared with *No Simplification*, *Stack*). 110 cases in all.
  - **The floor-aggregator set** (the owner): the canonical linear plan (1, 2, 1), the office plate (1, 3, 1), the enclosed court (1, 3, 1), and the stepped band's three storeys, each under *No Simplification* through each floor aggregator with both settings, against the reference (*No Simplification*, *Stack*, both options on). Beyond the checks above it asserts that Σ floor area × multiplier and Σ volume × multiplier equal the reference's (the `.eio` being tied to the building zone by zone), that EnergyPlus's *Total Building Area* equals the reference's, and that the IDF has shading surfaces exactly when the building has unmodelled storeys under *Stacked Floor Zone Multiplier* (`StackedFloorZoneMultiplier.UnmodelledStoreys`) and none under the other aggregators. It asserts no bound on heating or cooling differences, which are research results. It writes `reports/floor-aggregators-<plan>.csv` (every metric of experiment outputs §2 to §5 from `ExperimentMetrics.Compute`, each case against the reference; the hourly temperatures summarised as their annual means) and a text table of the key numbers beside it, and prints the table's path in the test output.
  - **Last run** (2026-10-11, EnergyPlus 26.2.0 build `4bd7a1f26f`, 28 logical cores, 14 runs at a time): the 110 cases passed every check; the test project passed 139 of 139 tests in 103 s of wall time.

```powershell
$env:BEMGEN_ENERGYPLUS = "D:\EnergyPlusV26-2-0"
dotnet test tests/Lod.Simulation.Tests -c Release
Remove-Item Env:BEMGEN_ENERGYPLUS
```
