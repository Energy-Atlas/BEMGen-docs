# Mixed program presets, and infiltration as a building-level input (design note)

> **Status:** Done (D-124; released in version 1.1.0 with Conditioned Merge, D-125) · **Date:** 2026-10-06 · **Decisions:** D-023, D-038, D-047, D-064, D-111, D-124 · **Branch:** `feature/program-mix`

This is a revision stage run as D-111 sets out: one test-first build on the branch in the worktree `D:\worktrees\program-mix`, a review by a second agent, the headless Rhino check once, and `scripts/verify.ps1` before the merge. It is a breaking change of the program model (D-064), so it gets an ADR (ADR-017) and one decision-log entry, D-124. The branch starts from `main` (`af9ac65`). The S10 branch (D-122, atlas) and the Conditioned Merge branch (D-123) are unmerged. The section "Interaction with the unmerged branches" says what each needs once this lands.

## Problem

The owner wants a Grasshopper operation that mixes one or a few program presets into a new preset, using a weight per input. Two questions came up:

1. **Loads in different unit bases.** How do they mix?
2. **Loads whose weight depends on geometry a preset does not know,** such as exposed surface area. Today that is infiltration per exterior wall area. What happens to them?

The owner's answers, 2026-10-06:

- **A weight is a floor-area share.** "Think of the user's weight as area."
- **Absolute loads are not weighted.** Fixed values, such as a fixture's flow in m³/h, are added as their raw values whatever the weights. They are "just there".
- **Exposure-dependent attributes leave the program** and become a building-level input before export to IDF or BEM.
- **Setpoints mix as zone merges mix them,** with the user's weights in place of areas.
- **The space type is an optional input.** When it is missing, the result takes the space type of the input with the largest weight.
- **Provenance records the inputs as source–weight pairs.**
- **The setpoint caveat of chained merges is accepted** (intentional).

## Part A: infiltration leaves the program

Infiltration is the only program load whose magnitude depends on the envelope. Today it is `LoadType.Infiltration`, given in air changes per hour by every example preset, and possibly per exterior wall area (`LoadBasis.PerExteriorWallArea`, which only infiltration uses). The atlas reports program-level infiltration as unknown in every record. ASHRAE prototype models set infiltration from building-level rules per exterior surface area.

1. **Program model (the owner chose option (a), everything moves).** `LoadType.Infiltration` and `LoadBasis.PerExteriorWallArea` leave program loads, and `ZoneProgram` has no infiltration (D-064).
   - **Aggregation:** the aggregator loses its exterior-wall-fraction path. `SourceZoneContribution.ExteriorWallFraction` and `FacadeAttribution`'s role in program aggregation are removed. Façade coverage and window attribution keep their own uses.
   - **Example presets:** they lose their infiltration loads.
   - **What is lost:** the per-space-type differences they carried. Mall 0.8, lobby 0.6, and retail 0.5 ACH came from entrance doors; the operating theatre's 0.1 came from a pressurised suite. These are illustrative values, and a building now has one infiltration input. The research documentation records this.
2. **Building-level infiltration.** A new `Infiltration` record in `Lod.Core.Envelope`:
   - **Design rate** with a basis, which is one of:
     - per m² of exterior surface area: walls, roofs, and exposed floors, as EnergyPlus `Flow/ExteriorArea`;
     - per m² of exterior wall area: `Flow/ExteriorWallArea`;
     - air changes per hour: `AirChanges/Hour`.
   - **Fraction schedule.**
   - It is carried by `EnvelopePreset`, the building-level input that both converters already take. `ExampleEnvelopePresets` gets an illustrative 0.3 air changes per hour, always on: the value most example presets used.
   - *Envelope Preset* gains the inputs.
3. **Conversion.** Every zone gets its infiltration at export.
   - *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` per zone in the native EnergyPlus method, so EnergyPlus multiplies the rate by that zone's own exterior area or volume.
   - *Convert2BEM* outputs the building's infiltration once, plus each zone's exterior area and volume.
   - No zone merge aggregates infiltration any more: it follows each target zone's own surfaces, so it is conserved by construction.
4. **Validation and research.**
   - The infiltration invariants of load conservation are removed.
   - The research brief (§ on invariants) and `docs/research/program-presets.md` say infiltration is an envelope input (GLOBAL.md scientific rule 7).
   - Snapshots that contain infiltration change, documented per file.

## Part B: *Mix Programs*

### Rule

The mix is the existing zone merge (`EquivalentPropertyAggregator`, ADR-005, ADR-007, D-047) applied to a virtual zone of unit floor area made of the input presets:

- input *i* is a source of floor area ŵᵢ (its normalised weight) and volume ŵᵢ (one common height);
- the target has floor area 1 and volume 1.

Because of that, every basis follows the rule zone merges already use, and the two operations agree by construction:

| Component | Mixed value | Mixed fraction schedule |
| --- | --- | --- |
| Per floor area (lighting, equipment, occupancy, ventilation, DHW, …) | Σ ŵᵢ·vᵢ; a preset without the component contributes 0 | Σ ŵᵢ·vᵢ·sᵢ(t) / Σ ŵᵢ·vᵢ |
| Air changes per hour (ventilation) | Σ ŵᵢ·vᵢ | the same form |
| Per person (ventilation per person, …) | Σ ŵᵢ·oᵢ·vᵢ / Σ ŵᵢ·oᵢ, weighted by the occupants oᵢ (per m²) each input brings | Σ ŵᵢ·oᵢ·vᵢ·sᵢ(t) / Σ ŵᵢ·oᵢ·vᵢ |
| Absolute (a fixture flow, …) | **Σ vᵢ, raw, not weighted** (the owner's rule; the unit-area virtual zone gives this exactly) | Σ vᵢ·sᵢ(t) / Σ vᵢ |
| Conditioning | conditioned when any input is conditioned (as zone merges) | — |
| Heating and cooling setpoints | over the conditioned inputs only: Σ ŵᵢ·θᵢ(t) / Σ ŵᵢ, renormalised over them (as zone merges) | — |

Each component keeps its basis. Different bases of one load type stay side by side and add up at export, as EnergyPlus objects do (D-047). A merged magnitude of zero gives value 0, a constant-zero schedule, and an info diagnostic, as today. Every mixed load and schedule gets an `AggregationRecord` naming the input presets and the weights.

### Inputs and checks

- **Inputs.** *Presets* (list, one or more), *Weights* (a list of the same length), *Name* (optional; default `Mix of A 0.7, B 0.3`), *Space Type* (optional), and *WWR* (optional).
- **Weights.** Each must be finite and greater than 0, with the same count as *Presets*. Zero is an error: a preset without a share does not belong in the mix, and its absolutes would otherwise be added silently. Weights are normalised to sum to 1. Both the given and the normalised weights are recorded.
- **Space type.** When the input is missing, the result takes the space type of the largest-weight input; on a tie, the first such input in list order. An any-program input (no space type) chosen this way makes the result an any-program preset.
- **WWR (the owner confirmed).** When the input is missing, the result takes the weighted mean Σ ŵᵢ·WWRᵢ, read as glazing per wall shared like floor area. It is recorded as a derived value.
- **Mixing conditioned with unconditioned inputs** is allowed, as in zone merges. The info diagnostic says that the unconditioned inputs' share becomes conditioned.
- **A per-person load with absolute occupancy is an error,** whether they are in one input or in two. A mixed per-person value is weighted by the occupants per m² of every input, and absolute occupants per m² depend on the zone's area, which the mix does not know: at unit area, one input's absolute occupancy would dilute another input's per-person load (a hall of 5 people mixed half and half with an office of 0.1 people/m² and 30 m³/h per person would give 0.297 m³/h per person, 2.97 m³/h on a 100 m² zone, where merging zones of 50 + 50 m² gives 150 m³/h). The error names the inputs of each kind. Per-area occupancy is fine, and so is absolute occupancy when no input has a per-person load.

### Provenance

The result is a `ProgramPreset` with `Source = Provenance.Of("MixPrograms", …)`.

- **Parameters.** One `Input.<k>` per input, holding the preset name, the given weight, and the normalised weight: the owner's source–weight pairs. The chosen space type and how it was chosen; the WWR and how it was chosen.
- **Inputs.** Each input preset's own `Source`, for example an atlas record. So a mix of atlas presets traces to its records, and a mix of mixes nests.

### Grasshopper

*Mix Programs*, in panel *1 Program*, with a new GUID and a new icon motif. Its inputs are those above, with *Space Type* as the existing enum input. Its output is *Preset*. It is a thin adaptor over `ProgramMix.Mix(...)` in `Lod.Core.Programs`.

## Tests (written first)

- **Part A.**
  - Programs reject infiltration and per-wall loads.
  - The example presets carry none.
  - `Infiltration` validation covers a finite, non-negative rate, a fraction schedule, and each basis.
  - *Envelope Preset* round trip.
  - *Convert2IDF* writes one infiltration object per zone with the native method and the building's rate. An IDF snapshot is rewritten, with the reason given.
  - *Convert2BEM* outputs.
  - Every family × simplifier × aggregator still validates, with the infiltration invariants gone.
- **Part B.**
  - Each row of the rule table, with presets whose densities differ: per area, air changes per hour, per person (occupant-weighted, against a hand calculation), absolute raw sum, and schedules hour by hour.
  - Conditioning and setpoints: conditioned only; mixed conditioned and unconditioned with the diagnostic; renormalisation.
  - Weights: normalisation, zero, negative, NaN, count mismatch.
  - Space type: default and tie; WWR: default and given; per-person with absolute occupancy.
  - **Equivalence with zone merges.** A plan of two zones with areas 70 and 30 m², merged into one zone by *Single Zone per Floor*, gives the same densities, schedules, and setpoints as *Mix Programs* with weights 0.7 and 0.3, except the absolute loads, which a zone merge also sums raw.
  - Provenance pairs, and nesting of input sources.
- **Integration.** A mixed preset through a generator, every simplifier, both aggregator families, validation, and *Convert2IDF*.
- **Headless Rhino.** A new spec `program-mix`: the component, its errors, the envelope infiltration inputs, and the IDF.

## Interaction with the unmerged branches

- **S10 (atlas, D-122).** The converter's infiltration handling becomes obsolete. `infiltration_m3_s_m2` is then "not converted: infiltration is a building-level input". The warning `InfiltrationNotFromAtlas` and the local Infiltration load go away. Whichever branch merges second adapts its code and its tests.
- **Conditioned Merge (D-123).** No code conflict is expected beyond the aggregator's exterior-wall path and the integration test lists.
- **Decision-log numbers.** D-122, D-123, and D-124 are reserved for the three branches in that order.

## Acceptance criteria

- Every new test passes and `scripts/verify.ps1` passes. Every changed snapshot is explained in its commit and in D-124.
- *Mix Programs* agrees with *Single Zone per Floor* on the two-zone equivalence test.
- The headless Rhino specs pass. No existing component GUID changes.

## Task list

1. The owner's approval and answers (2026-10-06):
   - Part A, option (a);
   - an illustrative envelope rate of 0.3 ACH;
   - the WWR weighted mean.
2. ADR-017.
3. Part A, test-first.
4. Part B, test-first.
5. The components, icons, and smoke spec.
6. A review by a second agent, then fixes.
7. The docs (pipeline, domain model, validation, research brief, program presets, Convert2IDF and Convert2BEM), D-124, verify, the headless Rhino check, and `sync-docs`.

## Outcome

The stage is built on `feature/program-mix`; D-124 records it, and D-125 records its release in version 1.1.0 together with Conditioned Merge. At the end the suites had 417 core, 518 generator, 1624 integration, and 705 export tests. What the build settled beyond this note, and where it differs from it:

- **The per-person rule applies to any inputs (a review finding).** This note first rejected a per-person load with absolute occupancy only within one input. A review found that a mixed per-person value is weighted by the occupants per m² of every input, so at unit area the absolute occupancy of one input dilutes another input's per-person load: a hall of 5 people mixed half and half with an office of 0.1 people/m² at 30 m³/h per person gave 2.97 m³/h on a zone of 100 m², where merged zones of 50 and 50 m² give 150 m³/h, wrong by about 50 times. The error `PerPersonWithAbsoluteOccupancy` now applies whichever inputs hold the two and names both ([ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md); the rule in "Inputs and checks" above is the final one).
- **Mix sources are `Input.k`.** A mixed load, schedule, and setpoint records its sources in its `AggregationRecord` as the keys `Input.1`, `Input.2`, … of the provenance parameters that name each input with its weights, not as preset names, which may repeat. The keys are zero-padded to the width of the input count so that they sort in input order.
- **`ZoneInfiltration` in core, and per-zone flows in *Convert2BEM*.** This note had *Convert2BEM* output each zone's exterior area and volume. The build outputs each zone's design infiltration flow in m³/h instead (output 21, *Infiltration Flows*), with the rate, basis, and schedule once (outputs 18 to 20). The flow comes from `ZoneInfiltration` in `Lod.Core.Conversion`, which computes the quantities EnergyPlus multiplies, and the export tests check it against the IDF zone by zone, so the converters agree whatever the basis. EnergyPlus 26.2 was run on converted files to find what its exterior surface area counts: outdoor walls, roofs, and exposed floors with windows included, not ground floors or adiabatic surfaces; this is recorded in `IdfLoads` and [convert2idf.md](../architecture/convert2idf.md#infiltration).
- **The example rebuild and the IO dialog.** The default preset components lost their *Infiltration* and *Infiltration Schedule* inputs, *Envelope Preset* gained three inputs, and *Convert2BEM* four outputs. A definition saved before this change opens only after Grasshopper's *Grasshopper IO* message, which also blocks a headless run, so the 19 example definitions were rebuilt and reopen without it. No component GUID changed.
- **Snapshots.** The 18 canonical plan snapshots of the generator tests and 7 snapshots of the integration tests lose their infiltration load lines and nothing else. The 5 IDF snapshots gain the header line `Infiltration:`; in four of them the infiltration of each zone now uses the envelope's one schedule, written once as `Example Always On`, in place of one schedule per zone, and the infiltration objects keep their names and values.
- **Validation.** The infiltration invariants are removed with the load type; the exterior areas and the volume it multiplies are still enforced. `UndefinedLoadKind` stops a cast of the removed load type or basis; the other new codes are `InfiltrationValue`, `MixWeight`, `PerPersonWithAbsoluteOccupancy`, and `MixedConditioning`.
- **`ProgramPreset.Source`.** The provenance of a preset's values (D-122) is declared on this branch with the same members as on the S10 branch, because a mix records its inputs there; the branch that merges second keeps one declaration.
