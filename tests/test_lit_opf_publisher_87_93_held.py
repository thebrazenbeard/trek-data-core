"""Falsifiers for held OPF and official publisher metadata, local IDs 0087–0093."""

import copy
import json
import unittest

from proposals.research.lit_opf_publisher_87_93_20261104.validate import (
    DATA, ORIGINAL_OPF, validate,
)


class Publisher8793Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))

    def test_seven_held_not_accepted(self):
        self.assertEqual((7, 4, 2, 1), validate(self.packet, self.opf))
        self.assertEqual([f"opf-local:{n:04d}" for n in range(87, 94)],
                         [row["opf_local_id"] for row in self.packet["rows"]])
        self.assertEqual("HELD_METADATA_ONLY_NOT_ACCEPTED", self.packet["status"])

    def test_nonoverlap_except_documented_owner_isbn_collision(self):
        root = DATA.parents[3]
        earlier = []
        for folder in (
            "lit_opf_publisher_seven_20261104",
            "lit_opf_publisher_nine_20261104",
            "lit_opf_publisher_71_79_20261104",
            "lit_opf_publisher_80_86_20261104",
        ):
            earlier.extend(json.loads((root / "proposals/research" / folder / "records.json")
                                    .read_text(encoding="utf-8"))["rows"])
        self.assertFalse({r["opf_local_id"] for r in earlier} &
                         {r["opf_local_id"] for r in self.packet["rows"]})
        self.assertFalse({r["isbn13"] for r in earlier} &
                         {r["isbn13"] for r in self.packet["rows"]})
        collided = self.packet["rows"][4]
        self.assertEqual("THE DEATH OF PRINCES", collided["opf_local_title"])
        self.assertEqual("9780743421225", collided["opf_isbn13_checksum_conversion"])
        self.assertEqual("9780743422888", collided["isbn13"])
        self.assertEqual("ISBN_TITLE_CONFLICT_UNRESOLVED", collided["opf_edition_crosswalk_state"])
        self.assertEqual("Balance of Power", next(r["publisher_title"] for r in earlier
                                                  if r["isbn13"] == collided["opf_isbn13_checksum_conversion"]))

    def test_conflict_is_not_misrepresented_as_identity_or_isbn_match(self):
        self.assertEqual("OPF_DEATH_OF_PRINCES_ISBN_POINTS_TO_BALANCE_OF_POWER",
                         self.packet["rows"][4]["source_anomaly"])
        for idx, field, value in (
            (4, "source_anomaly", None),
            (4, "opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
            (4, "isbn13", "9780743421225"),
            (4, "opf_isbn13_checksum_conversion", "9780743422888"),
            (4, "publisher_title", "Balance of Power"),
            (4, "private_source_edition_verified", True),
        ):
            with self.subTest(field=field, index=idx):
                packet = copy.deepcopy(self.packet)
                packet["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(packet, self.opf)

    def test_missing_owner_isbn_and_creator_not_backfilled(self):
        for idx in (2, 6):
            self.assertEqual("UNVERIFIED_LOCAL_TITLE_ONLY",
                             self.packet["rows"][idx]["opf_edition_crosswalk_state"])
            for field, value in (
                ("opf_claimed_isbn10", "0743421205"),
                ("opf_isbn13_checksum_conversion", "9780743421201"),
                ("opf_edition_crosswalk_state", "ISBN_CHECKSUM_ALIGNMENT_ONLY"),
                ("private_source_edition_verified", True),
            ):
                with self.subTest(field=field, index=idx):
                    packet = copy.deepcopy(self.packet)
                    packet["rows"][idx][field] = value
                    with self.assertRaises(ValueError):
                        validate(packet, self.opf)

    def test_publisher_metadata_spoof_rejected(self):
        for idx, field, value in (
            (0, "opf_entry_sha256", "0" * 64),
            (1, "creator_credits", ["J.M. Dillard"]),
            (2, "publisher_page", "https://www.simonandschuster.com.evil.test/foo"),
            (3, "publisher_page", self.packet["rows"][3]["publisher_page"] + "?edition=1"),
            (4, "publisher_date_us", "2099-99-99"),
            (5, "publisher_extent_pages", -1),
            (5, "isbn13", "9780743421256"),
            (6, "publisher_host", "simonandschuster.net"),
        ):
            with self.subTest(field=field, index=idx):
                packet = copy.deepcopy(self.packet)
                packet["rows"][idx][field] = value
                with self.assertRaises(ValueError):
                    validate(packet, self.opf)

    def test_no_private_leak_or_coverage_promotion(self):
        for field, value in (
            ("accepted_work_effect", "ADDED"),
            ("accepted_source_binding_effect", "BOUND"),
            ("accepted_evidence_effect", "YES"),
            ("coverage_effect", "CLOSE_READ"),
            ("full_text_read", True),
            ("private_manifestation_binding_verified", True),
            ("copyrighted_text_exported", True),
            ("public_explorer_effect", "ADDED"),
            ("independent_publisher_families", 7),
        ):
            with self.subTest(field=field):
                packet = copy.deepcopy(self.packet)
                packet[field] = value
                with self.assertRaises(ValueError):
                    validate(packet, self.opf)
        for field in ("private_member_path", "copyrighted_excerpt", "accepted_work_id"):
            packet = copy.deepcopy(self.packet)
            packet["rows"][0][field] = "unsafe"
            with self.assertRaises(ValueError):
                validate(packet, self.opf)

    def test_source_and_position_mutations(self):
        for method in (lambda d: d["rows"].reverse(), lambda d: d["rows"].pop()):
            packet = copy.deepcopy(self.packet)
            method(packet)
            with self.assertRaises(ValueError):
                validate(packet, self.opf)
        opf = copy.deepcopy(self.opf)
        next(r for r in opf["rows"] if r["source_local_id"] == "opf-local:0091")\
            ["isbn_checksum_valid"] = ["074342288X"]
        with self.assertRaises(ValueError):
            validate(self.packet, opf)


if __name__ == "__main__":
    unittest.main()
