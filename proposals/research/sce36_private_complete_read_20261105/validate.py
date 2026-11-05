"""Validate one HELD, owner-private S.C.E. #36 primary-source research packet.

The exact packet fingerprint makes any changed fact/evidence require a conscious
new review. It is not a proof of edition identity or an admission mechanism.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


DATA = Path(__file__).with_name("records.json")
EXPECTED_CANONICAL_SHA256 = "879ec7989a5b2f8ce0abbacd6605692a69cceb3534e69678e203852f3e332d67"
_HEX = re.compile(r"^[0-9a-f]{64}$")
_BARE_ANSWER_FIELDS = {"full_text", "raw_text", "text", "passage", "quote", "quote_text", "book_bytes"}


def _reject_if_embedded_prose(value: object) -> None:
    if isinstance(value, dict):
        if _BARE_ANSWER_FIELDS.intersection(value):
            raise ValueError("copyrighted full text/prose fields are forbidden")
        for item in value.values():
            _reject_if_embedded_prose(item)
    elif isinstance(value, list):
        for item in value:
            _reject_if_embedded_prose(item)


def _freeze(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def validate(packet: dict) -> tuple[int, int, int, int, int]:
    _reject_if_embedded_prose(packet)
    if packet.get("schema_version") != "trek-sce36-private-source-complete-read-held-v1":
        raise ValueError("schema version drift")
    if packet.get("baseline_accepted_main") != "3028765359001b90bc3e6b5c1835ee283b326e91":
        raise ValueError("unreviewed main baseline")
    if packet.get("status") != "HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED":
        raise ValueError("a HELD proposal cannot promote itself")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
                "cross_work_reconciliation_effect"):
        if packet.get(key) != "NONE":
            raise ValueError(f"protected effect not authorized: {key}")
    if packet.get("copyrighted_book_text_exported") is not False:
        raise ValueError("copyrighted novel text must never be in this packet")
    if packet.get("private_source_manifestation_authenticated") is not False:
        raise ValueError("conversion cannot authenticate a publisher edition")

    src, work, pub = packet["source"], packet["work_candidate"], packet["publisher"]
    if src["opf_inventory_id"] != "opf-local:0047" or src["opf_chaptertour_entries"] != 14:
        raise ValueError("wrong inventory source or chapter count")
    if src["html_narrative_chapter_anchors"] != 14 or src["novel_backmatter_start_byte"] != 166413:
        raise ValueError("narrative/backmatter boundary drift")
    if src["following_about_authors_and_promo_read_as_novel"] is not False:
        raise ValueError("backmatter is not another chapter")
    if src["conversion_link_independently_reproduced"] is not False:
        raise ValueError("unverified conversion silently promoted")
    if src["ebook_access_rights_verified_for_public_ingestion"] is not False:
        raise ValueError("owner possession does not convey public republication rights")
    for key in ("opf_sha256", "html_sha256", "toc_sha256", "original_lit_member_sha256",
                "archive_sha256", "original_lit_zip_sha256", "conversion_manifest_sha256"):
        if not _HEX.fullmatch(src[key]):
            raise ValueError(f"bad source digest: {key}")
    if src["raw_opf_work_isbn10_literal"] == src["raw_opf_converter_header_isbn10_literal"]:
        raise ValueError("converter ISBN header is not work ISBN")
    if src["creator_crosswalk_state"] != "CREATOR_DISPLAY_VARIANT_UNRESOLVED":
        raise ValueError("creator identity is not globally reconciled")
    if src["publisher_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
        raise ValueError("edition match cannot be silently authenticated")
    if pub["series_number"] != 36 or pub["isbn13"] != "9780743476102":
        raise ValueError("publisher candidate drift")
    if work["global_work_identity_resolved"] is not False or work["accepted_work_coverage"] != "NONE":
        raise ValueError("work identity/coverage admission prohibited")
    if work["full_private_source_read_done"] is not True:
        raise ValueError("incomplete read claim")
    if work["source_local_id"] != src["source_local_id"]:
        raise ValueError("local source/work link mismatched")

    chapters = packet["chapter_spans"]
    if len(chapters) != 14 or [x["number"] for x in chapters] != list(range(1, 15)):
        raise ValueError("non-sequential narrative chapters")
    if chapters[0]["byte_start_inclusive"] != 7427:
        raise ValueError("wrong first chapter boundary")
    if chapters[-1]["byte_end_exclusive"] != src["novel_backmatter_start_byte"]:
        raise ValueError("chapter read spills into promotional backmatter")
    for i, ch in enumerate(chapters):
        if ch["locator"] != f"DemonBook2,The.html#ch_{i+1}":
            raise ValueError("chapter source locator mismatch")
        if not _HEX.fullmatch(ch["raw_span_sha256"]):
            raise ValueError("invalid chapter raw-span hash")
        if not 40 <= len(ch["original_summary"]) <= 450:
            raise ValueError("missing or implausible original chapter coding")
        if ch["byte_start_inclusive"] >= ch["byte_end_exclusive"]:
            raise ValueError("empty or reversed source span")
        if i and chapters[i-1]["byte_end_exclusive"] != ch["byte_start_inclusive"]:
            raise ValueError("unindexed narrative gap or overlap")

    entities, evidence, assertions = packet["local_entities"], packet["evidence"], packet["assertions"]
    entity_ids = [x["id"] for x in entities]
    if len(set(entity_ids)) != len(entity_ids) or any(x["identity_scope"] != "THIS_SOURCE_ONLY" for x in entities):
        raise ValueError("entity ids nonlocal, duplicated or reconciled")
    evidence_ids = [e["id"] for e in evidence]
    if len(evidence) != 14 or len(set(evidence_ids)) != 14:
        raise ValueError("requires exactly 14 independent chapter-local observations")
    for index, item in enumerate(evidence):
        if (item["chapter"] != index + 1 or item["locator"] != chapters[index]["locator"]
                or item["id"] != f"sce36:e{index+1:02d}"):
            raise ValueError("evidence not source-locator aligned")
        if len(item["observation"]) < 60:
            raise ValueError("source observation too vague")
    assertion_ids = [x["id"] for x in assertions]
    if len(set(assertion_ids)) != len(assertion_ids):
        raise ValueError("duplicate assertions")
    for a in assertions:
        if a["subject"] not in entity_ids or not a["evidence_refs"]:
            raise ValueError("assertion has unbound local subject or absent evidence")
        if any(ref not in evidence_ids for ref in a["evidence_refs"]):
            raise ValueError("assertion references foreign/missing evidence")
        if not a.get("status"):
            raise ValueError("assertion lacks epistemic classification")
    if _freeze(packet) != EXPECTED_CANONICAL_SHA256:
        raise ValueError("the reviewed packet fingerprint changed: require independent review")
    return (1, 1, len(entities), len(evidence), len(chapters))


if __name__ == "__main__":
    result = validate(json.loads(DATA.read_text(encoding="utf-8")))
    print("SCE36 held private source-bound packet VALID:", result,
          "(source, local work candidate, entities, evidence, narrative chapters); accepted effects zero")
