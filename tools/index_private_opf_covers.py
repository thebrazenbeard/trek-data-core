#!/usr/bin/env python3
"""Identify candidate cover files from private OPF ZIPs without publishing images.

Only small OPF XML members and bounded candidate image bytes are read. Text,
HTML chapters, and other non-image ebook payloads are never opened. The JSON
report is private, owner-only, and cannot be written inside the public repo.
OPF claims, filename hints and ownership/display permissions remain distinct.
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
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import inventory_opf_metadata as intake


MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_IMAGE_BYTES = 512 * 1024 * 1024
MAX_TOTAL_ARCHIVE_BYTES = 8 * 1024 * 1024 * 1024
MAX_CANDIDATES_PER_PACKAGE = 32
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
IMAGE_MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif",
}
OPF_NAMESPACES = {"", "http://www.idpf.org/2007/opf",
                  "http://openebook.org/namespaces/oeb-package/1.0/"}
HINT_RE = re.compile(
    r"(?:^|[^a-z0-9])(?:cover\d*|frontcover\d*|jacket\d*|front|cov\d{2,})(?:$|[^a-z0-9])"
)


class CoverIntakeError(intake.IntakeError):
    """A private-cover inventory cannot safely proceed."""


def member_index(archive: ZipFile) -> dict[str, ZipInfo]:
    try:
        members = intake.safe_members(archive)
    except intake.IntakeError as exc:
        raise CoverIntakeError(str(exc)) from exc
    if sum(item.file_size for item in members) > MAX_TOTAL_ARCHIVE_BYTES:
        raise CoverIntakeError("archive uncompressed size exceeds hard limit")
    index: dict[str, ZipInfo] = {}
    normalized: set[str] = set()
    for item in members:
        name = item.filename
        parts = name.rstrip("/").split("/")
        if (not parts or any(part in ("", ".", "..") for part in parts)
                or ":" in parts[0] or any(ord(ch) < 32 for ch in name)):
            raise CoverIntakeError("archive contains noncanonical or unsafe member path")
        folded = unicodedata.normalize("NFKC", name.rstrip("/")).casefold()
        if folded in normalized:
            raise CoverIntakeError("archive contains Unicode/case-colliding member paths")
        normalized.add(folded)
        if item.flag_bits & 0x1:
            raise CoverIntakeError("encrypted ZIP members cannot be independently inventoried")
        if stat.S_ISLNK(item.external_attr >> 16):
            raise CoverIntakeError("archive contains symbolic-link member")
        index[name] = item
    return index


def parse_opf(raw: bytes) -> tuple[ET.Element, dict, bool]:
    metadata, legacy = intake.opf_metadata_with_legacy_review(raw)
    repaired = raw
    if legacy:
        repaired = raw.replace(
            b"<dc-metadata>",
            b'<dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core">',
            1,
        )
    scrubbed = intake.DOCTYPE.sub(b"", repaired, count=1)
    if (b"\x00" in scrubbed or b"<!DOCTYPE" in scrubbed.upper()
            or b"<!ENTITY" in scrubbed.upper() or b"<![" in scrubbed.upper()):
        raise CoverIntakeError("OPF contains unsafe XML markup")
    try:
        root = ET.fromstring(scrubbed)
    except ET.ParseError as exc:
        raise CoverIntakeError("OPF cover XML is not safely parseable") from exc
    return root, metadata, legacy


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def qname_namespace(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def signature_mime(header: bytes) -> str | None:
    """File signature only, not proof of a fully decodable or licensed image."""
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    return None


def image_member(opf_name: str, href: str) -> str:
    """Resolve an image href with no path traversal, network or URI support."""
    if not href or len(href) > 1024:
        raise CoverIntakeError("missing or excessively long OPF cover href")
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or parts.query or parts.fragment:
        raise CoverIntakeError("OPF cover href is external or contains URL components")
    try:
        decoded = unquote(parts.path, encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        raise CoverIntakeError("OPF cover href is not valid UTF-8") from exc
    path = PurePosixPath(decoded)
    if (path.is_absolute() or "\\" in decoded or "\x00" in decoded
            or any(piece in ("", ".", "..") for piece in decoded.split("/"))
            or ":" in decoded.split("/")[0]):
        raise CoverIntakeError("OPF cover href contains unsafe path traversal")
    return str(PurePosixPath(opf_name).parent / path)


def classify_package(opf_info: ZipInfo, raw: bytes, index: dict[str, ZipInfo], archive: ZipFile,
                     image_budget: list[int]) -> dict:
    record = {
        "opf_member": opf_info.filename,
        "opf_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "REVIEW_REQUIRED",
        "canonical_work_id": None,
        "rights_status": "PUBLIC_DISPLAY_RIGHTS_NOT_ESTABLISHED",
        "metadata": None,
        "selected_cover_member": None,
        "candidates": [],
        "review_holds": [],
    }
    try:
        root, metadata, legacy = parse_opf(raw)
    except intake.IntakeError as exc:
        record["review_holds"].append(str(exc))
        return record
    record["metadata"] = metadata
    if legacy:
        record["review_holds"].append("legacy XML namespace repair required review")

    manifest: dict[str, tuple[str, str, str]] = {}
    declared_media: dict[str, set[str]] = {}
    cover_ids: set[str] = set()
    guide_refs: list[str] = []
    explicit: dict[str, set[str]] = {}
    namespace = qname_namespace(root.tag)
    if namespace not in OPF_NAMESPACES:
        record["review_holds"].append("OPF package namespace is not recognized")
        return record
    q = lambda part: f"{{{namespace}}}{part}" if namespace else part
    # Only exact OPF-namespace direct section children count. A same-local-name
    # element in metadata, an extension namespace, or an arbitrary descendant
    # is never allowed to forge a cover-image manifest assertion.
    for section in root:
        if section.tag == q("manifest"):
            for element in section:
                if element.tag != q("item"):
                    continue
                key = element.get("id", "")
                href = element.get("href", "")
                mime = element.get("media-type", "")
                properties = element.get("properties", "").split()
                if key and href:
                    if key in manifest and manifest[key] != (href, mime, " ".join(properties)):
                        raise CoverIntakeError("duplicate OPF manifest item ids")
                    manifest[key] = (href, mime, " ".join(properties))
                    if mime:
                        declared_media.setdefault(href, set()).add(mime.casefold())
                    if "cover-image" in properties:
                        explicit.setdefault(href, set()).add("OPF3_COVER_IMAGE_PROPERTY")
        elif section.tag == q("metadata"):
            for element in section:
                if (element.tag == q("meta") and
                        element.get("name", "").casefold() == "cover" and
                        element.get("content")):
                    cover_ids.add(element.get("content"))
        elif section.tag == q("guide"):
            for element in section:
                if (element.tag == q("reference") and
                        element.get("type", "").casefold() == "cover" and
                        element.get("href")):
                    guide_refs.append(element.get("href"))
    for key in sorted(cover_ids):
        if key not in manifest:
            record["review_holds"].append("OPF meta cover id missing from manifest")
        else:
            explicit.setdefault(manifest[key][0], set()).add("OPF2_META_COVER_ID")
    for href in guide_refs:
        if PurePosixPath(urlsplit(href).path).suffix.lower() in IMAGE_EXTENSIONS:
            explicit.setdefault(href, set()).add("OPF_GUIDE_DIRECT_IMAGE")
        else:
            record["review_holds"].append("OPF guide points to cover page/non-image; page not opened")

    package_dir = PurePosixPath(opf_info.filename).parent
    hinted = [name for name, item in index.items()
              if not item.is_dir() and PurePosixPath(name).parent == package_dir
              and PurePosixPath(name).suffix.lower() in IMAGE_EXTENSIONS
              and (HINT_RE.search(PurePosixPath(name).stem.casefold())
                   or PurePosixPath(name).stem.casefold().endswith("msrcover"))]
    refs: dict[str, set[str]] = {}
    resolved_media: dict[str, set[str]] = {}
    for href, reasons in explicit.items():
        # Reject unsafe hrefs even if their targets do not exist.
        target = image_member(opf_info.filename, href)
        refs.setdefault(target, set()).update(reasons)
        resolved_media.setdefault(target, set()).update(declared_media.get(href, set()))
    for name in hinted:
        refs.setdefault(name, set()).add("FILENAME_HINT_ONLY")
    if len(refs) > MAX_CANDIDATES_PER_PACKAGE:
        raise CoverIntakeError("excessive cover candidates in one OPF package")

    explicit_targets = {name for name, reasons in refs.items()
                        if any(reason != "FILENAME_HINT_ONLY" for reason in reasons)}
    hinted_targets = {name for name, reasons in refs.items() if "FILENAME_HINT_ONLY" in reasons}
    if len(explicit_targets) > 1:
        record["review_holds"].append("conflicting explicit OPF cover references")
        record["status"] = "AMBIGUOUS_EXPLICIT_REFERENCES"
    elif explicit_targets:
        record["status"] = "EXPLICIT_OPF_REFERENCE_UNVERIFIED"
    elif len(hinted_targets) > 1:
        record["status"] = "AMBIGUOUS_FILENAME_HINTS"
    elif hinted_targets:
        record["status"] = "FILENAME_HINT_UNVERIFIED"
    else:
        record["status"] = "NO_DIRECT_IMAGE_COVER_REFERENCE"

    for name in sorted(refs):
        info = index.get(name)
        candidate = {
            "private_member_locator": name,
            "evidence_basis": sorted(refs[name]),
            "image_sha256": None,
            "image_bytes": None,
            "asset_status": "UNRESOLVED",
        }
        if info is None or info.is_dir():
            candidate["asset_status"] = "MISSING_REFERENCED_IMAGE"
            if name in explicit_targets:
                record["review_holds"].append("explicit OPF image reference missing")
        elif PurePosixPath(name).suffix.lower() not in IMAGE_EXTENSIONS:
            candidate["asset_status"] = "NON_IMAGE_REFERENCE"
        elif any(not mime.startswith("image/") for mime in resolved_media.get(name, set())):
            candidate["asset_status"] = "OPF_MEDIA_TYPE_CONFLICT_REVIEW"
            record["review_holds"].append("OPF manifest media type conflicts with image file extension")
        elif info.file_size > MAX_IMAGE_BYTES:
            candidate["asset_status"] = "IMAGE_SIZE_LIMIT_REVIEW"
            record["review_holds"].append("candidate image exceeds per-image limit")
        else:
            if image_budget[0] + info.file_size > MAX_TOTAL_IMAGE_BYTES:
                raise CoverIntakeError("aggregate candidate image bytes exceed safety budget")
            digest = hashlib.sha256()
            actual = 0
            header = b""
            with archive.open(info) as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    if not header:
                        header = chunk[:16]
                    actual += len(chunk)
                    if actual > MAX_IMAGE_BYTES:
                        raise CoverIntakeError("image decompressed beyond safety limit")
                    digest.update(chunk)
            if actual != info.file_size:
                raise CoverIntakeError("candidate image size changed during read")
            image_budget[0] += actual
            actual_mime = signature_mime(header)
            expected_mime = IMAGE_MIME[PurePosixPath(name).suffix.lower()]
            if actual_mime != expected_mime:
                candidate["asset_status"] = "IMAGE_SIGNATURE_MISMATCH_REVIEW"
                record["review_holds"].append("candidate image signature differs from extension")
            elif any(mime != actual_mime for mime in resolved_media.get(name, set())):
                candidate["asset_status"] = "OPF_MEDIA_TYPE_CONFLICT_REVIEW"
                record["review_holds"].append("OPF media type differs from detected image signature")
            else:
                candidate.update(image_sha256=digest.hexdigest(), image_bytes=actual,
                                 asset_status="PRIVATE_IMAGE_HASHED_UNVERIFIED_COVER")
        record["candidates"].append(candidate)
    if len(explicit_targets) == 1 and not record["review_holds"]:
        only = next(iter(explicit_targets))
        if any(row["private_member_locator"] == only and
               row["asset_status"] == "PRIVATE_IMAGE_HASHED_UNVERIFIED_COVER"
               for row in record["candidates"]):
            record["selected_cover_member"] = only
    return record


def build_cover_index(path: Path) -> dict:
    if not path.is_file() or path.is_symlink() or not hasattr(os, "O_NOFOLLOW"):
        raise CoverIntakeError("OPF ZIP must be an existing regular non-symlink file")
    records: list[dict] = []
    image_budget = [0]
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as source:
        starting = os.fstat(source.fileno())
        if not stat.S_ISREG(starting.st_mode):
            raise CoverIntakeError("source ZIP is not a regular file")
        with ZipFile(source) as archive:
            index = member_index(archive)
            opfs = sorted((entry for entry in index.values() if not entry.is_dir()
                           and PurePosixPath(entry.filename).suffix.lower() == ".opf"),
                          key=lambda entry: entry.filename.casefold())
            if sum(item.file_size for item in opfs) > intake.MAX_TOTAL_OPF:
                raise CoverIntakeError("OPF metadata aggregate exceeds safe limit")
            for opf in opfs:
                if opf.file_size > intake.MAX_OPF:
                    records.append({"opf_member": opf.filename, "status": "OPF_SIZE_LIMIT_REVIEW",
                                    "selected_cover_member": None, "candidates": [],
                                    "review_holds": ["OPF exceeds per-file limit"]})
                    continue
                with archive.open(opf) as stream:
                    raw = stream.read(intake.MAX_OPF + 1)
                if len(raw) > intake.MAX_OPF:
                    raise CoverIntakeError("OPF decompressed beyond metadata limit")
                records.append(classify_package(opf, raw, index, archive, image_budget))
        # Hash exactly the same opened file descriptor that supplied every
        # member. Reopening by pathname could falsely receipt a swapped ZIP.
        source.seek(0)
        source_digest = hashlib.sha256()
        for block in iter(lambda: source.read(1024 * 1024), b""):
            source_digest.update(block)
        ending = os.fstat(source.fileno())
        if (starting.st_dev, starting.st_ino, starting.st_size, starting.st_mtime_ns,
                starting.st_ctime_ns) != (ending.st_dev, ending.st_ino, ending.st_size,
                                          ending.st_mtime_ns, ending.st_ctime_ns):
            raise CoverIntakeError("source ZIP changed during private indexing")
    return {
        "schema_version": "0.1.0",
        "proposal_only": True,
        "public_artwork_release_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "accepted_work_effect": "NONE",
        "coverage_effect": "NONE",
        "rights_status": "PRIVATE_POSSESSION_NOT_PUBLIC_DISPLAY_PERMISSION",
        "input_archive_sha256": source_digest.hexdigest(),
        "summary": {
            "opf_packages": len(records),
            "explicit_link_candidates": sum(row["status"] == "EXPLICIT_OPF_REFERENCE_UNVERIFIED" for row in records),
            "filename_hint_candidates": sum(row["status"] == "FILENAME_HINT_UNVERIFIED" for row in records),
            "ambiguous_packages": sum(row["status"].startswith("AMBIGUOUS_") for row in records),
            "packages_with_review_holds": sum(bool(row.get("review_holds")) for row in records),
            "private_images_hashed": sum(c["image_sha256"] is not None for row in records
                                         for c in row["candidates"]),
        },
        "packages": records,
    }


def private_cover_output_path(path: Path) -> Path:
    """Reject output in *any* Git checkout, not just this source worktree."""
    target = intake.private_output_path(path)
    for ancestor in (target.parent, *target.parents):
        marker = ancestor / ".git"
        if (marker.is_symlink() or marker.is_file()
                or (marker.is_dir() and (marker / "HEAD").is_file())):
            raise CoverIntakeError("private artwork report must be outside every Git checkout")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opf-zip", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True,
                        help="new owner-only private JSON outside the public checkout")
    args = parser.parse_args()
    try:
        target = private_cover_output_path(args.out)
        parent_fd = intake.open_private_output_parent(target)
        try:
            index = build_cover_index(args.opf_zip)
            payload = json.dumps(index, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
            pinned = os.fstat(parent_fd)
            current = os.stat(target.parent, follow_symlinks=False)
            if (pinned.st_dev, pinned.st_ino) != (current.st_dev, current.st_ino):
                raise CoverIntakeError("private output parent changed during indexing")
            fd = os.open(target.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent_fd)
            with os.fdopen(fd, "w", encoding="utf-8", errors="strict") as out:
                out.write(payload)
        finally:
            os.close(parent_fd)
    except (intake.IntakeError, BadZipFile, OSError, ValueError) as exc:
        print(f"Private cover indexing refused: {exc}", file=sys.stderr)
        return 1
    summary = index["summary"]
    print(f"PRIVATE COVER CANDIDATES: {summary['opf_packages']} packages, "
          f"{summary['explicit_link_candidates']} explicit-reference packages, "
          f"{summary['filename_hint_candidates']} filename-only packages, "
          f"{summary['ambiguous_packages']} ambiguous, "
          f"{summary['packages_with_review_holds']} holds; "
          "no public artwork, no Work/coverage advancement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
