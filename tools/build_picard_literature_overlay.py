#!/usr/bin/env python3
"""Project two accepted *proposal records* as a separate, unadmitted Picard shelf.

The historical 1,214-row discovery catalog is immutable because many accepted
research receipts pin its bytes. This supplement does not rewrite that catalog,
admit literary Works, claim source texts were read, or release book artwork.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "proposals/librarian/picard-companion-editions-20261103/records.json"
OUTPUT = "explorer/picard-literature-overlay.json"
SOURCE_SHA = "cdbda4dfa33c795bd51a1ebbfb09e41c7d838b73ce17aa6756428bd6ed8d8da4"
BASE_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
EXPECTED = {
    "9781982154073": ("Star Trek: Picard: The Dark Veil", "James Swallow", "2021-09-07", 336,
                      "Star-Trek-Picard-The-Dark-Veil/James-Swallow"),
    "9781982175207": ("Star Trek: Picard: Rogue Elements", "John Jackson Miller", "2022-06-07", 416,
                      "Star-Trek-Picard-Rogue-Elements/John-Jackson-Miller"),
}


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def exact_source(source: dict) -> list[dict]:
    """Check semantic custody in addition to the whole source-byte receipt."""
    if not isinstance(source, dict) or source.get("schema_version") != "1.0.0" or \
            source.get("proposal_only") is not True or source.get("source_group") != "publisher:simonandschuster.com" or \
            source.get("accepted_work_effect") != "NONE" or source.get("accepted_source_binding_effect") != "NONE" or \
            source.get("coverage_effect") != "NONE" or source.get("observed_on") != "2026-11-03":
        raise ValueError("Picard proposal scope or evidence status changed")
    sources, editions, bindings, works = (source.get(key) for key in
                                         ("sources", "edition_candidates", "bindings", "works"))
    if not all(isinstance(items, list) and len(items) == 3 for items in
               (sources, editions, bindings, works)):
        raise ValueError("Picard source/work/edition crosswalk is incomplete")
    seen = set()
    rows = []
    for item in sources:
        meta = item.get("provider_metadata") if isinstance(item, dict) else None
        isbn = meta.get("isbn13") if isinstance(meta, dict) else None
        if isbn not in (set(EXPECTED) | {"9781982194833"}) or isbn in seen:
            raise ValueError("Unexpected or duplicate Picard publisher ISBN")
        seen.add(isbn)
        if item.get("record_type") != "source" or item.get("status") != "PROPOSED" or \
                item.get("source_id") != f"proposed-picard-publisher-source-{isbn}" or \
                item.get("independence_group") != "publisher:simonandschuster.com" or \
                item.get("provenance_family") != "SIMON_SCHUSTER_PICARD_PRODUCT_PAGES" or \
                item.get("source_kind") != "PUBLISHER_EDITION_METADATA" or \
                item.get("content_hash") is not None or item.get("content_fingerprint") is not None or \
                item.get("retrieved_at") is not None or item.get("derived_from") != [] or \
                item.get("fixture_only") is not False or meta.get("format") != "TRADE_PAPERBACK":
            raise ValueError("Picard source claims unsupported custody or scope")
        candidates = [c for c in editions if c.get("isbn13") == isbn]
        bound = [b for b in bindings if b.get("source_id") == item["source_id"]]
        work = [w for w in works if w.get("work_id") == f"proposed-lit-picard-{('the-dark-veil' if isbn == '9781982154073' else 'rogue-elements' if isbn == '9781982175207' else 'second-self')}"]
        if len(candidates) != 1 or len(bound) != 1 or len(work) != 1 or \
                candidates[0].get("status") != "PROPOSED" or \
                candidates[0].get("verification") != "PUBLISHER_METADATA_ONLY" or \
                bound[0].get("lifecycle") != "PROPOSED" or bound[0].get("mapping_role") != "METADATA_ONLY" or \
                work[0].get("status") != "PROPOSED":
            raise ValueError("Picard crosswalk silently promoted or altered")
        if isbn not in EXPECTED:
            continue  # Second Self already exists in immutable directory.
        title, author, pub_date, extent, slug = EXPECTED[isbn]
        url = f"https://www.simonandschuster.com/books/{slug}/Star-Trek-Picard/{isbn}"
        parts = urlsplit(item.get("locator", ""))
        if (meta.get("title"), meta.get("creator"), meta.get("publication_date"), meta.get("length_pages")) != \
                (title, author, pub_date, extent) or item.get("locator") != url or \
                (parts.scheme, parts.netloc, parts.query, parts.fragment) != \
                ("https", "www.simonandschuster.com", "", "") or \
                bound[0].get("basis") != [{"kind": "PUBLISHER_PRODUCT_URL", "value": url}] or \
                bound[0].get("work_id") != work[0].get("work_id") or \
                candidates[0].get("work_id") != work[0].get("work_id") or \
                work[0].get("title") != title:
            raise ValueError("Picard publisher URL, title, work and edition identity mismatch")
        rows.append({
            "row_id": "literature:" + work[0]["work_id"], "medium": "LITERATURE",
            "candidate_kind": "NOVEL", "title": title,
            "context": f"{author} · one publisher trade-paperback edition candidate",
            "source_group": "publisher:simonandschuster.com", "source_input": SOURCE,
            "source_locator": url, "details": [f"Trade Paperback · ISBN {isbn}",
                                                f"Publisher: {extent} pages · {pub_date}"],
            "verification_status": "UNVERIFIED_METADATA", "identity_scope": "SOURCE_LOCAL",
            "coverage_effect": "NONE", "admission_effect": "NONE",
        })
    if seen != set(EXPECTED) | {"9781982194833"} or len(rows) != 2:
        raise ValueError("Picard source candidate set incomplete")
    return sorted(rows, key=lambda row: row["row_id"])


def build(root: Path = ROOT) -> dict:
    path = root / SOURCE
    base = root / "explorer/discovery-catalog.json"
    if (not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or
            not base.is_file() or base.is_symlink() or
            hashlib.sha256(base.read_bytes()).hexdigest() != BASE_SHA):
        raise ValueError("Picard source path or immutable base catalog invalid")
    raw = path.read_bytes()
    if len(raw) > 50_000 or hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Picard proposal source bytes changed")
    rows = exact_source(json.loads(raw))
    base_rows = json.loads(base.read_bytes())["rows"]
    if len(base_rows) != 1214 or any(row["row_id"] in {r["row_id"] for r in rows} for row in base_rows):
        raise ValueError("Picard overlay overlaps the historical directory")
    return {
        "schema_version": "1.0.0", "data_status": "PICARD_LITERATURE_SOURCE_LOCAL_SUPPLEMENT_ONLY",
        "source_input": SOURCE, "source_input_sha256": SOURCE_SHA,
        "base_directory_sha256": BASE_SHA, "base_directory_row_count": 1214,
        "row_count": len(rows), "rows": rows, "coverage_effect": "NONE",
        "admission_effect": "NONE", "artwork_release_effect": "NONE",
        "identity_scope": "SOURCE_LOCAL_NOT_RECONCILED", "full_text_read": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = ROOT / OUTPUT
    data = encode(build())
    if args.check:
        if not output.is_file() or output.is_symlink() or output.read_bytes() != data:
            parser.error("Picard supplement differs from exact accepted source projection")
        print("PASS: two unadmitted Picard ISBN records; historical directory byte-identical")
    else:
        output.write_bytes(data)
        print(f"Wrote {OUTPUT}: two source-local proposals")


if __name__ == "__main__":
    main()
