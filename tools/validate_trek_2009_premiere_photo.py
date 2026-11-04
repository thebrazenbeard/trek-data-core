#!/usr/bin/env python3
"""Pin a HELD film-specific CC photograph; do not release artwork."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("explorer/search-catalog.json")
SOURCE_SHA = "a197138a9069fb67ac5307055588659dd74a9fb4e1caa9d5295d24bc0687d4e5"
OUTPUT = ROOT / "proposals/librarian/trek-2009-premiere-cc-photo-20261104/records.json"
ACCEPTED_MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
FILM_ROW = "film:film-2009"
FILM_URL = "https://www.startrek.com/movies/star-trek-2009"
COMMONS_FILE_PAGE = "https://commons.wikimedia.org/wiki/File:StarTrekSydneyOperaHousePremiereApr09.jpg"
COMMONS_REVISION = "https://commons.wikimedia.org/w/index.php?title=File:StarTrekSydneyOperaHousePremiereApr09.jpg&oldid=1254161622"
CC_LICENSE = "https://creativecommons.org/licenses/by/2.0/"


class HeldPhotoRejected(ValueError):
    pass


def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise HeldPhotoRejected("duplicate key")
            out[key] = value
        return out
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                         parse_constant=lambda _: (_ for _ in ()).throw(HeldPhotoRejected("nonfinite JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise HeldPhotoRejected("malformed JSON") from exc
    if not isinstance(obj, dict):
        raise HeldPhotoRejected("packet must be object")
    return obj


def expected(root: Path = ROOT) -> dict:
    path = root / SOURCE
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise HeldPhotoRejected("missing or unsafe accepted film catalog")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise HeldPhotoRejected("accepted film catalog SHA changed")
    rows = strict_json(raw).get("rows")
    if not isinstance(rows, list):
        raise HeldPhotoRejected("accepted film rows missing")
    matches = [r for r in rows if isinstance(r, dict) and r.get("row_id") == FILM_ROW]
    if len(matches) != 1:
        raise HeldPhotoRejected("film row missing or duplicated")
    row = matches[0]
    for key, value in (
        ("title", "Star Trek (2009)"),
        ("medium", "FILM"),
        ("candidate_kind", "FEATURE_FILM"),
        ("source_locator", FILM_URL),
        ("identity_scope", "SOURCE_LOCAL"),
        ("admission_effect", "NONE"),
        ("coverage_effect", "NONE"),
    ):
        if row.get(key) != value:
            raise HeldPhotoRejected(f"accepted film mismatch at {key}")
    return {
        "schema_version": "1.0.0",
        "batch_id": "LIBRARIAN.TREK_2009.COMMONS.PREMIERE.PHOTO.20261104",
        "accepted_main_commit": ACCEPTED_MAIN,
        "draft_pr_523_not_accepted_main": True,
        "accepted_film_row_receipt": {"path": SOURCE.as_posix(), "sha256": SOURCE_SHA,
                                      "row_id": FILM_ROW, "source_locator": FILM_URL,
                                      "title": "Star Trek (2009)"},
        "source_license_class": "COMMONS_FILE_PAGE_AND_FLICKR_LICENSE_REVIEW_OBSERVATION",
        "source_photographer_count": 1,
        "distinct_image_candidate_count": 1,
        "image_byte_observation_count": 0,
        "independently_approved_display_count": 0,
        "copied_photographic_bytes": False,
        "public_artwork_effect": "NONE",
        "accepted_work_effect": "NONE",
        "accepted_source_effect": "NONE",
        "research_coverage_effect": "NONE",
        "candidate": {
            "candidate_id": "commons-st2009-sydney-opera-house-premiere-cast",
            "photo_title": "StarTrekSydneyOperaHousePremiereApr09.jpg",
            "commons_file_page": COMMONS_FILE_PAGE,
            "commons_fixed_revision": COMMONS_REVISION,
            "original_source": "https://www.flickr.com/photos/visible-woman/3420160659",
            "photographer_display_name": "Penny B. Dreadful",
            "license_identifier_observed": "CC-BY-2.0",
            "license_url": CC_LICENSE,
            "license_review_observed": "COMMONS_TRUSTED_USER_HIGH_CONTRAST_2009_05_02_CONFIRMED_FLICKR_CC_BY_2_0",
            "license_page_explicit_rights_warning": "PERSONALITY_RIGHTS_OF_DEPICTED_PEOPLE",
            "photo_date": "2009-04-07",
            "documentary_event": "SYDNEY_OPERA_HOUSE_STAR_TREK_2009_FILM_PREMIERE",
            "event_city": "Sydney, Australia",
            "commons_original_dimensions": {"width": 1886, "height": 934},
            "commons_structured_metadata_original_sha1_claim_not_recomputed": "57f3913143347cdf32056a57aeb86e6b9086b33b",
            "subject_names_claimed_in_commons_file_description": [
                "Karl Urban", "Chris Pine", "Bryan Burk", "Zachary Quinto",
                "J. J. Abrams", "Eric Bana", "John Cho",
            ],
            "source_local_film_row_id_proposed_context": FILM_ROW,
            "proposed_image_kind": "OTHER_DOCUMENTARY_PREMIERE_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER",
            "alt_text_proposal": "Cast and filmmakers at the 2009 Star Trek Sydney Opera House film premiere.",
            "attribution_proposal": "StarTrekSydneyOperaHousePremiereApr09.jpg — Penny B. Dreadful, CC BY 2.0",
            "required_credit_components": ["FILE_TITLE", "PHOTOGRAPHER", "SOURCE_FILE_PAGE_URL",
                                           "LICENSE_URL", "CHANGES_NOTICE_IF_ADAPTED", "NONENDORSEMENT"],
            "photo_license_excludes_other_rights_clearance": True,
            "people_publicity_privacy_review": "NOT_DONE",
            "branding_backdrop_trademark_review": "NOT_DONE",
            "independent_visual_review": "NOT_DONE",
            "independent_legal_rights_review": "NOT_DONE",
            "exact_source_image_sha256": None,
            "exact_selected_thumbnail_sha256": None,
            "commons_page_snapshot_sha256": None,
            "reviewed_rights_receipt_sha256": None,
            "exact_explorer_release_binding": None,
            "public_display_eligible": False,
            "public_rehost_eligible": False,
            "release_status": "HELD_RIGHTS_AND_IMAGE_BYTE_GATE",
        },
    }


def validate(packet: dict, root: Path = ROOT) -> None:
    if packet != expected(root):
        raise HeldPhotoRejected("source, image, license or release state mutation")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if args.build:
        if OUTPUT.exists() or OUTPUT.is_symlink():
            raise HeldPhotoRejected("refuse overwrite or symlink")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        if OUTPUT.parent.is_symlink():
            raise HeldPhotoRejected("symlink output dir")
        OUTPUT.write_text(json.dumps(expected(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if OUTPUT.is_symlink() or not OUTPUT.is_file() or OUTPUT.stat().st_size > 25_000:
        raise HeldPhotoRejected("missing or unsafe held packet")
    validate(strict_json(OUTPUT.read_bytes()))
    print("TREK_2009_PREMIERE_HELD_OK: file=1 CC-BY-2.0=1 approved=0 pixels=0")


if __name__ == "__main__":
    main()
