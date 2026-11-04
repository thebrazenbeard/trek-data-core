"""Falsifiers for separately HELD owner OPF and publisher editions 0108-0114."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_108_114_20261104.validate import (
    DATA, ORIGINAL_OPF, validate,
)


class Publisher108114Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_held_tranche_not_accepted(self):
        self.assertEqual((7, 0, 1, 6), validate(self.packet, self.opf))
        self.assertEqual([f"opf-local:{n:04d}" for n in range(108, 115)],
                         [r["opf_local_id"] for r in self.packet["rows"]])
        for field in ("accepted_work_effect", "accepted_source_binding_effect",
                      "accepted_evidence_effect", "coverage_effect", "public_explorer_effect",
                      "synopsis_publication_effect"):
            self.assertEqual("NONE", self.packet[field])

    def test_nonoverlap_with_53_prior_source_local_rows(self):
        root = DATA.parents[3]
        folders = ("lit_opf_publisher_seven_20261104", "lit_opf_publisher_nine_20261104",
                   "lit_opf_publisher_71_79_20261104", "lit_opf_publisher_80_86_20261104",
                   "lit_opf_publisher_87_93_20261104", "lit_opf_publisher_94_100_20261104",
                   "lit_opf_publisher_101_107_20261104")
        prior = [r for folder in folders for r in json.loads(
            (root / "proposals/research" / folder / "records.json").read_text(encoding="utf-8"))["rows"]]
        self.assertEqual(53, len(prior))
        for key in ("opf_local_id", "isbn13"):
            self.assertFalse({r[key] for r in prior} & {r[key] for r in self.packet["rows"]})

    def test_a_hard_rain_owner_isbn_is_not_publisher_ebook(self):
        hard_rain = self.packet["rows"][1]
        self.assertEqual("074341926X", hard_rain["opf_claimed_isbn10"])
        self.assertEqual("9780743419260", hard_rain["opf_isbn13_checksum_conversion"])
        self.assertEqual("9780743419277", hard_rain["isbn13"])
        self.assertEqual("VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION",
                         hard_rain["opf_edition_crosswalk_state"])
        for field, value in (("opf_isbn13_checksum_conversion", "9780743419277"),
                             ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                             ("private_source_edition_verified", True),
                             ("source_anomaly", None)):
            with self.subTest(field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][1][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_missing_owner_identity_not_filled_in(self):
        self.assertEqual([], self.packet["rows"][3]["opf_local_creator"])
        self.assertEqual("ATimetoBeBorn", self.packet["rows"][3]["opf_local_title"])
        self.assertEqual([], self.packet["rows"][4]["opf_local_creator"])
        self.assertEqual(["Dayton Ward & Kevin Dilmore"], self.packet["rows"][5]["opf_local_creator"])
        self.assertEqual(["Kevin Dilmore", "Dayton Ward"], self.packet["rows"][5]["creator_credits"])
        for idx, field, value in ((3, "opf_local_title", "A Time to Be Born"),
                                  (3, "opf_local_creator", ["John Vornholt"]),
                                  (4, "opf_claimed_isbn10", "0743499444"),
                                  (5, "creator_credits", ["Dayton Ward", "Kevin Dilmore"])):
            with self.subTest(index=idx, field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_source_publisher_synopsis_falsifiers(self):
        for idx, field, value in ((0, "opf_entry_sha256", "0" * 64),
                                  (1, "publisher_page", "https://www.simonandschuster.com.evil.test/book"),
                                  (2, "isbn13", "9781982134907"),
                                  (3, "publisher_date_us", "2004-99-99"),
                                  (4, "publisher_extent_pages", -2),
                                  (5, "source_anomaly", None),
                                  (6, "held_synopsis", "I read the full novel.")):
            with self.subTest(index=idx, field=field):
                d = copy.deepcopy(self.packet)
                d["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(d, self.opf)

    def test_protected_or_private_effect_falsifiers(self):
        for field, value in (("accepted_work_effect", "ADDED"),
                             ("coverage_effect", "CLOSE_READ"),
                             ("full_text_read", True),
                             ("private_manifestation_binding_verified", True),
                             ("copyrighted_text_exported", True),
                             ("independent_publisher_families", 7)):
            d = copy.deepcopy(self.packet)
            d[field] = value
            with self.assertRaises(ValueError):
                validate(d, self.opf)
        d = copy.deepcopy(self.packet)
        d["rows"][0]["ebook_excerpt"] = "forbidden"
        with self.assertRaises(ValueError):
            validate(d, self.opf)

    def test_owner_source_tamper_or_order_change(self):
        d = copy.deepcopy(self.packet)
        d["rows"].reverse()
        with self.assertRaises(ValueError):
            validate(d, self.opf)
        d = copy.deepcopy(self.opf)
        next(r for r in d["rows"] if r["source_local_id"] == "opf-local:0109")\
            ["isbn_checksum_valid"] = ["0743419278"]
        with self.assertRaises(ValueError):
            validate(self.packet, d)


if __name__ == "__main__":
    unittest.main()
