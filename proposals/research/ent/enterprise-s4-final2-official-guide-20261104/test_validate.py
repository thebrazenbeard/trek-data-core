"""Adversarial gates for complete-but-HELD Enterprise S4 publisher descriptions."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, SIBLING, read_json, validate


class EnterpriseS4FinalTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(HERE / "records.json")
        cls.previous=[
            (read_json(SIBLING / folder / "records.json"),
             hashlib.sha256((SIBLING / folder / "records.json").read_bytes()).hexdigest())
            for folder, *_ in PRIOR
        ]

    def reject(self, mutation):
        changed=copy.deepcopy(self.packet)
        mutation(changed)
        with self.assertRaises(ValueError):
            validate(changed,self.previous)

    def test_valid_packet_passes(self):
        validate(self.packet,self.previous)

    def test_reuses_original_first_party_parser(self):
        self.assertEqual(publisher_parser().URL, "https://www.paramountplus.com/shows/enterprise/episodes/4/")

    def test_each_prior_file_digest_is_custodied(self):
        for i in range(4):
            with self.subTest(i=i):
                changed=copy.deepcopy(self.previous)
                changed[i]=(changed[i][0],"0"*64)
                with self.assertRaises(ValueError):
                    validate(self.packet,changed)

    def test_predecessor_unearned_acceptance_rejected(self):
        changed=copy.deepcopy(self.previous)
        changed[3][0]["accepted_work_effect"]="ADMITTED"
        with self.assertRaises(ValueError):
            validate(self.packet,changed)

    def test_each_prior_exact_receipt_and_scope(self):
        for i in range(4):
            with self.subTest(i=i):
                self.reject(lambda p: p["prior_batches"][i].update(commit="wrong"))
                self.reject(lambda p: p["prior_batches"][i].update(source_response_sha256="0"*64))
                self.reject(lambda p: p["prior_batches"][i].update(episode_scope=[1,22]))

    def test_no_unearned_protected_effects(self):
        for field in ("accepted_source_binding_effect", "accepted_work_effect","coverage_effect",
                      "denominator_effect","reconciliation_effect","explorer_synopsis_release_effect"):
            with self.subTest(field=field):
                self.reject(lambda p: p.update({field:"ACCEPTED"}))

    def test_no_audiovisual_transcript_image_read_claims(self):
        for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
            with self.subTest(flag=flag):
                self.reject(lambda p: p.update({flag:True}))

    def test_complete_first_party_receipt_and_lineage_pinned(self):
        for changed in (
            {"response_http_status":404}, {"raw_response_bytes":1}, {"raw_response_sha256":"0"*64},
            {"response_date_header":"OTHER"}, {"observed_at_utc":"OTHER"}, {"raw_html_committed":True},
            {"independence_group":"independent:multiple-views"}, {"url":"https://memory-alpha.fandom.com/"},
        ):
            with self.subTest(changed=changed):
                self.reject(lambda p: p["source"].update(changed))

    def test_four_source_reads_are_not_independent_witnesses(self):
        self.reject(lambda p: p["source"].update(independence_group="five-independent-sources"))
        self.reject(lambda p: p["prior_batches"][0].update(source_response_sha256="8790bff4111c5ad3b0bafc1491189373998eae3b3498addddb6594d7237418a9"))

    def test_full_22_fingerprint_context_noninvented(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=23))
        self.reject(lambda p: p["all_22_guide_cards"].append({"episode":23,"title":"Imaginary"}))
        self.reject(lambda p: p["all_22_guide_cards"][20].update(description_sha256="0"*64))
        self.reject(lambda p: p.update(all_22_metadata_and_description_fingerprints_match_four_prior_snapshots=False))
        self.reject(lambda p: p.update(raw_html_digest_differs_from_four_predecessors=False))

    def test_exactly_final_two_descriptions(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[20,21,22]))
        self.reject(lambda p: p.update(final_two_source_descriptions_inspected=22))
        self.reject(lambda p: p.update(final_two_analytical_synopses_proposed=22))
        self.reject(lambda p: p.update(final_two_description_total_chars=250))
        self.reject(lambda p: p["final_two_guide_cards"].pop())
        self.reject(lambda p: p["final_two_guide_cards"].reverse())

    def test_source_hash_and_html_locator_tamper(self):
        self.reject(lambda p: p["final_two_guide_cards"][0].update(description_sha256="0"*64))
        self.reject(lambda p: p["final_two_guide_cards"][1].update(html_description_line=2090))
        self.reject(lambda p: p["final_two_guide_cards"][0].update(title="Terra Other"))
        self.reject(lambda p: p["final_two_guide_cards"][1].update(video_route_path="/wrong/"))

    def test_collusive_source_card_and_evidence_fingerprint_tamper(self):
        def alter(p):
            p["final_two_guide_cards"][1]["description_sha256"]="0"*64
            p["source_relative_evidence"][1]["publisher_description_sha256"]="0"*64
        self.reject(alter)

    def test_e22_display_title_not_silently_normalized(self):
        self.reject(lambda p: p["final_two_guide_cards"][1].update(title="These Are The Voyages"))
        self.reject(lambda p: p["all_22_guide_cards"][21].update(analytics_series_title="These Are the Voyages"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(status="RESOLVED"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(global_reconciliation_effect="RECONCILED"))

    def test_e22_two_source_local_competing_title_tokens_kept(self):
        self.reject(lambda p: p["source_local_competing_title_tokens"]["card_html_h2"].update(value="These Are The Voyages"))
        self.reject(lambda p: p["source_local_competing_title_tokens"]["analytics_series_prefix_title"].update(value="These Are the Voyages"))
        self.reject(lambda p: p["source_local_competing_title_tokens"].update(chosen_canonical_title="These Are the Voyages"))
        self.reject(lambda p: p["source_local_competing_title_tokens"].update(exact_spelling_reconciliation="ACCEPTED"))
        self.reject(lambda p: p["source_local_competing_title_tokens"].update(casefold_identity_consistent=False))

    def test_held_completion_never_becomes_episode_coverage(self):
        self.reject(lambda p: p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=23))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=1))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=22))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(status="EPISODES_CLOSE_READ"))

    def test_no_work_identity_or_id_collision(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="ent:s4:e21"))
        self.reject(lambda p: p["local_entities"][1].update(id="ent-s4-e20-publisher-card"))
        self.reject(lambda p: p["source_relative_evidence"][1].update(id="ent-s4-e21-guide-description"))

    def test_source_evidence_attribution_not_episode_verified_truth(self):
        self.reject(lambda p: p["typed_assertions"][1].update(predicate="VIDEO_PROVES"))
        self.reject(lambda p: p["typed_assertions"][0].update(status="CLOSE_READ"))
        self.reject(lambda p: p["typed_assertions"][1].update(frame_claim_status="ACTUAL_VIDEO_VERIFIED"))
        self.reject(lambda p: p["source_relative_evidence"][0].update(locator="unknown"))
        self.reject(lambda p: p["source_relative_evidence"][1].update(original_paraphrase=""))

    def test_strict_source_ordinal_and_numeric_identity(self):
        self.reject(lambda p: p["final_two_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["final_two_guide_cards"][1].update(episode=22.0))
        self.reject(lambda p: p["local_entities"][0].update(source_local_episode_hint=23))


if __name__=="__main__":
    unittest.main()
