"""Pinned, fail-closed guard for 2009 original studio home-edition leads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PINNED_SHA256 = "6be638bcde58132e2702ce11d7d3d473cdb9b6fd24b789735d721db1a0e03724"
WEB = "https://www.paramount.com/movies/star-trek-2009"
HOME = "https://ir.paramount.com/static-files/21c8db87-fe44-48f0-be67-9fa3d6be0bc6"
ITUNES = "https://ir.paramount.com/static-files/65c97927-b964-415f-801a-329ab6d2883e"
LINEAGE = ("Paramount film page, Paramount Home Entertainment and Paramount Digital Entertainment "
           "are related divisions, not independent witnesses to runtime, product identity or image rights.")
SYNOPSIS = ("Kirk and Spock enter a difficult partnership aboard a young Enterprise crew "
            "as a vengeful threat puts the Federation at risk.")


def card(local_id: str, source: str, section: str, kind: str, described: str, art: str) -> dict:
    return {
        "local_id": local_id,
        "source_key": source,
        "source_section": section,
        "historical_release_date": "2009-11-17",
        "edition_type": kind,
        "publisher_media_description": described,
        "artwork_lead": art,
        "display_eligible": False,
    }


NO_ART = "NOT_SPECIFIED_FOR_THIS_EDITION"
EXPECTED_CARDS = {
    "phe-2009-bluray-three-disc": card(
        "phe-2009-bluray-three-disc", "home_release_2009_pdf",
        "Three-disc Blu-ray and Blu-ray feature sections", "THREE_DISC_BLURAY_WITH_DIGITAL_COPY",
        "1080p high definition Blu-ray, English 5.1 Dolby TrueHD, additional supplements, third-disc digital copy", NO_ART),
    "phe-2009-dvd-two-disc": card(
        "phe-2009-dvd-two-disc", "home_release_2009_pdf",
        "Two-disc DVD section", "TWO_DISC_DVD_WITH_DIGITAL_COPY",
        "16:9 enhanced-widescreen DVD, commentary and deleted scenes, second-disc digital copy", NO_ART),
    "phe-2009-dvd-single-disc": card(
        "phe-2009-dvd-single-disc", "home_release_2009_pdf",
        "Single-disc DVD paragraph", "SINGLE_DISC_DVD",
        "16:9 enhanced-widescreen DVD with commentary, A New Vision featurette and gag reel", NO_ART),
    "pde-2009-itunes-extras": card(
        "pde-2009-itunes-extras", "digital_extras_2009_pdf",
        "iTunes Extras release and content list", "ITUNES_HD_WITH_EXTRAS",
        "HD iTunes Extras package with featurettes, international trailers and more than forty described images",
        "POSTER_KEY_ART_MENTIONED_NO_IMAGE_FILE_CUSTODY_OR_REUSE_LICENSE"),
}


def check(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def exact(value: object, expected: object, what: str) -> None:
    check(type(value) is type(expected) and value == expected, f"{what}: unreviewed change")


def no_dupes(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for name, value in pairs:
        check(name not in result, "duplicate JSON key")
        result[name] = value
    return result


def read_pinned() -> dict:
    check(RECORDS.is_file() and not RECORDS.is_symlink(), "record path rejected")
    check(RECORDS.stat().st_size <= 12_000, "unbounded record")
    data = RECORDS.read_bytes()
    exact(hashlib.sha256(data).hexdigest(), PINNED_SHA256, "record bytes")
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_dupes)


def validate(record: dict, registry: dict) -> int:
    fixed = {
        "packet_id": "FILMS-STAR-TREK-2009-FORMATS-20261103",
        "role": "FILMS",
        "proposal_only": True,
        "baseline_accepted_main": "1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b",
        "observed_on_utc": "2026-11-03",
        "candidate_film_id": "film-2009",
        "source_group": "publisher:paramount-corporate-family",
        "independence_note": LINEAGE,
        "source_body_sha256": None,
        "media_bytes_fetched": False,
        "artwork_bytes_fetched": False,
        "film_viewed": False,
        "accepted_source_work_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "artwork_release_effect": "NONE",
        "sources": {
            "paramount_film_page": WEB,
            "home_release_2009_pdf": HOME,
            "digital_extras_2009_pdf": ITUNES,
        },
        "source_observations": {
            "film_page_year_as_listed": 2009,
            "film_page_rating_as_listed": "PG-13",
            "film_page_runtime_as_listed_minutes": 127,
            "home_sheet_runtime_as_listed_minutes": 127,
            "runtime_scope": "TWO_SAME_CORPORATE_FAMILY_LISTINGS_NO_VERSION_SPECIFIC_COPY_CHECK",
            "home_release_announcement_date": "2009-07-17",
            "digital_extras_announcement_date": "2009-11-17",
            "source_relative_synopsis_candidate": SYNOPSIS,
            "synopsis_status": "PUBLISHER_DESCRIPTION_PARAPHRASE_NOT_REVIEWED_OR_RELEASED",
        },
    }
    check(type(record) is dict and set(record) == set(fixed) | {"cards"}, "unexpected record key")
    for key, value in fixed.items():
        exact(record[key], value, key)
    check(type(registry) is dict and registry.get("proposal_type") == "FILM_DISCOVERY_METADATA",
          "not accepted film discovery")
    check(any(type(f) is dict and f.get("id") == "film-2009"
              and f.get("source_locator") == "https://www.startrek.com/movies/star-trek-2009"
              and f.get("title") == "Star Trek (2009)"
              for f in registry.get("films", [])), "unknown film candidate")
    cards = record["cards"]
    check(type(cards) is list and len(cards) == 4, "unreviewed card count")
    seen: set[str] = set()
    for i, row in enumerate(cards):
        check(type(row) is dict, "wrong card type")
        ident = row.get("local_id")
        check(type(ident) is str and ident in EXPECTED_CARDS and ident not in seen,
              f"card {i}: unexpected or duplicate ID")
        exact(row, EXPECTED_CARDS[ident], f"card {i}")
        seen.add(ident)
    check(seen == set(EXPECTED_CARDS), "missing reviewed card")
    return len(cards)


def main() -> None:
    registry = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    print(f"PASS: {validate(read_pinned(), registry)} Paramount 2009 edition cards; no public media/coverage")


if __name__ == "__main__":
    main()
