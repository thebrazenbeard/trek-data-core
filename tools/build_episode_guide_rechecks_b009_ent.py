#!/usr/bin/env python3
"""Deterministic held B009-ENT first-party episode-guide proposal compiler."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
SOURCE = Path("proposals/verification/episode-guide-rechecks-b009-ent-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b009-ent-20261103/records.json")
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"

EXPECTED = (
    ("Sleeping Dogs", "Sleeping Dogs", 1, 14, "EXACT_OFFICIAL_CARD_TITLE"),
    ("Desert Crossing", "Desert Crossing", 1, 24, "EXACT_OFFICIAL_CARD_TITLE"),
    ("Oasis", "Oasis", 1, 20, "EXACT_OFFICIAL_CARD_TITLE"),
    ("In a Mirror, Darkly, Part II", "In A Mirror, Darkly, Pt 2", 4, 19, "PART_NUMERAL_STYLE_UNRESOLVED"),
    ("Storm Front, Part I", "Storm Front, Pt. 1", 4, 1, "PART_NUMERAL_STYLE_UNRESOLVED"),
    ("Storm Front, Part II", "Storm Front, Pt. 2", 4, 2, "PART_NUMERAL_STYLE_UNRESOLVED"),
    ("Shockwave, Part I", "Shockwave Part I", 1, 26, "PUNCTUATION_STYLE_UNRESOLVED"),
    ("Broken Bow, Part I", "Broken Bow - Part 1 and 2", 1, 1, "COMBINED_CARD_SPLIT_UNRESOLVED"),
    ("Broken Bow, Part II", "Broken Bow - Part 1 and 2", 1, 1, "COMBINED_CARD_SPLIT_UNRESOLVED"),
)
SYNOPSES = (
    "T'Pol, Reed and Hoshi are stranded aboard a disabled Klingon vessel after a Klingon woman takes their shuttlepod.",
    "After Archer and Trip help repair a disabled vessel, its captain invites them to dine at his desert village.",
    "Trip explores a crashed ship on a desolate world and discovers that members of its crew have survived.",
)
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "catalog_sha256", "observed_date_utc",
    "source_family", "read_surface", "raw_webpage_bytes_custodied", "episode_video_or_transcript_read",
    "public_synopsis_authorized", "admission_effect", "coverage_effect", "rows",
}
ROW_KEYS = {"row_id", "official_card_title", "season", "episode", "title_resolution", "official_card_description_read", "original_synopsis_draft"}


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def load(path):
    f = ROOT / path
    if f.is_symlink() or not f.is_file() or f.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized input")
    raw = f.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys), raw


def compile_records(catalog, catalog_raw, source):
    if (hashlib.sha256(catalog_raw).hexdigest() != CATALOG_SHA
            or catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE"
            or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214):
        raise ValueError("discovery catalog input not accepted B009 snapshot")
    if (not isinstance(source, dict) or set(source) != TOP_KEYS
            or source["schema_version"] != "1.0.0"
            or source["proposal_id"] != "LIBRARIAN-B009-ENT-GUIDE-20261103"
            or source["baseline_accepted_main"] != "a7691f054fff2c55dbc183afb6086762b797cedd"
            or source["catalog_sha256"] != CATALOG_SHA or source["observed_date_utc"] != "2026-11-03"
            or source["source_family"] != "paramount_corporate_publisher_family"
            or source["read_surface"] != "RENDERED_OFFICIAL_PARAMOUNT_PLUS_EPISODE_GUIDE_CARDS"
            or source["raw_webpage_bytes_custodied"] is not False
            or source["episode_video_or_transcript_read"] is not False
            or source["public_synopsis_authorized"] is not False
            or source["admission_effect"] != "NONE" or source["coverage_effect"] != "NONE"
            or not isinstance(source["rows"], list) or len(source["rows"]) != len(EXPECTED)):
        raise ValueError("B009 source envelope changed")
    lookup = {r["row_id"]: r for r in catalog["rows"]}
    if len(lookup) != 1214:
        raise ValueError("duplicate source-local catalog identifiers")
    expected_ids = [f"lead:{i:04d}" for i in range(99, 108)]
    if [r.get("row_id") for r in source["rows"]] != expected_ids:
        raise ValueError("B009 source-local ID sequence changed")
    output = []
    seen_guide_slots = set()
    for i, row in enumerate(source["rows"]):
        if not isinstance(row, dict) or set(row) != ROW_KEYS or row["official_card_description_read"] is not True:
            raise ValueError("missing verified publisher card")
        title, official, season, episode, resolution = EXPECTED[i]
        indexed = lookup[row["row_id"]]
        if (indexed["title"] != title or indexed["context"] != "ENT"
                or indexed["medium"] != "EPISODE" or indexed["candidate_kind"] != "WIKIDATA_EPISODE"
                or indexed["source_group"] != "wikidata:wdqs"
                or indexed["verification_status"] != "UNVERIFIED_METADATA"
                or indexed["admission_effect"] != "NONE" or indexed["coverage_effect"] != "NONE"):
            raise ValueError("Wikidata discovery source-local binding changed")
        if (row["official_card_title"], row["season"], row["episode"], row["title_resolution"]) != (official, season, episode, resolution):
            raise ValueError("publisher card title, ordinal, or hold changed")
        if type(row["season"]) is not int or type(row["episode"]) is not int:
            raise ValueError("season/episode must be integers")
        slot = (season, episode)
        if slot in seen_guide_slots and (i not in (7, 8) or slot != (1, 1)):
            raise ValueError("unreviewed publisher card reuse")
        seen_guide_slots.add(slot)
        if resolution == "EXACT_OFFICIAL_CARD_TITLE":
            if row["original_synopsis_draft"] != SYNOPSES[i]:
                raise ValueError("editorial synopsis drift from read source")
        elif row["original_synopsis_draft"] is not None:
            raise ValueError("held title/card identity cannot publish synopsis")
        output.append({
            "source_local_row_id": row["row_id"],
            "source_local_title": indexed["title"],
            "source_local_locator": indexed["source_locator"],
            "source_local_lineage": "wikidata_collaborative_derivative",
            "source_local_context": "ENT",
            "official_card": {
                "title": official, "season": season, "episode": episode,
                "guide_url": f"https://www.paramountplus.com/shows/enterprise/episodes/{season}/",
                "section_locator": f"Episode Guide > {official} > S{season} E{episode} > short description",
                "brief_description_actually_read": True, "raw_webpage_sha256": None,
            },
            "title_resolution": resolution,
            "original_synopsis_draft": row["original_synopsis_draft"],
            "synopsis_publication_status": "HUMAN_AND_EDITORIAL_REVIEW_PENDING" if resolution == "EXACT_OFFICIAL_CARD_TITLE" else "HOLD_SOURCE_IDENTITY",
            "source_body_custody_status": "NOT_READ_OR_HASHED",
            "governed_coverage_state": "NOT_ADMITTED", "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return {
        "data_status": "B009-ENT_RENDERED_PUBLISHER_METADATA_PROPOSAL_ONLY",
        "catalog_sha256": CATALOG_SHA,
        "observation_manifest_sha256": hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
        "summary": {"source_local_rows_rechecked": 9, "literal_title_card_matches": 3, "part_or_punctuation_variants_unresolved": 4,
                    "combined_card_split_rows_unresolved": 2, "original_drafts_pending_review": 3,
                    "public_synopses_approved": 0, "raw_publisher_html_bodies_pinned": 0,
                    "governed_source_or_work_admissions": 0},
        "admission_effect": "NONE", "coverage_effect": "NONE", "rows": output,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    catalog, catalog_raw = load(CATALOG)
    source, _ = load(SOURCE)
    result = compile_records(catalog, catalog_raw, source)
    encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    dest = ROOT / OUTPUT
    if args.check:
        if dest.is_symlink() or not dest.is_file() or dest.read_bytes() != encoded:
            raise SystemExit("B009-ENT_DERIVATIVE_STALE_OR_UNREVIEWED")
    else:
        if dest.is_symlink():
            raise SystemExit("B009-ENT_SYMLINK_OUTPUT_REFUSED")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(encoded)
    print("B009-ENT_OK: 9 official card observations, 3 exact titles, 6 held source-identity cases; no admission")


if __name__ == "__main__":
    main()
