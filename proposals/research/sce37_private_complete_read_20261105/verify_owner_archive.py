"""Read-only private ZIP verification for S.C.E. #37; never emits ebook prose."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .validate import DATA, validate


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_chapters(source_html: bytes) -> list[tuple[int, int, str]]:
    # Include the *entire* chapter tag from its '<', not the embedded 'ch_N'.
    chapter_tags = list(re.finditer(rb'<div class="chapter" id="ch_([0-9]+)">', source_html))
    if [int(m.group(1)) for m in chapter_tags] != list(range(1, 11)):
        raise ValueError("expected ten ordered full HTML narrative-chapter tags")
    if len(chapter_tags) != 10:
        raise ValueError("duplicate or omitted narrative chapter tag")
    end = source_html.find(b'<div class="aboutAuthorPage"', chapter_tags[-1].start())
    if end <= chapter_tags[-1].start():
        raise ValueError("cannot identify first author-biography boundary")
    starts = [m.start() for m in chapter_tags]
    return [(start, stop, _digest(source_html[start:stop]))
            for start, stop in zip(starts, starts[1:] + [end])]


def verify_archive(converted_zip: Path, packet: dict, original_zip: Path | None = None) -> tuple[int, bool]:
    validate(packet)
    s = packet["source"]
    if converted_zip.name != s["archive_basename"] or not converted_zip.is_file():
        raise ValueError("exact private converted ZIP unavailable")
    if converted_zip.stat().st_size != s["archive_length_bytes"] or _digest(converted_zip.read_bytes()) != s["archive_sha256"]:
        raise ValueError("private converted archive differs from expected full bytes")
    with zipfile.ZipFile(converted_zip) as archive:
        for loc, length, digest in (("opf_entry", "opf_length_bytes", "opf_sha256"),
                                    ("html_entry", "html_length_bytes", "html_sha256"),
                                    ("toc_entry", "toc_length_bytes", "toc_sha256")):
            contents = archive.read(s[loc])
            if len(contents) != s[length] or _digest(contents) != s[digest]:
                raise ValueError(f"changed converted source member: {loc}")
        opf = archive.read(s["opf_entry"])
        if s["raw_opf_work_isbn10_literal"].encode() not in opf or s["owner_opf_creator_display"].encode() not in opf:
            raise ValueError("owner-private OPF content identity differs")
        toc = archive.read(s["toc_entry"])
        if len(re.findall(rb'#ch_[0-9]+', toc)) != 10:
            raise ValueError("converted TOC does not list exactly ten narrative anchors")
        actual = scan_chapters(archive.read(s["html_entry"]))
        stored = [(ch["byte_start_inclusive"], ch["byte_end_exclusive"], ch["raw_span_sha256"])
                  for ch in packet["chapter_spans"]]
        if actual != stored:
            raise ValueError("authored chapter tags/spans/digests differ from private source")
        manifest = archive.read(s["conversion_manifest_basename"])
        if _digest(manifest) != s["conversion_manifest_sha256"]:
            raise ValueError("owner conversion manifest fingerprint mismatch")
        matches = [x for x in json.loads(manifest)["books"] if x.get("source") == s["conversion_input_lit_basename"]]
        if len(matches) != 1:
            raise ValueError("exact converted source not uniquely found in manifest")
        entry = matches[0]
        for key, expected in (("status", "success"), ("drm", 1), ("exit_code", 0), ("output_file_count", 13)):
            if entry.get(key) != expected:
                raise ValueError(f"converter receipt changed: {key}")
    original_checked = False
    if original_zip is not None:
        if original_zip.name != s["original_lit_zip_basename"] or not original_zip.is_file():
            raise ValueError("exact original private LIT ZIP unavailable")
        if _digest(original_zip.read_bytes()) != s["original_lit_zip_sha256"]:
            raise ValueError("original LIT ZIP fingerprint mismatch")
        with zipfile.ZipFile(original_zip) as z:
            lit = z.read(s["original_lit_member"])
            if len(lit) != s["original_lit_member_length_bytes"] or _digest(lit) != s["original_lit_member_sha256"]:
                raise ValueError("original source LIT member mismatch")
        original_checked = True
    return len(actual), original_checked


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--original-lit-archive", type=Path)
    args = p.parse_args()
    counts = verify_archive(args.archive, json.loads(DATA.read_text(encoding="utf-8")), args.original_lit_archive)
    print("SCE37 private exact-source structure PASSED", counts[0], "chapters; original LIT verified=", counts[1])
