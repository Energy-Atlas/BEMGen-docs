# Four-source typology families (`SYN-TYP-*`)

The precedent set of the plan generators (D-093) is the active four-source family set of the research repository `typology-synthesizer`: 19 families `SYN-TYP-001` to `SYN-TYP-019`, drawn from four books, *High-Density Housing* (DETAIL, `HDHM`), *Floor Plan Manual Housing* (fifth edition, `FPMH`), *Architects' Data* (second international English edition, `AD`), and *Metric Handbook: Planning and Design Data* (second edition, `MH`). The set covers housing and non-residential programs alike (D-094). This page paraphrases the families in BEMGen's words, with their stable family and rule IDs, gives their lineage from the nine *High-Density Housing* families of S8 ([hdhm-typologies.md](hdhm-typologies.md)), and names the BEMGen generator that realises each one and the sub-stage that builds it (D-098). It contains no book text, no page images, no copied drawings, and no claim, plan, or project IDs, which lead back to the books and stay in the source repository.

## Source contract

| Item | Value |
| --- | --- |
| Repository | `typology-synthesizer` (local path `D:\typology-synthesizer`, read-only for BEMGen) |
| Tag | `v0.3.1-research` |
| Commit | `7538ed3` |
| Records version | 3.0.0 (`data/four_source/`) |
| `data/four_source/typologies.jsonl` | SHA-256 `3f0aa78a9b53cc91fe6d47554706374a548f46afe70f15a056984675c8833f65` |
| `data/four_source/generators.jsonl` | SHA-256 `9321ef1f14cfe39e6e103946b490e535283e3a0df8c4200b217c5faac086a56d` |
| `data/four_source/s6_validation.jsonl` | SHA-256 `94f5948e979d88193966a1a715857b6afdf373aa3a40aaba47caff68231f9129` |
| Read alongside | `docs/typologies/four-source.md`, `docs/typologies/integrated.md`, `docs/generator-specs/four-source-handoff.md` |

- BEMGen reads the records only at that tag and commit; nothing in the source repository is modified (D-093).
- Family IDs are `SYN-TYP-001` to `SYN-TYP-019`; rule IDs are `SYN-TYP-0nn-R00k`, in the order the source gives them (written `R00k` below where the family is clear).
- **IDs in BEMGen documents.** From S8.4 on, BEMGen documents name the families by their `SYN-TYP-*` IDs and give the `HDHM-TYP-*` lineage for `001` to `009`. Component descriptions written in S8.1–S8.3 may keep their `HDHM-TYP-*` IDs as long as the `SYN-TYP-*` ID is also given. This is a provisional controller decision of S8.4 (decision log).

## Labels

- **Support within a source** (`recurrent_in_source`): the family's relationships recur among several independently identified, named projects of that one book. *Provisional*: one project of that book only; usable as a design hypothesis without independent confirmation. A label says nothing beyond the book it is given for.
- **Support in the corpus** (`recurrent_in_corpus`): the family is supported by independent projects across the four books taken together; *provisional* otherwise. It claims no representativeness beyond these four books.
- **Topological only.** The rules name building parts and how they connect (which part serves which, which parts adjoin, whether a court is open, which route reaches which room). No source supports a metric or count range for any family: the only observed counts (core count, courtyard count) have no candidate bounds. Every dimension, count, room size, service provision, and façade choice in a BEMGen generator is a design input with a default chosen in [ADR-006](../../decisions/ADR-006-plan-generation-mechanism.md) (D-083, D-098).
- Every family has a *constraint* rule (keep all its essential relationships when other properties vary) and a *failure condition* (an organisation without one of them is not a member). BEMGen realises both through parameter validation: a parameter value that would remove an essential relationship is the error `InvalidParameter` (ADR-006).
- BEMGen generators are not tested against the source's symbolic validation records (`s6_validation.jsonl`; D-083); ADR-006 states in text how each generator realises its family's rules, citing these IDs. Which rooms of a non-residential family form one zone is set in [ADR-014](../../decisions/ADR-014-program-types-and-department-zoning.md) (D-097).

## Overview

| Family | Organisation | Lineage | Support within a source | Corpus | BEMGen generator | Sub-stage |
| --- | --- | --- | --- | --- | --- | --- |
| `SYN-TYP-001` | Repeated stair bays in a linear bar | `HDHM-TYP-001`, carried | HDHM recurrent (4 projects) | recurrent | `StairBayBarGenerator` (*Stair Bay Bar*) | S8.1 |
| `SYN-TYP-002` | Continuous external gallery beside a linear bar | `HDHM-TYP-002`, revised (more examples) | HDHM recurrent (5), FPMH recurrent (3), AD provisional (1) | recurrent | `GalleryBarGenerator` (*Gallery Bar*), gallery not modelled | S8.1 |
| `SYN-TYP-003` | Projecting wings joined by a common band | `HDHM-TYP-003`, carried | HDHM recurrent (3), FPMH provisional (1) | recurrent | `WingedBandGenerator` (*Winged Band*) | S8.2 |
| `SYN-TYP-004` | Open U-shaped court with stair-served wings | `HDHM-TYP-004`, carried | HDHM recurrent (2), FPMH provisional (1) | recurrent | `OpenCourtGenerator` (*Open Court*) | S8.2 |
| `SYN-TYP-005` | Enclosed courtyard residential block | `HDHM-TYP-005`, carried | HDHM provisional (1), FPMH provisional (1) | recurrent | `EnclosedCourtGenerator` (*Enclosed Court*) | S8.3 |
| `SYN-TYP-006` | Attached narrow terrace row | `HDHM-TYP-006`, carried | HDHM provisional (1), FPMH recurrent (2) | recurrent | `TerraceRowGenerator` (*Terrace Row*) | S8.1 |
| `SYN-TYP-007` | Compact point-access tower plate | `HDHM-TYP-007`, revised (more examples) | HDHM provisional (1), FPMH recurrent (2), AD recurrent (3) | recurrent | `PointPlateGenerator` (*Point Plate*) | S8.2 |
| `SYN-TYP-008` | One stair between a dwelling pair | `HDHM-TYP-008`, carried | HDHM provisional (1) | provisional | `StairPairGenerator` (*Stair Pair*) | S8.1 |
| `SYN-TYP-009` | Double-sided internal corridor bar | `HDHM-TYP-009`, carried | HDHM provisional (1), FPMH provisional (1) | recurrent | `LinearPlanGenerator` (*Linear Plan Generator*, since S2) | S8.1 (check) |
| `SYN-TYP-010` | Radial lobes around a point tower core | new | FPMH provisional (1) | provisional | `RadialLobesGenerator` (*Radial Lobes*) | S8.5 |
| `SYN-TYP-011` | Linked housing clusters around multiple courts | new | FPMH recurrent (3) | recurrent | `CourtClusterGenerator` (*Court Cluster*) | S8.6 |
| `SYN-TYP-012` | Stepped dwelling bands with exposed terraces | new | FPMH recurrent (2) | recurrent | `SteppedBandGenerator` (*Stepped Band*, one plan per storey, D-095, [ADR-015](../../decisions/ADR-015-plans-per-storey.md)) | S8.7 |
| `SYN-TYP-013` | Incremental row with reserved expansion bays | new | FPMH provisional (1) | provisional | none: set aside (D-096) | — |
| `SYN-TYP-014` | Branching public mall between retail wings | new | MH recurrent (2) | recurrent | `BranchingMallGenerator` (*Branching Mall*) | S8.5 |
| `SYN-TYP-015` | Operating suite with separated clean and dirty routes | new | AD provisional (1) | provisional | `OperatingSuiteGenerator` (*Operating Suite*) | S8.6 |
| `SYN-TYP-016` | Cafeteria service edge beside a dining field | new | MH recurrent (2) | recurrent | `CafeteriaGenerator` (*Cafeteria*) | S8.4 |
| `SYN-TYP-017` | Central service core within an office plate | new | AD recurrent (2) | recurrent | `OfficePlateGenerator` (*Office Plate*) | S8.4 |
| `SYN-TYP-018` | Communal hub serving elder-care bedroom groups | new | MH recurrent (2) | recurrent | `CareHubGenerator` (*Care Hub*) | S8.5 |
| `SYN-TYP-019` | Public foyer branching to distinct activity spaces | new | AD recurrent (2), MH provisional (1) | recurrent | `FoyerHallsGenerator` (*Foyer Halls*) | S8.5 |

Counts are distinct named projects, not drawings. "Carried" means the family keeps the organisation of its `HDHM-TYP-*` baseline and gains evidence from the other books; "revised" means the same, with further named examples (`002`, `007`); the nine existing generators therefore stay valid for `001` to `009` (D-093). Generator names marked *specified* are fixed in ADR-006 and built in the sub-stage shown.

## Families carried from *High-Density Housing* (`001`–`009`)

Their relationships and rules are those of the baseline families, paraphrased in [hdhm-typologies.md](hdhm-typologies.md) under the `HDHM-TYP-*` IDs; the rule numbering is the same (`SYN-TYP-001-R001` corresponds to `HDHM-TYP-001-R001`, and so on). What the four-source set adds:

- **`SYN-TYP-001` Repeated stair bays in a linear bar.** One linear tract of repeated dwelling groups (`R001`), each with a local stair (`R002`), access distributed among the groups instead of one continuous shared route (`R003`); `R004` constraint, `R005` failure condition. The three cores seen in one project are an observation, not a bound. A linear repeated-bay case of the second book has an unconfirmed stair arrangement and is not counted.
- **`SYN-TYP-002` Continuous external gallery beside a linear bar.** Dwelling modules in one linear tract (`R001`), served by a continuous external gallery (`R002`) along which the shared route runs (`R003`); `R004`, `R005`. Evidence now from three books. Gallery side, end cores, and galleries on selected levels only vary among projects; the continuous access relation defines the family.
- **`SYN-TYP-003` Projecting wings joined by a common band.** Wings attached to a shared band (`R001`), the relation repeated with no fixed count or shape (`R002`); `R003`, `R004`. Wings may taper or shift.
- **`SYN-TYP-004` Open U-shaped court with stair-served wings.** Residential sides on three sides of a shared space (`R001`), the fourth side open (`R002`), stair access (`R003`); `R004`, `R005`. A two-dwelling U without repeated wings is a boundary case.
- **`SYN-TYP-005` Enclosed courtyard residential block.** Residential edges around one interior court (`R001`) that is enclosed rather than open-sided (`R002`); `R003`, `R004`. One project in each housing book; combined support in the corpus. Stair and gallery access appear as variants of one project.
- **`SYN-TYP-006` Attached narrow terrace row.** Narrow attached house plots in one linear row (`R001`), repeated (`R002`), with a shared dividing wall between neighbours (`R003`); `R004`, `R005`. Floors differ within a plot; slope and row alignment vary.
- **`SYN-TYP-007` Compact point-access tower plate.** A compact dwelling plate rather than a long bar (`R001`) with access gathered at a point (`R002`); `R003`, `R004`. Further named examples from *Architects' Data*; dwelling counts and arrangements vary; a branching radial plate (`010`) and a corridor plate test its boundary.
- **`SYN-TYP-008` One stair between a dwelling pair.** One compact linear plate for one pair (`R001`), the two dwellings on opposite sides of one shared stair (`R002`) that serves both (`R003`); `R004`, `R005`. One project; stacked apartments do not establish a lateral pair.
- **`SYN-TYP-009` Double-sided internal corridor bar.** A long bar with occupiable sides flanking an internal strip (`R001`), a shared linear route inside it (`R002`), dwellings or rooms on both sides (`R003`); `R004`, `R005`. Combined support from one project in each housing book.

## New housing families (`010`–`013`)

### `SYN-TYP-010` Radial lobes around a point tower core

- **Support:** provisional in FPMH and in the corpus (one project). **Inputs:** footprint form (branching), access system (point access), circulation topology (radial).
- **Relationships.** Dwelling lobes branch off a compact centre, their number and size left open (`R001`); every lobe is reached from that point-access centre (`R002`); movement spreads radially from the centre into the lobes (`R003`). `R004` keeps these relationships when other properties vary; `R005` rejects an organisation missing one.
- **Not supported by the source:** the number, size, and angle of the lobes, the dwellings per lobe, and every dimension. A compact plate without lobes is `007`.

### `SYN-TYP-011` Linked housing clusters around multiple courts

- **Support:** recurrent in FPMH (three projects) and in the corpus. **Inputs:** footprint form (a non-linear cluster), courtyard form (several shared courts), circulation topology (branching or distributed).
- **Relationships.** Dwelling modules aggregate into a non-linear, linked cluster (`R001`); several shared courts lie between dwelling groups within it (`R002`); a branching or distributed route connects the groups (`R003`). `R004`, `R005` as above.
- **Not supported by the source:** court shapes, the route hierarchy (which differ among the projects), the number of courts, and dimensions. One enclosed court is `005`.

### `SYN-TYP-012` Stepped dwelling bands with exposed terraces

- **Support:** recurrent in FPMH (two projects) and in the corpus. **Inputs:** footprint form (a band), another spatial feature (stepping terraces), access system.
- **Relationships.** Dwelling bands step back from storey to storey, so that the roofs of lower storeys become terraces, without a fixed setback (`R001`); the terraced dwellings are reached from a shared circulation edge (`R002`). `R003` constraint, `R004` failure condition.
- **Not supported by the source:** setback dimensions, the number of storeys, whether access is by stairs or an internal gallery (both occur), and dimensions. The plan differs by storey, so its generator returns one plan per storey (D-095, [ADR-015](../../decisions/ADR-015-plans-per-storey.md)); implemented in S8.7 with a rear corridor as the shared circulation edge, a west stair, and steps on the south side only.

### `SYN-TYP-013` Incremental row with reserved expansion bays

- **Support:** provisional in FPMH and in the corpus (one project). **Inputs:** footprint form (a row), repetition, another spatial feature (reserved bays).
- **Relationships.** Built row-house bays alternate with bays reserved for infill (`R001`), and a household may later grow into the neighbouring reserved bay (`R002`). `R003`, `R004`.
- **BEMGen:** set aside, no generator (D-096): modelling the reserved bays needs a choice the precedent does not settle (outdoor gaps, built bays, unconditioned shells, or the growth state as an input), and the family rests on one provisional project.

## Non-residential families (`014`–`019`)

### `SYN-TYP-014` Branching public mall between retail wings

- **Support:** recurrent in MH (two projects) and in the corpus. **Inputs:** footprint form, access system, circulation topology (branching).
- **Relationships.** Retail wings and large destinations (anchors) lie around a branching public mall (`R001`), which joins the wings as one connected branching route along which shops and anchors are disposed (`R002`). `R003` keeps these relationships; `R004` rejects a floor organisation missing one.
- **Not supported by the source:** the size of wings and anchors, the angles and widths of the mall, the number of branches, and every dimension.

### `SYN-TYP-015` Operating suite with separated clean and dirty routes

- **Support:** provisional in AD and in the corpus (one project). **Inputs:** footprint form, access system, circulation topology (separated routes).
- **Relationships.** Operating theatres form repeated banks beside the support rooms (`R001`), and the banks are reached by distinct clean and dirty routes (`R002`). `R003`, `R004` as above.
- **Not supported by the source:** the number and size of theatres and banks, the support-room programme, and every dimension. A surgical floor whose theatres share one corridor, without documented separate routes, is outside the family.

### `SYN-TYP-016` Cafeteria service edge beside a dining field

- **Support:** recurrent in MH (two projects) and in the corpus. **Inputs:** footprint form, access system, circulation topology.
- **Relationships.** Food preparation and servery spaces lie along an edge of a larger dining field (`R001`); customers move past that service edge into the dining space (`R002`). `R003`, `R004` as above.
- **Not supported by the source:** counter count, seating capacity, aisle widths, the kitchen's internal layout, and every dimension.

### `SYN-TYP-017` Central service core within an office plate

- **Support:** recurrent in AD (two projects) and in the corpus. **Inputs:** footprint form (a plate), access system (a central core), circulation topology.
- **Relationships.** Office work areas gather around a central service core (`R001`), which holds the lifts and shared services (`R002`); the plate holds several work areas around the one shared core. `R003`, `R004` as above.
- **Not supported by the source:** the core's shape and position within the centre, the furniture layout, and every dimension. An office floor whose core lies near an edge is outside the family.

### `SYN-TYP-018` Communal hub serving elder-care bedroom groups

- **Support:** recurrent in MH (two projects) and in the corpus. **Inputs:** footprint form, access system, circulation topology (branching).
- **Relationships.** Bedroom groups are arranged around a common communal and service centre (`R001`), and circulation branches from that centre to the groups (`R002`). `R003`, `R004` as above.
- **Not supported by the source:** the number of bedrooms, the wing lengths, care-room sizes, and every dimension.

### `SYN-TYP-019` Public foyer branching to distinct activity spaces

- **Support:** recurrent in AD (two projects), provisional in MH (one), recurrent in the corpus. **Inputs:** footprint form, access system, circulation topology (branching).
- **Relationships.** Distinct activity spaces lie around a common public foyer, which also leads to the support rooms (`R001`), and access branches from the foyer to those spaces (`R002`). `R003`, `R004` as above.
- **Not supported by the source:** the program mix (sport or community uses occur), hall dimensions, and the number of halls. A hall added beside an existing space through a service zone is outside the family.

## Plans outside every family

The source keeps six named plans in its catalogue without a family (an edge-core office, a hospital floor with a shared corridor, an emergency department organised by its entrances, two museums with galleries around courts or along a spine, and a church hall reached through a service zone), and it excludes a schematic whose floor extent is not established. BEMGen builds nothing for them.

## Related documents

- [*High-Density Housing* families](hdhm-typologies.md): the issued baseline of `001`–`009`.
- [ADR-006 Plan generation mechanism](../../decisions/ADR-006-plan-generation-mechanism.md): parameter records, defaults, zone IDs, and how each generator realises its family.
- [ADR-014 Program types and department zoning](../../decisions/ADR-014-program-types-and-department-zoning.md): the non-residential space types, their presets, and which rooms form one zone.
- [Decision log](../../decisions/decision-log.md): D-093 (source), D-094 (non-residential scope), D-095 (plans per storey), D-096 (`013` set aside), D-097 (department zoning), D-098 (sub-stages).
