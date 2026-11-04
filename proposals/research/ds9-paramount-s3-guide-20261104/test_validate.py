"""Mutation tests that challenge provenance, cardinality, linkage, and coverage claims."""
import copy
import json
from pathlib import Path
import unittest

from validate import validate

ORIGINAL = json.loads(Path(__file__).with_name("records.json").read_text(encoding="utf-8"))


class TestS3PublisherGuide(unittest.TestCase):
    def assert_rejected(self, mutation):
        document = copy.deepcopy(ORIGINAL)
        mutation(document)
        self.assertTrue(validate(document), "mutated record should be rejected")

    def test_valid(self):
        self.assertEqual(validate(ORIGINAL), [])
        self.assertEqual(len(ORIGINAL["source_local_episode_slots"]), 24)
        self.assertEqual(ORIGINAL["missing_publisher_ordinals_in_extraction"], [4, 26])

    def test_reject_work_coverage_and_publication_admission(self):
        for key, value in (
            ("accepted_work_effect", "ADDED"),
            ("accepted_source_binding_effect", "BOUND"),
            ("episode_research_coverage_effect", "CLOSE_READ"),
            ("synopsis_publication_effect", "PUBLISHED"),
            ("admitted_briefings", 24),
            ("proposal_only", False),
            ("episode_census_claim", "SEASON_COMPLETE"),
        ):
            with self.subTest(key=key):
                self.assert_rejected(lambda b: b.update({key: value}))

    def test_reject_unobserved_source_proofs(self):
        for key, value in (
            ("raw_source_body_sha256", "f" * 64),
            ("raw_html_bytes_pinned", True),
            ("http_status_verified", True),
            ("full_episode_audiovisual_or_script_read", True),
            ("independence_group", "source:independent"),
        ):
            with self.subTest(key=key):
                self.assert_rejected(lambda b: b["source"].update({key: value}))

    def test_reject_card_ordinal_title_fingerprint_or_locator_mutation(self):
        for field, value in (
            ("source_episode_ordinal", 4),
            ("publisher_title", "The Visitor"),
            ("source_description_sha256", "a" * 64),
            ("source_card_locator", "Season 3"),
            ("work_ref", "ds9:season3:work01"),
            ("work_binding_status", "ACCEPTED"),
        ):
            with self.subTest(field=field):
                self.assert_rejected(lambda b: b["source_local_episode_slots"][0].update({field: value}))

    def test_reject_broken_chain_and_global_identity(self):
        for collection, field, value in (
            ("local_entities", "slot_id", "ds9-s3-slot-99"),
            ("local_entities", "identity_scope", "GLOBAL_RESOLVED"),
            ("evidence", "source_id", "fake"),
            ("evidence", "description_sha256", "0" * 64),
            ("assertions", "supporting_evidence_id", "fake"),
            ("assertions", "fictional_truth_scope", "OBJECTIVE_CANON"),
        ):
            with self.subTest(collection=collection, field=field):
                self.assert_rejected(lambda b: b[collection][0].update({field: value}))

    def test_reject_missing_duplicated_or_injected_records(self):
        for mutation in (
            lambda b: b["source_local_episode_slots"].pop(),
            lambda b: b["local_entities"].append(copy.deepcopy(b["local_entities"][-1])),
            lambda b: b["evidence"][0].update({"full_transcript": "unjustified"}),
            lambda b: b.update({"accepted_works": ["w1"]}),
            lambda b: b.update({"missing_publisher_ordinals_in_extraction": []}),
        ):
            with self.subTest(mutation=repr(mutation)):
                self.assert_rejected(mutation)

    def test_reject_unattributed_canon_claim(self):
        self.assert_rejected(
            lambda b: b["assertions"][2].update({"original_held_paraphrase": "The episode proves Quark murdered the Klingon."})
        )


if __name__ == "__main__":
    unittest.main()
