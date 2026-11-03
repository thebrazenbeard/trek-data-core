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
OBS = Path("proposals/verification/ent-season1-publisher-b002-20261103/observations.json")
OUTPUT = Path("proposals/verification/ent-season1-publisher-b002-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/enterprise/episodes/1/"
BASE = "7e0c56e5bbef70296de034e5283ed6217e6e7f91"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
BUNDLE_SHA = "79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486"

# Row-local immutable first-party metadata: title, visible slot, short-description
# SHA-256, literally present strings, and actual HTML card-bound thumbnail URL.
EXPECTED = (
    ("Silent Enemy", 12, "1917c28167155bd86c6ce90c832f2dcb0507920b4abb867b760377d6a951ec44",
     ("Trip", "Reed", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492981/CBS_ENTERPRISE_012_1215624_1920x1080.jpg"),
    ("Dear Doctor", 13, "bd6ea1f75ad3d5734f5352494ab79c1ec5119c65a71b95f3854c9cb2ad3e6632",
     ("Archer", "Dr. Phlox"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494761/CBS_ENTERPRISE_013_1215611_1920x1080.jpg"),
    ("Sleeping Dogs", 14, "aa035b480e42b6e4a76bb64f3a48c44861e43aa12230e65ad042006c74a0744d",
     ("Klingon", "T'Pol", "Reed", "Hoshi"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41493222/CBS_ENTERPRISE_014_2334941_1920x1080.jpg"),
    ("Shadows of P'Jem", 15, "19b79e1e94e076903d49e5fcd78290fdb6df33f87604faf4b1f49101aeea3e23",
     ("T'Pol", "Andorian", "P'Jem", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494166/CBS_ENTERPRISE_015_2334930_1920x1080.jpg"),
    ("Shuttlepod One", 16, "97adb720c497fda789697a9744bc43f0ea04dfd634f91f4c2479998ee4e85751",
     ("Enterprise", "Trip", "Reed", "Shuttlepod One"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41493328/CBS_ENTERPRISE_016_2334935_1920x1080.jpg"),
    ("Fusion", 17, "ac58be8b122d9a202051dd1e81c8bc2be94481d6cf164565fc0b75ff75fcf864",
     ("Vulcan", "T'Pol", "Mind meld", "Tolaris"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41493386/CBS_ENTERPRISE_017_1215626_1920x1080.jpg"),
    ("Rogue Planet", 18, "51177be62ac29ddaf7bd8f624039103de9d437e11d6d97eb547c58ebc610dbdb",
     ("Archer",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492791/CBS_ENTERPRISE_018_2334936_1920x1080.jpg"),
    ("Acquisition", 19, "abbb2e8187d38b09da2bc659d5849ebf63dc607b70c4a135a718debf4db1c21b",
     ("Enterprise", "Ferengi"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494011/CBS_ENTERPRISE_019_2334940_1920x1080.jpg"),
    ("Oasis", 20, "13d7dc8cb038c2992592e8ce85b120f9b75b1ba05668bf2f893a50e03941e30b",
     ("Trip",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41493516/CBS_ENTERPRISE_020_2334937_1920x1080.jpg"),
    ("Detained", 21, "6515cead2fc3c988841f11c23c2955ba2e949295c8f6a35b42db2dbd65f6baa9",
     ("Archer", "Mayweather", "Tandarans", "Suliban"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41491462/CBS_ENTERPRISE_021_2334938_1920x1080.jpg"),
)

TOP_KEYS = {"schema_version", "proposal_id", "baseline_accepted_main", "observed_utc_date",
            "source_family", "guide_url", "read_surface", "raw_html_bytes_archived",
            "audiovisual_episodes_watched", "public_synopsis_authorized",
            "artwork_copy_or_publication_authorized", "admission_effect", "coverage_effect",
            "accepted_ent_bundle_sha256", "rows"}
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


def compile_records(catalog, catalog_raw, bundle, bundle_raw, observations):
    require(digest(catalog_raw) == CATALOG_SHA and catalog.get("row_count") == 1214
            and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "accepted discovery drift")
    require(digest(bundle_raw) == BUNDLE_SHA, "accepted Enterprise S1 seed changed")
    require(isinstance(observations, dict) and set(observations) == TOP_KEYS,
            "closed source observation schema")
    envelope = {
        "schema_version": "1.0.0",
        "proposal_id": "ENT-S1-B002-PUBLISHER-CARDS-20261103",
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
    }
    for k, expected in envelope.items():
        require(type(observations[k]) is type(expected) and observations[k] == expected,
                f"forged or changed envelope: {k}")
    require(isinstance(observations["rows"], list) and len(observations["rows"]) == 10,
            "exactly ten source cards")
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
        local_id = f"legacy:s1:ent:{i + 10:03d}"
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
        hold = "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
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
        "data_status": "B002-ENT-S1-PUBLISHER_SOURCE_CARD_PROPOSAL_ONLY",
        "accepted_catalog_sha256": CATALOG_SHA,
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "observations_sha256": digest(json.dumps(observations, sort_keys=True,
                                                 separators=(",", ":")).encode()),
        "source_local_cards_enriched": 10,
        "new_source_local_title_slot_rechecks": 10,
        "combined_multipart_cards_preserved_as_single_source_slot": 0,
        "invented_separate_s1e2_source_cards": 0,
        "independent_corroborations": 0,
        "original_synopsis_drafts_held": 10,
        "publisher_artwork_url_leads_held": 10,
        "public_synopses_or_images_published": 0,
        "governed_research_admissions": 0,
        "admission_effect": "NONE", "coverage_effect": "NONE",
        "rows": records,
    }


SYNOPSIS_DIGESTS = (  # Frozen after author inspection of each exact publisher card.
    "052f4e009f6a111c8b791ea8e6e4be85778834547064a0eb9a755cc4c2827c98",
    "c49ef55c6ad7ef64e676733c5516d31446ef88ed17853992aefe4f0afb57140e",
    "dfeb10f75621f51aae46cb0353405f3948d4689cfefc1f5fb64e79064ec755a5",
    "3c46f60cf978f004a211fa4c7373cbb840081440b1c76118c0be551a9452fc79",
    "dc9b9c68b41f5dcbc54b265b6ae026c11d8835d505dfda79445baf4a0afc3fca",
    "ee6edb4d41d1d00f98897e8e071dda207efd548fbb15b2915dffab60aa7eb5e7",
    "d5b4f236f164ada0de34c4fbd25102e602320c164286968d92a7564590e34f94",
    "41606329e145698b98ed9ccac8770c4acda958856c08cbed977641b92973176c",
    "9cae1e48a8d66491c2c56d67ac8e8792911213ba0ff999a2f82cc56603626ffd",
    "8d77daab0062bf305640e10862736695f9469b9fa30af5ef4c275f98246d59aa",
)


def serialized(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, catalog_raw = load_json(CATALOG)
    bundle, bundle_raw = load_json(BUNDLE)
    observations, _ = load_json(OBS)
    output = serialized(compile_records(catalog, catalog_raw, bundle, bundle_raw, observations))
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != output:
            raise SystemExit("ENT B002 records stale or tampered")
        print("Enterprise B002 source-local card compilation: PASS")
    else:
        target.write_text(output, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
