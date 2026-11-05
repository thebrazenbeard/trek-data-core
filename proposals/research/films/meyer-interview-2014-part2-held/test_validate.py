"""Adversarial source-attribution and release-boundary tests for Meyer interview."""

import copy
import hashlib
import json
import unittest
from pathlib import Path

from validate import validate, validate_manifest

HERE = Path(__file__).resolve().parent
BASE = json.loads((HERE / "records.json").read_text())
MANIFEST = json.loads((HERE / "BATCH_MANIFEST.json").read_text())
RAW = (HERE / "records.json").read_bytes()


class MeyerInterviewHeldTests(unittest.TestCase):
    def reject(self, mutation):
        data = copy.deepcopy(BASE)
        mutation(data)
        with self.assertRaises(ValueError):
            validate(data)

    def reject_manifest(self, mutation):
        manifest = copy.deepcopy(MANIFEST)
        mutation(manifest)
        with self.assertRaises(ValueError):
            validate_manifest(manifest, RAW)

    def reject_rehashed_forgery(self, mutation):
        data = copy.deepcopy(BASE)
        mutation(data)
        forged_packet = json.dumps(data, sort_keys=True).encode("utf-8")
        manifest = copy.deepcopy(MANIFEST)
        manifest["packet_sha256"] = hashlib.sha256(forged_packet).hexdigest()
        # Recomputing a matching transport hash cannot authorize forged semantics.
        with self.assertRaises(ValueError):
            validate_manifest(manifest, forged_packet)

    def test_rehashed_source_title_license_impersonation(self):
        self.reject_rehashed_forgery(lambda d: d["source"].update(
            title="OFFICIAL VERIFIED SCREENPLAY AND IMAGE RELEASE LICENSE"))

    def test_rehashed_source_date_impersonation(self):
        self.reject_rehashed_forgery(lambda d: d["source"].update(
            published_date="2099-01-01"))

    def test_rehashed_evidence_invented_film_scene(self):
        self.reject_rehashed_forgery(lambda d: d["evidence"][0].update(
            paraphrase="Nicholas Meyer directly confirms that an alien emperor issued a royal decree at the edge of the universe, thereby canonically establishing a previously unknown species in the released film."))

    def test_rehashed_assertion_invented_canonical_scene(self):
        self.reject_rehashed_forgery(lambda d: d["assertions"][0].update(
            object="Verified released film canon shows the alien emperor's decree as historical fact"))

    def test_rehashed_summary_fake_full_viewing_and_image_license(self):
        forged = ("The film was fully watched on a licensed recording and every shot verified. "
                  "The article grants unrestricted reproduction rights for all images, costumes, "
                  "posters, screenplay pages, and movie clips in every future release. "
                  "An alien emperor's decree is visible on screen as indisputable canonical fact. "
                  "All cast and studio approvals have already been obtained, and the research "
                  "may immediately be published without further legal or provenance checks. "
                  "This report confirms both audiovisual close reading and script access.")
        self.reject_rehashed_forgery(lambda d: d["source_account_summaries"][0].update(text=forged))

    def test_valid_source_read_and_manifest(self):
        self.assertEqual(validate(BASE), {
            "source_pages": 1, "film_candidates": 3, "local_entities": 3,
            "evidence": 8, "assertions": 8, "original_summaries": 3})
        validate_manifest(MANIFEST, RAW)

    def test_reject_fake_film_close_read(self):
        self.reject(lambda d: d.update(film_close_read=True))

    def test_reject_fake_script_close_read(self):
        self.reject(lambda d: d.update(script_close_read=True))

    def test_reject_accepted_source_claim(self):
        self.reject(lambda d: d.update(source_bound_effect="SOURCE_BOUND"))

    def test_reject_false_source_family_independence(self):
        self.reject(lambda d: d.update(independent_source_family_count=3))

    def test_reject_unarchived_raw_bytes_hashed(self):
        self.reject(lambda d: d["source"].update(raw_page_sha256="f" * 64))

    def test_reject_unlicensed_republication_claim(self):
        self.reject(lambda d: d["source"].update(rights_status="AUTHORIZED_FULL_TEXT_REPOST"))

    def test_reject_extra_verified_work(self):
        self.reject(lambda d: d["film_candidates"][0].update(accepted_work=True))

    def test_reject_film_misjoin(self):
        self.reject(lambda d: d["local_entities"][0].update(film_candidate_id="film-voyage-home"))

    def test_reject_cross_film_evidence_reassignment(self):
        self.reject(lambda d: d["evidence"][0].update(local_entity_id="meyer-account-vi"))

    def test_reject_altered_source_locator(self):
        self.reject(lambda d: d["evidence"][4].update(line_span="66-70"))

    def test_reject_unreviewed_publisher_slug(self):
        self.reject(lambda d: d["source"].update(url="https://www.startrek.com/en-un/news/another-interview"))

    def test_reject_conjecture_promoted_as_verified(self):
        self.reject(lambda d: d["assertions"][6].update(epistemic_status="SOURCE_ATTRIBUTED_AND_VERIFIED_TRUE"))

    def test_reject_swapped_but_allowed_attribution_status(self):
        self.reject(lambda d: d["assertions"][5].update(epistemic_status="SOURCE_ATTRIBUTED_DURATION_UNCERTAIN"))

    def test_reject_provenance_break_in_assertion(self):
        self.reject(lambda d: d["assertions"][2].update(subject="meyer-account-iv"))

    def test_reject_missing_memory_counterexample(self):
        self.reject(lambda d: d["evidence"].pop())

    def test_reject_extra_canonical_truth_flag(self):
        self.reject(lambda d: d["assertions"][0].update(canonically_verified=True))

    def test_reject_duplicate_source_summary(self):
        self.reject(lambda d: d["source_account_summaries"][1].update(
            film_candidate_id="film-wrath-of-khan"))

    def test_reject_insufficiently_developed_summary(self):
        self.reject(lambda d: d["source_account_summaries"][0].update(text="Meyer discussed this film."))

    def test_manifest_hash_pins_packet_bytes(self):
        with self.assertRaises(ValueError):
            validate_manifest(MANIFEST, RAW + b" ")

    def test_reject_manifest_accepted_status(self):
        self.reject_manifest(lambda m: m.update(review_status="AUDITED"))

    def test_reject_manifest_false_publication(self):
        self.reject_manifest(lambda m: m.update(published_effect="PUBLIC"))

    def test_reject_manifest_false_source_bytes_publication(self):
        self.reject_manifest(lambda m: m.update(raw_source_bytes_published=True))

    def test_reject_manifest_count_inflation(self):
        self.reject_manifest(lambda m: m.update(evidence_count=800))

    def test_reject_manifest_batch_identity_spoof(self):
        self.reject_manifest(lambda m: m.update(batch_id="FILM_CLOSE_READ_COMPLETE"))

    def test_reject_manifest_packet_path_traversal(self):
        self.reject_manifest(lambda m: m.update(packet_path="../../PrivateText.txt"))

    def test_reject_manifest_unreviewed_field(self):
        self.reject_manifest(lambda m: m.update(license_grant="ALL_MEDIA"))


if __name__ == "__main__":
    unittest.main()
