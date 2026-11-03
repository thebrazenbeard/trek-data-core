"""Fail-closed source-local checks for the Librarian's artwork proposal."""

import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "proposals/librarian/artwork-source-candidates-20261103"


class ArtworkCandidateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((PACKAGE / "records.json").read_text(encoding="utf-8"))
        cls.directory = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))

    def test_effects_remain_proposal_only(self):
        self.assertTrue(self.packet["proposal_only"])
        for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect"):
            self.assertEqual(self.packet[effect], "NONE")
        self.assertFalse(self.packet["image_bytes_committed"])
        self.assertFalse(self.packet["public_display_permission_inferred"])

    def test_ids_are_unique_and_join_existing_rows_only_when_claimed(self):
        row_ids = {row["row_id"] for row in self.directory["rows"]}
        candidates = self.packet["candidates"]
        self.assertEqual(len(candidates), 4)
        self.assertEqual(len({item["candidate_id"] for item in candidates}), len(candidates))
        for item in candidates:
            expected_medium = {
                "art-episode": "EPISODE",
                "art-film": "FILM",
                "art-literature": "LITERATURE",
            }["-".join(item["candidate_id"].split("-")[:2])]
            self.assertEqual(item["medium"], expected_medium)
            if item["subject_row_id"] is not None:
                self.assertIn(item["subject_row_id"], row_ids)
                self.assertIsNone(item["external_subject_candidate_id"])
            else:
                self.assertTrue(item["external_subject_candidate_id"])
            self.assertTrue(item["alt_text"].strip())
            self.assertEqual(urlsplit(item["source_page_url"]).scheme, "https")

    def test_images_are_third_party_metadata_not_promoted_licenses(self):
        eligible = [item for item in self.packet["candidates"] if item["image_url"]]
        self.assertEqual(len(eligible), 1)
        item = eligible[0]
        self.assertEqual(item["openlibrary_cover_id"], 10157401)
        self.assertEqual(item["image_http_status"], 200)
        self.assertEqual(item["image_content_type"], "image/jpeg")
        self.assertEqual(urlsplit(item["image_url"]).hostname, "covers.openlibrary.org")
        self.assertEqual(item["rights_state"], "API_SERVES_THUMBNAIL_UNDERLYING_COPYRIGHT_UNRESOLVED")
        self.assertIsNone(item["image_source_content_sha256"])
        self.assertEqual(len(item["image_source_metadata_sha256"]), 64)
        for other in self.packet["candidates"]:
            if other is item:
                continue
            self.assertIsNone(other["image_url"])
            self.assertEqual(other["display_policy"], "BLOCK_UNTIL_AUTHORIZED_IMAGE_SOURCE")


if __name__ == "__main__":
    unittest.main()
