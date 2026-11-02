"""Adversarial checks for the separate metadata-review proposal contract."""
from __future__ import annotations

from contextlib import redirect_stdout, redirect_stderr
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_verified_episode_roster as module


class VerifiedMetadataReviewTests(unittest.TestCase):
    SNAPSHOT = b"<html><body>Example publisher episode list</body></html>"

    def setUp(self):
        self.catalog = json.loads((ROOT / "registry" / "mission_catalog.json").read_text())
        self.candidate = {
            "record_type": "publisher_episode_roster_proposal",
            "schema_version": "1.0.0",
            "batch_id": "test-publisher-s01",
            "mission_id": "tos",
            "proposal_status": "CANDIDATE_METADATA_ONLY",
            "accepted_work_effect": "NONE",
            "accepted_source_binding_effect": "NONE",
            "coverage_effect": "NONE",
            "denominator_effect": "NONE",
            "roster_completeness": "UNRESOLVED",
            "listed_slot_count": 2,
            "observation": {
                "publisher": "Example Publisher",
                "independence_group": "publisher:example",
                "observed_on": "2026-11-01",
                "primary_locator": "https://example.org/episodes",
                "crosscheck_locator": "https://example.org/catalog",
                "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
                "response_sha256": None,
                "publisher_revision": None,
                "audiovisual_content_inspected": False,
            },
            "series_qid_redirect": None,
            "episode_slots": [
                {"season": 1, "episode_number": 1, "title": "Example One", "status": "CANDIDATE",
                 "canonical_work_id": None, "source_binding_id": None},
                {"season": 1, "episode_number": 2, "title": "Example Two", "status": "CANDIDATE",
                 "canonical_work_id": None, "source_binding_id": None},
            ],
        }
        self.raw = json.dumps(self.candidate, sort_keys=True).encode("utf-8")
        self.review = {
            "record_type": "publisher_episode_metadata_review",
            "schema_version": "1.0.0",
            "candidate_batch_id": "test-publisher-s01",
            "candidate_sha256": module.digest(self.raw),
            "mission_id": "tos",
            "publisher_snapshot": {
                "locator": "https://example.org/episodes",
                "independence_group": "publisher:example",
                "retrieved_on": "2026-11-02",
                "content_sha256": module.digest(self.SNAPSHOT),
                "representation": "PUBLISHER_PAGE_BYTES",
                "publication": "BYTES_EXCLUDED",
            },
            "review": {
                "collector_id": "collector-one",
                "reviewer_id": "reviewer-two",
                "reviewed_on": "2026-11-02",
                "attestation": "IDENTITY_FIELDS_MATCH_SNAPSHOT",
                "scope": "PUBLISHER_TITLE_SEASON_EPISODE_ONLY",
                "checked_episode_slots": [
                    {"season": 1, "episode_number": 1, "title": "Example One"},
                    {"season": 1, "episode_number": 2, "title": "Example Two"},
                ],
            },
            "metadata_status": "REVIEW_PROPOSAL_ONLY",
            "canonical_work_effect": "NONE",
            "source_binding_effect": "NONE",
            "continuity_effect": "NONE",
            "coverage_effect": "NONE",
            "denominator_effect": "NONE",
            "publication_effect": "NONE",
        }

    def check(self, snapshot=None):
        return module.validate_review(self.candidate, self.raw, self.review, self.catalog, snapshot)

    def test_receipt_only_does_not_claim_snapshot_or_admission(self):
        status = self.check()
        self.assertEqual(status["review_receipt_status"], "DECLARED_REVIEW_RECEIPT_ONLY_NOT_ADMITTED")
        self.assertEqual(status["accepted_effect"], "NONE")
        self.assertEqual(status["checked_episode_slots"], 2)

    def test_exact_private_snapshot_digest_checked_without_copying_bytes(self):
        status = self.check(self.SNAPSHOT)
        self.assertEqual(status["review_receipt_status"], "SNAPSHOT_BYTES_MATCH_RECEIPT_NOT_ADMITTED")
        self.assertNotIn(self.SNAPSHOT.decode(), json.dumps(status))

    def test_changed_candidate_bytes_do_not_match_receipt(self):
        self.raw += b" "
        with self.assertRaisesRegex(module.Rejected, "candidate byte digest"):
            self.check()

    def test_snapshot_mismatch_rejected(self):
        with self.assertRaisesRegex(module.Rejected, "publisher snapshot byte digest"):
            self.check(b"not the recorded page")

    def test_self_review_rejected(self):
        self.review["review"]["reviewer_id"] = "collector-one"
        with self.assertRaisesRegex(module.Rejected, "distinct bounded identity"):
            self.check()

    def test_reviewer_checks_only_exact_candidate_slots(self):
        self.review["review"]["checked_episode_slots"][0]["title"] = "Made Up"
        with self.assertRaisesRegex(module.Rejected, "exactly match"):
            self.check()

    def test_review_date_before_snapshot_rejected(self):
        self.review["review"]["reviewed_on"] = "2026-10-31"
        with self.assertRaisesRegex(module.Rejected, "cannot precede"):
            self.check()

    def test_future_snapshot_rejected(self):
        self.review["publisher_snapshot"]["retrieved_on"] = "2099-01-01"
        self.review["review"]["reviewed_on"] = "2099-01-01"
        with self.assertRaisesRegex(module.Rejected, "future"):
            self.check()

    def test_attempted_coverage_promotion_rejected(self):
        self.review["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaisesRegex(module.Rejected, "cannot cause coverage_effect"):
            self.check()

    def test_same_publisher_cannot_change_independence_group(self):
        self.review["publisher_snapshot"]["independence_group"] = "publisher:second"
        with self.assertRaisesRegex(module.Rejected, "identity/representation"):
            self.check()

    def test_boolean_episode_number_rejected(self):
        self.review["review"]["checked_episode_slots"][0]["episode_number"] = True
        with self.assertRaisesRegex(module.Rejected, "uniquely and exactly match"):
            self.check()

    def test_private_snapshot_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "publisher.html"
            real.write_bytes(self.SNAPSHOT)
            link = root / "page-link"
            link.symlink_to(real)
            with self.assertRaisesRegex(module.Rejected, "non-symlink"):
                module.read_snapshot(link)

    def test_cli_emits_no_accepted_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proposal = root / "proposal.json"
            proposal.write_bytes(self.raw)
            review = root / "review.json"
            review.write_text(json.dumps(self.review))
            snapshot = root / "publisher.html"
            snapshot.write_bytes(self.SNAPSHOT)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = module.main(["--candidate", str(proposal), "--review", str(review),
                                    "--snapshot", str(snapshot)])
            self.assertEqual(code, 0)
            result = stdout.getvalue()
            self.assertIn("SNAPSHOT_BYTES_MATCH_RECEIPT_NOT_ADMITTED", result)
            self.assertIn('"accepted_effect": "NONE"', result)

    def test_cli_rejects_duplicate_candidate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proposal = root / "proposal.json"
            proposal.write_text('{"mission_id":"tos","mission_id":"tng"}')
            review = root / "review.json"
            review.write_text(json.dumps(self.review))
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = module.main(["--candidate", str(proposal), "--review", str(review)])
            self.assertEqual(code, 1)
            self.assertIn("duplicate JSON key", stderr.getvalue())

    def test_schema_matches_review_surface(self):
        schema = json.loads((ROOT / "schema" / "verified-episode-roster.schema.json").read_text())
        self.assertEqual(set(schema["properties"]), set(self.review))
        self.assertEqual(set(schema["required"]), set(self.review))
        self.assertEqual(schema["properties"]["publication_effect"]["const"], "NONE")


if __name__ == "__main__":
    unittest.main()
