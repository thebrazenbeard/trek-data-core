#!/usr/bin/env python3
"""Deterministic HELD TNG S2 E6–E22 publisher-card proposal; no admission."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
GUIDE = "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/"
CATALOG = Path("explorer/discovery-catalog.json")
CSV = Path("proposals/discovery/legacy-paramount-season2-20261102/tng.csv")
BUNDLE = Path("proposals/discovery/legacy-paramount-season2-20261102/tng/bundle.json")
DERIVATIVE = Path("proposals/research/tng-measure-of-a-man-derivative-20261103/MANIFEST.md")
INPUT_HASHES = {
    CATALOG: "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc",
    CSV: "32b3dffa2afa0ba315ed6ad16e70eec21e2ec50df76eb7d60a039cc88ae4a85d",
    BUNDLE: "4817f8abcea7d55855970ae149558ec9fbe4d291aa1cadb7c9e0f77ccac1af85",
    DERIVATIVE: "dfbbd49ff5d3d3eba7934f295923f70f89b02c93cb2f4e80f93d18eb7a26f747",
}
EXPECTED = (
    ("005", 6, "The Schizoid Man", "073245dc4c7603c19577358609411fdf905786f95638c86bfed24656561bb4e5",
     ("Data",), "The publisher describes a dying scientist seeking survival by transferring his mind into Data."),
    ("006", 7, "Unnatural Selection", "6293da7f7931691783015e69c2903e55072a598051754d9b5ad277a17f17e6d6",
     (), "A disease that rapidly ages humans becomes the crew's urgent problem in the publisher's outline."),
    ("007", 8, "A Matter of Honor", "13e0c224f98e83b9fa3d9dcb918ff74937bd95700870b3fdbbda2a932df51d93",
     ("Riker", "Klingon", "Enterprise"),
     "Riker's temporary assignment to a Klingon vessel becomes a test of loyalty when Enterprise is threatened."),
    ("008", 9, "The Measure of a Man", "7fb2e26657279394fdf0ff97fe9c79c58a4ab4e774b15c2aa513b26220320228",
     ("Data", "Picard"),
     "The publisher frames Data's refusal of research disassembly as the issue Picard must defend in court."),
    ("009", 10, "The Dauphin", "302df2a1b40175e52aab398f70bbfb19a2b15b29a7f22928b3a6a3dcfd7a83d8",
     ("Wesley", "Daled Four", "Enterprise"),
     "Wesley's romance with a young ruler is complicated by the undisclosed destructive power described in the publisher guide."),
    ("010", 11, "Contagion", "135fe3f503862f04089cca0501681630cd851a2d5004b4461090be3f5b52a5ce",
     ("Enterprise",), "The publisher describes an electronic infection of Enterprise's systems that threatens to trigger self-destruction."),
    ("011", 12, "The Royale", "e6255f79ef5fb17670945d8ba69b80e2b80f48c6837222e341e35af84d72c30a",
     ("United States Air Force", "The Hotel Royale"),
     "After finding an Air Force-marked object, an away team is described as trapped in an environment resembling a novel's hotel."),
    ("012", 13, "Time Squared", "2a57cc191cfe13f0c3ea2a169310b9412e4d58d4408587fd9d27c75b79507f5a",
     ("U.S.S. Enterprise", "Federation", "Picard"),
     "The publisher presents a shuttle whose occupant resembles Picard and appears to have arrived from six hours ahead."),
    ("013", 14, "The Icarus Factor", "fc534e9ea59518d3962923be0a368394aeba76693f239964f7f33ebcfe6a380f",
     ("Riker",), "Riker's estranged father returns during a period when a new starship command may be offered, according to the listing."),
    ("014", 15, "Pen Pals", "add15085200ac7a9de4389903c549e833667fdc4f530abec4a72c9ab47598ce1",
     ("Data",), "The publisher describes Data trying to protect an unnamed young alien as her planet faces destruction."),
    ("015", 16, "Q-Who?", "72d322507a912cf5d19a93e3cb9afed242bf85a36abe7fe02818aeb89078bc2c",
     ("Q", "Borg"), "Q is described as transporting the crew to a remote region where a Borg threat awaits them."),
    ("016", 17, "Samaritan Snare", "a5d0d15c55f13649f28ce2de5946672560b34d558368c3d4d04559e120820f46",
     ("Picard", "Geordi"), "The publisher juxtaposes Picard's life-threatening surgery with Geordi's captivity at the hands of an alien group."),
    ("017", 18, "Up the Long Ladder", "b6ab598dc82ab49362dfa8a807f38af76c5ce6774ab1c02145f0f7baff9bebf7",
     (), "A mission involving a missing Earth settlement is described as leading the crew to an all-clone society."),
    ("018", 19, "Manhunt", "f2c1db35349e3f469d2f671b382939d2e2f2d825f5d40aa905e1b513be2ab197",
     ("Troi", "Enterprise", "Picard"),
     "Troi's mother visits Enterprise in search of a partner and takes a particular interest in Picard, per the publisher."),
    ("019", 20, "The Emissary", "36028b9fe085ba46d2111100081e1d82930935808c47a523ac45eb355180e1c3",
     ("Worf", "Enterprise", "Klingons", "Federation"),
     "A former partner of Worf arrives to mediate a Klingon-Federation dispute, making an official mission personal."),
    ("020", 21, "Peak Performance", "58a7cd0af2efab32fdf99abdb979fd333b5a5da7d19f823387e1168c5d8259d5",
     ("Ferengi",), "The publisher describes a planned combat simulation overtaken by an actual ambush from a Ferengi ship."),
    ("021", 22, "Shades of Gray", "9f30092238553319b026a9339dc3ac4a63442ab17a492dbe1b4073c80894634c",
     ("Riker",), "Riker suffers a dangerous infection affecting his nervous system, in the publisher's episode listing."),
)
ENVELOPE = {"schema_version", "batch_id", "baseline_accepted_main", "status", "source",
            "audiovisual_episodes_watched", "scripts_or_transcripts_read_in_this_batch",
            "publisher_description_prose_republished", "global_work_identity_resolved",
            "admission_effect", "coverage_effect", "rows"}
SOURCE_FIELDS = {"guide_url", "publisher_lineage", "retrieved_utc_date", "read_surface",
                 "entire_guide_card_count_read", "raw_html_sha256", "raw_html_custody",
                 "description_fingerprint_method", "independent_source_families"}
ROW_FIELDS = {"row_id", "publisher_title", "season", "episode", "publisher_card_locator",
              "rendered_description_sha256", "literal_description_mentions",
              "original_short_paraphrase", "evidence_frame", "identity_hold"}
DERIVATIVE_FIELD = "prior_derivative_read_relationship"
DERIVATIVE_RELATION = "SAME_EPISODE_TITLE_SLOT_DIFFERENT_UNAUTHENTICATED_SOURCE_SURFACE"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key {key}")
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 4_000_000,
            f"missing, symlinked or excessive JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def accepted_inputs(root=ROOT):
    for path, digest in INPUT_HASHES.items():
        file = root / path
        require(file.is_file() and not file.is_symlink() and sha(file.read_bytes()) == digest,
                f"accepted source-local dependency drift: {path}")
    directory = read_json(root / CATALOG)
    require(directory.get("row_count") == 1214
            and directory.get("data_status") == "DISCOVERY_ONLY"
            and directory.get("admission_effect") == "NONE"
            and directory.get("coverage_effect") == "NONE", "accepted directory status drift")
    with (root / CSV).open(newline="", encoding="utf-8") as stream:
        roster = list(csv.DictReader(stream))
    require(len(roster) == 22 and list(roster[0]) == ["season", "episode_number", "title"],
            "accepted TNG Season 2 roster drift")
    require([(r["season"], r["episode_number"], r["title"]) for r in roster[5:22]] ==
            [("2", str(ep), title) for _, ep, title, *_ in EXPECTED],
            "accepted TNG S2E6–E22 source-local sequence drift")
    return directory


def compile_held(observations, directory):
    require(type(observations) is dict and set(observations) == ENVELOPE,
            "unreviewed batch envelope")
    exact_envelope = {
        "schema_version": "1.0.0", "batch_id": "TNG-S2-B014-B015-PUBLISHER-CARDS-20261104",
        "baseline_accepted_main": MAIN, "status": "HELD_SOURCE_LOCAL_PUBLISHER_METADATA",
        "audiovisual_episodes_watched": False,
        "scripts_or_transcripts_read_in_this_batch": False,
        "publisher_description_prose_republished": False,
        "global_work_identity_resolved": False,
        "admission_effect": "NONE", "coverage_effect": "NONE",
    }
    for key, expected in exact_envelope.items():
        require(type(observations[key]) is type(expected) and observations[key] == expected,
                f"unreviewed batch claim {key}")
    source = observations["source"]
    require(type(source) is dict and set(source) == SOURCE_FIELDS,
            "unreviewed source fields")
    exact_source = {
        "guide_url": GUIDE, "publisher_lineage": "paramount_corporate_publisher_family",
        "retrieved_utc_date": "2026-11-04",
        "read_surface": "FULL_RENDERED_PUBLISHER_SEASON_GUIDE_WEB_READER",
        "entire_guide_card_count_read": 22, "raw_html_sha256": None,
        "raw_html_custody": "UNAVAILABLE",
        "description_fingerprint_method": "RENDERED_WEB_READER_DESCRIPTION_TRIMMED_UTF8_NFC",
        "independent_source_families": 1,
    }
    for key, expected in exact_source.items():
        require(type(source[key]) is type(expected) and source[key] == expected,
                f"unreviewed source claim {key}")
    rows = observations["rows"]
    require(type(rows) is list and len(rows) == 17, "exact seventeen held cards required")
    accepted_directory = {row["row_id"]: row for row in directory["rows"]}
    require(len(accepted_directory) == 1214, "duplicate accepted discovery IDs")
    compiled = []
    for row, (suffix, ep, title, digest, mentions, paraphrase) in zip(rows, EXPECTED):
        row_id = f"legacy:s2:tng:{suffix}"
        exact_fields = ROW_FIELDS | ({DERIVATIVE_FIELD} if ep == 9 else set())
        require(type(row) is dict and set(row) == exact_fields,
                f"unreviewed card fields {row_id}")
        exact_row = {
            "row_id": row_id, "publisher_title": title, "season": 2, "episode": ep,
            "publisher_card_locator": f"Season 2 / {title} / S2 E{ep}",
            "rendered_description_sha256": digest,
            "literal_description_mentions": list(mentions),
            "original_short_paraphrase": paraphrase,
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "identity_hold": "NO_GLOBAL_WORK_IDENTITY_ASSERTED",
        }
        if ep == 9:
            exact_row[DERIVATIVE_FIELD] = DERIVATIVE_RELATION
        for key, expected in exact_row.items():
            require(type(row[key]) is type(expected) and row[key] == expected,
                    f"unreviewed publisher card claim {row_id} {key}")
        prior = accepted_directory.get(row_id)
        require(type(prior) is dict and prior.get("title") == title
                and prior.get("context") == f"TNG S2E{ep}"
                and prior.get("medium") == "EPISODE"
                and prior.get("candidate_kind") == "PUBLISHER_EPISODE_SLOT"
                and prior.get("source_group") == "publisher:paramount"
                and prior.get("source_input") == str(BUNDLE)
                and prior.get("source_locator") == GUIDE
                and prior.get("verification_status") == "UNVERIFIED_METADATA"
                and prior.get("coverage_effect") == "NONE"
                and prior.get("admission_effect") == "NONE",
                f"accepted local row changed {row_id}")
        compiled_row = {
            "source_local_row_id": row_id, "title": title,
            "publisher_card": {"guide_url": GUIDE, "season": 2, "episode": ep,
                               "rendered_description_sha256": digest,
                               "raw_webpage_sha256": None},
            "source_relative_mentions": list(mentions),
            "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
            "original_editorial_paraphrase_held": paraphrase,
            "synopsis_publication_status": "PENDING_EDITORIAL_AND_SOURCE_REVIEW",
            "global_work_identity": "UNRESOLVED", "source_custody": "NO_RAW_HTML_BYTES",
            "admission_effect": "NONE", "coverage_effect": "NONE",
        }
        if ep == 9:
            compiled_row["preexisting_derivative_source_relationship"] = {
                "relationship": DERIVATIVE_RELATION,
                "accepted_prior_manifest_sha256": INPUT_HASHES[DERIVATIVE],
                "corroboration_effect": "NONE",
                "source_authentication": "UNRESOLVED",
            }
        compiled.append(compiled_row)
    return {
        "schema_version": "1.0.0", "data_status": "HELD_TNG_S2_E6_TO_E22_PUBLISHER_METADATA",
        "accepted_catalog_sha256": INPUT_HASHES[CATALOG],
        "accepted_s2_csv_sha256": INPUT_HASHES[CSV],
        "accepted_s2_bundle_sha256": INPUT_HASHES[BUNDLE],
        "accepted_derivative_manifest_sha256": INPUT_HASHES[DERIVATIVE],
        "publisher_family": "paramount_corporate_publisher_family",
        "guide_url": GUIDE, "source_body_custody": "NOT_ESTABLISHED",
        "source_local_cards_enriched": 17, "new_works": 0,
        "independent_source_families": 1,
        "governed_research_admissions": 0,
        "coverage_effect": "NONE", "records": compiled,
    }


def render(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output = render(compile_held(read_json(HERE / "observations.json"), accepted_inputs()))
    target = HERE / "records.json"
    if args.check:
        require(target.is_file() and not target.is_symlink() and target.read_bytes() == output,
                "held TNG card projection stale")
    else:
        target.write_bytes(output)
    print("TNG-S2-B014-B015-HELD-PASS cards=17 independent_families=1 admissions=0")


if __name__ == "__main__":
    main()
