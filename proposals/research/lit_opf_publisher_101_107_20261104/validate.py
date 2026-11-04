#!/usr/bin/env python3
"""Local fail-closed publisher-versus-OPF evidence validator; no Work admission."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proposals.research.lit_opf_publisher_seven_20261104.validate import (  # noqa: E402
    BASE, FAMILY, OPF_SHA, ORIGINAL_OPF, date_ok, fail, text_ok,
    to_isbn13, valid_isbn10, valid_isbn13,
)

DATA = Path(__file__).with_name("records.json")
FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_local_title", "opf_local_creator",
    "opf_claimed_isbn10", "opf_isbn13_checksum_conversion", "opf_edition_crosswalk_state",
    "publisher_title", "publisher_book_part", "creator_credits", "publisher_host",
    "publisher_page", "isbn13", "edition_format", "publisher_date_us",
    "publisher_extent_pages", "source_anomaly", "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-101-107-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0101-0107-20261104",
    "baseline_accepted_main": BASE,
    "status": "HELD_METADATA_ONLY_NOT_ACCEPTED",
    "opf_metadata_source": str(ORIGINAL_OPF.relative_to(ROOT)),
    "opf_metadata_sha256": OPF_SHA,
    "publisher_upstream_family": FAMILY,
    "independent_publisher_families": 1,
    "publisher_page_read_method": "OFFICIAL_FIRST_PARTY_PRODUCT_PAGE_METADATA_AND_DESCRIPTION",
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

# Each tuple pins: ID, literal owner OPF title and creators, OPF ISBN10,
# S&S publisher title, optional explicit book part, creators, publisher ISBN13,
# date, extent, URL slug, evidence state, source anomaly, paraphrase SHA256.
EXPECTED = (
    (101, "Star Trek - TNG 056 Double Helix - The First Virtue", (), None,
     "The First Virtue", None, ("Michael Jan Friedman", "Christie Golden"),
     "9780743421362", "2000-09-22", 304, "The-First-Virtue/Michael-Jan-Friedman",
     "UNVERIFIED_LOCAL_TITLE_ONLY", "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "dbb91d5169f3f67512222567c6edf678cc7691af03cf02806d00c33948e0acd8"),
    (102, "THE FORGOTTEN WAR", ("William R. Forstchen",), "0743421388",
     "The Forgotten War", None, ("William R. Forstchen",),
     "9780743421386", "1999-09-01", 304, "The-Forgotten-War/William-R-Forstchen",
     "ISBN_CHECKSUM_ALIGNMENT_ONLY", None,
     "233553df39555a22d03c35e1c1e0c9b1ed89864bfd4915cff47741d3b56c2cdf"),
    (103, "GEMWORLD: BOOK ONE OF TWO", ("JOHN VORNHOLT",), "074342140X",
     "Gemworld", "Book One Of Two", ("John Vornholt",),
     "9780743406772", "2000-02-05", 272, "Gemworld/John-Vornholt",
     "VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION",
     "VALID_OWNER_ISBN_DIFFERS_FROM_CURRENT_PUBLISHER_GEMWORLD_ONE_EDITION_UNRESOLVED",
     "367a8653e476f068e449da64420ac1eee22f59867bcc4a80f0a78257ba151f1b"),
    (104, "GEMWORLD: BOOK TWO OF TWO", ("JOHN VORNHOLT",), "0743421426",
     "Gemworld", "Book Two Of Two", ("John Vornholt",),
     "9780743406789", "2000-02-01", 272, "Gemworld/John-Vornholt",
     "VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION",
     "VALID_OWNER_ISBN_DIFFERS_FROM_CURRENT_PUBLISHER_GEMWORLD_TWO_EDITION_UNRESOLVED",
     "085006356017a9f25005d825f285927b69a1a78842183078da15d6b91f3b2899"),
    (105, "Star Trek -Next Generation - Tooth and Claw.", ("Doranna Durgin",), None,
     "Tooth and Claw", None, ("Doranna Durgin",),
     "9780743419499", "2001-07-11", 272, "Tooth-and-Claw/Doranna-Durgin",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_TITLE_TRAILING_PUNCTUATION_AND_ISBN_ABSENT_UNRESOLVED",
     "71600e952e9f49958bd42d147f3cc05ca5743ce4965933cd9ba33a19d7a1ca70"),
    (106, "Star Trek Next Generations - Diplomatic Implausibility", ("Keith R.A. DeCandido",), None,
     "Diplomatic Implausibility", None, ("Keith R. A. DeCandido",),
     "9780743419505", "2001-07-07", 272, "Diplomatic-Implausibility/Keith-R-A-DeCandido",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_NEXT_GENERATIONS_TITLE_VARIANT_AND_ISBN_ABSENT_UNRESOLVED",
     "f2f921f1acb3f5a6962e0a54562f7368844c45d3f4baebe95c774ddc08ec1abf"),
    (107, "Star Trek - TNG - 62 - Maximum Warp, Book One", ("Dave Galanter and Greg Brodeur",), None,
     "Maximum Warp: Book One", None, ("Greg Brodeur", "Dave Galanter"),
     "9780743419529", "2001-04-11", 256, "Maximum-Warp-Book-One/Greg-Brodeur",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_CREATOR_ORDER_REVERSED_FROM_PUBLISHER_AND_ISBN_ABSENT_UNRESOLVED",
     "f91ca4a3d1b7999618b8be612c84c60a72247622794911fa7cd6cf56b3509a7b"),
)


def validate(packet: object, original: object) -> tuple[int, int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unexpected schema or injected acceptance/rights fields")
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in TOP.items()):
        fail("HELD baseline, source, or scope effects changed")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Owner OPF metadata source fingerprint changed")
    if not isinstance(original, dict) or original.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       original.get("ebook_full_text_read") is not False or original.get("edition_binding_verified") is not False or \
       original.get("work_admission_effect") != "NONE" or \
       not isinstance(original.get("rows"), list) or len(original["rows"]) != 347:
        fail("Owner OPF source has different rights, binding, or row structure")
    source_by_id = {r.get("source_local_id"): r for r in original["rows"] if isinstance(r, dict)}
    if len(source_by_id) != 347:
        fail("Owner source local IDs duplicate or missing")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 7:
        fail("Expected exactly seven held local entries")
    matched = divergent = no_isbn = 0
    for row, (num, local_title, local_creators, isbn10, title, part, creators,
              isbn13, date, pages, slug, state, anomaly, summary_hash) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != FIELDS:
            fail("Unreviewed row properties or confidential content")
        local_id = f"opf-local:{num:04d}"
        source = source_by_id.get(local_id)
        if not isinstance(source, dict) or source.get("parse_status") != "PARSED" or \
           source.get("title") != [local_title] or source.get("creator") != list(local_creators):
            fail(f"Original OPF local title/creator differs {local_id}")
        if row["opf_local_id"] != local_id or row["opf_entry_sha256"] != source.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_local_creator"] != list(local_creators) or \
           row["opf_claimed_isbn10"] != isbn10 or row["opf_edition_crosswalk_state"] != state:
            fail(f"Original owner OPF lineage/identity differed {local_id}")
        if isbn10 is None:
            if source.get("isbn_checksum_valid") != [] or row["opf_isbn13_checksum_conversion"] is not None:
                fail(f"Nonexistent owner ISBN was backfilled {local_id}")
            no_isbn += 1
        else:
            converted = to_isbn13(isbn10)
            if not valid_isbn10(isbn10) or source.get("isbn_checksum_valid") != [isbn10] or \
               row["opf_isbn13_checksum_conversion"] != converted:
                fail(f"Owner ISBN10 and literal checksum differ {local_id}")
            if num in (103, 104):
                if converted == isbn13 or state != "VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION":
                    fail(f"Unsupported Gemworld edition binding silently inferred {local_id}")
                divergent += 1
            elif converted != isbn13 or state != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
                fail(f"Owner/publisher checksum alignment falsely claimed {local_id}")
            else:
                matched += 1
        if row["publisher_title"] != title or row["publisher_book_part"] != part or \
           row["creator_credits"] != list(creators) or not all(text_ok(c) for c in row["creator_credits"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(isbn13) or \
           row["edition_format"] != "EBOOK" or row["source_anomaly"] != anomaly or \
           row["private_source_edition_verified"] is not False:
            fail(f"Publisher edition identity/anomaly altered {local_id}")
        if row["publisher_date_us"] != date or not date_ok(row["publisher_date_us"]) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Official publication date/extent altered {local_id}")
        host = "www.simonandschuster.com"
        url = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != host or \
           parsed.query or parsed.fragment or row["publisher_host"] != host or row["publisher_page"] != url:
            fail(f"Publisher page spoof or edition swap {local_id}")
        summary = row["held_synopsis"]
        if not text_ok(summary, 300) or hashlib.sha256(summary.encode("utf-8")).hexdigest() != summary_hash:
            fail(f"Original metadata paraphrase changed {local_id}")
    if (matched, divergent, no_isbn) != (1, 2, 4):
        fail("Expected one checksum alignment, two unbound valid ISBNs and four ISBN-absent holds")
    return (7, matched, divergent, no_isbn)


def main() -> None:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    count, match, divergent, absent = validate(doc, source)
    print(f"PASS: {count} HELD local leads, {match} ISBN checksum aligned, {divergent} valid owner ISBNs "
          f"not bound to publisher editions, {absent} owner ISBN-absent; zero accepted Work/coverage effect")


if __name__ == "__main__":
    main()
