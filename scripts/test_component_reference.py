"""Checks of component_reference.py on a small metadata sample: python -m unittest discover -s scripts/docs-site -p "test_*.py"."""

import re
import unittest

import component_reference as cr


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
        {"kind": "parameter", "class": "PlanParameter", "panel": "0 Info", "name": "Plan", "nickname": "Plan",
         "guid": "fca85387-7aaf-41fe-9654-382b2980f18f", "description": "A plan.", "exposure": "hidden", "exposure_rank": 0,
         "icon": "PlanParameter.png", "obsolete": False},
        {"kind": "parameter", "class": "FloorParameter", "panel": "0 Info", "name": "Floor", "nickname": "Floor",
         "guid": "15a085fa-f308-46b7-93e6-88a7a85e6a89", "description": "A floor.", "exposure": "hidden", "exposure_rank": 0,
         "icon": "FloorParameter.png", "obsolete": False},
    ],
    "examples": {"end-to-end.gh": ["6a86b976-c838-427f-93a7-344dcc2c18ce"]},
}


class ComponentReferenceTests(unittest.TestCase):
    def test_slug_matches_markdown_toc(self):
        self.assertEqual(cr.slug("Single Zone per Floor"), "single-zone-per-floor")
        self.assertEqual(cr.slug("Convert2BEM"), "convert2bem")
        self.assertEqual(cr.slug("BEMGen Info"), "bemgen-info")

    def test_panel_pages_drop_the_ordering_number(self):
        self.assertEqual(cr.panel_page("1 Program Presets"), "program-presets.md")
        self.assertEqual(cr.panel_title("5 Convert"), "Convert")

    def test_example_stem_follows_the_examples_spec(self):
        self.assertEqual(cr.example_stem("Linear Plan Generator"), "linear-plan")
        self.assertEqual(cr.example_stem("Stair Bay Bar"), "stair-bay-bar")

    def test_cells_escape_pipes_and_angle_brackets(self):
        self.assertEqual(cr.cell("a | b <c>\n d"), "a \\| b &lt;c&gt; d")

    def test_renders_index_and_one_page_per_panel(self):
        pages = cr.render(SAMPLE)
        self.assertEqual(sorted(pages), ["index.md", "info.md", "simplify.md"])
        self.assertEqual(pages, cr.render(SAMPLE))

    def test_component_entry_holds_icon_guid_tables_and_example(self):
        page = cr.render(SAMPLE)["simplify.md"]
        self.assertIn("## Perimeter Core", page)
        self.assertIn("../../assets/icons/PerimeterCoreComponent.png", page)
        self.assertIn("`6a86b976-c838-427f-93a7-344dcc2c18ce`", page)
        self.assertIn("| Depth | `D` | Number | item | no | `4.57` | d |", page)
        self.assertIn("| Plan | `Plan` | [Plan](info.md#plan) | item | no | – | d |", page)
        self.assertIn("`examples/end-to-end.gh`", page)
        self.assertIn("Perimeter zones | core &lt;ADR-008&gt;.", page)

    def test_links_are_relative(self):
        for name, page in cr.render(SAMPLE).items():
            for target in re.findall(r"\]\(([^)]*)\)", page):
                self.assertFalse(re.match(r"^([a-zA-Z]:|/|\\\\|https?:)", target), "%s links %s" % (name, target))


if __name__ == "__main__":
    unittest.main()
