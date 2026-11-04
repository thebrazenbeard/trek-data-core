"""Hostile custody tests for ENT S4 third publisher-description tranche."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, read_json, validate


class EnterpriseS4ThirdFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE / "records.json")
        cls.previous=[(read_json(path),hashlib.sha256(path.read_bytes()).hexdigest()) for path,*_ in PRIOR]

    def reject(self, mutation):
        packet=copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaises(ValueError):
            validate(packet,self.previous)

    def test_exact_held_packet_passes(self):
        validate(self.packet,self.previous)

    def test_exact_predecessor_parser(self):
        self.assertEqual(publisher_parser().URL,"https://www.paramountplus.com/shows/enterprise/episodes/4/")

    def test_both_predecessor_file_sha_must_match(self):
        for i in range(2):
            with self.subTest(i=i):
                prior=copy.deepcopy(self.previous)
                prior[i]=(prior[i][0],"0"*64)
                with self.assertRaises(ValueError):
                    validate(self.packet,prior)

    def test_predecessor_protected_effect_rejected(self):
        prior=copy.deepcopy(self.previous)
        prior[1][0]["accepted_work_effect"]="ADMITTED"
        with self.assertRaises(ValueError):
            validate(self.packet,prior)

    def test_prior_exact_commit_receipt_and_scope(self):
        for i in range(2):
            with self.subTest(i=i):
                self.reject(lambda p: p["prior_batches"][i].update(commit="wrong"))
                self.reject(lambda p: p["prior_batches"][i].update(source_response_sha256="0"*64))
                self.reject(lambda p: p["prior_batches"][i].update(episode_scope=[1,15]))

    def test_no_protected_effects(self):
        for field in ("accepted_source_binding_effect","accepted_work_effect","coverage_effect","denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p: p.update({field:"ACCEPTED"}))

    def test_no_audiovisual_or_image_read_claims(self):
        for field in ("episode_content_watched","transcripts_read","image_bytes_fetched"):
            with self.subTest(field=field):
                self.reject(lambda p: p.update({field:True}))

    def test_full_source_receipt_pinned(self):
        cases=[{"raw_response_sha256":"0"*64},{"raw_response_bytes":1},{"response_http_status":404},{"response_date_header":"other"},{"observed_at_utc":"other"},{"raw_html_committed":True},{"url":"https://other.site/"},{"independence_group":"independent:clone"}]
        for case in cases:
            with self.subTest(case=case):
                self.reject(lambda p: p["source"].update(case))

    def test_22_source_card_context_not_22_processed_episodes(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=5))
        self.reject(lambda p: p.update(third_five_source_descriptions_inspected=22))
        self.reject(lambda p: p.update(third_five_analytical_synopses_proposed=22))
        self.reject(lambda p: p.update(third_five_description_total_chars=720))

    def test_all_22_cards_match_exact_predecessors(self):
        self.reject(lambda p: p.update(all_22_metadata_and_description_fingerprints_match_two_prior_snapshots=False))
        self.reject(lambda p: p.update(raw_html_digest_differs_from_two_predecessors=False))
        self.reject(lambda p: p["all_22_guide_cards"].pop())
        self.reject(lambda p: p["all_22_guide_cards"][20].update(description_sha256="0"*64))

    def test_exclusive_third_five_scope(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[10,11,12,13,14]))
        self.reject(lambda p: p["third_five_guide_cards"].reverse())
        self.reject(lambda p: p["third_five_guide_cards"].pop())

    def test_card_metadata_description_hash_and_line_custody(self):
        self.reject(lambda p: p["third_five_guide_cards"][0].update(title="Made Up"))
        self.reject(lambda p: p["third_five_guide_cards"][0].update(description_sha256="0"*64))
        self.reject(lambda p: p["third_five_guide_cards"][0].update(html_description_line=1))
        self.reject(lambda p: p["third_five_guide_cards"][4].update(video_route_path="/fake/"))

    def test_collusive_metadata_evidence_hash_tamper(self):
        def tamper(p):
            p["third_five_guide_cards"][2]["description_sha256"]="0"*64
            p["source_relative_evidence"][2]["publisher_description_sha256"]="0"*64
        self.reject(tamper)

    def test_e22_source_internal_case_variant_not_normalized(self):
        self.reject(lambda p: p["all_22_guide_cards"][21].update(analytics_series_title="These Are the Voyages"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(status="RESOLVED"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(global_reconciliation_effect="ADMITTED"))

    def test_summary_not_coverage_or_final(self):
        self.reject(lambda p: p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=22))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=15))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(status="CLOSE_READ"))

    def test_local_id_collision_and_unearned_identity_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="ent:s4:e11"))
        self.reject(lambda p: p["source_relative_evidence"][0].update(id="ent-s4-e10-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][2].update(id="ent-s4-e12-guide-description"))

    def test_source_claim_separation(self):
        self.reject(lambda p: p["typed_assertions"][0].update(predicate="EPISODE_TRUTH"))
        self.reject(lambda p: p["typed_assertions"][1].update(status="VIDEO_CLOSE_READ"))
        self.reject(lambda p: p["typed_assertions"][2].update(evidence_id="ent-s4-e12-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][3].update(locator="unknown"))
        self.reject(lambda p: p["source_relative_evidence"][4].update(original_paraphrase=""))

    def test_strict_ordinal_numeric_type(self):
        self.reject(lambda p: p["third_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["third_five_guide_cards"][0].update(episode=11.0))


if __name__ == "__main__":
    unittest.main()
