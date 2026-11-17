#!/usr/bin/env python3
"""Build six original, held, source-ID-bound LCARS references from Librarian contract.

No copyrighted episode/film/book images or third-party image URLs are consumed.
This generator is intentionally outside the public Explorer Pages artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

try:
    from tools import build_reference_card_inputs as contract
except ModuleNotFoundError:
    import build_reference_card_inputs as contract


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "proposals/ui/source-local-art-preview"
MAIN = contract.EXPECTED_MAIN
RENDERER_PATH = ROOT / "proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py"
RENDERER_SPEC = importlib.util.spec_from_file_location("source_local_original_svg_renderer", RENDERER_PATH)
if RENDERER_SPEC is None or RENDERER_SPEC.loader is None:
    raise ValueError("accepted original renderer unavailable")
RENDERER = importlib.util.module_from_spec(RENDERER_SPEC)
RENDERER_SPEC.loader.exec_module(RENDERER)

APPROVED_MEDIA = {"EPISODE", "FILM", "LITERATURE"}
NO_IMAGE_LABEL = {
    "EPISODE": "NO EPISODE STILL",
    "FILM": "NO FILM POSTER",
    "LITERATURE": "NO BOOK JACKET",
}
SOURCE_HOSTS = {"www.wikidata.org", "www.startrek.com", "www.penguinrandomhouse.com", "www.simonandschuster.com"}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def canonical(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def build_art(rows: list[dict]) -> tuple[dict[str, bytes], list[dict]]:
    require(len(rows) == 6, "six bound source-local preview inputs required")
    require(rows == contract.build_inputs(), "source-local art inputs differ from pinned contract")
    require({media: sum(r.get("medium") == media for r in rows) for media in APPROVED_MEDIA} == {"EPISODE": 2, "FILM": 2, "LITERATURE": 2}, "media selection drift")
    require(len({r.get("source_local_row_id") for r in rows}) == 6, "duplicate source rows")
    assets: dict[str, bytes] = {}
    cards = []
    for row in rows:
        medium = row["medium"]
        row_id = row["source_local_row_id"]
        title = row["title"]
        require(row.get("identity_scope") == "SOURCE_LOCAL", "source identity promoted")
        require(row.get("verification_status") == "UNVERIFIED_METADATA", "source metadata promoted")
        require(row.get("admission_effect") == row.get("coverage_effect") == "NONE", "source effect promoted")
        require(row.get("edition_identifier") is None, "edition identity inferred")
        require(row.get("metadata_recheck_status") in {"rechecked_exact", "not_rechecked"}, "metadata recheck status changed")
        digest = hashlib.sha256((medium + "\x00" + row_id).encode("utf-8")).hexdigest()
        require(digest == row.get("visual_seed_sha256"), "source-ID visual seed drift")
        require(re.fullmatch(r"[0-9a-f]{64}", row.get("source_row_sha256", "")) is not None, "source row pin missing")
        source_url = urlsplit(row["source_reference_url"])
        require(
            source_url.scheme == "https" and source_url.hostname in SOURCE_HOSTS
            and source_url.username is None and source_url.password is None
            and source_url.port is None and not source_url.fragment,
            "unapproved source-reference locator",
        )
        svg = (RENDERER.render_card(row_id, medium, title) + "\n").encode("utf-8")
        name = f"art/{medium.lower()}-{digest[:16]}.svg"
        require(name not in assets, "duplicate art asset target")
        assets[name] = svg
        cards.append({
            "source_local_row_id": row_id,
            "medium": medium,
            "title": title,
            "context_label": row["context_label"],
            "source_reference_url": row["source_reference_url"],
            "source_group": row["source_group"],
            "source_input": row["source_input"],
            "identity_scope": "SOURCE_LOCAL",
            "verification_status": "UNVERIFIED_METADATA",
            "metadata_recheck_status": row["metadata_recheck_status"],
            "edition_identifier": None,
            "source_row_sha256": row["source_row_sha256"],
            "visual_seed_sha256": digest,
            "asset_path": name,
            "asset_sha256": hashlib.sha256(svg).hexdigest(),
            "artwork_class": "ORIGINAL_ABSTRACT_SOURCE_REFERENCE_NOT_OFFICIAL_IMAGE",
            "source_artwork_license_grant": "NONE",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    return assets, cards


def card_html(row: dict, n: int) -> str:
    require(row.get("verification_status") == "UNVERIFIED_METADATA", "card claims verified canon")
    require(row.get("identity_scope") == "SOURCE_LOCAL", "card identity promoted")
    require(row.get("admission_effect") == row.get("coverage_effect") == "NONE", "card claims admitted coverage")
    require(row.get("edition_identifier") is None, "card claims edition binding")
    require(row.get("source_artwork_license_grant") == "NONE", "card claims source image rights")
    require(re.fullmatch(r"art/(?:episode|film|literature)-[0-9a-f]{16}\.svg", row.get("asset_path", "")) is not None, "untrusted art path")
    locator = urlsplit(row["source_reference_url"])
    require(locator.scheme == "https" and locator.hostname in SOURCE_HOSTS and locator.port is None and not locator.fragment and locator.username is None and locator.password is None, "untrusted card source URL")
    label = NO_IMAGE_LABEL[row["medium"]]
    description = {
        "EPISODE": "not an episode frame or streaming thumbnail",
        "FILM": "not a theatrical poster or production photograph",
        "LITERATURE": "not a publisher jacket or edition-authenticated cover",
    }[row["medium"]]
    return f'''<article class="card" id="source-{n}" aria-labelledby="title-{n}">
  <img src="./{esc(row['asset_path'])}" loading="lazy" width="640" height="360" alt="Original LCARS index graphic for {esc(row['medium'].lower())} source-local record {esc(row['source_local_row_id'])}; {esc(description)}">
  <div class="body"><div class="pills"><span>{esc(row['medium'])}</span><span>HELD · UNVERIFIED METADATA</span></div>
    <h3 id="title-{n}">{esc(row['title'])}</h3>
    <p class="context">{esc(row['context_label'])}</p>
    <p class="hold">{label} · Original abstract reference only, NOT OFFICIAL ART.</p>
    <p class="local-id">Source-local ID: <code>{esc(row['source_local_row_id'])}</code></p>
    <details><summary>Source and visual provenance</summary><dl>
      <dt>Metadata recheck</dt><dd>{esc(row['metadata_recheck_status'])}; identity remains UNVERIFIED_METADATA</dd>
      <dt>Source family</dt><dd>{esc(row['source_group'])}</dd>
      <dt>Source input</dt><dd><code>{esc(row['source_input'])}</code></dd>
      <dt>Edition identifier</dt><dd>UNRESOLVED — no ISBN inferred</dd>
      <dt>Source row SHA-256</dt><dd><code>{esc(row['source_row_sha256'])}</code></dd>
      <dt>Visual seed SHA-256</dt><dd><code>{esc(row['visual_seed_sha256'])}</code></dd>
      <dt>Generated SVG SHA-256</dt><dd><code>{esc(row['asset_sha256'])}</code></dd>
      <dt>Admission and image rights</dt><dd>0 Work admission; no licensed source image used</dd>
    </dl></details>
    <a class="source-link" href="{esc(row['source_reference_url'])}" target="_blank" rel="noopener noreferrer">Inspect source listing</a>
  </div>
</article>'''


def render_page(cards: list[dict]) -> str:
    require(len(cards) == 6, "gallery must show exactly six held source-local references")
    cards_html = "\n".join(card_html(row, i) for i, row in enumerate(cards, 1))
    return f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
  <title>Original Source-Linked Reference Cards · HELD</title>
  <style>
    :root {{ color-scheme: dark; background: #0f1120; color: #fff3f3; font: 16px/1.5 system-ui,sans-serif; }}
    * {{ box-sizing: border-box; }} body {{ max-width: 1120px; margin: auto; padding: 10px 18px 55px; }}
    header {{ border-left: 22px solid #efad91; border-bottom: 7px solid #bd97df; padding: 20px; border-radius: 0 0 0 22px; }}
    .eyebrow {{ letter-spacing: .13em; color: #f9d39c; font-weight: 900; font-size: .82rem; }}
    h1 {{ font-size: clamp(1.55rem,4.5vw,2.65rem); line-height: 1.2; margin: 8px 0; }}
    header p {{ max-width: 85ch; }}
    .warning {{ border: 2px solid #f6ad9e; background: #322338; padding: 15px; border-radius: 8px; margin: 18px 0; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(min(100%,305px),1fr)); gap: 17px; }}
    .card {{ min-width: 0; border-left: 9px solid #b99add; background: #24273c; border-radius: 10px; overflow: hidden; }}
    .card img {{ width: 100%; height: auto; display: block; background: #141b28; aspect-ratio: 16 / 9; object-fit: contain; }}
    .body {{ min-width: 0; padding: 15px; }}
    .pills {{ display: flex; gap: 7px; flex-wrap: wrap; font-size: .72rem; color: #16121c; font-weight: 800; }}
    .pills span {{ background: #eec491; border-radius: 5px; padding: 3px 9px; }}
    .pills span+span {{ background: #d8a7ef; }}
    h3 {{ font-size: 1.25rem; margin: 10px 0; overflow-wrap: anywhere; }}
    .context {{ margin: 5px 0; color: #e6d5ff; }}
    .hold {{ color: #fbd0b8; font-size: .9rem; font-weight: 700; }}
    .local-id {{ font-size: .82rem; overflow-wrap: anywhere; color: #d6cbdc; }}
    summary {{ min-height: 44px; display: flex; align-items: center; color: #ffdaaa; cursor: pointer; font-weight: 800; }}
    summary::before {{ content:'▸'; margin-right: 8px; }} details[open] summary::before {{ content:'▾'; }}
    dl {{ display: grid; grid-template-columns: minmax(100px,1fr) minmax(0,2fr); gap: 7px; margin: 5px 0 12px; }}
    dt {{ color: #d4c2e5; }} dd {{ margin: 0; overflow-wrap: anywhere; }} code {{ overflow-wrap: anywhere; }}
    .source-link {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 8px 14px; border-radius: 9px; background: #f6d49c; color: #16121e; text-decoration: none; font-weight: 800; }}
    .source-link:hover {{ background: #f6aa91; }}
    a:focus-visible, summary:focus-visible {{ outline: 3px solid #fff3b7; outline-offset: 3px; }}
    footer {{ border-top: 5px solid #d4a9f0; padding-top: 14px; margin-top: 40px; color: #dfd0e3; }}
    @media(max-width:480px) {{ body {{ padding: 8px 10px 35px; }} header {{ border-left-width: 12px; padding: 12px; }} dl {{ grid-template-columns: 1fr; }} .source-link {{ display: flex; width: 100%; }} }}
  </style>
</head>
<body><header><div class="eyebrow">TREK DATA CORE / EXPERIMENTAL ART PROVENANCE</div><h1>References, not replicas</h1>
  <p>Six distinct original LCARS index graphics, keyed to six existing source-local candidate IDs. The titles and links are metadata leads; no complete work, film frame, book edition or studio artwork was authenticated by this gallery.</p></header>
  <aside class="warning" aria-label="Research and artwork limitations"><strong>HELD PROPOSAL — NO PUBLIC RELEASE.</strong> These original vector diagrams are not Star Trek stills, posters, book jackets, official insignia or licensed franchise art. All six inputs remain UNVERIFIED_METADATA; zero Works admitted and zero corpus coverage added. Source URLs are opened only on your click.</aside>
  <main><h2>Source-bound visual reference samples</h2><div class="cards">{cards_html}</div></main>
  <footer>Original generated SVG only · source-local row identity, not global Work identity · accepted metadata baseline {MAIN[:12]} · no network image fetch or automatic Explorer update.</footer>
</body></html>
'''


def expected() -> dict[Path, bytes]:
    assets, cards = build_art(contract.build_inputs())
    paths = {TARGET / name: data for name, data in assets.items()}
    paths[TARGET / "index.html"] = render_page(cards).encode("utf-8")
    packet = {
        "status": "HELD_ORIGINAL_SOURCE_LOCAL_CARD_PREVIEW_NOT_PUBLIC",
        "source_contract": "proposals/librarian/reference-card-provenance-contract-20261104/records.json",
        "accepted_main_baseline": MAIN,
        "identity_scope": "SOURCE_LOCAL_NOT_DEDUPLICATED",
        "rights_class": "ORIGINAL_PROCEDURAL_REFERENCE_INDEX_GRAPHIC_NOT_SOURCE_IMAGE",
        "third_party_image_bytes": 0,
        "licensed_stills_posters_jackets": 0,
        "admitted_works": 0,
        "coverage_effect": "NONE",
        "public_release_effect": "NONE",
        "cards": cards,
    }
    paths[TARGET / "manifest.json"] = canonical(packet)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed held preview bytes and no stray assets")
    args = parser.parse_args()
    paths = expected()
    if args.check:
        require(all(p.is_file() and not p.is_symlink() and p.read_bytes() == data for p, data in paths.items()), "missing or modified held preview asset")
        art_dir = TARGET / "art"
        require(art_dir.is_dir() and not art_dir.is_symlink(), "missing or redirected art directory")
        require(set(art_dir.iterdir()) == {p for p in paths if p.parent == art_dir}, "stray or missing source-local SVG")
        print("HELD ORIGINAL CARDS PASS: 2 episode + 2 film + 2 literature; zero third-party image or Work effect")
    else:
        for path, data in paths.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            require(not path.is_symlink(), "refusing symlink output")
            path.write_bytes(data)
        print("Built six source-bound original graphics; HELD ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
