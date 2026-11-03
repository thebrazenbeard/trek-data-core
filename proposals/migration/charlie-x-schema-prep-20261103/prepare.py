#!/usr/bin/env python3
"""Read-only, proposal-only schema-shape preview for the legacy Charlie X packet.

NEVER writes research/, registry/, a coverage event, or a binding. Candidate IDs
below are explicitly local to an *unadmitted* migration preview.
"""

from __future__ import annotations

import hashlib
import contextlib
import io
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / "proposals/research/tos-charlie-x-derivative-close-read-20261103"
PREVIEW_TYPE = "CHARLIE_X_SCHEMA_SHAPE_PREVIEW_V1_NOT_ADMITTED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(name: str) -> dict:
    return json.loads((LEGACY / name).read_text(encoding="utf-8"))


def prepare() -> dict:
    manifest = load("MANIFEST.json")
    # The original proposal validator pins the source identity and guards the
    # complete legacy packet, including flags this adapter does not interpret.
    # Invoke it on the immutable on-disk packet before making any preview.
    original = runpy.run_path(str(LEGACY / "validate.py"))
    with contextlib.redirect_stdout(io.StringIO()):
        original["validate"]()
    # A caller may supply an in-memory manifest (e.g. to test a potential
    # migration). Check that against the original validator's pinned identity
    # too: file SHA-256s do not pin fields stored in MANIFEST.json itself.
    for field, expected in original["SOURCE_IDENTITY"].items():
        require(manifest["source"].get(field) == expected,
                f"legacy source identity drift: {field}")
    for field, expected in original["MANIFEST_IDENTITY"].items():
        require(manifest.get(field) == expected,
                f"legacy manifest identity drift: {field}")
    # The derivative transcript's lineage and the candidate Work description
    # are part of the source-relative identity envelope, too. Validating only
    # the on-disk copy would miss a caller's in-memory substitution.
    for field, expected in original["WORK_IDENTITY"].items():
        require(manifest["work"].get(field) == expected,
                f"legacy work identity drift: {field}")
    require(manifest["source"].get("upstream_self_report") ==
            original["UPSTREAM_SELF_REPORT"], "legacy upstream provenance drift")
    require(set(manifest) == original["MANIFEST_FIELDS"],
            "unexpected manifest fields")
    require(set(manifest["source"]) == original["SOURCE_FIELDS"],
            "unexpected source fields")
    require(set(manifest["work"]) == original["WORK_FIELDS"],
            "unexpected work fields")
    for name, digest in manifest["files_sha256"].items():
        actual = hashlib.sha256((LEGACY / name).read_bytes()).hexdigest()
        require(actual == digest, f"legacy source file changed: {name}")

    source = manifest["source"]
    require(manifest["admission"] == "PROPOSAL_ONLY", "unexpected admission")
    require(manifest["status"] == "COMPLETE_AVAILABLE_DERIVATIVE_READING_NOT_ADMITTED", "unexpected coverage")
    require(source["private_source_custody"] == "TEMPORARY_LOCAL_ONLY_NO_DURABLE_AUTHENTICATED_ARTIFACT", "source custody status changed")
    require(source["authenticated_primary_av_or_studio_script"] is False, "primary source verification changed")
    require(manifest["records"]["coverage_events"] == 0, "accepted coverage changed")
    require(manifest["records"]["global_identity_reconciliations"] == 0, "identity reconciliation changed")
    require(manifest["records"]["accepted_briefings"] == 0, "admitted briefings changed")

    local = load("local_entities.json")
    evidence = load("evidence.json")
    assertions = load("assertions.json")
    candidate_work = manifest["work"]["candidate_id"]
    candidate_source = source["source_local_id"]
    for section in (local, evidence, assertions):
        require(section["source_local_id"] == candidate_source, "source mismatch")
        require(section["work_local_id"] == candidate_work, "work mismatch")
    require(local["global_identity_edges_created"] == 0, "nonlocal identity edges")
    require(assertions["accepted_assertions"] == 0, "accepted assertions")

    ids = [r["id"] for r in local["entities"]]
    ev_ids = [r["id"] for r in evidence["evidence"]]
    as_ids = [r["id"] for r in assertions["assertions"]]
    for label, values in (("entity", ids), ("evidence", ev_ids), ("assertion", as_ids)):
        require(len(values) == len(set(values)), f"duplicate {label} IDs")
    require((len(ids), len(ev_ids), len(as_ids)) == (20, 14, 7), "legacy cardinality changed")
    require(manifest["records"]["local_entities"] == len(ids), "manifest entity count")
    require(manifest["records"]["source_relative_evidence"] == len(ev_ids), "manifest evidence count")
    require(manifest["records"]["proposed_assertions"] == len(as_ids), "manifest assertion count")

    # Preserve legacy kind verbatim: the controlled evidence_kind enum is not a
    # lossless mapping from its named dialogue windows, so use 'other'.
    entities_out = [{
        "record_type": "local_entity",
        "local_entity_id": row["id"],
        "work_id": candidate_work,
        "label": row["label"],
        "entity_kind": row["kind"],
        "notes": row.get("notes"),
        "candidate_source_id": candidate_source,
    } for row in local["entities"]]

    evidence_out = []
    for row in evidence["evidence"]:
        require(1 <= row["start_line"] <= row["end_line"] <= source["rendered_text_numbered_lines"], "out of range text locator")
        require(set(row["local_entity_ids"]) <= set(ids), "orphan evidence entity reference")
        evidence_out.append({
            "record_type": "evidence",
            "evidence_id": row["id"],
            "source_id": candidate_source,
            "work_id": candidate_work,
            "evidence_kind": "other",
            "legacy_evidence_kind": row["kind"],
            "locator": {
                "system": "TVMEG_DERIVATIVE_RENDERED_TEXT_LINES",
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "rendered_text_sha256": source["rendered_text_sha256"],
            },
            "observed": {
                "source_relative_summary": row["observation"],
                "local_entity_ids": row["local_entity_ids"],
                "observation_is_source_relative": True,
            },
            "frame": "DERIVATIVE_TRANSCRIPT_ONLY_NOT_AUTHENTICATED_AV",
            "epistemic_status": "UNKNOWN",
        })

    assertions_out = []
    for row in assertions["assertions"]:
        require(row["status"] == "PROPOSED", "legacy assertion promoted")
        require(set(row["evidence"]) <= set(ev_ids) and row["evidence"], "orphan assertion evidence")
        for field in ("context_evidence_ids", "counter_evidence_ids"):
            require(set(row[field]) <= set(ev_ids), f"orphan {field}")
        if row["subject_type"] == "WORK":
            require(row["subject"] == candidate_work, "unexpected work subject")
        elif row["subject_type"] == "LOCAL_ENTITY":
            require(row["subject"] in ids, "orphan assertion subject")
        else:
            raise ValueError("unexpected assertion subject type")
        assertions_out.append({
            "record_type": "assertion",
            "assertion_id": row["id"],
            "subject_type": row["subject_type"],
            "subject": row["subject"],
            "predicate": row["predicate"],
            "object": row["object"],
            "evidence": row["evidence"],
            "status": "PROPOSED",
            "scope": row["scope"],
            "proposed_projection_status": row["proposed_projection_status"],
            "context_evidence_ids": row["context_evidence_ids"],
            "counter_evidence_ids": row["counter_evidence_ids"],
            "counter_evidence_search": row["counter_evidence_search"],
            "falsifier": row["falsifier"],
        })

    return {
        "preview_type": PREVIEW_TYPE,
        "admission_status": "NOT_ADMITTED",
        "source_custody": source["private_source_custody"],
        "candidate_work_id": candidate_work,
        "candidate_source_id": candidate_source,
        "canonical_work_id": None,
        "canonical_source_id": None,
        "accepted_coverage_events": 0,
        "local_entities": entities_out,
        "evidence": evidence_out,
        "assertions": assertions_out,
    }


if __name__ == "__main__":
    preview = prepare()
    print(json.dumps({
        "preview_type": preview["preview_type"],
        "admission_status": preview["admission_status"],
        "counts": {key: len(preview[key]) for key in ("local_entities", "evidence", "assertions")},
        "source_custody": preview["source_custody"],
        "canonical_source_id": preview["canonical_source_id"],
        "canonical_work_id": preview["canonical_work_id"],
    }, indent=2, sort_keys=True))

