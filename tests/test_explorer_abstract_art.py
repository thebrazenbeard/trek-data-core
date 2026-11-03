"""Public original-art backgrounds: deterministic, non-narrative and allowlisted."""

import importlib.util
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("explorer_art_build", ROOT / "tools/build_explorer_abstract_art.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class ExplorerAbstractArtTests(unittest.TestCase):
    def test_all_five_assets_exactly_rebuild_from_accepted_renderer(self):
        paths = BUILD.expected_art()
        self.assertEqual(len(paths), 5)
        for path, expected in paths.items():
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertFalse(path.is_symlink())
                self.assertEqual(path.read_bytes(), expected)
                self.assertLess(len(expected), 10000)

    def test_safe_official_art_distinction_and_xml_vocabulary(self):
        allowed = {"svg", "rect", "circle", "path", "text"}
        for path, data in BUILD.expected_art().items():
            with self.subTest(path=path.name):
                source = data.decode("utf-8")
                self.assertIn("ABSTRACT PLACEHOLDER", source)
                self.assertIn("NOT OFFICIAL ART", source)
                self.assertNotRegex(source, r"(?i)(?:<script|<foreignobject|<image|<use|xlink:|href=|url\()")
                root = ET.fromstring(source)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertTrue(all(node.tag.split("}")[-1] in allowed for node in root.iter()))

    def test_css_uses_exact_local_categories_no_dynamic_external_urls(self):
        css = (ROOT / "explorer/app.css").read_text(encoding="utf-8")
        for medium, (slug, _) in BUILD.CATEGORIES.items():
            with self.subTest(medium=medium):
                class_suffix = medium.lower()
                self.assertIn(f".artwork-slot.artwork-{class_suffix} {{ background-image: url('./art-original-{slug}.svg'); }}", css)
        self.assertEqual(set(re.findall(r"art-original-[a-z-]+\.svg", css)),
                         {path.name for path in BUILD.expected_art()})
        js = (ROOT / "explorer/app.js").read_text(encoding="utf-8")
        self.assertIn("Artwork not sourced · original abstract", js)
        self.assertIn("const source = artworkState.enabled ?", js,
                      "opt-in rights gate must remain distinct from generic placeholders")


if __name__ == "__main__":
    unittest.main()
