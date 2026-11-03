"""Hostile tests for sixth publisher-edition literary packet: proposals only."""

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "proposals/research/lit-six-next-arc-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_six_next_arc", P)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class SixthPublisherArcTests(unittest.TestCase):
    def reject(self, mutate):
        d = copy.deepcopy(module.EXPECTED)
        mutate(d)
        with self.assertRaises(ValueError):
            module.validate(d)

    def test_original_packet(self):
        self.assertTrue(module.validate(module.EXPECTED))

    def test_distinct_six_from_prior_27(self):
        titles, isbn = module.prior_inventory()
        self.assertEqual(len(titles), 27)
        self.assertEqual(len(isbn), 36)
        self.assertFalse({r["title"] for r in module.EXPECTED["candidate_works"]} & titles)

    def test_future_release_is_not_full_text(self):
        first = module.EXPECTED["candidate_works"][0]
        self.assertEqual(first["publisher_publication_date"], "2026-11-17")
        self.assertEqual(first["publisher_release_state"], "FUTURE_PUBLISHER_DATE_NO_TEXT_AVAILABILITY_CLAIM")
        self.assertFalse(module.EXPECTED["full_text_available"])

    def test_missing_work_rejected(self):
        self.reject(lambda d: d["candidate_works"].pop())

    def test_duplicate_title_rejected(self):
        self.reject(lambda d: d["candidate_works"][1].update(title=d["candidate_works"][0]["title"]))

    def test_duplicate_isbn_rejected(self):
        self.reject(lambda d: d["candidate_works"][1].update(isbn13=d["candidate_works"][0]["isbn13"]))

    def test_duplicate_fifth_title_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(title="A Dangerous Trade"))

    def test_duplicate_fourth_isbn_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(isbn13="9781982142186"))

    def test_future_release_claim_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(publisher_release_state="FULL_BOOK_AVAILABLE"))

    def test_future_release_date_falsification_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(publisher_publication_date="2026-10-01"))

    def test_imprint_swap_rejected(self):
        self.reject(lambda d: d["candidate_works"][5].update(imprint="Pocket Books/Star Trek"))

    def test_market_format_swap_rejected(self):
        self.reject(lambda d: d["candidate_works"][2].update(format="TRADE_PAPERBACK"))

    def test_illegal_global_identity_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(candidate_id="global-ds9-peacemakers"))

    def test_publisher_url_host_rejected(self):
        self.reject(lambda d: d["candidate_works"][2].update(publisher_url="https://another-site.com/unknown"))

    def test_edition_url_swap_rejected(self):
        self.reject(lambda d: d["candidate_works"][2].update(publisher_url=d["candidate_works"][1]["publisher_url"]))

    def test_cover_url_host_rejected(self):
        self.reject(lambda d: d["candidate_works"][1].update(cover_candidate_locator="https://example.org/fake.jpg"))

    def test_cover_edition_swap_rejected(self):
        self.reject(lambda d: d["candidate_works"][4].update(cover_candidate_locator=d["candidate_works"][5]["cover_candidate_locator"]))

    def test_cover_rights_escalation_rejected(self):
        self.reject(lambda d: d["candidate_works"][5].update(cover_rights_status="CLEARED"))

    def test_cover_bytes_escalation_rejected(self):
        self.reject(lambda d: d.update(cover_image_bytes_retrieved=True))

    def test_source_text_escalation_rejected(self):
        self.reject(lambda d: d.update(full_text_available=True))

    def test_close_read_escalation_rejected(self):
        self.reject(lambda d: d.update(close_read=True))

    def test_source_bound_escalation_rejected(self):
        self.reject(lambda d: d.update(source_bound=True))

    def test_work_admission_escalation_rejected(self):
        self.reject(lambda d: d.update(accepted_source_work_effect="SIX"))

    def test_coverage_escalation_rejected(self):
        self.reject(lambda d: d.update(accepted_coverage_effect="SIX"))

    def test_source_lineage_fanout_rejected(self):
        self.reject(lambda d: d.update(distinct_upstream_sources=6))

    def test_synopsis_close_read_label_rejected(self):
        self.reject(lambda d: d["candidate_works"][0].update(synopsis_status="FULL_BOOK_READ"))

    def test_synopsis_copy_length_rejected(self):
        self.reject(lambda d: d["candidate_works"][3].update(synopsis="Copied " * 400))

    def test_source_scope_swap_rejected(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        rows[0]["synopsis"], rows[1]["synopsis"] = rows[1]["synopsis"], rows[0]["synopsis"]
        with self.assertRaisesRegex(ValueError, "anchor"):
            module.validate_source_scope(rows)

    def test_source_scope_missing_future_book_jake_rejected(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        rows[0]["synopsis"] = "The publisher announces a forthcoming DS9 adventure with an unspecified protagonist."
        with self.assertRaisesRegex(ValueError, "anchor"):
            module.validate_source_scope(rows)

    def test_supernova_past_captivity_unestablished(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        self.assertNotIn("captivity", rows[5]["synopsis"].casefold())
        rows[5]["synopsis"] += " The threat comes from their earlier captivity."
        with self.assertRaisesRegex(ValueError, "earlier captivity"):
            module.validate_source_scope(rows)

    def test_prior_blob_custody_rejected(self):
        old = module.PRIOR_SHA256
        try:
            module.PRIOR_SHA256 = ("0" * 64, *old[1:])
            with self.assertRaises(ValueError):
                module.prior_inventory()
        finally:
            module.PRIOR_SHA256 = old


if __name__ == "__main__":
    unittest.main()
