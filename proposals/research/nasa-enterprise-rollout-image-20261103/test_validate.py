#!/usr/bin/env python3
"""Adversarial tests for the nonpublishing NASA photo receipt."""
from __future__ import annotations

import copy
import unittest

from validate import PACKET, read_json, validate


class TestNasaHistoricalPhotoProposal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(PACKET)

    def modified(self):
        return copy.deepcopy(self.packet)

    def test_valid_receipt(self):
        validate(self.modified())

    def test_reject_episode_binding(self):
        packet = self.modified()
        packet["candidate"]["fictional_episode_row_id"] = "legacy:s1:tos:000"
        with self.assertRaisesRegex(ValueError, "fiction binding"):
            validate(packet)

    def test_reject_film_binding(self):
        packet = self.modified()
        packet["candidate"]["fictional_film_row_id"] = "film:motion-picture"
        with self.assertRaisesRegex(ValueError, "fiction binding"):
            validate(packet)

    def test_reject_episode_still_claim(self):
        packet = self.modified()
        packet["candidate"]["fictional_work_illustration"] = True
        with self.assertRaisesRegex(ValueError, "fiction binding"):
            validate(packet)

    def test_reject_public_display(self):
        packet = self.modified()
        packet["public_display_eligible"] = True
        with self.assertRaisesRegex(ValueError, "unauthorized effect"):
            validate(packet)

    def test_reject_added_hotlink(self):
        packet = self.modified()
        packet["candidate"]["display_url"] = packet["candidate"]["source_image_url"]
        with self.assertRaisesRegex(ValueError, "public display"):
            validate(packet)

    def test_reject_governed_coverage(self):
        packet = self.modified()
        packet["coverage_effect"] = "DISCOVERED"
        with self.assertRaisesRegex(ValueError, "unauthorized effect"):
            validate(packet)

    def test_reject_wrong_persons_or_event_date(self):
        packet = self.modified()
        packet["candidate"]["subject_date"] = "1976-09-08"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(packet)

    def test_reject_source_image_transform(self):
        packet = self.modified()
        packet["candidate"]["source_image_url"] += "?w=1041"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(packet)

    def test_reject_forged_image_digest(self):
        packet = self.modified()
        packet["candidate"]["source_image_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(packet)

    def test_reject_image_bytes_as_boolean(self):
        packet = self.modified()
        packet["candidate"]["source_image_bytes"] = True
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(packet)

    def test_reject_rights_page_swap(self):
        packet = self.modified()
        packet["candidate"]["rights_page_html_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(packet)

    def test_reject_rights_caveat_removal(self):
        packet = self.modified()
        packet["candidate"]["marks_endorsement_caveat"] = "No problem."
        with self.assertRaisesRegex(ValueError, "critical rights"):
            validate(packet)

    def test_reject_unknown_rights_grant(self):
        packet = self.modified()
        packet["candidate"]["copyright_cleared_forever"] = True
        with self.assertRaisesRegex(ValueError, "schema changed"):
            validate(packet)

    def test_reject_changed_scope(self):
        packet = self.modified()
        packet["identity_scope"] = "GLOBAL_WORK"
        with self.assertRaisesRegex(ValueError, "unauthorized effect"):
            validate(packet)

    def test_reject_duplicate_json_key(self):
        from validate import strict_pairs
        with self.assertRaisesRegex(ValueError, "duplicate"):
            strict_pairs([("same", 1), ("same", 2)])


if __name__ == "__main__":
    unittest.main()
