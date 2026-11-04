"""Hostile provenance, identity and publisher-claim regression tests E11–E15."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, SIBLING, read_json, validate


class EnterpriseS2ThirdFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE/"records.json")
        cls.predecessors=[
            (read_json(SIBLING/folder/"records.json"),
             hashlib.sha256((SIBLING/folder/"records.json").read_bytes()).hexdigest())
            for folder,*_ in PRIOR
        ]

    def reject(self,mutate):
        packet=copy.deepcopy(self.packet)
        mutate(packet)
        with self.assertRaises(ValueError):
            validate(packet,self.predecessors)

    def test_packet_valid(self):
        validate(self.packet,self.predecessors)

    def test_exact_original_source_parser(self):
        p=publisher_parser()
        self.assertEqual(p.URL,"https://www.paramountplus.com/shows/enterprise/episodes/2/")
        self.assertEqual(p.SERIES_PREFIX,"Star Trek: Enterprise - ")

    def test_both_predecessor_sha_required(self):
        for i in range(2):
            previous=copy.deepcopy(self.predecessors)
            previous[i]=(previous[i][0],"0"*64)
            with self.subTest(i=i),self.assertRaises(ValueError):
                validate(self.packet,previous)

    def test_prior_unearned_status_fails_closed(self):
        previous=copy.deepcopy(self.predecessors)
        previous[0][0]["accepted_work_effect"]="ACCEPTED"
        with self.assertRaises(ValueError):
            validate(self.packet,previous)

    def test_exact_predecessor_commit_and_scope(self):
        for i in range(2):
            with self.subTest(i=i):
                self.reject(lambda p:p["prior_batches"][i].update(commit="wrong"))
                self.reject(lambda p:p["prior_batches"][i].update(source_response_sha256="0"*64))
                self.reject(lambda p:p["prior_batches"][i].update(episode_scope=[1,15]))

    def test_no_protected_effects(self):
        for field in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect",
                      "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p:p.update({field:"ACCEPTED"}))

    def test_unearned_source_read_claims_rejected(self):
        for field in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
            with self.subTest(field=field):
                self.reject(lambda p:p.update({field:True}))

    def test_full_first_party_response_receipt(self):
        for changed in (
            {"response_http_status":404},{"raw_response_bytes":1},
            {"raw_response_sha256":"0"*64},{"response_date_header":"wrong"},
            {"observed_at_utc":"wrong"},{"raw_html_committed":True},
            {"url":"https://other.example/"},{"independence_group":"independent:mirror"},
        ):
            with self.subTest(changed=changed):
                self.reject(lambda p:p["source"].update(changed))

    def test_26_observed_cards_not_all_content_analyzed(self):
        self.reject(lambda p:p.update(observed_full_guide_card_count=15))
        self.reject(lambda p:p["all_26_guide_cards"].pop())
        self.reject(lambda p:p.update(all_26_metadata_and_description_fingerprints_match_two_prior_snapshots=False))
        self.reject(lambda p:p.update(raw_html_digest_differs_from_two_predecessors=False))
        self.reject(lambda p:p["all_26_guide_cards"][25].update(description_sha256="0"*64))

    def test_exact_five_selected_descriptions(self):
        self.reject(lambda p:p.update(selected_tranche_episode_ordinals=[10,11,12,13,14]))
        self.reject(lambda p:p.update(third_five_source_descriptions_inspected=26))
        self.reject(lambda p:p.update(third_five_analytical_synopses_proposed=26))
        self.reject(lambda p:p.update(third_five_description_total_chars=530))
        self.reject(lambda p:p["third_five_guide_cards"].pop())
        self.reject(lambda p:p["third_five_guide_cards"].reverse())

    def test_source_fingerprints_and_line_locs(self):
        self.reject(lambda p:p["third_five_guide_cards"][0].update(title="Incorrect"))
        self.reject(lambda p:p["third_five_guide_cards"][1].update(description_sha256="0"*64))
        self.reject(lambda p:p["third_five_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p:p["third_five_guide_cards"][3].update(video_route_path="/wrong/"))

    def test_collusive_hash_tamper_is_detected(self):
        def corrupt(p):
            p["third_five_guide_cards"][4]["description_sha256"]="0"*64
            p["source_relative_evidence"][4]["publisher_description_sha256"]="0"*64
        self.reject(corrupt)

    def test_publisher_timestamp_inversions_are_preserved(self):
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"].clear())
        self.reject(lambda p:p["prior_source_local_publisher_datetime_anomalies_reobserved"][0].update(air_order_resolution="FIXED"))

    def test_publisher_claims_not_actual_episode_events(self):
        self.reject(lambda p:p["typed_assertions"][0].update(predicate="CANONICAL_EPISODE_FACT"))
        self.reject(lambda p:p["typed_assertions"][1].update(status="AUDIOVISUAL_CLOSE_READ"))
        self.reject(lambda p:p["typed_assertions"][4].update(frame_claim_status="VIDEO_VERIFIED"))
        self.reject(lambda p:p["source_relative_evidence"][3].update(claim_mode="DISEASE_MEDICALLY_VERIFIED"))

    def test_paraphrase_custody_source_relative(self):
        self.reject(lambda p:p["source_relative_evidence"][0].update(locator="unknown"))
        self.reject(lambda p:p["source_relative_evidence"][2].update(original_paraphrase=""))
        self.reject(lambda p:p["typed_assertions"][2].update(evidence_id="ent-s2-e14-guide-description"))

    def test_no_canonical_work_and_no_duplicate_local_ids(self):
        self.reject(lambda p:p["local_entities"][0].update(canonical_work_id="enterprise:s2:e11"))
        self.reject(lambda p:p["local_entities"][1].update(id="ent-s2-e02-publisher-card"))
        self.reject(lambda p:p["source_relative_evidence"][1].update(id="ent-s2-e11-guide-description"))

    def test_strict_episode_card_numerics(self):
        self.reject(lambda p:p["third_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p:p["third_five_guide_cards"][1].update(display_order=12.0))
        self.reject(lambda p:p["local_entities"][4].update(source_local_episode_hint=15.0))

    def test_held_count_cannot_promote_coverage(self):
        self.reject(lambda p:p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=26))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=15))
        self.reject(lambda p:p["held_season_description_partition_summary"].update(status="EPISODE_CONTENT_CLOSE_READ"))


if __name__=="__main__":
    unittest.main()
