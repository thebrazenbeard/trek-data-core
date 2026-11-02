#!/usr/bin/env python3
"""Extract bounded, source-local Prodigy episode title observations from publisher HTML.

Full publisher HTML stays outside Git. The source-body receipt is a local
integrity aid, not an independently authenticated or signed publisher record.
Nothing here admits a work, briefing, binding, coverage or denominator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_legacy_s2_discovery import ensure_no_symlink, safe_atomic_write
from tools import validate_publisher_episode_roster as roster

BASE = Path("proposals/discovery/prodigy-startrek-publisher-20261102")
DATE = "2026-11-02"
SOURCES = (
    ("s1b", "https://www.startrek.com/news/star-trek-prodigy-season-1-episodes-11-20-release", 1, 11, 20),
    ("s2", "https://www.startrek.com/news/star-trek-prodigy-season-2-now-available", 2, 1, 20),
)
S1_HEADING = re.compile(r"<h4\b[^>]*>\s*<strong>\s*<em>Star Trek: Prodigy</em>:\s*Season 1, Episodes 11-20</strong>:\s*</h4>", re.I)
ITEM = re.compile(r"<li\b[^>]*\bclass=\"[^\"]*listItem\"[^>]*>(.*?)</li>", re.S | re.I)
S2_TITLE = re.compile(r"<strong>\s*(2\d{2})\s*–\s*&quot;(.*?)&quot;\s*</strong>", re.S)
VALID_TITLE = re.compile(r"[^<>\x00-\x1f\x7f]{2,160}\Z")
INDEX_KEYS = {"schema_version", "proposal_type", "proposal_status", "observed_on", "publisher", "independence_group", "admission_effect", "coverage_effect", "denominator_effect", "source_pages", "acknowledged_gaps"}
RECEIPT_KEYS = {"source_id", "season", "observed_episode_range", "official_page", "source_body_sha256", "source_body_bytes", "observation_csv_sha256", "listed_slot_count"}


def serialize(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_for(source_id: str) -> tuple:
    return next((item for item in SOURCES if item[0] == source_id), None)


def normalize_title(fragment: str) -> str:
    # The official S2 list italicizes only the ship name inside two titles.
    plain = re.sub(r"</?em>", "", fragment)
    value = html.unescape(plain).strip()
    if not VALID_TITLE.fullmatch(value):
        raise ValueError(f"unsupported publisher title markup or invalid title: {fragment[:90]}")
    return value


def extract_source(raw: bytes, source_id: str) -> list[tuple[int, int, str]]:
    if not 100_000 <= len(raw) <= 3_000_000:
        raise ValueError("publisher HTML outside constrained source-body size")
    spec = source_for(source_id)
    if spec is None:
        raise ValueError("unknown Prodigy publisher source")
    _, url, season, first, last = spec
    text = raw.decode("utf-8")
    if f'<link rel="canonical" href="{url}"' not in text:
        raise ValueError("publisher HTML does not match expected canonical locator")
    if source_id == "s1b":
        heading = S1_HEADING.search(text)
        if not heading:
            raise ValueError("Season 1 Episodes 11–20 publisher heading not found")
        following = text[heading.end():]
        start = re.search(r"<ul\b[^>]*>", following)
        if not start:
            raise ValueError("publisher episode title list not found")
        end = following.find("</ul>", start.end())
        if end < 0 or end - start.end() > 10_000:
            raise ValueError("publisher title-list boundary missing or oversized")
        entries = ITEM.findall(following[start.end():end])
        rows = [(season, ordinal, normalize_title(entry)) for ordinal, entry in enumerate(entries, first)]
    else:
        # Source uses 201–220, which is publisher numbering for S2 E01–E20.
        tokens = S2_TITLE.findall(text)
        rows = [(season, int(number) - 200, normalize_title(entry)) for number, entry in tokens]
    expected = list(range(first, last + 1))
    if [n for _, n, _ in rows] != expected:
        raise ValueError(f"source {source_id}: expected season-local slots {first}–{last} exactly")
    if len({title.casefold() for _, _, title in rows}) != len(rows):
        raise ValueError("duplicate titles in one publisher source list")
    return rows


def csv_bytes(rows: list[tuple[int, int, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["season", "episode_number", "title"])
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def read_csv(data: bytes, source_id: str) -> list[tuple[int, int, str]]:
    if len(data) > 16_384:
        raise ValueError("oversized Prodigy observation CSV")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""))
    if reader.fieldnames != ["season", "episode_number", "title"]:
        raise ValueError("invalid Prodigy CSV header")
    rows = []
    for row in reader:
        if None in row or set(row) != set(reader.fieldnames):
            raise ValueError("invalid Prodigy CSV record")
        if not row["season"].isdigit() or not row["episode_number"].isdigit():
            raise ValueError("invalid Prodigy season or ordinal")
        title = row["title"]
        if title != normalize_title(title):
            raise ValueError("unnormalized Prodigy title")
        rows.append((int(row["season"]), int(row["episode_number"]), title))
    spec = source_for(source_id)
    if spec is None or [(s, n) for s, n, _ in rows] != [(spec[2], n) for n in range(spec[3], spec[4] + 1)]:
        raise ValueError("unexpected Prodigy source-local slots")
    if len({title.casefold() for _, _, title in rows}) != len(rows) or csv_bytes(rows) != data:
        raise ValueError("duplicate title or non-deterministic Prodigy CSV")
    return rows


def candidate_bundle(source_id: str, rows: list[tuple[int, int, str]]) -> dict:
    source = source_for(source_id)
    result = {
        "record_type": "publisher_episode_roster_proposal", "schema_version": "1.0.0",
        "batch_id": f"STARTREK-PRODIGY-{source_id.upper()}-20261102", "mission_id": "pro",
        "proposal_status": "CANDIDATE_METADATA_ONLY", "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE", "coverage_effect": "NONE",
        "denominator_effect": "NONE", "roster_completeness": "UNRESOLVED",
        "listed_slot_count": len(rows),
        "observation": {
            "publisher": "StarTrek.com", "independence_group": "publisher:paramount",
            "observed_on": DATE, "primary_locator": source[1],
            "crosscheck_locator": "https://www.startrek.com/series/star-trek-prodigy",
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None, "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": [
            {"season": s, "episode_number": n, "title": title, "status": "CANDIDATE",
             "canonical_work_id": None, "source_binding_id": None}
            for s, n, title in rows
        ],
    }
    roster.validate(result, roster.read_json(ROOT / "registry/mission_catalog.json"))
    return result


def index(receipts: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0", "proposal_type": "PUBLISHER_EPISODE_METADATA_SOURCE_OBSERVATIONS",
        "proposal_status": "DISCOVERY_ONLY", "observed_on": DATE, "publisher": "StarTrek.com",
        "independence_group": "publisher:paramount", "admission_effect": "NONE",
        "coverage_effect": "NONE", "denominator_effect": "NONE",
        "source_pages": receipts,
        "acknowledged_gaps": ["Season 1 episodes 1–10 lack a numbered, complete publisher title listing in this batch; no absence or completeness claim is made."],
    }


def ingest(raw_dir: Path) -> int:
    output = ROOT / BASE
    output.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink(output)
    receipts = []
    for source_id, url, season, first, last in SOURCES:
        path = raw_dir / f"{source_id}.html"
        ensure_no_symlink(path)
        raw = path.read_bytes()
        rows = extract_source(raw, source_id)
        data = csv_bytes(rows)
        (output / source_id).mkdir(parents=True, exist_ok=True)
        safe_atomic_write(BASE / f"{source_id}.csv", data)
        safe_atomic_write(BASE / source_id / "bundle.json", serialize(candidate_bundle(source_id, rows)))
        receipts.append({
            "source_id": source_id, "season": season,
            "observed_episode_range": [first, last], "official_page": url,
            "source_body_sha256": sha(raw), "source_body_bytes": len(raw),
            "observation_csv_sha256": sha(data), "listed_slot_count": len(rows),
        })
        print(f"PRODIGY_OBSERVED {source_id}: {len(rows)} titles; HTML SHA-256 {sha(raw)}")
    safe_atomic_write(BASE / "index.json", serialize(index(receipts)))
    return check()


def check() -> int:
    output = ROOT / BASE
    ensure_no_symlink(output / "index.json")
    source_index = roster.read_json(output / "index.json")
    template = index([])
    if (not isinstance(source_index, dict) or set(source_index) != INDEX_KEYS or
            {key: source_index[key] for key in INDEX_KEYS - {"source_pages"}} !=
            {key: template[key] for key in INDEX_KEYS - {"source_pages"}}):
        raise ValueError("publisher observation index is inconsistent")
    receipts = source_index["source_pages"]
    if not isinstance(receipts, list) or len(receipts) != len(SOURCES):
        raise ValueError("publisher source receipt count mismatch")
    total = 0
    for spec, receipt in zip(SOURCES, receipts):
        source_id, url, season, first, last = spec
        if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
            raise ValueError("publisher receipt fields invalid")
        if (receipt["source_id"], receipt["official_page"], receipt["season"],
                receipt["observed_episode_range"]) != (source_id, url, season, [first, last]):
            raise ValueError("publisher source receipt identity invalid")
        if (not re.fullmatch(r"[a-f0-9]{64}", str(receipt["source_body_sha256"])) or
                type(receipt["source_body_bytes"]) is not int or
                not 100_000 <= receipt["source_body_bytes"] <= 3_000_000):
            raise ValueError("source-body receipt invalid")
        csv_file, bundle_file = output / f"{source_id}.csv", output / source_id / "bundle.json"
        ensure_no_symlink(csv_file)
        ensure_no_symlink(bundle_file)
        data = csv_file.read_bytes()
        if sha(data) != receipt["observation_csv_sha256"]:
            raise ValueError("Provenance CSV checksum mismatch")
        rows = read_csv(data, source_id)
        if receipt["listed_slot_count"] != len(rows):
            raise ValueError("source receipt count mismatch")
        if bundle_file.read_bytes() != serialize(candidate_bundle(source_id, rows)):
            raise ValueError("publisher bundle is stale or modified")
        total += len(rows)
    print(f"PRODIGY_SOURCE_CHECKED: {total} publisher-listed source-local candidate rows")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ingest-dir", type=Path)
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        return check() if args.check else ingest(args.ingest_dir)
    except (ValueError, OSError, roster.Rejected) as exc:
        print(f"PRODIGY_SOURCE_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
