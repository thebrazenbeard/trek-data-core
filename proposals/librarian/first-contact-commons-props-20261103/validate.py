#!/usr/bin/env python3
"""Deterministic, fail-closed check of a HELD film-prop photo source packet.

Passing is *not* a copyright determination or public-image release.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ALLOWED = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
MEDIA_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".avif", ".mp4"}
MAGIC = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"%PDF", b"PK\x03\x04")
EXPECTED_ASSETS = {
    "first-contact-borg-cube-museum-photo": (
        "https://www.flickr.com/photos/joeross/49786189402/",
        "b027b2d81100271d56051502fdaa60a16fb6a41294c56808bac2da547a31caf1",
        51571,
    ),
    "first-contact-phasers-museum-photo": (
        "https://www.flickr.com/photos/joeross/49786193777/",
        "de9457f668d884d786ddef5d145c1fd8ddd5e542c7b45875a98ad18cfa350356",
        28770,
    ),
}
RELEASE_HOLDS = {
    "independent_underlying_prop_rights_editorial_context_review": "PENDING",
    "owner_explicit_public_image_release_decision": "PENDING",
    "exact_public_image_bytes_attribution_sharealike_qa": "PENDING",
    "browser_opt_in_network_accessibility_pages_qa": "PENDING",
}


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_record(path: Path = HERE / "records.json") -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked records.json")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check_text(path: Path) -> None:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 100_000:
        raise ValueError(f"unsafe packet source: {path.name}")
    raw = path.read_bytes()
    if raw.startswith(MAGIC) or (raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"):
        raise ValueError("binary disguised as source")
    body = raw.decode("utf-8", errors="strict")
    if "\x00" in body or any(ord(ch) < 32 and ch not in "\t\r\n" for ch in body):
        raise ValueError("binary/control character in source")
    if path.suffix.lower() in {".md", ".json"} and re.search(
        r"<\s*(?:img|picture|source|svg|iframe|video|audio)\b|!\[|data:image/", body, re.I
    ):
        raise ValueError("embedded or auto-loaded image prohibited in source-only packet")


def check_inventory(directory: Path = HERE, *, check_tracked: bool = True) -> None:
    if directory.is_symlink():
        raise ValueError("symlinked packet root")
    present: set[str] = set()
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        if path.is_symlink() or path.suffix.lower() in MEDIA_SUFFIXES:
            raise ValueError("symlink or media payload in HELD packet")
        if path.is_dir():
            if rel.parts != ("__pycache__",):
                raise ValueError("unreviewed subdirectory")
            continue
        if len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and path.suffix == ".pyc":
            continue
        if len(rel.parts) != 1 or rel.name not in ALLOWED:
            raise ValueError("unreviewed file in HELD packet")
        check_text(path)
        present.add(rel.name)
    if present != ALLOWED:
        raise ValueError("reviewed packet file inventory changed")
    if check_tracked and directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--", prefix],
            capture_output=True, text=True, cwd=ROOT, check=False, timeout=10,
        )
        if tracked.returncode or set(tracked.stdout.splitlines()) != {prefix + item for item in ALLOWED}:
            raise ValueError("git tracked file inventory changed")


def validate(record: dict, *, directory: Path = HERE, check_tracked: bool = True) -> None:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    fixed = {
        "status": "HELD_SOURCE_ONLY_NO_IMAGE_PUBLICATION",
        "catalogue_row_id": "film:film-first-contact",
        "association_status": "PHOTOGRAPHER_CAPTION_SOURCE_LOCAL_FILM_PROP_ASSOCIATION_ONLY",
        "photo_kind": "DOCUMENTARY_MUSEUM_PROP_NOT_FILM_FRAME_STILL_OR_POSTER",
        "photographer": "Joe Ross / Joetography LLC",
        "capture_date": "2019-08-22",
        "source_lineage": "JOE_ROSS_FLICKR_TO_WIKIMEDIA_COMMONS_SINGLE_PHOTOGRAPHER_FAMILY",
        "license": "CC_BY_SA_2_0_GENERIC_PHOTOGRAPHER_CONTRIBUTION_ONLY",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "underlying_prop_rights": "UNRESOLVED",
        "image_binary_committed": 0,
        "remote_image_hotlink_committed": False,
        "public_image_display_authorized": False,
        "site_effect": "NONE",
        "work_or_coverage_admission": "NONE",
    }
    for key, expected in fixed.items():
        if type(record.get(key)) is not type(expected) or record[key] != expected:
            raise ValueError(f"release, identity or copyright gate changed: {key}")
    if record.get("release_holds") != RELEASE_HOLDS:
        raise ValueError("independent release holds dropped or fabricated")
    assets = record.get("assets")
    if not isinstance(assets, list) or len(assets) != len(EXPECTED_ASSETS):
        raise ValueError("unexpected candidate asset inventory")
    if {a.get("id") for a in assets if isinstance(a, dict)} != set(EXPECTED_ASSETS):
        raise ValueError("missing or duplicate candidate ids")
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("asset not object")
        flickr, sha, size = EXPECTED_ASSETS[asset["id"]]
        if (asset.get("original_flickr") != flickr
                or asset.get("rendition_sha256_verified") != sha
                or type(asset.get("rendition_fetched_bytes")) is not int
                or asset["rendition_fetched_bytes"] != size
                or asset.get("rendition_dimensions_verified") != [330, 495]):
            raise ValueError("source identity or preview byte hash changed")
        if "commons.wikimedia.org/wiki/File:" not in asset.get("commons_page", ""):
            raise ValueError("missing Commons file/license page")
        if not asset.get("proposed_caption", "").endswith("not a film frame."):
            raise ValueError("film-frame confusion in proposed caption")
    check_inventory(directory, check_tracked=check_tracked)


def main() -> int:
    try:
        validate(load_record())
    except Exception as exc:
        print(f"FIRST_CONTACT_COMMONS_PROPS_SOURCE_HELD_INVALID: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {len(EXPECTED_ASSETS)} film-prop source photo candidates, {len(RELEASE_HOLDS)} rights/release holds; NO PUBLIC IMAGE EFFECT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
