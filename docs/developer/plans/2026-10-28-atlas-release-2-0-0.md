# Atlas release 2.0.0 contracts

> **Status:** Done, pending the owner's reading (D-172, D-173, D-174); merged into `main` (PR #2) and released in `v1.5.0` (D-175) · **Date:** 2026-10-28 · **Branch:** `claude/atlas-2-0-0-contracts`, from `feature/doe-geom` (`a527da5`) · **ADR:** [ADR-027](../decisions/ADR-027-atlas-release-2-0-0-contracts.md) · **Atlas:** release 2.0.0 (atlas ADR 0046), handoff note `docs/bemgen-handoff-release-2-0-0.md` of the atlas, read at atlas commit `188c4ead` (atlas PR #27); fixtures re-pinned to the corrected release at atlas commit `f617b30b` (atlas PR #28, its handoff note section 4 and ADR 0046 section 11; D-173)

## Goal

Move BEMGen's readers of the atlas's program JSON and construction JSON, their vendored schemas, and their tests to the export contracts of atlas release 2.0.0, and apply the three items of the atlas's handoff note: daylighting fractions as plain values, IDs re-derived once (`id-map.json`), and the PNNL prototype constructions as `alternates`.

## 1. Inventory: where BEMGen reads atlas JSON

| Place | What it reads | Before | After |
| --- | --- | --- | --- |
| `src/Lod.ProgramJson` (`ProgramJsonReader`, `DocumentBuilder`, `ProgramJsonSchema`, `Import/PresetMapper`) | program JSON | 2.0.0 `defaulted` (D-126), schema `program-json-v2` | 5.4.0 `source` and `filled`, schema `program-json-v5.4` |
| `src/Lod.ProgramJson/Import/ProgramGlazingFixture` | BEMGen's glazing stand-in keyed by `source.program_id` | the v0.1.1 ID `program-8c35a40eb0181596e0bfcac4` in its test fixture | kept (lower precedence than inputs, higher than the JSON's `fenestration`); its test fixture keyed by the 2.0.0 ID |
| `src/Lod.ConstructionJson` (`ConstructionJsonImporter`, `UnifiedReader`, `DetailedReader`) | construction JSON | unified 2.0.0, detailed 3.0.0 (packet v7, D-145) | unified 3.1.0, detailed 4.3.0 |
| `src/Lod.Grasshopper/Components/ProgramJsonComponent`, `ConstructionJsonComponent` | the text, through the libraries | — | *Program JSON*: *WWR* optional, *Climate Zone* and *Context* appended; *Construction JSON* unchanged |
| `scripts/TestSuiteGenerator` | program JSON and unified sets named in a suite spec, through the libraries | — | unchanged code; its tests use the 2.0.0 fixtures |
| `scripts/rhino-smoke/specs/program-json.py`, `glazing.py`, `examples.py`, `construction-json.py` | the fixtures | v2 and packet v7 | the 2.0.0 fixtures, expectations updated |
| `examples/program-json-office.gh` | a program JSON 2.0.0 text in a panel | — | rebuilt with the 5.4.0 filled export for `v1.5.0` (D-175) |
| DOE presets of `feature/doe-geom` (`DoeProgramPresets`, layout records) | none: illustrative example presets and DOE IDF zone names | — | nothing to change; the atlas loads (A1) are still pending |
| Building services 1.0.0, source model constructions 1.0.0 | not read by BEMGen | — | not read (no consumer yet; open) |

**What changes from 2.0.0 to 5.4.0 (program).** `version` (`source`/`filled`) replaces `export_mode` (`raw`/`defaulted`); the source block gains `release` and `source_family` and drops `definition_release` and `evidence_view`; `assumptions` become `metadata.resolutions`; values may be `null` in `source`; loads gain `value_by_climate`, `schedule_id_by_climate`, `applies_with`, `host_zone`, `role`, `fuel`, an occupancy load's `activity_schedule_id`, and the type `exterior_lighting`; heat fractions carry only the members of their type; a hot-water load's inlet is a method (`CorrelationFromWeatherFile` or `unresolved`), not a schedule, and the filled version moves hot water into `water_heating` draws; controls gain `conditioning_state` and humidity setpoints, and a side that is off has no setpoint; new top-level `lighting_controls`, `fenestration`, `source_calendar`, `source_spaces`, `source_zones`, `water_use_gains`, `building_service_ids`, `alternates`, `dwelling`; `id` is the release program ID.

**What changes from 3.0.0 to 4.3.0 (detailed) and 2.0.0 to 3.1.0 (unified).** Only additions: the infiltration's design-flow methods (`natural_ach` no longer required), an `evidence_id` on mass entries, `alternates` (detailed), `fenestration_defaults` (unified). The 19 packet v7 contexts re-exported from release 2.0.0 have equal values (checked within 2e-9 relative), new IDs, and the additions.

## 2. Compatibility decision

BEMGen reads **only** the release 2.0.0 contracts; the older versions are refused with a message to export again (D-172, ADR-027). Reasons: release 2.0.0 is the only release the atlas keeps and its exporters refuse 1.x; D-064 waives backward compatibility; D-126 and D-145 retired earlier readers the same way; the program contract changed shape; and the construction change is additive, so the packet's tests carry over to re-exported contexts with equal values.

## 3. Design

- **Program JSON 5.4.0** ([program-json.md](../architecture/program-json.md)): both versions; resolution by climate zone and construction context; unrecorded values left out or defaulted with `ProgramJsonValueNotRecorded`; parts a zone program cannot hold listed in *Left Out* with `ProgramJsonNotInstantiated`.
- **Daylighting** (handoff item 1): `DaylightingControls` on `ZoneProgram`, from `lighting_controls` as given; merged by conserving the controlled lighting power ([program-presets.md §6.2, §7](../research/program-presets.md#7-atlas-programs-program-json-d-126)); never written by *Convert2IDF* (D-174, [convert2idf.md](../architecture/convert2idf.md#daylighting-d-172-d-174)): the owner decided on 2026-10-29 that IDF runs never include dimming. D-172's opt-in writer (`IdfOptions.WriteDaylighting`) and the run check's acceptance of EnergyPlus's partial-control warning are removed.
- **Water mains:** `WaterTemperatures.InletFromWeatherFile`, written as a blank cold-water schedule with `Site:WaterMainsTemperature` `CorrelationFromWeatherFile`.
- **IDs** (handoff item 2): BEMGen stores no atlas ID of releases 1.x or 2.0.0. A scan of `feature/doe-geom` (`a527da5`) for ID-shaped strings found 2,519 candidates and none among the 11,507 keys of `id-map.json`; the only stored atlas IDs were v0.x content hashes (`program-8c35…`, `construction-set-…`, `equivalent-assembly-…`, `foundation-assembly-…`, `foundation-material-…`) in tests, docs, and the synthetic glazing fixture, which predate the map. They were re-keyed to release 2.0.0 by structural matching of the re-exported documents (the same program or construction context), not by the map; nothing is recomputed.
- **Alternates** (handoff item 3): read into `DetailedConstructionDocument.Alternates`, one *Roles* line each, never assigned; the unified set of the same context converts as before.
- **Fixtures:** `scripts/atlas-fixtures/export_fixtures.py` (seven programs, 21 construction pairs, schemas, notices), pinned by manifests with the atlas commit: `f617b30b1ca1552364af648a82797d2b39854c01`, release manifest SHA-256 `b7ce92a1694a85b42746bdc57ffa0ed1f21f11384561184af078d95a4865e40e` (D-173; first `188c4ead`, D-172). The script runs the atlas with `PYTHONHASHSEED=0`, since the atlas's key order follows Python's string hashing in places (item 6 below).
- **Mass contract 1.1.0 (D-173):** `construction-mass-accounting-v1.1` replaces 1.0.0 as the embedded schema the `mass_accounting` section is checked against; it is 1.0.0 with the optional mass-entry `evidence_id` that the detailed 4.3.0 and unified 3.1.0 schemas already embed. Nothing BEMGen reads needs 1.0.0, so it is not kept beside it.

## 4. Atlas defects found (reported, not worked around)

The atlas answered in its PR #28 (handoff note section 4, ADR 0046 section 11) and BEMGen took the corrected release (D-173): items 1 to 3 are fixed in the atlas, items 4 and 5 are not defects, and the IECC infiltration stays the source's method.

1. **IECC construction sets break the shared mass contract.** Their `mass_accounting.additional_mass.entries[*]` carry `evidence_id`, which the detailed 4.3.0 and unified 3.1.0 schemas allow but `construction-mass-accounting-v1` (which the section must also meet) forbids. BEMGen refused them with `ConstructionJsonSchemaViolation`. **Fixed (D-173):** the shared mass contract 1.1.0 allows the field; BEMGen embeds 1.1.0 and reads the IECC sets.
2. **IECC detailed sets file a ground floor under `InteriorFloor`.** The ground storey core's F-factor floor (`Core_bot_ZN_5_Floor`, boundary `Ground`, with a ground method) is an `InteriorFloor` assignment (target `Surface`/`Adiabatic`); the foundation contract allows ground methods on ground floors and foundation walls only. **Corrected in place (D-173):** in the five affected IECC types of every edition the adiabatic F-factor slabs with `PerimeterExposed` 0 are in the `GroundFloor` building default (rule `source_boundary_correction`); 30 set IDs changed, mapped by `id-map.json` (the fixture's `…8e0c58` is now `…a8a7b6`). BEMGen had no workaround to remove; its check that refuses a ground method on an `InteriorFloor` assignment stays, now pinned by a synthetic test.
3. **Schema text out of date.** The 5.4.0 schema's `lighting_controls.daylighting` description still says the fractions hold for the source model geometry, which user decision L-1 superseded; the schema also still allows `geometry_dependent` (harmless; release 2.0.0 files do not carry it). **Fixed (D-173):** the description now says the fractions are applied as given; the schema is embedded byte for byte again.
4. **Values moved by one ULP.** Some fitted unified absorptances changed from 0.45 and 0.9 (packet v7) to 0.44999999999999996 and 0.8999999999999999, within the stated 1e-9 relative; two BEMGen tests now assert the new values. **Not a defect** (atlas answer): area-weighted means in IEEE arithmetic; compare with a tolerance.
5. **Alternate area shares are rounded to six decimals** and sum to 0.999999 or 1.000001 for some roles. **Not a defect** (atlas answer); BEMGen does not check the sum.
6. **Export bytes depend on the hash seed (found with D-173).** The same export under `PYTHONHASHSEED` 0 and 1 gives JSON-equal documents with some keys in another order, so a byte-for-byte check of an export holds only for a fixed seed. BEMGen's exporter fixes it at 0; to be reported to the atlas.

## 5. Open

- For a person in Rhino 8: the canvas of *Program JSON* with its two new inputs. (`examples/program-json-office.gh` was rebuilt headless and the full smoke run passed for `v1.5.0`, D-175.)
- *Convert2BEM* does not output daylighting controls; D-174 names IDF runs, so whether it ever should is the owner's call.
- The IECC sets' zone design-flow infiltration is not converted, so the IECC sets, readable since D-173, still do not convert (the atlas keeps the source's method and defers a building-level equivalent to its IECC unified representation); the PNNL alternates are not modelled (splitting surfaces by `area_share`).
- Building services 1.0.0 and the source model constructions are not read; the source calendar's holiday rules are not resolved.
- The owner's reading of D-172, D-173, and ADR-027 (D-174 is the owner's own decision).
