# Grasshopper smoke test

A manual check that the BEMGen plugin loads in Rhino and its components work. Grasshopper code cannot be unit tested without Rhino (roadmap §6), so **a person** performs this check at the end of every stage that changes `Lod.Grasshopper`; an agent cannot. Each such stage appends its checklist under [Stage checklists](#stage-checklists).

## Requirements

- Windows with Rhino 8.19 or later (ADR-001). Check the version with Rhino's `About` command (Help > About Rhinoceros).
- A Release build from a git checkout whose changes are committed, so that the version shown identifies the code under test. From the repository root:

```bash
dotnet build BEMGen.sln -c Release
git rev-parse HEAD
```

Note the SHA that `git rev-parse HEAD` prints.

The build produces one plugin, for Rhino's .NET Core runtime:

| Rhino runtime | Build folder |
| --- | --- |
| .NET Core (Rhino 8 default) | `src/Lod.Grasshopper/bin/Release/net7.0/` |

The folder contains `BEMGen.gha` and `Lod.Core.dll` (with `.pdb` files, `Lod.Core.xml`, `BEMGen.deps.json`, and `BEMGen.runtimeconfig.json`). It never contains `RhinoCommon.dll` or `Grasshopper.dll`; Rhino supplies them.

## Load the plugin

Close Rhino before building or copying files: Grasshopper loads plugins only when it starts.

Use one of the methods below with one build folder only. Two copies of `BEMGen.gha` would register the same component GUIDs twice.

### Option A: add the build folder as a library folder (recommended during development)

1. Start Rhino and run the command `GrasshopperDeveloperSettings`.
2. Add the absolute path of the build folder (`<repository>\src\Lod.Grasshopper\bin\Release\net7.0`) to the library folders and confirm.
3. Restart Rhino. Later builds into the same folder are picked up at the next start.

### Option B: copy the build to the Grasshopper libraries folder

1. Create the folder `%APPDATA%\Grasshopper\Libraries\BEMGen\`.
2. Copy the contents of the build folder into it.
3. If the files were downloaded (for example as a zip) rather than built on this machine, unblock them: right-click each file, choose Properties, and tick Unblock; or run in PowerShell:

   ```powershell
   Get-ChildItem "$env:APPDATA\Grasshopper\Libraries\BEMGen" -Recurse | Unblock-File
   ```

   Windows marks downloaded files as blocked, and blocked plugin files may fail to load.
4. Restart Rhino.

### Option C: start Rhino from the IDE with a launch profile

`src/Lod.Grasshopper/Properties/launchSettings.json` defines one launch profile for Visual Studio and Rider, **Rhino 8 (.NET Core)** (D-052, D-053). It starts Rhino from its default install location (`C:\Program Files\Rhino 8\System\Rhino.exe`) in the .NET Core runtime, runs the `Grasshopper` command, and sets `RHINO_PACKAGE_DIRS` to the build folder (`bin\<configuration>\net7.0\`), so Rhino loads the plugin from there without a library-folder setting.

1. If Option A or B was used before, remove the build folder from the library folders and delete `%APPDATA%\Grasshopper\Libraries\BEMGen\`.
2. Select `Lod.Grasshopper` as the startup project, choose the Release configuration (the build that [Requirements](#requirements) describes), and choose the **Rhino 8 (.NET Core)** profile.
3. Start it. The IDE builds first, then starts Rhino with Grasshopper.

If Rhino is installed elsewhere, change `executablePath` locally and do not commit the change.

### Rhino runtime

BEMGen loads only in Rhino's .NET Core runtime, the Rhino 8 default (D-053); there is no build for the .NET Framework runtime. If Rhino was switched to .NET Framework with the `SetDotNetRuntime` command, switch it back to .NET Core the same way and restart Rhino before loading BEMGen. The Option C profile always starts Rhino in .NET Core.

## Run the check

1. Start Rhino and run the `Grasshopper` command.
2. Work through the checklist of the stage under test, ticking each item.
3. Record the result as described below.

### Scripted part

The checklist items that need no viewport or toolbar (registration, inputs, runtime messages, outputs, data trees, validation, and preview boxes) run headless from `scripts/rhino-smoke/` (`scripts/rhino-smoke/README.md`): it builds the plugin, starts Rhino 8 without a window, places and wires the components by GUID, and writes what it observes to a result file outside the repository (D-056, D-111). The viewport look, the toolbar, and the example `.gh` definitions remain for a person (D-058).

## Recording the result

Rebase merges (D-004) create no merge commit, so the result goes into the body of the stage close-out commit: who tested and when, the Rhino version and runtime, the SHA that was built, the version text shown by *BEMGen Info*, and pass or fail for each checklist item. A failed item blocks the stage close-out until it is fixed.

## Stage checklists

### S0 — Plugin shell

Build: the commit being closed out. Runtime: .NET Core (the Rhino 8 default).

Component under test:

| Component | Tab / panel | Inputs | Outputs | GUID |
| --- | --- | --- | --- | --- |
| BEMGen Info (nickname `Info`) | BEMGen / 0 Info | none | Version (`V`, text): the informational version; the part after `+` is the commit SHA | `b1d4f0a2-6c3e-4f7a-8e21-5a9c0d7e3b14` |

- [ ] Rhino reports version 8.19 or later.
- [ ] Grasshopper starts without an error message about BEMGen or `BEMGen.gha`.
- [ ] The component toolbar has a **BEMGen** tab with a panel **0 Info**.
- [ ] **BEMGen Info** can be placed from that panel. It has no inputs and one output, **Version** (`V`), and shows Grasshopper's generic icon (S0 to S4; since S4.1 it shows its own icon, D-063).
- [ ] The placed component shows no warning or error (it is neither orange nor red).
- [ ] A Panel connected to **Version** shows text that starts with `0.0.1`.
- [ ] The text after `+` equals the SHA printed by `git rev-parse HEAD` for the build.

### S2 checklist — pipeline skeleton (`v0.2.0`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings) and load it as described above. Runtime: .NET Core (Rhino 8's default). From S2 on, `BEMGen.gha` also needs `Lod.Generators.dll` and `Clipper2Lib.dll` next to it; the build puts them in `src/Lod.Grasshopper/bin/Release/net7.0/` together with `Lod.Core.dll`. Record the result as described in [Recording the result](#recording-the-result).

#### Toolbar

- [ ] The *BEMGen* tab shows the panels *0 Info*, *1 Program*, *2 Generate*, *3 Simplify*, *4 Aggregate*, *5 Convert*, and *6 Inspect*.
- [ ] *0 Info*: BEMGen Info. *1 Program*: Schedule, Load, Program Preset, Example Residential Presets. *2 Generate*: Linear Plan Generator. *3 Simplify*: No Simplification. *4 Aggregate*: Stack Floors. *5 Convert*: Convert2BEM. *6 Inspect*: Inspect.
- [ ] The BEMGen parameters (Schedule, Load, Program Preset, Plan, Floor, Building) do not appear on the toolbar; they exist only as component inputs and outputs.

#### Pipeline

1. Place *Example Residential Presets*.
   - [ ] It shows the remark "Illustrative values only; not sourced from DOE prototypes." and outputs three presets: Example Dwelling Unit (DwellingUnit, WWR 0.3), Example Corridor (Corridor, WWR 0.2), Example Stair (Stair, WWR 0.1). In these example presets the dwelling units and the corridor are conditioned and the stair is not.
2. Place *Linear Plan Generator*, keep every number input at its default (Length 24, Unit Depth 8, Corridor Width 2, Unit Width 10, Stair Length 4, Floor Height 3, Orientation 0), and connect *Presets*.
   - [ ] No warning or error.
   - [ ] The viewport previews a 24 m × 18 m plan with six zones: a stair at the west end, a corridor, and two units on each side of the corridor, coloured by space type (dwelling units sand, corridor grey, stair red).
   - [ ] Every exterior wall shows exactly one blue window, centered on the wall; interior walls have none.
3. Connect *No Simplification* to the plan.
   - [ ] The *Floor* output previews the same six zones and windows.
4. Connect *Stack Floors*: the floor into *Floors*, and a panel containing `3` into *Multipliers*.
   - [ ] The building preview shows three storeys, 9 m high, with windows on every storey.
5. Connect *Inspect* to the building, with panels on *Report* and *Provenance*.
   - [ ] The first line of *Report* is `building orientation=0.000000 sources=3`, followed by the zones `L0/ST` to `L2/UN2` (18 zones).
   - [ ] Each stair zone (`L0/ST`, `L1/ST`, `L2/ST`) is followed by its loads and the line `unconditioned`; every other zone has a `setpoints heatingMean=21.000000 coolingMean=24.000000` line.
   - [ ] Every outdoor wall line ends with one `window(offset=… sill=… W×H)` entry, e.g. `L0/ST/W1 … glazing=1.200000 window(offset=1.367544 sill=1.025658 1.264911x0.948683)`; interzone wall lines have none.
   - [ ] *Provenance* has three lines: `Stack Multipliers=3`, then (indented) `NoSimplification`, then (indented twice) `LinearPlanGenerator` with its parameters and `Presets=DwellingUnit:Example Dwelling Unit;Corridor:Example Corridor;Stair:Example Stair`; every line ends with the code version in brackets.
6. Connect *Convert2BEM* to the building and inspect its outputs (panels or Param Viewers).
   - [ ] All 15 outputs carry data. *Names* has 18 branches, `{0}` `L0/ST` to `{17}` `L2/UN2`.
   - [ ] *Conditioned* is `False` for the three stair branches (`{0}`, `{6}`, `{12}`) and `True` for all others.
   - [ ] *Zones* holds one closed Brep per branch.
   - [ ] *Boundaries* `{0}` reads `Outdoors`, `Interzone:L0/US1`, `Interzone:L0/CO`, `Interzone:L0/UN1`, `Outdoors`, `Outdoors`, `Ground`, `Interzone:L1/ST`, and *Surfaces* `{0}` has 8 Breps.
   - [ ] *Windows* `{0}` holds 3 Breps (the stair's south, north, and west windows).
   - [ ] *Load Schedules* has branches `{i;k}` of 8760 values; *Heating Setpoints* and *Cooling Setpoints* have 8760 values in every branch except the empty stair branches `{0}`, `{6}`, and `{12}`.
   - [ ] *Internal Mass* is 0 in every branch.

#### Changes and errors

- [ ] Change *Unit Width* from 10 to 6: the plan has three units per row (`US1`–`US3`, `UN1`–`UN3`), eight zones per storey, and the building 24 zones.
- [ ] Place a *Program Preset* with a name, *Space Type* `Corridor`, *WWR* 0.2, *Conditioned* left at `true`, and no *Heating*/*Cooling* input: it turns red with `A conditioned space needs both Heating and Cooling setpoints.` Set *Conditioned* to `false`: the error disappears and it outputs an unconditioned preset.
- [ ] Right-click *Program Preset*'s *Space Type* input: the space types are listed after *Manage Text collection*, the current one (`Corridor`) ticked. Choose `Office`: the input shows `Office` and the preset is recomputed. Right-click it again and choose *Extract parameter*: a dropdown labelled *Space Type* appears left of the input, wired into it and set to `Office`. Open the dropdown, choose `Corridor`, then press Ctrl+Z until the dropdown is gone: the input shows `Office` again. Repeat for *Schedule* *Kind* and *First Day* and *Load* *Type* and *Basis* (D-120).
- [ ] Set *Length* to 3: *Linear Plan Generator* turns red with `Error InvalidParameter: Length (3) must exceed StairLength (4).` and produces no plan; the downstream components produce no output. Set *Length* back to 24.
- [ ] Change the Rhino document units to millimetres (without scaling objects) and recompute the definition (*Solution → Recompute*): the *Convert2BEM* geometry, windows included, is 1000 times larger (bounding box 24 000 × 18 000 × 9 000 mm), while *Load Values*, setpoints, and *Internal Mass* are unchanged. Set the units back to metres.

#### Example definition

`examples/grasshopper/pipeline-skeleton.gh` holds steps 1–6 of the pipeline above with default inputs and *Multipliers* = 3: *Example Residential Presets* → *Linear Plan Generator* → *No Simplification* → *Stack Floors* → *Convert2BEM*, plus *Inspect* with panels on *Report* and *Provenance*. It is saved by a person in Rhino 8 (agents cannot create or check `.gh` files).

- [ ] Opened in Rhino 8 with the S2 plugin loaded, it solves without warnings or errors (the *Example Residential Presets* remark is expected) and every preview shows.

### S3 checklist — plan simplifiers and validation (`v0.3.0`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings), close Rhino, and start it again with the plugin loaded as described above.

#### Toolbar

- [ ] *3 Simplify*: No Simplification, Semantic Merge, Perimeter Core, Single Zone per Floor. *6 Inspect*: Inspect, Map Source to Target, Validate.
- [ ] *Convert2BEM* has the inputs *Building* and *Override* (default `False`) and 16 outputs, the last one *Provenance*.

#### Simplifiers

1. Place *Example Residential Presets* and *Linear Plan Generator* with every number input at its default, and connect *Presets* (the canonical 24 m × 18 m plan of the S2 checklist).
2. Connect the plan to *No Simplification*, *Semantic Merge*, *Perimeter Core* (*Depth* 4.57, the default), and *Single Zone per Floor*.
   - [ ] None of the four shows a warning or error.
   - [ ] The *Floor* outputs read `Floor (6 zones, NoSimplification)`, `Floor (4 zones, SemanticMerge)`, `Floor (5 zones, PerimeterCore)`, and `Floor (1 zones, SingleZonePerFloor)` (hover over the output or use a panel).
   - [ ] Semantic Merge previews the stair, the corridor, and one dwelling-unit zone per row; the partition between the two units of a row is gone.
   - [ ] Perimeter Core previews four trapezoidal perimeter zones that meet on the diagonals at the corners, and a rectangular core, all in the *Mixed* colour (green); the core has no window.
   - [ ] Single Zone per Floor previews one *Mixed* zone.
   - [ ] Every simplified floor shows the same windows as the *No Simplification* floor, at the same positions and sizes: three on the south façade, three on the north, three on the east, and one on the west (D-039).
3. Connect *Inspect* to each simplified floor.
   - [ ] Each *Report* equals the matching snapshot in `tests/Lod.Integration.Tests/Snapshots/` (`simplifier-SemanticMerge.txt`, `simplifier-PerimeterCore.txt`, `simplifier-SingleZonePerFloor.txt`); for example `surface P-South/W3 … glazing=19.200000 window(offset=1.367544 …)`, and `unconditioned` under `zone Stair-1`.
4. Connect *Map Source to Target* to the Perimeter Core floor.
   - [ ] It lists 18 rows. The rows with source `ST` have the targets `P-North`, `P-South`, and `P-West`, overlaps 8, 8, and 56 m², and source fractions 0.111111, 0.111111, and 0.777778.
5. Connect *Validate* to each simplified floor.
   - [ ] *Passed* is `True`, and *Report* starts with `PASSED`.
   - [ ] Semantic Merge: every line starts with `ok`. Perimeter Core and Single Zone per Floor: one line reads `note ConditionedFloorArea: reference 360.000000, actual 432.000000` (the unconditioned stair is merged into conditioned zones, D-038); every other line starts with `ok`.
   - [ ] Connected to the plan instead, *Validate* shows the error `Expected a floor or building, got Plan.`

#### Conversion

6. Connect each simplified floor in turn to *Stack Floors* (no multipliers), and the building to *Validate* and to *Convert2BEM*.
   - [ ] *Validate* reports `PASSED`; the `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` lines read `ok` (enforced, D-045, D-046).
   - [ ] *Convert2BEM* shows no warning or error and fills outputs 0–14 as in the S2 checklist. *Conditioned* is `False` only for `L0/Stair-1` of the Semantic Merge building; every zone of the Perimeter Core and Single Zone per Floor buildings is `True`.
   - [ ] *Provenance* starts with the provenance tree (`Stack`, then the simplifier, then `LinearPlanGenerator`), followed by `PASSED` and the `Floor0.` and `Building.` check lines, and has no `OVERRIDE` line.

#### Errors

- [ ] Set the *Perimeter Core* *Depth* to 10: the component turns red with `Error PlanTooNarrow: Perimeter depth 10 m leaves no valid core for this footprint.` and produces no floor. Set it back to 4.57.
- [ ] Set *Depth* to 0: the component shows `Error InvalidParameter: Perimeter depth must be positive, got 0.` Set it back to 4.57.

The blocked and overridden paths of *Convert2BEM* cannot be reached with valid pipeline components, because every simplifier and *Stack Floors* output validates; they are covered by code review of the gate and by the validator tests.

### S4 checklist — floor aggregators (`v0.4.0`)

Floor aggregators and the complete Checkpoint 1 pipeline. Prerequisite: the plugin built from this stage is loaded in Rhino 8 as described above, and the S3 checklist passes. The canonical floors are: *Example Residential Presets* → *Linear Plan Generator* with its default inputs (24 m × 18 m, 3 m storeys) → each of *No Simplification*, *Semantic Merge*, *Perimeter Core* (Depth 4.57), and *Single Zone per Floor*. To give an aggregator the same floor three times, pass the floor through *Duplicate Data* (Sets › List) with Number = 3. Give Multipliers as a panel with the three lines `1`, `3`, `1`.

- [ ] The **BEMGen › 4 Aggregate** panel shows *Stack Floors* (Stack), *Floor Area Multiplier* (Mult), and *Single Zone Merged* (1Zone).
- [ ] **Floor Area Multiplier on each canonical floor** (Multipliers 1, 3, 1): no runtime message; the preview shows three storeys with the plan's windows on every storey, with floors at 0, 6, and 12 m and empty gaps at 3 and 9 m (the building is 15 m tall, D-045); *Inspect* lists zones `L0/…`, `L2/…`, and `L4/…` with `multiplier=3` on the `L2/` zones, `Ground` floors on `L0/`, `Outdoors` ceilings on `L4/` (z = 15), and `Adiabatic` for every other floor and ceiling; its Provenance output starts with `FloorAreaMultiplier Multipliers=1,3,1 Storeys=L0x1,L2x3,L4x1`.
- [ ] **True elevations (D-045):** *Floor Area Multiplier* with the *No Simplification* floor three times and Multipliers 1, 8, 1: no runtime message; the preview shows storeys at 0, 15, and 27 m; *Inspect* lists zones `L0/…`, `L5/…` (`multiplier=8`), and `L9/…`, the top storey's ceilings `Outdoors` at z = 30; *Validate* gives Passed = True with the line `ok   Building.Height: reference 30.000000, actual 30.000000`.
- [ ] **Exposed storeys are split off (D-046):** *Floor Area Multiplier* with one floor (*No Simplification*) and Multipliers = 10 shows the remark `Info FloorTypeSplit: Floor type 0 (x10) has an exposed floor and ceiling; split into x1 + x8 + x1 so exposure is not multiplied (D-046).` and outputs a building, not an error. *Inspect* lists zones `L0/…` (`multiplier=1`), `L5/…` (`multiplier=8`), and `L9/…` (`multiplier=1`) at 0, 15, and 27 m, and its Provenance output starts with `FloorAreaMultiplier Multipliers=10 Storeys=L0x1,L5x8,L9x1`. *Validate* gives Passed = True.
- [ ] **Setback (D-046):** a second *Linear Plan Generator* with Length = 14 (other inputs at their defaults) → *No Simplification* gives a narrow floor (stair and one unit per row). *Merge* (Sets › Tree) the canonical floor, the canonical floor again, and the narrow floor into the Floors of a *Floor Area Multiplier* with Multipliers 1, 4, 3. It shows two remarks, `Info FloorTypeSplit: Floor type 1 (x4) has an exposed ceiling; split into x3 + x1 so exposure is not multiplied (D-046).` and `Info FloorTypeSplit: Floor type 2 (x3) has an exposed ceiling; split into x2 + x1 so exposure is not multiplied (D-046).`; its Provenance output starts with `FloorAreaMultiplier Multipliers=1,4,3 Storeys=L0x1,L2x3,L4x1,L6x2,L7x1`; *Inspect* shows `Outdoors` ceilings on `L4/` at z = 15 over the eastern part that the narrow floor leaves uncovered (180 m² in total) and on `L7/` at z = 24. *Validate* gives Passed = True with `ok` lines for `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` (reference 24.000000).
- [ ] **Mismatched multipliers:** three floors with two multipliers give the error `Give one multiplier per floor (3), or none for all 1.` on each of the three aggregators.
- [ ] **Single Zone Merged on each canonical floor** (Multipliers 1, 3, 1): the preview shows one zone in the Mixed colour across all five storeys (0 to 15 m), with no interior partitions and, on every storey, the windows at the same positions as in the detailed plan. *Inspect* shows a single zone line starting `zone BUILDING Mixed "Building" area=2160.000000 volume=6480.000000 parts=5 multiplier=1`, a `setpoints heatingMean=21.000000 coolingMean=24.000000` line (the zone is conditioned), and four lines `mass BUILDING area=432.000000 faces=2` at z = 3, 6, 9, and 12.
- [ ] **Convert2BEM on a Single Zone Merged building** (Multipliers 1, 3, 1): *Internal Mass* has one branch {0} with the value 3456 (4 slabs × 432 m² × 2 faces), not zero; *Windows* {0} holds 50 Breps (10 per storey); *Conditioned* {0} is True. For *Stack Floors* and *Floor Area Multiplier* buildings every *Internal Mass* branch is 0.
- [ ] **Single Zone Merged on the No Simplification floor:** *Validate* gives Passed = True; the Report has `ok` lines for `Building.GroundArea`, `Building.RoofArea`, `Building.ExposedFloorArea`, and `Building.Height` and the line `note Building.ConditionedFloorArea: reference 1800.000000, actual 2160.000000` (the unconditioned stair becomes part of the conditioned zone, reported only, D-038).
- [ ] **All 12 combinations** (Multipliers 1, 3, 1): for every simplifier × aggregator pair, *Validate* gives Passed = True with a Report that starts with `PASSED` and has no `FAIL` line, and *Convert2BEM* with Override = False converts without an error. Expected `note` lines: `Floor0.ConditionedFloorArea: reference 360.000000, actual 432.000000` for every building made from the Perimeter Core or Single Zone per Floor floor, and `Building.ConditionedFloorArea: reference 1800.000000, actual 2160.000000` for Single Zone Merged with the No Simplification or Semantic Merge floor; no other `note` lines.

| Simplifier \ Aggregator | Stack Floors | Floor Area Multiplier | Single Zone Merged |
| --- | --- | --- | --- |
| No Simplification | [ ] | [ ] | [ ] |
| Semantic Merge | [ ] | [ ] | [ ] |
| Perimeter Core | [ ] | [ ] | [ ] |
| Single Zone per Floor | [ ] | [ ] | [ ] |

- [ ] `examples/grasshopper/checkpoint-1-pipeline.gh` opens in a fresh Rhino 8 session and solves without errors. It wires every simplifier into every aggregator, *Validate*, and *Convert2BEM*, and reproduces the 12 combinations above.

### S4.1 checklist — presets, preview location, and icons (`v0.4.1`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings), close Rhino, and start it again with the plugin loaded as described above. Definitions saved before S4.1 lose their preset wiring: *Example Residential Presets* no longer exists and the *Linear Plan Generator* has new inputs (D-064).

#### Toolbar and icons

- [ ] *1 Program* shows Schedule, Load, Program Preset, Dwelling Unit Preset, Corridor Preset, and Stair Preset; *Example Residential Presets* is gone.
- [ ] Every BEMGen component on the toolbar and on the canvas shows its own icon, none shows Grasshopper's generic icon, and the icons of one panel share one accent colour. The BEMGen parameters show their icons in their tooltips and when placed from the *Params* search.

#### Default presets

1. Place *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset* with nothing connected.
   - [ ] Each shows the remark `Illustrative values; not sourced from DOE prototypes or standards.` and no warning or error.
   - [ ] Their *Preset* outputs read `Preset Example Dwelling Unit (DwellingUnit, WWR 0.3)`, `Preset Example Corridor (Corridor, WWR 0.2)`, and `Preset Example Stair (Stair, WWR 0.1)`.
   - [ ] *Dwelling Unit Preset* has the inputs Name, WWR, Conditioned, Heating, Cooling, Occupancy, Occupancy Schedule, Lighting, Lighting Schedule, Equipment, Equipment Schedule, Infiltration, and Infiltration Schedule; *Corridor Preset* and *Stair Preset* have Name, WWR, Conditioned, Heating, Cooling, Lighting, Lighting Schedule, Infiltration, and Infiltration Schedule. *Conditioned* defaults to `True` for the dwelling unit and the corridor and `False` for the stair.
2. Place *Linear Plan Generator* with every number input at its default and connect the three presets to *Dwelling Unit*, *Corridor*, and *Stair*.
   - [ ] No warning or error; the preview shows the canonical 24 m × 18 m plan of the S2 checklist.
   - [ ] *Inspect* on the plan gives a *Report* equal to `tests/Lod.Generators.Tests/Linear/Snapshots/linear-plan-canonical.txt`, and its *Provenance* contains `Presets=DwellingUnit:Example Dwelling Unit;Corridor:Example Corridor;Stair:Example Stair`.
3. Disconnect *Stair*.
   - [ ] The generator shows Grasshopper's warning that the input *Stair* failed to collect data and outputs no plan. Reconnect it.
4. Connect *Corridor Preset* to *Dwelling Unit* as well (both *Dwelling Unit* and *Corridor* now get the corridor preset).
   - [ ] The generator turns red with `Error PresetSpaceTypeMismatch [DwellingUnit]: Input DwellingUnit needs a DwellingUnit preset, got 'Example Corridor' (Corridor).` and outputs no plan. Reconnect *Dwelling Unit Preset*.
5. Set *WWR* of *Dwelling Unit Preset* to 0.5.
   - [ ] The windows of the dwelling units grow; in *Inspect* the line of `US1/W1` reads `glazing=15.000000`. Set it back to 0.3 (or disconnect the panel).
6. Set *Conditioned* of *Dwelling Unit Preset* to `False`.
   - [ ] In *Inspect* every dwelling-unit zone shows `unconditioned` instead of a `setpoints` line. Set it back to `True`.
7. Connect a *Schedule* component (Kind `Temperature`) to *Lighting Schedule* of *Corridor Preset*.
   - [ ] *Corridor Preset* turns red with an `Error ScheduleKindMismatch` message and outputs no preset. Disconnect it.

#### Preview location

8. Connect the canonical plan to *No Simplification* and *Single Zone per Floor*, and give *Single Zone per Floor* the *Preview Location* `0,30,0` (a *Vector XYZ* or a point).
   - [ ] The Single Zone per Floor preview sits 30 m north of the plan preview (bounding box 0,30,0 to 24,48,3); the No Simplification preview stays on the plan (0,0,0 to 24,18,3).
   - [ ] *Inspect* and *Validate* on the moved floor give the same results as without the move (the surface coordinates in *Report* are unchanged, `Passed` is `True`).
9. Connect the moved floor to *Stack Floors* with *Preview Location* left at its default.
   - [ ] The building previews at the origin (0,0,0 to 24,18,3), not 30 m north: downstream components do not inherit the move. Give *Stack Floors* the *Preview Location* `30,0,0`: its preview moves 30 m east.
   - [ ] *Convert2BEM* on that building outputs zone Breps between 0,0,0 and 24,18,3, at the true coordinates.
10. Give *Linear Plan Generator* the *Preview Location* `0,-30,0`.
   - [ ] Only the plan preview moves 30 m south; the floors and the building do not move.

### S4.2 checklist — aggregation methods, plan transform, and heat-transfer options (`v0.4.2`)

Build the plugin with `dotnet build src/Lod.Grasshopper -c Release` (0 warnings), close Rhino, and start it again with the plugin loaded as described above. Use a Rhino model in metres. The canonical floor is: *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset* → *Linear Plan Generator* with its default inputs (24 m × 18 m, 3 m storeys) → *No Simplification*. To give an aggregator the same floor three times, pass it through *Duplicate Data* (Sets › List) with Number = 3 and give Multipliers as a panel with the lines `1`, `3`, `1`. Definitions saved before S4.2 keep their components (D-064): a *Floor Area Multiplier* opens as *Stacked Floor Zone Multiplier*, and a *Single Zone Merged* opens as *Single Zone per Floor Type*, which now makes one zone per floor entry instead of one zone for the building.

#### Toolbar and icons

- [ ] *2 Generate* shows *Linear Plan Generator* and *Transform Plan* (TPlan). *4 Aggregate* shows *Stack Floors* (Stack), *Stacked Floor Zone Multiplier* (ZMult), *Single Zone per Floor Type* (1ZType), and *Single Zone Building* (1ZBldg); *Floor Area Multiplier* and *Single Zone Merged* are gone.
- [ ] *Transform Plan* has a green icon (a footprint, a turning arrow, and the turned footprint); *Single Zone per Floor Type* (a short block below a tall one) and *Single Zone Building* (one tall block) have purple icons that are told apart at toolbar size.

#### Aggregation methods and previews

1. Connect the canonical floor three times with Multipliers 1, 8, 1 to *Stacked Floor Zone Multiplier*.
   - [ ] No runtime message. *Inspect* lists zones `L0/…`, `L5/…` (`multiplier=8`), and `L9/…`; its Provenance output starts with `StackedFloorZoneMultiplier Multipliers=1,8,1 Storeys=L0x1,L5x8,L9x1`. *Validate* gives Passed = True.
   - [ ] The preview shows the whole 30 m building (bounding box 0,0,0 to 24,18,30): the modelled storeys at 0, 15, and 27 m in their space-type colours with their windows, and the storeys at 3 to 15 m and 18 to 27 m in transparent grey, without windows.
   - [ ] With *Preview Location* `30,0,0` the coloured and the grey storeys move 30 m east together; *Convert2BEM* still outputs zone Breps between 0,0,0 and 24,18,30.
2. Connect the canonical floor three times with Multipliers 1, 3, 1 to *Single Zone Building*.
   - [ ] No runtime message. The preview shows one closed volume in the Mixed colour from 0 to 15 m (bounding box 0,0,0 to 24,18,15) without horizontal seams at the slab levels, with the plan's windows on every storey.
   - [ ] *Inspect* starts its zone list with `zone BUILDING Mixed "Building" area=2160.000000 volume=6480.000000 parts=5 multiplier=1` and lists four lines `mass BUILDING area=432.000000 faces=2` at z = 3, 6, 9, and 12; its Provenance output starts with `SingleZoneBuilding Multipliers=1,3,1`. *Convert2BEM* outputs five Breps in *Zones* {0} and the *Internal Mass* value 3456.
3. Connect the same floors and multipliers to *Single Zone per Floor Type*.
   - [ ] No runtime message. *Inspect* lists three zones: `zone E0 Mixed "Floor type 0" area=432.000000 volume=1296.000000 parts=1`, `zone E1 Mixed "Floor type 1" area=1296.000000 volume=3888.000000 parts=3`, and `zone E2 Mixed "Floor type 2" area=432.000000 volume=1296.000000 parts=1`, and two lines `mass E1 area=432.000000 faces=2` at z = 6 and 9; its Provenance output starts with `SingleZonePerFloorType Multipliers=1,3,1`.
   - [ ] The preview shows three volumes, 0 to 3 m, 3 to 12 m (one closed volume without seams at 6 and 9 m), and 12 to 15 m.
   - [ ] *Validate* gives Passed = True. *Convert2BEM*: *Internal Mass* is 0, 1728, and 0 for branches {0}, {1}, {2}.

#### Transform Plan

4. Build a transform: *Rotate* (Transform › Euclidean) with any geometry, plane *XY Plane* at the origin, and angle 30° (switch the *Angle* input to degrees, or give 0.5235987756 rad), then *Move* with the vector 5.3, −2.1, 0, and combine their transforms (*X* outputs, rotation first) with *Compound* (Transform › Util). Connect the canonical plan and the compound transform to *Transform Plan*.
   - [ ] No runtime message. The preview shows the plan rotated 30° counter-clockwise about the origin and moved (bounding box about −3.7, −2.1, 0 to 26.084610, 25.488457, 3).
   - [ ] *Inspect* on the output: its Provenance starts with `TransformPlan RotationDegrees=` followed by 30 (to about 12 digits), `TranslationX=5.3` and `TranslationY=-2.1` (to about 12 digits), with `LinearPlanGenerator …` indented below; its Report lists the same zone and surface IDs as the input plan.
   - [ ] The rotated plan through each of the four simplifiers and each of the four aggregators (Multipliers 1, 3, 1) gives *Validate* Passed = True and no runtime message on the aggregators (16 combinations).
5. Replace the transform by the *X* output of *Scale* (Transform › Affine) with factor 2 about the origin.
   - [ ] *Transform Plan* shows the warning `Not applied (D-070): scaling, shear, or mirroring in plan, a rotation about another axis or scaling along z. Applied: a rotation of 0° about the world z axis and a translation of (0, 0) m in x and y.` and outputs the plan unscaled (bounding box 0,0,0 to 24,18,3).
6. Replace the transform by the *X* output of *Move* with the vector 0, 0, 3.
   - [ ] The warning starts `Not applied (D-070): a translation along z.`; the plan stays at elevation 0.

#### Unsupported storey

7. Give a second *Transform Plan* only the *Move* transform with the vector 5.3, −2.1, 0, pass the moved plan through *No Simplification*, and *Merge* (Sets › Tree) the canonical floor and the moved floor into the Floors of each aggregator with Multipliers 2, 2.
   - [ ] Every one of the four aggregators shows the warning `Warning UnsupportedStorey [L2]: The floor of storey 2 is not fully covered by storey 1: 134.670000 m² of it faces outdoors (D-074).` and still outputs a building; *Stacked Floor Zone Multiplier* also shows `FloorTypeSplit` remarks.
   - [ ] *Validate* on each gives Passed = True with `ok   Building.ExposedFloorArea: reference 134.670000, actual 134.670000`.

#### Heat-transfer options

8. Connect the *Stack Floors* building of the canonical floor (Multipliers 1, 3, 1) to *Convert2BEM*; *Convert2BEM* has the inputs Building, Override, EnableInternalWallHeatTransfer (IWHT), and EnableFloorHeatTransfer (FHT), both options `False` by default.
   - [ ] *Boundaries* contains no `Interzone:` text: the 90 walls between zones and the 48 floors and ceilings between storeys read `Adiabatic`. *Provenance* contains the line `OPTIONS: EnableInternalWallHeatTransfer=False EnableFloorHeatTransfer=False`.
   - [ ] IWHT = True: the 90 walls read `Interzone:<zone ID>` (for example `Interzone:L0/CO` on `L0/ST`), the floors and ceilings between storeys stay `Adiabatic`, and the *OPTIONS* line reads `EnableInternalWallHeatTransfer=True EnableFloorHeatTransfer=False`.
   - [ ] FHT = True (IWHT False): the 48 floors and ceilings between storeys read `Interzone:<zone ID>` and the walls `Adiabatic`.
   - [ ] *Validate* on the building gives the same report with every combination; *Zones*, *Surfaces*, and *Windows* are the same Breps.
9. Connect the *Stacked Floor Zone Multiplier* building of step 1 and set FHT = True.
   - [ ] Its floors and ceilings between storeys stay `Adiabatic` (D-075); with IWHT = True its walls between zones read `Interzone:<zone ID>`.
10. Connect the *Single Zone per Floor Type* building of step 3 and set FHT = True.
   - [ ] The 24 floor and ceiling pieces at 3 m and 12 m read `Interzone:E1`, `Interzone:E0`, or `Interzone:E2`; with FHT = False they read `Adiabatic`.

### S5 checklist — centred windows on rebuilt walls (`v0.5.0`)

S5 changes no component, input, output, icon, or GUID; only the windows of merged zones change (D-079, [ADR-012](../decisions/ADR-012-centred-windows.md)). Where earlier checklists expect the simplified or single-zone floors to show the plan's windows in place (S3 *Simplifiers* step 2, S4.2 *Aggregation methods* step 2), this checklist replaces those expectations.

#### Simplifiers

1. Connect the canonical plan (default *Linear Plan Generator* with the three default preset components) to the four plan simplifiers (*Perimeter Core* with *Depth* 4.57).
   - [ ] *No Simplification* shows the generator's ten windows: three on the south façade, three on the north, three on the east, and one on the west.
   - [ ] *Semantic Merge* shows one window per glazed outdoor wall, eight in all: the stair keeps its three, the corridor its one on the east, each dwelling-unit zone one on its long façade (`DwellingUnit-1/W4 … glazing=18.000000 window(offset=4.522774 sill=0.678416 10.954451x1.643168)` in *Inspect*) and one on the east.
   - [ ] *Perimeter Core* and *Single Zone per Floor* show one window per façade, four in all, each centred on its wall: south and north 12.393547 m × 1.549193 m at sill 0.725403 m (the south one from x = 5.803227 to 18.196773 m), east 9.674709 m × 1.612452 m at sill 0.693774 m (y = 4.162645 to 13.837355 m), west 5.692100 m × 0.948683 m at sill 1.025658 m (y = 6.153950 to 11.846050 m). The core has no window.
   - [ ] Each *Inspect* report equals the matching snapshot in `tests/Lod.Integration.Tests/Snapshots/`; every outdoor wall line ends with at most one `window(…)` entry.
   - [ ] *Validate* on each simplified floor gives Passed = True, and the lines `Glazing` and `Glazing.<orientation>` read `ok` with the same values as *Validate* on the *No Simplification* floor (59.4 m² in total: 19.2 south, 19.2 north, 15.6 east, 5.4 west).

#### Single-zone aggregators

2. Connect the *No Simplification* floor three times with Multipliers 1, 3, 1 to *Single Zone per Floor Type* and to *Single Zone Building*.
   - [ ] Every storey shows four windows, one centred on each façade, with the sizes of step 1 (*Single Zone Building*: 20 windows on 5 storeys).
   - [ ] *Stack Floors* and *Stacked Floor Zone Multiplier* on the same floors still show the generator's ten windows per modelled storey.
   - [ ] *Validate* on each building gives Passed = True with `Building.Glazing` = 297 m² (5 × 59.4).
   - [ ] *Convert2BEM*: *Windows* {0} holds 20 Breps for *Single Zone Building*.

#### Rotated plan

3. Put the canonical plan through *Transform Plan* with the 30° rotation and the move by 5.3, −2.1, 0 of the S4.2 checklist, then through each simplifier and each aggregator (Multipliers 1, 3, 1).
   - [ ] The merged walls carry one window each, centred on the rotated wall (in *Inspect*, `offset` equals (wall length − window width) / 2 for every window).
   - [ ] *Validate* gives Passed = True for all 16 combinations, with the same `Glazing.<orientation>` values as the rotated *No Simplification* floor, and no aggregator shows a runtime message.

### S8.1 checklist — bar typologies (`v0.8.0`)

S8.1 adds four plan generator components in *2 Generate* ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)) and the minimum wall and window geometry of every generator ([ADR-011](../decisions/ADR-011-minimum-wall-and-window-geometry.md)). No existing component, input, output, or GUID changes; the description of *Linear Plan Generator* names `HDHM-TYP-009`. Use the three default preset components (*Dwelling Unit Preset*, *Stair Preset*, and for the linear plan *Corridor Preset*) with nothing connected.

#### Toolbar and icons

- [ ] *2 Generate* shows *Linear Plan Generator*, *Stair Bay Bar*, *Stair Pair*, *Gallery Bar*, *Terrace Row*, and *Transform Plan*, each with its own green icon.
- [ ] Inputs, in order, with their defaults: *Stair Bay Bar* (SBar) Bay Count 3, Unit Width 7, Depth 12, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; *Stair Pair* (SPair) Unit Width 7, Depth 12, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; *Gallery Bar* (GBar) Unit Count 6, Unit Width 6, Depth 10, Stair Width 4, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; *Terrace Row* (Terr) Plot Count 6, Plot Width 5.5, Depth 10, Floor Height 3, Orientation 0, Dwelling Unit, Preview Location. Each has one output, *Plan*.
- [ ] With a preset input unconnected, the component shows Grasshopper's missing-input warning and outputs nothing (D-065).

#### Default plans

1. Place each new generator with its presets connected and nothing else changed; connect *Inspect* to each *Plan*.
   - [ ] *Stair Bay Bar*: no runtime message; nine zones `ST1`–`ST3`, `U1`–`U6`; footprint 51 m × 12 m (612 m²), stairs 36 m², dwellings 84 m²; every stair is flanked by the two dwellings of its bay (`ST2` between `U3` and `U4`, x = 24–27 m); 20 windows, 102.6 m² of glazing (40.5 south, 40.5 north, 10.8 east, 10.8 west in *Validate* on its *No Simplification* floor).
   - [ ] *Stair Pair*: three zones `ST1`, `U1`, `U2`; footprint 17 m × 12 m (204 m²); 8 windows, 48.6 m² of glazing.
   - [ ] *Gallery Bar*: eight zones `ST1`, `ST2`, `U1`–`U6`; footprint 44 m × 10 m (440 m²), stairs 40 m² at both ends, dwellings 60 m²; no gallery in the preview; 18 windows, 75.6 m² of glazing (34.8 south, 34.8 north, 3 east, 3 west).
   - [ ] *Terrace Row*: six zones `U1`–`U6` named *House 1*–*House 6*; footprint 33 m × 10 m (330 m²), 55 m² each; 14 windows, 77.4 m² of glazing.
   - [ ] Each *Inspect* report equals the snapshot `tests/Lod.Generators.Tests/<Family>/Snapshots/<family>-canonical.txt`.

#### Combinations

2. Connect each new plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] *Semantic Merge* gives 7 zones for *Stair Bay Bar* (the three stairs stay apart; dwellings of neighbouring bays merge), 3 for *Stair Pair*, 3 for *Gallery Bar*, and 1 for *Terrace Row*.
   - [ ] For all 16 combinations of each generator, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error.

#### Rotated placement

3. Put each new plan through *Transform Plan* with a 30° rotation about the world z axis and a move by 5.3, −2.1, 0, then through each simplifier and each aggregator (Multipliers 1, 3, 1).
   - [ ] *Validate* gives Passed = True for all 16 combinations of each generator, with the same total glazing as the unrotated plan.

#### Parameters and the minimum geometry

4. Change inputs one at a time and set each back afterwards.
   - [ ] *Stair Bay Bar* Bay Count 1: `Error InvalidParameter: BayCount must be at least 2 (one bay is HDHM-TYP-008, Stair Pair), got 1.` and no plan. *Gallery Bar* Unit Count 1 and *Terrace Row* Plot Count 1 give the matching errors; a width or depth of 0 gives `… must be positive, got 0.`
   - [ ] A *Stair Preset* in the *Dwelling Unit* input of *Stair Bay Bar*: `Error PresetSpaceTypeMismatch [DwellingUnit]: Input DwellingUnit needs a DwellingUnit preset, got 'Example Stair' (Stair).`
   - [ ] *Terrace Row* Plot Width 0.8: the plan is produced with twelve remarks such as `Info WindowOmitted [U1/W1]: Outdoor wall U1/W1 is 0.8 m long, below the 1 m minimum for a window (ADR-011); it has no window (0.72 m² of glazing not placed).`; only the two 10 m end walls show windows, and *Validate* on its *No Simplification* floor passes.
   - [ ] *Linear Plan Generator* with its defaults shows no remark, and its *Inspect* report equals `linear-plan-canonical.txt` (ADR-011 changes no existing plan).

### S8.2 checklist — non-rectangular typologies (`v0.8.1`)

S8.2 adds three plan generator components in *2 Generate* for the families without holes ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)) and makes *Semantic Merge* and the single-zone aggregators exact on rotated plans ([ADR-002](../decisions/ADR-002-geometry.md)). No existing component, input, output, or GUID changes. Use *Dwelling Unit Preset* and *Stair Preset* with nothing connected.

#### Toolbar and icons

- [ ] *2 Generate* shows *Point Plate*, *Winged Band*, and *Open Court* next to the S8.1 generators, each with its own green icon (a square pinwheel around a dark core, a comb, and a U).
- [ ] Inputs, in order, with their defaults: *Point Plate* (PPlate) Dwelling Depth 8, Core Width 6, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; *Winged Band* (WBand) Wing Count 3, Wing Length 17, Wing Spacing 17, Depth 12, Unit Width 7, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; *Open Court* (OCourt) Court Width 24, Court Depth 17, Depth 12, Unit Width 7, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location. Each has one output, *Plan*.
- [ ] With a preset input unconnected, the component shows Grasshopper's missing-input warning and outputs nothing (D-065).

#### Default plans

1. Place each new generator with its presets connected and nothing else changed; connect *Inspect* to each *Plan*.
   - [ ] *Point Plate*: no runtime message; five zones `ST` (*Core*), `U1`–`U4`; footprint 22 m × 22 m (484 m²), core 36 m² at x, y = 8–14 m with no outdoor wall, dwellings 112 m² in a pinwheel; 8 windows, 79.2 m² of glazing (19.8 m² per orientation in *Validate* on its *No Simplification* floor).
   - [ ] *Winged Band*: no runtime message; 21 zones `B-ST1`–`B-ST4`, `B-U1`–`B-U8`, `W1-ST1`, `W1-U1`, `W1-U2`, … `W3-U2`; a comb in a 70 m × 29 m box (1452 m²) with three 12 m wings to plan north; 43 windows, 217.8 m² of glazing (59.4 north, 55.8 south, 51.3 east, 51.3 west); the band's north façade between the wings carries a window on every fragment, the shortest 1.25 m.
   - [ ] *Open Court*: no runtime message; 15 zones `N-ST1`–`N-ST3`, `N-U1`–`N-U6`, `W-ST1`, `W-U1`, `W-U2`, `E-ST1`, `E-U1`, `E-U2`; a U in a 48 m × 29 m box (984 m²) whose 24 m × 17 m court is open to plan south; 30 windows, 154.8 m² of glazing (41.4 south, 37.8 north, 37.8 east, 37.8 west).
   - [ ] Each *Inspect* report equals the snapshot `tests/Lod.Generators.Tests/<Family>/Snapshots/<family>-canonical.txt`.

#### Combinations

2. Connect each new plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] *Semantic Merge* gives 2 zones for *Point Plate* (`DwellingUnit-1`, a ring around the core, previewed with the hole, and `Stair-1`), 13 for *Winged Band*, and 9 for *Open Court*.
   - [ ] *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, `CORE` for *Point Plate*; 13 zones for *Winged Band* (`P-North-1`–`P-North-5`, `P-East-1`–`P-East-3`, `P-South`, `P-West-1`–`P-West-3`, `CORE`) and 9 for *Open Court* (`P-North`, `P-East-1`, `P-East-2`, `P-South-1`–`P-South-3`, `P-West-1`, `P-West-2`, `CORE`), with diagonal walls also at the re-entrant corners.
   - [ ] For all 16 combinations of each generator, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error.

#### Rotated placement

3. Put each new plan through *Transform Plan* with a 30° rotation about the world z axis and a move by 5.3, −2.1, 0, then through each simplifier and each aggregator (Multipliers 1, 3, 1); repeat with a 131.4° rotation and a move by 15.08, −153.9, 0.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each generator and placement, with the same total glazing as the unrotated plan.
   - [ ] *Gallery Bar* (S8.1) through *Transform Plan* with a 321.2° rotation and a move by 136.4, −118.8, 0, then *Semantic Merge*, then *Single Zone Building* and *Single Zone per Floor Type*: no error and *Validate* passes (a regression check of the S8.2 geometry fixes; the integration test `SingleZoneMethodsCoverTheFacadesOfARotatedSemanticMergeFloor` covers the same case).

#### Parameters, preconditions, and the minimum geometry

4. Change inputs one at a time and set each back afterwards.
   - [ ] *Winged Band* Wing Count 1: `Error InvalidParameter: WingCount must be at least 2 (the wing-to-band relation repeats), got 1.` and no plan. A length of 0 on any of the three generators gives `… must be positive, got 0.`, for example *Point Plate* Core Width 0: `Error InvalidParameter: CoreWidth must be positive, got 0.`
   - [ ] *Open Court* Unit Width 0.5 and Stair Width 20: `Error InvalidParameter: StairWidth 20 m leaves no dwelling width in each 17 m side wing: its one stair bay needs 20 m of stairs; reduce StairWidth or UnitWidth.`
   - [ ] *Winged Band* Wing Spacing 14: the plan is produced with two remarks, `Info WindowOmitted [B-U4/W4]: Outdoor wall B-U4/W4 is 0.5 m long, below the 1 m minimum for a window (ADR-011); it has no window (0.45 m² of glazing not placed).` and the same for `B-U5/W3`; those two fragments show no window.
   - [ ] *Open Court* Depth 8 through *Perimeter Core* (Depth 4.57): `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: every wing and every part of the plan must be wider than twice the depth (9.14 m). Use a smaller depth or another simplifier.` and no floor; the other three simplifiers still work.

### S8.3 checklist — enclosed courtyard and footprints with holes (`v0.8.2`)

S8.3 adds one plan generator component in *2 Generate* for the enclosed courtyard ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)), the first footprint with a hole, and makes *Perimeter Core* zone court façades ([ADR-008](../decisions/ADR-008-perimeter-core-corners.md)). No existing component, input, output, or GUID changes. Use *Dwelling Unit Preset* and *Stair Preset* with nothing connected.

#### Toolbar and icons

- [ ] *2 Generate* shows *Enclosed Court* next to *Open Court*, with its own green icon (a closed square ring around a court, dark stairs).
- [ ] Inputs, in order, with their defaults: *Enclosed Court* (ECourt) Court Width 24, Court Depth 24, Depth 12, Unit Width 7, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; one output, *Plan*.
- [ ] With a preset input unconnected, the component shows Grasshopper's missing-input warning and outputs nothing (D-065).

#### Default plan

1. Place *Enclosed Court* with its presets connected and nothing else changed; connect *Inspect* to its *Plan*.
   - [ ] No runtime message; 24 zones `S-ST1`–`S-ST3`, `S-U1`–`S-U6`, `N-ST1`–`N-ST3`, `N-U1`–`N-U6`, `W-ST1`, `W-U1`, `W-U2`, `E-ST1`, `E-U1`, `E-U2`; a 48 m × 48 m block (1728 m²) around a 24 m × 24 m court at x, y = 12–36 m, which the preview shows as a hole.
   - [ ] 44 windows, 237.6 m² of glazing (57.6 north, 57.6 south, 61.2 east, 61.2 west in *Validate* on its *No Simplification* floor); 16 of the windows (79.2 m²) are on the court façades and face into the court.
   - [ ] The *Inspect* report equals the snapshot `tests/Lod.Generators.Tests/EnclosedCourt/Snapshots/enclosed-court-canonical.txt`.

#### Combinations

2. Connect the plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] *Semantic Merge* gives 12 zones: four L-shaped `DwellingUnit-…` zones, one around each corner of the court, and eight `Stair-…` zones.
   - [ ] *Perimeter Core* gives 9 zones `P-North`, `P-East`, `P-South`, `P-West`, `P-Court-North`, `P-Court-East`, `P-Court-South`, `P-Court-West`, `CORE`; the court zones hold the court façades and their windows, and `CORE` is a ring around the court (411.84 m²) without outdoor walls.
   - [ ] *Single Zone per Floor* gives one zone `FLOOR` with the court as a hole and 8 windows (4 outer, 4 court).
   - [ ] *Single Zone Building* gives one zone `BUILDING` with five parts, each with the court as a hole, previewed as one merged volume with the court open from ground to roof; 20 court walls, each with one centred window.
   - [ ] For all 16 combinations, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), ground and roof area are 1728 m² each (not 2304 m²), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error.
   - [ ] *Convert2BEM* *Zones* are closed Breps with inner walls along the court, and the floor and ceiling Breps of the zones that surround the court (`FLOOR`, `CORE`, `BUILDING`, `E0`–`E2`) are single faces with an inner loop for the court.
   - [ ] Orientation (all generators, not only this one): every *Convert2BEM* *Zones* Brep and every zone preview solid has a positive volume (outward-oriented); in *Surfaces* every wall normal points to the wall's facing, every floor normal down, and every ceiling normal up, interzone surfaces included; every *Windows* normal points the way its wall faces. Read a face's normal with `BrepFace.NormalAt`, which already includes `OrientationIsReversed` (negating it again for a reversed face gives the wrong direction); every planar face is built unreversed.

#### Rotated placement

3. Put the plan through *Transform Plan* with a 30° rotation about the world z axis and a move by 5.3, −2.1, 0, then through each simplifier and each aggregator (Multipliers 1, 3, 1); repeat with a 131.4° rotation and a move by 15.08, −153.9, 0.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each placement, with the same total glazing as the unrotated plan.

#### Parameters and preconditions

4. Change inputs one at a time and set each back afterwards.
   - [ ] Court Width 0: `Error InvalidParameter: CourtWidth must be positive, got 0.` and no plan.
   - [ ] Unit Width 0.5 and Stair Width 30: two errors, `Error InvalidParameter: StairWidth 30 m leaves no dwelling width in each 48 m south and north wing: its 2 stair bays need 60 m of stairs; reduce StairWidth or UnitWidth.` and the same for `each 24 m west and east wing: its one stair bay needs 30 m of stairs`.
   - [ ] Depth 9 through *Perimeter Core* (Depth 4.57): `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: every wing and every part of the plan must be wider than twice the depth (9.14 m). Use a smaller depth or another simplifier.` and no floor; the other three simplifiers still work.

### S8.4 checklist — non-residential programs, office plate, and cafeteria (`v0.8.3`)

S8.4 adds fifteen default preset components in *1 Program* for the non-residential space types ([ADR-014](../decisions/ADR-014-program-types-and-department-zoning.md)) and two plan generator components in *2 Generate* for the office plate (`SYN-TYP-017`) and the cafeteria (`SYN-TYP-016`) ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)). No existing component, input, output, or GUID changes.

#### Toolbar and icons

- [ ] *1 Program* shows, after *Stair Preset*, *Office Preset*, *Core Preset*, *Retail Preset*, *Mall Preset*, *Kitchen Preset*, *Dining Preset*, *Operating Theatre Preset*, *Clean Corridor Preset*, *Dirty Corridor Preset*, *Clinical Support Preset*, *Care Bedroom Preset*, *Care Communal Preset*, *Lobby Preset*, *Activity Hall Preset*, and *Service Preset*, each with its own orange icon.
- [ ] *2 Generate* shows *Office Plate* (a plate around a dark core) and *Cafeteria* (a dark kitchen band above a dining field with tables), each with its own green icon.
- [ ] Each preset component works with nothing connected, outputs one *Preset*, and shows the remark "Illustrative values; not sourced from DOE prototypes or standards."
- [ ] *Kitchen Preset* inputs, in order: Name (Example Kitchen), WWR (0.1), Conditioned (True), Heating (18), Cooling (26), Occupancy (0.05), Occupancy Schedule, Lighting (12), Lighting Schedule, Equipment (30), Equipment Schedule, Gas Equipment (40), Gas Equipment Schedule, Ventilation (15), Ventilation Schedule, Infiltration (0.3), Infiltration Schedule; the descriptions give W/m² for *Gas Equipment* and 1/h for *Ventilation*.
- [ ] *Operating Theatre Preset* defaults: WWR 0, Heating 20, Cooling 22, Ventilation 20; *Care Bedroom Preset*: Heating 22, Cooling 25.
- [ ] *Office Plate* (OPlate) inputs, in order, with their defaults: Plate Length 42, Plate Depth 30, Core Length 18, Core Depth 6, Floor Height 3.8, Orientation 0, Office, Core, Preview Location; one output, *Plan*.
- [ ] *Cafeteria* (Cafe) inputs: Length 30, Dining Depth 15, Kitchen Depth 8, Floor Height 4, Orientation 0, Kitchen, Dining, Preview Location; one output, *Plan*.
- [ ] With a preset input unconnected, each generator shows Grasshopper's missing-input warning and outputs nothing (D-065); *Office Preset* on the *Core* input gives `Error PresetSpaceTypeMismatch`.

#### Default plans

1. Place *Office Plate* with *Office Preset* and *Core Preset* connected; connect *Inspect* to its *Plan*.
   - [ ] No runtime message; zones `SC` (*Service Core*, 108 m²) and `OF` (*Office*, 1152 m²) in a 42 m × 30 m plate; the preview shows the office as a ring around the core at x = 12–30 m, y = 12–18 m.
   - [ ] 4 windows, 218.88 m² of glazing (63.84 north, 63.84 south, 45.6 east, 45.6 west in *Validate* on its *No Simplification* floor); the core has no outdoor wall and no window.
   - [ ] The *Inspect* report equals the snapshot `tests/Lod.Generators.Tests/OfficePlate/Snapshots/office-plate-canonical.txt`.
2. Place *Cafeteria* with *Kitchen Preset* and *Dining Preset* connected; connect *Inspect*.
   - [ ] No runtime message; zones `KS` (*Kitchen and Servery*, 240 m², y = 15–23 m) and `DI` (*Dining*, 450 m², y = 0–15 m).
   - [ ] 6 windows, 114.4 m² of glazing (12 north, 48 south, 27.2 east, 27.2 west).
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/Cafeteria/Snapshots/cafeteria-canonical.txt`.

#### Combinations

3. Connect each plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] Office: *Semantic Merge* gives two zones, the office still a ring; *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, `CORE` (685.4596 m², no outdoor walls); *Single Zone per Floor* gives one zone `FLOOR` without a hole and 4 windows.
   - [ ] Cafeteria: *Perimeter Core* gives `P-North` (kitchen only), `P-South` (dining only), `P-East`, `P-West`, `CORE`, all `Mixed`.
   - [ ] For all 16 combinations of each plan, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error; *Space Types* lists `Core`, `Office`, `Kitchen`, `Dining`, or `Mixed`.
   - [ ] *Convert2BEM* *Zones* of `OF` is one closed Brep with inner walls around the core; its floor and ceiling Breps are single faces with an inner loop for the core; every zone Brep has a positive volume (D-091).

#### Rotated placement

4. Put each plan through *Transform Plan* with a 30° rotation and a move by 5.3, −2.1, 0, then through each simplifier and aggregator (Multipliers 1, 3, 1); repeat with 131.4° and 15.08, −153.9, 0.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each placement, with the same total glazing as the unrotated plan.

#### Parameters

5. Change inputs one at a time and set each back afterwards.
   - [ ] *Office Plate* Core Length 40: `Error InvalidParameter: CoreLength 40 m leaves an office depth of 1 m at the west and east façades; SYN-TYP-017 needs at least 3 m of work area on every side of the core.` and no plan; Core Length 36 with Core Depth 24 (exactly 3 m on every side) gives a plan.
   - [ ] *Office Plate* Plate Depth 0: `Error InvalidParameter: PlateDepth must be positive, got 0.`
   - [ ] *Cafeteria* Kitchen Depth 15: `Error InvalidParameter: KitchenDepth 15 m must be smaller than DiningDepth 15 m: in SYN-TYP-016 the dining field is the larger part of the plan.` and no plan.

#### Result (S8.4)

Run by the controller as a scripted headless Grasshopper session (D-056) on 2026-10-02, on the verified reference of this sub-stage (`f841f0cf670cfff50f18c22e5ba39c0e43e78603`, whose `src/`, `tests/`, and `scripts/` are identical to the executed branch): Rhino 8.25.25314.11001, .NET 8.0.31, `BEMGen.gha` built in Release with 0 warnings, *BEMGen Info* version `0.8.2+f841f0cf670cfff50f18c22e5ba39c0e43e78603` (the version becomes 0.8.3 at the close-out).

- Passed: the 15 default preset components in *1 Program* and the 2 generator components in *2 Generate*, all primary, with the GUIDs of the S8.4 plan and 24 × 24 icons; every preset builds with only the remark "Illustrative values; not sourced from DOE prototypes or standards." (for example `Preset Example Office (Office, WWR 0.4)`, `Preset Example Operating Theatre (OperatingTheatre, WWR 0)`, `Preset Example Lobby (Lobby, WWR 0.5)`).
- Passed: *Office Plate* defaults: box (0, 0, 0)–(42, 30, 3.8), footprint 1260 m²; *Semantic Merge* 2 zones, *Perimeter Core* 5, *Single Zone per Floor* 1; *Stack Floors* (one floor) boundaries Adiabatic 8, Ground 2, Outdoors 6; 4 windows on the office façades and none on the core. *Zones*: the core of 6 faces, solid, valid, volume 410.4; the office of 10 faces, solid, valid, 2 inner loops, volume 4377.6 (4788 − 410.4). The office walls toward the core face into the core, the outer walls outward, floors down, ceilings up, windows as their walls. *Perimeter Core*: 5 valid solids, all with positive volume. *Single Zone Building* (1, 3, 1): *Validate* Passed = `True`, the preview one solid (0, 0, 0)–(42, 30, 19).
- Passed: *Cafeteria* defaults: box (0, 0, 0)–(30, 23, 4), footprint 690 m²; *Stack Floors* boundaries Adiabatic 2, Ground 2, Outdoors 8; 6 windows; *Zones* of volume 960 (kitchen and servery) and 1800 (dining), both valid solids of 6 faces; *Perimeter Core* 5 valid solids; *Single Zone Building* (1, 3, 1): *Validate* Passed = `True`, the preview one solid (0, 0, 0)–(30, 23, 20).
- Passed: all 96 combinations (the two families, on the canonical plan and rotated by 30° and moved by (5.3, −2.1, 0) and rotated by 131.4° and moved by (15.08, −153.9, 0), each through the four simplifiers and the four aggregators with 1, 3, 1): *Validate* Passed = `True`, no error, and no negative volume.
- Passed: *Office Plate* Core Length 40: `Error InvalidParameter: CoreLength 40 m leaves an office depth of 1 m at the west and east façades; SYN-TYP-017 needs at least 3 m of work area on every side of the core.`; Plate Length 0: `Error InvalidParameter: PlateLength must be positive, got 0.`; *Cafeteria* Kitchen Depth 20: `Error InvalidParameter: KitchenDepth 20 m must be smaller than DiningDepth 15 m: in SYN-TYP-016 the dining field is the larger part of the plan.`; a *Kitchen Preset* on the *Office* input: `Error PresetSpaceTypeMismatch [Office]: Input Office needs a Office preset, got 'Example Kitchen' (Kitchen).`; unconnected preset inputs: Grasshopper's missing-input warnings.
- Not performed, open for a person (D-058): the viewport look of the previews, the icons in the toolbar, the *Inspect* reports compared with the snapshots (the generator tests check them), and example definitions.

### S8.5 checklist — branching plans on a hub and its arms (`v0.8.4`)

S8.5 adds four plan generator components in *2 Generate* for the families that branch from a hub on the shared hub-and-arms layout ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)): the radial lobes (`SYN-TYP-010`), the branching mall (`SYN-TYP-014`), the care hub (`SYN-TYP-018`), and the foyer with halls (`SYN-TYP-019`). *Perimeter Core* keeps the footprint's own vertices in its perimeter zones ([ADR-008](../decisions/ADR-008-perimeter-core-corners.md)). No existing component, input, output, or GUID changes.

#### Toolbar and icons

- [ ] *2 Generate* shows, after *Cafeteria*, *Radial Lobes* (a cross of lobes around a dark core), *Branching Mall* (a T of shop wings along a dark branching mall), *Care Hub* (a hub with a table and three narrower wings with dark corridors), and *Foyer Halls* (a white foyer between two halls, a dark support wing above, an entrance arrow below), each with its own green icon.
- [ ] *Radial Lobes* (RLobes) inputs, in order, with their defaults: Lobe Count 4, Lobe Length 10, Lobe Width 12, Core Width 12, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location; one output, *Plan*.
- [ ] *Branching Mall* (BMall): Branch Count 3, Branch Length 40, Mall Width 8, Shop Depth 12, Anchor Depth 30, Floor Height 5, Orientation 0, Mall, Retail, Preview Location.
- [ ] *Care Hub* (CHub): Wing Count 3, Wing Length 30, Bedroom Depth 6, Corridor Width 2.4, Hub Width 16, Floor Height 3, Orientation 0, Care Bedroom, Care Communal, Corridor, Preview Location.
- [ ] *Foyer Halls* (FHalls): Hall Count 2, Hall Length 30, Hall Width 20, Support Length 10, Foyer Width 20, Floor Height 6, Orientation 0, Lobby, Activity Hall, Service, Preview Location.
- [ ] The count inputs are integers. With a preset input unconnected, each generator shows Grasshopper's missing-input warning and outputs nothing (D-065); a *Retail Preset* on the *Mall* input of *Branching Mall* gives `Error PresetSpaceTypeMismatch`.

#### Default plans

1. Place *Radial Lobes* with *Dwelling Unit Preset* and *Stair Preset* connected; connect *Inspect* to its *Plan*.
   - [ ] No runtime message; a cross of 624 m²: the core `ST` at x = y = 10–22 m and four lobes `L1` (east) to `L4` (south), each split along its axis into `L{i}-U1` and `L{i}-U2` of 60 m².
   - [ ] 16 windows, 115.2 m² of glazing (28.8 m² per orientation); the core has no outdoor wall.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/RadialLobes/Snapshots/radial-lobes-canonical.txt`.
2. Place *Branching Mall* with *Mall Preset* and *Retail Preset* connected; connect *Inspect*.
   - [ ] No runtime message; a T of 7744 m²; `MALL` (1984 m²) is one polygon through the court at x = 70–102 m, y = 0–32 m and the three 8 m strips; `B1-S1`, `B1-S2`, `B1-AN` to `B3-AN` around it.
   - [ ] 16 windows, 806 m² of glazing; the mall's only window is on the court's south side.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/BranchingMall/Snapshots/branching-mall-canonical.txt`.
3. Place *Care Hub* with *Care Bedroom Preset*, *Care Communal Preset*, and *Corridor Preset* connected; connect *Inspect*.
   - [ ] Six remarks `WindowOmitted`, one per 0.8 m hub corner; a T of 1552 m²: `HUB` at x = 30–46 m, y = 0–16 m and three wings, each `W{i}-CO` between `W{i}-B1` and `W{i}-B2`.
   - [ ] 16 windows, 217.92 m² of glazing; every corridor has one window at its end.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/CareHub/Snapshots/care-hub-canonical.txt`.
4. Place *Foyer Halls* with *Lobby Preset*, *Activity Hall Preset*, and *Service Preset* connected; connect *Inspect*.
   - [ ] No runtime message; a T of 1800 m²: `FO` at x = 30–50 m, y = 0–20 m, `H1` east, `H2` west, `SV` north; zones listed `FO`, `H1`, `H2`, `SV`.
   - [ ] 10 windows, 276 m² of glazing; the foyer's one window is on its south entrance façade.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/FoyerHalls/Snapshots/foyer-halls-canonical.txt`.

#### Combinations

5. Connect each plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] Radial lobes: *Semantic Merge* gives the core and four dwelling zones, one per lobe; *Perimeter Core* gives `P-North-1` to `P-West-3` and a cross-shaped `CORE` of 122.5796 m².
   - [ ] Branching mall: *Semantic Merge* gives `MALL` and one `Retail` zone of 1920 m² per branch.
   - [ ] Care hub: *Semantic Merge* keeps all ten zones; *Perimeter Core* gives six small perimeter zones of 3.656 m² at the hub corners.
   - [ ] For all 16 combinations of each plan, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error; every zone Brep has a positive volume (D-091).

#### Counts and rotated placement

6. Set each count to its smallest and largest value and repeat step 5 for each: Lobe Count 3 and 4, Branch Count 3 and 4, Wing Count 2 and 4, Hall Count 2 and 3.
   - [ ] Lobe Count 3: the core's south wall has a window; Branch Count 4: the mall has no outdoor wall; Wing Count 2: the wings leave the hub east and north; Hall Count 3: hall 3 is south of the foyer, which has no outdoor wall, and the zones are `FO`, `H1`, `H2`, `H3`, `SV`.
   - [ ] *Validate* gives Passed = True for every combination.
7. Put each default plan through *Transform Plan* with a 30° rotation and a move by 5.3, −2.1, 0, then through each simplifier and aggregator (Multipliers 1, 3, 1); repeat with 131.4° and 15.08, −153.9, 0.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each placement, with the same total glazing as the unrotated plan; *Care Hub* through *Perimeter Core* and *Single Zone Building* at 131.4° passes (it failed with `FacadeNotCovered` before S8.5).

#### Parameters

8. Change inputs one at a time and set each back afterwards.
   - [ ] *Radial Lobes* Lobe Count 5: `Error InvalidParameter: LobeCount must be at most 4 (lobes leave the core only on its four sides, D-100), got 5.`; Lobe Count 2: `Error InvalidParameter: LobeCount must be at least 3 (two lobes would be a bar through the core), got 2.`
   - [ ] *Radial Lobes* Lobe Width 13: `Error InvalidParameter: LobeWidth 13 m is wider than CoreWidth 12 m; an arm must not be wider than the hub it leaves, or it would overlap its neighbour beyond the hub's corner.`
   - [ ] *Branching Mall* Branch Count 2: `Error InvalidParameter: BranchCount must be at least 3 (two branches are a bend, not a branching), got 2.`
   - [ ] *Care Hub* Bedroom Depth 8: `Error InvalidParameter: The wing width 2·BedroomDepth + CorridorWidth 18.4 m is wider than HubWidth 16 m; an arm must not be wider than the hub it leaves, or it would overlap its neighbour beyond the hub's corner.`; Hub Width 14.4: no `WindowOmitted`.
   - [ ] *Foyer Halls* Hall Count 4: `Error InvalidParameter: HallCount must be at most 3 (the support wing takes one of the foyer's four sides, D-100), got 4.`
   - [ ] *Radial Lobes* Lobe Width 9 through *Perimeter Core* (Depth 4.57): `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: every wing and every part of the plan must be wider than twice the depth (9.14 m). Use a smaller depth or another simplifier.` and no floor; the other three simplifiers still work.

#### Result (S8.5)

Run by the controller as a scripted headless Grasshopper session (D-056) on 2026-10-02, on the verified reference of this sub-stage (`12a7e8318bb6f54dcffd59636ca2fe8e11113d6d`, whose `src/`, `tests/`, and `scripts/` are identical to the executed branch): Rhino 8.25.25314.11001, .NET 8.0.31, `BEMGen.gha` built in Release with 0 warnings, *BEMGen Info* version `0.8.3+12a7e8318bb6f54dcffd59636ca2fe8e11113d6d` (the version becomes 0.8.4 at the close-out); 54 scenarios.

- Passed: *Radial Lobes* (RLobes), *Branching Mall* (BMall), *Care Hub* (CHub), and *Foyer Halls* (FHalls) in *2 Generate*, all primary, with the GUIDs of the S8.5 plan and 24 × 24 icons; the integer count input first, the presets in record order, *Preview Location* last; unconnected presets give Grasshopper's missing-input warnings.
- Passed: *Radial Lobes* defaults: box (0, 0, 0)–(32, 32, 3), footprint 624 m²; *Semantic Merge* 5 zones, *Perimeter Core* 13, *Single Zone per Floor* 1; *Stack Floors* (one floor) boundaries Adiabatic 24, Ground 9, Outdoors 25. *Branching Mall*: footprint 7744 m², height 5 m; 4, 9, and 1 zones; Adiabatic 42, Ground 10, Outdoors 26. *Care Hub*: box (0, 0, 0)–(76, 46, 3), 1552 m², six `WindowOmitted` remarks for the 0.8 m hub corners; 10, 17, and 1 zones; Adiabatic 30, Ground 10, Outdoors 32. *Foyer Halls*: box (0, 0, 0)–(80, 30, 6), 1800 m²; 4, 9, and 1 zones; Adiabatic 6, Ground 4, Outdoors 14. The *Branching Mall* preview clipping box reports y = −0.72, because `PreviewGoo.ClippingBox` uses Rhino's fast, approximate box of the untrimmed planar surfaces of the mall zone; the geometry and the Breps are not affected.
- Passed: the 89 zone Breps inspected are valid solids, with no negative volume anywhere; *Single Zone Building* (1, 3, 1) previews one solid per family, (0, 0, 0)–(32, 32, 15), (172, 102, 25), (76, 46, 15), and (80, 30, 30), and *Validate* Passed = `True`.
- Passed: all 320 combinations (the four families on the canonical plan, rotated by 30° and moved by (5.3, −2.1, 0), rotated by 131.4° and moved by (15.08, −153.9, 0), and with the fewest and the most arms at 131.4°, each through the four simplifiers and the four aggregators with 1, 3, 1): *Validate* Passed = `True`, no error.
- Passed: the counts below and above their ranges (`Error InvalidParameter: LobeCount must be at least 3 (two lobes would be a bar through the core), got 2.`, `… at most 4 (lobes leave the core only on its four sides, D-100), got 5.`, and Branch Count 2 and 5, Wing Count 1 and 5, Hall Count 1 and 4 likewise); arms wider than the hub (`Error InvalidParameter: LobeWidth 14 m is wider than CoreWidth 12 m; an arm must not be wider than the hub it leaves, or it would overlap its neighbour beyond the hub's corner.`, the care hub's 14.4 m wings on a 12 m hub, the foyer's 25 m halls on a 20 m foyer); `Error InvalidParameter: BranchLength must be positive, got 0.`; 9 m lobes into *Perimeter Core*: `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: …`.
- Not performed, open for a person (D-058): the viewport look of the previews, the icons in the toolbar, the *Inspect* reports compared with the snapshots (the generator tests check them), and example definitions.

### S8.6 checklist — operating suite and court cluster (`v0.8.5`)

S8.6 adds two plan generator components in *2 Generate* ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)): the operating suite with separated clean and dirty routes (`SYN-TYP-015`) and the court cluster around several courts (`SYN-TYP-011`), the first footprint with several holes ([ADR-008](../decisions/ADR-008-perimeter-core-corners.md)). No existing component, input, output, or GUID changes.

#### Toolbar and icons

- [ ] *2 Generate* shows, after *Foyer Halls*, *Operating Suite* (a support block on the left and bands to its right: dark dirty corridors at the top and bottom, a white clean corridor between two green banks) and *Court Cluster* (a block with two court holes and a middle wing between them), each with its own green icon.
- [ ] *Operating Suite* (OSuite) inputs, in order, with their defaults: Bank Count 2, Bank Length 36, Theatre Depth 7, Clean Corridor Width 3, Dirty Corridor Width 2.4, Support Length 12, Floor Height 4.2, Orientation 0, Operating Theatre, Clean Corridor, Dirty Corridor, Clinical Support, Preview Location; one output, *Plan*.
- [ ] *Court Cluster* (CCluster): Court Count 2, Court Width 24, Court Depth 24, Depth 12, Unit Width 7, Stair Width 3, Floor Height 3, Orientation 0, Dwelling Unit, Stair, Preview Location.
- [ ] The count inputs are integers. With a preset input unconnected, each generator shows Grasshopper's missing-input warning and outputs nothing (D-065); a *Clean Corridor Preset* on the *Dirty Corridor* input gives `Error PresetSpaceTypeMismatch [DirtyCorridor]: Input DirtyCorridor needs a DirtyCorridor preset, got 'Example Clean Corridor' (CleanCorridor).`

#### Default plans

1. Place *Operating Suite* with *Operating Theatre Preset*, *Clean Corridor Preset*, *Dirty Corridor Preset*, and *Clinical Support Preset* connected; connect *Inspect* to its *Plan*.
   - [ ] No runtime message; a 48 m × 21.8 m plan of 1046.4 m², 4.2 m high: `SUP` at x = 0–12 m over the full depth, then from south to north `DC1` (y = 0–2.4 m), `TB1`, `CC1`, `TB2`, `DC2` (y = 19.4–21.8 m), each at x = 12–48 m.
   - [ ] 8 windows, 71.988 m² of glazing: three on `SUP`, two on each dirty corridor, one at the clean corridor's east end; the banks' east walls have no window (WWR 0) and no `WindowOmitted` remark.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/OperatingSuite/Snapshots/operating-suite-canonical.txt`.
2. Place *Court Cluster* with *Dwelling Unit Preset* and *Stair Preset* connected; connect *Inspect*.
   - [ ] No runtime message; an 84 m × 48 m block of 2880 m² with two courts as holes at x = 12–36 m and x = 48–72 m, y = 12–36 m; 39 zones: `S-…` and `N-…` (five stairs and ten dwellings each), `W-…`, `M1-…`, `E-…` (one stair and two dwellings each).
   - [ ] 72 windows, 374.4 m² of glazing, 32 of them (158.4 m²) on the court façades, facing into the courts; `M1-U1` has windows to the west and the east.
   - [ ] The *Inspect* report equals `tests/Lod.Generators.Tests/CourtCluster/Snapshots/court-cluster-canonical.txt`.

#### Combinations

3. Connect each plan to the four plan simplifiers (*Perimeter Core* Depth 4.57) and each floor three times, Multipliers 1, 3, 1, to the four floor aggregators.
   - [ ] Operating suite: *Semantic Merge* keeps all six zones; *Perimeter Core* gives `P-North`, `P-East`, `P-South`, `P-West`, and a `CORE` of 491.9676 m².
   - [ ] Court cluster: *Semantic Merge* gives six dwelling zones and thirteen stairs, none with a hole; *Perimeter Core* gives `P-North` to `P-West`, `P-Court-North-1`, `P-Court-North-2` to `P-Court-West-2` (130.5649 m² each), and a `CORE` of 712.5404 m² with two holes; *Single Zone Building* previews one solid with two courts through every storey.
   - [ ] For all 16 combinations of each plan, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error; every zone Brep has a positive volume (D-091).

#### Counts and rotated placement

4. Set Bank Count to 3 and 5 and Court Count to 3 and 4, and repeat step 3 for each.
   - [ ] Bank Count 3: the northmost band is `CC2`, a clean corridor with a north façade; Court Count 3: two middle wings `M1-…` and `M2-…` and three holes; *Perimeter Core* gives `P-Court-<Bin>-1` to `-3`.
   - [ ] *Validate* gives Passed = True for every combination.
5. Put each default plan through *Transform Plan* with a 30° rotation and a move by 5.3, −2.1, 0, then through each simplifier and aggregator (Multipliers 1, 3, 1); repeat with 131.4° and 15.08, −153.9, 0, and with Bank Count 5 and Court Count 4 at 131.4°.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each placement, with the same total glazing as the unrotated plan.

#### Parameters

6. Change inputs one at a time and set each back afterwards.
   - [ ] *Operating Suite* Bank Count 1: `Error InvalidParameter: BankCount must be at least 2 (the theatre banks repeat beside the support rooms), got 1.`; Bank Length 0: `Error InvalidParameter: BankLength must be positive, got 0.`
   - [ ] *Operating Theatre Preset* WWR 0.2: the operating suite has 10 windows, one on the east end of each bank.
   - [ ] *Court Cluster* Court Count 1: `Error InvalidParameter: CourtCount must be at least 2 (one court is SYN-TYP-005, Enclosed Court), got 1.`
   - [ ] *Court Cluster* Unit Width 0.5 and Stair Width 30: `Error InvalidParameter: StairWidth 30 m leaves no dwelling width in each 84 m south and north wing: its 3 stair bays need 90 m of stairs; reduce StairWidth or UnitWidth.` and `… in each 24 m west, middle, and east wing: its one stair bay needs 30 m of stairs; reduce StairWidth or UnitWidth.`
   - [ ] *Court Cluster* Depth 9 through *Perimeter Core* (Depth 4.57): `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: every wing and every part of the plan must be wider than twice the depth (9.14 m). Use a smaller depth or another simplifier.` and no floor; the other three simplifiers still work.

#### Result (S8.6)

Run by the controller as a scripted headless Grasshopper session (D-056) on 2026-10-02, on the verified reference of this sub-stage (`373af00d04cb32932947462f081c742711bcb638`, whose `src/`, `tests/`, and `scripts/` are identical to the executed branch): Rhino 8.25.25314.11001, .NET 8.0.31, `BEMGen.gha` built in Release with 0 warnings, *BEMGen Info* version `0.8.4+373af00d04cb32932947462f081c742711bcb638` (the version becomes 0.8.5 at the close-out); 27 scenarios.

- Passed: *Operating Suite* (OSuite) and *Court Cluster* (CCluster) in *2 Generate*, both primary, with the GUIDs of the S8.6 plan and 24 × 24 icons; the integer count input first, the presets in record order (Operating Theatre, Clean Corridor, Dirty Corridor, Clinical Support; Dwelling Unit, Stair), *Preview Location* last; unconnected presets give Grasshopper's missing-input warnings.
- Passed: *Operating Suite* defaults: box (0, 0, 0)–(48, 21.8, 4.2), footprint 1046.4 m²; *Semantic Merge* 6 zones, *Perimeter Core* 5, *Single Zone per Floor* 1; *Stack Floors* (one floor) boundaries Adiabatic 18, Ground 6, Outdoors 16; 8 windows, none on the theatre banks. *Court Cluster*: box (0, 0, 0)–(84, 48, 3), footprint 2880 m²; 19, 13, and 1 zones; Adiabatic 104, Ground 39, Outdoors 111; 72 windows; with three courts *Perimeter Core* gives 17 zones.
- Passed: the 92 zone Breps inspected are valid solids, with no negative volume anywhere; the *Perimeter Core* core of the court cluster is one solid with two holes (three with three courts); *Single Zone Building* (1, 3, 1) previews one solid per family, (0, 0, 0)–(48, 21.8, 21) and (84, 48, 15), and *Validate* Passed = `True`.
- Passed: all 160 combinations (the two families on the canonical plan, rotated by 30° and moved by (5.3, −2.1, 0), rotated by 131.4° and moved by (15.08, −153.9, 0), and with the fewest and the largest tested count (5 banks, 4 courts) at 131.4°, each through the four simplifiers and the four aggregators with 1, 3, 1): *Validate* Passed = `True`, no error.
- Passed: the error cases (`Error InvalidParameter: BankCount must be at least 2 (the theatre banks repeat beside the support rooms), got 1.`, `Error InvalidParameter: CourtCount must be at least 2 (one court is SYN-TYP-005, Enclosed Court), got 1.`, `Error InvalidParameter: BankLength must be positive, got 0.`; Unit Width 0.5 and Stair Width 30: `Error InvalidParameter: StairWidth 30 m leaves no dwelling width in each 84 m south and north wing: its 3 stair bays need 90 m of stairs; reduce StairWidth or UnitWidth.` and the same for the west, middle, and east wings); Depth 9 into *Perimeter Core*: `Error PlanTooNarrow: Perimeter depth 4.57 m leaves no valid core for this footprint: …`.
- Not performed, open for a person (D-058): the viewport look of the previews, the icons in the toolbar, the *Inspect* reports compared with the snapshots (the generator tests check them), and example definitions.

### S8.7 checklist — plans per storey and the stepped band (`v0.8.6`)

S8.7 adds one plan generator component in *2 Generate* ([ADR-006](../decisions/ADR-006-plan-generation-mechanism.md)), the stepped dwelling band with exposed terraces (`SYN-TYP-012`), the first generator that returns one plan per storey ([ADR-015](../decisions/ADR-015-plans-per-storey.md)). Its *Plan* output is a list; no existing component, input, output, or GUID changes.

#### Toolbar and icons

- [ ] *2 Generate* shows, after *Court Cluster*, *Stepped Band* (a section of three green storeys stepping back from the left, with a dark rear corridor on the right), with its own green icon.
- [ ] *Stepped Band* (SBand) inputs, in order, with their defaults: Storey Count 3, Length 36, Base Depth 14, Step Depth 3, Corridor Width 2, Unit Width 6, Stair Width 4, Floor Height 3, Orientation 0, Dwelling Unit, Corridor, Stair, Preview Location; one output, *Plan*, with list access.
- [ ] Storey Count is an integer. With a preset input unconnected, the generator shows Grasshopper's missing-input warning and outputs nothing (D-065); a *Stair Preset* on the *Corridor* input gives `Error PresetSpaceTypeMismatch [Corridor]: Input Corridor needs a Corridor preset, got 'Example Stair' (Stair).` once, not once per storey.

#### Default plans

1. Place *Stepped Band* with *Dwelling Unit Preset*, *Corridor Preset*, and *Stair Preset* connected; connect *Inspect* to its *Plan*.
   - [ ] No runtime message; *Plan* holds three plans, bottom-up, of 576 m², 468 m², and 360 m²: storey `k` spans x = 0–36 m and y = 3k–16 m, with `ST` at x = 0–4 m, `U1` to `U5` of 6.4 m each, and `CO` at y = 14–16 m over the full length.
   - [ ] The preview shows the three storeys stacked at 0 m, 3 m, and 6 m, each lower storey with a 36 m × 3 m terrace in front of the one above; with *Preview Location* 0, 40, 0 the whole stack moves, and the plans' data stay at elevation 0 (*Inspect*: every zone `z=0`).
   - [ ] 11 windows per storey (33 in all, 201.6 m² of glazing); on storeys 1 and 2 the south walls of `ST` and `U1` to `U5`, which face the terrace below, have windows.
   - [ ] The three *Inspect* reports equal the three sections `storey 0` to `storey 2` of `tests/Lod.Generators.Tests/SteppedBand/Snapshots/stepped-band-canonical.txt`, and each *Provenance* shows `SteppedBandGenerator … Storey=k …`.

#### Combinations

2. Connect the *Plan* list to each of the four plan simplifiers (*Perimeter Core* Depth 4.57) and each simplifier's *Floor* list to the four floor aggregators, with *Multipliers* unconnected.
   - [ ] Every simplifier outputs three floors; *Semantic Merge* gives each storey `ST`, `CO`, and one dwelling zone; *Perimeter Core* gives each storey `P-North`, `P-East`, `P-South`, `P-West`, and `CORE`.
   - [ ] *Stack Floors* (NoSimplification): the building is 9 m high; *Inspect* shows on storeys 0 and 1 ceiling pieces facing `Outdoors` of 108 m² in all (the terrace: 12 m² of `ST` and 19.2 m² of each dwelling) and the rest `Interzone` with the storey above; no `UnsupportedStorey` warning.
   - [ ] *Single Zone per Floor Type*: zones `E0`, `E1`, `E2`; *Single Zone Building*: one zone `BUILDING` previewed as one stepped solid, (0, 0, 0)–(36, 16, 9), with its windows.
   - [ ] For all 16 combinations, *Validate* gives Passed = True (only `ConditionedFloorArea` may read `note`), `Building.RoofArea` reads 576, no aggregator shows a warning, and *Convert2BEM* with Override = False converts without an error; every zone Brep has a positive volume (D-091).

#### Counts and rotated placement

3. Set Storey Count to 2, and to 4 with Base Depth 17, and repeat step 2 for each.
   - [ ] Two and four plans; *Validate* gives Passed = True for every combination.
   - [ ] Storey Count 4 with Base Depth 14 through *Perimeter Core*: the top storey (7 m deep) gives `Error PlanTooNarrow: …` and no floor for it; the other three storeys give floors.
4. Put the *Plan* list through *Transform Plan* with a 30° rotation and a move by 5.3, −2.1, 0 (every storey alike), then through each simplifier and aggregator; repeat with 131.4° and 15.08, −153.9, 0, and with Storey Count 4 and Base Depth 17 at 131.4°.
   - [ ] *Validate* gives Passed = True for all 16 combinations of each placement, with the same total glazing as the unrotated band.

#### Parameters

5. Change inputs one at a time and set each back afterwards.
   - [ ] Storey Count 1: `Error InvalidParameter: StoreyCount must be at least 2 (the band steps back from storey to storey, R001), got 1.`
   - [ ] Storey Count 5 with Base Depth 12: `Error InvalidParameter: BaseDepth 12 m leaves no dwelling depth on the top storey: its 4 steps of StepDepth 3 m take 12 m; SYN-TYP-012 needs dwellings on every storey, so reduce StoreyCount or StepDepth, or increase BaseDepth.`
   - [ ] Length 4: `Error InvalidParameter: Length 4 m must exceed StairWidth 4 m, so that the band has dwellings beside the stair (R002).`; Step Depth 0: `Error InvalidParameter: StepDepth must be positive, got 0.`
   - [ ] Corridor Width 0.8: six `WindowOmitted` remarks, two per storey, each starting `Storey k: Outdoor wall CO/…`.

#### Result (S8.7)

Run by the controller as a scripted headless Grasshopper session (D-056) on 2026-10-02, on the verified reference of this sub-stage (`a98d4c52d53bfcfde8a5f5686f0ab7e5aea85c1b`, whose `src/`, `tests/`, and `scripts/` are identical to the executed branch): Rhino 8.25.25314.11001, .NET 8.0.31, `BEMGen.gha` built in Release with 0 warnings, *BEMGen Info* version `0.8.5+a98d4c52d53bfcfde8a5f5686f0ab7e5aea85c1b` (the version becomes 0.8.6 at the close-out); 18 scenarios.

- Passed: *Stepped Band* (SBand) in *2 Generate*, primary, with the GUID of the S8.7 plan and a 24 × 24 icon; the integer Storey Count first, the presets in record order (Dwelling Unit, Corridor, Stair), *Preview Location* last; unconnected presets give Grasshopper's missing-input warnings.
- Passed: the *Plan* output holds three plans by default, bottom-up (`Plan (7 zones, SteppedBandGenerator)` each), footprints 576, 468, and 360 m²; each storey's preview is drawn at its elevation (offsets (0, 0, 0), (0, 0, 3), and (0, 0, 6); boxes (0, 0, 0)–(36, 16, 3), (0, 3, 3)–(36, 16, 6), and (0, 6, 6)–(36, 16, 9)). Wired item-wise, each simplifier returns three floors (*No Simplification* 7 zones, *Semantic Merge* 3, *Perimeter Core* 5, *Single Zone per Floor* 1 per storey); *Stack Floors* builds `Building (21 zones, Stack)` with multipliers 1, 1, 1 and also with its *Multipliers* input left at its default; *Validate* Passed = `True`; `Building.RoofArea` and `Building.GroundArea` reference 576, actual 576.
- Passed: the terraces (*Single Zone per Floor* → *Stack Floors*): the ground storey's ceiling has a piece between storeys over y = 3–16 m (Adiabatic, +z) and an outdoor terrace piece over y = 0–3 m (Outdoors, +z); the middle storey likewise (y = 6–16 m between storeys, y = 3–6 m terrace); the top ceiling is a roof (+z); the floors above the ground face −z (Adiabatic), the ground floor −z (Ground).
- Passed: the 42 zone Breps inspected are valid solids, with no negative volume anywhere; *Single Zone Building* (1, 1, 1) previews one solid (0, 0, 0)–(36, 16, 9) with three parts, *Validate* Passed = `True`, `Building.RoofArea` 576.
- Passed: all 80 combinations (the band on the canonical plan, rotated by 30° and moved by (5.3, −2.1, 0), rotated by 131.4° and moved by (15.08, −153.9, 0), and with 2 storeys and with 4 storeys of Base Depth 17 m at 131.4°, each through the four simplifiers and the four aggregators with multiplier 1 per storey): *Validate* Passed = `True`, no error, `Building.RoofArea` passed.
- Passed: the error cases (`Error InvalidParameter: StoreyCount must be at least 2 (the band steps back from storey to storey, R001), got 1.`; Base Depth 6: `Error InvalidParameter: BaseDepth 6 m leaves no dwelling depth on the top storey: its 2 steps of StepDepth 3 m take 6 m; …`; Length 3: `Error InvalidParameter: Length 3 m must exceed StairWidth 4 m, so that the band has dwellings beside the stair (R002).`; `Error InvalidParameter: StepDepth must be positive, got 0.`); 4 storeys with the default 14 m base depth into *Perimeter Core*: `Error PlanTooNarrow: …` (the 7 m top storey).
- Not performed, open for a person (D-058): the viewport look of the previews, the icons in the toolbar, the *Inspect* reports compared with the snapshot (the generator tests check them), and example definitions.

### S8.8 checklist — storey previews, the any-program preset, and the preset panel (`v0.8.7`)

S8.8 (D-108) previews the floors simplified from a storey plan at the storey's height, adds the parameter *Any Program Preset*, and moves the eighteen built-in preset components to a panel of their own. No component is added or removed, no GUID changes, and no data output changes.

#### Toolbar and icons

- [ ] *1 Program* shows *Schedule*, *Load*, *Program Preset*, and the parameter *Any Program Preset* (AnyP; a hexagon with an orange tag marked by an asterisk); *1 Program Presets*, next to it, shows the eighteen built-in preset components, from *Dwelling Unit Preset* to *Service Preset*, with their orange icons unchanged.
- [ ] The six parameters of S2 are still hidden from the toolbar.

#### Any program preset

1. Place *Linear Plan Generator* with *Dwelling Unit Preset* and *Stair Preset* on their inputs. Place *Any Program Preset* on the canvas, wire *Office Preset*'s *Preset* into its left grip and its right grip into the generator's *Corridor* input; connect *Inspect* to the *Plan*.
   - [ ] Hovering the parameter's output shows `Preset Example Office (any program, no space type, WWR 0.4)`; the generator's *Corridor* input description ends with the any-program sentence.
   - [ ] No runtime message on the generator; the corridor `CO` is still a `Corridor` zone (its preview colour and *Inspect*), with the office loads (occupancy 0.1 people/m², lighting and equipment 10 W/m²), and its outdoor walls carry windows of WWR 0.4.
   - [ ] *Inspect*'s provenance shows `AnyProgramPreset.Corridor=Example Office` and `Presets=DwellingUnit:Example Dwelling Unit;Corridor:Example Office;Stair:Example Stair`.
   - [ ] Wiring *Office Preset* directly into *Corridor*, without the parameter, still gives `Error PresetSpaceTypeMismatch [Corridor]: Input Corridor needs a Corridor preset, got 'Example Office' (Office).`
2. Wire *Program Preset* (any space type) and each of three other built-in preset components through *Any Program Preset* into the inputs of *Office Plate*, *Operating Suite*, and *Stepped Band*.
   - [ ] Every generator accepts them on every input; with the plan through each simplifier and aggregator, *Validate* gives Passed = True and *Convert2BEM* reports the zones' own space types.
   - [ ] An unconnected *Any Program Preset* is empty, and a generator input fed only by it shows Grasshopper's missing-input warning.

#### Storey previews

3. Wire *Stepped Band* (defaults) into each of the four simplifiers, also through *Transform Plan* (30°, 5.3, −2.1, 0).
   - [ ] Every simplifier previews its three floors at 0 m, 3 m, and 6 m, as the generator previews its plans; *Transform Plan* previews its moved storeys at the same heights; with a simplifier's *Preview Location* 0, 40, 0 its whole stack moves.
   - [ ] *Inspect* shows every zone of every plan and floor at `z=0`; the aggregated buildings, their previews, and *Convert2BEM* are as in S8.7.
   - [ ] A floor simplified from a plan of a single-plan generator (*Linear Plan Generator*) is still previewed at 0 m.

#### Result (S8.8)

Run by the controller as a scripted headless Grasshopper session (D-056) on 2026-10-02, on the verified reference of this stage (`d9c305913a75c5bd9076386da4e384067a3fb16d`, whose `src/`, `tests/`, and `scripts/` are identical to the executed branch): Rhino 8.25.25314.11001, .NET 8.0.31, `BEMGen.gha` built in Release with 0 warnings, *BEMGen Info* version `0.8.6+d9c305913a75c5bd9076386da4e384067a3fb16d` (the version becomes 0.8.7 at the close-out); 9 scenarios and 1 repeated to read the provenance.

- Passed: *1 Program* holds *Any Program Preset* (AnyP, `24bc6a12-ad06-4c25-bc9d-4e8318b8744c`, primary, 24 × 24 icon), *Program Preset*, *Load*, and *Schedule*; *1 Program Presets* holds the eighteen built-in presets (*Activity Hall Preset* … *Stair Preset*), all primary with 24 × 24 icons and unchanged GUIDs; the six parameters of S2 stay hidden in *0 Info*. An unconnected AnyP shows Grasshopper's warning `Floating parameter AnyP failed to collect data`.
- Passed: *Office Preset* → AnyP holds `Preset Example Office (any program, no space type, WWR 0.4)` (the Office preset itself is `Preset Example Office (Office, WWR 0.4)`).
- Passed: AnyP(Office) on the *Linear Plan Generator*'s *Corridor* input: no runtime message; `Plan (6 zones, LinearPlanGenerator)`; the provenance includes `AnyProgramPreset.Corridor=Example Office`; *No Simplification* → *Stack Floors* → *Validate* Passed = `True`. *Office Preset* wired directly into the same input: `Error PresetSpaceTypeMismatch [Corridor]: Input Corridor needs a Corridor preset, got 'Example Office' (Office).`
- Passed: AnyP(Kitchen) on both inputs of *Office Plate*: no runtime message; the provenance records `AnyProgramPreset.Core=Example Kitchen`, followed by the `AnyProgramPreset.Office` entry (the harness cut its output line there).
- Passed: AnyP(Care Bedroom) on all three inputs of *Stepped Band*: all 16 simplifier × aggregator combinations (multipliers 1, 1, 1) give *Validate* Passed = `True`.
- Passed: the storey previews of the default stepped band: the generator's three plans and the floors of every simplifier (*No Simplification*, *Semantic Merge*, *Perimeter Core*, *Single Zone per Floor*) are drawn at z 0–3, 3–6, and 6–9; through *Transform Plan* (30°, moved by (5.3, −2.1, 0)) the plans and the simplified floors keep the same heights; a simplifier *Preview Location* of (0, 40, 0) moves the three floors by +40 in y at the same heights; the linear plan and its floors stay at z 0–3. (The *Semantic Merge* and *Perimeter Core* boxes extend slightly beyond the footprint because `ClippingBox` uses Rhino's fast, approximate Brep box, as before.)
- Not performed, open for a person (D-058): the viewport look of the previews, the toolbar panel layout and icons, a non-preset value wired into AnyP (which may raise Grasshopper's cast assert, as for every BEMGen parameter), and example definitions.

### S6 checklist — envelope preset and Convert2IDF (`v0.9.0`)

Envelope preset and *Convert2IDF*; the scripted run is `scripts/rhino-smoke/specs/convert-idf.py`.

1. Find *Envelope Preset* in *1 Program Presets* and place it with nothing connected.
   - [ ] It has a 24 × 24 icon, the remark `Illustrative values; not sourced from ASHRAE 90.1, DOE prototypes, or other standards.`, and its *Envelope* output shows `Envelope Example Envelope (7 constructions, window U 1.8 SHGC 0.4 VT 0.7)`.
   - [ ] *SHGC* 1.5 gives `Error EnvelopeValue [Example Double Glazing]: …` and no output.
2. Wire the canonical *Linear Plan Generator* through *No Simplification* into *Stack Floors* (Multipliers 2) and into *Convert2BEM*, once with *Envelope* unconnected and once with *Envelope Preset* (U-Factor 1.4) connected.
   - [ ] *Constructions* is aligned with *Surfaces* in every branch: `Example Exterior Wall` for `Outdoors` walls, `Example Interior Wall` for walls between zones, `Example Ground Floor`, `Example Roof`, `Example Interior Floor` and `Example Interior Floor Reversed` for the floors and ceilings between storeys; *Window Constructions* is aligned with *Windows* and holds `Example Double Glazing`.
   - [ ] *Provenance* ends its options with the line `ENVELOPE: Example Envelope` in both cases; the other outputs are as before.
3. Wire *Convert2IDF* (*5 Convert*, 24 × 24 icon) after each aggregator of the linear plan and of *Enclosed Court*, *Path* a file in an existing folder outside the repository, *Write* true.
   - [ ] *Written* is True, the file exists, and *IDF* holds the same text; with *Write* false nothing is written and *Written* is False.
   - [ ] Writing another building to an existing file shows `Error FileExists [<path>]` and keeps the file; with *Overwrite* true it is replaced. *Write* true without *Path* shows `Error InvalidParameter`.
   - [ ] `python scripts/idd-check/idd_check.py <Energy+.idd> <folder>` reports 0 problems for the written files.

#### Result (S6)

Run headless (D-111) on 2026-10-02 on `feature/grasshopper-convert-idf`, the plugin built at `0583470` with the component change and the spec as committed in `ec16399`, in Rhino 8.25 (.NET 8): `convert-idf` 12 scenarios, Validate True 32 of 32, no exceptions or missing components; runtime errors only in its error scenarios (SHGC 1.5, a file that exists without *Overwrite*, *Write* without *Path*, and the failed *Envelope Preset* of the last scenario), each with the expected message; wired into *Convert2IDF* and *Convert2BEM*, that failed preset gives both the warning `Envelope is connected but yields no envelope preset; the Example Envelope is used instead.` *Envelope Preset* (primary in *1 Program Presets*) and *Convert2IDF* (primary in *5 Convert*) registered with 24 × 24 icons; the example envelope shows `Envelope Example Envelope (7 constructions, window U 1.8 SHGC 0.4 VT 0.7)`; *Convert2BEM*'s *Constructions* (80 items) and *Window Constructions* (20) are aligned with *Surfaces* and *Windows*, with the interior floor and its reverse on the floors and ceilings between the two storeys. All 32 *Convert2IDF* outputs wrote their file (*Written* True), for example 564 objects for the linear plan through *No Simplification* and *Stack Floors* (1, 3, 1); *Write* false wrote nothing; the existing file kept its size and content without *Overwrite* and was replaced with it. `scripts/idd-check` on the 33 files written: 0 problems against the EnergyPlus 25.2.0 IDD. In Rhino the IDF outputs are counted and checked against the IDD; their references and invariants are checked by the parse-back in the unit tests (`Lod.Export.Tests`). Regression: `any-preset-and-previews` (9 scenarios, Validate 17 of 17 True, its one expected error) and `linear-and-aggregators` (12 scenarios, Validate 20 of 20 True, no errors) unchanged. A failed validation cannot be built from the components, so blocking and *Override* are covered by unit tests only. Open for a person (D-058): the toolbar look of the new icons, and opening a written IDF in EnergyPlus once a weather file is chosen (D-112).

### S9 checklist — example definitions, component reference, and screenshots (`v1.0.0`)

The example definitions in `examples/` are built and checked by `scripts/rhino-smoke/specs/examples.py` (D-115); the data of the component reference and the screenshots of the docs site are captured by the specs in `scripts/docs-export/` (`scripts/docs-export/README.md`). Since D-118 the site is in the public repository `energy-atlas/BEMGen-docs`, which renders the reference from the export.

1. Scripted: `run.ps1 -Spec examples` reopens and solves every example.
   - [ ] 19 definitions (18 plan generators and `end-to-end.gh`), each with *Validate* Passed = True, no runtime warning or error, no exception.
2. Scripted, with Rhino and the Grasshopper editor on screen: `scripts/docs-export/export.ps1 -OutDir <folder>` (the metadata spec, then the screenshots spec).
   - [ ] `component-metadata.json` lists every registered BEMGen component and parameter, and every one has an icon in `icons/`; the metadata log has no `Gap:` line.
3. In the same export:
   - [ ] For every example a canvas image and the plan and building previews in `screenshots/`; the docs repository's import renders them into the reference.
4. For a person in Rhino 8:
   - [ ] Open `examples/end-to-end.gh` and two typology examples from the Grasshopper editor: they solve without errors, the columns, groups, and scribbles read left to right, and the previews show the plan and the 5-storey building.

#### Result (S9)

Run headless (D-111) on 2026-10-03 on `main` at `19c8e2b`, in Rhino 8.25.25314.11001: all 12 specs of `scripts/rhino-smoke` passed, every *Validate* True (`any-preset-and-previews` 17, `bar-typologies` 128, `convert-idf` 32, `enclosed-court` 49, `examples` 19, `hub-arms` 324, `linear-and-aggregators` 20, `non-rectangular` 146, `office-cafeteria` 98, `operating-suite-court-cluster` 162, `stepped-band` 83; `orientation` has none), with no exceptions, no missing components, and no expected error missing. Runtime errors appear only in the error scenarios, including the new one that wires a plan into an aggregator's floors input and requires `Data conversion failed from Plan to Floor`. All 19 example definitions reopen and solve (*Validate* True 19 of 19, 0 errors, 0 warnings). The same run found a freeze: BEMGen's Goo types had no public parameterless constructor, so Grasshopper's `Activator.CreateInstance` calls threw and its `Tracing.Assert` opened a modal dialog on a wire of the wrong type, on the "Data conversion failed" message, and on component help (every version up to `v0.9.1`); fixed in `d8e0650` and `19c8e2b`, and the spec now reads every parameter's type name and fails when an expected error is missing. `scripts/verify.ps1` passed with 0 warnings and `scripts/docs-site/build.ps1` printed `DOCS BUILD PASSED`. Open for a person (D-058): item 4 above (the examples on the canvas and in the viewport, where window fills may show transparency-sorting artefacts), dragging the `.yak` from `scripts/package-yak.ps1` onto Rhino 8, checking that a wrong-type wire shows only the conversion error and no dialog, the toolbar look of the icons, and a first EnergyPlus run once a weather file and outputs are chosen (D-112).

### Conditioned Merge and joined pieces checklist (D-123)

*Conditioned Merge* in *3 Simplify*, and the *Join Pieces* input of both merge simplifiers; the scripted run is `scripts/rhino-smoke/specs/merge-pieces.py`, with the linear plan in `linear-and-aggregators.py`. Use *Dwelling Unit Preset* and *Stair Preset* (Stair Bay Bar, Radial Lobes) and *Mall Preset* and *Retail Preset* (Branching Mall), with nothing connected; of these only the stair preset is unconditioned.

#### Toolbar and icons

- [ ] *3 Simplify* shows *Conditioned Merge* with its 24 × 24 icon (a blue zone with a thermometer beside a white one); no other icon has changed. Record the order of the panel's components as shown: no component sets its place in the panel, so it is Grasshopper's, not BEMGen's.
- [ ] *Semantic Merge* and *Conditioned Merge* have the inputs *Plan*, *Join Pieces* (J, default False), and *Preview Location*, and the output *Floor*. Hovering over *Join Pieces* explains what False and True do.

#### Previews of pieces

1. Wire *Stair Bay Bar* (defaults) into *Semantic Merge* and *Conditioned Merge*, each with *Join Pieces* False and True.
   - [ ] The *Floor* outputs read `Floor (7 zones, SemanticMerge)`, `Floor (2 zones, SemanticMerge)`, `Floor (7 zones, ConditionedMerge)`, and `Floor (2 zones, ConditionedMerge)`.
   - [ ] With *Join Pieces* True the preview shows four separate dwelling blocks and three separate stairs, one solid per piece, in the colours of their space types (*Conditioned Merge*: the conditioned zone takes the dwelling colour, the unconditioned zone the stair colour); no solid spans a stair bay, and there are no seams inside a piece.
   - [ ] Pieces that meet at a corner: *Radial Lobes* with either merge simplifier (*Join Pieces* True gives `DwellingUnit-1` or `Conditioned-1` of the 4 lobes) and *Branching Mall* with *Semantic Merge* (`Retail-1` of the 3 branches). Each lobe or branch is its own solid, and nothing fills the space between them. (*Conditioned Merge* on *Branching Mall* gives one zone of one piece, `Conditioned-1`: the mall and the retail are both conditioned.)
2. Wire three joined *Conditioned Merge* floors of the Stair Bay Bar into *Stack Floors* (Multipliers 1, 3, 1), into *Validate*, and into *Convert2BEM*.
   - [ ] *Validate* Passed = True; the preview shows every storey's pieces as separate solids at their storey heights.
   - [ ] *Convert2BEM* *Zones* has one branch per zone with one closed Brep per piece (4 for `L0/Conditioned-1`, 3 for `L0/Unconditioned-1`), and *Names* the matching zone IDs.
3. Through *Single Zone per Floor Type* and *Single Zone Building* instead:
   - [ ] The preview shows each zone as one volume through its storeys, as before.

#### Result (D-123)

Run headless (D-111) on 2026-10-06 on `feature/conditioned-merge` at `09bd3a9`, in Rhino 8.25.25314.11001: all 14 specs of `scripts/rhino-smoke` passed, every *Validate* True (`any-preset-and-previews` 17, `bar-typologies` 128, `convert-idf` 32, `enclosed-court` 49, `examples` 19, `hub-arms` 324, `linear-and-aggregators` 32, `merge-pieces` 16, `non-rectangular` 146, `office-cafeteria` 98, `operating-suite-court-cluster` 162, `stepped-band` 83; `enum-inputs` and `orientation` have none), with no exceptions, no missing components, no expected error missing, and no failed check. Runtime errors appear only in the error scenarios, including the new one that wires a plan into *Join Pieces* and requires `Data conversion failed from Plan to Boolean`. *Conditioned Merge* registered in *3 Simplify* (primary, nickname `Z1c`) with a 24 × 24 icon. The Stair Bay Bar floors read as in item 1 above, and the joined *Conditioned Merge* floors through *Stack Floors* (1, 3, 1) give `L0/Conditioned-1` of 4 pieces and `L0/Unconditioned-1` of 3 on each of the 5 storeys, with 35 closed Breps in the preview and in *Convert2BEM* and 10 `Zone` objects in the IDF. The first run found that the preview united the pieces of a zone on one storey, which fused the corner-touching pieces of joined Radial Lobes and Branching Mall floors into one solid (2 Breps for 5 and for 4 pieces); fixed in `7305504`, so pieces on one storey are never united. It also found that the five examples using *Semantic Merge* (`court-cluster`, `foyer-halls`, `radial-lobes`, `stair-bay-bar`, `terrace-row`) reopened with no output and no message, because the saved *Preview Location* was read into the new *Join Pieces* input; fixed in `f5deacc`, and the `examples` spec now fails when a *Validate* gives no item. After review, at `168f583`: `merge-pieces` (16 *Validate* True, 130 checks) and `examples` (19 *Validate* True, 38 checks) passed again. *Join Pieces* had shown only its name as its tooltip, because its description was read before it was set; fixed in `168f583` and now checked. A definition saved with that description keeps it on reopen, because Grasshopper restores a parameter's description from the file; only files saved with this branch's builds before `168f583` have it. `merge-pieces` also reopens `scripts/rhino-smoke/fixtures/semantic-merge-before-join-pieces.gh`, saved by the plugin of `af9ac65` with a vector wired into *Preview Location*, so the reading of older definitions stays tested after the examples are rebuilt. Open for a person (D-058): the order of the components in *3 Simplify* as shown, the look of *Conditioned Merge* and its icon, and the look of the piece previews in the viewport.

### Program mix checklist — mixed presets and building infiltration (D-124)

*Mix Programs* and the infiltration inputs of *Envelope Preset* and outputs of *Convert2BEM*; the scripted run is `scripts/rhino-smoke/specs/program-mix.py`. Since D-124 the default preset components have no *Infiltration* and *Infiltration Schedule* inputs, so the input lists of the *Dwelling Unit*, *Corridor*, *Stair*, and *Kitchen Preset* items in the S7 and S8 checklists above end before them.

1. Find *Mix Programs* in *1 Program* (a pie of shares, orange) and place it.
   - [ ] Inputs, in order: *Presets* (list), *Weights* (list), *Name*, *Space Type* (right-click lists the space types; no default), *WWR*; one output, *Preset*. The description states the rules: floor-area shares normalised to 1, densities and air changes weighted, per-person loads weighted by occupants, absolute loads added raw, setpoints over the conditioned presets, that absolute occupancy in any preset beside a per-person load in any preset is an error (give occupancy per floor area), and the space-type and WWR defaults.
   - [ ] *Office Preset* and *Core Preset* into *Presets*, *Weights* `1, 1`: the output reads `Preset Mix of Example Office 0.5, Example Core 0.5 (Office, WWR 0.2)`; through *Office Plate*'s *Office* input, a simplifier, an aggregator, and *Validate*, Passed is True, and *Convert2IDF*'s IDF header records `MixPrograms Input.1=Example Office; weight 1; normalised 0.5`.
   - [ ] *Weights* `1, 0` and *Weights* `1, 2, 3` each give an error and no output; so does a preset with absolute occupancy beside another with a per-person load.
   - [ ] A *Load* with *Type* `Infiltration` or *Basis* `PerExteriorWallArea` (typed, or from a definition saved before D-124) gives the error `infiltration is not a program load: set it on the Envelope Preset.`
2. Place *Envelope Preset* with nothing connected.
   - [ ] It has the new inputs *Infiltration Rate* (0.3), *Infiltration Basis* (`AirChangesPerHour`; right-click lists the three bases), and *Infiltration Schedule* (optional); the output ends `infiltration 0.3 AirChangesPerHour)`. A negative rate gives an error.
3. Wire *Envelope Preset* into *Convert2BEM* and *Convert2IDF* after *Office Plate* → *Single Zone per Floor* → *Stack Floors* (Multipliers 2).
   - [ ] *Convert2BEM* has four new outputs after *Window Constructions*: *Infiltration Rate*, *Infiltration Basis*, *Infiltration Schedule* (8760 values), and *Infiltration Flows* (one value per zone branch, m³/h); *Provenance* has an `INFILTRATION:` line.
   - [ ] With each basis, the IDF has one `ZoneInfiltration:DesignFlowRate` per zone with the method `AirChanges/Hour`, `Flow/ExteriorArea`, or `Flow/ExteriorWallArea`, and *Infiltration Flows* gives the lower zone (walls only) less flow than the roof zone for `PerExteriorSurfaceArea`, the same for `PerExteriorWallArea`.
4. For a person in Rhino 8:
   - [ ] The *Mix Programs* icon on the toolbar and the canvas, and the input layout of *Envelope Preset* and *Convert2BEM* on the canvas.
   - [ ] Open two rebuilt examples from `examples/` in the Grasshopper editor: they open without the *Grasshopper IO* message and solve.

#### Result (program mix)

Run headless (D-111) on 2026-10-07 on `feature/program-mix` at `e3fad38`, in Rhino 8.25.25314.11001: all 14 specs of `scripts/rhino-smoke` passed, every *Validate* True (`any-preset-and-previews` 17, `bar-typologies` 128, `convert-idf` 32, `enclosed-court` 49, `examples` 19, `hub-arms` 324, `linear-and-aggregators` 20, `non-rectangular` 146, `office-cafeteria` 98, `operating-suite-court-cluster` 162, `program-mix` 4, `stepped-band` 83; `orientation` and `enum-inputs` have none), no exceptions, no missing components, no expected error missing, and no failed check (`enum-inputs` 245 ok, now with *Infiltration Basis* and the *Mix Programs* *Space Type*; `program-mix` 64 ok). Runtime errors appear only in the error scenarios. `program-mix`: the two-preset mix (weights 3 and 1) matched the hand values for lighting 9 W/m², occupancy 0.0875 people/m², ventilation 33.43 m³/h per person (occupant-weighted), and hot water 5 m³/h absolute (2 + 3, unweighted), and their schedules at hour 0; the three-preset mix the given space type and WWR, setpoints 21/24 °C over the conditioned inputs, and the remark naming the unconditioned stair; a weight tie with an any-program first input gave an any-program mix. The mixed preset through *Office Plate*, *Semantic Merge*, and *Stacked Floor Zone Multiplier* validated, and its IDF records `MixPrograms` in the header and has one `ZoneInfiltration:DesignFlowRate` per zone (6 of 6) at 0.3 air changes per hour. For each infiltration basis the IDF method and rate were right, and *Convert2BEM*'s *Infiltration Flows* equalled the rate times the zones' Rhino volumes, outdoor surface areas (walls and roof; the ground floor not counted), or outdoor wall areas. The 19 example definitions, saved before D-124, opened only after Grasshopper's *Grasshopper IO* message about the preset components' removed inputs, which blocks a headless run, so they were rebuilt with `BEMGEN_EXAMPLES_WRITE=1`; the rebuilt files reopen without it and solve, each with one *Validate* True. Open for a person (D-058): item 4 above.

Rerun after the review fixes, on 2026-10-07 at `0e2a343` (same Rhino): all 14 specs passed again with the same *Validate* counts, no exceptions, no missing components, no expected error missing, and no failed check (`enum-inputs` 245 ok, its *Mix Programs* case now starting from `Mixed`, not the fallback; `program-mix` 17 scenarios, 76 ok). The new error scenarios gave the expected messages: absolute occupancy in *Hall* beside the per-person load of *P1* (`A mix cannot hold a per-person load and absolute occupancy: 'P1' has a per-person load and 'Hall' has absolute occupancy. …`), and a *Load* of *Type* `Infiltration` or *Basis* `perexteriorwallarea` (`… infiltration is not a program load: set it on the Envelope Preset.`). For every basis *Convert2BEM*'s `INFILTRATION:` line equalled the IDF header's (for example `0.3 AirChangesPerHour (EnergyPlus AirChanges/Hour), schedule Example Always On`), the document was in metres, and every zone's volume or outdoor area was positive before its flow was compared.

### Program JSON checklist — program presets from program JSON 2.0.0 (D-126)

*Program JSON* in *1 Program*, the appended inputs of *Load*, *Program Preset*, and the default preset components, and the appended outputs of *Convert2BEM*; the scripted run is `scripts/rhino-smoke/specs/program-json.py`, with the reopened definitions in `examples.py`. The example is `examples/program-json-office.gh`, which holds the Medium Office program JSON in a panel.

#### Toolbar and icons

- [ ] *1 Program* shows *Program JSON* (nickname `PJson`) with its 24 × 24 icon; no other icon has changed.
- [ ] Inputs, in order: *JSON*, *Name*, *Space Type* (right-click lists the space types; unset gives an any-program preset), *WWR* (0.4), *Year* (2007), *Holidays* (list), *Loads* (list), *Heating On*, *Cooling On*, *Heating Setpoint*, *Cooling Setpoint*, *Activity*, *People Radiant*, *People Sensible*; outputs *Preset*, *Source*, *Assumptions*, *Overrides*, *Left Out*. The description says that only the defaulted export is read, that no file or network is read, and that shared services are left out.

#### The example

1. Open `examples/program-json-office.gh` in the Grasshopper editor.
   - [ ] It opens without the *Grasshopper IO* message and solves with no warning or error; *Validate* Passed = True.
   - [ ] The panel holds the JSON; *Program JSON* outputs a preset named `WholeBuilding - Md Office_MediumOffice` for the space type Office; *Assumptions* lists the 22 substitutions of the JSON and *Left Out* the 7 design-day lines; *Source* shows `Json.Sha256 97399216…` and `DefaultPolicy atlas-program-defaults-1.0.0; 22 substitutions`.
   - [ ] The layout of the definition is readable (groups, scribbles, wires), like the other examples.

#### Overrides and errors

2. With the Medium Office JSON in a panel:
   - [ ] *WWR* 0.3, *Year* 2014, and *Holidays* `07-04`, `12-25` appear in *Source* (`WindowToWallRatio 0.3 (given)`, `Calendar 2014 (1 January a Wednesday), holidays 07-04, 12-25`); *Heating On* false gives the *Overrides* line `Heating On: off in place of on`; a *Load* of *Type* `Ventilation` is added and appears in *Overrides*.
   - [ ] *Year* 2016 (a leap year), a holiday `7-4`, JSON text with `"export_mode": "raw"` (the message asks for the defaulted form), text that is not JSON, and a heating setpoint above the cooling setpoint each give an error and no preset.
3. Place *Load* with *Type* `Lighting`, *End Use* `additional_lighting`, *Radiant* 0.6, and *Visible* 0.1.
   - [ ] It outputs a load whose description names the end use; *Latent* 0.2 on a lighting load gives an error (the lights object has no latent fraction).
4. Place *Program Preset* (Office) with only *Heating* connected.
   - [ ] It gives a preset that is heated only, with a remark that cooling is off; *Activity*, *People Radiant*, and *People Sensible* (`0.6` or `autocalculate`) are accepted.
5. Wire a preset through *Office Plate*, *No Simplification*, and *Stack Floors* into *Convert2BEM* and *Convert2IDF*.
   - [ ] *Convert2BEM* has nine new outputs after *Infiltration Flows*: *Load End Uses*, *Heat Fractions*, *Dwelling Units*, *Activity*, *People Radiant*, *People Sensible*, *Water Target*, *Water Inlet*, and *Calendar*; *Provenance* has a `CALENDAR:` line; a heated-only zone has an empty *Cooling Setpoints* branch.
   - [ ] The IDF has the lights fractions, the people activity schedule and fractions, the water-use temperature schedules, `ThermostatSetpoint:SingleHeating` for the heated-only zone, and the run period of the *Year*.

#### Old definitions and the package

- [ ] A definition saved with 1.1.0 (any example from the 1.1.0 release) opens in the editor without the *Grasshopper IO* message and keeps its wires and values, including the default preset components, *Load*, *Program Preset*, and *Convert2BEM*.
- [ ] From the `.yak` (`scripts/package-yak.ps1`) installed in Rhino 8: *Program JSON* loads and reads the Medium Office JSON (the JSON Schema libraries are next to `BEMGen.gha`).

#### Result (program JSON)

Run headless (D-111) on 2026-10-07 on `feature/program-json`, with the fixes of `608bbdd` and `bcaaa94`, in Rhino 8.25.25314.11001 on .NET 8.0.31: all 16 specs of `scripts/rhino-smoke` ran to the end (DONE True) with no failed check. `program-json` has 16 scenarios and 57 checks: the Medium Office through *Office Plate*, *No Simplification*, *Stack Floors*, *Validate*, *Convert2BEM*, and *Convert2IDF* against hand values (the loads with their end uses and values, the lighting heat fractions, people, hot-water temperatures, setpoints, the calendar 2007, the run period, the IDF lights and water uses); its overrides and errors; *Load*'s end use and heat fractions and their errors; *Program Preset* heated only; and a per-dwelling preset with a default preset with *Cooling On* false through *Convert2BEM*'s appended outputs and the IDF. The `examples` spec reopened 20 of 20 definitions (the 19 earlier ones and `program-json-office.gh`), each with one *Validate* True. The first examples run stalled for about 10 minutes on the *Grasshopper IO* dialog, which Grasshopper opens for every current parameter without a saved chunk, so all 19 definitions saved with 1.1.0 failed to reopen (the appended inputs and outputs); Rhino was ended with `taskkill` under the owner's permission, and `608bbdd` fixed it by setting the appended parameters aside while the saved ones are read; the `examples` spec now reads each archive first and fails, instead of stalling, when Grasshopper reports a message. Two full runs followed. The first had one failed check in `merge-pieces`: definitions saved before infiltration left the programs have trailing *Infiltration* inputs at the positions of the new *Heating On* and *Cooling On* and were read into them; `bcaaa94` fixed it, and the second run had no failed check. `program-json` also ran alone three times while its checks were written. Only `program-json-office.gh` was rebuilt (`BEMGEN_EXAMPLES_WRITE=1` with `BEMGEN_EXAMPLES_ONLY=program-json-office`); the other 19 were reopened, not rebuilt. The items of this checklist for a person (the layout of the example and the icon, a 1.1.0 definition in the editor, and the `.yak` install) are open.

### Simulation-ready IDF checklist — *Convert2IDF* weather and outputs (D-130)

*Convert2IDF* targets EnergyPlus 26.2, gains the appended input *Weather* (`Wthr`), and writes the research outputs, the ground temperatures "indoor minus 2 °C", and the case record ([convert2idf.md](../architecture/convert2idf.md), [the stage note](../plans/2026-10-11-idf-out.md)). The scripted run is `scripts/rhino-smoke/specs/convert-idf.py`, which adds a run with the Chicago weather file (`BEMGEN_EPW`, by default `D:\EnergyPlusV26-2-0\WeatherData\USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw`), one without, and one with a missing file.

1. Wire the linear plan through *No Simplification* and *Stack Floors* into *Convert2IDF*, *Path* a file outside the repository, *Write* true.
   - [ ] *Convert2IDF* shows *Weather* (`Wthr`) as its ninth input, optional; its GUID is unchanged.
   - [ ] Without *Weather*: the remark `No weather file was given …`; the IDF says `EnergyPlus 26.2 input file; no weather file was given …`, has no `Site:Location`, and its header holds `Site weather: none`; *Provenance* holds `WEATHER: none given …` and `GROUND: indoor minus 2 C; 20.5, …`.
   - [ ] With *Weather* the Chicago file: the IDF has `Site:Location` `Chicago Ohare Intl Ap IL USA` at 41.98, −87.92, time zone −6, 201 m, and the header and *Provenance* name the file with its SHA-256.
   - [ ] With *Weather* a missing file: an error naming the file, no IDF text, nothing written.
2. Reopen a definition saved with 1.2.0 that holds *Convert2IDF*.
   - [ ] It opens without the *Grasshopper IO* message, keeps its wires and values, and *Weather* is unset.
3. Run a written IDF in EnergyPlus 26.2 with the Chicago file.
   - [ ] It completes with no severe error, no version warning, and no meter warning.

4. Wire the linear plan (multipliers 1, 2, 1) through *No Simplification* and each floor aggregator into *Convert2BEM* and *Convert2IDF*.
   - [ ] *Convert2BEM* shows *Shading* as its last output. Under *Stacked Floor Zone Multiplier* it holds the outdoor walls of the unmodelled storey L1 at its true height, and *Provenance* holds `SHADING: …`. Under the other aggregators it is empty, with `SHADING: none (every storey is modelled)`.
   - [ ] The IDF of *Stacked Floor Zone Multiplier* holds the same surfaces as `Shading:Building:Detailed`, and its header holds `Shading: …`.
   - [ ] In the viewport the *Shading* surfaces fill the gap between the modelled storeys.

#### Result (simulation-ready IDF)

Run headless (D-111) on 2026-10-11 on `feature/idf-out` at `26644d3`, in Rhino 8: all 16 specs of `scripts/rhino-smoke` ran to the end (DONE True), with no exception, no missing component, no expected error missing, and no failed check.

- **Validate counts, all True:** `any-preset-and-previews` 17, `bar-typologies` 128, `convert-idf` 32, `enclosed-court` 49, `examples` 20, `hub-arms` 324, `linear-and-aggregators` 32, `merge-pieces` 16, `non-rectangular` 146, `office-cafeteria` 98, `operating-suite-court-cluster` 162, `program-json` 4, `program-mix` 4, `stepped-band` 83. `orientation` has none, and `enum-inputs` gave 245 ok, 0 failed.
- **Runtime errors** appear only in the error scenarios.
- **Weather in `convert-idf`:**
  - With the Chicago file the IDF has `Site:Location`, and *Provenance* holds `WEATHER: USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw sha256 c7d4efcf…; Chicago Ohare Intl Ap, IL, USA …` and `GROUND: indoor minus 2 C; 20.5, …`.
  - Without one, the remark `NoWeatherFile` and `Case weather: none`.
  - A missing file gives the error `InvalidWeatherFile`, and nothing is written.
- **Shading in `linear-and-aggregators`:** *Convert2BEM*'s *Shading* holds 20 surfaces under *Stacked Floor Zone Multiplier* and none under the other aggregators.
- **Convex split:** the converted enclosed-court files report non-convex roofs written as convex pieces (`SurfaceSplit`).
- **IDD check:** the 35 IDFs the spec wrote pass the EnergyPlus 26.2.0 IDD check with 0 problems.
- **Saved definitions:** all 20 example definitions, saved with 1.2.0, reopen and solve with *Validate* True and no warning or error, so the appended *Weather* input and *Shading* output keep saved definitions readable.

Open for a person (D-058): items 2 and 4 on the canvas and in the viewport, a 1.2.0 definition in the editor, and the toolbar look.

### Construction JSON checklist — construction sets for *Convert2IDF* (D-137, D-138, D-140, D-142, D-143, D-145)

*Construction JSON* in *1 Program* and the appended *Construction* input of *Convert2IDF*. The scripted run is `scripts/rhino-smoke/specs/construction-json.py`, and the reopened definitions are in `examples.py`. The documents are the pinned packet v7's (D-145), in `tests/Lod.ConstructionJson.Tests/Fixtures/packet/examples/`.

#### Toolbar and icons

- [ ] *1 Program* shows *Construction JSON* (nickname `CJson`) with its 24 × 24 icon, braces around a wall section, and no other icon has changed.
- [ ] Its input is *JSON*; its outputs are *Construction*, *Source*, *Roles*, and *Unused*.
- [ ] *Convert2IDF* has *Construction* after *Weather*, and *Fill From Example* (false) last.

#### In the editor

1. Put `medium-office-2019-3B.unified.json` in a Panel, wire it into *Construction JSON*, and wire *Construction* into *Convert2IDF*'s *Construction*, with a linear plan through *No Simplification* and *Stack Floors*, and a weather file in *Weather*.
   - [ ] *Roles* lists the seven roles and the window; *GroundFloor* is the set's F-factor (`GroundFloor: F-factor 1.26343630645112 W/m-K …; Convert2IDF writes it on GroundFCfactorMethod …`), not `NotApplicable`.
   - [ ] *Unused* lists the doors, skylights, tubular devices, and `InteriorCeiling`, but not *GroundFloor* (D-145).
   - [ ] *Convert2IDF* shows no remark for the ground floor; the IDF has `Construction:FfactorGroundFloor` objects, ground floors on `GroundFCfactorMethod`, and `Site:GroundTemperature:FCfactorMethod`; *Provenance* has `CONSTRUCTION SET:` and `GROUND: FCfactorMethod, monthly mean dry-bulb of …`.
   - [ ] With *Weather* empty, *Convert2IDF* reports `GroundTemperatureWeatherMissing` and writes nothing.
   - [ ] The IDF header has `Construction set:`, `Construction roles:`, and `Added mass:` with its ledger.
2. Repeat with `retained-midrise-apartment-2019-3B.unified.json`, *Fill From Example* false.
   - [ ] *Convert2IDF* converts with no error and no role taken from the Example.
   - [ ] With *Single Zone Building* instead of *Stack Floors*, the IDF's slab internal masses use the construction ending in ` Half`.
   - [ ] With `retained-residential-apartment-unit-1990s-4A.unified.json`, *Construction JSON* reports that a single-dwelling set is not converted.
3. Connect an *Envelope Preset* to *Envelope* as well.
   - [ ] *Convert2IDF* reports an error asking to connect one.
4. Replace the Panel's text with `medium-office-2019-3B.detailed.json`, about 0.5 MB.
   - [ ] The Panel stays responsive.
   - [ ] *Construction JSON* reads it with a warning, and *Roles* lists each component with its assignments and conditions.
   - [ ] *Convert2IDF* reports that it converts only unified building-scope documents and names the unified document to use.

#### Old definitions and the package

- [ ] A definition saved before *Construction* existed opens without the *Grasshopper IO* message and keeps its wires (also checked headless by `examples`).
- [ ] From the `.yak` (`scripts/package-yak.ps1`) installed in Rhino 8: *Construction JSON* loads and reads the Medium Office document (`Lod.ConstructionJson.dll` is next to `BEMGen.gha`).

#### Result (construction JSON)

Run headless (D-111) on 2026-10-15 on `feature/construction-json`, in Rhino 8: all 17 specs of `scripts/rhino-smoke` ran to the end (DONE True), with no exception, no missing component, no expected error missing, and no failed check.

- **`construction-json`:** 6 scenarios and 12 checks.
  - The Medium Office set through *Convert2IDF* has massless layers, furnishing and floor-distributed masses, and the fixed 0.10922 air changes in every zone. Its header and provenance name the set, and the ground is a remark.
  - The residential set gives warnings for the Example interior wall and floor, and 20 windows with 20 multipliers of 0.8276. Its VT is left to EnergyPlus.
  - The three error scenarios end in their expected errors.
- **`examples`:** reopened 20 of 20 definitions with *Validate* True. All were saved before *Construction* existed.
- **Results:** `D:\BEMGen-smoke\construction-json-all`.

Rerun on 2026-10-15 after C2 and E1 (D-141): all 17 specs ran to the end with no failed check. `construction-json` has 8 scenarios and 22 checks:
- the residential set with and without *Fill From Example*;
- the garage set without fill;
- the detailed document, read with a warning and refused by *Convert2IDF*.

`examples` reopened 20 of 20. Results: `D:\\BEMGen-smoke\\construction-json-c2e1`.

Rerun on 2026-10-16 after D-142 and the per-face slab mass (D-143): all 17 specs ran to the end (DONE True), with no exception, no missing component, no expected error missing, and no failed check. `construction-json` has 7 scenarios and 19 checks:
- the Medium Office set (9 checks, as before);
- the Midrise Apartment set without *Fill From Example* (6 checks): no error, no role from the Example, the header naming the set, furnishing mass, its fixed air changes, and no solar multiplier;
- the single-dwelling apartment-unit set, refused by *Construction JSON*, with no fallback to the Example in *Convert2IDF*;
- the Midrise Apartment's detailed document, read with a warning and refused by *Convert2IDF* (4 checks).

`examples` reopened 20 of 20 with *Validate* True. Results: `D:\\BEMGen-smoke\\d143-all`.

Checked by a person on 2026-10-16: the owner tested the construction JSON components in Grasshopper and Rhino 8 after D-142 and D-143 and reported that they look right. The items were not ticked one by one.

Rerun headless on 2026-10-18 after packet v7 and the native ground (D-145, D-146) on `claude/bemgen-construction-v7-update-bd63b1`: all 17 specs ran to the end and passed. `construction-json` has 23 checks, all ok; they include the office's F-factor ground floors on `GroundFCfactorMethod`, the Chicago ground temperatures, the *Roles* line for the ground floor, and the error for an F-factor set without *Weather*. Results: `D:\BEMGen-smoke\foundation-v7-rhino-2`. Not yet checked by a person in Grasshopper and Rhino 8.

### Glazing per orientation and skylights checklist (DOE geometry P0b)

The appended glazing inputs of the default preset components, *Program Preset*, and *Program JSON*, and skylights in *Convert2BEM*, the previews, and *Convert2IDF* ([design note](../plans/2026-10-25-doe-geometry-generators.md) S5, S6; [ADR-012](../decisions/ADR-012-centred-windows.md#skylights-doe-geometry-p0b)). No component is added or removed and no GUID or icon changes. The scripted run is `scripts/rhino-smoke/specs/glazing.py`; `examples.py` reopens the saved definitions.

- [ ] Every default preset component (*Dwelling Unit Preset* … *Service Preset*), *Program Preset*, and *Program JSON* end with *WWR North*, *WWR East*, *WWR South*, *WWR West* (WWRN … WWRW, optional) and *Skylight Ratio* (SR; 0 on the default presets, unset on the other two); the earlier inputs keep their order and defaults.
- [ ] *Office Preset* with *WWR North* 0.1 and *Skylight Ratio* 0.05 shows `Preset Example Office (Office, WWR N 0.1, E 0.4, S 0.4, W 0.4, skylight ratio 0.05)`; with nothing connected it shows `(Office, WWR 0.4)` as before.
- [ ] Through *Office Plate*, *No Simplification*, and *Stack Floors* (multiplier 3), the viewport preview shows one blue skylight on the top roof of the office ring and none on the lower ceilings; *Convert2BEM*'s *Windows* holds it after the zone's wall windows, facing up, with the window construction in *Window Constructions*; *Validate* passes.
- [ ] *Convert2IDF* writes the skylight as a `FenestrationSurface:Detailed` of type `Window` named `…/Sky1` in a roof piece; EnergyPlus runs the file without a severe error.
- [ ] *Skylight Ratio* 1 and *WWR East* 1.5 each give an error naming the ratio.
- [ ] A definition saved before this stage (any example) opens without the *Grasshopper IO* message and keeps its wires and values.

#### Result (glazing and skylights)

Run headless (D-111) on 2026-10-25 on `feature/doe-geom-p0b`: all 18 specs of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check, on the working tree of `248ae2f` before the edge-midpoint grid of `dc2c285`; `glazing` ran again alone on `248ae2f` itself with the same result. `glazing` has 6 scenarios and 10 checks: the appended inputs of *Office Preset*, *Program Preset*, and *Program JSON*; the skylit *Office Plate* (ratios and skylight ratio on the preset, *Validate* True, one skylight facing up in *Convert2BEM*'s *Windows* with its window construction, one `Window` in a roof in the IDF); *Program JSON*'s glazing and its provenance; and the two expected errors. `examples` reopened 20 of 20 definitions with *Validate* True. The items for a person (the viewport preview, an EnergyPlus run of a skylit IDF, the editor) are open.

Rerun headless on 2026-10-25 on `9b2b28e`, after review round 1 (equal orientation inputs, court cuts along either axis): all 18 specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; the runtime errors are those of the expected-error scenarios, as before. `glazing` has 7 scenarios and 11 checks, the new one being four orientation inputs at 0.2 beside *WWR* 0.4, which give a preset of WWR 0.2. `examples` reopened 20 of 20 with *Validate* True.

Rerun headless on 2026-10-25 on `5cd2cc5`, after the merge of `feature/doe-geom` (P0a) and the T4 harness: all 18 specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; the runtime errors are those of the expected-error scenarios, the same as on `9b2b28e`. `glazing` 7 scenarios and 11 checks, `program-json` 57 checks, `program-mix` 76, `enum-inputs` 245, all ok; `examples` reopened 20 of 20 with *Validate* True. Review round 2 changed no component, so the run was not repeated.

### DOE offices checklist (DOE geometry P1)

*DOE Program Map* and the three DOE office components, the first DOE generators ([doe-components.md](../architecture/doe-components.md),
[doe-ring-office.md](../architecture/doe-ring-office.md)). Four components and one parameter are added; no existing GUID, input, or icon changes.
The scripted run is `scripts/rhino-smoke/specs/doe-offices.py`.

- [ ] *2 Generate* shows a group of its own after the precedent generators with *DOE Small Office*, *DOE Medium Office*, and *DOE Large Office*; *1 Program* shows *DOE Program Map*; each has its own icon.
- [ ] Each office's inputs, in order: Storeys, Plate Length, Plate Depth, Perimeter Depth, Corridor Width, Floor Height, Orientation (with its record's defaults), Program Map, Preview Location; outputs *Plan* (list), *Multipliers* (list), *Program Keys* (list).
- [ ] An office without a *Program Map* lists its keys in *Program Keys* (9 small, 11 medium, 13 large) and shows the error asking for a map of that many keys.
- [ ] An office whose *Plate Length* is wired to a source without data still lists its keys and names *Plate Length* in an error.
- [ ] *Program Keys* of one office copy into *DOE Program Map*'s *Keys*, with one *Any Program Preset* (an *Office Preset*) in *Presets*, give a map that, on a second copy of the office, gives its plans; the viewport shows the medium office's three storeys and the large office's ground, middle, and top plans at 0, 3.96, and 43.60 m.
- [ ] *Plan* through *No Simplification* into *Stack Floors*, with *Multipliers* wired into *Multipliers*, gives the whole building (the large office's twelve storeys); *Validate* passes.
- [ ] *Stacked Floor Zone Multiplier* with the same wiring draws the large office's middle floor once (storey 6, D-045) and its nine other storeys as unmodelled grey.
- [ ] *Plate Length* 15 on the small office, *Storeys* 2 on the large office, a map without a key the plans need, and a map with a repeated key each give an error naming the cause.

#### Result (DOE offices)

Run headless (D-111) on 2026-10-26 on `36a61d8` of `feature/doe-geom-p1`, after review round 1 and the merge of `feature/doe-geom` (P5a): all 19
specs of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check;
no *Validate* output was False. `doe-offices` has 16 scenarios, 83 *Validate* outputs True, and 14 checks: the large office's three plans,
multipliers 1, 10, 1, its 13 keys, storey elevations 0, 3.9632, and 43.5952 m, the 312 zones of *Stack Floors*, the middle plan at 19.816 m on
storey 5, the zone multiplier's storeys 0, 6, and 11; *Validate* True on all 16 buildings of each of the five simplifier × aggregator matrices
(small, medium, large, medium at 30°, large with six storeys); and an office whose *Plate Length* is wired to a source without data still listing
its 9 keys. Its 20 runtime errors are those of the expected-error scenarios and of the first office copy that lists the keys without a map. `examples`
reopened 20 of 20 definitions with *Validate* True. The items for a person (the toolbar group and icons, the previews in the viewport) are open.

### DOE schools checklist (DOE geometry P3)

*DOE Primary School* and *DOE Secondary School* ([doe-school.md](../architecture/doe-school.md), [doe-components.md](../architecture/doe-components.md)).
Two components are added; no existing GUID, input, or icon changes. The scripted run is `scripts/rhino-smoke/specs/doe-schools.py`.

- [ ] *2 Generate*'s DOE group shows *DOE Primary School* and *DOE Secondary School* beside the offices; each has its own icon.
- [ ] Each school's inputs, in order: Wing Count, Length, Corridor Width, Classroom Depth, Floor Height, Orientation (with its record's defaults: 3, 104 or 141, 3 or 5, 9, 4, 0), Program Map, Preview Location; outputs *Plan* (list), *Multipliers* (list), *Program Keys* (list).
- [ ] A school without a *Program Map* lists its keys in *Program Keys* (9 primary, 12 secondary) and shows the error asking for a map of that many keys.
- [ ] *Program Keys* of one school copy into *DOE Program Map*'s *Keys*, with one *Any Program Preset* in *Presets*, give a map that, on a second copy, gives its plans; the viewport shows the primary school's three wings west of the spine and the secondary school's first floor over its ground storey at 4 m.
- [ ] *Wing Count* 6 gives six wings, the main corridor running past every middle wing.
- [ ] *Plan* through *No Simplification* into *Stack Floors*, with *Multipliers* wired, gives the building; *Validate* passes.
- [ ] *Wing Count* 1, *Corridor Width* 0.4, and *Classroom Depth* 1.9 each give an error naming the cause; *Perimeter Core* at 4.57 m on the secondary school is `PlanTooNarrow`, at 4 m it passes.

#### Result (DOE schools)

Run headless (D-111) on 2026-10-26 on `6598d84` of `feature/doe-geom-p3`, after the merge of `feature/doe-geom` (P1): all 20 specs of
`scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no
*Validate* output was False. `doe-schools` has 13 scenarios, 66 *Validate* outputs True, and 18 checks: the primary school's one plan of 25 zones,
6871 m², multiplier 1, and 9 keys in ordinal order; at six wings 40 zones, the main corridor to 144 m, and five `_Wing5` copies; the secondary
school's plans of 25 and 21 zones, multipliers 1, 1, 12 keys, storey elevations 0 and 4 m, 46 zones in *Stack Floors*, the gym one 4 m storey
high, and *Validate* True; *Validate* True on all 16 buildings of each of the four simplifier × aggregator matrices (primary, secondary with
*Perimeter Core* at 4 m, primary at 30°, secondary with six wings). Its 18 runtime errors are those of the expected-error scenarios (one wing, a
0.4 m corridor, a 1.9 m classroom row, *Perimeter Core* at 4.57 m on the secondary school) and of the first school copies that list the keys
without a map. `doe-offices` was unchanged (16 scenarios, 83 *Validate* True, 14 checks ok); `examples` reopened 20 of 20 definitions with
*Validate* True. The items for a person (the toolbar group and icons, the previews in the viewport) are open.

### DOE multiplied-room checklist (DOE geometry P5b)

*DOE Large Hotel* and *DOE Hospital*, the DOE generators of multiplied rooms ([doe-components.md](../architecture/doe-components.md),
[doe-tower-hotel.md](../architecture/doe-tower-hotel.md), [doe-hospital.md](../architecture/doe-hospital.md)). Two components are added; no
existing GUID, input, or icon changes. The scripted run is `scripts/rhino-smoke/specs/doe-multiplied-rooms.py`.

- [ ] *2 Generate*'s DOE group shows *DOE Large Hotel* and *DOE Hospital*, each with its own icon.
- [ ] *DOE Large Hotel*'s inputs, in order: Storeys, Guest Rooms Per Row, Length, Depth, Floor Height, Orientation, Program Map, Preview Location; *DOE Hospital*'s: Room Multipliers (17 values, the description naming each room by index), Plate Length, Plate Depth, Corridor Width, Floor Height, Orientation, Program Map, Preview Location; outputs Plan, Multipliers, Program Keys.
- [ ] Without a *Program Map* each lists its keys (15 hotel, 18 hospital) and asks for a map of that many keys.
- [ ] *Plan* through *No Simplification* into *Stack Floors* with *Multipliers* wired gives the hotel's six storeys (the typical plan four times) and the hospital's five; the repeated rooms' copy space shows as gaps in the plates; *Validate* passes.
- [ ] *Convert2BEM*'s *Boundaries* list `SelfAdjacent` for the walls toward the copy space, and its *Multipliers* the room multipliers (19 and 9 on *Stack Floors*, 76 on *Stacked Floor Zone Multiplier*).
- [ ] *Perimeter Core*, *Single Zone per Floor*, *Single Zone per Floor Type*, and *Single Zone Building* end with an error saying they do not support multiplied rooms.
- [ ] Two values in *Room Multipliers*, *Corridor Width* 0.4, *Storeys* 2 on the hotel, and *Guest Rooms Per Row* 1 each give an error naming the cause.

#### Result (DOE multiplied rooms)

Run headless (D-111) on 2026-10-26 on `37a3d3e` of `feature/doe-geom-p5b`, after the merge of `feature/doe-geom` (P1): all 20 specs of
`scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no
*Validate* output was False. `doe-multiplied-rooms` has 12 scenarios and 31 checks: the large hotel's three plans, multipliers 1, 4, 1, storey
elevations 0, 3.048, and 15.24 m, room multipliers 9 and 19, its 9,366.457 m² counted zone × multiplier on *Stack Floors* and *Stacked Floor Zone
Multiplier*, the ×76 room on storey 3 of the zone multiplier model, `SelfAdjacent` boundaries (87 of 364) and the room multipliers in *Convert2BEM*,
the same with 38 rooms per row (13,094.590 m², ×152); the hospital's five plans, its 18,682.874 m², `SelfAdjacent` boundaries (214 of 554); and
*Validate* True on all 10 buildings of each supported simplifier × aggregator matrix. Its 25 runtime errors are those of the expected-error
scenarios (the four `NotSupported` steps on each generator, the four parameter errors) and of the first generator copy that lists the keys
without a map. `examples` reopened 20 of 20 definitions with *Validate* True. The items for a person (the toolbar group and icons, the previews in
the viewport) are open.

### DOE outpatient checklist (DOE geometry P6)

*DOE Outpatient*, the DOE generator of the outpatient health-care building ([doe-outpatient.md](../architecture/doe-outpatient.md),
[doe-components.md](../architecture/doe-components.md)). One component is added; no existing GUID, input, or icon changes. The scripted run is
`scripts/rhino-smoke/specs/doe-outpatient.py`.

- [ ] *2 Generate* shows *DOE Outpatient* in the DOE group beside the DOE offices, with its own icon.
- [ ] Its inputs, in order: Plate Length (51.816), Plate Depth (35.3568), Corridor Width (1.8288), Floor Height (3.048), Orientation (0), Program Map, Preview Location; outputs *Plan* (list), *Multipliers* (list), *Program Keys* (list).
- [ ] Without a *Program Map* it lists its 32 keys in *Program Keys* and shows the error asking for a map of 32 keys.
- [ ] With a map built from its keys and one *Any Program Preset*, the viewport shows the three storeys at 0, 3.048, and 6.096 m: the ground storey reaching further north to the north-east stair, and each upper storey with its own copy of the stairs and the lift.
- [ ] *Plan* through *No Simplification* into *Stack Floors*, with *Multipliers* wired, gives 126 zones; *Validate* passes.
- [ ] *Perimeter Core* at its 4.57 m default gives `PlanTooNarrow`; at 1 m it passes.
- [ ] *Plate Length* 30 and *Corridor Width* 0.5 each give an error naming the limit (34.983 m; 0.6 m).

#### Result (DOE outpatient)

Run headless (D-111) on 2026-10-26 on `3adb0de` of `feature/doe-geom-p6` (after the merge of `feature/doe-geom` at `d58c2ff`), with no other Rhino
running: all 20 specs of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and
no failed check; no *Validate* output was False. `doe-outpatient` has 11 scenarios, 49 *Validate* outputs True, and 16 checks: three plans of 59,
41, and 26 zones with outlines of 18, 14, and 14 vertices, multipliers 1, 1, 1, the 32 keys in ordinal order, storey elevations 0, 3.048, and
6.096 m, the 126 zones of *Stack Floors* with 3,914.7483 m², the top storey's `NE_Stair` copy at 6.096 m, *Validate* True; *Validate* True on all
16 buildings of each of the three simplifier × aggregator matrices (canonical and at 30° with *Perimeter Core* at 1 m, the shortest plate
34.9832 × 26.3736 m with *Perimeter Core* at 0.8 m); the shortest plate 34.9832 m long on every storey with all its zones; and an input without
data that still lists the 32 keys. Its 14 runtime errors are those of the expected-error scenarios (*Perimeter Core* at 4.57 m, `PlanTooNarrow`;
*Plate Length* 30, shorter than 34.983 m; *Corridor Width* 0.5, the IT hall 0.417 m wide; a map with only `Stair`, `MissingPreset`; an unread
*Plate Length*) and of the first copy that lists the keys without a map. `doe-offices` and `examples` (20 of 20, *Validate* True) passed as before.
The items for a person (the toolbar, the icon, the viewport previews) are open.

### DOE single-storey checklist (DOE geometry P2)

The six components of the single-storey DOE generators ([doe-single-storey.md](../architecture/doe-single-storey.md)), on the DOE component
support of P1 ([doe-components.md](../architecture/doe-components.md)). Six components are added; no existing GUID, input, or icon changes. The
scripted run is `scripts/rhino-smoke/specs/doe-single-storey.py`.

- [ ] *2 Generate*'s DOE group shows *DOE Full-Service Restaurant*, *DOE Quick-Service Restaurant*, *DOE Strip Mall*, *DOE Stand-alone Retail*, *DOE Supermarket*, and *DOE Warehouse*; each has its own icon.
- [ ] Each component's inputs are in the DOE order with its record's defaults (the strip mall's *Store Counts*, *Store Sizes*, and *Store Tenancies* first, as lists), then *Floor Height*, *Orientation*, *Program Map*, *Preview Location*; outputs *Plan*, *Multipliers*, *Program Keys*.
- [ ] Without a *Program Map* each lists its keys (2, 2, 3, 4, 6, 3) and shows the error asking for a map of that many keys.
- [ ] With a map built from its *Program Keys*, each previews its plan in the viewport: the restaurants' dining room south of the kitchen, the strip mall's ten stores, the stand-alone retail's core reaching the entry, the supermarket's back of house along the north and east, the warehouse's office in the south-west corner.
- [ ] The strip mall with *Store Counts* 2, 1, *Store Sizes* Large, Small, and *Store Tenancies* 3, 1 previews two large stores and one small store.
- [ ] *Kitchen Depth* 0.4, a stand-alone retail *Length* of 5, a warehouse *Fine Storage Depth* of 9.5, store lists of different lengths, and a store size Medium each give an error naming the cause.

#### Result (DOE single-storey)

Run headless (D-111) on 2026-10-26 on `378fd5a` of `feature/doe-geom-p2`, after the merge of `feature/doe-geom` at `d58c2ff` (P1): all 20 specs
of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no
*Validate* output was False. `doe-single-storey` has 27 scenarios, 134 *Validate* outputs True, and 41 checks: each of the six records at its
defaults gives one plan with *Multipliers* 1, its program keys in ordinal order, its zones, the source's floor area within 0.1 %, zone parts on the
ground one floor height high, and *Validate* True; strip-mall runs given as lists give `LGstore1`, `LGstore2`, `SMstore1` with their tenancies'
keys on a 38.1 m by 22.86 m plate; and *Validate* True on all 16 buildings of each of the eight simplifier × aggregator matrices (the six
records, the supermarket at 30°, and a strip mall of twelve stores in three runs). Its 37 runtime errors are those of the expected-error
scenarios and of the first copies that list the keys without a map. `doe-offices` 14 checks, `enum-inputs` 245, `glazing` 11, `program-json` 57,
`program-mix` 76, all ok; `examples` reopened 20 of 20 definitions with *Validate* True. The items for a person (the toolbar group and icons, the
previews in the viewport) are open.

Rerun headless on 2026-10-26 on `c06d5a3`, after the review's low items (a band past its maximum named, store sizes read in any case): all 20
specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was
False. `doe-single-storey` has 28 scenarios (the new one a supermarket *Storage Depth* past its maximum, `StorageDepth 51 m exceeds its maximum
50.7944 m`), 134 *Validate* outputs True, and 41 checks, the strip-mall runs now given as `large` and `SMALL`; its 39 runtime errors are those of
the expected-error scenarios and of the first copies without a map. `examples` reopened 20 of 20 with *Validate* True.

### DOE small hotel checklist (DOE geometry P4)

*DOE Small Hotel*, the corridor hotel generator's component ([doe-corridor-hotel.md](../architecture/doe-corridor-hotel.md)). One component is
added; no existing GUID, input, or icon changes. The scripted run is `scripts/rhino-smoke/specs/doe-hotel.py`.

- [ ] *2 Generate* shows *DOE Small Hotel* in the DOE group with the offices; it has its own icon.
- [ ] Its inputs, in order: Storeys, Guest Room Bays, Length, Room Depth, Corridor Width, Floor Height, Orientation (with the record's defaults), Program Map, Preview Location; outputs *Plan* (list), *Multipliers* (list), *Program Keys* (list).
- [ ] Without a *Program Map* it lists its 14 keys in *Program Keys* and shows the error asking for a map of 14 keys.
- [ ] Its *Program Keys*, copied into *DOE Program Map* with one *Any Program Preset* in *Presets*, give a map that, on a second copy, gives four plans; the viewport shows the four storeys at 0, 2.74, 5.49, and 8.23 m, the ground storey with its own zones.
- [ ] *Plan* through *No Simplification* into *Stack Floors*, with *Multipliers* wired, gives the four-storey hotel; *Validate* passes.
- [ ] *Guest Room Bays* 22 narrows every guest room to 1.98 m and widens the run west of the lift lobby; *Storeys* 6 adds two storeys like the top one.
- [ ] *Length* 20, *Storeys* 1, *Guest Room Bays* 8, and *Corridor Width* 0.4 each give an error naming the cause.

#### Result (DOE small hotel)

Run headless (D-111) on 2026-10-26 on `266c674` of `feature/doe-geom-p4`, after the merge of `feature/doe-geom` (P1, P5a): all 20 specs of
`scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no
*Validate* output was False. `doe-hotel` has 11 scenarios, 49 *Validate* outputs True, and 19 checks: four plans of 19, 16, 16, and 16 zones,
multipliers 1, 1, 1, 1, the 14 keys in ordinal order, storey elevations 0, 2.7432, 5.4864, and 8.2296 m and every storey 2.7432 m high (G5), the
source's 3.9624 m bay, the 67 zones and 4,013.587 m² of *Stack Floors*; at six storeys and 22 bays, `Corridor_Flr5` and `GuestRoom401_Flr5` on
floor 5, every bay 1.9812 m, `GuestRoom220_223` 15 bays, and the front stairs 2.4384 m; *Validate* True on all 16 buildings of each of the three
simplifier × aggregator matrices (canonical, at 30°, eight storeys and 22 bays); and the hotel with *Length* wired to a source without data still
listing its 14 keys. Its 15 runtime errors are those of the five expected-error scenarios, of the two scenarios without a map, and of the eight
first hotel copies that list the keys without a map; its one warning is the empty *DOE Program Map* of the unread-input scenario. `doe-offices`
(83 *Validate* True, 14 checks) is unchanged, and `examples` reopened 20 of 20 definitions with *Validate* True. Results:
`D:\BEMGen-smoke\p4-all-1`. The items for a person (the toolbar group and the icon, the previews in the viewport) are open.

### DOE program presets checklist (DOE geometry P7)

The fifteen *DOE … Programs* components ([doe-components.md](../architecture/doe-components.md#doe-program-presets)), one per DOE
generator, in their own group of panel *1 Program Presets*. Fifteen components and icons are added; no existing GUID, input, or icon changes. The
scripted run is `scripts/rhino-smoke/specs/doe-presets.py`.

- [ ] *1 Program Presets* shows the fifteen *DOE … Programs* components in a group after the built-in presets; each icon is its generator's motif in orange, smaller, with a preset tag in the bottom-left corner.
- [ ] Each has no input and the outputs *Program Map*, *Keys*, *Presets*; it shows the remark that the loads are illustrative and the glazing is the DOE reference's for each key's zones, and, where keys take the Service fallback or are under a gap, a remark naming them.
- [ ] *Program Map* wired into the matching DOE generator's *Program Map* gives its plans at the defaults; the viewport shows the windows on the façades.
- [ ] *Keys* and *Presets* wired into *DOE Program Map*, one preset replaced by another, give a map the generator takes.

#### Result (DOE program presets)

Run headless (D-111) on 2026-10-26 on `8e0c491` of `feature/doe-geom-p7` (the plugin sources are those of the final commit; the commits after it change documents only), with no other Rhino running at its start: all 25 specs of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was False. `doe-presets` has 17 scenarios, 16 *Validate* outputs True, no runtime error or warning, and 75 checks, five per record: *Keys* equal to the generator's *Program Keys*, one preset per key named by it, the keys that take the Service fallback with their remark, *Validate* True, and the stacked window area per orientation and skylight area equal to the figures `DoeProgramPresetsTests` pins; the supermarket's presets rebuilt by *DOE Program Map* validate. The fifteen components register in *1 Program Presets* (secondary exposure), each with a 24 × 24 icon. The items for a person (the toolbar group and icons as drawn, the windows in the viewport) are open.
Rerun headless on 2026-10-26 on `305e4dd`, after the review's fixes (the keys under a gap keep the source's glazing and are named in a third remark, the edited-preset scenario moved into the checks): all 25 specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was False. `doe-presets` has 16 scenarios, 15 *Validate* outputs True, no runtime error or warning, and 93 checks: six per record (the five above and the keys under a gap with their remark: the warehouse's `Fine` and `Office`, the secondary school's `Auditorium`, `Gym`, and `Gym - audience`, the outpatient's `Stair`), and three on the supermarket's *Sales* preset replaced by the *Office Preset* as an any-program preset and rebuilt with *DOE Program Map* (the map's *Sales* preset is the replacement, every other key keeps its shipped preset, and *Validate* is True).
Rerun headless on 2026-10-26 on `f74e867`, after the re-review's fixes (each record's gap change described in its own terms in the remark and the provenance, the record's glazing compared exactly, the loader checking that every zone of a `gap_source_wall` key is under a gap), with no other Rhino running: all 25 specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was False. `doe-presets` passed its 93 checks, and the warehouse's remark names its keys under a gap with the office drawn to the 8.534 m storey height.

### DOE close-out checklist (DOE geometry stage C)

The icons of the 15 DOE generator components, *DOE Program Map*, and the parameter *Program Map* ([doe-components.md](../architecture/doe-components.md#icons)),
and the one message change of the close-out: a length shorter than the shortest valid one on an axis without a fixed interval no longer names "the 0 m of
fixed intervals". No component, input, output, or GUID changes.

- [ ] *2 Generate*'s DOE group shows 15 generators, each with its own 24 × 24 icon in the green accent, distinct from one another and from the six precedent non-residential generators: the three offices (a ring plan on one plate, on three, on a tall stack with a cross), the two restaurants (a square split by one line, a plate; a smaller square split in half, a cup), the strip mall (a bar of wide and narrow cells), the stand-alone retail (a box with a notch in its front), the supermarket (an L-shaped band), the warehouse (a tall box with a corner office), the two schools (wings joined by a spine, the second with a second storey outline), the small hotel (a bar with a corridor and a stack mark), the large hotel (a tower on a podium, dashed copies), the hospital (a plate with a cross of corridors, dashed copies), and the outpatient (a stepped block with a stair shaft and a cross).
- [ ] *1 Program* shows *DOE Program Map* with its orange icon (a key list with arrows to swatches); a *Program Map* parameter shows its hexagon with a key tag joined to a swatch.
- [ ] The icons stay legible at the toolbar size on the light and the dark canvas.
- [ ] *DOE Warehouse* with *Length* 1.99 gives an error ending "shortest valid 2 m: every flexible interval at 1 m, or at its own length under 1 m (S3)."

#### Result (DOE close-out)

Run headless (D-111) on 2026-10-26 on `4f4be06` of `feature/doe-geom-c` (the plugin sources are those of the final commit; the commits after it change documents only), with no other Rhino running: all 24 specs of `scripts/rhino-smoke` ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was False, and no registered component reported another icon size than 24 × 24. The metadata dump (`scripts/docs-export/component-metadata.py`, run headless alone) lists 85 objects, the 15 DOE generators, *DOE Program Map*, and *Program Map* each with its own icon file, and no `Gap:` line. The items for a person (the toolbar group and icons as drawn, the previews in the viewport) are open.

Rerun headless on 2026-10-26 on `6d4e331`, after the close-out review's three fixes (the *DOE Program Map* row of the pipeline document, the decision number dropped from the DOE generators' description text, the medium and large office icons redrawn as offset square plates): all 24 specs ran to the end (DONE True) with no exception, no missing component, no expected error missing, and no failed check; no *Validate* output was False, and no registered component reported another icon size than 24 × 24. The metadata dump again lists 85 objects and no `Gap:` line, and none of its descriptions cites a decision or an ADR number.

### Atlas release 2.0.0 checklist — program JSON 5.4.0, constructions 4.3.0 / 3.1.0 (D-172)

*Program JSON* reads program JSON 5.4.0 (versions `filled` and `source`) and *Construction JSON* the release 2.0.0 constructions. The scripted runs are `program-json.py`, `glazing.py`, and `construction-json.py` on the fixtures in `tests/Lod.ProgramJson.Tests/Fixtures/atlas/` and `tests/Lod.ConstructionJson.Tests/Fixtures/atlas-2.0.0/examples/`; [the design note](../plans/2026-10-28-atlas-release-2-0-0.md) has the rest.

- [ ] *Program JSON* shows *Climate Zone* (CZ) and *Context* (Ctx) after *Skylight Ratio*; *WWR* has no default value on a newly placed component; the description names program JSON 5.4.0. A definition saved before D-172 opens with the two new inputs unset and its saved *WWR* kept.
- [x] `examples/program-json-office.gh` is rebuilt with `medium-office-90-1-2019.filled.json` in its panel (headless, D-175) and solves with *Validate* True; *Assumptions* lists 3 resolutions and *Source* shows `Json.Version program JSON 5.4.0, filled` and the `Daylighting` line.
- [ ] `small-office-iecc-2021.source.json` with *Climate Zone* `1B` gives lighting 6.77084 W/m² and no climate warning; without it, 6.093756 W/m² and the warning `ProgramJsonClimateZoneNotGiven`; the source version's unrecorded people fractions warn.
- [ ] `multifamily-iecc-2021.source.json` without *Context* is the error naming `foundation`; with `foundation=slab` it solves, and *Left Out* lists the exterior lights, the shared services, and the loads of the other foundations.
- [ ] *Convert2IDF* of the medium office preset writes one `Site:WaterMainsTemperature` and no daylighting object; its header says `Daylighting: never written (D-174)` with the number of zones whose programs have controls.
- [ ] *Construction JSON* on `medium-office-2019-5B.detailed.json` lists the two *Alternates* lines in *Roles*; the unified document of the same context converts as before; `medium-office-iecc-2021-5B.unified.json` is read with only the warning `ConstructionJsonInfiltrationMethodNotSupported` (no schema error, D-173), and *Convert2IDF* does not convert its set because of the source design-flow infiltration.
