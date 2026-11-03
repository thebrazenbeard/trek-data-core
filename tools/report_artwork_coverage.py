#!/usr/bin/env python3
"""Read-only visual mapping audit over source-local discovery observations.

Counts are NOT counts of canonical Works or reviewed story content. The
Open Library historical held packet is a separate proposal-only inventory;
absence of artwork must never be interpreted as a rights refusal.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import validate_artwork_release as artwork


ROOT = Path(__file__).resolve().parents[1]
MEDIUMS = ("EPISODE", "FILM", "LITERATURE", "SHORT_FORM", "AUDIO")
RIGHTS = {"API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED", "PUBLIC_DISPLAY_PERMISSION_VERIFIED"}
REPORT_KIND = "SOURCE_LOCAL_VISUAL_MAPPING_AUDIT"
# This historical proposal packet must remain an immutable observation.
# A later source-local directory expansion must not silently rewrite its
# rejected-title-page / no-cover / missing-ISBN findings.
HISTORIC_PACKET_SHA256 = "f8dd9fc079d2a1eeb6dd10063954f6c41f37998eeb1de220ea672c06eb6f5762"


class CoverageRejected(ValueError):
    """Invalid or misleading source-local visual coverage report input."""


def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise CoverageRejected(reason)


def _source_rows(root: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    directory = artwork._json_file(root, "explorer/discovery-catalog.json")
    films = artwork._json_file(root, "explorer/film-catalog.json")
    _require(isinstance(directory, dict) and isinstance(films, dict),
             "source-local catalogs must be JSON objects")
    rows = directory.get("rows")
    film_rows = films.get("films")
    _require(directory.get("data_status") == "DISCOVERY_ONLY" and
             directory.get("coverage_effect") == "NONE" and
             directory.get("admission_effect") == "NONE" and
             isinstance(rows, list) and type(directory.get("row_count")) is int and
             len(rows) == directory["row_count"], "directory rows are not source-local discovery")
    _require(films.get("data_status") == "DISCOVERY_ONLY" and
             films.get("coverage_effect") == "NONE" and
             isinstance(film_rows, list) and type(films.get("film_count")) is int and
             len(film_rows) == films["film_count"], "film projection is not discovery-only")
    sources: dict[str, dict] = {}
    for row in rows:
        _require(isinstance(row, dict) and isinstance(row.get("row_id"), str) and
                 row["row_id"] not in sources and row.get("medium") in MEDIUMS and
                 isinstance(row.get("source_locator"), str),
                 "duplicate, untyped, or malformed source-local discovery row")
        sources[row["row_id"]] = row
    film_index: dict[str, dict] = {}
    for row in film_rows:
        _require(isinstance(row, dict) and isinstance(row.get("id"), str) and
                 row["id"] not in film_index and isinstance(row.get("source_locator"), str),
                 "duplicate or malformed film projection row")
        source = sources.get("film:" + row["id"])
        _require(source is not None and source["medium"] == "FILM" and
                 source["source_locator"] == row["source_locator"],
                 "film projection must map to one matching directory film observation")
        film_index[row["id"]] = row
    _require(sum(row["medium"] == "FILM" for row in sources.values()) == len(film_index),
             "film projection has missing or additional source-local rows")
    return sources, film_index


def report(root: Path = ROOT, *, verify_git: bool = False) -> dict:
    """Produce deterministic counts; validate, but never change, public inputs."""
    root = Path(root)
    sources, films = _source_rows(root)
    release = artwork.validate_manifest(root, verify_git=verify_git)
    _require(release.get("coverage_effect") == "NONE", "artwork release claimed coverage")
    manifest = root / artwork.MANIFEST
    if manifest.exists() or manifest.is_symlink():
        catalog = artwork._json_file(root, artwork.MANIFEST)
        entries = catalog.get("artwork")
        _require(catalog.get("schema_version") == "1.3.0" and
                 catalog.get("coverage_effect") == "NONE" and
                 catalog.get("rights_policy") == "PER_ENTRY_DISPLAY_GATE" and
                 isinstance(entries, list) and type(catalog.get("artwork_count")) is int and
                 len(entries) == catalog["artwork_count"] == release.get("artwork_count"),
                 "reviewed artwork manifest count or rights policy drift")
    else:
        entries = []
        _require(release.get("status") == "ARTWORK_UNAVAILABLE" and
                 release.get("artwork_count") == 0, "missing artwork manifest is not fail-closed")

    pinned: set[str] = set()
    pinned_medium = Counter()
    rights_medium: dict[str, Counter] = {medium: Counter() for medium in MEDIUMS}
    for entry in entries:
        _require(isinstance(entry, dict) and isinstance(entry.get("row_id"), str),
                 "malformed artwork row mapping")
        art_id = entry["row_id"]
        if art_id.startswith("directory:"):
            source_id = art_id.removeprefix("directory:")
        elif art_id.startswith("film:"):
            film_id = art_id.removeprefix("film:")
            _require(film_id in films, "artwork targets a missing film projection")
            source_id = "film:" + film_id
        else:
            raise CoverageRejected("artwork uses unsupported source-local row namespace")
        source = sources.get(source_id)
        _require(source is not None and source_id not in pinned and
                 source["source_locator"] == entry.get("source_locator"),
                 "artwork maps to missing, duplicate, or source-divergent observation")
        rights = entry.get("rights_status")
        _require(rights in RIGHTS, "artwork rights classification is not reviewed")
        pinned.add(source_id)
        pinned_medium[source["medium"]] += 1
        rights_medium[source["medium"]][rights] += 1

    # Deliberately count only this one explicitly scoped historic HELD ledger.
    # Other artwork proposals have heterogeneous schemas and are not silently
    # generalized to rights decisions. In particular, no-artwork != rights-HOLD.
    historical_held = Counter()
    held_reasons = Counter()
    packet_bytes = artwork._file_bytes(root, artwork.OL_SOURCE_PACKET, artwork.MAX_MANIFEST_BYTES)
    _require(hashlib.sha256(packet_bytes).hexdigest() == HISTORIC_PACKET_SHA256,
             "historical held proposal packet differs from immutable reviewed observation")
    packet = artwork._strict_json(packet_bytes, artwork.OL_SOURCE_PACKET)
    _require(isinstance(packet, dict), "historical held packet must be a JSON object")
    held = packet.get("held")
    _require(packet.get("data_status") == "PROPOSAL_ONLY_INDEPENDENT_ARTWORK_REVIEW_REQUIRED" and
             packet.get("coverage_effect") == "NONE" and
             packet.get("public_artwork_release_effect") == "NONE" and
             isinstance(held, list) and type(packet.get("held_count")) is int and
             packet["held_count"] == len(held), "historical held packet status/count drift")
    held_ids: set[str] = set()
    for entry in held:
        _require(isinstance(entry, dict) and isinstance(entry.get("row_id"), str) and
                 entry["row_id"] not in held_ids and
                 isinstance(entry.get("reason"), str) and entry["reason"].strip(),
                 "malformed or duplicate historical held visual candidate")
        source = sources.get(entry["row_id"])
        _require(source is not None and source["medium"] == "LITERATURE",
                 "historical held candidate is not a current literary discovery row")
        held_ids.add(entry["row_id"])
        historical_held["LITERATURE"] += 1
        held_reasons[entry["reason"]] += 1

    by_medium = []
    count_total = Counter(row["medium"] for row in sources.values())
    for medium in MEDIUMS:
        total = count_total[medium]
        art_count = pinned_medium[medium]
        _require(0 <= art_count <= total, "artwork count exceeds source-local rows")
        by_medium.append({
            "medium": medium,
            "source_local_metadata_rows": total,
            "reviewed_artwork_mappings": art_count,
            "unmapped_source_local_rows": total - art_count,
            "opt_in_api_previews_copyright_unresolved": rights_medium[medium][
                "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED"],
            "reviewed_same_origin_rights_assets": rights_medium[medium][
                "PUBLIC_DISPLAY_PERMISSION_VERIFIED"],
            "historical_held_artwork_proposals": historical_held[medium],
        })
    _require(sum(item["reviewed_artwork_mappings"] for item in by_medium) == len(entries),
             "visual map counts do not reconcile to manifest")
    return {
        "schema_version": "1.0.0",
        "report_kind": REPORT_KIND,
        "data_status": "SOURCE_LOCAL_METADATA_AND_ARTWORK_GATES_ONLY",
        "canonical_works_coverage": "NOT_MEASURED",
        "research_coverage_effect": "NONE",
        "catalog_paths": {"discovery": "explorer/discovery-catalog.json",
                          "film_parallel_projection": "explorer/film-catalog.json",
                          "artwork_reviewed": artwork.MANIFEST},
        "source_local_metadata_row_total": len(sources),
        "parallel_film_projection_rows_not_additive": len(films),
        "reviewed_artwork_mapping_total": len(entries),
        "historical_proposal_packet": artwork.OL_SOURCE_PACKET,
        "historical_held_artwork_proposal_total_not_rights_denials": len(held),
        "historical_held_reasons": dict(sorted(held_reasons.items())),
        "per_medium": by_medium,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on unreviewed source/artwork mappings")
    parser.add_argument("--verify-git", action="store_true", help="Require committed reviewed art bytes")
    args = parser.parse_args(argv)
    try:
        result = report(verify_git=args.verify_git)
    except (CoverageRejected, artwork.ArtworkRejected, OSError, UnicodeError, RecursionError) as error:
        print(f"ARTWORK_COVERAGE_REJECTED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
