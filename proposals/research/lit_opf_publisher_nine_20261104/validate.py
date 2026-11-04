#!/usr/bin/env python3
"""Strict local validator: nine HELD OPF title/ISBN to first-party publisher leads.

Unlike a source-to-Work reconciliation, this supports an explicit title-only
unverified row. Publisher web retrieval is not authenticated by these tests.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from proposals.research.lit_opf_publisher_seven_20261104.validate import (
    OPF_SHA, ORIGINAL_OPF, BASE, FAMILY, date_ok, fail, text_ok,
    valid_isbn10, valid_isbn13, to_isbn13,
)

DATA = Path(__file__).with_name("records.json")
ROW_FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_local_title", "opf_claimed_isbn10",
    "opf_edition_crosswalk_state", "publisher_title", "creator_credits", "publisher_host", "publisher_page",
    "isbn13", "edition_format", "publisher_date_us", "publisher_extent_pages", "source_anomaly",
    "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-nine-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-09-20261104",
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
    "held_edition_row_count": 9,
}

# Publisher product metadata values reviewed on 2026-11-04; local OPF title
# preserved independently, including its source typo at 0067. Host `.net`
# at 0062 is publisher-owned same lineage, not a second source family.
EXPECTED = (
    (62, "EXILES", "Exiles", ("Howard Weinstein",), "0743420942", "9780743420945", 288,
     "Exiles/Howard-Weinstein", "net", None, "2000-09-22"),
    (63, "FORTUNE'S LIGHT", "Fortune's Light", ("Michael Jan Friedman",), "0743420950", "9780743420952", 288,
     "Fortunes-Light/Michael-Jan-Friedman", "com", None, "2000-09-22"),
    (64, "CONTAMINATION", "Contamination", ("John Vornholt",), "0743420969", "9780743420969", 288,
     "Contamination/John-Vornholt", "com", None, "2000-09-22"),
    (65, "BOOGEYMEN", "Boogeymen", ("Mel Gilden",), "0743420977", "9780743420976", 244,
     "Boogeymen/Mel-Gilden", "com", None, "2000-09-22"),
    (66, "Star Trek - Q-In-Law", "Q-in-Law", ("Peter David",), None, "9780671040994", 252,
     "Q-in-Law/Peter-David", "com", "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED", "1991-10-01"),
    (67, "PRECHANCE TO DREAM", "Perchance to Dream", ("Howard Weinstein",), "0743420993", "9780743420990", 288,
     "Perchance-to-Dream/Howard-Weinstein", "com", "OPF_PRECHANCE_VS_PUBLISHER_PERCHANCE_UNRESOLVED", "2000-09-22"),
    (68, "SPARTACUS", "Spartacus", ("T. L. Mancour",), "0743421000", "9780743421003", 288,
     "Spartacus/T-L-Mancour", "com", None, "2000-09-22"),
    (69, "CHAINS OF COMMAND", "Chains of Command", ("W.A. McCay", "E.L. Flood"), "0743421019", "9780743421010", 288,
     "Chains-of-Command/W-A-McCay", "com", None, "2000-09-22"),
    (70, "IMBALANCE", "Imbalance", ("V.E. Mitchell",), "0743421027", "9780743421027", 288,
     "Imbalance/V-E-Mitchell", "com", None, "2000-09-22"),
)


def validate(packet: object, opf_input: object) -> tuple[int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unreviewed packet field or injected authority")
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in TOP.items()):
        fail("A provenance, scope or held-effect guard changed")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Accepted owner OPF metadata source SHA changed")
    if not isinstance(opf_input, dict) or opf_input.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       opf_input.get("ebook_full_text_read") is not False or \
       opf_input.get("edition_binding_verified") is not False or \
       opf_input.get("work_admission_effect") != "NONE" or \
       not isinstance(opf_input.get("rows"), list) or len(opf_input["rows"]) != 347:
        fail("Expected accepted metadata-only owner OPF source")
    by_id = {r.get("source_local_id"): r for r in opf_input["rows"] if isinstance(r, dict)}
    if len(by_id) != 347:
        fail("Duplicate owner OPF IDs or missing metadata rows")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != len(EXPECTED):
        fail("Wrong nine-row sequence")
    isbn_count = 0
    for row, (num, local_title, title, creators, isbn10, isbn13, pages, slug, tld, anomaly, date) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != ROW_FIELDS:
            fail("Unreviewed row fields or injected private data")
        local_id = f"opf-local:{num:04d}"
        source = by_id.get(local_id)
        if not isinstance(source, dict) or source.get("parse_status") != "PARSED" or \
           source.get("title") != [local_title]:
            fail(f"Owner-local title/parse guard drifted {local_id}")
        if row["opf_local_id"] != local_id or row["opf_entry_sha256"] != source.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_claimed_isbn10"] != isbn10:
            fail(f"Owner-local locator or ISBN changed {local_id}")
        if isbn10 is None:
            if source.get("isbn_checksum_valid") != [] or source.get("creator") != [] or \
               row["opf_edition_crosswalk_state"] != "UNVERIFIED_LOCAL_TITLE_ONLY":
                fail("Missing owner OPF ISBN/creator was silently invented")
        else:
            if source.get("isbn_checksum_valid") != [isbn10] or not valid_isbn10(isbn10) or \
               to_isbn13(isbn10) != isbn13 or \
               row["opf_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
                fail(f"Owner OPF checksum/crosswalk unsupported {local_id}")
            isbn_count += 1
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(n) for n in row["creator_credits"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(isbn13) or \
           row["edition_format"] != "EBOOK" or row["source_anomaly"] != anomaly or \
           row["private_source_edition_verified"] is not False:
            fail(f"Publisher bibliographic identity or hold changed {local_id}")
        if row["publisher_date_us"] != date or not date_ok(date) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Publisher edition date/extent drifted {local_id}")
        host = f"www.simonandschuster.{tld}"
        url = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.netloc != host or parsed.scheme != "https" or parsed.query or parsed.fragment or \
           row["publisher_host"] != host or row["publisher_page"] != url:
            fail(f"Publisher URL host, path, ISBN or anomaly attribution changed {local_id}")
        if not text_ok(row["held_synopsis"], 300):
            fail(f"Held synopsis is unsafe or missing {local_id}")
    if isbn_count != 8:
        fail("Exactly one owner-local title-only, eight ISBN matches expected")
    return (9, isbn_count, 9 - isbn_count)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    n, isbn, title = validate(data, opf)
    print(f"PASS: {n} HELD editions, {isbn} checksum-aligned owner ISBN metadata leads, {title} title-only unverified; zero accepted Work/coverage")


if __name__ == "__main__":
    main()
