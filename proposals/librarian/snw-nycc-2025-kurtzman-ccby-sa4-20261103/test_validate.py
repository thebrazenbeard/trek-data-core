#!/usr/bin/env python3
"""Adversarial own-work source, CC license and image release tests."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import validate as guard


class NYCCSNWPortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = guard.load_record()

    def test_exact_record_passes_with_release_held(self):
        self.assertEqual(guard.validate(self.record), 5)

    def test_forged_license_author_or_episode_still_rejected(self):
        for key, value in (
            ("uploader_credited_author", "Paramount"),
            ("license", "CC0"),
            ("commons_pinned_oldid", 0),
            ("original_sha1_commons_metadata", "0" * 40),
            ("original_sha256_independently_computed", "a" * 64),
            ("verified_rendition_sha256", "b" * 64),
            ("verified_rendition_dimensions", [1920, 1080]),
            ("photo_kind", "STRANGE_NEW_WORLDS_EPISODE_FRAME"),
            ("association_status", "SOURCE_BOUND"),
            ("public_image_display_authorized", True),
            ("remote_image_hotlink_committed", True),
            ("photo_binary_committed", 1),
            ("site_effect", "PUBLISHED"),
            ("work_or_coverage_admission", "ACCEPTED"),
            ("proposed_caption", "Alex Kurtzman in episode 5"),
            ("proposed_credit", "Public domain no author"),
        ):
            with self.subTest(key=key):
                packet = copy.deepcopy(self.record)
                packet[key] = value
                with self.assertRaises(ValueError):
                    guard.validate(packet)

    def test_forged_reviewer_go_fails(self):
        for key in guard.EXPECTED_HOLDS:
            with self.subTest(key=key):
                packet = copy.deepcopy(self.record)
                packet["release_holds"][key] = "GO"
                with self.assertRaises(ValueError):
                    guard.validate(packet)

    def test_misleading_rights_manifest_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            source = (guard.HERE / "MANIFEST.md").read_text()
            (d / "MANIFEST.md").write_text(source + "\nNo rights restrictions!\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "MANIFEST source/rights"):
                guard.validate(self.record, directory=d)

    def test_remote_media_embed_rejected(self):
        for markup in (
            "!" + "[Kurtzman](https://thumb.wikimedia.org/photo.jpg)",
            "<" + "picture>" + "<" + "source srcset='https://a.invalid/p.jpg'>",
            "data:" + "image/jpeg;base64,AAAA",
        ):
            with tempfile.TemporaryDirectory() as temp:
                d = Path(temp)
                (d / "test_validate.py").write_text(markup, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "active image/media embed"):
                    guard.validate(self.record, directory=d)

    def test_nested_binary_symlink_and_disguised_image_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "subdir").mkdir()
            (d / "subdir" / "hidden.jpg").write_bytes(b"faked")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)
            (d / "subdir" / "hidden.jpg").unlink()
            (d / "subdir" / "link").symlink_to(d.parent / "escaped")
            with self.assertRaises(ValueError):
                guard.validate(self.record, directory=d)
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d / "MANIFEST.md").write_bytes(b"\xff\xd8\xff\xe0hidden")
            with self.assertRaisesRegex(ValueError, "image binary disguised"):
                guard.validate(self.record, directory=d)

    def test_missing_mandatory_manifest_or_tests_rejected(self):
        for name in ("MANIFEST.md", "test_validate.py"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                d = Path(temp)
                for source in guard.ALLOWED:
                    shutil.copyfile(guard.HERE / source, d / source)
                (d / name).unlink()
                with self.assertRaisesRegex(ValueError, "missing reviewed packet source"):
                    guard.validate(self.record, directory=d)

    def test_duplicate_json_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
            guard.unique_keys([("license", "CC0"), ("license", "CC BY-SA4")])


if __name__ == "__main__":
    unittest.main()
