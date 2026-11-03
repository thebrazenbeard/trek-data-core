#!/usr/bin/env python3
"""Validate a private-derived, public-safe Trek TXT file-fingerprint proposal.

This validates the committed derivative and its provenance constraints, not
the owner's private ZIP or bibliographic identity of the named works.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
DATA = HERE / "observations.json"
ORIGINAL_ARCHIVE_SHA256 = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
SHA = re.compile(r"^[0-9a-f]{64}$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^txt-local:[0-9]{4}$")
ROW_KEYS = {"source_local_id", "archive_txt_ordinal", "series_file_sequence_hint", "title_hint", "uncompressed_bytes", "member_sha256"}
TOP_KEYS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "archive",
    "sample", "data_rights", "member_byte_access", "work_coverage_stage",
    "source_work_binding", "edition_binding", "copyrighted_text_exported",
    "private_member_paths_exported", "records", "records_sha256",
}


def rows_digest(rows: list[dict]) -> str:
    serialized = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def validate(data: dict) -> None:
    assert set(data) == TOP_KEYS, "unexpected or missing top-level field"
    assert data["schema_version"] == "1.0.0"
    assert data["proposal_id"] == "LIBRARIAN-PRIVATE-DS9-TXT50-20261103"
    assert COMMIT_SHA.fullmatch(data["accepted_main_baseline"])
    archive = data["archive"]
    assert set(archive) == {"opaque_id", "whole_zip_sha256", "bytes", "zip_members", "txt_members"}
    assert archive == {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B",
        "whole_zip_sha256": ORIGINAL_ARCHIVE_SHA256,
        "bytes": 126481241,
        "zip_members": 573,
        "txt_members": 220,
    }
    assert data["sample"] == "first 50 lexically sorted TXT members (DS9 positions 001-050)"
    assert data["data_rights"] == "UNKNOWN"
    assert data["member_byte_access"] == "HASHED_WITHOUT_SEMANTIC_READ"
    assert data["work_coverage_stage"] == "DISCOVERED"
    assert data["source_work_binding"] == "UNRESOLVED"
    assert data["edition_binding"] == "UNRESOLVED"
    assert data["copyrighted_text_exported"] is False
    assert data["private_member_paths_exported"] is False
    rows = data["records"]
    assert isinstance(rows, list) and len(rows) == 50
    assert SHA.fullmatch(data["records_sha256"])
    assert data["records_sha256"] == rows_digest(rows), "row digest mismatch"
    seen_hashes = set()
    for n, row in enumerate(rows, 1):
        assert isinstance(row, dict) and set(row) == ROW_KEYS, "unexpected row field"
        assert ID.fullmatch(row["source_local_id"])
        assert row["source_local_id"] == f"txt-local:{n:04d}"
        assert type(row["archive_txt_ordinal"]) is int and row["archive_txt_ordinal"] == n
        assert type(row["series_file_sequence_hint"]) is int and row["series_file_sequence_hint"] == n
        title = row["title_hint"]
        assert isinstance(title, str) and 1 <= len(title) <= 120
        assert not any(ch in title for ch in "/\\\r\n\x00"), "private paths or controls disallowed"
        assert type(row["uncompressed_bytes"]) is int and 100 <= row["uncompressed_bytes"] <= 8 * 1024 * 1024
        digest = row["member_sha256"]
        assert isinstance(digest, str) and SHA.fullmatch(digest)
        assert digest not in seen_hashes, "duplicate member byte fingerprint in sample"
        seen_hashes.add(digest)


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")))
    print("PASS: 50 metadata-only DS9 TXT source-member receipts; no Work/edition admissions")
