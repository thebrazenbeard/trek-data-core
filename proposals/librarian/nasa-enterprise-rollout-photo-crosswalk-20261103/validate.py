#!/usr/bin/env python3
"""NASA rollout photo corroboration guard; never authorizes display or upload.

No network by default. Explicit --verify-download checks the actual NASA JPEG
in memory and prints its SHA/size; it never writes or publishes an image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "packet.json"
ACCEPTED_DECISION = ROOT / "proposals/research/nasa-enterprise-rollout-display-decision-20261103/decision.json"
EXPECTED_CANONICAL_SHA256 = "3a30250081785392caeb2c7331262de307fd28ac179e0ae06fef653bed5fd038"
EXPECTED_IMAGE_URL = "https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg"
EXPECTED_IMAGE_SHA256 = "e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8"
EXPECTED_IMAGE_BYTES = 165312
EXPECTED_IMAGE_DIMENSIONS = (1041, 833)
MAX_DOWNLOAD_BYTES = 4_000_000
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"nonregular/symlinked/missing JSON: {path.name}")
    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_json_keys)
    if not isinstance(result, dict):
        raise ValueError("JSON must be a map")
    return result


def jpeg_dimensions(image: bytes) -> tuple[int, int]:
    """Read baseline/progressive JPEG dimensions without external libraries."""
    if image[:2] != b"\xff\xd8":
        raise ValueError("source is not a JPEG")
    pos = 2
    while pos + 4 < len(image):
        if image[pos] != 0xFF:
            raise ValueError("malformed JPEG segment marker")
        while pos < len(image) and image[pos] == 0xFF:
            pos += 1
        if pos >= len(image):
            break
        marker = image[pos]
        pos += 1
        if marker in (0xD9, 0xDA):
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if pos + 2 > len(image):
            break
        size = int.from_bytes(image[pos:pos + 2], "big")
        if size < 2 or pos + size > len(image):
            raise ValueError("invalid JPEG segment length")
        if marker in SOF_MARKERS:
            if size < 7:
                raise ValueError("invalid JPEG frame header")
            height = int.from_bytes(image[pos + 3:pos + 5], "big")
            width = int.from_bytes(image[pos + 5:pos + 7], "big")
            return width, height
        pos += size
    raise ValueError("JPEG dimensions not found")


def validate_source_bytes(image: bytes) -> dict:
    if type(image) is not bytes or len(image) != EXPECTED_IMAGE_BYTES:
        raise ValueError("NASA JPEG size differs from reviewed exact bytes")
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError("NASA JPEG SHA256 differs from reviewed exact bytes")
    dimensions = jpeg_dimensions(image)
    if dimensions != EXPECTED_IMAGE_DIMENSIONS:
        raise ValueError("NASA JPEG dimensions differ from reviewed exact image")
    return {"sha256": digest, "bytes": len(image), "dimensions": list(dimensions)}


def verify_download() -> dict:
    parsed = urllib.parse.urlsplit(EXPECTED_IMAGE_URL)
    if (parsed.scheme, parsed.hostname) != ("https", "www.nasa.gov"):
        raise ValueError("untrusted NASA image download host")
    request = urllib.request.Request(EXPECTED_IMAGE_URL, headers={"User-Agent": "TrekResearch-Librarian/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        final = urllib.parse.urlsplit(response.geturl())
        if (final.scheme, final.hostname) != ("https", "www.nasa.gov"):
            raise ValueError("NASA image redirected to unexpected host")
        image = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(image) > MAX_DOWNLOAD_BYTES:
        raise ValueError("image exceeds bounded download limit")
    return validate_source_bytes(image)


def validate(packet: dict, *, directory: Path = HERE) -> None:
    if not isinstance(packet, dict) or len(packet) != 42:
        raise ValueError("source crosswalk schema changed")
    digest = hashlib.sha256(json.dumps(
        packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    if digest != EXPECTED_CANONICAL_SHA256:
        raise ValueError("source, rights, caption, release or receipt changed without code review")
    for key, expected in {
        "proposal_id": "nasa-enterprise-rollout-photo-crosswalk-20261103",
        "status": "PHOTO_SPECIFIC_SOURCE_CORROBORATION_ONLY",
        "nasa_exact_jpeg_url": EXPECTED_IMAGE_URL,
        "nasa_exact_jpeg_sha256": EXPECTED_IMAGE_SHA256,
        "nasa_exact_jpeg_bytes": EXPECTED_IMAGE_BYTES,
        "nasa_exact_jpeg_dimensions": list(EXPECTED_IMAGE_DIMENSIONS),
        "nasa_institutional_flickr_url": "https://www.flickr.com/photos/nasacommons/9467279838/",
        "flickr_image_number": "S91-27436",
        "flickr_rights_label_meaning": "COLLECTION_PORTAL_STATUS_NOT_COPYRIGHT_LICENSE_OR_THIRD_PARTY_RELEASE",
        "public_display_eligible": False,
        "independent_photo_specific_rights_review": "PENDING",
        "independent_design_review": "PENDING",
        "image_release_manifest": None,
        "release_authorization": "NOT_GRANTED",
        "image_binaries_included": 0,
        "fictional_episode_or_film_artwork": False,
        "research_or_coverage_admission": "NONE",
        "site_effect": "NONE",
    }.items():
        if type(packet.get(key)) is not type(expected) or packet[key] != expected:
            raise ValueError(f"protected source/rights/fictional-work invariant changed: {key}")
    if len(packet["open_falsifiers"]) != 5:
        raise ValueError("material falsifier set changed")
    if directory.is_symlink() or any(
        child.suffix.lower() in IMAGE_EXTENSIONS for child in directory.iterdir()
    ):
        raise ValueError("image binary or symlink found in nonpublishing source packet")
    accepted = read_json(ACCEPTED_DECISION)
    if (accepted.get("historical_source_og_image_exact_url") != EXPECTED_IMAGE_URL
            or accepted.get("historical_source_image_sha256") != EXPECTED_IMAGE_SHA256
            or accepted.get("historical_source_image_bytes") != EXPECTED_IMAGE_BYTES
            or accepted.get("public_display_eligible") is not False
            or accepted.get("release_authorization") != "NOT_GRANTED"):
        raise ValueError("accepted #418 image receipt/release HOLD no longer matches")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-download", action="store_true", help="download exact NASA JPEG in memory only and verify bytes")
    args = parser.parse_args()
    try:
        validate(read_json(PACKET))
        if args.verify_download:
            receipt = verify_download()
            print("SOURCE_BYTES_VERIFIED:", json.dumps(receipt, sort_keys=True))
    except Exception as exc:
        print(f"NASA photo-specific source crosswalk HOLD: {exc}", file=sys.stderr)
        return 1
    print("PASS: NASA photo crosswalk; public display/release/binaries/fictional coverage remain HELD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
