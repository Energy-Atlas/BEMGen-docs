# ADR-005: Conditioning and setpoint aggregation

Status: Accepted; superseded in part by [ADR-018](ADR-018-program-json-and-extended-programs.md) (heating and cooling are separate sides: a conditioned zone needs one or both setpoints, each side is aggregated over the sources that have it, and a merge whose heating exceeds its cooling is an error)

Date: 2026-10-01

Decisions: D-038 (superseding D-027, D-028, and D-029)

## Context

When a plan simplifier or floor aggregator merges zones, the target zone needs one conditioning status and, if it is conditioned, one heating and one cooling setpoint schedule. Setpoints are controls, not additive loads (GLOBAL.md scientific rule 5): averaging them conserves no physical quantity, so the rule is a modelling choice that must be explicit and recorded. The research brief §7 lists candidate rules: the dominant source schedule, an area-weighted temperature schedule, a load-weighted schedule, or prohibiting merges of zones with incompatible setpoints.

The decision went through several steps. D-010 made the aggregation method a parameter with two options, floor-area weighting and exposed-surface-area weighting, and D-014 settled its details: the method was a required input; exposed area counted exterior walls (with their windows) and roofs; and when the exposed-area weights summed to zero, the weights fell back to floor area with a warning. D-027 replaced both entries with floor-area weighting only. D-028 treated every space as conditioned, and D-029 framed that as an intentional homogenisation. Plan review then found that with every space conditioned, every source has a thermostat, so the setpoint rule is never exercised, and Z0 loses the distinction between dwelling units and unconditioned corridors, stairs, or other spaces. D-038 supersedes D-027, D-028, and D-029.

## Options considered

### Conditioning status

1. **Every space conditioned (D-028, D-029).** Keeps conditioning out of the LoD variables, but the setpoint rule is never exercised and Z0 cannot represent unconditioned spaces.
2. **Conditioning from the program preset (D-038).** Each program is conditioned, with a thermostat, or unconditioned, without setpoints.

### Conditioning of a merged zone

1. **Conditioned only if every source is conditioned.** Merging a dwelling unit with an unconditioned stair would drop the dwelling unit's thermostat.
2. **Conditioned if any source contributing floor area is conditioned ("any conditioned wins", D-038).** Conditioned floor area never ends up without setpoints; in exchange, unconditioned floor area merged into a conditioned target becomes conditioned.
3. **Never merging conditioned with unconditioned spaces.** Would constrain perimeter/core and one-zone-per-floor zoning, which merge different space types by design.

### Setpoint weighting

1. **The dominant source schedule.** Ignores every other source, and small geometric changes can flip which source dominates, so the result jumps.
2. **Prohibiting merges of zones with incompatible setpoints.** Perimeter/core and one-zone-per-floor zoning merge different space types by design; they would be impossible whenever presets differ.
3. **Load weighting.** No single load is the natural weight, and the control assumption would change whenever an internal gain changes.
4. **Exposed-surface-area weighting (D-010, D-014).** Rejected for the reasons recorded in D-027, which D-038 keeps:
   - It makes the control assumption depend on geometry, which confounds the experiment: simplification should change geometry, not the thermostat assumption.
   - Split source zones carry floor area by overlap, but no well-defined share of exposure.
   - The zero-exposure fallback to floor area is discontinuous: a target whose sources have a tiny exposed area is weighted by exposure, one whose sources have none by floor area.
   - Exposure varies across typologies with the same program, so the same program would get different setpoints by typology.
5. **A method parameter (D-010, D-014).** More freedom, but every result would depend on a choice outside the LoD variables under study.
6. **Floor-area weighting over the conditioned sources.** Depends only on the floor area each conditioned source contributes, is continuous, and is defined for split zones.

### Conditioned floor area

1. **Enforce its conservation.** Every zoning that merges conditioned and unconditioned spaces would fail validation.
2. **Report the change without enforcing it (D-038).** The enlargement is a consequence of the zoning simplification under study, and it stays visible.

## Decision

**Conditioning comes from the program preset.** A conditioned program has a thermostat: a heating and a cooling setpoint schedule, both `Temperature` schedules (ADR-003). An unconditioned program has no setpoints.

**Any conditioned wins.** A target zone is conditioned if any source zone contributing floor area to it (area fraction above 0) is conditioned. A source that contributes only façade (area fraction 0) does not condition the target. If no contributing source is conditioned, the target is unconditioned and has no setpoints.

**Setpoints.** The heating and the cooling setpoint schedule of a conditioned target are each aggregated hour by hour by floor-area weighting over the conditioned contributing sources `C`:

```text
T*(t) = Σᵢ∈C wᵢ · Tᵢ(t) / Σᵢ∈C wᵢ        wᵢ = fᵢ · Aᵢ
```

`Aᵢ` is the floor area of source zone `i` and `fᵢ` the fraction of it transferred to the target, so `wᵢ` is the transferred floor area: the whole source area for a merged zone, and the part mapped to the target (its overlap) for a split zone.

- There is no method input, no exposed-area definition, and no fallback.
- The result is a `Temperature` schedule whose `AggregationRecord` holds the method `FloorAreaWeighted`, the conditioned source zones, and the weights `wᵢ` (ADR-003). This record, together with the provenance of the producing operation, is the experiment metadata the research brief §7 requires.
- A total weight of zero is an error (`ZeroSetpointWeight`). It occurs only when the conditioned contributing sources have zero floor area.
- Setpoint aggregation is a prescribed control rule, not a conservation invariant. Validation does not check setpoints for conservation; tests check the definition instead: the result equals the weighted mean over the conditioned sources at every hour; a single source returns its own schedule; the order of sources does not change the result; unconditioned sources carry no weight; a target whose contributing sources are all unconditioned is unconditioned; and façade-only sources do not condition a target.
- **Conditioned floor area.** Merging conditioned and unconditioned sources enlarges the conditioned floor area. Validation reports the conditioned floor area of source and target but does not enforce their equality.
- Exposed-surface-area weighting stays rejected for the reasons in D-027.
- D-027, D-028, and D-029 are superseded by D-038; D-010 and D-014 had already been superseded by D-027.

## Consequences

- The setpoint rule is exercised whenever conditioned zones with different setpoints merge, and Z0 keeps the distinction between conditioned and unconditioned spaces.
- A target zone's thermostat depends only on the conditioned floor area it receives, not on its façades, so simplification does not tie the control assumption to geometry.
- Conditioning itself can change with zoning: unconditioned floor area merged into a conditioned target becomes conditioned. The validation report shows the change, so results can be read with it in mind.
- Example with illustrative values: merging 30 m² conditioned at 21 °C, 10 m² conditioned at 17 °C, and 5 m² unconditioned gives a conditioned target at (30 × 21 + 10 × 17) / 40 = 20 °C for that hour; the conditioned floor area grows from 40 m² to 45 m², and validation reports it.
- Conditioning values come from the program presets. The example presets of S1 are illustrative; sourced conditioning for the DOE prototype is an open research input (roadmap §7).
- Converters handle unconditioned zones: `Convert2BEM` carries a conditioned flag (S2), and ADR-010 covers unconditioned zones for `Convert2IDF` (S6).
- The research brief §7 records the rule in the same change.
