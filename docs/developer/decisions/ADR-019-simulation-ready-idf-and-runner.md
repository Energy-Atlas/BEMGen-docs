# ADR-019: A simulation-ready IDF and an EnergyPlus runner

Status: Accepted (the owner's decisions of 2026-10-11; the realisation by the controller, provisional pending the owner's reading)

Date: 2026-10-11

Decisions: D-016, D-023, D-038, D-064, D-069, D-075, D-111, D-112, D-124, D-126, D-130. Applies [ADR-005](ADR-005-conditioning-and-setpoints.md), [ADR-010](ADR-010-convert2idf.md), [ADR-013](ADR-013-vertical-aggregation-methods.md), and [ADR-018](ADR-018-program-json-and-extended-programs.md). Supersedes in part:

- D-112: the EnergyPlus version 25.x, and "EnergyPlus is not run";
- ADR-010: the scope "no simulation scope yet", the fixed 18 °C ground, the monthly meters, and "`FullExterior` does not need convex surfaces";
- ADR-009: the empty gaps of a multiplied storey as part of the geometry effect;
- D-016, refined: simulation stays outside the pipeline, but the repository can run EnergyPlus.

Design note: [2026-10-11-idf-out.md](../plans/2026-10-11-idf-out.md) · Outputs: [experiment-outputs.md](../research/experiment-outputs.md) · Runner: [energyplus-runner.md](../architecture/energyplus-runner.md)

## Context

*Convert2IDF* wrote a file with the minimum simulation objects and EnergyPlus was never run (D-112). The study now needs simulations: the same settings in every case, the outputs from which every comparison metric is computed, and a way to run EnergyPlus from the repository. EnergyPlus 26.2.0 is installed on the development machine.

A first run before the build found:

- All 1073 IDFs the tests write completed in 26.2.
- Their warnings were a version mismatch, a gas meter with nothing on it, zone floor areas differing from space floor areas (by design for zones spanning storeys), and zero-area infiltration.
- There was one severe error: a non-convex exposed floor that casts shadows.
- The floor aggregators against the reference conserve area, volume, and hourly internal loads exactly through EnergyPlus.
- Under *Stacked Floor Zone Multiplier* the unmodelled storeys cast no shadow. The enclosed court's windows received 6.9 % more sun, which gave +4.7 % cooling and −2.9 % heating. Shading surfaces at the missing walls brought the sun back to +0.1 %.

## Decision

### The owner's decisions (2026-10-11)

1. **EnergyPlus 26.2** is the target.
2. **Weather comes from an `.epw` path input.** The IDF holds `Site:Location` from the file's header and records the file's name and SHA-256. EnergyPlus takes the weather file itself at run time.
3. **The outputs are the research set** that [experiment-outputs.md](../research/experiment-outputs.md) defines: hourly meters behind heating, cooling, and the total load, hourly zone mean air temperature, the summary tables, SQLite, and a case record in the header.
4. **The reference case** is *No Simplification* + *Stack* with both heat-transfer options on.
   - EUI is reported per conditioned and per total floor area.
   - The total load is the sum of the four facility meters, gas equipment included.
   - Peak duration is counted in hours above the reference's percentiles.
   - Both load-duration-curve measures are computed.
   - The building temperature is reported over all zones and over conditioned zones.
   - The metrics are computed in the repository.
5. **The ground is "indoor minus 2 °C".** The F-factor method was preferred if BEMGen held what it needs, but an F-factor depends on the slab-edge insulation, not on the envelope's layers, and no sourced value exists (D-023). The monthly ground temperature is the building's hourly setpoint, weighted by floor area times multiplier over its conditioned zones and averaged over the month, minus 2 °C; 18 °C without a conditioned zone. ISO 13370 was judged more than needed.
6. **Every non-convex outdoor surface is split** into convex pieces: roofs, exposed floors, walls, and shading surfaces.
7. **The storeys a multiplied storey stands for cast shadows.** The shading is generated at converter level, by *Convert2IDF* and *Convert2BEM*, from one shared rule.
8. **EnergyPlus runs only outside the pipeline**: in a C# library for the tests and a check tool now, and later in a Grasshopper component (deferred). GLOBAL.md gains architecture rule 7.
9. Finding F1 stays a finding: *Stacked Floor Zone Multiplier* keeps every slab between storeys adiabatic, even between two × 1 storeys.

### Realisation (controller, provisional)

- **Shared shading rule.** `UnmodelledStoreyShading` in `Lod.Core.Conversion` assembles the stack from the building's floor entries and returns the outdoor walls of every storey that no zone covers in height, as opaque shading surfaces at their true elevations. It names no aggregator and reads no provenance, so only *Stacked Floor Zone Multiplier* yields any. The building does not carry shading, and no pipeline type changes.
- **The ground rule's mapping is fixed; its result follows the zoning** (the owner, 2026-10-11). With uniform setpoints, as the example presets have, every level of detail gives the same monthly values. With uneven setpoints they differ, because each zone is weighted by its whole floor area and its own merged setpoints:
  - *Perimeter Core* moves January's value by 0.009 K in a test case;
  - a merge of a heating-only zone with dual-setpoint zones moves it by 0.45 K.

  That difference is part of what the study characterises about each zoning method and its resulting setpoints, so the rule is kept as it is.
- **Minimum warm-up days stay 6** (the owner, 2026-10-11). The 26.2 IDD default is 1; the writer's description now says so.
- **The convex split** cuts from each reflex vertex along an edge's extension, the shortest cut first, and keeps every window on one piece or fails with `WindowBlocksConvexSplit`.
- **`Lod.Simulation`** (`netstandard2.0`, depending on `Lod.Core` only) locates an installation, runs `energyplus.exe` through an injected process runner, and parses the outputs:
  - `eplusout.err`, `.eso`, `.mtr`, and `.eio`, and the *Building Area* table of `eplustbl.csv`, with the BCL only;
  - from these, a `SimulationResult` of the raw outputs;
  - over it, `ExperimentMetrics`, the definitions of the experiment outputs.

  `scripts/eplus-check` is a C# console tool over it. Tests that run EnergyPlus are opt-in through `BEMGEN_ENERGYPLUS`.
- **Clean error file.** A meter is written only when its source exists. A zone whose infiltration basis has no area gets no zero infiltration object. The zone-floor-area warning of zones spanning storeys is expected, and listed with its reason by the check tool.

## Options considered

- **The ground model.**
  - ISO 13370 at building level: invariant and climate-aware, but judged more than needed.
  - The F-factor method of ASHRAE 90.1 Appendix G and the DOE prototypes: conserved in total, but it needs a sourced F-factor; kept for when one exists.
  - The slab preprocessor: an external program run per footprint and weather file.
  - The fixed 18 °C: ignores both the climate and the building.
  - The `.epw` undisturbed temperatures used directly: the EnergyPlus documentation warns against them for building surfaces.
- **Shading made by the aggregator and carried on the building:** rejected by the owner in favour of converter-level generation, which leaves the pipeline types unchanged.
- **Splitting only exposed floors:** it removes the severe error but leaves non-convex roofs as receivers; the owner chose to split every non-convex outdoor surface.
- **Reading results through SQLite:** it would need a native library in the later Grasshopper component; the text outputs need none.

## Consequences

- Every IDF changes: version, header, outputs, ground temperatures, convex pieces, and shading under the multiplier. The snapshots change accordingly, and the build log explains every changed line kind.
- *Convert2IDF* gains a *Weather* input, and *Convert2BEM* a *Shading* output; no GUID changes.
- The research brief's Z5 and V4 say that unmodelled storeys cast shadows. The experiment outputs define what every simulated case yields.
- ADR-010's two items "to verify on the first EnergyPlus run" are settled: EnergyPlus uses the stated zone floor area, and the window construction named like its glazing runs.
- Set aside for now (the owner, 2026-10-11): the F-factor method once a sourced F-factor exists, F1, and the Grasshopper run component.
