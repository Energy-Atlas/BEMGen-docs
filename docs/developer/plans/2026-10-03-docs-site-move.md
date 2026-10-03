# Move the docs site to a public repository (design note)

> **Status:** In progress: step B done (D-119, `v1.0.1`); step C handed to the docs repository's agent · **Date:** 2026-10-03 · **Decisions:** D-111, D-115, D-116, D-117, D-118, D-119 · **Handover material:** [2026-10-03-docs-site-move/](2026-10-03-docs-site-move/HANDOVER.md)

The MkDocs site leaves this repository for the **public** repository `energy-atlas/BEMGen-docs`, deployed to GitHub Pages at `https://energy-atlas.github.io/BEMGen-docs/` (D-117, D-118). It is moved, not copied: nothing of the site stays here. The site publishes both its user part and its developer part. The public repository also carries the plugin's release files on its GitHub Releases. Below it is called *the docs repo*.

## Findings that shape the plan

1. **BEMGen is private** (its GitHub page returns 404 without a login). The docs repo therefore cannot check BEMGen out while it deploys, and no page may link to a file inside BEMGen. Everything the site takes from BEMGen arrives as a **docs export**, made here and committed there.
2. **The generated parts need Rhino and a BEMGen build.** The component reference, the icons, and the screenshots are made inside Rhino 8. They stay generated on a lab machine. The deployment only runs `mkdocs build --strict`.
3. **The developer part is generated from BEMGen too.** Its source is `docs/`, `GLOBAL.md`, and `AGENTS.md`, edited here and never in the docs repo. Their links to source files (`src/`, `tests/`, `scripts/`, ...) would point into the private repository. The export turns them into plain code text. The pages hold one e-mail address (D-050's commit identity). The export redacts e-mail addresses and user-profile paths (`C:\Users\<name>`) from the published copy, lists each redaction, and leaves the sources here as they are. Lab paths such as `D:\BEMGen` stay: they are instructions for the lab machine, not personal data.
4. **The generated reference quotes decision numbers** about 150 times, for example "(D-108)". They come from the components' descriptions, which Grasshopper users also see. They are removed at the source (D-118).
5. **Readers need the plugin.** The release files go on the docs repo's GitHub Releases:
   - the `.gha` with its libraries, as a zip;
   - the `.yak`;
   - the example definitions, as a zip;
   - checksums.

   The Yak package server stays unused (D-115).

## What goes where

| In BEMGen now | After the move |
| --- | --- |
| `docs-site/**` (hand-written pages) | Docs repo `docs/**`, owned there |
| `docs-site/user/components/`, `docs-site/assets/icons/`, `docs-site/assets/screenshots/` | Docs repo, regenerated from each export |
| `mkdocs.yml` | Docs repo root. `site_url` and `repo_url` point to the docs repo, and the `docs_dir` line is dropped. Its *Developer* navigation block is written by the import script. |
| `scripts/docs-site/component_reference.py`, `test_component_reference.py` | Docs repo `scripts/`, as `import_reference.py`, which reads an export |
| `scripts/docs-site/build.ps1`, `serve.ps1`, `requirements.txt` | Docs repo, without the assembly step |
| `scripts/docs-site/assemble.py` | Becomes `scripts/docs-export/developer_pages.py` here; writes the developer part into the export |
| `scripts/docs-site/component-metadata.py`, `screenshots.py` | `scripts/docs-export/` here |
| `scripts/package-yak.ps1` | Kept here, joined by `scripts/package-release.ps1` |
| `.claude/skills/sync-docs/` | Split. BEMGen's version checks the sources here and says when to export; the docs repo's version checks the site against an export and the plugin. BEMGen's version is `.claude/skills/sync-docs/SKILL.md`; the docs repo's draft is in the handover folder. |
| `docs/`, `GLOBAL.md`, `AGENTS.md`, `examples/` | Stay here as the sources. Published through the export and the release files. |

## Interfaces

**Docs export.** `scripts/docs-export/export.ps1 -OutDir <folder outside both repositories>` runs the Rhino specs through `scripts/rhino-smoke/run.ps1` and writes:

| Path in the export | Content |
| --- | --- |
| `component-metadata.json` | As `component-metadata.py` writes it today, with the objects each example holds |
| `screenshots/` | `canvas/<stem>.png`, `<stem>-plan.png`, `<stem>-building.png` |
| `icons/*.png` | From `src/Lod.Grasshopper/Icons/` |
| `developer/**` | `docs/**`, `GLOBAL.md`, and `AGENTS.md`, under the same paths the site uses today (`developer/<path in docs>`, `developer/GLOBAL.md`, `developer/AGENTS.md`), with links rewritten and redactions applied |
| `developer-nav.json` | The *Developer* navigation, as `assemble.py` builds it today |
| `redactions.txt` | Every redaction: file, line, and what was replaced |
| `source.json` | BEMGen version, commit, dirty flag, Rhino version, date |

The docs repo's `scripts/import_reference.py --export <folder>` then:

- renders `docs/user/components/`;
- replaces the icons, the screenshots, and `docs/developer/` (except its hand-written `index.md`);
- rewrites the marked *Developer* block of `mkdocs.yml`;
- writes `reference-source.json`.

User pages keep their links to developer pages, because the paths do not change.

**Release files.** `scripts/package-release.ps1` writes `dist/release/<version>/`, which is git-ignored and never pushed:

| File | Content |
| --- | --- |
| `bemgen-<version>-rh8-win.zip` | `BEMGen.gha`, `Lod.Core.dll`, `Lod.Generators.dll`, `Lod.Export.dll`, `Clipper2Lib.dll`, `BEMGen.deps.json` from the Release build (the files the Yak package holds), plus `LICENSE` and a short `INSTALL.txt`. No `.pdb` or `.xml` files. |
| `bemgen-<version>-rh8_19-win.yak` | From `package-yak.ps1` |
| `bemgen-<version>-examples.zip` | `examples/*.gh` and `examples/README.md` |
| `SHA256SUMS.txt` | Checksums of the three files above |

The release itself is created on the docs repo, with the tag `v<version>` and notes summarising the BEMGen decision-log entry of that version, and only with the owner's yes.

## Steps

**A. Owner.** Create the empty `energy-atlas/BEMGen-docs` repository and set *Settings → Pages → Source* to *GitHub Actions*.

**B. BEMGen, here.** One D-111 change, version **1.0.1**:

1. Remove the decision numbers from component, parameter, input, and output descriptions. Text only; GUIDs and behaviour do not change.
2. Add `scripts/docs-export/`:
   - the two specs, moved here;
   - `developer_pages.py`, with its test;
   - `export.ps1` and a README.
3. Add `scripts/package-release.ps1`.
4. Delete `docs-site/`, `mkdocs.yml`, and the rest of `scripts/docs-site/`.
5. Update `.gitignore`: drop `/.docs-build/` and `/site/`; `dist/` is already there.
6. Replace `.claude/skills/sync-docs/SKILL.md` with the BEMGen draft.
7. Update everything that mentions the old site: `README.md`, `AGENTS.md`, `scripts/rhino-smoke/README.md` and `run.ps1`, `examples/README.md`, `docs/development/grasshopper-smoke-test.md`, and the message in `scripts/package-yak.ps1`.
8. Review the diff with a second agent.
9. Run the gates: `scripts/verify.ps1`, `scripts/rhino-smoke` once, and the export once. Check that the export has no `Gap:` lines and that a scan finds no decision numbers left in `component-metadata.json`. Build the release files.
10. Add one decision-log entry and the tag `v1.0.1`, and run the fresh-clone gate.
11. Push only with the owner's yes.

Historical plans and log entries that mention `docs-site/` stay as they are.

**C. Docs repo agent**, from [PROMPT.md](2026-10-03-docs-site-move/PROMPT.md) and [HANDOVER.md](2026-10-03-docs-site-move/HANDOVER.md):

1. Import the hand-written pages from tag `v1.0.0`, the last commit that has them.
2. Add `import_reference.py` and import the export of `v1.0.1`.
3. Fix the two links to BEMGen on GitHub.
4. Point *Getting started* to the Releases page.
5. Pass the strict build and add the Pages workflow.
6. Push with the owner's yes, then check the live site.
7. Create the release `v1.0.1` with the release files, with the owner's yes.

## Acceptance

- **BEMGen:**
  - `docs-site/`, `mkdocs.yml`, and `scripts/docs-site/` are gone;
  - `docs-site` is mentioned only in historical plans and in the log;
  - `scripts/verify.ps1` passes, and the fresh clone of `v1.0.1` passes;
  - the export and the release files hold every file listed above;
  - the exported developer pages have no link into the private repository, and every redaction is listed.
- **Docs repo:**
  - `mkdocs build --strict` passes locally and in Actions, and the Pages URL serves both parts;
  - no page links to a path inside BEMGen;
  - the release `v1.0.1` has the four files, and their checksums match;
  - its `sync-docs` reports the site up to date with BEMGen `v1.0.1`.
