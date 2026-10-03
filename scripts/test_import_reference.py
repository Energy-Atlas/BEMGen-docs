"""Checks of import_reference.py on a small export fixture: python -m unittest discover -s scripts -p "test_*.py"."""

import json
import re
import tempfile
import unittest
from pathlib import Path

import import_reference as ir


def _param(name, nick, cls="Param_Number", typ="Number", access="item", optional=False, default=None, description="d"):
    return {"name": name, "nickname": nick, "class": cls, "type": typ, "access": access, "optional": optional,
            "default": default or [], "description": description}


SAMPLE = {
    "objects": [
        {"kind": "component", "class": "PerimeterCoreComponent", "panel": "3 Simplify", "name": "Perimeter Core", "nickname": "Z2",
         "guid": "6a86b976-c838-427f-93a7-344dcc2c18ce", "description": "Perimeter zones | core <ADR-008>.", "exposure": "primary",
         "exposure_rank": 2, "icon": "PerimeterCoreComponent.png", "obsolete": False,
         "inputs": [_param("Plan", "Plan", "PlanParameter", "Plan"), _param("Depth", "D", default=["4.57"])],
         "outputs": [_param("Floor", "Floor", "FloorParameter", "Floor")]},
        {"kind": "component", "class": "LinearPlanComponent", "panel": "2 Generate", "name": "Linear Plan Generator", "nickname": "Lin",
         "guid": "0f0c5b0e-1111-4c4c-9c9c-222233334444", "description": "A linear plan.", "exposure": "primary",
         "exposure_rank": 2, "icon": "LinearPlanComponent.png", "obsolete": False,
         "inputs": [], "outputs": [_param("Plan", "Plan", "PlanParameter", "Plan")]},
        {"kind": "parameter", "class": "PlanParameter", "panel": "0 Info", "name": "Plan", "nickname": "Plan",
         "guid": "fca85387-7aaf-41fe-9654-382b2980f18f", "description": "A plan.", "exposure": "hidden", "exposure_rank": 0,
         "icon": "PlanParameter.png", "obsolete": False},
        {"kind": "parameter", "class": "FloorParameter", "panel": "0 Info", "name": "Floor", "nickname": "Floor",
         "guid": "15a085fa-f308-46b7-93e6-88a7a85e6a89", "description": "A floor.", "exposure": "hidden", "exposure_rank": 0,
         "icon": "FloorParameter.png", "obsolete": False},
    ],
    "examples": {"end-to-end.gh": ["6a86b976-c838-427f-93a7-344dcc2c18ce"], "linear-plan.gh": ["0f0c5b0e-1111-4c4c-9c9c-222233334444"]},
}
SHOTS = {"linear-plan-plan.png", "linear-plan-building.png", "canvas/end-to-end.png"}
NAV = ["developer/index.md", {"Project rules": ["developer/GLOBAL.md"]}, {"Decisions": ["developer/decisions/decision-log.md"]}]
SOURCE = {"version": "1.0.1", "commit": "b587e63af36f654dbd9cf0d366a365be1f9d036e", "dirty": False, "rhino": "8.25", "date": "2026-10-03T22:41:33Z", "gaps": 0}
MKDOCS = """site_name: BEMGen
nav:
  - Home: index.md
  # BEGIN generated developer nav
  - Developer:
      - developer/index.md
  # END generated developer nav
"""


def write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_export(folder: Path) -> None:
    write(folder / "component-metadata.json", json.dumps(SAMPLE))
    write(folder / "developer-nav.json", json.dumps(NAV))
    write(folder / "redactions.txt", "")
    write(folder / "source.json", "\ufeff" + json.dumps(SOURCE))
    for o in SAMPLE["objects"]:
        write(folder / "icons" / o["icon"])
    for f in SHOTS:
        write(folder / "screenshots" / f)
    write(folder / "developer" / "GLOBAL.md", "# Rules\n")
    write(folder / "developer" / "decisions" / "decision-log.md", "# Log\n")


def make_repo(folder: Path) -> None:
    write(folder / "mkdocs.yml", MKDOCS)
    write(folder / "docs" / "index.md", "# Home\n")
    write(folder / "docs" / "developer" / "index.md", "# Hand-written\n")
    write(folder / "docs" / "developer" / "old" / "gone.md")
    write(folder / "docs" / "user" / "components" / "removed-panel.md")
    write(folder / "docs" / "assets" / "icons" / "RemovedComponent.png")
    write(folder / "docs" / "assets" / "screenshots" / "canvas" / "removed.png")


class RenderTests(unittest.TestCase):
    def test_slug_matches_markdown_toc(self):
        self.assertEqual(ir.slug("Single Zone per Floor"), "single-zone-per-floor")
        self.assertEqual(ir.slug("Convert2BEM"), "convert2bem")
        self.assertEqual(ir.slug("BEMGen Info"), "bemgen-info")

    def test_panel_pages_drop_the_ordering_number(self):
        self.assertEqual(ir.panel_page("1 Program Presets"), "program-presets.md")
        self.assertEqual(ir.panel_title("5 Convert"), "Convert")

    def test_example_stem_follows_the_examples_spec(self):
        self.assertEqual(ir.example_stem("Linear Plan Generator"), "linear-plan")
        self.assertEqual(ir.example_stem("Stair Bay Bar"), "stair-bay-bar")

    def test_cells_escape_pipes_and_angle_brackets(self):
        self.assertEqual(ir.cell("a | b <c>\n d"), "a \\| b &lt;c&gt; d")

    def test_renders_index_and_one_page_per_panel(self):
        pages = ir.render(SAMPLE, SHOTS)
        self.assertEqual(sorted(pages), ["generate.md", "index.md", "info.md", "simplify.md"])
        self.assertEqual(pages, ir.render(SAMPLE, SHOTS))

    def test_component_entry_holds_icon_guid_tables_and_example(self):
        page = ir.render(SAMPLE, SHOTS)["simplify.md"]
        self.assertIn("## Perimeter Core", page)
        self.assertIn("../../assets/icons/PerimeterCoreComponent.png", page)
        self.assertIn("`6a86b976-c838-427f-93a7-344dcc2c18ce`", page)
        self.assertIn("| Depth | `D` | Number | item | no | `4.57` | d |", page)
        self.assertIn("| Plan | `Plan` | [Plan](info.md#plan) | item | no | – | d |", page)
        self.assertIn("`end-to-end.gh` ([canvas](../../assets/screenshots/canvas/end-to-end.png))", page)
        self.assertIn("Perimeter zones | core &lt;ADR-008&gt;.", page)

    def test_generator_embeds_only_the_screenshots_the_export_has(self):
        page = ir.render(SAMPLE, SHOTS)["generate.md"]
        self.assertIn("../../assets/screenshots/linear-plan-plan.png", page)
        self.assertIn("../../assets/screenshots/linear-plan-building.png", page)
        self.assertNotIn("**Screenshots**", ir.render(SAMPLE, set())["generate.md"])
        self.assertNotIn("canvas/linear-plan.png", page)

    def test_links_are_relative(self):
        for name, page in ir.render(SAMPLE, SHOTS).items():
            for target in re.findall(r"\]\(([^)]*)\)", page):
                self.assertFalse(re.match(r"^([a-zA-Z]:|/|\\\\|https?:)", target), "%s links %s" % (name, target))


class NavTests(unittest.TestCase):
    def test_developer_nav_block_nests_sections(self):
        self.assertEqual(
            ir.developer_nav(NAV),
            "  # BEGIN generated developer nav\n"
            "  - Developer:\n"
            "      - developer/index.md\n"
            "      - Project rules:\n"
            "          - developer/GLOBAL.md\n"
            "      - Decisions:\n"
            "          - developer/decisions/decision-log.md\n"
            "  # END generated developer nav\n",
        )

    def test_unusual_section_titles_are_quoted(self):
        self.assertIn('- "Notes: draft":', ir.developer_nav([{"Notes: draft": ["developer/a.md"]}]))

    def test_replace_nav_keeps_the_rest_of_the_file(self):
        text = MKDOCS + "extra: 1\n"
        out = ir.replace_nav(text, ir.developer_nav(NAV))
        self.assertTrue(out.startswith("site_name: BEMGen\nnav:\n  - Home: index.md\n"))
        self.assertTrue(out.endswith("          - developer/decisions/decision-log.md\n  # END generated developer nav\nextra: 1\n"))
        self.assertEqual(out, ir.replace_nav(out, ir.developer_nav(NAV)))

    def test_replace_nav_needs_the_markers(self):
        with self.assertRaises(ValueError):
            ir.replace_nav("nav:\n  - Home: index.md\n", ir.developer_nav(NAV))


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.export = Path(self.tmp.name) / "export"
        self.repo = Path(self.tmp.name) / "repo"
        make_export(self.export)
        make_repo(self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_export_has_nothing_missing(self):
        self.assertEqual(ir.check_export(self.export), [])

    def test_missing_files_and_icons_are_reported(self):
        (self.export / "developer-nav.json").unlink()
        self.assertEqual(ir.check_export(self.export), ["developer-nav.json"])
        make_export(self.export)
        (self.export / "icons" / "PlanParameter.png").unlink()
        self.assertEqual(ir.check_export(self.export), ["icons/PlanParameter.png"])

    def test_import_replaces_the_generated_parts(self):
        ir.import_export(self.export, self.repo)
        docs = self.repo / "docs"
        self.assertEqual(ir.files_under(docs / "user" / "components"), {"generate.md", "index.md", "info.md", "simplify.md"})
        self.assertEqual(ir.files_under(docs / "assets" / "icons"), {o["icon"] for o in SAMPLE["objects"]})
        self.assertEqual(ir.files_under(docs / "assets" / "screenshots"), SHOTS)
        self.assertEqual(ir.files_under(docs / "developer"), {"index.md", "GLOBAL.md", "decisions/decision-log.md"})
        self.assertEqual((docs / "developer" / "index.md").read_text(encoding="utf-8"), "# Hand-written\n")
        self.assertEqual((docs / "index.md").read_text(encoding="utf-8"), "# Home\n")

    def test_import_writes_nav_and_source(self):
        ir.import_export(self.export, self.repo)
        config = (self.repo / "mkdocs.yml").read_text(encoding="utf-8")
        self.assertIn("      - Project rules:\n          - developer/GLOBAL.md\n", config)
        self.assertTrue(config.startswith("site_name: BEMGen\nnav:\n  - Home: index.md\n  # BEGIN generated developer nav\n"))
        self.assertEqual(json.loads((self.repo / "reference-source.json").read_text(encoding="utf-8")), SOURCE)

    def test_import_twice_changes_nothing(self):
        ir.import_export(self.export, self.repo)
        first = {f: (self.repo / f).read_bytes() for f in ir.files_under(self.repo)}
        ir.import_export(self.export, self.repo)
        self.assertEqual(first, {f: (self.repo / f).read_bytes() for f in ir.files_under(self.repo)})

    def test_public_content_check(self):
        docs = self.repo / "docs"
        self.assertEqual(ir.public_content_problems(docs), [])
        write(docs / "user" / "a.md", "See https://github.com/EnvironmentalSystemsLab/BEMGen/blob/main/x.md\n")
        write(docs / "developer" / "b.md", "Mail someone@example.org.\nPaths `C:\\Users\\<name>` and C:\\Users\\jdoe\\x.\n")
        self.assertEqual(
            ir.public_content_problems(docs),
            ["developer/b.md:1: e-mail address", "developer/b.md:2: user-profile path", "user/a.md:1: private repository link"],
        )


if __name__ == "__main__":
    unittest.main()
