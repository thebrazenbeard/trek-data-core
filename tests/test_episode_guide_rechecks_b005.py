"""Adversarial B005 checks: publisher-description misassociation and case variants."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b005 as mod  # noqa: E402


class EpisodeGuideB005Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = mod.read(mod.CATALOG)
        cls.observations, _ = mod.read(mod.OBS)
        cls.built = mod.compile_records(cls.catalog, cls.raw, cls.observations)

    def test_all_16_source_local_ids_and_statuses_without_admission(self):
        summary = self.built["summary"]
        self.assertEqual(summary["source_local_row_cases"], 16)
        self.assertEqual(summary["actual_official_cards_read"], 16)
        self.assertEqual(summary["exact_title_cases"], 14)
        self.assertEqual(summary["unresolved_case_variant_cases"], 2)
        self.assertEqual(summary["unresolved_publisher_description_conflict_cases"], 1)
        self.assertEqual(summary["original_synopsis_drafts_pending_human_review"], 15)
        self.assertEqual(summary["publicly_approved_synopses"], 0)
        self.assertEqual(summary["pinned_raw_publisher_html_bodies"], 0)
        self.assertEqual(summary["governed_work_or_evidence_admissions"], 0)
        for index, row in enumerate(self.built["rows"], start=51):
            self.assertEqual(row["source_local_row_id"], f"lead:{index:04d}")
            self.assertEqual(row["source_local_series_context"], "DS9")
            self.assertEqual(row["source_local_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["publisher_family"], "paramount_corporate_publisher_family")
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["public_synopsis_approval"], "NONE")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/"))
            card = row["official_card_candidates"][0]
            self.assertTrue(card["guide_url"].startswith("https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/"))
            self.assertIsNone(card["publisher_source_body_sha256"])
            self.assertTrue(card["brief_description_actually_read"])

    def test_publisher_swapped_description_the_visitor_no_synopsis(self):
        row = self.built["rows"][54 - 51]
        self.assertEqual(row["source_local_title"], "The Visitor")
        self.assertEqual(row["official_card_candidates"][0]["season"], 4)
        self.assertEqual(row["official_card_candidates"][0]["episode"], 3)
        self.assertEqual(row["publisher_brief_description_state"], "PUBLISHER_DESCRIPTION_SLOT_CONFLICT_UNRESOLVED")
        self.assertIsNone(row["original_synopsis_draft"])
        self.assertEqual(row["synopsis_status"], "WITHHELD_PUBLISHER_DESCRIPTION_MISASSOCIATED")

    def test_title_case_variants_do_not_become_exact(self):
        for row_id, official_title in mod.TITLE_CASE_EXCEPTIONS.items():
            row = next(r for r in self.built["rows"] if r["source_local_row_id"] == row_id)
            self.assertEqual(row["title_resolution"], "CASE_VARIANT_UNRESOLVED")
            self.assertEqual(row["official_card_candidates"][0]["title"], official_title)
            self.assertNotEqual(row["source_local_title"], official_title)

    def test_reject_false_title_slot_alias_promotion_and_synopsis_release(self):
        mutations = (
            (0, "title_resolution", "CASE_VARIANT_UNRESOLVED"),
            (1, "title_resolution", "EXACT"),
            (8, "title_resolution", "EXACT"),
            (3, "original_synopsis_draft", "This is an entirely fabricated summary about a different episode."),
            (3, "publisher_brief_description_state", "READ_CARD_DESCRIPTION_CONSISTENT"),
            (1, "cards", [{"season": 4, "episode": 13, "official_title": "Return To Grace"}]),
            (0, "cards", [{"season": 4, "episode": 40, "official_title": "Paradise Lost"}]),
            (0, "series", "TNG"),
        )
        for index, key, value in mutations:
            with self.subTest(index=index, key=key):
                altered = copy.deepcopy(self.observations)
                altered["rows"][index][key] = value
                with self.assertRaises(ValueError):
                    mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_unsafe_inputs_and_false_coverage(self):
        dirty = copy.deepcopy(self.observations)
        dirty["source_raw_bytes_pinned"] = True
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, dirty)
        dirty = copy.deepcopy(self.observations)
        dirty["admission_effect"] = "WORK_ADMITTED"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, dirty)
        dirty = copy.deepcopy(self.observations)
        dirty["rows"][1]["row_id"] = dirty["rows"][0]["row_id"]
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, dirty)
        dirty = copy.deepcopy(self.catalog)
        dirty["rows"][51]["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            mod.compile_records(dirty, self.raw, self.observations)

    def test_exact_deterministic_derivative_even_optimized_python(self):
        expected = (json.dumps(self.built, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual(expected, (ROOT / mod.OUTPUT).read_bytes())
        for optimize in (False, True):
            command = [sys.executable]
            if optimize:
                command.append("-O")
            command.extend([str(ROOT / "tools" / "build_episode_guide_rechecks_b005.py"), "--check"])
            proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertIn("16 DS9 official publisher cards", proc.stdout)


if __name__ == "__main__":
    unittest.main()
