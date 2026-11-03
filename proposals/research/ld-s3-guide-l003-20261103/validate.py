#!/usr/bin/env python3
"""Fail-closed Lower Decks S3 first-party source-only guide-card validator."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/3/"
CSV_PATH = "proposals/discovery/modern-paramount-season3-20261102/ld-observed-slots.csv"
BUNDLE_PATH = "proposals/discovery/modern-paramount-season3-20261102/ld/bundle.json"
CSV_SHA = "51687fbbeec8ef721c053f5f96d65724ccb23262f5464229757616870bc1690e"
BUNDLE_SHA = "1c23cb2c7ca77089deeb2191447bc9ab5241d1103750105c1ef6e23032e41dbd"
RAW_SHA = "6047c304d8af99e889c8bfb489a5c09584aa8b2e9847fb9eba1ebe655b1726e8"
PINS = (
    ("Grounded", "082ca564efde2e5a653bb7340750be2680ac8737717b8ad0d5c2e4494debc4e6", ("Mariner", "Captain Freeman", "Pakled Planet")),
    ("The Least Dangerous Game", "5a05c7a87fe9ea48b461b64542d7338d2dfc9d5808cd283c99ba81134c390881", ("Mariner", "Commander Ransom", "Boimler")),
    ("Mining the Mind's Mines", "b2c6ede1104704a49ba2bdba7a34747c3fc11253532a5497f65bf0213697dc15", ("Tendi", "Senior Science Officer Trainee")),
    ("Room for Growth", "6c2cbf303b5c84c61489d87fe98d41cd0e3c2111b808787ed6014732f6958245", ("Mariner", "Boimler", "Tendi", "Delta Shift", "Cerritos")),
    ("Reflections", "9cbe3a635c0f92b3c8675bfd587924bfb489a3f3e3014b351fc77905341beb78", ("Mariner", "Boimler", "Starfleet", "Rutherford")),
    ("Hear All, Trust Nothing", "b8b40238f7bdc894ce1ada8d3640ee31801fcc08640b40619ff9f9538874925a", ("Cerritos", "Deep Space Nine")),
    ("A Mathematically Perfect Redemption", "57acd24d74bd9ae6372030efd03065009a2141d422183dfedb7e99c3fa5f52d6", ("Starfleet",)),
    ("Crisis Point 2: Paradoxus", "7d34a992ad427cc096c57ed0342fa9986bedcb8f38bca6cd40c7dce7830320b9", ("Boimler",)),
    ("Trusted Sources", "5a3d21e8c8f4cd02b4f6afc83a4e6d79c32505194fc6d77e324a26c92786969a", ("Cerritos", "Captain Freeman")),
    ("The Stars at Night", "aa1feb9785600a56655f6d43b18b7c808f54b74eb160704548d72db50d16ae55", ("Cerritos",)),
)
EXPECTED_TOP = {
    "schema_version": "1.0.0", "batch_id": "ld-s3-guide-l003-20261103", "role": "LD",
    "proposal_only": True, "accepted_main_at_selection": "1ef3e4ef9cefa0e3ccd90caa4530a84c167a8ca6",
    "observed_utc_date": "2026-11-03", "publisher_guide_url": GUIDE,
    "source_scope": "PUBLIC_PARAMOUNT_LD_S3_GUIDE_TITLE_SLOT_DESCRIPTION_DIGEST_AND_LITERAL_MENTIONS",
    "publisher_source_family": "publisher:paramountplus.com",
    "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
    "historical_s3_csv_sha256": CSV_SHA, "historical_s3_bundle_sha256": BUNDLE_SHA,
    "current_http_status_observed": 200, "current_raw_html_bytes_observed": 272206,
    "current_raw_html_sha256_observed": RAW_SHA, "current_raw_html_archived": False,
    "actual_episode_or_script_read": False,
    "description_source_policy": "DIGEST_AND_LITERAL_MENTION_TOKENS_ONLY_NO_BLURBS_OR_PARAPHRASES_STORED",
    "synopsis_policy": "ALL_HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE",
    "artwork_policy": "FIRST_PARTY_GUIDE_PAGE_LEAD_ONLY_NO_ASSET_OR_RIGHTS",
    "accepted_source_work_effect": "NONE", "accepted_work_effect": "NONE", "coverage_effect": "NONE",
    "public_synopsis_effect": "NONE", "public_artwork_effect": "NONE",
}
RECORD_KEYS = {
    "observation_id", "local_card_entity_id", "season", "episode", "publisher_card_title",
    "publisher_description_sha256", "card_locator", "evidence_kind", "evidence_scope",
    "literal_mentions", "literal_mention_scope", "synopsis_status", "artwork_candidate_page_url",
    "artwork_asset_url", "artwork_rights_status", "accepted_work_id",
}


def require(ok, reason):
    if not ok:
        raise ValueError("LD L003 source custody invalid: " + reason)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
            "unsafe JSON path/size")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def digest_file(relative, expected):
    path = ROOT / relative
    require(path.is_file() and not path.is_symlink(), "missing/symlinked historical input")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, "historical byte drift")
    return path


def validate(data=None):
    if data is None:
        data = read_json(HERE / "observations.json")
    require(type(data) is dict and set(data) == set(EXPECTED_TOP) | {"records"},
            "exact top-level schema")
    for field, expected in EXPECTED_TOP.items():
        require(type(data[field]) is type(expected) and data[field] == expected,
                "source/admission field: " + field)

    with digest_file(CSV_PATH, CSV_SHA).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 10 and all(rows[i] == {
        "season": "3", "episode_number": str(i+1), "title": PINS[i][0],
    } for i in range(10)), "historical same-family 10-card directory")
    bundle = read_json(digest_file(BUNDLE_PATH, BUNDLE_SHA))
    require(bundle["mission_id"] == "ld" and
            bundle["observation"]["primary_locator"] == GUIDE and
            bundle["listed_slot_count"] == 10 and
            bundle["coverage_effect"] == "NONE" and
            bundle["accepted_work_effect"] == "NONE", "historical source/status")

    records = data["records"]
    require(type(records) is list and len(records) == 10, "ten exact guide cards")
    ids = set()
    for i, rec in enumerate(records, 1):
        require(type(rec) is dict and set(rec) == RECORD_KEYS, f"card {i} closed schema")
        title, sha, mentions = PINS[i - 1]
        evidence_id = f"ld-l003-o{i:02d}"
        require(rec["observation_id"] == evidence_id and
                rec["local_card_entity_id"] == f"ld-l003-card-{i:02d}" and
                evidence_id not in ids, f"card {i} local identities")
        ids.add(evidence_id)
        require(type(rec["season"]) is int and rec["season"] == 3 and
                type(rec["episode"]) is int and rec["episode"] == i and
                rec["publisher_card_title"] == title and
                rec["publisher_description_sha256"] == sha, f"card {i} title/slot/description fingerprint")
        require(rec["card_locator"] == f"Season 3 Episode Guide > S3 E{i} > {title} > description",
                f"card {i} source locator")
        require(rec["evidence_kind"] == "PUBLISHER_CARD_DISPLAY_AND_LITERAL_DESCRIPTION_MENTION" and
                rec["evidence_scope"] == "TITLE_SLOT_DESCRIPTION_DIGEST_AND_MENTIONS_NOT_PLOT_FACTS" and
                rec["literal_mention_scope"] == "PUBLISHER_DESCRIPTION_TEXT_ONLY" and
                type(rec["literal_mentions"]) is list and rec["literal_mentions"] == list(mentions),
                f"card {i} publisher utterance boundaries")
        require(rec["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                rec["artwork_candidate_page_url"] == GUIDE and
                rec["artwork_asset_url"] is None and
                rec["artwork_rights_status"] == "UNKNOWN_HELD" and
                rec["accepted_work_id"] is None, f"card {i} synopsis/artwork/Work holds")
    return len(records)


if __name__ == "__main__":
    print(f"LD_L003_OK: {validate()} exact S3 guide cards; no accepted Work/coverage/artwork release")
