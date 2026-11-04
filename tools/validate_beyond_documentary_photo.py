#!/usr/bin/env python3
"""Static fail-closed release gate for one opt-in CC BY 2.0 event photograph.

The source photograph is independently identified; this checks exact local
release bytes and UI contracts, not anyone's personality/trademark rights.
No downloaded photograph is stored by this repository.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
import sys

if __package__:
    from .validate_artwork_release import ArtworkRejected, check_css_no_pre_opt_in_network
else:
    from validate_artwork_release import ArtworkRejected, check_css_no_pre_opt_in_network

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "explorer/beyond-premiere-photo.json"
DIGEST = "bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634"
DECISION = "explorer/beyond-premiere-release-decision.json"
DECISION_DIGEST = "b3041c0fe9ed739c1187b5d9da97e9817dfca753683ca100bd8c93263b68cd89"
ACCEPTED_HELD_CONTRACT = "proposals/librarian/beyond-japan-premiere-ccby-display-criteria-20261103/contract.json"
ACCEPTED_HELD_CONTRACT_SHA = "9ed8d519d8bba7ef7e605ad0d09bdcf74dd7f48c9f9c1ef829dc28772ab8e4a5"
FUTURE_LOCAL_ASSET = "explorer/licensed-artwork/beyond-premiere-japan-2016-960.jpg"
PHOTO_SHA = "e8c2933469a00fb2c8b142f41472153ed7982c05f98f9c7c154b6bea689cc06f"
ORIGINAL_SHA = "7fd481633086f97e7b05e0eccbd3515a90d44f4fa7ce1255180007d9d13b4250"
THUMB_URL = ("https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a4/"
             "Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg/"
             "960px-Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg")
SOURCE_URL = ("https://commons.wikimedia.org/wiki/File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_"
              "J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg")


class ReleaseRejected(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseRejected(message)


def read_regular(root: Path, relative: str) -> bytes:
    current = root
    for part in Path(relative).parts:
        current = current / part
        require(not current.is_symlink(), f"symlink denied: {relative}")
    require(current.is_file() and stat.S_ISREG(current.stat().st_mode), f"missing file: {relative}")
    return current.read_bytes()


class PremiereMarkup(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.panel_depth = None
        self.images_before_consent = 0
        self.buttons = 0
        self.panels = 0
        self.csp = None
        self.svg_depth = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        require(len(values) == len(attrs), "duplicate HTML attributes")
        require(not (set(values) & {"srcset", "poster", "background", "ping"}),
                "unreviewed HTML resource-loading attribute")
        if tag == "svg":
            require(self.svg_depth is None, "nested SVG requires separate review")
            self.svg_depth = self.depth
        if self.svg_depth is not None:
            require(tag in {"svg", "g", "path", "polygon", "rect", "circle", "ellipse", "line", "polyline", "title", "desc"},
                    "unreviewed SVG image, animation or embedded resource element")
            require(not ({"href", "xlink:href", "src", "xlink:actuate", "xlink:show"} & set(values)),
                    "SVG external resource link denied")
            for value in values.values():
                require(not isinstance(value, str) or
                        ("\\" not in value and "/*" not in value and "*/" not in value and
                         re.search(r"u\s*r\s*l\s*\(|(?:https?:)?//", value, re.IGNORECASE) is None),
                        "SVG external paint/resource reference denied")
        if "style" in values:
            try:
                check_css_no_pre_opt_in_network(values["style"] or "")
            except ArtworkRejected as exc:
                raise ReleaseRejected(f"inline CSS resource before consent: {exc}") from exc
        if tag == "meta" and values.get("http-equiv") == "Content-Security-Policy":
            self.csp = values.get("content")
        if values.get("id") == "beyond-premiere-panel":
            self.panels += 1
            require(tag == "section" and "hidden" in values, "premiere section must start hidden")
            self.panel_depth = self.depth
        if values.get("id") == "beyond-premiere-toggle":
            self.buttons += 1
            require(tag == "button" and values.get("type") == "button" and "disabled" in values and
                    values.get("aria-pressed") == "false", "premiere toggle must start disabled and unpressed")
        # CSP host permission is global. A preload in <head>, remote <img>
        # outside the panel, or a CSS background is enough to leak a request
        # before consent; guarding only the candidate panel is insufficient.
        if tag == "link":
            require(values.get("rel") == "stylesheet" and
                    re.fullmatch(r"\./app\.css\?v=[a-f0-9]{64}", values.get("href") or "") is not None,
                    "unreviewed link/preload before visitor opt-in")
        if tag == "img":
            require(values.get("class") == "masthead-art" and
                    re.fullmatch(r"\./trek-data-core-hero\.jpg\?v=[a-f0-9]{64}", values.get("src") or "") is not None,
                    "unreviewed static image before visitor opt-in")
        if "src" in values and tag != "img":
            require(tag == "script" and
                    re.fullmatch(r"\./app\.js\?v=[a-f0-9]{64}", values["src"] or "") is not None,
                    "unreviewed HTML src resource before visitor opt-in")
        if tag in {"picture", "source", "video", "iframe", "object", "embed", "image", "feimage", "use", "foreignobject"}:
            raise ReleaseRejected("unreviewed pre-consent image-capable HTML element")
        if self.panel_depth is not None and tag == "img":
            self.images_before_consent += 1
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
                       "param", "source", "track", "wbr"}:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
                       "param", "source", "track", "wbr"}:
            self.depth -= 1
            if self.panel_depth is not None and self.depth == self.panel_depth:
                self.panel_depth = None
            if self.svg_depth is not None and self.depth == self.svg_depth:
                self.svg_depth = None


def validate(root: Path = ROOT) -> dict:
    raw = read_regular(root, MANIFEST)
    require(len(raw) < 8192 and hashlib.sha256(raw).hexdigest() == DIGEST,
            "photo sidecar does not match independently reviewed exact bytes")
    source = json.loads(raw)
    require(source["schema_version"] == "1.0.0" and
            source["data_status"] == "PROPOSED_DOCUMENTARY_PHOTOGRAPH_DISPLAY_ONLY" and
            source["image_kind"] == "REAL_WORLD_PREMIERE_DOCUMENTARY_PHOTO_NOT_FILM_STILL" and
            source["source_local_film_id"] == "film-beyond" and
            source["source_local_film_locator"] == "https://www.startrek.com/movies/star-trek-beyond" and
            source["image_url"] == THUMB_URL and source["source_url"] == SOURCE_URL and
            source["image_sha256_observed"] == PHOTO_SHA and source["original_image_sha256_observed"] == ORIGINAL_SHA and
            source["image_observed_bytes"] == 116536 and source["image_observed_width"] == 960 and
            source["image_observed_height"] == 640 and source["original_image_observed_bytes"] == 4134183 and
            source["photographer"] == "Dick Thomas Johnson" and source["license"] == "CC BY 2.0" and
            source["license_url"] == "https://creativecommons.org/licenses/by/2.0/" and
            source["network_policy"] == "NO_THIRD_PARTY_REQUEST_BEFORE_EXPLICIT_VISITOR_OPT_IN" and
            source["coverage_effect"] == source["work_admission_effect"] == "NONE", "source/rights identity mismatch")
    require(source["original_flickr_url"] == "https://www.flickr.com/photos/31029865@N06/31784488840/" and
            "4552×3035 to 960×640" in source["changes_notice"] and "endorsement" in source["nonendorsement_notice"] and
            "publicity/privacy" in source["rights_limit"] and "not a frame from the film" in source["caption"],
            "required photo attribution/change notice or qualification absent")
    source_contract_raw = read_regular(root, ACCEPTED_HELD_CONTRACT)
    require(hashlib.sha256(source_contract_raw).hexdigest() == ACCEPTED_HELD_CONTRACT_SHA,
            "accepted source-only display criteria have changed")
    source_contract = json.loads(source_contract_raw)
    require(source_contract["status"] == "HELD_PHOTO_SPECIFIC_EDITORIAL_DISPLAY_CONTRACT" and
            source_contract["public_image_display_authorized"] is False and
            source_contract["image_bytes_committed"] == 0 and
            source_contract["site_effect"] == "NONE" and
            source_contract["film_id_context_only"] == "film:film-beyond" and
            source_contract["commons_page"] == SOURCE_URL and
            source_contract["original_image_sha256"] == ORIGINAL_SHA and
            source_contract["license"] == "CC_BY_2_0_GENERIC" and
            source_contract["photographer"] == "Dick Thomas Johnson" and
            source_contract["work_or_coverage_admission"] == "NONE",
            "accepted PR442 source-only authorization cannot be silently promoted")
    decision_raw = read_regular(root, DECISION)
    require(len(decision_raw) < 8192 and hashlib.sha256(decision_raw).hexdigest() == DECISION_DIGEST,
            "release decision differs from code-owned held decision bytes")
    decision = json.loads(decision_raw)
    require(decision["schema_version"] == "1.0.0" and
            decision["decision_id"] == "beyond-premiere-japan-2016-editorial-image-v1" and
            decision["decision_status"] == "HELD_PENDING_INDEPENDENT_RELEASE_REVIEW" and
            decision["public_image_display_authorized"] is False and
            decision["source_local_film_id"] == "film-beyond" and
            decision["accepted_held_source_contract"] == ACCEPTED_HELD_CONTRACT and
            decision["accepted_held_source_contract_sha256"] == ACCEPTED_HELD_CONTRACT_SHA and
            decision["photo_manifest_sha256"] == DIGEST and
            decision["observed_rendition_sha256"] == PHOTO_SHA and
            decision["observed_rendition_bytes"] == 116536 and
            decision["proposed_same_origin_asset"] == "./licensed-artwork/beyond-premiere-japan-2016-960.jpg" and
            decision["independent_image_release_review"] == "PENDING" and
            decision["independent_browser_visual_review"] == "PENDING" and
            decision["owner_release_disposition"] == "PENDING" and
            decision["coverage_effect"] == decision["work_admission_effect"] == "NONE",
            "unreviewed release promotion or source identity change denied")
    require(not (root / FUTURE_LOCAL_ASSET).exists() and not (root / FUTURE_LOCAL_ASSET).is_symlink(),
            "public image binary cannot accompany a held release decision")
    html = read_regular(root, "explorer/index.html").decode("utf-8")
    css = read_regular(root, "explorer/app.css").decode("utf-8")
    js = read_regular(root, "explorer/app.js").decode("utf-8")
    try:
        check_css_no_pre_opt_in_network(css)
    except ArtworkRejected as exc:
        raise ReleaseRejected(f"unreviewed CSS network URL before consent: {exc}") from exc
    markup = PremiereMarkup()
    markup.feed(html)
    require(markup.panels == markup.buttons == 1 and markup.images_before_consent == 0,
            "premiere DOM must have one disabled consent gate and zero startup image nodes")
    require(markup.csp is not None, "missing CSP")
    # Badgey's standalone browser-only chat no longer needs loopback access.
    # Keep the connection policy same-origin only; an arbitrary connect-src
    # or widened img-src remains prohibited while this photo is held.
    allowed_connections = markup.csp.split("connect-src ", 1)[1].split(";", 1)[0] if "connect-src " in markup.csp else ""
    require("img-src 'self' https://covers.openlibrary.org https://archive.org https://*.us.archive.org;" in markup.csp and
            "https://thumb.wikimedia.org" not in markup.csp and
            "https://upload.wikimedia.org" not in markup.csp and
            allowed_connections == "'self'",
            "premiere photo must not extend image network CSP before public release")
    require(DIGEST in js and DECISION_DIGEST in js and
            "fetch('./beyond-premiere-photo.json'" in js and
            "fetch('./beyond-premiere-release-decision.json'" in js and
            "decision.public_image_display_authorized === true" in js and
            "image.src = './licensed-artwork/beyond-premiere-japan-2016-960.jpg';" in js and
            "image.referrerPolicy = 'no-referrer';" in js and
            "premierePhotoState.epoch !== epoch" in js and "holder.replaceChildren();" in js and
            "byId('beyond-premiere-toggle').addEventListener('click', togglePremierePhoto)" in js,
            "runtime image identity/consent/stale-generation guard missing")
    require(re.search(r"\.beyond-premiere-panel\[hidden\]\s*\{\s*display:\s*none", css) is not None and
            re.search(r"\.beyond-premiere-image img\s*\{[^}]*width:\s*100%", css) is not None,
            "missing responsive hidden/photo CSS")
    # Static exact-byte cache busting ensures the deployed HTML cannot render
    # stale JS (or a missing newer photo consent check) after a source merge.
    for name, content in (("app.js", js), ("app.css", css)):
        checksum = hashlib.sha256(content.encode()).hexdigest()
        require(f"./{name}?v={checksum}" in html, f"stale {name} cache key")
    return {"status": "HELD_SOURCE_BOUND_DOCUMENTARY_PHOTO_CANDIDATE", "photo_count": 1,
            "image_observed_bytes": 116536, "coverage_effect": "NONE", "work_admission_effect": "NONE"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    options = parser.parse_args()
    try:
        print(json.dumps(validate(options.root), sort_keys=True))
    except (ReleaseRejected, OSError, ValueError, KeyError) as exc:
        print(f"PHOTO RELEASE HOLD: {exc}", file=sys.stderr)
        sys.exit(1)
