#!/usr/bin/env python3
"""Bounded Season 7 publisher listing extraction; metadata proposals only.

Three source HTML captures stay outside git. The committed bundle, CSV and
content-hash receipts can be checked offline without reading restricted media.
No episode is admitted, reconciled, watched, or counted toward coverage.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import secrets
import stat
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import build_legacy_s3_discovery as source_tools
from tools import publisher_output_directory as dirguard
from tools import validate_publisher_episode_roster as roster

BASE = Path("proposals/discovery/publisher-season7-20261102")
DATE = "2026-11-02"
SEASON = 7
SLUGS = {
    "tng": "star_trek_the_next_generation",
    "ds9": "star_trek_deep_space_nine",
    "voy": "star_trek_voyager",
}
INDEX_KEYS = source_tools.INDEX_KEYS
PAGE_KEYS = source_tools.PAGE_KEYS


class _CanonicalLinks(HTMLParser):
    """Preserve duplicate attributes; never trust a spoofed publisher locator."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[list[tuple[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "link":
            return
        rels = [value for key, value in attrs if key == "rel"]
        if any(value is not None and "canonical" in value.lower().split() for value in rels):
            self.candidates.append(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def validate_canonical(page: str, mission: str) -> None:
    links = _CanonicalLinks()
    links.feed(page)
    links.close()
    if len(links.candidates) != 1:
        raise ValueError(f"{mission}: missing or duplicate canonical publisher locator")
    attributes = links.candidates[0]
    rels = [value for key, value in attributes if key == "rel"]
    hrefs = [value for key, value in attributes if key == "href"]
    if (len(rels) != 1 or len(hrefs) != 1 or
            rels[0] is None or rels[0].lower().split() != ["canonical"] or
            hrefs[0] != official_url(mission)):
        raise ValueError(f"{mission}: forged or ambiguous canonical publisher locator")


def safe_atomic_write(relative: Path, payload: bytes) -> None:
    """Pin output directories with no-follow descriptors under this branch root."""
    if (relative.is_absolute() or not relative.parts or
            any(part in (".", "..") for part in relative.parts)):
        raise ValueError("unsafe Season 7 output path")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ValueError("platform lacks safe no-follow output primitives")
    source_tools.ensure_no_symlink(ROOT / relative)
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
                raise ValueError("Season 7 output must be a regular file")
        temporary = f".trek-s7-{secrets.token_hex(12)}.tmp"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
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
    return f"https://www.paramountplus.com/shows/{SLUGS[mission]}/episodes/{SEASON}/"


def read_raw_response(path: Path) -> bytes:
    """Bounded regular-file source read resistant to link/special-file races."""
    source_tools.ensure_no_symlink(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or not 10_000 <= before.st_size <= 3_000_000:
        raise ValueError("publisher source must be a bounded regular HTML file")
    if not hasattr(os, "O_NONBLOCK") or not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("safe no-follow raw-input open unavailable")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or opened.st_ino != before.st_ino
                or opened.st_dev != before.st_dev):
            raise ValueError("publisher source path changed during open")
        raw = stream.read(3_000_001)
    if not 10_000 <= len(raw) <= 3_000_000:
        raise ValueError("publisher source response exceeds bounded size")
    return raw


def parse_cards(raw: bytes, mission: str) -> list[tuple[int, int, str]]:
    if not 10_000 <= len(raw) <= 3_000_000:
        raise ValueError(f"{mission}: source response size out of bounds")
    try:
        page = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{mission}: source response is not UTF-8") from exc
    validate_canonical(page, mission)
    parts = source_tools.CARD.split(page)
    if not 6 <= len(parts) <= 41:
        raise ValueError(f"{mission}: unexpected count of publisher episode cards")
    result: list[tuple[int, int, str]] = []
    seen: set[tuple[int, int]] = set()
    for part in parts[1:]:
        title = source_tools.TITLE.search(part)
        season = source_tools.SEASON.search(part)
        number = source_tools.NUMBER.search(part)
        if not (title and season and number):
            raise ValueError(f"{mission}: incomplete publisher episode card")
        import html
        title_text = html.unescape(title.group(1)).strip()
        if not source_tools.VALID_TITLE.fullmatch(title_text):
            raise ValueError(f"{mission}: invalid episode title")
        key = int(season.group(1)), int(number.group(1))
        if key[0] != SEASON or key in seen or (result and key <= result[-1][:2]):
            raise ValueError(f"{mission}: incorrect season, duplicate or unsorted ordinal")
        result.append((key[0], key[1], title_text))
        seen.add(key)
    if len({title.casefold() for _, _, title in result}) != len(result):
        raise ValueError(f"{mission}: duplicate title cannot be automatically reconciled")
    return result


def csv_bytes(rows: list[tuple[int, int, str]]) -> bytes:
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["season", "episode_number", "title"])
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def parse_csv(raw: bytes) -> list[tuple[int, int, str]]:
    if not 30 <= len(raw) <= 16_384:
        raise ValueError("Season 7 publisher observation CSV exceeds bounded size")
    try:
        rows = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
        if rows.fieldnames != ["season", "episode_number", "title"]:
            raise ValueError("unexpected CSV columns")
        parsed = []
        for row in rows:
            if None in row or set(row) != set(rows.fieldnames):
                raise ValueError("invalid CSV row fields")
            if not row["season"].isdigit() or not row["episode_number"].isdigit():
                raise ValueError("non-numeric season or episode ordinal")
            title = row["title"]
            if title != title.strip() or not source_tools.VALID_TITLE.fullmatch(title):
                raise ValueError("invalid episode title metadata")
            parsed.append((int(row["season"]), int(row["episode_number"]), title))
    except csv.Error as exc:
        raise ValueError(f"malformed CSV: {exc}") from exc
    if (not 5 <= len(parsed) <= 35 or any(s != SEASON for s, _, _ in parsed)
            or parsed != sorted(parsed) or len({(s, n) for s, n, _ in parsed}) != len(parsed)
            or len({t.casefold() for _, _, t in parsed}) != len(parsed)):
        raise ValueError("invalid season, duplicate, or unsorted episode slots")
    if csv_bytes(parsed) != raw:
        raise ValueError("non-canonical CSV bytes")
    return parsed


def bundle(mission: str, rows: list[tuple[int, int, str]]) -> dict:
    url = official_url(mission)
    candidate = {
        "record_type": "publisher_episode_roster_proposal",
        "schema_version": "1.0.0",
        "batch_id": f"PARAMOUNT-S7-20261102-{mission.upper()}",
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
            "crosscheck_locator": f"https://www.paramountplus.com/shows/{SLUGS[mission]}/",
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None,
            "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": [
            {"season": s, "episode_number": n, "title": t, "status": "CANDIDATE",
             "canonical_work_id": None, "source_binding_id": None}
            for s, n, t in rows
        ],
    }
    roster.validate(candidate, roster.read_json(ROOT / "registry/mission_catalog.json"))
    return candidate


def source_index(pages: list[dict]) -> dict:
    return {"schema_version": "1.0.0", "proposal_type": "PUBLISHER_EPISODE_METADATA_SOURCE_OBSERVATIONS",
            "proposal_status": "DISCOVERY_ONLY", "observed_on": DATE, "publisher": "Paramount+",
            "independence_group": "publisher:paramount", "admission_effect": "NONE",
            "coverage_effect": "NONE", "denominator_effect": "NONE", "source_pages": pages}


def ingest(raw_dir: Path) -> int:
    output_root = ROOT / BASE
    dirguard.ensure_directory(ROOT, BASE)
    source_tools.ensure_no_symlink(output_root)
    source_tools.ensure_no_symlink(output_root / "index.json")
    pages = []
    for mission in SLUGS:
        source = raw_dir / f"{mission}-s7.html"
        raw = read_raw_response(source)
        rows = parse_cards(raw, mission)
        csv_data = csv_bytes(rows)
        dirguard.ensure_directory(ROOT, BASE / mission)
        for path in (output_root / f"{mission}.csv", output_root / mission / "bundle.json"):
            source_tools.ensure_no_symlink(path)
        safe_atomic_write(BASE / f"{mission}.csv", csv_data)
        safe_atomic_write(BASE / mission / "bundle.json", source_tools.serialized(bundle(mission, rows)))
        pages.append({"mission_id": mission, "official_page": official_url(mission),
                      "source_body_sha256": source_tools.sha(raw), "source_body_bytes": len(raw),
                      "observation_csv_sha256": source_tools.sha(csv_data), "listed_slot_count": len(rows)})
        print(f"{mission}: {len(rows)} source-local publisher listing cards; raw SHA256 {source_tools.sha(raw)}")
    safe_atomic_write(BASE / "index.json", source_tools.serialized(source_index(pages)))
    return check()


def check() -> int:
    output_root = ROOT / BASE
    index_path = output_root / "index.json"
    source_tools.ensure_no_symlink(index_path)
    index = roster.read_json(index_path)
    if (not isinstance(index, dict) or set(index) != INDEX_KEYS
            or {key: index[key] for key in INDEX_KEYS - {"source_pages"}}
            != {key: source_index([])[key] for key in INDEX_KEYS - {"source_pages"}}):
        raise ValueError("Season 7 metadata source index invalid")
    pages = index["source_pages"]
    if not isinstance(pages, list) or len(pages) != len(SLUGS):
        raise ValueError("missing or extra official publisher page receipts")
    count = 0
    for mission, receipt in zip(SLUGS, pages):
        if not isinstance(receipt, dict) or set(receipt) != PAGE_KEYS or receipt["mission_id"] != mission:
            raise ValueError("unexpected publisher page receipt identity")
        if receipt["official_page"] != official_url(mission):
            raise ValueError("publisher locator mismatch")
        if (not re.fullmatch(r"[a-f0-9]{64}", str(receipt["source_body_sha256"]))
                or type(receipt["source_body_bytes"]) is not int
                or not 10_000 <= receipt["source_body_bytes"] <= 3_000_000):
            raise ValueError("invalid raw-source SHA/size receipt")
        csv_file = output_root / f"{mission}.csv"
        bundle_file = output_root / mission / "bundle.json"
        for path in (csv_file, bundle_file):
            source_tools.ensure_no_symlink(path)
        raw = csv_file.read_bytes()
        if source_tools.sha(raw) != receipt["observation_csv_sha256"]:
            raise ValueError(f"{mission}: CSV hash mismatch")
        rows = parse_csv(raw)
        if receipt["listed_slot_count"] != len(rows):
            raise ValueError(f"{mission}: listed count mismatch")
        if bundle_file.read_bytes() != source_tools.serialized(bundle(mission, rows)):
            raise ValueError(f"{mission}: generated candidate bundle stale or modified")
        count += len(rows)
    print(f"PUBLISHER_S7_CHECKED: {count} source-local listing rows across {len(pages)} official guides")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest-dir", type=Path, help="private directory of <mission>-s7.html files")
    parser.add_argument("--check", action="store_true", help="verify committed candidate snapshots offline")
    args = parser.parse_args(argv)
    try:
        if args.check == bool(args.ingest_dir):
            raise ValueError("choose exactly --check or --ingest-dir")
        return check() if args.check else ingest(args.ingest_dir)
    except (OSError, ValueError, roster.Rejected) as exc:
        print(f"PUBLISHER_S7_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
