"""Regression tests for the PR #3 TNG metadata-only recovery adapter."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "recover_tng_pilot.py"
SPEC = importlib.util.spec_from_file_location("recover_tng_pilot", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def fixture():
    blobs = {}
    hashes = {}
    verified = {}
    for i in range(9):
        name = f"records/{i+1:02d}-candidate.json"
        blobs[name] = f"{i+1:040x}"
        hashes[name] = f"{i+1:064x}"
        verified[name] = (blobs[name], hashes[name])
    for i, name in enumerate(("validation.json", "coverage_update.json"), start=10):
        blobs[name] = f"{i:040x}"
        hashes[name] = f"{i:064x}"
        verified[name] = (blobs[name], hashes[name])
    scope, sources = [], []
    for i in range(1, 6):
        ref = f"local.fixture.work.{i}"
        scope.append({
            "work_local_ref": ref,
            "display_title": f"Test Episode {i}",
            "airdate_crosscheck": "1987-09-28",
            "production_code_crosscheck": str(100+i),
            "transcript_index": f"s01e{i:02d}",
        })
        sources.append({
            "work_local_ref": ref,
            "url": f"https://transcripts.example.test/{i}",
            "crosscheck_url": f"https://crosscheck.example.test/{i}",
            "provider": "Example provider",
            "crosscheck_provider": "Example crosscheck",
            "retrieved_utc_date": "2026-08-14",
            "line_extent_processed": "1-99",
            "source_type": "third party transcript",
            "primary_audiovisual_verified": False,
            "lineage_independence": "UNKNOWN",
        })
    return {
        "batch_id": "tng-s01-b001",
        "lane": "TNG",
        "status": "PROPOSAL_VALIDATED",
        "base_main_sha": "a"*40,
        "record_counts": dict(mod.EXPECTED_COUNTS),
        "artifact_git_blob_sha1": blobs,
        "artifact_sha256": hashes,
        "scope": scope,
        "source_strategy": sources,
        "known_blockers": ["no registry", "audiovisual missing", "lineage unknown", "identity deferred"],
        "numbering_note": "Fixture conventions differ.",
    }, verified


class RecoveryTests(unittest.TestCase):
    def build(self, manifest, verified):
        return mod.build_proposal(manifest, "a"*40, "b"*40, b"fixture bytes", verified)

    def test_proposals_only_no_admitted_id_or_coverage(self):
        manifest, verified = fixture()
        result = self.build(manifest, verified)
        self.assertEqual(result["accepted_corpus_effect"], "NONE")
        self.assertEqual(result["accepted_coverage_effect"], "NONE")
        self.assertEqual(result["original_candidate_counts"], {"works": 5, "evidence": 58, "local_entities": 69, "assertions": 31})
        self.assertEqual(len(result["episode_work_candidates"]), 5)
        self.assertEqual(len(result["artifacts_verified"]), 11)
        for work in result["episode_work_candidates"]:
            self.assertEqual(work["status"], "CANDIDATE")
            self.assertIsNone(work["canonical_work_id"])
            self.assertIsNone(work["canonical_source_id"])
            self.assertEqual(work["source_work_binding_status"], "NOT_ADMITTED")
        payload = json.dumps(result)
        self.assertNotIn("transcript_text", payload)
        self.assertNotIn("dialogue", payload)

    def test_repeated_runs_are_byte_deterministic(self):
        manifest, verified = fixture()
        a, b = self.build(manifest, verified), self.build(manifest, verified)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_duplicate_work_reference_fails(self):
        manifest, verified = fixture()
        manifest["scope"][1]["work_local_ref"] = manifest["scope"][0]["work_local_ref"]
        with self.assertRaisesRegex(mod.RecoveryError, "duplicate/unbound"):
            self.build(manifest, verified)

    def test_duplicate_source_reference_fails(self):
        manifest, verified = fixture()
        manifest["source_strategy"][1]["work_local_ref"] = manifest["source_strategy"][0]["work_local_ref"]
        with self.assertRaisesRegex(mod.RecoveryError, "duplicate source"):
            self.build(manifest, verified)

    def test_duplicate_episode_title_fails(self):
        manifest, verified = fixture()
        manifest["scope"][1]["display_title"] = manifest["scope"][0]["display_title"]
        with self.assertRaisesRegex(mod.RecoveryError, "duplicate title"):
            self.build(manifest, verified)

    def test_duplicate_transcript_index_fails(self):
        manifest, verified = fixture()
        manifest["scope"][1]["transcript_index"] = manifest["scope"][0]["transcript_index"]
        with self.assertRaisesRegex(mod.RecoveryError, "duplicate transcript"):
            self.build(manifest, verified)

    def test_modified_blob_identity_fails(self):
        manifest, verified = fixture()
        manifest["artifact_git_blob_sha1"]["records/01-candidate.json"] = "f"*40
        with self.assertRaisesRegex(mod.RecoveryError, "digest mismatch"):
            self.build(manifest, verified)

    def test_artifact_path_traversal_fails(self):
        manifest, verified = fixture()
        manifest["artifact_git_blob_sha1"]["../bad.json"] = manifest["artifact_git_blob_sha1"].pop("records/01-candidate.json")
        manifest["artifact_sha256"]["../bad.json"] = manifest["artifact_sha256"].pop("records/01-candidate.json")
        with self.assertRaisesRegex(mod.RecoveryError, "unsafe or unexpected"):
            self.build(manifest, verified)

    def test_counts_cannot_mint_accepted_coverage(self):
        manifest, verified = fixture()
        manifest["record_counts"]["works"] = 6
        with self.assertRaisesRegex(mod.RecoveryError, "aggregate counts"):
            self.build(manifest, verified)

    def test_non_https_source_fails(self):
        manifest, verified = fixture()
        manifest["source_strategy"][0]["url"] = "http://example.test/transcript"
        with self.assertRaisesRegex(mod.RecoveryError, "not HTTPS"):
            self.build(manifest, verified)

    def test_output_restricted_to_proposals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(mod.output_path(root, "proposals/tng/candidates.json"), root/"proposals/tng/candidates.json")
            for path in ("/tmp/candidates.json", "other/candidates.json", "proposals/../../bad.json"):
                with self.assertRaises(mod.RecoveryError):
                    mod.output_path(root, path)

    def test_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)/"repo"
            root.mkdir()
            (root/"proposals").symlink_to(Path(temp))
            with self.assertRaisesRegex(mod.RecoveryError, "symlink"):
                mod.output_path(root, "proposals/tng/candidates.json")


if __name__ == "__main__":
    unittest.main()
