#!/usr/bin/env python3
"""Fail-closed DS9/Voyager B006 source-local official guide-card compiler."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_episode_guide_rechecks_b005 import read


ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b006-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b006-20261103/records.json")
ROOT_FIELDS = {"schema_version", "data_status", "observed_utc_date", "source_family", "source_raw_bytes_pinned", "admission_effect", "coverage_effect", "rows"}
ROW_FIELDS = {"row_id", "series", "cards", "title_resolution", "original_synopsis_draft"}
CARD_FIELDS = {"season", "episode", "official_title"}
CASE_EXCEPTIONS = {"lead:0069": "Favor The Bold", "lead:0073": "Time And Again"}
COMBINED = "lead:0074"
PUBLISHER_SLOTS = (
    ("DS9", 7, 1), ("DS9", 6, 20), ("DS9", 6, 5),
    ("VOY", 7, 19), ("VOY", 1, 6), ("VOY", 4, 21), ("VOY", 1, 4),
    ("VOY", 1, 1), ("VOY", 5, 4), ("VOY", 2, 2), ("VOY", 2, 20),
    ("VOY", 6, 13), ("VOY", 6, 18), ("VOY", 1, 15), ("VOY", 3, 11),
    ("VOY", 5, 20),
)
GUIDES = {"DS9": ("star_trek_deep_space_nine", "Star Trek: Deep Space Nine"),
          "VOY": ("star_trek_voyager", "Star Trek: Voyager")}


def compile_records(catalog: dict, catalog_raw: bytes, declared: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("catalog is not exact unadmitted source-local directory")
    if (set(declared) != ROOT_FIELDS or declared["schema_version"] != "1.0.0"
            or declared["data_status"] != "RENDERED_PRIMARY_GUIDE_CARDS_MULTIPART_LISTING_UNRESOLVED"
            or declared["observed_utc_date"] != "2026-11-03"
            or declared["source_family"] != "paramount_corporate_publisher_family"
            or declared["source_raw_bytes_pinned"] is not False
            or declared["admission_effect"] != "NONE" or declared["coverage_effect"] != "NONE"
            or not isinstance(declared["rows"], list) or len(declared["rows"]) != 16):
        raise ValueError("unreviewed B006 envelope")
    by_id = {r["row_id"]: r for r in catalog["rows"]}
    if len(by_id) != 1214 or [r.get("row_id") for r in declared["rows"]] != [f"lead:{i:04d}" for i in range(67, 83)]:
        raise ValueError("directory duplicate IDs or incorrect B006 frontier")
    records = []
    for index, row in enumerate(declared["rows"]):
        if not isinstance(row, dict) or set(row) != ROW_FIELDS or row["series"] not in GUIDES:
            raise ValueError("unexpected B006 observation fields")
        source = by_id[row["row_id"]]
        if (source.get("context") != row["series"] or source.get("medium") != "EPISODE"
                or source.get("source_group") != "wikidata:wdqs" or source.get("candidate_kind") != "WIKIDATA_EPISODE"
                or source.get("verification_status") != "UNVERIFIED_METADATA"
                or source.get("admission_effect") != "NONE" or source.get("coverage_effect") != "NONE"):
            raise ValueError("source-local discovery provenance altered")
        cards = row["cards"]
        if not isinstance(cards, list) or len(cards) != 1 or not isinstance(cards[0], dict) or set(cards[0]) != CARD_FIELDS:
            raise ValueError("not exactly one supported official guide card")
        card = cards[0]
        slot = (row["series"], card["season"], card["episode"])
        if (any(type(n) is not int for n in slot[1:]) or slot != PUBLISHER_SLOTS[index]
                or not isinstance(card["official_title"], str)):
            raise ValueError("incorrect source-local publisher episode slot/title type")
        if row["row_id"] in CASE_EXCEPTIONS:
            if (row["title_resolution"] != "CASE_VARIANT_UNRESOLVED"
                    or card["official_title"] != CASE_EXCEPTIONS[row["row_id"]]
                    or card["official_title"].casefold() != source["title"].casefold()):
                raise ValueError("publisher capitalization variant cannot be silently resolved")
        elif row["row_id"] == COMBINED:
            if (row["title_resolution"] != "COMBINED_MULTIPART_LISTING_UNRESOLVED"
                    or source["title"] != "Caretaker"
                    or card["official_title"] != "Caretaker, Part 1 & 2"
                    or row["original_synopsis_draft"] is not None):
                raise ValueError("Caretaker multipart identity and synopsis must remain unresolved")
        elif row["title_resolution"] != "EXACT" or card["official_title"] != source["title"]:
            raise ValueError("false exact title match")
        synopsis = row["original_synopsis_draft"]
        if row["row_id"] != COMBINED and (not isinstance(synopsis, str)
                or not 55 <= len(synopsis) <= 220 or not synopsis.endswith(".") or "\n" in synopsis):
            raise ValueError("original concise source-grounded synopsis draft missing")
        show_slug, label = GUIDES[row["series"]]
        records.append({
            "source_local_row_id": row["row_id"],
            "source_local_title": source["title"],
            "source_local_series_context": row["series"],
            "source_local_locator": source["source_locator"],
            "source_local_family": "wikidata_collaborative_derivative",
            "publisher_family": declared["source_family"],
            "official_card_candidates": [{
                "title": card["official_title"], "season": card["season"], "episode": card["episode"],
                "guide_url": f"https://www.paramountplus.com/shows/{show_slug}/episodes/{card['season']}/",
                "guide_page_series_label": label,
                "card_locator": f"Episode Guide > {card['official_title']} > S{card['season']} E{card['episode']} > short description",
                "brief_description_actually_read": True,
                "publisher_source_body_sha256": None,
            }],
            "title_resolution": row["title_resolution"],
            "observed_utc_date": declared["observed_utc_date"],
            "source_representation": "OFFICIAL_RENDERED_CARD_TEXT_UNPINNED",
            "original_synopsis_draft": synopsis,
            "synopsis_status": ("WITHHELD_COMBINED_MULTIPART_WORK_IDENTITY_UNRESOLVED" if synopsis is None
                                else "ORIGINAL_BLURB_PARAPHRASE_DRAFT_PENDING_HUMAN_REVIEW"),
            "public_synopsis_approval": "NONE",
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    resolutions = [r["title_resolution"] for r in records]
    return {
        "schema_version": "1.0.0",
        "data_status": "B006_PROPOSAL_ONLY_PRIMARY_RENDERED_CARD_TRIAGE",
        "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest(),
        "observation_manifest_sha256": hashlib.sha256(json.dumps(declared, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "summary": {
            "source_local_row_cases": len(records),
            "actual_official_cards_read": len(records),
            "exact_title_cases": resolutions.count("EXACT"),
            "unresolved_case_variant_cases": resolutions.count("CASE_VARIANT_UNRESOLVED"),
            "unresolved_combined_multipart_identity_cases": resolutions.count("COMBINED_MULTIPART_LISTING_UNRESOLVED"),
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
            raise SystemExit("B006_STALE_OR_UNREVIEWED_DERIVATIVE")
    else:
        if target.is_symlink():
            raise SystemExit("B006_SYMLINK_OUTPUT_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("B006_OK: 16 DS9/VOY guide cards; 13 exact, 2 case variants, "
          "1 combined multipart held, 15 synopsis drafts pending, zero admission")


if __name__ == "__main__":
    main()
