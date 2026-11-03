"""Adversarial checks for public aggregate receipt acceptance boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("private_receipt", ROOT / "validate.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class AggregateReceiptTests(unittest.TestCase):
    def setUp(self):
        self.original = mod.load(ROOT / "receipt.json")

    def test_authentic_public_receipt(self):
        mod.validate(self.original)

    def test_no_extra_fields_or_private_members(self):
        altered = copy.deepcopy(self.original)
        altered["private_inventory"]["internal_member_name"] = "sample/member.opf"
        with self.assertRaisesRegex(ValueError, "private_inventory"):
            mod.validate(altered)

    def test_no_admission_or_rights_promotion(self):
        for key, value in (("accepted_work_effect", "ACCEPTED"),
                           ("coverage_effect", "ADVANCED"),
                           ("rights_status", "PUBLIC_RELEASE_GRANTED")):
            altered = copy.deepcopy(self.original)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                mod.validate(altered)

    def test_receipt_count_or_hash_tamper(self):
        for branch, key, new in (("summary", "opf_packages", 348),
                                 ("original_archive", "sha256", "0" * 64),
                                 ("private_inventory", "sha256", "a" * 64)):
            altered = copy.deepcopy(self.original)
            altered[branch][key] = new
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                mod.validate(altered)

    def test_optimized_python_must_reject_tampered_admission(self):
        altered = copy.deepcopy(self.original)
        altered["accepted_source_effect"] = "ADMITTED"
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory) / "receipt.json"
            temporary.write_text(json.dumps(altered), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-O", str(ROOT / "validate.py"), "--input", str(temporary)],
                text=True, capture_output=True,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("forbidden accepted_source_effect", proc.stderr)

    def test_duplicate_json_keys_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory) / "duplicate.json"
            temporary.write_text('{"role":"LIBRARIAN","role":"AUDITOR"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                mod.load(temporary)


if __name__ == "__main__":
    unittest.main()
