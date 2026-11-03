"""Source-first contract for Titan Books fictional memoir product receipts."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools import build_prh_autobiography_candidates as literature


ROOT = Path(__file__).resolve().parents[1]


class PrhAutobiographySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / literature.SOURCE).read_bytes())

    def test_five_distinct_fictional_works_one_boxed_set_container(self):
        result = literature._observations(self.source)
        series, works, container = result
        self.assertEqual(series["observed_title_count"], 5)
        self.assertEqual(len(works), len({row["work_id"] for row in works}))
        self.assertEqual(len(works), len({row["isbn13"] for row in works}))
        self.assertEqual(len(works), 5)
        self.assertFalse(container["counted_as_independent_work"])
        self.assertEqual(len(container["contains_work_ids"]), 3)

    def test_deterministic_records_are_candidate_only(self):
        actual = (ROOT / literature.OUTPUT).read_bytes()
        self.assertEqual(actual, literature.build(ROOT))
        self.assertEqual(literature.main(["--repo-root", str(ROOT), "--check"]), 0)
        packet = json.loads(actual)
        self.assertEqual(packet["work_count"], 5)
        self.assertEqual(len(packet["sources"]), 5)
        self.assertEqual(len(packet["edition_candidates"]), 5)
        self.assertEqual(len(packet["bindings"]), 5)
        self.assertEqual(packet["deep_read_effect"], "NONE")
        self.assertEqual(packet["raw_html_publication"], "NONE")
        self.assertTrue(all(packet[k] == "NONE" for k in
                            ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect")))
        self.assertTrue(all(s["cover_license_verification"] == "NOT_ESTABLISHED"
                            for s in packet["sources"]))
        self.assertFalse(any(s.get("content") or s.get("description") for s in packet["sources"]))

    def test_raw_source_hashes_are_recorded_not_fake_completed_reads(self):
        packet = json.loads((ROOT / literature.OUTPUT).read_bytes())
        self.assertEqual(packet["distributor_series_source"]["source_body_bytes"], 183841)
        self.assertEqual(packet["collection_container"]["source_body_bytes"], 215042)
        self.assertTrue(all(len(s["content_hash_sha256"]) == 64 and s["source_body_bytes"] > 100_000
                            for s in packet["sources"]))
        digests = {r["path"]: r["sha256"] for r in
                   json.loads((ROOT / "explorer/discovery-catalog.json").read_bytes())["source_digests"]}
        self.assertEqual(digests[str(literature.SOURCE)],
                         hashlib.sha256((ROOT / literature.SOURCE).read_bytes()).hexdigest())

    def test_admission_and_nonfiction_misclassification_rejected(self):
        for field, value in (("coverage_effect", "SOURCE_BOUND"),
                             ("accepted_work_effect", "ADMITTED"),
                             ("source_method", "RECAPS"),
                             ("observed_on", "2020-01-01")):
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.source)
                mutation[field] = value
                with self.assertRaises(ValueError):
                    literature._observations(mutation)

    def test_source_url_and_cover_spoof_rejected(self):
        for field, value in (("locator", "https://www.penguinrandomhouse.com.evil.test/books/1/"),
                             ("locator", "https://www.penguinrandomhouse.com/books/1/?next=attack"),
                             ("locator", self.source["work_candidates"][1]["locator"]),
                             ("cover_locator", "https://evil.test/cover/9781783297481")):
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.source)
                mutation["work_candidates"][0][field] = value
                with self.assertRaises(ValueError):
                    literature._observations(mutation)

    def test_bad_source_hash_or_invalid_isbn_rejected(self):
        for field, value in (("source_body_sha256", "0" * 63),
                             ("isbn13", "9781783297489"),
                             ("source_body_bytes", 0),
                             ("source_body_bytes", 123456),
                             ("pages", 321),
                             ("published_date", "1999-01-01")):
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.source)
                mutation["work_candidates"][0][field] = value
                with self.assertRaises(ValueError):
                    literature._observations(mutation)

    def test_collection_and_series_raw_receipt_tamper_rejected(self):
        for location, field, value in (("source_collection", "source_body_bytes", 183842),
                                       ("source_collection", "source_body_sha256", "0" * 64),
                                       ("collection_container", "source_body_bytes", 215043),
                                       ("collection_container", "source_body_sha256", "0" * 64),
                                       ("collection_container", "title", "Another Collection"),
                                       ("collection_container", "locator", self.source["work_candidates"][0]["locator"])):
            with self.subTest(location=location, field=field):
                mutation = copy.deepcopy(self.source)
                mutation[location][field] = value
                with self.assertRaises(ValueError):
                    literature._observations(mutation)

    def test_collection_edition_never_becomes_sixth_work(self):
        for field, value in (("counted_as_independent_work", True),
                             ("contains_work_ids", ["prh-autobiography-kirk"]),
                             ("isbn13", self.source["work_candidates"][0]["isbn13"])):
            with self.subTest(field=field):
                mutation = copy.deepcopy(self.source)
                mutation["collection_container"][field] = value
                with self.assertRaises(ValueError):
                    literature._observations(mutation)

    def test_missing_and_symlinked_capture_receipts_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / literature.SOURCE
            source.parent.mkdir(parents=True)
            with self.assertRaises((OSError, ValueError)):
                literature.build(root)
            original = ROOT / literature.SOURCE
            source.symlink_to(original)
            with self.assertRaises((OSError, ValueError)):
                literature.build(root)


if __name__ == "__main__":
    unittest.main()
