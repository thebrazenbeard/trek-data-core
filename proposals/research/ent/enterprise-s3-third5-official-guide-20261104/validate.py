"""Deterministic, fail-closed ENT S3 E11–E15 publisher-guide packet checks."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIRST = ROOT / "proposals/research/ent/enterprise-s3-first5-official-guide-20261104/records.json"
SECOND = ROOT / "proposals/research/ent/enterprise-s3-last5-official-guide-20261104/records.json"
PRIOR = [
    (FIRST, "05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27",
     "67e997fe4db0eaa20a96b311c91006520c767848",
     "227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391",
     "ENT.PPLUS.S3.FIRST5.GUIDE.20261104", [1, 2, 3, 4, 5]),
    (SECOND, "54e50b5e169a961912f2cde1d1a19bdf8eabfc704bd5b216b40902df9ff302d7",
     "865291996cf0c16286f1aea05fe562c354a83408",
     "0cf747270fe37f0027b4a4c90937e2bd2b2ca91442768e6f7fafcc22adee1253",
     "ENT.PPLUS.S3.LAST5.GUIDE.20261104", [6, 7, 8, 9, 10]),
]
CURRENT_SHA = "3a970117c2e224b998be2b223e4f2ee925c41acb8c0c79eca34f4588d89d06c9"
TITLES = ["Carpenter Street", "Chosen Realm", "Proving Ground", "Strategem", "Harbinger"]
HASHES = [
    "d4ae4a81b47e18f99f6f11f49770ae36cdd9eeceb31fdef1bdadf2582f24eaec",
    "7102998269532aee2e019d5118093a6933c5b0e58633c5307ae9b99c126e2c59",
    "2e5062a9c9591dbd0ffd3fbea9f2fc70e9f37df8bc2447da3fe9d2ace0894340",
    "1f8253ca8affbe9098730f499b4b34188dc28520acfd769b1a012ab7df977ef7",
    "cb5fdbad86dbb29369ec7340bfafebf12168f8a0c2c10230722fa105d4d40029",
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def no_dup(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key}")
            out[key] = value
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_dup)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(packet: dict, predecessors: list[tuple[dict, str]]) -> None:
    check(len(predecessors) == 2 and len(packet.get("prior_batches", [])) == 2, "two exact predecessor tranches")
    first, second = [record for record, _ in predecessors]
    all_first_cards = first.get("all_24_guide_cards", [])
    check(len(all_first_cards) == 24, "first full publisher guide inventory")
    prior_ids = set()
    for i, ((prior_record, actual_sha), (prior_path, expected_sha, commit, receipt_sha, batch, ordinals)) in enumerate(zip(predecessors, PRIOR)):
        check(actual_sha == expected_sha, f"predecessor file SHA drift {i}")
        check(prior_record.get("batch_id") == batch and prior_record.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", f"predecessor identity {i}")
        check(prior_record.get("source", {}).get("raw_response_sha256") == receipt_sha, f"prior receipt {i}")
        for effect in EFFECTS:
            check(prior_record.get(effect) == "NONE", f"predecessor protected effect {effect} {i}")
        check([x.get("source_local_episode_hint") for x in prior_record.get("local_entities", [])] == ordinals, f"predecessor non-overlapping scope {i}")
        reference = packet["prior_batches"][i]
        check(reference.get("path") == str(prior_path.relative_to(ROOT)), f"prior locator {i}")
        check(reference.get("sha256") == expected_sha and reference.get("commit") == commit, f"prior exact local file/commit {i}")
        check(reference.get("source_response_sha256") == receipt_sha, f"prior exact page receipt {i}")
        for bucket in ("local_entities", "source_relative_evidence", "typed_assertions"):
            for row in prior_record.get(bucket, []):
                check(row.get("id") not in prior_ids, "predecessor ID collision")
                prior_ids.add(row.get("id"))
    check(packet.get("schema_version") == "1.0.0", "schema")
    check(packet.get("batch_id") == "ENT.PPLUS.S3.THIRD5.GUIDE.20261104", "batch identity")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "held ENT partition")
    for effect in EFFECTS:
        check(packet.get(effect) == "NONE", f"new protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(flag) is False, f"unearned source reading flag {flag}")
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s3-paramountplus-guide-html-third5-20261104", "source-local ID")
    check(source.get("url") == first["source"]["url"] == second["source"]["url"] == "https://www.paramountplus.com/shows/enterprise/episodes/3/", "one first-party guide URL")
    check(source.get("independence_group") == first["source"]["independence_group"] == second["source"]["independence_group"] == "publisher:paramountplus.com", "single source lineage")
    check(source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher") == "Paramount+", "source class")
    check(type(source.get("response_http_status")) is int and source.get("response_http_status") == 200, "exact response status")
    check(type(source.get("raw_response_bytes")) is int and source.get("raw_response_bytes") == 308190, "complete response bytes")
    check(source.get("raw_response_sha256") == CURRENT_SHA, "fresh exact raw response SHA")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 21:36:32 GMT", "HTTP Date")
    check(source.get("observed_at_utc") == "2026-11-04T21:36:32.669611+00:00", "UTC timestamp")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True, "copyright/raw HTML retention hold")
    check(source.get("reproducible_extractor") == "source_probe.py", "extractor provenance")
    check(packet.get("all_24_metadata_and_description_fingerprints_match_both_prior_snapshots") is True, "all-card normalized lineage comparison")
    check(packet.get("raw_html_digest_differs_from_both_predecessors") is True and CURRENT_SHA not in [x[3] for x in PRIOR], "dynamic raw HTML differs")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet.get("observed_full_guide_card_count") == 24, "full guide traversal")
    check(packet.get("selected_tranche_episode_ordinals") == [11, 12, 13, 14, 15], "distinct third tranche ordinals")
    for label in ("third_five_source_descriptions_inspected", "third_five_analytical_synopses_proposed"):
        check(type(packet.get(label)) is int and packet[label] == 5, f"five actually processed {label}")
    cards = packet.get("third_five_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 5 and [x.get("title") for x in cards] == TITLES, "five exact source-card titles")
    check(type(packet.get("third_five_description_total_chars")) is int and sum(c.get("description_chars", -1) for c in cards) == packet.get("third_five_description_total_chars") == 957, "957 source-description characters actually read")
    check(len({c.get("video_route_path") for c in cards}) == 5, "five distinct publisher routes")
    for i, card in enumerate(cards):
        ordinal = i + 11
        check(card == all_first_cards[ordinal - 1], f"E{ordinal:02d} source-card lineage match")
        for key in ("season", "episode", "analytics_ordinal", "display_order", "html_anchor_line", "html_description_line", "description_chars"):
            check(type(card.get(key)) is int, f"E{ordinal:02d} strict integer {key}")
        check(card["season"] == 3 and card["episode"] == card["analytics_ordinal"] == card["display_order"] == ordinal, f"E{ordinal:02d} guide ordinal")
        check(card.get("description_sha256") == HASHES[i], f"E{ordinal:02d} exact description fingerprint")
        check(card.get("html_anchor_line") == 1482 + 28 * (ordinal - 1) and card.get("html_description_line") == 1500 + 28 * (ordinal - 1), f"E{ordinal:02d} HTML line")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{ordinal:02d} video route locator")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{ordinal:02d} publisher datetime")
    entities = packet.get("local_entities", [])
    evidences = packet.get("source_relative_evidence", [])
    assertions = packet.get("typed_assertions", [])
    check(len(entities) == len(evidences) == len(assertions) == 5, "five source-local entities, evidence and assertions")
    new_ids = [r.get("id") for bucket in (entities, evidences, assertions) for r in bucket]
    check(len(set(new_ids)) == 15 and not set(new_ids).intersection(prior_ids), "no local ID collision among three tranches")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        number = i + 11
        entity_id = f"ent-s3-e{number:02d}-publisher-card"
        evidence_id = f"ent-s3-e{number:02d}-guide-description"
        check(entity.get("id") == entity_id and type(entity.get("source_local_episode_hint")) is int and entity.get("source_local_episode_hint") == number, f"E{number:02d} local entity ID")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{number:02d} Work remains unknown")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == entity_id, f"E{number:02d} evidence links")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence.get("card_ordinal") == number, f"E{number:02d} evidence class")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"] and str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"E{number:02d} source fingerprints")
        summary = evidence.get("original_paraphrase", "")
        check(isinstance(summary, str) and 65 <= len(summary) <= 200 and "\n" not in summary, f"E{number:02d} original concise paraphrase")
        check(assertion.get("id") == f"ent-s3-e{number:02d}-publisher-describes" and assertion.get("predicate") == "PUBLISHER_DESCRIBES", f"E{number:02d} attributed claim")
        check(assertion.get("evidence_id") == evidence_id and assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{number:02d} not actual episode truth")
    check(len(packet.get("holds", [])) >= 5, "explicit research and rights holds")


def main() -> int:
    try:
        prior = [(read_json(path), hashlib.sha256(path.read_bytes()).hexdigest()) for path, *_ in PRIOR]
        validate(read_json(HERE / "records.json"), prior)
    except (OSError, TypeError, KeyError, ValueError) as exc:
        print(f"FAIL ENT S3 E11–E15: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S3 E11–E15: 5 source-relative publisher synopses HELD, 3 non-overlapping batches, no coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
