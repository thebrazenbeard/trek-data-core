"""Deterministic, fail-closed PIC S3 first-five publisher-guide packet checks."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DISCOVERY = ROOT / "proposals/discovery/modern-paramount-season3-20261102/pic/bundle.json"
EXPECTED_TITLES = [
    "The Next Generation", "Disengage", "Seventeen Seconds",
    "No Win Scenario", "Imposters", "The Bounty", "Dominion",
    "Surrender", "Võx", "The Last Generation",
]
EXPECTED_ROUTES = [
    "/shows/video/dQo2jCxwxKSXtDyIPKb44W6hCEiqd_Ec/",
    "/shows/video/_hn3xX7z2ADLb5xnjtHAP_JQw9geuB_l/",
    "/shows/video/NjhnDbV7slibv9pl7MZ9LBC5fAyrvJTN/",
    "/shows/video/__96sEpIXP3iBbpyS_7nhEPaV_CVYiBv/",
    "/shows/video/d_z5_o1wYC8jHl3NOgHSqe_QY_eMYkY_/",
    "/shows/video/yeJ_ynW6Qu1C7H4H2_QoTHCZmQakA18V/",
    "/shows/video/91_ySBOXOfS_qMu4C95G3yTPJ8YZ9kBR/",
    "/shows/video/C2f7pUJxydwrcvPshqRWdFZ7D4G4xGAn/",
    "/shows/video/3IJy0NLkyr4r0VGOPx06qPX7PtjrE9rh/",
    "/shows/video/abCBCq46mnpopGlfoDFGpdZoGT807ldy/",
]
EXPECTED_DESCRIPTION_HASHES = [
    "4c81f2fabf65dd16a687854effef44fdd51c1a82b94090f6e92b1afa6ef3a9b0",
    "19d24fa5ae3654b12bcb7fd84d7de1766b45f38b38a20974b260a3f80d4a2757",
    "e12c551a469f3bc5409fd0ae1ad0e0995c24c8b6c51191dec3dd3ffa036eca78",
    "ff828d78204aeb13fe5e8a6932ee88a305ef4b9866462b66f02074ffb0643709",
    "3f9cc910315ebdf1c23f430f1c9bd0491534f6e536380d5dd7a2c02cd4775f15",
    "947a9d13f43590ed96eeda4079f82642db2c9fd61e036a737673ff2488e54a1d",
    "fee4ac7d2bd80d0a056254310226ac9b78a3b00a92f5b598dc7f1248da3c6f1c",
    "7b302beb35512f2e53b81b1cd54a49f0bbece229ef0bc1c4fbd91cd29b0c9801",
    "42511bacc17ff8c051d2a0d81b2f9ba5a3f24b26332e10095c07928ae1449a80",
    "a2c429168eb01b95e1999e2b8aea942e6f3126bc3825e3672e67dc37c0ff332f",
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check(test, message: str) -> None:
    if not test:
        raise ValueError(message)


def validate(data: dict, discovery: dict, discovery_sha: str) -> None:
    check(data.get("schema_version") == "1.0.0", "schema")
    check(data.get("batch_id") == "PIC.PPLUS.S3.FIRST5.GUIDE.20261104", "batch")
    check(data.get("role") == "PIC", "partition owner")
    check(data.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "source-relative hold")
    for key in EFFECTS:
        check(data.get(key) == "NONE", f"protected effect {key}")
    for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(data.get(key) is False, f"false full content claim {key}")
    source = data.get("source", {})
    check(source.get("url") == "https://www.paramountplus.com/shows/star-trek-picard/episodes/3/", "official page URL")
    check(source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "source kind")
    check(source.get("independence_group") == "publisher:paramountplus.com", "source lineage")
    check(source.get("response_http_status") == 200, "response status")
    check(source.get("raw_response_bytes") == 272699, "exact retrieval bytes")
    check(source.get("raw_response_sha256") == "54f51850043a1073f8ac4f4e68a22b6acf2bd5b70ad416adce695c36d9e659b3", "exact receipt SHA")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True, "no copyrighted HTML")
    check(source.get("reproducible_extractor") == "source_probe.py", "extractor provenance")
    check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*\+00:00", source.get("observed_at_utc", ""))), "UTC retrieval timestamp")
    upstream = data.get("upstream_discovery", {})
    check(upstream.get("path") == "proposals/discovery/modern-paramount-season3-20261102/pic/bundle.json", "held discovery locator")
    check(upstream.get("sha256") == discovery_sha, "held discovery exact SHA")
    check(upstream.get("identity_join_method") == "SOURCE_LOCAL_SEASON_EPISODE_TITLE_NOT_CANONICAL_WORK", "no global Work match")
    check(discovery.get("accepted_work_effect") == "NONE" and discovery.get("coverage_effect") == "NONE", "upstream held")
    candidates = discovery.get("episode_slots", [])
    check(len(candidates) == 10, "upstream ten candidates")
    cards = data.get("guide_cards")
    check(isinstance(cards, list) and len(cards) == 10 and data.get("guide_inventory_observed") == 10, "full page traversal")
    check([c.get("title") for c in cards] == EXPECTED_TITLES, "full guide title order")
    check(len({c.get("video_route_path") for c in cards}) == 10, "unique source routes")
    check(data.get("first_five_source_descriptions_inspected") == 5 and data.get("first_five_analytical_synopses_proposed") == 5, "bounded first-five batch")
    check(data.get("first_five_description_total_chars") == sum(c.get("description_chars", -1) for c in cards[:5]) == 1250, "source content actually processed")
    for number, (card, candidate) in enumerate(zip(cards, candidates), 1):
        check(card.get("display_order") == card.get("episode") == card.get("analytics_ordinal") == number, f"ordinal {number}")
        check(card.get("season") == 3 and candidate.get("season") == 3 and candidate.get("episode_number") == number, f"season/slot {number}")
        check(card.get("title") == candidate.get("title"), f"source-relative discovery crosswalk {number}")
        check(candidate.get("canonical_work_id") is None and candidate.get("source_binding_id") is None, f"upstream no Work binding {number}")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"official route shape {number}")
        check(card["video_route_path"] == EXPECTED_ROUTES[number - 1], f"exact observed route {number}")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"publisher raw datetime {number}")
        check(card.get("html_anchor_line") == 1470 + 28 * (number - 1), f"source locator anchor {number}")
        check(card.get("html_description_line") == 1488 + 28 * (number - 1), f"source locator description {number}")
        check(isinstance(card.get("description_chars"), int) and card["description_chars"] >= 100, f"description length {number}")
        check(bool(re.fullmatch(r"[a-f0-9]{64}", card.get("description_sha256", ""))), f"source description fingerprint {number}")
        check(card["description_sha256"] == EXPECTED_DESCRIPTION_HASHES[number - 1], f"exact observed description hash {number}")
    entities = data.get("local_entities", [])
    evidences = data.get("source_relative_evidence", [])
    assertions = data.get("typed_assertions", [])
    check(len(entities) == len(evidences) == len(assertions) == 5, "bounded five local evidence rows")
    for number, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions), 1):
        card = cards[number - 1]
        entity_id = f"pic-s3-e{number:02d}-publisher-card"
        evidence_id = f"pic-s3-e{number:02d}-guide-description"
        check(entity.get("id") == entity_id and entity.get("source_local_episode_hint") == number and entity.get("canonical_work_id") is None, f"local entity only {number}")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == entity_id, f"source-local evidence {number}")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and evidence.get("card_ordinal") == number, f"evidence class {number}")
        check(evidence.get("publisher_description_sha256") == card["description_sha256"], f"description fingerprint crosswalk {number}")
        check(f"{card['html_description_line']}" in evidence.get("locator", ""), f"HTML locator {number}")
        paraphrase = evidence.get("original_paraphrase", "")
        check(isinstance(paraphrase, str) and 65 <= len(paraphrase) <= 200, f"bounded original analysis {number}")
        check(assertion.get("evidence_id") == evidence_id and assertion.get("predicate") == "PUBLISHER_DESCRIBES", f"typed source assertion {number}")
        check(assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"assertion avoids truth promotion {number}")
    check(len(data.get("holds", [])) >= 5, "explicit provenance and rights holds")


def main() -> int:
    try:
        contents = DISCOVERY.read_bytes()
        discovery = read_json(DISCOVERY)
        validate(read_json(HERE / "records.json"), discovery, hashlib.sha256(contents).hexdigest())
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"FAIL PIC S3: {exc}", file=sys.stderr)
        return 1
    print("PASS PIC S3: full official guide processed, five source-relative synopsis candidates, 0 Work/coverage effects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
