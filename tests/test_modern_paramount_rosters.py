"""Bounded modern Paramount+ candidate receipt integrity, not source authentication."""

import copy
import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from normalize_episode_roster import build_proposal
from validate_publisher_episode_roster import CATALOG, Rejected, read_json, validate


DIR = ROOT / "proposals/discovery/modern-paramount-season1-20261102"
SECOND = ROOT / "proposals/discovery/modern-paramount-season2-first5-20261102"
EXPECTED = {"dis": 15, "pic": 10, "ld": 10, "snw": 10}
SLUGS = {
    "dis": "star-trek-discovery", "pic": "star-trek-picard",
    "ld": "star-trek-lower-decks", "snw": "star-trek-strange-new-worlds",
}


class ModernParamountCandidateTests(unittest.TestCase):
    def test_exact_receipts_and_offline_rebuild_are_bounded(self):
        for mission, count in EXPECTED.items():
            with self.subTest(mission=mission):
                csv_bytes = (DIR / f"{mission}-observed-slots.csv").read_bytes()
                receipt = read_json(DIR / f"{mission}-observation.json")
                proposal = read_json(DIR / mission / "bundle.json")
                self.assertEqual(hashlib.sha256(csv_bytes).hexdigest(), receipt["csv_sha256"])
                self.assertEqual(proposal, build_proposal(receipt, csv_bytes, read_json(CATALOG)))
                accepted = validate(proposal, read_json(CATALOG))
                self.assertEqual(accepted["listed_slots"], count)
                self.assertEqual(accepted["accepted_effect"], "NONE")
                self.assertEqual(proposal["listed_slot_count"], count)

    def test_source_locator_and_source_local_numbering_are_explicit(self):
        for mission in EXPECTED:
            with self.subTest(mission=mission):
                data = read_json(DIR / mission / "bundle.json")
                observation = data["observation"]
                self.assertEqual(observation["primary_locator"],
                                 f"https://www.paramountplus.com/shows/{SLUGS[mission]}/episodes/1/")
                self.assertEqual(observation["independence_group"], "publisher:paramountplus.com")
                self.assertEqual([row["episode_number"] for row in data["episode_slots"]],
                                 list(range(1, EXPECTED[mission] + 1)))
                self.assertTrue(all(row["season"] == 1 for row in data["episode_slots"]))

    def test_no_proposal_admits_evidence_or_creates_work_identity(self):
        for mission in EXPECTED:
            with self.subTest(mission=mission):
                data = read_json(DIR / mission / "bundle.json")
                for field in ("coverage_effect", "denominator_effect", "accepted_work_effect",
                              "accepted_source_binding_effect"):
                    self.assertEqual(data[field], "NONE")
                self.assertEqual(data["roster_completeness"], "UNRESOLVED")
                self.assertEqual(data["proposal_status"], "CANDIDATE_METADATA_ONLY")
                self.assertEqual(data["observation"]["response_sha256"], None)
                self.assertFalse(data["observation"]["audiovisual_content_inspected"])
                self.assertTrue(all(row["canonical_work_id"] is None and row["source_binding_id"] is None
                                    and row["status"] == "CANDIDATE" for row in data["episode_slots"]))

    def test_unauthorized_canonical_or_coverage_promotion_is_refused(self):
        data = read_json(DIR / "pic/bundle.json")
        bad = copy.deepcopy(data)
        bad["episode_slots"][0]["canonical_work_id"] = "fabricated:pic:s1:e1"
        with self.assertRaises(Rejected):
            validate(bad, read_json(CATALOG))
        bad = copy.deepcopy(data)
        bad["denominator_effect"] = "COMPLETE"
        with self.assertRaises(Rejected):
            validate(bad, read_json(CATALOG))

    def test_duplicate_slot_is_refused_even_if_sequential_count_is_same(self):
        data = read_json(DIR / "dis/bundle.json")
        bad = copy.deepcopy(data)
        bad["episode_slots"][1]["episode_number"] = 1
        with self.assertRaises(Rejected):
            validate(bad, read_json(CATALOG))

    def test_second_season_first_five_are_separately_pinned(self):
        for mission in EXPECTED:
            with self.subTest(mission=mission):
                source = (SECOND / f"{mission}-observed-slots.csv").read_bytes()
                receipt = read_json(SECOND / f"{mission}-observation.json")
                proposal = read_json(SECOND / mission / "bundle.json")
                self.assertEqual(hashlib.sha256(source).hexdigest(), receipt["csv_sha256"])
                self.assertEqual(proposal, build_proposal(receipt, source, read_json(CATALOG)))
                self.assertEqual(validate(proposal, read_json(CATALOG))["listed_slots"], 5)
                self.assertEqual(proposal["observation"]["primary_locator"],
                                 f"https://www.paramountplus.com/shows/{SLUGS[mission]}/episodes/2/")
                self.assertEqual([(row["season"], row["episode_number"])
                                  for row in proposal["episode_slots"]],
                                 [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)])
                self.assertEqual(proposal["roster_completeness"], "UNRESOLVED")
                self.assertEqual(proposal["accepted_work_effect"], "NONE")
                self.assertEqual(proposal["coverage_effect"], "NONE")

    def test_second_season_cannot_promote_source_binding(self):
        candidate = read_json(SECOND / "snw/bundle.json")
        forged = copy.deepcopy(candidate)
        forged["episode_slots"][0]["source_binding_id"] = "fabricated-source-binding"
        with self.assertRaises(Rejected):
            validate(forged, read_json(CATALOG))


if __name__ == "__main__":
    unittest.main()
