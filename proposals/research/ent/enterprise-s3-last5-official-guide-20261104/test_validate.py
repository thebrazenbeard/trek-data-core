"""Adversarial checks for ENT S3 last-five publisher-guide packet and lineage."""

from __future__ import annotations

import copy
import hashlib
import unittest

from validate import FIRST_FIVE, HERE, read_json, validate


class EnterpriseS3LastFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.first = read_json(FIRST_FIVE)
        cls.first_sha = hashlib.sha256(FIRST_FIVE.read_bytes()).hexdigest()

    def reject(self, change):
        packet = copy.deepcopy(self.packet)
        change(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.first, self.first_sha)

    def test_valid_packet(self):
        validate(self.packet, self.first, self.first_sha)

    def test_first_five_digest_drift_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.packet, self.first, "0" * 64)

    def test_predecessor_global_work_promotion_rejected(self):
        first = copy.deepcopy(self.first)
        first["accepted_work_effect"] = "PROMOTED"
        with self.assertRaises(ValueError):
            validate(self.packet, first, self.first_sha)

    def test_first_five_commit_forgery_rejected(self):
        self.reject(lambda p: p["prior_first_five"].update(commit="another"))

    def test_first_five_receipt_forgery_rejected(self):
        self.reject(lambda p: p["prior_first_five"].update(source_response_sha256="0" * 64))

    def test_source_admission_rejected(self):
        self.reject(lambda p: p.update(accepted_source_binding_effect="ADMITTED"))

    def test_work_admission_rejected(self):
        self.reject(lambda p: p.update(accepted_work_effect="FIVE_WORKS"))

    def test_coverage_claim_rejected(self):
        self.reject(lambda p: p.update(coverage_effect="FIVE_CLOSE_READS"))

    def test_denominator_claim_rejected(self):
        self.reject(lambda p: p.update(denominator_effect="TEN_NEW_WORKS"))

    def test_explorer_publishing_rejected(self):
        self.reject(lambda p: p.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_reconciliation_claim_rejected(self):
        self.reject(lambda p: p.update(reconciliation_effect="AUTO_BIND"))

    def test_claim_episode_watched_rejected(self):
        self.reject(lambda p: p.update(episode_content_watched=True))

    def test_claim_transcript_read_rejected(self):
        self.reject(lambda p: p.update(transcripts_read=True))

    def test_claim_image_copied_rejected(self):
        self.reject(lambda p: p.update(image_bytes_fetched=True))

    def test_wrong_html_digest_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_sha256="0" * 64))

    def test_wrong_html_byte_length_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_bytes=400))

    def test_raw_publisher_prose_commit_rejected(self):
        self.reject(lambda p: p["source"].update(raw_html_committed=True))

    def test_independent_witness_forgery_rejected(self):
        self.reject(lambda p: p["source"].update(independence_group="two:independent:sources"))

    def test_wrong_publisher_guide_rejected(self):
        self.reject(lambda p: p["source"].update(url="https://memory-alpha.fandom.com/"))

    def test_false_unchanged_html_rejected(self):
        self.reject(lambda p: p.update(raw_html_digest_differs_from_predecessor=False))

    def test_full_card_count_false_rejected(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=10))

    def test_first_five_reintroduced_rejected(self):
        self.reject(lambda p: p["selected_tranche_episode_ordinals"].__setitem__(0, 1))

    def test_missing_new_card_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"].pop())

    def test_out_of_order_new_card_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"].reverse())

    def test_wrong_title_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][1].update(title="Invented"))

    def test_false_24_analyses_rejected(self):
        self.reject(lambda p: p.update(last_five_analytical_synopses_proposed=24))

    def test_fingerprint_tamper_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][2].update(description_sha256="0" * 64))

    def test_collusive_fingerprint_tamper_rejected(self):
        def mutate(p):
            p["last_five_guide_cards"][0]["description_sha256"] = "0" * 64
            p["source_relative_evidence"][0]["publisher_description_sha256"] = "0" * 64
        self.reject(mutate)

    def test_wrong_source_description_line_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][4].update(locator="line 123"))

    def test_duplicate_evidence_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][1].update(id="ent-s3-e06-guide-description"))

    def test_predecessor_id_reuse_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(id="ent-s3-e01-publisher-card"))

    def test_canonical_work_binding_rejected(self):
        self.reject(lambda p: p["local_entities"][3].update(canonical_work_id="ent:s3:e09"))

    def test_objective_episode_truth_promotion_rejected(self):
        self.reject(lambda p: p["typed_assertions"][0].update(status="VERIFIED_EPISODE_TRUTH"))

    def test_wrong_assertion_evidence_join_rejected(self):
        self.reject(lambda p: p["typed_assertions"][2].update(evidence_id="ent-s3-e06-guide-description"))

    def test_invalid_paraphrase_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][0].update(original_paraphrase=""))

    def test_float_ordinal_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][0].update(episode=6.0))

    def test_bool_ordinal_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][0].update(episode=True))


if __name__ == "__main__":
    unittest.main()
