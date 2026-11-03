#!/usr/bin/env python3
"""Falsifiers for NASA photograph source identity and publication guard."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import validate as guard


class TestNasaPhotoCrosswalk(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = guard.read_json(guard.PACKET)

    def test_exact_source_packet_passes(self) -> None:
        guard.validate(self.packet)

    def test_packet_has_no_image_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "image.jpg").touch()
            with self.assertRaisesRegex(ValueError, "image binary"):
                guard.validate(self.packet, directory=directory)

    def test_rejects_any_changed_source_or_release_field(self) -> None:
        falsifiers = (
            ("nasa_exact_jpeg_sha256", "0" * 64),
            ("nasa_exact_jpeg_bytes", 1234),
            ("nasa_exact_jpeg_url", "https://example.test/photo.jpg"),
            ("flickr_image_number", "FAKE-ID"),
            ("flickr_rights_label_meaning", "UNRESTRICTED_PUBLIC_DOMAIN_LICENSE"),
            ("crosswalk_relation", "CRYPTOGRAPHICALLY_IDENTICAL"),
            ("individual_photographer", "Invented Photographer"),
            ("individual_photographer", "NASA"),
            ("photographer_rights_cleared", True),
            ("public_display_eligible", True),
            ("independent_photo_specific_rights_review", "PASSED"),
            ("independent_design_review", "PASSED"),
            ("release_authorization", "GRANTED"),
            ("image_binaries_included", 1),
            ("fictional_episode_or_film_artwork", True),
            ("research_or_coverage_admission", "ACCEPTED"),
            ("site_effect", "PUBLISHED"),
            ("factual_editorial_caption", "Official Star Trek episode still"),
            ("adjacent_credit", "NASA endorses this fan site"),
            ("open_falsifiers", []),
        )
        for key, forged in falsifiers:
            with self.subTest(key=key, forged=forged):
                mutant = copy.deepcopy(self.packet)
                mutant[key] = forged
                with self.assertRaises(ValueError):
                    guard.validate(mutant)

    def test_rejects_extra_claims_or_missing_field(self) -> None:
        mutant = copy.deepcopy(self.packet)
        mutant["rights_cleared"] = True
        with self.assertRaises(ValueError):
            guard.validate(mutant)
        mutant = copy.deepcopy(self.packet)
        mutant.pop("individual_photographer")
        with self.assertRaises(ValueError):
            guard.validate(mutant)

    def test_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "packet.json"
            path.write_text('{"status":"HOLD","status":"RELEASED"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                guard.read_json(path)

    def test_rejects_wrong_binary_signature_even_if_named_jpeg(self) -> None:
        with self.assertRaisesRegex(ValueError, "JPEG size"):
            guard.validate_source_bytes(b"not a photograph")

    def test_rejects_corrupt_jpeg_markers(self) -> None:
        with self.assertRaisesRegex(ValueError, "not a JPEG"):
            guard.jpeg_dimensions(b"PNG placeholder")
        with self.assertRaisesRegex(ValueError, "invalid JPEG segment length"):
            guard.jpeg_dimensions(b"\xff\xd8\xff\xe0\xff\xff----")


if __name__ == "__main__":
    unittest.main()
