"""Hostile falsifiers for owner OPF versus official edition leads 0101–0107."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_101_107_20261104.validate import (
    DATA, ORIGINAL_OPF, validate,
)


class Publisher101107Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_exact_held_counts(self):
        self.assertEqual((7, 1, 2, 4), validate(self.packet, self.opf))
        self.assertEqual([f"opf-local:{n:04d}" for n in range(101, 108)],
                         [r["opf_local_id"] for r in self.packet["rows"]])
        self.assertEqual("HELD_METADATA_ONLY_NOT_ACCEPTED", self.packet["status"])

    def test_prior_46_held_distinct(self):
        root = DATA.parents[3]
        earlier = []
        for folder in ("lit_opf_publisher_seven_20261104", "lit_opf_publisher_nine_20261104",
                       "lit_opf_publisher_71_79_20261104", "lit_opf_publisher_80_86_20261104",
                       "lit_opf_publisher_87_93_20261104", "lit_opf_publisher_94_100_20261104"):
            earlier.extend(json.loads((root / "proposals/research" / folder / "records.json")
                                    .read_text(encoding="utf-8"))["rows"])
        self.assertEqual(46, len(earlier))
        self.assertFalse({r["opf_local_id"] for r in earlier} &
                         {r["opf_local_id"] for r in self.packet["rows"]})
        self.assertFalse({r["isbn13"] for r in earlier} &
                         {r["isbn13"] for r in self.packet["rows"]})

    def test_gemworld_edition_divergence_remains_held(self):
        for idx, converted, publisher in ((2, "9780743421409", "9780743406772"),
                                          (3, "9780743421423", "9780743406789")):
            self.assertEqual(converted, self.packet["rows"][idx]["opf_isbn13_checksum_conversion"])
            self.assertEqual(publisher, self.packet["rows"][idx]["isbn13"])
            self.assertEqual("VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION",
                             self.packet["rows"][idx]["opf_edition_crosswalk_state"])
            for field, value in (("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                                 ("opf_isbn13_checksum_conversion", publisher),
                                 ("isbn13", converted),
                                 ("source_anomaly", None),
                                 ("private_source_edition_verified", True)):
                with self.subTest(index=idx, field=field):
                    d = copy.deepcopy(self.packet)
                    d["rows"][idx][field] = value
                    with self.assertRaises(ValueError):
                        validate(d, self.opf)

    def test_source_omissions_and_creator_spelling_order_preserved(self):
        for idx in (0, 4, 5, 6):
            for field, value in (("opf_claimed_isbn10", "0743421388"),
                                 ("opf_isbn13_checksum_conversion", "9780743421386"),
                                 ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY")):
                with self.subTest(index=idx, field=field):
                    d = copy.deepcopy(self.packet)
                    d["rows"][idx][field] = value
                    with self.assertRaises(ValueError):
                        validate(d, self.opf)
        self.assertEqual(["Dave Galanter and Greg Brodeur"], self.packet["rows"][6]["opf_local_creator"])
        self.assertEqual(["Greg Brodeur", "Dave Galanter"], self.packet["rows"][6]["creator_credits"])
        for idx, field, value in ((5, "opf_local_title", "Diplomatic Implausibility"),
                                  (6, "creator_credits", ["Dave Galanter", "Greg Brodeur"]),
                                  (6, "source_anomaly", None)):
            d = copy.deepcopy(self.packet)
            d["rows"][idx][field] = value
            with self.assertRaises(ValueError):
                validate(d, self.opf)

    def test_falsified_publisher_page_field_or_source_provenance(self):
        for idx, field, value in ((0, "publisher_page", "https://www.simonandschuster.com.evil.test/book"),
                                  (1, "opf_entry_sha256", "0" * 64),
                                  (2, "publisher_extent_pages", -3),
                                  (3, "publisher_date_us", "2026-99-99"),
                                  (4, "isbn13", "9780743419505"),
                                  (5, "publisher_page", self.packet["rows"][5]["publisher_page"] + "?q=x"),
                                  (6, "held_synopsis", "I have read the complete book.")):
            with self.subTest(index=idx, field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_no_private_prose_or_authority_expansion(self):
        for field, value in (("accepted_work_effect", "ADDED"),
                             ("accepted_source_binding_effect", "BOUND"),
                             ("accepted_evidence_effect", "PROMOTED"),
                             ("coverage_effect", "CLOSE_READ"),
                             ("public_explorer_effect", "PUBLISHED"),
                             ("full_text_read", True),
                             ("copyrighted_text_exported", True),
                             ("private_manifestation_binding_verified", True),
                             ("independent_publisher_families", 7)):
            d = copy.deepcopy(self.packet)
            d[field] = value
            with self.assertRaises(ValueError):
                validate(d, self.opf)
        for field in ("ebook_excerpt", "private_source_path", "canonical_work_id"):
            d = copy.deepcopy(self.packet)
            d["rows"][0][field] = "forbidden"
            with self.assertRaises(ValueError):
                validate(d, self.opf)

    def test_position_source_creator_swap(self):
        d = copy.deepcopy(self.packet)
        d["rows"].reverse()
        with self.assertRaises(ValueError):
            validate(d, self.opf)
        d = copy.deepcopy(self.opf)
        next(r for r in d["rows"] if r["source_local_id"] == "opf-local:0103")\
            ["isbn_checksum_valid"] = ["0743406771"]
        with self.assertRaises(ValueError):
            validate(self.packet, d)


if __name__ == "__main__":
    unittest.main()
