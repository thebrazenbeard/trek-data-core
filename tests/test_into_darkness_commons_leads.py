"""Film-specific documentary photo license intake must not self-publish."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tools import validate_into_darkness_commons_leads as subject


class IntoDarknessPhotoHeldTests(unittest.TestCase):
    def setUp(self):
        self.packet = subject.build()

    def test_exact_stored_source_derivation(self):
        subject.validate(subject.strict_json(subject.OUTPUT.read_bytes()))
        self.assertEqual(self.packet, subject.strict_json(subject.OUTPUT.read_bytes()))

    def test_exact_accepted_github_base_and_film_row(self):
        self.assertEqual(self.packet["accepted_main_commit"], subject.ACCEPTED_GITHUB_MAIN)
        self.assertEqual(self.packet["accepted_film_catalog_sha256"], subject.FILM_ROWS_SHA256)
        self.assertEqual(self.packet["source_local_film_row_id"], "film:film-into-darkness")
        self.assertEqual(self.packet["source_local_film_locator"],
                         "https://www.startrek.com/movies/star-trek-into-darkness")
        self.assertEqual(self.packet["source_local_film_title"], "Star Trek Into Darkness")

    def test_only_two_film_specific_photos_not_episode_or_poster(self):
        self.assertEqual(len(self.packet["assets"]), 2)
        self.assertTrue(self.packet["not_episode_stills_not_theatrical_posters"])
        self.assertEqual(self.packet["file_page_cc_license_observed_count"], 2)
        self.assertEqual(self.packet["visually_inspected_image_candidates"], 0)
        self.assertTrue(all("PREMIERE" in r["photo_context"] for r in self.packet["assets"]))
        self.assertTrue(all(not r["image_is_official_paramount_still"] and
                            not r["image_is_publisher_theatrical_poster"] for r in self.packet["assets"]))

    def test_distinct_photographic_files_but_not_independent_upstream_authors(self):
        images = self.packet["assets"]
        self.assertNotEqual(images[0]["file_page_revision_url"], images[1]["file_page_revision_url"])
        self.assertNotEqual(images[0]["flickr_source"], images[1]["flickr_source"])
        self.assertEqual({item["photographer"] for item in images}, {"Eva Rinaldi"})
        self.assertEqual(self.packet["same_author_single_original_source_family"],
                         "EVA_RINALDI_FLICKR_VIA_WIKIMEDIA_COMMONS")

    def test_file_level_license_and_flickr_review_pinned(self):
        self.assertEqual({r["license_identifier"] for r in self.packet["assets"]},
                         {"CC-BY-SA-2.0"})
        self.assertTrue(all(r["license_url"] == "https://creativecommons.org/licenses/by-sa/2.0/"
                            for r in self.packet["assets"]))
        self.assertIn("FLICKREVIEWR_2013_04_23", self.packet["assets"][0]["flickr_license_review_observed"])
        self.assertIn("COMMONS_BOT_2013_08_08", self.packet["assets"][1]["flickr_license_review_observed"])
        self.assertEqual(self.packet["license_page_class"],
                         "PRIMARY_COMMONS_FILE_DESCRIPTION_AND_FLICKR_LICENSE_REVIEW_OBSERVATION")

    def test_specific_per_file_cc_author_and_image_shape(self):
        group, portrait = self.packet["assets"]
        self.assertEqual((group["commons_file_original_width"], group["commons_file_original_height"]),
                         (1000, 612))
        self.assertEqual(group["observed_people_from_file_description"],
                         ["Karl Urban", "Zachary Quinto", "J. J. Abrams", "Chris Pine"])
        self.assertEqual((portrait["commons_file_original_width"], portrait["commons_file_original_height"]),
                         (1000, 1821))
        self.assertEqual(portrait["observed_people_from_file_description"],
                         ["Chris Pine", "Karl Urban"])
        self.assertTrue(all(len(r["alt_text_proposal"]) < 180 for r in self.packet["assets"]))

    def test_attribution_license_change_notice_and_sharealike_are_required(self):
        for item in self.packet["assets"]:
            self.assertTrue(item["adaptation_requires_sharealike"])
            self.assertEqual(set(item["attribution_required"]),
                             {"FILE_TITLE", "CREATOR", "LINK_EXACT_IMAGE", "LINK_LICENSE", "CHANGES_NOTICE", "NONENDORSEMENT"})
            self.assertIn(item["file_title"], item["attribution_proposal"])

    def test_people_backdrop_trademark_and_visual_rights_unresolved(self):
        self.assertTrue(self.packet["license_not_other_rights"])
        for item in self.packet["assets"]:
            self.assertEqual(item["depicted_subjects_rights_review"], "NOT_DONE")
            self.assertEqual(item["backdrop_branding_rights_review"], "NOT_DONE")
            self.assertIsNone(item["independent_visual_reviewer"])
            self.assertIsNone(item["independent_license_reviewer"])

    def test_no_image_bytes_remote_requests_or_source_coverage_changes(self):
        self.assertFalse(self.packet["downloaded_or_embedded_photographic_bytes"])
        self.assertEqual(self.packet["independently_publication_approved_count"], 0)
        for k in ("accepted_work_effect", "accepted_source_effect", "research_coverage_effect", "public_explorer_effect"):
            self.assertEqual(self.packet[k], "NONE")
        for item in self.packet["assets"]:
            self.assertIsNone(item["full_image_sha256"])
            self.assertIsNone(item["selected_thumbnail_sha256"])
            self.assertIsNone(item["file_page_snapshot_sha256"])
            self.assertIsNone(item["exact_public_artwork_release_binding"])
            self.assertFalse(item["public_release_eligible"])

    def test_cannot_forge_rights_release_or_license(self):
        for field, value in (("public_release_eligible", True),
                             ("right_to_rehost_for_explorer", "APPROVED"),
                             ("license_identifier", "CC0-1.0"),
                             ("image_is_official_paramount_still", True),
                             ("exact_public_artwork_release_binding", "film:film-into-darkness")):
            forged = copy.deepcopy(self.packet)
            forged["assets"][0][field] = value
            with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "modified"):
                subject.validate(forged)

    def test_cannot_import_image_binary_or_claim_reviewer(self):
        for field, value in (("full_image_sha256", "0" * 64),
                             ("independent_visual_reviewer", "imaginary-reviewer"),
                             ("file_page_snapshot_sha256", "f" * 64),
                             ("image_data", "base64")):
            forged = copy.deepcopy(self.packet)
            forged["assets"][1][field] = value
            with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "modified"):
                subject.validate(forged)

    def test_cannot_swap_into_beyond_film_row(self):
        forged = copy.deepcopy(self.packet)
        forged["source_local_film_row_id"] = "film:film-beyond"
        with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "modified"):
            subject.validate(forged)

    def test_cannot_add_unrelated_book_or_episode_row(self):
        forged = copy.deepcopy(self.packet)
        forged["assets"][0]["proposed_documentary_context_film_row_id"] = "directory:episode:1"
        with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "modified"):
            subject.validate(forged)

    def test_no_user_absolute_paths_or_image_code_payloads(self):
        raw = subject.OUTPUT.read_text(encoding="utf-8")
        for bad in ("OneDrive", "C:\\Users", "D:\\VERA", "data:image", '"pixels"', '"full_text"'):
            self.assertNotIn(bad, raw)
        self.assertEqual(self.packet["public_explorer_effect"], "NONE")

    def test_invalid_duplicate_json_key_and_nonfinite(self):
        with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "duplicate JSON key"):
            subject.strict_json(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "nonfinite JSON"):
            subject.strict_json(b'{"a":Infinity}')

    def test_accepted_local_film_search_index_tamper_fails_sha(self):
        with tempfile.TemporaryDirectory(prefix="trek-film-commons-") as temp:
            root = Path(temp)
            target = root / subject.FILM_ROWS
            target.parent.mkdir(parents=True)
            shutil.copyfile(subject.ROOT / subject.FILM_ROWS, target)
            catalog = json.loads(target.read_text(encoding="utf-8"))
            candidate = next(row for row in catalog["rows"] if row["row_id"] == "film:film-into-darkness")
            candidate["source_locator"] = "https://example.com/spoof"
            target.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "SHA drift"):
                subject.build(root)

    def test_accepted_local_film_search_index_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix="trek-film-commons-") as temp:
            root = Path(temp)
            target = root / subject.FILM_ROWS
            target.parent.mkdir(parents=True)
            target.symlink_to(subject.ROOT / subject.FILM_ROWS)
            with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "unsafe accepted"):
                subject.build(root)

    def test_duplicate_candidate_identity_rejected(self):
        corrupt = list(subject.PINS)
        corrupt[1] = dict(corrupt[0])
        with mock.patch.object(subject, "PINS", tuple(corrupt)):
            with self.assertRaisesRegex(subject.FilmPhotoLeadRejected, "duplicate Commons"):
                subject.build()


if __name__ == "__main__":
    unittest.main()
