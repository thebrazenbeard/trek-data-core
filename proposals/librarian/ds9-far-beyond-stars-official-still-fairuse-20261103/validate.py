#!/usr/bin/env python3
"""Fail-closed exact-still §107 source packet; does not adjudicate fair use."""

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
EXPECTED_CANONICAL = "7f5d6672c513a19f73e257904f7257c7da93b7d3b9fafe483ff9f2aeeb19e387"
EXPECTED_MANIFEST = "ebc72b8a4ef233732f90b018f48a5f64dc582ff7594b4eb0a2b57114c2bdb648"
EXPECTED_STILL_SHA = "d57a6dcae646c2abb3d35e19fcd046d4674dbe3d1c060f26212d808431e51b27"
EXPECTED_160_SHA = "6b4b2cac0e92cb737fbe4631e2815a715e6da7416faf39c58c1061dc43399763"
EXCLUDED_MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif", ".mp4", ".webm"}
EXPECTED_HOLDS = {
    "independent_exact_episode_still_identity_and_source_review": "PENDING",
    "independent_specific_107_four_factor_thumbnail_context_review": "PENDING",
    "exact_160px_derivative_byte_hash_and_accessibility_review": "PENDING",
    "browser_consent_network_and_no_decorative_hero_review": "PENDING",
    "owner_specific_image_release_decision": "PENDING",
}


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_record(path: Path = HERE / "record.json") -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source packet missing or symlinked")
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    if not isinstance(result, dict):
        raise ValueError("source packet root must be object")
    return result


def validate_source_text(path: Path) -> None:
    if path.stat().st_size > 200_000:
        raise ValueError("oversized packet text")
    raw = path.read_bytes()
    if (raw.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04"))
            or raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
            or raw[4:12] in (b"ftypavif", b"ftypavis")):
        raise ValueError("image/binary magic disguised as source")
    try:
        body = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("not UTF-8 source") from exc
    if "\x00" in body or any(ord(char) < 32 and char not in "\r\n\t" for char in body):
        raise ValueError("binary controls in source")
    lower = body.lower()
    if (("!" + "[") in lower
            or ("data:" + "image/") in lower
            or re.search(r"<\s*(?:img|picture|source|svg|video|audio|iframe)\b", lower)
            or re.search(r"url\s*\(\s*(?:https?://|data:)", lower)):
        raise ValueError("unreviewed live media embed/hotlink")
    if path.name == "MANIFEST.md" and hashlib.sha256(raw).hexdigest() != EXPECTED_MANIFEST:
        raise ValueError("MANIFEST rights/source statement changed")


def validate_directory(directory: Path = HERE) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked packet root")
    seen: set[str] = set()
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        if path.is_symlink():
            raise ValueError("symlink in packet")
        if path.suffix.lower() in EXCLUDED_MEDIA:
            raise ValueError("unexpected image/video asset")
        if path.is_dir():
            if rel.parts != ("__pycache__",):
                raise ValueError("unreviewed nested packet directory")
            continue
        if path.is_file() and len(rel.parts) == 1 and rel.name in ALLOWED:
            validate_source_text(path)
            seen.add(rel.name)
            continue
        if path.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and path.suffix == ".pyc":
            continue
        raise ValueError("unreviewed packet file")
    if seen != ALLOWED:
        raise ValueError("missing required packet source: " + ", ".join(sorted(ALLOWED - seen)))
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
            check=False, capture_output=True, text=True, timeout=10,
        )
        if tracked.returncode or set(tracked.stdout.splitlines()) != {prefix + name for name in ALLOWED}:
            raise ValueError("tracked source-only inventory not exact")


def validate(record: dict, *, directory: Path = HERE) -> int:
    if not isinstance(record, dict) or len(record) != 56:
        raise ValueError("unreviewed source packet schema")
    canonical_sha = hashlib.sha256(json.dumps(
        record, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if canonical_sha != EXPECTED_CANONICAL:
        raise ValueError("pinned evidence/legal facts changed")
    fixed = {
        "status": "HELD_107_THUMBNAIL_SOURCE_ONLY_NOT_PUBLICATION",
        "association_status": "SOURCE_LOCAL_EXACT_EPISODE_CREDIT_NOT_ACCEPTED_BINDING",
        "source_image_kind": "OFFICIAL_PUBLISHER_CAPTIONED_IN_EPISODE_STILL_NOT_A_RECAP_ONLY_IMAGE",
        "episode_name": "Far Beyond the Stars",
        "series_name": "Star Trek: Deep Space Nine",
        "article_served_variant_sha256": EXPECTED_STILL_SHA,
        "article_served_variant_bytes": 40996,
        "thumbnail_preferred_sha256": EXPECTED_160_SHA,
        "thumbnail_preferred_dimensions": [160, 122],
        "thumbnail_preferred_bytes": 5452,
        "permission_class": "NO_OPEN_IMAGE_LICENSE_EVIDENCED_SECTION_107_FAIR_USE_REVIEW_CANDIDATE",
        "fair_use_result": "BOUNDED_FOUR_FACTOR_PLAUSIBLE_THUMBNAIL_CANDIDATE_NOT_LEGAL_CLEARANCE",
        "image_binary_committed": 0,
        "public_image_display_authorized": False,
        "remote_hotlink_committed": False,
        "site_effect": "NONE",
        "work_or_coverage_admission": "NONE",
    }
    for key, expected in fixed.items():
        if type(record.get(key)) is not type(expected) or record[key] != expected:
            raise ValueError(f"identity, rights or publication invariant changed: {key}")
    if record.get("release_holds") != EXPECTED_HOLDS:
        raise ValueError("independent release gate falsely approved or removed")
    validate_directory(directory)
    return len(EXPECTED_HOLDS)


def main() -> int:
    try:
        holds = validate(read_record())
    except Exception as exc:
        print(f"DS9_FAR_BEYOND_THE_STARS_SOURCE_INVALID_HOLD: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: DS9 exact-still 160px §107 source candidate, {holds} independent release holds, zero public media")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
