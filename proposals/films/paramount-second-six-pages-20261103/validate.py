"""Fail-closed candidate gate: six new first-party Paramount film-page observations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
REGISTRY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PREVIOUS = ROOT / "proposals/films/paramount-six-source-pages-20261103/records.json"
STAR_TREK_PRIOR = ROOT / "proposals/research/films/publisher-synopses-20261103/observations.json"
RECORD_SHA256 = "aa590b5f77f0d148595814cd8d74fa7186c49c45fb32f854c7568d720f3e0b41"
LINEAGE = "Paramount movie pages and StarTrek.com publisher directory are related corporate sources, not independent film witnesses"
SECTIONS = ["About the Film", "Synopsis", "About the Cast", "About the Crew", "Follow on Social Media > movie poster"]
POSTER_PREFIX = "https://public-website-assets.paramountpictures.com/paramount2025/s3fs-public/styles/poster_medium/public/"
ITEMS = {
    "film-search-for-spock": ("star-trek-iii-the-search-for-spock", 1984, "PG", 105, "startrekiiithesearchforspock_en_refresh_800x1200.jpg?itok=h13sK86Q"),
    "film-voyage-home": ("star-trek-iv-the-voyage-home", 1986, "PG", 119, "startrekivthevoyagehome_en_refresh_800x1200_noquote.jpg?itok=tdIwFpAF"),
    "film-final-frontier": ("star-trek-v-the-final-frontier", 1989, "PG", 106, "startrekvthefinalfrontier_en_refresh_800x1200.jpg?itok=uyoLLKHy"),
    "film-undiscovered-country": ("star-trek-vi-the-undiscovered-country", 1991, "PG", 109, "startrekvitheundiscoveredcountry_en_refresh_800x1200_noquote.jpg?itok=I4lElNuH"),
    "film-insurrection": ("star-trek-ix-insurrection", 1998, "PG", 104, "startrekinsurrection-pm-800x1200-c.jpg?itok=IB6WIzna"),
    "film-nemesis": ("star-trek-x-nemesis", 2002, "PG-13", 117, "startreknemesis-pm-800x1200-c.jpg?itok=IxoXH5ZJ"),
}
ROW_SHA256 = {
    "film-search-for-spock": "e791456b521b3787bd15331aadb984f671327caeb9d20a8255d28a16903d8484",
    "film-voyage-home": "20557a6777021f3585adca42a75cc1bcca269c42ad88ef73ce413c6d1acaf2d7",
    "film-final-frontier": "4d1c25d8464cde97588b5ebc4bf21d549b2ec04dd4e8cb533d141812a9bf1e15",
    "film-undiscovered-country": "1a2fe64a81ae69950a6c3b40993806087840ab959cea9f99499d930b89c1e5a4",
    "film-insurrection": "21d79193c701990476ab4b0716380bdeee36adb41c578c2c2ca30bfdcaf87ef5",
    "film-nemesis": "4965bf16d1e3f6090b240057c4fd2cc82e08d72dd8ea95dfbeb0f72480af009b",
}
TOP = {
    "packet_id", "proposal_only", "role", "baseline_accepted_main", "observed_on_utc",
    "source_family", "source_lineage", "source_access", "source_page_sha256",
    "full_film_viewed", "accepted_source_work_binding_effect", "accepted_coverage_effect",
    "public_synopsis_release_effect", "public_artwork_release_effect", "poster_bytes_stored", "records",
}
FIELDS = {
    "local_id", "candidate_film_id", "source_locator", "source_sections", "year_as_listed",
    "rating_as_listed", "genre_as_listed", "runtime_as_listed_minutes", "selected_cast_as_listed",
    "selected_creative_roles_as_listed", "original_synopsis_candidate", "poster_asset_locator",
    "poster_label", "poster_status", "source_anomaly",
}


def check(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def nodupes(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path: Path) -> dict:
    check(path.is_file() and not path.is_symlink(), "unavailable or symlinked source record")
    check(path.stat().st_size < 25_000, "oversize source record")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=nodupes)


def reviewed() -> dict:
    check(hashlib.sha256(RECORDS.read_bytes()).hexdigest() == RECORD_SHA256, "unreviewed source record bytes")
    return load(RECORDS)


def validate(data: dict, discovery: dict, previous: dict, prior: dict) -> int:
    check(type(data) is dict and set(data) == TOP, "packet fields changed")
    exact = {
        "packet_id": "FILMS-PARAMOUNT-SECOND-SIX-PAGES-20261103",
        "proposal_only": True,
        "role": "FILMS",
        "baseline_accepted_main": "5b59deec9cf832ed030f25bd09c6fd7c318efb90",
        "observed_on_utc": "2026-11-03",
        "source_family": "publisher:paramount.com",
        "source_lineage": LINEAGE,
        "source_access": "SIX_RENDERED_PUBLISHER_PAGES_AND_POSTER_IMAGE_PREVIEWS_NO_IMMUTABLE_PAGE_OR_ASSET_BYTES",
        "source_page_sha256": None,
        "full_film_viewed": False,
        "accepted_source_work_binding_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "public_artwork_release_effect": "NONE",
        "poster_bytes_stored": False,
    }
    for key, value in exact.items():
        check(type(data[key]) is type(value) and data[key] == value, "packet boundary changed: " + key)
    check(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "film discovery registry missing")
    check(prior.get("schema_version") == "trek-film-publisher-description-paraphrase-v1", "prior publisher synopsis missing")
    check(previous.get("packet_id") == "FILMS-PARAMOUNT-SIX-SOURCE-PAGES-20261103", "accepted Paramount predecessor missing")
    earlier = {row.get("candidate_film_id") for row in previous.get("records", [])}
    check(type(data["records"]) is list and len(data["records"]) == 6, "required six source packets")
    ids: set[str] = set()
    posters: set[str] = set()
    for record in data["records"]:
        check(type(record) is dict and set(record) == FIELDS, "unexpected source record fields")
        film = record["candidate_film_id"]
        check(type(film) is str and film in ITEMS and film not in ids and film not in earlier,
              "film ID reused, duplicated, or unsupported")
        ids.add(film)
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        check(hashlib.sha256(canonical).hexdigest() == ROW_SHA256[film], "unreviewed source-local row contents")
        slug, year, rating, runtime, art_tail = ITEMS[film]
        source = "https://www.paramount.com/movies/" + slug
        check(record["source_locator"] == source, "source URL/film mismatch")
        check(record["local_id"] == "paramount-" + film.removeprefix("film-") + "-page-20261103", "local ID mismatch")
        check(record["source_sections"] == SECTIONS, "source section mismatch")
        check(type(record["year_as_listed"]) is int and record["year_as_listed"] == year, "publisher year mismatch")
        check(record["rating_as_listed"] == rating, "rating mismatch")
        check(type(record["runtime_as_listed_minutes"]) is int and record["runtime_as_listed_minutes"] == runtime,
              "runtime mismatch")
        check(record["genre_as_listed"] == "Science Fiction / Action / Adventure", "publisher genre mismatch")
        check(record["poster_asset_locator"] == POSTER_PREFIX + art_tail, "poster asset not source-bound")
        check(record["poster_asset_locator"] not in posters, "duplicate poster")
        posters.add(record["poster_asset_locator"])
        check(record["poster_label"] == "movie poster" and
              record["poster_status"] == "HELD_NO_PUBLIC_REUSE_PERMISSION_VERIFIED", "image rights inflated")
        check(type(record["original_synopsis_candidate"]) is str and
              45 <= len(record["original_synopsis_candidate"]) <= 240, "publisher paraphrase missing or excessive")
        check(type(record["selected_cast_as_listed"]) is list and len(record["selected_cast_as_listed"]) == 3,
              "selected cast not bounded")
        for pair in record["selected_cast_as_listed"]:
            check(type(pair) is dict and set(pair) == {"performer", "role"} and
                  all(type(v) is str and 1 <= len(v) <= 100 for v in pair.values()), "bad cast source label")
        check(type(record["selected_creative_roles_as_listed"]) is list and
              len(record["selected_creative_roles_as_listed"]) == 2, "creative role selection differs")
        for pair in record["selected_creative_roles_as_listed"]:
            check(type(pair) is dict and set(pair) == {"credit", "person"} and
                  pair["credit"] in {"Director", "Writer"} and
                  type(pair["person"]) is str and pair["person"], "bad crew source label")
        anomaly = {
            "film-search-for-spock": "PARAMOUNT_YEAR_1984_DIFFERS_FROM_STARTREK_COM_YEAR_1982; AFI_CATALOG_LISTS_1984; NOT_RECONCILED",
            "film-insurrection": "PARAMOUNT_CREDIT_LABELS_RUAFRO_ANJI_AND_MICHAEL_PILLAR_AS_WRITTEN; SPELLINGS_UNVERIFIED_NOT_RECONCILED",
        }.get(film)
        check(record["source_anomaly"] == anomaly, "source anomaly omitted or fabricated")
        check(any(row.get("id") == film and row.get("work_type") == "FEATURE_FILM"
                  for row in discovery.get("films", [])), "film candidate missing from accepted index")
        rows = [row for row in prior.get("records", []) if row.get("candidate_film_id") == film]
        check(len(rows) == 1 and rows[0]["source_locator"] != source, "publisher provenance collapsed")
    check(ids == set(ITEMS), "required film candidates missing")
    return len(ids)


def main() -> None:
    n = validate(reviewed(), load(REGISTRY), load(PREVIOUS), load(STAR_TREK_PRIOR))
    print(f"PASS: {n} source-local Paramount pages and HELD poster URLs; 0 coverage or public display")


if __name__ == "__main__":
    main()
