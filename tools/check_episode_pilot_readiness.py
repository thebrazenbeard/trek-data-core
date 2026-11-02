#!/usr/bin/env python3
"""Read-only, conservative first nonfixture Mission Briefing readiness report.

This is a diagnostic for the existing Librarian, coverage and projection gates,
not an admission command. In particular, a green technical check never proves
that copyrighted source material was inspected or that a human accepted it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

import build_explorer_index
import coverage_ledger
import validate

ROOT = Path(__file__).resolve().parents[1]


def mission_for_episode(work_id: str, works: dict, missions: list[dict]) -> str | None:
    """Resolve only an unambiguous accepted series ancestor in the display catalog."""
    title_ids = {row["title"].casefold(): row["id"] for row in missions}
    matches = set()
    seen = {work_id}
    parent = works[work_id].get("parent_work_id")
    while isinstance(parent, str) and parent:
        if parent in seen:
            return None
        seen.add(parent)
        ancestor = works.get(parent)
        if not ancestor or ancestor.get("status") != "ACCEPTED" or ancestor.get("fixture_only") is not False:
            return None
        match = title_ids.get(str(ancestor.get("title", "")).casefold())
        if match:
            matches.add(match)
        parent = ancestor.get("parent_work_id")
    return next(iter(matches)) if len(matches) == 1 else None


def summarize(works: dict, sources: dict, bindings: dict, records: list[dict],
              missions: list[dict], approved_hash_count: int, requested_work_id: str | None = None) -> dict:
    """Count evidence-gated *prerequisites*, never infer episode acceptance from leads."""
    active_successors = {
        row.get("supersedes_binding_id") for row in bindings.values()
        if row.get("lifecycle") == "ACCEPTED" and row.get("supersedes_binding_id")
    }
    accepted_works = {
        wid: row for wid, row in works.items()
        if row.get("status") == "ACCEPTED" and row.get("fixture_only") is False
    }
    evidence_rows = [row for row in records if row.get("record_type") == "evidence" and row.get("fixture_only") is not True]
    assertion_rows = [row for row in records if row.get("record_type") == "assertion" and row.get("status") == "ACCEPTED" and row.get("fixture_only") is not True]
    events = coverage_ledger.index_records(records, "coverage_event", "coverage_event_id")
    events = coverage_ledger.active_events(events)
    index = {"source": sources, "work": works, "source_work_binding": bindings}

    episode_ids = sorted(wid for wid, row in accepted_works.items() if row.get("work_type") == "EPISODE")
    if requested_work_id is not None:
        episode_ids = [wid for wid in episode_ids if wid == requested_work_id]
    episodes = []
    for wid in episode_ids:
        mission_id = mission_for_episode(wid, accepted_works, missions)
        eligible = {}
        for bid, binding in bindings.items():
            source = sources.get(binding.get("source_id")) or {}
            if (bid not in active_successors
                and binding.get("lifecycle") == "ACCEPTED"
                and binding.get("mapping_role") == "EVIDENCE_BEARING"
                and binding.get("fixture_only") is False
                and binding.get("work_id") == wid
                and source.get("status") == "ACCEPTED"
                and source.get("fixture_only") is False
                and coverage_ledger.accepted_source_binding_basis(source, binding)):
                eligible[bid] = binding

        matched_evidence = {}
        for row in evidence_rows:
            if row.get("work_id") != wid:
                continue
            binding = validate.eligible_evidence_binding(row, index)
            if binding and binding.get("binding_id") in eligible:
                matched_evidence[row.get("evidence_id")] = binding
        evidence_ids = {eid for eid in matched_evidence if isinstance(eid, str) and eid}
        asserted = any(
            isinstance(row.get("evidence"), list) and evidence_ids.intersection(row["evidence"])
            for row in assertion_rows
        )
        source_bound = any(
            event.get("status") == "ACCEPTED"
            and event.get("effect") == "ATTAINED"
            and event.get("coverage_state") == "SOURCE_BOUND"
            and event.get("work_id") == wid
            and event.get("binding_id") in eligible
            for event in events.values()
        )
        gates = {
            "unique_catalog_mission_ancestor": mission_id is not None,
            "accepted_byte_hash_source_binding": bool(eligible),
            "binding_grounded_nonfixture_evidence": bool(evidence_ids),
            "accepted_assertion_referencing_evidence": asserted,
            "accepted_source_bound_coverage_event": source_bound,
        }
        episodes.append({
            "work_id": wid,
            "mission_id": mission_id,
            "technical_gates": gates,
            "automated_prerequisites_present": all(gates.values()),
            "human_source_review": "REQUIRED_NOT_MACHINE_VERIFIABLE",
        })

    ready_count = sum(row["automated_prerequisites_present"] for row in episodes)
    return {
        "schema_version": "1.0.0",
        "report_kind": "NONFIXTURE_EPISODE_PILOT_TECHNICAL_PREREQUISITES",
        "overall_status": "HUMAN_REVIEW_REQUIRED" if ready_count else "TECHNICAL_PREREQUISITES_BLOCKED",
        "accepted_nonfixture_episode_works": len(episode_ids),
        "automated_prerequisite_complete_works": ready_count,
        "approved_projection_hash_count": approved_hash_count,
        "complete_mission_denominator": "NOT_ESTABLISHED_BY_THIS_REPORT",
        "rights_and_source_inspection": "REQUIRES_INDEPENDENT_HUMAN_REVIEW",
        "discovery_candidate_rows_counted_as_evidence": 0,
        "episodes": episodes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-id", help="Limit report to one already-accepted episode Work ID")
    parser.add_argument("--require-technical-prerequisites", action="store_true",
                        help="Exit 2 unless at least one episode passes all automated gates")
    args = parser.parse_args()

    # Check all governed records with the existing admission validators first.
    for tool in ("validate.py", "coverage_ledger.py"):
        cmd = [sys.executable, str(ROOT / "tools" / tool)]
        if tool == "coverage_ledger.py":
            cmd.append("validate")
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        if result.returncode:
            print(json.dumps({"schema_version": "1.0.0", "overall_status": "VALIDATION_FAILED",
                              "failed_validator": tool}, sort_keys=True))
            return 3
    try:
        works = coverage_ledger.authoritative_work_roster()
        sources, bindings = coverage_ledger.authoritative_source_binding_rosters()
        records, paths = coverage_ledger.scan_typed_records(with_paths=True)
        errors = coverage_ledger.validate_coverage(records, record_paths=paths, enforce_origins=True)
        if errors:
            raise ValueError("Coverage origin validation failed")
        missions = build_explorer_index.load_missions(ROOT / "registry" / "mission_catalog.json")
        approved = build_explorer_index.approved_hashes(ROOT / "registry" / "approved_projection_hashes.json")
        result = summarize(works, sources, bindings, records, missions, len(approved), args.work_id)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        print(json.dumps({"schema_version": "1.0.0", "overall_status": "READINESS_INPUT_INVALID"}, sort_keys=True))
        return 3
    print(json.dumps(result, sort_keys=True, indent=2))
    if args.require_technical_prerequisites and not result["automated_prerequisite_complete_works"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
