#!/usr/bin/env python3
"""Offline audit of reviewed live guide fields vs draft #488 and accepted inputs.

The field-level live observations were recorded separately in review.json.
This checker tests their internal/archived consistency, not remote freshness,
independent corpus identity or evidence-bearing Source admission.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "proposals/librarian/tos-s1-pr488-source-audit-20261104/review.json"
LEADS = ROOT / "explorer/research-leads.json"
PUBLISHER = ROOT / "proposals/discovery/legacy-paramount-season1-20261102/tos.csv"
LEADS_SHA = "efab937a08445f2ada98eb2b8137f05477b9002e8d462ece715925524fd35d66"
PUBLISHER_SHA = "b0055cd053941bc0f822ebe2738286e44e40ddb301134c6c6bcf448f42fe7859"
SELECTION_PATH = "proposals/librarian/lead-qualification-tos-s1-followon-20261104/selection.json"
GUIDE = "https://www.paramountplus.com/shows/star_trek/episodes/1/"


class AuditError(ValueError):
    pass


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise AuditError("duplicate JSON key")
        out[key] = value
    return out


def parse_json(data: bytes):
    try:
        return json.loads(data, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError("malformed JSON") from exc


def hash_accepted(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise AuditError(f"accepted input changed: {path.name}")
    return data


def validate_pr_selection(selection: dict, audit: dict) -> None:
    if selection.get("source_custody", {}).get("publisher_page") != GUIDE:
        raise AuditError("draft selection has changed publisher locator")
    if selection.get("source_custody", {}).get("live_page_rechecked") is not False:
        raise AuditError("draft selection falsely claims it made this live check")
    rows = selection.get("selected")
    if not isinstance(rows, list) or len(rows) != 5:
        raise AuditError("draft selection is not five rows")
    proposed = {(row.get("qid"), row.get("season"), row.get("publisher_episode_number"), row.get("publisher_title"))
                for row in rows if isinstance(row, dict)}
    audited = {(row["qid"], row["season"], row["paramount_slot"], row["title"]) for row in audit["rows"]}
    if len(proposed) != 5 or proposed != audited:
        raise AuditError("draft candidate title/slot/QID disagrees with reviewed source fields")


def analyze(audit: dict, archive_leads: dict, archive_csv: bytes) -> dict:
    if (audit.get("record_type") != "external_metadata_source_audit"
        or audit.get("status") != "REVIEW_ONLY_NO_ADMISSION"
        or audit.get("draft_pr") != 488
        or audit.get("accepted_main") != "3028765359001b90bc3e6b5c1835ee283b326e91"):
        raise AuditError("unrecognized audit scope or accepted baseline")
    if any(audit.get(field) != "NONE" for field in
           ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect")):
        raise AuditError("audit cannot make governed admission or coverage claims")
    publisher = audit.get("publisher_observation")
    wikidata = audit.get("wikidata_observation")
    if not isinstance(publisher, dict) or not isinstance(wikidata, dict):
        raise AuditError("missing source observations")
    if (publisher.get("official_guide_url") != GUIDE or publisher.get("raw_body_sha256") is not None
        or publisher.get("full_episode_content_read") is not False
        or publisher.get("retrieved_page_content") != "EPISODE_GUIDE_FIELD_TEXT_ONLY"
        or publisher.get("observed_on") != "2026-11-04"
        or wikidata.get("raw_response_sha256") is not None
        or wikidata.get("historical_discovery_independence_group") != "wikidata:wdqs"
        or wikidata.get("new_source_custody_effect") != "NONE"):
        raise AuditError("unreviewed source freshness/custody claim")
    rows = audit.get("rows")
    if not isinstance(rows, list) or len(rows) != 5:
        raise AuditError("audit must contain exactly five reviewed candidates")
    archived = archive_leads.get("leads")
    if not isinstance(archived, list):
        raise AuditError("archived lead container missing")
    ids = {}
    for lead in archived:
        if not isinstance(lead, dict):
            raise AuditError("malformed archived lead")
        qid = lead.get("episode_qid")
        # Publisher-only discovery rows legitimately lack an external QID.
        # Their shared `None` is not an episode identity collision.
        if qid is None:
            continue
        if qid in ids:
            raise AuditError("duplicate archived candidate QID")
        ids[qid] = lead
    csv_rows = list(csv.DictReader(io.StringIO(archive_csv.decode("utf-8"))))
    catalog = {}
    for row in csv_rows:
        if set(row) != {"season", "episode_number", "title"}:
            raise AuditError("unexpected publisher CSV schema")
        key = (int(row["season"]), int(row["episode_number"]))
        if key in catalog:
            raise AuditError("duplicate publisher episode slot")
        catalog[key] = row["title"]
    qids, slots, differences = set(), set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"qid", "title", "season", "paramount_slot",
            "wikidata_ordinal_observed", "paramount_guide_lines", "wikidata_item_url", "wikidata_item_lines"}:
            raise AuditError("unreviewed audit row schema")
        qid, title, season, slot = row["qid"], row["title"], row["season"], row["paramount_slot"]
        if qid in qids or (season, slot) in slots:
            raise AuditError("repeated candidate identity or publisher slot")
        qids.add(qid);slots.add((season,slot))
        lead = ids.get(qid)
        if (not lead or lead.get("mission_id") != "tos" or lead.get("episode_label") != title
            or lead.get("source_type") != "WIKIDATA_METADATA"
            or lead.get("verification_status") != "UNVERIFIED_METADATA"
            or lead.get("independence_group") != "wikidata:wdqs"):
            raise AuditError("reviewed QID/title diverges from unverified archived lead")
        if season != 1 or catalog.get((season, slot)) != title:
            raise AuditError("live-reviewed publisher title/slot disagrees with accepted prior observation")
        if row["wikidata_item_url"] != f"https://www.wikidata.org/wiki/{qid}":
            raise AuditError("Wikidata item locator mismatch")
        if (not isinstance(row["wikidata_ordinal_observed"], int)
            or isinstance(row["wikidata_ordinal_observed"], bool)
            or row["wikidata_ordinal_observed"] < 1):
            raise AuditError("invalid source-relative ordinal")
        if any(not isinstance(span, list) or len(span) < 2 or
               any(not isinstance(line, int) or line < 1 for line in span)
               for span in (row["paramount_guide_lines"], row["wikidata_item_lines"])):
            raise AuditError("missing review locators")
        if slot != row["wikidata_ordinal_observed"]:
            differences.append({"qid": qid, "publisher_slot": slot,
                                "wikidata_ordinal": row["wikidata_ordinal_observed"]})
    return {
        "status": "ORDINAL_NAMESPACE_DIVERGENCE_OBSERVED" if differences else "NO_ORDINAL_DIVERGENCE_IN_REVIEW_RECORD",
        "exact_live_publisher_title_slot_matches": len(rows),
        "ordinal_namespace_differences": sorted(differences, key=lambda row: row["qid"]),
        "independent_publisher_guide_families": 1,
        "independent_wdqs_snapshot_families": 1,
        "raw_live_page_hash_available": False,
        "reviewer_fidelity_to_live_pages": "MANUAL_FIELD_READ_NOT_CRYPTOGRAPHICALLY_ATTESTED",
        "accepted_source_work_coverage_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-pr-head", action="store_true", help="Require locally fetched exact PR #488 Git object")
    args = parser.parse_args()
    try:
        audit = parse_json(REVIEW.read_bytes())
        leads = parse_json(hash_accepted(LEADS, LEADS_SHA))
        publisher = hash_accepted(PUBLISHER, PUBLISHER_SHA)
        result = analyze(audit, leads, publisher)
        if args.verify_pr_head:
            head = audit.get("draft_pr_head")
            if head != "eea7478b08a1ae1b34bf27e74b8884f33f36a1a6":
                raise AuditError("unreviewed draft PR revision")
            selection = subprocess.run(["git", "show", f"{head}:{SELECTION_PATH}"],
                                       cwd=ROOT, capture_output=True, check=False)
            if selection.returncode:
                raise AuditError("exact draft PR #488 selection Git object unavailable")
            if hashlib.sha256(selection.stdout).hexdigest() != audit.get("draft_selection_sha256"):
                raise AuditError("draft selection bytes differ from reviewed revision")
            validate_pr_selection(parse_json(selection.stdout), audit)
            result["exact_draft_pr_head_verified"] = head
        else:
            result["exact_draft_pr_head_verified"] = "NOT_CHECKED"
    except (OSError, AuditError, UnicodeDecodeError, ValueError) as exc:
        print(json.dumps({"status": "REVIEW_INPUT_REJECTED", "reason": str(exc)}, sort_keys=True))
        return 3
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
