"""Adversarial tests of private OPF and official publisher metadata crosswalk."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "proposals" / "librarian" / "private-opf-publisher-ten-20261103"
SPEC = importlib.util.spec_from_file_location("opf_pub_ten", FOLDER / "validate.py")
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class OpfPublisherTenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(mod.DATA.read_text(encoding="utf-8"))
        cls.opf = json.loads(mod.OPF.read_text(encoding="utf-8"))
        cls.txt = json.loads(mod.TXT.read_text(encoding="utf-8"))

    def test_exact_crosswalk(self):
        mod.validate(self.good, self.opf, self.txt)

    def test_isbn10_conversion(self):
        self.assertEqual(mod.isbn13_from_isbn10("0743412133"), "9780743412131")
        self.assertEqual(mod.isbn13_from_isbn10("0743439961"), "9780743439961")
        self.assertRaises(ValueError, mod.isbn13_from_isbn10, "0743412134")

    def test_source_opf_sha_changed(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["original_opf_entry_sha256"] = "0" * 64
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_omnibus_identifier_conflict_hidden(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["edition_identifier_relation"] = "ISBN10_13_CHECKDIGIT_MATCH"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_wrong_publisher_product_url(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["official_product_page"] = "https://example.com/books/Ghost-Ship/9780743412131"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_namespace_repair_hold_removed(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["opf_xml_parse_status"] = "PARSED"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_private_path_field_leaked(self):
        bad = copy.deepcopy(self.good)
        bad["records"][0]["owner_zip_path"] = "private-location"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_false_work_admission(self):
        bad = copy.deepcopy(self.good)
        bad["canonical_work_admissions"] = 10
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_copyrighted_jacket_release_flag(self):
        bad = copy.deepcopy(self.good)
        bad["jacket_image_binary_published"] = True
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_source_txt_candidate_swapped(self):
        bad = copy.deepcopy(self.good)
        bad["records"][1]["original_txt_filename_candidate_id"] = "txt-local:0090"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)

    def test_publisher_creator_order_held(self):
        bad = copy.deepcopy(self.good)
        bad["records"][3]["creator_relation"] = "CASEFOLD_NAME_MATCH"
        bad["records_sha256"] = mod.rowset_digest(bad["records"])
        self.assertRaises(ValueError, mod.validate, bad, self.opf, self.txt)


if __name__ == "__main__":
    unittest.main()
