"""Malicious-input regressions for the source-relative VOY Season 1 packet."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate import HERE, validate, validate_serialized


class VoyagerSourceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = (HERE / "records.json").read_bytes()
        cls.original = json.loads(cls.raw)

    def mutated(self, operation) -> None:
        packet = copy.deepcopy(self.original)
        operation(packet)
        with self.assertRaises((ValueError, KeyError, TypeError, AttributeError)):
            validate(packet)

    def test_baseline_frozen_records(self) -> None:
        validate_serialized(self.raw)

    def test_reformatted_packet_requires_review(self) -> None:
        with self.assertRaisesRegex(ValueError, "packet bytes"):
            validate_serialized(json.dumps(self.original, indent=4).encode())

    def test_false_accepted_episode_count(self) -> None:
        self.mutated(lambda p: p.__setitem__("coverage_effect", "FIVE_EPISODE_CLOSE_READS"))

    def test_false_episode_watched(self) -> None:
        self.mutated(lambda p: p.__setitem__("episode_content_watched", True))

    def test_spoofed_false_integer(self) -> None:
        self.mutated(lambda p: p.__setitem__("source_relative_descriptions_read", True))

    def test_fake_third_party_source(self) -> None:
        self.mutated(lambda p: p["source"].__setitem__("url", "https://not-paramount.example.invalid/"))

    def test_fake_source_license_field(self) -> None:
        self.mutated(lambda p: p["source"].__setitem__("all_media_license_granted", True))

    def test_forged_raw_page_receipt(self) -> None:
        self.mutated(lambda p: p["source"].__setitem__("response_sha256", "0" * 64))

    def test_false_german_locale_reclassification(self) -> None:
        self.mutated(lambda p: p["source"].__setitem__("locale", "de-DE"))

    def test_pilot_split_fabrication(self) -> None:
        self.mutated(lambda p: p["pilot_representation"].__setitem__("second_card_publisher_episode_badge", 2))

    def test_cross_locale_automatic_identity(self) -> None:
        self.mutated(lambda p: p["pilot_representation"].__setitem__("canonical_two_part_episode_identity", "RECONCILED"))

    def test_caretaker_truncated_description_invention(self) -> None:
        self.mutated(lambda p: p["source_relative_evidence"][0].__setitem__("original_paraphrase", "Janeway definitively establishes the entire Delta Quadrant's permanent Federation border and saves everyone in the official episode."))

    def test_causal_uncertainty_promotion(self) -> None:
        self.mutated(lambda p: p["source_relative_evidence"][2].__setitem__("original_paraphrase", "The episode objectively proves the visitors caused every catastrophe, and no alternative explanation is possible."))

    def test_publisher_description_hash_forgery(self) -> None:
        self.mutated(lambda p: p["cards"][1].__setitem__("description_sha256", "f" * 64))

    def test_card_video_route_misbinding(self) -> None:
        self.mutated(lambda p: p["cards"][1].__setitem__("video_route_path", p["cards"][2]["video_route_path"]))

    def test_ordinal_episode_badge_conflation(self) -> None:
        self.mutated(lambda p: p["cards"][1].__setitem__("episode_badge", 2))

    def test_crosswire_evidence(self) -> None:
        self.mutated(lambda p: p["source_relative_evidence"][1].__setitem__("local_entity_id", "voy-s1-card01"))

    def test_global_work_identity_injection(self) -> None:
        self.mutated(lambda p: p["local_entities"][0].__setitem__("canonical_work_id", "voy-caretaker-global"))

    def test_unreviewed_image_rights(self) -> None:
        self.mutated(lambda p: p.__setitem__("third_party_artwork_published", True))

    def test_unearned_assertion_truth(self) -> None:
        self.mutated(lambda p: p["typed_assertions"][3].__setitem__("status", "CANONICAL_WORLD_STATE_VERIFIED"))

    def test_unreviewed_raw_transcript(self) -> None:
        self.mutated(lambda p: p["source_relative_evidence"][0].__setitem__("full_transcript", "copyrighted body"))

    def test_bad_packet_duplicate_json_key_rejected(self) -> None:
        import validate as gate
        raw = self.raw.replace(b'"role": "VOY",', b'"role": "VOY", "role": "TNG",', 1)
        with self.assertRaisesRegex(ValueError, "packet bytes"):
            gate.validate_serialized(raw)


if __name__ == "__main__":
    unittest.main()
