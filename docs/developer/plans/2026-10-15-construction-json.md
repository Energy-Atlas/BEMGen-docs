# Constructions from the atlas's construction JSON, into Convert2IDF (design note)

> **Status:** Done for Parts A to D (D-139, [ADR-021](../decisions/ADR-021-construction-sets-and-mass-ledger.md)), C2 and E1 (D-140, D-141, [ADR-022](../decisions/ADR-022-residential-construction-sets.md)), narrowed by D-142 and D-143 (unified building-scope sets only; E2, assigning detailed rules to zones, dropped; removed slabs written once per face; the solar multiplier checked); merged into `main` and released as `v1.4.0` (D-144). Approved 2026-10-15 (the owner) · **Date:** 2026-10-15 · **Decisions:** D-023, D-064, D-111, D-124, D-126, D-130; new: D-137 (the owner's answers, recorded) · **Branch:** `feature/construction-json` (from `main` `b64805c`) · **Source:** the atlas's handover draft `build/local-plans/bemgen-construction-handover.md` (local to the atlas, not tracked; dated 2026-10-15)

This is one stage run as D-111 sets out: this note first; one test-first build; a review of the diff by a second agent; the headless Rhino check, because a component changes; `scripts/verify.ps1` before the merge; a decision-log entry, and an ADR at the build, because the stage changes what a converted building's envelope is made of.

**Stop line.** The build ends with the branch verified, reviewed, and its documentation synchronised. It does not merge, tag, push, or release.

## Problem

The envelope of every converted building comes from an *Envelope Preset*: one layered construction for each of seven roles, one simple glazing, and the building's infiltration. Its values are illustrative (D-023). The atlas now publishes constructions as JSON, in two separate kinds of document:

- **Unified.** One equivalent recipe for each envelope semantic of a context (building type, standard, climate zone), with precomputed weights.
- **Detailed.** The source model's construction rules, which pick a recipe by source program, storey, boundary, and opening.

Programs already come from the atlas's program JSON through *Program JSON* (D-126). Constructions should come in the same way, and reach *Convert2IDF*.

`EnvelopePreset` cannot hold either document. It needs exactly one construction for each role and a ground floor, and `Layer` has only thickness, conductivity, density, and specific heat: no massless layers and no absorptances. *Convert2IDF* also falls back to the Example envelope when a connected envelope fails (`ComponentSupport.EnvelopeOrExample`).

## The owner's answers (2026-10-15)

1. **Scope: constructions only.** This stage imports construction JSON and connects it to *Convert2IDF*: unified first, detailed after it. Program JSON v3 (the handover's task D) and test-suite wiring (task G) are not part of it, and neither is *Convert2BEM*.
2. **Ground.** The atlas's constructions have no ground floor. Ground surfaces take the Example envelope's ground floor, with no new input. The ground-temperature rule (D-130) is unchanged.
3. **Mass residual.** When the explicit capacity of the geometry already exceeds the atlas's reference budget for a family, the added mass for that family is zero, explicit mass is kept as it is, and a warning records the overshoot.
4. **Fixtures.** The limited packet the atlas prepares (the two construction schemas and the pilot detailed/unified pairs, with their manifest and notices) may be committed byte for byte, like the program JSON 2.0.0 fixtures. Nothing else from the atlas.

## Design (from the handover, narrowed by the answers)

### Part A: fixtures

`tests/Lod.ConstructionJson.Tests/Fixtures/` holds the packet as delivered, with a README recording the atlas commit, each file's SHA-256 and byte count, and the notices. Detailed and unified documents are paired by identical context ID; the historical 4A detailed Medium Office example is not paired with a 3B unified one.

### Part B: physical types and the IDF writer (`Lod.Core`, `Lod.Export`)

- Typed layers: massive (`Material`) and massless (`Material:NoMass`, real resistance, no capacity; never a thin massive layer), with roughness and thermal, solar, and visible absorptance. Air gaps without mass.
- Glazing: simple glazing with an explicit VT-autocalculation mode, and detailed glazing with gas layers, several window constructions when the geometry uses them.
- Only used objects are written, deduplicated by stable identity, with IDF names of at most 100 characters; conflicting identities are rejected.
- The existing `EnvelopePreset` path keeps working through adapters, and its snapshots do not change.

### Part C: the library and unified binding (`Lod.ConstructionJson`, new)

- Depends on `Lod.Core` and JsonSchema.Net, like `Lod.ProgramJson`; no RhinoCommon or Grasshopper. It reuses the strict reader's rules: bounded size and depth, no duplicate keys or non-finite numbers, an input SHA-256, then the embedded schema, dispatched by kind and version.
- Checks beyond the schema: resource closure, ID equality, SI units, component status, finite physics, layer order, normalised contributions. A not-applicable component is not a zero material; a component the geometry needs but the set lacks blocks conversion.
- A construction binding service in `Lod.Core`, format-independent: per-surface and per-window assignments, the material registry, infiltration, the added-mass plan, and a report of what was used and not used.
- **Infiltration:** `natural_ach` in 1/s times 3600 gives air changes per hour, applied once to each zone's volume through `ZoneInfiltration`, with a constant schedule.
- **Mass ledger:** physical wall and slab pairs counted once, multipliers applied once, BEMGen's removed slabs, the atlas's additional mass, and the reference budgets scaled to the counted floor area. Missing wall capacity goes to `InternalMass`, missing floor capacity to `FloorDistributedMass`. A negative residual is clipped to zero with a warning (answer 3).
- **Ground:** ground surfaces get the Example envelope's ground floor (answer 2), and provenance records that this construction is BEMGen's, not the atlas's.

### Part C as built from the packet (unified documents; added 2026-10-15)

The packet made Part C concrete. This section replaces the Part C bullets above wherever they differ.

- **Types in `Lod.Core.Envelope`.**
  - A `ConstructionSet` holds the source, one `RoleConstruction` per `ConstructionRole` and for the window, the mass data, the window's incident solar multiplier, and the infiltration.
    - A `RoleConstruction` is `Provided` (a construction from the set), `NotApplicable`, or `Blocked`, each with the atlas's reason.
    - The infiltration is `natural_ach` × 3600 air changes per hour, always on.
    - A set can also be made from a plain `EnvelopePreset`, with every role provided and no mass data, so there is one writer path.
  - `ConstructionSet.Resolve(used roles, has windows)` gives an `EnvelopePreset` for the roles the building uses:
    - a `NotApplicable` role takes the Example's construction, recorded as a warning (D-138);
    - the ground floor is always the Example's (D-137), recorded as information;
    - a `Blocked` role is an error.
  - **Role mapping.**
    - `ExteriorWall` → ExteriorWall, `ExteriorRoof` → Roof, `ExteriorFloor` → ExposedFloor, `InteriorWall` → InteriorWall, `InteriorFloor` → InteriorFloor, whose ceiling side is the reverse, as the atlas's paired-surface policy says.
    - BEMGen's `InternalMass` role is a removed slab, so it takes the `InteriorFloor` recipe.
    - `ExteriorWindow` → the window.
    - `InteriorCeiling` is not used: every ceiling between storeys in BEMGen is the other side of a floor, interzone or adiabatic.
    - Doors, skylights, tubular devices, interior windows, and shading have no geometry in BEMGen and are listed as unused in provenance.
  - `EnvelopeValues` gains `AdditionalConstructions`: constructions written only when used (the added masses). They are checked with the rest for names.
- **Mass ledger (`Lod.Core.Conversion.ConstructionMassAccounting`).** Counted floor area is Σ zone floor area × multiplier; BEMGen has no attic or plenum. Each physical surface is counted once:
  - **Represented wall capacity:** Σ over interior walls of area × multiplier × C, halved because each wall between zones appears once from each side.
  - **Represented floor capacity:** Σ over floor-side interior floors of area × multiplier × C, plus each removed slab's area × multiplier × C, once. This applies the atlas's rule not to double a slab with two exposed faces; the writer still writes those faces as before (D-031).
  - **Budgets:** each family's Σ `capacity_per_counted_floor_area` × counted area.
  - **Added mass per m² of floor, applied to each zone's floor area as an `InternalMass` of that zone:**
    - furnishings at the atlas's `InternalMass` quantity, with its recipe;
    - missing wall capacity ÷ the interior wall's C, with the interior wall's recipe;
    - missing floor capacity ÷ `FloorDistributedMass`'s C, with its recipe.

    A negative residual adds nothing and is a warning with the overshoot (D-137). The total added is exactly the rate × counted area.
  - Every operand goes into provenance.
- **Writer.** `IdfWriter.Write` and `Convert2Idf.Run` take a `ConstructionSet`; the `EnvelopePreset` overloads wrap one.
  - It adds the mass `InternalMass` objects and a `SurfaceProperty:IncidentSolarMultiplier` for each window when the set has one.
  - The header records the set's source, each role's source, and the ledger.
- **Library `Lod.ConstructionJson`.** It depends on `Lod.Core`, `Lod.ProgramJson`, and JsonSchema.Net, reusing Program JSON's strict reader, which becomes public with the document's name in its messages.
  - It embeds the unified schema 1.1.0 byte for byte. A detailed `construction_set` is reported as not yet supported (Part E).
  - **Checks beyond the schema:**
    - the document status is `ready`;
    - every `ready` component's assembly exists and is `ready`;
    - units are SI as declared;
    - layer models are `Material` or `Material:NoMass` for opaque assemblies, and `SimpleGlazing` for the window;
    - an opaque assembly with one layer has equal faces;
    - solar modifiers are only a constant incident solar multiplier;
    - each layer's values pass Part B's checks.
  - **Naming.** Layers are named `{assembly id} L{n}`, constructions by assembly ID; a window without VT leaves it to EnergyPlus.

### Part D: Grasshopper

- A new *Construction JSON* component (`CJson`): JSON text in, as with *Program JSON*; a construction set, its source, and its reports out. New GUIDs and an icon motif.
- *Convert2IDF* gains an appended, optional *Construction* input; its GUID and port indices stay. Connecting both *Construction* and *Envelope* is an error. A failed connected *Construction* blocks the IDF and never falls back to the Example envelope; *Override* does not cover it.

### Part E: detailed assignment (after the unified path works)

*Dropped by D-142 (2026-10-16): BEMGen converts only unified building-scope sets, and detailed documents are read as evidence and never converted. The text below is the original plan.*

A typed binding context carries the source program, scope, and storey identity through `IFloor.Mapping` and `IGeneratedBuilding.Sources`. Matching uses exact source identifiers and the source's precedence (space type, then storey, then building default). Where rezoning loses the face-to-program relation, resolution fails with an ambiguity error, and the unified document is the explicit alternative; detailed candidates are never blended.

## Open before approval

- **The packet.** Not prepared yet; Part A and every end-to-end test wait for it. The JSON shapes in this note come from the handover, not from the schemas.
- **ADR.** The binding service and the mass ledger get an ADR at the build.
- **Names.** `Lod.ConstructionJson`, `ConstructionSetPreset`, and the component name are the handover's proposals.

## Build log

### 2026-10-15: Part B, typed layers and the IDF writer

The owner approved this note and asked for Part B first, since it needs no packet.

- **Types (`Lod.Core.Envelope`).**
  - `OpaqueLayer` is an abstract record with three kinds: `Layer` (massive, unchanged positional values), `NoMassLayer`, and `AirGapLayer`. It gives `ThermalResistance` and `HeatCapacity` per m², and `Construction.HeatCapacity` sums them for the mass ledger of Part C.
  - `Layer` and `NoMassLayer` carry a `SurfaceFinish`: optional roughness and thermal, solar, and visible absorptances.
  - The window is a `WindowGlazing`: `GlazingSpec`, now with an optional visible transmittance, or `LayeredGlazing` of `GlassLayer` (spectral average) and `GasLayer` (air, argon, krypton, xenon). `ExampleEnvelopePresets.Glazing` gives the example's simple glazing a static type.
- **Checks.** The ranges come from the EnergyPlus 26.2 IDD:
  - a massless resistance of at least 0.001;
  - thermal absorptance in (0, 0.99999];
  - optics in [0, 1], with transmittance plus reflectance at most 1;
  - infrared transmittance plus emissivity below 1;
  - 1 to 4 glass layers, alternating with gas, glass on both sides.

  An air gap as the outside or inside layer is a `ConstructionLayers` error. EnergyPlus 26.2 rejects it: a copy of the test IDF with the gap moved outside stops with "Outside Layer is Air".
- **Writer (`Lod.Export`).**
  - New objects: `Material:NoMass`, `Material:AirGap`, `WindowMaterial:Glazing` (`SpectralAverage`, written up to its conductivity), and `WindowMaterial:Gas`.
  - `Material` gains the absorptances, written up to the last one given.
  - A simple glazing without VT leaves the field out.
  - The legacy path writes the same text: no snapshot changed.
- **Decisions taken in the build (controller, Provisional).**
  - **Finish on both faces.** A finish applies to both faces of a layer, and the IDD's inside-face absorptances are not written. A layer's outside face becomes the inside face in a reversed construction, so distinct faces would need a reversed material copy. Part C revisits this if the atlas gives distinct faces.
  - **Air gaps.** An air gap has no finish.
  - **Out of Part B.** Glass optical data types other than `SpectralAverage`, gas mixtures, and custom gases are not supported. A preset still has one window; several window constructions, one per opening, come with the binding of Part C, because choosing among them is binding.
- **Tests.** `LayerKindsTests` (Core, 23 cases) and `IdfMaterialKindsTests` (Export, 7, read back from the IDF text). `IdfChecks` accepts the new material classes as construction layers.
- **Checks run.**
  - The three new IDFs pass the IDD check against 26.2 with 0 problems.
  - `eplus-check` with EnergyPlus 26.2 and the Golden TMY3 weather: 3 of 3 pass, 0 warnings.
- **Found on the way.** `TestSuiteGenerator.Tests` failed one test in this worktree: `SuiteWorkspace.NoteExample` is a raw string literal, so its line endings follow the checkout's. With `core.autocrlf=true` it is CRLF, and a replacement spanning `\n` misses. The test now normalises the string to LF. Every Windows clone with `autocrlf` would have failed, the fresh-clone gate included.

### 2026-10-15: Part A, the packet, and what it changes

**Part A.** The atlas delivered packet `bemgen-construction-7693e08-v1`, prepared from atlas commit `7693e08`. Its manifest matches `manifest.sha256`, and all 18 files match their manifest SHA-256 and byte counts, with no unlisted file.

- It is copied whole into `tests/Lod.ConstructionJson.Tests/Fixtures/packet/`, about 4.9 MB, most of it the three detailed examples.
- The folder is `-text` in `.gitattributes`, and `git ls-files --eol` shows LF kept.
- `PacketTests` repeats the hash checks and checks that each pair shares its context, climate, reference, and infiltration.
- The fixture README records the source and D-137.

**What the documents show** (unified 1.1.0, read from the packet; the detailed 2.0.0 shape matters only for Part E):

1. **Opaque assemblies.** Each is two massive layers and one massless layer, or a single massless layer. Layers have no names, so BEMGen names them from the assembly ID. Every value Part B checks is within its ranges.
2. **Surface properties are per face of the assembly**, `exterior` and `interior`, not per layer. Mapped onto Part B, the outside layer takes the exterior face and the inside layer the interior face; a reversed construction then shows each physical face where it really is. No assembly in the packet has a single layer with different faces; such an assembly would need the IDD's inside-face fields and is an error until one appears.
3. **Glazing.**
   - The exterior windows are simple glazing.
   - The residential window has no VT, only `energyplus_autocalculate_from_shgc`, which Part B's optional VT covers.
   - The residential window also has a solar modifier, `SurfaceProperty:IncidentSolarMultiplier` 0.8276, which Part C writes for each window.
   - Detailed glazing appears only on tubular daylighting devices, which BEMGen does not model.
4. **Components BEMGen has no geometry for** (doors, glass doors, overhead doors, skylights, tubular devices, interior windows, shading) are reported as unused, not errors.
5. **Mass.** BEMGen's `InternalMass` role (removed slabs) and the atlas's `InternalMass` (additional furnishings) differ.
   - Removed slabs are physical slabs, so they take the `InteriorFloor` recipe and count as represented floor capacity.
   - The atlas's `InternalMass` is added per zone: its quantity times the zone's floor area.
   - `FloorDistributedMass` takes the residual of `physical_capacity_budgets`, which can list several source assemblies per family; they sum.
6. **The residential pair has no interior walls, interior floors, or exposed floors.** Its source is a single-family detached house, so those components are `not_applicable` (`source_absent`). Yet every BEMGen residential plan has walls and slabs between zones. Under the handover's rule, a component the geometry needs but the set lacks blocks conversion, so the pair would block every BEMGen residential building. This is the owner's question, below.

Items 2 to 5 are controller choices (Provisional). Item 6 waits for the owner.

### 2026-10-15: Part C, unified documents (`d649a72` to the commit of this entry)

D-138 settled the fallback: a role the set lacks takes the Example's construction, with a warning.

- **Refactor in `Lod.ProgramJson`.** `StrictJson` is public, with the document's name in its messages. Its schema evaluation moved into a public `EmbeddedJsonSchema`, which `ProgramJsonSchema` now wraps. The program JSON tests are unchanged and pass.
- **Core.**
  - `ConstructionSet` with `RoleConstruction`, `WindowConstruction`, `SetMass`, and `Resolve`.
  - `EnvelopeValues.AdditionalConstructions`.
  - `ConstructionMassAccounting` and `MassPlan`.
  - New codes: `ConstructionFromExample`, `GroundConstructionFromExample`, `ConstructionBlocked`, `MassOverBudget`, `MassNotAdded`, and `NoMassBudget`.
- **Writer.** `IdfWriter.Write` takes a `ConstructionSet`, and the preset overloads wrap one. Added masses are one `InternalMass` per kind and zone, the solar multiplier one `SurfaceProperty:IncidentSolarMultiplier` per window, and the header gains the set's lines. Every snapshot is unchanged, and a test checks that a preset written as a set gives the same text.
- **Library `Lod.ConstructionJson`.** It embeds the unified schema 1.1.0 byte for byte (a test compares it with the packet's copy), and its `ConstructionJsonImporter` maps a document as set out above.
- **Tests.**
  - `ConstructionSetTests`: 10 Core cases.
  - `ImporterTests`: 27, on the packet's documents and mutations of them.
  - `IdfConstructionJsonTests`: 340, each of the three documents on the linear plan through every simplifier, aggregator, and heat-transfer setting. Each family's represented capacity plus the capacity added for it meets the budget, read back from the IDF text. The rest cover the fixed air changes, the residential fallbacks and solar multipliers, a blocked role, and the legacy text.
  - `IdfChecks` now tells removed slabs from added masses by name.
- **IDD and EnergyPlus.** 168 IDFs, 0 IDD problems, and all 168 ran in EnergyPlus 26.2 with no severe error and no unexpected warning.
  - The IDD lists `SurfaceNames` for the window that `SurfaceProperty:IncidentSolarMultiplier` names. EnergyPlus's own example file names windows there, and EnergyPlus runs it.
  - `idd_check.py` therefore gains `EXTRA_OBJECT_LISTS`, one entry with that evidence.
- **Decision taken in the build (controller, Provisional).** A family with a zero budget is information (`NoMassBudget`), not the over-budget warning. The residential source has no wall or floor inventory, so every residential conversion would otherwise warn.
- **Findings for the owner.**
  1. **The warehouse's floors exceed their budget in all 56 linear-plan cases.** The source is a one-storey warehouse with little slab capacity per floor area, while the test plan stacks storeys. The medium office's walls exceed it in 16 of 56, the fine zonings with many partitions. In each case D-137 applies: nothing is added and the overshoot is a warning.
  2. **A removed slab is counted once in the ledger, as the atlas asks.** The writer still writes its internal mass with both exposed faces (D-031), so EnergyPlus holds twice its capacity. That predates this stage and is left as it is.

### 2026-10-15: Part D, Grasshopper

- **New.**
  - *Construction JSON* (`CJson`, panel *1 Program*, GUID `b2802511-fee7-49ab-bdcb-9329ce293461`, `ConstructionJsonComponent`): JSON in; *Construction*, *Source*, *Roles*, and *Unused* out.
  - The parameter *Construction Set* (`Cons`, GUID `ef90ede8-f0ff-4495-822b-11c5e61a6fe5`) and `ConstructionSetGoo`.
  - Two icon motifs in `scripts/make_icons.py`: braces around the wall section, and the wall section with its inner layer cut short. Only the two new icons were written.
- **Changed.** *Convert2IDF* (GUID unchanged) gains *Construction* as input 9, appended after *Weather*, so saved definitions reopen with it unset.
  - `ComponentSupport.Constructions` selects the set: connecting *Envelope* and *Construction* together is an error, and so is a connected *Construction* that yields no set. That case never falls back to the Example, unlike *Envelope*, whose old fallback is unchanged.
  - The provenance says `CONSTRUCTION SET:` instead of `ENVELOPE:`.
  - The plugin references `Lod.ConstructionJson`.
  - The descriptions of *Envelope Preset*'s parameter now say "glazing", not "simple glazing".
- **Controller choices (Provisional).** *Construction JSON* sits in panel *1 Program*, next to *Program JSON*, the other atlas importer. *Convert2BEM* takes no construction set (answer 1).
- **Headless Rhino** (`scripts/rhino-smoke`, Rhino 8, results `D:\BEMGen-smoke\construction-json-all`): all 17 specs ran to the end with no failed check.
  - The new spec `construction-json` has 6 scenarios and 12 checks, with the three error scenarios ending in their expected errors.
  - `examples` reopened 20 of 20 definitions with *Validate* True. Each was saved before *Construction* existed.
- **For a person.** The look of the two icons in the editor, and wiring a Panel with a 1.5 MB detailed document (the error path only).
- **Review (second agent, read only).** No bug found. It verified:
  - the GUIDs, unchanged and unique;
  - the thin adaptors;
  - the selection rules;
  - the appended-parameter read for definitions saved with 8 or 9 inputs;
  - the smoke spec's IDF field indices and its guards against passing on empty lists;
  - the packaging, which copies every DLL.

  Fixed:
  - The two descriptions said the ground takes the Example's "with a warning"; it is a remark.
  - The smoke check of the ground's remark now matches its code.
  - `convert2idf.md` says *Override* does not cover a failed or conflicting set.
  - `docs/development/grasshopper-smoke-test.md` gains a Construction JSON checklist for a person, with the headless result.

  The `construction-json` spec reran with 12 of 12 checks.

### 2026-10-15: C2, the residential packet (D-140)

The atlas sent packet v2. Its manifest and all 23 files verified. It keeps v1 byte for byte and adds two residential pairs (4A, a two-storey house with a garage; 1A, a two-storey house on a raised floor) and a coverage file. Reading the residential documents' detailed `when` conditions showed that 5A's `ExteriorRoof` covers a vented attic: the importer had put that bare deck (R ≈ 0.25) on conditioned zones, while the insulation (R ≈ 5.3) was in the unused `InteriorCeiling`. The owner's answers are D-140.

- **Fixtures.** Packet v2 is pinned in place of v1 (`PacketTests` checks the packet ID and the five pairs). The Export tests link every unified document, so the zoning matrix now covers five documents.
- **Opt-in fill.** `ConstructionSet.Resolve` takes `fillFromExample`, default false: a role or window the building needs but the set lacks is the error `ConstructionMissing`, which names the role and the three ways out (another zoning, another set, *Fill From Example*). `IdfOptions.FillFromExample` and *Convert2IDF*'s appended input 10, *Fill From Example*, pass it. The header records it.
- **Approximations.** `RoleConstruction` gains `Approximation` (a used role warns with `ConstructionApproximation`, and the role's header line shows it) and `AdiabaticInSource`.
- **Residential rules in the importer**, read from the `whole_dwelling` scope since the unified document has no space types:
  - With `InteriorCeiling` and `ExteriorRoof` ready, the roof role is the attic ceiling's layers, named `{ceiling id} as roof L{n}`, with the source roof's exterior surface properties on its outside layer, and an approximation; the ceiling is no longer listed as unused.
  - The interior wall carries the garage-wall approximation.
  - The interior floor is flagged `AdiabaticInSource`; the writer warns `AdiabaticSourceConducted` when floor heat transfer is on.
- **Tests.**
  - Core: 4 new `ConstructionSetTests` (the default error for a role and for the window, the ground without fill, an approximation's warning); the two fallback tests now pass `fillFromExample: true`.
  - Importer: 4 new tests (the 5A attic roof against the ceiling's targets and both faces, a commercial set unchanged, the 4A caveats and budgets, the 1A exposed floor and missing wall), and the import theory covers all five documents.
  - End to end, kept apart from parsing: the zoning matrix of five documents with fill on; without fill, 5A on the linear plan is `ConstructionMissing`, 5A converts one storey of one zone with its attic-ceiling roof, 4A converts the linear plan and warns only with floor heat transfer on, and 1A converts storeys of one zone each.
- **Checks.**
  - 284 IDFs, 0 IDD problems; all 284 ran in EnergyPlus 26.2 (Golden TMY3) through `eplus-check`: 284 passed.
  - The `construction-json` spec: 8 scenarios, 18 checks, the four error scenarios ending in their expected errors.
  - `scripts/verify.ps1` passed on `889b250`.
- **Controller choices (Provisional).** The detection rules above; the attic roof's outside face takes the roof deck's exterior surface; the commercial `InteriorCeiling` stays unused.

### 2026-10-15: the review of E1 (second agent, read only)

Verdict: not approved, for one bug and five risks, all in `DetailedReader`, and all fixed. The core requirements held: all five documents parse, parsing is kept apart from assignment, the conditions survive, and no path converts a detailed set or fills it from the Example.

1. **Bug.** A schema-valid layer `order` of `0.0` or above the 32-bit range threw an exception. It is now the error `InvalidStructure` at the layer's pointer (tested with both values).
2. **Unusual alternatives.** Unsupported physics anywhere failed the whole document, against "do not reject sparse source-faithful documents". Such an assembly is now kept with `Unsupported` and no construction, with the warning `AssemblyNotSupported`; only malformed structure is an error. Orders may be sparse; repeated orders are an error. Tested with dirty glass, physics out of range, and sparse and repeated orders.
3. **Dropped data.** Each assignment's evidence IDs, area convention, interstorey area rule, paired flag, and threshold, the roof film rule, the infiltration method and evidence, and the whole metadata with its selection receipt are now kept. Checking the receipt against the assignments is left to E2.
4. **Cross-kind assignments.** A component's surface type is now checked against its assembly's model (`InvalidStructure`); the rule holds for every assignment in the packet.
5. **Malformed overhangs.** They are the warning `EvidenceNotRead`.
6. **The unified overhang tolerance.** It now has a test.
7. **Nits.**
   - Error pointers use the array index.
   - The dead fallback is removed.
   - Structural problems have their own code, `InvalidStructure`.
   - The detailed Source keeps the infiltration method and evidence.
   - *Construction JSON*'s message about a detailed document is a warning, so it is not missed on the canvas.
   - The docs are corrected: the overhang wording, five documents, and the AirGap and Gas property names marked as assumed.
   - New tests: layers out of array order, a `with` copy of a detailed set, the exact multiplier, and the kept overhang and roof pitch.

`DetailedImporterTests` now has 28 cases. The `construction-json` spec: 8 scenarios, 22 checks, including 4 on the detailed document.

### 2026-10-15: the review of C2 (second agent, read only)

The verdict was not approved, for one bug, which is fixed.

- **Bug.** `AdiabaticSourceConducted` fired with floor heat transfer on even where *Stacked Floor Zone Multiplier* writes every floor between storeys adiabatic. It now fires only when at least one floor is written interzone, and a test covers the zone multiplier case.

Also fixed:

1. **The wall-mass case.** A missing interior wall needed only for wall mass now says so in its error, through the new `needs` argument of `Resolve`. The garage-wall caveat mentions the walls' mass.
2. **The 4A floor.** It is a blend of adiabatic floors between storeys (about 92.5%) and the floor to the garage, so the warning now says "mostly or wholly" adiabatic. The removed-slab role is copied before the caveats, so it carries none (tested). D-140's wording, "adiabatic source floors", stands, read as "mostly adiabatic".
3. **Messages and docs.**
   - A one-layer attic ceiling gets its own `FacesDiffer` wording.
   - The XML docs of `ConstructionStatus.NotApplicable`, `Resolve`, and the importer are brought up to date.
   - `convert2idf.md` says five documents.
4. **Visibility and tests.**
   - The unified `RoleLines`, the *Roles* output, show approximations and "(adiabatic in the source)".
   - The zoning matrix asserts that the commercial documents never rely on *Fill From Example*.
   - A missing internal mass role is named "the removed slabs".

The reviewer ran 6 residential IDFs in EnergyPlus 26.2, and all passed with no warnings. The smoke spec was not part of the review; it runs at the close-out.

### 2026-10-15: E1, detailed documents read (D-140)

- **Library.**
  - `DetailedConstructionDocument` and its records: component, assignment, condition, overhang, assembly.
  - `DetailedReader` (internal).
  - The detailed schema embedded byte for byte.
  - `ConstructionJsonImporter.Import` dispatches on `kind` and `schema_version`. The import gains `Detailed` and `RoleLines`, the latter also for unified documents, so the component no longer formats roles itself.
  - `ConstructionSet.AssignmentUnavailable` and the code `ConstructionAssignmentUnavailable`.
- **Found on the way.**
  - The detailed residential windows carry their source overhang as an `overhang_geometry` solar modifier.
  - The detailed reader keeps it as evidence (`DetailedAssembly.SourceOverhang`) and never applies it, as the contract says.
  - The unified reader accepts it beside the multiplier but does not keep it; the packet's unified documents do not have it.
- **Grasshopper.**
  - *Construction JSON* reads a detailed document with a remark and lists its components and conditions in *Roles*.
  - *Convert2IDF* refuses the set with the actionable error.
  - The descriptions say so.
- **Tests.**
  - `DetailedImporterTests`, 18 cases:
    - all five detailed documents read, counted against the JSON;
    - a pair's context and air changes match;
    - absent components, the garage conditions, the attic conditions, and the source reversal flag are kept;
    - materials keep their layer order and finishes;
    - windows keep their glazing, multiplier, and overhang;
    - the set's error names the unified document;
    - four mutations fail: a missing material, a missing assembly, a provided component without assignments, a schema violation;
    - the embedded schema matches.
  - End to end: a detailed set is the single error `ConstructionAssignmentUnavailable`, even with *Fill From Example*.
  - The smoke spec's detailed scenario checks the conversion error; the review's fixes add checks of *Construction JSON*'s message and *Roles*.
  - All ten packet documents parse.

### 2026-10-15: the review of Part C (second agent, read only)

Verdict: not approved until two problems were fixed. The ledger's arithmetic, the face mapping under reversal, the fallbacks, and the EnergyPlus runs were found correct. Every finding is fixed:

1. **Blocked mass recipes were dropped silently.** `SetMass` now carries `FurnishingsBlocked` and `FloorDistributedMassBlocked`, and the ledger makes them `ConstructionBlocked` errors: furnishings always, floor mass where floor capacity falls short.
2. **A `with` copy of a preset's set kept the link to the preset**, so the changes were ignored and its added mass went unrecorded in the header. A private copy constructor drops the link.
3. **The wall-transfer recipe could be the Example's without a word.** It could also come from a blocked role on a building without interior walls. The writer now adds the interior wall role when wall mass is added and resolves again. The ledger also now prices removed slabs with the internal mass role's construction, the one the writer writes.
4. **A missing budget list read as zero.** It is now an error; an explicit empty list stays zero. The importer also checks `paired_face_area_policy`, `mean_zone_weighted_faces`, the convention the ledger implements.
5. **The ledger's only test shared its rules.** `ConstructionMassAccountingTests` (10 Core cases) now checks the ledger on a hand-built bar against hand-computed values:
   - a stack, the zone multiplier, and one zone with removed slabs;
   - a shortfall of exactly zero, a zero budget, and a missing recipe;
   - blocked furnishings, and a blocked floor mass.
6. **Nits.**
   - The circular test of the preset path is removed; the unchanged snapshots guard it.
   - The added-mass names are `IdfDefaults` constants, and the importer's status strings are constants.
   - The end-to-end tolerance is `RelativeLoad`.
   - A misnamed test is renamed.
   - The note now matches `Convert2Idf`, the importer count is corrected, and the IDD-check record is back in date order.
   - A note in `convert2idf.md` records that the ledger reads the building's areas, which can differ from the IDF's where the writer drops slivers.

New tests also cover a blocked furnishing and a blocked interior wall on a building without interior walls, both end to end, and a changed copy of a preset's set.

**Open (not checked):** whether EnergyPlus applies the incident solar multiplier when its schedule field is blank. The 168 runs completed without errors, but transmitted solar was not compared with and without the multiplier.

### 2026-10-15: the review of Part B (second agent, read only)

Verdict: approved, with no correctness bug. Fixed:

1. **Specific heat.** A massive layer's specific heat must now be at least 100 J/(kg·K), the IDD minimum (`Layer.MinimumSpecificHeat`); smaller values used to pass. The reviewer confirmed that EnergyPlus 26.2 stops on 50. This tightens a check that predates the stage; the example and every test layer are above it.
2. **`Hvac` comment.** Its summary is back on `Hvac` instead of on the new `Material` helper.
3. **Window constructions.** The deferral of several window constructions to Part C is now recorded above.
4. **Hash.** `LayeredGlazing.GetHashCode` no longer throws on a null name.
5. **Ambiguity message.** It now says a simple glazing's name counts as both a material and a construction; a layered window's name is a construction name only.
6. **Tests added.**
   - absorptances partly given (blank fields before the last one given), and a massless layer with absorptances;
   - a building without windows, which writes none of a layered window's materials;
   - glass and gas names that are not valid IDF names.
7. **Docs.** `pipeline.md` names the new types.
8. **Label.** The envelope's label formats the U-factor and SHGC in the invariant culture, like the VT.
9. **Roughness.** `IdfDefaults.Roughness` is `nameof(SurfaceRoughness.MediumRough)`, so the default is defined once.

The reviewer also ran two cases in EnergyPlus: glass whose solar transmittance and reflectance sum to exactly 1, and two adjacent air gaps. Both completed without warnings, so the `> 1` rule stands and no check is added for adjacent gaps.

**Checks.** The five IDFs of `IdfMaterialKindsTests` pass the IDD check against 26.2 with 0 problems, and `eplus-check` passes 5 of 5 with 0 warnings.

### D-142 and packet v3 (2026-10-16)

The owner answered the E2 note's questions (D-142) and sent packet v3. The build is on `feature/construction-json` (commits `3d7830b`, `288b486`, `dbc5eb6`); the decision is D-143.

- **Packet v3.** It is pinned in place of v2 (`bemgen-construction-7693e08-v3`, manifest SHA-256 `57a71b7c…`): seven pairs, v2's five byte for byte, plus `midrise-apartment-2019-3B` (scope `building`) and `residential-apartment-unit-1990s-4A` (scope `whole_dwelling`). The midrise apartment's unified set has the medium office's shape, with its `InteriorWindow` not applicable (`source_reference_zero_exposure`), and converts the linear plan on every zoning without *Fill From Example*.
- **D-142 in code.**
  - A unified document whose `scope` is not `building` is the error `ConstructionJsonScopeNotSupported` (subject `/scope`). The packet's four single-dwelling sets are refused; their detailed documents are still read.
  - The residential rules of D-140 are removed: the attic ceiling as the roof, the garage-wall caveat, the adiabatic-source floor warning, the diagnostics `ConstructionApproximation` and `AdiabaticSourceConducted`, and `RoleConstruction.Approximation` and `AdiabaticInSource`. `InteriorCeiling` is always listed as unused.
  - A detailed document is still read (E1) and is refused at conversion with `ConstructionAssignmentUnavailable`, whose message now says that BEMGen converts only unified building-scope documents.
  - *Fill From Example* (input 10) stays, for a role a building-scope set marks not applicable; the ground still takes the Example envelope's construction.
- **Removed slabs (D-143).** `Construction.Sliced(faces)` in `Lod.Core`; *Convert2IDF* writes each removed slab as an `InternalMass` of area slab area × 2 with the construction `{name} Half` (massive layers at half thickness, massless layers and air gaps at half resistance), so the IDF holds the slab's heat capacity once, as the mass ledger counts it. A slice whose massless layer would fall below 0.001 m²·K/W is the error `EnvelopeValue`, naming the layer. This is exact for a symmetric slab and an approximation for an asymmetric one. *Convert2BEM*'s *Internal Mass* output is unchanged. Two IDF snapshots changed.
- **Solar multiplier checked.** In EnergyPlus 26.2, the 5A set's transmitted solar with and without its multiplier was in the ratio 0.8276, so the open item of the Part C review is closed; an end-to-end test now checks that every window gets the set's multiplier.
- **Checks.**
  - After the change all test projects pass with plain `dotnet test`: `Lod.Core.Tests` 681, `Lod.Export.Tests` 1737, `Lod.ConstructionJson.Tests` 73, `Lod.Integration.Tests` 2726, the others unchanged.
  - The 168 construction IDFs of the Export matrix (medium office, warehouse, and midrise apartment, every zoning, heat transfer on and off, no *Fill From Example*) had 0 IDD problems.
  - 11 of them (the single-zone ones, which hold half slabs, and the midrise apartment on *Stack Floors*) passed `eplus-check` in EnergyPlus 26.2 with no unexpected warning.
- **Deferred by the owner:** Program JSON v3, the test-suite generator's construction input, and *Convert2BEM* with construction sets.
