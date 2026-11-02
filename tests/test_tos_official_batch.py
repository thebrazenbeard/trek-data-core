"""Regression checks for the two deliberately incompatible TOS publisher rosters."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/discovery/tos-publisher-s01-b001-20261102"
spec = importlib.util.spec_from_file_location("publisher_validator_tos", ROOT / "tools/validate_publisher_episode_roster.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TosPublisherBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mission_catalog = json.loads((ROOT / "registry/mission_catalog.json").read_text(encoding="utf-8"))

    def read(self, publisher):
        return json.loads((PROPOSAL / (publisher + ".json")).read_text(encoding="utf-8"))

    def test_both_rosters_are_candidate_only_under_existing_contract(self):
        for publisher in ("paramountplus", "plutotv"):
            with self.subTest(publisher=publisher):
                candidate = self.read(publisher)
                self.assertEqual(validator.validate(candidate, self.mission_catalog), {
                    "mission_id": "tos", "listed_slots": 5,
                    "roster_completeness": "UNRESOLVED", "accepted_effect": "NONE",
                })
                self.assertFalse(candidate["observation"]["audiovisual_content_inspected"])
                self.assertIsNone(candidate["observation"]["response_sha256"])
                self.assertEqual(candidate["observation"]["independence_group"], "publisher:paramount")

    def test_source_local_ordinals_are_not_silently_conflated(self):
        paramount = self.read("paramountplus")["episode_slots"]
        pluto = self.read("plutotv")["episode_slots"]
        self.assertEqual([r["title"] for r in paramount], [
            "The Cage", "The Man Trap", 'Charlie "X"', "Where No Man Has Gone Before", "The Naked Time",
        ])
        self.assertEqual([r["title"] for r in pluto], [
            "The Man Trap", 'Charlie "X"', "Where No Man Has Gone Before", "The Naked Time", "The Enemy Within",
        ])
        self.assertNotEqual(paramount[0]["title"], pluto[0]["title"])
        self.assertTrue(all(r["canonical_work_id"] is None and r["source_binding_id"] is None
                            for r in paramount + pluto))


if __name__ == "__main__":
    unittest.main()
