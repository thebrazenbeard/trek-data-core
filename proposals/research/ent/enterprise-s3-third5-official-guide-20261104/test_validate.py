"""Hostile source-custody and three-tranche separation regressions, all local."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, read_json, validate


class EnterpriseS3ThirdFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.predecessors = [
            (read_json(path), hashlib.sha256(path.read_bytes()).hexdigest())
            for path, *_ in PRIOR
        ]

    def reject(self, change):
        data = copy.deepcopy(self.packet)
        change(data)
        with self.assertRaises(ValueError):
            validate(data, self.predecessors)

    def test_held_packet_valid(self):
        validate(self.packet, self.predecessors)

    def test_imports_exact_predecessor_extractor(self):
        module = publisher_parser()
        self.assertEqual(module.URL, "https://www.paramountplus.com/shows/enterprise/episodes/3/")

    def test_prior_first_file_digest_drift_rejected(self):
        prior = copy.deepcopy(self.predecessors)
        prior[0] = (prior[0][0], "0" * 64)
        with self.assertRaises(ValueError):
            validate(self.packet, prior)

    def test_prior_second_file_digest_drift_rejected(self):
        prior = copy.deepcopy(self.predecessors)
        prior[1] = (prior[1][0], "0" * 64)
        with self.assertRaises(ValueError):
            validate(self.packet, prior)

    def test_predecessor_work_promotion_rejected(self):
        prior = copy.deepcopy(self.predecessors)
        prior[1][0]["accepted_work_effect"] = "ADMITTED"
        with self.assertRaises(ValueError):
            validate(self.packet, prior)

    def test_prior_first_commit_forgery_rejected(self):
        self.reject(lambda p: p["prior_batches"][0].update(commit="rewritten"))

    def test_prior_second_receipt_forgery_rejected(self):
        self.reject(lambda p: p["prior_batches"][1].update(source_response_sha256="0" * 64))

    def test_source_admission_rejected(self):
        self.reject(lambda p: p.update(accepted_source_binding_effect="ADMITTED"))

    def test_work_admission_rejected(self):
        self.reject(lambda p: p.update(accepted_work_effect="FIVE_WORKS"))

    def test_coverage_promotion_rejected(self):
        self.reject(lambda p: p.update(coverage_effect="FIVE_CLOSE_READS"))

    def test_denominator_inflation_rejected(self):
        self.reject(lambda p: p.update(denominator_effect="FIVE_ADDED"))

    def test_reconciliation_rejected(self):
        self.reject(lambda p: p.update(reconciliation_effect="GLOBAL_JOIN"))

    def test_explorer_release_rejected(self):
        self.reject(lambda p: p.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_episode_watch_claim_rejected(self):
        self.reject(lambda p: p.update(episode_content_watched=True))

    def test_transcript_read_claim_rejected(self):
        self.reject(lambda p: p.update(transcripts_read=True))

    def test_image_bytes_claim_rejected(self):
        self.reject(lambda p: p.update(image_bytes_fetched=True))

    def test_derived_source_falsely_independent_rejected(self):
        self.reject(lambda p: p["source"].update(independence_group="independent:mirror"))

    def test_source_url_rewritten_rejected(self):
        self.reject(lambda p: p["source"].update(url="https://wikipedia.org/Enterprise"))

    def test_source_http_not_successful_rejected(self):
        self.reject(lambda p: p["source"].update(response_http_status=404))

    def test_source_length_drift_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_bytes=1))

    def test_raw_response_sha_rewritten_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_sha256="0" * 64))

    def test_source_raw_html_commit_rejected(self):
        self.reject(lambda p: p["source"].update(raw_html_committed=True))

    def test_forged_same_raw_digest_rejected(self):
        self.reject(lambda p: p.update(raw_html_digest_differs_from_both_predecessors=False))

    def test_overstated_episode_count_rejected(self):
        self.reject(lambda p: p.update(third_five_analytical_synopses_proposed=24))

    def test_full_guide_count_mismatch_rejected(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=15))

    def test_first_ten_episode_overlap_rejected(self):
        self.reject(lambda p: p["selected_tranche_episode_ordinals"].__setitem__(0, 10))

    def test_missing_card_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"].pop())

    def test_title_mutation_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"][0].update(title="Imaginary"))

    def test_swapped_ordinal_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"].reverse())

    def test_description_fingerprint_tamper_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"][1].update(description_sha256="0" * 64))

    def test_card_and_evidence_hash_collusion_rejected(self):
        def corrupt(p):
            p["third_five_guide_cards"][0]["description_sha256"] = "0" * 64
            p["source_relative_evidence"][0]["publisher_description_sha256"] = "0" * 64
        self.reject(corrupt)

    def test_unknown_publisher_line_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][2].update(locator="unresolved"))

    def test_invented_work_binding_rejected(self):
        self.reject(lambda p: p["local_entities"][4].update(canonical_work_id="ent:S3:E15"))

    def test_first_ten_evidence_id_reuse_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][0].update(id="ent-s3-e08-guide-description"))

    def test_duplicate_new_evidence_id_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][1].update(id="ent-s3-e11-guide-description"))

    def test_bogus_claim_status_rejected(self):
        self.reject(lambda p: p["typed_assertions"][4].update(status="EPISODE_PLOT_VERIFIED"))

    def test_wrong_claim_evidence_join_rejected(self):
        self.reject(lambda p: p["typed_assertions"][0].update(evidence_id="ent-s3-e12-guide-description"))

    def test_blank_original_paraphrase_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][2].update(original_paraphrase=""))

    def test_boolean_ordinal_spoof_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"][0].update(episode=True))

    def test_float_ordinal_spoof_rejected(self):
        self.reject(lambda p: p["third_five_guide_cards"][0].update(episode=11.0))


if __name__ == "__main__":
    unittest.main()
