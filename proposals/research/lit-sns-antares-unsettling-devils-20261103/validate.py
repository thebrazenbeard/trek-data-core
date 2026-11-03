"""Source-relative, fail-closed review of three publisher-page literary leads.

This is a LIT proposal only. No book was read and no accepted Works or coverage
may be inferred from these publisher pages.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PINNED_OBSERVATIONS_SHA256 = "54872dfb1e9fd1040e52dc4ef644a267ab3a13f5c45fe1d253331b451ec89159"
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != PINNED_OBSERVATIONS_SHA256:
    raise ValueError("publisher observations changed without re-review and checksum update")
EXPECTED = json.loads(raw)

ROOT_FIELDS = {
    "schema_version", "role", "observation_date_utc", "proposal_only", "upstream_lineage",
    "distinct_upstream_sources", "candidate_work_count", "edition_pages_read",
    "original_publisher_description_paraphrases", "raw_page_bytes_custodied",
    "full_book_text_read", "full_text_available", "close_read", "source_work_binding_effect",
    "identity_reconciliation_effect", "accepted_coverage_effect", "public_explorer_effect",
    "cover_use_rights_verified", "candidates",
}
CANDIDATE_FIELDS = {
    "source_local_entity_id", "publisher_title", "author", "publisher_series", "edition", "evidence",
    "assertions", "original_publisher_description_paraphrase", "description_anchor_terms",
    "cover_on_publisher_page", "cover_publication_state", "text_equivalence_and_global_identity",
}
EDITION_FIELDS = {"isbn13", "format", "imprint", "release_date", "extent_pages", "source_url"}
EVIDENCE_FIELDS = {"id", "kind", "section", "supports"}
ASSERTION_FIELDS = {"id", "predicate", "object", "evidence_id", "status"}
PINNED = (
    ("9781982113209", "The Antares Maelstrom", "Greg Cox", "Star Trek: The Original Series", "TRADE_PAPERBACK", "2019-08-13", 368, "The-Antares-Maelstrom/Greg-Cox/Star-Trek-The-Original-Series", ("kirk", "baldur-3", "antares maelstrom")),
    ("9781982140601", "The Unsettling Stars", "Alan Dean Foster", "Star Trek", "TRADE_PAPERBACK", "2020-04-14", 304, "The-Unsettling-Stars/Alan-Dean-Foster/Star-Trek", ("kelvin", "kirk", "perenorean")),
    ("9781476700472", "Star Trek: The Original Series: Devil's Bargain", "Tony Daniel", "Star Trek: The Original Series", "MASS_MARKET_PAPERBACK", "2013-02-26", 320, "Star-Trek-The-Original-Series-Devils-Bargain/Tony-Daniel/Star-Trek-The-Original-Series", ("kirk", "vesbius", "spock")),
)
ANCHOR_DISPLAY = {
    "9781982113209": ["Kirk", "Baldur-3", "Antares Maelstrom"],
    "9781982140601": ["Kelvin", "Kirk", "Perenorean"],
    "9781476700472": ["Kirk", "Vesbius", "Spock"],
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def isbn13_valid(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 13 or not value.isascii() or not value.isdigit():
        return False
    check = sum((1 if i % 2 == 0 else 3) * int(ch) for i, ch in enumerate(value[:12]))
    return (10 - check % 10) % 10 == int(value[-1])


def accepted_other_titles_and_isbns() -> tuple[set[str], set[str]]:
    """Bounded duplicate guard across already-accepted JSON and public synopsis rows."""
    titles: set[str] = set()
    isbns: set[str] = set()

    def visit(obj: object) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in {"title", "publisher_display_title", "publisher_title"} and isinstance(value, str):
                    titles.add(value.casefold())
                if key in {"isbn13", "publisher_edition_isbn13"} and isinstance(value, str):
                    isbns.add(value)
                visit(value)
        elif isinstance(obj, list):
            for value in obj:
                visit(value)

    for path in sorted((ROOT / "proposals").rglob("*.json")):
        if path == HERE / "observations.json":
            continue
        visit(json.loads(path.read_text(encoding="utf-8")))
    for path in (ROOT / "explorer/synopsis-catalog.json", ROOT / "explorer/lit-publisher-edition-leads.json"):
        visit(json.loads(path.read_text(encoding="utf-8")))
    return titles, isbns


def validate(data: object, *, check_prior: bool = True) -> bool:
    require(type(data) is dict and set(data) == ROOT_FIELDS, "unknown root fields")
    require(data["schema_version"] == "lit-sns-antares-unsettling-devils-source-local-v1", "schema drift")
    require(data["role"] == "LIT" and data["observation_date_utc"] == "2026-11-03" and data["proposal_only"] is True, "not a dated LIT proposal")
    require(data["upstream_lineage"] == "publisher:simonandschuster.com" and data["distinct_upstream_sources"] == 1, "publisher lineage misrepresented as corroboration")
    require(tuple(data[k] for k in ("candidate_work_count", "edition_pages_read", "original_publisher_description_paraphrases")) == (3, 3, 3), "count promotion")
    for key in ("raw_page_bytes_custodied", "full_book_text_read", "full_text_available", "close_read", "cover_use_rights_verified"):
        require(data[key] is False, "unsupported full-text or rights claim: " + key)
    for key in ("source_work_binding_effect", "identity_reconciliation_effect", "accepted_coverage_effect", "public_explorer_effect"):
        require(data[key] == "NONE", "unauthorized accepted/public effect: " + key)
    rows = data["candidates"]
    require(type(rows) is list and len(rows) == 3, "wrong candidate count")
    seen_ids: set[str] = set()
    for row, (isbn, title, author, series, fmt, date, pages, path, anchors) in zip(rows, PINNED):
        require(type(row) is dict and set(row) == CANDIDATE_FIELDS, "candidate fields not reviewed")
        local = row["source_local_entity_id"]
        require(isinstance(local, str) and local.startswith("lit-sns-") and local not in seen_ids, "invalid source-local identity")
        seen_ids.add(local)
        require((row["publisher_title"], row["author"], row["publisher_series"]) == (title, author, series), "publisher title, author or series swapped")
        edition = row["edition"]
        require(type(edition) is dict and set(edition) == EDITION_FIELDS, "edition fields not reviewed")
        require(edition["isbn13"] == isbn and isbn13_valid(isbn), "edition ISBN mismatch")
        require((edition["format"], edition["imprint"], edition["release_date"], edition["extent_pages"]) == (fmt, "Pocket Books/Star Trek", date, pages), "edition format/imprint/date/extent drift")
        require(edition["source_url"] == f"https://www.simonandschuster.com/books/{path}/{isbn}", "wrong publisher edition locator")
        evidence = row["evidence"]
        require(type(evidence) is list and len(evidence) == 2 and all(type(e) is dict and set(e) == EVIDENCE_FIELDS for e in evidence), "evidence structure invalid")
        require(evidence[0]["kind"] == "PUBLISHER_PRODUCT_METADATA" and evidence[0]["supports"] == "EDITION_LISTING_ONLY" and evidence[0]["section"] == "Product Details", "edition evidence promoted")
        require(evidence[1]["kind"] == "PUBLISHER_ABOUT_BOOK" and evidence[1]["supports"] == "PUBLISHER_CLAIM_ONLY" and evidence[1]["section"] == "About the Book", "description evidence promoted")
        require(len({e["id"] for e in evidence}) == 2, "duplicate evidence ID")
        assertions = row["assertions"]
        require(type(assertions) is list and len(assertions) == 1 and type(assertions[0]) is dict and set(assertions[0]) == ASSERTION_FIELDS, "assertion structure invalid")
        require(assertions[0]["predicate"].startswith("PUBLISHER_DESCRIBES_") and assertions[0]["evidence_id"] == evidence[1]["id"], "unlinked publisher claim")
        require(assertions[0]["status"] == "SOURCE_RELATIVE_UNVERIFIED_IN_BOOK", "source claim promoted to truth")
        para = row["original_publisher_description_paraphrase"]
        require(type(para) is str and 25 <= len(para.split()) <= 70 and all(a in para.casefold() for a in anchors), "publisher-only synopsis absent/unanchored")
        require(row["description_anchor_terms"] == ANCHOR_DISPLAY[isbn], "anchor list changed")
        require(row["cover_on_publisher_page"] is True and row["cover_publication_state"] == "HELD_RIGHTS_UNVERIFIED", "cover rights release unsupported")
        require(row["text_equivalence_and_global_identity"] == "UNRESOLVED", "global Work identity silently resolved")
        require(row == EXPECTED["candidates"][len(seen_ids) - 1], "unreviewed content change")
    if check_prior:
        titles, isbns = accepted_other_titles_and_isbns()
        require(not titles.intersection(r["publisher_title"].casefold() for r in rows), "duplicate accepted title")
        require(not isbns.intersection(r["edition"]["isbn13"] for r in rows), "duplicate accepted edition")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("3 source-local publisher edition cards and descriptions validated; no admitted/public effects")
