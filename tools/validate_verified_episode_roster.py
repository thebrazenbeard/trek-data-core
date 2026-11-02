#!/usr/bin/env python3
"""Validate a claimed independent review of publisher episode *metadata*.

This is a separate handoff after an unadmitted publisher roster proposal. It
does not admit Works, Source bindings, episode content, coverage or projections.
An offline snapshot digest confirms custody of bytes, not the human review's
truth or independence. Project authority must make those decisions separately.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import re
import sys
from pathlib import Path

from validate_publisher_episode_roster import (
    CATALOG, IDENTIFIER, Rejected, keys, read_json, safe_locator, text, unique_pairs,
    validate as validate_candidate,
)
from normalize_episode_roster import read_csv_bytes

SHA256 = re.compile(r"sha256:[0-9a-f]{64}\Z")
REVIEW_KEYS = {
    "record_type", "schema_version", "candidate_batch_id", "candidate_sha256",
    "mission_id", "publisher_snapshot", "review", "metadata_status",
    "canonical_work_effect", "source_binding_effect", "continuity_effect",
    "coverage_effect", "denominator_effect", "publication_effect",
}
SLOT_KEYS = {"season", "episode_number", "title"}
SNAPSHOT_KEYS = {
    "locator", "independence_group", "retrieved_on", "content_sha256",
    "representation", "publication",
}
REVIEWER_KEYS = {
    "collector_id", "reviewer_id", "reviewed_on", "attestation", "scope",
    "checked_episode_slots",
}
EFFECT_KEYS = (
    "canonical_work_effect", "source_binding_effect", "continuity_effect",
    "coverage_effect", "denominator_effect", "publication_effect",
)


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def calendar(value: object, label: str) -> date:
    try:
        value = text(value, label, 10)
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("not ISO calendar format")
        return date.fromisoformat(value)
    except ValueError as exc:
        raise Rejected(f"{label} must be an ISO calendar date") from exc


def validate_review(candidate: dict, candidate_raw: bytes, review: dict,
                    catalog: dict, snapshot_raw: bytes | None = None) -> dict:
    """Validate claim-to-proposal consistency without promoting accepted state."""
    validate_candidate(candidate, catalog)
    keys(review, REVIEW_KEYS, "independent metadata review")
    if (review["record_type"] != "publisher_episode_metadata_review"
            or review["schema_version"] != "1.0.0"
            or review["metadata_status"] != "REVIEW_PROPOSAL_ONLY"):
        raise Rejected("unrecognized metadata-only review/status")
    for effect in EFFECT_KEYS:
        if review[effect] != "NONE":
            raise Rejected(f"metadata review cannot cause {effect}")
    if review["candidate_batch_id"] != candidate["batch_id"] or review["mission_id"] != candidate["mission_id"]:
        raise Rejected("metadata review targets a different candidate batch/Mission")
    if (not isinstance(review["candidate_sha256"], str)
            or not SHA256.fullmatch(review["candidate_sha256"])
            or review["candidate_sha256"] != digest(candidate_raw)):
        raise Rejected("candidate byte digest mismatch")

    snapshot = keys(review["publisher_snapshot"], SNAPSHOT_KEYS, "publisher snapshot")
    safe_locator(snapshot["locator"], "snapshot locator")
    if snapshot["locator"] != candidate["observation"]["primary_locator"]:
        raise Rejected("snapshot locator does not match the proposed publisher page")
    if (snapshot["independence_group"] != candidate["observation"]["independence_group"]
            or snapshot["representation"] != "PUBLISHER_PAGE_BYTES"
            or snapshot["publication"] != "BYTES_EXCLUDED"):
        raise Rejected("publisher snapshot has unsupported identity/representation")
    snapshot_date = calendar(snapshot["retrieved_on"], "snapshot retrieved_on")
    if snapshot_date > date.today():
        raise Rejected("snapshot retrieval cannot be in the future")
    if not isinstance(snapshot["content_sha256"], str) or not SHA256.fullmatch(snapshot["content_sha256"]):
        raise Rejected("publisher snapshot requires a full SHA-256 content digest")
    if snapshot_raw is not None and digest(snapshot_raw) != snapshot["content_sha256"]:
        raise Rejected("publisher snapshot byte digest mismatch")

    attestation = keys(review["review"], REVIEWER_KEYS, "reviewer attestation")
    collector = text(attestation["collector_id"], "collector identity", 100)
    reviewer = text(attestation["reviewer_id"], "reviewer identity", 100)
    if not IDENTIFIER.fullmatch(collector) or not IDENTIFIER.fullmatch(reviewer) or collector == reviewer:
        raise Rejected("metadata reviewer must have a distinct bounded identity")
    reviewed_on = calendar(attestation["reviewed_on"], "reviewed_on")
    if reviewed_on < snapshot_date:
        raise Rejected("review cannot precede publisher snapshot retrieval")
    if reviewed_on > date.today():
        raise Rejected("metadata review cannot be dated in the future")
    if (attestation["attestation"] != "IDENTITY_FIELDS_MATCH_SNAPSHOT"
            or attestation["scope"] != "PUBLISHER_TITLE_SEASON_EPISODE_ONLY"):
        raise Rejected("unsupported review attestation/scope")
    checked = attestation["checked_episode_slots"]
    if not isinstance(checked, list) or not checked or len(checked) > len(candidate["episode_slots"]):
        raise Rejected("review must identify bounded nonempty checked episode slots")
    candidates = {(row["season"], row["episode_number"]): row["title"] for row in candidate["episode_slots"]}
    prior = (0, 0)
    for i, slot in enumerate(checked):
        keys(slot, SLOT_KEYS, f"checked_episode_slots[{i}]")
        number = (slot["season"], slot["episode_number"])
        if (any(type(n) is not int or n < 1 for n in number) or number <= prior
                or candidates.get(number) != slot["title"]):
            raise Rejected("reviewed episode slot must uniquely and exactly match the candidate")
        text(slot["title"], "reviewed episode title")
        prior = number
    return {
        "mission_id": candidate["mission_id"],
        "checked_episode_slots": len(checked),
        "review_receipt_status": (
            "SNAPSHOT_BYTES_MATCH_RECEIPT_NOT_ADMITTED" if snapshot_raw is not None
            else "DECLARED_REVIEW_RECEIPT_ONLY_NOT_ADMITTED"
        ),
        "accepted_effect": "NONE",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path, help="Unadmitted proposal bundle JSON")
    parser.add_argument("--review", required=True, type=Path, help="Independent metadata review JSON")
    parser.add_argument("--snapshot", type=Path, help="Private publisher snapshot bytes for digest check")
    args = parser.parse_args(argv)
    try:
        candidate_raw = read_csv_bytes(args.candidate)
        candidate = json.loads(candidate_raw.decode("utf-8"), object_pairs_hook=unique_pairs)
        review = read_json(args.review)
        snapshot_raw = read_snapshot(args.snapshot) if args.snapshot else None
        result = validate_review(candidate, candidate_raw, review, read_json(CATALOG), snapshot_raw)
    except (Rejected, ValueError, OSError, UnicodeDecodeError, RecursionError) as exc:
        print(f"EPISODE_METADATA_REVIEW_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("EPISODE_METADATA_REVIEW_CHECK: " + json.dumps(result, sort_keys=True))
    return 0


def read_snapshot(path: Path) -> bytes:
    # Kept private; read-only safe input with a larger bound for publisher HTML.
    import os
    import stat
    limit = 8 * 1024 * 1024
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise Rejected("safe input flags are unavailable")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        raise Rejected("snapshot must be a bounded non-symlink regular file")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        actual = os.fstat(stream.fileno())
        if (not stat.S_ISREG(actual.st_mode) or actual.st_ino != before.st_ino
                or actual.st_dev != before.st_dev or actual.st_size > limit):
            raise Rejected("snapshot file changed during safe open")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise Rejected("snapshot exceeds byte limit")
    return raw


if __name__ == "__main__":
    raise SystemExit(main())
