"""Regression of Picard publisher source-local labels, without admission."""

from __future__ import annotations

import csv
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/pic-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_pic", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PicPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_candidate_status_and_no_accepted_effects(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "pic", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        self.assertEqual(self.bundle["observation"]["independence_group"], "publisher:paramount")
        self.assertFalse(self.bundle["observation"]["audiovisual_content_inspected"])
        self.assertIsNone(self.bundle["observation"]["response_sha256"])
        for key in ("accepted_work_effect", "accepted_source_binding_effect",
                    "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[key], "NONE")

    def test_exact_season_one_slots_and_regional_casing_retained(self):
        self.assertEqual([(r["season"], r["episode_number"], r["title"])
                          for r in self.bundle["episode_slots"]], [
            (1, 1, "Remembrance"),
            (1, 2, "Maps and Legends"),
            (1, 3, "The End Is The Beginning"),
            (1, 4, "Absolute Candor"),
            (1, 5, "Stardust City Rag"),
        ])
        self.assertTrue(all(r["status"] == "CANDIDATE"
                            and r["canonical_work_id"] is None
                            and r["source_binding_id"] is None
                            for r in self.bundle["episode_slots"]))

    def test_exact_local_csv_digest_and_normalized_row_equality(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.receipt["csv_sha256"])
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual([(int(r["season"]), int(r["episode_number"]), r["title"])
                          for r in rows], [
            (r["season"], r["episode_number"], r["title"])
            for r in self.bundle["episode_slots"]
        ])

    def test_failed_canonicalization_or_fake_content_claim(self):
        fake = copy.deepcopy(self.bundle)
        fake["episode_slots"][0]["canonical_work_id"] = "pic-001"
        with self.assertRaises(validator.Rejected):
            validator.validate(fake, self.catalog)
        fake = copy.deepcopy(self.bundle)
        fake["observation"]["audiovisual_content_inspected"] = True
        with self.assertRaises(validator.Rejected):
            validator.validate(fake, self.catalog)


if __name__ == "__main__":
    unittest.main()
