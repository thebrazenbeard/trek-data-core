#!/usr/bin/env python3
"""Fail-closed source-local guards for one complete Meyer interview, not film footage."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MAIN = "3028765359001b90bc3e6b5c1835ee283b326e91"
SOURCE_ID = "src-meyer-part2-2014"
FILMS = {
    "film-wrath-of-khan": "Star Trek II: The Wrath of Khan",
    "film-voyage-home": "Star Trek IV: The Voyage Home",
    "film-undiscovered-country": "Star Trek VI: The Undiscovered Country",
}
ENTITIES = {
    "meyer-account-ii": "film-wrath-of-khan",
    "meyer-account-iv": "film-voyage-home",
    "meyer-account-vi": "film-undiscovered-country",
}
EXPECTED_EVIDENCE = {
    "meyer-e01-spock-placement": ("meyer-account-ii", "47-55", "ATTRIBUTED_DIRECTOR_TESTIMONY"),
    "meyer-e02-return-setup": ("meyer-account-ii", "56-57", "ATTRIBUTED_DIRECTOR_TESTIMONY"),
    "meyer-e03-montalban-direction": ("meyer-account-ii", "60-65", "ATTRIBUTED_DIRECTOR_TESTIMONY"),
    "meyer-e04-earth-rewrite": ("meyer-account-iv", "66-70", "ATTRIBUTED_SCREENWRITER_TESTIMONY"),
    "meyer-e05-speed": ("meyer-account-iv", "71-73", "ATTRIBUTED_SCREENWRITER_TESTIMONY"),
    "meyer-e06-wall": ("meyer-account-vi", "76-82", "ATTRIBUTED_DIRECTOR_TESTIMONY"),
    "meyer-e07-writers": ("meyer-account-vi", "80-82", "ATTRIBUTED_DIRECTOR_TESTIMONY_WITH_INFERENCE"),
    "meyer-e08-corrected-recollection": ("meyer-account-vi", "76-87", "INTERVIEWER_CHALLENGE_AND_WITNESS_ACKNOWLEDGMENT"),
}
EXPECTED_ASSERTIONS = {
    "meyer-a01": ("meyer-e01-spock-placement", "DIRECTOR_RECALLS_OWN_SCRIPT_STRUCTURE", "SOURCE_ATTRIBUTED_UNCORROBORATED"),
    "meyer-a02": ("meyer-e02-return-setup", "DIRECTOR_RECALLS_LATE_REVISION_DISAGREEMENT", "SOURCE_ATTRIBUTED_WITH_RETROSPECTIVE_QUALIFICATION"),
    "meyer-a03": ("meyer-e03-montalban-direction", "DIRECTOR_RECALLS_PERFORMANCE_DIRECTION", "SOURCE_ATTRIBUTED_UNCORROBORATED"),
    "meyer-a04": ("meyer-e04-earth-rewrite", "WRITER_REPORTS_SECTION_ASSIGNMENT", "SOURCE_ATTRIBUTED_NOT_SCRIPT_VERIFIED"),
    "meyer-a05": ("meyer-e05-speed", "WRITER_RECALLS_RAPID_DEVELOPMENT", "SOURCE_ATTRIBUTED_DURATION_UNCERTAIN"),
    "meyer-a06": ("meyer-e06-wall", "DIRECTOR_RECALLS_COLLABORATIVE_THEME", "SOURCE_ATTRIBUTED_NOT_NIMOY_CORROBORATED"),
    "meyer-a07": ("meyer-e07-writers", "DIRECTOR_REPORTS_COMMISSIONING_HISTORY", "SOURCE_ATTRIBUTED_MOTIVE_SPECULATIVE"),
    "meyer-a08": ("meyer-e08-corrected-recollection", "INTERVIEW_EXPOSES_RETROSPECTIVE_MEMORY_LIMIT", "SOURCE_ATTRIBUTED_CORRECTION_NOT_EXTERNAL_VERIFICATION"),
}
# Frozen digests of the actual reviewed *original summaries*, not the copyrighted
# source article. A future source-grounded correction must explicitly update these
# pins and obtain fresh review; a recomputed transport/manifest hash alone is not
# an editorial or source-verification decision.
REVIEWED_SOURCE_RECORD_SHA256 = "301259342ee1dc47d293ffe09b9b26fb6a2a24822e24bf5cb1fe0abb184054e5"
REVIEWED_EVIDENCE_PARAPHRASE_SHA256 = {
    "meyer-e01-spock-placement": "7da3084882d73a7f76d8fe401a07510a54efc72c1fd04cb0c7bec20eb7d21a47",
    "meyer-e02-return-setup": "b1cd4c2c410738172e0bb44bb3ad6219364278881fc32785ee9dadcff29049f7",
    "meyer-e03-montalban-direction": "5d32dd1715cc53484d06553f71dd3dc5dd65f52d647e1fc6f27f200f10dd739f",
    "meyer-e04-earth-rewrite": "11d3a2647e79f95149a12d8334b1f13b9a4d1e0d47f74cd325bf18789beedad2",
    "meyer-e05-speed": "69c442d84bd6117c24678d4ab907e6b338e30413985b69209812c7bf97ee6f76",
    "meyer-e06-wall": "6fc947d63f56c5ceccd940d987b5111f803ab13317384b47732f981631c11a7b",
    "meyer-e07-writers": "4dadd67dd5b9281d861030407b9dfc2844caf96c09ede89bdb943502b9b63cbf",
    "meyer-e08-corrected-recollection": "78f1bb8b06a10f4ba31e919122bed68a0384052cc33af43b23ccd7333e1e65c7",
}
REVIEWED_ASSERTION_OBJECT_SHA256 = {
    "meyer-a01": "bbc2151da9f0eb57c9c45a0a1746ae1490d3af9055c2289684fac118d27bef6d",
    "meyer-a02": "f14bc231fee8ae718d2c2b1159865798ae3abda9613a9a367bedfacdb3e98807",
    "meyer-a03": "6aa49e51b1de8da3cb505bdd3660f3c52d5554c2d15e1d0e44aaf401d4667025",
    "meyer-a04": "ad573a3394dc25dac1d1d594f4d88f2918ba16a2439b2abb9eb3d28d398ed2e7",
    "meyer-a05": "4bce0ebd60dd7e25f767cf9462b2876a27903cd6371e07c3e05cd6202efe3791",
    "meyer-a06": "7fb59af0809fdc437b457432dd16e548ead9d311dcca1c7c3292c54acd742561",
    "meyer-a07": "55d4df9dc3d279289345a780e66617e99b8a05f4e6483203347bc70e5e418af9",
    "meyer-a08": "da1c21001b7068975433eb979924149dc11bd3b3d0ea9431919c2ea649ac01f4",
}
REVIEWED_SUMMARY_SHA256_BY_FILM = {
    "film-wrath-of-khan": "b98bb41971c97cd150a29bb92630c50d981c25b5e27cf4480093fc765a9ae85c",
    "film-voyage-home": "6e2423077f762efca5f30b42187ca375dae203ef984e373f8fec3979283ed16d",
    "film-undiscovered-country": "2ad48c45b68bb701b30f4d376b753371d33043d954b53f24406f5cb807ee87ac",
}
EXACT = {
    "packet": {"schema_version", "proposal_only", "accepted_main_at_start", "source_custody_state",
               "source_bound_effect", "coverage_effect", "film_close_read", "script_close_read",
               "public_source_text_effect", "independent_source_family_count", "source",
               "film_candidates", "local_entities", "evidence", "assertions", "source_account_summaries"},
    "source": {"id", "title", "url", "publisher", "published_date", "source_family",
               "first_person_witness", "retrieved_utc", "rendered_line_span", "raw_page_sha256", "rights_status"},
    "film": {"id", "title", "catalog_row_id"},
    "entity": {"id", "film_candidate_id", "source_id", "kind"},
    "evidence": {"id", "local_entity_id", "source_id", "line_span", "evidence_kind", "paraphrase"},
    "assertion": {"id", "evidence_id", "subject", "predicate", "object", "epistemic_status"},
    "summary": {"film_candidate_id", "source_id", "summary_kind", "text"},
    "manifest": {"batch_id", "proposal_only", "accepted_main_at_start", "packet_path", "packet_sha256",
                 "source_page_count", "film_candidate_count", "local_entity_count", "evidence_count",
                 "assertion_count", "original_summary_count", "raw_source_bytes_published",
                 "film_close_read", "script_close_read", "coverage_effect", "published_effect", "review_status"},
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def reviewed_sha(text):
    require(isinstance(text, str), "reviewed original text must be string")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fields(obj, label):
    require(isinstance(obj, dict) and set(obj) == EXACT[label], f"{label}: unreviewed fields or missing fields")


def keyed(rows, label):
    require(isinstance(rows, list) and all(isinstance(x, dict) for x in rows), f"{label}: expected objects")
    for r in rows:
        fields(r, label)
    keys = [row["id"] for row in rows]
    require(len(keys) == len(set(keys)), f"{label}: duplicate IDs")
    return {row["id"]: row for row in rows}


def validate(data):
    fields(data, "packet")
    require(data["schema_version"] == "trek-film-source-local-creator-interview-v1", "schema changed")
    require(data["proposal_only"] is True and data["accepted_main_at_start"] == MAIN, "unaccepted main/effect")
    for key in ("source_bound_effect", "coverage_effect", "public_source_text_effect"):
        require(data[key] == "NONE", f"{key} cannot promote effects")
    require(data["film_close_read"] is False and data["script_close_read"] is False, "false film/script access")
    require(data["source_custody_state"] == "COMPLETE_RENDERED_OFFICIAL_ARTICLE_READ_RAW_BYTES_NOT_ARCHIVED",
            "source custody drift")
    require(data["independent_source_family_count"] == 1, "one publisher interview, no multiple-source independence")

    src = data["source"]
    fields(src, "source")
    source_metadata_bytes = json.dumps(src, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    require(reviewed_sha(source_metadata_bytes) == REVIEWED_SOURCE_RECORD_SHA256,
            "source title/metadata differs from frozen reviewed interview")
    uri = urlparse(src["url"])
    require(src["id"] == SOURCE_ID and uri.scheme == "https" and uri.netloc == "www.startrek.com" and
            uri.path == "/en-un/news/exclusive-interview-part-ii-nicholas-meyer-on-directing",
            "unreviewed source")
    require(src["publisher"] == "StarTrek.com Staff" and src["published_date"] == "2014-09-26" and
            src["first_person_witness"] == "Nicholas Meyer" and src["source_family"] == "publisher:startrek.com",
            "source provenance drift")
    require(src["rendered_line_span"] == "39-89" and src["raw_page_sha256"] is None and
            src["rights_status"] == "READ_FOR_SOURCE_RELATIVE_ANALYSIS_NO_REHOST_LICENSE",
            "false raw custody or publication rights")
    require(bool(re.fullmatch(r"2026-11-04T\d\d:\d\d:\d\dZ", src["retrieved_utc"])),
            "unreviewed retrieval date")

    films = keyed(data["film_candidates"], "film")
    require(set(films) == set(FILMS), "film tranche changed")
    accepted = {x["id"]: x for x in json.loads((ROOT / "explorer/film-catalog.json").read_text())["films"]}
    for id_, film in films.items():
        require(film["title"] == FILMS[id_] and film["catalog_row_id"] == "film:" + id_,
                "film title/row changed")
        require(id_ in accepted and accepted[id_]["title"] == film["title"],
                "film discovery catalog does not agree")

    entities = keyed(data["local_entities"], "entity")
    require(set(entities) == set(ENTITIES), "local entity IDs changed")
    for id_, ent in entities.items():
        require(ent["film_candidate_id"] == ENTITIES[id_] and ent["source_id"] == SOURCE_ID and
                ent["kind"] == "SOURCE_RELATIVE_CREATOR_ACCOUNT", "unsupported local entity reconciliation")

    ev = keyed(data["evidence"], "evidence")
    require(set(ev) == set(EXPECTED_EVIDENCE), "evidence inventory drift")
    for id_, item in ev.items():
        expected_entity, span, kind = EXPECTED_EVIDENCE[id_]
        require((item["local_entity_id"], item["line_span"], item["evidence_kind"]) ==
                (expected_entity, span, kind), f"source-relative locator drift {id_}")
        require(item["source_id"] == SOURCE_ID and len(item["paraphrase"].split()) >= 15,
                "bad evidence attribution or insufficient paraphrase")
        require(reviewed_sha(item["paraphrase"]) == REVIEWED_EVIDENCE_PARAPHRASE_SHA256[id_],
                f"unreviewed evidence text substitution {id_}")
        require(not any(s in item["paraphrase"].lower() for s in
                        ("verified film event", "we viewed the film", "official script verified")),
                "unsupported depiction promotion")

    assertions = keyed(data["assertions"], "assertion")
    require(set(assertions) == set(EXPECTED_ASSERTIONS), "assertion inventory drift")
    for id_, item in assertions.items():
        ev_id, predicate, status = EXPECTED_ASSERTIONS[id_]
        require((item["evidence_id"], item["predicate"], item["epistemic_status"]) ==
                (ev_id, predicate, status), "assertion predicate/status must match reviewed source frame")
        require(item["subject"] == ev[ev_id]["local_entity_id"] and len(item["object"].split()) >= 6,
                "assertion local subject/evidence mismatch")
        require(reviewed_sha(item["object"]) == REVIEWED_ASSERTION_OBJECT_SHA256[id_],
                f"unreviewed assertion text substitution {id_}")

    summaries = data["source_account_summaries"]
    require(isinstance(summaries, list) and len(summaries) == 3, "unexpected source account summary count")
    for s in summaries:
        fields(s, "summary")
        require(s["film_candidate_id"] in FILMS and s["source_id"] == SOURCE_ID and
                s["summary_kind"] == "ORIGINAL_CREATOR_INTERVIEW_ACCOUNT", "summary source/film misjoin")
        require(len(s["text"].split()) >= 55, "summary not a substantive original source account")
        require(reviewed_sha(s["text"]) == REVIEWED_SUMMARY_SHA256_BY_FILM[s["film_candidate_id"]],
                "unreviewed creator-account summary substitution")
    require({s["film_candidate_id"] for s in summaries} == set(FILMS), "missing or duplicated film summary")
    return {"source_pages": 1, "film_candidates": len(films), "local_entities": len(entities),
            "evidence": len(ev), "assertions": len(assertions), "original_summaries": len(summaries)}


def validate_manifest(manifest, raw_packet):
    fields(manifest, "manifest")
    require(manifest["batch_id"] == "films-meyer-interview-2014-part2-held", "batch ID changed")
    require(manifest["accepted_main_at_start"] == MAIN and manifest["proposal_only"] is True, "main/effect")
    require(manifest["packet_path"] ==
            "proposals/research/films/meyer-interview-2014-part2-held/records.json", "packet path changed")
    require(manifest["packet_sha256"] == hashlib.sha256(raw_packet).hexdigest(), "packet hash mismatched")
    require(manifest["raw_source_bytes_published"] is False and
            manifest["film_close_read"] is False and manifest["script_close_read"] is False and
            manifest["coverage_effect"] == "NONE" and manifest["published_effect"] == "NONE" and
            manifest["review_status"] == "LOCAL_VALIDATION_ONLY_AUDIT_PENDING", "false publication/qualification")
    actual = validate(json.loads(raw_packet))
    for m, k in (
        ("source_page_count", "source_pages"), ("film_candidate_count", "film_candidates"),
        ("local_entity_count", "local_entities"), ("evidence_count", "evidence"),
        ("assertion_count", "assertions"), ("original_summary_count", "original_summaries")
    ):
        require(manifest[m] == actual[k], f"{m} not supported by packet")


if __name__ == "__main__":
    raw = (HERE / "records.json").read_bytes()
    data = json.loads(raw)
    validate(data)
    validate_manifest(json.loads((HERE / "BATCH_MANIFEST.json").read_text()), raw)
    print(json.dumps(validate(data), sort_keys=True))
