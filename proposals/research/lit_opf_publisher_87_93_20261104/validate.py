#!/usr/bin/env python3
"""Fail closed: seven owner-local OPF leads paired with publisher metadata, not admitted works."""

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
    "opf_isbn13_checksum_conversion", "opf_edition_crosswalk_state", "publisher_title",
    "creator_credits", "publisher_host", "publisher_page", "isbn13", "edition_format",
    "publisher_date_us", "publisher_extent_pages", "source_anomaly",
    "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-87-93-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0087-0093-20261104",
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

# Publisher-edition identities manually inspected at first-party URLs. The OPF
# ISBN10 of 0091 is valid but actually resolves to Balance of Power, NOT to the
# title in that OPF entry. This is a decisive negative reconciliation witness.
# Each row: owner ID, OPF title, OPF creator, ISBN10, publisher title/creators,
# publisher ISBN13, page extent, publisher slug, anomaly, synopsis SHA256.
EXPECTED = (
    (87, "ROGUE SAUCER", ("JOHN VORNHOLT",), "0743421167", "Rogue Saucer",
     ("John Vornholt",), "9780743421164", 288, "Rogue-Saucer/John-Vornholt", None,
     "eab637caa52b064bb3f9271f88a15d44b10069983f27430273493f44f6c9f68a"),
    (88, "POSSESSION", ("J. M. Dillard and Kathleen O'Malley",), "0743421175", "Possession",
     ("J.M. Dillard", "Kathleen O'malley"), "9780743421171", 288, "Possession/J-M-Dillard", None,
     "07d28a42fa32288185f70ae1b6b1619490c6395329d0fba5be9dcf46739ce3bc"),
    (89, "Star Trek - TNG - Infiltrator", (), None, "Infiltrator",
     ("W.R. Thompson",), "9780743421201", 288, "Infiltrator/W-R-Thompson",
     "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "453f6235fc58d40e0baf725bfc1e4e303c7a78b705eaf4e934c7587bad7e37a6"),
    (90, "A FURY SCORNED", ("PAMELA SARGENT AND GEORGE ZEBROWSKI",), "0743421213",
     "Star Trek: The Next Generation: A Fury Scorned", ("Pamela Sargent", "George Zebrowski"),
     "9780743421218", 288, "Star-Trek-The-Next-Generation-A-Fury-Scorned/Pamela-Sargent", None,
     "56c4cf3a9e5d4a7b82be27516d5e3c9b4b1d9fd8b570ecfadf6d5e99125d55bd"),
    (91, "THE DEATH OF PRINCES", ("JOHN PEEL",), "0743421221", "The Death of Princes",
     ("John Peel",), "9780743422888", 304, "The-Death-of-Princes/John-Peel",
     "OPF_DEATH_OF_PRINCES_ISBN_POINTS_TO_BALANCE_OF_POWER",
     "1364adaed144b62fd2c116cc051b41edb05eac5c6dcb4488edb7eda004f9c4fa"),
    (92, "INTELLIVORE", ("DIANE DUANE",), "0743421248", "Intellivore",
     ("Diane Duane",), "9780743421249", 272, "Intellivore/Diane-Duane", None,
     "333bd4be73ccc70e51c5acf2630450b28de415d47ff89111dd60f0520f77c895"),
    (93, "Star Trek - TNG 046 - To Storm Heaven", (), None, "To Storm Heaven",
     ("Esther Friesner",), "9780743421256", 240, "To-Storm-Heaven/Esther-Friesner",
     "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "dc6e316ca0b293aec69df3fa39569ab88b46ecef7bfcf8dee6a7a1da39e182c6"),
)


def validate(packet: object, original: object) -> tuple[int, int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unreviewed packet schema or injected authority fields")
    if any(type(packet[k]) is not type(v) or packet[k] != v for k, v in TOP.items()):
        fail("HELD baseline, rights, lineage, effects, or coverage were promoted")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Underlying owner OPF metadata file changed")
    if not isinstance(original, dict) or original.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       original.get("ebook_full_text_read") is not False or original.get("edition_binding_verified") is not False or \
       original.get("work_admission_effect") != "NONE" or \
       not isinstance(original.get("rows"), list) or len(original["rows"]) != 347:
        fail("Original OPF source no longer supports metadata-only intake")
    by_id = {r.get("source_local_id"): r for r in original["rows"] if isinstance(r, dict)}
    if len(by_id) != 347:
        fail("Owner OPF source-local IDs duplicate or disappear")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 7:
        fail("Expected seven bounded OPF local edition leads")
    aligned = title_only = conflict = 0
    for row, (num, local_title, local_creators, isbn10, title, creators, isbn13, pages, slug,
              anomaly, synopsis_sha) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != ROW_FIELDS:
            fail("Unreviewed row fields or confidential file content")
        opf_id = f"opf-local:{num:04d}"
        source = by_id.get(opf_id)
        if not isinstance(source, dict) or source.get("parse_status") != "PARSED" or \
           source.get("title") != [local_title] or source.get("creator") != list(local_creators):
            fail(f"Owner OPF local title/creator/parse differs {opf_id}")
        if row["opf_local_id"] != opf_id or row["opf_entry_sha256"] != source.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_claimed_isbn10"] != isbn10:
            fail(f"Owner OPF local ID/fingerprint/ISBN differs {opf_id}")
        if isbn10 is None:
            if source.get("isbn_checksum_valid") != [] or row["opf_isbn13_checksum_conversion"] is not None or \
               row["opf_edition_crosswalk_state"] != "UNVERIFIED_LOCAL_TITLE_ONLY":
                fail(f"Missing OPF metadata was silently filled {opf_id}")
            title_only += 1
        else:
            conversion = to_isbn13(isbn10)
            if source.get("isbn_checksum_valid") != [isbn10] or not valid_isbn10(isbn10) or \
               row["opf_isbn13_checksum_conversion"] != conversion:
                fail(f"Owner ISBN10 checksum/conversion differed {opf_id}")
            if num == 91:
                if conversion != "9780743421225" or conversion == isbn13 or \
                   row["opf_edition_crosswalk_state"] != "ISBN_TITLE_CONFLICT_UNRESOLVED":
                    fail("0081 Balance of Power vs 0091 Death of Princes owner ISBN conflict was hidden")
                conflict += 1
            elif conversion != isbn13 or row["opf_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
                fail(f"Owner/publisher ISBN alignment falsely promoted {opf_id}")
            else:
                aligned += 1
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(c) for c in row["creator_credits"]) or \
           row["isbn13"] != isbn13 or not valid_isbn13(isbn13) or \
           row["edition_format"] != "EBOOK" or row["source_anomaly"] != anomaly or \
           row["private_source_edition_verified"] is not False:
            fail(f"Official publisher edition or source anomaly changed {opf_id}")
        if row["publisher_date_us"] != "2000-09-22" or not date_ok(row["publisher_date_us"]) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Official publication date or page extent changed {opf_id}")
        host = "www.simonandschuster.com"
        exact_url = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != host or \
           parsed.query or parsed.fragment or row["publisher_host"] != host or \
           row["publisher_page"] != exact_url:
            fail(f"Official publisher page spoof/swap {opf_id}")
        summary = row["held_synopsis"]
        if not text_ok(summary, 300) or hashlib.sha256(summary.encode("utf-8")).hexdigest() != synopsis_sha:
            fail(f"Original bounded publisher-description paraphrase changed {opf_id}")
    # Assert the contradiction is not a second publisher edition or a new Work.
    earlier = json.loads((ROOT / "proposals/research/lit_opf_publisher_80_86_20261104/records.json")
                         .read_text(encoding="utf-8"))
    balance = next((row for row in earlier["rows"] if row["opf_local_id"] == "opf-local:0081"), None)
    if not isinstance(balance, dict) or balance["publisher_title"] != "Balance of Power" or \
       balance["isbn13"] != "9780743421225" or balance["private_source_edition_verified"] is not False:
        fail("Prior HELD Balance of Power collision witness is missing")
    if (aligned, title_only, conflict) != (4, 2, 1):
        fail("Expected four checksum alignments, two title-only holds and one contradiction")
    return (7, aligned, title_only, conflict)


def main() -> None:
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    n, aligned, title_only, conflict = validate(packet, source)
    print(f"PASS: {n} HELD edition leads, {aligned} ISBN checksums aligned, "
          f"{title_only} title-only holds, {conflict} explicit ISBN/title conflict; "
          "no Work, Source, or coverage effect")


if __name__ == "__main__":
    main()
