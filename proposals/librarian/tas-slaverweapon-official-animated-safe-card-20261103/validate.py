#!/usr/bin/env python3
"""Fail-closed gate for a TAS publisher scene URL; only an original card may stage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORD = HERE / "records.json"
FILES = {"MANIFEST.md", "records.json", "title-card.svg", "validate.py", "test_validate.py"}
MANIFEST_SHA = "1c02a61cc0204b7ab4630e603a65d88897f6b3fc842786443031aaffb02e3e6f"
CARD_SHA = "4e1addc4ae969932a08739add952213953883c998300a14257cbf104c81a6ec8"
RECORD_FINGERPRINT = "0e3b6c7bd225311d2d39bba78e64d985b93fa2f535056ae79e64a7ab259dd4a4"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    data = {}
    for key, value in pairs:
        require(key not in data, "duplicate source metadata key")
        data[key] = value
    return data


def load(path: Path = RECORD) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def text_guard(path: Path) -> None:
    require(path.is_file() and path.stat().st_size <= 150_000, "missing/oversized packet text")
    blob = path.read_bytes()
    require(not any(magic in blob for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n",
                                                 b"GIF" + b"87a", b"GIF" + b"89a", b"%" + b"PDF",
                                                 b"PK\x03\x04")), "hidden binary payload")
    try:
        text = blob.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid UTF-8 packet text") from exc
    require("\x00" not in text and not any(ord(c) < 32 and c not in "\n\r\t" for c in text),
            "hidden control character")
    if path.suffix in {".md", ".svg", ".json"}:
        folded = text.lower()
        require(not any(token in folded for token in ("data:" + "image/", "<!" + "doctype",
                                                      "<" + "script", "<" + "image",
                                                      "<" + "foreignobject")),
                "embedded data URI, active element, or image reference")


def file_inventory(directory: Path = HERE) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "invalid packet directory")
    for entry in directory.rglob("*"):
        rel = entry.relative_to(directory)
        require(not entry.is_symlink(), "symlink in packet")
        if entry.is_dir():
            require(rel.parts == ("__pycache__",), "nested source directory or binary smuggling")
            continue
        if entry.is_file() and len(rel.parts) == 1 and entry.name in FILES:
            text_guard(entry)
            continue
        if entry.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and entry.suffix == ".pyc":
            continue
        raise ValueError("unreviewed packet file")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "flat five-file packet required")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        result = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
                                capture_output=True, text=True, timeout=10, check=False)
        require(result.returncode == 0 and set(result.stdout.splitlines()) ==
                {prefix + item for item in FILES}, "unreviewed tracked files or image")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == MANIFEST_SHA,
            "rights prose or publisher caption changed")
    card = (directory / "title-card.svg").read_bytes()
    require(hashlib.sha256(card).hexdigest() == CARD_SHA, "original reference card changed")
    try:
        image = ET.fromstring(card)
    except ET.ParseError as exc:
        raise ValueError("invalid SVG") from exc
    namespace = "{http://www.w3.org/2000/svg}"
    require(image.tag == namespace + "svg" and image.get("viewBox") == "0 0 960 540",
            "not approved card size")
    for node in image.iter():
        require(node.tag in {namespace + tag for tag in ("svg", "title", "desc", "rect", "text")},
                "unapproved SVG media/content node")
        require(not any("href" in key.lower() or key.lower().startswith("on") for key in node.attrib),
                "SVG external resource or event callback")


def validate(packet: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(packet) is dict, "bad source packet")
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    require(hashlib.sha256(canonical.encode("utf-8")).hexdigest() == RECORD_FINGERPRINT,
            "source/rights record changed")
    catalog = (root / packet["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(catalog).hexdigest() == packet["discovery_catalog_sha256"],
            "accepted main discovery catalog drift")
    matches = [row for row in json.loads(catalog)["rows"]
               if row.get("row_id") == packet["source_local_episode_row_id"]]
    require(len(matches) == 1, "source-local episode missing or duplicated")
    row = matches[0]
    require((row["title"], row["context"], row["verification_status"],
             row["admission_effect"], row["coverage_effect"], row["identity_scope"]) ==
            ("The Slaver Weapon", "TAS S1E14", "UNVERIFIED_METADATA", "NONE", "NONE", "SOURCE_LOCAL"),
            "source-local discovery evidence drift")
    candidate = packet["actual_animated_scene_candidate"]
    base = ("https://images.prismic.io/star-trek-untold/"
            "01b39e29-601a-4ff5-b48d-f45a8688d4c3_theslaverweaponhd0213.jpeg")
    require(candidate["publisher_article_url"] == "https://www.startrek.com/news/top-animated-star-trek-episodes" and
            candidate["publisher_article_date"] == "2023-09-08" and
            candidate["publisher_section_heading"] == "9. The Slaver Weapon" and
            candidate["publisher_embedded_image_url"] == base + "?auto=compress%2Cformat" and
            candidate["publisher_embedded_image_format"] == "image/jpeg" and
            (candidate["publisher_embedded_image_width"], candidate["publisher_embedded_image_height"]) ==
            (1434, 1080) and
            candidate["publisher_embedded_image_bytes"] == 187263 and
            candidate["publisher_embedded_image_sha256"] ==
            "9f36424ed3cba13829cc140be686ab0e6f961a1f41f318cd4d78ffafa31416ec" and
            candidate["same_path_untransformed_url"] == base and
            candidate["same_path_untransformed_bytes"] == 480836 and
            candidate["same_path_untransformed_sha256"] ==
            "9083e38bc62d1a2d5ced92aa1805c99c2fa82b9141ff49c51f7fb1ee514679ba",
            "publisher scene/image byte identity drift")
    require(candidate["publisher_image_alt"] ==
            "A weapon locks onto Sulu as he, Uhura, and Spock stand atop of a trap aboard a frozen planet set up by the Kzinti in 'The Slaver Weapon'" and
            candidate["publisher_image_credit"] == "StarTrek.com" and
            candidate["visual_class"] ==
            "FIRST_PARTY_EDITORIAL_ANIMATED_EPISODE_SCENE_REUSE_PERMISSION_UNVERIFIED" and
            candidate["verified_broadcast_frame_extraction"] is False and
            candidate["individual_still_artist_or_frame_extract_author"] == "UNKNOWN_NOT_ESTABLISHED" and
            candidate["image_variants_independent_witnesses"] is False,
            "false source caption/creator/broadcast frame claim")
    require(candidate["public_image_display_admission"] == "HELD_NO_AFFIRMATIVE_REUSE_LICENSE" and
            candidate["source_link_admission"] == "PUBLISHER_ARTICLE_LINK_ONLY" and
            candidate["press_express_authorized_user_status"] == "NOT_ESTABLISHED" and
            candidate["press_express_terms_apply_as_grant_to_this_article_image"] is False and
            candidate["cors_or_cache_headers_are_copyright_license"] is False,
            "copyright/license inflation")
    placeholder = packet["safe_placeholder"]
    require(placeholder["svg_path"] ==
            "proposals/librarian/tas-slaverweapon-official-animated-safe-card-20261103/title-card.svg" and
            placeholder["displayed_title"] == "THE SLAVER WEAPON" and
            placeholder["visible_nonframe_label"] == "REFERENCE CARD — NOT AN ANIMATED FRAME" and
            placeholder["contains_official_episode_pixels"] is False and
            placeholder["contains_publisher_artwork"] is False and
            placeholder["uses_official_insignia_or_logo"] is False and
            placeholder["proposed_public_display_release"] == "NONE_SOURCE_LOCAL_REVIEW_ONLY" and
            packet["image_binary_committed"] is False and packet["explorer_effect"] == "NONE" and
            packet["coverage_effect"] == "NONE" and packet["global_work_admission_effect"] == "NONE",
            "publication/coverage/placeholder false admission")
    file_inventory(directory)


if __name__ == "__main__":
    validate(load())
    print("PASS: TAS Slaver Weapon editorial scene source pinned; publisher pixels HELD; original LCARS card source-local")
