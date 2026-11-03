#!/usr/bin/env python3
"""Adversarial regression checks for publisher poster-link custody."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate import HERE, errors, read_json


class PosterLocatorCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = read_json(HERE / "records.json")

    def mutate(self, action):
        packet = copy.deepcopy(self.good)
        action(packet)
        self.assertTrue(errors(packet), "tampered packet unexpectedly passed")

    def test_valid(self):
        self.assertEqual(errors(self.good), [])

    def test_duplicate_keys_fail_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "bad.json"
            test_file.write_text('{"rights_status":"HELD_NO_PUBLIC_DISPLAY_LICENSE", "rights_status":"PERMISSION_GRANTED"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                read_json(test_file)

    def test_substitution_between_valid_records(self):
        self.mutate(lambda p: p["observations"][0].update({
            "film_directory_id": p["observations"][1]["film_directory_id"],
            "source_url": p["observations"][1]["source_url"],
            "image_locator": p["observations"][1]["image_locator"],
            "publisher_image_alt_label": p["observations"][1]["publisher_image_alt_label"],
        }))

    def test_wrong_image_same_first_party_host(self):
        self.mutate(lambda p: p["observations"][0].update({"image_locator": p["observations"][0]["image_locator"].replace("ST1_ARTalt", "FAKE_KEYART")}))

    def test_wrong_publisher_page(self):
        self.mutate(lambda p: p["observations"][0].update({"source_url": "https://www.startrek.com/movies/star-trek-nemesis"}))

    def test_alt_label_forgery(self):
        self.mutate(lambda p: p["observations"][0].update({"publisher_image_alt_label": "Original 1979 poster verified"}))

    def test_false_rights_claim(self):
        self.mutate(lambda p: p.update({"rights_status": "PUBLIC_DISPLAY_PERMISSION_VERIFIED"}))

    def test_false_binary_claim(self):
        self.mutate(lambda p: p.update({"image_bytes_retrieved": True}))

    def test_false_coverage_promotion(self):
        self.mutate(lambda p: p.update({"research_coverage_effect": "CLOSE_READ"}))

    def test_false_explorer_release(self):
        self.mutate(lambda p: p.update({"explorer_effect": "PUBLISHED_POSTER_IMAGES"}))

    def test_false_display(self):
        self.mutate(lambda p: p["observations"][0].update({"display_eligible": True}))

    def test_fake_image_fetch(self):
        self.mutate(lambda p: p["observations"][0].update({"image_fetch_status": "FETCHED_AND_VERIFIED"}))

    def test_directory_input_mismatch(self):
        self.mutate(lambda p: p["source_input"].update({"sha256": "0" * 64}))

    def test_removed_row(self):
        self.mutate(lambda p: p["observations"].pop())

    def test_duplicate_row(self):
        self.mutate(lambda p: p["observations"].append(copy.deepcopy(p["observations"][0])))

    def test_injected_field(self):
        self.mutate(lambda p: p["observations"][0].update({"licensed": True}))

    def test_control_chars_in_source_evidence(self):
        self.mutate(lambda p: p["observations"][0].update({"source_page_evidence": "Poster link\u0000 licensed"}))

    def test_sanitized_public_packet_no_image_binary(self):
        payload = json.dumps(self.good)
        self.assertNotIn("data:image", payload)
        self.assertNotIn("licensed-artwork/", payload)
        self.assertNotIn("PRIVATE_BOOK", payload)


if __name__ == "__main__":
    unittest.main()
