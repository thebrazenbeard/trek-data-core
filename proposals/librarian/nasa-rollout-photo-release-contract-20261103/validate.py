#!/usr/bin/env python3
"""Fail-closed documentary photo release-criteria proposal; NOT a release tool."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "contract.json"
ACCEPTED = ROOT / "proposals/research/nasa-enterprise-rollout-display-decision-20261103/decision.json"
EXPECTED_DIGEST = "f0cbaadb97d6b759b541bb58187e00f7f6905891323bda4d195da7af283a3eca"
EXPECTED_IMAGE = "e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8"
EXPECTED_URL = "https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg"
PACKET_FILES = {"contract.json", "MANIFEST.md", "validate.py", "test_validate.py"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}
NEEDED_REVIEWS = {
    "source_crosswalk_accepted_on_main": "NOT_YET_ACCEPTED",
    "independent_photo_specific_rights_review": "NOT_RECEIVED",
    "independent_nonpromotional_design_review": "NOT_RECEIVED",
    "accepted_hash_pinned_image_release_manifest": "NOT_RECEIVED",
    "browser_qa_keyboard_mobile_privacy": "NOT_RECEIVED",
    "owner_publication_and_deployment_authorization": "NOT_RECEIVED",
}


def strict_pairs(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError(f"duplicate JSON key: {key}")
        data[key] = value
    return data


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("nonregular or missing JSON")
    parsed = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(parsed, dict):
        raise ValueError("source JSON must be object")
    return parsed


def validate_plaintext(path: Path) -> None:
    if path.stat().st_size > 200_000:
        raise ValueError("oversize source packet content")
    data = path.read_bytes()
    if (data.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04"))
            or data[:4] == b"RIFF" and data[8:12] == b"WEBP"
            or data[4:12] in (b"ftypavif", b"ftypavis")):
        raise ValueError("binary/image magic disguised as source text")
    try:
        content = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8 source text") from exc
    if "\x00" in content or any(ord(ch) < 32 and ch not in "\n\r\t" for ch in content):
        raise ValueError("control or NUL byte in source text")
    if path.suffix == ".md":
        lower = content.lower()
        if any(term in lower for term in ("data:image/", "<svg", "<img")):
            raise ValueError("embedded image disguised as Markdown")


def validate_tree(directory: Path = HERE) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked proposal packet")
    for item in directory.rglob("*"):
        relative = item.relative_to(directory)
        if item.is_symlink():
            raise ValueError("nested symlink in source packet")
        if item.suffix.lower() in IMAGE_SUFFIXES:
            raise ValueError("unexpected image binary in nonpublishing packet")
        if item.is_dir():
            if relative.parts != ("__pycache__",):
                raise ValueError("unapproved nested packet directory")
            continue
        if item.is_file():
            if len(relative.parts) == 1 and relative.name in PACKET_FILES:
                validate_plaintext(item)
                continue
            if (len(relative.parts) == 2 and relative.parts[0] == "__pycache__"
                    and item.suffix == ".pyc"):
                continue
        raise ValueError("unapproved packet file or nested payload")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
            capture_output=True, text=True, timeout=10, check=False,
        )
        if proc.returncode or set(proc.stdout.splitlines()) != {prefix + name for name in PACKET_FILES}:
            raise ValueError("unapproved tracked packet payload or missing reviewed file")


def validate(packet: dict, *, directory: Path = HERE) -> list[str]:
    if len(packet) != 44:
        raise ValueError("release contract schema changed")
    sha = hashlib.sha256(json.dumps(
        packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if sha != EXPECTED_DIGEST:
        raise ValueError("review, image identity, rights, or release state modified without code review")
    for key, expected in {
        "release_state": "HOLD_NO_MEDIA_PUBLICATION",
        "display_eligible_now": False,
        "rights_status": "NASA_INFORMATIONAL_EDITORIAL_REUSE_POTENTIALLY_APPLIES_NOT_A_BLANKET_LICENSE",
        "primary_nasa_photo_url": EXPECTED_URL,
        "primary_nasa_photo_sha256": EXPECTED_IMAGE,
        "primary_nasa_photo_bytes": 165312,
        "photographer_name": None,
        "photographer_or_third_party_rights_verified": False,
        "fictional_work_or_episode_media": False,
        "fictional_episode_or_film_coverage_effect": "NONE",
        "auto_fetch_before_opt_in": False,
        "preload_prefetch_preconnect": False,
        "remote_hotlink_permitted_by_this_contract": False,
        "same_origin_mirror_permitted_by_this_contract": False,
        "binary_files_included": 0,
        "site_files_modified": 0,
    }.items():
        if type(packet.get(key)) is not type(expected) or packet[key] != expected:
            raise ValueError(f"source/rights/publication invariant modified: {key}")
    if packet["acceptance_receipts"] != NEEDED_REVIEWS:
        raise ValueError("independent release receipt was fabricated or promoted")
    if len(packet["review_requirements"]) != 5:
        raise ValueError("material review obligations removed")
    current = read_json(ACCEPTED)
    if (current.get("historical_source_image_sha256") != EXPECTED_IMAGE
            or current.get("historical_source_og_image_exact_url") != EXPECTED_URL
            or current.get("public_display_eligible") is not False
            or current.get("release_authorization") != "NOT_GRANTED"):
        raise ValueError("accepted NASA source decision no longer matches this HOLD")
    validate_tree(directory)
    return [key for key, value in packet["acceptance_receipts"].items() if value != "PASSED_ACCEPTED_ON_MAIN"]


def main() -> int:
    try:
        remaining = validate(read_json(PACKET))
    except Exception as exc:
        print(f"NASA rollout release-contract INVALID/HOLD: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: source-only release criteria HOLD; {len(remaining)} independent acceptance gates remain, 0 images or site effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
