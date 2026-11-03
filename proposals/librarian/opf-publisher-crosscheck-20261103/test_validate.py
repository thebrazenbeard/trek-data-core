"""Mutation checks for the metadata-only source-boundary guard."""

from __future__ import annotations

import copy
import unittest

from validate import ROOT, SOURCE, forbid_private_paths, load, validate


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

    def test_adversarial_extra_author_private_path(self):
        self.check_rejected(lambda data: data["records"][1]["publisher_authors"].append(
            r"C:\\Users\\Patrick\\OneDrive\\Documents\\Books\\private.epub"))

    def test_adversarial_fabricated_canonical_synopsis(self):
        self.check_rejected(lambda data: data["records"][1].update(
            original_publisher_description_paraphrase="Verified canonical evidence proves global edition identity."))

    def test_adversarial_uncertainty_leaks_private_path(self):
        self.check_rejected(lambda data: data["records"][1].update(
            uncertainty="An unresolved observation at /home/patrick/private/books/item.epub must be audited."))

    def test_adversarial_unknown_private_source_key(self):
        self.check_rejected(lambda data: data["records"][1].update(
            source_private_local_path=r"D:\\VERA\\private\\novels\\item.epub"))

    def test_private_path_scanner_standalone(self):
        with self.assertRaises(ValueError):
            forbid_private_paths({"nested": [{"notes": "file:///Users/patrick/private.epub"}]})

    def test_extra_field_without_a_private_path(self):
        self.check_rejected(lambda data: data["records"][1].update(unreviewed_scalar="innocuous"))


if __name__ == "__main__":
    unittest.main()
