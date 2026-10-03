# Working in BEMGen-docs

The public documentation site and the release files of BEMGen, a Grasshopper plugin for Rhino 8. The site is built with MkDocs and the Material theme and published at <https://energy-atlas.github.io/BEMGen-docs/>; the releases are on this repository's GitHub Releases. The plugin's code and the sources of the developer pages are in the BEMGen repository, which is private. Everything taken from BEMGen arrives as a **docs export** and is imported by `scripts/import_reference.py`. Background and the first task: [HANDOVER.md](HANDOVER.md).

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

## Rules

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
8. **Deployment:** GitHub Actions only (`.github/workflows/pages.yml`); never `mkdocs gh-deploy`, there is no `gh-pages` branch. Pull requests build strictly but do not deploy.

## Commands

Windows PowerShell, with a virtual environment outside the repository:

```powershell
python -m venv <folder>
<folder>\Scripts\python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -Python <folder>\Scripts\python.exe   # mkdocs build --strict
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/serve.ps1 -Python <folder>\Scripts\python.exe   # http://127.0.0.1:8000/
python scripts/import_reference.py --export <export folder>                                                # import a docs export
python -m unittest discover -s scripts -p "test_*.py"                                                       # tests of the import
```

After a new BEMGen version: run the `sync-docs` skill (`.claude/skills/sync-docs/SKILL.md`), import the export, fix the hand-written pages, pass the strict build, and push and release only with the owner's yes.
