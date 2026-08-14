#!/usr/bin/env python3
"""Build a rebuildable SQLite query database from canonical logical projection JSONL."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

ASSERTION_PARTITIONS = {
    "facts.jsonl": "facts",
    "contested.jsonl": "contested",
    "unresolved.jsonl": "unresolved",
}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


def json_value(value):
    return None if value is None else canonical(value)


def create_schema(con: sqlite3.Connection):
    con.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE entities (
            local_entity_id TEXT PRIMARY KEY,
            work_id TEXT,
            label TEXT,
            resolved_entity_json TEXT,
            reconciliation_decision_id TEXT,
            record_json TEXT NOT NULL
        );

        CREATE TABLE assertions (
            assertion_id TEXT PRIMARY KEY,
            projection_status TEXT NOT NULL,
            partition TEXT NOT NULL CHECK (partition IN ('facts','contested','unresolved')),
            subject TEXT,
            resolved_subject_json TEXT,
            predicate TEXT,
            object_json TEXT,
            scope_json TEXT,
            resolved_scope_json TEXT,
            record_json TEXT NOT NULL
        );

        CREATE TABLE provenance (
            provenance_id TEXT PRIMARY KEY,
            assertion_id TEXT NOT NULL,
            evidence_id TEXT,
            source_id TEXT,
            work_id TEXT,
            evidence_kind TEXT,
            source_content_hash TEXT,
            record_json TEXT NOT NULL,
            FOREIGN KEY (assertion_id) REFERENCES assertions(assertion_id)
        );

        CREATE TABLE reconciliation (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT,
            subject_id TEXT,
            status TEXT,
            supersedes TEXT,
            value_json TEXT,
            record_json TEXT NOT NULL
        );

        CREATE TABLE relations (
            relation_id TEXT PRIMARY KEY,
            record_json TEXT NOT NULL
        );

        CREATE INDEX idx_assertions_status ON assertions(projection_status);
        CREATE INDEX idx_assertions_subject ON assertions(subject);
        CREATE INDEX idx_assertions_predicate ON assertions(predicate);
        CREATE INDEX idx_provenance_assertion ON provenance(assertion_id);
        CREATE INDEX idx_provenance_source ON provenance(source_id);
        CREATE INDEX idx_reconciliation_subject ON reconciliation(subject_id);
        """
    )


def build_database(projection_root: Path, database_path: Path):
    projection_root = Path(projection_root)
    database_path = Path(database_path)
    manifest = json.loads((projection_root / "manifest.json").read_text(encoding="utf-8"))
    projection_hash = manifest.get("projection_hash")
    if not projection_hash:
        raise ValueError("projection manifest missing projection_hash")

    if database_path.exists():
        database_path.unlink()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(database_path)
    try:
        create_schema(con)

        metadata_keys = (
            "projection_hash",
            "input_hash",
            "projection_version",
            "schema_version",
            "methodology_version",
            "research_head",
            "reconciliation_head",
            "predicate_registry_hash",
            "compiler_commit",
        )
        for key in metadata_keys:
            if key in manifest and manifest[key] is not None:
                con.execute("INSERT INTO metadata(key,value) VALUES (?,?)", (key, str(manifest[key])))

        for row in sorted(load_rows(projection_root / "entities.jsonl"), key=lambda item: item.get("local_entity_id", "")):
            con.execute(
                """INSERT INTO entities(
                    local_entity_id,work_id,label,resolved_entity_json,reconciliation_decision_id,record_json
                ) VALUES (?,?,?,?,?,?)""",
                (
                    row.get("local_entity_id"), row.get("work_id"), row.get("label"),
                    json_value(row.get("resolved_entity")), row.get("reconciliation_decision_id"), canonical(row),
                ),
            )

        seen_assertions = set()
        for filename, partition in ASSERTION_PARTITIONS.items():
            for row in sorted(load_rows(projection_root / filename), key=lambda item: item.get("assertion_id", "")):
                assertion_id = row.get("assertion_id")
                if assertion_id in seen_assertions:
                    raise ValueError(f"assertion {assertion_id} appears in multiple projection partitions")
                seen_assertions.add(assertion_id)
                con.execute(
                    """INSERT INTO assertions(
                        assertion_id,projection_status,partition,subject,resolved_subject_json,predicate,
                        object_json,scope_json,resolved_scope_json,record_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (
                        assertion_id, row.get("projection_status"), partition, row.get("subject"),
                        json_value(row.get("resolved_subject")), row.get("predicate"), json_value(row.get("object")),
                        json_value(row.get("scope")), json_value(row.get("resolved_scope")), canonical(row),
                    ),
                )

        for row in sorted(load_rows(projection_root / "provenance.jsonl"), key=lambda item: item.get("provenance_id", "")):
            con.execute(
                """INSERT INTO provenance(
                    provenance_id,assertion_id,evidence_id,source_id,work_id,evidence_kind,source_content_hash,record_json
                ) VALUES (?,?,?,?,?,?,?,?)""",
                (
                    row.get("provenance_id"), row.get("assertion_id"), row.get("evidence_id"), row.get("source_id"),
                    row.get("work_id"), row.get("evidence_kind"), row.get("source_content_hash"), canonical(row),
                ),
            )

        for row in sorted(load_rows(projection_root / "accepted_reconciliation.jsonl"), key=lambda item: item.get("decision_id", "")):
            con.execute(
                """INSERT INTO reconciliation(
                    decision_id,decision_type,subject_id,status,supersedes,value_json,record_json
                ) VALUES (?,?,?,?,?,?,?)""",
                (
                    row.get("decision_id"), row.get("decision_type"), row.get("subject_id"), row.get("status"),
                    row.get("supersedes"), json_value(row.get("value")), canonical(row),
                ),
            )

        for row in sorted(load_rows(projection_root / "relations.jsonl"), key=lambda item: item.get("relation_id", "")):
            relation_id = row.get("relation_id")
            if not relation_id:
                raise ValueError("relation row missing relation_id")
            con.execute("INSERT INTO relations(relation_id,record_json) VALUES (?,?)", (relation_id, canonical(row)))

        con.commit()
    except Exception:
        con.rollback()
        con.close()
        if database_path.exists():
            database_path.unlink()
        raise
    finally:
        if con:
            try:
                con.close()
            except sqlite3.Error:
                pass
    return projection_hash


def query_snapshot(database_path: Path):
    """Return deterministic query content; raw SQLite bytes are intentionally irrelevant."""
    with sqlite3.connect(database_path) as con:
        metadata = dict(con.execute("SELECT key,value FROM metadata ORDER BY key").fetchall())
        return {
            "projection_hash": metadata.get("projection_hash"),
            "metadata": sorted(metadata.items()),
            "entities": con.execute("SELECT local_entity_id,work_id,label,resolved_entity_json,reconciliation_decision_id,record_json FROM entities ORDER BY local_entity_id").fetchall(),
            "assertions": con.execute("SELECT assertion_id,projection_status,partition,subject,resolved_subject_json,predicate,object_json,scope_json,resolved_scope_json,record_json FROM assertions ORDER BY assertion_id").fetchall(),
            "provenance": con.execute("SELECT provenance_id,assertion_id,evidence_id,source_id,work_id,evidence_kind,source_content_hash,record_json FROM provenance ORDER BY provenance_id").fetchall(),
            "reconciliation": con.execute("SELECT decision_id,decision_type,subject_id,status,supersedes,value_json,record_json FROM reconciliation ORDER BY decision_id").fetchall(),
            "relations": con.execute("SELECT relation_id,record_json FROM relations ORDER BY relation_id").fetchall(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projection")
    ap.add_argument("database")
    args = ap.parse_args()
    projection_hash = build_database(Path(args.projection), Path(args.database))
    print(projection_hash)


if __name__ == "__main__":
    main()
