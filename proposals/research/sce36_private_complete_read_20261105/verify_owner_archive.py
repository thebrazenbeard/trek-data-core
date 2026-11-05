"""Optional owner-device read-only check of S.C.E. #36 private ZIPs.

Checks bytes only in memory. Does not print, extract, commit, or network-transfer
any copyrighted prose, original LIT bytes, illustration, or cover.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from .validate import DATA, validate


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_chapters(html: bytes) -> list[tuple[int, int, str]]:
    # Match structural chapter divs, not the textual string "chapter" in prose.
    anchor = re.compile(rb'<div class="chapter" id="ch_([0-9]+)">')
    items = list(anchor.finditer(html))
    if [int(match.group(1)) for match in items] != list(range(1, 15)):
        raise ValueError("source does not have exactly 14 ordered narrative anchors")
    after = html.find(b'<div class="backMatterPage">', items[-1].start())
    if after < 0 or after <= items[-1].start():
        raise ValueError("cannot establish the author/promo backmatter boundary")
    starts = [match.start() for match in items]
    ends = starts[1:] + [after]
    return [(start, end, _sha(html[start:end])) for start, end in zip(starts, ends)]


def verify_archive(converted_zip: Path, packet: dict, original_zip: Path | None = None) -> tuple[int, int]:
    validate(packet)
    if not converted_zip.is_file():
        raise ValueError("owner-private converted ZIP not accessible")
    s = packet["source"]
    if converted_zip.name != s["archive_basename"]:
        raise ValueError("converted ZIP filename mismatch")
    if converted_zip.stat().st_size != s["archive_length_bytes"]:
        raise ValueError("converted ZIP byte length mismatch")
    if _sha(converted_zip.read_bytes()) != s["archive_sha256"]:
        raise ValueError("converted archive SHA-256 mismatch")
    with zipfile.ZipFile(converted_zip) as z:
        for key, length_key, digest_key in (("opf_entry", "opf_length_bytes", "opf_sha256"),
                                             ("html_entry", "html_length_bytes", "html_sha256"),
                                             ("toc_entry", "toc_length_bytes", "toc_sha256")):
            content = z.read(s[key])
            if len(content) != s[length_key] or _sha(content) != s[digest_key]:
                raise ValueError(f"private source member mismatch: {key}")
        html = z.read(s["html_entry"])
        toc = z.read(s["toc_entry"])
        observed = scan_chapters(html)
        stored = [(c["byte_start_inclusive"], c["byte_end_exclusive"], c["raw_span_sha256"])
                  for c in packet["chapter_spans"]]
        if observed != stored:
            raise ValueError("chapter-level source fingerprint mismatch")
        if len(re.findall(rb'#ch_[0-9]+', toc)) != 14:
            raise ValueError("private table of contents chapter count changed")
        manifest = z.read(s["conversion_manifest_basename"])
        if _sha(manifest) != s["conversion_manifest_sha256"]:
            raise ValueError("converter manifest fingerprint mismatch")
        entries = json.loads(manifest)["books"]
        candidate = [entry for entry in entries if entry.get("source") == s["conversion_input_lit_basename"]]
        if len(candidate) != 1:
            raise ValueError("converter source identity not unique")
        entry = candidate[0]
        for key, expected in (("status", "success"), ("drm", 1), ("exit_code", 0),
                              ("output_file_count", 13)):
            if entry.get(key) != expected:
                raise ValueError(f"converter report changed: {key}")
    count_original = 0
    if original_zip is not None:
        if original_zip.name != s["original_lit_zip_basename"] or not original_zip.is_file():
            raise ValueError("owner-private LIT ZIP not accessible")
        if _sha(original_zip.read_bytes()) != s["original_lit_zip_sha256"]:
            raise ValueError("LIT ZIP fingerprint mismatch")
        with zipfile.ZipFile(original_zip) as z:
            original = z.read(s["original_lit_member"])
            if len(original) != s["original_lit_member_length_bytes"] or _sha(original) != s["original_lit_member_sha256"]:
                raise ValueError("source LIT member fingerprint mismatch")
        count_original = 1
    return len(observed), count_original


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="private converted ZIP: read-only")
    parser.add_argument("--original-lit-archive", type=Path, help="optional private original LIT ZIP")
    args = parser.parse_args()
    result = verify_archive(args.archive, json.loads(DATA.read_text(encoding="utf-8")), args.original_lit_archive)
    print(f"Owner-private fingerprints VALID: {result[0]} ordered narrative chapters; original LIT checked={bool(result[1])}")
