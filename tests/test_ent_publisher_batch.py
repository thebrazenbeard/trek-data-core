"""Offline checks of a source-local Enterprise publisher roster observation."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/ent-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_validator_ent", ROOT / "tools/validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class EnterprisePublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))
        cls.bundle = json.loads((PROPOSAL / "bundle.json").read_text(encoding="utf-8"))
        cls.receipt = json.loads((PROPOSAL / "observation_receipt.json").read_text(encoding="utf-8"))

    def test_candidate_only_with_no_admission_effects(self):
        self.assertEqual(validator.validate(self.bundle, self.catalog), {
            "mission_id": "ent", "listed_slots": 5,
            "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
        })
        self.assertEqual(self.bundle["proposal_status"], "CANDIDATE_METADATA_ONLY")
        for key in ("accepted_work_effect", "accepted_source_binding_effect",
                    "coverage_effect", "denominator_effect"):
            self.assertEqual(self.bundle[key], "NONE")
        observation = self.bundle["observation"]
        self.assertEqual(observation["independence_group"], "publisher:paramount")
        self.assertIsNone(observation["response_sha256"])
        self.assertIsNone(observation["publisher_revision"])
        self.assertFalse(observation["audiovisual_content_inspected"])
        self.assertIsNone(self.bundle["series_qid_redirect"])

    def test_combined_pilot_and_source_local_numbering_preserved(self):
        rows = self.bundle["episode_slots"]
        self.assertEqual([(r["season"], r["episode_number"], r["title"]) for r in rows], [
            (1, 1, "Broken Bow - Part 1 and 2"),
            (1, 3, "Fight or Flight"),
            (1, 4, "Strange New World"),
            (1, 5, "Unexpected"),
            (1, 6, "Terra Nova"),
        ])
        self.assertNotIn(2, [r["episode_number"] for r in rows])
        self.assertTrue(all(r["status"] == "CANDIDATE" and r["canonical_work_id"] is None
                            and r["source_binding_id"] is None for r in rows))

    def test_exact_csv_digest_and_receipt_provenance(self):
        raw = (PROPOSAL / "roster.csv").read_bytes()
        self.assertEqual(self.receipt["csv_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.receipt["batch_id"], self.bundle["batch_id"])
        self.assertEqual(self.receipt["primary_locator"],
                         "https://www.paramountplus.com/shows/enterprise/episodes/1/")
        self.assertEqual(self.receipt["observed_on"], "2026-11-02")
        with (PROPOSAL / "roster.csv").open(encoding="utf-8", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        self.assertEqual([(int(r["season"]), int(r["episode_number"]), r["title"])
                          for r in source_rows], [(r["season"], r["episode_number"], r["title"])
                                                 for r in self.bundle["episode_slots"]])

    def test_wikidata_held_arc_ids_remain_unreconciled(self):
        research = (PROPOSAL / "RESEARCH_RECORD.md").read_text(encoding="utf-8")
        for qid in ("Q380519", "Q56247746", "Q866375"):
            self.assertIn(qid, research)
        self.assertIn("not reconciled", research)
        self.assertIn("publisher:paramount", research)


if __name__ == "__main__":
    unittest.main()
