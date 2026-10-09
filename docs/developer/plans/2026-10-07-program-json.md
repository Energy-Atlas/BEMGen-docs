# Program presets from program JSON 2.0.0, and retiring the atlas fetch components (design note)

> **Status:** Done (D-126; released in version 1.2.0, D-127). Approved 2026-10-07 (the owner) · **Date:** 2026-10-07 · **Decisions:** D-009, D-023, D-038, D-047, D-064, D-111, D-122 (archived), D-124; new: D-126, ADR-018 · **Branch:** `feature/program-json` (worktree `D:\worktrees\program-json`, from `main` `0d301c5`) · **Target version:** 1.2.0

This is one stage run as D-111 sets out: this note first; one test-first build on the branch, with independent parts in parallel; a review of the diff by a second agent; the headless Rhino check once; `scripts/verify.ps1` before the merge; one decision-log entry (D-126) and an ADR (ADR-018), because the stage changes the program model and the equivalence rules. It breaks existing definitions where the section "Breaking changes" says so (D-064). No component GUID changes.

**How the build runs.** After the owner approves this note, the build runs without supervision. Every finding, deviation, and open issue goes into the section "Build log" at the end of this note as it happens, and the report at completion summarises it. Where the note leaves a choice open, the build takes the rule under "Fallbacks" and logs it.

**Stop line.** The build ends with the branch complete: verified, reviewed, smoke-checked, its documentation synchronised on the branch. It does **not** merge to `main`, tag, push, export the public docs, or publish a release; those wait for the owner (AGENTS.md: pushes only with the owner's approval). The archive tag of Part A stays local.

## Problem

The atlas now publishes a self-contained program contract, *program JSON 2.0.0* (`D:\archetype-atlas`, read-only): a program's loads, controls, and every schedule they use in one JSON object, in `raw` or `defaulted` mode, with the defaults already applied by the atlas exporter under the policy `atlas-program-defaults-1.0.0`. The owner wants:

1. **The atlas fetch components retired**, with no backward compatibility: the S10 work on `feature/archetype-data` (D-122, ADR-016), which resolves, downloads, and verifies atlas snapshots.
2. **One parser component** that turns a program JSON into a ready-to-use program preset.

The contract describes more of a program than BEMGen holds. The owner decided (2026-10-07) that BEMGen's program model grows to hold it.

### The owner's answers

- **Component inputs:** JSON *text* (no file path, no network), plus inputs that complete or override the JSON: a *WWR* with an ordinary default (0.4), and loads the JSON lacks (such as ventilation).
- **Model extensions:** a per-dwelling-unit basis; the people activity schedule, radiant fraction, and sensible fraction; two lighting loads (end uses); heating and cooling switched on separately, each with its setpoint schedule; hot-water target and inlet temperature schedules; and, from the review, power-load heat fractions.
- **Per-dwelling loads merge by dwelling count.** The owner first chose floor-area weighting (1b); after the conflict with GLOBAL.md scientific rule 1 was raised, the owner chose weighting by dwelling count, since BEMGen can track the number of dwellings (see "Per-dwelling loads and GLOBAL.md scientific rule 1").
- **Shared services are not added.**
- **Sensible fraction:** a merge of `autocalculate` with a number gives `autocalculate` with a warning (2b). The other merge rules proposed stand (they were not contested).
- **An override load** replaces the JSON loads of the same type and end use, or is added; *Load* gets an *End Use* input (3a).
- **Calendar:** *Year* (default 2007) and *Holidays* inputs; a leap year is an error (4a).
- **Design-day rules** are checked but not used (5a).
- **Retirement:** port what is reusable, tag the old branch as an archive, delete it (6a).
- **Validation:** bundle a JSON Schema library (7b).
- **Atlas files:** the two schemas and the Medium Office example may be committed (8b).
- **Release:** one stage for version 1.2.0 (9a).

## Per-dwelling loads and GLOBAL.md scientific rule 1

Rule 1 says simplified models preserve installed power. Merging per-dwelling loads by floor area would not, when the merged dwellings differ in size: an 80 m² and a 40 m² dwelling at 100 and 400 W/dwelling hold 500 W, and the area-weighted 200 W/dwelling × 2 gives 400 W. The conflict was raised and the owner decided (2026-10-07): **weight by dwelling count**, value* = Σ fᵢ·Nᵢ·vᵢ / Σ fᵢ·Nᵢ, which conserves installed and scheduled power like every other basis (250 W/dwelling × 2 = 500 W in the example). No exception to rule 1 is needed. The dwelling count is tracked exactly (Part B.1), and the building's total dwelling count becomes a conservation invariant.

## Part A: retire the atlas fetch components

1. **Archive.** Tag `feature/archetype-data` (`cf88cee`) as `archive/archetype-data` (local, annotated, naming D-126), remove its worktree `D:\worktrees\archetype-data` (if Visual Studio locks files, log it and leave the folder), and delete the local branch. The branch is not on `origin`, so nothing is pushed.
2. **Nothing to remove from `main`.** The atlas code was never merged. `main` holds one piece of it, `ProgramPreset.Source`, which stays: the JSON preset fills it.
3. **Retired identities.** The GUIDs of the three atlas components (`c231969e-a062-4f0b-a2b4-45ca60b7cc3e`, `ec2037f0-b14e-432b-a907-23a6e4566e94`, `43b5b5c4-b180-4be5-94ce-74d982640fd9`) and of the *Atlas Snapshot* parameter are listed in D-126 as never to be reused. The examples `atlas-office-plate.gh` and `atlas-explorer.gh` go with the branch.
4. **Ported, adapted, not merged:** the ruleset expansion and its calendar (`Lod.Atlas/Schedules`) and the strict JSON reading (duplicate keys rejected). The port checks the precedence against the 2.0.0 rule, `last_specific_match_else_last_default`, and its tests are rewritten for the 2.0.0 shape. Everything else (transport, snapshots, caches, resolver, the presets builder) is not ported.
5. **Records.** D-126 retires D-122 and ADR-016 (they exist only in the archive tag; `main`'s log gets no D-122 entry and the number stays unused), and the roadmap marks S10 as retired.

## Part B: program model extensions (`Lod.Core`)

All defaults below are the values the IDF writer uses today (`IdfDefaults`), so BEMGen's own presets give the same heat behaviour as before unless a value is set.

1. **Per-dwelling-unit basis.** `LoadBasis.PerDwellingUnit`, appended to the enum. Magnitude = value × the zone's dwelling count.
   - `ZoneMeasures` gains `DwellingUnits`. A generated zone of space type `DwellingUnit` counts 1 (a dwelling is one zone, never subdivided, D-009); every other zone counts 0. A target zone counts Σ fᵢ·Nᵢ of its sources, so a perimeter-core split gives fractional counts.
   - Occupancy may be per dwelling (person/dwelling).
   - A zone with a per-dwelling load and no dwellings is a validation error (`PerDwellingWithoutDwellings`).
2. **End uses.** `LoadDefinition.EndUse`, a non-empty text such as `lighting` or `additional_lighting`. Its default is the type's snake-case name (`occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water`, `ventilation`), the names the contract uses. A program holds at most one load per **type, end use, and basis**, which supersedes D-047's type and basis. Components merge by that triple.
3. **Heat fractions** (`HeatFractions`: radiant, latent, lost, visible, return air; convective is what remains; each in [0, 1], sum ≤ 1 within the central tolerance) on lighting, electric equipment, and gas equipment loads, and only on them. EnergyPlus `Lights` has no latent or lost field and `ElectricEquipment`/`GasEquipment` no visible or return-air field, so a non-zero value in a field the object lacks is an error, not dropped. Defaults: lights radiant 0.42, visible 0.18, return air 0; electric equipment radiant 0.5; gas equipment radiant 0.3; the rest 0.
4. **People properties** on `ZoneProgram` (`PeopleProperties`): an activity schedule (new `ScheduleKind.Activity`, W/person, ≥ 0), a radiant fraction of sensible heat in [0, 1], and a sensible fraction that is a number in [0, 1] or `autocalculate`. Defaults: constant 120 W/person, 0.3, `autocalculate`.
5. **Heating and cooling separately.** `Thermostat` holds an optional heating and an optional cooling setpoint schedule, at least one. A zone is conditioned when it has either. Where both exist, the heating setpoint must not exceed the cooling setpoint at any hour (`SetpointsCross`, an error).
6. **Hot-water temperatures.** A `DomesticHotWater` load holds a target and an inlet (cold-water) temperature schedule, °C, with the target not below the inlet at any hour. Defaults: constant 60 and 10 °C.
7. **Calendar.** `ScheduleCalendar` (a non-leap year and its holidays). A program preset may record the calendar its schedules were expanded on (`ProgramPreset.Calendar`; `null` for BEMGen's own presets, which assume a year starting on Monday). The building's presets must agree on one calendar (validation error `CalendarMismatch`), and the export uses it (Part G).

## Part C: aggregation rules (zone merges and *Mix Programs*)

The aggregator (`EquivalentPropertyAggregator`, ADR-005, ADR-007) keeps its form: source *i* transfers Tᵢ = fᵢ·Qᵢ of each component, Q* = ΣTᵢ, value* = Q*/B*. *Mix Programs* stays the same merge on a virtual zone of unit area (D-124), so it inherits every rule. New and changed rules, each recorded in `AggregationRecord`s and in the research brief (GLOBAL.md scientific rule 7):

| Quantity | Rule | Zero guard |
| --- | --- | --- |
| Per-dwelling component | value* = Σ fᵢ·Nᵢ·vᵢ / Σ fᵢ·Nᵢ (the basis quantity is the dwelling count, so the general rule Q*/B* gives it); schedule weighted by fᵢ·Nᵢ·vᵢ. In *Mix Programs*, which has no dwellings, each weight stands for the input's share of dwellings, as it stands for its share of floor area: value* = Σ ŵᵢ·vᵢ | zero magnitude: value 0, constant zero schedule, as today |
| Heat fractions of a component | each fraction weighted by Tᵢ, so installed radiant, latent, … power is conserved | Q* = 0: weighted by fᵢ·Aᵢ |
| Activity | a*(t) = Σ oᵢ(t)·aᵢ(t) / Σ oᵢ(t), oᵢ(t) the transferred scheduled occupants, so people heat is conserved every hour | an hour without occupants: weighted by transferred design occupants; no occupants at all: by fᵢ·Aᵢ |
| People radiant fraction | weighted by transferred design occupants | no occupants: by fᵢ·Aᵢ |
| People sensible fraction | all `autocalculate`: `autocalculate`; all numbers: weighted by design occupants; a mixture: `autocalculate` and a warning (2b) | as radiant |
| Hot-water target and inlet | each weighted by the transferred scheduled flow every hour, so the water heat Σ qᵢ(t)·(T_target − T_inlet) is conserved | an hour without flow: by transferred design flow; no flow: by fᵢ·Aᵢ |
| Heating setpoint | over the sources with heating on, floor-area weighted (ADR-005); on when any source has it on | — |
| Cooling setpoint | the same, over the sources with cooling on | — |
| Setpoints after a merge | a merge whose heating exceeds its cooling at any hour is an error naming the sources, since EnergyPlus rejects it | — |

Loads of the same type with different end uses stay separate, like different bases today. The calendar passes through; sources with different calendars are an error.

## Part D: the program JSON library (`Lod.ProgramJson`)

A new library, `net7.0` like the plugin, depending on `Lod.Core` and the JSON Schema library; `Lod.Core` stays BCL and Clipper2 only. `ProgramJsonReader.Read(string json, ProgramJsonOptions options)` returns `Result<ProgramJsonImport>`: the preset and a report. Each step's failure is a structured diagnostic with a JSON Pointer.

1. **Strict parse.** UTF-8 JSON, duplicate object keys rejected (ported), size bound in the central tolerances or limits.
2. **Schema validation** against `program-json-v2.schema.json`, embedded as a resource exactly as the atlas publishes it (8b), Draft 2020-12. Every schema error is reported with its instance path.
3. **Mode.** `raw` is rejected with "export the defaulted form"; only `defaulted` is accepted.
4. **The contract's extra checks:**
   1. every schedule key equals its object's `id`, and every reference resolves;
   2. schedule units by role: load schedules `1`, setpoints and water temperatures `degC`, activity `W/person`; anything else is rejected, not coerced;
   3. real MM-DD dates checked on a leap-capable reference year; rule order kept; every day of the model year covered (an error), design-day coverage checked (a warning, Part D.6);
   4. annual schedules: length matching their year's leap status, every annual year equal to the calendar's *Year*;
   5. heat fractions sum ≤ 1; heating ≤ cooling every hour of the expanded year; water target ≥ inlet every hour;
   6. no demand instantiated twice: loads sharing a `demand_id` are kept once if identical and are an error if they differ.
5. **Expansion to 8760 values** on the calendar (*Year*, *Holidays*).
   - **Ruleset:** for each date, the effective day type is `Hol` on a holiday, else the weekday. Rules are scanned in array order, never sorted; the last matching specific rule wins (`Wkdy` matches Mon–Fri, `Wknd` Sat–Sun, `Hol` only holidays), else the last matching `Default`; none is an error. A start date later than the end date wraps New Year. One value is constant, 24 values hourly, stepwise.
   - **29 February in a non-leap year** (the contract is silent): a rule starting on 02-29 starts on 03-01 and one ending on 02-29 ends on 02-28, with a warning. Logged as a contract gap for the atlas.
   - **Annual:** taken as is, local standard time, never resampled or moved to another year.
   - **Design days** (`WntrDsn`, `SmrDsn`) are not days of the model year; their coverage is checked and their profiles are not used (5a). The IDF keeps giving design days the Sunday schedule.
6. **Mapping to the program model:**

   | Contract | BEMGen |
   | --- | --- |
   | `occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water` | `Occupancy`, `Lighting`, `ElectricEquipment`, `GasEquipment`, `DomesticHotWater` |
   | `end_use` | `EndUse` |
   | basis `floor_area`, `dwelling_unit`, `person`, `absolute` | `PerFloorArea`, `PerDwellingUnit`, `PerPerson`, `Absolute` |
   | m³/s (per m², dwelling, person, or absolute) | m³/h, × 3600 |
   | person/m², person/dwelling, person; W/… | unchanged |
   | `heat_fractions` | `HeatFractions` |
   | `controls.heating_enabled`, `cooling_enabled`, setpoint schedules | `Thermostat` sides |
   | `activity_schedule_id`, `people_radiant_fraction`, `people_sensible_fraction` | `PeopleProperties` |
   | `target_temperature_schedule_id`, `inlet_temperature_schedule_id` | hot-water temperatures |

   Loads of one type, end use, and basis with different demand IDs are distinct physical demands that add: they combine into one load by the aggregator's own component rule (values add, schedules and heat fractions weighted by magnitude), recorded in the preset's source. A zero-magnitude load (the Medium Office's gas equipment) is kept, with its constant-zero schedule.
7. **Shared services are not added.** Their IDs, each once (a set, across every service in the JSON), are listed in a warning and in the report. A local load whose ID matches a shared service is not affected.
8. **Provenance.** The preset's `Source` records: the operation `ProgramJson`; the JSON's `id`, `name`, `scope`, mode, and SHA-256; the source program ID, release, building type, template, and evidence view; the default policy and the count of its substitutions; the calendar; every override from the component's inputs; the shared services left out. The JSON's `assumptions` and `evidence` are returned in full in the report, not copied into every schedule.

### Library choice (7b)

The candidate is **JsonSchema.Net** (json-everything, Draft 2020-12, on `System.Text.Json`). Conditions, each checked at build and logged:

- an OSI-permissive licence (MIT, Apache-2.0, or BSD), recorded in ADR-018 with the version;
- dependencies that Rhino 8's .NET 8 runtime already provides at a compatible version: a `System.Text.Json` newer than the runtime's can fail to load in Rhino, so the version is pinned to one whose dependencies are ≤ 8.0;
- its assemblies are shipped next to `BEMGen.gha` by the plugin build, `scripts/package-release.ps1`, and the `.yak`.

## Part E: the *Program JSON* component

Panel *1 Program*, a new GUID, nickname `PJson`, a new icon motif (`scripts/make_icons.py`). A thin adaptor over `ProgramJsonReader`.

| Input | Access | Default | Meaning |
| --- | --- | --- | --- |
| JSON | item, text | required | the program JSON 2.0.0 text, defaulted mode |
| Name | item | the JSON's `name` | preset name |
| Space Type | item, enum | any-program | the space type the preset applies to |
| WWR | item | 0.4 | window-to-wall ratio, illustrative, not from the JSON |
| Year | item | 2007 | non-leap calendar year of the expansion (1 January 2007 is a Monday, as BEMGen's presets assume) |
| Holidays | list, text `MM-DD` | none | holidays of that year |
| Loads | list | none | override or added loads: each replaces the JSON loads of its type and end use, or is added (ventilation, for one) |
| Heating On, Cooling On | item | the JSON's | override each side |
| Heating Setpoint, Cooling Setpoint | item, schedule | the JSON's | override each schedule |
| Activity | item, schedule | the JSON's | override the activity schedule |
| People Radiant | item | the JSON's | override the radiant fraction |
| People Sensible | item, text | the JSON's | a number or `autocalculate` |

Outputs: *Preset*; *Source* (the provenance text); *Assumptions* (the JSON's recorded substitutions, one line each); *Overrides* (what the inputs replaced or added); *Left Out* (shared services, design-day profiles). Errors and warnings are runtime messages.

## Part F: other component changes

- ***Load*:** new optional inputs *End Use*; *Radiant*, *Latent*, *Lost*, *Visible*, *Return Air* (lighting and equipment only); *Target Temperature* and *Inlet Temperature* schedules (hot water only). *Basis* offers `PerDwellingUnit`.
- ***Schedule*:** *Kind* offers `Activity`.
- ***Program Preset*:** new optional inputs *Heating On*, *Cooling On* (default true; a side is on when *Conditioned* and its *On* are both true; an unset setpoint schedule turns its side off), *Activity*, *People Radiant*, *People Sensible*.
- **Default preset components:** *Heating On* and *Cooling On* appended. Their loads take the default heat fractions, end uses, and water temperatures.
- ***Mix Programs*:** no new inputs. It inherits Part C, and mixing presets with different calendars is an error.
- ***Convert2BEM*:** outputs appended (the layout stays provisional, D-023): *Load End Uses* {i}; *Heat Fractions* {i;k} (five values per load, empty for others); *Dwelling Units* {i}; *Activity* {i} (8760 W/person); *People Radiant* {i}; *People Sensible* {i}; *Water Target* and *Water Inlet* {i;k} (8760 °C per hot-water load). *Heating Setpoints* and *Cooling Setpoints* are empty for a zone whose side is off. *Load Bases* may read `PerDwellingUnit`; *Load Values* stay in their basis.
- ***Convert2IDF*:** no new inputs (Part G).

## Part G: export (`Lod.Export`)

- `Lights`, `ElectricEquipment`, `GasEquipment` take their fractions from the load; `Fraction Replaceable` of lights stays 1.
- One object per load component, named with its end use where a type has more than one: `"{zone} {type} {end use} {basis}"`.
- A per-dwelling load is written as its absolute design level, value × the zone's dwelling count.
- `People`: the zone's activity schedule (written as a schedule with activity limits), its radiant fraction, and its sensible fraction or `autocalculate`.
- `WaterUse:Equipment`: the target temperature schedule and the inlet as the cold-water supply temperature schedule; the hot-water supply field stays blank. Still no zone heat from water (the contract keeps plant and zone gains separate). Checked against the EnergyPlus 25.2.0 IDD and its documentation during the build.
- Thermostats: `ThermostatSetpoint:DualSetpoint` (control type 4) with both sides, `SingleHeating` (1) with heating only, `SingleCooling` (2) with cooling only, each with its own constant control-type schedule.
- Calendar: the run period's year and first weekday come from the building's calendar, or 2007 and Monday when no preset has one. *Convert2BEM* reports the calendar in its provenance.

## Part H: validation

- Conservation (`Totals`) covers end uses separately and includes per-dwelling components (conserved by Part C); the building's dwelling count is a new conserved total.
- New errors: `PerDwellingWithoutDwellings`, `SetpointsCross`, `CalendarMismatch`, `HeatFractionsExceedOne`, `HeatFractionNotSupported`, `WaterTargetBelowInlet`. Diagnostic codes are added centrally.
- New invariant tests: installed radiant (and latent, lost, visible, return-air) power conserved per component; people heat (occupants × activity) conserved every hour; water heat conserved every hour.

## Breaking changes (D-064)

- `ZoneProgram`, `LoadDefinition`, `Thermostat`, and `ZoneMeasures` change shape; every call site and test follows.
- IDF snapshots change: light and equipment fractions are now written from the load (same values by default), and water uses gain their temperature schedules (constant 60 and 10 °C by default, where they were blank, so EnergyPlus's defaults applied). Each changed snapshot is listed in D-126.
- Definitions saved with 1.1.0 open with the new inputs at their defaults; no input is removed, so no value is lost. This is checked on the 19 examples.

## Tests and checks

- **Test-first** for every core transformation: the model types and their validation; each rule of Part C with its zero guards; the invariants of Part H.
- **`Lod.ProgramJson.Tests`:** the committed Medium Office defaulted example passes, and its preset matches hand values (occupancy 0.05382 person/m² = 5 per 1000 ft², lighting 6.8889 W/m² = 0.64 W/ft², equipment 8.0729 W/m² = 0.75 W/ft², hot water 1.0764 × 10⁻⁸ m³/s/m² = 3.875 × 10⁻⁵ m³/h/m², the two lighting end uses, the setpoint and activity profiles on chosen dates of 2007); mutations of it fail with the right code and pointer for every schema rule family and every extra check; synthetic fixtures cover annual schedules (8760 and a rejected 8784), holidays, New Year wrap, 29 February, rule precedence including a later `Wkdy` over an earlier `Mon`, the shared-service set, demand duplicates, overrides, and `raw` rejection. A golden text snapshot of the Medium Office preset.
- **Integration:** Medium Office JSON → an office plate generator → each plan simplifier and floor aggregator → validation → IDF, without Rhino.
- **Export:** the new IDF fields and thermostat types; the IDD check of every IDF the tests write.
- **Rhino:** a new smoke spec `program-json` (the component in Grasshopper, its overrides, errors, and *Convert2IDF*), the full run of every spec, the rebuilt examples, and a new example `examples/program-json-office.gh` with the Medium Office JSON in a panel.
- **`scripts/verify.ps1`** at the end, and the fresh-clone gate on the final branch commit.

## Documentation

ADR-018 (the program model extensions, the rules of Part C, the per-dwelling rule, the library choice) and D-126; the research brief and `docs/research/program-presets.md` (the new rules, GLOBAL.md rule 7); `docs/architecture/` (domain model, pipeline, Convert2BEM, Convert2IDF, validation, and a new `program-json.md` for the contract mapping); the roadmap, AGENTS.md project state, README; the smoke and docs-export READMEs; the atlas files' origin in `tests/Lod.ProgramJson.Tests/Fixtures/README.md` (path, date copied, SHA-256). The project skill `sync-docs` runs at close-out and its source edits are applied; the public site and release wait (stop line). Component descriptions cite no decision numbers.

## Build order

1. Part A (archive), then the core model and aggregation (Parts B, C, H), test-first.
2. In parallel once the core types are in: the library (Part D) and the export (Part G).
3. The Grasshopper components (Parts E, F), icons, examples, the smoke spec.
4. Review by a second agent, fixes, the Rhino run, the documentation, `sync-docs`, verify, the fresh-clone gate, the report.

## Controller choices (provisional; the owner may veto them when approving)

- The end-use default names; the uniqueness triple (type, end use, basis).
- Heat fractions in a field EnergyPlus lacks are an error.
- The 29 February rule; the size bound of the JSON text.
- Per-dwelling counts: 1 per dwelling-unit zone, fractional after a split.
- *Program Preset*'s *Heating On*/*Cooling On* beside *Conditioned* (kept so that old definitions lose nothing).
- Water temperatures 60/10 °C by default for BEMGen's own presets.
- A merged zone whose setpoints cross is an error.
- The *Convert2BEM* output additions and their order.

## Fallbacks (taken without asking, then logged)

- **The schema library fails a condition** (licence, a dependency that will not load in Rhino, or Draft 2020-12 support): try one other permissive library; if none passes, validate with a hand-written checker that mirrors the schema (the rejected option 7a), keep the embedded schema as the reference, and log it as a deviation to decide.
- **Rhino:** no person uses Rhino on this machine (the owner, 2026-10-07). If a Rhino instance is found open, or one the build started cannot be ended normally, the build may close the Rhino application. If Rhino still cannot run, finish everything else and report the Rhino checks as open.
- **The archive worktree is locked:** leave the folder and log it.
- **A snapshot changes for a reason this note does not predict:** stop that part, find the cause, and log it; never update a snapshot to make a test pass.
- **An equivalence rule turns out not to conserve what Part C says:** fix the rule or the claim, record which in the log, and keep the research documents in step.

## Build log

Filled in during the build: findings, deviations, issues, and their resolution, each dated. The controller appends the review findings after the build entries.

### 2026-10-07: Part A, the archive

- The branch `feature/archetype-data` (`cf88cee`) is tagged `archive/archetype-data` (annotated, local). Its worktree `D:\worktrees\archetype-data` was removed cleanly, with no Visual Studio lock this time, and the local branch is deleted. The branch was never on `origin`, so nothing was pushed.
- The atlas files were copied byte-exact. Their SHA-256 values are in `tests/Lod.ProgramJson.Tests/Fixtures/README.md`, and `.gitattributes` marks them `-text` so that a checkout keeps their LF bytes.

### 2026-10-07: the library choice (Part D, option 7b)

- JsonSchema.Net 9.x is under the OSMF EULA (`requireLicenseAcceptance`, licence file `OSMFEULA.txt`), which is not permissive; rejected.
- 8.x (MIT) resolves its `netstandard2.0` dependency chain to `System.Text.Json` 10.0.0 (through Json.More.Net 2.2.0), which cannot load next to the `System.Text.Json` 8 of Rhino 8's .NET 8 runtime; rejected.
- 7.4.0 and 7.3.x pull `System.Text.Json` 9.0.0; rejected.
- Chosen: JsonSchema.Net 7.2.3 (MIT, 2024-09-20), which needs JsonPointer.Net 5.0.0, Json.More.Net 2.0.1.2 (`System.Text.Json` 8.0.0 on `netstandard2.0`), and Humanizer.Core 2.14.1, all MIT. `System.Text.Json` is pinned directly at 8.0.5, because 8.0.0 to 8.0.4 carry NuGet audit advisories. A `net7.0` project resolves the `netstandard2.0` dependency groups, which is why the chain matters. The resolved transitive set is Humanizer.Core 2.14.1, Json.More.Net 2.0.1.2, JsonPointer.Net 5.0.0, System.Text.Encodings.Web 8.0.0, and System.Text.Json 8.0.5.

### 2026-10-07: contract gaps to send to the atlas

1. The rule boundaries of 29 February in a non-leap model year are unspecified.
2. With a non-empty holiday list, defaulted schedules without a `Hol` rule fall to the prepended `Default` rule, so the Medium Office's lighting and equipment are off on holidays while its occupancy keeps its `Default` value of 0.05.
3. The wording "heating does not exceed cooling in the relevant active periods" is vague; BEMGen checks every hour of the expanded year in which both sides are on.
4. The annual schedule's `allOf` constrains `rules`, which annual schedules lack (a copy-paste, harmless).
5. Design-day coverage is required by the checks, though a consumer without sizing never uses it.

### 2026-10-07: phase 2a, the library (`feature/program-json-lib`: `2964657`, `93b1e26`, `9e574bd`)

- `Lod.ProgramJson` reads, schema-validates (JsonSchema.Net 7.2.3), checks, and expands program JSON 2.0.0 into a neutral `ProgramJsonDocument`; 101 tests; `scripts/verify.ps1` passed. All fixtures were also validated independently with Python `jsonschema` 4.26.0 (0 errors).
- Choices:
  - The heat-fraction sum against 1 used `ToleranceSettings.LoadEquals` (1e-9) at first; the finished code uses the new `ToleranceSettings.AbsoluteFraction` (1e-9, as Core checks heat fractions), and the hourly setpoint and water-temperature comparisons use `AbsoluteSchedule`.
  - The size bound is 64 MiB and the depth 64 (`ProgramJsonLimits`); diagnostic codes are prefixed `ProgramJson`.
  - `raw` is rejected before the schema check; only referenced schedules are expanded.
  - Shared-service loads are not checked beyond the schema.
  - A repeated `demand_id` keeps the first copy.
  - Schema errors include every failing `oneOf`/`anyOf` branch, so a rule with 2 values gives 8 errors; the noise is accepted and pruning is left for later.
  - `format: date` is annotation-only in Draft 2020-12.
  - Repeated holidays collapsed silently in the library; the later unification on Core's calendar made them an error.
  - A `Default` rule counts as covering the design days.
- 29 February edge: a rule with start and end both 02-29 covers no day in a non-leap year (the note's literal mapping would make it wrap the whole year); it still warns.
- Contract notes: the Medium Office's `/loads/5/demand_id` is `service-…` (a service-style ID on a local load) while `shared_services` is empty, so it is read as a local load. Leap annual schedules pass the schema but always fail against BEMGen's non-leap calendar.
- Atlas version 1 against 2.0.0: the precedence is the same. Version 1 had `|`-joined day types, `DummySmrDsn`, YYYY-MM-DD dates, constant and fixed-profile forms, and resolved design-day profiles; none of that was ported.

### 2026-10-07: phase 1, the core (`e0db2c9` to `489a844`: Parts B, C, G, H)

- `scripts/verify.ps1` passed (583 core, 518 generator, 2698 integration, 1191 export tests at that point). The IDD check covered 1045 files with 0 problems against the EnergyPlus 25.2.0 template IDD, including `SingleHeating`, `SingleCooling`, the `WaterUse:Equipment` temperatures, and the `People` sensible fraction.
- Snapshots: 28 text reports gain only lines for the new fields (a script confirmed that removing them restores the originals exactly); 6 IDF snapshots gain the calendar header line, and their `RunPeriod` year moves from 2018 to 2007 (both start on a Monday; 2007 is the note's default year). No IDF snapshot had a water use, so the predicted water-temperature change did not occur in snapshots.
- Choices:
  - A calendar's year and weekday win over `IdfOptions`; an `IdfOptions` first day that contradicts the calendar is `CalendarMismatch`.
  - A calendar mismatch cannot be overridden, since no single run period fits.
  - `PlanBuilder` also raises `PerDwellingWithoutDwellings` and `CalendarMismatch` at generation.
  - The sensible-fraction mixture rule counts only sources with a positive occupant weight.
  - Identical schedules pass through a merge with their name, which keeps `BEMGen Activity Level` and the default IDF unchanged.
  - A repeated holiday in `ScheduleCalendar` is an error.
  - New tolerance `ToleranceSettings.AbsoluteFraction` (1e-9).
  - New diagnostic codes include `NoSetpoint`, `CalendarYear`, `CalendarHoliday`, `HeatFractionValue`, `WaterTemperaturesNotAllowed`, `PeopleFraction`, `ZeroAggregationWeight`, and the warning `MixedSensibleFraction`.
- Existing tests changed: three setpoint tests used a heating setpoint above the cooling setpoint (now rejected by `Thermostat`) and were moved to valid values; the enum-name tests gained `PerDwellingUnit`; `InfiltrationOutOfProgramsTests` parses the new per-component check names; `IdfChecks` accepts single-sided thermostats.
- Side effects: *Load*'s *Basis* dropdown and *Schedule*'s *Kind* now offer `PerDwellingUnit` and `Activity`, and the existing preset components now error on crossed setpoints.
- The library branch was rebased onto the core (`e862060`, `8272a32`, `f77f71a`) and verified, which adds its 101 tests; `feature/program-json` was fast-forwarded.

### 2026-10-07: phase 3a, Part F (`6d6e59c` to `4252e77`)

- *Load* inputs 4 to 11 (*End Use*, *Radiant*, *Latent*, *Lost*, *Visible*, *Return Air*, *Target Temperature*, *Inlet Temperature*); *Program Preset* inputs 7 to 11 (*Heating On*, *Cooling On*, *Activity*, *People Radiant*, *People Sensible*); the default preset components append *Heating On* and *Cooling On* at index 5 + 2 × loads; *Convert2BEM* outputs 22 to 30 (*Load End Uses*, *Heat Fractions*, *Dwelling Units*, *Activity*, *People Radiant*, *People Sensible*, *Water Target*, *Water Inlet*, *Calendar*).
- The input rules live in Core (`HeatFractions.WithOverrides`, `WaterTemperatures.WithOverrides`, `SensibleHeatFraction.Parse`, `Thermostat.ForSides`) with 16 tests; `scripts/verify.ps1` passed (599 core tests).
- Behaviour change: *Program Preset* with *Conditioned* and only one setpoint wired used to be an error; it now gives a one-sided space with a remark. *Conditioned* with both sides off is `NoSetpoint`.
- With *Override* on and zones on different calendars, *Convert2BEM* leaves *Calendar* unset with a warning.

### 2026-10-07: phase 2b, the importer

- `ProgramJsonImporter.Import` gives a `ProgramPreset` and a report (*Assumptions*, *Overrides*, *Left Out*). The calendar is unified on Core's `ScheduleCalendar` (`ProgramJsonCalendar` was removed; a repeated holiday is now an error as in Core). Demands of the same component are combined by running `EquivalentPropertyAggregator` on a unit-area zone, with no Core change.
- End to end, the Medium Office goes through the office plate, 7 simplifiers, and 4 aggregators to validation and the IDF: 154 `Lod.ProgramJson.Tests`, 1219 export tests, and an IDD check of 1073 files with 0 problems. The branch was rebased onto Part F and verified, `feature/program-json` was fast-forwarded, and the library worktree was removed.
- The Medium Office's hot-water end use is `hot_water_volume`, not Core's default `hot_water`, so its IDF names include the end use, and a BEMGen hot-water preset mixed with it stays a separate load.
- An override setpoint for a side that is off gives the `OverrideUnused` warning. Override loads replace after the JSON's demands are combined. One *Left Out* line is made per schedule with design-day rules (7 for the Medium Office). A "(given)" WWR is decided by value, so an explicit 0.4 reads as the default. The names of combined water-temperature schedules and of override schedules are not checked for uniqueness against the JSON's names.

### 2026-10-07: phase 3b, the component and Rhino (`f275d79` to `bcaaa94`)

- *Program JSON* has GUID `abb0aeb9-5a9f-40ff-b3a1-bb125cfb675c` (`PJson`), 14 inputs, and 5 outputs. Its icon makes 67 icons, 66 of them byte-identical to before. The example `program-json-office.gh` was built alone with `BEMGEN_EXAMPLES_ONLY`; the 19 others were not rebuilt. The smoke spec `program-json` has 16 scenarios and 57 checks. The full run of all 16 specs passed in Rhino 8.25.25314.11001 on .NET 8.0.31, and the examples spec reopened 20 of 20 definitions with *Validate* True. `scripts/verify.ps1` passed.
- Packaging: the package scripts already copy every top-level DLL, so the `.yak` and the zip now carry `Lod.ProgramJson`, JsonSchema.Net, JsonPointer.Net, Json.More, Humanizer, `System.Text.Json`, and `System.Text.Encodings.Web`. The two System.Text assemblies ship although they are unused on .NET 8 (the framework's 8.0.0.0 wins), because Rhino 8 still has a .NET 7 start in which JsonSchema.Net needs them. This is recorded in `Lod.Grasshopper.csproj`.
- Regression found and fixed (`608bbdd`): Grasshopper's reader reports every current parameter without a saved chunk as "parameter chunk is missing. Archive is corrupt." and opens the IO dialog, so all 19 examples saved with 1.1.0 stalled on reopening (the appended *Heating On* and *Cooling On*, the appended *Convert2BEM* outputs). The fix sets the appended parameters aside while the saved ones are read (the *Join Pieces* precedent); saved values and wires are kept. The examples spec now reads each archive first and fails instead of stalling on IO messages. The note's claim "no input is removed, so no value is lost" needed this fix to hold.
- Second regression fixed (`bcaaa94`): definitions saved before infiltration left the programs (fixture at `af9ac65`) have trailing *Infiltration* inputs at the positions of the new *Heating On* and *Cooling On*, and were read into them; trailing saved parameters whose name differs are no longer counted as saved.
- Rhino: the first examples run stalled about 10 minutes on the IO dialog (the first regression), and Rhino was ended with `taskkill` under the owner's permission. `program-json` ran alone three times (spec fixes: WWR and Year are recorded in *Source*, not *Overrides*; a heated-only test preset had no occupancy, so no *People*). Two full runs were made; the first had 1 failed check in `merge-pieces` (the second regression).

### 2026-10-07: documentation pass

- The version in `Directory.Build.props` was 1.1.0 during the build and is set to 1.2.0 in the documentation pass.
- Where the finished code differs from the wording of this note: the reader (`ProgramJsonReader.Read`) returns a `ProgramJsonDocument`, and the importer (`ProgramJsonImporter.Import`) returns the `ProgramJsonImport`; the errors of Part H that name a model rule (`HeatFractionsExceedOne`, `HeatFractionNotSupported`, `WaterTargetBelowInlet`, `SetpointsCross`) are raised when the model objects are created, while `PerDwellingWithoutDwellings` and `CalendarMismatch` are also validation checks; the heat-conservation, people-heat, and water-heat invariants are tests, not enforced validation checks; the library checks heating against cooling only when both sides are on, with `AbsoluteSchedule`; `Thermostat` first compared exactly, and a review fix gave `Thermostat` and `WaterTemperatures` the same slack, so Core and the importer agree.
- Two review-fix commits landed on the branch during this pass, and the documents describe the code after them: `4d65af3` (a mix with occupancy in more than one basis and a per-person load or different people properties is the error `MixedOccupancyBases`) and `36b55a2` (equal setpoints merged over different sources stay exactly equal; `Thermostat` and `WaterTemperatures` take the central tolerances; end uses are keys ignoring case, so an override *End Use* `Lighting` replaces the JSON's `lighting`; combined hot-water demands name their temperature schedules with their own basis; only activity and water-temperature schedules keep their name when every source holds the same one, load schedules and setpoints being named after the target).
- Counts at the end of the build: 599 core, 518 generator, 154 `Lod.ProgramJson`, 2698 integration, and 1219 export tests; the IDD check covers 1073 files with 0 problems.

### 2026-10-07: the review (second agent, read only)

The reviewer read the whole diff `main...feature/program-json` and confirmed two bugs by running scratch programs outside the repository; it also listed four small defects.

- **Major, fixed (`4d65af3`):** *Mix Programs* added occupants given per m², per dwelling, and absolute on its unit zone as if they were one quantity, so per-person loads and the people properties were weighted by a wrong split (ventilation 103.9 m³/h on 80 m² with one dwelling where the components imply 65 m³/h; people heat 351 W where they imply 390 W). The guard of D-124 covered only absolute occupancy beside a per-person load. Now occupancy in more than one basis across the inputs is the error `MixedOccupancyBases` when any input has a per-person load or when the inputs with occupants differ in their people properties; identical people properties stay allowed, and `PerPersonWithAbsoluteOccupancy` is checked first.
- **Minor, fixed (`36b55a2`):** equal setpoints averaged over different sets of sources rounded apart (21 against 20.999999999999996) and failed the strict crossing check, in 31 of 120 tried combinations. Setpoint means are now exact for equal values, and `SetpointsCross` and `WaterTargetBelowInlet` allow `ToleranceSettings.AbsoluteSchedule` (1e-9), in Core as in the importer.
- **Small defects, fixed (`36b55a2`):** the importer and Core used different crossing tolerances; end uses were matched with case, so an override *End Use* `Lighting` doubled the JSON's `lighting` (end uses are now keys ignoring case, keeping the first spelling); an aggregator comment overstated which schedules keep their name; combined hot-water temperature schedules were named `PerFloorArea` whatever their basis.
- **Checked and found correct:** the per-dwelling rule and the dwelling counts through every simplifier, floor aggregator, multiplier, and the mix; heat fractions, water temperatures, and activity in zone merges; validation; the importer's precedence, New Year wrap, 29 February, units, demand combination, overrides, and strict reading; the IDF field orders; the *Convert2BEM* tree paths; the reading of old definitions.
- **Not checked:** EnergyPlus's run-time behaviour of `WaterUse:Equipment` with a blank hot-water supply temperature.
- The *Mix Programs* description now states the occupancy-basis rule (`44692a1`).

### 2026-10-07: a concurrency bug behind a flaky test

- After the review fixes, `Lod.ProgramJson.Tests` failed about one run in eight on a quiet worktree, each time in a different `SchemaTests` case: schema validation reported an invalid document as having no schema error. The concurrent documentation commits were not the cause.
- Cause: xunit runs test classes in parallel, and concurrent evaluations of the one shared JsonSchema.Net 7.2.3 schema instance are not safe. A new test that reads valid and invalid documents on 16 threads failed 15 of 15 runs before the fix.
- Fix (`fe03c32`): `ProgramJsonSchema.Validate` serialises evaluations with a lock; validation is not a hot path. After it, the new test failed 0 of 15 runs and the whole project 0 of 30. Grasshopper normally solves on one thread, but a parallel solve is now safe too.

### 2026-10-07: final checks (on `fe03c32` and the documentation after it)

- `scripts/verify.ps1` passed with 0 warnings: 614 core, 518 generator, 160 `Lod.ProgramJson`, 2698 integration, and 1219 export tests.
- The IDD check against the EnergyPlus 25.2.0 template IDD: 1073 files, 0 problems.
- All 16 `scripts/rhino-smoke` specs ran once each, with no rerun, every one done with no failed checks and runtime errors only in the error scenarios; `examples` reopened 20 of 20 definitions with *Validate* True.
- A trial docs export (`D:\BEMGen-export\program-json-check`, outside both repositories) wrote version 1.2.0 with 60 screenshots and 0 description gaps; the exported component metadata cites no decision or ADR number.
- The fresh-clone gate: a clean clone of `feature/program-json` at `3d7e19c` passed `scripts/verify.ps1` with the same counts, the atlas fixtures byte-exact (their checksum test passed).
