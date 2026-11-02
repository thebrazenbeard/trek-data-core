"""Publisher Season 3 metadata candidates do not advance accepted research."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_legacy_s3_discovery as legacy


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / legacy.BASE


class LegacySeasonThreeTests(unittest.TestCase):
    COUNTS = {"tos": 24, "tng": 26, "ds9": 26, "voy": 26, "ent": 24}

    def test_source_attributed_bounded_five_series_126_cards(self):
        self.assertEqual(legacy.check(), 0)
        index = json.loads((BASE / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["proposal_status"], "DISCOVERY_ONLY")
        self.assertEqual(index["admission_effect"], "NONE")
        self.assertEqual(index["coverage_effect"], "NONE")
        self.assertEqual(index["denominator_effect"], "NONE")
        self.assertEqual(sum(row["listed_slot_count"] for row in index["source_pages"]), 126)
        self.assertEqual([(row["mission_id"], row["listed_slot_count"])
                          for row in index["source_pages"]], list(self.COUNTS.items()))

    def test_each_official_page_and_candidate_bundle_is_source_local(self):
        for mission, count in self.COUNTS.items():
            with self.subTest(mission=mission):
                bundle = json.loads((BASE / mission / "bundle.json").read_text(encoding="utf-8"))
                self.assertEqual(bundle["listed_slot_count"], count)
                self.assertEqual(bundle["observation"]["primary_locator"], legacy.official_url(mission))
                self.assertEqual(bundle["observation"]["independence_group"], "publisher:paramount")
                self.assertEqual(bundle["roster_completeness"], "UNRESOLVED")
                self.assertIs(bundle["observation"]["audiovisual_content_inspected"], False)
                self.assertIsNone(bundle["observation"]["response_sha256"])
                for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
                    self.assertEqual(bundle[effect], "NONE")
                self.assertTrue(all(row["status"] == "CANDIDATE" and row["canonical_work_id"] is None and row["source_binding_id"] is None
                                    for row in bundle["episode_slots"]))

    def test_no_invented_episode_count_or_completeness(self):
        for mission in self.COUNTS:
            bundle = json.loads((BASE / mission / "bundle.json").read_text(encoding="utf-8"))
            self.assertNotIn("canonical_episode_denominator", bundle)
            self.assertNotIn("admitted_briefing_count", bundle)
        # An observation of a publisher listing row never implies an accepted Work.
        tng = json.loads((BASE / "tng" / "bundle.json").read_text(encoding="utf-8"))
        self.assertEqual(tng["episode_slots"][0]["title"], "Evolution")
        self.assertEqual(tng["episode_slots"][0]["episode_number"], 1)

    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(BASE, root / legacy.BASE)
        (root / "registry").mkdir()
        shutil.copy2(ROOT / "registry/mission_catalog.json", root / "registry/mission_catalog.json")
        return root

    def test_mutated_csv_hash_is_refused(self):
        root = self.fixture()
        path = root / legacy.BASE / "tos.csv"
        path.write_bytes(path.read_bytes() + b"3,27,Forged Slot\n")
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                legacy.check()

    def test_changed_bundle_cannot_claim_acceptance(self):
        root = self.fixture()
        path = root / legacy.BASE / "ds9/bundle.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["coverage_effect"] = "SOURCE_BOUND"
        path.write_bytes(legacy.serialized(data))
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "stale or modified"):
                legacy.check()

    def test_forged_source_locator_rejected(self):
        root = self.fixture()
        path = root / legacy.BASE / "index.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["source_pages"][1]["official_page"] = "https://example.org/episodes/3/"
        path.write_bytes(legacy.serialized(data))
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "publisher locator mismatch"):
                legacy.check()

    def test_csv_bundle_symlink_refused_without_following(self):
        root = self.fixture()
        victim = root / "victim"
        victim.write_text("outside proposal\n", encoding="utf-8")
        path = root / legacy.BASE / "voy.csv"
        path.unlink()
        path.symlink_to(victim)
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                legacy.check()
        self.assertEqual(victim.read_text(encoding="utf-8"), "outside proposal\n")

    def test_ingest_refuses_symlinked_index_before_any_output_changes(self):
        root = self.fixture()
        target = root / "outside-index"
        target.write_text("protected\n", encoding="utf-8")
        index = root / legacy.BASE / "index.json"
        index.unlink()
        index.symlink_to(target)
        original_csv = (root / legacy.BASE / "tos.csv").read_bytes()
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                legacy.ingest(root)
        self.assertEqual(target.read_text(encoding="utf-8"), "protected\n")
        self.assertEqual((root / legacy.BASE / "tos.csv").read_bytes(), original_csv)

    def test_atomic_output_refuses_symlinked_parent_or_leaf(self):
        root = self.fixture()
        victim = root / "outside-index"
        victim.write_text("protected\n", encoding="utf-8")
        index = root / legacy.BASE / "index.json"
        index.unlink()
        index.symlink_to(victim)
        with patch.object(legacy, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                legacy.safe_atomic_write(legacy.BASE / "index.json", b"tampered\n")
            directory = root / legacy.BASE / "escape"
            directory.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                legacy.safe_atomic_write(legacy.BASE / "escape" / "outside-index", b"tampered\n")
        self.assertEqual(victim.read_text(encoding="utf-8"), "protected\n")

    def test_atomic_output_replaces_regular_file_without_residual_temp_file(self):
        root = self.fixture()
        relative = legacy.BASE / "index.json"
        with patch.object(legacy, "ROOT", root):
            legacy.safe_atomic_write(relative, b"updated index\n")
        self.assertEqual((root / relative).read_bytes(), b"updated index\n")
        self.assertEqual(list((root / legacy.BASE).glob(".trek-legacy-*.tmp")), [])

    def test_duplicate_or_html_title_rejected_by_parser(self):
        rows = [(3, 1, "First"), (3, 1, "Second"), (3, 3, "Third"), (3, 4, "Fourth"), (3, 5, "Fifth")]
        with self.assertRaisesRegex(ValueError, "duplicate or unsorted"):
            legacy.parse_csv(legacy.csv_bytes(rows))
        bad = [(3, 1, "First"), (3, 2, "<script>"), (3, 3, "Third"), (3, 4, "Fourth"), (3, 5, "Fifth")]
        with self.assertRaisesRegex(ValueError, "invalid title"):
            legacy.parse_csv(legacy.csv_bytes(bad))

    def test_source_snapshot_digest_shape_is_separate_from_admission(self):
        index = json.loads((BASE / "index.json").read_text(encoding="utf-8"))
        for receipt in index["source_pages"]:
            self.assertRegex(receipt["source_body_sha256"], r"^[a-f0-9]{64}$")
            self.assertGreater(receipt["source_body_bytes"], 10_000)
            self.assertNotIn("signature", receipt)
            self.assertNotIn("source_body", receipt)


if __name__ == "__main__":
    unittest.main()
