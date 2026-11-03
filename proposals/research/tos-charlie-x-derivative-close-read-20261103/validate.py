"""Validate the proposal-only Charlie X evidence batch without source bytes.

The batch-specific pins reject changed source identities, not source forgery or
independent audiovisual authenticity; source custody remains a separate gate.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ID = "tvmeg-tos-charlie-x-20261103"
WORK_ID = "tos-charlie-x-candidate-20261103"
MANIFEST_IDENTITY = {
    "batch_id": "tos-charlie-x-derivative-close-read-20261103",
    "role": "TOS_AUDIOVISUAL_WORKER",
    "base_accepted_main": "d4ecd970bf28019696abd692011007d7d47f9ff8",
    "captured_at_utc_date": "2026-11-03",
}
UPSTREAM_SELF_REPORT = {
    "raw_html_physical_line": 885,
    "attributed_upstream_url": "http://www.chakoteya.net/",
    "statement_paraphrase": "TVMEG reports that transcripts were taken from and modified from Chrissie's Transcripts Site.",
    "attribution_is_independently_verified": False,
    "this_episode_upstream_match_verified": False,
    "independent_transcript_corroboration_count": 0,
}
SOURCE_IDENTITY = {
    "source_local_id": SOURCE_ID,
    "url": "https://tvmeg.com/index.php/2023/08/07/charliextrans/",
    "source_kind": "THIRD_PARTY_DERIVATIVE_TRANSCRIPT_PAGE",
    "source_lineage_class": "SOURCE_SELF_REPORTED_UNVERIFIED_DERIVATION",
    "retrieval": "HTTP_200_AND_COMPLETE_AVAILABLE_CANDIDATE_DIALOGUE_BODY_PROCESSED",
    "private_source_custody": "TEMPORARY_LOCAL_ONLY_NO_DURABLE_AUTHENTICATED_ARTIFACT",
    "raw_html_bytes": 144687,
    "raw_html_sha256": "4498f2ac33c4e1aa4c48123aab84254b890fb9dd8603f0540189d7abdcd3c616",
    "raw_html_physical_lines": 2016,
    "raw_html_candidate_dialogue_physical_lines_inclusive": [499, 870],
    "rendered_text_bytes": 27813,
    "rendered_text_sha256": "0e033f6883644602b7a941619f4f895e3780feffdc92e2a3a20f0e295721e849",
    "rendered_text_numbered_lines": 833,
    "derivation": "sed -n '499,870p' raw.html | pandoc 3.1.3 -f html -t plain --wrap=auto --columns=96",
    "complete_rendered_text_read_windows_inclusive": [
        [1, 150], [151, 300], [301, 450], [451, 600], [601, 750], [751, 833]
    ],
}
WORK_IDENTITY = {
    "candidate_id": WORK_ID,
    "candidate_title": "Charlie X",
    "official_publisher_title": 'Charlie "X"',
    "series": "Star Trek: The Original Series",
    "official_publisher_listing_url": "https://www.paramountplus.com/shows/star_trek/episodes/1/",
    "official_publisher_episode_page": "https://www.paramountplus.com/shows/video/804598975/",
    "official_publisher_rendered_heading": 'S1 E3: Charlie "X"',
    "official_publisher_raw_html_hash_available": False,
    "derivative_site_image_caption_ordinal": "Season 1, episode 2",
}
MANIFEST_FIELDS = set(MANIFEST_IDENTITY) | {
    "admission", "status", "source", "work", "records", "files_sha256", "next_frontier",
}
SOURCE_FIELDS = set(SOURCE_IDENTITY) | {
    "upstream_self_report", "rights_to_republish_source_text",
    "authenticated_primary_av_or_studio_script", "public_transcript_text_included",
}
WORK_FIELDS = set(WORK_IDENTITY) | {"ordinal_conflict"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate():
    manifest = load("MANIFEST.json")
    entities = load("local_entities.json")
    evidence = load("evidence.json")
    assertions = load("assertions.json")

    require(set(manifest) == MANIFEST_FIELDS, "manifest schema/unknown acceptance effect")
    require(set(manifest["source"]) == SOURCE_FIELDS, "source schema/unknown authenticity")
    require(set(manifest["work"]) == WORK_FIELDS, "work schema/unknown identity")
    for field, expected in MANIFEST_IDENTITY.items():
        require(manifest[field] == expected, "manifest identity drift: " + field)
    require(manifest.get("admission") == "PROPOSAL_ONLY", "admission must remain proposed")
    require(manifest.get("status") == "COMPLETE_AVAILABLE_DERIVATIVE_READING_NOT_ADMITTED", "bad status")
    for field, expected in SOURCE_IDENTITY.items():
        require(manifest["source"][field] == expected, "source identity drift: " + field)
    require(manifest["source"]["upstream_self_report"] == UPSTREAM_SELF_REPORT,
            "upstream attribution cannot be promoted or silently changed")
    for field, expected in WORK_IDENTITY.items():
        require(manifest["work"][field] == expected, "work identity drift: " + field)
    require(manifest.get("source", {}).get("authenticated_primary_av_or_studio_script") is False,
            "derivative cannot claim primary AV authentication")
    require(manifest["source"].get("public_transcript_text_included") is False, "copyright source text not allowed")
    require(manifest["source"].get("rights_to_republish_source_text") == "UNVERIFIED", "rights were not cleared")
    require(manifest["source"]["upstream_self_report"]["independent_transcript_corroboration_count"] == 0,
            "unverified upstream cannot count as corroboration")
    require(manifest["work"]["ordinal_conflict"] == "PRESERVE_SOURCE_RELATIVE_DIFFERENCE_NO_CANONICAL_OVERRIDE",
            "ordinal difference must remain unresolved")
    for record in (entities, evidence, assertions):
        require(record.get("source_local_id") == SOURCE_ID, "source ID mismatch")
        require(record.get("work_local_id") == WORK_ID, "work ID mismatch")

    entity_list = entities["entities"]
    entity_ids = [e["id"] for e in entity_list]
    require(len(entity_ids) == len(set(entity_ids)), "duplicate local entity ID")
    require(entities["global_identity_edges_created"] == 0, "unexpected global identity edge")
    require(entities["canonical_status"] == "NOT_ADMITTED", "unexpected admission")

    evidence_list = evidence["evidence"]
    evidence_ids = [e["id"] for e in evidence_list]
    require(len(evidence_ids) == len(set(evidence_ids)), "duplicate evidence ID")
    require(evidence["eligible_candidate_body_lines"] == [1, 833], "rendered line bounds drift")
    for item in evidence_list:
        require(1 <= item["start_line"] <= item["end_line"] <= 833, "evidence out of bounds")
        require(set(item["local_entity_ids"]).issubset(entity_ids), "evidence has unknown local entity")
        require(item["observation"] and "http" not in item["observation"], "invalid observation")
    require(evidence["audiovisual_verified"] is False, "AV verification absent")
    require(evidence["copyright_text_republished"] is False, "transcript release prohibited")

    assertion_list = assertions["assertions"]
    assertion_ids = [a["id"] for a in assertion_list]
    require(len(assertion_ids) == len(set(assertion_ids)), "duplicate assertion ID")
    for item in assertion_list:
        require(item["status"] == "PROPOSED", "assertion unexpectedly accepted")
        require(item["proposed_projection_status"] in {"CONTESTED", "UNRESOLVED"}, "bad projection scope")
        require(item["predicate"] in {"CLAIMS", "DEPICTS"}, "ungoverned predicate")
        if item["subject_type"] == "LOCAL_ENTITY":
            require(item["subject"] in entity_ids, "unbound local assertion subject")
        else:
            require(item["subject_type"] == "WORK" and item["subject"] == WORK_ID,
                    "invalid work assertion subject")
        for field in ("evidence", "context_evidence_ids", "counter_evidence_ids"):
            require(set(item[field]).issubset(evidence_ids), "assertion references unknown evidence")
        require(item["evidence"] and item["falsifier"] and item["counter_evidence_search"],
                "unexamined assertion")
    require(assertions["accepted_assertions"] == 0 and assertions["projection_effect"] == "NONE",
            "unexpected canonical projection effect")

    expected = manifest["records"]
    require(expected == {
        "local_entities": len(entity_list),
        "source_relative_evidence": len(evidence_list),
        "proposed_assertions": len(assertion_list),
        "accepted_briefings": 0,
        "global_identity_reconciliations": 0,
        "coverage_events": 0,
    }, "manifest count or coverage mismatch")
    for filename, sha in manifest.get("files_sha256", {}).items():
        require(filename in {"RESEARCH_RECORD.md", "local_entities.json", "evidence.json", "assertions.json"},
                "unexpected hashed filename")
        require(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == sha,
                "proposal file digest mismatch: " + filename)
    require(set(manifest.get("files_sha256", {})) == {
        "RESEARCH_RECORD.md", "local_entities.json", "evidence.json", "assertions.json"},
        "required file digests missing")
    print(f"TOS_CHARLIE_X_DERIVATIVE_OK: {len(entity_list)} local entities, "
          f"{len(evidence_list)} source-relative evidence records, "
          f"{len(assertion_list)} proposed assertions, no accepted coverage")


if __name__ == "__main__":
    validate()
