# Handover prompt for the docs repository agent

Paste this into an agent session that has a clone of `energy-atlas/BEMGen-docs` as its working directory. Do this once BEMGen `v1.0.1` is built, its docs export is written, and its release files are in `D:\BEMGen\dist\release\1.0.1\` (step B of the move plan). Fill in the export folder.

```text
You are taking over the BEMGen documentation site and its releases, in this new public repository, energy-atlas/BEMGen-docs. The site is published on GitHub Pages at https://energy-atlas.github.io/BEMGen-docs/.

Before you change anything, read these three files in the private BEMGen checkout at D:\BEMGen. Read only these and the files they name; do not copy anything else from BEMGen.
- docs/plans/2026-10-03-docs-site-move/HANDOVER.md, which is your brief: what this repository is, who owns which files, the rules, the first task, and later versions
- docs/plans/2026-10-03-docs-site-move.md, the move plan and the docs export it defines
- docs/plans/2026-10-03-docs-site-move/docs-repo-sync-docs-SKILL.md, which becomes this repository's .claude/skills/sync-docs/SKILL.md

Inputs:
- hand-written pages: BEMGen tag v1.0.0, imported with git archive
- docs export of BEMGen v1.0.1: <export folder>
- release files: D:\BEMGen\dist\release\1.0.1\

Your first task is HANDOVER.md "First task: import, deploy, release", steps 1 to 8, in its order:
1. Import the pages.
2. Edit mkdocs.yml.
3. Write scripts/import_reference.py with its test, and import the export.
4. Fix the hand-written pages.
5. Simplify the scripts.
6. Add the repository files.
7. Pass mkdocs build --strict locally.
8. Add the Pages workflow, which uses GitHub Actions and never mkdocs gh-deploy.

Then stop. Show me the commits, the build output, and the export's redactions.txt, and wait for my yes before pushing. After my yes, push without force, watch the workflow until it deploys, and check the live site. Then ask me before step 10, the v1.0.1 release.

Rules:
- Commit as the configured git user, with messages of the form type(scope): summary in lower case. Never add co-author trailers, or agent, model, or tool names.
- Never force-push.
- Never edit the BEMGen repository.
- Never hand-edit generated files (the component reference, icons, screenshots, the developer pages except developer/index.md, or the generated nav block).
- Never put a link into the private BEMGen repository on any page.

If the repository is not empty, Settings → Pages is not set to GitHub Actions, or an input above is missing, ask me before you go on.
```
