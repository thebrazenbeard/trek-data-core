"""Adversarial, synthetic tests for final private Trek TXT 201–220 packet."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "proposals" / "librarian" / "private-txt201-220-20261103"
SPEC = importlib.util.spec_from_file_location("private_txt201_validator", SCOPE / "validate.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FinalTxtSourcePacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(mod.DATA.read_text(encoding="utf-8"))
        cls.prior = [json.loads(p.read_text(encoding="utf-8")) for p in mod.PRIOR]

    def test_all_220_receipts(self):
        mod.validate(self.good, self.prior)

    def test_changed_member_byte_hash(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = "0" * 64
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_cross_packet_duplicate_even_rehashed_rowset(self):
        bad = copy.deepcopy(self.good)
        bad["records"][3]["member_sha256"] = self.prior[3]["records"][20]["member_sha256"]
        bad["records_sha256"] = mod.rows_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_prior_packet_modified(self):
        prev = copy.deepcopy(self.prior)
        prev[0]["records"][0]["uncompressed_bytes"] += 1
        self.assertRaises(ValueError, mod.validate, self.good, prev)

    def test_false_coverage(self):
        bad = copy.deepcopy(self.good)
        bad["work_coverage_stage"] = "FULL_TEXT_AVAILABLE"
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_false_edition_rights(self):
        bad = copy.deepcopy(self.good)
        bad["data_rights"] = "OWNER"
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_extra_private_path(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["archive_member_path"] = "owner-secret-path"
        bad["records_sha256"] = mod.rows_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_sequence_failure(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["series_file_sequence_hint"] = 12
        bad["records_sha256"] = mod.rows_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)

    def test_twentyth_member_missing(self):
        bad = copy.deepcopy(self.good)
        bad["records"].pop()
        bad["records_sha256"] = mod.rows_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.prior)


if __name__ == "__main__":
    unittest.main()
