#!/usr/bin/env python3
"""Fail-closed invariants for this unadmitted publisher-edition proposal."""

from __future__ import annotations

import datetime
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    """Validate even when Python is run with optimization enabled."""
    if not condition:
        raise ValueError(message)


def isbn13_valid(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 13 or not value.isascii() or not value.isdigit():
        return False
    return sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(value)) % 10 == 0


def load_strict_json(path: Path) -> dict:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def validate(data: dict) -> None:
    require(data["schema_version"] == "1.0.0", "Unexpected proposal schema version")
    require(data["proposal_only"] is True, "Proposal flag must remain true")
    require(data["independence_group"] == "publisher:simonandschuster.com", "Publisher lineage changed")
    require("NO_RAW_BYTE_CUSTODY" in data["source_access"], "Source custody is overstated")
    require(
        data["accepted_effects"] == {key: "NONE" for key in ("sources", "works", "bindings", "coverage")},
        "Admission or coverage effect is forbidden",
    )
    works = data["works"]
    editions = data["editions"]
    require(len(works) == 3, "Expected three proposed Works")
    require(len(editions) == 9, "Expected nine publisher editions")
    work_ids = [work["candidate_work_id"] for work in works]
    require(len(set(work_ids)) == 3, "Duplicate Work candidate ID")
    require(
        all(work["status"] == "PROPOSED" and work["work_type"] == "NOVEL" for work in works),
        "Unexpected Work status or type",
    )
    require(all(work["medium"] == "LITERATURE" for work in works), "Unexpected Work medium")
    counts = Counter()
    formats_by_work = defaultdict(set)
    isbn_seen = set()
    for edition in editions:
        isbn = edition["isbn13"]
        require(isbn13_valid(isbn), f"Invalid ISBN-13: {isbn}")
        require(isbn not in isbn_seen, f"Duplicate ISBN-13: {isbn}")
        isbn_seen.add(isbn)
        work_id = edition["candidate_work_id"]
        require(work_id in work_ids, f"Unknown Work candidate: {work_id}")
        counts[work_id] += 1
        formats_by_work[work_id].add(edition["format"])
        require(edition["status"] == "PROPOSED_METADATA_ONLY", f"Unexpected edition status: {isbn}")
        require(edition["raw_response_sha256"] is None, f"Unverified source hash asserted: {isbn}")
        require(edition["source_version"] is None, f"Unverified source version asserted: {isbn}")
        parsed = urlparse(edition["publisher_product_url"])
        require(
            parsed.scheme == "https" and parsed.netloc == "www.simonandschuster.com",
            f"Unexpected publisher URL origin: {isbn}",
        )
        require(
            parsed.path.startswith("/books/") and parsed.path.endswith("/" + isbn),
            f"ISBN does not match publisher locator: {isbn}",
        )
        date = datetime.date.fromisoformat(edition["publisher_publication_date"])
        require(date <= datetime.date(2026, 11, 3), f"Future publication date: {isbn}")
        require(bool(edition["publisher_extent"]), f"Missing edition extent: {isbn}")
        if edition["format"] == "UNABRIDGED_AUDIO_DOWNLOAD":
            require(
                bool(edition["narrator"]) and edition["publisher_imprint"] == "Simon & Schuster Audio",
                f"Missing audiobook narrator or imprint: {isbn}",
            )
            require("hours" in edition["publisher_extent"], f"Missing audiobook runtime: {isbn}")
        else:
            require(edition["format"] in ("TRADE_PAPERBACK", "EBOOK"), f"Unknown edition format: {isbn}")
            require(edition["narrator"] is None, f"Unexpected narrator on nonaudio edition: {isbn}")
            require(edition["publisher_extent"].endswith(" pages"), f"Unexpected page extent: {isbn}")
    require(all(counts[work_id] == 3 for work_id in work_ids), "Each Work must have three manifestations")
    require(
        all(
            formats_by_work[work_id] == {"TRADE_PAPERBACK", "EBOOK", "UNABRIDGED_AUDIO_DOWNLOAD"}
            for work_id in work_ids
        ),
        "Each Work must have a paperback, eBook, and audio edition",
    )


if __name__ == "__main__":
    validate(load_strict_json(ROOT / "records.json"))
    print("PASS: three proposed Works, nine distinct publisher ISBN manifestations; zero accepted effects")
