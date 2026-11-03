#!/usr/bin/env python3
"""Fail-closed first-party OPF metadata crosscheck; not private-book admission."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
PREVIOUS = tuple(REPO / "proposals/librarian" / name / "records.json" for name in (
    "opf-publisher-crosscheck-20261103",
    "opf-publisher-crosscheck-next-ten-20261103",
    "opf-publisher-crosscheck-third-ten-20261103",
    "opf-publisher-crosscheck-fourth-six-20261103",
    "tng-opf-0076-0079-publisher-crosswalk-20261103",
))
SOURCE_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
MATCH = "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"
MISMATCH = "TITLE_AUTHOR_PRODUCT_MATCH_ISBN_EDITION_MISMATCH_UNRESOLVED"
HELD = "HELD_PUBLISHER_PARAPHRASE_NO_PRIVATE_TEXT"
ENVELOPE = frozenset((
    "schema_version", "proposal_id", "research_snapshot_date", "source_observation_path",
    "source_observation_sha256", "publisher_source_family", "publisher_source_mode",
    "publisher_raw_html_sha256", "private_ebook_text_read", "private_book_paths_exported",
    "publisher_cover_bytes_exported", "private_source_equivalence_verified", "global_work_admission",
    "coverage_effect", "records",
))
FIELDS = frozenset((
    "opf_source_local_id", "opf_entry_sha256", "opf_title", "opf_creator", "opf_metadata_date",
    "opf_isbn10", "isbn13_candidate", "publisher_locator", "publisher_title", "publisher_authors",
    "publisher_format", "publisher_isbn13", "publisher_publication_date", "publisher_pages",
    "publisher_series_number", "crosscheck_state", "synopsis_review_state",
    "original_publisher_description_paraphrase", "uncertainty",
))
EXPECTED = {
    "opf-local:0090": (
        "9f3e9472ff7685f5436d2b7052d794da9d07b91235a57caf4b7263fcb7a619a5",
        "A FURY SCORNED", "PAMELA SARGENT AND GEORGE ZEBROWSKI", "0743421213",
        "9780743421218", "Star Trek: The Next Generation: A Fury Scorned",
        ("Pamela Sargent", "George Zebrowski"), 288, 43,
        "Star-Trek-The-Next-Generation-A-Fury-Scorned/Pamela-Sargent", MATCH,
    ),
    "opf-local:0091": (
        "11d97f45a723d8dd0dad9adb517027b5a4b183b18ca8216ff667d05512ed25ab",
        "THE DEATH OF PRINCES", "JOHN PEEL", "0743421221",
        "9780743422888", "The Death of Princes", ("John Peel",), 304, 44,
        "The-Death-of-Princes/John-Peel", MISMATCH,
    ),
    "opf-local:0092": (
        "bc9ab5d3e99f28d15c6cdcba53574370092120dbce144a4f4a78d6ce095c4b3d",
        "INTELLIVORE", "DIANE DUANE", "0743421248",
        "9780743421249", "Intellivore", ("Diane Duane",), 272, 45,
        "Intellivore/Diane-Duane", MATCH,
    ),
}
# Hashes pin the reviewed original paraphrases and specific uncertainty wording as well as metadata.
PIN = {
    "opf-local:0090": "b2fc471085490c87046f8a630223e05e97ff9596bae13df97b860ff22caee2f0",
    "opf-local:0091": "c85859fbe79a4816c41abfd17202656cbf32a39438946106492bc077ad4b04b1",
    "opf-local:0092": "7b1d2fa70e62dcbb0c235757b51389a652c394c2912726edb7ae7e5126db761a",
}
PRIVATE_PATH = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|(?:^|[\\/])(?:Users|home|mnt|AppData|OneDrive|workspace|tmp)[\\/]|file://)",
    re.IGNORECASE,
)


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def load(path: Path) -> dict:
    def reject_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_pairs)


def forbid_private_paths(obj: object, location: str = "record") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            require(isinstance(key, str) and not PRIVATE_PATH.search(key), f"Bad key in {location}")
            forbid_private_paths(value, f"{location}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            forbid_private_paths(value, f"{location}[{index}]")
    elif isinstance(obj, str):
        require(not PRIVATE_PATH.search(obj), f"Private path leaked at {location}")


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Malformed ISBN10")
    require(sum((10 - i) * (10 if ch == "X" else int(ch)) for i, ch in enumerate(value)) % 11 == 0,
            "Invalid ISBN10 check digit")
    core = "978" + value[:9]
    check = -sum((1 if i % 2 == 0 else 3) * int(ch) for i, ch in enumerate(core)) % 10
    return core + str(check)


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate(data: dict, obs: dict, source_bytes: bytes, previous: tuple[dict, ...]) -> None:
    forbid_private_paths(data)
    require(isinstance(data, dict) and set(data) == ENVELOPE, "Unexpected envelope schema")
    require(data["schema_version"] == 1 and data["proposal_id"] == "tng-opf-0090-0092-publisher-editions-20261103"
            and data["research_snapshot_date"] == "2026-11-03", "Unexpected proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json"
            and data["source_observation_sha256"] == hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA,
            "Source snapshot not pinned")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek"
            and data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY"
            and data["publisher_raw_html_sha256"] is None, "Publisher custody overclaim")
    for key in ("private_ebook_text_read", "private_book_paths_exported",
                "publisher_cover_bytes_exported", "private_source_equivalence_verified"):
        require(data[key] is False, f"Forbidden custody/rights assertion: {key}")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE",
            "Forbidden global Work/coverage effect")
    require(obs["ebook_full_text_read"] is False and obs["edition_binding_verified"] is False,
            "Upstream private text evidence changed")
    existing = set()
    for old in previous:
        for row in old["records"]:
            identifier = row.get("opf_source_local_id") or row.get("source_local_id")
            if identifier:
                existing.add(identifier)
    require(set(EXPECTED).isdisjoint(existing), "Already accepted a conflicting OPF crosscheck")
    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == len(EXPECTED), "Unexpected tranche size")
    require(all(isinstance(row, dict) and set(row) == FIELDS for row in rows), "Unexpected row schema")
    identifiers = [row["opf_source_local_id"] for row in rows]
    require(len(identifiers) == len(set(identifiers)) and set(identifiers) == set(EXPECTED),
            "Duplicate or wrong source-local IDs")
    upstream = {row["source_local_id"]: row for row in obs["rows"]}
    for row in rows:
        identifier = row["opf_source_local_id"]
        sha, title, creator, isbn10, pub_isbn, pub_title, authors, pages, series_number, slug, status = EXPECTED[identifier]
        source_row = upstream[identifier]
        expected_opf_date = "2000-07-31" if identifier == "opf-local:0092" else "2000-08-05"
        require(row["opf_entry_sha256"] == source_row["opf_entry_sha256"] == sha
                and source_row["title"] == [row["opf_title"]] == [title]
                and source_row["creator"] == [row["opf_creator"]] == [creator]
                and row["opf_metadata_date"] == source_row["date"][0] == expected_opf_date,
                f"Upstream OPF provenance mismatch: {identifier}")
        require(row["opf_isbn10"] == isbn10 and isbn10 in source_row["isbn_checksum_valid"]
                and row["isbn13_candidate"] == isbn13_from_10(isbn10), "OPF ISBN computation error")
        require(row["publisher_isbn13"] == pub_isbn and row["publisher_title"] == pub_title
                and row["publisher_authors"] == list(authors)
                and row["publisher_format"] == "eBook"
                and row["publisher_publication_date"] == "2000-09-22"
                and type(row["publisher_pages"]) is int and row["publisher_pages"] == pages
                and type(row["publisher_series_number"]) is int and row["publisher_series_number"] == series_number,
                f"Unreviewed publisher metadata: {identifier}")
        url = urlparse(row["publisher_locator"])
        require(url.scheme == "https" and url.netloc == "www.simonandschuster.com"
                and url.path == f"/books/{slug}/Star-Trek-The-Next-Generation/{pub_isbn}"
                and not (url.query or url.params or url.fragment), f"Invalid publisher source: {identifier}")
        require(row["crosscheck_state"] == status and row["synopsis_review_state"] == HELD,
                f"Unreviewed crosscheck/held state: {identifier}")
        if status == MATCH:
            require(row["isbn13_candidate"] == pub_isbn, "ISBN equality required for metadata match")
        else:
            require(row["isbn13_candidate"] != pub_isbn, "ISBN mismatch must remain unresolved")
        require(isinstance(row["original_publisher_description_paraphrase"], str)
                and 50 <= len(row["original_publisher_description_paraphrase"]) <= 280
                and isinstance(row["uncertainty"], str) and len(row["uncertainty"]) >= 80,
                f"Unreviewed candidate synopsis/uncertainty: {identifier}")
        require(digest(row) == PIN[identifier], f"Unreviewed row content mutation: {identifier}")


if __name__ == "__main__":
    validate(load(ROOT / "records.json"), load(SOURCE), SOURCE.read_bytes(), tuple(load(p) for p in PREVIOUS))
    print("PASS: 3 source-first TNG publisher crosschecks; 2 matching ISBN metadata, 1 explicit edition mismatch; no global effect")
