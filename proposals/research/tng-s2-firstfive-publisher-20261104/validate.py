#!/usr/bin/env python3
"""Deterministic HELD TNG S2 publisher-card validator; no source/Work admission."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/"
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
CATALOG = Path("explorer/discovery-catalog.json")
LEGACY_CSV = Path("proposals/discovery/legacy-paramount-season2-20261102/tng.csv")
LEGACY_BUNDLE = Path("proposals/discovery/legacy-paramount-season2-20261102/tng/bundle.json")
ACCEPTED_HASHES = {
    CATALOG: "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    LEGACY_CSV: "32b3dffa2afa0ba315ed6ad16e70eec21e2ec50df76eb7d60a039cc88ae4a85d",
    LEGACY_BUNDLE: "4817f8abcea7d55855970ae149558ec9fbe4d291aa1cadb7c9e0f77ccac1af85",
}
EXPECTED = (
    ("000", 1, "The Child", "8d7afc2c9303182edbe28df5f2f21db4c12f50ad108fa096db9941a1affca3b7",
     ("Counselor Troi",), "A dangerous medical transport is interrupted by the crew's discovery that Counselor Troi is pregnant."),
    ("001", 2, "Where Silence Has Lease", "e8b690e9d059c1748001a9059c9887fd8310c092184c3336a6d9745fae9bce03",
     (), "The publisher presents the crew as captives of a being studying human mortality within an unfamiliar void."),
    ("002", 3, "Elementary, Dear Data", "4dce085bcc6f88e66e2148c89844b5dd67a2c909bda478b630349fd87c443e8d",
     ("Data", "Sherlock Holmes", "Dr. Pulaski"),
     "A Sherlock Holmes puzzle involving Data becomes a threat to Doctor Pulaski, according to the publisher's guide."),
    ("003", 4, "The Outrageous Okona", "ba2cdb966d6cf49e2a48e43ce334e61130c60113034d524ddb896d51912bb028",
     ("Enterprise crew", "Data"), "The Enterprise hosts a roguish visiting captain as Data grapples with understanding humor."),
    ("004", 5, "Loud as a Whisper", "7a0ea0e2d33856ba36f063fbff62932b1bfb8878ef83a5325ae199a6e2b0e48c",
     (), "A mediator essential to negotiations on a divided planet suddenly loses his established means of communication."),
)
ENVELOPE_KEYS = {
    "schema_version", "batch_id", "baseline_accepted_main", "status", "source",
    "audiovisual_episodes_watched", "scripts_or_transcripts_read",
    "publisher_description_prose_republished", "global_work_identity_resolved",
    "admission_effect", "coverage_effect", "rows",
}
SOURCE_KEYS = {
    "guide_url", "publisher_lineage", "retrieved_utc_date", "read_surface",
    "entire_guide_card_count_read", "raw_html_sha256", "raw_html_custody",
    "description_fingerprint_method", "independent_source_families",
}
ROW_KEYS = {
    "row_id", "publisher_title", "season", "episode", "publisher_card_locator",
    "rendered_description_sha256", "literal_description_mentions",
    "original_short_paraphrase", "evidence_frame", "identity_hold",
}


def fail(message: str) -> None:
    raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key {key}")
        result[key] = value
    return result


def read_json(path: Path):
    require(not path.is_symlink() and path.is_file() and path.stat().st_size <= 4_000_000,
            f"missing, symlinked or excessive JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_unique,
                      parse_constant=lambda value: fail("non-finite JSON constant"))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def accepted_inputs(root: Path = ROOT):
    for path, digest in ACCEPTED_HASHES.items():
        absolute = root / path
        require(not absolute.is_symlink() and absolute.is_file(), f"missing accepted input {path}")
        require(sha(absolute.read_bytes()) == digest, f"accepted input changed: {path}")
    catalog = read_json(root / CATALOG)
    require(catalog.get("row_count") == 1214 and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("coverage_effect") == "NONE" and catalog.get("admission_effect") == "NONE",
            "accepted directory admission or count drift")
    with (root / LEGACY_CSV).open(newline="", encoding="utf-8") as f:
        roster = list(csv.DictReader(f))
    require(len(roster) == 22 and list(roster[0].keys()) == ["season", "episode_number", "title"],
            "accepted TNG S2 legacy roster drift")
    require([(row["season"], row["episode_number"], row["title"]) for row in roster[:5]] ==
            [("2", str(ep), title) for _, ep, title, *_ in EXPECTED],
            "accepted legacy five-slot sequence drift")
    return catalog


def compile_held(observations: dict, catalog: dict) -> dict:
    require(type(observations) is dict and set(observations) == ENVELOPE_KEYS,
            "unreviewed observation envelope")
    exact = {
        "schema_version": "1.0.0",
        "batch_id": "TNG-S2-FIRST-FIVE-PUBLISHER-20261104",
        "baseline_accepted_main": MAIN,
        "status": "HELD_SOURCE_LOCAL_PUBLISHER_METADATA",
        "audiovisual_episodes_watched": False,
        "scripts_or_transcripts_read": False,
        "publisher_description_prose_republished": False,
        "global_work_identity_resolved": False,
        "admission_effect": "NONE", "coverage_effect": "NONE",
    }
    for key, value in exact.items():
        require(type(observations[key]) is type(value) and observations[key] == value,
                f"unapproved observation envelope change: {key}")
    source = observations["source"]
    require(type(source) is dict and set(source) == SOURCE_KEYS,
            "unreviewed publisher source fields")
    expected_source = {
        "guide_url": GUIDE, "publisher_lineage": "paramount_corporate_publisher_family",
        "retrieved_utc_date": "2026-11-04",
        "read_surface": "FULL_RENDERED_PUBLISHER_SEASON_GUIDE_WEB_READER",
        "entire_guide_card_count_read": 22, "raw_html_sha256": None,
        "raw_html_custody": "UNAVAILABLE",
        "description_fingerprint_method": "RENDERED_WEB_READER_DESCRIPTION_TRIMMED_UTF8_NFC",
        "independent_source_families": 1,
    }
    for key, value in expected_source.items():
        require(type(source[key]) is type(value) and source[key] == value,
                f"unapproved publisher source claim: {key}")

    rows = observations["rows"]
    require(type(rows) is list and len(rows) == 5, "exactly five publisher cards required")
    directory = {r["row_id"]: r for r in catalog["rows"]}
    require(len(directory) == 1214, "ambiguous accepted source-local IDs")
    compiled = []
    for row, (suffix, episode, title, digest, mentions, paraphrase) in zip(rows, EXPECTED):
        require(type(row) is dict and set(row) == ROW_KEYS, "unreviewed publisher card fields")
        row_id = "legacy:s2:tng:" + suffix
        expected_row = {
            "row_id": row_id, "publisher_title": title, "season": 2, "episode": episode,
            "publisher_card_locator": f"Season 2 / {title} / S2 E{episode}",
            "rendered_description_sha256": digest, "literal_description_mentions": list(mentions),
            "original_short_paraphrase": paraphrase,
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
        }
        for key, value in expected_row.items():
            require(type(row[key]) is type(value) and row[key] == value,
                    f"unreviewed source card field: {row_id} {key}")
        directory_row = directory.get(row_id)
        require(type(directory_row) is dict and directory_row.get("title") == title
                and directory_row.get("context") == f"TNG S2E{episode}"
                and directory_row.get("medium") == "EPISODE"
                and directory_row.get("candidate_kind") == "PUBLISHER_EPISODE_SLOT"
                and directory_row.get("source_group") == "publisher:paramount"
                and directory_row.get("source_input") == str(LEGACY_BUNDLE)
                and directory_row.get("source_locator") == GUIDE
                and directory_row.get("verification_status") == "UNVERIFIED_METADATA"
                and directory_row.get("admission_effect") == "NONE"
                and directory_row.get("coverage_effect") == "NONE",
                f"accepted source-local row changed: {row_id}")
        compiled.append({
            "source_local_row_id": row_id, "title": title,
            "publisher_card": {"guide_url": GUIDE, "season": 2, "episode": episode,
                               "rendered_description_sha256": digest,
                               "raw_webpage_sha256": None},
            "local_entity_mentions_in_publisher_description": list(mentions),
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "original_editorial_paraphrase_held": paraphrase,
            "synopsis_publication_status": "PENDING_EDITORIAL_AND_SOURCE_REVIEW",
            "global_work_identity": "UNRESOLVED", "source_custody": "NO_RAW_HTML_BYTES",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        })
    return {
        "schema_version": "1.0.0", "data_status": "HELD_TNG_S2_FIRST_FIVE_PUBLISHER_DESCRIPTION_OBSERVATIONS",
        "accepted_catalog_sha256": ACCEPTED_HASHES[CATALOG],
        "accepted_s2_csv_sha256": ACCEPTED_HASHES[LEGACY_CSV],
        "accepted_s2_bundle_sha256": ACCEPTED_HASHES[LEGACY_BUNDLE],
        "publisher_family": "paramount_corporate_publisher_family",
        "guide_url": GUIDE, "source_body_custody": "NOT_ESTABLISHED",
        "source_local_cards_enriched": 5, "new_works": 0,
        "independent_source_families": 1,
        "governed_research_admissions": 0, "coverage_effect": "NONE",
        "records": compiled,
    }


def render(data: dict) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    catalog = accepted_inputs()
    observations = read_json(HERE / "observations.json")
    output = render(compile_held(observations, catalog))
    target = HERE / "records.json"
    if args.check:
        require(target.is_file() and not target.is_symlink() and target.read_bytes() == output,
                "held projection stale or missing")
    else:
        target.write_bytes(output)
    print("TNG-S2-FIRST-FIVE-HELD-PASS cards=5 independent_families=1 admissions=0")


if __name__ == "__main__":
    main()
