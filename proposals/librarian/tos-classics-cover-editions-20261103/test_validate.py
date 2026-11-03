"""Falsify edition identity, source lineage, and unlicensed cover claims."""

import copy
import hashlib
import json
import pathlib
import unittest

from validate import CATALOG, HERE, validate, valid_isbn13

DATA = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
CATALOG_BYTES = CATALOG.read_bytes()


class ClassicEditionCoverSourceGate(unittest.TestCase):
    def test_exact_four_editions_three_work_labels(self):
        self.assertEqual(validate(copy.deepcopy(DATA), CATALOG_BYTES), {
            "edition_observations": 4, "distinct_work_labels": 3,
            "cover_links_indexed_not_cleared": 4,
        })

    def test_all_publisher_isbns_pass_check_digit(self):
        for row in DATA["edition_candidates"]:
            self.assertTrue(valid_isbn13(row["isbn13"]))
        self.assertFalse(valid_isbn13("9780743412095"))

    def test_mismatched_edition_format_imprint_isbn_or_url(self):
        for field, value in (
            ("format", "eBook"), ("publisher_imprint", "Pocket Books/Star Trek"),
            ("isbn13", "9781451607535"),
            ("publisher_product_url", DATA["edition_candidates"][0]["publisher_product_url"]),
            ("creator", "Diane Duane"),
        ):
            altered = copy.deepcopy(DATA)
            altered["edition_candidates"][1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_duplicate_edition_and_cross_format_identity_leak(self):
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][1] = copy.deepcopy(altered["edition_candidates"][0])
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][1]["edition_candidate_id"] = altered["edition_candidates"][0]["edition_candidate_id"]
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_cover_hotlink_and_rights_promotion_rejected(self):
        for field, value in (
            ("cover_file_uri", "https://cdn.example/cover.jpg"),
            ("cover_rights_state", "LICENSED_FOR_REUSE"),
            ("cover_link_on_product_page", False),
            ("cover_source_section", "Unverified image"),
        ):
            altered = copy.deepcopy(DATA)
            altered["edition_candidates"][2][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][2]["image_bytes"] = "copied"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_governed_effects_and_custody_always_zero(self):
        for field, value in (
            ("accepted_sources_added", 1), ("accepted_works_added", 3),
            ("accepted_edition_bindings_added", 4), ("coverage_events_added", 4),
            ("image_publication_effect", "DEPLOYED"),
            ("source_body_read", True), ("raw_page_sha256", "a" * 64),
            ("source_version", "verified"), ("rights_to_publish_covered_images", "CLEARED"),
            ("artwork_bytes_downloaded_or_committed", True),
        ):
            altered = copy.deepcopy(DATA)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_metadata_envelope_and_legacy_hold_pinned(self):
        for field, value in (
            ("proposal_id", "FAKE"), ("baseline_accepted_main", "0" * 40),
            ("observed_date_utc", "2025-10-02"), ("source_family", "community:memory-alpha"),
        ):
            altered = copy.deepcopy(DATA)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["legacy_crosswalk_hold"]["relation"] = "SAME_EDITION"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_directory_gap_cannot_be_forged_by_rehash(self):
        modified_catalog = json.loads(CATALOG_BYTES)
        modified_catalog["rows"][0]["medium"] = "LITERATURE"
        modified_catalog["rows"][0]["title"] = "The Wounded Sky"
        modified_raw = json.dumps(modified_catalog, separators=(",", ":"), sort_keys=True).encode("utf-8")
        altered = copy.deepcopy(DATA)
        altered["catalog_gap_snapshot"]["sha256"] = hashlib.sha256(modified_raw).hexdigest()
        with self.assertRaises(ValueError):
            validate(altered, modified_raw)


if __name__ == "__main__":
    unittest.main()
