#!/usr/bin/env python3
"""Fail-closed public derivative validator for final 20 private Trek TXT members.

Only metadata receipts and nonoverlap with accepted 200 source-member receipts
are checked; no Source→Work, edition, copyright or CLOSE_READ is admitted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
DATA = HERE / "observations.json"
PRIOR = (
    HERE.parent / "private-ds9-txt50-20261103" / "observations.json",
    HERE.parent / "private-txt51-100-20261103" / "observations.json",
    HERE.parent / "private-txt101-150-20261103" / "observations.json",
    HERE.parent / "private-txt151-200-20261103" / "observations.json",
)
PRIOR_META = (
    ("LIBRARIAN-PRIVATE-DS9-TXT50-20261103", "56017619758a9e0294384187ec1c18569b1966729bfaf47fbdc85a8d68438553", 1, 50),
    ("LIBRARIAN-PRIVATE-TXT51-100-20261103", "59cb068ab6fee0338846c031bcf4f25044c01a055856f156b6acdd4f0cf94d27", 51, 100),
    ("LIBRARIAN-PRIVATE-TXT101-150-20261103", "38f4c77d5dcbf1ff20eaea358253f93f6b193934830744948a43d0bf04bbd5e1", 101, 150),
    ("LIBRARIAN-PRIVATE-TXT151-200-20261103", "c608f11dde8278eb2a918f0885d99c208d8907cc2565d96f1c905181363380b0", 151, 200),
)
SHA = re.compile(r"^[0-9a-f]{64}$")
FIELDS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "archive", "sample",
    "prior_packets", "data_rights", "member_byte_access",
    "work_coverage_stage", "source_work_binding", "edition_binding",
    "copyrighted_text_exported", "private_member_paths_exported",
    "records", "records_sha256",
}
ROW_FIELDS = {
    "source_local_id", "archive_txt_ordinal", "series_hint",
    "series_file_sequence_hint", "title_hint", "uncompressed_bytes", "member_sha256",
}


def check(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def rows_digest(rows: list[dict]) -> str:
    serialized = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def validate(current: dict, previous: list[dict]) -> None:
    check(isinstance(current, dict) and set(current) == FIELDS, "unexpected top-level fields")
    check(current["schema_version"] == "1.0.0", "schema")
    check(current["proposal_id"] == "LIBRARIAN-PRIVATE-TXT201-220-20261103", "packet")
    check(current["accepted_main_baseline"] == "e4348bdf4287d82c2bb6e88db39209f1db5688af", "accepted base")
    check(current["archive"] == {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B",
        "whole_zip_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
        "bytes": 126481241, "zip_members": 573, "txt_members": 220,
    }, "source container receipt")
    check(current["sample"] ==
          "lexically sorted TXT member ordinals 201-220; VOY filename sequences 011-030", "sample definition")
    expected_previous = [
        {"proposal_id": id, "records_sha256": digest, "range_start": start, "range_end": end}
        for id, digest, start, end in PRIOR_META
    ]
    check(current["prior_packets"] == expected_previous, "predecessor packet chain")
    for key, expected in (
        ("data_rights", "UNKNOWN"),
        ("member_byte_access", "HASHED_WITHOUT_SEMANTIC_READ"),
        ("work_coverage_stage", "DISCOVERED"),
        ("source_work_binding", "UNRESOLVED"),
        ("edition_binding", "UNRESOLVED"),
        ("copyrighted_text_exported", False),
        ("private_member_paths_exported", False),
    ):
        check(type(current[key]) is type(expected) and current[key] == expected, f"false {key}")
    check(isinstance(previous, list) and len(previous) == 4, "expected four accepted predecessor packets")
    known_ids: set[str] = set()
    known_hashes: set[str] = set()
    for packet, (pid, digest, start, end) in zip(previous, PRIOR_META):
        check(isinstance(packet, dict) and packet.get("proposal_id") == pid, "predecessor identity")
        check(packet.get("records_sha256") == digest, "predecessor digest field")
        rows = packet.get("records")
        check(isinstance(rows, list) and len(rows) == end - start + 1 and
              rows_digest(rows) == digest, "predecessor rows drift")
        for n, row in enumerate(rows, start):
            check(row["source_local_id"] == f"txt-local:{n:04d}" and
                  row["archive_txt_ordinal"] == n, "predecessor positions")
            check(row["source_local_id"] not in known_ids and
                  row["member_sha256"] not in known_hashes, "predecessor overlap")
            known_ids.add(row["source_local_id"])
            known_hashes.add(row["member_sha256"])
    check(len(known_ids) == 200 and len(known_hashes) == 200, "predecessors not byte-distinct 200")

    rows = current["records"]
    check(isinstance(rows, list) and len(rows) == 20, "final packet must contain 20")
    digest = current["records_sha256"]
    check(isinstance(digest, str) and SHA.fullmatch(digest) is not None and
          rows_digest(rows) == digest, "final row digest")
    for n, row in enumerate(rows, 201):
        check(isinstance(row, dict) and set(row) == ROW_FIELDS, "unexpected or leaked row field")
        check(row["source_local_id"] == f"txt-local:{n:04d}" and
              type(row["archive_txt_ordinal"]) is int and row["archive_txt_ordinal"] == n,
              "final member order")
        check(row["series_hint"] == "VOY" and
              type(row["series_file_sequence_hint"]) is int and row["series_file_sequence_hint"] == n - 190,
              "Voyager sequence")
        title = row["title_hint"]
        check(isinstance(title, str) and 1 <= len(title) <= 120 and
              not any(ch in title for ch in "/\\\r\n\x00"), "private path/control in title")
        check(type(row["uncompressed_bytes"]) is int and
              100 <= row["uncompressed_bytes"] <= 8 * 1024 * 1024, "member size")
        member_sha = row["member_sha256"]
        check(isinstance(member_sha, str) and SHA.fullmatch(member_sha) is not None and
              member_sha not in known_hashes and row["source_local_id"] not in known_ids,
              "hash/ID repeat")
        known_hashes.add(member_sha)
        known_ids.add(row["source_local_id"])
    check(len(known_hashes) == 220 and len(known_ids) == 220, "entire 220 TXT file receipt set incomplete")


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")),
             [json.loads(p.read_text(encoding="utf-8")) for p in PRIOR])
    print("PASS: all 220 original TXT members have byte-distinct source-local metadata receipts")
