#!/usr/bin/env python3
"""Fail-closed guard for three non-admitted first-party publisher edition leads."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records.json"
SOURCE_MAP = {
    "9780743419987": ("The Kobayashi Maru", "Julia Ecklar", "EBOOK", "2000-09-22"),
    "9780743546744": ("Shadows of the Sun", "Michael Jan Friedman", "ABRIDGED_AUDIO_DOWNLOAD", "1993-08-01"),
    "9780743546591": ("The Star Trek: The Next Generation: The Genesis Wave Book 3", "John Vornholt", "ADAPTED_AUDIO_DOWNLOAD", "2002-01-01"),
}
EFFECTS = {
    "accepted_source_work_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
    "coverage_effect", "public_synopsis_effect", "artwork_release_effect",
}
FORBIDDEN_PROMOTION = re.compile(r"\b(?:read\s+the\s+book|full\s+text\s+verified|canonically\s+established|publicly\s+released)\b", re.I)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def is_isbn13(value: str) -> bool:
    return bool(re.fullmatch(r"\d{13}", value)) and sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(value)) % 10 == 0


def validate(value: object) -> None:
    require(isinstance(value, dict), "root must be object")
    serialized = json.dumps(value, ensure_ascii=False).casefold()
    require(not re.search(r"(?:\b[a-z]:[/\\]|/users/|\\users\\|patri[/\\]|onedrive|documents[/\\]books|star_trek_opf_converted\.zip)", serialized), "private host username/path/archive topology disclosed")
    require(value.get("schema_version") == "trek-lit-archive-discovery-publisher-editions-v1", "schema drift")
    require(value.get("proposal_only") is True and value.get("observed_on_utc") == "2026-11-03", "proposal/date drift")
    require(value.get("private_archive") == "owner-private-books-opf-archive-20261103", "archive source drift or private path disclosure")
    require(value.get("observed_archive_opf_count") == 347, "observed OPF inventory drift")
    require(value.get("private_to_publisher_edition_match") == "UNVERIFIED", "invented private ISBN binding")
    require(value.get("publisher_upstream_group") == "publisher:simonandschuster.com", "publisher lineage mismatch")
    require(value.get("independent_source_count") == 1, "same publisher must not count as independent witnesses")
    for key in EFFECTS:
        require(value.get(key) == "NONE", f"protected effect forbidden: {key}")
    for key in ("image_or_ebook_bytes_retrieved", "full_text_available", "structurally_indexed", "close_read", "semantically_analyzed"):
        require(value.get(key) is False, f"unearned coverage/custody claim: {key}")
    require(value.get("publisher_html_sha256") is None, "unobserved HTML hash invented")
    candidates = value.get("candidates")
    require(isinstance(candidates, list) and len(candidates) == 3, "exact three publisher editions required")
    require(value.get("publisher_product_pages_read") == 3 and value.get("candidate_edition_count") == 3 and value.get("original_publisher_description_paraphrase_count") == 3, "batch count drift")
    ids, isbns = set(), set()
    for record in candidates:
        require(isinstance(record, dict), "candidate must be object")
        cid, isbn = record.get("candidate_id"), record.get("publisher_isbn13")
        require(isinstance(cid, str) and cid.startswith("lit-sns-") and cid not in ids, "duplicate/invalid candidate ID")
        ids.add(cid)
        require(isinstance(isbn, str) and is_isbn13(isbn) and isbn in SOURCE_MAP and isbn not in isbns, "unbound/invalid/duplicate ISBN")
        isbns.add(isbn)
        title, creator, edition_type, pubdate = SOURCE_MAP[isbn]
        require((record.get("publisher_title"), record.get("creator"), record.get("publisher_edition_format"), record.get("publisher_publication_date")) == (title, creator, edition_type, pubdate), "first-party product metadata drift")
        url = record.get("publisher_url")
        require(isinstance(url, str) and url.startswith("https://www.simonandschuster.com/books/") and url.endswith("/" + isbn), "official edition locator drift")
        require(record.get("private_archive_edition_identity") == "UNVERIFIED", "private OPF metadata is not an ISBN match")
        require(record.get("fictional_truth_status") == "PUBLISHER_PROMOTIONAL_DESCRIPTION_ONLY", "publisher promotion overclaim")
        description = record.get("original_publisher_description_paraphrase")
        require(isinstance(description, str) and 110 <= len(description) <= 550 and not FORBIDDEN_PROMOTION.search(description), "description must be original scoped paraphrase")
        tags = record.get("source_relative_query_tags")
        require(isinstance(tags, list) and len(tags) == 5 and len(set(tags)) == 5 and all(isinstance(tag, str) and re.fullmatch(r"[a-z-]+:[a-z0-9-]+", tag) for tag in tags), "query tags invalid")
    require(isbns == set(SOURCE_MAP), "publisher edition inventory incomplete")
    shadows = next(c for c in candidates if c["publisher_isbn13"] == "9780743546744")
    require("Ssan" in shadows["original_publisher_description_paraphrase"] and "Susan" not in shadows["original_publisher_description_paraphrase"], "publisher typo promoted into synopsis")
    require("Susan" in shadows.get("publisher_copy_anomaly", "") and "Ssan" in shadows.get("publisher_copy_anomaly", ""), "source spelling disagreement lost")


if __name__ == "__main__":
    validate(json.loads(RECORDS.read_text(encoding="utf-8")))
    print("LIT_PRIVATE_ARCHIVE_PUBLISHER_EDITION_PROPOSALS_VALIDATED: 3 publisher pages, 3 scoped original descriptions, 0 private edition matches")
