# ADR-040: Atlas release 2.4.0 contracts, and the unoccupied lighting cap written on request

- **Status:** Accepted (the cap's default and the reading of G4 for a rule on another zone: Provisional, for the owner)
- **Date:** 2026-11-01
- **Decision log:** [D-253](decision-log.md#d-253--atlas-release-240-contracts-program-json-610-constructions-unchanged-adr-040), [D-254](decision-log.md#d-254--stored-atlas-texts-of-releases-200-to-230-refused-naming-their-240-ids-through-both-id-maps-adr-040), [D-256](decision-log.md#d-256--the-unoccupied-lighting-cap-pnnls-ems-program-per-zone-on-request-off-by-default-the-owners-g4-adr-040)
- **Design note:** [REL-B2, BEMGen 1.10.0 on atlas release 2.4.0](../plans/2026-11-01-rel-b2-atlas-2-4-0.md)
- **Supersedes in part:** [ADR-038](ADR-038-atlas-release-2-3-0-contracts.md) decisions 1 and 3 (the release read and the maps the refusals use)
- **Atlas side:** the atlas's ADR 0060 (the data: the cap, the PNNL office lighting power, the 90.1 elevators and reach-ins, the moved IDs), ADR 0061 (program JSON 6.1.0, the cap's field), and ADR 0062 (release 2.4.0, manifest SHA-256 `51ce9c9e04f3e8d23d4b326d841ef7cc3299b60485cb8a0d2153a3dc3317bd7f`, and `atlas-schedules` 4.1.1)

## Context

Atlas release 2.4.0, a delta on 2.3.0, carries round 2 of the 2026-10-31 review: PNNL's unoccupied lighting cap recorded on every known lighting-controls block (a rule on 19 90.1-2019 programs, an explicit null with its reason on 1,875), PNNL's lighting power for the 11 90.1 whole-building offices, and 84 PNNL elevator and kitchen reach-in services. Program JSON becomes 6.1.0 (one optional field); the construction and building-services contracts do not change, and no construction set moves; 2,301 program IDs move. The owner's G4: BEMGen applies the cap in *Convert2IDF* as PNNL does, per zone, only to zones whose people are not zero at all times.

## Decision

1. **BEMGen reads release 2.4.0's contracts.** Program JSON 6.1.0 only (its schema embedded byte for byte from atlas `7c543f5d`), and the unchanged unified 4.0.0 and detailed 5.0.0, so a construction document of release 2.3.0 is still read: the same contract with the same values (no set moved). `ProgramJsonDocument.KnownReleases` and `AtlasSiteIndex.KnownReleaseManifests` name release 2.4.0 only.
2. **Stored texts of releases 2.0.0 to 2.3.0 are refused by name, as ADR-038 decided for 2.2.0.** A program JSON 5.x or 6.0.0, and a DOE map or atlas mix stored from a site before 2.4.0, are refused with the advice to take them again, naming each program's release 2.4.0 ID: an ID of 2.0.0 to 2.2.0 through release 2.3.0's `id-map-2.3.0.json` and then release 2.4.0's `id-map-2.4.0.json`, an ID of 2.3.0 through the second, both embedded byte for byte (`AtlasIdMap.Maps`). A 2.3.0 text is refused even where its program kept its ID, since its block lacks the cap's statement: an absent field reads as "not stated", which the atlas's explicit nulls replace.
3. **The cap is program data, carried as given.** `UnoccupiedLightingCap` on `ZoneProgram` keeps the atlas's SI cap and threshold (the source's 0.09290304 and 0.093 conversions), the condition, the condition zone, the calling point, the additional lighting while capped, and the source zones' added conditions. A merge or mix keeps it only when every source carries the same rule.
4. **Convert2IDF writes it on request, off by default.** *Lighting Cap* (input 13), `IdfOptions.WriteUnoccupiedLightingCap`, and the suite spec's `settings.unoccupied_lighting_cap` write PNNL's EMS program per zone: occupant-count and lights-rate sensors, lights actuators, the program at the rule's calling point. Off, no EMS object is written and the header, the provenance, an info, and *Left Out* say so.
5. **G4.** A zone is capped only when the people the rule reads are not zero at all times: its own for `zone_occupant_count_zero`, the condition zone's for `other_zone_occupant_count_zero` (the warehouse storages have no people of their own; PNNL caps them while the office is empty, which does not cap them permanently, the purpose of G4). Otherwise `LightingCapNotApplied`.
6. **What BEMGen's zones cannot express.** The condition zone names a source model zone (`Zone1 Office`); BEMGen matches it to its zones by name or ID and, without a match, does not cap the zone rather than read the zone's own zero count. The `zone_conditions` name single source zones (`Perimeter_mid_ZN_2`, `Perimeter_ZN_2`) that BEMGen's zones do not correspond to, so they are not applied: every capped zone takes the general rule, and the header and *Left Out* list them.

## Alternatives

- **The cap on by default.** It is the program's recorded behaviour, and leaving it out leaves the lighting above PNNL's at unoccupied hours (D-257: 2.5 % of the medium office's lighting). Rejected for now, consistently with D-233: like daylighting, the cap makes a zone's lighting depend on its zoning (a merged zone is capped only when all of its sources are empty), so a zoning no longer conserves its reference's hourly lighting (D-157) and the LOD study, which stays on its pinned inputs (D-244), keeps both off. The owner may turn the default.
- **Translate a stored 2.3.0 text that kept its ID.** Rejected: see decision 2.
- **Read the zone's own occupant count when the condition zone is missing.** Rejected: the storages' own people are zero at all times, so they would be capped permanently, what G4 forbids.
- **Apply `zone_conditions` to a BEMGen zone of the same name.** Not done: the conditions use EMS sensors BEMGen does not write (a binary occupancy schedule) and daylight-saving flags BEMGen's standard-time IDFs do not need; a zone named after a prototype zone would be a coincidence. For a later minor if the owner wants it.
- **A merged zone capped when any source carries the cap**, on the capped sources' area. Rejected: the threshold and the condition act on the merged zone as a whole, so the uncapped sources' lighting and people would enter the rule.

## Consequences

- Every program text, DOE map, and mix stored with BEMGen 1.9.0 is refused, naming the 2.4.0 IDs, until *Get from Atlas…* stores it again; the examples holding atlas texts are rebuilt in Rhino (D-260).
- The 90.1-2019 offices, restaurants, retail, and warehouse programs give the same IDFs as before unless *Lighting Cap* is on; their lighting power and IDs follow release 2.4.0.
- In BEMGen's DOE warehouse the storages are not capped (its office zone is named `Office`). Either BEMGen's DOE layouts carry their source zone names, or the atlas records the condition zone's program (90.1 programs carry no `source_zones`): for the owner.
