"""Adversarial, optimized-Python-safe checks for VOY V003 publisher own-card packet."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proposals/research/voy-s2-tail-v003-20261103"
spec = importlib.util.spec_from_file_location("voy_s2_v003_validate", P / "validate.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class VoyagerV003ProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean = mod.read_json(P / "observations.json")

    def test_exact_valid_packet(self):
        self.assertEqual(mod.validate(), 10)
        self.assertEqual(
            [r["episode"] for r in self.clean["records"]],
            [16, 17, 18, 19, 21, 22, 23, 24, 25, 26],
        )
        self.assertNotIn(20, [r["episode"] for r in self.clean["records"]])

    def test_immutable_admission_and_source(self):
        changes = [
            ("coverage_effect", "CLOSE_READ"),
            ("accepted_source_work_effect", "ACCEPTED"),
            ("accepted_work_effect", "ACCEPTED"),
            ("public_artwork_effect", "APPROVED"),
            ("public_synopsis_effect", "APPROVED"),
            ("proposal_only", False),
            ("actual_episode_or_script_read", True),
            ("source_description_archived", True),
            ("raw_current_html_archived", True),
            ("current_http_status_observed", 404),
            ("current_raw_html_sha256_observed", "0" * 64),
            ("accepted_main_at_selection", "0" * 40),
            ("source_independence_status", "INDEPENDENT_CORROBORATION"),
            ("publisher_guide_url", "https://example.invalid/guide"),
            ("overlap_exclusion", "S2E20_NOW_COUNTED"),
        ]
        for field, forged in changes:
            with self.subTest(field=field):
                x = copy.deepcopy(self.clean)
                x[field] = forged
                with self.assertRaises(ValueError):
                    mod.validate(x)

    def test_immutable_individual_card(self):
        changes = [
            ("publisher_card_title", "New Title"),
            ("publisher_description_sha256", "f" * 64),
            ("video_url", "https://www.paramountplus.com/shows/video/forged/"),
            ("thumbnail_url", "https://thumbnails.cbsig.net/forged.jpg"),
            ("season", 3),
            ("episode", 20),
            ("card_locator", "S2E20"),
            ("observation_id", "duplicate-id"),
            ("local_card_entity_id", "global-work"),
            ("literal_mentions", ["Tuvok", "fabricated"]),
            ("literal_mention_scope", "OBJECTIVE_PLOT"),
            ("synopsis_status", "PUBLIC_APPROVED"),
            ("artwork_rights_status", "PUBLIC_LICENSED"),
            ("image_bytes_retrieved", True),
            ("accepted_work_id", "voyager-s2e16"),
        ]
        for field, forged in changes:
            with self.subTest(field=field):
                x = copy.deepcopy(self.clean)
                x["records"][0][field] = forged
                with self.assertRaises(ValueError):
                    mod.validate(x)

    def test_own_card_swap_rejected_even_if_same_publisher(self):
        x = copy.deepcopy(self.clean)
        x["records"][0]["thumbnail_url"], x["records"][1]["thumbnail_url"] = (
            x["records"][1]["thumbnail_url"], x["records"][0]["thumbnail_url"]
        )
        with self.assertRaises(ValueError):
            mod.validate(x)

    def test_full_row_swap_and_duplicate_card_rejected(self):
        x = copy.deepcopy(self.clean)
        x["records"][0], x["records"][1] = x["records"][1], x["records"][0]
        with self.assertRaises(ValueError):
            mod.validate(x)
        x = copy.deepcopy(self.clean)
        x["records"][1] = copy.deepcopy(x["records"][0])
        with self.assertRaises(ValueError):
            mod.validate(x)

    def test_unknown_license_and_accepted_fields_rejected(self):
        x = copy.deepcopy(self.clean)
        x["rights_granted"] = True
        with self.assertRaises(ValueError):
            mod.validate(x)
        x = copy.deepcopy(self.clean)
        x["records"][0]["verified_license"] = "CC0"
        with self.assertRaises(ValueError):
            mod.validate(x)

    def test_raw_duplicate_key_rejected_including_protected_shadow(self):
        original = (P / "observations.json").read_text(encoding="utf-8")
        forged = original.replace('"coverage_effect": "NONE"', '"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"', 1)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "forged.json"
            f.write_text(forged, encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.read_json(f)

    def test_typed_false_pins(self):
        x = copy.deepcopy(self.clean)
        x["records"][0]["episode"] = True
        with self.assertRaises(ValueError):
            mod.validate(x)
        x = copy.deepcopy(self.clean)
        x["current_http_status_observed"] = True
        with self.assertRaises(ValueError):
            mod.validate(x)


if __name__ == "__main__":
    unittest.main()
