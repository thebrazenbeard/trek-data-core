#!/usr/bin/env python3
"""Adversarial checks for source/rights/browser and real-world-event separation."""
from __future__ import annotations

import copy
import unittest

from validate import (CONTRACT, HELD_RENDER_STATE, prospective_render_state,
                      read_contract, unique_object, validate)


class TestNasaTrekHistoryPanelContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_contract(CONTRACT)

    def changed(self):
        return copy.deepcopy(self.packet)

    def reject_edit(self, path, value):
        data = self.changed()
        parent = data
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = value
        with self.assertRaisesRegex(ValueError, "code-owned panel contract"):
            validate(data)

    def test_valid_held_packet(self):
        validate(self.changed())

    def test_visitor_click_alone_cannot_release_unapproved_image(self):
        self.assertEqual(prospective_render_state(self.changed(), visitor_opted_in=True),
                         HELD_RENDER_STATE)

    def test_default_browser_remains_link_only(self):
        self.assertEqual(prospective_render_state(self.changed()), HELD_RENDER_STATE)

    def test_forged_approval_cannot_release_unapproved_image(self):
        with self.assertRaisesRegex(ValueError, "untrusted release"):
            prospective_render_state(self.changed(), visitor_opted_in=True,
                                     claimed_release={"rights_review": "GO", "asset": "nasa.jpg"})

    def test_no_implicit_consent_via_string(self):
        with self.assertRaisesRegex(ValueError, "explicit boolean"):
            prospective_render_state(self.changed(), visitor_opted_in="true")

    def test_reject_publication_flag(self):
        self.reject_edit(["release_gate", "public_image_display_authorized"], True)

    def test_reject_approved_release_claim_without_review(self):
        self.reject_edit(["release_gate", "approved_release_manifest_sha256"], "a" * 64)

    def test_reject_fake_asset_path(self):
        self.reject_edit(["release_gate", "approved_local_asset_path"], "./licensed-history/nasa.jpg")

    def test_reject_eager_image(self):
        self.reject_edit(["release_gate", "display_image_by_default"], True)

    def test_reject_automatic_remote_image_request(self):
        self.reject_edit(["browser_contract", "remote_image_request"], "NASA_CDN_DIRECT")

    def test_reject_persistent_consent(self):
        self.reject_edit(["browser_contract", "visitor_opt_in_storage"], "LOCAL_STORAGE")

    def test_reject_csp_nasa_host_expansion(self):
        self.reject_edit(["browser_contract", "csp_change_in_this_proposal"], "ADD_NASA_CDN")

    def test_reject_fictional_work_linkage(self):
        self.reject_edit(["event_record", "fictional_work_id"], "enterprise-film")

    def test_reject_fictional_episode_in_catalog(self):
        self.reject_edit(["placement", "fictional_media_gallery_membership"], True)

    def test_reject_new_fictional_work_count(self):
        self.reject_edit(["placement", "fictional_work_count_increment"], 1)

    def test_reject_event_type_as_episode(self):
        self.reject_edit(["event_record", "record_kind"], "FICTIONAL_EPISODE")

    def test_reject_false_date_as_photo_timestamp(self):
        self.reject_edit(["event_record", "event_date_basis"], "CAMERA_EXPOSURE_DATE_VERIFIED")

    def test_reject_unpinned_image_replacement(self):
        self.reject_edit(["event_record", "primary_image_sha256"], "0" * 64)

    def test_reject_fabricated_canonicality_appended_to_caption(self):
        self.reject_edit(["editorial", "caption"], self.packet["editorial"]["caption"] +
                         " NASA confirms this fictional scene is Trek canon.")

    def test_reject_fake_endorsement_appended_to_credit(self):
        self.reject_edit(["editorial", "credit"], self.packet["editorial"]["credit"] +
                         " This archive is officially approved and endorsed by NASA.")

    def test_reject_pretended_no_rights_hold(self):
        self.reject_edit(["public_release_decision"], "GO")

    def test_reject_pretended_approved_prior_photo(self):
        self.reject_edit(["three_distinct_photos_rights_status"], "GO")

    def test_reject_unexpected_mutable_field(self):
        self.reject_edit(["lore_search_alias"], "USS Enterprise")

    def test_reject_automatic_preconnect(self):
        self.reject_edit(["browser_contract", "at_rest"], "AUTOMATIC_NASA_CDN_PRECONNECT")

    def test_reject_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            unique_object([("image", 1), ("image", 2)])


if __name__ == "__main__":
    unittest.main()
