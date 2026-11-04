"""Negative coverage/identity/copyright tests for the five literary leads."""

import copy
import json
import unittest
from pathlib import Path

import validate


class FivePublisherWorksTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(Path(validate.RECORDS).read_text(encoding="utf-8"))

    def test_five_live_publisher_leads_only(self):
        validate.validate(self.data)
        self.assertEqual(validate.accepted_baseline_duplicate_isbns(), [])

    def test_cannot_invent_close_read(self):
        candidate = copy.deepcopy(self.data)
        candidate["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_cannot_launder_ebook_as_audio(self):
        candidate = copy.deepcopy(self.data)
        candidate["candidates"][0]["edition_format"] = "ADAPTED_AUDIO_DOWNLOAD"
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_editor_is_not_single_author(self):
        candidate = copy.deepcopy(self.data)
        target = next(r for r in candidate["candidates"] if r["edition_isbn13"] == "9780743400817")
        target["publisher_creator_credits"][0]["role"] = "AUTHOR"
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_romulan_coauthor_cannot_disappear(self):
        candidate = copy.deepcopy(self.data)
        target = next(r for r in candidate["candidates"] if r["edition_isbn13"] == "9780743419864")
        target["publisher_creator_credits"].pop()
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_unification_creator_conflict_kept_unresolved(self):
        candidate = copy.deepcopy(self.data)
        target = next(r for r in candidate["candidates"] if r["edition_isbn13"] == "9780743420730")
        target["publisher_copy_anomaly"] = None
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_cannot_bind_private_edition_without_source(self):
        candidate = copy.deepcopy(self.data)
        candidate["candidates"][0]["local_edition_identity_status"] = "PRIVATE_FILE_MATCHED"
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_cannot_add_copyrighted_prose_field(self):
        candidate = copy.deepcopy(self.data)
        candidate["candidates"][0]["book_passage"] = "not allowed"
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_cannot_double_count_publisher_as_independent_witnesses(self):
        candidate = copy.deepcopy(self.data)
        candidate["first_party_upstream_family_count"] = 5
        with self.assertRaises(ValueError):
            validate.validate(candidate)

    def test_duplicate_edition_rejected(self):
        candidate = copy.deepcopy(self.data)
        candidate["candidates"][1] = copy.deepcopy(candidate["candidates"][0])
        with self.assertRaises(ValueError):
            validate.validate(candidate)


if __name__ == "__main__":
    unittest.main()
