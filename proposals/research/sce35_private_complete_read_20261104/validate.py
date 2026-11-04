#!/usr/bin/env python3
"""Validate immutable HELD S.C.E. #35 private-source research, with zero admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).with_name("records.json")
OWNER_OPF = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OWNER_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
FROZEN_CANONICAL_SHA = "9bec69db19015e8104ed7cd90199d96e96789f9114067c56d1961e635d9b0313"
EXPECTED_SPANS = (
    (6557, 13738, "7c6f4cac89bf4d5565ca0763f8b6078957e778979708ae24b5a0b6e3f862b394"),
    (13738, 24412, "7687eec2f225d1bb2b7cf955927891f9dda9f763dc7593c785a56e857f1868e1"),
    (24412, 35824, "6d103b98099c2b93a92b561161311e085abf9a0774424082109681e67c0a454a"),
    (35824, 45614, "148679e60b5988c7da90ed502cc17343c1c3ab81cf49b3d6297cbeb24d3abd05"),
    (45614, 62535, "7bdc8a3844beb86759a6596e84eaccf7f85301adc6943de7f99b18e16a88490d"),
    (62535, 76108, "eb409b38685a5132f24b701274fb9904dbc5e0c5b7e04a1b893bcef5031b9495"),
    (76108, 89601, "9fbbdc51b114277e90d59f6192615ba514bec9cc55d4aad360949fa8701a163c"),
    (89601, 95537, "85250302de14b78fb1cf83f1046ddc36910741affefe90b6c0332bab9ae9fc6c"),
    (95537, 109412, "c3b32ec26f686644666588a834786f543fcfda091edbc4f9bd43a761e1ebdf0d"),
    (109412, 118742, "5eb105d274c76b8199d1be934c27e45621edff1c7d2efd0f9180ff8c80b7a157"),
    (118742, 126100, "944d3a9c1cfc2f1944abada28d97be034f47190ed749d177fcfefe59a3465cca"),
    (126100, 134738, "2986d8ba985923714dfaee32b801fab91ece47d0a24227f4d2d1e88420058bac"),
    (134738, 142638, "c62f37a440eb3a2c8fa04da9ed16750af4e63e7f858f5bdb7d3db7d4ce9a7d73"),
    (142638, 156001, "687bc35b43d53136c689a71d4171a5a58d73ba2959c38a093fe84b5277bfc294"),
    (156001, 166726, "37a6a3c95ecf70d2ead6f6436bbac3006f12ba448ef5d0ccb3b751c8c84d0021"),
)
EVIDENCE_KINDS = (
    "CHARACTER_OBSERVATION_WITH_INTERPRETATION", "CREW_RECONSTRUCTION_OF_SIGNAL",
    "DREAM_AND_CHARACTER_ANXIETY", "CREW_INFERENCE_FROM_MEASUREMENTS",
    "PROBE_RELAY_WITH_SENSOR_LIMITS", "UNRESOLVED_PRIOR_VISITOR_AND_AWAY_TEAM",
    "CHARACTER_DIALOGUE_AND_ACTION", "EMPATHIC_REPORT_WITH_OBSERVED_ACTION",
    "CHARACTER_CLAIM_UNCORROBORATED", "CHARACTER_TESTIMONY_WITH_MATERIAL_GAPS",
    "CREW_MEASUREMENT_DISAGREES_WITH_TESTIMONY", "IN_STORY_TECHNICAL_INFERENCE",
    "CLIFFHANGER_UNRESOLVED_RESCUE",
)
ASSERTION_STATUSES = (
    "SUPPORTED_BY_RESIDENT_TESTIMONY", "CONTESTED_UNCORROBORATED_CLAIM",
    "SOURCE_REPORTED_MEASUREMENTS", "CONTESTED_PROVISIONAL_TIMING",
    "INFERENCE_BY_TEV_NOT_PROVEN", "UNRESOLVED",
)


def fail(message: str) -> None:
    raise ValueError(message)


def bounded_text(v: object, maximum: int) -> bool:
    return type(v) is str and 0 < len(v) <= maximum and v == v.strip() and all(ord(c) >= 32 for c in v)


def validate(doc: object) -> tuple[int, int, int, int, int]:
    if not isinstance(doc, dict) or set(doc) != {
        "schema_version", "proposal_id", "baseline_accepted_main", "status",
        "accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
        "accepted_close_read_effect", "coverage_effect", "public_explorer_effect",
        "cross_work_reconciliation_effect", "copyrighted_book_text_exported",
        "private_source_manifestation_authenticated", "source", "publisher", "work_candidate",
        "chapter_spans", "local_entities", "evidence", "assertions",
    }:
        fail("Invalid root shape or leakage of unapproved data")
    for k, expected in {
        "schema_version": "trek-sce35-private-source-complete-read-held-v1",
        "proposal_id": "SCE35-OWNER-PRIVATE-SOURCE-20261104",
        "baseline_accepted_main": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "status": "HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED",
        "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
        "accepted_evidence_effect": "NONE", "accepted_close_read_effect": "NONE",
        "coverage_effect": "NONE", "public_explorer_effect": "NONE",
        "cross_work_reconciliation_effect": "NONE", "copyrighted_book_text_exported": False,
        "private_source_manifestation_authenticated": False,
    }.items():
        if doc[k] != expected or (type(expected) is bool and type(doc[k]) is not bool):
            fail("Protected state falsified: " + k)
    src, pub, work = (doc.get(k) for k in ("source", "publisher", "work_candidate"))
    if not all(isinstance(x, dict) for x in (src, pub, work)):
        fail("Missing source/publisher/work")
    if hashlib.sha256(OWNER_OPF.read_bytes()).hexdigest() != OWNER_SHA:
        fail("Owner OPF inventory changed")
    owner = json.loads(OWNER_OPF.read_text(encoding="utf-8"))
    row = next((r for r in owner["rows"] if r.get("source_local_id") == "opf-local:0046"), None)
    if not row or row.get("opf_entry_sha256") != "d263edc0cc885417a73b27ebcd8057ebb26a956cb095d887f85d4ad5292f8eed" or \
       row.get("title") != ["The Demon Book 1"] or \
       row.get("creator") != ["Loren L. Coleman & Randall N. Bills"] or \
       row.get("isbn_checksum_valid") != []:
        fail("Owner OPF inventory receipt absent, altered, or silently repaired")
    expected_source = {
        "source_local_id": "source-local:owner-archive-sce35-20261104",
        "source_kind": "OWNER_LOCAL_CONVERTED_OPF_AND_HTML",
        "archive_basename": "Star_Trek_OPF_Converted.zip",
        "archive_length_bytes": 95673655,
        "archive_sha256": "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f",
        "conversion_manifest_basename": "conversion_manifest.json",
        "conversion_manifest_sha256": "7b83b960729b3a51f2d2e026a543860f30dbd4183e7958c52a068935a9a65782",
        "conversion_input_lit_basename": "STAR TREK - SCE - 35 - Demon Bk 1.lit",
        "conversion_reported_status": "success", "conversion_reported_drm_label": 1,
        "conversion_reported_exit_code": 0, "conversion_reported_output_file_count": 13,
        "conversion_link_independently_reproduced": False,
        "original_lit_zip_basename": "ST ebooks.zip",
        "original_lit_zip_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
        "original_lit_member": "ST ebooks/STAR TREK - SCE - 35 - Demon Bk 1.lit",
        "original_lit_member_length_bytes": 262020,
        "original_lit_member_sha256": "31c5149fa7bc5f9b99270c71df5accf72f2e7d5d89c73106f86b5a3b5f0275e6",
        "opf_entry": "opf_books/STAR TREK - SCE - 35 - Demon Bk 1/STAR TREK - SCE - 35 - Demon Bk 1.opf",
        "opf_length_bytes": 4581,
        "opf_sha256": "d263edc0cc885417a73b27ebcd8057ebb26a956cb095d887f85d4ad5292f8eed",
        "html_entry": "opf_books/STAR TREK - SCE - 35 - Demon Bk 1/DemonBook1,The.html",
        "html_length_bytes": 170638,
        "html_sha256": "66d6fb884b0374cfb98cd96d8d2b0eb9b375aeab82a8e7cc9341991d82abc0eb",
        "toc_entry": "opf_books/STAR TREK - SCE - 35 - Demon Bk 1/contents.html",
        "toc_length_bytes": 1893,
        "toc_sha256": "5b094a495890fa011697259fcc6ec8a3f803bfab6b27f502b0cf33a8f4eac6bc",
        "opf_inventory_id": "opf-local:0046",
        "opf_inventory_entry_sha256": "d263edc0cc885417a73b27ebcd8057ebb26a956cb095d887f85d4ad5292f8eed",
        "opf_inventory_isbn_checksum_valid": [],
        "raw_opf_work_isbn10_literal": "0-7434-7609-3",
        "raw_opf_converter_header_isbn10_literal": "0-9673008-1-9",
        "work_isbn13_checksum_conversion": "9780743476096",
        "opf_isbn_parser_anomaly": "INVENTORY_MISSED_DECORATED_ISBN10_AND_CONVERTER_HEADER_DISTINCT",
        "publisher_edition_crosswalk_state": "ISBN_CHECKSUM_ALIGNMENT_ONLY",
        "owner_opf_creator_display": "Loren L. Coleman & Randall N. Bills",
        "owner_opf_creator_primary_display": "Loren L. Coleman",
        "creator_crosswalk_state": "CREATOR_DISPLAY_VARIANT_UNRESOLVED",
        "ebook_access_rights_verified_for_public_ingestion": False,
        "private_in_memory_source_read_utc": "2026-11-04",
        "opf_spine_html_entries": 1, "opf_chaptertour_entries": 15,
        "html_narrative_chapter_anchors": 15,
        "book_one_continuation_marker_byte": 166726,
        "following_book_two_read_as_source": False,
    }
    if src != expected_source:
        fail("Private source provenance, boundaries or uncertain edition identity changed")
    if pub != {
        "publisher_family": "publisher:simonandschuster.com",
        "page": "https://www.simonandschuster.com/books/Star-Trek-The-Demon-Book-1/Loren-Coleman/Star-Trek-Starfleet-Corps-of-Engineers/9780743476096",
        "title": "Star Trek: The Demon Book 1", "series": "Star Trek: Starfleet Corps of Engineers",
        "series_number": 35, "creator_primary_display": "Loren Coleman",
        "creator_secondary_display": "Randall N. Bills", "edition_format": "EBOOK",
        "isbn13": "9780743476096", "publisher_date_us": "2003-12-15",
        "extent_pages": 125, "page_read_utc": "2026-11-04", "page_snapshot_captured": False,
    }:
        fail("Publisher edition metadata differs from first-party listing")
    if set(work) != {
        "local_work_id", "source_local_id", "owner_opf_title", "owner_opf_creator_display",
        "source_bound_local_candidate", "source_read_scope", "full_private_source_read_done",
        "global_work_identity_resolved", "accepted_work_coverage", "original_synopsis",
    } or work["local_work_id"] != "work-local:sce35-the-demon-book-one" or \
       work["source_local_id"] != src["source_local_id"] or \
       work["owner_opf_title"] != "The Demon Book 1" or \
       work["owner_opf_creator_display"] != src["owner_opf_creator_display"] or \
       work["source_bound_local_candidate"] is not True or \
       work["source_read_scope"] != "ALL_FIFTEEN_NARRATIVE_CHAPTERS_THROUGH_TO_BE_CONTINUED_MARKER" or \
       work["full_private_source_read_done"] is not True or \
       work["global_work_identity_resolved"] is not False or \
       work["accepted_work_coverage"] != "NONE" or not bounded_text(work["original_synopsis"], 1400):
        fail("Local work identity/read boundary or synopsis invalid")
    spans = doc["chapter_spans"]
    if not isinstance(spans, list) or len(spans) != 15:
        fail("Expected 15 read narrative chapter spans")
    for i, (span, (start, end, digest)) in enumerate(zip(spans, EXPECTED_SPANS), 1):
        if not isinstance(span, dict) or set(span) != {
            "number", "locator", "byte_start_inclusive", "byte_end_exclusive",
            "raw_span_sha256", "original_summary",
        } or type(span["number"]) is not int or span["number"] != i or \
           type(span["byte_start_inclusive"]) is not int or span["byte_start_inclusive"] != start or \
           type(span["byte_end_exclusive"]) is not int or span["byte_end_exclusive"] != end or \
           span["locator"] != f"DemonBook1,The.html#ch_{i}" or \
           span["raw_span_sha256"] != digest or not bounded_text(span["original_summary"], 340):
            fail(f"Read source chapter {i} span, locator or original analysis invalid")
    ents = doc["local_entities"]
    if not isinstance(ents, list) or len(ents) != 12 or \
       len({e.get("id") for e in ents if isinstance(e, dict)}) != 12 or not all(
           isinstance(e, dict) and set(e) == {"id", "kind", "label", "identity_scope"}
           and e["id"].startswith("sce35:") and e["kind"] in {"PERSON", "VESSEL", "PLACE"}
           and e["identity_scope"] == "THIS_SOURCE_ONLY" and bounded_text(e["label"], 80)
           for e in ents):
        fail("Local-only entity scope invalid")
    evidence = doc["evidence"]
    if not isinstance(evidence, list) or len(evidence) != 13 or \
       [e.get("id") for e in evidence if isinstance(e, dict)] != [f"sce35:e{i:02d}" for i in range(1, 14)]:
        fail("Expected 13 source-relative evidence observations")
    for i, (e, kind) in enumerate(zip(evidence, EVIDENCE_KINDS), 1):
        if not isinstance(e, dict) or set(e) != {"id", "chapter", "locator", "kind", "observation"} or \
           type(e["chapter"]) is not int or e["chapter"] not in range(1, 16) or \
           e["locator"] != f'DemonBook1,The.html#ch_{e["chapter"]}' or \
           e["kind"] != kind or not bounded_text(e["observation"], 360):
            fail(f"Evidence observation {i} invented, unbounded or misclassified")
    assertions = doc["assertions"]
    ids = {e["id"] for e in evidence}
    entity_ids = {e["id"] for e in ents}
    if not isinstance(assertions, list) or len(assertions) != 6:
        fail("Expected 6 tentative assertions")
    for i, (a, status) in enumerate(zip(assertions, ASSERTION_STATUSES), 1):
        if not isinstance(a, dict) or set(a) != {
            "id", "subject", "predicate", "value", "evidence_refs", "status",
        } or a["id"] != f"sce35:a{i:02d}" or a["subject"] not in entity_ids or \
           not bounded_text(a["predicate"], 72) or not bounded_text(a["value"], 220) or \
           not isinstance(a["evidence_refs"], list) or not a["evidence_refs"] or \
           len(a["evidence_refs"]) != len(set(a["evidence_refs"])) or \
           not set(a["evidence_refs"]) <= ids or a["status"] != status:
            fail(f"Tentative assertion {i} contradicts source evidence or epistemic class")
    canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != FROZEN_CANONICAL_SHA:
        fail("Frozen source record/analysis digest changed; independent review required")
    return (1, 1, len(ents), len(evidence), len(spans))


if __name__ == "__main__":
    print("HELD_SCE35_SOURCE_READ_OK", validate(json.loads(DATA.read_text(encoding="utf-8"))))
