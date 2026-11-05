"""Fail-closed validator for a HELD S.C.E. #38 owner-archive source gap.

This is a discovery result, intentionally *not* a literary close-read packet.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


DATA = Path(__file__).with_name("records.json")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_PROSE_KEYS = {"full_text", "raw_text", "source_text", "passage", "quote", "quote_text", "ebook_bytes", "book_bytes"}
_EFFECT_KEYS = (
    "accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
    "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
    "global_identity_effect", "cross_work_reconciliation_effect", "push_merge_deploy_effect",
)


def _reject_raw_source_content(value: object) -> None:
    if isinstance(value, dict):
        if _PROSE_KEYS & set(value):
            raise ValueError("raw copyrighted source fields must not be exported")
        for child in value.values():
            _reject_raw_source_content(child)
    elif isinstance(value, list):
        for child in value:
            _reject_raw_source_content(child)


def _canonical_digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(data: dict) -> tuple[int, int, int]:
    _reject_raw_source_content(data)
    if data.get("schema_version") != "trek-literature-owner-source-gap-held-v1":
        raise ValueError("unexpected schema")
    if data.get("baseline_accepted_main") != "3028765359001b90bc3e6b5c1835ee283b326e91":
        raise ValueError("unreviewed accepted main baseline")
    if data.get("status") != "HELD_SOURCE_ABSENT_NOT_CLOSE_READ":
        raise ValueError("unsupported source/coverage promotion")
    if data.get("research_role") != "LITERATURE" or data.get("scope") != "SCE_38_OWNER_PRIVATE_LOCAL_ARCHIVE_DISCOVERY_ONLY":
        raise ValueError("role or source scope mismatch")

    pub = data["public_metadata_candidate"]
    if (pub.get("title"), pub.get("creator_display_name"), pub.get("publisher_series_number"), pub.get("publisher_ebook_isbn13")) != (
        "Star Trek: Orphans", "Kevin Killiany", 38, "9780743480857"
    ):
        raise ValueError("incorrect official publisher bibliographic candidate")
    if pub.get("evidence_class") != "PUBLISHER_PUBLIC_METADATA_ONLY":
        raise ValueError("publisher metadata cannot be primary-text evidence")
    if pub.get("source_edition_identity_authenticated") is not False or pub.get("global_work_identity_resolved") is not False:
        raise ValueError("unjustified edition or global identity resolution")
    if pub.get("publisher_url") != (
        "https://www.simonandschuster.com/books/Star-Trek-Orphans/Kevin-Killiany/"
        "Star-Trek-Starfleet-Corps-of-Engineers/9780743480857"
    ):
        raise ValueError("different publisher source")

    scan = data["owner_archive_scan"]
    if scan.get("scan_kind") != "READ_ONLY_ZIP_MEMBER_LIST_AND_BOOKS_TREE_NAME_SEARCH":
        raise ValueError("owner search was not a complete source read")
    if scan.get("owner_root_label") != "OneDrive/Documents/Books":
        raise ValueError("searched wrong owner root")
    original, converted, tree = scan["original_lit_zip"], scan["converted_opf_zip"], scan["books_tree_name_search"]
    expected_archives = (
        (original, "ST ebooks.zip", "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac", 573, 40),
        (converted, "Star_Trek_OPF_Converted.zip", "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f", 3846, 40),
    )
    for item, name, digest, total, count in expected_archives:
        if item.get("basename") != name or item.get("zip_members_total") != total:
            raise ValueError("wrong ZIP inventory")
        if item.get("zip_sha256") != digest or not _HEX.fullmatch(item["zip_sha256"]):
            raise ValueError("wrong archive fingerprint")
        labeled_count = item.get("sce_labeled_lit_members", item.get("sce_labeled_opf_members"))
        if labeled_count != count or item.get("sce_distinct_numbered_labels") != 36:
            raise ValueError("S.C.E. numbered archive count drift")
        if item.get("highest_numbered_sce_label") != 37 or item.get("matched_sce38_or_orphans_member_names") != 0:
            raise ValueError("#38 claimed present without primary source")
    if original.get("lit_members_total") != 347 or original.get("sce_missing_numbers_in_1_through_37") != [10]:
        raise ValueError("original LIT inventory mismatch")
    if original.get("sce_duplicate_label_multiplicities") != {"1": 2, "5": 2, "9": 2, "13": 2}:
        raise ValueError("original LIT numbered duplicates mismatch")
    if tree != {
        "search_scope": "LOCALLY_SYNCED_BOOKS_TREE_ONLY", "max_depth": 5,
        "case_insensitive_name_substring": "orphans", "matched_names": 0,
    }:
        raise ValueError("unverified external filesystem or cloud-wide absence claim")
    if scan.get("source_absence_claim_scope") != "ABSENT_FROM_THE_TWO_VERIFIED_ZIPS_AND_THE_LOCAL_BOOKS_TREE_NAME_SEARCH_ONLY":
        raise ValueError("source absence scope expanded")

    lit = data["literary_processing"]
    for key in ("owner_private_full_source_found", "full_private_source_read_done", "source_local_work_created", "chapter_count_verified_from_full_text"):
        if lit.get(key) is not False:
            raise ValueError(f"source absence cannot support literary processing: {key}")
    for key in ("chapter_spans", "local_entities", "evidence", "assertions"):
        if lit.get(key) != []:
            raise ValueError(f"no source-level {key} without complete text")
    if lit.get("original_source_based_synopsis") is not None or lit.get("covered_literary_count_delta") != 0:
        raise ValueError("fabricated synopsis or coverage promotion")

    effects = data["effects"]
    if any(effects.get(key) != "NONE" for key in _EFFECT_KEYS):
        raise ValueError("protected effect not authorized")
    if effects.get("copyrighted_book_text_exported") is not False:
        raise ValueError("copyrighted novel text cannot be exported")
    if data["next_frontier"].get("blocked_on") != "OWNER_AUTHORIZED_COMPLETE_SCE38_PRIMARY_SOURCE":
        raise ValueError("missing full source must remain explicit blocker")

    # A frozen content fingerprint makes any unreviewed packet extension fail closed.
    if _canonical_digest(data) != EXPECTED_PACKET_CANONICAL_SHA256:
        raise ValueError("packet changed since review; requires deliberate new held version")
    return (2, 0, 0)


# Generated from the reviewed source-gap observations.json-like records.json snapshot.
EXPECTED_PACKET_CANONICAL_SHA256 = "52550a0c8080bb7c128c479f349db779702c3f6ff0a175db5f60e82fc20fa061"


if __name__ == "__main__":
    print("SCE38 HELD local owner-source gap VALID", validate(json.loads(DATA.read_text(encoding="utf-8"))), "; accepted effects zero")
