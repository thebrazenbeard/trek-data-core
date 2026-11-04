#!/usr/bin/env python3
"""Fail-closed, explicitly HELD owner OPF/official publisher packet 0094–0100."""

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
    BASE, FAMILY, OPF_SHA, ORIGINAL_OPF, date_ok, fail, text_ok, valid_isbn13,
)

DATA = Path(__file__).with_name("records.json")
FIELDS = frozenset((
    "opf_local_id", "opf_entry_sha256", "opf_local_title", "opf_local_creator",
    "opf_claimed_isbn10", "opf_isbn13_checksum_conversion", "opf_edition_crosswalk_state",
    "publisher_title", "creator_credits", "publisher_host", "publisher_page", "isbn13",
    "edition_format", "publisher_date_us", "publisher_extent_pages", "source_anomaly",
    "private_source_edition_verified", "held_synopsis",
))
TOP = {
    "schema_version": "trek-lit-opf-publisher-94-100-held-v1",
    "proposal_id": "LIT-OPF-PUBLISHER-0094-0100-20261104",
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

# OPF local IDs/titles/creator strings are literal owner metadata. Published
# edition metadata below was read from distinct exact S&S product pages, but
# those pages belong to ONE publisher family (not independent corroboration).
# Tuple: local, title, creator, publisher title, credits, ISBN13, date, pages,
# URL slug, crosswalk state, anomaly, original paraphrase SHA256.
EXPECTED = (
    (94, "Star Trek - TNG 047 - Q-Space", (), "The Q Continuum: Book One: Q-Space",
     ("Greg Cox",), "9780671041014", "1999-07-14", 288,
     "The-Q-Continuum-Book-One-Q-Space/Greg-Cox", "UNVERIFIED_LOCAL_TITLE_ONLY",
     "LOCAL_TNG_047_NUMBER_NOT_ATTESTED_ON_PUBLISHER_PRODUCT_PAGE",
     "3cbc04ff350f3c9cd44f8cf7c46d77f10c9a3197d479c368df86f7f8ccdeae0b"),
    (95, "Star Trek - TNG 046 - Q-Zone", (), "The Q Continuum: Book Two: Q-Zone",
     ("Greg Cox",), "9780671041021", "1999-07-14", 288,
     "The-Q-Continuum-Book-Two-Q-Zone/Greg-Cox", "UNVERIFIED_LOCAL_TITLE_ONLY",
     "LOCAL_TNG_046_COLLIDES_WITH_0093_TO_STORM_HEAVEN_UNRESOLVED",
     "4d6efdd80ac3f230fa9b3f381e9476f025bca02a06987b3a46693217bd052b0a"),
    (96, "Star Trek - TNG - The Q Continuum 3 - Q-Strike", ("William C. Deets &Dean Williams",),
     "The Q Continuum: Book Three: Q-Strike", ("Greg Cox",), "9780671041038",
     "1999-07-14", 288, "The-Q-Continuum-Book-Three-Q-Strike/Greg-Cox",
     "TITLE_ONLY_CREATOR_CONFLICT_UNRESOLVED",
     "LOCAL_OPF_CREATOR_CONFLICTS_WITH_PUBLISHER_GREG_COX_UNRESOLVED",
     "aec2b49965d2be94cbc138880399c457d96bf7aad205cf20f6feb075945b7f55"),
    (97, "Star Trek - TNG 050 - Dyson Sphere", (), "Dyson Sphere",
     ("Charles Pellegrino", "George Zebrowski"), "9780743421294", "1999-04-01", 256,
     "Dyson-Sphere/Charles-Pellegrino", "UNVERIFIED_LOCAL_TITLE_ONLY",
     "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "2ffef460f2fd138d347f84be8379158430c6a7f40e59580a5185d629f63edbf1"),
    (98, "Vectors", ("Dean W. Smith & Kristine K. Rusch",), "Vectors",
     ("Dean Wesley Smith", "Kristine Kathryn Rusch"), "9780743421324", "2000-09-22", 304,
     "Vectors/Dean-Wesley-Smith", "UNVERIFIED_LOCAL_TITLE_CREATOR_ABBREVIATED",
     "OWNER_CREATOR_ABBREVIATIONS_DIFFER_FROM_PUBLISHER_UNRESOLVED",
     "7cea0fadb644c94440f6ff166fbb66659348f6771769d97a9231975f83c1e4ca"),
    (99, "Star Trek - TNG 053 - Double Helix Red Sector", (), "Red Sector",
     ("Diane Carey",), "9780743421331", "2000-09-22", 336,
     "Red-Sector/Diane-Carey", "UNVERIFIED_LOCAL_TITLE_ONLY",
     "LOCAL_OPF_HAS_NO_CREATOR_OR_ISBN_UNRESOLVED",
     "bc867ac72b02d480b072facec191b6c8b276f317ddf80a720dd9495e2ad0d248"),
    (100, "Star Trek - Double Helix - Quarantine", ("John Vornholt",), "Quarantine",
     ("John Vornholt",), "9780743421348", "2000-09-22", 288,
     "Quarantine/John-Vornholt", "UNVERIFIED_LOCAL_TITLE_CREATOR_ONLY",
     "LOCAL_OPF_HAS_NO_ISBN_UNRESOLVED",
     "b5dc242fda971cb3f0470d9772651243568defe85b1129ec02bbb2f2aa28d4c6"),
)


def validate(packet: object, original: object) -> tuple[int, int, int, int]:
    if not isinstance(packet, dict) or frozenset(packet) != frozenset(TOP) | {"rows"}:
        fail("Unexpected schema or promoted fields in HELD packet")
    if any(type(packet[key]) is not type(v) or packet[key] != v for key, v in TOP.items()):
        fail("Baseline, source, rights, coverage, or admission status was promoted")
    if hashlib.sha256(ORIGINAL_OPF.read_bytes()).hexdigest() != OPF_SHA:
        fail("Owner OPF metadata source SHA differs")
    if not isinstance(original, dict) or original.get("source_kind") != "OWNER_PRIVATE_OPF_XML_METADATA" or \
       original.get("ebook_full_text_read") is not False or original.get("edition_binding_verified") is not False or \
       original.get("work_admission_effect") != "NONE" or \
       not isinstance(original.get("rows"), list) or len(original["rows"]) != 347:
        fail("Owner OPF metadata provenance or held status differs")
    by_id = {r.get("source_local_id"): r for r in original["rows"] if isinstance(r, dict)}
    if len(by_id) != 347:
        fail("Owner OPF local IDs missing or duplicated")
    rows = packet["rows"]
    if not isinstance(rows, list) or len(rows) != 7:
        fail("Expected seven bounded owner OPF entries")
    conflicts = ordinal_conflicts = 0
    for row, (num, local_title, local_creators, title, creators, isbn13, date, pages,
              slug, state, anomaly, synopsis_sha) in zip(rows, EXPECTED):
        if not isinstance(row, dict) or frozenset(row) != FIELDS:
            fail("Unreviewed row fields or private content")
        local_id = f"opf-local:{num:04d}"
        source = by_id.get(local_id)
        if not isinstance(source, dict) or source.get("parse_status") != "PARSED" or \
           source.get("title") != [local_title] or source.get("creator") != list(local_creators) or \
           source.get("isbn_checksum_valid") != []:
            fail(f"Source-local owner metadata differs {local_id}")
        if row["opf_local_id"] != local_id or row["opf_entry_sha256"] != source.get("opf_entry_sha256") or \
           row["opf_local_title"] != local_title or row["opf_local_creator"] != list(local_creators) or \
           row["opf_claimed_isbn10"] is not None or row["opf_isbn13_checksum_conversion"] is not None or \
           row["opf_edition_crosswalk_state"] != state:
            fail(f"Nonexistent owner edition ISBN/identity was manufactured {local_id}")
        if row["publisher_title"] != title or row["creator_credits"] != list(creators) or \
           not all(text_ok(v) for v in row["creator_credits"]) or row["isbn13"] != isbn13 or \
           not valid_isbn13(isbn13) or row["edition_format"] != "EBOOK" or \
           row["source_anomaly"] != anomaly or row["private_source_edition_verified"] is not False:
            fail(f"Publisher edition attribution/creator anomaly changed {local_id}")
        if row["publisher_date_us"] != date or not date_ok(row["publisher_date_us"]) or \
           type(row["publisher_extent_pages"]) is not int or row["publisher_extent_pages"] != pages:
            fail(f"Official date or extent changed {local_id}")
        host = "www.simonandschuster.com"
        expected_url = f"https://{host}/books/{slug}/Star-Trek-The-Next-Generation/{isbn13}"
        parsed = urlsplit(row["publisher_page"]) if isinstance(row["publisher_page"], str) else None
        if parsed is None or parsed.scheme != "https" or parsed.netloc != host or \
           parsed.query or parsed.fragment or row["publisher_host"] != host or \
           row["publisher_page"] != expected_url:
            fail(f"First-party metadata URL spoof/swap {local_id}")
        synopsis = row["held_synopsis"]
        if not text_ok(synopsis, 300) or hashlib.sha256(synopsis.encode("utf-8")).hexdigest() != synopsis_sha:
            fail(f"Original bounded publisher-description paraphrase changed {local_id}")
        conflicts += num == 96
        ordinal_conflicts += num == 95
    # Check the second local '046' ordinal remains visible as counterevidence.
    previous = json.loads((ROOT / "proposals/research/lit_opf_publisher_87_93_20261104/records.json")
                          .read_text(encoding="utf-8"))
    prior = next((r for r in previous["rows"] if r["opf_local_id"] == "opf-local:0093"), None)
    if not isinstance(prior, dict) or prior["opf_local_title"] != "Star Trek - TNG 046 - To Storm Heaven" or \
       prior["private_source_edition_verified"] is not False:
        fail("Duplicate 046 source-local ordinal witness no longer available")
    if (conflicts, ordinal_conflicts) != (1, 1):
        fail("Expected exact material author and ordinal discrepancies")
    return (7, 0, conflicts, ordinal_conflicts)


def main() -> None:
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    source = json.loads(ORIGINAL_OPF.read_text(encoding="utf-8"))
    rows, isbn_matches, creator_conflicts, ordinal_conflicts = validate(packet, source)
    print(f"PASS: {rows} HELD source-local leads, {isbn_matches} owner ISBN matches, "
          f"{creator_conflicts} creator conflict, {ordinal_conflicts} local ordinal collision; "
          "no Source, Work or coverage changes")


if __name__ == "__main__":
    main()
