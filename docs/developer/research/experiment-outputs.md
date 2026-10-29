# Experiment outputs

> **Status:** Draft, from the owner's specification "Experiment Output Variables" (2026-10-11), integrated with BEMGen's model and EnergyPlus 26.2. The reference site, both floor areas, the total load, the thresholds, both discrepancy measures, both temperatures, and the place of the metrics were settled with the owner on 2026-10-11. The rest (the meters behind each quantity, the percentile method, the quantile grid, the zero guards, and the site record) is the controller's realisation, provisional pending the owner's reading. · **Decisions:** D-016, D-038, D-112; new: D-130, ADR-019; terms: D-133; ground heat transfer (§9): the owner, 2026-10-19, [constructions and ground note](../plans/2026-10-19-suite-constructions-ground.md), Part B; paired evaluation metrics (§10): the owner's request of 2026-10-26, D-156, [evaluation metrics note](../plans/2026-10-26-evaluation-metrics.md), its definitions provisional pending the owner's reading · **Applies to:** every EnergyPlus site simulated from a *Convert2IDF* file ([convert2idf.md](../architecture/convert2idf.md)) · **Refines:** §14 of the [research brief](../LOD_geometric_zoning_equivalence_research_brief.md#14-simulation-outputs)

This page defines what every simulated site must yield, so that each test site and parameter variant can be compared with the others on the same terms.

- **Raw outputs** come from EnergyPlus, or are rebuilt from what it writes.
- **Derived metrics** are computed afterwards from the raw outputs only, by one shared implementation, never inside a test-suite generator.

Every definition below is fixed across all sites: the timestep, the units, the floor-area convention, the percentile method, the quantile grid, and the reference model. Changing one is a research change (GLOBAL.md scientific rule 7): it needs a decision-log entry, and every site it touches is recomputed.

## Terms

- **Site.** One building (a typology, its generator parameters, and its seed) in one zoning configuration, with one envelope, one weather file, and one set of heat-transfer options, simulated once and written as one IDF (D-133, which renamed it from "case"). A site is identified by its configuration (see [Site record](#7-site-record)).
- **Test case.** One reference site and at least one test site that differ only in zoning (D-133); a batch groups its sites by test case.
- **Zoning configuration.** The plan simplifier with its options (for example *Join Pieces*), the floor aggregator, and the two heat-transfer options (D-069).
- **Reference site** (the owner, 2026-10-11). The site every test site is compared against: the same building, envelope, and weather, under *No Simplification* and *Stack*, with **both heat-transfer options on**: *EnableInternalWallHeatTransfer* and *EnableFloorHeatTransfer* (D-069). It is the least simplified and most realistic configuration, the ground truth of the brief's §3. Every zone has multiplier 1, so every wall, floor, and ceiling between zones is paired.
  - The heat-transfer options of a test site are therefore a factor of the experiment, compared against this one fixed reference.
  - There is no ground option. Floors on the ground always face `Ground` (ADR-010), in every site.
  - A reference site is its own reference, so every comparison metric is zero there.
- **Hour.** One of the 8760 hours of the run period: a full non-leap calendar year (ADR-010, ADR-018). EnergyPlus simulates with 6 timesteps per hour and reports hourly. Every series below has exactly 8760 values.
- **Hourly load.** The energy of an hour divided by 3600 s, so the mean power over the hour, in W. Annual values are in kWh.
- **Floor areas** (the owner, 2026-10-11). Every normalised value is reported twice:
  - per **conditioned** floor area: the *Net Conditioned Building Area* of EnergyPlus's *Building Area* table;
  - per **total** floor area: its *Total Building Area*.

  Both count each zone times its multiplier. The total floor area is conserved by every zoning configuration (GLOBAL.md scientific rule 1). The conditioned floor area is not always: a merge that joins conditioned and unconditioned zones conditions the whole merged zone (research brief §8, "What the zoning levels do to the conditioned floor area"), and *Single Zone per Floor Type* and *Single Zone Building* do the same across storeys. The first run of the linear plan shows it: 1440 m² conditioned in the reference, 1728 m² under both single-zone aggregators. Hence both values. "EUI" below means the annual sum per floor area.

## 1. Loads and the EnergyPlus outputs behind them

HVAC is ideal loads with no capacity limit (D-112). Its delivered energy is therefore the building's thermal load, and EnergyPlus meters it as district energy with an efficiency of 1. Meters include zone multipliers; per-zone output variables do not. So building totals come from meters only.

| Quantity | EnergyPlus meter (hourly) | Notes |
| --- | --- | --- |
| Heating load | `Heating:DistrictHeatingWater` | Ideal-loads supply-air total heating, sensible plus latent. `DistrictHeatingWater:Facility` is not used, because it also holds hot water. `Heating:EnergyTransfer` is sensible only; it is kept as a diagnostic. |
| Cooling load | `Cooling:DistrictCooling` | Ideal-loads supply-air total cooling, sensible plus latent (dehumidification). `Cooling:EnergyTransfer` (sensible only) is kept as a diagnostic. |
| Total load across all modelled end uses | the sum of `Electricity:Facility`, `NaturalGas:Facility`, `DistrictHeatingWater:Facility`, and `DistrictCooling:Facility` | It covers heating, cooling, interior lighting, interior electric equipment, **interior gas equipment** (`InteriorEquipment:NaturalGas` is on `NaturalGas:Facility`, confirmed in a 26.2 run), hot water, and ventilation fans. It adds thermal loads (heating, cooling, hot water as district energy) to site energy (lighting, equipment) (the owner, 2026-10-11). Because BEMGen conserves installed and hourly scheduled internal loads (GLOBAL.md scientific rule 1), the non-HVAC part is the same hour by hour in every variant of a building, so differences in the total come from heating and cooling. |
| End uses, for checks | `InteriorLights:Electricity`, `InteriorEquipment:Electricity`, `InteriorEquipment:NaturalGas`, `WaterSystems:DistrictHeatingWater` | They let the post-processing check that the end uses sum to the total and that internal loads are equal across test sites. |

A meter is requested only when the building has its source (EnergyPlus warns about a meter with nothing on it). A missing meter reads as zero every hour.

## 2. Annual loads

For heating, cooling, and total, per site:

| Metric | Definition |
| --- | --- |
| Annual sum | Σ over 8760 hours of the hourly energy, kWh |
| EUI, conditioned | annual sum / conditioned floor area, kWh/m² |
| EUI, total | annual sum / total floor area, kWh/m² |

## 3. Peak loads

For heating, cooling, and total, per site, from the hourly load series (W) of all 8760 hours, zero hours included:

| Metric | Definition |
| --- | --- |
| Maximum | the largest hourly load |
| P99, P95, P90 | the 99th, 95th, and 90th percentile, by linear interpolation between order statistics: Hyndman and Fan type 7, the default of NumPy and R. For sorted values x₍₁₎ ≤ … ≤ x₍ₙ₎, n = 8760, h = (n − 1)·p + 1, P = x₍⌊h⌋₎ + (h − ⌊h⌋)·(x₍⌊h⌋₊₁₎ − x₍⌊h⌋₎). |
| Normalised | each of the above / conditioned floor area, and / total floor area, W/m² |

For the total load, peak duration:

| Metric | Definition |
| --- | --- |
| Hours above P99, P95, P90 | the number of hours whose total load is strictly above the **reference site's** P99, P95, or P90 of the total load |

The thresholds are taken from the reference site (the owner, 2026-10-11). A site's hours above its own P99 are about 1 % of 8760 by construction, whatever the site, so own-percentile thresholds would carry no information. The reference's thresholds are fixed per building, envelope, weather, and heat-transfer options, and reproducible. The thresholds themselves are kept with the metric.

## 4. Hourly comparison with the reference

For heating, cooling, and total, each test site against its reference site, hour by hour. y is the test site's hourly load, r the reference's, n = 8760, and r̄ the reference's mean:

| Metric | Definition | Zero guard |
| --- | --- | --- |
| CV(RMSE) | √(Σ (yᵢ − rᵢ)² / n) / r̄, as a fraction (× 100 for percent). The denominator is n, with no parameter count (ASHRAE Guideline 14's n − p with p = 0). | r̄ = 0 (for example no cooling in a cold climate): undefined, stored as missing with the flag `ZeroReferenceMean`, never as 0 or infinity |
| Load-duration-curve discrepancy, quantile NRMSE | Qᵧ(p) and Qᵣ(p) are the type 7 quantiles above, on the fixed grid p = 0.00, 0.01, …, 1.00 (101 points). The metric is √(Σₚ (Qᵧ(p) − Qᵣ(p))² / 101) / r̄. It compares the two load-duration curves (the series sorted by magnitude) regardless of when each hour occurs. | as CV(RMSE) |
| Load-duration-curve discrepancy, Kolmogorov–Smirnov | D = maxₓ \|Fᵧ(x) − Fᵣ(x)\|, with Fᵧ and Fᵣ the empirical distribution functions of the 8760 hourly values, evaluated at every value of either series. It is unitless, in [0, 1]. Ties (many zero hours) are allowed. | both series all zero: D = 0 |

The spec asks for at least one load-duration-curve discrepancy. Both are computed (the owner, 2026-10-11), because they answer different questions: the quantile NRMSE measures magnitude, and KS measures distribution shape. Both definitions are fixed for every experiment.

## 5. Building-level temperature

Zones are not spatially aligned across zoning configurations, so zone temperatures are never compared zone by zone. From `Zone Mean Air Temperature` (hourly, every zone), per hour t:

| Metric | Definition |
| --- | --- |
| Area-weighted mean | T̄(t) = Σ_z w_z·T_z(t) / Σ_z w_z, with w_z = the zone's floor area × its multiplier, from EnergyPlus's own zone report (`.eio`) |
| Area-weighted standard deviation | σ(t) = √(Σ_z w_z·(T_z(t) − T̄(t))² / Σ_z w_z) (population form) |

Each is computed twice (the owner, 2026-10-11):

- over **all zones**;
- over the **conditioned zones**: those with a thermostat in the IDF.

A zone of zero floor area has zero weight, and a building with no floor area cannot be simulated, so Σ w_z > 0 over all zones. A building with no conditioned zone has no conditioned value: it is stored as missing with the flag `NoConditionedZone`. As the conditioned floor area does, the set of conditioned zones can grow under a merge. These are building-level summaries only.

## 6. Simulation runtime

| Field | Source |
| --- | --- |
| EnergyPlus runtime | the elapsed time EnergyPlus reports at the end of `eplusout.err` (`Elapsed Time=…`), in seconds |
| Wall-clock runtime | measured by the runner around the EnergyPlus process |
| Conditions | the EnergyPlus version and build, the processor name and logical core count, and the number of EnergyPlus processes run at the same time |
| Processor time | the EnergyPlus process's user and kernel time, read by the runner when it exits (§10, item 10) |
| Process memory | sampled by the runner's process runner every 50 ms while EnergyPlus runs: the mean working set, the largest peak working set, and the largest peak committed private memory (§10, item 11) |

Wall-clock runtime is comparable only between runs made one at a time on the same idle machine with the same EnergyPlus build. Runs made in parallel (for example by `scripts/eplus-check`) record their concurrency, and their wall-clock runtimes are not used as results. The processor time and the committed memory are far less sensitive to other processes, and the batch runner's serial timing pass gives runtimes made one at a time (§10, item 13, D-157).

## 7. Site record

Every site carries enough to identify it without opening Grasshopper (brief §18):

- **Site ID:** deterministic, the SHA-256 of the IDF text and the weather file's bytes.
- **Building ID:** the typology, the generator's typed parameters, and the seed, from the building's provenance.
- **Zoning configuration ID:** the simplifier and its options, the aggregator, and the heat-transfer options.
- **Reference site ID.**
- **Inputs:** the envelope preset's name, and the weather file's name and SHA-256.
- **Versions:** BEMGen's code version, and the EnergyPlus version and build.
- **Parameter values:** the experiment's own parameters.
- **Runtime:** with its conditions.

*Convert2IDF* writes the identifying lines into the IDF header, and the runner reads them back, so the record travels with the file.

## 8. Required raw outputs

What each site's metrics are computed from, read from the files EnergyPlus writes. All derived metrics in §2 to §5, §9, and §10 are computed from these only:

| Raw output | Source |
| --- | --- |
| Hourly heating, cooling, and total load (and the end-use and diagnostic meters of §1) | `eplusout.mtr` (meters, hourly) |
| Hourly zone mean air temperature | `eplusout.eso` |
| Hourly ideal sensible heating and cooling of each ideal-loads system (§10) | `eplusout.eso` (`Zone Ideal Loads Zone Sensible Heating Energy`, `… Cooling Energy`) |
| The ideal-loads systems' names (§10) | the IDF (`ZoneHVAC:IdealLoadsAirSystem`) |
| Processor time and process memory (§10) | the runner |
| Zone floor areas, volumes, and multipliers | `eplusout.eio` (`Zone Information`) |
| Hourly ground heat transfer (§9) | `eplusout.eso` (`Surface Inside Face Conduction Heat Transfer Energy` of each ground surface) |
| Each surface's zone and outside boundary, for §9 | `eplusout.eio` (the surface details: `Zone Surfaces` and `HeatTransfer Surface`) |
| Total and conditioned floor area | `eplustbl.csv` (*Building Area*) |
| Unmet hours, a sanity check: the hours with the heating or the cooling setpoint not met | `eplustbl.csv` (the *Facility* row of the *System Summary*'s *Time Setpoint Not Met*, *During Heating* and *During Cooling*: every hour of the run period, occupied or not) |
| Runtime | `eplusout.err`, and the runner |
| Run status: completed, warnings, severe errors | `eplusout.err` |
| Site record | the IDF header and the runner |

`Output:SQLite` is also written for tools outside the repository, but the repository's code reads the text files only, which needs no native library.

**What a run keeps** (D-153). The batch runner reads these files when a site finishes and keeps, by default:

- the site's metrics, its unmet hours, and its run status, in the run's central database;
- its hourly series (the loads and meters of §1, the building temperatures of §5, the ground heat transfer of §9, the sensible loads of §10), in one file per site;
- its `eplusout.err`.

The other EnergyPlus files of a succeeded site (`eplusout.mtr`, `eplusout.eso`, `eplusout.eio`, `eplustbl.csv`, `eplusout.sql`, …) are kept only when the run is asked to keep them (`--keep-raw`); a site that ran and did not succeed keeps all of them. So the metrics of a run can be recomputed from its hourly series, but a raw output that is not among them (a zone's own temperature, a surface's conduction) only from a site whose files were kept, or by running its IDF again: the site ID, the IDF, and the weather file make the run repeatable (the runner's README (`scripts/IdfBatchRunner/README.md`)).

## 9. Ground heat transfer

The heat that ground-contact surfaces conduct at their inside faces, summed over the building (the owner, 2026-10-19). Like the temperatures of §5, it is a building-level quantity: zones are not aligned across zoning configurations, so it is never compared zone by zone.

**Definition.** For hour t,

G(t) = Σ_s m_z(s) · Q_s(t) / 3600 s, in W (the mean power over the hour, like the hourly loads),

over every heat-transfer surface s whose outside boundary is the ground, where:

- Q_s(t) is EnergyPlus's `Surface Inside Face Conduction Heat Transfer Energy` of s in hour t, in J;
- m_z(s) is the multiplier of the surface's zone (zone multiplier × zone list multiplier, from `Zone Information`). EnergyPlus reports surface variables for one instance of a zone and does not multiply them: in a 26.2 run, a ground floor gave the same annual conduction (−2097.25 kWh) with its zone at multiplier 1 and at 3. Hence the multiplier here, as the meters of §1 have it.

**Which surfaces.** Those whose outside boundary condition is `Ground` or `GroundFCfactorMethod`, the two ground boundaries *Convert2IDF* writes (ADR-010, ADR-023). They are found in EnergyPlus's own surface report, never in the IDF: `Output:Surfaces:List, Details` makes `eplusout.eio` list every heat-transfer surface under its zone's `Zone Surfaces` line with its `ExtBoundCondition`, which EnergyPlus 26.2 writes as `Ground` for `Ground` and `FCGround` for `GroundFCfactorMethod` (seen in 26.2 runs; the *Output Details and Examples* lists only `ExternalEnvironment` and `Ground` among the outside values). Not included:

- a surface paired with another zone (`Surface`): its `ExtBoundCondition` is the partner's name;
- an adiabatic surface or an internal mass: its own name;
- an outdoor surface: `ExternalEnvironment`;
- a surface on other side coefficients or an other side conditions model: EnergyPlus shows the object's name, which does not say whether it stands for the ground. *Convert2IDF* writes none, so none is counted;
- a Kiva foundation surface (`Foundation`): Kiva is written only outside the pipeline (D-145).

A building whose `.eio` lists no ground surface has G = 0 every hour. Every building *Convert2IDF* writes has ground floors (ADR-010).

**Sign.** EnergyPlus's own, unchanged. The *Input Output Reference* (26.2, "Surface Inside Face Conduction Heat Transfer Rate") defines a positive value as conduction from just inside the inside face toward the inside face, and a negative value as conduction from the inside face into the core of the surface. So **G > 0 is heat conducted toward the zones, and G < 0 heat leaving the zones into the ground constructions.** It is conduction at the inside face, not the heat delivered to the zone air, which also depends on convection and radiation at the face (the same reference's note). Two EnergyPlus 26.2 runs of the packet's medium office F-factor set confirm the sign, G following the difference between the ground temperature and the zones:

- Chicago O'Hare TMY3, the canonical linear plan under *Perimeter Core* and *Stack* (the F-factor end-to-end case, with the two requests added to its IDF before the writer made them): G is negative in 10 of 12 months, January −738 kWh; the ground temperatures, the weather file's dry-bulb delayed three months, are below the zones in those months.
- Las Vegas (OpenEPW NSRDB GOES TMY 2025, 3B), the two-storey linear plan under *No Simplification* and *Stack*, F/C-factor ground temperatures of 21.0 °C in January, 8.9 °C in March, and 34.1 °C in October: monthly G of −69, −1187, and +664 kWh. The annual net is −3715 kWh, the gain 2947 kWh, and the loss 6662 kWh (`GroundHeatTransferEndToEndTests`).

**Metrics**, per site, in kWh:

| Metric | Definition |
| --- | --- |
| Annual net | Σ over 8760 hours of G (W × 1 h) / 1000 |
| Annual gain | Σ of G over the hours with G > 0, / 1000 |
| Annual loss | Σ of −G over the hours with G < 0, / 1000; never negative |

Net = gain − loss. A zero series gives zero for all three. There is no comparison with the reference yet: the comparison metrics of §4 stay on the loads.

## 10. Paired evaluation metrics

> **Status:** From the owner's request of 2026-10-26 (D-156). The owner settled on 2026-10-26 (D-157): the near-zero guard, the ideal sensible loads, the top intervals, the memory measure, and the pairing check as below; ASHRAE Guideline 14's sign for the bias errors; P90 beside P95 and P99; no temperature over unconditioned hours; and runtime and memory from concurrency-robust measures and a serial timing pass. [Evaluation metrics note](../plans/2026-10-26-evaluation-metrics.md).

A second metric set, beside §2 to §5, which it does not change: they stay on the total heating and cooling meters (sensible plus latent) and the total load, and §10 is on the **ideal sensible** heating and cooling loads, aggregated from the zones, each site compared with its reference site (§ Terms) hour by hour, with its temperature and its computational cost. y is the site's hourly series, r its reference's, n = 8760, and A the reference's total floor area.

1. **Sensible loads.** H(t) = Σ_z Q^sens,heat_z(t) / 3600 s and C(t) = Σ_z Q^sens,cool_z(t) / 3600 s, in W, over every zone with a `ZoneHVAC:IdealLoadsAirSystem`. Q is EnergyPlus's hourly `Zone Ideal Loads Zone Sensible Heating Energy` or `Zone Ideal Loads Zone Sensible Cooling Energy` of the zone's system, keyed by the system's name.
   - **The zone multiplier is already in Q.** Unlike the surface variables of §9, EnergyPlus reports the ideal-loads variables of a zone for all its instances. In 26.2 runs of the linear plan, under *Stack* and under *Stacked Floor Zone Multiplier* (multipliers above 1), Σ_z Q^sens,heat_z equals the multiplied meter `Heating:DistrictHeatingWater` to 1e-15 in every hour but rare ones, and Σ_z Q^total,cool_z equals `Cooling:DistrictCooling` to 1e-12; multiplied again, they exceeded the meters by up to 2.8 times (the evaluation metrics note, "The multiplier"). So Q is summed as reported.
   - Each zone's heating and cooling are separate non-negative variables, so they are summed separately at each hour and **never netted**; latent loads, hot water, lights, equipment, and fans are not in them.
   - *Convert2IDF*'s ideal loads have no humidification, so their heating is sensible only and H is the heating meter `Heating:DistrictHeatingWater` (§1) in all but rare hours: in the linear plan's 56 configurations, one hour in each of three, 1e-6 below it; in the atlas medium office, 57 of 8760 hours, by at most 2 × 10⁻⁵ of the hour's load. C is at most `Cooling:DistrictCooling`, which adds the latent part. The meters `Heating:EnergyTransfer` and `Cooling:EnergyTransfer` are another quantity, not H and C: they differ from them by up to 0.8 % in an hour and 0.3 % in a year, and stay diagnostics. The opt-in end-to-end tests check that the linear plan's H and C are never above the meters in any hour.
2. **Annual.** E = Σ y / 1000 (kWh); per conditioned and per total floor area (kWh/m², §Terms); relative error 100 · (E − E_ref) / E_ref (%).
3. **Peaks.** The maximum, P99, P95, and P90 (type 7, §3) of all hours, in kW, each with its relative error.
4. **Exceedance.** The thresholds are the reference's P99, P95, and P90 of the same load, common to the site and the reference: the site's hours with y strictly above, the reference's own hours above, and their difference (h). The thresholds are stored with the counts.
5. **CV(RMSE) and NMBE.** CV(RMSE) = 100 · √(Σ (y − r)² / n) / r̄ and NMBE = 100 · Σ (r − y) / (n · r̄), %, with n in the denominator (no parameter count). NMBE has **ASHRAE Guideline 14's sign, reference minus site**, the reference in the place of the measured data (D-157): positive when the site's load is below the reference's.
6. **Load-duration-curve NRMSE.** Both series sorted from largest to smallest; over an interval I of ranks, 100 · √(Σ_{i∈I} (y₍ᵢ₎ − r₍ᵢ₎)² / |I|) / mean_{i∈I} r₍ᵢ₎, normalised by the reference's mean **within the interval**. Four intervals: all n ranks, and the top 1 %, 5 %, 10 %: the first ⌈k · n / 100⌉ ranks, 88, 438, and 876 hours. It is rank by rank on the whole curve, beside the 101-point quantile NRMSE of §4, which stays.
7. **KS.** The two-sample Kolmogorov–Smirnov D of §4.
8. **Temperature.** T(t), the conditioned-floor-area-weighted mean zone air temperature: §5's area-weighted mean over the conditioned zones. MBE = Σ (T_ref − T) / n and RMSE = √(Σ (T_ref − T)² / n), °C, over all hours (n = 8760); MBE has ASHRAE Guideline 14's sign, reference minus site (D-157). Zones are never compared one by one (§5).
9. **No temperature over unconditioned hours** (the owner, 2026-10-26, D-157). No program is ever off by the hour: a zone is conditioned all year or not at all, and *Convert2IDF* leaves the ideal loads' availability schedules blank. Sourced programs set back their setpoints (the atlas medium office from 21/24 °C to 15.6/26.7 °C at night, on Saturday afternoons, Sundays, and holidays), which is conditioning, not its absence. The temperature is compared over all hours only, and no such subset is computed.
10. **Computation.** Wall-clock runtime and EnergyPlus's elapsed time (§6), the processor time (user and kernel, read when the process exits), the zone count (the zones of `eplusout.eio`) and the represented zone count (Σ multipliers), the process memory, and each one's ratio site / reference.
11. **Process memory.** The runner samples the EnergyPlus process at each 50 ms poll of its wait: the average working set is the mean of the samples, and the peak working set and the **peak committed private memory** are the largest peaks the operating system reported at a sample (they include growth between samples, not after the last one). In MiB. The working set is what the process holds in physical memory, which the operating system trims under pressure from other processes; the committed memory is what it allocated, which other processes do not change. It is not an EnergyPlus output; a run shorter than one poll has none.
12. **Pairing.** A site is compared only with its test case's reference: the same building, envelope, and weather file (D-132), the same run period hours. The runner also checks the non-zoning assumptions it can measure: the hourly internal-load end uses of §1 (lights, electric and gas equipment, hot water), conserved hour by hour (GLOBAL.md scientific rule 1), against the reference's within `ToleranceSettings.LoadEquals`. A site that fails keeps its metrics, with the problem in its status.
13. **Runtime and memory in parallel runs** (D-157). Energy results do not depend on how many EnergyPlus processes run at once, so batches run in parallel. Their runtime and memory are measured two ways:
    - **In every run,** with the concurrency-robust measures: the processor time rather than the wall clock (other processes slow a run's wall clock much more than its processor time, as long as runs are at most one per physical core), and the peak committed memory rather than the working set. Their ratios use the site's and the reference's runs of the same batch, which are not made at the same moment (references first, then variants, and possibly another session after a resume), so they are robust rather than exact. The wall clock, EnergyPlus's elapsed time, and the working set are kept, and are results only for runs made one at a time.
    - **In a serial timing pass** (`--timing-repeats N`, optionally on `--timing-test-cases K` test cases chosen deterministically by the SHA-256 of their IDs): once every site is written, the succeeded sites of the timed test cases run again one at a time, N times each. Repeats are the outer loop, and within a repeat a test case's reference runs just before its variants, so that a drift of the machine reaches them alike. Each run is kept; the medians of the completed repeats, with their ratios to the reference's medians, are the reported runtimes and memory. Comparing them with the same sites' parallel measures calibrates the parallel runs.

**Zero and near-zero denominators.** A metric normalised by the reference's load is missing with `NearZeroReference` when the reference's power intensity is at or below ε = `ToleranceSettings.NegligibleLoadIntensity`, 0.01 W/m² of A (0.0876 kWh/m² a year), and with `ZeroFloorArea` when A is zero. The intensity is the normaliser's: E_ref / (n · 1 h) / A for an annual error, the reference's peak / A for a peak error, r̄ / A for CV(RMSE), NMBE, and the full curve, the interval's mean / A for a top interval, and the threshold / A for an exceedance (hours above a threshold of almost nothing would count every hour with any load). A ratio without both values, or over a reference value of zero, is missing with `NotMeasured`. A missing metric is never 0, ±∞, or NaN. The tolerance is recorded with every run.

## What the IDF requests

Together these give exactly the raw outputs above. [convert2idf.md](../architecture/convert2idf.md) lists them in file order.

- Hourly meters: §1, each only when used.
- `Zone Mean Air Temperature` hourly for every zone.
- `Surface Inside Face Conduction Heat Transfer Energy` hourly for each ground-contact surface, keyed by its name (§9). Keying by name, not `*`, keeps the `.eso` small.
- `Output:Surfaces:List` `Details`, so that `eplusout.eio` gives each surface's zone and outside boundary (§9).
- `Output:Table:SummaryReports` `AllSummary` in comma and HTML style (floor areas, and the unmet hours as a sanity check, read before the batch runner discards the file).
- `Output:SQLite`, for tools outside the repository; the batch runner keeps it only with `--keep-raw` or for a site that did not succeed (§8).

The per-zone ideal-loads variables are also requested. Their sensible heating and cooling are raw outputs of §10, summed over the zones (never compared zone by zone, since zones do not align across configurations); their total heating and cooling stay diagnostics.

## Where the work happens

- **The IDF:** requests the outputs (`Lod.Export`).
- **The run and reading the raw outputs:** `Lod.Simulation` (ADR-019, written in the build of the [simulation-ready IDF stage](../plans/2026-10-11-idf-out.md)).
- **The metrics of §2 to §5 and §9:** pure functions over the raw outputs in `Lod.Simulation` (the owner, 2026-10-11), `ExperimentMetrics`; those of §10 in `EvaluationMetrics` beside it (D-156), the one tested implementation that the tests, the experiment harness, and the later component share, so that no generator or script computes them its own way. D-130 records this as refining D-016.
- **Running batches of sites and storing their results:** in the repository since D-132, in the batch runner `scripts/IdfBatchRunner` (a development tool, not released), which writes a run folder outside the repository: a central DuckDB database of every site's metrics and status, one Parquet file per succeeded site with its hourly series (the loads by end use and by fuel, the total, the building temperatures, and the ground heat transfer of §9), and each site's `eplusout.err` (D-153; `scripts/IdfBatchRunner/README.md`). The definitions on this page do not change.
- **Writing test suites:** test suites, the test cases and sites that the batch runner then simulates, are written by `scripts/TestSuiteGenerator` (D-133), a development tool that writes IDFs from a YAML spec and runs no EnergyPlus (`scripts/TestSuiteGenerator/README.md`). No definition on this page changes.
- **Analysis:** outside the repository (D-016).
