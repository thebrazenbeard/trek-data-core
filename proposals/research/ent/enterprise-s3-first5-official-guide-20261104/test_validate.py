"""Hostile packet and parser regressions, without live network requests."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import parse_page
from validate import DISCOVERY, HERE, read_json, validate


class EnterpriseS3FirstFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.discovery = read_json(DISCOVERY)
        cls.discovery_sha = hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()

    def reject(self, mutation):
        packet = copy.deepcopy(self.packet)
        mutation(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.discovery, self.discovery_sha)

    def test_valid_packet(self):
        validate(self.packet, self.discovery, self.discovery_sha)

    def test_upstream_file_digest_drift_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.packet, self.discovery, "0" * 64)

    def test_upstream_canonical_work_rejected(self):
        d = copy.deepcopy(self.discovery)
        d["episode_slots"][0]["canonical_work_id"] = "urn:work:unearned"
        with self.assertRaises(ValueError):
            validate(self.packet, d, self.discovery_sha)

    def test_accepted_source_binding_rejected(self):
        self.reject(lambda p: p.update(accepted_source_binding_effect="ADMITTED"))

    def test_accepted_work_rejected(self):
        self.reject(lambda p: p.update(accepted_work_effect="ADMITTED"))

    def test_coverage_promotion_rejected(self):
        self.reject(lambda p: p.update(coverage_effect="FIVE_CLOSE_READ"))

    def test_denominator_promotion_rejected(self):
        self.reject(lambda p: p.update(denominator_effect="24_NEW_WORKS"))

    def test_reconciliation_promotion_rejected(self):
        self.reject(lambda p: p.update(reconciliation_effect="AUTO_BIND"))

    def test_explorer_release_rejected(self):
        self.reject(lambda p: p.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_claim_of_watched_episode_rejected(self):
        self.reject(lambda p: p.update(episode_content_watched=True))

    def test_claim_of_transcripts_rejected(self):
        self.reject(lambda p: p.update(transcripts_read=True))

    def test_claim_of_downloaded_artwork_rejected(self):
        self.reject(lambda p: p.update(image_bytes_fetched=True))

    def test_source_response_digest_tamper_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_sha256="0" * 64))

    def test_source_response_size_tamper_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_bytes=308000))

    def test_source_replaced_by_derivative_domain_rejected(self):
        self.reject(lambda p: p["source"].update(url="https://memory-alpha.fandom.com/wiki/Enterprise"))

    def test_source_mislabeled_independent_rejected(self):
        self.reject(lambda p: p["source"].update(independence_group="publisher:second-independent-source"))

    def test_raw_publisher_html_falsely_committed_rejected(self):
        self.reject(lambda p: p["source"].update(raw_html_committed=True))

    def test_full_guide_count_drift_rejected(self):
        self.reject(lambda p: p.update(observed_full_guide_card_count=5))

    def test_last_19_cards_cannot_be_called_analyses(self):
        self.reject(lambda p: p.update(first_five_analytical_synopses_proposed=24))

    def test_first_five_slot_doublecount_rejected(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[1, 1, 2, 3, 4]))

    def test_misordered_card_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"].reverse())

    def test_duplicate_source_route_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"][1].update(video_route_path=p["all_24_guide_cards"][0]["video_route_path"]))

    def test_title_discovery_mismatch_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"][0].update(title="Fabrication"))

    def test_publisher_description_hash_drift_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"][1].update(description_sha256="0" * 64))

    def test_collusive_card_and_evidence_hash_tamper_rejected(self):
        def mutate(p):
            p["all_24_guide_cards"][1]["description_sha256"] = "0" * 64
            p["source_relative_evidence"][1]["publisher_description_sha256"] = "0" * 64
        self.reject(mutate)

    def test_invalid_source_line_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][4].update(locator="unresolved"))

    def test_false_episode_truth_promotion_rejected(self):
        self.reject(lambda p: p["typed_assertions"][0].update(status="OBJECTIVE_EPISODE_TRUTH"))

    def test_global_work_resolution_rejected(self):
        self.reject(lambda p: p["local_entities"][2].update(canonical_work_id="ent:s3:e03"))

    def test_duplicate_local_evidence_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][2].update(id="ent-s3-e02-guide-description"))

    def test_missing_paraphrase_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][1].update(original_paraphrase=""))

    def test_claim_source_disjunction_rejected(self):
        self.reject(lambda p: p["typed_assertions"][1].update(evidence_id="ent-s3-e01-guide-description"))

    def test_publisher_ordinal_integer_bool_spoof_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"][0].update(episode=True))

    def test_publisher_ordinal_float_spoof_rejected(self):
        self.reject(lambda p: p["all_24_guide_cards"][0].update(episode=1.0))

    @staticmethod
    def synthetic_card(number, *, shown_episode=None, analytics_title=None):
        title = f"Episode {number}"
        shown = number if shown_episode is None else shown_episode
        name = title if analytics_title is None else analytics_title
        return (
            f'<a href="/shows/video/{number}/" aa-link="episodes||Enterprise - {name}|{number}|Enterprise - {name}|{name}||">'
            f'<h2>{title}</h2><abbr class="seNum" title="Season 3">S3</abbr>'
            f'<abbr class="epNum" title="Episode {shown}">E{shown}</abbr>'
            '<time datetime="2003-01-01T20:00:00-08:00"></time>'
            '<div class="ep__copy" id="js-episode-copy">Synthetic test-only episode description.</div>'
        )

    def test_synthetic_parser_accepts_24_complete_cards(self):
        html = "".join(self.synthetic_card(i) for i in range(1, 25))
        cards, descriptions = parse_page(html)
        self.assertEqual(len(cards), 24)
        self.assertEqual(len(descriptions), 24)

    def test_synthetic_parser_rejects_incomplete_23_cards(self):
        html = "".join(self.synthetic_card(i) for i in range(1, 24))
        with self.assertRaisesRegex(ValueError, "24 ordered"):
            parse_page(html)

    def test_synthetic_parser_rejects_episode_badge_mismatch(self):
        html = self.synthetic_card(1, shown_episode=2) + "".join(self.synthetic_card(i) for i in range(2, 25))
        with self.assertRaisesRegex(ValueError, "ordinal conflict"):
            parse_page(html)

    def test_synthetic_parser_rejects_analytics_title_conflict(self):
        html = self.synthetic_card(1, analytics_title="Contradictory") + "".join(self.synthetic_card(i) for i in range(2, 25))
        with self.assertRaisesRegex(ValueError, "analytics/title conflict"):
            parse_page(html)


if __name__ == "__main__":
    unittest.main()
