"""Fail-closed checks for a proposed, non-released visual crosswalk."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as crosswalk  # noqa: E402


class OpenLibraryCandidateTests(unittest.TestCase):
    def setUp(self):
        self.packet = crosswalk.read_json(crosswalk.PACKET)

    def test_four_true_jackets_and_five_holds_proposal_validates(self):
        crosswalk.validate(self.packet)
        self.assertEqual(len(self.packet["candidates"]), 4)
        self.assertEqual(len(self.packet["held"]), 5)
        self.assertNotIn(12857937, [item["cover_id"] for item in self.packet["candidates"]])
        self.assertEqual(self.packet["public_artwork_release_effect"], "NONE")

    def test_license_admission_or_image_bytes_cannot_be_claimed(self):
        for key, value in (
            ("copyright_status", "LICENSED"),
            ("public_artwork_release_effect", "RELEASED"),
            ("coverage_effect", "SOURCE_BOUND"),
            ("accepted_work_effect", "ACCEPTED"),
            ("image_bytes_committed", True),
        ):
            with self.subTest(key=key):
                item = copy.deepcopy(self.packet)
                item[key] = value
                with self.assertRaises(ValueError):
                    crosswalk.validate(item)

    def test_row_or_publisher_locator_swaps_are_rejected(self):
        for key, value in (
            ("row_id", "literature:prh-autobiography-sisko"),
            ("source_locator", self.packet["candidates"][2]["source_locator"]),
            ("publisher_detail", "Paperback ISBN 9781668002391"),
            ("publisher_lineage", "publisher:simonandschuster.com"),
            ("publisher_source_sha256", "0" * 64),
        ):
            with self.subTest(key=key):
                item = copy.deepcopy(self.packet)
                item["candidates"][0][key] = value
                with self.assertRaises((ValueError, StopIteration)):
                    crosswalk.validate(item)

    def test_cover_endpoint_or_edition_id_must_be_exactly_derived(self):
        for key, value in (
            ("cover_url", "https://example.invalid/fake.jpg"),
            ("openlibrary_edition_json_url", "https://openlibrary.org/books/OL1M.json"),
            ("attribution_url", "https://openlibrary.org/isbn/0000000000000"),
            ("edition_metadata_sha256", "not-a-hash"),
            ("cover_head_status", 404),
            ("rights_status", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"),
            ("release_status", "RELEASED"),
        ):
            with self.subTest(key=key):
                item = copy.deepcopy(self.packet)
                item["candidates"][0][key] = value
                with self.assertRaises(ValueError):
                    crosswalk.validate(item)

    def test_each_literary_row_has_exactly_one_disposition(self):
        for key, value in (
            ("held", []),
            ("candidate_count", 9),
            ("literary_row_count", 8),
        ):
            with self.subTest(key=key):
                item = copy.deepcopy(self.packet)
                item[key] = value
                with self.assertRaises(ValueError):
                    crosswalk.validate(item)

    def test_no_cover_hold_cannot_invent_release_or_edition(self):
        item = copy.deepcopy(self.packet)
        item["held"][4]["openlibrary_edition_id"] = "OL111M"
        with self.assertRaises(ValueError):
            crosswalk.validate(item)

    def test_metadata_200_title_page_still_must_not_be_cover_candidate(self):
        for key, value in (
            ("reason", "EDITION_JSON_200_WITHOUT_COVERS"),
            ("rejected_cover_id", 13083310),
            ("rejected_image_type", "BOOK_JACKET"),
            ("review_evidence", "UNREVIEWED"),
        ):
            with self.subTest(key=key):
                item = copy.deepcopy(self.packet)
                item["held"][0][key] = value
                with self.assertRaises(ValueError):
                    crosswalk.validate(item)

    def test_extra_unreviewed_image_fields_are_rejected(self):
        item = copy.deepcopy(self.packet)
        item["candidates"][0]["image_path"] = "licensed-artwork/not-licensed.jpg"
        with self.assertRaises(ValueError):
            crosswalk.validate(item)

    def test_duplicate_json_keys_fail_closed(self):
        try:
            json.loads('{"key":1,"key":2}', object_pairs_hook=crosswalk.unique_object)
        except ValueError:
            pass
        else:
            self.fail("duplicate JSON silently accepted")


if __name__ == "__main__":
    unittest.main()
