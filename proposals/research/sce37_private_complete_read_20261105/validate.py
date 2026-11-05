"""Strict HELD-only validator for an owner-private complete S.C.E. #37 close read."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


DATA = Path(__file__).with_name("records.json")
EXPECTED_CANONICAL_SHA256 = "74d9bb0b37261e303718c21025dbdf0d751d79fd9f2433e4cd9575dfee4dafe4"
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_COPYRIGHT_FIELDS = {"full_text", "raw_text", "passage", "quote", "quote_text", "ebook_bytes", "book_bytes"}


def _no_prose_fields(data: object) -> None:
    if isinstance(data, dict):
        if _COPYRIGHT_FIELDS.intersection(data):
            raise ValueError("cannot publish copyrighted source text in a held packet")
        for item in data.values():
            _no_prose_fields(item)
    elif isinstance(data, list):
        for item in data:
            _no_prose_fields(item)


def _snapshot_digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate(data: dict) -> tuple[int, int, int, int, int]:
    _no_prose_fields(data)
    if data.get("schema_version") != "trek-sce37-private-source-complete-read-held-v1":
        raise ValueError("unexpected packet schema")
    if data.get("baseline_accepted_main") != "3028765359001b90bc3e6b5c1835ee283b326e91":
        raise ValueError("unreviewed accepted-main baseline")
    if data.get("status") != "HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED":
        raise ValueError("source packet cannot admit itself")
    if data.get("copyrighted_book_text_exported") is not False:
        raise ValueError("copyrighted novel bytes cannot be exported")
    if data.get("private_source_manifestation_authenticated") is not False:
        raise ValueError("converter output is not a purchased-edition authentication")
    for key in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                "accepted_close_read_effect", "coverage_effect", "public_explorer_effect", "cross_work_reconciliation_effect"):
        if data.get(key) != "NONE":
            raise ValueError(f"protected effect is not allowed here: {key}")

    src, pub, work = data["source"], data["publisher"], data["work_candidate"]
    if src["opf_inventory_id"] != "opf-local:0048":
        raise ValueError("different owner-private literary source")
    if src["opf_chaptertour_entries"] != 10 or src["html_narrative_chapter_anchors"] != 10:
        raise ValueError("full-source narrative chapter count drift")
    if src["chapter_span_start_rule"] != "FIRST_BYTE_OF_FULL_DIV_CLASS_CHAPTER_ID_TAG":
        raise ValueError("chapter spans must start at full tags, not inner id tokens")
    if src["novel_about_author_start_byte"] != 197110:
        raise ValueError("author biography boundary drift")
    if src["following_author_biography_or_next_work_promo_read_as_novel"] is not False:
        raise ValueError("author biography/promo must be excluded")
    for key in ("archive_sha256", "conversion_manifest_sha256", "original_lit_zip_sha256",
                "original_lit_member_sha256", "opf_sha256", "html_sha256", "toc_sha256"):
        if not _HEX.fullmatch(src[key]):
            raise ValueError(f"invalid digest: {key}")
    if src["ebook_access_rights_verified_for_public_ingestion"] is not False or src["conversion_link_independently_reproduced"] is not False:
        raise ValueError("no public republication rights or independently reproduced conversion")
    if src["creator_crosswalk_state"] != "DISPLAY_NAME_ALIGNMENT_ONLY":
        raise ValueError("same display name is not proven identity")
    if src["publisher_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
        raise ValueError("publisher/source edition identity was not authenticated")
    if src["raw_opf_work_isbn10_literal"] == src["raw_opf_converter_header_isbn10_literal"]:
        raise ValueError("book ISBN must not be confused with converter header")
    if pub["series_number"] != 37 or pub["isbn13"] != "9780743476119":
        raise ValueError("wrong publisher candidate")
    if work["source_local_id"] != src["source_local_id"] or work["global_work_identity_resolved"] is not False:
        raise ValueError("work/source link or global identity overreach")
    if work["full_private_source_read_done"] is not True or work["accepted_work_coverage"] != "NONE":
        raise ValueError("source-close-read admission conflation")

    chapters = data["chapter_spans"]
    if len(chapters) != 10 or [x["number"] for x in chapters] != list(range(1, 11)):
        raise ValueError("ten ordered novel chapters required")
    if chapters[0]["byte_start_inclusive"] != 7250 or chapters[-1]["byte_end_exclusive"] != 197110:
        raise ValueError("narrative tag start or author-bio end boundary wrong")
    for index, ch in enumerate(chapters):
        if ch["locator"] != f"RingAroundtheSky.html#ch_{index+1}":
            raise ValueError("chapter locator mismatch")
        if not _HEX.fullmatch(ch["raw_span_sha256"]):
            raise ValueError("invalid exact raw-chapter digest")
        if ch["byte_start_inclusive"] >= ch["byte_end_exclusive"]:
            raise ValueError("empty or inverted raw chapter span")
        if index and chapters[index-1]["byte_end_exclusive"] != ch["byte_start_inclusive"]:
            raise ValueError("source bytes skipped, duplicated, or overlapping")
        if len(ch["original_summary"]) < 80 or len(ch["original_summary"]) > 500:
            raise ValueError("chapter coding missing or implausible")

    entities, evidence, assertions = data["local_entities"], data["evidence"], data["assertions"]
    ids = [e["id"] for e in entities]
    if len(ids) != len(set(ids)) or any(e["identity_scope"] != "THIS_SOURCE_ONLY" for e in entities):
        raise ValueError("global or duplicated entity identities")
    eids = [e["id"] for e in evidence]
    if len(evidence) != 10 or len(set(eids)) != 10:
        raise ValueError("one or more chapter-relative evidence missing")
    for index, e in enumerate(evidence):
        if e["chapter"] != index + 1 or e["id"] != f"sce37:e{index+1:02d}" or e["locator"] != chapters[index]["locator"]:
            raise ValueError("evidence is not chapter-bound")
        if len(e["observation"]) < 60:
            raise ValueError("evidence observation lacks supportable content")
    if len(set(a["id"] for a in assertions)) != len(assertions):
        raise ValueError("duplicate asserted relation")
    for a in assertions:
        if a["subject"] not in ids or not a["evidence_refs"]:
            raise ValueError("assertion lacks source-local subject or evidence")
        if any(ref not in eids for ref in a["evidence_refs"]):
            raise ValueError("foreign evidence ref")
        if not a.get("status"):
            raise ValueError("epistemic status absent")

    if _snapshot_digest(data) != EXPECTED_CANONICAL_SHA256:
        raise ValueError("source-relative packet changed; requires deliberate re-review")
    return (1, 1, len(entities), len(evidence), len(chapters))


if __name__ == "__main__":
    counts = validate(json.loads(DATA.read_text(encoding="utf-8")))
    print("SCE37 HELD private complete read VALID", counts, "; accepted effects zero")
