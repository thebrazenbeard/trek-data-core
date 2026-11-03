"""Fail-closed tests for a held Commons premiere-event photograph proposal."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as premiere  # noqa: E402


class PremierePhotoTests(unittest.TestCase):
    def setUp(self):
        self.packet = premiere.read_json(premiere.PACKET)

    def test_exact_source_and_photo_packet_passes(self):
        premiere.validate(self.packet)
        self.assertFalse(self.packet["image_bytes_committed"])
        self.assertEqual(self.packet["candidate"]["editorial_display_admission"],
                         "HELD_UNTIL_INDEPENDENT_REVIEW")

    def test_cannot_claim_public_release_or_coverage(self):
        for key, value in (
            ("data_status", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"),
            ("public_artwork_release_effect", "RELEASED"),
            ("explorer_effect", "PUBLISHED"),
            ("coverage_effect", "SOURCE_BOUND"),
            ("image_bytes_committed", True),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed[key] = value
                with self.assertRaises(ValueError):
                    premiere.validate(changed)

    def test_wrong_film_or_other_event_photo_cannot_substitute(self):
        for key, value in (
            ("row_id", "film:film-beyond"),
            ("source_local_film_id", "film-beyond"),
            ("official_film_source", "https://www.startrek.com/movies/star-trek-beyond"),
            ("image_kind", "FILM_PRODUCTION_STILL"),
            ("suggested_alt", "Official film poster"),
            ("event_date", "2013-05-23"),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed["candidate"][key] = value
                with self.assertRaises(ValueError):
                    premiere.validate(changed)

    def test_license_or_snapshot_receipt_laundering_fails(self):
        for key, value in (
            ("creator", "Paramount Pictures"),
            ("reported_photographer_license", "PUBLIC_DOMAIN"),
            ("license_url", "https://example.com/fake-license"),
            ("commons_revision_oldid", 1),
            ("commons_rights_page_sha256", "0" * 64),
            ("original_image_sha256", "f" * 64),
            ("original_image_bytes", 1),
            ("editorial_display_admission", "RELEASED"),
            ("independent_pixel_review", "APPROVED"),
            ("other_rights_review", "ALL_RIGHTS_CLEARED"),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed["candidate"][key] = value
                with self.assertRaises(ValueError):
                    premiere.validate(changed)

    def test_source_and_image_swaps_with_recomputed_packet_are_rejected(self):
        changed = copy.deepcopy(self.packet)
        changed["candidate"]["original_commons_image_url"] = (
            "https://upload.wikimedia.org/wikipedia/commons/a/a0/Other_Premiere.jpg")
        with self.assertRaises(ValueError):
            premiere.validate(changed)
        changed = copy.deepcopy(self.packet)
        changed["film_catalog_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            premiere.validate(changed)

    def test_catalog_byte_tamper_detected(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "explorer").mkdir()
            (root / "explorer" / "film-catalog.json").write_bytes(
                (premiere.ROOT / "explorer" / "film-catalog.json").read_bytes() + b" ")
            with self.assertRaises(ValueError):
                premiere.validate(self.packet, root)

    def test_unknown_field_and_duplicate_key_fail_closed(self):
        changed = copy.deepcopy(self.packet)
        changed["candidate"]["may_hotlink_publicly"] = True
        with self.assertRaises(ValueError):
            premiere.validate(changed)
        with self.assertRaises(ValueError):
            json.loads('{"license":"CC","license":"PD"}',
                       object_pairs_hook=premiere.unique_object)


if __name__ == "__main__":
    unittest.main()
