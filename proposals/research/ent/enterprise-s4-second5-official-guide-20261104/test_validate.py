"""Hostile second-tranche ENT S4 publisher source-custody regressions (offline)."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, FIRST, read_json, validate


class EnterpriseS4SecondFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.previous = read_json(FIRST)
        cls.previous_sha = hashlib.sha256(FIRST.read_bytes()).hexdigest()

    def reject(self, modifier):
        packet = copy.deepcopy(self.packet)
        modifier(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.previous, self.previous_sha)

    def test_held_packet_passes(self):
        validate(self.packet, self.previous, self.previous_sha)

    def test_source_parser_custody(self):
        self.assertEqual(publisher_parser().URL, "https://www.paramountplus.com/shows/enterprise/episodes/4/")

    def test_exact_predecessor_sha_drift_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.packet, self.previous, "0" * 64)

    def test_predecessor_promoted_to_work_or_lineage_forged_rejected(self):
        for patch in ({"accepted_work_effect":"ADMITTED"}, {"coverage_effect":"FIVE_EPISODES_CLOSE_READ"}):
            prior = copy.deepcopy(self.previous)
            prior.update(patch)
            with self.assertRaises(ValueError):
                validate(self.packet, prior, self.previous_sha)
        prior = copy.deepcopy(self.previous)
        prior["source"]["independence_group"] = "independent:copy"
        with self.assertRaises(ValueError):
            validate(self.packet, prior, self.previous_sha)

    def test_prior_commit_source_or_scope_forgery_rejected(self):
        self.reject(lambda p: p["prior_batch"].update(commit="wrong"))
        self.reject(lambda p: p["prior_batch"].update(source_response_sha256="0"*64))
        self.reject(lambda p: p["prior_batch"].update(episode_scope=[1,10]))

    def test_protected_effects_stay_none(self):
        for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key:"ADMITTED"}))

    def test_no_episode_content_or_media_claims(self):
        for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key:True}))

    def test_full_source_receipt_must_match(self):
        mutations = (
            {"raw_response_bytes":5}, {"raw_response_sha256":"0"*64},
            {"response_http_status":404}, {"raw_html_committed":True},
            {"response_date_header":"Thu, 05 Nov 2026 00:00:00 GMT"},
            {"observed_at_utc":"2026-11-05T00:00:00Z"},
            {"url":"https://example.org/"},
            {"independence_group":"independent:myclone"},
        )
        for item in mutations:
            with self.subTest(change=item):
                self.reject(lambda p: p["source"].update(item))

    def test_full_guide_context_cannot_be_inflated(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=10))
        self.reject(lambda p: p.update(second_five_analytical_synopses_proposed=22))
        self.reject(lambda p: p.update(second_five_source_descriptions_inspected=4))
        self.reject(lambda p: p.update(second_five_description_total_chars=123))

    def test_22_normalized_card_agreement_not_new_independent_source(self):
        self.reject(lambda p: p.update(all_22_metadata_and_description_fingerprints_match_prior_snapshot=False))
        self.reject(lambda p: p.update(raw_html_digest_differs_from_predecessor=False))
        self.reject(lambda p: p["all_22_guide_cards"].pop())
        self.reject(lambda p: p["all_22_guide_cards"][0].update(description_sha256="0"*64))

    def test_source_episode_scope_exact_five_new_slots(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[5,6,7,8,9]))
        self.reject(lambda p: p["second_five_guide_cards"].pop())
        self.reject(lambda p: p["second_five_guide_cards"].reverse())

    def test_source_title_hash_line_and_route_tamper_rejected(self):
        self.reject(lambda p: p["second_five_guide_cards"][0].update(title="Unrelated"))
        self.reject(lambda p: p["second_five_guide_cards"][2].update(description_sha256="0"*64))
        self.reject(lambda p: p["second_five_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p: p["second_five_guide_cards"][4].update(video_route_path="/fake/"))

    def test_collusive_card_evidence_hash_edit_does_not_escape(self):
        def collude(p):
            p["second_five_guide_cards"][0]["description_sha256"] = "0"*64
            p["source_relative_evidence"][0]["publisher_description_sha256"] = "0"*64
        self.reject(collude)

    def test_e22_capitalization_variant_stays_unresolved(self):
        self.reject(lambda p: p["all_22_guide_cards"][21].update(analytics_series_title="These Are the Voyages"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(status="RESOLVED"))
        self.reject(lambda p: p["source_internal_title_variant_reobserved"].update(global_reconciliation_effect="ACCEPTED"))

    def test_held_partition_count_is_not_coverage(self):
        self.reject(lambda p: p["held_season_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=22))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(remaining_unprocessed_publisher_descriptions=0))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=10))
        self.reject(lambda p: p["held_season_description_partition_summary"].update(status="CLOSE_READ"))

    def test_local_identity_no_canonical_binding_or_overlap(self):
        self.reject(lambda p: p["local_entities"][1].update(canonical_work_id="ent:s4:e07"))
        self.reject(lambda p: p["source_relative_evidence"][0].update(id="ent-s4-e05-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][4].update(id="ent-s4-e09-guide-description"))

    def test_claim_remains_publisher_attributed(self):
        self.reject(lambda p: p["typed_assertions"][0].update(predicate="OBJECTIVE_EPISODE_TRUTH"))
        self.reject(lambda p: p["typed_assertions"][1].update(status="VIDEO_CLOSE_READ"))
        self.reject(lambda p: p["typed_assertions"][2].update(evidence_id="ent-s4-e07-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][3].update(locator="unknown"))
        self.reject(lambda p: p["source_relative_evidence"][4].update(original_paraphrase=""))

    def test_ordinal_strict_type(self):
        self.reject(lambda p: p["second_five_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["second_five_guide_cards"][0].update(episode=6.0))


if __name__ == "__main__":
    unittest.main()
