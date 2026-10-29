# Program JSON 5.4.0

The separate backend [DOE reference catalog](../research/reference-program-contract.md#source-packet) preserves source identities and declared departures. Its packet format is not atlas program JSON 5.4.0; this component's schema and illustrative defaults are unchanged.

> **Status:** Provisional (ADR-018 and [ADR-027](../decisions/ADR-027-atlas-release-2-0-0-contracts.md), realisation pending the owner's reading) · **Since:** version 1.2.0 (D-126); program JSON 5.4.0 of atlas release 2.0.0 since D-172, and of release 2.1.0 since version 1.6.0 (D-198) · **Component:** *Program JSON* (`PJson`), panel *1 Program*, GUID `abb0aeb9-5a9f-40ff-b3a1-bb125cfb675c` · **Code:** `Lod.ProgramJson` (`src/Lod.ProgramJson/`) · **Design notes:** [2026-10-07-program-json.md](../plans/2026-10-07-program-json.md), [2026-10-28-atlas-release-2-0-0.md](../plans/2026-10-28-atlas-release-2-0-0.md)

## Purpose

The Energy Archetype Atlas publishes a program as *program JSON*: one JSON object with the program's loads, its controls, and every schedule they use. Atlas release 2.0.0 (a full snapshot) and release 2.1.0 (a delta on it with the open licence and the generator 3.0.0 apartment recipes, whose program exports differ only in `source.release`, D-198) export **program JSON 5.4.0** in two versions: `source`, the actual values only, with what the source does not record left `null`, and `filled`, with the atlas's fillings and approved defaults applied (policy `atlas-program-defaults-2.0.0`) and the hot water as draw-only water heating. IECC programs and code-prototype dwellings export the source version only. *Program JSON* turns the text of either version into a ready-to-use [program preset](../research/program-presets.md#7-atlas-programs-program-json-d-126): the preset goes into any preset input of a plan generator, into *Any Program Preset*, or into *Mix Programs*, and is converted by *Convert2BEM* and *Convert2IDF* like any other.

BEMGen reads only the JSON **text**: no file path and no network. The retired program JSON 2.0.0 (D-126) is refused with a message to export again from release 2.0.0 (D-172) or 2.1.0. The embedded schema is release 2.1.0's copy of the 5.4.0 schema, which admits both releases' `source.release` (D-198). The contract's schema and seven release exports are the only atlas program files in the repository; `tests/Lod.ProgramJson.Tests/Fixtures/README.md` gives their origin and `manifest.json` their SHA-256.

`Lod.ProgramJson` is a plain library (`net7.0`, like the plugin) that depends on `Lod.Core` and the JSON Schema library; it never references RhinoCommon or Grasshopper (AGENTS.md). The component is a thin adaptor (GLOBAL.md architecture rule 3).

## The contract

The schema is `program-json-v5.4.schema.json` (Draft 2020-12), one `oneOf` of a `source` and a `filled` branch, embedded byte for byte in `src/Lod.ProgramJson/Schemas/`. The members BEMGen reads:

| Member | Content | In BEMGen |
| --- | --- | --- |
| `schema_version`, `kind`, `version` | `"5.4.0"`, `"program"`, `source` or `filled` | checked before the schema; anything else is `ProgramJsonVersionNotSupported` |
| `id`, `name`, `scope` | the release program ID (re-derived in release 2.0.0, ADR 0046 §8 of the atlas), the name, `program` or `whole_dwelling` | recorded in the preset's `Source`; the name is the default preset name |
| `source` | `program_id` (equal to `id`), `release` (`atlas-release-2.0.0`), `building_type`, `template`, `source_family`, `evidence` | recorded in `Source`; the evidence is kept in the document |
| `loads` | `demand_id`, `type`, `end_use`, `value` (`null` when the source does not record it), `unit`, `basis`, `schedule_id`; for power loads `heat_fractions` (lighting: radiant, visible, return air; equipment: radiant, latent, lost); for hot water `target_temperature_schedule_id` and `inlet_temperature.method`; optionally `value_by_climate`, `schedule_id_by_climate`, `activity_schedule_id` (occupancy), `applies_with`, `host_zone`, `role` | mapped to `LoadDefinition`s (below) |
| `water_heating` (filled) | draw-only water heating: each demand's `draw` (a hot-water load), its heater stages, and `ownership` | a draw owned `per_program_instance` is a hot-water load; one owned `instantiate_once` is left out |
| `controls` | `heating_enabled`, `cooling_enabled` (`null` when not recorded), the setpoint schedules of the sides that are on, `activity_schedule_id`, the people fractions, `conditioning_state`, the humidity setpoint schedules | mapped to the `Thermostat` and the `PeopleProperties`; humidity setpoints are left out |
| `lighting_controls` | `status` (`known` or `unknown`), `daylighting` (or `null`, a source zero), `daylighting_by_climate`, `source`, evidence | the program's `DaylightingControls` (below) |
| `fenestration` | WWR N/E/S/W and the roof skylight ratio of the program's zones (`null`: no exterior surface that way), `value_by_climate` | the preset's glazing when the inputs give none |
| `dwelling` | the dwelling family, construction set, climate, vintage (5.3 minor) | recorded in `Source` |
| `schedules` | schedules by ID, each a `ruleset` (dated rules by day type) or `annual` | the referenced ones are expanded to 8760 values |
| `shared_services`, `building_service_ids`, `water_use_gains`, `source_calendar` | services shared by several zones, building services, hot-water zone gains, the source's holiday rules | left out, each listed in *Left Out* |
| `default_policy_id`, `metadata.resolutions` | the policy and the atlas's recorded resolutions | the count is recorded in `Source`; the resolutions are the *Assumptions* output |
| `required_bindings` | what a consumer must bind | kept in the document; BEMGen binds the calendar through *Year* and *Holidays*, the weather file through *Convert2IDF*, and the rest through its geometry |

## How a JSON becomes a preset

`ProgramJsonImporter.Import(json, options)` runs these steps in order; each stops the read when it finds an error, and every diagnostic carries the JSON Pointer (RFC 6901) of the node it concerns, or the name of the input for an option.

1. **Strict parse** (`StrictJson`): UTF-8 JSON, no byte-order mark, no non-finite number, no repeated member name (`ProgramJsonDuplicateKey`), at most 64 MiB and nesting depth 64 (`ProgramJsonLimits`). The text's SHA-256 is taken from the parsed bytes.
2. **Version:** `kind` must be `program` and `schema_version` `5.4.0` (`ProgramJsonVersionNotSupported` otherwise, before the schema; the message names the retired 2.0.0 when the text has an `export_mode`).
3. **Schema:** validation against the embedded schema (JsonSchema.Net, Draft 2020-12). Every violation is reported with its instance path and keyword; the root `oneOf` reports both branches, so one wrong value can give several lines.
4. **Resolution:** the loads are selected for the **climate zone** and the **construction context** (below), then the contract's checks and the **expansion** of every referenced schedule.
5. **Mapping** to a `ProgramPreset` and the **overrides** of the component's inputs.

### Checks

| Code | Severity | When |
| --- | --- | --- |
| `ProgramJsonInputTooLarge`, `ProgramJsonInvalidJson`, `ProgramJsonDuplicateKey` | Error | The text exceeds the size bound; is empty, has a byte-order mark, a syntax error, a non-finite number, or too deep nesting; or has a repeated member name |
| `ProgramJsonVersionNotSupported` | Error | Not program JSON 5.4.0, such as the retired 2.0.0 |
| `ProgramJsonSchemaViolation` | Error | A rule of the schema is broken |
| `ProgramJsonScheduleIdMismatch` | Error | A schedule's key in `schedules` differs from its `id` |
| `ProgramJsonUnresolvedReference` | Error | A schedule ID used by an instantiated load or the controls is not a key of `schedules` |
| `ProgramJsonScheduleUnitMismatch` | Error | A schedule's unit does not fit its role: load schedules `1`, setpoints and water targets `degC`, activity `W/person`. Units are never converted |
| `ProgramJsonInvalidDate` | Error | A rule's `MM-DD` date is not a date of any year |
| `ProgramJsonAnnualLength`, `ProgramJsonAnnualYearMismatch` | Error | An annual schedule does not hold the hours of its own year, or its year differs from the calendar's *Year* |
| `ProgramJsonHeatFractionsExceedOne` | Error | A load's heat fractions sum to more than 1 (within `ToleranceSettings.AbsoluteFraction`) |
| `ProgramJsonDuplicateDemandConflict`, `ProgramJsonDuplicateDemandMerged` | Error, Warning | Two instantiated loads share a `demand_id` and differ, or are identical (kept once) |
| `ProgramJsonDayNotCovered`, `ProgramJsonDesignDayNotCovered`, `ProgramJsonFebruary29Adjusted` | Error, Warning, Warning | As for every ruleset (below) |
| `ProgramJsonSetpointsCross` | Error | With both sides on and both setpoints given, heating exceeds cooling in some hour by more than `AbsoluteSchedule` |
| `ProgramJsonContextRequired` | Error | A load has `applies_with` on a context key the options do not give (such as `foundation` for a dwelling); the message lists the values the document uses |
| `ProgramJsonClimateZoneNotGiven` | Warning | A load value or schedule, the window ratios, or the daylighting differ by climate, and no climate zone was given; the general value is used, one warning per kind |
| `ProgramJsonValueNotRecorded` | Warning | The source version leaves a value `null`: a load without a value, schedule, or water target (left out), a heat fraction (taken as 0, convective), a control switch (the side is off), a setpoint of a side that is on (the side is off), a people property (BEMGen's default), an unresolved hot-water inlet (BEMGen's 10 °C) |
| `ProgramJsonNotInstantiated` | Warning | An exterior lighting load (no zone), a water heating demand owned once per building, humidity setpoints, or hot-water zone gains: listed in *Left Out* |
| `ProgramJsonSharedServicesLeftOut` | Warning | The JSON has shared services |
| `ProgramJsonDuplicateOverrideLoad`, `ProgramJsonOverrideUnused` | Error, Warning | As before (overrides, below) |

The preset's own rules then apply, with the Core codes of [validation.md](validation.md#program-properties-d-126) and the JSON Pointer or input name as the subject: crossed setpoints, a schedule value outside its kind's range, an unreadable calendar, a WWR outside [0, 1) (`WindowToWallRatio`; an atlas ratio of 1 is refused this way), `DaylightingValue`, and the others. A heat fraction a load type does not have is refused by the 5.4 schema itself.

## Climate zone and construction context

- **Climate zone** (*Climate Zone* input, `ProgramJsonImportOptions.ClimateZone`, the contract's `^[0-8][A-C]$`, upper-cased): `value_by_climate`, `schedule_id_by_climate`, `fenestration.value_by_climate`, and `lighting_controls.daylighting_by_climate` take the zone's entry when there is one, otherwise the general value. Without a zone the general value is used, with `ProgramJsonClimateZoneNotGiven` when the document has entries. A load taken from `value_by_climate` is marked in the document (`ProgramJsonLoad.ValueByClimate`), and the zone is recorded as `ClimateZone` in the preset's source.
- **Construction context** (*Context* input, `key=value` items, `ProgramJsonImportOptions.Context`): a load with `applies_with` (such as the IECC dwellings' `{"foundation": ["crawlspace", "slab", "unheatedbsmt"]}`) is instantiated when every condition's key has a context value among its values, and left out (listed in *Left Out*) otherwise. A key without a context value is `ProgramJsonContextRequired`: keeping both variants would double the load and dropping both would lose it. The context is recorded as `Context`.

## Expanding schedules

Unchanged from D-126: every referenced schedule becomes 8760 hourly values on the calendar of the *Year* input (default 2007, whose 1 January is a Monday) and the *Holidays* input; a leap year is an error. Rulesets use `last_specific_match_else_last_default` in array order; a holiday matches `Hol` only, else the last `Default` rule; `02-29` boundaries move to 1 March or 28 February with a warning; design days (`WntrDsn`, `SmrDsn`) are checked and not used, each schedule with design-day rules gets one *Left Out* line, and the IDF gives design days the Sunday profile. The filled release-2.0.0 schedules resolve holidays as Sundays where the source had no holiday rule (the atlas's `accepted-holiday-sunday`, recorded in `metadata.resolutions`), so the D-126 gap 2 (holidays falling to the prepended `Default` rule) no longer shows for the medium office's lighting and equipment.

## Mapping to the program model

| Contract | BEMGen |
| --- | --- |
| `type` `occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water` | `LoadType.Occupancy`, `Lighting`, `ElectricEquipment`, `GasEquipment`, `DomesticHotWater`; `exterior_lighting` is left out |
| `end_use`, `basis` | `LoadDefinition.EndUse`; `LoadBasis.PerFloorArea`, `PerDwellingUnit`, `PerPerson`, `Absolute` |
| `value` (the climate zone's when given) | unchanged, except hot water × 3600 (m³/s to m³/h) |
| `schedule_id` (the climate zone's when given) | the load's fraction schedule, named after the schedule's `name` (or `id`; two schedules of one name take `name [id]`) |
| `heat_fractions` | `HeatFractions`; a fraction the type does not carry is 0 |
| `target_temperature_schedule_id` | `WaterTemperatures.Target` |
| `inlet_temperature.method` `CorrelationFromWeatherFile` | `WaterTemperatures.InletFromWeatherFile`: EnergyPlus's water mains temperature from the weather file (`Site:WaterMainsTemperature`, below) |
| `inlet_temperature.method` `unresolved` (source version) | BEMGen's constant 10 °C inlet, with a warning |
| `water_heating[].draw` owned `per_program_instance` | a hot-water load like any other (its heater stages are systems and are not modelled; zone gains are excluded, as the contract says) |
| `controls` switches and setpoints | the `Thermostat` sides; a switch not recorded is off; both off is an unconditioned program |
| `controls.activity_schedule_id`, or the occupancy load's | `PeopleProperties.Activity` |
| people fractions | `PeopleProperties.RadiantFraction`, `SensibleFraction`; not recorded: `PeopleProperties.Default`'s |
| `lighting_controls` | `ZoneProgram.Daylighting` (below) |
| `fenestration` | the preset's glazing (below) |
| the calendar | `ZoneProgram.Calendar` and `ProgramPreset.Calendar` |

**Demands that add.** Loads of one type, end use, and basis with different demand IDs are combined by the zone-merge rule ([domain-model.md](domain-model.md#62-rules)), recorded as `Combined.k`. A combined hot-water load on the weather file's mains stays on the mains.

### Daylighting (atlas handoff item 1)

The daylighting fractions of release 2.0.0 are plain program values (atlas user decision L-1; the 1.5.0/1.6.0 flag `geometry_dependent` is gone and is not read). They are applied as given and never recomputed from BEMGen's geometry:

- `status: known` with a `daylighting` block (or the climate zone's `daylighting_by_climate` entry) becomes `DaylightingControls`: `controlled_lighting_fraction`, `illuminance_setpoint_lux`, `control_type` (`continuous`, `stepped`, `continuous_off`), `method` (`split_flux`, `delight`), `minimum_input_power_fraction`, `minimum_light_output_fraction`, `stepped_control_steps`; `availability` is `all_days_except_design_days`.
- `daylighting: null` with `status: known` is a source zero, and `status: unknown` is not recorded: neither gives controls. A program without `lighting_controls` (a dwelling) has none.
- `controlled_floor_fraction`, `controlled_zones`, and `zones` are provenance, recorded in the `Daylighting` source parameter, never an instruction to split zones.
- A mix (*Mix Programs*) and a merged zone take each member's controls by the aggregation rule of [program-presets.md](../research/program-presets.md#7-atlas-programs-program-json-d-126): the controlled lighting power is conserved.
- The controls are source data and provenance: *Convert2IDF* never writes them, since daylight dimming is held fixed as part of the lighting load and never measured as a geometry effect (the owner's decision, D-174; [convert2idf.md](convert2idf.md#daylighting-d-172-d-174)). *Convert2BEM* does not output them either.

### Glazing

The preset's WWR per orientation and skylight ratio come, in this order, from: *WWR North/East/South/West* (`WindowToWallRatios`); the glazing fixture's entry (`ProgramJsonImportOptions.Glazing`, the stand-in of DOE geometry note A2, kept for its tests); *WWR* when connected; the JSON's `fenestration` for the climate zone, a `null` direction taking 0 (no exterior wall there, so no window), recorded as `… (the JSON's fenestration, program_zone_surfaces[, climate zone z], evidence e; …)`; and 0.4 (`default, not from the JSON`). The skylight ratio likewise ends with the JSON's `roof`, then 0. The JSON's ratios are on the true outdoor wall of the program's source zones; a generator reproduces glazed area per orientation and program (DOE geometry note S5).

## Overrides

The inputs after *JSON* complete or override the JSON. Unset, the JSON's value (or the stated default) is used.

| Input | Default | Effect |
| --- | --- | --- |
| *Name* | the JSON's `name` | the preset name; recorded as an override |
| *Space Type* | unset: an any-program preset | the space type the preset applies to |
| *WWR* | unset: the JSON's `fenestration`, else 0.4 | the window-to-wall ratio in [0, 1) on all four orientations |
| *Year*, *Holidays* | 2007, none | the calendar |
| *Loads* | none | each load replaces every JSON load of its type and end use (ignoring case), whatever its basis, or is added; two of one type, end use, and basis are an error |
| *Heating On*, *Cooling On* | the JSON's switches (not recorded: off) | switch each side |
| *Heating Setpoint*, *Cooling Setpoint* | the JSON's schedules | replace the JSON's; used only when that side is on |
| *Activity*, *People Radiant*, *People Sensible* | the JSON's (not recorded: BEMGen's defaults) | the people properties |
| *WWR North* … *WWR West*, *Skylight Ratio* | unset | glazing per orientation and skylight ratio (DOE geometry note S5) |
| *Climate Zone* | unset: the general values | the model's ASHRAE climate zone, such as `5B` (D-172) |
| *Context* | unset | `key=value` items of the construction context, such as `foundation=slab` (D-172) |

Outputs: *Preset*; *Source*; *Assumptions*, the JSON's `metadata.resolutions`, one compact JSON text each; *Overrides*; and *Left Out*, every part of the document the program does not hold. Errors and warnings are runtime messages.

## Provenance

The preset's `Source` is `Provenance.Of("ProgramJson", …)` with: `Json.Id`, `Json.Name`, `Json.Scope`, `Json.Version` (`program JSON 5.4.0, filled|source`), `Json.Sha256`; `Source.ProgramId`, `Source.Release`, `Source.BuildingType`, `Source.Template`, `Source.Family`; `DefaultPolicy` (the policy and the number of resolutions); `Calendar`; `ClimateZone`; `Daylighting` (the controls with their source and evidence, or why there are none); `SpaceType`, `WindowToWallRatio`, and `SkylightRatio` with how each was chosen; `GlazingFixture` when used; `Context` and `Dwelling` when present; one `Override.k`, `Combined.k`, and `SharedService.k` each.

## Library and licences

Unchanged from D-126: **JsonSchema.Net 7.2.3** (MIT) with its dependencies; see [ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md#validation-of-the-json).

## What is left out

- **Shared services**, **building services**, **water heating owned once per building**, **exterior lighting**: not in a zone program; listed in *Left Out*.
- **Water heaters** (the `water_heating` stages): systems, not modelled at ideal-loads grade.
- **Hot-water zone gains** (`water_use_gains`): BEMGen writes water use without zone gains.
- **Humidity setpoints**: ideal loads control temperature only.
- **The source calendar's holiday rules**: give the year's holidays through *Holidays* (resolving the rules is open).
- **Design-day profiles**: checked, not used. **Leap years**: an error.

## Tests and example

`tests/Lod.ProgramJson.Tests/Fixtures/atlas` holds seven release 2.0.0 exports and the schema, pinned by `manifest.json` (the 90.1-2019 medium office in both versions, the DOE Ref 1980–2004 medium office, the IECC 2021 small office, the 90.1-2019 stand-alone retail core with daylighting by climate, the 90.1-2019 full-service restaurant kitchen with per-program water heating, and the IECC 2021 multifamily dwelling); `synthetic/` holds the earlier synthetic fixtures rewritten in the 5.4.0 shape. The medium office preset is compared with hand values from its rules and a golden snapshot (`Snapshots/medium-office-preset.txt`); `ReleaseTwoTests` covers each export, the source version's nulls, the climate zone, the context, the window ratios, and daylighting. `examples/program-json-office.gh` still holds the retired 2.0.0 text and must be rebuilt in Rhino (open, D-172).

## Contract gaps reported to the atlas

From D-126, still open: 1 (29 February), 3 (the vague setpoint rule), 4 (the annual schedule's `allOf` on `rules`), 5 (design-day coverage). Gap 2 is resolved by the filled version's holiday resolution. Reported with release 2.0.0 (D-172) and fixed by the atlas (D-173): the `lighting_controls.daylighting` description in the 5.4.0 schema said the fractions hold for the source model geometry; it now says they are applied as given (L-1).
