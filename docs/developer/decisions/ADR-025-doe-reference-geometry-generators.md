# ADR-025: DOE reference geometry generators

Status: Accepted (by the controller under D-098; by the owner with PR #1, D-176); the owner's decisions O1 to O8 of 2026-10-25 are cited here, not made here; S8 is detailed in [ADR-026](ADR-026-multiplied-rooms.md)

Date: 2026-10-25

Decisions: D-009, D-026, D-061, D-093, D-097, D-098, D-111; the owner's O1 to O8 (design note §1); new: one decision-log entry that refines D-097 for the DOE generators (O4), added by the controller, and one entry per phase. Applies [ADR-002](ADR-002-geometry.md), [ADR-004](ADR-004-tolerances.md), [ADR-006](ADR-006-plan-generation-mechanism.md), [ADR-011](ADR-011-minimum-wall-and-window-geometry.md), [ADR-012](ADR-012-centred-windows.md), [ADR-014](ADR-014-program-types-and-department-zoning.md), and [ADR-015](ADR-015-plans-per-storey.md)

Design note: [2026-10-25-doe-geometry-generators.md](../plans/2026-10-25-doe-geometry-generators.md) (stage P0a) · Issue: Energy-Atlas/archetype-atlas#13

## Context

The plan generators of ADR-006 and ADR-014 realise the precedent families (D-093): residential families, and six non-residential families that place one zone per department (D-097). The goal of this work is different. BEMGen should build the geometry of every non-apartment DOE commercial building type with a parametric plan generator whose defaults reproduce the source plan and whose parameters vary its size and its repeated units. It builds geometry only; programs, schedules, and constructions come from the atlas.

The evidence is a read-only inspection on 2026-10-25 of the DOE commercial reference buildings (v1.4, EnergyPlus 7.2, all three vintages), the PNNL prototype buildings (ASHRAE 90.1-2004 to 2022, EnergyPlus 22.1), and the openstudio-standards detailed office geometry at `c8c1b9eb`, the commit the atlas pins. The figures in this ADR come from those files, through the design note.

**The owner's decisions (2026-10-25).** The design note §1 records eight decisions made by the owner. This ADR follows from them and does not restate them as its own:

| # | What it fixes |
| --- | --- |
| O1 | Geometry is one per type, not differentiated by vintage or by standard family. |
| O2 | The gaps G1 to G5 are recorded and not built. |
| O3 | Window-to-wall ratio per orientation and a skylight ratio are program data from the atlas, per zone type. Window shape is not reproduced. Glazed area per orientation is reproduced in total and per program key, and per zone where a key's zones share one ratio (wording corrected, D-164). |
| O4 | The DOE zone is the most detailed level of a DOE generator; D-097 is relaxed for these generators. |
| O5 | Zone multipliers inside a floor keep the DOE form: the repeated room is drawn once with its multiplier. |
| O6 | Offices take their room layout from the openstudio-standards detailed offices, a third source kept distinct from the reference and prototype buildings, on the reference plates and elevations. |
| O7 | Only programs defined in the standards; the atlas extracts the detailed-office space types (A1). |
| O8 | Where reference and prototype geometry differ, the reference wins; after O1 and O3 the only case left is the large office stacking. The data-centre zones stay in the large office geometry (O1). |

**The gaps (O2).** The five gaps between the sources and what BEMGen can draw are G1 plenums, G2 pitched attics, G3 basements, G4 zones taller than their storey, and G5 storeys of different height in one multi-storey generator.

**Numbering.** ADR-024 is taken on `feature/reduced-order-5r1c`, so the DOE decisions are ADR-025 (this ADR) and ADR-026 (multiplied rooms, phase P5a).

## Options considered

### How the layouts are built (S1, S2)

1. **One configurable generator for all DOE types.** One component, but a catch-all parameter record, which AGENTS.md forbids and ADR-006 rejects (its option 1).
2. **One generator per type with its layout written in C#.** The pattern of ADR-006, but a storey of 59 zones is not transcribed by hand (S2).
3. **One shared block, pinned layout data, and one generator per layout family (chosen).** It extends ADR-006's mechanism and its shared-block pattern (`StairBayLayout`, `HubArmsLayout`) to layouts that sit on a small grid.

### How a zone's program is chosen (S4)

1. **One preset input per space type, as in ADR-006.** The outpatient building alone has dozens of zone types, so one Grasshopper input each is unworkable.
2. **Reading the program from a zone's name.** Excluded by the rule that semantics are explicit data, never encoded in names (AGENTS.md, Architecture boundaries).
3. **An explicit program key on the zone and one program map (chosen).**

### How windows are sized (S5, S6)

1. **Keep one WWR per preset (D-026).** It cannot reproduce glazed area per orientation, which O3 requires.
2. **A WWR per orientation and a skylight ratio on the preset (chosen).**
3. **Apply the atlas WWR to the full 3.96 m office zone walls.** Without plenums an office zone is one floor-to-floor high, so this would overstate the glazing by 44 % (S6 gives the reference height instead).

### How multiplied rooms are modelled (S8)

1. **Draw every copy of a repeated room.** Excluded by O5, which keeps the DOE form.
2. **A zone multiplier on a planned zone, with isolated interior surfaces (chosen).** The source isolates multiplied rooms. A merge across different multipliers has no drawn geometry for the copies, so none is made.

### What happens to the precedent generators (S9)

1. **Replace the six non-residential `SYN-TYP` generators with DOE ones.** It gains nothing: they realise precedent families (D-093), not DOE types.
2. **Keep them and add the DOE generators as a separate set (chosen).**

## Decision

These are the planning decisions S1 to S10 of the design note §2, accepted by the controller under D-098; the owner may overrule any of them.

### S1. One shared block, one generator per DOE layout family

An internal `GridPlanLayout` in `Lod.Generators/Doe/` lays out a storey from x-cuts, y-cuts, and zones given as unions of grid cells. Eleven generators use it; each family has typed parameter and preset records and a `PlanGenerator` (or, for several storeys, a `MultiStoreyPlanGenerator`, [ADR-015](ADR-015-plans-per-storey.md)) as in ADR-006. Every DOE storey is axis-aligned and sits on a small grid: the largest is the outpatient ground floor at 32 × 30 cells, and the offices have at most 21 × 12.

| Generator | Records (default plans) | Source | Zones per storey | Gaps |
| --- | --- | --- | --- | --- |
| `RingOffice` | small, medium, large | openstudio-standards detailed offices on reference plates | 17; 23, 21, 21; 26 (×10 middle floor) | G1, G2 (small), G3 (large) |
| `Restaurant` | full-service, quick-service | reference | 2 | G2 |
| `StoreRow` | strip mall | reference | 10 | none |
| `RetailBox` | stand-alone retail | reference | 5 | none |
| `Supermarket` | supermarket | reference | 6 | none |
| `Warehouse` | warehouse | reference | 3 | G4 |
| `School` | primary, secondary | reference | 25; 25 and 21 | G4 (secondary) |
| `CorridorHotel` | small hotel | reference | 19, 16, 16, 16 | G5 |
| `TowerHotel` | large hotel | reference | 7, 7, 7 (×4 floor, rooms ×19) | G3, G5 |
| `Hospital` | hospital | reference | 9, 11, 13, 13, 8 | G3 |
| `Outpatient` | outpatient | reference | 59, 37, 22 | G4 |

The phases that build them (P1 to P6) and the stages around them are in the design note §4 and §6. The multiplied rooms that `TowerHotel` and `Hospital` need are phase P5a (S8).

### S2. Layouts are data, generated and pinned

A script `scripts/doe-geometry/extract.py` (standard library only, run with `python -I`, sources passed as arguments) reads the reference IDFs and the openstudio-standards OSMs as text. It writes one layout record per type (`src/Lod.Generators/Doe/Layouts/<type>.json`, an embedded resource) and one answer key per type (`tests/fixtures/doe/<type>.answer.json`), each with the SHA-256 of its source file. Only derived geometry is committed, never a source file. The openstudio-standards BSD-3 notice goes with the records derived from it. The records derived from the reference buildings, a US government work in the public domain with attribution requested, credit the DOE. The answer key makes exact reproduction testable without the source files on the test machine.

### S3. Size and unit variation

Each family names its parameters (the table in the design note §4 lists them). Fixed dimensions (perimeter depth, corridor width, room bay) keep their length. The remaining intervals are flexible: they absorb a change of plate length or depth in proportion to their slack (default length minus 1 m), shrinking and growing alike, so that every flexible interval reaches 1 m at the same plate size, the shortest valid plate; an interval under 1 m has no slack and keeps its length; below the shortest plate is `InvalidParameter`. A fixed band that a size parameter sets (a side's whole band, not each grid interval in it) is at least 0.5 m (`GridAxis.MinimumFixedBand`). This amends the first rule, "in proportion to their default length, each at least 1 m", which left the large office no room to shrink (D-164). Families with repeated units (stores, guest-room bays, classroom wings) expose a count, and the default count reproduces the source.

### S4. Program keys

A DOE zone carries its standards space type as an explicit field, `ProgramKey` (for example `MediumOffice - OpenOffice`), next to its BEMGen `SpaceType`. A fixed table maps the key to the space type (OpenOffice and ClosedOffice to `Office`, Corridor to `Corridor`, Stair to `Stair`, and so on; an unmapped key to `Other`). A DOE generator takes one program map keyed by `ProgramKey` instead of one input per space type, and a missing key is `MissingPreset`. *Semantic Merge* groups by space type and program key. The key is data from the source and is never parsed from a name (D-061); semantics are explicit data (AGENTS.md, Architecture boundaries).

### S5. Windows and skylights

`ProgramPreset` carries a WWR per orientation and a skylight ratio; a scalar WWR still means all four. A wall takes the WWR of the orientation it faces, with the sectors N [315, 45), E [45, 135), S [135, 225), and W [225, 315) of true azimuth, after `OrientationDegrees`. A roof takes one centred skylight in the largest grid rectangle of the zone's roof, of area ratio times roof area. Every simplifier and aggregator conserves skylight area per zone and orientation as it conserves window area ([ADR-012](ADR-012-centred-windows.md)). This follows O3.

### S6. Glazing reference height (G1)

Without plenums an office zone is one floor-to-floor high (3.96 m). Its windows are sized from the wall area below the source ceiling height (2.74 m), so the window area per orientation equals the reference. The height is recorded in provenance. The atlas WWR is relative to the conditioned zone's walls; applied to 3.96 m walls it would overstate the glazing by 44 %.

### S7. Gap conventions (G1 to G5)

| Gap | Convention |
| --- | --- |
| G1 plenums | Zone height is floor-to-floor, and the plenum volume lies inside the zone. |
| G2 pitched attics | A flat roof at the zone top. |
| G3 basements | Basements are omitted, and totals compare above grade. |
| G4 zones taller than their storey | Tall zones take the storey height: the gym 4 m, the outpatient stairs one zone per storey, the warehouse office 8.53 m with no fine-storage floor above it. |
| G5 storeys of different height in one multi-storey generator | One floor height per generator, the typical (upper) storey's. |

Each generator lists the gaps that apply to it in its documentation and provenance, and the acceptance tests exclude exactly those quantities. This follows O2.

### S8. Multiplied rooms (phase P5a)

A zone multiplier on a planned zone, with its interior surfaces self-referencing (a new boundary `SelfAdjacent`, written as an EnergyPlus `Surface` naming itself) or paired only with zones of the same multiplier, as in the source. *Semantic Merge* merges only zones of equal multiplier. *Perimeter Core*, *Single Zone per Floor*, and the single-zone aggregators return `NotSupported` for a plan with room multipliers until a later decision. This follows O5. It is summarised here only: its full rationale and mechanism are ADR-026, written in phase P5a, and nothing in P0a to P4 or P6 depends on it.

### S9. Precedent generators unchanged

The six non-residential `SYN-TYP` generators (`OfficePlate`, `Cafeteria`, `BranchingMall`, `OperatingSuite`, `CareHub`, `FoyerHalls`) stay. The DOE generators are a separate set in panel *2 Generate*. The residential generators are not touched.

### S10. Data-centre program in the DOE reference vintages

`OfficeLarge Data Center` is a row of the `doe_ref_pre_1980` and `doe_ref_1980_2004` `spc_typ.json`, so the atlas input A1 covers it. The data-centre zones stay in the large office geometry (O1, O7).

### Atlas inputs

The stage needs three inputs from the atlas: A1, programs for the standards space types of the detailed offices (the `SmallOffice - *` and `MediumOffice - *` rows and the plain large-office rows, including `OfficeLarge Data Center`, for the DOE reference templates); A2, WWR per orientation and skylight ratio per program in the program JSON BEMGen imports; and A3, a program key in each program record equal to the standards space type. P0 and P1 build and test with fixture programs before they land, and P1's test T4 is pending until A2 lands.

### Acceptance tests

Every phase checks every record of its families against its answer key, with the tolerances of [ADR-004](ADR-004-tolerances.md) unless stated (design note §5):

| # | Check | Tolerance |
| --- | --- | --- |
| T1 | Plate outline per storey, storey count, elevations, and floor heights equal the source, apart from the recorded gaps | ±0.01 m |
| T2 | Per storey: zone count, each zone's program key, floor area, the walls each pair of zones shares and their lengths, outdoor wall length per orientation per zone | areas ±0.1 m², lengths ±0.05 m |
| T3 | Conditioned floor area in total and per program key | ±0.1 % |
| T4 | Window area per orientation and skylight area equal the source, with the source's WWR and skylight ratio as program inputs | ±1 % |
| T5 | Variation: every parameter at 0.5×, 1×, and 2× of its default and every count at its minimum and twice its default gives a valid plan with the same zones and adjacencies; values below the limits are `InvalidParameter` | none |
| T6 | Every simplifier × aggregator combination validates, canonical and at the test suite's rotated placements; determinism and snapshots | as today |

Phase P1 adds exact figures from the sources: conditioned area 511.2, 4,982.2, and 46,320 m² above grade (the large office's 3,563 m² basement is G3); the zones per storey of the table above; reference elevations of 0, 3.96, and 7.92 m for the medium office and 0, 19.82 (×10), and 43.6 m for the large; T7, *Perimeter Core* at 5.0 m (small) and 4.57 m (medium, large) on the room plan, which gives the reference's five zones per storey with its areas (±0.1 m²); and the window area per orientation of each office, with S6's 2.74 m reference height for the medium and large offices. The tables of those figures are in the design note §5. Phase P5 adds that a building with room multipliers counts each zone times its multiplier in every total, that *Semantic Merge* never merges zones of different multipliers, and that the S8 `NotSupported` cases are tested.

### Left to the build

The design note fixes the rules above but not these details. The stage that builds each one settles it within S1 to S10 and records it in that stage's decision-log entry (Provisional, pending the owner's reading).

- P0a: the layout-record format, the loader, and the answer-key format (S2 fixes their location, content, and hash, not their schema); the rest of the space-type table of S4 beyond its examples; the shape of the program-map preset record; the format of the comparison harness's report.
- P0b: where in the pipeline skylights are placed and how they appear in the surfaces (S5 fixes the rule: one centred skylight in the largest grid rectangle of the zone's roof, of area ratio times roof area).
- Every stage: names, IDs, file layout, minor parameter limits, and test fixtures.

### Not in this stage

G1 to G5 themselves (only their conventions, S7); apartments; window shape (strips, punched counts, sill heights); interior shading and doors; the prototype buildings as a geometry source (O8); and choosing programs per vintage (the atlas).

## Consequences

- The DOE zone is the most detailed level of a DOE generator (O4). D-097 is relaxed for these generators only; the department zoning of [ADR-014](ADR-014-program-types-and-department-zoning.md) is unchanged for the other families.
- The DOE generators are a separate set. [ADR-006](ADR-006-plan-generation-mechanism.md)'s mechanism, the precedent generators, and the residential generators are unchanged (S9).
- Existing snapshots and icons stay byte-identical unless the design note documents the change for the stage that makes it; a scalar WWR keeps meaning all four orientations.
- Layout records and answer keys are committed derived data, each with its source SHA-256 and the required notices (the openstudio-standards BSD-3 notice, and credit to the DOE for geometry derived from the reference buildings). No source file is committed.
- The comparison against an answer key excludes exactly the quantities of the gaps that apply to a generator, so a gap is a documented difference and not a hidden one.
- A plan with room multipliers cannot yet go through *Perimeter Core*, *Single Zone per Floor*, or the single-zone aggregators (`NotSupported`, S8); ADR-026 settles the mechanism.
- A DOE zone's program comes from the program map, so the atlas inputs A1 to A3 must land before the programs are real; until then tests use fixture programs, and P1's T4 is pending. Since stage P7 (design note §9) every generator also has a ready map, `DoeProgramPresets`, with the illustrative example preset of each key's space type (the example Service preset as an any-program preset where the space type has none) and the source's own glazing per key, shipped in the layout records; its loads are not sourced programs and are replaced when A1 and A2 land ([doe-components.md](../architecture/doe-components.md#doe-program-presets)).
- S1 to S10 were provisional, as were the details each stage settled within them, until the owner accepted them with PR #1 (D-176). If the owner overrules one, a new decision-log entry supersedes it and this ADR is updated.
