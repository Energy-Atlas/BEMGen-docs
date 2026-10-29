# ADR-023: Native ground methods and construction packet v7

Status: Accepted (the owner's decisions of 2026-10-18, D-145); the controller's realisation (D-146) is Provisional, pending the owner's reading.

Date: 2026-10-18

Decisions: D-023, D-064, D-111, D-130, D-137, D-142, D-143, D-145; new: D-146. Refines [ADR-021](ADR-021-construction-sets-and-mass-ledger.md) (its decision 2, the ground, no longer holds for a packet v7 set) and keeps [ADR-022](ADR-022-residential-construction-sets.md)'s D-142 scope.

Design note: [2026-10-18-construction-foundation-v7.md](../plans/2026-10-18-construction-foundation-v7.md), build logs "Part A" to "Part D" and "Review fixes" · Architecture: [construction-json.md](../architecture/construction-json.md#foundation-and-ground-data), [convert2idf.md](../architecture/convert2idf.md#native-ground-of-a-construction-set-d-145) · Atlas source: the packet `bemgen-construction-foundation-v7` in `tests/Lod.ConstructionJson.Tests/Fixtures/packet/` (its `HANDOVER.md` and `reference/` contracts)

## Context

BEMGen pinned the atlas's packet v3 (D-143): unified 1.1.0 and detailed 2.0.0 documents with no ground. A construction set therefore took the Example envelope's ground floor (D-137), and every ground surface had ground temperatures of indoor minus 2 °C (D-130).

The atlas has since published packets v4 to v7, which BEMGen never imported:

- v4 is the shared mass contract 1.0.0.
- v5 and v6 add foundations and ground: four roles (`GroundFloor`, `FoundationWall`, `FloorOverFoundation`, `RimJoist`), a `foundation_ground` section with four methods (`FFactor`, `CFactor`, `LayeredGround`, `Kiva`), model-wide parameters, required geometry, and the document's materials and evidence.
- v7 changes no physics. It clarifies how a consumer resolves references (inside the selected document, never across documents) and how it instantiates a foundation (from actual geometry, never from the source's reference geometry), with acceptance tests R1 to R6, K1 to K6, and I1 to I6.

BEMGen's geometry has one ground surface, the floor under the bottom storey. It has no basement, crawlspace, garage, foundation wall, or rim joist, and it computed no exposed perimeter. The atlas also asks that native ground methods not take the "indoor minus 2 °C" rule, whose only justification was that D-130 needed some ground temperature.

## Decision

### The owner's decisions (2026-10-18, D-145)

1. **Packet v7 replaces v3**, pinned whole, byte for byte. The unified 1.1.0 and detailed 2.0.0 readers are retired, with no backward compatibility (D-064).
2. **D-142 is kept.** *Convert2IDF* converts only unified sets of scope `building`. Detailed documents and single-dwelling sets are imported and their foundations instantiated from declared geometry, but not converted. Kiva and the C-factor wall therefore run only outside the pipeline.
3. **Native ground in *Convert2IDF*** for a v7 set: F-factor floors with the surface's actual area and exposed perimeter, and layered ground floors. Shared edges between ground pieces cancel from the perimeter, and zero is allowed.
4. **F/C ground temperatures** come from the weather file's monthly mean dry-bulb, delayed three months and rounded to 0.1 °C, the OpenStudio Standards STAT method computed from the EPW's hours. A v7 set with F- or C-factor surfaces and no weather file is refused.
5. **Layered-ground temperatures** are 18 °C in every month, the source's effective condition: EnergyPlus's default `BuildingSurface` object, which the source's prototypes ran with.
6. **D-130 stays** for a conversion without a construction set, and for an uncovered ground that *Fill From Example* gives the Example's construction.

### Realisation (controller, Provisional)

- **Reading.** `ConstructionJsonImporter.Read` reads either representation of any scope with full closure; `Import` is `Read` plus D-142's scope refusal. The four v7 schemas are embedded byte for byte and evaluated without the network. The foundation data are plain types in `Lod.Core.Foundations` (`FoundationData`), carried on `ConstructionSet.Foundation`.
- **Instantiation service** (`FoundationInstantiator`, `Lod.Core.Foundations.Instantiation`, no IDF text). Requests carry declared geometry, never the source's reference geometry.
  - **Scoped reuse.** Definitions are compared by their complete resolved values (F with area and perimeter, C with height, layers with materials). Equal definitions may share one object; an assembly or method ID alone never authorizes sharing. A Kiva group is never merged with another, even when numerically equal. Model-wide Kiva settings and ground-temperature requests are shared when equal and refused when they conflict.
  - **Initialization** (`resstock_source_start_month_1.0.0`, `KivaInitialization`): the start month's mean outdoor dry-bulb, an indoor operand from the setpoints and balance thresholds (or the outdoor operand when explicitly uncontrolled), then T = w_o·T_out + w_g·T_ground + w_i·T_in + offset_K. Missing weather or setpoints and an unknown policy are errors; nothing is invented.
- **Native ground in *Convert2IDF*.**
  - A ground floor takes the one `GroundFloor` assignment that covers building-default ground (`NativeGroundFloor`). F-factor floors are `Construction:FfactorGroundFloor` per distinct (F, area, perimeter) on `GroundFCfactorMethod`; layered floors are the set's layers on `Ground`.
  - The exposed perimeter (`ExposedPerimeter`) is the length of a piece's edges that no other ground piece of the same level shares; the building's total is the footprint perimeter on every zoning.
  - `Site:GroundTemperature:FCfactorMethod` comes from `EpwDryBulb`; `Site:GroundTemperature:BuildingSurface` is 18 °C for layered ground. Both are recorded in the header and in provenance (`GROUND:` lines).
  - A ground the set does not cover is `ConstructionMissing`, or with *Fill From Example* the Example's construction with a warning. A method the pipeline cannot place (`Kiva`, `CFactor`) is `GroundMethodNotSupported`, with or without *Fill From Example*.
  - `FoundationWall`, `FloorOverFoundation`, and `RimJoist` have no BEMGen geometry and are listed as unused.
- **Outside the pipeline.** `IdfFoundations.Write` writes instantiated foundations as EnergyPlus 26.2 objects (C-factor walls, Kiva foundations with settings and exposed perimeter, layered constructions). *Convert2IDF* does not use it. Kiva and the C-factor wall are checked in EnergyPlus only through importer-generated cases that call it.

## Evidence

- **Research recorded in D-145.** ResStock and OS-HPXML (Kiva foundations, their initialization, and the start-day controls) and ComStock and OpenStudio Standards (F-factor floors, C-factor walls, and the STAT monthly dry-bulb delayed three months for `Site:GroundTemperature:FCfactorMethod`; no `BuildingSurface` object when the STAT file is found, so EnergyPlus's 18 °C default).
- **EPW ground temperatures are unreliable as an input.** 16 of the 157 local EPW files have none, ComStock's and ResStock's AMY files among them. Where present they are undisturbed soil values, which EnergyPlus advises against under a building.
- **EnergyPlus 26.2 runs** of the stage's cases (Chicago O'Hare TMY3; table in the design note, Part D): the pipeline cases (medium office and warehouse F-factor on two zonings, retained midrise apartment, tall building, small data centre windowless, legacy hospital, hospital 2019) and the importer-generated Kiva and C-factor cases (R4, K1, K2, K4) pass with no severe error and no unexpected warning, and the F-factor surfaces' U equals 1/(A/(P·F) − 0.165). The `.eio` shows the intended ground temperatures.
- **The atlas's own EnergyPlus checks are not counted as BEMGen results.** A pass there does not establish BEMGen's correctness.

## Options considered

- **Indoor minus 2 °C for native methods.** Rejected: it is a convenience from D-130, not a source's condition, and the atlas asks that native methods not use it.
- **The EPW header's ground temperatures.** Rejected: absent from 16 of 157 local files, and undisturbed soil values.
- **A new monthly ground-temperature input on *Convert2IDF*.** Rejected for now: the source's rule needs no input, and a researcher's input would open a second route to the same quantity.
- **A positive minimum exposed perimeter.** Rejected: it would be invented; zero is a valid perimeter of a core zone.
- **Merging equal Kiva groups.** Rejected by the contract (K2): each group has its own initial condition, and the document's ID or numerical equality does not make two foundations one.
- **Kiva and C-factor in the pipeline.** Not now: BEMGen has no foundation walls, basements, or foundation groups (D-145, D-142).

## Consequences

- A packet v7 building-scope set converts with its own ground. The IDF of an office, warehouse, apartment, or tall building has F-factor floors and monthly ground temperatures from the weather file; a data centre or hospital has layered ground at 18 °C.
- No existing export or integration snapshot changed: envelope presets and sets without foundation data write what they wrote before.
- Definitions and tests that used the v3 names move to the v7 names (`retained-*`).
- Ground floors and soil get no mass restoration; the shared mass contract's other rules are unchanged.

## Open items

- **Data centre with Example windows.** The small data centre's windowless source set with *Fill From Example* windows gives 6 severe errors in EnergyPlus (one per bottom-storey zone: "floor cannot absorb any solar gains"): the source's ground floor has solar absorptance 0, and the Example windows admit beam solar. The run completes. A warning from *Convert2IDF* when *Fill From Example* gives windows over such a floor is proposed, not built. The owner decides. *Resolved by D-147:* *Convert2IDF* now warns (`ExampleWindowSolarNotAbsorbed`), naming the zones; the values stay the source's.
- **Host air exchange** of crawlspaces and garages (SLA with the ASHRAE 62.2 weather factor, Sherman-Grimsrud) is not instantiated; it is reported as unsupported, and no air change rate is invented.
- **Start-day setpoints** of a Kiva group come from the caller, not from program schedules.
- **The 5A Kiva method gives no footing wall construction**, so EnergyPlus uses its default footing wall, with no warning.
- **C-factor soil resistance** appears capped at about 0.92 m²·K/W beyond about 2.47 m of wall; this is inferred from output, and the documentation's text gives no cap.
- **Two ground matchers.** The ground resolution of `ConstructionSet.Resolve` (Part C) and the `FoundationInstantiator`'s assignment selection (Part B) are separate, with different rules and codes. A shared selection helper is a follow-up.
- **Schema `$id` versions.** The v7 schemas' internal identifiers (`construction-equivalent:1.2.0`, `construction-set:2.1.0`) differ from the documents' versions (2.0.0 and 3.0.0). This is the atlas's naming, to be reported to the atlas.
- **Turned-plan court cases.** F-factor runs of turned plans with courts have not been made in EnergyPlus; the written perimeters are checked against the footprint in tests for every family.
