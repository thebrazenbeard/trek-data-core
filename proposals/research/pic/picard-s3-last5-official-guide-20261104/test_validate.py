"""Deterministic adversarial checks for separate publisher-card E06–E10 tranche."""

from __future__ import annotations

import copy
import hashlib
import unittest

from validate import FIRST_FIVE, HERE, read_json, validate


class PicS3LastFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.first = read_json(FIRST_FIVE)
        cls.first_sha = hashlib.sha256(FIRST_FIVE.read_bytes()).hexdigest()

    def reject(self, mutate):
        packet = copy.deepcopy(self.packet)
        mutate(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.first, self.first_sha)

    def test_valid_held_last_five(self):
        validate(self.packet, self.first, self.first_sha)

    def test_exact_predecessor_hash_required(self):
        with self.assertRaises(ValueError):
            validate(self.packet, self.first, "0" * 64)

    def test_wrong_predecessor_commit_rejected(self):
        self.reject(lambda p: p["prior_first_five"].update(commit="unknown"))

    def test_wrong_predecessor_response_digest_rejected(self):
        self.reject(lambda p: p["prior_first_five"].update(source_response_sha256="0" * 64))

    def test_predecessor_identity_cannot_be_promoted(self):
        first = copy.deepcopy(self.first)
        first["local_entities"][0]["canonical_work_id"] = "unearned-work"
        with self.assertRaises(ValueError):
            validate(self.packet, first, self.first_sha)

    def test_accepted_source_binding_rejected(self):
        self.reject(lambda p: p.update(accepted_source_binding_effect="ADMITTED"))

    def test_accepted_work_rejected(self):
        self.reject(lambda p: p.update(accepted_work_effect="FIVE_WORKS"))

    def test_coverage_claim_rejected(self):
        self.reject(lambda p: p.update(coverage_effect="FIVE_CLOSE_READS"))

    def test_denominator_claim_rejected(self):
        self.reject(lambda p: p.update(denominator_effect="TEN_DONE"))

    def test_reconciliation_claim_rejected(self):
        self.reject(lambda p: p.update(reconciliation_effect="GLOBAL_IDENTITY_RESOLVED"))

    def test_explorer_release_claim_rejected(self):
        self.reject(lambda p: p.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_claim_of_watching_episodes_rejected(self):
        self.reject(lambda p: p.update(episode_content_watched=True))

    def test_claim_of_transcript_read_rejected(self):
        self.reject(lambda p: p.update(transcripts_read=True))

    def test_source_html_committed_rejected(self):
        self.reject(lambda p: p["source"].update(raw_html_committed=True))

    def test_forged_fresh_source_sha_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_sha256="0" * 64))

    def test_source_length_tamper_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_bytes=200))

    def test_lineage_split_into_fake_independent_source_rejected(self):
        self.reject(lambda p: p["source"].update(independence_group="publisher:independent"))

    def test_mislabel_fresh_html_as_same_raw_snapshot_rejected(self):
        self.reject(lambda p: p.update(raw_html_digest_differs_from_predecessor=False))

    def test_first_five_episode_reintroduced_rejected(self):
        self.reject(lambda p: p["selected_tranche_episode_ordinals"].__setitem__(0, 1))

    def test_extra_episode_claim_rejected(self):
        self.reject(lambda p: p.update(last_five_analytical_synopses_proposed=10))

    def test_wrong_card_order_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"].reverse())

    def test_missing_card_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"].pop())

    def test_wrong_publisher_title_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][0].update(title="Invented"))

    def test_exact_source_fingerprint_tamper_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][2].update(description_sha256="0" * 64))

    def test_collusive_evidence_and_card_hash_tamper_rejected(self):
        def mutate(p):
            p["last_five_guide_cards"][0]["description_sha256"] = "0" * 64
            p["source_relative_evidence"][0]["publisher_description_sha256"] = "0" * 64
        self.reject(mutate)

    def test_wrong_source_description_locator_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][4].update(locator="line 123"))

    def test_empty_paraphrase_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][0].update(original_paraphrase=""))

    def test_canonical_work_binding_rejected(self):
        self.reject(lambda p: p["local_entities"][3].update(canonical_work_id="PIC-S3-E09"))

    def test_source_local_overlap_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(id="pic-s3-e01-publisher-card"))

    def test_duplicate_last_five_evidence_ids_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][1].update(id="pic-s3-e06-guide-description"))

    def test_assertion_objective_promotion_rejected(self):
        self.reject(lambda p: p["typed_assertions"][0].update(status="EPISODE_CONTENT_VERIFIED"))

    def test_assertion_evidence_misalignment_rejected(self):
        self.reject(lambda p: p["typed_assertions"][1].update(evidence_id="pic-s3-e06-guide-description"))

    def test_lineage_card_season_reassignment_rejected(self):
        self.reject(lambda p: p["last_five_guide_cards"][2].update(season=4))


if __name__ == "__main__":
    unittest.main()
