"""Guard Prodigy distributor publisher metadata against accidental admission."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/pro-publisher-s01-b001-20261102"
SPEC = importlib.util.spec_from_file_location(
    "publisher_validator_pro", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ProdigyPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_metadata_only_and_no_admission_effects(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "pro", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        for key in ("accepted_work_effect", "accepted_source_binding_effect",
                    "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[key], "NONE")
        observation = self.bundle["observation"]
        self.assertEqual(observation["independence_group"], "INDEPENDENCE_UNRESOLVED")
        self.assertEqual(observation["publisher"],
                         "Apple TV US (first-party distributor listing)")
        self.assertIsNone(observation["response_sha256"])
        self.assertFalse(observation["audiovisual_content_inspected"])

    def test_first_five_display_slots_preserve_unresolved_premiere(self):
        self.assertEqual([
            (row["season"], row["episode_number"], row["title"])
            for row in self.bundle["episode_slots"]
        ], [
            (1, 1, "Lost & Found, Pt. 1"),
            (1, 3, "Starstruck"),
            (1, 4, "Dreamcatcher"),
            (1, 5, "Terror Firma"),
            (1, 6, "Kobayashi"),
        ])
        self.assertNotIn(2, [row["episode_number"] for row in self.bundle["episode_slots"]])
        self.assertTrue(all(row["canonical_work_id"] is None
                            and row["source_binding_id"] is None
                            and row["status"] == "CANDIDATE"
                            for row in self.bundle["episode_slots"]))

    def test_csv_digest_and_normalized_bundle_agree(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.receipt["csv_sha256"])
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual([
            (int(row["season"]), int(row["episode_number"]), row["title"])
            for row in rows
        ], [
            (row["season"], row["episode_number"], row["title"])
            for row in self.bundle["episode_slots"]
        ])

    def test_reject_canonical_work_or_coverage_promotion(self):
        changed = json.loads(json.dumps(self.bundle))
        changed["episode_slots"][0]["canonical_work_id"] = "pro-se-1-1"
        with self.assertRaises(validator.Rejected):
            validator.validate(changed, self.catalog)
        changed = json.loads(json.dumps(self.bundle))
        changed["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaises(validator.Rejected):
            validator.validate(changed, self.catalog)


if __name__ == "__main__":
    unittest.main()
