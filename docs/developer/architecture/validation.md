# Validation

Applies from v0.3.0 (S3). Code: `src/Lod.Core/Validation/Totals.cs` and `src/Lod.Core/Validation/Validators.cs`. Rules: GLOBAL.md scientific rules 1, 2, and 6; research brief §17; D-038 (conditioning), D-041 (façade coverage), D-045 (building height), D-046 (ground, roof, and exposed floor area); D-124 (infiltration is not a program load, [ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)); roadmap S3 slice `feature/validation-invariants`.

## Purpose

Simplification deliberately changes zoning, heat transfer between zones, and controls where the LoD says so; those differences are what the study measures. It must not change the prescribed conservation invariants: floor area, volume, exterior wall area, glazed area in total and per orientation, and the installed and hourly scheduled magnitude of every program load type (since D-124 not infiltration, see [below](#infiltration-and-program-mixes-d-124)); for a building also ground, roof, and exposed floor area and the building height (D-045, D-046); and the target façades must cover the source façades. Validation checks these numerically, together with tiling and traceability, before a model is converted.

Validation applies to objects that exist. A simplifier that cannot produce a valid floor fails earlier, with its own diagnostics (`PlanTooNarrow`, `DisconnectedGroup`, `TouchingPieces` and `DuplicateZoneId` (D-123), `FacadeNotCovered`, the centred-window guards `WindowNotHosted` and `GlazingExceedsWall` (D-079), gaps and overlaps from the surface builder, aggregation errors), and returns no floor.

## References

| Validator | Validates | Compared with |
| --- | --- | --- |
| `FloorValidator` | an `IFloor` from any plan simplifier | its source plan, `IFloor.Source` (the detailed Z0 plan) |
| `BuildingValidator` | an `IGeneratedBuilding` from any floor aggregator | 1. every distinct source floor against its plan, as `FloorValidator` does; check names prefixed `Floor0.`, `Floor1.`, … in floor order. 2. the fully stacked reference `Stack.Aggregate(building.Sources)`: the same floor entries with every storey explicit; check names prefixed `Building.` |

If the stacked reference cannot be built, `BuildingValidator` adds the failed check `Building.Reference` with the stacking diagnostics and stops.

## Totals

`Totals.Of(zones, surfaces, orientationDegrees)` computes the extensive quantities of a set of zones, counting zone multipliers.

| Total | Definition |
| --- | --- |
| Floor area | Σ multiplier × zone floor area, m² |
| Volume | Σ multiplier × zone volume, m³ |
| Conditioned floor area | Σ multiplier × floor area of zones whose program has a thermostat, m² (D-038) |
| Exterior wall area | Σ multiplier × gross area of walls with boundary `Outdoors`, windows included, m² |
| Glazing | Σ multiplier × glazed area of those walls (all their windows), m² |
| Glazing per orientation | the same per bin North [315°, 45°), East [45°, 135°), South [135°, 225°), West [225°, 315°) of the wall's true azimuth (plan azimuth + orientation) |
| Ground area | Σ multiplier × area of horizontal surfaces with boundary `Ground`, m² |
| Roof area | Σ multiplier × area of ceilings with boundary `Outdoors`, m² |
| Exposed floor area | Σ multiplier × area of floors with boundary `Outdoors` (overhangs, floors not covered by the storey below), m² |
| Height | elevation of the highest zone top (part elevation + part height), m; 0 without zones. This is the building height when the lowest storey starts at 0 |
| Installed magnitude | per load type, summed over all bases of the type (D-047), Σ multiplier × design magnitude (ADR-007): people for occupancy; W for lighting, electric and gas equipment; m³/h for hot water and ventilation (infiltration is not a program load since D-124) |
| Scheduled magnitude | per load type and hour (8760 values), Σ multiplier × design magnitude × schedule fraction |

A court (a hole of the footprint, S8.3) is outside the building: its façades are outdoor walls and count in the exterior wall area and in the glazing of the orientation they face (into the court: the south wing's court façade faces north), and the court adds no floor, ground, or roof area. No check changes.

## Checks

Relative comparisons are `|a − b| ≤ tol × max(1, |a|, |b|)` (ADR-004).

| Check | Compares | Tolerance | Enforced |
| --- | --- | --- | --- |
| `FloorArea` | floor area | `RelativeArea` | yes |
| `Volume` | volume | `RelativeArea` | yes |
| `ConditionedFloorArea` | conditioned floor area | `RelativeArea` | no: reported only (D-038); for *Conditioned Merge* it never differs, in either mode (D-123) |
| `ExteriorWallArea` | exterior wall area | `RelativeArea` | yes |
| `Glazing` | total glazed area | `RelativeArea` | yes |
| `Glazing.<Bin>` | glazed area per orientation bin; one check per bin present in either total | `RelativeArea` | yes |
| `Installed.<LoadType>` | installed magnitude; one check per load type present in either total, all bases of the type together (D-047) | `RelativeLoad` | yes |
| `Scheduled.<LoadType>` | scheduled magnitude at each of the 8760 hours; the detail names the worst hour | `RelativeLoad` at every hour | yes |
| `FacadeCoverage` (floor) | every source outdoor wall is covered over its full length by target outdoor walls on the same façade line, before any normalisation. Two walls are on the same façade line when they face the same way (`Angle`), share elevation and height (`Distance`), overlap, and are within `Distance` of each other over their overlap (ADR-013) | `RelativeArea`, applied to lengths | yes (D-041) |
| `NoTargetOverlap` (floor) | Σ pairwise intersection area of the parts of the target zones, so the pieces of one zone are compared with each other and with every other zone (D-123) | at most `RelativeArea` × footprint area | yes |
| `SourceCoverage` (floor) | each source zone's floor area vs the sum of its mapping overlaps | `RelativeArea` | yes |
| `Traceability` (floor) | every target zone has a mapping row; an identity zone (no source zones, `NoSimplification`) has an identity row with source fraction 1; a derived zone has aggregation records on every load value and every load schedule and, if it is conditioned, on both setpoint schedules | exact | yes |
| `Building.Reference` | the stacked reference could not be built | — | yes |
| `Building.GroundArea` | ground area vs the stacked reference | `RelativeArea` | yes (D-046) |
| `Building.RoofArea` | roof area vs the stacked reference | `RelativeArea` | yes (D-046) |
| `Building.ExposedFloorArea` | exposed floor area vs the stacked reference: a floor aggregator must not multiply overhanging floors | `RelativeArea` | yes (D-046) |
| `Building.Height` | building height vs the stacked reference: representative storeys must sit at their true elevations | `Distance`, absolute | yes (D-045) |

Occupancy and air volume flow are not separate checks: occupancy is the load type `Occupancy` (people), and air-change loads are compared as m³/h magnitudes (ADR-007, D-019).

A zone of several pieces (D-123) is measured over all its parts: its floor area, volume, and exterior wall area are sums over the parts, so every total and check above counts all its pieces, and so does the exterior area its infiltration is applied to at conversion (D-124). Two pieces of one zone that share an edge are not validated but rejected when surfaces are built (`TouchingPieces`), because they would be one piece; two target zones with one ID are rejected before that (`DuplicateZoneId`).

Not compared:

- Setpoints. Floor-area weighting over the conditioned sources is a prescribed control rule, not a conservation invariant (D-038).
- Window positions and sizes. Where walls are rebuilt, each outdoor wall gets one window centred on it with the glazed area of the source windows it covers (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)), so individual windows are not conserved by design; the rule is covered by the unit tests of `CentredWindows` and the integration tests `CentredWindowTests`. Validation compares the glazed areas in total and per orientation, which the rule conserves per wall. The reference glazing is the plan's: a generator's wall or window below the ADR-011 minimum has no window (`WindowOmitted`), and validation compares with the glazing the generator placed, not with WWR × wall area. Every window is checked per wall when it is built, not by validation: a source window must lie on one target wall (`WindowNotHosted`) and a wall's glazed area must be smaller than its area (`GlazingExceedsWall`); both hold by construction once the façades are covered (D-041) and are kept as guards.
- Floor and ceiling boundaries of a floor. They stay `Unresolved` until a floor aggregator stacks the floors.

The conditioned floor area is reported because merging conditioned and unconditioned sources makes the merged zone conditioned ("any conditioned wins", D-038). With the example presets, Z2 and Z3 turn the 72 m² stair into conditioned area: `note ConditionedFloorArea: reference 360.000000, actual 432.000000`.

*Conditioned Merge* (Z1c, D-123) is the simplifier for which this check must pass: every target covers source zones of one class only, so the conditioned floor area of its floor equals the source's within `RelativeArea`, with separate and with joined pieces. The check stays reported only; the tests assert that it passes for *Conditioned Merge* and that every source of a target has the target's conditioning. *Semantic Merge* groups by space type, so it keeps the conditioned floor area only when the zones of each space type share their conditioning.

A program changed by mistake is caught through the totals: `ValidationCatchesAChangedProgram` replaces a Z3 program with a preset and fails both `Installed.Lighting` and `Traceability`.

## Infiltration and program mixes (D-124)

**The infiltration invariants are removed.** Infiltration left the zone programs in D-124 ([ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)), so no zone has an infiltration load, and the checks `Installed.Infiltration` and `Scheduled.Infiltration`, which compared its installed and hourly scheduled magnitude of a floor or building with its source, no longer exist: `Totals.Of` sums the program load types only, and a floor or building has one check per load type present, none of them infiltration. The reason is not that infiltration went unchecked. A target zone's infiltration is not transferred from source zones. It is the building's rate (an input of the envelope preset) times the zone's own exterior surface area, outdoor wall area, or volume, applied at conversion, so there is no source magnitude to conserve. It is conserved by construction wherever the quantities it multiplies are, and validation already enforces those:

| Basis of the infiltration | Quantity it multiplies (per zone, with zone multipliers) | Conserved by |
| --- | --- | --- |
| `PerExteriorSurfaceArea` | gross area of outdoor walls, roofs, and exposed floors, not ground floors | `ExteriorWallArea` (floor and building), `Building.RoofArea`, `Building.ExposedFloorArea` |
| `PerExteriorWallArea` | gross area of outdoor walls | `ExteriorWallArea` |
| `AirChangesPerHour` | volume | `Volume` |

*Convert2IDF*'s tests compare each zone's infiltration, read from the IDF as EnergyPlus reads it, with the design flow *Convert2BEM* outputs for the same zone (`ZoneInfiltration`), and the installed total with the building's (`IdfChecks`, [convert2idf.md](convert2idf.md#tests)). `InfiltrationOutOfProgramsTests` runs every family through every plan simplifier and every floor aggregator and finds that each combination validates, that no zone program has an infiltration load, and that every installed and scheduled check is of a program load type.

**New diagnostics.** These come from building the objects, not from the validators: an error stops the object and gives no output; the info is a remark.

| Code | Severity | Raised by | When |
| --- | --- | --- | --- |
| `UndefinedLoadKind` | Error | `LoadDefinition.Create` | The load type or basis is not defined, such as a value cast from the removed infiltration type or exterior-wall basis; the message says to set infiltration on the envelope preset |
| `InfiltrationValue` | Error | `EnvelopePreset.Create`, through `Infiltration.Check` | The design rate is negative or not finite, or the basis is not defined (a schedule that is not a fraction schedule is `ScheduleKindMismatch`) |
| `MixWeight` | Error | `ProgramMix.Mix` | The weights are not one per preset, a weight is not finite and greater than 0, or their sum is not finite |
| `PerPersonWithAbsoluteOccupancy` | Error | `ProgramMix.Mix` | A per-person load and absolute occupancy are in any inputs, the same or different; the message names both |
| `MixedConditioning` | Info | `ProgramMix.Mix` | Conditioned and unconditioned inputs are mixed; the unconditioned share becomes conditioned |

**Other changes to the checks.** None. The load checks keep their names, tolerance, and enforcement, `ExteriorWallArea` still compares the walls with an outdoor boundary, and the façade-coverage check is unchanged; only the exterior-wall fraction that the plan simplifiers took from the façade attribution to transfer loads per exterior wall area is gone, so `FacadeCoverage` is unchanged and still required: the rebuilt walls must cover every source wall for the window rehosting (D-041, D-079). A program mix is not validated further: its aggregation record is the same as a zone merge's, and its equivalence with a zone merge on matching area shares is a unit test (`ProgramMixEquivalenceTests`), not a runtime check, because a mix has no source plan to compare with.

## Tolerances

All tolerances come from `ToleranceSettings.Default` (ADR-004); validation defines none of its own.

| Setting | Value | Used for |
| --- | --- | --- |
| `RelativeArea` | 1e-6 | floor area, conditioned floor area, volume, wall area, glazing, façade coverage (lengths), source coverage, overlap, ground, roof, exposed floor |
| `Distance` | 1e-6 m | building height |
| `RelativeLoad` | 1e-9 | installed and hourly scheduled magnitudes |

Loads can be held to 1e-9 while areas need 1e-6 because transfer fractions are normalised per source (`TransferMatrix`) and per source wall (`FacadeAttribution`): extensive quantities are conserved to floating-point precision whatever the polygon rounding, whereas areas pass through Clipper2 on a 1e-6 m grid. Normalisation is safe only because coverage is checked separately and before it (`SourceCoverage`, `FacadeCoverage`). Tolerances are never widened to make a check pass (AGENTS.md rule 12).

## Report

`ValidationReport.Passed` is true when every enforced check passed. `ValidationReport.Describe()` writes `PASSED` or `FAILED` on the first line, then one line per check: `ok` for a passed check, `FAIL` for a failed enforced check, `note` for a failed reported-only check, followed by the check name and the reference and actual values with six decimals.

## Where validation runs

- *Validate* component (`6 Inspect`): takes a floor or a building and outputs `Passed` and the report; a failed validation adds a warning.
- *Convert2BEM* (`5 Convert`): validates the building with `BuildingValidator` before converting it; the heat-transfer options (D-069) change only the written boundaries, never the building or its validation. Passed: the conversion runs and `Provenance` (output 15) holds the provenance tree followed by the report, the options line, the envelope line, and since D-124 the line `INFILTRATION: <rate> <basis> (EnergyPlus <method>), schedule <name>`. Failed with `Override` false (the default): error `ValidationFailed`, no conversion (outputs 0–14 and 16–21 stay empty), and only `Provenance` is set so the failing checks can be read. Failed with `Override` true: warning `ValidationOverridden`, the conversion runs, and `Provenance` ends with the line `OVERRIDE: converted despite failed validation`. The override is recorded only in that text, so keep `Provenance` with any result produced from an overridden model.

## Tests

- `EverySimplifierSatisfiesTheInvariantsForRandomPlans`: each simplifier on linear plans drawn from explicit seeds (9 cases, including rotated plans and source zones split across several targets).
- `MergingTheUnconditionedStairEnlargesConditionedAreaAndIsReported`: the conditioned-area change is reported, not enforced.
- `ValidationCatchesAnUncoveredFacade`: a missing target wall fails `FacadeCoverage`.
- `NoSimplificationPassesValidation`: the identity floor passes.
- `ConditionedMergeConservesConditionedFloorAreaExactly` (core), `ConditionedMergeConservesConditionedFloorAreaOnRandomPlans` (integration, three random linear plans), and `ConditionedMergeConservesConditionedFloorArea` (integration, every one of the 18 plan families at the default placement and rotated and moved, with separate and with joined pieces): the conditioned floor area of the floor equals the source's and `ConditionedFloorArea` passes (D-123).
- `AFloorWithATwoPieceZoneValidates` and `TheOverlapCheckReadsEveryPart` (core): a floor with a two-piece zone passes every check, and a zone lying on the second piece of another zone fails `NoTargetOverlap` with its overlap; `EveryAggregatorValidatesABuildingOfTwoPieceZones` stacks such floors with every aggregator (D-123).
- `ValidationCatchesAChangedProgram`: a tampered program fails.
- `EveryCombinationValidatesOnARotatedAndTranslatedPlan` (S4.2): every plan simplifier with every floor aggregator on plans rotated and moved by *Transform Plan* (four placements, 64 cases) validates without warnings; `AStoreyMovedOffTheStoreyBelowIsUnsupported` checks the exposed floor and roof areas of storeys from differently moved plans, and `ARotatedSetbackStoreyHasNoUncoveredFloor` a rotated setback, whose floor is fully covered. `ZeroWidthArtefactTests` builds every family canonical and at the two placements of the typology tests through every simplifier and aggregator and finds no spike, repeated vertex, excursion, or sliver in any zone part or surface (ADR-002).
- `InfiltrationOutOfProgramsTests` (D-124): every family through every plan simplifier and floor aggregator validates, no zone program has an infiltration load, and no installed or scheduled check is of a type other than a program load type.
