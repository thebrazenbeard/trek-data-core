"""Hostile packet/ingestion regressions; all tests use synthetic or held data."""

from __future__ import annotations

import copy
import hashlib
import unittest

from validate import HERE, DISCOVERY, read_json, validate
from source_probe import parse_page


class PicS3PublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_json(HERE / "records.json")
        cls.discovery = read_json(DISCOVERY)
        cls.discovery_sha = hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()

    def reject(self, mutate):
        packet = copy.deepcopy(self.data)
        mutate(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.discovery, self.discovery_sha)

    def test_valid_held_source_packet(self):
        validate(self.data, self.discovery, self.discovery_sha)

    def test_false_accepted_work_rejected(self):
        self.reject(lambda p: p.update(accepted_work_effect="TEN_WORKS"))

    def test_false_coverage_rejected(self):
        self.reject(lambda p: p.update(coverage_effect="FIVE_CLOSE_READ"))

    def test_false_episode_watch_rejected(self):
        self.reject(lambda p: p.update(episode_content_watched=True))

    def test_false_synopsis_publication_rejected(self):
        self.reject(lambda p: p.update(explorer_synopsis_release_effect="PUBLISHED"))

    def test_wrong_source_sha_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_sha256="0" * 64))

    def test_truncated_source_page_rejected(self):
        self.reject(lambda p: p["source"].update(raw_response_bytes=200))

    def test_copied_publisher_content_rejected_as_no_raw(self):
        self.reject(lambda p: p["source"].update(raw_html_committed=True))

    def test_duplicate_video_route_rejected(self):
        self.reject(lambda p: p["guide_cards"][1].update(video_route_path=p["guide_cards"][0]["video_route_path"]))

    def test_wrong_source_title_rejected(self):
        self.reject(lambda p: p["guide_cards"][4].update(title="The Fake Title"))

    def test_wrong_display_order_rejected(self):
        self.reject(lambda p: p["guide_cards"][1].update(display_order=9))

    def test_badge_analytics_disagreement_rejected(self):
        self.reject(lambda p: p["guide_cards"][2].update(analytics_ordinal=7))

    def test_ambiguous_publisher_datetime_rejected(self):
        self.reject(lambda p: p["guide_cards"][4].update(publisher_datetime="2023-03-16"))

    def test_description_fingerprint_tamper_rejected(self):
        self.reject(lambda p: p["guide_cards"][0].update(description_sha256="0" * 64))

    def test_fingerprint_collusion_rejected(self):
        def tamper(p):
            p["guide_cards"][1]["description_sha256"] = "0" * 64
            p["source_relative_evidence"][1]["publisher_description_sha256"] = "0" * 64
        self.reject(tamper)

    def test_missing_source_description_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"].pop(2))

    def test_wrong_description_locator_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][4].update(locator="Unknown line"))

    def test_empty_original_paraphrase_rejected(self):
        self.reject(lambda p: p["source_relative_evidence"][3].update(original_paraphrase=""))

    def test_assertion_promoted_to_objective_truth_rejected(self):
        self.reject(lambda p: p["typed_assertions"][0].update(status="VERIFIED_EPISODE_TRUTH"))

    def test_global_identity_binding_rejected(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="PIC-S3-E01"))

    def test_source_lineage_promotion_rejected(self):
        self.reject(lambda p: p["source"].update(independence_group="independent:two_sources"))

    def test_not_all_ten_synopses_processed_rejected(self):
        self.reject(lambda p: p.update(first_five_analytical_synopses_proposed=10))

    def test_synthetic_extractor_rejects_visible_badge_mismatch(self):
        s = ('<a href="/shows/video/a/" aa-link="episodes||Star Trek: Picard - A|1|Star Trek: Picard - A|A||">'
             '<h2>A</h2><abbr class="seNum" title="Season 3">S3</abbr>'
             '<abbr class=\'epNum\' title="Episode 2">E1</abbr><time datetime="2023-01-01T00:00:00Z"></time>'
             '<div class="ep__copy overflow-ellipsis" id="js-episode-copy">A test-only synopsis.</div>')
        with self.assertRaisesRegex(ValueError, "badge mismatch"):
            parse_page(s)

    def test_synthetic_extractor_rejects_forged_analytics_title(self):
        s = ('<a href="/shows/video/a/" aa-link="episodes||Star Trek: Picard - A|1|Star Trek: Picard - B|B||">'
             '<h2>A</h2><abbr class="seNum" title="Season 3">S3</abbr>'
             '<abbr class=\'epNum\' title="Episode 1">E1</abbr><time datetime="2023-01-01T00:00:00Z"></time>'
             '<div class="ep__copy overflow-ellipsis" id="js-episode-copy">A test-only synopsis.</div>')
        with self.assertRaisesRegex(ValueError, "analytics/title mismatch"):
            parse_page(s)

    def test_synthetic_extractor_accepts_complete_source_card(self):
        s = ('<a href="/shows/video/a/" aa-link="episodes||Star Trek: Picard - A|1|Star Trek: Picard - A|A||">'
             '<h2>A</h2><abbr class="seNum" title="Season 3">S3</abbr>'
             '<abbr class=\'epNum\' title="Episode 1">E1</abbr><time datetime="2023-01-01T00:00:00Z"></time>'
             '<div class="ep__copy overflow-ellipsis" id="js-episode-copy">A test-only synopsis.</div>')
        rows, descriptions = parse_page(s)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["description_chars"], len(descriptions[0]))


if __name__ == "__main__":
    unittest.main()
