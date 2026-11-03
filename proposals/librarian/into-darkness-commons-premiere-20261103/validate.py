#!/usr/bin/env python3
"""Validate a source-bound, CC-licensed photograph proposal without release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
ROOT_FIELDS = {
    "schema_version", "batch_id", "data_status", "accepted_main",
    "film_catalog_path", "film_catalog_sha256", "observed_on",
    "candidate_count", "image_bytes_read_for_hash", "image_bytes_committed",
    "public_artwork_release_effect", "explorer_effect",
    "source_work_admission_effect", "coverage_effect", "candidate",
}
RECEIPT = {
    "row_id": "film:film-into-darkness",
    "source_local_film_id": "film-into-darkness",
    "film_title": "Star Trek Into Darkness",
    "official_film_source": "https://www.startrek.com/movies/star-trek-into-darkness",
    "image_kind": "DOCUMENTARY_FILM_PREMIERE_EVENT_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER",
    "suggested_alt": "Karl Urban, Zachary Quinto, J. J. Abrams and Chris Pine at the 2013 Sydney premiere of Star Trek Into Darkness",
    "creator": "Eva Rinaldi",
    "event_place": "Sydney, Australia",
    "event_date": "2013-04-23",
    "commons_file_page": "https://commons.wikimedia.org/wiki/File:Star_Trek_Into_Darkness_Cast_2013.jpg",
    "commons_pinned_revision": "https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Into_Darkness_Cast_2013.jpg&oldid=1158784125",
    "commons_revision_oldid": 1158784125,
    "commons_rights_page_http_status": 200,
    "commons_rights_page_bytes": 145529,
    "commons_rights_page_sha256": "6c715ffff293381a1cd2764a838e0463cb1119c6e208a7149944457a70e800f7",
    "original_flickr_source": "https://www.flickr.com/photos/evarinaldiphotography/8674151469/",
    "flickr_direct_read_status": "NOT_ACCESSIBLE_FROM_PUBLIC_RETRIEVAL",
    "commons_flickreviewr_license_confirmation": "2013-04-23",
    "reported_photographer_license": "CC_BY_SA_2_0",
    "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
    "license_scope": "PHOTOGRAPHER_COPY_AND_ADAPT_PERMISSION_SUBJECT_TO_ATTRIBUTION_AND_SHAREALIKE",
    "original_commons_image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d8/Star_Trek_Into_Darkness_Cast_2013.jpg",
    "original_image_http_status": 200,
    "original_image_mime": "image/jpeg",
    "original_image_width": 1000,
    "original_image_height": 612,
    "original_image_bytes": 438150,
    "original_image_sha256": "fadaaaedf16cc0b5c5924251f2ae1ddb3545a04796ec85fab951c160f9c3a9a6",
    "independent_pixel_review": "PENDING",
    "other_rights_review": "PUBLICITY_PRIVACY_MORAL_RIGHTS_AND_NONENDORSEMENT_PENDING",
    "editorial_display_admission": "HELD_UNTIL_INDEPENDENT_REVIEW",
    "attribution_requirements": "CREATOR_SOURCE_LICENSE_LINK_CHANGE_NOTICE_NO_ENDORSEMENT_AND_SA_FOR_ADAPTATIONS",
}


def check(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        check(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda _n: check(False, "nonfinite JSON value"))


def validate(packet: dict, root: Path = ROOT) -> None:
    check(type(packet) is dict and set(packet) == ROOT_FIELDS,
          "root schema mismatch or unreviewed release field")
    check(packet["schema_version"] == "1.0.0" and
          packet["batch_id"] == "LIBRARIAN.COMMONS.INTO_DARKNESS_PREMIERE.20261103" and
          packet["data_status"] == "PROPOSAL_ONLY_INDEPENDENT_PUBLIC_DISPLAY_REVIEW_PENDING" and
          packet["accepted_main"] == "a0494934782963b9a7f344cf50ed83191e08bf95" and
          packet["observed_on"] == "2026-11-03" and
          type(packet["candidate_count"]) is int and packet["candidate_count"] == 1,
          "proposal baseline or count mismatch")
    check(packet["image_bytes_read_for_hash"] is True and
          packet["image_bytes_committed"] is False and
          all(packet[key] == "NONE" for key in (
              "public_artwork_release_effect", "explorer_effect",
              "source_work_admission_effect", "coverage_effect")),
          "no public image or coverage promotion authorized")
    check(packet["film_catalog_path"] == "explorer/film-catalog.json" and
          packet["film_catalog_sha256"] ==
          "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de" and
          hashlib.sha256((root / packet["film_catalog_path"]).read_bytes()).hexdigest() ==
          packet["film_catalog_sha256"], "film catalog source bytes changed")
    film_catalog = read_json(root / packet["film_catalog_path"])
    films = film_catalog["films"]
    check(type(films) is list and len(films) == 14, "unexpected film directory shape")
    found = [r for r in films if r.get("id") == "film-into-darkness"]
    check(len(found) == 1 and found[0]["title"] == RECEIPT["film_title"] and
          found[0]["source_locator"] == RECEIPT["official_film_source"] and
          found[0]["source_group"] == "publisher:startrek.com" and
          found[0]["work_type"] == "FEATURE_FILM" and
          found[0]["verification_status"] == "UNVERIFIED_METADATA",
          "wrong public film source-local row")
    row = packet["candidate"]
    check(type(row) is dict and set(row) == set(RECEIPT),
          "photo receipt fields mismatch")
    for key, value in RECEIPT.items():
        check(type(row[key]) is type(value) and row[key] == value,
              f"unreviewed photo/rights/source identity: {key}")


if __name__ == "__main__":
    try:
        validate(read_json(PACKET))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"PREMIERE_PHOTO_PROPOSAL_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("PREMIERE_PHOTO_PROPOSAL_OK: 1 source-bound photographer-CC candidate, 0 released")
