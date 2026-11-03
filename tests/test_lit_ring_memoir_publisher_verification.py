"""Adversarial mutation guards for official edition pages, not literary close reads."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "proposals/research/lit-ring-memoir-publisher-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_ring_memoir_publisher_validation", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestRingMemoirPublisherVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ring = json.loads(module.RING_SOURCE.read_text(encoding="utf-8"))
        cls.prh = json.loads(module.PRH_SOURCE.read_text(encoding="utf-8"))

    def altered(self, key, value):
        obj = copy.deepcopy(module.EXPECTED)
        obj[key] = value
        with self.assertRaises(ValueError):
            module.validate(obj, self.ring, self.prh)

    def test_pristine_record_and_source_proposals(self):
        self.assertTrue(module.validate(module.EXPECTED, self.ring, self.prh))

    def test_actual_nine_edition_rows_and_six_distinct_works(self):
        records = module.EXPECTED["records"]
        self.assertEqual(len(records), 9)
        self.assertEqual(len({r["isbn13"] for r in records}), 9)
        self.assertEqual(len({r["candidate_work_id"] for r in records}), 6)

    def test_exact_six_original_source_labeled_synopses(self):
        synopses = module.EXPECTED["work_synopses"]
        self.assertEqual(len(synopses), 6)
        self.assertTrue(all(s["status"] == "PUBLISHER_DESCRIPTION_PARAPHRASE" for s in synopses))

    def test_deleting_edition_fails(self):
        self.altered("records", module.EXPECTED["records"][:-1])

    def test_duplicate_isbn_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[-1]["isbn13"] = records[0]["isbn13"]
        self.altered("records", records)

    def test_crossed_work_isbn_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[4]["candidate_work_id"] = records[5]["candidate_work_id"]
        self.altered("records", records)

    def test_wrong_creator_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[4]["creator"] = "Una McCormack"
        self.altered("records", records)

    def test_wrong_edition_format_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[1]["format"] = "HARDCOVER"
        self.altered("records", records)

    def test_future_publication_date_substitution_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[1]["publication_date"] = "2025-10-07"
        self.altered("records", records)

    def test_audio_narrator_removed_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[3]["narrator"] = None
        self.altered("records", records)

    def test_publisher_url_swapped_fails(self):
        records = copy.deepcopy(module.EXPECTED["records"])
        records[0]["publisher_url"] = records[1]["publisher_url"]
        self.altered("records", records)

    def test_lineage_independence_inflation_fails(self):
        self.altered("distinct_upstream_lineages", 9)

    def test_premature_coverage_fails(self):
        self.altered("accepted_coverage_effect", "NINE_VERIFIED_WORKS")

    def test_full_text_promotion_fails(self):
        self.altered("full_text_available", True)

    def test_semantic_close_read_promotion_fails(self):
        self.altered("semantic_close_read", True)

    def test_art_rights_claim_fails(self):
        self.altered("artwork_display_rights_verified", True)

    def test_synopsis_promoted_to_plot_fact_fails(self):
        synopses = copy.deepcopy(module.EXPECTED["work_synopses"])
        synopses[0]["status"] = "CLOSE_READ_CANONICAL_ASSERTION"
        self.altered("work_synopses", synopses)

    def test_synopsis_crossed_source_fails(self):
        synopses = copy.deepcopy(module.EXPECTED["work_synopses"])
        synopses[0]["source_locator"] = synopses[2]["source_locator"]
        self.altered("work_synopses", synopses)

    def test_publisher_copy_replaced_with_long_text_fails(self):
        synopses = copy.deepcopy(module.EXPECTED["work_synopses"])
        synopses[0]["synopsis"] = "repeat " * 200
        self.altered("work_synopses", synopses)

    def test_source_ring_work_mutation_fails(self):
        ring = copy.deepcopy(self.ring)
        ring["work"]["title"] = "Unknown Ring"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, ring, self.prh)

    def test_source_ring_isbn_mutation_fails(self):
        ring = copy.deepcopy(self.ring)
        ring["edition_candidates"][0]["isbn13"] = "9781668095897"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, ring, self.prh)

    def test_source_prh_publication_date_mutation_fails(self):
        prh = copy.deepcopy(self.prh)
        prh["edition_candidates"][2]["publication_date"] = "2001-01-01"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, self.ring, prh)

    def test_source_prh_work_swap_mutation_fails(self):
        prh = copy.deepcopy(self.prh)
        prh["edition_candidates"][0]["work_id"] = "prh-autobiography-sisko"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, self.ring, prh)

    def test_source_accepted_promotion_fails(self):
        ring = copy.deepcopy(self.ring)
        ring["proposal_only"] = False
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, ring, self.prh)

    def test_isbn13_checksum_rejects_bad_values(self):
        self.assertTrue(module.isbn13_valid("9781668095898"))
        self.assertFalse(module.isbn13_valid("9781668095897"))
        self.assertFalse(module.isbn13_valid(9781668095898))


if __name__ == "__main__":
    unittest.main()
