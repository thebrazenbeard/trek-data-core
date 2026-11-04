"""Fail-closed source-relative publisher-guide checks for ENT S4 E16–E20 HELD."""

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
SECOND_DIR = HERE.parent / "enterprise-s4-second5-official-guide-20261104"
THIRD_DIR = HERE.parent / "enterprise-s4-third5-official-guide-20261104"
PRIOR = [
    (FIRST_DIR / "records.json", "f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10", "9da214b3231870c3879f9f645e9bf9e9ab6f7c53", "e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392", "ENT.PPLUS.S4.FIRST5.GUIDE.20261104", [1,2,3,4,5]),
    (SECOND_DIR / "records.json", "a21928c263501e34be287ffd2c8524267ab30fa50e19dca1262ae8c0b9e49b05", "1bd2d94506815a2039d95a5dbabc932ef6a35cfd", "45b350714aa0d57596d38977018664e116e790f9186671999988c638e08d55e8", "ENT.PPLUS.S4.SECOND5.GUIDE.20261104", [6,7,8,9,10]),
    (THIRD_DIR / "records.json", "8515c84c55a4dd13d622d4d249624ed0b70b54e0a939ec792ee23cc13bf4bba7", "1dcd8662c2e7f0fdd7c9fd60fce789a28f2e841c", "07d67fdee1a556a92367d9e22913d8bc8bf26806c5d753a1113b189e4f85fde3", "ENT.PPLUS.S4.THIRD5.GUIDE.20261104", [11,12,13,14,15]),
]
CURRENT_SHA = "aa3731ca64e8022d2090cc833f420fb6ab367575d870ea102d9146c60461b04e"
TITLES = ["Divergence", "Bound", "In a Mirror, Darkly, Pt. 1", "In A Mirror, Darkly, Pt 2", "Demons"]
HASHES = [
    "f167b224da7cbd93f181dac161fc8886d69ba0decd3cc45a8ec606972824bfcf",
    "1690a6918b7a68894bae542dad95b8ec2e5ae2b31ddd7775e8a17c9f58fcdb92",
    "56afde4fd595b85776d0527011bf3c9adbf33db03bd56ee3ab612baaeba6cd31",
    "701428343bc7690929b7bcf2ac5f53e82579d5bed64aa7a99e52b56abbfd840c",
    "0c0195adbe71a85a6228aee12aae873031cfdbe33d6168dfd49abaffb0211cd4",
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_prior_records(predecessors: list[tuple[dict, str]]) -> None:
    check(len(predecessors) == 3, "exact three predecessor source tranches")
    for index, ((record, actual_sha), (path, expected_sha, commit, receipt_sha, batch_id, ordinals)) in enumerate(zip(predecessors, PRIOR)):
        check(actual_sha == expected_sha, f"prior record file digest {index}")
        check(record.get("batch_id") == batch_id and record.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", f"prior held identity {index}")
        check(record.get("source", {}).get("raw_response_sha256") == receipt_sha, f"prior raw HTML receipt {index}")
        check([r.get("source_local_episode_hint") for r in record.get("local_entities", [])] == ordinals, f"prior scope {index}")
        for effect in EFFECTS:
            check(record.get(effect) == "NONE", f"prior protected effect {index} {effect}")
        # Re-run first-party crosswalk and second-tranche deterministic validation,
        # rather than assuming two checksums imply honest source-relative analysis.
        mod_path = path.parent / "validate.py"
        spec = importlib.util.spec_from_file_location(f"ent_s4_prior_{index}", mod_path)
        check(spec is not None and spec.loader is not None, f"prior validator import {index}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if index == 0:
            discovered_sha = hashlib.sha256(mod.DISCOVERY.read_bytes()).hexdigest()
            mod.validate(record, mod.read_json(mod.DISCOVERY), discovered_sha)
        elif index == 1:
            mod.validate(record, predecessors[0][0], predecessors[0][1])
        else:
            mod.validate(record, predecessors[:2])


def validate(packet: dict, predecessors: list[tuple[dict, str]]) -> None:
    check_prior_records(predecessors)
    check(len(packet.get("prior_batches", [])) == 3, "three exact prior manifest links")
    prior_ids = set()
    prior_ordinals = []
    first, second, third = [record for record, _ in predecessors]
    for index, ((record, digest), (path, expected, commit, raw_sha, batch_id, ordinals)) in enumerate(zip(predecessors, PRIOR)):
        reference = packet["prior_batches"][index]
        check(reference == {
            "path":str(path.relative_to(ROOT)), "sha256":expected,
            "commit":commit, "source_response_sha256":raw_sha,
            "episode_scope":[ordinals[0], ordinals[-1]]}, f"exact prior package receipt {index}")
        prior_ordinals.extend(ordinals)
        for bucket in ("local_entities", "source_relative_evidence", "typed_assertions"):
            for row in record.get(bucket, []):
                check(row.get("id") not in prior_ids, "duplicate predecessor ID")
                prior_ids.add(row.get("id"))
    check(packet.get("schema_version") == "1.0.0" and packet.get("batch_id") == "ENT.PPLUS.S4.FOURTH5.GUIDE.20261104", "batch identity")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "HELD ENT partition")
    for effect in EFFECTS:
        check(packet.get(effect) == "NONE", f"new protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(flag) is False, f"unearned content access {flag}")
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s4-paramountplus-guide-html-fourth5-20261104", "source-local ID")
    check(source.get("url") == first["source"]["url"] == second["source"]["url"] == third["source"]["url"] == "https://www.paramountplus.com/shows/enterprise/episodes/4/", "same first-party guide")
    check(source.get("independence_group") == first["source"]["independence_group"] == second["source"]["independence_group"] == third["source"]["independence_group"] == "publisher:paramountplus.com", "one source lineage not three witnesses")
    check(source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher") == "Paramount+", "publisher class")
    check(type(source.get("response_http_status")) is int and source["response_http_status"] == 200, "HTTP status")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"] == 301606, "full response bytes")
    check(source.get("raw_response_sha256") == CURRENT_SHA, "fresh response hash")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 22:29:51 GMT" and source.get("observed_at_utc") == "2026-11-04T22:29:51.676867+00:00", "source retrieval timestamps")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor") == "source_probe.py", "copyright/raw source custody")
    check(packet.get("all_22_metadata_and_description_fingerprints_match_three_prior_snapshots") is True, "normalized source repeatability")
    check(packet.get("raw_html_digest_differs_from_three_predecessors") is True and CURRENT_SHA not in (PRIOR[0][3],PRIOR[1][3],PRIOR[2][3]), "dynamic HTML differs from both prior raw receipts")
    check(type(packet.get("observed_full_guide_card_count")) is int and packet["observed_full_guide_card_count"] == 22, "full guide traversal")
    full = packet.get("all_22_guide_cards", [])
    check(len(full) == 22 and full == first.get("all_22_guide_cards") == second.get("all_22_guide_cards") == third.get("all_22_guide_cards"), "22 normalized cards exactly match two full-guide snapshots")
    check(packet.get("selected_tranche_episode_ordinals") == [16,17,18,19,20], "distinct fourth five only")
    for field in ("fourth_five_source_descriptions_inspected", "fourth_five_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field] == 5, f"five actually processed {field}")
    cards = packet.get("fourth_five_guide_cards", [])
    check(isinstance(cards,list) and len(cards) == 5 and [card.get("title") for card in cards] == TITLES, "exact five publisher titles")
    check(type(packet.get("fourth_five_description_total_chars")) is int and sum(c.get("description_chars",-1) for c in cards) == packet["fourth_five_description_total_chars"] == 681, "721 source-text description chars")
    check(len({c.get("video_route_path") for c in cards}) == 5, "five distinct source metadata routes")
    for index, card in enumerate(cards):
        n=index+16
        check(card == full[n-1], f"E{n} exact full-guide source metadata")
        for field in ("display_order", "season", "episode", "analytics_ordinal", "html_anchor_line", "html_description_line", "description_chars"):
            check(type(card.get(field)) is int, f"E{n} strict integer {field}")
        check(card["season"] == 4 and card["episode"] == card["display_order"] == card["analytics_ordinal"] == n, f"E{n} source ordinal")
        check(card.get("description_sha256") == HASHES[index], f"E{n} exact publisher description fingerprint")
        check(card["html_anchor_line"] == 1482+28*(n-1) and card["html_description_line"] == 1500+28*(n-1), f"E{n} source HTML lines")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{n} source video locator only")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{n} date literal")
    check(packet.get("source_internal_title_variant_reobserved") == {
        "source_local_episode_hint":22, "display_title":"These Are the Voyages",
        "analytics_title":"These Are the Voyages", "analytics_series_title":"These Are The Voyages",
        "status":"CAPITALIZATION_VARIANT_UNRESOLVED", "global_reconciliation_effect":"NONE"}, "E22 title conflict is preserved")
    entities,evidence,assertions=(packet.get(x,[]) for x in ("local_entities", "source_relative_evidence", "typed_assertions"))
    check(len(entities) == len(evidence) == len(assertions) == 5, "five local entity/evidence/typed assertion chains")
    new_ids=[r.get("id") for bucket in (entities,evidence,assertions) for r in bucket]
    check(len(set(new_ids)) == 15 and not set(new_ids).intersection(prior_ids), "unique across all three tranches")
    for index,(entity,ev,assertion) in enumerate(zip(entities,evidence,assertions)):
        n=index+16
        eid,vid=f"ent-s4-e{n:02d}-publisher-card",f"ent-s4-e{n:02d}-guide-description"
        check(entity.get("id") == eid and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == n, f"E{n} local entity")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{n} Work identity unbound")
        check(ev.get("id") == vid and ev.get("source_id") == source["local_source_id"] and ev.get("local_entity_id") == eid, f"E{n} evidence links")
        check(ev.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"] == n, f"E{n} source-relative evidence class")
        check(ev.get("publisher_description_sha256") == cards[index]["description_sha256"] and str(cards[index]["html_description_line"]) in ev.get("locator", ""), f"E{n} source evidence fingerprint")
        synopsis=ev.get("original_paraphrase", "")
        check(isinstance(synopsis,str) and 65 <= len(synopsis) <= 200 and "\n" not in synopsis, f"E{n} original short paraphrase")
        check(assertion.get("id") == f"ent-s4-e{n:02d}-publisher-describes" and assertion.get("predicate") == "PUBLISHER_DESCRIBES" and assertion.get("evidence_id") == vid, f"E{n} publisher-attributed assertion")
        check(assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{n} source-relative only")
        check(assertion.get("claimed_narrative_frame") == ("MIRROR_UNIVERSE" if n in (18,19) else "UNSPECIFIED") and assertion.get("frame_claim_status") == "PUBLISHER_DESCRIPTION_ONLY", f"E{n} source-relative frame claim")
    check(prior_ordinals + [r["source_local_episode_hint"] for r in entities] == list(range(1,21)), "15 disjoint publisher-description proposals")
    check(packet.get("held_season_description_partition_summary") == {
        "prior_analyses":15, "this_tranche_analyses":5,
        "total_nonoverlapping_source_relative_description_proposals":20,
        "source_local_guide_cards_observed":22,
        "remaining_unprocessed_publisher_descriptions":2,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PARTIAL_PUBLISHER_GUIDE_DESCRIPTIONS_NOT_EPISODE_CONTENT_CLOSE_READ"}, "strict held count and unfinished frontier")
    check(len(packet.get("holds",[])) >= 7, "rights/method holds")


def main() -> int:
    try:
        predecessors=[(read_json(path),hashlib.sha256(path.read_bytes()).hexdigest()) for path,*_ in PRIOR]
        validate(read_json(HERE / "records.json"), predecessors)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(f"FAIL ENT S4 E16–E20: {exc}",file=sys.stderr)
        return 1
    print("PASS ENT S4 E16–E20: five HELD publisher descriptions; 20 disjoint analyses, two unprocessed; zero accepted Work/CLOSE_READ/coverage")
    return 0


if __name__=="__main__":
    sys.exit(main())
