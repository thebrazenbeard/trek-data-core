#!/usr/bin/env python3
"""Opt-in, local-only byte recheck of owner ZIP. Never prints or writes book text."""

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
    """Content-independent byte cuts. Chapter 5 is present despite missing OPF tour."""
    anchors = [m.start() for m in re.finditer(rb'id=.ch_[1-5]', html_bytes)]
    if len(anchors) != 5 or any(html_bytes[pos:pos + 9] != f'id="ch_{n}"'.encode()
                                  for n, pos in enumerate(anchors, 1)):
        fail("Five ordered HTML chapter anchors not observed")
    marker = html_bytes.find(b"TO BE CONTINUED")
    if marker <= anchors[-1]:
        fail("Book One continuation marker missing or misplaced")
    ends = [*anchors[1:], marker]
    return tuple((a, b, hashlib.sha256(html_bytes[a:b]).hexdigest()) for a, b in zip(anchors, ends))


def verify_archive(archive_path: Path, doc: dict) -> None:
    """Direct authenticated-read probe; no extraction to filesystem or GitHub."""
    validate(doc)
    if archive_path.is_symlink() or not archive_path.is_file():
        fail("Owner ZIP must be a regular non-symlink file")
    source = doc["source"]
    if archive_path.name != source["archive_basename"] or archive_path.stat().st_size != source["archive_length_bytes"]:
        fail("Owner ZIP filename/byte length changed")
    digest = hashlib.sha256()
    with archive_path.open("rb") as raw:
        for chunk in iter(lambda: raw.read(1 << 20), b""):
            digest.update(chunk)
    if digest.hexdigest() != source["archive_sha256"]:
        fail("Owner ZIP fingerprint differs; no source provenance re-use")
    with zipfile.ZipFile(archive_path) as z:
        for path_field, sha_field, len_field in (("opf_entry", "opf_sha256", "opf_length_bytes"),
                                                ("toc_entry", "toc_sha256", "toc_length_bytes"),
                                                ("html_entry", "html_sha256", "html_length_bytes")):
            entry = source[path_field]
            if z.namelist().count(entry) != 1 or z.getinfo(entry).file_size != source[len_field]:
                fail(f"Archive member missing, duplicate or resized: {path_field}")
            data = z.read(entry)
            if len(data) != source[len_field] or hashlib.sha256(data).hexdigest() != source[sha_field]:
                fail(f"Archive member changed: {path_field}")
        opf = z.read(source["opf_entry"])
        if b"ISBN 0-7434-8083-X" not in opf or opf.count(b'<itemref idref="CollectiveHindSightBook1"') != 1:
            fail("Owner OPF ID or spine membership changed")
        if len(re.findall(rb'<site\s+title="Chapter [1-4]"', opf)) != 4 or b'"#ch_5"' in opf:
            fail("OPF tour discrepancy unexpectedly resolved")
        html = z.read(source["html_entry"])
        if scan_chapters(html) != EXPECTED_SPANS:
            fail("Narrative chapter byte spans no longer match privately reviewed source")


def main() -> int:
    parser = argparse.ArgumentParser(description="Recheck locally owned ZIP without exposing contents")
    parser.add_argument("--archive", required=True, type=Path, help="Owner-local ZIP path; never stored")
    args = parser.parse_args()
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    try:
        verify_archive(args.archive, doc)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"HELD_SCE33_SOURCE_RECHECK_FAILED: {type(exc).__name__}", file=sys.stderr)
        return 1
    print("HELD_SCE33_SOURCE_RECHECK_PASS: 1 ZIP, 3 members, 5 chapter byte spans; no prose emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
