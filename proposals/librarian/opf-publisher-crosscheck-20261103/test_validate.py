"""Mutation checks for the metadata-only source-boundary guard."""

from __future__ import annotations

import copy
import unittest

from validate import ROOT, SOURCE, load, validate


class CrosscheckValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load(ROOT / "records.json")
        cls.source = load(SOURCE)
        cls.source_bytes = SOURCE.read_bytes()

    def check_rejected(self, modifier):
        mutant = copy.deepcopy(self.data)
        modifier(mutant)
        with self.assertRaises(ValueError):
            validate(mutant, self.source, self.source_bytes)

    def test_baseline(self):
        validate(self.data, self.source, self.source_bytes)

    def test_held_different_isbn_cannot_be_promoted(self):
        self.check_rejected(lambda data: data["records"][0].update(
            crosscheck_state="PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"))

    def test_wrong_converted_isbn(self):
        self.check_rejected(lambda data: data["records"][1].update(isbn13_candidate="9780743419018"))

    def test_private_file_claim(self):
        self.check_rejected(lambda data: data.update(private_source_equivalence_verified=True))

    def test_phantom_coverage(self):
        self.check_rejected(lambda data: data.update(coverage_effect="ONE"))

    def test_unreviewed_publisher_url(self):
        self.check_rejected(lambda data: data["records"][1].update(
            publisher_locator="https://en.wikipedia.org/wiki/The_Belly_of_the_Beast"))

    def test_altered_publisher_title(self):
        self.check_rejected(lambda data: data["records"][1].update(publisher_title="Some Different Title"))

    def test_duplicate_source_local_id(self):
        self.check_rejected(lambda data: data["records"][1].update(opf_source_local_id="opf-local:0009"))


if __name__ == "__main__":
    unittest.main()
