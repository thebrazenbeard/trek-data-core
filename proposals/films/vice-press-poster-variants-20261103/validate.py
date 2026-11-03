"""Fail-closed source/edition guard for a three-print Vice Press proposal."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
FILM_DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
ACCEPTED_MAIN = "5ea4a8d562e76931218329b8386e363e3c40845f"
ANNOUNCEMENT = "https://vice-press.com/blogs/news/star-trek-iv-the-voyage-home-by-bob-peak"
PARTNER_GUIDE = "https://www.startrek.com/gallery/star-trek-day-2024-gift-guide"
LINEAGE_NOTE = ("Vice Press editorial announcement and three variants derive from one product producer. "
                "StarTrek.com product coverage repeats partner marketing and does not independently license images to this project.")
CREATORS = {
    "original_artwork_credit": "Bob Peak",
    "original_art_supplied_by": "Thomas Peak",
    "remaster_credit": "Matt Ferguson",
    "claim_scope": "VICE_PRESS_2024_MARKETING_STATEMENT_NOT_INDEPENDENT_RIGHTS_CHAIN",
}

VARIANT_KEYS = {
    "local_entity_id", "evidence_id", "source_locator", "product_locator", "variant_kind",
    "evidence_kind", "evidence_observed", "edition_limit", "dimensions_inches",
    "artwork_basis", "source_assertion", "rights_status", "eligible_for_thumbnail",
}


def expected_variant(local_id, evidence_id, product_locator, kind, observed, limit, assertion):
    return {
        "local_entity_id": local_id,
        "evidence_id": evidence_id,
        "source_locator": ANNOUNCEMENT,
        "product_locator": product_locator,
        "variant_kind": kind,
        "evidence_kind": "PRODUCER_PAGE_VARIANT_DESCRIPTION",
        "evidence_observed": observed,
        "edition_limit": limit,
        "dimensions_inches": [24, 36],
        "artwork_basis": "2024_REMASTER_OF_BOB_PEAK_ARTWORK",
        "source_assertion": assertion,
        "rights_status": "NO_PUBLIC_DIGITAL_REUSE_GRANT_VERIFIED",
        "eligible_for_thumbnail": False,
    }


EXPECTED_VARIANTS = {
    "vice-press-trek-iv-2024-timed": expected_variant(
        "vice-press-trek-iv-2024-timed", "vp-trek-iv-2024-timed-announcement", None,
        "TIMED_REGULAR_EDITION", "Timed Edition; 24x36 inches", None,
        "VICE_PRESS_LISTS_TIMED_POSTER_EDITION"),
    "vice-press-trek-iv-2024-foil": expected_variant(
        "vice-press-trek-iv-2024-foil", "vp-trek-iv-2024-foil-announcement",
        "https://vice-press.com/products/star-trek-iv-the-voyage-home-foil-variant-poster-bob-peak",
        "FOIL_VARIANT", "Foil Variant; edition of 200; 24x36 inches", 200,
        "VICE_PRESS_LISTS_LIMITED_FOIL_POSTER_EDITION"),
    "vice-press-trek-iv-2024-japanese": expected_variant(
        "vice-press-trek-iv-2024-japanese", "vp-trek-iv-2024-japanese-announcement",
        "https://vice-press.com/products/star-trek-iv-the-voyage-home-japanese-title-variant-poster-bob-peak",
        "JAPANESE_TEXT_SUPER_VARIANT", "Japanese Super Variant; edition of 150; 24x36 inches", 150,
        "VICE_PRESS_LISTS_JAPANESE_TEXT_POSTER_VARIANT"),
}


def require(condition: bool, error: str) -> None:
    if not condition:
        raise ValueError(error)


def exact_keys(obj, allowed: set[str], context: str):
    require(type(obj) is dict and set(obj) == allowed, f"{context}: missing/extra field")


def validate(packet: dict, discovery: dict) -> int:
    exact_keys(packet, {
        "proposal_id", "role", "proposal_only", "accepted_main_at_start", "observed_on_utc",
        "coverage_effect", "accepted_source_work_binding_effect", "artwork_release_effect",
        "media_bytes_fetched", "raw_source_snapshot_sha256", "source_family",
        "source_lineage_note", "producer_announcement", "studio_partner_announcement",
        "candidate_film_ref", "source_attributed_creator_chain", "variants",
    }, "packet")
    for key, fixed in {
        "proposal_id": "FILMS-TREK-IV-VICE-PRESS-VARIANTS-20261103",
        "role": "FILMS", "proposal_only": True,
        "accepted_main_at_start": ACCEPTED_MAIN,
        "observed_on_utc": "2026-11-03",
        "coverage_effect": "NONE", "accepted_source_work_binding_effect": "NONE",
        "artwork_release_effect": "NONE", "media_bytes_fetched": False,
        "raw_source_snapshot_sha256": None,
        "source_family": "publisher:vice-press.com",
        "producer_announcement": ANNOUNCEMENT,
        "studio_partner_announcement": PARTNER_GUIDE,
        "candidate_film_ref": "film-voyage-home",
    }.items():
        require(type(packet[key]) is type(fixed) and packet[key] == fixed, f"invalid {key}")
    note = packet["source_lineage_note"]
    require(type(note) is str and len(note) <= 240, "lineage note too long")
    require(note == LINEAGE_NOTE, "source lineage claim was altered")
    exact_keys(packet["source_attributed_creator_chain"], set(CREATORS), "creator chain")
    require(packet["source_attributed_creator_chain"] == CREATORS, "creator chain not supported by producer source")
    require(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "missing discovery baseline")
    known = {film["id"] for film in discovery["films"]}
    require(packet["candidate_film_ref"] in known, "unknown candidate film")

    items = packet["variants"]
    require(type(items) is list and len(items) == 3, "expected three source-local variants")
    seen = set()
    for i, item in enumerate(items):
        exact_keys(item, VARIANT_KEYS, f"variant {i}")
        local_id = item["local_entity_id"]
        require(type(local_id) is str and local_id in EXPECTED_VARIANTS, f"variant {i}: unknown local entity")
        require(local_id not in seen, f"variant {i}: duplicate local entity")
        seen.add(local_id)
        require(item == EXPECTED_VARIANTS[local_id], f"variant {i}: source-relative evidence/edition/rights mismatch")
    require(seen == set(EXPECTED_VARIANTS), "omitted reviewed variant")
    return len(items)


def main() -> None:
    packet = json.loads(RECORDS.read_text(encoding="utf-8"))
    discovery = json.loads(FILM_DISCOVERY.read_text(encoding="utf-8"))
    print(f"PASS: {validate(packet, discovery)} Vice Press variant claims; no artwork release or film coverage")


if __name__ == "__main__":
    main()
