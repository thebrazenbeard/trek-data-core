#!/usr/bin/env python3
"""Query the held, deterministic 39-card OPF source-local metadata review sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import build_opf_sample_cards as builder


def validated_cards(root: Path = builder.ROOT) -> list[dict]:
    path = root / builder.OUTPUT
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 64 * 1024:
        raise ValueError("review sample file absent, symlinked or oversized")
    actual = path.read_bytes()
    if actual != builder.encode(builder.build(root)):
        raise ValueError("review sample does not match exact pinned OPF metadata source")
    return json.loads(actual)["card_rows"]


def search(rows: list[dict], *, query: str = "", source_id: str = "", offset: int = 0,
           limit: int = 20) -> dict:
    if not isinstance(query, str) or len(query) > 160 or not isinstance(source_id, str) or len(source_id) > 30:
        raise ValueError("query/source ID exceeds allowed length")
    if not isinstance(offset, int) or offset < 0 or not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("bad pagination")
    terms = query.casefold().split()
    matched = [row for row in rows if (not source_id or row["source_local_id"] == source_id)
               and all(term in " ".join([row["title_as_encoded_in_opf"],
                                         *row["creator_strings_as_encoded_in_opf"],
                                         row["source_local_id"]]).casefold() for term in terms)]
    page = matched[offset:offset + limit]
    return {
        "data_status": "HELD_SOURCE_LOCAL_OPF_METADATA_REVIEW_SAMPLE_ONLY",
        "query": query, "source_local_id": source_id,
        "total_matches": len(matched), "offset": offset, "limit": limit,
        "next_offset": offset + limit if offset + limit < len(matched) else None,
        "rows": page, "distinct_works": None, "work_admission_effect": "NONE",
        "coverage_effect": "NONE", "public_explorer_visibility": "NOT_AUTO_LOADED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q", default="")
    parser.add_argument("--source-id", default="")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    try:
        result = search(validated_cards(), query=args.q, source_id=args.source_id,
                        offset=args.offset, limit=args.limit)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
