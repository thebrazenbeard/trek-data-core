#!/usr/bin/env python3
"""Fail-closed local-only validator for HELD OPF/publisher leads 0080–0086."""

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
    BASE, FAMILY, OPF_SHA, ORIGINAL_OPF, date_ok, fail, text_ok, to_isbn13,
    valid_isbn10, valid_isbn13,
)

DATA = Path(__file__).with_name("records.json")
ROW_FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_local_title", "opf_claimed_isbn10",
    "opf_edition_crosswalk_state", "publisher_title", "creator_credits", "publisher_host",
    "publisher_page", "isbn13", "edition_format", "publisher_date_us", "publisher_extent_pages",
    "source_anomaly", "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-80-86-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0080-0086-20261104",
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

EXPECTED = (
    (80, "REQUIEM", "Requiem", ("Michael Jan Friedman", "Kevin Ryan"), "0743421159",
     "9780743421157", 288, "Requiem/Michael-Jan-Friedman",
     "OPF_MICHEAL_VS_PUBLISHER_MICHAEL_CREATOR_UNRESOLVED"),
    (81, "Star Trek - TNG 033 - Balance Of Power", "Balance of Power", ("Dafydd ab Hugh",), None,
     "9780743421225", 304, "Balance-of-Power/Dafydd-ab-Hugh",
     "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED"),
    (82, "BLAZE OF GLORY", "Blaze of Glory", ("Simon Hawke",), "074342123X",
     "9780743421232", 288, "Blaze-of-Glory/Simon-Hawke", None),
    (83, "Star Trek - The Romulan Stratagem", "The Romulan Stratagem", ("Robert Greenberger",), None,
     "9780743421300", 288, "The-Romulan-Stratagem/Robert-Greenberger",
     "LOCAL_OPF_HAS_NO_ISBN_UNRESOLVED"),
    (84, "INTO THE NEBULA", "Into the Nebula", ("Gene DeWeese",), "074342137X",
     "9780743421379", 160, "Into-the-Nebula/Gene-DeWeese", None),
    (85, "THE LAST STAND", "The Last Stand", ("Brad Ferguson",), "0743421396",
     "9780743421393", 288, "The-Last-Stand/Brad-Ferguson", None),
    (86, "DRAGONS'S HONOR", "Dragon's Honor", ("Kij Johnson", "Greg Cox"), "0743421418",
     "9780743421416", 320, "Dragons-Honor/Kij-Johnson",
     "OPF_DRAGONS_S_VS_PUBLISHER_DRAGONS_TITLE_UNRESOLVED"),
)


def validate(packet: object, original: object) -> tuple[int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unreviewed packet schema or injected authority fields")
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in TOP.items()):
        fail("Held baseline, rights, lineage or effects were promoted")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Underlying accepted owner OPF metadata fingerprint changed")
    if not isinstance(original, dict) or original.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       original.get("ebook_full_text_read") is not False or original.get("edition_binding_verified") is not False or \
       original.get("work_admission_effect") != "NONE" or \
       not isinstance(original.get("rows"), list) or len(original["rows"]) != 347:
        fail("Original owner OPF metadata no longer supports this metadata-only packet")
    by_id = {r.get("source_local_id"): r for r in original["rows"] if isinstance(r, dict)}
    if len(by_id) != 347:
        fail("Original OPF source-local IDs missing or duplicate")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 7:
        fail("Expected seven bounded OPF source-local edition leads")
    isbn_matches = 0
    for row, (num, local_title, title, creators, isbn10, isbn13, pages, slug, anomaly) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != ROW_FIELDS:
            fail("Unreviewed row properties or private content fields")
        opf_id = f"opf-local:{num:04d}"
        source = by_id.get(opf_id)
        if not isinstance(source, dict) or source.get("parse_status") != "PARSED" or \
           source.get("title") != [local_title]:
            fail(f"Private OPF source-local title/parse differs {opf_id}")
        if row["opf_local_id"] != opf_id or row["opf_entry_sha256"] != source.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_claimed_isbn10"] != isbn10:
            fail(f"Private OPF fingerprint/identifier differs {opf_id}")
        if isbn10 is None:
            expected_creator_n = 0 if num == 81 else 1
            if source.get("isbn_checksum_valid") != [] or len(source.get("creator", [])) != expected_creator_n or \
               row["opf_edition_crosswalk_state"] != (
                   "UNVERIFIED_LOCAL_TITLE_ONLY" if num == 81 else "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY"):
                fail(f"Missing OPF ISBN/creator was silently filled {opf_id}")
        else:
            if source.get("isbn_checksum_valid") != [isbn10] or not valid_isbn10(isbn10) or \
               to_isbn13(isbn10) != isbn13 or \
               row["opf_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
                fail(f"Owner ISBN checksum/edition metadata crosswalk failed {opf_id}")
            isbn_matches += 1
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(name) for name in row["creator_credits"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(isbn13) or \
           row["edition_format"] != "EBOOK" or row["source_anomaly"] != anomaly or \
           row["private_source_edition_verified"] is not False:
            fail(f"Official edition metadata or anomaly attribution differs {opf_id}")
        if row["publisher_date_us"] != "2000-09-22" or not date_ok(row["publisher_date_us"]) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Official publication date/extent differs {opf_id}")
        host = "www.simonandschuster.com"
        url = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != host or parsed.query or parsed.fragment or \
           row["publisher_host"] != host or row["publisher_page"] != url:
            fail(f"Official publisher edition URI spoof/swap {opf_id}")
        if not text_ok(row["held_synopsis"], 300):
            fail(f"Publisher-paraphrased synopsis unsafe or absent {opf_id}")
    if isbn_matches != 5:
        fail("Exactly five OPF ISBN matches and two identity-unresolved rows expected")
    return (7, isbn_matches, 7 - isbn_matches)


def main() -> None:
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    n, matched, held = validate(packet, source)
    print(f"PASS: {n} held edition metadata leads, {matched} owner OPF ISBN matches, {held} unresolved title-only holds; no Work/coverage effect")


if __name__ == "__main__":
    main()
