#!/usr/bin/env python3
"""Fail-closed photo-specific CC BY attribution proposal, not release approval."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
ALLOWED = {"contract.json", "MANIFEST.md", "validate.py", "test_validate.py"}
EXPECTED_CANON = "bbd7c00805b8a7f2e76d36d480a38f4c37c65170410129f7313a0a208e3e8f83"
EXPECTED_MANIFEST = "dad9f5c8d092962ed903401dbe15fb42ec47149d74ff4c16e14c48dd97e7692f"
EXPECTED_PHOTO_SHA = "7fd481633086f97e7b05e0eccbd3515a90d44f4fa7ce1255180007d9d13b4250"
EXPECTED_PHOTO_URL = "https://upload.wikimedia.org/wikipedia/commons/a/a4/Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg"
EXCLUDED_MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
EXPECTED_REVIEWS = {
    "photo_copyright_license_source_identity": "SOURCE_ONLY_PRIOR_REVIEW_NO_PUBLIC_RELEASE",
    "depicted_persons_marks_and_nonpromotional_context": "PENDING",
    "exact_modified_asset_change_notice_and_hash": "PENDING",
    "independent_live_browser_consent_caption_qa": "PENDING",
    "explicit_image_release_manifest_and_publication_decision": "PENDING",
}


def unique_json(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError(f"duplicate JSON key: {key}")
        data[key] = value
    return data


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked source packet")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_json)
    if not isinstance(data, dict):
        raise ValueError("source packet is not a map")
    return data


def validate_text(path: Path) -> None:
    if path.stat().st_size > 200_000:
        raise ValueError("oversized packet source")
    raw = path.read_bytes()
    if (raw.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04"))
            or raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
            or raw[4:12] in (b"ftypavif", b"ftypavis")):
        raise ValueError("image/binary magic disguised as source text")
    try:
        body = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8 source text") from exc
    if "\x00" in body or any(ord(ch) < 32 and ch not in "\t\r\n" for ch in body):
        raise ValueError("binary controls in source text")
    lower = body.lower()
    if (("data:" + "image/") in lower
            or ("!" + "[") in lower
            or re.search(r"<\s*(?:img|picture|source|svg|iframe|video|audio)\b", lower)
            or re.search(r"url\s*\(\s*(?:https?://|data:)", lower)):
        raise ValueError("embedded/external active image markup in held contract")
    if path.name == "MANIFEST.md" and hashlib.sha256(raw).hexdigest() != EXPECTED_MANIFEST:
        raise ValueError("source narrative MANIFEST digest changed without review")


def validate_directory(directory: Path = HERE) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked source packet directory")
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        if path.is_symlink():
            raise ValueError("symlink inside source packet")
        if path.suffix.lower() in EXCLUDED_MEDIA:
            raise ValueError("unexpected image binary")
        if path.is_dir():
            if rel.parts != ("__pycache__",):
                raise ValueError("unexpected nested packet directory")
            continue
        if path.is_file():
            if len(rel.parts) == 1 and rel.name in ALLOWED:
                validate_text(path)
                continue
            if len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and path.suffix == ".pyc":
                continue
        raise ValueError("unreviewed file in source packet")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
            capture_output=True, text=True, timeout=10, check=False,
        )
        if tracked.returncode or set(tracked.stdout.splitlines()) != {prefix + name for name in ALLOWED}:
            raise ValueError("unreviewed tracked asset or missing reviewed file")


def validate(contract: dict, *, directory: Path = HERE) -> int:
    if not isinstance(contract, dict) or len(contract) != 47:
        raise ValueError("unexpected contract schema")
    digest = hashlib.sha256(json.dumps(
        contract, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_CANON:
        raise ValueError("source/license/attribution/release digest changed without code review")
    fixed = {
        "status": "HELD_PHOTO_SPECIFIC_EDITORIAL_DISPLAY_CONTRACT",
        "photographer": "Dick Thomas Johnson",
        "original_image_url": EXPECTED_PHOTO_URL,
        "original_image_sha256": EXPECTED_PHOTO_SHA,
        "original_image_bytes": 4134183,
        "license": "CC_BY_2_0_GENERIC",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "public_image_display_authorized": False,
        "fictional_film_still_or_poster": False,
        "scene_or_episode_truth_claim": False,
        "work_or_coverage_admission": "NONE",
        "image_bytes_committed": 0,
        "site_effect": "NONE",
        "preopt_image_requests": 0,
    }
    for key, expected in fixed.items():
        if type(contract.get(key)) is not type(expected) or contract[key] != expected:
            raise ValueError(f"protected photograph or release invariant changed: {key}")
    if contract["independent_reviews"] != EXPECTED_REVIEWS:
        raise ValueError("independent review falsely promoted or omitted")
    validate_directory(directory)
    return sum(value == "PENDING" for value in contract["independent_reviews"].values())


def main() -> int:
    try:
        held = validate(read_json(CONTRACT))
    except Exception as exc:
        print(f"BEYOND_PREMIERE_LICENSE_CONTRACT_INVALID_HOLD: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: CC BY 2.0 documentary attribution source-only; {held} independent release holds, 0 public images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
