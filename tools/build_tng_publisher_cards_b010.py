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
OBSERVATIONS = Path("proposals/verification/tng-season1-publisher-b010-20261103/observations.json")
OUTPUT = Path("proposals/verification/tng-season1-publisher-b010-20261103/records.json")
CATALOG_SHA256 = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/"
BASE = "1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b"

# Exact observed source-local cards; the missing index 008 duplicates the already
# separately checked Hide-and-Q publisher card in accepted B004.
EXPECTED = (
    ("000", "Encounter At Farpoint Part 1 and 2", 1, "6c154fb038c5059de5a40b42d20b7b02312b9cf34c3b73dc5ddc3db7b9804be8"),
    ("001", "The Naked Now", 3, "29bcb303adf5eb8c44680fda1d3e09b1a90973404beb70f537e3b730f1c60665"),
    ("002", "Code of Honor", 4, "8a74dcefebcda160462d8f72261a7c3524133149f8b8228e77995d30dbc60a7b"),
    ("003", "The Last Outpost", 5, "647db450e72d8644fbd70ec6a35dcd8fdc1fda4722a476fd188caa021ec45d24"),
    ("004", "Where No One Has Gone Before", 6, "6e32b4046dc9f67dc1e7f4626d945105b294bb68506209f486a04f7ae686da79"),
    ("005", "Lonely Among Us", 7, "dd8d258e3775ddd37becc73c6fb63abca2265ac63d93625a5c743f630ec56f0b"),
    ("006", "Justice", 8, "cea8637109a9333c6ce66aee4e2a8cd8095acbc877f79b0bfff3d46fc0b62418"),
    ("007", "The Battle", 9, "e6d7cb86434e62e97960ca689e720b5fe6cf2bf8c545f9404f30ef2c6427fe62"),
    ("009", "Haven", 11, "10e9d9e1223b7e27c2bd66d04b8a41c7e7312bb7729ac17b9253a3d35c4c0c1b"),
    ("010", "The Big Goodbye", 12, "1502728b12bcc254844b63360761c07146eff441a2873ea73d67ac9d04cc6d0d"),
)
# Exact, publisher-page-observed card-to-image binding. Hostname validation by
# itself is insufficient: a different episode's legitimate CBS URL must fail.
# These literals are historical source-observation pins, NOT reusable licenses.
EXPECTED_ARTWORK = (
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2020/10/30/1813765187999/CBS_STAR_TREK_TNG_101_102_0721_HD_1920x1080_1122557_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26443843630/CBS_TNG_103_HD_IMAGE_CIAN_1122579_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26440771931/CBS_TNG_104_HD_IMAGE_CIAN_1122566_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26444355671/CBS_TNG_107_HD_IMAGE_CIAN_1122564_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26443331944/CBS_TNG_106_HD_IMAGE_CIAN_1122576_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26443843933/CBS_TNG_108_HD_IMAGE_CIAN_1122580_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26443843966/CBS_TNG_109_HD_IMAGE_CIAN_R_3164061_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26445891797/CBS_TNG_110_HD_IMAGE_CIAN_1122578_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26442819828/CBS_TNG_105_HD_IMAGE_CIAN_1122572_1920x1080.jpg",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26452035698/CBS_TNG_113_HD_IMAGE_CIAN_R_3164056_1920x1080.jpg",
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
            or observations["proposal_id"] != "TNG-S1-B010-PUBLISHER-CARDS-20261103"
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
        expected_hold = ("COMBINED_PART_1_AND_2_PUBLISHER_CARD_NO_PART_SPLIT" if i == 0
                         else "NO_GLOBAL_WORK_IDENTITY_ASSERTED")
        if row["identity_hold"] != expected_hold:
            raise ValueError("unreviewed Work/part identity reconciliation")
        synopsis = row["original_synopsis_draft"]
        if (not isinstance(synopsis, str) or len(synopsis) < 40 or len(synopsis) > 250
                or "TODO" in synopsis or "TBD" in synopsis):
            raise ValueError("unreviewed, missing or unusually long synopsis")
        entities = row["entity_mentions_source_relative"]
        if (not isinstance(entities, list) or not entities or len(entities) > 5
                or len(entities) != len(set(map(str, entities)))
                or any(not isinstance(e, str) or not 1 <= len(e) <= 50 for e in entities)):
            raise ValueError("unsupported entity mention structure")
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
        "data_status": "B010-TNG-S1-PUBLISHER_SOURCE_RECHECK_PROPOSAL_ONLY",
        "catalog_sha256": CATALOG_SHA256,
        "observations_sha256": hashlib.sha256(
            json.dumps(observations, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "source_local_rows_rechecked": 10,
        "publisher_card_slots_read": 10,
        "combined_multipart_identity_holds": 1,
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
            raise SystemExit("B010 TNG records stale or tampered; rebuild required")
        print("B010 TNG source-only records: exact deterministic check PASS")
    else:
        target.write_text(computed, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
