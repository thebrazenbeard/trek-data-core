"""Adversarial tests for source-local multipart versus title-alias provenance."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b004 as mod  # noqa: E402


class EpisodeGuideB004Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = mod.read(mod.CATALOG)
        cls.observations, _ = mod.read(mod.OBS)
        cls.built = mod.compile_records(cls.catalog, cls.raw, cls.observations)

    def test_complete_bounded_16_case_17_card_honest_accounting(self):
        s = self.built["summary"]
        self.assertEqual(s["source_local_row_cases"], 16)
        self.assertEqual(s["actual_official_cards_read"], 17)
        self.assertEqual(s["exact_title_cases"], 14)
        self.assertEqual(s["unresolved_punctuation_alias_cases"], 1)
        self.assertEqual(s["unresolved_multipart_work_identity_cases"], 1)
        self.assertEqual(s["original_synopsis_drafts_pending_human_review"], 15)
        self.assertEqual(s["publicly_approved_synopses"], 0)
        self.assertEqual(s["pinned_raw_publisher_html_bodies"], 0)
        self.assertEqual(s["governed_work_or_evidence_admissions"], 0)
        for i, row in enumerate(self.built["rows"], start=35):
            self.assertEqual(row["source_local_row_id"], f"lead:{i:04d}")
            self.assertEqual(row["source_local_family"], "wikidata_collaborative_derivative")
            self.assertEqual(row["publisher_family"], "paramount_corporate_publisher_family")
            self.assertEqual(row["governed_research_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["public_synopsis_approval"], "NONE")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/"))
            for card in row["official_card_candidates"]:
                self.assertTrue(card["guide_url"].startswith("https://www.paramountplus.com/shows/"))
                self.assertIsNone(card["publisher_source_body_sha256"])
                self.assertTrue(card["brief_description_actually_read"])

    def test_hide_and_q_alias_is_not_promoted_to_exact(self):
        row = self.built["rows"][41 - 35]
        self.assertEqual(row["source_local_title"], "Hide and Q")
        self.assertEqual(row["official_card_candidates"][0]["title"], 'Hide and "Q"')
        self.assertEqual(row["title_resolution"], "PUNCTUATION_VARIANT_UNRESOLVED")
        self.assertEqual(row["original_synopsis_draft"] is not None, True)

    def test_chain_of_command_multipart_unresolved_no_synopsis(self):
        row = self.built["rows"][42 - 35]
        self.assertEqual(row["source_local_title"], "Chain of Command")
        self.assertEqual([(c["season"], c["episode"]) for c in row["official_card_candidates"]],
                         [(6, 10), (6, 11)])
        self.assertEqual(row["title_resolution"], "MULTIPART_SOURCE_LOCAL_TARGET_UNRESOLVED")
        self.assertIsNone(row["original_synopsis_draft"])
        self.assertEqual(row["synopsis_status"], "WITHHELD_MULTIPART_WORK_IDENTITY_UNRESOLVED")

    def test_forged_work_identity_and_false_title_match_rejected(self):
        mutations = (
            (0, "title_resolution", "EXACTLY_MATCHED"),
            (6, "title_resolution", "EXACT"),
            (7, "title_resolution", "EXACT"),
            (7, "original_synopsis_draft", "A fabricated invented narrative that is not in either part."),
            (7, "cards", [{"season":6,"episode":10,"official_title":"Chain Of Command - Part 1"}]),
            (1, "series", "TOS"),
            (0, "cards", [{"season":2,"episode":40,"official_title":"The Pirates of Orion"}]),
        )
        for index, key, value in mutations:
            with self.subTest(index=index, key=key):
                dirty = copy.deepcopy(self.observations)
                dirty["rows"][index][key] = value
                with self.assertRaises(ValueError):
                    mod.compile_records(self.catalog, self.raw, dirty)

    def test_false_raw_source_and_coverage_claims_rejected(self):
        dirty = copy.deepcopy(self.observations)
        dirty["source_raw_bytes_pinned"] = True
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, dirty)
        dirty = copy.deepcopy(self.observations)
        dirty["admission_effect"] = "EVIDENCE_ADMITTED"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, dirty)
        dirty = copy.deepcopy(self.catalog)
        dirty["rows"][35]["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            mod.compile_records(dirty, self.raw, self.observations)

    def test_derivative_matches_committed_bytes_even_python_optimized(self):
        expected = (json.dumps(self.built, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual(expected, (ROOT / mod.OUTPUT).read_bytes())
        for optimize in (False, True):
            cmd = [sys.executable]
            if optimize:
                cmd.append("-O")
            cmd.extend([str(ROOT / "tools" / "build_episode_guide_rechecks_b004.py"), "--check"])
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("16 source cases, 17 publisher cards", result.stdout)


if __name__ == "__main__":
    unittest.main()
