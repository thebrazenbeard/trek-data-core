"""Adversarial first-five S1 guide-card and source-relative inference tests."""

from __future__ import annotations

import copy
import unittest

from source_probe import URL
from validate import HERE, RECORDS_SHA, read_json, validate, validate_serialized


class S1FirstFiveResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_json(HERE / "records.json")

    def reject(self, mutate) -> None:
        packet = copy.deepcopy(self.data)
        mutate(packet)
        with self.assertRaises(ValueError):
            validate(packet)

    def test_packet_passes(self):
        validate(self.data)
        validate_serialized((HERE / "records.json").read_bytes())

    def test_packet_bytes_sha_fail_closed(self):
        import hashlib
        raw = (HERE / "records.json").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), RECORDS_SHA)
        with self.assertRaises(ValueError):
            validate_serialized(raw + b" ")

    def test_original_source_relative_paraphrase_semantics_pinned(self):
        for i in range(5):
            with self.subTest(card=i + 1):
                self.reject(lambda p, idx=i: p["source_relative_evidence"][idx].update(
                    original_paraphrase="The publisher proves permanent Vulcan acceptance of every human decision and this directly confirms final canon outcomes without another source."))
        self.reject(lambda p: p["source_relative_evidence"][0].update(
            original_paraphrase="The publisher unequivocally proves lasting Vulcan acceptance and complete crew success throughout the opening voyage, beyond any reasonable dispute."))

    def test_exact_first_party_source_url(self):
        self.assertEqual(URL, "https://www.paramountplus.com/shows/enterprise/episodes/1/")
        self.reject(lambda p: p["source"].update(url="https://memory-alpha.fandom.com/wiki/"))

    def test_full_source_receipt_and_single_publisher_family(self):
        for changed in ({"raw_response_bytes": 100}, {"raw_response_sha256": "0" * 64},
                        {"all_25_cards_fingerprint_sha256": "0" * 64},
                        {"response_http_status": 404}, {"independence_group": "independent:copy"}):
            with self.subTest(changed=changed):
                self.reject(lambda p: p["source"].update(changed))

    def test_source_timestamp_is_pinned_not_inferred_from_airdate(self):
        self.reject(lambda p: p["source"].update(observed_at_utc="yesterday"))
        self.reject(lambda p: p["first_five_guide_cards"][1].update(publisher_datetime="2001-10-03T21:00:00-07:00"))

    def test_25_publisher_cards_not_25_canonical_episodes(self):
        self.reject(lambda p: p.update(observed_publisher_guide_card_count=26))
        self.reject(lambda p: p["pilot_structure"].update(two_part_pilot_global_episode_count=2))
        self.reject(lambda p: p["pilot_structure"].update(first_guide_card_title="Broken Bow Part 1"))

    def test_source_badge_gap_is_not_an_analytics_gap(self):
        self.reject(lambda p: p.update(selected_guide_card_ordinals=[1, 3, 4, 5, 6]))
        self.reject(lambda p: p.update(selected_publisher_episode_badges=[1, 2, 3, 4, 5]))
        self.reject(lambda p: p["first_five_guide_cards"][1].update(episode_badge=2))
        self.reject(lambda p: p["first_five_guide_cards"][1].update(analytics_ordinal=3))

    def test_five_description_reads_not_audiovisual_close_reads(self):
        for name in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
            with self.subTest(name=name):
                self.reject(lambda p: p.update({name: True}))
        self.reject(lambda p: p.update(five_source_descriptions_inspected=25))
        self.reject(lambda p: p.update(five_publisher_description_chars=1011))

    def test_no_accepted_work_denominator_reconciliation_or_publishing(self):
        for name in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
                     "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect"):
            with self.subTest(name=name):
                self.reject(lambda p: p.update({name: "ACCEPTED"}))

    def test_unreviewed_extra_effect_keys_fail_closed(self):
        self.reject(lambda p: p.update(public_release=True))
        self.reject(lambda p: p["source"].update(rights_cleared=True))
        self.reject(lambda p: p["first_five_guide_cards"][0].update(film_close_read=True))
        self.reject(lambda p: p["local_entities"][0].update(accepted_work="ent:s1:e01"))
        self.reject(lambda p: p["source_relative_evidence"][0].update(canonical_fact=True))
        self.reject(lambda p: p["typed_assertions"][0].update(verification_status="AUDITED"))

    def test_exact_local_entity_links_and_no_global_work(self):
        self.reject(lambda p: p["local_entities"][0].update(canonical_work_id="ent:s1:e01"))
        self.reject(lambda p: p["source_relative_evidence"][1].update(local_entity_id="ent-s1-card01"))
        self.reject(lambda p: p["typed_assertions"][2].update(evidence_id="ent-s1-card02-guide-description"))
        self.reject(lambda p: p["local_entities"][3].update(id="ent-s1-card03"))

    def test_original_paraphrase_and_publisher_frame(self):
        self.reject(lambda p: p["source_relative_evidence"][1].update(original_paraphrase=""))
        self.reject(lambda p: p["source_relative_evidence"][3].update(kind="EPISODE_VIDEO_DEPICTION"))
        self.reject(lambda p: p["typed_assertions"][2].update(predicate="CANON_PROVES"))
        self.reject(lambda p: p["typed_assertions"][4].update(frame_claim_status="OBJECTIVE_WORLD_FACT"))

    def test_hallucinatory_frame_not_observed_objective_danger(self):
        self.reject(lambda p: p["source_relative_evidence"][2].update(claim_mode="ALIEN_THREATS_CONFIRMED"))

    def test_biology_and_colony_evolution_not_independently_verified(self):
        self.reject(lambda p: p["source_relative_evidence"][3].update(claim_mode="BIOLOGICAL_MECHANISM_VERIFIED"))
        self.reject(lambda p: p["source_relative_evidence"][4].update(claim_mode="CONFIRMED_SPECIES_EVOLUTION"))

    def test_source_line_and_hash_receipts_not_mutable(self):
        self.reject(lambda p: p["first_five_guide_cards"][0].update(description_sha256="0" * 64))
        self.reject(lambda p: p["first_five_guide_cards"][4].update(html_description_line=999))
        self.reject(lambda p: p["source_relative_evidence"][4].update(publisher_description_sha256="0" * 64))

    def test_partition_arithmetic_never_promotes_accepted_coverage(self):
        self.reject(lambda p: p["held_description_partition"].update(accepted_episode_close_reads=5))
        self.reject(lambda p: p["held_description_partition"].update(remaining_unprocessed_card_descriptions=0))
        self.reject(lambda p: p["held_description_partition"].update(status="AUDITED"))


if __name__ == "__main__":
    unittest.main()
