"""Fail-closed ENT S4 E06–E10 publisher-guide receipt and prior-batch verification."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIRST_DIR = HERE.parent / "enterprise-s4-first5-official-guide-20261104"
FIRST = FIRST_DIR / "records.json"
FIRST_SHA = "f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10"
FIRST_COMMIT = "9da214b3231870c3879f9f645e9bf9e9ab6f7c53"
FIRST_RECEIPT = "e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392"
CURRENT_RECEIPT = "45b350714aa0d57596d38977018664e116e790f9186671999988c638e08d55e8"
TITLES = ["The Augments", "The Forge", "Awakening", "Kir'Shara", "Daedalus"]
HASHES = [
    "739295c7b2a8253ff2571357b5cd9631583671c0fbfebc6928a641cd2f156c12",
    "47ae93ad886d52f46f1ab82dd517ec73665b99c86eaba6cffadd8a43eb7d5e29",
    "352fe70f2709ef74f953c4fe5781ff3c34a359ec14afa96738b81ec64d6ca1cd",
    "bded78321051f42921244c738e156cbd6e8b2dd80165e74ce3fea067a55e32de",
    "9c1e2540da710e80246cf015b1d27ed88c776fc573bfe2b3ae276282c33a0456",
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_predecessor(first: dict, digest: str) -> None:
    check(digest == FIRST_SHA, "exact predecessor file digest")
    check(first.get("batch_id") == "ENT.PPLUS.S4.FIRST5.GUIDE.20261104", "previous batch ID")
    check(first.get("source", {}).get("raw_response_sha256") == FIRST_RECEIPT, "previous raw source receipt")
    for effect in EFFECTS:
        check(first.get(effect) == "NONE", f"predecessor effect {effect}")
    check([e.get("source_local_episode_hint") for e in first.get("local_entities", [])] == [1,2,3,4,5], "prior five source-local entities")
    # Also run the exact predecessor's independent bound-discovery validator.
    spec = importlib.util.spec_from_file_location("ent_s4_first5_validator", FIRST_DIR / "validate.py")
    check(spec is not None and spec.loader is not None, "predecessor validator import")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    discovery_digest = hashlib.sha256(module.DISCOVERY.read_bytes()).hexdigest()
    module.validate(first, module.read_json(module.DISCOVERY), discovery_digest)


def validate(packet: dict, predecessor: dict, predecessor_sha: str) -> None:
    check_predecessor(predecessor, predecessor_sha)
    check(packet.get("schema_version") == "1.0.0" and packet.get("batch_id") == "ENT.PPLUS.S4.SECOND5.GUIDE.20261104", "second-batch ID")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "held ENT lane")
    for effect in EFFECTS:
        check(packet.get(effect) == "NONE", f"protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(flag) is False, f"unearned content read {flag}")
    prior = packet.get("prior_batch", {})
    check(prior == {
        "path":"proposals/research/ent/enterprise-s4-first5-official-guide-20261104/records.json",
        "sha256":FIRST_SHA, "commit":FIRST_COMMIT, "source_response_sha256":FIRST_RECEIPT,
        "episode_scope":[1,5]}, "exact prior local packet/commit receipt")
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s4-paramountplus-guide-html-second5-20261104", "source-local ID")
    check(source.get("url") == predecessor["source"]["url"] == "https://www.paramountplus.com/shows/enterprise/episodes/4/", "same official publisher guide")
    check(source.get("publisher") == "Paramount+" and source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "first-party source class")
    check(source.get("independence_group") == predecessor["source"]["independence_group"] == "publisher:paramountplus.com", "same lineage not second witness")
    check(type(source.get("response_http_status")) is int and source.get("response_http_status") == 200, "HTTP 200")
    check(type(source.get("raw_response_bytes")) is int and source.get("raw_response_bytes") == 301606, "complete HTML response byte count")
    check(source.get("raw_response_sha256") == CURRENT_RECEIPT, "new exact raw HTML response")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 22:14:11 GMT" and source.get("observed_at_utc") == "2026-11-04T22:14:11.211831+00:00", "HTTP Date and UTC exact receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor") == "source_probe.py", "raw copyrighted response absent")
    check(packet.get("raw_html_digest_differs_from_predecessor") is True and CURRENT_RECEIPT != FIRST_RECEIPT, "two dynamic HTML response hashes")
    check(packet.get("all_22_metadata_and_description_fingerprints_match_prior_snapshot") is True, "all-card normalized comparison")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"] == 22, "full guide read not five-only")
    complete = packet.get("all_22_guide_cards", [])
    check(complete == predecessor.get("all_22_guide_cards") and len(complete) == 22, "all 22 normalized cards exact agreement across two full page reads")
    check(packet.get("selected_tranche_episode_ordinals") == [6,7,8,9,10], "bounded non-overlapping second five")
    for field in ("second_five_source_descriptions_inspected", "second_five_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field] == 5, f"actual second five {field}")
    cards = packet.get("second_five_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 5 and [c.get("title") for c in cards] == TITLES, "five source-local publisher titles")
    check(type(packet.get("second_five_description_total_chars")) is int and sum(c.get("description_chars", -1) for c in cards) == packet["second_five_description_total_chars"] == 723, "723 inspected source-description chars")
    check(len({card.get("video_route_path") for card in cards}) == 5, "five metadata locators")
    for i, card in enumerate(cards):
        ordinal=i+6
        check(card == complete[ordinal-1], f"E{ordinal} full-guide source card matches")
        for field in ("season", "episode", "display_order", "analytics_ordinal", "html_anchor_line", "html_description_line", "description_chars"):
            check(type(card.get(field)) is int, f"E{ordinal} typed integer {field}")
        check(card["season"] == 4 and card["episode"] == card["display_order"] == card["analytics_ordinal"] == ordinal, f"E{ordinal} source-local ordinal")
        check(card.get("description_sha256") == HASHES[i], f"E{ordinal} independently pinned description hash")
        check(card["html_anchor_line"] == 1482 + 28*(ordinal-1) and card["html_description_line"] == 1500 + 28*(ordinal-1), f"E{ordinal} exact source line")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{ordinal} route syntax")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{ordinal} date literal")
    check(packet.get("source_internal_title_variant_reobserved") == {
        "source_local_episode_hint":22, "display_title":"These Are the Voyages",
        "analytics_title":"These Are the Voyages", "analytics_series_title":"These Are The Voyages",
        "status":"CAPITALIZATION_VARIANT_UNRESOLVED", "global_reconciliation_effect":"NONE"}, "E22 source-internal capitalization variant persists unresolved")
    entities, evidences, assertions = (packet.get(name, []) for name in ("local_entities", "source_relative_evidence", "typed_assertions"))
    check(len(entities) == len(evidences) == len(assertions) == 5, "five local evidence/claim triples")
    ids = [row.get("id") for bucket in (entities, evidences, assertions) for row in bucket]
    prior_ids = [row.get("id") for bucket in (predecessor["local_entities"], predecessor["source_relative_evidence"], predecessor["typed_assertions"]) for row in bucket]
    check(len(set(ids)) == 15 and not set(ids).intersection(prior_ids), "no cross-batch local ID collision")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        ordinal = i+6
        eid, vid = f"ent-s4-e{ordinal:02d}-publisher-card", f"ent-s4-e{ordinal:02d}-guide-description"
        check(entity.get("id") == eid and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == ordinal, f"E{ordinal} local entity ID")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{ordinal} unbound Work")
        check(evidence.get("id") == vid and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == eid, f"E{ordinal} evidence join")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence["card_ordinal"] == ordinal, f"E{ordinal} source evidence")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"] and str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"E{ordinal} hashed description locator")
        summary = evidence.get("original_paraphrase", "")
        check(isinstance(summary, str) and 65 <= len(summary) <= 200 and "\n" not in summary, f"E{ordinal} concise original paraphrase")
        check(assertion.get("id") == f"ent-s4-e{ordinal:02d}-publisher-describes" and assertion.get("evidence_id") == vid and assertion.get("predicate") == "PUBLISHER_DESCRIBES", f"E{ordinal} source-attributed claim")
        check(assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{ordinal} no episode truth claim")
    check([x["source_local_episode_hint"] for x in predecessor["local_entities"] + entities] == list(range(1,11)), "ten disjoint source-relative proposals")
    check(packet.get("held_season_description_partition_summary") == {
        "prior_analyses":5, "this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":10,
        "source_local_guide_cards_observed":22,
        "remaining_unprocessed_publisher_descriptions":12,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ"}, "strict 10/22 held publisher-description status not coverage")
    check(len(packet.get("holds", [])) >= 5, "explicit research/rights holds")


def main() -> int:
    try:
        first_sha = hashlib.sha256(FIRST.read_bytes()).hexdigest()
        validate(read_json(HERE / "records.json"), read_json(FIRST), first_sha)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"FAIL ENT S4 E06–E10 HELD: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S4 E06–E10: five HELD publisher synopses, ten disjoint description proposals, no Work/CLOSE_READ/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
