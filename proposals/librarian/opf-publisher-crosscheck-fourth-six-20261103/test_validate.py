"""Adversarial checks against false OPF publisher research promotion."""
from __future__ import annotations
import copy
import unittest
from validate import ROOT, SOURCE, OLDER, load, validate, forbid_private_paths


class OPFFourthSixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load(ROOT / "records.json")
        cls.source = load(SOURCE)
        cls.source_bytes = SOURCE.read_bytes()
        cls.older = tuple(load(path) for path in OLDER)

    def rejected(self, mutate):
        payload = copy.deepcopy(self.data)
        mutate(payload)
        with self.assertRaises(ValueError):
            validate(payload, self.source, self.source_bytes, self.older)

    def test_baseline(self):
        validate(self.data, self.source, self.source_bytes, self.older)

    def test_changed_upstream_sha(self):
        self.rejected(lambda x: x.update(source_observation_sha256="0" * 64))

    def test_wrong_isbn(self):
        self.rejected(lambda x: x["records"][0].update(isbn13_candidate="9780743421088"))

    def test_wrong_source_fingerprint(self):
        self.rejected(lambda x: x["records"][0].update(opf_entry_sha256="0" * 64))

    def test_previous_id_reused(self):
        self.rejected(lambda x: x["records"][0].update(opf_source_local_id="opf-local:0062"))

    def test_duplicate_row(self):
        self.rejected(lambda x: x["records"][1].update(opf_source_local_id="opf-local:0073"))

    def test_missing_row(self):
        self.rejected(lambda x: x["records"].pop())

    def test_forged_publisher_title(self):
        self.rejected(lambda x: x["records"][0].update(publisher_title="Grounded: The Official Novel"))

    def test_forged_synopsis(self):
        self.rejected(lambda x: x["records"][0].update(
            original_publisher_description_paraphrase="Invented assertions about canonical life and events."))

    def test_added_creator(self):
        self.rejected(lambda x: x["records"][2]["publisher_authors"].append("Unreviewed Name"))

    def test_private_path_in_creator(self):
        self.rejected(lambda x: x["records"][0]["publisher_authors"].append(
            r"C:\\Users\\Example\\Private\\book.epub"))

    def test_private_path_in_uncertainty(self):
        self.rejected(lambda x: x["records"][0].update(
            uncertainty="Owner local file resides in /home/example/Books/private.epub"))

    def test_extra_row_field(self):
        self.rejected(lambda x: x["records"][0].update(hidden_field="unexpected"))

    def test_extra_envelope_field(self):
        self.rejected(lambda x: x.update(hidden_field="unexpected"))

    def test_wrong_publisher_url(self):
        self.rejected(lambda x: x["records"][0].update(
            publisher_locator="https://example.org/Grounded"))

    def test_false_cover_custody(self):
        self.rejected(lambda x: x.update(publisher_cover_bytes_exported=True))

    def test_false_raw_page_custody(self):
        self.rejected(lambda x: x.update(publisher_raw_html_sha256="0" * 64))

    def test_false_private_edition_binding(self):
        self.rejected(lambda x: x.update(private_source_equivalence_verified=True))

    def test_false_coverage(self):
        self.rejected(lambda x: x.update(coverage_effect="SIX_BOOKS"))

    def test_unheld_synopsis(self):
        self.rejected(lambda x: x["records"][0].update(synopsis_review_state="APPROVED"))

    def test_private_path_nested_map_key(self):
        with self.assertRaises(ValueError):
            forbid_private_paths({"nested": [{r"D:\\Private\\file.epub": "leak"}]})


if __name__ == "__main__":
    unittest.main()
