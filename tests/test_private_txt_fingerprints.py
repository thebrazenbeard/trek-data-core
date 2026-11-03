"""Adversarial tests of the public-safe DS9 TXT member receipt validator."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "proposals" / "librarian" / "private-ds9-txt50-20261103" / "validate.py"
SPEC = importlib.util.spec_from_file_location("private_txt_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
DATA, rows_digest, validate = module.DATA, module.rows_digest, module.validate


class PrivateTxtReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(DATA.read_text(encoding="utf-8"))

    def test_accepted_derivative_shape(self):
        validate(self.good)

    def test_row_tampering_fails(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_work_admission_claim_fails(self):
        bad = copy.deepcopy(self.good)
        bad["source_work_binding"] = "VERIFIED"
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_private_path_field_fails_even_with_rehash(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_path"] = "C:/private/books/example.txt"
        bad["records_sha256"] = rows_digest(bad["records"])
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_duplicate_digest_fails_even_with_rehash(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["member_sha256"] = bad["records"][0]["member_sha256"]
        bad["records_sha256"] = rows_digest(bad["records"])
        with self.assertRaises(AssertionError):
            validate(bad)

    def test_membership_count_change_fails(self):
        bad = copy.deepcopy(self.good)
        bad["archive"]["txt_members"] = 600
        with self.assertRaises(AssertionError):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
