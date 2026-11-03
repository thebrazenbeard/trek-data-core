#!/usr/bin/env python3
"""Validate metadata-only source-local Trek private TXT receipts 101–150.

This locks public derivative bytes, not the owner's inaccessible ZIP authority.
No literary Work, edition or source-content read is admitted.
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
)
PRIOR_META = [
    {"proposal_id": "LIBRARIAN-PRIVATE-DS9-TXT50-20261103",
     "records_sha256": "56017619758a9e0294384187ec1c18569b1966729bfaf47fbdc85a8d68438553",
     "range_start": 1, "range_end": 50},
    {"proposal_id": "LIBRARIAN-PRIVATE-TXT51-100-20261103",
     "records_sha256": "59cb068ab6fee0338846c031bcf4f25044c01a055856f156b6acdd4f0cf94d27",
     "range_start": 51, "range_end": 100},
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


def check(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def digest_rows(rows: list[dict]) -> str:
    data = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def validate(data: dict, previous: list[dict]) -> None:
    check(isinstance(data, dict) and set(data) == TOP_KEYS, "unexpected fields")
    check(data["schema_version"] == "1.0.0", "schema")
    check(data["proposal_id"] == "LIBRARIAN-PRIVATE-TXT101-150-20261103", "packet")
    check(data["accepted_main_baseline"] == "05d05de1c0238ed7ff39bd04427795e351f9b68b", "base")
    check(data["archive"] == {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B",
        "whole_zip_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
        "bytes": 126481241, "zip_members": 573, "txt_members": 220,
    }, "source archive")
    check(data["sample"] == "lexically sorted TXT member ordinals 101-150; TNG filename sequences 014-063", "sample")
    check(data["prior_accepted_packets"] == PRIOR_META, "prior packet metadata")
    check(data["data_rights"] == "UNKNOWN", "rights")
    check(data["member_byte_access"] == "HASHED_WITHOUT_SEMANTIC_READ", "reading status")
    check(data["work_coverage_stage"] == "DISCOVERED", "coverage inflation")
    check(data["source_work_binding"] == "UNRESOLVED", "Source→Work binding")
    check(data["edition_binding"] == "UNRESOLVED", "edition binding")
    check(data["copyrighted_text_exported"] is False, "copyright text")
    check(data["private_member_paths_exported"] is False, "private member paths")

    check(isinstance(previous, list) and len(previous) == 2, "previous packet count")
    known_hashes: set[str] = set()
    known_ids: set[str] = set()
    for packet, metadata in zip(previous, PRIOR_META):
        check(packet.get("proposal_id") == metadata["proposal_id"], "prior identity")
        check(packet.get("records_sha256") == metadata["records_sha256"], "prior claimed digest")
        oldrows = packet.get("records")
        check(isinstance(oldrows, list) and len(oldrows) == 50, "prior length")
        check(digest_rows(oldrows) == metadata["records_sha256"], "prior bytes")
        for ordinal, row in enumerate(oldrows, metadata["range_start"]):
            check(row["source_local_id"] == f"txt-local:{ordinal:04d}", "prior order")
            check(row["archive_txt_ordinal"] == ordinal, "prior ordinal")
            check(row["member_sha256"] not in known_hashes, "prior duplicate member")
            check(row["source_local_id"] not in known_ids, "prior duplicate ID")
            known_hashes.add(row["member_sha256"])
            known_ids.add(row["source_local_id"])
    check(len(known_hashes) == 100 and len(known_ids) == 100, "prior overlap")

    rows = data["records"]
    check(isinstance(rows, list) and len(rows) == 50, "new records count")
    check(isinstance(data["records_sha256"], str) and SHA.fullmatch(data["records_sha256"]) is not None, "row digest")
    check(digest_rows(rows) == data["records_sha256"], "row bytes drift")
    for n, row in enumerate(rows, 101):
        check(isinstance(row, dict) and set(row) == ROW_KEYS, "row field leak")
        check(row["source_local_id"] == f"txt-local:{n:04d}" and
              type(row["archive_txt_ordinal"]) is int and row["archive_txt_ordinal"] == n,
              "new ordinal")
        check(row["series_hint"] == "TNG" and
              type(row["series_file_sequence_hint"]) is int and row["series_file_sequence_hint"] == n - 87,
              "TNG sequence")
        title = row["title_hint"]
        check(isinstance(title, str) and 1 <= len(title) <= 120, "title hint")
        check(not any(c in title for c in "/\\\r\n\x00"), "member path or control chars")
        check(type(row["uncompressed_bytes"]) is int and 100 <= row["uncompressed_bytes"] <= 8 * 1024 * 1024,
              "byte length")
        h = row["member_sha256"]
        check(isinstance(h, str) and SHA.fullmatch(h) is not None and h not in known_hashes,
              "member hash or duplicate")
        check(row["source_local_id"] not in known_ids, "source ID duplicate")
        known_hashes.add(h)
        known_ids.add(row["source_local_id"])
    check(len(known_hashes) == 150 and len(known_ids) == 150, "three-packet uniqueness")


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")),
             [json.loads(p.read_text(encoding="utf-8")) for p in PRIOR])
    print("PASS: source-local TXT 101–150; 150 byte-distinct member receipts; zero Work admissions")
