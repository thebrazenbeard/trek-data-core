#!/usr/bin/env python3
"""Build an OFFLINE, HELD-only preview of two unmerged publisher research PRs.

The output is explicitly *not* the accepted Explorer projection. This tool
does not modify any repository file or create Works, evidence or coverage.
It reads exact, independently pinned Git blobs from review branches, and
prints a limited bibliographic metadata preview to stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_OUTPUT = ROOT / "proposals" / "consolidator" / "held-publisher-ui-preview-20261104" / "held-publisher-preview.json"
EFFECT_FIELDS = ("accepted_source_binding_effect", "accepted_work_effect", "accepted_evidence_effect",
                 "coverage_effect", "public_synopsis_effect", "artwork_release_effect")
SOURCES = (
    {
        "pr": 494,
        "head": "0ec895e17f70b505579b35c69e4af423e4b1dd6f",
        "path": "proposals/research/lit-five-publisher-bibliography-20261104/records.json",
        "sha256": "db04282ad717cb4f71932a5e2b7e8267c5e26b295dd7d02c1cf455b57be38c13",
        "family": "publisher:simonandschuster.com",
        "schema": "trek-lit-five-first-party-edition-leads-v1",
        "isbns": frozenset(("9780743453868", "9780743453851", "9780743420730", "9780743400817", "9780743419864")),
    },
    {
        "pr": 497,
        "head": "785e4516d65b8a8e3769e7eaf69875966bf2e4bb",
        "path": "proposals/research/lit-titan-five-artbooks-20261104/records.json",
        "sha256": "c01c276712477b94565cd61ec275fa83c6f2130637022abf7cca1fd8a9bedc8d",
        "family": "publisher:titanbooks.com",
        "schema": "trek-lit-titan-five-nonfiction-artbook-editions-v1",
        "isbns": frozenset(("9781785659119", "9781785659348", "9781781166703", "9781785653872", "9781789095159")),
    },
)


def fail(message: str) -> None:
    raise ValueError(message)


def isbn_valid(value: object) -> bool:
    return isinstance(value, str) and len(value) == 13 and value.isascii() and value.isdigit() and \
        sum((1 if i % 2 == 0 else 3) * int(n) for i, n in enumerate(value)) % 10 == 0


def safe_text(value: object, maxlen: int = 180) -> bool:
    return isinstance(value, str) and 1 <= len(value) <= maxlen and value == value.strip() and \
        not any(unicodedata.category(char) in ("Cc", "Cf", "Cs") for char in value)


def official_url(value: object, family: str, isbn: str) -> bool:
    if not isinstance(value, str) or not safe_text(value, 250):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    host = "www.simonandschuster.com" if family.endswith("simonandschuster.com") else "titanbooks.com"
    if parsed.scheme != "https" or parsed.netloc != host or parsed.username or parsed.password or \
       parsed.query or parsed.fragment or ".." in parsed.path or "%" in parsed.path:
        return False
    return (bool(re.fullmatch(r"/books/[A-Za-z0-9-]+/[A-Za-z0-9-]+/Star-Trek-[A-Za-z0-9-]+/\d{13}", parsed.path))
            and parsed.path.endswith("/" + isbn)) if host.startswith("www.") else \
           bool(re.fullmatch(r"/\d+-star-trek-[a-z0-9-]+/", parsed.path))


def check_document(doc: object, config: dict) -> list[dict]:
    if not isinstance(doc, dict) or doc.get("schema_version") != config["schema"] or \
       doc.get("proposal_only") is not True or any(doc.get(k) != "NONE" for k in EFFECT_FIELDS) or \
       doc.get("publisher_edition_count") != 5:
        fail("Draft source has unsupported schema, scope or admission effect")
    simon = config["pr"] == 494
    if simon:
        if doc.get("first_party_upstream_family") != config["family"] or \
           doc.get("first_party_upstream_family_count") != 1 or doc.get("candidate_work_count") != 5 or \
           any(doc.get(k) is not False for k in ("full_text_or_audio_read", "edition_completeness_verified",
                                                    "private_source_edition_matches_verified",
                                                    "copyrighted_story_text_or_art_reproduced")):
            fail("Simon & Schuster draft scope is no longer held")
    else:
        if doc.get("first_party_publisher_lineage") != config["family"] or \
           doc.get("first_party_publisher_family_count") != 1 or doc.get("local_work_candidate_count") != 5 or \
           any(doc.get(k) is not False for k in ("full_book_text_read", "full_artwork_read_or_stored",
                                                    "edition_completeness_verified", "private_source_matches_verified")):
            fail("Titan draft scope is no longer held")
    entries = doc.get("candidates" if simon else "works")
    if not isinstance(entries, list) or len(entries) != 5:
        fail("Draft row count drifted")
    seen = set()
    rows = []
    for item in entries:
        if not isinstance(item, dict):
            fail("Invalid metadata row")
        isbn = item.get("edition_isbn13")
        if not isbn_valid(isbn) or isbn not in config["isbns"] or isbn in seen:
            fail("Unreviewed, invalid or repeated ISBN")
        seen.add(isbn)
        title = item.get("publisher_work_title" if simon else "publisher_display_title")
        url = item.get("source_url" if simon else "publisher_source_url")
        credits = item.get("publisher_creator_credits")
        if not safe_text(title) or not safe_text(item.get("local_work_candidate_id")) or \
           not official_url(url, config["family"], isbn) or not isinstance(credits, list) or not 1 <= len(credits) <= 4 or \
           any(not isinstance(c, dict) or not safe_text(c.get("name")) or
               c.get("role") not in ("AUTHOR", "EDITOR", "AUTHOR_ARTIST") for c in credits):
            fail("Untrusted title, creator or source locator")
        if simon:
            if item.get("edition_format") != "EBOOK" or \
               item.get("source_kind") != "FIRST_PARTY_PUBLISHER_PRODUCT_METADATA" or \
               item.get("source_discovery_state") != "PUBLISHER_PAGE_READ_METADATA_ONLY" or \
               item.get("local_edition_identity_status") != "PUBLISHER_PRODUCT_ONLY_NO_PRIVATE_MATCH" or \
               item.get("publisher_copy_anomaly") not in (None, "AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED") or \
               not safe_text(item.get("publisher_series")) or not safe_text(item.get("edition_imprint")):
                fail("Simon & Schuster edition identity or publisher-copy scope was promoted")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item.get("edition_publication_date"))) or \
               not isinstance(item.get("edition_extent_pages"), int) or not 1 <= item["edition_extent_pages"] <= 5000:
                fail("Invalid publisher edition detail")
            form = "FICTION_PUBLISHER_EBOOK_METADATA"
            anomaly = item["publisher_copy_anomaly"]
            date = item["edition_publication_date"]
            extent = item["edition_extent_pages"]
        else:
            if item.get("edition_format") != "HARDBACK" or \
               item.get("work_form") != "NONFICTION_ILLUSTRATED_PRODUCTION_ART_BOOK" or \
               item.get("source_kind") != "FIRST_PARTY_TITAN_PUBLISHER_PRODUCT_METADATA" or \
               item.get("source_discovery_state") != "PUBLISHER_CATALOG_METADATA_ONLY" or \
               item.get("private_manifestation_binding") != "NOT_EVALUATED" or \
               not isinstance(item.get("edition_page_count_display"), int) or \
               not 1 <= item["edition_page_count_display"] <= 5000 or \
               any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item.get(k)))
                   for k in ("edition_published_us", "edition_published_uk")):
                fail("Titan edition identity or catalog metadata scope was promoted")
            form = "NONFICTION_ARTBOOK_PUBLISHER_METADATA"
            anomaly = None
            date = item["edition_published_us"]
            extent = item["edition_page_count_display"]
        rows.append({
            "row_id": f"draft-publisher-edition:{config['pr']}:{isbn}",
            "title": title, "creator_credits": credits, "edition_format": item["edition_format"],
            "source_local_form": form, "isbn13": isbn, "publisher_date_us": date,
            "publisher_extent_pages": extent, "source_url": url,
            "source_family": config["family"], "source_pr": config["pr"],
            "source_head": config["head"], "source_file": config["path"],
            "source_file_sha256": config["sha256"],
            "source_anomaly": anomaly, "identity_scope": "SOURCE_LOCAL_EDITION_UNRECONCILED",
            "full_text_status": "NOT_READ", "admission_effect": "NONE", "coverage_effect": "NONE",
            "publisher_claims_are_fictional_truth": False,
        })
    if seen != config["isbns"]:
        fail("Missing one of the pinned publisher editions")
    return rows


def build(raws: tuple[bytes, bytes], digests: tuple[str, str] | None = None,
          *, require_pinned: bool = True) -> dict:
    if len(raws) != 2 or any(not isinstance(raw, bytes) or len(raw) > 30_000 for raw in raws):
        fail("Expected exactly two small publisher metadata documents")
    if digests is None:
        digests = tuple(source["sha256"] for source in SOURCES)
    if len(digests) != 2:
        fail("Expected exactly two source digests")
    if require_pinned and any(hashlib.sha256(raw).hexdigest() != pinned or pinned != source["sha256"]
                              for raw, pinned, source in zip(raws, digests, SOURCES)):
        fail("Draft source digest mismatch: review the changed PR before preview")
    rows = []
    for raw, source in zip(raws, SOURCES):
        try:
            document = json.loads(raw)
        except (ValueError, UnicodeError):
            fail("Invalid UTF-8 JSON source")
        rows.extend(check_document(document, source))
    if len(rows) != 10 or len({row["isbn13"] for row in rows}) != 10:
        fail("Cross-family duplicate metadata rows")
    rows.sort(key=lambda row: (row["source_pr"], row["isbn13"]))
    return {
        "schema_version": "trek-held-draft-publisher-metadata-preview-v1",
        "status": "HELD_DRAFT_METADATA_PREVIEW_NOT_ACCEPTED",
        "source_family_count": 2, "row_count": 10,
        "source_pr_numbers": [494, 497],
        "public_explorer_effect": "NONE", "coverage_effect": "NONE",
        "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
        "accepted_evidence_effect": "NONE", "public_synopsis_effect": "NONE",
        "artwork_release_effect": "NONE", "main_commit_or_pages_release_effect": "NONE",
        "count_warning": "10 edition metadata rows, not ten accepted Works or complete book reads; separate from existing directory and publisher shelves",
        "rows": rows,
    }


def encode_preview(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def git_blob(repo: Path, source: dict) -> bytes:
    result = subprocess.run(["git", "show", f"{source['head']}:{source['path']}"], cwd=repo,
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT,
                        help="Local clone that has fetched both pinned draft PR heads")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write-preview", action="store_true",
                       help="Write only the scoped Consolidator review preview JSON (local proposal)")
    group.add_argument("--check-preview", action="store_true",
                       help="Check existing scoped preview bytes against pinned Git blobs")
    args = parser.parse_args()
    value = build(tuple(git_blob(args.repo, source) for source in SOURCES))
    encoded = encode_preview(value)
    if args.write_preview or args.check_preview:
        if PREVIEW_OUTPUT.is_symlink():
            parser.error("Untrusted preview output symlink")
        if args.write_preview:
            PREVIEW_OUTPUT.write_bytes(encoded)
            print(f"Wrote local HELD-only preview: {PREVIEW_OUTPUT.relative_to(ROOT)} ({value['row_count']} source-local editions)")
        elif not PREVIEW_OUTPUT.is_file() or PREVIEW_OUTPUT.read_bytes() != encoded:
            parser.error("Local preview differs from exact pinned draft source bytes")
        else:
            print("PASS: local HELD draft publisher preview matches two exact pinned Git source blobs")
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
