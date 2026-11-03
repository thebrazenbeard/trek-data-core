#!/usr/bin/env python3
"""Release-gate falsifiers and nonpublishing packet guarantees."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import validate as guard


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = guard.read_json(guard.PACKET)

    def test_held_contract_no_release(self):
        self.assertEqual(len(guard.validate(self.contract)), 6)

    def test_forged_approval_fails_closed(self):
        for field in guard.NEEDED_REVIEWS:
            with self.subTest(field=field):
                forged = copy.deepcopy(self.contract)
                forged["acceptance_receipts"][field] = "PASSED_ACCEPTED_ON_MAIN"
                with self.assertRaises(ValueError):
                    guard.validate(forged)

    def test_forged_image_eligibility_or_publication_fails_closed(self):
        for key, value in (
            ("release_state", "READY"),
            ("display_eligible_now", True),
            ("photographer_or_third_party_rights_verified", True),
            ("photo_credit", "Paramount"),
            ("primary_nasa_photo_sha256", "0" * 64),
            ("caption", "Official Star Trek film scene"),
            ("fictional_work_or_episode_media", True),
            ("auto_fetch_before_opt_in", True),
            ("remote_hotlink_permitted_by_this_contract", True),
            ("same_origin_mirror_permitted_by_this_contract", True),
            ("binary_files_included", 1),
            ("site_files_modified", 1),
        ):
            with self.subTest(key=key):
                forged = copy.deepcopy(self.contract)
                forged[key] = value
                with self.assertRaises(ValueError):
                    guard.validate(forged)

    def test_hidden_nested_image_and_symlink_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "hidden").mkdir()
            (directory / "hidden" / "still.jpg").write_bytes(b"fake")
            with self.assertRaises(ValueError):
                guard.validate(self.contract, directory=directory)
            (directory / "hidden" / "still.jpg").unlink()
            (directory / "hidden" / "link").symlink_to(directory.parent / "outside.jpg")
            with self.assertRaises(ValueError):
                guard.validate(self.contract, directory=directory)

    def test_disguised_binary_or_data_image_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "MANIFEST.md").write_bytes(b"\xff\xd8\xff\xe0image")
            with self.assertRaisesRegex(ValueError, "binary/image magic"):
                guard.validate(self.contract, directory=directory)
            (directory / "MANIFEST.md").write_text("![img](data:image/jpeg;base64,ABC)")
            with self.assertRaisesRegex(ValueError, "embedded image"):
                guard.validate(self.contract, directory=directory)

    def test_extra_fields_or_removed_obligations_rejected(self):
        forged = copy.deepcopy(self.contract)
        forged["copyright_cleared"] = True
        with self.assertRaises(ValueError):
            guard.validate(forged)
        forged = copy.deepcopy(self.contract)
        forged["review_requirements"] = []
        with self.assertRaises(ValueError):
            guard.validate(forged)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            guard.strict_pairs([("release_state", "HOLD"), ("release_state", "GO")])


if __name__ == "__main__":
    unittest.main()
