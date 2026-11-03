"""Fail-closed source-local DS9 B006 publisher-card triage; never Work admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBSERVATION_SHA = "2b48bda501fce90ac2bbac9ee4b4dde75e8b97203753f58c9ce0540f7e40badf"
ASSERTION_SHA = "a90eca1d7c6acc45a2eaf6bb5404b67f39606fdfb0962bba6da6d43994dbcbde"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
ENVELOPE_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_main_at_selection",
    "observed_utc_date", "discovery_directory_sha256", "discovery_lineage", "publisher_lineage",
    "read_scope", "raw_publisher_page_bytes_pinned", "full_episode_or_script_source_read",
    "accepted_source_work_binding_effect", "accepted_work_effect", "episode_research_coverage_effect",
    "synopsis_publication_effect", "source_local_cards",
}
CARD_KEYS = {
    "evidence_id", "source_local_row_id", "seed_title", "seed_external_locator", "official_title",
    "season", "episode", "publisher_guide_url", "publisher_card_locator", "title_comparison",
    "publisher_description_scope", "original_catalog_description_paraphrase", "synopsis_status",
    "accepted_work_id", "source_body_sha256",
}
EXPECTED = (
    ("lead:0067", "ds9-b006-p01", "Image in the Sand", "Q16744156",
     "Image in the Sand", 7, 1, "EXACT_LITERAL"),
    ("lead:0068", "ds9-b006-p02", "His Way", "Q16744174",
     "His Way", 6, 20, "EXACT_LITERAL"),
    ("lead:0069", "ds9-b006-p03", "Favor the Bold", "Q16744188",
     "Favor The Bold", 6, 5, "CASE_VARIANT_UNRESOLVED"),
)
ASSERTION_KEYS = {"schema_version", "batch_id", "proposal_only", "accepted_assertions",
                  "projection_effect", "assertions"}
ASSERTION_ROW_KEYS = {"id", "predicate", "subject_source_local_row_id", "evidence_ids",
                      "statement", "counter_evidence_ids", "status", "falsifier"}


def require(ok: bool, error: str) -> None:
    if not ok:
        raise ValueError(error)


def closed(obj, keys: set[str], scope: str) -> None:
    require(type(obj) is dict and set(obj) == keys, f"{scope}: extra or missing fields")


def fingerprint(obj) -> str:
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path, limit: int = 4_000_000):
    require(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size < limit,
            f"missing, symlinked, empty or oversized input: {path.name}")
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys), raw


def check(catalog: dict, raw_directory: bytes, observations: dict, assertions: dict,
          accepted_b005: dict) -> None:
    closed(observations, ENVELOPE_KEYS, "observation manifest")
    require(observations["schema_version"] == "1.0.0"
            and observations["batch_id"] == "ds9-publisher-guide-tail-b006-20261103"
            and observations["role"] == "DS9" and observations["proposal_only"] is True,
            "B006 batch role or schema changed")
    require(observations["accepted_main_at_selection"] == "5ea4a8d562e76931218329b8386e363e3c40845f"
            and observations["observed_utc_date"] == "2026-11-03",
            "observation origin changed")
    require(observations["discovery_directory_sha256"] == DIRECTORY_SHA
            and hashlib.sha256(raw_directory).hexdigest() == DIRECTORY_SHA,
            "pinned directory was changed")
    require(observations["discovery_lineage"] == "wikidata_collaborative_derivative"
            and observations["publisher_lineage"] == "paramount_corporate_publisher_family"
            and observations["read_scope"] == "PUBLIC_RENDERED_OFFICIAL_EPISODE_GUIDE_CARDS_ONLY",
            "publisher/discovery lineage or scope changed")
    for key in ("raw_publisher_page_bytes_pinned", "full_episode_or_script_source_read"):
        require(observations[key] is False, f"unsupported source read: {key}")
    for key in ("accepted_source_work_binding_effect", "accepted_work_effect",
                "episode_research_coverage_effect", "synopsis_publication_effect"):
        require(observations[key] == "NONE", f"unauthorized effect: {key}")

    require(type(catalog) is dict and catalog.get("data_status") == "DISCOVERY_ONLY"
            and catalog.get("row_count") == 1214 and len(catalog.get("rows", [])) == 1214
            and catalog.get("admission_effect") == "NONE"
            and catalog.get("coverage_effect") == "NONE", "discovery catalog scope changed")
    by_id = {row["row_id"]: row for row in catalog["rows"]}
    require(len(by_id) == 1214, "duplicate directory row identifiers")
    require(type(observations["source_local_cards"]) is list
            and len(observations["source_local_cards"]) == 3, "B006 must have three DS9 cards")
    require([x["source_local_row_id"] for x in observations["source_local_cards"]]
            == [x[0] for x in EXPECTED], "B006 DS9 lead frontier changed")

    require(type(accepted_b005) is dict
            and accepted_b005.get("data_status") == "RENDERED_PRIMARY_EPISODE_GUIDE_CARDS_WITH_PUBLISHER_BLURB_CONFLICT"
            and [x.get("row_id") for x in accepted_b005.get("rows", [])]
            == [f"lead:{i:04d}" for i in range(51, 67)], "accepted B005 frontier changed")
    require(not set(x["row_id"] for x in accepted_b005["rows"])
            .intersection(x["source_local_row_id"] for x in observations["source_local_cards"]),
            "B005/B006 overlap")

    for case, expected in zip(observations["source_local_cards"], EXPECTED):
        closed(case, CARD_KEYS, "source-local publisher card")
        (row_id, evidence_id, source_title, qid, official_title, season, episode, title_state) = expected
        source = by_id[row_id]
        require(source.get("context") == "DS9" and source.get("medium") == "EPISODE"
                and source.get("candidate_kind") == "WIKIDATA_EPISODE"
                and source.get("source_group") == "wikidata:wdqs"
                and source.get("verification_status") == "UNVERIFIED_METADATA"
                and source.get("admission_effect") == "NONE"
                and source.get("coverage_effect") == "NONE", "source lead was upgraded")
        require(case["evidence_id"] == evidence_id
                and case["source_local_row_id"] == row_id
                and case["seed_title"] == source_title == source["title"]
                and case["seed_external_locator"] == source["source_locator"]
                == f"https://www.wikidata.org/wiki/{qid}", "source seed identity changed")
        require(case["official_title"] == official_title
                and type(case["season"]) is int and case["season"] == season
                and type(case["episode"]) is int and case["episode"] == episode
                and case["title_comparison"] == title_state,
                "publisher title/slot mapping changed")
        if title_state == "EXACT_LITERAL":
            require(source_title == official_title, "claimed exact title is not exact")
        else:
            require(source_title != official_title and source_title.casefold() == official_title.casefold(),
                    "unresolved case variant was silently reconciled")
        guide = f"https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/{season}/"
        require(case["publisher_guide_url"] == guide
                and urlsplit(guide).hostname == "www.paramountplus.com"
                and case["publisher_card_locator"] == (
                    f"Season {season} Episode Guide > {official_title} > S{season} E{episode} > short description"),
                "official publisher card locator changed")
        require(case["publisher_description_scope"] == "CARD_TEXT_READ_NOT_INDEPENDENT_EPISODE_PROOF"
                and case["synopsis_status"] == "ORIGINAL_DRAFT_PENDING_EDITORIAL_REVIEW"
                and case["accepted_work_id"] is None and case["source_body_sha256"] is None,
                "card promoted to Work, source read or approved synopsis")
        summary = case["original_catalog_description_paraphrase"]
        require(type(summary) is str and 60 <= len(summary) <= 210 and summary.endswith(".")
                and "\n" not in summary, "invalid pending original description")

    closed(assertions, ASSERTION_KEYS, "source-local assertions")
    require(assertions["schema_version"] == "1.0.0"
            and assertions["batch_id"] == observations["batch_id"]
            and assertions["proposal_only"] is True
            and assertions["accepted_assertions"] == 0
            and assertions["projection_effect"] == "NONE", "source claim promoted")
    require(type(assertions["assertions"]) is list and len(assertions["assertions"]) == 1,
            "source-local assertion count changed")
    claim = assertions["assertions"][0]
    closed(claim, ASSERTION_ROW_KEYS, "source-local assertion")
    require(claim["id"] == "ds9-b006-a01"
            and claim["predicate"] == "PUBLISHER_TITLE_CASE_VARIANT_REQUIRES_RECONCILIATION"
            and claim["subject_source_local_row_id"] == "lead:0069"
            and claim["evidence_ids"] == ["ds9-b006-p03"]
            and claim["counter_evidence_ids"] == []
            and claim["status"] == "PROPOSED_UNRESOLVED"
            and type(claim["falsifier"]) is str and len(claim["falsifier"]) > 30,
            "case-variant claim improperly resolved")
    # Freezing the public research proposal does not authenticate Paramount+ HTML.
    require(fingerprint(observations) == OBSERVATION_SHA, "observed candidate receipt changed")
    require(fingerprint(assertions) == ASSERTION_SHA, "unresolved assertion receipt changed")


def validate() -> None:
    observations, _ = read_json(HERE / "observations.json")
    assertions, _ = read_json(HERE / "assertions.json")
    catalog, catalog_raw = read_json(ROOT / "explorer/discovery-catalog.json")
    b005, _ = read_json(ROOT / "proposals/verification/episode-guide-rechecks-b005-20261103/observations.json")
    check(catalog, catalog_raw, observations, assertions, b005)
    print("DS9_B006_OK: 3 source-local publisher cards; 2 literal titles, "
          "1 unresolved case variant, 3 pending original descriptions; zero Work/coverage admission")


if __name__ == "__main__":
    validate()
