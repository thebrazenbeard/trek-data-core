"""Held successor literary 0062–0070: provenance, anomaly and zero-effect tests."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_nine_20261104.validate import (
    DATA,
    ORIGINAL_OPF,
    validate,
)


class NineLiteraryCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_held_nine_passes(self):
        self.assertEqual((9, 8, 1), validate(self.doc, self.opf))

    def test_every_row_is_new_and_contiguous(self):
        self.assertEqual([f"opf-local:{i:04d}" for i in range(62, 71)],
                         [r["opf_local_id"] for r in self.doc["rows"]])
        earlier = json.loads((DATA.parents[3] /
                              "proposals/research/lit_opf_publisher_seven_20261104/records.json")
                             .read_text(encoding="utf-8"))
        self.assertFalse({r["opf_local_id"] for r in earlier["rows"]} &
                         {r["opf_local_id"] for r in self.doc["rows"]})
        older_draft = json.loads((DATA.parents[3] /
                                  "proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.json")
                                 .read_text(encoding="utf-8"))
        self.assertFalse({r["isbn13"] for r in older_draft["rows"]} &
                         {r["isbn13"] for r in self.doc["rows"]})
        self.assertFalse({r["isbn13"] for r in earlier["rows"]} &
                         {r["isbn13"] for r in self.doc["rows"]})

    def test_scope_promotion_rejected(self):
        for key, bad in (("accepted_work_effect", "CREATED"), ("coverage_effect", "CLOSE_READ"),
                         ("accepted_source_binding_effect", "VERIFIED"),
                         ("accepted_evidence_effect", "EVIDENCE_ADDED"),
                         ("public_explorer_effect", "YES"), ("full_text_read", True),
                         ("copyrighted_text_exported", True),
                         ("private_manifestation_binding_verified", True),
                         ("synopsis_publication_effect", "PUBLISHED")):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc[key] = bad
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_title_only_q_in_law_remains_unverified(self):
        q = self.doc["rows"][4]
        self.assertIsNone(q["opf_claimed_isbn10"])
        self.assertEqual("UNVERIFIED_LOCAL_TITLE_ONLY", q["opf_edition_crosswalk_state"])
        for field, value in (("opf_claimed_isbn10", "0671040992"),
                             ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                             ("private_source_edition_verified", True),
                             ("opus_work_id", "work:q-in-law")):
            with self.subTest(field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][4][field] = value
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_perchance_typo_not_silently_reconciled(self):
        self.assertEqual("OPF_PRECHANCE_VS_PUBLISHER_PERCHANCE_UNRESOLVED",
                         self.doc["rows"][5]["source_anomaly"])
        for index, field, value in ((5, "source_anomaly", None),
                                    (5, "publisher_title", "PRECHANCE TO DREAM"),
                                    (5, "opf_local_title", "Perchance to Dream"),
                                    (0, "source_anomaly", "OPF_PRECHANCE_VS_PUBLISHER_PERCHANCE_UNRESOLVED")):
            with self.subTest(index=index, field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][index][field] = value
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_official_sibling_domain_and_isbn_stay_bound(self):
        for index, field, value in ((0, "publisher_page", "https://www.simonandschuster.net.evil.test/books/Exiles"),
                                    (0, "publisher_page", "https://www.simonandschuster.com/books/Exiles/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420945"),
                                    (0, "publisher_host", "www.simonandschuster.com"),
                                    (1, "publisher_page", "https://www.simonandschuster.com/books/Fortunes-Light/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743420952?x=1"),
                                    (2, "isbn13", "9780743420976"),
                                    (2, "opf_claimed_isbn10", "0743420977"),
                                    (8, "publisher_date_us", "2000-02-31"),
                                    (8, "publisher_extent_pages", -2)):
            with self.subTest(index=index, field=field):
                doc = copy.deepcopy(self.doc)
                doc["rows"][index][field] = value
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_drift_attack_unexpected_fields_or_fabricated_independence(self):
        for key, value in (("independent_publisher_families", 9),
                           ("publisher_upstream_family", "nine-independent-sources"),
                           ("held_edition_row_count", 30)):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc[key] = value
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)
        for key, value in (("member_raw_path", "D:/Private/book.epub"),
                           ("original_ebook_text", "copyrighted prose"),
                           ("cover_image", "https://invalid/cover.jpg")):
            with self.subTest(key=key):
                doc = copy.deepcopy(self.doc)
                doc["rows"][0][key] = value
                with self.assertRaises(ValueError):
                    validate(doc, self.opf)

    def test_opf_mutations_and_duplicate_rows_rejected(self):
        for mutation in (lambda d: d["rows"].reverse(),
                         lambda d: d["rows"].pop(),
                         lambda d: d["rows"][1].update(opf_local_id="opf-local:0062")):
            doc = copy.deepcopy(self.doc)
            mutation(doc)
            with self.assertRaises(ValueError):
                validate(doc, self.opf)
        original = copy.deepcopy(self.opf)
        next(r for r in original["rows"] if r["source_local_id"] == "opf-local:0066")["isbn_checksum_valid"] = ["0671040992"]
        with self.assertRaises(ValueError):
            validate(self.doc, original)


if __name__ == "__main__":
    unittest.main()
