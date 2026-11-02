#!/usr/bin/env python3
"""Build film *discovery* metadata without admitting canonical research.

The source proposal is explicitly human-curated. This builder checks its
internal shape and reproduces the public candidate-only view; it does not
authenticate external webpages, sources, or audiovisual films.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


INPUT = Path("proposals/librarian/films-official-index-20261102/bundle.json")
OUTPUT = Path("explorer/film-catalog.json")
SOURCE_GROUP = "publisher:startrek.com"
CATALOG_URL = "https://www.startrek.com/series-and-movies"
SECTION_31_URL = "https://www.startrek.com/news/star-trek-section-31-premieres-january-24"
SNAPSHOT = "OFFICIAL-TREK-FILMS-20261102-001"
KEYS = {
    "proposal_type", "proposal_only", "coverage_effect", "admission_effect",
    "snapshot_id", "observed_on", "source_group", "catalog_locator", "films",
}
FILM_KEYS = {"id", "title", "source_locator", "work_type", "discovery_source"}
ID_PATTERN = re.compile(r"film-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DATE_PATTERN = re.compile(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]\Z")


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def _bad_constant(value: str) -> None:
    raise ValueError(f"non-JSON numeric constant: {value}")


def read_proposal(repo: Path) -> dict:
    path = repo / INPUT
    if repo.is_symlink() or path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError("film discovery source cannot be a symlink")
    if not path.is_file() or path.stat().st_size > 128_000:
        raise ValueError("film discovery proposal missing or too large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_keys, parse_constant=_bad_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed film proposal JSON") from exc
    return data


def _official_url(url: object, source: str) -> bool:
    if not isinstance(url, str):
        return False
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != "www.startrek.com" or parts.query or parts.fragment:
        return False
    if source == "OFFICIAL_DIRECTORY":
        return bool(re.fullmatch(r"/movies/[a-z0-9-]+", parts.path))
    return source == "OFFICIAL_ANNOUNCEMENT" and url == SECTION_31_URL


def validate(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != KEYS:
        raise ValueError("unexpected film proposal fields (including any admission field)")
    if data["proposal_type"] != "FILM_DISCOVERY_METADATA" or data["proposal_only"] is not True:
        raise ValueError("film entries must remain proposals")
    if data["coverage_effect"] != "NONE" or data["admission_effect"] != "NONE":
        raise ValueError("film discovery may not advance coverage or admission")
    if data["source_group"] != SOURCE_GROUP or data["catalog_locator"] != CATALOG_URL:
        raise ValueError("film proposal publisher lineage mismatch")
    if data["snapshot_id"] != SNAPSHOT or not isinstance(data["observed_on"], str) or not DATE_PATTERN.fullmatch(data["observed_on"]):
        raise ValueError("film discovery snapshot or observation date invalid")
    films = data["films"]
    if not isinstance(films, list) or not 1 <= len(films) <= 100:
        raise ValueError("film discovery list must contain bounded candidates")
    seen: set[str] = set()
    locators: set[str] = set()
    normalized: list[dict] = []
    for i, item in enumerate(films):
        if not isinstance(item, dict) or set(item) != FILM_KEYS:
            raise ValueError(f"film {i}: unexpected or admission-like fields")
        ident, title, locator = item["id"], item["title"], item["source_locator"]
        source, work_type = item["discovery_source"], item["work_type"]
        if not isinstance(ident, str) or len(ident) > 80 or not ID_PATTERN.fullmatch(ident) or ident in seen:
            raise ValueError(f"film {i}: duplicate or invalid candidate ID")
        seen.add(ident)
        if not isinstance(title, str) or not 3 <= len(title) <= 140 or title != title.strip() or any(ord(c) < 32 for c in title):
            raise ValueError(f"film {i}: invalid display title")
        if not _official_url(locator, source):
            raise ValueError(f"film {i}: source locator is not a permitted official publisher locator")
        if locator in locators:
            raise ValueError(f"film {i}: duplicate official publisher locator")
        locators.add(locator)
        if source == "OFFICIAL_DIRECTORY" and work_type != "FEATURE_FILM":
            raise ValueError(f"film {i}: source/work type mismatch")
        if source == "OFFICIAL_ANNOUNCEMENT" and (ident != "film-section-31" or work_type != "STREAMING_ORIGINAL_FILM"):
            raise ValueError(f"film {i}: unsupported supplementary film attribution")
        normalized.append({
            "id": ident,
            "title": title,
            "source_locator": locator,
            "source_group": SOURCE_GROUP,
            "work_type": work_type,
            "discovery_source": source,
            "verification_status": "UNVERIFIED_METADATA",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "DISCOVERY_ONLY",
        "coverage_effect": "NONE",
        "film_count": len(normalized),
        "source_group": SOURCE_GROUP,
        "observed_on": data["observed_on"],
        "snapshot_id": data["snapshot_id"],
        "films": normalized,
    }


def build(root: Path) -> bytes:
    result = validate(read_proposal(root))
    return (json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated output differs from the committed view")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        blob = build(args.repo_root)
        path = args.repo_root / OUTPUT
        if args.repo_root.is_symlink() or path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
            raise ValueError("refusing symlink output path")
        if args.check:
            if not path.is_file() or path.read_bytes() != blob:
                raise ValueError("film catalog is stale; run tools/build_film_catalog.py")
        else:
            path.write_bytes(blob)
    except (OSError, ValueError) as exc:
        print(f"film catalog: {exc}", file=sys.stderr)
        return 1
    print("film catalog: checked" if args.check else "film catalog: generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
