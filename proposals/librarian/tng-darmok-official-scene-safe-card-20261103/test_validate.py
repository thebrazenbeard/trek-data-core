#!/usr/bin/env python3
"""Red/green tests for first-party episode still identity and no-image placeholder."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, no_duplicate_keys, validate


class DarmokVisualPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load()

    def mutation_rejected(self, path: list[str], value: object) -> None:
        altered = copy.deepcopy(self.packet)
        record = altered
        for item in path[:-1]:
            record = record[item]
        record[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(altered)

    @staticmethod
    def staged(directory: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, directory / name)
        return directory

    def test_exact_held_source_packet_passes(self) -> None:
        validate(self.packet)

    def test_exact_held_source_packet_staged_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.packet, directory=self.staged(Path(temp)))

    def test_release_claim_cannot_change(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "public_image_display_admission"], "PUBLIC")

    def test_cannot_invent_press_express_authorized_user(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "press_express_authorized_user_status"], "AUTHORIZED")

    def test_cannot_call_publisher_image_broadcast_frame(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "verified_broadcast_frame"], True)

    def test_cannot_invent_photographer(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "individual_photographer"], "Unknown publicity photographer")

    def test_cannot_invent_public_license_from_cors(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "cors_or_cache_headers_are_copyright_license"], True)

    def test_official_image_hash_is_pinned(self) -> None:
        self.mutation_rejected(["actual_scene_candidate", "image_sha256"], "0" * 64)

    def test_no_accepted_work_or_coverage_inflation(self) -> None:
        self.mutation_rejected(["global_work_admission_effect"], "ONE_WORK_ADMITTED")
        self.mutation_rejected(["coverage_effect"], "ONE_EPISODE_CLOSE_READ")

    def test_no_public_explorer_effect(self) -> None:
        self.mutation_rejected(["explorer_effect"], "PUBLIC_THUMBNAIL")

    def test_no_real_scene_pixels_in_placeholder(self) -> None:
        self.mutation_rejected(["safe_placeholder", "contains_official_episode_pixels"], True)

    def test_duplicate_metadata_keys_rejected(self) -> None:
        with self.assertRaises(ValueError):
            no_duplicate_keys([("license", "HELD"), ("license", "PUBLIC")])

    def test_nested_data_uri_image_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            staged = self.staged(Path(temp))
            nested = staged / "payload"
            nested.mkdir()
            (nested / "notes.md").write_text("![" + "still](data:" + "image/jpeg;base64,/9j/...)",
                                             encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=staged)

    def test_nested_false_public_domain_caption_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            staged = self.staged(Path(temp))
            nested = staged / "payload"
            nested.mkdir()
            (nested / "notes.md").write_text("unrestricted public-domain screenshot of TNG Darmok",
                                             encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=staged)

    def test_nested_jpeg_or_png_after_text_is_rejected(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    staged = self.staged(Path(temp))
                    nested = staged / "payload"
                    nested.mkdir()
                    (nested / "notes.md").write_bytes(b"benign preface\n" + magic + b"binary")
                    with self.assertRaises(ValueError):
                        validate(self.packet, directory=staged)

    def test_unreviewed_replacement_card_remote_media_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            staged = self.staged(Path(temp))
            card = staged / "title-card.svg"
            card.write_text(card.read_text(encoding="utf-8")
                            + "\n<image href='https://images.example.org/held-scene.jpg'/>\n",
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=staged)

    def test_unreviewed_manifest_permission_assertion_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            staged = self.staged(Path(temp))
            manifest = staged / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\npublic domain screenshot\n",
                                encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=staged)

    def test_unreviewed_direct_image_file_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            staged = self.staged(Path(temp))
            (staged / "still.jpg").write_bytes(b"\xff\xd8\xff" + b"fake")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=staged)


if __name__ == "__main__":
    unittest.main(verbosity=2)
