"""Deterministic and fail-closed verification of HELD ENT S3 E21–E24 guide packet."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREFIX = ROOT / "proposals/research/ent"
PRIOR = [
    (PREFIX / "enterprise-s3-first5-official-guide-20261104/records.json", "05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27", "67e997fe4db0eaa20a96b311c91006520c767848", "227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391", "ENT.PPLUS.S3.FIRST5.GUIDE.20261104", [1, 2, 3, 4, 5]),
    (PREFIX / "enterprise-s3-last5-official-guide-20261104/records.json", "54e50b5e169a961912f2cde1d1a19bdf8eabfc704bd5b216b40902df9ff302d7", "865291996cf0c16286f1aea05fe562c354a83408", "0cf747270fe37f0027b4a4c90937e2bd2b2ca91442768e6f7fafcc22adee1253", "ENT.PPLUS.S3.LAST5.GUIDE.20261104", [6, 7, 8, 9, 10]),
    (PREFIX / "enterprise-s3-third5-official-guide-20261104/records.json", "f8dd841d56f6551824dbac89739893fb0b924c46743cb96ff6226d6d8fe9572c", "5719fcab4cac59c868d80456cb10a3110e728600", "3a970117c2e224b998be2b223e4f2ee925c41acb8c0c79eca34f4588d89d06c9", "ENT.PPLUS.S3.THIRD5.GUIDE.20261104", [11, 12, 13, 14, 15]),
    (PREFIX / "enterprise-s3-fourth5-official-guide-20261104/records.json", "5783a77f9910588ac4647e9c3ca384faae38912fa893749be5e04d9b032046ca", "e4fac2d43c0e24f7259a9eb22200d4dbcda1ee3f", "b939d2a77786228811338f2c3b3b4d7c2bf0babc289f47768339945e017283bb", "ENT.PPLUS.S3.FOURTH5.GUIDE.20261104", [16, 17, 18, 19, 20]),
]
CURRENT_SHA = "6c27e3a8ab1e8a5b7842f66bc51ecc142abe401aaefa08be201acd6a36aac7be"
TITLES = ["E (squared)", "The Council", "Countdown", "Zero Hour"]
HASHES = [
    "5570b50cb63f0043941cbf9a2469b9414152432f4628384deeb99989055b483a",
    "51e321ada9f03d4b72e64fa5f98e63b4d99b8d8092765c5eef3d4354fbb30956",
    "ab20b5e99082d383d162e6fc721d9d945f0e7f871d89fd5f2b02d45b4485812d",
    "f29bf2d5a9eec9512619456ed68a93dcc0df61527ad11f5eba76bee9025c4343",
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def check(condition: bool, detail: str):
    if not condition:
        raise ValueError(detail)


def validate(packet: dict, predecessors: list[tuple[dict, str]]) -> None:
    check(len(predecessors) == len(PRIOR) == len(packet.get("prior_batches", [])) == 4, "exact four predecessors")
    first_cards = predecessors[0][0].get("all_24_guide_cards", [])
    check(len(first_cards) == 24, "full first-packet inventory of 24")
    prior_ids = set()
    prior_ordinals = []
    for index, ((record, actual_sha), (path, sha, commit, receipt, batch, scope)) in enumerate(zip(predecessors, PRIOR)):
        check(actual_sha == sha, f"predecessor {index} file digest drift")
        check(record.get("batch_id") == batch and record.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", f"predecessor {index} identity/status")
        check(record.get("source", {}).get("raw_response_sha256") == receipt, f"predecessor {index} raw receipt")
        check(record.get("source", {}).get("url") == "https://www.paramountplus.com/shows/enterprise/episodes/3/", f"predecessor {index} publisher URL")
        check(record.get("source", {}).get("independence_group") == "publisher:paramountplus.com", f"predecessor {index} source lineage")
        for effect in EFFECTS:
            check(record.get(effect) == "NONE", f"predecessor {index} protected effect {effect}")
        ordinals = [e.get("source_local_episode_hint") for e in record.get("local_entities", [])]
        check(ordinals == scope, f"predecessor {index} scope")
        prior_ordinals.extend(ordinals)
        reference = packet["prior_batches"][index]
        check(reference.get("path") == str(path.relative_to(ROOT)), f"predecessor {index} locator")
        check(reference.get("sha256") == sha and reference.get("commit") == commit, f"predecessor {index} exact digest/commit")
        check(reference.get("source_response_sha256") == receipt and reference.get("episode_scope") == [scope[0], scope[-1]], f"predecessor {index} receipt/scope")
        for bucket in ("local_entities", "source_relative_evidence", "typed_assertions"):
            for row in record.get(bucket, []):
                check(row.get("id") not in prior_ids, "collision among predecessor IDs")
                prior_ids.add(row.get("id"))

    check(packet.get("schema_version") == "1.0.0" and packet.get("batch_id") == "ENT.PPLUS.S3.FINAL4.GUIDE.20261104", "new batch identity")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "HELD research partition")
    for effect in EFFECTS:
        check(packet.get(effect) == "NONE", f"protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(flag) is False, f"unearned content-reading claim {flag}")
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s3-paramountplus-guide-html-final4-20261104", "source-local ID")
    check(source.get("url") == "https://www.paramountplus.com/shows/enterprise/episodes/3/", "first-party URL")
    check(source.get("independence_group") == "publisher:paramountplus.com" and source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher") == "Paramount+", "publisher class and same lineage")
    check(type(source.get("response_http_status")) is int and source.get("response_http_status") == 200, "HTTP status")
    check(type(source.get("raw_response_bytes")) is int and source.get("raw_response_bytes") == 308190, "entire response byte count")
    check(source.get("raw_response_sha256") == CURRENT_SHA, "fresh raw response hash")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 21:56:03 GMT" and source.get("observed_at_utc") == "2026-11-04T21:56:03.917959+00:00", "exact source time receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor") == "source_probe.py", "no copyrighted HTML storage")
    check(packet.get("all_24_metadata_and_description_fingerprints_match_four_prior_snapshots") is True, "normalized all-card comparison")
    check(packet.get("raw_html_digest_differs_from_four_predecessors") is True and CURRENT_SHA not in [p[3] for p in PRIOR], "dynamic response distinction")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"] == 24, "24 actual publisher guide cards")
    check(packet.get("selected_tranche_episode_ordinals") == [21, 22, 23, 24], "final four only; E25 not implied")
    for key in ("final_four_source_descriptions_inspected", "final_four_analytical_synopses_proposed"):
        check(type(packet.get(key)) is int and packet[key] == 4, f"exact four {key}")
    cards = packet.get("final_four_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 4 and [card.get("title") for card in cards] == TITLES, "four publisher titles")
    check(type(packet.get("final_four_description_total_chars")) is int and sum(card.get("description_chars", -1) for card in cards) == packet["final_four_description_total_chars"] == 699, "699 actually inspected description chars")
    check(len({card.get("video_route_path") for card in cards}) == 4, "distinct publisher metadata routes")
    for index, card in enumerate(cards):
        ordinal = index + 21
        check(card == first_cards[ordinal - 1], f"E{ordinal} complete source-card fingerprint cross-check")
        for key in ("display_order", "season", "episode", "analytics_ordinal", "html_anchor_line", "html_description_line", "description_chars"):
            check(type(card.get(key)) is int, f"E{ordinal} strict integer {key}")
        check(card["season"] == 3 and card["episode"] == card["analytics_ordinal"] == card["display_order"] == ordinal, f"E{ordinal} publisher order")
        check(card["description_sha256"] == HASHES[index], f"E{ordinal} description hash")
        check(card["html_anchor_line"] == 1482 + 28*(ordinal-1) and card["html_description_line"] == 1500 + 28*(ordinal-1), f"E{ordinal} response lines")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{ordinal} metadata route")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{ordinal} publisher date string")
    entities, evidences, assertions = (packet.get(key, []) for key in ("local_entities", "source_relative_evidence", "typed_assertions"))
    check(len(entities) == len(evidences) == len(assertions) == 4, "four distinct evidence triples")
    new_ids = [row.get("id") for bucket in (entities, evidences, assertions) for row in bucket]
    check(len(set(new_ids)) == 12 and not prior_ids.intersection(new_ids), "new IDs do not collide with any earlier tranche")
    for index, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        ordinal = index+21
        eid, vid = f"ent-s3-e{ordinal:02d}-publisher-card", f"ent-s3-e{ordinal:02d}-guide-description"
        check(entity.get("id") == eid and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == ordinal, f"E{ordinal} local episode hint")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{ordinal} Work not admitted")
        check(evidence.get("id") == vid and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == eid, f"E{ordinal} evidence chain")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence["card_ordinal"] == ordinal, f"E{ordinal} source-relative evidence")
        check(evidence.get("publisher_description_sha256") == cards[index]["description_sha256"] and str(cards[index]["html_description_line"]) in evidence.get("locator", ""), f"E{ordinal} locator/hash")
        synopsis = evidence.get("original_paraphrase", "")
        check(isinstance(synopsis, str) and 65 <= len(synopsis) <= 200 and "\n" not in synopsis, f"E{ordinal} original concise paraphrase")
        check(assertion.get("id") == f"ent-s3-e{ordinal:02d}-publisher-describes" and assertion.get("predicate") == "PUBLISHER_DESCRIBES" and assertion.get("evidence_id") == vid, f"E{ordinal} attributed publisher assertion")
        check(assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{ordinal} not audiovisual truth")
    check(prior_ordinals + [row["source_local_episode_hint"] for row in entities] == list(range(1,25)), "all 24 source-local guide cards disjoint, no E25")
    summary = packet.get("held_series_guide_description_partition_summary", {})
    check(summary == {
        "prior_analyses": 20, "this_tranche_analyses": 4,
        "total_nonoverlapping_source_relative_description_proposals": 24,
        "source_local_guide_cards_observed": 24,
        "accepted_work_coverage_or_close_read_claims": 0,
        "final_publisher_card_ordinal": 24,
        "fictional_episode_25_invented": False,
        "status": "HELD_PUBLISHER_GUIDE_DESCRIPTIONS_COMPLETE_NOT_EPISODE_CONTENT_CLOSE_READ",
    }, "strict held publisher-guide-only closure statement")
    check(len(packet.get("holds", [])) >= 5, "explicit method and rights holds")


def main() -> int:
    try:
        prior = [(read_json(path), hashlib.sha256(path.read_bytes()).hexdigest()) for path, *_ in PRIOR]
        validate(read_json(HERE / "records.json"), prior)
    except (OSError, TypeError, KeyError, ValueError) as exc:
        print(f"FAIL ENT S3 E21–E24 HELD: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S3 E21–E24: four HELD publisher-guide descriptions; 24/24 only source-relative proposals, zero Work/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
