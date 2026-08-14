#!/usr/bin/env python3
"""Generate a deterministic PostgreSQL rebuild script from canonical projection JSONL.

This tool writes SQL files only. It never connects to PostgreSQL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "trek_projection_v0_1"
ASSERTION_PARTITIONS = {
    "facts.jsonl": "facts",
    "contested.jsonl": "contested",
    "unresolved.jsonl": "unresolved",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


def sql_text(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_jsonb(value):
    if value is None:
        return "NULL"
    return sql_text(canonical(value)) + "::jsonb"


def insert(table, columns, values):
    return f"INSERT INTO {SCHEMA}.{table} ({','.join(columns)}) VALUES ({','.join(values)});"


def generate_sql(projection_root: Path):
    projection_root = Path(projection_root)
    manifest = json.loads((projection_root / "manifest.json").read_text(encoding="utf-8"))
    projection_hash = manifest.get("projection_hash")
    if not projection_hash:
        raise ValueError("projection manifest missing projection_hash")

    lines = [
        "-- Generated derived PostgreSQL projection. Do not treat database storage as source truth.",
        f"-- canonical_projection_hash: {projection_hash}",
        "BEGIN;",
        f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;",
        f"CREATE SCHEMA {SCHEMA};",
        "",
        f"CREATE TABLE {SCHEMA}.metadata (key text PRIMARY KEY, value text NOT NULL);",
        f"CREATE TABLE {SCHEMA}.entities (",
        "  local_entity_id text PRIMARY KEY,",
        "  work_id text,",
        "  label text,",
        "  resolved_entity jsonb,",
        "  reconciliation_decision_id text,",
        "  record_json jsonb NOT NULL",
        ");",
        f"CREATE TABLE {SCHEMA}.assertions (",
        "  assertion_id text PRIMARY KEY,",
        "  projection_status text NOT NULL,",
        "  partition text NOT NULL CHECK (partition IN ('facts','contested','unresolved')),",
        "  subject text,",
        "  resolved_subject jsonb,",
        "  predicate text,",
        "  object_json jsonb,",
        "  scope_json jsonb,",
        "  resolved_scope jsonb,",
        "  record_json jsonb NOT NULL",
        ");",
        f"CREATE TABLE {SCHEMA}.provenance (",
        "  provenance_id text PRIMARY KEY,",
        "  assertion_id text NOT NULL REFERENCES " + SCHEMA + ".assertions(assertion_id),",
        "  evidence_id text, source_id text, work_id text, evidence_kind text, source_content_hash text,",
        "  record_json jsonb NOT NULL",
        ");",
        f"CREATE TABLE {SCHEMA}.reconciliation (",
        "  decision_id text PRIMARY KEY, decision_type text, subject_id text, status text, supersedes text,",
        "  value_json jsonb, record_json jsonb NOT NULL",
        ");",
        f"CREATE TABLE {SCHEMA}.relations (relation_id text PRIMARY KEY, record_json jsonb NOT NULL);",
        "",
    ]

    metadata_keys = (
        "projection_hash", "input_hash", "projection_version", "schema_version", "methodology_version",
        "research_head", "reconciliation_head", "predicate_registry_hash", "compiler_commit",
    )
    for key in metadata_keys:
        if key in manifest and manifest[key] is not None:
            lines.append(insert("metadata", ["key", "value"], [sql_text(key), sql_text(manifest[key])]))

    for row in sorted(load_rows(projection_root / "entities.jsonl"), key=lambda item: item.get("local_entity_id", "")):
        lines.append(insert(
            "entities",
            ["local_entity_id", "work_id", "label", "resolved_entity", "reconciliation_decision_id", "record_json"],
            [
                sql_text(row.get("local_entity_id")), sql_text(row.get("work_id")), sql_text(row.get("label")),
                sql_jsonb(row.get("resolved_entity")), sql_text(row.get("reconciliation_decision_id")), sql_jsonb(row),
            ],
        ))

    seen_assertions = set()
    for filename, partition in ASSERTION_PARTITIONS.items():
        for row in sorted(load_rows(projection_root / filename), key=lambda item: item.get("assertion_id", "")):
            assertion_id = row.get("assertion_id")
            if assertion_id in seen_assertions:
                raise ValueError(f"assertion {assertion_id} appears in multiple projection partitions")
            seen_assertions.add(assertion_id)
            lines.append(insert(
                "assertions",
                ["assertion_id", "projection_status", "partition", "subject", "resolved_subject", "predicate", "object_json", "scope_json", "resolved_scope", "record_json"],
                [
                    sql_text(assertion_id), sql_text(row.get("projection_status")), sql_text(partition), sql_text(row.get("subject")),
                    sql_jsonb(row.get("resolved_subject")), sql_text(row.get("predicate")), sql_jsonb(row.get("object")),
                    sql_jsonb(row.get("scope")), sql_jsonb(row.get("resolved_scope")), sql_jsonb(row),
                ],
            ))

    for row in sorted(load_rows(projection_root / "provenance.jsonl"), key=lambda item: item.get("provenance_id", "")):
        lines.append(insert(
            "provenance",
            ["provenance_id", "assertion_id", "evidence_id", "source_id", "work_id", "evidence_kind", "source_content_hash", "record_json"],
            [
                sql_text(row.get("provenance_id")), sql_text(row.get("assertion_id")), sql_text(row.get("evidence_id")),
                sql_text(row.get("source_id")), sql_text(row.get("work_id")), sql_text(row.get("evidence_kind")),
                sql_text(row.get("source_content_hash")), sql_jsonb(row),
            ],
        ))

    for row in sorted(load_rows(projection_root / "accepted_reconciliation.jsonl"), key=lambda item: item.get("decision_id", "")):
        lines.append(insert(
            "reconciliation",
            ["decision_id", "decision_type", "subject_id", "status", "supersedes", "value_json", "record_json"],
            [
                sql_text(row.get("decision_id")), sql_text(row.get("decision_type")), sql_text(row.get("subject_id")),
                sql_text(row.get("status")), sql_text(row.get("supersedes")), sql_jsonb(row.get("value")), sql_jsonb(row),
            ],
        ))

    for row in sorted(load_rows(projection_root / "relations.jsonl"), key=lambda item: item.get("relation_id", "")):
        relation_id = row.get("relation_id")
        if not relation_id:
            raise ValueError("relation row missing relation_id")
        lines.append(insert("relations", ["relation_id", "record_json"], [sql_text(relation_id), sql_jsonb(row)]))

    lines.extend([
        "",
        f"CREATE INDEX assertions_status_idx ON {SCHEMA}.assertions(projection_status);",
        f"CREATE INDEX assertions_subject_idx ON {SCHEMA}.assertions(subject);",
        f"CREATE INDEX assertions_predicate_idx ON {SCHEMA}.assertions(predicate);",
        f"CREATE INDEX provenance_assertion_idx ON {SCHEMA}.provenance(assertion_id);",
        f"CREATE INDEX provenance_source_idx ON {SCHEMA}.provenance(source_id);",
        f"CREATE INDEX reconciliation_subject_idx ON {SCHEMA}.reconciliation(subject_id);",
        "COMMIT;",
        "",
    ])
    return "\n".join(lines)


def write_bundle(projection_root: Path, output_root: Path):
    projection_root, output_root = Path(projection_root), Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    sql = generate_sql(projection_root)
    (output_root / "projection.sql").write_text(sql, encoding="utf-8")
    source_manifest = json.loads((projection_root / "manifest.json").read_text(encoding="utf-8"))
    manifest = {
        "record_type": "postgres_projection_bundle",
        "bundle_version": "0.1.0",
        "schema": SCHEMA,
        "projection_hash": source_manifest["projection_hash"],
        "sql_hash": sha256_text(sql),
        "sql_file": "projection.sql",
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projection")
    ap.add_argument("output")
    args = ap.parse_args()
    manifest = write_bundle(Path(args.projection), Path(args.output))
    print(manifest["sql_hash"])


if __name__ == "__main__":
    main()
