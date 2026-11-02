"""Offline regression for LD publisher title/slot discovery, with no admission."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/lds-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_lds", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class LowerDecksPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_candidate_only_and_no_admission_effects(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "ld", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        self.assertEqual(self.bundle["roster_completeness"], "UNRESOLVED")
        for name in ("accepted_work_effect", "accepted_source_binding_effect",
                     "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[name], "NONE")
        self.assertEqual(self.bundle["observation"]["independence_group"], "publisher:paramount")
        self.assertIsNone(self.bundle["observation"]["response_sha256"])
        self.assertFalse(self.bundle["observation"]["audiovisual_content_inspected"])

    def test_first_five_display_positions_not_invented(self):
        rows = self.bundle["episode_slots"]
        self.assertEqual([(row["season"], row["episode_number"], row["title"])
                          for row in rows], [
            (1, 1, "Second Contact"),
            (1, 2, "Envoys"),
            (1, 3, "Temporal Edict"),
            (1, 4, "Moist Vessel"),
            (1, 5, "Cupid's Errant Arrow"),
        ])
        self.assertTrue(all(row["status"] == "CANDIDATE"
                            and row["canonical_work_id"] is None
                            and row["source_binding_id"] is None for row in rows))

    def test_receipt_csv_exact_bytes_and_bundle_agree(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.receipt["csv_sha256"])
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        self.assertEqual([(int(row["season"]), int(row["episode_number"]), row["title"])
                          for row in source_rows], [
            (row["season"], row["episode_number"], row["title"])
            for row in self.bundle["episode_slots"]
        ])

    def test_reject_promoted_coverage(self):
        altered = dict(self.bundle)
        altered["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaises(validator.Rejected):
            validator.validate(altered, self.catalog)


if __name__ == "__main__":
    unittest.main()
