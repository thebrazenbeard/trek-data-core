#!/usr/bin/env python3
"""Deterministic source/license *non-admission* audit for six opt-in covers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[3]
LEDGER = Path(__file__).resolve().parent / "ledger.json"
SOURCE_PATHS = {
    "explorer/artwork-catalog-v1.3.json": "FOUR_CORE_AUTOBIOGRAPHIES",
    "explorer/picard-jackets-v1.0.json": "TWO_PICARD_SUPPLEMENT_EDITION_ROWS",
}
ROW_KEYS = {"row_id", "group", "isbn", "cover_id", "publisher_locator", "display_route", "copyright_status", "self_hosting_rights_status"}


class ArtworkRightsAuditError(ValueError):
    pass


def no_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ArtworkRightsAuditError("duplicate JSON key")
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_json_keys)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(packet: dict, source_catalogs: dict[str, dict], source_hashes: dict[str, str],
             root: Path = ROOT):
    if packet.get("schema_version") != "0.1.0" or packet.get("accepted_main_baseline") != "3028765359001b90bc3e6b5c1835ee283b326e91":
        raise ArtworkRightsAuditError("unreviewed baseline")
    if packet.get("source_catalog_sha256") != source_hashes:
        raise ArtworkRightsAuditError("reviewed-source digest drift")
    if packet.get("api_documentation_scope") != "THIRD_PARTY_SRC_DISPLAY_METHOD_NOT_UNDERLYING_COPYRIGHT_GRANT":
        raise ArtworkRightsAuditError("API display method falsely treated as image license")
    if packet.get("source_policy_locator") != "https://openlibrary.org/dev/docs/api/covers" or packet.get("source_license_caveat_locator") != "https://openlibrary.org/developers/licensing":
        raise ArtworkRightsAuditError("official API/rights caveat provenance changed")
    for key in ("public_local_artwork_bytes_mirrored", "rights_verified_self_hosted_assets", "actual_episode_thumbnail_mappings", "actual_film_thumbnail_mappings"):
        if packet.get(key) != 0:
            raise ArtworkRightsAuditError(f"unsupported positive release or artwork claim: {key}")
    for key in ("research_coverage_effect", "source_work_binding_effect"):
        if packet.get(key) != "NONE":
            raise ArtworkRightsAuditError(f"unsupported identity/coverage effect: {key}")

    if (root / "explorer/licensed-artwork").exists() or (root / "explorer/licensed-artwork").is_symlink():
        raise ArtworkRightsAuditError("unreviewed local licensed image directory appeared")
    if (root / "registry/artwork-rights-receipts").exists() or (root / "registry/artwork-rights-receipts").is_symlink():
        raise ArtworkRightsAuditError("rights receipts changed and require independent review")

    expected = {}
    for source_path, group in SOURCE_PATHS.items():
        source = source_catalogs[source_path]
        if source["artwork_count"] != len(source["artwork"]):
            raise ArtworkRightsAuditError("upstream cover count changed")
        if (group == "FOUR_CORE_AUTOBIOGRAPHIES" and len(source["artwork"]) != 4) or (group == "TWO_PICARD_SUPPLEMENT_EDITION_ROWS" and len(source["artwork"]) != 2):
            raise ArtworkRightsAuditError("four+two cover partition changed")
        for row in source["artwork"]:
            if row["row_id"] in expected:
                raise ArtworkRightsAuditError("overlapping publisher edition row identity")
            if row["provider"] != "OPEN_LIBRARY_COVERS_API" or row["image_size"] != "M" or row["rights_status"] != "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED":
                raise ArtworkRightsAuditError("upstream source route attempted rights escalation")
            expected[row["row_id"]] = (row, group)

    images = packet.get("images", [])
    if not isinstance(images, list) or len(images) != 6 or len({x.get("row_id") for x in images}) != 6:
        raise ArtworkRightsAuditError("six disjoint source-local image candidates required")
    if {x["row_id"] for x in images} != set(expected):
        raise ArtworkRightsAuditError("unexpected accepted-cover identity or missing edition")
    for item in images:
        if set(item) != ROW_KEYS:
            raise ArtworkRightsAuditError("unreviewed rights/asset assertion field")
        upstream, group = expected[item["row_id"]]
        if item["group"] != group:
            raise ArtworkRightsAuditError("misclassified four-core/two-overlay denominator")
        if (item["isbn"], item["cover_id"], item["publisher_locator"]) != (upstream["isbn"], upstream["cover_id"], upstream["source_locator"]):
            raise ArtworkRightsAuditError("publisher edition or Open Library cover crosswalk changed")
        url = urlparse(item["publisher_locator"])
        expected_hostname = "www.penguinrandomhouse.com" if group == "FOUR_CORE_AUTOBIOGRAPHIES" else "www.simonandschuster.com"
        if url.scheme != "https" or url.hostname != expected_hostname or url.username or url.password:
            raise ArtworkRightsAuditError("publisher first-party locator drift")
        if item["display_route"] != "OPEN_LIBRARY_COVERS_API_VISITOR_OPT_IN_ONLY" or item["copyright_status"] != "UNDERLYING_COPYRIGHT_UNRESOLVED" or item["self_hosting_rights_status"] != "NO_PERMISSION_RECEIPT":
            raise ArtworkRightsAuditError("documented API display cannot grant rehost/rights clearance")
    raw = json.dumps(packet, ensure_ascii=False).casefold()
    for phrase in ("licensed_and_authorized", "public_domain", "C:\\\\Users", "/mnt/c/", "OneDrive", "image_data", "base64_image"):
        if phrase.casefold() in raw:
            raise ArtworkRightsAuditError("fabricated permission, private path or image payload")
    return {"core_display_candidates": 4, "supplement_display_candidates": 2,
            "licensed_self_hosted_assets": 0, "episode_actual_thumbnail_mappings": 0,
            "film_actual_thumbnail_mappings": 0, "research_coverage_effect": "NONE"}


def main():
    source_catalogs = {path: read_json(ROOT / path) for path in SOURCE_PATHS}
    source_hashes = {path: sha256(ROOT / path) for path in SOURCE_PATHS}
    print("ARTWORK_SOURCE_RIGHTS_HELD_OK:", validate(read_json(LEDGER), source_catalogs, source_hashes))


if __name__ == "__main__":
    main()
