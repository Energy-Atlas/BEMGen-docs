# Stage BG3: opt-in code-rule daylighting on BEMGen's geometry (design note)

> **Status:** Done (D-233 to D-236, [ADR-037](../decisions/ADR-037-code-rule-daylighting.md)) · **Date:** 2026-11-01 · **Decided by:** Cheng Xuan Li (the owner accepted issue F5 (b) of the 2026-10-31 review on 2026-11-01 with its method "all as proposed"); the controller (the realisation below where the method leaves it open) · **Decisions:** D-157, D-172, D-174, D-213, ADR-027 decision 4; new: D-233 to D-235 · **Amends:** D-174 (its "never" becomes the default) and ADR-027 decision 4

The review's issue F5 (b) asked whether BEMGen should ever write the daylighting controls that *Program JSON* carries (`ZoneProgram.Daylighting`). D-172 had written one reference point per glazed zone controlling the program's recorded fraction, and D-174 removed that writer ("no daylight dimming in IDF runs, ever"). The owner's method keeps D-174 as the default and adds an opt-in in which **the program says whether and how and BEMGen's geometry says where**.

## 1. The owner's method (F5 b)

- **Whether and how: the program.** `daylighting` present or null; control type, setpoint, minimum input power and light output fractions, steps, availability, method (`ZoneProgram.Daylighting`, read as before).
- **Where: BEMGen's geometry.** The 90.1 primary and secondary sidelit areas from each window's head height and width, and toplit areas under skylights, as openstudio-standards computes them for the prototypes. Per zone up to two `Daylighting:ReferencePoint`s at 0.8 m (one in the primary area, one in the secondary), each controlling its area's share of the zone; `Daylighting:Controls` with SplitFlux; sun and sky from the EPW and `Site:Location`.
- A zone without glazing gets no controls; a merged zone gets its daylit areas from its own geometry (the power-weighted fraction stays provenance only).
- The prototype fractions are a check, not an input (§5).
- Off by default; the LOD study keeps it off.
- Occupancy sensors and time switches: check whether PNNL models them as reductions in the lighting schedules or power densities (§6).

## 2. The code rule (D-233)

openstudio-standards is pinned in the atlas at `c8c1b9ebb30c5f1a441231bf3eae76b18fbbe907` (its `standards-controls` build cache). The base methods (`Standard#space_daylighted_areas`, `#space_add_daylighting_controls`) are identical to the copy under `data/raw/openstudio-standards`; the edition methods are in `standards/ashrae_90_1/ashrae_90_1_<edition>/ashrae_90_1_<edition>.Space.rb`. BEMGen follows them as below (`Lod.Core.Conversion.CodeDaylighting`).

| Step | openstudio-standards | BEMGen |
| --- | --- | --- |
| Primary sidelit area | per window: as wide as the window plus, each side, 2 ft (`fixed`, 90.1-2010) or half the head height (`proportional`, 90.1-2013, 2016, 2019); from the wall to one head height in | the same, in the plane of the window's wall on the floor of the storey the window stands on |
| Secondary sidelit area | the same width, from one to two head heights in | the same |
| Toplit area | per rectangular skylight: grown on every side by 0.7 × its height above the floor | the same; BEMGen's skylights are rectangles |
| Net areas | united per kind; primary less toplit; secondary less toplit and primary; each on the space's floor | on the zone's floor: the union of its parts on each storey (so a merged zone takes its own geometry), the storeys added; a window belongs to the storey of the part hosting its wall (its outline under the window, its height holding the sill), a skylight to that of the part whose top is the roof and whose footprint holds it, so a part spanning another part's floor elevation keeps its own (D-236) |
| Required (2013 to 2019) | primary: ≥ 150 W of lighting in it and ≥ 20 ft² of window; secondary: ≥ 300 W in both sidelit areas and ≥ 20 ft² of window; toplit: ≥ 150 W in it | the same, with the zone's lighting power per floor area |
| Required (2010) | primary: ≥ 250 ft²; toplit: ≥ 900 ft² and skylight effective aperture ≥ 0.006; no secondary | the same; the sidelighting aperture exception applies only to buildings without a prototype type in openstudio-standards, so not here |
| Exceptions | `Core_Retail`: no primary, secondary flag for a second toplit point; `Entry`, `Front_Retail`, `Point_of_Sale`, strip malls: no sidelighting; apartments: none | the same, by the space type in the program's `space_types` evidence |
| Sensors | the edition's `space_daylighting_fractions_and_windows`: which areas sensors 1 and 2 control and at which window or skylight; toplighting only in 90.1-2013+: one sensor in 6A, 6B, 7A, 8A, two of half the share elsewhere | the same, with the program's climate zone; 90.1-2013 to 2019 with toplit and primary control required and secondary not have no branch in openstudio-standards' table, so no sensor: BEMGen keeps that parity, and the header says the controls are required and openstudio-standards places no sensor (D-236) |
| Office whole building | sensor 1 × `psa_nongeometry_fraction`, sensor 2 × `ssa_nongeometry_fraction`, only for Office `WholeBuilding` space types | the same, from the program's `standards_rule` |
| Shares | rounded to three decimals; sensor 1 below 1 by 0.001, sensor 2 lowered so both stay below 1 | the same |
| Position | sensor 1 0.66 × head in from the window's centre, sensor 2 1.33 × head; under a skylight's centre; 2.5 ft above the floor | the same in plan, 0.8 m above the floor (the owner's height); a point that falls outside the zone's floor (a zone shallower than 1.33 head heights) moves to the interior point of its area, recorded in the header |
| Window order | facade (south, west, east, north), then name | facade by the wall's plan azimuth, then the building's surface order |

- **The edition** comes from the program's template (`source.template`): 90.1-2010 has its own rule; 90.1-2013, 2016, and 2019 share one (their openstudio-standards `Space` methods are identical). Other templates (IECC, DOE reference, 90.1-2004 and 2007, where openstudio-standards requires no controls) have **no code rule**: their controls are carried and never placed, with the warning `DaylightingNoCodeRule`. A `standards_rule` with `daylighting_appropriate: false` (openstudio-standards' `na`) has no code rule either.
- **The settings** are the program's: setpoint at both points, control type, minimum fractions, steps, method. Availability `all_days_except_design_days` is written blank (always), since the IDF runs no sizing periods, as D-172 did. The glare is computed at point 1, view along the zone's y axis, DGI 22; it controls nothing (no window shading control).
- **Merges.** A merged zone takes its lead source's rule with its settings (`WithFraction`, ADR-027 decision 4's rule); its areas come from its own geometry, and the power-weighted `ControlledLightingFraction` stays provenance. *Since D-236* the rule is not part of `SameSettings`: two sources with the same written settings and different rules (90.1-2019 Banquet and Cafe, say) give no `DaylightingSettingsDiffer` warning but the info `DaylightingRuleDiffers`, so the default-off path's warnings are those of before D-233.

## 3. Interfaces

- `IdfOptions.WriteDaylighting` (false by default). *Convert2IDF* appends the input *Daylighting* (index 12, `Dayl`, Boolean, default false); the component's GUID is unchanged, and a Boolean input needs no new parameter type, so no new GUID.
- The test-suite spec's `settings.daylighting` (Boolean, default false) gives the option to every site. The LOD study's specs do not set it.
- IDF header: without controls in any program nothing changes. With the option off, `Daylighting: not written (Convert2IDF's Daylighting option is off, the default; D-233); n zone(s) with controls in their programs` and the info `DaylightingNotWritten`. With it on, `Daylighting: written by the code rule on BEMGen's geometry (D-233); k of n zone(s) …` and one line per zone: its edition, areas, and points, or why none (no window or skylight; not required, with its lighting power and areas; no code rule). Provenance: `DAYLIGHTING: …`.
- *Program JSON*: the preset's source gains `DaylightingRule` (the rule, or why none), and its *Left Out* line says the controls are written only when *Convert2IDF*'s Daylighting input is on.
- EnergyPlus's warning `GetDaylightingControls: Fraction of zone or space controlled by the Daylighting reference points is < 1.0.` is expected (`ExpectedWarnings.PartialDaylightingControl`) only for an IDF that holds a `Daylighting:Controls` object (`ExpectedWarnings.ForIdf`, used by `eplus-check` and the batch runner); `ExpectedWarnings.Default` keeps it unexpected. The export tests' `IdfChecks` keep failing any daylighting object unless a test passes `daylighting: true`.
- With the option on, a zoning's lighting depends on its windows, so the evaluation metrics' pairing check (D-157) can report a site as unpaired on its internal loads; nothing else changes. This is why the LOD study keeps it off.

## 4. Tests (test first)

- `CodeDaylightingTests` (Core, 31): rooms with one and two glazed walls, too little lighting, a skylight (by climate zone), toplit areas taken out of the sidelit ones, all three areas, no glazing, another zone's windows, a merged zone across its parts, a zone over two storeys, the office non-geometry fractions and where they do not apply, the `Core_Retail` exception, 90.1-2010's width, threshold, and two-window split, the 20 ft² window exception, the cap below 1, a point moved into its area, the templates with and without a rule. They failed to compile before the types existed (observed); the other new tests below were written before their code but first run after it, except the suite test, observed failing on the schema.
- `DaylightingAndMainsAggregationTests.AMergeKeepsTheCodeRuleOfItsControls` (Core).
- `ReleaseTwoTests` (ProgramJson, 4 new): the medium office's rule (90.1-2019, space type, 0.68 / 0.32, climate zone), the retail core's space type without non-geometry fractions, the IECC office without a rule, a space type where daylighting is not appropriate. The preset snapshot `medium-office-preset` gains its `DaylightingRule` line (the only change).
- `IdfCodeDaylightingTests` (Export, 6): off by default with its header; on, every zone's objects equal the layout of `CodeDaylighting` with the program's settings and pass the daylighting checks; a windowless zone's header line; a program without a code rule warns; a building without controls is written byte for byte the same with the option on; an IDF with controls fails the default checks. `IdfProgramJsonTests` takes the new header text.
- `RunVerdictTests.TheDaylightingWarningIsExpectedOnlyForAnIdfWithDaylightingControls` (Simulation).
- `DoeSuiteTests.DaylightingIsWrittenOnlyWhenTheSpecAsksForIt` (TestSuiteGenerator): it failed first on the schema (`/settings/daylighting`).
- `CodeDaylightingEndToEndTests` (Simulation, opt-in `BEMGEN_ENERGYPLUS`): the medium office program on the office plate, off and on, Chicago O'Hare TMY3, EnergyPlus 26.2.0 `4bd7a1f26f`: both runs completed with 0 severe and 0 fatal errors; the run with controls gave 3 warnings, all `PartialDaylightingControl`; interior lights 66 750.5 kWh off and 53 133.0 kWh on (20.4 % less), interior equipment 125 213.7 kWh both.
- Every existing IDF snapshot is unchanged (no snapshot's programs carry controls).

## 5. The prototype check (D-235)

The DOE prototypes as BEMGen generates them (the suite generator's `doe` block, 90.1-2019, climate zone 5A, *No Simplification* and *Stack*, the option on), with the LOD study's pinned atlas inputs, except the medium office, whose keys all take the whole-building program (`WholeBuilding - Md Office`, as in the PNNL model). Against the PNNL 90.1-2019 prototype IDFs for Buffalo (5A), read with their `table.htm` zone summaries (zones in the floor area only):

| Prototype | Controlled floor fraction, BEMGen / PNNL | Controlled lighting fraction, BEMGen / PNNL | Zones with controls, BEMGen / PNNL |
| --- | --- | --- | --- |
| Medium office | 0.438 / 0.408 | 0.183 / 0.213 | 22 of 65 / 12 of 15 |
| Primary school | 0.748 / 0.748 | 0.408 / 0.460 | 18 of 25 / 18 of 25 |
| Stand-alone retail | 0.066 / 0.698 | 0.012 / 0.387 | 1 of 5 / 1 of 5 |
| Warehouse | 0.052 / 1.000 | 0.058 / 0.492 | 1 of 3 / 3 of 3 |

The four IDFs ran a year in EnergyPlus 26.2.0 on the Buffalo weather (`eplus-check`): all passed, 0 severe, the only expected warning `PartialDaylightingControl`.

Why they differ:

- **Medium office.** BEMGen's DOE medium office is the DOE reference layout of rooms (`medium-office` layout record, 65 zones) with the reference building's glazing, a window centred on each wall at 0.477 of its area (heads at about 3.1 m, against 2.33 m in the PNNL ribbon); the PNNL model has 15 perimeter and core zones with a 33 % ribbon window. The rooms with windows hold 0.438 of the floor, close to the PNNL perimeter's 0.408. The lighting share is lower, 0.183 against 0.213, because the code's power thresholds act on each zone: in BEMGen's small rooms the secondary area often carries less than 300 W (the conference rooms get one point only) and one classroom carries less than 150 W in its primary area, so they are not controlled, where the PNNL model's large perimeter zones always pass; the deeper primary areas of BEMGen's taller windows do not make up for it.
- **Primary school.** The same 18 zones are controlled; the lighting share is lower, 0.408 against 0.460, from BEMGen's windows (one centred per wall at the reference ratio, heads at about 3.2 m) against the PNNL windows. It was not analysed zone by zone.
- **Stand-alone retail and warehouse.** The DOE reference records BEMGen's generators follow have no skylights in these types (`skylightRatio` 0), and the 2.0.0 atlas programs of the study carry no fenestration, so BEMGen's geometry has no toplit area; the 90.1-2019 PNNL models have skylights over the retail core and the warehouse's bulk and fine storage, which carry their controls. On BEMGen's geometry only the glazed front (retail, by the `Core_Retail` rule of its mixed program) and the office (warehouse) are daylit. This is a difference of the geometry's glazing, not of the rule; a program or spec that gives these keys the prototype's skylight ratio would give them toplit areas.

The rule is therefore checked where the geometry matches (the school's zones, the office's perimeter share), and the remaining differences are BEMGen's glazing, which the method deliberately uses.

## 6. Occupancy sensors and time switches (D-234)

Checked in the PNNL 90.1 medium office IDFs (Denver, 2004 to 2019) and the 90.1-2016 and 2019 IDFs of every type (Denver):

- **In the lighting schedules.** The occupied-hour values of the office lighting schedule fall from 0.9 (90.1-2004) to 0.885 × 0.9 (2010) and 0.8368 × 0.9 = 0.75314 (2013 to 2019); the atlas's 90.1-2019 medium office carries openstudio-standards' `OfficeMedium BLDG_LIGHT_SCH_2013` (0.776 at weekday occupied hours), so the program already holds a schedule-based control credit.
- **In the power density.** The 90.1-2019 IDF's parameters list `LPD_Ctrl = 0.02` and its office LPD is 6.664 W/m²; the atlas program carries openstudio-standards' 6.889 W/m² (0.64 W/ft²). The difference is the atlas's to explain (its program values come from openstudio-standards, not from the PNNL IDF).
- **A gap: an occupancy-driven cap.** The 90.1-2016 and 2019 PNNL models add an EMS program per zone in the office, restaurant, retail, strip mall, and warehouse types (2010 and 2013 have none): when the zone's occupant count is 0 and its lighting exceeds 0.02 W/ft², the lighting is set to 0.02 W/ft² (90.1's unoccupied lighting limit). Neither the atlas programs nor BEMGen carry it. Since BEMGen's occupancy is a deterministic schedule, it could be expressed as a schedule rule, but it changes the program's lighting, which is the atlas's to record (GLOBAL.md scientific rule 3: BEMGen does not change program assumptions). **BEMGen adds nothing**; the gap is reported to the owner for the atlas.
- **Time switches** appear only as the schedules above; there is no separate object.

## 7. Open

- The owner's choice for IECC programs: openstudio-standards has no IECC daylighting rule, so IECC controls are never placed (warning `DaylightingNoCodeRule`). An IECC edition could take the 90.1-2019 rule by decision.
- The atlas: the occupancy-driven unoccupied lighting cap of the 90.1-2016 and 2019 prototypes (§6), and the LPD difference.
- Rhino checks for the person: the smoke checklist's *Convert2IDF* daylighting items (`docs/development/grasshopper-smoke-test.md`).
