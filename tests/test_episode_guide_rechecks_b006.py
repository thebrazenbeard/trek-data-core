"""Adversarial Voyager B006 source-local publisher card checks."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b006 as mod  # noqa: E402


class VoyagerB006Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.catalog_raw = mod.load(mod.CATALOG)
        cls.obs, cls.obs_raw = mod.load(mod.OBS)
        cls.result = mod.compile_records(cls.catalog, cls.catalog_raw, cls.obs)

    def test_exact_13_voyager_rows_no_admission(self):
        summary = self.result["summary"]
        self.assertEqual(summary, {
            "source_local_row_cases": 13, "publisher_guide_cards_read": 13,
            "exact_title_cases": 11, "case_variant_unresolved": 1,
            "multipart_scope_unresolved": 1, "public_synopses_approved": 0,
            "raw_publisher_html_bodies_pinned": 0, "governed_source_or_work_admissions": 0,
        })
        for n, row in enumerate(self.result["rows"], start=70):
            self.assertEqual(row["source_local_row_id"], f"lead:{n:04d}")
            self.assertEqual(row["source_local_context"], "VOY")
            self.assertEqual(row["source_local_lineage"], "wikidata_collaborative_derivative")
            self.assertEqual(row["publisher_family"], "paramount_corporate_publisher_family")
            self.assertEqual(row["governed_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/Q"))
            card = row["official_card"]
            self.assertTrue(card["guide_url"].startswith("https://www.paramountplus.com/shows/star_trek_voyager/episodes/"))
            self.assertTrue(card["brief_description_actually_read"])
            self.assertIsNone(card["raw_webpage_sha256"])
            self.assertEqual(row["source_body_custody_status"], "NOT_READ_OR_HASHED")
            self.assertEqual(row["synopsis_publication_status"], "NOT_REQUESTED_OR_APPROVED")

    def test_explicit_variant_and_combined_card_hold(self):
        by_id = {row["source_local_row_id"]: row for row in self.result["rows"]}
        self.assertEqual(by_id["lead:0073"]["source_local_title"], "Time and Again")
        self.assertEqual(by_id["lead:0073"]["official_card"]["title"], "Time And Again")
        self.assertEqual(by_id["lead:0073"]["title_resolution"], "CASE_VARIANT_UNRESOLVED")
        self.assertEqual(by_id["lead:0074"]["source_local_title"], "Caretaker")
        self.assertEqual(by_id["lead:0074"]["official_card"]["title"], "Caretaker, Part 1 & 2")
        self.assertEqual(by_id["lead:0074"]["official_card"]["season"], 1)
        self.assertEqual(by_id["lead:0074"]["official_card"]["episode"], 1)
        self.assertEqual(by_id["lead:0074"]["title_resolution"], "MULTIPART_TITLE_SCOPE_UNRESOLVED")

    def test_reject_alias_promotion_and_swapped_slots(self):
        for index, field, value in (
            (3, "title_resolution", "EXACT"),
            (4, "title_resolution", "EXACT"),
            (4, "official_title", "Caretaker"),
            (0, "season", 6),
            (0, "episode", 20),
            (0, "official_title", "Virtuoso"),
            (0, "row_id", "lead:0071"),
            (0, "brief_description_read", False),
        ):
            altered = copy.deepcopy(self.obs)
            altered["rows"][index][field] = value
            with self.subTest(index=index, field=field), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.catalog_raw, altered)

    def test_reject_rights_custody_and_research_promotion(self):
        for field, value in (
            ("source_body_read", True), ("raw_webpage_bytes_available", True),
            ("public_synopsis_authorized", True), ("coverage_effect", "SOURCE_BOUND"),
            ("admission_effect", "ACCEPTED"), ("source_family", "wikidata:wdqs"),
        ):
            altered = copy.deepcopy(self.obs)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.catalog_raw, altered)

    def test_reject_unreviewed_envelope_or_media_text(self):
        for field, value in (
            ("proposal_id", "FAKE"),
            ("baseline_accepted_main", "0" * 40),
            ("observed_utc_date", "2026-10-03"),
            ("catalog_sha256", "0" * 64),
        ):
            altered = copy.deepcopy(self.obs)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.catalog_raw, altered)
        altered = copy.deepcopy(self.obs)
        altered["rows"][2]["recap"] = "unlicensed publisher text"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.catalog_raw, altered)
        altered = copy.deepcopy(self.obs)
        altered["rows"][2]["cover_url"] = "https://example.com/file.png"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.catalog_raw, altered)

    def test_reject_catalog_drift_even_with_rewritten_metadata(self):
        changed = copy.deepcopy(self.catalog)
        target = next(row for row in changed["rows"] if row["row_id"] == "lead:0070")
        target["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            mod.compile_records(changed, self.catalog_raw, self.obs)
        tampered_bytes = json.dumps(changed, sort_keys=True).encode("utf-8")
        with self.assertRaises(ValueError):
            mod.compile_records(changed, tampered_bytes, self.obs)

    def test_json_duplicate_keys_not_accepted(self):
        with self.assertRaises(ValueError):
            mod.unique_pairs([("admission_effect", "NONE"), ("admission_effect", "ACCEPTED")])

    def test_previous_b001_b005_ids_do_not_overlap(self):
        existing = json.loads((ROOT / "explorer/metadata-rechecks.json").read_text(encoding="utf-8"))
        previous = json.loads((ROOT / "proposals/verification/episode-guide-rechecks-b005-20261103/records.json").read_text(encoding="utf-8"))
        before = {row["row_id"] for row in existing["rows"]} | {row["source_local_row_id"] for row in previous["rows"]}
        current = {row["source_local_row_id"] for row in self.result["rows"]}
        self.assertTrue(before.isdisjoint(current))

    def test_derivative_is_deterministic_even_optimized(self):
        expected = (json.dumps(self.result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
        self.assertEqual(expected, (ROOT / mod.OUTPUT).read_bytes())
        for optimized in (False, True):
            cmd = [sys.executable] + (["-O"] if optimized else []) + [str(ROOT / "tools/build_episode_guide_rechecks_b006.py"), "--check"]
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("13 source-local cards", proc.stdout)


if __name__ == "__main__":
    unittest.main()
