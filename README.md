# BEMGen documentation

The documentation site and the releases of **BEMGen**, a Grasshopper plugin for Rhino 8 that builds building energy models at several levels of detail.

- **Site:** <https://energy-atlas.github.io/BEMGen-docs/>, with a user guide, the reference of every component, and the developer documentation. It is built with MkDocs and the Material theme and deployed to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`.
- **Downloads:** the [Releases page](https://github.com/energy-atlas/BEMGen-docs/releases). Each release `v<version>` has the plugin as a Yak package and as a zip, the example definitions, and their checksums. Installation: [Getting started](https://energy-atlas.github.io/BEMGen-docs/user/getting-started/).

BEMGen's source code is in its own repository, which is private for now. The site describes the BEMGen version named in `reference-source.json`.

## Build and serve locally

Install the pinned packages into a virtual environment outside this repository, then build strictly or serve on `127.0.0.1:8000` (Windows PowerShell):

```powershell
python -m venv <folder>
<folder>\Scripts\python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -Python <folder>\Scripts\python.exe
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/serve.ps1 -Python <folder>\Scripts\python.exe
```

`build.ps1` runs `mkdocs build --strict` into `site/`; every broken link, missing anchor, or page left out of the navigation fails it.

## Import a docs export

The component reference, the icons, the screenshots, and the developer pages (except `docs/developer/index.md`) are generated from BEMGen. BEMGen's `scripts/docs-export/export.ps1` writes them into a *docs export* folder on a machine with Rhino 8; this repository imports it:

```powershell
python scripts/import_reference.py --export <export folder>
python -m unittest discover -s scripts -p "test_*.py"
```

The import replaces the generated folders, rewrites the *Developer* navigation block of `mkdocs.yml` and `reference-source.json`, and prints the export's `redactions.txt`, which is read before committing. Never edit the generated files by hand; see [AGENTS.md](AGENTS.md) for who owns which file.

## License

MIT, copyright 2026 Environmental Systems Lab ([LICENSE](LICENSE)).
