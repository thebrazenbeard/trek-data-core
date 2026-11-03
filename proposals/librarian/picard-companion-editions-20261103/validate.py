#!/usr/bin/env python3
"""Deterministically compile and validate metadata-only publisher candidates."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


PARTITION = Path(__file__).resolve().parent
REPO = PARTITION.parents[2]
SOURCE = PARTITION / "bundle.json"
OUTPUT = PARTITION / "records.json"
GROUP = "publisher:simonandschuster.com"
WORK_FIELDS = {
    "work_id", "title", "creator", "publisher_series_position", "isbn13", "format",
    "publication_date", "length_pages", "locator",
}
ROOT_FIELDS = {
    "schema_version", "proposal_only", "accepted_work_effect", "accepted_source_binding_effect",
    "coverage_effect", "observed_on", "source_group", "works",
}


def require(ok: bool, description: str) -> None:
    if not ok:
        raise ValueError(description)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON field")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def read_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 40_000,
            "missing/unsafe/oversized proposal JSON")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=reject_constant)


def isbn13_valid(value: object) -> bool:
    if not isinstance(value, str) or re.fullmatch(r"97[89][0-9]{10}", value) is None:
        return False
    check = (10 - sum(int(d) * (1 if i % 2 == 0 else 3)
                      for i, d in enumerate(value[:12])) % 10) % 10
    return check == int(value[-1])


def normalized_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")


def validate_bundle(data: dict) -> list[dict]:
    require(type(data) is dict and set(data) == ROOT_FIELDS, "unexpected bundle fields")
    require(data["schema_version"] == "1.0.0" and data["proposal_only"] is True,
            "versioned proposal required")
    require(all(data[k] == "NONE" for k in
                ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect")),
            "no accepted state or coverage effect allowed")
    require(data["source_group"] == GROUP, "unexpected provenance group")
    require(data["observed_on"] == "2026-11-03", "observation date must be explicit")
    rows = data["works"]
    require(type(rows) is list and len(rows) == 3, "expected exactly three publisher editions")
    seen_ids, seen_isbns, seen_series = set(), set(), set()
    for row in rows:
        require(type(row) is dict and set(row) == WORK_FIELDS, "unexpected Work/edition field")
        wid, isbn = row["work_id"], row["isbn13"]
        require(type(wid) is str and re.fullmatch(r"proposed-lit-picard-[a-z0-9-]+", wid)
                and wid not in seen_ids, "invalid/duplicate proposed Work ID")
        require(isbn13_valid(isbn) and isbn not in seen_isbns, "invalid/duplicate ISBN")
        require(type(row["title"]) is str and row["title"].startswith("Star Trek: Picard: ")
                and 20 <= len(row["title"]) < 100, "invalid publisher Work title")
        require(type(row["creator"]) is str and re.fullmatch(r"[A-Za-z ]+", row["creator"])
                and 4 <= len(row["creator"]) <= 70, "invalid creator")
        require(row["format"] == "TRADE_PAPERBACK", "wrong edition format")
        require(type(row["length_pages"]) is int and 100 <= row["length_pages"] <= 1500,
                "unexpected page count")
        try:
            require(date.fromisoformat(row["publication_date"]).isoformat()
                    == row["publication_date"], "invalid publication date")
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid publication date") from exc
        position = row["publisher_series_position"]
        require(position in {"Book #2 of Star Trek: Picard", "Book #3 of Star Trek: Picard",
                             "Part of Star Trek: Picard"} and position not in seen_series,
                "unexpected/duplicate publisher series designation")
        tail = row["title"].removeprefix("Star Trek: Picard: ")
        slug = f"/books/Star-Trek-Picard-{normalized_slug(tail)}/"
        slug += f"{normalized_slug(row['creator'])}/Star-Trek-Picard/{isbn}"
        url = row["locator"]
        require(type(url) is str and url == f"https://www.simonandschuster.com{slug}",
                "publisher locator not exact ISBN/title/author product URL")
        parsed = urlsplit(url)
        require(parsed.scheme == "https" and parsed.hostname == "www.simonandschuster.com"
                and not parsed.query and not parsed.fragment, "unsafe product locator")
        seen_ids.add(wid)
        seen_isbns.add(isbn)
        seen_series.add(position)
    return sorted(rows, key=lambda row: row["isbn13"])


def compile_records(data: dict) -> dict:
    rows = validate_bundle(data)
    sources, works, bindings, editions = [], [], [], []
    for row in rows:
        isbn, wid = row["isbn13"], row["work_id"]
        sid = f"proposed-picard-publisher-source-{isbn}"
        sources.append({
            "record_type": "source", "source_id": sid, "status": "PROPOSED",
            "source_kind": "PUBLISHER_EDITION_METADATA", "provider": "Simon & Schuster",
            "locator": row["locator"], "source_version": None, "retrieved_at": None,
            "content_hash": None, "content_fingerprint": None,
            "source_variant": "publisher trade paperback product page",
            "provenance_family": "SIMON_SCHUSTER_PICARD_PRODUCT_PAGES",
            "independence_group": GROUP, "derived_from": [], "fixture_only": False,
            "provider_metadata": {
                "title": row["title"], "creator": row["creator"],
                "isbn13": isbn, "format": row["format"],
                "publication_date": row["publication_date"],
                "length_pages": row["length_pages"],
                "publisher_series_position": row["publisher_series_position"],
            },
            "notes": "Publisher product metadata only; no exact page-byte receipt or book-text read.",
        })
        works.append({
            "record_type": "work", "work_id": wid, "status": "PROPOSED",
            "title": row["title"], "work_type": "NOVEL", "parent_work_id": None,
            "component_label": None, "fixture_only": False,
            "notes": f"Publisher-attributed Work hypothesis; creator {row['creator']}; not reconciled.",
        })
        bindings.append({
            "record_type": "source_work_binding", "binding_id": f"proposed-picard-binding-{isbn}",
            "source_id": sid, "work_id": wid, "lifecycle": "PROPOSED",
            "mapping_role": "METADATA_ONLY", "source_scope": {"scope_type": "WHOLE", "locator": None},
            "work_scope": {"scope_type": "WHOLE", "component_label": None},
            "method": "PUBLISHER_PRODUCT_TITLE_AUTHOR_ISBN_MATCH_UNVERIFIED",
            "basis": [{"kind": "PUBLISHER_PRODUCT_URL", "value": row["locator"]}],
            "exclusive_scope_key": None, "supersedes_binding_id": None,
            "notes": "Not a reading or an evidence-bearing Source-to-Work binding.",
            "fixture_only": False,
        })
        editions.append({
            "edition_candidate_id": f"proposed-picard-edition-{isbn}", "source_id": sid,
            "work_id": wid, "isbn13": isbn, "format": row["format"],
            "publisher_series_position": row["publisher_series_position"],
            "status": "PROPOSED", "verification": "PUBLISHER_METADATA_ONLY",
        })
    result = {
        "schema_version": "1.0.0", "proposal_only": True,
        "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE", "source_group": GROUP,
        "observed_on": data["observed_on"],
        "works": works, "sources": sources, "bindings": bindings,
        "crosswalks": [], "edition_candidates": editions,
    }
    sys.path.insert(0, str(REPO / "tools"))
    from validate_librarian_registry import validate_registry  # noqa: E402
    errors = validate_registry(sources, works, bindings, [])
    require(not errors, "registry schema errors: " + " | ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        data = read_json(SOURCE)
        output = (json.dumps(compile_records(data), indent=2, sort_keys=True) + "\n").encode()
        require(not OUTPUT.is_symlink(), "unsafe output symlink")
        if args.check:
            require(OUTPUT.is_file() and OUTPUT.read_bytes() == output,
                    "committed candidate output does not match deterministic compiler")
        else:
            OUTPUT.write_bytes(output)
    except (OSError, ValueError) as exc:
        print(f"Picard publisher candidate validator: {exc}", file=sys.stderr)
        return 1
    print("Picard publisher candidate validator: PASS (3 Work/edition proposals; zero admission)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
