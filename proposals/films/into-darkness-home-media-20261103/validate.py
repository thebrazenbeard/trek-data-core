"""Fail-closed exact-edition Paramount home media research guard."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PINNED_SHA256 = "d3053c593ec5aa7a09264bff3e75831bcae19d958567eb3ad12ac02e12108065"
WEB = "https://www.paramount.com/movies/star-trek-into-darkness"
PDF = "https://ir.paramount.com/static-files/cf49d3ba-f408-4599-9180-d5141396e7e7"
LINEAGE = ("Both Paramount's current movie page and its 2013 Paramount Home Media Distribution press release "
           "are from one related corporate publisher family, not independent runtime verification.")
SUMMARY = ("Following an attack inside Federation territory, the Enterprise crew pursues the suspected instigator "
           "on a mission that threatens to test the crew's loyalties and judgment.")


def expected_card(local_id: str, section: str, kind: str, date: str, described: str, specificity: str) -> dict:
    return {
        "local_id": local_id,
        "source_key": "home_release_pdf",
        "source_section": section,
        "kind": kind,
        "announced_us_availability_date": date,
        "format_as_described": described,
        "source_specificity": specificity,
        "display_eligible": False,
    }


DATE_ONLY = "RELEASE_DATE_AND_FORMAT_ONLY_NOT_CURRENT_AVAILABILITY_OR_CUT_RUNTIME"
PACKAGE = "PACKAGE_CONTENTS_NOT_ARTWORK_OR_BITSTREAM_HASH"
EXPECTED_CARDS = {
    "paramount-id-2013-digital": expected_card(
        "paramount-id-2013-digital", "Digital debut and Street Date fact sheet",
        "DIGITAL_INITIAL_RELEASE", "2013-08-20", "Digital", DATE_ONLY),
    "paramount-id-2013-bluray-dvd": expected_card(
        "paramount-id-2013-bluray-dvd", "Blu-ray/DVD Combo Pack",
        "BLURAY_DVD_COMBO_PACK", "2013-09-10",
        "Blu-ray 1080p high definition plus 16:9 widescreen-enhanced DVD standard definition; advertised digital copy access", PACKAGE),
    "paramount-id-2013-bluray3d-bluray-dvd": expected_card(
        "paramount-id-2013-bluray3d-bluray-dvd", "Blu-ray 3D/Blu-ray/DVD Combo Pack",
        "BLURAY3D_BLURAY_DVD_COMBO_PACK", "2013-09-10",
        "Combo pack with 1080p 3D high-definition disc in addition to Blu-ray/DVD combo contents", PACKAGE),
    "paramount-id-2013-dvd": expected_card(
        "paramount-id-2013-dvd", "Single-Disc DVD", "SINGLE_DISC_DVD", "2013-09-10",
        "16:9 widescreen-enhanced standard-definition DVD", PACKAGE),
    "paramount-id-2013-on-demand": expected_card(
        "paramount-id-2013-on-demand", "Street Date fact sheet", "ON_DEMAND_RELEASE", "2013-09-10",
        "On Demand; platform and encode unspecified", DATE_ONLY),
}


def check(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def exact(value: object, expected: object, reason: str) -> None:
    check(type(value) is type(expected) and value == expected, f"{reason}: unreviewed claim")


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for k, v in pairs:
        check(k not in result, "duplicate JSON key")
        result[k] = v
    return result


def read_pinned() -> dict:
    check(RECORDS.is_file() and not RECORDS.is_symlink(), "invalid packet path")
    check(RECORDS.stat().st_size < 20_000, "oversized record")
    raw = RECORDS.read_bytes()
    exact(hashlib.sha256(raw).hexdigest(), PINNED_SHA256, "packet bytes")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys)


def validate(packet: dict, discovery: dict) -> int:
    expected = {
        "proposal_id": "FILMS-INTO-DARKNESS-HOME-MEDIA-20261103",
        "role": "FILMS",
        "proposal_only": True,
        "baseline_accepted_main": "1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b",
        "observed_on_utc": "2026-11-03",
        "candidate_film_id": "film-into-darkness",
        "source_group": "publisher:paramount-corporate-family",
        "source_independence": LINEAGE,
        "source_snapshots_sha256": None,
        "media_bytes_fetched": False,
        "accepted_coverage_effect": "NONE",
        "accepted_source_work_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "artwork_release_effect": "NONE",
        "source_locators": {"studio_movie_page": WEB, "home_release_pdf": PDF},
        "studio_listing_observation": {
            "source_key": "studio_movie_page", "section": "About the Film",
            "year_as_listed": 2013, "rating_as_listed": "PG-13",
            "runtime_as_listed_minutes": 132,
            "runtime_edition": "UNSPECIFIED_ON_STUDIO_WEB_PAGE",
            "synopsis_kind": "SOURCE_PUBLISHER_DESCRIPTION_NOT_FILM_VIEWED",
        },
        "home_release_observation": {
            "source_key": "home_release_pdf", "announcement_date": "2013-07-10",
            "publisher": "Paramount Home Media Distribution",
            "runtime_as_announced_minutes": 131,
            "runtime_edition": "UNSPECIFIED_ON_RELEASE_FACT_SHEET",
            "synopsis_kind": "SOURCE_PUBLISHER_DESCRIPTION_NOT_FILM_VIEWED",
            "original_synopsis_candidate": SUMMARY,
            "synopsis_release_status": "NOT_EDITORIALLY_REVIEWED_OR_RELEASED",
        },
        "runtime_disposition": "UNRESOLVED_132_STUDIO_WEB_VS_131_HOME_MEDIA_FACT_SHEET_NO_EXACT_EDITION_COMPARISON",
    }
    check(type(packet) is dict and set(packet) == set(expected) | {"cards"}, "unexpected packet fields")
    for k, v in expected.items():
        exact(packet[k], v, k)
    check(type(discovery) is dict and discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA",
          "missing accepted film discovery")
    check(any(row.get("id") == "film-into-darkness" and row.get("title") == "Star Trek Into Darkness"
              and row.get("source_locator") == "https://www.startrek.com/movies/star-trek-into-darkness"
              for row in discovery.get("films", [])), "unrecognized film candidate")
    cards = packet["cards"]
    check(type(cards) is list and len(cards) == len(EXPECTED_CARDS), "wrong card count")
    seen: set[str] = set()
    for i, card in enumerate(cards):
        check(type(card) is dict, f"card {i}: wrong type")
        key = card.get("local_id")
        check(type(key) is str and key in EXPECTED_CARDS and key not in seen,
              f"card {i}: unexpected/duplicate ID")
        exact(card, EXPECTED_CARDS[key], f"card {i}")
        seen.add(key)
    check(seen == set(EXPECTED_CARDS), "missing source-local format card")
    return len(cards)


def main() -> None:
    catalog = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    print(f"PASS: {validate(read_pinned(), catalog)} release-format source-local cards, no admission or image release")


if __name__ == "__main__":
    main()
