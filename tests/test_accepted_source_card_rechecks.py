"""Fail-closed source-local projection of accepted B005-B009 + DIS publisher cards."""

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_accepted_source_card_rechecks as projection  # noqa: E402
import query_accepted_source_card_rechecks as search  # noqa: E402


class AcceptedSourceCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = projection.build()

    def test_exact_source_local_counts_and_unresolved(self):
        result = self.result
        self.assertEqual((result["directory_row_count"], result["prior_metadata_recheck_count_unchanged"]),
                         (1214, 56))
        self.assertEqual((result["new_publisher_card_source_local_lead_count"],
                          result["new_exact_title_matches"],
                          result["new_unresolved_title_or_split_cases"]), (61, 46, 15))
        self.assertEqual(len(result["rows"]), 61)
        self.assertEqual([r["row_id"] for r in result["rows"]], projection.EXPECTED_LEADS)
        self.assertEqual(result["unmapped_snw_s3_cards_not_joined"], 10)
        self.assertEqual(len(set(r["row_id"] for r in result["rows"])), 61)

    def test_zero_promotions_or_publisher_blurbs(self):
        result = self.result
        self.assertEqual((result["admitted_works"], result["full_audiovisual_content_reads"],
                          result["approved_public_synopses"], result["raw_publisher_pages_custodied"]),
                         (0, 0, 0, 0))
        self.assertEqual(result["publisher_source_family_count"], 1)
        for row in result["rows"]:
            self.assertFalse(row["full_episode_or_transcript_read"])
            self.assertIsNone(row["raw_publisher_page_sha256"])
            self.assertEqual((row["admission_effect"], row["coverage_effect"],
                              row["synopsis_publication_effect"]), ("NONE", "NONE", "NONE"))
            self.assertNotIn("original_synopsis_draft", row)
            self.assertNotIn("publisher_blurb", row)

    def test_ent_combined_card_not_inferred_to_two_works(self):
        by_id = {r["row_id"]: r for r in self.result["rows"]}
        a, b = by_id["lead:0106"], by_id["lead:0107"]
        self.assertEqual(a["publisher_card_title"], b["publisher_card_title"])
        self.assertEqual(a["publisher_title_check"], "COMBINED_CARD_SPLIT_UNRESOLVED")
        self.assertEqual(b["publisher_title_check"], "COMBINED_CARD_SPLIT_UNRESOLVED")
        self.assertEqual(a["admission_effect"], "NONE")

    def test_digests_and_exact_committed_bytes(self):
        self.assertEqual((ROOT / projection.OUTPUT).read_bytes(), projection.encode(self.result))
        self.assertEqual(len(self.result["accepted_input_receipts"]), 9)
        for receipt in self.result["accepted_input_receipts"]:
            self.assertEqual(hashlib.sha256((ROOT / receipt["path"]).read_bytes()).hexdigest(),
                             receipt["sha256"])

    def test_query_returns_only_bounded_source_local_matches(self):
        rows = self.result["rows"]
        self.assertEqual([r["row_id"] for r in search.query(rows, row_id="lead:0108")], ["lead:0108"])
        self.assertEqual(len(search.query(rows, series="ENT")), 18)
        self.assertEqual(len(search.query(rows, batch="DIS-S3-SEVEN")), 7)
        self.assertEqual(len(search.query(rows, title="broken bow")), 2)
        self.assertEqual(len(search.query(rows, title="unification")), 1)
        self.assertEqual(len(search.query(rows, limit=3)), 3)
        with self.assertRaises(ValueError):
            search.query(rows, limit=0)
        with self.assertRaises(ValueError):
            search.query(rows, limit=1000000)

    def test_false_exact_title_fails_closed(self):
        real_load = projection.load
        def corrupt(path):
            data, raw = real_load(path)
            if path == projection.SOURCES[3][1]:
                data = copy.deepcopy(data)
                data["rows"][0]["official_card_title"] = "Invented publisher title"
            return data, raw
        with patch.object(projection, "load", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "false EXACT"):
                projection.build()

    def test_duplicate_or_fabricated_directory_mapping_fails_closed(self):
        real_load = projection.load
        for fake in ("lead:0051", "lead:1200"):
            def corrupt(path):
                data, raw = real_load(path)
                if path == projection.SOURCES[1][1]:
                    data = copy.deepcopy(data)
                    data["rows"][0]["row_id"] = fake
                return data, raw
            with self.subTest(fake=fake), patch.object(projection, "load", side_effect=corrupt):
                with self.assertRaises(ValueError):
                    projection.build()

    def test_promotion_of_source_only_status_fails_closed(self):
        real_load = projection.load
        def corrupt(path):
            data, raw = real_load(path)
            if path == projection.SOURCES[4][1]:
                data = copy.deepcopy(data)
                data["coverage_effect"] = "CLOSE_READ"
            return data, raw
        with patch.object(projection, "load", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "elevated"):
                projection.build()

    def test_unmapped_snw_never_silently_joins_directory(self):
        real_load = projection.load
        def corrupt(path):
            data, raw = real_load(path)
            if path == projection.UNMAPPED_SNW_INPUTS[0]:
                data = copy.deepcopy(data)
                data["works"][0]["lead_id"] = "lead:0115"
            return data, raw
        with patch.object(projection, "load", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "unaccepted directory binding"):
                projection.build()


if __name__ == "__main__":
    unittest.main()
