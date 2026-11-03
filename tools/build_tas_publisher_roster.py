#!/usr/bin/env python3
"""Source-local TAS publisher guide observations, never admitted episode research.

Raw Paramount+ HTML is read only from a private directory and is not committed.
Receipts and exact normalized publisher titles/ordinals are public metadata.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import build_publisher_s6_discovery as safe
from tools import build_legacy_s3_discovery as source
from tools import publisher_output_directory as output_directory
from tools import validate_publisher_episode_roster as roster

BASE = Path("proposals/discovery/tas-publisher-seasons-20261102")
DATE = "2026-11-02"
MISSION = "tas"
SEASONS = (1, 2)


def official_url(season: int) -> str:
    if season not in SEASONS:
        raise ValueError("unsupported TAS publisher season")
    return f"https://www.paramountplus.com/shows/star_trek_animated/episodes/{season}/"


def parse_cards(raw: bytes, season: int) -> list[tuple[int, int, str]]:
    """Reject ambiguous publisher identity or malformed/duplicated episode cards."""
    if season not in SEASONS or not 10_000 <= len(raw) <= 3_000_000:
        raise ValueError("invalid TAS season or source size")
    page = raw.decode("utf-8", errors="strict")
    links = safe._CanonicalLinks()
    links.feed(page)
    links.close()
    if len(links.candidates) != 1:
        raise ValueError("missing or duplicate canonical publisher locator")
    attrs = links.candidates[0]
    rels = [v for k, v in attrs if k == "rel"]
    hrefs = [v for k, v in attrs if k == "href"]
    if (len(rels) != 1 or len(hrefs) != 1 or
            rels[0] is None or rels[0].lower().split() != ["canonical"] or
            hrefs[0] != official_url(season)):
        raise ValueError("forged or ambiguous canonical publisher locator")
    parts = source.CARD.split(page)
    if not 6 <= len(parts) <= 41:
        raise ValueError("unexpected TAS publisher card count")
    output: list[tuple[int, int, str]] = []
    for part in parts[1:]:
        title, number, s = source.TITLE.search(part), source.NUMBER.search(part), source.SEASON.search(part)
        if not (title and number and s):
            raise ValueError("incomplete TAS publisher episode card")
        normalized = html.unescape(title.group(1)).strip()
        if not source.VALID_TITLE.fullmatch(normalized):
            raise ValueError("invalid TAS publisher title")
        row = (int(s.group(1)), int(number.group(1)), normalized)
        if row[0] != season or (output and row[:2] <= output[-1][:2]):
            raise ValueError("wrong season, repeated or unsorted episode ordinal")
        output.append(row)
    if len({title.casefold() for _, _, title in output}) != len(output):
        raise ValueError("duplicate TAS publisher title")
    return output


def csv_bytes(rows: list[tuple[int, int, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["season", "episode_number", "title"])
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def parse_csv(raw: bytes, season: int) -> list[tuple[int, int, str]]:
    if not 30 <= len(raw) <= 16_384:
        raise ValueError("unbounded TAS publisher CSV")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
        if reader.fieldnames != ["season", "episode_number", "title"]:
            raise ValueError("wrong TAS publisher CSV columns")
        rows: list[tuple[int, int, str]] = []
        for item in reader:
            if None in item or set(item) != set(reader.fieldnames):
                raise ValueError("ambiguous TAS publisher CSV row")
            if not item["season"].isdigit() or not item["episode_number"].isdigit():
                raise ValueError("non-numeric TAS episode ordinal")
            title = item["title"]
            if title != title.strip() or not source.VALID_TITLE.fullmatch(title):
                raise ValueError("invalid TAS publisher title")
            rows.append((int(item["season"]), int(item["episode_number"]), title))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("invalid TAS publisher CSV encoding") from exc
    if (not 5 <= len(rows) <= 35 or any(s != season for s, _, _ in rows)
            or rows != sorted(rows) or len({(s, n) for s, n, _ in rows}) != len(rows)
            or len({t.casefold() for _, _, t in rows}) != len(rows)
            or csv_bytes(rows) != raw):
        raise ValueError("noncanonical, duplicate or invalid TAS publisher CSV")
    return rows


def bundle(season: int, rows: list[tuple[int, int, str]]) -> dict:
    locator = official_url(season)
    value = {
        "record_type": "publisher_episode_roster_proposal",
        "schema_version": "1.0.0",
        "batch_id": f"PARAMOUNT-TAS-S{season}-20261102",
        "mission_id": MISSION,
        "proposal_status": "CANDIDATE_METADATA_ONLY",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "roster_completeness": "UNRESOLVED",
        "listed_slot_count": len(rows),
        "observation": {
            "publisher": "Paramount+", "independence_group": "publisher:paramount",
            "observed_on": DATE, "primary_locator": locator,
            "crosscheck_locator": "https://www.startrek.com/series/star-trek-the-animated-series",
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None, "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": [
            {"season": s, "episode_number": n, "title": t, "status": "CANDIDATE",
             "canonical_work_id": None, "source_binding_id": None}
            for s, n, t in rows
        ],
    }
    roster.validate(value, roster.read_json(ROOT / "registry/mission_catalog.json"))
    return value


def source_index(pages: list[dict]) -> dict:
    return {"schema_version": "1.0.0",
            "proposal_type": "PUBLISHER_EPISODE_METADATA_SOURCE_OBSERVATIONS",
            "proposal_status": "DISCOVERY_ONLY", "observed_on": DATE,
            "publisher": "Paramount+", "independence_group": "publisher:paramount",
            "admission_effect": "NONE", "coverage_effect": "NONE",
            "denominator_effect": "NONE", "source_pages": pages}


def ingest(private_dir: Path) -> int:
    target = ROOT / BASE
    output_directory.ensure_directory(ROOT, BASE)
    source.ensure_no_symlink(target)
    source.ensure_no_symlink(target / "index.json")
    pages: list[dict] = []
    for season in SEASONS:
        raw = safe.read_raw_response(private_dir / f"s{season}.html")
        rows = parse_cards(raw, season)
        csv_data = csv_bytes(rows)
        output_directory.ensure_directory(ROOT, BASE / f"s{season}")
        safe.safe_atomic_write(BASE / f"s{season}.csv", csv_data)
        safe.safe_atomic_write(BASE / f"s{season}" / "bundle.json", source.serialized(bundle(season, rows)))
        pages.append({"mission_id": MISSION, "official_page": official_url(season),
                      "source_body_sha256": source.sha(raw), "source_body_bytes": len(raw),
                      "observation_csv_sha256": source.sha(csv_data),
                      "listed_slot_count": len(rows)})
        print(f"TAS S{season}: {len(rows)} source-local publisher observations; raw SHA256 {source.sha(raw)}")
    safe.safe_atomic_write(BASE / "index.json", source.serialized(source_index(pages)))
    return check()


def check() -> int:
    target = ROOT / BASE
    source.ensure_no_symlink(target / "index.json")
    index = roster.read_json(target / "index.json")
    if (not isinstance(index, dict) or set(index) != safe.INDEX_KEYS
            or {k: index[k] for k in safe.INDEX_KEYS - {"source_pages"}}
            != {k: source_index([])[k] for k in safe.INDEX_KEYS - {"source_pages"}}):
        raise ValueError("invalid TAS source index")
    if not isinstance(index["source_pages"], list) or len(index["source_pages"]) != 2:
        raise ValueError("missing TAS publisher season receipts")
    total = 0
    for season, receipt in zip(SEASONS, index["source_pages"]):
        if (not isinstance(receipt, dict) or set(receipt) != safe.PAGE_KEYS
                or receipt["mission_id"] != MISSION or receipt["official_page"] != official_url(season)
                or not re.fullmatch(r"[0-9a-f]{64}", str(receipt["source_body_sha256"]))
                or type(receipt["source_body_bytes"]) is not int
                or not 10_000 <= receipt["source_body_bytes"] <= 3_000_000):
            raise ValueError("invalid TAS publisher source receipt")
        path = target / f"s{season}.csv"
        bp = target / f"s{season}" / "bundle.json"
        for candidate in (path, bp):
            source.ensure_no_symlink(candidate)
        csv_data = path.read_bytes()
        if source.sha(csv_data) != receipt["observation_csv_sha256"]:
            raise ValueError("TAS publisher CSV changed after source capture")
        rows = parse_csv(csv_data, season)
        if len(rows) != receipt["listed_slot_count"]:
            raise ValueError("TAS publisher count receipt mismatch")
        if bp.read_bytes() != source.serialized(bundle(season, rows)):
            raise ValueError("TAS source-local bundle changed after generation")
        total += len(rows)
    print(f"TAS_PUBLISHER_CHECKED: {total} source-local rows across both official guides")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest-dir", type=Path, help="private s1.html and s2.html captures")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check == bool(args.ingest_dir):
            raise ValueError("choose exactly --check or --ingest-dir")
        return check() if args.check else ingest(args.ingest_dir)
    except (OSError, ValueError, roster.Rejected) as exc:
        print(f"TAS_PUBLISHER_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
