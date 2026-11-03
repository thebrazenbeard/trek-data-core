"""Adversarial B008 Enterprise source-relative publisher-card checks."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_episode_guide_rechecks_b008_ent as mod  # noqa: E402


class EnterpriseB008Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = mod.load(mod.CATALOG)
        cls.obs, _ = mod.load(mod.SOURCE)
        cls.derived = mod.compile_records(cls.catalog, cls.raw, cls.obs)

    def test_exact_nine_enterprise_records_without_work_admission(self):
        self.assertEqual(self.derived["summary"], {
            "source_local_rows_rechecked": 9,
            "literal_title_card_matches": 9,
            "part_numeral_variants_unresolved": 0,
            "original_drafts_pending_review": 9,
            "public_synopses_approved": 0,
            "raw_publisher_html_bodies_pinned": 0,
            "governed_source_or_work_admissions": 0,
        })
        for index, row in enumerate(self.derived["rows"], start=90):
            self.assertEqual(row["source_local_row_id"], f"lead:{index:04d}")
            self.assertEqual(row["source_local_context"], "ENT")
            self.assertEqual(row["source_local_lineage"], "wikidata_collaborative_derivative")
            self.assertTrue(row["source_local_locator"].startswith("https://www.wikidata.org/wiki/Q"))
            self.assertTrue(row["official_card"]["guide_url"].startswith("https://www.paramountplus.com/shows/enterprise/episodes/"))
            self.assertTrue(row["official_card"]["brief_description_actually_read"])
            self.assertIsNone(row["official_card"]["raw_webpage_sha256"])
            self.assertEqual(row["title_resolution"], "EXACT_OFFICIAL_CARD_TITLE")
            self.assertTrue(row["original_synopsis_draft"])
            self.assertEqual(row["synopsis_publication_status"], "HUMAN_AND_EDITORIAL_REVIEW_PENDING")
            self.assertEqual(row["source_body_custody_status"], "NOT_READ_OR_HASHED")
            self.assertEqual(row["governed_coverage_state"], "NOT_ADMITTED")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")

    def test_accepted_voyager_b007_is_disjoint(self):
        voyager = json.loads((ROOT / "proposals/librarian/voy-b007-source-card-20261103/records.json").read_text(encoding="utf-8"))
        accepted = {row["row_id"] for row in voyager["candidate_rows"]}
        current = {row["source_local_row_id"] for row in self.derived["rows"]}
        self.assertEqual(accepted, {f"lead:{i:04d}" for i in range(83, 90)})
        self.assertTrue(accepted.isdisjoint(current))

    def test_reject_metadata_or_source_custody_promotion(self):
        for key, value in (
            ("admission_effect", "ACCEPTED"),
            ("coverage_effect", "SOURCE_BOUND"),
            ("public_synopsis_authorized", True),
            ("raw_webpage_bytes_custodied", True),
            ("episode_video_or_transcript_read", True),
            ("source_family", "two_independent_publishers"),
            ("read_surface", "FULL_EPISODES"),
        ):
            altered = copy.deepcopy(self.obs)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_swapped_slots_and_forged_aliases(self):
        for index, key, value in (
            (0, "official_card_title", "Bounty"),
            (0, "row_id", "lead:0089"),
            (0, "season", 3),
            (0, "episode", 25),
            (0, "official_card_description_read", False),
            (0, "title_resolution", "PART_NUMERAL_STYLE_UNRESOLVED"),
            (0, "original_synopsis_draft", None),
        ):
            altered = copy.deepcopy(self.obs)
            altered["rows"][index][key] = value
            with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.raw, altered)

    def test_reject_unreviewed_media_or_corpus_effect(self):
        altered = copy.deepcopy(self.obs)
        altered["rows"][0]["copied_publisher_synopsis"] = "unlicensed text"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)
        altered = copy.deepcopy(self.obs)
        altered["rows"][0]["original_synopsis_draft"] = "https://unauthorized.example/clip"
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)
        altered = copy.deepcopy(self.obs)
        altered["catalog_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.compile_records(self.catalog, self.raw, altered)

    def test_source_fidelity_reviewer_corrections_are_pinned(self):
        by_id = {r["source_local_row_id"]: r for r in self.derived["rows"]}
        self.assertEqual({k: by_id[k]["original_synopsis_draft"] for k in mod.SOURCE_FIDELITY_GUARDS}, mod.SOURCE_FIDELITY_GUARDS)
        prior_unsupported = (
            ("lead:0090", "recalls an earlier period in his career"),
            ("lead:0093", "identify Earth's attackers"),
            ("lead:0095", "questioning the accusations"),
            ("lead:0096", "persecution over the actions of others"),
            ("lead:0098", "distortions repeatedly strike"),
        )
        for row_id, prohibited in prior_unsupported:
            self.assertNotIn(prohibited, by_id[row_id]["original_synopsis_draft"])
            altered = copy.deepcopy(self.obs)
            entry = next(r for r in altered["rows"] if r["row_id"] == row_id)
            entry["original_synopsis_draft"] += " " + prohibited
            with self.subTest(row_id=row_id), self.assertRaises(ValueError):
                mod.compile_records(self.catalog, self.raw, altered)
    def test_reject_source_catalog_drift_and_duplicate_json_keys(self):
        altered = copy.deepcopy(self.catalog)
        altered["rows"][90]["verification_status"] = "SOURCE_BOUND"
        with self.assertRaises(ValueError):
            mod.compile_records(altered, self.raw, self.obs)
        with self.assertRaises(ValueError):
            mod.compile_records(altered, json.dumps(altered).encode(), self.obs)
        with self.assertRaises(ValueError):
            mod.unique_keys([("source_kind", "a"), ("source_kind", "b")])

    def test_byte_identical_derivative_under_normal_and_optimized_python(self):
        expected = (json.dumps(self.derived, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
        self.assertEqual(expected, (ROOT / mod.OUTPUT).read_bytes())
        for optimized in (False, True):
            command = [sys.executable] + (["-O"] if optimized else []) + [str(ROOT / "tools/build_episode_guide_rechecks_b008_ent.py"), "--check"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
