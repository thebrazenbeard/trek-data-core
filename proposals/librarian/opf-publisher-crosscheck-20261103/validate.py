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
# SHA-256 of each fully reviewed row serialized as deterministic JSON. These
# constants are code-owned audit pins, not untrusted digests supplied by rows.
# Any changed synopsis, additional author, surprise field, URL, or uncertainty
# statement requires another source review and an explicit pin update.
REVIEWED_ROW_SHA256 = {
    "opf-local:0009": "63fefc4280e1192c88bf6941e126020968259bd664267b8bdae9030c4e23522b",
    "opf-local:0010": "2111dbd285f123e979c9d8ba2806083cc84ab26274dcc2d58db16a6bea6e735b",
    "opf-local:0015": "592eb46ccb555ecb25b77ceafa4e70aafce9ca69bfc9a1fa9afae79ebd45824e",
    "opf-local:0028": "851fae9ace5d7bb8d59e0c34cb919c65f0cdadf443dea00eb7748281d0897e5c",
    "opf-local:0029": "7eed396f03c9f6185c563a07d3c2883b873cda95122f8d9de0d6aa564a93e8f6",
    "opf-local:0031": "6a8224c63cab4dd1ebe44dd8275253dfa1eb4edb5d9795a68e373dc918c96ae6",
    "opf-local:0034": "e95ab831467f1a05e9629a7951159c6fa6effa748637cbdaeea8b93f25d42555",
    "opf-local:0050": "eb63a9d7b7440172e8b85d0f47d083ce64581df70614a84740ff6e9ce1792bca",
    "opf-local:0051": "017b76a51e530794038ea7cf29468bff699673d0cb85ba22d2c94e6e246ae7d7",
}

ENVELOPE_FIELDS = frozenset({
    "schema_version", "proposal_id", "source_observation_path", "source_observation_sha256",
    "publisher_source_family", "publisher_source_mode", "research_snapshot_date",
    "publisher_raw_html_sha256", "private_ebook_text_read", "private_book_paths_exported",
    "publisher_cover_bytes_exported", "private_source_equivalence_verified",
    "global_work_admission", "coverage_effect", "records",
})
ROW_FIELDS = frozenset({
    "opf_source_local_id", "opf_entry_sha256", "opf_isbn10", "isbn13_candidate",
    "publisher_locator", "publisher_title", "publisher_authors", "publisher_format",
    "publisher_isbn13", "publisher_publication_date", "crosscheck_state",
    "original_publisher_description_paraphrase", "uncertainty",
})
PRIVATE_PATH = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|(?:^|[\\/])(?:Users|home|mnt|AppData|OneDrive|workspace|tmp)[\\/]|file://)",
    re.IGNORECASE,
)


def forbid_private_paths(value: object, breadcrumb: str = "data") -> None:
    """Inspect recursively, including extra fields, before checking schema."""
    if isinstance(value, dict):
        for key, subvalue in value.items():
            require(isinstance(key, str), f"Nonstring key: {breadcrumb}")
            require(PRIVATE_PATH.search(key) is None, f"Private path embedded in key: {breadcrumb}")
            forbid_private_paths(subvalue, f"{breadcrumb}.{key}")
    elif isinstance(value, list):
        for index, subvalue in enumerate(value):
            forbid_private_paths(subvalue, f"{breadcrumb}[{index}]")
    elif isinstance(value, str):
        require(PRIVATE_PATH.search(value) is None, f"Private path string: {breadcrumb}")


def reviewed_digest(value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
    forbid_private_paths(data)
    require(set(data) == ENVELOPE_FIELDS, "Unexpected or missing top-level field")
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
    require(all(isinstance(row, dict) for row in records), "Unexpected row type")
    require(all(set(row) == ROW_FIELDS for row in records), "Unexpected or missing row field")
    require({row["opf_source_local_id"] for row in records} == set(EXPECTED), "Missing or duplicate or unreviewed OPF row")
    for row in records:
        ident = row["opf_source_local_id"]
        require(reviewed_digest(row) == REVIEWED_ROW_SHA256[ident],
                f"Unreviewed record mutation, synopsis, author or uncertainty: {ident}")
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
