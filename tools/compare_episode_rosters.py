#!/usr/bin/env python3
"""Compare two unadmitted publisher episode rosters without resolving identity.

The comparison is of *source-local listings*, not episode truth, episode content,
accepted Works, completeness, or independent corroboration. No files are written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

from validate_publisher_episode_roster import CATALOG, Rejected, read_json, validate


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: object) -> str:
    """A local proposal identity checksum, not a source-response checksum."""
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def title_key(title: str) -> str:
    """Conservative comparison: case/spacing equivalence, no semantic aliases."""
    return " ".join(unicodedata.normalize("NFKC", title).casefold().split())


def source_descriptor(roster: dict) -> dict:
    observation = roster["observation"]
    return {
        "batch_id": roster["batch_id"],
        "publisher": observation["publisher"],
        "independence_group": observation["independence_group"],
        "observed_on": observation["observed_on"],
        "primary_locator": observation["primary_locator"],
        "proposal_sha256": digest(roster),
    }


def position(row: dict) -> dict:
    return {"season": row["season"], "episode_number": row["episode_number"]}


def compare(left: dict, right: dict, catalog: dict) -> dict:
    """Validate both inputs before comparing; never infer canonical episode IDs."""
    validate(left, catalog)
    validate(right, catalog)
    if left["mission_id"] != right["mission_id"]:
        raise Rejected("cannot compare rosters for different Missions")
    if (left["batch_id"] == right["batch_id"]
            or left["observation"]["primary_locator"] == right["observation"]["primary_locator"]):
        raise Rejected("comparison requires distinct source-local roster observations")

    left_index = {title_key(row["title"]): row for row in left["episode_slots"]}
    right_index = {title_key(row["title"]): row for row in right["episode_slots"]}
    # The primary validator rejects exact-casefold duplicates. NFKC may fold
    # additional lookalikes, which are ambiguous and must also fail closed.
    if len(left_index) != len(left["episode_slots"]) or len(right_index) != len(right["episode_slots"]):
        raise Rejected("normalized title collision requires manual identity review")

    shared = []
    left_only = []
    right_only = []
    for key in sorted(set(left_index) | set(right_index)):
        a, b = left_index.get(key), right_index.get(key)
        if a and b:
            equal_position = position(a) == position(b)
            shared.append({
                "left_title": a["title"], "right_title": b["title"],
                "left_slot": position(a), "right_slot": position(b),
                "classification": "SAME_SOURCE_LOCAL_SLOT" if equal_position else "SOURCE_LOCAL_SLOT_CONFLICT",
                "work_identity": "UNRESOLVED",
            })
        elif a:
            left_only.append({"title": a["title"], "left_slot": position(a),
                              "classification": "LISTED_ONLY_IN_LEFT_SAMPLE", "work_identity": "UNRESOLVED"})
        else:
            right_only.append({"title": b["title"], "right_slot": position(b),
                               "classification": "LISTED_ONLY_IN_RIGHT_SAMPLE", "work_identity": "UNRESOLVED"})

    same_family = left["observation"]["independence_group"] == right["observation"]["independence_group"]
    report = {
        "record_type": "publisher_episode_roster_comparison",
        "schema_version": "1.0.0",
        "mission_id": left["mission_id"],
        "comparison_status": "UNRESOLVED_SOURCE_LOCAL_LISTINGS",
        "source_a": source_descriptor(left),
        "source_b": source_descriptor(right),
        "same_independence_group": same_family,
        "independent_corroboration_effect": "NONE",
        "roster_completeness": "UNRESOLVED",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "shared_title_candidates": shared,
        "left_only_sample_candidates": left_only,
        "right_only_sample_candidates": right_only,
        "counts": {
            "shared_title_candidates": len(shared),
            "matching_source_local_slots": sum(item["classification"] == "SAME_SOURCE_LOCAL_SLOT" for item in shared),
            "conflicting_source_local_slots": sum(item["classification"] == "SOURCE_LOCAL_SLOT_CONFLICT" for item in shared),
            "left_only_sample_candidates": len(left_only),
            "right_only_sample_candidates": len(right_only),
        },
        "notes": [
            "Titles are candidate string matches only; no canonical Work identity is assigned.",
            "A title absent from a bounded sample is not evidence that its episode does not exist.",
            "Streaming-provider season/episode slots, original broadcast order, and pilot/production order are distinct.",
            "Matching provider positions do not prove broadcast order, production order or episode completeness.",
            "Source-family identity is declared metadata, not independently audited corroboration.",
        ],
    }
    report["comparison_sha256"] = digest(report)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", required=True, type=Path, help="First publisher candidate JSON")
    parser.add_argument("--right", required=True, type=Path, help="Second publisher candidate JSON")
    args = parser.parse_args(argv)
    try:
        report = compare(read_json(args.left), read_json(args.right), read_json(CATALOG))
    except (Rejected, OSError, ValueError) as exc:
        print(f"ROSTER_COMPARISON_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
