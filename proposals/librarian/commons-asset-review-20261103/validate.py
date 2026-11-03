"""Fail-closed artwork review bundle: metadata and offline preview, no public display."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FOLDER = Path(__file__).resolve().parent
PACKET = FOLDER / "records.json"
CATALOG = ROOT / "explorer/discovery-catalog.json"

TOP_FIELDS = {"schema_version", "role", "observed_on_utc", "source_effect", "work_effect",
              "evidence_effect", "coverage_effect", "site_release_effect", "artwork_binary_present",
              "remote_artwork_url_present", "public_display_authorized", "commons_photo_candidate",
              "edition_cover_candidate", "film_thumbnail_candidate"}

PHOTO = {
    "id": "commons-joe-ross-iconic-tos-props",
    "file_page": "https://commons.wikimedia.org/wiki/File:Iconic_Original_Series_Props_-Star_Trek_-_Exploring_New_Worlds_Exhibit_at_the_Henry_Ford_Museum.jpg",
    "original_source": "https://www.flickr.com/photos/joeross/49785620807/",
    "author": "Joe Ross",
    "source_date": "2019-08-22",
    "file_page_read": True,
    "file_page_license_claim": "CC BY-SA 2.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
    "license_crosscheck": "COMMONS_FLICKREVIEWR_CONFIRMED_FLICKR_LICENSE_2023-06-15",
    "commons_reported_file_sha1": "12e2558d6a21367f9c02495489d8832c4c539369",
    "commons_reported_byte_count": 6836153,
    "commons_reported_width": 3712,
    "commons_reported_height": 5568,
    "proposed_use": "OPTIONAL_DECORATIVE_MUSEUM_PHOTO_ONLY_NOT_EPISODE_STILL",
    "photograph_license": "FILE_PAGE_CC_LICENSE_RECORDED",
    "underlying_fictional_prop_design_and_brand_rights": "UNRESOLVED",
    "public_display_decision": "BLOCKED_PENDING_SEPARATE_HUMAN_RIGHTS_REVIEW",
    "attribution_text": "Iconic Original Series Props — photograph by Joe Ross (2019), CC BY-SA 2.0. No alterations; not endorsed by the photographer, Wikimedia, or the Star Trek rights holders.",
    "modifications": "NONE_PROPOSED",
    "asset_path": None,
    "asset_sha256": None,
    "image_url": None,
}

COVER = {
    "row_id": "literature:proposed-lit-snw-ring-of-fire",
    "isbn13": "9781668095898",
    "format": "Hardcover",
    "official_product_page": "https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898",
    "official_page_observation": "HIGH_RESOLUTION_BOOK_COVER_JPG_RESOURCE_ADVERTISED",
    "permissions_terms": "https://www.simonandschuster.com/p/terms-of-use",
    "rights_request_locator": "https://www.simonandschuster.biz/p/rights-and-permissions",
    "underlying_cover_rights": "NOT_CLEARED_BY_OFFICIAL_DOWNLOAD_LINK",
    "public_display_decision": "BLOCKED_PENDING_EXPRESS_REUSE_PERMISSION",
    "image_url": None,
}

FILM = {
    "row_id": "film:film-wrath-of-khan",
    "official_film_page": "https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan",
    "source_page_observation": "OFFICIAL_PAGE_CONTAINS_FILM_POSTER_IMAGE",
    "image_type": "PUBLISHER_PROMOTIONAL_POSTER_NOT_EPISODE_SCREENSHOT",
    "copyright_page_notice": "CBS_STUDIOS_AND_PARAMOUNT_ALL_RIGHTS_RESERVED",
    "independent_image_license": "NOT_FOUND",
    "public_display_decision": "BLOCKED_PENDING_EXPLICIT_STUDIO_PERMISSION_OR_DIFFERENT_RIGHTS_CLEARED_SOURCE",
    "image_url": None,
}

FORBIDDEN_ASSETS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp", ".avif",
                    ".ico", ".mp4", ".mov", ".tif", ".tiff"}


def require(predicate: bool, reason: str) -> None:
    if not predicate:
        raise ValueError(reason)


def exact_fields(value: object, expected: dict, namespace: str) -> None:
    require(type(value) is dict and set(value) == set(expected), f"{namespace} exact field set")
    for key, expected_value in expected.items():
        require(type(value[key]) is type(expected_value) and value[key] == expected_value,
                f"{namespace} {key} mismatch")


def validate(packet: dict, catalog: dict, folder: Path | None = None) -> None:
    require(type(packet) is dict and set(packet) == TOP_FIELDS, "top-level exact field set")
    baseline = {"schema_version": "1.0.0", "role": "LIBRARIAN",
                "observed_on_utc": "2026-11-03", "source_effect": "NONE",
                "work_effect": "NONE", "evidence_effect": "NONE", "coverage_effect": "NONE",
                "site_release_effect": "NONE", "artwork_binary_present": False,
                "remote_artwork_url_present": False, "public_display_authorized": False}
    for field, expected in baseline.items():
        require(type(packet[field]) is type(expected) and packet[field] == expected,
                f"top-level {field} mismatch")
    exact_fields(packet["commons_photo_candidate"], PHOTO, "Commons photograph")
    exact_fields(packet["edition_cover_candidate"], COVER, "publisher book-cover candidate")
    exact_fields(packet["film_thumbnail_candidate"], FILM, "official film poster candidate")
    require(catalog["data_status"] == "DISCOVERY_ONLY" and
            catalog["identity_scope"] == "SOURCE_LOCAL_NOT_DEDUPLICATED", "accepted catalog status")
    rows = {r["row_id"]: r for r in catalog["rows"]}
    book = rows.get(COVER["row_id"])
    require(book is not None and book["medium"] == "LITERATURE" and
            book["source_group"] == "publisher:simonandschuster.com" and
            book["source_locator"] == COVER["official_product_page"] and
            "Hardcover · ISBN 9781668095898" in book["details"], "exact publisher edition binding")
    film = rows.get(FILM["row_id"])
    require(film is not None and film["medium"] == "FILM" and
            film["source_group"] == "publisher:startrek.com" and
            film["source_locator"] == FILM["official_film_page"], "exact film source binding")
    if folder is not None:
        require(folder.is_dir(), "missing review folder")
        require(not any(p.is_file() and p.suffix.lower() in FORBIDDEN_ASSETS
                        for p in folder.rglob("*")), "review proposal contains media bytes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    args = parser.parse_args(argv)
    validate(json.loads(args.packet.read_text(encoding="utf-8")),
             json.loads(args.catalog.read_text(encoding="utf-8")), FOLDER)
    print("Artwork review bundle valid: 1 Commons photo / 1 exact ISBN cover / 1 film poster; 0 assets released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
