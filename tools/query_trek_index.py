#!/usr/bin/env python3
"""Query the downloadable, static, source-local Trek search index as JSON.

Examples:
  python3 tools/query_trek_index.py --q 'Doomsday Machine' --series TOS
  python3 tools/query_trek_index.py --medium LITERATURE --synopsis reviewed_publisher_paraphrase
  python3 tools/query_trek_index.py --tag series:voy --limit 20 --offset 20
  python3 tools/query_trek_index.py --id lead:0000 --validate-sources

Not a hosted API: GitHub Pages serves the unparameterized JSON file, and this
standard-library CLI performs a bounded, reproducible client-side query.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from build_source_local_search import INPUTS, ROOT, SERIES, VALID_MEDIA, build, encoded, normalized

DEFAULT_INDEX = ROOT / "explorer/search-catalog.json"
ID_PATTERN = re.compile(r"^[a-z0-9:_.-]{3,210}$")
REQUIRED = frozenset(("row_id", "title", "medium", "candidate_kind", "context", "series_code",
                      "source_group", "source_input", "source_locator", "verification_status",
                      "metadata_recheck_status", "metadata_recheck_batch", "synopsis_status",
                      "synopsis_receipt_sha256", "tags", "search_text", "identity_scope",
                      "coverage_effect", "admission_effect"))
SOURCE_HOSTS = {
    "wikidata:wdqs": frozenset(("www.wikidata.org",)),
    "publisher:paramount": frozenset(("www.startrek.com", "www.paramountplus.com", "www.mikrosanimation.com", "youtu.be")),
    "publisher:paramountplus.com": frozenset(("www.paramountplus.com",)),
    "publisher:startrek.com": frozenset(("www.startrek.com",)),
    "publisher:simonandschuster.com": frozenset(("www.simonandschuster.com",)),
    "distributor:penguinrandomhouse.com:titan-books": frozenset(("www.penguinrandomhouse.com",)),
}
KINDS = frozenset(("WIKIDATA_EPISODE", "PUBLISHER_EPISODE_SLOT", "PUBLISHER_REFERENCE", "FEATURE_FILM",
                   "STREAMING_FILM", "NOVEL", "FICTIONAL_MEMOIR", "SCRIPTED_SHORT",
                   "PROMOTIONAL_ANIMATION", "SCRIPTED_AUDIO_SERIES"))
CHECK_STATES = frozenset(("not_rechecked", "rechecked_exact", "rechecked_unresolved"))
SYNOPSIS_STATES = frozenset(("pending", "reviewed_publisher_paraphrase"))


def validate(data: dict, *, root: Path | None = None) -> list[dict]:
    """Reject tampered shape/scope; optional exact input-byte digest validation."""
    if not isinstance(data, dict) or data.get("schema_version") != "1.0.0" or \
       data.get("data_status") != "SOURCE_LOCAL_SEARCH_PROJECTION_ONLY" or \
       data.get("identity_scope") != "SOURCE_LOCAL_NOT_DEDUPLICATED" or \
       data.get("denominator_status") != "NOT_ESTABLISHED" or \
       data.get("coverage_effect") != "NONE" or data.get("admission_effect") != "NONE" or \
       not isinstance(data.get("rows"), list) or not 0 < len(data["rows"]) <= 5000 or \
       data.get("row_count") != len(data["rows"]):
        raise ValueError("Untrusted index envelope or changed research scope")
    hashes = data.get("source_input_sha256")
    if not isinstance(hashes, list) or [r.get("path") for r in hashes] != list(INPUTS) or \
       any(not re.fullmatch(r"[0-9a-f]{64}", r.get("sha256", "")) for r in hashes):
        raise ValueError("Missing source hash provenance")
    if root is not None:
        for receipt in hashes:
            path = root / receipt["path"]
            if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != receipt["sha256"]:
                raise ValueError(f"Source bytes drifted: {receipt['path']}")
        # Hashes listed *inside* a downloaded JSON do not authenticate its own
        # rows. With source custody available compare the complete rebuild.
        if encoded(build(root)) != encoded(data):
            raise ValueError("Search JSON differs from deterministic source-derived projection")
    rows = data["rows"]
    previous = ""
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Untrusted index row type")
        source_url = row.get("source_locator")
        try:
            parsed = urlsplit(source_url or "")
            safe_source = (source_url is None and row.get("source_group") == "wikidata:wdqs") or (
                isinstance(source_url, str) and parsed.scheme == "https" and
                parsed.hostname in SOURCE_HOSTS.get(row.get("source_group"), ()) and
                parsed.username is None and parsed.password is None and parsed.port is None and
                not parsed.query and not parsed.fragment and parsed.path.startswith("/"))
        except (ValueError, TypeError):
            safe_source = False
        context = row.get("context")
        series_code = (context.split(maxsplit=1)[0] if isinstance(context, str) and context.split() and
                       row.get("medium") == "EPISODE" and context.split(maxsplit=1)[0] in SERIES else None)
        # In downloaded mode enforce the exact possible structural tag set;
        # a self-inserted 'canon:*' or 'work:*' tag must never be queryable.
        expected_tags = sorted([
            "medium:" + str(row.get("medium", "")).lower(),
            "kind:" + str(row.get("candidate_kind", "")).lower(),
            "source:" + str(row.get("source_group", "")).lower(),
            "metadata:" + str(row.get("metadata_recheck_status", "")),
            "synopsis:" + str(row.get("synopsis_status", "")),
            *(["series:" + series_code.lower()] if series_code else []),
        ])
        if row.keys() != REQUIRED or \
           not isinstance(row["row_id"], str) or not ID_PATTERN.fullmatch(row["row_id"]) or \
           row["row_id"] <= previous or row["identity_scope"] != "SOURCE_LOCAL" or \
           row["coverage_effect"] != "NONE" or row["admission_effect"] != "NONE" or \
           row["verification_status"] != "UNVERIFIED_METADATA" or \
           row["medium"] not in VALID_MEDIA or row["candidate_kind"] not in KINDS or \
           row["series_code"] != series_code or \
           row["metadata_recheck_status"] not in CHECK_STATES or \
           row["synopsis_status"] not in SYNOPSIS_STATES or \
           (row["metadata_recheck_status"] == "not_rechecked") != (row["metadata_recheck_batch"] is None) or \
           (row["synopsis_status"] == "pending") != (row["synopsis_receipt_sha256"] is None) or \
           (row["metadata_recheck_batch"] is not None and not re.fullmatch(r"B\d{3}", str(row["metadata_recheck_batch"]))) or \
           (row["synopsis_receipt_sha256"] is not None and not re.fullmatch(r"[0-9a-f]{64}", str(row["synopsis_receipt_sha256"]))) or \
           not isinstance(row["source_input"], str) or not re.fullmatch(r"(?:explorer|proposals)/[a-z0-9/_.-]+\.json", row["source_input"]) or \
           not isinstance(row["search_text"], str) or len(row["search_text"]) > 5000 or \
           not isinstance(row["title"], str) or not row["title"] or \
           not isinstance(row["tags"], list) or row["tags"] != expected_tags or \
           any(not isinstance(tag, str) or len(tag) > 160 for tag in row["tags"]) or \
           not safe_source:
            raise ValueError("Untrusted row shape or identity/coverage promotion")
        previous = row["row_id"]
    facets = data.get("facet_counts")
    expected_facets = {
        name: dict(sorted(Counter(row[name] or "none" for row in rows).items()))
        for name in ("medium", "candidate_kind", "series_code", "source_group", "metadata_recheck_status", "synopsis_status")
    }
    if facets != expected_facets:
        raise ValueError("Search facet counts disagree with indexed rows")
    return rows


def query(rows: list[dict], *, text: str = "", row_id: str = "", medium: str = "", series: str = "",
          kind: str = "", source_group: str = "", source_input: str = "", context: str = "",
          verification: str = "", synopsis: str = "", tags: tuple[str, ...] = (),
          offset: int = 0, limit: int = 40) -> dict:
    """Filter in stable source row-ID order; every supplied tag is required."""
    terms = normalized(text).split()
    context_terms = normalized(context).split()
    wanted_tags = set(tags)
    found = []
    for row in rows:
        if row_id and row["row_id"] != row_id:
            continue
        if medium and row["medium"] != medium.upper():
            continue
        if series and (row["series_code"] or "") != series.upper():
            continue
        if kind and row["candidate_kind"] != kind.upper():
            continue
        if source_group and row["source_group"] != source_group:
            continue
        if source_input and row["source_input"] != source_input:
            continue
        if verification and row["metadata_recheck_status"] != verification:
            continue
        if synopsis and row["synopsis_status"] != synopsis:
            continue
        if wanted_tags and not wanted_tags.issubset(row["tags"]):
            continue
        if context_terms and not all(t in normalized(row["context"]) for t in context_terms):
            continue
        if terms and not all(t in row["search_text"] for t in terms):
            continue
        found.append(row)
    result = found[offset:offset + limit]
    return {"data_status": "SOURCE_LOCAL_SEARCH_RESULTS_NOT_ADMITTED",
            "identity_scope": "SOURCE_LOCAL_NOT_DEDUPLICATED",
            "coverage_effect": "NONE", "admission_effect": "NONE",
            "total_matches": len(found), "offset": offset, "limit": limit,
            "next_offset": offset + len(result) if offset + len(result) < len(found) else None,
            "rows": result}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="Downloaded search-catalog.json")
    parser.add_argument("--validate-sources", action="store_true", help="Verify source input bytes in this checkout")
    parser.add_argument("--q", default="", help="AND-match normalized search terms")
    parser.add_argument("--id", dest="row_id", default="", help="Exact source-local row ID")
    parser.add_argument("--medium", default="", help="EPISODE, FILM, LITERATURE, SHORT_FORM, AUDIO")
    parser.add_argument("--series", default="", help="Source-local series code for EPISODE observations")
    parser.add_argument("--kind", default="", help="Exact candidate kind")
    parser.add_argument("--source-group", default="", help="Exact source lineage family")
    parser.add_argument("--source-input", default="", help="Exact repository source-relative provenance path")
    parser.add_argument("--context", default="", help="Match source-local contextual/creator text")
    parser.add_argument("--verification", default="", choices=("", "not_rechecked", "rechecked_exact", "rechecked_unresolved"))
    parser.add_argument("--synopsis", default="", choices=("", "pending", "reviewed_publisher_paraphrase"))
    parser.add_argument("--tag", action="append", default=[], help="Structural tag, repeat for AND matching")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100 or not 0 <= args.offset <= 1000000 or \
       any(len(value) > 240 for value in (args.q, args.row_id, args.medium, args.series, args.kind,
           args.source_group, args.source_input, args.context, args.verification, args.synopsis)) or \
       len(args.tag) > 12 or any(not tag or len(tag) > 160 for tag in args.tag):
        parser.error("Query exceeds documented limits")
    try:
        data = json.loads(args.index.read_text(encoding="utf-8"))
        rows = validate(data, root=ROOT if args.validate_sources else None)
        print(json.dumps(query(rows, text=args.q, row_id=args.row_id, medium=args.medium,
            series=args.series, kind=args.kind, source_group=args.source_group,
            source_input=args.source_input, context=args.context, verification=args.verification,
            synopsis=args.synopsis, tags=tuple(args.tag), offset=args.offset,
            limit=args.limit), ensure_ascii=False, indent=2, sort_keys=True))
    except (ValueError, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        parser.error(f"Search index rejected: {exc}")


if __name__ == "__main__":
    main()
