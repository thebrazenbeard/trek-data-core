#!/usr/bin/env python3
"""Deterministic source-local validation for seven public publisher ISBN observations."""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent

# Independently transcribed from the public publisher product-detail fields.
# There is deliberately no private ebook/OPF data or canonical Work registry here.
EXPECTED = {
    "9781668051368": ("Star Trek: Strange New Worlds: Asylum", "Una McCormack", "Star Trek: Strange New Worlds", "HARDCOVER", "2024-11-05", 320, None, None, "Star-Trek-Strange-New-Worlds-Asylum/Una-McCormack/Star-Trek-Strange-New-Worlds"),
    "9781668074589": ("Star Trek: Strange New Worlds: Toward the Night", "James Swallow", "Star Trek: Strange New Worlds", "EBOOK", "2025-04-29", 336, None, None, None),
    "9781668046371": ("Star Trek: Picard: Firewall", "David Mack", "Star Trek: Picard", "EBOOK", "2024-02-27", 336, None, None, "Star-Trek-Picard-Firewall/David-Mack/Star-Trek-Picard"),
    "9781797172699": ("Pliable Truths", "Dayton Ward", "Star Trek: The Next Generation", "UNABRIDGED_AUDIO_DOWNLOAD", "2024-05-21", None, 660, "Robert Petkoff", "Pliable-Truths/Dayton-Ward/Star-Trek-The-Next-Generation"),
    "9781982154189": ("Shadows Have Offended", "Cassandra Rose Clarke", "Star Trek: The Next Generation", "EBOOK", "2021-07-13", 304, None, None, "Shadows-Have-Offended/Cassandra-Rose-Clarke/Star-Trek-The-Next-Generation"),
    "9781982133672": ("The Higher Frontier", "Christopher L. Bennett", "Star Trek: The Original Series", "EBOOK", "2020-03-10", 352, None, None, "The-Higher-Frontier/Christopher-L-Bennett/Star-Trek-The-Original-Series"),
    "9781982113285": ("Available Light", "Dayton Ward", "Star Trek: The Next Generation", "EBOOK", "2019-04-09", 368, None, None, "Available-Light/Dayton-Ward/Star-Trek-The-Next-Generation"),
}

ROOT_FIELDS = {
    "schema_version", "batch_id", "proposal_only", "observation_date_utc",
    "source_class", "source_independence_group", "raw_publisher_page_bytes_captured",
    "accepted_source_effect", "accepted_work_effect", "accepted_binding_effect", "coverage_effect", "records",
}
ROW_FIELDS = {
    "source_local_id", "publisher_title", "publisher_creator", "publisher_series", "publisher_isbn13",
    "format", "imprint", "publication_date", "page_count", "runtime_minutes", "narrator",
    "source_url", "source_field_locator", "source_raw_sha256", "status",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load(path: Path) -> dict:
    def distinct_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=distinct_pairs)


def valid_isbn13(isbn: str) -> bool:
    return (isinstance(isbn, str) and len(isbn) == 13 and isbn.isascii() and isbn.isdigit()
            and sum((1 if i % 2 == 0 else 3) * int(char) for i, char in enumerate(isbn)) % 10 == 0)


def validate(data: dict) -> None:
    require(isinstance(data, dict) and set(data) == ROOT_FIELDS, "Unexpected top-level fields")
    require(data["schema_version"] == "1.0.0", "Schema version changed")
    require(data["batch_id"] == "sns-public-edition-followon-20261103", "Batch identity changed")
    require(data["proposal_only"] is True, "Proposal status cannot be promoted")
    require(data["source_class"] == "PUBLIC_FIRST_PARTY_PUBLISHER_PRODUCT_METADATA", "Source class changed")
    require(data["source_independence_group"] == "publisher:simonandschuster.com", "Publisher lineage changed")
    require(data["raw_publisher_page_bytes_captured"] is False, "Unverified source-byte custody")
    require(
        all(data[key] == "NONE" for key in (
            "accepted_source_effect", "accepted_work_effect", "accepted_binding_effect", "coverage_effect"
        )), "Admission/coverage effects prohibited",
    )
    require(data["observation_date_utc"] == "2026-11-03", "Observation date changed")
    require(isinstance(data["records"], list) and len(data["records"]) == len(EXPECTED), "Expected seven records")

    seen = set()
    for record in data["records"]:
        require(isinstance(record, dict) and set(record) == ROW_FIELDS, "Unexpected edition fields")
        isbn = record["publisher_isbn13"]
        require(valid_isbn13(isbn), f"Invalid ISBN-13: {isbn}")
        require(isbn in EXPECTED and isbn not in seen, f"Unknown or duplicate ISBN: {isbn}")
        seen.add(isbn)
        title, creator, series, fmt, date, pages, runtime, narrator, slug = EXPECTED[isbn]
        require(record["source_local_id"] == f"sns-public-isbn-{isbn}", f"Source-local ID mismatch: {isbn}")
        require((record["publisher_title"], record["publisher_creator"], record["publisher_series"]) == (title, creator, series), f"Title/creator/series changed: {isbn}")
        require((record["format"], record["publication_date"], record["page_count"], record["runtime_minutes"], record["narrator"]) == (fmt, date, pages, runtime, narrator), f"Publisher edition fields changed: {isbn}")
        require(datetime.date.fromisoformat(date) <= datetime.date(2026, 11, 3), f"Future date: {isbn}")
        expected_imprint = "Simon & Schuster Audio" if fmt == "UNABRIDGED_AUDIO_DOWNLOAD" else "Pocket Books/Star Trek"
        require(record["imprint"] == expected_imprint, f"Imprint mismatch: {isbn}")
        require(record["status"] == "PROPOSED_METADATA_ONLY", f"Admission forbidden: {isbn}")
        require(record["source_raw_sha256"] is None, f"Raw-source hash not verified: {isbn}")
        require(record["source_field_locator"] == "Product Details / ISBN13", f"Unsupported locator: {isbn}")
        parsed = urlparse(record["source_url"])
        require(parsed.scheme == "https" and parsed.netloc in ("www.simonandschuster.com", "parents.simonandschuster.com") and not parsed.query and not parsed.fragment, f"Unapproved publisher origin: {isbn}")
        if slug is None:
            require(parsed.netloc == "parents.simonandschuster.com" and parsed.path == f"/{isbn}", f"Publisher edition URL mismatch: {isbn}")
        else:
            require(parsed.netloc == "www.simonandschuster.com" and parsed.path == f"/books/{slug}/{isbn}", f"Publisher edition URL mismatch: {isbn}")
    require(seen == set(EXPECTED), "Incomplete publisher source inventory")


if __name__ == "__main__":
    validate(load(ROOT / "records.json"))
    print("PUBLIC_PUBLISHER_EDITION_OK: 7 distinct ISBN manifestations; no admission or private-source effect")
