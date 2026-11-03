"""Adversarial B007 Voyager/Enterprise held source-local guide-card tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b007 as mod  # noqa: E402


class EpisodeGuideB007Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = mod.load(mod.CATALOG)
        cls.observations, _ = mod.load(mod.SOURCE)
        cls.derived = mod.compile_records(cls.catalog, cls.raw, cls.observations)

    def test_exact_16_source_local_rows_without_work_admission(self):
        self.assertEqual(self.derived["summary"], {
            "source_local_rows_rechecked": 16,
            "literal_title_card_matches": 13,
            "part_numeral_variants_unresolved": 3,
            "original_drafts_pending_review": 13,
            "public_synopses_approved": 0,
            "raw_publisher_html_bodies_pinned": 0,
            "governed_source_or_work_admissions": 0,
        })
        self.assertEqual(self.derived["admission_effect"], "NONE")
        self.assertEqual(self.derived["coverage_effect"], "NONE")
        for index, record in enumerate(self.derived["rows"], start=83):
            self.assertEqual(record["source_local_row_id"], f"lead:{index:04d}")
            self.assertEqual(record["source_local_lineage"], "wikidata_collaborative_derivative")
            self.assertTrue(record["source_local_locator"].startswith("https://www.wikidata.org/wiki/Q"))
            self.assertTrue(record["official_card"]["guide_url"].startswith("https://www.paramountplus.com/shows/"))
            self.assertTrue(record["official_card"]["brief_description_actually_read"])
            self.assertIsNone(record["official_card"]["raw_webpage_sha256"])
            self.assertEqual(record["source_body_custody_status"], "NOT_READ_OR_HASHED")
            self.assertEqual(record["governed_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(record["admission_effect"], "NONE")
            self.assertEqual(record["coverage_effect"], "NONE")

    def test_three_part_numeral_variants_remain_held_without_synopses(self):
        by_id = {row["source_local_row_id"]: row for row in self.derived["rows"]}
        for id_, wikidata, official in (
            ("lead:0087", "Basics, Part II", "Basics, Part 2"),
            ("lead:0088", "Future's End, Part II", "Future's End, Part 2"),
            ("lead:0089", "Year of Hell, Part II", "Year Of Hell, Part 2"),
        ):
            row = by_id[id_]
            self.assertEqual(row["source_local_title"], wikidata)
            self.assertEqual(row["official_card"]["title"], official)
            self.assertEqual(row["title_resolution"], "PART_NUMERAL_STYLE_UNRESOLVED")
            self.assertIsNone(row["original_synopsis_draft"])
            self.assertEqual(row["synopsis_publication_status"], "HOLD_SOURCE_IDENTITY")

    def test_original_synopses_are_held_for_editorial_review(self):
        exact = [row for row in self.derived["rows"] if row["title_resolution"] == "EXACT_OFFICIAL_CARD_TITLE"]
        self.assertEqual(len(exact), 13)
        for row in exact:
            self.assertGreater(len(row["original_synopsis_draft"]), 35)
            self.assertEqual(row["synopsis_publication_status"], "HUMAN_AND_EDITORIAL_REVIEW_PENDING")

    def test_reject_effect_or_source_custody_promotion(self):
        for key, value in (
            ("admission_effect", "SOURCE_BOUND"),
            ("coverage_effect", "CLOSE_READ"),
            ("public_synopsis_authorized", True),
            ("raw_webpage_bytes_custodied", True),
            ("episode_video_or_transcript_read", True),
            ("read_surface", "FULL_TRANSCRIPT"),
            ("catalog_sha256", "0" * 64),
            ("source_family", "independent_corroboration"),
        ):
            altered = copy.deepcopy(self.observations)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_swapped_title_slot_or_unresolved_synopsis(self):
        for index, key, value in (
            (0, "official_card_title", "Infinite Regress"),
            (0, "season", 4),
            (0, "episode", 22),
            (0, "row_id", "lead:0084"),
            (0, "official_card_description_read", False),
            (4, "title_resolution", "EXACT_OFFICIAL_CARD_TITLE"),
            (4, "original_synopsis_draft", "Publish this unsupported synopsis anyway."),
            (6, "official_card_title", "Year of Hell, Part II"),
        ):
            altered = copy.deepcopy(self.observations)
            altered["rows"][index][key] = value
            with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_extra_rights_artifact_or_false_review(self):
        altered = copy.deepcopy(self.observations)
        altered["rows"][0]["poster_bytes"] = "fake"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)
        altered = copy.deepcopy(self.observations)
        altered["rows"][0]["original_synopsis_draft"] = "https://publisher.example/clip"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)
        altered = copy.deepcopy(self.observations)
        altered["rows"][0]["original_synopsis_draft"] = "too short"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_catalog_drift_and_duplicate_json_keys(self):
        corrupted = copy.deepcopy(self.catalog)
        corrupted["rows"][83]["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            mod.compile_records(corrupted, self.raw, self.observations)
        with self.assertRaises(ValueError):
            mod.compile_records(corrupted, json.dumps(corrupted).encode(), self.observations)
        with self.assertRaises(ValueError):
            mod.unique_keys([("episode", 1), ("episode", 2)])

    def test_no_overlap_accepted_earlier_lanes(self):
        expected = {f"lead:{n:04d}" for n in range(83, 99)}
        old = set()
        for path in ROOT.glob("proposals/verification/episode-guide-rechecks-b00*/records.json"):
            if "b007-" in path.as_posix():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            old.update(row["source_local_row_id"] for row in data["rows"])
        self.assertTrue(old.isdisjoint(expected))

    def test_deterministic_derivative_under_normal_and_optimized_python(self):
        expected = (json.dumps(self.derived, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
        self.assertEqual(expected, (ROOT / mod.OUTPUT).read_bytes())
        for optimized in (False, True):
            command = [sys.executable] + (["-O"] if optimized else []) + [str(ROOT / "tools/build_episode_guide_rechecks_b007.py"), "--check"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
