#!/usr/bin/env python3
"""Adversarial checks for unpublished photographer-credited Discovery photo proposal."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, unique_keys, validate


class DiscoveryRedAngelVisualTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load()

    def mutated_rejected(self, path: list[str], value: object) -> None:
        data = copy.deepcopy(self.data)
        cursor = data
        for k in path[:-1]:
            cursor = cursor[k]
        cursor[path[-1]] = value
        with self.assertRaises(ValueError):
            validate(data)

    @staticmethod
    def stage(dest: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, dest / name)
        return dest

    def test_valid_held_packet(self) -> None:
        validate(self.data)

    def test_valid_staged_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.data, directory=self.stage(Path(temp)))

    def test_false_accepted_episode_row_rejected(self) -> None:
        self.mutated_rejected(["accepted_episode_row_for_this_title"], "publisher:discovery:s2:009")

    def test_false_global_identity_or_coverage_rejected(self) -> None:
        self.mutated_rejected(["identity_or_coverage_effect"], "WORK_ADMITTED")
        self.mutated_rejected(["protected_effects", "episode_coverage"], "CLOSE_READ")

    def test_wrong_episode_and_source_page_rejected(self) -> None:
        self.mutated_rejected(["source_local_episode_title"], "Such Sweet Sorrow")
        self.mutated_rejected(["publisher_source", "article_url"], "https://example.org/wrong-episode")

    def test_wrong_photo_credit_rejected(self) -> None:
        self.mutated_rejected(["publisher_source", "image_credit_exact"], "Public domain official episode screenshot")
        self.mutated_rejected(["publisher_source", "image_creator_credit"], "UNKNOWN")

    def test_faked_broadcast_still_rejected(self) -> None:
        self.mutated_rejected(["publisher_source", "image_role"], "VERIFIED_AIRDATE_VIDEO_FRAME")

    def test_exact_delivery_source_sha_bytes_rejected(self) -> None:
        self.mutated_rejected(["publisher_source", "delivery_sha256"], "0" * 64)
        self.mutated_rejected(["publisher_source", "delivery_bytes"], 80965)

    def test_exact_raw_source_sha_bytes_rejected(self) -> None:
        self.mutated_rejected(["publisher_source", "no_query_sha256"], "0" * 64)
        self.mutated_rejected(["publisher_source", "no_query_bytes"], 68247)

    def test_publisher_image_is_not_a_license(self) -> None:
        self.mutated_rejected(["publisher_source", "publisher_page_is_public_reuse_license"], True)

    def test_one_image_not_two_independent_sources(self) -> None:
        self.mutated_rejected(["publisher_source", "delivery_variants_are_independent_witnesses"], True)

    def test_larger_dimensions_or_canvas_rejected(self) -> None:
        self.mutated_rejected(["local_thumbnail", "actual_dimensions"], [320, 214])
        self.mutated_rejected(["local_thumbnail", "canvas_max"], [320, 220])

    def test_oversize_bytes_or_changed_digest_rejected(self) -> None:
        self.mutated_rejected(["local_thumbnail", "actual_bytes"], 10000)
        self.mutated_rejected(["local_thumbnail", "actual_sha256"], "0" * 64)

    def test_false_cropped_frame_rejected(self) -> None:
        self.mutated_rejected(["local_thumbnail", "uncropped"], False)

    def test_no_private_picture_goes_to_public_github(self) -> None:
        self.mutated_rejected(["local_thumbnail", "thumbnail_pixels_in_public_repo"], True)
        self.mutated_rejected(["local_thumbnail", "publisher_pixels_in_public_repo"], True)

    def test_no_explorer_published_thumbnail(self) -> None:
        self.mutated_rejected(["protected_effects", "explorer_change"], "PUBLIC_THUMBNAIL")
        self.mutated_rejected(["protected_effects", "publication"], "LIVE")

    def test_visible_original_research_context_required(self) -> None:
        self.mutated_rejected(["hypothetical_presentation", "adjacent_original_analysis"], "")

    def test_official_article_link_required(self) -> None:
        self.mutated_rejected(["hypothetical_presentation", "source_link"], "")

    def test_photo_credit_and_fair_use_notice_required(self) -> None:
        self.mutated_rejected(["hypothetical_presentation", "attribution"], "")
        self.mutated_rejected(["hypothetical_presentation", "notice"], "")

    def test_no_mass_promotional_episode_gallery(self) -> None:
        self.mutated_rejected(["hypothetical_presentation", "gallery_or_promotional_decoration"], True)
        self.mutated_rejected(["hypothetical_presentation", "full_episodic_article_images_mass_ingestion"], True)

    def test_no_high_res_hotlink_or_proxy(self) -> None:
        self.mutated_rejected(["hypothetical_presentation", "original_resolution_hotlink_proxy_or_lightbox"], True)

    def test_ambiguous_legal_market_must_stay_unresolved(self) -> None:
        self.mutated_rejected(["four_factor_review", "factor_four"], "NO_MARKET_HARM")
        self.mutated_rejected(["four_factor_review", "copyright_market_review_completed"], True)

    def test_critical_fair_use_factors_cannot_disappear(self) -> None:
        self.mutated_rejected(["four_factor_review", "factor_one"], "EDUCATIONAL_ALWAYS_FAIR")
        self.mutated_rejected(["four_factor_review", "factor_two"], "PUBLIC_DOMAIN_FICTIONAL_IMAGE")

    def test_independent_rights_review_not_faked(self) -> None:
        self.mutated_rejected(["four_factor_review", "independent_fair_use_review_completed"], True)
        self.mutated_rejected(["four_factor_review", "claim_automatic_legal_fair_use"], True)

    def test_hidden_jpeg_or_png_rejected(self) -> None:
        for name, magic in (("frame.jpg", b"\xff\xd8\xff\xe0"), ("frame.png", b"\x89PNG\r\n\x1a\n")):
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as temp:
                    folder = self.stage(Path(temp))
                    (folder / name).write_bytes(magic + b"unauthorized image")
                    with self.assertRaises(ValueError):
                        validate(self.data, directory=folder)

    def test_nested_fake_rights_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            folder = self.stage(Path(temp))
            (folder / "hidden").mkdir()
            (folder / "hidden" / "claim.md").write_text("Licensed public domain Star Trek photos", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=folder)

    def test_embed_uri_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            folder = self.stage(Path(temp))
            manifest = folder / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") + "\n![screenshot](data:" +
                                "image/jpeg;base64,/9j/...)\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=folder)

    def test_binary_magic_after_text_prefix_denied(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"PK\x03\x04"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    folder = self.stage(Path(temp))
                    (folder / "MANIFEST.md").write_bytes(b"good text first\n" + magic)
                    with self.assertRaises(ValueError):
                        validate(self.data, directory=folder)

    def test_manifest_false_license_denied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            folder = self.stage(Path(temp))
            manifest = folder / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") +
                                "\nThis credit grants unrestricted reuse.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=folder)

    def test_duplicate_json_key_denied(self) -> None:
        with self.assertRaises(ValueError):
            unique_keys([("permission", "HELD"), ("permission", "GRANTED")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
