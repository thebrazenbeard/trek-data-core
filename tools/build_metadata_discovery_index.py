#!/usr/bin/env python3
"""Build an UNADMITTED, read-only publisher episode-metadata discovery proposal.

This is deliberately separate from the authoritative Explorer index and its
admission gates. Publisher slots are source-local, not canonical Work IDs.
Receipt declaration, exact snapshot-byte custody, and authority admission are
three different things. This compiler performs only the first two checks.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

from normalize_episode_roster import read_csv_bytes
from validate_publisher_episode_roster import (
    CATALOG, Rejected, unique_pairs, validate as validate_candidate, read_json,
)
from validate_verified_episode_roster import (
    digest, read_snapshot, validate_review,
)

EFFECTS = {
    "canonical_work": "NONE", "source_binding": "NONE", "continuity": "NONE",
    "coverage": "NONE", "denominator": "NONE", "publication": "NONE",
}


def canonical_bytes(value: dict) -> bytes:
    """Stable UTF-8 JSON output independent of input ordering and host paths."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def load_pair(path: Path) -> tuple[dict, bytes]:
    """Read JSON exactly once through safe bounded no-follow input."""
    raw = read_csv_bytes(path)
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Rejected(f"invalid UTF-8 JSON at {path.name}: {exc}") from exc
    return value, raw


def _observation(row: dict) -> dict:
    """For a public comparison, never imply that sources are independent."""
    return {
        "source_locator": row["source_locator"],
        "independence_group": row["independence_group"],
        "candidate_sha256": row["candidate_sha256"],
        "title": row["title"],
        "season": row["season"],
        "episode_number": row["episode_number"],
    }


def _comparison_keys(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Report cross-source contradictions; never reconcile or select a winner."""
    by_slot: dict[tuple, list[dict]] = defaultdict(list)
    by_title: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        by_slot[(row["mission_id"], row["season"], row["episode_number"])].append(row)
        by_title[(row["mission_id"], row["title"].casefold())].append(row)

    slot_disagreements = []
    for (mission, season, episode), observed in sorted(by_slot.items()):
        if len({row["title"].casefold() for row in observed}) > 1:
            slot_disagreements.append({
                "mission_id": mission, "season": season, "episode_number": episode,
                "status": "UNRESOLVED_CROSS_SOURCE_SLOT_DISAGREEMENT",
                "observations": sorted((_observation(row) for row in observed),
                                       key=lambda row: (row["source_locator"], row["candidate_sha256"])),
            })

    title_disagreements = []
    for (mission, _title_key), observed in sorted(by_title.items()):
        if len({(row["season"], row["episode_number"]) for row in observed}) > 1:
            title_disagreements.append({
                "mission_id": mission,
                "title": sorted(row["title"] for row in observed)[0],
                "status": "UNRESOLVED_CROSS_SOURCE_TITLE_POSITION_DISAGREEMENT",
                "observations": sorted((_observation(row) for row in observed),
                                       key=lambda row: (row["source_locator"], row["candidate_sha256"])),
            })
    return slot_disagreements, title_disagreements


def build_projection(candidate_paths: list[Path], review_paths: list[Path] | None = None,
                     snapshot_paths: dict[Path, Path] | None = None) -> dict:
    """Validate every input and emit only source-local, non-admitted discoveries.

    `snapshot_paths` is keyed by receipt path, never by episode or proposed
    canonical identity. The returned JSON contains no private snapshot bytes.
    """
    if not candidate_paths:
        raise Rejected("at least one candidate proposal is required")
    review_paths = review_paths or []
    snapshot_paths = snapshot_paths or {}
    if any(path not in review_paths for path in snapshot_paths):
        raise Rejected("private snapshot supplied for an unknown review receipt")
    catalog = read_json(CATALOG)
    candidates: dict[str, tuple[dict, bytes]] = {}
    slot_origins: set[tuple] = set()
    for path in candidate_paths:
        data, raw = load_pair(path)
        validate_candidate(data, catalog)
        observation = data["observation"]
        # One source-local ordinal must have one observation in this build.
        # Different publisher pages may disagree without overwriting either.
        for row in data["episode_slots"]:
            source_local = (
                data["mission_id"], observation["independence_group"],
                observation["primary_locator"], row["season"], row["episode_number"],
            )
            if source_local in slot_origins:
                raise Rejected("duplicate source-local slot across candidate proposals")
            slot_origins.add(source_local)
        sha = digest(raw)
        if sha in candidates:
            raise Rejected("duplicate candidate proposal byte digest")
        candidates[sha] = (data, raw)

    reviews: dict[str, tuple[dict, str, str]] = {}
    for path in review_paths:
        review, review_raw = load_pair(path)
        candidate_sha = review.get("candidate_sha256") if isinstance(review, dict) else None
        if not isinstance(candidate_sha, str) or candidate_sha not in candidates:
            raise Rejected("review receipt has no input candidate with exact byte digest")
        if candidate_sha in reviews:
            raise Rejected("duplicate review receipts for one candidate proposal")
        candidate, raw = candidates[candidate_sha]
        snapshot_raw = read_snapshot(snapshot_paths[path]) if path in snapshot_paths else None
        report = validate_review(candidate, raw, review, catalog, snapshot_raw)
        reviews[candidate_sha] = (review, digest(review_raw), report["review_receipt_status"])

    rows = []
    inputs = []
    for sha, (candidate, _raw) in candidates.items():
        observation = candidate["observation"]
        reviewed = reviews.get(sha)
        checked = set()
        if reviewed:
            checked = {(entry["season"], entry["episode_number"])
                       for entry in reviewed[0]["review"]["checked_episode_slots"]}
        inputs.append({
            "mission_id": candidate["mission_id"], "candidate_batch_id": candidate["batch_id"],
            "candidate_sha256": sha, "publisher": observation["publisher"],
            "independence_group": observation["independence_group"],
            "source_locator": observation["primary_locator"],
            "observation_status": "UNADMITTED_CANDIDATE",
            "receipt_sha256": reviewed[1] if reviewed else None,
            "receipt_status": reviewed[2] if reviewed else "NO_REVIEW_RECEIPT",
        })
        for row in candidate["episode_slots"]:
            has_receipt = (row["season"], row["episode_number"]) in checked
            rows.append({
                "record_type": "publisher_episode_slot_discovery",
                "mission_id": candidate["mission_id"],
                "candidate_batch_id": candidate["batch_id"],
                "candidate_sha256": sha,
                "publisher": observation["publisher"],
                "independence_group": observation["independence_group"],
                "source_locator": observation["primary_locator"],
                "observed_on": observation["observed_on"],
                "season": row["season"], "episode_number": row["episode_number"],
                "title": row["title"],
                "candidate_status": "CANDIDATE_METADATA_ONLY",
                "receipt_sha256": reviewed[1] if has_receipt else None,
                "receipt_status": reviewed[2] if has_receipt else "NO_REVIEW_RECEIPT",
            })
    rows.sort(key=lambda row: (row["mission_id"], row["independence_group"],
                               row["source_locator"], row["season"],
                               row["episode_number"], row["candidate_sha256"]))
    inputs.sort(key=lambda row: (row["mission_id"], row["source_locator"],
                                 row["candidate_sha256"]))
    slots, titles = _comparison_keys(rows)
    result = {
        "record_type": "unadmitted_episode_metadata_discovery_projection",
        "schema_version": "1.0.0",
        "admission_status": "NOT_ADMITTED",
        "source_inspection_status": "AUDIOVISUAL_CONTENT_NOT_INSPECTED",
        "roster_completeness": "UNRESOLVED",
        "identity_reconciliation": "NOT_PERFORMED",
        "effects": EFFECTS.copy(),
        "inputs": inputs,
        "records": rows,
        "source_local_slot_disagreements": slots,
        "title_position_disagreements": titles,
    }
    result["projection_sha256"] = digest(canonical_bytes(result))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, action="append", required=True,
                        help="One unadmitted publisher candidate bundle; repeat for more sources")
    parser.add_argument("--review", type=Path, action="append", default=[],
                        help="Optional proposed review receipt linked by exact candidate byte hash")
    parser.add_argument("--snapshot-for-review", type=Path, nargs=2, action="append", default=[],
                        metavar=("REVIEW", "PRIVATE_SNAPSHOT"),
                        help="Optional exact publisher snapshot for one receipt; never emitted")
    args = parser.parse_args(argv)
    try:
        snapshots: dict[Path, Path] = {}
        for review, snapshot in args.snapshot_for_review:
            if review in snapshots:
                raise Rejected("duplicate private snapshot assignment")
            snapshots[review] = snapshot
        result = build_projection(args.candidate, args.review, snapshots)
    except (Rejected, ValueError, OSError, RecursionError) as exc:
        print(f"METADATA_DISCOVERY_REJECTED: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(canonical_bytes(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
