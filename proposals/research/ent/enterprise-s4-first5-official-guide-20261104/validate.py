"""Deterministic held ENT Season 4 E01–E05 source-custody and synopsis checks."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DISCOVERY = ROOT / "proposals/discovery/publisher-season4-20261102/ent/bundle.json"
DISCOVERY_SHA = "15dcc53ab83df5cf0dcf602a6938588b290c16217c0e36fb0375489b077c0e17"
SOURCE_SHA = "e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392"
EXPECTED_FINGERPRINTS = [
  "59aa440296569e80ad659b6fa4bcfef1d5d53e9ac94cc39e520859daf374d9e1",
  "877563d86183bc5e724c543b35a2b297acfbf4cb347999d4dd95cf8f5fe783ac",
  "2df3fc33e639774b86deef2623e5d4b19e12dd38e9427d41ba05f70ac7535ff5",
  "42275b6146ea5b96a24a2c08dd6d4cba58184522a68277c63d9405026f4c7cd7",
  "bc568c551852e4b2cdfae7af0c8e8aba7bf9a7eba8c7ba98d82f824205ce534f",
  "739295c7b2a8253ff2571357b5cd9631583671c0fbfebc6928a641cd2f156c12",
  "47ae93ad886d52f46f1ab82dd517ec73665b99c86eaba6cffadd8a43eb7d5e29",
  "352fe70f2709ef74f953c4fe5781ff3c34a359ec14afa96738b81ec64d6ca1cd",
  "bded78321051f42921244c738e156cbd6e8b2dd80165e74ce3fea067a55e32de",
  "9c1e2540da710e80246cf015b1d27ed88c776fc573bfe2b3ae276282c33a0456",
  "ff0443f6a0295ec0c093fbeddf7f1168e7a58fec70c2dc736a21c7a484875e9f",
  "8a915effba1911f81f3ee231295a2be84f73923bfbd67ef9c8476ea4a607d969",
  "fea2b749aad42b88e778b6296567984d42ccea27d1f82cd3747f860084fc3af2",
  "74e5a90e9973c1fa055397fb9cfdd686223564ba3bb725e368cfe92261fe869e",
  "2dc78705299e93d73b33c25a4bb2a0f5b0be243876babd1602e18d45194ac7df",
  "f167b224da7cbd93f181dac161fc8886d69ba0decd3cc45a8ec606972824bfcf",
  "1690a6918b7a68894bae542dad95b8ec2e5ae2b31ddd7775e8a17c9f58fcdb92",
  "56afde4fd595b85776d0527011bf3c9adbf33db03bd56ee3ab612baaeba6cd31",
  "701428343bc7690929b7bcf2ac5f53e82579d5bed64aa7a99e52b56abbfd840c",
  "0c0195adbe71a85a6228aee12aae873031cfdbe33d6168dfd49abaffb0211cd4",
  "8feccc9522fde17b61d59a9dc0526bd60c3b985868b3a69c05b3f63fe433f903",
  "2e73d100233573f99ffcec035e3d40692d40a727afd4769daffbd779c09795cd"
]
EXPECTED_ROUTES = [
  "/shows/video/NensQYeT7tid6zuxiZkEaxyN1x8YBzIV/",
  "/shows/video/aN_YQoBwM5Cb1X3c7X6MrHGnq66h_zCO/",
  "/shows/video/foE9_bRPraZdhW3D4vzjTaWJSO971Py8/",
  "/shows/video/1482475923/",
  "/shows/video/1482478168/",
  "/shows/video/1482478814/",
  "/shows/video/1482479260/",
  "/shows/video/1482480055/",
  "/shows/video/1484499111/",
  "/shows/video/1484500266/",
  "/shows/video/1484501847/",
  "/shows/video/1484504386/",
  "/shows/video/1484512625/",
  "/shows/video/1484514241/",
  "/shows/video/1484518693/",
  "/shows/video/1484522414/",
  "/shows/video/1484534262/",
  "/shows/video/0rgm7_kR4kFn02CcHd_yzaSz8E6SmLXZ/",
  "/shows/video/1484536612/",
  "/shows/video/1484538462/",
  "/shows/video/1484541359/",
  "/shows/video/1484542716/"
]
PROTECTED = ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
             "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect")


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def validate(data: dict, discovery: dict, discovery_sha: str) -> None:
    check(discovery_sha == DISCOVERY_SHA, "exact upstream discovery SHA")
    check(discovery.get("batch_id") == "PARAMOUNT-S4-20261102-ENT", "upstream discovery source")
    check(discovery.get("mission_id") == "ent" and discovery.get("listed_slot_count") == 22, "22 upstream source-local candidate slots")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        check(discovery.get(effect) == "NONE", f"upstream protected effect {effect}")
    check(data.get("schema_version") == "1.0.0" and data.get("batch_id") == "ENT.PPLUS.S4.FIRST5.GUIDE.20261104", "new packet identity")
    check(data.get("role") == "ENT" and data.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "ENT HELD lane")
    for effect in PROTECTED:
        check(data.get(effect) == "NONE", f"protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(data.get(flag) is False, f"unsupported content-reading claim {flag}")
    upstream = data.get("upstream_discovery", {})
    check(upstream.get("path") == "proposals/discovery/publisher-season4-20261102/ent/bundle.json" and upstream.get("sha256") == DISCOVERY_SHA, "upstream pinned locator/digest")
    check(upstream.get("identity_join_method") == "SOURCE_LOCAL_SEASON_EPISODE_TITLE_NOT_CANONICAL_WORK" and upstream.get("independent_corroboration") is False, "same publisher is not independent")
    source = data.get("source", {})
    check(source.get("local_source_id") == "ent-s4-paramountplus-guide-html-first5-20261104", "new local source ID")
    check(source.get("url") == discovery.get("observation", {}).get("primary_locator") == "https://www.paramountplus.com/shows/enterprise/episodes/4/", "official source URL")
    check(source.get("publisher") == "Paramount+" and source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "first-party guide type")
    check(source.get("independence_group") == "publisher:paramountplus.com", "no false independent witness")
    check(type(source.get("response_http_status")) is int and source["response_http_status"] == 200, "HTTP status")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"] == 301606, "complete HTML byte length")
    check(source.get("raw_response_sha256") == SOURCE_SHA, "complete HTML SHA")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 22:06:53 GMT" and source.get("observed_at_utc") == "2026-11-04T22:06:53.474398+00:00", "precise retrieval time receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor") == "source_probe.py", "copyright and reproducibility limits")
    cards, candidates = data.get("all_22_guide_cards", []), discovery.get("episode_slots", [])
    check(type(data.get("observed_full_guide_card_count")) is int and data["observed_full_guide_card_count"] == 22, "full guide traversal not five-only")
    check(isinstance(cards, list) and len(cards) == len(candidates) == 22, "22 publisher cards and candidate slots")
    check(data.get("selected_tranche_episode_ordinals") == [1,2,3,4,5], "five disjoint selected ordinals")
    for field in ("first_five_source_descriptions_inspected", "first_five_analytical_synopses_proposed"):
        check(type(data.get(field)) is int and data[field] == 5, f"actually read five {field}")
    check(type(data.get("first_five_description_total_chars")) is int and sum(card.get("description_chars", -1) for card in cards[:5]) == data["first_five_description_total_chars"] == 712, "712 publisher-description source-text chars")
    check(len({card.get("video_route_path") for card in cards}) == 22, "22 distinct source-local video paths")
    for index, (card, candidate) in enumerate(zip(cards, candidates)):
        ordinal = index+1
        for key in ("display_order", "season", "episode", "analytics_ordinal", "description_chars", "html_anchor_line", "html_description_line"):
            check(type(card.get(key)) is int, f"E{ordinal} integer {key}")
        check(card["display_order"] == card["episode"] == card["analytics_ordinal"] == ordinal, f"E{ordinal} source-local publisher ordinal")
        check(type(candidate.get("episode_number")) is int and candidate.get("episode_number") == ordinal and type(candidate.get("season")) is int and candidate.get("season") == card["season"] == 4, f"E{ordinal} candidate season/ordinal")
        check(card.get("title") == candidate.get("title"), f"E{ordinal} source-local title discovery consistency")
        check(candidate.get("source_binding_id") is None and candidate.get("canonical_work_id") is None, f"E{ordinal} global binding remains unset")
        check(card.get("description_sha256") == EXPECTED_FINGERPRINTS[index] and card.get("video_route_path") == EXPECTED_ROUTES[index], f"E{ordinal} independently pinned fingerprint/route")
        check(card["html_anchor_line"] == 1482+28*index and card["html_description_line"] == 1500+28*index, f"E{ordinal} source lines")
        check(card["description_chars"] >= 50 and bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card["video_route_path"])), f"E{ordinal} description and route syntax")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{ordinal} literal datetime")
        check(card.get("analytics_title") == card.get("title"), f"E{ordinal} analytics description title")
        if ordinal == 22:
            check(card.get("analytics_series_title") == "These Are The Voyages" and card.get("title") == "These Are the Voyages", "E22 exact source-title variants preserved")
            check(card.get("title_variant_status") == "CAPITALIZATION_VARIANT_UNRESOLVED", "E22 case variant explicitly unresolved")
        else:
            check(card.get("analytics_series_title") == card.get("title") and card.get("title_variant_status") == "EXACT_MATCH", f"E{ordinal} exact source title")
    variant = data.get("source_internal_title_variants", [])
    check(variant == [{
        "source_local_episode_hint":22, "display_title":"These Are the Voyages",
        "analytics_title":"These Are the Voyages", "analytics_series_title":"These Are The Voyages",
        "status":"CAPITALIZATION_VARIANT_UNRESOLVED", "global_reconciliation_effect":"NONE"}], "E22 local source-internal conflict preserved with no reconciliation")
    entities, evidences, assertions = (data.get(name, []) for name in ("local_entities", "source_relative_evidence", "typed_assertions"))
    check(len(entities) == len(evidences) == len(assertions) == 5, "five source-local evidence triples")
    ids = [row.get("id") for collection in (entities, evidences, assertions) for row in collection]
    check(len(set(ids)) == 15, "unique local IDs")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        n=i+1
        entity_id, evidence_id = f"ent-s4-e{n:02d}-publisher-card", f"ent-s4-e{n:02d}-guide-description"
        check(entity.get("id") == entity_id and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == n, f"E{n} entity")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{n} unbound Work")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == entity_id, f"E{n} source-relative evidence join")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence["card_ordinal"] == n, f"E{n} evidence")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"] and str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"E{n} description fingerprint/locator")
        prose = evidence.get("original_paraphrase", "")
        check(isinstance(prose,str) and 65 <= len(prose) <= 200 and "\n" not in prose, f"E{n} brief original paraphrase")
        check(assertion.get("id") == f"ent-s4-e{n:02d}-publisher-describes" and assertion.get("evidence_id") == evidence_id and assertion.get("predicate") == "PUBLISHER_DESCRIBES" and assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{n} attributed publisher statement")
    check(len(data.get("holds", [])) >= 6, "source/media/identity holds")


def main() -> int:
    try:
        disc_sha=hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()
        validate(read_json(HERE / "records.json"), read_json(DISCOVERY), disc_sha)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"FAIL ENT S4 E01–E05 HELD: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S4 E01–E05: 22-card complete guide source receipt, 5 HELD publisher synopsis paraphrases, E22 title variant preserved, no Work/CLOSE_READ/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
