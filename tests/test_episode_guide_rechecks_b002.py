"""Hostile controls: official guide cards must never elevate source-local coverage."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b002 as subject  # noqa: E402


class RenderedOfficialGuideBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = subject.read(subject.SOURCE)
        cls.observations, _ = subject.read(subject.OBS)
        cls.result = subject.compile_observations(cls.catalog, cls.raw, cls.observations)

    def test_sixteen_actual_rendered_card_observations_without_custody_or_coverage(self):
        self.assertEqual(self.result["summary"]["source_local_card_observations"], 16)
        self.assertEqual(self.result["summary"]["exact_official_title_matches"], 15)
        self.assertEqual(self.result["summary"]["unresolved_title_variants"], 1)
        self.assertEqual(self.result["summary"]["publicly_approved_synopses"], 0)
        self.assertEqual(self.result["summary"]["raw_page_bodies_byte_pinned"], 0)
        self.assertEqual(self.result["summary"]["governed_works_evidence_admitted"], 0)
        self.assertEqual(self.result["summary"]["unrechecked_rows_in_full_1214_directory_before_this_batch"], 1206)
        for i, row in enumerate(self.result["rows"], start=3):
            self.assertEqual(row["source_local_row_id"], f"lead:{i:04d}")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/"))
            self.assertEqual(row["source_local_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["official_guide_family"], "paramount_corporate_publisher_family")
            self.assertEqual(row["observed_guide_series_label"], "Star Trek")
            self.assertEqual(row["source_local_series_context"], "TOS")
            self.assertTrue(row["official_guide_url"].startswith("https://www.paramountplus.com/shows/star_trek/episodes/"))
            self.assertTrue(row["publisher_brief_description_read"])
            self.assertIsNone(row["raw_source_sha256"])
            self.assertEqual(row["human_review"], "PENDING")
            self.assertEqual(row["synopsis_state"], "ORIGINAL_PARAPHRASE_DRAFT_NOT_PUBLICATION_APPROVED")
            self.assertEqual(row["source_local_discovery_state"], "CATALOGUED_METADATA_ONLY")
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")

    def test_charlie_x_punctuation_is_an_unresolved_mismatch_not_a_silent_match(self):
        variant = next(r for r in self.result["rows"] if r["source_local_row_id"] == "lead:0006")
        self.assertEqual(variant["source_local_title"], "Charlie X")
        self.assertEqual(variant["observed_official_title"], 'Charlie "X"')
        self.assertEqual(variant["title_check"], "SOURCE_TITLE_VARIANT_REQUIRES_RECONCILIATION")
        self.assertEqual(variant["observed_episode"], 3)
        self.assertEqual(variant["observed_season"], 1)

    def test_forged_titles_slots_and_summaries_rejected(self):
        for key, value in (("official_title", "Alien New Title"),
                           ("guide_season", 9), ("guide_episode", 0),
                           ("guide_episode", 26), ("original_synopsis_draft", "Invented."),
                           ("title_match", "EXACT_TRUE_BY_INFERENCE"),
                           ("source_body_sha256", "0" * 64)):
            with self.subTest(key=key, value=value):
                declared = copy.deepcopy(self.observations)
                declared["observations"][0][key] = value
                with self.assertRaises(ValueError):
                    subject.compile_observations(self.catalog, self.raw, declared)

    def test_cross_row_collisions_and_false_synopsis_approval_rejected(self):
        declared = copy.deepcopy(self.observations)
        declared["observations"][1]["guide_season"] = 1
        declared["observations"][1]["guide_episode"] = 2
        with self.assertRaises(ValueError):
            subject.compile_observations(self.catalog, self.raw, declared)
        declared = copy.deepcopy(self.observations)
        declared["human_review"] = "APPROVED"
        with self.assertRaises(ValueError):
            subject.compile_observations(self.catalog, self.raw, declared)
        declared = copy.deepcopy(self.observations)
        declared["raw_source_bytes_pinned"] = True
        with self.assertRaises(ValueError):
            subject.compile_observations(self.catalog, self.raw, declared)

    def test_mutating_accepted_row_or_its_coverage_requires_new_review(self):
        for key, value in (("title", "Invented discovery title"),
                           ("source_group", "publisher:paramount"),
                           ("coverage_effect", "CLOSE_READ"),
                           ("verification_status", "SOURCE_BOUND")):
            with self.subTest(key=key):
                catalog = copy.deepcopy(self.catalog)
                catalog["rows"][3][key] = value
                with self.assertRaises(ValueError):
                    subject.compile_observations(catalog, self.raw, self.observations)

    def test_committed_derivative_check_normal_and_optimized(self):
        expected = (json.dumps(self.result, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual((ROOT / subject.OUT).read_bytes(), expected)
        for optimized in (False, True):
            command = [sys.executable]
            if optimized:
                command.append("-O")
            command += [str(ROOT / "tools" / "build_episode_guide_rechecks_b002.py"), "--check"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("16 rendered official", result.stdout)


if __name__ == "__main__":
    unittest.main()
