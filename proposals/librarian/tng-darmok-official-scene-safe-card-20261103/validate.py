#!/usr/bin/env python3
"""Fail-closed source-local TNG scene visual identity and original-card custody."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
FILES = {"records.json", "MANIFEST.md", "title-card.svg", "validate.py", "test_validate.py"}
MAX_TEXT_BYTES = 200_000
EXPECTED_RECORD_FINGERPRINT = "06089464ce8760e43f9d4503ce0bcc1745f92e08fda0bacc24b1a42230d952c2"
EXPECTED_MANIFEST_SHA = "ebd36f36162400b0eab49b476db26730705519257c6f6da6cca818118ffe6b0c"
EXPECTED_CARD_SHA = "90551de489db4b646ef7719278a71229e775b4a6cc984c7d7d93c211ca163ed3"


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path: Path = RECORDS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid {value}")))


def verify_text(path: Path) -> None:
    require(path.is_file() and path.stat().st_size <= MAX_TEXT_BYTES, "oversize or invalid packet text")
    data = path.read_bytes()
    magics = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF" + b"87a", b"GIF" + b"89a",
              b"%" + b"PDF", b"PK\x03\x04")
    require(not any(magic in data for magic in magics), "binary payload in source-only packet")
    try:
        decoded = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise ValueError("non-UTF8 packet file") from exc
    require("\x00" not in decoded and not any(ord(c) < 32 and c not in "\t\n\r" for c in decoded),
            "control bytes in text")
    if path.suffix.lower() in {".md", ".json", ".svg"}:
        lowered = decoded.lower()
        require(not any(marker in lowered for marker in ("data:" + "image/", "<!" + "doctype",
                                                          "<" + "script", "<" + "image", "<" + "foreignobject")),
                "embedded active/external image markup")


def verify_packet_files(directory: Path = HERE, root: Path = ROOT) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "invalid proposal directory")
    for p in directory.rglob("*"):
        rel = p.relative_to(directory)
        require(not p.is_symlink(), "symlink inside source packet")
        if p.is_dir():
            require(rel.parts == ("__pycache__",), "unreviewed nested directory")
            continue
        if p.is_file() and len(rel.parts) == 1 and p.name in FILES:
            verify_text(p)
            continue
        if p.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and p.suffix == ".pyc":
            continue
        raise ValueError("unexpected source packet file")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "missing allowed file")
    if directory == HERE:
        prefix = HERE.relative_to(root).as_posix() + "/"
        p = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=root, capture_output=True,
                           text=True, timeout=10, check=False)
        require(p.returncode == 0, "tracked-file inventory unavailable")
        require(set(p.stdout.splitlines()) == {prefix + name for name in FILES},
                "unreviewed committed image or file")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == EXPECTED_MANIFEST_SHA,
            "unreviewed manifest or false image-caption rights text")
    card = (directory / "title-card.svg").read_bytes()
    require(hashlib.sha256(card).hexdigest() == EXPECTED_CARD_SHA, "unreviewed SVG visual")
    try:
        svg = ET.fromstring(card)
    except ET.ParseError as exc:
        raise ValueError("malformed SVG") from exc
    ns = "{http://www.w3.org/2000/svg}"
    require(svg.tag == ns + "svg", "not inline SVG root")
    require(svg.attrib.get("viewBox") == "0 0 960 540", "original card dimensions changed")
    for element in svg.iter():
        require(element.tag in {ns + name for name in ("svg", "title", "desc", "rect", "text")},
                "unreviewed media/foreign/script SVG element")
        require(not any("href" in key.lower() or key.lower().startswith("on") for key in element.attrib),
                "external or event SVG attribute")


def validate(packet: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(packet) is dict, "not a JSON object")
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    require(digest == EXPECTED_RECORD_FINGERPRINT, "unreviewed rights/identity/coverage record change")
    expected_catalog = packet["discovery_catalog_sha256"]
    catalog_bytes = (root / packet["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(catalog_bytes).hexdigest() == expected_catalog, "discovery source drift")
    rows = [r for r in json.loads(catalog_bytes)["rows"] if r.get("row_id") == packet["source_local_episode_row_id"]]
    require(len(rows) == 1, "source-local episode row missing or duplicate")
    row = rows[0]
    require((row["title"], row["context"], row["verification_status"], row["admission_effect"],
             row["coverage_effect"]) == ("Darmok", "TNG S5E2", "UNVERIFIED_METADATA", "NONE", "NONE"),
            "source-local row no longer matches accepted main")
    image = packet["actual_scene_candidate"]
    require(image["publisher_embedded_image_url"] ==
            "https://images.prismic.io/star-trek-untold/ZrrC_EaF0TcGI4Q-_darmok-hd-236.jpg?auto=format%2Ccompress" and
            image["publisher_embedded_image_bytes"] == 113141 and
            image["publisher_embedded_image_sha256"] ==
            "f627a83a50d06333fd1c5a7d673df0002905da32ce0f3dbd96605429e2b17676",
            "exact published transformed JPEG variant mismatch")
    require(image["source_image_variant"] == "SAME_PRISMIC_IMAGE_PATH_WITHOUT_AUTO_FORMAT_COMPRESS_QUERY" and
            image["image_bytes"] == 321843 and image["image_sha256"] ==
            "a7a8ac3ef4ad18d4dcd003b53ac3f0ff73a7c0b49c2c3730f1fffd07bce8ab8c",
            "untransformed publisher JPEG variant mismatch")
    require(image["visual_class"] == "FIRST_PARTY_EDITORIAL_EPISODE_STILL_REUSE_PERMISSION_UNVERIFIED",
            "unwarranted conclusion about photo reuse permission")
    require(image["public_image_display_admission"] == "HELD_NO_AFFIRMATIVE_REUSE_LICENSE",
            "unlicensed image release")
    require(image["verified_broadcast_frame"] is False and image["individual_photographer"] ==
            "UNKNOWN_NOT_ESTABLISHED", "invented screenshot origin or photographer")
    require(image["press_express_authorized_user_status"] == "NOT_ESTABLISHED" and
            image["press_express_terms_apply_as_grant_to_this_article_image"] is False,
            "invalid conditional Press Express license elevation")
    require(packet["image_binary_committed"] is False and packet["explorer_effect"] == "NONE" and
            packet["coverage_effect"] == "NONE" and packet["global_work_admission_effect"] == "NONE",
            "protected effect escalation")
    safe = packet["safe_placeholder"]
    require(safe["contains_official_episode_pixels"] is False and
            safe["proposed_public_display_release"] == "NONE_SOURCE_LOCAL_REVIEW_ONLY",
            "held episode pixels or premature public release")
    verify_packet_files(directory, root)


if __name__ == "__main__":
    validate(load())
    print("PASS: official Darmok scene still identified, reuse held; original card source packet validated")
