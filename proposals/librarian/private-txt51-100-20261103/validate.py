#!/usr/bin/env python3
"""Fail-closed validation of metadata-only private Trek TXT ZIP receipts 51–100.

Verifies committed derivative and nonoverlap with accepted 1–50 packet.
Does not authenticate the private ZIP or prove distinct editions/Works.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE / "observations.json"
PRIOR = HERE.parent / "private-ds9-txt50-20261103" / "observations.json"
SHA = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^txt-local:\d{4}$")
SOURCE_SHA = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
PRIOR_ROWS_SHA = "56017619758a9e0294384187ec1c18569b1966729bfaf47fbdc85a8d68438553"
TOP_KEYS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "archive", "sample",
    "prior_accepted_packet", "data_rights", "member_byte_access",
    "work_coverage_stage", "source_work_binding", "edition_binding",
    "copyrighted_text_exported", "private_member_paths_exported",
    "records", "records_sha256",
}
ROW_KEYS = {
    "source_local_id", "archive_txt_ordinal", "series_hint",
    "series_file_sequence_hint", "title_hint", "uncompressed_bytes",
    "member_sha256",
}
SERIES = (
    (51, 52, "DS9", 51),
    (53, 69, "New Frontier", 1),
    (70, 75, "Slings and Arrows", 1),
    (76, 81, "Stargazer", 1),
    (82, 87, "Titan", 1),
    (88, 100, "TNG", 1),
)


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def digest_rows(rows: list[dict]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def series_for_ordinal(n: int) -> tuple[str, int]:
    for first, last, series, series_first in SERIES:
        if first <= n <= last:
            return series, series_first + n - first
    raise ValueError(f"unexpected TXT ordinal {n}")


def validate(data: dict, prior: dict) -> None:
    require(isinstance(data, dict) and set(data) == TOP_KEYS, "wrong top-level keys")
    require(data["schema_version"] == "1.0.0", "schema mismatch")
    require(data["proposal_id"] == "LIBRARIAN-PRIVATE-TXT51-100-20261103", "proposal mismatch")
    require(isinstance(data["accepted_main_baseline"], str) and
            COMMIT.fullmatch(data["accepted_main_baseline"]) is not None, "bad accepted head")
    require(data["accepted_main_baseline"] == "69f0a5c46e78b9d034ff168d969374892fc997e0", "incorrect base")
    require(data["archive"] == {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B",
        "whole_zip_sha256": SOURCE_SHA,
        "bytes": 126481241,
        "zip_members": 573,
        "txt_members": 220,
    }, "source archive changed")
    require(data["sample"] == "lexically sorted TXT member ordinals 51-100; six series filename hints", "sample changed")
    require(data["prior_accepted_packet"] == {
        "proposal_id": "LIBRARIAN-PRIVATE-DS9-TXT50-20261103",
        "records_sha256": PRIOR_ROWS_SHA,
        "range_start": 1,
        "range_end": 50,
    }, "prior packet receipt changed")
    require(data["data_rights"] == "UNKNOWN", "rights unsupported")
    require(data["member_byte_access"] == "HASHED_WITHOUT_SEMANTIC_READ", "false read claim")
    require(data["work_coverage_stage"] == "DISCOVERED", "false coverage")
    require(data["source_work_binding"] == "UNRESOLVED", "false Work binding")
    require(data["edition_binding"] == "UNRESOLVED", "false edition binding")
    require(data["copyrighted_text_exported"] is False, "copyright text flag")
    require(data["private_member_paths_exported"] is False, "member path flag")

    require(isinstance(prior, dict) and isinstance(prior.get("records"), list), "prior packet missing")
    require(prior.get("records_sha256") == PRIOR_ROWS_SHA, "prior digest claim changed")
    require(digest_rows(prior["records"]) == PRIOR_ROWS_SHA, "prior packet bytes changed")
    require(len(prior["records"]) == 50, "prior packet not 50 rows")
    prior_hashes = {r["member_sha256"] for r in prior["records"]}
    prior_ids = {r["source_local_id"] for r in prior["records"]}
    require(len(prior_hashes) == 50 and len(prior_ids) == 50, "prior packet repeats")

    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == 50, "this packet must have 50 entries")
    require(isinstance(data["records_sha256"], str) and
            SHA.fullmatch(data["records_sha256"]) is not None, "bad packet digest")
    require(digest_rows(rows) == data["records_sha256"], "record contents drifted")
    new_hashes = set()
    for n, row in enumerate(rows, 51):
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "unexpected record field")
        require(row["source_local_id"] == f"txt-local:{n:04d}" and
                ID.fullmatch(row["source_local_id"]) is not None, "noncontiguous or duplicate ID")
        require(type(row["archive_txt_ordinal"]) is int and row["archive_txt_ordinal"] == n,
                "noncontiguous TXT ordinal")
        expected_series, expected_sequence = series_for_ordinal(n)
        require(row["series_hint"] == expected_series and
                type(row["series_file_sequence_hint"]) is int and
                row["series_file_sequence_hint"] == expected_sequence, "series-position mismatch")
        title = row["title_hint"]
        require(isinstance(title, str) and 1 <= len(title) <= 120, "bad title hint")
        require(not any(ch in title for ch in "/\\\r\n\x00"), "private member path/control")
        require(type(row["uncompressed_bytes"]) is int and 100 <= row["uncompressed_bytes"] <= 8 * 1024 * 1024,
                "bad uncompressed size")
        digest = row["member_sha256"]
        require(isinstance(digest, str) and SHA.fullmatch(digest) is not None, "bad member digest")
        require(digest not in prior_hashes and digest not in new_hashes, "duplicate or prior member")
        require(row["source_local_id"] not in prior_ids, "duplicate prior member ID")
        new_hashes.add(digest)


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")), json.loads(PRIOR.read_text(encoding="utf-8")))
    print("PASS: TXT 51–100 file receipts; 100 nonoverlapping hashes/IDs, zero literary admissions")
