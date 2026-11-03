#!/usr/bin/env python3
"""Metadata-only fourth OPF tranche. Validity does not admit private editions."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OLDER = tuple(REPO / f"proposals/librarian/{name}/records.json" for name in (
    "opf-publisher-crosscheck-20261103",
    "opf-publisher-crosscheck-next-ten-20261103",
    "opf-publisher-crosscheck-third-ten-20261103",
))
# Independently accepted main crosswalk #345 (merged while this draft was in flight).
ACCEPTED_345_SOURCE_IDS = frozenset(f"opf-local:{number:04d}" for number in range(76, 80))
MATCH = "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"
HELD = "HELD_PUBLISHER_PARAPHRASE_NO_PRIVATE_TEXT"
EXPECTED = {
    "opf-local:0073": ("9780743421089", "Grounded", ("David Bischoff",), "Grounded/David-Bischoff"),
    "opf-local:0082": ("9780743421232", "Blaze of Glory", ("Simon Hawke",), "Blaze-of-Glory/Simon-Hawke"),
    "opf-local:0084": ("9780743421379", "Into the Nebula", ("Gene DeWeese",), "Into-the-Nebula/Gene-DeWeese"),
    "opf-local:0085": ("9780743421393", "The Last Stand", ("Brad Ferguson",), "The-Last-Stand/Brad-Ferguson"),
    "opf-local:0087": ("9780743421164", "Rogue Saucer", ("John Vornholt",), "Rogue-Saucer/John-Vornholt"),
    "opf-local:0088": ("9780743421171", "Possession", ("J.M. Dillard", "Kathleen O'malley"), "Possession/J-M-Dillard"),
}
PIN = {
    "opf-local:0073": "fbe1e767182ff5be856ee2c749dc0ac2b209abab2826a660c13de558b6e51e7f",
    "opf-local:0082": "731964c07a549928914b266339e9e3a6f9c06d700ba722035a70ce894ffd4341",
    "opf-local:0084": "342cd636afa4db303115a7413b527aed5a8ead16ea7add758b3b6a3dd7aa1fd6",
    "opf-local:0085": "aeda58453d58888c343c4ebceb6951186c3032357c09e9f2bc519690ad953fc7",
    "opf-local:0087": "e254cf2264db4f1dfef408043e8387181979eb3be8c362879986d8c0fe705341",
    "opf-local:0088": "585787f5f05b249cf5c7d8caa43ce030d015dfb1e50b07401bb8789b0d39cc6d",
}
ENVELOPE = frozenset({
    "schema_version", "proposal_id", "source_observation_path", "source_observation_sha256",
    "publisher_source_family", "publisher_source_mode", "research_snapshot_date",
    "publisher_raw_html_sha256", "private_ebook_text_read", "private_book_paths_exported",
    "publisher_cover_bytes_exported", "private_source_equivalence_verified",
    "global_work_admission", "coverage_effect", "records",
})
ROW = frozenset({
    "opf_source_local_id", "opf_entry_sha256", "opf_isbn10", "isbn13_candidate",
    "publisher_locator", "publisher_title", "publisher_authors", "publisher_format",
    "publisher_isbn13", "publisher_publication_date", "crosscheck_state",
    "synopsis_review_state", "original_publisher_description_paraphrase", "uncertainty",
})
PRIVATE_PATH = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|(?:^|[\\/])(?:Users|home|mnt|AppData|OneDrive|workspace|tmp)[\\/]|file://)",
    re.IGNORECASE,
)


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def load(path: Path) -> dict:
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate)


def forbid_private_paths(value: object, location: str = "data") -> None:
    if isinstance(value, dict):
        for key, v in value.items():
            require(isinstance(key, str) and PRIVATE_PATH.search(key) is None,
                    f"Private/malformed key at {location}")
            forbid_private_paths(v, f"{location}.{key}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            forbid_private_paths(v, f"{location}[{i}]")
    elif isinstance(value, str):
        require(PRIVATE_PATH.search(value) is None, f"Private path in {location}")


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Invalid ISBN10 structure")
    require(sum((10-i) * (10 if x == "X" else int(x)) for i, x in enumerate(value)) % 11 == 0,
            "Invalid ISBN10 checksum")
    core = "978" + value[:9]
    last = (-sum((1 if i % 2 == 0 else 3) * int(x) for i, x in enumerate(core))) % 10
    return core + str(last)


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate(data: dict, observations: dict, source_bytes: bytes, older: tuple[dict, ...]) -> None:
    forbid_private_paths(data)
    require(isinstance(data, dict) and set(data) == ENVELOPE,
            "Unexpected/missing envelope fields")
    require(data["schema_version"] == 1 and data["proposal_id"] == "opf-fourth-six-publisher-edition-crosscheck-20261103",
            "Unexpected proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json"
            and data["source_observation_sha256"] == hashlib.sha256(source_bytes).hexdigest()
            == "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7",
            "Upstream OPF snapshot drift")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek"
            and data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY"
            and data["publisher_raw_html_sha256"] is None,
            "Unsupported publisher raw custody")
    require(data["research_snapshot_date"] == "2026-11-03", "Unreviewed date")
    require(all(data[k] is False for k in (
        "private_ebook_text_read", "private_book_paths_exported",
        "publisher_cover_bytes_exported", "private_source_equivalence_verified")),
        "Private source access/equivalence overclaim")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE",
            "Forbidden Work/coverage promotion")
    require(observations["ebook_full_text_read"] is False and observations["edition_binding_verified"] is False,
            "Upstream source evidence boundary drift")
    require(len(older) == 3 and [len(p["records"]) for p in older] == [9, 10, 10],
            "Previous publisher batches changed")
    previous_ids = {r["opf_source_local_id"] for p in older for r in p["records"]}
    require(previous_ids.isdisjoint(EXPECTED), "Duplicate source-local ID against accepted publisher tranches")
    require(ACCEPTED_345_SOURCE_IDS.isdisjoint(EXPECTED),
            "Duplicate source-local ID against accepted #345 OPF crosswalk")
    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == 6
            and all(isinstance(r, dict) and set(r) == ROW for r in rows),
            "Unexpected records/schema")
    ids = [r["opf_source_local_id"] for r in rows]
    require(len(ids) == len(set(ids)) and set(ids) == set(EXPECTED), "Bad OPF source-local set")
    source = {r["source_local_id"]: r for r in observations["rows"]}
    for row in rows:
        ident = row["opf_source_local_id"]
        isbn, title, authors, slug = EXPECTED[ident]
        require(digest(row) == PIN[ident], f"Unreviewed row/prose mutation: {ident}")
        require(row["opf_entry_sha256"] == source[ident]["opf_entry_sha256"]
                and row["opf_isbn10"] in source[ident]["isbn_checksum_valid"],
                f"Changed source OPF evidence: {ident}")
        require(isbn13_from_10(row["opf_isbn10"]) == row["isbn13_candidate"]
                == row["publisher_isbn13"] == isbn, f"Bad ISBN mapping: {ident}")
        parsed = urlparse(row["publisher_locator"])
        require(parsed.scheme == "https" and parsed.netloc == "www.simonandschuster.com"
                and parsed.path == f"/books/{slug}/Star-Trek-The-Next-Generation/{isbn}"
                and not (parsed.params or parsed.query or parsed.fragment),
                f"Unreviewed official publisher locator: {ident}")
        require(row["publisher_title"] == title and row["publisher_authors"] == list(authors)
                and row["publisher_format"] == "eBook"
                and row["publisher_publication_date"] == "2000-09-22"
                and row["crosscheck_state"] == MATCH and row["synopsis_review_state"] == HELD,
                f"Publisher attribution/held state drift: {ident}")
        require(isinstance(row["original_publisher_description_paraphrase"], str)
                and 35 <= len(row["original_publisher_description_paraphrase"]) <= 280
                and isinstance(row["uncertainty"], str) and len(row["uncertainty"]) >= 45,
                f"Missing bounded candidate description: {ident}")


if __name__ == "__main__":
    raw = SOURCE.read_bytes()
    validate(load(ROOT / "records.json"), load(SOURCE), raw, tuple(load(p) for p in OLDER))
    print("PASS: six new first-party eBook ISBN metadata crosschecks, six synopsis candidates held, no private edition/Work/coverage")
