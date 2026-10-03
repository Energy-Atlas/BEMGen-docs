---
name: sync-docs
description: Check whether the public BEMGen documentation site in this repository (user guide, generated component reference, icons, screenshots, and the developer pages generated from BEMGen) and its latest release still match the BEMGen plugin, and write a plan of the edits needed. Use after a BEMGen release or stage close-out, after a new docs export, before a deployment or a release, and whenever someone asks whether the docs are stale or in sync. It reports; it does not edit unless asked.
---

# sync-docs (docs repository)

Compares this site and its releases with the BEMGen plugin and outputs a plan of edits. **Do not edit any file unless the user explicitly asks you to apply the plan.** Read-only commands and builds into git-ignored folders are fine.

Read `AGENTS.md` and `HANDOVER.md` first. The plugin is the source of truth. The developer pages are generated from BEMGen's `docs/`, `GLOBAL.md`, and `AGENTS.md`. Whether those sources are right is checked by BEMGen's own `sync-docs`. Here, check only that the published copy is current.

## 0. Find the source

- **BEMGen checkout:** `$env:BEMGEN_REPO`, default `D:\BEMGen`. If it is missing, say so, run only sections 3 and 4, and report that the comparison with the plugin was not made. BEMGen is private, so do not look for its files on GitHub.
- **Pinned version:** `reference-source.json` names the BEMGen version and commit the generated parts were imported from.
  - Compare it with the latest tag in the checkout (`git -C $env:BEMGEN_REPO describe --tags --abbrev=0 main`) and with `Directory.Build.props` there.
  - If BEMGen has moved on, `git -C $env:BEMGEN_REPO diff --stat <pinned>..main -- src/Lod.Grasshopper src/Lod.Generators src/Lod.Core src/Lod.Export examples docs GLOBAL.md AGENTS.md` lists what may have changed for the site.
- **Latest release:** the newest GitHub Release of this repository. It should have the tag `v<version>` of the pinned version and four files: the `.gha` zip, the `.yak`, the examples zip, and `SHA256SUMS.txt`.

## 1. Generated parts: reference, icons, screenshots, developer pages

Any difference here means "re-import from a new export", never a hand edit.

- **An export of the current BEMGen version exists**, or Rhino 8 is available to make one: `C:\Program Files\Rhino 8\System\Rhino.exe` exists and no Rhino process is running. To make one, run BEMGen's `scripts/docs-export/export.ps1 -OutDir <folder outside both repositories>` in the BEMGen checkout. Then:
  1. In a temporary worktree of this repository, run `python scripts/import_reference.py --export <folder>`.
  2. `git status` and `git diff` there show what is stale. Ignore screenshot pixel noise from anti-aliasing: a few pixels differing by one colour level.
  3. Read the export's `redactions.txt` and its log. `Gap:` lines (objects, inputs, or outputs without a description) are plan entries for BEMGen.
  4. Remove the worktree afterwards.
- **No export and no Rhino:**
  1. Read BEMGen's component sources and compare them with the committed reference pages: `src/Lod.Grasshopper/Components/*.cs`, `src/Lod.Grasshopper/Parameters/BemParameters.cs`, `src/Lod.Grasshopper/ComponentCategories.cs`, the generators' parameter records' `Default` values in `src/Lod.Generators/*/*Generator.cs`, and the example presets in `src/Lod.Core`.
  2. For every component and parameter compare these fields: name, nickname, panel, exposure, GUID, description, and every input and output (name, nickname, type, access, optional, default, description, and order).
  3. Compare `docs/assets/icons/` with BEMGen's `src/Lod.Grasshopper/Icons/` (byte-identical).
  4. Compare `docs/developer/**` with BEMGen's `docs/` by file list and modification commit: `git -C $env:BEMGEN_REPO log -1 --format=%h <pinned>..main -- docs GLOBAL.md AGENTS.md`.
  5. Say in the report that the comparison was made from the sources.

## 2. Hand-written pages

Check `docs/index.md`, `docs/user/*.md`, and `docs/developer/index.md` against the plugin and the generated reference:

- **Components:**
  - names, nicknames, and panels as registered;
  - no removed component still described, and no new one missing.
- **Inputs and outputs** in `workflow.md`, `example-end-to-end.md`, and `typologies.md`: names, nicknames, order, defaults, and units (metres).
- **The typologies table:** family IDs, preset inputs, default dimensions, and the default plans' zone counts, floor areas, and window counts.
- **The end-to-end example:** every input value and every expected output.
- **Recompute, do not trust the page.** Run the pipeline headless in a scratch project outside both repositories that references BEMGen's `src/Lod.Core`, `src/Lod.Generators`, and `src/Lod.Export`. Alternatively, read the values from BEMGen's tests and snapshots (`tests/**/Snapshots/`, `tests/Lod.Integration.Tests/Families.cs`).
- **Runtime message texts and diagnostic codes** quoted on the pages, against BEMGen's `src/Lod.Core/Common/DiagnosticCodes.cs`.
- **Install and download instructions** in `getting-started.md`, against the latest release's file names; the example file names against BEMGen's `examples/README.md`; every embedded screenshot exists.

## 3. Public-content check

- No link to a path inside the private BEMGen repository (`github.com/EnvironmentalSystemsLab/BEMGen/` followed by a path). Its home page may be named only as private.
- No e-mail addresses or user-profile paths (`C:\Users\<name>`, `C:/Users/<name>`, `/c/Users/<name>`) on any page. A hit in a developer page means the export's redaction missed it: that is a plan entry for BEMGen. Lab paths such as `D:\BEMGen` are allowed on developer pages: they are instructions for the lab machine (BEMGen D-119).
- No credentials or tokens anywhere in the repository.
- Decision numbers such as "(D-108)" belong on developer pages only. A hit in `docs/user/` is a plan entry: a BEMGen description if the hit is in the generated reference, or this repository if it is in a hand-written page.

## 4. Build and deployment

1. Run the strict build with a Python that has `requirements.txt` installed, in a virtual environment outside the repository: `scripts/build.ps1 -Python <venv>\Scripts\python.exe`. It must pass, and every warning is a plan entry.
2. Report the result of the latest Pages workflow run on `main`.
3. Check that the live site's version, as `reference-source.json` names it, matches `main`.

## 5. Output

Report, without editing:

1. What was checked and how:
   - the BEMGen version and commit compared with;
   - whether an export, Rhino, or source reading was used;
   - the build command and its result, quoted;
   - the latest release.
2. **Plan of edits:** a table with one row per edit, giving the repository (*this* or *BEMGen*), the file, the change (the stale text and the correct value), and the reason (the BEMGen code location, test, or decision that shows it). Put wrong instructions or numbers first, then missing content, then wording. A missing release for the current version is a plan entry.
3. Items that need a person: the look in Rhino, the deployed site in a browser, and installing from the release.
4. If nothing is stale, say explicitly: "The site and release are up to date with BEMGen <version> (<commit>)."

Apply the plan only when the user asks. Then:

1. Edit the hand-written pages.
2. Re-import the generated parts; never hand-edit them.
3. Run the strict build.
4. Push and release only with the owner's yes.
