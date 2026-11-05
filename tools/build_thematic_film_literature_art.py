#!/usr/bin/env python3
"""Four original film/literature visual interpretations with pinned first-party cues.

HELD proposal only. No screenshots, book jacket replication, screenplay/ebook read,
image rights grant, accepted Work, or public Explorer publication is implied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from tools import build_reference_card_inputs as librarian
except ModuleNotFoundError:
    import build_reference_card_inputs as librarian

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "proposals/ui/thematic-film-literature-art"
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"

# Short, exact source passages from identified first-party sections. The full
# pages/book/films are NOT copied; extra words are intentionally not reproduced.
CLAIMS = (
    {
        "row_id": "film:film-2009", "medium": "FILM", "motif_id": "legacy-future",
        "section": "StarTrek.com film page > Synopsis", "source_kind": "PUBLISHER_FILM_SYNOPSIS",
        "excerpts": ("legacy of his father", "vengeful Romulan from the future"),
        "motif_elements": ("two diverging legacy/future paths", "opposing vectors converging on an abstract star chart"),
    },
    {
        "row_id": "film:film-nemesis", "medium": "FILM", "motif_id": "mirror-weapon",
        "section": "StarTrek.com film page > Synopsis", "source_kind": "PUBLISHER_FILM_SYNOPSIS",
        "excerpts": ("A clone of Picard", "threatens the destruction of the Federation with a powerful weapon"),
        "motif_elements": ("two opposed mirrored geometric forms", "central destructive energy bar"),
    },
    {
        "row_id": "literature:prh-autobiography-janeway", "medium": "LITERATURE", "motif_id": "delta-journal",
        "section": "Penguin Random House distributor page > Book Description", "source_kind": "DISTRIBUTOR_BOOK_DESCRIPTION",
        "excerpts": ("her lifestory for the first time in her own words", "epic journey through the Delta Quadrant"),
        "motif_elements": ("open abstract memoir pages", "long dotted route across a stylized starfield"),
    },
    {
        "row_id": "literature:proposed-lit-snw-ring-of-fire", "medium": "LITERATURE", "motif_id": "accretion-station",
        "section": "Simon & Schuster publisher page > About the Book", "source_kind": "PUBLISHER_BOOK_DESCRIPTION",
        "excerpts": ("accretion disk of a black hole", "classified research facility located above"),
        "motif_elements": ("original accretion torus", "small abstract research station above the disk"),
    },
)

# Verified independently against first-party public URLs, not self-attested by
# the mutable six-row input contract. These are page-level SOURCE locators, not
# evidence that an accepted Work or a scanned/owned edition exists.
SOURCE_PINS = {
    "film:film-2009": ("Star Trek (2009)", "https://www.startrek.com/movies/star-trek-2009"),
    "film:film-nemesis": ("Star Trek Nemesis", "https://www.startrek.com/movies/star-trek-nemesis"),
    "literature:prh-autobiography-janeway": ("The Autobiography of Kathryn Janeway", "https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/"),
    "literature:proposed-lit-snw-ring-of-fire": ("Star Trek: Strange New Worlds: Ring of Fire", "https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898"),
}

# First-party page's *selected marketing listing*, distinct from accepted
# Librarian edition_identifier=null and from any physical/ebook edition read.
PAGE_EDITION_LISTINGS = {
    "literature:prh-autobiography-janeway": {
        "publisher_listed_isbn13": "9781789095333", "publisher_listed_format": "Paperback",
        "publisher_listed_publication_date": "2021-11-16", "publisher_listed_page_count": 224,
        "publisher_or_distributor": "Penguin Random House / Titan Books",
    },
    "literature:proposed-lit-snw-ring-of-fire": {
        "publisher_listed_isbn13": "9781668095898", "publisher_listed_format": "Hardcover",
        "publisher_listed_publication_date": "2025-10-07", "publisher_listed_page_count": 336,
        "publisher_or_distributor": "Simon & Schuster / Pocket Books/Star Trek",
    },
}

EXCERPT_PINS = {
    "film:film-2009": ("d69c11ff0c55e2331fb9befcd503a8d8f86e82c4cb486a5a258af19aa8bbe794", "8aecde71c3f1c7fb85cb591ae2033caa7cde0e33cb63772bf415c4ca79ce1216"),
    "film:film-nemesis": ("220273fdef976878f8e8cc8f3c1dcfda2e31c3229e49c15c7a71e6274f0d703f", "bb841e60d2768287dfc0dd8f6bc30fa0b9ef3940fb261177975badcadfd5b3c4"),
    "literature:prh-autobiography-janeway": ("4aea61c2de7a4a27c7f6da6cfa21764e1c15dd9efef7cd14e90e411c7eb29938", "6711c2002e7d231d210a5b98d1951e0efb506c1daebdbc271bb50eac4c178650"),
    "literature:proposed-lit-snw-ring-of-fire": ("e03e9e7dd7dc6f85a22ea610c560deee2063b64640f5c482e89ead6be1f1e56b", "b58ac4d9577e18d7ca3c4be553ea38d5187effb8747ea35118ed3289b017ca82"),
}

# Independent review pins for the ENTIRE per-row source/scene/evidence tuple,
# not just the two excerpt strings. Updating one requires an explicit source
# re-review and tests; unknown extra keys also invalidate this digest.
REVIEWED_CLAIM_PINS = {
    "film:film-2009": "2146f32fa08d190cb48b924658d8a7f98d51917f0d6fc8aca9dffe223d8be7a0",
    "film:film-nemesis": "96102bbd6fa223c44f44b1fe970c88b049db4ba0d1d8c3efe0938b7b09f12c8a",
    "literature:prh-autobiography-janeway": "e3de84ef73d92cfb7ff4a6e3ebd3b82f28fce92221b438fedb5f5e98a70e5dd7",
    "literature:proposed-lit-snw-ring-of-fire": "bc819a0d441b99e40a109e26a13ed2032eac36d3298612a0cbb01f913d777b0f",
}

REVIEWED_EDITION_LISTING_PINS = {
    "literature:prh-autobiography-janeway": "cdac3a1a22dfe5dae85ee4487688834671466bec35be14182d1b1242f73146ed",
    "literature:proposed-lit-snw-ring-of-fire": "c1c99def972166229888026ba9c0d97b40d80833c12771c9362b400bad876a5c",
}

# Prevent a same-ID theme function from silently swapping to another drawing.
REVIEWED_SCENE_PINS = {
    "legacy-future": "7d79039b9bc2407c1b44c632dc19c11082854fa88310bcdb5f0ecf0f92031bba",
    "mirror-weapon": "d80a81c2a075601ab9b9ba409657a4950690c72369fd825c9d40a45772d28432",
    "delta-journal": "6ccc1ceb49a7d509536b0822c109933d5cd51d3f167f2627aa5eadec00f9fc49",
    "accretion-station": "9256f36cd7df7534c4127d978968a4415a396920c18979f376c14d2b1faf270b",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def bound_inputs() -> list[dict]:
    contract = {x["source_local_row_id"]: x for x in librarian.build_inputs()}
    require(len(contract) == 6, "unexpected Librarian six-record contract")
    out = []
    for claim in CLAIMS:
        rid = claim["row_id"]
        require(rid in contract, "motif source not in immutable librarian contract")
        require(sha(canonical(claim)) == REVIEWED_CLAIM_PINS[rid], "reviewed source-kind/section/motif/evidence tuple altered")
        source = contract[rid]
        require(source["medium"] == claim["medium"] and source["identity_scope"] == "SOURCE_LOCAL", "medium or global identity changed")
        require((source["title"], source["source_reference_url"]) == SOURCE_PINS[rid], "source title or first-party URL changed")
        require(source["verification_status"] == "UNVERIFIED_METADATA" and source["admission_effect"] == source["coverage_effect"] == "NONE", "source record promoted")
        require(source["edition_identifier"] is None, "edition identity falsely asserted")
        require(claim["motif_id"] in SCENES and claim["motif_id"] in REVIEWED_SCENE_PINS, "unrenderable visual theme")
        require((rid in PAGE_EDITION_LISTINGS) == (claim["medium"] == "LITERATURE"), "edition listing/medium mismatch")
        if rid in PAGE_EDITION_LISTINGS:
            require(sha(canonical(PAGE_EDITION_LISTINGS[rid])) == REVIEWED_EDITION_LISTING_PINS[rid], "publisher-reported ISBN/format listing altered")
        require(source["source_reference_url"].startswith("https://www."), "untrusted provenance URL")
        hashes = tuple(sha(x.encode("utf-8")) for x in claim["excerpts"])
        require(hashes == EXCERPT_PINS[rid], "publisher-description cue modified from reviewed source")
        require(len(claim["excerpts"]) == len(claim["motif_elements"]) == 2, "motif-to-evidence trace count")
        out.append({
            "source_local_row_id": rid, "medium": source["medium"], "title": source["title"],
            "source_reference_url": source["source_reference_url"], "source_group": source["source_group"],
            "source_input": source["source_input"], "official_section": claim["section"],
            "source_kind": claim["source_kind"], "publisher_page_full_html_sha256": None,
            "source_text_scope": "SHORT_EXACT_FIRST_PARTY_PAGE_CUES_NOT_FULL_FILM_OR_BOOK",
            "source_cues": list(claim["excerpts"]), "source_cue_sha256": list(hashes),
            "motif_evidence_links": [{"cue_index": i, "illustrative_element": element} for i, element in enumerate(claim["motif_elements"])],
            "motif_id": claim["motif_id"], "art_class": "ORIGINAL_INTERPRETIVE_GEOMETRY_NOT_SOURCE_IMAGE",
            "verification_status": "UNVERIFIED_METADATA", "identity_scope": "SOURCE_LOCAL",
            "edition_identifier": None, "film_or_book_close_read": False,
            "publisher_page_edition_listing": PAGE_EDITION_LISTINGS.get(rid),
            "publisher_edition_listing_admitted": False,
            "official_image_rights_grant": "NONE", "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    require(len({r["source_local_row_id"] for r in out}) == 4, "duplicate source-local record")
    return out


def _base(bg: str) -> str:
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#d8ebff" opacity=".36"/>' for x,y,r in ((53,36,2),(166,85,1),(315,42,1),(483,77,2),(697,49,1),(745,166,1),(83,250,1)))
    return f'<rect width="800" height="450" fill="{bg}"/>' + stars


def _legacy_future() -> str:
    return _base("#16203e") + '''
    <path d="M 51 320 C 173 312 240 270 314 206 S 482 90 624 98" stroke="#ffc17e" stroke-width="20" fill="none" opacity=".8"/>
    <path d="M 52 78 C 173 102 237 172 313 206 S 492 309 734 238" stroke="#9bcaf0" stroke-width="19" fill="none" opacity=".9"/>
    <path d="M 314 206 l-23 -24 l0 48z" fill="#efcad1"/>
    <circle cx="315" cy="206" r="50" fill="none" stroke="#f6e5aa" stroke-width="8"/>
    <circle cx="624" cy="98" r="37" fill="none" stroke="#ffac7d" stroke-width="7"/>
    <path d="M 597 66 L 653 130 M 597 129 L 653 66" stroke="#ffac7d" stroke-width="6"/>
    <path d="M 120 62 V 337 M 676 75 V 288" stroke="#8e97d2" stroke-dasharray="10 15" opacity=".65"/>
    <text x="74" y="281" fill="#fbd6ae" font-size="16" font-family="sans-serif">LEGACY</text>
    <text x="655" y="330" fill="#c3dcfa" font-size="16" font-family="sans-serif">FUTURE</text>'''


def _mirror_weapon() -> str:
    return _base("#22152f") + '''
    <path d="M 44 74 L 283 103 L 355 205 L 283 307 L 44 329 L 183 202 Z" fill="#324b6a" stroke="#80bed1" stroke-width="8"/>
    <path d="M 756 74 L 517 103 L 445 205 L 517 307 L 756 329 L 617 202 Z" fill="#602d50" stroke="#eab0c3" stroke-width="8"/>
    <path d="M 400 48 V 338" stroke="#fcb472" stroke-width="5" stroke-dasharray="22 12"/>
    <path d="M 330 176 L 470 176 L 493 205 L 470 234 L 330 234 L 307 205 Z" fill="#df5b75" stroke="#ffe3a9" stroke-width="6"/>
    <path d="M 232 205 L 112 200 M 568 205 L 688 200" stroke="#f37496" stroke-width="10" opacity=".8"/>
    <path d="M 374 155 L 426 255 M 426 155 L 374 255" stroke="#ffe3a9" stroke-width="5"/>
    <circle cx="400" cy="205" r="95" fill="none" stroke="#fc9e87" stroke-width="3" opacity=".4"/>'''


def _delta_journal() -> str:
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f5dbab"/>' for x,y,r in ((167,126,4),(221,174,3),(308,102,4),(392,214,4),(480,140,4),(588,190,5)))
    return _base("#142d42") + '''
    <path d="M 80 80 Q 236 47 396 83 V 316 Q 235 281 80 326 Z" fill="#f0dbb3" stroke="#d6b67f" stroke-width="8"/>
    <path d="M 396 83 Q 560 43 720 81 V 326 Q 559 280 396 316 Z" fill="#f4e4c4" stroke="#d6b67f" stroke-width="8"/>
    <path d="M 396 85 V 315" stroke="#916c60" stroke-width="9"/>
    <path d="M 113 284 Q 235 256 348 287 M 452 287 Q 572 256 690 283" stroke="#ad9476" stroke-width="3" fill="none"/>''' + stars + '''
    <path d="M 167 126 Q 192 142 221 174 T 308 102 T 392 214 T 480 140 T 588 190" fill="none" stroke="#355d8b" stroke-width="8" stroke-dasharray="12 10"/>
    <path d="M 581 182 l22 8 l-15 19" fill="none" stroke="#355d8b" stroke-width="7"/>
    <text x="104" y="113" fill="#45627a" font-size="17" font-family="sans-serif">A JOURNEY RECORDED</text>'''


def _accretion_station() -> str:
    return _base("#0f1735") + '''
    <ellipse cx="393" cy="195" rx="240" ry="88" fill="none" stroke="#f2a56b" stroke-width="26" opacity=".78"/>
    <ellipse cx="393" cy="195" rx="205" ry="63" fill="none" stroke="#df697e" stroke-width="13" opacity=".73"/>
    <circle cx="394" cy="196" r="70" fill="#030911" stroke="#c7b2c8" stroke-width="6"/>
    <path d="M 226 174 C 306 141 494 121 579 166" stroke="#ffdc99" stroke-width="13" fill="none" opacity=".75"/>
    <path d="M 224 211 C 294 256 492 266 584 224" stroke="#9f6aad" stroke-width="11" fill="none"/>
    <path d="M 382 53 L 433 56 L 442 86 L 370 86 Z" fill="#8ab7cb" stroke="#d7e6ea" stroke-width="5"/>
    <path d="M 398 86 L 398 124" stroke="#d4dbe2" stroke-width="5"/>
    <path d="M 319 63 H 372 M 443 63 H 495" stroke="#aac9df" stroke-width="8"/>
    <path d="M 308 39 L 308 85 M 505 39 L 505 85" stroke="#aac9df" stroke-width="5"/>
    <circle cx="398" cy="53" r="7" fill="#f5d18a"/>'''


SCENES = {"legacy-future": _legacy_future, "mirror-weapon": _mirror_weapon,
          "delta-journal": _delta_journal, "accretion-station": _accretion_station}


def render(record: dict) -> bytes:
    require(record in bound_inputs(), "motif must be exactly source-evidence-bound")
    theme = record["motif_id"]
    require(theme in SCENES, "unapproved motif")
    require(sha(SCENES[theme]().encode("utf-8")) == REVIEWED_SCENE_PINS[theme], "reviewed motif scene body reassigned or changed")
    caption = "FILM SOURCE" if record["medium"] == "FILM" else "LITERARY SOURCE"
    title = escape(record["title"])
    art = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" aria-label="Original source-derived thematic index interpretation; not an official film still or book cover">{SCENES[theme]()}
    <rect y="348" width="800" height="102" fill="#0e1524" opacity=".97"/>
    <text x="30" y="375" fill="#f0c58e" font-family="sans-serif" font-size="17">{caption} · ORIGINAL THEMATIC INTERPRETATION</text>
    <text x="30" y="407" fill="#fff3e1" font-family="sans-serif" font-size="27" font-weight="700">{title}</text>
    <text x="30" y="433" fill="#d7e2f0" font-family="sans-serif" font-size="13">NOT OFFICIAL ART · NO FILM/BOOK CLOSE READ · SOURCE-LOCAL</text>
    </svg>'''
    ET.fromstring(art)
    lower = art.lower()
    require(not any(x in lower for x in ("<image", "<script", "<foreignobject", "href=", "javascript:", "data:", "<use ")), "external or active SVG content")
    return (art + "\n").encode("utf-8")


def expected() -> dict[Path, bytes]:
    records = bound_inputs()
    files: dict[Path, bytes] = {}
    manifest = []
    for rec in records:
        path = OUT / "art" / (rec["motif_id"] + ".svg")
        img = render(rec)
        files[path] = img
        manifest.append({**rec, "art_path": "art/" + path.name, "art_sha256": sha(img)})
    files[OUT / "manifest.json"] = canonical({"status": "HELD_FILM_LITERATURE_INTERPRETIVE_ART_NOT_PUBLIC",
        "accepted_main": MAIN, "source_image_bytes": 0, "admitted_works": 0, "edition_equivalence_asserted": False,
        "film_or_book_close_reads": 0, "coverage_effect": "NONE", "public_release_effect": "NONE", "records": manifest})
    return files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = expected()
    if args.check:
        require(all(p.is_file() and not p.is_symlink() and p.read_bytes() == data for p,data in files.items()), "art file changed or missing")
        require(set((OUT / "art").iterdir()) == {p for p in files if p.parent == OUT / "art"}, "stray visual files")
        print("FILM+LITERATURE THEMATIC ART VERIFIED: 4 originals, 0 source media bytes or admissions")
    else:
        for p, data in files.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            require(not p.is_symlink(), "output symlink refused")
            p.write_bytes(data)
        print("Built four original held film/literature images")


if __name__ == "__main__":
    main()
