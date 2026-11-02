"""Offline, deterministic and adversarial Explorer index safety tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("explorer_index", ROOT / "tools" / "build_explorer_index.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExplorerIndexTests(unittest.TestCase):
    def approved(self, root, manifest):
        path = root / "approved.json"
        path.write_text(json.dumps({"authority": "REVIEWED_MAIN_PROJECTION_HASH_ALLOWLIST", "projection_hashes": [manifest["projection_hash"]]}))
        return path

    def test_catalog_is_display_only_and_contains_twelve_distinct_missions(self):
        result = module.build_index(ROOT / "registry" / "mission_catalog.json")
        self.assertEqual(len(result["missions"]), 12)
        self.assertEqual(len({m["id"] for m in result["missions"]}), 12)
        self.assertEqual(result["build"]["data_status"], "MISSION_CATALOG_ONLY")
        self.assertEqual(result["briefings"], [])
        self.assertEqual(result["records"], [])

    def test_byte_determinism(self):
        result = module.build_index(ROOT / "registry" / "mission_catalog.json")
        self.assertEqual(module.canonical(result), module.canonical(module.build_index(ROOT / "registry" / "mission_catalog.json")))

    def test_duplicate_missions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            catalog = json.loads((ROOT / "registry" / "mission_catalog.json").read_text())
            catalog["missions"].append(catalog["missions"][0])
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError, "Duplicate Mission"):
                module.build_index(path)

    def test_projection_requires_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                module.build_index(ROOT / "registry" / "mission_catalog.json", Path(tmp))

    def test_projection_hash_and_count_rejected_when_tampered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs = {}
            for filename in module.CANONICAL_OUTPUTS:
                (root / filename).write_text("")
                outputs[filename] = {"hash": module.sha256(b""), "count": 0}
            manifest = {"record_type": "projection_manifest", "outputs": outputs, "projection_hash": module.sha256(module.canonical({k: v["hash"] for k, v in outputs.items()}).encode())}
            (root / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "reviewed mainline admission receipt"):
                module.build_index(ROOT / "registry" / "mission_catalog.json", root)
            approved = self.approved(root, manifest)
            result = module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)
            self.assertEqual(result["build"]["data_status"], "GOVERNED_PROJECTION")
            (root / "facts.jsonl").write_text("{}\n")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)

    def test_projected_assertion_without_admitted_binding_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs = {}
            fact = {"assertion_id": "a1", "effective_assertion_status": "ACCEPTED", "projection_status": "STABLE", "predicate": "observed", "subject": "test"}
            proof = {
                "assertion_id": "a1",
                "effective_assertion_status": "ACCEPTED",
                "evidence_record": {"source_id": "s1", "work_id": "w1"},
                "source_record": {"source_id": "s1", "status": "ACCEPTED", "fixture_only": False},
                "work_record": {"work_id": "w1", "status": "ACCEPTED", "fixture_only": False, "series": "tos", "work_type": "EPISODE", "title": "Test Episode"},
            }
            for filename in module.CANONICAL_OUTPUTS:
                rows = [fact] if filename == "facts.jsonl" else [proof] if filename == "provenance.jsonl" else []
                payload = ("\n".join(module.canonical(row) for row in rows) + ("\n" if rows else "")).encode()
                (root / filename).write_bytes(payload)
                outputs[filename] = {"hash": module.sha256(payload), "count": len(rows)}
            manifest = {"record_type": "projection_manifest", "outputs": outputs, "projection_hash": module.sha256(module.canonical({k: v["hash"] for k, v in outputs.items()}).encode())}
            (root / "manifest.json").write_text(json.dumps(manifest))
            approved = self.approved(root, manifest)
            with self.assertRaisesRegex(ValueError, "Missing accepted Source-to-Work binding"):
                module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)
            proof["source_work_binding_record"] = {"binding_id": "b1", "source_id": "s1", "work_id": "w1", "lifecycle": "ACCEPTED", "mapping_role": "EVIDENCE_BEARING", "fixture_only": True}
            self._write_proof(root, outputs, manifest, proof)
            approved = self.approved(root, manifest)
            with self.assertRaisesRegex(ValueError, "Synthetic or unadmitted"):
                module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)
            proof["source_work_binding_record"]["fixture_only"] = False
            self._write_proof(root, outputs, manifest, proof)
            approved = self.approved(root, manifest)
            result = module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)
            self.assertEqual(result["records"][0]["source_ids"], ["s1"])
            self.assertEqual(result["briefings"][0]["title"], "Test Episode")
            # Reviewed provenance may still be inconsistent across distinct proofs.
            conflicting = dict(proof)
            conflicting["provenance_id"] = "a1::e2"
            conflicting["work_record"] = {**proof["work_record"], "title": "Contradictory Episode"}
            payload = (module.canonical(proof) + "\n" + module.canonical(conflicting) + "\n").encode()
            (root / "provenance.jsonl").write_bytes(payload)
            outputs["provenance.jsonl"] = {"hash": module.sha256(payload), "count": 2}
            manifest["projection_hash"] = module.sha256(module.canonical({k: v["hash"] for k, v in outputs.items()}).encode())
            (root / "manifest.json").write_text(json.dumps(manifest))
            approved = self.approved(root, manifest)
            with self.assertRaisesRegex(ValueError, "Contradictory work provenance metadata"):
                module.build_index(ROOT / "registry" / "mission_catalog.json", root, approved)

    def _write_proof(self, root, outputs, manifest, proof):
            payload = (module.canonical(proof) + "\n").encode()
            (root / "provenance.jsonl").write_bytes(payload)
            outputs["provenance.jsonl"] = {"hash": module.sha256(payload), "count": 1}
            manifest["projection_hash"] = module.sha256(module.canonical({k: v["hash"] for k, v in outputs.items()}).encode())
            (root / "manifest.json").write_text(json.dumps(manifest))

    def test_unbounded_text_not_indexed(self):
        self.assertEqual(module.bounded_metadata("x" * 161), "")
        self.assertEqual(module.bounded_metadata({"dialogue": "x"}), "")


if __name__ == "__main__":
    unittest.main()
