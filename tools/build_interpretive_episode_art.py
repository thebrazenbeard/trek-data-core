#!/usr/bin/env python3
"""Deterministic, original geometric art for 22 held TNG season-two episode listings.

Artwork is an *interpretation of a metadata title*, never a production frame,
episode observation, character likeness, licensed emblem, or research evidence.
The source-local records remain UNVERIFIED_METADATA with no coverage effect.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "explorer/discovery-catalog.json"
ART = ROOT / "explorer/interpretive-episode"
LOCATOR = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/"
SOURCE_GROUP = "publisher:paramount"
SOURCE_INPUT = "proposals/discovery/legacy-paramount-season2-20261102/tng/bundle.json"

# The accepted discovery-roster identities are literal editorial pins, not
# deduced from whatever a future untrusted catalog happens to contain.
TITLES = (
    "The Child", "Where Silence Has Lease", "Elementary, Dear Data",
    "The Outrageous Okona", "Loud as a Whisper", "The Schizoid Man",
    "Unnatural Selection", "A Matter of Honor", "The Measure of a Man",
    "The Dauphin", "Contagion", "The Royale", "Time Squared",
    "The Icarus Factor", "Pen Pals", "Q-Who?", "Samaritan Snare",
    "Up the Long Ladder", "Manhunt", "The Emissary", "Peak Performance",
    "Shades of Gray",
)

# Twenty-two distinguishable hand-designed abstract motifs; the title can
# inspire shape vocabulary, but a drawn shape never claims a fictional event.
DESIGNS = (
    ("cradle", "#1c3f56", "#8ae3df", "#ffd19b"),
    ("quiet", "#303a62", "#aec7fa", "#e0b8f3"),
    ("deduction", "#293e50", "#92dbeb", "#ffcf94"),
    ("motion", "#533a59", "#f1abd0", "#9fe4ef"),
    ("whisper", "#264c58", "#a6e8d9", "#e9c4ff"),
    ("dual", "#4d3059", "#ddb8fa", "#f5bd8d"),
    ("branch", "#2f5148", "#a8edb7", "#c3c1ff"),
    ("honor", "#4d3545", "#ffc3a1", "#bee6ef"),
    ("measure", "#2f4b62", "#b9d7ff", "#eecd97"),
    ("crown", "#513654", "#efc1e0", "#f6e29d"),
    ("spread", "#344b59", "#9ce2ed", "#f5aaac"),
    ("royale", "#4d3752", "#e8bcff", "#f4d18e"),
    ("doubletime", "#2a475d", "#99cafa", "#eac6e8"),
    ("ascent", "#4d3d60", "#cbbefa", "#ffcf92"),
    ("correspond", "#27525b", "#9be9da", "#fbd2ad"),
    ("unknown", "#443b68", "#b5b9f8", "#f4b3cb"),
    ("snare", "#3a4d4b", "#a8e1c2", "#f2c6a8"),
    ("ladder", "#423e58", "#c9c9f6", "#f1bb9c"),
    ("pursuit", "#4c3b49", "#efb8ad", "#b5e3ec"),
    ("dispatch", "#294d66", "#a1dcfa", "#f2d49a"),
    ("summit", "#3c5360", "#b3e4e9", "#f6c6a2"),
    ("grayscale", "#3b4657", "#dee8f4", "#9baabe"),
)

# Reviewer-facing, title-only art direction. These are NOT conclusions from
# transcripts, scene descriptions, character arcs, or close reads.
MOTIF_NOTES = (
    "Child: a small circular form above a protective cradle arc.",
    "Silence: interrupted bands enclose a large quiet central void.",
    "Elementary: a deduction board of gridded cells and a focal node.",
    "Outrageous: energetic off-axis strokes imply unruly motion.",
    "Whisper: faint outgoing waves carry a tiny initial signal.",
    "Schizoid: two opposing asymmetric panels split around one axis.",
    "Selection: a branching graph forks from one origin point.",
    "Honor: balanced angular forms suggest a formal constraint.",
    "Measure: two symmetric hanging geometric masses form a balance.",
    "Dauphin: a title-inspired stylized crown of angular peaks.",
    "Contagion: radial links extend from one central node.",
    "Royale: two overlapping squares and contrasting pips.",
    "Squared: two offset rectangular time frames intersect.",
    "Icarus: an abstract steep ascent toward a bright point.",
    "Pen pals: two separated endpoints exchange curved signals.",
    "Who: an incomplete curved path ends at an unresolved point.",
    "Snare: intersecting lines converge inside a circular boundary.",
    "Ladder: evenly spaced rungs ascend between two rails.",
    "Manhunt: crossing vector trails enter a circular locator.",
    "Emissary: a folded envelope outline and converging lines.",
    "Peak: a sharp mountain-like apex and contrasting highlight.",
    "Gray: layered bars progress through neutral tonal values.",
)


def _motif(name: str, a: str, b: str) -> str:
    # No SVG text, image, foreignObject, script, links, or external resources.
    motifs = {
        "cradle": f'<path d="M38 272Q160 359 282 272" stroke="{a}" stroke-width="24" fill="none"/><circle cx="160" cy="167" r="65" fill="none" stroke="{b}" stroke-width="11"/><circle cx="160" cy="167" r="20" fill="{a}"/>',
        "quiet": f'<rect x="55" y="68" width="210" height="290" rx="20" stroke="{a}" stroke-width="9" fill="none"/><path d="M65 183H130M190 183H255M160 104V145M160 244V318" stroke="{b}" stroke-width="15"/>',
        "deduction": f'<path d="M34 101H286V319H34Z" stroke="{a}" stroke-width="9" fill="none"/><path d="M54 173H266M54 245H266M111 111V309M210 111V309" stroke="{b}" stroke-width="5" opacity=".75"/><circle cx="159" cy="209" r="27" fill="{a}"/>',
        "motion": f'<path d="M-25 316Q82 72 281 91M27 351Q170 136 352 247" stroke="{a}" stroke-width="22" fill="none"/><circle cx="243" cy="90" r="32" fill="{b}"/><path d="M35 106L94 72L125 119" stroke="{b}" stroke-width="10" fill="none"/>',
        "whisper": f'<circle cx="66" cy="210" r="17" fill="{b}"/><path d="M90 210Q150 152 150 210T215 210M90 210Q170 90 240 210M90 210Q180 36 292 210" stroke="{a}" stroke-width="8" fill="none" opacity=".9"/>',
        "dual": f'<path d="M48 90Q123 52 143 178L142 331Q78 281 48 90Z" fill="{a}" opacity=".68"/><path d="M272 90Q197 52 177 178L178 331Q242 281 272 90Z" fill="{b}" opacity=".7"/><path d="M160 60V351" stroke="{a}" stroke-width="7"/>',
        "branch": f'<path d="M160 363V240M160 240L72 153M160 240L251 151M72 153L57 84M72 153L23 137M251 151L295 92M251 151L281 199" stroke="{a}" stroke-width="13" fill="none"/><circle cx="160" cy="240" r="23" fill="{b}"/>',
        "honor": f'<path d="M160 42L277 136L231 332L160 373L89 332L43 136Z" fill="none" stroke="{a}" stroke-width="12"/><path d="M83 225L160 291L237 225M160 55V289" fill="none" stroke="{b}" stroke-width="11"/>',
        "measure": f'<path d="M160 57V356M65 114H255M72 114L30 225H114L72 114ZM248 114L206 225H290L248 114Z" stroke="{a}" stroke-width="10" fill="none"/><path d="M97 355H223" stroke="{b}" stroke-width="17"/><circle cx="160" cy="96" r="24" fill="{b}"/>',
        "crown": f'<path d="M38 275L62 119L127 202L160 76L195 202L261 119L282 275Z" fill="{a}" opacity=".6"/><path d="M38 286H282M58 315H262" stroke="{b}" stroke-width="13"/>',
        "spread": f'<circle cx="160" cy="207" r="39" fill="{b}"/><path d="M160 207L52 94M160 207L273 89M160 207L45 319M160 207L280 310M160 207V47M160 207V375" stroke="{a}" stroke-width="13"/><circle cx="52" cy="94" r="18" fill="{a}"/><circle cx="280" cy="310" r="18" fill="{a}"/>',
        "royale": f'<path d="M44 83H172V239H44ZM149 172H277V340H149Z" stroke="{a}" stroke-width="11" fill="none"/><circle cx="88" cy="126" r="13" fill="{b}"/><circle cx="131" cy="197" r="13" fill="{b}"/><circle cx="214" cy="226" r="13" fill="{b}"/><circle cx="187" cy="299" r="13" fill="{b}"/>',
        "doubletime": f'<rect x="44" y="76" width="190" height="230" rx="6" stroke="{a}" stroke-width="12" fill="none"/><rect x="88" y="126" width="190" height="230" rx="6" stroke="{b}" stroke-width="10" fill="none"/><path d="M160 145V227L213 265" stroke="{a}" stroke-width="9" fill="none"/>',
        "ascent": f'<path d="M30 355L135 111L162 194L217 54L292 355" stroke="{a}" stroke-width="19" fill="none"/><path d="M160 248L214 121L267 250" fill="{b}" opacity=".62"/><circle cx="218" cy="63" r="20" fill="{b}"/>',
        "correspond": f'<circle cx="73" cy="189" r="45" stroke="{a}" stroke-width="11" fill="none"/><circle cx="244" cy="230" r="45" stroke="{b}" stroke-width="11" fill="none"/><path d="M115 189Q162 117 204 224M118 197Q169 313 200 245" stroke="{a}" stroke-width="7" fill="none"/><path d="M192 211L210 225L218 203" stroke="{b}" stroke-width="8" fill="none"/>',
        "unknown": f'<path d="M91 128Q115 56 190 82Q260 110 201 184Q169 211 160 256" stroke="{a}" stroke-width="22" fill="none" stroke-linecap="round"/><circle cx="160" cy="324" r="24" fill="{b}"/><path d="M71 355H249" stroke="{a}" stroke-width="4" opacity=".45"/>',
        "snare": f'<circle cx="160" cy="207" r="110" stroke="{a}" stroke-width="10" fill="none"/><path d="M51 111L269 307M51 307L269 111M160 97V318M50 207H270" stroke="{b}" stroke-width="8" opacity=".75"/><circle cx="160" cy="207" r="25" fill="{a}"/>',
        "ladder": f'<path d="M95 366L139 58M221 366L178 58" stroke="{a}" stroke-width="17" fill="none"/><path d="M108 292H207M119 222H198M128 153H187M137 84H179" stroke="{b}" stroke-width="12"/><circle cx="160" cy="45" r="15" fill="{b}"/>',
        "pursuit": f'<circle cx="160" cy="213" r="106" stroke="{a}" stroke-width="6" fill="none"/><circle cx="160" cy="213" r="60" stroke="{b}" stroke-width="7" fill="none"/><path d="M6 311L102 228M214 191L311 107" stroke="{a}" stroke-width="21"/><circle cx="160" cy="213" r="18" fill="{a}"/>',
        "dispatch": f'<path d="M34 116L160 197L286 116M34 116H286V296H34Z" fill="none" stroke="{a}" stroke-width="12"/><path d="M39 287L128 209M281 287L190 209" stroke="{b}" stroke-width="8"/><circle cx="160" cy="199" r="17" fill="{b}"/>',
        "summit": f'<path d="M0 342L76 255L137 298L210 92L320 340" stroke="{a}" stroke-width="19" fill="none"/><path d="M170 203L210 91L252 205" fill="{b}" opacity=".86"/><circle cx="210" cy="67" r="20" fill="{b}"/>',
        "grayscale": f'<rect x="44" y="92" width="46" height="259" fill="{a}" opacity=".34"/><rect x="101" y="72" width="47" height="279" fill="{a}" opacity=".58"/><rect x="159" y="105" width="47" height="246" fill="{a}" opacity=".79"/><rect x="217" y="84" width="47" height="267" fill="{b}"/><path d="M39 351H280" stroke="{a}" stroke-width="7"/>',
    }
    return motifs[name]


def _svg(row_id: str, title: str, design: tuple[str, str, str, str]) -> bytes:
    motif, background, a, b = design
    seed = hashlib.sha256(f"{row_id}|{title}".encode("utf-8")).digest()
    stars = "".join(
        f'<circle cx="{15 + seed[i] * 290 // 255}" cy="{20 + seed[i + 13] * 365 // 255}" '
        f'r="{1 + seed[i] % 2}" fill="#fff" opacity=".32"/>'
        for i in range(13)
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 430">'
        f'<title>Original interpretive episode-record art for {escape(title)}</title>'
        '<desc>Geometric design inspired by the metadata title only. Not an episode still or source evidence.</desc>'
        '<defs><linearGradient id="ground" x2="1" y2="1">'
        f'<stop stop-color="{background}"/><stop offset="1" stop-color="#090b19"/>'
        '</linearGradient></defs><rect width="320" height="430" fill="url(#ground)"/>'
        + stars + _motif(motif, a, b)
        + f'<path d="M0 30H279Q309 30 309 61" stroke="{a}" stroke-width="9" fill="none"/>'
        + '</svg>\n'
    )
    return svg.encode("utf-8")


def expected() -> dict[Path, bytes]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows = [row for row in catalog.get("rows", []) if
            row.get("medium") == "EPISODE" and
            isinstance(row.get("context"), str) and row["context"].startswith("TNG S2E")]
    if len(rows) != 22:
        raise ValueError("TNG season-two discovery roster is not exactly 22 source-local rows")
    actual = {row.get("row_id"): row for row in rows}
    ids = {f"legacy:s2:tng:{index:03d}" for index in range(22)}
    if set(actual) != ids:
        raise ValueError("TNG season-two source-local IDs changed")
    result: dict[Path, bytes] = {}
    manifest_rows = []
    for index, title in enumerate(TITLES):
        row_id = f"legacy:s2:tng:{index:03d}"
        row = actual[row_id]
        context = f"TNG S2E{index + 1}"
        if any((row.get("title") != title,
                row.get("context") != context,
                row.get("source_locator") != LOCATOR,
                row.get("source_group") != SOURCE_GROUP,
                row.get("source_input") != SOURCE_INPUT,
                row.get("verification_status") != "UNVERIFIED_METADATA",
                row.get("identity_scope") != "SOURCE_LOCAL",
                row.get("admission_effect") != "NONE",
                row.get("coverage_effect") != "NONE")):
            raise ValueError(f"TNG source tuple or provenance mismatch: {row_id}")
        art_id = f"tng-s2-{index + 1:03d}"
        data = _svg(row_id, title, DESIGNS[index])
        result[ART / f"{art_id}.svg"] = data
        manifest_rows.append({
            "source_local_row_id": row_id,
            "title": title,
            "context": context,
            "source_group": SOURCE_GROUP,
            "source_locator": LOCATOR,
            "source_input": SOURCE_INPUT,
            "art_path": f"interpretive-episode/{art_id}.svg",
            "art_sha256": hashlib.sha256(data).hexdigest(),
            "motif": DESIGNS[index][0],
            "interpretive_basis": "TITLE_ONLY",
            "motif_note": MOTIF_NOTES[index],
            "rights_class": "ORIGINAL_AUTHOR_CREATED_GEOMETRIC_ART",
            "artwork_status": "ORIGINAL_TITLE_INTERPRETATION_NOT_SOURCE_IMAGE",
            "coverage_effect": "NONE",
            "admission_effect": "NONE",
        })
    manifest = {
        "schema_version": "1.0.0", "data_status": "DISPLAY_ONLY",
        "source_scope": "ACCEPTED_DISCOVERY_TNG_SEASON2_HELD_METADATA",
        "coverage_effect": "NONE", "admission_effect": "NONE",
        "original_art_count": len(manifest_rows), "art": manifest_rows,
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
            raise SystemExit("original episode-art directory membership differs from pinned source roster")
        for path, content in files.items():
            if not path.is_file() or path.is_symlink() or path.read_bytes() != content:
                raise SystemExit(f"original episode artwork changed: {path.name}")
    else:
        ART.mkdir(parents=True, exist_ok=True)
        if ART.is_symlink() or (set(ART.iterdir()) - set(files)):
            raise SystemExit("refusing to overwrite unrecognized episode-art directory contents")
        for path, content in files.items():
            if path.is_symlink():
                raise SystemExit("refusing to follow episode artwork symlink")
            path.write_bytes(content)


if __name__ == "__main__":
    main()
