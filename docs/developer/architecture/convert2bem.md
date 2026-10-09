# Convert2BEM output

> **Status:** Provisional (D-023) · **Since:** S2 (`v0.2.0`); envelope S6; infiltration outputs D-124; program outputs 22 to 30 D-126 · **Component:** *Convert2BEM* (`2BEM`), panel *5 Convert*, GUID `d091d70c-4de3-4f29-a900-ea4c9b777ba3`

## Purpose

*Convert2BEM* is the last step of the BEMGen pipeline (D-018). It turns an `IGeneratedBuilding` into plain Grasshopper data trees that serve the two uses of the pipeline's deliverable (D-016): visualising and checking the building in Rhino, and wiring zones, programs, and surfaces into a ClimateStudio definition. It does not run a simulation.

ClimateStudio is the downstream target (D-006, D-016), but no ClimateStudio reference definition is available yet (D-023). Until one is, the component produces the neutral layout described here: one tree branch per zone, standard Grasshopper types (Brep, text, integer, Boolean, number), and every number in a stated unit. Once a reference definition exists, the output is adapted to ClimateStudio's actual inputs; that change updates this document and the decision log.

The component is a thin adaptor (GLOBAL.md, architecture rule 3): it converts geometry to Rhino Breps through `Lod.Grasshopper.Convert.RhinoGeometry` and copies zone programs and boundary conditions. It computes one new quantity, the design infiltration flow of each zone (D-124, [Infiltration](#infiltration)); everything else is copied from the building and the envelope preset unchanged.

## Input

| Index | Name | Nickname | Access | Content |
| --- | --- | --- | --- | --- |
| 0 | Building | Bldg | item | An `IGeneratedBuilding` from a floor aggregator; in S2 from *Stack Floors*. |
| 1 | Override | Ovr | item | Boolean, default `false`. Convert even if validation fails; the override is recorded in *Provenance*. |
| 2 | EnableInternalWallHeatTransfer | IWHT | item | Boolean, default `false` (D-069, S4.2). When `false`, every wall between two zones is written `Adiabatic`; when `true`, it is written `Interzone:<zone ID>`. See [Heat transfer between zones](#heat-transfer-between-zones). |
| 3 | EnableFloorHeatTransfer | FHT | item | Boolean, default `false` (D-069, S4.2). The same for floors and ceilings between two zones. |
| 4 | Envelope | Env | item, optional | An envelope preset (S6, ADR-010), for example from *Envelope Preset*; when unconnected, the illustrative `ExampleEnvelopePresets.Example`. A connected input that yields no envelope preset (for example from an *Envelope Preset* with an error) also falls back to the example, with the warning `Envelope is connected but yields no envelope preset; the Example Envelope is used instead.` See [Constructions](#constructions). |

From S3 (`v0.3.0`) the component validates the building before converting it; see [Validation gate](#validation-gate).

## Validation gate

From S3 (`v0.3.0`) *Convert2BEM* validates the building before converting it (GLOBAL.md, scientific rule 6; checks and tolerances in [validation.md](validation.md)).

1. `BuildingValidator` with `ToleranceSettings.Default` runs on every solve.
2. Passed: the conversion runs, outputs 0–14 and 16–30 are filled, and *Provenance* holds the building's provenance tree followed by the validation report, the line `OPTIONS: EnableInternalWallHeatTransfer=<True|False> EnableFloorHeatTransfer=<True|False>`, the line `ENVELOPE: <preset name>`, and since D-124 the line `INFILTRATION: <rate> <basis> (EnergyPlus <method>), schedule <schedule name>`, worded as *Convert2IDF*'s, and since D-126 the line `CALENDAR: <calendar>` (the calendar the building's schedules were expanded on, or `none (BEMGen presets: a year whose 1 January is a Monday)`).
3. Failed and *Override* `false` (the default): the component shows the error `ValidationFailed`, outputs 0–14 and 16–30 stay empty, and only *Provenance* is set, so the failing checks can be read.
4. Failed and *Override* `true`: the component shows the warning `ValidationOverridden`, the conversion runs, and *Provenance* ends with the line `OVERRIDE: converted despite failed validation`.

Only enforced checks decide the outcome. The conditioned floor area is reported as a `note` line and never blocks (D-038); ground, roof, and exposed floor area (D-046) and building height (D-045) are enforced. The override is recorded only in *Provenance*, not in the building, so keep that text with any result produced from an overridden model.

## Zone order and tree paths

- Branch `{i}` belongs to zone `i` of `IGeneratedBuilding.Zones`, in the building's zone order. For *Stack Floors* that is storey by storey from the bottom (zone IDs `L0/…`, `L1/…`, …) and, within a storey, the floor's zone order; for the linear plan `ST`, `CO`, `US1` … `USn`, `UN1` … `UNn`. *Stacked Floor Zone Multiplier* lists its modelled storeys the same way; *Single Zone per Floor Type* has one zone per floor entry, `E0`, `E1`, …, bottom to top; *Single Zone Building* has the one zone `BUILDING`.
- Paths are explicit, so `{i}` means zone `i` in every output. *Names*, *Space Types*, *Multipliers*, *Conditioned*, *Heating Setpoints*, *Cooling Setpoints*, *Internal Mass*, and *Infiltration Flows* always have a branch for every zone; the setpoint branches of an unconditioned zone are empty, and since D-126 so is the branch of a side that is off in a conditioned zone (a zone that is heated only has an empty cooling branch). *Load End Uses* has a branch for every zone; *Dwelling Units*, *Activity*, *People Radiant*, and *People Sensible* (D-126) have one for every zone too. Another output can lack the branch of a zone that has no items of its kind (for example a zone without windows or without loads); match branches by path, not by position.
- Loads: item `k` of branch `{i}` in *Load Types*, *Load Bases*, and *Load Values* describes the same load, and its schedule is branch `{i;k}` of *Load Schedules*. Loads are in program order: by `LoadType` (Occupancy, Lighting, ElectricEquipment, GasEquipment, DomesticHotWater, Ventilation), then by end use (ignoring case, then ordinally), then by `LoadBasis` (PerFloorArea, PerPerson, Absolute, AirChangesPerHour, PerDwellingUnit). Infiltration is not a load since D-124; it has its own outputs, 18 to 21. A zone has at most one load per type, end use, and basis; components of the same type in different bases or end uses add up (D-047, D-126). *Load End Uses* (output 22) is aligned with *Load Types* item by item, and *Heat Fractions*, *Water Target*, and *Water Inlet* (outputs 23, 28, 29) have one branch `{i;k}` for every load `k` of zone `i`, numbered as in *Load Schedules*, empty when the load has none of that kind.
- *Surfaces*, *Boundaries*, and *Constructions* are aligned item by item within a branch.
- *Windows* are not aligned with *Surfaces*: branch `{i}` lists every window of zone `i`'s walls, wall by wall and, within a wall, by offset; walls without windows contribute nothing. *Window Constructions* is aligned with *Windows* item by item.

## Outputs

| Index | Name | Nickname | Tree layout | Content | Units |
| --- | --- | --- | --- | --- | --- |
| 0 | Zones | Z | `{i}`: one closed Brep per zone part | Zone volume: each part's floor polygon extruded by its floor-to-floor height, with coplanar faces merged so that a merged zone shows no seam where its source zones met. A zone has one part, except in two cases. In *Single Zone per Floor Type* and *Single Zone Building* buildings it has one part per storey outline (the viewport preview merges them into one volume; this output does not). A floor zone made by *Semantic Merge* or *Conditioned Merge* with *Join Pieces* true has one part per piece (D-123), so its branch holds one closed Brep per piece, for example four for the conditioned zone and three for the unconditioned zone of the Stair Bay Bar; the viewport preview shows them as separate solids too, never united. Every Brep is outward-oriented: its faces point out of the volume, so its volume is positive. | model units |
| 1 | Names | N | `{i}`: one text | Zone ID, e.g. `L0/US1` (the floor aggregator prefixes `L{k}/` for storey `k`). | — |
| 2 | Space Types | ST | `{i}`: one text | `SpaceType` name: `DwellingUnit`, `Corridor`, `Stair`, `Core`, `Lobby`, `Service`, `Mechanical`, `Other`, `Mixed`, or one of the non-residential types of ADR-014 (`Office`, `Retail`, `Mall`, `Kitchen`, `Dining`, `OperatingTheatre`, `CleanCorridor`, `DirtyCorridor`, `ClinicalSupport`, `CareBedroom`, `CareCommunal`, `ActivityHall`). | — |
| 3 | Multipliers | M | `{i}`: one integer | Zone multiplier: the number of storeys a representative storey stands for in *Stacked Floor Zone Multiplier*; always 1 for the other aggregators. | — |
| 4 | Conditioned | Cd | `{i}`: one Boolean | Whether the zone is conditioned, i.e. its program has a thermostat (D-038). | — |
| 5 | Load Types | LT | `{i}`: one text per load | `LoadType` name of each load. | — |
| 6 | Load Bases | LB | `{i}`: one text per load | `LoadBasis` name of each load, aligned with *Load Types*. | — |
| 7 | Load Values | LV | `{i}`: one number per load | Design value of each load in its basis, aligned with *Load Types*. A per-dwelling value is per dwelling; the zone's magnitude is the value times *Dwelling Units* (output 24). | SI, by basis (see below) |
| 8 | Load Schedules | LS | `{i;k}`: 8760 numbers | Hourly fraction schedule of load `k` of zone `i` (non-leap year). | fraction, 0–1 |
| 9 | Heating Setpoints | HS | `{i}`: 8760 numbers, or empty | Hourly heating setpoint of a zone that is heated; the branch is empty for an unconditioned zone and for a conditioned zone without heating (D-126). | °C |
| 10 | Cooling Setpoints | CS | `{i}`: 8760 numbers, or empty | Hourly cooling setpoint of a zone that is cooled; the branch is empty for an unconditioned zone and for a conditioned zone without cooling (D-126). | °C |
| 11 | Surfaces | S | `{i}`: Breps | The zone's surfaces in building surface order (for *Stack Floors*: its walls, then its floors and ceilings). A wall is one planar rectangle; a floor or ceiling gives the planar Breps of its polygon, one face with an inner loop per hole (a zone of several pieces has one floor and one ceiling per piece, D-123). Every surface faces out of its zone: a wall towards its outward side (its azimuth), a floor down, a ceiling (or roof) up, also where the surface is interzone. | model units |
| 12 | Boundaries | B | `{i}`: one text per *Surfaces* item | Boundary written for the surface at the same index (format below): its boundary condition, except that interzone surfaces are `Adiabatic` unless their heat-transfer option is on (D-069). | — |
| 13 | Windows | W | `{i}`: Breps | Every explicit window of the zone's walls, as a rectangle in the wall's plane at its offset along the wall and its sill height (D-039). That is one centred window per glazed outdoor wall: as the generator placed it (D-026) where walls are not rebuilt, and with the glazed area of the source windows the wall covers where zones are merged (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)). A window faces the way its wall faces, out of the zone. | model units |
| 14 | Internal Mass | IM | `{i}`: one number | Exposed internal-mass area: the sum of slab area × exposed faces over the zone's internal-mass objects; 0 when it has none. | m² |
| 15 | Provenance | P | item: one text | The building's provenance tree, then the validation report (`PASSED` or `FAILED`, then one line per check), then the line `OPTIONS: EnableInternalWallHeatTransfer=… EnableFloorHeatTransfer=…` with the values used, then the line `ENVELOPE: <preset name>` (S6), then the line `INFILTRATION: <rate> <basis> (EnergyPlus <method>), schedule <schedule name>` (D-124, worded as *Convert2IDF*'s; for example `INFILTRATION: 0.3 AirChangesPerHour (EnergyPlus AirChanges/Hour), schedule Example Always On`), then the line `CALENDAR: <calendar>` (D-126; for example `CALENDAR: 2007 (1 January a Monday), holidays 01-01, 12-25`), then the line `OVERRIDE: converted despite failed validation` when *Override* was used. Set on every solve that has a building, including blocked ones. | — |
| 16 | Constructions | Con | `{i}`: one text per *Surfaces* item | Name of the envelope preset's construction for the surface at the same index, by its envelope role (S6, ADR-010; see [Constructions](#constructions)). | — |
| 17 | Window Constructions | WCon | `{i}`: one text per *Windows* item | Name of the window construction for the window at the same index: the envelope preset's glazing. | — |
| 18 | Infiltration Rate | IR | item: one number | The envelope preset's infiltration design rate (D-124), the same for every zone, in the unit of *Infiltration Basis*. | m³/h per m², or 1/h (see below) |
| 19 | Infiltration Basis | IB | item: one text | What *Infiltration Rate* is per: `PerExteriorSurfaceArea` (outdoor walls, roofs, and exposed floors, windows included), `PerExteriorWallArea`, or `AirChangesPerHour`. | — |
| 20 | Infiltration Schedule | IS | item: 8760 numbers | The fraction schedule that multiplies the infiltration of every zone (non-leap year). | fraction, 0–1 |
| 21 | Infiltration Flows | IF | `{i}`: one number | Design infiltration flow of one instance of zone `i` at a schedule fraction of 1: *Infiltration Rate* times the zone's own exterior surface area, outdoor wall area, or volume, by the basis (`ZoneInfiltration`, see [Infiltration](#infiltration)). Times *Infiltration Schedule* it is the hourly flow, and times *Multipliers* that of every instance. | m³/h |
| 22 | Load End Uses | LE | `{i}`: one text per load | End use of each load, aligned with *Load Types*: `occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water`, `ventilation` by default, or the end use the load was given, such as `additional_lighting` (D-126). Loads of one type with different end uses are separate loads. | — |
| 23 | Heat Fractions | HF | `{i;k}`: five numbers, or empty | Radiant, latent, lost, visible, and return-air fraction of load `k` of zone `i`, in that order; the rest of the heat is convective. Empty for loads other than lighting, electric equipment, and gas equipment. | fraction, 0–1 |
| 24 | Dwelling Units | DU | `{i}`: one number | Number of dwellings of one instance of zone `i`, the quantity per-dwelling loads are multiplied by: 1 for a dwelling-unit zone, 0 for a zone without dwellings, fractional for a merged zone holding part of a dwelling. | dwellings |
| 25 | Activity | Act | `{i}`: 8760 numbers | Hourly activity level of the occupants of zone `i` (non-leap year). | W per person |
| 26 | People Radiant | PR | `{i}`: one number | Radiant fraction of the occupants' sensible heat in zone `i`. | fraction, 0–1 |
| 27 | People Sensible | PS | `{i}`: one text | Sensible heat fraction of the occupants of zone `i`: a number, or `autocalculate`. | fraction, 0–1, or `autocalculate` |
| 28 | Water Target | WT | `{i;k}`: 8760 numbers, or empty | Hourly target (mixed-water) temperature of hot-water load `k` of zone `i`; empty for loads other than hot water. | °C |
| 29 | Water Inlet | WI | `{i;k}`: 8760 numbers, or empty | Hourly inlet (cold-water supply) temperature of hot-water load `k` of zone `i`; empty for loads other than hot water. | °C |
| 30 | Calendar | Cal | item: one text | The calendar the building's schedules were expanded on (year and holidays), which *Convert2IDF* writes as its run period; `none (BEMGen presets: a year whose 1 January is a Monday)` for BEMGen's own presets. With *Override* and zones on different calendars no one calendar describes the building: the output stays unset and the component shows a warning. | — |

### Load value units

Each load's design magnitude is its value times the basis quantity (ADR-007). Magnitudes are in people (Occupancy), W (Lighting, ElectricEquipment, GasEquipment), or m³/h (DomesticHotWater, Ventilation).

| Load Basis | Unit of the Load Value |
| --- | --- |
| `PerFloorArea` | magnitude per m² of zone floor area |
| `PerPerson` | magnitude per occupant |
| `Absolute` | magnitude per zone |
| `AirChangesPerHour` | air changes per hour (1/h); the magnitude is value × zone volume, in m³/h |
| `PerDwellingUnit` | magnitude per dwelling (D-126); the magnitude is value × the zone's dwelling count (output 24) |

Load values, end uses, heat fractions, conditioning, setpoints, the occupants' properties, and the water temperatures are copied from the zone program unchanged (outputs 22 to 30 were appended in D-126, so the earlier outputs keep their positions and their wires). For Z0 buildings (*No Simplification*, *Stack Floors*) they are the program preset values; with the example presets the stair is unconditioned (illustrative, D-038).

## Boundary text format

| Text | Meaning |
| --- | --- |
| `Outdoors` | Outdoor air: exterior walls, roofs (ceilings of the top storey), the part of a ceiling not covered by the storey above (setbacks), and the part of a floor not covered by the storey below. |
| `Ground` | Ground contact: floors of the lowest storey. |
| `Adiabatic` | No heat transfer. Written for every surface between two zones whose heat-transfer option is off (the default, D-069), and for the floors and ceilings of *Stacked Floor Zone Multiplier* storeys that lie between two storeys, which are adiabatic in the building itself whatever the options say (D-075). |
| `Interzone:<zone ID>` | Another zone of the same building, e.g. `Interzone:L1/US1`: walls between zones when *EnableInternalWallHeatTransfer* is on, floors and ceilings between storeys (or, for *Single Zone per Floor Type*, between floor entries) when *EnableFloorHeatTransfer* is on. Every interzone surface has a matching surface in the other zone that refers back to it. |

There is no separate roof condition: a roof is an `Outdoors` ceiling. `Unresolved` marks floors and ceilings of plans and floors before stacking; a building from a floor aggregator has none.

## Heat transfer between zones

Since S4.2 (D-069) heat transfer between zones is a choice of the conversion, not of the building model. The building keeps its interzone surfaces, and its validation does not depend on the options. *Convert2BEM* writes each surface's boundary through `HeatTransferOptions.Exported` in `Lod.Core` (namespace `Lod.Core.Conversion`), which *Convert2IDF* (S6) uses too:

| Surface | IWHT `false`, FHT `false` (default) | IWHT `true` | FHT `true` |
| --- | --- | --- | --- |
| Wall between two zones | `Adiabatic` | `Interzone:<zone ID>` | `Adiabatic` |
| Floor or ceiling between two zones | `Adiabatic` | `Adiabatic` | `Interzone:<zone ID>` |
| Any other surface | its boundary | its boundary | its boundary |

For the canonical linear plan with Multipliers 1, 3, 1 and *Stack Floors*, the 90 interior walls and the 48 floors and ceilings between storeys are `Adiabatic` by default; for *Single Zone per Floor Type* the 24 floor and ceiling pieces between the three entries are; *Single Zone Building* has no interzone surface, so the options change nothing.

## Constructions

Since S6 every surface and window gets a construction from one envelope preset ([ADR-010](../decisions/ADR-010-convert2idf.md), [envelope presets](../research/envelope-presets.md)), the same preset *Convert2IDF* uses, so both outputs describe one envelope; it is the same at every level of detail. `ConstructionRoles.Of` in `Lod.Core.Conversion` gives each surface its role from its kind and the boundary written for it:

| Surface | Boundary written | Role | Construction (example preset) |
| --- | --- | --- | --- |
| Wall | `Outdoors` | Exterior wall | Example Exterior Wall |
| Wall | `Interzone:<zone>` or `Adiabatic` | Interior wall; reversed on the side whose zone ID sorts after the adjacent zone's | Example Interior Wall (symmetric, so its own reverse) |
| Floor | `Ground` | Ground floor | Example Ground Floor |
| Floor | `Outdoors` | Exposed floor | Example Exposed Floor |
| Floor | `Interzone:<zone>` or `Adiabatic` | Interior floor | Example Interior Floor |
| Ceiling | `Outdoors` (roof, terrace) | Roof | Example Roof |
| Ceiling | `Interzone:<zone>` or `Adiabatic` | Interior floor, reversed | Example Interior Floor Reversed |

The heat-transfer options never change a role, only the boundary. A ceiling between storeys is the other side of the slab whose floor uses the interior floor construction, so it gets the reversed layer order (`Construction.Reversed`, named `"<name> Reversed"`; a symmetric construction is its own reverse). Of the two walls between two zones, the one whose zone ID sorts after the other zone's ID (ordinal) is reversed, so both sides of an asymmetric partition list its layers in opposite order. The envelope preset's internal-mass construction is not output: *Internal Mass* (output 14) is only the exposed area, and the construction (the interior floor slab in the example, D-031) is written by *Convert2IDF*. If the building has a surface without a construction role (an unresolved boundary or a wall or ceiling on the ground, only possible with *Override* on a building that failed validation), the component shows the error `NoConstructionRole` and sets only *Provenance*. The layers themselves are not output: they are in the envelope preset, which *Inspect* or a script can read. How ClimateStudio takes constructions is decided with the ClimateStudio mapping (D-023).

## Infiltration

Since D-124 ([ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)) infiltration is an input of the envelope preset, not a load of the zone programs: its magnitude follows each zone's own surfaces or volume, which a program does not know. The same preset *Convert2IDF* uses gives it, so both outputs apply one infiltration. *Convert2BEM* gives the building's infiltration once (outputs 18 to 20, the same for every zone) and each zone its design flow (output 21), so that a ClimateStudio definition can take the flow as it is, whatever the basis. `ZoneInfiltration` in `Lod.Core.Conversion` computes the flow from the building's surfaces, with the quantities EnergyPlus uses for the three methods *Convert2IDF* writes:

| *Infiltration Basis* | *Infiltration Rate* | *Infiltration Flows* of a zone, m³/h |
| --- | --- | --- |
| `PerExteriorSurfaceArea` | m³/h per m² | rate × the gross area (windows included) of the zone's surfaces whose boundary is `Outdoors`: walls, roofs, and exposed floors; not floors on the ground, adiabatic surfaces, or surfaces between zones |
| `PerExteriorWallArea` | m³/h per m² | rate × the gross area (windows included) of the zone's outdoor walls |
| `AirChangesPerHour` | 1/h | rate × the zone's volume |

Each flow is of one zone instance, before the zone multiplier, as EnergyPlus applies a design flow rate. The building's own boundaries decide, not the exported ones: the heat-transfer options (D-069) only turn surfaces between zones adiabatic, so they never change a flow, and the slabs between storeys that *Stacked Floor Zone Multiplier* turns adiabatic are not counted. The tests of *Convert2IDF* compare every zone's infiltration, read from the IDF as EnergyPlus reads it, with this flow, so the two converters agree zone by zone ([convert2idf.md](convert2idf.md#loads)). The infiltration is not aggregated by any zone merge; it follows each target zone's own surfaces, so the building's infiltration is conserved wherever the exterior wall, roof, and exposed floor areas and the volume are ([validation.md](validation.md#infiltration-and-program-mixes-d-124)).

## Units and coordinates

- Pipeline geometry is in metres in a building-local plan frame: +Y is plan north, and elevation 0 is the bottom of the lowest storey.
- *Convert2BEM* scales every Brep from metres to the model units of the active Rhino document (`RhinoMath.UnitScale(UnitSystem.Meters, doc.ModelUnitSystem)`), about the world origin. Without an active document the scale is 1.
- Only geometry is converted. *Load Values*, *Load Schedules*, setpoints, *Internal Mass*, and the infiltration outputs (*Infiltration Flows* in m³/h) stay in the units listed above, whatever the model units are.
- The building orientation (`IGeneratedBuilding.OrientationDegrees`, the clockwise rotation of plan north from true north) is not applied to the geometry and is not an output; see *Not yet decided*.

## Internal mass

An `InternalMass` object (D-031) describes a slab whose faces both lie inside one zone. This happens when a single-zone aggregator merges storeys into one zone: *Single Zone Building* (all storeys, D-021) and *Single Zone per Floor Type* (the storeys of one floor entry, D-071). The slabs between storeys of that zone are then no longer boundaries between two zones and become internal mass, keeping their construction and area (D-031; ADR-009, ADR-013). Each object records the slab area (one face) and the number of faces exposed to the zone air. *Internal Mass* gives, per zone, the sum of slab area × exposed faces: the slab surface area that exchanges heat with the zone air, in m². Walls between merged zones are discarded, not turned into internal mass (D-034).

*Stack Floors* and *Stacked Floor Zone Multiplier* create no internal mass, so their output is 0 for every zone.

## Not yet decided

- **ClimateStudio mapping.** Which ClimateStudio components and inputs each output feeds, and in what form, is unknown until a ClimateStudio reference definition exists (D-023). This includes how loads and their schedules, infiltration, conditioning and setpoints, windows, boundary conditions, zone multipliers, and internal mass are represented there. The layout above will change accordingly.
- **Orientation.** The geometry stays in the plan frame and the orientation is not output. Whether *Convert2BEM* rotates the geometry to true north or passes the orientation on is decided together with the ClimateStudio mapping.
- **Constructions in ClimateStudio.** Since S6 *Convert2BEM* outputs the construction name of every surface and window from the envelope preset (ADR-010); how ClimateStudio receives constructions and their layers is decided with the ClimateStudio mapping.
- **Simulation.** Not part of the pipeline: ClimateStudio or EnergyPlus runs only after the pipeline, outside BEMGen (D-016). *Convert2BEM* prepares inputs and nothing else.
