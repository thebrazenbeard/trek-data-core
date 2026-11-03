"""Adversarial checks for publisher film poster locators; no image release."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as candidate  # noqa: E402


class FilmPosterLocatorTests(unittest.TestCase):
    def setUp(self):
        self.packet = candidate.read_json(candidate.PACKET)

    def test_exact_film_poster_research_packet(self):
        candidate.validate(self.packet)
        self.assertEqual(len(self.packet["artwork"]), 4)
        self.assertTrue(all(x["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE"
                            for x in self.packet["artwork"]))

    def test_no_inferred_license_or_research_coverage(self):
        for key, value in (
            ("public_artwork_release_effect", "APPROVED"),
            ("explorer_effect", "RELEASED"),
            ("coverage_effect", "SOURCE_BOUND"),
            ("image_bytes_downloaded_or_committed", True),
            ("external_image_display_eligible", True),
            ("publisher_terms_rights_reading", "PUBLIC_INLINE_USE_ALLOWED"),
            ("publisher_terms_raw_sha256", "0" * 64),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed[key] = value
                with self.assertRaises(ValueError):
                    candidate.validate(changed)

    def test_whole_film_identity_and_page_swapped_not_accepted(self):
        changed = copy.deepcopy(self.packet)
        a, b = changed["artwork"][:2]
        for key in ("film_id", "film_title", "publisher_page", "candidate_id"):
            a[key], b[key] = b[key], a[key]
        with self.assertRaises(ValueError):
            candidate.validate(changed)

    def test_poster_link_swap_cannot_be_approved(self):
        changed = copy.deepcopy(self.packet)
        a, b = changed["artwork"][:2]
        a["poster_image_url"], b["poster_image_url"] = b["poster_image_url"], a["poster_image_url"]
        with self.assertRaises(ValueError):
            candidate.validate(changed)

    def test_forged_same_host_poster_or_source_digest_fails(self):
        for key, value in (
            ("poster_image_url", "https://images.prismic.io/star-trek-untold/FORGED_KeyArt_full.png"),
            ("page_raw_sha256", "0" * 64),
            ("page_html_bytes", 1),
            ("poster_alt_from_page", "Officially licensed unrestricted poster"),
            ("rights_status", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"),
            ("image_pixel_review", "VERIFIED"),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed["artwork"][0][key] = value
                with self.assertRaises(ValueError):
                    candidate.validate(changed)

    def test_extra_unreviewed_fields_or_duplicate_id_fail(self):
        changed = copy.deepcopy(self.packet)
        changed["artwork"][0]["public_cdn_embed"] = True
        with self.assertRaises(ValueError):
            candidate.validate(changed)
        changed = copy.deepcopy(self.packet)
        changed["artwork"][0]["film_id"] = changed["artwork"][1]["film_id"]
        with self.assertRaises(ValueError):
            candidate.validate(changed)

    def test_catalog_bytes_and_specific_baseline_are_bound(self):
        changed = copy.deepcopy(self.packet)
        changed["catalog_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            candidate.validate(changed)
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "explorer").mkdir()
            (root / "explorer" / "film-catalog.json").write_bytes(
                (candidate.ROOT / "explorer" / "film-catalog.json").read_bytes() + b" ")
            with self.assertRaises(ValueError):
                candidate.validate(self.packet, root)

    def test_duplicate_json_keys_fail_closed(self):
        with self.assertRaises(ValueError):
            json.loads('{"image":true,"image":false}',
                       object_pairs_hook=candidate.unique_object)


if __name__ == "__main__":
    unittest.main()
