"""Closed-schema validator for held VOY S4 E10-14 publisher cards.

The pinned rendered-text fingerprints and row digests are independent of the
mutable proposal data, but NOT substitutes for archived source body custody.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
DATA = ROOT / "records.json"
ACCEPTED_SHA = "806c4502af8eb5306137c13eaacea54f8cd469ba"
UPSTREAM_CSV = "proposals/discovery/publisher-season4-20261102/voy.csv"
UPSTREAM_SHA = "e9e8ac0cae8a30ac1c71b0c36b1d0f28b9ff9cf25d5f2a8d2875fad2e34e598e"
TITLES = {
    10: "Random Thoughts",
    11: "Concerning Flight",
    12: "Mortal Coil",
    13: "Waking Moment's",
    14: "Message In A Bottle",
}
BLURB_FINGERPRINTS = {
    10: (120, "51e1f681580e372058d0ce86a80f08c160389dd032186cf7dbad1784d2752855"),
    11: (141, "c35393ae5a54818d0e406b283db1eb283d686b5893b340ba5b9b4d3ac4446cdc"),
    12: (87, "4210e909b9149a0b2165381c871efe5326b3a6674c6adf9fb864b3569bf5cf02"),
    13: (80, "913d210d3e9ab02b10bcef4650bc7643c679a66fa88edfd0a620fe5669d227cd"),
    14: (163, "6d6531a3142ef1dacacb23db9ccb856fc22fb77280c0cdb868e7d0b7d6bbc611"),
}
ROW_DIGESTS = {
    10: "61b3fa21c40b96394b8f6d2a24ba53c68d6d46a0c7aee9424a685ee74ba110c5",
    11: "7eeb9b3d712cde4a4fef8343ac61ac8f9db4f4c3b282d405d3ea63d9a6a56969",
    12: "f3603c2a96900de8719c9230beb7ef13fe18d13f0c8ff0f22d23c14bc5d0d651",
    13: "5127e90ed931c4cfd4b0246b86142ac09e1df9ae1a96b21cce445f332e8982d6",
    14: "5ec3370a4277e92237216ff666e143263e6d52ae856d2e5423fcd064315336f9",
}
ENVELOPE_KEYS = {
    "schema_version", "packet_id", "role", "base_accepted_main", "observation_date_utc",
    "status", "rights_or_publication_effect", "source_binding_effect", "global_work_identity_effect",
    "coverage_effect", "episode_source_read", "transcript_or_full_text_read",
    "images_or_videos_retrieved", "source", "source_local_cards", "coverage_update",
}
SOURCE_KEYS = {
    "id", "url", "lineage_group", "type", "read_representation", "source_locator",
    "raw_page_sha256", "direct_lappy_http_result", "source_text_fingerprint_mode",
    "upstream_discovery_csv", "upstream_discovery_sha256", "independent_corroboration",
}
CARD_KEYS = {
    "id", "season", "source_ordinal", "source_title", "title_reconciliation",
    "blurb_sha256", "blurb_normalized_chars", "locator", "evidence_state", "work_id",
    "publisher_image_locator", "publisher_video_locator", "original_synopsis", "synopsis_status",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def strict_pairs(pairs):
    out = {}
    for name, value in pairs:
        require(name not in out, "Duplicate JSON key: " + name)
        out[name] = value
    return out


def canonical_digest(obj: object) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate(data: dict, repo: Path = REPO) -> None:
    require(type(data) is dict and set(data) == ENVELOPE_KEYS, "unknown packet envelope")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema drift")
    require(data["packet_id"] == "voy-s4-e10-e14-publisher-cards-20261103", "packet drift")
    require(data["role"] == "VOY_SOURCE_LOCAL", "role drift")
    require(data["base_accepted_main"] == ACCEPTED_SHA, "accepted base drift")
    require(data["observation_date_utc"] == "2026-11-03", "observation date drift")
    require(data["status"] == "HELD_PROPOSAL_ONLY", "false status promotion")
    for key in ("rights_or_publication_effect", "source_binding_effect", "global_work_identity_effect", "coverage_effect"):
        require(data[key] == "NONE", "unapproved effect: " + key)
    for key in ("episode_source_read", "transcript_or_full_text_read", "images_or_videos_retrieved"):
        require(data[key] is False, "false source/media read: " + key)

    src = data["source"]
    require(type(src) is dict and set(src) == SOURCE_KEYS, "unknown source metadata")
    require(src["id"] == "paramount-voy-s4-guide-rendered", "foreign source")
    parsed = urlparse(src["url"])
    require((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment) == (
        "https", "www.paramountplus.com", "/shows/star_trek_voyager/episodes/4/", "", "", "",
    ), "source URL out of bounds")
    require(src["lineage_group"] == "PARAMOUNT_CBS_SKYDANCE_CORPORATE", "lineage escalation")
    require(src["type"] == "FIRST_PARTY_PUBLISHER_GUIDE", "source category")
    require(src["read_representation"] == "WEB_RENDERED_HTML_TEXT", "read modality drift")
    require(src["source_locator"] == "Season 4 > Episode Guide > S4 E10 through S4 E14", "source locator")
    require(src["raw_page_sha256"] is None, "raw response was not archived")
    require(src["direct_lappy_http_result"] == "HTTP_406_NOT_ACCEPTABLE", "direct fetch status drift")
    require(src["source_text_fingerprint_mode"] == "SHA256_OF_NFKC_WHITESPACE_COLLAPSED_RENDERED_CARD_BLURB_UNARCHIVED", "fingerprint provenance drift")
    require(src["upstream_discovery_csv"] == UPSTREAM_CSV and src["upstream_discovery_sha256"] == UPSTREAM_SHA, "upstream discovery locator")
    require(src["independent_corroboration"] is False, "dependent publisher not independent corroboration")

    upstream_path = (repo / UPSTREAM_CSV).resolve()
    require(upstream_path.is_relative_to(repo.resolve()) and upstream_path.is_file(), "unsafe/missing discovery CSV")
    raw = upstream_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == UPSTREAM_SHA, "accepted discovery CSV changed")
    all_discovered = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    require(len(all_discovered) >= 14, "discovery row shortage")

    rows = data["source_local_cards"]
    require(type(rows) is list and len(rows) == 5, "exact five-card batch required")
    seen = set()
    for row in rows:
        require(type(row) is dict and set(row) == CARD_KEYS, "unknown card schema")
        n = row["source_ordinal"]
        require(type(n) is int and n in TITLES and n not in seen, "invalid/duplicate episode ordinal")
        seen.add(n)
        title = TITLES[n]
        require(row["id"] == f"voy-s4-e{n:02d}-publisher-card", "source-local ID drift")
        require(type(row["season"]) is int and row["season"] == 4, "season drift")
        require(row["source_title"] == title, "publisher title drift")
        require(row["title_reconciliation"] == (
            "PUBLISHER_APOSTROPHE_VARIANT_HELD" if n == 13 else "SOURCE_DISPLAY_ONLY"
        ), "title identity overreach")
        require(row["locator"] == f"Season 4 > {title} > S4 E{n} > adjacent description", "source card locator")
        require(row["blurb_normalized_chars"] == BLURB_FINGERPRINTS[n][0]
                and row["blurb_sha256"] == BLURB_FINGERPRINTS[n][1], "rendered blurb fingerprint not reviewed")
        upstream_row = all_discovered[n - 1]
        require(upstream_row == {"season": "4", "episode_number": str(n), "title": title}, "publisher discovery card disagreement")
        require(row["evidence_state"] == "PUBLISHER_DISPLAY_ONLY_HELD", "source evidence promoted")
        require(row["work_id"] is None, "global Work relation not reconciled")
        require(row["publisher_image_locator"] is None and row["publisher_video_locator"] is None, "unread media link injected")
        require(row["synopsis_status"] == "HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW", "synopsis approved without review")
        require(type(row["original_synopsis"]) is str and 50 <= len(row["original_synopsis"]) <= 180, "synopsis length")
        require(canonical_digest(row) == ROW_DIGESTS[n], "code-pinned entire source-local row changed")
    require(seen == set(TITLES), "incomplete five-card batch")

    require(data["coverage_update"] == {
        "new_episode_discoveries": 0, "accepted_work_bindings": 0, "close_reads": 0,
        "released_synopses": 0, "released_artwork": 0, "status": "UNCHANGED",
    }, "fabricated coverage/publication effect")


if __name__ == "__main__":
    payload = json.loads(DATA.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)
    validate(payload)
    print("PASS: VOY S4 E10-E14 own-card rendered source HELD; five full-row pins; zero Work/coverage/publication effects")
