"""Fail-closed tests for the additive, unadmitted Picard discovery supplement."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("picard_overlay", ROOT / "tools/build_picard_literature_overlay.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PicardLiteratureOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = (ROOT / MODULE.SOURCE).read_bytes()
        cls.source = json.loads(cls.source_bytes)
        cls.directory_bytes = (ROOT / "explorer/discovery-catalog.json").read_bytes()

    def test_separate_exact_two_row_projection_has_no_admission_or_artwork(self):
        projected = MODULE.build()
        self.assertEqual(projected["row_count"], 2)
        self.assertEqual(projected["base_directory_row_count"], 1214)
        self.assertEqual(projected["source_input_sha256"], hashlib.sha256(self.source_bytes).hexdigest())
        self.assertEqual(projected["base_directory_sha256"], hashlib.sha256(self.directory_bytes).hexdigest())
        self.assertEqual(projected["data_status"], "PICARD_LITERATURE_SOURCE_LOCAL_SUPPLEMENT_ONLY")
        self.assertEqual(projected["identity_scope"], "SOURCE_LOCAL_NOT_RECONCILED")
        self.assertFalse(projected["full_text_read"])
        for effect in ("coverage_effect", "admission_effect", "artwork_release_effect"):
            self.assertEqual(projected[effect], "NONE")
        self.assertEqual([row["title"] for row in projected["rows"]], [
            "Star Trek: Picard: Rogue Elements", "Star Trek: Picard: The Dark Veil"
        ])
        for row in projected["rows"]:
            self.assertEqual(row["verification_status"], "UNVERIFIED_METADATA")
            self.assertEqual(row["identity_scope"], "SOURCE_LOCAL")
            self.assertEqual(row["admission_effect"], "NONE")
            self.assertEqual(row["coverage_effect"], "NONE")
            self.assertFalse(any(key.startswith("image") or key.startswith("cover_") or
                                 key in {"artwork", "artwork_url", "thumbnail"} for key in row))
        self.assertEqual((ROOT / MODULE.OUTPUT).read_bytes(), MODULE.encode(projected))
        self.assertEqual((ROOT / "explorer/discovery-catalog.json").read_bytes(), self.directory_bytes)

    def test_duplicate_source_is_rejected(self):
        poisoned = copy.deepcopy(self.source)
        poisoned["sources"][2] = copy.deepcopy(poisoned["sources"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.exact_source(poisoned)

    def test_missing_publisher_metadata_is_rejected(self):
        poisoned = copy.deepcopy(self.source)
        poisoned["sources"].pop()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            MODULE.exact_source(poisoned)

    def test_forged_full_text_source_hash_is_rejected(self):
        poisoned = copy.deepcopy(self.source)
        poisoned["sources"][0]["content_hash"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "custody"):
            MODULE.exact_source(poisoned)

    def test_forged_admitted_work_is_rejected(self):
        poisoned = copy.deepcopy(self.source)
        poisoned["works"][0]["status"] = "ACCEPTED"
        with self.assertRaisesRegex(ValueError, "promoted"):
            MODULE.exact_source(poisoned)

    def test_forged_provenance_url_is_rejected(self):
        poisoned = copy.deepcopy(self.source)
        poisoned["sources"][0]["locator"] = "https://www.simonandschuster.com.evil.test/a"
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            MODULE.exact_source(poisoned)

    def test_changed_source_bytes_fail_before_processing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / MODULE.SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes(self.source_bytes + b" ")
            base = temp / "explorer/discovery-catalog.json"
            base.parent.mkdir(parents=True)
            base.write_bytes(self.directory_bytes)
            with self.assertRaisesRegex(ValueError, "source bytes changed"):
                MODULE.build(temp)

    def test_changed_historical_directory_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source = temp / MODULE.SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes(self.source_bytes)
            base = temp / "explorer/discovery-catalog.json"
            base.parent.mkdir(parents=True)
            base.write_bytes(self.directory_bytes + b" ")
            with self.assertRaisesRegex(ValueError, "immutable base catalog invalid"):
                MODULE.build(temp)


if __name__ == "__main__":
    unittest.main()
