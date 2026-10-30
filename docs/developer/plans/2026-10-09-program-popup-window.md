# A JSON editor window on *Program JSON* (design note)

> **Status:** Done (D-128); merged into `main` on 2026-10-30 (D-207). Approved 2026-10-09 (the owner's answers) · **Date:** 2026-10-09 · **Decisions:** D-064, D-111, D-126; new: D-128 · **Branch:** `feature/program-popup-window` (worktree `D:\worktrees\program-popup-window`, from `main` `3e46108`)

A Grasshopper revision after v1.2.0, run as D-111 sets out: this note first; one test-first build on the branch; a review of the diff by a second agent; the headless Rhino check once; `scripts/verify.ps1` before the merge; one decision-log entry. The build stops before the merge, the version, the tag, the push, and the release (the owner, 2026-10-09).

## Problem

*Program JSON* (D-126) takes the program JSON as text on its *JSON* input (J). The text must come from elsewhere in the definition: a *Panel*, a file read by another component, or the parameter's *Set Text* box. An atlas program is long (the Medium Office fixture is about 60 kB), and pasting it into a panel or the *Set Text* box is awkward; a panel also limits how much text it shows and edits comfortably. The owner asked for a more convenient way to give the text, as an addition: every other input and behaviour of the component stays as it is.

## The owner's choices (2026-10-09)

1. **Where the text goes.** OK stores the text as the *JSON* input's own value (its persistent data), exactly as *Set Text* would, so it is saved in the definition. Grasshopper's usual rule applies: a wire into *J* wins over the stored text, and *Clear values* on the input removes it.
2. **The button.** A strip at the bottom of the component, labelled *Edit JSON…*; **double-clicking** it opens the window. Single clicks on it select and drag the component as anywhere else on it.
3. **The window.** One multi-line text field, prefilled with the stored text (empty if there is none), and *OK* and *Cancel*. **OK checks the text first**: if it is invalid, the window stays open and lists the errors; if it is valid, the text is stored and the component re-solves.
4. **Scope.** Build, review, and check; stop before the merge.

## Design

- **The check** is a domain service, so it is tested without Rhino: `ProgramJsonTextCheck.Check(string? text, ProgramJsonOptions? options)` in `Lod.ProgramJson` returns what OK does:
  - **Clear** when the text is empty or only white space: OK removes the stored text (the input then has no value, and the component shows Grasshopper's usual message for a missing input, unless J has a wire);
  - **Store** when `ProgramJsonReader.Read` accepts it (strict parsing, the mode, the schema, the contract's checks, and the expansion of every schedule); its warnings are listed but do not block;
  - **Reject** when the reader returns errors; the messages are the diagnostics as text, one per line (`Error <code> [<JSON Pointer>]: <message>`).

  The stored text is the text exactly as typed or pasted, never trimmed. The SHA-256 in the preset's *Source* is that of the stored text with LF line endings (the owner's decision during the build; see the build log).
- **The calendar of the check.** The expansion's hourly checks depend on the calendar. The check uses the component's *Year* and *Holidays* when each holds one value (or one list) that makes a valid calendar, else 2007 without holidays, the inputs' defaults. The overrides (*Loads*, the controls, the people inputs) are not part of the check: they are checked in the solve, as now, and their errors appear on the component as they do today.
- **Attributes.** `ProgramJsonAttributes`, a `GH_ComponentAttributes` subclass in `src/Lod.Grasshopper/Components/`, used by `ProgramJsonComponent.CreateAttributes`. `Layout` adds a strip of 22 pixels below the component's body and enlarges the bounds; `Render` draws it as a button capsule labelled *Edit JSON…*, or *Edit JSON… (wired)* when J has a source, since the wire then takes precedence; `RespondToMouseDoubleClick` opens the window when the double-click is inside the strip, and otherwise leaves the double-click to Grasshopper.
- **The window.** `ProgramJsonDialog`, an Eto `Dialog<bool>` (Eto and `Rhino.UI` come with the RhinoCommon package; no new dependency): a monospaced multi-line `TextArea` that accepts tabs and returns, a read-only area below it for the check's messages (hidden when empty), *OK* and *Cancel* (abort button, also Esc; OK is not the default button, so Return stays in the text field), resizable, about 800 × 600 pixels, modal over Rhino's main window. When J has a wire, a line above the text says that the wire is used while it is connected.
- **Storing.** `ProgramJsonComponent.SetJsonText(string? text)` is the one method OK calls: it records an undo event on the *JSON* input, replaces or clears its persistent data, and expires the input (and with it the component) so that the next solution collects the text. The smoke check calls the same method, since a headless Rhino cannot show the window.
- **Unchanged.** The component's GUID, inputs, outputs, descriptions of the other inputs, and its solve. The *JSON* input's description gains one sentence on the button. No `Lod.Core` change.

## Tests

- **Unit, test-first** (`tests/Lod.ProgramJson.Tests/TextCheckTests.cs`): empty, white space, and null give Clear; the Medium Office fixture gives Store without messages, and a fixture with a warning gives Store with the warning listed; a raw export, text that is not JSON, a schema violation, and a document whose holidays make an hourly check fail on one calendar but not on another give Reject with the reader's diagnostics, formatted one per line.
- **Headless Rhino** (`scripts/rhino-smoke/specs/program-json-editor.py`, written before the component change): the component's attributes are the new type and its bounds hold the strip below the last parameter; `SetJsonText` with the Medium Office text gives the preset; a wire into J wins over the stored text; `SetJsonText("")` clears the stored text; the stored text survives saving and reopening the definition; the check rejects a raw export. The spec `examples` still reopens all 20 examples.
- **For a person in Rhino 8** (added to the smoke-test checklist): the strip's look in both canvas themes, the double-click, the window's size, paste of a whole file, the error list, Cancel, Esc, and undo.

## Documentation

`docs/architecture/program-json.md` (the component section), the component reference through the *JSON* input's description, `docs/development/grasshopper-smoke-test.md`, the roadmap's progress log, and D-128. The public site follows at the next release.

## Acceptance criteria

`scripts/verify.ps1` passes; the new and the existing smoke specs pass; no GUID changes; a definition saved with 1.2.0 opens unchanged.

## Build log

- 2026-10-09: note written; branch and worktree made from `main` `3e46108`.
- 2026-10-09: `ProgramJsonTextCheck` test-first (11 tests); the smoke spec `program-json-editor` written first and failing (0 ok, 6 failed); then the attributes, the dialog, and `SetJsonText` / `CheckJsonText`.
- 2026-10-09, **finding:** Grasshopper's archive turns every LF of stored text into CR LF, on saving a definition and in undo records (the Medium Office's 45 262 characters came back as 46 852). The reader hashed the exact text, so the SHA-256 in *Source* changed after a save, an undo, or a paste with CR LF; this already held for text set with *Set Text*. Raised with the owner, who chose **LF** (D-128): the reader hashes the UTF-8 text with CR LF and lone CR made LF, so the checksum equals that of the atlas file, which uses LF, however the JSON arrives. JSON allows raw line breaks only as whitespace between tokens, so the JSON's meaning is unchanged; tests cover CR LF, CR, mixed endings, and other whitespace. The smoke spec then passed 29 of 29.
- 2026-10-09, **review** (second agent): nothing blocking. Fixed: a null *Year* on a wire made `First()` throw in the double-click (now the default calendar); the window says when *J* stores several texts, which OK replaces with one; smoke checks added for *Holidays* in two branches, a *Year* of two items, wired *Year* and *Holidays*, a null *Year*, and the check while *J* is wired; `DataOf` reads wired inputs' collected data and otherwise the stored values; the hash streams through `IncrementalHash`; this note's wording on the checksum, the default button, and the warnings.
- 2026-10-10, **owner's test in Rhino 8:** after OK the window closed and the *JSON* input held the text (its tooltip showed it), but the component still warned `Input parameter J failed to collect data`. `SetJsonText` expired only the component, so the input kept its collected data from before; the headless checks had solved with `NewSolution(true)`, which expires every object and hid it. A new smoke check, `live document`, stores, stores again, clears, and undoes in a solved, enabled document with only the solutions `SetJsonText` starts; it failed 3 of 6 before the fix. `SetJsonText` now expires the input, and `program-json-editor` passes 40 of 40.
