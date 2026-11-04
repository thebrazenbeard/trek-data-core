"""Adversarial checks for source identity, date anomaly and character claims."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import FIRST_RECORD, HERE, read_json, validate


class EnterpriseS2SecondFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE/"records.json")
        cls.first=read_json(FIRST_RECORD)
        cls.sha=hashlib.sha256(FIRST_RECORD.read_bytes()).hexdigest()

    def reject(self,mutation):
        changed=copy.deepcopy(self.packet)
        mutation(changed)
        with self.assertRaises(ValueError):
            validate(changed,self.first,self.sha)

    def test_packet_passes(self):
        validate(self.packet,self.first,self.sha)

    def test_exact_s2_predecessor_parser(self):
        parser=publisher_parser()
        self.assertEqual(parser.URL,"https://www.paramountplus.com/shows/enterprise/episodes/2/")
        self.assertEqual(parser.SERIES_PREFIX,"Star Trek: Enterprise - ")

    def test_predecessor_digest_required(self):
        with self.assertRaises(ValueError):
            validate(self.packet,self.first,"0"*64)

    def test_predecessor_held_status_required(self):
        first=copy.deepcopy(self.first)
        first["status"]="ACCEPTED"
        with self.assertRaises(ValueError):
            validate(self.packet,first,self.sha)

    def test_exact_commit_and_source_lineage(self):
        self.reject(lambda p:p["prior_batch"].update(commit="wrong"))
        self.reject(lambda p:p["prior_batch"].update(source_response_sha256="0"*64))
        self.reject(lambda p:p["prior_batch"].update(episode_scope=[1,10]))

    def test_protected_effects_absent(self):
        for k in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect",
                  "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=k):
                self.reject(lambda p:p.update({k:"ACCEPTED"}))

    def test_no_video_audio_text_or_image_claims(self):
        for k in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
            with self.subTest(field=k):
                self.reject(lambda p:p.update({k:True}))

    def test_source_receipt_pinned(self):
        for change in (
            {"response_http_status":404},{"raw_response_bytes":1},
            {"raw_response_sha256":"0"*64},{"response_date_header":"wrong"},
            {"observed_at_utc":"wrong"},{"raw_html_committed":True},
            {"url":"https://other.example/"},{"independence_group":"independent"},
        ):
            with self.subTest(change=change):
                self.reject(lambda p:p["source"].update(change))

    def test_full_26_card_digest_and_context(self):
        self.reject(lambda p:p.update(observed_full_guide_card_count=10))
        self.reject(lambda p:p.update(all_26_metadata_and_description_fingerprints_match_prior_snapshot=False))
        self.reject(lambda p:p.update(raw_html_digest_differs_from_predecessor=False))
        self.reject(lambda p:p["all_26_guide_cards"].pop())
        self.reject(lambda p:p["all_26_guide_cards"][25].update(description_sha256="0"*64))

    def test_only_second_five_descriptions_processed(self):
        self.reject(lambda p:p.update(selected_tranche_episode_ordinals=[5,6,7,8,9]))
        self.reject(lambda p:p.update(second_five_source_descriptions_inspected=26))
        self.reject(lambda p:p.update(second_five_analytical_synopses_proposed=26))
        self.reject(lambda p:p.update(second_five_description_total_chars=800))
        self.reject(lambda p:p["second_five_guide_cards"].pop())
        self.reject(lambda p:p["second_five_guide_cards"].reverse())

    def test_exact_card_title_and_source_digest(self):
        self.reject(lambda p:p["second_five_guide_cards"][0].update(title="Marauder"))
        self.reject(lambda p:p["second_five_guide_cards"][1].update(description_sha256="0"*64))
        self.reject(lambda p:p["second_five_guide_cards"][2].update(html_description_line=6))
        self.reject(lambda p:p["second_five_guide_cards"][3].update(video_route_path="/fake/"))

    def test_colluding_hash_changes_do_not_bypass_custody(self):
        def tamper(p):
            p["second_five_guide_cards"][4]["description_sha256"]="0"*64
            p["source_relative_evidence"][4]["publisher_description_sha256"]="0"*64
        self.reject(tamper)

    def test_prior_publisher_datetime_anomaly_must_survive(self):
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"].clear())
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"][0].update(air_order_resolution="FIXED"))
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"][1].update(later_guide_slot=9))

    def test_character_memory_not_objective_history(self):
        self.reject(lambda p:p["source_relative_evidence"][1].update(claim_mode="OBJECTIVE_MEMORY"))
        self.reject(lambda p:p["typed_assertions"][1].update(narrative_claim_kind="TIME_TRAVEL_VERIFIED"))

    def test_accusation_not_evidence_of_actual_espionage(self):
        self.reject(lambda p:p["source_relative_evidence"][2].update(claim_mode="CONFIRMED_ESPIONAGE"))
        self.reject(lambda p:p["typed_assertions"][2].update(narrative_claim_kind="ACTUAL_SPYING"))

    def test_hoshi_identity_question_not_proof_of_replacement(self):
        self.reject(lambda p:p["source_relative_evidence"][4].update(claim_mode="IDENTITY_SWAP_PROVEN"))
        self.reject(lambda p:p["typed_assertions"][4].update(narrative_claim_kind="CHARACTER_REPLACED"))
        self.reject(lambda p:p["typed_assertions"][4].update(frame_claim_status="EPISODE_CLOSE_READ"))

    def test_evidence_and_assertion_link_custody(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(locator="unknown"))
        self.reject(lambda p:p["source_relative_evidence"][3].update(original_paraphrase=""))
        self.reject(lambda p:p["typed_assertions"][3].update(predicate="EPISODE_TRUTH"))
        self.reject(lambda p:p["typed_assertions"][1].update(evidence_id="ent-s2-e06-guide-description"))

    def test_global_identity_and_duplicate_ids_rejected(self):
        self.reject(lambda p:p["local_entities"][0].update(canonical_work_id="ent-s2-e06"))
        self.reject(lambda p:p["local_entities"][1].update(id="ent-s2-e01-publisher-card"))
        self.reject(lambda p:p["source_relative_evidence"][2].update(id="ent-s2-e07-guide-description"))

    def test_strict_integer_episode_cards(self):
        self.reject(lambda p:p["second_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p:p["second_five_guide_cards"][1].update(episode=7.0))
        self.reject(lambda p:p["local_entities"][0].update(source_local_episode_hint=6.0))

    def test_held_summary_cannot_be_accepted_coverage(self):
        self.reject(lambda p:p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=26))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=10))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(status="CLOSE_READ"))


if __name__=="__main__":
    unittest.main()
