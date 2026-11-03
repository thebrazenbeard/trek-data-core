#!/usr/bin/env python3
"""Fail-closed validation of source-local owner TXT ZIP observations 151–200."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
DATA = HERE / "observations.json"
PREVIOUS = (
    HERE.parent / "private-ds9-txt50-20261103" / "observations.json",
    HERE.parent / "private-txt51-100-20261103" / "observations.json",
    HERE.parent / "private-txt101-150-20261103" / "observations.json",
)
OLD_RECEIPTS = [
    ("LIBRARIAN-PRIVATE-DS9-TXT50-20261103", "56017619758a9e0294384187ec1c18569b1966729bfaf47fbdc85a8d68438553", 1, 50),
    ("LIBRARIAN-PRIVATE-TXT51-100-20261103", "59cb068ab6fee0338846c031bcf4f25044c01a055856f156b6acdd4f0cf94d27", 51, 100),
    ("LIBRARIAN-PRIVATE-TXT101-150-20261103", "38f4c77d5dcbf1ff20eaea358253f93f6b193934830744948a43d0bf04bbd5e1", 101, 150),
]
SHA = re.compile(r"^[0-9a-f]{64}$")
ROW_KEYS = {
    "source_local_id", "archive_txt_ordinal", "series_hint",
    "series_file_sequence_hint", "title_hint", "uncompressed_bytes", "member_sha256",
}
TOP_KEYS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "archive", "sample",
    "prior_accepted_packets", "data_rights", "member_byte_access",
    "work_coverage_stage", "source_work_binding", "edition_binding",
    "copyrighted_text_exported", "private_member_paths_exported",
    "records", "records_sha256",
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def rows_digest(rows: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def validate(current: dict, previous: list[dict]) -> None:
    require(isinstance(current, dict) and set(current) == TOP_KEYS, "unexpected or private field")
    require(current["schema_version"] == "1.0.0", "schema mismatch")
    require(current["proposal_id"] == "LIBRARIAN-PRIVATE-TXT151-200-20261103", "packet identity")
    require(current["accepted_main_baseline"] == "4a6ebb1c1ae22f7e4b1221f20c32aa93b322d01c", "accepted main")
    require(current["archive"] == {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B",
        "whole_zip_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
        "bytes": 126481241, "zip_members": 573, "txt_members": 220,
    }, "source container receipt drift")
    require(current["sample"] ==
            "lexically sorted TXT member ordinals 151-200; TNG 064-103 and VOY 001-010 filename hints",
            "sample definition changed")
    expected_old = [
        {"proposal_id": pid, "records_sha256": sha, "range_start": first, "range_end": last}
        for pid, sha, first, last in OLD_RECEIPTS
    ]
    require(current["prior_accepted_packets"] == expected_old, "prior packet custody")
    for key, expected in (
        ("data_rights", "UNKNOWN"),
        ("member_byte_access", "HASHED_WITHOUT_SEMANTIC_READ"),
        ("work_coverage_stage", "DISCOVERED"),
        ("source_work_binding", "UNRESOLVED"),
        ("edition_binding", "UNRESOLVED"),
        ("copyrighted_text_exported", False),
        ("private_member_paths_exported", False),
    ):
        require(type(current[key]) is type(expected) and current[key] == expected, f"false {key}")
    require(isinstance(previous, list) and len(previous) == 3, "prior packet count")
    ids: set[str] = set()
    hashes: set[str] = set()
    for packet, (pid, digest, first, last) in zip(previous, OLD_RECEIPTS):
        require(isinstance(packet, dict) and packet.get("proposal_id") == pid, "prior packet identity")
        require(packet.get("records_sha256") == digest, "prior claimed hash")
        rows = packet.get("records")
        require(isinstance(rows, list) and len(rows) == 50 and rows_digest(rows) == digest, "prior packet bytes")
        for n, row in enumerate(rows, first):
            require(row["source_local_id"] == f"txt-local:{n:04d}" and
                    row["archive_txt_ordinal"] == n, "prior ordinal")
            require(row["source_local_id"] not in ids and row["member_sha256"] not in hashes,
                    "prior packet overlap")
            ids.add(row["source_local_id"])
            hashes.add(row["member_sha256"])
        require(n == last, "prior packet position")
    require(len(ids) == 150 and len(hashes) == 150, "prior packets incomplete")

    rows = current["records"]
    require(isinstance(rows, list) and len(rows) == 50, "new packet not 50")
    digest = current["records_sha256"]
    require(isinstance(digest, str) and SHA.fullmatch(digest) is not None, "invalid new digest")
    require(rows_digest(rows) == digest, "new packet byte drift")
    for n, row in enumerate(rows, 151):
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "row field leakage")
        require(row["source_local_id"] == f"txt-local:{n:04d}" and
                type(row["archive_txt_ordinal"]) is int and row["archive_txt_ordinal"] == n, "new ID/ordinal")
        series, seq = ("TNG", n - 87) if n <= 190 else ("VOY", n - 190)
        require(row["series_hint"] == series and
                type(row["series_file_sequence_hint"]) is int and row["series_file_sequence_hint"] == seq,
                "series sequence")
        title = row["title_hint"]
        require(isinstance(title, str) and 1 <= len(title) <= 120 and
                not any(ch in title for ch in "/\\\r\n\x00"), "unsafe title hint")
        require(type(row["uncompressed_bytes"]) is int and
                100 <= row["uncompressed_bytes"] <= 8 * 1024 * 1024, "member size")
        member_sha = row["member_sha256"]
        require(isinstance(member_sha, str) and SHA.fullmatch(member_sha) is not None and
                member_sha not in hashes and row["source_local_id"] not in ids, "duplicate member/ID")
        hashes.add(member_sha)
        ids.add(row["source_local_id"])
    require(len(ids) == 200 and len(hashes) == 200, "incomplete 200-member chain")


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")),
             [json.loads(p.read_text(encoding="utf-8")) for p in PREVIOUS])
    print("PASS: first 200 TXT member receipts cross-checked; no rights, edition or Work admissions")
