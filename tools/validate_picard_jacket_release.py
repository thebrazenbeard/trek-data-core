#!/usr/bin/env python3
"""Fail-closed release gate for two *remote, opt-in* Picard cover previews.

This does not clear original cover copyright or admit any literary Work.
Physical image binaries remain forbidden by the independent Pages gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import validate_picard_cover_candidates as source
import validate_artwork_release as historical

ROOT = Path(__file__).resolve().parents[1]
SIDECAR = "explorer/picard-jackets-v1.0.json"
SIDECAR_SHA = "85bdc8ebbb348d713d604fb9486c2af091e36d40138587a761ddd93716cd9615"
SOURCE_PACKET_SHA = "031e558658de77627158f022621752d0dd863b47f41b47531161989650b3d3ad"
RECEIPT = "registry/artwork-edition-receipts/picard-jackets-review.json"
ROOT_KEYS = {"schema_version", "data_status", "source_packet_path", "source_packet_sha256",
             "source_overlay_sha256", "copyright_status", "public_image_bytes_committed",
             "coverage_effect", "work_admission_effect", "artwork_count", "artwork"}
ENTRY_KEYS = {"row_id", "provider", "cover_id", "image_size", "isbn", "alt_text",
              "source_locator", "rights_status", "edition_metadata_sha256", "attribution_url"}
RECEIPT_KEYS = {"schema_version", "review_status", "source_packet_sha256", "sidecar_sha256",
                "reviewed_on", "edition_reviewer", "publisher_source_reviewer",
                "large_image_reviewer", "medium_image_reviewer", "edition_source_scope",
                "visual_inspection_scope", "api_display_scope", "copyright_status",
                "coverage_effect", "work_admission_effect", "image_bytes_mirrored",
                "source_local_jacket_count"}


def check(root: Path = ROOT, verify_git: bool = False) -> dict:
    root = Path(root)
    source.validate(root)
    historical_result = historical.validate_manifest(root, verify_git=verify_git)
    if historical_result.get("artwork_count") != 4:
        raise source.Rejected("historic four-cover fallback not reviewed")
    raw = source.file_bytes(root, SIDECAR)
    if hashlib.sha256(raw).hexdigest() != SIDECAR_SHA:
        raise source.Rejected("Picard release artifact not code-pinned")
    manifest = source.strict_json(raw)
    if (not isinstance(manifest, dict) or set(manifest) != ROOT_KEYS or
            manifest.get("schema_version") != "1.0.0" or
            manifest.get("data_status") != "PICARD_SOURCE_LOCAL_OPEN_LIBRARY_API_OPT_IN_ONLY" or
            manifest.get("source_packet_path") != source.PACKET or
            manifest.get("source_packet_sha256") != SOURCE_PACKET_SHA or
            manifest.get("source_overlay_sha256") != source.OVERLAY_SHA256 or
            manifest.get("copyright_status") != "UNDERLYING_JACKET_COPYRIGHT_UNRESOLVED" or
            manifest.get("public_image_bytes_committed") is not False or
            manifest.get("coverage_effect") != "NONE" or
            manifest.get("work_admission_effect") != "NONE" or
            manifest.get("artwork_count") != 2 or
            not isinstance(manifest.get("artwork"), list) or len(manifest["artwork"]) != 2):
        raise source.Rejected("Picard sidecar provenance/rights boundary invalid")
    packet = source.strict_json(source.file_bytes(root, source.PACKET))
    rows = {"directory:" + c["row_id"]: c for c in packet["candidates"]}
    seen = set()
    for item in manifest["artwork"]:
        if not isinstance(item, dict) or set(item) != ENTRY_KEYS:
            raise source.Rejected("unreviewed Picard jacket sidecar field")
        candidate = rows.get(item["row_id"])
        if (candidate is None or item["row_id"] in seen or
                item["provider"] != "OPEN_LIBRARY_COVERS_API" or item["image_size"] != "M" or
                item["cover_id"] != candidate["cover_id"] or item["isbn"] != candidate["isbn"] or
                item["source_locator"] != candidate["source_locator"] or
                item["edition_metadata_sha256"] != candidate["edition_metadata_sha256"] or
                item["attribution_url"] != candidate["attribution_url"] or
                item["rights_status"] != "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" or
                not item["alt_text"].startswith("Open Library jacket preview: " + candidate["publisher_title"]) or
                "underlying copyright unresolved" not in item["alt_text"] or
                len(item["alt_text"]) > 180):
            raise source.Rejected("Picard sidecar cannot promote unreviewed source/cover association")
        seen.add(item["row_id"])
    if len(seen) != 2:
        raise source.Rejected("Picard sidecar must include two reviewed jackets")

    receipt = source.strict_json(source.file_bytes(root, RECEIPT))
    if (not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS or
            receipt["schema_version"] != "1.0.0" or
            receipt["review_status"] != "FOUR_DISTINCT_REVIEWERS_API_OPT_IN" or
            receipt["source_packet_sha256"] != SOURCE_PACKET_SHA or
            receipt["sidecar_sha256"] != SIDECAR_SHA or
            receipt["reviewed_on"] != "2026-11-03" or
            receipt["edition_source_scope"] != "TWO_PICARD_S_AND_S_TRADE_PAPERBACK_ISBNS" or
            receipt["visual_inspection_scope"] != "TWO_FRONT_JACKETS_M_AND_L_BYTES" or
            receipt["api_display_scope"] != "REMOTE_OPEN_LIBRARY_API_AFTER_EXPLICIT_CONSENT" or
            receipt["copyright_status"] != "UNRESOLVED" or
            receipt["coverage_effect"] != "NONE" or
            receipt["work_admission_effect"] != "NONE" or
            receipt["image_bytes_mirrored"] is not False or
            receipt["source_local_jacket_count"] != 2):
        raise source.Rejected("missing independently reviewed source/artwork receipt")
    reviewers = [receipt[k] for k in ("edition_reviewer", "publisher_source_reviewer",
                                     "large_image_reviewer", "medium_image_reviewer")]
    if not all(isinstance(r, str) and re.fullmatch(r"[a-z0-9._-]{5,80}", r)
               for r in reviewers) or len(set(reviewers)) != 4:
        raise source.Rejected("four distinct independently observed review roles required")
    js = source.file_bytes(root, "explorer/app.js").decode("utf-8")
    html = source.file_bytes(root, "explorer/index.html").decode("utf-8")
    if (SIDECAR_SHA not in js or "loadArtworkCatalog().then(loadPicardJacketCatalog)" not in js or
            "!artworkState.available || !picardLiteratureSupplement.available" not in js or
            "if (source) {" not in js or "const source = artworkState.enabled ?" not in js or
            f'./app.js?v={hashlib.sha256(js.encode()).hexdigest()}' not in html):
        raise source.Rejected("Picard JS opt-in/cache release gate missing")
    workflow = source.file_bytes(root, ".github/workflows/static.yml").decode("utf-8")
    if ("python3 tools/validate_picard_jacket_release.py --check --verify-git" not in workflow or
            "! -path explorer/picard-jackets-v1.0.json" not in workflow or
            "test -e explorer/licensed-artwork || test -L explorer/licensed-artwork" not in workflow):
        raise source.Rejected("Pages independent media or release validator absent")
    if verify_git:
        for relative in (SIDECAR, source.PACKET, RECEIPT, "explorer/app.js", "explorer/index.html",
                         ".github/workflows/static.yml", "tools/validate_picard_jacket_release.py"):
            expected = subprocess.run(["git", "rev-parse", "HEAD:" + relative], cwd=root,
                                      capture_output=True, text=True, check=False)
            actual = subprocess.run(["git", "hash-object", relative], cwd=root,
                                    capture_output=True, text=True, check=False)
            if expected.returncode or actual.returncode or expected.stdout.strip() != actual.stdout.strip():
                raise source.Rejected("uncommitted Picard artwork release file: " + relative)
    return {"status": "SIX_REMOTE_API_COVERS_OPT_IN_REVIEWED", "original_covers": 4,
            "new_picard_covers": 2, "coverage_effect": "NONE", "public_local_image_bytes": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-git", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check(verify_git=args.verify_git), sort_keys=True))
