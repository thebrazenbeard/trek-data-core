"""Adversarial contract tests for film-specific photo source proposal."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import read_json, validate, RECORD


class PhotoProposalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.good = read_json(RECORD)

    def mutate_fails(self, edits: dict, key: str | None = None) -> None:
        bad = copy.deepcopy(self.good)
        dst = bad if key is None else bad[key]
        dst.update(edits)
        with self.assertRaises(ValueError):
            validate(bad)

    def test_accepts_pinned_held_candidate(self) -> None:
        validate(self.good)

    def test_rejects_release(self) -> None:
        self.mutate_fails({"public_artwork_release_effect": "APPROVED"})

    def test_rejects_mislabeled_still(self) -> None:
        self.mutate_fails({"image_kind": "FILM_STILL"}, key="candidate")

    def test_rejects_false_frame_claim_even_with_premiere_keywords(self) -> None:
        self.mutate_fails({
            "suggested_alt": "Frame from Star Trek Beyond showing Captain Kirk on Enterprise bridge, premiere microphone"
        }, key="candidate")

    def test_rejects_wrong_film(self) -> None:
        self.mutate_fails({"source_local_film_id": "film-into-darkness"}, key="candidate")

    def test_rejects_wrong_photo_digest(self) -> None:
        self.mutate_fails({"original_image_sha256": "0" * 64}, key="candidate")

    def test_rejects_wrong_rights_digest(self) -> None:
        self.mutate_fails({"commons_rights_page_sha256": "0" * 64}, key="candidate")

    def test_rejects_rights_swap(self) -> None:
        self.mutate_fails({"license_url": "https://creativecommons.org/publicdomain/zero/1.0/"}, key="candidate")

    def test_rejects_origin_swap(self) -> None:
        self.mutate_fails({"commons_file_page": "https://example.org/forged"}, key="candidate")

    def test_rejects_display_admission(self) -> None:
        self.mutate_fails({"editorial_display_admission": "READY"}, key="candidate")

    def test_rejects_extra_fields(self) -> None:
        self.mutate_fails({"private_path": "C:/Users/foo"})


if __name__ == "__main__":
    unittest.main()
