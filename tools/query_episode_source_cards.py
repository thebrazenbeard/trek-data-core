#!/usr/bin/env python3
"""Offline callable search of 20 accepted-but-HELD Paramount+ episode guide cards."""

from __future__ import annotations

import argparse
import json

try:
    from .build_episode_source_cards import ROOT, OUTPUT, build, encode, require
except ImportError:  # Direct entrypoint: python tools/query_episode_source_cards.py
    from build_episode_source_cards import ROOT, OUTPUT, build, encode, require


def query(data, text="", series="all", status="all", tag="all", limit=20):
    require(type(text) is str and len(text) <= 160, "query too long")
    require(series in ("all", "PIC", "SNW"), "unknown series")
    require(status in ("all", "HELD_PUBLISHER_GUIDE_ONLY"), "unsupported source status")
    require(type(tag) is str and len(tag) <= 100, "invalid facet tag")
    require(type(limit) is int and 1 <= limit <= 20, "query limit outside bounded cards")
    terms = text.casefold().split()
    selected = []
    for row in data["rows"]:
        if series != "all" and row["series_code"] != series:
            continue
        if status != "all" and row["source_status"] != status:
            continue
        if tag != "all" and tag not in row["tags"]:
            continue
        body = " ".join((row["title"], row["series_title"], row["source_local_id"],
                         f"S{row['season']}E{row['episode']:02}", row["source_status"],
                         *row["publisher_utterance_labels"], *row["tags"])).casefold()
        if all(term in body for term in terms):
            selected.append(row)
    return {"status": "SOURCE_LOCAL_HELD_ONLY", "matching_count": len(selected),
            "returned_count": min(len(selected), limit), "rows": selected[:limit],
            "coverage_effect": "NONE", "admission_effect": "NONE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q", default="")
    parser.add_argument("--series", choices=("all", "PIC", "SNW"), default="all")
    parser.add_argument("--status", choices=("all", "HELD_PUBLISHER_GUIDE_ONLY"), default="all")
    parser.add_argument("--tag", default="all")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--validate-sources", action="store_true", help="Re-read and validate all four upstream packets")
    args = parser.parse_args()
    data = build()  # Always validates original upstream sources and per-row SHA pins.
    target = ROOT / OUTPUT
    require(target.is_file() and not target.is_symlink() and target.read_bytes() == encode(data),
            "published episode card artifact is stale or poisoned")
    print(json.dumps(query(data, args.q, args.series, args.status, args.tag, args.limit),
                     sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
