#!/usr/bin/env python3
"""Validate and compile five source-local, distributor-backed fictional memoirs.

The HTML source-body bytes were read on the owner host; only receipt hashes and
JSON-LD-derived bibliographic metadata are public. This is discovery, NOT an
admitted Source/Work binding, literary close read, or cover-image license.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

if __package__:
    from .build_research_leads import safe_read
    from .build_publisher_catalog import safe_write
else:
    from build_research_leads import safe_read
    from build_publisher_catalog import safe_write


PARTITION = Path("proposals/librarian/prh-star-trek-autobiographies-20261103")
SOURCE = PARTITION / "bundle.json"
OUTPUT = PARTITION / "records.json"
SOURCE_GROUP = "distributor:penguinrandomhouse.com:titan-books"
WORK_KEYS = {"work_id", "title", "creator", "isbn13", "format", "published_date",
             "pages", "locator", "cover_locator", "source_body_sha256", "source_body_bytes"}
SOURCE_PINS = {
    "prh-autobiography-kirk": ("The Autobiography of James T. Kirk", "David A. Goodman",
                                "9781783297481", "5acfa401c5ee942e185c308ded5ff264972b7a013852961aad8b2757083684af"),
    "prh-autobiography-picard": ("The Autobiography of Jean-Luc Picard", "David A. Goodman",
                                  "9781785659409", "119eddb5ca3d8d1b76bdd9d0b411f5d16e3a470b62507796e053301c37c51b26"),
    "prh-autobiography-janeway": ("The Autobiography of Kathryn Janeway", "Una McCormack",
                                   "9781789095333", "fa8dbce6950678405dfe4615a0e26782406af0b73acf0ad7409aaed991ac49ca"),
    "prh-autobiography-spock": ("The Autobiography of Mr. Spock", "Una McCormack",
                                 "9781785659416", "1c54fd926d0641d98fb41d827e9c999bb56e24fd11fae97ee4d304f4fbca8510"),
    "prh-autobiography-sisko": ("The Autobiography of Benjamin Sisko", "Derek Tyler Attico",
                                 "9781803366258", "9fe73b190eec8fe1bb3209d1d58c2c4dadd404b336ece66e6dfab22bb43e9d42"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _unique(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key {key}")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant {value}")


def valid_isbn(isbn: object) -> bool:
    if type(isbn) is not str or re.fullmatch(r"97[89]\d{10}", isbn) is None:
        return False
    weights = (1, 3) * 6
    return (10 - sum(int(d) * weight for d, weight in zip(isbn[:12], weights)) % 10) % 10 == int(isbn[-1])


def source_url(value: object, prefix: str) -> bool:
    if type(value) is not str:
        return False
    parsed = urlsplit(value)
    return (parsed.scheme == "https" and parsed.netloc == "www.penguinrandomhouse.com"
            and parsed.path.startswith(prefix) and parsed.path.endswith("/")
            and not parsed.username and not parsed.password and not parsed.query
            and not parsed.fragment and ".." not in parsed.path and value == parsed.geturl())


def raw_receipt(record: dict) -> bool:
    return (type(record.get("source_body_sha256")) is str and
            re.fullmatch(r"[a-f0-9]{64}", record["source_body_sha256"]) is not None and
            type(record.get("source_body_bytes")) is int and
            100_000 <= record["source_body_bytes"] <= 1_000_000)


def _observations(raw: object) -> tuple[dict, list[dict], dict]:
    require(type(raw) is dict and set(raw) == {"schema_version", "proposal_only",
            "accepted_work_effect", "accepted_source_binding_effect", "coverage_effect",
            "observed_on", "source_group", "source_method", "source_collection",
            "work_candidates", "collection_container"}, "unknown source-batch fields")
    require(raw["schema_version"] == "1.0.0" and raw["proposal_only"] is True,
            "not a versioned candidate source batch")
    require(all(raw[k] == "NONE" for k in
            ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect")),
            "admission or coverage effect forbidden")
    require(raw["source_group"] == SOURCE_GROUP and
            raw["source_method"] == "DIRECT_HTTP_RAW_HTML_AND_PUBLISHER_JSONLD_EXTRACTION",
            "provenance lineage mismatch")
    try:
        require(date.fromisoformat(raw["observed_on"]).isoformat() == raw["observed_on"],
                "bad source-observation date")
    except (ValueError, TypeError) as exc:
        raise ValueError("bad source-observation date") from exc
    collection = raw["source_collection"]
    require(type(collection) is dict and set(collection) == {
            "locator", "source_body_sha256", "source_body_bytes", "observed_title_count"},
            "unexpected distributor series source")
    require(collection["locator"] ==
            "https://www.penguinrandomhouse.com/series/0PT/star-trek-autobiographies-series/"
            and raw_receipt(collection) and collection["observed_title_count"] == 5,
            "distributor series source receipt invalid")
    works = raw["work_candidates"]
    require(type(works) is list and len(works) == 5, "expected five distinct publisher title records")
    ids, isbns, observed = set(), set(), []
    for row in works:
        require(type(row) is dict and set(row) == WORK_KEYS, "unexpected title/source field")
        ident, isbn = row["work_id"], row["isbn13"]
        require(type(ident) is str and re.fullmatch(r"prh-autobiography-[a-z]+", ident)
                and ident not in ids, "duplicate/invalid local Work candidate")
        require(valid_isbn(isbn) and isbn not in isbns, "invalid/duplicate edition ISBN")
        require(type(row["title"]) is str and row["title"].startswith("The Autobiography of ")
                and 15 <= len(row["title"]) <= 100 and type(row["creator"]) is str
                and 3 <= len(row["creator"]) <= 80, "unexpected title/creator")
        require(ident in SOURCE_PINS and
                (row["title"], row["creator"], isbn, row["source_body_sha256"]) == SOURCE_PINS[ident],
                "title/creator/ISBN/raw page hash mismatches independently reviewed source pin")
        require(row["format"] == "PAPERBACK" and type(row["pages"]) is int and
                100 <= row["pages"] <= 1000, "format/page mismatch")
        try:
            require(date.fromisoformat(row["published_date"]).isoformat() == row["published_date"],
                    "bad publication date")
        except (ValueError, TypeError) as exc:
            raise ValueError("bad publication date") from exc
        require(source_url(row["locator"], "/books/") and
                row["cover_locator"] == f"https://images.penguinrandomhouse.com/cover/{isbn}"
                and raw_receipt(row), "publisher locator/source/cover metadata invalid")
        ids.add(ident); isbns.add(isbn)
        observed.append(row)
    container = raw["collection_container"]
    require(type(container) is dict and set(container) == {"container_id", "title", "isbn13",
            "format", "locator", "source_body_sha256", "source_body_bytes",
            "contains_work_ids", "counted_as_independent_work"}, "invalid collection keys")
    require(container["container_id"] == "prh-captains-autobiographies-boxed-set" and
            container["format"] == "BOXED_SET" and
            container["counted_as_independent_work"] is False and
            valid_isbn(container["isbn13"]) and container["isbn13"] not in isbns and
            source_url(container["locator"], "/books/") and raw_receipt(container),
            "collection cannot be silently promoted to another Work")
    require(container["contains_work_ids"] == ["prh-autobiography-kirk",
            "prh-autobiography-picard", "prh-autobiography-janeway"],
            "collection contents unresolved")
    require(set(container["contains_work_ids"]) <= ids, "container points to missing Work")
    return collection, observed, container


def build(root: Path) -> bytes:
    raw = safe_read(root, SOURCE, max_bytes=65_000)
    source = json.loads(raw, object_pairs_hook=_unique, parse_constant=_reject_constant)
    series, rows, container = _observations(source)
    works, editions, sources, bindings = [], [], [], []
    for row in rows:
        wid, isbn = row["work_id"], row["isbn13"]
        sid = "proposed-prh-source-" + isbn
        works.append({"record_type": "work", "work_id": wid, "status": "PROPOSED",
                      "medium": "LITERATURE", "work_type": "FICTIONAL_MEMOIR",
                      "title": row["title"], "creator": row["creator"],
                      "series": "Star Trek Autobiographies"})
        editions.append({"edition_candidate_id": "proposed-prh-edition-" + isbn,
                         "work_id": wid, "source_id": sid, "isbn13": isbn,
                         "format": row["format"], "publication_date": row["published_date"],
                         "status": "PROPOSED"})
        sources.append({"record_type": "source", "source_id": sid, "status": "PROPOSED",
                        "source_kind": "DISTRIBUTOR_JSONLD_EDITION_METADATA",
                        "provider": "Penguin Random House (Titan Books distribution)",
                        "locator": row["locator"], "content_hash_sha256": row["source_body_sha256"],
                        "source_body_bytes": row["source_body_bytes"],
                        "independence_group": SOURCE_GROUP, "isbn13": isbn,
                        "publisher_cover_locator": row["cover_locator"],
                        "cover_license_verification": "NOT_ESTABLISHED"})
        bindings.append({"record_type": "source_work_binding",
                         "binding_id": "proposed-prh-binding-" + isbn,
                         "source_id": sid, "work_id": wid, "lifecycle": "PROPOSED",
                         "mapping_role": "METADATA_ONLY", "fixture_only": False})
    result = {"schema_version": "1.0.0", "proposal_only": True,
              "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
              "coverage_effect": "NONE", "source_group": SOURCE_GROUP,
              "observed_on": source["observed_on"], "distributor_series_source": series,
              "work_count": len(works), "works": works, "edition_candidates": editions,
              "sources": sources, "bindings": bindings,
              "collection_container": container,
              "raw_html_publication": "NONE", "deep_read_effect": "NONE"}
    return (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        target = OUTPUT
        payload = build(args.repo_root)
        if args.check:
            require(safe_read(args.repo_root, target, max_bytes=64_000) == payload,
                    "stale generated distributor candidate packet")
        else:
            safe_write(args.repo_root, target, payload)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        print(f"PRH_LITERATURE_REJECTED: {exc}", file=sys.stderr)
        return 1
    print("PRH_LITERATURE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
