#!/usr/bin/env python3
"""Offline source-local custody gate for seven public S&S ISBN product pages."""
from __future__ import annotations

import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "records.json"

# ISBN-specific first-party Product Details and title/format fields, read 2026-11-03.
# Tuple: title, author, publisher series, edition format, imprint, date, pages, slug.
EXPECTED = {
    "9781668096642": ("Identity Theft", "Greg Cox", "Star Trek: The Original Series", "EBOOK", "Pocket Books/Star Trek", "2025-12-02", 352, "Identity-Theft/Greg-Cox/Star-Trek-The-Original-Series"),
    "9781668096628": ("Identity Theft", "Greg Cox", "Star Trek: The Original Series", "TRADE_PAPERBACK", "Pocket Books/Star Trek", "2025-12-02", 352, "Identity-Theft/Greg-Cox/Star-Trek-The-Original-Series"),
    "9781668050057": ("Lost to Eternity", "Greg Cox", "Star Trek: The Original Series", "TRADE_PAPERBACK", "Pocket Books/Star Trek", "2024-07-23", 400, "Lost-to-Eternity/Greg-Cox/Star-Trek-The-Original-Series"),
    "9781668050064": ("Lost to Eternity", "Greg Cox", "Star Trek: The Original Series", "EBOOK", "Gallery Books", "2024-07-23", 400, "Lost-to-Eternity/Greg-Cox/Star-Trek-The-Original-Series"),
    "9781982113599": ("Collateral Damage", "David Mack", "Star Trek: The Next Generation", "EBOOK", "Pocket Books/Star Trek", "2019-10-08", 384, "Collateral-Damage/David-Mack/Star-Trek-The-Next-Generation"),
    "9781982175214": ("Star Trek: Picard: Rogue Elements", "John Jackson Miller", "Star Trek: Picard", "EBOOK", "Pocket Books/Star Trek", "2021-08-17", 416, "Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller/Star-Trek-Picard"),
    "9781982113308": ("The Captain's Oath", "Christopher L. Bennett", "Star Trek: The Original Series", "EBOOK", "Pocket Books/Star Trek", "2019-05-28", 400, "The-Captains-Oath/Christopher-L-Bennett/Star-Trek-The-Original-Series"),
}

PACKET_KEYS = {
    "schema_version", "batch_id", "accepted_base_sha", "observed_utc_date", "role", "proposal_only",
    "source_class", "source_independence_group", "raw_publisher_html_captured", "private_owner_data_used",
    "image_or_book_bytes_captured", "source_admission_effect", "work_admission_effect",
    "source_work_binding_effect", "explorer_effect", "research_coverage_effect", "record_count", "records",
}
ROW_KEYS = {
    "source_local_id", "publisher_title", "publisher_creator", "publisher_series", "publisher_isbn13",
    "format", "imprint", "publication_date", "page_count", "source_url", "source_field_locator",
    "source_page_access", "source_raw_sha256", "status",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path = RECORDS) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 100_000,
            "missing, symlinked or oversized records file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def valid_isbn13(isbn: object) -> bool:
    return (isinstance(isbn, str) and len(isbn) == 13 and isbn.isascii() and isbn.isdigit()
            and sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(isbn)) % 10 == 0)


def validate(data: object) -> None:
    require(isinstance(data, dict) and set(data) == PACKET_KEYS, "closed packet schema")
    envelope = {
        "schema_version": "1.0.0",
        "batch_id": "SNS.PUBLIC.EDITIONS.FIVE.TITLES.20261103.001",
        "accepted_base_sha": "37d6863da94b8ccfa64af81dbe7ed179272241bc",
        "observed_utc_date": "2026-11-03",
        "role": "LIBRARIAN",
        "proposal_only": True,
        "source_class": "PUBLIC_FIRST_PARTY_PUBLISHER_PRODUCT_METADATA",
        "source_independence_group": "publisher:simonandschuster.com",
        "raw_publisher_html_captured": False,
        "private_owner_data_used": False,
        "image_or_book_bytes_captured": False,
        "source_admission_effect": "NONE",
        "work_admission_effect": "NONE",
        "source_work_binding_effect": "NONE",
        "explorer_effect": "NONE",
        "research_coverage_effect": "NONE",
        "record_count": 7,
    }
    for name, expected in envelope.items():
        require(type(data[name]) is type(expected) and data[name] == expected, f"unsafe packet field: {name}")
    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == 7, "seven exact ISBN pages required")

    observed = set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "closed row schema; no private data or cover fields")
        isbn = row["publisher_isbn13"]
        require(valid_isbn13(isbn), "invalid ISBN-13 checksum")
        require(isbn in EXPECTED and isbn not in observed, "unknown or duplicate publisher ISBN")
        observed.add(isbn)
        title, author, series, fmt, imprint, date, pages, slug = EXPECTED[isbn]
        fields = ("publisher_title", "publisher_creator", "publisher_series", "format", "imprint", "publication_date", "page_count")
        values = (title, author, series, fmt, imprint, date, pages)
        require(tuple(row[name] for name in fields) == values and type(row["page_count"]) is int,
                f"unverified title/creator/format/imprint/date/length for {isbn}")
        require(datetime.date.fromisoformat(date) <= datetime.date(2026, 11, 3), "future publisher date")
        require(row["source_local_id"] == f"sns-edition-public-{isbn}", "source local ID mismatch")
        url = row["source_url"]
        require(isinstance(url, str), "source URL is not text")
        parsed = urlsplit(url)
        require(url == f"https://www.simonandschuster.com/books/{slug}/{isbn}" and
                parsed.scheme == "https" and parsed.hostname == "www.simonandschuster.com" and
                not parsed.username and not parsed.password and parsed.port is None and
                not parsed.query and not parsed.fragment, "wrong exact publisher product URL")
        require(row["source_field_locator"] == "Product Details / ISBN13", "source locator drift")
        require(row["source_page_access"] == "FIRST_PARTY_RENDERED_PRODUCT_TEXT_READ", "unverified source access")
        require(row["source_raw_sha256"] is None, "raw HTML bytes not archived/hash-verified")
        require(row["status"] == "PROPOSED_METADATA_ONLY", "forbidden edition or Work admission")
    require(observed == set(EXPECTED), "incomplete source-local edition batch")


if __name__ == "__main__":
    validate(load())
    print("PASS: 7 public publisher ISBN edition observations / five titles; no private source, rights, Work or coverage effects")
