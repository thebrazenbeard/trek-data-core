#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("build_graph_search.py")
spec = importlib.util.spec_from_file_location("trek_build_graph_search", MODULE_PATH)
graph_search = importlib.util.module_from_spec(spec)
if spec.loader is not None:
    spec.loader.exec_module(graph_search)


def write_jsonl(root, filename, rows):
    (root / filename).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def write_projection(root, conflicting_evidence=False, domain_relation=False):
    (root / "manifest.json").write_text(json.dumps({
        "record_type": "projection_manifest",
        "projection_version": "0.1.0",
        "schema_version": "0.1.0",
        "methodology_version": "0.1.0",
        "compiler_commit": "fixture",
        "research_head": "research-fixture",
        "reconciliation_head": "recon-fixture",
        "predicate_registry_hash": "sha256:predicate",
        "input_hash": "sha256:input",
        "projection_hash": "sha256:projection-fixture",
        "outputs": {},
    }) + "\n", encoding="utf-8")
    write_jsonl(root, "entities.jsonl", [
        {"record_type": "local_entity", "local_entity_id": "local-1", "work_id": "work-1", "label": "Fixture Entity", "resolved_entity": "global:one"},
    ])
    write_jsonl(root, "facts.jsonl", [
        {"record_type": "assertion", "assertion_id": "a1", "subject": "local-1", "resolved_subject": "global:one", "predicate": "CLAIMS", "object": {"text": "stable fixture"}, "projection_status": "STABLE"},
    ])
    write_jsonl(root, "contested.jsonl", [
        {"record_type": "assertion", "assertion_id": "a2", "subject": "local-1", "predicate": "CLAIMS", "object": {"text": "paradox fixture"}, "projection_status": "STRUCTURAL_PARADOX"},
    ])
    write_jsonl(root, "unresolved.jsonl", [])
    write_jsonl(root, "relations.jsonl", [
        {"relation_id": "r1", "source": "local-1", "predicate": "CLAIMS", "target": "unknown-shape"}
    ] if domain_relation else [])
    provenance = [
        {"provenance_id": "a1::e1", "assertion_id": "a1", "evidence_id": "e1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "dialogue", "source_content_hash": "sha256:source-a", "work_title": "Fixture Work"},
        {"provenance_id": "a2::e1", "assertion_id": "a2", "evidence_id": "e1", "source_id": "source-1", "work_id": "work-1", "evidence_kind": "dialogue", "source_content_hash": "sha256:source-a" if not conflicting_evidence else "sha256:source-b", "work_title": "Fixture Work"},
    ]
    write_jsonl(root, "provenance.jsonl", provenance)
    write_jsonl(root, "accepted_reconciliation.jsonl", [])


def read_jsonl(path):
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


class GraphSearchProjectionTests(unittest.TestCase):
    def test_graph_contains_only_structural_edges_not_domain_predicate_edges(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection)
            out = Path(td) / "out"
            graph_search.build_bundle(projection, out)
            edges = read_jsonl(out / "graph_edges.jsonl")
            kinds = {edge["edge_kind"] for edge in edges}
            self.assertIn("ASSERTION_SUBJECT", kinds)
            self.assertIn("ASSERTION_EVIDENCE", kinds)
            self.assertIn("EVIDENCE_SOURCE", kinds)
            self.assertIn("EVIDENCE_WORK", kinds)
            self.assertIn("ENTITY_WORK", kinds)
            self.assertNotIn("CLAIMS", kinds)

    def test_graph_nodes_preserve_projection_status(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection)
            out = Path(td) / "out"; graph_search.build_bundle(projection, out)
            nodes = {row["node_id"]: row for row in read_jsonl(out / "graph_nodes.jsonl")}
            self.assertEqual(nodes["assertion:a2"]["projection_status"], "STRUCTURAL_PARADOX")
            self.assertEqual(nodes["assertion:a2"]["partition"], "contested")

    def test_search_documents_preserve_literal_content_and_status(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection)
            out = Path(td) / "out"; graph_search.build_bundle(projection, out)
            docs = {row["document_id"]: row for row in read_jsonl(out / "search_documents.jsonl")}
            self.assertEqual(docs["assertion:a2"]["projection_status"], "STRUCTURAL_PARADOX")
            self.assertIn("paradox fixture", docs["assertion:a2"]["text"])
            self.assertIn("Fixture Entity", docs["entity:local-1"]["text"])

    def test_bundle_is_deterministic_and_projection_pinned(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection)
            first = Path(td) / "first"; second = Path(td) / "second"
            manifest_a = graph_search.build_bundle(projection, first)
            manifest_b = graph_search.build_bundle(projection, second)
            self.assertEqual(manifest_a, manifest_b)
            self.assertEqual(manifest_a["projection_hash"], "sha256:projection-fixture")
            for filename in ("graph_nodes.jsonl", "graph_edges.jsonl", "search_documents.jsonl", "manifest.json"):
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())

    def test_conflicting_structural_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection, conflicting_evidence=True)
            out = Path(td) / "out"
            with self.assertRaises(ValueError):
                graph_search.build_bundle(projection, out)

    def test_nonempty_domain_relations_fail_closed_until_schema_is_governed(self):
        with tempfile.TemporaryDirectory() as td:
            projection = Path(td) / "projection"; projection.mkdir(); write_projection(projection, domain_relation=True)
            out = Path(td) / "out"
            with self.assertRaises(ValueError):
                graph_search.build_bundle(projection, out)


if __name__ == "__main__":
    unittest.main()
