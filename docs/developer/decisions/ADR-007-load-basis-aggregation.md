# ADR-007: Load-basis aggregation

Status: Accepted; superseded in part by [ADR-017](ADR-017-program-mix-and-building-infiltration.md) (the exterior-wall basis and fraction left the program with infiltration, D-124)

Date: 2026-10-01

Decisions: D-019, D-041, D-047

ADR-006 is reserved for the plan generation mechanism (S7).

## Context

The research brief §7 conserves installed and per-timestep scheduled load with `p* = Σ Aᵢpᵢ / Σ Aᵢ` and `s*(t) = Σ Aᵢpᵢsᵢ(t) / Σ Aᵢpᵢ`. §9 treats rezoning as a mapping with transfer fractions, conserving extensive quantities `Q_j = Σᵢ f_ji Q_i` and weighting intensive quantities by "the appropriate basis". The repository spec (§4.6) lists load bases: area density, per person, absolute, façade-area based, and air-change based. D-019 requires air-change loads to be volume weighted. Plan simplifiers split source zones across several targets (S3), so the rule must work with fractions, not only with whole-zone merges. D-041 adds that fractions normalised per source wall are safe only when the target façades cover each source façade completely. One program may express a load type in more than one basis (ASHRAE 62.1 ventilation is per person plus per floor area), and simplified zones merge programs that express the same load type in different bases, e.g. ventilation per person in one and per floor area in another (D-047).

## Options considered

1. **One formula per basis** (area weighting, occupancy weighting, summation, façade weighting, volume weighting). Five code paths, each to be proven conservative separately, each needing its own rule for split zones.
2. **One magnitude rule for every basis.** Convert each source value to an absolute design magnitude, transfer a fraction of it, sum, and re-express the sum in the same basis. The per-basis rules follow as special cases.
3. **Express every target load as an absolute magnitude.** Conservation is trivial, but the target program would no longer be expressed like the source program (GLOBAL.md scientific rule 3).
4. **Several bases for one load type, within a program or among the sources of a target.**
   - *Aggregate each (load type, basis) component separately; components of one type add up* (adopted, D-047). Every component is conserved exactly by the rule of option 2, and no basis is converted.
   - *Reject mixed bases* (rejected). It blocks legitimate program combinations: ventilation per person plus per floor area within one program, or merging a zone with per-person ventilation into one with per-area ventilation.
   - *Convert them to one basis* (rejected). It would choose a basis silently and change program assumptions (GLOBAL.md scientific rule 3).
5. **The exterior-area basis: walls and roofs, or walls only.** Plan simplifiers work on one storey before floors are stacked, so whether a ceiling becomes a roof is unknown when loads are aggregated. Counting walls only keeps the basis well defined at every pipeline step.

## Decision

**Units of design magnitudes.** Occupancy in people; lighting, electric equipment, and gas equipment in W; domestic hot water, ventilation, and infiltration in m³/h.

**Bases.** A load value is expressed per a basis quantity `B`; its design magnitude is `Q = value × B`.

| Basis | Basis quantity `B` |
| --- | --- |
| `PerFloorArea` | floor area, m² |
| `PerPerson` | design occupants of the zone, the summed magnitude of its occupancy components |
| `Absolute` | 1 |
| `PerExteriorWallArea` | gross area of the zone's walls with an outdoor boundary, windows included, m²; walls only, no roofs |
| `AirChangesPerHour` | zone volume, m³, so `Q = ACH × V` in m³/h |

Occupancy may only be `PerFloorArea` or `Absolute`. A program with a `PerPerson` load must also contain an occupancy load.

**Components (D-047).** A program holds at most one load per load type and basis; a load type expressed in several bases has several components, which add up (ventilation per person plus per floor area). Occupancy may have components too: the zone's design occupants are their sum, and every `PerPerson` component uses that sum.

**One rule for every basis.** Each component (load type and basis) is aggregated on its own. For each component of a target zone, every source zone `i` that has the component transfers

```text
Tᵢ = fᵢ · Qᵢ
```

where `fᵢ` is the exterior-wall fraction (the share of the source's exterior wall area that becomes the target's exterior wall area) for `PerExteriorWallArea` loads, and the area fraction (the share of the source's floor area, and with it of its volume, occupants, and absolute loads) for every other basis. A source without the component contributes nothing to it. Then

```text
Q*     = Σᵢ Tᵢ
value* = Q* / B*                 B* = the target's quantity of the component's basis
s*(t)  = Σᵢ Tᵢ · sᵢ(t) / Q*
```

Occupancy components are aggregated first, so the `B*` of a `PerPerson` component is the target's design occupants summed over all its occupancy components.

For whole-zone merges (`fᵢ = 1`) this gives area weighting for `PerFloorArea` (`value* = Σ Aᵢpᵢ / Σ Aᵢ`, the research brief §7 formulation), occupancy weighting for `PerPerson`, summation for `Absolute`, exterior-wall-area weighting for `PerExteriorWallArea`, and volume weighting for `AirChangesPerHour` (`ACH* = Σ VᵢACHᵢ / Σ Vᵢ`, D-019).

**Errors and the zero-magnitude rule.** Sources of one target that define the same load type in different bases are not an error: each basis is its own component. Per component:

- `Q* > 0` while the target's basis quantity `B*` is 0: error, because the magnitude cannot be expressed in the target.
- `Q* = 0`: value 0, a constant-zero fraction schedule, and an informational diagnostic. This is the zero-denominator guard of the schedule formula.

**Traceability.** Every aggregated load component records its method (`MagnitudeConserved`), source zones, and transferred magnitudes `Tᵢ` as weights; its schedule records `MagnitudeWeighted` with the same sources and weights (ADR-003).

**Transfer fractions.** Area fractions are normalised per source, `f_ji = overlap_ji / Σⱼ overlap_ji`, so each source's fractions sum to exactly 1 and every extensive quantity is conserved to floating-point precision regardless of polygon rounding; how well the targets cover each source is a separate validation check. Exterior-wall fractions come from matching source and target outdoor walls that lie on the same façade line and are normalised per source wall in the same way (S3).

**Façade coverage first (D-041).** Normalisation alone would hand the whole wall area of a source wall to a target façade that covers only part of it. `PerExteriorWallArea` transfers therefore use exterior-wall fractions only after façade coverage is proven: for every source outdoor wall `i`, the target outdoor walls on the same façade line must cover its full length, `Σⱼ Lᵢⱼ ≈ Lᵢ` within the relative tolerance of ADR-004, checked before any normalisation. Plan simplifiers and `SingleZoneMerged` fail when it does not hold, and floor validation enforces it as a separate check.

**Invariants.** For each load component (load type and basis), the installed magnitude `Σ Q` and the scheduled magnitude `Σ Q · s(t)` at each of the 8760 hours are conserved within `RelativeLoad` (ADR-004); the totals of each load type, the sums of its components, are therefore conserved too. Occupancy and air flows are load types, so the same checks cover them, and the design occupants, the sum of the occupancy components, are conserved.

## Worked example

Lighting in two source zones merged whole into one target (`f = 1` for both):

| Zone | Floor area | Value | Magnitude `Q = value × area` |
| --- | --- | --- | --- |
| A | 10 m² | 5 W/m² | 50 W |
| B | 30 m² | 1 W/m² | 30 W |
| Target | 40 m² | 80 W / 40 m² = 2 W/m² | 80 W |

The target schedule is `s*(t) = (50 · s_A(t) + 30 · s_B(t)) / 80`: the source schedules are weighted 50:30. In an hour with `s_A = 1` and `s_B = 0`, `s* = 0.625`, and the target's scheduled magnitude 2 W/m² × 40 m² × 0.625 = 50 W equals the sources' 50 W × 1 + 30 W × 0. Weighting the schedules by floor area instead, (10 · 1 + 30 · 0) / 40 = 0.25, would give only 20 W in that hour: floor-area weighting is right for the value, magnitude weighting for the schedule.

Mixed bases (D-047): source A (100 m², 0.1 people/m², so 10 people) has ventilation 30 m³/h per person; source B (100 m², no occupancy) has ventilation 2 m³/h per m². Merged whole into a 200 m² target, the target has 10 people and two ventilation components: per person, 300 m³/h / 10 people = 30 m³/h per person with A's schedule; per floor area, 200 m³/h / 200 m² = 1 m³/h per m² with B's schedule. Each component conserves its source magnitude at every hour, and the target's total ventilation is their sum.

## Consequences

- One code path implements every basis, so conservation is proven once.
- Bases survive simplification: a per-floor-area load stays per floor area in the target.
- Programs that express a load type in different bases can be merged; each basis stays a separate component in the target, so a target may carry several components of one type, each with its own schedule.
- A positive magnitude that cannot be expressed in the target's basis fails instead of being dropped.
- A zoning whose target façades leave part of a source façade uncovered fails, instead of shifting that façade's wall-based loads silently.
- The research brief §9 records the rule in the same change.
