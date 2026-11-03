#!/usr/bin/env python3
"""Callable, offline query of *separate* publisher-edition discovery leads.

These are not admitted Works, and this query intentionally never combines its
three-row count with the independently governed 1,214-row Explorer directory.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from build_lit_publisher_leads import (ACCEPTED_SOURCE_COMMIT, ACCEPTED_SOURCE_SHA256,
                                       CLAIM_PREFIXES, EXPECTED, INPUT, OUTPUT, ROOT,
                                       TAG, build, encode, norm, valid_isbn)

REQUIRED = frozenset(("row_id", "title", "creator", "publisher_series", "edition_format", "isbn13",
                      "publisher_publication_date", "publisher_imprint", "publisher_extent",
                      "source_group", "source_input", "source_locator", "query_tags", "search_text",
                      "promotional_claim_scope", "synopsis_status", "private_edition_equivalence",
                      "identity_scope", "coverage_effect", "admission_effect"))


def validate(value: object, *, sources: bool = False) -> list[dict]:
    if not isinstance(value, dict) or value.get("schema_version") != "1.0.0" or \
       value.get("data_status") != "PUBLISHER_EDITION_LEADS_SEARCH_OVERLAY_ONLY" or \
       value.get("source_input") != INPUT or value.get("source_input_sha256") != ACCEPTED_SOURCE_SHA256 or \
       value.get("source_accepted_commit") != ACCEPTED_SOURCE_COMMIT or \
       value.get("identity_scope") != "SOURCE_LOCAL_EDITION_NOT_RECONCILED" or \
       any(value.get(effect) != "NONE" for effect in ("denominator_effect", "coverage_effect", "admission_effect",
                                                   "public_synopsis_effect", "artwork_release_effect")) or \
       not isinstance(value.get("rows"), list) or len(value["rows"]) != 3 or value.get("row_count") != 3:
        raise ValueError("Untrusted source-only edition lead index envelope")
    previous = ""
    for row in value["rows"]:
        if not isinstance(row, dict) or row.keys() != REQUIRED:
            raise ValueError("Untrusted publisher-edition row shape")
        isbn = row.get("isbn13")
        parsed = urlsplit(row.get("source_locator", ""))
        tags = row.get("query_tags")
        promo = [tag.removeprefix("publisher-claim:") for tag in tags
                 if isinstance(tag, str) and tag.startswith("publisher-claim:")] if isinstance(tags, list) else []
        structural = ("format:" + str(row.get("edition_format", "")).lower(),
                      "kind:publisher-edition-lead", "medium:literature")
        if not valid_isbn(isbn) or isbn not in EXPECTED or \
           (row.get("title"), row.get("creator"), row.get("edition_format")) != EXPECTED[isbn] or \
           row.get("row_id") != "publisher-edition:" + isbn or row["row_id"] <= previous or \
           parsed.scheme != "https" or parsed.netloc != "www.simonandschuster.com" or \
           parsed.username or parsed.password or parsed.query or parsed.fragment or \
           not parsed.path.startswith("/books/") or parsed.path.rsplit("/", 1)[-1] != isbn or \
           row.get("source_group") != "publisher:simonandschuster.com" or row.get("source_input") != INPUT or \
           row.get("identity_scope") != "EDITION_CANDIDATE_SOURCE_LOCAL" or \
           row.get("coverage_effect") != "NONE" or row.get("admission_effect") != "NONE" or \
           row.get("private_edition_equivalence") != "UNVERIFIED" or \
           row.get("synopsis_status") != "UNREVIEWED_PARAPHRASE_HELD_NOT_PUBLIC" or \
           row.get("promotional_claim_scope") != "PUBLISHER_COPY_TAGS_NOT_FICTIONAL_TRUTH" or \
           not isinstance(tags, list) or tags != sorted(set(tags)) or len(tags) != 8 or \
           any(tag not in tags for tag in structural) or len(promo) != 5 or \
           any(not TAG.fullmatch(tag) or tag.partition(":")[0] not in CLAIM_PREFIXES for tag in promo) or \
           not isinstance(row.get("search_text"), str) or not 1 <= len(row["search_text"]) <= 3000:
            raise ValueError("Untrusted publisher-edition row identity, provenance or tags")
        previous = row["row_id"]
    if sources and encode(value) != encode(build(ROOT)):
        raise ValueError("Downloaded publisher lead overlay differs from exact source-derived projection")
    return value["rows"]


def query(rows: list[dict], *, q: str = "", isbn: str = "", tags: tuple[str, ...] = (),
          offset: int = 0, limit: int = 40) -> dict:
    terms = norm(q).split()
    found = [row for row in rows if (not isbn or row["isbn13"] == isbn)
             and set(tags).issubset(row["query_tags"])
             and all(word in row["search_text"] for word in terms)]
    selection = found[offset:offset + limit]
    return {
        "data_status": "UNADMITTED_PUBLISHER_EDITION_LEADS_ONLY",
        "source_group": "publisher:simonandschuster.com",
        "identity_scope": "SOURCE_LOCAL_EDITION_NOT_RECONCILED",
        "denominator_effect": "NONE", "coverage_effect": "NONE", "admission_effect": "NONE",
        "total_matches": len(found), "offset": offset, "limit": limit,
        "next_offset": offset + len(selection) if offset + len(selection) < len(found) else None,
        "rows": selection,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=ROOT / OUTPUT)
    parser.add_argument("--validate-sources", action="store_true", help="Verify exact accepted source and projection bytes")
    parser.add_argument("--q", default="", help="AND-match normalized metadata and publisher-claim tag terms")
    parser.add_argument("--isbn", default="", help="Exact ISBN-13")
    parser.add_argument("--tag", action="append", default=[], help="Full source-scoped tag, repeated for AND")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100 or not 0 <= args.offset <= 1000000 or \
       len(args.q) > 240 or len(args.isbn) > 13 or len(args.tag) > 12 or \
       any(not tag or len(tag) > 145 for tag in args.tag):
        parser.error("Query exceeds publisher edition lead limits")
    try:
        value = json.loads(args.index.read_text(encoding="utf-8"))
        rows = validate(value, sources=args.validate_sources)
        print(json.dumps(query(rows, q=args.q, isbn=args.isbn, tags=tuple(args.tag),
                               offset=args.offset, limit=args.limit), ensure_ascii=False, sort_keys=True, indent=2))
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError) as exc:
        parser.error(f"Publisher edition lead index rejected: {exc}")


if __name__ == "__main__":
    main()
