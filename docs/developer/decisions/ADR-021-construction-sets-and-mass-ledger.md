# ADR-021: Construction sets from the atlas, and a mass ledger against reference budgets

Status: Accepted (the owner's decisions of 2026-10-15, D-137 and D-138); the realisation is the controller's and stays provisional until the owner has read it. Decision 2 (the ground) is superseded by D-145 (2026-10-18) for packet v7 sets, which take the ground method of their own `GroundFloor` ([ADR-023](ADR-023-native-ground-methods-and-packet-v7.md)); it still holds for a set without foundation data.

Date: 2026-10-15

Decisions: D-023, D-031, D-064, D-111, D-124, D-126, D-130; new: D-137, D-138, D-139. Extends [ADR-010](ADR-010-convert2idf.md) (the envelope preset and *Convert2IDF*).

Design note: [2026-10-15-construction-json.md](../plans/2026-10-15-construction-json.md) · Architecture: [construction-json.md](../architecture/construction-json.md), [convert2idf.md](../architecture/convert2idf.md#construction-sets) · Atlas source: ADR 0025 and the construction contract, in the pinned packet `tests/Lod.ConstructionJson.Tests/Fixtures/packet/docs/`

## Context

An envelope preset (ADR-010) holds exactly one construction per role, every value illustrative (D-023). The Energy Archetype Atlas now publishes sourced constructions in two kinds of document. The unified one, `building_level_equivalent` 1.1.0, gives one assembly per envelope semantic. It also gives the source's reference capacity budgets, for interior walls and slabs per counted floor area, and its furnishing mass. Three things in these documents do not fit a preset:

- **Missing semantics.** A document may lack a semantic the building's geometry has. The residential source, a single-family house, has no interior walls or floors.
- **Mass the geometry cannot represent.** A zoning that merges zones removes walls and slabs, and the capacity they held has to go somewhere.
- **No ground.** The contract is above-ground only.

## Decision

### The owner's decisions (2026-10-15)

1. **Scope.** Constructions only, unified documents first; detailed documents follow as Part E. Program JSON v3, suite wiring, and *Convert2BEM* are out of scope (D-137).
2. **Ground.** Ground floors take the Example envelope's ground floor, with no new input (D-137).
3. **Over budget.** Where the building already represents more capacity than a family's budget, no mass is added for that family, and a warning records the overshoot (D-137).
4. **Fixtures.** The pinned packet is committed byte for byte (D-137).
5. **Missing roles.** A role the set lacks but the geometry needs takes the Example's construction, with a warning (D-138).

### Realisation (controller, provisional)

- **A construction set is not a preset.**
  - `ConstructionSet` (`Lod.Core.Envelope`) holds one `RoleConstruction` per role: provided, not applicable, or blocked, with the source's reason. It also holds the window, the infiltration, the mass data, and the window's incident solar multiplier.
  - `Resolve` turns it into an `EnvelopePreset` for the roles a given building uses, so the converter's existing path writes it.
  - A preset is the set `FromEnvelope(preset)`, which resolves to the preset itself, so legacy output is byte for byte unchanged.
- **Role mapping.**
  - `InteriorFloor` is the canonical slab, and the ceiling below is its reverse, as the atlas's paired-surface policy says. `InteriorCeiling` is unused, because BEMGen has no unpaired ceilings.
  - BEMGen's internal mass role is a removed slab (D-031), so it takes the interior floor recipe.
  - Doors, skylights, and tubular devices have no BEMGen geometry and are listed as unused.
- **The mass ledger** (`ConstructionMassAccounting`, `Lod.Core.Conversion`) follows the atlas's physical convention and counts each physical surface once:
  - a wall between zones is the mean of its two multiplied faces;
  - a slab is its floor side, times the zone multiplier;
  - a removed slab counts once, although it exchanges heat on two faces.

  Each family's shortfall against its budget, scaled to the counted floor area, becomes added `InternalMass` of the family's recipe: the interior wall's for walls, the floor-distributed mass's for floors. It is added at a rate per m² of floor, applied to each zone's floor area, so the totals are exact. Furnishings are added at the set's rate. A zero budget is information, not a warning, because the source has no such inventory. A blocked recipe that the ledger needs stops the conversion.
- **Strict import.**
  - Unknown operands are errors, never zeros: a missing budget list, an unsupported layer or solar-modifier model, or a single layer with different faces.
  - The surface properties of the exterior face go to the outside layer, those of the interior face to the inside layer.
  - Natural air changes in 1/s become air changes per hour, always on.
- **Grasshopper.**
  - *Construction JSON* outputs a set.
  - *Convert2IDF* takes it on an appended *Construction* input, whose GUID is unchanged.
  - Connecting both *Envelope* and *Construction* is an error. A connected *Construction* that fails stops the conversion; it never falls back to the Example.

## Options considered

- **Squeeze the documents into `EnvelopePreset`.** Rejected: a preset cannot say "not applicable" or "blocked", and it cannot carry budgets. The handover advised against it.
- **Block on every missing role** (the handover's rule). Rejected by the owner (D-138): it would make the residential set unusable on every BEMGen residential plan.
- **Add the atlas's precomputed `FloorDistributedMass` quantity as it is.** Rejected: that quantity is the reference geometry's. The ledger recomputes the residual for each zoning, which is what the study compares.
- **Clip silently, or block on an overshoot.** The owner chose a warning (D-137).

## Consequences

- **Invariant, checked from the IDF text.** A family's represented capacity plus the capacity added for it equals its budget, wherever the budget is not exceeded. Every packet document is checked this way through every simplifier, aggregator, and heat-transfer setting.
- **Envelope capacity varies with zoning by design.** The added mass makes the total match the reference budget. With an overshoot it does not, which is recorded as a warning.
- **Findings left open:**
  - The warehouse budget is exceeded on every multi-storey plan.
  - The writer still gives a removed slab the internal mass area of both its exposed faces (D-031), so EnergyPlus holds twice the capacity the ledger counts for it. *(Closed by D-143, 2026-10-16: each exposed face is written as a half slice of the slab, so the IDF's removed-slab capacity now matches the ledger's count of it once; see [convert2idf.md](../architecture/convert2idf.md#removed-slabs-as-internal-mass).)*
  - The effect of the incident solar multiplier has not been compared in EnergyPlus. *(Checked by D-143, 2026-10-16: the 5A set's IDF on the linear plan, *No Simplification* with *Stack Floors*, run for a year in EnergyPlus 26.2 in Golden, CO (TMY3) with and without its `SurfaceProperty:IncidentSolarMultiplier` objects, gave windows' transmitted solar in the ratio 0.8276, the multiplier, with a blank schedule.)*
- **Part E.** Detailed documents need source-aware binding: a typed binding context through the floor mapping, and several window constructions.
