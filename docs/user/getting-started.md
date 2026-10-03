# Getting started

## What you need

- Windows with **Rhino 8.19 or later** (Rhino 7 is not supported). Rhino 8 runs plugins on .NET Core by default, which is what BEMGen is built for.
- Grasshopper, which comes with Rhino 8.
- To simulate the models later: ClimateStudio (for the output of *Convert2BEM*) or EnergyPlus 25.2 (for the files of *Convert2IDF*). BEMGen itself never runs a simulation.

## Install the plugin

Close Rhino before installing: Grasshopper loads plugins only when it starts. Install BEMGen in one way only; two copies of `BEMGen.gha` register the same components twice.

### From the Yak package

BEMGen is packaged as a Rhino package (a `.yak` file). It is not published on the Rhino package server yet, so the package is built locally from a clone of the repository, with the .NET SDK 8 or later and Rhino 8 installed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/package-yak.ps1
```

The script builds the plugin in Release and writes `dist/yak/bemgen-<version>-rh8_19-win.yak`, where `<version>` is the version in `Directory.Build.props`, `rh8_19` means Rhino 8.19 or later, and `win` means Windows. To install it, drag the `.yak` file onto a running Rhino 8 window, then restart Rhino.

### From a build folder

If you build BEMGen from source (`dotnet build BEMGen.sln -c Release`), the plugin is in `src/Lod.Grasshopper/bin/Release/net7.0/`. Either add that folder in Rhino with the command `GrasshopperDeveloperSettings` (library folders), or copy its contents into `%APPDATA%\Grasshopper\Libraries\BEMGen\`, then restart Rhino. The [Grasshopper smoke test](../developer/development/grasshopper-smoke-test.md) describes these options in detail.

## Check that it loaded

1. Start Rhino 8 and run `Grasshopper`.
2. A **BEMGen** tab appears on the Grasshopper toolbar with the panels *0 Info*, *1 Program*, *1 Program Presets*, *2 Generate*, *3 Simplify*, *4 Aggregate*, *5 Convert*, and *6 Inspect*.
3. Place *BEMGen Info* (Info) from *0 Info*. Its *Version* output shows the version of the loaded plugin and, after the `+`, the commit it was built from, in the form `<version>+<commit>`. Record it with any results you keep.

## A first definition

This definition generates a plan and shows it in the viewport; it takes a minute.

1. From *1 Program Presets*, place *Dwelling Unit Preset* (Unit), *Corridor Preset* (Corr), and *Stair Preset* (Stair). Every input of these components has a default, so they work with nothing connected; each shows the remark that its values are illustrative.
2. From *2 Generate*, place *Linear Plan Generator* (Linear).
3. Wire the *Preset* output of *Dwelling Unit Preset* to the generator's *Dwelling Unit* input, *Corridor Preset* to *Corridor*, and *Stair Preset* to *Stair*.

The viewport shows a 24 m × 18 m plan, 3 m high: a stair at the west end, a corridor along the middle, and two dwelling units on each side, coloured by space type, with blue windows. The generator's *Plan* output reads `Plan (6 zones, LinearPlanGenerator)`.

From here, the [workflow guide](workflow.md) explains every further step, and the [end-to-end example](example-end-to-end.md) continues this definition up to an IDF file.

!!! tip "Example definitions"
    The repository's `examples/` folder holds one Grasshopper definition per typology and `end-to-end.gh`, the definition of the end-to-end example; see [Typologies](typologies.md#example-definitions).
