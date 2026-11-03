#!/usr/bin/env python3
"""Deterministic, held Enterprise S1 publisher-card observations; never episode evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
BUNDLE = Path("proposals/discovery/legacy-paramount-season1-20261102/ent/bundle.json")
ACCEPTED_B001_OBS = Path("proposals/verification/ent-season1-publisher-b001-20261103/observations.json")
ACCEPTED_B001_RECORDS = Path("proposals/verification/ent-season1-publisher-b001-20261103/records.json")
OBS = Path("proposals/verification/ent-season1-publisher-b003-20261103/observations.json")
OUTPUT = Path("proposals/verification/ent-season1-publisher-b003-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/enterprise/episodes/1/"
BASE = "90aee8750c87afb8f64fa5d687e76db6e3f1c7aa"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
BUNDLE_SHA = "79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486"
B001_OBS_SHA = "761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b"
B001_RECORDS_SHA = "4a48f7136eebff4693fb516bdc3af9bd320af3f2670abfbd492e48816b4e9fc0"

# Row-local immutable first-party metadata: title, visible slot, short-description
# SHA-256, literally present strings, and actual HTML card-bound thumbnail URL.
EXPECTED = (
    ("Vox Solis", 22, "2d852de739f4456dd61a97c6ae8b9e4e906befa84e26ce741c78e78663f81bc7",
     ("Enterprise", "Archer", "Trip"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494034/CBS_ENTERPRISE_022_2334946_1920x1080.jpg"),
    ("Fallen Hero", 23, "7c6ed446c4bbc43ee64e810f9a3369f8d41c6beddfb9972c6986e96fcc169af8",
     ("Archer", "Vulcan Ambassador", "Mazar"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490312/CBS_ENTERPRISE_023_2334932_1920x1080.jpg"),
    ("Desert Crossing", 24, "c93d685449523fd6694fda78c1242911ebf39186b016480784e654496ce92108",
     ("Archer", "Trip"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41491718/CBS_ENTERPRISE_024_2334944_1920x1080.jpg"),
    ("Two Days and Two Nights", 25, "d163d8bb818f49601aa3731b3d934798dd1c09a241ad62a630c5cb8a65eb35f0",
     ("Risa", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492009/CBS_ENTERPRISE_025_2334934_1920x1080.jpg"),
    ("Shockwave Part I", 26, "0ebf1f9165493f5a9509a8d023ae234338fcea393520f24edc931f71eaf28366",
     ("Captain Archer", "Sulibans"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41491506/CBS_ENTERPRISE_026_2334943_1920x1080.jpg"),
)

TOP_KEYS = {"schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
            "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
            "audiovisual_episodes_watched", "public_synopsis_authorized",
            "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect",
            "accepted_ent_bundle_sha256", "accepted_b001_observations_sha256",
            "accepted_b001_records_sha256", "rows"}
ROW_KEYS = {"row_id", "publisher_title", "season", "episode",
            "publisher_description_sha256", "original_synopsis_draft",
            "entity_mentions_source_relative", "mention_frame", "publisher_thumbnail_url",
            "identity_hold"}


def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError(f"duplicate JSON key: {k}")
        result[k] = v
    return result


def load_json(path):
    item = (ROOT / path) if not Path(path).is_absolute() else Path(path)
    if item.is_symlink() or not item.is_file() or item.stat().st_size > 4_000_000:
        raise ValueError(f"missing, symlinked, or oversized input: {path}")
    raw = item.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs), raw


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compile_records(catalog, catalog_raw, bundle, bundle_raw, b001_obs,
                    b001_obs_raw, b001_records, b001_records_raw, observations):
    require(digest(catalog_raw) == CATALOG_SHA and catalog.get("row_count") == 1214
            and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "accepted discovery drift")
    require(digest(bundle_raw) == BUNDLE_SHA, "accepted Enterprise S1 seed changed")
    require(digest(b001_obs_raw) == B001_OBS_SHA
            and digest(b001_records_raw) == B001_RECORDS_SHA
            and b001_obs.get("coverage_effect") == "NONE"
            and b001_obs.get("admission_effect") == "NONE"
            and b001_records.get("governed_research_admissions") == 0,
            "accepted Enterprise B001 source-only snapshot drift")
    prior_ids = {r["row_id"] for r in b001_obs["rows"]}
    require(prior_ids == {f"legacy:s1:ent:{i:03d}" for i in range(10)},
            "accepted B001 source-local frontier changed")
    require(isinstance(observations, dict) and set(observations) == TOP_KEYS,
            "closed source observation schema")
    envelope = {
        "schema_version": "1.0.0",
        "proposal_id": "ENT-S1-B003-PUBLISHER-CARDS-20261103",
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
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "accepted_b001_observations_sha256": B001_OBS_SHA,
        "accepted_b001_records_sha256": B001_RECORDS_SHA,
    }
    for k, expected in envelope.items():
        require(type(observations[k]) is type(expected) and observations[k] == expected,
                f"forged or changed envelope: {k}")
    require(isinstance(observations["rows"], list) and len(observations["rows"]) == 5,
            "exactly five source cards")
    rows_by_id = {r["row_id"]: r for r in catalog["rows"]}
    require(len(rows_by_id) == 1214, "duplicate discovery source ID")
    require(isinstance(bundle.get("episode_slots"), list)
            and len(bundle["episode_slots"]) == 25
            and bundle.get("coverage_effect") == "NONE",
            "Enterprise S1 discovery seed unexpectedly changed")
    source_ids = set()
    records = []
    for i, (row, expected) in enumerate(zip(observations["rows"], EXPECTED)):
        title, episode, description_sha, mentions, picture = expected
        local_id = f"legacy:s1:ent:{i + 20:03d}"
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "closed source-card fields")
        require(row["row_id"] == local_id and local_id not in source_ids,
                "duplicate/misplaced local source ID")
        source_ids.add(local_id)
        require(row["publisher_title"] == title and type(row["season"]) is int
                and row["season"] == 1 and type(row["episode"]) is int
                and row["episode"] == episode
                and row["publisher_description_sha256"] == description_sha,
                "publisher title/slot/description binding changed")
        require(isinstance(row["original_synopsis_draft"], str)
                and 60 <= len(row["original_synopsis_draft"]) <= 240
                and digest(row["original_synopsis_draft"].encode()) == SYNOPSIS_DIGESTS[i],
                "unreviewed original held synopsis edit")
        require(isinstance(row["entity_mentions_source_relative"], list)
                and tuple(row["entity_mentions_source_relative"]) == mentions
                and row["mention_frame"] == "LITERAL_PUBLISHER_DESCRIPTION_TEXT_ONLY_NOT_UTTERANCE_OR_DEPICTION",
                "unsupported publisher mention or semantic promotion")
        image = row["publisher_thumbnail_url"]
        u = urlsplit(image) if isinstance(image, str) else None
        require(u is not None and u.scheme == "https"
                and u.hostname == "thumbnails.cbsig.net"
                and re.fullmatch(r"/_x/w400/CBS_Production_Entertainment_VMS/[\w/.-]+\.jpg", u.path)
                and not u.query and not u.fragment and image == picture,
                "unbound thumbnail or wrong-card same-host artwork")
        hold = (
            "PUBLISHER_TITLE_VOX_SOLIS_ALTERNATE_TITLE_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY"
            if i == 0 else
            "PUBLISHER_PART_I_CROSS_SEASON_CONTINUATION_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY"
            if i == 4 else "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
        )
        require(row["identity_hold"] == hold, "multipart/Work identity hold changed")
        original = rows_by_id.get(local_id)
        require(original is not None and original["title"] == title
                and original["context"] == f"ENT S1E{episode}"
                and original["medium"] == "EPISODE"
                and original["candidate_kind"] == "PUBLISHER_EPISODE_SLOT"
                and original["source_group"] == "publisher:paramount"
                and original["source_input"] == str(BUNDLE)
                and original["source_locator"] == GUIDE
                and original["verification_status"] == "UNVERIFIED_METADATA"
                and original["admission_effect"] == "NONE"
                and original["coverage_effect"] == "NONE",
                "discovery candidate source lineage/title/slot drift")
        records.append({
            "source_local_row_id": local_id,
            "source_local_title": title,
            "publisher_lineage": "paramount_corporate_publisher_family",
            "publisher_card": {"guide_url": GUIDE, "title": title, "season": 1,
                               "episode": episode, "publisher_description_sha256": description_sha,
                               "brief_description_actually_read": True,
                               "raw_webpage_sha256": None},
            "source_relative_entity_mentions": list(mentions),
            "assertion_frame": row["mention_frame"],
            "original_synopsis_draft": row["original_synopsis_draft"],
            "synopsis_publication_status": "HELD_PENDING_HUMAN_EDITORIAL_REVIEW",
            "publisher_thumbnail_url_held": picture,
            "artwork_asset_status": "URL_DISCOVERY_ONLY_NO_LICENSE_OR_IMAGE_COPY",
            "identity_resolution": hold,
            "source_body_custody": "NOT_ARCHIVED_HTML_EPHEMERALLY_RETRIEVED_FOR_READ_ONLY_INSPECTION",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "B003-ENT-S1-PUBLISHER_SOURCE_CARD_PROPOSAL_ONLY",
        "accepted_catalog_sha256": CATALOG_SHA,
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "observations_sha256": digest(json.dumps(observations, sort_keys=True,
                                                 separators=(",", ":")).encode()),
        "source_local_cards_enriched": 5,
        "new_source_local_title_slot_rechecks": 5,
        "combined_multipart_cards_preserved_as_single_source_slot": 0,
        "unresolved_publisher_title_variants": 1,
        "unresolved_part_i_continuation_links": 1,
        "independent_corroborations": 0,
        "original_synopsis_drafts_held": 5,
        "publisher_artwork_url_leads_held": 5,
        "public_synopses_or_images_published": 0,
        "governed_research_admissions": 0,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "rows": records,
    }


SYNOPSIS_DIGESTS = (  # Frozen after source-relative publisher-card inspection.
    "818607bd1bf77f7c694835dc13ed3f3a8ce1962c35cd269db5ce09280cb00c74",
    "aada5b6643b7135446d0245ce5ee77f4be0f81f8449c24b20d66edcaa8e35235",
    "c8e846ad00eed87ade1721cb0a6258402676022789798053d0b07f0c337e97a2",
    "9220ee6bbb2a7b9e731d10247bc0b03219b47fed454edc2f14c6995595b9c49c",
    "b81a5e70d5117a858efbe3dcf8a2667bc2e87b0b75d3760abc1bd33946af6dd3",
)


def serialized(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, catalog_raw = load_json(CATALOG)
    bundle, bundle_raw = load_json(BUNDLE)
    b001_obs, b001_obs_raw = load_json(ACCEPTED_B001_OBS)
    b001_records, b001_records_raw = load_json(ACCEPTED_B001_RECORDS)
    observations, _ = load_json(OBS)
    output = serialized(compile_records(catalog, catalog_raw, bundle, bundle_raw,
                                        b001_obs, b001_obs_raw,
                                        b001_records, b001_records_raw, observations))
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != output:
            raise SystemExit("ENT B003 records stale or tampered")
        print("Enterprise B003 source-local card compilation: PASS")
    else:
        target.write_text(output, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
