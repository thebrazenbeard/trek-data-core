"""Hostile falsifiers for terminal four-card source-relative ENT S3 tranche."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import publisher_parser
from validate import HERE, PRIOR, read_json, validate


class EnterpriseS3FinalFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.predecessors = [(read_json(path), hashlib.sha256(path.read_bytes()).hexdigest()) for path, *_ in PRIOR]

    def reject(self, modifier):
        packet = copy.deepcopy(self.packet)
        modifier(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.predecessors)

    def test_clean_held_packet_passes(self):
        validate(self.packet, self.predecessors)

    def test_reuses_original_exact_source_parser(self):
        self.assertEqual(publisher_parser().URL, "https://www.paramountplus.com/shows/enterprise/episodes/3/")

    def test_every_predecessor_file_tamper_rejected(self):
        for index in range(4):
            with self.subTest(index=index):
                prior = copy.deepcopy(self.predecessors)
                prior[index] = (prior[index][0], "0" * 64)
                with self.assertRaises(ValueError):
                    validate(self.packet, prior)

    def test_each_previous_commit_and_source_digest_tamper_rejected(self):
        for index in range(4):
            with self.subTest(index=index):
                self.reject(lambda p: p["prior_batches"][index].update(commit="wrong"))
                self.reject(lambda p: p["prior_batches"][index].update(source_response_sha256="0" * 64))
                self.reject(lambda p: p["prior_batches"][index].update(episode_scope=[1, 24]))

    def test_predecessor_promoted_to_accepted_work_rejected(self):
        prior = copy.deepcopy(self.predecessors)
        prior[3][0]["accepted_work_effect"] = "ADMITTED"
        with self.assertRaises(ValueError):
            validate(self.packet, prior)

    def test_predecessor_publisher_lineage_forgery_rejected(self):
        prior = copy.deepcopy(self.predecessors)
        prior[1][0]["source"]["independence_group"] = "independent:copy"
        with self.assertRaises(ValueError):
            validate(self.packet, prior)

    def test_no_public_or_protected_effects(self):
        for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect"):
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key: "ADMITTED"}))

    def test_no_content_or_media_read_claims(self):
        for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key: True}))

    def test_source_receipt_tampering_rejected(self):
        changes = [
            {"raw_response_bytes": 1}, {"raw_response_sha256": "0" * 64},
            {"response_http_status": 404}, {"raw_html_committed": True},
            {"response_date_header": "Thu, 05 Nov 2026 00:00:00 GMT"},
            {"observed_at_utc": "2026-11-05T00:00:00+00:00"},
            {"independence_group": "independent:mycopy"},
            {"url": "https://wikipedia.org/"},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.reject(lambda p: p["source"].update(change))

    def test_full_card_count_inflation_rejected(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=25))

    def test_raw_drift_and_repeated_observations_not_independent(self):
        self.reject(lambda p: p.update(raw_html_digest_differs_from_four_predecessors=False))
        self.reject(lambda p: p.update(all_24_metadata_and_description_fingerprints_match_four_prior_snapshots=False))

    def test_final_batch_card_scope_exact_four(self):
        self.reject(lambda p: p["selected_tranche_episode_ordinals"].append(25))
        self.reject(lambda p: p["final_four_guide_cards"].pop())
        self.reject(lambda p: p.update(final_four_analytical_synopses_proposed=5))
        self.reject(lambda p: p.update(final_four_source_descriptions_inspected=3))

    def test_episode_25_fabrication_rejected(self):
        self.reject(lambda p: p["held_series_guide_description_partition_summary"].update(fictional_episode_25_invented=True))
        self.reject(lambda p: p["held_series_guide_description_partition_summary"].update(final_publisher_card_ordinal=25))

    def test_not_audiovisual_close_read_or_accepted_work_coverage(self):
        self.reject(lambda p: p["held_series_guide_description_partition_summary"].update(accepted_work_coverage_or_close_read_claims=24))
        self.reject(lambda p: p["held_series_guide_description_partition_summary"].update(total_nonoverlapping_source_relative_description_proposals=25))
        self.reject(lambda p: p["held_series_guide_description_partition_summary"].update(status="CLOSE_READ"))

    def test_card_order_and_title_falsification_rejected(self):
        self.reject(lambda p: p["final_four_guide_cards"].reverse())
        self.reject(lambda p: p["final_four_guide_cards"][0].update(title="E²"))
        self.reject(lambda p: p["final_four_guide_cards"][3].update(episode=25))

    def test_card_source_digest_and_line_tampering_rejected(self):
        self.reject(lambda p: p["final_four_guide_cards"][1].update(description_sha256="0" * 64))
        self.reject(lambda p: p["final_four_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p: p["final_four_guide_cards"][0].update(video_route_path="/fake/"))

    def test_collision_and_collusive_hash_tampering_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][0].update(id="ent-s3-e20-guide-description"))
        def collude(packet):
            packet["final_four_guide_cards"][2]["description_sha256"] = "0" * 64
            packet["source_relative_evidence"][2]["publisher_description_sha256"] = "0" * 64
        self.reject(collude)

    def test_forged_work_identity_or_unsupported_assertion_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="ent-s3-e21"))
        self.reject(lambda p: p["typed_assertions"][0].update(status="EPISODE_CONTENT_VERIFIED"))
        self.reject(lambda p: p["typed_assertions"][1].update(predicate="OBJECTIVE_TRUTH"))
        self.reject(lambda p: p["typed_assertions"][3].update(evidence_id="ent-s3-e23-guide-description"))

    def test_original_paraphrase_custody(self):
        self.reject(lambda p: p["source_relative_evidence"][0].update(original_paraphrase=""))
        self.reject(lambda p: p["source_relative_evidence"][2].update(locator="no line"))

    def test_numeric_ordinal_typed_correctly(self):
        self.reject(lambda p: p["final_four_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["final_four_guide_cards"][0].update(episode=21.0))


if __name__ == "__main__":
    unittest.main()
