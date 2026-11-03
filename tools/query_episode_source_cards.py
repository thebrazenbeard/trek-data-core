#!/usr/bin/env python3
"""Offline callable search of 20 accepted-but-HELD Paramount+ episode guide cards.

All CLI calls first rebuild the pinned source receipts and compare the published
sidecar byte-for-byte. IDs below are *source-local cards*, never admitted Works.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

try:
    from .build_episode_source_cards import ROOT, OUTPUT, build, encode, require
except ImportError:  # Direct entrypoint: python tools/query_episode_source_cards.py
    from build_episode_source_cards import ROOT, OUTPUT, build, encode, require


def query(data, text="", series="all", status="all", tag="all", limit=20,
          *, local_id="", source_batch="", offset=0, facets=False):
    """Query a previously source-validated build with exact provenance filters.

    Ordering is that of the deterministic publisher-card build, rather than a
    guessed global episode timeline. Facets count matches *before* pagination.
    """
    require(type(text) is str and len(text) <= 160, "query too long")
    require(series in ("all", "PIC", "SNW"), "unknown series")
    require(status in ("all", "HELD_PUBLISHER_GUIDE_ONLY"), "unsupported source status")
    require(type(tag) is str and len(tag) <= 100, "invalid facet tag")
    require(type(limit) is int and 1 <= limit <= 20, "query limit outside bounded cards")
    require(type(local_id) is str and len(local_id) <= 100, "invalid source-local card ID")
    require(type(source_batch) is str and len(source_batch) <= 100, "invalid source batch")
    require(type(offset) is int and 0 <= offset <= 1_000_000, "invalid query offset")
    require(type(facets) is bool, "invalid facet request")
    terms = text.casefold().split()
    selected = []
    for row in data["rows"]:
        if series != "all" and row["series_code"] != series:
            continue
        if status != "all" and row["source_status"] != status:
            continue
        if tag != "all" and tag not in row["tags"]:
            continue
        if local_id and row["source_local_id"] != local_id:
            continue
        if source_batch and row["source_batch"] != source_batch:
            continue
        body = " ".join((row["title"], row["series_title"], row["source_local_id"],
                         f"S{row['season']}E{row['episode']:02}", row["source_status"],
                         *row["publisher_utterance_labels"], *row["tags"])).casefold()
        if all(term in body for term in terms):
            selected.append(row)
    page = selected[offset:offset + limit]
    result = {
        "status": "SOURCE_LOCAL_HELD_ONLY",
        "identity_scope": "SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK",
        "matching_count": len(selected), "returned_count": len(page),
        "offset": offset, "limit": limit,
        "next_offset": offset + len(page) if offset + len(page) < len(selected) else None,
        "rows": page, "coverage_effect": "NONE", "admission_effect": "NONE",
    }
    if facets:
        result["matched_facets"] = {
            "series_code": dict(sorted(Counter(row["series_code"] for row in selected).items())),
            "source_batch": dict(sorted(Counter(row["source_batch"] for row in selected).items())),
            "source_status": dict(sorted(Counter(row["source_status"] for row in selected).items())),
            "publisher_utterance_tags": dict(sorted(Counter(
                tag for row in selected for tag in row["tags"]
                if tag.startswith("publisher-utterance:")).items())),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--q", default="")
    parser.add_argument("--series", choices=("all", "PIC", "SNW"), default="all")
    parser.add_argument("--status", choices=("all", "HELD_PUBLISHER_GUIDE_ONLY"), default="all")
    parser.add_argument("--tag", default="all")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--id", dest="local_id", default="", help="Exact source-local card ID (not Work identity)")
    parser.add_argument("--source-batch", default="", help="Exact accepted packet batch: PIC-FIRST5, etc.")
    parser.add_argument("--offset", type=int, default=0, help="Deterministic result pagination offset")
    parser.add_argument("--facets", action="store_true", help="Count matched source-local facets before pagination")
    parser.add_argument("--validate-sources", action="store_true", help="Re-read and validate all four upstream packets")
    args = parser.parse_args()
    try:
        data = build()  # Always validates original upstream sources and per-row SHA pins.
        target = ROOT / OUTPUT
        require(target.is_file() and not target.is_symlink() and target.read_bytes() == encode(data),
                "published episode card artifact is stale or poisoned")
        result = query(data, args.q, args.series, args.status, args.tag, args.limit,
                       local_id=args.local_id, source_batch=args.source_batch,
                       offset=args.offset, facets=args.facets)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
