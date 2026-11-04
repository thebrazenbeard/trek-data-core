"""Fail-closed Enterprise S3 E06–E10 publisher-description companion audit."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIRST_FIVE = ROOT / "proposals/research/ent/enterprise-s3-first5-official-guide-20261104/records.json"
FIRST_SHA = "05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27"
FIRST_COMMIT = "67e997fe4db0eaa20a96b311c91006520c767848"
FIRST_SOURCE_SHA = "227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391"
LAST_SOURCE_SHA = "0cf747270fe37f0027b4a4c90937e2bd2b2ca91442768e6f7fafcc22adee1253"
EXPECTED_TITLES = ["Exile", "The Shipment", "Twilight", "North Star", "Similitude"]
EXPECTED_HASHES = [
    "9fbfe25466b7f8d670d35c66d480f498884f0ece7b9cbc4050cc8c3fc1c98c53",
    "e797d41bea3abc7f33f89dbfe4702f91168ff002a7c6fd048fa06444e2c1c590",
    "25046c252c40e19250ca307777cee39edffffbb1f8b18f5a9092c4b2ce021915",
    "5065c3891b188cce824b3ba881f682a341d87cb9f973f6bccee5782623f36743",
    "037c1fad4eed589d8633110f841d48adc862349a93ff81a2facf085b264267e3",
]
PROTECTED = ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
             "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect")


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(packet: dict, first: dict, first_sha: str) -> None:
    check(first_sha == FIRST_SHA, "predecessor record bytes drift")
    check(first.get("batch_id") == "ENT.PPLUS.S3.FIRST5.GUIDE.20261104", "predecessor batch identity")
    check(first.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "predecessor held")
    for effect in PROTECTED:
        check(first.get(effect) == "NONE", f"predecessor effect {effect}")
    first_cards = first.get("all_24_guide_cards", [])
    check(len(first_cards) == 24, "predecessor 24-card guide snapshot")
    check([x.get("source_local_episode_hint") for x in first.get("local_entities", [])] == [1, 2, 3, 4, 5], "distinct predecessor scope")

    check(packet.get("schema_version") == "1.0.0", "schema")
    check(packet.get("batch_id") == "ENT.PPLUS.S3.LAST5.GUIDE.20261104", "companion batch identity")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "held ENT worker")
    for effect in PROTECTED:
        check(packet.get(effect) == "NONE", f"protected effect {effect}")
    for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(key) is False, f"false audiovisual claim {key}")
    prior = packet.get("prior_first_five", {})
    check(prior.get("path") == "proposals/research/ent/enterprise-s3-first5-official-guide-20261104/records.json", "source-local predecessor locator")
    check(prior.get("sha256") == first_sha and prior.get("commit") == FIRST_COMMIT, "exact preceding records/commit")
    check(prior.get("source_response_sha256") == first["source"]["raw_response_sha256"] == FIRST_SOURCE_SHA, "predecessor raw source receipt")
    check("E01" in prior.get("scope", "") and "E05" in prior.get("scope", ""), "distinct prior episode scope")
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s3-paramountplus-guide-html-last5-20261104", "source local ID")
    check(source.get("url") == first["source"]["url"] == "https://www.paramountplus.com/shows/enterprise/episodes/3/", "one official publisher guide")
    check(source.get("source_kind") == first["source"]["source_kind"] == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "publisher guide kind")
    check(source.get("independence_group") == first["source"]["independence_group"] == "publisher:paramountplus.com", "not independent publisher evidence")
    check(type(source.get("response_http_status")) is int and source.get("response_http_status") == 200, "HTTP response")
    check(type(source.get("raw_response_bytes")) is int and source.get("raw_response_bytes") == 308190, "complete retrieved HTML length")
    check(source.get("raw_response_sha256") == LAST_SOURCE_SHA, "exact fresh raw HTML receipt")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 21:27:07 GMT", "HTTP Date header")
    check(source.get("observed_at_utc") == "2026-11-04T21:27:07.719354+00:00", "UTC retrieval timestamp")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True, "copyright/volatile raw source hold")
    check(source.get("reproducible_extractor") == "source_probe.py", "reproducible extractor")
    check(packet.get("raw_html_digest_differs_from_predecessor") is True and LAST_SOURCE_SHA != FIRST_SOURCE_SHA, "mutated raw webpage bytes")
    check(packet.get("all_24_metadata_and_description_fingerprints_match_predecessor_snapshot") is True, "normalized 24-card comparison observed")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet.get("observed_full_guide_card_count") == 24, "all 24 source cards observed")
    check(packet.get("selected_tranche_episode_ordinals") == [6, 7, 8, 9, 10], "five unique non-overlapping ordinals")
    for name in ("last_five_source_descriptions_inspected", "last_five_analytical_synopses_proposed"):
        check(type(packet.get(name)) is int and packet.get(name) == 5, f"five actual descriptions {name}")
    cards = packet.get("last_five_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 5, "five source-relative guide cards")
    check([x.get("title") for x in cards] == EXPECTED_TITLES, "five official publisher titles in order")
    check(type(packet.get("last_five_description_total_chars")) is int and
          packet.get("last_five_description_total_chars") == sum(c.get("description_chars", -1) for c in cards) == 836, "actual last-five description lengths")
    check(len({c.get("video_route_path") for c in cards}) == 5, "unique source routes")
    for i, card in enumerate(cards):
        number = i + 6
        check(card == first_cards[number - 1], f"full predecessor source metadata/fingerprint agreement E{number:02d}")
        for key in ("display_order", "season", "episode", "analytics_ordinal", "description_chars", "html_anchor_line", "html_description_line"):
            check(type(card.get(key)) is int, f"strict ordinal/locator type {key} E{number:02d}")
        check(card["display_order"] == card["episode"] == card["analytics_ordinal"] == number and card["season"] == 3, f"E{number:02d} publisher order")
        check(card.get("description_sha256") == EXPECTED_HASHES[i], f"E{number:02d} exact publisher description fingerprint")
        check(card["html_anchor_line"] == 1482 + 28 * (number - 1) and card["html_description_line"] == 1500 + 28 * (number - 1), f"E{number:02d} line locator")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{number:02d} route shape")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{number:02d} publisher datetime")
    entities = packet.get("local_entities", [])
    evidences = packet.get("source_relative_evidence", [])
    assertions = packet.get("typed_assertions", [])
    check(len(entities) == len(evidences) == len(assertions) == 5, "five analyst records")
    first_ids = {x.get("id") for key in ("local_entities", "source_relative_evidence", "typed_assertions") for x in first.get(key, [])}
    last_ids = [x.get("id") for key in ("local_entities", "source_relative_evidence", "typed_assertions") for x in packet.get(key, [])]
    check(len(set(last_ids)) == 15 and not set(last_ids).intersection(first_ids), "distinct first/last evidence IDs, no double count")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        number = i + 6
        local_id = f"ent-s3-e{number:02d}-publisher-card"
        evidence_id = f"ent-s3-e{number:02d}-guide-description"
        check(entity.get("id") == local_id and type(entity.get("source_local_episode_hint")) is int and entity.get("source_local_episode_hint") == number, f"E{number:02d} local entity")
        check(entity.get("canonical_work_id") is None and entity.get("source_kind") == "PUBLISHER_EPISODE_CARD", f"E{number:02d} source local Work hold")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == local_id, f"E{number:02d} evidence joins")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence.get("card_ordinal") == number, f"E{number:02d} evidence class")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"] and str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"E{number:02d} exact description line")
        text = evidence.get("original_paraphrase", "")
        check(isinstance(text, str) and 65 <= len(text) <= 200 and "\n" not in text, f"E{number:02d} bounded original synopsis")
        check(assertion.get("id") == f"ent-s3-e{number:02d}-publisher-describes" and assertion.get("predicate") == "PUBLISHER_DESCRIBES", f"E{number:02d} attributed publisher claim")
        check(assertion.get("evidence_id") == evidence_id and assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{number:02d} not episode truth")
    check(isinstance(packet.get("holds"), list) and len(packet["holds"]) >= 5, "unresolved source/rights holds")


def main() -> int:
    try:
        sha = hashlib.sha256(FIRST_FIVE.read_bytes()).hexdigest()
        validate(read_json(HERE / "records.json"), read_json(FIRST_FIVE), sha)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        print(f"FAIL ENT S3 E06–E10: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S3 E06–E10: 5 publisher descriptions HELD, no duplicates, no Work/CLOSE_READ/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
