"""Hostile date, temporal/identity, source custody and scope falsifiers."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, SIBLING, read_json, validate


class EnterpriseS2FourthFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE/"records.json")
        cls.predecessors=[
            (read_json(SIBLING/folder/"records.json"),
             hashlib.sha256((SIBLING/folder/"records.json").read_bytes()).hexdigest())
            for folder,*_ in PRIOR
        ]

    def reject(self,mutate):
        changed=copy.deepcopy(self.packet)
        mutate(changed)
        with self.assertRaises(ValueError):
            validate(changed,self.predecessors)

    def test_packet_passes(self):
        validate(self.packet,self.predecessors)

    def test_reuses_exact_original_26_card_parser(self):
        p=publisher_parser()
        self.assertEqual(p.URL,"https://www.paramountplus.com/shows/enterprise/episodes/2/")
        self.assertEqual(p.SERIES_PREFIX,"Star Trek: Enterprise - ")

    def test_three_predecessor_hashes_must_match(self):
        for i in range(3):
            with self.subTest(i=i):
                previous=copy.deepcopy(self.predecessors)
                previous[i]=(previous[i][0],"0"*64)
                with self.assertRaises(ValueError):
                    validate(self.packet,previous)

    def test_predecessor_accepted_work_claim_rejected(self):
        previous=copy.deepcopy(self.predecessors)
        previous[1][0]["accepted_work_effect"]="ADMITTED"
        with self.assertRaises(ValueError):
            validate(self.packet,previous)

    def test_exact_prior_commit_source_and_ordinal_scopes(self):
        for i in range(3):
            with self.subTest(i=i):
                self.reject(lambda p:p["prior_batches"][i].update(commit="wrong"))
                self.reject(lambda p:p["prior_batches"][i].update(source_response_sha256="0"*64))
                self.reject(lambda p:p["prior_batches"][i].update(episode_scope=[1,20]))

    def test_protected_effects_rejected(self):
        for field in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect",
                      "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p:p.update({field:"ACCEPTED"}))

    def test_unearned_media_read_claims_rejected(self):
        for field in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
            with self.subTest(field=field):
                self.reject(lambda p:p.update({field:True}))

    def test_first_party_full_source_receipt_and_lineage(self):
        for change in (
            {"response_http_status":404},{"raw_response_bytes":1},
            {"raw_response_sha256":"0"*64},{"response_date_header":"wrong"},
            {"observed_at_utc":"wrong"},{"raw_html_committed":True},
            {"url":"https://elsewhere.example/"},{"independence_group":"independent:copy"},
        ):
            with self.subTest(change=change):
                self.reject(lambda p:p["source"].update(change))

    def test_26_metadata_cards_not_26_watched_episodes(self):
        self.reject(lambda p:p.update(observed_full_guide_card_count=20))
        self.reject(lambda p:p.update(all_26_metadata_and_description_fingerprints_match_three_prior_snapshots=False))
        self.reject(lambda p:p.update(raw_html_digest_differs_from_three_predecessors=False))
        self.reject(lambda p:p["all_26_guide_cards"].pop())
        self.reject(lambda p:p["all_26_guide_cards"][25].update(description_sha256="0"*64))

    def test_exclusive_five_description_scope(self):
        self.reject(lambda p:p.update(selected_tranche_episode_ordinals=[15,16,17,18,19]))
        self.reject(lambda p:p.update(fourth_five_source_descriptions_inspected=26))
        self.reject(lambda p:p.update(fourth_five_analytical_synopses_proposed=26))
        self.reject(lambda p:p.update(fourth_five_description_total_chars=676))
        self.reject(lambda p:p["fourth_five_guide_cards"].reverse())
        self.reject(lambda p:p["fourth_five_guide_cards"].pop())

    def test_metadata_title_line_and_hash_custody(self):
        self.reject(lambda p:p["fourth_five_guide_cards"][0].update(title="Future Past"))
        self.reject(lambda p:p["fourth_five_guide_cards"][1].update(description_sha256="0"*64))
        self.reject(lambda p:p["fourth_five_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p:p["fourth_five_guide_cards"][3].update(video_route_path="/wrong/"))

    def test_collusive_source_and_evidence_digest_rejected(self):
        def tamper(p):
            p["fourth_five_guide_cards"][2]["description_sha256"]="0"*64
            p["source_relative_evidence"][2]["publisher_description_sha256"]="0"*64
        self.reject(tamper)

    def test_prior_publisher_date_inversions_still_unresolved(self):
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"].clear())
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"][1].update(air_order_resolution="SORTED"))

    def test_prior_speech_memory_accusation_identity_holds_still_active(self):
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"].clear())
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"][0].update(claim_kind="OBJECTIVE_HISTORY"))
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"][3].update(claim_kind="IDENTITY_REPLACEMENT_PROVEN"))

    def test_apparent_corpse_not_confirmed_identity_death(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(claim_mode="HUMAN_DEATH_CONFIRMED"))
        self.reject(lambda p:p["typed_assertions"][0].update(narrative_claim_kind="IDENTITY_VERIFIED"))

    def test_wrongful_arrest_and_tribunal_are_not_guilt(self):
        self.reject(lambda p:p["source_relative_evidence"][1].update(claim_mode="CRIMINAL_GUILT_CONFIRMED"))
        self.reject(lambda p:p["typed_assertions"][3].update(narrative_claim_kind="CONSPIRACY_PROVEN"))

    def test_consciousness_exchange_intention_not_completed_identity_transfer(self):
        self.reject(lambda p:p["source_relative_evidence"][2].update(claim_mode="CONSCIOUSNESS_TRANSFER_COMPLETED"))
        self.reject(lambda p:p["typed_assertions"][2].update(narrative_claim_kind="PERSISTENT_IDENTITY_SWAP_VERIFIED"))
        self.reject(lambda p:p["typed_assertions"][2].update(frame_claim_status="VIDEO_CLOSE_READ"))

    def test_source_evidence_and_assertion_links(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(locator="unknown"))
        self.reject(lambda p:p["source_relative_evidence"][4].update(original_paraphrase=""))
        self.reject(lambda p:p["typed_assertions"][3].update(predicate="EPISODE_PROVES"))
        self.reject(lambda p:p["typed_assertions"][1].update(evidence_id="ent-s2-e18-guide-description"))

    def test_no_canonical_work_or_local_id_collision(self):
        self.reject(lambda p:p["local_entities"][0].update(canonical_work_id="ent:s2:e16"))
        self.reject(lambda p:p["local_entities"][1].update(id="ent-s2-e15-publisher-card"))
        self.reject(lambda p:p["source_relative_evidence"][2].update(id="ent-s2-e17-guide-description"))

    def test_strict_source_numeric_ordinals(self):
        self.reject(lambda p:p["fourth_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p:p["fourth_five_guide_cards"][1].update(display_order=17.0))
        self.reject(lambda p:p["local_entities"][2].update(source_local_episode_hint=18.0))

    def test_held_description_counts_cannot_upgrade_coverage(self):
        self.reject(lambda p:p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=26))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=20))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(status="CLOSE_READ"))


if __name__=="__main__":
    unittest.main()
