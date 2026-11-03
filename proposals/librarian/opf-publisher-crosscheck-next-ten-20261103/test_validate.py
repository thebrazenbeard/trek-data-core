"""Adversarial tests: source-local publisher data cannot silently be promoted."""

from __future__ import annotations

import copy
import unittest

from validate import OLDER, ROOT, SOURCE, forbid_private_paths, load, validate


class TenOPFCrosscheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposal = load(ROOT / "records.json")
        cls.source = load(SOURCE)
        cls.raw = SOURCE.read_bytes()
        cls.older = load(OLDER)

    def rejected(self, mutation):
        altered = copy.deepcopy(self.proposal)
        mutation(altered)
        with self.assertRaises(ValueError):
            validate(altered, self.source, self.raw, self.older)

    def test_baseline(self):
        validate(self.proposal, self.source, self.raw, self.older)

    def test_wrong_converted_isbn(self):
        self.rejected(lambda x: x["records"][0].update(isbn13_candidate="9780743412156"))

    def test_wrong_upstream_opf_fingerprint(self):
        self.rejected(lambda x: x["records"][0].update(opf_entry_sha256="0" * 64))

    def test_fabricated_synopsis(self):
        self.rejected(lambda x: x["records"][1].update(original_publisher_description_paraphrase=
                      "Source proves a canonical plot claim that the publisher never states."))

    def test_extra_author_even_without_private_path(self):
        self.rejected(lambda x: x["records"][1]["publisher_authors"].append("Unknown Author"))

    def test_extra_author_private_path(self):
        self.rejected(lambda x: x["records"][1]["publisher_authors"].append(
                      r"C:\\Users\\Example\\Documents\\Books\\item.epub"))

    def test_private_path_in_uncertainty(self):
        self.rejected(lambda x: x["records"][0].update(uncertainty=
                      "Unresolved item recorded at /home/example/private/book.epub"))

    def test_unrecognized_envelope_field(self):
        self.rejected(lambda x: x.update(unreviewed_metadata="surprise"))

    def test_unrecognized_record_field(self):
        self.rejected(lambda x: x["records"][1].update(unreviewed_private_source="surprise"))

    def test_false_work_admission(self):
        self.rejected(lambda x: x.update(global_work_admission="YES"))

    def test_false_coverage_effect(self):
        self.rejected(lambda x: x.update(coverage_effect="TEN_BOOKS"))

    def test_false_raw_html_custody(self):
        self.rejected(lambda x: x.update(publisher_raw_html_sha256="f" * 64))

    def test_creator_conflict_cannot_be_silently_resolved(self):
        self.rejected(lambda x: x["records"][0].update(crosscheck_state=
                      "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"))

    def test_second_creator_publisher_source_cannot_be_dropped(self):
        self.rejected(lambda x: x["records"][8]["publisher_authors"].pop(1))

    def test_unreviewed_publisher_url(self):
        self.rejected(lambda x: x["records"][0].update(publisher_locator="https://example.org/claim"))

    def test_duplicate_opf_id(self):
        self.rejected(lambda x: x["records"][1].update(opf_source_local_id="opf-local:0052"))

    def test_missing_row(self):
        self.rejected(lambda x: x["records"].pop())

    def test_source_digest_drift(self):
        self.rejected(lambda x: x.update(source_observation_sha256="f" * 64))

    def test_private_path_in_nested_extra_key(self):
        with self.assertRaises(ValueError):
            forbid_private_paths({"nested": [{r"D:\\Private\\file.epub": "absent"}]})


if __name__ == "__main__":
    unittest.main()
