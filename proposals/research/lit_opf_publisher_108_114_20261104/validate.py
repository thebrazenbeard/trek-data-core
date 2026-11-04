#!/usr/bin/env python3
"""Fail-closed publisher/owner OPF lead validator. Local HELD only; not Work admission."""

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
    "schema_version": "trek-lit-opf-publisher-108-114-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0108-0114-20261104",
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

# Literal owner data, independent official publisher rows, anomalies, paraphrase hashes.
# Publisher eBook ISBNs are NOT claimed as the owner's private EPUB manifestations.
EXPECTED = (
    (108, "Star Trek - TNG - 63 - Maximum Warp, Book Two", ("Dave Galanter and Greg Brodeur",), None,
     "Maximum Warp: Book Two", None, ("Dave Galanter", "Greg Brodeur"),
     "9780743419536", "2001-07-08", 240, "Maximum-Warp-Book-Two/Dave-Galanter",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_TNG_063_ORDINAL_NOT_ATTESTED_ON_PUBLISHER_US_EBOOK_PAGE_AND_ISBN_ABSENT",
     "a3e50c62df9b0123790d7c1512c3fe00aed6bae1e5de7c54a67f2175394a4971"),
    (109, "A Hard Rain", ("Dean Wesley Smith",), "074341926X", "A Hard Rain", None,
     ("Dean Wesley Smith",), "9780743419277", "2002-03-12", 256,
     "A-Hard-Rain/Dean-Wesley-Smith", "VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION",
     "VALID_OWNER_ISBN_9780743419260_DIFFERS_FROM_PUBLISHER_EBOOK_9780743419277_LOCAL_FORMAT_UNVERIFIED",
     "ef9802bdbafb22455dd9c05769c31a44a93c4c280af38a5221eee6b7bf7296c0"),
    (110, "A Time for War, A Time for Peace", ("Keith R.A. DeCandido",), None,
     "A Star Trek: The Next Generation: Time #9: A Time for War, A Time for Peace", None,
     ("Keith R. A. DeCandido",), "9780743499972", "2004-10-01", 384,
     "A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_CREATOR_INITIAL_SPACING_VARIANT_AND_ISBN_ABSENT_UNRESOLVED",
     "0760738ffe1bd99228c06eddeff5f4a2fb61dd7d1344ef7ea94d2454e5f1b7da"),
    (111, "ATimetoBeBorn", (), None,
     "A Star Trek: The Next Generation: Time #1: A Time to Be Born", None,
     ("John Vornholt",), "9780743491495", "2004-02-01", 304,
     "A-Star-Trek-The-Next-Generation-Time-1-A-Time-to-Be-Born/John-Vornholt",
     "UNVERIFIED_LOCAL_TITLE_ONLY", "LOCAL_TITLE_CONCATENATED_WITH_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "a93a695c968d4c4aed36a847191fd5878317e592bd99a67cf66ec43cf53340c6"),
    (112, "A Time to Die", (), None,
     "A Star Trek: The Next Generation: Time #2: A Time to Die", None,
     ("John Vornholt",), "9780743499446", "2004-03-02", 320,
     "A-Star-Trek-The-Next-Generation-Time-2-A-Time-to-Die/John-Vornholt",
     "UNVERIFIED_LOCAL_TITLE_ONLY", "LOCAL_CREATOR_AND_ISBN_ABSENT_UNRESOLVED",
     "8aa8f385d9df50ee997c52c91b674335ccebe5990c0c0ab71de4c3be703cfa4f"),
    (113, "A Time to Harvest", ("Dayton Ward & Kevin Dilmore",), None,
     "Time #4: A Time to Harvest", None, ("Kevin Dilmore", "Dayton Ward"),
     "9780743488952", "2004-05-01", 352, "Time-4-A-Time-to-Harvest/Kevin-Dilmore",
     "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_CREATOR_ORDER_REVERSED_FROM_PUBLISHER_AND_ISBN_ABSENT_UNRESOLVED",
     "51d102621735e561e23dde12a1aaeb6672deab0f97ab23b98f180025143e6cc6"),
    (114, "A Time to Hate", ("Robert Greenberger",), None, "A Time to Hate", None,
     ("Robert Greenberger",), "9780743462907", "2004-07-01", 304,
     "A-Time-to-Hate/Robert-Greenberger", "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_ISBN_ABSENT_UNRESOLVED",
     "871732846c2c985ce0da11c818a1a5b2fd7cefea060d5f09dd688aa91206fc2f"),
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
            fail(f"Owner OPF lineage/identity differed {local_id}")
        if isbn10 is None:
            if source.get("isbn_checksum_valid") != [] or row["opf_isbn13_checksum_conversion"] is not None:
                fail(f"Nonexistent owner ISBN was backfilled {local_id}")
            no_isbn += 1
        else:
            converted = to_isbn13(isbn10)
            if not valid_isbn10(isbn10) or source.get("isbn_checksum_valid") != [isbn10] or \
               row["opf_isbn13_checksum_conversion"] != converted:
                fail(f"Owner ISBN10 and literal checksum differ {local_id}")
            if num != 109 or converted != "9780743419260" or converted == isbn13 or \
               state != "VALID_OPF_ISBN_NOT_BOUND_TO_PUBLISHER_EDITION":
                fail(f"Unsupported owner/publisher edition binding {local_id}")
            divergent += 1
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
    if (matched, divergent, no_isbn) != (0, 1, 6):
        fail("Expected zero ISBN alignments, one valid divergent owner ISBN and six ISBN-absent holds")
    return (7, matched, divergent, no_isbn)


def main() -> None:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    count, match, divergent, absent = validate(doc, source)
    print(f"PASS: {count} HELD local leads, {match} ISBN checksum aligned, {divergent} owner ISBN not "
          f"bound to publisher eBook edition, {absent} owner ISBN-absent; zero accepted Work/coverage effect")


if __name__ == "__main__":
    main()
