"""Strict source-only OPF publisher comparison and adversarial mutation checks."""
from __future__ import annotations

import copy
import unittest

from validate import OLDER, ROOT, SOURCE, forbid_private_paths, load, validate


class OPFThirdTenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load(ROOT / "records.json")
        cls.observed = load(SOURCE)
        cls.source_bytes = SOURCE.read_bytes()
        cls.predecessors = (load(OLDER[0]), load(OLDER[1]))

    def rejected(self, mutation):
        altered = copy.deepcopy(self.records)
        mutation(altered)
        with self.assertRaises(ValueError):
            validate(altered, self.observed, self.source_bytes, self.predecessors)

    def test_unmodified_batch(self):
        validate(self.records, self.observed, self.source_bytes, self.predecessors)

    def test_wrong_isbn(self):
        self.rejected(lambda x: x["records"][0].update(isbn13_candidate="9780743420946"))

    def test_wrong_source_fingerprint(self):
        self.rejected(lambda x: x["records"][0].update(opf_entry_sha256="0" * 64))

    def test_false_edition_equivalence(self):
        self.rejected(lambda x: x.update(private_source_equivalence_verified=True))

    def test_false_work_admission(self):
        self.rejected(lambda x: x.update(global_work_admission="TEN"))

    def test_false_coverage(self):
        self.rejected(lambda x: x.update(coverage_effect="TEN"))

    def test_false_raw_page_custody(self):
        self.rejected(lambda x: x.update(publisher_raw_html_sha256="a" * 64))

    def test_silent_source_title_correction(self):
        self.rejected(lambda x: x["records"][4].update(
            crosscheck_state="PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"))

    def test_fabricated_synopsis(self):
        self.rejected(lambda x: x["records"][2].update(
            original_publisher_description_paraphrase="An invented canonical episode detail nobody published."))

    def test_extra_author(self):
        self.rejected(lambda x: x["records"][6]["publisher_authors"].append("Invented Contributor"))

    def test_extra_private_path_in_author(self):
        self.rejected(lambda x: x["records"][6]["publisher_authors"].append(
            r"C:\\Users\\Example\\Documents\\Books\\item.epub"))

    def test_private_path_uncertainty(self):
        self.rejected(lambda x: x["records"][1].update(
            uncertainty="A private file at /home/example/books/secret.epub should not be exported."))

    def test_unknown_field(self):
        self.rejected(lambda x: x["records"][0].update(unreviewed_field="surprise"))

    def test_unknown_envelope_field(self):
        self.rejected(lambda x: x.update(unreviewed_envelope="surprise"))

    def test_wrong_publisher_url(self):
        self.rejected(lambda x: x["records"][0].update(
            publisher_locator="https://example.com/book/9780743420945"))

    def test_duplicate_opf_id(self):
        self.rejected(lambda x: x["records"][1].update(opf_source_local_id="opf-local:0062"))

    def test_removed_row(self):
        self.rejected(lambda x: x["records"].pop())

    def test_source_digest_drift(self):
        self.rejected(lambda x: x.update(source_observation_sha256="0" * 64))

    def test_private_path_nested_key_scan(self):
        with self.assertRaises(ValueError):
            forbid_private_paths({"nested": [{r"D:\\Vera\\private\\novel.epub": "secret"}]})


if __name__ == "__main__":
    unittest.main()
