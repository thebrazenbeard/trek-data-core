#!/usr/bin/env python3
"""Fail-closed validation for one held *Arena* museum-photo source proposal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path(__file__).with_name("records.json")


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"nonfinite {value}")))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def validate(packet: dict, root: Path = ROOT) -> None:
    fixed_roots = {
        "schema_version": "1.0.0",
        "batch_id": "LIBRARIAN.COMMONS.ARENA_GORN_MUSEUM.20261103",
        "data_status": "SOURCE_ONLY_HELD_THIRD_PARTY_ARTIFACT_RIGHTS_UNRESOLVED",
        "accepted_main": "f06e1951cce31efa6cc393d92d0f3c489f50d23b",
        "discovery_catalog_path": "explorer/discovery-catalog.json",
        "discovery_catalog_sha256": "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
        "observed_on": "2026-11-03",
        "candidate_count": 1,
        "image_bytes_read_for_hash_and_pixel_review": True,
        "image_bytes_committed": False,
        "public_artwork_release_effect": "NONE",
        "explorer_effect": "NONE",
        "source_work_admission_effect": "NONE",
        "coverage_effect": "NONE",
    }
    require(type(packet) is dict, "packet must be object")
    require(set(packet) == set(fixed_roots) | {"candidate"}, "unexpected root field")
    for key, value in fixed_roots.items():
        require(type(packet[key]) is type(value) and packet[key] == value, f"root field: {key}")

    catalog_bytes = (root / fixed_roots["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(catalog_bytes).hexdigest() == fixed_roots["discovery_catalog_sha256"],
            "accepted discovery catalog drift")
    catalog = json.loads(catalog_bytes)
    rows = [r for r in catalog["rows"] if r.get("row_id") == "legacy:s1:tos:018"]
    require(len(rows) == 1, "missing/ambiguous accepted source-local Arena row")
    episode = rows[0]
    require(episode["title"] == "Arena" and episode["context"] == "TOS S1E19"
            and episode["verification_status"] == "UNVERIFIED_METADATA", "episode work row drift")

    fixed_candidate = {
        "candidate_id": "external:commons:photograph:joeross:49786531687",
        "source_local_episode_row_id": "legacy:s1:tos:018",
        "episode_title": "Arena",
        "series_name": "Star Trek: The Original Series",
        "episode_identity_state": "DISCOVERY_ONLY_UNVERIFIED_METADATA",
        "independent_studio_episode_mention": "https://www.startrek.com/news/strange-new-worlds-gorn-arenas-message-of-mercy",
        "image_kind": "2019_MUSEUM_EXHIBIT_PHOTOGRAPH_OF_GORN_COSTUME_DISPLAY_NOT_EPISODE_FRAME",
        "proposed_caption": "A Gorn costume display photographed by Joe Ross at the 2019 Star Trek: Exploring New Worlds exhibit at the Henry Ford Museum; the photographer associates the display with The Original Series episode Arena. Not a frame from the episode; original filming-artifact status unverified.",
        "proposed_alt": "Photograph of a green Gorn costume display inside a museum case at the 2019 Star Trek: Exploring New Worlds exhibit, associated by the photographer with the episode Arena",
        "depicted_artifact_status": "MUSEUM_DISPLAY_AUTHENTIC_FILMING_PROP_PROVENANCE_UNVERIFIED",
        "photographer": "Joe Ross / Joetography LLC",
        "photographed_at": "Star Trek: Exploring New Worlds traveling exhibit, Henry Ford Museum, Dearborn, Michigan",
        "photographed_on": "2019-08-22T16:22:11",
        "commons_file_page": "https://commons.wikimedia.org/wiki/File:The_Gorn!_Star_Trek-_Exploring_New_Worlds_exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg",
        "commons_pinned_revision": "https://commons.wikimedia.org/w/index.php?title=File:The_Gorn!_Star_Trek-_Exploring_New_Worlds_exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg&oldid=1167442434",
        "commons_revision_oldid": 1167442434,
        "commons_rights_page_http_status": 200,
        "commons_rights_page_bytes": 138306,
        "commons_rights_page_sha256": "5541a7251878e26d959455e30200395780986a998bdd4d471b0f749532c57b4c",
        "original_flickr_source": "https://www.flickr.com/photos/joeross/49786531687/",
        "commons_flickreviewr_license_confirmation": "2023-06-15",
        "reported_photographer_license": "CC_BY_SA_2_0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "license_scope": "PHOTOGRAPHER_COPY_AND_ADAPT_PERMISSION_WITH_ATTRIBUTION_SHARE_ALIKE_CHANGE_NOTICE_AND_NONENDORSEMENT;_DOES_NOT_CLEAR_RIGHTS_IN_DEPICTED_STUDIO_ARTIFACT",
        "original_commons_image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1f/The_Gorn%21_Star_Trek-_Exploring_New_Worlds_exhibit_at_the_Henry_Ford_Museum%2C_Dearborn%2C_Michigan.jpg",
        "original_image_http_status": 200,
        "original_image_mime": "image/jpeg",
        "original_image_width": 5568,
        "original_image_height": 3712,
        "image_exif_orientation": "EXIF_8_ROTATED_90_DEGREES_CCW",
        "original_image_bytes": 7753903,
        "original_image_sha256": "c71f33e5d123e21dbefcfef41dc3f97f425c62470ef46d2f138cdf3baeaeb287",
        "pixel_review": "VISUALLY_INSPECTED_PHOTO_SHOWS_GREEN_REPTILIAN_COSTUME_MANNEQUIN_IN_MUSEUM_CASE;PIXELS_ALONE_DO_NOT_VERIFY_PROVENANCE",
        "other_rights_review": "STUDIO_COSTUME_DESIGN_AND_EXHIBIT_OBJECT_DISPLAY_RIGHTS_UNRESOLVED",
        "editorial_display_admission": "HELD_NO_PUBLIC_THUMBNAIL",
        "attribution_requirements": "JOE_ROSS_SOURCE_LINK_LICENSE_LINK_CHANGE_NOTICE_SHARE_ALIKE_NONENDORSEMENT_AND_PROMINENT_MUSEUM_EXHIBIT_CONTEXT",
    }
    candidate = packet["candidate"]
    require(type(candidate) is dict and set(candidate) == set(fixed_candidate), "candidate schema drift")
    for key, value in fixed_candidate.items():
        require(type(candidate[key]) is type(value) and candidate[key] == value, f"candidate field: {key}")
    for path in RECORD.parent.rglob("*"):
        require(not path.is_symlink(), "symlink in proposal subtree")
        if not path.is_file():
            continue
        require(path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
                "image extension in proposal subtree")
        with path.open("rb") as stream:
            signature = stream.read(20)
        require(not (signature.startswith((b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a"))
                     or signature[:4] == b"RIFF" and signature[8:12] == b"WEBP"),
                "image binary disguised by extension in proposal subtree")


if __name__ == "__main__":
    validate(read_json(RECORD))
    print("PASS: source-pinned Gorn museum image is HELD, with no episode-thumbnail release")
