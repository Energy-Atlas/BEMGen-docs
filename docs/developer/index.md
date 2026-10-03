# Developer documentation

!!! abstract "You are in the developer documentation"
    This part of the site is for people who change BEMGen: its code, its research rules, or its documents. If you want to build energy models with BEMGen, go to the [user guide](../user/index.md).

Every page of this section except this one is taken from the repository's `docs/` folder (and `GLOBAL.md` and `AGENTS.md` at its root) each time the site is built. They are never copied into `docs-site/`: edit them in `docs/`, and links to source files outside `docs/` lead to the repository on GitHub.

## Where to start

1. [Project rules](GLOBAL.md): the non-negotiable scientific, architecture, quality, and git rules, and the [working instructions](AGENTS.md) for contributors and coding agents (commands, architecture boundaries, commit format, stage workflow).
2. [Pipeline](architecture/pipeline.md): every step of the pipeline, its types, components, and decisions.
3. [Domain model](architecture/domain-model.md): the core types, units, and diagnostic codes; [validation](architecture/validation.md): every check and tolerance; the converters [Convert2BEM](architecture/convert2bem.md) and [Convert2IDF](architecture/convert2idf.md).
4. [Decision log](decisions/decision-log.md): every project decision, newest at the bottom, and the architecture decision records (ADR-001 to ADR-015) it links.
5. [Implementation roadmap](plans/2026-09-30-implementation-roadmap.md): the stages and their progress log; each stage's design note is in *Plans*.
6. [Research brief](LOD_geometric_zoning_equivalence_research_brief.md) and [repository specification](LOD_grasshopper_plugin_repository_spec.md): the research questions, levels of detail, equivalence rules, and the original architecture.

## Repository layout

| Folder | Content |
| --- | --- |
| `src/Lod.Core` | Pipeline types, presets, loads, schedules, simplifiers, floor aggregators, validation; no Rhino dependency |
| `src/Lod.Generators` | The eighteen plan generators |
| `src/Lod.Export` | *Convert2IDF* (the IDF writer) |
| `src/Lod.Grasshopper` | Components, parameters, previews, *Convert2BEM*, icons |
| `tests/` | Unit, invariant, snapshot, and integration tests, run with `dotnet test` without Rhino |
| `docs/` | Architecture, decisions, plans, research, development guides (the source of this section) |
| `docs-site/` | The hand-written pages of this site and the generated component reference |
| `scripts/` | `verify.ps1` (the merge gate), `rhino-smoke/` (headless Rhino check), `idd-check/`, `docs-site/` (this site), `package-yak.ps1`, `make_icons.py` |
| `examples/` | Example Grasshopper definitions |

## Build, test, and document

```powershell
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-site/build.ps1 -Python <venv>\Scripts\python.exe
```

`scripts/verify.ps1` must print `VERIFY PASSED` before every merge; `scripts/docs-site/build.ps1` builds this site with `mkdocs build --strict`. How the site is assembled and served: [`scripts/docs-site/README.md`](https://github.com/EnvironmentalSystemsLab/BEMGen/blob/main/scripts/docs-site/README.md). Whether the documentation still matches the code is checked with the project skill `sync-docs` (`.claude/skills/sync-docs/SKILL.md`), run at every stage close-out.
