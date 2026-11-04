#!/usr/bin/env python3
"""Rebuild 14 original film-record illustrations from held publisher metadata.

These are authored geometric interpretations, NOT Star Trek frames, official
posters, character likenesses, logos, or source evidence. A deterministic art
file does not create an accepted Source/Work or lift the copyright gate for
third-party imagery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
FILMS = ROOT / "explorer/film-catalog.json"
ART = ROOT / "explorer/interpretive-film"

# One editorial motif per exact publisher source-local candidate. The meaning
# is deliberately abstract; it is NOT a depiction or claim of a scene.
DESIGNS = {
    "film-2009": ("branching", "#0b2944", "#72dce5", "#faac77"),
    "film-beyond": ("fragments", "#263958", "#a8b5ee", "#ffbf7c"),
    "film-final-frontier": ("pilgrimage", "#352c57", "#dac1ff", "#ffe093"),
    "film-first-contact": ("portal", "#21475b", "#a4efe0", "#f7c580"),
    "film-generations": ("ribbons", "#4a3162", "#f1bcd2", "#c9dcff"),
    "film-insurrection": ("landscape", "#304b3c", "#b7e2a6", "#f8ce8a"),
    "film-into-darkness": ("shadow", "#4d2b42", "#f3b0b8", "#e8e7ff"),
    "film-motion-picture": ("signal", "#1b3e56", "#86dfed", "#d6c0ff"),
    "film-nemesis": ("mirror", "#392943", "#d7a8da", "#9fe2e3"),
    "film-search-for-spock": ("return", "#204b44", "#8be6c4", "#eec38a"),
    "film-section-31": ("cipher", "#2e344a", "#e0a3a9", "#9fb4f5"),
    "film-undiscovered-country": ("accord", "#4a3956", "#f2d4ac", "#a5dce3"),
    "film-voyage-home": ("tide", "#1b4864", "#8edfea", "#f0cf93"),
    "film-wrath-of-khan": ("opposition", "#512e41", "#f3ada5", "#d6dcfb"),
}


def _motif(name: str, a: str, b: str) -> str:
    """All shapes are hand-authored geometry with no copied visual input."""
    shapes = {
        "branching": f'<path d="M160 375V238M160 238L55 88M160 238L273 78" stroke="{a}" stroke-width="13" fill="none"/><circle cx="55" cy="88" r="29" fill="none" stroke="{b}" stroke-width="7"/><circle cx="273" cy="78" r="38" fill="none" stroke="{a}" stroke-width="8"/>',
        "fragments": f'<path d="M0 230L93 182L137 237L213 162L320 206" fill="none" stroke="{a}" stroke-width="23"/><path d="M73 93l53 28-22 46-46-27zM230 82l53-32 13 63-50 22zM174 271l74-20 17 54-80 17z" fill="{b}" opacity=".83"/>',
        "pilgrimage": f'<path d="M28 380Q105 170 160 75Q220 155 292 380" stroke="{a}" stroke-width="13" fill="none"/><path d="M75 360Q135 240 160 131Q190 240 252 360" stroke="{b}" stroke-width="6" fill="none"/><circle cx="160" cy="74" r="26" fill="{b}"/>',
        "portal": f'<circle cx="160" cy="206" r="114" stroke="{a}" stroke-width="17" fill="none"/><circle cx="160" cy="206" r="73" stroke="{b}" stroke-width="10" fill="none"/><path d="M37 206H284M160 81V330" stroke="{a}" stroke-width="4" opacity=".68"/>',
        "ribbons": f'<path d="M-10 135Q78 29 160 182T335 222" fill="none" stroke="{a}" stroke-width="31" opacity=".72"/><path d="M-10 291Q72 375 160 210T337 147" fill="none" stroke="{b}" stroke-width="19" opacity=".83"/>',
        "landscape": f'<circle cx="242" cy="108" r="54" fill="{b}"/><path d="M0 277Q85 189 150 268T330 239V440H0Z" fill="{a}" opacity=".48"/><path d="M0 336Q88 269 176 314T330 282V440H0Z" fill="{b}" opacity=".46"/>',
        "shadow": f'<path d="M0 112L142 32L206 375L320 296" stroke="{a}" stroke-width="27" fill="none"/><path d="M92 0L189 165L280 0M40 360L170 210L301 360" stroke="{b}" stroke-width="11" fill="none" opacity=".7"/><circle cx="160" cy="190" r="37" fill="{a}"/>',
        "signal": f'<circle cx="164" cy="209" r="107" fill="none" stroke="{a}" stroke-width="4" opacity=".7"/><circle cx="164" cy="209" r="69" fill="none" stroke="{b}" stroke-width="9"/><circle cx="164" cy="209" r="25" fill="{a}"/><path d="M-10 208H330M164 36V375" stroke="{b}" stroke-width="5" opacity=".56"/>',
        "mirror": f'<path d="M40 80L140 145L140 340L40 266ZM280 80L180 145L180 340L280 266Z" fill="{a}" opacity=".53"/><path d="M160 58V358" stroke="{b}" stroke-width="10"/><circle cx="89" cy="182" r="26" fill="{b}"/><circle cx="231" cy="182" r="26" fill="{b}"/>',
        "return": f'<circle cx="160" cy="212" r="107" fill="none" stroke="{a}" stroke-width="10"/><path d="M63 206Q90 105 180 105M180 105l-36-37M180 105l-52 20" fill="none" stroke="{b}" stroke-width="18" stroke-linecap="round"/><circle cx="192" cy="230" r="46" fill="{a}" opacity=".63"/>',
        "cipher": f'<path d="M35 64H285V336H35Z" fill="none" stroke="{a}" stroke-width="7"/><path d="M54 103H266M54 143H266M54 183H266M54 223H266M54 263H266M54 303H266" stroke="{a}" stroke-width="5" opacity=".32"/><path d="M84 92V311M160 92V311M237 92V311" stroke="{b}" stroke-width="6" opacity=".45"/><circle cx="160" cy="183" r="25" fill="{a}"/>',
        "accord": f'<path d="M24 311Q82 92 160 191Q240 92 296 311" stroke="{a}" stroke-width="23" fill="none"/><path d="M42 306H278" stroke="{b}" stroke-width="12"/><circle cx="101" cy="112" r="22" fill="{b}"/><circle cx="219" cy="112" r="22" fill="{a}"/>',
        "tide": f'<path d="M-10 164Q40 109 90 164T190 164T290 164T390 164M-10 224Q40 170 90 224T190 224T290 224T390 224M-10 284Q40 230 90 284T190 284T290 284T390 284" fill="none" stroke="{a}" stroke-width="16" opacity=".8"/><path d="M93 89Q160 24 227 89L160 132Z" fill="{b}" opacity=".91"/>',
        "opposition": f'<path d="M-10 351L116 92L145 351Z" fill="{a}" opacity=".73"/><path d="M332 351L207 92L175 351Z" fill="{b}" opacity=".8"/><circle cx="160" cy="205" r="35" fill="none" stroke="{a}" stroke-width="8"/>',
    }
    return shapes[name]


def _svg(ident: str, title: str, design: tuple[str, str, str, str]) -> bytes:
    motif, bg, a, b = design
    seed = hashlib.sha256(ident.encode("ascii")).digest()
    stars = "".join(
        f'<circle cx="{13 + seed[i] * 294 // 255}" cy="{17 + seed[i + 14] * 352 // 255}" '
        f'r="{1 + seed[i] % 2}" fill="#fff" opacity=".36"/>'
        for i in range(14)
    )
    markup = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 430">'
        f'<title>Original interpretive film-record art for {escape(title)}</title>'
        '<desc>Geometric art made for this source-local metadata entry. Not an official poster or still.</desc>'
        '<defs><linearGradient id="ground" x2="1" y2="1">'
        f'<stop stop-color="{bg}"/><stop offset="1" stop-color="#090b19"/>'
        '</linearGradient></defs>'
        '<rect width="320" height="430" fill="url(#ground)"/>'
        + stars + _motif(motif, a, b)
        + '<path d="M0 28H276Q308 28 308 60" fill="none" stroke="'
        + a + '" stroke-width="9"/>'
        '</svg>\n'
    )
    return markup.encode("utf-8")


def expected() -> dict[Path, bytes]:
    catalog = json.loads(FILMS.read_text(encoding="utf-8"))
    if (catalog.get("schema_version") != "1.0.0" or
            catalog.get("data_status") != "DISCOVERY_ONLY" or
            catalog.get("coverage_effect") != "NONE" or
            catalog.get("source_group") != "publisher:startrek.com" or
            catalog.get("film_count") != 14 or not isinstance(catalog.get("films"), list)):
        raise ValueError("film metadata does not match the held publisher catalog")
    films = catalog["films"]
    if {item.get("id") for item in films} != set(DESIGNS) or len(films) != 14:
        raise ValueError("film illustration set diverges from source-local film identities")
    result: dict[Path, bytes] = {}
    records = []
    for item in sorted(films, key=lambda row: row["id"]):
        ident = item["id"]
        locator = item.get("source_locator")
        if (item.get("source_group") != "publisher:startrek.com" or
                item.get("verification_status") != "UNVERIFIED_METADATA" or
                not isinstance(locator, str) or
                not locator.startswith("https://www.startrek.com/") or
                not isinstance(item.get("title"), str) or not item["title"]):
            raise ValueError("film illustration has no valid source-local title/locator")
        path = ART / f"{ident}.svg"
        art = _svg(ident, item["title"], DESIGNS[ident])
        result[path] = art
        records.append({
            "source_local_film_id": ident,
            "title": item["title"],
            "metadata_source": locator,
            "art_path": f"interpretive-film/{ident}.svg",
            "art_sha256": hashlib.sha256(art).hexdigest(),
            "motif": DESIGNS[ident][0],
            "rights_class": "ORIGINAL_AUTHOR_CREATED_GEOMETRIC_ART",
            "artwork_status": "ORIGINAL_INTERPRETATION_NOT_SOURCE_IMAGE",
            "coverage_effect": "NONE",
        })
    manifest = {
        "schema_version": "1.0.0", "data_status": "DISPLAY_ONLY",
        "source_scope": "EXACT_HELD_PUBLISHER_FILM_CANDIDATES",
        "coverage_effect": "NONE", "admission_effect": "NONE",
        "original_art_count": len(records), "art": records,
    }
    result[ART / "manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    files = expected()
    if args.check:
        if not ART.is_dir() or ART.is_symlink() or set(ART.iterdir()) != set(files):
            raise SystemExit("original film art directory membership differs from the pinned catalog")
        for path, content in files.items():
            if not path.is_file() or path.is_symlink() or path.read_bytes() != content:
                raise SystemExit(f"original film art changed: {path.name}")
    else:
        ART.mkdir(parents=True, exist_ok=True)
        if ART.is_symlink() or (set(ART.iterdir()) - set(files)):
            raise SystemExit("refusing to overwrite a non-catalog art directory")
        for path, content in files.items():
            if path.is_symlink():
                raise SystemExit("refusing to follow image symlink")
            path.write_bytes(content)


if __name__ == "__main__":
    main()
