"""Deterministic public-source ISBN shelf without private archive disclosure."""

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_publisher_isbn_crosschecks as build  # noqa: E402
import query_publisher_isbn_crosschecks as search  # noqa: E402


class PublisherIsbnCrosscheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build.build()

    def test_accepted_five_batch_scope_disjoint_public_isbns(self):
        data = self.result
        self.assertEqual((data["row_count"], data["publisher_isbn_identifier_agreements"],
                          data["held_discrepancy_count"]), (39, 30, 9))
        self.assertEqual((data["existing_publisher_edition_leads_count_unchanged"],
                          data["existing_directory_rows_count_unchanged"]), (3, 1214))
        self.assertEqual(len(data["accepted_public_input_receipts"]), 5)
        self.assertEqual(len({r["source_local_ref"] for r in data["rows"]}), 39)
        self.assertEqual(len({r["publisher_isbn13"] for r in data["rows"]}), 39)
        self.assertEqual(set(int(r["source_local_ref"][-4:]) for r in data["rows"]), build.EXPECTED_IDS)

    def test_no_private_archive_metadata_or_plot_text_in_public_projection(self):
        data = self.result
        self.assertEqual((data["private_ebooks_authenticated"], data["canonical_works_admitted"],
                          data["synopses_published"], data["artwork_published"]), (0, 0, 0, 0))
        self.assertEqual(data["publisher_independence_group_count"], 1)
        for row in data["rows"]:
            self.assertEqual((row["private_edition_equivalence"], row["work_identity"]),
                             ("UNVERIFIED", "NOT_RECONCILED"))
            self.assertEqual((row["public_synopsis_effect"], row["artwork_effect"],
                              row["admission_effect"], row["coverage_effect"]),
                             ("NONE", "NONE", "NONE", "NONE"))
            self.assertFalse(any(k in row for k in ("opf_entry_sha256", "opf_isbn10", "opf_title",
                                                   "original_publisher_description_paraphrase", "uncertainty",
                                                   "opf_input", "private_archive_path", "cover_url")))
            self.assertTrue(row["public_source_record"].startswith("proposals/librarian/"))
        raw = build.encode(data).decode("utf-8")
        for forbidden in ("C:\\\\Users", "/mnt/d/", "OneDrive/", "D:\\\\VERA", "opf_entry_sha256",
                          "original_publisher_description_paraphrase", "private-opf-metadata-20261103/"):
            self.assertNotIn(forbidden, raw)

    def test_exact_bytes_and_source_hash_receipts(self):
        self.assertEqual((ROOT / build.OUT).read_bytes(), build.encode(self.result))
        for receipt in self.result["accepted_public_input_receipts"]:
            self.assertEqual(hashlib.sha256((ROOT / receipt["path"]).read_bytes()).hexdigest(),
                             receipt["sha256"])

    def test_callable_query_with_limit_and_held_filter(self):
        rows = self.result["rows"]
        self.assertEqual(len(search.query(rows, creator="Peter David")), 3)
        self.assertEqual(len(search.query(rows, state="HELD_PUBLISHER_DATE_DISCREPANCY")), 4)
        self.assertEqual([r["source_local_ref"] for r in search.query(rows, source_ref="opf-local:0076")],
                         ["opf-local:0076"])
        self.assertEqual(len(search.query(rows, limit=2)), 2)
        with self.assertRaises(ValueError):
            search.query(rows, limit=0)
        with self.assertRaises(ValueError):
            search.query(rows, limit=40)

    def test_reject_duplicate_source_ids_and_unapproved_status(self):
        real_load = build.load
        for variant in ("duplicate", "forged"):
            def corrupt(path):
                data, raw = real_load(path)
                if path == build.INPUTS[1][1]:
                    data = copy.deepcopy(data)
                    if variant == "duplicate":
                        data["records"][0]["opf_source_local_id"] = "opf-local:0009"
                    else:
                        data["records"][0]["crosscheck_state"] = "WORK_ADMITTED_AND_READ_FULL_TEXT_UNRESOLVED"
                return data, raw
            with self.subTest(variant=variant), patch.object(build, "load", side_effect=corrupt):
                with self.assertRaises(ValueError):
                    build.build()

    def test_reject_off_host_or_wrong_isbn_product_path(self):
        real_load = build.load
        for url in ("https://evil.example/books/a/b/c/9780743412155",
                    "https://www.simonandschuster.com/books/a/b/c/9780743412156"):
            def corrupt(path):
                data, raw = real_load(path)
                if path == build.INPUTS[1][1]:
                    data = copy.deepcopy(data)
                    data["records"][0]["publisher_locator"] = url
                return data, raw
            with self.subTest(url=url), patch.object(build, "load", side_effect=corrupt):
                with self.assertRaises(ValueError):
                    build.build()

    def test_reject_private_read_or_equivalence_claim(self):
        real_load = build.load
        def corrupt(path):
            data, raw = real_load(path)
            if path == build.INPUTS[0][1]:
                data = copy.deepcopy(data)
                data["private_source_equivalence_verified"] = True
            return data, raw
        with patch.object(build, "load", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "custody/admission"):
                build.build()


if __name__ == "__main__":
    unittest.main()
