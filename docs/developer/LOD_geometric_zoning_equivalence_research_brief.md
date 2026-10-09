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
- infiltration (in this project a building-level envelope input applied to each zone's own surfaces or volume, not a zone parameter; see §7 and §9),
- ventilation parameter,
- heating setpoint schedule,
- cooling setpoint schedule,
- occupancy schedule,
- lighting schedule,
- equipment schedule,
- DHW schedule where relevant,
- semantic category,
- since D-126, also: the number of dwellings (for loads per dwelling unit), the end use of each load, the heat fractions of lighting and equipment, the activity level and heat fractions of the occupants, the target and inlet temperatures of hot water, heating and cooling as separate controls, and the calendar of the schedules (see §7).

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
- other internally scheduled gains.

Infiltration is not in this list in this project (D-124, [ADR-017](decisions/ADR-017-program-mix-and-building-infiltration.md)). Its magnitude depends on the envelope, which a program does not know, so it is an input of the envelope preset, applied by the converters to each target zone's own exterior surface area, exterior wall area, or volume, according to its basis. It is therefore not aggregated or transferred between zones: every zone gets the building's rate times its own exterior quantity. Those quantities (exterior wall area, roof and exposed floor area, volume) are conserved by the zoning (§17), so the building's infiltration is conserved by construction, and it has no separate check.

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

### Extended program properties (D-126)

The atlas's program JSON 2.0.0 describes more than power densities, schedules, and setpoints, and a program that ignored the rest would change program assumptions silently (GLOBAL.md scientific rule 3). BEMGen's program therefore holds the properties below ([ADR-018](decisions/ADR-018-program-json-and-extended-programs.md)), each with an explicit aggregation rule so that the invariants of §17 still hold. The notation is that of §9: source \(i\) transfers the fraction \(f_i\) of its floor area \(A_i\); for a load component (a load type with an end use in a basis) \(T_i = f_i Q_i\) is the transferred design magnitude, \(Q^\* = \sum_i T_i\), and \(s^\*(t) = \sum_i T_i s_i(t) / Q^\*\) as before. A component is identified by its **type, end use, and basis**: components with different end uses (lighting and additional lighting) are never merged with each other, and the conservation of §17 holds for each separately.

**Loads per dwelling unit.** The basis quantity of a zone is its dwelling count \(N\): 1 for a generated zone of space type `DwellingUnit` (a dwelling is one zone and is never subdivided, D-009), 0 for any other generated zone, and \(N^\* = \sum_i f_i N_i\) for a target zone, fractional when a source is split. A per-dwelling load of value \(v\) has the design magnitude \(Q = N v\), and the general rule \(v^\* = Q^\*/B^\*\) with \(B^\* = N^\*\) gives

\[
v^\* = \frac{\sum_i f_i N_i v_i}{\sum_i f_i N_i}, \qquad
s^\*(t) = \frac{\sum_i f_i N_i v_i s_i(t)}{\sum_i f_i N_i v_i}.
\]

Weighting by floor area instead would not conserve installed power when the merged dwellings differ in size: dwellings of 80 m² and 40 m² at 100 and 400 W/dwelling hold 500 W, and the area-weighted 200 W/dwelling on two dwellings gives 400 W; the dwelling-count rule gives 250 W/dwelling and 500 W. The owner chose the dwelling-count weighting for that reason. A zone with a per-dwelling load and no dwellings (\(N = 0\)) has no magnitude and is an error. The building's dwelling count \(\sum_z m_z N_z\) (multipliers \(m_z\)) is a conserved total (§17). In a mix of presets (*Mix Programs*) the virtual zone has no dwellings of its own, so each input's weight stands for its share of dwellings as it stands for its share of floor area: \(v^\* = \sum_i \hat w_i v_i\).

**Heat fractions.** A lighting, electric equipment, or gas equipment component carries the fractions \(\varphi^k\) of its heat that are radiant, latent, lost, visible, and return air (\(k\)), each in \([0, 1]\), with the convective fraction \(1 - \sum_k \varphi^k \ge 0\). A merge weights each fraction by the transferred magnitude,

\[
\varphi^{k\*} = \frac{\sum_i T_i \varphi_i^k}{Q^\*}, \qquad\text{so}\qquad Q^\* \varphi^{k\*} = \sum_i T_i \varphi_i^k,
\]

and the installed power that goes to each heat path is conserved; the sum stays at most 1 because a weighted mean of values summing to at most 1 does. When \(Q^\* = 0\) the weights are the transferred floor areas \(f_i A_i\). The EnergyPlus `Lights` object has no latent or lost fraction, and `ElectricEquipment` and `GasEquipment` no visible or return-air fraction, so a non-zero value in such a field is an error and is never dropped (GLOBAL.md scientific rule 3).

**People.** Let \(o_i(t)\) be the transferred scheduled occupants of source \(i\) (its occupancy components times their schedules) and \(a_i(t)\) its activity level in W per person. The merged activity level

\[
a^\*(t) = \frac{\sum_i o_i(t)\, a_i(t)}{\sum_i o_i(t)}
\]

conserves the heat the occupants give off, \(\sum_i o_i(t) a_i(t) = o^\*(t) a^\*(t)\), in every hour. An hour without occupants takes the weights \(D_i\), the transferred design occupants, and a merge with no occupants at all takes \(f_i A_i\). The radiant fraction of the sensible heat is the mean weighted by \(D_i\) (by \(f_i A_i\) without occupants). The sensible heat fraction is a number in \([0, 1]\) or `autocalculate` (EnergyPlus computes it): when every weighted source is `autocalculate` the merge is; when every one is a number it is the \(D_i\)-weighted mean; when they mix, the merge is `autocalculate` with the warning `MixedSensibleFraction`, since a fraction that EnergyPlus computes has no number to average with (the owner's rule). A mean of equal values is that value exactly.

**Hot-water temperatures.** A hot-water component carries a target and an inlet (cold-water) temperature schedule, \(\vartheta_{\mathrm{t},i}(t)\) and \(\vartheta_{\mathrm{in},i}(t)\), the target never below the inlet. With the transferred scheduled flow \(q_i(t) = T_i s_i(t)\) as the weight, both are weighted by the same weights,

\[
\vartheta^\*(t) = \frac{\sum_i q_i(t)\, \vartheta_i(t)}{\sum_i q_i(t)},
\]

so the water heat \(\sum_i q_i(t)\,(\vartheta_{\mathrm{t},i} - \vartheta_{\mathrm{in},i})\) is conserved in every hour, and the merged target is not below the merged inlet. An hour without flow takes \(T_i\), and a component with no flow at all takes \(f_i A_i\). The IDF gives the water temperatures to `WaterUse:Equipment` and adds no heat to a zone from water; the heat above is the quantity the temperatures stand for.

**Heating and cooling separately.** A zone's thermostat has an optional heating and an optional cooling setpoint schedule, at least one. A merged zone is heated when any contributing source heats, and its heating setpoint is the floor-area-weighted mean of the setpoints of those sources only, as in the rule above; cooling is the same over the sources that cool. A merge whose heating setpoint exceeds its cooling setpoint in any hour is an error that names the sources, because EnergyPlus rejects a dual setpoint with heating above cooling. Setpoints stay a prescribed control rule, not a conservation invariant.

**Calendar.** Every schedule has 8760 values on a non-leap year. A program records the calendar (year and holidays) its schedules were expanded on, or none for BEMGen's own presets, which assume a year whose 1 January is a Monday. Sources of a merge, inputs of a mix, and zones of a building must share one calendar, and a program without one agrees only with a calendar that starts on a Monday; otherwise the combination is an error (`CalendarMismatch`), because the same hourly index would mean different days. The calendar passes through the merge unchanged.

**Left out.** Shared services of the contract (equipment serving several zones) are not modelled, and the design-day profiles of a schedule are not used; both are reported when a program JSON is imported.

### Mixing program presets (D-124)

Programs are also combined without any geometry, to give the program of a space made of several programs by floor-area share (*Mix Programs*, [ADR-017](decisions/ADR-017-program-mix-and-building-infiltration.md)). Take inputs \(i = 1,\ldots,m\) with weights \(w_i > 0\), normalised to \(\hat w_i = w_i / \sum_k w_k\); for each component (a load type in a basis) its value \(v_i\) and schedule \(s_i(t)\), a missing component being \(v_i = 0\); the design occupants per m² of floor area \(o_i\), the summed occupancy components; and the heating and cooling setpoints \(\theta_i(t)\) of the set \(C\) of conditioned inputs.

The mix is the merge rule above and of §9 applied to one virtual zone of floor area 1 and volume 1 whose sources are the inputs, input \(i\) a source of floor area and volume \(\hat w_i\) (one common height) transferred whole. Each input transfers

\[
T_i = \hat w_i v_i \ \text{(per floor area, air changes per hour)}, \qquad
T_i = \hat w_i o_i v_i \ \text{(per person)}, \qquad
T_i = v_i \ \text{(absolute)},
\]

and the mixed component is \(v^\* = \sum_i T_i / B^\*\) and \(s^\*(t) = \sum_i T_i s_i(t) / \sum_i T_i\), with \(B^\* = 1\), or for per-person loads the mixed occupants per m², \(\sum_i \hat w_i o_i\). A zero \(\sum_i T_i\) gives the value 0 and a constant-zero schedule. Absolute values are summed raw and not weighted: a fixed value is "just there" whatever the shares. Conditioning and setpoints follow the rule above with the weights as floor areas: the mix is conditioned when \(C\) is not empty, and

\[
\theta^\*(t) = \frac{\sum_{i \in C} \hat w_i \theta_i(t)}{\sum_{i \in C} \hat w_i}.
\]

By construction, for every component and hour the scheduled magnitude of the mix per m² of floor area, \(B^\* v^\* s^\*(t)\), is \(\sum_i T_i s_i(t)\), the inputs' scheduled magnitudes each scaled by its share (absolute magnitudes not scaled).

**Equivalence with a zone merge.** Let one source zone stand for each input, with floor areas \(A_i = \hat w_i A\) for any \(A > 0\) and one common height, merged whole into one target zone of area \(A\). The merge rule gives exactly the mixed values \(v^\*\), schedules \(s^\*(t)\), conditioning, and setpoints \(\theta^\*(t)\), whatever \(A\) is: area-weighted densities, volume-weighted air changes, occupant-weighted per-person values, raw sums of absolute loads, and floor-area-weighted setpoints over the conditioned inputs. So a mix of weights \(w_i\) is the merge of zones whose floor areas are in the ratio of the weights; `ProgramMixEquivalenceTests` compares the two for zones of 70 m² and 30 m² against weights 0.7 and 0.3, component by component, with every schedule and setpoint at every hour. Two things bound the statement:

- The merge adds an absolute value once per source zone, so a preset that stands for \(k\) zones of a plan adds it \(k\) times, and a source zone split between targets transfers only its fraction of it; a mix has one input per preset and no split.
- Absolute occupancy beside a per-person load has no such equivalent. The merge's per-person value then depends on the area \(A\) (the absolute occupants do not scale with it, the others do), and a mix has no area, so at unit area an absolute occupancy would dilute the other inputs' per-person load by a factor that no real zone has; for example a hall of 5 people mixed half and half with an office of 0.1 people/m² at 30 m³/h per person would give 2.97 m³/h on a zone of 100 m², and merged zones of 50 m² and 50 m² give 150 m³/h. The mix rejects this combination (`PerPersonWithAbsoluteOccupancy`) in any inputs. The same reasoning applies to occupancy in any two bases (per m², per dwelling, absolute), because the virtual zone has unit floor area and one dwelling: with such occupancy a per-person load, or people properties that differ between the inputs with occupants, would be weighted by a split that no real zone has, and the mix rejects it (`MixedOccupancyBases`, D-126).

The setpoint rule is a prescribed control rule, not a conservation invariant, and chaining mixes renormalises over the conditioned inputs step by step, so a mix of mixes can differ from the same inputs mixed once; this is accepted. The window-to-wall ratio of a mix, when not given, is the weighted mean \(\sum_i \hat w_i \mathrm{WWR}_i\), glazing per wall shared like floor area, recorded as derived.

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

Variant, joined pieces (D-123). The zones of one class often form several pieces that share no wall: the stairs of a floor are usually several separate cores, and the stair bays of a bar cut its dwellings into blocks. By default each connected piece is its own target zone; zones are connected when they share a wall, and zones that touch only at a point are not. With joined pieces, all pieces of a class on the floor form one target zone, a zone of several disjoint pieces at one elevation. The aggregation rules (§7) apply unchanged to the larger group, every invariant of §17 holds, and joining removes no partition, because the pieces share none. What the variant adds is the modelling assumption that the separate pieces are one thermal zone, with one air volume and one set of setpoints. It is a switch of the merge, not a new level, so a study can vary it on its own.

### Z1c — Conditioning merge

Merge by a known semantic relationship other than space type: conditioning. A source zone is conditioned when its program has a thermostat (D-038), and by nothing else: not its space type, its name, or the values of its setpoints. The conditioned zones that share walls form one target zone, and so do the unconditioned ones; a conditioned and an unconditioned source zone are never merged. With joined pieces, a floor has at most one conditioned and one unconditioned zone, each made of all the pieces of its class, and a floor without unconditioned zones has one conditioned zone. In both modes:

- Schedules, installed loads, and occupancy are conserved per target zone by the rules of §7. Infiltration is not merged: it is the envelope's and is applied to each target zone's own outdoor surfaces or volume, over all its pieces (D-124, §7, §9).
- The conditioned floor area is conserved exactly. Every target zone covers source zones of one class only, so no unconditioned area becomes conditioned and no conditioned area is lost. Validation reports the conditioned floor area as a note (§7, D-038) and for Z1c it never differs.
- A conditioned target zone's setpoints are the floor-area weighted schedules of §7 over its sources, all of which are conditioned. An unconditioned target zone has no thermostat and keeps its loads.
- A target zone takes the space type its sources share, or `Mixed` when they differ.

Z1c separates two effects that Z2 and Z3 confound. Those levels make a zone conditioned whenever any source in it is, so where they cover an unconditioned source, such as the stairs, they enlarge the conditioned floor area, and their difference from Z0 mixes the removal of internal partitions with the conditioning of that space. Z1c removes the partitions inside conditioned space and keeps the boundary between conditioned and unconditioned space, in either mode. Comparing it with Z0 or Z1 therefore shows the effect of the internal partitions alone, and comparing it with Z3 shows the effect of conditioning the unconditioned space and removing its boundary with the conditioned space.

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

### What the zoning levels do to the conditioned floor area

Every zoning level Z0 to Z3, in every variant, conserves the quantities of §17. They differ in how they treat one quantity, the conditioned floor area, which §7 defines through the thermostat of the program (D-038) and validation reports without enforcing.

| Level | Conditioned floor area |
| --- | --- |
| Z0 | the source's |
| Z1, separate or joined pieces | the source's when the zones of each space type share their conditioning; a group of zones that differ in conditioning is conditioned as a whole, which enlarges it |
| Z1c, separate or joined pieces | exactly the source's |
| Z2 | enlarged, wherever a perimeter or core zone covers both conditioned and unconditioned source zones, by the unconditioned area in it |
| Z3 | enlarged by all the unconditioned area of the floor when any source on the floor is conditioned |

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
- infiltration: not transferred (D-124); it is an envelope input applied to each target zone's own exterior area or volume.

The transfer matrix should be retained as part of the output metadata so every simplified model can be traced back to its source model.

Rule adopted for this project (ADR-007, D-019, D-041, D-047): loads are aggregated per component, one per load type, end use, and basis (D-126; D-047 said type and basis); a program may express a load type in several bases (e.g. ventilation per person plus per floor area) and several end uses (lighting and additional lighting), and its components add up. Every component is converted to its absolute design magnitude \(Q_i\) = value × basis quantity, where the basis quantity is the floor area, the design occupants (the sum of the zone's occupancy components), 1 for absolute loads, the zone volume for air changes per hour (D-124: no basis depends on the envelope), or the zone's dwelling count for loads per dwelling unit (D-126). Source zone \(i\) transfers \(T_{ji} = f_{ji} Q_i\) to target zone \(j\), where \(f_{ji}\) is the floor-area fraction; a source without the component contributes nothing to it. The target magnitude \(Q_j = \sum_i T_{ji}\) is re-expressed in the component's basis as \(v_j = Q_j / B_j\), and the target schedule is

\[
s_j(t) = \frac{\sum_i T_{ji} s_i(t)}{Q_j}
\]

This yields area weighting for densities, occupancy weighting for per-person loads, summation for absolute loads, and volume weighting for air changes per hour, \(ACH^\* = \sum_i V_i ACH_i / \sum_i V_i\) (D-019), and dwelling-count weighting for loads per dwelling unit, \(v^\* = \sum_i f_i N_i v_i / \sum_i f_i N_i\) (D-126; the other properties that came with it are in §7). Transfer fractions are normalised per source, \(\sum_j f_{ji} = 1\), so every extensive quantity is conserved to floating-point precision regardless of polygon rounding; how well the target zones cover each source is checked separately. Through S8 a second, exterior-wall fraction transferred loads per exterior wall area, and was used only after the target façades were shown to cover every source outdoor wall over its full length, checked before any normalisation (D-041); it left with infiltration (D-124), and the façade coverage is still checked for the rebuilt walls and windows (§10). Loads of one type with different bases are neither rejected nor converted to one basis: each basis is aggregated as its own component and conserved exactly, so no program assumption changes (D-047). A positive magnitude cannot be expressed in a target whose basis quantity is zero; this is an error. A zero total magnitude gives the value 0 and a constant-zero schedule.

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
- end use (D-126),
- basis,
- density or absolute value,
- heat fractions (lighting and equipment) or water temperatures (hot water), D-126,
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

Since D-126 the check runs for each load component (type, end use, and basis), per-dwelling components included, and the building's dwelling count is a conserved total. That the installed power of each heat path (radiant, latent, lost, visible, return air), the heat the occupants give off (occupants × activity), and the water heat (flow × (target − inlet)) are conserved in every timestep follows from the aggregation rules of §7 and is proven by the aggregation's invariant tests; it is not an enforced validation check. Validation also requires that a per-dwelling load is only in a zone with dwellings and that every zone shares one calendar.

The load types are those of a zone program. Infiltration is not one (D-124): it is the envelope's and is applied to each zone's own surfaces or volume, so it has no check of its own and is conserved by construction through the conserved exterior wall, roof, exposed floor, and volume.

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
