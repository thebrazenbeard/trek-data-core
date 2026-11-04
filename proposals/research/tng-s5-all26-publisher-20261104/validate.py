#!/usr/bin/env python3
"""Deterministic HELD TNG S5 publisher descriptions, never episode admissions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/5/"
PRIOR_RAW_DIGEST = "8545f8456f527c4c253c8ee7f3a4ad51991e42e74faf4591de536a19bbe78644"
OBSERVATIONS_DIGEST = "4aafad373c3016043faff060026505259d23da9449b545b62a0a35c44e647845"
CATALOG = Path("explorer/discovery-catalog.json")
CSV = Path("proposals/discovery/publisher-season5-20261102/tng.csv")
BUNDLE = Path("proposals/discovery/publisher-season5-20261102/tng/bundle.json")
INDEX = Path("proposals/discovery/publisher-season5-20261102/index.json")
INPUT_HASHES = {
    CATALOG: "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    CSV: "e3ef73cea98cc7f737715e72bb7f514b32963be21934e02b6a93b2bfbb431da7",
    BUNDLE: "968f48a0a623f05a5cac8971d2075050c08ccb347c60b8ff23e53f148477e992",
    INDEX: "7eec39af66a3240316c77da7e6d83fb2886dc5c327d61412e04e2d012ab26ca7",
}
EXPECTED_CARDS = (
    (1, "Redemption, Part 2", "c237570a1a40dc87aebc79772b2999aa34caa973a166b746746f630db43d5df5", "THREATENED_WAR_NOT_OCCURRED"),
    (2, "Darmok", "f4a07c39186491c1bd9c47e997011faf407e6832e074835462c0ec9c396b4e6e", "UNNAMED_ALIEN_CAPTAIN"),
    (3, "Ensign Ro", "561327a5605813a94905a44d3d7b03677d5a9e5588a7787088348181088c473c", "SOURCE_NEAR_DUPLICATE_S6E20_NONINDEPENDENT"),
    (4, "Silicon Avatar", "a0c4693955e7b67f5639f1ae5ba52a5dce1621b8508716f7cc0af9b74d89a7e8", "UNNAMED_DESTRUCTIVE_FORCE"),
    (5, "Disaster", "f401d42ccfe0c08518352c15efee4c3e4495673e8b052ece4bdd7fe65546d94a", "DISASTER_PROMOTIONAL_CAUSE"),
    (6, "The Game", "46c07db7fbb2a0e3a63e41bf0bdb91b6b9fb1d5ad4b9a895d89de6ba85ced4f0", "ADDICTION_LABEL_SOURCE_RELATIVE"),
    (7, "Unification - Part 1", "bc7c2a8a54a98ed0487bdd6f1984cfd1580501704bd328a6c93aa2eb7fecc2e7", "PUBLISHER_SPOCK_SPACING_VARIANT"),
    (8, "Unification - Part 2", "a517cfa7947402c59b0e2dc2cd1ce3fac9c21f560ac6f98f1d3f8a63fb530480", "POLITICAL_PLAN_NOT_OCCURRED"),
    (9, "A Matter of Time", "576e07242628c6aec5975e3543e0e7432a9e1a13ae1044904effd53905f0a94b", "TIME_TRAVEL_CLAIM_NOT_ADJUDICATED"),
    (10, "New Ground", "e195cf3c88677abda8e5ed5837698aaf83d24a09288fecd0f873bcad8db02a35", "NAMED_PARENT_CHILD_SOURCE_RELATIVE"),
    (11, "Hero Worship", "5c17ad4410b72d3e160952fbdb363f68fb89a5cd40f07585251273db65a19825", "SURVIVOR_SIMULATION_NOT_ENTITY_IDENTITY"),
    (12, "Violations", "5b8eb6fcec267cb5a2a55908a720a2c31722d2b4eb2676c1b9609738510587c3", "UNEXPLAINED_COMA_NO_CAUSAL_INFERENCE"),
    (13, "The Masterpiece Society", "e06ca22d8295db55d9a980005601dd69be7d09bd9d8ecdae2e57ee5a7e8fb617", "CAUSAL_RESCUE_THREAT_NOT_VERIFIED"),
    (14, "Conundrum", "9149adbfb38404e980e0cb4631f38303ccaaace40923a7158224876c027c8034", "AMNESIA_UNRELIABLE_MEMORY"),
    (15, "Power Play", "947a7e2bdceb6324913128072d03690402c9438fdaa5920b7534ab492918b6de", "MOTIVE_BEHIND_BRIDGE_ACTION_UNRESOLVED"),
    (16, "Ethics", "459ba517d53489c795ee769305087546481ec4e9f45028a568e8bb5236d1c0bc", "REQUEST_FOR_ASSISTANCE_NOT_ACT"),
    (17, "The Outcast", "d67f1e2dd071cd9a0deaa0615b38099922ccd99f2296f81af7705efee1d9290a", "GENDER_AND_ROMANCE_NOT_ONTOLOGY"),
    (18, "Cause and Effect", "9d9dd032533185888d8c4ea4b5add82b188a3b314539d5f027a8d2d801e2cfb9", "RECURSIVE_TIMELINE_NOT_RECONCILED"),
    (19, "The First Duty", "7dcad3f7a6c5791acbb71860b7cce06047be222b59042d834cf7578bfa494c76", "COVER_UP_INVOLVEMENT_NOT_GUILT"),
    (20, "Cost of Living", "a9c11a3bc56bd3d18f3132f3065fb60626da21c23554cae5d4125f4dc91df98f", "UNNAMED_MOTHER_NO_INFERRED_IDENTITY"),
    (21, "The Perfect Mate", "3272a57b9ff6d8ebf4c51e03ce061dca9725ab29f8c5b3a6cf4d3ae67e8be522", "PERSON_AS_PEACE_OFFERING_AGENCY_UNRESOLVED"),
    (22, "Imaginary Friend", "26c041b12fc98e4cc763ada565dba4968525ba88682f8c7ffa610e787d3da77f", "IMAGINARY_FRIEND_REALITY_CLAIM_UNVERIFIED"),
    (23, "I, Borg", "b14fa4cf8f658b26b161396926dc3079657b414377f7d143ffa142e0918b3bfc", "BORG_INDIVIDUAL_IDENTITY_UNRESOLVED"),
    (24, "The Next Phase", "d9b4b73bb05288df4312a3d437621711411d5cab6d6ff4c97384532e55a47f0a", "DECLARED_DEATH_NOT_VERIFIED_DEATH"),
    (25, "The Inner Light", "7448e8beb76c7739c8c77192ecbf1edc7692f52c8d3f92a0d1f95a9a496cb375", "SUBJECTIVE_LIFE_IDENTITY_UNRESOLVED"),
    (26, "Time's Arrow - Part 1", "2c76eb354ef795037073ba873f6b3ef34697ee9cdb71196be919f3a20e642a5c", "FORETOLD_DEATH_NOT_ACTUAL_DEATH"),
)
ENVELOPE_FIELDS = {
    "schema_version", "batch_id", "baseline_accepted_main", "status", "source",
    "audiovisual_episodes_watched", "scripts_or_transcripts_read_in_this_batch",
    "publisher_description_prose_republished", "global_work_identity_resolved",
    "admission_effect", "coverage_effect", "rows",
}
SOURCE_FIELDS = {
    "guide_url", "publisher_lineage", "retrieved_utc_date", "read_surface",
    "entire_guide_card_count_read", "fresh_raw_html_sha256", "fresh_raw_html_custody",
    "prior_2026_11_02_discovery_receipt_sha256", "prior_receipt_status",
    "description_fingerprint_method", "independent_source_families",
}
ROW_FIELDS = {
    "row_id", "publisher_title", "season", "episode", "publisher_card_locator",
    "rendered_description_sha256", "literal_description_mentions",
    "original_short_paraphrase", "publisher_framing_anomaly",
    "evidence_frame", "identity_hold",
}
DUPLICATE_FIELD = "same_publisher_near_duplicate"
SIXTH_SEASON_CROSSCHECK = {
    "comparison_guide_url": "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/6/",
    "comparison_card_locator": "Season 6 / The Chase / S6 E20",
    "comparison_reader_description_sha256": "c412ee53e45dfa2053ffb62395bccdd3fd1205967dae7f0dcf5aeb8f864bc8fd",
    "difference": "FOUR_BILLION_YEAR_OLD_HYPHENATION_ONLY",
    "lineage": "SAME_PARAMOUNT_PUBLISHER_FAMILY",
    "independent_corroboration": False,
    "identity_resolution_effect": "NONE",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key {key}")
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 4_000_000,
            f"missing, symlinked, or excessive JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def render(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def accepted_inputs(root=ROOT):
    for path, digest in INPUT_HASHES.items():
        original = root / path
        require(original.is_file() and not original.is_symlink() and sha(original.read_bytes()) == digest,
                f"accepted source-local dependency drift: {path}")
    index = read_json(root / INDEX)
    require(index.get("proposal_status") == "DISCOVERY_ONLY"
            and index.get("admission_effect") == "NONE"
            and index.get("coverage_effect") == "NONE", "accepted historical receipt status drift")
    tng = [x for x in index.get("source_pages", []) if x.get("mission_id") == "tng"]
    require(len(tng) == 1 and tng[0].get("official_page") == GUIDE
            and tng[0].get("source_body_sha256") == PRIOR_RAW_DIGEST
            and tng[0].get("observation_csv_sha256") == INPUT_HASHES[CSV]
            and tng[0].get("listed_slot_count") == 26, "accepted prior publisher receipt drift")
    with (root / CSV).open(newline="", encoding="utf-8") as stream:
        roster = list(csv.DictReader(stream))
    require(len(roster) == 26 and list(roster[0]) == ["season", "episode_number", "title"],
            "accepted TNG Season 5 roster drift")
    require([(x["season"], x["episode_number"], x["title"]) for x in roster]
            == [("5", str(ep), title) for ep, title, *_ in EXPECTED_CARDS],
            "accepted TNG Season 5 official-title/ordinal drift")
    directory = read_json(root / CATALOG)
    require(directory.get("row_count") == 1214
            and directory.get("data_status") == "DISCOVERY_ONLY"
            and directory.get("admission_effect") == "NONE"
            and directory.get("coverage_effect") == "NONE", "accepted discovery directory drift")
    return directory


def compile_held(observations, directory):
    require(type(observations) is dict and set(observations) == ENVELOPE_FIELDS,
            "unreviewed observations envelope")
    require(sha((json.dumps(observations, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            == OBSERVATIONS_DIGEST, "observations content does not match source-read review pin")
    envelope = {
        "schema_version": "1.0.0", "batch_id": "TNG-S5-B018-PUBLISHER-CARDS-20261104",
        "baseline_accepted_main": MAIN, "status": "HELD_SOURCE_LOCAL_PUBLISHER_METADATA",
        "audiovisual_episodes_watched": False,
        "scripts_or_transcripts_read_in_this_batch": False,
        "publisher_description_prose_republished": False,
        "global_work_identity_resolved": False,
        "admission_effect": "NONE", "coverage_effect": "NONE",
    }
    for key, expected in envelope.items():
        require(type(observations[key]) is type(expected) and observations[key] == expected,
                f"unreviewed batch claim: {key}")
    source = observations["source"]
    require(type(source) is dict and set(source) == SOURCE_FIELDS, "unreviewed source fields")
    expected_source = {
        "guide_url": GUIDE, "publisher_lineage": "paramount_corporate_publisher_family",
        "retrieved_utc_date": "2026-11-04",
        "read_surface": "FULL_RENDERED_PUBLISHER_SEASON_GUIDE_WEB_READER",
        "entire_guide_card_count_read": 26,
        "fresh_raw_html_sha256": None, "fresh_raw_html_custody": "UNAVAILABLE",
        "prior_2026_11_02_discovery_receipt_sha256": PRIOR_RAW_DIGEST,
        "prior_receipt_status": "HISTORICAL_UNREVALIDATED_RAW_DISCOVERY_RECEIPT",
        "description_fingerprint_method": "RENDERED_WEB_READER_DESCRIPTION_TRIMMED_UTF8_NFC",
        "independent_source_families": 1,
    }
    for key, expected in expected_source.items():
        require(type(source[key]) is type(expected) and source[key] == expected,
                f"unreviewed publisher source claim {key}")
    rows = observations["rows"]
    require(type(rows) is list and len(rows) == 26, "exact 26 publisher cards required")
    require(type(directory) is dict and type(directory.get("rows")) is list,
            "accepted discovery row structure drift")
    accepted = {row["row_id"]: row for row in directory["rows"]}
    require(len(accepted) == 1214, "accepted discovery duplicate local IDs")
    records = []
    for row, (ep, title, digest, anomaly) in zip(rows, EXPECTED_CARDS):
        row_id = f"publisher:s5:tng:{ep - 1:03d}"
        require(type(row) is dict and set(row) == (ROW_FIELDS | ({DUPLICATE_FIELD} if ep == 3 else set())),
                f"unreviewed card shape {row_id}")
        exact = {
            "row_id": row_id, "publisher_title": title,
            "season": 5, "episode": ep,
            "publisher_card_locator": f"Season 5 / {title} / S5 E{ep}",
            "rendered_description_sha256": digest,
            "publisher_framing_anomaly": anomaly,
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
        }
        for key, expected in exact.items():
            require(type(row[key]) is type(expected) and row[key] == expected,
                    f"publisher-card claim drift {row_id}.{key}")
        if ep == 3:
            comparison = row[DUPLICATE_FIELD]
            require(type(comparison) is dict and set(comparison) == set(SIXTH_SEASON_CROSSCHECK),
                    "unreviewed cross-guide source comparison shape")
            for key, expected in SIXTH_SEASON_CROSSCHECK.items():
                require(type(comparison[key]) is type(expected) and comparison[key] == expected,
                        f"unreviewed source comparison {key}")
        mentions = row["literal_description_mentions"]
        paraphrase = row["original_short_paraphrase"]
        require(type(mentions) is list and len(mentions) <= 10
                and len(mentions) == len(set(mentions))
                and all(type(x) is str and x.strip() == x and 1 <= len(x) <= 80 for x in mentions),
                f"invalid literal mentions {row_id}")
        require(type(paraphrase) is str and paraphrase.strip() == paraphrase
                and 30 <= len(paraphrase) <= 220, f"invalid held paraphrase {row_id}")
        prior = accepted.get(row_id)
        require(type(prior) is dict and prior.get("title") == title
                and prior.get("context") == f"TNG S5E{ep}"
                and prior.get("medium") == "EPISODE"
                and prior.get("candidate_kind") == "PUBLISHER_EPISODE_SLOT"
                and prior.get("source_group") == "publisher:paramount"
                and prior.get("source_input") == str(BUNDLE)
                and prior.get("source_locator") == GUIDE
                and prior.get("verification_status") == "UNVERIFIED_METADATA"
                and prior.get("identity_scope") == "SOURCE_LOCAL"
                and prior.get("coverage_effect") == "NONE"
                and prior.get("admission_effect") == "NONE",
                f"accepted source-local row drift: {row_id}")
        record = {
            "source_local_row_id": row_id, "publisher_title": title,
            "publisher_card": {
                "guide_url": GUIDE, "season": 5, "episode": ep,
                "rendered_description_sha256": digest,
                "current_raw_html_sha256": None,
                "prior_unrevalidated_source_body_sha256": PRIOR_RAW_DIGEST,
            },
            "source_relative_mentions": mentions,
            "publisher_framing_anomaly": anomaly,
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "original_editorial_paraphrase_held": paraphrase,
            "synopsis_publication_status": "PENDING_EDITORIAL_AND_SOURCE_REVIEW",
            "global_work_identity": "UNRESOLVED",
            "source_custody": "NO_FRESH_RAW_HTML_BYTES",
            "source_families": 1,
            "new_work": False, "admission_effect": "NONE", "coverage_effect": "NONE",
        }
        if ep == 3:
            record["same_publisher_cross_guide_near_duplicate"] = row[DUPLICATE_FIELD]
        records.append(record)
    return {
        "schema_version": "1.0.0",
        "data_status": "HELD_TNG_S5_ALL_26_PUBLISHER_METADATA",
        "baseline_accepted_main": MAIN,
        "accepted_catalog_sha256": INPUT_HASHES[CATALOG],
        "accepted_s3_csv_sha256": INPUT_HASHES[CSV],
        "accepted_s3_bundle_sha256": INPUT_HASHES[BUNDLE],
        "accepted_prior_index_sha256": INPUT_HASHES[INDEX],
        "publisher_family": "paramount_corporate_publisher_family",
        "guide_url": GUIDE, "fresh_source_body_custody": "NOT_ESTABLISHED",
        "previous_source_receipt_status": "HISTORICAL_UNREVALIDATED_RAW_DISCOVERY_RECEIPT",
        "source_local_cards_enriched": 26, "new_works": 0,
        "independent_source_families": 1, "governed_research_admissions": 0,
        "coverage_effect": "NONE", "records": records,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    data = render(compile_held(read_json(HERE / "observations.json"), accepted_inputs()))
    output = HERE / "records.json"
    if args.check:
        require(output.is_file() and not output.is_symlink() and output.read_bytes() == data,
                "TNG S5 publisher-held projection stale")
    else:
        output.write_bytes(data)
    print("TNG-S5-B018-HELD-PASS cards=26 independent_families=1 admissions=0")


if __name__ == "__main__":
    main()
