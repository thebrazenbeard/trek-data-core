#!/usr/bin/env python3
"""Fail-closed validation for HELD owner-OPF/publisher items 0071–0079."""

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
ROW_FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_local_title", "opf_claimed_isbn10",
    "opf_edition_crosswalk_state", "publisher_title", "creator_credits", "publisher_host",
    "publisher_page", "isbn13", "edition_format", "publisher_date_us", "publisher_extent_pages",
    "source_anomaly", "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-71-79-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0071-0079-20261104",
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

# Separate literal publisher claims; hard-pinned to precise edition URLs,
# not to a global Work identity and not to a private ebook manifestation.
EXPECTED = (
    (71, "Star Trek - TNG - War Drums", "War Drums", ("John Vornholt",), None,
     "9780743421034", 272, "War-Drums/John-Vornholt", "com", "LOCAL_OPF_HAS_NO_ISBN_UNRESOLVED"),
    (72, "Star Trek - TNG - 24 - Nightshade", "Nightshade", ("Laurell K. Hamilton",), None,
     "9780743421072", 288, "Nightshade/Laurell-K-Hamilton", "com", "LOCAL_OPF_HAS_NO_ISBN_UNRESOLVED"),
    (73, "GROUNDED", "Grounded", ("David Bischoff",), "0743421086",
     "9780743421089", 288, "Grounded/David-Bischoff", "com", None),
    (74, "THE ROMULAN PRIZE", "The Romulan Prize", ("Simon Hawke",), "0743421094",
     "9780743421096", 288, "The-Romulan-Prize/Simon-Hawke", "com", None),
    (75, "GUISES OF THE MIND", "Guises of the Mind", ("Rebecca Neason",), "0743421108",
     "9780743421102", 288, "Guises-of-the-Mind/Rebecca-Neason", "com", None),
    (76, "HERE THERE BE DRAGONS", "Here There Be Dragons", ("John Peel",), "0743421116",
     "9780743421119", 288, "Here-There-Be-Dragons/John-Peel", "com", None),
    (77, "SINS OF COMMISSION", "Star Trek: The Next Generation: Sins of Commission", ("Susan Wright",), "0743421124",
     "9780743421126", 288, "Star-Trek-The-Next-Generation-Sins-of-Commission/Susan-Wright", "com",
     "PUBLISHER_EXPANDED_SERIES_DISPLAY_TITLE"),
    (78, "DEBTOR'S PLANET", "Star Trek: The Next Generation: Debtor's Planet", ("W.R. Thompson",), "0743421132",
     "9780743421133", 272, "Star-Trek-The-Next-Generation-Debtors-Planet/W-R-Thompson", "net",
     "PUBLISHER_EXPANDED_SERIES_DISPLAY_TITLE"),
    (79, "FOREIGN FOES", "Foreign Foes", ("Dave Galanter", "Greg Brodeur"), "0743421140",
     "9780743421140", 320, "Foreign-Foes/Dave-Galanter", "com", None),
)


def validate(packet: object, opf_input: object) -> tuple[int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unreviewed packet fields or privilege injection")
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in TOP.items()):
        fail("Held baseline, rights, provenance or zero-effect scope changed")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Accepted-public owner OPF source fingerprint changed")
    if not isinstance(opf_input, dict) or opf_input.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       opf_input.get("ebook_full_text_read") is not False or \
       opf_input.get("edition_binding_verified") is not False or \
       opf_input.get("work_admission_effect") != "NONE" or \
       not isinstance(opf_input.get("rows"), list) or len(opf_input["rows"]) != 347:
        fail("OPF source is not the accepted source-local metadata-only receipt")
    source_rows = {r.get("source_local_id"): r for r in opf_input["rows"] if isinstance(r, dict)}
    if len(source_rows) != 347:
        fail("Duplicate or missing OPF local identifiers")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 9:
        fail("Not nine source-local publisher leads")
    aligned = 0
    for row, (num, local_title, title, creators, local_isbn10, isbn13, pages, slug, tld, anomaly) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != ROW_FIELDS:
            fail("Unreviewed metadata field or private information injected")
        opf_id = f"opf-local:{num:04d}"
        opf_row = source_rows.get(opf_id)
        if not isinstance(opf_row, dict) or opf_row.get("parse_status") != "PARSED" or \
           opf_row.get("title") != [local_title]:
            fail(f"Owner source-local parse/title drifted: {opf_id}")
        if row["opf_local_id"] != opf_id or row["opf_entry_sha256"] != opf_row.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_claimed_isbn10"] != local_isbn10:
            fail(f"Owner source-local locator/ISBN drifted: {opf_id}")
        if local_isbn10 is None:
            if opf_row.get("isbn_checksum_valid") != [] or len(opf_row.get("creator", [])) != 1 or \
               row["opf_edition_crosswalk_state"] != "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY":
                fail(f"Owner-local edition ISBN was silently invented: {opf_id}")
        else:
            if opf_row.get("isbn_checksum_valid") != [local_isbn10] or not valid_isbn10(local_isbn10) or \
               row["opf_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY" or \
               to_isbn13(local_isbn10) != isbn13:
                fail(f"Owner ISBN10 checksum/crosswalk unsupported: {opf_id}")
            aligned += 1
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(name) for name in row["creator_credits"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(isbn13) or \
           row["edition_format"] != "EBOOK" or \
           row["source_anomaly"] != anomaly or \
           row["private_source_edition_verified"] is not False:
            fail(f"Publisher metadata or scoped anomaly changed: {opf_id}")
        if row["publisher_date_us"] != "2000-09-22" or not date_ok(row["publisher_date_us"]) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Publisher date/extent differed: {opf_id}")
        host = f"www.simonandschuster.{tld}"
        official = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != host or parsed.query or parsed.fragment or \
           row["publisher_host"] != host or row["publisher_page"] != official:
            fail(f"Unreviewed publisher host, path or ISBN: {opf_id}")
        if not text_ok(row["held_synopsis"], 300):
            fail(f"Held publisher-derived synopsis unsafe or missing: {opf_id}")
    if aligned != 7:
        fail("Exactly seven local ISBN alignments and two title/author-only holds expected")
    return (9, aligned, 9 - aligned)


def main() -> None:
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    opf = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    n, aligned, held = validate(packet, opf)
    print(f"PASS: {n} publisher metadata leads, {aligned} ISBN checksum alignments, {held} title/creator-only holds; zero accepted Work/coverage")


if __name__ == "__main__":
    main()
