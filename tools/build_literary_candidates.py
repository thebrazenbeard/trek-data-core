#!/usr/bin/env python3
"""Compile a bounded Simon & Schuster edition *proposal*, without admission.

Only locally declared bibliographic locators are consumed. The script does not
fetch books, copy page content, establish rights, or reconcile canonical Works.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


PARTITION = Path("proposals/librarian/ring-of-fire-editions-20261102")
SOURCE = PARTITION / "bundle.json"
OUTPUT = PARTITION / "records.json"
GROUP = "publisher:simonandschuster.com"
PUBLISHER = "Simon & Schuster"
WORK_ID = "proposed-lit-snw-ring-of-fire"
TITLE = "Star Trek: Strange New Worlds: Ring of Fire"
SLUG = "/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/"
FORMATS = {"HARDCOVER", "TRADE_PAPERBACK", "EBOOK", "UNABRIDGED_AUDIO_DOWNLOAD"}
ALLOWED = {
    "schema_version", "proposal_only", "accepted_work_effect", "accepted_source_binding_effect",
    "coverage_effect", "source_group", "observed_on", "work", "editions",
}
WORK_KEYS = {"record_type", "work_id", "title", "creator", "medium", "work_type", "series", "status"}
EDITION_KEYS = {"isbn13", "format", "locator"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def reject_non_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON number: {value}")


def isbn13_valid(value: object) -> bool:
    if type(value) is not str or re.fullmatch(r"97[89][0-9]{10}", value) is None:
        return False
    weights = (1, 3) * 6
    check = (10 - sum(int(d) * weight for d, weight in zip(value[:12], weights)) % 10) % 10
    return check == int(value[-1])


def legal_locator(value: object, isbn: str) -> bool:
    if type(value) is not str:
        return False
    parts = urlsplit(value)
    return (parts.scheme == "https" and parts.netloc == "www.simonandschuster.com"
            and parts.path == SLUG + isbn and not parts.query and not parts.fragment
            and value == f"https://www.simonandschuster.com{SLUG}{isbn}")


def validate(data: object) -> dict:
    require(type(data) is dict and set(data) == ALLOWED, "unexpected proposal fields")
    require(data["schema_version"] == "1.0.0" and data["proposal_only"] is True,
            "the source must be a versioned proposal")
    require(all(data[k] == "NONE" for k in
                ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect")),
            "proposal may not modify accepted state or coverage")
    require(data["source_group"] == GROUP, "publisher lineage mismatch")
    when = data["observed_on"]
    require(type(when) is str and len(when) == 10, "invalid observation date")
    try:
        require(date.fromisoformat(when).isoformat() == when, "invalid ISO observation date")
    except ValueError as exc:
        raise ValueError("invalid ISO observation date") from exc
    work = data["work"]
    require(type(work) is dict and set(work) == WORK_KEYS, "unexpected Work fields")
    require(work == {
        "record_type": "work", "work_id": WORK_ID, "title": TITLE, "creator": "David Mack",
        "medium": "LITERATURE", "work_type": "NOVEL", "series": "Star Trek: Strange New Worlds",
        "status": "PROPOSED",
    }, "Work must remain precisely identified and proposed")
    editions = data["editions"]
    require(type(editions) is list and len(editions) == 4, "expected four bounded editions")
    seen_ids: set[str] = set()
    seen_formats: set[str] = set()
    prepared = []
    for edition in editions:
        require(type(edition) is dict and set(edition) == EDITION_KEYS,
                "unexpected edition or admission field")
        isbn = edition["isbn13"]
        kind = edition["format"]
        require(isbn13_valid(isbn) and isbn not in seen_ids, "invalid/duplicate ISBN13")
        require(type(kind) is str and kind in FORMATS and kind not in seen_formats,
                "unknown/duplicate product format")
        require(legal_locator(edition["locator"], isbn), "publisher URL is outside edition scope")
        seen_ids.add(isbn)
        seen_formats.add(kind)
        prepared.append({"isbn13": isbn, "format": kind, "locator": edition["locator"]})
    require(seen_formats == FORMATS, "the four expected formats are not represented")
    return {"work": work.copy(), "editions": sorted(prepared, key=lambda x: x["isbn13"]),
            "observed_on": when}


def read(root: Path) -> dict:
    source = root / SOURCE
    require(not root.is_symlink() and not source.is_symlink()
            and not any(parent.is_symlink() for parent in source.parents),
            "refusing symlink source path")
    require(source.is_file() and source.stat().st_size <= 32_000, "missing/oversized proposal")
    try:
        return json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                          parse_constant=reject_non_json_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed JSON source") from exc


def compile_records(proposal: object) -> dict:
    validated = validate(proposal)
    work = validated["work"]
    editions = validated["editions"]
    sources, bindings, candidates = [], [], []
    for row in editions:
        isbn = row["isbn13"]
        source_id = f"proposed-publisher-source-{isbn}"
        sources.append({
            "record_type": "source", "source_id": source_id, "status": "PROPOSED",
            "source_kind": "PUBLISHER_EDITION_METADATA", "provider": PUBLISHER,
            "locator": row["locator"], "source_version": None, "content_hash": None,
            "retrieved_at": None, "independence_group": GROUP,
            "provider_metadata": {"isbn13": isbn, "format": row["format"]},
        })
        bindings.append({
            "record_type": "source_work_binding", "binding_id": f"proposed-lit-binding-{isbn}",
            "source_id": source_id, "work_id": WORK_ID, "lifecycle": "PROPOSED",
            "mapping_role": "METADATA_ONLY",
            "source_scope": {"scope_type": "WHOLE", "locator": None},
            "work_scope": {"scope_type": "WHOLE", "component_label": None},
            "method": "PUBLISHER_EDITION_TITLE_AUTHOR_AND_ISBN_MATCH_UNVERIFIED",
            "basis": [{"kind": "PUBLISHER_PRODUCT_URL", "value": row["locator"]}],
            "exclusive_scope_key": None, "supersedes_binding_id": None, "fixture_only": False,
        })
        candidates.append({
            "edition_candidate_id": f"proposed-lit-edition-{isbn}", "isbn13": isbn,
            "format": row["format"], "work_id": WORK_ID, "source_id": source_id,
            "status": "PROPOSED", "verification": "PUBLISHER_METADATA_ONLY",
        })
    return {
        "schema_version": "1.0.0", "proposal_only": True,
        "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE", "observed_on": validated["observed_on"],
        "source_group": GROUP, "work": work, "edition_candidates": candidates,
        "sources": sources, "bindings": bindings,
    }


def build(root: Path) -> bytes:
    return (json.dumps(compile_records(read(root)), indent=2, sort_keys=True,
                       ensure_ascii=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="verify deterministic committed output")
    args = parser.parse_args(argv)
    try:
        blob = build(args.repo_root)
        target = args.repo_root / OUTPUT
        require(not args.repo_root.is_symlink() and not target.is_symlink()
                and not any(parent.is_symlink() for parent in target.parents),
                "refusing symlink output path")
        if args.check:
            require(target.is_file() and target.read_bytes() == blob, "stale literary proposal output")
        else:
            target.write_bytes(blob)
    except (OSError, ValueError) as exc:
        print(f"literary candidate compiler: {exc}", file=sys.stderr)
        return 1
    print("literary candidate compiler: checked" if args.check else "literary candidate compiler: generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
