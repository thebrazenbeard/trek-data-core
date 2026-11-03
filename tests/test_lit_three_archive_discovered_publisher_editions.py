"""Tests designed to run under repository-wide discovery without module collisions."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_FILE = ROOT / "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/validate.py"
SPEC = importlib.util.spec_from_file_location("lit_three_archive_publisher_validate_module", MODULE_FILE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("source-local publisher validator not found")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class PublisherEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(module.RECORDS.read_text(encoding="utf-8"))

    def test_valid_source_local_packet(self):
        module.validate(self.good)

    def test_private_edition_identity_not_assumed(self):
        bad = copy.deepcopy(self.good)
        bad["candidates"][0]["private_archive_edition_identity"] = "MATCHED"
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_private_absolute_path_not_public(self):
        bad = copy.deepcopy(self.good)
        bad["private_archive"] = "C:/Users/private-user/OneDrive/Documents/Books/archive.zip"
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_private_topology_rejected_even_outside_archive_field(self):
        bad = copy.deepcopy(self.good)
        bad["owner_note"] = "C:/Users/private-user/Documents/Books"
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_abridged_audio_not_mislabeled_as_full_ebook(self):
        bad = copy.deepcopy(self.good)
        bad["candidates"][1]["publisher_edition_format"] = "EBOOK"
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_no_private_text_custody_promotion(self):
        bad = copy.deepcopy(self.good)
        bad["full_text_available"] = True
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_no_public_effect(self):
        bad = copy.deepcopy(self.good)
        bad["public_synopsis_effect"] = "PUBLISHED"
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_source_typo_remains_qualified(self):
        bad = copy.deepcopy(self.good)
        bad["candidates"][1]["original_publisher_description_paraphrase"] = bad["candidates"][1]["original_publisher_description_paraphrase"].replace("Ssan", "Susan")
        with self.assertRaises(ValueError):
            module.validate(bad)

    def test_isbn_mismatch_rejected(self):
        bad = copy.deepcopy(self.good)
        bad["candidates"][2]["publisher_isbn13"] = "9780743546592"
        with self.assertRaises(ValueError):
            module.validate(bad)


if __name__ == "__main__":
    unittest.main()
