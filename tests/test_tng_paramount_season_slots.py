"""Candidate-only Paramount+ TNG episode-slot observations."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "proposals" / "discovery" / "tng-paramount-season-slots-20261102"
spec = importlib.util.spec_from_file_location(
    "publisher_episode_roster", ROOT / "tools" / "validate_publisher_episode_roster.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TngParamountSeasonSlotTests(unittest.TestCase):
    EXPECTED = {
        "season-1": [(1, 10, 'Hide and "Q"'), (1, 23, "Skin of Evil"),
                     (1, 26, "The Neutral Zone")],
        "season-4": [(4, 3, "Brothers")],
        "season-5": [(5, 10, "New Ground")],
    }

    def test_three_season_scoped_bundle_shapes(self):
        catalog = json.loads((ROOT / "registry" / "mission_catalog.json").read_text(encoding="utf-8"))
        for season, expected in self.EXPECTED.items():
            with self.subTest(season=season):
                data = validator.read_json(BASE / season / "bundle.json")
                result = validator.validate(data, catalog)
                self.assertEqual(result["accepted_effect"], "NONE")
                self.assertEqual(data["mission_id"], "tng")
                self.assertEqual(data["listed_slot_count"], len(expected))
                self.assertEqual([(r["season"], r["episode_number"], r["title"])
                                  for r in data["episode_slots"]], expected)

    def test_provenance_is_conservatively_one_publisher_family(self):
        sources = set()
        for season in self.EXPECTED:
            data = validator.read_json(BASE / season / "bundle.json")
            observation = data["observation"]
            self.assertEqual(observation["independence_group"], "publisher:paramount")
            self.assertEqual(observation["observed_on"], "2026-11-02")
            self.assertIsNone(observation["response_sha256"])
            self.assertIsNone(observation["publisher_revision"])
            self.assertIs(observation["audiovisual_content_inspected"], False)
            self.assertEqual(data["proposal_status"], "CANDIDATE_METADATA_ONLY")
            self.assertEqual(data["roster_completeness"], "UNRESOLVED")
            self.assertTrue(observation["primary_locator"].startswith(
                "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/"))
            sources.add(observation["primary_locator"])
        self.assertEqual(len(sources), 3)

    def test_none_of_five_slots_can_admit_canonical_works_or_coverage(self):
        for season in self.EXPECTED:
            data = validator.read_json(BASE / season / "bundle.json")
            for key in ("accepted_work_effect", "accepted_source_binding_effect",
                        "coverage_effect", "denominator_effect"):
                self.assertEqual(data[key], "NONE")
            for row in data["episode_slots"]:
                self.assertEqual(row["status"], "CANDIDATE")
                self.assertIsNone(row["canonical_work_id"])
                self.assertIsNone(row["source_binding_id"])
            data["coverage_effect"] = "SOURCE_BOUND"
            with self.assertRaisesRegex(validator.Rejected, "cannot change accepted state"):
                validator.validate(data, json.loads(
                    (ROOT / "registry" / "mission_catalog.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
