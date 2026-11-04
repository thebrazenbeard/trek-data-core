#!/usr/bin/env python3
"""Optional read-only rehash of owner-only S.C.E. #35. Emits no novel text."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from .validate import DATA, EXPECTED_SPANS, fail, validate


def scan_chapters(html_bytes: bytes) -> tuple[tuple[int, int, str], ...]:
    """Locate exact 15 ordered HTML anchors, terminating at continuation, not backmatter."""
    matches = list(re.finditer(rb'id="ch_(\d+)"', html_bytes))
    if len(matches) != 15 or [int(m.group(1)) for m in matches] != list(range(1, 16)):
        fail("Expected 15 unique sequential narrative chapter anchors")
    starts = [m.start() for m in matches]
    marker = html_bytes.find(b"TO BE CONTINUED")
    if marker <= starts[-1] or html_bytes.find(b"TO BE CONTINUED", marker + 1) >= 0:
        fail("Missing, duplicate, or premature Book One continuation marker")
    ends = [*starts[1:], marker]
    return tuple((a, b, hashlib.sha256(html_bytes[a:b]).hexdigest()) for a, b in zip(starts, ends))


def verify_archive(archive_path: Path, doc: dict) -> None:
    """Rehash exact members and chapter slices in memory without extraction/output."""
    validate(doc)
    if archive_path.is_symlink() or not archive_path.is_file():
        fail("Owner ZIP must be a regular non-symlink file")
    src = doc["source"]
    if archive_path.name != src["archive_basename"] or archive_path.stat().st_size != src["archive_length_bytes"]:
        fail("Owner ZIP name/length differs")
    sha = hashlib.sha256()
    with archive_path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(part)
    if sha.hexdigest() != src["archive_sha256"]:
        fail("Owner ZIP digest differs")
    with zipfile.ZipFile(archive_path) as archive:
        archive_members = archive.namelist()
        for name_field, size_field, sha_field in (
            ("opf_entry", "opf_length_bytes", "opf_sha256"),
            ("toc_entry", "toc_length_bytes", "toc_sha256"),
            ("html_entry", "html_length_bytes", "html_sha256"),
        ):
            name = src[name_field]
            if archive_members.count(name) != 1 or archive.getinfo(name).file_size != src[size_field]:
                fail("Expected unique bounded owner ZIP member")
            blob = archive.read(name)
            if len(blob) != src[size_field] or hashlib.sha256(blob).hexdigest() != src[sha_field]:
                fail("Owner ZIP member content has changed")
        opf = archive.read(src["opf_entry"])
        if b"0-7434-7609-3" not in opf or b"0-9673008-1-9" not in opf:
            fail("Two distinct OPF ISBN header/work literals missing")
        if len(re.findall(rb"<itemref\s", opf)) != 1:
            fail("Unexpected OPF spine HTML entry count")
        for n in range(1, 16):
            if opf.count(f'DemonBook1,The.html#ch_{n}"'.encode()) != 1:
                fail(f"OPF chapter tour {n} missing/duplicated")
        if scan_chapters(archive.read(src["html_entry"])) != EXPECTED_SPANS:
            fail("Exact privately read chapter spans disagree with frozen receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Opt-in local owner archive verification, no content export")
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify_archive(args.archive, json.loads(DATA.read_text(encoding="utf-8")))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("HELD_SCE35_ARCHIVE_RECHECK_FAILED: " + type(exc).__name__, file=sys.stderr)
        return 1
    print("HELD_SCE35_ARCHIVE_RECHECK_PASS: 3 archive members, 15 spans; no source text output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
