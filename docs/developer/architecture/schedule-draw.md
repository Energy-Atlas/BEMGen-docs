# Schedule Draw

> **Status:** Provisional ([ADR-033](../decisions/ADR-033-schedule-draw-external-generator.md), D-194 to D-196) · **Component:** *Schedule Draw* (`SDraw`), panel *1 Program*, GUID `740cafea-7afe-47f4-8723-b24b6ec3c836` · **Code:** `Lod.ProgramJson.ScheduleDraw` (`src/Lod.ProgramJson/ScheduleDraw/`), `scripts/TestSuiteGenerator` (`schedules:`) · **Design note:** [2026-10-29-schedule-draw.md](../plans/2026-10-29-schedule-draw.md) · **Requirement:** [schedule-generator-requirement.md](../research/schedule-generator-requirement.md)

## Purpose

A program JSON 5.4.0 defines deterministic ruleset schedules. *Schedule Draw* replaces them, as an optional add-on, with stochastic 8,760-hour schedules drawn by the atlas's generator `atlas_schedules` 3.0.0 (ComStock's sampled hours of operation and base-to-peak ratios for commercial programs), called as an external command. The result is another program JSON 5.4.0, which *Program JSON* and the test-suite generator import like any other.

## Inputs

| Input | What it is |
| --- | --- |
| Program JSON | The program JSON 5.4.0 text (atlas release 2.0.0). |
| Generator JSON | The program setting: the `generator.json` of the program's release folder, `data/atlas-releases/v2.0.0/<family>/<template>/<building>/generator.json`, recipes by release program ID (`source` view; `reviewed` too for 90.1). |
| Setting | The schedule-generator setting, `schedule_draw_setting` 1.0.0 (below). |
| Seed | The master seed (0 or more; the component takes a Grasshopper integer, a suite up to 2^53 − 1). |
| Floor Area | The floor area the program represents, m² (default 100), the extent of its shared services. |
| Command, Folder | The command line (default `python -m atlas_schedules`) and the folder it runs in. With the released wheel installed in a virtual environment (below), the command is that environment's `Scripts/atlas-schedules.exe` or `Scripts/python.exe -m atlas_schedules`, and *Folder* may stay unset; the module form from an atlas checkout runs with the checkout as *Folder*. |
| Run | The command runs only while true. |

Outputs: *Drawn JSON* (the drawn program JSON), *Provenance* (text), *Diagnostics* (every error, warning, and note, one per item).

### The setting

```json
{
  "schema_version": "1.0.0",
  "kind": "schedule_draw_setting",
  "generator": {"name": "atlas_schedules", "version": "3.0.0", "bundle_schema": "3.0.0"},
  "view": "source",
  "draw": ["occupancy", "lighting", "electric_equipment", "gas_equipment", "hot_water", "activity", "heating_setpoint", "cooling_setpoint"],
  "operating_hours": "per_instance",
  "occupancy": {"mix": "state", "window": "2003-2019"},
  "timeout_seconds": 600
}
```

Only `schema_version`, `kind`, and `generator` are required; the rest takes the values shown (`occupancy` is passed to the request only when given). `operating_hours: shared` gives every instance of a draw one set of sampled hours.

### The generator

The pinned generator is `atlas-schedules` 3.0.0, released as the wheel `atlas_schedules-3.0.0-py3-none-any.whl` on the atlas release [`atlas-schedules-v3.0.0`](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v3.0.0) (D-198). It needs Python 3.11 or later; pip brings numpy and jsonschema:

```powershell
python -m venv D:\bemgen-venv-schedules
D:\bemgen-venv-schedules\Scripts\python -m pip install atlas_schedules-3.0.0-py3-none-any.whl
D:\bemgen-venv-schedules\Scripts\atlas-schedules --help
```

It reports `generator_version` 3.0.0, so a draw gives no `ScheduleDrawPreRelease`. The `generator.json` files come from atlas release 2.0.0 (`data/atlas-releases/v2.0.0/...`); release 2.1.0 replaces only those of the eight apartment folders, whose unit recipes *Schedule Draw* refuses.

## How a draw works

`ScheduleDrawer.Draw(instances, recipes, setting, seed, readOptions)`:

1. **Checks** the calendar year (2007), each instance (key of letters, digits, `.`, `_`, `-`; positive floor area), reads its program JSON, finds its recipe in the `generator.json` files by the program's `id` and the setting's view, and refuses apartment-unit and composition recipes.
2. **Writes the request** (schema 3.0.0, compact JSON with one line feed): per instance, `key`, the recipe's `program_id`, `extent.floor_area`, `operating_group` (the key, or `building` when shared), and `service_links` to one shared-service instance per required service (`<key>~service<k>`, with the recipe's ComStock configuration).
3. **Runs the generator once** (`IScheduleGenerator`; `ProcessScheduleGenerator` runs the command in a temporary folder with a timeout and captured standard error).
4. **Reads the bundle:** its schema and generator versions against the pins, the seed, the 2007 hourly calendar, every owner asked for, 8,760 numbers per schedule.
5. **Replaces the schedules** of each role the setting draws (table below) by `annual` schedules `draw:<slot>:<source ID>` with the bundle's values, checks each drawn load's magnitude and annual binding, records `metadata.schedule_draw`, and reads the document back.

| Bundle slot | Program JSON member replaced |
| --- | --- |
| `occupancy`, `occupants` | the occupancy load's `schedule_id` |
| `lighting`, `lighting_interior`, `additional_lighting` | the lighting load's `schedule_id` (several: matched by the recipe's schedule ID, then by value) |
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
| `ScheduleDrawRecipesInvalid`, `ScheduleDrawRecipeNotFound`, `ScheduleDrawKindNotSupported` | Error | A `generator.json` is malformed or two disagree; no recipe for the program and view; an apartment-unit or composition recipe |
| `ScheduleDrawInstanceInvalid`, `ScheduleDrawCalendarYear` | Error | A bad key or floor area; a calendar year other than 2007 |
| `ScheduleDrawCommandFailed`, `ScheduleDrawTimeout`, `ScheduleDrawGeneratorFailed` | Error | The command cannot start; it ran too long; it exited non-zero or wrote no bundle (with its standard error) |
| `ScheduleDrawBundleInvalid`, `ScheduleDrawVersionMismatch` | Error | The bundle is malformed or answers another request; another schema or generator version |
| `ScheduleDrawPreRelease` | Warning | A pre-release of the pinned version, such as `3.0.0.dev0` |
| `ScheduleDrawBindingMismatch`, `ScheduleDrawBindingNotKept`, `ScheduleDrawAmbiguous`, `ScheduleDrawUnitMismatch` | Error | Magnitude or annual binding disagree; a slot matches several loads; a unit does not fit |
| `ScheduleDrawClimateScheduleReplaced` | Warning | A drawn load had schedules by climate zone |
| `ScheduleDrawNotDrawn` | Info | A slot or role not drawn |
| `ScheduleDrawDrawnDocumentInvalid` | Error | The drawn document does not read back (such as a fraction outside [0, 1]) |

## In a test suite

The spec's optional `schedules:` section (`scripts/TestSuiteGenerator/README.md`) makes each seed a test case. One generator run per test case, on the zones of its generated plans before any zoning (key `<plan index>.<zone ID>`); every zone takes its drawn program, and the simplifiers and stackers aggregate the drawn zone schedules as they aggregate any programs, so a merged zone never gets a draw and the reference and its test sites conserve installed and hourly scheduled loads and occupancy.

## Determinism and provenance

The same instances, recipes, setting, and seed give byte-identical documents. Each document's `metadata.schedule_draw` records the generator, versions, SHA-256 of setting, program settings, source program, request, and bundle, the seed, instance, operating group, seed policy and seed, and the schedules drawn and not drawn; every drawn schedule's `source_context` names its source schedule and bundle schedule.

## Tests

`tests/Lod.ProgramJson.Tests/ScheduleDraw/` on the recorded draw `Fixtures/draw/` (the DOE Ref 1980–2004 medium office, instances `0.KS` 200 m² and `0.DI` 300 m², seed 42; the request BEMGen writes and the bundle the released `atlas_schedules` 3.0.0 answered with, D-198 answered with), and `tests/TestSuiteGenerator.Tests/ScheduleDrawSuiteTests.cs` (the cafeteria suite, the merged-zone aggregate). `RealDrawTests` runs the real generator when `BEMGEN_ATLAS_GENERATOR` names the folder to run in (an atlas checkout for the module form, any folder for the installed package) and `BEMGEN_ATLAS_COMMAND` the command, and checks that it reports 3.0.0 without `ScheduleDrawPreRelease` and gives the recorded bundle byte for byte. The Rhino smoke spec `schedule-draw` runs the component with `BEMGEN_SCHEDULE_COMMAND`.
