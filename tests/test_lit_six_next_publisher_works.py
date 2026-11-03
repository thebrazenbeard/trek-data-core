"""Falsifier suite: six distinct publisher-page Work proposals, never book-text evidence."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "proposals/research/lit-six-next-publisher-works-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_next_six_publisher_validation", PATH)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestNextSixPublisherWorks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(module.PICARD_SOURCE.read_text(encoding="utf-8"))

    def reject(self, fn):
        candidate = copy.deepcopy(module.EXPECTED)
        fn(candidate)
        with self.assertRaises(ValueError):
            module.validate(candidate, self.source)

    def test_pristine_observations(self):
        self.assertTrue(module.validate(module.EXPECTED, self.source))

    def test_six_distinct_sources_and_synopses(self):
        rows = module.EXPECTED["candidate_works"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({(r["series"], r["title"]) for r in rows}), 6)
        self.assertEqual(len({r["isbn13"] for r in rows}), 6)
        self.assertTrue(all(r["synopsis_status"] == "PUBLISHER_DESCRIPTION_PARAPHRASE" for r in rows))

    def test_all_are_not_previous_nine(self):
        for r in module.EXPECTED["candidate_works"]:
            self.assertNotIn((r["series"], r["title"]), module.PRIOR_NINE)

    def test_isbn_checksum(self):
        self.assertTrue(module.isbn13_valid("9781982154073"))
        self.assertFalse(module.isbn13_valid("9781982154070"))
        self.assertFalse(module.isbn13_valid(9781982154073))

    def test_missing_work_rejected(self):
        self.reject(lambda x: x["candidate_works"].pop())

    def test_duplicate_isbn_rejected(self):
        self.reject(lambda x: x["candidate_works"][1].update(isbn13=x["candidate_works"][0]["isbn13"]))

    def test_previous_nine_title_insertion_rejected(self):
        def mutate(x):
            x["candidate_works"][2].update(series="Star Trek: Picard", title="Star Trek: Picard: Second Self")
        self.reject(mutate)

    def test_existing_librarian_id_cross_work_forgery_rejected(self):
        self.reject(lambda x: x["candidate_works"][0].update(existing_librarian_candidate_id="proposed-lit-picard-rogue-elements"))

    def test_new_candidate_claims_existing_id_rejected(self):
        self.reject(lambda x: x["candidate_works"][3].update(existing_librarian_candidate_id="proposed-lit-picard-the-dark-veil"))

    def test_creator_forgery_rejected(self):
        self.reject(lambda x: x["candidate_works"][0].update(creator="David Mack"))

    def test_format_overpromotion_rejected(self):
        self.reject(lambda x: x["candidate_works"][3].update(format="HARDCOVER"))

    def test_wrong_page_count_rejected(self):
        self.reject(lambda x: x["candidate_works"][0].update(publisher_extent="400 pages"))

    def test_wrong_publication_date_rejected(self):
        self.reject(lambda x: x["candidate_works"][1].update(publisher_publication_date="2000-01-01"))

    def test_wrong_locator_rejected(self):
        self.reject(lambda x: x["candidate_works"][5].update(publisher_url="https://example.org/books/revenant"))

    def test_synopsis_canonical_reclassification_rejected(self):
        self.reject(lambda x: x["candidate_works"][5].update(synopsis_status="ACCEPTED_CANONICAL_PLOT"))

    def test_excessive_synopsis_rejected(self):
        self.reject(lambda x: x["candidate_works"][4].update(synopsis="unsupported " * 400))

    def test_no_accepted_source_work_effect(self):
        self.reject(lambda x: x.update(accepted_source_work_effect="ADMITTED"))

    def test_no_accepted_coverage_effect(self):
        self.reject(lambda x: x.update(accepted_coverage_effect="CLOSE_READ"))

    def test_no_full_text_promotion(self):
        self.reject(lambda x: x.update(full_text_available=True))

    def test_no_semantic_promotion(self):
        self.reject(lambda x: x.update(semantically_analyzed=True))

    def test_no_cover_rights_claim(self):
        self.reject(lambda x: x.update(artwork_display_rights_verified=True))

    def test_source_candidate_title_mutation_rejected(self):
        source = copy.deepcopy(self.source)
        source["works"][0]["title"] = "Made-Up Title"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, source)

    def test_source_isbn_mutation_rejected(self):
        source = copy.deepcopy(self.source)
        source["sources"][0]["provider_metadata"]["isbn13"] = "9781982154070"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, source)

    def test_source_publication_date_mutation_rejected(self):
        source = copy.deepcopy(self.source)
        source["sources"][1]["provider_metadata"]["publication_date"] = "1900-01-01"
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, source)

    def test_unaccepted_librarian_source_reclassification_rejected(self):
        source = copy.deepcopy(self.source)
        source["proposal_only"] = False
        with self.assertRaises(ValueError):
            module.validate(module.EXPECTED, source)


if __name__ == "__main__":
    unittest.main()
