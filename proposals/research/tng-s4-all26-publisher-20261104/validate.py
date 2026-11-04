#!/usr/bin/env python3
"""Deterministic HELD TNG S4 publisher descriptions, never episode admissions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/4/"
PRIOR_RAW_DIGEST = "0cc73489140c6427a0cf0f608483d6d0aa07671596d31e4be6e96dcf285dab95"
OBSERVATIONS_DIGEST = "9a45d27bd1d5a7ffef20ef137064618682f9cbbacc33f732753627cb11ac19f8"
CATALOG = Path("explorer/discovery-catalog.json")
CSV = Path("proposals/discovery/publisher-season4-20261102/tng.csv")
BUNDLE = Path("proposals/discovery/publisher-season4-20261102/tng/bundle.json")
INDEX = Path("proposals/discovery/publisher-season4-20261102/index.json")
INPUT_HASHES = {
    CATALOG: "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    CSV: "709317afb74c9cb6ca1fe2bcf3788ed6ed1449b3437fab556ab46091cae237a2",
    BUNDLE: "631627a240ca997d51c5c6c031dc46aecf23a59350e024474e00caa9eb9f15d9",
    INDEX: "f29e5bda97ea63a85c3a0fa4730238ca3f67535685370732f87fbb4a20977346",
}
EXPECTED_CARDS = (
    (1, "The Best Of Both Worlds, Part 2", "245c7f87bbd53b1e44f67c53bee1bd9d5bcd5124510c4326b32b5c77658c6589", "THREATENED_DESTRUCTION_NOT_COMPLETION"),
    (2, "Family", "f3562986f1913c80583892250fdd97ff394370baffd6fd4f3c5c7bcf84c41b6d", "UNNAMED_BROTHER"),
    (3, "Brothers", "48b59d3c7fce119a8156649828f60e23ec6beb7acdd887384b0f5510448bb49c", "EVALUATIVE_EVIL_LABEL"),
    (4, "Suddenly Human", "0f381ea9e2e0fac5ee053cdfcc54195456da1d2706bd24da6eab2a610d9b1347", "ABUSE_SUSPICION_NOT_VERIFIED"),
    (5, "Remember Me", "49540104054d340cea01be26ee43b176e40706a816aae1c6bbc0fb0c3f01ccb1", "CAUSE_NOT_INDEPENDENTLY_ESTABLISHED"),
    (6, "Legacy", "3846e86935e32922bbb9bb1ef2e40589144e3a6a4bd074dd869af10a6d10dd21", "UNNAMED_SISTER"),
    (7, "Reunion", "669ac966dc9a75e3d58efdbbb899aada2cca3dc5527d4d55362bef891df2b40e", "PAST_DISGRACE_SOURCE_RELATIVE"),
    (8, "Future Imperfect", "e8e669f54aca396f0a8fcaa46c8cd74b70fb9449147e5c46f117a4c2e77cac9a", "SUBJECTIVE_TIME_DISPLACEMENT_UNRESOLVED"),
    (9, "Final Mission", "657d3ca3e35fdf086e6e4376281a2a53895c609a610a5be516d95462f99181a9", "NONE"),
    (10, "The Loss", "93f396b18817d1bb9abbaf97b1b2f1995d31d22ace61b2bbcf97b242ad9bb6dd", "SUBJECTIVE_CAPABILITY_LOSS"),
    (11, "Data's Day", "9509034342f166289f6d051125fd9421febcdec0b5a395254713201c53ab334e", "UNNAMED_FRIEND"),
    (12, "The Wounded", "a1836eedb448cf78b953cc59cabfafec66c8853719a0d0e6ce16c9e12aa0c661", "UNPROVOKED_ATTACKS_PUBLISHER_FRAMING"),
    (13, "Devil's Due", "efa843e75e5e4ca43fa717f8c45862a2e51f31e346685e5e8987e6e5898a53b7", "SELF_PROCLAIMED_DEVIL_NOT_ONTOLOGY"),
    (14, "Clues", "1d2bade0b67f39208105919dfc3d05e51daf0a7d09649ce2f4ed26dea1e7d57e", "PUBLISHER_DECEPTION_FRAME_NOT_ADJUDICATED"),
    (15, "First Contact", "984afad29dce0943107f92f39d90457c7788ffd054bc1f090bb94762e801cac1", "ERRONEOUS_HOSTILE_LABEL"),
    (16, "Galaxy's Child", "5d7cd8b3ff250af9f4839268a42f32484bdc600f07eaf7f9a762edea1353b05f", "METAPHORICAL_PARENTAGE_NOT_BIOLOGY"),
    (17, "Night Terrors", "f3ffa25c6d7a73054955622f5ddbea1a61d6e4ae4154ee4f598a53ba9c3218c9", "PERCEPTION_HALLUCINATION_FRAME"),
    (18, "Identity Crisis", "0322c5f85cb780e34675858b2fb3d11814ab4bc1da228f2e145a190bfd996c45", "THREATENED_CHANGE_NOT_VERIFIED"),
    (19, "The Nth Degree", "670857a4709db466e367abdeef09d1fcb673b1e6dc42a3c9c30a5d55e54a0692", "UNNAMED_CREW_MEMBER"),
    (20, "Qpid", "49da68c1ca1ac9249b09c1fb4dd3fb849f5b1053fca044d11d0cd36338edab91", "ROLEPLAY_IDENTITY_NOT_GLOBAL"),
    (21, "The Drumhead", "abf64a871b679c8bb5d19af6d1d990c5ade818a06042a442ab8f94171a5a4d23", "ALLEGATION_NOT_GUILT"),
    (22, "Half a Life", "cd811b03a4cf223bd7d5b0ab2a82359a4f13f0ca6d3b83b7863a3d8dc433062b", "SOCIETAL_MANDATE_NOT_ACT"),
    (23, "The Host", "1de34a7e0c457aa8de72c52abdb85571d4727de1ea3de17c3b52e00e5b6818f4", "MULTIPLE_HOST_BODY_IDENTITY_UNRESOLVED"),
    (24, "The Mind's Eye", "84c1485a8c98a47fec1cbff6e29dba8c942453702b65cff13fa28c2dd0dcd4ef", "PUBLISHER_METAPHOR_NOT_ACTION_PROOF"),
    (25, "In Theory", "830c0b4b4b5788e63687c0d20408d18cd6b89e10644f5585eee2ad36fa8ce8e1", "ROMANCE_NOT_CONSCIOUSNESS_PROOF"),
    (26, "Redemption, Part 1", "cf98f4de8b67aad8107b690cae16095c485d19757bd055cf133256935b7bec76", "THREATENED_CONFLICT_NOT_CONFIRMED"),
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
            "accepted TNG Season 4 roster drift")
    require([(x["season"], x["episode_number"], x["title"]) for x in roster]
            == [("4", str(ep), title) for ep, title, *_ in EXPECTED_CARDS],
            "accepted TNG Season 4 official-title/ordinal drift")
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
        "schema_version": "1.0.0", "batch_id": "TNG-S4-B017-PUBLISHER-CARDS-20261104",
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
        row_id = f"publisher:s4:tng:{ep - 1:03d}"
        require(type(row) is dict and set(row) == ROW_FIELDS, f"unreviewed card shape {row_id}")
        exact = {
            "row_id": row_id, "publisher_title": title,
            "season": 4, "episode": ep,
            "publisher_card_locator": f"Season 4 / {title} / S4 E{ep}",
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
                and prior.get("context") == f"TNG S4E{ep}"
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
                "guide_url": GUIDE, "season": 4, "episode": ep,
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
        "data_status": "HELD_TNG_S4_ALL_26_PUBLISHER_METADATA",
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
                "TNG S4 publisher-held projection stale")
    else:
        output.write_bytes(data)
    print("TNG-S4-B017-HELD-PASS cards=26 independent_families=1 admissions=0")


if __name__ == "__main__":
    main()
