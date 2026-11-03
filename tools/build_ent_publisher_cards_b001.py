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
OBS = Path("proposals/verification/ent-season1-publisher-b001-20261103/observations.json")
OUTPUT = Path("proposals/verification/ent-season1-publisher-b001-20261103/records.json")
GUIDE = "https://www.paramountplus.com/shows/enterprise/episodes/1/"
BASE = "91d1af747d728345fa86fdfbb5ab7228327516af"
CATALOG_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
BUNDLE_SHA = "79a1347c46e73fc74120353c43a819d891b1406e4ea91fa5d20793ba7040c486"

# Row-local immutable first-party metadata: title, visible slot, short-description
# SHA-256, literally present strings, and actual HTML card-bound thumbnail URL.
EXPECTED = (
    ("Broken Bow - Part 1 and 2", 1, "f9cdbebc04c72787fb2d4fbd27a18b7328f560a67e48f95360c0842a439bcd04",
     ("Enterprise", "Humans", "Vulcans", "Klingon", "Kronos"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2026/02/25/vDnTX2qyJMb41JRFGjBNY2SmJKplW9uD/PPUSA_STARTREKENTERPRISE_999_V1_4533271_1920x1080.jpg"),
    ("Fight or Flight", 3, "13e04b4fee6e130a6e24d101a6f6867ea7f718bbdf1d971db04f66ee3e7ef113",
     ("Archer", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492899/CBS_ENTERPRISE_003_1227935_1920x1080.jpg"),
    ("Strange New World", 4, "cacf492e4be677014615a61dbbd655e64112ba3b2372a20129ab04587f2ff101",
     ("Enterprise",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41493446/CBS_ENTERPRISE_004_1215607_1920x1080.jpg"),
    ("Unexpected", 5, "21e7fe97c79abfb50c4e6f7d08214ab1b480d559f2c7b0280eab38ca88c5f8ea",
     ("Trip", "Enterprise"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492815/CBS_ENTERPRISE_005_2334931_1920x1080.jpg"),
    ("Terra Nova", 6, "2ee93b94196b39c376dc5d6259bbb34dd76cf2947833837b5205af30c8448832",
     ("Terra Nova", "Archer", "Enterprise", "Novans"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492880/CBS_ENTERPRISE_006_2334933_1920x1080.jpg"),
    ("The Andorian Incident", 7, "47a33689e71c6d2731fb372f361ab57ecbf9d939e2667612f9fa2395395154c9",
     ("Archer", "Trip", "T'Pol", "Andorians", "Vulcan", "P'Jem"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494108/CBS_ENTERPRISE_007_2334945_1920x1080.jpg"),
    ("Breaking The Ice", 8, "fb39c49887911f71d0330a8698471d581dc7cbb79994534c66418a4f2212d7bb",
     ("Archer", "Vulcan Captain", "Reed", "Mayweather"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494782/CBS_ENTERPRISE_008_1215609_1920x1080.jpg"),
    ("Civilization", 9, "ccecba82a8c9f48edbfd4da5879adfce686004ed9fa8c8d85a3278ae976594c2",
     ("Archer",),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2026/02/25/1477082216/PPUSA_STARTREKENTERPRISE_109_V1_4332577_1920x1080.jpg"),
    ("Fortunate Son", 10, "f39515ee8ac269663b4204e26092288e508c1c96a3a2ca45ea933ca6f5f68799",
     ("Earth", "Fortunate", "Enterprise", "Mayweather"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41494246/CBS_ENTERPRISE_010_1215623_1920x1080.jpg"),
    ("Cold Front", 11, "c43e5f662a35b918b73f81ac8c86af886807886721953f83b14976cbe785ea30",
     ("Enterprise", "Archer", "Suliban", "Silik"),
     "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2012/09/12/41492805/CBS_ENTERPRISE_011_2334942_1920x1080.jpg"),
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
        "proposal_id": "ENT-S1-B001-PUBLISHER-CARDS-20261103",
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
        local_id = f"legacy:s1:ent:{i:03d}"
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
        hold = "COMBINED_BROKEN_BOW_CARD_S1E1_WITH_NO_DISPLAYED_E2_CARD_NO_GLOBAL_WORK_IDENTITY" if i == 0 else "NO_GLOBAL_WORK_IDENTITY_ASSERTED"
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
        "data_status": "B001-ENT-S1-PUBLISHER_SOURCE_CARD_PROPOSAL_ONLY",
        "accepted_catalog_sha256": CATALOG_SHA,
        "accepted_ent_bundle_sha256": BUNDLE_SHA,
        "observations_sha256": digest(json.dumps(observations, sort_keys=True,
                                                 separators=(",", ":")).encode()),
        "source_local_cards_enriched": 10,
        "new_source_local_title_slot_rechecks": 10,
        "combined_multipart_cards_preserved_as_single_source_slot": 1,
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
    "5cabacc1f72193949e14b5faf89e534491b2bb8724525438325339853e662c60",
    "5869b7f3a37c77dcc7d9cc8b339b36f1638db69bf7af73709f9b34315089fa98",
    "92c167d2d5860ffb130d57036e83df4abe94330ecce3cfdaf8a00542c7209b6c",
    "2990897c50ed7a2cec310305eb383b5f11fb2efab0a5d4ea646fa4badf9e6ef9",
    "c210d2a7bf17e51f57d5791e983c2e48e0b930d7315f8a1593004d5e9eace4d0",
    "d5862369f30b361dfe428f304d3771c8ae2fe2cfd7275189498362825f97afd4",
    "84cb64e80ff3b2b77f2261a53f82f5fbb25b4bb13abed2a6491ebf440a28f8ec",
    "223791657cc38f7d3f89e8a1266c386aa56352e591e2659fbbfd0197799a5da9",
    "790d02bf5accfa0338deaea5036dc46670051ce93031299ade688113e918caf7",
    "d021cf04ea3255ce1779aad04569f7e23da8709670ff8e5cbee872371f2f3e0b",
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
            raise SystemExit("ENT B001 records stale or tampered")
        print("Enterprise B001 source-local card compilation: PASS")
    else:
        target.write_text(output, encoding="utf-8")
        print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
