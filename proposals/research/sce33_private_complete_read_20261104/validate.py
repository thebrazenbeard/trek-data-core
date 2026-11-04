#!/usr/bin/env python3
"""Frozen HELD SCE #33 local source-relative reading receipt; no public prose."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).with_name("records.json")
OWNER_OPF = ROOT / "proposals/librarian/private-opf-metadata-20261103/observations.json"
OWNER_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
FROZEN_CANONICAL_SHA = "f3e482990cee663bf92eb4ee3ee4ec28d2e8bf127187b5b3b69a7265f08ae331"
EXPECTED_SPANS = (
    (6260, 27617, "c4cc3aa185613b2dd4f92ba8c68ef62410946a810e1a640da9a479a04f7db825"),
    (27617, 49287, "78573b26256ecbe83184d0be8cda8c8bf5aca9f208c6a454fbac0ff3d6542fd2"),
    (49287, 79754, "ad8519e9d0ad30b5f07067e8a033e7034343bd934f2fc895893e55e4ee264fc9"),
    (79754, 104608, "18d2f913084cf310eef33ffbda5dfc01535fc331fd4a509f7b5ae19eef12e2ec"),
    (104608, 111428, "394a21ccfba09a77ea5b06670d0db4d4fe8e37d98a1612b60622300c7072dab7"),
)
ALLOWED_STATUS = {
    "SUPPORTED_IN_STORY_NOT_INDEPENDENTLY_VERIFIED",
    "REPORTED_FROM_IN_STORY_LOG", "CHARACTER_INFERENCE", "UNRESOLVED",
}
ALLOWED_EVIDENCE_KINDS = {
    "CREW_REPORTED_IDENTIFICATION", "NARRATOR_CHARACTER_INTERIORITY", "CHARACTER_BRIEFING",
    "CHARACTER_REPORTED_COMPUTER_LOG", "INFERENCE_BY_CHARACTER",
    "NARRATED_SCENE_AND_IN_STORY_SENSOR_REPORT", "CHARACTER_ACTION_AND_DISPOSAL_PLAN",
    "NARRATOR_CHARACTER_RECONSTRUCTION",
}


def fail(reason: str) -> None:
    raise ValueError(reason)


def bounded_text(value: object, maximum: int) -> bool:
    return type(value) is str and 0 < len(value) <= maximum and value == value.strip() and \
        all(ord(char) >= 32 for char in value)


def validate(doc: object) -> tuple[int, int, int, int, int]:
    if not isinstance(doc, dict) or set(doc) != {
        "schema_version", "proposal_id", "baseline_accepted_main", "status", "accepted_work_effect",
        "accepted_source_binding_effect", "accepted_evidence_effect", "accepted_close_read_effect",
        "coverage_effect", "public_explorer_effect", "copyrighted_book_text_exported",
        "private_source_manifestation_authenticated", "source", "publisher", "work_candidate",
        "chapter_spans", "local_entities", "evidence", "assertions",
    }:
        fail("Unexpected fields or missing HELD boundaries")
    if doc["schema_version"] != "trek-sce33-private-source-complete-read-held-v1" or \
       doc["proposal_id"] != "SCE33-OWNER-PRIVATE-SOURCE-20261104" or \
       doc["baseline_accepted_main"] != "3028765359001b90bc3e6b5c1835ee283b326e91" or \
       doc["status"] != "HELD_PRIVATE_COMPLETE_READ_NOT_ACCEPTED":
        fail("Historical baseline or HELD-only scope changed")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect", "accepted_evidence_effect",
                   "accepted_close_read_effect", "coverage_effect", "public_explorer_effect"):
        if doc[effect] != "NONE":
            fail(f"Protected effect changed: {effect}")
    if doc["copyrighted_book_text_exported"] is not False or \
       doc["private_source_manifestation_authenticated"] is not False:
        fail("Unverified private rights/manifestation falsely promoted")
    source, publisher, work = (doc.get(k) for k in ("source", "publisher", "work_candidate"))
    if not all(isinstance(v, dict) for v in (source, publisher, work)):
        fail("Source/Work/publisher contract missing")
    if hashlib.sha256(OWNER_OPF.read_bytes()).hexdigest() != OWNER_SHA:
        fail("Owner OPF-only inventory changed; this requires re-review")
    inventory = json.loads(OWNER_OPF.read_text(encoding="utf-8"))
    row = next((r for r in inventory["rows"] if r.get("source_local_id") == "opf-local:0044"), None)
    if row is None or row.get("opf_entry_sha256") != source.get("opf_inventory_entry_sha256") or \
       row.get("title") != ["Collective Hindsight Book 1"] or \
       row.get("creator") != ["Aaron Rosenberg"] or row.get("isbn_checksum_valid") != []:
        fail("Original owner OPF receipt was overruled or mutated")
    if source["opf_inventory_id"] != "opf-local:0044" or \
       source["opf_sha256"] != row["opf_entry_sha256"] or \
       source["raw_opf_isbn10_literal"] != "0-7434-8083-X" or \
       source["raw_opf_isbn10_checksum_conversion"] != "9780743480833" or \
       source["opf_inventory_isbn_checksum_valid"] != [] or \
       source["publisher_edition_crosswalk_state"] != "ISBN_CHECKSUM_ALIGNMENT_ONLY":
        fail("Undocumented edition/ISBN identity correction")
    if source["archive_basename"] != "Star_Trek_OPF_Converted.zip" or \
       source["archive_length_bytes"] != 95673655 or \
       source["archive_sha256"] != "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f" or \
       source["opf_length_bytes"] != 4070 or \
       source["html_length_bytes"] != 113659 or \
       source["html_sha256"] != "59986296c2017c1c8adf656c603421649612e5c278df25ad808c16d78fb35059" or \
       source["toc_length_bytes"] != 1082 or \
       source["toc_sha256"] != "87cc9595247d2c71630644472f061a8c318b8b406c918562cd506c0934a8d572":
        fail("Host-read source byte fingerprint drift")
    if source["conversion_manifest_basename"] != "conversion_manifest.json" or \
       source["conversion_manifest_sha256"] != "7b83b960729b3a51f2d2e026a543860f30dbd4183e7958c52a068935a9a65782" or \
       source["conversion_input_lit_basename"] != "STAR TREK - SCE - 33 - Collective Hindsight Bk 1.lit" or \
       source["conversion_reported_status"] != "success" or \
       source["conversion_reported_drm_label"] != 1 or \
       source["conversion_reported_exit_code"] != 0 or \
       source["conversion_reported_output_file_count"] != 13 or \
       source["conversion_link_independently_reproduced"] is not False or \
       source["original_lit_zip_basename"] != "ST ebooks.zip" or \
       source["original_lit_zip_sha256"] != "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac" or \
       source["original_lit_member"] != "ST ebooks/STAR TREK - SCE - 33 - Collective Hindsight Bk 1.lit" or \
       source["original_lit_member_length_bytes"] != 238466 or \
       source["original_lit_member_sha256"] != "065140cfb0b10a2e3217734f14f1acf1689a3183a066ca9a4f05ff983dd2bb2b":
        fail("Original LIT conversion lineage or checksum receipt altered")
    prefix = "opf_books/STAR TREK - SCE - 33 - Collective Hindsight Bk 1/"
    if source["opf_entry"] != prefix + "STAR TREK - SCE - 33 - Collective Hindsight Bk 1.opf" or \
       source["html_entry"] != prefix + "CollectiveHindSightBook1.html" or \
       source["toc_entry"] != prefix + "contents.html":
        fail("Archive internal locator changed")
    if source["opf_spine_html_entries"] != 1 or source["opf_chaptertour_entries"] != 4 or \
       source["html_narrative_chapter_anchors"] != 5 or \
       source["book_one_narrative_end_marker_byte"] != 111428 or \
       source["chaptertour_anomaly"] != "OPF_TOUR_OMITS_PRESENT_HTML_CHAPTER_FIVE" or \
       source["continuation_book_two_read"] is not False or \
       source["ebook_access_rights_verified_for_public_ingestion"] is not False:
        fail("Owner source chapter structure or rights status promoted")
    if publisher != {
        "publisher_family": "publisher:simonandschuster.com",
        "page": "https://www.simonandschuster.com/books/Star-Trek-Collective-Hindsight-Book-1/Aaron-Rosenberg/Star-Trek-Starfleet-Corps-of-Engineers/9780743480833",
        "title": "Star Trek: Collective Hindsight Book 1",
        "series": "Star Trek: Starfleet Corps of Engineers",
        "series_number": 33, "creator": "Aaron Rosenberg", "edition_format": "EBOOK",
        "isbn13": "9780743480833", "publisher_date_us": "2003-10-27", "extent_pages": 75,
        "page_read_utc": "2026-11-04", "page_snapshot_captured": False,
    }:
        fail("First-party publisher edition facts changed")
    if set(work) != {"local_work_id", "source_local_id", "owner_opf_title", "author",
                     "source_bound_local_candidate", "source_read_scope", "full_private_source_read_done",
                     "global_work_identity_resolved", "accepted_work_coverage", "original_synopsis"} or \
       work["local_work_id"] != "work-local:sce33-collective-hindsight-book-one" or \
       work["source_local_id"] != source["source_local_id"] or \
       work["source_bound_local_candidate"] is not True or \
       work["source_read_scope"] != "ALL_FIVE_NARRATIVE_CHAPTERS_AND_END_MARKER_OF_BOOK_ONE" or \
       work["full_private_source_read_done"] is not True or \
       work["global_work_identity_resolved"] is not False or \
       work["accepted_work_coverage"] != "NONE" or not bounded_text(work["original_synopsis"], 900) or \
       "Salek inferred" not in work["original_synopsis"] or \
       "might have protected" not in work["original_synopsis"] or \
       "Salek learned" in work["original_synopsis"]:
        fail("Local source-to-Work candidate invalid")
    spans = doc["chapter_spans"]
    if not isinstance(spans, list) or len(spans) != 5:
        fail("Five source chapter scopes expected")
    for idx, (span, (start, end, sha)) in enumerate(zip(spans, EXPECTED_SPANS), 1):
        if set(span) != {"number", "locator", "byte_start_inclusive", "byte_end_exclusive",
                         "raw_span_sha256", "original_summary"} or \
           type(span["number"]) is not int or span["number"] != idx or \
           span["locator"] != f"CollectiveHindSightBook1.html#ch_{idx}" or \
           type(span["byte_start_inclusive"]) is not int or span["byte_start_inclusive"] != start or \
           type(span["byte_end_exclusive"]) is not int or span["byte_end_exclusive"] != end or \
           span["raw_span_sha256"] != sha or not bounded_text(span["original_summary"], 290):
            fail(f"Source-relative chapter span altered: {idx}")
    entities = doc["local_entities"]
    if not isinstance(entities, list) or len(entities) != 7 or \
       len(set(e.get("id") for e in entities if isinstance(e, dict))) != 7 or \
       not all(isinstance(e, dict) and set(e) == {"id", "kind", "label", "identity_scope"} and
               e["identity_scope"] == "THIS_SOURCE_ONLY" and e["kind"] in {"PERSON", "VESSEL", "PLACE"} and
               bounded_text(e["label"], 70) and bounded_text(e["id"], 80) for e in entities):
        fail("Entity IDs or local-only identity constraints invalid")
    evidence = doc["evidence"]
    if not isinstance(evidence, list) or len(evidence) != 8 or \
       len(set(e.get("id") for e in evidence if isinstance(e, dict))) != 8:
        fail("Expected exactly eight source-relative evidence records")
    for e in evidence:
        if not isinstance(e, dict) or set(e) != {"id", "chapter", "locator", "kind", "observation"} or \
           e["chapter"] not in range(1, 6) or e["locator"] != f'CollectiveHindSightBook1.html#ch_{e["chapter"]}' or \
           e["kind"] not in ALLOWED_EVIDENCE_KINDS or not bounded_text(e["observation"], 300):
            fail("Evidence scope/speaker-class/locator invalid")
    assertions = doc["assertions"]
    if not isinstance(assertions, list) or len(assertions) != 4:
        fail("Four bounded candidate assertions expected")
    eids = {e["id"] for e in evidence}
    for a in assertions:
        if not isinstance(a, dict) or set(a) != {"id", "subject", "predicate", "value", "evidence_refs", "status"} or \
           a["status"] not in ALLOWED_STATUS or a["subject"] != "sce33:vessel:dancing-star" or \
           not isinstance(a["evidence_refs"], list) or not a["evidence_refs"] or \
           not set(a["evidence_refs"]) <= eids or not bounded_text(a["value"], 160):
            fail("In-story assertions falsely reconciled or ungrounded")
    canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != FROZEN_CANONICAL_SHA:
        fail("Frozen original-source analysis, labels, or semantics changed without review")
    return (1, 1, len(entities), len(evidence), len(spans))


if __name__ == "__main__":
    print("HELD_SCE33_SOURCE_READ_OK", validate(json.loads(DATA.read_text(encoding="utf-8"))))
