"""Fail closed on forged ISBN, cover variant, rights and held title-page art."""

from __future__ import annotations

import copy
import json
import unittest
import importlib.util
from pathlib import Path

DIR = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("medium_cover_validate", DIR / "validate.py")
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class MediumSourceCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads((DIR / "records.json").read_text(encoding="utf-8"))

    def test_valid_source_candidate_packet(self) -> None:
        self.assertEqual(module.validate(self.packet), 4)

    def test_wrong_isbn_does_not_match_reviewed_cover(self) -> None:
        self.packet["candidates"][0]["isbn"] = "9781982113315"
        with self.assertRaisesRegex(ValueError, "edition-cover mismatch"):
            module.validate(self.packet)

    def test_wrong_cover_id_does_not_match(self) -> None:
        self.packet["candidates"][0]["cover_id"] = 12857937
        with self.assertRaisesRegex(ValueError, "edition-cover mismatch"):
            module.validate(self.packet)

    def test_unreviewed_remote_host_rejected(self) -> None:
        self.packet["candidates"][0]["image_url"] = "https://example.com/art.jpg"
        with self.assertRaisesRegex(ValueError, "unreviewed image host"):
            module.validate(self.packet)

    def test_rights_promotion_rejected(self) -> None:
        self.packet["candidates"][0]["rights_status"] = "PUBLIC_DOMAIN"
        with self.assertRaisesRegex(ValueError, "rights promotion"):
            module.validate(self.packet)

    def test_release_promotion_rejected(self) -> None:
        self.packet["candidates"][0]["release_status"] = "DISPLAY_CLEARED"
        with self.assertRaisesRegex(ValueError, "release promotion"):
            module.validate(self.packet)

    def test_title_page_hold_cannot_be_removed(self) -> None:
        self.packet["holds"] = []
        with self.assertRaisesRegex(ValueError, "visually rejected"):
            module.validate(self.packet)

    def test_duplicate_row_rejected(self) -> None:
        self.packet["candidates"][3] = copy.deepcopy(self.packet["candidates"][0])
        with self.assertRaisesRegex(ValueError, "duplicate row"):
            module.validate(self.packet)

    def test_variant_change_rejected(self) -> None:
        self.packet["candidates"][0]["variant"] = "L"
        with self.assertRaisesRegex(ValueError, "variant/width mismatch"):
            module.validate(self.packet)

    def test_valid_looking_but_wrong_jpeg_hash_rejected(self) -> None:
        self.packet["candidates"][0]["image_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "medium byte receipt mismatch"):
            module.validate(self.packet)


if __name__ == "__main__":
    unittest.main()
