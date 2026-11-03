#!/usr/bin/env python3
"""Deterministic, held Enterprise S2 E1–E10 publisher cards; not episode evidence."""

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
OBS = Path("proposals/verification/ent-season2-publisher-b001-20261103/observations.json")
OUTPUT = Path("proposals/verification/ent-season2-publisher-b001-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/enterprise/episodes/2/"
BASE = "e5bfab953a9da961fd9d7ebc5d94b432ebca8fbc"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
BUNDLE_SHA = "b3ba6c175202d0bd55b711a850a939af6aee2786d0900bc1365cbd109086ef84"
S1_B001_OBS_SHA = "761f45a956f8fc409f2c3a80273c9e0d6ba479310ac536729760cef10716de4b"
S1_B001_RECORDS_SHA = "4a48f7136eebff4693fb516bdc3af9bd320af3f2670abfbd492e48816b4e9fc0"
S1_B002_OBS_SHA = "ce21bf57f9863915e612f46d9e81cc15139433b909a48b6e659c03add5a324b4"
S1_B002_RECORDS_SHA = "88996d6a16d52d6ea82faeccbc01cf97b924b8657d2f78139f2ec131d2e01ae0"

# Exact immutable publisher card: source-relative title, displayed E#, description SHA-256,
# literal description-name tokens, per-card publisher art lead, publisher claim-frame hold.
EXPECTED = (
    ("Shockwave Part II", 1, "002d314336f29209603e9dc4ff30820ff37ccc87bc9d393460aa1412b9d6970e",
     ("Archer", "Sulibans", "Enterprise", "Silik"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492637/CBS_ENTERPRISE_027_2784417_1920x1080.jpg",
     "PUBLISHER_PART_II_CONTINUATION_CLAIM_NO_WORK_IDENTITY_LINK"),
    ("Carbon Creek", 2, "8cd473070d262c6a33a51eec0ea7d83be938dd82a414b4daa415b33fa0e8b4de",
     ("TPol", "Vulcans", "Carbon Creek", "Archer", "Trip"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492074/CBS_ENTERPRISE_028_2784416_1920x1080.jpg",
     "PUBLISHER_REPORTS_CHARACTER_NARRATED_TALE_NOT_AUTHENTICATED_HISTORY"),
    ("Minefield", 3, "df06736f37dd8fafdff4f0a57d9f6cdb0c1f566e39ef5462ab261a3e87896c4c",
     ("Enterprise", "Reed", "Romulans", "Archer"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490418/CBS_ENTERPRISE_029_2784408_1920x1080.jpg",
     "PUBLISHER_PLOT_DESCRIPTION_NOT_AV_EPISODE_DEPICTION"),
    ("Dead Stop", 4, "5dd65d877019abd6af5d949684675f3db1e2bd5b49b1fba54787940fd3bbb563",
     ("Mayweather",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492039/CBS_ENTERPRISE_030_2784303_1920x1080.jpg",
     "PUBLISHER_APPARENT_DEATH_NOT_AUTHENTICATED_CHARACTER_DEATH"),
    ("A Night in Sickbay", 5, "35a16decfa3813aaa532b342574231ede51a5d4a0c162d924eb22aad0abdeedc",
     ("Archer", "Porthos", "Kreetassens", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490437/CBS_ENTERPRISE_031_2784400_1920x1080.jpg",
     "PUBLISHER_PLOT_DESCRIPTION_NOT_AV_EPISODE_DEPICTION"),
    ("Marauders", 6, "68b4109b374fde6c194d56b5f735113eb262d13e24ead999cfe1e30132aec648",
     ("Archer", "Klingons"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492021/CBS_ENTERPRISE_032_2784412_1920x1080.jpg",
     "PUBLISHER_PLOT_DESCRIPTION_NOT_AV_EPISODE_DEPICTION"),
    ("The Seventh", 7, "82b7e0de2e74e260739a0f7be35756c015c0d415938557a2b6af2d03c461422e",
     ("Vulcan", "TPol"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490516/CBS_ENTERPRISE_033_2784395_1920x1080.jpg",
     "PUBLISHER_REPORTS_TROUBLING_MEMORY_NOT_VERIFIED_HISTORY"),
    ("The Communicator", 8, "3ee8adb601775a30ee8992264c247ec06e2c17133c4fbc3017d7aa05076f122c",
     ("Reed", "Archer"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490767/CBS_ENTERPRISE_034_2784407_1920x1080.jpg",
     "PUBLISHER_REPORTS_SUSPECTED_SPIES_NOT_ESTABLISHED_SPIES"),
    ("Singularity", 9, "2e7ffc2fcfa631897fadd944ba1e6c90ed54370606f512d3fd8b1cccef3cf378",
     ("Enterprise",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41490214/CBS_ENTERPRISE_035_2784406_1920x1080.jpg",
     "PUBLISHER_BEHAVIOR_DESCRIPTION_NOT_MEDICAL_DIAGNOSIS"),
    ("Vanishing Point", 10, "c96a2ede0435119fc325677be0299ccfab345c9cdfc8f0825055f1c924fca703",
     ("Hoshi",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41488410/CBS_ENTERPRISE_036_2784410_1920x1080.jpg",
     "PUBLISHER_CHARACTER_IDENTITY_DOUBT_NOT_IDENTITY_CHANGE"),
)

TOP_KEYS = {"schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
            "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
            "audiovisual_episodes_watched", "public_synopsis_authorized",
            "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect",
            "accepted_ent_bundle_sha256", "accepted_s1_b001_observations_sha256",
            "accepted_s1_b001_records_sha256", "accepted_s1_b002_observations_sha256",
            "accepted_s1_b002_records_sha256", "rows"}
ROW_KEYS = {"row_id", "publisher_title", "season", "episode",
            "publisher_description_sha256", "original_synopsis_draft",
            "entity_mentions_source_relative", "mention_frame", "publisher_thumbnail_url",
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
    require(isinstance(observations, dict) and set(observations) == TOP_KEYS,
            "closed source observation schema")
    envelope = {
        "schema_version": "1.0.0",
        "proposal_id": "ENT-S2-B001-PUBLISHER-CARDS-20261103",
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
        title, episode, description_sha, mentions, picture, frame = expected
        local_id = f"legacy:s2:ent:{i:03d}"
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
        require(row["source_claim_frame"] == frame,
                "publisher narration/memory/death/identity frame altered")
        hold = ("PUBLISHER_SHOCKWAVE_PART_II_S1_PART_I_LINK_UNRESOLVED_NO_GLOBAL_WORK_IDENTITY"
                if i == 0 else "NO_GLOBAL_WORK_IDENTITY_ASSERTED")
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
            "artwork_asset_status": "URL_DISCOVERY_ONLY_NO_LICENSE_OR_IMAGE_COPY",
            "identity_resolution": hold,
            "source_body_custody": "NOT_ARCHIVED_HTML_EPHEMERALLY_RETRIEVED_FOR_READ_ONLY_INSPECTION",
            "governed_coverage_state": "NOT_ADMITTED",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "B001-ENT-S2-PUBLISHER_SOURCE_CARD_PROPOSAL_ONLY",
        "accepted_catalog_sha256": CATALOG_SHA,
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "accepted_s1_b001_observations_sha256": S1_B001_OBS_SHA,
        "accepted_s1_b001_records_sha256": S1_B001_RECORDS_SHA,
        "accepted_s1_b002_observations_sha256": S1_B002_OBS_SHA,
        "accepted_s1_b002_records_sha256": S1_B002_RECORDS_SHA,
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
    "390154439a04df3ce1534367aa9e0104ad474944875711196d1ccdeffad5378e",
    "497fa7bafe1beef7742c92b2610df0cfa80d24e60eeaea1bcfafc4710ffc39f1",
    "74e64aa1bba373b4970d30ad60136dc1bef0404efe2d04a26ba4816b5d8481d1",
    "9d61262e5e2ebb9f729e8082fb02fbb1a660a9b9a11a9975a39b58a623c88959",
    "3f31f6da532b575677c8b5d29c4a45c77b98d25b8597ea8a9926958a03944f2b",
    "7c414aa77629dc80c42b4288f7906f7ceec7d9d42a2a79c55287fbf9fa5d9f95",
    "7b316d0d364714c5871a0e118ed6d56d136bcf67d8012a914fdeb74f5abae367",
    "a9975c7e5b56b4eab27a26907aa36a150a273fb0764ff2728fb6af1a836f3190",
    "ad93c260c28c4cc097d4fc8f09eea749f44e4fd8483321c1855fa2f97d667b16",
    "43b07b4d68937e8ed801d29defcf68d13d48cf418694dbc899aadf2ce88579ca",
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
            raise SystemExit("ENT S2_B001 records stale or tampered")
        print("Enterprise S2_B001 source-local card compilation: PASS")
    else:
        target.write_text(output, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
