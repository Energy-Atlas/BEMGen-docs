# Programs and program maps from the atlas site (design note)

> **Status:** Done: phase 1 merged (D-207), phase 2 merged (D-208), phase 3b merged (D-209, [ADR-036](../decisions/ADR-036-atlas-program-maps.md), PR #16), released in 1.8.0 (D-210). Approved 2026-10-30: the owner accepted every recommendation of §6 ("Accept all, start") · **Date:** 2026-10-30 · **Decisions:** D-122, D-126, D-128, D-129, D-155, ADR-018, ADR-033, ADR-035; new: D-207 (phase 1), D-208 (phase 2), D-209 (phase 3), D-210 (release 1.8.0) · **Branch:** `docs/atlas-program-picker` (this note; phase 1 builds on it) · **Atlas side:** a new ADR (0052) in `Energy-Atlas/archetype-atlas`, phase 3 only

The owner asked (2026-10-30) to merge the program JSON popup, and to go further: link it to the atlas site, and let both *Program JSON* and the DOE program map presets take their programs that way. This note records what was found, the design, the questions for the owner, and a plan in three phases. Each phase is run as D-111 sets out: its part of this note approved, a test-first build on its own branch, a review by a second agent, the headless Rhino check, `scripts/verify.ps1` with 0 warnings, one decision-log entry, and a person's checklist in Rhino 8.

## 1. What exists

- **`feature/program-popup-window`** (D-128, 15 commits, not merged). A strip *Edit JSON…* on *Program JSON*. A double-click opens an editor window. OK checks the text with `ProgramJsonTextCheck` and stores it as the *JSON* input's persistent data with one undo event (`SetJsonText`). The branch also fixes a real defect that is still on `main`: Grasshopper stores text with CR LF line endings, so the SHA-256 in the preset's *Source* changed after a save, an undo, or a paste. The branch hashes the text with LF line endings, which gives the atlas file's checksum however the text arrives.
- **`feature/program-popup-web`** (D-129, the window branch plus 4 commits, experimental). A second strip *Get from Atlas…* opens a web view of an atlas page. The user clicks *Copy JSON*, then *Copy with defaults*, and `ClipboardWatcher` picks the text up from the clipboard by the Windows clipboard sequence number. The page re-serialises the JSON, so the checksum is not that of the atlas file. D-129 left four items open before a merge: the owner's decision on web access after D-126, the docs and ADR-018, a fixed or configurable start page, and a person's checklist.
- **Merge state (trial merge, 2026-10-30).** Both branches start at `3e46108` and are 489 commits behind `main` (`062f5e1`). Nine files conflict, up from five at D-155: six documents (AGENTS.md, the decision log, `program-json.md`, the roadmap, the smoke-test document, the rhino-smoke README) and three code files (`ProgramJsonComponent.cs`, `ProgramJsonDocument.cs`, `MediumOfficeTests.cs`). On `main` the component now reads release 2.2.0 exports, filled or source. D-128 and D-129 are free on `main`, whose log goes from D-127 to D-130, so neither needs renumbering.
- **The DOE program map presets.** The fifteen *DOE … Programs* components (panel *1 Program Presets*) have no inputs. Each outputs a program map, its keys (whole standards space types such as `MediumOffice - OpenOffice`, in ordinal order), and one preset per key. The presets are illustrative: the example preset of each key's space type, with the DOE reference building's window ratios per orientation. *DOE Program Map* rebuilds a map from keys and presets.

## 2. What the atlas site already offers

The site (https://energy-atlas.github.io/archetype-atlas/) publishes `site-manifest.json`, an index of the release it was built from. Checked on 2026-10-30 against the live site (release 2.2.0, `partial: false`):

- `programs` maps each of the 3051 program IDs to its page path (relative to the site root) and to the store paths of its filled and source exports.
- Every store file is gzip-compressed canonical JSON named by the SHA-256 of its gzip bytes (`store/<sha256>.json.gz`; `scripts/site_store.py`), so a download is checked against its own name.
- The site sends `Access-Control-Allow-Origin: *`. The index is 2.6 MB, 761 kB on the wire. A program export is a few kilobytes on the wire and about 30 kB of text.
- The site holds no folder `generation.json`, which *Schedule Draw* needs (ADR-035).

So BEMGen can resolve the page the user is looking at to a program ID, and download that program's export verified by its checksum, without the clipboard and without any change to the site.

## 3. How DOE keys meet atlas programs

Every commercial atlas program is named `<space type>_<building type>` (2978 of 2978 in release 2.0.0, whose program IDs 2.1.0 and 2.2.0 keep). Matching the 153 program keys of BEMGen's DOE layouts to these names, folder by folder:

| Atlas family | Keys that resolve once in the prototype's folder |
| --- | --- |
| DOE Ref pre-1980 | 153 of 153 |
| DOE Ref 1980–2004 | 153 of 153 |
| 90.1-2007 | 151 of 153 |
| 90.1-2013 | 149 of 153 |
| 90.1-2019 | 149 of 153 |

- **The gaps are renamed or split space types**, not missing data. Secondary school `Gym - audience` (all three 90.1 vintages); small hotel `GuestRoom`, which 90.1 splits into occupied and vacant rooms by floor (all three); hospital `Office`, which 90.1-2013 and 2019 split by floor; stand-alone retail `Retail`, which 90.1-2013 and 2019 split into core and front.
- **Names alone are ambiguous across folders.** `Retail` also appears in the tall and super-tall buildings, and several restaurant keys appear in both restaurants and the hospital. The folder must be fixed per prototype, never searched.
- **Prototype to folder.** The medium and large office keys live in the atlas's detailed folders (`medium-office-detailed`, `large-office-detailed`), and the small office's in `small-office-detailed`. Three folders are spelled differently from their prototypes: `retail-standalone`, `retail-stripmall`, and `super-market`. The other nine carry the prototype's own name.

## 4. Design

### 4.1 Phase 1: the editor window and the checksum fix

Merge `feature/program-popup-window` as it was approved in D-128, rebased onto `main`. Nothing new is designed.

- Resolve the nine conflicts. In the component, the branch's `CreateAttributes`, `SetJsonText`, and the *JSON* description sentence go onto `main`'s 2.2.0 component. The check (`ProgramJsonTextCheck`) runs on `main`'s reader, so it accepts what `main` accepts.
- The checksum change alters *Source* once for a definition that stored CR LF text: it becomes the checksum of the same text with LF. No recorded fixture changes, since the fixtures are LF. Nothing else reads `Json.Sha256`: *Schedule Draw* records the program by ID and the release's manifest hash.
- D-128 is added to `main`'s log with a line on the rebase. The smoke spec `program-json-editor` runs in the headless Rhino check.
- **As built (D-207).** A merge commit rather than a rebase. The release 2.x fixtures have CR LF line endings, so their recorded checksums did change (no fixture file did), and *Schedule Draw*'s `source_program_sha256` reads `Json.Sha256` too; the check also takes the component's *Climate Zone* and *Context*.

### 4.2 Phase 2: *Get from Atlas…* on *Program JSON*

The web view of D-129 stays. The clipboard goes: BEMGen reads the page's address, not the page or the clipboard.

- **`AtlasSite`** in `Lod.ProgramJson`, with no Rhino dependency and the HTTP transport injected, so it is tested offline on recorded files:
  - the site root is a constant, `https://energy-atlas.github.io/archetype-atlas/`;
  - `ReadIndex` parses `site-manifest.json` and refuses an index marked `partial`;
  - `ProgramForPage(uri)` gives the program ID whose page is that address, or none;
  - `Download(programId, values)` fetches the filled or source export, refuses it unless the SHA-256 of the gzip bytes equals the hash in its path, decompresses it, and refuses it unless its `id` is that program and its `source.release` is the index's release.
- **The window.** `ProgramJsonAtlasDialog` keeps its address box and web view, and opens on the site's catalogue. Navigation outside the site root is refused, with a status line naming the address. A button *Use this program* is enabled while the page is a program page. It downloads the filled export (or the source one, by a choice in the window), runs `ProgramJsonTextCheck`, and on Store saves the text with `SetJsonText` and closes. The status line names the program, the release, and what failed.
- **The solve reads no file or network**, as D-126 set out. The network is used only after a click in the window, and the definition keeps the text, so it reopens and re-solves offline and gives the same preset.
- **The index** is downloaded when the window opens and kept for the Rhino session while the site's cache time (10 minutes) holds. A timeout or an offline machine gives a message, never an exception.
- **The stored text** is the store file's content byte for byte. The checksum in *Source* is therefore that of the site's canonical JSON. It differs from that of the pretty-printed file in `atlas-release-2.2.0.zip`, and the docs say so.
- **Removed:** `ClipboardWatcher` and the *Copy JSON* instruction. Pasting stays possible through *Edit JSON…*.

### 4.3 Phase 3: atlas program maps on the DOE program map presets

**Atlas side (ADR 0052).** `site-manifest.json` gains, for each program, `space_type` (the name before its last `_`), `building_type`, `folder` (the release folder path), and `mode`. They are written by `scripts/suite_site.py` from the release records, and `scripts/site_check.py` checks that every commercial program has them and that they rebuild its name. The change is additive: readers that do not know the fields ignore them. No data release is needed, since the site is rebuilt from the same release. Optionally, the same ADR puts each folder's `generation.json` in the store and the index, so *Schedule Draw*'s *Generator JSON* can come from the site too.

**BEMGen side.**

- **`DoeAtlasFolders`** in `Lod.Generators`: one row per DOE building type with its atlas folder name (§3). A test checks it against a recorded index: per family, the keys that resolve once and the gaps, listed explicitly. A new gap or a new ambiguity fails the test.
- **The strip.** Each *DOE … Programs* component gets a strip *Get from Atlas…*. The window lists the families that hold the prototype's folder, each with its coverage (for example "13 of 14 keys; `GuestRoom` has no program"), and the choice of filled or source. OK downloads every key's program as in §4.2, in parallel and each verified, and stores them with one undo event as one persistent text: the site's release, the family, the folder, and the program text per key. *Clear* in the window returns the component to its illustrative presets.
- **The solve** reads the stored texts offline through the same import as *Program JSON*, sharing its code. The component has no inputs today; it gains optional ones: *Climate Zone*, *Year*, *Holidays*, *Context*. Unset, they behave as on *Program JSON*. The window ratios stay those of the DOE reference building, as today, so the presets still fit the generator's geometry. The remark says the presets are the atlas's, names the release and family, and drops the "illustrative" wording.
- **Keys without a program** follow the owner's answer to §6 question 5.
- **Unchanged:** every GUID, every existing output, and *DOE Program Map*. Without stored texts a component behaves exactly as today, so saved definitions are untouched.
- ***Schedule Draw*** takes one program's JSON text and its folder's `generation.json`. The phase adds an output *JSON* to the DOE *Programs* components, after the existing ones: the stored text per key in the order of *Keys*, so a map's programs can be drawn one by one.
- **As built (D-209).** `MatchKeys` takes only `source` programs, so the atlas's department and general programs (`*_Mixed`) are never matched; the matching test (`DoeAtlasProgramMapTests`) gives the gaps of §3 exactly. The IECC templates are not offered (ADR-036 decision 4). OK stores a family with gaps, and the solve refuses its map by key (question 5a). The stored map is the component's own state, not an input. *Schedule Draw*'s strip takes the folder by the program's `id` in the index; none of the `*-detailed` office folders has a `generation.json` on the site (90 of 255 folders have one), which its window says.

## 5. Plan

| Phase | Repository | Work | Depends on |
| --- | --- | --- | --- |
| 1 | BEMGen | Rebase the window branch, resolve nine conflicts, verify, Rhino check, merge | Owner's go-ahead |
| 2 | BEMGen | `AtlasSite` test-first, the window on the address, remove the clipboard, verify, Rhino check, merge | Phase 1; questions 1–3 |
| 3a | atlas | ADR 0052, the index fields, site check, PR, full site build on `main` | Questions 4–7 |
| 3b | BEMGen | `DoeAtlasFolders` test-first, the strip and window, the solve, the *JSON* output, verify, Rhino check, merge | Phases 2 and 3a |

- Phases 1 and 2 can ship as one BEMGen release, phase 3 as the next. Releases follow D-175 and D-197.
- Each phase's live check runs once against the real site, gated by an environment variable as `RealDrawTests` is. Every other test reads recorded files.
- Phase 3a changes only the site, so the sampled PR build checks it and the full build on `main` is the gate (the atlas's ADR 0043 §6).
- `feature/program-popup-web` is closed after phase 2 and kept as the tag `archive/program-popup-web`, as `batch1-saved` was.

## 6. Questions for the owner

Each has a recommendation. **The owner accepted all eight on 2026-10-30**, so the build follows them. Phases 1 to 3 are merged one by one and released together as BEMGen 1.8.0, which saves one release cycle against §5's two.

1. **Web access (D-126).** Allow the network after a click in a window, never in a solve, from the atlas site only? *Recommended: yes.* The definition keeps the text, so it stays reproducible offline.
2. **The site address.** Fixed to the atlas site, or configurable (for a local build or a fork)? *Recommended: fixed in phase 2*, with a configurable root later if needed.
3. **Filled or source.** Which does the window take by default? *Recommended: filled*, with source as a choice in the window. DOE Ref programs have only a `source` view in `generation.json` (ADR-035), which matters to *Schedule Draw*, not to the import.
4. **Where the map strip goes.** On each *DOE … Programs* component, as designed; on *DOE Program Map*; or in a new component? *Recommended: on each DOE Programs component.* It knows its prototype, so only the family is chosen, and its outputs already feed the generators.
5. **Keys without a program** (the four 90.1 renames in §3). (a) Refuse: the map is not output, the error names the keys, and *Presets* is output with those positions empty so *DOE Program Map* can complete it by hand. (b) Fill them with the illustrative preset, with a warning naming them. (c) An owner-approved crosswalk per key (for example `GuestRoom` to the occupied guest room of the same floor group). *Recommended: (a) now*, since (b) mixes sourced and illustrative values in one map and (c) is a source decision that needs its own evidence.
6. **Families offered.** All five commercial families that hold the folder? *Recommended: all five*, with coverage shown in the window.
7. ***Generator JSON* from the site.** Put each folder's `generation.json` in the site index (ADR 0052), and give *Schedule Draw* the same strip? *Recommended: yes, in phase 3*, since the draw needs both texts and the site is where the user finds the program.
8. **Platforms.** The plugin is released for Windows only, where the web view is WebView2. *Recommended: no macOS work in these phases.*
