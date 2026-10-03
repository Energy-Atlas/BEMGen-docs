# Handover: the BEMGen documentation site

This file goes to the root of the public repository `energy-atlas/BEMGen-docs`. It tells whoever works there, person or agent, what the repository is, where its content comes from, the rules, and the first task: deployment to GitHub Pages and the first release.

## What this repository is

The public documentation and the release files of **BEMGen**, a Grasshopper plugin for Rhino 8 that builds building energy models at several levels of detail.

- **The site** is built with MkDocs and the Material theme, and published on GitHub Pages at `https://energy-atlas.github.io/BEMGen-docs/`. It has a user part (guide and component reference) and a developer part (architecture, decisions, plans, research, and project rules).
- **The releases** on this repository's GitHub Releases carry the plugin for each version:
  - the `.gha` with its libraries;
  - the Yak package;
  - the example definitions;
  - checksums.

The plugin's code, tests, examples, and the sources of the developer pages live in the BEMGen repository, which is **private**. So:

- this repository never checks BEMGen out during deployment;
- no page links to a file inside BEMGen;
- everything that comes from BEMGen arrives as a **docs export**: a folder written by BEMGen's `scripts/docs-export/export.ps1` on a lab machine with Rhino 8. It is imported here by `scripts/import_reference.py` and committed.

The site was moved here from BEMGen's `docs-site/` (BEMGen decisions D-117 and D-118). BEMGen keeps no copy of the hand-written pages.

## Who owns what

| Path | Owner | How it changes |
| --- | --- | --- |
| `docs/index.md`, `docs/user/*.md`, `docs/developer/index.md`, `docs/assets/stylesheets/` | This repository | Edited here |
| `docs/user/components/`, `docs/assets/icons/`, `docs/assets/screenshots/` | Generated from the export | `import_reference.py` only, never by hand |
| `docs/developer/**` except `index.md` | BEMGen (`docs/`, `GLOBAL.md`, `AGENTS.md`) | `import_reference.py` only. A fix to a developer page is made in BEMGen, then exported. |
| The *Developer* block of `mkdocs.yml`, between its marker comments | Generated from `developer-nav.json` | `import_reference.py` only |
| `reference-source.json` | Generated from the export's `source.json` | `import_reference.py` only |
| Release files | BEMGen's `scripts/package-release.ps1` | Uploaded to a GitHub Release, never committed |
| Everything else (`mkdocs.yml` outside the marked block, `scripts/`, workflow, README, ...) | This repository | Edited here |

## Rules (copy them into `AGENTS.md`)

1. **Commits:**
   - format `type(scope): imperative summary in lower case`, with the types `feature`, `fix`, `refactor`, `test`, `docs`, `build`, `chore`, `perf`; scopes such as `site`, `user`, `reference`, `developer`, `deploy`, `release`, `repo`;
   - authored by the configured git user;
   - no agent, model, provider, or tool names, no attribution footers, no `Co-Authored-By` trailers for tools.
2. **Pushing and releasing:**
   - push and create releases only with the owner's explicit yes, given for that action;
   - never force-push, and never delete or move a pushed tag;
   - the owner is Cheng Xuan Li.
3. **Generated content:** never hand-edit anything the table above marks as generated.
4. **The build gate:**
   - `mkdocs build --strict` must pass before every push;
   - every broken link, missing anchor, or page left out of the navigation is an error. Keep the `validation:` block of `mkdocs.yml`;
   - keep the exact versions in `requirements.txt`. MkDocs 1.6 with Material 9.7 is what the site was built and checked with. Material warns that MkDocs 2.0 drops plugins and themes, so never upgrade to it without the owner.
5. **Public content:**
   - no link to a path inside the private BEMGen repository; its home page may be named only as private;
   - no credentials;
   - the export already redacts e-mail addresses and user-profile paths (`C:\Users\<name>`) from the developer pages and lists them in `redactions.txt`. Check that list at each import. Lab paths such as `D:\BEMGen` may appear on developer pages; they are instructions for the lab machine.
6. **The content follows the plugin:**
   - when a page disagrees with BEMGen's code or generated reference, the page is wrong;
   - decisions are made and recorded in BEMGen.
7. **Versions:**
   - the site describes the version named in `reference-source.json`;
   - a release here has the tag `v<plugin version>` and the files of exactly that BEMGen version;
   - backward compatibility is not required yet, so the docs follow the current version only.

## Layout to reach

```text
mkdocs.yml                 site configuration; the Developer nav block is generated
requirements.txt           pinned MkDocs packages
reference-source.json      the BEMGen version and commit the generated parts describe
docs/                      the site (MkDocs's default docs_dir)
  index.md, user/, developer/index.md, assets/stylesheets/   hand-written
  user/components/, assets/icons/, assets/screenshots/       generated
  developer/** (except index.md)                             generated
scripts/
  import_reference.py      imports an export (from BEMGen's component_reference.py)
  test_import_reference.py
  build.ps1, serve.ps1     local strict build and server (Windows)
.github/workflows/pages.yml
.claude/skills/sync-docs/SKILL.md
README.md, LICENSE, AGENTS.md, CLAUDE.md, HANDOVER.md, .gitignore
```

## First task: import, deploy, release

Before you begin, check three things:

- the owner has created this repository empty and set *Settings → Pages → Source* to *GitHub Actions*;
- BEMGen's version 1.0.1 is built: tag `v1.0.1` in `D:\BEMGen`;
- the export folder and the release folder `D:\BEMGen\dist\release\1.0.1\` exist. The prompt names the export folder; its format is described in BEMGen's `scripts/docs-export/README.md`.

If any of these is missing, stop and ask.

1. **Import the hand-written pages and the renderer** from BEMGen tag `v1.0.0`. It is the last commit that has them; they did not change after it. Use `git archive`, not a copy of a working tree:

   ```bash
   git -C /d/BEMGen archive v1.0.0 docs-site mkdocs.yml scripts/docs-site/component_reference.py scripts/docs-site/test_component_reference.py scripts/docs-site/build.ps1 scripts/docs-site/serve.ps1 scripts/docs-site/requirements.txt LICENSE | tar -x -C <empty scratch folder>
   ```

   Arrange the files:
   - `docs-site/` becomes `docs/`;
   - `requirements.txt` goes to the root;
   - the scripts go to `scripts/`.

   Delete the old generated folders (`docs/user/components/`, `docs/assets/icons/`, `docs/assets/screenshots/`), because step 3 regenerates them. Commit with the content otherwise unchanged (`docs(site): import the documentation site from bemgen v1.0.0`). Builds may fail at this commit; that is expected.
2. **`mkdocs.yml`:**
   - drop `docs_dir: docs-site`;
   - set `site_url: https://energy-atlas.github.io/BEMGen-docs/`;
   - set `repo_url: https://github.com/energy-atlas/BEMGen-docs` and `repo_name: energy-atlas/BEMGen-docs`;
   - keep `edit_uri: ""`;
   - replace the *Developer* section with a block between two marker comments (`# BEGIN generated developer nav` / `# END generated developer nav`), holding only `developer/index.md` for now;
   - rewrite the header comment: plain `mkdocs build --strict`, with no assembly step.
3. **`scripts/import_reference.py --export <folder>`**, from `component_reference.py`:
   - render `docs/user/components/` from `component-metadata.json`, as before;
   - replace `docs/assets/icons/` with the export's `icons/`, and `docs/assets/screenshots/` with its `screenshots/`;
   - replace `docs/developer/**` except `index.md` with the export's `developer/`;
   - write the *Developer* nav block from `developer-nav.json` (landing page, *Project rules*, then *Architecture*, *Decisions*, *Plans*, *Research*, *Development*, and *Specifications*);
   - write `reference-source.json` from `source.json`;
   - remove files the export no longer has.

   Adapt the test to a small export fixture. Run it on the v1.0.1 export, and read `redactions.txt` before you commit (`docs(reference): import the bemgen v1.0.1 export`).
4. **Fix the hand-written pages:**

   | Page | Now | Change to |
   | --- | --- | --- |
   | `docs/index.md` | Link to `https://github.com/EnvironmentalSystemsLab/BEMGen` as the source code | The source is in BEMGen, private for now, access on request. Downloads are on this repository's Releases page. |
   | `docs/user/workflow.md` | Link to `.../BEMGen/blob/main/scripts/idd-check/README.md` | The developer page that describes the IDD check, if the export has one; otherwise one sentence and no link |
   | `docs/user/getting-started.md` | Installation from a build or a local Yak package | Download from `https://github.com/energy-atlas/BEMGen-docs/releases`: the `.yak` (drag onto Rhino 8) or the zip (unpack into `%APPDATA%\Grasshopper\Libraries\BEMGen\`, then unblock it); the examples zip. Building from source needs access to BEMGen. |
   | `docs/user/typologies.md`, `example-end-to-end.md` | Example file names | Say that the files are in the examples zip of the release |
   | `docs/developer/index.md` | Says its pages come from `docs/` at build time and links to BEMGen on GitHub | Say that the pages come from BEMGen's `docs/`, `GLOBAL.md`, and `AGENTS.md` through the docs export; that links to source files appear as plain paths because the code is private; and how to propose a fix (an issue here) |

   The user pages' links to `../developer/...` stay as they are: the paths are the same. Afterwards no page may contain `github.com/EnvironmentalSystemsLab/BEMGen/` followed by a path.
5. **Scripts:**
   - make `scripts/build.ps1` and `scripts/serve.ps1` run `mkdocs build --strict` and `mkdocs serve -a 127.0.0.1:8000` on the root `mkdocs.yml`, with no assembly step;
   - keep the `-Python` parameter and its message about a virtual environment outside the repository.
6. **Repository files:**
   - `README.md`: what the site is, its URL, the Releases page, the local build and serve commands, and how an export is imported;
   - `LICENSE`: the imported MIT licence;
   - `.gitignore`: `site/`, `__pycache__/`, `.venv/`;
   - `AGENTS.md`: the rules and ownership table above, plus the commands;
   - `CLAUDE.md`: one line, `@AGENTS.md`;
   - `.claude/skills/sync-docs/SKILL.md`: the draft handed over with this file;
   - `HANDOVER.md`: this file.
7. **Strict build locally:**
   - use a virtual environment outside the repository: `python -m venv <folder>`, then `<folder>\Scripts\python -m pip install -r requirements.txt`;
   - run `scripts/build.ps1 -Python <folder>\Scripts\python.exe`. It must pass with no warnings;
   - serve the site and look at the landing page, one user page, one reference page with its icons and screenshots, and the decision log.
8. **Workflow** `.github/workflows/pages.yml`. Before writing it, check the current major versions of the four actions:

   ```yaml
   name: Pages
   on:
     push:
       branches: [main]
     pull_request:
     workflow_dispatch:
   permissions:
     contents: read
     pages: write
     id-token: write
   concurrency:
     group: pages
     cancel-in-progress: false
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.14"
             cache: pip
         - run: pip install -r requirements.txt
         - run: mkdocs build --strict
         - uses: actions/upload-pages-artifact@v3
           if: github.event_name != 'pull_request'
           with:
             path: site
     deploy:
       if: github.event_name != 'pull_request'
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - id: deployment
           uses: actions/deploy-pages@v4
   ```

   Pull requests build strictly but do not deploy. Never use `mkdocs gh-deploy`: there is no `gh-pages` branch.
9. **Push and check:**
   - show the owner the commits, the local build result, and `redactions.txt`, and push only after their yes;
   - watch the workflow until both jobs pass;
   - open the Pages URL and check that both parts, the navigation, the search, the icons, and the screenshots load.
10. **Release `v1.0.1`**, only after the owner's yes for it:
    1. check `SHA256SUMS.txt` against the three files it lists in `D:\BEMGen\dist\release\1.0.1\`;
    2. create the release with the tag `v1.0.1` on `main`, the title `BEMGen 1.0.1`, and short notes: what the version is, the install steps from *Getting started*, and a link to the site;
    3. upload the files, using `gh release create` if the GitHub CLI is installed and signed in. Otherwise give the owner the exact steps for the web page;
    4. check that the *Getting started* links resolve.

## Each later version

1. BEMGen builds the version, runs `export.ps1` and `package-release.ps1`, and tells you the export folder.
2. Run `sync-docs`.
3. Import the export, and fix the hand-written pages the plan lists.
4. Pass the strict build and push with the owner's yes.
5. Create the release `v<version>` with the owner's yes.

## Open items for a person

- Look at the deployed site in a browser: theme, dark mode, and the images at phone width.
- Install from the release on a clean Rhino 8: the `.yak`, then the zip on another machine or profile, and open one example.
- The screenshots show Rhino's viewport at the time of capture. A person still has to check the window fills for transparency artefacts, which BEMGen lists as open.
