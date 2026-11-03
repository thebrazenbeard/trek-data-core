#!/usr/bin/env python3
"""Search 14 explicitly pinned, unadmitted research observations on accepted main.

This is a local command, NOT an Explorer, Work, consensus, or coverage compiler.
It never scans proposed branches or accepts new packet families implicitly.
Every call checks source/validator byte pins and runs each original validator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKETS = (
    ("VOY_GUIDE_CARD", "proposals/research/voy-s4-e01-e05-guide-recheck-20261103/records.json",
     "5653fc0baa4bb816ce741b2a1817425b2978d5baea9c41a288f3eff578901163",
     "d244b0f2e320aa960d4274c4417e610f7b122b4748c33ad5c63478c49806661a"),
    ("TNG_EDITORIAL_OBSERVATION", "proposals/research/tng-lore-official-character-surface-20261103/records.json",
     "b639c2b5af578c804c86b610f9315670e089d9c3d14cdfee1b078f16f929a04c",
     "2fbb51aa0655f81059a2b54027565763dabd0763d8152dba59d1cd503d6b979c"),
    ("LITERARY_EDITION_CROSSCHECK", "proposals/librarian/tng-opf-0090-0092-publisher-editions-20261103/records.json",
     "ac67d958c0c75aee0fe3979bba8cd145972cfaca40aca920748ceec55b892964",
     "573f337084aef7bb586206c122188b25e0ea8ba51767bfa6fda89abf0350fb32"),
)
SCHEMA_VERSION = "1.0.0"
STATUS = "ACCEPTED_FILES_HELD_SOURCE_LOCAL_PROPOSALS_ONLY"
IDENTITY_SCOPE = "SOURCE_LOCAL_NOT_GLOBAL_WORK_OR_ENTITY"


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate source JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"Nonstandard source JSON constant: {value}")


def _pinned_bytes(root: Path, relative: str, expected: str) -> bytes:
    """Refuse path aliases, oversized inputs, and edits to reviewed bytes."""
    path = root
    for component in Path(relative).parts:
        path = path / component
        if path.is_symlink():
            raise ValueError(f"Source alias refused: {relative}")
    if not path.is_file() or not 0 < path.stat().st_size <= 100_000:
        raise ValueError(f"Missing or oversized source: {relative}")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f"Accepted source digest drift: {relative}")
    return raw


def _validated_packet(root: Path, kind: str, relative: str, sha: str, validator_sha: str) -> dict:
    raw = _pinned_bytes(root, relative, sha)
    validator = str(Path(relative).with_name("validate.py"))
    _pinned_bytes(root, validator, validator_sha)
    try:
        packet = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys,
                            parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid pinned packet encoding/JSON: {relative}") from exc
    if type(packet) is not dict:
        raise ValueError(f"Invalid pinned packet envelope: {relative}")
    try:
        check = subprocess.run([sys.executable, str(root / validator)], cwd=root,
                               capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Original {kind} validator could not run") from exc
    if check.returncode != 0:
        raise ValueError(f"Original {kind} validator rejected accepted-source inputs")
    return packet


def _row(*, row_id: str, local_id: str, kind: str, title: str, url: str,
         locator: str, family: str, state: str, note: str,
         source_path: str, sha: str, tags: list[str]) -> dict:
    return {
        "row_id": row_id, "source_local_id": local_id, "kind": kind,
        "title": title, "source_url": url, "source_locator": locator,
        "source_family": family, "source_status": state,
        "source_relative_note": note, "source_input": source_path,
        "source_input_sha256": sha, "tags": sorted(tags),
        "identity_scope": IDENTITY_SCOPE,
        "evidence_scope": "SOURCE_RELATIVE_METADATA_OR_EDITORIAL_OBSERVATION_NOT_CANONICAL_FACT",
        "source_lineage_independence": "NOT_ESTABLISHED",
        "full_work_read": False, "coverage_effect": "NONE",
        "work_admission_effect": "NONE", "public_release_effect": "NONE",
    }


def build(root: Path = ROOT) -> dict:
    """Read just three explicit accepted-file packets; do not admit their proposals."""
    rows, receipts = [], []
    for kind, relative, sha, validator_sha in PACKETS:
        data = _validated_packet(root, kind, relative, sha, validator_sha)
        receipts.append({"kind": kind, "source_input": relative, "sha256": sha,
                         "validator_sha256": validator_sha})
        if kind == "VOY_GUIDE_CARD":
            src = data["source"]
            evidence = {ev["id"]: ev for ev in data["evidence"]}
            for item in data["local_entities"]:
                ev = evidence[item["evidence_id"]]
                rows.append(_row(
                    row_id=f"voy-guide:{item['id']}", local_id=item["id"], kind=kind,
                    title=item["display_title"], url=src["url"], locator=ev["locator"],
                    family=src["lineage_group"], state=data["state"],
                    note=ev["establishes"], source_path=relative, sha=sha,
                    tags=["series:voy", "season:4", f"slot:s4e{item['display_ordinal']:02d}",
                          "source-kind:publisher-guide"]),
                )
        elif kind == "TNG_EDITORIAL_OBSERVATION":
            sources = {src["id"]: src for src in data["sources"]}
            for item in data["evidence"]:
                source = sources[item["source_id"]]
                rows.append(_row(
                    row_id=f"lore-evidence:{item['id']}", local_id=item["id"], kind=kind,
                    title=f"Lore publisher editorial observation {item['id']}",
                    url=source["url"], locator=item["locator"],
                    family=source["publisher_lineage"], state=data["status"],
                    note=item["observation"], source_path=relative, sha=sha,
                    tags=["subject:lore", "source-kind:publisher-editorial",
                          "evidence-kind:" + item["kind"].lower()]),
                )
        else:
            for item in data["records"]:
                rows.append(_row(
                    row_id=f"opf-crosscheck:{item['opf_source_local_id']}",
                    local_id=item["opf_source_local_id"], kind=kind,
                    title=item["publisher_title"], url=item["publisher_locator"],
                    locator=item["opf_source_local_id"],
                    family=data["publisher_source_family"], state=item["crosscheck_state"],
                    note=item["uncertainty"], source_path=relative, sha=sha,
                    tags=["medium:literature", "format:ebook", "source-kind:publisher-edition",
                          "opf-isbn13:" + item["isbn13_candidate"],
                          "publisher-isbn13:" + item["publisher_isbn13"]]),
                )
    rows.sort(key=lambda row: row["row_id"])
    if len(rows) != len({row["row_id"] for row in rows}) or len(rows) != 14 or \
       Counter(row["kind"] for row in rows) != {
           "VOY_GUIDE_CARD": 5, "TNG_EDITORIAL_OBSERVATION": 6,
           "LITERARY_EDITION_CROSSCHECK": 3,
       }:
        raise ValueError("Held packet query cardinality/identity drift")
    return {
        "schema_version": SCHEMA_VERSION, "data_status": STATUS,
        "identity_scope": IDENTITY_SCOPE, "source_file_count": len(receipts),
        "source_lineage_independence": "NOT_ESTABLISHED",
        "source_input_receipts": receipts, "row_count": len(rows),
        "full_work_reads": 0, "work_admissions": 0, "coverage_effect": "NONE",
        "public_explorer_effect": "NONE", "public_release_effect": "NONE",
        "rows": rows,
    }


def query(report: dict, *, text: str = "", row_id: str = "", kind: str = "",
          status: str = "", source_family: str = "", tag: str = "",
          limit: int = 20, offset: int = 0) -> dict:
    """AND-match casefolded terms, then page exact source-local rows only."""
    for name, value in (("query", text), ("row ID", row_id), ("kind", kind),
                        ("status", status), ("source family", source_family), ("tag", tag)):
        if type(value) is not str or len(value) > 160:
            raise ValueError(f"Invalid bounded {name}")
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or \
       not 0 <= offset <= 1_000_000:
        raise ValueError("Invalid query window")
    terms = text.casefold().split()
    matched = []
    for row in report["rows"]:
        if row_id and row["row_id"] != row_id:
            continue
        if kind and row["kind"] != kind:
            continue
        if status and row["source_status"] != status:
            continue
        if source_family and row["source_family"] != source_family:
            continue
        if tag and tag not in row["tags"]:
            continue
        search = " ".join((row["title"], row["source_relative_note"], row["source_local_id"],
                           row["source_locator"], *row["tags"])).casefold()
        if all(term in search for term in terms):
            matched.append(row)
    page = matched[offset:offset + limit]
    return {
        "schema_version": SCHEMA_VERSION, "data_status": STATUS,
        "identity_scope": IDENTITY_SCOPE, "source_lineage_independence": "NOT_ESTABLISHED",
        "total_matches": len(matched), "offset": offset, "limit": limit,
        "next_offset": offset + len(page) if offset + len(page) < len(matched) else None,
        "facet_counts": {
            column: dict(sorted(Counter(row[column] for row in matched).items()))
            for column in ("kind", "source_status", "source_family")
        },
        "rows": page, "work_admission_effect": "NONE", "coverage_effect": "NONE",
        "public_release_effect": "NONE", "public_explorer_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q", default="", help="AND-match source-relative metadata and editorial notes")
    parser.add_argument("--id", dest="row_id", default="", help="Exact namespaced source-local row ID")
    parser.add_argument("--kind", default="", help="Exact scoped packet observation kind")
    parser.add_argument("--status", default="", help="Exact HELD or unresolved source status")
    parser.add_argument("--source-family", default="", help="Exact source family label (not corroboration)")
    parser.add_argument("--tag", default="", help="Exact source-local structural tag")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    try:
        result = query(build(), text=args.q, row_id=args.row_id, kind=args.kind,
                       status=args.status, source_family=args.source_family,
                       tag=args.tag, limit=args.limit, offset=args.offset)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
