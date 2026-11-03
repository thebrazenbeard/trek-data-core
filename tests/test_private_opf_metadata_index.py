"""Privacy, custody and deterministic-search tests for private OPF metadata observations."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_private_opf_metadata_index as mod  # noqa: E402


class PrivateOPFIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.raw = mod.exact_read(mod.SOURCE)
        cls.index = mod.compile_index(cls.source, cls.raw)

    @staticmethod
    def compile_repinned_mutation(altered):
        """Re-pin only snapshot digest so semantic guard tests reach their actual guard."""
        raw = json.dumps(altered, sort_keys=True, ensure_ascii=False).encode()
        with mock.patch.object(mod, "RAW_OBSERVATION_SHA256", hashlib.sha256(raw).hexdigest()):
            return mod.compile_index(altered, raw)

    def test_all_347_source_local_metadata_rows_without_work_admission(self):
        self.assertEqual(self.index["row_count"], 347)
        self.assertEqual(self.index["normal_xml_parse"], 332)
        self.assertEqual(self.index["in_memory_namespace_recovered"], 15)
        self.assertEqual(self.index["isbn_checksum_valid_candidate_rows"], 75)
        self.assertEqual(self.index["edition_bindings_verified"], 0)
        self.assertEqual(self.index["full_text_sources_read"], 0)
        self.assertEqual(self.index["work_admission_effect"], "NONE")
        self.assertEqual(self.index["coverage_effect"], "NONE")
        self.assertEqual(len(self.index["records"]), 347)
        for n, row in enumerate(self.index["records"], 1):
            self.assertEqual(row["source_local_id"], f"opf-local:{n:04d}")
            self.assertEqual(row["edition_binding"], "NOT_VERIFIED")
            self.assertEqual(row["work_identity"], "NOT_RECONCILED")
            self.assertEqual(row["source_identity_scope"], "ONE_OWNER_PRIVATE_OPF_XML_ENTRY")
            self.assertTrue(row["title_search_keys"])

    def test_recovered_entries_marked_without_forging_original_bytes(self):
        recovered = [i for i, row in enumerate(self.index["records"], 1) if row["metadata_parse_status"] == "OPF_XML_NAMESPACE_RECOVERED"]
        self.assertEqual(set(recovered), mod.NAMESPACE_RECOVERED)
        for i in recovered:
            self.assertEqual(self.index["records"][i-1]["entry_fingerprint_sha256"], self.source["rows"][i-1]["opf_entry_sha256"])

    def test_valid_isbn_checksums(self):
        self.assertTrue(mod.valid_isbn("0743412133"))
        self.assertTrue(mod.valid_isbn("9780743412131"))
        self.assertFalse(mod.valid_isbn("0743412134"))
        self.assertFalse(mod.valid_isbn("9780743412130"))
        self.assertFalse(mod.valid_isbn("{BCC2C6C9-4D69-4873-9F70-6242EAFE3704}"))
        self.assertFalse(mod.valid_isbn("5795.186"))
        self.assertFalse(mod.valid_isbn("0-7434-1213-3"))

    def test_normalized_search_keys_do_not_claim_reconciliation(self):
        row = self.index["records"][0]
        self.assertIn("star trek gateways 1of7 one small step", row["title_search_keys"])
        self.assertEqual(row["work_identity"], "NOT_RECONCILED")
        self.assertEqual(mod.search_key("THE  KOBAYASHI-MARU"), "the kobayashi maru")

    def test_protected_metadata_envelope_cannot_promote_admission_or_full_text(self):
        for key, value in (
            ("work_admission_effect", "SOURCE_BOUND"),
            ("coverage_effect", "FULL_TEXT_AVAILABLE"),
            ("ebook_full_text_read", True),
            ("private_member_paths_exported", True),
            ("private_identifier_guids_exported", True),
            ("copyrighted_text_or_images_exported", True),
            ("edition_binding_verified", True),
            ("public_synopsis_approved", True),
        ):
            altered = copy.deepcopy(self.source)
            altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.compile_repinned_mutation(altered)

    def test_sensitive_fields_and_hidden_identifier_cannot_be_added(self):
        for extra, value in (("absolute_path", "C:\\Users\\example"), ("OverDriveGUID", "abc"), ("cover", "file.png")):
            altered = copy.deepcopy(self.source)
            altered["rows"][0][extra] = value
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.compile_repinned_mutation(altered)
        altered = copy.deepcopy(self.source)
        altered["rows"][0]["title"] = ["C:\\Users\\example\\Documents\\Books\\secret.opf"]
        with self.assertRaises(ValueError):
            self.compile_repinned_mutation(altered)
        for leak in (
            "C:/Users/example/Documents/Books/secret.opf",
            "file:///private/archive", "{08DC3623-76F1-4F2D-BC22-E6E50E1D6EDE}",
            "person@example.invalid", "\\server\\share\\private", "control\x01character",
            "bidirectional\u202eoverride", "control\x85character",
            "/var/private/research.opf", "//server/share/cover.jpg",
            "C%3A%5CUsers%5Csomeone%5Csecret",
        ):
            altered = copy.deepcopy(self.source)
            altered["rows"][0]["creator"] = [leak]
            with self.subTest(leak=leak), self.assertRaises(ValueError):
                self.compile_repinned_mutation(altered)

    def test_source_id_and_recovered_state_are_immutable(self):
        for index, key, value in (
            (0, "source_local_id", "opf-local:9999"),
            (0, "opf_entry_sha256", "0" * 64),
            (0, "parse_status", "OPF_XML_NAMESPACE_RECOVERED"),
            (49, "parse_status", "PARSED"),
            (1, "isbn_checksum_valid", ["1234567890"]),
        ):
            altered = copy.deepcopy(self.source)
            altered["rows"][index][key] = value
            with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                self.compile_repinned_mutation(altered)

    def test_digest_and_duplicate_keys_fail_closed(self):
        altered = copy.deepcopy(self.source)
        altered["source_container"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.compile_repinned_mutation(altered)
        with self.assertRaises(ValueError):
            mod.compile_index(self.source, b"{}")
        with self.assertRaises(ValueError):
            mod.reject_duplicate_keys([("title", "x"), ("title", "y")])

    def test_public_metadata_contains_no_private_locator_or_guid(self):
        data = (ROOT / mod.SOURCE).read_text(encoding="utf-8")
        index_data = (ROOT / mod.INDEX).read_text(encoding="utf-8")
        for forbidden in ("OneDrive", "OverDriveGUID", "C:\\Users\\", "opf_books/", "\\\\patri\\", "/mnt/c/"):
            self.assertNotIn(forbidden, data)
            self.assertNotIn(forbidden, index_data)

    def test_derivative_is_byte_stable_in_both_python_modes(self):
        expected = (json.dumps(self.index, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
        self.assertEqual((ROOT / mod.INDEX).read_bytes(), expected)
        for optimized in (False, True):
            command = [sys.executable] + (["-O"] if optimized else []) + [str(ROOT / "tools/build_private_opf_metadata_index.py"), "--check"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
