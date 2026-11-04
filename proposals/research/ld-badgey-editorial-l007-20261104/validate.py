"""Fail-closed validation of held Badgey publisher-editorial source boundaries.

This validates an exact locally reviewed fixture, NOT the external pages'
truth, their continued availability, or full audiovisual episode coverage.
No `assert`: checks must survive `python -O`.
"""

import copy
import hashlib
import json
from pathlib import Path


FIXTURE_DIGEST = "176c645c9a50d1bc467eac2a59c1a3cd3bcb2f503e9347ba7bd80093961c8232"
MAIN_AT_SELECTION = "3028765359001b90bc3e6b5c1835ee283b326e91"
PR_HEAD_AT_INSPECTION = "dd858712a31319aecc3bde67e0f7dcaf1900f776"

TOP_KEYS = {
    "packet_id", "role", "accepted_main_at_selection", "observed_date_utc", "scope",
    "source_receipts", "source_lineage", "source_local_work_locators", "local_entities",
    "source_relative_evidence", "typed_assertions", "alternate_fiction_premise",
    "non_inferences", "full_episode_read", "source_work_admission",
    "semantic_canon_assertions", "new_coverage_events", "global_reconciliation_effect",
    "public_media_effect", "projection_effect", "status",
}
SOURCE_KEYS = {
    "local_source_id", "url", "title", "byline", "publisher", "publication_date_display",
    "kind", "sections_inspected", "source_read_extent", "raw_html_digest",
    "episode_audio_visual_access", "copyright_republication_rights",
}
SOURCE_CONTRACT = {
    "l007-s01": (
        "https://www.startrek.com/news/star-trek-megalomaniacal-ai-guide",
        "A Who's Who Guide to Star Trek's Megalomaniacal AI", "Christine Dinh",
        "2023-10-23", ["Badgey", "AGIMUS", "Peanut Hamper"],
    ),
    "l007-s02": (
        "https://www.startrek.com/news/below-deck-lower-decks-407-good-badge-and-ugly",
        "Below Deck with Lower Decks: The Good, the Badge, and the Ugly", "Dayton Ward",
        "2023-10-13", ["S4E7 episode discussion", "Daystrom subplot", "Badgey subplot"],
    ),
}
ENTITY_CONTRACT = {
    "l007-badgey": "Badgey", "l007-goodgey": "Goodgey", "l007-logicy": "Logic-y",
    "l007-rutherford": "Sam Rutherford", "l007-agimus": "AGIMUS",
    "l007-peanut-hamper": "Peanut Hamper",
}
EVIDENCE_CONTRACT = {
    "l007-e01": ("l007-s01", "Badgey / origin paragraph", ["l007-badgey", "l007-rutherford"], "PUBLISHER_EDITORIAL_CHARACTER_DESCRIPTION_NOT_DIRECT_EPISODE_OBSERVATION"),
    "l007-e02": ("l007-s01", "Badgey / reconciliation and segmentation paragraph", ["l007-badgey", "l007-goodgey", "l007-logicy", "l007-rutherford"], "PUBLISHER_EDITORIAL_PLOT_DESCRIPTION_NOT_DIRECT_EPISODE_OBSERVATION"),
    "l007-e03": ("l007-s01", "Badgey / final two paragraphs", ["l007-badgey"], "PUBLISHER_EDITORIAL_PLOT_DESCRIPTION_NOT_DIRECT_EPISODE_OBSERVATION"),
    "l007-e04": ("l007-s01", "AGIMUS / imprisonment and later Daystrom paragraphs", ["l007-agimus", "l007-peanut-hamper"], "PUBLISHER_EDITORIAL_DETAINEE_DESCRIPTION_NOT_BADGEY_IDENTITY"),
    "l007-e05": ("l007-s01", "Peanut Hamper / incarceration paragraph", ["l007-peanut-hamper", "l007-agimus"], "PUBLISHER_EDITORIAL_DETAINEE_DESCRIPTION_NOT_BADGEY_IDENTITY"),
    "l007-e06": ("l007-s02", "S4E7 opening Daystrom subplot and Badgey subplot", ["l007-badgey", "l007-agimus", "l007-peanut-hamper"], "SAME_PUBLISHER_EDITORIAL_STORYLINE_DISTINCTION"),
    "l007-e07": ("l007-s02", "S4E7 Badgey metamorphosis paragraph", ["l007-badgey"], "SAME_PUBLISHER_EDITORIAL_STORYLINE_DESCRIPTION"),
}
ASSERTION_CONTRACT = {
    "l007-a01": ("PUBLISHER_EDITORIAL_DESCRIBES_CHARACTER_ORIGIN", ["l007-e01"]),
    "l007-a02": ("PUBLISHER_EDITORIAL_DESCRIBES_CHARACTER_SEGMENTATION", ["l007-e02"]),
    "l007-a03": ("PUBLISHER_EDITORIAL_DESCRIBES_CHARACTER_DEPARTURE", ["l007-e03", "l007-e07"]),
    "l007-a04": ("PUBLISHER_EDITORIAL_IDENTIFIES_DAYSTROM_DETAINEES", ["l007-e04", "l007-e05", "l007-e06"]),
}
DAYSTROM_OBSERVATION_CONTRACT = {
    "l007-e04": "The editorial names AGIMUS as sentenced to the Daystrom computer-storage facility and describes meeting Peanut Hamper there.",
    "l007-e05": "The editorial separately describes Peanut Hamper being taken to Daystrom and held next to AGIMUS.",
    "l007-e06": "A second official franchise editorial places the AGIMUS/Peanut Hamper story in a Daystrom setting and separately describes Badgey's return through a recovered implant.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected, label):
    require(type(value) is dict, f"{label} must be an object")
    require(set(value) == expected, f"{label} keys differ: {set(value) ^ expected}")


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def indexed(items, id_key, expected_ids, label):
    require(type(items) is list and len(items) == len(expected_ids), f"{label} count")
    found = {}
    for item in items:
        require(type(item) is dict and type(item.get(id_key)) is str, f"{label} ID")
        ident = item[id_key]
        require(ident not in found, f"duplicate {label} ID {ident}")
        found[ident] = item
    require(set(found) == expected_ids, f"{label} IDs differ")
    return found


def validate(data):
    keys(data, TOP_KEYS, "receipt")
    require(data["packet_id"] == "ld-badgey-editorial-l007-20261104", "packet ID")
    require(data["role"] == "LD" and data["scope"] == "HELD_FIRST_PARTY_PUBLISHER_EDITORIAL_ANALYSIS", "scope")
    require(data["accepted_main_at_selection"] == MAIN_AT_SELECTION, "main SHA")
    require(data["observed_date_utc"] == "2026-11-04", "date")
    require(data["status"] == "HELD_EDITORIAL_BOUNDARY_FIXTURE", "held status")

    sources = indexed(data["source_receipts"], "local_source_id", set(SOURCE_CONTRACT), "source")
    for source_id, expected in SOURCE_CONTRACT.items():
        row = sources[source_id]
        keys(row, SOURCE_KEYS, f"source {source_id}")
        require((row["url"], row["title"], row["byline"], row["publication_date_display"], row["sections_inspected"]) == expected, f"source binding {source_id}")
        require(row["kind"] == "FIRST_PARTY_PUBLISHER_EDITORIAL" and row["publisher"] == "StarTrek.com", f"source kind {source_id}")
        require(row["source_read_extent"] == "TARGETED_SECTIONS_READ_NOT_FULL_EPISODE", f"read extent {source_id}")
        require(row["episode_audio_visual_access"] == "NONE" and row["raw_html_digest"] is None, f"source access {source_id}")
        require(row["copyright_republication_rights"] == "NOT_ESTABLISHED", f"source rights {source_id}")

    keys(data["source_lineage"], {"publisher_family", "independent_episode_witnesses", "same_publisher_editorials_are_independent_primary_episode_witnesses"}, "lineage")
    require(data["source_lineage"] == {
        "publisher_family": "StarTrek.com official franchise editorial",
        "independent_episode_witnesses": 0,
        "same_publisher_editorials_are_independent_primary_episode_witnesses": False,
    }, "source lineage must not double-count publisher articles")
    works = data["source_local_work_locators"]
    require(type(works) is list and len(works) == 2, "work locators")
    require(works == [
        {"title": "Terminal Provocations", "series": "Star Trek: Lower Decks", "season_episode": "S1E6", "admitted_work_id": None},
        {"title": "A Few Badgeys More", "series": "Star Trek: Lower Decks", "season_episode": "S4E7", "admitted_work_id": None},
    ], "work locators must remain unadmitted")
    entities = indexed(data["local_entities"], "local_id", set(ENTITY_CONTRACT), "local entity")
    for ident, label in ENTITY_CONTRACT.items():
        keys(entities[ident], {"local_id", "source_label", "global_identity"}, f"entity {ident}")
        require(entities[ident]["source_label"] == label and entities[ident]["global_identity"] is None, f"entity mapping {ident}")

    evidence = indexed(data["source_relative_evidence"], "evidence_id", set(EVIDENCE_CONTRACT), "evidence")
    for ident, expected in EVIDENCE_CONTRACT.items():
        item = evidence[ident]
        keys(item, {"evidence_id", "source_id", "section_locator", "local_entity_ids", "observation", "establishes"}, f"evidence {ident}")
        require((item["source_id"], item["section_locator"], item["local_entity_ids"], item["establishes"]) == expected, f"evidence binding {ident}")
        require(type(item["observation"]) is str and item["observation"].strip(), f"observation text {ident}")
        if ident in DAYSTROM_OBSERVATION_CONTRACT:
            require(item["observation"] == DAYSTROM_OBSERVATION_CONTRACT[ident], f"Daystrom scope was rewritten: {ident}")

    assertions = indexed(data["typed_assertions"], "assertion_id", set(ASSERTION_CONTRACT), "typed assertion")
    for ident, expected in ASSERTION_CONTRACT.items():
        item = assertions[ident]
        keys(item, {"assertion_id", "candidate_predicate", "support", "status"}, f"assertion {ident}")
        require((item["candidate_predicate"], item["support"]) == expected, f"assertion support mismatch {ident}")
        require(item["status"] == "HELD_SOURCE_RELATIVE_ONLY", f"assertion admission {ident}")

    overlay = data["alternate_fiction_premise"]
    keys(overlay, {"description", "provenance", "does_not_follow_from_source_evidence", "not_a_global_canon_assertion", "draft_pr_inspection"}, "fiction overlay")
    require(overlay["provenance"] == "USER_DIRECTED_UNOFFICIAL_FICTION", "fiction provenance")
    require(overlay["does_not_follow_from_source_evidence"] is True and overlay["not_a_global_canon_assertion"] is True, "fiction boundary")
    pr = overlay["draft_pr_inspection"]
    keys(pr, {"pull_request_url", "head_sha_at_inspection", "inspected_file", "observed_disclosure_scope"}, "draft PR")
    require(pr == {
        "pull_request_url": "https://github.com/thebrazenbeard/trek-data-core/pull/486",
        "head_sha_at_inspection": PR_HEAD_AT_INSPECTION,
        "inspected_file": "explorer/index.html",
        "observed_disclosure_scope": "UNOFFICIAL_INVENTED_CONTAINMENT_NOT_CANON",
    }, "PR disclosure identity")

    require(type(data["non_inferences"]) is list and len(data["non_inferences"]) == 4, "non-inference guardrails")
    require(data["full_episode_read"] is False and data["source_work_admission"] == "NONE", "episode admission")
    require(data["semantic_canon_assertions"] == [] and data["new_coverage_events"] == [], "no canon/coverage effects")
    for field in ("global_reconciliation_effect", "public_media_effect", "projection_effect"):
        require(data[field] == "NONE", f"forbidden effect: {field}")

    # A frozen canonical fixture digest catches arbitrary claim drift, including
    # rephrased observations unrelated to the three Daystrom-specific checks.
    frozen = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    require(hashlib.sha256(frozen).hexdigest() == FIXTURE_DIGEST, "reviewed fixture digest mismatch")


def negative_cases(record):
    mutations = [
        lambda d: d["source_relative_evidence"][3]["local_entity_ids"].append("l007-badgey"),
        lambda d: d["source_relative_evidence"][3].update(observation="The editorial says Badgey was incarcerated at Daystrom."),
        lambda d: d["source_receipts"][0].update(url="https://example.invalid/false-article"),
        lambda d: d.update(full_copyrighted_transcript="UNVERIFIED_SENTINEL"),
        lambda d: d["typed_assertions"][0].update(support=["l007-e04"]),
        lambda d: d.update(full_episode_read=True),
        lambda d: d["source_lineage"].update(independent_episode_witnesses=2),
        lambda d: d["typed_assertions"][0].update(status="ACCEPTED_CANON"),
        lambda d: d["alternate_fiction_premise"].update(does_not_follow_from_source_evidence=False),
        lambda d: d["new_coverage_events"].append({"work": "invented"}),
    ]
    for index, mutation in enumerate(mutations, 1):
        invalid = copy.deepcopy(record)
        mutation(invalid)
        try:
            validate(invalid)
        except ValueError:
            continue
        raise ValueError(f"hostile mutation {index} was not rejected")
    return len(mutations)


if __name__ == "__main__":
    path = Path(__file__).with_name("observations.json")
    record = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    validate(record)
    count = negative_cases(record)
    try:
        json.loads('{"injected":1,"injected":2}', object_pairs_hook=unique_pairs)
    except ValueError:
        pass
    else:
        raise ValueError("duplicate-key hostile mutation was not rejected")
    print(f"LD L007 PUBLISHER EDITORIAL BOUNDARY: VALID; {count + 1} hostile mutations rejected")
