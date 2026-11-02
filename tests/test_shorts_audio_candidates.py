"""Hard boundaries for short-form and scripted-audio discovery-only metadata."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import build_shorts_audio_candidates as shortform


ROOT = Path(__file__).resolve().parents[1]


class ShortFormDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.bundle = shortform.read_bundle(ROOT)

    def test_real_tranche_separates_three_work_containers(self):
        emitted = shortform.validate(self.bundle)
        self.assertEqual(emitted["container_count"], 3)
        self.assertEqual(emitted["short_candidate_count"], 15)
        self.assertEqual({row["medium"] for row in emitted["container_candidates"]}, {"AUDIOVISUAL", "PROMOTIONAL_ANIMATION", "SCRIPTED_AUDIO"})
        self.assertEqual(sum(row["parent_candidate_id"] == "short-treks" for row in emitted["short_candidates"]), 10)
        self.assertEqual(sum(row["parent_candidate_id"] == "very-short-treks" for row in emitted["short_candidates"]), 5)
        self.assertEqual({row["verification_status"] for row in emitted["short_candidates"]}, {"UNVERIFIED_METADATA"})
        self.assertFalse(emitted["universe_complete"])

    def test_publisher_slots_not_equal_promo_release_order(self):
        emitted = shortform.validate(self.bundle)
        by_parent = {parent: {row["slot_meaning"] for row in emitted["short_candidates"] if row["parent_candidate_id"] == parent}
                     for parent in ("short-treks", "very-short-treks")}
        self.assertEqual(by_parent["short-treks"], {"OFFICIAL_EPISODE_GUIDE"})
        self.assertEqual(by_parent["very-short-treks"], {"ANNOUNCED_RELEASE_ORDER"})
        self.assertFalse(any(row["parent_candidate_id"] == "khan-audio" for row in emitted["short_candidates"]))

    def test_generated_bytes_reproducible(self):
        self.assertEqual((ROOT / shortform.OUTPUT).read_bytes(), shortform.build(ROOT))

    def test_admission_and_coverage_promotions_rejected(self):
        for key, forged in (("admission_effect", "ACCEPTED"), ("coverage_effect", "SOURCE_BOUND"),
                            ("universe_complete", True), ("universe_complete", 0), ("proposal_only", 1)):
            with self.subTest(key=key):
                mutated = copy.deepcopy(self.bundle)
                mutated[key] = forged
                with self.assertRaisesRegex(ValueError, "discovery-only boundary"):
                    shortform.validate(mutated)
        mutated = copy.deepcopy(self.bundle)
        mutated["installments"][0]["canonical_work_id"] = "some-accepted-work"
        with self.assertRaisesRegex(ValueError, "fields"):
            shortform.validate(mutated)

    def test_publisher_identity_and_locator_are_pinned(self):
        mutated = copy.deepcopy(self.bundle)
        mutated["sources"][0]["url"] = "https://evil.example/shows/star-trek-short-treks/episodes/"
        with self.assertRaisesRegex(ValueError, "publisher source lineage"):
            shortform.validate(mutated)
        mutated = copy.deepcopy(self.bundle)
        mutated["publisher_independence_group"] = "publisher:three-independent-witnesses"
        with self.assertRaisesRegex(ValueError, "discovery-only boundary"):
            shortform.validate(mutated)

    def test_reject_duplicate_ids_slots_and_titles(self):
        for field in ("candidate_id", "source_local_slot", "title"):
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.bundle)
                mutated["installments"][1][field] = mutated["installments"][0][field]
                with self.assertRaises(ValueError):
                    shortform.validate(mutated)

    def test_audio_episode_or_forged_ordinal_rejected(self):
        mutated = copy.deepcopy(self.bundle)
        mutated["installments"][0]["parent_candidate_id"] = "khan-audio"
        with self.assertRaisesRegex(ValueError, "no evidenced episodes"):
            shortform.validate(mutated)
        mutated = copy.deepcopy(self.bundle)
        mutated["installments"][-1]["source_local_slot"] = "S1E5"
        with self.assertRaisesRegex(ValueError, "slot mismatch"):
            shortform.validate(mutated)

    def test_duplicate_json_object_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            json.loads('{"proposal_only":true,"proposal_only":false}', object_pairs_hook=shortform.unique_object_keys)

    def test_check_detects_stale_bytes_and_symlink_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / shortform.INPUT
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps(self.bundle), encoding="utf-8")
            target = root / shortform.OUTPUT
            self.assertEqual(shortform.main(["--repo-root", folder]), 0)
            self.assertEqual(shortform.main(["--repo-root", folder, "--check"]), 0)
            target.write_bytes(b"altered")
            self.assertEqual(shortform.main(["--repo-root", folder, "--check"]), 1)
            target.unlink()
            victim = root / "do-not-touch.json"
            victim.write_bytes(b"protected")
            target.symlink_to(victim)
            self.assertEqual(shortform.main(["--repo-root", folder]), 1)
            self.assertEqual(victim.read_bytes(), b"protected")


if __name__ == "__main__":
    unittest.main()
