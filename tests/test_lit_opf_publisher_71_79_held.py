"""Red/green anti-promotion tests for publisher leads OPF 0071–0079."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_71_79_20261104.validate import DATA, ORIGINAL_OPF, validate


class Publisher7179HeldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_held_nine_rows_seven_isbn_two_title_only(self):
        self.assertEqual((9, 7, 2), validate(self.doc, self.opf))

    def test_nonoverlap_and_order(self):
        self.assertEqual([f"opf-local:{n:04d}" for n in range(71, 80)],
                         [row["opf_local_id"] for row in self.doc["rows"]])
        older = []
        root = DATA.parents[3]
        for name in ("lit_opf_publisher_seven_20261104", "lit_opf_publisher_nine_20261104"):
            older.extend(json.loads((root / "proposals/research" / name / "records.json")
                                    .read_text(encoding="utf-8"))["rows"])
        draft = json.loads((root / "proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.json")
                           .read_text(encoding="utf-8"))["rows"]
        self.assertFalse({row["opf_local_id"] for row in self.doc["rows"]} &
                         {row["opf_local_id"] for row in older})
        self.assertFalse({row["isbn13"] for row in self.doc["rows"]} &
                         {row["isbn13"] for row in older + draft})

    def test_title_creator_only_rows_remain_unverified(self):
        for index in (0, 1):
            self.assertIsNone(self.doc["rows"][index]["opf_claimed_isbn10"])
            self.assertEqual("UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
                             self.doc["rows"][index]["opf_edition_crosswalk_state"])
            for field, value in (("opf_claimed_isbn10", "0743421035"),
                                 ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                                 ("private_source_edition_verified", True),
                                 ("work_id", "work:fake")):
                with self.subTest(index=index, field=field):
                    doc = copy.deepcopy(self.doc)
                    doc["rows"][index][field] = value
                    with self.assertRaises(ValueError):
                        validate(doc, self.opf)

    def test_promotion_or_rights_cannot_be_inferred(self):
        for field, bad in (("accepted_work_effect", "ADDED"), ("coverage_effect", "FULL_TEXT_AVAILABLE"),
                           ("accepted_source_binding_effect", "ADDED"), ("accepted_evidence_effect", "ADDED"),
                           ("public_explorer_effect", "YES"), ("full_text_read", True),
                           ("private_manifestation_binding_verified", True),
                           ("copyrighted_text_exported", True), ("synopsis_publication_effect", "PUBLISHED"),
                           ("artwork_release_effect", "APPROVED")):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc[field] = bad
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_isbn_creator_and_source_spoofs_rejected(self):
        for idx, field, bad in ((2, "isbn13", "9780743421096"),
                                (2, "opf_claimed_isbn10", "0743421094"),
                                (2, "opf_entry_sha256", "0" * 64),
                                (2, "publisher_title", "The Romulan Prize"),
                                (8, "creator_credits", ["Greg Brodeur", "Dave Galanter"]),
                                (7, "publisher_host", "www.simonandschuster.com"),
                                (7, "publisher_page", "https://www.simonandschuster.net.evil.test/books/x"),
                                (7, "publisher_page", "https://www.simonandschuster.net/books/Star-Trek-The-Next-Generation-Debtors-Planet/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421133?q=1"),
                                (5, "publisher_extent_pages", -3),
                                (5, "publisher_date_us", "2000-99-99"),
                                (0, "source_anomaly", None)):
            with self.subTest(index=idx, field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][idx][field] = bad
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_source_schema_and_private_data_spoofs_rejected(self):
        for field, bad in (("opf_metadata_sha256", "0" * 64),
                           ("independent_publisher_families", 9),
                           ("publisher_upstream_family", "nine-independent-sources"),
                           ("publisher_snapshot_bytes_held", True)):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc[field] = bad
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)
        for field, bad in (("private_member_path", "D:/Private/book.lit"),
                           ("ebook_full_text", "Do not copy"),
                           ("cover_image", "https://example.com/x.jpg")):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][0][field] = bad
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_original_opf_mutation_and_row_swap_rejected(self):
        for mutation in (lambda d: d["rows"].reverse(),
                         lambda d: d["rows"].pop()):
            doc = copy.deepcopy(self.doc)
            mutation(doc)
            with self.assertRaises(ValueError):
                validate(doc, self.opf)
        original = copy.deepcopy(self.opf)
        next(r for r in original["rows"] if r["source_local_id"] == "opf-local:0071")["isbn_checksum_valid"] = ["074342103X"]
        with self.assertRaises(ValueError):
            validate(self.doc, original)


if __name__ == "__main__":
    unittest.main()
