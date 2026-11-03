"""Fail-closed validation for an unadmitted SNW publisher-description tranche."""

from datetime import datetime, timezone
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED = [
    (6, "Lost in Translation", "2023-07-20T02:00:00-07:00", [1639, 1651]),
    (7, "Those Old Scientists", "2023-07-22T18:45:00-07:00", [1667, 1679]),
    (8, "Under the Cloak of War", "2023-07-27T02:00:00-07:00", [1695, 1707]),
    (9, "Subspace Rhapsody", "2023-08-03T02:00:00-07:00", [1723, 1735]),
    (10, "Hegemony", "2023-08-10T02:00:00-07:00", [1751, 1763]),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_ids(records, field):
    ids = [row.get(field) for row in records]
    require(all(isinstance(value, str) and value for value in ids), f"missing {field}")
    require(len(ids) == len(set(ids)), f"duplicate {field}")
    return set(ids)


def validate_records(data):
    require(data.get("schema_version") == "1.0.0", "schema mismatch")
    require(data.get("lane") == "SNW", "wrong research partition")
    require(data.get("batch_id") == "SNW.PPLUS.S2.LAST5.20261103", "batch mismatch")
    require(data.get("proposal_only") is True, "candidate-only flag absent")
    for field in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(data.get(field) == "NONE", f"unapproved effect: {field}")
    require(data.get("audiovisual_content_inspected") is False, "unsupported primary AV read")
    require(data.get("full_primary_source_available") is False, "unsupported full source claim")

    source = data.get("source", {})
    require(source.get("source_local_id") == "snw-s2-paramount-guide-20261103", "wrong source id")
    require(source.get("url") == "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/2/", "wrong source locator")
    require(source.get("kind") == "PUBLISHER_EPISODE_GUIDE_HTML", "unexpected source kind")
    require(source.get("independence_group") == "publisher:paramountplus.com", "source independence inflated")
    require(source.get("response_status") == 200, "source was not retrieved successfully")
    require(source.get("response_body_bytes") == 273092, "source-size receipt mismatch")
    require(source.get("response_sha256") == "b8665d256eeee7bb4bb148c6c2d4389ebcdfd1cc398fd36c05bd567ee598cc32", "source digest mismatch")
    require(source.get("snapshot_committed") is False, "source bytes must remain private")
    require(source.get("publisher_revision") is None, "unverified revision")

    works = data.get("works")
    evidence = data.get("evidence")
    assertions = data.get("assertions")
    entities = data.get("local_entities")
    require(all(isinstance(x, list) for x in (works, evidence, assertions, entities)), "missing research arrays")
    require(len(works) == len(evidence) == len(assertions) == 5, "five-card tranche required")
    work_ids = unique_ids(works, "local_work_id")
    evidence_ids = unique_ids(evidence, "evidence_id")
    unique_ids(assertions, "assertion_id")
    entity_ids = unique_ids(entities, "local_entity_id")

    for actual, expected in zip(works, EXPECTED):
        num, title, instant, lines = expected
        require(actual.get("local_work_id") == f"snw-s2-e{num:02d}-pplus", "wrong work-local id")
        require(actual.get("season") == 2 and actual.get("episode_number") == num, "wrong season/ordinal")
        require(actual.get("title") == title, "wrong publisher title")
        require(actual.get("source_datetime") == instant, "publisher timestamp changed")
        require(actual.get("card_html_lines") == lines, "page locator lost")
        require(actual.get("canonical_work_id") is None and actual.get("source_binding_id") is None, "premature accepted identity")
        require(datetime.fromisoformat(instant).utcoffset() is not None, "naive publisher timestamp")

    # July 22 at -07:00 represents July 23 UTC. This must not be silently
    # normalized into a contradiction or a fictional-world date.
    require(datetime.fromisoformat(works[1]["source_datetime"]).astimezone(timezone.utc).date().isoformat() == "2023-07-23", "S2E7 timezone edge case")

    entity_map = {row["local_entity_id"]: row for row in entities}
    for entity in entities:
        require(entity.get("work_id") in work_ids, "orphan local entity")
        require(entity.get("global_entity_id") is None, "global identity leak")
        require(entity.get("kind") in ("PERSON_MENTION", "VESSEL_MENTION"), "unsupported local entity type")
        require(isinstance(entity.get("label"), str) and entity["label"], "missing entity label")
    evidence_map = {row["evidence_id"]: row for row in evidence}
    for row in evidence:
        require(row.get("work_id") in work_ids, "orphan evidence")
        require(row.get("source_local_id") == source["source_local_id"], "unlinked source")
        require(row.get("kind") == "PUBLISHER_DESCRIPTION", "publisher claim promoted to depiction")
        require(row.get("observation_scope") == "PUBLISHER_TEXT_ONLY", "primary content falsely claimed")
        require(isinstance(row.get("locator"), str) and "HTML lines" in row["locator"], "missing source locator")
        require(isinstance(row.get("paraphrase"), str) and 30 <= len(row["paraphrase"]) <= 260, "missing or excessive paraphrase")
        require("<" not in row["paraphrase"], "raw markup in analysis")

    for row in assertions:
        require(row.get("work_id") in work_ids, "orphan assertion")
        require(row.get("evidence_id") in evidence_ids, "assertion without evidence")
        require(evidence_map[row["evidence_id"]]["work_id"] == row["work_id"], "cross-work evidence leak")
        require(row.get("predicate") == "PUBLISHER_SUMMARY_MENTIONS", "fictional fact falsely asserted")
        require(row.get("status") == "SOURCE_RELATIVE_UNVERIFIED_EPISODE_CONTENT", "unverified status promoted")
        refs = row.get("local_entity_ids")
        require(isinstance(refs, list) and len(refs) > 0, "assertion lacks local entities")
        for ref in refs:
            require(ref in entity_ids and entity_map[ref]["work_id"] == row["work_id"], "cross-work entity leak")

    limits = data.get("counterevidence_and_limits")
    require(isinstance(limits, list) and {x.get("kind") for x in limits} == {"NOT_INDEPENDENT", "UNINSPECTED_PRIMARY_AV", "TIMEZONE_EDGE_CASE"}, "limits omitted")
    return len(works)


if __name__ == "__main__":
    count = validate_records(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print(f"SNW_PUBLISHER_SOURCE_CHECKED: {count} source-local publisher descriptions, no admitted coverage")
