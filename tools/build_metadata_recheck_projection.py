#!/usr/bin/env python3
"""Compile accepted B001–B004 rendered metadata checks for read-only Explorer display.

This source-local projection does NOT admit a Work, bind raw source bytes,
authorize proposed synopses, resolve title variants, or certify fictional facts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_discovery_verification_ledger import _read_json, build as b001_build
from build_episode_guide_rechecks_b002 import compile_observations as b002_build
from build_episode_guide_rechecks_b003 import compile_records as b003_build
from build_episode_guide_rechecks_b004 import compile_records as b004_build

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OUT = Path("explorer/metadata-rechecks.json")
B001 = Path("proposals/verification/discovery-source-rechecks-b001-20261103")
B002 = Path("proposals/verification/episode-guide-rechecks-b002-20261103")
B003 = Path("proposals/verification/episode-guide-rechecks-b003-20261103")
B004 = Path("proposals/verification/episode-guide-rechecks-b004-20261103")


def build() -> dict:
    catalog, raw_catalog = _read_json(CATALOG)
    b001_sources, raw_b001_sources = _read_json(B001 / "source_rechecks.json")
    b001_episodes, raw_b001_episodes = _read_json(B001 / "episode_rechecks.json")
    b002_obs, raw_b002 = _read_json(B002 / "observations.json")
    b003_obs, raw_b003 = _read_json(B003 / "observations.json")
    b004_obs, raw_b004 = _read_json(B004 / "observations.json")
    base = b001_build(catalog, raw_catalog, b001_sources, b001_episodes)
    b2 = b002_build(catalog, raw_catalog, b002_obs)
    b3 = b003_build(catalog, raw_catalog, b003_obs)
    b4 = b004_build(catalog, raw_catalog, b004_obs)
    inputs = [(B001 / "source_rechecks.json", raw_b001_sources),
              (B001 / "episode_rechecks.json", raw_b001_episodes),
              (B002 / "observations.json", raw_b002),
              (B003 / "observations.json", raw_b003),
              (B004 / "observations.json", raw_b004)]
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    if len(by_id) != 1214 or len(base["rows"]) != 1214:
        raise ValueError("accepted source-local catalog changed or contains duplicate IDs")
    checked = {}

    def add(row_id: str, batch: str, observed_title: str, observed_date: str,
            official_source_url: str, evidence_section: str, title_check: str,
            fields: list[str], observation_path: Path, raw: bytes) -> None:
        row = by_id.get(row_id)
        if row is None or row_id in checked or not official_source_url.startswith("https://"):
            raise ValueError("duplicate/missing source-local metadata check or invalid official URL")
        if title_check == "EXACT" and observed_title != row["title"]:
            raise ValueError("false exact metadata title check")
        if title_check != "EXACT" and observed_title == row["title"]:
            raise ValueError("false unresolved-title claim")
        if row["verification_status"] != "UNVERIFIED_METADATA" or row["coverage_effect"] != "NONE":
            raise ValueError("source-local discovery claim was elevated")
        checked[row_id] = {
            "row_id": row_id,
            "medium": row["medium"],
            "source_local_title": row["title"],
            "source_local_context": row["context"],
            "source_local_group": row["source_group"],
            "source_local_input": row["source_input"],
            "source_local_locator": row["source_locator"],
            "recheck_batch": batch,
            "official_observed_title": observed_title,
            "official_evidence_url": official_source_url,
            "official_section_locator": evidence_section,
            "observed_utc_date": observed_date,
            "title_check": title_check,
            "fields_observed": fields,
            "source_observation_path": observation_path.as_posix(),
            "source_observation_sha256": hashlib.sha256(raw).hexdigest(),
            "source_representation": "RENDERED_OFFICIAL_METADATA_NOT_RAW_PAGE_CUSTODY",
            "official_source_family": "paramount_corporate_publisher_family" if row["medium"] == "EPISODE" else (
                "titan_books_via_prh_distributor_family" if "penguinrandomhouse" in official_source_url else
                "simon_and_schuster_publisher_family"),
            "raw_webpage_sha256": None,
            "source_local_discovery_state": "CATALOGUED_METADATA_ONLY",
            "governed_research_coverage_state": "NOT_ADMITTED",
            "synopsis_publication_effect": "NONE",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        }

    for original in base["rows"]:
        if original["metadata_check_state"] == "NOT_RECHECKED":
            continue
        row_id = original["row_id"]
        obs = next((o for o in b001_sources["observations"] if o["row_id"] == row_id), None)
        if obs:
            add(row_id, "B001", obs["observed_title"], obs["observed_at_utc_date"],
                obs["source_locator"], obs["evidence_locator"], "EXACT",
                ["title", "creator", "edition_isbn"], B001 / "source_rechecks.json", raw_b001_sources)
        else:
            obs = next(o for o in b001_episodes["observations"] if o["row_id"] == row_id)
            add(row_id, "B001", obs["observed_title"], obs["observed_at_utc_date"],
                obs["official_episode_url"], obs["evidence_locator"], "EXACT",
                ["title", "series", "season_episode", "air_date"], B001 / "episode_rechecks.json", raw_b001_episodes)

    for item in b2["rows"]:
        add(item["source_local_row_id"], "B002", item["observed_official_title"],
            item["observed_at_utc_date"], item["official_guide_url"], item["guide_card_locator"],
            "EXACT" if item["title_check"] == "EXACT_RENDERED_CARD_MATCH" else "UNRESOLVED_PUNCTUATION",
            ["title", "official_season_episode_slot"], B002 / "observations.json", raw_b002)
    for item in b3["rows"]:
        add(item["source_local_row_id"], "B003", item["observed_title"],
            item["observed_utc_date"], item["official_guide_url"], item["guide_card_locator"],
            "EXACT" if item["title_check"] == "EXACT_RENDERED_OFFICIAL_CARD_MATCH" else "UNRESOLVED_CASE",
            ["title", "official_season_episode_slot"], B003 / "observations.json", raw_b003)
    for item in b4["rows"]:
        cards = item["official_card_candidates"]
        title_check = {"EXACT": "EXACT", "PUNCTUATION_VARIANT_UNRESOLVED": "UNRESOLVED_PUNCTUATION",
                       "MULTIPART_SOURCE_LOCAL_TARGET_UNRESOLVED": "UNRESOLVED_MULTIPART"}[item["title_resolution"]]
        add(item["source_local_row_id"], "B004", " / ".join(card["title"] for card in cards),
            item["observed_utc_date"], cards[0]["guide_url"],
            " | ".join(card["card_locator"] for card in cards), title_check,
            ["title", "official_season_episode_slot"] if len(cards) == 1 else ["multipart_official_card_candidates"],
            B004 / "observations.json", raw_b004)
    rows = [checked[key] for key in sorted(checked)]
    if (len(rows) != 56 or sum(r["title_check"] != "EXACT" for r in rows) != 4
            or sum(r["medium"] == "LITERATURE" for r in rows) != 5
            or sum(r["medium"] == "EPISODE" for r in rows) != 51):
        raise ValueError("unexpected accepted batch scope; fail closed before display")
    return {
        "schema_version": "1.0.0", "data_status": "SOURCE_LOCAL_RENDERED_METADATA_RECHECKS_DISPLAY_ONLY",
        "source_directory_sha256": hashlib.sha256(raw_catalog).hexdigest(),
        "input_observation_receipts": [{"path": path.as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}
                                       for path, raw in inputs],
        "source_local_row_count": 1214,
        "embedded_research_lead_rows": 218,
        "embedded_research_leads_rechecked": 51,
        "embedded_research_leads_not_rechecked": 167,
        "literary_directory_rows_rechecked": 5,
        "rendered_metadata_rechecks": 56,
        "unrechecked_source_local_rows": 1158,
        "exact_title_matches": 52,
        "unresolved_title_or_multipart_cases": 4,
        "raw_webpage_bytes_custodied": 0,
        "admitted_works_or_evidence": 0,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    encoded = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    path = ROOT / OUT
    if args.check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != encoded:
            raise SystemExit("METADATA_RECHECK_PROJECTION_STALE_OR_TAMPERED")
    else:
        if path.is_symlink():
            raise SystemExit("METADATA_RECHECK_OUTPUT_SYMLINK_REFUSED")
        path.write_bytes(encoded)
    print("METADATA_RECHECK_PROJECTION_OK: 56 official rendered metadata checks / "
          "1,158 source-local rows not rechecked / 4 unresolved title-or-multipart cases; "
          "0 admissions, 0 raw pages pinned")


if __name__ == "__main__":
    main()
