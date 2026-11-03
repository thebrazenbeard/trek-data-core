"""Hostile checks for sixteen official rendered TOS/TAS source-local card observations."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b003 as module  # noqa: E402


class EpisodeGuideB003Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw_catalog = module.read(module.CATALOG)
        cls.source, _ = module.read(module.OBS)
        cls.derived = module.compile_records(cls.catalog, cls.raw_catalog, cls.source)

    def test_mixed_series_sixteen_cards_and_no_governed_coverage(self):
        summary = self.derived["summary"]
        self.assertEqual(summary["source_local_records_checked_from_rendered_guides"], 16)
        self.assertEqual(summary["tos_cards"], 1)
        self.assertEqual(summary["tas_cards"], 15)
        self.assertEqual(summary["official_title_exact_matches"], 15)
        self.assertEqual(summary["unresolved_case_variant"], 1)
        self.assertEqual(summary["original_synopsis_drafts_pending_human_review"], 16)
        self.assertEqual(summary["public_synopses_approved"], 0)
        self.assertEqual(summary["raw_page_bodies_byte_pinned"], 0)
        self.assertEqual(summary["governed_evidence_or_works_admitted"], 0)
        for number, row in enumerate(self.derived["rows"], start=19):
            self.assertEqual(row["source_local_row_id"], f"lead:{number:04d}")
            self.assertEqual(row["source_local_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["official_provenance_family"], "paramount_corporate_publisher_family")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/"))
            self.assertTrue(row["official_guide_url"].startswith("https://www.paramountplus.com/shows/"))
            self.assertTrue(row["publisher_brief_description_actually_read"])
            self.assertIsNone(row["raw_page_body_sha256"])
            self.assertEqual(row["public_synopsis_approval"], "NONE")
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["source_local_discovery_state"], "CATALOGUED_METADATA_ONLY")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")

    def test_case_variant_preserved_and_never_exact(self):
        row = next(r for r in self.derived["rows"] if r["source_local_row_id"] == "lead:0029")
        self.assertEqual(row["source_local_title"], "One of Our Planets Is Missing")
        self.assertEqual(row["observed_title"], "One of Our Planets is Missing")
        self.assertEqual(row["title_check"], "UNRESOLVED_CASE_VARIANT")

    def test_episode_slot_bounds_include_official_tos_s1_episode_30(self):
        self.assertTrue(module.valid_official_slot("TOS", 1, 30))
        self.assertFalse(module.valid_official_slot("TOS", 1, 31))
        self.assertTrue(module.valid_official_slot("TAS", 1, 16))
        self.assertFalse(module.valid_official_slot("TAS", 1, 17))
        self.assertTrue(module.valid_official_slot("TAS", 2, 6))
        self.assertFalse(module.valid_official_slot("TAS", 2, 7))
        self.assertFalse(module.valid_official_slot("TAS", True, 1))

    def test_invalid_title_slot_or_summary_rejected(self):
        for key, value in (("official_title", "Malicious replacement"),
                           ("title_check", "FORCE_MATCH"),
                           ("season", 9), ("episode", 32),
                           ("series", "TNG"), ("original_synopsis_draft", "New."),
                           ("raw_page_body_sha256", "a" * 64)):
            with self.subTest(key=key, value=value):
                bad = copy.deepcopy(self.source)
                bad["rows"][0][key] = value
                with self.assertRaises(ValueError):
                    module.compile_records(self.catalog, self.raw_catalog, bad)

    def test_collisions_and_forged_research_promotion_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["rows"][2]["episode"] = bad["rows"][1]["episode"]
        with self.assertRaises(ValueError):
            module.compile_records(self.catalog, self.raw_catalog, bad)
        bad = copy.deepcopy(self.source)
        bad["raw_publisher_source_bytes_pinned"] = True
        with self.assertRaises(ValueError):
            module.compile_records(self.catalog, self.raw_catalog, bad)
        bad = copy.deepcopy(self.source)
        bad["admission_effect"] = "WORK_ADMITTED"
        with self.assertRaises(ValueError):
            module.compile_records(self.catalog, self.raw_catalog, bad)
        catalog = copy.deepcopy(self.catalog)
        catalog["rows"][20]["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            module.compile_records(catalog, self.raw_catalog, self.source)

    def test_deterministic_derivative_normal_and_optimized(self):
        expected = (json.dumps(self.derived, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual(expected, (ROOT / module.OUT).read_bytes())
        for optimized in (False, True):
            args = [sys.executable]
            if optimized:
                args += ["-O"]
            args += [str(ROOT / "tools" / "build_episode_guide_rechecks_b003.py"), "--check"]
            proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertIn("16 TOS/TAS cards", proc.stdout)


if __name__ == "__main__":
    unittest.main()
