"""Source-bound, proposal-only guard for TMP poster-art attribution and editions."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
BOB = "https://vice-press.com/blogs/news/star-trek-the-motion-picture-by-bob-peak"
FERGUSON = "https://vice-press.com/blogs/news/star-trek-the-motion-picture-by-matt-ferguson"
DIRECTOR = "https://www.startrek.com/news/fully-restored-directors-edition-of-star-trek-the-motion-picture-arrives-on-4k-ultra-hd"
LINEAGE = ("Two Vice Press producer announcements are one marketing-source family, not independent image-rights confirmations. "
           "Both describe 2023 physical print editions; neither licenses digital display by this project.")

EXPECTED_FAMILIES = {
    "vice-press-tmp-bob-peak-2023": {
        "local_artwork_id": "vice-press-tmp-bob-peak-2023",
        "source_key": "bob_peak_2023",
        "artwork_kind": "BOB_PEAK_ORIGINAL_ARTWORK_REMASTERED_FOR_2023_PRINTS",
        "original_artist_credit": "Bob Peak",
        "source_provision_credit": "Thomas Peak",
        "remaster_credit": "Matt Ferguson",
        "rights_status": "NO_PUBLIC_DIGITAL_REUSE_PERMISSION_VERIFIED",
    },
    "vice-press-tmp-matt-ferguson-2023": {
        "local_artwork_id": "vice-press-tmp-matt-ferguson-2023",
        "source_key": "matt_ferguson_2023",
        "artwork_kind": "NEW_ARTWORK_COMMISSIONED_FOR_2023_PRINTS",
        "original_artist_credit": "Matt Ferguson",
        "source_provision_credit": None,
        "remaster_credit": None,
        "rights_status": "NO_PUBLIC_DIGITAL_REUSE_PERMISSION_VERIFIED",
    },
}


def expected_variant(local_id, family, source, evidence_id, description, kind, cap, assertion):
    return {
        "local_entity_id": local_id,
        "artwork_family_ref": family,
        "source_key": source,
        "evidence_id": evidence_id,
        "source_description": description,
        "edition_type": kind,
        "edition_limit": cap,
        "dimensions_inches": [24, 36],
        "source_assertion": assertion,
        "display_eligible": False,
    }


EXPECTED_VARIANTS = {
    "vp-tmp-bob-2023-timed": expected_variant(
        "vp-tmp-bob-2023-timed", "vice-press-tmp-bob-peak-2023", "bob_peak_2023",
        "vp-tmp-bob-timed-2023-announcement", "Timed Edition; 24x36 inches",
        "TIMED_REGULAR", None, "VICE_PRESS_LISTS_TIMED_PRINT"),
    "vp-tmp-bob-2023-foil": expected_variant(
        "vp-tmp-bob-2023-foil", "vice-press-tmp-bob-peak-2023", "bob_peak_2023",
        "vp-tmp-bob-foil-2023-announcement", "Foil Variant; edition of 200; 24x36 inches",
        "FOIL_VARIANT", 200, "VICE_PRESS_LISTS_LIMITED_FOIL_PRINT"),
    "vp-tmp-ferguson-2023-regular": expected_variant(
        "vp-tmp-ferguson-2023-regular", "vice-press-tmp-matt-ferguson-2023", "matt_ferguson_2023",
        "vp-tmp-ferguson-regular-2023-announcement", "Regular edition of 200; 24x36 inches",
        "NUMBERED_REGULAR", 200, "VICE_PRESS_LISTS_LIMITED_REGULAR_PRINT"),
    "vp-tmp-ferguson-2023-foil": expected_variant(
        "vp-tmp-ferguson-2023-foil", "vice-press-tmp-matt-ferguson-2023", "matt_ferguson_2023",
        "vp-tmp-ferguson-foil-2023-announcement", "Foil variant of 175; 24x36 inches",
        "FOIL_VARIANT", 175, "VICE_PRESS_LISTS_LIMITED_FOIL_PRINT"),
}


def check(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError(why)


def exact_keys(value, expected: set[str], context: str) -> None:
    check(type(value) is dict and set(value) == expected, f"{context}: unexpected/missing field")


def reviewed_records(value, expected: dict, identity_key: str, context: str) -> None:
    check(type(value) is list and len(value) == len(expected), f"{context}: incorrect count")
    seen: set[str] = set()
    for i, row in enumerate(value):
        exact_keys(row, set(next(iter(expected.values()))), f"{context} {i}")
        identity = row[identity_key]
        check(type(identity) is str and identity in expected, f"{context} {i}: unreviewed identity")
        check(identity not in seen, f"{context} {i}: duplicate identity")
        check(row == expected[identity], f"{context} {i}: reviewed evidence or edition mismatch")
        seen.add(identity)
    check(seen == set(expected), f"{context}: missing reviewed record")


def validate(packet: dict, discovery: dict) -> int:
    exact_keys(packet, {
        "proposal_id", "role", "proposal_only", "baseline_accepted_main", "observed_on_utc",
        "candidate_film_id", "source_group", "source_family_independence", "source_page_sha256",
        "media_bytes_fetched", "accepted_coverage_effect", "accepted_identity_effect",
        "public_artwork_release_effect", "version_exclusion", "sources", "artwork_families",
        "print_variants",
    }, "packet")
    expected = {
        "proposal_id": "FILMS-TMP-2023-POSTER-ART-LINES",
        "role": "FILMS", "proposal_only": True,
        "baseline_accepted_main": "8a89b16e96220188d200b6ff9300fb90fa137627",
        "observed_on_utc": "2026-11-03",
        "candidate_film_id": "film-motion-picture",
        "source_group": "producer:vice-press.com",
        "source_page_sha256": None,
        "media_bytes_fetched": False,
        "accepted_coverage_effect": "NONE",
        "accepted_identity_effect": "NONE",
        "public_artwork_release_effect": "NONE",
        "version_exclusion": "2023_PHYSICAL_PRINTS_NOT_2022_DIRECTORS_EDITION_4K_PACKAGING_OR_FILM_STILLS",
    }
    for field, fixed in expected.items():
        check(type(packet[field]) is type(fixed) and packet[field] == fixed, f"invalid {field}")
    lineage = packet["source_family_independence"]
    check(type(lineage) is str and len(lineage) <= 240, "unbounded source lineage")
    check(lineage == LINEAGE, "unreviewed independence claim")
    check(packet["sources"] == {
        "bob_peak_2023": BOB, "matt_ferguson_2023": FERGUSON,
        "director_edition_context_only": DIRECTOR,
    }, "unreviewed source locator")
    check(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "missing accepted film discovery")
    check(packet["candidate_film_id"] in {x["id"] for x in discovery["films"]}, "unrecognized film candidate")
    reviewed_records(packet["artwork_families"], EXPECTED_FAMILIES, "local_artwork_id", "families")
    reviewed_records(packet["print_variants"], EXPECTED_VARIANTS, "local_entity_id", "variants")
    return len(packet["print_variants"])


def main() -> None:
    packet = json.loads(RECORDS.read_text(encoding="utf-8"))
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    print(f"PASS: {validate(packet, discovery)} source-local print variants across 2 distinct art families; 0 public artwork")


if __name__ == "__main__":
    main()
