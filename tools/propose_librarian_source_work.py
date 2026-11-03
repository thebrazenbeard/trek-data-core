#!/usr/bin/env python3
"""Turn replay-verified private Source bytes into a *proposed* Librarian triad.

The Source digest is observed; the Work identity and its relationship to those
bytes are still operator declarations. No accepted records or coverage events
are written. This deliberately cannot produce an EVIDENCE_BEARING binding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import source_custody_receipt as custody
from validate_librarian_registry import validate_registry


FIELDS = {
    "record_type", "schema_version", "proposal_id", "work_candidate_id",
    "work_title", "work_type", "work_identity_note", "work_identity_reference",
    "fixture_only",
}


def proposed_work(item: dict) -> dict:
    if set(item) != FIELDS or item.get("record_type") != "work_identity_declaration" or item.get("schema_version") != "1.0.0":
        raise custody.Rejected("work identity declaration needs exact v1 fields")
    for key in ("proposal_id", "work_candidate_id"):
        custody.ident(item[key], key)
    for key in ("work_title", "work_type", "work_identity_note"):
        custody.text(item[key], key, length=240)
    if len(item["work_identity_note"]) < 20:
        raise custody.Rejected("work identity note must explain the operator's specific basis")
    if type(item["fixture_only"]) is not bool:
        raise custody.Rejected("fixture_only must be a boolean")
    if item["work_identity_reference"] is not None:
        custody.public_https(item["work_identity_reference"])
    return {
        "record_type": "work", "work_id": item["work_candidate_id"],
        "status": "PROPOSED", "title": item["work_title"],
        "work_type": item["work_type"], "parent_work_id": None,
        "component_label": None, "fixture_only": item["fixture_only"],
        "notes": "OPERATOR_DECLARED_NOT_INDEPENDENTLY_VERIFIED: " + item["work_identity_note"],
    }


def build_proposal(request: dict, receipt: dict, work_declaration: dict, source_file: Path) -> dict:
    """Strictly replay the receipt against current bytes before proposing triad."""
    expected = custody.build_receipt(request, source_file)
    if expected != receipt:
        raise custody.Rejected("receipt does not replay against source request and exact current bytes")
    work = proposed_work(work_declaration)
    source_id = receipt["source_candidate_id"]
    work_id = work["work_id"]
    binding_id = work_declaration["proposal_id"] + "-binding"
    if len(binding_id) > 64 or len({source_id, work_id, binding_id}) != 3:
        raise custody.Rejected("proposed Source, Work and binding identifiers must be unique and bounded")

    source = {
        "record_type": "source", "source_id": source_id, "status": "PROPOSED",
        "source_kind": receipt["source_kind"],
        "provider": "DECLARED_NOT_INDEPENDENTLY_VERIFIED",
        "locator": receipt["source_locator"],
        "provider_metadata": {
            "custody_receipt_id": receipt["receipt_id"],
            "custody_receipt_sha256": receipt["receipt_sha256"],
            "locator_kind": receipt["locator_kind"],
            "edition_identity_declared": receipt["edition_identity"],
            "rights_basis_reported": receipt["rights_basis_reported"],
            "rights_verification": "NOT_PERFORMED",
            "work_identity_verification": "NOT_PERFORMED",
            "source_metadata_verification": "NOT_PERFORMED",
            "work_identity_reference_declared": work_declaration["work_identity_reference"],
            "byte_length": receipt["size_bytes"],
        },
        "source_version": receipt["source_version"],
        "retrieved_at": receipt["observed_on"],
        "content_hash": "sha256:" + receipt["content_sha256"],
        "content_fingerprint": None,
        "source_variant": receipt["edition_identity"],
        "provenance_family": receipt["provenance_family"],
        "independence_group": receipt["independence_group"],
        "derived_from": [], "fixture_only": work_declaration["fixture_only"],
        "notes": "LOCAL_BYTES_HASHED_ONLY; provenance and Work relation are unverified declarations.",
    }
    binding = {
        "record_type": "source_work_binding", "binding_id": binding_id,
        "source_id": source_id, "work_id": work_id, "lifecycle": "PROPOSED",
        "mapping_role": "METADATA_ONLY",
        "source_scope": {"scope_type": "WHOLE", "locator": None},
        "work_scope": {"scope_type": "WHOLE", "component_label": None},
        "method": "local Source byte replay; operator-declared Work association; no content-based identity verification",
        "basis": [{"kind": "BYTE_HASH", "value": source["content_hash"]}],
        "exclusive_scope_key": None, "supersedes_binding_id": None,
        "notes": "BYTE_HASH verifies only captured local Source bytes, not Source-to-Work identity.",
        "fixture_only": work_declaration["fixture_only"],
    }
    errors = validate_registry([source], [work], [binding], [])
    if errors:
        raise custody.Rejected("candidate Librarian schema rejected: " + "; ".join(errors))
    proposal = {
        "record_type": "librarian_source_work_proposal", "schema_version": "1.0.0",
        "proposal_id": work_declaration["proposal_id"],
        "source": source, "work": work, "source_work_binding": binding,
        "custody_state": "LOCAL_BYTES_HASHED_ONLY",
        "source_work_identity_state": "DECLARED_NOT_INDEPENDENTLY_VERIFIED",
        "independent_content_review": "NOT_PERFORMED",
        "rights_verification": "NOT_PERFORMED",
        "accepted_registry_effect": "NONE", "coverage_effect": "NONE",
        "fixture_only": work_declaration["fixture_only"],
        "admission_blockers": [
            "Independent source edition and publisher/lineage verification",
            "Independent content-to-Work identity verification",
            "Rights and source-use review for intended research",
            "Explicit Librarian/Auditor governance before authoritative admission",
        ],
    }
    proposal["proposal_sha256"] = hashlib.sha256(custody.canonical(proposal)).hexdigest()
    return proposal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--source-file", required=True, type=Path)
    parser.add_argument("--work-declaration", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        proposal = build_proposal(custody.read_json(args.request), custody.read_json(args.receipt),
                                  custody.read_json(args.work_declaration), args.source_file)
    except custody.Rejected as exc:
        print(f"LIBRARIAN_PROPOSAL_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(proposal, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
