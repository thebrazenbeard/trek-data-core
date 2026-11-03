"""Fail-closed validation of one TNG derivative-transcript research proposal."""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SOURCE_ID = "tng-s02e09-springfield-transcript-20261103"
WORK_ID = "tng-the-measure-of-a-man-candidate-20261103"
SOURCE_SHA256 = "951bb1d5a4c3529213dcabb8addf9fbcdff76c819f96e96061e49d74f17bcebe"
ENTITY_KINDS = {
    "CHARACTER_OCCURRENCE",
    "CHARACTER_REFERENCE",
    "INSTITUTION_OCCURRENCE",
    "INSTITUTIONAL_PROCEEDING",
    "PROPOSED_PROCEDURE",
    "HYPOTHETICAL_GROUP",
    "GROUP_OCCURRENCE",
}
EVIDENCE_KINDS = {
    "DEPICTION_ACTION", "DIALOGUE_TESTIMONY", "LOG_RECORD", "LEGAL_RULING",
}


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def validate_bundle(data):
    require(isinstance(data, dict) and data.get("schema_version") == "1.0.0", "schema")
    require(data.get("role") == "TNG" and data.get("status") == "PROPOSAL_ONLY", "role/admission")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect",
                   "coverage_effect", "reconciliation_effect",
                   "public_artwork_release_effect"):
        require(data.get(effect) == "NONE", f"forbidden promotion: {effect}")
    require(set(data) == {
        "schema_version", "role", "status", "accepted_work_effect",
        "accepted_source_binding_effect", "coverage_effect",
        "reconciliation_effect", "public_artwork_release_effect",
        "selection", "source", "work", "local_entities", "evidence", "assertions",
    }, "unexpected root field")

    selection = data.get("selection")
    require(isinstance(selection, dict), "missing selection provenance")
    require(selection.get("method") == "PURPOSIVE_SOURCE_SAMPLE"
            and selection.get("selection_order") == "NON_SEQUENTIAL"
            and selection.get("sampling_frame") == "NOT_ESTABLISHED", "sampling claim")
    require(selection.get("selection_bias_risk") ==
            "TOPICAL_SALIENCE_AND_SOURCE_AVAILABILITY", "selection bias omitted")
    require(selection.get("corpus_level_prevalence_or_generalization_effect") == "NONE",
            "unearned corpus generalization")
    require(isinstance(selection.get("selection_rationale"), str)
            and "deliberately searched" in selection["selection_rationale"],
            "inadequate selection provenance")
    require(isinstance(selection.get("neutrality_boundary"), str)
            and "not make" in selection["neutrality_boundary"],
            "missing neutrality limitation")
    require(set(selection) == {
        "method", "selection_rationale", "selection_order", "sampling_frame",
        "selection_bias_risk", "neutrality_boundary",
        "corpus_level_prevalence_or_generalization_effect",
    }, "unexpected sampling field")

    source = data.get("source")
    require(isinstance(source, dict) and source.get("source_local_id") == SOURCE_ID, "source ID")
    require(source.get("type") == "DERIVATIVE_EPISODE_TRANSCRIPT_WEBPAGE", "source type")
    url = urlsplit(source.get("url", ""))
    require(url.scheme == "https" and url.hostname == "www.springfieldspringfield.co.uk"
            and not url.username and not url.password and not url.fragment, "source URL")
    require(url.path == "/view_episode_scripts.php" and
            "episode=s02e09" in url.query and
            "tv-show=star-trek-the-next-generation" in url.query, "episode locator")
    require(source.get("raw_html_bytes") == 54681
            and source.get("raw_html_sha256") == SOURCE_SHA256, "source receipt")
    require(re.fullmatch(r"[0-9a-f]{64}", source["raw_html_sha256"]) is not None,
            "bad source hash")
    require(source.get("normalized_body_lines") == 509, "source line bounds")
    require(isinstance(source.get("line_normalization"), str)
            and "<br>" in source["line_normalization"], "line transform")
    require(source.get("independence_group") ==
            "springfieldspringfield.co.uk:tng-s02e09", "source lineage")
    require(source.get("upstream_transcript_origin") == "UNKNOWN", "unverified origin")
    require(source.get("source_body_completely_processed") is True, "read scope")
    for key in ("audiovisual_episode_watched", "authenticated_studio_script_read",
                "source_text_committed"):
        require(source.get(key) is False, f"false media/source claim: {key}")
    require(source.get("republication_rights") == "NOT_ESTABLISHED", "copyright gate")
    require(set(source) == {
        "source_local_id", "type", "url", "retrieved_at_utc", "raw_html_bytes",
        "raw_html_sha256", "normalized_body_lines", "line_normalization",
        "independence_group", "upstream_transcript_origin",
        "source_body_completely_processed", "audiovisual_episode_watched",
        "authenticated_studio_script_read", "source_text_committed",
        "republication_rights",
    }, "unexpected source field")

    work = data.get("work")
    require(isinstance(work, dict) and work.get("work_local_id") == WORK_ID, "work ID")
    require(work.get("title") == "The Measure of a Man", "work title")
    require(work.get("series") == "Star Trek: The Next Generation", "series identity")
    publisher = urlsplit(work.get("publisher_listing_url", ""))
    require(publisher.scheme == "https" and publisher.hostname == "www.paramountplus.com"
            and publisher.path == "/shows/video/5peN9NEF4VR1htPxpN8nhNL_lQ6lhk_H/"
            and not publisher.username and not publisher.password, "publisher locator")
    require(work.get("publisher_listing") == "Season 2 Episode 9", "publisher slot")
    require(work.get("publisher_metadata_not_a_viewing_receipt") is True, "publisher admission")
    require(work.get("global_work_identity") == "UNRESOLVED", "global work admission")

    entities = data.get("local_entities")
    evidence = data.get("evidence")
    assertions = data.get("assertions")
    require(isinstance(entities, list) and len(entities) == 13, "local entity count")
    require(isinstance(evidence, list) and len(evidence) == 15, "evidence count")
    require(isinstance(assertions, list) and len(assertions) == 8, "assertion count")
    entity_ids = {e.get("id") for e in entities if isinstance(e, dict)}
    require(len(entity_ids) == len(entities), "duplicate entity ID")
    for entity in entities:
        require(entity.get("kind") in ENTITY_KINDS, "ungoverned local entity kind")
        require(entity.get("id", "").startswith("ent-") and entity.get("label"),
                "incomplete local entity")
        require(set(entity) == {"id", "kind", "label"}, "unreviewed entity field")

    evidence_ids = {e.get("id") for e in evidence if isinstance(e, dict)}
    require(len(evidence_ids) == len(evidence), "duplicate evidence ID")
    for record in evidence:
        require(record.get("kind") in EVIDENCE_KINDS
                and record.get("frame") == "DERIVATIVE_TRANSCRIPT", "evidence kind/frame")
        start, end = record.get("start_line"), record.get("end_line")
        require(isinstance(start, int) and not isinstance(start, bool)
                and isinstance(end, int) and not isinstance(end, bool)
                and 1 <= start <= end <= 509, "out-of-range evidence")
        refs = record.get("local_entity_ids")
        require(isinstance(refs, list) and refs and set(refs) <= entity_ids,
                "unknown local entity in evidence")
        observation = record.get("observation")
        require(isinstance(observation, str) and 20 <= len(observation) <= 400
                and "\n" not in observation and "<" not in observation,
                "invalid source-relative paraphrase")
        require(set(record) == {"id", "start_line", "end_line", "kind", "frame",
                                "local_entity_ids", "observation"}, "unknown evidence field")

    assertion_ids = {a.get("id") for a in assertions if isinstance(a, dict)}
    require(len(assertion_ids) == len(assertions), "duplicate assertion ID")
    for assertion in assertions:
        require(assertion.get("subject") in entity_ids, "unknown assertion subject")
        require(assertion.get("predicate") in {"CLAIMS", "DEPICTS"}, "ungoverned predicate")
        require(assertion.get("status") == "PROPOSED", "premature assertion admission")
        require(assertion.get("proposed_projection_status") in
                {"CONTESTED", "UNRESOLVED"}, "unsupported projection certainty")
        require(assertion.get("falsifier") and assertion.get("interpretation"),
                "missing falsifier or interpretation")
        for key in ("supporting_evidence_ids", "neutral_evidence_ids",
                    "counter_evidence_ids"):
            refs = assertion.get(key)
            require(isinstance(refs, list) and refs and set(refs) <= evidence_ids,
                    f"invalid {key}")
        require(set(assertion) == {
            "id", "subject", "predicate", "interpretation",
            "supporting_evidence_ids", "neutral_evidence_ids",
            "counter_evidence_ids", "status",
            "proposed_projection_status", "falsifier",
        }, "unknown assertion field")
    return {
        "local_entities": len(entities),
        "evidence": len(evidence),
        "assertions": len(assertions),
        "accepted_coverage_events": 0,
    }


def validate():
    data = json.loads((ROOT / "records.json").read_text(encoding="utf-8"))
    counts = validate_bundle(data)
    print(f"TNG_DERIVATIVE_PROPOSAL_OK: {counts}; no admission, projection or artwork release")


if __name__ == "__main__":
    validate()
