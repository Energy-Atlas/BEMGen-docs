# ADR-032: DOE prototype suites and pinned study inputs

- **Status:** Provisional (D-185); the owner reviews the study choices it carries (D-186)
- **Date:** 2026-10-29
- **Context:** [run plan](../plans/2026-10-29-lod-study-run-plan.md) §3, D-133, D-171, D-172, D-179, ADR-025

## Context

The geometric LOD study runs the DOE/PNNL prototypes at their own dimensions, with the atlas release 2.0.0 programs and constructions of each vintage and climate zone, through the test-suite generator and the batch runner. The generator knew only the 17 single-plan generators, one program per slot of a fixed preset record, one plan for every floor entry, programs imported without a climate zone, and glazing only as a scalar ratio. The atlas inputs are hundreds of files (366 for the main study), too many to commit, and the atlas's names for three record keys differ from the records'.

## Decision

1. **A DOE building block.** A spec's `building` is either a generated building or `doe`: a list of prototypes (a `DoeBuildingType`), each with its orientations and its vintages. Every other parameter is the layout record's (`Default` of the generator's typed record), so a test case is the prototype at its source dimensions, storeys, and floor heights. Each storey plan is simplified on its own and stacked with the storeys it stands for, read from its `StoreyMultiplier` provenance (ADR-015).
2. **Programs per program key.** A vintage gives a program, or a floor-area mix, for every program key of the record and no other key; the plan refuses a missing or unknown key. The zones take these imported programs through a `DoeProgramMap`; the illustrative presets (D-171) are used only to read a record's storeys and glazing, never for loads.
3. **Glazing.** `window_to_wall_ratio` is an axis of numbers, `program` (each JSON's `fenestration`), or, in a DOE building, `record`, the layout record's own WWR per orientation and skylight ratio of each key (D-162, D-163), the default there.
4. **Climate zone and context.** Every program is imported for the climate zone of its test case's weather file and with the spec's optional `program_context`, so by-climate values are the zone's own.
5. **Floor research gate.** `settings.floor_research_gate` is `off`, `report` (each site's verdict recorded in `sites`, nothing blocked), or `require` (passed to `Convert2Idf`, a failing site `Invalid`). The gate's rules are unchanged.
6. **Pinned inputs outside the repository.** The atlas inputs are exported by `scripts/lod-study/export_inputs.py` from an atlas checkout with the atlas's own exporter into a folder outside the repository; the committed manifest pins each file by SHA-256 and size. The stage specs are generated from the manifest and the study file only (`make_specs.py`) and pin every input; the generator reads them with `--inputs-root`. The weather files are pinned in a committed lock, and a registry `sha256` is checked by the generator.

## Consequences

- One suite spec holds the whole study matrix; the test case ID holds the prototype, orientation, storeys, every key's program by SHA-256, and the glazing, so the same spec writes the same suite.
- DOE suites have no `program_<slot>` columns; `program_map` holds the programs. `sites` gains the gate's verdict columns; earlier suites' IDs are unchanged (the program context enters the ID only when given), but their IDFs now record the climate zone of each program's import.
- The spec's zonings stay a full factorial, so the plan's 18 main zonings become 24 (D-186).
- The inputs folder must be exported before a stage runs; `--check` modes of both scripts compare a fresh export and the specs with the committed manifest and specs.
- The record-key aliases and the 90.1-2007 small-hotel set are study data in `research/lod-study/study.json`, not code, and are listed for the owner.
