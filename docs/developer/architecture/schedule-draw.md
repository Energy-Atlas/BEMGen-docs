# Schedule Draw

> **Status:** Provisional ([ADR-033](../decisions/ADR-033-schedule-draw-external-generator.md), D-194 to D-196); generator 4.0.0 and atlas release 2.2.0 since 1.7.0 ([ADR-035](../decisions/ADR-035-schedule-draw-generator-4-0-0.md), D-205) · **Component:** *Schedule Draw* (`SDraw`), panel *1 Program*, GUID `740cafea-7afe-47f4-8723-b24b6ec3c836` · **Code:** `Lod.ProgramJson.ScheduleDraw` (`src/Lod.ProgramJson/ScheduleDraw/`), `scripts/TestSuiteGenerator` (`schedules:`) · **Design note:** [2026-10-29-schedule-draw.md](../plans/2026-10-29-schedule-draw.md) · **Requirement:** [schedule-generator-requirement.md](../research/schedule-generator-requirement.md)

## Purpose

A program JSON 5.4.0 defines deterministic ruleset schedules. *Schedule Draw* replaces them, as an optional add-on, with stochastic 8,760-hour schedules drawn by the atlas's generator `atlas_schedules` 4.0.0, which assembles its recipes from atlas release 2.2.0 (ComStock's sampled hours of operation and base-to-peak ratios for commercial programs), called as an external command. The result is another program JSON 5.4.0, which *Program JSON* and the test-suite generator import like any other.

## Inputs

| Input | What it is |
| --- | --- |
| Program JSON | The program JSON 5.4.0 text (atlas release 2.0.0, 2.1.0, or 2.2.0; their program IDs and values are the same). Its `version` (`filled` or `source`) chooses the values the generator draws from. |
| Generator JSON | The program setting: the `generation.json` of the program's folder in atlas release 2.2.0, `v2.2.0/<family>/<template>/<building>/generation.json` in `atlas-release-2.2.0.zip` of the release [`v2.2.0`](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/v2.2.0): per release program its generation method and, per view (`source`, and `filled` for 90.1), its ComStock configuration; per release service the configurations it runs under. A `generator.json` of release 2.0.0 or 2.1.0 is refused. |
| Setting | The schedule-generator setting, `schedule_draw_setting` 2.0.0 (below). |
| Seed | The master seed (0 or more; the component takes a Grasshopper integer, a suite up to 2^53 − 1). |
| Floor Area | The floor area the program represents, m² (default 100), the extent of its shared services. |
| Command, Folder | The command line (default `python -m atlas_schedules`) and the folder it runs in. With the released wheel installed in a virtual environment (below), the command is that environment's `Scripts/atlas-schedules.exe` or `Scripts/python.exe -m atlas_schedules`, and *Folder* may stay unset; the module form from an atlas checkout runs with the checkout as *Folder*. |
| Run | The command runs only while true. |

Outputs: *Drawn JSON* (the drawn program JSON), *Provenance* (text), *Diagnostics* (every error, warning, and note, one per item).

### Generator JSON from the atlas site (D-209)

The strip *Get from Atlas…* at the bottom of the component ([ADR-036](../decisions/ADR-036-atlas-program-maps.md)) opens, on a double-click, a window that reads the `id` of the program in *Program JSON* (its wire's text of the last solution, else its stored text), finds the program's folder in the atlas site's index, and downloads and checks that folder's `generation.json` (`AtlasSite.DownloadGenerationAsync`). *Use this file* stores it as *Generator JSON*'s own value with one undo event (`SetGeneratorJsonText`); a wire into *Generator JSON* still takes precedence. The stored text is the site's store file, compact JSON equal in content to the release's file. Where the release has no generation file for the folder the window says so (`AtlasSiteGenerationNotPublished`) and stores nothing: in release 2.2.0 only 90 of 255 folders have one, and none of the `*-detailed` office folders, so the programs of the DOE small, medium, and large office's keys, which live in those folders, have no program setting on the site, as in the release. That is a limitation of the atlas data, which BEMGen does not work around. The network is used only while the window is open, never in a solve.

### The setting

```json
{
  "schema_version": "2.0.0",
  "kind": "schedule_draw_setting",
  "generator": {"name": "atlas_schedules", "version": "4.0.0", "bundle_schema": "4.0.0"},
  "draw": ["occupancy", "lighting", "electric_equipment", "gas_equipment", "hot_water", "activity", "heating_setpoint", "cooling_setpoint"],
  "operating_hours": "per_instance",
  "occupancy": {"mix": "state", "window": "2003-2019"},
  "timeout_seconds": 600
}
```

Only `schema_version`, `kind`, and `generator` are required; the rest takes the values shown (`occupancy` is passed to the request only when given). `operating_hours: shared` gives every instance of a draw one set of sampled hours. Setting 1.0.0 (generator 3.0.0) had a `view`; it is refused with what to change, since the view is the program JSON's own version (ADR-035).

### The generator

The pinned generator is `atlas-schedules` 4.0.0, released as the wheel `atlas_schedules-4.0.0-py3-none-any.whl` with `SHA256SUMS.txt` on the atlas release [`atlas-schedules-v4.0.0`](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v4.0.0) (D-205). It needs Python 3.11 or later; pip brings numpy and jsonschema, and the wheel bundles the generator view of atlas release 2.2.0, so no atlas checkout or data download is needed to draw:

```powershell
sha256sum -c SHA256SUMS.txt --ignore-missing
python -m venv D:\bemgen-venv-schedules
D:\bemgen-venv-schedules\Scripts\python -m pip install --upgrade atlas_schedules-4.0.0-py3-none-any.whl
D:\bemgen-venv-schedules\Scripts\atlas-schedules --version
```

`--version` prints `atlas-schedules 4.0.0 (request schema 4.0.0); reads atlas release 2.2.0 from ...`. A draw then gives no `ScheduleDrawPreRelease`, and the bundle's `release` is 2.2.0 with the pinned manifest SHA-256 `67e73e55…7ece4`; a generator pointed at another release (`ATLAS_RELEASES`, `--release-dir`) is refused with `ScheduleDrawVersionMismatch`. The `generation.json` files come from the same release (`atlas-release-2.2.0.zip`).

## How a draw works

`ScheduleDrawer.Draw(instances, recipes, setting, seed, readOptions)`:

1. **Checks** the calendar year (2007), each instance (key of letters, digits, `.`, `_`, `-`; positive floor area), reads its program JSON, finds its generation block in the `generation.json` files by the program's `id`, takes the view of the program's `version` (a view the block lacks: `source`, with `ScheduleDrawValuesSource`, as for the DOE Ref programs' filled exports), and refuses the methods other than `comstock_hours` and `fixed`. Its shared services are the release services of the files that its hot-water demands name (`water_heating[].demand_id`, a `hot_water` load's `demand_id`), each of which must run under the program's configuration.
2. **Writes the request** (schema 4.0.0, compact JSON with one line feed): per instance, `key`, the release `program_id`, `values` (`source` or `filled`), `extent.floor_area`, `operating_group` (the key, or `building` when shared), and `service_links` to one shared-service instance per shared service (`<key>~service<k>`, with the view's ComStock configuration).
3. **Runs the generator once** (`IScheduleGenerator`; `ProcessScheduleGenerator` runs the command in a temporary folder with a timeout and captured standard error).
4. **Reads the bundle:** its schema and generator versions and its data release (version and manifest SHA-256) against the pins, the seed, the 2007 hourly calendar, every owner asked for with the view asked for, 8,760 numbers per schedule.
5. **Replaces the schedules** of each role the setting draws (table below) by `annual` schedules `draw:<slot>:<source ID>` with the bundle's values, checks each drawn load's magnitude and annual binding, records `metadata.schedule_draw`, and reads the document back.

| Bundle slot | Program JSON member replaced |
| --- | --- |
| `occupancy`, `occupants` | the occupancy load's `schedule_id` |
| `lighting`, `lighting_interior`, `additional_lighting` | the lighting load's `schedule_id` (several: the one whose value is the bundle's amplitude for the slot) |
| `electric_equipment`, `gas_equipment` | that load's `schedule_id` |
| `activity` | `controls.activity_schedule_id` and the occupancy load's `activity_schedule_id` |
| `heating_setpoint`, `cooling_setpoint` | `controls.heating_setpoint_schedule_id`, `controls.cooling_setpoint_schedule_id` |
| service `hot_water_volume`, `water_target_temperature` | the hot-water demand (a `hot_water` load or a `water_heating[].draw`, matched by the service ID): `schedule_id`, `target_temperature_schedule_id` |

A slot without a role (the water-use zone gains' fractions), a role the setting does not draw, or a role the program has no schedule for is listed in `not_drawn` and as `ScheduleDrawNotDrawn`.

### Conservation

A drawn load keeps the program's value, which must equal the generator's amplitude in the same unit, and amplitude × Σ values × s (s = 1 for W, 3600 for m³/s) equals the bundle's annual total within `ToleranceSettings.RelativeLoad`. Installed loads are therefore those of the program; the hourly scheduled load is the generator's.

### Codes

| Code | Severity | When |
| --- | --- | --- |
| `ScheduleDrawSettingInvalid`, `ScheduleDrawGeneratorNotSupported` | Error | The setting is not valid, or names another generator, version, or bundle schema |
| `ScheduleDrawRecipesInvalid`, `ScheduleDrawRecipeNotFound`, `ScheduleDrawKindNotSupported` | Error | A `generation.json` is malformed, a `generator.json` of an earlier release, or two disagree, or a shared service does not run under the program's configuration; no generation block for the program or no usable view; a composition, apartment-unit, or ResStock dwelling method |
| `ScheduleDrawInstanceInvalid`, `ScheduleDrawCalendarYear` | Error | A bad key or floor area; a calendar year other than 2007 |
| `ScheduleDrawCommandFailed`, `ScheduleDrawTimeout`, `ScheduleDrawGeneratorFailed` | Error | The command cannot start; it ran too long; it exited non-zero or wrote no bundle (with its standard error) |
| `ScheduleDrawBundleInvalid`, `ScheduleDrawVersionMismatch` | Error | The bundle is malformed or answers another request (another seed, owner, or view); another schema or generator version, or another data release or manifest |
| `ScheduleDrawPreRelease` | Warning | A pre-release of the pinned version, such as `4.0.0.dev0` |
| `ScheduleDrawValuesSource` | Info | The export's view is not one of the block's views, so the request asks for `source` |
| `ScheduleDrawBindingMismatch`, `ScheduleDrawBindingNotKept`, `ScheduleDrawAmbiguous`, `ScheduleDrawUnitMismatch` | Error | Magnitude or annual binding disagree; a slot matches several loads; a unit does not fit |
| `ScheduleDrawClimateScheduleReplaced` | Warning | A drawn load had schedules by climate zone |
| `ScheduleDrawNotDrawn` | Info | A slot or role not drawn |
| `ScheduleDrawDrawnDocumentInvalid` | Error | The drawn document does not read back (such as a fraction outside [0, 1]) |

## In a test suite

The spec's optional `schedules:` section (`scripts/TestSuiteGenerator/README.md`) makes each seed a test case. One generator run per test case, on the zones of its generated plans before any zoning (key `<plan index>.<zone ID>`); every zone takes its drawn program, and the simplifiers and stackers aggregate the drawn zone schedules as they aggregate any programs, so a merged zone never gets a draw and the reference and its test sites conserve installed and hourly scheduled loads and occupancy.

## Determinism and provenance

The same instances, recipes, setting, and seed give byte-identical documents. Each document's `metadata.schedule_draw` records the generator and its versions, the data release (`release`: version, manifest SHA-256, generation schema), the values drawn from (`values`), the SHA-256 of the setting, the program settings (`recipe_sha256`, the `generation.json` files), the source program, the request, and the bundle, the seed, instance, operating group, seed policy and seed, and the schedules drawn and not drawn; every drawn schedule's `source_context` names its source schedule and bundle schedule.

## Tests

`tests/Lod.ProgramJson.Tests/ScheduleDraw/` on the recorded draws `Fixtures/draw/` (the DOE Ref 1980–2004 medium office's filled export, instances `0.KS` 200 m² and `0.DI` 300 m², seed 42; the 90.1-2019 medium office's source export, `0.OF` 250 m²; the requests BEMGen writes and the bundles the released `atlas_schedules` 4.0.0 answered with, D-205), and `tests/TestSuiteGenerator.Tests/ScheduleDrawSuiteTests.cs` (the cafeteria suite, the merged-zone aggregate). `RealDrawTests` runs the real generator when `BEMGEN_ATLAS_GENERATOR` names the folder to run in (an atlas checkout for the module form, any folder for the installed package) and `BEMGEN_ATLAS_COMMAND` the command, and checks that it reports 4.0.0 without `ScheduleDrawPreRelease`, reads release 2.2.0, and gives the recorded bundles byte for byte, twice. The Rhino smoke spec `schedule-draw` runs the component with `BEMGEN_SCHEDULE_COMMAND`.
