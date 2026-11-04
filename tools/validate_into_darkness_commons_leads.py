#!/usr/bin/env python3
"""Validate two HELD Commons premiere photographs against an accepted film row.

File-page CC license evidence is not image-byte verification, third-party
depiction clearance, or an automatic public artwork-release permission.
This tool never makes network requests or reads/downloads image bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILM_ROWS = Path("explorer/search-catalog.json")
FILM_ROWS_SHA256 = "a197138a9069fb67ac5307055588659dd74a9fb4e1caa9d5295d24bc0687d4e5"
OUTPUT = ROOT / "proposals/librarian/into-darkness-permissive-premiere-leads-20261104/records.json"
ACCEPTED_GITHUB_MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
PINNED_SOURCE_LOCAL_ROW = "film:film-into-darkness"
PINNED_SOURCE_LOCATOR = "https://www.startrek.com/movies/star-trek-into-darkness"

# Exact per-file Commons/source metadata manually observed on 2026-11-04.
# Existing accepted film-beyond premiere photo is intentionally not duplicated.
PINS = (
    {
        "candidate_id": "commons-stid-sydney-2013-ensemble-eva-rinaldi",
        "file_page_url": "https://commons.wikimedia.org/wiki/File:Star_Trek_Into_Darkness_Cast_2013.jpg",
        "file_page_revision_url": "https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Into_Darkness_Cast_2013.jpg&oldid=1158784125",
        "file_title": "Star Trek Into Darkness Cast 2013.jpg",
        "flickr_source": "https://www.flickr.com/photos/58820009@N05/8674151469",
        "photographer": "Eva Rinaldi",
        "event_place": "Sydney, Australia",
        "event_date": "2013-04-23",
        "commons_file_original_width": 1000,
        "commons_file_original_height": 612,
        "observed_people_from_file_description": ["Karl Urban", "Zachary Quinto", "J. J. Abrams", "Chris Pine"],
        "flickr_license_review_observed": "FLICKREVIEWR_2013_04_23_CC_BY_SA_2_0_CONFIRMED",
        "photo_context": "PREMIERE_CAST_GROUP_DOCUMENTARY_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER",
        "alt_text_proposal": "Karl Urban, Zachary Quinto, J. J. Abrams and Chris Pine at the 2013 Sydney premiere of Star Trek Into Darkness.",
    },
    {
        "candidate_id": "commons-stid-sydney-2013-pine-urban-eva-rinaldi",
        "file_page_url": "https://commons.wikimedia.org/wiki/File:Chris_Pine,_Karl_Urban_(8674159443).jpg",
        "file_page_revision_url": "https://commons.wikimedia.org/w/index.php?title=File:Chris_Pine,_Karl_Urban_(8674159443).jpg&oldid=1165852288",
        "file_title": "Chris Pine, Karl Urban (8674159443).jpg",
        "flickr_source": "https://www.flickr.com/photos/58820009@N05/8674159443",
        "photographer": "Eva Rinaldi",
        "event_place": "Sydney, Australia",
        "event_date": "2013-04-23",
        "commons_file_original_width": 1000,
        "commons_file_original_height": 1821,
        "observed_people_from_file_description": ["Chris Pine", "Karl Urban"],
        "flickr_license_review_observed": "COMMONS_BOT_2013_08_08_FLICKR_CC_BY_SA_2_0_CONFIRMED",
        "photo_context": "PREMIERE_TWO_CAST_DOCUMENTARY_PHOTOGRAPH_NOT_FILM_STILL_OR_POSTER",
        "alt_text_proposal": "Chris Pine and Karl Urban at the 2013 Sydney premiere of Star Trek Into Darkness.",
    },
)


class FilmPhotoLeadRejected(ValueError):
    pass


def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise FilmPhotoLeadRejected("duplicate JSON key")
            result[key] = value
        return result
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                         parse_constant=lambda _: (_ for _ in ()).throw(FilmPhotoLeadRejected("nonfinite JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise FilmPhotoLeadRejected("invalid JSON") from exc
    if not isinstance(obj, dict):
        raise FilmPhotoLeadRejected("JSON object required")
    return obj


def build(root: Path = ROOT) -> dict:
    source = root / FILM_ROWS
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 2_000_000:
        raise FilmPhotoLeadRejected("unsafe accepted film source")
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FILM_ROWS_SHA256:
        raise FilmPhotoLeadRejected("accepted film row source SHA drift")
    catalog = strict_json(raw)
    candidates = catalog.get("rows")
    if not isinstance(candidates, list):
        raise FilmPhotoLeadRejected("accepted film rows missing")
    matched = [row for row in candidates if isinstance(row, dict) and
               row.get("row_id") == PINNED_SOURCE_LOCAL_ROW]
    if len(matched) != 1:
        raise FilmPhotoLeadRejected("film source identity ambiguous")
    target = matched[0]
    if target.get("source_locator") != PINNED_SOURCE_LOCATOR or \
       target.get("title") != "Star Trek Into Darkness" or \
       target.get("medium") != "FILM" or \
       target.get("identity_scope") != "SOURCE_LOCAL" or \
       target.get("admission_effect") != "NONE" or \
       target.get("coverage_effect") != "NONE":
        raise FilmPhotoLeadRejected("source-local film metadata drift")
    if len({item["candidate_id"] for item in PINS}) != 2 or \
       len({item["file_page_revision_url"] for item in PINS}) != 2 or \
       len({item["flickr_source"] for item in PINS}) != 2:
        raise FilmPhotoLeadRejected("duplicate Commons image candidate identity")
    return {
        "schema_version": "1.0.0",
        "batch_id": "LIBRARIAN.COMMONS.INTO_DARKNESS.PREMIERE_PHOTOS.20261104",
        "accepted_main_commit": ACCEPTED_GITHUB_MAIN,
        "reviewed_open_pr_513_is_not_accepted_main": True,
        "accepted_film_catalog_path": FILM_ROWS.as_posix(),
        "accepted_film_catalog_sha256": FILM_ROWS_SHA256,
        "source_local_film_row_id": PINNED_SOURCE_LOCAL_ROW,
        "source_local_film_locator": PINNED_SOURCE_LOCATOR,
        "source_local_film_title": "Star Trek Into Darkness",
        "not_episode_stills_not_theatrical_posters": True,
        "same_author_single_original_source_family": "EVA_RINALDI_FLICKR_VIA_WIKIMEDIA_COMMONS",
        "license_page_class": "PRIMARY_COMMONS_FILE_DESCRIPTION_AND_FLICKR_LICENSE_REVIEW_OBSERVATION",
        "license_not_other_rights": True,
        "license_reviewed_image_candidates": 2,
        "visually_inspected_image_candidates": 0,
        "file_page_cc_license_observed_count": 2,
        "independently_publication_approved_count": 0,
        "downloaded_or_embedded_photographic_bytes": False,
        "accepted_work_effect": "NONE",
        "accepted_source_effect": "NONE",
        "research_coverage_effect": "NONE",
        "public_explorer_effect": "NONE",
        "assets": [{
            **pin,
            "license_identifier": "CC-BY-SA-2.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
            "attribution_proposal": f"{pin['file_title']} — {pin['photographer']} (CC BY-SA 2.0); Wikimedia Commons source and license links required",
            "attribution_required": ["FILE_TITLE", "CREATOR", "LINK_EXACT_IMAGE", "LINK_LICENSE", "CHANGES_NOTICE", "NONENDORSEMENT"],
            "adaptation_requires_sharealike": True,
            "proposed_documentary_context_film_row_id": PINNED_SOURCE_LOCAL_ROW,
            "exact_public_artwork_release_binding": None,
            "full_image_sha256": None,
            "selected_thumbnail_sha256": None,
            "file_page_snapshot_sha256": None,
            "independent_license_reviewer": None,
            "independent_visual_reviewer": None,
            "depicted_subjects_rights_review": "NOT_DONE",
            "backdrop_branding_rights_review": "NOT_DONE",
            "image_is_official_paramount_still": False,
            "image_is_publisher_theatrical_poster": False,
            "right_to_rehost_for_explorer": "HELD_PENDING_IMAGE_AND_RIGHTS_REVIEW",
            "right_to_display_for_explorer": "HELD_PENDING_IMAGE_AND_RIGHTS_REVIEW",
            "public_release_eligible": False,
        } for pin in PINS],
    }


def validate(packet: dict, root: Path = ROOT) -> None:
    if packet != build(root):
        raise FilmPhotoLeadRejected("candidate binding, license or release state modified")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--build", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.build:
        if OUTPUT.exists() or OUTPUT.is_symlink():
            raise FilmPhotoLeadRejected("refusing overwrite or symlink output")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        if OUTPUT.parent.is_symlink():
            raise FilmPhotoLeadRejected("symlink output directory")
        OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if OUTPUT.is_symlink() or not OUTPUT.is_file() or OUTPUT.stat().st_size > 40_000:
        raise FilmPhotoLeadRejected("missing or unsafe candidate manifest")
    validate(strict_json(OUTPUT.read_bytes()))
    print("INTO_DARKNESS_COMMONS_LEADS_HELD_OK: candidates=2 license-observed=2 approved=0 images=0")


if __name__ == "__main__":
    main()
