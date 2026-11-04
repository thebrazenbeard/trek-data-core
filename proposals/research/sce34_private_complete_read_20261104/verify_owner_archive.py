#!/usr/bin/env python3
"""Optional owner-host recheck. No extraction, copyrighted output, or network use."""

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
    """Pin seven in-source anchors and stop before backmatter/Book Three advertisement."""
    anchors = [m.start() for m in re.finditer(rb'id=.ch_[1-7]', html_bytes)]
    if len(anchors) != 7 or any(html_bytes[pos:pos + 9] != f'id="ch_{n}"'.encode()
                                  for n, pos in enumerate(anchors, 1)):
        fail("Expected exactly seven ordered narrative HTML anchors")
    marker = html_bytes.find(b">END<")
    if marker <= anchors[-1] or html_bytes.find(b">END<", marker + 1) >= 0:
        fail("Narrative end marker missing, duplicated or misplaced")
    ends = [*anchors[1:], marker]
    return tuple((a, b, hashlib.sha256(html_bytes[a:b]).hexdigest()) for a, b in zip(anchors, ends))


def verify_archive(archive_path: Path, doc: dict) -> None:
    """Read bounded exact private archive members in memory, emit no text."""
    validate(doc)
    if archive_path.is_symlink() or not archive_path.is_file():
        fail("Owner ZIP must be a regular non-symlink file")
    src = doc["source"]
    if archive_path.name != src["archive_basename"] or archive_path.stat().st_size != src["archive_length_bytes"]:
        fail("Owner archive name or size differs")
    digest = hashlib.sha256()
    with archive_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != src["archive_sha256"]:
        fail("Owner ZIP SHA-256 changed")
    with zipfile.ZipFile(archive_path) as archive:
        for member_field, size_field, digest_field in (
            ("opf_entry", "opf_length_bytes", "opf_sha256"),
            ("toc_entry", "toc_length_bytes", "toc_sha256"),
            ("html_entry", "html_length_bytes", "html_sha256"),
        ):
            member = src[member_field]
            if archive.namelist().count(member) != 1 or archive.getinfo(member).file_size != src[size_field]:
                fail("Owner archive member missing, duplicated or wrong size")
            content = archive.read(member)
            if len(content) != src[size_field] or hashlib.sha256(content).hexdigest() != src[digest_field]:
                fail("Owner archive member digest differs")
        opf = archive.read(src["opf_entry"])
        if b"ISBN 0-7434-8084-8" not in opf or \
           opf.count(b'<itemref idref="CollectiveHindsightBook2"') != 1:
            fail("Owner ISBN or one-spine-item identity changed")
        for i in range(1, 8):
            entry = f'<site title="Chapter {i}" href="CollectiveHindsightBook2.html#ch_{i}"'.encode()
            if opf.count(entry) != 1:
                fail(f"OPF chapter tour missing or duplicated locator {i}")
        if re.search(rb'<site\s+title="Chapter (?:8|9|10)"', opf):
            fail("Tour has additional advertised chapters; packet needs review")
        if scan_chapters(archive.read(src["html_entry"])) != EXPECTED_SPANS:
            fail("Read chapter byte ranges differ from frozen receipt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Opt-in local-only source fingerprint recheck")
    parser.add_argument("--archive", required=True, type=Path, help="Path remains local and is never recorded")
    args = parser.parse_args()
    packet = json.loads(DATA.read_text(encoding="utf-8"))
    try:
        verify_archive(args.archive, packet)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print("HELD_SCE34_SOURCE_RECHECK_FAILED: " + type(exc).__name__, file=sys.stderr)
        return 1
    print("HELD_SCE34_SOURCE_RECHECK_PASS: ZIP, OPF, TOC, HTML, 7 spans; zero source prose emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
