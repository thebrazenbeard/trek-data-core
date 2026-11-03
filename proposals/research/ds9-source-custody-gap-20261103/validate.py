"""Structural, nonadmission validator for DS9 primary-source custody leads."""

import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ALLOWED_HOSTS = {
    "gaming.trekcore.com", "www.nobleknight.com", "www.wgfoundation.org",
    "oac.cdlib.org", "www.memoryalpha.st-minutiae.com", "www.paramountplus.com",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_contract(routes, evidence, assertions, known_card_ids):
    require(routes.get("role") == "DS9" and routes.get("proposal_only") is True,
            "must be DS9 candidate-only")
    for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        require(routes.get(effect) == "NONE", f"unexpected acceptance effect: {effect}")
    require(routes.get("full_primary_episode_or_script_read") is False, "unauthorized primary close-read")
    require(routes.get("primary_script_or_av_reads_completed") == 0, "new primary read claim")
    require(routes.get("new_close_read_batches_created") == 0 and routes.get("admitted_briefings") == 0,
            "queue hold or admission bypass")
    require(routes.get("global_identity_links_created") == 0, "global identity mutation")
    require(routes.get("director_queue_hold") == "https://github.com/thebrazenbeard/trek-data-core/issues/23",
            "queue hold erased")
    cards = routes.get("target_source_local_cards", [])
    require(len(cards) == len(set(cards)) == 5 and set(cards).issubset(known_card_ids),
            "unknown or duplicate source-local card")
    require(routes.get("target_work_identity_status") == "UNBOUND_CANDIDATE_CARDS_NOT_ACCEPTED_WORKS",
            "unreviewed Work binding")

    items = routes.get("routes", [])
    require(len(items) == 5, "source route count drift")
    route_ids = [item.get("route_id") for item in items]
    require(len(set(route_ids)) == 5, "source route collision")
    for route in items:
        require(route.get("source_pages_or_images_read") is not True, "unsupported script read")
        require(route.get("rights_to_republish_script_text", "UNVERIFIED") == "UNVERIFIED",
                "rights silently upgraded")
        require(route.get("next_gate") and route.get("observed_claim"), "missing custody or audit gate")
        require(route.get("lineage_group"), "missing lineage group")
        for url in route.get("public_observation_urls", []):
            parts = urlsplit(url)
            require(parts.scheme == "https" and parts.hostname in ALLOWED_HOSTS
                    and parts.username is None and parts.password is None
                    and parts.fragment == "", "untrusted source URL")
    require(len(evidence.get("evidence", [])) == 5 and evidence.get("episode_scene_or_dialogue_evidence_count") == 0,
            "scene evidence manufactured")
    evidence_ids = [e.get("id") for e in evidence["evidence"]]
    require(len(set(evidence_ids)) == 5, "duplicate source evidence")
    for observation in evidence["evidence"]:
        require(observation.get("route_id") in route_ids, "orphan source observation")
        require(observation.get("source_level") and observation.get("kind"), "unscoped observation")
    require(assertions.get("accepted_assertions") == 0 and assertions.get("projection_effect") == "NONE",
            "assertion promotion")
    require(len(assertions.get("assertions", [])) == 3, "assertion count drift")
    for assertion in assertions["assertions"]:
        require(assertion.get("status") == "PROPOSED_UNRESOLVED", "forced resolution")
        require(set(assertion.get("evidence_ids", [])).issubset(evidence_ids), "orphan assertion")
        require(assertion.get("falsifier"), "unfalsifiable source claim")


def load_and_validate():
    def load(path):
        return json.loads(path.read_text(encoding="utf-8"))

    routes = load(HERE / "source_routes.json")
    evidence = load(HERE / "evidence.json")
    assertions = load(HERE / "assertions.json")
    prior = load(REPO / "proposals/research/ds9-paramount-s1-guide-20261103/records.json")
    known_ids = {row["id"] for row in prior["source_local_episode_slots"]}
    check_contract(routes, evidence, assertions, known_ids)
    print("DS9_SOURCE_CUSTODY_GAP_OK: 5 gated routes, 5 public-source observations, "
          "3 unresolved claims; zero new primary reads/coverage")


if __name__ == "__main__":
    load_and_validate()
