"""Hostile synthetic tests for literary metadata-only TXT member receipts 101–150."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "proposals" / "librarian" / "private-txt101-150-20261103"
SPEC = importlib.util.spec_from_file_location("txt101_validator", SCOPE / "validate.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class ThirdTxtPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(mod.DATA.read_text(encoding="utf-8"))
        cls.prior = [json.loads(p.read_text(encoding="utf-8")) for p in mod.PRIOR]

    def test_valid_three_packet_sequence(self):
        mod.validate(self.good, self.prior)

    def test_member_hash_tampering(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = "0" * 64
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_recycled_prior_hash_even_with_new_row_digest(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = self.prior[0]["records"][30]["member_sha256"]
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_prior_packet_rewrite(self):
        old = copy.deepcopy(self.prior)
        old[1]["records"][0]["uncompressed_bytes"] += 1
        self.assertRaises(ValueError, mod.validate, self.good, old)

    def test_edition_claim(self):
        bad = copy.deepcopy(self.good)
        bad["edition_binding"] = "VERIFIED"
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_copyright_publication_claim(self):
        bad = copy.deepcopy(self.good)
        bad["copyrighted_text_exported"] = True
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_series_number_forged(self):
        bad = copy.deepcopy(self.good)
        bad["records"][2]["series_file_sequence_hint"] = 18
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_private_path_injected(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["file_path"] = "owner/private/secret.txt"
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_third_packet_missing_row(self):
        bad = copy.deepcopy(self.good)
        bad["records"].pop()
        bad["records_sha256"] = mod.digest_rows(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)


if __name__ == "__main__":
    unittest.main()
