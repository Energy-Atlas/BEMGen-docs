# Construction JSON

> **Status:** Provisional (the controller's realisation of D-137, D-138, D-140 to D-143, and D-145, pending the owner's reading) · **Component:** *Construction JSON* (`CJson`), panel *1 Program*, GUID `b2802511-fee7-49ab-bdcb-9329ce293461` · **Parameter:** *Construction Set* (`Cons`), GUID `ef90ede8-f0ff-4495-822b-11c5e61a6fe5` · **Design note:** [2026-10-15-construction-json](../plans/2026-10-15-construction-json.md)

## Purpose

The Energy Archetype Atlas publishes the constructions of a building context as JSON, in two kinds of document:

- the **unified** `building_level_equivalent` 3.1.0: one assembly per envelope semantic;
- the **detailed** `construction_set` 4.3.0: the source model's assignment rules.

These are the contracts of atlas release 2.0.0 (D-172, [ADR-027](../decisions/ADR-027-atlas-release-2-0-0-contracts.md)), unchanged in release 2.1.0, whose construction sets and schemas are 2.0.0's (D-198); the unified 2.0.0 and detailed 3.0.0 of packet v7 are retired and refused (`ConstructionJsonKindNotSupported`). Over those, 4.3.0 and 3.1.0 add, all optional and all read as information, never assigned:

- `alternates.<role>` (detailed 4.3.0, atlas handoff item 3): in the 90.1 templates, where the PNNL prototype builds a role differently from the openstudio-standards building default by more than 1%, every prototype variant with its share of the role's net area, its compared values, an assembly in `assemblies`, and its evidence. They are `DetailedConstructionDocument.Alternates` and one *Roles* line each; the assignments stay the building default. A variant whose assembly is missing is `ConstructionJsonUnresolvedAssembly`; its evidence ID is provenance and is not resolved. The area shares are given to six decimals by the atlas and sum to 1 within 1e-6; BEMGen does not check the sum. Modelling a role the PNNL way (splitting its surfaces by the shares, walls by floor) is not done (open).
- `fenestration_defaults` (unified 3.1.0): the source model's whole-building window ratios (all, conditioned, unconditioned zone surfaces; `null` where there is no exterior surface), `ConstructionJsonImport.FenestrationDefaults`, for checking a generator's total glazing.
- the source's design-flow infiltration methods (`methods.doe_design_flow`, `methods.source_design_flow`, detailed 4.1.0 and 4.2.0) and an `evidence_id` on mass entries (checked against the shared mass contract 1.1.0, D-173). A set whose `default_method` is `source_design_flow` (the IECC sets) is read with the warning `ConstructionJsonInfiltrationMethodNotSupported` and refuses conversion (`AssignmentUnavailable`): its rules name the source model's zones and carry a wind coefficient, which BEMGen's building-level infiltration (D-124) does not hold. This is the only reason the IECC sets of release 2.0.0 do not convert (D-173): the atlas records the source's method faithfully and defers a building-level equivalent to its IECC unified representation.

Both carry, since packet v7 (D-145), the shared mass contract (`mass_accounting`, section version 1.0.0; its schema is 1.1.0 since D-173), the document's `materials` and `evidence`, four foundation roles (`GroundFloor`, `FoundationWall`, `FloorOverFoundation`, `RimJoist`), and a `foundation_ground` section with the source's configuration, ground methods (`FFactor`, `CFactor`, `LayeredGround`, `Kiva`), model parameters, and required geometry ([below](#foundation-and-ground-data)). The unified 1.1.0 and detailed 2.0.0 readers are retired (D-064).

BEMGen converts only the unified document, and only one of the whole-building scope (`building`, such as the office, warehouse, and apartment prototypes); a single-dwelling set (scope `whole_dwelling`) is refused ([scope](#scope), D-142). It reads the detailed document with every rule and condition, as evidence, and never converts it ([below](#detailed-documents)).

As with *Program JSON*, BEMGen reads only the JSON **text**: no file path and no network. The four schemas of release 2.0.0 are embedded byte for byte in `src/Lod.ConstructionJson/Schemas/`: `construction-equivalent-v3.1` (unified), `construction-json-v4.3` (detailed), `construction-mass-accounting-v1.1` (1.0.0 with the optional mass-entry `evidence_id`, D-173), and `construction-foundation-ground-v1`. The two document schemas are self-contained: they inline the mass and foundation fragments and have no external `$ref`. The two fragment schemas are evaluated on their sections as well, so nothing resolves over the network. The test documents are release 2.0.0 exports, 21 detailed/unified pairs in `tests/Lod.ConstructionJson.Tests/Fixtures/atlas-2.0.0/`: the 19 contexts of the retired packet v7 under their old names (equal values, new IDs), the medium office in 5B with alternates, and an IECC medium office (the README (`tests/Lod.ConstructionJson.Tests/Fixtures/README.md`), D-172), pinned to atlas commit `f617b30b`, release 2.0.0 as corrected in place (D-173). **IECC sets (D-173):** the two atlas defects BEMGen reported (D-172) are fixed in the atlas: the mass entries' `evidence_id` meets the shared mass contract 1.1.0, and the ground storey's adiabatic F-factor slabs with no exposed perimeter (the medium office's `Core_bot_ZN_5_Floor`) are in the `GroundFloor` building default (rule `source_boundary_correction`), whose F-factor method takes the exposed perimeter from BEMGen's geometry. BEMGen still refuses a ground method on an `InteriorFloor` assignment. The IECC documents are read with one warning, on their infiltration.

`Lod.ConstructionJson` depends on `Lod.Core`, on `Lod.ProgramJson` for its strict reader and embedded-schema evaluation, and on the JSON Schema library. It never references RhinoCommon or Grasshopper.

## From the JSON to a construction set

`ConstructionJsonImporter.Read(text)` reads the text strictly (UTF-8 without a BOM, no duplicate members, finite numbers), checks it against the schemas, and then against the contract's rules, for a document of either representation and any scope. Every problem is reported, with its JSON Pointer as subject. `ConstructionJsonImporter.Import(text)` is `Read` plus the scope rule ([scope](#scope)); the component uses it. The result, a `ConstructionJsonImport`, holds a `ConstructionSet` (`Lod.Core.Envelope`), the document's `Foundation` (`Lod.Core.Foundations.FoundationData`, also on `ConstructionSet.Foundation`), its `Evidence`, its scope, and its identity:

| JSON | Construction set |
| --- | --- |
| `ExteriorWall`, `ExteriorRoof`, `ExteriorFloor`, `InteriorWall`, `InteriorFloor` | the roles exterior wall, roof, exposed floor, interior wall, interior floor (the ceiling below is its reverse); BEMGen's internal mass role, a removed slab, takes the interior floor recipe |
| a component `not_applicable` or `blocked` | the role not applicable or blocked, with the source's reason |
| the ground | the set's own `GroundFloor` component, in `ConstructionSet.Foundation`: *Convert2IDF* writes an F-factor or layered-ground recipe natively and refuses a Kiva or C-factor one ([convert2idf.md](convert2idf.md#native-ground-of-a-construction-set-d-145), D-145). The role's entry in `ConstructionSet.Roles` is not applicable with a reason naming the foundation data, since a set with foundation data never reads it; the *Roles* line for `GroundFloor` is `ConstructionSet.DescribeGround()`, which says what *Convert2IDF* does with the ground |
| `Material` and `Material:NoMass` layers | massive and massless layers named `{assembly id} L{n}`, outside first; the exterior surface properties are the outside layer's finish, the interior ones the inside layer's |
| `ExteriorWindow` `SimpleGlazing` | the window's simple glazing; `visible_transmittance_mode` `energyplus_autocalculate_from_shgc` leaves the VT to EnergyPlus |
| `solar_modifiers.incident_solar_multiplier` (constant) | one `SurfaceProperty:IncidentSolarMultiplier` per window |
| `infiltration.natural_ach` (1/s) | × 3600 air changes per hour, always on |
| `InternalMass` with `quantity` | the furnishing recipe and its area per counted floor area |
| `mass_accounting.physical_capacity_budgets` | each family's capacities summed (each entry's `source_assembly_id` is provenance); an empty list is zero, a missing one a schema error |
| `mass_accounting.additional_mass` | checked, not added a second time: its entries' `area_per_counted_floor_area` must sum to the ready `InternalMass` quantity within the relative area tolerance of the tolerances `Import` or `Read` is given (`ToleranceSettings.Default` when none); a `known_zero` status has no entries; every entry's `recipe_id` is in `mass_accounting.recipes` |
| `FloorDistributedMass` | the recipe of unrepresented floor capacity |
| other ready components (doors, skylights, tubular devices, `InteriorCeiling`, and the foundation roles `FoundationWall`, `FloorOverFoundation`, and `RimJoist`) | listed as unused: BEMGen has no geometry for them. `GroundFloor` is never listed, since every building has ground floors, which take it or refuse it |

The codes are in `ConstructionJsonDiagnosticCodes`; strict-reading errors keep the codes of `ProgramJsonDiagnosticCodes`. Conversion is in [convert2idf.md](convert2idf.md#construction-sets): resolving the set for each building, the mass ledger, and the header lines.

### Scope

Only a unified document whose `scope` is `building` is converted (D-142). `Read` reads a document of any scope, so that its foundations can be instantiated; the set of a unified document of another scope carries `AssignmentUnavailable`, which *Convert2IDF* refuses with `ConstructionAssignmentUnavailable`. `Import`, and so the *Construction JSON* component, makes any other scope the error `ConstructionJsonScopeNotSupported`, with the subject `/scope`, and nothing is made.

- A `whole_dwelling` set describes one dwelling, such as a ResStock house or the packet's apartment unit (`retained-residential-apartment-unit-1990s-4A`). BEMGen's residential buildings are apartment blocks, which take a building-scope apartment set.
- So the residential rules of D-140 are gone: a house's attic ceiling as its roof, the garage-wall caveat, and the warning on an interior floor that is adiabatic in the source (and the diagnostics `ConstructionApproximation` and `AdiabaticSourceConducted`). `InteriorCeiling` is always listed as unused.
- **The apartment set is the residential case.** The packet's `retained-midrise-apartment-2019-3B` has the medium office's shape: every role BEMGen uses is ready, its `InteriorWindow` is not applicable with the reason `source_reference_zero_exposure` (valid, and not listed as unused), and it has budgets, furnishings, and a floor-distributed mass.
- Unconditioned space is unconditioned: no garage or attic category is modelled.
- BEMGen's windows are fixed, and a unified set's window is already resolved by its source's window areas, so operability raises no question.
- *Fill From Example* (*Convert2IDF*) stays opt-in, for a role a building-scope set marks not applicable, a ground the set's `GroundFloor` does not cover among them; a covered ground takes the set's own ground method (D-145), and a Kiva or C-factor one is refused either way.

## Foundation and ground data

Both representations are read into the same plain, immutable types of `Lod.Core.Foundations` (`FoundationData`), which instantiation (D-145, Part B) consumes. Nothing is instantiated here: an ID names a recipe, not a construction or a physical foundation.

| JSON | Type |
| --- | --- |
| the four foundation roles | a `FoundationComponent` per `FoundationRole`, with `FoundationAssignment`s: the assembly, the `when` as an `AssignmentCondition` with its `ThermalHost`, and an optional ground method. A unified role is one recipe or, for the native exceptions, two or more assignments with `NativeExceptionReason` |
| `FFactorGroundFloorConstruction`, `CFactorUndergroundWallConstruction` | `FFactorGroundFloorAssembly` (`FFactor`, W/(m·K)), `CFactorUndergroundWallAssembly` (`CFactor`, W/(m²·K)) |
| `native_opaque_layers` (and a detailed `opaque_layers`) | `LayeredFoundationAssembly`: its material IDs, exterior to interior |
| a unified `opaque_layers` equivalent (`FloorOverFoundation`, `RimJoist`) | `EquivalentFoundationAssembly`: its `Construction`, read as the ordinary roles are |
| `materials` | a `MaterialResource`: opaque (`Layer`, `NoMassLayer`, `AirGapLayer`), glazing (`GlassLayer`, `GasLayer`), simple glazing, `BulkMaterialResource` (soil), or unsupported with its reason |
| `foundation_ground.methods` | `FFactorGroundMethod`, `CFactorGroundMethod`, `LayeredGroundMethod`, or `KivaGroundMethod` with `KivaMethodParameters`: wall depth below slab, wall height above grade, insulations, footing, custom blocks, and `KivaInitializationWeights` |
| `foundation_ground.model_parameters` | `FCFactorBoundaryParameters`, `LayeredGroundBoundaryParameters`, or `KivaModelParameters`: soil, initialization policy, balance temperatures, ground absorptivities and roughness, far field, deep ground, cells, timestep |
| a dimension | a `DimensionOperand`: a number in metres, or `geometry_input`, `material_thickness_id`, or `assembly_thickness_id`, then `scale` and `offset_m` |
| `configuration` | `FoundationConfiguration`: type, reason, thermal hosts, and each host's `HostAirExchange` (`constant_ach`, `source_sla_annual`, `source_garage_sherman_grimsrud`) |
| `required_geometry` | a `RequiredGeometryInput` per `FoundationGeometryInput` |

**Closure.** Every executable reference must resolve inside the same document, or it is an error naming its JSON Pointer; another document never repairs it.

- An assignment's `assembly_id`: `UnresolvedAssembly`.
- `UnresolvedReference`: an assignment's `ground_method_id`, a method's `model_parameters_id`, the Kiva `soil_material_id`, an insulation's, footing's, or custom block's `material_id`, a layer's `material_id`, a dimension's `material_thickness_id`, `assembly_thickness_id`, or `geometry_input`, a method's `required_geometry`, an assignment's `when.thermal_host` and an air exchange's host (both against `configuration.thermal_hosts`), and a mass entry's `recipe_id`.

Provenance, evidence, and source-locator IDs (`evidence_ids`, `property_evidence`, a budget's `source_assembly_id`, a derivation's contributors) are not executable references. A test reads all 40 readable fixture documents with full closure.

**Pairing.** An F-factor method executes a ground floor's F-factor assembly and a C-factor method a foundation wall's C-factor assembly, both on `FCBoundary` parameters. Layered-ground and Kiva methods execute layered assemblies of materials by ID (`LayeredFoundationAssembly`), on `LayeredGroundBoundary` and `Kiva` parameters; a unified `opaque_layers` equivalent with inline layers (`EquivalentFoundationAssembly`) under either is `InvalidStructure`, since neither *Convert2IDF* nor instantiation executes one (no packet document has one). These are `InvalidStructure`:

- a native F/C assembly without a method;
- a ground floor or foundation wall touching the ground (`boundary_condition` `Ground`) without one;
- a method on any other role;
- a Kiva soil that is not a bulk or massive opaque material, an insulation or block that is not a massive opaque material, and a thickness operand whose material has no thickness.

**Nothing is ignored.** An operand of another model (an `sla` on a constant air exchange, a Kiva setting on an F/C boundary) or a geometry input outside the contract's eight is `ModelNotSupported`. The document's `evidence` is kept as `ConstructionEvidence` records, as provenance only.

## Detailed documents

`ConstructionJsonImporter.Read` (and `Import`) reads a detailed `construction_set` 4.3.0 (embedded schema `construction-json-v4.3.schema.json`, byte for byte) into a `DetailedConstructionDocument` on the import's `Detailed`, with its `Materials` and `Foundation`.

- **What is kept.**
  - Each component, in document order: its semantic, disposition (`Provided` or `SourceAbsent`), target, and assignments.
  - Each assignment: its assembly, its ground method if any, its `when` condition (`AssignmentCondition`: scope, space type, storey, window operation, interior and exterior space types, boundary, thermal host), and its source element IDs.
  - Each assignment's geometry instructions: area method, partition area per conditioned floor area, the source reversal flag, roof pitch, and overhang.
- **Assemblies in BEMGen's types.** Each assembly is read into an opaque `Construction` named by the assembly ID, its layers named by material ID, outside first. A window becomes a `GlazingSpec` or a `LayeredGlazing`. A native assembly also carries its foundation assembly as `Native`: an F-factor floor or a C-factor wall, without a construction, or native layers.
- **Materials.** `StandardOpaqueMaterial` is a `Layer` and `MasslessOpaqueMaterial` a `NoMassLayer`, each with its own surface finish; clean, non-diffusing `SpectralAverage` `StandardGlazing` is a `GlassLayer`; and `BulkMaterial` (soil) is a `BulkMaterialResource`. These are the models the packet's documents use. `AirGap` and `Gas` are read too, but no packet document has one, and their property names (`resistance_m2_K_W`; `gas_type`, `thickness_m`) are assumed, not confirmed by the contract.
- **Solar modifiers.** A constant incident solar multiplier is kept. A window's `overhang_geometry` is kept as evidence (`SourceOverhang`) and never applied, since BEMGen owns geometry.
- **Kept for a later assignment.** Each assignment's evidence IDs, area convention, interstorey area rule, paired-floor flag, and activation threshold, and the roof film rule. The whole `metadata`, as `MetadataJson`, including the selection receipt that an assignment must agree with; it is not checked against the assignments yet.
- **Malformed structure is an error:**
  - an assembly or material key differs from its ID (`AssemblyIdMismatch`);
  - an assignment's assembly is missing (`UnresolvedAssembly`) or a layer's material is (`UnresolvedReference`), each pointing at the array entry;
  - a layer order is not an integer or repeats;
  - a provided component has no assignments, or an absent one has some;
  - a glazed opening (window, glass door, skylight, tubular device) is assigned an opaque assembly, or anything else a glazing one;
  - a role other than a ground floor or foundation wall names a ground method;
  - any foundation or mass check [above](#foundation-and-ground-data).

  The layer-order, disposition, glazing, and ground-method cases are `InvalidStructure`. Orders need not be contiguous.
- **Unsupported physics is a warning.** Glass BEMGen does not read, an unknown roughness or gas, a solar modifier other than a constant multiplier, or a value out of the envelope's ranges makes only that assembly unsupported: it is kept with `Unsupported` and no construction, with the warning `AssemblyNotSupported`. One unusual alternative does not make a source-faithful document unreadable.
- **Malformed evidence** (an overhang without its numbers) is the warning `EvidenceNotRead`. The unified reader also accepts `overhang_geometry` beside the multiplier, but does not keep it.
- **Nothing is assigned.** A detailed document is evidence and is never converted (D-142): binding its conditions to BEMGen zones (E2) was dropped. A garage-facing wall is not turned into a generic partition, an `Adiabatic` interstorey recipe is not authorised as a conductive slab, and the source reversal flag is evidence, not a second reversal.
- **The construction set.** It has every role not applicable and carries `AssignmentUnavailable`, so *Convert2IDF* gives the error `ConstructionAssignmentUnavailable`, whose message says that BEMGen converts only unified building-scope documents and names the context whose unified document to use. That is a compatibility error, not a malformed-JSON one, and *Fill From Example* does not change it. *Construction JSON* shows it as a warning.

## Component

*Construction JSON* is a thin adaptor over the importer.

| Index | Input | Nickname | Access | Content |
| --- | --- | --- | --- | --- |
| 0 | JSON | J | item | The unified construction JSON text. |

| Index | Output | Nickname | Content |
| --- | --- | --- | --- |
| 0 | Construction | Cons | The construction set, for *Convert2IDF*'s *Construction* input. |
| 1 | Source | Src | The JSON's identity and SHA-256, its scope, detailed context, climate zone, reference, infiltration, and a line on its foundation. |
| 2 | Roles | R | Unified: each role and the window, with its assembly, or its status and reason. Detailed: each component, with its disposition and every assignment's assembly and condition. |
| 3 | Unused | U | Ready components without BEMGen geometry, the foundation roles among them. |

*Convert2BEM* does not take a construction set; that converter keeps its envelope preset.
