#!/usr/bin/env python3
"""Held-only deterministic validation of final 13 OPF ISBN visual candidates."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import py_compile
import re
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
PART = PACKET.relative_to(ROOT).parent
MANIFEST_SHA = "6833f0079a0185cef02f798111ff4fae8cdf572754f70c09beee8a8f1af3d36b"
ROWS_SHA = "365c14c87e6aab55c742df4c910df7b04ae5b54567953635d59a268938d29a5d"
OPF_PATH = "proposals/librarian/private-opf-metadata-20261103/observations.json"
OPF_SHA = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
SOURCE_IDS = {214, 238, 282, 283, 284, 285, 286, 288, 294, 306, 323, 346, 347}
COVER_IDS = {
    "9780743464543": 10827006, "9780743412223": 13904465,
    "9780671501068": 405687, "9780743448727": 10701689,
    "9780743427920": 476607,
}
EXACT_ISBNS = {"9780743464543", "9780743412223", "9780743448727"}
NO_PUBLISHER_ISBN = "9780671501068"
DIFFERENT_ISBN = "9780743427920"
HTTP_404 = {"9780743412247", "9780743421195"}
ALLOWED_FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
FIELD_KEYS = {
    "opf_id", "opf_sha256", "isbn10", "isbn13", "status", "ol_edition",
    "ol_sha256", "cover_id", "medium_bytes", "medium_sha256",
    "publisher_relation", "publisher_url", "publisher_isbn13", "visual",
}
ROOT_KEYS = {
    "schema_version", "proposal_id", "accepted_baseline",
    "accepted_opf_metadata_path", "accepted_opf_metadata_sha256", "observed_on_utc",
    "private_narrative_read", "private_member_paths_exported",
    "source_or_work_admission", "artwork_release", "image_bytes_committed",
    "rights_status", "rows",
}
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
OL_RE = re.compile(r"^OL[0-9]+M$")
PYC_RE = re.compile(r"^(validate|test_validate)\.cpython-[0-9]+(?:\.opt-[12])?\.pyc$")
EMBED_RE = re.compile(r"!\s*\[|<\s*/?\s*[a-z][^>]*>|<\s*!|\bdata\s*:\s*(?:image|audio|video|text/html)\s*/", re.I)


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text("utf-8"), object_pairs_hook=pairs_unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isbn10_to13(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{9}[0-9X]", value):
        raise ValueError("invalid ISBN10 string")
    if sum((10-i) * (10 if ch == "X" else int(ch)) for i, ch in enumerate(value)) % 11:
        raise ValueError("ISBN10 checksum mismatch")
    base = "978" + value[:9]
    return base + str((-sum(int(ch) * (1 if i % 2 == 0 else 3)
                           for i, ch in enumerate(base))) % 10)


def guard_packet(root):
    folder = root / PART
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("held packet missing or redirected")
    files = list(folder.iterdir())
    names = {p.name for p in files}
    if names - {"__pycache__"} != ALLOWED_FILES:
        raise ValueError("new unreviewed packet file or image payload")
    if any(p.is_symlink() or not p.is_file() for p in files if p.name != "__pycache__"):
        raise ValueError("nested/symlink/nonregular packet member")
    if "__pycache__" in names:
        folder_cache = folder / "__pycache__"
        if folder_cache.is_symlink() or not folder_cache.is_dir():
            raise ValueError("nonstandard cache directory")
        for p in folder_cache.iterdir():
            match = PYC_RE.fullmatch(p.name)
            if not match or p.is_symlink() or not p.is_file():
                raise ValueError("unreviewed cache media/symlink/nested file")
            source = (folder / (match.group(1) + ".py")).resolve()
            opt = int(p.name[-5]) if ".opt-" in p.name else 0
            with tempfile.TemporaryDirectory() as tmp:
                check = Path(tmp) / "expected.pyc"
                py_compile.compile(str(source), cfile=str(check), doraise=True, optimize=opt)
                expected = check.read_bytes()[16:]
            raw = p.read_bytes()
            if not raw.startswith(importlib.util.MAGIC_NUMBER) or raw[16:] != expected:
                raise ValueError("cache is not exact CPython compilation")
    if sha(folder / "MANIFEST.md") != MANIFEST_SHA:
        raise ValueError("manifest not source-reviewed")
    if EMBED_RE.search((folder / "MANIFEST.md").read_text("utf-8")):
        raise ValueError("remote image/media/html embed in held manifest")


def validate(data=None, root=ROOT):
    guard_packet(root)
    data = load(root / PACKET.relative_to(ROOT)) if data is None else data
    if not isinstance(data, dict) or set(data) != ROOT_KEYS:
        raise ValueError("unreviewed packet field")
    if (data["schema_version"] != "1.0.0" or
            data["proposal_id"] != "LIBRARIAN-OPF-FINAL-THIRTEEN-JACKETS-20261103" or
            data["accepted_baseline"] != "a3b30aa686a3fadd7ec0ea572cdcf483730a2c41" or
            data["accepted_opf_metadata_path"] != OPF_PATH or
            data["accepted_opf_metadata_sha256"] != OPF_SHA or
            data["observed_on_utc"] != "2026-11-03" or
            data["private_narrative_read"] is not False or
            data["private_member_paths_exported"] is not False or
            data["source_or_work_admission"] != "NONE" or
            data["artwork_release"] != "NONE" or
            data["image_bytes_committed"] is not False or
            data["rights_status"] != "THIRD_PARTY_JACKET_RIGHTS_UNVERIFIED"):
        raise ValueError("release, identity, private body or rights elevation")
    rows = data["rows"]
    if not isinstance(rows, list) or len(rows) != 13:
        raise ValueError("final thirteen denominator changed")
    if hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != ROWS_SHA:
        raise ValueError("unreviewed OPF/OL/JPEG publisher observations")
    original_path = root / OPF_PATH
    if sha(original_path) != OPF_SHA:
        raise ValueError("accepted OPF metadata source bytes changed")
    source = {r["source_local_id"]: r for r in load(original_path)["rows"]}
    ids, hashes, isbns = set(), set(), set()
    counts = {
        "exact_publisher_isbn_matches": 0,
        "publisher_different_isbn_holds": 0,
        "publisher_unbound_cover_holds": 0,
        "medium_jackets_held": 0,
        "api_no_cover_holds": 0,
        "api_404_holds": 0,
        "namespace_recovered_opf": 0,
    }
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELD_KEYS:
            raise ValueError("unreviewed row field")
        src = source.get(row["opf_id"])
        if (not src or src["parse_status"] not in ("PARSED", "OPF_XML_NAMESPACE_RECOVERED") or
                src["opf_entry_sha256"] != row["opf_sha256"] or
                src["isbn_checksum_valid"] != [row["isbn10"]] or
                isbn10_to13(row["isbn10"]) != row["isbn13"] or
                not SHA_RE.fullmatch(row["opf_sha256"]) or
                not SHA_RE.fullmatch(row["ol_sha256"])):
            raise ValueError("not source-bound accepted OPF ISBN metadata")
        if src["parse_status"] == "OPF_XML_NAMESPACE_RECOVERED":
            counts["namespace_recovered_opf"] += 1
        if row["opf_id"] in ids or row["opf_sha256"] in hashes or row["isbn13"] in isbns:
            raise ValueError("duplicated OPF source, hash or ISBN")
        ids.add(row["opf_id"])
        hashes.add(row["opf_sha256"])
        isbns.add(row["isbn13"])
        isbn = row["isbn13"]
        if isbn in COVER_IDS:
            if (row["status"] != 200 or not OL_RE.fullmatch(row["ol_edition"] or "") or
                    row["cover_id"] != COVER_IDS[isbn] or
                    type(row["medium_bytes"]) is not int or row["medium_bytes"] < 1000 or
                    not SHA_RE.fullmatch(row["medium_sha256"])):
                raise ValueError("unreviewed Open Library image source")
            counts["medium_jackets_held"] += 1
            if isbn in EXACT_ISBNS:
                if (row["publisher_relation"] != "OFFICIAL_EXACT_ISBN_EBOOK" or
                        row["publisher_isbn13"] != isbn or
                        row["visual"] != "TITLE_BEARING_JACKET_LIBRARIAN_HOLD"):
                    raise ValueError("official exact edition claim drift")
                counts["exact_publisher_isbn_matches"] += 1
            elif isbn == DIFFERENT_ISBN:
                if (row["publisher_relation"] != "OFFICIAL_DIFFERENT_EBOOK_ISBN_HOLD" or
                        row["publisher_isbn13"] != "9780743427951" or
                        row["visual"] != "TITLE_BEARING_JACKET_LIBRARIAN_HOLD"):
                    raise ValueError("Gauntlet edition mismatch suppressed")
                counts["publisher_different_isbn_holds"] += 1
            elif isbn == NO_PUBLISHER_ISBN:
                if (row["publisher_relation"] != "NO_EXACT_ISBN_PUBLISHER_PRODUCT_FOUND" or
                        row["publisher_url"] is not None or
                        row["publisher_isbn13"] is not None or
                        row["visual"] != "JACKET_TEXT_MATCH_BUT_OL_TITLE_UNDERSPECIFIED"):
                    raise ValueError("Deep Space Nine Companion unbound ISBN promoted")
                counts["publisher_unbound_cover_holds"] += 1
            if row["publisher_url"] is not None and (
                    not row["publisher_url"].startswith(("https://www.simonandschuster.com/",
                                                         "https://www.simonandschuster.biz/")) or
                    not row["publisher_url"].endswith("/" + row["publisher_isbn13"])):
                raise ValueError("publisher source URL not exact official ISBN page")
        else:
            if (row["cover_id"] is not None or row["medium_bytes"] is not None or
                    row["medium_sha256"] is not None or row["publisher_url"] is not None or
                    row["publisher_isbn13"] is not None):
                raise ValueError("unsourced image or publisher on no-cover hold")
            if isbn in HTTP_404:
                if (row["status"] != 404 or row["ol_edition"] is not None or
                        row["publisher_relation"] != "NOT_CHECKED_OL_ISBN_404" or
                        row["visual"] != "OL_ISBN_ENDPOINT_404"):
                    raise ValueError("404 held source promoted")
                counts["api_404_holds"] += 1
            else:
                if (row["status"] != 200 or not OL_RE.fullmatch(row["ol_edition"] or "") or
                        row["publisher_relation"] != "NOT_CHECKED_NO_COVERS_FIELD" or
                        row["visual"] != "NO_COVERS_FIELD"):
                    raise ValueError("no-cover source claim changed")
                counts["api_no_cover_holds"] += 1
    if {int(i.split(":")[1]) for i in ids} != SOURCE_IDS or len(hashes) != 13 or len(isbns) != 13:
        raise ValueError("unexpected final source selection")
    if counts != {
        "exact_publisher_isbn_matches": 3, "publisher_different_isbn_holds": 1,
        "publisher_unbound_cover_holds": 1, "medium_jackets_held": 5,
        "api_no_cover_holds": 6, "api_404_holds": 2, "namespace_recovered_opf": 5,
    }:
        raise ValueError("source denominator or publisher edition classification changed")
    return {**counts, "opf_metadata_rows": 13, "distinct_opf_member_sha256": 13,
            "accepted_works": 0, "explorer_images_released": 0}


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
