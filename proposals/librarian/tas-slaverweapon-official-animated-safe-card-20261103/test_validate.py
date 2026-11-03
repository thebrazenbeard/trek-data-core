#!/usr/bin/env python3
"""Hostile regressions for an episode-scene source-link, not image publication."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, unique_keys, validate


class TasSlaverWeaponVisualTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = load()

    def altered_rejected(self, path: list[str], value: object) -> None:
        packet = copy.deepcopy(self.packet)
        node = packet
        for item in path[:-1]:
            node = node[item]
        node[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(packet)

    @staticmethod
    def stage(where: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, where / name)
        return where

    def test_held_packet(self) -> None:
        validate(self.packet)

    def test_clean_staged_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.packet, directory=self.stage(Path(temp)))

    def test_rights_false_public_display_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "public_image_display_admission"],
                              "PUBLIC_GRANTED")

    def test_false_press_user_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "press_express_authorized_user_status"],
                              "AUTHORIZED")

    def test_false_grant_from_press_terms_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "press_express_terms_apply_as_grant_to_this_article_image"],
                              True)

    def test_false_broadcast_extract_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "verified_broadcast_frame_extraction"], True)

    def test_false_animated_still_artist_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "individual_still_artist_or_frame_extract_author"],
                              "Animator 1")

    def test_false_independent_image_variants_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "image_variants_independent_witnesses"], True)

    def test_exact_publisher_alt_caption_denied(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "publisher_image_alt"],
                              "Public domain screenshot of The Slaver Weapon")

    def test_source_url_hash_bytes_locked(self) -> None:
        self.altered_rejected(["actual_animated_scene_candidate", "publisher_embedded_image_sha256"], "0" * 64)
        self.altered_rejected(["actual_animated_scene_candidate", "same_path_untransformed_sha256"], "0" * 64)
        self.altered_rejected(["actual_animated_scene_candidate", "publisher_embedded_image_bytes"], 480836)
        self.altered_rejected(["actual_animated_scene_candidate", "same_path_untransformed_url"],
                              "https://example.org/not-a-source.png")

    def test_source_identity_cannot_change(self) -> None:
        self.altered_rejected(["source_local_episode_row_id"], "lead:0020")
        self.altered_rejected(["source_local_episode_title"], "Yesteryear")

    def test_publication_and_coverage_effects_denied(self) -> None:
        self.altered_rejected(["explorer_effect"], "PUBLIC_EPISODE_THUMBNAIL")
        self.altered_rejected(["coverage_effect"], "CLOSE_READ")
        self.altered_rejected(["global_work_admission_effect"], "ONE_NEW_WORK")
        self.altered_rejected(["image_binary_committed"], True)

    def test_original_card_cannot_be_relabelled_frame(self) -> None:
        self.altered_rejected(["safe_placeholder", "visible_nonframe_label"], "OFFICIAL SCENE")
        self.altered_rejected(["safe_placeholder", "contains_official_episode_pixels"], True)
        self.altered_rejected(["safe_placeholder", "contains_publisher_artwork"], True)

    def test_json_duplicate_keys_denied(self) -> None:
        with self.assertRaises(ValueError):
            unique_keys([("license", "HELD"), ("license", "PUBLIC")])

    def test_nested_data_image_uri_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            (stage / "notes").mkdir()
            (stage / "notes" / "scene.md").write_text("![frame](data:" + "image/jpeg;base64,/9j/...)",
                                                      encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_nested_false_public_domain_caption_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            (stage / "notes").mkdir()
            (stage / "notes" / "license.md").write_text("unrestricted public-domain TAS screenshot",
                                                        encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_binary_magic_hidden_after_text_prefix_denied(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"PK\x03\x04"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    stage = self.stage(Path(temp))
                    (stage / "notes").mkdir()
                    (stage / "notes" / "payload.md").write_bytes(b"hello world\n" + magic)
                    with self.assertRaises(ValueError):
                        validate(self.packet, directory=stage)

    def test_replaced_svg_external_asset_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            card = stage / "title-card.svg"
            card.write_text(card.read_text(encoding="utf-8") +
                            "\n<image href='https://example.org/scene.jpg'/>\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)

    def test_manifest_false_license_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stage = self.stage(Path(temp))
            manifest = stage / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") +
                                "\nUnrestricted public-domain episode screenshot.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.packet, directory=stage)


if __name__ == "__main__":
    unittest.main(verbosity=2)
