"""Season 5 publisher-source observations are never admitted research."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_publisher_s5_discovery as s5

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / s5.BASE
COUNTS = {"tng": 26, "ds9": 26, "voy": 25, "dis": 10, "ld": 10}


class PublisherSeasonFiveTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(BASE, root / s5.BASE)
        (root / "registry").mkdir()
        shutil.copy2(ROOT / "registry/mission_catalog.json", root / "registry/mission_catalog.json")
        return root

    def test_official_captured_observations_are_bounded_and_canonical(self):
        self.assertEqual(s5.check(), 0)
        index = json.loads((BASE / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["independence_group"], "publisher:paramount")
        self.assertEqual(index["proposal_status"], "DISCOVERY_ONLY")
        for effect in ("admission_effect", "coverage_effect", "denominator_effect"):
            self.assertEqual(index[effect], "NONE")
        self.assertEqual([(item["mission_id"], item["listed_slot_count"])
                          for item in index["source_pages"]], list(COUNTS.items()))
        self.assertEqual(sum(COUNTS.values()), 97)
        for item in index["source_pages"]:
            mission = item["mission_id"]
            self.assertEqual(item["official_page"], s5.official_url(mission))
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
        path = root / s5.BASE / "voy.csv"
        path.write_bytes(path.read_bytes() + b"5,99,Forged\n")
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "CSV hash mismatch"):
                s5.check()

    def test_bundle_cannot_claim_reconciled_episode_or_admission(self):
        root = self.fixture()
        path = root / s5.BASE / "tng/bundle.json"
        proposal = json.loads(path.read_text(encoding="utf-8"))
        proposal["episode_slots"][0]["canonical_work_id"] = "fabricated-work"
        path.write_bytes(s5.source_tools.serialized(proposal))
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "stale or modified"):
                s5.check()

    def test_official_page_forgery_is_detected(self):
        root = self.fixture()
        path = root / s5.BASE / "index.json"
        index = json.loads(path.read_text(encoding="utf-8"))
        index["source_pages"][0]["official_page"] = "https://forged.invalid/"
        path.write_bytes(s5.source_tools.serialized(index))
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "publisher locator mismatch"):
                s5.check()

    def test_symlinked_csv_refused_without_following(self):
        root = self.fixture()
        victim = root / "outside"
        victim.write_bytes(b"Do not overwrite\n")
        path = root / s5.BASE / "ld.csv"
        path.unlink()
        path.symlink_to(victim)
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s5.check()
        self.assertEqual(victim.read_bytes(), b"Do not overwrite\n")

    def test_ingest_refuses_symlinked_index_before_any_write(self):
        root = self.fixture()
        victim = root / "outside"
        victim.write_bytes(b"Protected\n")
        index = root / s5.BASE / "index.json"
        index.unlink()
        index.symlink_to(victim)
        previous_csv = (root / s5.BASE / "dis.csv").read_bytes()
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s5.ingest(root)
        self.assertEqual(victim.read_bytes(), b"Protected\n")
        self.assertEqual((root / s5.BASE / "dis.csv").read_bytes(), previous_csv)

    def test_raw_source_symlink_and_fifo_are_rejected(self):
        root = self.fixture()
        outside = root / "raw-source.html"
        outside.write_bytes(b"private source\n" * 2000)
        source_link = root / "source-link.html"
        source_link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink forbidden"):
            s5.read_raw_response(source_link)
        self.assertEqual(outside.read_bytes(), b"private source\n" * 2000)
        special = root / "source-fifo"
        os.mkfifo(special)
        with self.assertRaisesRegex(ValueError, "bounded regular HTML"):
            s5.read_raw_response(special)

    def test_atomic_writer_rejects_symlinked_leaf_and_parent(self):
        root = self.fixture()
        target = root / "outside"
        target.write_bytes(b"protected\n")
        destination = root / s5.BASE / "index.json"
        destination.unlink()
        destination.symlink_to(target)
        with patch.object(s5, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s5.safe_atomic_write(s5.BASE / "index.json", b"corrupt\n")
            (root / s5.BASE / "shortcut").symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                s5.safe_atomic_write(s5.BASE / "shortcut" / "outside", b"corrupt\n")
        self.assertEqual(target.read_bytes(), b"protected\n")

    def test_episode_parser_does_not_invent_missing_two_part_ordinals(self):
        rows = [(5, 1, "Premiere"), (5, 3, "Second"), (5, 4, "Third"),
                (5, 5, "Fourth"), (5, 6, "Fifth")]
        self.assertEqual(s5.parse_csv(s5.csv_bytes(rows)), rows)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            s5.parse_csv(s5.csv_bytes(rows[:1] + rows[:1] + rows[1:]))
        with self.assertRaisesRegex(ValueError, "invalid episode title"):
            s5.parse_csv(s5.csv_bytes([(5, 1, "<script>")] + rows[1:]))
        with self.assertRaisesRegex(ValueError, "invalid season"):
            s5.parse_csv(s5.csv_bytes([(4, 1, "Older season")] + rows[1:]))

    def test_voyager_source_gap_is_retained_without_invented_work(self):
        rows = s5.parse_csv((BASE / "voy.csv").read_bytes())
        self.assertEqual(len(rows), 25)
        self.assertEqual([n for _, n, _ in rows], list(range(1, 16)) + list(range(17, 27)))
        self.assertEqual(rows[14][2], "Dark Frontier")

    def test_source_parser_rejects_spoofed_missing_and_ambiguous_canonical_links(self):
        """Otherwise plausible cards cannot be attributed to a forged page."""
        official = s5.official_url("tng")
        canonical = f'<link rel="canonical" href="{official}"/>'
        cards = "".join(
            f'<div class="episode"><div class="epTitle"><h2>Card {n}</h2></div>'
            f'<abbr class="seNum">S5</abbr><abbr class="epNum">E{n}</abbr>'
            for n in range(1, 6)
        )
        baseline = f'<html><head>{canonical}</head><body>{cards}{" " * 11000}</body></html>'
        self.assertEqual(len(s5.parse_cards(baseline.encode(), "tng")), 5)
        forbidden = (
            baseline.replace(official, "https://forged.invalid/shows/tng/episodes/5/"),
            baseline.replace(canonical, ""),
            baseline.replace(canonical, canonical + canonical),
            baseline.replace(canonical, canonical + f'<link rel="canonical" href="{official}"/>'),
            baseline.replace(canonical, f'<link rel="canonical" href="{official}" href="https://forged.invalid/"/>'),
            baseline.replace(canonical, f'<link rel="canonical" rel="alternate" href="{official}"/>'),
        )
        for altered in forbidden:
            with self.subTest(altered=altered[:160]):
                with self.assertRaisesRegex(ValueError, "canonical publisher locator"):
                    s5.parse_cards(altered.encode(), "tng")


if __name__ == "__main__":
    unittest.main()
