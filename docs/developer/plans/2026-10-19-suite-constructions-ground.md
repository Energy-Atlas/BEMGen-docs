# Constructions, native ground, and ground heat transfer in test suites and the batch runner (design note)

> **Status:** Done on `feature/test-suite-generator` (built, reviewed, verified, D-151); merged into `main` (D-152) and pushed (D-154); released in `v1.5.0` (D-175) · **Date:** 2026-10-19 · **Decisions:** D-133 to D-136, D-137 to D-150 (on `main`); new: D-151 · **Branch:** `feature/test-suite-generator`, on `main` `3da0bba` (packet v7 and native ground merged, D-150; D-136: work continues here)

This is one stage, run as D-111 sets out:

- this note;
- one test-first build;
- a review by a second agent;
- `scripts/verify.ps1` before the merge;
- one decision-log entry.

It makes no Grasshopper component changes. Program JSON 3.0.0 is the next stage, with its own note ([Programs](#programs)). The schedule generator is not part of either.

**Stop line.** The build ends with the branch verified, reviewed, and documented. It does not merge, tag, push, or release.

## What changed since the test suites (review)

### Constructions (D-137 to D-144, v1.4.0)

- **Import.** *Construction JSON* imports the atlas's construction JSON into a `ConstructionSet` (`Lod.ConstructionJson`, `Lod.Core.Envelope`).
- **Conversion.** *Convert2IDF* takes the set through `Convert2Idf.Run(building, ConstructionSet, IdfOptions, …)`, with `IdfOptions.FillFromExample`.
- **Scope.** Only unified sets of scope `building` convert. Single-dwelling sets and detailed documents are refused (D-142).
- **Fill From Example** (default false) fills a role the set marks not applicable with the Example envelope's construction, with a warning. Without it, a missing role is the error `ConstructionMissing` (D-140).
- **Mass.** A set adds mass from its reference budgets (the mass ledger, D-139). A slab removed by a merge is written as twice its area at half its thickness, so its capacity counts once (D-143). The ledger holds on every zoning.
- **Windows.** A set's windows take its incident solar multiplier, which was checked in EnergyPlus (D-143).

### Ground conditions (D-145 to D-149, merged as D-150)

- **Packet.** Packet v7 replaces v3, with readers for unified 2.0.0 and detailed 3.0.0. The v3 readers are retired (D-145, D-146, ADR-023).
- **Native ground.** A v7 set's ground floor takes the set's own `GroundFloor` method:
  - **F-factor:** `Construction:FfactorGroundFloor` with the set's F, the piece's area, and its exposed perimeter, with shared zone edges cancelled. A core's perimeter is exactly 0 (D-149).
  - **Layered ground:** the set's layers on `Ground`.
- **Ground temperatures** follow the source's rules:
  - **F- and C-factor surfaces:** the weather file's monthly mean dry-bulb, delayed three months and rounded to 0.1 °C. A v7 set with such surfaces and no weather file is refused.
  - **Layered ground:** `BuildingSurface` at 18 °C in every month.
  - **Without a set:** D-130's rule stays.
- **Diagnostics:**
  - `GroundMethodNotSupported`, `GroundTemperatureWeatherMissing`, and `GroundAssignmentSetAside`.
  - `ExampleWindowSolarNotAbsorbed` (D-147) warns when Example windows fill a set without windows over a ground floor that absorbs no solar. EnergyPlus then reports one severe error per such zone.
- **Checked in EnergyPlus 26.2.** These cases passed with no unexpected warning:
  - the office, warehouse, apartment, and tall-building F-factor cases;
  - the layered hospital cases;
  - the turned plans with courts, now that core perimeters are exactly 0 (D-148, D-149).

  The runner's list of expected warnings is unchanged.
- **Open (ADR-023):**
  - the crawlspace or garage air exchange is unsupported;
  - the C-factor soil resistance appears capped;
  - the schemas' `$id` versions differ from the documents', to be reported to the atlas.

### Why constructions and ground fit a test case

A test site may differ from its reference only in zoning (D-133). The changes keep that:

- The mass ledger and the half-thickness slices conserve heat capacity across zonings (D-143).
- The F-factor perimeters times multipliers keep the footprint's perimeter on every zoning (D-146, D-149).
- The ground temperatures depend only on the weather file and the set, both fixed per test case.

So a construction set, its fill choice, and its ground method are test-case inputs. Their effects across a test case's sites are zoning effects.

### Programs

Nothing changed in BEMGen since *Program JSON* 2.0.0 (D-126, v1.2.0). The atlas (branch `codex/foundation-ground`, `e9a982d`, read only) now has two newer contracts.

**Program JSON 3.0.0** is the form the catalogue exports. It changes the physical model, not only the file format:

- object-specific heat fractions (lights: radiant, visible, return air; equipment: radiant, latent, lost);
- explicit conditioning states, with no setpoint for a disabled service;
- zero loads omitted;
- fuel and host kept, so propane is not natural gas and may need `OtherEquipment`;
- exterior lighting;
- shared services instantiated once;
- hot-water mains from EnergyPlus's weather-file correlation instead of a fixed 10 °C;
- `metadata.resolutions` replaces `assumptions`.

So it needs changes to the program model in `Lod.Core`, to `Lod.ProgramJson`, and to *Convert2IDF*'s loads. It is a stage of its own, not part of this one.

**Program JSON 4.0.0** is opt-in. It moves hot water out of `loads` into `water_heating` draws on heaters with a fuel and a conversion efficiency. That changes how the experiment outputs count hot water: today it is district heating water (experiment outputs §1). So it is a research change, left for a later decision.

**Files for the 3.0.0 stage.** The 3.0.0 stage copies these from the atlas at `e9a982d` into its test fixtures and schemas (the owner's allowance, 2026-10-19). The table gives the first 16 hex digits of each file's SHA-256:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `schemas/program-json-v3.schema.json` | 41 329 | `9647eb7bd5ee0f12…` |
| `schemas/schedule-json-v2.schema.json` | 8 401 | `ea61c7bdf58e19ca…` |
| `docs/examples/program-json-v3/medium-office.defaulted.json` | 55 029 | `2ffc1bd338cd59e2…` |
| `docs/examples/program-json-v3/medium-office.raw.json` (a raw file, to be refused) | 45 251 | `7f3b08875a3f98c8…` |
| `docs/examples/program-json-v3/residential.defaulted.json` | 2 886 769 | `74437bb92ccd2248…` |

The residential example is large. Its stage decides whether to commit it, or to keep it outside the repository behind an opt-in test.

Once *Program JSON* reads 3.0.0, the suite generator needs no change of its own: `program_json` takes whatever the importer accepts, and a program's content is already hashed into the test case ID.

## Plan

### Part A: the test-suite generator

1. **Spec, still version 1 (an additive change).** A constructions entry gives either `builtin: Example` (as now) or a unified construction JSON:

   ```yaml
   constructions:
     example: {builtin: Example}
     office-5a: {construction_json: constructions/medium-office-2019-5A.unified.json, labels: {vintage: "2019"}}
     office-4b: {construction_json: https://…/medium-office-2019-4B.unified.json, sha256: 1f2e…, fill_from_example: true}
   ```

   - `construction_json` is a file next to the spec, or a URL pinned by `sha256`, as programs are.
   - `fill_from_example` defaults to false.
2. **Inputs.** A `ConstructionFiles` class, alongside `ProgramFiles`:
   - each file is located and hashed when the plan is made;
   - with `--write`, it is fetched and imported (`ConstructionJsonImporter.Import`) before anything is written;
   - each file is kept in `inputs/` by its SHA-256.

   A refused set stops the suite with exit code 2, before the suite folder exists. Refusal covers:
   - a scope other than `building`;
   - a schema or closure error;
   - an F- or C-factor set in a suite that has no weather file for it.
3. **Test case ID.** The constructions part holds the content, not the id: `builtin:Example`, or `json:<sha256>;fill=<bool>`. Two entries with one file and one fill choice are the same inputs, which is an error as today.
4. **Pairing by climate (the owner, 2026-10-19).** A construction set and its ground are made for one climate, so the generator pairs each set only with weather files of the set's climate zone (`ConstructionJsonImport.ClimateZone`):
   - The cross product of constructions and weather files keeps only the matching pairs. A non-matching pair is never a test case, so it is not listed as excluded either.
   - `builtin: Example` has no climate zone and pairs with every weather file, as now.
   - A set whose zone matches no selected weather file is an error in the plan, since the spec would write nothing for it.
   - Programs keep their existing climate filter (`ExcludedByClimate`).
   - The plan's printout gives the pairs per set.
5. **Writing.** `Convert2Idf.Run(building, set, new IdfOptions(heat) { FillFromExample = … }, file, weather)`.
   - The conversion's warnings are kept per site in a new `suite_sites.warnings` column.
   - **Invalid sites (the owner, 2026-10-19).** A site whose conversion gives `ExampleWindowSolarNotAbsorbed` is `Invalid` and is not written, because EnergyPlus would fail it with severe errors. Its row records the diagnostic.
   - If the reference is such a site, its test case is `ReferenceInvalid`, as today.
6. **Tables.** `test_cases` gains five columns, and the same values go into `test_case_parameters`:
   - `constructions_kind`: `builtin` or `json`;
   - `constructions_sha256`;
   - `constructions_climate_zone`;
   - `fill_from_example`;
   - `ground_method`, one of:
     - `IndoorMinus2`: no set (D-130);
     - `FFactor` or `Layered`: a v7 set (D-145);
     - (no `Mixed`: see the build log)
7. **Tests, first.** These use the pinned packet v7's fixtures (`tests/Lod.ConstructionJson.Tests/Fixtures/packet/`).
   - **Spec:**
     - a URL without `sha256`;
     - an unknown key;
     - `fill_from_example` that is not a boolean.
   - **Plan:**
     - IDs by content;
     - pairing: the 3B medium office set with a 3B and a 5A weather file gives one pair, and `builtin: Example` gives two;
     - a set with no matching weather file is an error.
   - **Writing:**
     - **The medium office F-factor set on the linear plan.** Every site is written with F-factor ground, and every site's Σ P × multiplier equals the footprint's perimeter.
     - **A layered set:** `BuildingSurface` at 18 °C.
     - **A single-dwelling set:** refused before writing.
     - **The small data centre's windowless set with fill, on a windowed plan:** `Invalid`, with the warning, and no file.

### Part B: ground heat transfer (the owner, 2026-10-19)

A new building-level raw output: the hourly heat that ground-contact surfaces conduct into the zones. Like the temperatures (experiment outputs §5), it is a building-level sum, never compared zone by zone. A research addition, so it changes `docs/research/experiment-outputs.md` in the same change (GLOBAL.md scientific rule 7).

1. **Definition.** For hour t, G(t) = Σ_s m_z(s) · Q_s(t), over every heat-transfer surface s whose outside boundary condition is `Ground`, `GroundFCfactorMethod`, or `OtherSideCoefficients` used for ground. In this definition:
   - m_z(s) is the multiplier of the surface's zone;
   - Q_s(t) is EnergyPlus's `Surface Inside Face Conduction Heat Transfer Energy` for s.

   Its unit is W, as an hourly mean, like the load series. Its sign is EnergyPlus's: positive when heat enters the zone through the inside face. The build confirms the sign on a run before writing it down.

   Not included:
   - a surface paired with another zone (`Surface`);
   - an adiabatic surface;
   - an outdoor surface.
2. **The IDF (`Lod.Export`).** The research output set requests:
   - `Surface Inside Face Conduction Heat Transfer Energy`, hourly, keyed by the name of each ground-contact surface. Keying by name, not `*`, keeps the `.eso` small;
   - `Output:Surfaces:List, Details`, so that `eplusout.eio` lists every surface with its zone and its outside boundary condition.

   Every building has ground-contact surfaces (ADR-010), so the requests are unconditional. The snapshots and `docs/architecture/convert2idf.md` change.
3. **Reading (`Lod.Simulation`).**
   - `SimulationResultReader` reads the surfaces' zones and boundary conditions from the `.eio`, never from the IDF. The zone multipliers already come from there (§5).
   - It sums the variable into `SimulationResult.GroundHeatTransfer`, an `HourlySeries`.
   - A run without the variable fails with the reader's actionable error, as a missing meter's would.
   - A building whose `.eio` lists no ground surface has a zero series.
4. **Metrics.** The annual net, the annual gain (the sum over hours with G > 0), and the annual loss (the sum of −G over hours with G < 0), in kWh. There is no comparison with the reference yet; the comparison metrics of §4 stay on the loads.
5. **The runner.**
   - **Batch database:** a new series `GroundHeatTransfer`, of kind `Ground`, in the long table.
   - **Central database:** a new table `hourly_ground (site_key, hour, value_w)`, with its long view, and merges that copy it.
   - **Site columns:** `annual_kwh_ground_net`, `annual_kwh_ground_gain`, and `annual_kwh_ground_loss`.
   - The central database's `schema_version` goes up by one. A merge refuses databases of different versions with a message, as it refuses other mismatches.
6. **Tests, first.**
   - **`Lod.Export`:** the output requests on the snapshots, keyed by ground surface; a building with a multiplied ground floor.
   - **`Lod.Simulation`:**
     - the reader on small `.eio` and `.eso` fixtures: two ground surfaces in zones with multipliers 1 and 3, one paired floor left out, and the sum and sign;
     - a zero-ground building;
     - the missing variable;
     - the annual metrics with the zero cases.
   - **Runner:**
     - the scripted EnergyPlus writes the variable, and the series, table, and columns follow;
     - a merge across schema versions is refused.
   - **Opt-in EnergyPlus run:** the medium office F-factor set on a two-storey linear plan. The variable is present; G is negative in winter; and the `.eio`'s ground surfaces are exactly the IDF's.

### Part C: the batch runner, suites with constructions

1. **No change to the site record.** The IDF header's `! Site envelope:` line already names the set. A suite's constructions and ground method reach `central.duckdb` through the copied `test_cases` table, and `site_results` gains `constructions_kind`, `constructions_sha256`, `ground_method`, and `fill_from_example`. A plain IDF run (not a suite) keeps the envelope name only.
2. **Expected warnings.** None are added in advance. The pilot below runs every v7 ground method through `scripts/eplus-check` and the runner. Any new warning is added only with its reason and a decision (`scripts/eplus-check/README.md`).
3. **Tests.**
   - A suite with a construction set, run on the scripted EnergyPlus: `site_results` carries the new columns. A merge with a builtin-only suite keeps the builtin rows with `constructions_kind = builtin`.
   - **Opt-in:** a suite of the packet's medium office F-factor set (3B) and the warehouse set (3B), on a 3B weather file, through the runner on EnergyPlus 26.2:
     - every site succeeds;
     - the reference's comparison metrics are 0;
     - each test site's annual loads and annual ground heat transfer are reported against its reference.

     The weather file is the one the owner named on 2026-10-19: OpenEPW Las Vegas, Nevada (NSRDB GOES TMY v4.0.0, TMY 2025, climate zone 3B; SHA-256 `b94c04eeedd357a8…`), kept outside the repository. The test reads its path from `BEMGEN_WEATHER_3B` and is skipped without it, as without EnergyPlus.

### Part D: documentation

- The generator's and runner's READMEs, and the spec schema.
- `docs/research/experiment-outputs.md` (§1 or a new section for ground heat transfer, §8, and "What the IDF requests"), and `docs/architecture/convert2idf.md`.
- AGENTS.md's commands, ADR-020's consequences, and D-151.

## Construction files for suites

Packet v7's examples are mostly 3B, with residential sets in 1A, 4A, and 5A. A pilot in other climates needs construction JSON for its climate zones. The atlas's combined construction release 1.0.0 (`data/construction-foundation-releases/v1.0.0`, 177 suites and 3320 contexts) is internal storage. Its README says standalone documents come from its exporter: `--context-id ID --representation unified --output PATH`.

So:

- **Fetching.** The pilot's sets are exported by the owner, or by the build with the owner's yes. The export is written outside both repositories and modifies nothing in the atlas.
- **Storage.** The files sit next to the pilot spec, outside the repository, as the program files do. They are never committed (the packet's licence note).
- **Tests.** The repository's tests use only the pinned packet v7 fixtures.

## Order

1. Parts A and B, test-first, in parallel worktrees: A touches only `scripts/TestSuiteGenerator`, and B touches `Lod.Export`, `Lod.Simulation`, and the runner's series.
2. Part C, after both.
3. Review, `scripts/verify.ps1`, the opt-in EnergyPlus runs, Part D, and D-151.
4. Next stage: Program JSON 3.0.0, with its own note.

## Decided with the owner (2026-10-19)

1. **Base.** Packet v7 is merged into `main` (D-150). This stage builds on it.
2. **Pairing.** The generator pairs each construction set with the weather files of its climate zone. Climate must match the construction and its ground by design.
3. **Example windows over a non-absorbing ground floor.** The site is `Invalid` and not written.
4. **Programs.** The 3.0.0 files come from the atlas's `codex/foundation-ground` branch at `e9a982d`, read only.
5. **Ground output.** Add the hourly building-level ground heat transfer (Part B).
6. **Cleanup.** The v7 sibling branches are deleted and their worktrees deregistered.

## Build log (2026-10-19)

Parts A and B were built in parallel worktrees (`feature/suite-constructions`, `feature/ground-heat-transfer`) and merged into `feature/test-suite-generator`; Part C followed there.

**Deviations from the plan above, each with its reason:**

- **Construction URLs are fetched when the plan is made**, not only with `--write`: pairing needs the set's climate zone, which is inside the file. Program URLs still download only with `--write`.
- **Two more refusals before writing.** A set whose ground floor cannot be placed (`GroundMethodNotSupported`, `ConstructionBlocked`, or an uncovered ground without fill) is refused, since every building has ground floors (ADR-010) and every site would fail. A detailed document is refused (D-142).
- **The F/C-factor weather refusal is per paired weather file** without a full year of hourly records; a suite always has weather files.
- **`ground_method` has no `Mixed`.** The converter resolves one building-default ground recipe for a set and sets any other rule aside with `GroundAssignmentSetAside`, so no set gives more than one method.
- **Ground heat transfer counts `Ground` and `GroundFCfactorMethod` only** (`FCGround` in the `.eio`). `OtherSideCoefficients` is not counted: the `.eio` names only the coefficients object, so the reader cannot tell a ground use, and BEMGen writes none.
- **No export test with a multiplied ground floor:** the pipeline always splits the ground storey off at multiplier 1 (D-046). The multiplier is tested in the reader instead (zones with multipliers 1 and 3).
- **The research addition is experiment outputs §9**, not a section after §5, so that the many references to §6 to §8 stay valid.
- **The sign**, confirmed in the EnergyPlus 26.2 I/O reference and on runs: positive is heat conducted toward the zone through the inside face, negative heat leaving it. EnergyPlus does not apply the zone multiplier to surface outputs, so the reader does.

**Checks:**

- `scripts/verify.ps1` on each part's branch: `VERIFY PASSED`, 0 warnings.
- Part B's opt-in run (the medium office F-factor set, two storeys, the owner's Las Vegas file): 0 warnings, 0 severe; the `.eio`'s 6 ground surfaces equal the IDF's; annual G net −3715.2, gain 2946.9, loss 6662.1 kWh. `scripts/eplus-check` on that IDF: PASS, no new warning from the output requests.
- Part C's opt-in pilot (the F-factor medium office and warehouse sets, 3B, on the linear plan with storeys [1, 2, 1], 2 test cases of 8 sites, the owner's Las Vegas file): all 16 sites succeeded, each reference's comparison metrics 0. Example rows (annual total, change against the reference, ground net, in kWh):

  | Site | Total | Δ total | Ground net |
  | --- | --- | --- | --- |
  | Office reference | 249 806 | 0 | −3 935 |
  | Office, Perimeter Core + Stack, IWHT/FHT off | 261 508 | +11 702 | −3 762 |
  | Office, Perimeter Core + Single Zone Building (either heat-transfer setting) | 247 452 | −2 354 | −4 478 |
  | Warehouse reference | 256 811 | 0 | −4 140 |
  | Warehouse, Perimeter Core + Stack, IWHT/FHT off | 274 451 | +17 640 | −3 929 |

  These come from one synthetic plan and one weather file; they test the pipeline, and are not experiment results.
- A full opt-in `Lod.Simulation.Tests` run with a long output path failed two turned-court cases because EnergyPlus wrote no `eplusout.err`; with a short `BEMGEN_SIM_OUT` all four passed. Keep `BEMGEN_SIM_OUT` short on Windows.
