"""Synthetic negative checks: source metadata is not a display grant."""
from __future__ import annotations

import copy
import unittest

from validate import load, validate


class HeldPicardSourceTests(unittest.TestCase):
    def setUp(self):
        self.packet = load()

    def test_unchanged_is_proposal_only(self):
        self.assertEqual(validate(self.packet), {"candidate_count": 1, "admitted": 0, "public_images": 0})

    def test_release_promotion_rejected(self):
        for key, value in (
            ("public_display_effect", "LIVE"), ("admission_effect", "SOURCE_BOUND"),
            ("image_binary_in_repository", True), ("image_binary_in_repository", 0),
        ):
            with self.subTest(key=key):
                bad = copy.deepcopy(self.packet)
                bad[key] = value
                with self.assertRaises(ValueError):
                    validate(bad)

    def test_forged_work_and_character_identity_rejected(self):
        for key, value in (("work_or_episode_row_id", "picard-1x01"), ("character_identity_inferred", True)):
            bad = copy.deepcopy(self.packet)
            bad["candidates"][0][key] = value
            with self.assertRaises(ValueError):
                validate(bad)

    def test_forged_photo_source_rejected(self):
        for key, value in (
            ("photographer", "Paramount"),
            ("commons_pinned_oldid", 1234567890),
            ("original_jpeg_sha1_claim", "0" * 40),
            ("commons_file_title", "File:Star Trek Picard S01E01.jpg"),
            ("public_image_url", "https://example.org/shot.jpg"),
        ):
            bad = copy.deepcopy(self.packet)
            bad["candidates"][0][key] = value
            with self.assertRaises(ValueError):
                validate(bad)

    def test_extra_fields_rejected(self):
        bad = copy.deepcopy(self.packet)
        bad["candidates"][0]["claimed_scene"] = "Picard pilot"
        with self.assertRaises(ValueError):
            validate(bad)


if __name__ == "__main__":
    unittest.main()
