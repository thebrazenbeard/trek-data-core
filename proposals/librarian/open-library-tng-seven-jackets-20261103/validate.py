#!/usr/bin/env python3
"""Fail-closed, source-only validation of seven TNG cover candidates.

This checks committed record identity and prior accepted publisher packet bytes.
It does NOT re-fetch mutable Open Library JSON or JPEGs and grants no display right.
"""

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
EXPECTED_PACKET_FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
CACHE_NAME_RE = re.compile(r"^(validate|test_validate)\.cpython-[0-9]+(?:\.opt-[12])?\.pyc$")
MANIFEST_SHA256 = "82e1b51a9940afa0fa07dbd35f4ffba887dc160deaba4dd9b64d05bae0d81400"
MEDIA_OR_EMBED_RE = re.compile(
    r"!\s*\[|<\s*/?\s*[a-z][^>]*>|<\s*!|\bdata\s*:\s*(?:image|audio|video|text/html)\s*/",
    re.IGNORECASE,
)
ROW_SET_DIGEST = "58a2fc334d40aacee8b0f4d3354350cf9fedc78fd79ac866238cf318e784f6f3"
BASELINE = "4b047d014c57b7fd4a56628acb6c9a631cc21c74"
EXPECTED_COVERS = {
    "9780743412155": (13778645, "NEXT_TEN"),
    "9780743420877": (8641748, "NEXT_TEN"),
    "9780743420952": (13902771, "THIRD_TEN"),
    "9780743420969": (13787094, "THIRD_TEN"),
    "9780743420976": (13778643, "THIRD_TEN"),
    "9780743421027": (476408, "THIRD_TEN"),
    "9780743421102": (13783845, "THIRD_TEN"),
}
EXPECTED_HELD_ISBNS = {
    "9780743412162", "9780743412179", "9780743420860", "9780743420891",
    "9780743420907", "9780743420914", "9780743420921", "9780743420938",
    "9780743420945", "9780743420990", "9780743421003", "9780743421010",
    "9780743421096", "9780743420587", "9780671040994", "9780743475631",
}
ROOT_KEYS = {
    "schema_version", "proposal_id", "accepted_baseline", "source_scope",
    "publisher_packet_receipts", "metadata_api", "cover_api", "rights_context",
    "observed_on_utc", "isbn_api_responses_checked", "medium_jacket_candidates",
    "no_cover_field_holds", "private_archive_members_or_text_exported",
    "source_or_work_admission_effect", "literary_coverage_effect",
    "explorer_artwork_release_effect", "image_bytes_committed",
    "copyright_disposition", "candidate_review_disposition", "candidates", "holds",
}
CANDIDATE_KEYS = {
    "publisher_packet", "publisher_title", "publisher_locator", "isbn13",
    "open_library_edition", "open_library_title", "open_library_response_sha256",
    "cover_id", "medium_url", "medium_sha256", "medium_bytes",
    "visual_result", "specific_hold",
}
HOLD_KEYS = {"isbn13", "open_library_edition", "open_library_response_sha256", "reason"}
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
ISBN_RE = re.compile(r"^97[89][0-9]{10}$")
EDITION_RE = re.compile(r"^OL[0-9]+M$")


def _pairs_unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _load(path: Path):
    return json.loads(path.read_text("utf-8"), object_pairs_hook=_pairs_unique)


def _sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_isbn(isbn: str):
    if not isinstance(isbn, str) or not ISBN_RE.fullmatch(isbn):
        raise ValueError("invalid ISBN13")
    checksum = sum((1 if i % 2 == 0 else 3) * int(n) for i, n in enumerate(isbn))
    if checksum % 10:
        raise ValueError("ISBN13 check digit mismatch")


def _validate_source_only_packet(root: Path):
    """Hold is a *whole-packet* property, not just records.json fields.

    Reject surprise trees, symlinks and media before reading any other receipt.
    Markdown is additionally byte-pinned and prohibited from embedding media/HTML.
    """
    folder = root / PACKET.relative_to(ROOT).parent
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("missing or redirected held packet")
    children = list(folder.iterdir())
    names = {p.name for p in children}
    if names - {"__pycache__"} != EXPECTED_PACKET_FILES:
        raise ValueError("unreviewed packet file, directory or media payload")
    if any(not p.is_file() or p.is_symlink()
           for p in children if p.name != "__pycache__"):
        raise ValueError("redirected, nested or nonregular held packet member")
    if "__pycache__" in names:
        cache = folder / "__pycache__"
        if not cache.is_dir() or cache.is_symlink():
            raise ValueError("nonstandard Python cache")
        for bytecode_file in cache.iterdir():
            match = CACHE_NAME_RE.fullmatch(bytecode_file.name)
            if not match or not bytecode_file.is_file() or bytecode_file.is_symlink():
                raise ValueError("unreviewed Python cache member or nested payload")
            source = (folder / f"{match.group(1)}.py").resolve()
            compiled_optimization = int(bytecode_file.name[-5]) if ".opt-" in bytecode_file.name else 0
            actual = bytecode_file.read_bytes()
            with tempfile.TemporaryDirectory() as temp:
                expected_path = Path(temp) / "expected.pyc"
                py_compile.compile(str(source), cfile=str(expected_path), doraise=True,
                                   optimize=compiled_optimization)
                expected_code = expected_path.read_bytes()[16:]
            if (not actual.startswith(importlib.util.MAGIC_NUMBER) or actual[16:] != expected_code):
                raise ValueError("Python cache not exact compilation of allowed source")
    manifest = folder / "MANIFEST.md"
    if _sha(manifest) != MANIFEST_SHA256:
        raise ValueError("reviewed source-only manifest bytes changed")
    if MEDIA_OR_EMBED_RE.search(manifest.read_text("utf-8")):
        raise ValueError("executable or hotlinked media markup in held manifest")


def validate(data=None, root: Path = ROOT):
    _validate_source_only_packet(root)
    data = _load(root / PACKET.relative_to(ROOT)) if data is None else data
    if not isinstance(data, dict) or set(data) != ROOT_KEYS:
        raise ValueError("unreviewed packet envelope")
    if (data["schema_version"] != "1.0.0" or
            data["proposal_id"] != "LIBRARIAN-OPEN-LIBRARY-TNG-SEVEN-JACKETS-20261103" or
            data["accepted_baseline"] != BASELINE or
            data["source_scope"] != "PUBLIC_PUBLISHER_EDITION_TO_OPEN_LIBRARY_ISBN_COVER_CANDIDATES" or
            data["metadata_api"] != "https://openlibrary.org/dev/docs/api/books" or
            data["cover_api"] != "https://openlibrary.org/dev/docs/api/covers" or
            data["rights_context"] != "https://openlibrary.org/developers/licensing" or
            data["observed_on_utc"] != "2026-11-03" or
            data["isbn_api_responses_checked"] != 23 or
            data["medium_jacket_candidates"] != 7 or
            data["no_cover_field_holds"] != 16 or
            data["private_archive_members_or_text_exported"] is not False or
            data["image_bytes_committed"] is not False or
            any(data[k] != "NONE" for k in ("source_or_work_admission_effect",
                "literary_coverage_effect", "explorer_artwork_release_effect")) or
            data["copyright_disposition"] != "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" or
            data["candidate_review_disposition"] != "LIBRARIAN_VISUAL_CHECK_REQUIRES_INDEPENDENT_REVIEW"):
        raise ValueError("unreviewed rights, coverage or release promotion")
    rows = data["candidates"]
    holds = data["holds"]
    if not isinstance(rows, list) or not isinstance(holds, list) or len(rows) != 7 or len(holds) != 16:
        raise ValueError("candidate/hold denominator drift")
    encoded = json.dumps([rows, holds], sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != ROW_SET_DIGEST:
        raise ValueError("observed Open Library source/visual identity packet changed")

    receipts = data["publisher_packet_receipts"]
    if not isinstance(receipts, dict) or set(receipts) != {"NEXT_TEN", "THIRD_TEN"}:
        raise ValueError("publisher source packets changed")
    expected_paths = {
        "NEXT_TEN": ("proposals/librarian/opf-publisher-crosscheck-next-ten-20261103/records.json",
                     "32ef1fe89532fbc42dfb6f9e7dd979ca415fef60dd307573b212cb16ea2aa5c1"),
        "THIRD_TEN": ("proposals/librarian/opf-publisher-crosscheck-third-ten-20261103/records.json",
                      "7889531fc770d6457e8cab034b685c0bbc41a7861693644e615ff2761a707f66"),
    }
    source_rows = {}
    for label, (path, digest) in expected_paths.items():
        receipt = receipts[label]
        if not isinstance(receipt, dict) or receipt != {"path": path, "sha256": digest}:
            raise ValueError("publisher source packet receipt changed")
        source_path = root / path
        if _sha(source_path) != digest:
            raise ValueError("publisher packet source bytes changed")
        source_rows[label] = {row["publisher_isbn13"]: row for row in _load(source_path)["records"]}

    if {r["isbn13"] for r in rows} != set(EXPECTED_COVERS) or \
            {h["isbn13"] for h in holds} != EXPECTED_HELD_ISBNS:
        raise ValueError("unreviewed ISBN inserted, dropped or duplicated")
    if len({r["cover_id"] for r in rows}) != len(rows):
        raise ValueError("reused Open Library cover identifier")
    for row in rows:
        if not isinstance(row, dict) or set(row) != CANDIDATE_KEYS:
            raise ValueError("candidate fields changed")
        isbn = row["isbn13"]
        _expected_isbn(isbn)
        cover_id, packet = EXPECTED_COVERS[isbn]
        old = source_rows[packet].get(isbn)
        if (old is None or row["publisher_packet"] != packet or
                row["publisher_title"] != old["publisher_title"] or
                row["publisher_locator"] != old["publisher_locator"] or
                old["publisher_isbn13"] != old["isbn13_candidate"] or
                row["cover_id"] != cover_id):
            raise ValueError("publisher ISBN/title/edition-to-cover identity mismatch")
        if (not EDITION_RE.fullmatch(row["open_library_edition"]) or
                not row["open_library_title"] or
                not SHA_RE.fullmatch(row["open_library_response_sha256"]) or
                row["medium_url"] != f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg?default=false" or
                not SHA_RE.fullmatch(row["medium_sha256"]) or
                type(row["medium_bytes"]) is not int or not 1000 <= row["medium_bytes"] <= 100000 or
                row["visual_result"] != "TNG_BOOK_JACKET_TITLE_MATCH_LIBRARIAN_VISUAL_CHECK" or
                row["specific_hold"] != ("PUBLISHER_CREATOR_RENDERING_CONFLICT_UNRESOLVED"
                    if isbn == "9780743412155" else "NONE")):
            raise ValueError(f"unreviewed Open Library JPEG, image class or author hold: {isbn}")
    for row in holds:
        if not isinstance(row, dict) or set(row) != HOLD_KEYS:
            raise ValueError("no-cover hold fields changed")
        _expected_isbn(row["isbn13"])
        if (not EDITION_RE.fullmatch(row["open_library_edition"]) or
                not SHA_RE.fullmatch(row["open_library_response_sha256"]) or
                row["reason"] != "NO_COVERS_FIELD"):
            raise ValueError("no-cover metadata claim drifted")
    return {"isbn_checked": 23, "visually_reviewed_held_jackets": 7,
            "no_cover_field_holds": 16, "work_admissions": 0, "images_released": 0}


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
