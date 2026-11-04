#!/usr/bin/env python3
"""Owner-private, source-local byte custody for a converted ebook ZIP.

This *derivative* intake deliberately does not alter the original ebook
custody tool. Zero-byte converter outputs are retained as incomplete
placeholders, never content or admitted literary Sources/Works. Nothing here
reads or exports book prose, cover imagery, or OPF metadata semantics.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
ALLOWED_EXTENSIONS = frozenset({
    ".css", ".csv", ".gif", ".htm", ".html", ".jpg", ".json",
    ".opf", ".png", ".txt", ".xml",
})
EMPTY_PLACEHOLDER_EXTENSIONS = frozenset({".css", ".htm", ".jpg"})


class CustodyError(ValueError):
    """A source ZIP or private receipt violated the bounded custody contract."""


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def safe_name(name: str, seen: set[str]) -> None:
    """Reject unsafe or Windows/POSIX-ambiguous ZIP member paths."""
    normalized = unicodedata.normalize("NFKC", name)
    parts = name.split("/")
    if (not name or name.startswith("/") or DRIVE.match(name) or "\\" in name
            or any(part in {"", ".", ".."} for part in parts[:-1])
            or (parts[-1] in {"", ".", ".."} and not name.endswith("/"))
            or any(unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in name)):
        raise CustodyError("unsafe converted ZIP member path")
    if (DRIVE.match(normalized) or normalized.startswith("/")
            or normalized.split("/") != name.split("/")
            or any(part in {"", ".", ".."} for part in normalized.split("/")[:-1])
            or "\\" in normalized):
        raise CustodyError("ambiguous Unicode converted ZIP member path")
    key = normalized.casefold()
    if key in seen:
        raise CustodyError("duplicate or Unicode/case-colliding ZIP member")
    seen.add(key)


def stable_source(path: Path):
    """Open each path component with O_NOFOLLOW, not a racy path precheck."""
    target = path.absolute()
    if ".." in target.parts:
        raise CustodyError("parent-traversing custody source refused")
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_NONBLOCK")
            and hasattr(os, "O_DIRECTORY")):
        raise CustodyError("secure regular-file open unavailable")
    directory_fd = None
    try:
        directory_fd = os.open(target.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for part in target.parent.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        raw_fd = os.open(target.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=directory_fd)
        stream = os.fdopen(raw_fd, "rb")
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= MAX_ARCHIVE_BYTES:
            stream.close()
            raise CustodyError("custody source must be a bounded regular file")
        return stream, info
    except OSError:
        raise CustodyError("cannot securely open custody source") from None
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def inventory_zip(path: Path) -> dict:
    """Produce private deterministic records; never extract members to disk."""
    stream, before = stable_source(Path(path))
    with stream:
        whole = hashlib.sha256()
        while chunk := stream.read(CHUNK):
            whole.update(chunk)
        stream.seek(0)
        counts = Counter({extension: 0 for extension in ALLOWED_EXTENSIONS})
        empty_counts = Counter({extension: 0 for extension in EMPTY_PLACEHOLDER_EXTENSIONS})
        rows = []
        total_bytes = 0
        directories = 0
        try:
            with ZipFile(stream) as archive:
                entries = archive.infolist()
                if len(entries) > MAX_MEMBERS:
                    raise CustodyError("converted ZIP entry count exceeds limit")
                seen: set[str] = set()
                files = []
                entry_paths = []
                for info in entries:
                    safe_name(info.filename, seen)
                    unix_type = stat.S_IFMT(info.external_attr >> 16)
                    is_directory = info.is_dir()
                    if is_directory and unix_type not in {0, stat.S_IFDIR}:
                        raise CustodyError("ZIP directory marker has non-directory mode")
                    if not is_directory and unix_type not in {0, stat.S_IFREG}:
                        raise CustodyError("ZIP file member has non-regular Unix mode")
                    if info.flag_bits & 1:
                        raise CustodyError("encrypted ZIP member refused")
                    if info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
                        raise CustodyError("unsupported ZIP compression")
                    normalized_path = unicodedata.normalize("NFKC", info.filename).casefold()
                    entry_paths.append((normalized_path.rstrip("/"), is_directory))
                    if is_directory:
                        if info.file_size != 0:
                            raise CustodyError("directory marker contains unexpected bytes")
                        directories += 1
                        continue
                    extension = PurePosixPath(info.filename).suffix.lower()
                    if extension not in ALLOWED_EXTENSIONS:
                        raise CustodyError("unexpected converted ZIP file extension")
                    if not 0 <= info.file_size <= MAX_MEMBER_BYTES:
                        raise CustodyError("invalid or oversized converted member")
                    if info.file_size == 0 and extension not in EMPTY_PLACEHOLDER_EXTENSIONS:
                        raise CustodyError("unexpected empty converted member, including OPF")
                    if info.file_size > max(1, info.compress_size) * MAX_COMPRESSION_RATIO:
                        raise CustodyError("excessive converted ZIP compression ratio")
                    total_bytes += info.file_size
                    if total_bytes > MAX_TOTAL_BYTES:
                        raise CustodyError("total converted ZIP expansion exceeds limit")
                    files.append((extension, info))
                file_paths = {name for name, is_directory in entry_paths if not is_directory}
                directory_paths = {name for name, is_directory in entry_paths if is_directory}
                for name, is_directory in entry_paths:
                    if not is_directory and name in directory_paths:
                        raise CustodyError("ZIP path is both file and directory")
                    segments = name.split("/")
                    if any("/".join(segments[:index]) in file_paths
                           for index in range(1, len(segments))):
                        raise CustodyError("ZIP member nested beneath file path")
                for extension, info in sorted(files, key=lambda item: (item[0], item[1].filename.casefold())):
                    counts[extension] += 1
                    empty = info.file_size == 0
                    if empty:
                        empty_counts[extension] += 1
                    digest = hashlib.sha256()
                    byte_count = 0
                    with archive.open(info) as member:
                        while chunk := member.read(CHUNK):
                            byte_count += len(chunk)
                            if byte_count > MAX_MEMBER_BYTES or byte_count > info.file_size:
                                raise CustodyError("converted member expanded beyond declared size")
                            digest.update(chunk)
                    if byte_count != info.file_size:
                        raise CustodyError("converted member actual size mismatch")
                    rows.append({
                        "member_id": f"converted-local:{extension[1:]}:{counts[extension]:04d}",
                        "member_name_private": info.filename,
                        "member_type": extension,
                        "content_kind": ("CONVERSION_PLACEHOLDER" if empty
                                         else "DERIVATIVE_BYTES_HASHED_NO_COMPLETENESS_CLAIM"),
                        "uncompressed_bytes": byte_count,
                        "compressed_bytes": info.compress_size,
                        "zip_crc32": f"{info.CRC:08x}",
                        "member_sha256": digest.hexdigest(),
                    })
        except (BadZipFile, OSError, RuntimeError, EOFError):
            raise CustodyError("converted ZIP is corrupt or unreadable") from None
        after = os.fstat(stream.fileno())
        for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns"):
            if getattr(before, field) != getattr(after, field):
                raise CustodyError("converted ZIP changed during inventory")
    return {
        "schema_version": "1.0.0",
        "record_type": "PRIVATE_CONVERTED_DERIVATIVE_MEMBER_CUSTODY",
        "archive_sha256": whole.hexdigest(),
        "archive_bytes": before.st_size,
        "zip_entries": len(entries),
        "directory_entries": directories,
        "file_observations": len(rows),
        "counts_by_extension": dict(sorted(counts.items())),
        "empty_file_observations": sum(empty_counts.values()),
        "empty_counts_by_extension": dict(sorted(empty_counts.items())),
        "total_uncompressed_bytes": total_bytes,
        "members_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
        "members": rows,
        "source_work_binding": "UNRESOLVED",
        "edition_identity": "UNRESOLVED",
        "copyright_rights": "UNKNOWN",
        "content_completeness": "NOT_ESTABLISHED",
        "work_admission_effect": "NONE",
        "coverage_effect": "NONE",
        "source_read_level": "FILE_BYTES_HASHED_NO_SEMANTIC_READ",
        "privacy": "OWNER_PRIVATE_DO_NOT_PUBLISH",
    }


def checked_private_target(path: Path) -> Path:
    """Reject lexical aliases and canonical containment within the public repo.

    A path like /unrelated/../repo/private/file is physically inside repo,
    despite its lexical parent list containing an unrelated leading segment.
    Reject every '..' outright and additionally compare canonical locations.
    O_NOFOLLOW dirfd opens below still protect against subsequent symlink races.
    """
    target = path.absolute()
    if ".." in target.parts:
        raise CustodyError("parent traversal in private receipt path refused")
    try:
        canonical_root = ROOT.resolve(strict=False)
        canonical_target = target.resolve(strict=False)
    except (OSError, RuntimeError):
        raise CustodyError("cannot verify private receipt containment") from None
    if canonical_target == canonical_root or canonical_root in canonical_target.parents:
        raise CustodyError("refusing private receipt inside public repository")
    return target


def check_private_parent(path: Path):
    """Require a real owner-private receipt parent, even for verify."""
    parent = checked_private_target(path).parent
    if parent.is_symlink():
        raise CustodyError("symlinked private receipt parent refused")
    try:
        info = parent.lstat()
    except OSError:
        raise CustodyError("private receipt parent unavailable") from None
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700:
        raise CustodyError("private receipt parent must have mode 0700")


def open_private_output(path: Path):
    """Create private receipt with O_EXCL and no followed directory links."""
    target = checked_private_target(path)
    check_private_parent(target)
    if target.exists() or target.is_symlink():
        raise CustodyError("refusing to overwrite existing private receipt")
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise CustodyError("secure output directory open unavailable")
    fd = os.open(target.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in target.parent.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                              dir_fd=fd)
            os.close(fd)
            fd = next_fd
        if stat.S_IMODE(os.fstat(fd).st_mode) != 0o700:
            raise CustodyError("private receipt parent changed permissions")
        output_fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                            0o600, dir_fd=fd)
        return os.fdopen(output_fd, "wb")
    except OSError:
        raise CustodyError("cannot securely create private converted receipt") from None
    finally:
        os.close(fd)


def read_private_json(path: Path) -> dict:
    check_private_parent(path)
    if stat.S_IMODE(path.lstat().st_mode) != 0o600:
        raise CustodyError("private receipt must have mode 0600")
    stream, info = stable_source(path)
    with stream:
        if info.st_size > MAX_RECEIPT_BYTES:
            raise CustodyError("private receipt exceeds size limit")

        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise CustodyError("duplicate private receipt JSON key")
                result[key] = value
            return result

        try:
            result = json.loads(stream.read().decode("utf-8"), object_pairs_hook=unique_keys,
                                parse_constant=lambda _: (_ for _ in ()).throw(
                                    CustodyError("invalid non-JSON value")))
        except (ValueError, UnicodeError, RecursionError):
            raise CustodyError("invalid private receipt JSON") from None
    if type(result) is not dict:
        raise CustodyError("private receipt must be a JSON object")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("capture", "verify"))
    parser.add_argument("--converted-zip", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--expect-archive-sha256", required=True)
    parser.add_argument("--expect-files", type=int, required=True)
    parser.add_argument("--expect-directories", type=int, required=True)
    parser.add_argument("--expect-opf", type=int, required=True)
    parser.add_argument("--expect-empty-css", type=int, required=True)
    parser.add_argument("--expect-empty-htm", type=int, required=True)
    parser.add_argument("--expect-empty-jpg", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        if ((args.mode == "capture" and (args.out is None or args.receipt is not None))
                or (args.mode == "verify" and (args.receipt is None or args.out is not None))):
            raise CustodyError("capture requires --out; verify requires --receipt")
        if not re.fullmatch("[0-9a-f]{64}", args.expect_archive_sha256):
            raise CustodyError("invalid expected converted archive digest")
        expected = (args.expect_files, args.expect_directories, args.expect_opf,
                    args.expect_empty_css, args.expect_empty_htm, args.expect_empty_jpg)
        if any(count < 0 for count in expected):
            raise CustodyError("negative expected converted ZIP counts")
        inventory = inventory_zip(args.converted_zip)
        if (inventory["archive_sha256"] != args.expect_archive_sha256
                or inventory["file_observations"] != args.expect_files
                or inventory["directory_entries"] != args.expect_directories
                or inventory["counts_by_extension"][".opf"] != args.expect_opf
                or inventory["empty_counts_by_extension"] != {
                    ".css": args.expect_empty_css,
                    ".htm": args.expect_empty_htm,
                    ".jpg": args.expect_empty_jpg,
                }):
            raise CustodyError("converted ZIP source identity/count mismatch")
        if args.mode == "capture":
            payload = json.dumps(inventory, indent=2, ensure_ascii=False,
                                 allow_nan=False).encode("utf-8") + b"\n"
            if len(payload) > MAX_RECEIPT_BYTES:
                raise CustodyError("private converted receipt exceeds size limit")
            with open_private_output(args.out) as output:
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
            print(f"PRIVATE_CONVERTED_CAPTURED {inventory['file_observations']} file hashes; "
                  f"{inventory['empty_file_observations']} conversion placeholders; no corpus effect")
        else:
            if read_private_json(args.receipt) != inventory:
                raise CustodyError("private converted receipt differs from archive bytes")
            print(f"PRIVATE_CONVERTED_VERIFIED {inventory['file_observations']} file hashes; "
                  f"{inventory['empty_file_observations']} conversion placeholders; no corpus effect")
        return 0
    except (CustodyError, OSError) as exc:
        message = str(exc) if isinstance(exc, CustodyError) else "custody filesystem error"
        print(f"PRIVATE_CONVERTED_REJECTED: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
