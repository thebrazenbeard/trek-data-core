"""Hostile date, temporal/identity, source custody and scope falsifiers."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, SIBLING, read_json, validate


class EnterpriseS2FinalSixTests(unittest.TestCase):
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

    def test_four_predecessor_hashes_must_match(self):
        for i in range(4):
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
        for i in range(4):
            with self.subTest(i=i):
                self.reject(lambda p:p["prior_batches"][i].update(commit="wrong"))
                self.reject(lambda p:p["prior_batches"][i].update(source_response_sha256="0"*64))
                self.reject(lambda p:p["prior_batches"][i].update(episode_scope=[1,20]))

    def test_protected_effects_rejected(self):
        for field in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect",
                      "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p:p.update({field:"ACCEPTED"}))

    def test_unreviewed_extra_effect_fields_rejected(self):
        self.reject(lambda p:p.update(public_release=True))
        self.reject(lambda p:p["source"].update(rights_cleared=True))
        self.reject(lambda p:p["final_six_guide_cards"][0].update(watched=True))
        self.reject(lambda p:p["local_entities"][0].update(admitted_work_id="ent:s2:e21"))
        self.reject(lambda p:p["source_relative_evidence"][0].update(verification_status="AUDITED"))
        self.reject(lambda p:p["typed_assertions"][0].update(objective_canon=True))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(published_episodes=26))

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
        self.reject(lambda p:p.update(all_26_metadata_and_description_fingerprints_match_four_prior_snapshots=False))
        self.reject(lambda p:p.update(raw_html_digest_differs_from_four_predecessors=False))
        self.reject(lambda p:p["all_26_guide_cards"].pop())
        self.reject(lambda p:p["all_26_guide_cards"][25].update(description_sha256="0"*64))

    def test_exclusive_six_description_scope(self):
        self.reject(lambda p:p.update(selected_tranche_episode_ordinals=[20,21,22,23,24,25]))
        self.reject(lambda p:p.update(final_six_source_descriptions_inspected=26))
        self.reject(lambda p:p.update(final_six_analytical_synopses_proposed=26))
        self.reject(lambda p:p.update(final_six_description_total_chars=802))
        self.reject(lambda p:p["final_six_guide_cards"].reverse())
        self.reject(lambda p:p["final_six_guide_cards"].pop())

    def test_metadata_title_line_and_hash_custody(self):
        self.reject(lambda p:p["final_six_guide_cards"][0].update(title="Wrong Breach"))
        self.reject(lambda p:p["final_six_guide_cards"][1].update(description_sha256="0"*64))
        self.reject(lambda p:p["final_six_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p:p["final_six_guide_cards"][3].update(video_route_path="/wrong/"))

    def test_collusive_source_and_evidence_digest_rejected(self):
        def tamper(p):
            p["final_six_guide_cards"][2]["description_sha256"]="0"*64
            p["source_relative_evidence"][2]["publisher_description_sha256"]="0"*64
        self.reject(tamper)

    def test_prior_publisher_date_inversions_still_unresolved(self):
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"].clear())
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"][1].update(air_order_resolution="SORTED"))

    def test_prior_speech_memory_accusation_identity_holds_still_active(self):
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"].clear())
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"][0].update(claim_kind="OBJECTIVE_HISTORY"))
        self.reject(lambda p:p["prior_semantic_ambiguity_fixtures_reobserved"][3].update(claim_kind="IDENTITY_REPLACEMENT_PROVEN"))

    def test_extraction_assignment_not_completed_rescue(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(claim_mode="RESCUE_COMPLETED"))
        self.reject(lambda p:p["typed_assertions"][0].update(narrative_claim_kind="GEOLOGISTS_SAFELY_EVACUATED"))

    def test_vissian_social_classification_not_independent_verification(self):
        self.reject(lambda p:p["source_relative_evidence"][1].update(claim_mode="INDEPENDENT_SOCIAL_SCIENCE_VERIFIED"))
        self.reject(lambda p:p["typed_assertions"][1].update(narrative_claim_kind="BIOLOGICAL_ESSENTIALISM_CONFIRMED"))

    def test_cybernetic_bodies_not_confirmed_identity_or_life(self):
        self.reject(lambda p:p["source_relative_evidence"][2].update(claim_mode="BORG_IDENTITY_CONFIRMED"))
        self.reject(lambda p:p["typed_assertions"][2].update(narrative_claim_kind="BIOLOGICAL_LIFE_STATUS_CONFIRMED"))

    def test_reported_death_not_an_independent_witness(self):
        self.reject(lambda p:p["source_relative_evidence"][3].update(claim_mode="RIVAL_DEATH_FORENSICALLY_CONFIRMED"))
        self.reject(lambda p:p["typed_assertions"][3].update(frame_claim_status="EPISODE_VIDEO_CLOSE_READ"))

    def test_reward_intent_not_completed_payment(self):
        self.reject(lambda p:p["source_relative_evidence"][4].update(claim_mode="KLINGON_REWARD_PAID"))
        self.reject(lambda p:p["typed_assertions"][4].update(narrative_claim_kind="ARREST_CONVICTION_PROVEN"))
        self.assertNotIn("klingon authorities",self.packet["source_relative_evidence"][4]["original_paraphrase"].lower())

    def test_unknown_earth_attack_perpetrator_not_silently_resolved(self):
        self.reject(lambda p:p["source_relative_evidence"][5].update(claim_mode="ASSAILANT_IDENTIFIED"))
        self.reject(lambda p:p["typed_assertions"][5].update(narrative_claim_kind="CANONICAL_PERPETRATOR_VERIFIED"))

    def test_same_publisher_datetime_not_unique_airdate(self):
        self.assertEqual(self.packet["final_six_guide_cards"][3]["publisher_datetime"],self.packet["final_six_guide_cards"][4]["publisher_datetime"])
        self.reject(lambda p:p["final_six_guide_cards"][4].update(publisher_datetime="2003-05-14T21:00:00-07:00"))

    def test_exact_last_card_no_fictitious_27th(self):
        self.assertEqual(self.packet["final_six_guide_cards"][-1]["episode"],26)
        self.reject(lambda p:p["final_six_guide_cards"].append(copy.deepcopy(p["final_six_guide_cards"][-1])))

    def test_source_evidence_and_assertion_links(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(locator="unknown"))
        self.reject(lambda p:p["source_relative_evidence"][5].update(original_paraphrase=""))
        self.reject(lambda p:p["typed_assertions"][3].update(predicate="EPISODE_PROVES"))
        self.reject(lambda p:p["typed_assertions"][1].update(evidence_id="ent-s2-e23-guide-description"))

    def test_no_canonical_work_or_local_id_collision(self):
        self.reject(lambda p:p["local_entities"][0].update(canonical_work_id="ent:s2:e21"))
        self.reject(lambda p:p["local_entities"][1].update(id="ent-s2-e20-publisher-card"))
        self.reject(lambda p:p["source_relative_evidence"][2].update(id="ent-s2-e22-guide-description"))

    def test_strict_source_numeric_ordinals(self):
        self.reject(lambda p:p["final_six_guide_cards"][0].update(episode=True))
        self.reject(lambda p:p["final_six_guide_cards"][1].update(display_order=22.0))
        self.reject(lambda p:p["local_entities"][2].update(source_local_episode_hint=23.0))

    def test_held_description_counts_cannot_upgrade_coverage(self):
        self.reject(lambda p:p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=27))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=1))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=26))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(status="CLOSE_READ"))


if __name__=="__main__":
    unittest.main()
