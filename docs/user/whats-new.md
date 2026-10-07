# What's new in 1.1.0

Version 1.1.0 adds a plan simplifier, a way to mix programs, and a new place for infiltration. This page says what changed and what to do about definitions saved with an earlier version. The other pages of this guide describe version 1.1.0.

## Conditioned Merge

*Conditioned Merge* (Z1c), in panel *3 Simplify*, is a fifth plan simplifier. It sorts the zones of a floor into two classes and merges each class:

- **Conditioned** zones, those whose program preset has heating and cooling setpoints (a *Conditioned* preset), become one zone, `Conditioned-1`.
- **Unconditioned** zones, such as the stairs, become another, `Unconditioned-1`.

Each merged zone takes the space type its sources share, or `Mixed` when they differ. Loads, schedules, and setpoints are combined as in every zone merge ([Workflow](workflow.md#3-simplify-the-plan)).

What sets it apart is the floor area it keeps. *Perimeter Core* and *Single Zone per Floor* give every zone a conditioned program as soon as one source is conditioned, so wherever they cover a stair, the conditioned floor area grows and *Validate* reports a note. *Conditioned Merge* never mixes the two classes, so the conditioned floor area is exactly that of the plan. On the default linear plan (432 m², of which the 72 m² stair is unconditioned) it gives a conditioned zone of 360 m² and a stair zone of 72 m², and *Validate* shows no note.

### Join Pieces

*Semantic Merge* and *Conditioned Merge* both have a Boolean input *Join Pieces* (J), false by default.

- **False:** every connected piece of a class becomes its own zone. This is what *Semantic Merge* always did.
- **True:** every piece of a class becomes part of one zone. The stairs of a floor, for example, become one stair zone, even though they do not touch.

On the default *Stair Bay Bar* (three stair bays, 612 m²), *Semantic Merge* gives seven zones: three stairs and four groups of dwellings. With *Join Pieces* true it gives two: one stair zone of three pieces (108 m²) and one dwelling zone of four pieces (504 m²). *Conditioned Merge* gives the same two zones, named `Unconditioned-1` and `Conditioned-1`, and its conditioned area is exactly the plan's 504 m².

A zone made of several pieces is one zone for everything downstream: one set of loads, one multiplier, one `Zone` object in the IDF. The viewport previews draw one solid per piece, and *Convert2BEM* gives one closed Brep per piece in the *Zones* branch of the zone.

## Mix Programs

*Mix Programs* (Mix), in panel *1 Program*, mixes several program presets into one new preset. Give it the presets (*Presets*) and one weight for each (*Weights*): the preset's share of the floor area, in any unit, because only the ratios matter. Use it for a zone that holds several programs, such as a dwelling with a shop below.

The mix is calculated the way a zone merge combines the programs of zones with those floor areas:

- loads per floor area and in air changes per hour are weighted by the area share;
- loads per person are weighted by the occupants each preset brings;
- absolute loads, such as a fixture's flow, are added as they are, without weights;
- schedules and setpoints combine as they do when zones merge; the mix is conditioned if any preset is, and its setpoints are those of the conditioned presets;
- the space type is that of the preset with the largest weight, and the window-to-wall ratio is the weighted mean, unless you give a *Space Type* or a *WWR*.

For example, mixing *Dwelling Unit Preset* and *Corridor Preset* with the weights 0.7 and 0.3 gives a preset named `Mix of Example Dwelling Unit 0.7, Example Corridor 0.3` of space type `DwellingUnit`, with occupancy 0.021 people/m², lighting 5 W/m², equipment 3.5 W/m², and a window-to-wall ratio of 0.27, conditioned. The same program results from merging two zones of 70 m² and 30 m² with *Single Zone per Floor*.

A mix cannot combine absolute occupancy in one preset with a per-person load in another, because the number of people would then depend on a zone area the mix does not know; give occupancy per floor area instead. The mixed preset goes wherever a program preset goes, and its provenance records the presets and their weights. *Name* is optional; unset, it is built from the names and the normalised weights.

## Infiltration is set on Envelope Preset

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

## Definitions saved with an earlier version

!!! warning "Infiltration values in old definitions are dropped"
    When you open a definition saved with version 1.0.2 or earlier, Grasshopper shows a message about the removed inputs of the preset components, and **any infiltration values or wires on those inputs are dropped**. The building then uses the infiltration of its *Envelope Preset*, 0.3 air changes per hour by default. If your presets used other rates, set the rate (and basis) on *Envelope Preset*, and connect it to the converters.

Definitions that use *Semantic Merge* open with *Join Pieces* false, so they give the same zones as before. The example definitions in the examples zip have been rebuilt with the new components.
