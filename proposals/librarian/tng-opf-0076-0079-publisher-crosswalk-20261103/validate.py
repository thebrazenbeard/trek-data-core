#!/usr/bin/env python3
"""Fail-closed metadata-only TNG OPF0076-0079/S&S product crosswalk."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "records.json"
OPF = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"
MAIN_SHA = "c7a201df1a50aadcd062063aa48476f8eb6f4222"
OPF_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
ROOT_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only", "observed_date_utc",
    "baseline_accepted_main", "source_family", "source_read_class", "publisher_pages_read",
    "source_snapshots_available", "opf_input", "directory_baseline",
    "accepted_source_work_effect", "literary_coverage_effect", "private_ebook_custody_effect",
    "public_text_image_effect", "records",
}
ROW_KEYS = {
    "id", "opf_id", "opf_entry_sha256", "opf_title", "opf_creator", "opf_date_raw",
    "opf_isbn10", "publisher_title", "publisher_creator", "publisher_product_url",
    "publisher_isbn13", "publisher_series_ordinal", "publisher_format", "publisher_imprint",
    "publisher_product_date", "publisher_page_count", "product_details_line_anchor",
    "isbn_relation", "date_relation", "private_edition_verified", "rights_status",
}
# Exact source-worker-reported page-read tuples, pinned by validator code, not
# self-declared digest fields. No remote HTML snapshots were committed.
REVIEWED_ROWS_SHA256 = {
    "sns-tng-28-here-there-be-dragons-ebook-9780743421119": "7157f627fa7d856b92a56b5f8636e418e70e519e6a5151bb623a35ded708cdcd",
    "sns-tng-29-sins-of-commission-ebook-9780743421126": "ce0c8cdb8cd5790156b1cc9d5a67b35db74809d6f931970218bc0c2af231287e",
    "sns-tng-30-debtors-planet-ebook-9780743421133": "9a2a7e2095ee2544d55516ad6d40f03db63e468e7116713bc652baf26dd9be8f",
    "sns-tng-31-foreign-foes-ebook-9780743421140": "c80bc1b10779db62d479aee4c418c73d39d4cb0c67085382348ea8f99b261ad8",
}
OPF_BY_LOCAL = {
    "sns-tng-28-here-there-be-dragons-ebook-9780743421119": "opf-local:0076",
    "sns-tng-29-sins-of-commission-ebook-9780743421126": "opf-local:0077",
    "sns-tng-30-debtors-planet-ebook-9780743421133": "opf-local:0078",
    "sns-tng-31-foreign-foes-ebook-9780743421140": "opf-local:0079",
}


def require(condition: bool, failure: str) -> None:
    if not condition:
        raise ValueError(failure)


def closed(value: object, expected: set[str], context: str) -> None:
    require(isinstance(value, dict) and set(value) == expected, f"{context}: unknown or missing keys")


def parse_json_strict(raw: bytes | str) -> dict:
    def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
        out = {}
        for key, value in pairs:
            require(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out
    obj = json.loads(raw, object_pairs_hook=unique_pairs)
    require(isinstance(obj, dict), "JSON root not object")
    return obj


def isbn10_to_13(text: str) -> str:
    require(isinstance(text, str) and len(text) == 10 and text[:9].isascii() and
            text[:9].isdigit() and (text[-1].isdigit() or text[-1] == "X"),
            "invalid ISBN10 syntax")
    checksum = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(text))
    require(checksum % 11 == 0, "invalid ISBN10 checksum")
    root = "978" + text[:9]
    checksum13 = (-sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(root))) % 10
    return root + str(checksum13)


def validate(packet: dict, opf_bytes: bytes, catalog_bytes: bytes) -> int:
    closed(packet, ROOT_KEYS, "packet")
    require(packet["schema_version"] == "1.0.0" and
            packet["batch_id"] == "LIBRARIAN.TNG.OPF.0076-0079.PUBLISHER.20261103", "batch identity")
    require(packet["role"] == "LIBRARIAN" and packet["proposal_only"] is True, "worker role/proposal scope")
    require(packet["observed_date_utc"] == "2026-11-03" and
            packet["baseline_accepted_main"] == MAIN_SHA, "date/accepted-main snapshot identity")
    require(packet["source_family"] == "publisher:simonandschuster.com" and
            packet["source_read_class"] == "FIRST_PARTY_RENDERED_PRODUCT_DETAILS" and
            packet["publisher_pages_read"] == 4 and packet["source_snapshots_available"] is False,
            "unreviewed publisher acquisition claim")
    for effect in ("accepted_source_work_effect", "literary_coverage_effect",
                   "private_ebook_custody_effect", "public_text_image_effect"):
        require(packet[effect] == "NONE", f"{effect}: forbidden promotion")

    meta = packet["opf_input"]
    closed(meta, {"path", "sha256", "scope"}, "OPF source")
    require(meta == {
        "path": "proposals/librarian/private-opf-metadata-20261103/observations.json",
        "sha256": OPF_SHA, "scope": "ACCEPTED_SANITIZED_OPF_METADATA_ONLY",
    }, "OPF path/hash/scope substitution")
    require(hashlib.sha256(opf_bytes).hexdigest() == OPF_SHA, "OPF source bytes changed")
    private_rows = parse_json_strict(opf_bytes)["rows"]
    private = {r["source_local_id"]: r for r in private_rows}
    require(len(private) == len(private_rows), "OPF source IDs duplicated")

    snap = packet["directory_baseline"]
    closed(snap, {"path", "sha256", "source_local_rows", "literature_rows", "publisher_title_hits"}, "directory snapshot")
    require(snap["path"] == "explorer/discovery-catalog.json" and snap["sha256"] == CATALOG_SHA,
            "directory path/hash substitution")
    require(hashlib.sha256(catalog_bytes).hexdigest() == CATALOG_SHA, "directory source bytes changed")
    records = packet["records"]
    require(isinstance(records, list) and len(records) == 4, "exactly four source-local editions required")
    directory_rows = parse_json_strict(catalog_bytes)["rows"]
    literary = [r for r in directory_rows if r.get("medium") == "LITERATURE"]
    titles = {r.get("publisher_title") for r in packet["records"]}
    require(len(directory_rows) == snap["source_local_rows"] == 1214 and
            len(literary) == snap["literature_rows"] == 9 and
            sum(r.get("title") in titles for r in literary) == snap["publisher_title_hits"] == 0,
            "directory denominator or title overlap")

    seen = set()
    for row in records:
        closed(row, ROW_KEYS, "edition record")
        local_id = row["id"]
        require(local_id in REVIEWED_ROWS_SHA256 and local_id not in seen, "unreviewed/duplicate edition ID")
        seen.add(local_id)
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":"),
                                           ensure_ascii=False).encode("utf-8")).hexdigest()
        require(digest == REVIEWED_ROWS_SHA256[local_id], f"{local_id}: unreviewed source/edition tuple")
        require(row["opf_id"] == OPF_BY_LOCAL[local_id], f"{local_id}: wrong OPF source ID")
        require(isbn10_to_13(row["opf_isbn10"]) == row["publisher_isbn13"],
                f"{local_id}: identifier conversion mismatch")
        publisher_url = urlsplit(row["publisher_product_url"])
        require(publisher_url.scheme == "https" and publisher_url.netloc == "www.simonandschuster.com" and
                not publisher_url.query and not publisher_url.fragment and not publisher_url.username and
                not publisher_url.password, f"{local_id}: unsafe publisher page URL")
        require(row["publisher_format"] == "EBOOK" and row["publisher_imprint"] == "Pocket Books/Star Trek" and
                row["publisher_product_date"] == "2000-09-22", f"{local_id}: publisher product scope drift")
        require(row["opf_date_raw"] != row["publisher_product_date"] and
                row["date_relation"] == "CONFLICT_UNRESOLVED" and
                row["isbn_relation"] == "MATCHING_CHECKSUM_CONVERTED_IDENTIFIER_ONLY",
                f"{local_id}: premature date/identity reconciliation")
        require(row["private_edition_verified"] is False and
                row["rights_status"] == "METADATA_ONLY_NO_PUBLIC_TEXT_IMAGE_RIGHTS",
                f"{local_id}: source or rights escalation")
        source = private.get(row["opf_id"])
        require(isinstance(source, dict) and source["opf_entry_sha256"] == row["opf_entry_sha256"] and
                source["title"] == [row["opf_title"]] and source["creator"] == [row["opf_creator"]] and
                source["date"] == [row["opf_date_raw"]] and
                source["isbn_checksum_valid"] == [row["opf_isbn10"]],
                f"{local_id}: OPF fields not source-relative")
    require(seen == set(REVIEWED_ROWS_SHA256), "reviewed source rows omitted")
    return len(seen)


def main() -> None:
    n = validate(parse_json_strict(PACKET.read_text(encoding="utf-8")), OPF.read_bytes(), CATALOG.read_bytes())
    print(f"PASS: {n} first-party TNG eBook product/OPF identifier leads; 4 unresolved dates, no admission/custody/release")


if __name__ == "__main__":
    main()
