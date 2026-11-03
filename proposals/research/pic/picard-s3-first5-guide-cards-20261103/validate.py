#!/usr/bin/env python3
"""Strict source-local Paramount+ Picard S3 E1–5 evidence; no admissions."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = "https://www.paramountplus.com/shows/star-trek-picard/episodes/3/"
UPSTREAM = "proposals/discovery/modern-paramount-season3-20261102/pic-observed-slots.csv"
UPSTREAM_SHA = "033f18a51a5ea16c452aab27bbcdd3373ed321f97bf38bd994d813b5edbb6fe0"
IMAGE_BASE = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
RAW_RECEIPTS = [
    {"bytes": 271825, "sha256": "02dbab5ad9518af0589ff5be618fee1a13e983270cdf948807dd32b4667c683f"},
    {"bytes": 271825, "sha256": "9911e2cfb52ba80ee75e0e63063b4c04c7797b4df3f82b399446a164398539a4"},
]
# Source-local code-owned digests over each FULL published card, including status,
# mentions, synopsis, original publisher-description fingerprint, and URL pair.
CARD_SHA256 = (
    "ea4ecca8e7a610fd1a321576b8844867be058d0753c7d709c235b324b25f465f",
    "c2d0b854951d47bb32dd6b39e2fdaa2b6455350634c0c1a2e6ad54543988ee6d",
    "7715ff96b74155413b6cc13aff405f54dcade2a4f0a8196e2bf434e2253aa5df",
    "9aeb0190690d133ead1eaf2b69fd93f7f3fd116af1fc458ee62a2be32951e912",
    "da6c86a26bea14cad956225acdf766f4b44f5c1c1913ee577e2a009e84fba076",
)
PINS = (
    ("The Next Generation", "dQo2jCxwxKSXtDyIPKb44W6hCEiqd_Ec", "2023/01/11/2160568387838/Picard_301_TP_0917_02037_RT_1942956_1920x1080.jpg", 244, "4c81f2fabf65dd16a687854effef44fdd51c1a82b94090f6e92b1afa6ef3a9b0", ["Dr. Beverly Crusher", "Admiral Jean-Luc Picard", "Starfleet"]),
    ("Disengage", "_hn3xX7z2ADLb5xnjtHAP_JQw9geuB_l", "2023/01/11/2160574531772/Picard_302_TP_0927_01612_RT_1948761_1920x1080.jpg", 302, "19d24fa5ae3654b12bcb7fd84d7de1766b45f38b38a20974b260a3f80d4a2757", ["Seven of Nine", "U.S.S. Titan", "Picard", "Raffi"]),
    ("Seventeen Seconds", "NjhnDbV7slibv9pl7MZ9LBC5fAyrvJTN", "2023/01/11/2160574531773/Star_Trek_Picard_303_No_Logo_1969562_1920x1080.jpg", 280, "e12c551a469f3bc5409fd0ae1ad0e0995c24c8b6c51191dec3dd3ffa036eca78", ["Picard", "Titan", "Vadic", "Raffi", "Worf", "Starfleet"]),
    ("No Win Scenario", "__96sEpIXP3iBbpyS_7nhEPaV_CVYiBv", "2023/01/11/2160576067777/Star_Trek_Picard_304_No_Logo-R1_1977607_1920x1080.jpg", 221, "ff828d78204aeb13fe5e8a6932ee88a305ef4b9866462b66f02074ffb0643709", ["Picard", "Riker", "Titan"]),
    ("Imposters", "d_z5_o1wYC8jHl3NOgHSqe_QY_eMYkY_", "2023/01/11/2160576579605/star_trek_picard_305_HD_CBS_Interactive_ProRes_Rec709_422_2398_20230301_15756_2385631_1920x1080.jpg", 203, "3f9cc910315ebdf1c23f430f1c9bd0491534f6e536380d5dd7a2c02cd4775f15", ["Starfleet", "Picard"]),
)
PACKET_FIELDS = {"schema_version", "batch_id", "role", "proposal_only", "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "explorer_effect", "source", "upstream_discovery", "source_local_episode_cards"}
SOURCE_FIELDS = {"local_id", "provider", "independence_group", "url", "retrieval_date_utc", "retrieval_method", "http_status", "raw_sample_receipts", "raw_html_retained_in_public_repo", "publisher_html_stability", "full_primary_audiovisual_content_read", "scope", "description_fingerprint_rule"}
CARD_FIELDS = {"local_id", "season", "episode_number", "title", "guide_line_window", "description_length_utf8_codepoints", "description_sha256", "video_url", "thumbnail_url", "thumbnail_status", "literal_name_mentions", "synopsis_paraphrase_candidate", "synopsis_state", "evidence_scope"}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def require(condition, reason):
    if not condition:
        raise ValueError("PIC_S3_P001: " + reason)


def card_digest(card):
    return hashlib.sha256(json.dumps(card, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def validate(packet=None, repo=REPO):
    if packet is None:
        packet = load(HERE / "records.json")
    require(type(packet) is dict and set(packet) == PACKET_FIELDS, "closed packet fields")
    require(packet["schema_version"] == "1.0.0" and packet["batch_id"] == "PIC.PPLUS.S3.FIRST5.CARDS.20261103", "exact batch identity")
    require(packet["role"] == "PIC" and packet["proposal_only"] is True, "proposal-only role")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "explorer_effect"):
        require(type(packet[effect]) is str and packet[effect] == "NONE", "forbidden admission/coverage/public effect: " + effect)
    src = packet["source"]
    require(type(src) is dict and set(src) == SOURCE_FIELDS, "closed source fields")
    require(src["local_id"] == "pic-pplus-s3-first5-episode-guide-20261103", "source-local identity")
    require(src["provider"] == "Paramount+" and src["independence_group"] == "publisher:paramountplus.com", "publisher lineage")
    require(src["url"] == SOURCE and src["retrieval_date_utc"] == "2026-11-03", "source URL and retrieval date")
    require(src["retrieval_method"] == "DIRECT_HTTP_GET_AND_RENDERED_WEB_VIEW" and type(src["http_status"]) is int and src["http_status"] == 200, "source HTTP observation")
    require(src["raw_sample_receipts"] == RAW_RECEIPTS and type(src["raw_sample_receipts"]) is list, "exact mutable raw HTML receipts")
    require(src["raw_html_retained_in_public_repo"] is False and src["publisher_html_stability"] == "DIFFERING_RESPONSE_DIGESTS_SAME_CARD_OBSERVATIONS", "mutable raw-HTML caveat")
    require(src["full_primary_audiovisual_content_read"] is False and src["scope"] == "SEASON_GUIDE_CARD_METADATA_NOT_EPISODE_CONTENT", "no episode close read")
    require(src["description_fingerprint_rule"] == "SHA256_UTF8_HTML_UNESCAPED_STRIPPED_EP_COPY_TEXT", "fingerprint normalization rule")
    require(packet["upstream_discovery"] == {"path": UPSTREAM, "sha256": UPSTREAM_SHA, "effect": "SOURCE_LOCAL_CROSSCHECK_ONLY"}, "discovery lineage")
    discovery = repo / UPSTREAM
    require(discovery.is_file() and not discovery.is_symlink(), "missing/symlinked discovery input")
    require(hashlib.sha256(discovery.read_bytes()).hexdigest() == UPSTREAM_SHA, "source-local discovery bytes drift")
    slots = list(csv.DictReader(discovery.read_text(encoding="utf-8").splitlines()))
    require(len(slots) == 10, "upstream S3 ten guide slots (not coverage)")
    cards = packet["source_local_episode_cards"]
    require(type(cards) is list and len(cards) == 5, "five guide cards only")
    ids, videos, thumbs, descs = set(), set(), set(), set()
    for index, card in enumerate(cards):
        title, video_id, image_suffix, length, desc_hash, names = PINS[index]
        ep = index + 1
        require(type(card) is dict and set(card) == CARD_FIELDS, "closed card fields")
        require(card_digest(card) == CARD_SHA256[index], "code-owned full-row digest including every semantic field")
        require(card["local_id"] == f"pic-s3-e{ep:02d}-pplus-guide" and type(card["season"]) is int and card["season"] == 3 and type(card["episode_number"]) is int and card["episode_number"] == ep, "season/slot/ID")
        require(card["title"] == title and card["guide_line_window"] == [104 + index*5, 108 + index*5], "publisher guide title and text locator")
        require(type(card["description_length_utf8_codepoints"]) is int and card["description_length_utf8_codepoints"] == length and card["description_sha256"] == desc_hash, "first-party description fingerprint")
        require(card["video_url"] == f"https://www.paramountplus.com/shows/video/{video_id}/" and card["thumbnail_url"] == IMAGE_BASE + image_suffix, "own-card video/CDN image pair")
        require(card["thumbnail_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "no media rights release")
        require(type(card["literal_name_mentions"]) is list and card["literal_name_mentions"] == names and all(type(name) is str for name in names), "literal publisher-utterance mentions")
        require(type(card["synopsis_paraphrase_candidate"]) is str and 40 <= len(card["synopsis_paraphrase_candidate"]) <= 180 and card["synopsis_state"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE", "original held guide paraphrase only")
        require(card["evidence_scope"] == "PUBLISHER_GUIDE_DESCRIPTION_AND_HTML_CARD", "not full episode evidence")
        require(slots[index] == {"season": "3", "episode_number": str(ep), "title": title}, "same-publisher discovery slot crosscheck")
        ids.add(card["local_id"]); videos.add(card["video_url"]); thumbs.add(card["thumbnail_url"]); descs.add(card["description_sha256"])
    require(len(ids) == len(videos) == len(thumbs) == len(descs) == 5, "unique own-card identities, asset links, and descriptions")
    return len(cards)


if __name__ == "__main__":
    print(f"PIC_S3_P001_OK: {validate()} held first-party publisher guide cards, zero Work/coverage/art/synopsis promotion")
