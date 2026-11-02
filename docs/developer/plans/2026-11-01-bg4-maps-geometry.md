# Stage BG4: DOE maps and geometry by family (design note)

> **Status:** Done (D-246 to D-251) · **Date:** 2026-11-01 · **Decided by:** Cheng Xuan Li (the owner's answers to issues G1, G3, G6, and G9 of the 2026-10-31 review, round 2: "follow the source evidence"); the controller (the realisation below where the answers leave it open) · **Decisions:** D-209, D-212, D-218, D-233, D-235, D-241, ADR-036, ADR-037; new: D-246 to D-251, [ADR-039](../decisions/ADR-039-doe-skylights-by-family.md) · **Branch:** `feat/bg4-maps-geometry` in `D:/bg-bg4`, from `main` at `5b73e0b` (1.9.0, atlas release 2.3.0)

| Issue | Owner's answer | Decision | Section |
| --- | --- | --- | --- |
| G1 | Stand-alone retail: the generator keys its zones by family; 90.1-2013, 2019, and every IECC family give `Core_Retail` and `Front_Retail` their own atlas programs, DOE Ref and 90.1-2007 keep `Retail`; no atlas mix | D-246, amends D-218 | §1 |
| G3 | IECC programs take the 90.1-2019 code-rule daylighting | D-248, amends D-233 | §2 |
| G6 | Skylights in the DOE geometry only where the source geometry carries them, per family where they differ | D-249, ADR-039 | §3 |
| G6 | D-235's prototype check of retail and warehouse run again | D-250 | §4 |
| G9 | IECC offices: every office key takes the folder's whole-building program, as PNNL's IECC model gives every zone that program; the window says the rooms are not distinguished | D-247, amends D-241 | §5 |

## 1. Stand-alone retail keys (G1, D-246)

- **Source.** The DOE Ref zones `Core_Retail` and `Front_Retail` are both the openstudio-standards space type `Retail` in the DOE Ref geometry (`DOERefRetailStandalone.osm`), which is how the layout record keyed them (`osm_space`). The atlas follows its sources: `Retail` in DOE Ref pre-1980, 1980–2004, and 90.1-2007; `Core_Retail` and `Front_Retail` (identical loads, the core with the skylight daylighting rule) in 90.1-2013, 2019, and the six IECC families.
- **Realisation.** The generator cannot know a map's family, so the zones are keyed by their own space types once and the families that lack them take `Retail` through the crosswalk: the layout record keys `Core_Retail` and `Front_Retail` by the 90.1-2013 geometry that openstudio-standards' `ashrae_90_1_2013.prototype_inputs.json` names for the type (`ASHRAE9012013RetailStandalone.osm`, spaces of those names with those standards space types; link `osm_space_2013`), and `DoeAtlasFolders.Crosswalk` gives `Core_Retail → Retail` and `Front_Retail → Retail` in DOE Ref pre-1980, 1980–2004, and 90.1-2007. `AtlasSiteIndex.MatchKeys` now matches a crosswalk target among the folder's `source` programs first and then its one `department` mix (D-218). Each zone's glazing is its own: the record's `programGlazing` splits `Retail` into the two keys (south 0.248352 is the front's; the core has no south wall), so the window area is unchanged.
- **Window.** A key crosswalked to a source program is named in the coverage (`Core_Retail and Front_Retail take Retail, the family's one program of both zones`). The gaps of 90.1-2013, 2019, and IECC are `Gym - audience` only.
- **Daylighting.** `CodeDaylighting` takes the program's openstudio-standards space type, not the key: the `Core_Retail` and `Front_Retail` programs of 90.1-2013 and 2019 keep their exceptions; DOE Ref and 90.1-2007 have no code rule; IECC follows §2.
- **Changed outputs.** The retail record, its answer key, and every retail snapshot and test that names the key `Retail`. A stored retail atlas map of 1.9.0 is refused for its keys (use *Get from Atlas…* again).

## 2. IECC daylighting (G3, D-248)

- `DaylightingCodeRule.For` gives an IECC template (`IECC 2006` to `IECC 2021`) the 90.1-2013 to 2019 rule set (`DaylightingCodeEdition.Ashrae2013`, openstudio-standards 90.1-2019's methods), recorded as the owner's rule.
- IECC programs carry no `space_types` evidence and no `standards_rule`. Their openstudio-standards space type is the program's `name` before `_<source.building_type>` (`WholeBuilding - Sm Office_SmallOffice`, `Core_Retail_RetailStandalone`), checked against that suffix (no space type otherwise), and their building type `standards_building_type`. The office whole-building non-geometry fractions come from openstudio-standards 90.1-2019's `spc_typ` (pinned `c8c1b9eb`, SHA-256 `d3b988cb…c0e72`): `WholeBuilding - Sm Office` 0.43 / 0.14, `WholeBuilding - Md Office`, `- Lg Office`, `- Lg Office-basement`, `- Lg Office-others` 0.68 / 0.32, applied only where the rule applies them (Office, `WholeBuilding`).

## 3. Skylights by family (G6, D-249, ADR-039)

**Sources read** (`scripts/doe-geometry/family_skylights.py`, every file's SHA-256 recorded in the output's digests):

| Family | Source geometry | Skylights found |
| --- | --- | --- |
| DOE Ref pre-1980, 1980–2004 | DOE Ref v1.4 Pre1980 and Post1980 IDFs, 16 climates each; openstudio-standards `DOERef*.osm` | none in any type |
| (the layout records) | DOE Ref v1.4 New2004 Chicago | the schools' gyms only |
| 90.1-2007 | PNNL 90.1-2007 IDFs, 19 climates; the supermarket (no PNNL model) `ASHRAESuperMarket.osm` | retail core 6.69 m², warehouse bulk 14.86 m², schools' gyms as New2004 |
| 90.1-2013, 2019 | PNNL 90.1 IDFs; the supermarket `ASHRAE9012013SuperMarket.osm` | retail core 23.78 m², warehouse fine 20.81 and bulk 47.57 m² outside 6A, 6B, 7A, 8A, where the 90.1-2004/2007 skylights stand (openstudio-standards' `model_custom_geometry_tweaks`); schools' gyms; supermarket main sales 35.67 m² |
| IECC 2006, 2009 | PNNL IECC IDFs | as 90.1-2007 |
| IECC 2012 | PNNL IECC IDFs | retail core 23.78 m² in every climate; warehouse fine 25.27 and bulk 71.35 m² in every climate |
| IECC 2015 to 2021 | PNNL IECC IDFs | as 90.1-2013 and 2019 |

Every other type has no skylight in any family's source. The openstudio-standards template geometries agree with the PNNL IDFs where both exist (the 1–5 climate groups).

- **Data.** `src/Lod.Generators/Doe/Skylights/family-skylights.json` (embedded): per type and family, the climate groups and per key the source skylight area, the key's source roof area (the answer key's, as the record's ratio), and the ratio; a group marked `default` is the template's own geometry (the largest group).
- **Use.** `DoeProgramPresets.KeyRatios(type, key, template, climateZone)` keeps the record's window ratios and takes the family's skylight ratio; a climate zone outside every group, or none, takes the default group, with `ClimateZoneAssumed` when the groups differ. The DOE *Programs* components use it for an atlas map (the map's family, the *Climate Zone* input; a warning when the zone is assumed), and the test-suite generator's `record` glazing for a DOE slot whose programs all name one family's template (their atlas IDs' first segment). The illustrative presets keep the record's glazing (New2004).
- **Changed outputs.** Atlas maps and record-glazing suites of retail, warehouse, and supermarket gain toplit roofs where their family's source has them; the schools' gyms lose theirs in the DOE Ref families.

## 4. The prototype check again (D-250)

The suite generator's 90.1-2019 5A stand-alone retail and warehouse (*No Simplification*, *Stack*, `settings.daylighting: true`, record glazing) with their atlas release 2.3.0 programs, against the PNNL 90.1-2019 Buffalo IDFs, by one scratch script for both (controlled floor fraction: the floor of zones with controls; controlled lighting fraction: each zone's lighting power times its points' shares).

| Prototype | Controlled floor fraction, BEMGen / PNNL (D-235's BEMGen) | Controlled lighting fraction, BEMGen / PNNL (D-235's BEMGen) |
| --- | --- | --- |
| Stand-alone retail | 0.698 / 0.698 (0.066) | 0.090 / 0.387 (0.012) |
| Warehouse | 1.000 / 1.000 (0.052) | 0.208 / 0.492 (0.058) |

The skylight area is the source's, so the toplit zones are PNNL's; the lighting each controls is a quarter to a half of PNNL's, because BEMGen's skylight rule (S5) places one centred skylight per roof, whose toplit area is far smaller than that of the source's sixteen (retail) or 32 and 14 (warehouse) spread ones. Details in D-250.

## 5. IECC offices (G9, D-247)

- **Site** (release 2.3.0): the IECC `small-office` folders hold `WholeBuilding - Sm Office` and `Attic`; `medium-office` `WholeBuilding - Md Office` and `Plenum`; `large-office` `WholeBuilding - Lg Office-others` (the above-grade zones), `- Lg Office-basement`, `OfficeLarge Data Center` (`DataCenter_bot/mid/top_ZN_6`), `OfficeLarge Main Data Center` (the basement's), and `Plenum`, all source only.
- **Decision.** `DoeAtlasFolders` holds the offices in the IECC families at those folders (not the `-detailed` ones); the crosswalk gives every office key the folder's whole-building program (`WholeBuilding - Lg Office-others` for the large office, whose BEMGen storeys are all above grade, G3), except the large office's `OfficeLarge Data Center`, which matches its own source program as the PNNL IDF gives those zones their own loads. BEMGen's office layouts have no plenum, attic, or basement key (G1, G2, G3), so `Plenum`, `Attic`, `- basement`, and `Main Data Center` take no key. The coverage says `the rooms are not distinguished in this family: every room key takes WholeBuilding - …, as PNNL's IECC model gives every zone`. The supermarket stays unoffered (no IECC folder).

## 6. Tests (test first)

Listed with each decision in the log. The site fixtures are recorded again from the live release 2.3.0 index with the IECC office folders (`record_site_fixtures.py`).

## 7. Open

- Rhino checks for a person: the smoke checklist's BG4 items. The headless smoke specs whose expectations move are updated, not run.
