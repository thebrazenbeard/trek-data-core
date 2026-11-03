"""Adversarial exact-card tests for held TNG S1E13-E22 publisher observations."""

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/build_tng_publisher_cards_b011.py"
SPEC = importlib.util.spec_from_file_location("tng_b011_compiler", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class TNGPublisherCardsB011Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.raw = MOD.load_json(MOD.CATALOG)
        cls.observations, _ = MOD.load_json(MOD.OBSERVATIONS)

    def reject(self, mutation):
        copy_of_source = copy.deepcopy(self.observations)
        mutation(copy_of_source)
        with self.assertRaises(ValueError):
            MOD.compile_records(self.catalog, self.raw, copy_of_source)

    def test_ten_new_distinct_publisher_cards_no_accepted_b010_overlap(self):
        out = MOD.compile_records(self.catalog, self.raw, self.observations)
        self.assertEqual(out["source_local_rows_rechecked"], 10)
        self.assertEqual(out["publisher_card_slots_read"], 10)
        self.assertEqual(out["original_synopsis_drafts_held"], 10)
        self.assertEqual(out["publisher_artwork_url_leads_held"], 10)
        self.assertEqual(out["combined_multipart_identity_holds"], 0)
        self.assertEqual(out["public_synopses_or_images_published"], 0)
        self.assertEqual(out["governed_research_admissions"], 0)
        ids = [row["source_local_row_id"] for row in out["rows"]]
        self.assertEqual(ids, [f"legacy:s1:tng:{i:03d}" for i in range(11, 21)])
        self.assertFalse(set(ids) & {
            f"legacy:s1:tng:{i:03d}" for i in (0, 1, 2, 3, 4, 5, 6, 7, 9, 10)
        })
        self.assertEqual([r["publisher_card"]["episode"] for r in out["rows"]],
                         list(range(13, 23)))
        self.assertTrue(all(r["publisher_card"]["raw_webpage_sha256"] is None
                            and r["identity_resolution"] == "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
                            and r["coverage_effect"] == "NONE"
                            and r["admission_effect"] == "NONE"
                            and r["synopsis_publication_status"] == "PENDING_HUMAN_AND_EDITORIAL_REVIEW"
                            for r in out["rows"]))

    def test_unapproved_media_synopsis_source_or_coverage_effects_rejected(self):
        for key, value in (
            ("raw_html_bytes_archived", True),
            ("audiovisual_episodes_watched", True),
            ("public_synopsis_authorized", True),
            ("artwork_copy_or_publication_authorized", True),
            ("coverage_effect", "CLOSE_READ"),
            ("admission_effect", "ADMITTED"),
        ):
            with self.subTest(key=key):
                self.reject(lambda o: o.__setitem__(key, value))

    def test_title_slot_description_fingerprint_or_source_row_swap_rejected(self):
        self.reject(lambda o: o["rows"][0].update(row_id="legacy:s1:tng:010"))
        self.reject(lambda o: o["rows"][1].update(episode=13))
        self.reject(lambda o: o["rows"][2].update(publisher_title="11000101"))
        self.reject(lambda o: o["rows"][4].update(publisher_description_sha256="a" * 64))
        self.reject(lambda o: o["rows"][7].update(identity_hold="CANONICAL_WORK_RESOLVED"))

    def test_same_host_wrong_card_artwork_fails_even_if_url_shape_valid(self):
        self.reject(lambda o: o["rows"][0].update(
            publisher_thumbnail_url=o["rows"][1]["publisher_thumbnail_url"]))
        self.reject(lambda o: o["rows"][5].update(
            publisher_thumbnail_url=o["rows"][9]["publisher_thumbnail_url"]))
        self.reject(lambda o: o["rows"][7].update(
            publisher_thumbnail_url=o["rows"][6]["publisher_thumbnail_url"]))

    def test_nonsource_character_alias_or_unsupported_mentions_fail(self):
        self.reject(lambda o: o["rows"][1].update(
            entity_mentions_source_relative=["Riker", "Enterprise"]))
        self.reject(lambda o: o["rows"][6].update(
            entity_mentions_source_relative=["Wesley Crusher", "Starfleet Academy", "Picard"]))
        self.reject(lambda o: o["rows"][8].update(
            entity_mentions_source_relative=["Jean-Luc Picard", "away team"]))

    def test_forged_but_plausible_draft_summary_fails_closed(self):
        self.reject(lambda o: o["rows"][0].update(original_synopsis_draft=(
            "A secret Federation plot transforms Data into a villain who attacks his friends."
        )))
        self.reject(lambda o: o["rows"][9].update(original_synopsis_draft=(
            "Two interstellar civilizations resolve their disagreement peacefully."
        )))

    def test_catalog_cross_series_or_source_lineage_mutation_refused(self):
        mutated = copy.deepcopy(self.catalog)
        for row in mutated["rows"]:
            if row["row_id"] == "legacy:s1:tng:019":
                row["context"] = "TOS S1E21"
                break
        with self.assertRaises(ValueError):
            MOD.compile_records(mutated, self.raw, self.observations)

    def test_duplicate_json_keys_refused(self):
        with self.assertRaises(ValueError):
            json.loads('{"episode":13,"episode":14}', object_pairs_hook=MOD.unique_pairs)

    def test_generated_records_exactly_regenerate(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
