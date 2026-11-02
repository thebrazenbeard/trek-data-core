#!/usr/bin/env python3
"""Read-only consistency audit of the two public Explorer evidence tiers.

This checks exported JSON relationships, not publisher truth, source inspection,
coverage denominators, or independent admission authority.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

if __package__:
    from . import build_research_leads
else:
    import build_research_leads


HASH = re.compile(r"sha256:[0-9a-f]{64}\Z")
QID = re.compile(r"Q[1-9][0-9]{0,15}\Z")


def _positive_number(value: object) -> bool:
    return type(value) is int and 1 <= value <= 9999


def _object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def audit_artifacts(catalog: dict, index: dict, leads: dict) -> dict:
    """Validate provenance-tier boundaries and joins, returning only counts."""
    catalog = _object(catalog, "catalog")
    index = _object(index, "canonical Explorer index")
    leads = _object(leads, "research leads index")
    if catalog.get("admission_status") != "DISPLAY_CATALOG_ONLY":
        raise ValueError("catalog must remain display-only")
    missions = catalog.get("missions")
    if not isinstance(missions, list) or not missions:
        raise ValueError("catalog must contain Missions")
    ids = [m.get("id") for m in missions if isinstance(m, dict)]
    if (len(ids) != len(missions) or any(not isinstance(i, str) or not i for i in ids)
            or len(ids) != len(set(ids))):
        raise ValueError("catalog contains invalid or duplicate Mission identities")
    expected_missions = sorted(missions, key=lambda m: m["title"].casefold())
    if index.get("schema_version") != "1.0.0" or index.get("missions") != expected_missions:
        raise ValueError("Explorer Mission catalog drift")
    build = _object(index.get("build"), "Explorer build receipt")
    status, projection_hash = build.get("data_status"), build.get("projection_hash")
    if not ((status == "MISSION_CATALOG_ONLY" and projection_hash is None)
            or (status == "GOVERNED_PROJECTION" and isinstance(projection_hash, str)
                and HASH.fullmatch(projection_hash))):
        raise ValueError("Explorer build status or projection receipt is invalid")
    briefings, records = index.get("briefings"), index.get("records")
    if not isinstance(briefings, list) or not isinstance(records, list):
        raise ValueError("Explorer briefings and records must be arrays")
    if status == "MISSION_CATALOG_ONLY" and (briefings or records):
        raise ValueError("display-only Explorer cannot expose admitted records")

    briefing_by_id = {}
    briefing_counts = Counter()
    for item in briefings:
        item = _object(item, "Mission Briefing")
        bid, mission_id = item.get("id"), item.get("mission_id")
        if (not isinstance(bid, str) or not bid or bid in briefing_by_id
                or mission_id not in ids or item.get("work_id") != bid
                or item.get("admission_status") != "EVIDENCED_IN_PROJECTION"):
            raise ValueError("invalid or duplicate admitted Mission Briefing")
        for key in ("season", "episode"):
            if item.get(key) is not None and not _positive_number(item[key]):
                raise ValueError("invalid Mission Briefing episode number")
        briefing_by_id[bid] = item
        briefing_counts[mission_id] += 1
    record_ids = set()
    for item in records:
        item = _object(item, "continuity record")
        rid, mission_id, bid = item.get("id"), item.get("mission_id"), item.get("briefing_id")
        if not isinstance(rid, str) or not rid or rid in record_ids:
            raise ValueError("invalid or duplicate projected record")
        record_ids.add(rid)
        if mission_id is not None and mission_id not in ids:
            raise ValueError("projected record links to an unknown Mission")
        if bid is not None and (bid not in briefing_by_id or
                                briefing_by_id[bid]["mission_id"] != mission_id):
            raise ValueError("projected record has an orphan or cross-Mission Briefing link")

    if (leads.get("schema_version") != "2.0.0"
            or leads.get("data_status") != "CANDIDATE_DISCOVERY_ONLY"
            or leads.get("source_policy") != "EXTERNAL_METADATA_ONLY"
            or leads.get("coverage_effect") != "NONE"):
        raise ValueError("research leads cannot claim canonical admission or coverage")
    candidates = leads.get("leads")
    if (not isinstance(candidates, list)
            or type(leads.get("lead_count")) is not int
            or leads["lead_count"] != len(candidates)):
        raise ValueError("candidate lead count does not match the rows")
    if leads.get("held_candidate_count") != 2:
        raise ValueError("Enterprise arc/umbrella holds are not preserved")
    identities = set()
    lead_counts = Counter()
    for item in candidates:
        item = _object(item, "research lead")
        mission_id = item.get("mission_id")
        if mission_id not in ids or item.get("verification_status") != "UNVERIFIED_METADATA":
            raise ValueError("research lead has unknown Mission or false verification")
        if item.get("source_type") == "WIKIDATA_METADATA":
            qid = item.get("episode_qid")
            if (not isinstance(qid, str) or not QID.fullmatch(qid)
                    or item.get("independence_group") != "wikidata:wdqs"
                    or (mission_id == "ent" and qid in ("Q56247746", "Q866375"))):
                raise ValueError("invalid Wikidata lead or held Enterprise identity")
            identity = ("wikidata", qid)
        elif item.get("source_type") == "PUBLISHER_EPISODE_SLOT_METADATA":
            season, episode = item.get("season_number"), item.get("episode_number")
            if (not _positive_number(season) or not _positive_number(episode)
                    or item.get("independence_group") != "publisher:paramount"):
                raise ValueError("invalid publisher episode slot or independence group")
            identity = ("publisher", mission_id, season, episode)
        else:
            raise ValueError("unknown candidate source type")
        if identity in identities:
            raise ValueError("duplicate research candidate identity")
        identities.add(identity)
        lead_counts[mission_id] += 1
    if (type(leads.get("sampled_missions_count")) is not int
            or leads["sampled_missions_count"] != len(lead_counts)):
        raise ValueError("sampled Mission count does not match candidates")
    return {
        "audit_status": "PUBLIC_INDEX_RELATIONS_CONSISTENT",
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "projection_status": status,
        "missions": len(ids),
        "projected_records": len(records),
        "unverified_research_leads": len(candidates),
        "per_mission": [
            {"mission_id": mid, "admitted_briefings": briefing_counts[mid],
             "unverified_leads": lead_counts[mid]}
            for mid in ids
        ],
    }


def audit_directory(root: Path) -> dict:
    values = []
    for name in ("registry/mission_catalog.json", "explorer/index.json", "explorer/research-leads.json"):
        raw = build_research_leads.safe_read(root, Path(name))
        values.append(build_research_leads._strict_json(raw, name))
    return audit_artifacts(*values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        report = audit_directory(args.repo_root)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"RESEARCH_LEADS_AUDIT_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
