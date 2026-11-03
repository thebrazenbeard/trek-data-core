"""TAS publisher rows remain source-relative discovery, not episode research."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_tas_publisher_roster as tas

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / tas.BASE


class TasPublisherRosterTests(unittest.TestCase):
    def fixture(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        shutil.copytree(BASE, root / tas.BASE)
        (root / "registry").mkdir()
        shutil.copy2(ROOT / "registry/mission_catalog.json", root / "registry/mission_catalog.json")
        return root

    def test_source_local_index_receipts_and_explicit_counts(self):
        self.assertEqual(tas.check(), 0)
        index = json.loads((BASE / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["independence_group"], "publisher:paramount")
        self.assertEqual(index["proposal_status"], "DISCOVERY_ONLY")
        self.assertTrue(all(index[f] == "NONE" for f in ("admission_effect", "coverage_effect", "denominator_effect")))
        self.assertEqual([p["listed_slot_count"] for p in index["source_pages"]], [16, 6])
        for season in tas.SEASONS:
            receipt = index["source_pages"][season - 1]
            self.assertEqual(receipt["official_page"], tas.official_url(season))
            self.assertRegex(receipt["source_body_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(receipt["source_body_bytes"], 10_000)
            bundle = json.loads((BASE / f"s{season}" / "bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle["listed_slot_count"], 16 if season == 1 else 6)
            self.assertFalse(bundle["observation"]["audiovisual_content_inspected"])
            self.assertIsNone(bundle["observation"]["response_sha256"])
            self.assertEqual(bundle["accepted_work_effect"], "NONE")
            self.assertTrue(all(slot["canonical_work_id"] is None and slot["source_binding_id"] is None
                                for slot in bundle["episode_slots"]))

    def test_old_first_five_are_explicit_overlap_not_new_canon(self):
        legacy = (ROOT / "proposals/discovery/ds9-voy-episode-slots-20261102/tas-observed-slots.csv").read_text()
        rows = tas.parse_csv((BASE / "s1.csv").read_bytes(), 1)
        self.assertEqual(rows[0][2], "Beyond the Farthest Star")
        self.assertEqual(rows[4][2], "More Tribbles, More Troubles")
        for season, ordinal, title in rows[:5]:
            self.assertIn(f"{season},{ordinal},", legacy)
            self.assertTrue(title)
        self.assertEqual(tas.parse_csv((BASE / "s2.csv").read_bytes(), 2)[-1][2],
                         "The Counterclock Incident")

    def test_publisher_csv_hash_tampering_is_detected(self):
        root = self.fixture()
        path = root / tas.BASE / "s2.csv"
        path.write_bytes(path.read_bytes() + b"2,99,Forged Episode\n")
        with patch.object(tas, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "CSV changed"):
                tas.check()

    def test_source_bundle_cannot_be_promoted_to_canon(self):
        root = self.fixture()
        path = root / tas.BASE / "s1/bundle.json"
        record = json.loads(path.read_text())
        record["episode_slots"][0]["canonical_work_id"] = "invented"
        path.write_bytes(tas.source.serialized(record))
        with patch.object(tas, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "bundle changed"):
                tas.check()

    def test_source_index_locator_forgery_fails(self):
        root = self.fixture()
        path = root / tas.BASE / "index.json"
        index = json.loads(path.read_text())
        index["source_pages"][0]["official_page"] = "https://forged.invalid/"
        path.write_bytes(tas.source.serialized(index))
        with patch.object(tas, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "invalid TAS publisher source receipt"):
                tas.check()

    def test_realistic_card_source_rejects_bad_canonical(self):
        url = tas.official_url(1)
        canonical = f'<link rel="canonical" href="{url}"/>'
        cards = "".join(
            f'<div class="episode"><div class="epTitle"><h2>Test Card {n}</h2></div>'
            f'<abbr class="seNum">S1</abbr><abbr class="epNum">E{n}</abbr>'
            for n in range(1, 6)
        )
        original = f'<html><head>{canonical}</head><body>{cards}{" " * 11000}</body></html>'
        self.assertEqual(len(tas.parse_cards(original.encode(), 1)), 5)
        for candidate in (
            original.replace(url, "https://forged.invalid/"),
            original.replace(canonical, ""),
            original.replace(canonical, canonical + canonical),
            original.replace(canonical, f'<link rel="canonical" href="{url}" href="https://forged.invalid/">'),
            original.replace(canonical, f'<link rel="canonical" rel="canonical" href="{url}">'),
        ):
            with self.subTest(candidate=candidate[:100]):
                with self.assertRaisesRegex(ValueError, "canonical publisher locator"):
                    tas.parse_cards(candidate.encode(), 1)

    def test_symlink_receipt_and_raw_inputs_are_rejected(self):
        root = self.fixture()
        victim = root / "outside.txt"
        victim.write_text("do not touch\n")
        target = root / tas.BASE / "s1.csv"
        target.unlink()
        target.symlink_to(victim)
        with patch.object(tas, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                tas.check()
        self.assertEqual(victim.read_text(), "do not touch\n")
        with self.assertRaisesRegex(ValueError, "symlink forbidden"):
            tas.safe.read_raw_response(target)

    def test_csv_rejects_duplicate_and_invalid_html_titles(self):
        baseline = tas.parse_csv((BASE / "s1.csv").read_bytes(), 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            tas.parse_csv(tas.csv_bytes(baseline[:1] + baseline[:1] + baseline[1:]), 1)
        with self.assertRaisesRegex(ValueError, "invalid TAS publisher title"):
            tas.parse_csv(tas.csv_bytes([(1, 1, "<script>")] + baseline[1:]), 1)


if __name__ == "__main__":
    unittest.main()
