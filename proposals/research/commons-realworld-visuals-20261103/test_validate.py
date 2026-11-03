"""Adversarial fixture tests; model review does not become a rights grant."""
import unittest

import validate as gate


class CommonsRealworldSourceHoldTests(unittest.TestCase):
    def setUp(self):
        self.packet = gate.load_packet()

    def check_bad(self, token: str):
        with self.assertRaisesRegex(gate.Refused, token):
            gate.validate(self.packet)

    def test_only_three_proposal_subjects_none_admitted(self):
        result = gate.validate(self.packet)
        self.assertEqual(result, {"status": "PROPOSAL_ONLY", "candidates": 3,
                                  "release": 0, "coverage": 0})
        self.assertEqual([r["subject_kind"] for r in self.packet["candidates"]], [
            "REAL_WORLD_PERFORMER_AT_EVENT", "EXHIBITED_PRODUCTION_OBJECT",
            "EXHIBITED_PRODUCTION_OBJECT"])

    def test_duplicate_json_key_is_rejected(self):
        with self.assertRaisesRegex(gate.Refused, "duplicate JSON"):
            gate.unique([("id", 1), ("id", 2)])

    def test_public_release_escalation_fails(self):
        for key, value in (("public_artwork_release_effect", "PUBLISHED"),
                           ("image_files_committed", 1), ("image_urls_in_public_sidecar", 1),
                           ("coverage_effect", "STRUCTURALLY_INDEXED")):
            with self.subTest(key=key):
                self.packet = gate.load_packet()
                self.packet[key] = value
                self.check_bad("public release or coverage")

    def test_public_asset_and_remote_hotlink_never_accepted(self):
        for key, value in (("public_image_url", "https://upload.wikimedia.org/wikipedia/commons/a.jpg"),
                           ("public_asset_path", "./licensed-artwork/ship.jpg"),
                           ("release_status", "PUBLIC_DISPLAY_PERMISSION_VERIFIED")):
            with self.subTest(key=key):
                self.packet = gate.load_packet()
                self.packet["candidates"][1][key] = value
                self.check_bad("cannot self-authorize")

    def test_photo_license_cannot_be_spoofed_to_public_domain(self):
        self.packet["candidates"][0]["photo_license"] = "CC0"
        self.check_bad("photographer credit/license")

    def test_attribution_and_source_creator_mismatch_fail(self):
        self.packet["candidates"][0]["attribution_text"] = "No credit required"
        self.check_bad("photographer credit/license")
        self.packet = gate.load_packet()
        self.packet["candidates"][0]["photographer_source"] = "https://star-trek.com/press/photo"
        self.check_bad("photographer credit/license")

    def test_commons_revision_must_identify_exact_same_file(self):
        self.packet["candidates"][2]["commons_pinned_revision"] = (
            "https://commons.wikimedia.org/w/index.php?title=File:Other.jpg&oldid=964617610")
        self.check_bad("page/revision identity")
        self.packet = gate.load_packet()
        self.packet["candidates"][2]["commons_file_page"] = "https://evil.invalid/wiki/File:Other.jpg"
        self.check_bad("page/revision identity")

    def test_unreviewed_production_claim_cannot_become_canon(self):
        self.packet["candidates"][1]["work_or_episode_row_id"] = "legacy:s3:tos:002"
        self.check_bad("silently bind")
        self.packet = gate.load_packet()
        self.packet["candidates"][1]["source_claim_scope"] = "VERIFIED_FILMING_OBJECT"
        self.check_bad("silently bind")
        self.packet = gate.load_packet()
        self.packet["candidates"][0]["character_identity_inferred"] = True
        self.check_bad("silently bind")

    def test_record_hash_must_have_correct_shape_but_not_claim_license(self):
        self.packet["candidates"][0]["original_jpeg_sha256"] = "abc"
        self.check_bad("hash receipt")
        self.packet = gate.load_packet()
        self.packet["candidates"][0]["original_jpeg_sha1"] = "a" * 64
        self.check_bad("hash receipt")

    def test_duplicate_image_and_candidate_identity_fail(self):
        self.packet["candidates"][1]["candidate_id"] = self.packet["candidates"][0]["candidate_id"]
        self.check_bad("duplicate or unsafe candidate")
        self.packet = gate.load_packet()
        self.packet["candidates"][2]["original_jpeg_sha256"] = (
            self.packet["candidates"][1]["original_jpeg_sha256"])
        self.check_bad("duplicate source/image hash")

    def test_unsupported_subject_type_or_missing_hold_fails(self):
        self.packet["candidates"][0]["subject_kind"] = "CANON_CHARACTER_STILL"
        self.check_bad("unsupported subject")
        self.packet = gate.load_packet()
        self.packet["candidates"][0]["subject_rights_status"] = "CLEARED"
        self.check_bad("cannot self-authorize")

    def test_misleading_numeric_and_extra_fields_fail(self):
        self.packet["candidates"][0]["original_jpeg_bytes"] = True
        self.check_bad("unreviewed JPEG")
        self.packet = gate.load_packet()
        self.packet["candidates"][0]["new_permission"] = "YES"
        self.check_bad("candidate shape")

    def test_coordinated_plausible_source_identity_spoof_is_not_admitted(self):
        # Independent hostile-review PoC: all fields retain plausible types,
        # hosts and shapes, but rewrite the convention attendee into a scene.
        record = self.packet["candidates"][0]
        record["subject_label"] = "Captain James T Kirk"
        record["source_described_context"] = "Official film scene portrait from the 1960s"
        record["commons_pinned_revision"] = record["commons_pinned_revision"].replace(
            "oldid=1107732292", "oldid=1107732293")
        record["commons_page_html_sha256"] = "f" * 64
        record["imageinfo_api_response_sha256"] = "d" * 64
        record["original_jpeg_sha1"] = "e" * 40
        record["original_jpeg_sha256"] = "a" * 64
        record["photographer"] = "Joe Ross"
        record["photographer_source"] = "https://www.flickr.com/photos/joeross/not_real/"
        record["attribution_text"] = "Captain James T Kirk film portrait — photo by Joe Ross, CC BY-SA 2.0"
        self.check_bad("candidate identity/source/rights tuple")

    def test_individual_plausible_snapshot_or_subject_rewrite_must_fail_pin(self):
        for key, value in (("subject_label", "Captain Kirk actor"),
                           ("commons_page_html_sha256", "f" * 64),
                           ("original_jpeg_sha1", "e" * 40),
                           ("photographer", "Joe Ross"),
                           ("commons_flickr_license_review",
                            "FLICKREVIEWR_2_CONFIRMED_CC_BY_SA_2_0_ON_2023_06_15")):
            with self.subTest(key=key):
                self.packet = gate.load_packet()
                self.packet["candidates"][0][key] = value
                if key == "photographer":
                    self.packet["candidates"][0]["attribution_text"] = (
                        self.packet["candidates"][0]["attribution_text"].replace(
                            "Gage Skidmore", "Joe Ross"))
                self.check_bad("candidate identity/source/rights tuple")


if __name__ == "__main__":
    unittest.main()
