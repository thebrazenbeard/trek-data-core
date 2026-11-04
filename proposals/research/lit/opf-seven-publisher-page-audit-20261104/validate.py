"""Offline invariants for an independently *visually observed* publisher recheck.

This script does not fetch web pages or claim private owner-host source access.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "proposals/research/opf-seven-official-editions-20261103/observations.json"
SOURCE_SHA256 = "3d3aa4703bb2ab47291aa7fadb487320ed4cbef68c7456fabe09c52a1e848d42"

# Observed exact rendered Product Details, kept independent of the input packet.
# local-id, publisher-ISBN13, title, byline, format, imprint, ISO date, pages, series number.
EXPECTED = (
    ("0110", "9781982134907", "A Star Trek: The Next Generation: Time #9: A Time for War, A Time for Peace", "Keith R. A. DeCandido", "TRADE_PAPERBACK", "Gallery Books", "2019-05-18", 384, 9),
    ("0150", "9780743419628", "Yesterday's Son", "A.C. Crispin", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 192, 11),
    ("0181", "9780743420013", "Doctor's Orders", "Diane Duane", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 291, 50),
    ("0275", "9780743475631", "Homecoming", "Christie Golden", "EBOOK", "Pocket Books/Star Trek", "2003-05-12", 288, None),
    ("0296", "9780743420488", "The Heart of the Warrior", "John Gregory Betancourt", "EBOOK", "Pocket Books/Star Trek", "2000-09-22", 288, 17),
    ("0326", "9780743464574", "Star Trek: Enterprise: Shockwave", "Paul Ruditis", "EBOOK", "Pocket Books/Star Trek", "2002-10-30", 256, None),
    ("0335", "9780743455725", "Fire On High", "Peter David", "EBOOK", "Pocket Books/Star Trek", "2002-08-04", 288, 6),
)
EBOOK_0110 = ("9780743499972", "EBOOK", "Pocket Books/Star Trek", "2004-10-01", 384)


def isbn13_valid(value: str) -> bool:
    if len(value) != 13 or not value.isascii() or not value.isdecimal():
        return False
    return sum(int(ch) * (1 if ix % 2 == 0 else 3) for ix, ch in enumerate(value)) % 10 == 0


def validate(root: Path = ROOT) -> tuple[int, int]:
    source = root / SOURCE.relative_to(ROOT)
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("pinned accepted held publisher proposal changed")
    doc = json.loads(raw)
    rows = doc["rows"]
    if len(rows) != 7 or doc.get("publisher_family_independent_witnesses") != 1:
        raise ValueError("seven rows and one publisher lineage required")
    if (doc.get("coverage_effect"), doc.get("artwork_effect"), doc.get("public_explorer_release"),
        doc.get("global_work_identity"), doc.get("owner_private_edition_equivalence")) != (
        "NONE", "NONE", "HELD", "NOT_RECONCILED", "NOT_VERIFIED"):
        raise ValueError("cannot promote coverage, release or identity")
    if doc.get("publisher_pages_byte_snapshotted") is not False:
        raise ValueError("no raw publisher byte snapshot was captured")
    for row, expected in zip(rows, EXPECTED, strict=True):
        local, isbn, title, byline, fmt, imprint, date, pages, ordinal = expected
        observed = (row["opf_source_local_id"].split(":")[-1], row["publisher_isbn13"],
                    row["publisher_title"], row["publisher_byline"], row["publisher_format"],
                    row["publisher_imprint"], row["publisher_date"], row["publisher_pages"],
                    row["publisher_series_ordinal"])
        if observed != expected:
            raise ValueError(f"held publisher page metadata mismatch for {local}")
        if not isbn13_valid(isbn) or not row["publisher_url"].startswith("https://www.simonandschuster.com/books/") or not row["publisher_url"].endswith("/" + isbn):
            raise ValueError(f"bad publisher ISBN/page locator for {local}")
    first = rows[0]
    linked = first["source_isbn10_corresponding_publisher_ebook"]
    if tuple(linked[k] for k in ("isbn13", "format", "imprint", "date", "pages")) != EBOOK_0110:
        raise ValueError("held 2004 ebook edition changed")
    if not isbn13_valid(linked["isbn13"]) or not linked["url"].endswith("/" + linked["isbn13"]):
        raise ValueError("invalid distinct 2004 ebook locator")
    if linked["private_source_edition_equivalence"] != "NOT_VERIFIED":
        raise ValueError("private source edition must remain unverified")
    if first["original_opf_xml_isbn10_literal"] != "ISBN 0-7434-9997-2":
        raise ValueError("original case-sensitive identifier receipt changed")
    if first["publisher_isbn13"] == linked["isbn13"]:
        raise ValueError("2019 trade and 2004 ebook must remain separate editions")
    if rows[3]["prior_same_family_publisher_candidate"] != "SSEBOOK-VOY-HOMECOMING-9780743475631":
        raise ValueError("same-family Homecoming duplicate not recorded")
    if "New Frontiers #6" not in rows[-1]["unresolved_difference"]:
        raise ValueError("New Frontier vs TNG publisher disagreement missing")
    return len(rows), len(rows) + 1


if __name__ == "__main__":
    print("HELD page recheck pins: source-local rows / publisher products:", *validate())
