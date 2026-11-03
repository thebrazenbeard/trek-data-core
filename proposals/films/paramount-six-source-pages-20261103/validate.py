"""Exact, source-local gate for six first-party distributor film page observations.

This validates a candidate research packet, NOT film-viewing coverage or
authorization to publish any images or synopsis text in the Explorer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
SYNOPSES = ROOT / "proposals/research/films/publisher-synopses-20261103/observations.json"
BEYOND = ROOT / "proposals/films/beyond-paramount-metadata-20261103/records.json"
RECORD_SHA256 = "c41eeeab288dd01eff8c89e0f9749d749b16487f6b1630d84deca09badfd869e"
LINEAGE = "Paramount distributor pages are related to the StarTrek.com corporate publisher lineage; not independent film witnesses"
SECTIONS = ["About the Film", "Synopsis", "About the Cast", "About the Crew", "Follow on Social Media > movie poster"]
FAMILY = "https://public-website-assets.paramountpictures.com/paramount2025/s3fs-public/styles/poster_medium/public/"
ROWS = {
    # Film discovery ID: (Paramount URL tail, page year, rating, minutes, poster filename+query)
    "film-motion-picture": ("star-trek-the-motion-picture", 1979, "G", 132, "startrekithemotionpicture_en_800x1200.jpg?itok=Pb_3PWcx"),
    "film-wrath-of-khan": ("star-trek-ii-the-wrath-of-khan", 1982, "PG", 113, "startrek2thewrathofkhan_en_800x1200.jpg?itok=Sw_hHdtO"),
    "film-generations": ("star-trek-vii-generations", 1994, "PG", 118, "startrekgenerations-pm-800x1200-c.jpg?itok=tZSr90Bd"),
    "film-first-contact": ("star-trek-viii-first-contact", 1996, "PG-13", 112, "startrekfirstcontact-pm-800x1200-c.jpg?itok=hjoolzh8"),
    "film-2009": ("star-trek-2009", 2009, "PG-13", 127, "startrek2009_en_800x1200.jpg?itok=s9aBGrD0"),
    "film-into-darkness": ("star-trek-into-darkness", 2013, "PG-13", 132, "startrekintodarkness_en_800x1200.jpg?itok=idJWNsal"),
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


def require(test: bool, reason: str) -> None:
    if not test:
        raise ValueError(reason)


def pairs_no_dupes(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f"missing or symlinked {path.name}")
    require(path.stat().st_size < 24_000, "oversize packet")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_no_dupes)


def load_reviewed() -> dict:
    require(hashlib.sha256(PACKET.read_bytes()).hexdigest() == RECORD_SHA256, "unreviewed packet bytes")
    return load(PACKET)


def validate(data: dict, discovery: dict, prior: dict, beyond: dict) -> int:
    require(type(data) is dict and set(data) == TOP, "unexpected packet fields")
    expected = {
        "packet_id": "FILMS-PARAMOUNT-SIX-SOURCE-PAGES-20261103",
        "proposal_only": True,
        "role": "FILMS",
        "baseline_accepted_main": "5d555279116a2f9152b76754cfcb7d6c522e04c5",
        "observed_on_utc": "2026-11-03",
        "source_family": "publisher:paramount.com",
        "source_lineage": LINEAGE,
        "source_access": "SIX_RENDERED_OFFICIAL_FILM_PAGES_AND_LINKED_POSTER_PREVIEWS_NO_IMMUTABLE_SOURCE_BYTES",
        "source_page_sha256": None,
        "full_film_viewed": False,
        "accepted_source_work_binding_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "public_artwork_release_effect": "NONE",
        "poster_bytes_stored": False,
    }
    for field, value in expected.items():
        require(type(data[field]) is type(value) and data[field] == value, f"forged packet field: {field}")
    require(type(data["records"]) is list and len(data["records"]) == 6, "six distinct sources required")
    require(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "discovery registry changed")
    require(prior.get("schema_version") == "trek-film-publisher-description-paraphrase-v1", "prior synopsis lineage changed")
    require(beyond.get("candidate_film_id") == "film-beyond" and beyond.get("source_locator") ==
            "https://www.paramount.com/movies/star-trek-beyond", "accepted Paramount predecessor changed")
    ids: set[str] = set()
    poster_assets: set[str] = set()
    for row in data["records"]:
        require(type(row) is dict and set(row) == FIELDS, "unexpected source-row fields")
        film_id = row["candidate_film_id"]
        require(type(film_id) is str and film_id in ROWS and film_id not in ids, "invalid/duplicate film ID")
        ids.add(film_id)
        tail, year, rating, runtime, poster = ROWS[film_id]
        expected_source = "https://www.paramount.com/movies/" + tail
        require(row["source_locator"] == expected_source, "unverified official publisher page")
        require(row["local_id"] == "paramount-" + film_id.removeprefix("film-") + "-page-20261103", "local ID differs")
        require(row["source_sections"] == SECTIONS, "unread or misbound source section")
        require(type(row["year_as_listed"]) is int and row["year_as_listed"] == year, "page year differs")
        require(row["rating_as_listed"] == rating, "page rating differs")
        require(type(row["runtime_as_listed_minutes"]) is int and row["runtime_as_listed_minutes"] == runtime,
                "page runtime differs")
        require(row["poster_asset_locator"] == FAMILY + poster, "poster URL not exact publisher-linked asset")
        require(row["poster_asset_locator"] not in poster_assets, "duplicate poster URL")
        poster_assets.add(row["poster_asset_locator"])
        require(row["poster_label"] == "movie poster", "publisher's image label changed")
        require(row["poster_status"] == "HELD_NO_PUBLIC_REUSE_PERMISSION_VERIFIED", "artwork clearance forged")
        require(type(row["genre_as_listed"]) is str and row["genre_as_listed"], "genre missing")
        require(type(row["original_synopsis_candidate"]) is str and
                45 <= len(row["original_synopsis_candidate"]) <= 240, "unreviewed synopsis size")
        require(type(row["selected_cast_as_listed"]) is list and len(row["selected_cast_as_listed"]) == 3,
                "selected cast shape")
        for credit in row["selected_cast_as_listed"]:
            require(type(credit) is dict and set(credit) == {"performer", "role"} and
                    all(type(v) is str and 1 < len(v) < 100 for v in credit.values()), "cast field not source-local")
        require(type(row["selected_creative_roles_as_listed"]) is list and
                2 <= len(row["selected_creative_roles_as_listed"]) <= 4, "creative-credit shape")
        for credit in row["selected_creative_roles_as_listed"]:
            require(type(credit) is dict and set(credit) == {"credit", "person"} and
                    credit["credit"] in {"Director", "Writer"} and
                    type(credit["person"]) is str and credit["person"], "crew field not source-local")
        anomaly = ("PARAMOUNT_PAGE_LISTS_BOTH_PETER_LAURITSON_AND_JONATHAN_FRAKES_UNDER_DIRECTOR; NOT_RECONCILED"
                   if film_id == "film-first-contact" else None)
        require(row["source_anomaly"] == anomaly, "director-label anomaly erased or fabricated")
        require(any(f.get("id") == film_id and f.get("work_type") == "FEATURE_FILM"
                    for f in discovery["films"]), "unrecognized film discovery candidate")
        previous = [x for x in prior["records"] if x.get("candidate_film_id") == film_id]
        require(len(previous) == 1 and previous[0]["source_locator"] != expected_source,
                "prior-source lineage or duplicate contradiction")
    require(ids == set(ROWS), "one or more required film IDs missing")
    return len(ids)


def main() -> None:
    count = validate(load_reviewed(), load(DISCOVERY), load(SYNOPSES), load(BEYOND))
    print(f"PASS: {count} source-local Paramount film-page packets; 6 poster URLs HELD; 0 viewing, release or coverage")


if __name__ == "__main__":
    main()
