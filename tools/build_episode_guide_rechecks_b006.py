#!/usr/bin/env python3
"""Compile Voyager B006 official rendered metadata rechecks, candidate-only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBS = Path("proposals/verification/episode-guide-rechecks-b006-voy-20261103/observations.json")
OUTPUT = Path("proposals/verification/episode-guide-rechecks-b006-voy-20261103/records.json")
BASELINE = "5ea4a8d562e76931218329b8386e363e3c40845f"
CATALOG_HASH = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "catalog_sha256",
    "observed_utc_date", "source_family", "read_surface", "raw_webpage_bytes_available",
    "source_body_read", "public_synopsis_authorized", "admission_effect", "coverage_effect", "rows",
}
ROW_KEYS = {"row_id", "official_title", "season", "episode", "title_resolution", "brief_description_read"}
EXPECTED = (
    ("Q2", 7, 19), ("The Cloud", 1, 6), ("The Omega Directive", 4, 21),
    ("Time And Again", 1, 4), ("Caretaker, Part 1 & 2", 1, 1),
    ("In the Flesh", 5, 4), ("Initiations", 2, 2), ("Investigations", 2, 20),
    ("Virtuoso", 6, 13), ("Ashes to Ashes", 6, 18), ("Jetrel", 1, 15),
    ("The Q and the Grey", 3, 11), ("Think Tank", 5, 20),
)
EXCEPTIONS = {
    "lead:0073": "CASE_VARIANT_UNRESOLVED",
    "lead:0074": "MULTIPART_TITLE_SCOPE_UNRESOLVED",
}


def unique_pairs(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ValueError("duplicate JSON key")
        values[key] = value
    return values


def load(path: Path) -> tuple[dict, bytes]:
    full = ROOT / path
    if full.is_symlink() or not full.is_file() or full.stat().st_size > 4_000_000:
        raise ValueError("missing, symlinked or oversized B006 source")
    raw = full.read_bytes()
    obj = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs)
    if not isinstance(obj, dict):
        raise ValueError("B006 source is not an object")
    return obj, raw


def compile_records(catalog: dict, catalog_raw: bytes, obs: dict) -> dict:
    if (catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE" or catalog.get("coverage_effect") != "NONE"
            or catalog.get("row_count") != 1214 or len(catalog.get("rows", [])) != 1214
            or hashlib.sha256(catalog_raw).hexdigest() != CATALOG_HASH):
        raise ValueError("unrecognized source-local catalog snapshot")
    if (set(obs) != TOP_KEYS or obs["schema_version"] != "1.0.0"
            or obs["proposal_id"] != "LIBRARIAN-B006-VOY-RENDERED-METADATA-20261103"
            or obs["baseline_accepted_main"] != BASELINE or obs["catalog_sha256"] != CATALOG_HASH
            or obs["observed_utc_date"] != "2026-11-03"
            or obs["source_family"] != "paramount_corporate_publisher_family"
            or obs["read_surface"] != "RENDERED_OFFICIAL_PARAMOUNT_PLUS_EPISODE_GUIDE_CARDS"
            or obs["raw_webpage_bytes_available"] is not False
            or obs["source_body_read"] is not False or obs["public_synopsis_authorized"] is not False
            or obs["admission_effect"] != "NONE" or obs["coverage_effect"] != "NONE"
            or not isinstance(obs["rows"], list) or len(obs["rows"]) != 13):
        raise ValueError("unreviewed B006 Voyager envelope")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    if len(by_id) != 1214:
        raise ValueError("duplicate source-local catalog IDs")
    ids = [f"lead:{i:04d}" for i in range(70, 83)]
    if [item.get("row_id") for item in obs["rows"]] != ids:
        raise ValueError("B006 Voyager row frontier drift")
    used_slots = set()
    result_rows = []
    for index, entry in enumerate(obs["rows"]):
        if not isinstance(entry, dict) or set(entry) != ROW_KEYS or entry["brief_description_read"] is not True:
            raise ValueError("unread, extra or malformed Voyager publisher card")
        row = by_id[entry["row_id"]]
        if (row.get("context") != "VOY" or row.get("medium") != "EPISODE"
                or row.get("candidate_kind") != "WIKIDATA_EPISODE"
                or row.get("source_group") != "wikidata:wdqs"
                or row.get("verification_status") != "UNVERIFIED_METADATA"
                or row.get("admission_effect") != "NONE" or row.get("coverage_effect") != "NONE"):
            raise ValueError("source-local Voyager metadata provenance drift")
        slot = (entry["season"], entry["episode"])
        if type(slot[0]) is not int or type(slot[1]) is not int or not 1 <= slot[0] <= 7 or not 1 <= slot[1] <= 26:
            raise ValueError("invalid official season or episode number")
        if slot in used_slots:
            raise ValueError("official Voyager slot claimed twice")
        used_slots.add(slot)
        if (entry["official_title"], *slot) != EXPECTED[index]:
            raise ValueError("not exact reviewed publisher card title and slot")
        variant = EXCEPTIONS.get(entry["row_id"])
        if variant == "CASE_VARIANT_UNRESOLVED":
            if (entry["title_resolution"] != variant or
                    entry["official_title"].casefold() != row["title"].casefold() or
                    entry["official_title"] == row["title"]):
                raise ValueError("title case variant silently accepted")
        elif variant == "MULTIPART_TITLE_SCOPE_UNRESOLVED":
            if (entry["title_resolution"] != variant or row["title"] != "Caretaker"
                    or entry["official_title"] != "Caretaker, Part 1 & 2"):
                raise ValueError("combined Caretaker card misrepresented as Work identity")
        elif entry["title_resolution"] != "EXACT" or entry["official_title"] != row["title"]:
            raise ValueError("false exact guide-card title match")
        season = entry["season"]
        url = f"https://www.paramountplus.com/shows/star_trek_voyager/episodes/{season}/"
        result_rows.append({
            "source_local_row_id": entry["row_id"],
            "source_local_title": row["title"],
            "source_local_locator": row["source_locator"],
            "source_local_lineage": "wikidata_collaborative_derivative",
            "source_local_context": "VOY",
            "publisher_family": obs["source_family"],
            "official_card": {
                "title": entry["official_title"],
                "season": season, "episode": entry["episode"],
                "guide_url": url,
                "section_locator": f"Episode Guide > {entry['official_title']} > S{season} E{entry['episode']} > short description",
                "brief_description_actually_read": True,
                "raw_webpage_sha256": None,
            },
            "title_resolution": entry["title_resolution"],
            "synopsis_publication_status": "NOT_REQUESTED_OR_APPROVED",
            "source_body_custody_status": "NOT_READ_OR_HASHED",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    statuses = [item["title_resolution"] for item in obs["rows"]]
    if (statuses.count("EXACT") != 11 or statuses.count("CASE_VARIANT_UNRESOLVED") != 1
            or statuses.count("MULTIPART_TITLE_SCOPE_UNRESOLVED") != 1):
        raise ValueError("unreviewed title/scope status counts")
    return {
        "data_status": "B006_VOY_RENDERED_PUBLISHER_METADATA_PROPOSAL_ONLY",
        "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest(),
        "observation_manifest_sha256": hashlib.sha256(
            json.dumps(obs, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        "summary": {
            "source_local_row_cases": 13,
            "publisher_guide_cards_read": 13,
            "exact_title_cases": 11,
            "case_variant_unresolved": 1,
            "multipart_scope_unresolved": 1,
            "public_synopses_approved": 0,
            "raw_publisher_html_bodies_pinned": 0,
            "governed_source_or_work_admissions": 0,
        },
        "admission_effect": "NONE", "coverage_effect": "NONE", "rows": result_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, catalog_raw = load(CATALOG)
    observations, _ = load(OBS)
    result = compile_records(catalog, catalog_raw, observations)
    encoded = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    target = ROOT / OUTPUT
    if args.check:
        if target.is_symlink() or not target.is_file() or target.read_bytes() != encoded:
            raise SystemExit("B006_VOY_DERIVATIVE_STALE_OR_UNREVIEWED")
    else:
        if target.is_symlink():
            raise SystemExit("B006_VOY_SYMLINK_OUTPUT_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("B006_VOY_OK: 13 source-local cards, 11 exact, 1 case variant, 1 multipart hold; zero admission")


if __name__ == "__main__":
    main()
