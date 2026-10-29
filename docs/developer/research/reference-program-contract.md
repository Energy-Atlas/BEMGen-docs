# Reference program and comparison contracts

Implementation status: first-stage backend APIs under [ADR-028](../decisions/ADR-028-reference-programs-and-research-contract.md), opt-in Grasshopper adapters under [ADR-029](../decisions/ADR-029-reference-program-grasshopper-adapters.md), and stricter spatial-program checks plus explicit research ledgers under [ADR-030](../decisions/ADR-030-spatial-program-signatures-and-volume-ledgers.md). This feature branch is not merged or released. Comparison reporting remains a backend API.

The reference path is additive. Existing examples remain illustrative; their program or envelope values are not reclassified as DOE defaults. Selecting a source program does not select weather, replace a building's geometry or certify reference-building equivalence.

## Source packet

The first packet is the new-2004 DOE MidriseApartment Chicago/5A source, with 1.4_7.2 as the default and 1.3_5.0 as a separate selectable alternative. Its source identity includes the archive/member/file hashes, original zone/use keys, declared climate and explicit schedule-expansion calendar. Source building geometry, multipliers and HVAC assumptions remain evidence, not silently changed program inputs.

Select a program by original source zone identity. Do not infer a program from the building label or fill unknown uses with Office or Service examples. The office and corridor uses inside an apartment source retain their own schedules and loads. A preset applied to a different layout has a geometry departure even when its loads are preserved.

Read the representability matrix before using the packet. It distinguishes directly imported program quantities from explicitly changed and unsupported source features. Any chosen calendar/glazing/geometry substitution must be visible. Source shared services and design-day profiles require separate handling; a full annual schedule does not imply those are implemented.

The existing DOE branch's office rooms are an OpenStudio/DOE hybrid. Source authentication alone does not map an original DOE zone's loads into detailed rooms. That allocation and the branch's directional glazing/skylight dependencies are later integration work. Keep original-source measurements and accepted G1–G5 target measurements separate.

## Research preflight

In Grasshopper, *Convert2IDF* appends **Require Floor Research Eligibility** (`FloorCheck`) at input index 11, default false. Existing input indices and component GUID are unchanged. It passes the option to the backend gate below; *Override* cannot bypass it. The appended-input archive guard is retained, but the current laptop's normal component-discovery conflict prevents claiming historical saved-definition compatibility from the prepared smoke spec alone.

Use `FloorResearchEligibilityValidator.Validate(IFloor)` for an inspectable report. Enforce it in the existing `IdfWriter.Write` path with `IdfOptions.Default with { RequireFloorResearchEligibility = true }`. The option defaults to false. When enabled, missing source floors or failed floor checks block writing even with `OverrideValidation = true` or a separately supplied production-validation pass. Successful IDFs state the floor spatial-control/program-gain/configured-partition/mapping scope and unverified contracts; vertical aggregation and whole-building equivalence remain unverified.

Production validation answers whether a generated representation meets the project's normal invariants. It deliberately does not enforce conditioned-area equality or fixed setpoint values. The opt-in floor research preflight additionally checks spatial conditioning/control regions, complete geometrically valid source assignment, normalized program signatures and configured hourly heat partitions.

Compare the actual 8,760-hour heating/cooling schedule values and enabled sides, not schedule names or annual means. Check each contributing source and its target. Equal-area swaps of conditioned/unconditioned regions must fail even if total conditioned area is unchanged. Splitting one source is valid only when its geometry, assignments and controls are preserved completely.

A successful scoped preflight is not a complete geometry or thermal certificate. Its unverified contracts remain visible, including any contact/window realization, orientation, courtyard/access, native simulation or whole-building checks that the first stage cannot establish.

`SpatialProgramCompatibility` compares every mapped source region with its target and with other contributing sources. Component identity, design magnitudes and all 8,760 hourly values are normalized with actual area, volume, design occupants or fractional dwellings as appropriate. Compatible splitting and homogeneous merging remain valid; equal-area gain swaps and heterogeneous redistribution fail explicitly. Positive component schedules are checked even when their watt magnitude is tiny. Calendar declarations, relevant people/activity settings, water temperatures and stored fractions remain part of the input signature.

`HourlyHeatPartitions` checks configured lighting/equipment sensible, latent, radiant and other stored partitions at every hour. Numeric people settings are checked when supplied. Automatic people heat partition, water response and HVAC/system response depend on runtime physics and remain unverified. Explicit-versus-default origin of a stored heat fraction is not recovered from the current model. The gate does not invent missing runtime quantities. Production aggregation, production validation, examples and central tolerances are unchanged.

Exact composition must still separately establish realized window placement, contact topology, orientation and construction roles. Vertical multiplication can replace inter-storey contacts with adiabatic boundaries; that needs a separate declared boundary/coupling contract. Passing this opt-in gate establishes neither complete geometry identity nor whole-building thermal equivalence.

### Default-off registered identity screening

The subsequent [ADR-031 preflight](../decisions/ADR-031-exact-composition-identity-preflight.md) exposes `ExactCompositionPreflight.Validate(IFloor, ExactCompositionOptions?)` as a separate backend API. Options default disabled. An explicit caller can set `Enabled = true` and declare Identity or ExactComposition; Simplification is outside this contract. Only already registered one-floor records are supported; this does not create a new composer or register arbitrary placements.

Inspect each check's **Preserved**, **Failed** or **Unavailable** status. Supported checks cover one-to-one ID/mapping registration, footprint/part/surface geometry, reciprocal contacts, exposure, no internal windows, independent true orientation, host/ordinal window offset/sill/size and spatial program/control/configured-partition identity. Central distance/area/fraction/angular tolerances are reused. There is no geometry repair or new energy-error tolerance.

`GeometryPreserved` and `ProgramsPreserved` describe their supported input comparisons independently. `ProductionBaseline` retains the existing production report separately: for example changed glazing can fail that baseline while unchanged programs remain preserved. Full eligibility requires a valid baseline and every required contract known and preserved. Missing ownership is Unavailable; explicit caller declarations are snapshotted with evidence IDs and establish declaration identity/coverage only, never physical court/bay/stair authenticity. Core surfaces lack full construction assignments, so `ConstructionRoles` remains Unavailable and **`FullExactCompositionEligible` remains false in this increment**.

Six canonical OpenCourt/EnclosedCourt/CourtCluster fixtures at 0/37 degrees exercise actual generators and NoSimplification. Independent mutations cover contacts, exposure/internal glazing, true orientation, window placement with conserved glazing totals, heterogeneous spatial programs while production conservation still passes, ownership and invalid mappings. This is software evidence for registered input preservation, not source-model authentication, native behavior or measured energy equivalence. No new Grasshopper input or exporter enforcement is added; existing conversion behavior is unchanged.

## Explicit source and derived ledgers

`Lod.Core.Research.ResearchVolumeLedger.Create` takes an explicit Source or Derived representation, caller provenance, air-region rows and boundary rows. Air roles include occupied, plenum, attic, basement and excluded air. Boundary rows identify their regions and explicit interzone, adiabatic, outdoors, ground or unavailable coupling. Units are cubic metres and square metres; invalid quantities, references and duplicate identities are rejected.

`ResearchVolumeLedgerComparison.Compare` takes explicit source/derived mappings and optional declared departures such as plenum absorption, basement omission or coupling change. It retains both ledgers, raw nullable volume differences, mapping gaps, boundary comparisons and unverified contracts. Role quantities distinguish **Absent**, **Unavailable** and **Known**, including known zero. An absent role does not mean zero; an unknown constituent leaves its total unavailable. Names never infer occupancy, conditioning, correspondence or geometry.

The generic API retains its conceptual fixtures. A subsequent authenticated MediumOffice caller (`scripts/research-ledgers/README.md`) adds extracted source geometry/control references and the exact stored hybrid layout. It preserves actual measurements, declared G1 absorption, blank engine volume fields and unavailable hybrid occupied quantities/boundary sets. Explicit mapping gaps remain because no DOE-zone-to-hybrid-room thermal allocation is authenticated. This is an evidence ledger with unknowns, not a fully reconciled reference model or vertical equivalence certificate; the conceptual height-ratio illustration is not substituted for source measurements.

## Energy and cost boundaries

| Quantity | Interpretation |
|---|---|
| Zone sensible heating/cooling | Thermal demand excluding latent energy; the existing paired zoning metrics use this boundary |
| Zone total heating/cooling | Thermal demand including the compatible latent component, when actually observed |
| Zone latent component | Observed directly or derived only from matching zone-total and zone-sensible quantities; never from a district/supply minus zone residual |
| District/supply meters | Their own boundary; not automatically zone loads or purchased electricity |
| Purchased electricity/fuel | Requires genuinely observed meters and an explicit reporting boundary; facility electricity includes more than HVAC |
| Constant-COP electricity | A labelled estimate: compatible thermal demand divided by an explicit positive COP; default heating/cooling COP is 3/3 |
| Monetary cost | Requires explicit rates, currency and a stated energy boundary; absent data stay unavailable |
| Computational cost | Runtime, processor time and memory in the existing evaluation metrics; not an electricity bill |

Missing quantities are unavailable, not automatically zero. Dividing heating and cooling on the same thermal boundary by the same COP cannot reverse their ratio. Constant-COP estimates do not model fans, pumps, defrost, backup heat, distribution losses or part-load performance unless separately supplied. They are not measured energy accuracy.

## First-stage limits

### Backend selection and reporting

```csharp
using Lod.ProgramJson.Reference;

var packet = DoeReferenceCatalog.Load(
    "DOE1.4_7.2", "5A", "USA_IL_CHICAGO-OHARE").Value;
var preset = packet.CreatePreset("G SW Apartment", 0.3,
    acceptGeometryDeparture: true,
    acceptDaylightSavingDeparture: true);
```

Inspect each returned `Result` before using its value. Omitting the version selects 1.4_7.2; `DOE1.3_5.0` selects the older packet. Unknown versions, climates, locations or original zone names fail without fallback. The geometry acknowledgement is a required argument; the separate daylight-saving acknowledgement defaults to false. Generated geometry/scalar WWR depart from source geometry; annual schedules preserve source local-clock values without reproducing source daylight saving. The internal packet format is not atlas Program JSON 2.0.0 and cannot be pasted into that component. The separate *DOE Reference Program* component below provides native selection.

Both packets use the explicit non-leap Sunday calendar of 2006, including ten explicit source holidays. Weather-file holiday/daylight-saving flags set to No do not erase explicit control objects. The source daylight-saving period (second Sunday in March to first Sunday in November) is retained as evidence but unsupported in expansion. Local-clock arrays require separate alignment before comparison with standard-time simulation outputs.

`SourceObjects` is an authenticated subset. `SourceCoverage` declares retained/omitted types and counts: 395 of 1,357 objects in 1.4_7.2; 368 of 1,346 in 1.3_5.0. All 27 stored zone identities per version and their original multipliers remain evidence; selecting a program does not apply a building multiplier. The absolute `G Corridor_Elevators_Equip` load of 16,054.9450549451 W remains unsupported, with its raw row and schedule retained, and is not repeated in each corridor preset.

Call `Lod.Simulation.Comparison.ComparisonEnergyReport.Create(parsedResult)` after the existing result reader. Optional `ConstantCopOptions`, `PurchasedEnergyBoundary` and `EnergyTariff` arguments declare estimates, meter attestation and cost assumptions. Nullable zone-total quantities require compatible observed hourly zone-total outputs; latent values require matching sensible and total observations. Existing paired sensible metrics, batch schema and computational-cost fields keep their definitions. This stage adds no reporting UI.

### Grasshopper selection

*DOE Reference Program* (`DOEProg`), panel *1 Program*, GUID `9f3c8f73-4d64-4c7c-a2a2-8eb071dc7c12`, is a thin adapter over `DoeReferenceProgramSelection.Select` and the existing catalog/CreatePreset APIs. It uses the existing Program Preset output type; it does not change *Program JSON* or any existing component GUID.

| Input index | Input | Default / requirement |
| --- | --- | --- |
| 0 | Version | `DOE1.4_7.2`; older `DOE1.3_5.0` selectable |
| 1 | Climate | `5A` only in this packet |
| 2 | Location | `USA_IL_CHICAGO-OHARE` only; does not select weather |
| 3 | Source Zone | Blank means catalog discovery with **no preset**; otherwise exact original zone name |
| 4 | WWR | No default; an explicit scalar is required for a selected preset |
| 5 | Accept Geometry Departure | False; independently required for a preset |
| 6 | Accept DST Departure | False; independently required for a preset |

Outputs are Preset, Source, Zones, Zone Details, Representability and Notices. Start with a blank Source Zone and inspect the catalog and omissions. Copy an exact name from Zones, supply WWR and consciously accept each departure. An error yields no preset or fallback. The source's 2006 Sunday calendar cannot be silently mixed with Monday-calendar example programs: provide deliberately compatible presets for every generator slot. Any explicit space-type adaptation through *Any Program Preset* is a comparison-model choice, not a DOE room allocation.

The source provenance, source multipliers (not applied), authenticated-subset coverage and unsupported shared-service/design-day/DST behavior remain visible in outputs. A source preset does not supply source geometry, weather or HVAC. The comparison-report API is not exposed as a new Grasshopper runner/reader because the existing graph has no parsed simulation-result parameter or reader workflow.

The focused `reference-programs` native spec checks discovery, exact selections and errors, the existing writer gate and current/synthesized previous-input-shape archives. The latter is not a preserved historical fixture. The isolated direct-instance check on this laptop establishes the real component/document solution path only; normal startup registration, archive reopen and viewport appearance remain distinct checks.

### Source and caller checks

`scripts/reference-packet-check/verify_source_packet.py` independently reads the untouched ZIP archives and compares hashes, retained raw objects, zones, loads and consumed full-year schedules with optional public-API observations. Set `BEMGEN_REFERENCE_OBSERVATIONS` to an absolute file outside the checkout when running ProgramJson tests, then run:

```text
python scripts/reference-packet-check/verify_source_packet.py observations.json --archives-root <archives-folder> --out verification.json
```

Integration tests pass every represented source-zone program through existing generation and IDF services and reconstruct all 8,760 dated schedule values, including holidays. The writer encodes holiday values in dated annual schedules; an additional `RunPeriodControl:SpecialDays` object is not required by this representation. Generic test geometry is solely a serialization fixture and establishes no DOE geometry or thermal equivalence.

The first reference-program stage adds no typology generator, office-height default replacement, general courtyard composer or production/batch simulation. The subsequent integration branch combines that research chain with the complete DOE geometry branch; see [the integration plan](../plans/2026-10-28-main-research-doe-integration.md). The two source paths remain distinct: illustrative DOE geometry-program maps do not become authenticated MidriseApartment allocations. Chicago/5A source tests are not a silent substitute for JFK comparisons. Native/manual outcomes and exact test evidence are reported separately from source/contract tests.

### Compatibility with the DOE geometry model

The integration retains the DOE branch's orientation glazing, roof skylights, program-key grouping and multiplied-room behavior. The opt-in exact screen also compares the explicit skylight outlines on each registered ceiling host, in list order, using existing numerical tolerances. A same-area relocation, host change, shape change, reordering or missing skylight cannot pass `PlacedWindowIdentity`; conservation of total glazing alone is insufficient.

`ProgramsPreserved` compares configured thermal inputs and controls, not the source semantic classification in `Zone.ProgramKey`. It does not certify a key's meaning or physical ownership. The DOE branch's key-based `SemanticMerge` remains unchanged. Exact identity still refuses zone multipliers above one; matching `SelfAdjacent` labels do not authenticate their physical justification. Construction and physical bay/stair/court ownership evidence remain unavailable, so these software checks do not establish full eligibility or thermal/energy equivalence.
