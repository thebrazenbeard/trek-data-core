#!/usr/bin/env python3
"""Callable offline search for source-local Paramount film-page metadata only."""

from __future__ import annotations

import argparse
import json

from build_paramount_film_rechecks import ROOT, OUTPUT, build, encode


def query(rows: list[dict], *, text: str = "", tag: str = "", status: str = "",
          year: int | None = None, limit: int = 13) -> list[dict]:
    if not isinstance(limit, int) or not 1 <= limit <= 13:
        raise ValueError("limit must be 1..13")
    if any(len(v) > 150 for v in (text, tag, status)):
        raise ValueError("query or facet too long")
    terms = text.casefold().split()
    return [
        row for row in rows
        if (not tag or tag in row["tags"])
        and (not status or status == row["recheck_status"])
        and (year is None or year == row["year_as_listed"])
        and all(t in " ".join([
            row["source_page_slug"], row["source_local_candidate_id"],
            row["genre_as_listed"], row["rating_as_listed"],
            *row["selected_directors_as_listed"], *row["selected_cast_performers_as_listed"],
        ]).casefold() for t in terms)
    ][:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q", default="")
    parser.add_argument("--tag", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--year", type=int)
    parser.add_argument("--limit", type=int, default=13)
    args = parser.parse_args()
    artifact = build()
    sidecar = ROOT / OUTPUT
    if sidecar.is_symlink() or not sidecar.is_file() or sidecar.read_bytes() != encode(artifact):
        parser.error("source-local Paramount film projection stale/tampered")
    results = query(artifact["rows"], text=args.q, tag=args.tag, status=args.status,
                    year=args.year, limit=args.limit)
    print(json.dumps({
        "data_status": artifact["data_status"],
        "source_local_only": True, "full_films_viewed": 0,
        "match_count": len(results), "rows": results,
    }, sort_keys=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
