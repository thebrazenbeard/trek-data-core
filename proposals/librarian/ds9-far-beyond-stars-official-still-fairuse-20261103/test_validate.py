#!/usr/bin/env python3
"""Hostile still-identity, rights, byte, embed, and release-gate regression tests."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import validate as guard


class DS9ExactOfficialStillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = guard.read_record()

    def test_provenanced_still_passes_without_publication(self):
        self.assertEqual(guard.validate(self.record), 5)

    def test_false_still_or_license_or_coverage_claim_rejected(self):
        for key, value in (
            ("source_image_kind", "RECAP_ART_NOT_EPISODE_STILL"),
            ("episode_name", "Darmok"),
            ("series_name", "Star Trek: Picard"),
            ("article_served_variant_sha256", "a" * 64),
            ("thumbnail_preferred_sha256", "b" * 64),
            ("thumbnail_preferred_dimensions", [1920, 1080]),
            ("thumbnail_preferred_bytes", 500000),
            ("permission_class", "CC0"),
            ("fair_use_result", "FULL_RIGHTS_CLEARANCE"),
            ("proposed_caption", "Authorized Paramount film still"),
            ("image_binary_committed", 1),
            ("public_image_display_authorized", True),
            ("remote_hotlink_committed", True),
            ("site_effect", "PUBLISHED"),
            ("work_or_coverage_admission", "ACCEPTED"),
        ):
            with self.subTest(key=key):
                altered = copy.deepcopy(self.record)
                altered[key] = value
                with self.assertRaises(ValueError):
                    guard.validate(altered)

    def test_review_gate_forgery_rejected(self):
        for key in guard.EXPECTED_HOLDS:
            with self.subTest(key=key):
                altered = copy.deepcopy(self.record)
                altered["release_holds"][key] = "GO"
                with self.assertRaises(ValueError):
                    guard.validate(altered)

    def test_manifest_false_copyright_claim_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "MANIFEST.md").write_text(
                (guard.HERE / "MANIFEST.md").read_text() + "\nParamount licensed it CC0 without review\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "MANIFEST rights/source"):
                guard.validate(self.record, directory=d)

    def test_live_image_embed_in_allowed_source_rejected(self):
        for fragment in (
            "!" + "[still](https://example.invalid/still.jpg)",
            "<" + "picture>" + "<" + "source srcset='https://example.invalid/a.jpg'>",
            "# " + "data:" + "image/jpeg;base64,AAAA",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / "test_validate.py").write_text(fragment, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "live media embed/hotlink"):
                    guard.validate(self.record, directory=d)

    def test_nested_image_or_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "payload").mkdir()
            (d / "payload" / "still.jpg").write_bytes(b"unqualified")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)
            (d / "payload" / "still.jpg").unlink()
            (d / "payload" / "escape").symlink_to(d.parent / "outside.jpg")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)

    def test_disguised_jpeg_magic_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "MANIFEST.md").write_bytes(b"\xff\xd8\xff\xe0fake")
            with self.assertRaisesRegex(ValueError, "image/binary magic"):
                guard.validate(self.record, directory=d)

    def test_missing_manifest_and_tests_rejected(self):
        for missing in ("MANIFEST.md", "test_validate.py"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                for name in guard.ALLOWED:
                    shutil.copyfile(guard.HERE / name, d / name)
                (d / missing).unlink()
                with self.assertRaisesRegex(ValueError, "missing required packet source"):
                    guard.validate(self.record, directory=d)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            guard.unique_pairs([("rights", "CC0"), ("rights", "no license")])


if __name__ == "__main__":
    unittest.main()
