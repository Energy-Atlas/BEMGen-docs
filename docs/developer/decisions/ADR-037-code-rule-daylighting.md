# ADR-037: Opt-in code-rule daylighting on BEMGen's geometry

- **Status:** Accepted
- **Date:** 2026-11-01
- **Decision log:** [D-233](decision-log.md#d-233--opt-in-code-rule-daylighting-the-program-says-whether-and-how-bemgens-geometry-says-where-amends-d-174-adr-037), [D-234](decision-log.md#d-234--occupancy-sensors-and-time-switches-in-the-schedules-and-power-densities-an-occupancy-driven-cap-left-to-the-atlas), [D-235](decision-log.md#d-235--the-prototype-check-of-code-rule-daylighting-on-four-doe-prototypes)
- **Design note:** [stage BG3](../plans/2026-11-01-bg3-daylighting.md)
- **Amends:** [D-174](decision-log.md#d-174--no-daylight-dimming-in-idf-runs-ever-the-daylighting-writer-removed-the-controls-kept-as-source-data) (its "never" becomes the default) and [ADR-027](ADR-027-atlas-release-2-0-0-contracts.md) decision 4 (*Convert2IDF* never writes the controls)

## Context

Programs from *Program JSON* carry the atlas's daylighting controls (`ZoneProgram.Daylighting`, D-172): the settings of the PNNL prototypes' `Daylighting:Controls` and the share of lighting power they controlled in the source models. D-172 wrote them as one reference point per glazed zone controlling that recorded share; D-174, the owner's decision, removed the writer, since dimming makes a zone's lighting depend on its windows and a zoning would then not conserve its reference's hourly lighting (D-157). The recorded shares belong to the source's zones and windows, so on BEMGen's other zonings and glazing they would control lights that are not daylit, or miss lights that are. The 2026-10-31 review (issue F5) asked for a way to model daylighting where it is wanted without giving up D-174 for the LOD study.

## Decision

1. **Off by default.** *Convert2IDF* writes no daylighting object unless its *Daylighting* input (`IdfOptions.WriteDaylighting`, the test-suite spec's `settings.daylighting`) is on. D-174's rule is the default; the LOD study keeps it.
2. **The program says whether and how.** A zone's program with `DaylightingControls` and lights is a candidate; the setpoint, control type, minimum input power and light output fractions, steps, and method are the program's. Availability "all days except design days" is written as always available, since the IDF runs no design days.
3. **BEMGen's geometry says where.** `CodeDaylighting` computes the 90.1 toplit, primary, and secondary sidelit areas from the zone's own windows (head height and width) and skylights as openstudio-standards computes them for the prototypes, applies the edition's control requirements, and places up to two reference points at 0.8 m, each controlling its area's share of the zone. The edition is the program's template's: 90.1-2010, or the shared 90.1-2013 to 2019 rule. The office whole-building non-geometry fractions apply where openstudio-standards applies them.
4. **The program's recorded shares are provenance.** `ControlledLightingFraction` and the source's floor fraction are not used to write controls; a merged zone's areas come from its own geometry, and it keeps its lead source's settings and rule.
5. **No code rule, no controls.** A program whose template has no openstudio-standards daylighting rule (IECC, DOE reference, 90.1-2004 and 2007) or whose space type openstudio-standards finds not appropriate for daylighting is carried and not placed, with a warning.
6. **Warnings and checks follow the option.** EnergyPlus's partial-control warning is expected only for an IDF that holds daylighting controls; the export tests' parse-back checks fail any daylighting object unless a test asks for it.

## Consequences

- With the option off every IDF is as before D-233; a building whose programs carry controls gets a reworded header line and info. No snapshot changes except the program preset's new `DaylightingRule` source line.
- With it on, the lighting of a site depends on its zoning's windows, so paired metrics can report the site unpaired on internal loads (D-157), as intended: the option is for studies of daylighting, not for the LOD study.
- On the DOE prototypes BEMGen generates, the controlled floor and lighting fractions follow the prototype's where BEMGen's geometry resembles it (the primary school's zones exactly, the medium office's perimeter share) and differ where it does not (the retail and warehouse skylights the DOE reference records do not have), D-235.
- IECC programs get no controls until a rule is chosen for them.
- The occupancy-driven unoccupied lighting cap of the 90.1-2016 and 2019 prototypes is not modelled; it is the atlas's to record (D-234).

## Alternatives

- **Write the program's recorded share at one point (D-172).** Rejected: it applies the source's geometry to BEMGen's, which the review found wrong for every zoning but the source's.
- **Split zones into daylit and non-daylit parts.** Rejected (ADR-027): a zoning change for a control.
- **Place points at fixed depths without the code rule.** Rejected: the owner asked for the code's definitions, which the prototype fractions can then check.
- **Use openstudio-standards' 2.5 ft point height.** Not taken: the owner's method fixes 0.8 m; the difference (0.038 m) is recorded.
- **Apply the 90.1-2019 rule to IECC programs.** Left to the owner: openstudio-standards has no IECC rule, and IECC's daylight zone definitions differ in detail.
