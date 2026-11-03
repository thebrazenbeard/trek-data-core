#!/usr/bin/env python3
"""Fail-closed validation for held, source-local Picard S1 guide cards 6–10."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = "https://www.paramountplus.com/shows/star-trek-picard/episodes/1/"
UPSTREAM = "proposals/discovery/modern-paramount-season1-20261102/pic-observed-slots.csv"
UPSTREAM_SHA = "a3c798fce4ab4121f8487319d921a56f42a3793b4668273474e69a74842f383c"
SAMPLE_RECEIPTS = [
    {"bytes": 273178, "sha256": "201bdde6ffbe0dcceaf3a65d6f677d9e5f6d657bfd676bcadb8a046a029ea664"},
    {"bytes": 273178, "sha256": "20a548779772d17dd70723d8f61c3f3d3b2a8c199b9f2b7f8af686bc1992462d"},
]
BASE_IMAGE = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
PINS = [
    (
        6, "The Impossible Box", "ILu3u0v0pecOu3csQp_2vpwvTomMwj17",
        "2020/02/11/1696554563951/CBS_STAR_TREK_PICARD_106_NO_LOGO_IMAGE_172910_1920x1080.jpg",
        ["Picard", "Soji", "Borg cube", "Narek"],
        "Picard's crew traces Soji to a Borg cube in Romulan space as Narek seeks information from her.",
    ),
    (
        7, "Nepenthe", "9D5se7TaQpNkFuHlSJL4Gl_VVoZBPZnz",
        "2020/02/11/1696554563995/CBS_STAR_TREK_PICARD_107_NO_LOGO_IMAGE_176144_1920x1080.jpg",
        ["Picard", "Soji", "Nepenthe", "La Sirena", "Hugh", "Elnor", "Narissa"],
        "Picard and Soji reach Nepenthe, home to trusted friends, while Hugh and Elnor face danger aboard the Borg cube.",
    ),
    (
        8, "Broken Pieces", "YQqXfmwR39lrrJGR87_PRroedTeh1frX",
        "2020/02/11/1696554563998/CBS_STAR_TREK_PICARD_108_NO_LOGO_IMAGE_178149_1920x1080.jpg",
        ["Mars attack", "Picard", "La Sirena", "Narissa", "Elnor", "Borg cube"],
        "Revelations about the Mars attack unsettle the La Sirena crew, while Elnor faces danger on the Borg cube.",
    ),
    (
        9, "Et in Arcadia Ego, Part 1", "vXDy0sihl2s6_4dJ4_ECW8vS8Vy1TpJk",
        "2020/03/13/1710643779875/CBS_STAR_TREK_PICARD_109_NO_LOGO_IMAGE_179650_1920x1080.jpg",
        ["Picard", "Soji", "Coppelius", "Romulan warbirds"],
        "The crew reaches Soji's homeworld, Coppelius, with Romulan pursuers approaching and unexpected discoveries ahead.",
    ),
    (
        10, "Et in Arcadia Ego, Part 2", "OByehBzRg7bOQxNbekLFzyoBLQ0Fwbv5",
        "2020/03/17/1712091203818/CBS_STAR_TREK_PICARD_110_NO_LOGO_IMAGE_180777_1920x1080.jpg",
        ["Coppelius", "Picard", "Romulans", "synths"],
        "A confrontation on Coppelius sets Picard's team against Romulan forces and synthetic residents protecting their future.",
    ),
]

PACKET_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_source_binding_effect",
    "accepted_work_effect", "coverage_effect", "denominator_effect", "source",
    "upstream_discovery", "source_local_episode_cards",
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


def require(ok, description):
    if not ok:
        raise ValueError("PIC P002: " + description)


def validate(packet=None, repo=REPO):
    if packet is None:
        packet = load(HERE / "records.json")
    require(type(packet) is dict and set(packet) == PACKET_FIELDS, "packet schema")
    require(packet["schema_version"] == "1.0.0" and
            packet["batch_id"] == "PIC.PPLUS.S1.LAST5.CARDS.20261103", "batch identity")
    require(packet["role"] == "PIC" and packet["proposal_only"] is True, "worker proposal boundary")
    for field in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(packet[field] == "NONE" and type(packet[field]) is str, "forbidden effect: " + field)
    src = packet["source"]
    require(type(src) is dict and set(src) == SOURCE_FIELDS, "source schema")
    require(src["local_id"] == "pic-pplus-s1-last5-episode-guide-20261103", "source local identity")
    require(src["provider"] == "Paramount+" and
            src["independence_group"] == "publisher:paramountplus.com", "publisher family")
    require(src["url"] == SOURCE and src["retrieval_date_utc"] == "2026-11-03", "source locator/date")
    require(src["retrieval_method"] == "DIRECT_HTTP_GET_AND_RENDERED_WEB_VIEW" and
            type(src["http_status"]) is int and src["http_status"] == 200, "observed source access")
    require(src["raw_sample_receipts"] == SAMPLE_RECEIPTS and
            all(type(r["bytes"]) is int for r in src["raw_sample_receipts"]), "raw HTML receipt assertions")
    require(src["raw_html_retained_in_public_repo"] is False and
            src["publisher_html_stability"] == "DIFFERING_RESPONSE_DIGESTS_SAME_CARD_OBSERVATIONS", "mutable HTML caveat")
    require(src["full_primary_audiovisual_content_read"] is False and
            src["scope"] == "SEASON_GUIDE_CARD_METADATA_NOT_EPISODE_CONTENT", "no full episode evidence")
    require(packet["upstream_discovery"] == {
        "path": UPSTREAM, "sha256": UPSTREAM_SHA, "effect": "SOURCE_LOCAL_CROSSCHECK_ONLY",
    }, "same-family upstream provenance")
    path = repo / UPSTREAM
    require(path.is_file() and not path.is_symlink(), "missing / symlinked discovery input")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == UPSTREAM_SHA, "upstream byte drift")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    require(len(rows) == 10, "discovery season length")
    cards = packet["source_local_episode_cards"]
    require(type(cards) is list and len(cards) == 5, "exact five guide cards")
    ids = set()
    images = set()
    videos = set()
    for offset, card in enumerate(cards):
        ep, title, vid, thumb, mentions, synopsis = PINS[offset]
        require(type(card) is dict and set(card) == CARD_FIELDS, "closed card schema")
        require(card["local_id"] == f"pic-s1-e{ep:02d}-pplus-guide" and
                type(card["season"]) is int and card["season"] == 1 and
                type(card["episode_number"]) is int and card["episode_number"] == ep,
                "source-local episode scope")
        require(card["title"] == title and
                card["guide_line_window"] == [128 + offset * 5, 132 + offset * 5], "title and read lines")
        require(card["video_url"] == f"https://www.paramountplus.com/shows/video/{vid}/" and
                card["thumbnail_url"] == BASE_IMAGE + thumb, "exact original publisher HTML link pair")
        require(card["thumbnail_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "no public image rights")
        require(type(card["literal_name_mentions"]) is list and
                card["literal_name_mentions"] == mentions and
                all(type(x) is str for x in card["literal_name_mentions"]), "publisher text mentions only")
        require(card["synopsis_paraphrase_candidate"] == synopsis and
                card["synopsis_state"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE", "held paraphrase")
        require(card["evidence_scope"] == "PUBLISHER_GUIDE_DESCRIPTION_AND_HTML_CARD", "description not episode")
        require(rows[ep - 1] == {"season": "1", "episode_number": str(ep), "title": title},
                "same-publisher historical card crosswalk")
        ids.add(card["local_id"])
        images.add(card["thumbnail_url"])
        videos.add(card["video_url"])
    require(len(ids) == len(images) == len(videos) == 5, "duplicate source-local identity/asset locator")
    return len(cards)


if __name__ == "__main__":
    print(f"PIC_P002_OK: {validate()} held S1 E6–E10 publisher guide cards; no public media, Work or coverage")
