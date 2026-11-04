#!/usr/bin/env python3
"""Validate a frozen S.C.E. #34 HELD private-source reading receipt (never public prose)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).with_name("records.json")
OWNER_OPF = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OWNER_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
FROZEN_CANONICAL_SHA = "997263dc75fecc5ccacc5c6e518f1114d7dbfccb30200bc9c0c321c71c39ddfb"
EXPECTED_SPANS = (
    (6413, 17685, "c000e263fa41bea8a439d69794e81960787de2a1932f8165e697334e958f5df4"),
    (17685, 36826, "3855bbaf7c9fd0b9cf1cf429e16fa5061cc33d471b5d483a10a8dd1e9c18a63c"),
    (36826, 57912, "6af0b83d7b316e9115e8bc194860459092b58c675e91846982477b0be26031db"),
    (57912, 69108, "1098e026c07bbdc05ba20d330842935c2c5b2cf7330571247ef438d6886f3452"),
    (69108, 80802, "4a2a6136168fc95f8492e53ce0e621b25c2c1831d4d7c11bc86a0e7f52e75fb6"),
    (80802, 103622, "61ee3a3663e501bbd5a4ac1a0d385f6dde273b4fdb3845dedf5f494eca129b74"),
    (103622, 113016, "c5eac07db5931ac85b4715dfff831cbc43664d20a89d580c2ef05959bcbf6014"),
)
KINDS = (
    "CHARACTER_LOG_RECONSTRUCTION", "CHARACTER_DIALOGUE_AND_ACTION",
    "NARRATOR_CHARACTER_INTERIORITY", "TEAM_MODEL_OF_MEASUREMENTS",
    "IN_STORY_CREW_HYPOTHESIS", "IN_STORY_COMPUTER_DIRECTIVE_REPORT",
    "IN_STORY_SENSOR_AND_SCENE", "IN_STORY_SENSOR_LIMIT",
    "NARRATED_ACTION_WITH_CHARACTER_REPORT", "CREW_REPORT_AND_UNRESOLVED_HULL",
)
STATUSES = (
    "SUPPORTED_IN_STORY_NOT_INDEPENDENTLY_VERIFIED", "REPORTED_FROM_IN_STORY_CODE",
    "CREW_MODEL_NOT_INDEPENDENTLY_VERIFIED", "CREW_REPORTED_ACTION", "UNRESOLVED",
)


def fail(reason: str) -> None:
    raise ValueError(reason)


def bounded_text(value: object, maximum: int) -> bool:
    return type(value) is str and 0 < len(value) <= maximum and value == value.strip() and \
        all(ord(char) >= 32 for char in value)


def validate(doc: object) -> tuple[int, int, int, int, int]:
    if not isinstance(doc, dict) or set(doc) != {
        "schema_version", "proposal_id", "baseline_accepted_main", "status", "accepted_work_effect",
        "accepted_source_binding_effect", "accepted_evidence_effect", "accepted_close_read_effect",
        "coverage_effect", "public_explorer_effect", "cross_work_reconciliation_effect",
        "copyrighted_book_text_exported", "private_source_manifestation_authenticated", "source", "publisher",
        "work_candidate", "chapter_spans", "local_entities", "evidence", "assertions",
    }:
        fail("Unexpected root field or HELD-rights boundary")
    if doc["schema_version"] != "trek-sce34-private-source-complete-read-held-v1" or \
       doc["proposal_id"] != "SCE34-OWNER-PRIVATE-SOURCE-20261104" or \
       doc["baseline_accepted_main"] != "3028765359001b90bc3e6b5c1835ee283b326e91" or \
       doc["status"] != "HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED":
        fail("Status or historical accepted baseline changed")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                   "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
                   "cross_work_reconciliation_effect"):
        if doc[effect] != "NONE":
            fail("Protected effect promoted: " + effect)
    if doc["copyrighted_book_text_exported"] is not False or \
       doc["private_source_manifestation_authenticated"] is not False:
        fail("Rights/export claim changed")
    src, pub, work = (doc[k] for k in ("source", "publisher", "work_candidate"))
    if not all(isinstance(v, dict) for v in (src, pub, work)):
        fail("Source, publisher or Work local candidate missing")
    if hashlib.sha256(OWNER_OPF.read_bytes()).hexdigest() != OWNER_SHA:
        fail("Owner OPF inventory receipts changed")
    inventory = json.loads(OWNER_OPF.read_text(encoding="utf-8"))
    row = next((r for r in inventory["rows"] if r.get("source_local_id") == "opf-local:0045"), None)
    if row is None or row.get("opf_entry_sha256") != src.get("opf_sha256") or \
       row.get("title") != ["Collective Hindsight Book 2"] or \
       row.get("creator") != ["Aaron Rosenberg"] or row.get("isbn_checksum_valid") != []:
        fail("Owner OPF receipt omitted or falsely corrected")
    expected_source = {
        "source_local_id": "source-local:owner-archive-sce34-20261104",
        "source_kind": "OWNER_LOCAL_CONVERTED_OPF_AND_HTML",
        "archive_basename": "Star_Trek_OPF_Converted.zip",
        "archive_length_bytes": 95673655,
        "archive_sha256": "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f",
        "conversion_manifest_basename": "conversion_manifest.json",
        "conversion_manifest_sha256": "7b83b960729b3a51f2d2e026a543860f30dbd4183e7958c52a068935a9a65782",
        "conversion_input_lit_basename": "STAR TREK - SCE - 34 - Collective Hindsight Bk 2.lit",
        "conversion_reported_status": "success", "conversion_reported_drm_label": 1,
        "conversion_reported_exit_code": 0, "conversion_reported_output_file_count": 12,
        "conversion_link_independently_reproduced": False,
        "original_lit_zip_basename": "ST ebooks.zip",
        "original_lit_zip_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
        "original_lit_member": "ST ebooks/STAR TREK - SCE - 34 - Collective Hindsight Bk 2.lit",
        "original_lit_member_length_bytes": 236948,
        "original_lit_member_sha256": "d86f0743b2582b5ba4227c349504b0843b0b3a1af70835c335e2ea3fc174c956",
        "opf_entry": "opf_books/STAR TREK - SCE - 34 - Collective Hindsight Bk 2/STAR TREK - SCE - 34 - Collective Hindsight Bk 2.opf",
        "opf_length_bytes": 4222,
        "opf_sha256": "ca025b2d11a8982524e89a97e1e454340ae639c1b6a38f4f1eebbb09b07e2706",
        "html_entry": "opf_books/STAR TREK - SCE - 34 - Collective Hindsight Bk 2/CollectiveHindsightBook2.html",
        "html_length_bytes": 115388,
        "html_sha256": "fcc08e791e209bd2c90d36fea30f1820137ca753b1f3a1ff9eb0ea82683ed3bd",
        "toc_entry": "opf_books/STAR TREK - SCE - 34 - Collective Hindsight Bk 2/contents.html",
        "toc_length_bytes": 1401,
        "toc_sha256": "63739a129851c7d736d4c09c2f1d1efca917b517fe9bf8bc8c11fd8f537d21fa",
        "opf_inventory_id": "opf-local:0045",
        "opf_inventory_entry_sha256": "ca025b2d11a8982524e89a97e1e454340ae639c1b6a38f4f1eebbb09b07e2706",
        "opf_inventory_isbn_checksum_valid": [],
        "raw_opf_isbn10_literal": "0-7434-8084-8",
        "raw_opf_isbn10_checksum_conversion": "9780743480840",
        "opf_isbn_parser_anomaly": "INVENTORY_MISSED_DECORATED_ISBN10_LITERAL",
        "publisher_edition_crosswalk_state": "ISBN_CHECKSUM_ALIGNMENT_ONLY",
        "ebook_access_rights_verified_for_public_ingestion": False,
        "private_in_memory_source_read_utc": "2026-11-04",
        "opf_spine_html_entries": 1, "opf_chaptertour_entries": 7,
        "html_narrative_chapter_anchors": 7, "book_two_narrative_end_marker_byte": 113016,
        "following_book_three_teaser_read_as_source": False,
    }
    if src != expected_source:
        fail("Owner source bytes, conversion ancestry or scope changed")
    if pub != {
        "publisher_family": "publisher:simonandschuster.com",
        "page": "https://www.simonandschuster.com/books/Star-Trek-Collective-Hindsight-Book-2/Aaron-Rosenberg/Star-Trek-Starfleet-Corps-of-Engineers/9780743480840",
        "title": "Star Trek: Collective Hindsight Book 2", "series": "Star Trek: Starfleet Corps of Engineers",
        "series_number": 34, "creator": "Aaron Rosenberg", "edition_format": "EBOOK",
        "isbn13": "9780743480840", "publisher_date_us": "2003-11-17", "extent_pages": 79,
        "page_read_utc": "2026-11-04", "page_snapshot_captured": False,
    }:
        fail("First-party publisher listing changed")
    if set(work) != {"local_work_id", "source_local_id", "owner_opf_title", "author",
                     "source_bound_local_candidate", "source_read_scope", "full_private_source_read_done",
                     "global_work_identity_resolved", "accepted_work_coverage", "original_synopsis"} or \
       work["local_work_id"] != "work-local:sce34-collective-hindsight-book-two" or \
       work["source_local_id"] != src["source_local_id"] or \
       work["owner_opf_title"] != "Collective Hindsight Book 2" or \
       work["author"] != "Aaron Rosenberg" or work["source_bound_local_candidate"] is not True or \
       work["source_read_scope"] != "ALL_SEVEN_NARRATIVE_CHAPTERS_THROUGH_END_MARKER_OF_BOOK_TWO" or \
       work["full_private_source_read_done"] is not True or \
       work["global_work_identity_resolved"] is not False or work["accepted_work_coverage"] != "NONE" or \
       not bounded_text(work["original_synopsis"], 1100):
        fail("Local Work source and identity boundary changed")
    spans = doc["chapter_spans"]
    if not isinstance(spans, list) or len(spans) != 7:
        fail("Expected seven completely read narrative chapters")
    for i, (span, (a, b, sha)) in enumerate(zip(spans, EXPECTED_SPANS), 1):
        if not isinstance(span, dict) or set(span) != {
            "number", "locator", "byte_start_inclusive", "byte_end_exclusive", "raw_span_sha256",
            "original_summary"} or type(span["number"]) is not int or span["number"] != i or \
           span["locator"] != f"CollectiveHindsightBook2.html#ch_{i}" or \
           type(span["byte_start_inclusive"]) is not int or span["byte_start_inclusive"] != a or \
           type(span["byte_end_exclusive"]) is not int or span["byte_end_exclusive"] != b or \
           span["raw_span_sha256"] != sha or not bounded_text(span["original_summary"], 320):
            fail(f"Source chapter {i} span/locator/analysis invalid")
    entities = doc["local_entities"]
    if not isinstance(entities, list) or len(entities) != 8 or \
       len(set(e.get("id") for e in entities if isinstance(e, dict))) != 8 or \
       not all(isinstance(e, dict) and set(e) == {"id", "kind", "label", "identity_scope"} and
               e["id"].startswith("sce34:") and e["identity_scope"] == "THIS_SOURCE_ONLY" and
               e["kind"] in {"PERSON", "VESSEL", "PLACE"} and
               bounded_text(e["label"], 70) for e in entities):
        fail("Local entity identity/shape invalid")
    evidence = doc["evidence"]
    if not isinstance(evidence, list) or len(evidence) != 10 or \
       [e.get("id") for e in evidence if isinstance(e, dict)] != [f"sce34:e{i:02d}" for i in range(1, 11)]:
        fail("Expected ten source-relative evidence observations")
    for i, (e, expected_kind) in enumerate(zip(evidence, KINDS), 1):
        if not isinstance(e, dict) or set(e) != {"id", "chapter", "locator", "kind", "observation"} or \
           type(e["chapter"]) is not int or e["chapter"] not in range(1, 8) or \
           e["locator"] != f'CollectiveHindsightBook2.html#ch_{e["chapter"]}' or \
           e["kind"] != expected_kind or not bounded_text(e["observation"], 320):
            fail(f"Evidence observation {i} kind/scope invalid")
    assertions = doc["assertions"]
    if not isinstance(assertions, list) or len(assertions) != 5:
        fail("Five explicitly typed tentative assertions expected")
    ids = {e["id"] for e in evidence}
    for i, (a, status) in enumerate(zip(assertions, STATUSES), 1):
        if not isinstance(a, dict) or set(a) != {"id", "subject", "predicate", "value",
                                                    "evidence_refs", "status"} or \
           a["id"] != f"sce34:a{i:02d}" or a["subject"] != "sce34:vessel:dancing-star" or \
           a["status"] != status or not isinstance(a["evidence_refs"], list) or \
           not a["evidence_refs"] or not set(a["evidence_refs"]) <= ids or \
           not bounded_text(a["value"], 170):
            fail(f"Assertion {i} source/semantics invalid")
    canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != FROZEN_CANONICAL_SHA:
        fail("Frozen source analysis changed; explicit review required")
    return (1, 1, len(entities), len(evidence), len(spans))


if __name__ == "__main__":
    print("HELD_SCE34_SOURCE_READ_OK", validate(json.loads(DATA.read_text(encoding="utf-8"))))
