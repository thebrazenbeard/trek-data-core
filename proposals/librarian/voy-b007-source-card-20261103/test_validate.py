"""Hostile tests for publisher title/slot and multipart numbering discipline."""

import copy
import hashlib
import json
import pathlib
import unittest

from validate import CATALOG, HERE, validate

DATA = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
CATALOG_BYTES = CATALOG.read_bytes()


class VoyagerB007SourceCardTests(unittest.TestCase):
    def test_verified_seven_card_seed(self):
        self.assertEqual(validate(copy.deepcopy(DATA), CATALOG_BYTES), 7)
        self.assertEqual([r["row_id"] for r in DATA["candidate_rows"]],
                         [f"lead:{i:04d}" for i in range(83, 90)])

    def test_do_not_promote_roman_numerals_to_exact(self):
        for index in (4, 5, 6):
            altered = copy.deepcopy(DATA)
            altered["candidate_rows"][index]["title_status"] = "EXACT"
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_wrong_official_slot_title_qid_or_url_rejected(self):
        for field, value in (
            ("official_title", "Basics, Part II"),
            ("season", 7),
            ("episode", 2),
            ("source_local_qid_url", "https://www.wikidata.org/wiki/Q16744066"),
            ("guide_url", "https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/"),
        ):
            altered = copy.deepcopy(DATA)
            altered["candidate_rows"][4][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_unknown_fields_duplicated_id_false_read_rejected(self):
        altered = copy.deepcopy(DATA)
        altered["candidate_rows"][0]["image_url"] = "https://example.test/frame.jpg"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["candidate_rows"][1]["row_id"] = "lead:0083"
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["candidate_rows"][2]["brief_description_read"] = False
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_false_custody_artwork_synopses_admission_rejected(self):
        for field, value in (
            ("raw_http_response_sha256", "0" * 64),
            ("source_body_read", True),
            ("publisher_blurbs_reproduced", True),
            ("artwork_bytes_retrieved", True),
            ("accepted_corpus_effect", "WORK_ADMITTED"),
            ("source_family", "wikidata:wdqs"),
        ):
            altered = copy.deepcopy(DATA)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)
        altered = copy.deepcopy(DATA)
        altered["summary"]["coverage_events"] = 7
        with self.assertRaises(ValueError):
            validate(altered, CATALOG_BYTES)

    def test_exact_envelope_not_forgeable(self):
        for field, value in (
            ("proposal_id", "FAKE"), ("baseline_accepted_main", "0" * 40),
            ("observed_date_utc", "2026-10-01"), ("role", "FILMS"),
        ):
            altered = copy.deepcopy(DATA)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(altered, CATALOG_BYTES)

    def test_catalog_forgery_with_recomputed_sha_fails(self):
        catalog = json.loads(CATALOG_BYTES)
        target = next(x for x in catalog["rows"] if x["row_id"] == "lead:0083")
        target["title"] = "An Unrelated Episode"
        raw = json.dumps(catalog, sort_keys=True, separators=(",", ":")).encode()
        altered = copy.deepcopy(DATA)
        altered["catalog_snapshot"]["sha256"] = hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):
            validate(altered, raw)

    def test_previous_b006_ids_disjoint(self):
        preceding = json.loads((HERE.parents[2] / "proposals/verification/episode-guide-rechecks-b006-voy-20261103/records.json").read_text(encoding="utf-8"))
        before = {r["source_local_row_id"] for r in preceding["rows"]}
        after = {r["row_id"] for r in DATA["candidate_rows"]}
        self.assertTrue(before.isdisjoint(after))


if __name__ == "__main__":
    unittest.main()
