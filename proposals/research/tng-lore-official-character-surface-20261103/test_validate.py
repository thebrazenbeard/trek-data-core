"""Mutation checks for claims and rights that this research has not earned."""

import copy
import json
import unittest
from pathlib import Path

from validate import no_duplicates, validate


class PacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good = json.loads(Path(__file__).with_name("records.json").read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)

    def test_current_packet(self):
        validate(self.good)

    def reject(self, alter):
        payload = copy.deepcopy(self.good)
        alter(payload)
        with self.assertRaises(ValueError):
            validate(payload)

    def test_public_lore_image_cannot_be_promoted(self):
        self.reject(lambda p: p["artwork_candidates"][0].update(rights_status="PUBLIC_USE_AUTHORIZED"))

    def test_cannot_publish_image_bytes(self):
        self.reject(lambda p: p["artwork_candidates"][1].update(bytes_downloaded=True))

    def test_unverified_paramount_read_cannot_be_claimed(self):
        self.reject(lambda p: p["inaccessible_candidate_sources"][0].update(verified=True))

    def test_publisher_article_is_not_full_episode(self):
        self.reject(lambda p: p["sources"][0].update(full_episode_source=True))

    def test_no_reconciled_global_entity(self):
        self.reject(lambda p: p["local_entities"][0].update(global_identity="accepted:lore"))

    def test_lore_is_not_actual_uploaded_consciousness(self):
        self.reject(lambda p: p["persona_note"].update(actual_consciousness_transfer_claim=True))

    def test_no_public_explorer_release(self):
        self.reject(lambda p: p.update(public_explorer_effect="PUBLISHED"))

    def test_injected_real_model_claim_in_observation_fails(self):
        self.reject(lambda p: p["evidence"][0].update(observation="Publisher says real model possessed by consciousness"))

    def test_injected_real_consciousness_predicate_fails(self):
        self.reject(lambda p: p["assertions"][0].update(predicate="REAL_CONSCIOUSNESS_TRANSFER"))

    def test_artwork_public_domain_mislabel_fails(self):
        self.reject(lambda p: p["artwork_candidates"][0].update(description="Public domain official portrait"))

    def test_reordered_artwork_source_link_fails(self):
        self.reject(lambda p: p["artwork_candidates"][0].update(source_id="S2"))

    def test_evidence_bound_to_read_pages(self):
        self.reject(lambda p: p["evidence"][0].update(source_id="paramount-500"))

    def test_no_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"role":"TNG","role":"GLOBAL"}', object_pairs_hook=no_duplicates)


if __name__ == "__main__":
    unittest.main()
