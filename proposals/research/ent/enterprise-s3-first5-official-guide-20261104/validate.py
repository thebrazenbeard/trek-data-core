"""Fail-closed held Enterprise S3 first-five publisher guide packet validation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DISCOVERY = ROOT / "proposals/discovery/legacy-paramount-season3-20261102/ent/bundle.json"
DISCOVERY_SHA = "ae106b332e3e2c4d966b544ad6c31d9deb04c7f6843533519d79f93c2ebc9358"
SOURCE_SHA = "227c1cbcbafd29cabb62ff83e73cccd2466604ab0e3c4462920badf774453391"
EXPECTED_FINGERPRINTS = [
      "09f7401e2e1b1c9c9ea481974abdeed46792c04451d52a430f08d28e8663bf32",
      "cfe67589d19c28dd42e2eaf988ca7427e970d8d6331350b1be8261bcbacc3faa",
      "95c0b5b6c23ac338f52cef3c8f6006b3cacbf554683d2dbe0a1f161435b9fedd",
      "fe5c2f6e438c215a0934a1141450089cac2238f33e3081ad7ce3514118362f3f",
      "0b0fd0666adfbe98c16657fb2a94f55f2c7ceec15e255917d0baabf55a4d3c10",
      "9fbfe25466b7f8d670d35c66d480f498884f0ece7b9cbc4050cc8c3fc1c98c53",
      "e797d41bea3abc7f33f89dbfe4702f91168ff002a7c6fd048fa06444e2c1c590",
      "25046c252c40e19250ca307777cee39edffffbb1f8b18f5a9092c4b2ce021915",
      "5065c3891b188cce824b3ba881f682a341d87cb9f973f6bccee5782623f36743",
      "037c1fad4eed589d8633110f841d48adc862349a93ff81a2facf085b264267e3",
      "d4ae4a81b47e18f99f6f11f49770ae36cdd9eeceb31fdef1bdadf2582f24eaec",
      "7102998269532aee2e019d5118093a6933c5b0e58633c5307ae9b99c126e2c59",
      "2e5062a9c9591dbd0ffd3fbea9f2fc70e9f37df8bc2447da3fe9d2ace0894340",
      "1f8253ca8affbe9098730f499b4b34188dc28520acfd769b1a012ab7df977ef7",
      "cb5fdbad86dbb29369ec7340bfafebf12168f8a0c2c10230722fa105d4d40029",
      "2b060a05e7e317e320e793f83696a8d529f8f4742dfe93572057369fd6537c7d",
      "9f307bd33144f6f21dc221607b3a5993de5dec3dd3cec9da2a249cf2e5f98125",
      "465eb244c950bcb79cd685ee3f25449ab5d692fc79c3a119c851fff1528fded5",
      "0647b740b5dff34294f1cc59508f06966b2c4d5e2b450a62f93c6a137709385b",
      "78d4de662bfffd6c2f070c3b3c8eb5771f8b52e8dc3051b84d30cd13d05a08c2",
      "5570b50cb63f0043941cbf9a2469b9414152432f4628384deeb99989055b483a",
      "51e321ada9f03d4b72e64fa5f98e63b4d99b8d8092765c5eef3d4354fbb30956",
      "ab20b5e99082d383d162e6fc721d9d945f0e7f871d89fd5f2b02d45b4485812d",
      "f29bf2d5a9eec9512619456ed68a93dcc0df61527ad11f5eba76bee9025c4343"
    ]
EXPECTED_ROUTES = [
      "/shows/video/1478467601/",
      "/shows/video/1478469433/",
      "/shows/video/1478469984/",
      "/shows/video/1478472684/",
      "/shows/video/1478475038/",
      "/shows/video/1478477187/",
      "/shows/video/1478503461/",
      "/shows/video/1478507809/",
      "/shows/video/1479231371/",
      "/shows/video/1479232274/",
      "/shows/video/1479237112/",
      "/shows/video/1479264034/",
      "/shows/video/1479267580/",
      "/shows/video/1479269511/",
      "/shows/video/1479270313/",
      "/shows/video/1479394951/",
      "/shows/video/1479395507/",
      "/shows/video/1479395808/",
      "/shows/video/1479396610/",
      "/shows/video/1479407804/",
      "/shows/video/oJeuPw0_lI36D1DJ_RAQMA0a0qchtYve/",
      "/shows/video/1479408410/",
      "/shows/video/1479412103/",
      "/shows/video/1479413796/"
    ]
PROTECTED = ("accepted_source_binding_effect", "accepted_work_effect",
             "coverage_effect", "denominator_effect", "reconciliation_effect",
             "explorer_synopsis_release_effect")


def read_json(path: Path) -> dict:
    def unique_pairs(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f"duplicate JSON key: {k}")
            out[k] = v
        return out
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(data: dict, discovery: dict, discovery_sha: str) -> None:
    check(discovery_sha == DISCOVERY_SHA, "upstream discovery exact-file drift")
    check(discovery.get("batch_id") == "PARAMOUNT-S3-20261102-ENT", "upstream ENT S3 identity")
    check(discovery.get("mission_id") == "ent" and discovery.get("listed_slot_count") == 24, "upstream 24 candidates")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        check(discovery.get(effect) == "NONE", f"upstream protection {effect}")
    check(data.get("schema_version") == "1.0.0", "schema")
    check(data.get("batch_id") == "ENT.PPLUS.S3.FIRST5.GUIDE.20261104", "batch identity")
    check(data.get("role") == "ENT" and data.get("status") == "HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE", "held partition")
    for effect in PROTECTED:
        check(data.get(effect) == "NONE", f"protected effect {effect}")
    for flag in ("episode_content_watched", "transcripts_read", "image_bytes_fetched"):
        check(data.get(flag) is False, f"unearned evidence flag {flag}")
    upstream = data.get("upstream_discovery", {})
    check(upstream.get("path") == "proposals/discovery/legacy-paramount-season3-20261102/ent/bundle.json", "discovery path")
    check(upstream.get("sha256") == discovery_sha, "discovery digest linkage")
    check(upstream.get("identity_join_method") == "SOURCE_LOCAL_SEASON_EPISODE_TITLE_NOT_CANONICAL_WORK", "no canonical Work join")
    source = data.get("source", {})
    check(source.get("local_source_id") == "ent-s3-paramountplus-guide-html-first5-20261104", "local source ID")
    check(source.get("url") == discovery.get("observation", {}).get("primary_locator") == "https://www.paramountplus.com/shows/enterprise/episodes/3/", "official publisher guide")
    check(source.get("source_kind") == "FIRST_PARTY_PUBLISHER_SEASON_EPISODE_GUIDE_HTML", "publisher guide type")
    check(source.get("publisher") == "Paramount+" and source.get("independence_group") == "publisher:paramountplus.com", "same-source publisher lineage")
    check(type(source.get("response_http_status")) is int and source.get("response_http_status") == 200, "HTTP 200")
    check(source.get("response_date_header") == "Wed, 04 Nov 2026 21:17:58 GMT", "HTTP Date pinned")
    check(type(source.get("raw_response_bytes")) is int and source.get("raw_response_bytes") == 308190, "full HTML response length")
    check(source.get("raw_response_sha256") == SOURCE_SHA, "full HTML response SHA256")
    check(source.get("raw_html_committed") is False and source.get("snapshot_mutable") is True, "no copyrighted source bytes")
    check(source.get("reproducible_extractor") == "source_probe.py", "extractor identity")
    check(source.get("observed_at_utc") == "2026-11-04T21:17:58.093971+00:00", "UTC source retrieval timestamp")
    cards = data.get("all_24_guide_cards", [])
    candidates = discovery.get("episode_slots", [])
    check(type(data.get("observed_full_guide_card_count")) is int and data.get("observed_full_guide_card_count") == 24, "full 24-card page traversed")
    check(isinstance(cards, list) and len(cards) == 24 and len(candidates) == 24, "24 source-relative candidate slots")
    check(data.get("selected_tranche_episode_ordinals") == [1, 2, 3, 4, 5], "bounded first-five subset")
    for name in ("first_five_source_descriptions_inspected", "first_five_analytical_synopses_proposed"):
        check(type(data.get(name)) is int and data.get(name) == 5, f"five actually processed {name}")
    check(type(data.get("first_five_description_total_chars")) is int and
          data["first_five_description_total_chars"] == sum(c.get("description_chars", -1) for c in cards[:5]) == 951, "951 read publisher characters")
    check(len({c.get("video_route_path") for c in cards}) == 24, "unique publisher route per card")
    for i, (card, candidate) in enumerate(zip(cards, candidates)):
        n = i + 1
        for field in ("display_order", "season", "episode", "analytics_ordinal", "description_chars", "html_anchor_line", "html_description_line"):
            check(type(card.get(field)) is int, f"integer {field} card {n}")
        check(card["display_order"] == card["episode"] == card["analytics_ordinal"] == candidate.get("episode_number") == n, f"publisher ordinal {n}")
        check(type(candidate.get("episode_number")) is int and type(candidate.get("season")) is int and candidate.get("season") == card["season"] == 3, f"source season {n}")
        check(card.get("title") == candidate.get("title"), f"source-relative title/candidate crosscheck {n}")
        check(candidate.get("canonical_work_id") is None and candidate.get("source_binding_id") is None, f"upstream unbound {n}")
        check(card.get("video_route_path") == EXPECTED_ROUTES[i], f"pinned route {n}")
        check(card.get("description_sha256") == EXPECTED_FINGERPRINTS[i], f"pinned description hash {n}")
        check(card["html_anchor_line"] == 1482 + 28 * i and card["html_description_line"] == 1500 + 28 * i, f"HTML source-relative locator {n}")
        check(card.get("description_chars") >= 50, f"nonempty description {n}")
        check(bool(re.fullmatch(r"/shows/video/[A-Za-z0-9_-]+/", card.get("video_route_path", ""))), f"route syntax {n}")
        check(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", card.get("publisher_datetime", ""))), f"publisher datetime literal {n}")
    entities = data.get("local_entities", [])
    evidences = data.get("source_relative_evidence", [])
    assertions = data.get("typed_assertions", [])
    check(len(entities) == len(evidences) == len(assertions) == 5, "exactly five analytical records")
    ids = [r.get("id") for bucket in (entities, evidences, assertions) for r in bucket]
    check(len(set(ids)) == 15, "unique local entity/evidence/assertion IDs")
    for i, (entity, evidence, assertion) in enumerate(zip(entities, evidences, assertions)):
        n = i + 1
        local_id = f"ent-s3-e{n:02d}-publisher-card"
        evidence_id = f"ent-s3-e{n:02d}-guide-description"
        check(entity.get("id") == local_id and type(entity.get("source_local_episode_hint")) is int and entity["source_local_episode_hint"] == n, f"source-local entity {n}")
        check(entity.get("source_kind") == "PUBLISHER_EPISODE_CARD" and entity.get("canonical_work_id") is None, f"no canonical Work {n}")
        check(evidence.get("id") == evidence_id and evidence.get("source_id") == source["local_source_id"] and evidence.get("local_entity_id") == local_id, f"source-local evidence ID {n}")
        check(evidence.get("kind") == "PUBLISHER_GUIDE_DESCRIPTION" and type(evidence.get("card_ordinal")) is int and evidence["card_ordinal"] == n, f"source class {n}")
        check(evidence.get("publisher_description_sha256") == cards[i]["description_sha256"] and str(cards[i]["html_description_line"]) in evidence.get("locator", ""), f"source description locator/fingerprint {n}")
        paraphrase = evidence.get("original_paraphrase", "")
        check(isinstance(paraphrase, str) and 65 <= len(paraphrase) <= 200 and "\n" not in paraphrase, f"original bounded paraphrase {n}")
        check(assertion.get("id") == f"ent-s3-e{n:02d}-publisher-describes" and assertion.get("evidence_id") == evidence_id, f"assertion/evidence join {n}")
        check(assertion.get("predicate") == "PUBLISHER_DESCRIBES" and assertion.get("status") == "SOURCE_RELATIVE_NOT_EPISODE_CONTENT_VERIFIED", f"editorial claim only {n}")
    check(len(data.get("holds", [])) >= 5, "mandatory holds")


def main() -> int:
    try:
        discovery_sha = hashlib.sha256(DISCOVERY.read_bytes()).hexdigest()
        validate(read_json(HERE / "records.json"), read_json(DISCOVERY), discovery_sha)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        print(f"FAIL ENT S3 first five: {exc}", file=sys.stderr)
        return 1
    print("PASS ENT S3 E01-E05: 24-card full publisher guide read, 5 publisher synopsis analyses HELD, 0 Work/CLOSE_READ/coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
