#!/usr/bin/env python3
"""Fail-closed validator for five non-admitted publisher-edition discovery leads."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
ROOT_FIELDS = {
    "schema_version", "batch_id", "role", "observed_on_utc", "proposal_only",
    "first_party_upstream_family", "first_party_upstream_family_count",
    "candidate_work_count", "publisher_edition_count", "full_text_or_audio_read",
    "edition_completeness_verified", "private_source_edition_matches_verified",
    "copyrighted_story_text_or_art_reproduced", "accepted_source_binding_effect",
    "accepted_work_effect", "accepted_evidence_effect", "coverage_effect",
    "public_synopsis_effect", "artwork_release_effect", "candidates",
}
ROW_FIELDS = {
    "local_work_candidate_id", "publisher_work_title", "publisher_creator_credits",
    "publisher_series", "source_url", "source_kind", "edition_format",
    "edition_isbn13", "edition_imprint", "edition_publication_date",
    "edition_extent_pages", "source_discovery_state",
    "local_edition_identity_status", "publisher_copy_anomaly",
}
EXPECTED = {
    "9780743453868": ("mosaic", "Mosaic", (("Jeri Taylor", "AUTHOR"),), "Star Trek: Voyager", "2002-10-04", 320,
       "https://www.simonandschuster.com/books/Mosaic/Jeri-Taylor/Star-Trek-Voyager/9780743453868", None),
    "9780743453851": ("pathways", "Pathways", (("Jeri Taylor", "AUTHOR"),), "Star Trek: Voyager", "2009-09-29", 528,
       "https://www.simonandschuster.com/books/Pathways/Jeri-Taylor/Star-Trek-Voyager/9780743453851", None),
    "9780743420730": ("unification", "Unification", (("Jeri Taylor", "AUTHOR"),), "Star Trek: The Next Generation", "2000-09-22", 256,
       "https://www.simonandschuster.com/books/Unification/Jeri-Taylor/Star-Trek-The-Next-Generation/9780743420730", "AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED"),
    "9780743400817": ("lives-of-dax", "The Lives Of Dax", (("Marco Palmieri", "EDITOR"),), "Star Trek: Deep Space Nine", "1999-12-01", 384,
       "https://www.simonandschuster.com/books/The-Lives-Of-Dax/Marco-Palmieri/Star-Trek-Deep-Space-Nine/9780743400817", None),
    "9780743419864": ("romulan-way", "The Romulan Way", (("Diane Duane", "AUTHOR"), ("Peter Morwood", "AUTHOR")), "Star Trek: The Original Series", "2000-09-22", 304,
       "https://www.simonandschuster.com/books/The-Romulan-Way/Diane-Duane/Star-Trek-The-Original-Series/9780743419864", None),
}
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
    "coverage_effect", "public_synopsis_effect", "artwork_release_effect",
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def isbn13_ok(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9]{13}", value)) and (
        sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value)) % 10 == 0
    )


def validate(data: object) -> None:
    require(isinstance(data, dict) and set(data) == ROOT_FIELDS, "root field-set drift")
    require(data["schema_version"] == "trek-lit-five-first-party-edition-leads-v1", "schema drift")
    require(data["batch_id"] == "lit-five-publisher-bibliography-20261104", "batch drift")
    require(data["role"] == "LIT" and data["observed_on_utc"] == "2026-11-04", "role/time drift")
    require(data["proposal_only"] is True, "unadmitted source promoted")
    require(data["first_party_upstream_family"] == "publisher:simonandschuster.com", "source lineage drift")
    require(type(data["first_party_upstream_family_count"]) is int and data["first_party_upstream_family_count"] == 1,
            "one publisher family is not five independent sources")
    require(type(data["candidate_work_count"]) is int and data["candidate_work_count"] == 5, "candidate count drift")
    require(type(data["publisher_edition_count"]) is int and data["publisher_edition_count"] == 5, "edition count drift")
    for field in ("full_text_or_audio_read", "edition_completeness_verified",
                  "private_source_edition_matches_verified", "copyrighted_story_text_or_art_reproduced"):
        require(data[field] is False, f"unsupported coverage/copyright claim: {field}")
    for field in EFFECTS:
        require(data[field] == "NONE", f"protected effect attempted: {field}")

    rows = data["candidates"]
    require(isinstance(rows, list) and len(rows) == 5, "expected five candidate records")
    ids, isbns, work_labels = set(), set(), set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == ROW_FIELDS, "candidate field-set drift")
        isbn = row["edition_isbn13"]
        require(isbn13_ok(isbn) and isbn in EXPECTED and isbn not in isbns, "ISBN invalid, duplicated, or unqualified")
        isbns.add(isbn)
        slug, title, creators, series, pubdate, pages, url, anomaly = EXPECTED[isbn]
        require(row["local_work_candidate_id"] == f"lit-pub5-20261104-{slug}" and row["local_work_candidate_id"] not in ids,
                "local work identifier drift")
        ids.add(row["local_work_candidate_id"])
        require(row["publisher_work_title"] == title and title.casefold() not in work_labels, "work title drift/duplicate")
        work_labels.add(title.casefold())
        credits = row["publisher_creator_credits"]
        require(isinstance(credits, list) and all(isinstance(c, dict) and set(c) == {"name", "role"} for c in credits),
                "creator credit schema drift")
        require(tuple((c["name"], c["role"]) for c in credits) == creators, "author/editor/coauthor identity drift")
        require(row["publisher_series"] == series, "series drift")
        require(row["source_url"] == url and row["source_kind"] == "FIRST_PARTY_PUBLISHER_PRODUCT_METADATA",
                "publisher locator/kind drift")
        require(row["edition_format"] == "EBOOK", "publisher edition format drift")
        require(row["edition_imprint"] == "Pocket Books/Star Trek" and row["edition_publication_date"] == pubdate,
                "imprint/date drift")
        require(type(row["edition_extent_pages"]) is int and row["edition_extent_pages"] == pages,
                "publisher page extent drift")
        require(row["source_discovery_state"] == "PUBLISHER_PAGE_READ_METADATA_ONLY", "discovery overclaim")
        require(row["local_edition_identity_status"] == "PUBLISHER_PRODUCT_ONLY_NO_PRIVATE_MATCH", "private identity overclaim")
        require(row["publisher_copy_anomaly"] == anomaly, "publisher copy anomaly drift")
    require(isbns == set(EXPECTED), "five-edition inventory incomplete")


def accepted_baseline_duplicate_isbns() -> list[str]:
    """Check existing proposal JSON only; do not silently change any record."""
    matches = []
    for path in (REPO_ROOT / "proposals").rglob("*.json"):
        if HERE in path.parents:
            continue
        raw = path.read_text(encoding="utf-8")
        if any(isbn in raw for isbn in EXPECTED):
            matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(matches)


if __name__ == "__main__":
    validate(json.loads(RECORDS.read_text(encoding="utf-8")))
    duplicates = accepted_baseline_duplicate_isbns()
    require(not duplicates, f"edition already represented in another proposal: {duplicates}")
    print("PASS: five distinct first-party publisher ebook editions, no private source identity or coverage effects")
