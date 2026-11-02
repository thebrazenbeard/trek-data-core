"""TAS Season 1 publisher display-slot metadata remains unadmitted and reproducible."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/tas-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_tas", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TasPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_publisher_candidates_do_not_advance_accepted_state(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "tas", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        for field in ("accepted_work_effect", "accepted_source_binding_effect",
                      "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[field], "NONE")
        self.assertFalse(self.bundle["observation"]["audiovisual_content_inspected"])
        self.assertIsNone(self.bundle["observation"]["response_sha256"])
        self.assertEqual(self.bundle["observation"]["independence_group"], "publisher:paramount")

    def test_five_exact_publisher_display_slots(self):
        observed = [(slot["season"], slot["episode_number"], slot["title"])
                    for slot in self.bundle["episode_slots"]]
        self.assertEqual(observed, [
            (1, 1, "Beyond the Farthest Star"),
            (1, 2, "Yesteryear"),
            (1, 3, "One of Our Planets is Missing"),
            (1, 4, "The Lorelei Signal"),
            (1, 5, "More Tribbles, More Troubles"),
        ])
        self.assertTrue(all(slot["status"] == "CANDIDATE"
                            and slot["canonical_work_id"] is None
                            and slot["source_binding_id"] is None
                            for slot in self.bundle["episode_slots"]))

    def test_receipt_csv_sha256_and_rows(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(self.receipt["csv_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            csv_rows = list(csv.DictReader(stream))
        self.assertEqual([(int(row["season"]), int(row["episode_number"]), row["title"])
                          for row in csv_rows], [
            (slot["season"], slot["episode_number"], slot["title"])
            for slot in self.bundle["episode_slots"]
        ])


if __name__ == "__main__":
    unittest.main()
