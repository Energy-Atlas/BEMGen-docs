# ADR-006: Plan generation mechanism

Status: Accepted (by the controller under D-084; provisional pending the owner's reading); extended to the families of the four-source set in S8.4 (by the controller under D-098); hub-and-arms families implemented in S8.5; operating suite and court cluster implemented in S8.6; stepped band implemented in S8.7 with one plan per storey ([ADR-015](ADR-015-plans-per-storey.md))

Date: 2026-10-02

Decisions: D-009, D-026, D-061, D-065, D-082, D-083, D-084, D-085, D-093 to D-098, D-100; applies [ADR-014](ADR-014-program-types-and-department-zoning.md), [ADR-015](ADR-015-plans-per-storey.md), [ADR-002](ADR-002-geometry.md), [ADR-008](ADR-008-perimeter-core-corners.md), and [ADR-011](ADR-011-minimum-wall-and-window-geometry.md)

## Context

Since S2 one plan generator exists, `LinearPlanGenerator`, built on the base class `PlanGenerator<TParameters, TPresets>`: the subclass validates its parameters and lays out zones as polygons; the base checks the presets (D-061), builds the surfaces, places the windows (D-026), and records provenance. The precedent study (D-082) gives nine typology families, `HDHM-TYP-001` to `HDHM-TYP-009`, as topological rules without dimensions or counts ([precedent page](../research/precedents/hdhm-typologies.md)). D-083 asks for one generator per family, with the dimensions and counts chosen by the controller as design defaults and recorded here, and with each generator's documentation stating how it realises its family's rules. D-084 implements the bar families (009 checked, 001, 008, 002, 006) in S8.1, the non-rectangular families without holes (007, 003, 004) in S8.2, and the enclosed courtyard (005) in S8.3. This ADR fixes the mechanism and the parameter and preset records of all nine families, so that S8.2 and S8.3 only implement them. Since S8.4 the precedent set is the four-source family set `SYN-TYP-001` to `SYN-TYP-019` (D-093), which carries the nine families as `SYN-TYP-001` to `SYN-TYP-009` and adds families of every program type (D-094); the section [Families of the four-source set](#families-of-the-four-source-set-s84s87) specifies them in the same way. Family IDs below are the `HDHM-TYP-*` IDs of S8.1–S8.3, which are `SYN-TYP-*` with the same number.

## Options considered

1. **One configurable generator for all families** (a family enum plus a union of parameters). One component, but a catch-all parameter record, which AGENTS.md forbids, and every family's validation in one place.
2. **A rule interpreter over the source's topological graphs.** Close to the source records, but the records carry no geometry: every dimension, count, and placement would still need a family-specific layout, and the interpreter would be a second mechanism next to `PlanGenerator`.
3. **One `PlanGenerator` subclass per family (chosen).** Extends the existing pattern (AGENTS.md working rule 2): a typed parameter record and a typed preset record per family, a layout that returns zone polygons, and the shared base for presets, surfaces, windows, and provenance. Families with the same building block (stair bays) share layout code without sharing records.

## Decision

### Mechanism

- **One generator per family.** Each family has, in `Lod.Generators/<Family>/` (namespace `Lod.Generators.<Family>`), a parameter record `<Family>Parameters : PlanParameters`, a preset record `<Family>Presets : PlanPresets` with one preset per space type it places (D-061), and a generator `<Family>Generator : PlanGenerator<<Family>Parameters, <Family>Presets>`. The family `HDHM-TYP-009` keeps the S2 names (`Lod.Generators/Linear/`, `LinearPlanParameters`, `LinearPlanPresets`, `LinearPlanGenerator`).
- **The subclass** validates its own parameters (`Validate`, every error at once, code `InvalidParameter`), lays out the storey (`Layout`: the footprint and the zones as `PlannedZone(Id, Name, SpaceType, Footprint)` polygons that tile it), and lists its parameters for provenance (`Describe`). It does not build surfaces or windows.
- **The base** (`PlanGenerator`) checks `FloorHeight` (positive) and `OrientationDegrees` (finite), checks every preset slot (`MissingPreset`, `PresetSpaceTypeMismatch`), builds the surfaces with `LayoutSurfaceBuilder` (a gap or overlap between zones is an error, ADR-002), places one centred window per outdoor wall from the zone preset's WWR (D-026) unless the wall or window is below the minimum of [ADR-011](ADR-011-minimum-wall-and-window-geometry.md) (no window, info `WindowOmitted`), and records provenance: the family parameters, `FloorHeight`, `OrientationDegrees`, and `Presets` in slot order.
- **Plan frame.** Layouts are axis-aligned in the plan frame of ADR-002, metres, origin at the south-west corner of the footprint, a bar's long axis along +x (plan east) and its depth along +y (plan north). `OrientationDegrees` turns plan north from true north, as for the linear plan; *Transform Plan* (D-070) moves or rotates the result.
- **Defaults.** Every parameter record of S8 has a static `Default` holding the defaults below; the Grasshopper component of the family takes its input defaults from it, so the defaults live in one place. The defaults are design defaults chosen by the controller (D-083): plausible residential dimensions, not values from the source, which supports no metric or count range (D-082). Floor height is 3 m and orientation 0° for every family.
- **Validation.** Lengths must be positive and finite; counts are whole numbers with a family minimum where the family needs repetition. A value that would remove one of the family's essential relationships is rejected (`InvalidParameter`), which is how a generator realises its family's constraint and failure-condition rules (`R004`/`R005`, or `R003`/`R004`). No family has an upper bound.
- **Zones.** One zone per dwelling unit and storey; dwellings are never subdivided into rooms (D-009). Non-dwelling spaces are their own zones. The housing families of S8.1–S8.3 use only the space types `DwellingUnit`, `Stair`, and `Corridor`, so the residential default preset components serve them (the non-residential families zone per department with the space types of ADR-014, below); a point-access core is a `Stair` zone. Zone IDs are short, stable, and numbered from 1 west to east (along a wing's axis for wings), like the linear plan's `ST`, `CO`, `US1…`, `UN1…`; display names spell them out (`Unit 3`, `Stair 2`).
- **Windows.** The source fixes no façade or window rule, so every family uses the D-026 rule with the ADR-011 limits. Every outdoor wall above the limits gets one centred window; there is no façade without windows.
- **Not modelled by any family:** rooms (D-009), balconies, galleries (D-083), shading, and differences between storeys (every storey of a plan is the same; vertical variation comes from the floor aggregators), except in `SYN-TYP-012`, whose generator returns one plan per storey (D-095, [ADR-015](ADR-015-plans-per-storey.md), S8.7).

### Shared building block: the stair bay

A **stair bay** is dwelling | stair | dwelling side by side along a bar, each spanning the full bar depth: the stair serves the two dwellings beside it on every storey, and every dwelling has two opposite outdoor façades. `StairBayLayout` (in `Lod.Generators/StairBayBar/`, internal) lays out *n* bays from given widths, along plan x from the origin or, for a wing, from any start along plan x or plan y (`Wing`), and fits the bays to a wing's length (`Fit`, `FitErrors`); `HDHM-TYP-001`, `HDHM-TYP-008`, the wings of 003 and 004, and later 005 use it, so the bay geometry exists once. In a bay of width `2·UnitWidth + StairWidth`, the west dwelling is `[x₀, x₀ + U]`, the stair `[x₀ + U, x₀ + U + S]`, and the east dwelling `[x₀ + U + S, x₀ + 2U + S]`.

### Families implemented in S8.1

#### `HDHM-TYP-009` Double-sided internal corridor bar: `LinearPlanGenerator` (since S2)

| Parameter | Default | Reason |
| --- | --- | --- |
| `Length` | 24 m | S2 canonical plan; long enough for two units per row behind the stair |
| `UnitDepth` | 8 m | single-aspect units off a corridor are shallower than through units |
| `CorridorWidth` | 2 m | within the usual 1.8–2 m of an internal residential corridor |
| `TargetUnitWidth` | 10 m | the row length is divided evenly (`UnitsPerRow`, rounded half away from zero) |
| `StairLength` | 4 m | a full-depth stair hall at the west end |

- Presets `LinearPlanPresets(DwellingUnit, Corridor, Stair)`; zones `ST` (stair, full depth, west end), `CO` (corridor, from the stair to the east façade), `US1…USn` and `UN1…UNn` (south and north units, west to east).
- Realisation: `R001` the two unit rows flank the corridor strip along the whole bar; `R002` the corridor runs inside the bar from the stair to the east façade; `R003` every row has at least one unit (`UnitsPerRow` ≥ 1), so dwellings lie on both sides. Validation: every length positive; `Length` > `StairLength`.
- Check (D-083): the generator realises all of the family's rules; nothing is added. The component defaults above are unchanged.

#### `HDHM-TYP-001` Repeated stair bays in a linear bar: `StairBayBarGenerator`

| Parameter | Default | Reason |
| --- | --- | --- |
| `BayCount` | 3 | the smallest count with a middle bay between two end bays; minimum 2 |
| `UnitWidth` | 7 m | within 6–8 m for a through dwelling |
| `Depth` | 12 m | a through (double-aspect) dwelling; within 10–12 m |
| `StairWidth` | 3 m | a stair hall with two flights and landings, spanning the depth |

- Presets `StairBayBarPresets(DwellingUnit, Stair)`; the bar is `BayCount` stair bays, `BayCount · (2·UnitWidth + StairWidth)` × `Depth` (51 m × 12 m by default). Zones `ST1…STn` (stairs, west to east) then `U1…U2n` (dwellings, west to east): bay *i* is `U(2i−1)`, `STi`, `U(2i)`.
- Realisation: `R001` one rectangular tract of repeated dwelling groups; `R002` each stair adjoins exactly the two dwellings of its bay, on every storey; `R003` there is no corridor or gallery zone, stairs never adjoin each other, and neighbouring bays meet only dwelling to dwelling (a party wall). `R004`/`R005`: `BayCount` < 2 is `InvalidParameter`, since one bay is `HDHM-TYP-008`.
- Validation: `BayCount` ≥ 2; `UnitWidth`, `Depth`, `StairWidth` positive.

#### `HDHM-TYP-008` One stair between a dwelling pair: `StairPairGenerator`

| Parameter | Default | Reason |
| --- | --- | --- |
| `UnitWidth` | 7 m | as `HDHM-TYP-001` |
| `Depth` | 12 m | as `HDHM-TYP-001` |
| `StairWidth` | 3 m | as `HDHM-TYP-001` |

- Presets `StairPairPresets(DwellingUnit, Stair)`; one stair bay as its own building, 17 m × 12 m by default, laid out by `StairBayLayout` with one bay. Zones `ST1`, `U1` (west), `U2` (east).
- Realisation: `R001` one compact linear plate with one dwelling pair; `R002` the two dwellings lie on opposite sides of the stair; `R003` the stair adjoins both. Validation: every length positive.

#### `HDHM-TYP-002` Continuous external gallery beside a linear bar: `GalleryBarGenerator`

| Parameter | Default | Reason |
| --- | --- | --- |
| `UnitCount` | 6 | a run of modules long enough to need a gallery; minimum 2 |
| `UnitWidth` | 6 m | gallery-access modules are narrow; within 6–8 m |
| `Depth` | 10 m | a through dwelling from the gallery side to the opposite façade |
| `StairWidth` | 4 m | an end stair with the landing that reaches the gallery |

- Presets `GalleryBarPresets(DwellingUnit, Stair)`; a row of `UnitCount` dwellings through the bar depth with a full-depth stair at each end, `UnitCount · UnitWidth + 2 · StairWidth` × `Depth` (44 m × 10 m by default). Zones `ST1` (west end), `ST2` (east end), then `U1…Un` (west to east).
- **Not modelled (D-083):** the gallery itself. There is no gallery zone and no gallery geometry (no shading); the façade on the gallery side is an ordinary outdoor façade with windows by D-026. The source does not fix the gallery side, and the generator does not choose one.
- Realisation: `R001` one straight tract of modules; `R002`, `R003` are realised only in the access they imply: the two end stairs, from which a gallery would run past every module; the gallery is omitted. Validation: `UnitCount` ≥ 2 (successive modules, `R002`); every length positive.

#### `HDHM-TYP-006` Attached narrow terrace row: `TerraceRowGenerator`

| Parameter | Default | Reason |
| --- | --- | --- |
| `PlotCount` | 6 | a short row; minimum 2 (an attached row) |
| `PlotWidth` | 5.5 m | a narrow house plot, 5–6 m |
| `Depth` | 10 m | a through house |

- Presets `TerraceRowPresets(DwellingUnit)`; a row of `PlotCount` plots, `PlotCount · PlotWidth` × `Depth` (33 m × 10 m by default). Zones `U1…Un` (named `House 1…`, west to east). No stair or corridor zones: each house's stair is inside the dwelling and is not zoned (D-009).
- **Houses span storeys.** A plan is one storey, so each plot is one dwelling zone per storey; the floor aggregators stack the storeys. A house of three storeys is therefore three zones in the detailed model (a consequence of the plan → floor → building pipeline that D-009's "one zone per dwelling unit" does not cover; *Single Zone per Floor Type* or *Single Zone Building* merge storeys).
- Realisation: `R001` one straight row of narrow attached plots; `R002` the plot repeats along the row; `R003` neighbouring plots share a dividing wall (an interzone wall pair `Ui`/`Ui+1`). Validation: `PlotCount` ≥ 2; `PlotWidth`, `Depth` positive.

### Families implemented in S8.2 and S8.3

Records, defaults, and zoning are fixed here; the layouts are implemented, and may be refined, in their sub-stage, which records any change here. S8.2 implemented 007, 003, and 004 and S8.3 implemented 005 as specified, without changing a record or a default; the details each sub-stage settled are recorded below each family. Each wing below is a bar of stair bays: `n = max(1, round(L / (2U + S)))` bays, rounded half away from zero, with the unit width adjusted to `(L − n·S) / (2n)` so the bays fill the wing's length `L` exactly. Validation additionally requires that adjusted width to be positive: stairs that leave no room for dwellings are `InvalidParameter`, for example `StairWidth 10 m leaves no dwelling width in each 17 m wing: its 2 stair bays need 20 m of stairs; reduce StairWidth or UnitWidth.` Within a wing, zones are listed stairs first, then dwellings, numbered along the wing's axis, and each wing's last bay ends exactly at the wing's end.

#### `HDHM-TYP-007` Compact point-access tower plate: `PointPlateGenerator` (S8.2, implemented)

| Parameter | Default | Reason |
| --- | --- | --- |
| `DwellingDepth` | 8 m | single-aspect corner dwellings around a core |
| `CoreWidth` | 6 m | a square core with stair, lift, and landing |

- Presets `PointPlatePresets(DwellingUnit, Stair)`. A square plate of side `CoreWidth + 2·DwellingDepth` (22 m) with the core `ST` at its centre and four dwellings `U1…U4` around it in a pinwheel, counter-clockwise from the south-west: `[0, d + c] × [0, d]`, `[d + c, s] × [0, d + c]`, `[d, s] × [d + c, s]`, `[0, d] × [d, s]` for `d` = `DwellingDepth`, `c` = `CoreWidth`, `s` = plate side. Every dwelling adjoins the core along one full side and has two façades; the core has no outdoor wall.
- Realisation: `R001` a compact plate (aspect ratio 1) instead of a bar; `R002` every dwelling's access is the one central core. Validation: both lengths positive. The unit count is fixed at four by the pinwheel; the source supports no count.
- Implemented (S8.2): zones `ST` (*Core*), then `U1…U4` (*Unit 1…*); the default plate is 484 m², the core 36 m², each dwelling 112 m², with 8 windows. The core is the first zone of any family without an outdoor wall. *Semantic Merge* unites the four dwellings into one zone with a hole around the core, which needed the union of zones as tiles ([ADR-002](ADR-002-geometry.md)).

#### `HDHM-TYP-003` Projecting wings joined by a common band: `WingedBandGenerator` (S8.2, implemented)

| Parameter | Default | Reason |
| --- | --- | --- |
| `WingCount` | 3 | repetition of the wing-to-band relation; minimum 2 |
| `WingLength` | 17 m | one stair bay projecting from the band |
| `WingSpacing` | 17 m | clear distance between wings, at least the wing length, so the yards between wings are as wide as they are deep |
| `Depth` | 12 m | band and wing depth, a through dwelling |
| `UnitWidth` | 7 m | as `HDHM-TYP-001` |
| `StairWidth` | 3 m | as `HDHM-TYP-001` |

- Presets `WingedBandPresets(DwellingUnit, Stair)`. The band is a stair-bay bar along x, `y ∈ [0, Depth]`, of length `WingCount · Depth + (WingCount − 1) · WingSpacing` (70 m); wing *i* (from 1) is a stair-bay bar along y, `x ∈ [(i − 1)(Depth + WingSpacing), (i − 1)(Depth + WingSpacing) + Depth]`, `y ∈ [Depth, Depth + WingLength]`. Zones `B-ST1…`, `B-U1…` (band, west to east) and `W{i}-ST1…`, `W{i}-U1…` (wing *i*, south to north).
- Realisation: `R001` every wing adjoins the band along its whole root; `R002` `WingCount` ≥ 2 repeats the relation. The comb outline gives the band's north façade short fragments between the wings' roots and its bay boundaries; ADR-011 governs their windows.
- Implemented (S8.2): the first wing is flush with the band's west end and the last with its east end. Zones `B-ST1…B-ST4`, `B-U1…B-U8` (*Band Stair 1*, *Band Unit 1*, …; four bays of 7.25 m dwellings in the 70 m band), then per wing `W{i}-ST1`, `W{i}-U1`, `W{i}-U2` (*Wing 2 Stair 1*, …; one bay of 7 m dwellings); 1452 m², 43 windows. The band's north fragments are 5.5, 7.25, 3, 1.25, 1.25, 3, 7.25, and 5.5 m by default, so every one keeps its window; with `WingSpacing` 14 m two fragments are 0.5 m and get no window (`WindowOmitted`). `WingCount` < 2 is `WingCount must be at least 2 (the wing-to-band relation repeats), got 1.`

#### `HDHM-TYP-004` Open U-shaped court with stair-served wings: `OpenCourtGenerator` (S8.2, implemented)

| Parameter | Default | Reason |
| --- | --- | --- |
| `CourtWidth` | 24 m | twice the wing depth, so the court is daylit |
| `CourtDepth` | 17 m | one stair bay along each side wing |
| `Depth` | 12 m | wing depth, a through dwelling |
| `UnitWidth` | 7 m | as `HDHM-TYP-001` |
| `StairWidth` | 3 m | as `HDHM-TYP-001` |

- Presets `OpenCourtPresets(DwellingUnit, Stair)`. Three stair-bay wings: west `[0, D] × [0, CourtDepth]`, east `[D + CourtWidth, 2D + CourtWidth] × [0, CourtDepth]`, north `[0, 2D + CourtWidth] × [CourtDepth, CourtDepth + D]` (the north wing holds the corners). The court is open to plan south. Zones `N-…`, `W-…`, `E-…` with `ST`/`U` numbering per wing.
- Realisation: `R001` dwellings on three sides of the court; `R002` the fourth (south) side stays open; `R003` every dwelling adjoins a stair. Validation: lengths positive; `CourtWidth` and `CourtDepth` positive (an open court exists).
- Implemented (S8.2): zones `N-ST1…N-ST3`, `N-U1…N-U6` (*North Stair 1*, *North Unit 1*, …; three bays of 6.5 m dwellings in the 48 m north wing), then `W-ST1`, `W-U1`, `W-U2` and `E-ST1`, `E-U1`, `E-U2` (*West Unit 1*, …; one bay of 7 m dwellings, south to north); 984 m², 30 windows. The court's façades are the north wing's south façade between the side wings and the side wings' inner façades.

#### `HDHM-TYP-005` Enclosed courtyard residential block: `EnclosedCourtGenerator` (S8.3, implemented)

| Parameter | Default | Reason |
| --- | --- | --- |
| `CourtWidth` | 24 m | twice the wing depth |
| `CourtDepth` | 24 m | a square court |
| `Depth` | 12 m | wing depth, a through dwelling |
| `UnitWidth` | 7 m | as `HDHM-TYP-001` |
| `StairWidth` | 3 m | as `HDHM-TYP-001` |

- Presets `EnclosedCourtPresets(DwellingUnit, Stair)`. Four stair-bay wings around one court: south and north full width, `[0, 2D + CourtWidth] × [0, D]` and `× [D + CourtDepth, 2D + CourtDepth]`; west and east between them, `[0, D]` and `[D + CourtWidth, 2D + CourtWidth]` × `[D, D + CourtDepth]`. The footprint is the outer rectangle with the court as a hole; court façades are outdoor. Zones `S-…`, `N-…`, `W-…`, `E-…`.
- Realisation: `R001` dwellings on every edge of the court; `R002` the court is closed on all four sides (the footprint has exactly one hole). Validation: lengths positive. Requires footprints with holes in every plan simplifier and floor aggregator (S8.3, D-084).
- Implemented (S8.3): zones `S-ST1…S-ST3`, `S-U1…S-U6` (*South Stair 1*, *South Unit 1*, …; three bays of 6.5 m dwellings in the 48 m south wing), the same for `N-…`, then `W-ST1`, `W-U1`, `W-U2` and `E-ST1`, `E-U1`, `E-U2` (one bay of 10.5 m dwellings in each 24 m side wing, south to north); 1728 m² (48 m × 48 m less the 24 m × 24 m court), 44 windows, 16 of them on the court façades (79.2 m² of the 237.6 m² of glazing). The footprint's hole is the court ring `(D, D)`, `(D, D + c)`, `(D + w, D + c)`, `(D + w, D)`, stored clockwise. Validation also fits the stair bays to each wing as for the open court (`StairWidth 30 m leaves no dwelling width in each 48 m south and north wing: …`). The generator does not impose the *Perimeter Core* precondition of D-087, which belongs to that simplifier: the default 12 m wings are wider than twice the 4.57 m default perimeter depth, and 9 m wings fail *Perimeter Core* with `PlanTooNarrow`. *Semantic Merge* gives four L-shaped dwelling zones, one around each corner of the court (the side wings' stairs and the middle stairs of the long wings separate them), and the eight stairs; no merged zone has a hole.

### Pipeline consequences of S8.2

Running every plan simplifier and floor aggregator on the non-rectangular families, canonical and rotated, found three faults on rotated plans; the second (`UnmatchedEdge` in *Semantic Merge*) also affected the linear plan and the gallery bar at some placements in released versions up to `v0.8.0` (D-088); each is fixed and documented where it belongs, and no tolerance or check is relaxed:

- *Semantic Merge* united its groups with a plain union, which splits a group whose zones meet at T-junctions once rotated (`DisconnectedGroup`); it now unites them as tiles ([ADR-002](ADR-002-geometry.md)).
- The surface builder tested whether a vertex lies on an edge between snapped grid cells, which can put a T-junction exactly on an edge up to √2 grid units off it (`UnmatchedEdge`); it now measures the original positions against the distance tolerance (ADR-002).
- A union of tiles returned vertices rounded to the clipping grid, so a storey outline united from a *Semantic Merge* floor could lie off the merged walls' façade lines (`FacadeNotCovered` in the single-zone aggregators); it now keeps the tiles' own vertices (ADR-002, [ADR-013](ADR-013-vertical-aggregation-methods.md)).

The bisector rule of *Perimeter Core* needed no change: it handles the re-entrant corners of the comb and the U. Its precondition, that every wing or other part of the footprint be wider than twice the perimeter depth, is stated in its `PlanTooNarrow` message and in [ADR-008](ADR-008-perimeter-core-corners.md); with the defaults (12 m deep wings and plates of 22 m, 4.57 m depth) every family passes.

### Pipeline consequences of S8.3

The enclosed court is the first footprint with a hole. Tests on a simple ring footprint (four wings around a square court) and on the generator, canonical and at the two rotated placements, show what every step needed:

- The surface builder already treated the hole's edges as plan boundary, so the court's edges are outdoor walls facing into the court. It now also requires every edge of the plan boundary, outer ring and holes, to be covered by outdoor zone edges over its full length (`UnmatchedEdge`): a zone filling the court shares every edge with a wing and was not detected by edge matching alone ([ADR-002](ADR-002-geometry.md)).
- *Perimeter Core* rejected holes (`NotSupported`). It now offsets every ring by the bisector rule, gives the court façades their own zones `P-Court-<Bin>`, and leaves a core that is a ring around the court; its precondition (D-087) applies to every wing between the outer and a court façade ([ADR-008](ADR-008-perimeter-core-corners.md)).
- *No Simplification*, *Semantic Merge*, *Single Zone per Floor*, the four floor aggregators, validation, and the window rule needed no change: united zones and storey outlines keep the hole, the court has neither a ground slab nor a roof because it is outside every footprint, rebuilt court walls get one centred window each (D-079), and glazing per orientation counts the court façades by the direction they face ([ADR-013](ADR-013-vertical-aggregation-methods.md)). Every existing snapshot is byte-identical.

### Families of the four-source set (S8.4–S8.7)

The four-source precedent set (D-093, [syn-typologies.md](../research/precedents/syn-typologies.md)) carries `SYN-TYP-001` to `SYN-TYP-009` as the nine families above (lineage `HDHM-TYP-001` to `HDHM-TYP-009`, same organisation and rule numbering), so their generators, records, and defaults are unchanged. It adds nine families that get generators (D-094, D-096): the housing families `010`, `011`, and `012` and the non-residential families `014` to `019`; `SYN-TYP-013` is set aside (D-096). This section specifies all nine now, as S8.1 specified the families of S8.2 and S8.3, so that S8.5–S8.7 only implement them; a sub-stage that refines a layout records the change here. D-098 assigns them: `017` and `016` in S8.4, `010`, `014`, `018`, and `019` in S8.5 on a shared hub-and-arms layout, `015` and `011` in S8.6, and `012` in S8.7 with plans per storey (D-095).

The mechanism above applies unchanged, with three additions:

- **Zones.** Housing families keep one zone per dwelling and storey (D-009, D-085); non-residential families place one zone per department (D-097), with the space types and the rooms each zone stands for set in [ADR-014](ADR-014-program-types-and-department-zoning.md). A department zone may surround another zone (a ring); it is never split into rooms or tenancies.
- **Defaults.** The source supports no metric or count range for any family (D-093), so every default below is a controller design default (D-098): a plausible dimension for the building type, not a value from the source, with its reason. Floor heights are chosen per family (3 m for housing, more where the program needs deeper services or tall rooms); orientation is 0° for every family.
- **Upper bounds.** The layouts are axis-aligned in the plan frame. Where a family's branches are arms on the four sides of a hub, at most four fit; a larger count needs non-orthogonal arms and is not supported (`InvalidParameter`). This is a limit of the layout, not of the family.

#### `SYN-TYP-017` Central service core within an office plate: `OfficePlateGenerator` (S8.4)

| Parameter | Default | Reason |
| --- | --- | --- |
| `PlateLength` | 42 m | a rectangular office plate: 12 m of office depth on both sides of an 18 m core |
| `PlateDepth` | 30 m | 12 m of office depth on both sides of a 6 m core, so every work area is daylit from one façade |
| `CoreLength` | 18 m | lifts, stairs, toilets, and risers in one core along the plate's long axis |
| `CoreDepth` | 6 m | two rows of service rooms either side of a lift lobby |
| `FloorHeight` | 3.8 m | a raised floor and a suspended ceiling with services |

- Presets `OfficePlatePresets(Office, Core)`. The plate is the rectangle `[0, PlateLength] × [0, PlateDepth]` (1260 m² by default); the core is centred on it, `[(L − l)/2, (L + l)/2] × [(D − d)/2, (D + d)/2]` for a plate `L × D` and a core `l × d` (108 m²). Zones `SC` (*Service Core*, `Core`), then `OF` (*Office*, `Office`): the office work area is one zone, the plate minus the core, a polygon with the core as its hole (1152 m²); the footprint has no hole.
- Realisation: `R001` office work areas gather around the central core: the work-area zone surrounds the core on all four sides; the several work areas of the precedents form one contiguous department and are one zone (D-097). `R002` lifts and shared services lie in the central core, a `Core` zone without an outdoor wall. `R003`/`R004`: the core must be central, with work area on every side.
- Validation: every length positive; the core leaves an office depth of at least `OfficePlateGenerator.MinimumOfficeDepth` = 3 m on every side, `(PlateLength − CoreLength)/2` at the west and east façades and `(PlateDepth − CoreDepth)/2` at the south and north façades: a core closer to a façade is the edge-core plan that the source records outside the family, and 3 m is the shallowest band that holds a row of desks with its aisle. For example `CoreLength 40 m leaves an office depth of 1 m at the west and east façades; SYN-TYP-017 needs at least 3 m of work area on every side of the core.`
- Not modelled: individual work areas, meeting rooms, and the rooms of the core (D-097); a core off the centre; non-rectangular plates. *Perimeter Core* still needs every part of the plate wider than twice its depth (D-087); the default plate passes with 4.57 m.
- Implemented (S8.4): as specified. Zones `SC` (*Service Core*), `OF` (*Office*); by default 108 m² and 1152 m², 4 windows of WWR 0.4 (218.88 m² of glazing), none on the core, whose four walls are all interzone walls with the office. The office's hole is the core's ring, so the office has eight walls: four outdoor and four facing the core. *Semantic Merge* keeps the two zones (the ring keeps its hole); *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, and a `CORE` of 32.86 m × 20.86 m (685.4596 m²) that contains the whole service core and the inner part of the ring; the single-zone methods drop the ring.

#### `SYN-TYP-016` Cafeteria service edge beside a dining field: `CafeteriaGenerator` (S8.4)

| Parameter | Default | Reason |
| --- | --- | --- |
| `Length` | 30 m | the length of the service edge and of the dining field it borders |
| `DiningDepth` | 15 m | a dining field of 450 m², about 300 seats at 1.5 m² each |
| `KitchenDepth` | 8 m | preparation, cooking, wash-up, and a servery counter along the kitchen's front |
| `FloorHeight` | 4 m | a tall dining hall and kitchen extract ducts |

- Presets `CafeteriaPresets(Kitchen, Dining)`. The plan is the rectangle `[0, Length] × [0, DiningDepth + KitchenDepth]` (690 m² by default): the dining field `[0, Length] × [0, DiningDepth]` on the plan's south side, which gets the daylight, and the service edge `[0, Length] × [DiningDepth, DiningDepth + KitchenDepth]` on its north side. Zones `KS` (*Kitchen and Servery*, `Kitchen`), then `DI` (*Dining*, `Dining`).
- Realisation: `R001` food preparation and servery lie along an edge of the dining field: the kitchen zone shares the dining field's whole north edge. `R002` customers move past the service edge into the dining space: the servery counter is the kitchen's front on that shared edge, so the route along it lies in the dining field and is not a zone of its own. `R003`/`R004`: the dining field must be the larger part (the precedents' dining field is larger than the service edge it adjoins).
- Validation: every length positive; `KitchenDepth` < `DiningDepth`, for example `KitchenDepth 15 m must be smaller than DiningDepth 15 m: in SYN-TYP-016 the dining field is the larger part of the plan.`
- Not modelled: the counter, the queue, the kitchen's rooms (stores, wash-up), seating, and entrances (D-097); a service edge on more than one side.
- Implemented (S8.4): as specified. Zones `KS` (*Kitchen and Servery*, 240 m²) and `DI` (*Dining*, 450 m²), sharing one 30 m interzone wall; 6 windows (114.4 m² of glazing), three per zone. *Perimeter Core* puts the kitchen alone in `P-North`, the dining field alone in `P-South`, and both in `P-East`, `P-West`, and `CORE`.

#### Pipeline consequences of S8.4

The office plate's work area is the first generated zone with a hole in a footprint without one. The surface builder pairs the hole's edges with the core's edges as interzone walls, and every plan simplifier and floor aggregator handles the ring as it handles the united rings of *Semantic Merge* (S8.2): every combination validates for both families, canonical and at the two rotated placements of the test suite (and, in a sweep run while building the reference, at 50 rotations from 0° to 357.7° for the default plans and for an office plate with the 3 m minimum depth). No step of `Lod.Core` changed, and no tolerance or check was relaxed.

#### Shared building block: the hub and its arms (S8.5)

`HubArmsLayout` (in `Lod.Generators/HubArms/`, internal) lays out a square hub of side `H` and up to four rectangular arms on its sides, in the order east, north, west, south (counter-clockwise from plan east), each arm centred on its side, of length `Lᵢ` away from the hub and width `A` along the side. An arm must not be wider than the hub (`A ≤ H`; a wider arm would overlap its neighbour beyond the hub's corner), which every family validates. The footprint is the union of hub and arms (a T for three arms, a cross for four), placed with the south-west corner of its bounding box at the origin. A hub side without an arm, and the hub's corners when `A < H`, are outdoor walls. The families subdivide the hub and the arms into their zones; zones are listed hub first, then arm by arm in the order above, except that `019` lists its halls before its support wing (its section below).

- Implemented (S8.5): `HubArmsLayout(hubWidth, armWidth, armLengths)` takes one length per arm, so the support wing of `019` can be shorter than its halls. A family with *n* arms uses the first *n* sides in the order east, north, west, south: two arms (`018`) leave the hub east and north (an L), three leave its south side free (a T), four make a cross. Each `HubArm` has its own frame: *along* runs from the root on the hub's side to the tip, *across* from the arm's clockwise side (the right-hand side looking out from the hub: south for the east arm, east for the north arm, north for the west arm, west for the south arm) to its counter-clockwise side. `Piece(along₀, along₁, across₀, across₁)` is a rectangle of that frame, and pieces with the same along or across values share their edges exactly, so the families subdivide the arms without geometry of their own. `HubWithStrips(across₀, across₁, length)` unites the hub with one strip of every arm into one polygon (the mall of `014`). The footprint and that polygon are walked counter-clockwise around the hub, start at their lowest, then leftmost, vertex, and have no repeated or collinear vertices, so an arm as wide as the hub continues the hub's sides without a vertex at the hub's corner. `CountErrors` and `WidthErrors` give every family the same messages, for example `LobeCount must be at most 4 (lobes leave the core only on its four sides, D-100), got 5.` and `LobeWidth 13 m is wider than CoreWidth 12 m; an arm must not be wider than the hub it leaves, or it would overlap its neighbour beyond the hub's corner.`; a fifth arm is an `ArgumentOutOfRangeException` of the layout, which the families' validation never lets through. The layout's own tests reach it through `InternalsVisibleTo` from `Lod.Generators` to `Lod.Generators.Tests`.

#### `SYN-TYP-010` Radial lobes around a point tower core: `RadialLobesGenerator` (S8.5)

| Parameter | Default | Reason |
| --- | --- | --- |
| `LobeCount` | 4 | a cruciform tower; minimum 3 (two lobes would be a bar through a core), maximum 4 (orthogonal arms) |
| `LobeLength` | 10 m | a dwelling depth from the core to the lobe's end |
| `LobeWidth` | 12 m | two 6 m dwellings side by side in each lobe |
| `CoreWidth` | 12 m | stairs, lifts, and the landing that every dwelling opens onto; at least the lobe width |
| `FloorHeight` | 3 m | housing |

- Presets `RadialLobesPresets(DwellingUnit, Stair)`. The hub is the core, the arms are the lobes (`A` = `LobeWidth`, `H` = `CoreWidth`). Each lobe holds two dwellings side by side along its axis, each spanning the lobe's length and half its width, so each adjoins the core over half the lobe's root. Zones `ST` (*Core*), then `L{i}-U1`, `L{i}-U2` (*Lobe i Unit 1*, …; lobe `i` from 1 in the arm order, `U1` the half clockwise of the lobe's axis). Default plan 624 m²: a 144 m² core and eight 60 m² dwellings.
- Realisation: `R001` dwelling lobes branch around the compact core; `R002` every dwelling adjoins the core (point access); `R003` movement spreads from the core into the lobes, and there is no other circulation zone. Validation: `LobeCount` 3–4; lengths positive; `LobeWidth` ≤ `CoreWidth`. With three lobes the core's free side is an outdoor wall with the stair preset's windows.
- Not modelled: lobes at other than right angles, lobes of different sizes, more than two dwellings per lobe.
- Implemented (S8.5): as specified. Zones `ST` (*Core*), then `L1-U1`, `L1-U2`, …, `L4-U2` (*Lobe 1 Unit 1*, …); by default 624 m², a 144 m² core and eight 60 m² dwellings, with 16 windows of WWR 0.3 (115.2 m² of glazing, 28.8 m² per orientation), two per dwelling (its side and its end) and none on the core, which adjoins every dwelling over 6 m. Three lobes give a T of 504 m² with 13 windows; the core's 12 m south wall gets one window of the stair preset's WWR 0.1. Lobes narrower than the core leave the core's corners as outdoor walls, which get no window below 1 m (11 m lobes on the 12 m core: eight 0.5 m walls, `WindowOmitted`). *Semantic Merge* unites the two dwellings of each lobe (lobes meet only at the core's corners) and keeps the core; *Perimeter Core* gives three zones per orientation, `P-North-1` to `P-West-3`, and a cross-shaped `CORE` of 122.5796 m²; 9 m lobes fail it with `PlanTooNarrow` (D-087).

#### `SYN-TYP-014` Branching public mall between retail wings: `BranchingMallGenerator` (S8.5)

| Parameter | Default | Reason |
| --- | --- | --- |
| `BranchCount` | 3 | a T of mall branches; minimum 3 (two branches are a bend, not a branching), maximum 4 |
| `BranchLength` | 40 m | the shop wings along each branch |
| `MallWidth` | 8 m | a covered public mall with room for kiosks |
| `ShopDepth` | 12 m | shop units on each side of the mall |
| `AnchorDepth` | 30 m | a large store at the end of each branch, across its full width |
| `FloorHeight` | 5 m | tall shop fronts and a mall roof |

- Presets `BranchingMallPresets(Mall, Retail)`. Arm width `A` = `2·ShopDepth + MallWidth` (32 m) and hub side `H` = `A`; each arm is `BranchLength + AnchorDepth` long. The hub is the mall's central court; each arm holds, from the hub outwards, a shop wing of depth `ShopDepth` on either side of a mall strip of width `MallWidth`, then the anchor across the arm's width. Zones `MALL` (*Mall*: the hub and every mall strip, one polygon), then per branch `B{i}-S1`, `B{i}-S2` (*Branch i Shops 1*, …; the shop wings clockwise and counter-clockwise of the mall strip) and `B{i}-AN` (*Branch i Anchor*). Space types `Mall` for the mall and `Retail` for shop wings and anchors (ADR-014).
- Realisation: `R001` retail wings and anchors lie around the branching mall: every shop wing and anchor adjoins `MALL`; `R002` the mall is one connected, branching route reaching every branch. Validation: `BranchCount` 3–4; lengths positive.
- Not modelled: individual shops and tenancies (D-097), branches at other than right angles, rooflights, servicing yards.
- Implemented (S8.5): as specified; the mall is `HubWithStrips` of the shop depth to the shop depth plus the mall width, over the branch length. Zones `MALL` (*Mall*, 1984 m²: the 32 m court and three 40 m × 8 m strips, one polygon of 16 vertices), then per branch `B{i}-S1`, `B{i}-S2` (*Branch i Shops 1*, *Shops 2*, 480 m² each) and `B{i}-AN` (*Branch i Anchor*, 960 m²); 7744 m² by default, with 16 windows (806 m² of glazing): the mall's only outdoor wall is the court's 32 m south side, its entrance, each shop wing has one façade and each anchor three. Every shop wing adjoins the mall over 52 m (40 m along the strip and 12 m at the court) and its anchor over 12 m, and every anchor adjoins the mall over 8 m. With four branches (9984 m²) the mall has no outdoor wall. *Semantic Merge* keeps the mall and unites the two shop wings and the anchor of each branch into one `Retail` zone of 1920 m² around the strip's end; *Perimeter Core* gives `P-North-1` to `P-North-3`, `P-East-1`, `P-East-2`, `P-South`, `P-West-1`, `P-West-2`, and `CORE`.

#### `SYN-TYP-018` Communal hub serving elder-care bedroom groups: `CareHubGenerator` (S8.5)

| Parameter | Default | Reason |
| --- | --- | --- |
| `WingCount` | 3 | three bedroom groups around the hub; minimum 2 (groups, plural), maximum 4 |
| `WingLength` | 30 m | about eight bedrooms of 3.6 m along each side of a wing |
| `BedroomDepth` | 6 m | a care bedroom with its en-suite |
| `CorridorWidth` | 2.4 m | passing wheelchairs and beds |
| `HubWidth` | 16 m | lounge, dining, care station, and kitchenette; at least the wing width |
| `FloorHeight` | 3 m | residential scale |

- Presets `CareHubPresets(CareBedroom, CareCommunal, Corridor)`. Arm width `A` = `2·BedroomDepth + CorridorWidth` (14.4 m), `H` = `HubWidth`. Each wing is a corridor along its axis, from the hub to the wing's end, with a bedroom strip on each side. Zones `HUB` (*Communal Hub*), then per wing `W{i}-CO` (*Wing i Corridor*), `W{i}-B1`, `W{i}-B2` (*Wing i Bedrooms 1*, …).
- Realisation: `R001` bedroom groups are arranged around the communal and service hub; `R002` circulation branches from the hub: every wing corridor adjoins it. Validation: `WingCount` 2–4; lengths positive; `2·BedroomDepth + CorridorWidth` ≤ `HubWidth`.
- Not modelled: individual bedrooms (D-097), the care station as a zone of its own, gardens.
- Implemented (S8.5): as specified; two wings leave the hub east and north. Zones `HUB` (*Communal Hub*, 256 m²), then per wing `W{i}-CO` (*Wing i Corridor*, 72 m²), `W{i}-B1`, `W{i}-B2` (*Wing i Bedrooms 1*, *Bedrooms 2*, 180 m² each); 1552 m² by default. The 14.4 m wings on the 16 m hub leave six 0.8 m hub corners as outdoor walls, which get no window (ADR-011, info `WindowOmitted`), so the default plan has 16 windows (217.92 m² of glazing): one on the hub's 16 m south side, two per bedroom zone (its side and its end), and one at each corridor's 2.4 m end. Every corridor adjoins the hub over 2.4 m, every bedroom zone the hub over 6 m and its corridor over 30 m. *Semantic Merge* keeps every zone, since no two zones of one type touch; *Perimeter Core* gives each hub corner a perimeter zone of its own, 0.8 m × 4.57 m (3.656 m²), and 9 m wings (3.5 m bedrooms and a 2 m corridor) fail it with `PlanTooNarrow` (D-087). The short corners exposed a rounding fault of *Perimeter Core* on rotated plans, fixed in S8.5 ([below](#pipeline-consequences-of-s85)).

#### `SYN-TYP-019` Public foyer branching to distinct activity spaces: `FoyerHallsGenerator` (S8.5)

| Parameter | Default | Reason |
| --- | --- | --- |
| `HallCount` | 2 | two distinct activity spaces; minimum 2, maximum 3 (one arm holds the support rooms) |
| `HallLength` | 30 m | a four-court sports hall or a large community hall |
| `HallWidth` | 20 m | as above |
| `SupportLength` | 10 m | changing rooms, stores, and toilets in one wing |
| `FoyerWidth` | 20 m | a foyer as wide as the halls it serves; at least the hall width |
| `FloorHeight` | 6 m | a hall for sport; the plan has one storey height |

- Presets `FoyerHallsPresets(Lobby, ActivityHall, Service)`. `A` = `HallWidth`, `H` = `FoyerWidth`. Arms in the order east, north, west, south: hall 1 east, the support wing north, hall 2 west, and hall 3 south when `HallCount` is 3; with two halls the foyer's south side is its entrance façade. Zones `FO` (*Foyer*), then `H1…Hn` (*Hall i*), then `SV` (*Support*).
- Realisation: `R001` distinct activity spaces and the support rooms lie around the common foyer; `R002` access branches from the foyer: every hall and the support wing adjoins it. Validation: `HallCount` 2–3; lengths positive; `HallWidth` ≤ `FoyerWidth`. With three halls and `FoyerWidth` = `HallWidth` the foyer has no outdoor wall, which is allowed.
- Not modelled: individual changing rooms and stores (D-097), spectator galleries, halls of different sizes, and different storey heights for halls and foyer.
- Implemented (S8.5): as specified; the halls are listed before the support wing, as the zone list above says, although the support wing is the second arm. Zones `FO` (*Foyer*, 400 m²), `H1`, `H2` (*Hall 1*, *Hall 2*, 600 m² each), `SV` (*Support*, 200 m²); 1800 m² by default, a T whose short stem is the support wing, with 10 windows (276 m² of glazing): the foyer's 20 m south entrance façade (WWR 0.5), three per hall, and three on the support wing. Every hall and the support wing adjoins the foyer over the hall width and no other zone. Three halls (2400 m²) close the foyer's south side, so the foyer has no outdoor wall; a foyer wider than the halls leaves its corners outdoor (a 24 m foyer with three halls: eight 2 m walls, each with a window). *Semantic Merge* keeps every zone; *Perimeter Core* gives `P-North-1` to `P-North-3`, `P-East-1`, `P-East-2`, `P-South`, `P-West-1`, `P-West-2`, and `CORE`.

#### Pipeline consequences of S8.5

Every plan simplifier and floor aggregator was run on the four families, canonical, at the two rotated placements of the test suite, and with the fewest and the most arms, and, while building the reference, in a sweep of 50 rotations from 0° to 353.5° with translations for each family with its fewest, default, and most arms, 11 m lobes on a 12 m core, and a 24 m foyer with three halls. It found one fault, now fixed:

- *Perimeter Core* united the trapezoids of one orientation bin with a plain union, which rounds every vertex to the clipping grid. On a rotated plan the wall on a footprint edge shorter than about 1 m, such as a 0.8 m hub corner of the care hub, then differs in direction from the source wall by more than the angular tolerance (ADR-004), so *Single Zone per Floor Type* and *Single Zone Building* reported `FacadeNotCovered` for it: in 22, 10, and 26 of 800 combinations of the care hub with 3, 2, and 4 wings in the sweep, and at the test suite's 131.4° placement. The union now keeps the footprint's own vertices; the mitred offset vertices keep their rounding, so every existing result is unchanged ([ADR-008](ADR-008-perimeter-core-corners.md), [ADR-002](ADR-002-geometry.md)). No tolerance or check was relaxed, and after the fix the sweep has no failure.

Nothing else in `Lod.Core` changed. Arms as wide as the hub give the footprint only re-entrant corners, which the bisector rule of *Perimeter Core* handles (S8.2); arms narrower than the hub add short steps at the hub's corners, which it handles too, each step getting a small perimeter zone. Arms not wider than twice the perimeter depth fail *Perimeter Core* with `PlanTooNarrow` (D-087), a precondition of the simplifier that the generators do not impose.

#### `SYN-TYP-015` Operating suite with separated clean and dirty routes: `OperatingSuiteGenerator` (S8.6)

| Parameter | Default | Reason |
| --- | --- | --- |
| `BankCount` | 2 | repeated theatre banks; minimum 2 |
| `BankLength` | 36 m | four theatres of about 9 m with their anaesthetic rooms in one bank |
| `TheatreDepth` | 7 m | a theatre of about 9 m × 7 m |
| `CleanCorridorWidth` | 3 m | a clean route wide enough for beds |
| `DirtyCorridorWidth` | 2.4 m | a disposal route for trolleys |
| `SupportLength` | 12 m | scrub, stores, recovery, and sluice across the suite's west end |
| `FloorHeight` | 4.2 m | a ceiling plenum for theatre air handling |

- Presets `OperatingSuitePresets(OperatingTheatre, CleanCorridor, DirtyCorridor, ClinicalSupport)`. The support rooms `[0, SupportLength]` span the suite's full depth at its west end; east of them, bands along plan x of length `BankLength` are stacked from south to north: a dirty corridor, then for each bank the bank and the next corridor, the corridors alternating clean and dirty (`DC1`, `TB1`, `CC1`, `TB2`, `DC2`, `TB3`, `CC2`, …), so every bank lies between a clean and a dirty corridor and consecutive banks share a corridor. Zones `SUP` (*Support*), then the bands south to north: `DC{k}` (*Dirty Corridor k*), `TB{k}` (*Theatre Bank k*), `CC{k}` (*Clean Corridor k*).
- Realisation: `R001` repeated theatre banks beside the support rooms: every bank and corridor adjoins `SUP`; `R002` distinct clean and dirty routes: every bank adjoins one clean and one dirty corridor, and no clean corridor adjoins a dirty one. Validation: `BankCount` ≥ 2; lengths positive.
- Not modelled: individual theatres and their anaesthetic and preparation rooms (D-097), pressure cascades (only the presets' ventilation), lifts.
- Implemented (S8.6): as specified. Zones `SUP` (*Support*, 261.6 m²), then south to north `DC1` (*Dirty Corridor 1*, 86.4 m²), `TB1` (*Theatre Bank 1*, 252 m²), `CC1` (*Clean Corridor 1*, 108 m²), `TB2`, `DC2`; by default the plan is 48 m × 21.8 m (1046.4 m²). A corridor follows every bank, so *n* banks have *n* + 1 corridors, ⌈*n*/2⌉ clean and ⌊*n*/2⌋ + 1 dirty, and the northmost band is a dirty corridor for an even count and a clean one for an odd count (`CC2` with three banks). Every bank and corridor adjoins `SUP` over its full depth; every bank adjoins its two corridors over the bank length and no other bank; every corridor adjoins only banks and `SUP`. The outdoor walls are `SUP`'s west, south, and north sides, every band's east end, `DC1`'s south side, and the northmost corridor's north side, so a bank's only outdoor wall is its 7 m east end. The theatre preset's WWR is 0, so those walls get no window and no `WindowOmitted` info (ADR-011 rule 1: no glazed area, no window, no diagnostic); the default plan has 8 windows (71.988 m² of glazing): three on `SUP`, two on each dirty corridor, and one at the clean corridor's end. A theatre preset with glazing gives each bank one window on its east end. *Semantic Merge* keeps every zone, since no two zones of one type touch; *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, and a `CORE` of 38.86 m × 12.66 m (491.9676 m²) over `SUP`, both banks, and `CC1`; `P-East` carries the glazing of every band's east end. The family has no upper bound; 2 to 5 banks are tested.

#### `SYN-TYP-011` Linked housing clusters around multiple courts: `CourtClusterGenerator` (S8.6)

| Parameter | Default | Reason |
| --- | --- | --- |
| `CourtCount` | 2 | several shared courts; minimum 2 (one court is `005`) |
| `CourtWidth` | 24 m | twice the wing depth, as `005` |
| `CourtDepth` | 24 m | a square court, as `005` |
| `Depth` | 12 m | wing depth, a through dwelling |
| `UnitWidth` | 7 m | as `001` |
| `StairWidth` | 3 m | as `001` |
| `FloorHeight` | 3 m | housing |

- Presets `CourtClusterPresets(DwellingUnit, Stair)`. A row of `CourtCount` courts along plan x: south and north wings across the full width, then a west wing, `CourtCount − 1` middle wings between neighbouring courts, and an east wing, every wing a bar of stair bays fitted to its length as for `005`. The footprint is the outer rectangle with one hole per court. Zones `S-…`, `N-…` (west to east), then `W-…`, `M{i}-…` (middle wing `i`, west to east), `E-…`, each wing stairs first, then dwellings, as in `005`.
- Realisation: `R001` dwelling wings linked into one cluster around several courts; `R002` the courts lie between dwelling groups (each middle wing borders two courts); `R003` access is distributed: every wing has its own stairs. Validation: `CourtCount` ≥ 2; lengths positive; the stair bays fit every wing (`StairBayLayout.FitErrors`).
- Not modelled: courts that are not in one row or not rectangular, the outdoor routes through the courts, a route hierarchy.
- Implemented (S8.6): as specified, on `StairBayLayout` like `005`, which is unchanged: the two generators share the bay geometry and its fitting and differ only in where their wings and holes lie, so no further helper is extracted. With `k` courts the plan is `(k + 1)·D + k·w` wide; middle wing `i` (from 1) lies at `x ∈ [i·(D + w), i·(D + w) + D]` and the east wing at `x ∈ [k·(D + w), k·(D + w) + D]`, both over `y ∈ [D, D + c]`; court `j` (from 1) is the hole `[(j − 1)·(D + w) + D, j·(D + w)] × [D, D + c]`, stored clockwise, holes west to east. Zones `S-ST1…S-ST5`, `S-U1…S-U10` (*South Stair 1*, *South Unit 1*, …; five bays of 6.9 m dwellings in the 84 m south wing), the same for `N-…`, then `W-ST1`, `W-U1`, `W-U2`, `M1-ST1`, `M1-U1`, `M1-U2` (*Middle 1 Stair 1*, *Middle 1 Unit 1*, …), and `E-ST1`, `E-U1`, `E-U2` (one bay of 10.5 m dwellings in each 24 m wing, south to north); 2880 m² (84 m × 48 m less two 24 m × 24 m courts), 39 zones, 72 windows, 32 of them on the court façades, 16 per court (158.4 m² of the 374.4 m² of glazing). The zones of a middle wing have only court façades, west into one court and east into the next. Validation fits the stair bays to the south and north wings only for a valid `CourtCount`, since their length depends on it (`StairWidth 30 m leaves no dwelling width in each 84 m south and north wing: …`), and to the side wings (`… in each 24 m west, middle, and east wing: …`). *Semantic Merge* gives six dwelling zones, an L around each outer corner (374.4 m²) and a T where the middle wing meets the south or north wing (457.2 m²), and the thirteen stairs; no merged zone has a hole. *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, one court zone per court and bin, `P-Court-North-1`, `P-Court-North-2`, … `P-Court-West-2` (130.5649 m² each, [ADR-008](ADR-008-perimeter-core-corners.md)), and a `CORE` with one hole per court (712.5404 m²); 9 m wings fail it with `PlanTooNarrow` (D-087). The family has no upper bound; up to 6 courts are tested in the generator's tests and 4 through every simplifier and aggregator.

#### Pipeline consequences of S8.6

Every plan simplifier and floor aggregator was run on both families, canonical, at the two rotated placements of the test suite, with the fewest and the most tested counts (2 and 5 banks, 2 and 4 courts), and with the most at 131.4°, and, while building the reference, in a sweep of 50 rotations from 0° to 353.5° with translations for the operating suite with 2, 3, and 5 banks, the court cluster with 2, 3, and 4 courts, one plan of each with other dimensions, and, as a regression, the enclosed court and the four S8.5 families with their fewest and most arms: 14 400 combinations without a failure. No step of `Lod.Core` changed, and no tolerance or check was relaxed:

- The court cluster is the first footprint with several holes. The surface builder and its boundary coverage, *No Simplification*, *Semantic Merge*, *Single Zone per Floor*, the four floor aggregators, and validation treat every hole as they treat the one hole of `005` ([ADR-002](ADR-002-geometry.md)).
- *Perimeter Core* offsets every hole by the bisector rule and unites the court trapezoids of one bin across all holes, as it did for one hole. The middle wings keep the bands of neighbouring courts apart, so each bin gives one polygon per court, numbered `P-Court-<Bin>-1`, `-2`, … in the union's output order, which is west to east on the canonical plan but is not a court number on a rotated plan. Its check that the offset holes lie apart from each other is what rejects middle wings not wider than twice the depth (`PlanTooNarrow`, D-087, [ADR-008](ADR-008-perimeter-core-corners.md)).
- The theatre banks are the first generated zones whose outdoor walls get no window because their preset's WWR is 0; the base's window rule already places none and reports nothing for them (ADR-011), and every later step conserves the glazing that remains.

#### `SYN-TYP-012` Stepped dwelling bands with exposed terraces: `SteppedBandGenerator` (S8.7)

| Parameter | Default | Reason |
| --- | --- | --- |
| `StoreyCount` | 3 | a band stepping back twice; minimum 2 |
| `Length` | 36 m | a band of five or six dwellings per storey |
| `BaseDepth` | 14 m | dwelling depth on the ground storey |
| `StepDepth` | 3 m | a terrace deep enough to sit on |
| `CorridorWidth` | 2 m | the shared circulation edge along the band's rear |
| `UnitWidth` | 6 m | target dwelling width; adjusted to fill the band |
| `StairWidth` | 4 m | a stair at the west end |
| `FloorHeight` | 3 m | housing |

- Presets `SteppedBandPresets(DwellingUnit, Corridor, Stair)`. The generator returns one plan per storey ([D-095](decision-log.md#d-095--a-plan-generator-may-produce-a-different-plan-per-storey); the interface, how the floor aggregators treat storeys that differ, and the designation of terraces are fixed in [ADR-015](ADR-015-plans-per-storey.md)). On storey `k` (from 0) the dwellings span `y ∈ [k·StepDepth, BaseDepth]` and `x ∈ [StairWidth, Length]`, divided evenly into `max(1, round((Length − StairWidth) / UnitWidth))` dwellings; the corridor `CO` spans `[0, Length] × [BaseDepth, BaseDepth + CorridorWidth]` on every storey and the stair `ST` `[0, StairWidth] × [k·StepDepth, BaseDepth]`. The part of storey `k − 1`'s roof that storey `k` does not cover, `[0, Length] × [(k − 1)·StepDepth, k·StepDepth]`, is a terrace: an outdoor roof (D-068). Zones per storey `ST`, `CO`, `U1…Un` (west to east).
- Realisation: `R001` the band steps back storey by storey, so that lower roofs become terraces; `R002` every dwelling adjoins the shared corridor along the rear. Validation: `StoreyCount` ≥ 2; lengths positive (`StepDepth` > 0: the stepping is essential); `BaseDepth − (StoreyCount − 1)·StepDepth` > 0, so the top storey keeps dwellings.
- Not modelled: terrace parapets, planting, and shading; an internal gallery instead of a rear corridor; steps on both sides of the band.
- Implemented (S8.7): as specified, as the first `MultiStoreyPlanGenerator` ([ADR-015](ADR-015-plans-per-storey.md)): `Generate` returns the storeys bottom-up, each an ordinary plan whose provenance adds `Storey` (from 0); the dwelling count is `SteppedBandGenerator.DwellingsPerStorey`, the same on every storey, so dwelling `Ui` of storey `k + 1` stands on dwelling `Ui` of storey `k`. Zones per storey `ST` (*Stair*), `CO` (*Corridor*), `U1…U5` (*Unit 1…*; five dwellings of 6.4 m by default). By default the three storeys are 576 m², 468 m², and 360 m² (1404 m²), each lower storey keeping a 36 m × 3 m terrace of 108 m²; every storey has 11 windows (33 in all, 201.6 m² of glazing: 70.8, 67.2, and 63.6 m² from the ground up), and the south walls of the stair and the dwellings of storeys 1 and 2 face the terrace below them and keep their windows. Every dwelling and the stair adjoin the corridor over their full width on every storey (6.4 m and 4 m). Validation settles two further essential relationships: `Length` must exceed `StairWidth` (`Length 4 m must exceed StairWidth 4 m, so that the band has dwellings beside the stair (R002).`), and the top storey must keep its dwellings (`BaseDepth 12 m leaves no dwelling depth on the top storey: its 4 steps of StepDepth 3 m take 12 m; SYN-TYP-012 needs dwellings on every storey, so reduce StoreyCount or StepDepth, or increase BaseDepth.`); both are checked only when every length is positive. `StoreyCount` < 2 is `StoreyCount must be at least 2 (the band steps back from storey to storey, R001), got 1.` *Semantic Merge* gives each storey the stair, the corridor, and one dwelling zone (448, 352, and 256 m²); *Perimeter Core* gives every storey `P-North`, `P-East`, `P-South`, `P-West`, and a `CORE` 26.86 m long, and needs the top storey, the narrowest, to be deeper than twice the perimeter depth: with the default 4.57 m the cores of the three default storeys are 6.86 m, 3.86 m, and 0.86 m deep, and four storeys of the default 14 m leave a 7 m deep top storey that fails with `PlanTooNarrow` (D-087) while the storeys below pass. The family has no upper bound; 2 to 5 storeys are tested in the generator's tests and 2 to 4 through every simplifier and aggregator.

#### Pipeline consequences of S8.7

Every plan simplifier and floor aggregator was run on the stepped band, each storey simplified on its own and the storeys stacked bottom-up with multiplier 1, canonical, at the two rotated placements of the test suite (every storey placed alike), with 2 and 4 storeys (4 with a 17 m base depth), and with 4 at 131.4°, and, while building the reference, in a sweep of 50 rotations from 0° to 353.5° with translations for the default band, 2 storeys, 4 storeys of 17 m, and a band of other dimensions, and, as a regression, the linear plan, the enclosed court, the court cluster, and the care hub (entries 1/3/1): 6400 combinations without a failure. No step of `Lod.Core` changed apart from the new base class and the helper it shares with `PlanGenerator`, and no tolerance or check was relaxed:

- The floor aggregators already take floors that differ (setbacks since S4) and designate floors and ceilings on the assembled stack (D-068): the part of each lower ceiling that the storey above does not cover faces outdoors and counts as roof, the covered part lies between the storeys. In every method the terraces on each lower storey are `Length × StepDepth`, the roofs and terraces together equal the ground storey's footprint, no floor is exposed, and no storey is unsupported ([ADR-015](ADR-015-plans-per-storey.md), [ADR-013](ADR-013-vertical-aggregation-methods.md)).
- `StackedFloorZoneMultiplier` models every storey, since every entry has multiplier 1; `SingleZonePerFloorType` makes one zone per storey with interzone pairs over the covered slabs; `SingleZoneBuilding` makes one zone with one part per storey outline and turns the covered slabs into internal mass. Their rebuilt walls include the south walls that face the terraces, each with one centred window (D-079).

## Consequences

- A new family is a folder with three types and a component; the base keeps presets, surfaces, windows, and provenance identical across families, and every family passes the same tiling, window, determinism, and simplifier × aggregator tests.
- Families do not share parameter or preset records, even where their fields coincide (001 and 008), so each component's inputs match its family exactly (AGENTS.md: typed parameter records per typology).
- The defaults are design choices, recorded here with their reasons; changing one changes the canonical snapshot of its family and is recorded in this ADR.
- The gallery of `HDHM-TYP-002` and the internal stairs of `HDHM-TYP-006` are not in the energy model; results for those families exclude the gallery's shading and the stairs as separate zones.
- `HDHM-TYP-006` houses are one zone per storey; comparisons that count zones per dwelling must take that into account.
- The source's abstract validation records are not used as tests (D-083); a sub-stage that refines a layout updates the realisation text here.
- Wings and plates narrower than twice the perimeter depth, including the wings between the outer and the court façades of `HDHM-TYP-005`, cannot be zoned by *Perimeter Core* (`PlanTooNarrow`); the user chooses a smaller depth or another simplifier.
- The court of `HDHM-TYP-005` is outside the building: its façades are outdoor walls with windows, and it has no ground slab, roof, or zone.
- The four-source families (S8.4–S8.7) are specified before they are built; their defaults are controller design defaults (D-098), and every non-residential zone is a department (D-097, ADR-014), so a non-residential detailed model has fewer and larger zones than a room-level model.
- The office plate's work area is the first zone with a hole whose footprint has none (a ring around the core); the surface builder, every simplifier, and every floor aggregator handle it (S8.4).
- Arms on the sides of a hub are limited to four by the axis-aligned layout (S8.5); counts beyond the limits in the tables are `InvalidParameter`.
- The hub-and-arms families share one layout (`HubArmsLayout`, S8.5); arms narrower than the hub leave short hub façades at its corners, which get no window below the ADR-011 limits (the care hub's 0.8 m corners by default).
- The stepped band (`SYN-TYP-012`, S8.7) is the only family whose generator returns one plan per storey (`MultiStoreyPlanGenerator`, [ADR-015](ADR-015-plans-per-storey.md)); its terraces are outdoor roofs designated on the assembled stack, and its narrowest storey, the top one, decides whether *Perimeter Core* applies (D-087).
- The court cluster (`SYN-TYP-011`, S8.6) has several holes; *Perimeter Core* gives each court its own court zone per bin, whose number follows the union's output order, not a court. The operating suite (`SYN-TYP-015`, S8.6) has no glazing on its theatre banks with the example theatre preset (WWR 0); the banks' only outdoor walls are their east ends.
