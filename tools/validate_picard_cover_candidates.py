#!/usr/bin/env python3
"""Validate held, source-local Picard jacket candidates (never public art)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACKET = "proposals/librarian/open-library-picard-jackets-20261103/records.json"
OVERLAY = "explorer/picard-literature-overlay.json"
PUBLISHER = "proposals/librarian/picard-companion-editions-20261103/records.json"
OVERLAY_SHA256 = "ab8e5d15f7b33bf1311aec0afb2755322b41bca73978d3c7889f1272dbfe21c8"
PUBLISHER_SHA256 = "cdbda4dfa33c795bd51a1ebbfb09e41c7d838b73ce17aa6756428bd6ed8d8da4"
HASH = re.compile(r"[0-9a-f]{64}\Z")
ISBN = re.compile(r"97[89][0-9]{10}\Z")
ROW_KEYS = {
    "row_id", "publisher_title", "publisher_creator", "publisher_isbn_detail", "source_locator",
    "isbn", "openlibrary_edition_id", "openlibrary_edition_json_url", "openlibrary_edition_title",
    "edition_metadata_sha256", "cover_id", "medium_preview_url", "medium_preview_sha256",
    "medium_preview_bytes", "medium_width", "medium_height", "large_preview_url",
    "large_preview_sha256", "large_preview_bytes", "large_width", "large_height",
    "image_observation", "image_observer", "attribution_url", "rights_status", "release_status",
}
ROOT_KEYS = {
    "schema_version", "data_status", "observed_on", "source_catalog_path", "source_catalog_sha256",
    "publisher_source_input", "publisher_source_sha256", "source_lineage", "api_guidance",
    "copyright_guidance", "underlying_cover_copyright", "image_bytes_committed",
    "public_artwork_release_effect", "source_work_admission_effect", "coverage_effect",
    "candidate_count", "candidates",
}
EXPECTED = {
    "literature:proposed-lit-picard-the-dark-veil": (
        "9781982154073", 10691195, "OL32025277M",
        "4d7798715ac839095498c1c508501b7717be2fc63f4c93ce804af2702e3f4488",
        "8172dd71c563fae8aee4b82b645a4e852ffb1bc968be0578efb85b3112854c3a",
        "0f75f3ffc1db2f6378d71d4224c5f225fb35f15214b9af550ce640d50b01c853",
        19466, 271, 42030, 331),
    "literature:proposed-lit-picard-rogue-elements": (
        "9781982175207", 13231543, "OL36102337M",
        "725e29c8f1dce0391b46887eacb783f4e9b34d4486031edccb2ac62d9656878b",
        "e4c8ce22a96738d739d256389db0a91f51659877592cb731c452d96b13e9609f",
        "9633fd168e7082e3a77fef4f453bb93dee3a35603f864d51041fe983c7af0cfd",
        25665, 280, 55406, 321),
}


class Rejected(ValueError):
    pass


def require(valid: bool, reason: str):
    if not valid:
        raise Rejected(reason)


def strict_json(raw: bytes):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, "duplicate JSON key")
            obj[key] = value
        return obj
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique)


def file_bytes(root: Path, relative: str) -> bytes:
    require(isinstance(relative, str) and ".." not in relative and not relative.startswith("/"),
            "unbounded source path")
    path = root / relative
    require(not path.is_symlink() and path.is_file(), "missing or symlinked source file")
    data = path.read_bytes()
    require(len(data) <= 1_000_000, "oversized metadata file")
    return data


def is_sha(value) -> bool:
    return isinstance(value, str) and HASH.fullmatch(value) is not None


def validate(root: Path = ROOT) -> dict:
    root = Path(root)
    packet = strict_json(file_bytes(root, PACKET))
    require(isinstance(packet, dict) and set(packet) == ROOT_KEYS, "candidate packet envelope drift")
    require(packet["schema_version"] == "1.0.0" and
            packet["data_status"] == "SOURCE_LOCAL_JACKET_CANDIDATES_HELD" and
            packet["observed_on"] == "2026-11-03" and
            packet["source_catalog_path"] == OVERLAY and
            packet["source_catalog_sha256"] == OVERLAY_SHA256 and
            packet["publisher_source_input"] == PUBLISHER and
            packet["publisher_source_sha256"] == PUBLISHER_SHA256 and
            packet["api_guidance"] == "https://openlibrary.org/dev/docs/api/covers" and
            packet["copyright_guidance"] == "https://openlibrary.org/developers/licensing" and
            packet["underlying_cover_copyright"] == "UNRESOLVED" and
            packet["image_bytes_committed"] is False and
            all(packet[field] == "NONE" for field in ("public_artwork_release_effect",
                                                      "source_work_admission_effect", "coverage_effect")) and
            isinstance(packet["source_lineage"], str) and len(packet["source_lineage"]) >= 30,
            "held status, provider guidance or coverage boundary drift")
    require(hashlib.sha256(file_bytes(root, OVERLAY)).hexdigest() == OVERLAY_SHA256 and
            hashlib.sha256(file_bytes(root, PUBLISHER)).hexdigest() == PUBLISHER_SHA256,
            "accepted publisher/overlay bytes drifted")
    overlay = strict_json(file_bytes(root, OVERLAY))
    publisher = strict_json(file_bytes(root, PUBLISHER))
    require(overlay["data_status"] == "PICARD_LITERATURE_SOURCE_LOCAL_SUPPLEMENT_ONLY" and
            overlay["row_count"] == 2 and publisher["proposal_only"] is True and
            publisher["accepted_work_effect"] == "NONE", "source-local reference lost")
    source_rows = {row["row_id"]: row for row in overlay["rows"]}
    editions = {e["isbn13"]: e for e in publisher["edition_candidates"]}
    candidates = packet["candidates"]
    require(type(packet["candidate_count"]) is int and packet["candidate_count"] == 2 and
            isinstance(candidates, list) and len(candidates) == 2, "exactly two held jacket candidates required")
    found = set()
    for row in candidates:
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "candidate field contract drift")
        key = row["row_id"]
        require(key in EXPECTED and key not in found and key in source_rows,
                "unknown/duplicate source-local jacket association")
        found.add(key)
        isbn, cover_id, edition_id, metadata_digest, medium_digest, large_digest, medium_bytes, medium_height, large_bytes, large_width = EXPECTED[key]
        source = source_rows[key]
        require(row["isbn"] == isbn and row["cover_id"] == cover_id and
                row["openlibrary_edition_id"] == edition_id and
                row["openlibrary_edition_json_url"] == f"https://openlibrary.org/books/{edition_id}.json" and
                row["publisher_title"] == source["title"] and
                row["source_locator"] == source["source_locator"] and
                row["publisher_isbn_detail"] in source["details"] and
                row["publisher_isbn_detail"].endswith(isbn) and
                editions[isbn]["format"] == "TRADE_PAPERBACK" and
                editions[isbn]["work_id"] in key,
                "jacket cannot be bound to exact publisher/ISBN row")
        require(row["edition_metadata_sha256"] == metadata_digest and
                row["medium_preview_sha256"] == medium_digest and
                row["large_preview_sha256"] == large_digest and
                row["medium_preview_bytes"] == medium_bytes and
                row["medium_height"] == medium_height and
                row["large_preview_bytes"] == large_bytes and
                row["large_width"] == large_width,
                "preview digest/length/dimension not code-owned and reproducible")
        require(isinstance(row["publisher_creator"], str) and
                row["publisher_creator"] in source["context"] and
                ISBN.fullmatch(isbn) is not None and
                sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(isbn)) % 10 == 0 and
                all(is_sha(row[k]) for k in ("edition_metadata_sha256", "medium_preview_sha256",
                                               "large_preview_sha256")), "edition identity/hash invalid")
        for size in ("medium", "large"):
            suffix = "M" if size == "medium" else "L"
            require(row[f"{size}_preview_url"] ==
                    f"https://covers.openlibrary.org/b/id/{cover_id}-{suffix}.jpg?default=false" and
                    type(row[f"{size}_preview_bytes"]) is int and
                    1024 <= row[f"{size}_preview_bytes"] <= 100_000 and
                    type(row[f"{size}_width"]) is int and type(row[f"{size}_height"]) is int,
                    "unreviewed preview byte/provider locator")
        require(row["medium_width"] == 180 and 200 <= row["medium_height"] <= 400 and
                250 <= row["large_width"] <= 1000 and 350 <= row["large_height"] <= 1500 and
                row["attribution_url"] == f"https://openlibrary.org/isbn/{isbn}" and
                row["rights_status"] == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" and
                row["release_status"] == "HELD_FOR_INDEPENDENT_REVIEW" and
                row["image_observer"] == "chatgpt.trek.visual_bookcover_mapping" and
                isinstance(row["openlibrary_edition_title"], str) and
                3 <= len(row["openlibrary_edition_title"]) <= 100 and
                isinstance(row["image_observation"], str) and
                30 <= len(row["image_observation"]) <= 260,
                "image rights/release or visual evidence status changed")
    require(found == set(EXPECTED), "missing candidate")
    return {"status": "HELD_FOR_INDEPENDENT_REVIEW", "source_local_jackets": len(found),
            "public_release_effect": "NONE", "coverage_effect": "NONE"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(), sort_keys=True))
