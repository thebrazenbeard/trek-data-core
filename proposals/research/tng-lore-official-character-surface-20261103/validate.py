"""Fail-closed validator for the bounded Lore official-source proposal packet."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

PACKET = Path(__file__).with_name("records.json")

EXPECTED_SOURCES = {
    "S1": "https://www.startrek.com/news/a-look-back-at-descent",
    "S2": "https://www.startrek.com/news/recap-star-trek-picard-307-dominion",
    "S3": "https://www.startrek.com/news/star-trek-megalomaniacal-ai-guide",
}

# Code-owned semantic pin for this immutable, source-reviewed candidate packet.
# A structural validator alone must not accept an adversarial rewrite of
# evidence observations, assertion predicates or artwork descriptions while
# retaining otherwise-valid source IDs and HELD publication flags.
EXPECTED_PACKET_CANONICAL_SHA256 = "c2ab94838d80d9507d307db66fb46f71b37831d99ae587e64433e7d9c12c61f2"


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def validate(payload: dict) -> None:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    actual_digest = hashlib.sha256(canonical).hexdigest()
    require(actual_digest == EXPECTED_PACKET_CANONICAL_SHA256, "source-local packet semantic/content digest mismatch")
    require(payload["role"] == "TNG_SOURCE_LOCAL_RESEARCH", "role must be source-local TNG")
    require(payload["status"] == "PROPOSAL_ONLY", "unadmitted work")
    require(payload["accepted_main_at_start"] == "aebf9e8a69ab44919f2d89ab60dd1e824e05a807", "source head drift")
    require(payload["method"] == "PURPOSIVE_USER_PROMPTED_SAMPLE_NOT_CORPUS_REPRESENTATIVE", "selection bias disclosure")
    require(payload["sampling_frame"] == "NOT_ESTABLISHED", "sampling frame")
    for key in ("source_text_complete", "audiovisual_works_watched", "authenticated_episode_scripts_read"):
        require(payload[key] is False, "unearned full-source coverage: " + key)
    require(payload["source_body_sha256"] is None, "invented source snapshot")
    for key in ("accepted_source_binding_effect", "accepted_work_identity_effect", "coverage_effect", "reconciliation_effect", "public_explorer_effect", "public_artwork_release_effect"):
        require(payload[key] == "NONE", "protected effect: " + key)

    sources = payload["sources"]
    require(len(sources) == 3, "three bounded first-party source reads")
    require({s["id"]: s["url"] for s in sources} == EXPECTED_SOURCES, "source identity drift")
    for source in sources:
        require(source["publisher_lineage"] == "STAR_TREK_PARAMOUNT", "source lineage")
        require(source["full_episode_source"] is False, "article is not an episode")
        require(source["type"].startswith("FIRST_PARTY_EDITORIAL"), "evidence type")

    missing = payload["inaccessible_candidate_sources"]
    require(len(missing) == 2, "Paramount source-attempt count")
    for candidate in missing:
        require(candidate["direct_open_result"] == "ERROR_500" and candidate["verified"] is False, "invented Paramount read")
        require(candidate["url"].startswith("https://www.paramountplus.com/shows/video/"), "Paramount candidate URL")

    works = payload["work_candidates"]
    require(len(works) == 3 and len({w["id"] for w in works}) == 3, "work candidate IDs")
    for work in works:
        require(work["global_work_identity"] == "UNRESOLVED", "global work reconciliation")
    entities = payload["local_entities"]
    entity_ids = {e["id"] for e in entities}
    require(len(entities) == len(entity_ids) == 4, "local entities")
    for entity in entities:
        require(entity["global_identity"] == "UNRESOLVED", "global entity reconciliation")

    evidence = payload["evidence"]
    ids = {e["id"] for e in evidence}
    require(len(evidence) == len(ids) == 6, "source-local evidence IDs")
    for item in evidence:
        require(item["source_id"] in EXPECTED_SOURCES, "evidence unbound")
        require(item["kind"].startswith("PUBLISHER_"), "not a firsthand episode view")
        require(item["locator"].startswith(("article lines", "image caption")), "line locator")
        require(item["evidence_strength"].startswith(("FIRST_PARTY_PUBLISHER_", "VISIBLE_PUBLISHER_")), "evidence framing")

    assertions = payload["assertions"]
    require(len(assertions) == 3, "bounded assertion count")
    for assertion in assertions:
        require(assertion["subject"] in entity_ids, "unbound subject")
        require(assertion["status"].startswith("PROPOSED_"), "false admission")
        require(assertion["supporting_evidence_ids"] and set(assertion["supporting_evidence_ids"]) <= ids, "missing supporting evidence")
        require(set(assertion["neutral_evidence_ids"] + assertion["disconfirming_evidence_ids"]) <= ids, "missing comparison evidence")
        require(assertion["falsifier"], "missing falsifier")

    artwork = payload["artwork_candidates"]
    require(len(artwork) == 3 and {a["id"] for a in artwork} == {"A1", "A2", "A3"}, "artwork count")
    require({a["source_id"] for a in artwork} == set(EXPECTED_SOURCES), "artwork bound to sources")
    for item in artwork:
        require(item["url"].startswith("https://images.prismic.io/star-trek-untold/"), "not publisher-linked asset")
        require(item["direct_image_fetch"] == "ERROR", "image bytes weren't retrieved")
        require(item["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "publication grant not established")
        require(item["bytes_downloaded"] is False and item["repo_distribution"] == "NONE" and item["explorer_effect"] == "NONE", "image publication")

    persona = payload["persona_note"]
    require(persona["mode"] == "OPTIONAL_FICTIONAL_ROLEPLAY_ONLY", "unqualified Lore persona")
    require(persona["actual_consciousness_transfer_claim"] is False and persona["actual_model_personhood_claim"] is False, "real AI metaphysical claim")
    require(persona["research_evidence_for_real_model_identity"] == "NONE", "real model identity evidence")
    require(persona["user_suggested_premise_not_canon_assertion"] is True, "user speculation promoted")


def main() -> None:
    data = json.loads(PACKET.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)
    validate(data)
    print("TNG_LORE_PRIMARY_PACKET_VALID: 3 publisher articles, 6 evidence, 3 HELD artwork locators, zero public/admitted effects")


if __name__ == "__main__":
    main()
