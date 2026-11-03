"""Fail-closed, exact-source guard for a distributor film-metadata proposal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET_PATH = HERE / "records.json"
DISCOVERY_PATH = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PRIOR_PATH = ROOT / "proposals/research/films/publisher-synopses-20261103/observations.json"
PINNED_BYTES_SHA256 = "cde05393657f16d7c846c77c6c87227948bd38a2d2a06a2946bcd727e44cf122"
PARAMOUNT = "https://www.paramount.com/movies/star-trek-beyond"
LINEAGE = "Paramount corporate publisher family: related to StarTrek.com and Pluto TV; NOT independent cross-publisher verification"
SYNOPSIS = ("An Enterprise rescue mission becomes an ambush that strands and scatters the crew on a hostile world. "
            "With help from Jaylah, they must reunite and prevent Krall from launching a larger war.")
CAST = [
    ("John Cho", "Sulu"), ("Simon Pegg", "Scotty"),
    ("Chris Pine", "Kirk"), ("Zachary Quinto", "Spock"),
    ("Zoe Saldana", "Uhura"), ("Karl Urban", "Bones"),
    ("Anton Yelchin", "Chekov"), ("Idris Elba", "Krall"),
]
TOP_LEVEL = {
    "packet_id", "proposal_only", "role", "baseline_accepted_main", "observed_on_utc",
    "candidate_film_id", "source_locator", "source_group", "provenance_family",
    "source_access", "source_page_sha256", "film_viewed", "image_bytes_fetched",
    "full_text_available", "accepted_source_work_binding_effect", "accepted_coverage_effect",
    "public_synopsis_release_effect", "artwork_release_effect", "observation",
}
OBS_LEVEL = {
    "local_id", "section", "source_year", "rating", "genre_as_listed",
    "running_time_as_listed_minutes", "runtime_scope", "synopsis_section", "synopsis_kind",
    "synopsis_candidate", "synopsis_publication_status", "cast_section", "cast_as_listed",
    "crew_section", "director_as_listed", "writers_as_listed",
}


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def exact(actual: object, expected: object, name: str) -> None:
    check(type(actual) is type(expected) and actual == expected, f"{name}: unreviewed value")


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_pinned() -> dict:
    check(not PACKET_PATH.is_symlink() and PACKET_PATH.is_file(), "missing or symlinked packet")
    check(PACKET_PATH.stat().st_size < 12_000, "oversize packet")
    data = PACKET_PATH.read_bytes()
    exact(hashlib.sha256(data).hexdigest(), PINNED_BYTES_SHA256, "source-local packet bytes")
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicate_keys)


def validate(packet: dict, discovery: dict, prior: dict) -> int:
    check(type(packet) is dict and set(packet) == TOP_LEVEL, "unexpected top-level field")
    expected_top = {
        "packet_id": "FILMS-BEYOND-PARAMOUNT-METADATA-20261103",
        "proposal_only": True,
        "role": "FILMS",
        "baseline_accepted_main": "3c0b37564123166bf38bcfa66f018abc4d5c9996",
        "observed_on_utc": "2026-11-03",
        "candidate_film_id": "film-beyond",
        "source_locator": PARAMOUNT,
        "source_group": "publisher:paramount.com",
        "provenance_family": LINEAGE,
        "source_access": "RENDERED_PRODUCER_FILM_PAGE_READ_NO_RAW_HTML_SNAPSHOT",
        "source_page_sha256": None,
        "film_viewed": False,
        "image_bytes_fetched": False,
        "full_text_available": False,
        "accepted_source_work_binding_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "artwork_release_effect": "NONE",
    }
    for key, value in expected_top.items():
        exact(packet[key], value, key)
    exact(discovery.get("proposal_type"), "FILM_DISCOVERY_METADATA", "registry kind")
    check(any(row == {
        "id": "film-beyond", "title": "Star Trek Beyond", "work_type": "FEATURE_FILM",
        "discovery_source": "OFFICIAL_DIRECTORY",
        "source_locator": "https://www.startrek.com/movies/star-trek-beyond",
    } for row in discovery.get("films", [])), "accepted film candidate not identified")
    check(prior.get("schema_version") == "trek-film-publisher-description-paraphrase-v1", "missing prior synopsis set")
    previous = [x for x in prior.get("records", []) if x.get("candidate_film_id") == "film-beyond"]
    check(len(previous) == 1, "previous publisher description missing or duplicate")
    exact(previous[0]["source_locator"], "https://www.startrek.com/movies/star-trek-beyond", "prior source")
    check(previous[0]["source_locator"] != packet["source_locator"], "duplicated publisher locator")
    row = packet["observation"]
    check(type(row) is dict and set(row) == OBS_LEVEL, "unexpected observation field")
    expected_obs = {
        "local_id": "paramount-beyond-film-page-20261103",
        "section": "About the Film",
        "source_year": 2016,
        "rating": "PG-13",
        "genre_as_listed": "Action / Adventure / Science Fiction",
        "running_time_as_listed_minutes": 122,
        "runtime_scope": "UNSPECIFIED_VERSION_PUBLISHER_LISTING_NOT_VERIFIED_AGAINST_A_FILM_COPY",
        "synopsis_section": "Synopsis",
        "synopsis_kind": "ORIGINAL_PARAPHRASE_OF_PUBLISHER_DESCRIPTION",
        "synopsis_candidate": SYNOPSIS,
        "synopsis_publication_status": "NOT_EDITORIALLY_ADMITTED",
        "cast_section": "About the Cast",
        "crew_section": "About the Crew",
        "director_as_listed": "Justin Lin",
        "writers_as_listed": ["Simon Pegg", "Doug Jung"],
        "cast_as_listed": [{"performer": person, "role": role} for person, role in CAST],
    }
    for key, value in expected_obs.items():
        exact(row[key], value, key)
    return 1


def main() -> None:
    discovery = json.loads(DISCOVERY_PATH.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
    print(f"PASS: {validate(read_pinned(), discovery, prior)} Paramount source-local film metadata proposal; 0 coverage/release")


if __name__ == "__main__":
    main()
