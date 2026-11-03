#!/usr/bin/env python3
"""Guard a publisher-source-bound Voyager still while withholding copyrighted pixels."""

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
MANIFEST_SHA = "fcd086b69cb1f2e3902959d490d549fceef6967004ed7a2ff60e380cfef2fc46"
CARD_SHA = "115e485050d89a22d59b9d15c7dc6de26e8975427a46b5b489c7ee5984b04bd6"
RECORD_FINGERPRINT = "8990d3b4ac9d41065701931b722d05422d3f6353cefa616251a62d8758067f47"


def require(valid: bool, explanation: str) -> None:
    if not valid:
        raise ValueError(explanation)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate source metadata key")
        result[key] = value
    return result


def load(path: Path = RECORD) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid {value}")))


def text_guard(path: Path) -> None:
    require(path.is_file() and path.stat().st_size <= 150_000, "oversized or missing text file")
    b = path.read_bytes()
    require(not any(s in b for s in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF" + b"87a",
                                    b"GIF" + b"89a", b"%" + b"PDF", b"PK\x03\x04")),
            "binary data disguised as text")
    try:
        t = b.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise ValueError("non-UTF8 packet source") from exc
    require("\x00" not in t and not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in t),
            "control byte hidden in text")
    if path.suffix in {".md", ".json", ".svg"}:
        lower = t.lower()
        require(not any(s in lower for s in ("data:" + "image/", "<!" + "doctype", "<" + "script",
                                           "<" + "image", "<" + "foreignobject")),
                "embedded or active image payload")


def file_inventory(directory: Path = HERE) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "invalid packet dir")
    for p in directory.rglob("*"):
        rel = p.relative_to(directory)
        require(not p.is_symlink(), "symlink in packet")
        if p.is_dir():
            require(rel.parts == ("__pycache__",), "unreviewed nested directory")
            continue
        if p.is_file() and len(rel.parts) == 1 and p.name in FILES:
            text_guard(p)
            continue
        if p.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and p.suffix == ".pyc":
            continue
        raise ValueError("unreviewed file or nested payload")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "incomplete packet")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        p = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
                           capture_output=True, text=True, timeout=10, check=False)
        require(p.returncode == 0 and set(p.stdout.splitlines()) ==
                {prefix + n for n in FILES}, "unexpected tracked image or packet file")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == MANIFEST_SHA,
            "unreviewed rights prose / scene caption in manifest")
    card = (directory / "title-card.svg").read_bytes()
    require(hashlib.sha256(card).hexdigest() == CARD_SHA, "unreviewed original SVG")
    try:
        svg = ET.fromstring(card)
    except ET.ParseError as exc:
        raise ValueError("invalid SVG") from exc
    ns = "{http://www.w3.org/2000/svg}"
    require(svg.tag == ns + "svg" and svg.attrib.get("viewBox") == "0 0 960 540", "SVG dimensions")
    for node in svg.iter():
        require(node.tag in {ns + name for name in ("svg", "title", "desc", "rect", "text")},
                "unreviewed active/media SVG tag")
        require(not any("href" in k.lower() or k.lower().startswith("on") for k in node.attrib),
                "SVG external resource or event callback")


def validate(packet: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(packet) is dict, "not a packet")
    fingerprint = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=False).encode("utf-8")).hexdigest()
    require(fingerprint == RECORD_FINGERPRINT, "unreviewed source/rights/content mutation")
    raw = (root / packet["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == packet["discovery_catalog_sha256"], "accepted catalog drift")
    matches = [r for r in json.loads(raw)["rows"] if r.get("row_id") == packet["source_local_episode_row_id"]]
    require(len(matches) == 1, "source-local episode row missing or duplicated")
    row = matches[0]
    require((row["title"], row["context"], row["verification_status"], row["admission_effect"],
             row["coverage_effect"]) == ("Living Witness", "VOY S4E23", "UNVERIFIED_METADATA", "NONE", "NONE"),
            "source-local episode join drift")
    photo = packet["actual_scene_candidate"]
    path = "https://images.prismic.io/star-trek-untold/NjFiMDBmZGEtYjczNC00N2I4LThkMjAtNjRlNWY4NWE3NjQ5_th_livingwitness.jpg"
    require(photo["publisher_embedded_image_url"] == path + "?auto=compress%2Cformat" and
            photo["publisher_embedded_image_bytes"] == 97350 and
            photo["publisher_embedded_image_sha256"] ==
            "0190eb49039850fc0515375e754b14539354a835d25e9606a3efe641fa652358",
            "actual article JPEG delivery identity")
    require(photo["same_path_untransformed_url"] == path and photo["same_path_untransformed_bytes"] ==
            114509 and photo["same_path_untransformed_sha256"] ==
            "d9361b21961b0446def489d9c4b2b6ed845e1cc6410e3a9f8bf89c69bba6c2e9",
            "untransformed photo variant identity")
    require(photo["publisher_image_alt"] == 'Star Trek: Voyager "Living Witness"' and
            photo["visual_class"] == "FIRST_PARTY_EDITORIAL_EPISODE_STILL_REUSE_PERMISSION_UNVERIFIED" and
            photo["verified_broadcast_frame"] is False and photo["individual_photographer"] ==
            "UNKNOWN_NOT_ESTABLISHED", "false still/creator claim")
    require(photo["image_variants_independent_witnesses"] is False and
            photo["press_express_authorized_user_status"] == "NOT_ESTABLISHED" and
            photo["press_express_terms_apply_as_grant_to_this_article_image"] is False and
            photo["public_image_display_admission"] == "HELD_NO_AFFIRMATIVE_REUSE_LICENSE",
            "license or corroboration inflation")
    require(packet["image_binary_committed"] is False and packet["explorer_effect"] == "NONE" and
            packet["coverage_effect"] == "NONE" and packet["global_work_admission_effect"] == "NONE" and
            packet["safe_placeholder"]["contains_official_episode_pixels"] is False and
            packet["safe_placeholder"]["proposed_public_display_release"] == "NONE_SOURCE_LOCAL_REVIEW_ONLY",
            "unapproved publication/coverage")
    file_inventory(directory)


if __name__ == "__main__":
    validate(load())
    print("PASS: VOY Living Witness first-party still source pinned; publisher pixels held, original card source-only")
