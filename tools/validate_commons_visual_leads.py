#!/usr/bin/env python3
"""Fail-closed, metadata-only Commons file-level license observation packet.

This is a research intake gate, NOT copyright clearance or an artwork release
gate. No image bytes are read and no network request is performed here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "proposals/librarian/commons-license-visual-leads-20261104/records.json"

# Exact Commons file-page metadata observed from original per-file pages on
# 2026-11-04. This is a document assertion about a *photograph* license only.
# It does not license Star Trek trademarks, underlying props or people's likeness.
PINS = (
    {
        "candidate_id": "commons-2011-nimoy-convention-photo",
        "file_page_url": "https://commons.wikimedia.org/wiki/File:Leonard_Nimoy,_2011,_ST_Con-2.jpg",
        "file_page_revision_url": "https://commons.wikimedia.org/w/index.php?title=File:Leonard_Nimoy,_2011,_ST_Con-2.jpg&oldid=1138116837",
        "photo_subject": "Leonard Nimoy at 2011 Star Trek convention",
        "photo_creator": "Beth Madison",
        "original_creator_source_url": "https://www.flickr.com/photos/29456903@N04/6060504064",
        "license_identifier_observed": "CC-BY-2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "license_provenance": "FLICKREVIEWR_FLICKR_CC_BY_2_0_CONFIRMED_2011_10_30",
        "file_date": "2011-08-13",
        "proposed_context": "REAL_ACTOR_CONVENTION_PHOTO_NOT_SPOCK_OR_EPISODE_STILL",
        "third_party_rights_review_items": ["IDENTIFIABLE_PERSON_PUBLICITY_PRIVACY", "NO_ENDORSEMENT"],
    },
    {
        "candidate_id": "commons-2013-star-trek-convention-photo",
        "file_page_url": "https://commons.wikimedia.org/wiki/File:Star_Trek_Convention_(9501108956).jpg",
        "file_page_revision_url": "https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Convention_(9501108956).jpg&oldid=978911963",
        "photo_subject": "Star Trek fan convention in Las Vegas, 2013",
        "photo_creator": "Tomás Del Coro",
        "original_creator_source_url": "https://www.flickr.com/photos/tomasdelcoro/9501108956/",
        "license_identifier_observed": "CC-BY-SA-2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "license_provenance": "FLICKREVIEWR_FLICKR_CC_BY_SA_2_0_CONFIRMED_2017_04_24",
        "file_date": "2013-08-10",
        "proposed_context": "FANDOM_OR_CONVENTION_CONTEXT_NOT_EPISODE_OR_FILM_FRAME",
        "third_party_rights_review_items": ["IDENTIFIABLE_ATTENDEES_IF_VISIBLE", "COSTUME_OR_BRANDED_DESIGN_IF_VISIBLE", "NO_ENDORSEMENT"],
    },
    {
        "candidate_id": "commons-2022-tos-set-tour-exterior-photo",
        "file_page_url": "https://commons.wikimedia.org/wiki/File:Star_Trek_Original_Series_Set_Tour_Ticonderoga_NY.jpg",
        "file_page_revision_url": "https://commons.wikimedia.org/w/index.php?title=File:Star_Trek_Original_Series_Set_Tour_Ticonderoga_NY.jpg&oldid=946074810",
        "photo_subject": "Star Trek Original Series Set Tour building exterior in Ticonderoga, New York",
        "photo_creator": "Kenneth C. Zirkel",
        "original_creator_source_url": None,
        "license_identifier_observed": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "license_provenance": "COMMONS_UPLOADER_OWN_WORK_ASSERTION",
        "file_date": "2022-07-15",
        "proposed_context": "REAL_WORLD_SET_TOUR_NOT_TOS_PRODUCTION_STILL",
        "third_party_rights_review_items": ["TRADEMARK_OR_SIGNAGE_IF_VISIBLE", "UNDERLYING_SCULPTURE_OR_PROP_IF_VISIBLE", "NO_ENDORSEMENT"],
    },
)


class CommonsLeadRejected(ValueError):
    pass


def expected_packet() -> dict:
    return {
        "schema_version": "1.0.0",
        "batch_id": "COMMONS.LICENSE.VISUAL.LEADS.20261104",
        "accepted_main_base": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "observed_utc_date": "2026-11-04",
        "source_class": "PRIMARY_FILE_PAGE_LICENSE_AND_CREATOR_METADATA",
        "source_scope": "WIKIMEDIA_COMMONS_THIRD_PARTY_HOSTED_FILES",
        "source_reuse_guidance_url": "https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia",
        "license_scope_warning_url": "https://creativecommons.org/faq/",
        "proposal_only": True,
        "file_page_license_claims_observed": 3,
        "independently_approved_for_trek_explorer": 0,
        "released_artwork_assets": [],
        "retrieved_image_bytes": False,
        "committed_image_bytes": False,
        "accepted_source_work_effect": "NONE",
        "research_coverage_effect": "NONE",
        "public_explorer_effect": "NONE",
        "candidates": [{
            **pin,
            "license_evidence_class": "FILE_PAGE_AND_PRIOR_PLATFORM_REVIEW_OBSERVATION_NOT_TREK_RIGHTS_APPROVAL",
            "license_not_covering_other_rights": True,
            "attribution_requirements": ["CREATOR", "SOURCE_FILE_PAGE", "LICENSE_LINK", "CHANGE_INDICATION", "NO_ENDORSEMENT"] +
                                        (["SHAREALIKE_IF_ADAPTED"] if "BY-SA" in pin["license_identifier_observed"] else []),
            "independent_license_reviewer": None,
            "independent_visual_reviewer": None,
            "image_sha256": None,
            "exact_explorer_work_binding": None,
            "candidate_status": "HELD_FILE_PAGE_LICENSE_VISIBLE_RELEASE_NOT_REVIEWED",
            "public_display_eligible": False,
            "public_rehost_eligible": False,
        } for pin in PINS],
    }


def _strict_json(raw: bytes) -> dict:
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise CommonsLeadRejected("duplicate JSON key")
            out[k] = v
        return out
    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=lambda _: (_ for _ in ()).throw(CommonsLeadRejected("non-finite JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CommonsLeadRejected("malformed JSON") from exc
    if not isinstance(parsed, dict):
        raise CommonsLeadRejected("packet must be object")
    return parsed


def validate(data: dict) -> None:
    # No external supplied packet, fake reviewer, attached image, or rights
    # label can self-promote a Commons lead into public Explorer state.
    if data != expected_packet():
        raise CommonsLeadRejected("changed file source, license, attribution, binding or release status")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--build", action="store_true", help="create only the local proposed metadata packet")
    args = parser.parse_args()
    if args.build:
        if RECORD_PATH.exists() or RECORD_PATH.is_symlink():
            raise CommonsLeadRejected("refusing to overwrite candidate packet")
        RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
        if RECORD_PATH.parent.is_symlink():
            raise CommonsLeadRejected("symlink output directory")
        RECORD_PATH.write_text(json.dumps(expected_packet(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if RECORD_PATH.is_symlink() or not RECORD_PATH.is_file() or RECORD_PATH.stat().st_size > 60_000:
        raise CommonsLeadRejected("unsafe or missing record packet")
    validate(_strict_json(RECORD_PATH.read_bytes()))
    print("COMMONS_FILE_LICENSE_LEADS_HELD_OK: files=3 approved=0 images=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
