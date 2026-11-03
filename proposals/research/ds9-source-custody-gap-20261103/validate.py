"""Structural, nonadmission validator for DS9 primary-source custody leads."""

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ALLOWED_HOSTS = {
    "gaming.trekcore.com", "www.nobleknight.com", "www.wgfoundation.org",
    "oac.cdlib.org", "www.memoryalpha.st-minutiae.com", "www.paramountplus.com",
}

# This validator guards the *accepted historical observation*, not future access.
# If a source is later authenticated, publish a superseding evidence batch and
# obtain the appropriate Source/Work admission; do not rewrite this gap receipt.
ROUTE_OBSERVATION_CONTRACT = {
    "ds9-licensed-companion-cdrom": {
        "source_class": "PUBLISHER_RELEASED_SCRIPT_LIBRARY_CANDIDATE",
        "lineage_group": "simon-schuster-cdrom-product-description",
        "public_observation_urls": [
            "https://gaming.trekcore.com/ds9companion/description.html",
            "https://www.nobleknight.com/P/2148381541/Star-Trek---Deep-Space-Nine-Companion",
        ],
        "access_status": "NO_AUTHENTICATED_CDROM_SOURCE_IN_CUSTODY",
        "exact_media_hash": None,
    },
    "ds9-wgf-library": {
        "source_class": "INSTITUTION_HELD_PRODUCTION_SCRIPT_CANDIDATE",
        "lineage_group": "institution:wgfoundation",
        "public_observation_urls": [
            "https://www.wgfoundation.org/blog/2026/9/1/read-it-in-the-wgf-library-60-years-of-star-trek",
            "https://www.wgfoundation.org/frequently-asked-questions",
        ],
        "remote_access_status": "ON_SITE_ONLY_NO_REMOTE_COPY",
    },
    "ds9-ucr-ms379": {
        "source_class": "INSTITUTION_HELD_DRAFT_SCRIPT_CANDIDATE",
        "lineage_group": "institution:ucr-ms379",
        "public_observation_urls": ["https://oac.cdlib.org/findaid/ark:/13030/c84t6grz"],
        "remote_access_status": "COLLECTION_DESCRIBED_NO_SCRIPT_BYTES_RETRIEVED",
        "collection_identifier": "MS 379",
    },
    "ds9-st-minutiae-scripts": {
        "source_class": "THIRD_PARTY_TEXT_DERIVATIVE_OR_UNVERIFIED_PROVENANCE",
        "lineage_group": "unverified:st-minutiae",
        "public_observation_urls": [
            "https://www.memoryalpha.st-minutiae.com/resources/scripts/index.html",
        ],
        "remote_access_status": "INDEX_DISCOVERED_CONTENT_NOT_READ_DUE_QUEUE_HOLD",
    },
    "ds9-paramount-streaming": {
        "source_class": "PRIMARY_AIRING_CUT_POTENTIAL_BUT_NOT_VIEWED",
        "lineage_group": "publisher:paramount",
        "public_observation_urls": [
            "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/",
        ],
        "remote_access_status": "NO_AUTHORIZED_STREAM_CAPTURE_OR_FULL_SOURCE_READ",
    },
}

SOURCE_LEVEL_BY_ROUTE = {
    "ds9-licensed-companion-cdrom": "PRODUCT_CLAIM_NOT_SCRIPT_FIDELITY_PROOF",
    "ds9-wgf-library": "PRIMARY_INSTITUTION_SELF_REPORT_NO_SCRIPT_READ",
    "ds9-ucr-ms379": "PRIMARY_ARCHIVE_COLLECTION_DESCRIPTION_NOT_ITEM_EXAMINATION",
    "ds9-st-minutiae-scripts": "DISCOVERY_ONLY_NO_AUTHENTICATED_SCRIPT",
    "ds9-paramount-streaming": "PUBLISHER_METADATA_NOT_PRIMARY_AV_CONTENT",
}

EVIDENCE_KIND_BY_ROUTE = {
    "ds9-licensed-companion-cdrom": "PRODUCT_DESCRIPTION_AND_RESELLER_METADATA",
    "ds9-wgf-library": "INSTITUTIONAL_HOLDINGS_AND_POLICY",
    "ds9-ucr-ms379": "ARCHIVAL_FINDING_AID",
    "ds9-st-minutiae-scripts": "DERIVATIVE_INDEX_DISCOVERY",
    "ds9-paramount-streaming": "PUBLISHER_EPISODE_CATALOG",
}

EXPECTED_UNREAD_FIELDS = {
    "ds9-licensed-companion-cdrom": {
        "publisher_master_or_custody_chain_verified",
        "script_versions_and_revision_pages_verified", "matching_target_script_bytes_read",
    },
    "ds9-wgf-library": {"exact_target_titles_located_in_catalog", "source_pages_or_images_read"},
    "ds9-ucr-ms379": {"exact_target_titles_located_in_catalog", "source_pages_or_images_read"},
    "ds9-st-minutiae-scripts": {"source_pages_or_images_read", "episode_text_read"},
    "ds9-paramount-streaming": {"episode_video_or_audio_read"},
}

EXPECTED_CLAIM_EVIDENCE_CLASSES = {
    "ds9-licensed-companion-cdrom": "PUBLISHER_BOX_TEXT_TRANSCRIBED_BY_THIRD_PARTY_PLUS_RESELLER_METADATA",
    "ds9-wgf-library": "PRIMARY_INSTITUTION_HOLDINGS_AND_ACCESS_POLICY_STATEMENT",
    "ds9-ucr-ms379": "PRIMARY_ARCHIVAL_FINDING_AID",
    "ds9-st-minutiae-scripts": "THIRD_PARTY_INDEX_DISCOVERY_ONLY",
    "ds9-paramount-streaming": "PUBLISHER_CATALOG_OBSERVATION",
}

EXPECTED_EVIDENCE_LOCATORS = {
    "ds9-licensed-companion-cdrom": "TrekCore product-description lines 14-29; Noble Knight retail product metadata",
    "ds9-wgf-library": "WGF 60 Years of Star Trek article, library-materials section; WGF FAQ Library and Archive script-copy section",
    "ds9-ucr-ms379": "OAC UC Riverside MS379 Summary, Scope and Content, Access and Use",
    "ds9-st-minutiae-scripts": "Public Collected Star Trek Scripts index, DS9 seasons and aggregate ZIP listing",
    "ds9-paramount-streaming": "Paramount+ DS9 Season 1 episode guide; accepted publisher-guide proposal in this repository",
}

# Accepted public candidate receipts are historical observations. These are
# canonical JSON semantic fingerprints (not authentication of source bytes).
# A correction or subsequent access must be a separately reviewed successor.
SNAPSHOT_SHA256 = {
    "source_routes": "a6a1eefa0902bd3ceb2049bd57cb2195717ce71bc6d7a33c660c428e78c9c513",
    "evidence": "2f51a179da0ec313d8a1dba9292ecc36a7f0fd93cfd50afa409e2452c6a1c58d",
    "assertions": "7bae5b275c0378ca4ecb3adca097ad86419213c52fa7ffeb9a3a782e78dc1147",
    "archive_item_leads": "5b3b449268ffeea02dce293164b2ed92fa62cad505f4a9b02ac7d1c4fd182d06",
}

ARCHIVE_ITEM_CONTRACT = {
    "lead_id": "ds9-ucr-ms379-for-the-uniform-box3-folder15",
    "source_route_id": "ds9-ucr-ms379",
    "archive": "UC Riverside Special Collections and Archives",
    "collection_identifier": "MS 379",
    "item_title_as_cataloged": (
        'Call sheets and other material for the Star Trek Deep Space Nine episode '
        'titled "For the Uniform"'
    ),
    "cataloged_date": "1996",
    "box": "3",
    "folder": "15",
    "item_url": "https://oac.cdlib.org/findaid/ark:/13030/c84t6grz_aspace_ref54_5ke",
    "observed_fidelity": "ARCHIVE_ITEM_LEVEL_HOLDINGS_DESCRIPTION_ONLY",
    "held_material_scope": "CALL_SHEETS_AND_OTHER_MATERIAL_SCRIPT_NOT_ATTESTED",
    "relationship_to_target_batch": "OUTSIDE_CURRENT_FIVE_SEASON_1_CARDS",
    "web_locator": "OAC item page, title, Containers, Dates, Access and use, Collection Overview",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exactly_keys(obj, expected, scope):
    require(isinstance(obj, dict) and set(obj) == set(expected),
            f"{scope}: missing or extra fields")


def check_snapshot(obj, name):
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    require(digest == SNAPSHOT_SHA256[name], f"{name}: accepted observation was rewritten")


def reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def check_contract(routes, evidence, assertions, known_card_ids):
    exactly_keys(routes, {
        "schema_version", "batch_id", "role", "proposal_only", "accepted_work_effect",
        "accepted_source_binding_effect", "coverage_effect", "denominator_effect",
        "full_primary_episode_or_script_read", "scope", "accepted_main_at_selection",
        "director_queue_hold", "observed_date_utc", "target_source_local_cards",
        "target_work_identity_status", "routes", "public_catalog_or_policy_pages_read",
        "primary_script_or_av_reads_completed", "new_close_read_batches_created",
        "admitted_briefings", "global_identity_links_created",
    }, "route manifest")
    require(routes["schema_version"] == "1.0.0"
            and routes["batch_id"] == "ds9-source-custody-gap-20261103", "route schema drift")
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
    require(len(items) == len(ROUTE_OBSERVATION_CONTRACT), "source route count drift")
    route_ids = [item.get("route_id") for item in items]
    require(len(set(route_ids)) == len(ROUTE_OBSERVATION_CONTRACT)
            and set(route_ids) == set(ROUTE_OBSERVATION_CONTRACT), "source route identity drift")
    for route in items:
        rid = route["route_id"]
        rights_field = ("rights_to_republish_episode_media" if rid == "ds9-paramount-streaming"
                        else "rights_to_republish_script_text")
        exactly_keys(route, set(ROUTE_OBSERVATION_CONTRACT[rid]) | {
            "route_id", "candidate_material", "claim_evidence_class",
            "observed_claim", "next_gate", rights_field,
        } | EXPECTED_UNREAD_FIELDS[rid], f"{rid} route")
        for field, value in ROUTE_OBSERVATION_CONTRACT[rid].items():
            require(field in route and route[field] == value, f"{rid}: {field} observation changed")
        for flag in EXPECTED_UNREAD_FIELDS[rid]:
            require(route[flag] is False, f"{rid}: {flag} cannot claim unreviewed access")
        require(route.get("claim_evidence_class") == EXPECTED_CLAIM_EVIDENCE_CLASSES[rid],
                f"{rid}: source claim evidence reclassified")
        require(route.get(rights_field) == "UNVERIFIED", f"{rid}: rights status changed")
        require(route.get("next_gate") and route.get("observed_claim"), "missing custody or audit gate")
        require(route.get("lineage_group"), "missing lineage group")
        for url in route.get("public_observation_urls", []):
            parts = urlsplit(url)
            require(parts.scheme == "https" and parts.hostname in ALLOWED_HOSTS
                    and parts.username is None and parts.password is None
                    and parts.fragment == "", "untrusted source URL")
    exactly_keys(evidence, {
        "record_type", "batch_id", "source_scope", "evidence",
        "episode_scene_or_dialogue_evidence_count", "source_route_observation_count",
    }, "evidence manifest")
    require(len(evidence.get("evidence", [])) == 5 and evidence.get("episode_scene_or_dialogue_evidence_count") == 0,
            "scene evidence manufactured")
    evidence_ids = [e.get("id") for e in evidence["evidence"]]
    require(len(set(evidence_ids)) == 5, "duplicate source evidence")
    for observation in evidence["evidence"]:
        exactly_keys(observation, {"id", "route_id", "kind", "locator", "observation", "source_level"},
                     "source evidence")
        require(observation.get("route_id") in route_ids, "orphan source observation")
        require(observation.get("source_level") == SOURCE_LEVEL_BY_ROUTE[observation["route_id"]],
                "source observation upgraded or changed")
        require(observation.get("kind") == EVIDENCE_KIND_BY_ROUTE[observation["route_id"]]
                and observation.get("locator") == EXPECTED_EVIDENCE_LOCATORS[observation["route_id"]],
                "unscoped or recoded source observation")
    require({e["route_id"] for e in evidence["evidence"]} == set(route_ids),
            "source evidence route duplication or omission")
    exactly_keys(assertions, {
        "record_type", "batch_id", "assertions", "accepted_assertions", "projection_effect",
    }, "assertion manifest")
    require(assertions.get("accepted_assertions") == 0 and assertions.get("projection_effect") == "NONE",
            "assertion promotion")
    require(len(assertions.get("assertions", [])) == 3, "assertion count drift")
    for assertion in assertions["assertions"]:
        exactly_keys(assertion, {
            "id", "predicate", "subject", "object", "evidence_ids", "counter_evidence_ids",
            "status", "falsifier",
        }, "source assertion")
        require(assertion.get("status") == "PROPOSED_UNRESOLVED", "forced resolution")
        require(set(assertion.get("evidence_ids", [])).issubset(evidence_ids), "orphan assertion")
        require(assertion.get("falsifier"), "unfalsifiable source claim")
    check_snapshot(routes, "source_routes")
    check_snapshot(evidence, "evidence")
    check_snapshot(assertions, "assertions")


def check_archive_item_leads(leads):
    exactly_keys(leads, {
        "schema_version", "record_type", "proposal_only", "coverage_effect",
        "accepted_work_effect", "source_bytes_retrieved",
        "primary_script_or_av_reads_completed", "items",
    }, "archive lead manifest")
    require(leads["schema_version"] == "1.0.0", "archive lead schema drift")
    require(leads.get("record_type") == "SOURCE_LOCAL_ARCHIVAL_ITEM_DISCOVERY_NOT_SOURCE_WORK_BINDING"
            and leads.get("proposal_only") is True, "archive lead scope upgraded")
    require(leads.get("coverage_effect") == "NONE" and leads.get("accepted_work_effect") == "NONE",
            "archive lead admitted as coverage or Work")
    require(leads.get("source_bytes_retrieved") == 0
            and leads.get("primary_script_or_av_reads_completed") == 0, "archive bytes falsely claimed")
    items = leads.get("items", [])
    require(len(items) == 1, "archive item count drift")
    item = items[0]
    exactly_keys(item, set(ARCHIVE_ITEM_CONTRACT) | {
        "accepted_work_id", "script_body_read", "episode_audiovisual_read",
        "item_bytes_read", "source_content_hash", "exact_episode_cut_or_script_revision",
        "rights_to_reproduce_material", "next_gate",
    }, "archive item")
    for field, expected in ARCHIVE_ITEM_CONTRACT.items():
        require(field in item and item[field] == expected, f"archive lead {field} identity drift")
    require(item.get("accepted_work_id") is None
            and item.get("source_content_hash") is None
            and item.get("exact_episode_cut_or_script_revision") is None,
            "archive item falsely bound or authenticated")
    for field in ("script_body_read", "episode_audiovisual_read", "item_bytes_read"):
        require(item.get(field) is False, f"archive item {field} falsely claimed")
    require(item.get("rights_to_reproduce_material") == "UNVERIFIED", "archive rights upgraded")
    require(item.get("next_gate"), "archive next gate missing")
    check_snapshot(leads, "archive_item_leads")


def load_and_validate():
    def load(path):
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_json_keys)

    routes = load(HERE / "source_routes.json")
    evidence = load(HERE / "evidence.json")
    assertions = load(HERE / "assertions.json")
    archive_leads = load(HERE / "archive_item_leads.json")
    prior = load(REPO / "proposals/research/ds9-paramount-s1-guide-20261103/records.json")
    known_ids = {row["id"] for row in prior["source_local_episode_slots"]}
    check_contract(routes, evidence, assertions, known_ids)
    check_archive_item_leads(archive_leads)
    print("DS9_SOURCE_CUSTODY_GAP_OK: 5 gated routes, 5 public-source observations, "
          "3 unresolved claims, 1 catalog-only item lead; zero new primary reads/coverage")


if __name__ == "__main__":
    load_and_validate()
