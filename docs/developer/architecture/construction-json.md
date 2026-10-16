# Construction JSON

> **Status:** Provisional (the controller's realisation of D-137, D-138, and D-140 to D-143, pending the owner's reading) · **Component:** *Construction JSON* (`CJson`), panel *1 Program*, GUID `b2802511-fee7-49ab-bdcb-9329ce293461` · **Parameter:** *Construction Set* (`Cons`), GUID `ef90ede8-f0ff-4495-822b-11c5e61a6fe5` · **Design note:** [2026-10-15-construction-json](../plans/2026-10-15-construction-json.md)

## Purpose

The Energy Archetype Atlas publishes the constructions of a building context as JSON, in two kinds of document:

- the **unified** `building_level_equivalent` 1.1.0: one assembly per envelope semantic;
- the **detailed** `construction_set` 2.0.0: the source model's assignment rules.

BEMGen converts only the unified document, and only one of the whole-building scope (`building`, such as the office, warehouse, and apartment prototypes); a single-dwelling set (scope `whole_dwelling`) is refused ([scope](#scope), D-142). It reads the detailed document with every rule and condition, as evidence, and never converts it ([below](#detailed-documents)).

As with *Program JSON*, BEMGen reads only the JSON **text**: no file path and no network. The schema is embedded byte for byte in `src/Lod.ConstructionJson/Schemas/`. The pinned packet of seven documents per kind (v3, D-143) is in `tests/Lod.ConstructionJson.Tests/Fixtures/packet/` (D-137).

`Lod.ConstructionJson` depends on `Lod.Core`, on `Lod.ProgramJson` for its strict reader and embedded-schema evaluation, and on the JSON Schema library. It never references RhinoCommon or Grasshopper.

## From the JSON to a construction set

`ConstructionJsonImporter.Import(text)` reads the text strictly (UTF-8 without a BOM, no duplicate members, finite numbers), checks it against the schema, and then against the contract's rules. Every problem is reported, with its JSON Pointer as subject. The result is a `ConstructionSet` (`Lod.Core.Envelope`):

| JSON | Construction set |
| --- | --- |
| `ExteriorWall`, `ExteriorRoof`, `ExteriorFloor`, `InteriorWall`, `InteriorFloor` | the roles exterior wall, roof, exposed floor, interior wall, interior floor (the ceiling below is its reverse); BEMGen's internal mass role, a removed slab, takes the interior floor recipe |
| a component `not_applicable` or `blocked` | the role not applicable or blocked, with the source's reason |
| the ground | not part of the contract: not applicable (the Example's at conversion, D-137) |
| `Material` and `Material:NoMass` layers | massive and massless layers named `{assembly id} L{n}`, outside first; the exterior surface properties are the outside layer's finish, the interior ones the inside layer's |
| `ExteriorWindow` `SimpleGlazing` | the window's simple glazing; `visible_transmittance_mode` `energyplus_autocalculate_from_shgc` leaves the VT to EnergyPlus |
| `solar_modifiers.incident_solar_multiplier` (constant) | one `SurfaceProperty:IncidentSolarMultiplier` per window |
| `infiltration.natural_ach` (1/s) | × 3600 air changes per hour, always on |
| `InternalMass` with `quantity` | the furnishing recipe and its area per counted floor area |
| `mass_accounting.physical_capacity_budgets` | each family's capacities summed; an empty list is zero, a missing one an error |
| `FloorDistributedMass` | the recipe of unrepresented floor capacity |
| other ready components (doors, skylights, tubular devices, `InteriorCeiling`) | listed as unused; BEMGen has no geometry for them |

The codes are in `ConstructionJsonDiagnosticCodes`; strict-reading errors keep the codes of `ProgramJsonDiagnosticCodes`. Conversion is in [convert2idf.md](convert2idf.md#construction-sets): resolving the set for each building, the mass ledger, and the header lines.

### Scope

Only a unified document whose `scope` is `building` is converted (D-142). Any other scope is the error `ConstructionJsonScopeNotSupported`, with the subject `/scope`, and nothing is made.

- A `whole_dwelling` set describes one dwelling, such as a ResStock house or the packet's apartment unit (`residential-apartment-unit-1990s-4A`). BEMGen's residential buildings are apartment blocks, which take a building-scope apartment set.
- So the residential rules of D-140 are gone: a house's attic ceiling as its roof, the garage-wall caveat, and the warning on an interior floor that is adiabatic in the source (and the diagnostics `ConstructionApproximation` and `AdiabaticSourceConducted`). `InteriorCeiling` is always listed as unused.
- **The apartment set is the residential case.** The packet's `midrise-apartment-2019-3B` has the medium office's shape: every role BEMGen uses is ready, its `InteriorWindow` is not applicable with the reason `source_reference_zero_exposure` (valid, and not listed as unused), and it has budgets, furnishings, and a floor-distributed mass.
- Unconditioned space is unconditioned: no garage or attic category is modelled.
- BEMGen's windows are fixed, and a unified set's window is already resolved by its source's window areas, so operability raises no question.
- *Fill From Example* (*Convert2IDF*) stays opt-in, for a role a building-scope set marks not applicable; the ground is always the Example envelope's (D-137).

## Detailed documents

`ConstructionJsonImporter.Import` reads a detailed `construction_set` 2.0.0 (embedded schema `construction-json-v2.schema.json`, byte for byte) into a `DetailedConstructionDocument` on the import's `Detailed`.

- **What is kept.**
  - Each component, in document order: its semantic, disposition (`Provided` or `SourceAbsent`), target, and assignments.
  - Each assignment: its assembly, its `when` condition (`DetailedCondition`: scope, space type, storey, window operation, interior and exterior space types, boundary), and its source element IDs.
  - Each assignment's geometry instructions: area method, partition area per conditioned floor area, the source reversal flag, roof pitch, and overhang.
- **Assemblies in BEMGen's types.** Each assembly is read into an opaque `Construction` named by the assembly ID, its layers named by material ID, outside first. A window becomes a `GlazingSpec` or a `LayeredGlazing`.
- **Materials.** `StandardOpaqueMaterial` is a `Layer` and `MasslessOpaqueMaterial` a `NoMassLayer`, each with its own surface finish, and clean, non-diffusing `SpectralAverage` `StandardGlazing` is a `GlassLayer`. These are the models the packet's documents use. `AirGap` and `Gas` are read too, but no packet document has one, and their property names (`resistance_m2_K_W`; `gas_type`, `thickness_m`) are assumed, not confirmed by the contract.
- **Solar modifiers.** A constant incident solar multiplier is kept. A window's `overhang_geometry` is kept as evidence (`SourceOverhang`) and never applied, since BEMGen owns geometry.
- **Kept for a later assignment.** Each assignment's evidence IDs, area convention, interstorey area rule, paired-floor flag, and activation threshold, and the roof film rule. The whole `metadata`, as `MetadataJson`, including the selection receipt that an assignment must agree with; it is not checked against the assignments yet.
- **Malformed structure is an error:**
  - an assembly or material key differs from its ID (`AssemblyIdMismatch`);
  - an assignment's assembly or a layer's material is missing (`UnresolvedAssembly`, pointing at the array entry);
  - a layer order is not an integer or repeats;
  - a provided component has no assignments, or an absent one has some;
  - a glazed opening (window, glass door, skylight, tubular device) is assigned an opaque assembly, or anything else a glazing one.

  The last three are `InvalidStructure`. Orders need not be contiguous.
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
| 1 | Source | Src | The JSON's identity and SHA-256, its detailed context, climate zone, reference, and infiltration. |
| 2 | Roles | R | Unified: each role and the window, with its assembly, or its status and reason. Detailed: each component, with its disposition and every assignment's assembly and condition. |
| 3 | Unused | U | Ready components without BEMGen geometry. |

*Convert2BEM* does not take a construction set; that converter keeps its envelope preset.
