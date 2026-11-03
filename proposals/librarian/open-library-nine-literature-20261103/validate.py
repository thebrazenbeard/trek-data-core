#!/usr/bin/env python3
"""Validate a held, source-local Open Library cover *proposal*, never release approval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
HEX = re.compile(r"[0-9a-f]{64}\Z")
ISBN = re.compile(r"[0-9]{13}\Z")
OLID = re.compile(r"OL[0-9]+M\Z")
ROOT_FIELDS = {
    "schema_version", "data_status", "accepted_source_effect", "accepted_work_effect",
    "accepted_binding_effect", "coverage_effect", "public_artwork_release_effect",
    "image_bytes_committed", "copyright_status", "source_catalog_commit",
    "source_catalog_path", "source_catalog_sha256", "literary_row_count",
    "candidate_count", "held_count", "observed_on", "cover_api_documentation",
    "cover_rights_caveat", "independence_assessment", "candidates", "held",
}
CANDIDATE_FIELDS = {
    "row_id", "publisher_title", "source_locator", "publisher_detail",
    "publisher_lineage", "publisher_source_input", "publisher_source_sha256",
    "isbn", "openlibrary_edition_id", "openlibrary_edition_title",
    "openlibrary_edition_subtitle", "openlibrary_edition_json_url",
    "edition_metadata_sha256", "cover_id", "cover_url", "attribution_url",
    "edition_json_get_status", "cover_head_status", "cover_head_content_type",
    "rights_status", "release_status",
}
HELD_FIELDS = {"row_id", "isbn", "openlibrary_edition_id", "edition_metadata_sha256", "reason"}
REJECTED_IMAGE_FIELDS = HELD_FIELDS | {
    "rejected_cover_id", "rejected_image_type", "review_evidence",
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        check(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda _s: check(False, "nonfinite JSON number"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_isbn13(value: object) -> bool:
    if type(value) is not str or not ISBN.fullmatch(value):
        return False
    return sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value)) % 10 == 0


def publisher_row_match(row: dict, item: dict) -> None:
    isbn = item["isbn"]
    check(valid_isbn13(isbn), "invalid edition ISBN-13")
    check(item["row_id"] == row["row_id"] and item["source_locator"] == row["source_locator"],
          "candidate row/source locator does not match accepted directory")
    check(item.get("publisher_title", row["title"]) == row["title"] and
          item.get("publisher_lineage", row["source_group"]) == row["source_group"] and
          item.get("publisher_source_input", row["source_input"]) == row["source_input"],
          "candidate publisher identity/lineage mismatch")
    check(row["medium"] == "LITERATURE" and row["verification_status"] == "UNVERIFIED_METADATA"
          and row["identity_scope"] == "SOURCE_LOCAL" and row["coverage_effect"] == "NONE"
          and row["admission_effect"] == "NONE", "non-literary or admitted target row")
    if row["source_group"] == "publisher:simonandschuster.com":
        check(row["source_locator"].startswith("https://www.simonandschuster.com/books/")
              and row["source_locator"].endswith("/" + isbn) and
              item["publisher_detail"] in row["details"] and
              item["publisher_detail"].endswith("ISBN " + isbn),
              "publisher product URL/edition details do not identify ISBN")
    elif row["source_group"] == "distributor:penguinrandomhouse.com:titan-books":
        check(row["candidate_kind"] == "FICTIONAL_MEMOIR" and
              re.fullmatch(r"https://www\.penguinrandomhouse\.com/books/[0-9]+/[a-z0-9-]+/",
                           row["source_locator"]) is not None and
              item["publisher_detail"] == "Paperback ISBN " + isbn and
              item["publisher_detail"] in row["details"],
              "distributor memoir product/ISBN detail mismatch")
    else:
        raise ValueError("unknown publisher lineage")


def validate(packet: dict, root: Path = ROOT) -> None:
    check(type(packet) is dict and set(packet) == ROOT_FIELDS, "proposal root contract mismatch")
    check(packet["schema_version"] == "1.0.0" and
          packet["data_status"] == "PROPOSAL_ONLY_INDEPENDENT_ARTWORK_REVIEW_REQUIRED" and
          packet["source_catalog_commit"] == "da44aecc4a44829c2cd8c969e80ade7d311c355d" and
          packet["source_catalog_path"] == "explorer/discovery-catalog.json", "unexpected source base")
    check(all(packet[key] == "NONE" for key in (
        "accepted_source_effect", "accepted_work_effect", "accepted_binding_effect",
        "coverage_effect", "public_artwork_release_effect")) and
          packet["image_bytes_committed"] is False and
          packet["copyright_status"] == "UNDERLYING_COVER_COPYRIGHT_UNRESOLVED" and
          packet["independence_assessment"] ==
          "OPEN_LIBRARY_MAY_REUSE_UPSTREAM_PUBLISHER_METADATA_NOT_INDEPENDENT_CANON_CORROBORATION",
          "proposal cannot claim release, license, admission or independent corroboration")
    check(packet["observed_on"] == "2026-11-03" and
          packet["cover_api_documentation"] == "https://openlibrary.org/dev/docs/api/covers" and
          packet["cover_rights_caveat"] == "https://openlibrary.org/developers/licensing",
          "unrecognized Open Library documentation")
    check(type(packet["candidates"]) is list and type(packet["held"]) is list and
          len(packet["candidates"]) == packet["candidate_count"] == 4 and
          len(packet["held"]) == packet["held_count"] == 5 and
          packet["literary_row_count"] == 9, "nine-row candidate/hold cardinality mismatch")
    check(type(packet["source_catalog_sha256"]) is str and
          HEX.fullmatch(packet["source_catalog_sha256"]) and
          sha256(root / packet["source_catalog_path"]) == packet["source_catalog_sha256"],
          "pinned accepted directory bytes mismatch")
    catalog = read_json(root / packet["source_catalog_path"])
    rows = {r["row_id"]: r for r in catalog["rows"] if r["medium"] == "LITERATURE"}
    check(len(rows) == 9 and len(catalog["rows"]) == catalog["row_count"] == 1214,
          "accepted directory source-local counts changed")
    seen = set()
    for item in packet["candidates"]:
        check(type(item) is dict and set(item) == CANDIDATE_FIELDS,
              "candidate fields must be exact and contain no image bytes")
        row_id = item["row_id"]
        check(type(row_id) is str and row_id in rows and row_id not in seen,
              "unknown or duplicate candidate row")
        seen.add(row_id)
        row = rows[row_id]
        publisher_row_match(row, item)
        path = item["publisher_source_input"]
        check(type(path) is str and path.startswith("proposals/librarian/") and
              type(item["publisher_source_sha256"]) is str and
              HEX.fullmatch(item["publisher_source_sha256"]) and
              sha256(root / path) == item["publisher_source_sha256"],
              "publisher source-input raw receipt mismatch")
        check(type(item["openlibrary_edition_id"]) is str and
              OLID.fullmatch(item["openlibrary_edition_id"]) and
              item["openlibrary_edition_json_url"] ==
              f'https://openlibrary.org/books/{item["openlibrary_edition_id"]}.json' and
              type(item["openlibrary_edition_title"]) is str and
              1 <= len(item["openlibrary_edition_title"]) <= 180 and
              (item["openlibrary_edition_subtitle"] is None or
               (type(item["openlibrary_edition_subtitle"]) is str and
                1 <= len(item["openlibrary_edition_subtitle"]) <= 180)),
              "Open Library edition ID/metadata locator invalid")
        check(type(item["edition_metadata_sha256"]) is str and
              HEX.fullmatch(item["edition_metadata_sha256"]) and
              type(item["cover_id"]) is int and 0 < item["cover_id"] < 100_000_000 and
              item["cover_url"] ==
              f'https://covers.openlibrary.org/b/id/{item["cover_id"]}-S.jpg?default=false' and
              item["attribution_url"] == f'https://openlibrary.org/isbn/{item["isbn"]}' and
              item["edition_json_get_status"] == item["cover_head_status"] == 200 and
              item["cover_head_content_type"] == "image/jpeg", "image metadata/attribution receipt invalid")
        check(item["rights_status"] == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" and
              item["release_status"] == "HELD_FOR_INDEPENDENT_REVIEW",
              "a proposed image cannot assert licensed display")
    for item in packet["held"]:
        check(type(item) is dict and set(item) ==
              (REJECTED_IMAGE_FIELDS if item.get("reason") == "IMAGE_VISUALLY_REJECTED_TITLE_PAGE"
               else HELD_FIELDS), "held row fields mismatch")
        row_id = item["row_id"]
        check(type(row_id) is str and row_id in rows and row_id not in seen,
              "unknown or duplicate held row")
        seen.add(row_id)
        publisher_row_match(rows[row_id], {
            "row_id": row_id, "isbn": item["isbn"],
            "source_locator": rows[row_id]["source_locator"],
            "publisher_detail": next(d for d in rows[row_id]["details"] if "ISBN " + item["isbn"] in d),
        })
        if item["reason"] == "IMAGE_VISUALLY_REJECTED_TITLE_PAGE":
            check(row_id == "literature:proposed-lit-discovery-enterprise-war" and
                  item["isbn"] == "9781982113315" and
                  item["openlibrary_edition_id"] == "OL28720619M" and
                  item["edition_metadata_sha256"] ==
                  "ecaca36ebb2419de7d96214f8ed8145c13bf1d90a20d0e72ac62e71090425208" and
                  type(item["rejected_cover_id"]) is int and
                  item["rejected_cover_id"] == 12857937 and
                  item["rejected_image_type"] == "INTERIOR_TITLE_PAGE_NOT_BOOK_JACKET" and
                  item["review_evidence"] ==
                  "INDEPENDENT_AUDITOR_BROWSER_VISUAL_INSPECTION_2026-11-03",
                  "visually rejected title page cannot be offered as jacket artwork")
        elif item["reason"] == "EDITION_JSON_200_WITHOUT_COVERS":
            check(type(item["openlibrary_edition_id"]) is str and
                  OLID.fullmatch(item["openlibrary_edition_id"]) and
                  type(item["edition_metadata_sha256"]) is str and
                  HEX.fullmatch(item["edition_metadata_sha256"]),
                  "missing no-cover metadata receipt")
        else:
            check(item["reason"] == "ISBN_JSON_RETURNED_404_AT_OBSERVATION" and
                  item["openlibrary_edition_id"] is None and
                  item["edition_metadata_sha256"] is None,
                  "404 hold must not invent an edition or metadata digest")
    check(seen == set(rows), "not all nine literary source-local rows were classified")


def main() -> int:
    try:
        validate(read_json(PACKET))
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f"OPEN_LIBRARY_CROSSWALK_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("OPEN_LIBRARY_CROSSWALK_PROPOSAL_OK: 4 jacket candidates; 5 held; 0 released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
