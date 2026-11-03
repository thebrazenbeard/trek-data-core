#!/usr/bin/env python3
"""Project accepted publisher-edition *leads* into a separate, callable index.

The 1,214-row Explorer directory is governed by older source/review receipts.
This overlay does not change that denominator, reclassify a candidate as a
Work, or release its unreviewed publisher-description paraphrases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
INPUT = "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json"
OUTPUT = "explorer/lit-publisher-edition-leads.json"
ACCEPTED_SOURCE_COMMIT = "7ec335d207047646a5fb38d7d22c9f537f639729"
ACCEPTED_SOURCE_SHA256 = "03173ed5ac94c7052a8c416bcca9cc762a8e7ca0ca3280eae0a4b3f902954dea"
EXPECTED = {
    "9780743419987": ("The Kobayashi Maru", "Julia Ecklar", "EBOOK"),
    "9780743546744": ("Shadows of the Sun", "Michael Jan Friedman", "ABRIDGED_AUDIO_DOWNLOAD"),
    "9780743546591": ("The Star Trek: The Next Generation: The Genesis Wave Book 3", "John Vornholt", "ADAPTED_AUDIO_DOWNLOAD"),
}
CLAIM_PREFIXES = frozenset(("series", "character", "topic", "setting", "plot", "vessel"))
TAG = re.compile(r"^[a-z]+:[a-z0-9][a-z0-9-]{2,100}$")


def encode(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def norm(value: str) -> str:
    return unicodedata.normalize("NFKD", value).casefold()


def safe_text(value: object, *, limit: int = 250) -> bool:
    return (isinstance(value, str) and 1 <= len(value) <= limit and value == value.strip()
            and not any(unicodedata.category(char) in ("Cc", "Cf", "Cs") or
                        ord(char) in (0xfffe, 0xffff) for char in value))


def valid_isbn(isbn: str) -> bool:
    return isinstance(isbn, str) and len(isbn) == 13 and isbn.isdigit() and \
        sum((1 if n % 2 == 0 else 3) * int(c) for n, c in enumerate(isbn)) % 10 == 0


def verify_source(source: object) -> list[dict]:
    """Check semantics independently of a source-byte digest (also fuzz-tested)."""
    if not isinstance(source, dict) or source.get("schema_version") != "trek-lit-archive-discovery-publisher-editions-v1" or \
       source.get("proposal_only") is not True or source.get("publisher_upstream_group") != "publisher:simonandschuster.com" or \
       source.get("independent_source_count") != 1 or source.get("publisher_product_pages_read") != 3 or \
       source.get("candidate_edition_count") != 3 or source.get("original_publisher_description_paraphrase_count") != 3 or \
       source.get("private_to_publisher_edition_match") != "UNVERIFIED" or \
       source.get("source_reader") != "RENDERED_FIRST_PARTY_ABOUT_THE_BOOK_AND_PRODUCT_DETAILS_NO_RAW_HTML_CUSTODY" or \
       source.get("publisher_html_sha256") is not None or source.get("image_or_ebook_bytes_retrieved") is not False or \
       any(source.get(effect) != "NONE" for effect in ("accepted_source_work_binding_effect", "accepted_work_effect", "accepted_evidence_effect", "coverage_effect", "public_synopsis_effect", "artwork_release_effect")) or \
       any(source.get(depth) is not False for depth in ("full_text_available", "structurally_indexed", "close_read", "semantically_analyzed")):
        raise ValueError("Publisher source is not exact unadmitted metadata-only scope")
    candidates = source.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != len(EXPECTED):
        raise ValueError("Publisher source candidate count drifted")
    rows = []
    seen = set()
    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("Invalid edition candidate type")
        isbn = item.get("publisher_isbn13")
        if not valid_isbn(isbn) or isbn not in EXPECTED or isbn in seen:
            raise ValueError("Edition ISBN invalid, unreviewed or duplicated")
        seen.add(isbn)
        title, creator, medium_format = EXPECTED[isbn]
        if (item.get("publisher_title"), item.get("creator"), item.get("publisher_edition_format")) != (title, creator, medium_format) or \
           item.get("fictional_truth_status") != "PUBLISHER_PROMOTIONAL_DESCRIPTION_ONLY" or \
           item.get("private_archive_edition_identity") != "UNVERIFIED":
            raise ValueError("Edition identity or source-truth status unexpectedly promoted")
        for key in ("publisher_series", "publisher_imprint", "publisher_publication_date", "publisher_extent"):
            if not safe_text(item.get(key), limit=180):
                raise ValueError(f"Invalid publisher metadata field: {key}")
        if not re.fullmatch(r"20\d\d-\d\d-\d\d|19\d\d-\d\d-\d\d", item["publisher_publication_date"]):
            raise ValueError("Invalid publisher edition date")
        url = item.get("publisher_url")
        parsed = urlsplit(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme != "https" or parsed.netloc != "www.simonandschuster.com" or \
           parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.path.startswith("/books/") or \
           parsed.path.rsplit("/", 1)[-1] != isbn or ".." in parsed.path:
            raise ValueError("Publisher ISBN locator escaped source scope")
        tags = item.get("source_relative_query_tags")
        if not isinstance(tags, list) or len(tags) != 5 or len(set(tags)) != 5 or \
           any(not isinstance(tag, str) or not TAG.fullmatch(tag) or
               tag.partition(":")[0] not in CLAIM_PREFIXES for tag in tags):
            raise ValueError("Unsafe or unsupported publisher-description query tags")
        # Explicitly label tags as claims *in the publisher's promotional copy*.
        # No semantic identity/canon tag is accepted by the callable index.
        public_tags = sorted("publisher-claim:" + tag for tag in tags)
        structural_tags = ["medium:literature", "kind:publisher-edition-lead", "format:" + medium_format.lower()]
        rows.append({
            "row_id": "publisher-edition:" + isbn,
            "title": title, "creator": creator, "publisher_series": item["publisher_series"],
            "edition_format": medium_format, "isbn13": isbn,
            "publisher_publication_date": item["publisher_publication_date"],
            "publisher_imprint": item["publisher_imprint"], "publisher_extent": item["publisher_extent"],
            "source_group": source["publisher_upstream_group"], "source_input": INPUT,
            "source_locator": url, "query_tags": sorted(structural_tags + public_tags),
            "search_text": norm(" ".join((title, creator, isbn, item["publisher_series"],
                                         medium_format.replace("_", " "), *tags))),
            "promotional_claim_scope": "PUBLISHER_COPY_TAGS_NOT_FICTIONAL_TRUTH",
            "synopsis_status": "UNREVIEWED_PARAPHRASE_HELD_NOT_PUBLIC",
            "private_edition_equivalence": "UNVERIFIED",
            "identity_scope": "EDITION_CANDIDATE_SOURCE_LOCAL", "coverage_effect": "NONE", "admission_effect": "NONE",
        })
    if set(EXPECTED) != seen:
        raise ValueError("Missing required publisher edition")
    return sorted(rows, key=lambda row: row["row_id"])


def build(root: Path = ROOT) -> dict:
    path = root / INPUT
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Untrusted accepted publisher source path")
    raw = path.read_bytes()
    if len(raw) > 40_000 or hashlib.sha256(raw).hexdigest() != ACCEPTED_SOURCE_SHA256:
        raise ValueError("Publisher source bytes no longer match accepted SHA-256")
    rows = verify_source(json.loads(raw))
    return {
        "schema_version": "1.0.0", "data_status": "PUBLISHER_EDITION_LEADS_SEARCH_OVERLAY_ONLY",
        "source_input": INPUT, "source_input_sha256": ACCEPTED_SOURCE_SHA256,
        "source_accepted_commit": ACCEPTED_SOURCE_COMMIT,
        "identity_scope": "SOURCE_LOCAL_EDITION_NOT_RECONCILED", "denominator_effect": "NONE",
        "coverage_effect": "NONE", "admission_effect": "NONE", "public_synopsis_effect": "NONE",
        "artwork_release_effect": "NONE", "row_count": len(rows), "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = encode(build())
    path = ROOT / OUTPUT
    if args.check:
        if not path.is_file() or path.is_symlink() or path.read_bytes() != value:
            parser.error("Publisher-edition index differs from pinned accepted source")
        print("PASS: 3 source-local publisher edition leads; no Explorer denominator or synopsis promotion")
    else:
        path.write_bytes(value)
        print(f"Wrote {path.relative_to(ROOT)}: 3 source-local publisher edition leads")


if __name__ == "__main__":
    main()
