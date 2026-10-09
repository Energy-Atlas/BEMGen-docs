# Program JSON 2.0.0

> **Status:** Provisional (ADR-018, realisation pending the owner's reading) · **Since:** version 1.2.0 (D-126) · **Component:** *Program JSON* (`PJson`), panel *1 Program*, GUID `abb0aeb9-5a9f-40ff-b3a1-bb125cfb675c` · **Code:** `Lod.ProgramJson` (`src/Lod.ProgramJson/`) · **Design note:** [2026-10-07-program-json.md](../plans/2026-10-07-program-json.md)

## Purpose

The Energy Archetype Atlas publishes a program as *program JSON 2.0.0*: one JSON object with the program's loads, its controls, and every schedule they use, either as the atlas holds them (`raw`, unknown values null) or with the atlas's defaults already applied (`defaulted`, under the policy `atlas-program-defaults-1.0.0`). *Program JSON* turns the text of a defaulted export into a ready-to-use [program preset](../research/program-presets.md#7-atlas-programs-program-json-d-126): the preset goes into any preset input of a plan generator, into *Any Program Preset*, or into *Mix Programs*, and is converted by *Convert2BEM* and *Convert2IDF* like any other.

BEMGen reads only the JSON **text**: no file path and no network. The S10 atlas components that downloaded and verified snapshots were retired (D-126; [ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md)). The contract's own schema and one example are the only atlas files in the repository; their origin, date, and SHA-256 are in `tests/Lod.ProgramJson.Tests/Fixtures/README.md`.

`Lod.ProgramJson` is a plain library (`net7.0`, like the plugin) that depends on `Lod.Core` and the JSON Schema library; it never references RhinoCommon or Grasshopper (AGENTS.md). `Lod.Core` still depends on the base class library and Clipper2 only. The component is a thin adaptor (GLOBAL.md architecture rule 3).

## The contract

A program JSON has these top-level members, all required (the schema is `program-json-v2.schema.json`, Draft 2020-12, embedded byte for byte in `src/Lod.ProgramJson/Schemas/`):

| Member | Content | In BEMGen |
| --- | --- | --- |
| `schema_version`, `kind` | `"2.0.0"`, `"program"` | checked by the schema |
| `export_mode` | `raw` or `defaulted` | only `defaulted` is read |
| `id`, `name`, `scope` | identity; `scope` is `program` or `whole_dwelling` | recorded in the preset's `Source`; the name is the default preset name |
| `source` | the atlas program (`program_id`, `definition_release`, `building_type`, `template`, `evidence_view`) and its `evidence` | the identifiers are recorded in `Source`; the evidence is kept in the document |
| `loads` | the program's loads: `demand_id`, `type`, `end_use`, `value`, `unit`, `basis`, `schedule_id`, and for power loads `heat_fractions`, for hot water `target_temperature_schedule_id` and `inlet_temperature_schedule_id` | mapped to `LoadDefinition`s |
| `controls` | `heating_enabled`, `cooling_enabled`, `heating_setpoint_schedule_id`, `cooling_setpoint_schedule_id`, `activity_schedule_id`, `people_radiant_fraction`, `people_sensible_fraction` | mapped to the `Thermostat` and the `PeopleProperties` |
| `schedules` | an object of schedules by ID, each a `ruleset` (dated rules by day type) or `annual` (one value per hour of a year) | expanded to 8760 values |
| `shared_services` | equipment shared by several zones | left out |
| `default_policy_id`, `assumptions` | the policy and each substitution it made (`path`, `rule_id`, `original_value`, `replacement_value`, `reason`) | the count is recorded in `Source`; the lines are the *Assumptions* output |
| `required_bindings` | what a consumer must bind: `floor_area_m2`, `dwelling_unit_count`, `person_count`, `shared_service_host`, `calendar_year`, `holiday_calendar` | kept in the document; BEMGen binds the calendar through *Year* and *Holidays*, and the others through its geometry |

In the `defaulted` mode the schema requires every value to be known: each load has a number, a schedule, and (power loads) all five heat fractions; the controls are complete; and `default_policy_id` is set.

## How a JSON becomes a preset

`ProgramJsonImporter.Import(json, options)` runs these steps in order; each stops the read when it finds an error, and every diagnostic carries the JSON Pointer (RFC 6901) of the node it concerns, or the name of the input for an option.

1. **Strict parse** (`StrictJson`): UTF-8 JSON, no byte-order mark, no non-finite number, no repeated member name (`ProgramJsonDuplicateKey`), at most 64 MiB and nesting depth 64 (`ProgramJsonLimits`, input bounds and not numerical tolerances). The text's SHA-256 is taken from the parsed bytes.
2. **Mode:** `raw` is rejected with a message to export the defaulted form (`ProgramJsonModeNotSupported`), before the schema is checked.
3. **Schema:** validation against the embedded schema (JsonSchema.Net, Draft 2020-12). Every violation is reported with its instance path and the schema keyword; the message of a `oneOf` or `anyOf` lists every failing branch, so one wrong value can give several lines.
4. **The contract's checks** beyond the schema, then the **expansion** of every referenced schedule and the hourly checks (below).
5. **Mapping** to a `ProgramPreset` and the **overrides** of the component's inputs (below).

### Checks

| Code | Severity | When |
| --- | --- | --- |
| `ProgramJsonInputTooLarge`, `ProgramJsonInvalidJson`, `ProgramJsonDuplicateKey` | Error | The text exceeds the size bound; is empty, has a byte-order mark, a syntax error, a non-finite number, or too deep nesting; or has a repeated member name |
| `ProgramJsonModeNotSupported` | Error | `export_mode` is `raw` |
| `ProgramJsonSchemaViolation` | Error | A rule of the schema is broken |
| `ProgramJsonScheduleIdMismatch` | Error | A schedule's key in `schedules` differs from its `id` |
| `ProgramJsonUnresolvedReference` | Error | A schedule ID used by a load or the controls is not a key of `schedules` |
| `ProgramJsonScheduleUnitMismatch` | Error | A schedule's unit does not fit its role: load schedules `1`, setpoints and water temperatures `degC`, the activity schedule `W/person`. Units are never converted |
| `ProgramJsonInvalidDate` | Error | A rule's `MM-DD` date is not a date of any year, such as `02-30`. `02-29` is accepted (checked against a leap year) |
| `ProgramJsonAnnualLength`, `ProgramJsonAnnualYearMismatch` | Error | An annual schedule does not hold the hours of its own year (8760, or 8784 for a leap year), or its year differs from the calendar's *Year*. An annual schedule is taken as it is, in local standard time, and never resampled or moved to another year; a leap-year schedule can never match BEMGen's non-leap calendar |
| `ProgramJsonHeatFractionsExceedOne` | Error | A load's five heat fractions sum to more than 1 (within `ToleranceSettings.AbsoluteFraction`) |
| `ProgramJsonDuplicateDemandConflict` | Error | Two loads share a `demand_id` but differ |
| `ProgramJsonDuplicateDemandMerged` | Warning | Two loads share a `demand_id` and are identical; the demand is kept once |
| `ProgramJsonDayNotCovered` | Error | A day of the calendar year matches no rule of a ruleset, neither a specific rule nor a `Default` rule; the message names the first days |
| `ProgramJsonDesignDayNotCovered` | Warning | A ruleset has no rule for `WntrDsn` or `SmrDsn` and no `Default` rule. Design-day profiles are checked and not used |
| `ProgramJsonFebruary29Adjusted` | Warning | A rule starts or ends on `02-29`, which the non-leap calendar year lacks (below) |
| `ProgramJsonSetpointsCross` | Error | With heating and cooling both enabled, the heating setpoint exceeds the cooling setpoint in some hour of the expanded year by more than `AbsoluteSchedule` (the preset's own `SetpointsCross` check allows the same slack); the message gives the number of hours and the first |
| `ProgramJsonWaterTargetBelowInlet` | Error | A hot-water load's target temperature is below its inlet temperature in some hour by more than `AbsoluteSchedule` |
| `ProgramJsonSharedServicesLeftOut` | Warning | The JSON has shared services; they are listed and not added |
| `ProgramJsonDuplicateOverrideLoad` | Error | Two override loads of the import have the same type, end use, and basis |
| `ProgramJsonOverrideUnused` | Warning | A setpoint override is given for a side that is off |

The preset's own rules then apply, with the Core codes of [validation.md](validation.md#program-properties-d-126) and the JSON Pointer or input name as the subject: a heat fraction in a field EnergyPlus lacks (`HeatFractionNotSupported`, pointing at `…/heat_fractions`), crossed setpoints (`SetpointsCross`), `WaterTargetBelowInlet`, a schedule value outside its kind's range (`ScheduleValue`), an unreadable calendar (`CalendarYear` for a leap *Year*, `CalendarHoliday` for a holiday that is not `MM-DD`), a WWR outside [0, 1) (`WindowToWallRatio`, subject `WindowToWallRatio`), and the others.

## Expanding schedules

Every schedule that a load or the controls refers to becomes 8760 hourly values on the calendar of the *Year* input (default 2007, whose 1 January is a Monday, as BEMGen's own presets assume) and the *Holidays* input (`MM-DD` dates of that year). The year must be a non-leap year; a leap year is an error (`CalendarYear`), because every BEMGen schedule has 8760 values (ADR-003).

**Ruleset schedules** (`rule_selection` is `last_specific_match_else_last_default`):

1. For each date of the year, the effective day type is `Hol` if the date is a holiday, otherwise the weekday of the date.
2. The rules are scanned **in array order and never sorted**. A rule applies to the date if its range, inclusive at both ends and recurring every year, contains the month and day; a start later than the end wraps New Year.
3. Among the applicable rules, the **last** one with a matching specific day type wins. `Wkdy` matches Monday to Friday, `Wknd` Saturday and Sunday, `Mon` to `Sun` their day, and `Hol` only holidays. An explicit weekday has no priority over a later `Wkdy` (so a later `Wkdy` rule overrides an earlier `Mon` rule). A holiday matches `Hol` only, never its weekday, `Wkdy`, or `Wknd`.
4. When no specific day type matches, the last applicable rule that lists `Default` is used.
5. When neither exists, the date is not covered: an error.
6. One value in a rule is constant over the day; 24 values are hourly steps over [h, h+1).

**29 February in a non-leap year.** The contract is silent, so BEMGen compares dates as month × 100 + day: a rule that starts on `02-29` starts on 1 March, and one that ends on `02-29` ends on 28 February, each with the warning `ProgramJsonFebruary29Adjusted`. A rule with start and end both `02-29` covers no day (the literal reading, a start later than the end, would wrap the whole year), and still warns.

**Holidays.** Holidays enter only through the `Hol` day type: on a holiday the schedule takes the value of its last applicable `Hol` rule, or else its last `Default` rule. The values reach the IDF as hourly values, so the writer defines no special day. A defaulted schedule without a `Hol` rule falls to the `Default` rule the atlas prepended, so for the Medium Office lighting and equipment are off on a holiday while occupancy keeps its `Default` value (a gap reported to the atlas, below).

**Design days.** `WntrDsn` and `SmrDsn` are not days of the model year and never match a date. A schedule with no rule for them and no `Default` rule gets a warning; their profiles are not used, and each schedule that has such rules gets one line in the *Left Out* output (7 for the Medium Office). The IDF gives design days the Sunday profile.

The reader keeps the first copy of a repeated `demand_id` and never expands a schedule that nothing refers to.

## Mapping to the program model

| Contract | BEMGen |
| --- | --- |
| `type` `occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water` | `LoadType.Occupancy`, `Lighting`, `ElectricEquipment`, `GasEquipment`, `DomesticHotWater` |
| `end_use` | `LoadDefinition.EndUse` (for the Medium Office: `occupancy`, `lighting`, `additional_lighting`, `electric_equipment`, `gas_equipment`, `hot_water_volume`) |
| `basis` `floor_area`, `dwelling_unit`, `person`, `absolute` | `LoadBasis.PerFloorArea`, `PerDwellingUnit`, `PerPerson`, `Absolute` |
| `value` with `unit` person/m², person/dwelling, person; W/m², W/dwelling, W/person, W | unchanged (the schema ties each unit to the load's type and basis, so the mapping reads the type and basis and carries the unit only for the report) |
| `value` of a hot-water load in m³/s per m², per dwelling, per person, or absolute | × 3600, m³/h of the same basis (the only unit conversion) |
| `schedule_id` | the load's fraction schedule (`ScheduleKind.Fraction`), named after the schedule's `name`, or its `id` when the name is empty; two schedules with one name each take their id in brackets, `name [id]` |
| `heat_fractions` (`radiant`, `latent`, `lost`, `visible`, `return_air`) | `HeatFractions` |
| `target_temperature_schedule_id`, `inlet_temperature_schedule_id` | `WaterTemperatures.Target` and `.Inlet` (`ScheduleKind.Temperature`) |
| `controls.heating_enabled`, `heating_setpoint_schedule_id` | `Thermostat.HeatingSetpoint` when enabled; heating is off otherwise |
| `controls.cooling_enabled`, `cooling_setpoint_schedule_id` | `Thermostat.CoolingSetpoint` when enabled |
| both sides disabled | an unconditioned program (no thermostat) |
| `controls.activity_schedule_id` | `PeopleProperties.Activity` (`ScheduleKind.Activity`, W/person) |
| `controls.people_radiant_fraction`, `people_sensible_fraction` (a number or `autocalculate`) | `PeopleProperties.RadiantFraction`, `SensibleFraction` |
| the calendar (*Year*, *Holidays*) | `ZoneProgram.Calendar` and `ProgramPreset.Calendar` |
| `shared_services` | not added |
| `source`, `id`, `name`, `scope`, `export_mode`, SHA-256, `default_policy_id`, `assumptions` | `ProgramPreset.Source` (below) and the *Assumptions* output |

A **zero-magnitude load** is kept with its own schedule: the Medium Office's gas equipment is 0 W/m² with a constant-zero schedule, and its `additional_lighting` is 0 W/m² with the lighting schedule.

**Demands that add.** Loads of one type, end use, and basis with different demand IDs are distinct physical demands. They are combined into one load by the zone-merge rule: each demand, re-expressed per floor area, is a source of unit area in a target of unit area, so the values add, and the schedule and the heat fractions are weighted by each demand's magnitude and the water temperatures every hour by its scheduled flow ([domain-model.md](domain-model.md#62-rules)). Each combination is recorded in the preset's source (`Combined.k`). A combined load's schedule and, for hot water, its two temperature schedules are named `<preset name> <type> <end use> <basis>` (with ` Target Temperature` or ` Inlet Temperature`) unless one of the demands already had that schedule.

## Overrides

The inputs after *JSON* complete or override the JSON. Unset, the JSON's value (or the stated default) is used. WWR, space type, and calendar are inputs because the JSON does not hold them.

| Input | Default | Effect |
| --- | --- | --- |
| *Name* | the JSON's `name` | the preset name; recorded as an override |
| *Space Type* | unset: an any-program preset | the space type the preset applies to |
| *WWR* | 0.4 | the window-to-wall ratio in [0, 1); the JSON holds no glazing, so 0.4 is an illustrative value and recorded as `default, not from the JSON` (a value of exactly 0.4 reads as the default) |
| *Year* | 2007 | the non-leap year schedules are expanded on |
| *Holidays* | none | `MM-DD` dates of that year |
| *Loads* | none | each load replaces every JSON load of its **type and end use** (end uses compared ignoring case, so `Lighting` replaces `lighting`), whatever its basis, or is added when the JSON has none (ventilation, which the contract does not carry). The replacement happens after the JSON's demands are combined. Two override loads of one type, end use, and basis are an error |
| *Heating On*, *Cooling On* | the JSON's `heating_enabled`, `cooling_enabled` | switch each side |
| *Heating Setpoint*, *Cooling Setpoint* | the JSON's schedules | a `Temperature` schedule replacing the JSON's; used only when that side is on, otherwise the warning `ProgramJsonOverrideUnused` |
| *Activity* | the JSON's | an `Activity` schedule replacing the JSON's |
| *People Radiant* | the JSON's | the radiant fraction of people's sensible heat |
| *People Sensible* | the JSON's | a number from 0 to 1 or `autocalculate` |

Outputs: *Preset*; *Source*, the preset's provenance text; *Assumptions*, the JSON's recorded substitutions, one line each (`path: original -> replacement (rule: reason)`); *Overrides*, what the inputs replaced or added; and *Left Out*, each shared service and the design-day rules of the schedules that have them. Errors and warnings are runtime messages.

## Provenance

The preset's `Source` is `Provenance.Of("ProgramJson", …)` with these parameters: `Json.Id`, `Json.Name`, `Json.Scope`, `Json.ExportMode`, `Json.Sha256`; `Source.ProgramId`, `Source.DefinitionRelease`, `Source.BuildingType`, `Source.Template`, `Source.EvidenceView`; `DefaultPolicy` (the policy ID and the number of substitutions); `Calendar`; `SpaceType` and `WindowToWallRatio` with how each was chosen; one `Override.k` per override, one `Combined.k` per combination of demands, and one `SharedService.k` per shared service left out. The JSON's `assumptions` and `evidence` are returned in full by the document and the *Assumptions* output and are not copied into every schedule. A plan made from the preset records its source among its provenance inputs, and *Inspect* prints it.

## Library and licences

The schema is validated by **JsonSchema.Net 7.2.3** (MIT). The choice, the versions rejected, and the reasons are in [ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md#validation-of-the-json): a version whose `netstandard2.0` dependencies pull a `System.Text.Json` newer than 8 cannot load next to Rhino 8's .NET 8 runtime, and the later versions are not permissively licensed.

| Package (assembly) | Version | Licence | Why it ships |
| --- | --- | --- | --- |
| JsonSchema.Net (`JsonSchema.Net.dll`) | 7.2.3 | MIT | schema validation |
| JsonPointer.Net | 5.0.0 | MIT | its dependency |
| Json.More.Net (`Json.More.dll`) | 2.0.1.2 | MIT | its dependency |
| Humanizer.Core (`Humanizer.dll`) | 2.14.1 | MIT | its dependency |
| System.Text.Json | 8.0.5 (pinned; 8.0.0 to 8.0.4 have NuGet audit advisories) | MIT | on Rhino's .NET 8 the framework's assembly of the same version wins and this file is unused; it stays for a Rhino 8 started on .NET 7 |
| System.Text.Encodings.Web | 8.0.0 | MIT | the same |

The packaging copies every top-level DLL next to `BEMGen.gha`, so the plugin zip and the `.yak` carry `Lod.ProgramJson.dll` and these six files (`scripts/package-release.ps1`, `scripts/package-yak.ps1`); `Lod.Grasshopper.csproj` records why.

## What is left out

- **Shared services** (`shared_services`): equipment that serves several zones, with `ownership` `instantiate_once` and a `host_assignment` of `consumer_selected_zone`. BEMGen does not model them (the owner's decision). Each ID is listed once in the warning `ProgramJsonSharedServicesLeftOut` and in *Left Out*, and in the source. A local load whose ID looks like a service's is a local load.
- **Design-day profiles:** checked, not used.
- **`required_bindings`:** not acted on beyond the calendar.
- **`raw` exports:** rejected.
- **Leap years:** an error, as for every BEMGen schedule.

## Tests and example

`tests/Lod.ProgramJson.Tests` holds the committed Medium Office defaulted example, the atlas schemas, and synthetic fixtures for annual schedules, holidays, New Year wrap, 29 February, rule precedence, shared services, and demand duplicates. The Medium Office preset is compared with hand values (occupancy 0.05382 person/m², lighting 6.8889 W/m², electric equipment 8.0729 W/m², hot water 3.875 × 10⁻⁵ m³/h per m², the two lighting end uses, the setpoint and activity profiles on chosen dates) and with a golden snapshot (`Snapshots/medium-office-preset.txt`); mutations of the example fail with the right code and pointer for every schema rule family and every check; the example goes through the office plate, every plan simplifier, and every floor aggregator to a validated building and an IDF. `examples/program-json-office.gh` wires the Medium Office JSON in a panel into *Program JSON* for the office input of *Office Plate*; the smoke spec `program-json` (`scripts/rhino-smoke/README.md`) checks the component, its overrides, and its errors in Rhino.

## Contract gaps reported to the atlas

BEMGen reports these to the atlas and does not work around them:

1. The rule boundaries of 29 February in a non-leap model year are unspecified.
2. With a non-empty holiday list, defaulted schedules without a `Hol` rule fall to the prepended `Default` rule.
3. "Heating does not exceed cooling in the relevant active periods" is vague; BEMGen checks every hour of the expanded year in which both sides are on.
4. The annual schedule's `allOf` constrains `rules`, which annual schedules lack (harmless).
5. Design-day coverage is required by the checks, though a consumer without sizing never uses it.
