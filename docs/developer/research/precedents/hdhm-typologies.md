# *High-Density Housing* typology families

> **Issued baseline.** Since D-093 the precedent set is the four-source family set `SYN-TYP-001` to `SYN-TYP-019`, paraphrased in [syn-typologies.md](syn-typologies.md). The nine families below are carried there as `SYN-TYP-001` to `SYN-TYP-009` with the same organisation and rule numbering; this page stays as the issued baseline of S8.1–S8.3 and is not updated further.

The precedent source of the plan generators (D-082) is the book *High-Density Housing* (DETAIL). It was studied in a separate research repository, `typology-synthesizer`, which catalogues the book's floor plans with cited claims and specifies nine typology families as topological generator rules. This page paraphrases those families in BEMGen's words, with their stable IDs, and names the BEMGen generator that realises each one (D-083). It contains no book text, no page images, and no copied drawings.

## Source contract

| Item | Value |
| --- | --- |
| Repository | `typology-synthesizer` (local path `D:\typology-synthesizer`, read-only for BEMGen) |
| Commit | `366ffbb` |
| `data/derived/generators.jsonl` | SHA-256 `29700dedd0db2898af4715df0f7e9f6dac0d4e0ab5470a3f62982d9fd3c1f061` |
| `data/derived/typologies.jsonl` | SHA-256 `5bb31c5c2bd9579df4b791e935e03edad7f6f11998cbc87fe5e2f3e573b2b22a` |
| `data/derived/s6_validation.jsonl` | SHA-256 `1ebd21d0528b4e028b84c480cd47e59e38e8812c08c4469af4498b48b04c1a02` |

- Family IDs are `HDHM-TYP-001` to `HDHM-TYP-009`; rule IDs are `<family>-R<nnn>`, in the order the source gives them. Claim, plan, and project IDs, which lead back to the book, stay in the source repository.
- **Support labels.** *Recurrent* (`recurrent_in_source`): the family occurs in several independently identified projects of the book. *Provisional*: one project only; usable as a design hypothesis without independent confirmation. Neither label says anything about housing in general.
- **Topological only.** The rules name building parts and how they connect (which part serves which, which parts adjoin, whether a court is open). The book supports no metric or count range for any family, so every dimension, count, and façade choice in a BEMGen generator is a design input with a default chosen in [ADR-006](../../decisions/ADR-006-plan-generation-mechanism.md) (D-083).
- **Generator inputs** of a family are categorical choices (an access system, a footprint form, a repetition), not ranges of variation.
- Every family has a *constraint* rule (keep all its essential relationships when other properties vary) and a *failure condition* (an organisation that lacks one of them is not a member). BEMGen realises both through parameter validation: a parameter value that would remove an essential relationship is the error `InvalidParameter`.
- BEMGen generators are not tested against the source's abstract validation records (D-083); ADR-006 states in text how each generator realises its family's rules, citing these IDs.

## Overview

| Family | Name | Support | BEMGen generator | Sub-stage |
| --- | --- | --- | --- | --- |
| `HDHM-TYP-001` | Repeated stair bays in a linear bar | recurrent (4 projects) | `StairBayBarGenerator` (*Stair Bay Bar*) | S8.1 |
| `HDHM-TYP-002` | Continuous external gallery beside a linear bar | recurrent (5 projects) | `GalleryBarGenerator` (*Gallery Bar*), gallery not modelled | S8.1 |
| `HDHM-TYP-003` | Projecting wings joined by a common band | recurrent (3 projects) | `WingedBandGenerator` (*Winged Band*) | S8.2 |
| `HDHM-TYP-004` | Open U-shaped court with stair-served wings | recurrent (2 projects) | `OpenCourtGenerator` (*Open Court*) | S8.2 |
| `HDHM-TYP-005` | Enclosed courtyard residential block | provisional | `EnclosedCourtGenerator` (*Enclosed Court*) | S8.3 |
| `HDHM-TYP-006` | Attached narrow terrace row | provisional | `TerraceRowGenerator` (*Terrace Row*) | S8.1 |
| `HDHM-TYP-007` | Compact point-access tower plate | provisional | `PointPlateGenerator` (*Point Plate*) | S8.2 |
| `HDHM-TYP-008` | One stair between a dwelling pair | provisional | `StairPairGenerator` (*Stair Pair*) | S8.1 |
| `HDHM-TYP-009` | Double-sided internal corridor bar | provisional | `LinearPlanGenerator` (*Linear Plan Generator*, since S2) | S8.1 (check) |

## Families

### `HDHM-TYP-001` Repeated stair bays in a linear bar

- **Support:** recurrent. **Inputs:** access system (stairs distributed along the bar), footprint form (a straight tract).
- **Relationships.** One straight residential tract holds repeated dwelling groups (`R001`). Each group along the tract has its own local stair (`R002`). Access stays distributed among the groups; no continuous shared route such as a gallery or corridor joins them (`R003`). `R004` keeps these relationships under variation; `R005` rejects an organisation missing one of them.
- **Not supported by the source:** the number of stair bays, their spacing, how the dwellings are subdivided, and every dimension. A single stair with one dwelling pair is the boundary case that belongs to `HDHM-TYP-008` instead.

### `HDHM-TYP-002` Continuous external gallery beside a linear bar

- **Support:** recurrent. **Inputs:** access system (one continuous external gallery), footprint form (a straight tract).
- **Relationships.** Dwelling modules are arranged in one straight tract (`R001`). A continuous gallery outside the tract serves the successive modules (`R002`); the shared route runs along the modules (`R003`). `R004` and `R005` as above.
- **Not supported by the source:** which side the gallery is on, how the stairs at the ends are arranged, the number of modules, their subdivision, and every dimension.

### `HDHM-TYP-003` Projecting wings joined by a common band

- **Support:** recurrent. **Inputs:** footprint form (a band with branching wings), wing repetition (the wing-to-band relation repeats; count open).
- **Relationships.** Residential wings project from a shared connecting band (`R001`), and the wing-to-band relation repeats without a fixed wing count or shape (`R002`). `R003` keeps these relationships; `R004` rejects an organisation missing one.
- **Not supported by the source:** the number and shape of the wings, the access system, unit subdivision, and dimensions.

### `HDHM-TYP-004` Open U-shaped court with stair-served wings

- **Support:** recurrent. **Inputs:** courtyard form (an open court), footprint form (residential sides in a U).
- **Relationships.** Residential sides enclose a shared space on three sides (`R001`); the fourth side stays open, so the space is an open court (`R002`); dwellings are reached by stairs (`R003`). `R004` and `R005` as above.
- **Not supported by the source:** how the stairs are distributed, the heights of the wings, unit layouts, and dimensions.

### `HDHM-TYP-005` Enclosed courtyard residential block

- **Support:** provisional. **Input:** footprint form (a residential perimeter around an interior court).
- **Relationships.** Residential edges surround an interior courtyard (`R001`), and the court is closed on all sides rather than open like a U (`R002`). `R003` keeps these relationships; `R004` rejects an organisation missing one.
- **Not supported by the source:** the single court observed is not a bound on the number of courts, and the access variants seen (stairs, galleries) do not establish one common access rule.

### `HDHM-TYP-006` Attached narrow terrace row

- **Support:** provisional. **Inputs:** footprint form (a straight row), plot repetition (attached plots repeat; count open).
- **Relationships.** Narrow attached house plots form one straight row (`R001`), repeated along the row (`R002`), with a shared dividing wall between neighbouring plots (`R003`). `R004` and `R005` as above.
- **Not supported by the source:** the number and width of the plots, the rooms inside a house, differences between storey heights, and dimensions.

### `HDHM-TYP-007` Compact point-access tower plate

- **Support:** provisional (one reviewed floor). **Inputs:** access system (point access; number of cores open), footprint form (a compact plate).
- **Relationships.** The dwellings form a compact plate rather than a long connected bar (`R001`), and their access is gathered at one point of vertical circulation (`R002`). `R003` keeps these relationships; `R004` rejects an organisation missing one.
- **Not supported by the source:** the number of cores and units, unit subdivision, which façades the units get, and plate dimensions.

### `HDHM-TYP-008` One stair between a dwelling pair

- **Support:** provisional. **Inputs:** access system (one shared stair), unit arrangement (a dwelling pair around that stair).
- **Relationships.** One compact linear plate holds a single dwelling pair (`R001`); the two dwellings lie on opposite sides of one shared stair (`R002`), which serves both (`R003`). `R004` and `R005` as above.
- **Not supported by the source:** room partitions, balconies, which façades the dwellings get, and plate dimensions.

### `HDHM-TYP-009` Double-sided internal corridor bar

- **Support:** provisional. **Inputs:** access system (an internal corridor), footprint form (a straight bar).
- **Relationships.** A long residential bar has occupiable sides on both flanks of an internal strip (`R001`); a shared linear route runs inside the bar through the floor (`R002`); dwellings (or rooms) lie on both sides of that route (`R003`). `R004` and `R005` as above.
- **Not supported by the source:** how the dwellings are subdivided, the corridor width, façade assignment, and bar dimensions.

## Related documents

- [ADR-006 Plan generation mechanism](../../decisions/ADR-006-plan-generation-mechanism.md): parameter records, defaults, zone IDs, and how each generator realises its family.
- [ADR-011 Minimum wall and window geometry](../../decisions/ADR-011-minimum-wall-and-window-geometry.md)
- [Decision log](../../decisions/decision-log.md): D-082 (source), D-083 (one generator per family), D-084 (sub-stages).
