# E2: binding detailed construction rules to BEMGen zones (design note)

> **Status:** Superseded by D-142 (2026-10-16): BEMGen converts only unified building-scope sets, so detailed rules are never bound to zones. Kept as the record of the questions; the owner's answers are in D-142 · **Date:** 2026-10-16 · **Decisions:** D-137 to D-141; new: one entry for the owner's answers · **Branch:** `feature/construction-json` (proposed; see question 10) · **Builds on:** [construction JSON note](2026-10-15-construction-json.md) (E1), [ADR-021](../decisions/ADR-021-construction-sets-and-mass-ledger.md), [ADR-022](../decisions/ADR-022-residential-construction-sets.md), [construction-json.md](../architecture/construction-json.md)

This is one stage run as D-111 sets out: this note first, then one test-first build, a review by a second agent, the headless Rhino check, `scripts/verify.ps1`, a decision-log entry, and an ADR, because it decides how a source's construction rules meet BEMGen's geometry.

**Stop line.** The build ends verified, reviewed, and documented. It does not merge, tag, push, or release.

## Problem

E1 reads a detailed `construction_set` 2.0.0 with every assignment rule, but *Convert2IDF* refuses it (`ConstructionAssignmentUnavailable`). E2 makes it convertible.

For each surface, window, and internal mass of a building, E2 chooses the one assignment whose condition (`when`) matches, as the source's policy says: space type, then storey, then the building default; a unique compatible rule; and an error when no rule matches or several do (`unmatched_or_ambiguous: error`). The unified path (C2) stays as it is. Detailed and unified are two explicit choices, never switched or blended automatically (handover).

## What the packet's rules look like

From the five detailed documents (`docs/residential-fixture-coverage.json` and a census of `when`):

| Document | Rules | Conditions used |
| --- | --- | --- |
| Medium Office 3B | one per component, plus `InteriorFloor` for `space_type: Plenum` | `building_default`; `window_operation` fixed or operable |
| Warehouse 3B | four per component: the default and `space_type` `Office`, `Fine`, `Bulk` | `building_default`, `space_type`, `window_operation` |
| Residential 5A | conditioned space to outside; attic to outside; conditioned space to attic (the ceiling); partitions | `whole_dwelling` with `interior_space_type`, `exterior_space_type` |
| Residential 4A | the above without the attic, plus conditioned space to garage (wall, floor) and an `Adiabatic` interstorey floor | as above, and `boundary_condition` |
| Residential 1A | conditioned space to outside, with an exposed floor; an `Adiabatic` interstorey floor | as above |

No packet document uses `story` rules. Every one declares the same policy (`space_type_then_story_then_building_default`, `explicit_assignment_id_or_unique_compatible_rule`, `source_absent_override: inherit_building_default`, `unmatched_or_ambiguous: error`).

## What a BEMGen zone knows today

- **Space type.** `SpaceType`, BEMGen's own: `DwellingUnit`, `Corridor`, `Stair`, `Office`, `Core`, `Retail`, …, `Mixed`.
- **Program.** `ProgramPreset.Source`. For a *Program JSON* preset it names the atlas program (`Source.ProgramId`), its building type and template. Program JSON 2.0.0 has no field for the native space type; its name and evidence carry it as text (`WholeBuilding - Md Office_MediumOffice`).
- **Conditioning.** `Program.IsConditioned`.
- **Origin.** Its source zones before simplification (`SourceZones`, `Mapping`), its storey (parts' elevations), and its multiplier.
- **Each surface.** Its kind, its boundary (outdoors, ground, interzone, adiabatic), and the zone across it; for an interzone surface, its partner.
- **Windows.** A window has no operation: BEMGen has no operable windows.

The handover warns against inferring native contexts from labels such as `Office` or `Mixed`, from floor indices, or from text in provenance.

## Proposal

### Part A: a binding context, explicit and typed (`Lod.Core`)

Each zone gets a `ConstructionBinding` that says which source context it stands for:

- its **source space type**: the native name the detailed rules use, such as `Bulk` or `Plenum`, or none;
- its **space category** for residential rules: `conditioned space`, or an unconditioned category such as `garage`, `attic - vented`, `unconditioned space`.

Question 1 decides where these come from. The binding is carried through simplification and aggregation the way `SourceZones` is. A merged zone whose sources disagree has no single binding, which is question 6.

### Part B: the surface context and the matcher (`Lod.Core.Conversion`)

For every written surface, window, and removed or added mass, the converter builds a context:

- the **detailed semantic**, from `ConstructionRoles` and the boundary:

  | Surface | Semantic |
  | --- | --- |
  | wall to outdoors | `ExteriorWall` |
  | roof | `ExteriorRoof` |
  | floor to outdoors | `ExteriorFloor` |
  | wall between zones | `InteriorWall` |
  | slab between storeys | `InteriorFloor`, the ceiling side reversed |
  | window | `ExteriorWindow` |
  | removed slab | `InteriorFloor` |
  | partition mass | `InteriorPartition` |

- the zone's **source space type**, the **interior space category** (the zone's) and the **exterior one** (`outside` to outdoors, or the adjacent zone's category);
- the **boundary condition** as written (`Outdoors`, `Surface`, `Adiabatic`), and the **window operation** (question 4).

The matcher keeps the assignments of that semantic whose every given condition equals the context, then applies the precedence: a `space_type` rule over a `story` rule over a `building_default` rule (or `whole_dwelling` rule). One rule left is the assignment. None left is `ConstructionUnmatched`, and more than one `ConstructionAmbiguous`. Each error names the surface, its context, and the rules that came closest.

A paired surface between two zones is bound once, from the zone that owns it as `ConstructionRoles` already decides, and its partner takes the reverse (`paired_surface_policy: reverse_order`). `SourceReferenceReversed` is evidence only.

### Part C: constructions per surface and per window (`Lod.Export`)

- **Assemblies.** The writer gives each surface the assembly its rule selects, not one construction per role. Every selected assembly is written once, with its reverse where a pair needs it.
- **Windows.** A window's construction is chosen per window, so a building may have several window constructions. Each with an incident solar multiplier gets its own `SurfaceProperty:IncidentSolarMultiplier`.
- **Unsupported assemblies.** Selecting one (E1's `Unsupported`) is an error that names it.
- **The header** lists each assignment used, with its ID, condition, assembly, and number of surfaces, plus every rule that matched nothing in this building.

### Part D: mass (`ConstructionMassAccounting`)

The detailed document has no capacity budgets and no `FloorDistributedMass`. Its mass rules are geometric:

- `InteriorPartition`: area per conditioned floor area, by its `area_convention`;
- the interstorey floor's `source_ordinary_interstory_scaling`: an area rule, a paired flag, an activation threshold.

Question 7 decides how they apply.

### Part E: Grasshopper

*Convert2IDF* converts a detailed set. Question 1 decides whether the binding needs a new input, such as a *Space Type Map*. *Construction JSON* is unchanged, apart from its warning, which goes.

## Open questions for the owner

1. **Where does a zone's source space type come from?**
   - (a) A new explicit map on *Convert2IDF*, from BEMGen space type (or zone name) to source space type and space category, such as `Office → Office`, `Core → Bulk`, `Stair → unconditioned space`.
   - (b) The program preset: *Program JSON* would record the native space type, which needs a structured field from the atlas (program JSON v3 may have one).
   - (c) Only building-default and whole-dwelling rules are bound, and a document with `space_type` rules is refused.

   I lean to (a) now, with (b) when the atlas provides the field.
2. **Residential categories.** BEMGen's residential plans have dwellings, corridors, and stairs; the residential sources have conditioned space, garage, and attic.
   - Are unconditioned corridors and stairs "unconditioned space"? No source rule mentions it, so their walls would be unmatched.
   - Is a garage ever modelled, or is the garage rule only evidence?
3. **Walls and floors between two conditioned zones, residential.** No residential rule covers them: the sources are single dwellings, and the only `InteriorWall` rule faces a garage. Options:
   - (a) Unmatched, an error.
   - (b) Fill From Example, as for unified sets (D-140).
   - (c) Use the `Adiabatic` interstorey rule for floors written adiabatic only; walls by (a) or (b).

   And with floor heat transfer on, does the `Adiabatic` rule match an interzone floor (D-140 accepted that with a warning for unified sets), or is it unmatched?
4. **Window operation.** BEMGen windows have no operation, and the commercial documents give separate fixed and operable rules. Choose one by default (fixed?), or an input?
5. **The attic in detailed documents.** For 5A, the conditioned zones' roof matches no rule: the roof rule's interior is the attic. Apply D-140's approximation, the attic ceiling as the roof, through the `InteriorCeiling` rule, as for unified sets?
6. **Rezoned zones.** A merging simplifier makes zones whose sources have different space types. Options:
   - (a) An ambiguity error; use the unified document, as the handover suggests.
   - (b) The space type with the largest floor share.
   - (c) Allow it only when every source agrees.

   I lean to (c), with (a) otherwise.
7. **Mass for detailed sets.**
   - Add the partitions as internal mass at their area per conditioned floor area, by their area convention?
   - Apply the interstorey area rule to slabs BEMGen does not represent?
   - Or keep the detailed path to explicit surfaces only, with no added mass?

   The unified ledger cannot be reused, because there are no budgets.
8. **`story` rules.** No packet document has them. Refuse a document that has them until a storey map exists, or design the map now?
9. **Fill From Example.** Should it also cover unmatched detailed surfaces, or only not-applicable roles as now?
10. **Branch and order.** Continue on `feature/construction-json`, or merge C2 and E1 first and start `feature/construction-binding` from `main`?

## Tests and checks (planned)

- **Matcher unit tests** on hand-built contexts: precedence, unique compatible rule, unmatched and ambiguous errors, paired reversal.
- **End to end on the packet documents:**
  - the warehouse with its three space types, mapped onto *Office Plate* and a warehouse-like plan;
  - the medium office's plenum floor;
  - 4A's garage and adiabatic rules;
  - 1A's exposed floor;
  - 5A on one storey of one zone.
- **Checks on the result:**
  - every surface's construction against its rule, read back from the IDF;
  - several window constructions and their multipliers;
  - an unsupported assembly selected is an error.
- **A unified-detailed pair** converted on the same building, comparing the area-weighted U-values per semantic. This is a check, not an equivalence claim.
- **IDD check, EnergyPlus runs, and the headless Rhino spec.**

## Build log

(empty)
