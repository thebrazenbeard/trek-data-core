#!/usr/bin/env python3
"""Private, source-local LIT-to-OPF converter-manifest candidate crosswalk.

Only the converter JSON/CSV metadata manifests and already-hashed private
member custody receipts are read. No LIT, OPF, book prose or cover content is
opened. The converter's JSON and CSV are two outputs of ONE upstream event,
not independent witnesses. No result admits a Source, Work, or coverage event.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import unicodedata
from zipfile import BadZipFile, ZipFile

from tools.inventory_converted_derivative_members import (
    CHUNK, MAX_RECEIPT_BYTES, CustodyError, canonical, open_private_output,
    read_private_json, stable_source,
)


VERSION = "1.0.0"
MANIFEST_MAX_BYTES = 2 * 1024 * 1024
MANIFEST_FIELDS = frozenset({"source_lit", "status", "opf_files"})


def key_name(value: str, extension: str) -> str:
    """Strict basename identity key, never a fuzzy title/Work judgment."""
    if (not isinstance(value, str) or not value.strip() or len(value) > 1024
            or "/" in value or "\\" in value
            or any(unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in value)):
        raise CustodyError("unsafe or non-basename converter manifest reference")
    clean = " ".join(unicodedata.normalize("NFKC", value).casefold().split())
    if not clean.endswith(extension) or clean in {extension, ".", ".."}:
        raise CustodyError("converter manifest reference has wrong extension")
    return clean


def optional_key_name(value: str, extension: str) -> str | None:
    """A missing converter target is unresolved, not an invented filename."""
    if value is None or value == "":
        return None
    return key_name(value, extension)


def receipt_name(row: dict, extension: str) -> str:
    if row.get("member_type") != extension:
        raise CustodyError("unexpected member type in private custody receipt")
    name = row.get("member_name_private")
    if not isinstance(name, str) or not name:
        raise CustodyError("private custody member has no valid name")
    return key_name(PurePosixPath(name).name, extension)


def validate_custody(receipt: dict, *, expected_type: str, archive_sha: str,
                     extension: str, expected_count: int) -> list[dict]:
    if (receipt.get("record_type") != expected_type
            or receipt.get("archive_sha256") != archive_sha
            or receipt.get("source_work_binding") != "UNRESOLVED"
            or receipt.get("coverage_effect") != "NONE"
            or receipt.get("work_admission_effect") != "NONE"
            or not isinstance(receipt.get("members"), list)
            or receipt.get("members_sha256") != hashlib.sha256(
                canonical(receipt["members"])).hexdigest()):
        raise CustodyError("private custody receipt identity/lineage mismatch")
    rows = [r for r in receipt["members"] if r.get("member_type") == extension]
    if (len(rows) != expected_count
            or receipt.get("counts_by_extension", {}).get(extension) != expected_count
            or len({r.get("member_id") for r in receipt["members"]}) != len(receipt["members"])):
        raise CustodyError("private custody member count or unique ID mismatch")
    for row in rows:
        receipt_name(row, extension)
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("member_sha256"))):
            raise CustodyError("invalid private custody member digest")
        if extension == ".opf" and (
            row.get("uncompressed_bytes", 0) <= 0
            or row.get("content_kind") != "DERIVATIVE_BYTES_HASHED_NO_COMPLETENESS_CLAIM"
        ):
            raise CustodyError("empty or non-byte OPF cannot enter candidate map")
    return rows


def unique_json(pairs):
    value = {}
    for key, member in pairs:
        if key in value:
            raise CustodyError("duplicate converter manifest JSON key")
        value[key] = member
    return value


def manifest_bytes(archive: ZipFile, receipt: dict, extension: str) -> bytes:
    entries = [x for x in receipt["members"] if x.get("member_type") == extension]
    if len(entries) != 1:
        raise CustodyError("converter manifest type must occur exactly once")
    entry = entries[0]
    if not 0 < entry.get("uncompressed_bytes", 0) <= MANIFEST_MAX_BYTES:
        raise CustodyError("converter manifest metadata exceeds size limit")
    try:
        with archive.open(entry["member_name_private"]) as stream:
            data = stream.read(MANIFEST_MAX_BYTES + 1)
    except (BadZipFile, RuntimeError, OSError):
        raise CustodyError("converter manifest metadata unreadable") from None
    if (len(data) != entry["uncompressed_bytes"]
            or hashlib.sha256(data).hexdigest() != entry["member_sha256"]):
        raise CustodyError("converter manifest metadata differs from custody hash")
    return data


def load_manifests(zip_path: Path, converted_receipt: dict):
    stream, before = stable_source(zip_path)
    with stream:
        whole = hashlib.sha256()
        while chunk := stream.read(CHUNK):
            whole.update(chunk)
        if whole.hexdigest() != converted_receipt["archive_sha256"]:
            raise CustodyError("converted archive drifted from private custody")
        stream.seek(0)
        try:
            with ZipFile(stream) as archive:
                json_data = manifest_bytes(archive, converted_receipt, ".json")
                csv_data = manifest_bytes(archive, converted_receipt, ".csv")
        except BadZipFile:
            raise CustodyError("converted archive ZIP is corrupt") from None
        after = os.fstat(stream.fileno())
        if any(getattr(before, name) != getattr(after, name) for name in (
            "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns"
        )):
            raise CustodyError("converted archive changed during manifest audit")
    try:
        obj = json.loads(json_data.decode("utf-8"), object_pairs_hook=unique_json)
        if not isinstance(obj, dict) or not isinstance(obj.get("books"), list):
            raise CustodyError("converter JSON books manifest absent")
        decoder = csv.DictReader(io.StringIO(csv_data.decode("utf-8-sig")))
        if (not decoder.fieldnames or len(decoder.fieldnames) != len(set(decoder.fieldnames))
                or not MANIFEST_FIELDS.issubset(decoder.fieldnames)):
            raise CustodyError("converter CSV schema missing required columns")
        csv_rows = list(decoder)
        if any(None in row or any(value is None for value in row.values()) for row in csv_rows):
            raise CustodyError("malformed converter CSV row")
    except (UnicodeError, ValueError, csv.Error, RecursionError):
        raise CustodyError("converter manifest metadata parse failed") from None
    return obj["books"], csv_rows


def build_crosswalk(original: dict, converted: dict, converted_zip: Path,
                    expected_original_sha: str, expected_converted_sha: str,
                    expected_lit: int, expected_opf: int,
                    expected_manifest_rows: int) -> dict:
    lit = validate_custody(original,
                           expected_type="PRIVATE_ORIGINAL_EBOOK_MEMBER_CUSTODY",
                           archive_sha=expected_original_sha,
                           extension=".lit", expected_count=expected_lit)
    opf = validate_custody(converted,
                           expected_type="PRIVATE_CONVERTED_DERIVATIVE_MEMBER_CUSTODY",
                           archive_sha=expected_converted_sha,
                           extension=".opf", expected_count=expected_opf)
    json_books, csv_rows = load_manifests(converted_zip, converted)
    if len(json_books) != expected_manifest_rows or len(csv_rows) != expected_manifest_rows:
        raise CustodyError("converter manifest record count differs from expected custody")

    by_lit = defaultdict(list)
    by_opf = defaultdict(list)
    for item in lit:
        by_lit[receipt_name(item, ".lit")].append(item)
    for item in opf:
        by_opf[receipt_name(item, ".opf")].append(item)

    by_json = defaultdict(list)
    by_csv = defaultdict(list)
    for index, row in enumerate(json_books):
        if (not isinstance(row, dict) or not isinstance(row.get("opf_files"), list)
                or not isinstance(row.get("status"), str)):
            raise CustodyError("invalid converter JSON book record")
        source = key_name(row.get("source"), ".lit")
        targets = [optional_key_name(x, ".opf") for x in row["opf_files"]]
        by_json[source].append((index, targets, row["status"]))
    for index, row in enumerate(csv_rows):
        source = key_name(row.get("source_lit"), ".lit")
        target = optional_key_name(row.get("opf_files"), ".opf")
        by_csv[source].append((index, target, row["status"]))

    links = []
    referenced_opf_ids = set()
    consistent_exports = 0
    stem_support = 0
    for source in sorted(lit, key=lambda row: row["member_id"]):
        source_key = receipt_name(source, ".lit")
        json_records = by_json[source_key]
        csv_records = by_csv[source_key]
        status = "UNMATCHED_NO_CONVERTER_RECORD"
        declared_keys = set()
        for _, names, _ in json_records:
            declared_keys.update(name for name in names if name is not None)
        for _, name, _ in csv_records:
            if name is not None:
                declared_keys.add(name)
        targets = sorted({item["member_id"] for key in declared_keys
                          for item in by_opf[key]})
        referenced_opf_ids.update(targets)
        converter_status = "UNKNOWN"
        evidence = []
        if len(by_lit[source_key]) != 1 or len(json_records) > 1 or len(csv_records) > 1:
            status = "AMBIGUOUS_SOURCE_OR_MANIFEST_MULTIPLICITY"
        elif json_records and csv_records:
            json_index, declared, j_status = json_records[0]
            csv_index, csv_declared, c_status = csv_records[0]
            converter_status = j_status
            evidence = ["EXPLICIT_CONVERTER_SOURCE_LIT_BASENAME",
                        "JSON_CSV_SAME_CONVERTER_LINEAGE"]
            if len(declared) > 1:
                status = "AMBIGUOUS_MULTIPLE_TARGET_CLAIMS"
            elif not declared or declared[0] is None:
                status = "UNRESOLVED_EMPTY_MANIFEST_TARGET"
            elif csv_declared is None or declared[0] != csv_declared or j_status != c_status:
                status = "CONTESTED_MANIFEST_EXPORTS"
            else:
                consistent_exports += 1
                matches = by_opf[declared[0]]
                if not targets:
                    status = "UNRESOLVED_DECLARED_OPF_ABSENT"
                elif len(targets) > 1:
                    status = "AMBIGUOUS_MULTIPLE_CONVERTED_OPF"
                else:
                    status = "CANDIDATE_EXPLICIT_CONVERTER_LINK"
                    evidence.append("EXACT_CONVERTER_OPF_BASENAME_TO_HASHED_MEMBER")
                    lit_stem = source_key[:-4]
                    opf_stem = declared[0][:-4]
                    if lit_stem == opf_stem:
                        stem_support += 1
                        evidence.append("SAME_STEM_REDUNDANT_FILENAME_SUPPORT")
        elif json_records or csv_records:
            status = "UNRESOLVED_SINGLE_MANIFEST_EXPORT"
        links.append({
            "original_lit_member_id": source["member_id"],
            "converted_opf_member_ids": targets,
            "link_status": status,
            "converter_reported_status": converter_status,
            "evidence_kinds": evidence,
            "semantic_work_identity": "NOT_ASSERTED",
            "content_completeness": "NOT_ESTABLISHED",
        })
    statuses = Counter(row["link_status"] for row in links)
    orphan_ids = sorted(x["member_id"] for x in opf if x["member_id"] not in referenced_opf_ids)
    candidates = statuses["CANDIDATE_EXPLICIT_CONVERTER_LINK"]
    ambiguous = sum(v for k, v in statuses.items() if k.startswith("AMBIGUOUS"))
    contested = statuses["CONTESTED_MANIFEST_EXPORTS"]
    unresolved = len(lit) - candidates - ambiguous - contested
    partial = sum(row["link_status"] == "CANDIDATE_EXPLICIT_CONVERTER_LINK"
                  and row["converter_reported_status"] == "partial_with_opf"
                  for row in links)
    return {
        "schema_version": VERSION,
        "record_type": "PRIVATE_SOURCE_LOCAL_LIT_OPF_CONVERTER_CANDIDATES",
        "original_archive_sha256": original["archive_sha256"],
        "converted_archive_sha256": converted["archive_sha256"],
        "original_member_list_sha256": original["members_sha256"],
        "converted_member_list_sha256": converted["members_sha256"],
        "original_lit_member_count": len(lit),
        "converted_opf_member_count": len(opf),
        "converter_json_book_records": len(json_books),
        "converter_csv_book_records": len(csv_rows),
        "manifest_json_csv_consistent_record_count": consistent_exports,
        "candidate_link_count": candidates,
        "candidate_filename_stem_support_count": stem_support,
        "ambiguous_original_count": ambiguous,
        "contested_original_count": contested,
        "unresolved_original_count": unresolved,
        "partial_candidate_count": partial,
        "orphan_converted_opf_count": len(orphan_ids),
        "orphan_converted_opf_member_ids": orphan_ids,
        "links_sha256": hashlib.sha256(canonical(links)).hexdigest(),
        "links": links,
        "converter_provenance_family": "SAME_CONVERSION_RUN_JSON_AND_CSV_NOT_INDEPENDENT",
        "matching_policy": "EXPLICIT_MANIFEST_SOURCE_AND_OUTPUT_BASENAME_NOT_ORDINAL",
        "source_work_binding": "UNRESOLVED",
        "edition_identity": "UNRESOLVED",
        "copyright_rights": "UNKNOWN",
        "content_completeness": "NOT_ESTABLISHED",
        "work_admission_effect": "NONE",
        "coverage_effect": "NONE",
        "privacy": "OWNER_PRIVATE_DO_NOT_PUBLISH",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "verify"))
    parser.add_argument("--original-receipt", type=Path, required=True)
    parser.add_argument("--converted-receipt", type=Path, required=True)
    parser.add_argument("--converted-zip", type=Path, required=True)
    parser.add_argument("--expect-original-sha256", required=True)
    parser.add_argument("--expect-converted-sha256", required=True)
    parser.add_argument("--expect-lit", type=int, required=True)
    parser.add_argument("--expect-opf", type=int, required=True)
    parser.add_argument("--expect-manifest-rows", type=int, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        if ((args.mode == "capture" and (args.out is None or args.receipt is not None))
                or (args.mode == "verify" and (args.receipt is None or args.out is not None))):
            raise CustodyError("capture requires --out, verify requires --receipt")
        if (not all(re.fullmatch("[0-9a-f]{64}", x) for x in (
            args.expect_original_sha256, args.expect_converted_sha256
        )) or any(x < 0 for x in (
            args.expect_lit, args.expect_opf, args.expect_manifest_rows
        ))):
            raise CustodyError("invalid explicit source identity/count expectations")
        original = read_private_json(args.original_receipt)
        converted = read_private_json(args.converted_receipt)
        result = build_crosswalk(original, converted, args.converted_zip,
                                 args.expect_original_sha256, args.expect_converted_sha256,
                                 args.expect_lit, args.expect_opf, args.expect_manifest_rows)
        if args.mode == "capture":
            payload = json.dumps(result, indent=2, ensure_ascii=False,
                                 allow_nan=False).encode("utf-8") + b"\n"
            if len(payload) > MAX_RECEIPT_BYTES:
                raise CustodyError("private candidate receipt exceeds bound")
            with open_private_output(args.out) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            label = "PRIVATE_MANIFEST_CROSSWALK_CAPTURED"
        else:
            if read_private_json(args.receipt) != result:
                raise CustodyError("private candidate receipt replay differs")
            label = "PRIVATE_MANIFEST_CROSSWALK_VERIFIED"
        print(f"{label}: {result['candidate_link_count']} explicit candidates; "
              f"{result['ambiguous_original_count']} ambiguous; "
              f"{result['contested_original_count']} contested; "
              f"{result['unresolved_original_count']} unresolved; "
              f"{result['orphan_converted_opf_count']} orphan OPF; no corpus effect")
        return 0
    except (CustodyError, OSError, KeyError, TypeError) as exc:
        message = str(exc) if isinstance(exc, CustodyError) else "private metadata invalid"
        print(f"PRIVATE_MANIFEST_CROSSWALK_REJECTED: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
