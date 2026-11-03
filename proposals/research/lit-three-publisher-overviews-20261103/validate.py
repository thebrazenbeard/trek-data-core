#!/usr/bin/env python3
"""Fail-closed, source-local validation of three first-party marketing overviews."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBSERVATIONS = HERE / "observations.json"
EDITORIAL = ROOT / "proposals/publication/lit-overview-expansion-20261103/editorial-request.json"
PUBLIC = ROOT / "explorer/synopsis-catalog.json"
SHA256 = {
    OBSERVATIONS: "3989c480061492453b2b905c14e2b1b61014f9d379d9b0e8ea0d7afe3019f85f",
    EDITORIAL: "bf9cc901d772a11b9c6e92260575a1116e4de132938a037ea087a6be036b5f42",
    PUBLIC: "1d3db3991bdc16a99b34c098f5004ba979d3d20b0e130027dbe3acb8d16d8c0e",
}
SOURCE = "https://www.simonandschuster.com/books/"
EXPECTED = {
    "A Stitch in Time": (
        "9780743420587", "Andrew J. Robinson", "Star Trek: Deep Space Nine", "EBOOK",
        "Pocket Books/Star Trek", "2000-05-01", "432 pages",
        "https://www.simonandschuster.com/books/A-Stitch-in-Time/Andrew-J-Robinson/Star-Trek-Deep-Space-Nine/9780743420587",
    ),
    "Star Trek: The Next Generation: Q&A": (
        "9781982160357", "Keith R. A. DeCandido", "Star Trek: The Next Generation", "TRADE_PAPERBACK",
        "Gallery Books", "2020-05-02", "320 pages",
        "https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Q-A/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9781982160357",
    ),
    "The Eternal Tide": (
        "9781668288559", "Kirsten Beyer", "Star Trek: Voyager", "TRADE_PAPERBACK",
        "Gallery Books", "2026-10-17", "400 pages",
        "https://www.simonandschuster.com/books/The-Eternal-Tide/Kirsten-Beyer/Star-Trek-Voyager/9781668288559",
    ),
}
ROOT_FIELDS = frozenset({
    "schema_version", "proposal_only", "observed_on_utc", "method", "source_reader",
    "independence_group", "independent_upstream_source_count", "publisher_product_pages_read",
    "distinct_candidate_work_count", "original_publisher_description_paraphrase_count",
    "accepted_source_work_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
    "accepted_coverage_effect", "public_synopsis_publication_effect", "public_artwork_release_effect",
    "source_bound", "full_text_available", "structurally_indexed", "close_read", "semantically_analyzed",
    "image_or_ebook_bytes_retrieved", "publisher_edition_family_complete", "candidates",
})
CANDIDATE_FIELDS = frozenset({
    "candidate_id", "publisher_title", "creator", "publisher_series", "edition_format", "edition_isbn13",
    "edition_imprint", "publisher_publication_date", "publisher_extent", "publisher_edition_url",
    "overview_basis", "original_overview", "overview_scope", "publisher_html_sha256",
    "private_edition_match", "full_text_content_read", "cover_rights_status", "alternate_edition_observation",
})
ALTERNATE_FIELDS = frozenset({
    "source_locator", "format", "isbn13", "publisher_publication_date", "imprint",
    "title_author_match", "text_equivalence", "work_identity_effect",
})


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exact_keys(value: object, keys: frozenset[str], context: str) -> None:
    check(type(value) is dict and set(value) == keys, f"unexpected or missing {context} fields")


def isbn13(value: object) -> bool:
    return (type(value) is str and len(value) == 13 and value.isascii() and value.isdigit() and
            sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value)) % 10 == 0)


def raw_pinned(path: Path) -> dict:
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == SHA256[path], f"source artifact drift: {path.name}")
    value = json.loads(raw)
    check(type(value) is dict, f"invalid source object: {path.name}")
    return value


def accepted_title_and_isbn_snapshot() -> tuple[set[str], set[str]]:
    review = raw_pinned(EDITORIAL)
    public = raw_pinned(PUBLIC)
    check(review.get("candidate_count") == 18 and len(review.get("candidates", [])) == 18,
          "editorial request count drift")
    check(public.get("synopsis_count") == 23 and len(public.get("synopses", [])) == 23,
          "public synopsis count drift")
    titles = {x["title"].casefold() for x in review["candidates"]}
    titles.update(x["title"].casefold() for x in public["synopses"] if x["row_id"].startswith("directory:literature:"))
    isbn = {x["publisher_edition_isbn13"] for x in review["candidates"]}
    return titles, isbn


def validate(data: object) -> None:
    exact_keys(data, ROOT_FIELDS, "batch")
    check(data["schema_version"] == "trek-lit-three-publisher-overviews-v1", "schema identity drift")
    check(data["proposal_only"] is True and data["observed_on_utc"] == "2026-11-03", "proposal context drift")
    check(data["method"] == "DIRECT_FIRST_PARTY_PUBLISHER_PRODUCT_PAGE_DESCRIPTION_AND_EDITION_METADATA" and
          data["source_reader"] == "RENDERED_WEB_PAGE_NO_ARCHIVED_HTML_BYTES", "source observation tier drift")
    check(data["independence_group"] == "publisher:simonandschuster.com" and
          type(data["independent_upstream_source_count"]) is int and
          data["independent_upstream_source_count"] == 1, "publisher independence overcount")
    check(data["publisher_product_pages_read"] == 4 and data["distinct_candidate_work_count"] == 3 and
          data["original_publisher_description_paraphrase_count"] == 3, "observation count drift")
    for key in ("accepted_source_work_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
                "accepted_coverage_effect", "public_synopsis_publication_effect", "public_artwork_release_effect"):
        check(data[key] == "NONE", f"unauthorized effect {key}")
    for key in ("source_bound", "full_text_available", "structurally_indexed", "close_read",
                "semantically_analyzed", "image_or_ebook_bytes_retrieved", "publisher_edition_family_complete"):
        check(data[key] is False, f"unsupported source/content promotion {key}")

    rows = data["candidates"]
    check(type(rows) is list and len(rows) == 3, "candidate count not three")
    seen_title, seen_isbn, seen_id = set(), set(), set()
    for row in rows:
        exact_keys(row, CANDIDATE_FIELDS, "candidate")
        title, isbn = row["publisher_title"], row["edition_isbn13"]
        check(type(title) is str and title in EXPECTED and isbn13(isbn), "unknown title or malformed ISBN")
        check(title not in seen_title and isbn not in seen_isbn and row["candidate_id"] not in seen_id,
              "duplicate edition/Work candidate")
        seen_title.add(title)
        seen_isbn.add(isbn)
        seen_id.add(row["candidate_id"])
        check((isbn, row["creator"], row["publisher_series"], row["edition_format"],
               row["edition_imprint"], row["publisher_publication_date"], row["publisher_extent"],
               row["publisher_edition_url"]) == EXPECTED[title], "publisher edition observation mismatch")
        check(type(row["candidate_id"]) is str and
              row["candidate_id"].startswith("lit-source-local-sns-") and
              row["candidate_id"].endswith("-20261103"), "unauthorized canonical Work ID")
        check(row["publisher_edition_url"].startswith(SOURCE) and
              row["publisher_edition_url"].endswith("/" + isbn), "not an exact ISBN-specific publisher page")
        check(row["overview_basis"] == "PUBLISHER_DESCRIPTION_PARAPHRASE" and
              row["overview_scope"] == "PROMOTIONAL_PAGE_CLAIMS_NOT_VERIFIED_BOOK_EVENTS", "misrepresented story evidence")
        overview = row["original_overview"]
        check(type(overview) is str and 25 <= len(overview.split()) <= 65 and
              overview.startswith("The publisher "), "missing bounded original marketing paraphrase")
        check(row["publisher_html_sha256"] is None and row["private_edition_match"] == "UNVERIFIED" and
              row["full_text_content_read"] is False and
              row["cover_rights_status"] == "NOT_ESTABLISHED_NO_PUBLIC_DISPLAY",
              "unsupported source custody, text or image rights")
        alt = row["alternate_edition_observation"]
        if title != "The Eternal Tide":
            check(alt is None, "invented sibling edition")
        else:
            exact_keys(alt, ALTERNATE_FIELDS, "alternate edition")
            check(alt == {
                "source_locator": "https://www.simonandschuster.com/books/The-Eternal-Tide/Kirsten-Beyer/Star-Trek-Voyager/9781451668186",
                "format": "MASS_MARKET_PAPERBACK", "isbn13": "9781451668186",
                "publisher_publication_date": "2012-08-28", "imprint": "Pocket Books/Star Trek",
                "title_author_match": "SAME_PUBLISHER_TITLE_CREATOR_METADATA", "text_equivalence": "UNVERIFIED",
                "work_identity_effect": "NONE",
            } and isbn13(alt["isbn13"]), "sibling edition not independently text-equivalent")
    check(seen_title == set(EXPECTED), "candidate identity set drift")
    prior_titles, prior_isbn = accepted_title_and_isbn_snapshot()
    check(not {title.casefold() for title in seen_title} & prior_titles and not seen_isbn & prior_isbn,
          "duplicate accepted public or 18-item editorial synopsis candidate")
    original = raw_pinned(OBSERVATIONS)
    check(data == original, "unreviewed or injected proposal fields or marketing content")


if __name__ == "__main__":
    try:
        validate(raw_pinned(OBSERVATIONS))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f"LIT_THREE_OVERVIEWS_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("LIT_THREE_OVERVIEWS_OK: 3 source-local marketing overviews, 4 edition pages, zero admission")
