#!/usr/bin/env python3
"""Hostile mutation tests for the one-image source packet."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from validate import ROOT, RECORD, read_json, validate, unique_pairs


class TestArenaMuseumCustody(unittest.TestCase):
    def setUp(self) -> None:
        self.original = read_json(RECORD)

    def test_exact_packet(self) -> None:
        validate(self.original)

    def reject(self, key: str, forged: object, *, root: bool = False) -> None:
        modified = copy.deepcopy(self.original)
        target = modified if root else modified["candidate"]
        target[key] = forged
        with self.assertRaises(ValueError):
            validate(modified)

    def test_fail_bad_artifact_claim(self) -> None:
        self.reject("depicted_artifact_status", "ORIGINAL_GORN_FILMING_PROP_CERTIFIED")

    def test_fail_wrong_exif_rotation(self) -> None:
        self.reject("image_exif_orientation", "EXIF_8_ROTATED_90_DEGREES_CW")

    def test_fail_fake_screen_frame_alt(self) -> None:
        self.reject("proposed_alt", "Frame from the Arena episode showing Kirk fighting the Gorn in a museum case")

    def test_fail_fake_behind_scenes_caption(self) -> None:
        self.reject("proposed_caption", "Original on-set behind-the-scenes Gorn costume from Arena, 1967")

    def test_fail_episode_identity_admission(self) -> None:
        self.reject("episode_identity_state", "CANONICAL_EPISODE_ID_CONFIRMED")

    def test_fail_license_scope_inflation(self) -> None:
        self.reject("license_scope", "CC_FULLY_CLEARS_ALL_STUDIO_COSTUME_RIGHTS")

    def test_fail_unheld_display(self) -> None:
        self.reject("editorial_display_admission", "RELEASED_IN_EXPLORER")

    def test_fail_claimed_catalog_coverage(self) -> None:
        self.reject("coverage_effect", "ONE_EPISODE_ANALYZED", root=True)

    def test_fail_changed_sha256(self) -> None:
        self.reject("original_image_sha256", "0" * 64)

    def test_fail_changed_source(self) -> None:
        self.reject("commons_pinned_revision", "https://commons.wikimedia.org/wiki/SomeOtherFile")

    def test_fail_modified_accepted_main(self) -> None:
        self.reject("accepted_main", "0" * 40, root=True)

    def test_fail_floating_image_binary_status(self) -> None:
        self.reject("image_bytes_committed", True, root=True)

    def test_fail_duplicate_json_keys(self) -> None:
        with self.assertRaises(ValueError):
            unique_pairs([("held", True), ("held", False)])

    def test_fail_unexpected_fields(self) -> None:
        modified = copy.deepcopy(self.original)
        modified["candidate"]["fictional_episode_scene"] = "Arena"
        with self.assertRaises(ValueError):
            validate(modified)

    def test_fail_nested_jpeg_upload(self) -> None:
        with tempfile.TemporaryDirectory(dir=RECORD.parent) as directory:
            nested = Path(directory) / "screenshot"
            nested.mkdir()
            (nested / "episode.jpg").write_bytes(b"\xff\xd8\xff" + b"not a real scene")
            with self.assertRaises(ValueError):
                validate(self.original)

    def test_fail_disguised_binary(self) -> None:
        with tempfile.TemporaryDirectory(dir=RECORD.parent) as directory:
            (Path(directory) / "ordinary.dat").write_bytes(b"\xff\xd8\xff" + b"disguised")
            with self.assertRaises(ValueError):
                validate(self.original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
