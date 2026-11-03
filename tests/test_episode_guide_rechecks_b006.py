"""Adversarial checks for DS9/Voyager B006 official episode-guide triage."""

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


class EpisodeGuideB006Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = mod.read(mod.CATALOG)
        cls.observations, _ = mod.read(mod.OBS)
        cls.built = mod.compile_records(cls.catalog, cls.raw, cls.observations)

    def test_16_rows_primary_publisher_but_no_admitted_research(self):
        summary = self.built["summary"]
        for k, value in {
            "source_local_row_cases":16, "actual_official_cards_read":16,
            "exact_title_cases":13, "unresolved_case_variant_cases":2,
            "unresolved_combined_multipart_identity_cases":1,
            "original_synopsis_drafts_pending_human_review":15,
            "publicly_approved_synopses":0, "pinned_raw_publisher_html_bodies":0,
            "governed_work_or_evidence_admissions":0,
        }.items():
            self.assertEqual(summary[k], value, k)
        for index, row in enumerate(self.built["rows"], start=67):
            self.assertEqual(row["source_local_row_id"], f"lead:{index:04d}")
            self.assertEqual(row["source_local_series_context"], "DS9" if index <= 69 else "VOY")
            self.assertEqual(row["publisher_family"], "paramount_corporate_publisher_family")
            self.assertEqual(row["source_local_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["public_synopsis_approval"], "NONE")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/"))
            card = row["official_card_candidates"][0]
            self.assertTrue(card["guide_url"].startswith("https://www.paramountplus.com/shows/"))
            self.assertTrue(card["brief_description_actually_read"])
            self.assertIsNone(card["publisher_source_body_sha256"])

    def test_caretaker_combined_publisher_listing_does_not_resolve_work_identity(self):
        row = self.built["rows"][74-67]
        self.assertEqual(row["source_local_title"], "Caretaker")
        self.assertEqual(row["official_card_candidates"][0]["title"], "Caretaker, Part 1 & 2")
        self.assertEqual(row["official_card_candidates"][0]["season"], 1)
        self.assertEqual(row["official_card_candidates"][0]["episode"], 1)
        self.assertEqual(row["title_resolution"], "COMBINED_MULTIPART_LISTING_UNRESOLVED")
        self.assertEqual(row["synopsis_status"], "WITHHELD_COMBINED_MULTIPART_WORK_IDENTITY_UNRESOLVED")
        self.assertIsNone(row["original_synopsis_draft"])

    def test_case_variants_are_unresolved_and_not_exact(self):
        for row_id, official in mod.CASE_EXCEPTIONS.items():
            row = next(r for r in self.built["rows"] if r["source_local_row_id"] == row_id)
            self.assertEqual(row["title_resolution"], "CASE_VARIANT_UNRESOLVED")
            self.assertEqual(row["official_card_candidates"][0]["title"], official)
            self.assertNotEqual(row["source_local_title"], official)

    def test_false_slot_series_title_alias_and_synopsis_mutations_rejected(self):
        mutations = (
            (0,"series","VOY"),
            (1,"cards",[{"season":6,"episode":21,"official_title":"His Way"}]),
            (2,"title_resolution","EXACT"),
            (6,"title_resolution","EXACT"),
            (7,"title_resolution","EXACT"),
            (7,"cards",[{"season":1,"episode":1,"official_title":"Caretaker"}]),
            (7,"original_synopsis_draft","A made-up resolution to a combined multipart identity."),
            (13,"cards",[{"season":1,"episode":26,"official_title":"Jetrel"}]),
        )
        for index, key, value in mutations:
            with self.subTest(index=index,key=key):
                dirty = copy.deepcopy(self.observations)
                dirty["rows"][index][key] = value
                with self.assertRaises(ValueError):
                    mod.compile_records(self.catalog, self.raw, dirty)

    def test_forged_custody_coverage_duplicate_and_source_lineage_rejected(self):
        dirty = copy.deepcopy(self.observations)
        dirty["source_raw_bytes_pinned"] = True
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog,self.raw,dirty)
        dirty = copy.deepcopy(self.observations)
        dirty["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog,self.raw,dirty)
        dirty = copy.deepcopy(self.observations)
        dirty["rows"][1]["row_id"] = dirty["rows"][0]["row_id"]
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog,self.raw,dirty)
        dirty = copy.deepcopy(self.catalog)
        dirty["rows"][67]["source_group"] = "paramount:unverified"
        with self.assertRaises(ValueError):
            mod.compile_records(dirty,self.raw,self.observations)

    def test_derivative_reproducible_python_optimized_and_unoptimized(self):
        expected = (json.dumps(self.built,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
        self.assertEqual(expected,(ROOT/mod.OUTPUT).read_bytes())
        for optimized in (False,True):
            cmd=[sys.executable]
            if optimized:
                cmd.append("-O")
            cmd.extend([str(ROOT/"tools"/"build_episode_guide_rechecks_b006.py"),"--check"])
            proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr or proc.stdout)
            self.assertIn("16 DS9/VOY guide cards",proc.stdout)


if __name__ == "__main__":
    unittest.main()
