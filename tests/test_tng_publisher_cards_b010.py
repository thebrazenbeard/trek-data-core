"""Fail-closed guards for held TNG first-party publisher-card observations."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_tng_publisher_cards_b010.py"
SPEC = importlib.util.spec_from_file_location("tng_b010_compiler", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TNGPublisherCardsB010Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = MOD.load_json(MOD.CATALOG)
        cls.observations, _ = MOD.load_json(MOD.OBSERVATIONS)

    def reject(self, operation):
        mutated = copy.deepcopy(self.observations)
        operation(mutated)
        with self.assertRaises(ValueError):
            MOD.compile_records(self.catalog, self.raw, mutated)

    def test_rechecked_exactly_distinct_tng_frontier_without_b004_overlap(self):
        records = MOD.compile_records(self.catalog, self.raw, self.observations)
        self.assertEqual(records["source_local_rows_rechecked"], 10)
        self.assertEqual(records["combined_multipart_identity_holds"], 1)
        self.assertEqual(records["original_synopsis_drafts_held"], 10)
        self.assertEqual(records["publisher_artwork_url_leads_held"], 10)
        self.assertEqual(records["public_synopses_or_images_published"], 0)
        self.assertEqual(records["governed_research_admissions"], 0)
        self.assertEqual([r["source_local_row_id"] for r in records["rows"]],
                         [f"legacy:s1:tng:{i:03d}" for i in (0, 1, 2, 3, 4, 5, 6, 7, 9, 10)])
        self.assertEqual(len({r["publisher_card"]["episode"] for r in records["rows"]}), 10)
        self.assertTrue(all(r["admission_effect"] == r["coverage_effect"] == "NONE"
                            and r["synopsis_publication_status"] == "PENDING_HUMAN_AND_EDITORIAL_REVIEW"
                            and r["publisher_card"]["raw_webpage_sha256"] is None
                            for r in records["rows"]))

    def test_false_promotion_of_admission_or_publication(self):
        self.reject(lambda x: x.update(coverage_effect="CLOSE_READ"))
        self.reject(lambda x: x.update(admission_effect="ADMITTED"))
        self.reject(lambda x: x.update(public_synopsis_authorized=True))
        self.reject(lambda x: x.update(artwork_copy_or_publication_authorized=True))

    def test_false_av_source_and_custody_claims(self):
        self.reject(lambda x: x.update(audiovisual_episodes_watched=True))
        self.reject(lambda x: x.update(raw_html_bytes_archived=True))
        self.reject(lambda x: x.update(read_surface="FULL_EPISODE_TRANSCRIPT"))

    def test_source_identity_and_ordinal_not_guessed_or_collapsed(self):
        self.reject(lambda x: x["rows"][0].update(row_id="legacy:s1:tng:001"))
        self.reject(lambda x: x["rows"][0].update(episode=2))
        self.reject(lambda x: x["rows"][2].update(publisher_title="Code Of Honor"))
        self.reject(lambda x: x["rows"][2].update(episode=5))
        self.reject(lambda x: x["rows"][0].update(identity_hold="TWO_SEPARATE_WORKS"))

    def test_source_fingerprints_and_held_artwork_are_not_invented(self):
        self.reject(lambda x: x["rows"][1].update(publisher_description_sha256="0" * 64))
        self.reject(lambda x: x["rows"][1].update(publisher_thumbnail_url="https://evil.test/thumb.jpg"))
        self.reject(lambda x: x["rows"][1].update(publisher_thumbnail_url="http://thumbnails.cbsig.net/a.jpg"))
        self.reject(lambda x: x["rows"][1].update(original_synopsis_draft="TODO"))

    def test_cross_series_catalog_contamination_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        for row in catalog["rows"]:
            if row["row_id"] == "legacy:s1:tng:005":
                row["context"] = "TOS S1E7"
                break
        with self.assertRaises(ValueError):
            MOD.compile_records(catalog, self.raw, self.observations)

    def test_duplicate_json_keys_refused(self):
        with self.assertRaises(ValueError):
            json.loads('{"row_id":"a","row_id":"b"}', object_pairs_hook=MOD.unique_pairs)

    def test_generated_records_exact_check(self):
        process = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT,
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)


if __name__ == "__main__":
    unittest.main()
