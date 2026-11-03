"""Fail-closed source-local VOY regional-listing batch validator."""

import csv
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXPECTED_AU_SLOTS = {(5, 15), (5, 16), (7, 9), (7, 10), (7, 25), (7, 26)}
EXPECTED_AU_TITLES = {
    (5, 15): "Dark Frontier, Part 1", (5, 16): "Dark Frontier, Part 2",
    (7, 9): "Flesh & Blood, Part 1", (7, 10): "Flesh & Blood, Part 2",
    (7, 25): "Endgame Part 1", (7, 26): "Endgame Part 2",
}
SOURCE_HOSTS = {"www.paramountplus.com", "www.intl.paramountplus.com", "www.bbfc.co.uk"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def us_ordinals(season):
    folder = f"publisher-season{season}-20261102"
    path = REPO / "proposals" / "discovery" / folder / "voy.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    require(rows and all(int(row["season"]) == season for row in rows),
            "US source-local CSV season mismatch")
    return {int(row["episode_number"]) for row in rows}


def validate_payload(doc):
    require(doc.get("schema_version") == "1.0.0" and doc.get("role") == "VOY",
            "wrong batch type")
    require(doc.get("proposal_only") is True, "unreviewed batch cannot be admitted")
    for flag in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect", "denominator_effect"):
        require(doc.get(flag) == "NONE", f"unexpected promotion: {flag}")
    require(doc.get("full_av_or_transcript_read") is False, "false full-source claim")
    require(doc.get("raw_source_snapshots_archived") is False, "source snapshot not retained")
    coverage = doc.get("coverage_update", {})
    for key in ("events_added", "admitted_briefings", "source_bound_works_added", "full_text_available_added", "close_read_added"):
        require(coverage.get(key) == 0, f"unexpected coverage increment: {key}")
    require(coverage.get("denominator_status") == "DENOMINATOR_UNRESOLVED", "invented denominator")

    sources = doc.get("sources", [])
    source_ids = {s.get("id") for s in sources}
    require(source_ids == {"paramount-us-s5", "paramount-us-s7", "paramount-au-s5", "paramount-au-s7", "bbfc-voyager"},
            "source identity set drift")
    require(len(sources) == len(source_ids), "duplicate source")
    for source in sources:
        url = urlsplit(source.get("url", ""))
        require(url.scheme == "https" and url.hostname in SOURCE_HOSTS and not url.username and not url.password,
                "source URL origin invalid")
        require(source.get("new_raw_snapshot_digest") is None, "unheld snapshot digest invented")
        require(source.get("lineage_group") in {"PARAMOUNT_CBS_STUDIO", "BBFC_CLASSIFICATION_RECORD"},
                "invalid independence group")
        if source["id"].startswith("paramount-"):
            require(source["lineage_group"] == "PARAMOUNT_CBS_STUDIO", "regional mirror is not independent")

    entities = doc.get("local_entities", [])
    ids = {e.get("id") for e in entities}
    require(len(entities) == len(ids) == 6, "expected six distinct source-local entities")
    require({(e.get("season"), e.get("ordinal")) for e in entities} == EXPECTED_AU_SLOTS,
            "source-local ordinal set drift")
    for entity in entities:
        require(entity.get("source_id") == f"paramount-au-s{entity['season']}", "local entity wrong source")
        require(entity.get("display_title") == EXPECTED_AU_TITLES[(entity["season"], entity["ordinal"])],
                "publisher display title drift")

    evidence = doc.get("evidence", [])
    evidence_ids = {item.get("id") for item in evidence}
    require(len(evidence) == len(evidence_ids) == 10, "expected ten distinct evidence records")
    for item in evidence:
        require(item.get("source_id") in source_ids, "evidence source does not exist")
        require(item.get("local_entity_id") is None or item["local_entity_id"] in ids,
                "evidence references non-local entity")
        require(item.get("kind") in {"PUBLISHER_LISTING", "PUBLISHER_LISTING_ABSENCE", "REGULATOR_CLASSIFICATION_LISTING"},
                "evidence frame unrecognized")
        require(isinstance(item.get("locator"), str) and item["locator"], "missing evidence locator")
    require({e.get("local_entity_id") for e in evidence if e.get("kind") == "PUBLISHER_LISTING"} == ids,
            "not every Australian card has a source-relative evidence record")

    assertions = doc.get("assertions", [])
    assert_ids = {item.get("id") for item in assertions}
    require(len(assertions) == len(assert_ids) == 2, "expected two distinct proposed cases")
    for item in assertions:
        require(item.get("predicate") == "SOURCE_LISTING_DIFFERS_BY_REGION" and item.get("status") == "PROPOSED",
                "unauthorized reconciliation")
        require(item.get("evidence_ids") and set(item["evidence_ids"]).issubset(evidence_ids),
                "assertion has broken evidence references")
        require(item.get("counterevidence_search"), "missing counterevidence note")

    require(16 not in us_ordinals(5), "US Season 5 source gap no longer matches checked batch")
    require(10 not in us_ordinals(7) and 26 not in us_ordinals(7),
            "US Season 7 source gaps no longer match checked batch")
    print("VOY_REGION_SPLIT_OK: 6 Australian source-local listings, 10 evidence items, 2 unresolved comparison assertions; no admission")


if __name__ == "__main__":
    validate_payload(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
