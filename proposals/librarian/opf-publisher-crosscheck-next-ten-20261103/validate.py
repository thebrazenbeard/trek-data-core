#!/usr/bin/env python3
"""Fail-closed source-only OPF ↔ rendered publisher metadata crosschecks.

No validation here proves private ebook contents, canonical Work identity, or
raw publisher page custody. Code-owned row hashes guard the reviewed snapshot;
they are not cryptographic attestation of a publisher website.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OLDER = REPO / "proposals/librarian/opf-publisher-crosscheck-20261103/records.json"

# ISBN, source-specific title, official publisher author list, URL product path,
# date and explicit status are pinned to the publisher-first reviewed pages.
MATCH = "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED"
CONFLICT = "PUBLISHER_ISBN_MATCH_CREATOR_RENDERING_CONFLICT_UNRESOLVED"
EXPECTED = {
    "opf-local:0052": ("9780743412155", "The Children of Hamlin", ("Carter Carmen",), "The-Children-of-Hamlin/Carter-Carmen", "2000-05-23", CONFLICT),
    "opf-local:0053": ("9780743412162", "Survivors", ("Jean Lorrah",), "Survivors/Jean-Lorrah", "2000-05-23", MATCH),
    "opf-local:0054": ("9780743412179", "Strike Zone", ("Peter David",), "Strike-Zone/Peter-David", "2000-05-23", MATCH),
    "opf-local:0055": ("9780743420860", "Power Hungry", ("Howard Weinstein",), "Power-Hungry/Howard-Weinstein", "2000-09-22", MATCH),
    "opf-local:0056": ("9780743420877", "Masks", ("John Vornholt",), "Masks/John-Vornholt", "2000-09-22", MATCH),
    "opf-local:0057": ("9780743420891", "A Call to Darkness", ("Michael Jan Friedman",), "A-Call-to-Darkness/Michael-Jan-Friedman", "2000-09-22", MATCH),
    "opf-local:0058": ("9780743420907", "A Rock and a Hard Place", ("Peter David",), "A-Rock-and-a-Hard-Place/Peter-David", "2000-09-22", MATCH),
    "opf-local:0059": ("9780743420914", "Gulliver's Fugitives", ("Keith Sharee",), "Gullivers-Fugitives/Keith-Sharee", "2000-09-22", MATCH),
    "opf-local:0060": ("9780743420921", "Doomsday World", ("Peter David", "Carter Carmen", "Michael Jan Friedman", "Robert Greenberger"), "Doomsday-World/Peter-David", "2000-09-22", CONFLICT),
    "opf-local:0061": ("9780743420938", "The Eyes of the Beholders", ("A.C. Crispin",), "The-Eyes-of-the-Beholders/A-C-Crispin", "2000-09-22", MATCH),
}

# SHA-256 of deterministic, complete reviewed row JSON (not untrusted row-supplied
# values). Any synopsis, author, source locator, field or uncertainty mutation
# requires source re-review, a changed pin, and a new validation audit.
REVIEWED_ROW_SHA256 = {
    "opf-local:0052": "13e6fee3b89c0ac23793452a93318a06f912daf88bc959a83c226bca6eafa1ba",
    "opf-local:0053": "7f306e7643073015d5c26994f82c9550dfde6bf367ebf5c32af159dff67ab653",
    "opf-local:0054": "673d92ba1ff97921ec10abaaeb2158bfcab93f98cc1c37e69db61c8357f27074",
    "opf-local:0055": "f270579ed75dd6cd458ab234f3ed9a536445459bd377f3b638a6d737b42021be",
    "opf-local:0056": "e349603e802195b5e793c414ee3b687306b9f3dd200ded2d1ce247be291b3615",
    "opf-local:0057": "d421b1b50964065aaaaf7e71ea451b5a144653cda6f6ff214266fec549399de1",
    "opf-local:0058": "262038d68e16992283946466f1aec0732d0789b9e58b0254586586f5e72b64ba",
    "opf-local:0059": "54282766ef3e84e5742f75a3692c8218740250a461d19a2c86b42c7d2fdd7efc",
    "opf-local:0060": "6c27090907c1fef1e8c610fdbb79b29717f5cde1074628f3b4ce3860f76c555c",
    "opf-local:0061": "1813200446469d8addd2055a427633d6138e00ae787cd3f85fb724b075c44c1e",
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


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


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
        for key, subvalue in value.items():
            require(isinstance(key, str) and PRIVATE_PATH.search(key) is None,
                    f"Private or malformed key: {breadcrumb}")
            forbid_private_paths(subvalue, f"{breadcrumb}.{key}")
    elif isinstance(value, list):
        for i, subvalue in enumerate(value):
            forbid_private_paths(subvalue, f"{breadcrumb}[{i}]")
    elif isinstance(value, str):
        require(PRIVATE_PATH.search(value) is None, f"Private path: {breadcrumb}")


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Bad ISBN10 structure")
    require(sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(value)) % 11 == 0,
            "Bad ISBN10 checksum")
    core = "978" + value[:9]
    digit = (-sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(core))) % 10
    return core + str(digit)


def isbn13_valid(value: str) -> bool:
    return (isinstance(value, str) and re.fullmatch(r"[0-9]{13}", value) is not None
            and sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value)) % 10 == 0)


def reviewed_digest(value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate(data: dict, source: dict, source_bytes: bytes, older: dict) -> None:
    forbid_private_paths(data)
    require(isinstance(data, dict) and set(data) == ENVELOPE_FIELDS,
            "Unreviewed envelope fields")
    require(data["schema_version"] == 1 and data["proposal_id"] == "opf-next-ten-publisher-edition-crosscheck-20261103",
            "Unexpected proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json",
            "Changed source locator")
    require(data["source_observation_sha256"] == hashlib.sha256(source_bytes).hexdigest()
            == "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7",
            "Source observation digest drift")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek",
            "Publisher lineage changed")
    require(data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY"
            and data["publisher_raw_html_sha256"] is None,
            "Unsupported publisher raw byte custody")
    require(data["research_snapshot_date"] == "2026-11-03", "Unreviewed research date")
    require(all(data[key] is False for key in (
        "private_ebook_text_read", "private_book_paths_exported", "publisher_cover_bytes_exported",
        "private_source_equivalence_verified")), "Forbidden private source effect")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE",
            "Forbidden global Work/coverage effect")
    require(source["ebook_full_text_read"] is False and source["edition_binding_verified"] is False,
            "Upstream OPF evidence overclaimed")
    require(isinstance(older, dict) and len(older["records"]) == 9,
            "Prior admitted publisher tranche changed")
    older_ids = {row["opf_source_local_id"] for row in older["records"]}
    require(older_ids.isdisjoint(EXPECTED), "Duplicate previously handled source-local OPF IDs")
    observed = {row["source_local_id"]: row for row in source["rows"]}
    records = data["records"]
    require(isinstance(records, list) and len(records) == len(EXPECTED)
            and all(isinstance(row, dict) and set(row) == ROW_FIELDS for row in records),
            "Unexpected records/schema")
    ids = [row["opf_source_local_id"] for row in records]
    require(len(set(ids)) == len(ids) and set(ids) == set(EXPECTED),
            "Duplicate/missing/unreviewed OPF rows")
    for row in records:
        ident = row["opf_source_local_id"]
        require(reviewed_digest(row) == REVIEWED_ROW_SHA256[ident],
                f"Unreviewed row/prose mutation: {ident}")
        opf = observed[ident]
        isbn, title, authors, slug, date, state = EXPECTED[ident]
        require(row["opf_entry_sha256"] == opf["opf_entry_sha256"] and
                row["opf_isbn10"] in opf["isbn_checksum_valid"],
                f"Source-local OPF binding mismatch: {ident}")
        require(isbn13_from_10(row["opf_isbn10"]) == row["isbn13_candidate"] == isbn,
                f"Bad ISBN10 conversion: {ident}")
        require(row["publisher_isbn13"] == isbn and isbn13_valid(isbn),
                f"Unreviewed publisher ISBN: {ident}")
        require(row["publisher_title"] == title and row["publisher_authors"] == list(authors)
                and row["publisher_format"] == "eBook" and row["publisher_publication_date"] == date,
                f"Publisher metadata mismatch: {ident}")
        require(row["crosscheck_state"] == state, f"Unreviewed status: {ident}")
        u = urlparse(row["publisher_locator"])
        require(u.scheme == "https" and u.netloc == "www.simonandschuster.com"
                and u.path == f"/books/{slug}/Star-Trek-The-Next-Generation/{isbn}"
                and not (u.params or u.query or u.fragment),
                f"Unreviewed publisher locator: {ident}")
        desc = row["original_publisher_description_paraphrase"]
        require(isinstance(desc, str) and 35 <= len(desc) <= 280,
                f"Missing bounded synopsis paraphrase: {ident}")
        require(isinstance(row["uncertainty"], str) and len(row["uncertainty"]) >= 45,
                f"Missing uncertainty note: {ident}")
        if state == CONFLICT:
            require("carmen carter" in " ".join(opf["creator"]).casefold()
                    and "Carter Carmen" in authors,
                    f"Creator rendering disagreement not preserved: {ident}")


if __name__ == "__main__":
    raw = SOURCE.read_bytes()
    validate(load(ROOT / "records.json"), load(SOURCE), raw, load(OLDER))
    print("PASS: ten new private OPF leads / publisher eBook ISBN matches; two creator-name rendering conflicts; no edition or Work admission")
