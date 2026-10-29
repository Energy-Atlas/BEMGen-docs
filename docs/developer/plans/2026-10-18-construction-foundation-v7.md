# Construction packet v7: foundation and ground methods (design note)

> **Status:** Done 2026-10-18 (built, reviewed, and verified; merged into `main` on 2026-10-19, D-150; released in `v1.5.0`, D-175; [D-146](../decisions/decision-log.md), [ADR-023](../decisions/ADR-023-native-ground-methods-and-packet-v7.md)). Approved the same day on the owner's answers, D-145 · **Date:** 2026-10-18 · **Decisions:** D-023, D-064, D-111, D-130, D-137, D-142, D-143, D-145; new: D-146 · **Branch:** `claude/bemgen-construction-v7-update-bd63b1` (from `main` `e6c073e`) · **Source:** the atlas's packet `bemgen-construction-foundation-v7` (`D:\archetype-atlas\build\local-handover\`): its `HANDOVER.md`, `README.md`, `reference/construction-foundation-ground-v1-contract.md`, `reference/bemgen-foundation-instantiation-tests.md`, and `acceptance/initialization-cases.json`

This is one stage run as D-111 sets out: this note first; one test-first build in parts; a review of the diff by a second agent; the headless Rhino check, because *Construction JSON* and *Convert2IDF* change; `scripts/verify.ps1` before any merge; a decision-log entry and an ADR at the build, because the stage changes how a converted building meets the ground.

**Stop line.** The build ends with the branch verified, reviewed, and its documentation synchronised. It does not merge, tag, push, or trigger anything remote.

## Problem

BEMGen pins packet v3: unified 1.1.0 and detailed 2.0.0 documents with no ground. Every ground floor takes the Example envelope's construction (D-137), with ground temperatures of indoor minus 2 °C (D-130). The atlas has since published v4 (the shared mass contract 1.0.0), v5 and v6 (foundations and ground), and v7. v7 changes no physics; it clarifies how a consumer resolves and instantiates them. Its documents are unified 2.0.0 and detailed 3.0.0, with four new roles (`GroundFloor`, `FoundationWall`, `FloorOverFoundation`, `RimJoist`) and a `foundation_ground` section holding methods (`FFactor`, `CFactor`, `LayeredGround`, `Kiva`), model-wide parameters, and required geometry. BEMGen cannot read any v7 document today.

BEMGen's geometry has one ground surface: the floor under the bottom storey. It has no basement, crawlspace, garage, foundation wall, or rim joist, and computes no exposed perimeter.

## The owner's answers (2026-10-18, D-145)

1. **v7 replaces v3**, pinned whole; the old readers are retired (D-064).
2. **D-142 kept.** Only unified sets of scope `building` convert. Detailed documents and single-dwelling sets are imported and instantiated, not converted.
3. **Native ground in *Convert2IDF*** for v7 sets: F-factor floors with actual area and exposed perimeter, and layered ground floors.
4. **FC ground temperatures:** the EPW's monthly mean dry-bulb, delayed three months, rounded to 0.1 °C; no weather file means a v7 set with F/C surfaces is refused.
5. **Layered ground temperatures:** 18 °C every month, the source's effective condition.

## Design

### Part A: packet v7 and the readers (`Lod.ConstructionJson`)

- **Fixtures.** `tests/Lod.ConstructionJson.Tests/Fixtures/packet/` becomes v7 as delivered (61 files, about 10.6 MB), with `manifest.sha256` and a README naming the atlas commit. `PacketTests` checks every file's SHA-256 and size, that no extra file exists, and `packet_id`. v3's files leave the tree; git history keeps them.
- **Schemas.** The four v7 schemas are embedded byte for byte: `construction-equivalent-v2`, `construction-json-v3`, `construction-mass-accounting-v1`, and `construction-foundation-ground-v1`. Their cross-references resolve inside the library, never over the network.
- **Unified 2.0.0** replaces 1.1.0.
  - The ordinary roles, window, infiltration, and mass are read as before. Their payloads are unchanged from v3; `mass_accounting` is now the shared mass contract 1.0.0, and its `additional_mass` entries are checked against the `InternalMass` quantity.
  - The four foundation roles, `materials`, and `foundation_ground` are read into plain types in `Lod.Core` (Part B).
  - A document of any scope is readable. The *Construction JSON* component and `ConstructionSet` keep refusing a non-`building` scope with `ConstructionJsonScopeNotSupported` (D-142).
- **Detailed 3.0.0** replaces 2.0.0. Assemblies (layered, `FFactorGroundFloorConstruction`, `CFactorUndergroundWallConstruction`, `native_opaque_layers`), materials, assignments with their `when` conditions, and `foundation_ground` are read. The document is still never converted (D-142).
- **Closure (both representations).** Every executable reference resolves inside the selected document: assembly, material, ground method, model parameters, soil and insulation materials, and dimension operands (`material_thickness_id`, `assembly_thickness_id`). A missing one is an error naming its JSON pointer. Provenance and source-locator IDs are not executable references.
- The existing tests move to the v7 pair names (`midrise-apartment-2019-3B` becomes `retained-midrise-apartment-2019-3B`, and so on).

### Part B: resolving and instantiating foundations (`Lod.Core`)

Format-independent types and one service. The importer fills the types and the service instantiates them. Nothing is written to an IDF here.

- **Types.**
  - A native ground assembly: F-factor (`f_W_m_K`), C-factor (`c_W_m2_K`), or layered.
  - A ground method (`FFactor`, `CFactor`, `LayeredGround`, `Kiva`) with its parameters and model-parameter reference.
  - Model parameters (`FCBoundary`, `LayeredGroundBoundary`, `Kiva` settings with soil material, balance temperatures, and solver settings).
  - A dimension operand: a number in SI units, or `geometry_input`, `material_thickness_id`, or `assembly_thickness_id`, then `scale` and `offset_m`.
  - Initialization weights (outdoor, ground, indoor, `offset_K`).
- **Instantiation request.** Declared geometry for one surface or one foundation group, never taken from the source's reference geometry:
  - role, thermal host, and boundary;
  - actual area, exposed perimeter, and wall height;
  - group identity and topology.
- **Result.** Per surface, a resolved native definition. Per Kiva group, its own instance: resolved operands, insulation, soil, and initial temperature.
- **Identity and reuse.**
  - Definitions are compared by their complete resolved values: F with area and perimeter, C with height, and layers with materials.
  - Two equal definitions may share one object; method or assembly IDs alone never authorize sharing.
  - A Kiva group is never merged with another, even when numerically equal.
  - Model-wide Kiva settings and ground-temperature requests are shared when equal and refused when they conflict.
  - An interner over several documents accepts equal IDs with equal payloads and refuses conflicting payloads.
- **Initialization (`resstock_source_start_month_1.0.0`).**
  - The outdoor operand is the start month's mean outdoor dry-bulb.
  - With controls, the indoor operand follows the setpoints and balance thresholds:
    - heating below the heating balance temperature;
    - cooling above the cooling balance temperature;
    - linear in between.
  - Without controls (explicitly uncontrolled), the indoor operand is the outdoor operand.
  - Then T = w_o·T_out + w_g·T_ground + w_i·T_in + offset_K.
  - Missing weather, missing or reversed setpoints on a controlled host, and an unknown policy are errors. Nothing is invented and nothing is shared between groups.
- **Tests, test-first, on both representations:**
  - **R1–R6:** closure, identity conflicts, and geometry-dependent F/C reuse.
  - **K1–K6:** slab/wall coupling, independent groups, the 5A thickness operand (0.1016 m with a 120 m², 44 m slab), conflicting or missing operands, and model-wide settings.
  - **I1–I6:** read from the pinned `acceptance/initialization-cases.json`. I5 uses the vented crawlspace's weights.

  Each test compares resolved operands and group membership, not names or object counts.

### Part C: native ground in *Convert2IDF* (`Lod.Core`, `Lod.Export`)

- **Exposed perimeter.** For each ground-floor surface, the length of its polygon's edges that are not shared with another ground-floor polygon of the same storey. Partial overlaps are cancelled by length, zero is allowed, and a positive minimum is never added. The edges of an enclosed court count, since they face outdoors. The building's total is the footprint perimeter on every zoning.
- **F-factor.** One `Construction:FfactorGroundFloor` per distinct (F, area, perimeter), named by its values, on a surface with boundary `GroundFCfactorMethod`.
- **Layered ground.** The set's layers on `Ground`.
- **Ground temperatures.**
  - `Site:GroundTemperature:FCfactorMethod`: January takes October's mean, from the EPW's hourly dry-bulb, rounded to 0.1 °C.
  - `Site:GroundTemperature:BuildingSurface`: 18 °C every month, written when the IDF has a layered-ground surface.
  - Each is recorded in the header and in provenance (`GROUND:` lines).
  - A conversion without a construction set keeps D-130's rule unchanged.
- **Refusals.**
  - A v7 set with F/C surfaces and no weather file.
  - A building whose ground surfaces the set's `GroundFloor` does not cover. It takes the Example's construction only with *Fill From Example*, as a warning; it is never silent.
  - A ground method the pipeline cannot place: `Kiva` needs foundation groups, and `CFactor` needs walls below grade.
- **Unused roles.** `FoundationWall`, `FloorOverFoundation`, and `RimJoist` have no BEMGen geometry and are listed as unused in provenance.
- **Mass.** Ground floors and soil are not counted as represented interior capacity and get no restoration. The shared mass contract's other rules are unchanged.
- **Wall vertices.** A writer test checks that a rectangular wall wider than it is tall gives EnergyPlus its true height under `GlobalGeometryRules` (UpperLeftCorner, counterclockwise). This is the condition a C-factor wall depends on.

### Part D: importer-generated EnergyPlus 26.2 checks

These are opt-in with `BEMGEN_ENERGYPLUS`, plus `scripts/idd-check` on every IDF written.

- **Pipeline cases:**
  - office and warehouse F-factor on two zonings;
  - small data centre layered;
  - tall building F-factor (its `FoundationWall` unused).
- **Instantiation-only cases.** Minimal one-zone IDFs written by `Lod.Export` from Part B's instances, outside the pipeline:
  - two C-factor walls of 2 m and 3 m (R4);
  - the retained 5A Kiva slab, 10 × 12 m with 44 m perimeter, with `Foundation:Kiva`, its settings, and `SurfaceProperty:ExposedFoundationPerimeter`;
  - two separate, numerically equal Kiva foundations (K2);
  - a coupled vented-crawlspace slab and walls (K1).
- **Pass criteria.** Each run completes with no severe or fatal error and no unexpected warning. The `.eio` shows the intended constructions, foundations, and initial temperatures.
- **Reporting.** Results are reported as pass, fail, or unsupported, with the warnings. Atlas checks are not counted as BEMGen results.

### Part E: documents

- ADR-023 (native ground methods and packet v7).
- `docs/architecture/convert2idf.md`, `pipeline.md`, the fixture README, and the roadmap progress log.
- AGENTS.md project state, if the summary changes.
- A decision-log close-out entry.
- `sync-docs`.

## Order

Part A first, since everything reads its types. Then B and C, which touch different files (B: `Lod.Core` foundation types and service, plus importer tests; C: `Lod.Export` and the conversion path). Then D, which uses both, then E. A second agent reviews the whole diff before the close-out.

## Not in this stage

- Basements, crawlspaces, garages, and below-grade walls in BEMGen's geometry.
- Kiva in the pipeline.
- Single-dwelling or detailed conversion.
- Duct and mechanical systems.
- *Convert2BEM* with construction sets.
- An annual or systematic study.
- Any push, release, or CI.

## Build log, Part A

**What is built** (branch `claude/bemgen-construction-v7-update-bd63b1`):

- **Fixtures.** Packet v7 is pinned whole in place of v3: 61 files and `manifest.json`, with `manifest.sha256` `2367c495…` and the fixture README. `PacketTests` checks every file's SHA-256 and size, that no other file exists, the packet ID, the atlas commit, the 19 pairs, and that the four embedded schemas are the packet's byte for byte.
- **Schemas.** The four v7 schemas are embedded. They have no external `$ref`: the two document schemas inline the mass and foundation fragments, identical to the fragment files. The fragment schemas are evaluated on their sections too, so nothing resolves over the network. The unified 1.1.0 and detailed 2.0.0 schemas and readers are gone.
- **Types** (`Lod.Core.Foundations`, data only):
  - `FoundationData`;
  - `FoundationComponent` and `FoundationAssignment`, and `AssignmentCondition`, which replaces `DetailedCondition` and adds `ThermalHost` (in `Lod.Core.Envelope`);
  - assemblies: `FFactorGroundFloorAssembly`, `CFactorUndergroundWallAssembly`, `LayeredFoundationAssembly`, `EquivalentFoundationAssembly`;
  - materials: the `MaterialResource` kinds, `BulkMaterialResource` among them;
  - methods: `FFactorGroundMethod`, `CFactorGroundMethod`, `LayeredGroundMethod`, and `KivaGroundMethod` with `KivaMethodParameters`, `KivaInsulation`, `KivaCustomBlock`, and `KivaInitializationWeights`;
  - model parameters: `FCFactorBoundaryParameters`, `LayeredGroundBoundaryParameters`, `KivaModelParameters`;
  - `DimensionOperand`, `FoundationConfiguration` with the `HostAirExchange` kinds, and `RequiredGeometryInput`.

  `ConstructionSet.Foundation` carries the data.
- **Readers.** `ConstructionJsonImporter.Read` reads either representation of any scope. `Import` is `Read` plus D-142's scope refusal. Shared readers:
  - `FoundationReader`: closure and model pairing;
  - `MaterialReader`;
  - `MassContract`.

  Every packet document of both representations reads with full closure and no diagnostic.
- **Unchanged conversion.** The ground floor role stays not applicable, so *Convert2IDF* still takes the Example's ground floor. No export or integration snapshot changed.

**Controller choices** (Provisional):

- **The `additional_mass` rule.** For a ready unified `InternalMass`, the entries' `area_per_counted_floor_area` must sum to the component's quantity within `ToleranceSettings.Default.RelativeArea`. A `known_zero` status has no entries. Every `recipe_id` resolves in `mass_accounting.recipes`. A detailed document, or a blocked or not-applicable `InternalMass`, has no single quantity to compare. The packet's sums agree to about 1e-16.
- **The closure set.** Beyond the brief's list, the closure also covers:
  - `geometry_input` and a method's `required_geometry`, against `required_geometry`;
  - `when.thermal_host` and an air-exchange host, against `configuration.thermal_hosts`;
  - a mass entry's `recipe_id`.

  Unresolved references other than assemblies use the new `ConstructionJsonUnresolvedReference`. A detailed layer's missing material moves from `UnresolvedAssembly` to `UnresolvedReference`.
- **Pairing rules** (`InvalidStructure`):
  - FFactor executes only a GroundFloor F-factor assembly and CFactor only a FoundationWall C-factor assembly, both on `FCBoundary`;
  - LayeredGround and Kiva execute layered assemblies, on their own parameters;
  - a native F/C assembly or a `Ground` contact without a method is an error, and so is a method on any other role;
  - the soil is a bulk or massive opaque material, insulation and blocks massive opaque materials, and a thickness material has a thickness.
- **Nothing ignored.** An operand of another model, or a geometry input outside the schema's eight names, is `ModelNotSupported`.
- **Defaults.** A dimension without `scale` or `offset_m` has scale 1 and offset 0.
- **Unused.** The foundation roles, `GroundFloor` included, are listed as unused, so the IDF header names them. Part C removes `GroundFloor` from the list when it writes native ground.
- **Single-dwelling sets.** A unified set of scope `whole_dwelling` read with `Read` carries `AssignmentUnavailable`, so *Convert2IDF* refuses it even outside the component.
- **Superseded tests.** Two mass tests now expect `SchemaViolation`: the shared mass contract's schema requires both budget lists and fixes `paired_face_area_policy`.

**Open:**

- The unified schema's `$id` reads `construction-equivalent:1.2.0` while its documents are 2.0.0, and the detailed schema's reads `construction-set:2.1.0` for 3.0.0. This is the atlas's naming; to report to the atlas.
- `IdfConstructionJsonTests` still converts three building-scope documents. The five new ones are not yet in its matrix (Part C/D).
- Material `properties` keys are not checked against a closed list (the schema leaves them open).
- The headless Rhino check and the docs export have not been run for this part.

## Build log, Part B

**What is built** (`Lod.Core.Foundations.Instantiation`, plain C#, no IDF text):

- **Requests.** `FoundationSurfaceRequest` (surface ID, role, `FoundationBoundary`, actual area; optional host, exposed perimeter, height, space type, storey, interior and exterior space types, explicit assignment ID) and `KivaFoundationGroupRequest` (group ID, slabs, soil-contact walls, `FoundationEnvironment`, optional declared wall height above grade). The environment holds the twelve monthly mean dry-bulbs, the start month, the ground operand, and `FoundationControls`: `UncontrolledHost.Instance` or `ThermostatControls(heating, cooling)`.
- **Service.** `FoundationInstantiator(ToleranceSettings).Instantiate(FoundationData, FoundationInstantiationRequest)` returns `Result<FoundationInstantiation>`:
  - standalone `ResolvedFoundationSurface`s with a `FoundationConstructionDefinition` (`FFactorGroundFloorDefinition(F, area, perimeter)`, `CFactorUndergroundWallDefinition(C, height)`, `LayeredConstructionDefinition(materials)`, `EquivalentConstructionDefinition(layers)`), the method model, the ground-temperature input, and `FoundationSurfaceSource` (document, assignment, assembly, method);
  - one `KivaFoundationInstance` per group: resolved `KivaFoundationDefinition` operands and placements, `KivaModelSettings` (soil physics and solver settings without IDs), `KivaInitialCondition`, and its slab and wall surfaces.
- **Initialization.** `KivaInitialization.Derive` is the packet's `initial_temperature_C`, with the balance thresholds read from the model parameters.
- **Reuse.** `FoundationModelScope.MayShare` (definitions: equal complete values; Kiva instances: only the same instance) and `Combine(instantiations, GroundTemperatureRequest[])`, which gives a `FoundationModel` with the distinct definitions, every Kiva instance, one shared settings, and one request per ground-temperature input.
- **Interning.** `FoundationResourceInterner.Intern(FoundationData[])` gives a `FoundationResourceCatalog` of recipes only.
- **Tests.** `FoundationInstantiationTests` (66, R1–R6, K1–K6, I1–I6 on both representations, every case of `acceptance/initialization-cases.json`) and `KivaInitializationTests` (21).

**Choices** (Provisional):

- **Precedence.** `space_type`, then `story`, then `building_default` or `whole_dwelling` (one rank), as the documents' `assignment_policy` states; an explicit assignment ID wins when its rule is compatible. A rule's condition the request does not satisfy (including a window operation) makes it incompatible. A host the configuration does not declare is `FoundationInterfaceNotSupported`.
- **Boundary and method.** A `Ground` surface needs a method and a non-`Ground` surface must not have one.
- **Definition scope.** A C-factor definition is (C, height); the area stays on the surface, since `Construction:CfactorUndergroundWall` has no area. A layered definition is its materials only.
- **Kiva groups.**
  - A group needs at least one slab; its members are `GroundFloor` or `FoundationWall` on `Ground`, with one Kiva method and one host.
  - The wall height above grade from `geometry_input` is the group's declared value. Any other geometry input in an operand, or `thermal_host_height_m`, `thermal_host_volume_m3`, or `foundation_top_height_above_grade_m` in a method's list, is `FoundationInterfaceNotSupported`.
  - A declared height above grade that differs from an explicit operand by more than `ToleranceSettings.Distance` is `FoundationGeometryConflict`.
  - An assembly thickness is the sum of its layers' thicknesses.
  - A custom block's x and z may be negative; other dimensions may not.
- **Weather.** All twelve monthly means must be finite, not only the start month's. Equal setpoints are allowed, as in the source. Balance thresholds without a positive interval are refused rather than divided by zero.
- **Model scope.** `Combine` refuses a surface that reads a ground-temperature input no request supplies. A request no surface reads is kept.
- **Codes.** The new codes are in `FoundationInstantiationCodes`, not `DiagnosticCodes`, to keep Part C's files untouched.

**Open:**

- Part D writes `Foundation:Kiva`, its settings, the exposed perimeter, and the C-factor objects from these instances. Kiva wall heights are optional here; the writer needs them for vertices.
- Air exchange of thermal hosts (crawlspace SLA, garage ELA) is not instantiated.
- Program-derived start-day setpoints are not read; the caller supplies the controls.
- No IDF was written and EnergyPlus was not run for this part.

## Build log, Part C

**What is built** (branch `feature/foundation-native-ground`, from `79a0ef1`, to be rebased onto Part B):

- **Exposed perimeter** (`ExposedPerimeter`, `Lod.Core.Conversion`): per floor polygon, its edges (holes included) less the length that edges of other polygons of the same level cover within the distance tolerance (overlap intervals merged, so an edge met by several neighbours cancels each part). Zero is allowed and no minimum is added. `OfGroundFloors` groups a building's ground floors by elevation. Every family through every simplifier and aggregator, unrotated and turned, exposes the footprint's outer and court perimeter in total.
- **Ground floor resolution** (`ConstructionSet.Resolve`, `NativeGroundFloor`): for a set with foundation data, the one `GroundFloor` assignment covering building-default ground gives `FFactorGroundFloor` or `LayeredGroundFloor` (materials by ID). `ResolvedConstructions` gains `Ground` and `Unused` (without `GroundFloor` when it is used).
- **Writer.** F-factor ground floors are written per piece with `Construction:FfactorGroundFloor` (one per distinct F, area, perimeter as written) on `GroundFCfactorMethod`; layered ground floors with the set's layers on `Ground`. `Site:GroundTemperature:FCfactorMethod` comes from `EpwDryBulb` (the EPW's hourly dry-bulb, field 7, monthly means delayed three months, rounded to 0.1 °C half away from zero); `Site:GroundTemperature:BuildingSurface` is 18 °C for layered ground. `IdfDocument.Provenance` carries the `GROUND:` and `UNUSED:` lines. Envelope presets and sets without foundation data write what they wrote before; no snapshot changed.
- **Diagnostics:** `GroundMethodNotSupported` and `GroundTemperatureWeatherMissing` (errors). An uncovered ground uses `ConstructionMissing` / `ConstructionFromExample`.
- **Tests:** `ExposedPerimeterTests`, `ExposedPerimeterFamilyTests`, `NativeGroundFloorTests`, `EpwDryBulbTests` (with an opt-in Chicago TMY3 check), `IdfNativeGroundTests`, the wall-vertex and court F-factor tests in `IdfGeometryTests`, a ground-mass test in `ConstructionMassAccountingTests`, and `IdfConstructionJsonTests` on the eight building-scope sets. `IdfChecks` accepts `GroundFCfactorMethod` and checks each F-factor construction's area against its surface.

**Controller choices** (Provisional):

- **What covers the ground.** An assignment without a condition, or with scope `building_default`, boundary `Ground` or none, and no other qualifier. Two covering assignments are refused, not chosen between.
- **Perimeter per written piece.** A floor with a court is split into hole-free pieces; each piece's construction takes the piece's area and perimeter, the cut edges cancelling between pieces, so the area always equals its surface's.
- **Edge coincidence.** Within `ToleranceSettings.Distance` of the other edge's line; the family test allows the distance per edge of the ground polygons, since turned plans leave vertex offsets of that order (PerimeterCore, up to about 6 µm in total).
- **Fill From Example on a v7 set's uncovered ground** keeps D-130's indoor-minus-2 rule for that ground, since it is the Example's ground and not the source's.
- **No ground floor, no ground temperatures** for a v7 set: nothing is written.
- **`UNUSED:` provenance** is written for every construction set, not only v7 ones.
- **A missing dry-bulb (99.9) or a month without records** is an error, never filled in. A header-only weather file still gives `Site:Location`.

**Open:**

- EnergyPlus 26.2 with Chicago TMY3 (`scripts/eplus-check`, 5 sample IDFs): the office F-factor (with and without a core zone), the office on a single zone, and the C-factor hospital (layered ground floor) passed with no severe error. The data centre's layered ground failed the check with 6 severe errors, one per ground zone, "floor cannot absorb any solar gains": its source's material `Adiabatic Material` (R 1760.9 m²·K/W) has solar absorptance 0, and BEMGen's `FullExterior` solar distribution puts beam solar on the floor; EnergyPlus spreads it and completes. The value is the source's and is written as given; whether to keep it, change the solar distribution, or report it to the atlas is for the owner.
- After the rebase, the ground resolution could use Part B's instantiation service instead of its own matching.
- A multiplied ground zone (a single-zone aggregator) repeats its ground floor as EnergyPlus repeats the zone, as before; F and perimeter are the actual surface's.
- The headless Rhino check and the docs export were not run for this part.

## Build log, Part D

**What is built** (branch `claude/bemgen-construction-v7-update-bd63b1`):

- **Writers** (`Lod.Export`, `IdfFoundations.Write(FoundationModel)`):
  - `Construction:CfactorUndergroundWall` (C, height) and `Construction:FfactorGroundFloor` (F, area, perimeter);
  - layered `Construction`s with their materials by ID, and the reversed construction of a `Surface` boundary;
  - one `Foundation:Kiva` per Kiva instance (initial temperature, insulation, wall height above grade, wall depth below slab, footing, custom blocks), one `Foundation:Kiva:Settings`, and `SurfaceProperty:ExposedFoundationPerimeter` (`TotalExposedPerimeter`);
  - the two ground temperature objects;
  - an `IdfFoundationPlacement` per surface: construction, boundary, `Foundation:Kiva`, and group.

  Every field was checked against the 26.2 IDD's order, units, and defaults. What EnergyPlus cannot hold is the new error `FoundationNotWritable`. *Convert2IDF* does not use the writer, and its behaviour is unchanged ([convert2idf.md](../architecture/convert2idf.md#foundation-objects-outside-the-pipeline-construction-foundation-v7-part-d)).
- **Tests.**
  - `IdfFoundationsTests`: 19 field-assertion tests on both representations.
  - `FoundationEndToEndTests` in `Lod.Simulation.Tests`: 17 opt-in cases, run with `BEMGEN_ENERGYPLUS` and skipped otherwise. The pipeline cases go through `Convert2Idf` with a v7 building set on the canonical linear plan (*Stack*, both heat-transfer options on). The instantiation-only cases are boxes whose foundations come from `FoundationInstantiator` on the imported documents. Results go to `BEMGEN_SIM_OUT` (here under `D:\BEMGen-smoke\foundation-v7\`), one line per case in `foundation-results.txt`.

**Results** (EnergyPlus 26.2.0, Chicago O'Hare TMY3, 2026-10-18). Pass means the run completed with no severe or fatal error and no unexpected warning, and the checked values agree.

| Case | Representation | Outcome | Severe / warnings | Key checked values |
| --- | --- | --- | --- | --- |
| Medium office F-factor, *No Simplification* | unified | pass | 0 / 0 | Four F-factor constructions. EnergyPlus's U without films (Envelope Summary) equals 1/(A/(P·F) − 0.165): (72 m², 26 m) 0.493; (40, 2) 0.064; (80, 10) 0.162; (80, 18) 0.298. Σ P × multiplier = 84 m = 2 × (24 + 18). The `.eio`'s FC ground temperatures equal those written: 11.0, 4.7, −3.7, −4.6, −2.5, 3.8, 10.0, 15.3, 21.1, 24.1, 21.8, 18.1 °C |
| Medium office F-factor, *Perimeter Core* | unified | pass | 0 / 0 | (88.80, 24) 0.362; (61.38, 18) 0.395; the core (131.66 m², P 0) 0.006 = 1/177. Σ 84 m; FC ground as written |
| Warehouse F-factor, *No Simplification* / *Perimeter Core* | unified | pass / pass | 0 / 0 each | Same F as the office (1.26343630645112 W/(m·K)), so the same values |
| Retained midrise apartment F-factor | unified | pass | 0 / 0 | F 0.9346: 0.357, 0.047, 0.119, 0.218; Σ 84 m |
| Tall building F-factor | unified | pass | 0 / 0 | As the office; `UNUSED:` names `FoundationWall` |
| Small data centre layered, windowless | unified | pass | 0 / 0 | No window; `BuildingSurface` 18 °C read |
| Small data centre layered, Example windows (*Fill From Example*) | unified | fail | 6 / 0 | Completes; one severe error per bottom-storey zone (6 of 6), "floor cannot absorb any solar gains" (see below) |
| Legacy hospital basement layered | unified | pass | 0 / 0 | `BuildingSurface` 18 °C read |
| Hospital 2019 3B (layered floor) | unified | pass | 0 / 0 | 18 °C; `UNUSED:` names its C-factor `FoundationWall` |
| R4: two C-factor walls 2 m / 3 m, 6 m wide | unified, detailed | pass, pass | 0 / 0 each | Surface details: ~Width 6.00, ~Height 2.00 / 3.00, `FCGround`, each wall on its own height's construction; no "does not match its construction height" message. Fictitious R 0.8341 / 0.9976 m²·K/W |
| K4: retained 5A Kiva slab, 10 × 12 m, P 44 m | unified, detailed | pass, pass | 0 / 0 each | One `Foundation:Kiva` with floor `DWELLING SLAB`, exposed perimeter 44.00, fraction 1.00, `<Default Footing Wall Construction>`. Initial temperature field 20 °C: January mean −4.65 °C is below the 10 °C heating balance, weights (0, 0, 1). Wall height above grade 0.1016 m, depth below slab 0.2032 m |
| K2: two equal 5A slabs in two zones | unified, detailed | pass, pass | 0 / 0 each | Two `Foundation:Kiva`, each with its own zone's floor only; one settings object; both 20 °C |
| K1: vented crawlspace, coupled slab and walls | unified, detailed | pass, pass | 0 / 0 each | One `Foundation:Kiva` with floor `CRAWLSPACE SLAB` and its four walls (wall height 1.20 m, the source's 8 in concrete wall construction). Initial temperature −2.18185 °C = 0.9 × (−4.64651) + 0.1 × 20. Floor over the foundation paired with its reversed construction; rim joists `Outdoors` |
| K1 crawlspace air exchange (SLA 0.006667, ASHRAE 62.2 WSF) | both | unsupported | — | Not instantiated by Part B; the crawlspace has no infiltration object, and no ACH is invented |

The *Initial Indoor Air Temperature* is not echoed in the `.eio`. The tests check the IDF field EnergyPlus read against the instance's derived value, and EnergyPlus accepted it.

**IDD check.** `idd_check.py` against `D:\EnergyPlusV26-2-0\Energy+.idd` on the 18 distinct IDFs of the cases above (8 instantiation-only, 10 pipeline): 0 problems.

**The data-centre finding.** The severe errors come from the Example windows, not from the ground floor's values alone:

- The source's ground floor is one massless layer, R 1760.9 m²·K/W, with solar absorptance 0. The source data centre has no windows.
- Without windows (every preset's window-to-wall ratio 0), the same set runs with 0 severe errors and no warning.
- With the Example windows, which *Fill From Example* already reports as `ConstructionFromExample`, EnergyPlus reports one severe error per zone that has windows over that floor. It spreads the beam solar over the zone's surfaces and completes.

The source's values are kept. Proposal for the owner, not implemented: when *Fill From Example* gives windows to zones whose ground floor's inside layer has solar absorptance 0, *Convert2IDF* adds a warning that EnergyPlus will spread their beam solar. Alternatively, such a set is used only on windowless buildings.

**Not done: Part C's ground resolution through `FoundationInstantiator`.** It is not straightforward, and it would not be snapshot-neutral in diagnostics:

- `ConstructionSet.Resolve` runs before the geometry, without surfaces, areas, or perimeters, while the instantiator needs one request per surface.
- The two use different rules: Part C takes only building-default assignments without qualifiers and refuses two covering ones; Part B ranks `space_type`, `story`, and the defaults.
- The codes differ: `GroundMethodNotSupported` and `ConstructionMissing`, which `NativeGroundFloorTests` asserts, against `FoundationInstantiationCodes`.

**Observations** (Provisional):

- **C-factor wall resistance.** EnergyPlus's fictitious resistance for the 2 m wall is 1/C + (0.0607 + 0.3479 × 2) − 0.0769, as the Engineering Reference gives. For the 3 m wall it is 1/C + 0.92 − 0.0769: the soil resistance appears capped at about 0.92 m²·K/W beyond about 2.47 m. EnergyPlus's own 4.57 m example gives the same 0.92. This is inferred from the outputs; the documentation's text gives no cap.
- **Footing wall.** A Kiva slab without walls takes EnergyPlus's default footing wall construction, since the 5A method gives none. EnergyPlus reports no warning for it.

**Open:**

- The proposed warning above, for the owner.
- Crawlspace air exchange (SLA with the weather factor) and the garage ELA are not instantiated.
- No program-derived start-day setpoints: the cases supply 20/26 °C, and the ground operand is the annual mean of the monthly means, which every packet Kiva method weights 0.
- The headless Rhino check and the docs export were not run for this part.

## Review fixes

The second agent's review of the stage's diff, fixed test-first on the same branch. No export, integration, or program snapshot changed.

- **Major 1: the ground before Part C in user-facing text.** Fixed (`6bfcdb0`).
  - *Construction JSON*'s description, its *Roles* and *Unused* outputs, and *Convert2IDF*'s *Construction* and *Weather* inputs now say that the ground floors take the set's own method: F-factor on `GroundFCfactorMethod`, which needs *Weather* (else `GroundTemperatureWeatherMissing`), layered ground at 18 °C, and Kiva or C-factor refused (`GroundMethodNotSupported`). No GUID changed.
  - Representation: `ConstructionSet.Roles[GroundFloor]` stays `NotApplicable` internally, with the reason "given by the set's foundation data, by its native … ground method, not by this entry". `Resolve` never reads it for a set with foundation data, so `Resolve` and `IdfWriter` behave as before.
  - The *Roles* line comes from the new `ConstructionSet.DescribeGround()`, which follows `Resolve`: the F-factor or layered recipe Convert2IDF writes, a recipe it cannot place, or the status of an uncovered ground. The Rhino spec's check that *Roles* does not list `GroundFloor: NotApplicable` therefore holds as written and was not changed.
  - `GroundFloor` is no longer in `ConstructionSet.Unused`, since every building has ground floors, which take it or refuse it. Two assertions changed with this behaviour: the office's unused list and `IdfNativeGroundTests`' `Set(TallBuilding).Unused`.
  - `construction-json.md`, `convert2idf.md`, and the smoke-test checklist are updated.
- **Minor 2: ground rules set aside silently.** Fixed (`6bfcdb0`). A `GroundFloor` rule whose condition BEMGen cannot evaluate, beside the covering building-default one, gives the new warning `GroundAssignmentSetAside`, naming the rule and its condition. It is tested in Core and on a modified office document with a `space_type` rule.
- **Minor 3: the Kiva check on construction cache hits.** Fixed (`0ceb896`). The regular-material check of a Kiva surface now runs before the cache is read, so a massless layering first written for a standalone surface is refused on the Kiva slab.
- **Minor 4: the start-month off-by-one.** Fixed (`cbbc2ea`): twelve distinct monthly means with start months 1, 6, and 12 in `KivaInitializationTests`, and months 6 and 12 on the vented crawlspace of both representations. With the index mutated to `month % 12`, 3 and 4 of these tests fail. The old two-valued test still passed under that mutation.
- **Minor 5: written F-factor perimeters for every family.** The new `FFactorPerimeterFamilyTests` (`f95e1ec`) found a real defect. On turned plans the written pieces did not keep the footprint perimeter:
  - *Court Cluster* and *Enclosed Court* through *Perimeter Core*: 586.2 m against 456 m, and 337.6 m against 288 m;
  - *Point Plate* through the merging simplifiers: 89.27 m against 88 m.

  The cause: a hole split leaves its cut vertices on the 1e-6 m clipping grid, in the middle of a neighbour's long edge. Edge coincidence was measured at the neighbour's far corners from the line of the short cut edge, where the offset reached about 1.05e-6 m. The fix (`ec4835c`) measures the offset at both ends of the stretch where the two edges overlap, which is the rule the documentation already stated. The tolerance is unchanged. There is a unit test for a short edge ending 0.9 µm off a 20 m neighbour. The building-polygon family test and every other test are unchanged. EnergyPlus F-factor runs of turned plans with courts had not been made before this fix.
- **Minor 6: `EquivalentFoundationAssembly` under a layered-ground or Kiva method.** Fixed (`606471d`) by refusing it at read time with `InvalidStructure`. Neither `ConstructionSet.Resolve` nor `FoundationInstantiator` executes an inline `opaque_layers` equivalent under a method, and no packet document has one: all 20 layered-ground and Kiva assignments use `native_opaque_layers`.
- **Nits.**
  - Boundary keywords are in one place, `IdfBoundaries`, used by `IdfFoundations`, `IdfGeometry`, `IdfObjects`, and `IdfWriter`.
  - F-factor construction names go through `IdfNames.Unique`. The names are unchanged.
  - `MaximumCustomBlocks = 10` is documented: the ten blocks the 26.2 IDD lists. More are refused rather than written untested, although the object is `\extensible:4`.
  - The Kiva operand check counts errors only.
  - All of these are in `7dddc70` and `b3f190d`.
  - The mass contract check now uses the tolerances given to `ConstructionJsonImporter.Import` and `Read`, a new optional argument, with `ToleranceSettings.Default` when none is given (`f3b9da3`, tested).
- **Smoke spec.** The controller's edit of `scripts/rhino-smoke/specs/construction-json.py` is committed unchanged (`8874209`). The headless Rhino check was not run here.

## Build log, Part E (documents and `sync-docs`)

**Written:** [ADR-023](../decisions/ADR-023-native-ground-methods-and-packet-v7.md) (Accepted for D-145; the controller's realisation Provisional) and the decision-log entry D-146, which carries the checks, the EnergyPlus table, the review, and the open items. D-137 and D-143 are marked superseded in part by D-145, and D-140 and D-141 (an omission from D-142) by D-142, in their status lines only. ADR-021's status line names D-145's change to its decision 2. The roadmap's progress log and AGENTS.md "Project state" have one short entry each.

**`sync-docs`** (the project skill, run on 2026-10-18 at the end of this branch):

- **Applied here:**
  - [domain-model.md](../architecture/domain-model.md): the `ConstructionSet` entry said the ground is always the Example's; it now describes `Foundation` (`FoundationData`), `NativeGroundFloor`, `FoundationInstantiator`, and `ExposedPerimeter`, and the document's scope names `Lod.Core.Foundations`.
  - [pipeline.md](../architecture/pipeline.md): the *Construction JSON* paragraph names the native ground, and the *Convert2IDF* summary no longer says every ground uses "indoor minus 2 °C".
  - `scripts/rhino-smoke/README.md`: the `construction-json` spec's description (the ground remark became F-factor ground floors with the weather file, and the no-weather error).
  - [grasshopper-smoke-test.md](../development/grasshopper-smoke-test.md): the result of the headless rerun (all 17 specs, `construction-json` 23 checks).
  - Status markers in the decision log and ADR-021, as above.
- **Already current (the parts' own edits):** [construction-json.md](../architecture/construction-json.md), [convert2idf.md](../architecture/convert2idf.md), the smoke-test checklist, and the descriptions of *Construction JSON* and *Convert2IDF* in `src/Lod.Grasshopper` (they cite no decision or ADR numbers).
- **Not changed:** `README.md` and the "Status" section describe released versions (1.4.0); this branch is not released, and no version bump is made (`Directory.Build.props` stays 1.4.0). The rest of AGENTS.md "Project state" stands.
- **Recorded for the public docs repository** (not touched; no docs export was run, since it belongs to a tagged version):
  - The site pins 1.4.0 at `e6c073e` (`reference-source.json` in `D:\BEMGen-docs`). Since then these changed what the site shows: the description and the *Source*, *Roles*, and *Unused* outputs of *Construction JSON*, the *Weather* and *Construction* inputs of *Convert2IDF*, and the developer documents (this note, ADR-023, the decision log, `construction-json.md`, `convert2idf.md`, `domain-model.md`, `pipeline.md`, the smoke-test checklist, AGENTS.md).
  - At the tagged version: run `scripts/docs-export/export.ps1` (Rhino 8 is installed here), import it in the docs repository, and run its `sync-docs`. A release `v<version>` with the files of `scripts/package-release.ps1` is also needed then. The owner chooses the version.
  - Hand-written pages of the site that mention the ground ("the Example's ground floor", "indoor minus 2 °C") should be checked against D-145 when it imports the export.
- **For a person in Rhino:** the components' look and text in Grasshopper (the new *Roles* ground line and the *Construction* and *Weather* input descriptions), and an install from the release at the tagged version.
- **Link check:** `python scripts/docs-export/developer_pages.py --check` printed `Developer pages: 76 checked; 1 redaction(s)` and no broken link. The one redaction is the owner's e-mail address at `decision-log.md:302`, which was there before this stage.

## Build log, the solar warning (D-147)

- The owner asked for a *Convert2IDF* warning when Example windows go into zones whose ground floor absorbs no solar. Built test-first: `ExampleWindowSolarNotAbsorbed` (warning), raised when the set has no window, the resolved ground floor's inside layer has an explicit solar absorptance of 0, and some zones with windows have only ground floors; it names those zones and repairs nothing.
- Tests: two in `IdfNativeGroundTests` (the named zones on the linear plan; no warning without windows, on the office F-factor set, or on the legacy hospital's absorbing layered ground), and the opt-in EnergyPlus data-centre case now checks that the warning names as many zones as EnergyPlus reports severe errors (6) and is absent on the windowless run.

## Build log, turned plans with courts in EnergyPlus (D-148)

D-146 left one item open: F-factor runs of turned plans with courts, the case `ec4835c` fixed, had never been made in EnergyPlus. The new opt-in theory `AnFFactorSetOnATurnedPlanWithCourtsExposesTheFootprintsOuterAndCourtPerimeter` in `FoundationEndToEndTests` covers it. It converts the medium office v7 set (`medium-office-2019-3B.unified.json`) on *Enclosed Court* and *Court Cluster*, turned 30° and moved (5, −3) m as `FFactorPerimeterFamilyTests` turns them, through *Perimeter Core* and *Conditioned Merge* with *Stack* (multipliers 1, 2, 1, both heat-transfer options on). It checks:

- the run is clean;
- each F-factor surface's U without films (Envelope Summary) is 1/(A/(P·F) − 0.165), or 1/177 at P = 0;
- Σ P × zone multiplier is the turned footprint's outer and court perimeter, within the distance tolerance per ground-polygon edge.

The F-factor checks of the existing pipeline cases moved into a shared helper, `FFactorFloors`, unchanged.

**Results** (EnergyPlus 26.2.0, Chicago O'Hare TMY3, 2026-10-19, outputs under `D:\BEMGen-smoke\foundation-v7\turned-courts\`):

| Case | Outcome | Severe / warnings | Key checked values |
| --- | --- | --- | --- |
| *Enclosed Court* turned 30°, *Conditioned Merge* | pass | 0 / 0 | Five F-factor constructions: (360 m², 63 m) 0.229; (36, 3) 0.107; (36, 6) 0.218, each equal to 1/(A/(P·F) − 0.165) at the table's three decimals. Σ P × multiplier 288 m = the footprint's outer ring and its court (72 ground-floor edges). FC ground as written |
| *Court Cluster* turned 30°, *Conditioned Merge* | pass | 0 / 0 | Ten F-factor constructions: (374.4, 65.4) 0.229; (457.2, 67.2) 0.192; (36, 3) 0.107; (36, 6) 0.218. Σ 456 m = the outer ring and two courts (116 edges). FC ground as written |
| *Enclosed Court* turned 30°, *Perimeter Core* | fail | — | EnergyPlus stopped by the runner's 30-minute limit (`EnergyPlusTimeout`) in "Initializing Simulation"; the `.err` is empty. Σ P × multiplier in the IDF is 288.0000036 m |
| *Court Cluster* turned 30°, *Perimeter Core* | fail | — | The same timeout. Σ 456.0000051 m |

**IDD check.** `idd_check.py` against `D:\EnergyPlusV26-2-0\Energy+.idd` on the four IDFs: 0 problems.

**The finding: a near-zero perimeter instead of zero.** The *Perimeter Core* pieces of the turned bottom-storey core are not written with P = 0:

- *Court Cluster*'s three core pieces have P = 1.03e-6, 3.92e-7, and 6.57e-7 m (`L0/CORE/F1#1` to `#3`, 205.9 to 300.7 m²).
- *Enclosed Court*'s two core pieces have P = 1.03e-6 and 8.84e-7 m.

`ExposedPerimeter` subtracts the covered length from each edge. On a turned plan, the neighbours' corners miss each other along the edge by about a micrometre, so a sliver stays exposed. These slivers sum to less than the per-edge tolerance `FFactorPerimeterFamilyTests` allows, so that test passes.

EnergyPlus takes 177 m²·K/W only at P = 0. With P ≈ 1e-6 m, its fictitious insulation is A/(P·F) − 0.165 − R_concrete, about 1.6e8 to 6.1e8 m²·K/W, and the run never leaves initialisation.

As a check, the *Court Cluster* IDF with only those three perimeter fields set to 0 completed in 17.5 s, with 0 severe errors and 0 warnings.

The unturned *Perimeter Core* office of Part D writes its core with P = 0 and passes.

**Not fixed here.** The fix is to the transformation logic in `ExposedPerimeter`, for example by treating an uncovered remainder within the distance tolerance as covered, so that a piece with no exposed edge gets exactly 0. It changes written perimeters, so it is for the stage owner and needs its own test first. Once it lands, the two *Perimeter Core* cases are the EnergyPlus check. Until then they fail, each after the 30-minute runner limit.

## Build log, exact-zero core perimeters (D-149)

D-148's fix, built test-first on `claude/nifty-sanderson-4e38ed`'s tip (`5900d2e`).

- **Tests first.** `ExposedPerimeterTests` gains a 20 m square split as *Perimeter Core* splits it, turned 30° and moved (5, −3) m, whose neighbours' inner corners lie 0.4 µm inside the core's: the core gave 3.2e-6 m and must give 0.0 exactly. A second test keeps a 10 µm gap exposed. `FFactorPerimeterFamilyTests` now also requires each written ground piece with no edge on the footprint's boundary (no edge midpoint within the distance tolerance of a footprint edge) to have P == 0. Before the fix it failed in 24 of its 36 cases, every one a bottom-storey *Perimeter Core* core: up to 4.5e-6 m on turned plans, and floating-point remainders (2.8e-14 m on the two inspected) on the unturned *Foyer Halls*, *Care Hub*, *Court Cluster*, *Radial Lobes*, *Branching Mall*, and *Winged Band*. The per-edge allowance on the total had hidden all of them.
- **Fix.** `ExposedPerimeter` exposes what the covering intervals leave of an edge stretch by stretch, and a stretch no longer than `ToleranceSettings.Distance` counts as covered: a gap between two intervals or between an interval and an end of the edge. It replaces the subtraction of the merged intervals' length. No tolerance was added and no minimum is added; edge coincidence is unchanged.
- **Snapshots.** No IDF, integration, or program snapshot changed; `scripts/verify.ps1` passed.
- **EnergyPlus** (26.2.0, Chicago O'Hare TMY3, 2026-10-19, outputs under `D:\BEMGen-smoke\foundation-v7\turned-courts-fix\`): all four turned-court cases pass, each with 0 severe errors and 0 warnings.

| Case | Run | Key checked values |
| --- | --- | --- |
| *Enclosed Court* turned 30°, *Perimeter Core* | 12 s | Two core pieces at P = 0 (205.9 m²), EnergyPlus U 0.006 (1/177 = 0.00565). Perimeter pieces at P = 48 and 24 m exactly. Σ P × multiplier 288 m, against 288.0000036 m before |
| *Court Cluster* turned 30°, *Perimeter Core* | 18 s | Three core pieces at P = 0 (205.9, 300.7, 205.9 m²), U 0.006. Perimeter pieces at P = 84, 48, and 24 m. Σ 456 m, against 456.0000051 m before |
| *Enclosed Court* turned 30°, *Conditioned Merge* | 18 s | As in D-148: Σ 288 m |
| *Court Cluster* turned 30°, *Conditioned Merge* | 29 s | As in D-148: Σ 456 m |

The same rule also drops the sub-tolerance slivers on the perimeter pieces' shared edges, so their perimeters are now exact as well. Before, they were a micrometre above.

## Build log, one assignment-selection rule

The review accepted Part C's ground resolution and Part B's selection as two rules for now, noting they could quietly disagree on a multi-assignment `GroundFloor` component. They now share one rule, with no change of behaviour.

- **`AssignmentSelector.Select(assignments, AssignmentRequest)`** (`Lod.Core.Foundations`) holds the matching and the precedence that were private to `FoundationInstantiator`. It needs no area, perimeter, or other geometry, since `Resolve` runs before the geometry exists.
  - A `Surface` request is the instantiator's: each qualifier satisfied, ranks `space_type`, `story`, then `building_default` or `whole_dwelling`; a named assignment when its rule applies; an applying scope without precedence reported.
  - A `BuildingDefault` request is `ConstructionSet.Resolve`'s ground (`AssignmentRequest.BuildingDefault("Ground")`): the same matching, restricted to unconditional or `building_default` rules. This is exactly the former `CoversGround`: the rules it took, the two covering rules it refused (now `Ambiguous`), and the rules it set aside (now `NotApplying`).
- **Diagnostics unchanged.** Each caller turns the outcome into its own codes and messages: `GroundMethodNotSupported`, `ConstructionMissing` / `ConstructionFromExample`, and `GroundAssignmentSetAside` for `Resolve`; `FoundationAssignmentUnmatched`, `FoundationAssignmentAmbiguous`, and `FoundationInterfaceNotSupported` for the instantiator. No test changed.
- **Tests.** `AssignmentSelectorTests` (11) in `Lod.Core.Tests`; `NativeGroundFloorTests`, `FoundationInstantiationTests` (R, K, I), and `IdfNativeGroundTests` pass unchanged; no snapshot changed.
