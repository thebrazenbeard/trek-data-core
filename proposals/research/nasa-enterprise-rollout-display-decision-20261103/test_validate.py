#!/usr/bin/env python3
"""Adversarial checks for nonpublishing NASA photo display-decision packet."""
from __future__ import annotations

import copy
import unittest

from validate import PACKET, read_json, strict_pairs, validate


class TestNasaDisplayDecision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(PACKET)

    def changed(self):
        return copy.deepcopy(self.packet)

    def test_valid_research_decision(self):
        validate(self.changed())

    def test_reject_source_image_change(self):
        d = self.changed()
        d["historical_source_image_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_resized_img_url(self):
        d = self.changed()
        d["historical_source_og_image_exact_url"] += "?w=1041"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_creator_invention(self):
        d = self.changed()
        d["individual_photographer"] = "NASA Astronaut"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_fake_copyright_clearance(self):
        d = self.changed()
        d["individual_third_party_copyright_notice_on_source_page"] = "NONE_CONFIRMED"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_publication_flag(self):
        d = self.changed()
        d["public_display_eligible"] = True
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_site_effect(self):
        d = self.changed()
        d["site_effect"] = "DEPLOYED"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_episode_crosswalk(self):
        d = self.changed()
        d["fictional_episode_row_id"] = "legacy:s1:tos:000"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_fictional_illustration(self):
        d = self.changed()
        d["fictional_work_illustration"] = True
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_nasa_logo_as_branding(self):
        d = self.changed()
        d["policy_support"]["nasa_logo_seal_as_interface_branding"] = True
        with self.assertRaisesRegex(ValueError, "policy caveat"):
            validate(d)

    def test_reject_unconditional_cdn_embedding(self):
        d = self.changed()
        d["policy_support"]["remote_cdn_img_src_embed"] = "ALLOWED_UNCONDITIONALLY"
        with self.assertRaisesRegex(ValueError, "policy caveat"):
            validate(d)

    def test_reject_unrestricted_mirroring(self):
        d = self.changed()
        d["policy_support"]["locally_mirrored_binary"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "policy caveat"):
            validate(d)

    def test_reject_cc0_inference(self):
        d = self.changed()
        d["policy_support"]["global_public_domain_or_cc0_claim"] = True
        with self.assertRaisesRegex(ValueError, "policy caveat"):
            validate(d)

    def test_reject_rights_review_bypass(self):
        d = self.changed()
        d["independent_rights_review"] = "GO"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_other_nasa_photos_promotion(self):
        d = self.changed()
        d["separate_held_photos_must_remain_held"] = False
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_removed_nasa_disclaimer(self):
        d = self.changed()
        d["proposed_credit"] = "NASA historical image"
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_fictional_caption(self):
        d = self.changed()
        d["proposed_caption"] = "The USS Enterprise crew poses for a mission photograph."
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_append_false_canonicality_to_valid_caption(self):
        d = self.changed()
        d["proposed_caption"] += " NASA states that this scene occurs in Star Trek canon."
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_append_fake_nasa_endorsement_to_valid_credit(self):
        d = self.changed()
        d["proposed_credit"] += " This archive is officially NASA-approved and endorsed by NASA."
        with self.assertRaisesRegex(ValueError, "pin changed"):
            validate(d)

    def test_reject_append_fictional_episode_to_valid_falsifier(self):
        d = self.changed()
        d["open_falsifiers"][3] += " NASA confirms this fictional scene as episode canon."
        with self.assertRaisesRegex(ValueError, "falsifier text pin changed"):
            validate(d)

    def test_reject_append_third_party_clearance_to_valid_falsifier(self):
        d = self.changed()
        d["open_falsifiers"][0] += " All third-party publicity rights are now fully cleared."
        with self.assertRaisesRegex(ValueError, "falsifier text pin changed"):
            validate(d)

    def test_reject_falsifier_elision(self):
        d = self.changed()
        d["open_falsifiers"] = []
        with self.assertRaisesRegex(ValueError, "falsifiers removed"):
            validate(d)

    def test_reject_unexpected_rights_grant_field(self):
        d = self.changed()
        d["licensed_worldwide"] = True
        with self.assertRaisesRegex(ValueError, "schema changed"):
            validate(d)

    def test_reject_duplicate_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            strict_pairs([("rights", 1), ("rights", 2)])


if __name__ == "__main__":
    unittest.main()
