"""Adversarial checks on the source-relative TNG proposal boundary."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("tng_derivative_validator", ROOT / "validate.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class TngDerivativeValidationTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((ROOT / "records.json").read_text(encoding="utf-8"))

    def rejects(self, edit):
        candidate = copy.deepcopy(self.bundle)
        edit(candidate)
        with self.assertRaises(ValueError):
            VALIDATOR.validate_bundle(candidate)

    def test_valid_candidate_remains_unadmitted(self):
        self.assertEqual(VALIDATOR.validate_bundle(self.bundle)["accepted_coverage_events"], 0)

    def test_coverage_cannot_promote(self):
        self.rejects(lambda d: d.update(coverage_effect="CLOSE_READ"))

    def test_av_watch_claim_cannot_be_forged(self):
        self.rejects(lambda d: d["source"].update(audiovisual_episode_watched=True))

    def test_source_hash_cannot_be_replaced(self):
        self.rejects(lambda d: d["source"].update(raw_html_sha256="0" * 64))

    def test_unsupported_global_work_identity(self):
        self.rejects(lambda d: d["work"].update(global_work_identity="ACCEPTED"))

    def test_duplicate_entity_identity_rejected(self):
        self.rejects(lambda d: d["local_entities"][1].update(id=d["local_entities"][0]["id"]))

    def test_out_of_bounds_line_locator_rejected(self):
        self.rejects(lambda d: d["evidence"][0].update(end_line=510))

    def test_dangling_entity_reference_rejected(self):
        self.rejects(lambda d: d["evidence"][0].update(local_entity_ids=["global-data"]))

    def test_accepted_assertion_rejected(self):
        self.rejects(lambda d: d["assertions"][0].update(status="ACCEPTED"))

    def test_forged_stable_projection_rejected(self):
        self.rejects(lambda d: d["assertions"][0].update(proposed_projection_status="STABLE"))

    def test_unreviewed_transcript_text_field_rejected(self):
        self.rejects(lambda d: d.update(full_transcript="Do not publish copyright source"))

    def test_removed_counterevidence_rejected(self):
        self.rejects(lambda d: d["assertions"][0].update(counter_evidence_ids=[]))

    def test_purposive_sampling_cannot_claim_representativeness(self):
        self.rejects(lambda d: d["selection"].update(
            corpus_level_prevalence_or_generalization_effect="ALLOWED"))

    def test_purposive_selection_cannot_be_silently_relabelled_sequential(self):
        self.rejects(lambda d: d["selection"].update(method="SEQUENTIAL"))


if __name__ == "__main__":
    unittest.main()
