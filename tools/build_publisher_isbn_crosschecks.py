#!/usr/bin/env python3
"""Public, source-local S&S ISBN crosscheck projection: no OPF files or plot copy.

The five accepted librarian batches contain rendered product-page metadata,
not evidence of any owner-private ebook's identity, content, title/creator
equivalence, or unique canonical Work. No private source metadata is copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("explorer/publisher-isbn-crosschecks.json")
INPUTS = (
    ("OPF-FIRST-NINE", Path("proposals/librarian/opf-publisher-crosscheck-20261103/records.json"), 9),
    ("OPF-NEXT-TEN", Path("proposals/librarian/opf-publisher-crosscheck-next-ten-20261103/records.json"), 10),
    ("OPF-THIRD-TEN", Path("proposals/librarian/opf-publisher-crosscheck-third-ten-20261103/records.json"), 10),
    ("OPF-TNG-0076-0079", Path("proposals/librarian/tng-opf-0076-0079-publisher-crosswalk-20261103/records.json"), 4),
    ("OPF-FOURTH-SIX", Path("proposals/librarian/opf-publisher-crosscheck-fourth-six-20261103/records.json"), 6),
)
PRIVATE_SOURCE_OBSERVATION_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
STATES = {
    "PUBLISHER_ISBN_METADATA_MATCH_PRIVATE_EQUIVALENCE_UNVERIFIED": "ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL",
    "HELD_PUBLISHER_DIFFERENT_ISBN_FORMAT": "HELD_ISBN_FORMAT_DISCREPANCY",
    "PUBLISHER_ISBN_MATCH_CREATOR_RENDERING_CONFLICT_UNRESOLVED": "HELD_CREATOR_RENDERING_DISCREPANCY",
    "PUBLISHER_ISBN_MATCH_TITLE_SPELLING_CONFLICT_UNRESOLVED": "HELD_TITLE_SPELLING_DISCREPANCY",
}
EXPECTED_IDS = frozenset({9, 10, 15, 28, 29, 31, 34, 50, 51, *range(52, 66), 67, 68, 69,
                          70, 73, 74, 75, 76, 77, 78, 79, 82, 84, 85, 87, 88})
PIN_LABELS = {"OPF-FIRST-NINE": "REVIEWED_ROW_SHA256", "OPF-NEXT-TEN": "REVIEWED_ROW_SHA256",
              "OPF-THIRD-TEN": "REVIEWED_ROW_SHA256", "OPF-TNG-0076-0079": "REVIEWED_ROWS_SHA256",
              "OPF-FOURTH-SIX": "PIN"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs: list[tuple]) -> dict:
    found = {}
    for key, value in pairs:
        if key in found:
            raise ValueError("duplicate accepted JSON key")
        found[key] = value
    return found


def load(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 2_000_000:
        raise ValueError(f"accepted source path missing, symlinked, or oversized: {path}")
    raw = target.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("accepted source JSON must be an object")
    return value, raw


def isbn_valid(value: str) -> bool:
    return (isinstance(value, str) and bool(re.fullmatch(r"97[89][0-9]{10}", value))
            and sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(value)) % 10 == 0)


def publisher_product_url(url: str, isbn: str) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parts = urlsplit(url)
        return (parts.scheme == "https" and parts.netloc == "www.simonandschuster.com"
                and not parts.query and not parts.fragment
                and bool(re.fullmatch(r"/books/[A-Za-z0-9-]+/[A-Za-z0-9-]+/[A-Za-z0-9-]+/" + isbn, parts.path)))
    except ValueError:
        return False


def accepted_review_pins(batch: str, source_path: Path, count: int) -> dict:
    """Reuse the *code-owned*, per-row reviewed receipts, not JSON self-claims."""
    validator = ROOT / source_path.parent / "validate.py"
    if validator.is_symlink() or not validator.is_file() or validator.stat().st_size > 100_000:
        raise ValueError(f"missing/symlinked/oversized accepted validator: {source_path}")
    namespace = runpy.run_path(str(validator))
    pins = namespace.get(PIN_LABELS[batch])
    if (not isinstance(pins, dict) or len(pins) != count or
            any(not isinstance(k, str) or not isinstance(v, str) or
                re.fullmatch(r"[0-9a-f]{64}", v) is None for k, v in pins.items())):
        raise ValueError(f"unrecognized code-owned row-review pins: {batch}")
    return pins


def verify_all_accepted_source_validators() -> None:
    """Mandatory original source/custody/identity validators for all five inputs."""
    for batch, path, _ in INPUTS:
        validator = ROOT / path.parent / "validate.py"
        try:
            result = subprocess.run([sys.executable, str(validator)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError(f"accepted upstream validator unavailable: {batch}") from exc
        if result.returncode != 0:
            raise ValueError(f"accepted upstream source-review validator rejected {batch}: "
                             f"{(result.stderr or result.stdout).strip()[:250]}")


def build() -> dict:
    verify_all_accepted_source_validators()
    rows = []
    receipts = []
    opf_ids, isbns, source_urls = set(), set(), set()
    for batch, path, expected in INPUTS:
        data, raw = load(path)
        reviewed = accepted_review_pins(batch, path, expected)
        receipts.append({"path": path.as_posix(), "sha256": sha(raw)})
        source_rows = data.get("records")
        if not isinstance(source_rows, list) or len(source_rows) != expected:
            raise ValueError(f"accepted batch count drift: {batch}")
        if batch == "OPF-TNG-0076-0079":
            if (data.get("source_family") != "publisher:simonandschuster.com" or
                    data.get("source_read_class") != "FIRST_PARTY_RENDERED_PRODUCT_DETAILS" or
                    data.get("publisher_pages_read") != 4 or data.get("source_snapshots_available") is not False or
                    data.get("accepted_source_work_effect") != "NONE" or
                    data.get("literary_coverage_effect") != "NONE" or
                    data.get("private_ebook_custody_effect") != "NONE" or
                    data.get("public_text_image_effect") != "NONE" or
                    data.get("opf_input", {}).get("sha256") != PRIVATE_SOURCE_OBSERVATION_SHA256):
                raise ValueError("accepted TNG source-only boundary changed")
        else:
            if (data.get("source_observation_sha256") != PRIVATE_SOURCE_OBSERVATION_SHA256 or
                    data.get("publisher_source_family") != "publisher:simonandschuster.com:pocket-books-star-trek" or
                    data.get("publisher_source_mode") != "PUBLIC_RENDERED_PRODUCT_PAGE_NO_RAW_HTML_CUSTODY" or
                    data.get("private_ebook_text_read") is not False or
                    data.get("private_book_paths_exported") is not False or
                    data.get("publisher_cover_bytes_exported") is not False or
                    data.get("private_source_equivalence_verified") is not False or
                    data.get("global_work_admission") != "NONE" or
                    data.get("coverage_effect") != "NONE"):
                raise ValueError("accepted publisher crosscheck custody/admission drift")
        for original in source_rows:
            source_id = original["opf_id"] if batch == "OPF-TNG-0076-0079" else original["opf_source_local_id"]
            pinned_id = original["id"] if batch == "OPF-TNG-0076-0079" else source_id
            source_row_digest = sha(json.dumps(original, sort_keys=True, separators=(",", ":"),
                                               ensure_ascii=False).encode("utf-8"))
            if reviewed.get(pinned_id) != source_row_digest:
                raise ValueError(f"unreviewed publisher row/status/ISBN binding: {batch}:{pinned_id}")
            match = re.fullmatch(r"opf-local:(\d{4})", source_id)
            if match is None or source_id in opf_ids:
                raise ValueError("duplicate or invalid source-local ID")
            isbn = original["publisher_isbn13"]
            url = original["publisher_product_url"] if batch == "OPF-TNG-0076-0079" else original["publisher_locator"]
            title = original["publisher_title"]
            authors = ([original["publisher_creator"]] if batch == "OPF-TNG-0076-0079"
                       else original["publisher_authors"])
            if (not isbn_valid(isbn) or not publisher_product_url(url, isbn) or
                    isbn in isbns or url in source_urls or
                    not isinstance(title, str) or not 1 <= len(title) <= 180 or
                    not isinstance(authors, list) or not 1 <= len(authors) <= 8 or
                    any(not isinstance(a, str) or not 1 <= len(a) <= 110 for a in authors)):
                raise ValueError("invalid, duplicate or non-publisher ISBN metadata")
            if batch == "OPF-TNG-0076-0079":
                if (original.get("isbn_relation") != "MATCHING_CHECKSUM_CONVERTED_IDENTIFIER_ONLY" or
                        original.get("date_relation") != "CONFLICT_UNRESOLVED" or
                        original.get("private_edition_verified") is not False or
                        original.get("rights_status") != "METADATA_ONLY_NO_PUBLIC_TEXT_IMAGE_RIGHTS"):
                    raise ValueError("TNG discrepancy/private-equivalence drift")
                state = "HELD_PUBLISHER_DATE_DISCREPANCY"
            else:
                state = STATES.get(original.get("crosscheck_state"))
                if state is None:
                    raise ValueError("unknown source-local crosscheck status")
                if original.get("publisher_format") != "eBook":
                    raise ValueError("unapproved publisher format")
            opf_ids.add(source_id)
            isbns.add(isbn)
            source_urls.add(url)
            rows.append({
                "row_id": "publisher-isbn-crosscheck:" + source_id.rsplit(":", 1)[-1],
                "source_local_ref": source_id,
                "publisher_title": title,
                "publisher_creators": authors,
                "publisher_isbn13": isbn,
                "publisher_format": "EBOOK",
                "publisher_url": url,
                "publisher_lineage": "publisher:simonandschuster.com",
                "crosscheck_state": state,
                "source_batch": batch,
                "public_source_record": path.as_posix(),
                "public_source_record_sha256": sha(raw),
                "private_edition_equivalence": "UNVERIFIED",
                "work_identity": "NOT_RECONCILED",
                "public_synopsis_effect": "NONE",
                "artwork_effect": "NONE",
                "admission_effect": "NONE",
                "coverage_effect": "NONE",
            })
    expected_labels = {f"opf-local:{i:04d}" for i in EXPECTED_IDS}
    if opf_ids != expected_labels or len(rows) != 39 or len(isbns) != 39:
        raise ValueError("accepted five-batch 39-record ISBN scope changed")
    rows.sort(key=lambda row: row["source_local_ref"])
    agreement = sum(r["crosscheck_state"] == "ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL" for r in rows)
    if agreement != 30:
        raise ValueError("accepted ISBN discrepancy breakdown changed")
    return {
        "schema_version": "1.0.0",
        "data_status": "PUBLIC_PUBLISHER_ISBN_SOURCE_LOCAL_CROSSCHECKS_ONLY",
        "row_count": 39,
        "publisher_isbn_identifier_agreements": 30,
        "held_discrepancy_count": 9,
        "existing_publisher_edition_leads_count_unchanged": 3,
        "existing_directory_rows_count_unchanged": 1214,
        "private_ebooks_authenticated": 0,
        "canonical_works_admitted": 0,
        "synopses_published": 0,
        "artwork_published": 0,
        "publisher_independence_group_count": 1,
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "accepted_public_input_receipts": receipts,
        "rows": rows,
    }


def encode(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = encode(build())
    target = ROOT / OUT
    if target.is_symlink():
        raise SystemExit("PUBLISHER_ISBN_CROSSCHECK_OUTPUT_SYMLINK_REFUSED")
    if args.check:
        if not target.is_file() or target.read_bytes() != result:
            raise SystemExit("PUBLISHER_ISBN_CROSSCHECK_STALE_OR_TAMPERED")
    else:
        target.write_bytes(result)
    print("PUBLISHER_ISBN_CROSSCHECK_OK: 39 source-local ISBN records; "
          "30 publisher identifier agreements, 9 held discrepancies; zero admissions")


if __name__ == "__main__":
    main()
