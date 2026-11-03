#!/usr/bin/env python3
"""Adversarial nonrelease tests for one exact 159x120 fair-use research thumbnail."""

from __future__ import annotations

import copy
from pathlib import Path
import shutil
import tempfile
import unittest

from validate import FILES, HERE, load, unique_keys, validate


class TasFairUsePilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = load()

    def altered_rejected(self, keys: list[str], value: object) -> None:
        record = copy.deepcopy(self.record)
        cur = record
        for key in keys[:-1]:
            cur = cur[key]
        cur[keys[-1]] = value
        with self.assertRaises(ValueError):
            validate(record)

    @staticmethod
    def stage(where: Path) -> Path:
        for name in FILES:
            shutil.copyfile(HERE / name, where / name)
        return where

    def test_valid_held_proposal(self) -> None:
        validate(self.record)

    def test_clean_staged_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            validate(self.record, directory=self.stage(Path(temp)))

    def test_reject_larger_thumbnail_width(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "width"], 320)

    def test_reject_larger_thumbnail_height(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "height"], 240)

    def test_reject_larger_byte_payload(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "size_bytes"], 200_000)

    def test_reject_excessive_configured_canvas(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "reference_canvas_max_width"], 640)

    def test_reject_wrong_derived_image_hash(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "sha256"], "0" * 64)

    def test_reject_crop(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "no_crop"], False)

    def test_reject_publisher_original_mismatch(self) -> None:
        self.altered_rejected(["source_binding", "input_embedded_variant_sha256"], "0" * 64)
        self.altered_rejected(["source_binding", "untransformed_same_path_size_bytes"], 187263)

    def test_reject_fake_episode_or_publisher_caption(self) -> None:
        self.altered_rejected(["source_local_episode_row_id"], "lead:0020")
        self.altered_rejected(["source_binding", "article_image_alt"], "Unlicensed official Paramount portrait")

    def test_reject_missing_original_research_context(self) -> None:
        self.altered_rejected(["proposed_presentation", "surrounding_critical_text"], "")

    def test_reject_missing_source_link(self) -> None:
        self.altered_rejected(["proposed_presentation", "linked_target"], "")

    def test_reject_missing_nonendorsement_notice(self) -> None:
        self.altered_rejected(["proposed_presentation", "visible_copyright_fair_use_notice"], "")

    def test_reject_full_original_download_lightbox(self) -> None:
        self.altered_rejected(["proposed_presentation", "access_to_original_quality"], "FULL_SIZE_DOWNLOAD")

    def test_reject_source_hotlinking(self) -> None:
        self.altered_rejected(["proposed_presentation", "automatic_hotlinking_or_proxy"], True)

    def test_reject_screenshot_gallery_purpose(self) -> None:
        self.altered_rejected(["proposed_presentation", "purpose"], "DECORATIVE_TREK_GALLERY")

    def test_reject_omitted_adverse_factors(self) -> None:
        self.altered_rejected(["legal_review", "factor_2_nature_creative"], "NEUTRAL")
        self.altered_rejected(["legal_review", "factor_4_market_effect"], "NO_HARM_PROVED")

    def test_reject_false_universal_fair_use(self) -> None:
        self.altered_rejected(["legal_review", "claim_of_categorical_fair_use"], True)

    def test_reject_release_or_coverage_claims(self) -> None:
        self.altered_rejected(["admission", "public_image_release"], "LIVE")
        self.altered_rejected(["admission", "main_explorer_change"], "ONE_NEW_IMAGE")
        self.altered_rejected(["admission", "coverage_change"], "CLOSE_READ")

    def test_reject_committed_copyright_pixels(self) -> None:
        self.altered_rejected(["local_pilot_thumbnail", "derivative_binary_in_public_repo"], True)
        with tempfile.TemporaryDirectory() as temp:
            where = self.stage(Path(temp))
            (where / "source-frame.jpg").write_bytes(b"\xff\xd8\xff\xe0test")
            with self.assertRaises(ValueError):
                validate(self.record, directory=where)

    def test_reject_nested_rights_assertion_or_data_uri(self) -> None:
        for text in ("licensed public-domain TAS screenshot", "![frame](data:" + "image/jpeg;base64,/9j...)"):
            with self.subTest(text=text):
                with tempfile.TemporaryDirectory() as temp:
                    where = self.stage(Path(temp))
                    (where / "notes").mkdir()
                    (where / "notes" / "unreviewed.md").write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validate(self.record, directory=where)

    def test_reject_binary_magic_after_text_prefix(self) -> None:
        for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"PK\x03\x04"):
            with self.subTest(magic=repr(magic)):
                with tempfile.TemporaryDirectory() as temp:
                    where = self.stage(Path(temp))
                    (where / "notes").mkdir()
                    (where / "notes" / "stowaway.txt").write_bytes(b"cover text\n" + magic)
                    with self.assertRaises(ValueError):
                        validate(self.record, directory=where)

    def test_reject_manifest_legality_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            where = self.stage(Path(temp))
            manifest = where / "MANIFEST.md"
            manifest.write_text(manifest.read_text(encoding="utf-8") +
                                "\nAll copyrighted screenshots are automatically fair use.\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.record, directory=where)

    def test_duplicate_json_keys(self) -> None:
        with self.assertRaises(ValueError):
            unique_keys([("factor_4", "UNKNOWN"), ("factor_4", "FAVOR")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
