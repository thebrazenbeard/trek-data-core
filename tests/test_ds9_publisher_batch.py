"""Offline regressions for the first five DS9 publisher-listed display positions."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/ds9-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_ds9", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class Ds9PublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_candidate_only_and_no_accepted_effects(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "ds9", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        for key in ("accepted_work_effect", "accepted_source_binding_effect",
                    "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[key], "NONE")
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        self.assertEqual(self.bundle["observation"]["independence_group"], "publisher:paramount")
        self.assertIsNone(self.bundle["observation"]["response_sha256"])
        self.assertFalse(self.bundle["observation"]["audiovisual_content_inspected"])

    def test_display_positions_preserve_pilot_multipart_gap(self):
        rows = self.bundle["episode_slots"]
        self.assertEqual([(r["season"], r["episode_number"], r["title"]) for r in rows], [
            (1, 1, "The Emissary, Parts I and II"),
            (1, 3, "Past Prologue"),
            (1, 4, "A Man Alone"),
            (1, 5, "Babel"),
            (1, 6, "Captive Pursuit"),
        ])
        self.assertNotIn(2, [r["episode_number"] for r in rows])
        self.assertTrue(all(r["status"] == "CANDIDATE"
                            and r["canonical_work_id"] is None
                            and r["source_binding_id"] is None for r in rows))

    def test_receipt_digest_and_csv_reproduce_bundle_rows(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(self.receipt["csv_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        self.assertEqual([(int(r["season"]), int(r["episode_number"]), r["title"])
                          for r in source_rows], [
            (r["season"], r["episode_number"], r["title"])
            for r in self.bundle["episode_slots"]
        ])


if __name__ == "__main__":
    unittest.main()
