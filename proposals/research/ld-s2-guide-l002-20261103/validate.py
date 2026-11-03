#!/usr/bin/env python3
"""Fail-closed validation of source-local Lower Decks S2 guide-card proposals."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/2/"
CSV_PATH = "proposals/discovery/modern-paramount-season2-first5-20261102/ld-observed-slots.csv"
BUNDLE_PATH = "proposals/discovery/modern-paramount-season2-first5-20261102/ld/bundle.json"
CSV_SHA = "603c969c7a2d82cd99d63610ca04371db0dbdeeb9dbef1aed21176178f2b4115"
BUNDLE_SHA = "f7514d54a138df96c33264cc21510fabc74a1f954cf16bbf09bc432b77330c66"
RAW_SHA = "168764bebbde440545fb6471be24b3162d9b5718802eb6cdf0594f459419ed8c"
TITLES_AND_MENTIONS = (
    ("Strange Energies", ("U.S.S. Cerritos", "Commander Ransom")),
    ("Kayshon, His Eyes Open", ("Ensign Jet Manhaver", "Boimler", "U.S.S. Titan")),
    ("We'll Always Have Tom Paris", ("Dr. T Ana", "Tendi", "Mariner", "U.S.S. Cerritos", "Rutherford")),
    ("Mugato, Gumato", ("U.S.S. Cerritos", "Mugato")),
    ("An Embarrassment of Dooplers", ("Mariner", "Boimler", "Starfleet")),
    ("The Spy Humongous", ("U.S.S. Cerritos", "Lower Deckers", "Captain Freeman", "Pakled")),
    ("Where Pleasant Fountains Lie", ("Mariner", "Boimler", "Cerritos", "Lt. Commander Billups")),
    ("I, Excretus", ("U.S.S. Cerritos",)),
    ("wej Duj", ("Boimler", "U.S.S. Cerritos")),
    ("First First Contact", ("U.S.S. Cerritos",)),
)
EXPECTED_TOP = {
    "schema_version": "1.0.0",
    "batch_id": "ld-s2-guide-l002-20261103",
    "role": "LD",
    "proposal_only": True,
    "accepted_main_at_selection": "7e0c56e5bbef70296de034e5283ed6217e6e7f91",
    "observed_utc_date": "2026-11-03",
    "publisher_guide_url": GUIDE,
    "source_scope": "PUBLIC_PARAMOUNT_LD_S2_GUIDE_TITLE_SLOT_AND_LITERAL_DESCRIPTION_MENTIONS",
    "publisher_source_family": "publisher:paramountplus.com",
    "source_independence_status": "SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION",
    "historical_s2_first5_csv_sha256": CSV_SHA,
    "historical_s2_first5_bundle_sha256": BUNDLE_SHA,
    "current_http_status_observed": 200,
    "current_raw_html_bytes_observed": 273095,
    "current_raw_html_sha256_observed": RAW_SHA,
    "current_raw_html_archived": False,
    "actual_episode_or_script_read": False,
    "description_source_policy": "LITERAL_MENTION_TOKENS_ONLY_NO_BLURBS_OR_PARAPHRASES_STORED",
    "synopsis_policy": "ALL_HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE",
    "artwork_policy": "FIRST_PARTY_GUIDE_PAGE_LEAD_ONLY_NO_ASSET_OR_RIGHTS",
    "accepted_source_work_effect": "NONE",
    "accepted_work_effect": "NONE",
    "coverage_effect": "NONE",
    "public_synopsis_effect": "NONE",
    "public_artwork_effect": "NONE",
}
RECORD_FIELDS = {
    "observation_id", "local_card_entity_id", "season", "episode", "publisher_card_title",
    "card_locator", "evidence_kind", "evidence_scope", "literal_mentions",
    "literal_mention_scope", "synopsis_status", "artwork_candidate_page_url",
    "artwork_asset_url", "artwork_rights_status", "accepted_work_id",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(f"LD L002 source custody invalid: {message}")


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def read_json(path: Path):
    require(path.is_file() and not path.is_symlink(), "unsafe JSON source")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def digest_file(relative: str, expected: str) -> Path:
    p = ROOT / relative
    require(p.is_file() and not p.is_symlink(), "missing or symlinked historical input")
    require(hashlib.sha256(p.read_bytes()).hexdigest() == expected, "historical input drift")
    return p


def validate(data=None) -> int:
    if data is None:
        data = read_json(HERE / "observations.json")
    require(isinstance(data, dict) and set(data) == set(EXPECTED_TOP) | {"records"}, "closed top-level schema")
    for key, expected in EXPECTED_TOP.items():
        require(type(data[key]) is type(expected) and data[key] == expected, f"source/admission scope: {key}")

    with digest_file(CSV_PATH, CSV_SHA).open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 5 and all(rows[i] == {
        "season": "2", "episode_number": str(i + 1), "title": TITLES_AND_MENTIONS[i][0],
    } for i in range(5)), "historical first-five source-local directory")
    bundle = read_json(digest_file(BUNDLE_PATH, BUNDLE_SHA))
    require(bundle["mission_id"] == "ld" and
            bundle["observation"]["primary_locator"] == GUIDE and
            bundle["listed_slot_count"] == 5 and
            bundle["coverage_effect"] == "NONE" and
            bundle["accepted_work_effect"] == "NONE", "historical family/status")

    records = data["records"]
    require(type(records) is list and len(records) == 10, "exactly ten cards")
    ids = set()
    for i, rec in enumerate(records, 1):
        require(type(rec) is dict and set(rec) == RECORD_FIELDS, f"card {i} closed schema")
        title, mentions = TITLES_AND_MENTIONS[i - 1]
        observed_id = f"ld-l002-o{i:02d}"
        require(rec["observation_id"] == observed_id and
                rec["local_card_entity_id"] == f"ld-l002-card-{i:02d}", f"card {i} source-local IDs")
        require(observed_id not in ids, "duplicate evidence ID")
        ids.add(observed_id)
        require(type(rec["season"]) is int and rec["season"] == 2 and
                type(rec["episode"]) is int and rec["episode"] == i and
                rec["publisher_card_title"] == title, f"card {i} title/slot")
        require(rec["card_locator"] == f"Season 2 Episode Guide > S2 E{i} > {title} > description",
                f"card {i} locator")
        require(rec["evidence_kind"] == "PUBLISHER_CARD_DISPLAY_AND_LITERAL_DESCRIPTION_MENTION" and
                rec["evidence_scope"] == "TITLE_SLOT_AND_MENTION_TOKENS_NOT_PLOT_FACTS" and
                rec["literal_mention_scope"] == "PUBLISHER_DESCRIPTION_TEXT_ONLY" and
                type(rec["literal_mentions"]) is list and rec["literal_mentions"] == list(mentions),
                f"card {i} publisher utterance/mentions")
        require(rec["synopsis_status"] == "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE" and
                rec["artwork_candidate_page_url"] == GUIDE and
                rec["artwork_asset_url"] is None and rec["artwork_rights_status"] == "UNKNOWN_HELD" and
                rec["accepted_work_id"] is None, f"card {i} rights/identity hold")
    return len(records)


if __name__ == "__main__":
    print(f"LD_L002_OK: {validate()} source-local Season 2 guide cards; no AV/Work/coverage/art rights")
