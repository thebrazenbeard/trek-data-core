"""Adversarial guard against false literary Source/Work manifestation joins."""

import copy
import json
import unittest
from pathlib import Path

import audit


class AudioIdentityTest(unittest.TestCase):
    def setUp(self):
        self.batch = audit.load_pinned_public_batch()
        self.record = json.loads((Path(audit.HERE) / "AUDIT.json").read_text(encoding="utf-8"))

    def test_real_publisher_identity_audits_without_covering_book(self):
        report = audit.validate(self.batch, self.record)
        self.assertFalse(report["private_opf_edition_identified"])
        self.assertEqual(report["close_read_effect"], "NONE")

    def test_cannot_launder_audio_as_ebook(self):
        record = copy.deepcopy(self.record)
        record["publisher_page_metadata"]["edition_format"] = "EBOOK"
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_cannot_launder_private_opf_edition_match(self):
        record = copy.deepcopy(self.record)
        record["private_opf_to_audio_isbn_identity_verified"] = True
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_cannot_mark_close_read(self):
        record = copy.deepcopy(self.record)
        record["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_cannot_fake_second_source_family(self):
        record = copy.deepcopy(self.record)
        record["publisher_upstream_family_count"] = 2
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_cannot_silence_ambiguous_place_spelling(self):
        record = copy.deepcopy(self.record)
        record["publisher_description_spelling_disagreement"] = "RESOLVED"
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_no_unreviewed_text_or_artwork_fields(self):
        record = copy.deepcopy(self.record)
        record["copyrighted_text"] = "not permitted"
        with self.assertRaises(ValueError):
            audit.validate(self.batch, record)

    def test_no_edition_change_in_prior_publisher_packet(self):
        batch = copy.deepcopy(self.batch)
        target = next(r for r in batch["candidates"] if r["publisher_isbn13"] == audit.TARGET_ISBN)
        target["publisher_edition_format"] = "EBOOK"
        with self.assertRaises(ValueError):
            audit.validate(batch, self.record)


if __name__ == "__main__":
    unittest.main()
