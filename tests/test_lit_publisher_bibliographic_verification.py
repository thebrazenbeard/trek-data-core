"""Adversarial regression tests for three existing novel leads, nine publisher editions."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals/research/lit-three-publisher-editions-20261103"
spec = importlib.util.spec_from_file_location("literary_page_verify", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
OBS = json.loads((PROPOSAL / "observations.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "proposals/librarian/simon-schuster-three-novels-20261103/records.json").read_text(encoding="utf-8"))


class PublisherEditionChecks(unittest.TestCase):
    def test_verified_edition_pages_have_no_admission_effect(self):
        self.assertTrue(module.validate(OBS))

    def reject_record_mutation(self, change):
        record = copy.deepcopy(OBS)
        change(record)
        with self.assertRaises(ValueError):
            module.validate(record)

    def reject_source_mutation(self, change):
        source = copy.deepcopy(SOURCE)
        change(source)
        with self.assertRaises(ValueError):
            module.validate(OBS, source)

    def test_premature_source_bound(self):
        self.reject_record_mutation(lambda d: d.update(source_bound=True))

    def test_premature_full_text(self):
        self.reject_record_mutation(lambda d: d.update(full_text_available=True))

    def test_premature_semantic_close_read(self):
        self.reject_record_mutation(lambda d: d.update(semantic_close_read=True))

    def test_coverage_promotion(self):
        self.reject_record_mutation(lambda d: d.update(accepted_coverage_effect="CLOSE_READ"))

    def test_fabricated_second_upstream(self):
        self.reject_record_mutation(lambda d: d.update(distinct_upstream_sources=2))

    def test_wrong_edition_work(self):
        self.reject_record_mutation(lambda d: d["records"][0].update(candidate_work_id="proposed-lit-snw-high-country"))

    def test_wrong_isbn(self):
        self.reject_record_mutation(lambda d: d["records"][0].update(isbn13="9781982194840"))

    def test_wrong_duration(self):
        self.reject_record_mutation(lambda d: d["records"][5].update(publisher_extent="16 hours 12 minutes"))

    def test_wrong_narrator(self):
        self.reject_record_mutation(lambda d: d["records"][8].update(narrator="Another Reader"))

    def test_unknown_publication_field(self):
        self.reject_record_mutation(lambda d: d["records"][0].update(verified_full_edition=True))

    def test_synopsis_claimed_as_complete_read(self):
        self.reject_record_mutation(lambda d: d["work_synopses"][0].update(status="CLOSE_READ"))

    def test_synopsis_wrong_work(self):
        self.reject_record_mutation(lambda d: d["work_synopses"][0].update(candidate_work_id="proposed-lit-snw-high-country"))

    def test_synopsis_unrelated_source(self):
        self.reject_record_mutation(lambda d: d["work_synopses"][0].update(source_locator="https://www.simonandschuster.com/books/unrelated/9781982194840"))

    def test_synopsis_text_changed(self):
        self.reject_record_mutation(lambda d: d["work_synopses"][0].update(synopsis="An unsupported alternative plot description."))

    def test_source_publisher_url_swapped(self):
        self.reject_source_mutation(lambda d: d["editions"][0].update(publisher_product_url="https://www.simonandschuster.com/books/unrelated/9781982194833"))

    def test_source_title_swapped(self):
        self.reject_source_mutation(lambda d: d["works"][0].update(title="Another Book"))

    def test_source_edition_date_forged(self):
        self.reject_source_mutation(lambda d: d["editions"][4].update(publisher_publication_date="2000-01-01"))


if __name__ == "__main__":
    unittest.main()
