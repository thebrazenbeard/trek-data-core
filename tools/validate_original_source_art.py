"""Fail-closed gate for exact original, source-local public Explorer SVG assets.

These images are originally drawn index illustrations. This validator does not
establish film/episode reading, canonical identity, or third-party art rights.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "explorer/original-source-art"
# This release gate intentionally pins the complete effective JS/CSS, not just
# the first source-map declaration. Otherwise a later Map.set(), early resolver
# return, or later specificity override can silently misbind original visuals.
# Any subsequent UI change requires an explicit pin review and HTML cache update.
REVIEWED_EXPLORER_JS_SHA256 = "83b097b45f681399d470a534bc1ac7fcf4c42aa9822a16d2c66d38651c10ef40"
REVIEWED_EXPLORER_CSS_SHA256 = "0a6eb6c0c9e532f4f54157b012a604a5231ea0f3c5f8240f0c1dfd89d1ac6dac"
ALLOWED_TAGS = {"svg", "defs", "linearGradient", "radialGradient", "stop", "circle", "ellipse", "rect", "path", "text"}
ALLOWED_ATTRS = {
    "xmlns", "viewBox", "role", "aria-label", "id", "x", "y", "x1", "x2", "y1", "y2",
    "width", "height", "rx", "ry", "cx", "cy", "r", "d", "fill", "stroke",
    "stroke-width", "stroke-dasharray", "opacity", "font-family", "font-size",
    "font-weight", "offset", "stop-color", "stop-opacity",
}
# The key is the immutable discovery record identity, never a title slug.
# Asset hashes are SHA-256 of the exact results in HELD source-art proposals.
# A review of such proposals is not an approval to merge, publish, or license.
PINS = {
    "directory:lead:0000": (
        "doomsday.svg", "6a04cc729c7de6c44a26f1f125ee4ccc02e3e5ac9d22a43a9b481f0bd0505f1f",
        "EPISODE", "The Doomsday Machine", "https://www.wikidata.org/wiki/Q1136071"),
    "directory:lead:0001": (
        "tribbles.svg", "5c2221b36d88d00966e5fd8bcace79067fc8e562845d610bf09705d7e9387480",
        "EPISODE", "The Trouble with Tribbles", "https://www.wikidata.org/wiki/Q1136084"),
    "directory:lead:0050": (
        "episode-8cf3e38782500993.svg", "81ed8bbd09cbc99b658fb63eb3d69267df10784f34345032d9c742e1cc4e78ba",
        "EPISODE", "Crossfire", "https://www.wikidata.org/wiki/Q1027877"),
    "film:film-2009": (
        "film-ec60cc8243a3c9b6.svg", "53aec4331ba61bc5f8803e650f262a20d298c0eaff46a50c4ccd94f2067e2a25",
        "FILM", "Star Trek (2009)", "https://www.startrek.com/movies/star-trek-2009"),
    "film:film-nemesis": (
        "film-b83e09c9a6ac3f76.svg", "1de2b3b86ae1a06f27219db58062c01fb25fcdae7f4c60de68250964e44f517a",
        "FILM", "Star Trek Nemesis", "https://www.startrek.com/movies/star-trek-nemesis"),
    "directory:literature:prh-autobiography-janeway": (
        "literature-4c4c1a2caf914887.svg", "3398130475f32ab39f27623afc05a1bf4cf544eaaf49d4a1efdc571211aefb4a",
        "LITERATURE", "The Autobiography of Kathryn Janeway",
        "https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/"),
    "directory:literature:proposed-lit-snw-ring-of-fire": (
        "literature-a86727079426b771.svg", "7f404c22c18e272d48ea080727d3928542ab754d19f34853847bcd725f6c8a97",
        "LITERATURE", "Star Trek: Strange New Worlds: Ring of Fire",
        "https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898"),
}
THEMATIC_SOURCES = {
    "directory:lead:0000": "https://www.paramountplus.com/shows/video/1226106142/",
    "directory:lead:0001": "https://www.paramountplus.com/shows/video/1226188697/",
    "film:film-2009": "https://www.startrek.com/movies/star-trek-2009",
    "film:film-nemesis": "https://www.startrek.com/movies/star-trek-nemesis",
    "directory:literature:prh-autobiography-janeway": "https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/",
    "directory:literature:proposed-lit-snw-ring-of-fire": "https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898",
}


def validate() -> int:
    if ASSETS.is_symlink() or not ASSETS.is_dir():
        raise ValueError("Original illustration directory is missing or linked")
    expected = {values[0] for values in PINS.values()}
    if {p.name for p in ASSETS.iterdir()} != expected:
        raise ValueError("Unexpected, missing, or hidden original illustration asset")
    directory = json.loads((ROOT / "explorer/discovery-catalog.json").read_text())
    films = json.loads((ROOT / "explorer/film-catalog.json").read_text())
    rows = {f"directory:{row['row_id']}": row for row in directory["rows"]}
    rows.update({f"film:{row['id']}": row for row in films["films"]})
    for record_id, (filename, digest, medium, title, locator) in PINS.items():
        row = rows.get(record_id)
        if not row or row["title"] != title or row["source_locator"] != locator or \
                row["verification_status"] != "UNVERIFIED_METADATA" or \
                (row.get("medium") or "FILM") != medium:
            raise ValueError(f"Source-local identity/locator changed: {record_id}")
        path = ASSETS / filename
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked original art: {filename}")
        payload = path.read_bytes()
        if not (200 <= len(payload) <= 64000) or hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError(f"Original art has altered bytes: {filename}")
        root = ET.fromstring(payload)
        for element in root.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            if tag not in ALLOWED_TAGS:
                raise ValueError(f"Unexpected SVG element: {tag}")
            for attr, value in element.attrib.items():
                name = attr.rsplit("}", 1)[-1]
                if name not in ALLOWED_ATTRS or "{" in name or "}" in name or \
                        re.search(r"(?i)(https?:|data:|javascript:|<|>|@import|expression\s*\()", value):
                    raise ValueError(f"Unsafe SVG attribute: {name}")
                if "url(" in value and not re.fullmatch(r"url\(#[A-Za-z][A-Za-z0-9_-]*\)", value):
                    raise ValueError("SVG paint must be a local defined gradient")
    js = (ROOT / "explorer/app.js").read_text()
    block = js.split("const proposedOriginalArt = new Map([", 1)[1].split("]);", 1)[0]
    entries = re.findall(
        r"\['([^']+)', \['([^']+)', '([^']+)', '([^']+)', '([^']+)', (null|'[^']+')\]\]",
        block,
    )
    if len(entries) != len(PINS) or len({row[0] for row in entries}) != len(PINS):
        raise ValueError("JavaScript original artwork receipt count differs from file gate")
    actual = {rid: (medium, title, locator, asset, thematic)
              for rid, medium, title, locator, asset, thematic in entries}
    css = (ROOT / "explorer/app.css").read_text()
    for record_id, (filename, _, medium, title, locator) in PINS.items():
        source = THEMATIC_SOURCES.get(record_id)
        thematic = f"'{source}'" if source else "null"
        if actual.get(record_id) != (medium, title, locator, filename, thematic):
            raise ValueError(f"Missing source-locked JS artwork receipt: {record_id}")
        css_selector = f".artwork-slot.artwork-original-{filename.removesuffix('.svg')} {{ background-image: url('./original-source-art/{filename}')"
        if css_selector not in css:
            raise ValueError(f"Original image has no exact safe CSS presentation: {record_id}")
    for name, pinned in (("app.js", REVIEWED_EXPLORER_JS_SHA256),
                         ("app.css", REVIEWED_EXPLORER_CSS_SHA256)):
        path = ROOT / "explorer" / name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != pinned:
            raise ValueError(f"effective Explorer {name} digest differs from approved source-art binding")
    html = ROOT / "explorer/index.html"
    if not html.is_file() or html.is_symlink():
        raise ValueError("Explorer HTML is missing or linked")
    document = html.read_text()
    for name, pinned in (("app.js", REVIEWED_EXPLORER_JS_SHA256),
                         ("app.css", REVIEWED_EXPLORER_CSS_SHA256)):
        if document.count(f'./{name}?v={pinned}') != 1:
            raise ValueError(f"Explorer {name} cache fingerprint is not the exact reviewed file")
    return len(PINS)


if __name__ == "__main__":
    print(f"Validated {validate()} original source-local illustrations; zero third-party pixels")
