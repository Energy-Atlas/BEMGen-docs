# Convert2IDF output

> **Status:** Provisional (ADR-010, realisation pending the owner's reading); program fields, single-sided thermostats, and the calendar-based run period since D-126 ([ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md)) · **Since:** S6 (version 0.9.0, D-113) · **Component:** *Convert2IDF* (`2IDF`), panel *5 Convert*, GUID `56dd6611-90b2-4299-b53c-650652843a1a` · **Code:** `Lod.Export.Idf` (`src/Lod.Export/Idf/`)

## Purpose

*Convert2IDF* is the second converter of the pipeline (D-020). It writes an EnergyPlus 25.2 input file (IDF) from an `IGeneratedBuilding` and an envelope preset, as [ADR-010](../decisions/ADR-010-convert2idf.md) specifies. EnergyPlus is not run, neither by the tests nor by BEMGen (D-112): the file holds the minimum simulation objects, and weather, outputs, and climates are added when simulations are run. Correctness is checked by reading the file back (see [Tests](#tests)).

`Lod.Export` is a plain C# library (`netstandard2.0`) that depends only on `Lod.Core`, never on RhinoCommon or Grasshopper (AGENTS.md). Its tests (`tests/Lod.Export.Tests`) run with `dotnet test`.

## Interface

```csharp
Result<IdfDocument> result = new IdfWriter(ToleranceSettings.Default)
    .Write(building, ExampleEnvelopePresets.Example, new IdfOptions(new HeatTransferOptions(false, false)));
string idf = result.Value.ToText();
```

| Type | Role |
| --- | --- |
| `IdfWriter` | `Write(building, envelope, options)`: validates the building, then builds the document; returns `Result<IdfDocument>` with diagnostics. |
| `IdfOptions` | `HeatTransfer` (`HeatTransferOptions`, D-069, both off by default), `OverrideValidation` (default `false`), `FirstDayOfYear` (weekday of 1 January of the schedules; unset by default, which takes it from the building's calendar, else Monday, as every example preset; a weekday given here must agree with the calendar, D-126). `IdfOptions.Default` has all defaults. |
| `IdfDocument` | `Header` (comment lines), `Objects` (typed objects in file order), `ToText()` (the IDF text with `\n` line ends). |
| `IIdfObject` and the `Idf…` records | One typed record per EnergyPlus class (`IdfZone`, `IdfBuildingSurface`, `IdfScheduleYear`, …), each giving its fields in EnergyPlus 25.2 order. |
| `IdfDefaults` | Every modelling default of the writer, in one place (table below). |
| `Convert2Idf` | `Run(building, envelope, options, file)`: the service behind the component. Validates once, writes the document, saves it with `IdfFile` when `IdfFileRequest.Write` is set, and returns `IdfConversion` (text or `null` when blocked, provenance, whether the file was written, all diagnostics). |
| `IdfFile` | `Save(path, text, overwrite)`: UTF-8 without a byte-order mark, only to an absolute path in an existing folder (the folder is not created), never over an existing file unless `overwrite`. |
| `IdfFormat` | Number formatting: invariant culture, fifteen significant digits (`G15`), `0` for negative zero. Fifteen digits are formatted identically by .NET Framework 4.8 and .NET 8 (the round-trip format `R` is not), and the rounding, at most 5e-15 relative, is far below every tolerance of `ToleranceSettings`. |

## Component

*Convert2IDF* (2IDF) in panel *5 Convert* is a thin adaptor over `Convert2Idf` (GLOBAL.md architecture rule 3): it reads its inputs, runs the service, shows every diagnostic as a runtime message (errors, warnings, info as remarks), and sets its outputs. EnergyPlus is not run.

| Index | Input | Nickname | Access | Content |
| --- | --- | --- | --- | --- |
| 0 | Building | Bldg | item | An `IGeneratedBuilding` from a floor aggregator. |
| 1 | Envelope | Env | item, optional | An envelope preset, for example from *Envelope Preset*; the illustrative `ExampleEnvelopePresets.Example` when unconnected. A connected input that yields no envelope preset (for example from an *Envelope Preset* with an error) also falls back to the example, with the warning `Envelope is connected but yields no envelope preset; the Example Envelope is used instead.` |
| 2 | EnableInternalWallHeatTransfer | IWHT | item | Boolean, default `false` (D-069): walls between zones paired, else adiabatic. |
| 3 | EnableFloorHeatTransfer | FHT | item | Boolean, default `false` (D-069): floors and ceilings between zones paired, else adiabatic. |
| 4 | Override | Ovr | item | Boolean, default `false`: convert even if validation fails; recorded in *Provenance* and in the IDF header. |
| 5 | Path | P | item, optional | Fully qualified path of the IDF file (a drive letter and a separator, or a UNC path `\\server\share\…`), in an existing folder; used only when *Write* is true. Drive-relative (`C:model.idf`) and root-relative (`\model.idf`) paths are rejected (`InvalidParameter`), because they depend on the process's current folder. |
| 6 | Write | W | item | Boolean, default `false`: write the file; when false nothing is written. |
| 7 | Overwrite | O | item | Boolean, default `false`: replace an existing file; when false the existing file is kept and the error `FileExists` is shown. |

| Index | Output | Nickname | Content |
| --- | --- | --- | --- |
| 0 | IDF | IDF | The IDF text; empty when the conversion is blocked. |
| 1 | Provenance | P | The building's provenance tree, the validation report, then `OPTIONS: …`, `ENVELOPE: <preset name>`, `INFILTRATION: <rate> <basis> (EnergyPlus <method>), schedule <name>` (D-124), `ENERGYPLUS: 25.2`, `OVERRIDE: converted despite failed validation` when *Override* was used on a failed validation, and `FILE: written <full path>` or `FILE: not written (<reason>)` (Write is false, the file exists, the conversion was blocked, or see the error). Set on every solve that has a building. |
| 2 | Written | Wr | Whether the file was written in this solution. |

A file is written only when *Write* is true, *Path* is fully qualified and its folder exists, and the file does not exist or *Overwrite* is true; otherwise the error `InvalidParameter`, `FileWriteFailed`, or `FileExists` is shown, *Written* is false, and the *IDF* text is still output. Keep *Write* false while editing a definition: every solve with *Write* and *Overwrite* true rewrites the file.

## Validation gate

`BuildingValidator` (with the writer's tolerances) runs first (GLOBAL.md scientific rule 6). A failed enforced check returns the error `ValidationFailed`, naming the failed checks, and no document. With `OverrideValidation` the file is written, the warning `ValidationOverridden` is returned, and the header records `Validation: FAILED`, every failed check (`  FAIL <check>: <detail>`), and `OVERRIDE: converted despite failed validation`.

## File layout

Every object is written at least up to its `\min-fields` in the EnergyPlus 25.2 IDD, the fields BEMGen does not set holding the IDD defaults explicitly (for `ZoneHVAC:IdealLoadsAirSystem`: no humidification, no outdoor air, no economizer, no heat recovery). Objects are written in a fixed order, each with one field per line and its field name as a comment (hourly values six to a line, a vertex's three coordinates on one line):

1. Header comments: code version (`BuildInfo.InformationalVersion`), the EnergyPlus version and the note that BEMGen does not run the file, the envelope preset, its infiltration (D-124; for example `Infiltration: 0.3 AirChangesPerHour (EnergyPlus AirChanges/Hour), schedule Example Always On`), the heat-transfer options, the first day of the year, the calendar (D-126; `none (BEMGen presets; run period 2007, 1 January a Monday)` or, for example, `2007 (1 January a Monday), holidays 01-01, 12-25`), the validation result, the building's provenance tree, and every zone with its multiplier and source zones (GLOBAL.md scientific rule 2).
2. `Version` (25.2), `SimulationControl` (no sizing, no HVAC sizing simulation; run on the weather-file run periods only), `Building`, `Timestep` (6), `RunPeriod`, `GlobalGeometryRules`, `Site:GroundTemperature:BuildingSurface`.
3. `ScheduleTypeLimits` (`BEMGen Fraction` 0–1, `BEMGen Temperature` unbounded, and when needed `BEMGen Activity Level`, not negative, and `BEMGen Control Type` 0–4), `Schedule:Constant` (the default activity level `BEMGen Activity Level` when a program uses it, and one control type schedule for each kind of thermostat used), then each schedule as its day, week, and year objects, in order of first use (zone by zone, loads before setpoints).
4. `Material` and `WindowMaterial:SimpleGlazingSystem`, then `Construction`: only those used, in the envelope preset's order; the window construction is named after the glazing and has the glazing as its one layer.
5. `Zone`, in building order.
6. `BuildingSurface:Detailed` in building surface order (the pieces of a split surface one after another), then `FenestrationSurface:Detailed`, then `InternalMass`.
7. Loads, zone by zone in program order, each zone's `ZoneInfiltration:DesignFlowRate` from the envelope after its program loads (D-124); then, for every conditioned zone, `ZoneControl:Thermostat`, its `ThermostatSetpoint:DualSetpoint`, `ThermostatSetpoint:SingleHeating`, or `ThermostatSetpoint:SingleCooling` (D-126), `ZoneHVAC:IdealLoadsAirSystem`, `ZoneHVAC:EquipmentList`, and `ZoneHVAC:EquipmentConnections`.
8. `Output:Meter` (monthly): `Heating:EnergyTransfer`, `Cooling:EnergyTransfer`, `Electricity:Facility`, `NaturalGas:Facility`.

The same building, envelope, and options always give the same text.

### Names

Names come from zone and surface IDs (`L0/US1`, `L0/US1/W1`); a split surface's pieces are `<id>#1`, `<id>#2`, …; windows `<wall>/Win<k>`; loads `<zone> <LoadType> <LoadBasis>`, or `<zone> <LoadType> <end use> <LoadBasis>` when the zone holds more than one end use of that type (D-126); infiltration `<zone> Infiltration <InfiltrationBasis>`; internal masses `<zone> Internal Mass <k>`; HVAC objects and nodes `<zone> Thermostat`, `<zone> Ideal Loads`, `<zone> Supply Inlet`, …; schedules keep their names, with `Day <k>` and `Week <k>` for their parts. Names are unique within each group in which EnergyPlus compares them, ignoring case (zones; surfaces, windows, and internal masses together; schedules; …): IDF's reserved characters (`,` `;` `!`) become `_`, a name longer than 100 characters keeps its start and ends with `~` and an FNV-1a hash of the whole name, and a name already taken gets `~2`, `~3`, ….

## Geometry

- **Coordinates.** Vertices are the building's own coordinates in metres, the same as the pipeline's and *Convert2BEM*'s plan frame. `GlobalGeometryRules` uses relative coordinates with every zone origin at 0 and no zone rotation, so the coordinates are used as they are, and `Building` *North Axis* is the building's orientation (`IGeneratedBuilding.OrientationDegrees`, the clockwise rotation of plan north from true north). EnergyPlus therefore sees the same true azimuths as validation does.
- **Vertex order.** Counter-clockwise seen from outside the zone, starting at the upper-left corner (D-091): a wall from its top start corner (the wall runs with its zone on the left, so its outside faces right); a ceiling or roof seen from above from its northernmost, then westernmost vertex; a floor seen from below from its northernmost, then easternmost vertex. Floors face down, ceilings and roofs up, walls and windows out of their zone.
- **Surface types.** Walls are `Wall`; floors `Floor`; ceilings `Roof` when they face outdoors (roofs and terraces, ADR-015), otherwise `Ceiling`.
- **Zones.** Every zone states its multiplier, volume, and floor area (one instance) instead of letting EnergyPlus compute them; a zone spanning storeys (*Single Zone per Floor Type*, *Single Zone Building*) has no surface for the slabs inside it. A zone of several pieces on one storey (*Semantic Merge* or *Conditioned Merge* with *Join Pieces* true, D-123) is one `Zone` as well: its floor area and volume are the sums over its pieces, and it holds the surfaces of every piece, the walls numbered on across the pieces and one floor and one ceiling per piece (`<zone>/F1`, `<zone>/F2`, …). EnergyPlus takes a zone as a set of surfaces and as one air volume, so the air of the pieces is one volume there. The writer needed no change for this.
- **Collinear vertices**, which the pipeline keeps where another zone's vertex meets an edge (ADR-002), are removed: a vertex within the distance tolerance of the segment joining its neighbours is dropped, from the start of the ring, until none is left.
- **Zero-width parts.** The pipeline no longer produces them on generated plans (floors and ceilings are clipped from conformed footprints, ADR-002, and `IdfTypologyTests` asserts that no rotated conversion warns), so this handling and the next are a guard for buildings from elsewhere. Clipping on the grid can leave a floor or ceiling with a part of no width (D-090): a spike, where the boundary runs out to a tip within the distance tolerance of the line through its neighbours and straight back, or an excursion out and back through a repeated vertex. A spike tip is removed with the collinear vertices; a ring still not simple (two vertices or two non-adjacent edges within the distance tolerance) is rebuilt as the union of its own region, which drops such parts, with its vertices put back on the original ones. The rebuilt rings that are not slivers must have the piece's area within the relative area tolerance plus the area of the rebuilt slivers (an excursion subtracts its thin area from the net area and the union adds it back as a sliver); otherwise the ring crosses itself or encloses area twice, is not a zero-width part, and the conversion fails with the error `DegeneratePolygon` instead of writing less area. Either repair is reported with the warning `SliverOmitted`, which names the zone, whether the surface is a floor or a ceiling, its elevation, the area of the slivers omitted, and the number of spikes and excursions removed with the area they changed; the region and its area do not change beyond the tolerance.
- **Holes.** EnergyPlus surfaces cannot have holes. A floor or ceiling with holes (courts, ring zones, ring cores) is cut by one line parallel to the y axis through the middle of each hole's x-range and clipped to the strips between the cuts; every hole is crossed by its own cut, so no piece keeps a hole. The pieces have the polygon's area (checked within the relative area tolerance); clipping rounds to the distance grid, so piece vertices are put back on the polygon's own vertices. The info `SurfaceSplit` names every split surface.
- **Slivers.** Where storeys touch along an edge, clipping on the grid can leave a piece of floor or ceiling narrower than the distance tolerance (about 1e-6 m wide and a few 1e-6 m² in area; D-090). A piece is a sliver when removing collinear vertices leaves fewer than three, or when its area is at most the distance tolerance times its perimeter (its mean width is then at most twice the tolerance; a real 1 m² surface has 4e-6 m² of this bound). It is not written, and the warning `SliverOmitted` names its surface and area; its partner omits the same piece. A floor or ceiling that is nothing but slivers is omitted before partners are matched, so it is neither paired nor reported unpaired (the two sides of such a sliver can clip to no overlap at all).
- **Short edges.** EnergyPlus merges vertices closer than about 0.01 m (`IdfDefaults.EnergyPlusVertexMergeDistance`, EnergyPlus's own distance, not a BEMGen tolerance). Every written surface and window with an edge shorter than that gets the warning `ShortEdge`; the file is still written. No conversion of the tests has one, the rotated and moved plans included.
- **Windows** are `FenestrationSurface:Detailed` rectangles in their wall at their offset and sill (D-039), with the wall's vertex order. A window in a wall that is not written `Outdoors` is the error `InteriorWindow` (no generator places one).

## Heat transfer between zones

Each surface's boundary comes from `HeatTransferOptions.Exported` (D-069, D-077), as in *Convert2BEM*:

| Building surface | Written |
| --- | --- |
| `Outdoors`, `Ground`, `Adiabatic` | the same keyword; `Outdoors` surfaces are sun and wind exposed, the others not |
| Interzone, its option off | `Adiabatic` |
| Interzone, its option on | `Surface`, with its partner in the adjacent zone as boundary object |
| Interzone, option on, zones of different multipliers | `Adiabatic` on both sides, with the warning `InterzoneMultiplierMismatch` naming both |

Partners are found in the building: a wall in the adjacent zone running the other way between the same end points, at the same elevation and height; a floor or ceiling of the other kind in the adjacent zone at the same elevation and with the same polygon (equal area and overlap within the relative area tolerance). A surface without a partner is the error `UnpairedInterzoneSurface`. The first surface of a pair in building order defines the geometry: its partner's pieces are its pieces, each with the vertices in reverse order. A floor uses the interior floor construction and the ceiling below it the reversed one; of two walls between zones, the one whose zone ID sorts after the other zone's ID (ordinal) uses the reversed interior wall (`ConstructionRoles`, the one rule for both converters, ADR-010), so both sides of every pair list the same layers in opposite order. *Stacked Floor Zone Multiplier* buildings have no floor or ceiling between storeys to pair: those pieces are adiabatic in the building itself (D-075).

## Constructions

`ConstructionRoles.Of` (`Lod.Core.Conversion`) gives each surface its construction role from its kind and exported boundary, and the envelope preset its construction ([convert2bem.md](convert2bem.md#constructions), [envelope presets](../research/envelope-presets.md)). Internal masses use the preset's internal-mass construction. Materials are written with roughness `MediumRough` and EnergyPlus's default absorptances (thermal 0.9, solar 0.7, visible 0.7).

## Loads

One object per load component (type, end use, and basis, D-047, D-126), with the load's own fraction schedule:

| Load type | Object | Basis written in its own field | Other bases |
| --- | --- | --- | --- |
| Occupancy | `People` | per floor area (`People/Area`), absolute (`People`) | per dwelling unit: the number of people of the zone's dwellings, absolute (value × dwelling count, D-126) |
| Lighting | `Lights` | per floor area (`Watts/Area`), per person (`Watts/Person`), absolute (`LightingLevel`) | absolute design magnitude, W (per dwelling unit: value × the zone's dwelling count) |
| Electric equipment | `ElectricEquipment` | as lighting (`EquipmentLevel`) | absolute design magnitude, W |
| Gas equipment | `GasEquipment` | as lighting (`EquipmentLevel`) | absolute design magnitude, W |
| Ventilation | `ZoneVentilation:DesignFlowRate` | per floor area (`Flow/Area`), per person (`Flow/Person`), absolute (`Flow/Zone`), air changes (`AirChanges/Hour`) | absolute design magnitude (`Flow/Zone`) |
| Domestic hot water | `WaterUse:Equipment` | — | always the absolute peak flow of one zone instance, with the zone for its multiplier, the load's target temperature schedule and its inlet temperature schedule as the cold-water supply temperature (D-126), and no zone heat gains; written only when a preset defines it (the example presets do not; a program JSON usually does) |

Flows are converted from m³/h to m³/s. Where EnergyPlus has no field for a basis (for example lighting in air changes per hour), the writer writes the absolute design magnitude of one zone instance, value × basis quantity (ADR-007), which EnergyPlus applies identically, because every design-level method resolves to a fixed design level of the zone and the zones state their own floor area and volume. So no load is dropped and no basis is an error. Ventilation and infiltration have the coefficients 1, 0, 0, 0, so the flow is the design flow times the schedule whatever the weather; ventilation is `Balanced` with no fan (pressure rise 0, efficiency 1). Infiltration is not a program load since D-124; see the next section.

**Program fields (D-126).** The fractions and the people's properties that were fixed writer defaults in S6 are program fields now ([domain-model.md](domain-model.md#4-loads-lodcoreloads), [ADR-018](../decisions/ADR-018-program-json-and-extended-programs.md)), and their defaults are the old values, so a program that sets none is written exactly as before:

| Object | Fields written from the program |
| --- | --- |
| `Lights` | `Return Air Fraction`, `Fraction Radiant`, `Fraction Visible` from the load's heat fractions; `Fraction Replaceable` stays 1 (`IdfDefaults.LightsFractionReplaceable`, a daylighting field, not a program field) |
| `ElectricEquipment`, `GasEquipment` | `Fraction Latent`, `Fraction Radiant`, `Fraction Lost` from the load's heat fractions |
| `People` | `Fraction Radiant` and `Sensible Heat Fraction` (the number, or `autocalculate`) from the zone's people properties; `Activity Level Schedule Name` is the zone's activity schedule: the default (constant 120 W per person) as the `Schedule:Constant` `BEMGen Activity Level`, any other as a schedule under the type limits `BEMGen Activity Level` |
| `WaterUse:Equipment` | `Target Temperature Schedule Name` and `Cold Water Supply Temperature Schedule Name` from the load's water temperatures (they were blank, so EnergyPlus's defaults applied); `Hot Water Supply Temperature Schedule Name` stays blank, and the sensible and latent fraction schedules are not written, so water adds no zone heat, as the contract keeps plant and zone gains separate |

A heat fraction in a field the EnergyPlus object lacks (latent or lost on lights, visible or return air on equipment) cannot reach the writer: a program with one is rejected when it is built (`HeatFractionNotSupported`). A per-dwelling load is the absolute design level value × the zone's dwelling count, for one zone instance; EnergyPlus applies the zone multiplier.

## Infiltration

The infiltration of the envelope preset (D-124, [ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)) is written once per zone, after the zone's program loads, conditioned or not: a `ZoneInfiltration:DesignFlowRate` named `<zone> Infiltration <InfiltrationBasis>` with the envelope's fraction schedule (one schedule shared by every zone, written once under its own name), the coefficients 1, 0, 0, 0, and the rate in EnergyPlus's own method for its basis, so that EnergyPlus multiplies the rate by that zone's own quantity, per zone instance before the zone multiplier. The writer computes no flow: no zone merge aggregates infiltration, and EnergyPlus gives each zone the flow of the surfaces and volume the file states for it.

| `InfiltrationBasis` | Design Flow Rate Calculation Method | Rate written in | EnergyPlus multiplies it by |
| --- | --- | --- | --- |
| `PerExteriorSurfaceArea` | `Flow/ExteriorArea` | `Flow Rate per Exterior Surface Area`, m³/s per m² (the rate in m³/h per m² divided by 3600) | the zone's exterior surface area |
| `PerExteriorWallArea` | `Flow/ExteriorWallArea` | the same field | the zone's exterior wall area |
| `AirChangesPerHour` | `AirChanges/Hour` | `Air Changes per Hour`, 1/h | the volume the `Zone` object states |

**The exterior area of EnergyPlus (found by running 26.2).** What EnergyPlus counts as a zone's exterior surface area was checked by running EnergyPlus 26.2, the version at hand, on converted files with a storey moved off the one below (the file targets 25.2, with its version line changed for the run; 25.2 itself has not been run, D-112). Each zone's design flow in the `.eio` was the rate times the zone's outdoor walls, roofs, and exposed floors, with windows included in the gross areas, and without its ground floor; with `Flow/ExteriorWallArea` it was the rate times its outdoor walls alone. Surfaces with the boundary `Ground` or `Adiabatic`, and surfaces between zones, are not counted. BEMGen writes every outdoor wall, roof, and exposed floor of a zone with the boundary `Outdoors` and its full area, so EnergyPlus uses the area of the zone's own surfaces facing outdoors; the slabs between storeys that *Stacked Floor Zone Multiplier* repeats are adiabatic, as in the building itself, and are not counted. The finding is recorded in the comments of `IdfLoads.Infiltration`, and `ZoneInfiltration` in `Lod.Core.Conversion` computes the same areas for *Convert2BEM*'s *Infiltration Flows* ([convert2bem.md](convert2bem.md#infiltration)).

## HVAC and thermostats

Every conditioned zone (D-038) gets `ZoneControl:Thermostat` and the setpoint object of its sides (D-126): `ThermostatSetpoint:DualSetpoint` with control type 4 when it has both a heating and a cooling setpoint schedule, `ThermostatSetpoint:SingleHeating` with control type 1 when it has heating only, `ThermostatSetpoint:SingleCooling` with control type 2 when it has cooling only, each type with its own constant control type schedule (`BEMGen Dual Setpoint Control`, `BEMGen Single Heating Control`, `BEMGen Single Cooling Control`, written when used). Every zone also gets a `ZoneHVAC:IdealLoadsAirSystem` with no heating or cooling limit, in an equipment list connected to the zone. An unconditioned zone gets neither, but keeps its loads and infiltration.

## Schedules

Every 8760-value schedule (ADR-003) is reproduced hour by hour, to fifteen significant digits, as `Schedule:Year` over `Schedule:Week:Daily` and `Schedule:Day:Hourly`: each distinct day of the schedule is one day schedule; the year is cut into seven-day blocks from 1 January, each block a week schedule giving every weekday the day schedule of its date in the block; consecutive equal blocks share one week schedule and one period. The last block, 31 December alone, takes the other weekdays from the block before it, so it merges with that block when its day agrees. A schedule from weekday and weekend profiles is thus two day schedules, one week schedule, and one period. The holiday, design-day, and custom-day types use the Sunday day schedule, and the writer defines no holiday or special day: a program's holidays (D-126) are already in its hourly values, which carry each date's own profile, so the run period applies them without a day type of their own. A program JSON's design-day profiles are not used (they are not days of the year); the design days of the weather file, when one is added, get the Sunday profile. A schedule is written once per name and values; another schedule with the same name but other values gets its own name.

The `RunPeriod` covers 1 January to 31 December of a non-leap year with the weather file's holidays and daylight saving off, so EnergyPlus applies the hourly values on the days they were made for. Since D-126 the year and the weekday come from the building's calendar (the one calendar its zones share, `ProgramChecks.Calendar`): a program JSON built on 2014 gives the year 2014 starting on a Wednesday. Without a calendar (BEMGen's own presets) the year is the one that starts on `IdfOptions.FirstDayOfYear` (Monday if unset): 2007 for Monday (it was 2018 before D-126, also a Monday), 2017 for Sunday, 2019 for Tuesday, 2014 for Wednesday, 2015 for Thursday, 2010 for Friday, and 2011 for Saturday. A weekday given in the options that contradicts the calendar is the error `CalendarMismatch`, and so are zones on different calendars, which no single run period fits (the validation override does not lift it).

## Defaults

The writer's own are in `IdfDefaults`; they are defaults for a runnable file, not values from a standard (ADR-010). The rows marked as program defaults are held by the program since D-126, with the values the writer used before, and are written here only for completeness:

| Default | Value |
| --- | --- |
| Timesteps per hour | 6 |
| Terrain; solar distribution | `Suburbs`; `FullExterior` (no convex zones needed) |
| Convergence tolerances; warm-up days | 0.04 W and 0.4 K; 25 maximum, 6 minimum (EnergyPlus defaults) |
| Ground temperature under the building | 18 °C every month (what EnergyPlus assumes without input; no climate is chosen, D-112) |
| Activity level | 120 W per person (program default since D-126: `PeopleProperties.Default`) |
| People | radiant fraction 0.3, sensible fraction autocalculated (program defaults) |
| Lights | return air 0, radiant 0.42, visible 0.18 (program defaults, `HeatFractions.DefaultFor`); replaceable 1 (writer default) |
| Electric equipment | latent 0, radiant 0.5, lost 0 (program defaults) |
| Gas equipment | latent 0, radiant 0.3, lost 0 (program defaults) |
| Hot-water temperatures | target 60 °C, inlet 10 °C (program defaults, `WaterTemperatures.Default`) |
| Run period without a calendar | 2007, starting on a Monday |
| Ideal loads | supply air 50 °C heating and 13 °C cooling, humidity ratios 0.0156 and 0.0077 (EnergyPlus defaults); no capacity limit |
| Meters | monthly |

## Diagnostics

| Code | Severity | When |
| --- | --- | --- |
| `ValidationFailed` | Error | Validation failed and no override; no document |
| `ValidationOverridden` | Warning | Validation failed and the override was used; recorded in the header |
| `UnpairedInterzoneSurface` | Error | An interzone surface has no partner in the adjacent zone |
| `InterzoneMultiplierMismatch` | Warning | Two partners belong to zones of different multipliers; both written adiabatic |
| `InteriorWindow` | Error | A window lies in a wall not written `Outdoors` |
| `SurfaceSplit` | Info | A floor or ceiling with holes was written as hole-free pieces |
| `SliverOmitted` | Warning | A floor or ceiling piece narrower than the distance tolerance, or a zero-width part of one, was not written |
| `ShortEdge` | Warning | A written surface or window has an edge shorter than the distance at which EnergyPlus merges vertices |
| `NoConstructionRole` | Error | A surface has no construction role (an unresolved boundary, a wall or ceiling on the ground), only possible on an overridden validation |
| `CalendarMismatch` | Error | The zones' programs were expanded on different calendars, or `IdfOptions.FirstDayOfYear` contradicts the building's calendar (D-126); no override |
| `InvalidParameter` | Error | *Write* is true but *Path* is not a fully qualified file path (the component) |
| `FileExists` | Error | The file exists and *Overwrite* is false; it is kept (the component) |
| `FileWriteFailed` | Error | The folder does not exist or the file could not be written (the component) |
| `DegeneratePolygon` | Error | Splitting or cleaning a polygon failed, or a floor or ceiling crosses itself so that rebuilding it would change its area (no building of the tests has one) |

## Tests

`tests/Lod.Export.Tests` checks every part on its own (text and names, schedules, geometry, loads, the writer), and whole files by reading them back with a small IDF parser (`Support/IdfParser.cs`, `Support/IdfChecks.cs`), without EnergyPlus:

- **Counts and references:** zones, ideal-loads systems, thermostats, windows, internal masses, and load objects as in the building; every surface's zone and construction, every construction's layers, every window's wall, every load's zone and schedule, every thermostat's schedules, and every year schedule's weeks and days exist; names are unique as EnergyPlus requires and at most 100 characters.
- **Partners:** every `Surface` boundary points to a surface in another zone that points back, with its vertices reversed and its construction's layers reversed; with the options on, every surface between zones of equal multipliers is paired; with both off, none is.
- **Geometry:** every surface and window is planar and simple (no hole, slit, or repeated vertex), walls are vertical, floors face down, ceilings and roofs up, and windows face as their wall does.
- **Invariants against the building**, counting multipliers: floor area and volume, exterior wall, ground, roof, and exposed floor area, the floor and ceiling surface area by surface type and written boundary (ground, outdoors, partner surface, adiabatic), so a missing or extra piece shows even where the zone fields agree, internal-mass area, glazing in total and per orientation (from the window normals and the north axis), and installed and hourly scheduled magnitude per program load type, from the IDF's own design levels and expanded schedules (relative load tolerance), and the infiltration (D-124): one object per zone in the method of the envelope's basis, with the envelope's rate and schedule, whose flow from the IDF's own surfaces and volumes, as EnergyPlus reads them, equals `ZoneInfiltration.DesignFlow` zone by zone and in the installed total (`IdfInfiltrationTests`, `IdfChecks`).
- **Coverage:** the canonical linear plan (multipliers 1, 2, 1) through every simplifier and aggregator with both settings; the enclosed court, the court cluster, and the office plate (multipliers 1, 3, 1) and the stepped band (its three storeys) the same way; each of these five plans also rotated by 30° and moved by (5.3, −2.1) m, and the linear plan with an orientation of 30° (north axis and glazing per orientation end to end); on the rotated plans only zero-width parts may be omitted, and what is written of each such surface keeps its area. A plan with every load kind and basis (hot water, gas, ventilation; per person, absolute) is converted too, and the canonical linear plan through every combination with each infiltration basis. No conversion has a short edge. Negative tests break one thing in a correct file and expect the checks to name it.
- **Snapshots** (`tests/Lod.Export.Tests/Snapshots/idf-*.txt`): the minimal linear plan in full, and four combinations of the canonical plan that cover each simplifier, each aggregator, and both settings once (one file per combination of the sixteen would be tens of thousands of lines; every combination is read back instead). Numbers are compared to the building within the tolerances of `ToleranceSettings`, because they are written with fifteen significant digits. Since D-124 every snapshot has the header line `Infiltration:`, and in five of them (four of the canonical plan and the stair-bay bar's of D-123) the infiltration of every zone uses the one envelope schedule, written once, where each zone had its own aggregated schedule.
- **Program fields (D-126)** (`IdfProgramPropertiesTests`, `IdfExtendedProgramMatrixTests`, `IdfProgramJsonTests`): the heat fractions, people properties, water temperatures, and per-dwelling levels the IDF holds equal the program's; the three thermostat kinds and their control type schedules; two end uses of one type with their own names; the run period of a calendar and of no calendar; the options' weekday against the calendar; the Medium Office program JSON through the office plate, every plan simplifier, and every floor aggregator to a validated building and an IDF that reads back. Six IDF snapshots gained the header line `Calendar:` and the run-period year 2007 in place of 2018, and nothing else.
- **Zones of several pieces (D-123)** (`IdfMultiPartZoneTests`): the stair-bay bar under *Conditioned Merge* with *Join Pieces* true, two storeys stacked, gives per storey one conditioned zone of four pieces and one unconditioned zone of three. With both heat-transfer settings its IDF reads back with consistent references and the building's invariants; each such zone is one `Zone` with one floor surface per piece and the zone's floor area and volume; the interzone walls between the two zones are paired; and one snapshot holds the file (`idf-StairBayBar-ConditionedMerge-JoinPieces-Stack-on.txt`). With the upper storey moved so that every upper piece overhangs, each basis of the infiltration (D-124) is applied to the outdoor walls, roofs (`C1`, `C2`, …), and exposed floors of every piece of a zone, and the flow EnergyPlus computes from the IDF equals `ZoneInfiltration.DesignFlow` zone by zone.

## IDD check

`scripts/idd-check/idd_check.py` checks IDF files against the EnergyPlus IDD (class names, field counts and `\min-fields`, required fields, choice keys, numeric limits, references, unique objects); the IDD stays outside the repository (`scripts/idd-check/README.md`). With `BEMGEN_IDF_OUT` set, the export tests write every file they convert. Last run: 2026-10-02, against the EnergyPlus 25.2.0 IDD (`idd/Energy+.idd.in` at the tag `v25.2.0`), 355 files (the 32 linear-plan combinations, the four plans with holes or storeys and all five plans rotated and moved, each through the 32 combinations, the linear plan with orientation 30°, the two load-kind plans, and the minimal plan): 0 problems. Every class the writer uses was also compared field by field with the IDD. Repeated on 2026-10-07 for D-124 against the same IDD (`idd/Energy+.idd.in` at `v25.2.0`): 579 files, now including the infiltration-basis tests written by `IdfInfiltrationTests` (16 files each in `Flow/ExteriorArea` and `Flow/ExteriorWallArea`, the rest in `AirChanges/Hour`): 0 problems. Repeated on 2026-10-07 for version 1.1.0 (D-125) on the integrated Conditioned Merge and program mix, again against the EnergyPlus 25.2.0 IDD: 1016 files, all three infiltration methods, 0 problems. The count is higher because 288 files of the joined merge modes, named after `ConditionedMerge:JoinPieces` and the like, had been written with a colon in the name; on Windows that makes an alternate data stream that a folder listing does not show, so the check had never seen them. The export tests now write every IDF under a plain name (`IdfOut.FileName` replaces each character a file name cannot hold with `_`). Repeated on 2026-10-07 for version 1.2.0 (D-126) against the same IDD: 1073 files, 0 problems, now including single heating and single cooling thermostats, the water-use temperature fields, the people sensible fraction, the heat fractions of two lighting end uses, and per-dwelling loads written as absolute levels (the files of `IdfProgramPropertiesTests`, `IdfExtendedProgramMatrixTests`, and `IdfProgramJsonTests`).

## Headless Rhino check

`scripts/rhino-smoke/specs/convert-idf.py` runs the component in Rhino 8 for the linear plan and the enclosed court through every simplifier and aggregator, writing each file to a folder next to the result file, outside the repository; it also checks *Write* false, *Overwrite*, a missing path, a failed *Envelope Preset* wired into both converters (the warning), *Envelope Preset*, and *Convert2BEM*'s envelope input and construction outputs. In Rhino the spec counts each IDF's objects and main classes and the files are then run through the IDD check (`scripts/idd-check`); the parse-back of references, partners, geometry, and invariants against the building runs in the unit tests (`Lod.Export.Tests`, [Tests](#tests)), not in Rhino. The 2026-10-02 run and the IDD check of the files it wrote are recorded in the [smoke test](../development/grasshopper-smoke-test.md) S6 checklist. A failed validation cannot be produced from the components (every aggregator's building validates), so the blocking and the override are covered by the unit tests only (`Convert2IdfTests`, `IdfWriterTests`). `merge-pieces.py` (D-123) converts every merge mode of the Stair Bay Bar with every aggregator and checks one `Zone` object per zone of the building.

## To verify on the first EnergyPlus run

Recorded in ADR-010 (D-112): zones spanning storeys state their own floor area, and per-area loads there rely on EnergyPlus using the stated zone floor area; the window construction has the same name as its glazing material.

## Not yet decided

Weather, climate, location, design days, outputs beyond the four meters, and running EnergyPlus (D-112); sourced envelope and program values (D-023). The metabolic rate and the load fractions became program fields in D-126; shared services of the program JSON contract are not modelled.
