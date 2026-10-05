# Enum inputs with a right-click menu and a dropdown on extraction (design note)

> **Status:** Done (D-120) · **Date:** 2026-10-04 · **Decisions:** D-064, D-111, D-120 · **Branch:** `features/dropdown-enums`

A Grasshopper revision after v1.0.1, run as D-111 sets out: built once, test-first, on a feature branch in a worktree; reviewed by a second agent; `scripts/verify.ps1` before the merge; the headless Rhino check once; recorded in one decision-log entry.

## Problem

Five component inputs take the name of an enum as text: *Schedule* *Kind* (`ScheduleKind`) and *First Day* (`DayOfWeek`), *Load* *Type* (`LoadType`) and *Basis* (`LoadBasis`), and *Program Preset* *Space Type* (`SpaceType`). Today a user types the name into a panel or the parameter's *Set Text* box, and only the input description lists the valid names. The owner asked for two ways to choose a value instead:

1. **Extract parameter** on such an input places a dropdown, Grasshopper's *Value List* in dropdown mode, holding every value of the enum and wired into the input.
2. **Right-click** on the input lists the enum's values as menu items next to Grasshopper's own items. Clicking one sets it as the input's value, and the current value is ticked.

## Design

- **`EnumParameter<TEnum>`** (`src/Lod.Grasshopper/Parameters/EnumParameter.cs`), an internal sealed generic subclass of Grasshopper's `Param_String`:
  - The data stays text (`GH_String`), so panels, wires, saved definitions, and the existing parsing (`ComponentSupport.TryParse`, case-insensitive, an error listing the valid names) work as before.
  - It is internal and generic, so Grasshopper's component server never registers it (it loads only public, non-generic types with a public parameterless constructor). It keeps the *Text* parameter's `ComponentGuid`, icon, and type name, and needs no GUID or icon of its own.
  - The values offered are `Enum.GetNames(typeof(TEnum))` in declaration order, exactly the names the parser accepts.
- **Right-click menu.** `Menu_AppendManageCollection` is overridden. It appends Grasshopper's *Manage Text collection* item, a separator, and then one item per enum value, so the values sit between *Set Text* / *Set Multiple Text* / *Manage collection* and *Clear values* / *Internalise data* / *Extract parameter*. An item is enabled only when the input has no source, like Grasshopper's own data items. It is ticked when the input's only persistent value names it, ignoring case. A click records an undo event, replaces the persistent data with the name, and recomputes.
- **Extract parameter.** `Menu_AppendExtractParameter` is overridden. The item keeps its name and its enabled state (no source). It places a `GH_ValueList` in `DropDown` mode left of the input, centred on it and moved down past any object it would overlap, labelled with the input's name. The list has one item per enum value (name shown, the quoted name as its expression, so it outputs text). The list selects the input's current persistent value when that names an enum value, otherwise the first value. It is wired into the input, and the addition and the wire are one undo record.
- **Inputs.** The five inputs are registered with `EnumParameter<TEnum>` through one helper, with their current names, nicknames, access, and defaults (`Fraction`, `Monday`). Their descriptions keep the list of names and add how to choose one. No component GUID changes. Saved definitions still load because the input's data type is unchanged; backward compatibility is not required anyway (D-064).
- The Grasshopper project stays a thin adaptor: no domain logic moves, and `Lod.Core` is untouched.

## Tests

`Lod.Grasshopper` has no `dotnet test` project (its types need Rhino), so the behaviour is tested in the headless Rhino check. The new spec `scripts/rhino-smoke/specs/enum-inputs.py` is written first and fails before the build. For each of the five inputs it checks:

- the input is an enum parameter whose menu holds every enum name, ticked for the default where there is one;
- clicking a value sets the persistent data, and the component solves with it (for example, the *Schedule* output's kind);
- *Extract parameter* adds one value list in dropdown mode, wired as the input's only source, with the enum names in order and the expressions as quoted names, selected on the current value;
- selecting another list item changes the component's result;
- an input with a source shows the values disabled.

The existing specs must stay unchanged in their results.

## Documentation

- [pipeline.md](../architecture/pipeline.md): a short note on enum inputs next to the component table.
- [grasshopper-smoke-test.md](../development/grasshopper-smoke-test.md): a manual check of the menu and the dropdown, since the headless check sees no canvas.
- The decision log (D-120), and the `sync-docs` skill at close-out.

## Acceptance criteria

- The new spec passes and every existing spec is unchanged.
- `scripts/verify.ps1` passes.
- No component GUID changes, and no input's name, nickname, access, or default changes.
