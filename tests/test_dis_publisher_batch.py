"""Checks for an unadmitted, source-relative Discovery Season 1 publisher sample."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/dis-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_dis", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DiscoveryPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_is_bounded_candidate_only_no_accepted_state_effect(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "dis", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        for field in ("accepted_work_effect", "accepted_source_binding_effect",
                      "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[field], "NONE")
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        observation = self.bundle["observation"]
        self.assertEqual(observation["independence_group"], "publisher:paramount")
        self.assertFalse(observation["audiovisual_content_inspected"])
        self.assertIsNone(observation["response_sha256"])
        self.assertIsNone(observation["publisher_revision"])

    def test_first_five_source_local_slots_exact(self):
        self.assertEqual([(row["season"], row["episode_number"], row["title"])
                          for row in self.bundle["episode_slots"]], [
            (1, 1, "The Vulcan Hello"),
            (1, 2, "Battle at the Binary Stars"),
            (1, 3, "Context Is For Kings"),
            (1, 4, "The Butcher's Knife Cares Not for the Lamb's Cry"),
            (1, 5, "Choose Your Pain"),
        ])
        self.assertTrue(all(row["status"] == "CANDIDATE"
                            and row["canonical_work_id"] is None
                            and row["source_binding_id"] is None
                            for row in self.bundle["episode_slots"]))

    def test_csv_receipt_hash_and_bundle_identical(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(self.receipt["csv_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        self.assertEqual(self.receipt["mission_id"], self.bundle["mission_id"])
        self.assertEqual(self.receipt["primary_locator"], self.bundle["observation"]["primary_locator"])
        self.assertEqual(self.receipt["crosscheck_locator"], self.bundle["observation"]["crosscheck_locator"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            csv_rows = list(csv.DictReader(stream))
        self.assertEqual([(int(row["season"]), int(row["episode_number"]), row["title"])
                          for row in csv_rows],
                         [(row["season"], row["episode_number"], row["title"])
                          for row in self.bundle["episode_slots"]])

    def test_publisher_lineage_and_title_casing_are_explicitly_unresolved(self):
        doc = (PROPOSAL / "RESEARCH_RECORD.md").read_text(encoding="utf-8")
        self.assertIn("NOT independent external corroboration", doc)
        self.assertIn("Context Is for Kings", doc)
        self.assertIn("Context Is For Kings", doc)
        self.assertIn("**UNRESOLVED**", doc)


if __name__ == "__main__":
    unittest.main()
