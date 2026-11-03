"""Publisher-only literary edition packet. Never admits source texts or Work identity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBS_SHA256 = "9f0daa1268260621abacbd93a40546deb2b8205fdd6afc957e07faae99524590"
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != OBS_SHA256:
    raise ValueError("literature publisher observation bytes changed")
EXPECTED = json.loads(raw)
ROOT_KEYS = {
    "schema_version", "observed_date_utc", "role", "proposal_only", "source_class", "publisher_lineage",
    "independent_upstream_source_family_count", "candidate_work_count", "edition_page_count",
    "original_publisher_paraphrase_count", "private_book_source_bound", "private_book_text_read",
    "source_content_byte_sha256", "accepted_evidence_effect", "accepted_source_work_effect",
    "accepted_coverage_effect", "public_site_effect", "cover_art_rights_verified", "cover_art_bytes_stored",
    "candidates",
}
RECORD_KEYS = {
    "source_local_id", "publisher_display_title", "publisher_author", "publisher_series", "edition",
    "related_edition", "synopsis_basis", "original_paraphrase", "source_scope_anchors",
    "artwork_observation", "identity_status",
}
EDITION_KEYS = {"isbn13", "format", "imprint", "publisher_date", "pages", "publication_state_as_of_observation", "publisher_url"}
CATALOG = (
    ("9781668290712", "The Lost Era: The Buried Age", "Christopher L. Bennett", "Star Trek: The Next Generation", "TRADE_PAPERBACK", "Gallery Books", "2027-02-13", 448),
    ("9781476788319", "Star Trek: The Next Generation: A Singular Destiny", "Keith R. A. DeCandido", "Star Trek: The Next Generation", "TRADE_PAPERBACK", "Pocket Books/Star Trek", "2014-04-12", 400),
    ("9780743464062", "The Star Trek: The Lost era: 2328-2346: The Art of the Impossible", "Keith R. A. DeCandido", "Star Trek: Deep Space Nine", "EBOOK", "Pocket Books/Star Trek", "2003-10-01", 384),
)
URL_PARTS = {
    "9781668290712": "The-Lost-Era-The-Buried-Age/Christopher-L-Bennett/Star-Trek-The-Next-Generation",
    "9781416537397": "The-Lost-Era-The-Buried-Age/Christopher-L-Bennett/Star-Trek-The-Next-Generation",
    "9781476788319": "Star-Trek-The-Next-Generation-A-Singular-Destiny/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation",
    "9780743464062": "The-Star-Trek-The-Lost-era-2328-2346-The-Art-of-the-Impossible/Keith-R-A-DeCandido/Star-Trek-Deep-Space-Nine",
}
ANCHORS = {
    "9781668290712": ("picard", "stargazer", "archaeology"),
    "9781476788319": ("destiny", "federation", "sonek pran"),
    "9780743464062": ("klingon", "cardassian", "curzon dax"),
}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def valid_isbn13(isbn: object) -> bool:
    if not isinstance(isbn, str) or len(isbn) != 13 or not isbn.isascii() or not isbn.isdigit():
        return False
    check = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(isbn[:12]))
    return (10 - check % 10) % 10 == int(isbn[12])


def validate_edition(row: object, expected: tuple, *, sibling: bool = False) -> None:
    isbn, _, _, _, fmt, imprint, date, pages = expected
    require(type(row) is dict and set(row) == EDITION_KEYS | ({"content_equivalence"} if sibling else set()), "unexpected edition/private fields")
    require(valid_isbn13(row["isbn13"]) and row["isbn13"] == isbn, "ISBN invalid or substituted")
    require((row["format"], row["imprint"], row["publisher_date"], row["pages"]) == (fmt, imprint, date, pages), "edition metadata mismatch")
    require(row["publisher_url"] == "https://www.simonandschuster.com/books/" + URL_PARTS[isbn] + "/" + isbn, "edition-specific publisher URL mismatch")
    future = isbn == "9781668290712"
    require(row["publication_state_as_of_observation"] == ("FUTURE_PUBLISHER_LISTING_NOT_BOOK_CUSTODY" if future else "PAST_PUBLISHER_DATE_NOT_BOOK_CUSTODY"), "publisher listing misrepresented as text custody")
    if sibling:
        require(row["content_equivalence"] == "UNVERIFIED", "edition equivalence unverified")


def prior_titles_and_isbns() -> tuple[set[str], set[str]]:
    """Detect prior exact candidate overlap, not speculative alternate-title equivalence."""
    titles: set[str] = set()
    isbns: set[str] = set()
    for path in sorted((ROOT / "proposals").rglob("*.json")):
        if path == HERE / "observations.json":
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        def visit(data):
            if type(data) is dict:
                for key, value in data.items():
                    if key in {"title", "publisher_title", "publisher_display_title"} and isinstance(value, str):
                        titles.add(value)
                    if key in {"isbn13", "publisher_isbn13", "publisher_edition_isbn13"} and isinstance(value, str):
                        isbns.add(value)
                    visit(value)
            elif type(data) is list:
                for value in data:
                    visit(value)
        visit(obj)
    display = json.loads((ROOT / "explorer/synopsis-catalog.json").read_text(encoding="utf-8"))
    require(display["admission_effect"] == "NONE", "accepted display unexpectedly admitted")
    titles.update(r["title"] for r in display["synopses"] if r["medium"] == "LITERATURE")
    return titles, isbns


def validate(data: object, *, check_prior: bool = True) -> bool:
    require(type(data) is dict and set(data) == ROOT_KEYS, "unexpected root/private fields")
    require(data["schema_version"] == "trek-lit-lost-era-destiny-publisher-v1" and data["observed_date_utc"] == "2026-11-03" and data["role"] == "LIT" and data["proposal_only"] is True, "wrong packet identity")
    require(data["source_class"] == "FIRST_PARTY_PUBLISHER_RENDERED_PRODUCT_AND_ABOUT_BOOK", "invalid source tier")
    require(data["publisher_lineage"] == "publisher:simonandschuster.com" and type(data["independent_upstream_source_family_count"]) is int and data["independent_upstream_source_family_count"] == 1, "source-family count inflated")
    require((data["candidate_work_count"], data["edition_page_count"], data["original_publisher_paraphrase_count"]) == (3, 4, 3) and all(type(data[k]) is int for k in ("candidate_work_count", "edition_page_count", "original_publisher_paraphrase_count")), "candidate counts inflated")
    for key in ("private_book_source_bound", "private_book_text_read", "cover_art_rights_verified", "cover_art_bytes_stored"):
        require(data[key] is False, "unverified source or rights escalation: " + key)
    require(data["source_content_byte_sha256"] is None, "unpossessed source-byte digest")
    for key in ("accepted_evidence_effect", "accepted_source_work_effect", "accepted_coverage_effect", "public_site_effect"):
        require(data[key] == "NONE", "unauthorized effect: " + key)
    rows = data["candidates"]
    require(type(rows) is list and len(rows) == 3, "work candidate count")
    ids = set()
    for i, (row, expected) in enumerate(zip(rows, CATALOG)):
        isbn, title, author, series, *rest = expected
        require(type(row) is dict and set(row) == RECORD_KEYS, "unexpected candidate field/protected text")
        sid = row["source_local_id"]
        require(type(sid) is str and sid.startswith("lit-sns-") and sid not in ids, "global/duplicate identity")
        ids.add(sid)
        require((row["publisher_display_title"], row["publisher_author"], row["publisher_series"]) == (title, author, series), "publisher bibliographic source scope changed")
        require(row["identity_status"] == "SOURCE_LOCAL_NO_GLOBAL_RECONCILIATION", "identity overclaim")
        require(row["synopsis_basis"] == "ORIGINAL_PUBLISHER_DESCRIPTION_PARAPHRASE_ONLY", "book close-read inference")
        require(row["artwork_observation"] == "PUBLISHER_RESOURCE_LINK_ONLY_RIGHTS_UNVERIFIED_HOLD", "cover rights claim")
        para = row["original_paraphrase"]
        require(type(para) is str and 25 <= len(para.split()) <= 65, "unreviewed paraphrase length")
        require(type(row["source_scope_anchors"]) is list and row["source_scope_anchors"] == EXPECTED["candidates"][i]["source_scope_anchors"] and all(anchor in para.casefold() for anchor in ANCHORS[isbn]), "publisher premise source anchors missing")
        validate_edition(row["edition"], expected)
        if i == 0:
            other = ("9781416537397", title, author, series, "MASS_MARKET_PAPERBACK", "Pocket Books/Star Trek", "2007-06-26", 448)
            validate_edition(row["related_edition"], other, sibling=True)
        else:
            require(row["related_edition"] is None, "unreviewed related edition")
        require(row == EXPECTED["candidates"][i], "unreviewed synopsis or metadata mutation")
    if check_prior:
        titles, isbns = prior_titles_and_isbns()
        require(not (titles & {row["publisher_display_title"] for row in rows}), "title collision with accepted proposal")
        new_isbns = {edition["isbn13"] for row in rows for edition in (row["edition"], row["related_edition"]) if edition}
        require(not (isbns & new_isbns), "ISBN collision with accepted proposal")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("3 source-local publisher Work candidates; 4 ISBN pages; 0 source text, coverage or public effects")
