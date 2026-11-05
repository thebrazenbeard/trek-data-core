#!/usr/bin/env python3
"""Generate two original, explicitly interpretive, publisher-description-bound SVGs.

Never use this HELD output as an episode still, proof of viewing, or licensed art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "proposals/ui/thematic-source-art"
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
DESCRIPTION_SOURCE = "OFFICIAL_PARAMOUNT_PLUS_RENDERED_EPISODE_LISTING_NOT_VIDEO_CLOSE_READ"
PUBLISHER_DESCRIPTION_SHA256 = {
    "lead:0000": "0ec46cffd8810f5700b9e23bb7aebe8e18e8f2bfbbb03b59d83a660bb2ad9b7f",
    "lead:0001": "948b01094036dd5e0cd391fc558e8ec77ec26a7e4a8a4e4066ff2bf4ed305729",
}

ROWS = (
    {
        "row_id": "lead:0000", "title": "The Doomsday Machine", "episode_slot": "TOS S2 E6",
        "official_url": "https://www.paramountplus.com/shows/video/1226106142/",
        "description": "A machine that destroys planets threatens the Enterprise",
        "motif": "abstract mechanical planet-destroyer near a fragmented world",
        "motif_tags": ("machine", "destroys planets"),
        "theme": "doomsday",
    },
    {
        "row_id": "lead:0001", "title": "The Trouble with Tribbles", "episode_slot": "TOS S2 E15",
        "official_url": "https://www.paramountplus.com/shows/video/1226188697/",
        "description": "The Enterprise is overrun by furry creatures while tangling with Klingons and bureaucrats",
        "motif": "abstract overflow of fuzzy circles through generic compartments",
        "motif_tags": ("overrun", "furry creatures"),
        "theme": "tribbles",
    },
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_source_rows() -> list[dict]:
    search_path = ROOT / "explorer/search-catalog.json"
    recheck_path = ROOT / "explorer/metadata-rechecks.json"
    search = json.loads(search_path.read_text())
    rechecks = json.loads(recheck_path.read_text())
    assert isinstance(search["rows"], list) and isinstance(rechecks["rows"], list)
    output = []
    for rec in ROWS:
        matching = [x for x in search["rows"] if x.get("row_id") == rec["row_id"]]
        checked = [x for x in rechecks["rows"] if x.get("row_id") == rec["row_id"]]
        require(len(matching) == len(checked) == 1, "missing or duplicate accepted source-local row")
        row, observation = matching[0], checked[0]
        require(row["title"] == rec["title"] and observation["official_observed_title"] == rec["title"], "source title mismatch")
        require(row["medium"] == "EPISODE" and row["verification_status"] == "UNVERIFIED_METADATA", "episode/source status promoted")
        require(row["identity_scope"] == "SOURCE_LOCAL" and row["admission_effect"] == row["coverage_effect"] == "NONE", "source effect promoted")
        require(row["source_input"] == "explorer/research-leads.json", "source input changed")
        require(observation["official_evidence_url"] == rec["official_url"], "official publisher URL changed")
        require(observation["fields_observed"] == ["title", "series", "season_episode", "air_date"], "metadata recheck unexpectedly claims description")
        # The descriptive synopsis was retrieved separately from the exact official publisher page;
        # accepted rechecks are title/date ONLY, and must not be mislabeled a prior synopsis read.
        desc = rec["description"].lower()
        require(sha(rec["description"].encode("utf-8")) == PUBLISHER_DESCRIPTION_SHA256[rec["row_id"]], "publisher description digest drift")
        require(all(tag in desc for tag in rec["motif_tags"]), "motif tag not supported by publisher description")
        output.append({
            "source_local_row_id": rec["row_id"], "medium": "EPISODE", "title": rec["title"],
            "episode_slot": rec["episode_slot"], "metadata_row_sha256": sha((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()),
            "accepted_metadata_status": "UNVERIFIED_METADATA", "identity_scope": "SOURCE_LOCAL",
            "official_publisher_url": rec["official_url"], "publisher_description": rec["description"],
            "description_utf8_sha256": sha(rec["description"].encode("utf-8")),
            "publisher_source_scope": DESCRIPTION_SOURCE, "raw_publisher_html_sha256": None,
            "motif_id": rec["theme"], "motif_interpretation": rec["motif"],
            "motif_evidence_terms": list(rec["motif_tags"]),
            "motif_status": "INTERPRETIVE_FROM_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "licensed_source_image": False, "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return output


def _stars() -> str:
    return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ddf5ff" opacity=".54"/>' for x, y, r in ((38, 42, 1), (190, 43, 1), (359, 57, 2), (633, 23, 1), (719, 81, 1), (93, 178, 1), (747, 194, 1)))


def _doomsday() -> str:
    # Geometric machinery is intentionally unrelated to the franchise's distinctive prop design.
    teeth = "".join(f'<path d="M {112+i*15} {144+i%3*8} L {133+i*15} 179 L {112+i*15} 213" stroke="#ffbf63" stroke-width="5" fill="none" opacity=".72"/>' for i in range(5))
    return '''<defs><linearGradient id="space" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#121a39"/><stop offset="1" stop-color="#093c56"/></linearGradient><radialGradient id="planet"><stop stop-color="#e2e8fa"/><stop offset=".7" stop-color="#7dcada"/><stop offset="1" stop-color="#347b9a"/></radialGradient></defs>
    <rect width="800" height="450" fill="url(#space)"/>''' + _stars() + '''
    <circle cx="601" cy="211" r="90" fill="url(#planet)"/>
    <path d="M 554 147 L 575 176 L 551 202 L 603 244 L 626 209 L 651 231 L 661 255" stroke="#0e557b" stroke-width="8" fill="none"/>
    <path d="M 613 108 L 670 95 L 681 119 L 715 122 L 701 145 L 735 166" stroke="#f7e7b0" stroke-width="10" fill="none"/>
    <path d="M 527 270 L 486 310 L 475 286 L 447 296 M 675 281 L 707 299 L 728 288" stroke="#b8f6ef" stroke-width="6" fill="none"/>
    <path d="M -20 103 L 200 60 L 373 189 L 194 341 L -20 302 Z" fill="#22334c" stroke="#f5ad6b" stroke-width="12"/>
    <path d="M 30 131 L 179 109 L 282 186 L 169 290 L 30 275 Z" fill="#142a3d" stroke="#e7c07a" stroke-width="6"/>
    <ellipse cx="198" cy="198" rx="57" ry="90" fill="#e26568" opacity=".38"/>
    <ellipse cx="198" cy="198" rx="33" ry="59" fill="#ffb871" opacity=".6"/>
    <path d="M 275 166 L 442 182 M 275 232 L 435 220" stroke="#ffb45a" stroke-width="5" stroke-dasharray="17 13" opacity=".8"/>''' + teeth


def _tribbles() -> str:
    circles = []
    palette = ("#f4b48a", "#e8d2b8", "#b3b8df", "#bd83a4", "#e5a9ca")
    for i in range(54):
        x = 134 + (i * 83 + (i * i * 19)) % 550
        y = 76 + (i * 47 + (i * i * 13)) % 219
        size = 12 + (i * 7) % 17
        color = palette[i % len(palette)]
        circles.append(f'<circle cx="{x}" cy="{y}" r="{size}" fill="{color}" stroke="#713b5b" stroke-width="3"/>')
        circles.append(f'<path d="M{x-size-2} {y-4} l-5 -4 M{x+size+2} {y+3} l6 4 M{x-5} {y-size-2} l-4 -5" stroke="{color}" stroke-width="3"/>')
    return '''<defs><linearGradient id="space" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#301d46"/><stop offset="1" stop-color="#74415f"/></linearGradient></defs>
    <rect width="800" height="450" fill="url(#space)"/>
    <path d="M 60 68 H 733 V 330 H 60 Z" fill="#33233e" stroke="#e0a47a" stroke-width="7"/>
    <path d="M 60 148 H 733 M 60 241 H 733 M 286 68 V 330 M 508 68 V 330" stroke="#a76687" stroke-width="6" opacity=".65"/>
    <path d="M 74 89 H 261 M 299 89 H 484 M 520 89 H 719" stroke="#efbe86" stroke-width="3" opacity=".5"/>''' + "".join(circles) + '''
    <path d="M 50 320 H 750" stroke="#f2cf8b" stroke-width="9" opacity=".7"/>
    <path d="M 724 308 L 756 321 L 722 336" fill="none" stroke="#f2cf8b" stroke-width="9"/>'''


def svg(row: dict) -> bytes:
    require(row in exact_source_rows(), "motif rendering requires exact pinned source-evidence record")
    theme = row["motif_id"]
    require(theme in {"doomsday", "tribbles"}, "unreviewed visual motif")
    visual = _doomsday() if theme == "doomsday" else _tribbles()
    out = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="Original thematic interpretation of Paramount publisher episode description; not a production image">''' + visual + f'''
    <rect x="0" y="349" width="800" height="101" fill="#111323" opacity=".96"/>
    <text x="32" y="378" font-family="sans-serif" font-size="18" fill="#f5c58a">{escape(row['episode_slot'])} · ORIGINAL SOURCE-BOUND INTERPRETATION</text>
    <text x="32" y="411" font-family="sans-serif" font-size="27" fill="#fff5e9" font-weight="700">{escape(row['title'])}</text>
    <text x="32" y="434" font-family="sans-serif" font-size="13" fill="#d5ddeb">NOT AN EPISODE STILL · NOT OFFICIAL ART · NOT CLOSE-READ EVIDENCE</text>
    </svg>'''
    ET.fromstring(out)
    require(not any(forbidden in out.lower() for forbidden in ("<script", "<image", "<foreignobject", "href=", "javascript:", "data:")), "forbidden embedded SVG media")
    return (out + "\n").encode("utf-8")


def expected() -> dict[Path, bytes]:
    rows = exact_source_rows()
    images = {}
    records = []
    for row in rows:
        file_name = "art/" + row["motif_id"] + ".svg"
        img = svg(row)
        images[OUT / file_name] = img
        records.append({**row, "art_path": file_name, "art_sha256": sha(img)})
    packet = {"status": "HELD_THEMATIC_PUBLISHER_DESCRIPTION_ART_NOT_PUBLIC", "accepted_main": MAIN,
              "source_scope": DESCRIPTION_SOURCE, "art_class": "ORIGINAL_THEMATIC_INTERPRETATION_NOT_OFFICIAL",
              "source_image_bytes": 0, "full_episode_viewing": False, "admitted_works": 0, "coverage_effect": "NONE", "public_release_effect": "NONE", "records": records}
    images[OUT / "manifest.json"] = (json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return images


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = expected()
    if args.check:
        require(all(p.is_file() and not p.is_symlink() and p.read_bytes() == data for p, data in files.items()), "thematic file missing or modified")
        art = OUT / "art"
        require(art.is_dir() and not art.is_symlink() and set(art.iterdir()) == {p for p in files if p.parent == art}, "artwork directory unexpected contents")
        print("THEMATIC SOURCE ART VERIFIED: two original motifs, no official imagery, zero Work effects")
    else:
        for p, data in files.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            require(not p.is_symlink(), "refusing output symlink")
            p.write_bytes(data)
        print("THEMATIC SOURCE ART BUILT: held, no public effects")


if __name__ == "__main__":
    main()
