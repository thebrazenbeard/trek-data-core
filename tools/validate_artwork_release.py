#!/usr/bin/env python3
"""Fail-closed, non-admitting artwork sidecar and static Pages release gate.

No proposed artwork becomes a public file merely by supplying a plausible
hash, ISBN, Commons label, or `PUBLIC_DISPLAY_PERMISSION_VERIFIED` string.
The independently reviewed, code-owned pins below are deliberately empty.
An authorized release changes those pins and includes exact review receipts,
real same-origin image bytes, and the separately reviewed Explorer UI gate.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "explorer/artwork-catalog.json"
ART_DIRECTORY = "explorer/licensed-artwork"
OL_SOURCE_PACKET = "proposals/librarian/open-library-nine-literature-20261103/records.json"
MAX_ART_BYTES = 16_000_000
MAX_MANIFEST_BYTES = 2_000_000
HASH = re.compile(r"[a-f0-9]{64}\Z")
IMAGE_PATH = re.compile(r"\./licensed-artwork/([a-z0-9][a-z0-9._-]{1,128}\.(?:png|jpe?g|webp))\Z")
RECEIPT_PATH = re.compile(r"registry/artwork-(?:rights|edition)-receipts/[a-z0-9][a-z0-9_-]{1,100}\.json\Z")
ISBN = re.compile(r"97[89][0-9]{10}\Z")
ROOT_KEYS = {"schema_version", "data_status", "coverage_effect", "rights_policy", "artwork_count", "artwork"}
LOCAL_KEYS = {"row_id", "image_path", "image_sha256", "alt_text", "source_locator", "rights_status",
              "rights_receipt_sha256", "artwork_kind", "attribution_text", "attribution_url"}
OPEN_LIBRARY_KEYS = {"row_id", "provider", "cover_id", "isbn", "alt_text", "source_locator",
                     "rights_status", "edition_metadata_sha256", "attribution_url"}
LOCAL_PIN_KEYS = LOCAL_KEYS | {"rights_receipt_path", "rights_page_snapshot_sha256", "rights_evidence_url",
                               "license_identifier"}
OPEN_LIBRARY_PIN_KEYS = OPEN_LIBRARY_KEYS | {"edition_review_receipt_path", "edition_review_receipt_sha256",
                                             "edition_metadata_locator", "image_preview_sha256"}
LOCAL_RECEIPT_KEYS = {"schema_version", "review_status", "row_id", "source_locator", "image_path",
                      "image_sha256", "rights_page_snapshot_sha256", "rights_evidence_url", "license_identifier",
                      "artwork_kind", "attribution_text", "attribution_url", "rights_reviewer",
                      "source_reviewer", "reviewed_on"}
OPEN_LIBRARY_RECEIPT_KEYS = {"schema_version", "review_status", "row_id", "source_locator", "isbn",
                             "cover_id", "edition_metadata_sha256", "edition_metadata_locator",
                             "edition_reviewer", "source_reviewer", "reviewed_on", "image_review_status",
                             "image_review_observation", "image_reviewer", "image_preview_sha256"}
ARTWORK_KINDS = {"PUBLICITY_STILL", "POSTER", "COVER", "OTHER"}
LICENSE_BASES = {"PD-US-no-notice", "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "EXPLICIT_WRITTEN_PERMISSION"}

# Accepted release reviews are code-owned, not read from sidecar-supplied data.
# Each pin is exact LOCAL_PIN_KEYS / OPEN_LIBRARY_PIN_KEYS. A public review
# receipt, its literal SHA-256, and a real image are still separately required.
# In particular, a Commons file-page tag is NOT independent rights clearance.
REVIEWED_LOCAL_ARTWORK_PINS: dict[str, dict] = {}
# Separately source-checked public publisher ISBN rows, raw Open Library
# edition metadata digests, and an independent *visual* jacket inspection.
# These four are API preview candidates only: underlying jacket copyright is
# unresolved, no binary is mirrored, and the browser must require opt-in.
# Enterprise War / cover_id 12857937 was visually an INTERIOR TITLE PAGE:
# intentionally excluded despite its valid Open Library edition metadata.
REVIEWED_OPEN_LIBRARY_COVER_PINS: dict[str, dict] = {
    "directory:literature:prh-autobiography-kirk": {
        "row_id": "directory:literature:prh-autobiography-kirk",
        "source_locator": "https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/",
        "provider": "OPEN_LIBRARY_COVERS_API", "cover_id": 13083310, "isbn": "9781783297481",
        "alt_text": "Open Library jacket preview: The Autobiography of James T. Kirk; underlying copyright unresolved",
        "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
        "edition_metadata_sha256": "dd84f9c51b9ee75de748b3ac542e74c9099d4eac0882ffcf97877fc182fb13aa",
        "attribution_url": "https://openlibrary.org/isbn/9781783297481",
        "edition_metadata_locator": "https://openlibrary.org/books/OL28813033M.json",
        "image_preview_sha256": "1aee9b2835d96e3f04ca457e3728c98e24584a80c9a07beab6cce2c2350d8ec5",
        "edition_review_receipt_path": "registry/artwork-edition-receipts/autobiography-kirk.json",
        "edition_review_receipt_sha256": "d04cf6046eea79ce29ebcf7b9cd2f176231157d78c2d2400ad6ec10f876966de",
    },
    "directory:literature:prh-autobiography-picard": {
        "row_id": "directory:literature:prh-autobiography-picard",
        "source_locator": "https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/",
        "provider": "OPEN_LIBRARY_COVERS_API", "cover_id": 10694457, "isbn": "9781785659409",
        "alt_text": "Open Library jacket preview: The Autobiography of Jean-Luc Picard; underlying copyright unresolved",
        "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
        "edition_metadata_sha256": "733e32b6e06efcca3392046968e4b34d6fa92747c223e012665aebf39df4644f",
        "attribution_url": "https://openlibrary.org/isbn/9781785659409",
        "edition_metadata_locator": "https://openlibrary.org/books/OL32028282M.json",
        "image_preview_sha256": "c9f9736af9b191e7f9e2acd69a1b1f03793940ee178870a34e0fb63957fa4121",
        "edition_review_receipt_path": "registry/artwork-edition-receipts/autobiography-picard.json",
        "edition_review_receipt_sha256": "1b0161d3e01f0486bd7d4278f3d68150c0e682ae58083e5b94359c7adc9b6ec6",
    },
    "directory:literature:prh-autobiography-janeway": {
        "row_id": "directory:literature:prh-autobiography-janeway",
        "source_locator": "https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/",
        "provider": "OPEN_LIBRARY_COVERS_API", "cover_id": 12097815, "isbn": "9781789095333",
        "alt_text": "Open Library jacket preview: The Autobiography of Kathryn Janeway; underlying copyright unresolved",
        "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
        "edition_metadata_sha256": "b70790160ac39ca865e9447684df05b45f601c3004c7a7e0d2384c23701cdf09",
        "attribution_url": "https://openlibrary.org/isbn/9781789095333",
        "edition_metadata_locator": "https://openlibrary.org/books/OL30052366M.json",
        "image_preview_sha256": "6ac504dee361e64bf5d84f6a79966e3a49d2f0827d59a809b52713ae93de81d6",
        "edition_review_receipt_path": "registry/artwork-edition-receipts/autobiography-janeway.json",
        "edition_review_receipt_sha256": "9329b0d00d9698853058832bfecb54d390cd94c15754638c55126b4435ce3e87",
    },
    "directory:literature:prh-autobiography-spock": {
        "row_id": "directory:literature:prh-autobiography-spock",
        "source_locator": "https://www.penguinrandomhouse.com/books/577045/the-autobiography-of-mr-spock-by-una-mccormack/",
        "provider": "OPEN_LIBRARY_COVERS_API", "cover_id": 11945787, "isbn": "9781785659416",
        "alt_text": "Open Library jacket preview: The Autobiography of Mr. Spock; underlying copyright unresolved",
        "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED",
        "edition_metadata_sha256": "b5b382d37755a124b0298ae86deebec1fadf1979c526ce5e47304c331892bc2d",
        "attribution_url": "https://openlibrary.org/isbn/9781785659416",
        "edition_metadata_locator": "https://openlibrary.org/books/OL33271375M.json",
        "image_preview_sha256": "6c7e699801faed04d08e8b54079ca28d6be59e464822320e7d8c1dc61dc15a3c",
        "edition_review_receipt_path": "registry/artwork-edition-receipts/autobiography-spock.json",
        "edition_review_receipt_sha256": "97a3bfe6777f61d0cdfe36295e14f3c528f63cd06f9ba57186fb019d9dd9450e",
    },
}


class ArtworkRejected(ValueError):
    """The entire optional artwork release must remain unpublished."""


def _ensure(condition: bool, reason: str) -> None:
    if not condition:
        raise ArtworkRejected(reason)


def _object(value, keys: set[str], label: str) -> dict:
    _ensure(isinstance(value, dict) and set(value) == keys, f"{label}: unexpected or missing keys")
    return value


def _sha(value) -> bool:
    return isinstance(value, str) and HASH.fullmatch(value) is not None


def _safe_https(value) -> bool:
    if not isinstance(value, str) or any(ch in value for ch in ("\\", "\n", "\r", "\t")):
        return False
    try:
        parsed = urlsplit(value)
        allowed_query = (not parsed.query or (parsed.hostname == "commons.wikimedia.org" and
                                          re.fullmatch(r"oldid=[0-9]{1,12}", parsed.query) is not None))
        return (parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and
                not parsed.password and parsed.port is None and allowed_query and not parsed.fragment and
                parsed.netloc == parsed.hostname and parsed.path.startswith("/") and
                not any(x in parsed.path.lower() for x in ("%2f", "%5c", "/../", "/./")))
    except ValueError:
        return False


def _file_bytes(root: Path, relative: str, maximum: int) -> bytes:
    """Reject links, nested symlink parents, non-regular files and oversized inputs."""
    _ensure(isinstance(relative, str) and not relative.startswith("/") and
            all(part not in ("", ".", "..") for part in relative.split("/")), "unsafe file path")
    path = root
    for part in relative.split("/"):
        path = path / part
        _ensure(not path.is_symlink(), f"symlink in release path: {relative}")
    try:
        mode = path.stat().st_mode
        _ensure(stat.S_ISREG(mode), f"not a regular release file: {relative}")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as stream:
            _ensure(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), f"non-regular release input: {relative}")
            data = stream.read(maximum + 1)
    except (OSError, OverflowError) as error:
        raise ArtworkRejected(f"release file missing or unreadable: {relative}") from error
    _ensure(len(data) <= maximum, f"oversized release file: {relative}")
    return data


def _strict_json(data: bytes, label: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _ensure(key not in result, f"{label}: duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ArtworkRejected("non-finite JSON")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ArtworkRejected(f"invalid JSON: {label}") from error


def _json_file(root: Path, relative: str, maximum=MAX_MANIFEST_BYTES):
    return _strict_json(_file_bytes(root, relative, maximum), relative)


def _source_rows(root: Path) -> dict[str, dict]:
    directory = _json_file(root, "explorer/discovery-catalog.json")
    films = _json_file(root, "explorer/film-catalog.json")
    _ensure(directory.get("data_status") == "DISCOVERY_ONLY" and directory.get("coverage_effect") == "NONE" and
            directory.get("admission_effect") == "NONE" and isinstance(directory.get("rows"), list) and
            directory.get("row_count") == len(directory["rows"]), "directory source envelope inconsistent")
    _ensure(films.get("data_status") == "DISCOVERY_ONLY" and films.get("coverage_effect") == "NONE" and
            isinstance(films.get("films"), list) and films.get("film_count") == len(films["films"]),
            "film source envelope inconsistent")
    rows: dict[str, dict] = {}
    for row in directory["rows"]:
        key = f"directory:{row.get('row_id')}" if isinstance(row, dict) else None
        _ensure(key is not None and key not in rows and isinstance(row.get("source_locator"), str),
                "invalid or duplicate source-local directory row")
        rows[key] = row
    for row in films["films"]:
        key = f"film:{row.get('id')}" if isinstance(row, dict) else None
        _ensure(key is not None and key not in rows and isinstance(row.get("source_locator"), str),
                "invalid or duplicate film row")
        rows[key] = row
    return rows


def _open_library_source_candidates(root: Path) -> dict[str, dict]:
    """Bind release pins to the accepted, still proposal-only Librarian ledger."""
    packet = _json_file(root, OL_SOURCE_PACKET)
    candidates = packet.get("candidates")
    _ensure(packet.get("data_status") == "PROPOSAL_ONLY_INDEPENDENT_ARTWORK_REVIEW_REQUIRED" and
            packet.get("accepted_work_effect") == "NONE" and packet.get("accepted_source_effect") == "NONE" and
            packet.get("accepted_binding_effect") == "NONE" and packet.get("coverage_effect") == "NONE" and
            packet.get("public_artwork_release_effect") == "NONE" and
            packet.get("image_bytes_committed") is False and
            packet.get("copyright_status") == "UNDERLYING_COVER_COPYRIGHT_UNRESOLVED" and
            packet.get("source_catalog_path") == "explorer/discovery-catalog.json" and
            isinstance(candidates, list) and packet.get("candidate_count") == len(candidates) and
            isinstance(packet.get("held"), list) and packet.get("held_count") == len(packet["held"]),
            "Open Library source packet is not an accepted provenance-only inventory")
    _ensure(packet.get("source_catalog_sha256") == hashlib.sha256(_file_bytes(
            root, "explorer/discovery-catalog.json", MAX_MANIFEST_BYTES)).hexdigest(),
            "Open Library source packet directory digest drift")
    by_row: dict[str, dict] = {}
    for candidate in candidates:
        _ensure(isinstance(candidate, dict) and isinstance(candidate.get("row_id"), str) and
                candidate["row_id"] not in by_row, "duplicate or malformed reviewed edition candidate")
        source_file = candidate.get("publisher_source_input")
        _ensure(isinstance(source_file, str) and re.fullmatch(
                r"proposals/librarian/[a-z0-9-]+/records\.json", source_file) is not None and
                candidate.get("publisher_source_sha256") == hashlib.sha256(_file_bytes(
                    root, source_file, MAX_MANIFEST_BYTES)).hexdigest(),
                "publisher edition source packet digest mismatch")
        by_row[candidate["row_id"]] = candidate
    return by_row


def _image_media(data: bytes, suffix: str) -> bool:
    # Magic checking is deliberately narrow, not a substitute for an image
    # decoder/security scanner or a license. SVG and HTML are never admitted.
    if suffix == ".png":
        return (len(data) >= 33 and data.startswith(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR") and
                int.from_bytes(data[16:20], "big") in range(1, 8193) and
                int.from_bytes(data[20:24], "big") in range(1, 8193))
    if suffix in (".jpg", ".jpeg"):
        return len(data) >= 16 and data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")
    if suffix == ".webp":
        return (len(data) >= 20 and data[:4] == b"RIFF" and data[8:12] == b"WEBP" and
                data[12:16] in (b"VP8 ", b"VP8L", b"VP8X") and
                int.from_bytes(data[4:8], "little") + 8 == len(data))
    return False


def _reviewed_receipt(root: Path, pin: dict, path_key: str, digest_key: str,
                      receipt_keys: set[str], review_status: str, candidate: dict) -> None:
    path = pin[path_key]
    _ensure(isinstance(path, str) and RECEIPT_PATH.fullmatch(path) is not None, "unapproved receipt path")
    raw = _file_bytes(root, path, 50_000)
    digest = hashlib.sha256(raw).hexdigest()
    _ensure(_sha(pin[digest_key]) and digest == pin[digest_key], "review receipt SHA-256 does not match bytes")
    receipt = _object(_strict_json(raw, path), receipt_keys, "independent review receipt")
    _ensure(receipt["schema_version"] == "1.0.0" and receipt["review_status"] == review_status,
            "review receipt has no accepted review status")
    for key, value in candidate.items():
        _ensure(receipt.get(key) == value, f"review receipt diverges on {key}")
    _ensure(isinstance(receipt.get("reviewed_on"), str) and
            re.fullmatch(r"20\d\d-\d\d-\d\d", receipt["reviewed_on"]) is not None,
            "review date absent")
    reviewers = (("rights_reviewer", "source_reviewer") if review_status == "INDEPENDENT_SOURCE_AND_RIGHTS_REVIEW"
                 else ("edition_reviewer", "source_reviewer"))
    _ensure(all(isinstance(receipt.get(key), str) and re.fullmatch(r"[a-zA-Z0-9._-]{3,80}", receipt[key])
                for key in reviewers) and receipt[reviewers[0]] != receipt[reviewers[1]],
            "independent reviewer identities absent")
    if review_status == "INDEPENDENT_EDITION_CROSSWALK_REVIEW":
        _ensure(receipt.get("image_review_status") == "COVER_IMAGE_VISUALLY_REVIEWED" and
                _sha(receipt.get("image_preview_sha256")) and
                isinstance(receipt.get("image_review_observation"), str) and
                20 <= len(receipt["image_review_observation"].strip()) <= 260 and
                isinstance(receipt.get("image_reviewer"), str) and
                re.fullmatch(r"[a-zA-Z0-9._-]{3,80}", receipt["image_reviewer"]) is not None and
                receipt["image_reviewer"] not in (receipt["edition_reviewer"], receipt["source_reviewer"]),
                "cover image not independently visually reviewed")


def _local_entry(root: Path, item: dict, row: dict, pin: dict) -> str:
    _object(item, LOCAL_KEYS, "local artwork entry")
    _object(pin, LOCAL_PIN_KEYS, "code-owned local release pin")
    for key in LOCAL_KEYS:
        _ensure(item[key] == pin[key], f"local artwork not independently pinned: {key}")
    _ensure(item["rights_status"] == "PUBLIC_DISPLAY_PERMISSION_VERIFIED" and
            item["artwork_kind"] in ARTWORK_KINDS and
            isinstance(item["attribution_text"], str) and 1 <= len(item["attribution_text"].strip()) <= 160 and
            _safe_https(item["attribution_url"]) and _safe_https(pin["rights_evidence_url"]) and
            pin["license_identifier"] in LICENSE_BASES and _sha(pin["rights_page_snapshot_sha256"]),
            "local artwork has no reviewed attribution/license/snapshot identity")
    _ensure(item["artwork_kind"] != "COVER" or row.get("medium") == "LITERATURE",
            "cover classified outside literature")
    match = IMAGE_PATH.fullmatch(item["image_path"]) if isinstance(item["image_path"], str) else None
    _ensure(match is not None and ".." not in item["image_path"], "unsafe licensed-artwork path")
    rel = f"{ART_DIRECTORY}/{match.group(1)}"
    data = _file_bytes(root, rel, MAX_ART_BYTES)
    _ensure(_image_media(data, Path(rel).suffix) and _sha(item["image_sha256"]) and
            hashlib.sha256(data).hexdigest() == item["image_sha256"],
            "licensed image media type/byte digest does not match")
    _ensure(_sha(item["rights_receipt_sha256"]), "rights review receipt digest absent")
    receipt_values = {key: pin[key] for key in ("row_id", "source_locator", "image_path", "image_sha256",
                                              "rights_page_snapshot_sha256", "rights_evidence_url",
                                              "license_identifier", "artwork_kind", "attribution_text", "attribution_url")}
    _reviewed_receipt(root, pin, "rights_receipt_path", "rights_receipt_sha256", LOCAL_RECEIPT_KEYS,
                      "INDEPENDENT_SOURCE_AND_RIGHTS_REVIEW", receipt_values)
    return rel


def _isbn_valid(isbn) -> bool:
    return (isinstance(isbn, str) and ISBN.fullmatch(isbn) is not None and
            sum((1 if i % 2 == 0 else 3) * int(digit) for i, digit in enumerate(isbn)) % 10 == 0)


def _library_entry(root: Path, item: dict, row: dict, pin: dict, source_candidate: dict) -> None:
    _object(item, OPEN_LIBRARY_KEYS, "Open Library artwork entry")
    _object(pin, OPEN_LIBRARY_PIN_KEYS, "code-owned Open Library cover pin")
    for key in OPEN_LIBRARY_KEYS:
        _ensure(item[key] == pin[key], f"Open Library crosswalk not independently pinned: {key}")
    for public_key, candidate_key in (("source_locator", "source_locator"), ("isbn", "isbn"),
                                      ("cover_id", "cover_id"),
                                      ("edition_metadata_sha256", "edition_metadata_sha256"),
                                      ("attribution_url", "attribution_url"),
                                      ("rights_status", "rights_status")):
        _ensure(item[public_key] == source_candidate.get(candidate_key),
                f"Open Library release diverges from accepted candidate {candidate_key}")
    _ensure(source_candidate.get("row_id") == item["row_id"].removeprefix("directory:") and
            source_candidate.get("openlibrary_edition_json_url") == pin["edition_metadata_locator"] and
            source_candidate.get("release_status") == "HELD_FOR_INDEPENDENT_REVIEW",
            "Open Library release has no matching independently checked source candidate")
    isbn = item["isbn"]
    _ensure(row.get("medium") == "LITERATURE" and item["provider"] == "OPEN_LIBRARY_COVERS_API" and
            item["rights_status"] == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" and
            type(item["cover_id"]) is int and 1 <= item["cover_id"] <= 999_999_999 and
            _isbn_valid(isbn) and _sha(item["edition_metadata_sha256"]) and
            item["attribution_url"] == f"https://openlibrary.org/isbn/{isbn}",
            "Open Library edition/API identity invalid")
    details = row.get("details")
    _ensure(isinstance(details, list) and any(isinstance(detail, str) and
            (re.fullmatch(r"[A-Za-z][A-Za-z -]{0,56} · ISBN (97[89][0-9]{10})", detail) or
             re.fullmatch(r"(?:Paperback|Hardcover|Trade Paperback|Ebook) ISBN (97[89][0-9]{10})", detail)) and
            detail.endswith(isbn) for detail in details), "cover ISBN not in publisher source-local edition details")
    locator = row.get("source_locator", "")
    if row.get("source_group") == "publisher:simonandschuster.com":
        _ensure(re.fullmatch(r"https://www\.simonandschuster\.com/books/[^?\#]+/" + isbn, locator) is not None,
                "Simon & Schuster URL does not identify same edition ISBN")
    elif row.get("source_group") == "distributor:penguinrandomhouse.com:titan-books":
        _ensure(row.get("candidate_kind") == "FICTIONAL_MEMOIR" and
                re.fullmatch(r"https://www\.penguinrandomhouse\.com/books/[0-9]+/[a-z0-9-]+/", locator) is not None and
                f"Paperback ISBN {isbn}" in details, "PRH/Titan book edition scope mismatch")
    else:
        raise ArtworkRejected("unreviewed literary publisher/source group")
    metadata_locator = pin["edition_metadata_locator"]
    _ensure(isinstance(metadata_locator, str) and
            re.fullmatch(r"https://openlibrary\.org/books/OL[0-9]+M\.json", metadata_locator) is not None,
            "Open Library raw edition metadata locator unreviewed")
    candidate = {key: pin[key] for key in ("row_id", "source_locator", "isbn", "cover_id",
                                            "edition_metadata_sha256", "edition_metadata_locator",
                                            "image_preview_sha256")}
    _reviewed_receipt(root, pin, "edition_review_receipt_path", "edition_review_receipt_sha256",
                      OPEN_LIBRARY_RECEIPT_KEYS, "INDEPENDENT_EDITION_CROSSWALK_REVIEW", candidate)


def validate_manifest(root: Path = ROOT, *, local_pins=None, library_pins=None,
                      verify_git: bool = False) -> dict:
    """Use code-owned pins in CLI; explicit test-only injections exercise release fixtures."""
    root = Path(root)
    local_pins = REVIEWED_LOCAL_ARTWORK_PINS if local_pins is None else local_pins
    library_pins = REVIEWED_OPEN_LIBRARY_COVER_PINS if library_pins is None else library_pins
    manifest = root / MANIFEST
    if not manifest.exists() and not manifest.is_symlink():
        if verify_git:
            committed = subprocess.run(["git", "cat-file", "-e", f"HEAD:{MANIFEST}"], cwd=root,
                                       capture_output=True, check=False)
            _ensure(committed.returncode != 0, "committed artwork catalog missing from release")
        _ensure(not (root / ART_DIRECTORY).exists() and not (root / ART_DIRECTORY).is_symlink(),
                "orphaned licensed artwork without a release sidecar")
        return {"status": "ARTWORK_UNAVAILABLE", "artwork_count": 0, "coverage_effect": "NONE"}
    data = _object(_json_file(root, MANIFEST), ROOT_KEYS, "artwork sidecar")
    entries = data["artwork"]
    _ensure(data["schema_version"] == "1.2.0" and data["data_status"] == "PROVENANCE_REVIEWED_ARTWORK" and
            data["coverage_effect"] == "NONE" and data["rights_policy"] == "PER_ENTRY_DISPLAY_GATE" and
            isinstance(entries, list) and 1 <= len(entries) <= 5000 and type(data["artwork_count"]) is int and
            data["artwork_count"] == len(entries), "artwork sidecar envelope not an authorized release")
    rows = _source_rows(root)
    seen: set[str] = set()
    used_files: set[str] = set()
    used_receipts: set[str] = set()
    ol_candidates = (_open_library_source_candidates(root) if any(
        isinstance(item, dict) and item.get("provider") == "OPEN_LIBRARY_COVERS_API" for item in entries) else {})
    for item in entries:
        _ensure(isinstance(item, dict), "artwork entry is not an object")
        row_id = item.get("row_id")
        _ensure(isinstance(row_id, str) and row_id in rows and row_id not in seen,
                "unknown or duplicate artwork source-local row")
        row = rows[row_id]
        _ensure(item.get("source_locator") == row["source_locator"] and
                isinstance(item.get("alt_text"), str) and item["alt_text"].strip() and
                len(item["alt_text"]) <= 180,
                "artwork source locator or alternate text mismatch")
        if item.get("provider") == "OPEN_LIBRARY_COVERS_API":
            pin = library_pins.get(row_id)
            _ensure(pin is not None, "Open Library cover lacks separately reviewed edition receipt")
            candidate = ol_candidates.get(row_id.removeprefix("directory:"))
            _ensure(candidate is not None, "Open Library cover absent from accepted source candidates")
            _library_entry(root, item, row, pin, candidate)
            used_receipts.add(pin["edition_review_receipt_path"])
        else:
            pin = local_pins.get(row_id)
            _ensure(pin is not None, "same-origin art lacks separately reviewed license/asset receipt")
            used_files.add(_local_entry(root, item, row, pin))
            used_receipts.add(pin["rights_receipt_path"])
        seen.add(row_id)
    art_dir = root / ART_DIRECTORY
    if art_dir.exists() or art_dir.is_symlink():
        _ensure(art_dir.is_dir() and not art_dir.is_symlink(), "unsafe licensed artwork directory")
        actual = set()
        for file in art_dir.iterdir():
            _ensure(not file.is_symlink() and file.is_file(), "unexpected licensed-artwork directory or special file")
            actual.add(file.relative_to(root).as_posix())
        _ensure(actual == used_files, "unlisted or missing licensed image in public artifact")
    else:
        _ensure(not used_files, "licensed artwork files missing")
    if verify_git:
        for rel in sorted({MANIFEST, "tools/validate_artwork_release.py", "explorer/app.css",
                           "explorer/index.html", *used_files, *used_receipts}):
            expected = subprocess.run(["git", "rev-parse", f"HEAD:{rel}"], cwd=root,
                                      capture_output=True, text=True, check=False)
            actual = subprocess.run(["git", "hash-object", rel], cwd=root,
                                    capture_output=True, text=True, check=False)
            _ensure(expected.returncode == 0 and actual.returncode == 0 and
                    expected.stdout.strip() == actual.stdout.strip(), f"uncommitted artwork bytes: {rel}")
    return {"status": "REVIEWED_ARTWORK_READY_FOR_SEPARATE_UI_RELEASE", "artwork_count": len(entries),
            "coverage_effect": "NONE"}


ALLOWED_CSS_ASSETS = {f"./art-original-{kind}.svg" for kind in
                      ("episode", "film", "literature", "short-form", "audio")}


def check_css_no_pre_opt_in_network(css: str) -> None:
    # The browser CSP allows Open Library images after opt-in; CSS must never
    # use that allowance to fetch art automatically on page startup.
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    _ensure("\\" not in clean and re.search(r"@import\b|image-set\s*\(|@font-face\b", clean,
                                            re.IGNORECASE) is None,
            "CSS imports or escaped URLs can bypass artwork opt-in")
    matches = list(re.finditer(r"url\s*\(([^)]*)\)", clean, re.IGNORECASE))
    _ensure(len(matches) == len(re.findall(r"\burl\b", clean, re.IGNORECASE)), "malformed CSS URL")
    for match in matches:
        src = match.group(1).strip().strip("\"'")
        _ensure(src in ALLOWED_CSS_ASSETS, "CSS pre-opt-in image/network URL not explicitly allowlisted")


class _StartupHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        _ensure(len(values) == len(attrs), "duplicate HTML attributes")
        if tag in ("base", "iframe", "object", "embed", "source", "video", "audio", "image",
                   "picture", "use", "feimage", "canvas"):
            raise ArtworkRejected("unreviewed network-capable HTML element")
        if tag == "svg" and ("href" in values or "xlink:href" in values):
            raise ArtworkRejected("SVG external resource references denied")
        if tag == "style":
            self.in_style = True
        if "style" in values:
            check_css_no_pre_opt_in_network(values["style"])
        if any(name.startswith("on") for name in values):
            raise ArtworkRejected("unreviewed HTML inline event handler")
        if "srcset" in values or "poster" in values or "background" in values:
            raise ArtworkRejected("unreviewed HTML image resource attribute")
        if "src" in values and tag not in ("img", "script"):
            raise ArtworkRejected("unreviewed HTML resource source")
        if tag == "link":
            _ensure(values.get("rel") == "stylesheet" and
                    re.fullmatch(r"\./app\.css\?v=[a-f0-9]{64}", values.get("href", "")) is not None,
                    "unexpected HTML preloading or stylesheet URL")
        if tag == "script":
            _ensure(re.fullmatch(r"\./app\.js\?v=[a-f0-9]{64}", values.get("src", "")) is not None,
                    "unexpected script URL")
        if tag == "img":
            _ensure(re.fullmatch(r"\./trek-data-core-hero\.jpg\?v=[a-f0-9]{64}", values.get("src", "")) is not None and
                    "srcset" not in values, "unreviewed pre-opt-in HTML image source")
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            raise ArtworkRejected("automatic HTML redirect/preload denied")

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            check_css_no_pre_opt_in_network(data)


def check_static_startup(root: Path = ROOT) -> None:
    check_css_no_pre_opt_in_network(_file_bytes(root, "explorer/app.css", 600_000).decode("utf-8"))
    html = _file_bytes(root, "explorer/index.html", 200_000).decode("utf-8")
    parser = _StartupHTML()
    parser.feed(html)
    parser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Require a safe absent or exact reviewed release")
    parser.add_argument("--verify-git", action="store_true", help="Also require committed manifest and image bytes")
    args = parser.parse_args()
    try:
        check_static_startup(ROOT)
        report = validate_manifest(ROOT, verify_git=args.verify_git)
    except (ArtworkRejected, OSError, UnicodeError) as error:
        print(f"ARTWORK_RELEASE_REJECTED: {error}")
        return 1
    print(f"{report['status']}: {report['artwork_count']} items; coverage_effect NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
