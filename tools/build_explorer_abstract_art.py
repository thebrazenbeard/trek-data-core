"""Rebuild five original category placeholders from the accepted safe SVG renderer.

No outside image inputs, title metadata, artwork leads, or remote fetches enter this
public artifact. A category placeholder is NOT a franchise still or book cover.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py"
SPEC = importlib.util.spec_from_file_location("trek_accepted_abstract_renderer", RENDERER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("accepted abstract art renderer is unavailable")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

# Explicit paths are mirrored in the Pages publication allowlist and CSS.
# Stable fixed seeds make every rebuild byte-for-byte identical on any host.
CATEGORIES = {
    "EPISODE": ("episode", "EPISODE REFERENCE"),
    "FILM": ("film", "FILM REFERENCE"),
    "LITERATURE": ("literature", "LITERARY REFERENCE"),
    "SHORT_FORM": ("short-form", "SHORT-FORM REFERENCE"),
    "AUDIO": ("audio", "AUDIO REFERENCE"),
}


def background_without_labels(svg: str) -> str:
    """Keep the procedural drawing, but leave visible record labels to HTML.

    The category renderer embeds three fixed <text> elements; when used as a
    CSS background those words collided with the source-keyed record title,
    initials, and attribution rendered by the Explorer at mobile widths.
    Fail closed if that renderer's contract changes.
    """
    result, count = re.subn(r"<text\b[^>]*>[^<>]*</text>", "", svg)
    if count != 3 or "<text" in result.lower():
        raise ValueError("accepted abstract renderer's text vocabulary changed")
    return result


def expected_art() -> dict[Path, bytes]:
    if set(CATEGORIES) != set(MODULE.MEDIA):
        raise ValueError("renderer media vocabulary changed; manual review required")
    return {
        ROOT / "explorer" / f"art-original-{slug}.svg":
            (background_without_labels(
                MODULE.render_card(f"public-category:{medium}", medium, title)
            ) + "\n").encode("utf-8")
        for medium, (slug, title) in CATEGORIES.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="reject missing or altered committed SVG assets")
    args = parser.parse_args()
    for path, data in expected_art().items():
        if args.check:
            if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
                raise SystemExit(f"original abstract art is absent or changed: {path.relative_to(ROOT)}")
        else:
            path.write_bytes(data)


if __name__ == "__main__":
    main()
