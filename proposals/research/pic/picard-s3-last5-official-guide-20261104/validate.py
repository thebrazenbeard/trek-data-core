"""Fail-closed validation for held Picard S3 publisher-guide cards E06–E10.

The predecessor is a separate, immutable local proposal—not accepted Work state.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIRST_FIVE = ROOT / "proposals/research/pic/picard-s3-first5-official-guide-20261104/records.json"
FIRST_FIVE_SHA = "fdbb21d3b168b6375ef304fd70a4a55dc964213ac8102cf5929d4d689df5a948"
FIRST_FIVE_COMMIT = "da3b01eeca623bde26642d9177dbf7aad4b24b25"
FIRST_SOURCE_SHA = "54f51850043a1073f8ac4f4e68a22b6acf2bd5b70ad416adce695c36d9e659b3"
LATEST_SOURCE_SHA = "c938f6fe567d1782f7c2130acf051ee09867adcf8abf3bc6cae8ef305c8035d4"
EXPECTED_TITLES = ["The Bounty", "Dominion", "Surrender", "Võx", "The Last Generation"]
EXPECTED_DESCRIPTION_HASHES = [
    "947a9d13f43590ed96eeda4079f82642db2c9fd61e036a737673ff2488e54a1d",
    "fee4ac7d2bd80d0a056254310226ac9b78a3b00a92f5b598dc7f1248da3c6f1c",
    "7b302beb35512f2e53b81b1cd54a49f0bbece229ef0bc1c4fbd91cd29b0c9801",
    "42511bacc17ff8c051d2a0d81b2f9ba5a3f24b26332e10095c07928ae1449a80",
    "a2c429168eb01b95e1999e2b8aea942e6f3126bc3825e3672e67dc37c0ff332f",
]
PROTECTED_EFFECTS = (
    "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
)


def read_json(path: Path) -> dict:
    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(packet: dict, first: dict, first_sha: str) -> None:
    check(first_sha == FIRST_FIVE_SHA, "predecessor file-byte SHA drift")
    check(first.get("batch_id") == "PIC.PPLUS.S3.FIRST5.GUIDE.20261104", "predecessor identity")
    check(first.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "predecessor remains held")
    for effect in PROTECTED_EFFECTS:
        check(first.get(effect) == "NONE", f"predecessor effect {effect}")
    first_cards = first.get("guide_cards", [])
    check(len(first_cards) == 10, "predecessor ten-card source inventory")
    first_entities = first.get("local_entities", [])
    check([e.get("source_local_episode_hint") for e in first_entities] == [1, 2, 3, 4, 5], "first five separately scoped")
    check([e.get("canonical_work_id") for e in first_entities] == [None] * 5, "predecessor Work unbound")

    check(packet.get("schema_version") == "1.0.0", "packet schema")
    check(packet.get("batch_id") == "PIC.PPLUS.S3.LAST5.GUIDE.20261104", "last-five batch ID")
    check(packet.get("role") == "PIC", "PIC owner")
    check(packet.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "last-five held")
    for effect in PROTECTED_EFFECTS:
        check(packet.get(effect) == "NONE", f"protected effect {effect}")
    for key in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(packet.get(key) is False, f"unwarranted content evidence {key}")

    prior = packet.get("prior_first_five", {})
    check(prior.get("path") == "proposals/research/pic/picard-s3-first5-official-guide-20261104/records.json", "first-five locator")
    check(prior.get("sha256") == first_sha, "first-five exact digest linkage")
    check(prior.get("commit") == FIRST_FIVE_COMMIT, "first-five exact commit linkage")
    check(prior.get("source_response_sha256") == FIRST_SOURCE_SHA == first["source"]["raw_response_sha256"], "first-five exact receipt")
    check("E01-E05" in prior.get("scope", ""), "explicit separate predecessor scope")
    source = packet.get("source", {})
    check(source.get("url") == first["source"]["url"] == "https://www.paramountplus.com/shows/star-trek-picard/episodes/3/", "same first-party guide URL")
    check(source.get("source_kind") == first["source"]["source_kind"] == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "source kind")
    check(source.get("independence_group") == first["source"]["independence_group"] == "publisher:paramountplus.com", "same non-independent lineage")
    check(source.get("response_http_status") == 200, "HTTP status")
    check(source.get("raw_response_bytes") == 272699, "exact full HTML response length")
    check(source.get("raw_response_sha256") == LATEST_SOURCE_SHA, "exact fresh receipt SHA")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True, "no copyrighted source prose committed")
    check(source.get("reproducible_extractor") == "../picard-s3-first5-official-guide-20261104/source_probe.py", "extractor lineage")
    check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*\+00:00", source.get("observed_at_utc", ""))), "UTC retrieval")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 21:06:01 GMT", "receipt HTTP Date")

    check(packet.get("observed_full_guide_card_count") == 10, "full guide observed")
    check(packet.get("all_ten_metadata_and_description_fingerprints_match_predecessor_snapshot") is True, "ten-card lineage fingerprint match")
    check(packet.get("raw_html_digest_differs_from_predecessor") is True and LATEST_SOURCE_SHA != FIRST_SOURCE_SHA, "mutable full HTML different")
    check(packet.get("selected_tranche_episode_ordinals") == [6, 7, 8, 9, 10], "last-five selected exactly")
    check(packet.get("last_five_descriptions_inspected") == packet.get("last_five_analytical_synopses_proposed") == 5, "five actually processed")
    cards = packet.get("last_five_guide_cards", [])
    check(isinstance(cards, list) and len(cards) == 5, "five source-relative cards")
    check([c.get("title") for c in cards] == EXPECTED_TITLES, "publisher last-five title order")
    check(len({c.get("video_route_path") for c in cards}) == 5, "distinct publisher routes")
    check(sum(c.get("description_chars", -1) for c in cards) == packet.get("last_five_description_total_chars") == 1174, "full description chars read")
    for i, card in enumerate(cards):
        number = i + 6
        check(card == first_cards[number - 1], f"E{number:02d} card differs from predecessor's observed guide fingerprint")
        check(card.get("display_order") == card.get("episode") == card.get("analytics_ordinal") == number, f"E{number:02d} source ordering")
        check(card.get("season") == 3, f"E{number:02d} season")
        check(card.get("description_sha256") == EXPECTED_DESCRIPTION_HASHES[i], f"E{number:02d} pinned publisher description fingerprint")
        check(card.get("html_anchor_line") == 1470 + 28 * (number - 1), f"E{number:02d} anchor locator")
        check(card.get("html_description_line") == 1488 + 28 * (number - 1), f"E{number:02d} description locator")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"E{number:02d} official video route shape")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"E{number:02d} raw source datetime")

    entities = packet.get("local_entities", [])
    evidences = packet.get("source_relative_evidence", [])
    assertions = packet.get("typed_assertions", [])
    check(len(entities) == len(evidences) == len(assertions) == 5, "five source/evidence/assertion mappings")
    first_ids = {r.get("id") for name in ("local_entities", "source_relative_evidence", "typed_assertions") for r in first.get(name, [])}
    last_ids = {r.get("id") for name in ("local_entities", "source_relative_evidence", "typed_assertions") for r in packet.get(name, [])}
    check(len(last_ids) == 15 and not first_ids.intersection(last_ids), "no duplicate/double-counted IDs across tranches")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        number = i + 6
        entity_id = f"pic-s3-e{number:02d}-publisher-card"
        evidence_id = f"pic-s3-e{number:02d}-guide-description"
        check(entity.get("id") == entity_id and entity.get("source_local_episode_hint") == number, f"E{number:02d} local entity")
        check(entity.get("canonical_work_id") is None and entity.get("source_kind") == "PUBLISHER_EPISODE_CARD", f"E{number:02d} no canonical Work")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"], f"E{number:02d} evidence ID/source")
        check(evidence.get("local_entity_id") == entity_id and evidence.get("card_ordinal") == number, f"E{number:02d} evidence/card join")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION", f"E{number:02d} evidence kind")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"], f"E{number:02d} description hash")
        check(str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"E{number:02d} source line")
        text = evidence.get("original_paraphrase", "")
        check(isinstance(text, str) and 65 <= len(text) <= 200 and "\n" not in text, f"E{number:02d} bounded original paraphrase")
        check(assertion.get("id") == f"pic-s3-e{number:02d}-publisher-describes", f"E{number:02d} typed assertion ID")
        check(assertion.get("predicate") == "PUBLISHER_DESCRIBES" and assertion.get("evidence_id") == evidence_id, f"E{number:02d} publisher claim only")
        check(assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"E{number:02d} not episode truth")
    check(isinstance(packet.get("holds"), list) and len(packet["holds"]) >= 5, "unresolved lineage/rights/coverage holds")


def main() -> int:
    try:
        first_sha = hashlib.sha256(FIRST_FIVE.read_bytes()).hexdigest()
        validate(read_json(HERE / "records.json"), read_json(FIRST_FIVE), first_sha)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"FAIL PIC S3 E06–E10: {exc}", file=sys.stderr)
        return 1
    print("PASS PIC S3 E06–E10: five publisher-description paraphrases held; ten non-overlapping cards; zero Work/CLOSE_READ/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
