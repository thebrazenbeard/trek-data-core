"""Original, abstract SVG card *proposal*; never a Trek still or official cover.

No external assets, network calls, unsafe SVG elements, franchise marks or
episode-depicting claims. The caller must label the result as abstract art.
The script itself does not publish assets or change the Explorer.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import unicodedata
from xml.sax.saxutils import escape


MEDIA = {
    "EPISODE": ("#1b4f64", "#f0b568", "EPISODE OBSERVATION"),
    "FILM": ("#562c4c", "#e5a6b8", "FILM OBSERVATION"),
    "LITERATURE": ("#60432a", "#f3ca82", "LITERARY OBSERVATION"),
    "SHORT_FORM": ("#34487f", "#abbaf8", "SHORT-FORM OBSERVATION"),
    "AUDIO": ("#385850", "#9de2cc", "AUDIO OBSERVATION"),
}


def _clean(value: str, field: str, limit: int) -> str:
    if not isinstance(value, str) or not (0 < len(value) <= limit):
        raise ValueError(f"{field} must be a nonempty bounded string")
    if any(unicodedata.category(character) in {"Cc", "Cs"} for character in value):
        raise ValueError(f"{field} contains disallowed control characters")
    return value


def _wrapped(title: str, width: int = 29, max_lines: int = 3) -> list[str]:
    words = re.findall(r"\S+", title)
    lines: list[str] = []
    for word in words:
        if len(word) > width:
            word = word[: width - 1] + "…"
        if lines and len(lines[-1]) + 1 + len(word) <= width:
            lines[-1] += " " + word
        elif len(lines) < max_lines:
            lines.append(word)
        else:
            lines[-1] = (lines[-1][: width - 1] + "…")
            break
    return lines or ["UNTITLED"]


def render_card(row_id: str, medium: str, title: str) -> str:
    """Generate a reproducible SVG abstract placeholder, not narrative artwork."""
    row_id = _clean(row_id, "row_id", 200)
    title = _clean(title, "title", 240)
    if medium not in MEDIA:
        raise ValueError("unknown medium")
    background, accent, label = MEDIA[medium]
    seed = hashlib.sha256((medium + "\x00" + row_id).encode("utf-8")).digest()
    stars = []
    for i in range(18):
        a = seed[(2 * i) % len(seed)]
        b = seed[(2 * i + 1) % len(seed)]
        x = 18 + (a * 604 // 255)
        y = 16 + (b * 312 // 255)
        radius = 1 if a % 4 else 2
        stars.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#fff" opacity=".45"/>')
    lines = _wrapped(title)
    text_lines = [
        f'<text x="44" y="{175 + i * 38}" font-size="29" fill="#fff" '
        f'font-family="sans-serif" font-weight="700">{escape(line)}</text>'
        for i, line in enumerate(lines)
    ]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" '
        'role="img" aria-label="Original abstract category placeholder, not an episode still or book cover">'
        f'<rect width="640" height="360" rx="20" fill="{background}"/>'
        + "".join(stars)
        + f'<path d="M0 24H590Q630 24 630 66V101" fill="none" stroke="{accent}" stroke-width="20"/>'
        + f'<path d="M0 326H530Q606 326 606 286" fill="none" stroke="{accent}" stroke-width="16"/>'
        + f'<text x="44" y="112" font-size="18" fill="{accent}" font-family="sans-serif">{label}</text>'
        + "".join(text_lines)
        + '<text x="44" y="300" font-size="13" fill="#ddd" font-family="sans-serif">ABSTRACT PLACEHOLDER · NOT OFFICIAL ART</text>'
        + '</svg>'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-id", required=True)
    parser.add_argument("--medium", choices=MEDIA, required=True)
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    print(render_card(args.row_id, args.medium, args.title))


if __name__ == "__main__":
    main()
