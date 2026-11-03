#!/usr/bin/env python3
"""Validate a public literary structural proposal, without accessing book text."""

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
HEX256 = re.compile(r"[0-9a-f]{64}\Z")
PINNED_SHA256 = {
    "source_container_sha256": "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f",
    "opf_member_sha256": "36c23dc2c9ff5e1ebc3d7009dcff503ac5b42661c5c6376e5e787b49fb562322",
    "html_spine_sha256": "f509150d56264056b6f1c2dc46361dd52d1a44faba82634af80a0f570078cb5f",
}
PUBLISHER_URL = (
    "https://www.simonandschuster.com/books/"
    "A-Star-Trek-The-Next-Generation-Time-7-A-Time-to-Kill/"
    "David-Mack/Star-Trek-The-Next-Generation/9780743494076"
)
# This is a public receipt of the observed chapter rows. A matching digest
# detects unreviewed sidecar changes; it is not private-text authentication.
PINNED_CHAPTER_ROW_DIGEST = "43a01348ee7e4012d82945a5531cb5aba8b48b3903a6ae527c6e113a8a95ff31"
EXPECTED_TOP = {
    "schema_version", "proposal_only", "accepted_source_binding_effect",
    "accepted_work_effect", "coverage_effect", "source_kind",
    "source_container_sha256", "opf_member_sha256", "html_spine_sha256",
    "work_candidate_title", "work_candidate_creator", "isbn10_metadata",
    "isbn13_publisher", "publisher_url", "extraction_method",
    "normalization_scope", "method_specific_whitespace_token_count",
    "normalized_nonblank_line_count", "chapter_count", "chapters",
}
EXPECTED_CHAPTER = {
    "chapter", "source_relative_normalized_line_start",
    "source_relative_normalized_line_end_exclusive",
    "whitespace_token_count", "segment_sha256",
}


def validate(data):
    if set(data) != EXPECTED_TOP:
        raise ValueError("public index field set drift")
    if data["schema_version"] != "trek-lit-private-structural-proposal-v1":
        raise ValueError("schema version drift")
    if data["proposal_only"] is not True:
        raise ValueError("cannot promote this proposal")
    for name in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect"):
        if data[name] != "NONE":
            raise ValueError("nonzero accepted research effect")
    if data["source_kind"] != "USER_HELD_CONVERTED_OPF_DERIVATIVE_UNVERIFIED":
        raise ValueError("source-kind boundary drift")
    if data["normalization_scope"] != "CONVERTED_HTML_NOT_ORIGINAL_LIT":
        raise ValueError("normalization scope drift")
    for name in ("source_container_sha256", "opf_member_sha256", "html_spine_sha256"):
        if not isinstance(data[name], str) or not HEX256.fullmatch(data[name]):
            raise ValueError(f"bad SHA-256 field: {name}")
        if data[name] != PINNED_SHA256[name]:
            raise ValueError(f"source receipt fingerprint drift: {name}")
    if data["work_candidate_title"] != "A Time to Kill":
        raise ValueError("wrong book")
    if data["work_candidate_creator"] != "David Mack":
        raise ValueError("wrong creator")
    if data["isbn10_metadata"] != "0743494075" or data["isbn13_publisher"] != "9780743494076":
        raise ValueError("edition identifier drift")
    if data["publisher_url"] != PUBLISHER_URL:
        raise ValueError("publisher-edition URL drift")
    if not isinstance(data["extraction_method"], str) or len(data["extraction_method"]) > 350:
        raise ValueError("unexpected extractor metadata")
    if data["method_specific_whitespace_token_count"] != 71974:
        raise ValueError("normalization receipt drift")
    rows = data["chapters"]
    if not isinstance(rows, list) or len(rows) != 69 or data["chapter_count"] != 69:
        raise ValueError("expected 69 chapter observations")
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if hashlib.sha256(payload).hexdigest() != PINNED_CHAPTER_ROW_DIGEST:
        raise ValueError("chapter receipt fingerprint drift")
    previous_end = None
    for ordinal, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != EXPECTED_CHAPTER:
            raise ValueError("unexpected chapter field")
        if type(row["chapter"]) is not int or row["chapter"] != ordinal:
            raise ValueError("nonmonotonic chapter ordinal")
        start = row["source_relative_normalized_line_start"]
        end = row["source_relative_normalized_line_end_exclusive"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end:
            raise ValueError("invalid normalized line span")
        if previous_end is not None and start != previous_end:
            raise ValueError("gap/overlap in chapter spans")
        if type(row["whitespace_token_count"]) is not int or row["whitespace_token_count"] <= 0:
            raise ValueError("invalid method-specific token count")
        if not isinstance(row["segment_sha256"], str) or not HEX256.fullmatch(row["segment_sha256"]):
            raise ValueError("invalid chapter fingerprint")
        previous_end = end
    if rows[0]["source_relative_normalized_line_start"] != 33:
        raise ValueError("front-matter offset drift")
    if previous_end != data["normalized_nonblank_line_count"] or previous_end != 2225:
        raise ValueError("terminal normalized line count drift")
    if sum(row["whitespace_token_count"] for row in rows) != 71636:
        raise ValueError("chapter-only whitespace token count drift")


if __name__ == "__main__":
    with (HERE / "CHAPTER_INDEX.json").open(encoding="utf-8") as stream:
        validate(json.load(stream))
    print("PASS: proposal-only literary structural index (69 chapters; no book text)")
