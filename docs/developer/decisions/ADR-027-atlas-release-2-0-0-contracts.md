# ADR-027: Atlas release 2.0.0 contracts — program JSON 5.4.0, constructions 4.3.0 / 3.1.0, daylighting controls

> **Status:** Proposed by the controller (D-172, amended by D-173 and D-174), pending the owner's reading · **Date:** 2026-10-28 · **Supersedes in part:** ADR-018 (the program JSON 2.0.0 reader), ADR-023 (the packet v7 pin) · **Design note:** [2026-10-28-atlas-release-2-0-0.md](../plans/2026-10-28-atlas-release-2-0-0.md)

## Context

The Energy Archetype Atlas replaced its releases 1.0.0 to 1.6.0 and its frozen folders with release 2.0.0, a full snapshot and the only release in its tree (atlas ADR 0046). Its exports are program JSON 5.4.0 (versions `source` and `filled`), detailed constructions 4.3.0, unified constructions 3.1.0, building services 1.0.0, and the dwellings' source model constructions 1.0.0. BEMGen read program JSON 2.0.0 (D-126) and the packet v7 constructions, detailed 3.0.0 and unified 2.0.0 (D-145). The atlas's handoff note for 2.0.0 lists three changes: daylighting fractions as plain values, IDs re-derived once with `id-map.json`, and PNNL prototype constructions as `alternates`.

## Decision

1. **Read only the release 2.0.0 contracts.** The program JSON 2.0.0 reader and the detailed 3.0.0 / unified 2.0.0 readers are retired, and their documents are refused with a message to export again from release 2.0.0.
2. **Read both program JSON versions.** The IECC programs and the code-prototype dwellings export only `source`, so BEMGen reads it: a value the source does not record (`null`) is never invented. A load without a value or schedule is left out, a heat fraction is 0 (convective), a control side is off, and a people property takes BEMGen's default, each with `ProgramJsonValueNotRecorded`, and the inputs can complete them.
3. **Resolve by climate zone and construction context at import.** New inputs *Climate Zone* and *Context* select `value_by_climate`, `schedule_id_by_climate`, the window ratios, and the daylighting by climate, and the loads whose `applies_with` matches. A missing context key is an error; a missing climate zone takes the general values with a warning.
4. **Daylighting controls are a program property** (`ZoneProgram.Daylighting`), applied as given. A merged zone conserves the controlled lighting power, `c* = Σ cᵢ·Pᵢ / Σ Pᵢ`, and takes the settings of the source with the most controlled power. *Convert2IDF* never writes them (D-174): daylight dimming is held fixed as part of the lighting load, never measured as a geometry effect.
5. **The hot-water inlet may be the weather file's water mains** (`WaterTemperatures.InletFromWeatherFile`), written as a blank cold-water schedule with `Site:WaterMainsTemperature` `CorrelationFromWeatherFile`.
6. **Construction additions are information.** `alternates` (detailed 4.3.0) and `fenestration_defaults` (unified 3.1.0) are read and never assigned. A set whose infiltration is the source's zone design flow (`source_design_flow`) is read as evidence and refuses conversion. The `mass_accounting` section is checked against the shared mass contract 1.1.0 (D-173), which adds the optional mass-entry `evidence_id` the document schemas embed.
7. **Fixtures are release exports, written by a script.** `scripts/atlas-fixtures/export_fixtures.py` runs the atlas's own export command (with `PYTHONHASHSEED=0`, D-173) and pins every file by SHA-256 with the atlas commit; the 19 packet v7 contexts are re-exported under their old names.

## Alternatives

- **Keep reading the 1.x and packet v7 versions beside 2.0.0.** Rejected: nothing produces them any more (the atlas refuses 1.x releases and keeps them only at a tag), D-064 waives backward compatibility, and D-126 and D-145 retired earlier readers the same way. The program contract changed shape (`version` in place of `export_mode`, the inlet as a method, optional setpoints, a hot-water draw in `water_heating`), so two program readers would share little. The constructions changed only additively, so their tests move to the 2.0.0 exports of the same contexts with equal values (checked to 2e-9 relative).
- **Read only the filled version.** Rejected: the IECC programs and dwellings have no filled version.
- **Recompute daylighting from BEMGen's geometry.** Rejected by the atlas's user decision L-1 and the handoff note: the fractions are program values like a lighting power density.
- **Split a zone into daylit and non-daylit parts by `controlled_floor_fraction`.** Rejected by the handoff note: the floor fraction and zone counts are provenance.
- **Average the daylighting settings in a merge.** Rejected: setpoints and control types are controls, not quantities; averaging a stepped and a continuous control has no meaning. The atlas takes the settings of the zone with the most lighting power for a program; BEMGen applies the same rule to a merge.
- **Map an `unresolved` inlet to the weather file's mains.** Rejected: that would invent the source's value; BEMGen's 10 °C is its documented default (and EnergyPlus's mains temperature without a `Site:WaterMainsTemperature`), recorded with a warning.
- **Convert the IECC sets' zone design-flow infiltration to one building rate.** Rejected: the rules name the source model's zones and carry a wind coefficient, which BEMGen's building-level infiltration (D-124) does not hold. Left open.

## Consequences

- *Program JSON* takes release 2.0.0 programs of every family; definitions holding a 2.0.0 text must be given a release 2.0.0 export; `examples/program-json-office.gh` was rebuilt with one for `v1.5.0` (D-175).
- Programs with daylighting controls do not change the IDF's objects (D-174): the controls are never written, and the file's header and an info name the zones that carry them. Presets without controls, and every existing snapshot, are unchanged. (D-172 had written one `Daylighting:Controls` and `Daylighting:ReferencePoint` per glazed zone on request; D-174 removed that writer.)
- The filled version's hot water runs on the weather file's mains temperature in place of the D-126 default 10 °C.
- Two atlas defects made the IECC construction sets unreadable as first exported (D-172); BEMGen did not work around them. The atlas fixed both in release 2.0.0 in place (mass contract 1.1.0; the IECC ground slabs under `GroundFloor`), and BEMGen took the corrected release (D-173): the IECC sets are read, and their source design-flow infiltration is now the only reason they do not convert.
- `Convert2BEM` does not output daylighting controls (open).
