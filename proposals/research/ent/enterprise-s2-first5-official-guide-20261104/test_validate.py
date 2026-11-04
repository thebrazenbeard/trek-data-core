"""Hostile claims/lineage/card-count regression gates for ENT S2 first five."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import URL, SERIES_PREFIX, parse_page
from validate import DISCOVERY, HERE, read_json, validate


class EnterpriseS2FirstFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE/"records.json")
        cls.discovery=read_json(DISCOVERY)
        cls.digest=hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()

    def reject(self,mutation):
        changed=copy.deepcopy(self.packet)
        mutation(changed)
        with self.assertRaises(ValueError):
            validate(changed,self.discovery,self.digest)

    def test_held_packet_valid(self):
        validate(self.packet,self.discovery,self.digest)

    def test_publisher_parser_exact_scope(self):
        self.assertEqual(URL,"https://www.paramountplus.com/shows/enterprise/episodes/2/")
        self.assertEqual(SERIES_PREFIX,"Star Trek: Enterprise - ")

    def test_parser_refuses_non26_card_html(self):
        with self.assertRaises(ValueError):
            parse_page("<html><body>No publisher cards</body></html>")

    def test_accepted_discovery_digest_must_match(self):
        with self.assertRaises(ValueError):
            validate(self.packet,self.discovery,"0"*64)

    def test_discovery_remains_candidate_not_acceptance(self):
        changed=copy.deepcopy(self.discovery)
        changed["proposal_status"]="WORK_ACCEPTED"
        with self.assertRaises(ValueError):
            validate(self.packet,changed,self.digest)

    def test_discovery_no_work_binding(self):
        changed=copy.deepcopy(self.discovery)
        changed["accepted_work_effect"]="ACCEPTED"
        with self.assertRaises(ValueError):
            validate(self.packet,changed,self.digest)

    def test_all_protected_effects_fail_closed(self):
        for field in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect",
                      "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p: p.update({field:"ACCEPTED"}))

    def test_unearned_audiovisual_or_image_claims_fail(self):
        for field in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
            with self.subTest(field=field):
                self.reject(lambda p: p.update({field:True}))

    def test_full_first_party_receipt_pinned(self):
        for change in (
            {"url":"https://another.example/"},{"independence_group":"independent:two"},
            {"response_http_status":404},{"raw_response_bytes":1},{"raw_response_sha256":"0"*64},
            {"response_date_header":"other"},{"observed_at_utc":"other"},{"raw_html_committed":True},
        ):
            with self.subTest(change=change):
                self.reject(lambda p: p["source"].update(change))

    def test_full26_cards_not_all_episodes_read(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=5))
        self.reject(lambda p: p["all_26_guide_cards"].pop())
        self.reject(lambda p: p.update(first_five_source_descriptions_inspected=26))
        self.reject(lambda p: p.update(first_five_analytical_synopses_proposed=26))

    def test_exact_first5_selection_and_order(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[1,2,3,4,6]))
        self.reject(lambda p: p["first_five_guide_cards"].reverse())
        self.reject(lambda p: p["first_five_guide_cards"].append({"episode":6}))

    def test_title_source_card_and_description_hash(self):
        self.reject(lambda p: p["first_five_guide_cards"][0].update(title="Invented"))
        self.reject(lambda p: p["first_five_guide_cards"][2].update(description_sha256="0"*64))
        self.reject(lambda p: p["first_five_guide_cards"][4].update(html_description_line=99))
        self.reject(lambda p: p["all_26_guide_cards"][0].update(title="Invented"))

    def test_collusive_source_and_evidence_hash_change(self):
        def tamper(p):
            p["first_five_guide_cards"][1]["description_sha256"]="0"*64
            p["source_relative_evidence"][1]["publisher_description_sha256"]="0"*64
        self.reject(tamper)

    def test_source_local_datetime_inversions_not_rewritten(self):
        self.reject(lambda p: p["source_local_publisher_datetime_anomalies"].clear())
        self.reject(lambda p: p["source_local_publisher_datetime_anomalies"][0].update(air_order_resolution="CORRECTED"))
        self.reject(lambda p: p["first_five_guide_cards"][0].update(publisher_datetime="2002-09-10T21:00:00-07:00"))

    def test_in_universe_tpol_account_not_objective_canon(self):
        self.reject(lambda p: p["typed_assertions"][1].update(narrative_claim_kind="OBJECTIVE_FIRST_CONTACT"))
        self.reject(lambda p: p["source_relative_evidence"][1].update(claim_mode="CHARACTER_REPORT_VERIFIED"))
        self.reject(lambda p: p["typed_assertions"][1].update(predicate="EPISODE_PROVES"))

    def test_source_relative_claim_not_video_close_read(self):
        self.reject(lambda p: p["typed_assertions"][0].update(status="EPISODE_CLOSE_READ"))
        self.reject(lambda p: p["typed_assertions"][4].update(evidence_id="ent-s2-e04-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][3].update(locator="unknown"))
        self.reject(lambda p: p["source_relative_evidence"][2].update(original_paraphrase=""))

    def test_identity_collision_or_canonical_work_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="enterprise:s2e1"))
        self.reject(lambda p: p["local_entities"][4].update(id="ent-s2-e01-publisher-card"))
        self.reject(lambda p: p["source_relative_evidence"][0].update(id="ent-s2-e02-guide-description"))

    def test_strict_integer_ordinal_not_bool_float(self):
        self.reject(lambda p: p["first_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["first_five_guide_cards"][1].update(analytics_ordinal=2.0))
        self.reject(lambda p: p["local_entities"][0].update(source_local_episode_hint=1.0))

    def test_held_summary_not_earned_coverage(self):
        self.reject(lambda p: p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=26))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=5))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(status="EPISODES_CLOSE_READ"))


if __name__=="__main__":
    unittest.main()
