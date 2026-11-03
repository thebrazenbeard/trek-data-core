"""Fail-closed validation of the Prodigy derivative press-list metadata proposal.

This checks the committed structure and pinned locator receipts; it does not
authenticate an inaccessible Paramount original or grant copyright permissions.
"""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_ID = "pro-derivative-tvmeg-episode-guide-20261103"
SOURCE_URL = "https://tvmeg.com/index.php/2023/06/29/stpepguide/"
SOURCE_SHA = "e01541968cce29eccba2792b52299e718a36cc4880e1535d0b319737aa4a06bc"
PUBLISHER_SHA = "cdfa762fd65814d83c864072e1807c5ba5493e8d049845dc321661354225bea9"
LINE_HASHES = {
    500: "d661fc7770d609d5fee631f7104b3c1f9c27543ec174c23598aa8299cc7b59c2",
    501: "a755823c1b4cb3c537376475d66b81e6cdded332fc11a7e8f4106908420ebcd4",
    502: "2c1443c8dfdffab938ea8c4148c5de6938a5e1c6080f485e984845215a9dcf13",
    503: "8f81ac358757b941003f55180a11e6a4de980cb3e559fc6720165c280581ffc8",
}
SLOT_SEQUENCES = [[101, 102], [103], [104], [105]]
TITLES = ["Lost & Found", "Starstruck", "Dreamcatcher", "Terror Firma"]
DATES = ["Thursday, October 28th", "Thursday, November 4th", "Thursday, November 11th", "Thursday, November 18th"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_id_map(items, label):
    require(isinstance(items, list), f"{label} must be a list")
    result = {}
    for item in items:
        require(isinstance(item, dict) and isinstance(item.get("id"), str), f"bad {label} item")
        ident = item["id"]
        require(ident not in result, f"duplicate {label} id: {ident}")
        result[ident] = item
    return result


def validate_payload(data):
    require(isinstance(data, dict), "bundle must be an object")
    require(data.get("schema_version") == "1.0.0" and data.get("role") == "PRO",
            "unexpected schema/worker lane")
    require(data.get("proposal_only") is True, "proposal-only flag required")
    for flag in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "artwork_release_effect"):
        require(data.get(flag) == "NONE", f"research or artwork promoted: {flag}")
    for forbidden in ("briefings", "coverage_events", "global_identity_reconciliation", "licensed_artwork", "image_url", "image_path"):
        require(forbidden not in data, f"forbidden public release/admission field: {forbidden}")

    source = data.get("source")
    require(isinstance(source, dict) and source.get("id") == SOURCE_ID and source.get("url") == SOURCE_URL,
            "source identity changed")
    require(source.get("type") == "THIRD_PARTY_DERIVATIVE_PROMOTIONAL_EPISODE_GUIDE",
            "derivative source cannot become a primary film/episode witness")
    require(source.get("raw_html_bytes") == 121944 and source.get("raw_html_sha256") == SOURCE_SHA,
            "source receipt changed without review")
    require(source.get("body_physical_lines_read_inclusive") == [499, 519], "source read scope changed")
    require(source.get("http_status") == 200 and source.get("retrieved_date_utc") == "2026-11-03",
            "source retrieval receipt incomplete")
    require(source.get("original_press_page_verified") is False and source.get("primary_audiovisual_source_read") is False,
            "source verification or primary read fabricated")
    require(source.get("upstream_attribution_status") == "DERIVATIVE_SELF_REPORT_LINE_532",
            "derivative upstream attribution not preserved")
    require(source.get("independence_group") == "publisher:paramount-derivative-reproduction",
            "source dependence silently changed")
    require(source.get("copyrighted_source_text_committed") is False,
            "copyrighted source text cannot be shipped")

    boundary = data.get("first_party_boundary_check")
    require(isinstance(boundary, dict) and boundary.get("url") ==
            "https://www.startrek.com/news/star-trek-prodigy-season-1-volume-1-release",
            "first-party boundary locator changed")
    require(boundary.get("raw_html_bytes") == 1226890 and boundary.get("raw_html_sha256") == PUBLISHER_SHA,
            "first-party raw HTML receipt changed")
    require(boundary.get("scope") == "FIRST_TEN_EPISODES_VOLUME_EXISTENCE_ONLY" and
            boundary.get("provides_numbered_episode_roster") is False and
            boundary.get("independent_of_claimed_press_upstream") is False,
            "publisher boundary exceeded")

    works = unique_id_map(data.get("work_candidates"), "work")
    entities = unique_id_map(data.get("local_entities"), "entity")
    evidence = unique_id_map(data.get("evidence"), "evidence")
    assertions = unique_id_map(data.get("assertions"), "assertion")
    require(len(works) == len(entities) == len(evidence) == len(assertions) == 4,
            "this bounded tranche must have four line-bounded entries")
    require([item.get("printed_slot_labels") for item in data["work_candidates"]] == SLOT_SEQUENCES,
            "source 101/102 combined slot identity cannot be split or renumbered")
    require([item.get("display_title") for item in data["work_candidates"]] == TITLES,
            "source local titles changed")
    require(all(item.get("admission") == "UNRESOLVED" for item in works.values()),
            "local Work identity promoted")
    require(data["work_candidates"][0].get("part_statement") == "PART_1_AND_PART_2_IN_ONE_SOURCE_ENTRY",
            "combined premiere structure collapsed")
    require(all(item.get("part_statement") == "NO_SEPARATE_PART_STATEMENT"
                for item in data["work_candidates"][1:]), "invented part structure")

    for entity in entities.values():
        require(entity.get("type") == "SOURCE_LIST_ENTRY" and entity.get("candidate_work_id") in works,
                "entity lacks local Work candidate")
        require(entity.get("year_in_listing") is None, "source does not print year for individual list entries")
        require(isinstance(entity.get("writer_credit"), list) and entity["writer_credit"] and
                isinstance(entity.get("director_credit"), list) and entity["director_credit"],
                "missing production-credit observation")
    require(len({e["candidate_work_id"] for e in entities.values()}) == 4,
            "multiple source entries collapsed into one local Work")
    require([item.get("source_date_as_written") for item in data["local_entities"]] == DATES,
            "source-relative date labels changed or silently normalized")

    for item in evidence.values():
        line = item.get("raw_html_physical_line")
        require(item.get("source_id") == SOURCE_ID and item.get("local_entity_id") in entities,
                "evidence source/subject mismatch")
        require(item.get("kind") == "DERIVATIVE_LIST_ENTRY_TEXT" and
                LINE_HASHES.get(line) == item.get("raw_html_line_sha256"),
                "unrecognized source line/hash")
        require(isinstance(item.get("establishes"), str) and item["establishes"],
                "missing source-relative evidence meaning")
    require({v["raw_html_physical_line"] for v in evidence.values()} == set(LINE_HASHES),
            "missing or duplicated source paragraphs")

    used_evidence = set()
    for item in assertions.values():
        require(item.get("subject_local_entity_id") in entities and
                item.get("status") == "SOURCE_ATTRIBUTED_UNRESOLVED",
                "assertion claims global truth or lacks local subject")
        require(item.get("predicate") in {"SOURCE_PRINTS_COMBINED_SLOT_LABELS", "SOURCE_PRINTS_EPISODE_SLOT"},
                "unreviewed assertion predicate")
        refs = item.get("supporting_evidence_ids")
        require(isinstance(refs, list) and len(refs) == 1 and refs[0] in evidence,
                "assertion must cite one specific source line")
        require(evidence[refs[0]]["local_entity_id"] == item["subject_local_entity_id"],
                "assertion evidence points to a different entity")
        used_evidence.add(refs[0])
    require(used_evidence == set(evidence), "orphaned evidence")
    require(isinstance(data.get("review_challenges"), list) and len(data["review_challenges"]) >= 4,
            "missing hostile source-dependence and identity gates")
    return len(works)


if __name__ == "__main__":
    n = validate_payload(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print(f"PRO_DERIVATIVE_SOURCE_LOCAL_OK: {n} source entries; 5 printed slots; 0 admitted Works")
