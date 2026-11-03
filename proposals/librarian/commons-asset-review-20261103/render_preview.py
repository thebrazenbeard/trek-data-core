"""Generate a local LCARS-styled candidate review, with no image network loads.

The output is intentionally NOT an Explorer/public Pages artifact. Its links
navigate to source description pages only after a deliberate user click.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path

from validate import CATALOG, PACKET, validate


def render(packet: dict, catalog: dict) -> str:
    validate(packet, catalog)
    photo = packet["commons_photo_candidate"]
    book = packet["edition_cover_candidate"]
    film = packet["film_thumbnail_candidate"]

    def link(url: str, label: str) -> str:
        return (f'<a href="{escape(url, quote=True)}" rel="noreferrer noopener" '
                f'target="_blank">{escape(label)}</a>')

    def card(heading: str, subtitle: str, status: str, body: str) -> str:
        return (f'<section class="card"><div class="plate" aria-hidden="true">'
                f'<span>VISUAL HELD</span></div><div class="copy"><p class="tag">'
                f'{escape(status)}</p><h2>{escape(heading)}</h2><p>{escape(subtitle)}</p>'
                f'{body}</div></section>')

    photo_card = card(
        "Commons / TOS prop exhibit", "Museum photograph candidate — not an episode still",
        "LICENSE CLAIM CHECKED · SUBJECT IP HOLD",
        f'<p class="credit">{escape(photo["attribution_text"])}</p>'
        f'<p>{link(photo["file_page"], "View Commons file and license page")}</p>'
        f'<p>{link(photo["original_source"], "View original Flickr listing")}</p>'
        f'<p class="hold">No photo pixels were loaded. The CC claim is for the photograph; '
        f'rights in depicted Star Trek prop designs remain unresolved.</p>')
    book_card = card(
        "Ring of Fire / hardcover", f'Publisher ISBN {book["isbn13"]}',
        "OFFICIAL JPG LISTED · REUSE PERMISSION ABSENT",
        f'<p>{link(book["official_product_page"], "View exact Simon & Schuster edition")}</p>'
        f'<p>{link(book["permissions_terms"], "View publisher site terms")}</p>'
        f'<p class="hold">This link is not permission to reproduce the book jacket.</p>')
    film_card = card(
        "The Wrath of Khan / film", "Official studio page displays poster art",
        "OFFICIAL POSTER LOCATED · RIGHTS UNVERIFIED",
        f'<p>{link(film["official_film_page"], "View original studio film page")}</p>'
        f'<p class="hold">The studio retains film and poster rights; no image URL was imported.</p>')

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'none'; media-src 'none'; connect-src 'none'; frame-src 'none'; script-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Artwork Review Deck — Not a Public Release</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#11131b;color:#f3e8ff}
body{margin:0;max-width:1080px;padding:1.5rem;margin-inline:auto}
header{display:grid;grid-template-columns:120px 1fr;gap:1rem;align-items:center}
.arch{height:96px;background:#eead80;border-radius:5.5rem 1rem 0 0}
h1{font-size:clamp(1.4rem,4vw,2.6rem);margin:.3rem 0}
header p,.intro{color:#e7d9e6}
.stripe{height:18px;background:linear-gradient(90deg,#eead80 0 26%,#11131b 26% 28%,#b995ed 28% 66%,#11131b 66% 68%,#91a8ff 68%);border-radius:18px;margin:1.2rem 0}
.card{display:grid;grid-template-columns:minmax(125px,32%) 1fr;gap:1rem;margin:1.1rem 0;padding:1rem;background:#202536;border-left:18px solid #ddabec;border-radius:0 1rem 1rem 0}
.plate{min-height:160px;background:repeating-linear-gradient(120deg,#2b3445 0 24px,#232a39 24px 48px);border:2px dashed #ddabec;display:grid;place-items:center;color:#ffcb94;font-size:1.1rem;font-weight:800;letter-spacing:.12em}
.copy p{line-height:1.45}.tag{font-size:.7rem;font-weight:800;letter-spacing:.08em;color:#ffbd95;margin:0}
h2{margin:.35rem 0;font-size:1.3rem}a{color:#b9cdfb;text-underline-offset:.18rem}
.credit{font-size:.9rem;color:#e6e0fa}.hold{color:#ffcfbd;border-top:1px solid #67718b;padding-top:.5rem}
footer{padding:1rem;margin-top:1rem;background:#473657;border-radius:0 2rem 2rem 0}
@media(max-width:540px){.card{grid-template-columns:1fr}.plate{min-height:90px}header{grid-template-columns:54px 1fr}.arch{height:70px}}
</style>
</head>
<body><header><div class="arch" aria-hidden="true"></div><div><p>LCARS • LIBRARIAN REVIEW ONLY</p>
<h1>Artwork Candidate Deck</h1><p>Three source-specific routes. Zero released images.</p></div></header>
<div class="stripe" aria-hidden="true"></div>
<p class="intro">This is an offline rights-and-identity review preview, not public Explorer artwork. Placeholder panels are CSS; no image elements, requests, embedded media, or third-party scripts.</p>
<main>""" + photo_card + book_card + film_card + """</main>
<footer><strong>RELEASE HOLD</strong> · Each asset needs its own exact-row/edition binding, rights decision, attribution, byte digest and separately reviewed display package. No blanket approval follows from a Commons file page, a publisher cover download, or a studio poster.</footer>
</body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="explicit private/local HTML destination")
    args = parser.parse_args(argv)
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    page = render(packet, catalog)
    if args.output:
        # Refuse overwrites, symlinks, and any path under the public repository.
        dest = args.output.resolve(strict=False)
        if dest.is_relative_to(Path(__file__).resolve().parents[3]) or dest.exists():
            raise ValueError("preview destination must be a fresh, non-repository local file")
        with dest.open("x", encoding="utf-8") as out:
            out.write(page)
        print(f"Offline candidate review written to {dest}")
    else:
        print("Candidate preview valid (in memory only): " + str(len(page)) + " HTML characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
