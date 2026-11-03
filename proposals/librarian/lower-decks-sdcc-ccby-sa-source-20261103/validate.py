#!/usr/bin/env python3
"""Fail-closed CC BY-SA documentary photo source packet; no release approval."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ALLOWED = {"record.json", "MANIFEST.md", "validate.py", "test_validate.py"}
CONTRACT = HERE / "record.json"
EXPECTED_CANONICAL = "8202c336b5898df36af28de2214d3fbf3454312003b7add7bb56e1a1935618e6"
EXPECTED_MANIFEST = "d8f009e023dff98bef5c0870bcb74e232df934a6405049fd9dc099ec78f0c6b1"
EXPECTED_RENDITION_SHA = "bdebd31dde804b2ae75a4dcc51d85cd33d24c471cc21356e61c61d0eb7be1853"
EXPECTED_ORIGINAL_SHA1 = "08ace751dbddcab29c128b6912c4e377b367fb31"
EXPECTED_FLICKR = "https://www.flickr.com/photos/gageskidmore/48443838191/"
EXPECTED_LICENSE = "https://creativecommons.org/licenses/by-sa/2.0/"
EXCLUDED_MEDIA = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif", ".mp4"}
EXPECTED_HOLDS = {
    "source_original_sha256_or_documented_original_fetch_limit": "ORIGINAL_FETCH_HTTP429_HELD_USE_ONLY_EXACT_RENDITION",
    "independent_image_rights_context_and_attribution_review": "PENDING",
    "exact_display_asset_hash_and_resizing_sharealike_qa": "PENDING",
    "independent_browser_network_caption_consent_qa": "PENDING",
    "owner_explicit_image_release_decision": "PENDING",
}


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    value: dict = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON field: {key}")
        value[key] = item
    return value


def read_record(path: Path = CONTRACT) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked record")
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError("record root not object")
    return value


def validate_text(path: Path) -> None:
    if path.stat().st_size > 200_000:
        raise ValueError("oversized packet file")
    raw = path.read_bytes()
    if (raw.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04"))
            or raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
            or raw[4:12] in (b"ftypavif", b"ftypavis")):
        raise ValueError("image/binary magic disguised as source")
    try:
        body = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8") from exc
    if "\x00" in body or any(ord(ch) < 32 and ch not in "\t\r\n" for ch in body):
        raise ValueError("binary control characters in source")
    lower = body.lower()
    if (("data:" + "image/") in lower
            or ("!" + "[") in lower
            or re.search(r"<\s*(?:img|picture|source|svg|iframe|video|audio)\b", lower)
            or re.search(r"url\s*\(\s*(?:https?://|data:)", lower)):
        raise ValueError("embedded/hotlinked media in held source packet")
    if path.name == "MANIFEST.md" and hashlib.sha256(raw).hexdigest() != EXPECTED_MANIFEST:
        raise ValueError("MANIFEST source statement changed without review")


def validate_directory(directory: Path = HERE) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked packet root")
    seen: set[str] = set()
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        if path.is_symlink():
            raise ValueError("symlink in source packet")
        if path.suffix.lower() in EXCLUDED_MEDIA:
            raise ValueError("actual media bytes unreviewed")
        if path.is_dir():
            if rel.parts != ("__pycache__",):
                raise ValueError("nested packet directory")
            continue
        if path.is_file() and len(rel.parts) == 1 and rel.name in ALLOWED:
            validate_text(path)
            seen.add(rel.name)
            continue
        if path.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and path.suffix == ".pyc":
            continue
        raise ValueError("unexpected packet source")
    if seen != ALLOWED:
        raise ValueError("missing reviewed source: " + ", ".join(sorted(ALLOWED - seen)))
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
            capture_output=True, text=True, check=False, timeout=10,
        )
        if tracked.returncode or set(tracked.stdout.splitlines()) != {prefix + name for name in ALLOWED}:
            raise ValueError("tracked file inventory deviates from reviewed packet")


def validate(record: dict, *, directory: Path = HERE) -> int:
    if not isinstance(record, dict) or len(record) != 48:
        raise ValueError("unexpected source record shape")
    digest = hashlib.sha256(json.dumps(
        record, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_CANONICAL:
        raise ValueError("pinned source, license or event assertion mutated")
    fixed = {
        "status": "HELD_SOURCE_ONLY_NO_IMAGE_PUBLICATION",
        "association_status": "SOURCE_LOCAL_REAL_WORLD_EVENT_NOT_GOVERNED_SOURCE_WORK_BINDING",
        "photo_kind": "DOCUMENTARY_CONVENTION_PANEL_NOT_EPISODE_FRAME_STILL_OR_POSTER",
        "photographer": "Gage Skidmore",
        "original_flickr": EXPECTED_FLICKR,
        "original_size_from_commons_bytes": 16625228,
        "original_sha1_from_commons_metadata": EXPECTED_ORIGINAL_SHA1,
        "original_sha256_independently_computed": None,
        "rendition_fetched_bytes": 142209,
        "rendition_sha256_verified": EXPECTED_RENDITION_SHA,
        "license": "CC_BY_SA_2_0_GENERIC",
        "license_url": EXPECTED_LICENSE,
        "image_binary_committed": 0,
        "remote_image_hotlink_committed": False,
        "public_image_display_authorized": False,
        "site_effect": "NONE",
        "work_or_coverage_admission": "NONE",
    }
    for key, expected in fixed.items():
        if type(record.get(key)) is not type(expected) or record[key] != expected:
            raise ValueError(f"source/license/publication invariant changed: {key}")
    if record["release_holds"] != EXPECTED_HOLDS:
        raise ValueError("fabricated or omitted independent release review")
    validate_directory(directory)
    return len(EXPECTED_HOLDS)


def main() -> int:
    try:
        holds = validate(read_record())
    except Exception as exc:
        print(f"LOWER_DECKS_SDDC_CCBYSA_SOURCE_INVALID_HOLD: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: Lower Decks documentary CC BY-SA 2.0 source-only, {holds} release holds, zero images committed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
