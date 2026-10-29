# Paired evaluation metrics: sensible loads, peaks, hourly fit, temperature, and computation (design note)

> **Status:** Done: built, reviewed, and verified on `feature/evaluation-metrics` (D-156, D-157), merged into `main` (D-158), pushed (D-159), released in `v1.5.0` (D-175) · **Date:** 2026-10-26 · **Decisions:** D-016, D-112, D-130, D-132, D-153; new: D-156, D-157, D-158 · **Requested by:** the owner, 2026-10-26 ("update the IDF simulation evaluation pipeline to compute and export …") · **Refines:** [experiment outputs](../research/experiment-outputs.md), which gains §10

One stage, run as D-111 sets out: this note; one test-first build; a review of the diff by a second agent; `scripts/verify.ps1`; a decision-log entry. It changes `Lod.Simulation` (a second metric set, the ideal-loads sensible series, processor time and process memory), `Lod.Core` (one tolerance), `scripts/IdfBatchRunner` (central schema version 7, a metric definitions table, two more hourly series, a serial timing pass), and the research documentation. It changes no pipeline type, no Grasshopper component, no IDF the writer produces, and none of the existing metrics.

**Stop line.** The build ends with the branch verified, reviewed, and documented. It does not merge, tag, push, or release.

## The owner's decisions (2026-10-26, D-157)

After the first build (D-156) the owner read the open choices:

| Choice | Decision |
| --- | --- |
| Near-zero threshold, 0.01 W/m² of the reference's total floor area | kept |
| Zone sensible variables as the ideal sensible load | kept |
| Top intervals as the first ⌈k · n / 100⌉ ranks, rank by rank | kept |
| Working set as the memory measure | kept, with the committed memory beside it (below) |
| The pairing check keeps a failing site's metrics | kept |
| NMBE's sign | **ASHRAE Guideline 14's, reference minus site**; the temperature MBE follows, as the same kind of bias error |
| P90 | **added** beside P95 and P99, for the peaks and the exceedance, as §3 has it |
| Temperature over common unconditioned hours | **removed** from the code and this plan, never to be completed: no program is off by the hour (a zone is conditioned all year or not at all, and *Convert2IDF* writes no availability schedule), and setbacks are conditioning. The availability reading, its flags, its columns, and its hourly series are gone |
| Runtime and memory of parallel runs | **concurrency-robust measures in every run** (processor time and peak committed memory) **and an optional serial timing pass** |

## What exists and what is missing

The metrics of experiment outputs §2 to §5 and §9 stay as they are. They are computed on the *total* heating and cooling meters (sensible plus latent) and on the total load. The request asks for a set on the **ideal sensible** heating and cooling loads, aggregated from the zones, with more comparison statistics.

| Request | Before | This stage |
| --- | --- | --- |
| Annual sensible heating, cooling (kWh), per floor area, relative error | total heating, cooling meters only; no relative error | new, on the sensible series |
| Peak, P95, P99 (kW), relative errors | max, P99, P95, P90 in W on the total meters; no errors | new, on the sensible series, in kW, with P90 (D-157) |
| Exceedance hours with reference thresholds | total load only, against its P99, P95, P90 | new, per sensible load, against the reference's P99, P95, and P90 |
| CV(RMSE), NMBE | CV(RMSE) as a fraction; no NMBE | both, in %, on the sensible series |
| LDC NRMSE over full and top 1, 5, 10 % | one quantile NRMSE on a 101-point grid | new, rank-wise, four intervals |
| KS | on total meters | also on the sensible series |
| Conditioned-area-weighted temperature | the series exists (`TemperatureMean:ConditionedZones`) | MBE and RMSE against the reference over all hours |
| Runtime, zone count | both | processor time, and ratios against the reference |
| Average and peak process memory | not measured | sampled by the process runner, with the committed memory, with ratios |

## Definitions (experiment outputs §10)

Notation: y is the site's hourly series, r its reference's, n = 8760, A the reference's total floor area (the total floor area is conserved by every zoning configuration, GLOBAL.md scientific rule 1).

1. **Sensible loads.** H(t) = Σ_z Q^sens,heat_z(t) / 3600 s and C(t) = Σ_z Q^sens,cool_z(t) / 3600 s, in W, over every zone with a `ZoneHVAC:IdealLoadsAirSystem`, where Q is EnergyPlus's hourly `Zone Ideal Loads Zone Sensible Heating Energy` or `… Cooling Energy` of the zone's system, keyed by the system's name.
   - Heating and cooling are separate output variables of each zone, each non-negative, so they are summed separately at each hour and never netted. Latent loads, hot water, lights, equipment, and fans are not in them.
   - The zone multiplier is already in Q (see "The multiplier" below), so Q is summed as reported.
2. **Annual.** E = Σ y / 1000 (kWh); per conditioned and per total floor area (kWh/m²); relative error 100 · (E − E_ref) / E_ref (%).
3. **Peaks.** Maximum, P99, P95, P90 (type 7, §3), in kW; relative errors as above.
4. **Exceedance.** Thresholds θ99, θ95, and θ90 are the reference's P99, P95, and P90 of the same load; the site's hours with y > θ, the reference's own count at the same thresholds, and their difference (h). The thresholds are stored with the counts.
5. **Hourly fit.** CV(RMSE) = 100 · √(Σ (y − r)² / n) / r̄; NMBE = 100 · Σ (r − y) / (n · r̄), ASHRAE Guideline 14's sign with the reference as the measured data: positive when the site's load is below the reference's (D-157). Both with n in the denominator, no parameter count.
6. **Load-duration-curve NRMSE.** Each series sorted from largest to smallest, y₍₁₎ ≥ … ≥ y₍ₙ₎ and r₍₁₎ ≥ … ≥ r₍ₙ₎. For an interval I of ranks, NRMSE_I = 100 · √(Σ_{i∈I} (y₍ᵢ₎ − r₍ᵢ₎)² / |I|) / mean_{i∈I} r₍ᵢ₎. The intervals: all n ranks, and the top 1 %, 5 %, 10 %: the first ⌈k · n / 100⌉ ranks (88, 438, 876 hours). The normaliser is the reference's mean within the interval. The 101-point quantile NRMSE of §4 is kept.
7. **KS.** The two-sample statistic of §4, on the sensible series.
8. **Temperature.** T(t), the conditioned-floor-area-weighted mean zone air temperature of §5 (over zones with a thermostat, weights floor area × multiplier). MBE = Σ (T_ref − T) / n and RMSE = √(Σ (T_ref − T)² / n), °C, over all hours, MBE with Guideline 14's sign (D-157).
9. **No temperature over unconditioned hours** (D-157). The first build (D-156) defined common unconditioned hours from the ideal loads' availability schedules; every *Convert2IDF* IDF leaves them blank, so the set was always empty. The owner removed it.
10. **Computation.** Wall-clock runtime (s), EnergyPlus's own elapsed time, and the process's **processor time** (user and kernel, read when it exits); zone count (zones in `eplusout.eio`) and represented zone count (Σ multipliers); process memory (below); and the ratios site / reference of each.
11. **Process memory.** The process runner samples the EnergyPlus process at each poll of its wait loop (every 50 ms): the average working set is the mean of the samples; the peak working set and the **peak committed private memory** (`PeakPagedMemorySize64`) are the largest peaks the operating system reported at a sample, which include growth between samples but not after the last one. In MiB. A run shorter than one poll has no memory values (`NotMeasured`).
12. **Runtime and memory of parallel runs** (D-157). See "Measuring cost in parallel batches" below.

### Zero and near-zero denominators

A metric whose normaliser is the reference's load is missing with the flag `NearZeroReference` when the reference's power intensity is at or below ε = `ToleranceSettings.NegligibleLoadIntensity`, 0.01 W/m² of A by default (0.0876 kWh/m² a year). The intensity is the normaliser's own: for an annual error, E_ref / (n · 1 h · A); for a peak error, the reference's peak / A; for CV(RMSE), NMBE, and the full LDC NRMSE, r̄ / A; for a top interval, its mean / A; for exceedance, θ / A. A count of hours above a threshold at or below ε would count hours with any load, so it is missing too. Missing values are never stored as 0, ±∞, or NaN. A ratio over a zero or unmeasured reference value is missing with `NotMeasured`. The value is a tolerance of the central configuration (GLOBAL.md quality rule 4), recorded with every run.

## The multiplier (found in the build)

The first draft of this note multiplied Q by the zone multiplier, as §9 does for surface variables, and checked H and C against `Heating:EnergyTransfer` and `Cooling:EnergyTransfer`. The opt-in EnergyPlus 26.2 runs (Chicago O'Hare TMY3, 2026-10-26) refuted both:

| Building and configuration | Σ_z Q^sens,heat vs `Heating:DistrictHeatingWater` | Σ_z Q^total,cool vs `Cooling:DistrictCooling` | Σ_z Q^sens,cool vs `Cooling:EnergyTransfer` |
| --- | --- | --- | --- |
| linear plan, *No Simplification*, *Stack* (multipliers 1) | equal every hour (relative 6 × 10⁻¹⁶) | equal (2 × 10⁻¹²) | up to 0.8 % in an hour |
| linear plan, *Conditioned Merge*, *Stacked Floor Zone Multiplier* | equal (4 × 10⁻¹⁶) | equal (3 × 10⁻¹²) | up to 0.25 % |
| medium office, *Conditioned Merge* (joined), *Stacked Floor Zone Multiplier* (1, 3, 1) | 57 hours differ, at most 2 × 10⁻⁵ | 27 hours differ | up to 3.3 %; 0.1 % a year |

- With multipliers above 1, the plain sum equals the multiplied meter, and the sum multiplied again was up to 2.8 times the meter. So EnergyPlus reports the ideal-loads variables with the multiplier in, and the reader sums them as reported.
- The `EnergyTransfer` meters are not the zone sensible loads. A first replacement check, H equal to `Heating:DistrictHeatingWater` every hour within `ToleranceSettings.LoadEquals`, failed on the linear plan's full matrix in one hour of each of three *Perimeter Core* configurations (H 1e-6 below the meter, 9 × 10⁻⁵ W of 94 W): heating without humidification is sensible only, but EnergyPlus's supply-air total is very slightly higher in rare hours. The tolerance is not widened; the check is now an inequality, which is what catches a double count: on the linear plan's matrix, H and C are never above `Heating:DistrictHeatingWater` and `Cooling:DistrictCooling` in any hour.

## Measuring cost in parallel batches (D-157)

Energy results do not depend on how many EnergyPlus processes run at once, so batches run in parallel, which an experiment needs. Runtime and memory do depend on it: other processes share the cores, the caches, the memory bandwidth, and the physical memory. So the cost is measured two ways.

- **In every run, concurrency-robust measures.**
  - The **processor time** of the EnergyPlus process (user and kernel). Other processes lengthen a run's wall clock by making it wait for a core; its processor time moves much less (cache and memory-bandwidth contention, the clock's turbo), as long as there are no more runs than physical cores.
  - The **peak committed private memory**: what the process allocated. The working set is what it holds in physical memory, which the operating system trims under pressure from other processes.
  - The site's and the reference's measures come from the same batch, but not from the same moment: references run in the first phase and variants in the second, under other loads, and after `--resume` a reference's measures may come from an earlier session at another concurrency. The processor time still moves a little with shared cores (SMT) and memory bandwidth. So these ratios are robust, not exact, and the timing pass calibrates them. The wall clock, EnergyPlus's elapsed time, and the working set are kept too, and are results only for runs made one at a time (`runtime_comparable`).
- **An optional serial timing pass** (`--timing-repeats N`, and `--timing-test-cases K` to take K test cases): once every site is written, so that no other EnergyPlus runs beside it, the succeeded sites of the timed test cases run again one at a time, N times each.
  - The test cases are taken in the order of the SHA-256 of their IDs: a deterministic spread over the suite rather than its first test cases.
  - Repeats are the outer loop; within a repeat, a test case's reference runs just before its variants, so that a slow drift of the machine (temperature, background work) reaches every site of a test case alike.
  - Each run is a row of `site_timing`; its EnergyPlus folder is discarded, since the energy results are the main run's. `site_timing_summary` gives each site's medians over its completed repeats and their ratios to its reference's medians: the reported runtimes and memory. Comparing them with the same sites' parallel measures calibrates the parallel runs.
  - A resumed run makes only the timing runs its database lacks; merge carries them with their sites.
- **Recommended use.** Run the experiment with `--parallel` at most the number of physical cores, use the processor-time and committed-memory ratios of every site, and time a sample of test cases serially (for example `--timing-repeats 3 --timing-test-cases 20`) to report runtimes and to check how far the parallel measures are off.

## Pairing

A site is compared only with the reference of its test case: the same building line, envelope line, and weather file's SHA-256 (D-132), the same run period hours (D-153), the reference run first. This stage adds a measured check of the non-zoning assumptions: the hourly internal-load end uses (lights, electric and gas equipment, hot water), which BEMGen conserves hour by hour (GLOBAL.md scientific rule 1), are compared with the reference's. The largest absolute difference and whether every hour is within `ToleranceSettings.LoadEquals` of the reference's value are stored (`pair_internal_loads_max_dev_w`, `pair_internal_loads_equal`). A site that fails it keeps its metrics and gets the problem in its status message, so that the analysis can exclude it; a run never silently relaxes the tolerance.

## Storage

- **`central.duckdb`, schema version 7** (6 for D-156's first build, on this branch only, without the timing table or the robust measures; a folder of it is refused by resume and merge). `sites` gains the columns of §10 (names in the runner's README), each metric that may be missing with its `_flag` column; `batches` gains `negligible_load_w_m2`; a new table `metric_definitions` (`metric`, `unit`, `definition`, `zero_guard`, `reference_dependent`) holds one row per evaluation column, written when the database is created; `site_timing` holds the serial timing runs and the view `site_timing_summary` their medians and ratios. Merge copies sites and their timing runs; a target of another schema version is refused as before.
- **Hourly Parquet.** Two more series: `SensibleHeating` and `SensibleCooling` (W); 20 in all. The conditioned temperature is already there.
- **Resume.** A reference written before an interruption gives its test sites its sensible series and temperature from its hourly file, and its floor area, runtime, processor time, zone counts, and memory from its `sites` row.
- `raw/` and `failure/` are unchanged; `--keep-raw` keeps every EnergyPlus file.

## What cannot be computed from the current outputs

- **Temperature over unconditioned hours:** not computed (D-157).
- **Processor time and memory** are not EnergyPlus outputs; only runs of the batch runner made after this stage have them. Results folders of schema version 5 cannot be resumed or merged with version 6, as before for any version change.
- **Sensible loads of a site whose IDF has ideal loads but whose `eplusout.eso` lacks the variables** (an IDF not written by *Convert2IDF*): a read error, as for the ground surfaces.

## Tests (test-first)

- `EvaluationMetrics`: each formula on small hand-computed series; the reference against itself (zero errors, equal counts); each zero and near-zero guard; top-interval sizes 88, 438, 876; the signs of NMBE and MBE; P90 peaks and exceedance; cost ratios with and without measures.
- `SimulationResultReader`: sensible series summed as reported (not multiplied again) and separately for heating and cooling, from a synthetic `.eso` with two ideal-loads systems; a missing variable as an error.
- `SystemProcessRunner`: memory and committed memory sampled from a real short process; processor time read when it exits.
- Batch runner: the new columns, the metric definitions table (every evaluation column has a row, and every metric that may be missing a flag column), the two series, resume of a reference with the new fields; the timing pass (selection, order, rows, summary, resume, merge, options).
- Opt-in end-to-end (EnergyPlus 26.2): on the linear plan's matrix, H and C are never above `Heating:DistrictHeatingWater` and `Cooling:DistrictCooling` ("The multiplier"); every run has processor time and committed memory; the pairing check passes for every configuration; a real batch with `--timing-repeats 1`.
