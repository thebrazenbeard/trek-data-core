"""Adversarial publisher edition/Work-boundary tests for Titan bibliography."""

import copy
import json
import unittest

import validate


class TitanFiveTest(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(validate.RECORDS.read_text(encoding="utf-8"))

    def test_nonfiction_publisher_corpus_only(self):
        validate.validate(self.record)
        self.assertEqual(validate.accepted_main_duplicate_isbn_paths(), [])

    def test_cannot_promote_artbook_to_novel(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][0]["work_form"] = "FICTION_NOVEL"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_fake_close_read(self):
        mutant = copy.deepcopy(self.record)
        mutant["coverage_effect"] = "CLOSE_READ"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_count_titan_as_five_upstreams(self):
        mutant = copy.deepcopy(self.record)
        mutant["first_party_publisher_family_count"] = 5
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_conflate_art_subject_with_author(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][0]["publisher_creator_credits"][0]["name"] = "John Eaves"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_drop_second_credited_creator(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][1]["publisher_creator_credits"].pop()
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_mix_up_ortiz_series_editions(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][2]["edition_isbn13"] = "9781785653872"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_flatten_us_uk_release_dates(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][0]["edition_published_us"] = mutant["works"][0]["edition_published_uk"]
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_add_copyrighted_cover_field(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][0]["artwork_embedded"] = "no"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_cannot_claim_private_copy_matched(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][0]["private_manifestation_binding"] = "VERIFIED"
        with self.assertRaises(ValueError):
            validate.validate(mutant)

    def test_duplicate_isbn_rejected(self):
        mutant = copy.deepcopy(self.record)
        mutant["works"][4]["edition_isbn13"] = mutant["works"][0]["edition_isbn13"]
        with self.assertRaises(ValueError):
            validate.validate(mutant)


if __name__ == "__main__":
    unittest.main()
