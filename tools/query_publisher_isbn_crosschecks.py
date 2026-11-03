#!/usr/bin/env python3
"""Offline callable search over accepted source-only publisher ISBN crosschecks."""

from __future__ import annotations

import argparse
import json

from build_publisher_isbn_crosschecks import ROOT, OUT, build, encode


def query(rows: list[dict], *, title: str = "", creator: str = "", isbn: str = "",
          state: str = "", source_ref: str = "", limit: int = 39) -> list[dict]:
    if not 1 <= limit <= 39:
        raise ValueError("limit must be in 1..39")
    return [row for row in rows
            if (not title or title.casefold() in row["publisher_title"].casefold())
            and (not creator or creator.casefold() in " ".join(row["publisher_creators"]).casefold())
            and (not isbn or isbn in row["publisher_isbn13"])
            and (not state or state == row["crosscheck_state"])
            and (not source_ref or source_ref == row["source_local_ref"])][:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", default="")
    parser.add_argument("--creator", default="")
    parser.add_argument("--isbn", default="")
    parser.add_argument("--state", default="")
    parser.add_argument("--source-ref", default="")
    parser.add_argument("--limit", type=int, default=39)
    parser.add_argument("--validate-sources", action="store_true", help="Recompile and refuse stale/tampered sidecar (always enforced)")
    args = parser.parse_args()
    result = build()
    output = ROOT / OUT
    if output.is_symlink() or not output.is_file() or output.read_bytes() != encode(result):
        raise SystemExit("PUBLISHER_ISBN_QUERY_REJECTED_STALE_OR_TAMPERED")
    matched = query(result["rows"], title=args.title, creator=args.creator, isbn=args.isbn,
                    state=args.state, source_ref=args.source_ref, limit=args.limit)
    print(json.dumps({"source_local_only": True, "private_edition_equivalence": "UNVERIFIED",
                      "match_count": len(matched), "rows": matched}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
