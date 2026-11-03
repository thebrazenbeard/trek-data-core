"""Fail-closed check of source-local literary publisher descriptions, never admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBS_SHA256 = "042591beed80964fe6e050f38f8947a6f0a55d7fec0e4b66cf13c32edfd55e15"
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != OBS_SHA256:
    raise ValueError("publisher observations have changed without independent review")
EXPECTED = json.loads(raw)

ROOT_FIELDS = {
    "schema_version", "observation_date_utc", "role", "proposal_only", "verification_class",
    "upstream_lineage", "distinct_upstream_sources", "candidate_work_count",
    "edition_pages_inspected", "original_description_paraphrase_count", "raw_page_byte_custody",
    "full_book_text_inspected", "source_bound", "close_read", "artwork_rights_verified",
    "artwork_bytes_stored", "accepted_source_work_effect", "accepted_evidence_effect",
    "accepted_coverage_effect", "public_site_effect", "candidates",
}
RECORD_FIELDS = {
    "source_local_id", "publisher_display_title", "author", "series", "edition",
    "other_publisher_edition", "synopsis_basis", "publisher_description_paraphrase",
    "description_anchor_terms", "cover_resource_observed", "cover_public_use_state",
    "identity_and_text_equivalence_state",
}
EDITION_FIELDS = {"isbn13", "publisher_imprint", "format", "publisher_date", "extent_pages", "source_url"}
EXPECTED_CATALOG = (
    ("9781982113292", "The Captain's Oath", "Christopher L. Bennett", "2019-05-28", "TRADE_PAPERBACK", "Pocket Books/Star Trek", 400),
    ("9781439109618", "Star Trek: Deep Space Nine: The Never Ending Sacrifice", "Una McCormack", "2009-08-25", "MASS_MARKET_PAPERBACK", "Pocket Books/Star Trek", 384),
    ("9781668282182", "Architects of Infinity", "Kirsten Beyer", "2026-09-12", "TRADE_PAPERBACK", "Gallery Books", 400),
)
URL_PATHS = {
    "9781982113292": "The-Captains-Oath/Christopher-L-Bennett/Star-Trek-The-Original-Series",
    "9781439109618": "Star-Trek-Deep-Space-Nine-The-Never-Ending-Sacrifice/Una-McCormack/Star-Trek-Deep-Space-Nine",
    "9781668282182": "Architects-of-Infinity/Kirsten-Beyer/Star-Trek-Voyager",
    "9781501138768": "Architects-of-Infinity/Kirsten-Beyer/Star-Trek-Voyager",
}
ANCHORS = {
    "9781982113292": ("kirk", "klingon", "starfleet"),
    "9781439109618": ("rugal", "bajoran", "dominion"),
    "9781668282182": ("full circle", "krenim", "conlon"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def isbn13_valid(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 13 or not value.isascii() or not value.isdigit():
        return False
    check = sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(value[:12]))
    return (10 - check % 10) % 10 == int(value[-1])


def validate_edition(edition: object, expected_isbn: str, extra: bool = False) -> None:
    require(type(edition) is dict and set(edition) == EDITION_FIELDS | ({"text_equivalence"} if extra else set()), "edition fields unreviewed")
    require(edition["isbn13"] == expected_isbn and isbn13_valid(expected_isbn), "ISBN identity/check digit mismatch")
    require(edition["source_url"] == "https://www.simonandschuster.com/books/" + URL_PATHS[expected_isbn] + "/" + expected_isbn, "edition source URL mismatch")
    if extra:
        require(edition["text_equivalence"] == "UNVERIFIED", "edition text equivalence not established")


def accepted_other_titles_and_isbns() -> tuple[set[str], set[str]]:
    """Discover accepted-main proposals and released overview titles; no identity reconciliation."""
    titles, isbns = set(), set()
    for path in sorted((ROOT / "proposals").rglob("*.json")):
        if path == HERE / "observations.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        def visit(item):
            if type(item) is dict:
                for key, value in item.items():
                    if key in {"title", "publisher_display_title"} and isinstance(value, str):
                        titles.add(value)
                    if key in {"isbn13", "publisher_edition_isbn13"} and isinstance(value, str):
                        isbns.add(value)
                    visit(value)
            elif type(item) is list:
                for value in item:
                    visit(value)
        visit(data)
    published = json.loads((ROOT / "explorer/synopsis-catalog.json").read_text(encoding="utf-8"))
    require(published["data_status"] == "EDITORIALLY_REVIEWED_DISPLAY_ONLY" and published["admission_effect"] == "NONE", "accepted overview basis changed")
    titles.update(row["title"] for row in published["synopses"] if row["medium"] == "LITERATURE")
    return titles, isbns


def validate(data: object, *, check_prior: bool = True) -> bool:
    require(type(data) is dict and set(data) == ROOT_FIELDS, "unreviewed root fields/private metadata")
    require(data["schema_version"] == "trek-lit-publisher-overviews-trio-b-v1", "wrong schema")
    require(data["role"] == "LIT" and data["observation_date_utc"] == "2026-11-03" and data["proposal_only"] is True, "source proposal state drift")
    require(data["verification_class"] == "OFFICIAL_PUBLISHER_EDITION_PAGE_AND_ABOUT_BOOK_DESCRIPTION", "publisher evidence tier drift")
    require(data["upstream_lineage"] == "publisher:simonandschuster.com" and type(data["distinct_upstream_sources"]) is int and data["distinct_upstream_sources"] == 1, "source lineage overcount")
    for field in ("raw_page_byte_custody", "full_book_text_inspected", "source_bound", "close_read", "artwork_rights_verified", "artwork_bytes_stored"):
        require(data[field] is False, "unauthorized custody or rights promotion: " + field)
    for field in ("accepted_source_work_effect", "accepted_evidence_effect", "accepted_coverage_effect", "public_site_effect"):
        require(data[field] == "NONE", "unauthorized effect: " + field)
    require(all(type(data[k]) is int for k in ("candidate_work_count", "edition_pages_inspected", "original_description_paraphrase_count")), "invalid count types")
    require(tuple(data[k] for k in ("candidate_work_count", "edition_pages_inspected", "original_description_paraphrase_count")) == (3, 4, 3), "false work/edition counts")
    rows = data["candidates"]
    require(type(rows) is list and len(rows) == 3, "wrong candidate count")
    ids = set()
    for row, (isbn, title, author, date, fmt, imprint, pages) in zip(rows, EXPECTED_CATALOG):
        require(type(row) is dict and set(row) == RECORD_FIELDS, "unreviewed candidate/private fields")
        require(type(row["source_local_id"]) is str and row["source_local_id"].startswith("lit-sns-") and row["source_local_id"] not in ids, "not source-local or duplicate ID")
        ids.add(row["source_local_id"])
        require((row["publisher_display_title"], row["author"]) == (title, author), "title/author not publisher verified")
        require(row["identity_and_text_equivalence_state"] == "SOURCE_LOCAL_UNRECONCILED", "global identity overclaim")
        require(row["synopsis_basis"] == "ORIGINAL_PARAPHRASE_OF_PUBLISHER_ABOUT_BOOK_NOT_CLOSE_READ", "narrative source overclaim")
        require(row["cover_resource_observed"] is True and row["cover_public_use_state"] == "UNVERIFIED_RIGHTS_NO_PUBLIC_DISPLAY", "cover rights escalation")
        require(type(row["description_anchor_terms"]) is list and len(row["description_anchor_terms"]) == 3, "source anchors invalid")
        para = row["publisher_description_paraphrase"]
        require(type(para) is str and 25 <= len(para.split()) <= 70, "possible copied publisher prose or missing paraphrase")
        require(all(anchor in para.casefold() for anchor in ANCHORS[isbn]), "publisher source-scope anchor omitted")
        edition = row["edition"]
        validate_edition(edition, isbn)
        require((edition["publisher_date"], edition["format"], edition["publisher_imprint"], edition["extent_pages"]) == (date, fmt, imprint, pages), "edition metadata swapped")
        alternate = row["other_publisher_edition"]
        if isbn == "9781668282182":
            validate_edition(alternate, "9781501138768", extra=True)
            require((alternate["publisher_date"], alternate["format"], alternate["publisher_imprint"], alternate["extent_pages"]) == ("2018-03-27", "MASS_MARKET_PAPERBACK", "Pocket Books/Star Trek", 400), "2018 sibling edition metadata drift")
        else:
            require(alternate is None, "unreviewed alternate edition")
        require(row == EXPECTED["candidates"][len(ids)-1], "unreviewed observation change")
    if check_prior:
        prior_titles, prior_isbns = accepted_other_titles_and_isbns()
        require(not (prior_titles & {r["publisher_display_title"] for r in rows}), "duplicates accepted proposal title")
        require(not (prior_isbns & {e["isbn13"] for r in rows for e in (r["edition"], r["other_publisher_edition"]) if e}), "duplicates accepted proposal ISBN")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Three official publisher description observations and four edition pages checked; zero admitted/public effects")
