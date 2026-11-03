#!/usr/bin/env python3
"""Fail-closed metadata-only checks; this does not admit a private edition."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
EXPECTED = {
    "opf-local:0009": ("9780743439961", "9780743439978", "HELD_PUBLISHER_DIFFERENT_ISBN_FORMAT"),
    "opf-local:0010": ("9780743419017", "9780743419017", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0015": ("9780743444125", "9780743448475", "HELD_PUBLISHER_DIFFERENT_ISBN_FORMAT"),
    "opf-local:0028": ("9780743456722", "9780743456722", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0029": ("9780743456739", "9780743456739", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0031": ("9780743456753", "9780743456753", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0034": ("9780743456784", "9780743456784", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0050": ("9780743412131", "9780743412131", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
    "opf-local:0051": ("9780743412148", "9780743412148", "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"),
}
REVIEWED_PUBLISHER_METADATA = {
    "opf-local:0009": ("Have Tech Will Travel", "Keith R. A. DeCandido", "Have-Tech-Will-Travel/Keith-R-A-DeCandido/Star-Trek-Starfleet-Corps-of-Engineers", None),
    "opf-local:0010": ("Star Trek: The Belly of the Beast", "Dean Wesley Smith", "Star-Trek-The-Belly-of-the-Beast/Dean-Wesley-Smith/Star-Trek-Starfleet-Corps-of-Engineers", "2000-08-08"),
    "opf-local:0015": ("Miracle Workers, S.C.E. Book Two", "Keith R. A. DeCandido", "Miracle-Workers-S-C-E-Book-Two/Keith-R-A-DeCandido/Star-Trek-Starfleet-Corps-of-Engineers", "2002-03-14"),
    "opf-local:0028": ("Star Trek: Corps of Engineers: Foundations #1", "Dayton Ward", "Star-Trek-Corps-of-Engineers-Foundations-1/Dayton-Ward/Star-Trek-Starfleet-Corps-of-Engineers", "2002-06-14"),
    "opf-local:0029": ("Star Trek: Corps of Engineers: Foundations #2", "Dayton Ward", "Star-Trek-Corps-of-Engineers-Foundations-2/Dayton-Ward/Star-Trek-Starfleet-Corps-of-Engineers", "2002-07-15"),
    "opf-local:0031": ("Enigma Ship", "J. Steven York", "Enigma-Ship/J-Steven-York/Star-Trek-Starfleet-Corps-of-Engineers", "2002-09-23"),
    "opf-local:0034": ("Wildfire Book 1", "David Mack", "Wildfire-Book-1/David-Mack/Star-Trek-Starfleet-Corps-of-Engineers", "2003-01-02"),
    "opf-local:0050": ("Ghost Ship", "Diane Carey", "Ghost-Ship/Diane-Carey/Star-Trek-The-Next-Generation", "2000-05-23"),
    "opf-local:0051": ("The Peacekeepers", "Gene DeWeese", "The-Peacekeepers/Gene-DeWeese/Star-Trek-The-Next-Generation", "2000-05-23"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path) -> dict:
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate)


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Malformed source ISBN-10")
    require(sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(value)) % 11 == 0,
            "Invalid source ISBN-10 checksum")
    core = "978" + value[:9]
    digit = (-sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(core))) % 10
    return core + str(digit)


def isbn13_valid(value: str) -> bool:
    return (isinstance(value, str) and bool(re.fullmatch(r"[0-9]{13}", value))
            and sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value)) % 10 == 0)


def validate(data: dict, source: dict, source_bytes: bytes) -> None:
    require(data["schema_version"] == 1, "Wrong crosscheck schema version")
    require(data["proposal_id"] == "opf-first-nine-publisher-edition-check-20261103", "Wrong proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json", "Wrong source path")
    require(data["source_observation_sha256"] == hashlib.sha256(source_bytes).hexdigest(), "Source observation digest drift")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek", "Source lineage drift")
    require(data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY", "Source access overstated")
    require(data["research_snapshot_date"] == "2026-11-03", "Unreviewed snapshot date")
    require(data["publisher_raw_html_sha256"] is None, "Raw publisher webpage custody not established")
    require(all(data[k] is False for k in ("private_ebook_text_read", "private_book_paths_exported",
            "publisher_cover_bytes_exported", "private_source_equivalence_verified")), "Unsupported private-file claim")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE", "Forbidden admission/coverage")
    require(source["edition_binding_verified"] is False and source["ebook_full_text_read"] is False,
            "Private observation source semantics changed")
    observed = {row["source_local_id"]: row for row in source["rows"]}
    records = data["records"]
    require(len(records) == len(EXPECTED), "Wrong bounded row count")
    require({row["opf_source_local_id"] for row in records} == set(EXPECTED), "Missing or duplicate or unreviewed OPF row")
    for row in records:
        ident = row["opf_source_local_id"]
        local = observed[ident]
        candidate, publisher, expected_state = EXPECTED[ident]
        reviewed_title, reviewed_author, reviewed_path, reviewed_date = REVIEWED_PUBLISHER_METADATA[ident]
        require(row["opf_entry_sha256"] == local["opf_entry_sha256"], f"OPF observation digest mismatch: {ident}")
        require(row["opf_isbn10"] in local["isbn_checksum_valid"], f"OPF ISBN not recorded: {ident}")
        require(isbn13_from_10(row["opf_isbn10"]) == row["isbn13_candidate"] == candidate,
                f"ISBN10 conversion wrong: {ident}")
        require(row["publisher_isbn13"] == publisher and isbn13_valid(publisher), f"Publisher ISBN mismatch: {ident}")
        require(row["publisher_title"] == reviewed_title
                and row["publisher_authors"][0] == reviewed_author
                and row["publisher_publication_date"] == reviewed_date,
                f"Publisher title, lead author or publication date drift: {ident}")
        require(row["crosscheck_state"] == expected_state, f"Unreviewed reconciliation status: {ident}")
        parsed = urlparse(row["publisher_locator"])
        require(parsed.scheme == "https" and parsed.netloc == "www.simonandschuster.com"
                and parsed.path == f"/books/{reviewed_path}/{publisher}"
                and not (parsed.params or parsed.query or parsed.fragment), f"Invalid first-party locator: {ident}")
        require(row["publisher_format"] == "eBook", f"Unreviewed publisher format: {ident}")
        require(isinstance(row["publisher_title"], str) and bool(row["publisher_title"].strip()),
                f"Missing catalog title: {ident}")
        require(isinstance(row["publisher_authors"], list) and row["publisher_authors"]
                and all(isinstance(author, str) and author.strip() for author in row["publisher_authors"]),
                f"Missing catalog authors: {ident}")
        require(isinstance(row["uncertainty"], str) and len(row["uncertainty"]) > 25,
                f"Missing evidence-boundary note: {ident}")
        synopsis = row["original_publisher_description_paraphrase"]
        if expected_state.startswith("HELD_"):
            require(candidate != publisher and synopsis is None, f"Held case promoted: {ident}")
        else:
            require(candidate == publisher and isinstance(synopsis, str) and 25 <= len(synopsis) <= 280,
                    f"Matched publisher metadata/paraphrase missing: {ident}")
            require(isinstance(row["publisher_publication_date"], str)
                    and bool(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", row["publisher_publication_date"])),
                    f"Missing publisher date: {ident}")


if __name__ == "__main__":
    source_bytes = SOURCE.read_bytes()
    validate(load(ROOT / "records.json"), load(SOURCE), source_bytes)
    print("PASS: 9 source-local OPF ISBN crosschecks; 7 publisher metadata matches, 2 held; no admission or coverage")
