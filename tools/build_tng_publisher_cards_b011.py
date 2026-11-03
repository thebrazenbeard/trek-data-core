#!/usr/bin/env python3
"""Deterministic *held* source-relative TNG S1 publisher-card proposal compiler.

No network at compile time: the source cards were read directly on 2026-11-03.
This module does not promote coverage, global identity, media use, or synopsis release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBSERVATIONS = Path("proposals/verification/tng-season1-publisher-b011-20261103/observations.json")
OUTPUT = Path("proposals/verification/tng-season1-publisher-b011-20261103/records.json")
CATALOG_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/"
BASE = "a81d1829b394af66fb1a1d1a2c93a6b374fa81ef"

EXPECTED = (
    ("011", "Datalore", 13, "a3970bf53329e5ba9dd7e0c51e76231398932c85e46ee6d2d19fec6097808370"),
    ("012", "Angel One", 14, "d9e6871dee039a5c166b7edc521c2bbf9c24d4bab5824d50a2e6c4859f208fae"),
    ("013", "11001001", 15, "3bc6d753d4d0c77d78bac368cd10dc43734d3eba35b02c2f0f59bfb3709e4e7e"),
    ("014", "Too Short a Season", 16, "4fe0e5419e507beea982b0d6351aa31010a17dc2367255705c9731616e9d3af9"),
    ("015", "When the Bough Breaks", 17, "5adf27fff80bda0bc17756bf8c3d53ae35207d9434313ec478414bdded5789b9"),
    ("016", "Home Soil", 18, "ba80c2f4087047eb1a3b9cd5c96bf78b4165df9434cdf3505f2549e758d7b466"),
    ("017", "Coming of Age", 19, "ddb289b70d50e68289bad71c1d9d10156c44ece981537b0cd1bbe495ff720709"),
    ("018", "Heart of Glory", 20, "856cd6a6f476dcdc8b8698d16d0b29e156123ec04c898e2aa6984969ea9d029b"),
    ("019", "The Arsenal of Freedom", 21, "37bcc6c6f321c32ca8da9ba47457a200f8d59ade42524d1a0bf092d39db322d6"),
    ("020", "Symbiosis", 22, "6d4df41b58780d58ae3f7590db6e815a26d77a0c4c1d48728b64dd1ebf28a5ee"),
)

# Exact newly reviewed source-local cards, disjoint from accepted preceding wave.
# Publisher URL values are historical source observations, NOT reuse licenses.
EXPECTED_ARTWORK = (
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26450499987/CBS_TNG_114_HD_IMAGE_CIAN_R_3164052_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26453571626/CBS_TNG_115_HD_IMAGE_CIAN_R_3164051_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26451523796/CBS_TNG_116_HD_IMAGE_CIAN_1122571_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26451523622/CBS_TNG_112_HD_IMAGE_CIAN_1122570_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26452035910/CBS_TNG_118_HD_IMAGE_CIAN_1122568_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26452035841/CBS_TNG_117_HD_IMAGE_CIAN_1122574_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26455107532/CBS_TNG_119_HD_IMAGE_CIAN_1122567_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26452547870/CBS_TNG_120_HD_IMAGE_CIAN_1122563_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26453059797/CBS_TNG_121_HD_IMAGE_CIAN_1122575_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26456131538/CBS_TNG_123_HD_IMAGE_CIAN_1122561_1920x1080.jpg",
)
# Exact literal source-phrase mentions, with no lore-based identity resolution.
EXPECTED_SYNOPSIS_SHA256 = (
    "890b7096d420faa538d0f67b148500e5fc135169c112757aa922e58cb4fc10b2",
    "197e27f8227f4752bd2b1e566905d6f8f67a05716003bd39583ed33f8c65e38c",
    "50fef2332ebb317d5207c38836112d05b104b52d4d4b45d1b5274cd03e399d84",
    "29508a6499a7a8383a3cf2dcee0c2f65a2d0430ae9890316de744e131f26205a",
    "1fbe36bf4699e799d938effc5492674246366bb4ce947ee8227ff1a2f53be803",
    "fd12cc04109d8383a486a8e8ae9d27d300172b4c5dac5fc580f9486d26a9049c",
    "1db7281b07450975b02913e87726296fdf566160db0879873c8b4a3ec4f5b905",
    "32c7085728884e300ded69ee7f8971547d0ff4f0de5722bb3d583a61e942fb47",
    "9c22c0f851cd91ec158c77b50b532360e91586f9c154ffb7e93cd2eeb2a84b8c",
    "cb7e4be14d64fcdc5a279b0511a4516ec5bc87ecb83b4501e21ed744eb3594b4",
)
EXPECTED_MENTIONS = (
    ("Data", "Enterprise"),
    ("away team", "Enterprise"),
    ("Enterprise",),
    ("Enterprise", "Federation"),
    ("Wesley", "Enterprise"),
    ("humans", "Enterprise"),
    ("Wesley", "Starfleet Academy", "Captain Picard"),
    ("Lt. Worf", "Enterprise", "Klingon"),
    ("Picard", "away team"),
    ("Enterprise",),
)
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
    "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
    "audiovisual_episodes_watched", "public_synopsis_authorized",
    "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect", "rows",
}
ROW_KEYS = {
    "row_id", "publisher_title", "season", "episode", "publisher_description_sha256",
    "original_synopsis_draft", "entity_mentions_source_relative", "publisher_thumbnail_url", "identity_hold",
}


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def load_json(path):
    file = ROOT / path
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 4_000_000:
        raise ValueError(f"missing, symlinked or excessive input: {path}")
    data = file.read_bytes()
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_pairs), data


def compile_records(catalog, catalog_bytes, observations):
    if (hashlib.sha256(catalog_bytes).hexdigest() != CATALOG_SHA256
            or catalog.get("row_count") != 1214
            or catalog.get("data_status") != "DISCOVERY_ONLY"
            or catalog.get("admission_effect") != "NONE"
            or catalog.get("coverage_effect") != "NONE"):
        raise ValueError("accepted discovery snapshot mismatch")
    if (not isinstance(observations, dict) or set(observations) != TOP_KEYS
            or observations["schema_version"] != "1.0.0"
            or observations["proposal_id"] != "TNG-S1-B011-PUBLISHER-CARDS-20261103"
            or observations["baseline_accepted_main"] != BASE
            or observations["observed_utc_date"] != "2026-11-03"
            or observations["source_family"] != "paramount_corporate_publisher_family"
            or observations["guide_url"] != GUIDE
            or observations["read_surface"] != "PUBLISHER_RENDERED_GUIDE_AND_RAW_HTML_CARD_METADATA"
            or observations["raw_html_bytes_archived"] is not False
            or observations["audiovisual_episodes_watched"] is not False
            or observations["public_synopsis_authorized"] is not False
            or observations["artwork_copy_or_publication_authorized"] is not False
            or observations["admission_effect"] != "NONE"
            or observations["coverage_effect"] != "NONE"
            or not isinstance(observations["rows"], list)
            or len(observations["rows"]) != len(EXPECTED)):
        raise ValueError("held observation envelope invalid")

    lookup = {r["row_id"]: r for r in catalog["rows"]}
    if len(lookup) != 1214:
        raise ValueError("ambiguous catalog row identity")
    out = []
    for i, row in enumerate(observations["rows"]):
        key, title, episode, digest = EXPECTED[i]
        row_id = f"legacy:s1:tng:{key}"
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise ValueError("observation row schema mismatch")
        if (row["row_id"] != row_id or row["publisher_title"] != title
                or type(row["season"]) is not int or row["season"] != 1
                or type(row["episode"]) is not int or row["episode"] != episode
                or row["publisher_description_sha256"] != digest):
            raise ValueError("publisher card title/slot/content fingerprint drift")
        expected_hold = "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
        if row["identity_hold"] != expected_hold:
            raise ValueError("unreviewed Work/part identity reconciliation")
        synopsis = row["original_synopsis_draft"]
        if (not isinstance(synopsis, str) or len(synopsis) < 40 or len(synopsis) > 250
                or "TODO" in synopsis or "TBD" in synopsis
                or hashlib.sha256(synopsis.encode("utf-8")).hexdigest() != EXPECTED_SYNOPSIS_SHA256[i]):
            raise ValueError("unreviewed, missing or unusually long synopsis")
        entities = row["entity_mentions_source_relative"]
        if (not isinstance(entities, list) or not entities or len(entities) > 5
                or len(entities) != len(set(map(str, entities)))
                or any(not isinstance(e, str) or not 1 <= len(e) <= 50 for e in entities)
                or tuple(entities) != EXPECTED_MENTIONS[i]):
            raise ValueError("source-relative mention not literally supported by publisher card")
        artwork = row["publisher_thumbnail_url"]
        parts = urlsplit(artwork) if isinstance(artwork, str) else None
        if (not parts or parts.scheme != "https" or parts.hostname != "thumbnails.cbsig.net"
                or not re.fullmatch(r"/_x/w400/CBS_Production_Entertainment_VMS/[\w/.-]+\.jpg", parts.path)
                or parts.query or parts.fragment or artwork != EXPECTED_ARTWORK[i]):
            raise ValueError("publisher episode card-to-image binding mismatch")
        source = lookup.get(row_id)
        if (not source or source["title"] != title or source["context"] != f"TNG S1E{episode}"
                or source["medium"] != "EPISODE" or source["candidate_kind"] != "PUBLISHER_EPISODE_SLOT"
                or source["source_group"] != "publisher:paramount"
                or source["source_input"] != "proposals/discovery/legacy-paramount-season1-20261102/tng/bundle.json"
                or source["source_locator"] != GUIDE or source["verification_status"] != "UNVERIFIED_METADATA"
                or source["admission_effect"] != "NONE" or source["coverage_effect"] != "NONE"):
            raise ValueError("unverified source-local discovery binding changed")
        out.append({
            "source_local_row_id": row_id,
            "source_local_title": source["title"],
            "source_local_context": source["context"],
            "source_local_lineage": "paramount_publisher_guide_prior_listing",
            "publisher_lineage": "paramount_corporate_publisher_family",
            "publisher_card": {
                "guide_url": GUIDE,
                "section_locator": f"Episode Guide > {title} > S1 E{episode} > short description",
                "title": title,
                "season": 1,
                "episode": episode,
                "publisher_description_sha256": digest,
                "brief_description_actually_read": True,
                "raw_webpage_sha256": None,
            },
            "source_relative_entity_mentions": entities,
            "assertion_frame": "MENTIONS_IN_PUBLISHER_DESCRIPTION_NOT_EPISODE_TRUTH",
            "original_synopsis_draft": synopsis,
            "synopsis_publication_status": "PENDING_HUMAN_AND_EDITORIAL_REVIEW",
            "publisher_thumbnail_url_held": artwork,
            "artwork_asset_status": "URL_DISCOVERY_ONLY_NO_LICENSE_ADMISSION_OR_IMAGE_COPY",
            "identity_resolution": row["identity_hold"],
            "source_body_custody": "NOT_ARCHIVED_HTML_RETRIEVED_FOR_READ_ONLY_INSPECTION",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE",
            "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "B011-TNG-S1-PUBLISHER_SOURCE_RECHECK_PROPOSAL_ONLY",
        "catalog_sha256": CATALOG_SHA256,
        "observations_sha256": hashlib.sha256(
            json.dumps(observations, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "source_local_rows_rechecked": 10,
        "publisher_card_slots_read": 10,
        "combined_multipart_identity_holds": 0,
        "original_synopsis_drafts_held": 10,
        "publisher_artwork_url_leads_held": 10,
        "public_synopses_or_images_published": 0,
        "governed_research_admissions": 0,
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
        "rows": out,
    }


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, catalog_raw = load_json(CATALOG)
    observations, _ = load_json(OBSERVATIONS)
    computed = serialized(compile_records(catalog, catalog_raw, observations))
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != computed:
            raise SystemExit("B011 TNG records stale or tampered; rebuild required")
        print("B011 TNG source-only records: exact deterministic check PASS")
    else:
        target.write_text(computed, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
