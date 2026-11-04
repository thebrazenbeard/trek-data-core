"""Validate the held FILMS archival-finding-aid proposal without network access."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RECORD_PATH = HERE / "records.json"
MANIFEST_PATH = HERE / "BATCH_MANIFEST.json"
RECORD_SHA256 = "8de7913a0a68006ab734fac8b294612cea47b8a041ab150cd9e5aa3b1952d3ed"
EXPECTED_SOURCES = {
    "film-meyer-old-finding-aid-20261104": "https://www.lib.uiowa.edu/scua/msc/tomsc450/msc425/msc425.html",
    "film-meyer-archivespace-item-20261104": "https://aspace.lib.uiowa.edu/repositories/2/archival_objects/496613",
    "film-meyer-archivespace-collection-20261104": "https://s-lib019.lib.uiowa.edu/repositories/2/resources/2996",
}
EXPECTED_WORKS = {"candidate:film-wrath-of-khan", "candidate:film-voyage-home", "candidate:film-undiscovered-country"}
# Source-specific, independently reviewed item claims. A generic allowlist of film
# IDs and evidence IDs is not enough: it permits an otherwise valid item to be
# silently relabeled as a different film or moved to an invented box/date.
II = "candidate:film-wrath-of-khan"
IV = "candidate:film-voyage-home"
VI = "candidate:film-undiscovered-country"
LEGACY = "film-meyer-old-finding-aid-20261104"
CURRENT = "film-meyer-archivespace-item-20261104"
COLLECTION = "film-meyer-archivespace-collection-20261104"
EXPECTED_ENTITY_WORK = {
    "meyer-legacy-ii-revised-draft": II,
    "meyer-legacy-ii-release-dialogue": II,
    "meyer-legacy-iv-script-material": IV,
    "meyer-legacy-vi-revision-group": VI,
    "meyer-current-mixed-title-1982-draft": II,
}
EXPECTED_EVIDENCE = {
    "meyer-e-ii-1982-draft": {
        "source_id": LEGACY, "work_id": II,
        "locator": {"collection": "MsC 425", "addendum": "2000", "listed_box": "48", "section": "Star Trek II: The Wrath of Khan", "finding_aid_lines": [1437, 1439]},
        "observed": {"catalog_item_kind": "Revised Final Draft", "date_as_listed": "1982-01-18"},
    },
    "meyer-e-ii-release-dialogue": {
        "source_id": LEGACY, "work_id": II,
        "locator": {"collection": "MsC 425", "addendum": "2000", "listed_box": "48", "section": "Star Trek II: The Wrath of Khan", "finding_aid_lines": [1466, 1469]},
        "observed": {"catalog_item_kind": "Release Dialogue Script", "date_as_listed": "1982-05-24"},
    },
    "meyer-e-iv-script-material": {
        "source_id": LEGACY, "work_id": IV,
        "locator": {"collection": "MsC 425", "addendum": "2000", "listed_box": "49", "section": "Star Trek IV: The Voyage Home", "finding_aid_lines": [1491, 1504]},
        "observed": {"catalog_item_kinds": ["Revised First Act", "Script Revisions", "Scripts/Correspondence"], "date_labels": ["1985-10-18", "1985-11-07/1985-11-12", "1986-02/1986-03"], "first_act_explicitly_incomplete": True},
    },
    "meyer-e-vi-script-revisions": {
        "source_id": LEGACY, "work_id": VI,
        "locator": {"collection": "MsC 425", "addendum": "2000", "listed_boxes": ["49", "50"], "section": "Star Trek VI: The Undiscovered Country", "finding_aid_lines": [1513, 1555]},
        "observed": {"catalog_item_kinds": ["1991 script revisions", "Complete Script"], "complete_script_date_as_listed": "1991-01-21", "revision_colors_as_listed": ["Pink", "Yellow", "Blue", "Green"], "not_distributed_revision_as_listed": "1991-02-22"},
    },
    "meyer-e-current-mixed-title": {
        "source_id": CURRENT, "work_id": II,
        "locator": {"collection": "MsC0425", "archivespace_object_id": "496613", "listed_box": "56", "catalog_page_lines": [2, 5]},
        "observed": {"catalog_title_as_listed": "Revised final draft by Harve Bennett with Jack B. Sowards and Samuel A. Peepies, Titled: Star Trek II: The Undiscovered Country", "date_as_listed": "1982-01-18"},
    },
    "meyer-e-collection-access": {
        "source_id": COLLECTION, "work_id": II,
        "locator": {"collection": "MsC0425", "section": "Conditions Governing Access / Conditions Governing Use", "catalog_page_lines": [47, 52]},
        "observed": {"research_access_as_stated": "open for research", "publication_requires_rightsholder_consent": True, "unpublished_text_read": False},
    },
}
EXPECTED_ASSERTION_JOINS = {
    "meyer-a-ii-1982-draft": ("meyer-legacy-ii-revised-draft", "meyer-e-ii-1982-draft"),
    "meyer-a-ii-release-dialogue": ("meyer-legacy-ii-release-dialogue", "meyer-e-ii-release-dialogue"),
    "meyer-a-iv-script-material": ("meyer-legacy-iv-script-material", "meyer-e-iv-script-material"),
    "meyer-a-vi-script-revisions": ("meyer-legacy-vi-revision-group", "meyer-e-vi-script-revisions"),
    "meyer-a-current-mixed-title": ("meyer-current-mixed-title-1982-draft", "meyer-e-current-mixed-title"),
    "meyer-a-collection-access": (COLLECTION, "meyer-e-collection-access"),
}
EXPECTED_ASSERTION_OBJECTS = {
    "meyer-a-ii-1982-draft": {"item_kind": "Revised Final Draft", "date": "1982-01-18", "listed_box": "48"},
    "meyer-a-ii-release-dialogue": {"item_kind": "Release Dialogue Script", "date": "1982-05-24", "listed_box": "48"},
    "meyer-a-iv-script-material": {"kinds": ["first-act draft", "script revisions", "script correspondence"], "listed_box": "49"},
    "meyer-a-vi-script-revisions": {"kinds": ["complete script", "color-coded revisions"], "listed_boxes": ["49", "50"]},
    "meyer-a-current-mixed-title": {"literal_title_contains": "Star Trek II: The Undiscovered Country", "date": "1982-01-18", "listed_box": "56", "identity_with_legacy_draft": "UNRESOLVED"},
    "meyer-a-collection-access": {"research": "open", "publication_of_papers": "requires consent", "exact_item_access": "UNVERIFIED"},
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_ids(records: list[dict], key: str, description: str) -> set[str]:
    ids = [r.get(key) for r in records]
    require(len(set(ids)) == len(ids) and all(isinstance(i, str) and i for i in ids), f"{description} unique IDs")
    return set(ids)


def validate_records(data: dict) -> None:
    require(data["packet_id"] == "FILMS-MEYER-ARCHIVAL-SCRIPT-ACCESS-20261104", "packet identity")
    require(data["schema_version"] == "film-archival-script-access-v1", "packet schema")
    require(data["accepted_main"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "accepted head")
    require(data["role"] == "FILMS" and data["proposal_only"] is True, "proposal role")
    require(data["status"] == "HELD_FINDING_AID_READ_ONLY_NO_SCRIPT_CONTENT", "access status")
    for flag in ("coverage_effect", "source_work_binding_effect", "public_release_effect"):
        require(data[flag] == "NONE", f"effect: {flag}")
    for flag in ("full_film_viewed", "screenplay_content_read", "release_dialogue_content_read", "source_page_bytes_held", "archival_page_or_media_bytes_held"):
        require(data[flag] is False, f"false evidence promotion: {flag}")
    require(data["source_hashes"] == [], "no upstream source digests without bytes")
    require(data["synopsis_handling"]["status"] == "HELD_NO_NEW_FILM_CONTENT_SYNOPSIS", "synopsis boundary")
    require(data["synopsis_handling"]["existing_source_relative_paraphrase_packet"] == "proposals/research/films/publisher-synopses-20261103/observations.json", "avoid duplicate synopsis")
    require(data["unresolved_identity"] == "LEGACY_BOX_48_1982_JAN_DRAFT_VS_ARCHIVESSPACE_BOX_56_MIXED_TITLE_NOT_RECONCILED", "do not silently reconcile")

    sources = data["sources"]
    require(len(sources) == 3, "source count")
    require(unique_ids(sources, "source_id", "source") == set(EXPECTED_SOURCES), "source identity")
    for source in sources:
        require(source["record_type"] == "source" and source["status"] == "PROPOSED", "source schema/status")
        require(source["locator"] == EXPECTED_SOURCES[source["source_id"]], "source locator")
        require(source["provider"].startswith("University of Iowa Libraries"), "institutional custody")
        require(source["content_hash"] is None, "no fake raw source hash")
        require(source["independence_group"] == data["independence_group"], "catalogs not independent")

    entities = data["local_entities"]
    entity_ids = unique_ids(entities, "local_entity_id", "local entity")
    require(len(entities) == 5, "entity count")
    require(entity_ids == set(EXPECTED_ENTITY_WORK), "expected archival entities")
    for ent in entities:
        require(ent["record_type"] == "local_entity" and ent["work_id"] in EXPECTED_WORKS, "candidate-local entity")
        require("ARCHIVAL_CATALOG" in ent["entity_kind"], "source-local entity kind")
        require(ent["work_id"] == EXPECTED_ENTITY_WORK[ent["local_entity_id"]], "archival item-to-film binding")

    discoveries = json.loads((ROOT / "explorer/film-catalog.json").read_text(encoding="utf-8"))
    discovered_ids = {f["id"] for f in discoveries["films"]}
    require({w.removeprefix("candidate:") for w in EXPECTED_WORKS} <= discovered_ids, "candidate film IDs accepted")
    require((ROOT / data["synopsis_handling"]["existing_source_relative_paraphrase_packet"]).is_file(), "accepted predecessor exists")

    evidence = data["evidence"]
    evid_ids = unique_ids(evidence, "evidence_id", "evidence")
    require(len(evidence) == 6, "evidence count")
    require(evid_ids == set(EXPECTED_EVIDENCE), "exact expected evidence items")
    for e in evidence:
        require(e["record_type"] == "evidence" and e["source_id"] in EXPECTED_SOURCES, "evidence source")
        require(e["work_id"] in EXPECTED_WORKS and e["evidence_kind"] == "document", "evidence scope")
        require(e["epistemic_status"] == "DIRECT" and e["frame"].startswith("ARCHIVAL_"), "catalog observation only")
        require("collection" in e["locator"] and e["observed"], "evidence locator")
        require("_lines" in "|".join(e["locator"].keys()) or "page_lines" in "|".join(e["locator"].keys()), "line locator")
        expected = EXPECTED_EVIDENCE[e["evidence_id"]]
        for field in ("source_id", "work_id", "locator", "observed"):
            require(e[field] == expected[field], f"archival source-specific {field}: {e['evidence_id']}")

    assertions = data["assertions"]
    require(len(assertions) == 6 and len(unique_ids(assertions, "assertion_id", "assertion")) == 6, "assertions count")
    require({a["assertion_id"] for a in assertions} == set(EXPECTED_ASSERTION_JOINS), "exact expected assertions")
    entities_by_id = {entity["local_entity_id"]: entity for entity in entities}
    evidence_by_id = {item["evidence_id"]: item for item in evidence}
    for a in assertions:
        require(a["record_type"] == "assertion" and a["status"] == "PROPOSED", "assertion not accepted")
        require(a["subject_type"] in ("LOCAL_ENTITY", "SOURCE"), "source-local assertion")
        require(a["subject"] in entity_ids | set(EXPECTED_SOURCES), "assertion target")
        require(a["predicate"] in {"FINDING_AID_LISTS_ARCHIVAL_SCRIPT", "FINDING_AID_LISTS_ARCHIVAL_SCRIPT_GROUP", "ARCHIVESSPACE_LISTS_POTENTIALLY_AMBIGUOUS_SCRIPT", "COLLECTION_CATALOG_STATES_ACCESS_RESTRICTIONS"}, "not a film fact")
        require(a["scope"].get("source_metadata_only") is True or a["scope"].get("access_terms_only") is True, "scope not film truth")
        require(a["evidence"] and set(a["evidence"]) <= evid_ids, "assertion evidence")
        expected_subject, expected_evidence = EXPECTED_ASSERTION_JOINS[a["assertion_id"]]
        require(a["subject"] == expected_subject and a["evidence"] == [expected_evidence], "assertion-specific evidence join")
        require(a["object"] == EXPECTED_ASSERTION_OBJECTS[a["assertion_id"]], "source-relative assertion object must match observed item")
        observed_item = evidence_by_id[expected_evidence]
        if a["subject_type"] == "LOCAL_ENTITY":
            require(entities_by_id[a["subject"]]["work_id"] == observed_item["work_id"], "claim and evidence must name same film")
        else:
            require(a["subject"] == observed_item["source_id"], "source assertion must cite its own source")

    old = next(e for e in evidence if e["evidence_id"] == "meyer-e-ii-1982-draft")
    newer = next(e for e in evidence if e["evidence_id"] == "meyer-e-current-mixed-title")
    require(old["locator"]["listed_box"] == "48" and newer["locator"]["listed_box"] == "56", "box discrepancy retained")
    require(old["observed"]["date_as_listed"] == newer["observed"]["date_as_listed"] == "1982-01-18", "date crosswalk is only a lead")
    require("Star Trek II: The Undiscovered Country" in newer["observed"]["catalog_title_as_listed"], "mixed title retained")
    require(next(a for a in assertions if a["assertion_id"] == "meyer-a-current-mixed-title")["object"]["identity_with_legacy_draft"] == "UNRESOLVED", "do not assert SAME_AS")
    require(next(e for e in evidence if e["evidence_id"] == "meyer-e-ii-release-dialogue")["observed"]["date_as_listed"] == "1982-05-24", "release dialogue lead")


def validate_files() -> None:
    payload = RECORD_PATH.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == RECORD_SHA256, "records SHA256 changed without review")
    data = json.loads(payload)
    validate_records(data)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest["record_type"] == "batch_manifest" and manifest["batch_id"] == data["packet_id"], "manifest batch")
    require(manifest["schema_version"] == data["schema_version"], "manifest schema")
    require(set(manifest["works"]) == EXPECTED_WORKS and len(manifest["works"]) == len(EXPECTED_WORKS), "manifest works")
    require(manifest["source_hashes"] == [], "manifest does not claim raw source hashes")
    require(manifest["record_counts"] == {key: len(data[key]) for key in ("sources", "local_entities", "evidence", "assertions")}, "manifest counts")
    require(manifest["batch_hash"] == f"sha256:{RECORD_SHA256}", "manifest content hash")


if __name__ == "__main__":
    validate_files()
    print("FILMS ARCHIVAL SCRIPT ACCESS: HELD source-metadata batch PASS; no film coverage promoted")
