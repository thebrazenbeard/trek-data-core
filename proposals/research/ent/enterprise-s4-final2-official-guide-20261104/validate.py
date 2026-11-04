"""Fail-closed custody and coverage boundary for final ENT S4 guide tranche."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SIBLING = HERE.parent
PRIOR = [
    ("enterprise-s4-first5-official-guide-20261104", "f8e65b062b7b53929341d6dbca31dd20f29bf09f995b9a5daf628dc12b6e4f10", "9da214b3231870c3879f9f645e9bf9e9ab6f7c53", "e0a5c2910e2f9cd43a3316d1bbbc06774c9d76eec422829f0f60fd9630eb6392", "ENT.PPLUS.S4.FIRST5.GUIDE.20261104", list(range(1, 6))),
    ("enterprise-s4-second5-official-guide-20261104", "a21928c263501e34be287ffd2c8524267ab30fa50e19dca1262ae8c0b9e49b05", "1bd2d94506815a2039d95a5dbabc932ef6a35cfd", "45b350714aa0d57596d38977018664e116e790f9186671999988c638e08d55e8", "ENT.PPLUS.S4.SECOND5.GUIDE.20261104", list(range(6, 11))),
    ("enterprise-s4-third5-official-guide-20261104", "8515c84c55a4dd13d622d4d249624ed0b70b54e0a939ec792ee23cc13bf4bba7", "1dcd8662c2e7f0fdd7c9fd60fce789a28f2e841c", "07d67fdee1a556a92367d9e22913d8bc8bf26806c5d753a1113b189e4f85fde3", "ENT.PPLUS.S4.THIRD5.GUIDE.20261104", list(range(11, 16))),
    ("enterprise-s4-fourth5-official-guide-20261104", "d84d077f9eb8ca82ec02f9962dfc2a78166f11f7dc1001aab7b37e5894bd9a5a", "c055a88d742ea48a4e095b9861cd6308811ca731", "aa3731ca64e8022d2090cc833f420fb6ab367575d870ea102d9146c60461b04e", "ENT.PPLUS.S4.FOURTH5.GUIDE.20261104", list(range(16, 21))),
]
SOURCE_SHA = "8790bff4111c5ad3b0bafc1491189373998eae3b3498addddb6594d7237418a9"
EXPECTED_FINAL = [
    ("Terra Prime", "8feccc9522fde17b61d59a9dc0526bd60c3b985868b3a69c05b3f63fe433f903", 109, 2042, 2060),
    ("These Are the Voyages", "2e73d100233573f99ffcec035e3d40692d40a727afd4769daffbd779c09795cd", 123, 2070, 2088),
]
EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check_predecessors(predecessors: list[tuple[dict, str]]) -> None:
    check(len(predecessors) == 4, "exact four predecessor tranches")
    for index, ((record, observed_sha), (directory, digest, commit, raw_sha, batch_id, ordinals)) in enumerate(zip(predecessors, PRIOR)):
        check(observed_sha == digest, f"prior file digest {index}")
        check(record.get("batch_id") == batch_id and record.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", f"prior identity {index}")
        check(record.get("source", {}).get("raw_response_sha256") == raw_sha, f"prior first-party response receipt {index}")
        check([row.get("source_local_episode_hint") for row in record.get("local_entities", [])] == ordinals, f"prior nonoverlap {index}")
        for effect in EFFECTS:
            check(record.get(effect) == "NONE", f"prior protected effect {index} {effect}")
        module_path = SIBLING / directory / "validate.py"
        spec = importlib.util.spec_from_file_location(f"ent_s4_final_prior_{index}", module_path)
        check(spec is not None and spec.loader is not None, "prior validator import")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if index == 0:
            digest_discovery = hashlib.sha256(mod.DISCOVERY.read_bytes()).hexdigest()
            mod.validate(record, mod.read_json(mod.DISCOVERY), digest_discovery)
        elif index == 1:
            mod.validate(record, predecessors[0][0], predecessors[0][1])
        else:
            mod.validate(record, predecessors[:index])


def validate(packet: dict, predecessors: list[tuple[dict, str]]) -> None:
    check_predecessors(predecessors)
    check(packet.get("schema_version") == "1.0.0" and packet.get("batch_id") == "ENT.PPLUS.S4.FINAL2.GUIDE.20261104", "packet identity")
    check(packet.get("role") == "ENT" and packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "held ENT boundary")
    for effect in EFFECTS:
        check(packet.get(effect) == "NONE", f"new protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(flag) is False, f"unearned source access {flag}")
    check(len(packet.get("prior_batches", [])) == 4, "four predecessor receipts")
    ids, ordinals = set(), []
    for i, ((record, observed_sha), (directory, digest, commit, raw_sha, batch_id, scoped)) in enumerate(zip(predecessors, PRIOR)):
        ref = packet["prior_batches"][i]
        check(ref == {
            "path":str((SIBLING / directory / "records.json").relative_to(ROOT)), "sha256":digest,
            "commit":commit, "source_response_sha256":raw_sha,
            "episode_scope":[scoped[0], scoped[-1]],
        }, f"exact predecessor receipt {i}")
        ordinals.extend(scoped)
        for bucket in ("local_entities", "source_relative_evidence", "typed_assertions"):
            for row in record.get(bucket, []):
                ident = row.get("id")
                check(ident not in ids and isinstance(ident, str), f"predecessor ID collision {i}")
                ids.add(ident)
    source = packet.get("source", {})
    check(source.get("local_source_id") == "ent-s4-paramountplus-guide-html-final2-20261104", "local source identity")
    for record, _ in predecessors:
        check(source.get("url") == record.get("source", {}).get("url") == "https://www.paramountplus.com/shows/enterprise/episodes/4/", "same publisher URL")
        check(source.get("independence_group") == record.get("source", {}).get("independence_group") == "publisher:paramountplus.com", "one source lineage")
    check(source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML" and source.get("publisher") == "Paramount+", "first-party guide class")
    check(type(source.get("response_http_status")) is int and source["response_http_status"] == 200, "HTTP 200 observed")
    check(type(source.get("raw_response_bytes")) is int and source["raw_response_bytes"] == 301606, "complete HTML source size")
    check(source.get("raw_response_sha256") == SOURCE_SHA, "exact response fingerprint")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 22:38:16 GMT" and source.get("observed_at_utc") == "2026-11-04T22:38:16.420232+00:00", "timestamp receipt")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True and source.get("reproducible_extractor") == "source_probe.py", "copyright/raw HTML custody")
    check(packet.get("observed_full_guide_card_count") == 22 and type(packet["observed_full_guide_card_count"]) is int, "entire source guide count")
    check(packet.get("all_22_metadata_and_description_fingerprints_match_four_prior_snapshots") is True, "normalized four-repeat agreement")
    check(packet.get("raw_html_digest_differs_from_four_predecessors") is True and SOURCE_SHA not in [row[3] for row in PRIOR], "no spurious raw-byte equality")
    full = packet.get("all_22_guide_cards")
    check(isinstance(full, list) and len(full) == 22, "exact 22 metadata cards")
    for record, _ in predecessors:
        check(full == record.get("all_22_guide_cards"), "all 22 normalized cards match every prior source receipt")
    check(packet.get("selected_tranche_episode_ordinals") == [21, 22], "only final E21/E22 selected")
    for field in ("final_two_source_descriptions_inspected", "final_two_analytical_synopses_proposed"):
        check(type(packet.get(field)) is int and packet[field] == 2, f"only two descriptions read and analyzed: {field}")
    cards = packet.get("final_two_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 2, "exact final two cards")
    check(type(packet.get("final_two_description_total_chars")) is int and packet["final_two_description_total_chars"] == 232, "two publisher descriptions total 232 chars")
    check(len({card.get("video_route_path") for card in cards}) == 2, "distinct route metadata")
    for index, card in enumerate(cards):
        n = 21 + index
        title, expected_sha, chars, anchor, desc_line = EXPECTED_FINAL[index]
        check(card == full[n-1] and card.get("title") == title, f"E{n} exact publisher card")
        for field in ("season", "episode", "display_order", "analytics_ordinal", "description_chars", "html_anchor_line", "html_description_line"):
            check(type(card.get(field)) is int, f"E{n} strict integer {field}")
        check(card["season"] == 4 and card["episode"] == card["display_order"] == card["analytics_ordinal"] == n, f"E{n} ordinal")
        check(card["description_sha256"] == expected_sha and card["description_chars"] == chars and card["html_anchor_line"] == anchor and card["html_description_line"] == desc_line, f"E{n} exact source fingerprint and locators")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{n} source route metadata")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{n} publisher timestamp")
    check(sum(card["description_chars"] for card in cards) == packet["final_two_description_total_chars"], "source description sum")
    case = packet.get("source_internal_title_variant_reobserved")
    expected_case = {
        "source_local_episode_hint":22,
        "display_title":"These Are the Voyages",
        "analytics_title":"These Are the Voyages",
        "analytics_series_title":"These Are The Voyages",
        "status":"CAPITALIZATION_VARIANT_UNRESOLVED",
        "global_reconciliation_effect":"NONE",
    }
    check(case == expected_case, "publisher-local E22 capitalization discrepancy preserved")
    check(cards[1]["title"] == case["display_title"] and cards[1]["analytics_title"] == case["analytics_title"] and cards[1]["analytics_series_title"] == case["analytics_series_title"], "same source-local E22 competing tokens")
    check(packet.get("source_local_competing_title_tokens") == {
        "source_local_episode_hint":22,
        "card_html_h2":{"value":"These Are the Voyages","locator":"HTML h2 within card whose anchor begins line 2070"},
        "analytics_leaf_title":{"value":"These Are the Voyages","locator":"HTML aa-link attribute, leaf segment, anchor line 2070"},
        "analytics_series_prefix_title":{"value":"These Are The Voyages","locator":"HTML aa-link attribute, series-prefixed segment, anchor line 2070"},
        "differing_tokens":"the vs The",
        "casefold_identity_consistent":True, "exact_spelling_reconciliation":"UNRESOLVED", "chosen_canonical_title":None,
    }, "source-local conflicting tokens cannot silently be reconciled")
    entities, evidence, assertions = (packet.get(k, []) for k in ("local_entities", "source_relative_evidence", "typed_assertions"))
    check(len(entities) == len(evidence) == len(assertions) == 2, "two local entity/evidence/assertion chains")
    for index, (entity, ev, claim) in enumerate(zip(entities, evidence, assertions)):
        n=21+index
        stem=f"ent-s4-e{n:02d}"
        eid=f"{stem}-publisher-card"
        vid=f"{stem}-guide-description"
        check(entity.get("id") == eid and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == n, f"E{n} source-local entity")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"E{n} Work unbound")
        check(ev.get("id") == vid and ev.get("source_id") == source["local_source_id"] and ev.get("local_entity_id") == eid, f"E{n} evidence links")
        check(ev.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(ev.get("card_ordinal")) is int and ev["card_ordinal"] == n, f"E{n} evidence class")
        check(ev.get("publisher_description_sha256") == cards[index]["description_sha256"] and str(cards[index]["html_description_line"]) in ev.get("locator", ""), f"E{n} evidence source fingerprint/locator")
        paraphrase=ev.get("original_paraphrase", "")
        check(isinstance(paraphrase,str) and 65<=len(paraphrase)<=200 and "\n" not in paraphrase, f"E{n} original short paraphrase")
        check(claim.get("id") == f"{stem}-publisher-describes" and claim.get("predicate") == "PUBLISHER_DESCRIBES" and claim.get("evidence_id") == vid, f"E{n} publisher attribution")
        check(claim.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED" and claim.get("claimed_narrative_frame") == "UNSPECIFIED" and claim.get("frame_claim_status") == "PUBLISHER_DESCRIPTION_ONLY", f"E{n} publisher-claim evidence boundary")
        for row in (entity,ev,claim):
            check(row["id"] not in ids, f"E{n} globally unique local ID")
            ids.add(row["id"])
    check(ordinals + [row["source_local_episode_hint"] for row in entities] == list(range(1,23)), "five nonoverlapping batches exactly cover source-local 1–22 only")
    check(packet.get("held_season_description_partition_summary") == {
        "prior_analyses":20, "this_tranche_analyses":2,
        "total_nonoverlapping_source_relative_description_proposals":22,
        "source_local_guide_cards_observed":22,
        "remaining_unprocessed_publisher_descriptions":0,
        "accepted_work_coverage_or_close_read_claims":0,
        "status":"HELD_PUBLISHER_GUIDE_DESCRIPTIONS_COMPLETE_NOT_EPISODE_CONTENT_CLOSE_READ",
    }, "final publisher-guide proposals do not become episode close-read or accepted coverage")
    check(len(packet.get("holds", [])) >= 7, "method/rights/deployment holds explicit")


def main() -> int:
    try:
        prior=[(read_json(SIBLING / folder / "records.json"), hashlib.sha256((SIBLING / folder / "records.json").read_bytes()).hexdigest()) for folder, *_ in PRIOR]
        validate(read_json(HERE / "records.json"), prior)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL ENT S4 E21–E22: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S4: 22/22 HELD publisher-guide descriptions in five source-relative batches; no episode video CLOSE_READ, Work binding, coverage, or public effect")
    return 0


if __name__ == "__main__":
    sys.exit(main())
