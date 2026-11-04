#!/usr/bin/env python3
"""Fail-closed validator for seven held-only owner-OPF/publisher edition leads.

These checks are not live publisher retrieval, edition equivalence, content read,
source authentication or a new Work admission. Seven first-party bibliographic
claims are independently pinned against accepted owner OPF metadata claims.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).with_name("records.json")
ORIGINAL_OPF = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OPF_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
BASE = "3028765359001b90bc3e6b5c1835ee283b326e91"
PREFIX = "https://www.simonandschuster.com/books/"
FAMILY = "publisher:simonandschuster.com"
ANOMALY = "CARTER_CARMEN_HEADER_VS_BIO_OPF_UNRESOLVED"

# Reviewer-pinned, observed first-party publisher metadata; checked against
# independent source-local OPF metadata, not a global literary identity table.
EXPECTED = (
    ("0055", "Power Hungry", ("Howard Weinstein",), "0743420861", "9780743420860", 272,
     "Power-Hungry/Howard-Weinstein", None),
    ("0056", "Masks", ("John Vornholt",), "074342087X", "9780743420877", 288,
     "Masks/John-Vornholt", None),
    ("0057", "A Call to Darkness", ("Michael Jan Friedman",), "0743420896", "9780743420891", 272,
     "A-Call-to-Darkness/Michael-Jan-Friedman", None),
    ("0058", "A Rock and a Hard Place", ("Peter David",), "074342090X", "9780743420907", 288,
     "A-Rock-and-a-Hard-Place/Peter-David", None),
    ("0059", "Gulliver's Fugitives", ("Keith Sharee",), "0743420918", "9780743420914", 256,
     "Gullivers-Fugitives/Keith-Sharee", None),
    ("0060", "Doomsday World", ("Peter David", "Carter Carmen", "Michael Jan Friedman", "Robert Greenberger"),
     "0743420926", "9780743420921", 276, "Doomsday-World/Peter-David", ANOMALY),
    ("0061", "The Eyes of the Beholders", ("A.C. Crispin",), "0743420934", "9780743420938", 256,
     "The-Eyes-of-the-Beholders/A-C-Crispin", None),
)
PACKET_FIELDS = frozenset((
    "schema_version", "proposal_id", "baseline_accepted_main", "status", "opf_metadata_source",
    "opf_metadata_sha256", "publisher_upstream_family", "independent_publisher_families",
    "publisher_page_read_method", "publisher_page_read_utc", "publisher_snapshot_bytes_held",
    "full_text_read", "private_manifestation_binding_verified", "copyrighted_text_exported",
    "public_explorer_effect", "accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
    "coverage_effect", "artwork_release_effect", "synopsis_publication_effect", "held_edition_row_count", "rows",
))
ROW_FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_claimed_isbn10", "publisher_title", "creator_credits",
    "edition_format", "isbn13", "publisher_date_us", "publisher_extent_pages", "publisher_page",
    "source_anomaly", "held_synopsis",
))


def fail(msg: str) -> None:
    raise ValueError(msg)


def text_ok(v: object, maxlen: int = 180) -> bool:
    return isinstance(v, str) and 0 < len(v) <= maxlen and v == v.strip() and \
        all(unicodedata.category(char) not in ("Cc", "Cf", "Cs") and char not in "<>" for char in v)


def valid_isbn10(v: object) -> bool:
    if not isinstance(v, str) or not re.fullmatch(r"[0-9]{9}[0-9X]", v):
        return False
    return sum((10 - i) * (10 if n == "X" else int(n)) for i, n in enumerate(v)) % 11 == 0


def to_isbn13(v: str) -> str:
    raw = "978" + v[:9]
    check = (-sum((1 if i % 2 == 0 else 3) * int(n) for i, n in enumerate(raw))) % 10
    return raw + str(check)


def valid_isbn13(v: object) -> bool:
    return isinstance(v, str) and bool(re.fullmatch(r"[0-9]{13}", v)) and \
        sum((1 if i % 2 == 0 else 3) * int(n) for i, n in enumerate(v)) % 10 == 0


def date_ok(v: object) -> bool:
    if not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return False
    try:
        dt.date.fromisoformat(v)
        return True
    except ValueError:
        return False


def validate(packet: object, original_opf: object) -> int:
    if not isinstance(packet, dict) or frozenset(packet) != PACKET_FIELDS:
        fail("Unreviewed packet schema or injected properties")
    expected_top = {
        "schema_version": "trek-lit-opf-publisher-seven-held-v1",
        "proposal_id": "LIT-OPF-PUBLISHER-07-20261104",
        "baseline_accepted_main": BASE,
        "status": "HELD_METADATA_ONLY_NOT_ACCEPTED",
        "opf_metadata_source": str(ORIGINAL_OPF.relative_to(ROOT)),
        "opf_metadata_sha256": OPF_SHA,
        "publisher_upstream_family": FAMILY,
        "independent_publisher_families": 1,
        "publisher_page_read_method": "FIRST_PARTY_PUBLISHER_WEB_PAGE_METADATA_AND_DESCRIPTION",
        "publisher_page_read_utc": "2026-11-04",
        "publisher_snapshot_bytes_held": False,
        "full_text_read": False,
        "private_manifestation_binding_verified": False,
        "copyrighted_text_exported": False,
        "public_explorer_effect": "NONE",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "accepted_evidence_effect": "NONE",
        "coverage_effect": "NONE",
        "artwork_release_effect": "NONE",
        "synopsis_publication_effect": "NONE",
        "held_edition_row_count": 7,
    }
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in expected_top.items()):
        fail("Held-only scope, baseline, source SHA or upstream lineage altered")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Underlying accepted owner OPF public metadata bytes differ")
    if not isinstance(original_opf, dict) or original_opf.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       original_opf.get("ebook_full_text_read") is not False or \
       original_opf.get("edition_binding_verified") is not False or \
       original_opf.get("work_admission_effect") != "NONE" or \
       not isinstance(original_opf.get("rows"), list) or len(original_opf["rows"]) != 347:
        fail("Owner OPF inventory is not the accepted metadata-only surface")
    original_by_id = {r.get("source_local_id"): r for r in original_opf["rows"] if isinstance(r, dict)}
    if len(original_by_id) != 347:
        fail("Owner OPF source-local IDs are duplicate or incomplete")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 7:
        fail("Expected exactly seven held edition observations")
    for row, (num, title, creators, isbn10, isbn13, pages, slug, anomaly) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != ROW_FIELDS:
            fail("Unexpected typed edition fields")
        opf_id = f"opf-local:{num}"
        opf = original_by_id.get(opf_id)
        if not isinstance(opf, dict) or opf.get("parse_status") != "PARSED" or \
           opf.get("isbn_checksum_valid") != [isbn10] or \
           not isinstance(opf.get("opf_entry_sha256"), str):
            fail(f"Owner OPF metadata cannot substantiate ISBN claim {opf_id}")
        if row["opf_local_id"] != opf_id or row["opf_entry_sha256"] != opf["opf_entry_sha256"] or \
           row["opf_claimed_isbn10"] != isbn10 or not valid_isbn10(row["opf_claimed_isbn10"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(row["isbn13"]) or \
           to_isbn13(row["opf_claimed_isbn10"]) != row["isbn13"]:
            fail(f"Source-local ISBN/entry crosswalk did not hold {opf_id}")
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(name) for name in row["creator_credits"]) or \
           row["edition_format"] != "EBOOK" or row["source_anomaly"] != anomaly:
            fail(f"Official publisher title/creator/format/anomaly differs {opf_id}")
        if not isinstance(row["publisher_extent_pages"], int) or \
           isinstance(row["publisher_extent_pages"], bool) or row["publisher_extent_pages"] != pages or \
           row["publisher_date_us"] != "2000-09-22" or not date_ok(row["publisher_date_us"]):
            fail(f"Publisher date and extent claim differs {opf_id}")
        url = f"{PREFIX}{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != "www.simonandschuster.com" or \
           parsed.query or parsed.fragment or row["publisher_page"] != url:
            fail(f"Publisher link/edition attribution differs {opf_id}")
        if not text_ok(row["held_synopsis"], 300):
            fail(f"Source-described original synopsis is absent/unsafe {opf_id}")
    return 7


def main() -> None:
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    original_opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    print(f"PASS: {validate(packet, original_opf)} HELD metadata-only publisher/OPF edition leads; no Work, Evidence, close-read or coverage effect")


if __name__ == "__main__":
    main()
