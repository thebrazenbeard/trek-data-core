#!/usr/bin/env python3
"""Adversarial source, license, media-byte and release-state tests."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import validate as guard


class LowerDecksCCBYSA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = guard.read_record()

    def test_packet_held_exactly(self):
        self.assertEqual(guard.validate(self.record), 5)

    def test_false_original_sha_or_film_frame_or_publication_rejected(self):
        for key, val in (
            ("original_sha256_independently_computed", "a" * 64),
            ("original_sha1_from_commons_metadata", "b" * 40),
            ("rendition_sha256_verified", "c" * 64),
            ("photographer", "Paramount"),
            ("license", "CC_BY_2_0_GENERIC"),
            ("photo_kind", "EPISODE_FRAME"),
            ("public_image_display_authorized", True),
            ("remote_image_hotlink_committed", True),
            ("image_binary_committed", 1),
            ("work_or_coverage_admission", "ACCEPTED"),
            ("proposed_caption", "A scene from the Lower Decks show"),
            ("proposed_credit", "No credit necessary, public domain"),
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.record)
                changed[key] = val
                with self.assertRaises(ValueError):
                    guard.validate(changed)

    def test_independent_review_forgery_rejected(self):
        for key in guard.EXPECTED_HOLDS:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.record)
                changed["release_holds"][key] = "GO"
                with self.assertRaises(ValueError):
                    guard.validate(changed)

    def test_falsified_manifest_licensing_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "MANIFEST.md").write_text(
                (guard.HERE / "MANIFEST.md").read_text() + "\nNo attribution, not ShareAlike!\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "MANIFEST source statement"):
                guard.validate(self.record, directory=d)

    def test_remote_embeds_rejected(self):
        for markup in (
            "!" + "[panel](https://thumb.wikimedia.org/wikipedia/commons/file.jpg)",
            "<" + "picture>" + "<" + "source srcset='https://evil.invalid/pic.jpg'>",
            "data:" + "image/jpeg;base64,AAAA",
        ):
            with tempfile.TemporaryDirectory() as temp:
                d = Path(temp)
                (d / "test_validate.py").write_text(markup, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "embedded/hotlinked media"):
                    guard.validate(self.record, directory=d)

    def test_nested_image_or_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "hidden").mkdir()
            (d / "hidden" / "panel.jpg").write_bytes(b"image")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)
            (d / "hidden" / "panel.jpg").unlink()
            (d / "hidden" / "out").symlink_to(d.parent / "escaped")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)

    def test_misnamed_jpeg_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "MANIFEST.md").write_bytes(b"\xff\xd8\xff\xe0NOT_TEXT")
            with self.assertRaisesRegex(ValueError, "image/binary magic"):
                guard.validate(self.record, directory=d)

    def test_absent_mandatory_files_rejected(self):
        for missing in ("MANIFEST.md", "test_validate.py"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temp:
                d = Path(temp)
                for source in guard.ALLOWED:
                    shutil.copyfile(guard.HERE / source, d / source)
                (d / missing).unlink()
                with self.assertRaisesRegex(ValueError, "missing reviewed source"):
                    guard.validate(self.record, directory=d)

    def test_duplicate_json_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
            guard.no_duplicate_keys([("license", "CC0"), ("license", "CC BY-SA")])


if __name__ == "__main__":
    unittest.main()
