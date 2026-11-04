"""Deterministic SFA publisher/WDQS difference audit with fail-closed holds.

Only checks accepted repository documentary/metadata evidence and a stacked,
unaccepted SFA route proposal. It does not authenticate private WDQS responses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

INPUT_DIGESTS = {
    "proposals/research/sfa-publisher-video-routes-20261104/records.json": "734e5744de1deaa80a3f9cb81cdb7b1893616e6952931b9250a2ceb3f9a56975",
    "proposals/librarian/sfa-publisher-roster-20261102/bundle.json": "be92c853c5d3c59b0b13810e2a5c9848bc473f8e0c16c77d05e15f785b5b07de",
    "proposals/research/sfa-publisher-refresh-20261103/records.json": "e6965602a534a5976a371501b457eb91aa5e9375302fdc62c99a42fd9a4136d3",
    "proposals/discovery/wikidata-mission-samples-20261102/nextgen/receipts/sfa.json": "cdbb144913f65495f2857aa897fbcb30a405377e2d45a1e57a382e9d0de1747b",
    "proposals/discovery/wikidata-ent-sfa-second-pass-20261102/receipts/sfa.json": "c75e76c4ad355dbffdf8035b3da3198b1bc9fd2a62b66cde9447ef3226398822",
    "proposals/discovery/wikidata-ent-sfa-second-pass-20261102/REVIEW_HOLDS.json": "22558857b49f2ef82fd9d8eb3a54707ef69c4e5acee73d931655df6bc0726775",
}
ROUTE, ROSTER, PRESS, WD_TYPED, WD_SIMPLE, HOLDS = INPUT_DIGESTS
REPORT_DIGESTS = {
    "proposals/discovery/wikidata-mission-samples-20261102/nextgen/RESEARCH_RECORD.md": "cd2b08147288f4c3252b077e98db7497bbacc9ccc5b3cc1627b78b3882ee0c6d",
    "proposals/discovery/wikidata-ent-sfa-second-pass-20261102/RESEARCH_RECORD.md": "b6e21bb17de3364c40f61e60d658cec112a0111c9c51f77aa8ddae1f0ec7d8a8",
}
TOP_KEYS = {
    "schema_version", "audit_id", "role", "status", "basis_accepted_main",
    "basis_unaccepted_local_route_commit", "effects", "evidence_classes",
    "lineage", "comparison_rows", "negative_or_ambiguous_evidence",
}


def check(predicate: bool, reason: str) -> None:
    if not predicate:
        raise ValueError(reason)


def read_sources() -> dict[str, dict]:
    sources: dict[str, dict] = {}
    for path, expected_digest in INPUT_DIGESTS.items():
        raw = (ROOT / path).read_bytes()
        check(hashlib.sha256(raw).hexdigest() == expected_digest, f"drifted upstream source {path}")
        sources[path] = json.loads(raw)
    # The raw WDQS response bytes are absent. The reported zero rows must be
    # anchored in accepted documentary records, not inferred from a receipt.
    for path, expected_digest in REPORT_DIGESTS.items():
        raw = (ROOT / path).read_bytes()
        check(hashlib.sha256(raw).hexdigest() == expected_digest, f"drifted WDQS research report {path}")
        document = raw.decode("utf-8")
        if "nextgen/" in path:
            check("Starfleet Academy | Q134592591 | 200 | **0**" in document, "missing typed-zero report")
        else:
            check("E2-SFA / confirmatory / FAIL to yield candidates" in document and "empty `bindings` list" in document, "missing simple-zero report")
    return sources


def validate(data: dict, sources: dict[str, dict]) -> None:
    check(type(data) is dict and set(data) == TOP_KEYS, "crosswalk field boundary")
    check(data["schema_version"] == "1.0.0", "schema")
    check(data["audit_id"] == "SFA-PUBLISHER-WDQS-DIFF-20261104-001", "audit identity")
    check(data["role"] == "SFA" and data["status"] == "HELD_COMPARISON_PROPOSAL", "held SFA only")
    check(data["basis_accepted_main"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "accepted main basis")
    check(data["basis_unaccepted_local_route_commit"] == "bef9925", "unaccepted dependency must be explicit")
    check(data["effects"] == {
        "accepted_work": "NONE", "source_work_binding": "NONE", "coverage": "NONE",
        "episode_denominator": "NONE", "reconciliation": "NONE", "public_projection": "NONE",
    }, "no accepted effects")
    check(data["evidence_classes"] == {
        "publisher": "DIRECT_HTML_METADATA_RETRIEVAL_NOT_AV_CONTENT",
        "wikidata": "SECONDARY_ACCEPTED_RESEARCH_RECORDS_OF_ZERO_RESULT_NOT_RAW_RESPONSE_REPLAY",
        "redirect": "ACCEPTED_REVIEW_HOLD_NOT_NEW_QID_QUERY",
    }, "evidence class separation")

    route = sources[ROUTE]
    roster = sources[ROSTER]
    press = sources[PRESS]
    wd_typed = sources[WD_TYPED]
    wd_simple = sources[WD_SIMPLE]
    holds = sources[HOLDS]
    check(route["disposition"] == "HELD_PUBLISHER_SOURCE_ROUTE_METADATA", "upstream route hold")
    check(route["accepted_source_binding_effect"] == "NONE" and route["audiovisual_content_inspected"] is False, "upstream no media")
    check(roster["proposal_status"] == "CANDIDATE_METADATA_ONLY" and roster["denominator_effect"] == "NONE", "roster not accepted")
    check(press["status"] == "PROPOSAL_ONLY_PUBLISHER_METADATA" and press["coverage_effect"] == "NONE", "press not close-read")
    check(all(x["independence_group"] == "publisher:paramount" for x in press["source_snapshots"]), "press same publisher family")
    check(route["source_observation"]["independence_group"] == "publisher:paramount", "route same publisher family")

    for receipt, expected_snapshot in ((wd_typed, "WDQS-SFA-Q134592591-20261102-LIMIT20-001"),
                                       (wd_simple, "WDQS-SFA-Q134592591-SIMPLE-P179-20261102-LIMIT20-001")):
        check(receipt["snapshot_id"] == expected_snapshot, "historical WDQS receipt")
        check(receipt["source_url"] == "https://query.wikidata.org/sparql", "WDQS identity")
        check("wd:Q134592591" in receipt["query_text"] and "wd:Q117350388" not in receipt["query_text"], "queried obsolete QID")
    check("wdt:P31/wdt:P279*" in wd_typed["query_text"], "typed query constraint")
    check("wdt:P31/wdt:P279*" not in wd_simple["query_text"], "simple query constraint")
    identity_holds = holds["series_identity_holds"]
    check(len(identity_holds) == 1, "one SFA redirect hold")
    check(identity_holds[0]["queried_series_qid"] == "Q134592591" and identity_holds[0]["current_target_qid"] == "Q117350388", "QID redirection")
    check(holds["canonical_admission_effect"] == "NONE", "no canonical resolution")

    check(data["lineage"] == [
        {"source":"Paramount+ episode guide HTML","independence_group":"publisher:paramount","contributes":"exact displayed S1 title, ordinal, video path, datetime"},
        {"source":"Paramount Press Express episode listing","independence_group":"publisher:paramount","contributes":"source-local press codes and non-episode promotional bucket counterexamples"},
        {"source":"Wikidata WDQS queries","independence_group":"thirdparty:wikidata","contributes":"two reported zero-result historical queries against redirected Q134592591; no comparable episode rows"},
    ], "lineage classification")

    rows = data["comparison_rows"]
    observed_routes = route["publisher_page_route_observations"]
    accepted_slots = roster["episode_slots"]
    check(type(rows) is list and len(rows) == len(observed_routes) == len(accepted_slots) == 10, "ten paired publisher rows")
    for i, (row, candidate_route, candidate_slot) in enumerate(zip(rows, observed_routes, accepted_slots, strict=True), start=1):
        check(type(row) is dict and set(row) == {
            "publisher_route_id", "season", "episode", "publisher_title", "publisher_roster_alignment",
            "wikidata_episode_qid", "wikidata_title", "wikidata_alignment",
        }, f"row fields {i}")
        check((row["publisher_route_id"], row["season"], row["episode"], row["publisher_title"]) == (
            candidate_route["id"], candidate_route["season"], candidate_route["episode_number"], candidate_route["displayed_title"]
        ), f"source-relative route row {i}")
        check((row["season"], row["episode"], row["publisher_title"]) == (
            candidate_slot["season"], candidate_slot["episode_number"], candidate_slot["title"]
        ), f"publisher slot exact alignment {i}")
        check(row["publisher_roster_alignment"] == "EXACT", "publisher alignment label")
        check(row["wikidata_episode_qid"] is None and row["wikidata_title"] is None, "do not fabricate WDQS candidate")
        check(row["wikidata_alignment"] == "UNTESTABLE_NO_COMPARABLE_ROWS", "no false Wikidata mismatch")

    evidence = data["negative_or_ambiguous_evidence"]
    check(type(evidence) is list and len(evidence) == 7, "bounded adversarial observations")
    by_id = {entry["id"]: entry for entry in evidence}
    check(len(by_id) == 7, "unique anomaly identity")
    check(set(by_id) == {
        "wdqs-typed-zero-obsolete-qid", "wdqs-simple-zero-obsolete-qid", "wdqs-redirect",
        "press-s2-early-release", "press-s1-early-images", "publisher-label-05", "publisher-label-10",
    }, "expected anomaly types")
    for name, receipt in (("wdqs-typed-zero-obsolete-qid", wd_typed), ("wdqs-simple-zero-obsolete-qid", wd_simple)):
        item = by_id[name]
        check(item == {
            "id": name, "class": "HISTORICAL_ZERO_QUERY", "receipt": receipt["snapshot_id"],
            "queried_series_qid": "Q134592591", "reported_binding_count": 0,
            "interpretation": "NO_COMPARABLE_ROWS_FOR_EXACT_QUERY_NOT_ABSENCE_OF_EPISODES",
        }, f"historical no-row query {name}")
    check(by_id["wdqs-redirect"] == {
        "id":"wdqs-redirect","class":"SOURCE_IDENTITY_HOLD", "queried_series_qid":"Q134592591",
        "observed_redirect_target":"Q117350388","corrected_qid_query_executed_in_this_audit":False,
        "interpretation":"NO_CURRENT_QID_RESULT_AVAILABLE_FOR_ALIGNMENT",
    }, "QID redirection not resolution")
    media = {x["id"]: x for x in press["local_entities"] if x["kind"] == "PUBLISHER_MEDIA_BUCKET"}
    check(set(media) == {"sfa-press-20261103-s2-promotional", "sfa-press-20261103-s1-promotional"}, "press has two buckets")
    for audit_id, source_id, code, cls in (
        ("press-s2-early-release", "sfa-press-20261103-s2-promotional", "200", "MEDIA_BUCKET_NOT_ADMITTED_S2_EPISODE"),
        ("press-s1-early-images", "sfa-press-20261103-s1-promotional", "Multiple", "MEDIA_BUCKET_NOT_ADMITTED_S1_EPISODE"),
    ):
        check(media[source_id]["publisher_episode_code"] == code, f"publisher code {source_id}")
        check(by_id[audit_id] == {
            "id":audit_id,"class":"COUNTEREXAMPLE_TO_EPISODE_CARD_ASSUMPTION",
            "source_local_id":source_id,"publisher_code":code,"interpretation":cls,
        }, f"media-bucket anomaly {audit_id}")
    for audit_id, i, class_label, interpretation in (
        ("publisher-label-05", 5, "TITLE_FORM_UNRESOLVED", "DO_NOT_EXPAND_OR_CORRECT_PUBLISHER_LABEL_WITHOUT_EVIDENCE"),
        ("publisher-label-10", 10, "TITLE_ORTHOGRAPHY_HOLD", "DO_NOT_SUBSTITUTE_ALTERNATE_UNVERIFIED_SPELLING"),
    ):
        row = rows[i - 1]
        check(by_id[audit_id] == {
            "id":audit_id,"class":class_label,"publisher_route_id":row["publisher_route_id"],
            "observed_label":row["publisher_title"],"interpretation":interpretation,
        }, f"orthography hold {audit_id}")


def main() -> None:
    data = json.loads((HERE / "crosswalk.json").read_text(encoding="utf-8"))
    validate(data, read_sources())
    print("PASS: 10 exact publisher-to-publisher rows, 0 comparable historical WDQS rows; all held/ambiguous")


if __name__ == "__main__":
    main()
