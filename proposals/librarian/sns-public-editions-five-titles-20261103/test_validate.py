#!/usr/bin/env python3
"""Negative custody and privacy checks for seven public publisher edition leads."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class PublicEditionsValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = load()

    def reject(self, mutate):
        modified = copy.deepcopy(self.good)
        mutate(modified)
        with self.assertRaises(ValueError):
            validate(modified)

    def test_expected_seven_edition_pages_pass(self):
        self.assertIsNone(validate(self.good))

    def test_isbn_checksum_and_url_swaps_fail(self):
        self.reject(lambda d: d["records"][0].update(publisher_isbn13="9781668096643"))
        self.reject(lambda d: d["records"][0].update(publisher_isbn13=d["records"][1]["publisher_isbn13"]))
        self.reject(lambda d: d["records"][0].update(source_url=d["records"][1]["source_url"]))
        self.reject(lambda d: d["records"][4].update(source_url="https://malicious.example/books/Collateral-Damage"))

    def test_format_author_and_imprint_binding_fail(self):
        self.reject(lambda d: d["records"][0].update(format="TRADE_PAPERBACK"))
        self.reject(lambda d: d["records"][4].update(publisher_creator="Greg Cox"))
        self.reject(lambda d: d["records"][3].update(imprint="Pocket Books/Star Trek"))
        self.reject(lambda d: d["records"][2].update(publication_date="2025-12-02"))
        self.reject(lambda d: d["records"][2].update(page_count=0))

    def test_no_private_opf_or_asset_fields(self):
        self.reject(lambda d: d.update(private_owner_data_used=True))
        self.reject(lambda d: d.update(image_or_book_bytes_captured=True))
        self.reject(lambda d: d["records"][0].update(private_opf_path="D:/VERA/Private/Book.opf"))
        self.reject(lambda d: d["records"][0].update(image_locator="https://example.invalid/cover.jpg"))
        self.reject(lambda d: d["records"][0].update(edition_equivalent_to="same-text-work"))

    def test_no_false_html_or_content_reads(self):
        self.reject(lambda d: d.update(raw_publisher_html_captured=True))
        self.reject(lambda d: d["records"][0].update(source_raw_sha256="0" * 64))
        self.reject(lambda d: d["records"][0].update(source_page_access="FULL_EBOOK_READ"))

    def test_all_admission_and_release_promotions_fail(self):
        for name in ("source_admission_effect", "work_admission_effect", "source_work_binding_effect",
                     "explorer_effect", "research_coverage_effect"):
            with self.subTest(name=name):
                self.reject(lambda d, n=name: d.update({n: "ACCEPTED"}))
        self.reject(lambda d: d["records"][0].update(status="CLOSE_READ"))
        self.reject(lambda d: d.update(proposal_only=False))

    def test_missing_duplicate_and_injected_rows_fail(self):
        self.reject(lambda d: d["records"].pop())
        self.reject(lambda d: d["records"].append(copy.deepcopy(d["records"][0])))
        self.reject(lambda d: d["records"][1].update(publisher_isbn13=d["records"][0]["publisher_isbn13"]))
        self.reject(lambda d: d["records"][0].update(source_text="copyrighted excerpt"))

    def test_duplicate_raw_json_keys_fail_in_normal_and_optimized_python(self):
        with tempfile.TemporaryDirectory() as temp:
            payload = (HERE / "records.json").read_text(encoding="utf-8")
            poisoned = payload.replace('"proposal_only": true',
                                       '"proposal_only": false, "proposal_only": true', 1)
            destination = Path(temp) / "poisoned.json"
            destination.write_text(poisoned, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load(destination)
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    run = subprocess.run(
                        [sys.executable, *(["-O"] if optimized else []), "-c",
                         "import sys;from validate import load;load(__import__('pathlib').Path(sys.argv[1]))",
                         str(destination)], cwd=HERE, capture_output=True, text=True, check=False)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("duplicate JSON key", run.stderr)

    def test_optimized_python_rejects_impossible_admission(self):
        with tempfile.TemporaryDirectory() as temp:
            forged = copy.deepcopy(self.good)
            forged["research_coverage_effect"] = "CLOSE_READ"
            destination = Path(temp) / "promoted.json"
            destination.write_text(json.dumps(forged), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, "-O", "-c",
                 "import sys;from pathlib import Path;from validate import load,validate;validate(load(Path(sys.argv[1])))",
                 str(destination)], cwd=HERE, capture_output=True, text=True, check=False)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("unsafe packet field", run.stderr)

    def test_public_packet_has_no_private_or_copy_payload(self):
        serialized = json.dumps(self.good)
        for forbidden in ("Book.opf", "private_opf", "D:/", "C:/", "data:image", "<p>", "source_body", "raw_book_bytes"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
