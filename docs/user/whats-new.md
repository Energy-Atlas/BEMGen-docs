# What's new

This page says what each version changed and what to do about definitions saved with an earlier one. The other pages of this guide describe version 1.2.0.

## 1.2.0

Version 1.2.0 reads programs from the Energy Archetype Atlas, and a program can now hold everything such a program describes: end uses, heat fractions, the occupants' activity, heating and cooling as separate sides, hot-water temperatures, loads per dwelling, and a calendar with holidays.

### Program JSON

*Program JSON* (PJson), in panel *1 Program*, turns the text of a program JSON 2.0.0 file from the atlas into a program preset. It reads only the **defaulted** export, in which the atlas has filled in every unknown value; a raw export is rejected with a message to export the defaulted form. It reads no file and no network: connect the JSON text itself, for example from a *Panel* or a file read by Grasshopper.

The text is checked against the program JSON schema and the contract's rules before anything is made, and every message names the place in the JSON it concerns. The preset then holds the JSON's loads, end uses, heat fractions, people, heating and cooling, hot-water temperatures, and every schedule, expanded hour by hour on the calendar of *Year* (default 2007, which must not be a leap year) and *Holidays* (MM-DD text, such as `07-04`, on which the JSON's holiday rules apply).

The inputs after *JSON* complete or override it:

- *Name* and *Space Type*: unset, the preset takes the JSON's name and has no space type, so it fits every preset input of a plan generator, as an [any-program preset](workflow.md#any-program-preset) does.
- *WWR*: the JSON holds no glazing, so the window-to-wall ratio is an input, 0.4 by default.
- *Loads*: each load you connect replaces the JSON's loads of its type and end use, or is added when the JSON has none, such as ventilation.
- *Heating On*, *Cooling On*, *Heating Setpoint*, *Cooling Setpoint*, *Activity*, *People Radiant*, and *People Sensible* replace the JSON's controls.

Its outputs are the *Preset*, its *Source* (the JSON's identity and checksum, the atlas program, the calendar, every override, and what was left out), the *Assumptions* the atlas's defaults made, the *Overrides*, and what was *Left Out*: shared services, which BEMGen does not model, and the design-day rules of the schedules. The example definition `program-json-office.gh` uses the atlas's Medium Office program as the office of an *Office Plate*.

### Richer programs

The general components of panel *1 Program* and the preset components gain inputs at the end; their earlier inputs are unchanged.

- ***Load*** has the basis `PerDwellingUnit` (a value per dwelling: a generated dwelling-unit zone holds one dwelling, and a merged zone the sum of its sources), an optional *End Use* that tells loads of one type apart (a program holds one load per type, end use, and basis), the heat fractions of lighting and equipment (*Radiant*, *Latent*, *Lost*, *Visible*, *Return Air*; unset, the values the IDF used before), and the *Target Temperature* and *Inlet Temperature* of hot water (unset, 60 °C and 10 °C).
- ***Program Preset*** and every built-in preset have *Heating On* and *Cooling On* (both true by default): a conditioned space can be only heated or only cooled, and needs at least one side. *Program Preset* also has the occupants' *Activity* schedule (unset, 120 W per person), *People Radiant* (0.3), and *People Sensible* (a number, or `autocalculate`, the default).
- ***Schedule*** has the kind `Activity` (W per person) beside `Fraction` and `Temperature`.
- ***Mix Programs*** and every zone merge carry all of it. A zone merge weights per-dwelling loads by the dwellings of each source; in a mix, a weight stands for the preset's share of dwellings as well as of floor area. Heat fractions are weighted by each load's share, hot-water temperatures by each load's flow, and the occupants' activity and fractions by the occupants each program brings. The heating setpoint mixes over the heated programs only and the cooling setpoint over the cooled ones; a heating setpoint above the cooling setpoint is an error. In a mix, occupancy given in more than one basis (per floor area, per dwelling, absolute) is an error when any preset has a per-person load or the presets with occupants differ in their people settings; give all occupancy in one basis.

The defaults are the values BEMGen used before, so the built-in presets give the same results as in 1.1.0.

### The converters

- *Convert2BEM* has nine new outputs, 22 to 30: *Load End Uses* (LE), *Heat Fractions* (HF), *Dwelling Units* (DU), *Activity* (Act), *People Radiant* (PR), *People Sensible* (PS), *Water Target* (WT), *Water Inlet* (WI), and *Calendar* (Cal). The heating or cooling setpoints of a zone that is only cooled or only heated are empty. See [Convert2BEM](workflow.md#6-convert2bem).
- *Convert2IDF* writes the program's heat fractions, people properties, and hot-water temperatures, and a zone with one side gets `ThermostatSetpoint:SingleHeating` or `ThermostatSetpoint:SingleCooling`. The run period takes its year from the building's calendar; without one, as with the built-in presets, it is 2007, which starts on a Monday, as 2018, the year used before, does.

### Opening older definitions

Definitions saved with 1.1.0 open as they were, with their values and wires; the new inputs take their defaults. Definitions saved with 1.0.2 or earlier still lose the infiltration values of their presets, as described under [1.1.0](#definitions-saved-with-an-earlier-version). The example definitions in the examples zip have been rebuilt with 1.2.0.

## 1.1.0

Version 1.1.0 added a plan simplifier, a way to mix programs, and a new place for infiltration.

### Conditioned Merge

*Conditioned Merge* (Z1c), in panel *3 Simplify*, is a fifth plan simplifier. It sorts the zones of a floor into two classes and merges each class:

- **Conditioned** zones, those whose program preset has heating and cooling setpoints (a *Conditioned* preset), become one zone, `Conditioned-1`.
- **Unconditioned** zones, such as the stairs, become another, `Unconditioned-1`.

Each merged zone takes the space type its sources share, or `Mixed` when they differ. Loads, schedules, and setpoints are combined as in every zone merge ([Workflow](workflow.md#3-simplify-the-plan)).

What sets it apart is the floor area it keeps. *Perimeter Core* and *Single Zone per Floor* give every zone a conditioned program as soon as one source is conditioned, so wherever they cover a stair, the conditioned floor area grows and *Validate* reports a note. *Conditioned Merge* never mixes the two classes, so the conditioned floor area is exactly that of the plan. On the default linear plan (432 m², of which the 72 m² stair is unconditioned) it gives a conditioned zone of 360 m² and a stair zone of 72 m², and *Validate* shows no note.

#### Join Pieces

*Semantic Merge* and *Conditioned Merge* both have a Boolean input *Join Pieces* (J), false by default.

- **False:** every connected piece of a class becomes its own zone. This is what *Semantic Merge* always did.
- **True:** every piece of a class becomes part of one zone. The stairs of a floor, for example, become one stair zone, even though they do not touch.

On the default *Stair Bay Bar* (three stair bays, 612 m²), *Semantic Merge* gives seven zones: three stairs and four groups of dwellings. With *Join Pieces* true it gives two: one stair zone of three pieces (108 m²) and one dwelling zone of four pieces (504 m²). *Conditioned Merge* gives the same two zones, named `Unconditioned-1` and `Conditioned-1`, and its conditioned area is exactly the plan's 504 m².

A zone made of several pieces is one zone for everything downstream: one set of loads, one multiplier, one `Zone` object in the IDF. The viewport previews draw one solid per piece, and *Convert2BEM* gives one closed Brep per piece in the *Zones* branch of the zone.

### Mix Programs

*Mix Programs* (Mix), in panel *1 Program*, mixes several program presets into one new preset. Give it the presets (*Presets*) and one weight for each (*Weights*): the preset's share of the floor area, in any unit, because only the ratios matter. Use it for a zone that holds several programs, such as a dwelling with a shop below.

The mix is calculated the way a zone merge combines the programs of zones with those floor areas:

- loads per floor area and in air changes per hour are weighted by the area share;
- loads per person are weighted by the occupants each preset brings;
- absolute loads, such as a fixture's flow, are added as they are, without weights;
- schedules and setpoints combine as they do when zones merge; the mix is conditioned if any preset is, and its setpoints are those of the conditioned presets;
- the space type is that of the preset with the largest weight, and the window-to-wall ratio is the weighted mean, unless you give a *Space Type* or a *WWR*.

For example, mixing *Dwelling Unit Preset* and *Corridor Preset* with the weights 0.7 and 0.3 gives a preset named `Mix of Example Dwelling Unit 0.7, Example Corridor 0.3` of space type `DwellingUnit`, with occupancy 0.021 people/m², lighting 5 W/m², equipment 3.5 W/m², and a window-to-wall ratio of 0.27, conditioned. The same program results from merging two zones of 70 m² and 30 m² with *Single Zone per Floor*.

A mix cannot combine absolute occupancy in one preset with a per-person load in another, because the number of people would then depend on a zone area the mix does not know; give occupancy per floor area instead. The mixed preset goes wherever a program preset goes, and its provenance records the presets and their weights. *Name* is optional; unset, it is built from the names and the normalised weights.

### Infiltration is set on Envelope Preset

Infiltration is no longer part of a program preset. It is one setting for the whole building, on *Envelope Preset*, and every zone gets it from its own surfaces or volume. *Envelope Preset* has three new inputs:

| Input | Nickname | Default | Meaning |
| --- | --- | --- | --- |
| Infiltration Rate | Inf | 0.3 | The design rate, not negative, in the unit of the basis. |
| Infiltration Basis | InfB | `AirChangesPerHour` | What the rate is per: `PerExteriorSurfaceArea` (m³/h per m² of the zone's outdoor walls, roofs, and exposed floors, windows included), `PerExteriorWallArea` (m³/h per m² of its outdoor walls), or `AirChangesPerHour` (1/h of its volume). Right-click the input to choose one, or extract it as a dropdown. |
| Infiltration Schedule | InfS | always on | Optional fraction schedule that multiplies the rate. |

The effect of this on the converters:

- *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` object per zone, in EnergyPlus's own method for the basis. A zone made of several pieces takes the surfaces or volume of all its pieces.
- *Convert2BEM* has four new outputs, 18 to 21: *Infiltration Rate* (IR), *Infiltration Basis* (IB), *Infiltration Schedule* (IS), and *Infiltration Flows* (IF), the design flow of each zone in m³/h. See [Convert2BEM](workflow.md#6-convert2bem).
- The program preset components no longer have *Infiltration* and *Infiltration Schedule* inputs, and the example presets no longer carry rates. The mall, lobby, retail, and operating-theatre presets used to have their own rates (0.8, 0.6, 0.5, and 0.1 air changes per hour); the whole building now uses the one rate of its *Envelope Preset*.
- *Load* no longer accepts the load type `Infiltration` or the basis `PerExteriorWallArea`; it reports `'Infiltration': infiltration is not a program load: set it on the Envelope Preset.`

### Definitions saved with an earlier version

!!! warning "Infiltration values in old definitions are dropped"
    When you open a definition saved with version 1.0.2 or earlier, Grasshopper shows a message about the removed inputs of the preset components, and **any infiltration values or wires on those inputs are dropped**. The building then uses the infiltration of its *Envelope Preset*, 0.3 air changes per hour by default. If your presets used other rates, set the rate (and basis) on *Envelope Preset*, and connect it to the converters.

Definitions that use *Semantic Merge* open with *Join Pieces* false, so they give the same zones as before. The example definitions of 1.1.0 were rebuilt with the new components.
