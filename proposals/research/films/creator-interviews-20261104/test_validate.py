"""Adversarial semantic joins and custody falsifiers."""

import copy
import json
import unittest
from pathlib import Path
from validate import validate, validate_manifest

BASE = json.loads((Path(__file__).parent / "records.json").read_text())


class ValidateCreatorInterviews(unittest.TestCase):
    def test_valid_packet(self):
        self.assertEqual(validate(BASE)["source_pages_read"], 4)

    def reject(self, callback):
        data = copy.deepcopy(BASE)
        callback(data)
        with self.assertRaises(ValueError):
            validate(data)

    def test_wrong_film_source(self):
        self.reject(lambda d: d["sources"][0].update(film_candidate_id="film-insurrection"))

    def test_fake_studio_date(self):
        self.reject(lambda d: d["sources"][1].update(published="2099-01-01"))

    def test_wrong_interview_slug(self):
        self.reject(lambda d: d["sources"][2].update(url="https://www.startrek.com/news/other-interview"))

    def test_misjoined_evidence(self):
        self.reject(lambda d: d["evidence"][0].update(source_id="src-frakes-2016"))

    def test_misjoined_assertion(self):
        self.reject(lambda d: d["assertions"][0].update(subject="entity-frakes-account"))

    def test_wrong_film_synopsis_join(self):
        self.reject(lambda d: d["source_account_summaries"][0].update(source_ids=["src-stillwell-2011"]))

    def test_false_film_viewing(self):
        self.reject(lambda d: d.update(full_film_viewed=True))

    def test_false_close_read(self):
        self.reject(lambda d: d.update(close_read=True))

    def test_fabricated_raw_checksum(self):
        self.reject(lambda d: d["sources"][0].update(raw_page_sha256="1" * 64))

    def test_fabricated_independent_source_lineage(self):
        self.reject(lambda d: d.update(independent_publisher_family_count=4))

    def test_claim_promotion(self):
        self.reject(lambda d: d["assertions"][0].update(epistemic_status="OBJECTIVELY_TRUE_FILM_EVENT"))

    def test_reject_source_attributed_canonical_verification_suffix(self):
        self.reject(lambda d: d["assertions"][0].update(epistemic_status="SOURCE_ATTRIBUTED_AND_CANONICALLY_VERIFIED"))

    def test_reject_transposed_but_allowed_attribution_status(self):
        self.reject(lambda d: d["assertions"][0].update(epistemic_status="SOURCE_ATTRIBUTED_NOT_DRAFT_COMPARED"))

    def test_tampered_line_locator(self):
        self.reject(lambda d: d["evidence"][0].update(line_span="500-600"))

    def test_transposed_plausible_same_source_locator(self):
        self.reject(lambda d: d["evidence"][0].update(line_span="85-87"))

    def test_manifest_pins_exact_packet_bytes(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        original = (Path(__file__).parent / "records.json").read_bytes()
        validate_manifest(manifest, original)
        with self.assertRaises(ValueError):
            validate_manifest(manifest, original + b" ")

    def test_reject_extra_top_level_coverage_claim(self):
        self.reject(lambda d: d.update(film_close_read=True))

    def test_reject_extra_source_rights_claim(self):
        self.reject(lambda d: d["sources"][0].update(rights_basis="AUTHORIZED_FULL_SCRIPT"))

    def test_reject_extra_evidence_admission(self):
        self.reject(lambda d: d["evidence"][0].update(accepted=True))

    def test_reject_extra_assertion_verification(self):
        self.reject(lambda d: d["assertions"][0].update(verification_status="VERIFIED"))

    def test_reject_extra_summary_coverage(self):
        self.reject(lambda d: d["source_account_summaries"][0].update(coverage_effect="CLOSE_READ"))

    def test_reject_extra_manifest_release_claim(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["public_release"] = True
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_reject_changed_existing_manifest_release_claim(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["published_effect"] = "ADMITTED"
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_reject_existing_manifest_film_close_read_claim(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["film_close_read"] = True
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_reject_inflated_source_account_summary_count(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["source_account_synopsis_count"] = 999
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_reject_manifest_packet_path_traversal(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["packet_path"] = "../../private-text"
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_reject_manifest_batch_identity_impersonation(self):
        manifest = json.loads((Path(__file__).parent / "BATCH_MANIFEST.json").read_text())
        manifest["batch_id"] = "ESCALATED_ADMISSION"
        with self.assertRaises(ValueError):
            validate_manifest(manifest, (Path(__file__).parent / "records.json").read_bytes())

    def test_stillwell_finished_book_is_not_merely_proposed(self):
        evidence = next(x for x in BASE["evidence"] if x["id"] == "ev-stillwell-drafts")
        assertion = next(x for x in BASE["assertions"] if x["id"] == "as-stillwell-drafts")
        synopsis = next(x for x in BASE["source_account_summaries"] if x["film_candidate_id"] == "film-insurrection")
        for text in (evidence["paraphrase"], assertion["object"], synopsis["text"]):
            self.assertIn("completed", text.lower())
            self.assertIn("unpublished", text.lower())


if __name__ == "__main__":
    unittest.main()
