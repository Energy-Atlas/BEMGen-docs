# Experiment outputs

> **Status:** Draft, from the owner's specification "Experiment Output Variables" (2026-10-11), integrated with BEMGen's model and EnergyPlus 26.2. The reference site, both floor areas, the total load, the thresholds, both discrepancy measures, both temperatures, and the place of the metrics were settled with the owner on 2026-10-11. The rest (the meters behind each quantity, the percentile method, the quantile grid, the zero guards, and the site record) is the controller's realisation, provisional pending the owner's reading. · **Decisions:** D-016, D-038, D-112; new: D-130, ADR-019; terms: D-133 · **Applies to:** every EnergyPlus site simulated from a *Convert2IDF* file ([convert2idf.md](../architecture/convert2idf.md)) · **Refines:** §14 of the [research brief](../LOD_geometric_zoning_equivalence_research_brief.md#14-simulation-outputs)

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

Runtime is comparable only between runs made one at a time on the same idle machine with the same EnergyPlus build. Runs made in parallel (for example by `scripts/eplus-check`) record their concurrency, and their runtimes are not used as results.

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

What every site keeps, or can rebuild from the files EnergyPlus writes. All derived metrics in §2 to §5 are computed from these only:

| Raw output | Source |
| --- | --- |
| Hourly heating, cooling, and total load (and the end-use and diagnostic meters of §1) | `eplusout.mtr` (meters, hourly) |
| Hourly zone mean air temperature | `eplusout.eso` |
| Zone floor areas, volumes, and multipliers | `eplusout.eio` (`Zone Information`) |
| Total and conditioned floor area | `eplustbl.csv` (*Building Area*) |
| Runtime | `eplusout.err`, and the runner |
| Run status: completed, warnings, severe errors | `eplusout.err` |
| Site record | the IDF header and the runner |

`Output:SQLite` is also written for tools outside the repository, but the repository's code reads the text files only, which needs no native library.

## What the IDF requests

Together these give exactly the raw outputs above. [convert2idf.md](../architecture/convert2idf.md) lists them in file order.

- Hourly meters: §1, each only when used.
- `Zone Mean Air Temperature` hourly for every zone.
- `Output:Table:SummaryReports` `AllSummary` in comma and HTML style (floor areas, and the unmet hours as a sanity check).
- `Output:SQLite`.

The per-zone ideal-loads variables are also requested, as diagnostics. They are not raw outputs of this page, because zones do not align across configurations.

## Where the work happens

- **The IDF:** requests the outputs (`Lod.Export`).
- **The run and reading the raw outputs:** `Lod.Simulation` (ADR-019, written in the build of the [simulation-ready IDF stage](../plans/2026-10-11-idf-out.md)).
- **The metrics of §2 to §5:** pure functions over the raw outputs in `Lod.Simulation` (the owner, 2026-10-11), the one tested implementation that the tests, the experiment harness, and the later component share, so that no generator or script computes them its own way. D-130 records this as refining D-016.
- **Running batches of sites and storing their results:** in the repository since D-132, in the batch runner `scripts/IdfBatchRunner` (a development tool, not released), which writes DuckDB databases outside the repository: per run, a central database of the useful results and the hourly loads by fuel and by end use, and a full batch database (`scripts/IdfBatchRunner/README.md`). The definitions on this page do not change.
- **Writing test suites:** test suites, the test cases and sites that the batch runner then simulates, are written by `scripts/TestSuiteGenerator` (D-133), a development tool that writes IDFs from a YAML spec and runs no EnergyPlus (`scripts/TestSuiteGenerator/README.md`). No definition on this page changes.
- **Analysis:** outside the repository (D-016).
