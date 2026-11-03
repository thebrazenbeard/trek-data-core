#!/usr/bin/env python3
"""Deterministic, held Enterprise S2 E11–E20 publisher cards; not episode evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("explorer/discovery-catalog.json")
BUNDLE = Path("proposals/discovery/legacy-paramount-season2-20261102/ent/bundle.json")
ACCEPTED_S1_B001_OBS = Path("proposals/verification/ent-season1-publisher-b001-20261103/observations.json")
ACCEPTED_S1_B001_RECORDS = Path("proposals/verification/ent-season1-publisher-b001-20261103/records.json")
ACCEPTED_S1_B002_OBS = Path("proposals/verification/ent-season1-publisher-b002-20261103/observations.json")
ACCEPTED_S1_B002_RECORDS = Path("proposals/verification/ent-season1-publisher-b002-20261103/records.json")
OBS = Path("proposals/verification/ent-season2-publisher-b002-20261103/observations.json")
OUTPUT = Path("proposals/verification/ent-season2-publisher-b002-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/enterprise/episodes/2/"
BASE = "8744c1dd234fa1e3ad3eb34951399b34f5fe9c6f"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
BUNDLE_SHA = "b3ba6c175202d0bd55b711a850a939af6aee2786d0900bc1365cbd109086ef84"
S1_B001_OBS_SHA = "761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b"
S1_B001_RECORDS_SHA = "4a48f7136eebff4693fb516bdc3af9bd320af3f2670abfbd492e48816b4e9fc0"
S1_B002_OBS_SHA = "ce21bf57f9863915e612f46d9e81cc15139433b909a48b6e659c03add5a324b4"
S1_B002_RECORDS_SHA = "88996d6a16d52d6ea82faeccbc01cf97b924b8657d2f78139f2ec131d2e01ae0"
ACCEPTED_S2_B001_OBS = Path("proposals/verification/ent-season2-publisher-b001-20261103/observations.json")
ACCEPTED_S2_B001_RECORDS = Path("proposals/verification/ent-season2-publisher-b001-20261103/records.json")
S2_B001_OBS_SHA = "547eae257037f2888ccd9eaee50795eed494d9ef02cfcda5ca0d0645a79458af"
S2_B001_RECORDS_SHA = "d71c0e01c6e60c60222b3fd39dd9c21943f581d9816b4063d96b1b26ae897a9d"


# Exact immutable publisher card: source-relative title, displayed E#, description SHA-256,
# literal description-name tokens, per-card publisher art lead, publisher claim-frame hold.
EXPECTED = (
    ("Precious Cargo", 11, "b7206134bd508b0ffa9691c38280dcc7544fb15206a1d8ff8c57b1bcd6be1b70",
     ("Trip",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490133/CBS_ENTERPRISE_037_2784415_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475199129/",
     "PUBLISHER_RESCUE_AND_ROMANCE_DESCRIPTION_NOT_AV_DEPICTION"),
    ("The Catwalk", 12, "ef545ed58147cfa3c6c70762930100aef938712cc306e149e590f83a27652668",
     ("Enterprise",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41489653/CBS_ENTERPRISE_038_2784399_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475205305/",
     "PUBLISHER_EIGHT_DAY_SHELTER_CLAIM_NOT_AV_DEPICTION"),
    ("Dawn", 13, "37e271ac937a2376361ed0a8eec3ab9a3110964079adf0ed6f48b9e384e9de29",
     ("Trip",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41489420/CBS_ENTERPRISE_039_2784306_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475207106/",
     "PUBLISHER_TERRITORIAL_ATTACK_NOT_AV_VERIFIED"),
    ("Stigma", 14, "b710b055e12b193a1d6edfe4a24bf765617d947d44dc88c8a8066fdb27ffd39b",
     ("T'Pol", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490246/CBS_ENTERPRISE_040_2784402_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475208813/",
     "PUBLISHER_DISEASE_DIAGNOSIS_NOT_MEDICAL_OR_AV_VERIFIED"),
    ("Cease Fire", 15, "dbb61e31f7795309719f12034794fa61f9058ba19fed10538596112a7a6d28bd",
     ("Vulcans", "Andorians", "Archer"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490030/CBS_ENTERPRISE_041_2784403_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475308641/",
     "PUBLISHER_NEGOTIATOR_ROLE_NOT_AV_VERIFIED"),
    ("Future Tense", 16, "2dfc93f038711c1c38d73664dba2508f654460f3b2b078d7a0522cd83f487715",
     ("Enterprise", "Suliban", "Tholians"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41489534/CBS_ENTERPRISE_042_2784404_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475314335/",
     "PUBLISHER_APPARENT_CORPSE_NOT_AUTHENTICATED_DEATH"),
    ("Canamar", 17, "67e33c3ed9262014761cbdb762bcb07d6b90751b5d95fad246d78daae02937c8",
     ("Archer", "Tucker", "Canamar"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41488662/CBS_ENTERPRISE_043_2784405_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475317514/",
     "PUBLISHER_MISTAKEN_ARREST_NOT_GUILT"),
    ("The Crossing", 18, "6932145a418e7fbdddeb05d747adea0bff2f637a73b4098885c48d91e738f459",
     ("Enterprise",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490570/CBS_ENTERPRISE_044_2784418_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475321661/",
     "PUBLISHER_CONSCIOUSNESS_TRADE_CLAIM_NOT_IDENTITY_TRANSFER_PROOF"),
    ("Judgement", 19, "39151362a85745b857fe721da865667f30250ee5983fd0f9e14783c57985bdea",
     ("Archer", "Klingon", "Empire", "Rura Penthe"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41489315/CBS_ENTERPRISE_045_2784411_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475322357/",
     "PUBLISHER_CHARGE_NOT_ESTABLISHED_CONSPIRACY"),
    ("Horizon", 20, "e09ac73fd3a9de71954df2276a7c37cfedd485b14c7ae2f3fd3607bbbf238508",
     ("Enterprise", "Mayweather"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41488681/CBS_ENTERPRISE_046_2784409_1920x1080.jpg",
     "https://www.paramountplus.com/shows/video/1475325435/",
     "PUBLISHER_BIOGRAPHICAL_REPORT_NOT_AV_VERIFIED"),
)

TOP_KEYS = {"schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
            "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
            "audiovisual_episodes_watched", "public_synopsis_authorized",
            "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect",
            "accepted_ent_bundle_sha256", "accepted_s1_b001_observations_sha256",
            "accepted_s1_b001_records_sha256", "accepted_s1_b002_observations_sha256",
            "accepted_s1_b002_records_sha256", "accepted_s2_b001_observations_sha256",
            "accepted_s2_b001_records_sha256", "rows"}
ROW_KEYS = {"row_id", "publisher_title", "season", "episode",
            "publisher_description_sha256", "original_synopsis_draft",
            "entity_mentions_source_relative", "mention_frame", "publisher_thumbnail_url",
            "publisher_video_url",
            "identity_hold", "source_claim_frame"}


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


def compile_records(catalog, catalog_raw, bundle, bundle_raw, s1_b001_obs,
                    s1_b001_obs_raw, s1_b001_records, s1_b001_records_raw,
                    s1_b002_obs, s1_b002_obs_raw, s1_b002_records, s1_b002_records_raw,
                    observations):
    require(digest(catalog_raw) == CATALOG_SHA and catalog.get("row_count") == 1214
            and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "accepted discovery drift")
    require(digest(bundle_raw) == BUNDLE_SHA, "accepted Enterprise S2 discovery seed changed")
    require(digest(s1_b001_obs_raw) == S1_B001_OBS_SHA
            and digest(s1_b001_records_raw) == S1_B001_RECORDS_SHA
            and digest(s1_b002_obs_raw) == S1_B002_OBS_SHA
            and digest(s1_b002_records_raw) == S1_B002_RECORDS_SHA
            and s1_b001_obs.get("admission_effect") == "NONE"
            and s1_b002_obs.get("admission_effect") == "NONE"
            and s1_b001_records.get("governed_research_admissions") == 0
            and s1_b002_records.get("governed_research_admissions") == 0,
            "accepted Enterprise Season 1 research pin/source-only drift")
    require({r["row_id"] for r in s1_b001_obs["rows"]} ==
            {f"legacy:s1:ent:{i:03d}" for i in range(10)}
            and {r["row_id"] for r in s1_b002_obs["rows"]} ==
            {f"legacy:s1:ent:{i:03d}" for i in range(10, 20)},
            "previous accepted Season 1 source-local frontier drift")
    s2_b001_obs, s2_b001_obs_raw = load_json(ACCEPTED_S2_B001_OBS)
    s2_b001_records, s2_b001_records_raw = load_json(ACCEPTED_S2_B001_RECORDS)
    require(digest(s2_b001_obs_raw) == S2_B001_OBS_SHA
            and digest(s2_b001_records_raw) == S2_B001_RECORDS_SHA
            and s2_b001_obs["admission_effect"] == "NONE"
            and s2_b001_obs["coverage_effect"] == "NONE"
            and s2_b001_records["governed_research_admissions"] == 0
            and {r["row_id"] for r in s2_b001_obs["rows"]} ==
                {f"legacy:s2:ent:{i:03d}" for i in range(10)},
            "accepted S2 B001 source-local predecessor drift or collision")
    require(isinstance(observations, dict) and set(observations) == TOP_KEYS,
            "closed source observation schema")
    envelope = {
        "schema_version": "1.0.0",
        "proposal_id": "ENT-S2-B002-PUBLISHER-CARDS-20261103",
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
        "accepted_s1_b001_observations_sha256": S1_B001_OBS_SHA,
        "accepted_s1_b001_records_sha256": S1_B001_RECORDS_SHA,
        "accepted_s1_b002_observations_sha256": S1_B002_OBS_SHA,
        "accepted_s1_b002_records_sha256": S1_B002_RECORDS_SHA,
        "accepted_s2_b001_observations_sha256": S2_B001_OBS_SHA,
        "accepted_s2_b001_records_sha256": S2_B001_RECORDS_SHA,
    }
    for k, expected in envelope.items():
        require(type(observations[k]) is type(expected) and observations[k] == expected,
                f"forged or changed envelope: {k}")
    require(isinstance(observations["rows"], list) and len(observations["rows"]) == 10,
            "exactly ten source cards")
    rows_by_id = {r["row_id"]: r for r in catalog["rows"]}
    require(len(rows_by_id) == 1214, "duplicate discovery source ID")
    require(isinstance(bundle.get("episode_slots"), list)
            and len(bundle["episode_slots"]) == 26
            and bundle.get("coverage_effect") == "NONE",
            "Enterprise S2 discovery seed unexpectedly changed")
    source_ids = set()
    records = []
    for i, (row, expected) in enumerate(zip(observations["rows"], EXPECTED)):
        title, episode, description_sha, mentions, picture, video_url, frame = expected
        local_id = f"legacy:s2:ent:{i + 10:03d}"
        require(isinstance(row, dict) and set(row) == ROW_KEYS, "closed source-card fields")
        require(row["row_id"] == local_id and local_id not in source_ids,
                "duplicate/misplaced local source ID")
        source_ids.add(local_id)
        require(row["publisher_title"] == title and type(row["season"]) is int
                and row["season"] == 2 and type(row["episode"]) is int
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
        video = row["publisher_video_url"]
        v = urlsplit(video) if isinstance(video, str) else None
        require(v is not None and v.scheme == "https"
                and v.hostname == "www.paramountplus.com"
                and re.fullmatch(r"/shows/video/\d+/", v.path)
                and not v.query and not v.fragment and video == video_url,
                "unbound or cross-card publisher video locator")
        require(row["source_claim_frame"] == frame,
                "publisher narration/memory/death/identity frame altered")
        hold = "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
        require(row["identity_hold"] == hold, "multipart/Work identity hold changed")
        original = rows_by_id.get(local_id)
        require(original is not None and original["title"] == title
                and original["context"] == f"ENT S2E{episode}"
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
            "publisher_card": {"guide_url": GUIDE, "title": title, "season": 2,
                               "episode": episode, "publisher_description_sha256": description_sha,
                               "brief_description_actually_read": True,
                               "raw_webpage_sha256": None},
            "source_relative_entity_mentions": list(mentions),
            "assertion_frame": row["mention_frame"],
            "publisher_description_claim_frame": frame,
            "original_synopsis_draft": row["original_synopsis_draft"],
            "synopsis_publication_status": "HELD_PENDING_HUMAN_EDITORIAL_REVIEW",
            "publisher_thumbnail_url_held": picture,
            "publisher_video_url_held": video_url,
            "publisher_video_status": "DISCOVERY_URL_ONLY_NOT_PLAYED",
            "artwork_asset_status": "URL_DISCOVERY_ONLY_NO_LICENSE_OR_IMAGE_COPY",
            "identity_resolution": hold,
            "source_body_custody": "NOT_ARCHIVED_HTML_EPHEMERALLY_RETRIEVED_FOR_READ_ONLY_INSPECTION",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "B002-ENT-S2-PUBLISHER_SOURCE_CARD_PROPOSAL_ONLY",
        "accepted_catalog_sha256": CATALOG_SHA,
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "accepted_s1_b001_observations_sha256": S1_B001_OBS_SHA,
        "accepted_s1_b001_records_sha256": S1_B001_RECORDS_SHA,
        "accepted_s1_b002_observations_sha256": S1_B002_OBS_SHA,
        "accepted_s1_b002_records_sha256": S1_B002_RECORDS_SHA,
        "accepted_s2_b001_observations_sha256": S2_B001_OBS_SHA,
        "accepted_s2_b001_records_sha256": S2_B001_RECORDS_SHA,
        "observations_sha256": digest(json.dumps(observations, sort_keys=True,
                                                 separators=(",", ":")).encode()),
        "source_local_cards_enriched": 10,
        "new_source_local_title_slot_rechecks": 10,
        "combined_multipart_cards_preserved_as_single_source_slot": 0,
        "cross_season_shockwave_work_links_resolved": 0,
        "publisher_narrated_tales_treated_as_historical_truth": 0,
        "publisher_apparent_deaths_treated_as_confirmed_deaths": 0,
        "identity_doubts_promoted_to_identity_changes": 0,
        "independent_corroborations": 0,
        "original_synopsis_drafts_held": 10,
        "publisher_artwork_url_leads_held": 10,
        "public_synopses_or_images_published": 0,
        "governed_research_admissions": 0,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "rows": records,
    }


SYNOPSIS_DIGESTS = (  # Frozen after source-relative publisher-card inspection.
    "77da3a38b6c6b7c62061913b1fddf5e96537d5e14bac61adbcfd012f747afffe",
    "4d5b50c92d51c2f47cb9698a9635f0f1063b49867b8b6d364fc2eda3e6f044e4",
    "88d6b7574369b9bd920c4358bd5cd1f1d91cb058f9e40813b5c25f95ec458fac",
    "03600276b702bbc1a865c72a4441ad32c349a40268d8ff4ba5b9c0aaa0961acb",
    "b54808103390a5e8a560a9d5acc50f9497b92f37f7e47617274662ad9779da09",
    "205cf00b72222c5524771322af2860e9391ff5c712e1e6de8e4f0bbc711a04df",
    "dcc6e5fe4c2a3971de33a5805e18b6941b9faf2842bd80034e93920f7f77eafd",
    "a8600b47b91a744df704c406f7fd3dbe5a6b7eef983f7b3296e545e1f9d9ef23",
    "6bb4eb067633009df86a9399d1023480532019d6656725f13bd37d6f52ec4a9d",
    "9dc572a0584a9af878d783d5bc9e870c81a032ac6a9cbdc10c8c9c9a657800ad",
)


def serialized(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, catalog_raw = load_json(CATALOG)
    bundle, bundle_raw = load_json(BUNDLE)
    s1_b001_obs, s1_b001_obs_raw = load_json(ACCEPTED_S1_B001_OBS)
    s1_b001_records, s1_b001_records_raw = load_json(ACCEPTED_S1_B001_RECORDS)
    s1_b002_obs, s1_b002_obs_raw = load_json(ACCEPTED_S1_B002_OBS)
    s1_b002_records, s1_b002_records_raw = load_json(ACCEPTED_S1_B002_RECORDS)
    observations, _ = load_json(OBS)
    output = serialized(compile_records(
        catalog, catalog_raw, bundle, bundle_raw,
        s1_b001_obs, s1_b001_obs_raw, s1_b001_records, s1_b001_records_raw,
        s1_b002_obs, s1_b002_obs_raw, s1_b002_records, s1_b002_records_raw,
        observations))
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != output:
            raise SystemExit("ENT S2_B002 records stale or tampered")
        print("Enterprise S2_B002 source-local card compilation: PASS")
    else:
        target.write_text(output, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
