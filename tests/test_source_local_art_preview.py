"""Tests for rights-safe, original, held source-local reference visuals."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("source_local_art_preview", ROOT / "tools/build_source_local_art_preview.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


class SourceLocalArtPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = mod.contract.build_inputs()
        cls.assets, cls.cards = mod.build_art(cls.inputs)
        cls.html = mod.render_page(cls.cards)
        cls.expected = mod.expected()

    def test_six_source_id_bound_original_assets(self):
        self.assertEqual(len(self.assets), 6)
        self.assertEqual(len(self.cards), 6)
        self.assertEqual({m: sum(r["medium"] == m for r in self.cards) for m in mod.APPROVED_MEDIA}, {"EPISODE": 2, "FILM": 2, "LITERATURE": 2})
        self.assertEqual(len({r["visual_seed_sha256"] for r in self.cards}), 6)
        self.assertEqual(len({r["asset_sha256"] for r in self.cards}), 6)
        for row in self.cards:
            self.assertEqual(row["identity_scope"], "SOURCE_LOCAL")
            self.assertEqual(row["verification_status"], "UNVERIFIED_METADATA")
            self.assertIsNone(row["edition_identifier"])
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertEqual(row["source_artwork_license_grant"], "NONE")
            self.assertTrue((mod.TARGET / row["asset_path"]).is_file())

    def test_generated_svgs_are_original_resource_free_and_safe(self):
        for name, data in self.assets.items():
            art = data.decode("utf-8")
            parsed = ET.fromstring(art)
            self.assertEqual(parsed.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertEqual({item.tag.split("}")[-1] for item in parsed.iter()}, {"svg", "rect", "circle", "path", "text"})
            self.assertIn("ABSTRACT PLACEHOLDER", art)
            self.assertIn("NOT OFFICIAL ART", art)
            for forbidden in ("<image", "<script", "<foreignObject", "href=", "url(", "data:"):
                self.assertNotIn(forbidden.lower(), art.lower(), name)

    def test_held_html_is_accessible_and_fails_closed_on_external_media(self):
        self.assertEqual(self.html.count('class="card"'), 6)
        self.assertEqual(self.html.count('loading="lazy"'), 6)
        self.assertEqual(self.html.count("HELD · UNVERIFIED METADATA"), 6)
        self.assertEqual(self.html.count("Inspect source listing"), 6)
        self.assertEqual(self.html.count("Edition identifier</dt><dd>UNRESOLVED"), 6)
        self.assertEqual(self.html.count('target="_blank" rel="noopener noreferrer"'), 6)
        self.assertIn("NO EPISODE STILL", self.html)
        self.assertIn("NO FILM POSTER", self.html)
        self.assertIn("NO BOOK JACKET", self.html)
        self.assertIn("img-src 'self'", self.html)
        self.assertIn("script-src 'none'", self.html)
        self.assertIn("connect-src 'none'", self.html)
        self.assertIn("@media(max-width:480px)", self.html)
        self.assertIn("min-height: 44px", self.html)
        self.assertIn("a:focus-visible", self.html)
        self.assertIn("overflow-wrap: anywhere", self.html)
        self.assertNotRegex(self.html, r"<(?:script|iframe|object|video|picture)\b")
        for source in re.findall(r'<img src="([^"]+)"', self.html):
            self.assertRegex(source, r"^\./art/(?:episode|film|literature)-[0-9a-f]{16}\.svg$")

    def test_pinned_contract_rejects_forged_work_or_art_rights(self):
        for field, value in (
            ("admission_effect", "WORK_ADMITTED"),
            ("coverage_effect", "CLOSE_READ"),
            ("identity_scope", "GLOBAL_WORK"),
            ("verification_status", "VERIFIED"),
            ("edition_identifier", "9781668095898"),
            ("source_reference_url", "javascript:alert(1)"),
            ("title", "Overridden film title"),
        ):
            mutant = copy.deepcopy(self.inputs)
            mutant[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.build_art(mutant)

    def test_record_markup_escapes_hostile_title_and_source_url(self):
        row = copy.deepcopy(self.cards[0])
        row["title"] = '<img src="https://tracker.invalid">'
        markup = mod.card_html(row, 1)
        self.assertNotIn('<img src="https://tracker.invalid">', markup)
        self.assertIn('&lt;img src=&quot;https://tracker.invalid&quot;&gt;', markup)
        for key, value in (("source_reference_url", "javascript:alert(1)"), ("asset_path", "https://tracker.invalid/still.jpg"), ("source_artwork_license_grant", "LICENSED")):
            mutated = copy.deepcopy(self.cards[0])
            mutated[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.card_html(mutated, 1)

    def test_byte_exact_rebuild_and_no_stray_assets(self):
        self.assertEqual(len(self.expected), 8)  # six SVGs, gallery, manifest
        for path, data in self.expected.items():
            self.assertEqual(path.read_bytes(), data)
        manifest = json.loads((mod.TARGET / "manifest.json").read_bytes())
        self.assertEqual(manifest["third_party_image_bytes"], 0)
        self.assertEqual(manifest["licensed_stills_posters_jackets"], 0)
        self.assertEqual(manifest["admitted_works"], 0)
        self.assertEqual(manifest["coverage_effect"], "NONE")
        self.assertEqual(manifest["public_release_effect"], "NONE")

    def test_private_opf_preview_is_excluded_from_this_art_only_proposal(self):
        self.assertFalse((ROOT / "proposals/ui/opf-copy-review").exists())
        self.assertNotIn("opf-copy-review", self.html)
        self.assertNotIn("owner-private", self.html.lower())


if __name__ == "__main__":
    unittest.main()
