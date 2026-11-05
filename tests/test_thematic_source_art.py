"""Hostile checks for two actual thematic, not merely title-card, drawings."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("thematic_source_art", ROOT / "tools/build_thematic_source_art.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ThematicOriginalArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = mod.exact_source_rows()
        cls.files = mod.expected()

    def test_source_row_and_publisher_description_custody_are_distinct(self):
        self.assertEqual(len(self.rows), 2)
        self.assertEqual({x["source_local_row_id"] for x in self.rows}, {"lead:0000", "lead:0001"})
        for row in self.rows:
            self.assertEqual(row["accepted_metadata_status"], "UNVERIFIED_METADATA")
            self.assertEqual(row["identity_scope"], "SOURCE_LOCAL")
            self.assertEqual(row["motif_status"], "INTERPRETIVE_FROM_DESCRIPTION_NOT_EPISODE_DEPICTION")
            self.assertEqual(row["publisher_source_scope"], mod.DESCRIPTION_SOURCE)
            self.assertIsNone(row["raw_publisher_html_sha256"])
            self.assertEqual(row["admission_effect"], row["coverage_effect"])
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertFalse(row["licensed_source_image"])
            self.assertEqual(hashlib.sha256(row["publisher_description"].encode()).hexdigest(), row["description_utf8_sha256"])
            self.assertEqual(row["description_utf8_sha256"], mod.PUBLISHER_DESCRIPTION_SHA256[row["source_local_row_id"]])
            self.assertEqual(row["official_publisher_url"].startswith("https://www.paramountplus.com/shows/video/"), True)
            for term in row["motif_evidence_terms"]:
                self.assertIn(term, row["publisher_description"].lower())

    def test_semantic_motif_mutants_fail_before_drawing(self):
        original = mod.ROWS
        for key, value in (("title", "Unverified episode"), ("official_url", "https://fake.example/episode"), ("description", "A machine destroys planets but a starship lands inside it"), ("motif_tags", ("machine", "spaceship combat unseen"))):
            row = copy.deepcopy(original[0]); row[key] = value
            try:
                mod.ROWS = (row, original[1])
                with self.subTest(key=key), self.assertRaises(ValueError):
                    mod.exact_source_rows()
            finally:
                mod.ROWS = original

    def test_distinct_nonofficial_motifs_with_nontrivial_visual_content(self):
        doomsday, tribbles = self.rows
        first = mod.svg(doomsday).decode(); second = mod.svg(tribbles).decode()
        self.assertNotEqual(first, second)
        self.assertIn('id="planet"', first)
        self.assertIn('fill="url(#planet)"', first)
        self.assertIn('stroke="#ffbf63"', first)
        self.assertNotIn('id="planet"', second)
        self.assertGreater(second.count('<circle '), 50)
        self.assertIn('stroke="#713b5b"', second)
        for data in (first, second):
            root = ET.fromstring(data)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertTrue({x.tag.split('}')[-1] for x in root.iter()} <= {"svg", "defs", "linearGradient", "radialGradient", "stop", "rect", "path", "circle", "ellipse", "text"})
            self.assertIn("NOT OFFICIAL ART", data)
            self.assertIn("NOT CLOSE-READ EVIDENCE", data)
            for forbidden in ("<image", "<script", "<foreignObject", "href=", "javascript:", "data:", "<use "):
                self.assertNotIn(forbidden.lower(), data.lower())

    def test_direct_renderer_cannot_substitute_unsourced_picture_caption(self):
        for field, value in (("title", "Official frame"), ("motif_interpretation", "canonically proven plot"), ("publisher_description", "unknown"), ("motif_id", "tribbles")):
            forged = copy.deepcopy(self.rows[0]); forged[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.svg(forged)

    def test_byte_exact_images_manifest_and_no_stray_artwork(self):
        self.assertEqual(len(self.files), 3)
        for p, b in self.files.items():
            self.assertEqual(p.read_bytes(), b)
        packet = json.loads((mod.OUT / "manifest.json").read_text())
        self.assertEqual(packet["accepted_main"], mod.MAIN)
        self.assertEqual(packet["source_image_bytes"], 0)
        self.assertEqual(packet["admitted_works"], 0)
        self.assertEqual(packet["coverage_effect"], "NONE")
        self.assertEqual(packet["public_release_effect"], "NONE")
        self.assertIs(packet["full_episode_viewing"], False)
        for record in packet["records"]:
            path = mod.OUT / record["art_path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["art_sha256"])
        self.assertEqual(set((mod.OUT / "art").iterdir()), {mod.OUT / "art/doomsday.svg", mod.OUT / "art/tribbles.svg"})


if __name__ == "__main__":
    unittest.main()
