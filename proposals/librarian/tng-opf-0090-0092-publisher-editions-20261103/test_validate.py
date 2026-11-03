#!/usr/bin/env python3
"""Hostile mutations must fail under regular and optimized Python."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import validate as v


class PublisherEditionValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = v.load(v.ROOT / "records.json")
        cls.upstream = v.load(v.SOURCE)
        cls.upstream_raw = v.SOURCE.read_bytes()
        cls.previous = tuple(v.load(path) for path in v.PREVIOUS)

    def check(self, mutated, upstream=None, raw=None, previous=None):
        v.validate(mutated, self.upstream if upstream is None else upstream,
                   self.upstream_raw if raw is None else raw,
                   self.previous if previous is None else previous)

    def must_fail(self, edit, upstream=None, raw=None, previous=None):
        mutant = copy.deepcopy(self.good)
        edit(mutant)
        with self.assertRaises((ValueError, KeyError, TypeError, IndexError)):
            self.check(mutant, upstream, raw, previous)

    def test_positive(self):
        self.check(copy.deepcopy(self.good))

    def test_duplicate_json_key(self):
        raw = '{"schema_version":1,"schema_version":1}'
        with tempfile.TemporaryDirectory() as path:
            filename = Path(path) / "duplicated.json"
            filename.write_text(raw, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                v.load(filename)

    def test_private_path_leak(self):
        self.must_fail(lambda d: d["records"][0].__setitem__("uncertainty", "C:/Users/private/book.epub"))

    def test_work_admission(self):
        self.must_fail(lambda d: d.__setitem__("global_work_admission", "ADMITTED"))

    def test_coverage_promotion(self):
        self.must_fail(lambda d: d.__setitem__("coverage_effect", "STRUCTURALLY_INDEXED"))

    def test_private_text_overclaim(self):
        self.must_fail(lambda d: d.__setitem__("private_ebook_text_read", True))

    def test_cover_rights_overclaim(self):
        self.must_fail(lambda d: d.__setitem__("publisher_cover_bytes_exported", True))

    def test_equivalence_overclaim(self):
        self.must_fail(lambda d: d.__setitem__("private_source_equivalence_verified", True))

    def test_wrong_upstream_sha(self):
        self.must_fail(lambda d: d.__setitem__("source_observation_sha256", "0" * 64))

    def test_changed_upstream_bytes(self):
        with self.assertRaises(ValueError):
            self.check(self.good, raw=self.upstream_raw + b" ")

    def test_opf_source_local_id_swap(self):
        self.must_fail(lambda d: d["records"][0].__setitem__("opf_source_local_id", "opf-local:0091"))

    def test_isbn_mismatch_falsely_marked_match(self):
        self.must_fail(lambda d: d["records"][1].__setitem__("crosscheck_state", v.MATCH))

    def test_isbn_publisher_mismatch_hidden(self):
        self.must_fail(lambda d: d["records"][1].__setitem__("publisher_isbn13", "9780743421225"))

    def test_publisher_page_url_substitution(self):
        self.must_fail(lambda d: d["records"][0].__setitem__("publisher_locator", "https://example.com/publisher/book"))

    def test_opf_date_publisher_date_conflation(self):
        self.must_fail(lambda d: d["records"][0].__setitem__("opf_metadata_date", "2000-09-22"))

    def test_publisher_date_forged(self):
        self.must_fail(lambda d: d["records"][1].__setitem__("publisher_publication_date", "2000-08-05"))

    def test_title_contamination(self):
        self.must_fail(lambda d: d["records"][2].__setitem__("opf_title", "Data's Evil Twin"))

    def test_synopsis_change_unreviewed(self):
        self.must_fail(lambda d: d["records"][2].__setitem__("original_publisher_description_paraphrase", "The original synopsis is now completely different and fabricated by a careless editor."))

    def test_prior_accepted_duplicate(self):
        previous = copy.deepcopy(self.previous)
        prior = list(previous)
        prior[0]["records"][0]["opf_source_local_id"] = "opf-local:0090"
        with self.assertRaisesRegex(ValueError, "Already accepted"):
            self.check(self.good, previous=tuple(prior))

    def test_schema_extension_fails(self):
        self.must_fail(lambda d: d["records"][0].__setitem__("canonical_entity", "work:foo"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
