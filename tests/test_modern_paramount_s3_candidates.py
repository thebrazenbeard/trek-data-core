"""No accepted progress from source-local Season 3 publisher episode listings."""

import copy
import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from normalize_episode_roster import build_proposal
from validate_publisher_episode_roster import CATALOG, Rejected, read_json, validate


BASE = ROOT / "proposals" / "discovery" / "modern-paramount-season3-20261102"
SOURCES = {
    "dis": ("star-trek-discovery", 13),
    "pic": ("star-trek-picard", 10),
    "ld": ("star-trek-lower-decks", 10),
    "snw": ("star-trek-strange-new-worlds", 10),
}


class ModernParamountSeasonThreeTests(unittest.TestCase):
    def test_replay_exact_csv_receipt_and_generated_proposals(self):
        catalog = read_json(CATALOG)
        observed_total = 0
        for mission, (slug, expected) in SOURCES.items():
            with self.subTest(mission=mission):
                raw = (BASE / f"{mission}-observed-slots.csv").read_bytes()
                receipt = read_json(BASE / f"{mission}-observation.json")
                bundle = read_json(BASE / mission / "bundle.json")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["csv_sha256"])
                self.assertEqual(bundle, build_proposal(receipt, raw, catalog))
                self.assertEqual(validate(bundle, catalog)["accepted_effect"], "NONE")
                self.assertEqual(bundle["listed_slot_count"], expected)
                self.assertEqual(receipt["primary_locator"],
                                 f"https://www.paramountplus.com/shows/{slug}/episodes/3/")
                self.assertEqual(bundle["observation"]["independence_group"], "publisher:paramountplus.com")
                self.assertEqual([(row["season"], row["episode_number"]) for row in bundle["episode_slots"]],
                                 [(3, index) for index in range(1, expected + 1)])
                for key in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
                    self.assertEqual(bundle[key], "NONE")
                self.assertTrue(all(row["canonical_work_id"] is None and row["source_binding_id"] is None
                                    for row in bundle["episode_slots"]))
                observed_total += expected
        self.assertEqual(observed_total, 43)

    def test_forged_identity_and_completeness_are_rejected(self):
        bundle = read_json(BASE / "pic/bundle.json")
        catalog = read_json(CATALOG)
        bad = copy.deepcopy(bundle)
        bad["episode_slots"][0]["canonical_work_id"] = "invented-picard-identity"
        with self.assertRaises(Rejected):
            validate(bad, catalog)
        bad = copy.deepcopy(bundle)
        bad["roster_completeness"] = "COMPLETE"
        with self.assertRaises(Rejected):
            validate(bad, catalog)


if __name__ == "__main__":
    unittest.main()
