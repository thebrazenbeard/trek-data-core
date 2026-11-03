#!/usr/bin/env python3
"""Adversarial license, caption, source and media-publication tests."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import validate as guard


class BeyondPremiereTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = guard.read_json(guard.CONTRACT)

    def test_exact_packet_passes_with_release_on_hold(self):
        self.assertEqual(guard.validate(self.contract), 4)

    def test_false_fiction_or_eligibility_claims_rejected(self):
        for key, value in (
            ("public_image_display_authorized", True),
            ("fictional_film_still_or_poster", True),
            ("scene_or_episode_truth_claim", True),
            ("work_or_coverage_admission", "COMPLETE"),
            ("preopt_image_requests", 1),
            ("image_bytes_committed", 1),
            ("site_effect", "PUBLIC"),
            ("caption", "Star Trek Beyond movie scene"),
            ("proposed_caption", "Star Trek Beyond official film frame"),
            ("license", "CC0"),
            ("photographer", "unknown"),
            ("original_image_sha256", "0" * 64),
            ("credit_template", "NASA owns this work"),
        ):
            with self.subTest(key=key):
                packet = copy.deepcopy(self.contract)
                packet[key] = value
                with self.assertRaises(ValueError):
                    guard.validate(packet)

    def test_forged_rights_reviewer_pass_fails(self):
        for key in guard.EXPECTED_REVIEWS:
            with self.subTest(key=key):
                packet = copy.deepcopy(self.contract)
                packet["independent_reviews"][key] = "GO"
                with self.assertRaises(ValueError):
                    guard.validate(packet)

    def test_manifest_misinformation_is_digest_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            source = (guard.HERE / "MANIFEST.md").read_text(encoding="utf-8")
            (d / "MANIFEST.md").write_text(source + "\nOfficial Paramount film screenshot; public domain!\n")
            with self.assertRaisesRegex(ValueError, "MANIFEST digest"):
                guard.validate(self.contract, directory=d)

    def test_markdown_or_html_embedded_remote_image_rejected(self):
        for markup in (
            "!" + "[image](https://upload.wikimedia.org/wikipedia/commons/test.jpg)",
            "<" + "picture>" + "<" + "source srcset='https://test.invalid/img.jpg'>",
            "# " + "data:" + "image/jpeg;base64,AAA",
        ):
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / "validate.py").write_text(markup, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "embedded/external active image"):
                    guard.validate(self.contract, directory=d)

    def test_nested_image_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "hidden").mkdir()
            (d / "hidden" / "photo.jpg").write_bytes(b"unreviewed")
            with self.assertRaises(ValueError):
                guard.validate(self.contract, directory=d)
            (d / "hidden" / "photo.jpg").unlink()
            (d / "hidden" / "out").symlink_to(d.parent / "outside.jpg")
            with self.assertRaises(ValueError):
                guard.validate(self.contract, directory=d)

    def test_image_binary_in_text_extension_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "MANIFEST.md").write_bytes(b"\xff\xd8\xff\xe0FAKE")
            with self.assertRaisesRegex(ValueError, "image/binary magic"):
                guard.validate(self.contract, directory=d)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            guard.unique_json([("license", "CC0"), ("license", "CC BY")])

    def test_missing_manifest_or_test_source_rejected(self):
        for missing in ("MANIFEST.md", "test_validate.py"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                for name in guard.ALLOWED:
                    shutil.copyfile(guard.HERE / name, d / name)
                (d / missing).unlink()
                with self.assertRaisesRegex(ValueError, "missing reviewed packet source"):
                    guard.validate(self.contract, directory=d)


if __name__ == "__main__":
    unittest.main()
