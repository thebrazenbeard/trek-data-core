#!/usr/bin/env python3
"""Derive six text-free 16:9 artwork thumbnails from pinned HELD originals.

This module owns only proposal assets; it never patches Explorer, accepted
source/Work ledgers, rights decisions, or the shipped static-site allowlist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from tools import build_thematic_film_literature_art as film_lit
    from tools import build_thematic_source_art as episodes
except ModuleNotFoundError:
    import build_thematic_film_literature_art as film_lit
    import build_thematic_source_art as episodes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "proposals/ui/pictorial-thematic-thumbnails"
NS = "http://www.w3.org/2000/svg"
Q = "{" + NS + "}"
ET.register_namespace("", NS)

# Source-local record IDs, motifs, and destination names are code-pinned.
# These are not global reconciled Work IDs and do not authorize Explorer use.
REVIEWED = {
    "lead:0000": ("EPISODE", "doomsday", "doomsday-thumb.svg"),
    "lead:0001": ("EPISODE", "tribbles", "tribbles-thumb.svg"),
    "film:film-2009": ("FILM", "legacy-future", "film-2009-thumb.svg"),
    "film:film-nemesis": ("FILM", "mirror-weapon", "film-nemesis-thumb.svg"),
    "literature:prh-autobiography-janeway": ("LITERATURE", "delta-journal", "janeway-thumb.svg"),
    "literature:proposed-lit-snw-ring-of-fire": ("LITERATURE", "accretion-station", "ring-of-fire-thumb.svg"),
}

# This stays an explicit proposed integration mapping to the currently OPEN
# DRAFT #595 original-source-art filenames; no shipped CSS is altered here.
DRAFT_595_FULL_SIZE = {
    "lead:0000": "doomsday.svg", "lead:0001": "tribbles.svg",
    "film:film-2009": "film-ec60cc8243a3c9b6.svg",
    "film:film-nemesis": "film-b83e09c9a6ac3f76.svg",
    "literature:prh-autobiography-janeway": "literature-4c4c1a2caf914887.svg",
    "literature:proposed-lit-snw-ring-of-fire": "literature-a86727079426b771.svg",
}

# Frozen mapping digests keep aliases/filenames from silently switching while
# source code is reviewed. These are integrity tripwires, not external trust.
REVIEWED_BINDINGS_SHA256 = "af891535924e155d3c5a2f174990c17b3b719b4d84b6fe19265842d2be820886"
DRAFT_595_FILENAMES_SHA256 = "91815d9462af8c7dde472dc18bcf72760517d292e012a2d98d96d3ba73a1eed2"

# Raw SHA-256 of each *full-size original* as frozen in held parent art
# 0a14381. The episode generator has looser body controls than film/lit;
# this additional pin prevents an unnoticed motif replacement here.
REVIEWED_PARENT_ART_SHA256 = {
    "lead:0000": "6a04cc729c7de6c44a26f1f125ee4ccc02e3e5ac9d22a43a9b481f0bd0505f1f",
    "lead:0001": "5c2221b36d88d00966e5fd8bcace79067fc8e562845d610bf09705d7e9387480",
    "film:film-2009": "53aec4331ba61bc5f8803e650f262a20d298c0eaff46a50c4ccd94f2067e2a25",
    "film:film-nemesis": "1de2b3b86ae1a06f27219db58062c01fb25fcdae7f4c60de68250964e44f517a",
    "literature:prh-autobiography-janeway": "3398130475f32ab39f27623afc05a1bf4cf544eaaf49d4a1efdc571211aefb4a",
    "literature:proposed-lit-snw-ring-of-fire": "7f404c22c18e272d48ea080727d3928542ab754d19f34853847bcd725f6c8a97",
}

# Independent first-party URL/cue/rights tuple reviewed before thumbnail
# derivation. Source records imported from another generator are *untrusted*
# inputs here: authentic SVG pixels cannot attest that metadata is authentic.
REVIEWED_SOURCE_TUPLES = {
    "lead:0000": {
        "title": "The Doomsday Machine",
        "source_reference_url": "https://www.paramountplus.com/shows/video/1226106142/",
        "source_cue_sha256": ["0ec46cffd8810f5700b9e23bb7aebe8e18e8f2bfbbb03b59d83a660bb2ad9b7f"],
        "source_kind": "OFFICIAL_PARAMOUNT_PLUS_RENDERED_EPISODE_LISTING_NOT_VIDEO_CLOSE_READ",
        "official_image_rights_grant": "NONE",
    },
    "lead:0001": {
        "title": "The Trouble with Tribbles",
        "source_reference_url": "https://www.paramountplus.com/shows/video/1226188697/",
        "source_cue_sha256": ["948b01094036dd5e0cd391fc558e8ec77ec26a7e4a8a4e4066ff2bf4ed305729"],
        "source_kind": "OFFICIAL_PARAMOUNT_PLUS_RENDERED_EPISODE_LISTING_NOT_VIDEO_CLOSE_READ",
        "official_image_rights_grant": "NONE",
    },
    "film:film-2009": {
        "title": "Star Trek (2009)",
        "source_reference_url": "https://www.startrek.com/movies/star-trek-2009",
        "source_cue_sha256": ["d69c11ff0c55e2331fb9befcd503a8d8f86e82c4cb486a5a258af19aa8bbe794", "8aecde71c3f1c7fb85cb591ae2033caa7cde0e33cb63772bf415c4ca79ce1216"],
        "source_kind": "PUBLISHER_FILM_SYNOPSIS",
        "official_image_rights_grant": "NONE",
    },
    "film:film-nemesis": {
        "title": "Star Trek Nemesis",
        "source_reference_url": "https://www.startrek.com/movies/star-trek-nemesis",
        "source_cue_sha256": ["220273fdef976878f8e8cc8f3c1dcfda2e31c3229e49c15c7a71e6274f0d703f", "bb841e60d2768287dfc0dd8f6bc30fa0b9ef3940fb261177975badcadfd5b3c4"],
        "source_kind": "PUBLISHER_FILM_SYNOPSIS",
        "official_image_rights_grant": "NONE",
    },
    "literature:prh-autobiography-janeway": {
        "title": "The Autobiography of Kathryn Janeway",
        "source_reference_url": "https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/",
        "source_cue_sha256": ["4aea61c2de7a4a27c7f6da6cfa21764e1c15dd9efef7cd14e90e411c7eb29938", "6711c2002e7d231d210a5b98d1951e0efb506c1daebdbc271bb50eac4c178650"],
        "source_kind": "DISTRIBUTOR_BOOK_DESCRIPTION",
        "official_image_rights_grant": "NONE",
    },
    "literature:proposed-lit-snw-ring-of-fire": {
        "title": "Star Trek: Strange New Worlds: Ring of Fire",
        "source_reference_url": "https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898",
        "source_cue_sha256": ["e03e9e7dd7dc6f85a22ea610c560deee2063b64640f5c482e89ead6be1f1e56b", "b58ac4d9577e18d7ca3c4be553ea38d5187effb8747ea35118ed3289b017ca82"],
        "source_kind": "PUBLISHER_BOOK_DESCRIPTION",
        "official_image_rights_grant": "NONE",
    },
}

# Full canonical source record digests catch *unexpected extra keys* as well
# as subtle field forgeries omitted from the human-readable evidence tuple.
REVIEWED_PARENT_SOURCE_ROW_SHA256 = {
    "lead:0000": "16307f91f75c018b748fb2c5af77fe71683be4f6bac578d8514560bc46247c03",
    "lead:0001": "bf19ce8c4cfde488a34cf8f415b8c7ffe79e4ec40f819049e55cbb1341d11b5f",
    "film:film-2009": "62221ba4d3d3db201ed0ebae7c1cc97fe5125737246b22d2d48a091c450ee1bb",
    "film:film-nemesis": "3bfb4a20e14f64ab6a5c651ef9f5c6ecce912d88fb488c483278b188d55e8592",
    "literature:prh-autobiography-janeway": "7fa4f984e90b83d2b2977f3997139c69c913b14847ff76d2f725eb41d5387562",
    "literature:proposed-lit-snw-ring-of-fire": "5eb0a1705c37e93623f8d19a6648d7854dad4fa195790d8ecf6199b7364f7774",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def frozen_digest(mapping: dict) -> str:
    return sha(json.dumps(mapping, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def exact_sources() -> list[dict]:
    require(frozen_digest(REVIEWED) == REVIEWED_BINDINGS_SHA256, "thumbnail source ID/theme/filename mapping changed")
    require(frozen_digest(DRAFT_595_FULL_SIZE) == DRAFT_595_FILENAMES_SHA256, "draft full-size reference mapping changed")
    original_episode_rows = {r["source_local_row_id"]: r for r in episodes.exact_source_rows()}
    original_film_lit_rows = {r["source_local_row_id"]: r for r in film_lit.bound_inputs()}
    require(len(original_episode_rows) == 2 and len(original_film_lit_rows) == 4, "unexpected source-art contract count")
    require(set(REVIEWED) == set(original_episode_rows) | set(original_film_lit_rows), "source-local art mapping incomplete or extra")
    require(set(REVIEWED_SOURCE_TUPLES) == set(REVIEWED_PARENT_SOURCE_ROW_SHA256) == set(REVIEWED), "unreviewed source tuple keys")
    rows = []
    for rid, (medium, motif, filename) in REVIEWED.items():
        source = (original_episode_rows if medium == "EPISODE" else original_film_lit_rows)[rid]
        require(source["medium"] == medium and source["motif_id"] == motif, "source record assigned wrong theme")
        require(frozen_digest(source) == REVIEWED_PARENT_SOURCE_ROW_SHA256[rid],
                "upstream source row changed including possible hidden rights claims")
        if medium == "EPISODE":
            original_bytes = episodes.svg(source)
            original_path = episodes.OUT / "art" / f"{motif}.svg"
            locator = source["official_publisher_url"]
            cues = [source["description_utf8_sha256"]]
            cue_kind = source["publisher_source_scope"]
            require(source["licensed_source_image"] is False, "episode now claims licensed source images")
            close_read = False
            verification_status = source["accepted_metadata_status"]
        else:
            original_bytes = film_lit.render(source)
            original_path = film_lit.OUT / "art" / f"{motif}.svg"
            locator = source["source_reference_url"]
            cues = source["source_cue_sha256"]
            cue_kind = source["source_kind"]
            require(source["official_image_rights_grant"] == "NONE", "publisher image rights falsely elevated")
            close_read = source["film_or_book_close_read"]
            verification_status = source["verification_status"]
        require(original_path.is_file() and not original_path.is_symlink() and original_path.read_bytes() == original_bytes,
                "full-size source illustration stale or replaced")
        require(sha(original_bytes) == REVIEWED_PARENT_ART_SHA256[rid], "full-size parent art no longer matches independently frozen SHA")
        require(verification_status == "UNVERIFIED_METADATA" and not close_read, "false coverage or close-read promotion")
        require({"title": source["title"], "source_reference_url": locator,
                 "source_cue_sha256": cues, "source_kind": cue_kind,
                 "official_image_rights_grant": "NONE"} == REVIEWED_SOURCE_TUPLES[rid],
                "unreviewed source citation/description/source-kind/rights tuple")
        require(source["identity_scope"] == "SOURCE_LOCAL" and source["admission_effect"] == source["coverage_effect"] == "NONE",
                "source effect promoted")
        rows.append({
            "source_local_row_id": rid, "medium": medium, "motif_id": motif,
            "title": source["title"], "thumbnail_name": filename,
            "draft_595_full_size_filename": DRAFT_595_FULL_SIZE[rid],
            "source_reference_url": locator, "source_cue_sha256": cues,
            "source_cue_kind": cue_kind, "source_full_art_sha256": sha(original_bytes),
            "accepted_metadata_status": verification_status, "identity_scope": "SOURCE_LOCAL",
            "source_full_art_path": str(original_path.relative_to(ROOT)),
            "official_image_rights_grant": "NONE", "full_media_close_read": False,
            "source_image_bytes": 0, "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    require(len(rows) == len({r["thumbnail_name"] for r in rows}) == 6, "duplicate thumbnail identity")
    return rows


def _is_footer(child: ET.Element) -> bool:
    if child.tag != Q + "rect":
        return False
    return (float(child.attrib.get("y", "0")) >= 348
            and float(child.attrib.get("width", "0")) == 800
            and float(child.attrib.get("height", "0")) >= 100)


def thumbnail(original_bytes: bytes, source: dict) -> bytes:
    """Transform reviewed motif pixels, not depict new unsupported events.

    A centered uniform 1.25x enlargement recovers the title-strip area while
    preserving circular/spherical geometry; side-edge crop is intentional.
    The source's visual geometry is unchanged except scale and crop;
    captions and title strip are omitted because the real card has an
    accessible external label, title, source link and attribution.
    """
    require(source in exact_sources(), "thumbnail source must be exact reviewed row")
    require(sha(original_bytes) == source["source_full_art_sha256"], "original source motif bytes not independently pinned")
    root = ET.fromstring(original_bytes)
    require(root.tag == Q + "svg" and root.attrib.get("viewBox") == "0 0 800 450", "unexpected source graphic geometry")
    children = list(root)
    text_count = sum(1 for child in children if child.tag == Q + "text")
    footer_count = sum(1 for child in children if _is_footer(child))
    require(text_count >= 3 and footer_count == 1, "source poster label/footer structure changed")
    accepted_shape_tags = {Q + name for name in ("defs", "linearGradient", "radialGradient", "stop", "rect", "path", "circle", "ellipse")}
    for child in root.iter():
        require(child.tag in accepted_shape_tags | {Q + "svg", Q + "text"}, "non-graphic/active SVG element")
    view = ET.Element(Q + "svg", {
        "viewBox": "0 0 800 450", "role": "img",
        "aria-label": f"Original visual motif for source-local {source['source_local_row_id']}; not official art or close-read evidence",
    })
    scene = ET.SubElement(view, Q + "g", {"transform": "translate(-100 -9) scale(1.25)"})
    for child in children:
        if child.tag == Q + "text" or _is_footer(child):
            continue
        scene.append(child)
    require(not any(c.tag == Q + "text" for c in view.iter()), "tiny embedded SVG text survived crop")
    result = ET.tostring(view, encoding="utf-8", xml_declaration=False) + b"\n"
    lower = result.lower()
    require(not any(unsafe in lower for unsafe in (b"<image", b"<script", b"<foreignobject", b"href=", b"javascript:", b"data:", b"<use ")),
            "thumbnail contains active or third-party content")
    return result


def expected() -> dict[Path, bytes]:
    files = {}
    metadata = []
    for source in exact_sources():
        original = (ROOT / source["source_full_art_path"]).read_bytes()
        dest = OUT / "art" / source["thumbnail_name"]
        art = thumbnail(original, source)
        files[dest] = art
        metadata.append({**source, "thumbnail_path": f"art/{source['thumbnail_name']}", "thumbnail_sha256": sha(art),
                         "composition_rule": "REMOVE_SOURCE_FOOTER_AND_VISIBLE_TEXT;UNIFORM_CENTER_CROP_1_25;NO_NEW_SCENE_GEOMETRY"})
    files[OUT / "manifest.json"] = (json.dumps({
        "status": "HELD_ONLY_NO_EXPLORER_PUBLICATION",
        "accepted_main_when_original_art_anchored": episodes.MAIN,
        "source_parent_art_commit": "0a14381a01b77966f6c2d1be9b805aaf025d58b4",
        "draft_explorer_integration_pr": 595,
        "intended_css_slot_widths_px": [132, 190],
        "purpose": "PICTORIAL_ART_ONLY_NO_TINY_EMBEDDED_TITLE_OR_FOOTER",
        "source_image_bytes": 0, "public_release_effect": "NONE", "admitted_works": 0,
        "coverage_effect": "NONE", "full_episode_film_or_book_close_reads": 0,
        "records": metadata,
    }, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = expected()
    if args.check:
        require(all(p.is_file() and not p.is_symlink() and p.read_bytes() == b for p,b in output.items()), "thumbnail generated-byte drift")
        art = OUT / "art"
        require(art.is_dir() and not art.is_symlink() and set(art.iterdir()) == {p for p in output if p.parent == art}, "unexpected thumbnail file")
        print("PICTORIAL THUMBNAILS VERIFIED: six HELD original source-motif crops, no public Work/art release")
    else:
        for p, blob in output.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            require(not p.is_symlink(), "symlink output refused")
            p.write_bytes(blob)
        print("PICTORIAL THUMBNAILS BUILT: six HELD originals, no remote integration")


if __name__ == "__main__":
    main()
