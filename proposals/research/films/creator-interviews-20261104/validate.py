#!/usr/bin/env python3
"""Fail-closed, source-local schema and relational guards for held film interviews."""

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
REQUIRED_SOURCE = {
    "src-jung-2016": ("film-beyond", "Doug Jung", "2016-07-28", "co-writer-doug-jung-takes-you-inside-beyond"),
    "src-frakes-2016": ("film-first-contact", "Jonathan Frakes", "2016-11-22", "frakes-answers-fans-questions-part-2"),
    "src-berman-2011": ("film-insurrection", "Rick Berman", "2011-02-10", "rick-berman-looks-back-at-18-years-of-trek-part-3"),
    "src-stillwell-2011": ("film-insurrection", "Eric Stillwell", "2011-02-17", "recalling-yesterdays-enterprise-with-eric-stillwell-part-2"),
}
REQUIRED_EVIDENCE = {
    "ev-jung-vision": ("src-jung-2016", "49-53"),
    "ev-jung-ben": ("src-jung-2016", "85-87"),
    "ev-jung-screening": ("src-jung-2016", "79-80"),
    "ev-frakes-edit": ("src-frakes-2016", "53-59"),
    "ev-frakes-q": ("src-frakes-2016", "70-72"),
    "ev-frakes-audio": ("src-frakes-2016", "77-78"),
    "ev-berman-draft": ("src-berman-2011", "51-56"),
    "ev-stillwell-drafts": ("src-stillwell-2011", "60-62"),
}
REQUIRED_EPISTEMIC_STATUS = {
    "as-jung-vision": "SOURCE_ATTRIBUTED_NOT_FILM_VERIFIED",
    "as-jung-ben": "SOURCE_ATTRIBUTED_NOT_FILM_VERIFIED",
    "as-jung-screening": "SOURCE_ATTRIBUTED_WITH_INTERVIEW_DATE_UNCERTAINTY",
    "as-frakes-edit": "SOURCE_ATTRIBUTED_NOT_PRODUCTION_RECORD_VERIFIED",
    "as-frakes-q": "SOURCE_ATTRIBUTED_CONTESTABLE",
    "as-frakes-audio": "SOURCE_ATTRIBUTED_NOT_BUDGET_VERIFIED",
    "as-berman-draft": "SOURCE_ATTRIBUTED_NOT_DRAFT_COMPARED",
    "as-stillwell-drafts": "SOURCE_ATTRIBUTED_NOT_DRAFT_COMPARED",
}
ALLOWED_FIELDS = {
    "packet": {"schema_version", "proposal_only", "accepted_main_at_start", "observed_utc", "source_access", "source_families", "independent_publisher_family_count", "source_bound_effect", "coverage_effect", "full_film_viewed", "screenplay_read", "close_read", "source_page_raw_sha256", "public_plot_synopsis_effect", "film_candidates", "sources", "local_entities", "evidence", "assertions", "source_account_summaries"},
    "film": {"id", "title", "catalog_row_id"},
    "source": {"id", "film_candidate_id", "title", "url", "publisher", "published", "primary_witness", "witness_role", "access_status", "raw_page_sha256", "readable_article_line_span", "source_family"},
    "entity": {"id", "source_id", "kind"},
    "evidence": {"id", "source_id", "local_entity_id", "line_span", "locator", "paraphrase", "evidence_kind"},
    "assertion": {"id", "evidence_id", "subject", "predicate", "object", "epistemic_status"},
    "synopsis": {"film_candidate_id", "source_ids", "synopsis_kind", "text"},
    "manifest": {"batch_id", "proposal_only", "accepted_main_at_start", "source_page_count", "film_candidate_count", "evidence_count", "assertion_count", "source_account_synopsis_count", "packet_path", "packet_sha256", "upstream_raw_page_sha256", "full_film_viewed", "film_close_read", "screenplay_close_read", "coverage_effect", "published_effect", "review_status"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_fields(row, kind):
    require(isinstance(row, dict) and set(row) == ALLOWED_FIELDS[kind], f"{kind} must have exact reviewed fields; no extra claims")


def unique(rows, name):
    ids = [row["id"] for row in rows]
    require(len(ids) == len(set(ids)), f"duplicate {name} IDs")
    return {row["id"]: row for row in rows}


def validate(data):
    exact_fields(data, "packet")
    require(data["schema_version"] == "trek-film-publisher-interview-testimony-v1", "wrong schema")
    require(data["proposal_only"] is True, "proposal status")
    require(data["accepted_main_at_start"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "main anchor")
    for field in ("source_bound_effect", "coverage_effect", "public_plot_synopsis_effect"):
        require(data[field] == "NONE", f"unapproved effect {field}")
    for field in ("full_film_viewed", "screenplay_read", "close_read"):
        require(data[field] is False, f"false access claim {field}")
    require(data["source_access"] == "FULL_RENDERED_ARTICLE_TEXT_READ_NO_RAW_RESPONSE_CUSTODY", "false custody claim")
    require(data["source_page_raw_sha256"] is None, "raw source checksum without custody")
    require(data["source_families"] == ["publisher:startrek.com"] and data["independent_publisher_family_count"] == 1, "independence inflation")

    films = unique(data["film_candidates"], "film")
    for film in films.values():
        exact_fields(film, "film")
    require(set(films) == {"film-beyond", "film-first-contact", "film-insurrection"}, "film tranche drift")
    catalog = json.loads((ROOT / "explorer/film-catalog.json").read_text())
    catalog_rows = catalog["films"]
    catalog_ids = {str(row.get("id")) for row in catalog_rows}
    for film in films.values():
        require(film["catalog_row_id"] == "film:" + film["id"], "film ID mapping")
        require(film["id"] in catalog_ids, "missing film catalog row")
        require(next(row for row in catalog_rows if row["id"] == film["id"])["title"] == film["title"], "title differs from accepted film catalog")

    sources = unique(data["sources"], "source")
    require(set(sources) == set(REQUIRED_SOURCE), "source tranche count/identity")
    for sid, source in sources.items():
        exact_fields(source, "source")
        film, witness, date, slug = REQUIRED_SOURCE[sid]
        require(source["film_candidate_id"] == film, f"film-specific source join {sid}")
        require(source["primary_witness"] == witness and source["published"] == date, f"source witness/date {sid}")
        url = urlparse(source["url"])
        require(url.scheme == "https" and url.netloc == "www.startrek.com" and url.path == "/news/" + slug, f"source URL drift {sid}")
        require(source["source_family"] == "publisher:startrek.com", "unrelated source family")
        require(source["access_status"] == "COMPLETE_ARTICLE_RENDERED_TEXT_READ", "access claim drift")
        require(source["raw_page_sha256"] is None, "upstream checksum was not captured")

    entities = unique(data["local_entities"], "entity")
    require(set(entities) == {"entity-jung-account", "entity-frakes-account", "entity-berman-account", "entity-stillwell-account"}, "entity inventory")
    for ent in entities.values():
        exact_fields(ent, "entity")
        require(ent["source_id"] in sources and ent["kind"] == "CREATOR_INTERVIEW_ACCOUNT", "local entity source/kind")
        require(ent["id"] == "entity-" + sources[ent["source_id"]]["primary_witness"].split()[-1].lower() + "-account", "misattributed source entity")

    evidence = unique(data["evidence"], "evidence")
    assertions = unique(data["assertions"], "assertion")
    require(len(evidence) == len(assertions) == 8, "unexpected testimony count")
    require(set(evidence) == set(REQUIRED_EVIDENCE), "source evidence inventory changed")
    for ev in evidence.values():
        exact_fields(ev, "evidence")
        require((ev["source_id"], ev["line_span"]) == REQUIRED_EVIDENCE[ev["id"]], f"evidence not at reviewed source passage {ev['id']}")
        require(ev["source_id"] in sources, f"missing evidence source {ev['id']}")
        require(ev["local_entity_id"] in entities, f"missing local entity {ev['id']}")
        require(entities[ev["local_entity_id"]]["source_id"] == ev["source_id"], f"evidence attribution mismatch {ev['id']}")
        require(ev["evidence_kind"] == "ATTRIBUTED_INTERVIEW_TESTIMONY", "source testimony classification")
        require(bool(re.fullmatch(r"\d+-\d+", ev["line_span"])), "missing line locator")
        start, end = map(int, ev["line_span"].split("-"))
        allowed_start, allowed_end = map(int, sources[ev["source_id"]]["readable_article_line_span"].split("-"))
        require(allowed_start <= start <= end <= allowed_end, f"out-of-source text locator {ev['id']}")
        require(len(ev["paraphrase"].split()) >= 7 and not any(x in ev["paraphrase"].lower() for x in ("verified film fact", "film watched")), "unsupported evidence summary")
    for assertion in assertions.values():
        exact_fields(assertion, "assertion")
        require(assertion["evidence_id"] in evidence, "orphan assertion")
        ev = evidence[assertion["evidence_id"]]
        require(assertion["subject"] == ev["local_entity_id"], "assertion/evidence witness mismatch")
        require(assertion["id"] in REQUIRED_EPISTEMIC_STATUS and
                assertion["epistemic_status"] == REQUIRED_EPISTEMIC_STATUS[assertion["id"]],
                "assertion epistemic status deviates from source-relative reviewed classification")
        require(assertion["predicate"] in {
            "CREATOR_STATES_THEMATIC_INTENT", "CREATOR_STATES_SCRIPT_CHARACTER_LABEL", "CREATOR_REPORTS_SCREENING_STATE",
            "DIRECTOR_RECALLS_EDITING_DECISION", "DIRECTOR_RECALLS_UNREALIZED_PITCH", "DIRECTOR_RECALLS_MUSIC_CLEARANCE",
            "PRODUCER_RECALLS_SCRIPT_DEVELOPMENT", "SCRIPT_COORDINATOR_RECALLS_DRAFT_PROCESS"
        }, "claim wrongly promoted to film truth")

    summaries = data["source_account_summaries"]
    require({s["film_candidate_id"] for s in summaries} == set(films) and len(summaries) == 3, "film source account synopsis coverage")
    for summary in summaries:
        exact_fields(summary, "synopsis")
        require(summary["synopsis_kind"] == "ORIGINAL_CREATOR_TESTIMONY_SUMMARY", "film plot misclassified as source account")
        require(summary["source_ids"] and all(s in sources and sources[s]["film_candidate_id"] == summary["film_candidate_id"] for s in summary["source_ids"]), "cross-film summary source")
        require(len(summary["text"].split()) >= 30, "too shallow source account synopsis")
    return {"source_pages_read": len(sources), "film_candidates": len(films), "evidence": len(evidence), "assertions": len(assertions), "source_account_summaries": len(summaries)}


def validate_manifest(manifest, record_bytes):
    exact_fields(manifest, "manifest")
    require(manifest["batch_id"] == "films-firstparty-creator-interviews-20261104", "manifest batch identity")
    require(manifest["packet_path"] == "proposals/research/films/creator-interviews-20261104/records.json", "manifest exact packet path")
    require(manifest["proposal_only"] is True and manifest["coverage_effect"] == "NONE" and manifest["published_effect"] == "NONE", "manifest effect")
    require(manifest["full_film_viewed"] is False and manifest["film_close_read"] is False and manifest["screenplay_close_read"] is False, "manifest film/script access inflation")
    require(manifest["review_status"] == "LOCAL_VALIDATION_ONLY_PENDING_INDEPENDENT_AUDIT", "manifest review status")
    require(manifest["accepted_main_at_start"] == "3028765359001b90bc3e6b5c1835ee283b326e91", "manifest main drift")
    require(manifest["packet_sha256"] == hashlib.sha256(record_bytes).hexdigest(), "packet bytes changed")
    require(manifest["upstream_raw_page_sha256"] is None, "uncaptured upstream byte hash")
    actual = validate(json.loads(record_bytes))
    for manifest_field, actual_field in (
        ("source_page_count", "source_pages_read"),
        ("film_candidate_count", "film_candidates"),
        ("evidence_count", "evidence"),
        ("assertion_count", "assertions"),
        ("source_account_synopsis_count", "source_account_summaries"),
    ):
        require(manifest[manifest_field] == actual[actual_field], f"manifest {manifest_field} inconsistent with reviewed records")


if __name__ == "__main__":
    record_bytes = (HERE / "records.json").read_bytes()
    result = validate(json.loads(record_bytes))
    validate_manifest(json.loads((HERE / "BATCH_MANIFEST.json").read_text()), record_bytes)
    print(json.dumps(result, sort_keys=True))
