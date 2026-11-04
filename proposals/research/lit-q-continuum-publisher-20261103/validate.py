"""Fail-closed three numbered publisher-product checks; fourth product stays unlinked."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBS_SHA256 = "ccd22f2159985e37522471bb02bcef4d68f763e366f810be27ec30b018acc488"
OPF_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
raw = (HERE / "observations.json").read_bytes()
if hashlib.sha256(raw).hexdigest() != OBS_SHA256:
    raise ValueError("publisher observation drift")
EXPECTED = json.loads(raw)

ROOT_FIELDS = {
    "schema_version", "observation_date_utc", "role", "proposal_only", "source_kind",
    "publisher_lineage", "independent_source_families", "numbered_book_candidates",
    "distinct_publisher_isbn_pages_read", "unresolved_unnumbered_product_count", "private_book_custody_verified",
    "full_text_read", "raw_html_sha256", "cover_art_public_rights_verified", "cover_art_bytes_committed",
    "accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect", "public_site_effect",
    "numbered_books", "adjacent_unnumbered_publisher_product", "accepted_opf_candidate_lead_context",
}
BOOK_FIELDS = {
    "source_local_id", "publisher_display_title", "publisher_author", "publisher_series", "publisher_sequence_number",
    "isbn13", "format", "imprint", "publisher_date", "publisher_pages", "publisher_url",
    "original_publisher_description_paraphrase", "synopsis_basis", "source_anchors",
    "publication_and_custody_state", "identity_state",
}
UNNUMBERED_FIELDS = (BOOK_FIELDS - {"publisher_sequence_number", "source_anchors"}) | {
    "relationship_to_numbered_books", "publisher_page_contains_explicit_complete_trilogy_claim",
}
OPF_FIELDS = {"opf_source_local_id", "sanitized_opf_title", "opf_isbn_present", "identity_link_state"}
CATALOG = (
    ("9780671041014", "The Q Continuum: Book One: Q-Space", "The-Q-Continuum-Book-One-Q-Space", 1),
    ("9780671041021", "The Q Continuum: Book Two: Q-Zone", "The-Q-Continuum-Book-Two-Q-Zone", 2),
    ("9780671041038", "The Q Continuum: Book Three: Q-Strike", "The-Q-Continuum-Book-Three-Q-Strike", 3),
)
UNNUMBERED = ("9780743491822", "The Q Continuum", "The-Q-Continuum")
OPF_IDS = ("opf-local:0094", "opf-local:0095", "opf-local:0096")
ANCHORS = (("picard", "barrier", "continuum"), ("q", "picard", "continuum"), ("galactic barrier", "picard", "q"))


def require(ok: bool, message: str):
    if not ok:
        raise ValueError(message)


def isbn13_valid(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 13 or not value.isascii() or not value.isdigit():
        return False
    s = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(value[:12]))
    return (10 - s % 10) % 10 == int(value[-1])


def publisher_url(slug: str, isbn: str) -> str:
    return "https://www.simonandschuster.com/books/" + slug + "/Greg-Cox/Star-Trek-The-Next-Generation/" + isbn


def validate_book(row: object, catalog: tuple, *, unnumbered: bool = False):
    isbn, title, slug, *seq = catalog
    keys = UNNUMBERED_FIELDS if unnumbered else BOOK_FIELDS
    require(type(row) is dict and set(row) == keys, "unexpected publisher book field or private path")
    require(row["publisher_display_title"] == title and row["publisher_author"] == "Greg Cox" and row["publisher_series"] == "Star Trek: The Next Generation", "publisher title/creator/series conflict")
    require(isbn13_valid(row["isbn13"]) and row["isbn13"] == isbn, "invalid/substituted publisher ISBN")
    require(row["publisher_url"] == publisher_url(slug, isbn), "publisher URL/ISBN mismatch")
    require(row["format"] == "EBOOK" and row["imprint"] == "Pocket Books/Star Trek", "format/imprint drift")
    require(row["publisher_date"] == ("2003-10-07" if unnumbered else "1999-07-14"), "publisher date drift")
    require(row["publisher_pages"] == (368 if unnumbered else 288) and type(row["publisher_pages"]) is int, "distinct extent misrepresented")
    require(type(row["source_local_id"]) is str and row["source_local_id"].startswith("lit-sns-q-continuum-"), "global source identity overclaim")
    require(row["identity_state"] == "SOURCE_LOCAL_UNRECONCILED" and row["publication_and_custody_state"] == "PAST_PUBLISHER_DATE_NO_SOURCE_TEXT_CUSTODY", "source or identity promotion")
    require(row["synopsis_basis"] == "ORIGINAL_PARAPHRASE_OF_PUBLISHER_PROMOTION_ONLY", "unsupported book reading")
    synopsis = row["original_publisher_description_paraphrase"]
    require(type(synopsis) is str and 25 <= len(synopsis.split()) <= 65, "missing or copied promotional text")
    if unnumbered:
        require(row["relationship_to_numbered_books"] == "UNRESOLVED_NOT_A_VERIFIED_OMNIBUS_OR_SAME_TEXT_EDITION", "unsupported omnibus claim")
        require(row["publisher_page_contains_explicit_complete_trilogy_claim"] is False, "invented complete trilogy claim")
    else:
        require(row["publisher_sequence_number"] == seq[0] and type(row["publisher_sequence_number"]) is int, "publisher numbered order drift")
        require(row["source_anchors"] == EXPECTED["numbered_books"][seq[0] - 1]["source_anchors"], "unreviewed source anchor")
        require(all(anchor in synopsis.casefold() for anchor in ANCHORS[seq[0] - 1]), "description not publisher grounded")


def accepted_opf_leads():
    opf_raw = (ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json").read_bytes()
    require(hashlib.sha256(opf_raw).hexdigest() == OPF_SHA256, "accepted OPF metadata custody hash drift")
    d = json.loads(opf_raw)
    require(d["ebook_full_text_read"] is False and d["edition_binding_verified"] is False, "OPF metadata unexpectedly treated as bound source")
    rows = {row["source_local_id"]: row for row in d["rows"]}
    return [rows[k] for k in OPF_IDS]


def validate(data: object, *, check_prior: bool = True) -> bool:
    require(type(data) is dict and set(data) == ROOT_FIELDS, "unexpected packet root/private keys")
    require(data["schema_version"] == "trek-lit-q-continuum-publisher-v1" and data["role"] == "LIT" and data["observation_date_utc"] == "2026-11-03" and data["proposal_only"] is True, "packet contract drift")
    require(data["source_kind"] == "FIRST_PARTY_SNS_RENDERED_PUBLISHER_EDITION_PAGE_AND_DESCRIPTION", "wrong evidence class")
    require(data["publisher_lineage"] == "publisher:simonandschuster.com" and type(data["independent_source_families"]) is int and data["independent_source_families"] == 1, "upstream overcount")
    require(tuple(data[k] for k in ("numbered_book_candidates", "distinct_publisher_isbn_pages_read", "unresolved_unnumbered_product_count")) == (3, 4, 1) and all(type(data[k]) is int for k in ("numbered_book_candidates", "distinct_publisher_isbn_pages_read", "unresolved_unnumbered_product_count")), "wrong title/edition count")
    for field in ("private_book_custody_verified", "full_text_read", "cover_art_public_rights_verified", "cover_art_bytes_committed"):
        require(data[field] is False, "unverified custody/rights status: " + field)
    require(data["raw_html_sha256"] is None, "fabricated publisher HTML bytes")
    for field in ("accepted_work_effect", "accepted_evidence_effect", "accepted_coverage_effect", "public_site_effect"):
        require(data[field] == "NONE", "unapproved admission/release: " + field)
    books = data["numbered_books"]
    require(type(books) is list and len(books) == 3, "wrong book count")
    for i, (row, catalog) in enumerate(zip(books, CATALOG)):
        validate_book(row, catalog)
        require(row == EXPECTED["numbered_books"][i], "unreviewed numbered-book observation")
    unnumbered = data["adjacent_unnumbered_publisher_product"]
    validate_book(unnumbered, UNNUMBERED, unnumbered=True)
    require(unnumbered == EXPECTED["adjacent_unnumbered_publisher_product"], "unreviewed unnumbered-product claim")
    all_ids = [r["source_local_id"] for r in books] + [unnumbered["source_local_id"]]
    require(len(set(all_ids)) == 4, "duplicate local product")
    opf_rows = data["accepted_opf_candidate_lead_context"]
    require(type(opf_rows) is list and len(opf_rows) == 3, "wrong OPF discovery context")
    for i, (row, prior) in enumerate(zip(opf_rows, accepted_opf_leads())):
        require(type(row) is dict and set(row) == OPF_FIELDS | ({"opf_creator_mismatch"} if i == 2 else set()), "OPF context extra field/private path")
        require(row["opf_source_local_id"] == OPF_IDS[i] and row["sanitized_opf_title"] == prior["title"][0], "OPF metadata title/ID misbound")
        require(row["opf_isbn_present"] is False and prior["isbn_checksum_valid"] == [], "unverified OPF ISBN granted")
        require(row["identity_link_state"] == "UNRESOLVED_DISCOVERY_ONLY", "OPF/publisher work identity promoted")
        if i == 2:
            require(row["opf_creator_mismatch"] == "OPF_LISTS_WILLIAM_C_DEETS_AND_DEAN_WILLIAMS_PUBLISHER_LISTS_GREG_COX", "creator disagreement erased")
            require(prior["creator"] == ["William C. Deets &Dean Williams"], "creator discrepancy not source-grounded")
        require(row == EXPECTED["accepted_opf_candidate_lead_context"][i], "unreviewed OPF crosscheck")
    if check_prior:
        known_isbns = {r["isbn13"] for r in books} | {unnumbered["isbn13"]}
        # A publisher ISBN can legitimately recur in independent, HELD source-local
        # observations. Another proposal mentioning it does not establish a
        # duplicate accepted Work/edition; identity is resolved only through the
        # governed reconciliation path. Do not scan all proposal JSON as if it
        # were an accepted-identity registry.
        require(len(known_isbns) == len(books) + 1, "duplicate ISBN within publisher source packet")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Q Continuum: 3 numbered publisher Work candidates + 1 held unnumbered ISBN; 0 source/public effects")
