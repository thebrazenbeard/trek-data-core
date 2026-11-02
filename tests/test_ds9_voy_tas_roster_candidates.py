"""Regression tests for three bounded 2026-11-02 publisher-slot proposals.

These tests prove structural proposal safety and deterministic offline
reconstruction; they do not independently authenticate the publisher pages.
"""

import copy
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from normalize_episode_roster import build_proposal
from validate_publisher_episode_roster import CATALOG, Rejected, read_json, validate

DIR = ROOT / "proposals/discovery/ds9-voy-episode-slots-20261102"


class CandidateSlotObservationsTests(unittest.TestCase):
    def test_three_bounded_batches_are_deterministic_and_unadmitted(self):
        for mission in ("ds9", "voy", "tas"):
            with self.subTest(mission=mission):
                raw = (DIR / f"{mission}-observed-slots.csv").read_bytes()
                receipt = read_json(DIR / f"{mission}-observation.json")
                proposal = read_json(DIR / mission / "bundle.json")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["csv_sha256"])
                self.assertEqual(proposal, build_proposal(receipt, raw, read_json(CATALOG)))
                summary = validate(proposal, read_json(CATALOG))
                self.assertEqual(summary["mission_id"], mission)
                self.assertEqual(summary["listed_slots"], 5)
                self.assertEqual(summary["accepted_effect"], "NONE")
                self.assertEqual(summary["roster_completeness"], "UNRESOLVED")
                self.assertEqual(proposal["observation"]["response_sha256"], None)
                self.assertEqual(proposal["observation"]["audiovisual_content_inspected"], False)
                self.assertTrue(all(row["canonical_work_id"] is None and
                                    row["source_binding_id"] is None for row in proposal["episode_slots"]))

    def test_combined_pilots_preserve_noncontiguous_platform_ordinals(self):
        for mission in ("ds9", "voy"):
            with self.subTest(mission=mission):
                proposal = read_json(DIR / mission / "bundle.json")
                self.assertEqual([(r["season"], r["episode_number"]) for r in proposal["episode_slots"]],
                                 [(1, 1), (1, 3), (1, 4), (1, 5), (1, 6)])
                self.assertNotIn("E2", str(proposal["episode_slots"]))

    def test_candidate_cannot_promote_itself_to_accepted_status(self):
        proposal = read_json(DIR / "ds9/bundle.json")
        forged = copy.deepcopy(proposal)
        forged["episode_slots"][0]["canonical_work_id"] = "fabricated:ds9:p1"
        with self.assertRaises(Rejected):
            validate(forged, read_json(CATALOG))
        forged = copy.deepcopy(proposal)
        forged["denominator_effect"] = "RESOLVED"
        with self.assertRaises(Rejected):
            validate(forged, read_json(CATALOG))


if __name__ == "__main__":
    unittest.main()
