# ADR-022: Residential construction sets: opt-in Example fill, attic roofs, adiabatic source floors, and detailed documents read but not assigned

Status: Accepted (the owner's decisions of 2026-10-15, D-140). The detection rules and the reading of detailed documents are the controller's, provisional until the owner has read them. Superseded in part by D-142 (2026-10-16), removed in code by D-143: the attic roof, the garage-wall caveat, and the warning on adiabatic source floors (decisions 2 and 3, and the detection rules), because a single-dwelling set is now refused, and E2 (decision 4), which was dropped. Still in force: opt-in *Fill From Example* (decision 1), and the reading of detailed documents, now as evidence that is never converted.

Date: 2026-10-15

Decisions: D-137, D-138, D-140; refines [ADR-021](ADR-021-construction-sets-and-mass-ledger.md).

Design note: [2026-10-15-construction-json.md](../plans/2026-10-15-construction-json.md), build log "C2" and "E1" · Architecture: [construction-json.md](../architecture/construction-json.md), [convert2idf.md](../architecture/convert2idf.md#construction-sets)

## Context

The atlas's packet v2 adds two residential pairs to the one-storey house of v1. All three sources are single detached dwellings (`whole_dwelling`), and no residential source has interior walls, interior floors, and exposed floors together. Reading their detailed conditions showed three things:

- **The attic.** In the one-storey house, `ExteriorRoof` is the deck over a vented attic, and the insulation is in `InteriorCeiling`, between the conditioned space and the attic. ADR-021's mapping wrote the bare deck over conditioned zones.
- **The garage.** The residential `InteriorWall` is a wall to a garage.
- **Adiabatic floors.** The residential `InteriorFloor` comes mostly from floors that are adiabatic in the source.

The atlas also asked:

- that a role a building needs but the set lacks give an actionable diagnostic, or an explicitly reviewed override, never a silent fill;
- that both document kinds parse;
- that parsing stay separate from assignment.

## Decision

### The owner's decisions (2026-10-15, D-140)

*(Decisions 2 and 3 are superseded by D-142, and E2 in decision 4 is dropped; decision 1 stands.)*

1. **Fill is opt-in.** A role the set lacks is the error `ConstructionMissing` by default. *Convert2IDF*'s *Fill From Example* (`IdfOptions.FillFromExample`) makes it the Example's construction with a warning, the reviewed override of D-138. The ground stays the Example's with a remark (D-137).
2. **Attic roofs.** The roof of conditioned zones takes the attic ceiling, recorded as an approximation that leaves out the attic air and the roof deck. No attic zone is modelled.
3. **Adiabatic source floors** written conductive by floor heat transfer give a warning, not an error.
4. **Order.** C2 and then E1 without a stop. E2, the assignment of detailed rules, comes later.

### Realisation (controller, provisional)

*(D-142, D-143: the detection rules, the attic roof, and the `Approximation` and `AdiabaticInSource` properties are removed; a `whole_dwelling` set is refused with `ConstructionJsonScopeNotSupported`. The reading of detailed documents remains, as evidence only.)*

- **Detection.** The unified document carries no space types, so the residential rules key on the `whole_dwelling` scope:
  - `InteriorCeiling` and `ExteriorRoof` both ready means an attic roof;
  - `InteriorWall` carries the garage caveat;
  - `InteriorFloor` is flagged adiabatic in the source.

  An explicit flag from the atlas would replace these rules.
- **The attic roof.** It is the ceiling's layers under its own name (`{ceiling id} as roof`), with the source roof's exterior surface properties on the outside layer, because that face is now outdoors. It is recorded as `RoleConstruction.Approximation`, which gives `ConstructionApproximation` wherever a building uses the role.
- **Detailed documents.** They are read into `DetailedConstructionDocument`, which keeps every condition, disposition, reversal flag, and geometry instruction as data and the assemblies in BEMGen's types. The set made from one carries `AssignmentUnavailable`, so a conversion is the compatibility error `ConstructionAssignmentUnavailable`, which names the unified document to use. Nothing about the detailed rules is applied.

## Options considered

- **An attic zone.** Rejected for now. It is a geometry element across every generator and aggregator, it needs a sourced attic ventilation rate, and it is geometry BEMGen's flat-roofed residential generators never had.
- **The bare roof deck as the roof** (ADR-021's mapping). Rejected: about twenty times too conductive over conditioned rooms.
- **A compatibility error for attic roofs.** Rejected by the owner in favour of the approximation, which keeps the one-storey house usable.
- **Fill on by default** (D-138). Superseded: a silent fill on every residential conversion hides a mismatch between source and geometry.
- **Assign detailed rules with BEMGen's own space mapping now.** Deferred to E2. BEMGen has no garage space type and no source storeys, so any mapping now would be a guess.

## Consequences

*(D-142, D-143: the bullets on the one-storey house, the floor heat transfer warning, and E2 no longer apply; the other bullets stand, with the five packet documents now seven, of which three building-scope ones convert.)*

- **Fill.** A residential set on a multi-zone plan needs *Fill From Example*, or a zoning without interior walls (*Single Zone per Floor*). Either choice is recorded in the IDF header.
- **The one-storey house** converts with its insulated ceiling as the roof. Summer attic heat is missed, and winter heat loss is slightly overstated.
- **Floor heat transfer** with a residential set warns that its interior floor's resistance was never meant for conduction between storeys.
- **All ten packet documents parse.** The five unified ones convert, through every zoning in the test matrix, and the five detailed ones are refused with an actionable error.
- **E2** needs a design note: how detailed conditions bind to BEMGen zones, whether BEMGen gains a garage or unconditioned space type, and whether source storeys map to generated storeys.
