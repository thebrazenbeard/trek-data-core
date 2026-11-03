#!/usr/bin/env python3
"""Validate two held Commons movie-premiere photographic source packets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
CATALOG_SHA256 = "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de"
BASELINE = "26d87065072fef8f6944a63b3a8a46f165f020d9"
ROOT_FIELDS = {
    "schema_version", "batch_id", "data_status", "accepted_main", "observed_on",
    "film_catalog_path", "film_catalog_sha256", "candidate_count",
    "image_bytes_read_for_hash", "image_bytes_committed",
    "public_artwork_release_effect", "explorer_effect",
    "source_work_admission_effect", "coverage_effect", "candidates",
}
# These independently reviewed code-owned candidate fingerprints are not
# supplied by records.json. An edit to a row, rights claim, source or digest
# requires explicit validator review, not a self-certified receipt mutation.
REVIEWED_ROWS = (
    ("film-2009", "Star Trek (2009)",
     "https://www.startrek.com/movies/star-trek-2009",
     "47f65a72a824d1bfc15bc50cf351f1e9081a05e761d342d2d498ae816c156cbb"),
    ("film-beyond", "Star Trek Beyond",
     "https://www.startrek.com/movies/star-trek-beyond",
     "552c4381a3ec83bd6047b490a65bdecc2815f3056d56802a9907025745e1f029"),
)


def check(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError(why)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    output = {}
    for key, value in pairs:
        check(key not in output, f"duplicate JSON key: {key}")
        output[key] = value
    return output


def read_json(path: Path) -> dict:
    def reject_constant(value: str):
        raise ValueError(f"nonfinite JSON: {value}")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object, parse_constant=reject_constant)


def sha_json(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate(packet: dict, root: Path = ROOT) -> None:
    check(type(packet) is dict and set(packet) == ROOT_FIELDS,
          "root schema mismatch or unreviewed release field")
    fixed = {
        "schema_version": "1.0.0",
        "batch_id": "LIBRARIAN.COMMONS.TWO_FILM_PREMIERES.20261103",
        "data_status": "PROPOSAL_ONLY_INDEPENDENT_DISPLAY_REVIEW_PENDING",
        "accepted_main": BASELINE,
        "observed_on": "2026-11-03",
        "film_catalog_path": "explorer/film-catalog.json",
        "film_catalog_sha256": CATALOG_SHA256,
        "candidate_count": 2,
        "image_bytes_read_for_hash": True,
        "image_bytes_committed": False,
        "public_artwork_release_effect": "NONE",
        "explorer_effect": "NONE",
        "source_work_admission_effect": "NONE",
        "coverage_effect": "NONE",
    }
    for key, expected in fixed.items():
        check(type(packet[key]) is type(expected) and packet[key] == expected,
              f"unreviewed root field: {key}")
    path = root / "explorer" / "film-catalog.json"
    check(hashlib.sha256(path.read_bytes()).hexdigest() == CATALOG_SHA256,
          "film catalog bytes differ from accepted source-local baseline")
    catalog = read_json(path)
    check(type(catalog["films"]) is list and len(catalog["films"]) == 14,
          "unexpected film catalog shape")
    rows = packet["candidates"]
    check(type(rows) is list and len(rows) == len(REVIEWED_ROWS),
          "unexpected candidates count or type")
    for record, (film_id, title, official_locator, approved_sha) in zip(rows, REVIEWED_ROWS):
        check(type(record) is dict and
              record.get("row_id") == f"film:{film_id}" and
              record.get("source_local_film_id") == film_id and
              record.get("film_title") == title and
              record.get("official_film_source") == official_locator,
              "incorrect film-to-photograph crosswalk")
        matching = [x for x in catalog["films"] if x.get("id") == film_id]
        check(len(matching) == 1 and matching[0]["title"] == title and
              matching[0]["source_locator"] == official_locator and
              matching[0]["source_group"] == "publisher:startrek.com" and
              matching[0]["work_type"] == "FEATURE_FILM" and
              matching[0]["verification_status"] == "UNVERIFIED_METADATA",
              "first-party source-local film entry differs")
        check(record.get("reported_photographer_license") == "CC_BY_2_0" and
              record.get("license_url") == "https://creativecommons.org/licenses/by/2.0/" and
              record.get("independent_pixel_review") == "PENDING" and
              record.get("editorial_display_admission") == "HELD_UNTIL_INDEPENDENT_REVIEW" and
              record.get("image_kind") ==
              "DOCUMENTARY_PREMIERE_EVENT_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER",
              "licensing, image category or rights boundary changed")
        check(sha_json(record) == approved_sha,
              "unreviewed change to exact photographer, Commons file, bytes or rights receipt")


if __name__ == "__main__":
    try:
        validate(read_json(PACKET))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"TWO_PREMIERES_PROPOSAL_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("TWO_PREMIERES_PROPOSAL_OK: 2 source-bound CC BY 2.0 leads; 0 public releases")
