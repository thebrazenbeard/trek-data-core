"""Hostile guards for a fourth-to-fifth literary publisher proposal tranche."""

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "proposals/research/lit-six-series-expansion-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_six_series_expansion", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PublisherSixSeriesExpansionTests(unittest.TestCase):
    def reject(self, mutation):
        data = copy.deepcopy(module.EXPECTED)
        mutation(data)
        with self.assertRaises(ValueError):
            module.validate(data)

    def test_clean_six_title_packet(self):
        self.assertTrue(module.validate(module.EXPECTED))

    def test_six_titles_held_covers_and_isbn_checks(self):
        rows = module.EXPECTED["candidate_works"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r["title"] for r in rows}), 6)
        self.assertTrue(all(module.isbn13_valid(r["isbn13"]) for r in rows))
        self.assertTrue(all(r["cover_rights_status"] == "RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY" for r in rows))

    def test_four_prior_accepted_main_candidate_ledgers_excluded(self):
        titles, isbn = module.prior_inventory()
        self.assertEqual(len(titles), 21)
        self.assertEqual(len(isbn), 30)
        self.assertEqual(len(set(module.SOURCE_SCOPE_ANCHORS)), 6)

    def test_no_missing_work(self):
        self.reject(lambda d: d["candidate_works"].pop())

    def test_no_duplicate_title(self):
        self.reject(lambda d: d["candidate_works"][1].update(title=d["candidate_works"][0]["title"]))

    def test_no_duplicate_isbn(self):
        self.reject(lambda d: d["candidate_works"][1].update(isbn13=d["candidate_works"][0]["isbn13"]))

    def test_no_duplicate_earlier_title(self):
        self.reject(lambda d: d["candidate_works"][0].update(title="Star Trek: Strange New Worlds: The High Country"))

    def test_no_duplicate_fourth_wave_title(self):
        self.reject(lambda d: d["candidate_works"][0].update(title="Agents of Influence"))

    def test_no_duplicate_fourth_wave_isbn(self):
        self.reject(lambda d: d["candidate_works"][0].update(isbn13="9781982142186"))

    def test_no_unsupported_book_text_promotion(self):
        self.reject(lambda d: d.update(full_text_available=True))

    def test_no_close_read_promotion(self):
        self.reject(lambda d: d.update(close_read=True))

    def test_no_source_bound_promotion(self):
        self.reject(lambda d: d.update(source_bound=True))

    def test_no_coverage_promotion(self):
        self.reject(lambda d: d.update(accepted_coverage_effect="SIX_BOOKS"))

    def test_no_accepted_work_promotion(self):
        self.reject(lambda d: d.update(accepted_source_work_effect="SIX_WORKS"))

    def test_no_independence_inflation(self):
        self.reject(lambda d: d.update(distinct_upstream_sources=6))

    def test_no_cover_rights_escalation(self):
        self.reject(lambda d: d["candidate_works"][3].update(cover_rights_status="PUBLIC_DISPLAY_ALLOWED"))

    def test_no_image_bytes_promotion(self):
        self.reject(lambda d: d.update(cover_image_bytes_retrieved=True))

    def test_no_wrong_publisher_page(self):
        self.reject(lambda d: d["candidate_works"][0].update(publisher_url="https://example.org/unknown"))

    def test_no_wrong_edition_page(self):
        self.reject(lambda d: d["candidate_works"][4].update(publisher_url=d["candidate_works"][3]["publisher_url"]))

    def test_no_wrong_cover_edition(self):
        self.reject(lambda d: d["candidate_works"][4].update(cover_candidate_locator=d["candidate_works"][2]["cover_candidate_locator"]))

    def test_no_wrong_cover_host(self):
        self.reject(lambda d: d["candidate_works"][5].update(cover_candidate_locator="https://example.org/cover.jpg"))

    def test_no_fake_publisher_format(self):
        self.reject(lambda d: d["candidate_works"][1].update(format="HARDCOVER"))

    def test_no_fake_imprint(self):
        self.reject(lambda d: d["candidate_works"][5].update(imprint="Pocket Books/Star Trek"))

    def test_no_fabricated_metadata(self):
        self.reject(lambda d: d["candidate_works"][5].update(publisher_extent="999 pages"))

    def test_no_unsupported_global_id(self):
        self.reject(lambda d: d["candidate_works"][0].update(candidate_id="canonical-work-001"))

    def test_no_full_book_synopsis_label(self):
        self.reject(lambda d: d["candidate_works"][1].update(synopsis_status="CLOSE_READ"))

    def test_no_long_excerpt(self):
        self.reject(lambda d: d["candidate_works"][2].update(synopsis="Copied " * 300))

    def test_source_scope_guards_against_synopsis_swap(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        rows[0]["synopsis"], rows[1]["synopsis"] = rows[1]["synopsis"], rows[0]["synopsis"]
        with self.assertRaisesRegex(ValueError, "anchors"):
            module.validate_source_scope(rows)

    def test_source_scope_guards_against_franchise_inference(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        rows[5]["synopsis"] = "The publisher presents Dal and Gwyn finding a powerful superweapon."
        with self.assertRaisesRegex(ValueError, "anchors"):
            module.validate_source_scope(rows)

    def test_toward_night_does_not_claim_stranded_team(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        self.assertNotIn("strand", rows[0]["synopsis"].casefold())
        rows[0]["synopsis"] += " Spock's party is stranded."
        with self.assertRaisesRegex(ValueError, "stranded party"):
            module.validate_source_scope(rows)

    def test_dangerous_trade_not_completed_exchange(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        self.assertIn("plan to trade", rows[5]["synopsis"].casefold())
        rows[5]["synopsis"] += " The crew exchanged the battery."
        with self.assertRaisesRegex(ValueError, "completed battery exchange"):
            module.validate_source_scope(rows)

    def test_prior_snapshot_custody_fail_closed(self):
        original = module.PRIOR_SHA256
        try:
            module.PRIOR_SHA256 = ("0" * 64, *original[1:])
            with self.assertRaises(ValueError):
                module.prior_inventory()
        finally:
            module.PRIOR_SHA256 = original


if __name__ == "__main__":
    unittest.main()
