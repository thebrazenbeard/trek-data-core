#!/usr/bin/env python3
"""Create a private, byte-grounded custody ledger for original LIT/TXT ZIP members.

Reads each member as opaque bytes, never interprets its prose, and never extracts
files. All member-level receipts and source-local conversion hints stay in a new
owner-only JSON outside this repository. This is *not* Source/Work admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import unicodedata
import zlib
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED, ZIP_STORED

from inventory_opf_metadata import (
    IntakeError, build_inventory as build_opf_inventory,
    open_private_output_parent, private_output_path,
)


MAX_ARCHIVE_BYTES = 4 * 1024**3
MAX_MEMBERS = 10000
MAX_MEMBER_BYTES = 512 * 1024**2
MAX_TOTAL_BYTES = 4 * 1024**3
MAX_RATIO = 1000
CHUNK = 1024 * 1024
STABLE_FIELDS = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")


def _digest_stream(stream) -> str:
    h = hashlib.sha256()
    while chunk := stream.read(CHUNK):
        h.update(chunk)
    return h.hexdigest()


def _stable(before, after) -> bool:
    return all(getattr(before, field) == getattr(after, field) for field in STABLE_FIELDS)


def _open_pinned_regular_input(path: Path) -> int:
    """Pin every ancestor directory and the leaf without following links."""
    path = Path(os.path.abspath(path))
    parent_fd = open_private_output_parent(path)
    try:
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return os.open(path.name, flags, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)


def _member_name(name: str) -> str:
    """Validate without logging the private name; return collision key."""
    if (not name or len(name) > 512 or name.startswith("/") or "\\" in name or
            "\x00" in name or "//" in name or name.startswith("./")):
        raise IntakeError("archive contains an unsafe ZIP path")
    parts = name.rstrip("/").split("/")
    if (not parts or len(parts) > 16 or any(part in ("", ".", "..") or ":" in part
            for part in parts) or any(unicodedata.category(ch) in ("Cc", "Cf", "Cs")
                                      for ch in name)):
        raise IntakeError("archive contains an unsafe ZIP path")
    return unicodedata.normalize("NFKC", name.rstrip("/")).casefold()


def _stem(name: str) -> str:
    return unicodedata.normalize("NFKC", PurePosixPath(name).stem).casefold().strip()


def _source_member_index(archive: ZipFile) -> list:
    entries = archive.infolist()
    if len(entries) > MAX_MEMBERS:
        raise IntakeError("archive has too many ZIP members")
    seen = set()
    total = 0
    for member in entries:
        key = _member_name(member.filename)
        if key in seen:
            raise IntakeError("duplicate or normalization-colliding ZIP paths")
        seen.add(key)
        file_type = stat.S_IFMT(member.external_attr >> 16)
        if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise IntakeError("non-regular ZIP member refused")
        if bool(member.is_dir()) != (file_type == stat.S_IFDIR) and file_type:
            raise IntakeError("ZIP directory/type disagreement")
        if member.flag_bits & 0x41:
            raise IntakeError("encrypted ZIP member refused")
        if member.compress_type not in (ZIP_STORED, ZIP_DEFLATED):
            raise IntakeError("unsupported ZIP compression")
        if member.is_dir():
            if member.file_size:
                raise IntakeError("nonempty ZIP directory refused")
            continue
        if PurePosixPath(member.filename).suffix.casefold() not in (".lit", ".txt"):
            raise IntakeError("unexpected non-LIT/TXT member in original ZIP")
        if member.file_size > MAX_MEMBER_BYTES:
            raise IntakeError("ZIP member exceeds per-file byte limit")
        if member.file_size and (not member.compress_size or
                                 member.file_size > member.compress_size * MAX_RATIO):
            raise IntakeError("ZIP member exceeds compression ratio limit")
        total += member.file_size
        if total > MAX_TOTAL_BYTES:
            raise IntakeError("ZIP uncompressed bytes exceed aggregate limit")
    return sorted((entry for entry in entries if not entry.is_dir()),
                  key=lambda entry: _member_name(entry.filename))


def _member_receipts(archive: ZipFile, entries: list) -> tuple[list[dict], dict]:
    records = []
    stems: dict[str, list[dict]] = {}
    for ordinal, info in enumerate(entries, 1):
        digest = hashlib.sha256()
        crc, size = 0, 0
        try:
            with archive.open(info, "r") as stream:
                while chunk := stream.read(CHUNK):
                    size += len(chunk)
                    if size > MAX_MEMBER_BYTES or size > info.file_size:
                        raise IntakeError("ZIP member decompressed beyond stated limits")
                    digest.update(chunk)
                    crc = zlib.crc32(chunk, crc)
        except (EOFError, RuntimeError, BadZipFile, zlib.error) as exc:
            raise IntakeError("ZIP member decompression or CRC verification failed") from exc
        if size != info.file_size or (crc & 0xffffffff) != info.CRC:
            raise IntakeError("ZIP member byte count or CRC mismatch")
        suffix = PurePosixPath(info.filename).suffix.casefold()
        receipt = {
            "member_id": f"member:{ordinal:05d}",
            "member_name_sha256": hashlib.sha256(info.filename.encode("utf-8")).hexdigest(),
            "media_hint": suffix.lstrip(".").upper(),
            "byte_sha256": digest.hexdigest(),
            "uncompressed_bytes": size,
            "compressed_bytes": info.compress_size,
            "crc32": f"{crc & 0xffffffff:08x}",
            "canonical_source_id": None,
            "canonical_work_id": None,
        }
        records.append(receipt)
        stems.setdefault(_stem(info.filename), []).append(receipt)
    return records, stems


def _crosswalk(stems: dict, opf_zip: Path, original_zip: Path, original_digest: str) -> dict:
    """Only source-local filename-stem hints, never verified edition identity."""
    opf = build_opf_inventory(opf_zip, original_zip)
    if opf["input_receipts"]["original_archive_sha256"] != original_digest:
        raise IntakeError("OPF crosswalk original source receipt mismatch")
    links = []
    for ordinal, candidate in enumerate(opf["candidates"], 1):
        key = _stem(PurePosixPath(candidate["archive_member"]).parent.name)
        matches = stems.get(key, [])
        lit = [record for record in matches if record["media_hint"] == "LIT"]
        txt = [record for record in matches if record["media_hint"] == "TXT"]
        links.append({
            "opf_ordinal": ordinal,
            "lit_member_id": lit[0]["member_id"] if len(lit) == 1 else None,
            "txt_member_id": txt[0]["member_id"] if len(txt) == 1 else None,
            "status": ("UNIQUE_STEM_CANDIDATE_UNVERIFIED" if len(lit) == 1
                       else "AMBIGUOUS_STEM" if len(lit) > 1 else "NO_LIT_STEM_MATCH"),
            "work_identity_effect": "NONE",
        })
    return {"opf_archive_sha256": opf["input_receipts"]["opf_archive_sha256"],
            "opf_count": len(links), "links": links}


def inventory(original_zip: Path, *, expected_sha256: str | None = None,
              opf_zip: Path | None = None) -> dict:
    """Open a pinned regular file; hash container before/after member reads."""
    if expected_sha256 is not None and (len(expected_sha256) != 64 or
            any(ch not in "0123456789abcdef" for ch in expected_sha256)):
        raise IntakeError("expected SHA-256 must be lowercase hex")
    nofollow, nonblock = getattr(os, "O_NOFOLLOW", 0), getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not nonblock:
        raise IntakeError("safe input file open unavailable")
    try:
        fd = _open_pinned_regular_input(original_zip)
    except (OSError, IntakeError) as exc:
        raise IntakeError("original ZIP path is not a secure regular input") from exc
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or
                not 0 < before.st_size <= MAX_ARCHIVE_BYTES):
            raise IntakeError("original ZIP must be a bounded regular file")
        container_digest = _digest_stream(stream)
        if expected_sha256 and container_digest != expected_sha256:
            raise IntakeError("original ZIP differs from expected custody receipt")
        stream.seek(0)
        with ZipFile(stream) as archive:
            members = _source_member_index(archive)
            receipts, stems = _member_receipts(archive, members)
        middle = os.fstat(fd)
        if not _stable(before, middle):
            raise IntakeError("original ZIP changed during member inventory")
        stream.seek(0)
        replay_digest = _digest_stream(stream)
        after = os.fstat(fd)
        if not _stable(before, after) or container_digest != replay_digest:
            raise IntakeError("original ZIP changed during custody replay")
    counts = {kind: sum(row["media_hint"] == kind for row in receipts)
              for kind in ("LIT", "TXT")}
    result = {
        "schema_version": "0.1.0",
        "record_type": "private_ebook_member_custody_inventory",
        "proposal_only": True,
        "container_sha256": container_digest,
        "container_bytes": before.st_size,
        "rights_status": "USER_SUPPLIED_RIGHTS_NOT_VERIFIED",
        "work_identity_effect": "NONE",
        "source_admission_effect": "NONE",
        "source_work_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "summary": {"original_members_hashed": len(receipts),
                    "lit_members": counts["LIT"], "txt_members": counts["TXT"]},
        "member_receipts": receipts,
    }
    if opf_zip is not None:
        result["conversion_stem_crosswalk"] = _crosswalk(
            stems, opf_zip, original_zip, container_digest,
        )
    return result


def write_private(out: Path, result: dict) -> None:
    path = private_output_path(out)
    parent_fd = open_private_output_parent(path)
    try:
        pinned = os.fstat(parent_fd)
        current = os.stat(path.parent, follow_symlinks=False)
        if (pinned.st_dev, pinned.st_ino) != (current.st_dev, current.st_ino):
            raise IntakeError("private output parent changed during inventory")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        fd = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
    finally:
        os.close(parent_fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-zip", required=True, type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--opf-zip", type=Path,
                        help="optional converted ZIP for source-local OPF stem hints")
    parser.add_argument("--out", required=True, type=Path,
                        help="new private JSON outside repository; never publicly commit")
    args = parser.parse_args(argv)
    try:
        # Check destination before incurring a potentially expensive full-file scan.
        private_output_path(args.out)
        result = inventory(args.original_zip, expected_sha256=args.expected_sha256,
                           opf_zip=args.opf_zip)
        write_private(args.out, result)
    except (IntakeError, BadZipFile, OSError, ValueError, NotImplementedError) as exc:
        # Do not expose user-provided paths or ZIP member names in error output.
        print(f"PRIVATE_MEMBER_INTAKE_REFUSED: {type(exc).__name__}", file=sys.stderr)
        return 1
    summary = result["summary"]
    print("PRIVATE_MEMBER_INTAKE_OK "
          f"members={summary['original_members_hashed']} "
          f"lit={summary['lit_members']} txt={summary['txt_members']} "
          "source/work/coverage_effect=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
