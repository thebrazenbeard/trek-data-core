#!/usr/bin/env python3
"""Compile bounded B005 DS9 publisher episode-guide observations, fail-closed."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b005-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b005-20261103/records.json")
ROOT_FIELDS = {"schema_version", "data_status", "observed_utc_date", "source_family",
               "source_raw_bytes_pinned", "admission_effect", "coverage_effect", "rows"}
ROW_FIELDS = {"row_id", "series", "cards", "title_resolution",
              "publisher_brief_description_state", "original_synopsis_draft"}
CARD_FIELDS = {"season", "episode", "official_title"}
TITLE_CASE_EXCEPTIONS = {"lead:0052": "Return To Grace", "lead:0059": "The House Of Quark"}
CONFLICT = "lead:0054"
PINNED_OFFICIAL_SLOTS = (
    (4, 12), (4, 14), (5, 6), (4, 3), (4, 6), (1, 5), (1, 3), (1, 4),
    (3, 3), (2, 2), (2, 6), (3, 8), (2, 8), (2, 1), (2, 25), (7, 16),
)


def read(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized B005 input")
    raw = target.read_bytes()

    def unique(pairs):
        data = {}
        for k, v in pairs:
            if k in data:
                raise ValueError("duplicate JSON object key")
            data[k] = v
        return data

    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    if not isinstance(data, dict):
        raise ValueError("B005 input must be a JSON object")
    return data, raw


def compile_records(catalog: dict, catalog_raw: bytes, declared: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("catalog not exact unadmitted source-local directory")
    if (set(declared) != ROOT_FIELDS or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "RENDERED_PRIMARY_EPISODE_GUIDE_CARDS_WITH_PUBLISHER_BLURB_CONFLICT"
            or declared["observed_utc_date"] != "2026-11-03"
            or declared["source_family"] != "paramount_corporate_publisher_family"
            or declared["source_raw_bytes_pinned"] is not False
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or not isinstance(declared["rows"], list) or len(declared["rows"]) != 16):
        raise ValueError("unreviewed B005 envelope")
    by_id = {r["row_id"]: r for r in catalog["rows"]}
    if len(by_id) != 1214:
        raise ValueError("source-local directory contains duplicate identifiers")
    expected_ids = [f"lead:{i:04d}" for i in range(51, 67)]
    if [row.get("row_id") for row in declared["rows"]] != expected_ids:
        raise ValueError("not exact B005 16-row frontier")
    used_slots = set()
    records = []
    for item in declared["rows"]:
        if not isinstance(item, dict) or set(item) != ROW_FIELDS or item["series"] != "DS9":
            raise ValueError("unexpected B005 guide-card fields or series")
        source = by_id[item["row_id"]]
        if (source.get("context") != "DS9" or source.get("medium") != "EPISODE"
                or source.get("source_group") != "wikidata:wdqs"
                or source.get("candidate_kind") != "WIKIDATA_EPISODE"
                or source.get("verification_status") != "UNVERIFIED_METADATA"
                or source.get("admission_effect") != "NONE" or source.get("coverage_effect") != "NONE"):
            raise ValueError("source-local row provenance or research status changed")
        cards = item["cards"]
        if not isinstance(cards, list) or len(cards) != 1:
            raise ValueError("B005 must have exactly one official card candidate per row")
        card = cards[0]
        if not isinstance(card, dict) or set(card) != CARD_FIELDS:
            raise ValueError("malformed official card")
        season, episode = card["season"], card["episode"]
        if (type(season) is not int or not 1 <= season <= 7 or type(episode) is not int
                or not 1 <= episode <= {1: 20, 2: 26, 3: 26, 4: 26, 5: 26, 6: 26, 7: 25}[season]):
            raise ValueError("invalid official DS9 season/episode slot")
        slot = (season, episode)
        if slot in used_slots:
            raise ValueError("official DS9 slot double-claimed")
        used_slots.add(slot)
        if slot != PINNED_OFFICIAL_SLOTS[len(records)]:
            raise ValueError("official guide row-to-slot binding changed without review")
        if not isinstance(card["official_title"], str):
            raise ValueError("official title not string")
        if item["row_id"] in TITLE_CASE_EXCEPTIONS:
            if (item["title_resolution"] != "CASE_VARIANT_UNRESOLVED"
                    or card["official_title"] != TITLE_CASE_EXCEPTIONS[item["row_id"]]
                    or card["official_title"].casefold() != source["title"].casefold()):
                raise ValueError("source-publisher case variant silently promoted")
        elif item["title_resolution"] != "EXACT" or card["official_title"] != source["title"]:
            raise ValueError("false exact official title match")
        summary = item["original_synopsis_draft"]
        if item["row_id"] == CONFLICT:
            if (item["publisher_brief_description_state"] != "PUBLISHER_DESCRIPTION_SLOT_CONFLICT_UNRESOLVED"
                    or summary is not None or (season, episode, card["official_title"]) != (4, 3, "The Visitor")):
                raise ValueError("The Visitor card blurb conflict must remain unresolved and synopsis withheld")
            synopsis_status = "WITHHELD_PUBLISHER_DESCRIPTION_MISASSOCIATED"
        else:
            if (item["publisher_brief_description_state"] != "READ_CARD_DESCRIPTION_CONSISTENT"
                    or not isinstance(summary, str) or not 55 <= len(summary) <= 220
                    or not summary.endswith(".") or "\n" in summary):
                raise ValueError("no source-grounded pending human-review synopsis")
            synopsis_status = "ORIGINAL_BLURB_PARAPHRASE_DRAFT_PENDING_HUMAN_REVIEW"
        records.append({
            "source_local_row_id": item["row_id"],
            "source_local_title": source["title"],
            "source_local_series_context": item["series"],
            "source_local_locator": source["source_locator"],
            "source_local_family": "wikidata_collaborative_derivative",
            "publisher_family": declared["source_family"],
            "official_card_candidates": [{
                "title": card["official_title"],
                "season": season,
                "episode": episode,
                "guide_url": f"https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/{season}/",
                "guide_page_series_label": "Star Trek: Deep Space Nine",
                "card_locator": f"Episode Guide > {card['official_title']} > S{season} E{episode} > short description",
                "brief_description_actually_read": True,
                "publisher_source_body_sha256": None,
            }],
            "title_resolution": item["title_resolution"],
            "publisher_brief_description_state": item["publisher_brief_description_state"],
            "observed_utc_date": declared["observed_utc_date"],
            "source_representation": "OFFICIAL_RENDERED_CARD_TEXT_UNPINNED",
            "original_synopsis_draft": summary,
            "synopsis_status": synopsis_status,
            "public_synopsis_approval": "NONE",
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    statuses = [r["title_resolution"] for r in records]
    return {
        "schema_version": "1.0.0",
        "data_status": "B005_PROPOSAL_ONLY_PRIMARY_RENDERED_CARD_TRIAGE",
        "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest(),
        "observation_manifest_sha256": hashlib.sha256(
            json.dumps(declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "summary": {
            "source_local_row_cases": len(records),
            "actual_official_cards_read": len(records),
            "exact_title_cases": statuses.count("EXACT"),
            "unresolved_case_variant_cases": statuses.count("CASE_VARIANT_UNRESOLVED"),
            "unresolved_publisher_description_conflict_cases": sum(r["source_local_row_id"] == CONFLICT for r in records),
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
    target = ROOT / OUTPUT
    if args.check:
        if target.is_symlink() or not target.is_file() or target.read_bytes() != encoded:
            raise SystemExit("B005_STALE_OR_UNREVIEWED_DERIVATIVE")
    else:
        if target.is_symlink():
            raise SystemExit("B005_SYMLINK_OUTPUT_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("B005_OK: 16 DS9 official publisher cards, 14 exact, 2 case variants, "
          "1 blurb conflict, 15 synopsis drafts pending; zero admission")


if __name__ == "__main__":
    main()
