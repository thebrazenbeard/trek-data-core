#!/usr/bin/env python3
"""Validate source-only first-party episodic image identity without display grant."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path(__file__).with_name("records.json")
EXPECTED_CANDIDATE_SHA256 = "b9d543749f725d8229a41b5e3fa4fad4de40336e5be4796155ae4c3a20225cea"


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate key {key}")
        out[key] = value
    return out


def load_packet(path: Path = RECORD) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"nonfinite {value}")))


def require(predicate: bool, message: str) -> None:
    if not predicate:
        raise ValueError(message)


def validate(packet: dict, root: Path = ROOT) -> None:
    fixed = {
        "schema_version": "1.0.0",
        "batch_id": "LIBRARIAN.FIRST_PARTY.SNW_201_EPISODIC_STILL.20261103",
        "data_status": "SOURCE_LOCAL_RIGHTS_HOLD_NO_PUBLIC_IMAGE_DISPLAY",
        "accepted_main": "0b27926ea8e006354ef99aa04557d2b06baaa4f3",
        "discovery_catalog_path": "explorer/discovery-catalog.json",
        "discovery_catalog_sha256": "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
        "observed_on": "2026-11-03",
        "candidate_count": 1,
        "image_bytes_read_for_hash_and_pixel_review": True,
        "image_bytes_committed": False,
        "public_artwork_release_effect": "NONE",
        "explorer_effect": "NONE",
        "source_work_admission_effect": "NONE",
        "coverage_effect": "NONE",
    }
    require(type(packet) is dict and set(packet) == set(fixed) | {"candidate"}, "root schema drift")
    for key, value in fixed.items():
        require(type(packet[key]) is type(value) and packet[key] == value, f"root mismatch {key}")
    catalog_bytes = (root / fixed["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(catalog_bytes).hexdigest() == fixed["discovery_catalog_sha256"], "source row drift")
    catalog = json.loads(catalog_bytes)
    rows = [item for item in catalog["rows"] if item.get("row_id") == "roster:modern-s2:snw:000"]
    require(len(rows) == 1, "SNW S2E1 discovery row count")
    row = rows[0]
    require((row["title"], row["context"], row["verification_status"], row["admission_effect"])
            == ("The Broken Circle", "SNW S2E1", "UNVERIFIED_METADATA", "NONE"), "accepted row mutation")

    photo = packet["candidate"]
    require(type(photo) is dict, "candidate not object")
    fingerprint = hashlib.sha256(json.dumps(photo, sort_keys=True, separators=(",", ":"),
                                           ensure_ascii=False).encode("utf-8")).hexdigest()
    require(fingerprint == EXPECTED_CANDIDATE_SHA256, "candidate metadata fingerprint mismatch")
    require(photo["source_local_episode_row_id"] == row["row_id"], "episode row link")
    require(photo["source_local_episode_status"] == row["verification_status"], "episode status")
    require(photo["primary_photo_alt"] == "Spock sits in the captain's chair on the bridge in 'The Broken Circle'",
            "must preserve first-party image-to-episode caption")
    require(photo["primary_photo_photographer"] == "UNKNOWN_NOT_ESTABLISHED_FOR_EXACT_ASSET", "fabricated creator")
    require(photo["license_state"] == "NO_PUBLIC_REUSE_LICENSE_FOUND_FOR_EXACT_IMAGE", "false rights grant")
    require(photo["editorial_display_admission"] == "HELD_PERMISSION_AND_RIGHTS_REVIEW_REQUIRED", "false release")
    require(photo["gallery_proves_this_exact_photo_is_in_gallery"] is False, "undocumented cross-gallery identity")
    require(photo["photo_bytes_sha256"] == "96a88ec842d8a10329c09e66ee3442dbe4c8f21a2d04b1e8fce712d5d033e02d",
            "image byte identity")
    for path in RECORD.parent.rglob("*"):
        require(not path.is_symlink(), "symlink inside held partition")
        if path.is_file():
            require(path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"},
                    "image binary in held partition")
            with path.open("rb") as stream:
                prefix = stream.read(20)
            require(not (prefix.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a"))
                         or prefix[:4] == b"RIFF" and prefix[8:12] == b"WEBP"),
                    "disguised image binary in held partition")


if __name__ == "__main__":
    validate(load_packet())
    print("PASS: actual first-party SNW201 still source pinned; image rights remain HELD")
