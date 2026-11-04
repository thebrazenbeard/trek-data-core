"""Exact rights/source regression tests for a HELD 2009 premiere photograph."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools import validate_trek_2009_premiere_photo as subject


class HeldTrek2009PremiereTests(unittest.TestCase):
    def setUp(self):
        self.packet = subject.expected()
        self.photo = self.packet["candidate"]

    def test_accepted_film_catalog_recomputed(self):
        self.assertEqual(subject.strict_json(subject.OUTPUT.read_bytes()), self.packet)
        subject.validate(self.packet)
        self.assertEqual(self.packet["accepted_main_commit"], "3028765359001b90bc3e6b5c1835ee283b326e91")
        self.assertTrue(self.packet["draft_pr_523_not_accepted_main"])
        self.assertEqual(self.packet["accepted_film_row_receipt"]["row_id"], "film:film-2009")
        self.assertEqual(self.packet["accepted_film_row_receipt"]["source_locator"],
                         "https://www.startrek.com/movies/star-trek-2009")

    def test_actual_film_specific_cc_photo_identity_not_poster(self):
        self.assertEqual(self.photo["documentary_event"],
                         "SYDNEY_OPERA_HOUSE_STAR_TREK_2009_FILM_PREMIERE")
        self.assertEqual(self.photo["photo_date"], "2009-04-07")
        self.assertIn("NOT_FILM_STILL_OR_POSTER", self.photo["proposed_image_kind"])
        self.assertEqual(self.photo["source_local_film_row_id_proposed_context"], "film:film-2009")

    def test_distinct_from_existing_beyond_and_into_darkness(self):
        self.assertNotIn("Beyond", self.photo["photo_title"])
        self.assertNotIn("Into_Darkness", self.photo["photo_title"])
        self.assertNotIn("Eva Rinaldi", self.photo["attribution_proposal"])
        self.assertEqual(self.photo["photographer_display_name"], "Penny B. Dreadful")

    def test_original_flickr_primary_and_historical_license_review(self):
        self.assertEqual(self.photo["original_source"],
                         "https://www.flickr.com/photos/visible-woman/3420160659")
        self.assertEqual(self.photo["license_identifier_observed"], "CC-BY-2.0")
        self.assertEqual(self.photo["license_url"], "https://creativecommons.org/licenses/by/2.0/")
        self.assertIn("HIGH_CONTRAST_2009_05_02", self.photo["license_review_observed"])
        self.assertIn("oldid=1254161622", self.photo["commons_fixed_revision"])

    def test_file_metadata_claims_not_independently_computed_image_digest(self):
        self.assertEqual(self.photo["commons_original_dimensions"], {"width": 1886, "height": 934})
        self.assertEqual(self.photo["commons_structured_metadata_original_sha1_claim_not_recomputed"],
                         "57f3913143347cdf32056a57aeb86e6b9086b33b")
        self.assertIsNone(self.photo["exact_source_image_sha256"])
        self.assertIsNone(self.photo["exact_selected_thumbnail_sha256"])

    def test_author_and_file_title_required_in_attribution(self):
        for piece in ("FILE_TITLE", "PHOTOGRAPHER", "SOURCE_FILE_PAGE_URL", "LICENSE_URL", "NONENDORSEMENT"):
            self.assertIn(piece, self.photo["required_credit_components"])
        self.assertIn(self.photo["photo_title"], self.photo["attribution_proposal"])
        self.assertIn(self.photo["photographer_display_name"], self.photo["attribution_proposal"])

    def test_commons_personality_warning_and_brand_rights_unresolved(self):
        self.assertEqual(self.photo["license_page_explicit_rights_warning"],
                         "PERSONALITY_RIGHTS_OF_DEPICTED_PEOPLE")
        self.assertTrue(self.photo["photo_license_excludes_other_rights_clearance"])
        for name in ("people_publicity_privacy_review", "branding_backdrop_trademark_review",
                     "independent_visual_review", "independent_legal_rights_review"):
            self.assertEqual(self.photo[name], "NOT_DONE")

    def test_no_coverage_or_work_admission_or_release(self):
        self.assertEqual(self.packet["independently_approved_display_count"], 0)
        self.assertEqual(self.packet["image_byte_observation_count"], 0)
        self.assertFalse(self.packet["copied_photographic_bytes"])
        self.assertFalse(self.photo["public_display_eligible"])
        self.assertFalse(self.photo["public_rehost_eligible"])
        self.assertIsNone(self.photo["exact_explorer_release_binding"])
        for effect in ("public_artwork_effect", "accepted_work_effect", "accepted_source_effect", "research_coverage_effect"):
            self.assertEqual(self.packet[effect], "NONE")

    def test_seven_subject_names_are_description_not_visual_authentication(self):
        self.assertEqual(len(self.photo["subject_names_claimed_in_commons_file_description"]), 7)
        self.assertEqual(self.photo["subject_names_claimed_in_commons_file_description"][0], "Karl Urban")
        self.assertEqual(self.photo["subject_names_claimed_in_commons_file_description"][-1], "John Cho")
        self.assertEqual(self.photo["independent_visual_review"], "NOT_DONE")

    def test_cannot_self_approve_change_license_or_image_class(self):
        for name, value in (("public_display_eligible", True),
                            ("public_rehost_eligible", True),
                            ("license_identifier_observed", "PUBLIC_DOMAIN"),
                            ("proposed_image_kind", "OFFICIAL_FILM_POSTER"),
                            ("exact_explorer_release_binding", "film:film-2009")):
            forged = copy.deepcopy(self.packet)
            forged["candidate"][name] = value
            with self.assertRaisesRegex(subject.HeldPhotoRejected, "mutation"):
                subject.validate(forged)

    def test_cannot_claim_undownloaded_bytes_or_invent_rights_receipt(self):
        for name, value in (("exact_source_image_sha256", "0" * 64),
                            ("reviewed_rights_receipt_sha256", "1" * 64),
                            ("image_b64", "AAAA"),
                            ("independent_legal_rights_review", "PASSED")):
            forged = copy.deepcopy(self.packet)
            forged["candidate"][name] = value
            with self.assertRaisesRegex(subject.HeldPhotoRejected, "mutation"):
                subject.validate(forged)

    def test_cannot_swap_into_another_film_or_claim_canonical_identity(self):
        forged = copy.deepcopy(self.packet)
        forged["candidate"]["source_local_film_row_id_proposed_context"] = "film:film-beyond"
        with self.assertRaisesRegex(subject.HeldPhotoRejected, "mutation"):
            subject.validate(forged)
        forged = copy.deepcopy(self.packet)
        forged["accepted_film_row_receipt"]["row_id"] = "work:canon-0001"
        with self.assertRaisesRegex(subject.HeldPhotoRejected, "mutation"):
            subject.validate(forged)

    def test_duplicate_json_key_or_nonfinite_number_rejected(self):
        with self.assertRaisesRegex(subject.HeldPhotoRejected, "duplicate key"):
            subject.strict_json(b'{"x":1,"x":2}')
        with self.assertRaisesRegex(subject.HeldPhotoRejected, "nonfinite"):
            subject.strict_json(b'{"x":NaN}')

    def test_private_paths_and_image_bytes_absent(self):
        raw = subject.OUTPUT.read_text(encoding="utf-8")
        for danger in ("C:\\Users", "OneDrive", "D:\\VERA", "data:image", '"bytes_base64"', '"prose"'):
            self.assertNotIn(danger, raw)

    def test_local_accepted_source_sha_poisoning_fails(self):
        with tempfile.TemporaryDirectory(prefix="trek-2009-art-") as tmp:
            root = Path(tmp)
            source = root / subject.SOURCE
            source.parent.mkdir(parents=True)
            shutil.copyfile(subject.ROOT / subject.SOURCE, source)
            obj = json.loads(source.read_text(encoding="utf-8"))
            film = next(item for item in obj["rows"] if item["row_id"] == "film:film-2009")
            film["source_locator"] = "https://example.net/forgery"
            source.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(subject.HeldPhotoRejected, "SHA changed"):
                subject.expected(root)

    def test_local_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory(prefix="trek-2009-art-") as tmp:
            root = Path(tmp)
            source = root / subject.SOURCE
            source.parent.mkdir(parents=True)
            source.symlink_to(subject.ROOT / subject.SOURCE)
            with self.assertRaisesRegex(subject.HeldPhotoRejected, "unsafe"):
                subject.expected(root)


if __name__ == "__main__":
    unittest.main()
