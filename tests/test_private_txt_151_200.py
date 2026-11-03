"""Adversarial derivative tests for source-local Trek TXT ZIP 151–200 packet."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "proposals" / "librarian" / "private-txt151-200-20261103"
SPEC = importlib.util.spec_from_file_location("private_txt151_validator", FOLDER / "validate.py")
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class FourthTxtPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(module.DATA.read_text(encoding="utf-8"))
        cls.previous = [json.loads(p.read_text(encoding="utf-8")) for p in module.PREVIOUS]

    def test_200_source_member_chain(self):
        module.validate(self.good, self.previous)

    def test_new_member_rehash_required(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = "0" * 64
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_duplicate_prior_member_even_with_valid_new_row_digest(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["member_sha256"] = self.previous[1]["records"][3]["member_sha256"]
        bad["records_sha256"] = module.rows_digest(bad["records"])
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_earlier_packet_changed(self):
        old = copy.deepcopy(self.previous)
        old[2]["records"][4]["uncompressed_bytes"] += 1
        self.assertRaises(ValueError, module.validate, self.good, old)

    def test_false_rights(self):
        bad = copy.deepcopy(self.good)
        bad["data_rights"] = "OWNER"
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_unsupported_literary_coverage(self):
        bad = copy.deepcopy(self.good)
        bad["work_coverage_stage"] = "CLOSE_READ"
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_series_boundary_incorrect(self):
        bad = copy.deepcopy(self.good)
        bad["records"][40]["series_hint"] = "TNG"
        bad["records_sha256"] = module.rows_digest(bad["records"])
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_extra_private_path_field(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["file_path"] = "owner-secret-book.zip"
        bad["records_sha256"] = module.rows_digest(bad["records"])
        self.assertRaises(ValueError, module.validate, bad, self.previous)

    def test_missing_entry(self):
        bad = copy.deepcopy(self.good)
        bad["records"].pop()
        bad["records_sha256"] = module.rows_digest(bad["records"])
        self.assertRaises(ValueError, module.validate, bad, self.previous)


if __name__ == "__main__":
    unittest.main()
