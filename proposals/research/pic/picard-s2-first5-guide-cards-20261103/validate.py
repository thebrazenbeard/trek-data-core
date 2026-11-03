#!/usr/bin/env python3
"""Source-local Picard S2 E1–E5 guide-card validator; no admissions or rights."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = "https://www.paramountplus.com/shows/star-trek-picard/episodes/2/"
UPSTREAM = "proposals/discovery/modern-paramount-season2-first5-20261102/pic-observed-slots.csv"
UPSTREAM_SHA = "1ebab18e8e0ca4dc6a4204ddd6e68e338d8d346df5569a867f797b1dcbbeb78a"
RECEIPTS = [
    {"bytes": 271518, "sha256": "889000c328534710a7dd3b4f670cff0ea0a2bbb49b88ff41d6c1eebcd125a5e7"},
    {"bytes": 271518, "sha256": "d0c28ad7afbd6b58d4e5ad12d9ac733243dc4d23c4be1d068da272a71eaddae3"},
]
IMAGE_BASE = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
PINS = [
    (
        1, "The Star Gazer", "RznkQ28IQNPYFk6_3mkZRpJbtBeKKxuf",
        "2022/02/18/2004660291513/STAR_TREK_PICARD_201_1194183_1920x1080.jpg",
        ["Starfleet", "Jean-Luc Picard", "Cristóbal Rios", "Seven of Nine", "Raffi Musiker", "Dr. Agnes Jurati"],
        "Starfleet calls on Picard after former crewmates discover a dangerous anomaly in space.",
    ),
    (
        2, "Penance", "k8ebkarVRm5YBcIfTi7lr_VIweb0wxpl",
        "2022/03/02/2008775747666/Picard_202_TP_2244_RT_1215557_1920x1080.jpg",
        ["Picard", "alternate timeline", "year 2400", "Q"],
        "In an alternate 2400, Picard searches for his crew amid a trial arranged by Q.",
    ),
    (
        3, "Assimilation", "8s3v_BRcan18peRItu4lV_eT_9Z60tmY",
        "2022/03/02/2008774211729/STAR_TREK_PICARD_203_1225961_1920x1080.jpg",
        ["Picard", "2024 Los Angeles", "Watcher", "Seven", "Raffi", "Rios", "Jurati"],
        "The crew reaches 2024 Los Angeles to find a Watcher who may help explain the changed timeline.",
    ),
    (
        4, "Watcher", "94mLIxbwQKjaztosqgeCYJRnxosmtFUg",
        "2022/03/02/2008774211730/STAR_TREK_PICARD_204_1235670_1920x1080.jpg",
        ["Picard", "Rios", "Jurati", "Borg Queen"],
        "Picard seeks an old friend's help as Rios faces legal trouble and Jurati bargains with the Borg Queen.",
    ),
    (
        5, "Fly Me to the Moon", "2NV4H17unfaAo7GKv1Neb1zvTLNynHcF",
        "2022/03/02/2008775747695/STAR_TREK_PICARD_205_1259340_1920x1080.jpg",
        ["Picard", "Q", "Dr. Adam Soong", "Seven", "Raffi", "Rios", "Jurati", "Borg Queen"],
        "Picard investigates a key to the altered timeline while Seven and Raffi seek Rios and Jurati faces her bargain.",
    ),
]
PACKET_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_source_binding_effect",
    "accepted_work_effect", "coverage_effect", "denominator_effect", "source", "upstream_discovery",
    "source_local_episode_cards",
}
SOURCE_FIELDS = {
    "local_id", "provider", "independence_group", "url", "retrieval_date_utc", "retrieval_method",
    "http_status", "raw_sample_receipts", "raw_html_retained_in_public_repo", "publisher_html_stability",
    "full_primary_audiovisual_content_read", "scope",
}
CARD_FIELDS = {
    "local_id", "season", "episode_number", "title", "guide_line_window", "video_url",
    "thumbnail_url", "thumbnail_status", "literal_name_mentions", "synopsis_paraphrase_candidate",
    "synopsis_state", "evidence_scope",
}


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_unique)


def require(condition, reason):
    if not condition:
        raise ValueError("PIC S2 P001: " + reason)


def validate(packet=None, repo=REPO):
    if packet is None:
        packet = load(HERE / "records.json")
    require(type(packet) is dict and set(packet) == PACKET_FIELDS, "closed packet fields")
    require(packet["schema_version"] == "1.0.0" and
            packet["batch_id"] == "PIC.PPLUS.S2.FIRST5.CARDS.20261103", "batch identity")
    require(packet["role"] == "PIC" and packet["proposal_only"] is True, "worker proposal-only scope")
    for effect in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(packet[effect] == "NONE" and type(packet[effect]) is str, "forbidden effect: " + effect)
    src = packet["source"]
    require(type(src) is dict and set(src) == SOURCE_FIELDS, "closed source fields")
    require(src["local_id"] == "pic-pplus-s2-first5-episode-guide-20261103", "source-local identity")
    require(src["provider"] == "Paramount+" and
            src["independence_group"] == "publisher:paramountplus.com", "same publisher lineage")
    require(src["url"] == SOURCE and src["retrieval_date_utc"] == "2026-11-03", "source URL/date")
    require(src["retrieval_method"] == "DIRECT_HTTP_GET_AND_RENDERED_WEB_VIEW" and
            type(src["http_status"]) is int and src["http_status"] == 200, "actual source access")
    require(src["raw_sample_receipts"] == RECEIPTS and type(src["raw_sample_receipts"]) is list and
            all(type(x["bytes"]) is int for x in src["raw_sample_receipts"]), "exact raw HTML receipts")
    require(src["raw_html_retained_in_public_repo"] is False and
            src["publisher_html_stability"] == "DIFFERING_RESPONSE_DIGESTS_SAME_CARD_OBSERVATIONS", "dynamic HTML caveat")
    require(src["full_primary_audiovisual_content_read"] is False and
            src["scope"] == "SEASON_GUIDE_CARD_METADATA_NOT_EPISODE_CONTENT", "no full episode claim")
    require(packet["upstream_discovery"] == {
        "path": UPSTREAM, "sha256": UPSTREAM_SHA, "effect": "SOURCE_LOCAL_CROSSCHECK_ONLY",
    }, "source-relative discovery provenance")
    discovery = repo / UPSTREAM
    require(discovery.is_file() and not discovery.is_symlink(), "missing/symlinked discovery input")
    raw = discovery.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == UPSTREAM_SHA, "discovery bytes drift")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    require(len(rows) == 5, "five historical discovery slots")
    cards = packet["source_local_episode_cards"]
    require(type(cards) is list and len(cards) == 5, "five current guide cards")
    ids, images, videos = set(), set(), set()
    for offset, record in enumerate(cards):
        ep, title, video_id, image_suffix, mentions, synopsis = PINS[offset]
        require(type(record) is dict and set(record) == CARD_FIELDS, "closed card fields")
        require(record["local_id"] == f"pic-s2-e{ep:02d}-pplus-guide" and
                type(record["season"]) is int and record["season"] == 2 and
                type(record["episode_number"]) is int and record["episode_number"] == ep,
                "source-local season/episode/ID")
        require(record["title"] == title and
                record["guide_line_window"] == [104 + 5*offset, 108 + 5*offset], "publisher title/slot/line locator")
        require(record["video_url"] == f"https://www.paramountplus.com/shows/video/{video_id}/" and
                record["thumbnail_url"] == IMAGE_BASE + image_suffix, "source HTML card URL pair")
        require(record["thumbnail_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "no public artwork license")
        require(type(record["literal_name_mentions"]) is list and
                record["literal_name_mentions"] == mentions and
                all(type(x) is str for x in record["literal_name_mentions"]), "literal publisher description mentions")
        require(record["synopsis_paraphrase_candidate"] == synopsis and
                record["synopsis_state"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE", "held original synopsis")
        require(record["evidence_scope"] == "PUBLISHER_GUIDE_DESCRIPTION_AND_HTML_CARD", "guide not episode evidence")
        require(rows[offset] == {"season": "2", "episode_number": str(ep), "title": title},
                "same-family historical source-local slot crosscheck")
        ids.add(record["local_id"])
        images.add(record["thumbnail_url"])
        videos.add(record["video_url"])
    require(len(ids) == len(images) == len(videos) == 5, "duplicate card identifier or media link")
    return len(cards)


if __name__ == "__main__":
    print(f"PIC_S2_P001_OK: {validate()} held Paramount+ S2 E1–5 guide cards; no Work/media license/coverage")
