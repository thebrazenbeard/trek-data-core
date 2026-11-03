#!/usr/bin/env python3
"""Fail-closed publisher/OPF bibliographic source-local crosswalk validator.

The source files and publisher pages were separately observed; this validator
checks the committed derivative and accepted OPF/TXT receipts, not external
URL freshness or copyright/edition authenticity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE / "observations.json"
OPF = ROOT / "proposals" / "librarian" / "private-opf-metadata-20261103" / "observations.json"
TXT = ROOT / "proposals" / "librarian" / "private-txt51-100-20261103" / "observations.json"
SHA = re.compile(r"^[a-f0-9]{64}$")
ISBN10 = re.compile(r"^[0-9]{9}[0-9X]$")
ISBN13 = re.compile(r"^[0-9]{13}$")
EXPECTED_IDS = ["opf-local:0009"] + [f"opf-local:{n:04d}" for n in range(50, 59)]
EXPECTED_ISBNS = [
    "9780743439978", "9780743412131", "9780743412148", "9780743412155", "9780743412162",
    "9780743412179", "9780743420860", "9780743420877", "9780743420891", "9780743420907",
]
EXPECTED_TITLES = [
    "Have Tech Will Travel", "Ghost Ship", "The Peacekeepers", "The Children of Hamlin",
    "Survivors", "Strike Zone", "Power Hungry", "Masks", "A Call to Darkness",
    "A Rock and a Hard Place",
]
EXPECTED_BOOK_NUMBERS = [None, 1, 2, 3, 4, 5, 6, 7, 9, 10]
TOP_KEYS = {
    "schema_version", "proposal_id", "accepted_main_baseline", "owner_source_container",
    "independent_publisher_source", "observation_date_utc", "source_class",
    "total_candidates", "rehashed_original_opf_xml_members",
    "original_book_chapter_prose_read", "jacket_reference_only",
    "jacket_image_binary_published", "canonical_work_admissions",
    "accepted_edition_bindings", "coverage_effect", "identity_reconciliation_effect",
    "rights_status", "records", "records_sha256",
}
ROW_KEYS = {
    "source_local_opf_id", "original_opf_entry_sha256", "original_opf_xml_bytes",
    "opf_xml_parse_status", "opf_title_claim", "opf_creator_claims", "opf_isbn10_claim",
    "isbn13_computed_from_opf_isbn10", "official_product_title",
    "official_product_author_display", "official_product_isbn13",
    "official_product_ebook", "official_series_number", "official_product_page",
    "official_jacket_jpg_reference_seen", "edition_identifier_relation",
    "creator_relation", "bibliographic_role", "original_txt_filename_candidate_id",
    "original_txt_candidate_basis",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rowset_digest(rows: list[dict]) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def normalize_title(s: str) -> str:
    return re.sub(r"[^\w]+", "", s.casefold())


def valid_isbn10(s: str) -> bool:
    return bool(ISBN10.fullmatch(s)) and sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(s)) % 11 == 0


def isbn13_from_isbn10(s: str) -> str:
    require(valid_isbn10(s), "source ISBN10 check digit invalid")
    digits = "978" + s[:9]
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(digits))
    return digits + str((-total) % 10)


def valid_isbn13(s: str) -> bool:
    return bool(ISBN13.fullmatch(s)) and sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s)) % 10 == 0


def validate(data: dict, opf_index: dict, txt_index: dict) -> None:
    require(isinstance(data, dict) and set(data) == TOP_KEYS, "unexpected metadata fields")
    require(data["schema_version"] == "1.0.0", "schema")
    require(data["proposal_id"] == "LIBRARIAN-OPF-PUBLISHER-EDITION-TNG-SCE10-20261103", "packet")
    require(data["accepted_main_baseline"] == "885df8dc60122e55d9f37195eabd0b1a7c67b3c6", "accepted main")
    require(data["owner_source_container"] == {
        "opaque_id": "OWNER_PRIVATE_ST_OPF_ARCHIVE_A",
        "whole_zip_sha256": "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f",
        "bytes": 95673655, "opf_members": 347,
    }, "owner OPF container receipt")
    require(data["independent_publisher_source"] == "https://www.simonandschuster.com/", "publisher host")
    require(data["observation_date_utc"] == "2026-11-03", "observation date")
    require(data["source_class"] == "PRIVATE_OPF_XML_METADATA_PLUS_OFFICIAL_PUBLISHER_PAGE_BIBLIOGRAPHY", "source class")
    for field, value in (
        ("total_candidates", 10), ("rehashed_original_opf_xml_members", 10),
        ("original_book_chapter_prose_read", False), ("jacket_reference_only", True),
        ("jacket_image_binary_published", False), ("canonical_work_admissions", 0),
        ("accepted_edition_bindings", 0), ("coverage_effect", "NONE"),
        ("identity_reconciliation_effect", "NONE"), ("rights_status", "NOT_ESTABLISHED"),
    ):
        require(type(data[field]) is type(value) and data[field] == value, f"unsupported {field}")
    require(isinstance(opf_index, dict) and isinstance(opf_index.get("rows"), list) and
            opf_index.get("proposal_id") == "LIBRARIAN-PRIVATE-OPF-METADATA-20261103", "accepted OPF source missing")
    require(isinstance(txt_index, dict) and txt_index.get("proposal_id") ==
            "LIBRARIAN-PRIVATE-TXT51-100-20261103", "accepted TXT source missing")
    orig = {r["source_local_id"]: r for r in opf_index["rows"]}
    txt = {r["source_local_id"]: r for r in txt_index["records"]}
    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == 10, "crosswalk count")
    require(isinstance(data["records_sha256"], str) and SHA.fullmatch(data["records_sha256"]) and
            rowset_digest(rows) == data["records_sha256"], "rowset drift")
    for i, row in enumerate(rows):
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "unexpected row field")
        sid = EXPECTED_IDS[i]
        require(row["source_local_opf_id"] == sid, "source-local OPF identity changed")
        source = orig[sid]
        require(row["original_opf_entry_sha256"] == source["opf_entry_sha256"] and
                SHA.fullmatch(row["original_opf_entry_sha256"]), "original OPF fingerprint")
        require(type(row["original_opf_xml_bytes"]) is int and
                100 <= row["original_opf_xml_bytes"] <= 1_048_576, "source OPF XML length")
        require(row["opf_xml_parse_status"] == source["parse_status"], "unbound namespace repair hold removed")
        require(row["opf_title_claim"] == source["title"][0], "source title claim changed")
        require(row["opf_creator_claims"] == source["creator"], "source creator claim changed")
        require(row["opf_isbn10_claim"] in source["isbn_checksum_valid"], "source ISBN provenance")
        isbn = isbn13_from_isbn10(row["opf_isbn10_claim"])
        require(row["isbn13_computed_from_opf_isbn10"] == isbn, "ISBN10→13 conversion")
        require(row["official_product_title"] == EXPECTED_TITLES[i] and
                normalize_title(row["official_product_title"]) == normalize_title(row["opf_title_claim"]),
                "publisher title crosswalk")
        official_isbn = row["official_product_isbn13"]
        require(official_isbn == EXPECTED_ISBNS[i] and valid_isbn13(official_isbn), "official ISBN13")
        require(row["official_product_ebook"] is True, "official format")
        require(row["official_series_number"] == EXPECTED_BOOK_NUMBERS[i], "publisher series ordinal")
        url = row["official_product_page"]
        require(isinstance(url, str) and url.startswith("https://www.simonandschuster.com/books/") and
                url.endswith("/" + official_isbn) and url.count("//") == 1, "official product locator")
        require(row["official_jacket_jpg_reference_seen"] is True, "official jacket locator missing")
        authors = row["official_product_author_display"]
        require(isinstance(authors, list) and 1 <= len(authors) <= 3 and
                all(isinstance(a, str) and a and "/" not in a for a in authors), "publisher creator")
        if i == 0:
            require(row["edition_identifier_relation"] == "DIFFERENT_PRODUCT_IDENTIFIERS_HOLD" and
                    official_isbn != isbn, "omnibus ISBN conflict hidden")
            require(row["creator_relation"] == "AUTHOR_SET_DIFFERENCE_HOLD", "omnibus contributors conflict")
            require(row["bibliographic_role"] == "OMNIBUS_CONTAINER_CANDIDATE", "omnibus flattened to Work")
            require(row["original_txt_filename_candidate_id"] is None and
                    row["original_txt_candidate_basis"] == "NONE", "false omnibus TXT match")
        else:
            require(row["edition_identifier_relation"] == "ISBN10_13_CHECKDIGIT_MATCH" and
                    official_isbn == isbn, "publisher edition ISBN mismatch")
            require(row["bibliographic_role"] == "SINGLE_TITLE_EDITION_CANDIDATE", "false collection")
            expected_author_relation = "PUBLISHER_NAME_ORDER_REVERSED_HOLD" if sid == "opf-local:0052" else "CASEFOLD_NAME_MATCH"
            require(row["creator_relation"] == expected_author_relation, "creator claim overwritten")
            if expected_author_relation == "CASEFOLD_NAME_MATCH":
                require(len(authors) == 1 and authors[0].casefold() == row["opf_creator_claims"][0].casefold(),
                        "creator not actually aligned")
            tid = row["original_txt_filename_candidate_id"]
            require(isinstance(tid, str) and tid in txt, "TXT source-member hint missing")
            require(row["original_txt_candidate_basis"] == "FILENAME_TITLE_HINT_ONLY", "false TXT content match")
            require(normalize_title(txt[tid]["title_hint"]) ==
                    normalize_title(row["official_product_title"]), "TXT title hint disagrees")


if __name__ == "__main__":
    validate(json.loads(DATA.read_text(encoding="utf-8")),
             json.loads(OPF.read_text(encoding="utf-8")),
             json.loads(TXT.read_text(encoding="utf-8")))
    print("PASS: 9 publisher ISBN matches, one omnibus identifier HOLD; zero Work/edition admissions")
