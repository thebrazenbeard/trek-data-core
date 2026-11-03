#!/usr/bin/env python3
"""Hash a locally held source and prepare/replay a proposal-only custody receipt.

This tool never fetches, publishes or copies the source; a receipt authenticates
the bytes read by this invocation, not their origin, legality or Work identity.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata
from urllib.parse import urlsplit


JSON_LIMIT = 64 * 1024
MAX_SOURCE_BYTES = 128 * 1024**3
CHUNK_SIZE = 4 * 1024 * 1024
ID = re.compile(r"[A-Za-z][A-Za-z0-9._-]{2,63}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
PRIVATE_LOCATOR = re.compile(r"private:[A-Za-z][A-Za-z0-9._-]{2,100}\Z")
FIELDS = {
    "record_type", "schema_version", "receipt_id", "source_candidate_id", "source_kind",
    "locator_kind", "source_locator", "source_version", "edition_identity",
    "provenance_family", "independence_group", "rights_basis_reported", "observed_on",
    "declared_sha256",
}
SOURCE_KINDS = {
    "AUDIOVISUAL_EPISODE", "FEATURE_FILM", "LITERARY_EDITION", "AUDIO_PRODUCTION",
    "TRANSCRIPT_REPRESENTATION", "SUBTITLE_REPRESENTATION", "OTHER_SOURCE_BYTES",
}
RIGHTS_BASES = {
    "OWNED_COPY", "RIGHTS_HOLDER_PERMISSION", "LICENSED_STREAMING",
    "PUBLIC_DOMAIN_CLAIM", "UNKNOWN",
}


class Rejected(ValueError):
    """Missing or unsafe custody evidence, not an accepted corpus record."""


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(_value: str) -> None:
    raise Rejected("non-JSON numeric constant")


def read_json(path: Path) -> dict:
    """Read bounded JSON without following a final symlink or hanging on a FIFO."""
    nofollow, nonblock = getattr(os, "O_NOFOLLOW", 0), getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not nonblock:
        raise Rejected("safe regular-file open is not supported on this host")
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise Rejected("symlinked JSON path refused")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow | nonblock)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > JSON_LIMIT:
                raise Rejected("JSON must be a bounded regular file")
            raw = stream.read(JSON_LIMIT + 1)
    except OSError:
        raise Rejected("cannot open JSON as a regular file") from None
    if len(raw) > JSON_LIMIT:
        raise Rejected("JSON request exceeds size limit")
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys,
                            parse_constant=reject_constant)
    except Rejected:
        raise
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError):
        raise Rejected("invalid UTF-8 JSON") from None
    if type(result) is not dict:
        raise Rejected("request/receipt must be a JSON object")
    return result


def text(value: object, label: str, *, length: int = 180) -> str:
    if type(value) is not str or not 1 <= len(value) <= length or value != value.strip():
        raise Rejected(f"{label} must be bounded, trimmed text")
    if any(unicodedata.category(ch) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for ch in value):
        raise Rejected(f"{label} contains control/format characters")
    if any(ch in value for ch in "<>"):
        raise Rejected(f"{label} must be plain text")
    return value


def ident(value: object, label: str) -> str:
    value = text(value, label, length=64)
    if not ID.fullmatch(value):
        raise Rejected(f"{label} must be a portable identifier")
    return value


def public_https(value: object) -> str:
    value = text(value, "source_locator", length=500)
    try:
        parts = urlsplit(value)
        host, port = parts.hostname, parts.port
    except ValueError:
        raise Rejected("invalid public HTTPS locator") from None
    if (parts.scheme != "https" or not host or "." not in host or parts.username or
            parts.password or parts.query or parts.fragment or port is not None or
            host.endswith((".local", ".internal", ".localhost")) or
            host.startswith("localhost") or not re.fullmatch(r"[A-Za-z0-9.-]+", host) or
            re.fullmatch(r"[0-9.]+", host) or "\\" in value):
        raise Rejected("public locator requires credential-free HTTPS without query or fragment")
    return value


def validate_request(item: dict) -> dict:
    if set(item) != FIELDS:
        raise Rejected("custody request requires exactly the declared fields")
    if item["record_type"] != "source_custody_request" or item["schema_version"] != "1.0.0":
        raise Rejected("unsupported custody request version/type")
    ident(item["receipt_id"], "receipt_id")
    ident(item["source_candidate_id"], "source_candidate_id")
    if type(item["source_kind"]) is not str or item["source_kind"] not in SOURCE_KINDS:
        raise Rejected("unsupported source_kind")
    if item["locator_kind"] == "PUBLIC_HTTPS":
        public_https(item["source_locator"])
    elif item["locator_kind"] == "PRIVATE_OPAQUE":
        if type(item["source_locator"]) is not str or not PRIVATE_LOCATOR.fullmatch(item["source_locator"]):
            raise Rejected("private locator must be an opaque ID, never a local path")
    else:
        raise Rejected("unsupported locator_kind")
    for key in ("source_version", "edition_identity", "provenance_family", "independence_group"):
        value = text(item[key], key)
        if "/" in value or "\\" in value:
            raise Rejected(f"{key} cannot include path separators or local file paths")
    if type(item["rights_basis_reported"]) is not str or item["rights_basis_reported"] not in RIGHTS_BASES:
        raise Rejected("invalid operator-reported rights basis")
    try:
        if type(item["observed_on"]) is not str or date.fromisoformat(item["observed_on"]).isoformat() != item["observed_on"]:
            raise Rejected("observed_on must be a real YYYY-MM-DD date")
    except (TypeError, ValueError):
        raise Rejected("observed_on must be a real YYYY-MM-DD date") from None
    digest = item["declared_sha256"]
    if digest is not None and (type(digest) is not str or not SHA.fullmatch(digest)):
        raise Rejected("declared_sha256 must be null or lowercase SHA-256")
    return item


def hash_regular_file(path: Path) -> tuple[str, int]:
    nofollow, nonblock = getattr(os, "O_NOFOLLOW", 0), getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not nonblock:
        raise Rejected("safe regular-file open is not supported on this host")
    # O_NOFOLLOW protects the final component; reject symlinked ancestors too.
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise Rejected("symlinked source path refused")
    try:
        fd = os.open(path, os.O_RDONLY | nofollow | nonblock)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_SOURCE_BYTES:
                raise Rejected("source must be a nonempty bounded regular file")
            hasher, count = hashlib.sha256(), 0
            while block := stream.read(CHUNK_SIZE):
                count += len(block)
                if count > MAX_SOURCE_BYTES:
                    raise Rejected("source exceeds maximum byte size")
                hasher.update(block)
            after = os.fstat(stream.fileno())
    except OSError:
        raise Rejected("unable to read source as a regular file") from None
    stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if count != before.st_size or any(getattr(before, key) != getattr(after, key) for key in stable):
        raise Rejected("source changed during hashing; re-capture a stable edition")
    return hasher.hexdigest(), count


def canonical(item: dict) -> bytes:
    return json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_receipt(item: dict, path: Path) -> dict:
    validate_request(item)
    digest, count = hash_regular_file(path)
    if item["declared_sha256"] is not None and digest != item["declared_sha256"]:
        raise Rejected("declared source digest disagrees with exact local bytes")
    receipt = {
        "record_type": "source_custody_receipt", "schema_version": "1.0.0",
        "receipt_id": item["receipt_id"],
        "source_candidate_id": item["source_candidate_id"],
        "source_kind": item["source_kind"],
        "locator_kind": item["locator_kind"], "source_locator": item["source_locator"],
        "source_version": item["source_version"], "edition_identity": item["edition_identity"],
        "provenance_family": item["provenance_family"],
        "independence_group": item["independence_group"],
        "rights_basis_reported": item["rights_basis_reported"],
        "rights_verification": "NOT_PERFORMED", "observed_on": item["observed_on"],
        "source_metadata_verification": "DECLARED_NOT_INDEPENDENTLY_VERIFIED",
        "hash_scope": "EXACT_LOCAL_FILE_BYTES", "content_sha256": digest,
        "size_bytes": count, "custody_state": "LOCAL_BYTES_HASHED_ONLY",
        "acceptance_effect": "NONE", "coverage_effect": "NONE",
        "work_identity_effect": "NONE", "source_work_binding_effect": "NONE",
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical(receipt)).hexdigest()
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "verify"))
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, help="Previously captured JSON receipt for exact replay")
    args = parser.parse_args(argv)
    try:
        if (args.mode == "verify") != (args.receipt is not None):
            raise Rejected("--receipt is required for verify and forbidden for capture")
        receipt = build_receipt(read_json(args.request), args.source_file)
        if args.mode == "verify":
            candidate = read_json(args.receipt)
            if candidate != receipt:
                raise Rejected("receipt does not match re-hashed bytes and declared source metadata")
            print(f"SOURCE_CUSTODY_RECEIPT_VERIFIED sha256:{receipt['receipt_sha256']}")
        else:
            print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    except Rejected as exc:
        print(f"SOURCE_CUSTODY_REJECTED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
