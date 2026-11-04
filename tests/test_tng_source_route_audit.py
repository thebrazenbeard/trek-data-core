"""Negative qualification tests for the held TNG proposal metadata route."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_tng_source_route", ROOT / "tools/audit_tng_source_route.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TngSourceRouteAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original, cls.sha = mod.read_bundle()

    def analyze(self, mutation=None):
        bundle = copy.deepcopy(self.original)
        if mutation:
            mutation(bundle)
        return mod.analyze(bundle, self.sha)

    def test_accepted_metadata_cannot_claim_full_episode_binding(self):
        report = self.analyze()
        self.assertEqual(report["status"], "STRUCTURAL_ROUTE_BLOCKED")
        self.assertEqual(report["accepted_effect"], "NONE")
        self.assertEqual(report["coverage_effect"], "NONE")
        self.assertEqual(report["observed_publisher_slot"], "S1E26")
        self.assertTrue(all(value is False for value in report["technical_checks"].values()))
        for key in ("independent_audiovisual_bytes_inspected", "rights_valid_full_episode_custody",
                    "independent_work_identity_adjudication"):
            self.assertEqual(report[key], "NOT_ESTABLISHED")

    def test_unreviewed_source_bytes_cannot_be_substituted(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "pilot.json"
            candidate.write_bytes(mod.PILOT.read_bytes() + b" ")
            with self.assertRaisesRegex(mod.RouteAuditError, "bytes changed"):
                mod.read_bundle(candidate)

    def test_paper_promotion_cannot_pass_metadata_representation_gate(self):
        def paper_promotion(bundle):
            source = bundle["sources"][0]
            work = bundle["works"][0]
            binding = bundle["bindings"][0]
            source["status"] = work["status"] = binding["lifecycle"] = "ACCEPTED"
            work["parent_work_id"] = "fabricated:parent:work"
            binding["mapping_role"] = "EVIDENCE_BEARING"
            source["content_hash"] = "sha256:" + "a" * 64
            binding["basis"].append({"kind": "BYTE_HASH", "value": source["content_hash"]})
        report = self.analyze(paper_promotion)
        self.assertEqual(report["status"], "STRUCTURAL_ROUTE_BLOCKED")
        self.assertFalse(report["technical_checks"]["source_representation_beyond_metadata"])
        self.assertEqual(report["rights_valid_full_episode_custody"], "NOT_ESTABLISHED")

    def test_lineage_swap_rejected(self):
        with self.assertRaisesRegex(mod.RouteAuditError, "lineage"):
            self.analyze(lambda b: b["sources"][0].update(provenance_family="publisher:independent"))

    def test_identity_crossing_rejected(self):
        with self.assertRaisesRegex(mod.RouteAuditError, "tuple changed"):
            self.analyze(lambda b: b["bindings"][0].update(source_id=b["sources"][1]["source_id"]))

    def test_ambiguous_binding_rejected(self):
        def duplicate(bundle):
            extra = copy.deepcopy(bundle["bindings"][0])
            extra["binding_id"] += ":other"
            bundle["bindings"].append(extra)
        with self.assertRaisesRegex(mod.RouteAuditError, "ambiguous"):
            self.analyze(duplicate)

    def test_duplicate_record_id_rejected(self):
        with self.assertRaisesRegex(mod.RouteAuditError, "duplicate source"):
            self.analyze(lambda b: b["sources"].append(copy.deepcopy(b["sources"][0])))

    def test_no_silent_acceptance_after_optimized_interpreter(self):
        # Assertions in this suite are unittest assertions, not Python `assert`.
        report = self.analyze()
        self.assertEqual(report["status"], "STRUCTURAL_ROUTE_BLOCKED")


if __name__ == "__main__":
    unittest.main()
