# ADR-020: Test suites, declared test cases, and a shared site ID

Status: Accepted (the owner's decisions of 2026-10-12, D-133 and D-134; the realisation by the controller, provisional pending the owner's reading)

Date: 2026-10-12

Decisions: D-016, D-064, D-111, D-124, D-126, D-130, D-132, D-133, D-134; new: D-135. Refines [ADR-019](ADR-019-simulation-ready-idf-and-runner.md) (the runner and its case record, now the site record).

Design note: [2026-10-12-test-suite-generator.md](../plans/2026-10-12-test-suite-generator.md) · Tool: TestSuiteGenerator (`scripts/TestSuiteGenerator/README.md`) · Runner: IdfBatchRunner (`scripts/IdfBatchRunner/README.md`) · Schedules: [schedule-generator requirement](../research/schedule-generator-requirement.md)

## Context

The batch runner (D-132) simulated any set of IDFs and inferred each test case from the IDF headers: the building, envelope, and weather lines. The study now needs suites of tens or hundreds of thousands of sites, generated from one spec, with every generation parameter queryable afterwards (D-133). Two facts made header inference insufficient:

- Two test cases can share a building, envelope, and weather and still differ, for example by window-to-wall ratio or program mix. Their headers would merge them into one, with two references.
- The analysis groups by generation parameters, such as geometry, storeys, programs, and climate zone. Most of these are not in the header, or only as unparsed provenance text.

## Decision

### The owner's decisions (2026-10-12)

1. **Terms.** Site, zoning, test case, reference site, and test suite replace "case" everywhere (D-133).
2. **The suite's tool.** One tool writes a suite's IDFs from a YAML spec and nothing else. The batch runner simulates them.
3. **The spec.** Axes combine in full factorial, with bundles, `range`, and `zip`. The plan is shown before anything is written. One generator per suite, and the same simplifier on every floor.
4. **The scale.** One table holds every test case, with structured parameter columns.
5. **Schedules.** The schedule generator is deferred to a recorded requirement (D-134).

### Realisation (controller, provisional)

- **Declared test cases.** The generator writes `suite.json`, listing every test case with its sites, its reference, and its weather file. The runner's `--suite` takes membership and references from it (`BatchPlan.CreateForTestCases`), not from the headers. Header inference (`BatchPlan.Create`) stays for plain IDF folders.
- **One site ID.** The site ID is the SHA-256 of the IDF bytes followed by the weather bytes (experiment outputs §7). The generator computes it when it writes each IDF, and the runner computes it again when it reads the file.
  - Equal IDs join the suite's tables to the runner's results without paths.
  - A site whose ID differs from the one the suite recorded is refused (`ModifiedSinceWritten`), so a hand-edited IDF never passes as the generated one.
- **IDs and paths.** A test case ID is 16 hexadecimal digits of the SHA-256 of its resolved inputs, labels excluded: 64 bits, so 100 000 test cases collide with a chance near 3 in 10⁹. A site's code is `R` for the reference, else 8 digits, with a collision within a test case refused. A site's IDF is `idf/<test case>/<code>.idf`, which keeps paths short on Windows.
- **The spec's checks.** YAML is typed by the YAML 1.2 core schema and checked against an embedded JSON Schema (JsonSchema.Net, already a dependency of `Lod.ProgramJson`); unknown keys are errors. What the schema cannot check (ranges, zips, mixes, ids, label sources, repeated zonings, the generator's parameters and slots) is checked before anything is written. `max_sites`, 20 000 by default, refuses an oversized suite.
- **The generator registry** binds a spec map to each generator's typed parameter and presets records, written out per generator; there is no reflection outside the tests, which check the binding against the records by reflection. *SteppedBand* waits for the spec of buildings whose floors differ.
- **The tables.**
  - `test_cases` has one typed column per geometry parameter (`geom_<name>`), program slot, and label.
  - `test_case_parameters` holds the same values as a long table, so that suites of different generators can be queried together.
  - The runner copies the suite's tables into its central database and adds any column a target lacks, both at a run and at a merge. The view `site_results` joins every site's metrics to its test case's parameters.
- **Programs** come from program JSON only. A slot is imported with the slot's space type, the test case's window-to-wall ratio, and the suite's calendar, or mixed by floor-area shares through `ProgramMix` (D-124). A URL program is pinned by its SHA-256 and kept in the suite's `inputs/`.
- **Climate zones.** Until program JSON metadata carries them, `programs.<id>.climate_zones` in the spec is the placeholder (D-133). A test case whose program does not apply in its weather file's zone is kept as `ExcludedByClimate` and not written.

## Options considered

- **Header inference for suites.** It is simple, but it merges test cases whose headers agree, and it leaves the parameters unqueryable. Rejected.
- **Extra header lines naming the test case.** These would need a change to *Convert2IDF*'s options for every IDF and still carry no parameters. A manifest beside the IDFs carries both. Rejected.
- **Test case IDs of 10 hexadecimal digits**, as the design note first sketched: at 100 000 test cases, a collision is near 0.5 % likely. Lengthened to 16.
- **Labels in the test case ID.** Two test cases differing only in labels would be two identical simulations. Labels are excluded, and such a spec is an error.
- **A provisional constructions file.** It was ruled out by the owner until the schema exists (D-134); the built-in example envelope is the only constructions.

## Consequences

- The runner has two planning paths: header inference for IDF folders, and declared test cases for suites. The not-run reasons are shared, and `ModifiedSinceWritten` is new.
- The central database gains `suites`, `test_cases`, `test_case_parameters`, `suite_sites`, and `site_results`; its schema version is 2. A central file of version 1 is refused.
- The IDF header's `! Case …` lines are `! Site …` lines (D-134); 6 IDF snapshots changed by those prefixes only.
- Buildings whose floors differ, the schedule generator, real constructions files, and HVAC systems remain open (D-133, D-134).
