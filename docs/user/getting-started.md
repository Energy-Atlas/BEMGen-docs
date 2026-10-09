# Getting started

## What you need

- Windows with **Rhino 8.19 or later** (Rhino 7 is not supported). Rhino 8 runs plugins on .NET Core by default, which is what BEMGen is built for.
- Grasshopper, which comes with Rhino 8.
- To simulate the models later: ClimateStudio (for the output of *Convert2BEM*) or EnergyPlus 25.2 (for the files of *Convert2IDF*). BEMGen itself never runs a simulation.

## Install the plugin

Download the files of the latest version from the [Releases page](https://github.com/energy-atlas/BEMGen-docs/releases). This guide describes version 1.2.0, which has:

- `bemgen-1.2.0-rh8_19-win.yak`, the Rhino package (`rh8_19` means Rhino 8.19 or later, `win` means Windows);
- `bemgen-1.2.0-rh8-win.zip`, the same plugin as a folder;
- `bemgen-1.2.0-examples.zip`, the example definitions;
- `SHA256SUMS.txt`, the checksums of the three files.

Later versions have the same files with their own version number. If you are updating from an earlier version, read [What's new](whats-new.md) first: definitions saved with 1.1.0 open as they were, but those saved with 1.0.2 or earlier lose the infiltration values of their presets.

Close Rhino before installing: Grasshopper loads plugins only when it starts. Install BEMGen in one way only; two copies of `BEMGen.gha` register the same components twice.

### From the Yak package

Drag the `.yak` file onto a running Rhino 8 window, then restart Rhino. BEMGen is not published on the Rhino package server, so the package is installed from the file.

### From the zip

1. In Windows Explorer, open the zip's *Properties* and tick *Unblock*; Windows blocks plugins that come from the internet.
2. Unpack it, and copy the folder `BEMGen` it holds into `%APPDATA%\Grasshopper\Libraries\`, so that the plugin is at `%APPDATA%\Grasshopper\Libraries\BEMGen\BEMGen.gha`.
3. Restart Rhino.

### From source

Building BEMGen from source needs access to its repository, which is private for now. The [Grasshopper smoke test](../developer/development/grasshopper-smoke-test.md) describes how a build is loaded.

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
    The examples zip of the release holds one Grasshopper definition per typology, `end-to-end.gh`, the definition of the end-to-end example, and `program-json-office.gh`, a preset made from program JSON; see [Typologies](typologies.md#example-definitions).
