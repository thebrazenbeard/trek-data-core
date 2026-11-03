"""Regression and adversarial tests of 51–100 TXT ZIP receipt observations."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "proposals" / "librarian" / "private-txt51-100-20261103"
SPEC = importlib.util.spec_from_file_location("private_txt51_validator", SCOPE / "validate.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class NextTxtReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(mod.DATA.read_text(encoding="utf-8"))
        cls.prior = json.loads(mod.PRIOR.read_text(encoding="utf-8"))

    def test_happy_path(self):
        mod.validate(self.good, self.prior)

    def test_bad_member_bytes_digest(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = "0" * 64
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_duplicate_accepted_member_even_with_valid_packet_digest(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["member_sha256"] = self.prior["records"][0]["member_sha256"]
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_prior_receipt_tampering(self):
        prior = copy.deepcopy(self.prior)
        prior["records"][0]["uncompressed_bytes"] += 1
        self.assertRaises(ValueError, mod.validate, self.good, prior)

    def test_private_path_injection_even_with_rehash(self):
        bad = copy.deepcopy(self.good)
        bad["records"][3]["private_path"] = "C:/private/user/secret.txt"
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_false_source_or_work_binding(self):
        for key, value in (("work_coverage_stage", "CLOSE_READ"), ("source_work_binding", "VERIFIED"),
                           ("edition_binding", "VERIFIED"), ("data_rights", "OWNER")):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.good)
                bad[key] = value
                self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_ordinal_and_series_mismatch(self):
        for key in ("archive_txt_ordinal", "series_file_sequence_hint"):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.good)
                bad["records"][0][key] += 1
                bad["records_sha256"] = mod.digest_rows(bad["records"])
                self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_missing_fiftyfirst_row(self):
        bad = copy.deepcopy(self.good)
        bad["records"] = bad["records"][1:]
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)


if __name__ == "__main__":
    unittest.main()
