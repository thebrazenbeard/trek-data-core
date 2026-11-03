#!/usr/bin/env python3
"""Validate held visual observations for two public-row Trek eBook editions.

An Open Library Covers API result is not a publisher copyright license or a
work-identity reconciliation. This intentionally cannot release images.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import validate_picard_cover_candidates as utilities

ROOT = Path(__file__).resolve().parents[1]
PACKET = "proposals/artwork/ol-publisher-ebook-jackets-20261103/records.json"
DIRECTORY = "explorer/discovery-catalog.json"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
ROOT_KEYS = {
    "schema_version", "data_status", "observed_on", "source_catalog_path", "source_catalog_sha256",
    "source_lineage", "api_guidance", "copyright_guidance", "underlying_cover_copyright",
    "image_bytes_committed", "public_artwork_release_effect", "source_work_admission_effect",
    "coverage_effect", "candidate_count", "candidates",
}
ENTRY_KEYS = {
    "row_id", "public_row_title", "public_row_creator", "public_row_locator", "public_row_edition_detail",
    "publisher_ebook_locator", "publisher_ebook_format", "isbn", "openlibrary_edition_id",
    "openlibrary_edition_json_url", "openlibrary_edition_title", "openlibrary_edition_subtitle",
    "edition_metadata_sha256", "cover_id", "medium_preview_url", "medium_preview_sha256",
    "medium_preview_bytes", "medium_width", "medium_height", "large_preview_url",
    "large_preview_sha256", "large_preview_bytes", "large_width", "large_height",
    "image_observation", "image_observer", "attribution_url", "rights_status", "release_status",
}

# Code-owned exact version/byte observations; changing a proposal JSON alone
# must never authorize new covers, changed endpoints or rights escalation.
EXPECTED = {
    "literature:proposed-lit-picard-second-self": {
        "isbn": "9781982194840", "edition": "OL34985674M", "cover_id": 14663887,
        "edition_sha": "d33501b91b26f3e92704c4f251fe38aedfedd3470e19bc738984af320b3df5cd",
        "edition_title": "Star Trek : Picard", "edition_subtitle": "Second Self",
        "medium_sha": "c37b62e49e1c14f5b925ad295a20230341ce7dc9e8dbeefcb8893aa173860a11",
        "medium_bytes": 21305, "medium_dims": (180, 280),
        "large_sha": "c876b5f87b1525d3fdc43e0d4b2efe3ba6e10068d8389dd7582d2138159ae0a1",
        "large_bytes": 34166, "large_dims": (257, 400),
    },
    "literature:proposed-lit-snw-high-country": {
        "isbn": "9781668002407", "edition": "OL38063809M", "cover_id": 12773868,
        "edition_sha": "0ff98bb8874821fafec6a96cac747f60f57542a5450d7fca7eab4f760ab3e44d",
        "edition_title": "The High Country", "edition_subtitle": "Star Trek: Strange New Worlds",
        "medium_sha": "11fdfa946b3834be1a0bce29925bd10ed78f101e791949fc42758edcb0321566",
        "medium_bytes": 23434, "medium_dims": (180, 271),
        "large_sha": "743d327a97a0820268a00328b76fdb4436b408d31051833254e8c63fcad428dd",
        "large_bytes": 47677, "large_dims": (315, 475),
    },
}


def validate(root: Path = ROOT) -> dict:
    root = Path(root)
    raw = utilities.file_bytes(root, PACKET)
    packet = utilities.strict_json(raw)
    utilities.require(isinstance(packet, dict) and set(packet) == ROOT_KEYS,
                      "candidate envelope keys invalid")
    utilities.require(packet["schema_version"] == "1.0.0" and
                      packet["data_status"] == "SOURCE_LOCAL_EBOOK_JACKET_CANDIDATES_HELD" and
                      packet["observed_on"] == "2026-11-03" and
                      packet["source_catalog_path"] == DIRECTORY and
                      packet["source_catalog_sha256"] == DIRECTORY_SHA and
                      packet["api_guidance"] == "https://openlibrary.org/dev/docs/api/covers" and
                      packet["copyright_guidance"] == "https://openlibrary.org/developers/licensing" and
                      packet["underlying_cover_copyright"] == "UNRESOLVED" and
                      packet["image_bytes_committed"] is False and
                      all(packet[field] == "NONE" for field in ("public_artwork_release_effect",
                                                                 "source_work_admission_effect", "coverage_effect")) and
                      isinstance(packet["source_lineage"], str) and len(packet["source_lineage"]) > 50,
                      "held-only rights and evidence boundary invalid")
    directory_raw = utilities.file_bytes(root, DIRECTORY)
    utilities.require(hashlib.sha256(directory_raw).hexdigest() == DIRECTORY_SHA,
                      "accepted 1214 directory bytes drifted")
    directory = utilities.strict_json(directory_raw)
    utilities.require(directory["rows"] and len(directory["rows"]) == 1214,
                      "not the accepted source-local directory")
    source_rows = {row["row_id"]: row for row in directory["rows"]}
    candidates = packet["candidates"]
    utilities.require(type(packet["candidate_count"]) is int and packet["candidate_count"] == 2 and
                      isinstance(candidates, list) and len(candidates) == 2,
                      "exact two held candidate records required")
    seen = set()
    for candidate in candidates:
        utilities.require(isinstance(candidate, dict) and set(candidate) == ENTRY_KEYS,
                          "candidate field contract invalid")
        key = candidate["row_id"]
        utilities.require(key in EXPECTED and key not in seen and key in source_rows,
                          "unknown/duplicate source-local eBook association")
        seen.add(key)
        expected = EXPECTED[key]
        src = source_rows[key]
        isbn = expected["isbn"]
        edition = expected["edition"]
        cover_id = expected["cover_id"]
        utilities.require(src["medium"] == "LITERATURE" and
                          src["source_group"] == "publisher:simonandschuster.com" and
                          candidate["public_row_title"] == src["title"] and
                          candidate["public_row_creator"] in src["context"] and
                          candidate["public_row_locator"] == src["source_locator"] and
                          candidate["public_row_edition_detail"] == f"Ebook · ISBN {isbn}" and
                          candidate["public_row_edition_detail"] in src["details"] and
                          candidate["publisher_ebook_format"] == "eBook" and
                          candidate["isbn"] == isbn and
                          candidate["publisher_ebook_locator"] == src["source_locator"].rsplit("/", 1)[0] + "/" + isbn and
                          candidate["openlibrary_edition_id"] == edition and
                          candidate["openlibrary_edition_json_url"] ==
                          f"https://openlibrary.org/books/{edition}.json" and
                          candidate["openlibrary_edition_title"] == expected["edition_title"] and
                          candidate["openlibrary_edition_subtitle"] == expected["edition_subtitle"],
                          "exact public publisher eBook ISBN or edition association invalid")
        utilities.require(utilities.ISBN.fullmatch(isbn) is not None and
                          sum((1 if idx % 2 == 0 else 3) * int(digit)
                              for idx, digit in enumerate(isbn)) % 10 == 0 and
                          candidate["edition_metadata_sha256"] == expected["edition_sha"] and
                          all(utilities.is_sha(candidate[field]) for field in (
                              "edition_metadata_sha256", "medium_preview_sha256", "large_preview_sha256")),
                          "Open Library edition JSON digest or ISBN checkdigit invalid")
        for size, suffix in (("medium", "M"), ("large", "L")):
            width, height = expected[size + "_dims"]
            utilities.require(candidate[size + "_preview_url"] ==
                              f"https://covers.openlibrary.org/b/id/{cover_id}-{suffix}.jpg?default=false" and
                              candidate[size + "_preview_sha256"] == expected[size + "_sha"] and
                              candidate[size + "_preview_bytes"] == expected[size + "_bytes"] and
                              candidate[size + "_width"] == width and
                              candidate[size + "_height"] == height,
                              "exact decoded image bytes, geometry, provider URL or hash invalid")
        utilities.require(candidate["cover_id"] == cover_id and
                          candidate["attribution_url"] == f"https://openlibrary.org/isbn/{isbn}" and
                          candidate["rights_status"] == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED" and
                          candidate["release_status"] == "HELD_FOR_INDEPENDENT_REVIEW" and
                          candidate["image_observer"] == "chatgpt.trek.visual_bookcover_mapping" and
                          isinstance(candidate["image_observation"], str) and
                          30 <= len(candidate["image_observation"]) <= 260 and
                          "front jacket" in candidate["image_observation"],
                          "reviewer observation is not release rights")
    utilities.require(seen == set(EXPECTED), "missing reviewed candidate")
    return {"status": "HELD_FOR_INDEPENDENT_REVIEW", "source_local_ebook_jackets": len(seen),
            "public_release_effect": "NONE", "coverage_effect": "NONE"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    print(json.dumps(validate(), sort_keys=True))
