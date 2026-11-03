#!/usr/bin/env python3
"""Build held B007 source-local guide-card observations; never admit Works."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
SOURCE = Path("proposals/verification/episode-guide-rechecks-b007-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b007-20261103/records.json")
CATALOG_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"

# Title/number/slot observations copied from the first-party rendered guides, not inferred from Wikidata.
CARDS = (
    ("VOY", "Juggernaut", 5, 21),
    ("VOY", "Infinite Regress", 5, 7),
    ("VOY", "Natural Law", 7, 22),
    ("VOY", "Human Error", 7, 18),
    ("VOY", "Basics, Part 2", 3, 1),
    ("VOY", "Future's End, Part 2", 3, 9),
    ("VOY", "Year Of Hell, Part 2", 4, 9),
    ("ENT", "First Flight", 2, 24),
    ("ENT", "Bounty", 2, 25),
    ("ENT", "The Expanse", 2, 26),
    ("ENT", "The Xindi", 3, 1),
    ("ENT", "Dear Doctor", 1, 13),
    ("ENT", "Fallen Hero", 1, 23),
    ("ENT", "Detained", 1, 21),
    ("ENT", "Cold Front", 1, 11),
    ("ENT", "Anomaly", 3, 2),
)
HELD = {"lead:0087", "lead:0088", "lead:0089"}
ROW_KEYS = {
    "row_id", "official_card_title", "season", "episode", "title_resolution",
    "official_card_description_read", "original_synopsis_draft",
}
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "catalog_sha256",
    "observed_date_utc", "source_family", "read_surface", "raw_webpage_bytes_custodied",
    "episode_video_or_transcript_read", "public_synopsis_authorized", "admission_effect",
    "coverage_effect", "rows",
}


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load(path):
    full = ROOT / path
    if full.is_symlink() or not full.is_file() or full.stat().st_size > 4_000_000:
        raise ValueError("source missing, symlinked or oversized")
    raw = full.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys), raw


def compile_records(catalog, catalog_bytes, observations):
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE"
            or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214
            or len(catalog.get("rows", [])) != 1214
            or hashlib.sha256(catalog_bytes).hexdigest() != CATALOG_SHA256):
        raise ValueError("discovery catalog snapshot changed")
    if (not isinstance(observations, dict) or set(observations) != TOP_KEYS
            or observations["schema_version"] != "1.0.0"
            or observations["proposal_id"] != "LIBRARIAN-B007-VOY-ENT-GUIDE-20261103"
            or observations["catalog_sha256"] != CATALOG_SHA256
            or observations["baseline_accepted_main"] != "3c0b37564123166bf38bcfa66f018abc4d5c9996"
            or observations["observed_date_utc"] != "2026-11-03"
            or observations["source_family"] != "paramount_corporate_publisher_family"
            or observations["read_surface"] != "RENDERED_OFFICIAL_PARAMOUNT_PLUS_EPISODE_GUIDE_CARDS"
            or observations["raw_webpage_bytes_custodied"] is not False
            or observations["episode_video_or_transcript_read"] is not False
            or observations["public_synopsis_authorized"] is not False
            or observations["admission_effect"] != "NONE"
            or observations["coverage_effect"] != "NONE"
            or not isinstance(observations["rows"], list) or len(observations["rows"]) != 16):
        raise ValueError("unreviewed B007 source envelope")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    if len(by_id) != 1214:
        raise ValueError("duplicate discovery row ids")
    if [x.get("row_id") for x in observations["rows"]] != [f"lead:{i:04d}" for i in range(83, 99)]:
        raise ValueError("B007 row range altered")

    result = []
    used = set()
    for i, entry in enumerate(observations["rows"]):
        if not isinstance(entry, dict) or set(entry) != ROW_KEYS or entry["official_card_description_read"] is not True:
            raise ValueError("unread or malformed first-party episode card")
        source = by_id[entry["row_id"]]
        medium, title, season, episode = CARDS[i]
        if (source.get("context") != medium or source.get("medium") != "EPISODE"
                or source.get("candidate_kind") != "WIKIDATA_EPISODE"
                or source.get("source_group") != "wikidata:wdqs"
                or source.get("verification_status") != "UNVERIFIED_METADATA"
                or source.get("admission_effect") != "NONE"
                or source.get("coverage_effect") != "NONE"):
            raise ValueError("source-local provenance changed")
        if ((entry["official_card_title"], entry["season"], entry["episode"]) != (title, season, episode)
                or type(entry["season"]) is not int or type(entry["episode"]) is not int):
            raise ValueError("publisher title/slot mismatch")
        slot = (medium, season, episode)
        if slot in used:
            raise ValueError("duplicate publisher slot")
        used.add(slot)
        held = entry["row_id"] in HELD
        if held:
            if (entry["title_resolution"] != "PART_NUMERAL_STYLE_UNRESOLVED"
                    or entry["original_synopsis_draft"] is not None
                    or "Part II" not in source["title"] or "Part 2" not in title):
                raise ValueError("unresolved multipart style silently admitted")
        else:
            synopsis = entry["original_synopsis_draft"]
            if (entry["title_resolution"] != "EXACT_OFFICIAL_CARD_TITLE"
                    or title != source["title"] or not isinstance(synopsis, str)
                    or not 35 <= len(synopsis) <= 350
                    or "http" in synopsis.lower() or "\n" in synopsis):
                raise ValueError("unreviewed synopsis or false exact title")
        guide_slug = "star_trek_voyager" if medium == "VOY" else "enterprise"
        url = f"https://www.paramountplus.com/shows/{guide_slug}/episodes/{season}/"
        result.append({
            "source_local_row_id": entry["row_id"],
            "source_local_title": source["title"],
            "source_local_locator": source["source_locator"],
            "source_local_lineage": "wikidata_collaborative_derivative",
            "source_local_context": medium,
            "official_card": {
                "title": title, "season": season, "episode": episode,
                "guide_url": url,
                "section_locator": f"Episode Guide > {title} > S{season} E{episode} > short description",
                "brief_description_actually_read": True,
                "raw_webpage_sha256": None,
            },
            "title_resolution": entry["title_resolution"],
            "original_synopsis_draft": entry["original_synopsis_draft"],
            "synopsis_publication_status": "HOLD_SOURCE_IDENTITY" if held else "HUMAN_AND_EDITORIAL_REVIEW_PENDING",
            "source_body_custody_status": "NOT_READ_OR_HASHED",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    if sum(x["title_resolution"] == "EXACT_OFFICIAL_CARD_TITLE" for x in result) != 13:
        raise ValueError("exact match tally drift")
    return {
        "data_status": "B007_RENDERED_PUBLISHER_METADATA_PROPOSAL_ONLY",
        "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
        "observation_manifest_sha256": hashlib.sha256(json.dumps(observations, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
        "summary": {
            "source_local_rows_rechecked": 16, "literal_title_card_matches": 13,
            "part_numeral_variants_unresolved": 3, "original_drafts_pending_review": 13,
            "public_synopses_approved": 0, "raw_publisher_html_bodies_pinned": 0,
            "governed_source_or_work_admissions": 0,
        },
        "admission_effect": "NONE", "coverage_effect": "NONE", "rows": result,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    catalog, raw = load(CATALOG)
    obs, _ = load(SOURCE)
    result = compile_records(catalog, raw, obs)
    encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    target = ROOT / OUTPUT
    if args.check:
        if target.is_symlink() or not target.is_file() or target.read_bytes() != encoded:
            raise SystemExit("B007_DERIVATIVE_STALE_OR_UNREVIEWED")
    else:
        if target.is_symlink():
            raise SystemExit("B007_SYMLINK_OUTPUT_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("B007_OK: 16 official cards, 13 literal title matches, 3 held part-numeral variants; zero admission")


if __name__ == "__main__":
    main()
