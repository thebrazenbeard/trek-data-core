#!/usr/bin/env python3
"""Hostile tests deny image identity, provenance, rights and release inflation."""

from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from validate import RECORD, load_packet, validate, no_duplicate_keys


class FirstPartyEpisodeStillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load_packet()

    def mutation_rejected(self, key: str, value: object, *, at_root: bool = False) -> None:
        mutated = copy.deepcopy(self.packet)
        target = mutated if at_root else mutated["candidate"]
        target[key] = value
        with self.assertRaises(ValueError):
            validate(mutated)

    def test_valid_held_packet(self) -> None:
        validate(self.packet)

    def test_no_public_thumbnail_release(self) -> None:
        self.mutation_rejected("editorial_display_admission", "PUBLICLY_DISPLAYABLE")

    def test_no_invented_open_license(self) -> None:
        self.mutation_rejected("license_state", "CC_BY_PUBLIC_REUSE_PERMITTED")

    def test_no_assumed_named_photographer(self) -> None:
        self.mutation_rejected("primary_photo_photographer", "Michael Gibson")

    def test_no_mislabeled_photo_as_broadcast_frame(self) -> None:
        self.mutation_rejected("primary_photo_class", "BROADCAST_SCREENSHOT_VERIFIED")

    def test_no_unproven_cross_gallery_join(self) -> None:
        self.mutation_rejected("gallery_proves_this_exact_photo_is_in_gallery", True)

    def test_no_alt_scene_substitution(self) -> None:
        self.mutation_rejected("primary_photo_alt", "Spock on the planet Vulcan in episode 201")

    def test_no_coveraged_episode(self) -> None:
        self.mutation_rejected("coverage_effect", "ONE_EPISODE_CLOSE_READ", at_root=True)

    def test_no_source_work_identity_elevation(self) -> None:
        self.mutation_rejected("source_work_admission_effect", "ADMITTED", at_root=True)

    def test_no_image_binary_commit_flag(self) -> None:
        self.mutation_rejected("image_bytes_committed", True, at_root=True)

    def test_no_wrong_image_digest(self) -> None:
        self.mutation_rejected("photo_bytes_sha256", "0" * 64)

    def test_no_press_portal_geoblock_evasion_claim(self) -> None:
        self.mutation_rejected("press_portal_read_state", "FULL_RIGHTS_DOC_RETRIEVED")

    def test_no_duplicate_json_keys(self) -> None:
        with self.assertRaises(ValueError):
            no_duplicate_keys([("a", 1), ("a", 2)])

    def test_no_nested_image_binary(self) -> None:
        with tempfile.TemporaryDirectory(dir=RECORD.parent) as directory:
            nested = Path(directory) / "subfolder"
            nested.mkdir()
            (nested / "photo.png").write_bytes(b"not the real image")
            with self.assertRaises(ValueError):
                validate(self.packet)

    def test_no_disguised_binary(self) -> None:
        with tempfile.TemporaryDirectory(dir=RECORD.parent) as directory:
            (Path(directory) / "rights.dat").write_bytes(b"\xff\xd8\xff" + b"bad")
            with self.assertRaises(ValueError):
                validate(self.packet)


if __name__ == "__main__":
    unittest.main(verbosity=2)
