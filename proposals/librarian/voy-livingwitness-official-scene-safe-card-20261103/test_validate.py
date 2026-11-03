#!/usr/bin/env python3
"""Adversarial checks prevent false rights, source identity, or hidden image release."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, unique_keys, validate


class VoyagerLivingWitnessVisualTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load()

    def altered_rejected(self, path: list[str], value: object) -> None:
        test = copy.deepcopy(self.packet)
        node = test
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(test)

    @staticmethod
    def stage(dest: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, dest / name)
        return dest

    def test_held_source_packet(self) -> None:
        validate(self.packet)

    def test_clean_staged_source_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.packet, directory=self.stage(Path(temp)))

    def test_false_public_display_rights(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "public_image_display_admission"], "PUBLIC")

    def test_false_authorized_press_express_user(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "press_express_authorized_user_status"], "AUTHORIZED")

    def test_false_broadcast_frame(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "verified_broadcast_frame"], True)

    def test_false_photographer(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "individual_photographer"], "Known creator")

    def test_false_derived_independence(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "image_variants_independent_witnesses"], True)

    def test_exact_publisher_embedded_and_untransformed_hashes(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "publisher_embedded_image_sha256"], "0" * 64)
        self.altered_rejected(["actual_scene_candidate", "same_path_untransformed_sha256"], "0" * 64)
        self.altered_rejected(["actual_scene_candidate", "publisher_embedded_image_bytes"], 114509)

    def test_exact_publisher_caption_cannot_be_faked(self) -> None:
        self.altered_rejected(["actual_scene_candidate", "publisher_image_alt"],
                              "Public-domain screenshot of Voyager's Doctor")

    def test_no_explorer_work_or_coverage_promotion(self) -> None:
        self.altered_rejected(["explorer_effect"], "ONE_NEW_THUMBNAIL")
        self.altered_rejected(["coverage_effect"], "ONE_EPISODE_CLOSE_READ")
        self.altered_rejected(["global_work_admission_effect"], "ONE_WORK_ADMITTED")

    def test_no_official_pixels_in_original_card(self) -> None:
        self.altered_rejected(["safe_placeholder", "contains_official_episode_pixels"], True)

    def test_duplicate_keys_denied(self) -> None:
        with self.assertRaises(ValueError):
            unique_keys([("state", "HELD"), ("state", "PUBLIC")])

    def test_nested_image_uri_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            (stage / "notes").mkdir()
            (stage / "notes" / "image.md").write_text("![" + "still](data:" + "image/jpeg;base64,/9j/...)",
                                                      encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_nested_fake_public_domain_caption_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            (stage / "notes").mkdir()
            (stage / "notes" / "license.md").write_text("unrestricted public-domain Voyager episode screenshot",
                                                        encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_jpeg_png_magic_after_text_prefix_denied(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    stage = self.stage(Path(temp))
                    (stage / "notes").mkdir()
                    (stage / "notes" / "payload.md").write_bytes(b"hello world\n" + magic)
                    with self.assertRaises(ValueError):
                        validate(self.packet, directory=stage)

    def test_replacement_svg_external_asset_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            svg = stage / "title-card.svg"
            svg.write_text(svg.read_text(encoding="utf-8") + "\n<image href='https://cdn.example.org/scene.jpg'/>\n",
                           encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_manifest_rewrite_false_license_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            manifest = stage / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\npublic domain screenshot\n",
                                encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)


if __name__ == "__main__":
    unittest.main(verbosity=2)
