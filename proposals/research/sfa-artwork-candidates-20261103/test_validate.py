"""Mutation regression tests for SFA publisher-photo candidate restrictions."""

import copy
import json
import unittest
from pathlib import Path

from validate import EXPECTED_UPSTREAM_SHA256, UPSTREAM_PATH, validate


HERE = Path(__file__).resolve().parent


class ArtworkCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream_bytes = UPSTREAM_PATH.read_bytes()
        cls.upstream = json.loads(cls.upstream_bytes)
        cls.data = json.loads((HERE / "records.json").read_text(encoding="utf-8"))

    def test_valid_bounded_candidate(self):
        self.assertEqual(validate(self.data, self.upstream, self.upstream_bytes), 3)

    def reject(self, edit, pattern):
        mutated = copy.deepcopy(self.data)
        edit(mutated)
        with self.assertRaisesRegex(ValueError, pattern):
            validate(mutated, self.upstream, self.upstream_bytes)

    def test_image_url_is_not_accepted(self):
        self.reject(lambda d: d["candidate_photo_locators"][0].update(image_url="https://example.org/still.jpg"), "forbidden image")

    def test_arbitrary_extra_image_field_is_not_accepted(self):
        self.reject(lambda d: d["candidate_photo_locators"][0].update(display_uri="https://example.org/still.jpg"), "unexpected candidate field")

    def test_unlicensed_display_gate_fails(self):
        self.reject(lambda d: d["candidate_photo_locators"][0].update(rights_status="PUBLIC_DISPLAY_PERMISSION_VERIFIED"), "unreviewed thumbnail permission")

    def test_false_claim_of_asset_read_fails(self):
        self.reject(lambda d: d.update(photo_contents_inspected=True), "unverified action")

    def test_publisher_line_must_match(self):
        self.reject(lambda d: d["candidate_photo_locators"][0].update(source_relative_html_line=9999), "line locator altered")

    def test_caption_must_match(self):
        self.reject(lambda d: d["candidate_photo_locators"][1].update(caption_subjects_as_publisher_metadata=["fictional character"]), "publisher caption altered")

    def test_source_lineage_cannot_claim_independence(self):
        self.reject(lambda d: d["upstream_proposal"].update(publisher_independence_group="independent:fake"), "invented independent publisher")

    def test_media_bucket_is_not_a_work(self):
        self.reject(lambda d: d["candidate_photo_locators"][0].update(canonical_episode_id="season-2-episode-200"), "forbidden image/Work promotion")

    def test_no_paid_licensing_commitment(self):
        self.reject(lambda d: d.update(budget_committed_usd=1), "fee commitment")

    def test_license_receipt_cannot_be_invented(self):
        self.reject(lambda d: d["rights_review"].update(license_receipt_sha256="0" * 64), "unverified image rights")

    def test_missing_photo_fails(self):
        self.reject(lambda d: d["candidate_photo_locators"].pop(), "exactly three")

    def test_wrong_upstream_proposal_sha_fails(self):
        self.reject(lambda d: d["upstream_proposal"].update(sha256="0" * 64), "wrong upstream digest")

    def test_upstream_bytes_are_hash_locked(self):
        self.assertEqual(EXPECTED_UPSTREAM_SHA256, self.data["upstream_proposal"]["sha256"])
        with self.assertRaisesRegex(ValueError, "upstream publisher proposal changed"):
            validate(self.data, self.upstream, self.upstream_bytes + b" ")


if __name__ == "__main__":
    unittest.main()
