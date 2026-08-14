#!/usr/bin/env python3
"""Build deterministic structural graph and literal search projections.

No domain predicate is interpreted as a graph relation here. Structural edges only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ASSERTION_PARTITIONS = {
    "facts.jsonl": "facts",
    "contested.jsonl": "contested",
    "unresolved.jsonl": "unresolved",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


def merge_node(nodes, node_id, values):
    incoming = {"node_id": node_id, **{key: value for key, value in values.items() if value is not None}}
    existing = nodes.get(node_id)
    if existing is None:
        nodes[node_id] = incoming
        return
    for key, value in incoming.items():
        if key == "node_id":
            continue
        if key not in existing or existing[key] is None:
            existing[key] = value
        elif value is not None and existing[key] != value:
            raise ValueError(f"conflicting structural metadata for {node_id}.{key}: {existing[key]!r} vs {value!r}")


def add_edge(edges, edge_id, edge_kind, source_node, target_node, **metadata):
    row = {
        "edge_id": edge_id,
        "edge_kind": edge_kind,
        "source_node": source_node,
        "target_node": target_node,
        **{key: value for key, value in metadata.items() if value is not None},
    }
    existing = edges.get(edge_id)
    if existing is not None and existing != row:
        raise ValueError(f"conflicting structural edge {edge_id}")
    edges[edge_id] = row


def string_values(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float, bool)):
        return [str(value)]
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(string_values(item))
        return out
    if isinstance(value, dict):
        out = []
        for key in sorted(value):
            out.extend(string_values(value[key]))
        return out
    return []


def write_jsonl(path: Path, rows, id_key):
    ordered = sorted(rows, key=lambda row: (str(row.get(id_key, "")), canonical(row)))
    payload = "".join(canonical(row) + "\n" for row in ordered).encode("utf-8")
    path.write_bytes(payload)
    return {"hash": sha256_bytes(payload), "count": len(ordered)}


def build_bundle(projection_root: Path, output_root: Path):
    projection_root, output_root = Path(projection_root), Path(output_root)
    manifest = json.loads((projection_root / "manifest.json").read_text(encoding="utf-8"))
    projection_hash = manifest.get("projection_hash")
    if not projection_hash:
        raise ValueError("projection manifest missing projection_hash")

    domain_relations = load_rows(projection_root / "relations.jsonl")
    if domain_relations:
        raise ValueError("relations.jsonl is non-empty but no governed relation row schema exists for graph mapping")

    nodes = {}
    edges = {}
    search_records = {}
    local_entity_ids = set()

    for entity in sorted(load_rows(projection_root / "entities.jsonl"), key=lambda row: row.get("local_entity_id", "")):
        local_id = entity.get("local_entity_id")
        if not local_id:
            raise ValueError("entity row missing local_entity_id")
        local_entity_ids.add(local_id)
        node_id = f"entity:{local_id}"
        merge_node(nodes, node_id, {
            "node_kind": "local_entity",
            "local_entity_id": local_id,
            "work_id": entity.get("work_id"),
            "label": entity.get("label"),
            "resolved_entity": entity.get("resolved_entity"),
            "record": entity,
        })
        if entity.get("work_id"):
            work_node = f"work:{entity['work_id']}"
            merge_node(nodes, work_node, {"node_kind": "work", "work_id": entity["work_id"]})
            add_edge(edges, f"{node_id}::work::{entity['work_id']}", "ENTITY_WORK", node_id, work_node)
        search_records[node_id] = {
            "document_id": node_id,
            "document_kind": "local_entity",
            "text": " ".join(string_values(entity)),
            "record": entity,
        }

    assertion_rows = {}
    for filename, partition in ASSERTION_PARTITIONS.items():
        for assertion in sorted(load_rows(projection_root / filename), key=lambda row: row.get("assertion_id", "")):
            assertion_id = assertion.get("assertion_id")
            if not assertion_id:
                raise ValueError(f"{filename}: assertion missing assertion_id")
            if assertion_id in assertion_rows:
                raise ValueError(f"assertion {assertion_id} appears in multiple projection partitions")
            assertion_rows[assertion_id] = (assertion, partition)
            node_id = f"assertion:{assertion_id}"
            merge_node(nodes, node_id, {
                "node_kind": "assertion",
                "assertion_id": assertion_id,
                "projection_status": assertion.get("projection_status"),
                "partition": partition,
                "predicate": assertion.get("predicate"),
                "record": assertion,
            })
            subject = assertion.get("subject")
            if subject in local_entity_ids:
                add_edge(edges, f"{node_id}::subject::{subject}", "ASSERTION_SUBJECT", node_id, f"entity:{subject}")
            search_records[node_id] = {
                "document_id": node_id,
                "document_kind": "assertion",
                "projection_status": assertion.get("projection_status"),
                "partition": partition,
                "text": " ".join(string_values(assertion)),
                "record": assertion,
            }

    for prov in sorted(load_rows(projection_root / "provenance.jsonl"), key=lambda row: row.get("provenance_id", "")):
        assertion_id = prov.get("assertion_id")
        evidence_id = prov.get("evidence_id")
        if assertion_id not in assertion_rows:
            raise ValueError(f"provenance references missing projected assertion {assertion_id}")
        if not evidence_id:
            raise ValueError("provenance row missing evidence_id")

        assertion_node = f"assertion:{assertion_id}"
        evidence_node = f"evidence:{evidence_id}"
        merge_node(nodes, evidence_node, {
            "node_kind": "evidence",
            "evidence_id": evidence_id,
            "source_id": prov.get("source_id"),
            "work_id": prov.get("work_id"),
            "evidence_kind": prov.get("evidence_kind"),
            "source_content_hash": prov.get("source_content_hash"),
        })
        add_edge(edges, f"{assertion_node}::evidence::{evidence_id}", "ASSERTION_EVIDENCE", assertion_node, evidence_node)

        source_id = prov.get("source_id")
        if source_id:
            source_node = f"source:{source_id}"
            merge_node(nodes, source_node, {
                "node_kind": "source",
                "source_id": source_id,
                "content_hash": prov.get("source_content_hash"),
                "locator": prov.get("source_locator"),
            })
            add_edge(edges, f"{evidence_node}::source::{source_id}", "EVIDENCE_SOURCE", evidence_node, source_node)

        work_id = prov.get("work_id")
        if work_id:
            work_node = f"work:{work_id}"
            merge_node(nodes, work_node, {
                "node_kind": "work",
                "work_id": work_id,
                "title": prov.get("work_title"),
            })
            add_edge(edges, f"{evidence_node}::work::{work_id}", "EVIDENCE_WORK", evidence_node, work_node)

    # Add literal search documents for provenance-derived structural nodes.
    for node_id, node in sorted(nodes.items()):
        if node_id in search_records:
            continue
        search_records[node_id] = {
            "document_id": node_id,
            "document_kind": node.get("node_kind"),
            "text": " ".join(string_values(node)),
            "record": node,
        }

    output_root.mkdir(parents=True, exist_ok=True)
    outputs = {
        "graph_nodes.jsonl": write_jsonl(output_root / "graph_nodes.jsonl", nodes.values(), "node_id"),
        "graph_edges.jsonl": write_jsonl(output_root / "graph_edges.jsonl", edges.values(), "edge_id"),
        "search_documents.jsonl": write_jsonl(output_root / "search_documents.jsonl", search_records.values(), "document_id"),
    }
    bundle_manifest = {
        "record_type": "graph_search_projection_bundle",
        "bundle_version": "0.1.0",
        "projection_hash": projection_hash,
        "outputs": outputs,
        "domain_relation_mapping": "DEFERRED_UNTIL_GOVERNED_RELATION_SCHEMA",
    }
    (output_root / "manifest.json").write_text(json.dumps(bundle_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return bundle_manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projection")
    ap.add_argument("output")
    args = ap.parse_args()
    manifest = build_bundle(Path(args.projection), Path(args.output))
    print(manifest["projection_hash"])


if __name__ == "__main__":
    main()
