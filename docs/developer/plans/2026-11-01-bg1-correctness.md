# Stage BG1: correctness fixes from the 2026-10-31 review (design note)

> **Status:** Done (D-211 to D-218) · **Date:** 2026-11-01 · **Decided by:** Cheng Xuan Li (the owner accepted every issue and fix of the 2026-10-31 review on 2026-11-01, with the owner rules quoted below); the controller (the designs below where the owner left the method open) · **Decisions:** D-069, D-162, D-172, D-174, D-201, D-208, D-209, ADR-018, ADR-021, ADR-036; new: D-211 to D-218 · **Branch:** `fix/bg1-correctness` in `D:/bg-bg1`, from `main` at `137db0e` (1.8.0)

The review of 2026-10-31 (five subjects; the evidence of BEMGen's side is the subject-4 review, findings S4-01 to S4-16) gave nine issues to BEMGen in this stage. Stage LOD1 (`scripts/lod-study`, D-219 to D-224) runs in parallel and reruns R4's small-hotel cells once F3b is merged.

| Issue | Finding | Decision | Rule or design |
| --- | --- | --- | --- |
| F3b | S5-11, D-193 | D-211, amends D-201 | §1 |
| A1 | S4-01 | D-212 | §2 |
| F5a | S3-15 | D-213 | §3 |
| A3 | S4-02 | D-214 | §4 |
| A4 | S4-03 | D-215 | §4 |
| B3 | S4-04, S4-05 | D-216 | §4 |
| B7, B8 | S4-06, S4-08, S4-10, S4-11 | D-217 | §4 |
| F2 | S2-12 | D-218 | §5 |

## 1. Heat-transfer options and zones without HVAC (F3b, D-211)

**Owner rule (2026-11-01).** *EnableInternalWallHeatTransfer* off and *EnableFloorHeatTransfer* off make a surface adiabatic only when both zones it separates are conditioned; a surface of a zone without HVAC keeps its interzone link.

- **Why.** R4's 24 failures (D-193) are one zone under three names: the small hotel's 15.05 m² ground-floor elevator core with no HVAC and the 90.1 program's 2133 W/m² (32.1 kW) of equipment. With IWHT off three of its four walls were adiabatic and EnergyPlus diverged in warm-up. Keeping the interzone link of every wall touching a zone without HVAC, the failing site ran a full year with no severe error (2026-11-01, scratch `rule.py`).
- **Where.** `HeatTransferOptions.Exported(surface, isConditioned)` in `Lod.Core.Conversion`, the one function of both converters (D-069), with `For(building)` giving each zone's `ZoneProgram.IsConditioned`. *Convert2IDF* (`IdfGeometry`) and *Convert2BEM* use it, so the two converters keep one meaning of the options. A conditioned zone is one with a thermostat, which *Convert2IDF* gives ideal loads (`ZoneHVAC:EquipmentConnections`).
- **Tests.** The R4 case is rebuilt from the DOE small hotel with the 90.1 elevator core's load (`ElevatorCoreHotel`): the core's interior surfaces are written `Surface` with both options off and no pair joins two conditioned zones; an opt-in EnergyPlus run (`BEMGEN_ENERGYPLUS`) completes the year with no severe error, where the old rule stopped in warm-up.

## 2. Skylight glazing (A1, D-212)

**Owner rule (2026-10-31).** A set with skylight glazing gives the skylights its glazing; a model with skylights and a set without skylight glazing warns and falls back to the vertical glazing; no skylights and no skylight glazing give no message. `Skylight` is not listed as unused when the building has skylights.

- `UnifiedReader` reads the set's `Skylight` component as it reads `ExteriorWindow` (one `simple_glazing` of one `SimpleGlazing` layer). An unsupported or incomplete skylight assembly is read as blocked, not as an import error, so a set stays importable for buildings without skylights.
- `ConstructionSet.Skylight` (`WindowConstruction`, not applicable unless given) and `EnvelopeValues.Skylight` / `EnvelopePreset.Skylight` (`null`: the skylights take the window glazing, as every envelope preset does). `ConstructionSet.Resolve` takes whether the building has skylights: a provided skylight is the preset's; otherwise, with skylights, the warning `SkylightGlazingFromWindow` and the window glazing; a blocked one with skylights is the error `ConstructionBlocked`, as for any role.
- *Convert2IDF* writes the skylight glazing and its construction and gives every skylight that construction; the role line `skylight:` is written when the building has skylights; `Skylight` leaves the unused list when the building has skylights.

## 3. No simulation with an unresolved climate (F5a, D-213)

**Owner rule (2026-11-01).** *Convert2IDF* refuses a program that has climate-dependent values (`value_by_climate`, `schedule_id_by_climate`, window ratios, daylighting by climate) and no resolved climate zone; the zone comes from the *Climate Zone* input, or else from the `.stat` file next to the EPW.

- **Where the resolution happens (the controller's design).** At import, as today: *Program JSON* and the DOE *Programs* components take the zone from their *Climate Zone* input. It cannot move to *Convert2IDF*: a by-climate window ratio has already shaped the generated windows, and a merged zone's loads have already been aggregated from its sources, so a zone chosen at conversion could no longer be applied consistently.
- **What travels.** An import without a climate zone of a document with by-climate values records it in the preset's provenance (`ClimateZone.Unresolved`, a key of `Lod.Core`'s `ClimateResolution`, with the program and what differs by climate zone). Provenance travels with every plan, floor, and building, through mixes and merges.
- **What *Convert2IDF* does.** It walks the building's provenance; any unresolved program is the error `ClimateZoneUnresolved` and no file. The `.stat` file next to the weather file (same name, extension `.stat`), when it states an ASHRAE climate zone (`Climate type "5A" (ASHRAE Standard 196-2006 Climate Zone)`), names the zone to give in the message, and a program resolved for another zone than the `.stat`'s gets the warning `ClimateZoneDiffersFromWeather`. The `.stat` zone is recorded in the IDF header.

## 4. Program JSON fields read past (A3, A4, B3, B7, B8: D-214 to D-217)

- **A3 (D-214).** `water_heating[].delivery_policy` `cap_at_source_outlet`: the draw's hot water is delivered at the heating stage's outlet temperature, so *Convert2IDF* writes the stage outlet as the `WaterUse:Equipment` hot-water supply temperature schedule (a constant), and the import records the cap in *Source*. A policy BEMGen does not know is a warning and a *Left Out* line.
- **A4 (D-215).** A load `fuel` other than natural gas or electricity cannot be metered by `GasEquipment` (natural gas): the import warns (`ProgramJsonFuelNotApplied`) and lists it in *Left Out*. Every per-program water-heating demand with stages gets a *Left Out* line naming its stage fuel and efficiency, which BEMGen does not apply: it reports the hot water's thermal demand (district heating).
- **B3 (D-216).** The DOE *Programs* components' atlas solve gains a *Left Out* output (one branch per key); `source_calendar.daylight_saving` gets a *Left Out* line; the holiday line is written only when the calendar has no holidays.
- **B7, B8 (D-217).** Descriptions and messages corrected without GUID changes (the *Construction JSON* schema version, skylights, the *People* input, the re-export advice, the filled-version advice); a remark on a site release whose manifest SHA-256 is not one BEMGen knows; a warning for each `required_bindings` entry the model does not meet.

## 5. DOE map crosswalk (F2, D-218)

**Owner rule (2026-11-01).** Map small-hotel `GuestRoom`, hospital `Office`, and stand-alone retail `Retail` to the atlas department mixes `GuestRooms_Mixed`, `Office_Mixed`, and `Sales_Mixed` after confirming from the atlas release that their members are the split spaces; keep `Gym - audience` refused.

Members, read from the atlas release records (`data/atlas-releases/v2.0.0/commercial/<template>/<type>/programs/department/`, whose IDs releases 2.1.0 and 2.2.0 keep):

| Template | Key | Mix | Members (area weight) | Confirmed |
| --- | --- | --- | --- | --- |
| 90.1-2007, 2013, 2019 | small hotel `GuestRoom` | `GuestRooms_Mixed` | `GuestRoom123Occ` 0.4535, `GuestRoom123Vac` 0.2347, `GuestRoom4Occ` 0.1931, `GuestRoom4Vac` 0.1188 | yes: the four split guest rooms |
| 90.1-2013, 2019 | hospital `Office` | `Office_Mixed` | `HospitalOfficeFlr1` 0.1087, `HospitalOfficeFlr5` 0.8913 | yes: the two split office floors |
| 90.1-2013, 2019 | stand-alone retail `Retail` | `Sales_Mixed` | `Front_Retail` 0.0793, `Core_Retail` 0.8414, `Point_of_Sale` 0.0793 | **no**: `Point_of_Sale` is also its own key of the map, so its program would count twice |

So the crosswalk maps `GuestRoom` and the hospital's `Office`; `Retail` stays refused, as does `Gym - audience`, until the atlas publishes a mix of the split retail spaces alone (reported to the owner).
