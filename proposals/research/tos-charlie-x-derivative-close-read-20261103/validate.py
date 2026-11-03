"""Validate the proposal-only Charlie X evidence batch without source bytes."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_ID = "tvmeg-tos-charlie-x-20261103"
WORK_ID = "tos-charlie-x-candidate-20261103"


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

    require(manifest.get("admission") == "PROPOSAL_ONLY", "admission must remain proposed")
    require(manifest.get("status") == "COMPLETE_AVAILABLE_DERIVATIVE_READING_NOT_ADMITTED", "bad status")
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
