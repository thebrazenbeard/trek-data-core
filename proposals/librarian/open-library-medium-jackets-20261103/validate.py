"""Check exact source-relative medium-cover candidate receipts; never release art."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import validate_artwork_release as artwork  # noqa: E402

RECORDS = Path(__file__).with_name("records.json")
ROW_KEYS = {
    "row_id", "isbn", "cover_id", "variant", "width_px_observed",
    "image_sha256", "image_url", "image_visual_observation",
    "rights_status", "release_status",
}
SHA = re.compile(r"^[a-f0-9]{64}$")
# Separately reported by the independently operating visual reviewer in
# Blotter event #3466; not derived from the untrusted candidate JSON.
REVIEWED_MEDIUM_SHA256 = {
    "directory:literature:prh-autobiography-kirk": "aac6802ca2738fb8df5c119eb05824936b52653233a01a755441d8f57458304a",
    "directory:literature:prh-autobiography-picard": "9e1b7f2c9b84d63bc00f2d32cb8fd3c605788ddcde8d174a964d7edc33def887",
    "directory:literature:prh-autobiography-janeway": "8ee45c479222f6b021bca4094673d7232e75c2b15aec43b57021ecab3b874051",
    "directory:literature:prh-autobiography-spock": "6f6a749fcbccc95fbf3700b0d1a78eee04924996d6f4a756abe49b586d8bf4d0",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def validate(packet: dict) -> int:
    require(set(packet) == {"schema", "provenance", "candidates", "holds"}, "packet keys")
    require(packet["schema"] == "trek-open-library-medium-cover-candidates-v1", "schema")
    provenance = packet["provenance"]
    require(set(provenance) == {
        "source_reviewer", "blotter_seq", "observation_date", "api_documentation",
        "license_context", "scope", "release_effect",
    }, "provenance keys")
    require(provenance["blotter_seq"] == 3466 and provenance["release_effect"] == "NONE", "review anchor")
    require(provenance["scope"] == "source_local_medium_api_previews_only", "scope")
    pins = artwork.REVIEWED_OPEN_LIBRARY_COVER_PINS
    rows = packet["candidates"]
    require(isinstance(rows, list) and len(rows) == len(pins) == 4, "four pinned candidates required")
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "candidate keys")
        name = row["row_id"]
        require(name in pins and name not in seen, "unreviewed or duplicate row")
        seen.add(name)
        pin = pins[name]
        require(row["isbn"] == pin["isbn"] and row["cover_id"] == pin["cover_id"], "edition-cover mismatch")
        require(row["variant"] == "M" and row["width_px_observed"] == 180, "variant/width mismatch")
        require(isinstance(row["image_sha256"], str) and SHA.fullmatch(row["image_sha256"]), "image hash")
        require(row["image_sha256"] == REVIEWED_MEDIUM_SHA256[name], "medium byte receipt mismatch")
        expected_url = f"https://covers.openlibrary.org/b/id/{pin['cover_id']}-M.jpg?default=false"
        require(row["image_url"] == expected_url, "unreviewed image host, variant or cover URL")
        require(row["rights_status"] == "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED", "rights promotion")
        require(row["release_status"] == "CANDIDATE_REQUIRES_SEPARATE_REVIEW", "release promotion")
        require(row["image_visual_observation"].startswith("independently identified jacket;"), "visual receipt")
    require(seen == set(pins), "missing reviewed row")
    require(packet["holds"] == [
        {
            "row_id": "directory:literature:proposed-lit-discovery-enterprise-war",
            "cover_id": 12857937,
            "reason": "VISUALLY_REJECTED_INTERIOR_TITLE_PAGE",
        }
    ], "visually rejected image must stay held")
    return len(rows)


if __name__ == "__main__":
    print(f"PASS: {validate(json.loads(RECORDS.read_text(encoding='utf-8')))} medium candidates; no release effect")
