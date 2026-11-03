#!/usr/bin/env python3
"""Fail-closed Picard S2 E6–10 Paramount guide-only research validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = "https://www.paramountplus.com/shows/star-trek-picard/episodes/2/"
DIRECTORY = "explorer/discovery-catalog.json"
DIRECTORY_SHA = "2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc"
RECEIPTS = [
    {"bytes": 271518, "sha256": "b609f7a17bb94e2a502cb875d7f90b25aea0978961070103751aa58fc84bae5e"},
    {"bytes": 271518, "sha256": "741f6748b12dfd6d521783c1915704373a0874897b58936cae7084d66fdf2669"},
]
IMAGE_BASE = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
PINS = [
    (
        6, "Two of One", "tIuwjUibicfGCetcbbyNa8DweJrW0GTJ",
        "2022/03/02/2008775747696/STAR_TREK_PICARD_206_1267460_1920x1080.jpg",
        ["Tallinn", "Picard", "Renee Picard", "Kore"],
        "Picard's group enters a gala to protect Renee Picard, while Kore discovers something unexpected about her father.",
    ),
    (
        7, "Monsters", "Bt4tZXm3JepcttPX_bu1jerD83LANMzb",
        "2022/03/02/2008776771870/STAR_TREK_PICARD_207_1279310_1920x1080.jpg",
        ["Tallinn", "Picard", "Seven", "Raffi", "Jurati", "Rios", "Teresa"],
        "Tallinn attempts to wake Picard through his subconscious as Seven and Raffi search for Jurati.",
    ),
    (
        8, "Mercy", "Tx8XWTR5leamdSkC2CzBsdSTHu0In8Gk",
        "2022/03/02/2008776771872/STAR_TREK_PICARD_208_1288407_1920x1080.jpg",
        ["Europa Mission", "Picard", "Guinan", "FBI", "Seven", "Raffi", "Jurati"],
        "Picard and Guinan seek freedom from FBI custody as Seven and Raffi confront Jurati before the Europa launch.",
    ),
    (
        9, "Hide and Seek", "vRsQxCbNYgvPxw_pNu34cPQx_w91p1RA",
        "2022/03/02/2008777795618/STAR_TREK_PICARD_209_1298197_1920x1080.jpg",
        ["Picard", "Seven", "Raffi", "Jurati"],
        "Picard and his crew confront an old adversary in new form as Seven and Raffi face Jurati.",
    ),
    (
        10, "Farewell", "rwUrttf9CvXXYzI2YbHCO0CdPUfOiDE6",
        "2022/03/02/2008777795619/STAR_TREK_PICARD_210_1310974_1920x1080.jpg",
        ["Picard", "Europa Launch"],
        "Picard's crew races to save the future with the Europa launch only hours away.",
    ),
]
PACKET_FIELDS = {
    "schema_version", "batch_id", "role", "proposal_only", "accepted_source_binding_effect",
    "accepted_work_effect", "coverage_effect", "denominator_effect", "source", "prior_lead_index",
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


def require(ok, reason):
    if not ok:
        raise ValueError("PIC S2 P002 invalid: " + reason)


def validate(packet=None, repo=REPO):
    if packet is None:
        packet = load(HERE / "records.json")
    require(type(packet) is dict and set(packet) == PACKET_FIELDS, "closed packet fields")
    require(packet["schema_version"] == "1.0.0" and
            packet["batch_id"] == "PIC.PPLUS.S2.LAST5.CARDS.20261103", "batch identity")
    require(packet["role"] == "PIC" and packet["proposal_only"] is True, "role/proposal boundary")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(type(packet[key]) is str and packet[key] == "NONE", "forbidden effect: " + key)
    source = packet["source"]
    require(type(source) is dict and set(source) == SOURCE_FIELDS, "closed source fields")
    require(source["local_id"] == "pic-pplus-s2-last5-episode-guide-20261103", "source-relative id")
    require(source["provider"] == "Paramount+" and
            source["independence_group"] == "publisher:paramountplus.com", "publisher identity/lineage")
    require(source["url"] == SOURCE and source["retrieval_date_utc"] == "2026-11-03", "publisher locator/date")
    require(source["retrieval_method"] == "DIRECT_HTTP_GET_AND_RENDERED_WEB_VIEW" and
            type(source["http_status"]) is int and source["http_status"] == 200, "primary access observed")
    require(source["raw_sample_receipts"] == RECEIPTS and
            type(source["raw_sample_receipts"]) is list and
            all(type(x["bytes"]) is int for x in source["raw_sample_receipts"]), "dynamic page receipts")
    require(source["raw_html_retained_in_public_repo"] is False and
            source["publisher_html_stability"] == "DIFFERING_RESPONSE_DIGESTS_SAME_CARD_OBSERVATIONS", "no immutable HTML assertion")
    require(source["full_primary_audiovisual_content_read"] is False and
            source["scope"] == "SEASON_GUIDE_CARD_METADATA_NOT_EPISODE_CONTENT", "guide-only evidence")
    require(packet["prior_lead_index"] == {
        "path": DIRECTORY, "sha256": DIRECTORY_SHA, "source_group": "wikidata:wdqs",
        "row_ids": [f"lead:{n:04d}" for n in range(133, 138)],
        "scope": "TITLE_CANDIDATES_ONLY_NOT_INDEPENDENT_EPISODE_SLOT_OR_PLOT_CONFIRMATION",
        "effect": "NONE",
    }, "legacy title-only lead scope")
    path = repo / DIRECTORY
    require(path.is_file() and not path.is_symlink(), "missing or symlinked discovery directory")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == DIRECTORY_SHA, "accepted discovery bytes drift")
    directory = json.loads(raw, object_pairs_hook=pairs_unique)
    require(directory["data_status"] == "DISCOVERY_ONLY" and directory["row_count"] == 1214,
            "discovery observations must not masquerade as admitted Works")
    by_id = {r["row_id"]: r for r in directory["rows"]}
    require(len(by_id) == len(directory["rows"]), "duplicate discovery row ID")
    cards = packet["source_local_episode_cards"]
    require(type(cards) is list and len(cards) == 5, "exact last five publisher cards")
    ids, videos, images = set(), set(), set()
    for i, card in enumerate(cards):
        episode, title, video_id, image_suffix, mentions, synopsis = PINS[i]
        require(type(card) is dict and set(card) == CARD_FIELDS, "closed card schema")
        require(card["local_id"] == f"pic-s2-e{episode:02d}-pplus-guide" and
                type(card["season"]) is int and card["season"] == 2 and
                type(card["episode_number"]) is int and card["episode_number"] == episode,
                "source-local season/episode scope")
        require(card["title"] == title and
                card["guide_line_window"] == [129 + i*5, 133 + i*5], "exact publisher card title/position")
        require(card["video_url"] == f"https://www.paramountplus.com/shows/video/{video_id}/" and
                card["thumbnail_url"] == IMAGE_BASE + image_suffix, "actual adjacent HTML media locator pair")
        require(card["thumbnail_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "no public image rights")
        require(type(card["literal_name_mentions"]) is list and
                card["literal_name_mentions"] == mentions and
                all(type(x) is str for x in card["literal_name_mentions"]), "literal description terms only")
        require(card["synopsis_paraphrase_candidate"] == synopsis and
                card["synopsis_state"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE", "original held guide synopsis")
        require(card["evidence_scope"] == "PUBLISHER_GUIDE_DESCRIPTION_AND_HTML_CARD", "not an episode or script read")
        lead = by_id[f"lead:{133 + i:04d}"]
        require(lead["title"] == title and lead["source_group"] == "wikidata:wdqs" and
                lead["verification_status"] == "UNVERIFIED_METADATA" and
                lead["identity_scope"] == "SOURCE_LOCAL" and
                lead["admission_effect"] == "NONE" and lead["coverage_effect"] == "NONE",
                "legacy Wikidata title lead was never direct audiovisual corroboration")
        ids.add(card["local_id"])
        videos.add(card["video_url"])
        images.add(card["thumbnail_url"])
    require(len(ids) == len(videos) == len(images) == 5, "duplicate identifiers / video / thumbnail")
    return len(cards)


if __name__ == "__main__":
    print(f"PIC_S2_P002_OK: {validate()} held S2 E6–E10 publisher cards; no media/Work/coverage release")
