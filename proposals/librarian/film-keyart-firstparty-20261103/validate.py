#!/usr/bin/env python3
"""Fail-closed, proposal-only first-party film poster URL observations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
HEX = re.compile(r"[0-9a-f]{64}\Z")
ROOT_KEYS = {
    "schema_version", "batch_id", "status", "accepted_main", "catalog_path",
    "catalog_sha256", "observed_on", "candidate_count", "image_bytes_downloaded_or_committed",
    "publisher_terms_url", "publisher_terms_get_status", "publisher_terms_response_bytes",
    "publisher_terms_raw_sha256", "publisher_terms_rights_reading",
    "external_image_display_eligible",
    "public_artwork_release_effect", "explorer_effect", "source_binding_effect",
    "coverage_effect", "artwork",
}
ROW_KEYS = {
    "candidate_id", "film_id", "film_title", "publisher_page", "page_get_status",
    "page_html_bytes", "page_raw_sha256", "poster_image_url", "poster_alt_from_page",
    "raw_html_poster_uuid_occurrences_followup", "source_observation",
    "image_identification", "image_pixel_review", "rights_status",
}
PINS = {
    "film-voyage-home": (
        "Star Trek IV: The Voyage Home",
        "https://www.startrek.com/movies/star-trek-iv-the-voyage-home",
        "https://images.prismic.io/star-trek-untold/8b45139c-36aa-42ae-a12b-43ac1f8e7747_StarTrekIV_TheVoyageHomee_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster Art for Star Trek IV: The Voyage Home",
        1379788, "7874be5c9fe8c180cf0c6fa0d8a9956aca907f4fae47fc7a4069294256cd78cb",
    ),
    "film-first-contact": (
        "Star Trek: First Contact",
        "https://www.startrek.com/movies/star-trek-viii-first-contact",
        "https://images.prismic.io/star-trek-untold/fd853cdc-24d2-4812-8896-f234f6d22755_StarTrek_FirstContact_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek: First Contact featuring Jean-Luc Picard, Data and the Borg Queen",
        1379848, "169f9c759ac7512c6c3afbda5d98643fe501d79808a3f3210c8049daaacc6b5e",
    ),
    "film-into-darkness": (
        "Star Trek Into Darkness",
        "https://www.startrek.com/movies/star-trek-into-darkness",
        "https://images.prismic.io/star-trek-untold/f90728b4-27b7-4e13-b4be-216043bba1f1_StarTrek_IntoDarkness_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek: Into Darkness",
        1379927, "681ca23a9a90e547eed7791ed908ee16b0afc195fa359f0f2ce6b5fe5c5a9865",
    ),
    "film-beyond": (
        "Star Trek Beyond",
        "https://www.startrek.com/movies/star-trek-beyond",
        "https://images.prismic.io/star-trek-untold/2fbea6e9-dc38-4a10-9965-11596b16be7a_StarTrek_Beyond_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster Art for Star Trek: Beyond",
        1379195, "c214e84c61c5dc662019b92269c63ad5ed82ec29a063bf670c42c7a04834c93e",
    ),
}


def check(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        check(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda _: check(False, "nonfinite number"))


def validate(packet: dict, root: Path = ROOT) -> None:
    check(type(packet) is dict and set(packet) == ROOT_KEYS, "closed proposal root schema")
    check(packet["schema_version"] == "1.0.0" and
          packet["batch_id"] == "LIBRARIAN.FILM.FIRST_PARTY.POSTER_LOCATORS.20261103" and
          packet["status"] == "PROPOSAL_ONLY_RIGHTS_HOLD" and
          packet["accepted_main"] == "50e20f8776abb5c78d04a89df7ed7c56c31af8ac" and
          packet["observed_on"] == "2026-11-03", "unrecognized batch identity")
    check(packet["catalog_path"] == "explorer/film-catalog.json" and
          packet["catalog_sha256"] == "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de" and
          hashlib.sha256((root / packet["catalog_path"]).read_bytes()).hexdigest() ==
          packet["catalog_sha256"], "accepted film catalog byte digest mismatch")
    check(packet["image_bytes_downloaded_or_committed"] is False and
          packet["external_image_display_eligible"] is False and
          all(packet[k] == "NONE" for k in (
              "public_artwork_release_effect", "explorer_effect",
              "source_binding_effect", "coverage_effect")),
          "source locator observation cannot claim public art or research admission")
    check(packet["publisher_terms_url"] ==
          "https://www.viacomcbs.legal/us/en/cbsi/terms-of-use" and
          packet["publisher_terms_get_status"] == 200 and
          type(packet["publisher_terms_response_bytes"]) is int and
          packet["publisher_terms_response_bytes"] == 55007 and
          packet["publisher_terms_raw_sha256"] ==
          "22cca1e7632f0f6809e718a46c5cd759683027aa1f1b3c3090a1cb9740792a35" and
          packet["publisher_terms_rights_reading"] ==
          "SECTION_4_4_1_AND_10_NO_UNAUTHORIZED_OFFSITE_INLINE_DISPLAY",
          "independently reviewed publisher terms observation changed")
    check(type(packet["artwork"]) is list and
          len(packet["artwork"]) == packet["candidate_count"] == len(PINS),
          "candidate count mismatch")
    catalog = read_json(root / packet["catalog_path"])
    film_rows = {f["id"]: f for f in catalog["films"]}
    check(len(film_rows) == 14, "film directory baseline changed")
    seen = set()
    for item in packet["artwork"]:
        check(type(item) is dict and set(item) == ROW_KEYS, "unreviewed observation field")
        film_id = item["film_id"]
        check(type(film_id) is str and film_id in PINS and film_id not in seen,
              "unrecognized or duplicate film ID")
        seen.add(film_id)
        title, page, image, alt, length, digest = PINS[film_id]
        row = film_rows[film_id]
        check(item["candidate_id"] == f"librarian-{film_id}-poster-keyart-20261103" and
              item["film_title"] == title == row["title"] and
              item["publisher_page"] == page == row["source_locator"] and
              row["source_group"] == "publisher:startrek.com" and
              row["discovery_source"] == "OFFICIAL_DIRECTORY" and
              row["verification_status"] == "UNVERIFIED_METADATA" and
              row["work_type"] == "FEATURE_FILM",
              "source-local film/page/title identity mismatch")
        check(item["poster_image_url"] == image and
              item["poster_alt_from_page"] == alt and
              item["page_get_status"] == 200 and
              type(item["page_html_bytes"]) is int and item["page_html_bytes"] == length and
              type(item["page_raw_sha256"]) is str and HEX.fullmatch(item["page_raw_sha256"]) and
              item["page_raw_sha256"] == digest,
              "unreviewed film-to-poster or source response receipt")
        check(type(item["raw_html_poster_uuid_occurrences_followup"]) is int and
              item["raw_html_poster_uuid_occurrences_followup"] == 48 and
              item["source_observation"] ==
              "FIRST_PARTY_FILM_PAGE_RENDERED_IMG_LINK_AND_SEPARATE_RAW_HTML_GET" and
              item["image_identification"] == "PUBLISHER_PAGE_POSTER_KEY_ART" and
              item["image_pixel_review"] == "NOT_PERFORMED" and
              item["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE",
              "image not reviewed/rights hold changed")
    check(seen == set(PINS), "one or more reviewed film IDs missing")


if __name__ == "__main__":
    try:
        validate(read_json(PACKET))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"FILM_POSTER_LOCATOR_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("FILM_POSTER_LOCATOR_PROPOSAL_OK: 4 exact publisher posters, 0 display grants")
