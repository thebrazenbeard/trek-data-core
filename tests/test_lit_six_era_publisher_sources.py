"""Adversarial verification of six title/ISBN/cover-hold source-local leads."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "proposals/research/lit-six-era-publisher-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_six_era_validation", SOURCE)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestSixEraPublisherSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.priors = [json.loads(path.read_text(encoding="utf-8")) for path in (module.PRIOR_A, module.PRIOR_B, module.PRIOR_C)]

    def reject(self, mutate):
        obj = copy.deepcopy(module.EXPECTED)
        mutate(obj)
        with self.assertRaises(ValueError):
            module.validate(obj, *self.priors)

    def test_untampered_six_works(self):
        self.assertTrue(module.validate(module.EXPECTED, *self.priors))

    def test_six_distinct_sourced_titles(self):
        rows = module.EXPECTED["candidate_works"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r["title"] for r in rows}), 6)
        self.assertTrue(all(r["cover_rights_status"] == "RIGHTS_UNVERIFIED_HOLD_NO_PUBLIC_DISPLAY" for r in rows))

    def test_last_best_unsupported_specifics_absent(self):
        picard = next(r for r in module.EXPECTED["candidate_works"] if r["isbn13"] == "9781982142186")
        self.assertNotIn("romulan", picard["synopsis"].casefold())
        self.assertNotIn("supernova", picard["synopsis"].casefold())

    def test_last_best_source_scope_rejects_inference(self):
        rows = copy.deepcopy(module.EXPECTED["candidate_works"])
        rows[0]["synopsis"] += " Romulan supernova."
        with self.assertRaisesRegex(ValueError, "absent from cited page"):
            module.validate_page_description_scope(rows)

    def test_prior_proposals_cover_fifteen_works_24_editions(self):
        titles, isbn = module.prior_inventory(*self.priors)
        self.assertEqual(len(titles), 15)
        self.assertEqual(len(isbn), 24)

    def test_isbn13_checksum(self):
        self.assertTrue(module.isbn13_valid("9781982142186"))
        self.assertFalse(module.isbn13_valid("9781982142187"))
        self.assertFalse(module.isbn13_valid(9781982142186))

    def test_missing_work(self):
        self.reject(lambda d: d["candidate_works"].pop())

    def test_duplicate_title(self):
        self.reject(lambda d: d["candidate_works"][1].update(title=d["candidate_works"][0]["title"]))

    def test_duplicate_isbn(self):
        self.reject(lambda d: d["candidate_works"][1].update(isbn13=d["candidate_works"][0]["isbn13"]))

    def test_duplicate_prior15_title(self):
        self.reject(lambda d: d["candidate_works"][0].update(title="Star Trek: Picard: Second Self"))

    def test_duplicate_prior15_isbn(self):
        self.reject(lambda d: d["candidate_works"][0].update(isbn13="9781668046364"))

    def test_wrong_publisher_format(self):
        self.reject(lambda d: d["candidate_works"][4].update(format="TRADE_PAPERBACK"))

    def test_imprint_injection(self):
        self.reject(lambda d: d["candidate_works"][2].update(imprint="Unverified Imprint"))

    def test_global_identity_injection(self):
        self.reject(lambda d: d["candidate_works"][3].update(candidate_id="global-work-available-light"))

    def test_publisher_page_domain_swap(self):
        self.reject(lambda d: d["candidate_works"][4].update(publisher_url="https://example.com/fake"))

    def test_publisher_isbn_page_swap(self):
        self.reject(lambda d: d["candidate_works"][3].update(publisher_url=d["candidate_works"][0]["publisher_url"]))

    def test_publisher_date_forgery(self):
        self.reject(lambda d: d["candidate_works"][0].update(publisher_publication_date="1990-01-01"))

    def test_publisher_extent_forgery(self):
        self.reject(lambda d: d["candidate_works"][5].update(publisher_extent="999 pages"))

    def test_status_promoted_to_close_read(self):
        self.reject(lambda d: d["candidate_works"][1].update(synopsis_status="FULL_BOOK_CLOSE_READ"))

    def test_too_long_synopsis(self):
        self.reject(lambda d: d["candidate_works"][2].update(synopsis="Copied " * 400))

    def test_false_cover_cleared(self):
        self.reject(lambda d: d["candidate_works"][3].update(cover_rights_status="PUBLIC_DISPLAY_CLEARED"))

    def test_false_cover_host(self):
        self.reject(lambda d: d["candidate_works"][3].update(cover_candidate_locator="https://malicious.example/cover.jpg"))

    def test_cover_wrong_edition(self):
        self.reject(lambda d: d["candidate_works"][3].update(cover_candidate_locator=d["candidate_works"][0]["cover_candidate_locator"]))

    def test_cover_bytes_false_promotion(self):
        self.reject(lambda d: d.update(cover_image_bytes_retrieved=True))

    def test_artwork_license_false_promotion(self):
        self.reject(lambda d: d.update(artwork_display_rights_verified=True))

    def test_book_source_false_promotion(self):
        self.reject(lambda d: d.update(full_text_available=True))

    def test_corpus_admission_false_promotion(self):
        self.reject(lambda d: d.update(accepted_source_work_effect="SIX_WORKS_ACCEPTED"))

    def test_lineage_independence_inflation(self):
        self.reject(lambda d: d.update(distinct_upstream_sources=6))

    def test_prior_title_drift(self):
        priors = copy.deepcopy(self.priors)
        priors[0]["records"][0]["title"] = "Mistitled"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, *priors)

    def test_prior_edition_drift(self):
        priors = copy.deepcopy(self.priors)
        priors[1]["records"][0]["isbn13"] = "9780000000002"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, *priors)

    def test_prior_proposal_promotion(self):
        priors = copy.deepcopy(self.priors)
        priors[2]["proposal_only"] = False
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, *priors)


if __name__ == "__main__":
    unittest.main()
