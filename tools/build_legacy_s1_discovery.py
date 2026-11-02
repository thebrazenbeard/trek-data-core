#!/usr/bin/env python3
"""Ingest locally captured official Season 1 listings; verify offline candidates.

Raw HTML is kept outside the repo. Only source hashes, publisher-listed title/
ordinal metadata, CSV observations, and candidate-only bundles are committed.
This is not audiovisual research, independent source authentication, or a
complete/accepted episode denominator. No network calls occur here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
import re
import secrets
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import validate_publisher_episode_roster as roster


BASE = Path("proposals/discovery/legacy-paramount-season1-20261102")
DATE = "2026-11-02"
SLUGS = {
    "tos": "star_trek",
    "tng": "star_trek_the_next_generation",
    "ds9": "star_trek_deep_space_nine",
    "voy": "star_trek_voyager",
    "ent": "enterprise",
}
CARD = re.compile(r'<div\s+class=["\']episode["\']\s*>', re.IGNORECASE)
TITLE = re.compile(r'<div\s+class=["\']epTitle["\']>\s*<h2[^>]*>(.*?)</h2>', re.I | re.S)
SEASON = re.compile(r'<abbr\s+class=["\']seNum["\'][^>]*>\s*S(\d+)\s*</abbr>', re.I)
NUMBER = re.compile(r'<abbr\s+class=["\']epNum["\'][^>]*>\s*E(\d+)\s*</abbr>', re.I)
VALID_TITLE = re.compile(r"[^<>\x00-\x1f\x7f]{2,160}\Z")
INDEX_KEYS = {"schema_version", "proposal_type", "proposal_status", "observed_on",
              "publisher", "independence_group", "admission_effect", "coverage_effect",
              "denominator_effect", "source_pages"}
PAGE_KEYS = {"mission_id", "official_page", "source_body_sha256", "source_body_bytes",
             "observation_csv_sha256", "listed_slot_count"}


def serialized(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_no_symlink(path: Path) -> None:
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError(f"symlink forbidden in source/output path: {path}")


def safe_atomic_write(relative: Path, payload: bytes) -> None:
    """Write through no-follow directory descriptors, refusing symlink leaves.

    The directory FD pins the destination even if an ancestor changes after
    validation. A replace is atomic and cannot follow a racing leaf symlink.
    This deliberately fails closed without POSIX/WSL no-follow support.
    """
    if relative.is_absolute() or not relative.parts or any(part in (".", "..") for part in relative.parts):
        raise ValueError("unsafe legacy discovery output path")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("platform lacks safe no-follow output primitives")
    ensure_no_symlink(ROOT / relative)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(ROOT, flags)
    try:
        for part in relative.parent.parts:
            next_fd = os.open(part, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        try:
            old = os.stat(relative.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(old.st_mode):
                raise ValueError("legacy discovery output must be a regular non-symlink file")
        temporary = f".trek-legacy-{secrets.token_hex(12)}.tmp"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                # The finished metadata is public-repository material; preserve
                # the ordinary 0644 tracked-file mode after private temp write.
                os.fchmod(stream.fileno(), 0o644)
                os.fsync(stream.fileno())
            os.replace(temporary, relative.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        finally:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            except FileNotFoundError:
                pass
    finally:
        os.close(directory_fd)


def official_url(mission: str) -> str:
    return f"https://www.paramountplus.com/shows/{SLUGS[mission]}/episodes/1/"


def parse_cards(raw: bytes, mission: str) -> list[tuple[int, int, str]]:
    if len(raw) < 10_000 or len(raw) > 3_000_000:
        raise ValueError(f"{mission}: page size is outside constrained HTML bounds")
    page = raw.decode("utf-8")
    parts = CARD.split(page)
    if len(parts) < 6 or len(parts) > 40:
        raise ValueError(f"{mission}: unexpected episode-card count")
    result = []
    seen = set()
    for piece in parts[1:]:
        title, season, episode = TITLE.search(piece), SEASON.search(piece), NUMBER.search(piece)
        if not (title and season and episode):
            raise ValueError(f"{mission}: incomplete publisher episode card")
        raw_title = html.unescape(title.group(1)).strip()
        if not VALID_TITLE.fullmatch(raw_title):
            raise ValueError(f"{mission}: malformed publisher episode title")
        key = (int(season.group(1)), int(episode.group(1)))
        if key[0] != 1 or key in seen or (result and key <= result[-1][:2]):
            raise ValueError(f"{mission}: incorrect season, duplicate or unsorted ordinal")
        seen.add(key)
        result.append((key[0], key[1], raw_title))
    return result


def csv_bytes(rows: list[tuple[int, int, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["season", "episode_number", "title"])
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def parse_csv(data: bytes) -> list[tuple[int, int, str]]:
    if len(data) > 16_384:
        raise ValueError("oversized episode observation CSV")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != ["season", "episode_number", "title"]:
        raise ValueError("unexpected episode CSV columns")
    rows = []
    for row in reader:
        if None in row or set(row) != set(reader.fieldnames):
            raise ValueError("malformed episode CSV row")
        if not row["season"].isdigit() or not row["episode_number"].isdigit():
            raise ValueError("non-numeric publisher episode slot")
        title = row["title"]
        if title != title.strip() or not VALID_TITLE.fullmatch(title):
            raise ValueError("invalid title metadata")
        rows.append((int(row["season"]), int(row["episode_number"]), title))
    if not 5 <= len(rows) <= 35 or any(s != 1 for s, _, _ in rows):
        raise ValueError("episode CSV has unexpected season or card count")
    if rows != sorted(rows) or len({(s, n) for s, n, _ in rows}) != len(rows):
        raise ValueError("episode CSV has duplicate or unsorted slots")
    if len({title.casefold() for _, _, title in rows}) != len(rows):
        raise ValueError("duplicate title cannot be silently mapped")
    if csv_bytes(rows) != data:
        raise ValueError("episode CSV is not in deterministic normalized form")
    return rows


def bundle(mission: str, rows: list[tuple[int, int, str]]) -> dict:
    url = official_url(mission)
    result = {
        "record_type": "publisher_episode_roster_proposal",
        "schema_version": "1.0.0",
        "batch_id": f"PARAMOUNT-S1-20261102-{mission.upper()}",
        "mission_id": mission,
        "proposal_status": "CANDIDATE_METADATA_ONLY",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "roster_completeness": "UNRESOLVED",
        "listed_slot_count": len(rows),
        "observation": {
            "publisher": "Paramount+",
            "independence_group": "publisher:paramount",
            "observed_on": DATE,
            "primary_locator": url,
            # The related official series page is not an independent crosscheck.
            "crosscheck_locator": f"https://www.paramountplus.com/shows/{SLUGS[mission]}/",
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None,  # no independently authenticated content receipt
            "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": [
            {"season": season, "episode_number": episode, "title": title,
             "status": "CANDIDATE", "canonical_work_id": None, "source_binding_id": None}
            for season, episode, title in rows
        ],
    }
    catalog = roster.read_json(ROOT / "registry/mission_catalog.json")
    roster.validate(result, catalog)
    return result


def source_index(pages: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "proposal_type": "PUBLISHER_EPISODE_METADATA_SOURCE_OBSERVATIONS",
        "proposal_status": "DISCOVERY_ONLY",
        "observed_on": DATE,
        "publisher": "Paramount+",
        "independence_group": "publisher:paramount",
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "source_pages": pages,
    }


def ingest(raw_dir: Path) -> int:
    root = ROOT / BASE
    if not root.is_dir():
        root.mkdir(parents=True)
    ensure_no_symlink(root)
    # Detect a forged index leaf before making any other generated changes.
    ensure_no_symlink(root / "index.json")
    receipts = []
    for mission in SLUGS:
        html_file = raw_dir / f"{mission}-s1.html"
        ensure_no_symlink(html_file)
        raw = html_file.read_bytes()
        rows = parse_cards(raw, mission)
        observation = csv_bytes(rows)
        csv_path = root / f"{mission}.csv"
        bundle_path = root / mission / "bundle.json"
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        for path in (csv_path, bundle_path):
            ensure_no_symlink(path)
        safe_atomic_write(BASE / f"{mission}.csv", observation)
        safe_atomic_write(BASE / mission / "bundle.json", serialized(bundle(mission, rows)))
        receipts.append({
            "mission_id": mission,
            "official_page": official_url(mission),
            "source_body_sha256": sha(raw),
            "source_body_bytes": len(raw),
            "observation_csv_sha256": sha(observation),
            "listed_slot_count": len(rows),
        })
        print(f"{mission}: observed {len(rows)} publisher listing rows; source SHA-256 {sha(raw)}")
    safe_atomic_write(BASE / "index.json", serialized(source_index(receipts)))
    return 0


def check() -> int:
    root = ROOT / BASE
    index_path = root / "index.json"
    ensure_no_symlink(index_path)
    index = roster.read_json(index_path)
    if (not isinstance(index, dict) or set(index) != INDEX_KEYS or
            {key: index[key] for key in INDEX_KEYS - {"source_pages"}} !=
            {key: source_index([])[key] for key in INDEX_KEYS - {"source_pages"}}):
        raise ValueError("legacy publisher source index metadata invalid")
    pages = index["source_pages"]
    if not isinstance(pages, list) or len(pages) != len(SLUGS):
        raise ValueError("legacy publisher source count invalid")
    for mission, page in zip(SLUGS, pages):
        if not isinstance(page, dict) or set(page) != PAGE_KEYS or page["mission_id"] != mission:
            raise ValueError("unexpected source page identity or fields")
        if page["official_page"] != official_url(mission):
            raise ValueError("publisher locator mismatch")
        if (not re.fullmatch(r"[a-f0-9]{64}", str(page["source_body_sha256"])) or
                type(page["source_body_bytes"]) is not int or
                not 10_000 <= page["source_body_bytes"] <= 3_000_000):
            raise ValueError("unbounded or invalid source HTML receipt")
        csv_path = root / f"{mission}.csv"
        bundle_path = root / mission / "bundle.json"
        for path in (csv_path, bundle_path):
            ensure_no_symlink(path)
        data = csv_path.read_bytes()
        if sha(data) != page["observation_csv_sha256"]:
            raise ValueError(f"{mission}: observed CSV hash mismatch")
        rows = parse_csv(data)
        if page["listed_slot_count"] != len(rows):
            raise ValueError(f"{mission}: listed count mismatch")
        if bundle_path.read_bytes() != serialized(bundle(mission, rows)):
            raise ValueError(f"{mission}: generated bundle is stale or modified")
    print(f"LEGACY_PARAMOUNT_S1_CHECKED: {sum(p['listed_slot_count'] for p in pages)} publisher listing rows across {len(pages)} series")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest-dir", type=Path, help="temporary directory with <mission>-s1.html files")
    parser.add_argument("--check", action="store_true", help="verify committed CSV, receipts and bundles offline")
    args = parser.parse_args(argv)
    try:
        if args.check == bool(args.ingest_dir):
            raise ValueError("choose exactly --check or --ingest-dir")
        return check() if args.check else ingest(args.ingest_dir)
    except (OSError, ValueError, roster.Rejected) as exc:
        print(f"LEGACY_PARAMOUNT_S1_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
