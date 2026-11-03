"""The metadata-discovery projection must never admit Mission Briefings."""
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
import build_metadata_discovery_index as module

TOS = ROOT / "proposals" / "discovery" / "tos-publisher-s01-b001-20261102"


class MetadataDiscoveryProjectionTests(unittest.TestCase):
    def setUp(self):
        self.paramount = TOS / "paramountplus.json"
        self.pluto = TOS / "plutotv.json"

    def test_cross_source_tos_slots_and_titles_remain_conflicted_not_resolved(self):
        result = module.build_projection([self.paramount, self.pluto])
        self.assertEqual(result["record_type"], "unadmitted_episode_metadata_discovery_projection")
        self.assertEqual(len(result["records"]), 10)
        firsts = [row for row in result["records"]
                  if row["mission_id"] == "tos" and row["season"] == 1 and row["episode_number"] == 1]
        self.assertEqual({row["title"] for row in firsts}, {"The Cage", "The Man Trap"})
        self.assertEqual({row["independence_group"] for row in firsts}, {"publisher:paramount"})
        self.assertEqual(len(result["source_local_slot_disagreements"]), 5)
        man_trap = [row for row in result["title_position_disagreements"]
                    if row["title"] == "The Man Trap"]
        self.assertEqual(len(man_trap), 1)
        self.assertEqual({entry["episode_number"] for entry in man_trap[0]["observations"]}, {1, 2})
        self.assertTrue(all(row["candidate_status"] == "CANDIDATE_METADATA_ONLY"
                            and row["receipt_status"] == "NO_REVIEW_RECEIPT"
                            for row in result["records"]))
        self.assertNotIn("canonical_work_id", json.dumps(result))
        self.assertNotIn("source_binding_id", json.dumps(result))
        self.assertEqual(result["effects"], {
            "canonical_work": "NONE", "source_binding": "NONE", "continuity": "NONE",
            "coverage": "NONE", "denominator": "NONE", "publication": "NONE",
        })

    def test_reversed_input_order_is_byte_identical(self):
        forward = module.build_projection([self.paramount, self.pluto])
        reverse = module.build_projection([self.pluto, self.paramount])
        self.assertEqual(module.canonical_bytes(forward), module.canonical_bytes(reverse))
        self.assertEqual(forward["projection_sha256"], reverse["projection_sha256"])

    def make_receipt(self, candidate, candidate_raw, checked=None):
        snapshot = b"<html>synthetic fixture, not a publisher page</html>"
        return {
            "record_type": "publisher_episode_metadata_review", "schema_version": "1.0.0",
            "candidate_batch_id": candidate["batch_id"],
            "candidate_sha256": module.digest(candidate_raw), "mission_id": candidate["mission_id"],
            "publisher_snapshot": {
                "locator": candidate["observation"]["primary_locator"],
                "independence_group": candidate["observation"]["independence_group"],
                "retrieved_on": "2026-11-02", "content_sha256": module.digest(snapshot),
                "representation": "PUBLISHER_PAGE_BYTES", "publication": "BYTES_EXCLUDED",
            },
            "review": {
                "collector_id": "test-collector", "reviewer_id": "test-reviewer",
                "reviewed_on": "2026-11-02", "attestation": "IDENTITY_FIELDS_MATCH_SNAPSHOT",
                "scope": "PUBLISHER_TITLE_SEASON_EPISODE_ONLY",
                "checked_episode_slots": checked or [
                    {"season": row["season"], "episode_number": row["episode_number"], "title": row["title"]}
                    for row in candidate["episode_slots"][:1]
                ],
            },
            "metadata_status": "REVIEW_PROPOSAL_ONLY", "canonical_work_effect": "NONE",
            "source_binding_effect": "NONE", "continuity_effect": "NONE",
            "coverage_effect": "NONE", "denominator_effect": "NONE", "publication_effect": "NONE",
        }, snapshot

    def test_synthetic_receipt_upgrades_only_checked_slot_declaration_not_admission(self):
        candidate_raw = self.paramount.read_bytes()
        candidate = json.loads(candidate_raw)
        receipt, snapshot = self.make_receipt(candidate, candidate_raw)
        with tempfile.TemporaryDirectory() as tmp:
            review = Path(tmp) / "review.json"
            snapshot_path = Path(tmp) / "publisher-private.html"
            review.write_text(json.dumps(receipt), encoding="utf-8")
            snapshot_path.write_bytes(snapshot)
            declared = module.build_projection([self.paramount], [review])
            verified_bytes = module.build_projection([self.paramount], [review], {review: snapshot_path})
        for result, expected_status in ((declared, "DECLARED_REVIEW_RECEIPT_ONLY_NOT_ADMITTED"),
                                        (verified_bytes, "SNAPSHOT_BYTES_MATCH_RECEIPT_NOT_ADMITTED")):
            checked = [row for row in result["records"] if row["episode_number"] == 1]
            unchecked = [row for row in result["records"] if row["episode_number"] != 1]
            self.assertEqual(checked[0]["receipt_status"], expected_status)
            self.assertTrue(all(row["receipt_status"] == "NO_REVIEW_RECEIPT" for row in unchecked))
            self.assertEqual(result["effects"]["canonical_work"], "NONE")
            self.assertEqual(result["effects"]["coverage"], "NONE")
            self.assertNotIn(snapshot.decode(), json.dumps(result))
            self.assertNotIn("source_binding_id", json.dumps(result))

    def test_duplicate_or_conflicting_source_local_slot_rejected(self):
        with self.assertRaisesRegex(module.Rejected, "duplicate source-local slot"):
            module.build_projection([self.paramount, self.paramount])
        altered = copy.deepcopy(json.loads(self.paramount.read_text()))
        altered["batch_id"] = "test-conflict-batch"
        altered["episode_slots"][0]["title"] = "A Different Candidate Title"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "conflict.json"
            path.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(module.Rejected, "duplicate source-local slot"):
                module.build_projection([self.paramount, path])

    def test_receipt_byte_mismatch_and_unknown_candidate_rejected(self):
        candidate_raw = self.paramount.read_bytes()
        candidate = json.loads(candidate_raw)
        receipt, snapshot = self.make_receipt(candidate, candidate_raw)
        with tempfile.TemporaryDirectory() as tmp:
            review = Path(tmp) / "review.json"
            receipt["candidate_sha256"] = "sha256:" + hashlib.sha256(b"wrong").hexdigest()
            review.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(module.Rejected, "no input candidate"):
                module.build_projection([self.paramount], [review])
            receipt["candidate_sha256"] = module.digest(candidate_raw)
            review.write_text(json.dumps(receipt), encoding="utf-8")
            bad_snapshot = Path(tmp) / "wrong-snapshot.html"
            bad_snapshot.write_bytes(b"not the snapshot")
            with self.assertRaisesRegex(module.Rejected, "snapshot byte digest mismatch"):
                module.build_projection([self.paramount], [review], {review: bad_snapshot})

    def test_cli_stdout_only_and_no_canonical_index_mutation(self):
        existing_index = (ROOT / "explorer" / "index.json").read_bytes()
        out = io.StringIO()
        with redirect_stdout(out):
            result = module.main(["--candidate", str(self.pluto), "--candidate", str(self.paramount)])
        self.assertEqual(result, 0)
        obj = json.loads(out.getvalue())
        self.assertEqual(obj["effects"]["publication"], "NONE")
        self.assertEqual((ROOT / "explorer" / "index.json").read_bytes(), existing_index)


if __name__ == "__main__":
    unittest.main()
