"""Negative drift tests for source-relative original LIT custody proposal."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "proposals" / "research" / "lit-time-to-kill-original-lit-20261103"
spec = importlib.util.spec_from_file_location("lit_original_custody_validator", PROPOSAL / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RECEIPT = json.loads((PROPOSAL / "RECEIPT.json").read_text(encoding="utf-8"))


class OriginalLitCustodyTests(unittest.TestCase):
    def test_valid_public_receipt(self):
        self.assertTrue(module.validate(RECEIPT))

    def assert_rejected(self, mutate):
        candidate = copy.deepcopy(RECEIPT)
        mutate(candidate)
        with self.assertRaises(ValueError):
            module.validate(candidate)

    def test_wrong_original_archive(self):
        self.assert_rejected(lambda d: d.update(original_archive_sha256="0" * 64))

    def test_wrong_original_lit_member(self):
        self.assert_rejected(lambda d: d.update(original_lit_member_sha256="0" * 64))

    def test_wrong_converted_spine(self):
        self.assert_rejected(lambda d: d.update(converted_html_spine_sha256="0" * 64))

    def test_premature_content_equivalence(self):
        self.assert_rejected(lambda d: d.update(conversion_equivalence_verified=True))

    def test_premature_source_read(self):
        self.assert_rejected(lambda d: d.update(original_lit_content_parsed=True))

    def test_premature_coverage(self):
        self.assert_rejected(lambda d: d.update(coverage_effect="SOURCE_BOUND"))

    def test_hidden_source_text(self):
        self.assert_rejected(lambda d: d.update(book_excerpt="not allowed"))

    def test_false_member_count(self):
        self.assert_rejected(lambda d: d.update(matching_original_lit_member_count=2))

    def test_bool_integer_type_confusion(self):
        self.assert_rejected(lambda d: d.update(matching_original_lit_member_count=True))


if __name__ == "__main__":
    unittest.main()
