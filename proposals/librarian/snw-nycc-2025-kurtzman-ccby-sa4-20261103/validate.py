#!/usr/bin/env python3
"""Fail-closed Commons own-work CC BY-SA4 source packet; no public image release."""

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
EXPECTED_CANONICAL = "294e0dc9d77a18187c0a5945af10c7a02cfad3eac591fb7f1568920dbcbd4546"
EXPECTED_MANIFEST = "507ccbc31d4e00261bcd45165460ba097fe4e681eb25f4722377019aa3926187"
EXPECTED_RENDITION_SHA = "407debc7d161010a84043c1d017fe65de5705fd9837f9d2315263fc1831037de"
EXPECTED_ORIGINAL_SHA1 = "af5beaa437808a7c85d1aa9c6a04e50b6cdaf5f6"
EXCLUDED_MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif", ".mp4"}
EXPECTED_HOLDS = {
    "independent_uploader_source_license_and_person_identification": "PENDING",
    "specific_nonendorsement_personality_trademark_context_review": "PENDING",
    "exact_resized_asset_byte_hash_credit_and_sharealike_qa": "PENDING",
    "independent_browser_consent_accessibility_and_hidden_request_qa": "PENDING",
    "owner_explicit_image_publication_decision": "PENDING",
}


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def load_record(path: Path = HERE / "record.json") -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked record")
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    if not isinstance(result, dict):
        raise ValueError("expected JSON object")
    return result


def validate_text(path: Path) -> None:
    if path.stat().st_size > 200_000:
        raise ValueError("oversized source file")
    raw = path.read_bytes()
    if (raw.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04"))
            or raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
            or raw[4:12] in (b"ftypavif", b"ftypavis")):
        raise ValueError("embedded image binary disguised as text")
    try:
        body = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("not UTF-8 packet source") from exc
    if "\x00" in body or any(ord(ch) < 32 and ch not in "\t\r\n" for ch in body):
        raise ValueError("binary controls in source")
    lower = body.lower()
    if (("!" + "[") in lower
            or ("data:" + "image/") in lower
            or re.search(r"<\s*(?:img|picture|source|svg|iframe|video|audio)\b", lower)
            or re.search(r"url\s*\(\s*(?:https?://|data:)", lower)):
        raise ValueError("active image/media embed in source-only packet")
    if path.name == "MANIFEST.md" and hashlib.sha256(raw).hexdigest() != EXPECTED_MANIFEST:
        raise ValueError("MANIFEST source/rights changed without review")


def validate_directory(directory: Path = HERE) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked packet root")
    seen: set[str] = set()
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        if path.is_symlink():
            raise ValueError("unreviewed symlink in packet")
        if path.suffix.lower() in EXCLUDED_MEDIA:
            raise ValueError("image/video binary forbidden in source packet")
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
        raise ValueError("unreviewed source packet file")
    if seen != ALLOWED:
        raise ValueError("missing reviewed packet source: " + ", ".join(sorted(ALLOWED - seen)))
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
            check=False, capture_output=True, text=True, timeout=10,
        )
        if tracked.returncode or set(tracked.stdout.splitlines()) != {prefix + name for name in ALLOWED}:
            raise ValueError("unreviewed tracked packet file or absent reviewed source")


def validate(record: dict, *, directory: Path = HERE) -> int:
    if not isinstance(record, dict) or len(record) != 46:
        raise ValueError("unexpected metadata source packet shape")
    sha = hashlib.sha256(json.dumps(
        record, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if sha != EXPECTED_CANONICAL:
        raise ValueError("pinned author, license, depiction or release facts mutated")
    protected = {
        "status": "HELD_SOURCE_ONLY_NO_PUBLIC_IMAGE",
        "association_status": "CONTEXT_ONLY_REAL_WORLD_PRODUCTION_EVENT_NOT_SOURCE_WORK_BINDING",
        "photo_kind": "REAL_WORLD_CONVENTION_PANEL_PORTRAIT_NOT_FICTIONAL_EPISODE_FRAME",
        "uploader_credited_author": "Vbrunophotog",
        "commons_pinned_oldid": 1225238639,
        "original_bytes_commons_metadata": 9025703,
        "original_sha1_commons_metadata": EXPECTED_ORIGINAL_SHA1,
        "original_sha256_independently_computed": None,
        "verified_rendition_dimensions": [330, 275],
        "verified_rendition_bytes": 27620,
        "verified_rendition_sha256": EXPECTED_RENDITION_SHA,
        "license": "CC_BY_SA_4_0_INTERNATIONAL",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "photo_binary_committed": 0,
        "public_image_display_authorized": False,
        "remote_image_hotlink_committed": False,
        "site_effect": "NONE",
        "work_or_coverage_admission": "NONE",
    }
    for key, expected in protected.items():
        if type(record.get(key)) is not type(expected) or record[key] != expected:
            raise ValueError(f"source/photo/license/publication invariant changed: {key}")
    if record.get("release_holds") != EXPECTED_HOLDS:
        raise ValueError("release approval forged or missing independent gate")
    validate_directory(directory)
    return len(EXPECTED_HOLDS)


def main() -> int:
    try:
        held = validate(load_record())
    except Exception as exc:
        print(f"SNW_2025_NYCC_CC_BY_SA4_SOURCE_INVALID_HOLD: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: own-work Commons CC BY-SA4 source-only, {held} image release holds, 0 public pixels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
