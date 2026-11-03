#!/usr/bin/env python3
"""Source-local Picard guide-card validation; never promotes episode coverage."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
UPSTREAM = "proposals/discovery/modern-paramount-season1-20261102/pic-observed-slots.csv"
UPSTREAM_SHA = "a3c798fce4ab4121f8487319d921a56f42a3793b4668273474e69a74842f383c"
SOURCE = "https://www.paramountplus.com/shows/star-trek-picard/episodes/1/"
SOURCE_RECEIPTS = [
    {"bytes": 273178, "sha256": "4c83db68d022e895fd5c1e7581e09aca04984828b6bc23ba4c7d0817f5e1356e"},
    {"bytes": 273178, "sha256": "c0828d5836c211eebcc88bda32a21832d9ed8ac5b0bb08554f5d1ef984c0c250"},
]
PINS = [
    (
        "Remembrance", "p_F16OmokbFpnKJC64lcdoP9_MdR1I7D",
        "2020/01/11/1669514307830/CBS_STAR_TREK_PICARD_101_NO_LOGO_IMAGE_162071_1920x1080.jpg",
        ["Jean-Luc Picard", "Dahj"],
        "Retired Picard meets Dahj, whose need for help suggests an unexpected connection to his past.",
    ),
    (
        "Maps and Legends", "dEv998pdGs_0n4meq536O_U7KgdES1Ew",
        "2020/01/23/1684686403944/CBS_STAR_TREK_PICARD_102_NO_LOGO_IMAGE__746585_165221_1920x1080.jpg",
        ["Picard", "Dahj", "Agnes Jurati", "Raffi Musiker"],
        "Without Starfleet's backing, Picard seeks help from Jurati and Raffi while investigating Dahj's significance.",
    ),
    (
        "The End is the Beginning", "hB4J7gllhhJUPRpYkgpQwjYb2sTfwIr9",
        "2020/01/30/1691286595587/CBS_STAR_TREK_PICARD_103_NO_LOGO_IMAGE_167174_1920x1080.jpg",
        ["Soji", "Raffi", "Picard", "Bruce Maddox", "Cristóbal Rios"],
        "Soji attracts scrutiny at the Borg research project as Picard recruits help to locate Maddox.",
    ),
    (
        "Absolute Candor", "bRbQB8Mj_ylqhHCcD96HIkpZ1j1ZVqxD",
        "2020/02/05/1693801539611/CBS_STAR_TREK_PICARD_104_NO_LOGO_IMAGE_168648_1920x1080.jpg",
        ["Picard", "Raffi", "Elnor", "Narek", "Soji", "Narissa"],
        "Picard detours to Vashti and reconnects with Elnor while Narek continues seeking information about Soji.",
    ),
    (
        "Stardust City Rag", "o1UkhNQZmPtcDud9Ku1fH4M6lHJ8abMw",
        "2020/02/11/1696553027846/CBS_STAR_TREK_PICARD_105_NO_LOGO_IMAGE_171583_1920x1080.jpg",
        ["La Sirena", "Bruce Maddox"],
        "The La Sirena crew heads to Freecloud to find Bruce Maddox, whose situation puts their search at risk.",
    ),
]
BASE_IMAGE = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
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
    "local_id", "season", "episode_number", "title", "guide_line_window",
    "video_url", "thumbnail_url", "thumbnail_status", "literal_name_mentions",
    "synopsis_paraphrase_candidate", "synopsis_state", "evidence_scope",
}


def _pairs_unique(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_unique)


def validate(obj: object, repo: Path = REPO) -> None:
    def require(ok: bool, message: str) -> None:
        if not ok:
            raise ValueError(message)

    require(isinstance(obj, dict) and set(obj) == PACKET_FIELDS, "packet schema")
    require(obj["schema_version"] == "1.0.0" and obj["batch_id"] == "PIC.PPLUS.S1.FIRST5.CARDS.20261103", "packet identity")
    require(obj["role"] == "PIC" and obj["proposal_only"] is True, "role/proposal boundary")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(obj[key] == "NONE", f"forbidden {key}")
    src = obj["source"]
    require(isinstance(src, dict) and set(src) == SOURCE_FIELDS, "source schema")
    require(src["local_id"] == "pic-pplus-s1-episode-guide-20261103", "source local id")
    require(src["provider"] == "Paramount+" and src["independence_group"] == "publisher:paramountplus.com", "publisher lineage")
    require(src["url"] == SOURCE and src["retrieval_date_utc"] == "2026-11-03", "source locator/date")
    require(src["retrieval_method"] == "DIRECT_HTTP_GET_AND_RENDERED_WEB_VIEW" and src["http_status"] == 200, "source access")
    require(src["raw_sample_receipts"] == SOURCE_RECEIPTS, "observed dynamic HTML digests")
    require(src["raw_html_retained_in_public_repo"] is False and
            src["publisher_html_stability"] == "DIFFERING_RESPONSE_DIGESTS_SAME_CARD_OBSERVATIONS", "mutable source caveat")
    require(src["full_primary_audiovisual_content_read"] is False and
            src["scope"] == "SEASON_GUIDE_CARD_METADATA_NOT_EPISODE_CONTENT", "no episode full-text evidence")
    require(obj["upstream_discovery"] == {
        "path": UPSTREAM, "sha256": UPSTREAM_SHA, "effect": "SOURCE_LOCAL_CROSSCHECK_ONLY"}, "discovery crosscheck")

    source_path = repo / UPSTREAM
    require(source_path.is_file() and not source_path.is_symlink(), "missing exact upstream discovery")
    data = source_path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == UPSTREAM_SHA, "upstream digest drift")
    rows = list(csv.DictReader(data.decode("utf-8").splitlines()))
    require(len(rows) == 10 and [row["title"] for row in rows[:5]] == [x[0] for x in PINS], "upstream episode crosswalk changed")
    cards = obj["source_local_episode_cards"]
    require(isinstance(cards, list) and len(cards) == 5, "five exact guide cards required")
    require(len({c.get("local_id") for c in cards if isinstance(c, dict)}) == 5, "duplicate local IDs")
    require(len({c.get("thumbnail_url") for c in cards if isinstance(c, dict)}) == 5, "duplicate thumbnail URLs")
    for i, card in enumerate(cards, 1):
        require(isinstance(card, dict) and set(card) == CARD_FIELDS, f"card {i} schema")
        title, video_id, image_suffix, mentions, synopsis = PINS[i - 1]
        require(card["local_id"] == f"pic-s1-e{i:02d}-pplus-guide", f"card {i} ID")
        require((card["season"], card["episode_number"], card["title"], card["guide_line_window"]) ==
                (1, i, title, [103 + 5*(i-1), 107 + 5*(i-1)]), f"card {i} position/title/line")
        video_url = f"https://www.paramountplus.com/shows/video/{video_id}/"
        thumb_url = BASE_IMAGE + image_suffix
        require(card["video_url"] == video_url and card["thumbnail_url"] == thumb_url,
                f"card {i} exact video/thumbnail bindings")
        for url, host in ((video_url, "www.paramountplus.com"), (thumb_url, "thumbnails.cbsig.net")):
            parsed = urlsplit(url)
            require(parsed.scheme == "https" and parsed.hostname == host and parsed.port is None and
                    parsed.username is None and parsed.password is None and not parsed.query and not parsed.fragment,
                    f"card {i} strict source domain")
        require(card["literal_name_mentions"] == mentions, f"card {i} literal mentions")
        require(card["synopsis_paraphrase_candidate"] == synopsis, f"card {i} synopsis custody")
        require(card["synopsis_state"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE", f"card {i} synopsis gate")
        require(card["thumbnail_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE", f"card {i} artwork gate")
        require(card["evidence_scope"] == "PUBLISHER_GUIDE_DESCRIPTION_AND_HTML_CARD", f"card {i} evidence scope")


if __name__ == "__main__":
    validate(load(HERE / "records.json"))
    print("PICARD_PPLUS_SOURCE_LOCAL_OK: 5 exact S1 guide cards; no Work, image release, or coverage effect")
