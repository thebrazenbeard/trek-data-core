#!/usr/bin/env python3
"""Deterministically project source-attributed short-form/audio discovery proposals.

Publisher titles and slots are observations, not authenticated source bodies,
accepted Work records, episode coverage denominators or continuity facts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
INPUT = Path("proposals/discovery/shorts-audio-20261102/bundle.json")
OUTPUT = Path("proposals/discovery/shorts-audio-20261102/records.json")

SOURCE_SCOPE = {
    "short-guide": ("OFFICIAL_EPISODE_GUIDE", "https://www.paramountplus.com/shows/star-trek-short-treks/episodes/"),
    "very-short-announcement": ("OFFICIAL_PROMOTIONAL_ANNOUNCEMENT", "https://www.startrek.com/en-un/news/star-trek-very-short-treks-announce"),
    "khan-audio-site": ("OFFICIAL_AUDIO_SERIES_PAGE", "https://www.startrek.com/en-un/podcasts/star-trek-khan"),
}

CONTAINERS = {
    "short-treks": ("AUDIOVISUAL", "SCRIPTED_SHORT_ANTHOLOGY", "short-guide"),
    "very-short-treks": ("PROMOTIONAL_ANIMATION", "PROMOTIONAL_SHORT_SERIES", "very-short-announcement"),
    "khan-audio": ("SCRIPTED_AUDIO", "SCRIPTED_AUDIO_SERIES", "khan-audio-site"),
}

ROOT_KEYS = {"schema_version", "proposal_only", "data_status", "admission_effect", "coverage_effect", "universe_complete", "observed_on", "publisher_independence_group", "sources", "containers", "installments"}
SOURCE_KEYS = {"id", "source_type", "url"}
CONTAINER_KEYS = {"candidate_id", "title", "medium", "work_type", "source_id"}
INSTALLMENT_KEYS = {"candidate_id", "parent_candidate_id", "title", "source_local_slot", "source_id"}


def unique_object_keys(pairs: list[tuple[str, object]]) -> dict:
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON object key: {key}")
        output[key] = value
    return output


def no_nonfinite(value: str) -> None:
    raise ValueError(f"non-JSON value: {value}")


def _safe_file(repo: Path, relative: Path) -> Path:
    path = repo / relative
    if repo.is_symlink() or path.is_symlink() or any(part.is_symlink() for part in path.parents):
        raise ValueError(f"symlink source or output path refused: {relative}")
    return path


def read_bundle(root: Path) -> dict:
    path = _safe_file(root, INPUT)
    if not path.is_file() or path.stat().st_size > 64_000:
        raise ValueError("short-form proposal source missing or too large")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object_keys, parse_constant=no_nonfinite)


def _title(value: object) -> bool:
    return isinstance(value, str) and 2 <= len(value) <= 180 and value == value.strip() and all(ord(c) >= 32 for c in value)


def validate(payload: object) -> dict:
    if not isinstance(payload, dict) or set(payload) != ROOT_KEYS:
        raise ValueError("unexpected proposal shape or admission fields")
    for key, expected in (("schema_version", "1.0.0"), ("proposal_only", True), ("data_status", "DISCOVERY_ONLY"),
                          ("admission_effect", "NONE"), ("coverage_effect", "NONE"), ("universe_complete", False),
                          ("publisher_independence_group", "publisher:paramount")):
        if payload[key] != expected or (isinstance(expected, bool) and type(payload[key]) is not bool):
            raise ValueError(f"invalid discovery-only boundary: {key}")
    if not isinstance(payload["observed_on"], str) or not re.fullmatch(r"20\d\d-[01]\d-[0-3]\d", payload["observed_on"]):
        raise ValueError("invalid observation date")
    sources = payload["sources"]
    if not isinstance(sources, list) or len(sources) != len(SOURCE_SCOPE):
        raise ValueError("unexpected publisher source count")
    source_by_id = {}
    for row in sources:
        if not isinstance(row, dict) or set(row) != SOURCE_KEYS or row.get("id") not in SOURCE_SCOPE or row["id"] in source_by_id:
            raise ValueError("unknown or duplicate publisher source")
        expected_type, expected_url = SOURCE_SCOPE[row["id"]]
        parsed = urlsplit(row["url"]) if isinstance(row["url"], str) else None
        if row["source_type"] != expected_type or row["url"] != expected_url or parsed.scheme != "https" or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("publisher source lineage or official URL mismatch")
        source_by_id[row["id"]] = row
    containers = payload["containers"]
    if not isinstance(containers, list) or len(containers) != len(CONTAINERS):
        raise ValueError("unexpected container count")
    container_by_id = {}
    for row in containers:
        if not isinstance(row, dict) or set(row) != CONTAINER_KEYS or row.get("candidate_id") not in CONTAINERS or row["candidate_id"] in container_by_id or not _title(row["title"]):
            raise ValueError("invalid or duplicate container candidate")
        if tuple(row[key] for key in ("medium", "work_type", "source_id")) != CONTAINERS[row["candidate_id"]]:
            raise ValueError("container medium/work identity mismatch")
        container_by_id[row["candidate_id"]] = row
    installments = payload["installments"]
    if not isinstance(installments, list) or len(installments) != 15:
        raise ValueError("expected bounded 15-item short-form discovery tranche")
    seen_ids, seen_slots, seen_titles = set(), set(), set()
    normalized = []
    for row in installments:
        if not isinstance(row, dict) or set(row) != INSTALLMENT_KEYS or not _title(row.get("title")):
            raise ValueError("invalid short-form installment fields")
        parent = row["parent_candidate_id"]
        if parent not in ("short-treks", "very-short-treks"):
            raise ValueError("a scripted audio series has no evidenced episodes in this tranche")
        expected_source = CONTAINERS[parent][2]
        if row["source_id"] != expected_source:
            raise ValueError("installment source/container mismatch")
        match = re.fullmatch(r"short-treks-(\d\d)", row["candidate_id"]) if parent == "short-treks" else re.fullmatch(r"very-short-treks-(\d\d)", row["candidate_id"])
        if not match:
            raise ValueError("malformed source-local short candidate ID")
        sequence = int(match.group(1))
        expected_slot = f"S1E{sequence}" if parent == "short-treks" else f"ANNOUNCED_RELEASE_{sequence:02}"
        if sequence < 1 or sequence > (10 if parent == "short-treks" else 5) or row["source_local_slot"] != expected_slot:
            raise ValueError("short-form source-local slot mismatch")
        ident, slot, title = row["candidate_id"], (parent, row["source_local_slot"]), (parent, row["title"].casefold())
        if ident in seen_ids or slot in seen_slots or title in seen_titles:
            raise ValueError("duplicate short-form ID, slot, or title")
        seen_ids.add(ident); seen_slots.add(slot); seen_titles.add(title)
        normalized.append({
            "candidate_id": ident,
            "parent_candidate_id": parent,
            "title": row["title"],
            "source_local_slot": row["source_local_slot"],
            "slot_meaning": "OFFICIAL_EPISODE_GUIDE" if parent == "short-treks" else "ANNOUNCED_RELEASE_ORDER",
            "source_id": row["source_id"],
            "source_url": source_by_id[row["source_id"]]["url"],
            "verification_status": "UNVERIFIED_METADATA",
        })
    if {row["source_local_slot"] for row in normalized if row["parent_candidate_id"] == "short-treks"} != {f"S1E{i}" for i in range(1, 11)}:
        raise ValueError("publisher episode-guide observations are incomplete within this bounded tranche")
    if {row["source_local_slot"] for row in normalized if row["parent_candidate_id"] == "very-short-treks"} != {f"ANNOUNCED_RELEASE_{i:02}" for i in range(1, 6)}:
        raise ValueError("announced-release order observations are incomplete within this bounded tranche")
    return {
        "schema_version": "1.0.0",
        "data_status": "DISCOVERY_ONLY",
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "universe_complete": False,
        "publisher_independence_group": "publisher:paramount",
        "observed_on": payload["observed_on"],
        "container_count": len(containers),
        "short_candidate_count": len(normalized),
        "sources": sorted(sources, key=lambda row: row["id"]),
        "container_candidates": sorted([{**row, "verification_status": "UNVERIFIED_METADATA"} for row in containers], key=lambda row: row["candidate_id"]),
        "short_candidates": sorted(normalized, key=lambda row: row["candidate_id"]),
    }


def build(root: Path) -> bytes:
    return (json.dumps(validate(read_bundle(root)), sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        blob = build(args.repo_root)
        output = _safe_file(args.repo_root, OUTPUT)
        if args.check:
            if not output.is_file() or output.read_bytes() != blob:
                raise ValueError("short-form discovery projection does not match the source bundle")
        else:
            output.write_bytes(blob)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"short-form discovery builder: {exc}", file=sys.stderr)
        return 1
    print("short-form discovery builder: checked" if args.check else "short-form discovery builder: generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
