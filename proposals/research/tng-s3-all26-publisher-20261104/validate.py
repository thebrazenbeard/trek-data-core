#!/usr/bin/env python3
"""Deterministic HELD TNG S3 publisher descriptions, never episode admissions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/3/"
PRIOR_RAW_DIGEST = "3b0492e8dac432bf82334a9bc27baf0a7718c1fc34d8ee4ac73a9b49ac714244"
OBSERVATIONS_DIGEST = "fef46bdef5c0c2f2968dbc1794751ba4defba3f927a08a421651a790d66ffaaa"
CATALOG = Path("explorer/discovery-catalog.json")
CSV = Path("proposals/discovery/legacy-paramount-season3-20261102/tng.csv")
BUNDLE = Path("proposals/discovery/legacy-paramount-season3-20261102/tng/bundle.json")
INDEX = Path("proposals/discovery/legacy-paramount-season3-20261102/index.json")
INPUT_HASHES = {
    CATALOG: "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    CSV: "b7d9718f20c9c74d0552483b99accb66c48d1d62fd22864febf14ae0f5a6b514",
    BUNDLE: "cd38dbdd2095585736a25b4a3821d80ad7f3150e31914330e936b0c5e224ebf4",
    INDEX: "452574d2f012c16ccf33583435ba1059b13f674dbba4ff53ea8056ac95f3afbf",
}
EXPECTED_CARDS = (
    (1, "Evolution", "2287d2dd067b833f25f51ad0f462a32f919d86f46092cf23d88626f4a318bc2b", "NONE"),
    (2, "The Ensigns of Command", "d8f7e5ee5c17c98ad21bc6e4ac2b237194650e107c2fa413c3a0160fa598e242", "NONE"),
    (3, "The Survivors", "0fdd3c7f72fe6ddfc3d17d8a6c3031075f8be34f95b87b1fb5f78d7521c9d055", "PUBLISHER_SURVIVOR_COUNT_UNVERIFIED"),
    (4, "Who Watches the Watchers", "3ee95e9eae3d1ca37de12767edf4267948b5a0f73249b1e813e49dc18dcc9be5", "ATTRIBUTED_BELIEF_NOT_DIVINITY"),
    (5, "The Bonding", "613bc171838c4bcdc399fef02d263fbe43145c94edd1da484617b31354643e03", "UNNAMED_DECEASED_PERSON_AND_CHILD"),
    (6, "Booby Trap", "4628198dc3b62a4fb2850a261dd9f27494a881b87d124b51f30e62bddfd95e15", "NONE"),
    (7, "The Enemy", "7a98a0e6d4c4431059b588e46f06977571f05c4d0b6a4781c8f6150d0c12e8c9", "NONE"),
    (8, "The Price", "b311ee62f802ed9daa10dce0ce897325bb4b9baedb9fe96420533ef3dc980391", "UNNAMED_DELEGATE_AND_VALUE_JUDGMENT"),
    (9, "The Vengeance Factor", "d85bac80edf6cd982903d7795f8c6408573e027edbf86027e37c6a511a9fc300", "UNNAMED_FACTIONS_AND_ASSASSIN"),
    (10, "The Defector", "f93daf6754514781f15dbfa98f4f50a9e60521c03ff7cd8052b6d07b20774154", "UNNAMED_DEFECTOR_AND_WAR_PROSPECT"),
    (11, "The Hunted", "d697e6cecf9f93c3374d728274d706bfdafd88cfcb5a3b8d4ef6a8c58c57974c", "CAUSAL_MIND_CONTROL_CLAIM"),
    (12, "The High Ground", "61e91391071df71c4ed97a5bb9f64c1a168ffaf77392ca7a9190d6259ad2ce14", "POLITICAL_GROUP_LABEL"),
    (13, "Deja Q", "0f444866583b93ebcbda375864c32b3dbaaae2ecd9588f948087819431116934", "NONE"),
    (14, "A Matter of Perspective", "a88be5aa8fa2c86da1d6d0b521c7cdc91dbfe794948d0648197d372e31cfaf08", "ACCUSATION_NOT_GUILT"),
    (15, "Yesterday's Enterprise", "78c6a66e0c02ff95a645c88fadabf06e8d4f3389cc2d0cd7e09e0fc5fcc2c107", "ALTERNATE_HISTORY_IDENTITY_UNRESOLVED"),
    (16, "The Offspring", "62b16bb257731320e00ea5df08cd57baf6f5e74b836119c382197557d36c59a3", "PARENTAL_RELATION_NOT_LEGAL_STATUS"),
    (17, "Sins of the Father", "490f667de293177990b30d96c96fde5698b8d239341219c5922eede2139ae6a4", "UNNAMED_BROTHER"),
    (18, "Allegiance", "ac5a03711a56fb319bf1604dd61fb28bc357dc8bde14eb1d5e462377ce913beb", "REPLACEMENT_IDENTITY_UNRESOLVED"),
    (19, "Captain's Holiday", "a87d280993add589d165483a8555edf56c9649d7cf0ce8262e7e98b440ee05f2", "FUTURE_ORIGIN_CLAIM_UNVERIFIED"),
    (20, "Tin Man", "f1fef29c4d6b810f190f11af8dc2ecc59c090aa8e0d33a56ca52f66ceaa3469c", "UNNAMED_LIFE_FORM"),
    (21, "Hollow Pursuits", "fde5a51de8266506044fbdb3364c2f2200294e3ca5176c8561a5d1706cee33b5", "UNNAMED_ENGINEER_HOLODECK_WORLD"),
    (22, "The Most Toys", "85389accdd650dd2e924a33c87321eae89161257aca2d470ff9236b04b83d04c", "PRESUMED_DEATH_NOT_VERIFIED_DEATH"),
    (23, "Sarek", "9853ac0a730be0fb90ccb4ffd1b4056ae5df9c6664570d16f3b8690363ddbdad", "TITLE_NAME_NOT_PUBLISHER_DESCRIPTION_ASSERTION"),
    (24, "Ménage à Troi", "3d306cae1b9a2ffbb118156a783f7fd75cddb4b6ebc37c704b7971caa47286a8", "TROI_DEANNA_RELATION_NOT_GLOBALLY_LINKED"),
    (25, "Transfigurations", "258213c858d2aea811ae33e95055333b0c1cbe7a110ce31d43bc6641312cdaa6", "UNNAMED_RESCUED_HUMANOID"),
    (26, "The Best Of Both Worlds, Part 1", "c1d29ed7558373478aa8f5d1605705242abff8e51c9753ab76b4548f757955bf", "EVALUATIVE_EVIL_LABEL"),
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
            "accepted TNG Season 3 roster drift")
    require([(x["season"], x["episode_number"], x["title"]) for x in roster]
            == [("3", str(ep), title) for ep, title, *_ in EXPECTED_CARDS],
            "accepted TNG Season 3 official-title/ordinal drift")
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
        "schema_version": "1.0.0", "batch_id": "TNG-S3-B016-PUBLISHER-CARDS-20261104",
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
        row_id = f"legacy:s3:tng:{ep - 1:03d}"
        require(type(row) is dict and set(row) == ROW_FIELDS, f"unreviewed card shape {row_id}")
        exact = {
            "row_id": row_id, "publisher_title": title,
            "season": 3, "episode": ep,
            "publisher_card_locator": f"Season 3 / {title} / S3 E{ep}",
            "rendered_description_sha256": digest,
            "publisher_framing_anomaly": anomaly,
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
        }
        for key, expected in exact.items():
            require(type(row[key]) is type(expected) and row[key] == expected,
                    f"publisher-card claim drift {row_id}.{key}")
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
                and prior.get("context") == f"TNG S3E{ep}"
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
        records.append({
            "source_local_row_id": row_id, "publisher_title": title,
            "publisher_card": {
                "guide_url": GUIDE, "season": 3, "episode": ep,
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
        })
    return {
        "schema_version": "1.0.0",
        "data_status": "HELD_TNG_S3_ALL_26_PUBLISHER_METADATA",
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
                "TNG S3 publisher-held projection stale")
    else:
        output.write_bytes(data)
    print("TNG-S3-B016-HELD-PASS cards=26 independent_families=1 admissions=0")


if __name__ == "__main__":
    main()
