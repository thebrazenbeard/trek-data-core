#!/usr/bin/env python3
"""Fail-closed publisher-opf gap observation; no source identity or Work promotion."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OBS_PATH = REPO / "proposals/librarian/private-opf-metadata-20261103/observations.json"
PRIOR_PATH = REPO / "proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103/records.json"
OBS_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
PRIOR_SHA = "ac67d958c0c75aee0fe3979bba8cd145972cfaca40aca920748ceec55b892964"
ENVELOPE = frozenset((
    "schema_version", "proposal_id", "research_snapshot_date", "source_observation_path",
    "source_observation_sha256", "prior_crosscheck_path", "prior_crosscheck_sha256",
    "publisher_source_family", "publisher_source_mode", "publisher_raw_html_sha256",
    "private_ebook_text_read", "private_edition_identity_verified", "publisher_cover_bytes_exported",
    "global_work_admission", "coverage_effect", "public_synopsis_effect", "records",
))
ROW = frozenset((
    "source_local_observation_id", "opf_source_local_reference", "opf_entry_sha256", "opf_title",
    "opf_creators", "opf_isbn10", "isbn13_from_opf", "publisher_locator", "publisher_title",
    "publisher_authors", "publisher_format", "publisher_isbn13", "publisher_publication_date",
    "publisher_pages", "publisher_series_number", "crosscheck_state", "synopsis_review_state",
    "original_publisher_description_paraphrase", "uncertainty",
))
HELD = "HELD_PUBLISHER_PARAPHRASE_NO_PRIVATE_TEXT"
NONE = "NONE_NO_NEW_PUBLIC_SYNOPSIS"
EXPECTED = {
    "publisher-gap:opf0089:infiltrator:e9780743421201": (
        "opf-local:0089", "73b2ed96170cdbd7f0db2ddebf4b9d1f6aad0d6011c07aec3c48022c6109b1f1",
        "Star Trek - TNG - Infiltrator", (), None, None,
        "Infiltrator", ("W.R. Thompson",), "9780743421201", 288, 42,
        "Infiltrator/W-R-Thompson", "TITLE_TOKEN_CANDIDATE_NO_OPF_EDITION_IDENTIFIER", HELD,
    ),
    "publisher-gap:opf0091:death-of-princes:e9780743422888": (
        "opf-local:0091", "11d97f45a723d8dd0dad9adb517027b5a4b183b18ca8216ff667d05512ed25ab",
        "THE DEATH OF PRINCES", ("JOHN PEEL",), "0743421221", "9780743421225",
        "The Death of Princes", ("John Peel",), "9780743422888", 304, 44,
        "The-Death-of-Princes/John-Peel", "TITLE_AUTHOR_MATCH_BUT_OPF_ISBN_NOT_THIS_PRODUCT", NONE,
    ),
    "publisher-gap:opf0091:balance-of-power:e9780743421225": (
        "opf-local:0091", "11d97f45a723d8dd0dad9adb517027b5a4b183b18ca8216ff667d05512ed25ab",
        "THE DEATH OF PRINCES", ("JOHN PEEL",), "0743421221", "9780743421225",
        "Balance of Power", ("Dafydd ab Hugh",), "9780743421225", 304, 33,
        "Balance-of-Power/Dafydd-ab-Hugh", "EXACT_OPF_ISBN_MAPS_TO_DIFFERENT_PUBLISHER_TITLE_AUTHOR", NONE,
    ),
}
PIN = {
    "publisher-gap:opf0089:infiltrator:e9780743421201": "e989d37ca71fd3e353c33ff30c86e5fe6270e591e3b9edc64abb31203f16f91e",
    "publisher-gap:opf0091:death-of-princes:e9780743422888": "21a6a7e312cf79dbdb7b9d176ed61814d82e54ad931a4c8a45e5c7d94fb7eaad",
    "publisher-gap:opf0091:balance-of-power:e9780743421225": "31dfc451d75d8301b149a951dbf4ef19e03ade810de04c27ac6b7a80fe0dd9b7",
}
PRIVATE_PATH = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|\\\\|(?:^|[\\/])(?:Users|home|mnt|AppData|OneDrive|workspace|tmp)[\\/]|file://)", re.I,
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load(path: Path) -> dict:
    def unique(pairs):
        output = {}
        for key, value in pairs:
            require(key not in output, f"Duplicate JSON key: {key}")
            output[key] = value
        return output
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def reject_private_paths(value: object, scope: str = "records") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            require(isinstance(key, str) and PRIVATE_PATH.search(key) is None, f"Invalid key: {scope}")
            reject_private_paths(item, f"{scope}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            reject_private_paths(item, f"{scope}[{i}]")
    elif isinstance(value, str):
        require(PRIVATE_PATH.search(value) is None, f"Private path: {scope}")


def isbn13_from_10(value: str) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{9}[0-9X]", value) is not None,
            "Invalid ISBN10 syntax")
    require(sum((10 - i) * (10 if ch == "X" else int(ch)) for i, ch in enumerate(value)) % 11 == 0,
            "Invalid ISBN10 checksum")
    raw = "978" + value[:9]
    check = -sum((1 if i % 2 == 0 else 3) * int(ch) for i, ch in enumerate(raw)) % 10
    return raw + str(check)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate(data: dict, obs: dict, obs_bytes: bytes, prior: dict, prior_bytes: bytes) -> None:
    reject_private_paths(data)
    require(isinstance(data, dict) and set(data) == ENVELOPE, "Unexpected envelope")
    require(data["schema_version"] == 1 and data["proposal_id"] == "opf-0089-0091-firstparty-gap-20261103"
            and data["research_snapshot_date"] == "2026-11-03", "Unexpected proposal identity")
    require(data["source_observation_path"] == "proposals/librarian/private-opf-metadata-20261103/observations.json"
            and data["source_observation_sha256"] == hashlib.sha256(obs_bytes).hexdigest() == OBS_SHA,
            "Sanitized OPF source drift")
    require(data["prior_crosscheck_path"] == "proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103/records.json"
            and data["prior_crosscheck_sha256"] == hashlib.sha256(prior_bytes).hexdigest() == PRIOR_SHA,
            "Accepted prior crosscheck drift")
    require(data["publisher_source_family"] == "publisher:simonandschuster.com:pocket-books-star-trek"
            and data["publisher_source_mode"] == "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY"
            and data["publisher_raw_html_sha256"] is None, "Publisher custody overclaim")
    for key in ("private_ebook_text_read", "private_edition_identity_verified", "publisher_cover_bytes_exported"):
        require(data[key] is False, "Private text, edition, or art overclaim")
    require(data["global_work_admission"] == "NONE" and data["coverage_effect"] == "NONE"
            and data["public_synopsis_effect"] == "NONE", "Forbidden public effect")
    require(obs["ebook_full_text_read"] is False and obs["edition_binding_verified"] is False,
            "Upstream custody claims changed")
    prior_0091 = [row for row in prior["records"] if row["opf_source_local_id"] == "opf-local:0091"]
    require(len(prior_0091) == 1 and prior_0091[0]["opf_isbn10"] == "0743421221"
            and prior_0091[0]["isbn13_candidate"] == "9780743421225"
            and prior_0091[0]["publisher_isbn13"] == "9780743422888"
            and prior_0091[0]["crosscheck_state"] == "TITLE_AUTHOR_PRODUCT_MATCH_ISBN_EDITION_MISMATCH_UNRESOLVED",
            "Prior unresolved OPF 0091 observation altered")
    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == 3 and all(isinstance(x, dict) and set(x) == ROW for x in rows),
            "Unexpected source-local row schema")
    ids = [row["source_local_observation_id"] for row in rows]
    require(len(set(ids)) == 3 and set(ids) == set(EXPECTED), "Unexpected/duplicate source-local publisher observation")
    source = {row["source_local_id"]: row for row in obs["rows"]}
    for row in rows:
        ident = row["source_local_observation_id"]
        (opf, sha, title, creators, isbn10, candidate, pub_title, pub_authors, pub_isbn,
         pages, series, slug, crosscheck, synopsis) = EXPECTED[ident]
        src = source[opf]
        require(row["opf_source_local_reference"] == opf and row["opf_entry_sha256"] == src["opf_entry_sha256"] == sha
                and row["opf_title"] == title and src["title"] == [title]
                and row["opf_creators"] == list(creators) and src["creator"] == list(creators)
                and row["opf_isbn10"] == isbn10 and row["isbn13_from_opf"] == candidate,
                f"OPF evidence drift: {ident}")
        if isbn10 is None:
            require(src["isbn_checksum_valid"] == [] and src["publisher"] == [] and src["date"] == [],
                    "OPF0089 suddenly has independent metadata")
        else:
            require(src["isbn_checksum_valid"] == [isbn10]
                    and isbn13_from_10(isbn10) == candidate,
                    "Wrong OPF ISBN conversion")
        require(row["publisher_title"] == pub_title and row["publisher_authors"] == list(pub_authors)
                and row["publisher_format"] == "eBook" and row["publisher_isbn13"] == pub_isbn
                and row["publisher_publication_date"] == "2000-09-22"
                and type(row["publisher_pages"]) is int and row["publisher_pages"] == pages
                and type(row["publisher_series_number"]) is int and row["publisher_series_number"] == series,
                f"Unreviewed publisher metadata: {ident}")
        url = urlparse(row["publisher_locator"])
        require(url.scheme == "https" and url.netloc == "www.simonandschuster.com"
                and url.path == f"/books/{slug}/Star-Trek-The-Next-Generation/{pub_isbn}"
                and not (url.query or url.params or url.fragment or url.username or url.password),
                f"Not the reviewed first-party publisher product: {ident}")
        require(row["crosscheck_state"] == crosscheck
                and row["synopsis_review_state"] == synopsis,
                f"Unreviewed cross-title/synopsis state: {ident}")
        if opf == "opf-local:0089":
            require(candidate is None and row["original_publisher_description_paraphrase"] is not None,
                    "Infiltrator must remain title-only HELD candidate")
        else:
            require(row["original_publisher_description_paraphrase"] is None,
                    "Conflicted OPF0091 may not publish/relabel a synopsis")
            require((candidate == pub_isbn) == ("balance-of-power" in ident),
                    "Publisher identity cross-title mismatch hidden")
        require(isinstance(row["uncertainty"], str) and len(row["uncertainty"]) >= 90,
                f"Missing explicit unresolved scope: {ident}")
        require(digest(row) == PIN[ident], f"Unreviewed row content mutation: {ident}")


if __name__ == "__main__":
    validate(load(ROOT / "records.json"), load(OBS_PATH), OBS_PATH.read_bytes(),
             load(PRIOR_PATH), PRIOR_PATH.read_bytes())
    print("PASS: source-local Infiltrator title lead and OPF0091 cross-title ISBN collision HELD; no private/Work/art/coverage")
