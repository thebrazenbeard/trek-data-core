import importlib.util
import json
import pathlib
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("art", ROOT / "tools/render_original_abstract_art.py")
ART = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ART)


class AbstractArtTests(unittest.TestCase):
    def test_original_cards_are_deterministic_and_parseable(self):
        for medium in ART.MEDIA:
            first = ART.render_card(f"directory:{medium}:42", medium, "A Source-Relative Title")
            self.assertEqual(first, ART.render_card(f"directory:{medium}:42", medium, "A Source-Relative Title"))
            root = ET.fromstring(first)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("NOT OFFICIAL ART", first)
            self.assertNotIn("http://www.w3.org/2000/svg" + "#", first)

    def test_untrusted_titles_are_data_not_markup(self):
        svg = ART.render_card("lead:0000", "EPISODE", '<script onload="alert(1)">&<img src=x>')
        root = ET.fromstring(svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("<img", svg)
        self.assertFalse(any(attribute.startswith("on") for el in root.iter() for attribute in el.attrib))
        self.assertIn("&lt;script", svg)

    def test_only_safe_svg_tag_and_attribute_vocabulary(self):
        allowed_tags = {"svg", "rect", "circle", "path", "text"}
        allowed_attrs = {"xmlns", "viewBox", "role", "aria-label", "width", "height", "rx", "fill", "cx", "cy", "r", "opacity", "d", "stroke", "stroke-width", "x", "y", "font-size", "font-family", "font-weight"}
        for medium in ART.MEDIA:
            svg = ART.render_card(f"safe:{medium}", medium, "Validated")
            root = ET.fromstring(svg)
            for el in root.iter():
                self.assertIn(el.tag.split("}")[-1], allowed_tags)
                self.assertTrue(set(el.attrib).issubset(allowed_attrs))
            self.assertNotIn("href=", svg)

    def test_control_chars_and_unknown_type_fail_closed(self):
        for args in [("", "EPISODE", "title"), ("id", "OTHER", "title"), ("id", "FILM", "bad\x00title"), ("id\n", "FILM", "title")]:
            with self.assertRaises(ValueError):
                ART.render_card(*args)

    def test_external_references_held_and_no_fake_work_binding(self):
        records = json.loads((ROOT / "records.json").read_text(encoding="utf-8"))
        self.assertEqual(records["artwork_release_effect"], "NONE")
        self.assertEqual(records["current_directory_binding"], "NONE")
        self.assertEqual(len(records["visual_candidates"]), 3)
        for candidate in records["visual_candidates"]:
            self.assertFalse(candidate["depicts_fictional_work"])
            self.assertNotIn(candidate["public_display_state"], {"CLEARED", "PUBLISHED"})
            if candidate["kind"] != "ORIGINAL_PROCEDURAL_PLACEHOLDER":
                self.assertIsNone(candidate["local_binary_sha256"])
                self.assertIsNone(candidate["asset_url"])


if __name__ == "__main__":
    unittest.main()
