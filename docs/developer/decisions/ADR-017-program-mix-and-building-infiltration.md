# ADR-017: Program mix and building-level infiltration

Status: Accepted (the owner's decisions of 2026-10-06; the realisation by the controller, provisional pending the owner's reading)

Date: 2026-10-06

Decisions: D-023, D-038, D-047, D-064, D-111, D-124; applies [ADR-005](ADR-005-conditioning-and-setpoints.md), [ADR-007](ADR-007-load-basis-aggregation.md), and [ADR-010](ADR-010-convert2idf.md); supersedes in part ADR-007 (the exterior-wall basis and fraction), ADR-010 (infiltration as a program load), and [ADR-014](ADR-014-program-types-and-department-zoning.md) (the example presets' infiltration values)

Design note: [2026-10-06-program-mix.md](../plans/2026-10-06-program-mix.md)

## Context

The owner wanted a Grasshopper operation that mixes one or a few program presets into a new preset, with one weight per input. Two problems came up.

1. **Loads in different unit bases.** A preset's loads are per floor area, per person, absolute, or in air changes per hour (ADR-007). A mix has to say how each combines, and it must not change a program assumption silently (GLOBAL.md scientific rule 3).
2. **Weights that depend on geometry a preset does not know.** The only such load was infiltration, expressed per exterior wall area or in air changes per hour. A preset has no walls, so a weight for its exterior wall area cannot exist. Infiltration is also the one program load whose magnitude follows the envelope: ASHRAE prototype models set it from building-level rules per exterior surface area, and the atlas reports program-level infiltration as unknown in every record.

The owner's answers (2026-10-06) fixed the semantics. A weight is a floor-area share ("think of the user's weight as area"). Absolute loads are not weighted. Exposure-dependent attributes leave the program and become a building-level input before export. Setpoints mix as zone merges mix them, with the user's weights in place of areas. The space type is optional. Provenance records the inputs as source and weight pairs.

## Options considered

### Where infiltration lives

- **(a) Everything moves (chosen, the owner's choice).** `LoadType.Infiltration` and `LoadBasis.PerExteriorWallArea` leave the program model; `ZoneProgram` has no infiltration. A new `Infiltration` record (design rate, basis, fraction schedule) sits on `EnvelopePreset`, the building-level input both converters already take. Every zone gets its infiltration at conversion from its own surfaces or volume.
- **(b) The envelope-dependent part only.** The per-exterior-wall basis would leave the program, and air changes per hour, which depend on the volume only, would stay a program load. Two places would then hold one physical quantity, a mix would have to weigh the air-change infiltration of its inputs, and the per-type rates (a mall's entrance doors, a pressurised operating suite) would stay program properties although the atlas does not report them. Not chosen.
- **(c) Keep infiltration a program load.** A mix would have no weight for the per-exterior-wall basis, which is the problem as stated. Not chosen.

Decision: (a). The aggregator loses its exterior-wall path: `ZoneMeasures` has floor area and volume only, and `SourceZoneContribution` has one fraction, the area fraction. Façade coverage and window attribution keep their own uses (ADR-013, ADR-012).

### The mix rule

- **The zone merge on a virtual unit-area zone (chosen).** The mix is the existing `EquivalentPropertyAggregator` (ADR-005, ADR-007, D-047) applied to one virtual zone of floor area 1 and volume 1 whose sources are the inputs: input *i* is a source of floor area and volume ŵᵢ, its normalised weight (one common height), transferred whole (area fraction 1). Every basis then follows the rule zone merges already use, and the two operations agree by construction.
- **Per-attribute weights.** Each attribute (a density, a per-person value, a schedule, a setpoint) would get its own weighting rule. Each rule would need its own proof of conservation, and the mix would no longer agree with a zone merge of the same shares. Not chosen.

The rule per component, with *v* a load value, *s*(*t*) its schedule, *B* the basis quantity, and *o* the occupants per m² of an input:

| Component | Mixed value | Mixed fraction schedule |
| --- | --- | --- |
| Per floor area | Σ ŵᵢ·vᵢ; a preset without the component contributes 0 | Σ ŵᵢ·vᵢ·sᵢ(t) / Σ ŵᵢ·vᵢ |
| Air changes per hour | Σ ŵᵢ·vᵢ | the same form |
| Per person | Σ ŵᵢ·oᵢ·vᵢ / Σ ŵᵢ·oᵢ | Σ ŵᵢ·oᵢ·vᵢ·sᵢ(t) / Σ ŵᵢ·oᵢ·vᵢ |
| Absolute | Σ vᵢ, raw | Σ vᵢ·sᵢ(t) / Σ vᵢ |
| Conditioning | conditioned when any input is | — |
| Setpoints | over the conditioned inputs only: Σ ŵᵢ·θᵢ(t) / Σ ŵᵢ, renormalised over them | — |

Each component keeps its basis; different bases of one load type stay side by side and add up at export (D-047). A merged magnitude of zero gives value 0, a constant-zero schedule, and the info `ZeroLoadSchedule`, as in zone merges.

### Absolute loads: summed raw (the owner)

A fixed value, such as a fixture's flow in m³/h, is "just there": it is added at its raw value whatever the weights. In the virtual zone this is exact, because each input transfers its whole absolute magnitude into the one zone (area fraction 1). The alternative, scaling an absolute value by its share, would make a fixture shrink when its input gets a small share of the floor area.

Two consequences follow, and both are intended. A mix of one preset equals that preset. A mix of a preset with itself doubles its absolute loads. A weight must be greater than 0 (`MixWeight`): a preset without a share does not belong in the mix, and its absolutes would otherwise be added silently.

### Setpoints: zone merges, weights as areas (the owner)

A mixed setpoint is the zone merge's rule (ADR-005, D-038): conditioned when any input is conditioned, and each of the heating and cooling setpoints is the weighted mean Σ ŵᵢ·θᵢ(t) / Σ ŵᵢ over the conditioned inputs only, with the normalised weights as the areas. Unconditioned inputs still contribute their loads and never weigh a setpoint. The result is a prescribed control rule, not a conservation invariant.

Mixing conditioned with unconditioned inputs is allowed, as in zone merges; the info `MixedConditioning` names the unconditioned inputs and the share that becomes conditioned.

Chained mixes carry the caveat that chained zone merges carry: the weights an inner mix renormalises over its conditioned inputs are lost to the outer mix. A mix of (A conditioned 0.5, B unconditioned 0.5) with C conditioned, weights 0.5 and 0.5, gives the setpoint 0.5·A + 0.5·C, whereas the three-input mix with weights 0.25, 0.25, and 0.5 gives A/3 + 2·C/3. The owner accepted this as intentional. A mix of several presets should be made in one step.

### The space type default (the owner)

*Space Type* is optional. When it is missing, the result takes the space type of the input with the largest weight, the first such input in list order on a tie (weights compared exactly). An any-program input (no space type, D-108) chosen this way makes an any-program mix. The provenance records the choice and how it was made.

### The window-to-wall ratio: the weighted mean (the owner)

When *WWR* is missing, the result takes Σ ŵᵢ·WWRᵢ, read as glazing per wall shared like floor area. It is recorded as a derived value. A given WWR is kept and checked to lie in [0, 1). The weighted mean is an approximation of the glazing per wall of the merged zone, not an invariant; the glazed area of a building is conserved by the plan simplifiers from the plan's windows, not from a preset.

### A per-person load with absolute occupancy: the any-input rule

The first realisation rejected a per-person load beside absolute occupancy only when both were in one input. A review found this wrong. A mixed per-person value is weighted by the occupants per m² of every input, so absolute occupancy in any input enters that weighting. A mix has no zone area, so the virtual zone fixes it at 1 m², and an absolute occupancy dilutes another input's per-person load as if that input's area were 1 m² too.

Example: a hall of 5 people (absolute occupancy, no per-person load) mixed half and half with an office of 0.1 people/m² and ventilation of 30 m³/h per person. The mix has 5 + 0.05 occupants at unit area, so its per-person ventilation is 1.5 / 5.05 = 0.297 m³/h per person, and on a zone of 100 m², with 5 + 5 = 10 people, 2.97 m³/h. Merging zones of 50 m² (hall) and 50 m² (office) gives 5 office people times 30 = 150 m³/h. The mix was wrong by about 50 times.

Options:

1. **Allow it.** The result above is wrong by orders of magnitude and depends on an area the mix cannot know. Rejected.
2. **Reject it within one input only** (the first realisation). It misses the case above, where the absolute occupancy and the per-person load are in different inputs. Rejected.
3. **Reject it whichever inputs hold the two (chosen).** `PerPersonWithAbsoluteOccupancy` names the inputs of each kind and says to express the occupancy per floor area. Per-area occupancy is fine, and so is absolute occupancy when no input has a per-person load: then the absolutes add up raw, as every absolute load does.

## Decision

- Infiltration is not a program property. `Lod.Core.Envelope.Infiltration(DesignRate, Basis, Schedule)` is carried by `EnvelopePreset` (and `EnvelopeValues`); its basis is `PerExteriorSurfaceArea` (m³/h per m² of outdoor walls, roofs, and exposed floors, EnergyPlus `Flow/ExteriorArea`), `PerExteriorWallArea` (`Flow/ExteriorWallArea`), or `AirChangesPerHour` (`AirChanges/Hour`). `ExampleEnvelopePresets` holds 0.3 air changes per hour, always on, the value most example presets carried; it is illustrative like the rest of the example envelope (D-023).
- `LoadDefinition.Create` rejects a load type or basis that is not defined (`UndefinedLoadKind`), so the removed infiltration type and the per-exterior-wall basis cannot come back through a cast. The message tells the user to set infiltration on the envelope preset.
- *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` per zone in EnergyPlus's own method for the basis, so EnergyPlus multiplies the rate by each zone's own exterior area or volume. *Convert2BEM* outputs the building's infiltration once and each zone's design flow in m³/h, from `Lod.Core.Conversion.ZoneInfiltration`, which uses the quantities EnergyPlus uses.
- No zone merge aggregates infiltration. It follows each target zone's own surfaces, so it is conserved wherever the checked exterior areas and volumes are. The infiltration invariants of load conservation are removed ([validation.md](../architecture/validation.md)).
- `ProgramMix.Mix` in `Lod.Core.Programs` implements the rule above; *Mix Programs* (panel *1 Program*, GUID `744378f8-861d-4e6d-bff4-68c7fe2b62c1`) is a thin adaptor over it. Weights are floor-area shares, finite and greater than 0, one per preset, normalised to sum to 1.
- The mix records its provenance as a `ProgramPreset.Source`: the operation `MixPrograms`, one `Input.k` parameter per input holding its name, given weight, and normalised weight (the owner's source and weight pairs), the chosen space type and WWR with how each was chosen, and each input's own `Source` as an input, so a mix of atlas presets traces to their records and a mix of mixes nests. Every mixed load and schedule gets an `AggregationRecord` whose sources are the keys `Input.k`, not the preset names, which may repeat. A plan records the distinct sources of its presets among its provenance inputs.

## Worked example

A: lighting 10 W/m², occupancy 0.1 people/m², ventilation 30 m³/h per person, hot water 0.5 m³/h absolute. B: lighting 4 W/m², occupancy 0.02 people/m², ventilation 10 m³/h per person, hot water 0.2 m³/h absolute. Weights 7 and 3 (ŵ = 0.7 and 0.3):

| Component | Mixed value |
| --- | --- |
| Lighting, per floor area | 0.7·10 + 0.3·4 = 8.2 W/m² |
| Occupancy, per floor area | 0.07 + 0.006 = 0.076 people/m² |
| Ventilation, per person | (0.07·30 + 0.006·10) / 0.076 = 28.42 m³/h per person |
| Hot water, absolute | 0.5 + 0.2 = 0.7 m³/h, raw |

A plan of two zones of 70 m² (A) and 30 m² (B) merged by *Single Zone per Floor* gives the same four values (lighting (70·10 + 30·4) / 100 = 8.2 W/m², and so on), the same schedules at every hour, and the same setpoints at every hour. `ProgramMixEquivalenceTests` checks this for every component, schedule, and setpoint.

## Consequences

- **Per-type infiltration differences are lost.** The example presets carried 0.8 air changes per hour for the mall, 0.6 for the lobby, 0.5 for retail, 0.1 for the operating theatre, and 0.3 for every other type; the first three stood for entrance doors and the last for a pressurised suite. A building now has one infiltration input, with one rate and one schedule for every zone. The values were illustrative (D-023), and [program presets](../research/program-presets.md) records them as dropped.
- **Snapshots changed**, each explained in its commit. The 18 canonical plan snapshots of `Lod.Generators.Tests` and 7 snapshots of `Lod.Integration.Tests` lose their infiltration load lines and nothing else. Of the 5 IDF snapshots, all gain the header line `Infiltration:`; four also change in the schedule objects, because the infiltration of every zone now uses the envelope's schedule, written once under its own name (`Example Always On`), instead of one schedule per zone named after the zone. The infiltration objects keep their names and values.
- **Old definitions open with a Grasshopper IO dialog.** The default preset components lost their *Infiltration* and *Infiltration Schedule* inputs, *Envelope Preset* gained three inputs, and *Convert2BEM* four outputs; A definition saved before D-124 opens only after Grasshopper's *Grasshopper IO* message about the preset components' removed inputs, which also blocks a headless run. The 19 example definitions were rebuilt with the new components (`BEMGEN_EXAMPLES_WRITE=1`) and reopen without it. No component GUID changed (D-064). On opening, the dialog drops the preset components' saved infiltration values and any wires into those inputs, without a further message. A preset that had 0.8 ACH then gets the envelope's rate, 0.3 ACH unless the envelope is changed. Release notes must say so.
- **The S10 atlas branch's infiltration handling becomes obsolete when both merge.** Its converter treats `infiltration_m3_s_m2` as a program load and warns `InfiltrationNotFromAtlas`. After this change the field is "not converted: infiltration is a building-level input", and the warning and the local infiltration load go away. `ProgramPreset.Source` is declared on both branches the same way; the branch that merges second resolves the duplicate. The Conditioned Merge branch (D-123) is expected to conflict at most in the aggregator's exterior-wall path and in the integration test lists.
- **Zone merges no longer aggregate infiltration.** `SourceZoneContribution.ExteriorWallFraction`, `FacadeAttribution.ExteriorWallFraction`, `LayoutMeasures.ExteriorWallArea`, and the second argument of `LayoutMeasures.Of` are removed. A target zone's infiltration comes from its own surfaces at conversion, so it is conserved by construction wherever the exterior wall, ground, roof, and exposed floor areas and the volume are, which validation already enforces.
- **A mix equals a zone merge on matching area shares.** A plan whose zones have floor areas in the ratio of the weights, merged into one zone by *Single Zone per Floor*, has the mix's densities, per-person values (with per-area occupancy), air changes, schedules, and setpoints. Three differences remain. Air changes are volume weighted in a merge and area weighted in a mix, which agree because the mix has one common height. Absolute loads agree only when each input stands for one source zone transferred whole: a preset used by *k* zones of a plan has its absolute value added *k* times by a merge and once by a mix, and a source zone split between targets transfers only its fraction of an absolute value. Absolute occupancy beside a per-person load has no equivalent, which is why a mix rejects it.
- **Provisional.** The owner's decisions are final; the realisation (the rule table, the any-input rule, the `Input.k` keys) stands until the owner has read it.
