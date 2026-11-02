#!/usr/bin/env python3
"""Convert a bounded offline publisher CSV into an unadmitted episode proposal.

The publisher URL and supplied CSV are operator observations, not independently
verified source evidence. This never creates canonical Works or changes coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import stat
import sys
from pathlib import Path

from validate_publisher_episode_roster import (
    CATALOG,
    Rejected,
    read_json,
    validate,
)


MAX_CSV_BYTES = 128 * 1024
MAX_ROWS = 500
NUMBER = re.compile(r"[1-9][0-9]{0,3}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CSV_HEADER = ["season", "episode_number", "title"]
RECEIPT_KEYS = {
    "batch_id", "mission_id", "publisher", "independence_group", "observed_on",
    "primary_locator", "crosscheck_locator", "csv_sha256",
}


def read_csv_bytes(path: Path) -> bytes:
    """Reject links, special files and oversized reads, including a stat/open race."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise Rejected("safe no-follow/nonblocking input flags are unavailable")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise Rejected("CSV must be a regular non-symlink file")
    if before.st_size > MAX_CSV_BYTES:
        raise Rejected("CSV exceeds 128 KiB")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino):
            raise Rejected("CSV changed during safe open")
        raw = stream.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise Rejected("CSV exceeds 128 KiB")
    return raw


def parse_rows(raw: bytes) -> list[dict]:
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Rejected("CSV must be UTF-8") from exc
    try:
        rows = csv.reader(io.StringIO(content, newline=""), strict=True)
        if next(rows, None) != CSV_HEADER:
            raise Rejected("CSV header must be exactly season,episode_number,title")
        normalized = []
        for index, row in enumerate(rows, 2):
            if len(normalized) >= MAX_ROWS:
                raise Rejected("CSV exceeds 500 episode slots")
            if len(row) != 3 or not NUMBER.fullmatch(row[0]) or not NUMBER.fullmatch(row[1]):
                raise Rejected(f"CSV row {index} has invalid season/episode fields")
            normalized.append({
                "season": int(row[0]),
                "episode_number": int(row[1]),
                "title": row[2],
                "status": "CANDIDATE",
                "canonical_work_id": None,
                "source_binding_id": None,
            })
    except csv.Error as exc:
        raise Rejected(f"malformed CSV: {exc}") from exc
    if not normalized:
        raise Rejected("CSV must have at least one episode slot")
    normalized.sort(key=lambda row: (row["season"], row["episode_number"]))
    return normalized


def build_proposal(receipt: dict, raw: bytes, catalog: dict) -> dict:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
        raise Rejected("receipt has missing or unexpected fields")
    digest = hashlib.sha256(raw).hexdigest()
    if (not isinstance(receipt["csv_sha256"], str)
            or not SHA256.fullmatch(receipt["csv_sha256"])
            or receipt["csv_sha256"] != digest):
        raise Rejected("receipt CSV SHA-256 does not match exact input bytes")
    proposal = {
        "record_type": "publisher_episode_roster_proposal",
        "schema_version": "1.0.0",
        "batch_id": receipt["batch_id"],
        "mission_id": receipt["mission_id"],
        "proposal_status": "CANDIDATE_METADATA_ONLY",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "roster_completeness": "UNRESOLVED",
        "listed_slot_count": 0,
        "observation": {
            "publisher": receipt["publisher"],
            "independence_group": receipt["independence_group"],
            "observed_on": receipt["observed_on"],
            "primary_locator": receipt["primary_locator"],
            "crosscheck_locator": receipt["crosscheck_locator"],
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None,
            "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": parse_rows(raw),
    }
    proposal["listed_slot_count"] = len(proposal["episode_slots"])
    validate(proposal, catalog)
    return proposal


def resolve_output(value: str, root: Path) -> Path:
    path = Path(value)
    if (path.is_absolute() or ".." in path.parts or path.parts[:1] != ("proposals",)
            or len(path.parts) < 3 or path.name != "bundle.json"):
        raise Rejected("output must be a new relative proposals/.../bundle.json")
    target = (root / path).resolve()
    parent = (root / "proposals").resolve()
    if not target.is_relative_to(parent):
        raise Rejected("output resolves outside proposals/")
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True, help="Offline UTF-8 three-column episode roster")
    parser.add_argument("--receipt", type=Path, required=True, help="Metadata-only source observation receipt")
    parser.add_argument("--output", required=True, help="New proposals/.../bundle.json path")
    parser.add_argument("--check", action="store_true", help="Validate without writing a file")
    args = parser.parse_args(argv)
    try:
        raw = read_csv_bytes(args.csv)
        proposal = build_proposal(read_json(args.receipt), raw, read_json(CATALOG))
        target = resolve_output(args.output, Path.cwd())
        if not args.check:
            # No implicit directory creation or replacement. The reviewer owns
            # proposal partition setup and publication independently.
            with target.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(proposal, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
    except (Rejected, OSError, ValueError) as exc:
        print(f"ROSTER_NORMALIZATION_REJECTED: {exc}", file=sys.stderr)
        return 1
    result = {"proposal_status": "CANDIDATE_METADATA_ONLY", "accepted_effect": "NONE",
              "mission_id": proposal["mission_id"], "listed_slots": len(proposal["episode_slots"]),
              "csv_sha256": hashlib.sha256(raw).hexdigest(),
              "mode": "CHECK_ONLY" if args.check else "NEW_PROPOSAL"}
    print("ROSTER_NORMALIZATION_CANDIDATE: " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
