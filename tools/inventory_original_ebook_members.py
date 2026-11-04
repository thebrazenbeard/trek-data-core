#!/usr/bin/env python3
"""Create a private, replayable byte inventory of an original ebook ZIP.

No book text is parsed, displayed, or exported to Git. The private JSON contains
member paths for owner-side linkage; it MUST NOT be committed or served. Hashing
does not establish a licensed edition, a Work, a Source binding, or coverage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
from zipfile import BadZipFile, ZIP_DEFLATED, ZIP_STORED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
MAX_ARCHIVE_BYTES = 1024 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
MAX_RECEIPT_BYTES = 2 * 1024 * 1024
CHUNK = 1024 * 1024
DRIVE = re.compile(r"^[A-Za-z]:")


class CustodyError(ValueError):
    """The source or private receipt violates the custody contract."""


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def safe_name(name: str, seen: set[str]) -> None:
    """Reject paths that are dangerous or ambiguous on Windows and POSIX."""
    normalized = unicodedata.normalize("NFKC", name)
    parts = name.split("/")
    if (not name or name.startswith("/") or DRIVE.match(name) or "\\" in name
            or any(part in {"", ".", ".."} for part in parts[:-1])
            or (parts[-1] in {"", ".", ".."} and not name.endswith("/"))
            or any(unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in name)):
        raise CustodyError("unsafe ZIP member name")
    if (DRIVE.match(normalized) or normalized.startswith("/")
            or normalized.split("/") != name.split("/")
            or any(part in {"", ".", ".."} for part in normalized.split("/")[:-1])
            or "\\" in normalized):
        raise CustodyError("ambiguous Unicode ZIP member name")
    key = normalized.casefold()
    if key in seen:
        raise CustodyError("duplicate or case/Unicode-colliding ZIP member")
    seen.add(key)


def stable_source(path: Path):
    """Open an unlinked, regular archive without following symlink ancestors."""
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise CustodyError("symlinked archive path is refused")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise CustodyError("safe regular-file open is unavailable")
    try:
        fd = os.open(path, flags)
        stream = os.fdopen(fd, "rb")
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= MAX_ARCHIVE_BYTES:
            stream.close()
            raise CustodyError("archive must be a bounded regular file")
        return stream, info
    except OSError:
        raise CustodyError("cannot securely open original ZIP") from None


def inventory_zip(path: Path) -> dict:
    stream, before = stable_source(Path(path))
    with stream:
        archive_sha = hashlib.sha256()
        while chunk := stream.read(CHUNK):
            archive_sha.update(chunk)
        stream.seek(0)
        rows = []
        counts = {".lit": 0, ".txt": 0}
        directory_count = 0
        total_uncompressed = 0
        try:
            with ZipFile(stream) as archive:
                members = archive.infolist()
                if len(members) > MAX_MEMBERS:
                    raise CustodyError("too many ZIP entries")
                seen: set[str] = set()
                files = []
                for info in members:
                    safe_name(info.filename, seen)
                    if stat.S_ISLNK(info.external_attr >> 16):
                        raise CustodyError("symbolic-link ZIP entry refused")
                    if info.flag_bits & 1:
                        raise CustodyError("encrypted ZIP entry refused")
                    if info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
                        raise CustodyError("unsupported ZIP compression")
                    if info.is_dir():
                        directory_count += 1
                        continue
                    extension = PurePosixPath(info.filename).suffix.lower()
                    if extension not in counts:
                        raise CustodyError("unexpected original archive file type")
                    if not 0 < info.file_size <= MAX_MEMBER_BYTES:
                        raise CustodyError("invalid or oversized member")
                    if info.file_size > max(1, info.compress_size) * MAX_COMPRESSION_RATIO:
                        raise CustodyError("excessive ZIP compression ratio")
                    total_uncompressed += info.file_size
                    if total_uncompressed > MAX_TOTAL_BYTES:
                        raise CustodyError("total declared ZIP expansion exceeds limit")
                    files.append((extension, info))
                # Exact byte order is source-local and deterministic for fixed ZIP bytes.
                for extension, info in sorted(files, key=lambda item: (item[0], item[1].filename.casefold())):
                    counts[extension] += 1
                    hasher = hashlib.sha256()
                    count = 0
                    with archive.open(info) as member:
                        while chunk := member.read(CHUNK):
                            count += len(chunk)
                            if count > MAX_MEMBER_BYTES or count > info.file_size:
                                raise CustodyError("ZIP entry expanded beyond its declared size")
                            hasher.update(chunk)
                    if count != info.file_size:
                        raise CustodyError("ZIP entry size differs from actual bytes")
                    rows.append({
                        "member_id": f"original-local:{extension[1:]}:{counts[extension]:04d}",
                        "member_name_private": info.filename,
                        "member_type": extension,
                        "uncompressed_bytes": count,
                        "compressed_bytes": info.compress_size,
                        "zip_crc32": f"{info.CRC:08x}",
                        "member_sha256": hasher.hexdigest(),
                    })
        except (BadZipFile, OSError, RuntimeError, EOFError):
            raise CustodyError("original ZIP is corrupt or unreadable") from None
        after = os.fstat(stream.fileno())
        stable = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise CustodyError("original ZIP changed during inventory")
    return {
        "schema_version": "1.0.0",
        "record_type": "PRIVATE_ORIGINAL_EBOOK_MEMBER_CUSTODY",
        "archive_sha256": archive_sha.hexdigest(),
        "archive_bytes": before.st_size,
        "zip_entries": len(members),
        "directory_entries": directory_count,
        "file_observations": len(rows),
        "counts_by_extension": counts,
        "total_uncompressed_bytes": total_uncompressed,
        "members_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "members": rows,
        "source_work_binding": "UNRESOLVED",
        "edition_identity": "UNRESOLVED",
        "copyright_rights": "UNKNOWN",
        "work_admission_effect": "NONE",
        "coverage_effect": "NONE",
        "source_read_level": "FILE_BYTES_HASHED_NO_SEMANTIC_READ",
        "privacy": "OWNER_PRIVATE_DO_NOT_PUBLISH",
    }


def open_private_output(path: Path):
    """Open an owner-only, non-overwriting private file, with pinned parents."""
    target = path.absolute()
    if target == ROOT or ROOT in target.parents:
        raise CustodyError("refusing output inside the public repository")
    if target.exists() or target.is_symlink():
        raise CustodyError("refusing to overwrite a previous receipt")
    if not target.parent.is_dir() or not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise CustodyError("secure private output directory unavailable")
    fd = os.open(target.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in target.parent.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=fd)
            os.close(fd)
            fd = next_fd
        output_fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                            0o600, dir_fd=fd)
        return os.fdopen(output_fd, "wb")
    except OSError:
        raise CustodyError("cannot securely create new private receipt") from None
    finally:
        os.close(fd)


def read_private_json(path: Path) -> dict:
    stream, info = stable_source(path)
    with stream:
        if info.st_size > MAX_RECEIPT_BYTES:
            raise CustodyError("private receipt exceeds size limit")
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise CustodyError("duplicate JSON key in private receipt")
                result[key] = value
            return result
        try:
            result = json.loads(stream.read().decode("utf-8"),
                                object_pairs_hook=unique_keys,
                                parse_constant=lambda _: (_ for _ in ()).throw(CustodyError("non-JSON constant")))
        except (ValueError, UnicodeError, RecursionError):
            raise CustodyError("invalid private receipt JSON") from None
    if type(result) is not dict:
        raise CustodyError("private receipt must be a JSON object")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "verify"))
    parser.add_argument("--original-zip", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expect-archive-sha256")
    parser.add_argument("--expect-lit", type=int)
    parser.add_argument("--expect-txt", type=int)
    args = parser.parse_args(argv)
    try:
        if (args.mode == "capture" and (args.out is None or args.receipt is not None)
                or args.mode == "verify" and (args.receipt is None or args.out is not None)):
            raise CustodyError("capture requires --out; verify requires --receipt")
        inventory = inventory_zip(args.original_zip)
        if args.expect_archive_sha256 is not None and (
            not re.fullmatch(r"[0-9a-f]{64}", args.expect_archive_sha256)
            or inventory["archive_sha256"] != args.expect_archive_sha256
        ):
            raise CustodyError("original archive SHA-256 differs from expected custody receipt")
        if args.expect_lit is not None and (
            args.expect_lit < 0 or inventory["counts_by_extension"][".lit"] != args.expect_lit
        ):
            raise CustodyError("LIT member count differs from expected custody receipt")
        if args.expect_txt is not None and (
            args.expect_txt < 0 or inventory["counts_by_extension"][".txt"] != args.expect_txt
        ):
            raise CustodyError("TXT member count differs from expected custody receipt")
        if args.mode == "capture":
            payload = json.dumps(inventory, indent=2, ensure_ascii=False,
                                 allow_nan=False).encode("utf-8") + b"\n"
            if len(payload) > MAX_RECEIPT_BYTES:
                raise CustodyError("private inventory exceeds receipt size limit")
            with open_private_output(args.out) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            print(f"PRIVATE_CUSTODY_CAPTURED {inventory['file_observations']} file members; no corpus effect")
        else:
            if read_private_json(args.receipt) != inventory:
                raise CustodyError("private receipt does not match original archive bytes")
            print(f"PRIVATE_CUSTODY_VERIFIED {inventory['file_observations']} file members; no corpus effect")
        return 0
    except CustodyError as exc:
        print(f"PRIVATE_CUSTODY_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
