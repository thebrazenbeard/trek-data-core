#!/usr/bin/env python3
"""Validate a fixed aggregate-only public custody receipt without private files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ZERO_FIELDS = ("coverage_effect", "accepted_source_effect", "accepted_work_effect", "source_work_binding_effect")
TOP_KEYS = {
    "schema_version", "batch_id", "role", "record_class", "admission_status",
    "coverage_effect", "accepted_source_effect", "accepted_work_effect", "source_work_binding_effect",
    "rights_status", "private_file_inventory_released", "original_archive", "converted_archive",
    "private_inventory", "method", "summary", "open_gates",
}
EXPECTED = {
    "original_archive": ("ST ebooks.zip", 126481241, "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"),
    "converted_archive": ("Star_Trek_OPF_Converted.zip", 95673655, "0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f"),
}
EXPECTED_SUMMARY = {
    "opf_packages": 347,
    "parsed_metadata": 347,
    "matched_unique_original_lit_stems": 345,
    "review_holds": 15,
    "original_lit_file_entries": 347,
    "original_txt_file_entries": 220,
}
EXPECTED_GATES = {
    "REVIEW_15_LEGACY_DUBLIN_CORE_NAMESPACE_REPAIRS",
    "RESOLVE_UNMATCHED_OR_AMBIGUOUS_ORIGINAL_FILE_STEMS",
    "RECONCILE_EDITION_OMNIBUS_AND_CONVERSION_IDENTITIES",
    "VERIFY_RIGHTS_AND_SOURCE_ACCESS_PER_EDITION",
    "BIND_AUTHENTICATED_SOURCE_TO_WORK_BEFORE_CONTENT_RESEARCH",
}


def reject_if(condition: bool, message: str) -> None:
    if condition:
        raise ValueError(message)


def exact_keys(value: object, expected: set[str], name: str) -> None:
    reject_if(not isinstance(value, dict) or set(value) != expected, f"unexpected {name} fields")


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        reject_if(key in result, f"duplicate JSON key {key}")
        result[key] = value
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def validate(record: dict) -> None:
    exact_keys(record, TOP_KEYS, "receipt")
    for field, expected in (
        ("schema_version", "1.0.0"),
        ("batch_id", "private-opf-custody-receipt-20261103"),
        ("role", "LIBRARIAN"),
        ("record_class", "PRIVATE_ARCHIVE_AGGREGATE_INTAKE_RECEIPT"),
        ("admission_status", "NOT_ADMITTED"),
        ("rights_status", "USER_HELD_COPYRIGHT_AND_REPUBLICATION_RIGHTS_UNVERIFIED"),
        ("private_file_inventory_released", False),
    ):
        reject_if(record[field] != expected, f"invalid {field}")
    for field in ZERO_FIELDS:
        reject_if(record[field] != "NONE", f"forbidden {field} effect")
    for key, (label, size, digest) in EXPECTED.items():
        archive = record[key]
        exact_keys(archive, {"label", "byte_length", "sha256"}, key)
        reject_if(archive != {"label": label, "byte_length": size, "sha256": digest}, f"{key} receipt mismatch")
    private = record["private_inventory"]
    exact_keys(private, {"sha256", "byte_length", "owner_only_mode", "public_location"}, "private_inventory")
    reject_if(private != {
        "sha256": "125702e5e4832fb3211f9c839ba6889392539559b2aeb09b3487dd452d4d5951",
        "byte_length": 283361,
        "owner_only_mode": "0600",
        "public_location": None,
    }, "private inventory receipt mismatch")
    method = record["method"]
    exact_keys(method, {"accepted_main_sha", "script_path", "script_sha256", "runtime", "observed_date_utc", "read_scope"}, "method")
    reject_if(method != {
        "accepted_main_sha": "d4ecd970bf28019696abd692011007d7d47f9ff8",
        "script_path": "tools/inventory_opf_metadata.py",
        "script_sha256": "efaa3a1c80ae025dce48e8dca111acff145d8abfbf4127a8a9f1a1224483b703",
        "runtime": "WSL2 Ubuntu-26.04 Python 3.14.4",
        "observed_date_utc": "2026-11-03",
        "read_scope": "ZIP_CENTRAL_DIRECTORY_AND_BOUNDED_OPF_METADATA_ONLY",
    }, "unsupported intake method or source head")
    exact_keys(record["summary"], set(EXPECTED_SUMMARY), "summary")
    reject_if(record["summary"] != EXPECTED_SUMMARY, "aggregate source summary was modified")
    gates = record["open_gates"]
    reject_if(not isinstance(gates, list) or len(gates) != len(EXPECTED_GATES) or set(gates) != EXPECTED_GATES,
              "unresolved intake gates removed, duplicated or replaced")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "receipt.json")
    args = parser.parse_args()
    validate(load(args.input))
    print("PASS: public aggregate-only OPF receipt; zero corpus/artwork/coverage admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
