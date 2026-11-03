#!/usr/bin/env python3
"""No-media/rights-gate regression tests for HELD First Contact source photos."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("first_contact_source_validator", HERE / "validate.py")
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FirstContactCommonsSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = mod.load_record()

    def test_held_packet_accepts_exact_source_only(self) -> None:
        mod.validate(self.record)

    def test_no_public_release_or_privilege_flip(self) -> None:
        for field, changed in (("public_image_display_authorized", True),
                               ("remote_image_hotlink_committed", True),
                               ("image_binary_committed", 1),
                               ("site_effect", "PUBLIC"),
                               ("underlying_prop_rights", "CLEARED")):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.record)
                candidate[field] = changed
                with self.assertRaises(ValueError):
                    mod.validate(candidate, check_tracked=False)

    def test_no_fabricated_rights_approval(self) -> None:
        candidate = copy.deepcopy(self.record)
        candidate["release_holds"]["independent_underlying_prop_rights_editorial_context_review"] = "PASS"
        with self.assertRaises(ValueError):
            mod.validate(candidate, check_tracked=False)

    def test_preview_source_hash_pins(self) -> None:
        candidate = copy.deepcopy(self.record)
        candidate["assets"][0]["rendition_sha256_verified"] = "0" * 64
        with self.assertRaises(ValueError):
            mod.validate(candidate, check_tracked=False)

    def test_rejects_duplicate_json_keys(self) -> None:
        with self.assertRaises(ValueError):
            json.loads('{"status":"HELD", "status":"PUBLIC"}', object_pairs_hook=mod.unique_pairs)

    def test_rejects_binary_disguised_and_html_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "MANIFEST.md"
            src.write_bytes(b"\xff\xd8\xffbinary")
            with self.assertRaises(ValueError):
                mod.check_text(src)
            src.write_text('<img src="https://example.test/photo.jpg">', encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.check_text(src)


if __name__ == "__main__":
    unittest.main()
