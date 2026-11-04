#!/usr/bin/env python3
"""Read-only Librarian eligibility audit for the held TNG metadata pilot.

This is deliberately narrower than canonical admission validation. It answers
whether one *proposal* has even the source/identity prerequisites for a
nonfixture episode binding. It cannot certify independent inspection or rights.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "proposals/librarian/tng-official-metadata-20261102/bundle.json"
TARGET = "proposal:tng:work:neutral-zone:20261102"
EXPECTED_BUNDLE_SHA256 = "622f25232a4bb8dc9c11a21ebff56fbf87240c20523047ac26c569af2449ce12"
EXPECTED_LINK = (
    "proposal:tng:source:neutral-zone:20261102",
    "proposal:tng:binding:neutral-zone:20261102",
    "https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone",
)


class RouteAuditError(ValueError):
    """Invalid or ambiguously identified proposal input."""


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RouteAuditError("duplicate JSON object key")
        result[key] = value
    return result


def read_bundle(path: Path = PILOT) -> tuple[dict, str]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    # The exact accepted proposal bytes are part of this particular review.
    if digest != EXPECTED_BUNDLE_SHA256:
        raise RouteAuditError("reviewed pilot bytes changed; requalify source route")
    try:
        parsed = json.loads(data, object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RouteAuditError("invalid JSON proposal") from exc
    if not isinstance(parsed, dict):
        raise RouteAuditError("proposal root must be an object")
    return parsed, digest


def indexed(rows, kind: str, key: str) -> dict:
    if not isinstance(rows, list) or not rows:
        raise RouteAuditError(f"missing {kind} records")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("record_type") != kind:
            raise RouteAuditError(f"malformed {kind} record")
        identity = row.get(key)
        if not isinstance(identity, str) or not identity or identity in result:
            raise RouteAuditError(f"missing or duplicate {kind} identity")
        result[identity] = row
    return result


def analyze(bundle: dict, input_sha256: str) -> dict:
    sources = indexed(bundle.get("sources"), "source", "source_id")
    works = indexed(bundle.get("works"), "work", "work_id")
    bindings = indexed(bundle.get("bindings"), "source_work_binding", "binding_id")
    if bundle.get("proposal_status") != "PROPOSAL_ONLY_NOT_ADMITTED":
        raise RouteAuditError("input is not the reviewed proposal-only pilot")
    if TARGET not in works or not isinstance(bundle.get("batch_id"), str):
        raise RouteAuditError("missing reviewed episode candidate")
    matches = [b for b in bindings.values() if b.get("work_id") == TARGET]
    if len(matches) != 1:
        raise RouteAuditError("episode has missing or ambiguous Source-Work association")
    binding = matches[0]
    source = sources.get(binding.get("source_id"))
    if source is None:
        raise RouteAuditError("binding points to missing Source")
    work = works[TARGET]
    if (source.get("source_id"), binding.get("binding_id"), source.get("locator")) != EXPECTED_LINK:
        raise RouteAuditError("reviewed Source/Work/page identity tuple changed")
    if work.get("title") != "The Neutral Zone" or work.get("work_type") != "EPISODE":
        raise RouteAuditError("reviewed episode identity changed")
    if source.get("provenance_family") != "publisher:startrek.com:official-pages":
        raise RouteAuditError("source lineage has changed")
    if source.get("independence_group") != "publisher:startrek.com":
        raise RouteAuditError("unreviewed independence-group claim")

    digest = source.get("content_hash")
    exact_hash = isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None
    basis = binding.get("basis")
    linked_byte_hash = (
        exact_hash and isinstance(basis, list) and
        any(isinstance(row, dict) and row.get("kind") == "BYTE_HASH"
            and row.get("value") == digest for row in basis)
    )
    checks = {
        "accepted_nonfixture_episode_work": work.get("status") == "ACCEPTED" and work.get("fixture_only") is False,
        "accepted_parent_series_work_declared": isinstance(work.get("parent_work_id"), str) and bool(work["parent_work_id"]),
        "accepted_nonfixture_source": source.get("status") == "ACCEPTED" and source.get("fixture_only") is False,
        "accepted_evidence_bearing_binding": binding.get("lifecycle") == "ACCEPTED" and binding.get("mapping_role") == "EVIDENCE_BEARING" and binding.get("fixture_only") is False,
        "source_representation_beyond_metadata": source.get("source_variant") not in {"WEB_METADATA_ONLY", None} and not str(source.get("source_kind", "")).endswith("_METADATA"),
        "exact_source_byte_sha256_declared": exact_hash,
        "binding_basis_matches_source_bytes": linked_byte_hash,
    }
    # Even a completely green structural report cannot establish an actual
    # full-episode read, lawful custody, edition identity, or independent review.
    return {
        "schema_version": "1.0.0",
        "report_kind": "LIBRARIAN_HELD_SOURCE_ROUTE_ELIGIBILITY",
        "status": "STRUCTURAL_ROUTE_BLOCKED" if not all(checks.values()) else "STRUCTURAL_ROUTE_REVIEW_REQUIRED",
        "accepted_effect": "NONE",
        "coverage_effect": "NONE",
        "input_proposal_sha256": input_sha256,
        "reviewed_batch": bundle["batch_id"],
        "candidate_work_id": TARGET,
        "candidate_source_id": source["source_id"],
        "candidate_binding_id": binding["binding_id"],
        "source_locator": source["locator"],
        "source_independence_group": source["independence_group"],
        "source_variant": source.get("source_variant"),
        "observed_publisher_slot": "S1E26",
        "technical_checks": checks,
        "independent_audiovisual_bytes_inspected": "NOT_ESTABLISHED",
        "rights_valid_full_episode_custody": "NOT_ESTABLISHED",
        "independent_work_identity_adjudication": "NOT_ESTABLISHED",
        "accepted_authoritative_registry_entry": "NOT_ESTABLISHED_BY_PROPOSAL",
        "corroboration_warning": "One publisher-family metadata observation, not a full-episode witness",
    }


def main() -> int:
    try:
        bundle, digest = read_bundle()
        report = analyze(bundle, digest)
    except (OSError, RouteAuditError) as exc:
        print(json.dumps({"status": "INPUT_REVIEW_INVALID", "error": str(exc)}, sort_keys=True))
        return 3
    print(json.dumps(report, sort_keys=True, indent=2))
    return 2 if report["status"] == "STRUCTURAL_ROUTE_BLOCKED" else 0


if __name__ == "__main__":
    sys.exit(main())
