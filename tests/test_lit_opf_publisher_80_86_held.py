"""Deterministic hostile checks on HELD owner OPF / publisher items 0080–0086."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_80_86_20261104.validate import DATA, ORIGINAL_OPF, validate


class Publisher8086Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_bounded_packet(self):
        self.assertEqual((7, 5, 2), validate(self.doc, self.opf))

    def test_nonoverlap_with_25_held(self):
        root = DATA.parents[3]
        earlier = []
        for folder in ("lit_opf_publisher_seven_20261104", "lit_opf_publisher_nine_20261104",
                       "lit_opf_publisher_71_79_20261104"):
            earlier.extend(json.loads((root / "proposals/research" / folder / "records.json")
                                    .read_text(encoding="utf-8"))["rows"])
        self.assertEqual([f"opf-local:{n:04d}" for n in range(80, 87)],
                         [row["opf_local_id"] for row in self.doc["rows"]])
        self.assertFalse({row["opf_local_id"] for row in earlier} &
                         {row["opf_local_id"] for row in self.doc["rows"]})
        self.assertFalse({row["isbn13"] for row in earlier} &
                         {row["isbn13"] for row in self.doc["rows"]})

    def test_missing_opf_isbns_do_not_become_proof(self):
        self.assertEqual("UNVERIFIED_LOCAL_TITLE_ONLY", self.doc["rows"][1]["opf_edition_crosswalk_state"])
        self.assertEqual("UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY", self.doc["rows"][3]["opf_edition_crosswalk_state"])
        for idx in (1, 3):
            self.assertIsNone(self.doc["rows"][idx]["opf_claimed_isbn10"])
            for key, val in (("opf_claimed_isbn10", "0743421221"),
                             ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                             ("private_source_edition_verified", True)):
                with self.subTest(idx=idx, field=key):
                    doc = copy.deepcopy(self.doc)
                    doc["rows"][idx][key] = val
                    with self.assertRaises(ValueError):
                        validate(doc, self.opf)

    def test_source_orthographic_disagreement_persists(self):
        self.assertEqual("OPF_MICHEAL_VS_PUBLISHER_MICHAEL_CREATOR_UNRESOLVED",
                         self.doc["rows"][0]["source_anomaly"])
        self.assertEqual("OPF_DRAGONS_S_VS_PUBLISHER_DRAGONS_TITLE_UNRESOLVED",
                         self.doc["rows"][6]["source_anomaly"])
        for idx, field, val in ((0, "source_anomaly", None),
                                (0, "publisher_title", "MICHEAL"),
                                (0, "creator_credits", ["Micheal Jan Friedman", "Kevin Ryan"]),
                                (6, "source_anomaly", None),
                                (6, "opf_local_title", "DRAGON'S HONOR")):
            with self.subTest(idx=idx, field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][idx][field] = val
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_fail_closed_on_source_or_product_swap(self):
        for idx, field, val in ((0, "opf_entry_sha256", "0" * 64),
                                (0, "opf_claimed_isbn10", "074342123X"),
                                (2, "isbn13", "9780743421157"),
                                (2, "publisher_title", "Requiem"),
                                (4, "publisher_page", "https://www.simonandschuster.com.evil.test/books/x"),
                                (4, "publisher_page", "https://www.simonandschuster.com/books/Into-the-Nebula/Gene-DeWeese/Star-Trek-The-Next-Generation/9780743421379?x=1"),
                                (4, "publisher_extent_pages", -5),
                                (4, "publisher_date_us", "2000-99-99"),
                                (6, "publisher_host", "www.simonandschuster.net")):
            with self.subTest(idx=idx, field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][idx][field] = val
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_no_effects_or_private_leaks(self):
        for key, val in (("accepted_work_effect", "ADDED"), ("accepted_source_binding_effect", "BOUND"),
                         ("accepted_evidence_effect", "PROMOTED"), ("coverage_effect", "CLOSE_READ"),
                         ("public_explorer_effect", "YES"), ("full_text_read", True),
                         ("copyrighted_text_exported", True), ("artwork_release_effect", "APPROVED"),
                         ("private_manifestation_binding_verified", True),
                         ("publisher_snapshot_bytes_held", True),
                         ("synopsis_publication_effect", "PUBLISHED"),
                         ("independent_publisher_families", 7)):
            with self.subTest(field=key):
                doc = copy.deepcopy(self.doc)
                doc[key] = val
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)
        for key, val in (("private_member_path", "D:/Private/novel.epub"),
                         ("copyrighted_ebook_excerpt", "Once upon a time"),
                         ("canonical_work_id", "TNG-080")):
            with self.subTest(field=key):
                doc = copy.deepcopy(self.doc)
                doc["rows"][0][key] = val
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_row_swap_opf_mutation_rejected(self):
        for change in (lambda d: d["rows"].reverse(), lambda d: d["rows"].pop()):
            doc = copy.deepcopy(self.doc)
            change(doc)
            with self.assertRaises(ValueError):
                validate(doc, self.opf)
        source = copy.deepcopy(self.opf)
        next(r for r in source["rows"] if r["source_local_id"] == "opf-local:0081")["isbn_checksum_valid"] = ["0743421221"]
        with self.assertRaises(ValueError):
            validate(self.doc, source)


if __name__ == "__main__":
    unittest.main()
