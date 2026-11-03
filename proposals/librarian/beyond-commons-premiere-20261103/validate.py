#!/usr/bin/env python3
"""Validate a film-specific licensed-photo custody *proposal*, never release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path(__file__).with_name("records.json")


def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def read_json(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=unique_pairs,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"nonfinite {x}")),
    )


def require(test: bool, what: str) -> None:
    if not test:
        raise ValueError(what)


def validate(packet: dict, root: Path = ROOT) -> None:
    require(type(packet) is dict, "packet must be a dictionary")
    require(set(packet) == {
        "schema_version", "batch_id", "data_status", "accepted_main",
        "film_catalog_path", "film_catalog_sha256", "observed_on",
        "candidate_count", "image_bytes_read_for_hash_and_pixel_review",
        "image_bytes_committed", "public_artwork_release_effect",
        "explorer_effect", "source_work_admission_effect", "coverage_effect",
        "candidate",
    }, "unexpected root fields")
    require(packet["schema_version"] == "1.0.0", "schema version")
    require(packet["batch_id"] == "LIBRARIAN.COMMONS.BEYOND_PREMIERE.20261103", "batch ID")
    require(packet["data_status"] == "PROPOSAL_ONLY_PUBLIC_DISPLAY_REVIEW_PENDING", "status must be held")
    require(packet["accepted_main"] == "2b1b76850abfe23bab42977e60213c06e70165ee", "base main provenance")
    require(packet["film_catalog_path"] == "explorer/film-catalog.json", "catalog path")
    require(packet["film_catalog_sha256"] == "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de", "catalog checksum")
    require(packet["observed_on"] == "2026-11-03", "observation date")
    require(type(packet["candidate_count"]) is int and packet["candidate_count"] == 1, "candidate count")
    require(packet["image_bytes_read_for_hash_and_pixel_review"] is True, "hashing flag")
    require(packet["image_bytes_committed"] is False, "image bytes must not be committed")
    for key in ("public_artwork_release_effect", "explorer_effect", "source_work_admission_effect", "coverage_effect"):
        require(packet[key] == "NONE", f"protected effect: {key}")

    catalog_bytes = (root / packet["film_catalog_path"]).read_bytes()
    require(hashlib.sha256(catalog_bytes).hexdigest() == packet["film_catalog_sha256"], "catalog drift")
    catalog = json.loads(catalog_bytes)
    matches = [row for row in catalog["films"] if row.get("id") == "film-beyond"]
    require(len(matches) == 1, "missing/ambiguous official film row")
    film = matches[0]
    candidate = packet["candidate"]
    require(type(candidate) is dict, "candidate must be a dictionary")
    require(set(candidate) == {
        "row_id", "source_local_film_id", "film_title", "official_film_source",
        "image_kind", "suggested_alt", "creator", "event_place", "event_date",
        "commons_file_page", "commons_pinned_revision", "commons_revision_oldid",
        "commons_rights_page_http_status", "commons_rights_page_bytes",
        "commons_rights_page_sha256", "original_flickr_source",
        "flickr_public_page_observation", "commons_flickreviewr_license_confirmation",
        "reported_photographer_license", "license_url", "license_scope",
        "original_commons_image_url", "original_image_http_status",
        "original_image_mime", "original_image_width", "original_image_height",
        "original_image_bytes", "original_image_sha256", "pixel_review",
        "other_rights_review", "editorial_display_admission", "attribution_requirements",
    }, "unexpected candidate fields")
    require(candidate["row_id"] == "film:film-beyond", "source-local art row")
    require(candidate["source_local_film_id"] == film["id"], "film ID mismatch")
    require(candidate["film_title"] == film["title"], "film title mismatch")
    require(candidate["official_film_source"] == film["source_locator"], "first-party source mismatch")
    require(candidate["image_kind"] == "DOCUMENTARY_JAPAN_FILM_PREMIERE_EVENT_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER", "genre must be documentary")
    require(
        candidate["suggested_alt"]
        == "J. J. Abrams and Simon Pegg at the October 2016 Star Trek Beyond Japan premiere, with Simon Pegg holding a microphone",
        "exact event caption required; never let a film-frame or scene claim pass",
    )
    require(candidate["creator"] == "Dick Thomas Johnson", "creator attribution")
    require(candidate["event_place"] == "Japan" and candidate["event_date"] == "2016-10-19", "event provenance")
    file_part = "Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg"
    page_part = "Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_(31784488840).jpg"
    require(candidate["commons_file_page"] == "https://commons.wikimedia.org/wiki/File:" + file_part, "Commons file URL")
    require(candidate["commons_pinned_revision"] == "https://commons.wikimedia.org/w/index.php?title=File:" + page_part + "&oldid=1217252320", "Commons revision URL")
    require(type(candidate["commons_revision_oldid"]) is int and candidate["commons_revision_oldid"] == 1217252320, "revision")
    require(candidate["commons_rights_page_http_status"] == 200, "pinned page retrieval status")
    require(type(candidate["commons_rights_page_bytes"]) is int and candidate["commons_rights_page_bytes"] == 131423, "pinned page byte count")
    require(candidate["commons_rights_page_sha256"] == "120ef8dab3534b75d8c0cbf56f0dede4ea3a232a4e31e31d081488a3579bc1c1", "rights page digest")
    require(candidate["original_flickr_source"] == "https://www.flickr.com/photos/31029865@N06/31784488840/", "original source")
    require(candidate["flickr_public_page_observation"] == "PHOTOGRAPHER_DATE_AND_CC_BY_2_0_LICENSE_LINK_OBSERVED", "Flickr observation")
    require(candidate["commons_flickreviewr_license_confirmation"] == "2017-01-08", "Commons review")
    require(candidate["reported_photographer_license"] == "CC_BY_2_0", "license label")
    require(candidate["license_url"] == "https://creativecommons.org/licenses/by/2.0/", "license URL")
    require("NONENDORSEMENT" in candidate["license_scope"], "license restrictions")
    require(candidate["original_commons_image_url"] == "https://upload.wikimedia.org/wikipedia/commons/a/a4/" + file_part, "image URL")
    require(candidate["original_image_http_status"] == 200 and candidate["original_image_mime"] == "image/jpeg", "image retrieval")
    require((candidate["original_image_width"], candidate["original_image_height"], candidate["original_image_bytes"]) == (4552, 3035, 4134183), "image dimensions/bytes")
    require(candidate["original_image_sha256"] == "7fd481633086f97e7b05e0eccbd3515a90d44f4fa7ce1255180007d9d13b4250", "image digest")
    require(candidate["pixel_review"] == "HUMAN_STYLE_MODEL_VISUAL_INSPECTION_SEES_ABRAMS_AND_PEGG_AT_MIC_CANNOT_PROVE_EVENT_DATE_FROM_PIXELS", "pixel review class")
    require(candidate["other_rights_review"] == "PERSONALITY_PRIVACY_AND_EDITORIAL_NONENDORSEMENT_PENDING", "other rights review")
    require(candidate["editorial_display_admission"] == "HELD_UNTIL_INDEPENDENT_REVIEW", "display hold")
    require(candidate["attribution_requirements"] == "CREATOR_SOURCE_LICENSE_LINK_CHANGE_NOTICE_AND_NO_ENDORSEMENT", "attribution contract")
    require(all(not path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
                for path in RECORD.parent.iterdir()), "image binary in public proposal")


if __name__ == "__main__":
    validate(read_json(RECORD))
    print("PASS: source-bound held Star Trek Beyond premiere photograph (no display release)")
