# Developer documentation

!!! abstract "You are in the developer documentation"
    This part of the site is for people who change BEMGen: its code, its research rules, or its documents. If you want to build energy models with BEMGen, go to the [user guide](../user/index.md).

Every page of this section except this one comes from BEMGen's `docs/` folder and the `GLOBAL.md` and `AGENTS.md` at its root, through the docs export made with each BEMGen version. BEMGen's code is private for now, so links to source files outside `docs/` appear as plain paths, such as `src/Lod.Core`.

To propose a fix to a page, open an [issue](https://github.com/energy-atlas/BEMGen-docs/issues) in this site's repository. The fix is made in BEMGen and reaches this site with its next export.

## Where to start { .ea-strip data-index="01" data-note="Six entry points" }

<div class="grid cards compact" markdown>

1.  [Project rules](GLOBAL.md)

    The non-negotiable scientific, architecture, quality, and git rules, and the [working instructions](AGENTS.md) for contributors and coding agents (commands, architecture boundaries, commit format, stage workflow).

2.  [Pipeline](architecture/pipeline.md)

    Every step of the pipeline, its types, components, and decisions.

3.  [Domain model](architecture/domain-model.md)

    The core types, units, and diagnostic codes; [validation](architecture/validation.md): every check and tolerance; the converters [Convert2BEM](architecture/convert2bem.md) and [Convert2IDF](architecture/convert2idf.md).

4.  [Decision log](decisions/decision-log.md)

    Every project decision, newest at the bottom, and the architecture decision records (ADR-001 to ADR-015 and ADR-017) it links.

5.  [Implementation roadmap](plans/2026-09-30-implementation-roadmap.md)

    The stages and their progress log; each stage's design note is in *Plans*.

6.  [Research brief](LOD_geometric_zoning_equivalence_research_brief.md)

    The research questions, levels of detail, and equivalence rules, with the [repository specification](LOD_grasshopper_plugin_repository_spec.md) and its original architecture.

</div>

## Repository layout { .ea-strip data-index="02" data-note="BEMGen, private" }

| Folder | Content |
| --- | --- |
| `src/Lod.Core` | Pipeline types, presets, loads, schedules, simplifiers, floor aggregators, validation; no Rhino dependency |
| `src/Lod.Generators` | The eighteen plan generators |
| `src/Lod.Export` | *Convert2IDF* (the IDF writer) |
| `src/Lod.Grasshopper` | Components, parameters, previews, *Convert2BEM*, icons |
| `tests/` | Unit, invariant, snapshot, and integration tests, run with `dotnet test` without Rhino |
| `docs/` | Architecture, decisions, plans, research, development guides (the source of this section) |
| `scripts/` | `verify.ps1` (the merge gate), `rhino-smoke/` (headless Rhino check), `idd-check/`, `docs-export/` (the export of this site's generated parts), `package-yak.ps1` and `package-release.ps1` (the release files), `make_icons.py` |
| `examples/` | Example Grasshopper definitions |

## Build, test, and document { .ea-strip data-index="03" data-note="Lab machine" }

```powershell
dotnet build BEMGen.sln -c Release
dotnet test BEMGen.sln -c Release
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docs-export/export.ps1 -OutDir <folder outside the repository>
```

`scripts/verify.ps1` must print `VERIFY PASSED` before every merge. `scripts/docs-export/export.ps1` runs on a machine with Rhino 8 and writes the docs export: the pages of this section, the component reference, the icons, and the screenshots. This site's repository imports it and builds the site with `mkdocs build --strict`. Whether the documentation still matches the code is checked with the project skill `sync-docs` (`.claude/skills/sync-docs/SKILL.md`), run at every stage close-out.
