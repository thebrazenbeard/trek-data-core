"""Hostile validation tests for publisher-edition source-local proposals."""

import copy
import hashlib
import json
import pathlib
import unittest

from validate import ROOT, validate, valid_isbn13

HERE = pathlib.Path(__file__).resolve().parent
DATA = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
CATALOG_BYTES = (ROOT / "explorer/discovery-catalog.json").read_bytes()


class EditionCatalogGate(unittest.TestCase):
    def test_original(self):
        self.assertEqual(validate(copy.deepcopy(DATA), CATALOG_BYTES), 3)

    def test_bad_isbn_checksum(self):
        self.assertFalse(valid_isbn13("9780743420588"))
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][0]["isbn13"] = "9780743420588"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_source_locator_title_collision_or_wrong_host_rejected(self):
        for locator in (
            DATA["edition_candidates"][1]["source_locator"],
            "https://memory-alpha.fandom.com/wiki/Homecoming",
            "https://www.simonandschuster.com/books/Homecoming/Christie-Golden/Star-Trek-Voyager/9780743475632",
        ):
            altered = copy.deepcopy(DATA)
            altered["edition_candidates"][2]["source_locator"] = locator
            with self.subTest(locator=locator), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_catalog_mutation_or_snapshot_claim_rejected(self):
        changed = CATALOG_BYTES.replace(b'"row_count": 1214', b'"row_count": 1215')
        with self.assertRaises(ValueError):
            validate(DATA, changed)
        altered = copy.deepcopy(DATA)
        altered["catalog_gap_snapshot"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_forged_catalog_digest_cannot_hide_matching_literature(self):
        # Reproduce the actual Explorer medium, and even repair the hash claim.
        # A title already listed in the directory must invalidate the gap proof.
        catalog = json.loads(CATALOG_BYTES)
        catalog["rows"][0]["medium"] = "LITERATURE"
        catalog["rows"][0]["title"] = "Homecoming"
        forged_bytes = json.dumps(catalog, separators=(",", ":"), sort_keys=True).encode("utf-8")
        altered = copy.deepcopy(DATA)
        altered["catalog_gap_snapshot"]["sha256"] = hashlib.sha256(forged_bytes).hexdigest()
        with self.assertRaisesRegex(ValueError, "literary gap no longer valid"):
            validate(altered, forged_bytes)

    def test_metadata_envelope_cannot_be_forged(self):
        for field, value in (
            ("proposal_id", "FAKE-ID"),
            ("observed_date_utc", "1999-01-01"),
            ("baseline_accepted_main", "0" * 40),
        ):
            altered = copy.deepcopy(DATA)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_rights_coverage_protected(self):
        for field, val in (("coverage_events_added", 1), ("accepted_works_added", 3), ("rights_to_republish_text_or_art", "GRANTED")):
            altered = copy.deepcopy(DATA)
            altered[field] = val
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_media_text_and_unverified_response_forbidden(self):
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][0]["cover_url"] = "https://example.org/cover.jpg"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["publisher_evidence"]["response_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_duplicate_candidate_and_creator_swap_rejected(self):
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][1] = altered["edition_candidates"][0]
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["edition_candidates"][0]["creator"] = "Peter David"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)


if __name__ == "__main__":
    unittest.main()
