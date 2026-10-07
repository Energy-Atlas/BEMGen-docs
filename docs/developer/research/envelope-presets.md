# Envelope Presets

> **Status:** Current as of S6 (part B); infiltration added in D-124 · **Date:** 2026-10-02 · **Decisions:** D-023, D-031, D-069, D-112, D-124; [ADR-010](../decisions/ADR-010-convert2idf.md), [ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md)
>
> **Read this first:** the envelope that ships with BEMGen (`ExampleEnvelopePresets.Example`) holds **illustrative round numbers chosen for development and tests. Its layers and glazing are NOT taken from ASHRAE 90.1, the DOE prototype buildings, a national code, or any other standard**, and no result based on it may be presented as if they were. Sourced envelopes are an open research input (§4), like sourced program presets ([program presets](program-presets.md) §3).

An envelope preset describes the constructions of a building: one layered construction per envelope role, one simple glazing for every window (ADR-010, D-112), and since D-124 the building's infiltration. It is separate from the program presets on purpose: the envelope is the same at every level of detail, whatever zones are merged, so geometry effects are not confounded with envelope changes (GLOBAL.md scientific rule 4). *Convert2BEM* and *Convert2IDF* take the same preset, so both outputs describe one envelope.

## 1. What an envelope preset is

In code an envelope preset is an `EnvelopePreset` (`src/Lod.Core/Envelope/EnvelopePreset.cs`), built from its plain values `EnvelopeValues` with `ToPreset()`, which reports every invalid value at once.

| Type | Values | Rejected with diagnostic |
| --- | --- | --- |
| `Layer` | `Name`, `Thickness` (m), `Conductivity` (W/(m·K)), `Density` (kg/m³), `SpecificHeat` (J/(kg·K)) | `EmptyName`; `EnvelopeValue` when a property is not positive and finite |
| `Construction` | `Name` and 1 to 10 `Layers`, listed from the outside to the inside as the zone whose surface it is sees them | `EmptyName`; `ConstructionLayers` for no layers or more than 10 (the EnergyPlus limit) |
| `GlazingSpec` | `Name`, `UFactor` (W/(m²·K)), `SolarHeatGainCoefficient`, `VisibleTransmittance` of the whole window | `EmptyName`; `EnvelopeValue` when the U-factor is not in (0, 7] or SHGC or VT is not in (0, 1) |
| `Infiltration` | `DesignRate` (finite, not negative), `Basis` (`InfiltrationBasis`), and a fraction `Schedule`, the same for every zone (§2.5) | `InfiltrationValue` when the rate is negative or not finite or the basis is not defined; `ScheduleKindMismatch` when the schedule is not a fraction schedule |
| `EnvelopeValues` | `Name`, one construction per role (below), `Window`, and `Infiltration` | `EmptyName` for the preset name |

Names identify materials and constructions in the converters' output, so `ToPreset` also checks that they are unambiguous, ignoring case as EnergyPlus does (`DuplicateEnvelopeName`): one material name per set of layer properties, one construction name per layer sequence, and the glazing name, which names both the window construction and its glazing material, used by no other material or construction. Names are written as they are, so they must also be valid IDF names (`EnvelopeName`): at most 100 characters, the generated `"{Name} Reversed"` included, and none of `,` `;` `!`. The same `Construction` may serve several roles, and a layer used by several constructions is checked once.

### 1.1 Roles

| `ConstructionRole` | Surfaces | Layers listed from |
| --- | --- | --- |
| `ExteriorWall` | walls facing outdoors | outdoors to the zone |
| `Roof` | ceilings facing outdoors: roofs and terraces (ADR-015) | outdoors to the zone |
| `GroundFloor` | floors on the ground | the ground to the zone |
| `ExposedFloor` | floors facing outdoors: overhangs and storeys the storey below does not carry (D-074) | outdoors to the zone |
| `InteriorWall` | walls between zones, written interzone or adiabatic (D-069): the wall whose zone ID sorts first uses the construction, its partner the reverse | the adjacent zone to the owning zone, as the wall whose zone ID sorts first sees them |
| `InteriorFloor` | slabs between storeys: the floor above uses the construction, the ceiling below its reverse | the zone below to the zone above |
| `InternalMass` | slabs inside one zone that became internal mass (D-031) | — (both faces exposed) |

`ConstructionRoles.Of(surface, exportedBoundary)` (`src/Lod.Core/Conversion/ConstructionRoles.cs`) gives a surface its role from its kind and the boundary a converter writes for it (`HeatTransferOptions.Exported`), as a `Result<ConstructionAssignment>` holding the role and `Reversed`; an unresolved boundary or a wall or ceiling on the ground, which no floor aggregator produces but which an overridden validation can let through, is the error `NoConstructionRole`. The heat-transfer options only turn interzone surfaces adiabatic, so they never change a role. A ceiling between storeys has `Reversed = true`, and so has a wall between zones whose zone ID sorts after the adjacent zone's (ordinal comparison, read from the building's adjacency, so the same wall is reversed whatever the options); this is the one rule both converters use to pick the reversed side: `EnvelopePreset.For(assignment)` then returns `Construction.Reversed()`, the same layers in reverse order named `"{Name} Reversed"` (a symmetric construction is its own reverse). The two sides of a surface between zones thereby list the same layers in opposite order, as EnergyPlus expects of paired interzone surfaces. `EnvelopePreset.Constructions` lists every construction a converter may write, each once (the roles' constructions in role order, then the reverses of the interior wall and floor where they differ), and `EnvelopePreset.Materials` every layer, each material once.

## 2. The example envelope

`ExampleEnvelopePresets.Values` and `ExampleEnvelopePresets.Example` (`src/Lod.Core/Envelope/ExampleEnvelopePresets.cs`), named *Example Envelope*. Every name starts with `Example`, so no output can be mistaken for a sourced envelope.

### 2.1 Materials

Round numbers of the order found in general material property tables; not taken from any particular table or standard.

| Material | Thickness (m) | Conductivity (W/(m·K)) | Density (kg/m³) | Specific heat (J/(kg·K)) | Resistance (m²·K/W) |
| --- | --- | --- | --- | --- | --- |
| Example Brick | 0.1 | 0.8 | 1800 | 840 | 0.125 |
| Example Wall Insulation | 0.12 | 0.04 | 30 | 1400 | 3.0 |
| Example Roof Insulation | 0.16 | 0.04 | 30 | 1400 | 4.0 |
| Example Floor Insulation | 0.08 | 0.04 | 30 | 1400 | 2.0 |
| Example Partition Insulation | 0.1 | 0.05 | 20 | 1000 | 2.0 |
| Example Concrete | 0.2 | 2.0 | 2300 | 900 | 0.1 |
| Example Screed | 0.05 | 1.25 | 2000 | 840 | 0.04 |
| Example Gypsum Board | 0.0125 | 0.25 | 900 | 1000 | 0.05 |

### 2.2 Constructions

Layers from the outside to the inside; the resistance is that of the layers alone, without surface films (`Construction.ThermalResistance`).

| Role | Construction | Layers | Resistance (m²·K/W) |
| --- | --- | --- | --- |
| Exterior wall | Example Exterior Wall | Brick, Wall Insulation, Concrete, Gypsum Board | 3.275 |
| Roof | Example Roof | Roof Insulation, Concrete, Gypsum Board | 4.15 |
| Ground floor | Example Ground Floor | Floor Insulation, Concrete, Screed | 2.14 |
| Exposed floor | Example Exposed Floor | Wall Insulation, Concrete, Screed | 3.14 |
| Interior wall | Example Interior Wall | Gypsum Board, Partition Insulation, Gypsum Board (symmetric) | 2.1 |
| Interior floor | Example Interior Floor | Gypsum Board (ceiling below), Concrete, Screed (floor above); its reverse is *Example Interior Floor Reversed* | 0.19 |
| Internal mass | Example Interior Floor | the interior floor slab, which internal mass keeps (D-031) | 0.19 |

### 2.3 Window

*Example Double Glazing*: U-factor 1.8 W/(m²·K), SHGC 0.4, visible transmittance 0.7, for the whole window (frame and glass together, as a simple glazing system). The glazed area itself comes from the program presets' WWR and the generators' window rule (D-026, D-079); the envelope only gives its properties.

### 2.4 Why these values

- The example only has to be physically plausible and valid, so that converters, tests, and example definitions have an envelope to write; its numbers carry no research meaning.
- The interior wall is symmetric and the interior floor is not, so both cases of interzone pairing (a construction that is its own reverse and one that is not) are exercised.
- Internal mass uses the interior floor construction, because a slab that becomes internal mass keeps its construction (D-031).

### 2.5 Infiltration (D-124)

Infiltration is the building's, not a space type's: its magnitude follows each zone's exterior surfaces or volume, which a program preset does not know, so it left the program presets and is a field of the envelope preset ([ADR-017](../decisions/ADR-017-program-mix-and-building-infiltration.md); [program presets](program-presets.md) §1.1). One design rate with a basis and a fraction schedule applies to every zone, at every level of detail, so zoning does not change the infiltration the model assumes (GLOBAL.md scientific rule 4).

| `InfiltrationBasis` | The rate is per | EnergyPlus method of *Convert2IDF* |
| --- | --- | --- |
| `PerExteriorSurfaceArea` | m² of the zone's exterior surface: the gross area, windows included, of its outdoor walls, roofs, and exposed floors, not its ground floor (m³/h per m²) | `Flow/ExteriorArea` |
| `PerExteriorWallArea` | m² of the zone's gross outdoor wall area (m³/h per m²) | `Flow/ExteriorWallArea` |
| `AirChangesPerHour` | the zone's volume per hour (1/h) | `AirChanges/Hour` |

`ExampleEnvelopePresets` has **0.3 air changes per hour, always on** (the schedule `Example Always On`, constant 1). Like the rest of the example envelope it is illustrative: 0.3 was the value most of the example program presets carried before infiltration moved here, and it is NOT taken from ASHRAE 90.1, the DOE prototypes, or any other standard. The per-type rates those presets had (mall 0.8, lobby 0.6, retail 0.5, operating theatre 0.1) are dropped, not moved ([program presets](program-presets.md) §2.2). A sourced envelope would state its infiltration with the source, for example a rate per exterior surface area as the prototype models give it (§4).

## 3. Using an envelope preset

- **In C#:** `ExampleEnvelopePresets.Example`, or `(ExampleEnvelopePresets.Values with { Window = new GlazingSpec("My Glazing", 1.4, 0.35, 0.6) }).ToPreset()`, or a new `EnvelopeValues` with your own constructions.
- **In Grasshopper:** *Envelope Preset* (panel *1 Program Presets*) outputs the example envelope; its inputs *Name*, *Glazing*, *U-Factor*, *SHGC*, *VT*, *Infiltration Rate* (default 0.3), *Infiltration Basis* (an enum input; default `AirChangesPerHour`, right-click lists `PerExteriorSurfaceArea`, `PerExteriorWallArea`, and `AirChangesPerHour`), and the optional *Infiltration Schedule* (unset: always on) default to the example values and replace the name, the glazing, and the infiltration. The layered constructions are the example's. *Convert2BEM* takes the preset on its *Envelope* input (the example when unconnected) and outputs each surface's and window's construction and the infiltration with each zone's design flow ([convert2bem.md](../architecture/convert2bem.md)); *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` per zone ([convert2idf.md](../architecture/convert2idf.md#infiltration)).

## 4. Sourced envelopes: an open research input

Sourcing envelope constructions, for example from a code or a prototype building for a chosen climate, is an **open research input**, decided together with climates and weather when simulations are run (D-112). When sourced envelopes are added, they must cite every value (document, version, table), state every conversion (for example from a U-value requirement to layers), be added alongside `ExampleEnvelopePresets` without changing it, and be recorded in the decision log and in this document.
