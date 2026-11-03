#!/usr/bin/env python3
"""Deterministic held TNG S1 E23–26 source-card proposal; not episode coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
OBSERVATIONS = Path("proposals/verification/tng-season1-publisher-b012-20261103/observations.json")
OUTPUT = Path("proposals/verification/tng-season1-publisher-b012-20261103/records.json")
PRIOR_B004 = Path("proposals/verification/episode-guide-rechecks-b004-20261103/observations.json")
PRIOR_B011_OBS = Path("proposals/verification/tng-season1-publisher-b011-20261103/observations.json")
PRIOR_B011_RECORDS = Path("proposals/verification/tng-season1-publisher-b011-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/"
BASE = "2070b0153228272b5dd667b0a23465ff49a95a5f"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
B004_SHA = "1b8e2dcf3fb80b17e9bda1565416e5a9a96181fc0be9b0b118dca9d7107aeed3"
B011_OBS_SHA = "89222839cbdf6e15f860efbce0d6aa6fd38bf0421a07c2813b1e915f4b83205a"
B011_RECORDS_SHA = "1e484266c0cf980fbbb1768b78bf624005007669f50135311e9ee2eba937eed4"

# (source-local suffix, exact publisher title, displayed episode, publisher-description digest,
#  independent original held blurb digest, literal source-description mentions,
#  exact official HTML image lead, overlapping accepted B004 seed if present)
EXPECTED = (
    ("021", "Skin of Evil", 23,
     "43bc68d6b8e50b544cec3ed2da0865ba9d945b9b0247e848456cda7a02896d67",
     "feec36f5ef821ce2fcc8b8d89ab1357ecf9ce0d1c822f651096f4092bd71c4a8",
     ("Enterprise",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26453059819/CBS_TNG_122_HD_IMAGE_CIAN_1732780_1920x1080.jpg", "lead:0043"),
    ("022", "We'll Always Have Paris", 24,
     "3867d1eb7f80d9cfdd57785648e97de403fa904799a7e1838a19cf33edf23e6a",
     "754b7d44636ded932d4fffe04bed0e0a0416e483a9064cbeec9320ed3f79e915",
     ("Captain Picard",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26455107770/CBS_TNG_124_HD_IMAGE_CIAN_1122558_1920x1080.jpg", None),
    ("023", "Conspiracy", 25,
     "a40a3decc5db26f99cd6eb5aff76994c961d41dc6ce24ccc794196fb5bbbd593",
     "966614bd215c3a5ae3ed3ae61a9e0f4f514b3b5c0769b03dee146518c71f94a0",
     ("Captain Picard", "Commander Riker", "Earth", "Starfleet"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26455107854/CBS_TNG_125_HD_IMAGE_CIAN_1122569_1920x1080.jpg", None),
    ("024", "The Neutral Zone", 26,
     "ecee596a410a394aaa3ffb5b638e5d2ff80ed138770abd50539aa9e9678760cc",
     "2392de60e84834798e69780cbe34a7b3eae1246828280211df341cdec53ad082",
     ("Romulans", "Americans"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/17/26454595923/CBS_TNG_126_HD_IMAGE_CIAN_1122560_1920x1080.jpg", "lead:0040"),
)
TOP_KEYS = {
    "schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
    "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
    "audiovisual_episodes_watched", "public_synopsis_authorized",
    "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect",
    "accepted_b004_observations_sha256", "accepted_b011_observations_sha256",
    "accepted_b011_records_sha256", "rows",
}
ROW_KEYS = {
    "row_id", "publisher_title", "season", "episode", "publisher_description_sha256",
    "original_synopsis_draft", "entity_mentions_source_relative", "publisher_thumbnail_url",
    "prior_same_family_title_slot_recheck_id", "identity_hold",
}


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path):
    file = ROOT / path
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 4_000_000:
        raise ValueError(f"missing, symlinked or excessive input: {path}")
    raw = file.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs), raw


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compile_records(catalog, catalog_raw, observations, b004, b004_raw,
                    b011_obs, b011_obs_raw, b011_records, b011_records_raw):
    require(sha(catalog_raw) == CATALOG_SHA and catalog.get("row_count") == 1214
            and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery snapshot drift")
    require(sha(b004_raw) == B004_SHA and b004.get("data_status") ==
            "RENDERED_PRIMARY_EPISODE_GUIDE_CARDS_WITH_MULTIPART_UNRESOLVED"
            and b004.get("admission_effect") == "NONE"
            and b004.get("coverage_effect") == "NONE", "accepted B004 drift")
    require(sha(b011_obs_raw) == B011_OBS_SHA and sha(b011_records_raw) == B011_RECORDS_SHA
            and b011_obs.get("admission_effect") == "NONE"
            and b011_obs.get("coverage_effect") == "NONE"
            and b011_records.get("governed_research_admissions") == 0,
            "accepted B011 byte or source-only drift")
    require(isinstance(observations, dict) and set(observations) == TOP_KEYS,
            "closed held observation schema")
    exact_envelope = {
        "schema_version": "1.0.0",
        "proposal_id": "TNG-S1-B012-PUBLISHER-CARDS-20261103",
        "baseline_accepted_main": BASE,
        "observed_utc_date": "2026-11-03",
        "source_family": "paramount_corporate_publisher_family",
        "guide_url": GUIDE,
        "read_surface": "PUBLISHER_RENDERED_GUIDE_AND_RAW_HTML_CARD_METADATA",
        "raw_html_bytes_archived": False,
        "audiovisual_episodes_watched": False,
        "public_synopsis_authorized": False,
        "artwork_copy_or_publication_authorized": False,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "accepted_b004_observations_sha256": B004_SHA,
        "accepted_b011_observations_sha256": B011_OBS_SHA,
        "accepted_b011_records_sha256": B011_RECORDS_SHA,
    }
    for field, expected in exact_envelope.items():
        require(type(observations[field]) is type(expected) and observations[field] == expected,
                f"unapproved envelope field {field}")
    require(isinstance(observations["rows"], list) and len(observations["rows"]) == 4,
            "four observed cards only")

    directory = {r["row_id"]: r for r in catalog["rows"]}
    require(len(directory) == 1214, "ambiguous discovery local ID")
    prior_s1 = {(r["season"], r["episode"]) for r in b011_obs["rows"]}
    prior_ids = {r["row_id"] for r in b011_obs["rows"]}
    require(prior_ids == {f"legacy:s1:tng:{i:03d}" for i in range(11, 21)}
            and prior_s1 == {(1, i) for i in range(13, 23)}, "accepted B011 frontier")
    b004_overlap = {}
    for prior in b004["rows"]:
        if prior.get("series") == "TNG":
            for card in prior["cards"]:
                if card["season"] == 1 and 23 <= card["episode"] <= 26:
                    b004_overlap[(card["episode"], card["official_title"])] = prior["row_id"]
    require(b004_overlap == {(23, "Skin of Evil"): "lead:0043",
                             (26, "The Neutral Zone"): "lead:0040"},
            "preexisting B004 same-publisher overlap changed")

    records = []
    for index, (row, expected) in enumerate(zip(observations["rows"], EXPECTED)):
        key, title, episode, description_digest, synopsis_digest, mentions, art, overlap = expected
        row_id = f"legacy:s1:tng:{key}"
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "closed source-card fields")
        require(row["row_id"] == row_id and row["publisher_title"] == title
                and type(row["season"]) is int and row["season"] == 1
                and type(row["episode"]) is int and row["episode"] == episode
                and row["publisher_description_sha256"] == description_digest,
                "source title/slot/description fingerprint mismatch")
        synopsis = row["original_synopsis_draft"]
        require(isinstance(synopsis, str) and 40 <= len(synopsis) <= 250
                and sha(synopsis.encode("utf-8")) == synopsis_digest,
                "unreviewed held synopsis edit")
        require(isinstance(row["entity_mentions_source_relative"], list)
                and tuple(row["entity_mentions_source_relative"]) == mentions,
                "not an exact literal publisher-description mention list")
        image = row["publisher_thumbnail_url"]
        parts = urlsplit(image) if isinstance(image, str) else None
        require(parts and parts.scheme == "https" and parts.hostname == "thumbnails.cbsig.net"
                and re.fullmatch(r"/_x/w400/CBS_Production_Entertainment_VMS/[\w/.-]+\.jpg", parts.path)
                and not parts.query and not parts.fragment and image == art,
                "wrong episode image URL or unapproved artwork locator")
        require(row["prior_same_family_title_slot_recheck_id"] == overlap
                and b004_overlap.get((episode, title)) == overlap,
                "unacknowledged same-family B004 overlap or forged identity")
        require(row["identity_hold"] == "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
                "Work reconciliation not authorized")
        source = directory.get(row_id)
        require(source is not None and source["title"] == title
                and source["context"] == f"TNG S1E{episode}"
                and source["medium"] == "EPISODE"
                and source["candidate_kind"] == "PUBLISHER_EPISODE_SLOT"
                and source["source_group"] == "publisher:paramount"
                and source["source_input"] ==
                "proposals/discovery/legacy-paramount-season1-20261102/tng/bundle.json"
                and source["source_locator"] == GUIDE
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["admission_effect"] == "NONE"
                and source["coverage_effect"] == "NONE", "source-local discovery row drift")
        records.append({
            "source_local_row_id": row_id,
            "source_local_title": title,
            "publisher_lineage": "paramount_corporate_publisher_family",
            "publisher_card": {"guide_url": GUIDE, "title": title, "season": 1,
                               "episode": episode, "publisher_description_sha256": description_digest,
                               "brief_description_actually_read": True,
                               "raw_webpage_sha256": None},
            "source_relative_entity_mentions": row["entity_mentions_source_relative"],
            "assertion_frame": "MENTIONS_IN_PUBLISHER_DESCRIPTION_NOT_EPISODE_TRUTH",
            "original_synopsis_draft": synopsis,
            "synopsis_publication_status": "PENDING_HUMAN_AND_EDITORIAL_REVIEW",
            "publisher_thumbnail_url_held": art,
            "artwork_asset_status": "URL_DISCOVERY_ONLY_NO_LICENSE_ADMISSION_OR_IMAGE_COPY",
            "prior_same_family_title_slot_recheck_id": overlap,
            "prior_overlap_effect": "ENRICHMENT_ONLY_NOT_NEW_TITLE_SLOT_RECHECK" if overlap else
                                    "NEW_SOURCE_LOCAL_TITLE_SLOT_RECHECK",
            "identity_resolution": "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
            "source_body_custody": "NOT_ARCHIVED_HTML_RETRIEVED_FOR_READ_ONLY_INSPECTION",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    require(len({r["source_local_row_id"] for r in records}) == 4,
            "duplicate new source-local row")
    return {
        "schema_version": "1.0.0",
        "data_status": "B012-TNG-S1-PUBLISHER_SOURCE_RECHECK_PROPOSAL_ONLY",
        "catalog_sha256": CATALOG_SHA,
        "observations_sha256": sha(json.dumps(observations, sort_keys=True,
                                              separators=(",", ":")).encode("utf-8")),
        "source_local_cards_enriched": 4,
        "new_title_slot_rechecks": 2,
        "same_publisher_prior_title_slot_overlaps": 2,
        "independent_corroborations": 0,
        "original_synopsis_drafts_held": 4,
        "publisher_artwork_url_leads_held": 4,
        "public_synopses_or_images_published": 0,
        "governed_research_admissions": 0,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "rows": records,
    }


def serialized(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, raw = load_json(CATALOG)
    observations, _ = load_json(OBSERVATIONS)
    b004, b004_raw = load_json(PRIOR_B004)
    b011_obs, b011_obs_raw = load_json(PRIOR_B011_OBS)
    b011_records, b011_records_raw = load_json(PRIOR_B011_RECORDS)
    computed = serialized(compile_records(catalog, raw, observations, b004, b004_raw,
                                          b011_obs, b011_obs_raw, b011_records, b011_records_raw))
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != computed:
            raise SystemExit("TNG B012 output stale or tampered; rebuild required")
        print("TNG B012 exact source-local card compilation: PASS")
    else:
        target.write_text(computed, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
