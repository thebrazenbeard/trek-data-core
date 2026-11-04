"""Fail-closed regression tests for literary public-receipt cross-packet audit."""

import copy
import unittest

import audit


class CrossPacketTest(unittest.TestCase):
    def setUp(self):
        self.original = audit.load_pinned(
            audit.ORIGINAL / "RECEIPT.json", audit.PUBLIC_RECEIPT_SHA256
        )
        self.converted = audit.load_pinned(
            audit.CONVERTED / "CHAPTER_INDEX.json", audit.PUBLIC_INDEX_SHA256
        )

    def test_current_public_packets_consistent_but_unadmitted(self):
        report = audit.validate(self.original, self.converted)
        self.assertEqual(report["coverage_effect"], "NONE")
        self.assertFalse(report["private_conversion_text_equivalence_verified"])
        self.assertEqual(report["converted_chapter_segments_observed"], 69)

    def test_changed_original_opf_digest_rejected(self):
        candidate = copy.deepcopy(self.original)
        candidate["converted_opf_member_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            audit.validate(candidate, self.converted)

    def test_changed_converted_html_digest_rejected(self):
        candidate = copy.deepcopy(self.converted)
        candidate["html_spine_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            audit.validate(self.original, candidate)

    def test_false_original_equivalence_promotion_rejected(self):
        candidate = copy.deepcopy(self.original)
        candidate["conversion_equivalence_verified"] = True
        with self.assertRaises(ValueError):
            audit.validate(candidate, self.converted)

    def test_fake_source_bound_coverage_rejected(self):
        candidate = copy.deepcopy(self.converted)
        candidate["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            audit.validate(self.original, candidate)

    def test_missing_chapter_rejected(self):
        candidate = copy.deepcopy(self.converted)
        candidate["chapters"].pop()
        candidate["chapter_count"] = 68
        with self.assertRaises(ValueError):
            audit.validate(self.original, candidate)

    def test_book_text_field_not_permitted(self):
        candidate = copy.deepcopy(self.converted)
        candidate["copyrighted_full_text"] = "disallowed"
        with self.assertRaises(ValueError):
            audit.validate(self.original, candidate)


if __name__ == "__main__":
    unittest.main()
