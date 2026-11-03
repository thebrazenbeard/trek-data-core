"""Mutation-based checks of the SNW S3 proposal's fail-closed boundaries."""

import copy
import json
from pathlib import Path
import unittest

from validate import validate_records


DATA = json.loads((Path(__file__).resolve().parent / "records.json").read_text(encoding="utf-8"))


class SourcePacketValidation(unittest.TestCase):
    def test_full_packet(self):
        self.assertEqual(validate_records(copy.deepcopy(DATA)), 5)

    def test_accepted_work_effect_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["accepted_work_effect"] = "CREATED"
        with self.assertRaisesRegex(ValueError, "accepted_work_effect"):
            validate_records(changed)

    def test_explorer_publication_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["artwork_candidates"][0]["explorer_effect"] = "HOTLINKED"
        with self.assertRaisesRegex(ValueError, "unreviewed publication"):
            validate_records(changed)

    def test_unsupported_stream_read_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["audiovisual_content_inspected"] = True
        with self.assertRaisesRegex(ValueError, "unsubstantiated"):
            validate_records(changed)

    def test_false_independent_source_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["source"]["independence_group"] = "independent:episode-1"
        with self.assertRaisesRegex(ValueError, "lineage"):
            validate_records(changed)

    def test_global_entity_reconciliation_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["local_entities"][0]["global_entity_id"] = "person-pike"
        with self.assertRaisesRegex(ValueError, "global entity"):
            validate_records(changed)

    def test_cross_work_assertion_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["assertions"][0]["evidence_id"] = changed["evidence"][1]["evidence_id"]
        with self.assertRaisesRegex(ValueError, "cross-work"):
            validate_records(changed)

    def test_digest_corruption_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["source"]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_records(changed)

    def test_wrong_episode_number_rejected(self):
        changed = copy.deepcopy(DATA)
        changed["works"][0]["episode_number"] = 10
        with self.assertRaisesRegex(ValueError, "publisher episode"):
            validate_records(changed)

    def test_audited_e05_quest_fidelity(self):
        changed = copy.deepcopy(DATA)
        changed["evidence"][4]["paraphrase"] = changed["evidence"][4]["paraphrase"].replace("quest", "investigation")
        with self.assertRaisesRegex(ValueError, "quest semantics"):
            validate_records(changed)


if __name__ == "__main__":
    unittest.main()
