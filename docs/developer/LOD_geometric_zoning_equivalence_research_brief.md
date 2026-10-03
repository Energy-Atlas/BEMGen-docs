# Geometric Level of Detail and Zoning Equivalence Study for Building Energy Modeling

## 1. Project Context

This project is a side study within the broader Level of Detail research program for Building Energy Modeling. Its purpose is to quantify how geometric simplification, thermal zoning strategy, and window representation affect building energy simulation results when all non-geometric modeling assumptions are held equivalent.

The study will use a high-detail reference model as the ground truth representation and derive a family of systematically simplified models from it. Each simplified model must preserve the same underlying building program, internal gains, schedules, conditioning assumptions, and aggregate envelope quantities unless the experiment explicitly varies them.

The central research principle is:

> Different geometric and zoning representations should be compared only after their non-geometric energy-model inputs have been transformed into equivalent representations.

The objective is therefore not simply to generate alternative floor plans or EnergyPlus models. It is to construct a reproducible pipeline that creates **equivalent models under different geometric Levels of Detail (LoD)** and measures the resulting simulation error across climates, building typologies, zoning strategies, and window representations.

---

## 2. Research Questions

The study should answer the following questions.

1. How much error is introduced by simplifying a detailed building floor plan into coarser thermal zoning representations?
2. How does the effect of zoning simplification vary by building typology, across housing and non-residential programs (D-094)?
3. How much error is introduced when explicitly located windows are replaced by simplified window-to-wall-ratio representations?
4. How sensitive are results to redistributing or aggregating windows after zones are merged?

Questions 3 and 4 are not pursued as a separate window axis in this project: windows follow one rule at every level (§10, D-079), and their effect is part of the zoning and vertical simplification under study.
5. How much additional error is introduced by vertical simplification, such as:
   - making floors geometrically identical,
   - simulating floors independently,
   - using one thermal zone per floor,
   - using EnergyPlus floor multipliers?
6. Do the same simplifications produce similar errors under different weather conditions?
7. Which output metrics are most sensitive to geometric and zoning simplification:
   - annual energy,
   - monthly energy,
   - peak loads,
   - hourly loads,
   - heating/cooling balance,
   - thermal comfort or zone temperature,
   - load duration characteristics?
8. Which simplifications are acceptable for different classes of UBEM analysis?

---

## 3. Ground-Truth Reference Model

The highest-detail representation should approximate the organization found in detailed prototype or archetype models, such as DOE prototype building models.

The reference representation may include:

- individual dwelling units,
- departments of non-residential floors (D-097),
- corridors or aisles,
- stairwells,
- entrance or porch zones where relevant,
- service or circulation spaces,
- distinct perimeter exposures,
- realistic exterior façade assignments,
- explicitly positioned windows,
- floor-specific plan variation,
- vertically stacked but potentially non-identical floor plans,
- semantically distinct space types.

Each space or thermal zone must retain explicit semantic metadata so that the same underlying program can be reconstructed after geometric simplification.

Recommended semantic attributes include:

- `SpaceType`
- `UnitType`
- `FloorIndex`
- `ZoneRole`
- `ConditioningType`
- `OccupancyCategory`
- `ExteriorExposure`
- `ProgramGroup`
- `SourceZoneId`

The ground-truth model should be treated as the source from which lower-LoD representations are derived.

---

## 4. Building Typologies

The first study phase focused on residential buildings. Since D-094 the study covers every program type of its precedent set (D-093): housing, retail, healthcare (operating suites), food service, office, elder care, and assembly or community uses. The typologies are the families `SYN-TYP-001` to `SYN-TYP-019` of [docs/research/precedents/syn-typologies.md](research/precedents/syn-typologies.md), except `SYN-TYP-013` (D-096). At the most detailed level a dwelling is one zone per storey (D-009, D-085) and a non-residential floor has one zone per department: a contiguous group of rooms of one program in one part of the floor (D-097, ADR-014). The residential typologies of §4.1–§4.4 were the starting set.

At minimum, the parametric plan generator should support several representative plan typologies.

### 4.1 Linear Block

Characteristics may include:

- double-loaded or single-loaded corridor,
- repeated dwelling units,
- long façade,
- directional exposure differences,
- high perimeter-to-core ratio.

### 4.2 Point Block / Tower

Characteristics may include:

- compact footprint,
- central circulation or service core,
- multiple orientations,
- repeated perimeter units,
- relatively high façade exposure.

### 4.3 Courtyard Block

Characteristics may include:

- exterior and courtyard-facing façades,
- internal circulation,
- complex solar exposure,
- increased perimeter length,
- potentially distinct internal and external unit orientations.

### 4.4 Optional Later Typologies

Later extensions may include:

- slab block,
- L-shaped block,
- U-shaped block,
- perimeter block,
- podium-and-tower,
- row housing,
- mixed residential/commercial floor plates.

The typology system should be extensible rather than hard-coded to only three cases.

---

## 5. Parametric Floor Plan Generation

Each floor plan generator should produce a **fully zoned semantic floor plan**, not only a footprint.

The generator should accept a compact parameter set and return:

1. building footprint geometry,
2. internal partitions,
3. dwelling unit boundaries,
4. circulation spaces,
5. stair/service cores,
6. semantic zone assignments,
7. floor-level metadata,
8. façade ownership,
9. window placement,
10. zone-level load metadata.

Example input parameters may include:

- overall width and depth,
- target gross floor area,
- corridor width,
- unit depth,
- target unit width,
- number of units,
- core dimensions,
- courtyard dimensions,
- orientation,
- façade setbacks,
- floor count,
- floor-to-floor height,
- window-to-wall ratio,
- window module width and height,
- unit-type distribution,
- plan asymmetry or perturbation parameters.

The output should be deterministic for a given parameter set and random seed.

---

## 6. Semantic Energy-Load Representation

The geometry generator must attach energy-related scalar and schedule metadata to the generated semantic spaces.

The Grasshopper-side representation does **not** need to define a complete EnergyPlus object model. Its role is to preserve, transform, aggregate, and export values required by downstream APIs.

Each source zone or space should support at least:

- floor area,
- volume,
- occupancy density,
- lighting power density,
- electric equipment power density,
- gas equipment density if used,
- infiltration parameter,
- ventilation parameter,
- heating setpoint schedule,
- cooling setpoint schedule,
- occupancy schedule,
- lighting schedule,
- equipment schedule,
- DHW schedule where relevant,
- semantic category.

Schedules should use a common normalized representation, preferably dimensionless fractions over a fixed timestep.

---

## 7. Equivalence Principle

Every geometric simplification must preserve the appropriate aggregate physical or operational quantity.

For a source set of spaces \(i = 1,\ldots,n\), with:

- area \(A_i\),
- power density \(p_i\),
- schedule \(s_i(t)\),

the instantaneous aggregate load is:

\[
P(t) = \sum_i A_i p_i s_i(t)
\]

For a merged target zone with total area

\[
A^\* = \sum_i A_i
\]

the equivalent representation must satisfy:

\[
A^\* p^\* s^\*(t) = \sum_i A_i p_i s_i(t)
\]

for the quantity being preserved.

Several equivalent decompositions are possible. The implementation should use a consistent rule.

One preferred formulation is:

\[
p^\* = \frac{\sum_i A_i p_i}{\sum_i A_i}
\]

and:

\[
s^\*(t) =
\frac{\sum_i A_i p_i s_i(t)}
{\sum_i A_i p_i}
\]

provided the denominator is non-zero.

This formulation preserves both:

- total installed load,
- instantaneous scheduled load.

The same principle should be applied separately to:

- lighting,
- plug/equipment loads,
- occupancy,
- DHW,
- ventilation,
- infiltration where appropriate,
- other internally scheduled gains.

For thermostat setpoints, a separate explicit aggregation rule is required because setpoints are controls rather than additive loads. Possible rules include:

- retain the dominant source-zone schedule,
- area-weighted temperature schedule,
- load-weighted schedule,
- prohibit merging zones with incompatible setpoints.

The chosen rule must be recorded in experiment metadata.

Rule adopted for this project (ADR-005, D-038): conditioning comes from the program preset, and an unconditioned zone has no setpoints. A simplified zone is conditioned if any source zone contributing floor area to it is conditioned ("any conditioned wins"). Its heating and cooling setpoint schedules are each aggregated hour by hour by floor-area weighting over the conditioned contributing sources \(C\) only,

\[
T^\*(t) = \frac{\sum_{i \in C} w_i T_i(t)}{\sum_{i \in C} w_i}, \qquad w_i = f_i A_i
\]

where \(w_i\) is the floor area of source zone \(i\) transferred to the target zone: its area fraction \(f_i\) times its floor area \(A_i\), which is the overlap area when a source zone is split between targets. There is no method parameter and no fallback; exposed-surface-area weighting was rejected because it would make the control assumption depend on geometry. This is a prescribed control rule, not a conservation invariant, so validation checks it against its definition rather than against a conserved total. Merging conditioned and unconditioned sources enlarges the conditioned floor area; validation reports this change without enforcing it, because it is a consequence of the zoning simplification under study. Each aggregated setpoint schedule records its source zones, the method, and the weights.

---

## 8. Zoning Levels of Detail

The study should support a sequence of zoning simplifications.

### Z0 — Detailed Semantic Zoning

Ground-truth zoning.

Examples:

- individual dwelling units,
- departments of non-residential floors, such as an office work area, a kitchen and servery, or a bank of operating theatres (D-097),
- corridors,
- stairwells,
- entrance spaces,
- service spaces.

### Z1 — Semantic Zone Merging

Merge zones according to known semantic relationships.

Examples:

- adjacent units of the same type,
- repeated corridor segments,
- repeated service spaces,
- same-orientation units.

The merged zones preserve equivalent schedules and installed loads.

### Z2 — Re-Zoning to Perimeter/Core

Discard detailed internal semantic partitions and create new thermal zones from the floor plate.

Example representation:

- north perimeter,
- east perimeter,
- south perimeter,
- west perimeter,
- core.

Other perimeter zoning schemes may be included.

Source-space properties must be spatially mapped into the new zones and aggregated using the equivalence rules.

### Z3 — One Zone per Floor

Represent the complete floor as a single thermal zone.

The resulting zone must preserve the aggregate internal gains and schedules of the source floor.

### Z4 — Vertically Repeated Floor Representation

Use a representative floor and simulate repeated floors using simplified vertical assumptions.

Possible variants:

- one representative floor simulated independently,
- selected bottom/middle/top floors,
- repeated identical geometry with separate zones.

### Z5 — EnergyPlus Floor Multiplier

Represent multiple geometrically similar floors using a single simulated floor with an EnergyPlus multiplier.

The experiment must clearly distinguish zoning simplification from the multiplier approximation.

---

## 9. Rezoning as Spatial Remapping

Rezoning must be treated as a mapping between:

- source semantic zones,
- target thermal zones.

A target zone may contain fractions of multiple source zones.

Define a transfer matrix:

\[
M_{ji}
\]

where \(M_{ji}\) is the area of source zone \(i\) assigned to target zone \(j\), or equivalently the fractional overlap.

For every extensive scalar quantity:

\[
Q_j = \sum_i f_{ji} Q_i
\]

where \(f_{ji}\) is the fraction of source quantity associated with the intersecting area.

For intensive quantities, use the appropriate weighting basis.

Examples:

- power density: area weighted,
- occupancy density: area weighted,
- installed equipment power: extensive,
- schedules: installed-load weighted where relevant,
- window area: façade-overlap weighted,
- infiltration: depends on whether represented by exterior area, floor area, or ACH.

The transfer matrix should be retained as part of the output metadata so every simplified model can be traced back to its source model.

Rule adopted for this project (ADR-007, D-019, D-041, D-047): loads are aggregated per component, one per load type and basis; a program may express a load type in several bases (e.g. ventilation per person plus per floor area), and its components add up. Every component is converted to its absolute design magnitude \(Q_i\) = value × basis quantity, where the basis quantity is the floor area, the design occupants (the sum of the zone's occupancy components), 1 for absolute loads, the gross exterior wall area (walls with an outdoor boundary, windows included), or the zone volume for air changes per hour. Source zone \(i\) transfers \(T_{ji} = f_{ji} Q_i\) to target zone \(j\), where \(f_{ji}\) is the exterior-wall fraction for loads per exterior wall area and the floor-area fraction otherwise; a source without the component contributes nothing to it. The target magnitude \(Q_j = \sum_i T_{ji}\) is re-expressed in the component's basis as \(v_j = Q_j / B_j\), and the target schedule is

\[
s_j(t) = \frac{\sum_i T_{ji} s_i(t)}{Q_j}
\]

This yields area weighting for densities, occupancy weighting for per-person loads, summation for absolute loads, exterior-wall-area weighting for loads per exterior wall area, and volume weighting for air changes per hour, \(ACH^\* = \sum_i V_i ACH_i / \sum_i V_i\) (D-019). Transfer fractions are normalised per source, \(\sum_j f_{ji} = 1\), so every extensive quantity is conserved to floating-point precision regardless of polygon rounding; how well the target zones cover each source is checked separately. Exterior-wall fractions are used only after the target façades are shown to cover every source outdoor wall over its full length, checked before any normalisation (D-041). Loads of one type with different bases are neither rejected nor converted to one basis: each basis is aggregated as its own component and conserved exactly, so no program assumption changes (D-047). A positive magnitude cannot be expressed in a target whose basis quantity is zero; this is an error. A zero total magnitude gives the value 0 and a constant-zero schedule.

---

## 10. Window Representation

Window representation is not a separate experimental axis. Models are built from the bottom up: the plan generator creates the most detailed model, windows included, and every later step only simplifies or aggregates, so windows follow the zoning and vertical levels (D-079, ADR-012).

Rule adopted for this project (D-026, D-039, D-079): walls carry explicit windows, each with a position along the wall, a sill height, a width, and a height (ADR-002). The first plan generator uses one simple deterministic rule: one window per outdoor wall, centred on it and sized from the window-to-wall ratio of the zone's program preset, \(A_\text{glazing} = \text{WWR} \times A_\text{wall}\) (D-026); the window is the wall rectangle scaled about its centre by \(\sqrt{A_\text{glazing} / A_\text{wall}}\). This is that generator's placement rule, not a property of windows. Every plan generator uses it (ADR-006), except that a wall shorter than 1 m, or a window narrower or lower than 0.3 m, gets no window, reported as the info `WindowOmitted` (ADR-011); the detailed model's glazing is then what the generator placed, and every later step conserves it.

Wherever zones are merged and walls are rebuilt (Z1–Z3, and the single-zone vertical methods), every outdoor wall of a target zone carries exactly one window, centred on the wall by the same rule, whose glazed area is the total glazed area of the source windows that wall covers:

\[
A_{\text{window,target wall}} =
\sum_{\text{source windows on the wall}} A_{\text{window,source}}
\]

A target wall without glazed area gets no window. Glazed area is therefore conserved per target wall, and so per façade, orientation, and building; individual window positions are not. Because every target façade covers every source façade over its full length (D-041), every source window lies on exactly one target wall and a target wall's glazed area is smaller than its area; both are checked and fail loudly if they ever do not hold, and windows are never capped or moved silently. Steps that do not rebuild walls (Z0, stacking, the floor multiplier) keep the windows of their input, which already follow the rule.

The window levels W1 to W5 planned earlier (equivalent window area by source zone, WWR by target zone, redistributed windows, orientation-level and building-level WWR) are dropped (D-079).

---

## 11. Vertical Geometry Levels

Vertical simplification should be represented separately from horizontal zoning.

Possible levels include:

### V0 — Floor-Specific Geometry

Each floor may have its own:

- footprint,
- zoning,
- window pattern,
- space program.

### V1 — Repeated Floor Geometry

All typical floors share one floor plan.

### V2 — Representative Bottom / Middle / Top Floors

Capture major vertical boundary-condition differences without modeling every floor.

### V3 — Representative Typical Floor

Use a single typical floor for the building.

### V4 — Floor Multiplier

Use EnergyPlus multipliers for repeated floors.

This separation allows the study to distinguish:

- horizontal zoning loss,
- façade/window loss,
- vertical geometry loss.

---

## 12. Experimental Factorization

The experiment should treat geometric choices as independent factors whenever practical.

Suggested dimensions:

- building typology,
- geometry realization,
- zoning LoD,
- vertical LoD,
- climate/weather file,
- orientation,
- internal-load scenario if later needed.

A model configuration may therefore be represented as:

`Typology × GeometrySeed × Z-Level × V-Level × Weather`

Windows are not a factor of their own (§10, D-079).

This enables systematic factorial or reduced-factorial experiments.

---

## 13. Weather Conditions

Each model should be simulated under multiple weather conditions.

At minimum, select climates that vary in:

- heating dominance,
- cooling dominance,
- diurnal temperature range,
- solar intensity,
- humidity,
- seasonal variation.

The same geometry and model assumptions must be retained across weather cases.

Weather variation is intended to determine whether geometric simplification error is:

- climate-independent,
- climate-sensitive,
- season-specific,
- primarily driven by solar gains,
- primarily driven by envelope conduction,
- primarily driven by internal-load aggregation.

---

## 14. Simulation Outputs

The downstream EnergyPlus workflow should collect at least:

### Building-Level Outputs

- annual electricity,
- annual heating energy,
- annual cooling energy,
- annual gas or fuel use,
- total site energy,
- peak electricity,
- peak heating load,
- peak cooling load,
- monthly energy.

### Time-Series Outputs

- hourly electricity,
- hourly heating,
- hourly cooling,
- zone air temperature,
- zone sensible load,
- solar gains,
- envelope heat transfer if practical.

### Comparison Metrics

- annual percentage error,
- monthly NMBE,
- monthly CVRMSE,
- hourly NMBE,
- hourly CVRMSE,
- RMSE,
- MAE,
- peak magnitude error,
- peak timing error,
- load-duration-curve error,
- seasonal error,
- heating/cooling-specific error.

The ground-truth representation is the reference for all error calculations.

---

## 15. Required Parametric Pipeline

The complete research pipeline should support:

1. generate a parametric detailed floor plan,
2. assign semantic zones,
3. assign semantic schedules and load densities,
4. generate explicit windows,
5. generate the detailed reference representation,
6. generate one or more simplified zoning representations,
7. construct source-to-target transfer maps,
8. calculate equivalent schedules and scalar inputs,
9. rebuild windows on merged walls (one centred window per wall, §10),
10. optionally simplify vertical geometry,
11. package the resulting model in a common intermediate schema,
12. pass the schema to an existing EnergyPlus/IDF generation API,
13. run multiple EnergyPlus simulations in parallel,
14. collect results,
15. calculate comparison metrics,
16. export experiment metadata and results.

---

## 16. Common Intermediate Representation

All generators and rezoning methods should emit the same intermediate model schema.

The schema should include:

### Building

- building ID,
- typology,
- number of floors,
- orientation,
- floor height,
- experiment metadata.

### Floor

- floor ID,
- elevation,
- floor geometry,
- source floor ID where applicable.

### Zone

- zone ID,
- geometry,
- area,
- volume,
- semantic metadata,
- source-zone references,
- exterior boundary references,
- load definitions,
- schedules.

### Surface

- surface ID,
- orientation,
- area,
- boundary condition,
- zone ownership.

### Window

- window ID,
- host surface,
- geometry or equivalent WWR,
- area,
- source-window references.

### Load Definition

- load type,
- density or absolute value,
- schedule ID,
- aggregation method.

### Schedule

- schedule ID,
- timestep,
- values,
- source schedules,
- aggregation weights.

### Transformation Metadata

- zoning LoD,
- vertical LoD,
- source model ID,
- mapping matrix,
- transformation parameters.

The intermediate representation should be serializable, preferably as JSON.

---

## 17. Validation and Invariants

Before any EnergyPlus simulation is allowed to run, each transformed model must pass equivalence checks.

Required checks should include:

### Geometry

- floor area conserved within tolerance,
- building volume conserved where applicable,
- target zones do not overlap,
- target zones cover the intended source floor area,
- exterior surfaces remain valid.

### Internal Loads

For each load type:

- total installed power conserved,
- timestep-level aggregate scheduled load conserved.

### Occupancy

- total design occupancy conserved,
- timestep-level occupancy conserved.

### Windows

- total window area conserved,
- window area per orientation conserved,
- target windows remain on exterior walls (by construction, §10).

### Traceability

Every target zone must reference one or more source zones.

Every transformed schedule must record:

- source schedules,
- aggregation method,
- weighting quantities.

Failed invariant checks should stop model export by default.

---

## 18. Reproducibility

Every generated case must have a complete configuration record containing:

- input parameters,
- random seed,
- typology,
- source model identifier,
- zoning level,
- vertical level,
- weather file,
- transformation rules,
- schedule aggregation rule,
- code version or commit,
- simulation metadata.

A model should be reproducible from this configuration without requiring manual Grasshopper editing.

---

## 19. Initial Undergraduate Scope

The first implementation milestone should prioritize the transformation framework rather than the complete research matrix.

### Phase 1

- common data schema,
- one residential typology,
- detailed semantic zoning,
- explicit windows,
- basic load/schedule assignment,
- source-to-target mapping,
- zone merging,
- equivalence validation.

### Phase 2

- perimeter/core rezoning,
- one-zone-per-floor transformation,
- equivalent schedule calculation,
- equivalent WWR calculation.

### Phase 3

- additional typologies, residential and non-residential (D-094),
- vertical simplification,
- EnergyPlus export connection,
- automated simulation dispatch.

### Phase 4

- weather matrix,
- batch simulation,
- result collection,
- error analysis.

The key deliverable of the undergraduate project is therefore an automated and extensible **geometry-to-equivalent-model transformation pipeline**, not only a collection of individual Grasshopper definitions.

---

## 20. Research Deliverables

Expected outputs include:

1. parametric plan generators for residential and non-residential typologies,
2. semantic zoning definitions,
3. automatic rezoning tools,
4. source-to-target mapping tools,
5. equivalent schedule and load calculators,
6. window rebuilding on merged walls,
7. common intermediate model representation,
8. validation and invariant checks,
9. automated export interface,
10. batch simulation configurations,
11. comparative simulation dataset,
12. analysis of error by zoning, vertical LoD, typology, and weather,
13. documented assumptions and reproducible examples.

---

## 21. Guiding Principle

The project should not compare arbitrary simplified models against a detailed model.

It should compare:

> **the same building program and energy assumptions represented through systematically different geometric abstractions.**

The scientific contribution depends on making those representations equivalent before attributing differences in simulation results to geometry, zoning, windows, or vertical simplification.
