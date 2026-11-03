#!/usr/bin/env python3
"""Deterministic guide-card review B004, with multipart work identity fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b004-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b004-20261103/records.json")
SLOTS = {"TAS": {1:16,2:6}, "TNG":{1:26,2:22,3:26,4:26,5:26,6:26,7:25}, "DS9":{1:20,2:26,3:26,4:26,5:26,6:26,7:25}}
GUIDES = {
    "TAS": ("star_trek_animated", "Star Trek The Animated Series"),
    "TNG": ("star_trek_the_next_generation", "Star Trek: The Next Generation"),
    "DS9": ("star_trek_deep_space_nine", "Star Trek: Deep Space Nine"),
}
ROOT_FIELDS = {"schema_version", "data_status", "observed_utc_date", "source_family",
               "source_raw_bytes_pinned", "admission_effect", "coverage_effect", "rows"}
ROW_FIELDS = {"row_id", "series", "cards", "title_resolution", "original_synopsis_draft"}
CARD_FIELDS = {"season", "episode", "official_title"}


def read(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized B004 input")
    raw = target.read_bytes()
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError("duplicate JSON object key")
            out[k] = v
        return out
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError("B004 input must be a JSON object")
    return data, raw


def valid_slot(series: str, season: int, episode: int) -> bool:
    return series in SLOTS and type(season) is int and season in SLOTS[series] and type(episode) is int and 1 <= episode <= SLOTS[series][season]


def compile_records(catalog: dict, catalog_raw: bytes, declared: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("catalog not exact unadmitted source-local directory")
    if (set(declared) != ROOT_FIELDS or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "RENDERED_PRIMARY_EPISODE_GUIDE_CARDS_WITH_MULTIPART_UNRESOLVED"
            or declared["observed_utc_date"] != "2026-11-03"
            or declared["source_family"] != "paramount_corporate_publisher_family"
            or declared["source_raw_bytes_pinned"] is not False
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or not isinstance(declared["rows"], list) or len(declared["rows"]) != 16):
        raise ValueError("unreviewed B004 envelope")
    by_id = {r["row_id"]: r for r in catalog["rows"]}
    if len(by_id) != 1214:
        raise ValueError("source-local directory contains duplicate identifiers")
    expected_ids = [f"lead:{i:04d}" for i in range(35, 51)]
    if [row.get("row_id") for row in declared["rows"]] != expected_ids:
        raise ValueError("not exact B004 next-16 frontier")
    used_slots = set()
    records = []
    for item in declared["rows"]:
        if not isinstance(item, dict) or set(item) != ROW_FIELDS:
            raise ValueError("unexpected guide-card observation fields")
        source = by_id[item["row_id"]]
        if (source.get("context") != item["series"] or source.get("medium") != "EPISODE"
                or source.get("source_group") != "wikidata:wdqs"
                or source.get("candidate_kind") != "WIKIDATA_EPISODE"
                or source.get("verification_status") != "UNVERIFIED_METADATA"
                or source.get("admission_effect") != "NONE" or source.get("coverage_effect") != "NONE"):
            raise ValueError("source-local row provenance or research status changed")
        cards = item["cards"]
        if not isinstance(cards, list) or len(cards) not in (1, 2):
            raise ValueError("no bounded one- or two-part official title candidates")
        compiled_cards = []
        for card in cards:
            if not isinstance(card, dict) or set(card) != CARD_FIELDS:
                raise ValueError("malformed official episode card")
            season, episode, series = card["season"], card["episode"], item["series"]
            if not valid_slot(series, season, episode):
                raise ValueError("invalid official series season episode slot")
            slot = (series, season, episode)
            if slot in used_slots:
                raise ValueError("different source rows claim same official episode slot")
            used_slots.add(slot)
            show_slug, show_label = GUIDES[series]
            compiled_cards.append({
                "title": card["official_title"],
                "season": season,
                "episode": episode,
                "guide_url": f"https://www.paramountplus.com/shows/{show_slug}/episodes/{season}/",
                "guide_page_series_label": show_label,
                "card_locator": f"Episode Guide > {card['official_title']} > S{season} E{episode} > short description",
                "brief_description_actually_read": True,
                "publisher_source_body_sha256": None,
            })
        if item["title_resolution"] == "EXACT":
            if len(cards) != 1 or cards[0]["official_title"] != source["title"]:
                raise ValueError("false exact official title match")
        elif item["title_resolution"] == "PUNCTUATION_VARIANT_UNRESOLVED":
            if (item["row_id"] != "lead:0041" or source["title"] != "Hide and Q"
                    or len(cards) != 1 or cards[0]["official_title"] != 'Hide and "Q"'):
                raise ValueError("unapproved title alias closure")
        elif item["title_resolution"] == "MULTIPART_SOURCE_LOCAL_TARGET_UNRESOLVED":
            if (item["row_id"] != "lead:0042" or source["title"] != "Chain of Command"
                    or [(c["season"], c["episode"], c["official_title"]) for c in cards] !=
                    [(6, 10, "Chain Of Command - Part 1"), (6, 11, "Chain Of Command - Part 2")]
                    or item["original_synopsis_draft"] is not None):
                raise ValueError("multipart Work identity was silently flattened")
        else:
            raise ValueError("unknown title resolution state")
        summary = item["original_synopsis_draft"]
        if item["title_resolution"] != "MULTIPART_SOURCE_LOCAL_TARGET_UNRESOLVED":
            if (not isinstance(summary, str) or not 55 <= len(summary) <= 220
                    or not summary.endswith(".") or "\n" in summary):
                raise ValueError("unreviewed/empty/oversized original synopsis")
        records.append({
            "source_local_row_id": item["row_id"],
            "source_local_title": source["title"],
            "source_local_series_context": item["series"],
            "source_local_locator": source["source_locator"],
            "source_local_family": "wikidata_collaborative_derivative",
            "publisher_family": declared["source_family"],
            "official_card_candidates": compiled_cards,
            "title_resolution": item["title_resolution"],
            "observed_utc_date": declared["observed_utc_date"],
            "source_representation": "OFFICIAL_RENDERED_CARD_TEXT_UNPINNED",
            "original_synopsis_draft": summary,
            "synopsis_status": ("WITHHELD_MULTIPART_WORK_IDENTITY_UNRESOLVED" if summary is None else
                                "ORIGINAL_BLURB_PARAPHRASE_DRAFT_PENDING_HUMAN_REVIEW"),
            "public_synopsis_approval": "NONE",
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    statuses = [r["title_resolution"] for r in records]
    return {
        "schema_version": "1.0.0",
        "data_status": "B004_PROPOSAL_ONLY_PRIMARY_RENDERED_CARD_TRIAGE",
        "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest(),
        "observation_manifest_sha256": hashlib.sha256(
            json.dumps(declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "summary": {
            "source_local_row_cases": len(records),
            "actual_official_cards_read": sum(len(r["official_card_candidates"]) for r in records),
            "exact_title_cases": statuses.count("EXACT"),
            "unresolved_punctuation_alias_cases": statuses.count("PUNCTUATION_VARIANT_UNRESOLVED"),
            "unresolved_multipart_work_identity_cases": statuses.count("MULTIPART_SOURCE_LOCAL_TARGET_UNRESOLVED"),
            "original_synopsis_drafts_pending_human_review": sum(r["original_synopsis_draft"] is not None for r in records),
            "publicly_approved_synopses": 0,
            "pinned_raw_publisher_html_bodies": 0,
            "governed_work_or_evidence_admissions": 0,
        },
        "admission_effect": "NONE", "coverage_effect": "NONE", "rows": records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, raw = read(CATALOG)
    observations, _ = read(OBS)
    result = compile_records(catalog, raw, observations)
    encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    dest = ROOT / OUTPUT
    if args.check:
        if dest.is_symlink() or not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("B004_STALE_OR_UNREVIEWED_DERIVATIVE")
    else:
        if dest.is_symlink():
            raise SystemExit("B004_SYMLINK_OUTPUT_REFUSED")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(encoded)
    print("B004_OK: 16 source cases, 17 publisher cards, 14 exact, 1 punctuation variant, "
          "1 multipart unresolved, 15 synopses pending; zero admission")


if __name__ == "__main__":
    main()
