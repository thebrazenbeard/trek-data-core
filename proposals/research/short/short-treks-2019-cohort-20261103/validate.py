"""Fail-closed checks for the 2019 Short Treks publisher-metadata proposal.

This validates internal structure and fixed source-relative transcription,
not audiovisual viewing, source authenticity, legal rights, or admission.
"""

import datetime as dt
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_IDS = {"short-2019-nycc-announcement", "short-current-paramount-guide"}
EXPECTED = [
    ("qa", "Q&A", "2019-10-05", "S1E5"),
    ("trouble-edward", "The Trouble with Edward", "2019-10-10", "S1E6"),
    ("ask-not", "Ask Not", "2019-11-14", "S1E7"),
    ("girl-stars", "The Girl Who Made the Stars", "2019-12-12", "S1E8"),
    ("ephraim-dot", "Ephraim and Dot", "2019-12-12", "S1E9"),
    ("children-mars", "Children of Mars", "2020-01-09", "S1E10"),
]
DATE_BASIS = {
    "qa": "ARTICLE_DATE_AND_AVAILABLE_NOW",
    "trouble-edward": "EXPLICIT_SCHEDULE",
    "ask-not": "EXPLICIT_SCHEDULE",
    "girl-stars": "EXPLICIT_SCHEDULE",
    "ephraim-dot": "EXPLICIT_SCHEDULE",
    "children-mars": "EXPLICIT_SCHEDULE_WITH_ARTICLE_YEAR_ROLLOVER",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def keys(value, allowed, label):
    need(isinstance(value, dict) and set(value) == set(allowed), f"invalid {label} fields")


def unique(items, field, label):
    values = [x[field] for x in items]
    need(len(values) == len(set(values)), f"duplicate {label}")


def validate(data):
    keys(data, ["schema_version", "proposal_only", "status", "accepted_source_binding_effect",
                "accepted_work_effect", "coverage_effect", "admission_effect",
                "primary_audiovisual_processed", "source_independence_group", "observed_on_utc",
                "sources", "work_candidates", "local_entities", "evidence", "assertions"], "root")
    need(data["schema_version"] == "1.0.0" and data["proposal_only"] is True,
         "candidate schema required")
    need(data["status"] == "SOURCE_RELATIVE_PUBLISHER_METADATA", "status changed")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "admission_effect"):
        need(data[effect] == "NONE", f"unapproved promotion: {effect}")
    need(data["primary_audiovisual_processed"] is False, "false primary-source reading claim")
    need(data["source_independence_group"] == "publisher:paramount", "false independence")
    need(data["observed_on_utc"] == "2026-11-03", "unreviewed observation date")
    need(len(data["sources"]) == 2, "expected two source representations")
    unique(data["sources"], "source_id", "source")
    need({s["source_id"] for s in data["sources"]} == SOURCE_IDS, "unexpected source")
    urls = {
        "short-2019-nycc-announcement": "https://www.startrek.com/news/star-trek-discovery-season-three-short-treks-nycc",
        "short-current-paramount-guide": "https://www.paramountplus.com/shows/star-trek-short-treks/episodes/",
    }
    for source in data["sources"]:
        keys(source, ["source_id", "url", "source_kind", "source_locator", "response_sha256",
                      "hash_method", "source_bytes_committed", "independence_group"], "source")
        need(source["url"] == urls[source["source_id"]], "source URL changed")
        expected_kind = ("OFFICIAL_2019_ROLLOUT_ANNOUNCEMENT" if source["source_id"] ==
                         "short-2019-nycc-announcement" else "CURRENT_OFFICIAL_EPISODE_GUIDE")
        need(source["source_kind"] == expected_kind, "source kind invalid")
        need(isinstance(source["source_locator"], str) and source["source_locator"], "source locator absent")
        need(bool(re.fullmatch(r"[a-f0-9]{64}", source["response_sha256"])), "source hash malformed")
        need(source["hash_method"] == "SHA256_OF_TRANSIENT_HTTP_RESPONSE_NOT_COMMITTED",
             "source custody overstated")
        need(source["source_bytes_committed"] is False and source["independence_group"] == "publisher:paramount",
             "source copyright or lineage gate failed")

    need(len(data["work_candidates"]) == len(EXPECTED), "unexpected work count")
    unique(data["work_candidates"], "local_work_id", "work")
    expected_work = {f"short2019-{suffix}": title for suffix, title, _, _ in EXPECTED}
    for work in data["work_candidates"]:
        keys(work, ["local_work_id", "title", "type", "accepted_work_id"], "work")
        need(work["local_work_id"] in expected_work and work["title"] == expected_work[work["local_work_id"]],
             "unreviewed title or local work")
        need(work["type"] == "SCRIPTED_AUDIOVISUAL_SHORT" and work["accepted_work_id"] is None,
             "short Work type or admission altered")
    need(len(data["local_entities"]) == 12, "missing source-local entities")
    unique(data["local_entities"], "local_entity_id", "local entity")
    local_entities = {x["local_entity_id"]: x for x in data["local_entities"]}
    for suffix, _, _, _ in EXPECTED:
        for prefix, source_id, role in (
            ("news", "short-2019-nycc-announcement", "ANNOUNCED_SHORT_TITLE"),
            ("guide", "short-current-paramount-guide", "GUIDE_LISTING_TITLE"),
        ):
            entity = local_entities.get(f"{prefix}-{suffix}")
            keys(entity, ["local_entity_id", "work_candidate_id", "source_id", "source_relative_role"],
                 "local entity")
            need(entity["work_candidate_id"] == f"short2019-{suffix}" and entity["source_id"] == source_id
                 and entity["source_relative_role"] == role, "source-local linkage altered")

    need(len(data["evidence"]) == 12, "missing source-relative evidence")
    unique(data["evidence"], "evidence_id", "evidence")
    evs = {x["evidence_id"]: x for x in data["evidence"]}
    for suffix, _, date, slot in EXPECTED:
        news = evs.get(f"ev-news-{suffix}")
        guide = evs.get(f"ev-guide-{suffix}")
        keys(news, ["evidence_id", "local_entity_id", "kind", "locator", "announced_date",
                    "date_basis", "observed_claim"], "news evidence")
        keys(guide, ["evidence_id", "local_entity_id", "kind", "locator", "source_local_slot",
                     "observed_claim"], "guide evidence")
        need(news["local_entity_id"] == f"news-{suffix}" and news["kind"] == "PUBLISHER_RELEASE_ANNOUNCEMENT",
             "announcement provenance changed")
        need(guide["local_entity_id"] == f"guide-{suffix}" and guide["kind"] == "PUBLISHER_GUIDE_SLOT",
             "guide provenance changed")
        need(news["announced_date"] == date and guide["source_local_slot"] == slot,
             "source date or slot transcription changed")
        dt.date.fromisoformat(news["announced_date"])
        need(news["date_basis"] == DATE_BASIS[suffix], "date uncertainty lost")
        for evidence in (news, guide):
            need(isinstance(evidence["locator"], str) and evidence["locator"]
                 and isinstance(evidence["observed_claim"], str) and evidence["observed_claim"],
                 "evidence locator or claim empty")

    need(len(data["assertions"]) == 6, "unexpected assertion count")
    unique(data["assertions"], "assertion_id", "assertion")
    ass = {x["assertion_id"]: x for x in data["assertions"]}
    for suffix, _, _, _ in EXPECTED:
        item = ass.get(f"as-{suffix}")
        keys(item, ["assertion_id", "predicate", "work_candidate_id", "evidence_ids",
                    "status", "global_identity_effect"], "assertion")
        need(item["predicate"] == "CANDIDATE_SOURCE_LOCAL_TITLE_CORRESPONDENCE"
             and item["work_candidate_id"] == f"short2019-{suffix}"
             and item["evidence_ids"] == [f"ev-news-{suffix}", f"ev-guide-{suffix}"]
             and item["status"] == "PROPOSED" and item["global_identity_effect"] == "NONE",
             "automatic global reconciliation attempted")


def main():
    validate(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print("SHORT_2019_SOURCE_LOCAL_OK: 6 source-relative title pairs, 12 evidence observations, no admission")


if __name__ == "__main__":
    main()
