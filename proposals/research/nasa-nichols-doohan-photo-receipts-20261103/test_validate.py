#!/usr/bin/env python3
"""Adversarial invariants for nonpublishing NASA-history photograph research."""
from __future__ import annotations

import copy
import unittest

from validate import PACKET, read_json, strict_pairs, validate


class TestNasaHistoryImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(PACKET)

    def fresh(self):
        return copy.deepcopy(self.packet)

    def test_valid_three_images(self):
        validate(self.fresh())

    def test_reject_duplicate_candidate(self):
        p = self.fresh()
        p["records"][2]["candidate_id"] = p["records"][0]["candidate_id"]
        with self.assertRaisesRegex(ValueError, "repeated candidate"):
            validate(p)

    def test_reject_extra_candidate(self):
        p = self.fresh()
        p["records"].append(copy.deepcopy(p["records"][0]))
        with self.assertRaisesRegex(ValueError, "three bounded"):
            validate(p)

    def test_reject_wrong_event_date(self):
        p = self.fresh()
        p["records"][0]["subject_date"] = "1977-03-04"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_upgraded_date_precision(self):
        p = self.fresh()
        p["records"][0]["subject_date_precision"] = "DAY"
        with self.assertRaisesRegex(ValueError, "unsafe fictional"):
            validate(p)

    def test_reject_new_episode_binding(self):
        p = self.fresh()
        p["records"][0]["fictional_episode_row_id"] = "legacy:s1:tos:000"
        with self.assertRaisesRegex(ValueError, "unsafe fictional"):
            validate(p)

    def test_reject_new_film_binding(self):
        p = self.fresh()
        p["records"][2]["fictional_film_row_id"] = "film:star-trek"
        with self.assertRaisesRegex(ValueError, "unsafe fictional"):
            validate(p)

    def test_reject_invented_fictional_still(self):
        p = self.fresh()
        p["records"][1]["fictional_work_illustration"] = True
        with self.assertRaisesRegex(ValueError, "unsafe fictional"):
            validate(p)

    def test_reject_source_image_swap(self):
        p = self.fresh()
        p["records"][0]["source_image_sha256"] = "e" * 64
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_resized_image_url(self):
        p = self.fresh()
        p["records"][0]["source_image_url"] += "?w=985"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_photo_credit_forgery(self):
        p = self.fresh()
        p["records"][2]["individual_photo_credit"] = "NASA public domain"
        with self.assertRaisesRegex(ValueError, "unsafe fictional"):
            validate(p)

    def test_reject_laundered_la_times_credit(self):
        p = self.fresh()
        p["records"][2]["photo_credit_status"] = "NASA_CONFIRMED"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_page_receipt_swap(self):
        p = self.fresh()
        p["source_page_html_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_unattributed_receipt_client(self):
        p = self.fresh()
        p["receipt_client"] = "unknown"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_rights_overclaim(self):
        p = self.fresh()
        p["rights_basis"] = "NASA released everything unrestricted."
        with self.assertRaisesRegex(ValueError, "blanket rights"):
            validate(p)

    def test_reject_display_url(self):
        p = self.fresh()
        p["records"][1]["display_url"] = p["records"][1]["source_image_url"]
        with self.assertRaisesRegex(ValueError, "public display"):
            validate(p)

    def test_reject_coverage_promotion(self):
        p = self.fresh()
        p["coverage_effect"] = "DISCOVERED"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(p)

    def test_reject_unknown_rights_grant_field(self):
        p = self.fresh()
        p["records"][0]["globally_cleared"] = True
        with self.assertRaisesRegex(ValueError, "schema changed"):
            validate(p)

    def test_reject_removed_falsifier(self):
        p = self.fresh()
        p["records"][0]["open_rights_falsifier"] = "Nothing to check"
        with self.assertRaisesRegex(ValueError, "uncertainty removed"):
            validate(p)

    def test_reject_duplicate_json_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            strict_pairs([("id", 1), ("id", 2)])


if __name__ == "__main__":
    unittest.main()
