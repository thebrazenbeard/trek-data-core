"""Replay a frozen publisher discovery receipt against five archived candidate labels.

This is Librarian metadata triage only: NO new source retrieval, canonical Work
identity, accepted Source/Work binding, complete-source reading, or coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from tools.build_lead_source_crosswalk import CrosswalkValidationError, canonical_bytes, require


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/librarian/lead-qualification-tos-s1-followon-20261104"
LEADS = ROOT / "explorer/research-leads.json"
PUBLISHER_DIR = ROOT / "proposals/discovery/legacy-paramount-season1-20261102"
PREVIOUS = ROOT / "proposals/librarian/lead-qualification-tos-s1-20261103/crosswalk.json"
# Anchors are digests of files on accepted main@3028765359001b90bc3e6b5c1835ee283b326e91.
# A mutable index and a correspondingly altered CSV must not be allowed to
# mutually attest a new source history. These pins establish Git-baseline
# integrity only; they do NOT authenticate the original web retrieval.
ACCEPTED_SOURCE_SHA256 = {
    "archived_wdqs_leads": "efab937a08445f2ada98eb2b8137f05477b9002e8d462ece715925524fd35d66",
    "publisher_discovery_index": "028b43d43b009ac7f88d37c94002c70331b5394d2c978eff51f0c711fab3638d",
    "publisher_discovery_csv": "b0055cd053941bc0f822ebe2738286e44e40ddb301134c6c6bcf448f42fe7859",
    "publisher_discovery_bundle": "8d6ce2370dbc57b340c395089247061ce8967d4f17324132fc981b331c88c2a0",
    "prior_crosswalk": "3722d732ff65350713a516b8c720a18211943dc818442d4031415f5683c22430",
}


def pinned_bytes(path: Path, anchor: str) -> bytes:
    payload = path.read_bytes()
    require(hashlib.sha256(payload).hexdigest() == ACCEPTED_SOURCE_SHA256[anchor],
            f"Accepted-main source-lineage anchor drift: {anchor}")
    return payload


def build(selection_override: dict | None = None) -> dict:
    selection_bytes = (BATCH / "selection.json").read_bytes()
    selected = selection_override if selection_override is not None else json.loads(selection_bytes)
    custody = selected["source_custody"]
    require(selected["batch_id"] == BATCH.name, "Wrong batch identifier")
    require(custody["new_primary_source_retrieval"] == "NONE", "Unexpected retrieval claim")
    require(custody["live_page_rechecked"] is False, "Unexpected live page claim")
    require(custody["new_html_response_sha256"] is None, "Unexpected new capture digest")
    require(custody["prior_observation_directory"] == str(PUBLISHER_DIR.relative_to(ROOT)), "Observation directory changed")
    require(custody["prior_observation_date"] == "2026-11-02", "Observation date changed")

    publisher_index = json.loads(pinned_bytes(PUBLISHER_DIR / "index.json", "publisher_discovery_index"))
    publisher_bundle = json.loads(pinned_bytes(PUBLISHER_DIR / "tos/bundle.json", "publisher_discovery_bundle"))
    prior_guide = next((x for x in publisher_index["source_pages"] if x["mission_id"] == "tos"), None)
    require(prior_guide is not None, "No accepted TOS discovery receipt")
    require(publisher_index["independence_group"] == "publisher:paramount", "Publisher provenance group drift")
    require(custody["publisher_page"] == prior_guide["official_page"], "Publisher URL mismatch")
    require(publisher_bundle["accepted_source_binding_effect"] == "NONE", "Publisher source binding unexpectedly admitted")
    require(publisher_bundle["accepted_work_effect"] == "NONE", "Publisher Work unexpectedly admitted")
    observation = pinned_bytes(PUBLISHER_DIR / "tos.csv", "publisher_discovery_csv")
    require(hashlib.sha256(observation).hexdigest() == prior_guide["observation_csv_sha256"], "Publisher CSV digest mismatch")
    rows = list(csv.DictReader(io.StringIO(observation.decode("utf-8"))))
    require(len(rows) == prior_guide["listed_slot_count"] == 30, "Publisher slot count drift")

    leads = json.loads(pinned_bytes(LEADS, "archived_wdqs_leads"))
    require(leads["lead_count"] == len(leads["leads"]) == 218, "Archived lead count drift")
    qids = [x["episode_qid"] for x in leads["leads"] if x.get("episode_qid")]
    require(len(qids) == len(set(qids)), "Archived candidate QID collision")
    by_qid = {x["episode_qid"]: x for x in leads["leads"] if x.get("episode_qid")}
    previous = json.loads(pinned_bytes(PREVIOUS, "prior_crosswalk"))
    require(previous["source_work_binding_admission"] == "NONE", "Prior tranche has admitted bindings")
    prior_qids = {x["candidate_qid"] for x in previous["matches"]}
    prior_ordinals = {(x["publisher_season"], x["publisher_episode_number"]) for x in previous["matches"]}
    choices = selected["selected"]
    require(len(choices) == 5, "Tranche must be five choices")
    require(len({x["qid"] for x in choices}) == 5, "Duplicate candidate QIDs")
    require(len({(x["season"], x["publisher_episode_number"]) for x in choices}) == 5, "Duplicate publisher ordinals")

    matches = []
    for choice in choices:
        require(choice["qid"] not in prior_qids, "QID overlaps prior tranche")
        require((choice["season"], choice["publisher_episode_number"]) not in prior_ordinals, "Publisher ordinal overlaps prior tranche")
        candidate = by_qid.get(choice["qid"])
        require(candidate is not None, "Unknown archived QID")
        require(candidate["mission_id"] == "tos", "Candidate is not from TOS mission")
        require(candidate["source_type"] == "WIKIDATA_METADATA", "Unexpected candidate source type")
        require(candidate["verification_status"] == "UNVERIFIED_METADATA", "Candidate unexpectedly verified")
        require(candidate["independence_group"] == "wikidata:wdqs", "Candidate provenance group drift")
        corresponding = [x for x in rows if x["season"] == str(choice["season"]) and x["episode_number"] == str(choice["publisher_episode_number"])]
        require(len(corresponding) == 1, "Publisher ordinal absent or ambiguous")
        observed = corresponding[0]
        require(candidate["episode_label"] == choice["publisher_title"] == observed["title"], "Exact-title publisher/lead mismatch")
        require(sum(x["title"] == observed["title"] for x in rows) == 1, "Publisher title not unique")
        matches.append({
            "candidate_qid": candidate["episode_qid"],
            "candidate_title": candidate["episode_label"],
            "candidate_mission": candidate["mission_id"],
            "candidate_snapshot_id": candidate["snapshot_id"],
            "candidate_response_sha256": candidate["response_sha256"],
            "candidate_independence_group": candidate["independence_group"],
            "publisher_title": observed["title"],
            "publisher_season": choice["season"],
            "publisher_episode_number": choice["publisher_episode_number"],
            "publisher_independence_group": publisher_index["independence_group"],
            "publisher_official_page": prior_guide["official_page"],
            "publisher_prior_observation_locator": f"Season {choice['season']} / {observed['title']} / S1 E{choice['publisher_episode_number']}",
            "publisher_prior_html_sha256": prior_guide["source_body_sha256"],
            "publisher_prior_html_byte_count": prior_guide["source_body_bytes"],
            "publisher_observation_csv_sha256": prior_guide["observation_csv_sha256"],
            "status": "PROPOSED_TITLE_AND_SERIES_CROSSWALK",
            "source_lineage_independent_of_wikidata_export": "UNVERIFIED_HISTORICAL_PROVENANCE",
            "canonical_work_id": None,
            "accepted_source_work_binding": None,
            "briefing_admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    return {
        "batch_id": selected["batch_id"],
        "schema_version": "1.0.0",
        "proposal_status": "SOURCE_RELATIVE_METADATA_CROSSWALK_ONLY",
        "source_retrieved_in_this_batch": "NONE_REPLAY_OF_PRIOR_HASH_PINNED_OBSERVATION",
        "accepted_source_integrity_anchor": "ACCEPTED_MAIN_3028765359001B90_BLOB_DIGESTS_NOT_EXTERNAL_AUTHENTICATION",
        "publisher_raw_html_new_capture": "NOT_CAPTURED",
        "source_local_crosswalk_count": 5,
        "total_research_leads_unchanged": leads["lead_count"],
        "prior_tranche_crosswalk_count": len(prior_qids),
        "source_work_binding_admission": "NONE",
        "briefing_admission_effect": "NONE",
        "denominator_effect": "NONE",
        "coverage_effect": "NONE",
        "selection_sha256": hashlib.sha256(selection_bytes).hexdigest() if selection_override is None else None,
        "matches": matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = canonical_bytes(build())
    dest = BATCH / "crosswalk.json"
    if args.check:
        require(dest.is_file() and dest.read_bytes() == payload, "Follow-on crosswalk is stale or missing")
        print("TOS_FOLLOWON_CROSSWALK_OK:5 (proposal only; 0 admissions)")
        return 0
    dest.write_bytes(payload)
    print("WROTE_TOS_FOLLOWON_CROSSWALK:5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
