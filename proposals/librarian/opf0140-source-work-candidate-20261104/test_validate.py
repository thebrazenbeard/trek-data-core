"""Adversarial contract checks for the held, nonfixture Librarian candidate."""

import copy
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("held_candidate_validator", HERE / "validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HeldCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = MODULE.load(HERE / "candidate.json")
        cls.upstream = MODULE.load(MODULE.ROOT / "proposals" / "librarian" /
                                   "private-opf-metadata-20261103" / "observations.json")

    def test_valid_held_candidate(self):
        self.assertTrue(MODULE.check(self.packet, self.upstream))

    def mutate_and_reject(self, mutation):
        candidate = copy.deepcopy(self.packet)
        mutation(candidate)
        with self.assertRaises((ValueError, TypeError, KeyError)):
            MODULE.check(candidate, self.upstream)

    def test_rejects_false_positive_admission(self):
        self.mutate_and_reject(lambda c: c.update(coverage_effect="SOURCE_BOUND"))

    def test_rejects_binding_promotion(self):
        self.mutate_and_reject(lambda c: c["proposal"]["source_work_binding"].update(
            mapping_role="EVIDENCE_BEARING"))

    def test_rejects_fake_verified_rights(self):
        self.mutate_and_reject(lambda c: c["custody_observation"].update(
            rights_verification="VERIFIED"))

    def test_rejects_wrong_member_hash(self):
        self.mutate_and_reject(lambda c: c["custody_observation"].update(
            original_extracted_member_sha256="0" * 64))

    def test_rejects_relabelled_nonfixture_as_fixture(self):
        self.mutate_and_reject(lambda c: c["proposal"]["source"].update(fixture_only=True))

    def test_rejects_private_path(self):
        self.mutate_and_reject(lambda c: c.update(private_path="/home/vera/private"))

    def test_rejects_publisher_isbn_drift(self):
        self.mutate_and_reject(lambda c: c["publisher_observation"].update(
            isbn13="9780743412088"))

    def test_rejects_upstream_hash_drift(self):
        upstream = copy.deepcopy(self.upstream)
        row = next(r for r in upstream["rows"] if r.get("source_local_id") == "opf-local:0140")
        row["opf_entry_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.check(self.packet, upstream)


if __name__ == "__main__":
    unittest.main()
