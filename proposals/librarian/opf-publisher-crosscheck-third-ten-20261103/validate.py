#!/usr/bin/env python3
"""Fail-closed source-only publisher checks; no private edition admission."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OLDER = (
    REPO / "proposals/librarian/opf-publisher-crosscheck-20261103/records.json",
    REPO / "proposals/librarian/opf-publisher-crosscheck-next-ten-20261103/records.json",
)
MATCH = "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"
SPELL = "PUBLISHER_ISBN_MATCH_TITLE_SPELLING_CONFLICT_UNRESOLVED"
EXPECTED = {
    "opf-local:0062": ("9780743420945", "Exiles/Howard-Weinstein", MATCH),
    "opf-local:0063": ("9780743420952", "Fortunes-Light/Michael-Jan-Friedman", MATCH),
    "opf-local:0064": ("9780743420969", "Contamination/John-Vornholt", MATCH),
    "opf-local:0065": ("9780743420976", "Boogeymen/Mel-Gilden", MATCH),
    "opf-local:0067": ("9780743420990", "Perchance-to-Dream/Howard-Weinstein", SPELL),
    "opf-local:0068": ("9780743421003", "Spartacus/T-L-Mancour", MATCH),
    "opf-local:0069": ("9780743421010", "Chains-of-Command/W-A-McCay", MATCH),
    "opf-local:0070": ("9780743421027", "Imbalance/V-E-Mitchell", MATCH),
    "opf-local:0074": ("9780743421096", "The-Romulan-Prize/Simon-Hawke", MATCH),
    "opf-local:0075": ("9780743421102", "Guises-of-the-Mind/Rebecca-Neason", MATCH),
}
REVIEWED_ROW_SHA256 = {
    "opf-local:0062": "dd8f779170144ef30e014010cfecc31f194617ab9ef2b6d53c412048866bdfc0",
    "opf-local:0063": "f80498ebae84ffc0e718bc4cab6a5d74edb64564a4f08785dab9d93b0db43b25",
    "opf-local:0064": "3917364b2606bb9d56d171254b90431be69caae900a5e6031ae123dac11d10c7",
    "opf-local:0065": "339721b84ed264c46952e212254038bae9fe394cff02d272439d723cc5095572",
    "opf-local:0067": "598e5a6c7c0897b5d3de16acc60db1cc7c23369f7ac78de090125e7584f3aa77",
    "opf-local:0068": "e6b18d1f4c1385020eb4856f78328c5e90014e6894feabe296cd60c7a3be1c0d",
    "opf-local:0069": "017ee08803f8cbe4581c13d959a9d4044094a7fedb5a70a6a851d88166d68aef",
    "opf-local:0070": "a20fa8e1621431162fa31c983fadf10193d38caf89e5d34e8a6571e2bfeef2d8",
    "opf-local:0074": "437b36d59fa3f6d05dad477a3f0adbfd8fde6a38a4cb1f934e73e03f153f1555",
    "opf-local:0075": "0560cebe6d09d19701e43a7ef09bfee8a91f17c5cec740cefb3ab98d6617c004",
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
    "original_publisher_description_paraphrase", "uncertainty",
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
        out = {}
        for key, value in pairs:
            require(key not in out, f"Duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate)


def forbid_private_paths(value: object, breadcrumb: str = "data") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(isinstance(key, str) and PRIVATE_PATH.search(key) is None,
                    f"Malformed/private JSON key at {breadcrumb}")
            forbid_private_paths(child, f"{breadcrumb}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            forbid_private_paths(child, f"{breadcrumb}[{i}]")
    elif isinstance(value, str):
        require(PRIVATE_PATH.search(value) is None, f"Private path at {breadcrumb}")


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Invalid source ISBN10 format")
    require(sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(value)) % 11 == 0,
            "Invalid source ISBN10 checksum")
    core = "978" + value[:9]
    digit = (-sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(core))) % 10
    return core + str(digit)


def digest(row: dict) -> str:
    canonical = json.dumps(row, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate(data: dict, source: dict, source_bytes: bytes, predecessors: tuple[dict, dict]) -> None:
    forbid_private_paths(data)
    require(isinstance(data, dict) and set(data) == ENVELOPE, "Unexpected envelope fields")
    require(data["schema_version"] == 1 and data["proposal_id"] == "opf-third-ten-publisher-edition-crosscheck-20261103",
            "Unexpected proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json"
            and data["source_observation_sha256"] == hashlib.sha256(source_bytes).hexdigest()
            == "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7",
            "Source observation changed")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek"
            and data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY"
            and data["publisher_raw_html_sha256"] is None,
            "Publisher provenance/custody overstated")
    require(data["research_snapshot_date"] == "2026-11-03", "Source date drift")
    require(all(data[k] is False for k in ("private_ebook_text_read", "private_book_paths_exported",
                                            "publisher_cover_bytes_exported", "private_source_equivalence_verified")),
            "Private source effect invented")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE",
            "Forbidden Work/coverage promotion")
    require(source["ebook_full_text_read"] is False and source["edition_binding_verified"] is False,
            "Source OPF source boundary changed")
    old_ids = {record["opf_source_local_id"] for old in predecessors for record in old["records"]}
    require(len(predecessors[0]["records"]) == 9 and len(predecessors[1]["records"]) == 10
            and old_ids.isdisjoint(EXPECTED), "Reused previous local OPF ID")
    records = data["records"]
    require(isinstance(records, list) and len(records) == 10 and
            all(isinstance(row, dict) and set(row) == ROW for row in records),
            "Unexpected record set/schema")
    ids = [row["opf_source_local_id"] for row in records]
    require(len(ids) == len(set(ids)) and set(ids) == set(EXPECTED),
            "Unexpected/duplicate OPF IDs")
    opf = {row["source_local_id"]: row for row in source["rows"]}
    for row in records:
        ident = row["opf_source_local_id"]
        isbn, slug, state = EXPECTED[ident]
        require(digest(row) == REVIEWED_ROW_SHA256[ident], f"Unreviewed row/prose edit: {ident}")
        require(row["opf_entry_sha256"] == opf[ident]["opf_entry_sha256"]
                and row["opf_isbn10"] in opf[ident]["isbn_checksum_valid"],
                f"Wrong source OPF entry: {ident}")
        require(isbn13_from_10(row["opf_isbn10"]) == row["isbn13_candidate"]
                == row["publisher_isbn13"] == isbn, f"Wrong ISBN conversion: {ident}")
        u = urlparse(row["publisher_locator"])
        require(u.scheme == "https" and u.netloc == "www.simonandschuster.com"
                and u.path == f"/books/{slug}/Star-Trek-The-Next-Generation/{isbn}"
                and not (u.params or u.query or u.fragment), f"Wrong publisher locator: {ident}")
        require(row["publisher_format"] == "eBook"
                and row["publisher_publication_date"] == "2000-09-22"
                and isinstance(row["publisher_authors"], list) and row["publisher_authors"]
                and row["crosscheck_state"] == state,
                f"Unreviewed edition metadata: {ident}")
        require(isinstance(row["original_publisher_description_paraphrase"], str)
                and 35 <= len(row["original_publisher_description_paraphrase"]) <= 280
                and isinstance(row["uncertainty"], str) and len(row["uncertainty"]) >= 45,
                f"Missing synopsis boundary: {ident}")
        if ident == "opf-local:0067":
            require(opf[ident]["title"] == ["PRECHANCE TO DREAM"]
                    and row["publisher_title"] == "Perchance to Dream",
                    "OPF/publisher spelling difference lost")


if __name__ == "__main__":
    raw = SOURCE.read_bytes()
    validate(load(ROOT / "records.json"), load(SOURCE), raw,
             (load(OLDER[0]), load(OLDER[1])))
    print("PASS: ten new OPF ISBN / first-party eBook catalog comparisons, one source-title conflict held, zero Work/edition/coverage")
