#!/usr/bin/env python3
"""Strict local proposal validator: Titan art/reference editions, no text claim."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
ROOT_KEYS = {
    "schema_version", "batch_id", "observed_on_utc", "worker_role", "proposal_only",
    "first_party_publisher_lineage", "first_party_publisher_family_count",
    "source_family_distinct_from_prior_simon_and_schuster", "local_work_candidate_count",
    "publisher_edition_count", "full_book_text_read", "full_artwork_read_or_stored",
    "edition_completeness_verified", "private_source_matches_verified",
    "accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
    "coverage_effect", "public_synopsis_effect", "artwork_release_effect", "works",
}
WORK_KEYS = {
    "local_work_candidate_id", "publisher_display_title", "publisher_creator_credits",
    "work_form", "publisher_source_url", "source_kind", "edition_isbn13",
    "edition_format", "edition_page_count_display", "edition_published_us",
    "edition_published_uk", "source_discovery_state", "private_manifestation_binding",
}
DATA = {
    "9781785659119": ("eaves", "Star Trek: The Art of John Eaves", (("Joe Nazzaro", "AUTHOR"),),
       "https://titanbooks.com/9614-star-trek-the-art-of-john-eaves/", 208, "2018-11-27", "2018-11-20"),
    "9781785659348": ("curry", "Star Trek: The Artistry of Dan Curry", (("Dan Curry", "AUTHOR"), ("Ben Robinson", "AUTHOR")),
       "https://titanbooks.com/9639-star-trek-the-artistry-of-dan-curry/", 204, "2020-12-01", "2020-12-01"),
    "9781781166703": ("ortiz-tos", "Star Trek: The Art of Juan Ortiz", (("Juan Ortiz", "AUTHOR_ARTIST"),),
       "https://titanbooks.com/6933-star-trek-the-art-of-juan-ortiz/", 112, "2013-09-03", "2013-09-06"),
    "9781785653872": ("ortiz-tng", "Star Trek The Next Generation: The Art of Juan Ortiz", (("Juan Ortiz", "AUTHOR_ARTIST"),),
       "https://titanbooks.com/9032-star-trek-the-next-generation-the-art-of-juan-ortiz/", 208, "2017-09-05", "2017-09-05"),
    "9781789095159": ("neville-page", "Star Trek: The Art of Neville Page", (("Joe Nazzaro", "AUTHOR"),),
       "https://titanbooks.com/70373-star-trek-the-art-of-neville-page/", 192, "2023-08-08", "2023-08-08"),
}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def isbn13_ok(s: object) -> bool:
    return isinstance(s, str) and bool(re.fullmatch(r"\d{13}", s)) and (
        sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s)) % 10 == 0
    )


def validate(root: object) -> None:
    require(isinstance(root, dict) and set(root) == ROOT_KEYS, "root field-set drift")
    require(root["schema_version"] == "trek-lit-titan-five-nonfiction-artbook-editions-v1", "schema drift")
    require(root["batch_id"] == "lit-titan-five-artbooks-20261104" and root["observed_on_utc"] == "2026-11-04", "batch/date drift")
    require(root["worker_role"] == "LIT" and root["proposal_only"] is True, "worker/proposal boundary drift")
    require(root["first_party_publisher_lineage"] == "publisher:titanbooks.com" and root["source_family_distinct_from_prior_simon_and_schuster"] is True,
            "Titan source provenance changed")
    require(type(root["first_party_publisher_family_count"]) is int and root["first_party_publisher_family_count"] == 1,
            "one Titan publisher family cannot become five independent corroborators")
    for name in ("local_work_candidate_count", "publisher_edition_count"):
        require(type(root[name]) is int and root[name] == 5, f"five-lead count drift: {name}")
    for name in ("full_book_text_read", "full_artwork_read_or_stored", "edition_completeness_verified", "private_source_matches_verified"):
        require(root[name] is False, f"unearned private source/book/art qualification: {name}")
    for name in ("accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
                 "coverage_effect", "public_synopsis_effect", "artwork_release_effect"):
        require(root[name] == "NONE", f"protected effect attempted: {name}")

    works = root["works"]
    require(isinstance(works, list) and len(works) == 5, "expected five distinct publisher works")
    seen_isbns, seen_ids, seen_titles = set(), set(), set()
    for row in works:
        require(isinstance(row, dict) and set(row) == WORK_KEYS, "work field-set drift or leakage")
        isbn = row["edition_isbn13"]
        require(isbn13_ok(isbn) and isbn in DATA and isbn not in seen_isbns, "ISBN invalid, duplicated, or unsupported")
        seen_isbns.add(isbn)
        slug, title, creator_credits, url, pages, date_us, date_uk = DATA[isbn]
        work_id = "lit-titan5-20261104-" + slug
        require(row["local_work_candidate_id"] == work_id and work_id not in seen_ids, "local work identity drift")
        seen_ids.add(work_id)
        require(row["publisher_display_title"] == title and title.casefold() not in seen_titles, "title drift/duplicate")
        seen_titles.add(title.casefold())
        credits = row["publisher_creator_credits"]
        require(isinstance(credits, list) and all(isinstance(x, dict) and set(x) == {"name", "role"} for x in credits), "credit schema drift")
        require(tuple((x["name"], x["role"]) for x in credits) == creator_credits, "art-creator/cowriter credit drift")
        require(row["work_form"] == "NONFICTION_ILLUSTRATED_PRODUCTION_ART_BOOK", "artbook misclassified as novel")
        require(row["publisher_source_url"] == url and row["source_kind"] == "FIRST_PARTY_TITAN_PUBLISHER_PRODUCT_METADATA",
                "source locator/lineage drift")
        require(row["edition_format"] == "HARDBACK", "format drift")
        require(type(row["edition_page_count_display"]) is int and row["edition_page_count_display"] == pages,
                "page count or integer type drift")
        require(row["edition_published_us"] == date_us and row["edition_published_uk"] == date_uk,
                "regional publication date drift")
        require(row["source_discovery_state"] == "PUBLISHER_CATALOG_METADATA_ONLY", "source-read inflation")
        require(row["private_manifestation_binding"] == "NOT_EVALUATED", "unsupported private edition identity")
    require(seen_isbns == set(DATA), "Titan ISBN inventory incomplete")


def accepted_main_duplicate_isbn_paths() -> list[str]:
    paths = []
    for path in (REPO_ROOT / "proposals").rglob("*.json"):
        if HERE in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        if any(isbn in text for isbn in DATA):
            paths.append(str(path.relative_to(REPO_ROOT)))
    return sorted(paths)


if __name__ == "__main__":
    validate(json.loads(RECORDS.read_text(encoding="utf-8")))
    conflicts = accepted_main_duplicate_isbn_paths()
    require(not conflicts, f"publisher ISBN already present in other proposals: {conflicts}")
    print("PASS: five distinct Titan Books hardback nonfiction art/reference editions, zero research admissions")
