#!/usr/bin/env python3
"""Offline callable search over the accepted source-only publisher-card sidecar.

Always recompiles and byte-checks the sidecar against accepted source inputs
before returning results; --row-id remains source-local, not a Work identity.
"""

from __future__ import annotations

import argparse
import json

from build_accepted_source_card_rechecks import OUTPUT, ROOT, build, encode


def query(rows: list[dict], *, row_id: str | None = None, series: str | None = None,
          title: str | None = None, batch: str | None = None,
          title_check: str | None = None, limit: int = 61) -> list[dict]:
    if not 1 <= limit <= 61:
        raise ValueError("limit must be 1..61")
    matches = []
    for row in rows:
        if row_id and row["row_id"] != row_id:
            continue
        if series and row["source_local_context"] != series:
            continue
        if title and title.casefold() not in (
            row["source_local_title"] + " " + row["publisher_card_title"]
        ).casefold():
            continue
        if batch and row["source_batch"] != batch:
            continue
        if title_check and row["publisher_title_check"] != title_check:
            continue
        matches.append(row)
    return matches[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--row-id", help="Exact source-local discovery row ID, e.g. lead:0106")
    parser.add_argument("--series", choices=["DS9", "VOY", "ENT", "DIS"])
    parser.add_argument("--title", help="Case-insensitive substring on directory/card titles")
    parser.add_argument("--batch", choices=["B005-DS9", "B006-VOY", "B007-VOY",
                                            "B008-ENT", "B009-ENT", "DIS-S3-SEVEN"])
    parser.add_argument("--title-check", help="Exact publisher_title_check label")
    parser.add_argument("--limit", type=int, default=61)
    args = parser.parse_args()
    projection = build()
    target = ROOT / OUTPUT
    if target.is_symlink() or not target.is_file() or target.read_bytes() != encode(projection):
        raise SystemExit("SOURCE_CARD_QUERY_REFUSED_STALE_OR_TAMPERED_SIDECAR")
    selected = query(projection["rows"], row_id=args.row_id, series=args.series,
                     title=args.title, batch=args.batch, title_check=args.title_check,
                     limit=args.limit)
    print(json.dumps({"source_local_only": True, "coverage_effect": "NONE",
                      "match_count": len(selected), "rows": selected}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
