"""Source-local episode-order reconciliation never becomes canonical admission."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "compare_episode_rosters.py"
TOS = ROOT / "proposals" / "discovery" / "tos-publisher-s01-b001-20261102"
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("roster_comparison", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PublisherRosterComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.left = mod.read_json(TOS / "paramountplus.json")
        cls.right = mod.read_json(TOS / "plutotv.json")
        cls.catalog = mod.read_json(ROOT / "registry" / "mission_catalog.json")

    def compare(self, left=None, right=None):
        return mod.compare(copy.deepcopy(left if left is not None else self.left),
                           copy.deepcopy(right if right is not None else self.right), self.catalog)

    def test_actual_tos_rosters_surface_shifted_order_and_sample_boundaries(self):
        report = self.compare()
        self.assertEqual(report["counts"], {
            "shared_title_candidates": 4,
            "matching_source_local_slots": 0,
            "conflicting_source_local_slots": 4,
            "left_only_sample_candidates": 1,
            "right_only_sample_candidates": 1,
        })
        self.assertEqual(report["left_only_sample_candidates"][0]["title"], "The Cage")
        self.assertEqual(report["right_only_sample_candidates"][0]["title"], "The Enemy Within")
        man_trap = next(row for row in report["shared_title_candidates"] if row["left_title"] == "The Man Trap")
        self.assertEqual(man_trap["left_slot"], {"season": 1, "episode_number": 2})
        self.assertEqual(man_trap["right_slot"], {"season": 1, "episode_number": 1})
        self.assertEqual(man_trap["work_identity"], "UNRESOLVED")
        self.assertTrue(report["same_independence_group"])
        self.assertEqual(report["independent_corroboration_effect"], "NONE")
        self.assertTrue(any("original broadcast order" in note for note in report["notes"]))
        self.assertTrue(any("pilot/production order" in note for note in report["notes"]))

    def test_candidate_status_and_coverage_never_elevated(self):
        report = self.compare()
        self.assertEqual(report["comparison_status"], "UNRESOLVED_SOURCE_LOCAL_LISTINGS")
        self.assertEqual(report["roster_completeness"], "UNRESOLVED")
        for field in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(report[field], "NONE")
        self.assertTrue(all(row["work_identity"] == "UNRESOLVED" for row in report["shared_title_candidates"]))
        self.assertFalse(any("canonical_work_id" in row for row in report["shared_title_candidates"]))

    def test_deterministic_repeated_and_source_order_changes_are_explicit(self):
        first = self.compare()
        self.assertEqual(first, self.compare())
        self.assertEqual(first["comparison_sha256"], mod.digest({k: v for k, v in first.items() if k != "comparison_sha256"}))
        swapped = self.compare(self.right, self.left)
        self.assertEqual(first["counts"], swapped["counts"])
        self.assertEqual(swapped["left_only_sample_candidates"][0]["title"], "The Enemy Within")
        self.assertNotEqual(first["comparison_sha256"], swapped["comparison_sha256"])

    def test_match_does_not_claim_independent_order_authority(self):
        right = copy.deepcopy(self.left)
        right["batch_id"] = "TOS-DISTINCT-SOURCE-OBSERVATION"
        right["observation"]["publisher"] = "Second publisher display"
        right["observation"]["primary_locator"] = "https://example.org/second-roster/"
        report = self.compare(right=right)
        self.assertEqual(report["counts"]["matching_source_local_slots"], 5)
        self.assertEqual(report["independent_corroboration_effect"], "NONE")
        self.assertTrue(report["same_independence_group"])
        self.assertEqual(report["roster_completeness"], "UNRESOLVED")

    def test_distinct_source_family_still_does_not_automatically_corroborate(self):
        right = copy.deepcopy(self.right)
        right["observation"]["independence_group"] = "publisher:unrelated-example"
        report = self.compare(right=right)
        self.assertFalse(report["same_independence_group"])
        self.assertEqual(report["independent_corroboration_effect"], "NONE")

    def test_cross_mission_comparison_fails_closed(self):
        right = copy.deepcopy(self.right)
        right["mission_id"] = "tng"
        with self.assertRaisesRegex(mod.Rejected, "different Missions"):
            self.compare(right=right)

    def test_self_comparison_and_same_locator_rejected(self):
        with self.assertRaisesRegex(mod.Rejected, "distinct source-local"):
            self.compare(self.left, self.left)
        right = copy.deepcopy(self.right)
        right["observation"]["primary_locator"] = self.left["observation"]["primary_locator"]
        with self.assertRaisesRegex(mod.Rejected, "distinct source-local"):
            self.compare(right=right)

    def test_duplicate_titles_and_unicode_lookalikes_rejected(self):
        right = copy.deepcopy(self.right)
        right["episode_slots"][1]["title"] = right["episode_slots"][0]["title"]
        with self.assertRaisesRegex(mod.Rejected, "duplicate publisher title"):
            self.compare(right=right)
        right = copy.deepcopy(self.right)
        right["episode_slots"][1]["title"] = "Ｔｈｅ Ｍａｎ Ｔｒａｐ"
        with self.assertRaisesRegex(mod.Rejected, "normalized title collision"):
            self.compare(right=right)

    def test_promoted_input_status_is_not_accepted(self):
        right = copy.deepcopy(self.right)
        right["episode_slots"][0]["canonical_work_id"] = "W999"
        with self.assertRaisesRegex(mod.Rejected, "cannot create Work"):
            self.compare(right=right)
        right = copy.deepcopy(self.right)
        right["coverage_effect"] = "SOURCE_BOUND"
        with self.assertRaisesRegex(mod.Rejected, "cannot change accepted state"):
            self.compare(right=right)

    def test_cli_readonly_and_deterministic(self):
        args = [sys.executable, str(TOOL), "--left", str(TOS / "paramountplus.json"),
                "--right", str(TOS / "plutotv.json")]
        before = [p.read_bytes() for p in (TOS / "paramountplus.json", TOS / "plutotv.json")]
        first = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        second = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        parsed = json.loads(first.stdout)
        self.assertEqual(parsed["counts"]["conflicting_source_local_slots"], 4)
        self.assertEqual(before, [p.read_bytes() for p in (TOS / "paramountplus.json", TOS / "plutotv.json")])


if __name__ == "__main__":
    unittest.main()
