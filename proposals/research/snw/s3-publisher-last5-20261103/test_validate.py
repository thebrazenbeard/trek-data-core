"""Adversarial invariants for an unadmitted Paramount+ publisher-card packet."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("snw_s3_last5_validator_20261103", HERE / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate_records = MODULE.validate_records
DATA = json.loads((HERE / "records.json").read_text(encoding="utf-8"))


class SourcePacketValidation(unittest.TestCase):
    def test_complete(self):
        self.assertEqual(validate_records(copy.deepcopy(DATA)), 5)

    def test_canonical_admission_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["works"][0]["canonical_work_id"] = "snw-301"
        with self.assertRaisesRegex(ValueError, "Work reconciliation"):
            validate_records(edited)

    def test_false_explorer_effect_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["explorer_effect"] = "PUBLISHED"
        with self.assertRaisesRegex(ValueError, "explorer_effect"):
            validate_records(edited)

    def test_false_av_inspection_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["audiovisual_content_inspected"] = True
        with self.assertRaisesRegex(ValueError, "uninspected AV"):
            validate_records(edited)

    def test_source_lineage_forgery_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["source"]["independence_group"] = "independent:publisher-e06"
        with self.assertRaisesRegex(ValueError, "independence"):
            validate_records(edited)

    def test_artwork_hotlinking_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["artwork_candidates"][0]["explorer_effect"] = "HOTLINKED"
        with self.assertRaisesRegex(ValueError, "artwork publication"):
            validate_records(edited)

    def test_cross_work_evidence_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["assertions"][0]["evidence_id"] = edited["evidence"][1]["evidence_id"]
        with self.assertRaisesRegex(ValueError, "cross-work assertion"):
            validate_records(edited)

    def test_cross_work_entity_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["assertions"][0]["local_entity_ids"] = [edited["local_entities"][2]["local_entity_id"]]
        with self.assertRaisesRegex(ValueError, "cross-work mention"):
            validate_records(edited)

    def test_digest_mutation_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["source"]["response_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_records(edited)

    def test_ordinal_mutation_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["works"][0]["episode_number"] = 5
        with self.assertRaisesRegex(ValueError, "episode mismatch"):
            validate_records(edited)

    def test_anomalous_art_host_rejected(self):
        edited = copy.deepcopy(DATA)
        edited["artwork_candidates"][0]["source_url"] = "https://example.org/fiction.jpg"
        with self.assertRaisesRegex(ValueError, "artwork URL"):
            validate_records(edited)

    def test_no_global_entity_identity(self):
        edited = copy.deepcopy(DATA)
        edited["local_entities"][0]["global_entity_id"] = "kirk-person"
        with self.assertRaisesRegex(ValueError, "global identity"):
            validate_records(edited)


if __name__ == "__main__":
    unittest.main()
