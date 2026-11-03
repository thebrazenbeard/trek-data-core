"""Adversarial tests for the public, proposal-only chapter locator index."""

import copy
import json
from pathlib import Path
import unittest

from validate import validate


FIXTURE = json.loads((Path(__file__).resolve().parent / "CHAPTER_INDEX.json").read_text("utf-8"))


class ChapterLocatorTests(unittest.TestCase):
    def test_original_is_proposal_only(self):
        validate(FIXTURE)

    def assert_rejected(self, edit):
        record = copy.deepcopy(FIXTURE)
        edit(record)
        with self.assertRaises(ValueError):
            validate(record)

    def test_source_prose_key_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][0].update({"passage": "not permitted"}))

    def test_accepted_coverage_promotion_rejected(self):
        self.assert_rejected(lambda d: d.update({"coverage_effect": "SOURCE_BOUND"}))

    def test_nonmonotonic_chapter_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][4].update({"chapter": 99}))

    def test_duplicate_line_span_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][9].update({"source_relative_normalized_line_start": 5}))

    def test_hash_corruption_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][1].update({"segment_sha256": "0" * 63}))

    def test_well_formed_chapter_forgery_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][0].update({"segment_sha256": "0" * 64}))

    def test_well_formed_body_forgery_rejected(self):
        self.assert_rejected(lambda d: d.update({"html_spine_sha256": "0" * 64}))

    def test_valid_domain_wrong_book_rejected(self):
        self.assert_rejected(lambda d: d.update({"publisher_url": "https://www.simonandschuster.com/books/unrelated"}))

    def test_mismatched_method_count_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][0].update({"whitespace_token_count": 1}))

    def test_book_swap_rejected(self):
        self.assert_rejected(lambda d: d.update({"work_candidate_title": "Different work"}))

    def test_boolean_spoof_rejected(self):
        self.assert_rejected(lambda d: d["chapters"][1].update({"whitespace_token_count": True}))


if __name__ == "__main__":
    unittest.main()
