"""Falsifiers for two photographer-licensed, still-held film premiere pictures."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as batch  # noqa: E402


class FilmPremiereTests(unittest.TestCase):
    def setUp(self):
        self.packet = batch.read_json(batch.PACKET)

    def test_exact_packet_and_two_distinct_films_pass(self):
        batch.validate(self.packet)
        self.assertEqual(len({r["row_id"] for r in self.packet["candidates"]}), 2)
        self.assertFalse(self.packet["image_bytes_committed"])

    def test_no_release_or_coverage_promotion(self):
        for field, value in (
            ("public_artwork_release_effect", "RELEASED"),
            ("explorer_effect", "PUBLISHED"),
            ("source_work_admission_effect", "SOURCE_BOUND"),
            ("coverage_effect", "CLOSE_READ"),
            ("image_bytes_committed", True),
            ("data_status", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.packet)
                changed[field] = value
                with self.assertRaises(ValueError):
                    batch.validate(changed)

    def test_cross_film_source_row_substitution_rejected(self):
        for key in ("row_id", "source_local_film_id", "film_title", "official_film_source"):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.packet)
                changed["candidates"][0][key] = changed["candidates"][1][key]
                with self.assertRaises(ValueError):
                    batch.validate(changed)

    def test_swap_whole_photo_receipts_rejected(self):
        changed = copy.deepcopy(self.packet)
        changed["candidates"].reverse()
        with self.assertRaises(ValueError):
            batch.validate(changed)

    def test_rights_and_image_byte_receipt_falsifiers(self):
        for index in (0, 1):
            for key, fake in (
                ("creator", "Paramount"),
                ("reported_photographer_license", "PUBLIC_DOMAIN"),
                ("commons_rights_page_sha256", "0" * 64),
                ("original_image_sha256", "0" * 64),
                ("original_image_sha1_matching_commons", "0" * 40),
                ("original_commons_image_url", "https://example.org/other.jpg"),
                ("original_image_bytes", 13),
                ("pixel_inspection", "INDEPENDENTLY_APPROVED"),
                ("independent_pixel_review", "APPROVED"),
                ("editorial_display_admission", "RELEASED"),
                ("other_rights_review", "EVERYTHING_CLEARED"),
            ):
                with self.subTest(index=index, key=key):
                    changed = copy.deepcopy(self.packet)
                    changed["candidates"][index][key] = fake
                    with self.assertRaises(ValueError):
                        batch.validate(changed)

    def test_unknown_field_and_duplicate_json_key_fail_closed(self):
        changed = copy.deepcopy(self.packet)
        changed["candidates"][0]["hotlink_allowed"] = True
        with self.assertRaises(ValueError):
            batch.validate(changed)
        with self.assertRaises(ValueError):
            json.loads('{"creator":"a","creator":"b"}',
                       object_pairs_hook=batch.unique_object)
        with self.assertRaises(ValueError):
            json.loads('{"x": NaN}', parse_constant=lambda v: batch.check(False, v))

    def test_catalog_falsifier(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "explorer").mkdir()
            path = root / "explorer" / "film-catalog.json"
            path.write_bytes((batch.ROOT / "explorer" / "film-catalog.json").read_bytes() + b" ")
            with self.assertRaises(ValueError):
                batch.validate(self.packet, root)


if __name__ == "__main__":
    unittest.main()
