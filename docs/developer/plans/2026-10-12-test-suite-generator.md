# Test suites: a generator of IDFs from a test-suite spec (design note)

> **Status:** Done (D-135; built 2026-10-12, not merged). Approved 2026-10-12 (the owner) · **Date:** 2026-10-12 · **Decisions:** D-016, D-064, D-111, D-126, D-130, D-132; new: D-133 and D-134 (the owner's answers, recorded), ADR-020 (at the build) · **Branch:** `feature/test-suite-generator` (from `feature/idf-batch-runner` `a9edab0`, which is not merged) · **Definitions:** [experiment outputs](../research/experiment-outputs.md) · **Runner:** IdfBatchRunner (`scripts/IdfBatchRunner/README.md`)

This is one stage run as D-111 sets out: this note first; one test-first build; a review of the diff by a second agent; `scripts/verify.ps1` before the merge; a decision-log entry and an ADR, because the stage changes what the study compares. No Grasshopper component changes, so the headless Rhino check is not needed. No GUID changes.

**Stop line.** The build ends with the branch verified, reviewed, and its documentation synchronised. It does not merge, tag, push, or release.

## Terms (the owner, 2026-10-12)

These replace the earlier use of "case" everywhere: in the code, the databases, the IDF header, and the docs.

- **Site.** One building in one zoning configuration, written as one IDF and simulated once. This is what experiment outputs, D-130, and the batch runner called a "case".
- **Zoning.** The plan simplifier with its options, the stacker (the floor aggregator), and the two heat-transfer options: *EnableInternalWallHeatTransfer* and *EnableFloorHeatTransfer*.
- **Test case.** One reference site and at least one test site that differ **only in zoning**. Everything else is fixed per test case and forms its identity: the generator and its geometry, the storey count, the programs, the window-to-wall ratio, the constructions, the weather, the calendar, and the labels. The storey count is fed to the stacker, but it is geometry, so two storey counts are two test cases.
- **Reference site.** The ground truth: *No Simplification*, *Stack*, both heat-transfer options on. It is always added, and it is never listed as a test site.
- **Test site.** Any other zoning of the test case's building, compared with its reference.
- **Test suite.** The test cases expanded from one test-suite spec (a YAML file). Test cases are independent of each other.

## The owner's answers (2026-10-12)

1. The batch runner switches to these terms before it merges; backward compatibility is waived (D-064).
2. Test sites differ only in zoning; the storey count separates test cases.
3. The reference is fixed, always added, and never a test site.
4. The heat-transfer options are a zoning axis.
5. **Combination rule.** A list is an axis, combined freely with every other axis; a map inside a list is one fixed bundle. A `range` and a `zip` are allowed. Each multiplies the sites, so the plan states the count before anything is written.
6. **Full factorial**, with no sampling of the axes. The tool shows the plan by default and writes only when asked. Seeded sampling exists only inside the coming ResStock/ComStock-style schedule generator: a draw is like another version of a program's settings.
7. **One plan generator per suite.** Buildings whose floors differ are deferred to another spec schema: mixed use, a few stacked floor types, and per-storey plans such as *SteppedBand*.
8. *SteppedBand* belongs to that deferred schema.
9. The same simplifier on every floor.
10. A site that fails validation is recorded and skipped. A test case whose reference fails is dropped. Validation is never overridden.
11. A program JSON may be a local file or a URL. The two are expected to merge later.
12. **No program presets.** Every program comes from a program JSON.
13. Climate zones a program applies to will come from the program JSON's metadata; until then a placeholder in the spec stands in for it, documented as such.
14. One calendar per suite, default year 2007.
15. A slot may take a weighted mix of programs.
16. A schedule draw is part of the test case; all sites of a test case use the same draws.
17. Schedules are drawn per zone.
18. **Schedule generation.** A program setting (with its schedule-generation parameters), a schedule-generator setting, and a seed give one program JSON with generated schedules. The spec names the program setting, the schedule generator, its parameters, and the seed.
19. Constructions will be files like the envelope presets; their schema is not defined yet. Vintage is only a tag.
20. **Systems are out of scope.** HVAC stays ideal loads.
21. Labels are only tags.
22. Weather files go in a folder the tool defines, named by climate zone and location, or mapped by a registry file in that folder.
23. **This tool writes IDFs only.** It replaces the Grasshopper workflow for suites, and the batch runner simulates them.
24. `discard_ep_results` keeps only `central.duckdb`, `batch.json`, and the IDFs.
25. Test cases and sites are named by short IDs, mindful of Windows' path length limit.
26. The spec has a version, unknown keys are errors, and the YAML is checked against a schema.
27. **Scale: 100 000 sites or more.** One table holds every test case as a row, and the generation parameters are structured columns. Queries such as "group by x, y, z, and show the distribution or the median of the error in column c" must be direct.
28. D-133, ADR-020, and this note come before the code.

**Second answers (2026-10-12):**

29. The IDF header's `! Case …` lines become `! Site …`.
30. The window-to-wall ratio is a suite axis.
31. Labels attach to bundles, such as a constructions entry carrying `vintage`. A label axis is an error.
32. Storeys are written as explicit floor entries (`[1, 6, 1]`) or as a count N: a ground floor, N − 2 typical floors, and a top floor. A count of 1 or 2 means that many single floors.
33. The schedule generator runs **once per test case**, and the schedules it generates are per zone. Zones take shifted seeds, so that units of the same type do not all get the same schedule. Every site of a test case shares the same schedule sources; a simplified site's actual schedules may still differ, because its merges aggregate them.
34. Constructions are the built-in example envelope only, until their schema exists.
35. `max_sites` defaults to 20 000.
36. The tool is `scripts/TestSuiteGenerator`.
37. **The schedule generator is not designed in this stage.** Its requirement is recorded ([schedule-generator requirement](../research/schedule-generator-requirement.md), D-134). Programs and their schedules are used as their program JSON defines them, so answers 16 to 18 and 33 wait for that design. The spec has no schedule section and no seed.

## The spec (version 1)

```yaml
spec_version: 1
suite_id: linear-pilot                  # [a-z0-9-], at most 24 characters; part of the output folder's name
settings:
  calendar: {year: 2007, holidays: []}  # one per suite (answer 14)
  discard_ep_results: true              # written to suite.json for the runner (answer 24)
  max_sites: 20000                      # the tool refuses to write a larger suite unless this is raised

programs:                               # id -> program JSON; a file next to the spec, or a URL with its SHA-256
  dwelling-mf: {program_json: programs/dwelling-mf.json, climate_zones: [4A, 5A]}   # climate_zones: a placeholder until program metadata carries it (answer 13)
  dwelling-sf: {program_json: https://example.org/dwelling-sf.json, sha256: 3f2a…}
  corridor:    {program_json: programs/corridor.json}
  stair:       {program_json: programs/stair.json}

constructions:                          # id -> constructions file (schema to come, answer 19), plus tags
  example: {builtin: Example, labels: {vintage: example}}   # ExampleEnvelopePresets.Example; the only kind until the schema exists (answer 34)

weather:
  registry: default                     # the registry in the weather folder (below)
  select: [{climate_zone: 4A}, {climate_zone: 5A}]  # or {id: ...}; a file selected twice counts once

labels: {study: pilot-1}                # suite-wide tags; a bundle may carry its own (answers 21 and 31)

building:
  generator: LinearPlan                 # one per suite (answer 7)
  geometry:                             # a list of bundles, each a full parameter record
    - {Length: 24, UnitDepth: 8, CorridorWidth: 2, TargetUnitWidth: 10, StairLength: 4, FloorHeight: 3, OrientationDegrees: 0}
    - {Length: {range: {from: 30, to: 60, step: 15}}, UnitDepth: 8, CorridorWidth: 2, TargetUnitWidth: 10, StairLength: 4, FloorHeight: 3, OrientationDegrees: [0, 90]}
    - zip: {Length: [24, 36], TargetUnitWidth: [8, 12]}
      with: {UnitDepth: 8, CorridorWidth: 2, StairLength: 4, FloorHeight: 3, OrientationDegrees: 0}
  storeys: [[1, 2, 1], 8]               # floor entries bottom to top, or a count: 8 means [1, 6, 1] (answer 32)
  programs:                             # a list of bundles: one program (or a mix) per slot of the generator
    - {DwellingUnit: dwelling-mf, Corridor: corridor, Stair: stair}
    - {DwellingUnit: {mix: {dwelling-mf: 0.7, dwelling-sf: 0.3}}, Corridor: corridor, Stair: stair}
  window_to_wall_ratio: [0.3, 0.4]      # a suite axis (answer 30)
  constructions: [example]

zoning:                                 # the test sites; the reference is added by the tool (answer 3)
  simplifiers:
    - NoSimplification
    - {SemanticMerge: {JoinPieces: [false, true]}}
    - {ConditionedMerge: {JoinPieces: [false, true]}}
    - {PerimeterCore: {PerimeterDepth: [3.0, 4.57]}}
    - SingleZonePerFloor
  stackers: [Stack, StackedFloorZoneMultiplier, SingleZonePerFloorType, SingleZoneBuilding]
  heat_transfer: [{iwht: false, fht: false}, {iwht: true, fht: true}]
```

**Expansion.**

- **Test cases:** geometry × storeys × programs × WWR × constructions × weather. Combinations a program's climate zones exclude are then removed.
- **Sites per test case:** the reference, plus simplifiers × stackers × heat transfer, minus the reference's own combination when the axes contain it. The reference is never listed twice.

The example gives 1 + 6 + 2 = 9 geometries: the `range` bundle expands to 3 lengths × 2 orientations, the `zip` to 2. With one weather file in each of the two zones:

| Axis | Count |
| --- | --- |
| Geometry | 9 |
| Storeys | 2 |
| Programs | 2 |
| WWR | 2 |
| Constructions | 1 |
| Weather | 2 |
| **Test cases** | 9 × 2 × 2 × 2 × 1 × 2 = **144** |
| Sites per test case | 8 simplifier variants × 4 stackers × 2 heat-transfer settings = 64. The reference is one of these combinations, so it is listed once: 1 reference and 63 test sites. |
| **Sites** | **9 216** |

A second constructions entry and a third weather file would give 432 test cases and 27 648 sites. That is over `max_sites`, so the tool would refuse to write it, and the plan would say which axes drive the count. This is the guard answer 5 asks for.

**Rules checked before anything is written:**

- Every key is known to the schema. A label given as a list is an error (answer 31).
- Every geometry bundle is a complete parameter record of the generator. Every slot of the generator has a program, and no other slot does.
- Every id resolves, every file exists, and every URL has a SHA-256 that matches.
- Mix weights are positive and sum to 1. Each program's space type matches its slot (D-126).
- A `range` has a positive step and divides its span within the central tolerance. A `zip`'s lists have equal lengths.

## Weather folder

`--weather-root`, else the environment variable `BEMGEN_WEATHER_ROOT`, names a folder outside the repository with a `registry.json`:

```json
{"files": [{"id": "chicago-ohare-tmy3", "file": "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw", "climate_zone": "5A", "location": "Chicago O'Hare, IL"}]}
```

- The tool computes each file's SHA-256, so the case record and the test case table carry it.
- A file missing from the folder is an error. So is a registry entry without a climate zone.
- The zone system is the one the registry uses; nothing is inferred from an EPW header.

## Schedules

Not designed in this stage (answer 37). Each zone takes the program of its slot, or the slot's mix, with the schedules its program JSON defines. That is what the pipeline does today. The requirement for the coming generator is recorded in [schedule-generator-requirement.md](../research/schedule-generator-requirement.md).

## Output

`--out`, else the environment variable `BEMGEN_SUITES_ROOT`, names the root (never inside the repository):

```text
<root>/<suite_id>-<yyyyMMdd-HHmmss>/
  spec.yaml            the spec as given
  inputs/              every program, constructions file, and URL download, by SHA-256
  suite.json           the manifest the batch runner reads: suite, spec SHA-256, code version, and every test case with its sites and IDF paths
  suite.duckdb         the tables below
  idf/<tc>/<site>.idf  tc: 10 hexadecimal digits of the test case ID; site: R for the reference, else 6 of the site ID
```

A path stays near 80 characters below the root. IDs are the leading hexadecimal digits of SHA-256 hashes of the resolved inputs: of the test case's inputs, and of the test case ID plus the zoning. The same spec with the same inputs writes the same files.

**The batch runner reads `suite.json`.** Membership becomes explicit, not inferred from header lines, so two test cases cannot be confused. It copies the suite's tables into its `central.duckdb`, so the central database stays self-contained. It honours `discard_ep_results`.

### Tables (answer 27)

`test_cases`: one row per test case.

- **Columns:**
  - `test_case_id`, `suite_id`, `status` (`Written`, `ReferenceInvalid`, `ExcludedByClimate`), `message`;
  - `generator`, then one typed column per geometry parameter (`geom_length`, `geom_unit_depth`, …);
  - `storeys` (`1,2,1`), `storey_count`;
  - `program_<slot>` (an id or a mix such as `dwelling-mf:0.7;dwelling-sf:0.3`), `program_<slot>_sha256`, `window_to_wall_ratio`, `constructions_id`;
  - `weather_id`, `climate_zone`, `location`, `weather_sha256`, `calendar_year`;
  - `label_<key>` per label;
  - `reference_site_id`, `site_count`.
- **Plus:** `test_case_parameters` (`test_case_id`, `name`, `value_number`, `value_text`): the same values as a long table. Suites of different generators have different `geom_` columns, so this table lets them be queried together. Their `test_cases` tables also combine with DuckDB's `UNION ALL BY NAME`.

`sites`: one row per site.

- **Columns:** `site_id`, `test_case_id`, `is_reference`, `simplifier`, `join_pieces`, `perimeter_depth`, `stacker`, `iwht`, `fht`, `idf_path`, `status` (`Written`, `Invalid`), `message`, `zone_count`.

**Joining the results.** In the runner's `central.duckdb`, a view `site_results` joins `sites`, `test_cases`, and the metric columns. The owner's example query becomes:

```sql
SELECT climate_zone, simplifier, stacker, median(total_cvrmse), quantile_cont(total_cvrmse, [0.1, 0.5, 0.9])
FROM site_results WHERE NOT is_reference GROUP BY ALL
```

## Where the code goes

| Part | Project | Contents |
| --- | --- | --- |
| 0. Terms | `Lod.Simulation`, `Lod.Export`, `scripts/IdfBatchRunner`, docs | Case → site and group → test case. This covers types (`CaseRecord` → `SiteRecord`, `CaseMetrics` → `SiteMetrics`), plan statuses, database columns, the IDF header lines (`! Case …` → `! Site …`, answer 29, 19 snapshot files), and experiment outputs §7. No research definition changes. |
| B. Spec | `scripts/TestSuiteGenerator` | YAML (YamlDotNet, MIT, this tool only), the JSON Schema, the expansion (axes, bundles, `range`, `zip`, mixes, storey counts, the climate filter), counts, and IDs. |
| C. Registries | `scripts/TestSuiteGenerator` | Generator, simplifier, and stacker by name. Explicit per-generator binding from a YAML map to its typed parameter record and slots: 17 generators, *SteppedBand* deferred. No reflection (AGENTS code style). |
| D. Inputs | `scripts/TestSuiteGenerator` | Program JSON (`ProgramJsonImporter`, the suite calendar, the slot's space type and WWR), URL download with SHA-256, constructions (the built-in example only, answer 34), and the weather registry. |
| E. Writing | `scripts/TestSuiteGenerator` | Per test case: generate and assign the slot programs, then for each zoning simplify, stack, and `Convert2Idf`. Then `suite.json`, `suite.duckdb`, and the IDFs; in parallel across test cases, written in ID order. |
| F. Runner | `scripts/IdfBatchRunner` | Read `suite.json`; copy the suite's tables into `central.duckdb`; the `site_results` view; `discard_ep_results`. |
| G. Tests | `tests/TestSuiteGenerator.Tests`, and the existing projects | Expansion counts and orders, every validation rule, IDs stable across runs and input order, a mixed slot's programs, and one small suite written and read back. One opt-in suite run through the batch runner on EnergyPlus. |

## Settled with the owner (2026-10-12)

1. The note is approved for the build.
2. The placeholder for a program's climate zones is the spec's optional `programs.<id>.climate_zones`; a program without it applies in every climate zone.


## Build log (2026-10-12)

Built on `feature/test-suite-generator`, test-first, in the order of [Where the code goes](#where-the-code-goes). The case → site rename was built by a second agent in a separate worktree. A guard of the session kept it from writing there, so its finished code changes were applied here as a patch, and the rest of part 0 was completed here.

**What differs from the note, and why:**

- **ID lengths.** The note set 10 hexadecimal digits for a test case ID; the build uses **16**. At 100 000 test cases, 10 digits (40 bits) collide with a chance near 0.5 %, and 16 digits with a chance near 3 in 10⁹. Site codes are **8** digits rather than 6; a collision within a test case is refused.
- **The site ID** is the experiment outputs' SHA-256 of the IDF and weather bytes, computed by the generator when it writes and again by the runner when it reads. It joins the suite's tables to the runner's results without paths, and the runner refuses a site whose ID changed after it was written (`ModifiedSinceWritten`).
- **Labels are not part of the test case ID.** They are tags, so two test cases differing only in labels would be one simulation twice; such a spec is an error.
- **Runner site names** are `<test case>/<site code>`, so each site's EnergyPlus folder sits in its test case's folder.
- **The central database** keeps the suite's tables as `suites`, `test_cases`, `test_case_parameters`, and `suite_sites` (the suite's `sites` table, renamed so it does not collide with the runner's results), with the view `site_results`. Columns a target lacks are added, at a run and at a merge, so suites of different generators combine. Its schema version is 2, and version 1 files are refused.
- **The snapshots.** 6 IDF snapshots carry the header lines, not about 19; they changed by the four prefixes only.
- **A test case that cannot generate** (a generator or program error) is `GenerationFailed`, a status the note did not list.
- **`LinearPlanParameters` has no `Default`**, unlike the other 17 records. The registry test uses the canonical linear plan for it.
- **YamlDotNet** refuses a repeated key itself; the tool's own check of repeated keys stays as a second line.

**Checks:**

- `scripts/verify.ps1`: VERIFY PASSED with 0 warnings: 629 core, 518 generator, 160 program JSON, 1382 export, 2726 integration, 180 simulation, 89 test-suite generator, and 52 batch-runner tests; the 7 opt-in EnergyPlus tests skipped.
- The opt-in tests (`BEMGEN_ENERGYPLUS=D:\EnergyPlusV26-2-0`, EnergyPlus 26.2.0 build `4bd7a1f26f`) passed:
  - the earlier batch of four IDFs;
  - a suite written by the generator: the linear plan (1, 2, 1) with the Medium Office program in every slot, the installation's Chicago TMY3 file, and 8 sites. All 8 ran and succeeded, the reference first; `site_results` gave all 8 with their parameters, and the reference's comparison metrics are 0.
- The developer pages' links check passes.
- **The review by a second agent** found no blocking bug, and confirmed that the rename changes only names and wording. Its points, each fixed or recorded here, with tests:
  1. The test case ID named the constructions entry, not its content, so two entries of one envelope wrote identical IDFs twice. It now holds the content, and such a spec is refused as the same inputs.
  2. A declared reference that duplicates an earlier site let its test sites run with no reference. Duplicates are now settled first, and such test sites are `NoReferenceSite`.
  3. A mix of one program was accepted. A mix now names at least two programs (the schema).
  4. Programs were fetched only after the suite folder existed. Every program is now fetched, checked against its SHA-256, and imported for each slot and window-to-wall ratio before anything is written; a program that cannot be imported stops the suite (exit code 2).
  5. The note's example query grouped by `stacker`, which `site_results` lacked. The view now carries `suite_sites`' `site_code`, `stacker`, `join_pieces`, and `perimeter_depth`.
  6. `discard_ep_results` also deleted the folders of failed sites. Those are now kept, so their `eplusout.err` can be read.
  7. The holidays' order changed the test case ID. They now enter it sorted and without repeats.
  8. A range with a tiny step overflowed. A range of more than 1 000 000 values is now refused before it expands.
  9. `InternalsVisibleTo` was listed twice in the project.
  10. Added tests:
      - a test site that cannot be simplified (`Invalid`, the test case still written);
      - a test case the generator refuses (`GenerationFailed`);
      - a program that cannot be imported;
      - URL downloads with a matching, a mismatching, and an unreachable source;
      - a resumed suite run;
      - a merge of suites of two generators.

      Not covered by a test: a reference that fails *Convert2IDF*'s validation, because no input of the 17 generators is known to make the reference alone fail; the code drops such a test case as `ReferenceInvalid` and deletes its folder.

**Open:**

- The second worktree `D:\BEMGen\.claude\worktrees\suite-rename` (branch `feature/suite-rename`) held the rename agent's uncommitted copy of part 0, all of it in this branch. The owner allowed its removal (2026-10-12). By then the worktree, its folder, and its branch were already gone.
- Buildings whose floors differ (*SteppedBand*, mixed use), the schedule generator, constructions files, and HVAC systems wait for their own designs (D-133, D-134).
