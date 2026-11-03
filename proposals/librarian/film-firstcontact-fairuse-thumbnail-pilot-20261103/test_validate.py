#!/usr/bin/env python3
"""Hostile tests: exact film scene, bounded private pixels, contextual legal uncertainty."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, unique_keys, validate


class FilmFirstContactThumbnailPilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load()

    def changed_rejected(self, keys: list[str], value: object) -> None:
        data = copy.deepcopy(self.data)
        node = data
        for key in keys[:-1]:
            node = node[key]
        node[keys[-1]] = value
        with self.assertRaises(ValueError):
            validate(data)

    @staticmethod
    def stage(directory: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, directory / name)
        return directory

    def test_valid_held_film_photo_source(self) -> None:
        validate(self.data)

    def test_valid_temporary_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.data, directory=self.stage(Path(temp)))

    def test_false_different_film_binding_rejected(self) -> None:
        self.changed_rejected(["source_local_film_row_id"], "film:film-beyond")

    def test_false_publisher_alt_or_frame_capture_rejected(self) -> None:
        self.changed_rejected(["source_binding", "publisher_image_alt"], "Official movie poster Star Trek First Contact")
        self.changed_rejected(["source_binding", "verified_film_runtime_frame_capture"], True)

    def test_false_image_creator_and_license_rejected(self) -> None:
        self.changed_rejected(["source_binding", "individual_photographer_or_frame_author"], "A licensed photographer")
        self.changed_rejected(["source_binding", "first_party_page_is_reuse_license"], True)

    def test_variant_identity_and_pixel_hash_rejected(self) -> None:
        self.changed_rejected(["source_binding", "delivered_sha256"], "0" * 64)
        self.changed_rejected(["source_binding", "untransformed_sha256"], "0" * 64)
        self.changed_rejected(["source_binding", "delivered_bytes"], 358259)
        self.changed_rejected(["source_binding", "two_delivery_variants_are_independent_sources"], True)

    def test_excessive_thumbnail_pixels_or_dimensions_rejected(self) -> None:
        self.changed_rejected(["private_thumbnail", "actual_dimensions"], [320, 180])
        self.changed_rejected(["private_thumbnail", "max_canvas"], [1920, 1080])

    def test_excessive_thumbnail_bytes_rejected(self) -> None:
        self.changed_rejected(["private_thumbnail", "actual_bytes"], 16000)

    def test_different_small_byte_hash_rejected(self) -> None:
        self.changed_rejected(["private_thumbnail", "actual_sha256"], "0" * 64)

    def test_false_crop_claim_rejected(self) -> None:
        self.changed_rejected(["private_thumbnail", "uncropped_full_composition"], False)

    def test_actual_image_would_be_publicly_committed_rejected(self) -> None:
        self.changed_rejected(["private_thumbnail", "binary_committed_to_public_github"], True)
        self.changed_rejected(["effects", "actual_image_in_proposal"], True)

    def test_reject_missing_contextual_research(self) -> None:
        self.changed_rejected(["proposed_use", "adjacent_original_commentary"], "")

    def test_reject_missing_direct_source(self) -> None:
        self.changed_rejected(["proposed_use", "one_click_source_url"], "")

    def test_reject_absent_copyright_notice(self) -> None:
        self.changed_rejected(["proposed_use", "visible_fair_use_notice"], "")

    def test_reject_claim_source_image_licensed(self) -> None:
        self.changed_rejected(["proposed_use", "source_credit_line"], "Licensed by Paramount for our site")

    def test_reject_gallery_lightbox_or_proxy(self) -> None:
        self.changed_rejected(["proposed_use", "image_gallery_or_merchandising_use"], True)
        self.changed_rejected(["proposed_use", "full_size_lightbox_or_download"], True)
        self.changed_rejected(["proposed_use", "remote_hotlink_or_image_proxy"], True)

    def test_reject_dishonest_rights_certainty(self) -> None:
        self.changed_rejected(["legal_four_factor_review", "asserts_fair_use_legally_certain"], True)
        self.changed_rejected(["legal_four_factor_review", "asserts_license_is_always_required"], True)

    def test_reject_removal_of_market_risk(self) -> None:
        self.changed_rejected(["legal_four_factor_review", "factor_four"], "NO_MARKET_HARM")

    def test_reject_false_commercial_market_study(self) -> None:
        self.changed_rejected(["legal_four_factor_review", "rightsholder_market_study_completed"], True)

    def test_reject_false_review_done(self) -> None:
        self.changed_rejected(["legal_four_factor_review", "independent_legal_or_human_review_completed"], True)

    def test_reject_live_image_or_work_coverage(self) -> None:
        self.changed_rejected(["effects", "public_thumbnail_release"], "LIVE")
        self.changed_rejected(["effects", "main_explorer_change"], "ONE_THUMBNAIL")
        self.changed_rejected(["effects", "coverage_change"], "ONE_CLOSE_READ")
        self.changed_rejected(["effects", "global_work_resolution"], "ACCEPTED")

    def test_reject_hidden_image_in_public_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = self.stage(Path(temp))
            (directory / "still.jpeg").write_bytes(b"\xff\xd8\xff\xe0not an authorized repo image")
            with self.assertRaises(ValueError):
                validate(self.data, directory=directory)

    def test_reject_nested_rights_bait(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = self.stage(Path(temp))
            (directory / "notes").mkdir()
            (directory / "notes" / "fake.md").write_text("Unrestricted public domain film frame", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=directory)

    def test_reject_embedded_data_uri(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = self.stage(Path(temp))
            (directory / "records.json").write_text((directory / "records.json").read_text(encoding="utf-8") +
                                                     "\n![frame](data:" + "image/jpeg;base64,/9j/...)\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=directory)

    def test_reject_binary_magic_after_text_prefix(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"PK\x03\x04"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    directory = self.stage(Path(temp))
                    (directory / "MANIFEST.md").write_bytes(b"good prose first\n" + magic)
                    with self.assertRaises(ValueError):
                        validate(self.data, directory=directory)

    def test_reject_manifest_fairuse_certainty_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = self.stage(Path(temp))
            manifest = directory / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") +
                                "\nAll movie images are automatically fair use.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.data, directory=directory)

    def test_reject_duplicate_key(self) -> None:
        with self.assertRaises(ValueError):
            unique_keys([("rights", "UNKNOWN"), ("rights", "PUBLIC")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
