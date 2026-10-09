# ADR-018: Program presets from program JSON 2.0.0, and the extended program model

Status: Accepted (the owner's decisions of 2026-10-07; the realisation by the controller, provisional pending the owner's reading)

Date: 2026-10-07

Decisions: D-009, D-023, D-038, D-047, D-064, D-111, D-124, D-126; applies [ADR-003](ADR-003-schedules.md), [ADR-004](ADR-004-tolerances.md), [ADR-005](ADR-005-conditioning-and-setpoints.md), [ADR-007](ADR-007-load-basis-aggregation.md), [ADR-010](ADR-010-convert2idf.md), and [ADR-017](ADR-017-program-mix-and-building-infiltration.md); supersedes in part ADR-005 (a conditioned zone needs both setpoints), ADR-007 and D-047 (one load per type and basis), and ADR-010 (the fixed heat fractions, activity, thermostat, water handling, and run-period year of the IDF); retires the unmerged S10 atlas work (D-122, ADR-016), which exists only in the tag `archive/archetype-data`

Design note: [2026-10-07-program-json.md](../plans/2026-10-07-program-json.md) · Contract mapping: [program-json.md](../architecture/program-json.md)

## Context

The Energy Archetype Atlas now publishes a self-contained program contract, *program JSON 2.0.0*: one program's loads, controls, and every schedule they use in one JSON object, in a `raw` or a `defaulted` mode, with the defaults already applied by the atlas under its policy `atlas-program-defaults-1.0.0`. The owner retired the S10 fetch components (D-122, ADR-016), which resolved and verified atlas snapshots over the network, and asked for one parser component that turns such a JSON into a ready-to-use program preset.

The contract describes more of a program than BEMGen held: heat fractions per power load, a people activity schedule and radiant and sensible fractions, several loads of one type (lighting and additional lighting), heating and cooling enabled separately, hot-water target and inlet temperatures, loads per dwelling unit, shared services, and a calendar (year and holidays) on which rule-based schedules are expanded. Ignoring any of these would replace a program assumption silently (GLOBAL.md scientific rule 3). The owner decided (2026-10-07) that BEMGen's program model grows to hold them, except shared services, which are left out.

## Options considered

### Contract features without a home in BEMGen

- **(a) Extend the program model (chosen, the owner).** Per-dwelling basis, end uses, heat fractions, people properties, one-sided thermostats, water temperatures, and a calendar become part of `ZoneProgram`, are aggregated by explicit rules, and are written by both converters.
- **(b) Keep them as provenance only.** The exporter would keep its fixed values with a warning. Every imported atlas program would then be simulated with BEMGen's assumptions instead of its own. Not chosen.

### Per-dwelling loads: the merge weight

- **Floor area (the owner's first answer).** It does not conserve installed power when the merged dwellings differ in size, which GLOBAL.md scientific rule 1 requires: 80 m² and 40 m² dwellings at 100 and 400 W/dwelling hold 500 W; the area-weighted 200 W/dwelling × 2 gives 400 W. Raised as a conflict with rule 1.
- **Dwelling count (chosen, the owner).** BEMGen can track the number of dwellings exactly, so the general rule value* = Q*/B* with the dwelling count as the basis quantity applies: 250 W/dwelling × 2 = 500 W. No exception to rule 1 is needed.

### Validation of the JSON

- **A bundled JSON Schema library (chosen, the owner).** The contract's own schema is embedded byte for byte and validated in Draft 2020-12, so BEMGen checks exactly what the atlas publishes.
- **A hand-written checker mirroring the schema.** No dependency, but two definitions of one contract that can drift. Kept as the fallback if no library loads in Rhino; not needed.

The library had to be permissive and load next to Rhino 8's .NET 8 runtime. The plugin targets `net7.0`, so NuGet resolves the `netstandard2.0` dependency groups of a library, and those decide which `System.Text.Json` it brings:

| JsonSchema.Net | Licence | Pulls `System.Text.Json` | Outcome |
| --- | --- | --- | --- |
| 9.x | OSMF EULA (acceptance required) | — | not permissive; rejected |
| 8.x | MIT | 10.0.0, through Json.More.Net 2.2.0 | cannot load beside the runtime's version 8; rejected |
| 7.3 and 7.4 | MIT | 9.0.0 | rejected |
| **7.2.3** (2024-09-20) | MIT | 8.0.0 | **chosen** |

JsonSchema.Net 7.2.3 depends on JsonPointer.Net 5.0.0, Json.More.Net 2.0.1.2, and Humanizer.Core 2.14.1, all MIT. `System.Text.Json` is pinned directly at 8.0.5, because 8.0.0 to 8.0.4 carry NuGet audit advisories. The six third-party assemblies (`JsonSchema.Net`, `JsonPointer.Net`, `Json.More`, `Humanizer`, `System.Text.Json`, `System.Text.Encodings.Web`) and `Lod.ProgramJson.dll` ship next to `BEMGen.gha`. On Rhino's .NET 8 runtime the framework's `System.Text.Json` of the same assembly version wins and the two `System.Text` files are unused; they stay because a Rhino 8 started on .NET 7 needs them. All fixtures were also validated independently with Python `jsonschema` 4.26.0 (0 errors).

## Decision

### The program model (`Lod.Core`)

- **Per dwelling unit.** `LoadBasis.PerDwellingUnit`; a load's magnitude is value × the zone's dwelling count (`ZoneMeasures.DwellingUnits`, `Zone.DwellingUnits`). A generated zone of space type `DwellingUnit` counts 1 dwelling (a dwelling is one zone, never subdivided, D-009) and every other zone 0; a target zone counts Σ fᵢ·Nᵢ of its sources, so a split gives fractional counts. Occupancy may be per dwelling. A per-dwelling load on a zone with no dwellings is the error `PerDwellingWithoutDwellings`, at generation and at validation. The building's dwelling count (zone multipliers included) is a conserved total.
- **End uses.** `LoadDefinition.EndUse`, defaulting to the type's snake-case name (`occupancy`, `lighting`, `electric_equipment`, `gas_equipment`, `hot_water`, `ventilation`), the names the contract uses. A program holds at most one load per type, end use, and basis (`LoadComponent`; superseding D-047's type and basis); end uses are compared ignoring case (`LoadEndUses.Comparer`), so `Lighting` and `lighting` are one end use, and a merged component keeps the spelling of the first source that has it; loads of one type with different end uses stay separate in every merge and in both converters.
- **Heat fractions** (`HeatFractions`) on lighting, electric equipment, and gas equipment: radiant, latent, lost, visible, and return air, each in [0, 1], their sum at most 1 within `ToleranceSettings.AbsoluteFraction` (1e-9, a new central tolerance, ADR-004), the convective share what remains. A non-zero value in a field the EnergyPlus object lacks (latent or lost on lights, visible or return air on equipment) is the error `HeatFractionNotSupported`, not dropped. Defaults are the values the IDF writer used before: lights radiant 0.42 and visible 0.18; electric equipment radiant 0.5; gas equipment radiant 0.3; the rest 0.
- **People properties** (`PeopleProperties`) on the program: an activity schedule (`ScheduleKind.Activity`, W/person, finite and not negative), a radiant fraction of the sensible heat, and a sensible fraction (`SensibleHeatFraction`) that is a number in [0, 1] or `autocalculate`. Defaults: constant 120 W/person named `BEMGen Activity Level`, 0.3, `autocalculate`.
- **Heating and cooling separately.** A `Thermostat` holds an optional heating and an optional cooling setpoint schedule, at least one (`NoSetpoint`); a zone is conditioned when it has a thermostat. Where both exist, heating must not exceed cooling at any hour by more than `ToleranceSettings.AbsoluteSchedule` (`SetpointsCross`).
- **Hot-water temperatures** (`WaterTemperatures`): a hot-water load holds a target and an inlet temperature schedule (°C), the target never below the inlet by more than `AbsoluteSchedule` (`WaterTargetBelowInlet`). Defaults: constant 60 and 10 °C, named `BEMGen Hot Water Target Temperature` and `BEMGen Hot Water Inlet Temperature`.
- **Calendar.** `ScheduleCalendar`: a non-leap year (BEMGen schedules hold 8760 values, ADR-003) and its distinct holidays. A program records the calendar its schedules were expanded on; BEMGen's own presets record none and assume a year whose 1 January is a Monday. Programs on different calendars cannot be merged, mixed, or built into one building (`CalendarMismatch`); a program without a calendar agrees only with a calendar starting on a Monday. Holidays reach the IDF only through the hourly values, which already hold the holiday profile.

### The aggregation rules

The aggregator keeps its form (ADR-007): source *i* transfers Tᵢ = fᵢ·Qᵢ of each component, Q* = ΣTᵢ, value* = Q*/B*. *Mix Programs* stays the same merge on a virtual zone of unit area (ADR-017); there each input's dwelling count is its normalised weight, as its floor area is. Because that virtual zone has unit floor area and one dwelling, occupants per m², per dwelling, and absolute would be added as if they were one quantity, and a per-person load or the people properties would be weighted by a wrong split; a mix with occupancy in more than one basis and either a per-person load in any input or different people properties among the inputs with occupants is therefore the error `MixedOccupancyBases` (found in review: 0.05 person/m² at 10 m³/h per person mixed with 3 person/dwelling at 30 m³/h per person gave 29.67 m³/h per person). Identical people properties and mixes with one occupancy basis stay allowed. New rules, each recorded in an `AggregationRecord` (the methods `OccupantWeighted` and `FlowWeighted` are new):

| Quantity | Rule | Fallback |
| --- | --- | --- |
| Per-dwelling component | value* = Σ fᵢ·Nᵢ·vᵢ / Σ fᵢ·Nᵢ; schedule weighted by Tᵢ, as every basis | zero magnitude: value 0, constant zero schedule |
| Heat fractions of a component | each weighted by Tᵢ: installed radiant, latent, lost, visible, and return-air power conserved | Q* = 0: by fᵢ·Aᵢ |
| Activity | a*(t) = Σ oᵢ(t)·aᵢ(t) / Σ oᵢ(t), with oᵢ(t) the transferred scheduled occupants: people heat conserved every hour | an hour without occupants: transferred design occupants; none at all: fᵢ·Aᵢ |
| People radiant fraction | weighted by transferred design occupants | fᵢ·Aᵢ |
| People sensible fraction | all `autocalculate` → `autocalculate`; all numbers → occupant-weighted; a mixture → `autocalculate` and the warning `MixedSensibleFraction` (the owner) | as radiant |
| Water target and inlet | weighted every hour by the transferred scheduled flow: the water heat Σ qᵢ(t)·(T_target − T_inlet) conserved every hour | an hour without flow: transferred design flow; no flow: fᵢ·Aᵢ |
| Heating setpoint | floor-area weighted over the sources with heating on; on when any source has it (ADR-005, per side) | — |
| Cooling setpoint | the same over the sources with cooling on | — |
| Crossed setpoints after a merge | an error naming the sources (EnergyPlus rejects them) | — |

The people sensible rule counts only the sources with a positive weight. A weighted mean of equal values returns that value exactly (heat fractions, people fractions, activity, water temperatures, and setpoints hour by hour, so equal heating and cooling setpoints merged over different sources stay equal and do not cross by rounding), and an activity or water-temperature schedule identical in every source keeps its name, so a merge of default presets leaves `BEMGen Activity Level` and the default water-temperature names (and the default IDF) unchanged. Load schedules and setpoints are always named after the target. When every weight is zero (no magnitude, flow, or occupants, and no floor area) the error `ZeroAggregationWeight` names the target.

### The program JSON library (`Lod.ProgramJson`)

`ProgramJsonImporter.Import(json, options)` reads in `ProgramJsonReader`: strictly (duplicate keys rejected, 64 MiB and depth 64 at most, `ProgramJsonLimits`), then the mode (`raw` rejected before the schema), then the embedded schema, then the contract's checks (schedule keys and references, units by role, real dates, annual lengths and years, heat-fraction sums, repeated demands), then the expansion of every referenced schedule on the calendar and the hourly checks (heating ≤ cooling when both sides are on, water target ≥ inlet). Rule-based schedules use the holiday day type `Hol` on holidays; the last matching specific rule wins, else the last matching `Default`; rules are never sorted; a start after the end wraps New Year; a day no rule covers is an error. Design-day rules are checked for coverage (a warning) and not used. Hot-water flows convert from m³/s to m³/h. Loads of one type, end use, and basis with different demand IDs add, by the aggregator's own rule. Shared services are left out and listed once each. The preset's `Source` records the JSON's identity and SHA-256, its source record, the default policy and the number of its substitutions, the calendar, every override, and what was left out. Every diagnostic carries the JSON Pointer of its node.

*Program JSON* (panel *1 Program*, `abb0aeb9-5a9f-40ff-b3a1-bb125cfb675c`) is a thin adaptor over the importer. It takes the JSON text only (no file, no network), a WWR (illustrative default 0.4), a year (default 2007, whose 1 January is a Monday, as BEMGen's presets assume) and holidays, and optional overrides: loads (each replaces the JSON loads of its type and end use, or is added, such as ventilation, which the contract does not carry), each thermostat side and its schedule, the activity schedule, and the two people fractions. The space type is unset by default, which gives an any-program preset.

### Export

- `Lights`, `ElectricEquipment`, and `GasEquipment` take their fractions from the load; a load whose type has more than one end use in a zone is named with its end use.
- A per-dwelling load is written as its absolute level, value × dwelling count.
- `People` take the zone's activity schedule, radiant fraction, and sensible fraction or `autocalculate`.
- `WaterUse:Equipment` takes the target as its target temperature and the inlet as its cold-water supply temperature; water still adds no zone heat.
- A thermostat is `ThermostatSetpoint:DualSetpoint`, `SingleHeating`, or `SingleCooling` by its sides.
- The run period's year and first weekday come from the building's calendar, else 2007 and Monday (before: 2018, also a Monday).

## Consequences

- **Atlas programs keep their own assumptions** in the IDF: their heat fractions, activity, setpoints per side, and water temperatures, not BEMGen's.
- **Snapshots changed**, each explained in D-126: text reports gain lines for the new fields only (removing them restores the originals exactly), and IDF snapshots gain a calendar header line and move their run-period year from 2018 to 2007.
- **Existing definitions open unchanged.** Every new input and output is appended and optional, so a 1.1.0 definition keeps its wires and values; the components set the appended parameters aside while Grasshopper reads the saved ones, because its reader would otherwise open the IO dialog. Two behaviours change: *Program Preset* with one setpoint wired makes a one-sided space instead of an error, and crossed setpoints are now an error on every preset component.
- **The plugin ships more libraries**: `Lod.ProgramJson` and the six third-party assemblies above.
- **Shared services are not modelled.** A program JSON with shared services imports without them, with a warning listing them.
- **Retired:** the S10 fetch components, their GUIDs (never to be reused, listed in D-126), and the two atlas examples, kept only in the tag `archive/archetype-data`.
- **Contract gaps** found while building are reported to the atlas, not worked around: 29 February in a non-leap model year, holidays for schedules without a `Hol` rule, the vague "relevant active periods" wording of the setpoint rule, a copy-paste constraint on annual schedules, and design-day coverage that a consumer without sizing never uses (D-126).
- **Provisional.** The owner's decisions are final; the realisation stands until the owner has read it.
