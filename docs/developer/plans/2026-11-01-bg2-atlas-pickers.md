# Stage BG2: atlas pickers on Mix Programs and Construction JSON, canonical checksums, and site downloads (design note)

> **Status:** Done (D-225 to D-230) · **Date:** 2026-11-01 · **Decided by:** Cheng Xuan Li (the owner accepted every issue and fix of the 2026-10-31 review on 2026-11-01: B1 part 2, B4, B5, B6); the controller (the designs below where the owner left the method open) · **Decisions:** D-124, D-126, D-142, D-207, D-208, D-209, D-217, D-218, ADR-017, ADR-018, ADR-021, ADR-036; new: D-225 to D-230 · **Atlas side:** atlas ADR 0057 (canonical store documents, `json_sha256`) and ADR 0058 (the site index schema 1.0.0, reasons beside nulls, `folders[*].compositions`), live on the 2.2.0 site since 2026-11-01 · **Branch:** `fix/bg2-atlas-pickers` in `D:/bg-bg2`, from `main` at `bdc9eef`

The review of 2026-10-31 gave BEMGen four issues of the atlas site in this stage. The evidence is the subject-4 review (S4-07, S4-09, S4-16) and S1-13, S1-19, S3-08.

| Issue | Finding | Decision | Design |
| --- | --- | --- | --- |
| B4 | S4-09 | D-225 | §1 |
| B5 | S4-07, S1-13, S3-08 | D-226 | §2 |
| B1 (2) | O-1 | D-227, D-228 | §3 |
| B6 | S4-16, S1-19 | D-229 | §4 |

Built against the live 2.2.0 site, whose index is now atlas site index schema 1.0.0 (`kind: atlas_site`). The atlas's data release 2.3.0 (stage AT1, not merged) changes export contracts; §5 lists what stage REL-B refreshes then. The readers stay strict.

## 1. Site downloads (B4, D-225)

- **At most four requests at a time.** `AtlasSite` fetches store files through one gate of four (`AtlasSite.MaxConcurrentDownloads`), shared by every window of the Rhino session, so a DOE map of 32 keys or a mix of 20 members never sends more than four requests at once.
- **One retry.** `HttpAtlasSiteTransport` asks once more after an HTTP 429 or 5xx answer, after a backoff (2 s, or the server's `Retry-After` when it is longer, at most 10 s). A cancelled wait is a cancelled request.
- **A message that says what to do.** A 429 after the retry is `AtlasSiteRateLimited`: the site (GitHub Pages) is limiting requests from this network; wait a few minutes and try again. A 5xx after the retry says the site answered it twice.
- **No exception reaches the window's thread.** Every `async void` handler of the four atlas windows (and the two new ones) catches any exception besides cancellation and puts it in the status line, re-enabling the buttons.
- **Tests.** Two loopback HTTP servers: 429 then 200 gives the body; 429 twice gives `AtlasSiteRateLimited` with the wait advice; 503 then 200 gives the body; 404 is not retried. A recorded site that counts requests in flight shows a DOE map of eleven keys never above four. The window handlers are a person's check in Rhino.

## 2. Canonical checksums and the store path (B5, D-226)

- **One canonical form, the atlas's.** `CanonicalJson` (`Lod.ProgramJson`) writes a parsed JSON value as the atlas's `site_store.canonical` does (atlas ADR 0057): object keys sorted by code point, no insignificant whitespace, strings in UTF-8 with only `"`, `\`, and control characters escaped (`\b \f \n \r \t`, else `\u00xx`), integers as written (a leading minus of zero dropped), and other numbers as Python's `repr` of the double: the shortest round-trip digits, fixed notation from 10⁻⁴ to below 10¹⁶ with at least one decimal (`100.0`), otherwise `1e-05`, `1.5e+16`; no trailing newline. A lone surrogate is refused (Python cannot encode it either).
- **Both readers.** `ProgramJsonReader` and `ConstructionJsonImporter` set `Json.Sha256` (and the construction set's `SHA-256` line) to the SHA-256 of the canonical bytes. The site's store text is canonical already, so its checksum is the descriptor's `json_sha256` and the file the site's *Download* saves; the pretty-printed release file, a CR LF panel, and a re-indented copy of the same JSON get the same checksum. This replaces D-207's LF checksum. Recorded checksums in tests and snapshots change once, each recomputed outside BEMGen with the atlas's `python -m scripts.site_store`.
- **The store path.** A program taken from the site records where it came from: `Json.Store` in *Source*, `<site root>store/<sha256>.json.gz (atlas site release 2.2.0)`. *Program JSON* keeps the last atlas pick (store path, release, canonical checksum) in the component and records it only while its text has that checksum, so an edited or rewired text does not claim it. The DOE maps and the atlas mixes give each key's or member's own path. *Construction JSON* records the unified document's path in the set's source the same way.
- **Not changed.** The draw's `recipe_sha256` and `setting_sha256` and the test-suite generator's file names identify files, as ADR-033 decision 10 says; they stay checksums of the bytes.

## 3. *Get from Atlas…* on *Mix Programs* (B1 part 2, D-227, D-228)

**The site index (D-227).** `AtlasSiteIndex` reads `kind` `atlas_site` and `schema_version` 1.x (a newer major is refused with "update BEMGen"), the generation descriptor's `json_sha256` (checked after decompression), and each folder's `compositions`: by mix program ID, `mode` (`general` or `department`, the mix program's own mode) and `members` (`program_id`, `represented_area_m2` ≥ 0, `weight` in [0, 1]). Each member must be a `source` program of the same folder, listed once; the weights must sum to 1 and each equal its area share, within `ToleranceSettings.AbsoluteFraction`; every mix of the folder must have its composition. A fault drops the compositions only (`CompositionsFault`), as a folders fault leaves the programs (ADR-036 decision 2).

**The strip (D-228).** *Mix Programs* gets *Get from Atlas…* at the bottom.

- **The window** lists the site's folders that hold source programs, by template and building type. For a folder it offers the starting selections: each general mix and each department mix of the folder (members ticked, default weights the composition's area shares), and *Free selection*: every source program of the folder, unticked, with the area share of the folder's general mixes as its default weight where it is a member of one, else no weight. The user ticks or unticks members and edits weights (finite, greater than 0); the window shows each member's space type, represented area, weight, and normalised share.
- **OK** downloads each ticked member in the chosen version (filled by default), verified as *Program JSON*'s download is, gives each the program check on the component's *Climate Zone*, *Year*, *Holidays*, and *Context*, then solves the mix as the component will; only a mix the solve accepts is stored. One text (`bemgen-atlas-program-mix` 1.0.0: the site, its release and manifest checksum, the folder, the starting selection, the version, and per member its program, space type, store path, represented area, weight, and text), with one undo event. *Clear* removes it.
- **The solve** reads the stored text offline: each member through *Program JSON*'s import (any-program preset named by its space type, the JSON's fenestration), then `ProgramMix.Mix` with the stored weights (D-124). Old definitions reopen without the IO dialog (appended inputs).
- **Presets and Weights become optional overrides.** A wire into *Presets* takes precedence over the stored mix, as a wire into *Program JSON*'s *JSON* does over its stored text, and then needs *Weights* as before (a remark says the stored mix is unused). With the stored mix and no *Presets*, *Weights*, when given, replace the stored weights, one per member in the stored order. Without either, the component asks for them.
- **New inputs and outputs, appended.** Inputs *Climate Zone*, *Year*, *Holidays*, *Context* (used with the stored mix only); outputs *JSON* (each member's text, in member order) and *Left Out* (a branch per member). No GUID changes.
- **Why BEMGen mixes the members itself** rather than taking the atlas's `General_Mixed` program: the user can untick and reweight, and the result keeps every member's program, checksum, store path, and weight in its provenance (GLOBAL scientific rule 2). The atlas's own mix programs stay available through *Program JSON*; the two may differ where the atlas's mixing rule differs from D-124's.

## 4. *Get from Atlas…* on *Construction JSON* (B6, D-229)

- **The index's construction sets.** `AtlasSiteIndex` reads `construction_sets`: each set's page and contexts, each context's `detailed` and `unified` store paths with `reason` and `unified_reason` beside their nulls (atlas ADR 0058). A fault drops the sets only (`ConstructionSetsFault`).
- **The window** lists the sets, grouped by template and building type as their IDs begin, and a set's construction contexts (the climate zone, and for the offices' shared sets the folder). OK downloads the context's unified document, verified by its store path, checks that it is `building_level_equivalent` whose `detailed_context_id` is `<set>.<context>`, imports it with `ConstructionJsonImporter.Import` (the solve's own call), and stores the text as the *JSON* input's value with one undo event, with its store path recorded as in §2.
- **Residential sets are refused, with the reason (the issue's second half).** Where one document serves both representations (`unified` names the `detailed` file: the 1,112 contexts of the IECC residential and manufactured-housing sets), the document is a `source_model_construction` 1.0.0, which BEMGen does not read: it describes a source dwelling's constructions by the source's own surfaces, and BEMGen converts only whole-building unified sets (D-142). The window says so before any download. The ResStock sets' unified documents are single-dwelling (`whole_dwelling`) and are refused by the import's own message (D-142). *Decision:* BEMGen does not read source-model constructions in this stage; reading them needs a mapping from source surfaces to BEMGen's roles, a design of its own.
- **The IECC commercial sets** download and import, and their source design-flow infiltration refuses conversion as before (D-172); the window shows the import's warning.

### As built

- **§2.** The DOE maps keep each key's canonical checksum as downloaded (`bemgen-atlas-program-map` 1.1.0; a 1.0.0 map from 1.8.0 reads and records no store file), and the mixes each member's, so `Json.Store` is recorded against the download, not against the text read (review, D-230).
- **§3.** OK's trial mix uses the stored weights and the component's calendar, climate zone, and context, not its *Name*, *Space Type*, or *WWR*, which the solve applies. The starting selection and its represented areas are taken from the index, never from the window. A wired but empty *Presets* still takes precedence, with a warning. *Read* sets *Presets* and *Weights* optional on a definition saved before, since Grasshopper saves the flag (review). The mixed preset's own *Source* names its members (`Input.k`) and nests their *Source*s, but not the folder and starting mix, which the remark names.
- **§4.** The window groups the sets by the template and building type their IDs begin with; the index gives no folder for a set.

## 5. At atlas release 2.3.0 (stage REL-B)

- `AtlasSiteIndex.KnownReleaseManifests` gains the 2.3.0 manifest; `ProgramJsonDocument.KnownReleases` its label.
- The recorded sites `Fixtures/site/` and `Fixtures/site-doe/` and their tests (store paths, checksums, the composition and construction-set counts) are recorded again from the 2.3.0 site.
- If AT1 changes the unified construction contract (A2's `InternalMass`, a schema version), the embedded construction schemas and `ConstructionJsonImporter.UnifiedVersion`, and the picker's identity check, follow it.
- The canonical checksums of the fixtures do not change with a re-export unless the content does.

## 6. Checks

`scripts/verify.ps1` with 0 warnings before the merge; the live site checks (`BEMGEN_ATLAS_SITE_LIVE=1`) once; a review by a second agent (D-111). Rhino is not launched (the owner may be using it): the smoke specs are written and the windows go to a person's checklist in `grasshopper-smoke-test.md`.
