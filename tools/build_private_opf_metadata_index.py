#!/usr/bin/env python3
"""Project owner-local OPF XML metadata claims into a held, source-local search index.

This compiler NEVER reads ebook text or ZIP member paths and cannot bind Work identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("proposals/librarian/private-opf-metadata-20261103/observations.json")
INDEX = Path("proposals/librarian/private-opf-metadata-20261103/search-index.json")
RAW_OBSERVATION_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
OPF_CONTAINER_SHA256 = "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"
EBOOK_CONTAINER_SHA256 = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
OPF_ENTRY_DIGEST_MULTISET_SHA256 = "532db2000ea03e2aabd713f31557552ce57c6eefe0b2eb18f8e1643c3127c0b4"
NAMESPACE_RECOVERED = {50, 51, 52, 53, 54, 140, 141, 142, 143, 144, 282, 283, 284, 285, 286}
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "observation_date_utc", "source_kind",
    "source_container", "related_unread_text_container", "private_member_paths_exported",
    "private_identifier_guids_exported", "copyrighted_text_or_images_exported",
    "opf_xml_metadata_elements_read", "ebook_full_text_read", "edition_binding_verified",
    "public_synopsis_approved", "work_admission_effect", "coverage_effect", "rows",
}
ROW_KEYS = {"source_local_id", "opf_entry_sha256", "parse_status", "title", "creator", "publisher", "date", "language", "isbn_checksum_valid"}
PRIVATE_PATTERN = re.compile(
    r"(?:^/|[A-Za-z]:[/\\]|[A-Za-z]%3a(?:%5c|%2f)|/mnt/|\\\\|OverDriveGUID|/Users/|/home/|file://|"
    r"\{?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\}?|"
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\\[^\\\s]+\\[^\\\s]+)",
    re.IGNORECASE,
)
UNSAFE_UNICODE = re.compile(r"[\x00-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def exact_read(path):
    target = ROOT / path
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 2_000_000:
        raise ValueError("source missing, symlinked or oversized")
    raw = target.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys), raw


def valid_isbn(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{9}[0-9X]|[0-9]{13}", value):
        return False
    if len(value) == 10:
        return (sum((10 - i) * int(v) for i, v in enumerate(value[:9])) + (10 if value[-1] == "X" else int(value[-1]))) % 11 == 0
    return (sum((1 if i % 2 == 0 else 3) * int(v) for i, v in enumerate(value[:12])) + int(value[-1])) % 10 == 0


def search_key(text):
    folded = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"[^\w]+", " ", folded, flags=re.UNICODE).strip()


def ensure_values(values, name, limit):
    if not isinstance(values, list) or len(values) > limit or len(set(values)) != len(values):
        raise ValueError(f"bad {name} list")
    for value in values:
        if (not isinstance(value, str) or not value.strip() or len(value) > 180
                or PRIVATE_PATTERN.search(value) or UNSAFE_UNICODE.search(value)):
            raise ValueError(f"unbounded/private {name} value")


def compile_index(source, raw):
    if hashlib.sha256(raw).hexdigest() != RAW_OBSERVATION_SHA256:
        raise ValueError("source observations changed without review")
    if json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys) != source:
        raise ValueError("in-memory source differs from pinned source bytes")
    if not isinstance(source, dict) or set(source) != TOP_KEYS:
        raise ValueError("unreviewed envelope")
    expected = {
        "schema_version": "1.0.0", "proposal_id": "LIBRARIAN-PRIVATE-OPF-METADATA-20261103",
        "baseline_accepted_main": "4e75c2ba45a9ce8d1537497052007cd215ab0bef",
        "observation_date_utc": "2026-11-03", "source_kind": "OWNER_PRIVATE_OPF_XML_METADATA",
        "private_member_paths_exported": False, "private_identifier_guids_exported": False,
        "copyrighted_text_or_images_exported": False, "opf_xml_metadata_elements_read": True,
        "ebook_full_text_read": False, "edition_binding_verified": False,
        "public_synopsis_approved": False, "work_admission_effect": "NONE", "coverage_effect": "NONE",
    }
    for field, value in expected.items():
        if source[field] != value:
            raise ValueError(f"protected OPF envelope mismatch: {field}")
    if source["source_container"] != {
        "opaque_id": "OWNER_PRIVATE_ST_OPF_ARCHIVE_A", "sha256": OPF_CONTAINER_SHA256,
        "bytes": 95673655, "zip_members": 3846, "opf_members": 347, "image_members_unread": 1910,
    } or source["related_unread_text_container"] != {
        "opaque_id": "OWNER_PRIVATE_ST_EBOOK_ARCHIVE_B", "sha256": EBOOK_CONTAINER_SHA256,
        "bytes": 126481241, "zip_members": 573, "lit_members_unread": 347, "txt_members_unread": 220,
    }:
        raise ValueError("opaque source container lineage changed")
    if not isinstance(source["rows"], list) or len(source["rows"]) != 347:
        raise ValueError("incomplete private OPF metadata batch")
    if hashlib.sha256("".join(sorted(row.get("opf_entry_sha256", "") for row in source["rows"] if isinstance(row, dict))).encode()).hexdigest() != OPF_ENTRY_DIGEST_MULTISET_SHA256:
        raise ValueError("OPF source entry fingerprint multiset changed")
    output = []
    for number, row in enumerate(source["rows"], 1):
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise ValueError("malformed OPF metadata observation")
        if (row["source_local_id"] != f"opf-local:{number:04d}"
                or not isinstance(row["opf_entry_sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", row["opf_entry_sha256"])):
            raise ValueError("source-local ID or immutable OPF fingerprint drift")
        expected_status = "OPF_XML_NAMESPACE_RECOVERED" if number in NAMESPACE_RECOVERED else "PARSED"
        if row["parse_status"] != expected_status:
            raise ValueError("malformed XML recovery state changed")
        for field, bound in (("title", 3), ("creator", 4), ("publisher", 4), ("date", 4), ("language", 4)):
            ensure_values(row[field], field, bound)
        if len(row["title"]) < 1:
            raise ValueError("OPF record without observed title")
        ensure_values(row["isbn_checksum_valid"], "isbn_checksum_valid", 3)
        if any(not valid_isbn(v) for v in row["isbn_checksum_valid"]):
            raise ValueError("invalid ISBN presented as checksum-valid")
        output.append({
            "source_local_id": row["source_local_id"],
            "entry_fingerprint_sha256": row["opf_entry_sha256"],
            "metadata_parse_status": row["parse_status"],
            "title_search_keys": sorted({search_key(v) for v in row["title"]}),
            "creator_search_keys": sorted({search_key(v) for v in row["creator"]}),
            "isbn_search_keys": sorted(row["isbn_checksum_valid"]),
            "edition_binding": "NOT_VERIFIED",
            "source_identity_scope": "ONE_OWNER_PRIVATE_OPF_XML_ENTRY",
            "work_identity": "NOT_RECONCILED",
        })
    return {
        "data_status": "OWNER_PRIVATE_SOURCE_METADATA_DISCOVERY_ONLY",
        "source_container_opaque_id": "OWNER_PRIVATE_ST_OPF_ARCHIVE_A",
        "source_container_sha256": OPF_CONTAINER_SHA256,
        "observations_sha256": hashlib.sha256(raw).hexdigest(),
        "row_count": len(output),
        "normal_xml_parse": 332,
        "in_memory_namespace_recovered": 15,
        "isbn_checksum_valid_candidate_rows": sum(bool(v["isbn_search_keys"]) for v in output),
        "edition_bindings_verified": 0,
        "full_text_sources_read": 0,
        "work_admission_effect": "NONE", "coverage_effect": "NONE",
        "records": output,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source, raw = exact_read(SOURCE)
    result = compile_index(source, raw)
    encoded = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    target = ROOT / INDEX
    if args.check:
        if target.is_symlink() or not target.is_file() or target.read_bytes() != encoded:
            raise SystemExit("OPF_METADATA_INDEX_STALE_OR_UNREVIEWED")
    else:
        if target.is_symlink():
            raise SystemExit("OPF_METADATA_INDEX_SYMLINK_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("OPF_METADATA_INDEX_OK: 347 source-local records, 332 strict XML, 15 in-memory namespace recovery; zero Work admission")


if __name__ == "__main__":
    main()
