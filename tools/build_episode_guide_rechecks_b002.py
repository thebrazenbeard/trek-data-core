#!/usr/bin/env python3
"""Compile independently reviewable TOS official-guide metadata observations, never admission."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b002-20261103/observations.json")
OUT = Path("proposals/verification/episode-guide-rechecks-b002-20261103/records.json")
KEYS = {"row_id", "guide_season", "guide_episode", "official_title", "title_match", "original_synopsis_draft"}
URL_TEMPLATE = "https://www.paramountplus.com/shows/star_trek/episodes/{}/"


def read(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized source/observation input")
    raw = target.read_bytes()
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON object required")
    return data, raw


def compile_observations(catalog: dict, raw_catalog: bytes, declared: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("not the pinned unadmitted discovery input")
    if (set(declared) != {"schema_version", "data_status", "admission_effect", "coverage_effect",
                         "raw_source_bytes_pinned", "observed_at_utc_date", "source_family", "observations"}
            or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "BOUNDED_PRIMARY_RENDERED_EPISODE_GUIDE_CARD_OBSERVATIONS_UNPINNED"
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or declared["raw_source_bytes_pinned"] is not False
            or declared["observed_at_utc_date"] != "2026-11-03"
            or declared["source_family"] != "paramount_corporate_publisher_family"
            or not isinstance(declared["observations"], list) or len(declared["observations"]) != 16):
        raise ValueError("unknown/unreviewed bounded observation envelope")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    if len(by_id) != 1214:
        raise ValueError("duplicate accepted discovery row identity")
    expected_ids = [f"lead:{n:04d}" for n in range(3, 19)]
    if [obs.get("row_id") for obs in declared["observations"]] != expected_ids:
        raise ValueError("not the declared bounded initial-16 episode queue")
    seen_slots = set()
    compiled = []
    for obs in declared["observations"]:
        if not isinstance(obs, dict) or set(obs) != KEYS:
            raise ValueError("unrecognized observation fields")
        row = by_id[obs["row_id"]]
        if (row.get("medium") != "EPISODE" or row.get("context") != "TOS"
                or row.get("source_group") != "wikidata:wdqs"
                or row.get("candidate_kind") != "WIKIDATA_EPISODE"
                or row.get("verification_status") != "UNVERIFIED_METADATA"
                or row.get("admission_effect") != "NONE" or row.get("coverage_effect") != "NONE"):
            raise ValueError("source row is not unadmitted TOS Wikidata discovery")
        season, episode = obs["guide_season"], obs["guide_episode"]
        if (type(season) is not int or season not in (1, 2, 3)
                or type(episode) is not int or not 1 <= episode <= {1: 29, 2: 26, 3: 24}[season]):
            raise ValueError("invalid/unsupported official season-and-episode slot")
        slot = (season, episode)
        if slot in seen_slots:
            raise ValueError("same official episode slot assigned to different source-local rows")
        seen_slots.add(slot)
        matched = obs["official_title"] == row["title"]
        if matched:
            if obs["title_match"] != "EXACT":
                raise ValueError("false source title mismatch")
        elif (obs["row_id"] != "lead:0006" or row["title"] != "Charlie X"
              or obs["official_title"] != 'Charlie "X"'
              or obs["title_match"] != "PUNCTUATION_VARIANT_UNRESOLVED"):
            raise ValueError("unapproved official/source title divergence")
        summary = obs["original_synopsis_draft"]
        if (not isinstance(summary, str) or not 55 <= len(summary) <= 220
                or not summary.endswith(".") or "\n" in summary
                or summary.casefold().strip(". ") == row["title"].casefold()):
            raise ValueError("unreviewed/empty/oversized original summary draft")
        official_url = URL_TEMPLATE.format(season)
        compiled.append({
            "source_local_row_id": obs["row_id"],
            "source_local_title": row["title"],
            "source_local_locator": row["source_locator"],
            "source_local_family": "wikidata_collaborative_derivative",
            "official_guide_url": official_url,
            "official_guide_family": "paramount_corporate_publisher_family",
            "observed_official_title": obs["official_title"],
            "observed_guide_series_label": "Star Trek",
            "source_local_series_context": "TOS",
            "observed_season": season,
            "observed_episode": episode,
            "guide_card_locator": f"Episode Guide > {obs['official_title']} > S{season} E{episode} > brief description",
            "title_check": "EXACT_RENDERED_CARD_MATCH" if matched else "SOURCE_TITLE_VARIANT_REQUIRES_RECONCILIATION",
            "season_episode_check": "OBSERVED_OFFICIAL_CARD_NOT_IN_WIKIDATA_ROW",
            "publisher_brief_description_read": True,
            "metadata_check_state": "RENDERED_OFFICIAL_GUIDE_CARD_UNPINNED",
            "observed_at_utc_date": declared["observed_at_utc_date"],
            "rendered_source_representation": "WEB_RENDERED_TEXT_NOT_RAW_PAGE_CUSTODY",
            "raw_source_sha256": None,
            "original_synopsis_draft": summary,
            "synopsis_state": "ORIGINAL_PARAPHRASE_DRAFT_NOT_PUBLICATION_APPROVED",
            "human_review": "PENDING",
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    variants = sum(row["title_check"] != "EXACT_RENDERED_CARD_MATCH" for row in compiled)
    return {
        "schema_version": "1.0.0",
        "data_status": "PROPOSAL_ONLY_RENDERED_EPISODE_GUIDE_RECHECKS",
        "catalog_sha256": hashlib.sha256(raw_catalog).hexdigest(),
        "declared_observations_sha256": hashlib.sha256(
            json.dumps(declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "summary": {
            "source_local_card_observations": len(compiled),
            "exact_official_title_matches": len(compiled) - variants,
            "unresolved_title_variants": variants,
            "brief_descriptions_actually_read_in_rendered_guide": len(compiled),
            "original_synopsis_drafts_pending_human_review": len(compiled),
            "publicly_approved_synopses": 0,
            "raw_page_bodies_byte_pinned": 0,
            "governed_works_evidence_admitted": 0,
            "unrechecked_rows_in_full_1214_directory_before_this_batch": 1206,
        },
        "rows": compiled,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="reject stale or changed deterministic output")
    args = parser.parse_args()
    catalog, raw = read(SOURCE)
    declared, _ = read(OBS)
    result = compile_observations(catalog, raw, declared)
    encoded = (json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
    dest = ROOT / OUT
    if args.check:
        if not dest.is_file() or dest.is_symlink() or dest.read_bytes() != encoded:
            raise SystemExit("EPISODE_B002_DERIVATIVE_STALE_OR_MUTATED")
    else:
        if dest.is_symlink():
            raise SystemExit("EPISODE_B002_OUTPUT_SYMLINK_REFUSED")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(encoded)
    print("EPISODE_B002_OK: 16 rendered official title/slot/brief descriptions; 15 exact, "
          "1 title variant, 16 original synopsis drafts PENDING; zero admitted")


if __name__ == "__main__":
    main()
