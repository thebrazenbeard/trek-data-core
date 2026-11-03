"""Validate seven non-admitting, source-local Voyager B007 publisher cards."""

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CATALOG = ROOT / "explorer/discovery-catalog.json"
EXPECTED = (
    ("lead:0083", "Juggernaut", 5, 21, "EXACT", "Q16744043"),
    ("lead:0084", "Infinite Regress", 5, 7, "EXACT", "Q16744066"),
    ("lead:0085", "Natural Law", 7, 22, "EXACT", "Q16744191"),
    ("lead:0086", "Human Error", 7, 18, "EXACT", "Q16744675"),
    ("lead:0087", "Basics, Part 2", 3, 1, "ROMAN_NUMERAL_VARIANT_UNRESOLVED", "Q25587669"),
    ("lead:0088", "Future's End, Part 2", 3, 9, "ROMAN_NUMERAL_VARIANT_UNRESOLVED", "Q25587671"),
    ("lead:0089", "Year Of Hell, Part 2", 4, 9, "NUMERAL_AND_CASE_VARIANT_UNRESOLVED", "Q25587679"),
)
ROOT_FIELDS = {
    "proposal_id", "baseline_accepted_main", "role", "observed_date_utc", "proposal_only",
    "accepted_corpus_effect", "source_family", "source_representation",
    "raw_http_response_sha256", "source_body_read", "publisher_blurbs_reproduced",
    "artwork_bytes_retrieved", "catalog_snapshot", "candidate_rows", "summary",
}
ROW_FIELDS = {"row_id", "source_local_qid_url", "official_title", "season", "episode", "guide_url", "title_status", "brief_description_read"}


def require(test, reason):
    if not test:
        raise ValueError(reason)


def validate(data, catalog_bytes):
    require(isinstance(data, dict) and set(data) == ROOT_FIELDS, "unreviewed proposal payload")
    require(data["proposal_id"] == "LIBRARIAN-VOY-B007-RENDERED-GUIDE-CARDS-20261103", "wrong proposal identity")
    require(data["baseline_accepted_main"] == "3c0b37564123166bf38bcfa66f018abc4d5c9996", "wrong baseline")
    require(data["role"] == "LIBRARIAN" and data["observed_date_utc"] == "2026-11-03", "wrong role or observation date")
    require(data["proposal_only"] is True and data["accepted_corpus_effect"] == "NONE", "unexpected admission")
    require(data["source_family"] == "paramount_corporate_publisher_family", "wrong publisher independence family")
    require(data["source_representation"] == "RENDERED_FIRST_PARTY_PARAMOUNT_PLUS_SEASON_GUIDE_CARDS_NOT_SOURCE_BODY", "false source representation")
    for name, value in (("raw_http_response_sha256", None), ("source_body_read", False),
                        ("publisher_blurbs_reproduced", False), ("artwork_bytes_retrieved", False)):
        require(data[name] is value, "unsupported source text/media custody")
    gap = data["catalog_snapshot"]
    require(set(gap) == {"path", "sha256", "row_count"}, "unreviewed catalog snapshot")
    require(gap["path"] == "explorer/discovery-catalog.json", "wrong catalog path")
    require(gap["sha256"] == "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc", "unreviewed catalog hash")
    require(hashlib.sha256(catalog_bytes).hexdigest() == gap["sha256"], "catalog byte hash changed")
    catalog = json.loads(catalog_bytes)
    require(catalog.get("data_status") == "DISCOVERY_ONLY" and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery catalog admitted")
    require(catalog["row_count"] == len(catalog["rows"]) == gap["row_count"] == 1214, "catalog size drift")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    require(len(by_id) == 1214, "duplicate source IDs")
    rows = data["candidate_rows"]
    require(isinstance(rows, list) and len(rows) == len(EXPECTED), "unreviewed B007 tranche size")
    used = set()
    for row, (ident, title, season, episode, status, qid) in zip(rows, EXPECTED):
        require(isinstance(row, dict) and set(row) == ROW_FIELDS, "unreviewed narrative or art payload")
        require(row["row_id"] == ident, "wrong source lead order")
        source = by_id[ident]
        require(source["context"] == "VOY" and source["medium"] == "EPISODE"
                and source["source_group"] == "wikidata:wdqs"
                and source["candidate_kind"] == "WIKIDATA_EPISODE"
                and source["verification_status"] == "UNVERIFIED_METADATA"
                and source["admission_effect"] == "NONE" and source["coverage_effect"] == "NONE", "source-lineage drift")
        require(row["source_local_qid_url"] == source["source_locator"] == f"https://www.wikidata.org/wiki/{qid}", "wrong QID crosswalk locator")
        require(row["official_title"] == title and type(row["season"]) is int and row["season"] == season
                and type(row["episode"]) is int and row["episode"] == episode, "wrong official card title/slot")
        require((season, episode) not in used, "duplicated official card slot")
        used.add((season, episode))
        require(row["guide_url"] == f"https://www.paramountplus.com/shows/star_trek_voyager/episodes/{season}/", "wrong official guide")
        require(row["title_status"] == status, "unreviewed identity status change")
        if status == "EXACT":
            require(source["title"] == title, "false exact title")
        else:
            require(source["title"] != title, "suppressed identity ambiguity")
        require(row["brief_description_read"] is True, "official card unread")
    require(data["summary"] == {
        "source_local_leads_inspected": 7, "official_rendered_cards_read": 7,
        "exact_publisher_titles": 4, "unresolved_numeral_variants": 2,
        "unresolved_numeral_and_case_variants": 1, "approved_synopses": 0,
        "accepted_work_bindings": 0, "coverage_events": 0,
    }, "unreviewed source-relative accounting or coverage")
    return len(rows)


if __name__ == "__main__":
    print("VOY_B007_SOURCE_LOCAL_OK:", validate(
        json.loads((HERE / "records.json").read_text(encoding="utf-8")), CATALOG.read_bytes()))
