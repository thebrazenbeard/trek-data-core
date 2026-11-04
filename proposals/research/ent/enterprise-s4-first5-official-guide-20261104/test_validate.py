"""Independent hostile source-custody and E22-title-variant regressions, no network."""

from __future__ import annotations

import copy
import hashlib
import unittest

from source_probe import parse_page
from validate import DISCOVERY, HERE, read_json, validate


class EnterpriseS4FirstFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(HERE / "records.json")
        cls.discovery = read_json(DISCOVERY)
        cls.discovery_sha = hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()

    def reject(self, modifier):
        packet = copy.deepcopy(self.packet)
        modifier(packet)
        with self.assertRaises(ValueError):
            validate(packet, self.discovery, self.discovery_sha)

    def test_valid_packet(self):
        validate(self.packet, self.discovery, self.discovery_sha)

    def test_wrong_discovery_file_hash(self):
        with self.assertRaises(ValueError):
            validate(self.packet, self.discovery, "0" * 64)

    def test_discovery_work_binding_cannot_be_silent(self):
        d = copy.deepcopy(self.discovery)
        d["episode_slots"][0]["canonical_work_id"] = "urn:unearned:work"
        with self.assertRaises(ValueError):
            validate(self.packet, d, self.discovery_sha)

    def test_derivative_source_cannot_claim_independence(self):
        self.reject(lambda p: p["upstream_discovery"].update(independent_corroboration=True))
        self.reject(lambda p: p["source"].update(independence_group="other:independent"))

    def test_all_six_protected_effects_are_none(self):
        keys = ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
                "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect")
        for key in keys:
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key: "ADMITTED"}))

    def test_no_episode_video_transcript_image_claims(self):
        for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
            with self.subTest(key=key):
                self.reject(lambda p: p.update({key: True}))

    def test_source_receipt_tampering(self):
        for data in (
            {"url": "https://memory-alpha.fandom.com/wiki/Enterprise"},
            {"raw_response_sha256": "0" * 64},
            {"raw_response_bytes": 0},
            {"response_http_status": 404},
            {"raw_html_committed": True},
            {"observed_at_utc": "2026-11-04T23:00:00Z"},
            {"response_date_header": "Thu, 05 Nov 2026 00:00:00 GMT"},
        ):
            with self.subTest(change=data):
                self.reject(lambda p: p["source"].update(data))

    def test_guide_context_does_not_equal_22_analyses(self):
        self.reject(lambda p: p.update(first_five_analytical_synopses_proposed=22))
        self.reject(lambda p: p.update(first_five_source_descriptions_inspected=22))
        self.reject(lambda p: p.update(observed_full_guide_card_count=5))
        self.reject(lambda p: p.update(first_five_description_total_chars=1000))

    def test_exact_five_scope(self):
        self.reject(lambda p: p.update(selected_tranche_episode_ordinals=[1, 1, 2, 3, 4]))
        self.reject(lambda p: p["local_entities"].pop())

    def test_title_and_ordinals_source_pinned(self):
        self.reject(lambda p: p["all_22_guide_cards"].reverse())
        self.reject(lambda p: p["all_22_guide_cards"][2].update(title="Unverified Replacement"))
        self.reject(lambda p: p["all_22_guide_cards"][0].update(episode=True))
        self.reject(lambda p: p["all_22_guide_cards"][0].update(episode=1.0))

    def test_description_hash_route_and_locator_pinned(self):
        self.reject(lambda p: p["all_22_guide_cards"][2].update(description_sha256="0"*64))
        self.reject(lambda p: p["all_22_guide_cards"][2].update(html_description_line=1))
        self.reject(lambda p: p["all_22_guide_cards"][1].update(video_route_path=p["all_22_guide_cards"][0]["video_route_path"]))
        self.reject(lambda p: p["source_relative_evidence"][3].update(locator="unresolved"))

    def test_collusive_source_card_evidence_hash_tamper(self):
        def mutate(packet):
            packet["all_22_guide_cards"][2]["description_sha256"] = "0" * 64
            packet["source_relative_evidence"][2]["publisher_description_sha256"] = "0" * 64
        self.reject(mutate)

    def test_e22_display_analytics_mismatch_must_remain_visible(self):
        self.reject(lambda p: p["all_22_guide_cards"][21].update(analytics_series_title="These Are the Voyages"))
        self.reject(lambda p: p["all_22_guide_cards"][21].update(title_variant_status="EXACT_MATCH"))
        self.reject(lambda p: p["source_internal_title_variants"].clear())
        self.reject(lambda p: p["source_internal_title_variants"][0].update(global_reconciliation_effect="ACCEPTED"))
        self.reject(lambda p: p["source_internal_title_variants"][0].update(status="RESOLVED"))

    def test_unbound_work_and_source_relative_assertion(self):
        self.reject(lambda p: p["local_entities"][2].update(canonical_work_id="ent:s4:e03"))
        self.reject(lambda p: p["source_relative_evidence"][1].update(id="ent-s4-e01-guide-description"))
        self.reject(lambda p: p["typed_assertions"][0].update(predicate="EPISODE_TRUTH"))
        self.reject(lambda p: p["typed_assertions"][1].update(status="CLOSE_READ"))
        self.reject(lambda p: p["typed_assertions"][1].update(evidence_id="ent-s4-e01-guide-description"))
        self.reject(lambda p: p["source_relative_evidence"][4].update(original_paraphrase=""))

    @staticmethod
    def card(i: int, *, episode=None, displayed_title=None, series_title=None):
        title = displayed_title or f"Synthetic Episode {i}"
        parent_title = series_title or title
        number = i if episode is None else episode
        return (
            f'<a href="/shows/video/test{i}/" aa-link="episodes||Enterprise - {parent_title}|{i}|Enterprise - {parent_title}|{title}||">'
            f'<h2>{title}</h2><abbr class="seNum" title="Season 4">S4</abbr>'
            f'<abbr class="epNum" title="Episode {number}">E{number}</abbr>'
            '<time datetime="2004-10-01T20:00:00-07:00"></time>'
            '<div class="ep__copy">Synthetic parser test description only.</div>'
        )

    def test_synthetic_22_card_guide(self):
        cards, descriptions = parse_page("".join(self.card(i) for i in range(1, 23)))
        self.assertEqual(len(cards), len(descriptions))
        self.assertEqual(len(cards), 22)

    def test_synthetic_21_card_guide_rejected(self):
        with self.assertRaisesRegex(ValueError, "22 ordered"):
            parse_page("".join(self.card(i) for i in range(1, 22)))

    def test_synthetic_bad_episode_badge_rejected(self):
        broken = self.card(1, episode=2) + "".join(self.card(i) for i in range(2, 23))
        with self.assertRaises(ValueError):
            parse_page(broken)

    def test_synthetic_title_difference_beyond_case_rejected(self):
        broken = self.card(1, displayed_title="A", series_title="B") + "".join(self.card(i) for i in range(2, 23))
        with self.assertRaisesRegex(ValueError, "identity conflict"):
            parse_page(broken)

    def test_synthetic_source_case_variant_preserved(self):
        page = "".join(self.card(i, displayed_title="These Are the Voyages", series_title="These Are The Voyages") if i == 22 else self.card(i) for i in range(1, 23))
        cards, _ = parse_page(page)
        self.assertEqual(cards[21]["title_variant_status"], "CAPITALIZATION_VARIANT_UNRESOLVED")
        self.assertEqual(cards[21]["analytics_series_title"], "These Are The Voyages")


if __name__ == "__main__":
    unittest.main()
