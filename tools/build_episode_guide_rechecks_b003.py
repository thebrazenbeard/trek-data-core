#!/usr/bin/env python3
"""Deterministic triage for source-local TOS/TAS official rendered guide cards B003."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b003-20261103/observations.json")
OUT = Path("proposals/verification/episode-guide-rechecks-b003-20261103/records.json")
EXPECTED_FIELDS = {"row_id", "series", "season", "episode", "official_title", "title_check", "original_synopsis_draft"}
GUIDES = {
    "TOS": ("https://www.paramountplus.com/shows/star_trek/episodes/{}/", "Star Trek"),
    "TAS": ("https://www.paramountplus.com/shows/star_trek_animated/episodes/{}/", "Star Trek The Animated Series"),
}
# 30 is intentional: Paramount+ lists Operation: Annihilate! as TOS S1E30;
# B002's 29-slot assertion is insufficient for a future full-series batch.
SEASON_UPPER = {"TOS": {1: 30, 2: 26, 3: 24}, "TAS": {1: 16, 2: 6}}


def read(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized source input")
    raw = target.read_bytes()
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate key in JSON input")
            out[key] = value
        return out
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError("expected top-level object")
    return data, raw


def valid_official_slot(series: str, season: int, episode: int) -> bool:
    return (series in SEASON_UPPER and type(season) is int and season in SEASON_UPPER[series]
            and type(episode) is int and 1 <= episode <= SEASON_UPPER[series][season])


def compile_records(catalog: dict, raw_catalog: bytes, source: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("not exact current source-local catalog")
    if (set(source) != {"schema_version", "data_status", "observed_utc_date", "source_family",
                       "raw_publisher_source_bytes_pinned", "admission_effect", "coverage_effect", "rows"}
            or source["schema_version"] != "1.0.0"
            or source["data_status"] != "RENDERED_OFFICIAL_TOS_TAS_EPISODE_GUIDE_CARDS_UNPINNED"
            or source["observed_utc_date"] != "2026-11-03"
            or source["source_family"] != "paramount_corporate_publisher_family"
            or source["raw_publisher_source_bytes_pinned"] is not False
            or source["admission_effect"] != "NONE" or source["coverage_effect"] != "NONE"
            or not isinstance(source["rows"], list) or len(source["rows"]) != 16):
        raise ValueError("B003 envelope unsound or beyond bounded size")
    ids = [f"lead:{n:04d}" for n in range(19, 35)]
    if [obs.get("row_id") for obs in source["rows"]] != ids:
        raise ValueError("not exact proposed next 16 source-local leads")
    accepted = {row["row_id"]: row for row in catalog["rows"]}
    if len(accepted) != 1214:
        raise ValueError("duplicate source-local identifiers in accepted directory")
    result = []
    used_slots = set()
    for obs in source["rows"]:
        if not isinstance(obs, dict) or set(obs) != EXPECTED_FIELDS:
            raise ValueError("unexpected source observation fields")
        row = accepted[obs["row_id"]]
        if (row.get("source_group") != "wikidata:wdqs" or row.get("context") != obs["series"]
                or row.get("medium") != "EPISODE" or row.get("candidate_kind") != "WIKIDATA_EPISODE"
                or row.get("verification_status") != "UNVERIFIED_METADATA"
                or row.get("admission_effect") != "NONE" or row.get("coverage_effect") != "NONE"):
            raise ValueError("source-local row changed lineage or admission")
        season, episode, series = obs["season"], obs["episode"], obs["series"]
        if not valid_official_slot(series, season, episode):
            raise ValueError("invalid official episode ordinal/series boundary")
        slot = (series, season, episode)
        if slot in used_slots:
            raise ValueError("duplicate official card assignment")
        used_slots.add(slot)
        exact = obs["official_title"] == row["title"]
        if exact:
            if obs["title_check"] != "EXACT":
                raise ValueError("manufactured title mismatch")
        elif not (obs["row_id"] == "lead:0029" and row["title"] == "One of Our Planets Is Missing"
                  and obs["official_title"] == "One of Our Planets is Missing"
                  and obs["title_check"] == "CASE_VARIANT_UNRESOLVED"):
            raise ValueError("unapproved source/publisher title divergence")
        synopsis = obs["original_synopsis_draft"]
        if (not isinstance(synopsis, str) or not 55 <= len(synopsis) <= 220
                or not synopsis.endswith(".") or "\n" in synopsis
                or synopsis.casefold().strip(". ") == row["title"].casefold()):
            raise ValueError("no valid original short synopsis draft")
        template, page_label = GUIDES[series]
        result.append({
            "source_local_row_id": obs["row_id"],
            "source_local_title": row["title"],
            "source_local_locator": row["source_locator"],
            "source_local_family": "wikidata_collaborative_derivative",
            "source_local_context": series,
            "official_guide_url": template.format(season),
            "official_page_series_label": page_label,
            "official_provenance_family": source["source_family"],
            "observed_title": obs["official_title"],
            "observed_season": season,
            "observed_episode": episode,
            "guide_card_locator": f"Episode Guide > {obs['official_title']} > S{season} E{episode} > short description",
            "title_check": "EXACT_RENDERED_OFFICIAL_CARD_MATCH" if exact else "UNRESOLVED_CASE_VARIANT",
            "slot_check": "OBSERVED_OFFICIAL_PAGE_NOT_SOURCE_LOCAL_ROW_COMPARED",
            "publisher_brief_description_actually_read": True,
            "metadata_status": "RENDERED_OFFICIAL_GUIDE_CARD_UNPINNED",
            "observed_utc_date": source["observed_utc_date"],
            "raw_page_body_sha256": None,
            "original_synopsis_draft": synopsis,
            "synopsis_status": "ORIGINAL_BRIEF_DESCRIPTION_PARAPHRASE_DRAFT_PENDING_HUMAN_REVIEW",
            "public_synopsis_approval": "NONE",
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    unmatched = sum(r["title_check"] != "EXACT_RENDERED_OFFICIAL_CARD_MATCH" for r in result)
    return {
        "schema_version": "1.0.0",
        "data_status": "PROPOSAL_ONLY_OFFICIAL_GUIDE_CARD_CHECKS_B003",
        "source_directory_sha256": hashlib.sha256(raw_catalog).hexdigest(),
        "declared_observations_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "summary": {
            "source_local_records_checked_from_rendered_guides": len(result),
            "official_title_exact_matches": len(result) - unmatched,
            "unresolved_case_variant": unmatched,
            "tos_cards": sum(r["source_local_context"] == "TOS" for r in result),
            "tas_cards": sum(r["source_local_context"] == "TAS" for r in result),
            "original_synopsis_drafts_pending_human_review": len(result),
            "public_synopses_approved": 0,
            "raw_page_bodies_byte_pinned": 0,
            "governed_evidence_or_works_admitted": 0,
        },
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "rows": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, raw = read(CATALOG)
    observations, _ = read(OBS)
    derived = compile_records(catalog, raw, observations)
    bytes_out = (json.dumps(derived, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    target = ROOT / OUT
    if args.check:
        if target.is_symlink() or not target.is_file() or target.read_bytes() != bytes_out:
            raise SystemExit("EPISODE_B003_STALE_OR_TAMPERED")
    else:
        if target.is_symlink():
            raise SystemExit("EPISODE_B003_SYMLINK_OUTPUT_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes_out)
    print("EPISODE_B003_OK: 16 TOS/TAS cards, 15 literal titles, 1 case variant, 16 synopsis drafts pending, zero admission")


if __name__ == "__main__":
    main()
