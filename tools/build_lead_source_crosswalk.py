"""Reproducible, deliberately non-admitting lead-to-publisher title crosswalk.

Matching QID and title against a publisher listing is *not* canonical Work
identity, authenticated television footage, or an accepted Source↔Work bind.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "proposals/librarian/lead-qualification-tos-s1-20261103"
LEADS = ROOT / "explorer/research-leads.json"
PUBLISHER_DIR = ROOT / "proposals/discovery/legacy-paramount-season1-20261102"


class CrosswalkValidationError(ValueError):
    """Unsafe or unverified publisher/lead reconciliation input."""


def require(condition: bool, reason: str) -> None:
    """Fail closed even when invoked with `python -O`."""
    if not condition:
        raise CrosswalkValidationError(reason)


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build() -> dict:
    selection = json.loads((BATCH / "selection.json").read_text(encoding="utf-8"))
    leads = json.loads(LEADS.read_text(encoding="utf-8"))
    publisher_index = json.loads((PUBLISHER_DIR / "index.json").read_text(encoding="utf-8"))
    publisher_bundle = json.loads((PUBLISHER_DIR / "tos/bundle.json").read_text(encoding="utf-8"))
    guide = next((s for s in publisher_index["source_pages"] if s["mission_id"] == "tos"), None)
    require(guide is not None, "Missing official TOS source receipt")
    observation = (PUBLISHER_DIR / "tos.csv").read_bytes()
    require(hashlib.sha256(observation).hexdigest() == guide["observation_csv_sha256"], "Publisher observation CSV SHA-256 mismatch")
    require(publisher_index["independence_group"] == "publisher:paramount", "Publisher lineage mismatch")
    require(guide["official_page"] == selection["publisher_page_rendered_recheck"]["official_page"], "Official publisher URL mismatch")
    require(publisher_bundle["accepted_source_binding_effect"] == "NONE", "Unexpected publisher source-binding admission")
    require(publisher_bundle["accepted_work_effect"] == "NONE", "Unexpected publisher Work admission")
    source_rows = list(csv.DictReader(io.StringIO(observation.decode("utf-8"))))
    require(len(source_rows) == guide["listed_slot_count"] == 30, "TOS Season 1 guide observation row count changed")
    by_qid = {row.get("episode_qid"): row for row in leads["leads"] if row.get("episode_qid")}
    require(len({x["qid"] for x in selection["selected"]}) == len(selection["selected"]) == 5, "Duplicate QIDs or incorrect crosswalk tranche size")

    matches = []
    for item in selection["selected"]:
        lead = by_qid.get(item["qid"])
        require(lead is not None, f"QID not present in archived candidate leads: {item['qid']}")
        require(lead["mission_id"] == "tos", "Lead is not assigned to TOS")
        require(lead["source_type"] == "WIKIDATA_METADATA", "Lead no longer has archived Wikidata source type")
        require(lead["independence_group"] == "wikidata:wdqs", "Lead independence group mismatch")
        require(lead["verification_status"] == "UNVERIFIED_METADATA", "Unexpected promoted lead admission")
        expected = next(
            (row for row in source_rows
            if row["season"] == str(item["season"])
            and row["episode_number"] == str(item["publisher_episode_number"])), None
        )
        require(expected is not None, "Selected publisher ordinal absent from captured guide")
        require(lead["episode_label"] == expected["title"], "Archived lead title does not exactly match publisher listing")
        require(expected["title"] in item["publisher_rendered_heading_locator"], "Publisher rendered heading locator title mismatch")
        require(f"S1 E{item['publisher_episode_number']}" in item["publisher_rendered_heading_locator"], "Publisher rendered heading locator ordinal mismatch")
        matches.append({
            "candidate_qid": lead["episode_qid"],
            "candidate_title": lead["episode_label"],
            "candidate_mission": lead["mission_id"],
            "candidate_snapshot_id": lead["snapshot_id"],
            "candidate_response_sha256": lead["response_sha256"],
            "candidate_independence_group": lead["independence_group"],
            "publisher_independence_group": publisher_index["independence_group"],
            "publisher_title": expected["title"],
            "publisher_season": item["season"],
            "publisher_episode_number": item["publisher_episode_number"],
            "publisher_official_page": guide["official_page"],
            "publisher_rendered_heading_locator": item["publisher_rendered_heading_locator"],
            "publisher_prior_html_sha256": guide["source_body_sha256"],
            "publisher_prior_html_byte_count": guide["source_body_bytes"],
            "publisher_observation_csv_sha256": guide["observation_csv_sha256"],
            "status": "PROPOSED_TITLE_AND_SERIES_CROSSWALK",
            "source_lineage_independent_of_wikidata_export": "UNVERIFIED_HISTORICAL_PROVENANCE",
            "canonical_work_id": None,
            "accepted_source_work_binding": None,
            "briefing_admission_effect": "NONE",
            "coverage_effect": "NONE",
        })

    return {
        "batch_id": selection["batch_id"],
        "schema_version": "1.0.0",
        "proposal_status": "SOURCE_RELATIVE_METADATA_CROSSWALK_ONLY",
        "source_retrieved_in_this_batch": "PUBLISHER_PAGE_WEB_READER_RENDERED_COMPLETE_GUIDE",
        "publisher_raw_html_new_capture": "NOT_CAPTURED",
        "source_local_crosswalk_count": len(matches),
        "total_research_leads_unchanged": leads["lead_count"],
        "source_work_binding_admission": "NONE",
        "briefing_admission_effect": "NONE",
        "denominator_effect": "NONE",
        "coverage_effect": "NONE",
        "selection_sha256": hashlib.sha256((BATCH / "selection.json").read_bytes()).hexdigest(),
        "matches": matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = canonical_bytes(build())
    dest = BATCH / "crosswalk.json"
    if args.check:
        if not dest.exists() or dest.read_bytes() != payload:
            raise SystemExit("crosswalk.json is stale or missing")
        print("LEAD_CROSSWALK_OK:5 (proposal only; 0 admissions)")
        return 0
    dest.write_bytes(payload)
    print("WROTE_LEAD_CROSSWALK:5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
