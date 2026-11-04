"""Local-only falsifiers for owner OPF/publisher leads 0094–0100."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_94_100_20261104.validate import (
    DATA, ORIGINAL_OPF, validate,
)


class Publisher94100Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_bounded_held_packet_with_no_owner_isbn_matches(self):
        self.assertEqual((7, 0, 1, 1), validate(self.packet, self.opf))
        self.assertEqual([f"opf-local:{n:04d}" for n in range(94, 101)],
                         [r["opf_local_id"] for r in self.packet["rows"]])
        self.assertTrue(all(r["opf_claimed_isbn10"] is None for r in self.packet["rows"]))
        self.assertTrue(all(r["opf_isbn13_checksum_conversion"] is None for r in self.packet["rows"]))

    def test_distinct_source_locals_and_publisher_editions(self):
        root = DATA.parents[3]
        earlier = []
        for folder in ("lit_opf_publisher_seven_20261104", "lit_opf_publisher_nine_20261104",
                       "lit_opf_publisher_71_79_20261104", "lit_opf_publisher_80_86_20261104",
                       "lit_opf_publisher_87_93_20261104"):
            earlier.extend(json.loads((root / "proposals/research" / folder / "records.json")
                                    .read_text(encoding="utf-8"))["rows"])
        self.assertFalse({r["opf_local_id"] for r in earlier} &
                         {r["opf_local_id"] for r in self.packet["rows"]})
        self.assertFalse({r["isbn13"] for r in earlier} &
                         {r["isbn13"] for r in self.packet["rows"]})

    def test_actual_creator_contradiction_cannot_be_laundered(self):
        strike = self.packet["rows"][2]
        self.assertEqual("William C. Deets &Dean Williams", strike["opf_local_creator"][0])
        self.assertEqual(["Greg Cox"], strike["creator_credits"])
        self.assertEqual("LOCAL_OPF_CREATOR_CONFLICTS_WITH_PUBLISHER_GREG_COX_UNRESOLVED",
                         strike["source_anomaly"])
        self.assertEqual("TITLE_ONLY_CREATOR_CONFLICT_UNRESOLVED",
                         strike["opf_edition_crosswalk_state"])
        for field, value in (("source_anomaly", None), ("creator_credits", ["William C. Deets", "Dean Williams"]),
                             ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                             ("private_source_edition_verified", True)):
            with self.subTest(field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][2][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_duplicate_tng_046_ordinal_not_reconciled(self):
        self.assertIn("TNG 046", self.packet["rows"][1]["opf_local_title"])
        self.assertEqual("LOCAL_TNG_046_COLLIDES_WITH_0093_TO_STORM_HEAVEN_UNRESOLVED",
                         self.packet["rows"][1]["source_anomaly"])
        for field, value in (("source_anomaly", None),
                             ("opf_local_title", "Star Trek - TNG 048 - Q-Zone"),
                             ("publisher_title", "To Storm Heaven")):
            with self.subTest(field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][1][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_no_owner_isbn_or_creator_insertions(self):
        for idx in range(7):
            for field, value in (("opf_claimed_isbn10", "0743421221"),
                                 ("opf_isbn13_checksum_conversion", "9780743421225"),
                                 ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY")):
                with self.subTest(idx=idx, field=field):
                    d = copy.deepcopy(self.packet)
                    d["rows"][idx][field] = value
                    with self.assertRaises(ValueError):
                        validate(d, self.opf)

    def test_official_page_and_metadata_forgeries_fail_closed(self):
        for idx, field, value in ((0, "isbn13", "9780671041021"),
                                  (0, "publisher_page", "https://www.simonandschuster.com.evil.test/x"),
                                  (1, "publisher_date_us", "1999-99-99"),
                                  (2, "opf_entry_sha256", "0" * 64),
                                  (3, "publisher_extent_pages", -1),
                                  (4, "creator_credits", ["Dean W. Smith"]),
                                  (5, "publisher_page", self.packet["rows"][5]["publisher_page"]+"?x=1"),
                                  (6, "held_synopsis", "This was definitely close-read.")):
            with self.subTest(idx=idx, field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_no_private_prose_or_accepted_effects(self):
        for field, value in (("accepted_work_effect", "ADDED"),
                             ("accepted_source_binding_effect", "BOUND"),
                             ("accepted_evidence_effect", "YES"),
                             ("coverage_effect", "CLOSE_READ"),
                             ("copyrighted_text_exported", True),
                             ("full_text_read", True),
                             ("private_manifestation_binding_verified", True),
                             ("public_explorer_effect", "SHIPPED"),
                             ("independent_publisher_families", 7)):
            d = copy.deepcopy(self.packet)
            d[field] = value
            with self.assertRaises(ValueError):
                validate(d, self.opf)
        for field in ("copyrighted_ebook_excerpt", "canonical_work_id", "private_file_path"):
            d = copy.deepcopy(self.packet)
            d["rows"][0][field] = "forbidden"
            with self.assertRaises(ValueError):
                validate(d, self.opf)

    def test_owner_row_changed_or_reordered_fails(self):
        d = copy.deepcopy(self.packet)
        d["rows"].reverse()
        with self.assertRaises(ValueError):
            validate(d, self.opf)
        d = copy.deepcopy(self.opf)
        next(r for r in d["rows"] if r["source_local_id"] == "opf-local:0096")\
            ["creator"] = ["Greg Cox"]
        with self.assertRaises(ValueError):
            validate(self.packet, d)


if __name__ == "__main__":
    unittest.main()
