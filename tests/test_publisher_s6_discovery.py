"""Season 6 publisher-source observations are never admitted research."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_publisher_s6_discovery as s6

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / s6.BASE
COUNTS = {"tng": 26, "ds9": 26, "voy": 26}


class PublisherSeasonSixTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(BASE, root / s6.BASE)
        (root / "registry").mkdir()
        shutil.copy2(ROOT / "registry/mission_catalog.json", root / "registry/mission_catalog.json")
        return root

    def test_official_captured_observations_are_bounded_and_canonical(self):
        self.assertEqual(s6.check(), 0)
        index = json.loads((BASE / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["independence_group"], "publisher:paramount")
        self.assertEqual(index["proposal_status"], "DISCOVERY_ONLY")
        for effect in ("admission_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(index[effect], "NONE")
        self.assertEqual([(item["mission_id"], item["listed_slot_count"])
                          for item in index["source_pages"]], list(COUNTS.items()))
        self.assertEqual(sum(COUNTS.values()), 78)
        for item in index["source_pages"]:
            mission = item["mission_id"]
            self.assertEqual(item["official_page"], s6.official_url(mission))
            self.assertRegex(item["source_body_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(item["source_body_bytes"], 10_000)
            self.assertNotIn("source_body", item)
            proposal = json.loads((BASE / mission / "bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(proposal["listed_slot_count"], COUNTS[mission])
            self.assertEqual(proposal["roster_completeness"], "UNRESOLVED")
            self.assertFalse(proposal["observation"]["audiovisual_content_inspected"])
            self.assertIsNone(proposal["observation"]["response_sha256"])
            for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
                self.assertEqual(proposal[effect], "NONE")
            self.assertTrue(all(row["status"] == "CANDIDATE" and
                                row["canonical_work_id"] is None and row["source_binding_id"] is None
                                for row in proposal["episode_slots"]))

    def test_source_csv_changed_after_capture_is_detected(self):
        root = self.fixture()
        path = root / s6.BASE / "voy.csv"
        path.write_bytes(path.read_bytes() + b"4,99,Forged\n")
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "CSV hash mismatch"):
                s6.check()

    def test_bundle_cannot_claim_reconciled_episode_or_admission(self):
        root = self.fixture()
        path = root / s6.BASE / "tng/bundle.json"
        proposal = json.loads(path.read_text(encoding="utf-8"))
        proposal["episode_slots"][0]["canonical_work_id"] = "fabricated-work"
        path.write_bytes(s6.source_tools.serialized(proposal))
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "stale or modified"):
                s6.check()

    def test_official_page_forgery_is_detected(self):
        root = self.fixture()
        path = root / s6.BASE / "index.json"
        index = json.loads(path.read_text(encoding="utf-8"))
        index["source_pages"][0]["official_page"] = "https://forged.invalid/"
        path.write_bytes(s6.source_tools.serialized(index))
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "publisher locator mismatch"):
                s6.check()

    def test_symlinked_csv_refused_without_following(self):
        root = self.fixture()
        victim = root / "outside"
        victim.write_bytes(b"Do not overwrite\n")
        path = root / s6.BASE / "ds9.csv"
        path.unlink()
        path.symlink_to(victim)
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s6.check()
        self.assertEqual(victim.read_bytes(), b"Do not overwrite\n")

    def test_ingest_refuses_symlinked_index_before_any_write(self):
        root = self.fixture()
        victim = root / "outside"
        victim.write_bytes(b"Protected\n")
        index = root / s6.BASE / "index.json"
        index.unlink()
        index.symlink_to(victim)
        previous_csv = (root / s6.BASE / "tng.csv").read_bytes()
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s6.ingest(root)
        self.assertEqual(victim.read_bytes(), b"Protected\n")
        self.assertEqual((root / s6.BASE / "tng.csv").read_bytes(), previous_csv)

    def test_raw_source_symlink_and_fifo_are_rejected(self):
        root = self.fixture()
        outside = root / "raw-source.html"
        outside.write_bytes(b"private source\n" * 2000)
        source_link = root / "source-link.html"
        source_link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink forbidden"):
            s6.read_raw_response(source_link)
        self.assertEqual(outside.read_bytes(), b"private source\n" * 2000)
        special = root / "source-fifo"
        os.mkfifo(special)
        with self.assertRaisesRegex(ValueError, "bounded regular HTML"):
            s6.read_raw_response(special)

    def test_atomic_writer_rejects_symlinked_leaf_and_parent(self):
        root = self.fixture()
        target = root / "outside"
        target.write_bytes(b"protected\n")
        destination = root / s6.BASE / "index.json"
        destination.unlink()
        destination.symlink_to(target)
        with patch.object(s6, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s6.safe_atomic_write(s6.BASE / "index.json", b"corrupt\n")
            (root / s6.BASE / "shortcut").symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s6.safe_atomic_write(s6.BASE / "shortcut" / "outside", b"corrupt\n")
        self.assertEqual(target.read_bytes(), b"protected\n")

    def test_episode_parser_does_not_invent_missing_two_part_ordinals(self):
        rows = [(6, 1, "Premiere"), (6, 3, "Second"), (6, 4, "Third"),
                (6, 5, "Fourth"), (6, 6, "Fifth")]
        self.assertEqual(s6.parse_csv(s6.csv_bytes(rows)), rows)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            s6.parse_csv(s6.csv_bytes(rows[:1] + rows[:1] + rows[1:]))
        with self.assertRaisesRegex(ValueError, "invalid episode title"):
            s6.parse_csv(s6.csv_bytes([(6, 1, "<script>")] + rows[1:]))
        with self.assertRaisesRegex(ValueError, "invalid season"):
            s6.parse_csv(s6.csv_bytes([(3, 1, "Older season")] + rows[1:]))

    def test_source_parser_rejects_forged_missing_and_duplicate_canonical_urls(self):
        """An otherwise valid card array must not launder a forged publisher page."""
        official = s6.official_url("tng")
        canonical = f'<link rel="canonical" href="{official}"/>'
        cards = "".join(
            f'<div class="episode"><div class="epTitle"><h2>Card {n}</h2></div>'
            f'<abbr class="seNum">S6</abbr><abbr class="epNum">E{n}</abbr>'
            for n in range(1, 6)
        )
        baseline = f'<html><head>{canonical}</head><body>{cards}{" " * 11000}</body></html>'
        self.assertEqual(len(s6.parse_cards(baseline.encode(), "tng")), 5)
        forbidden = (
            baseline.replace(official, "https://evil.example/shows/tng/episodes/6/"),
            baseline.replace(canonical, ""),
            baseline.replace(canonical, canonical + canonical),
            baseline.replace(canonical, canonical + f'<link href="{official}" rel="canonical">'),
            baseline.replace(canonical, f'<link rel="canonical" href="{official}" href="https://evil.example/">'),
        )
        for altered in forbidden:
            with self.subTest(altered=altered[:150]):
                with self.assertRaisesRegex(ValueError, "canonical publisher locator"):
                    s6.parse_cards(altered.encode(), "tng")


if __name__ == "__main__":
    unittest.main()
