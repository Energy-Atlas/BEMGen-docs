# Concepts

BEMGen passes a small number of typed objects from component to component. This page defines them and the words used for them in the rest of the guide.

## The pipeline in one picture

```text
program presets ──► plan generator ──► (Transform Plan) ──► plan simplifier ──► floor aggregator ──► Convert2BEM
  (1 Program,         (2 Generate)          (2 Generate)        (3 Simplify)        (4 Aggregate)        Convert2IDF
   1 Program Presets)                                                                                 (5 Convert)
        preset              plan                  plan               floor               building
```

Each arrow carries one object: a *preset*, a *plan*, a *floor*, a *building*. *Validate* and *Inspect* (panel *6 Inspect*) read floors and buildings at any point; both converters validate the building again before converting it.

## Objects

Plan
:   The detailed floor plan of one storey, produced by a plan generator: a footprint, zones, and the walls, floors, ceilings, and windows of those zones. A plan is the most detailed model, one zone per dwelling unit or per department. Its floors and ceilings are not yet resolved as ground, roof, or between storeys; that happens when floors are stacked.

Zone
:   A thermal zone: one or more parts (pieces, when a merge simplifier joins pieces that do not touch), each a floor polygon extruded by the floor-to-floor height, with a space type, a program (loads, schedules, conditioning, setpoints), a multiplier, and the list of source zones it was made from. Zone IDs are short codes such as `ST` (stair), `CO` (corridor), `US1` (unit south 1); after stacking they get a storey prefix, `L0/US1`.

Space type
:   What a zone is used for: `DwellingUnit`, `Corridor`, `Stair`, and the non-residential types `Office`, `Core`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, `Lobby`, `ActivityHall`, `Service` (and a few more the general *Program Preset* accepts: `Mechanical`, `Other`). A zone merged from several space types is `Mixed`. The space type is explicit data on the zone, never a layer name or colour.

Program preset
:   The program of one space type: its loads, their schedules, whether it is conditioned and its heating and cooling setpoints, and the window-to-wall ratio (WWR) the plan generator uses for that space type's outdoor walls. Infiltration is not part of it; it belongs to the envelope preset. Its name is descriptive only; it never decides where the preset goes. There are four kinds:

    - **Built-in presets**, one component per space type in panel *1 Program Presets* (*Dwelling Unit Preset*, *Office Preset*, …). Every input has a default, so each works with nothing connected; you can change any value.
    - **General presets**, built in panel *1 Program* from *Schedule*, *Load*, and *Program Preset* for any space type and any set of loads.
    - **Mixed presets**, made by *Mix Programs* (panel *1 Program*) from several presets and a floor-area share for each ([What's new in 1.1.0](whats-new.md#mix-programs)).
    - **Any-program presets**: wire any preset into the parameter *Any Program Preset* (AnyP, panel *1 Program*) and it comes out without a space type. Every preset input of every generator accepts it. The zones keep the space type of the input and take the preset's program, and the plan records the substitution in its provenance (`AnyProgramPreset.<Input>=<preset name>`).

Load
:   One internal gain or air flow: a load type (`Occupancy`, `Lighting`, `ElectricEquipment`, `GasEquipment`, `DomesticHotWater`, `Ventilation`), a basis (`PerFloorArea`, `PerPerson`, `Absolute`, `AirChangesPerHour`), a design value in that basis, and an hourly fraction schedule. Design magnitudes are people, W, or m³/h. A program has at most one load per type and basis; loads of one type in different bases add up.

Schedule
:   8760 hourly values for a non-leap year, either fractions (0 to 1, for loads) or temperatures (°C, for setpoints). The *Schedule* component builds one from a 24-hour weekday profile and a 24-hour weekend profile; holidays are not modelled.

Conditioning and setpoints
:   A conditioned program has a heating and a cooling setpoint schedule; an unconditioned one (the example stair) has none. When zones are merged, the merged zone is conditioned if any of its sources is, and its setpoints are the floor-area-weighted mean of the conditioned sources. *Conditioned Merge* keeps the two kinds of zone apart, so it never changes the conditioned floor area. Setpoints are controls, not loads, so this is a prescribed rule rather than a conservation law.

Window
:   An explicit rectangle in a wall, with an offset along the wall, a sill height, a width, and a height. Plan generators place one window centred on every outdoor wall, with an area of the zone preset's WWR times the wall area, except on walls shorter than 1 m or where the window would be narrower or lower than 0.3 m (the info message `WindowOmitted`). Wherever zones are merged and walls rebuilt, every outdoor wall gets one centred window with the total glazed area of the windows it covers, so glazed area is conserved per wall, façade, orientation, and building, while individual window positions are not.

Envelope preset
:   The constructions and the infiltration of the building: one layered construction per envelope role (exterior wall, roof, ground floor, exposed floor, interior wall, interior floor, internal mass), one simple glazing (U-factor, SHGC, visible transmittance) for every window, and the infiltration rate, basis, and schedule that every zone gets from its own exterior surfaces or volume. It is separate from the program presets and the same at every level of detail, so changing the zoning never changes the envelope. Both converters take it; when none is connected they use the illustrative *Example Envelope*.

Plan generator
:   A component that builds the plan of one typology family from a few dimensions and one preset per space type it places. BEMGen has eighteen ([Typologies](typologies.md)). One of them, *Stepped Band*, returns one plan per storey because its storeys differ.

Storey plans
:   The list of plans, bottom to top, that a generator such as *Stepped Band* returns, one per storey. Each storey is simplified on its own and the floors go to a floor aggregator in the same order, each standing for one storey. The viewport draws each storey at its height.

Plan simplifier
:   A component that turns a plan into a floor with coarser thermal zoning: *No Simplification* (Z0), *Semantic Merge* (Z1), *Conditioned Merge* (Z1c), *Perimeter Core* (Z2), *Single Zone per Floor* (Z3). It maps every source zone onto the new zones by overlap area and aggregates loads, schedules, and setpoints so that they are conserved.

Floor
:   The result of a plan simplifier: the zones and surfaces of one storey, plus its source plan and the source-to-target mapping. *Map Source to Target* lists that mapping.

Floor aggregator
:   A component that stacks floors into a building: *Stack Floors*, *Stacked Floor Zone Multiplier*, *Single Zone per Floor Type*, *Single Zone Building*. It decides which floors and ceilings touch the ground, the outdoors, or another storey, and how repeated storeys are represented.

Multiplier
:   The number of storeys one floor stands for, given per floor to a floor aggregator's *Multipliers* input (whole numbers from 1, default 1). What it does depends on the aggregator: *Stack Floors* repeats the floor explicitly; *Stacked Floor Zone Multiplier* models one representative storey of a group and sets the zone multiplier of its zones to the group size, never multiplying ground, roof, or exposed surfaces. A zone multiplier tells the simulation to count a zone several times.

Building
:   The result of a floor aggregator: every zone at its final elevation, every surface with its boundary condition (`Outdoors`, `Ground`, `Adiabatic`, or between two zones), internal masses, and the floors it was made from.

## Checking and tracing

Validation
:   The numerical check that a simplified floor or building still holds its prescribed invariants: floor area, volume, exterior wall area, glazed area in total and per orientation, the installed and hourly scheduled magnitude of every load type, and for a building the ground, roof, and exposed floor area and its height; also that the new façades cover the old ones and that every zone is traceable. Tolerances are fixed centrally (relative 1e-6 for areas, 1e-9 for loads). *Validate* shows the result; *Convert2BEM* and *Convert2IDF* refuse to convert a building that fails unless *Override* is set.

Override
:   A Boolean input of both converters. When validation fails and *Override* is true, the conversion runs anyway, with a warning, and the override is written into the *Provenance* output (and the IDF header). Keep that record with any result produced from an overridden model.

Provenance
:   The record of how an object was made: every operation, its parameters, the presets used, and the BEMGen version and commit, nested from the building back to the plan. *Inspect* shows it, and both converters output it with the validation report.

## Levels of detail

The research behind BEMGen describes a model by its level of detail on separate axes:

| Axis | Levels in BEMGen | Where it is chosen |
| --- | --- | --- |
| Zoning (Z) | Z0 detailed zones (one per dwelling or department), Z1 zones of one space type merged, Z1c conditioned and unconditioned zones merged separately, Z2 perimeter zones per orientation plus a core, Z3 one zone per floor | the plan simplifier |
| Vertical (V) | every storey explicit; representative storeys with zone multipliers; one zone per floor type; one zone for the whole building | the floor aggregator and its multipliers |
| Windows | one rule at every level: explicit centred windows whose glazed area is conserved per wall | fixed (the plan generator's WWR) |

Because programs, loads, schedules, glazed area, and the envelope are held equivalent across levels, differences in simulated results between two levels come from geometry, zoning, and the representation of storeys, which is what the study measures.
