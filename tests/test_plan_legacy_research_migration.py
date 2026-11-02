"""Synthetic-only, adversarial tests for the untrusted legacy dry-run reader."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "tools" / "plan_legacy_research_migration.py"
spec = importlib.util.spec_from_file_location("plan_legacy_research_migration", TOOL)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def serialized(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class PlanLegacyMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "records").mkdir()
        self.record = {
            "batch_id": "tng-demo", "lane": "TNG", "schema_version": "LEGACY_TEST_V1",
            "evidence": [{"id": "ev1", "src": "T", "loc": "12-20", "work": "local-work"}],
            "assertions": [{"id": "as1", "support": ["ev1"]}],
            "local_entities": [{"id": "entity1", "work": "local-work", "global_identity": "UNRESOLVED_LOCAL_ONLY"}],
        }
        self.manifest = {
            "status": "PROPOSAL_VALIDATED", "batch_id": "tng-demo", "lane": "TNG",
            "schema_version": "LEGACY_TEST_V1",
            "source_strategy": [{"alias": "T", "provider": "unverified", "url": "https://example.invalid"}],
            "scope": [{"work_local_ref": "local-work", "display_title": "Synthetic episode"}],
            "record_counts": {"works": 1, "evidence": 1, "assertions": 1, "local_entities": 1},
        }

    def fixture(self) -> str:
        data = serialized(self.record)
        (self.root / "records" / "one.json").write_bytes(data)
        self.manifest["artifact_sha256"] = {"records/one.json": sha256(data)}
        self.manifest["artifact_git_blob_sha1"] = {"records/one.json": git_sha(data)}
        manifest_bytes = serialized(self.manifest)
        (self.root / "manifest.json").write_bytes(manifest_bytes)
        return sha256(manifest_bytes)

    def test_valid_fixture_is_only_a_proposal_and_deterministic(self) -> None:
        digest = self.fixture()
        a = module.plan(self.root, digest, source_pr=3, source_head_sha="a" * 40)
        b = module.plan(self.root, digest, source_pr=3, source_head_sha="a" * 40)
        self.assertEqual(a, b)
        self.assertEqual(a["observed_record_counts"], {"evidence": 1, "assertions": 1, "local_entities": 1})
        self.assertEqual(a["evidence_locators"][0]["locator"], "12-20")
        self.assertEqual(a["accepted_source_work_evidence_assertion_coverage_effect"], "NONE")
        self.assertFalse(a["external_source_bytes_inspected"])
        self.assertEqual(a["status"], "STRUCTURAL_MIGRATION_CANDIDATE_NOT_ADMITTED")

    def test_record_byte_corruption_rejected(self) -> None:
        digest = self.fixture()
        (self.root / "records" / "one.json").write_bytes(b"{}")
        with self.assertRaisesRegex(module.MigrationRejected, "hashes disagree"):
            module.plan(self.root, digest)

    def test_manifest_byte_corruption_rejected(self) -> None:
        digest = self.fixture()
        (self.root / "manifest.json").write_bytes(b"{}")
        with self.assertRaisesRegex(module.MigrationRejected, "manifest hash"):
            module.plan(self.root, digest)

    def test_parent_traversal_rejected(self) -> None:
        self.fixture()
        self.manifest["artifact_sha256"] = {"records/../one.json": "0" * 64}
        self.manifest["artifact_git_blob_sha1"] = {"records/../one.json": "0" * 40}
        digest = sha256(serialized(self.manifest))
        (self.root / "manifest.json").write_bytes(serialized(self.manifest))
        with self.assertRaisesRegex(module.MigrationRejected, "unsafe artifact path"):
            module.plan(self.root, digest)

    def test_symlinked_artifact_rejected(self) -> None:
        digest = self.fixture()
        artifact = self.root / "records" / "one.json"
        genuine = self.root / "original.json"
        artifact.rename(genuine)
        artifact.symlink_to(genuine)
        with self.assertRaisesRegex(module.MigrationRejected, "bounded regular file"):
            module.plan(self.root, digest)

    def test_invalid_local_identity_rejected(self) -> None:
        self.record["local_entities"][0]["global_identity"] = "SAME_AS_ACCEPTED_GLOBAL_ID"
        with self.assertRaisesRegex(module.MigrationRejected, "global identity"):
            module.plan(self.root, self.fixture())

    def test_missing_assertion_support_rejected(self) -> None:
        self.record["assertions"][0]["support"] = ["nonexistent-evidence"]
        with self.assertRaisesRegex(module.MigrationRejected, "missing evidence support"):
            module.plan(self.root, self.fixture())

    def test_duplicate_cross_category_ids_rejected(self) -> None:
        self.record["local_entities"][0]["id"] = "ev1"
        with self.assertRaisesRegex(module.MigrationRejected, "duplicate cross-file local record ID"):
            module.plan(self.root, self.fixture())

    def test_count_mismatch_rejected(self) -> None:
        self.manifest["record_counts"]["evidence"] = 99
        with self.assertRaisesRegex(module.MigrationRejected, "record counts"):
            module.plan(self.root, self.fixture())

    def test_unknown_status_rejected(self) -> None:
        self.manifest["status"] = "ACCEPTED"
        with self.assertRaisesRegex(module.MigrationRejected, "unsupported legacy status"):
            module.plan(self.root, self.fixture())

    def test_unknown_source_alias_rejected(self) -> None:
        self.record["evidence"][0]["src"] = "UNKNOWN"
        with self.assertRaisesRegex(module.MigrationRejected, "undeclared source alias"):
            module.plan(self.root, self.fixture())


if __name__ == "__main__":
    unittest.main()
