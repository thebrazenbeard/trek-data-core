#!/usr/bin/env python3
"""Deterministic held Sisko *paperback* image-provenance packet check.

This validates only a reviewed source-local observation. It does not download
images, judge fair use, or authorize any Explorer/display effect.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path("proposals/librarian/prh-sisko-paperback-cover-20261103")
DIRECTORY = Path("explorer/discovery-catalog.json")
EXPECTED_DIRECTORY_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
EXPECTED_PACKET_SHA256 = "c83f134f3bd6f495c0b64c0bac1a98b097705c22008460ac679d5dc7968b6fcb"
ALLOWED_PACKET_FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def checked_json(path: Path) -> tuple[dict, bytes]:
    require(path.is_file() and not path.is_symlink(), f"missing/symlink file {path}")
    raw = path.read_bytes()
    decoded = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    require(type(decoded) is dict, "JSON root must be object")
    return decoded, raw


def validate(root: Path = ROOT) -> dict:
    root = Path(root)
    folder = root / PACKET
    require(folder.is_dir() and not folder.is_symlink(), "missing/symlink packet directory")
    contents = {entry.name for entry in folder.iterdir()}
    if "__pycache__" in contents:
        # Running the Python fixture creates compiler cache artifacts, which
        # are not packet artifacts and must never be committed as evidence.
        cache = folder / "__pycache__"
        require(cache.is_dir() and not cache.is_symlink(), "unsafe bytecode cache")
        for entry in cache.iterdir():
            require(entry.is_file() and not entry.is_symlink() and
                    re.fullmatch(r"(?:validate|test_validate)\.cpython-\d+\.pyc", entry.name)
                    is not None and entry.read_bytes().startswith(importlib.util.MAGIC_NUMBER),
                    "unexpected bytecode cache content")
        if (root / ".git").exists():
            tracked = subprocess.run(
                ["git", "ls-files", "--cached", "--", str(PACKET / "__pycache__")],
                cwd=root, capture_output=True, check=True, text=True,
            )
            require(not tracked.stdout.strip(), "tracked bytecode is not allowed")
        contents.remove("__pycache__")
    require(contents == ALLOWED_PACKET_FILES, "unexpected or missing packet file")
    require(all((folder / name).is_file() and not (folder / name).is_symlink()
                for name in contents), "nested or linked packet content")

    record, raw = checked_json(folder / "records.json")
    require(sha256(raw) == EXPECTED_PACKET_SHA256, "unreviewed packet bytes")
    require(record["schema_version"] == "1.0.0", "unexpected schema")
    require(record["batch_id"] == "ARTWORK.PRH.SISKO.PAPERBACK.20261103", "wrong batch")
    require(record["role"] == "LIBRARIAN", "wrong role")
    require(record["accepted_main_sha"] == "adf2ac38a4b3be24821663a2ae88601be17c3684", "wrong accepted snapshot")
    require(record["accepted_directory_sha256"] == EXPECTED_DIRECTORY_SHA256, "wrong source pin")
    require(record["status"] == "SOURCE_LOCAL_ARTWORK_CANDIDATE_HELD", "must remain held")
    require(all(record[key] == "NONE" for key in ("admission_effect", "coverage_effect", "explorer_effect")),
            "unreviewed effect")
    require(record["public_image_display_authorized"] is False and
            record["image_bytes_in_repository"] is False, "public effect or binary claim")

    candidate = record["candidate"]
    require(candidate["row_id"] == "literature:prh-autobiography-sisko", "wrong source-local row")
    require(candidate["medium"] == "LITERATURE" and candidate["format"] == "PAPERBACK", "wrong medium or format")
    require(candidate["isbn_13"] == "9781803366258", "wrong paperback ISBN")
    require(candidate["publisher_image_url"] ==
            "https://images3.penguinrandomhouse.com/cover/9781803366258", "unreviewed image source")
    require(candidate["publisher_image_sha256"] ==
            "2785f8b2bc671483813d69a56325585dbd8751c81490e44dbc0e118f3e132f0e", "wrong reviewed bytes")
    require(candidate["publisher_image_width"] == 298 and
            candidate["publisher_image_height"] == 450 and
            candidate["publisher_image_bytes"] == 29616, "wrong reviewed dimensions/size")
    require(candidate["rights_status"] == "COPYRIGHT_UNRESOLVED_FAIR_USE_ANALYSIS_PENDING" and
            candidate["display_eligible"] is False, "candidate gained unreviewed release")

    counterexample = record["edition_counterexample"]
    require(counterexample["queried_paperback_isbn"] == candidate["isbn_13"] and
            counterexample["open_library_paperback_http_status"] == 404, "paperback endpoint mismatched")
    require(counterexample["separate_hardcover_isbn"] == "9781803366234" and
            counterexample["open_library_hardcover_cover_id"] == 14433753 and
            counterexample["same_edition_as_accepted_paperback"] is False and
            counterexample["may_project_hardcover_image_onto_paperback_row"] is False,
            "hardcover silently promoted to paperback")
    require(record["fair_use_candidate_scope"]["legal_conclusion"] == "NOT_DETERMINED" and
            record["fair_use_candidate_scope"]["release_state"] == "HELD_OWNER_AND_INDEPENDENT_RIGHTS_REVIEW",
            "unreviewed legal conclusion or release")

    directory, directory_raw = checked_json(root / DIRECTORY)
    require(sha256(directory_raw) == EXPECTED_DIRECTORY_SHA256, "accepted directory bytes drifted")
    hits = [r for r in directory["rows"] if r.get("row_id") == candidate["row_id"]]
    require(len(hits) == 1, "source-local Sisko row unresolved")
    source = hits[0]
    require(source.get("medium") == "LITERATURE" and
            source.get("title") == candidate["title"] and
            source.get("source_locator") == candidate["publisher_product_url"] and
            any("Paperback ISBN 9781803366258" == detail for detail in source.get("details", [])),
            "publisher paperback edition does not match accepted row")

    return {"status": "HELD_SOURCE_ONLY", "batch": record["batch_id"],
            "validated_source_rows": 1, "image_bytes_published": 0}


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
