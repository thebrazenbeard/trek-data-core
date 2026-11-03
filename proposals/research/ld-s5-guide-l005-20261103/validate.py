#!/usr/bin/env python3
"""Strict, proposal-only LD Season 5 publisher guide-card custody checks.

Static row pins constrain the reviewed research proposal, not outside source bytes
or public display rights.  Source descriptions and image binaries are not stored.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/5/"
CSV_PATH = "proposals/discovery/publisher-season5-20261102/ld.csv"
BUNDLE_PATH = "proposals/discovery/publisher-season5-20261102/ld/bundle.json"
CSV_SHA = "500b9c1498c2fb493918d356f4c47ae31eba3c3554ac80ea48db356cb0be1d93"
BUNDLE_SHA = "49c52ca05f91373cd146039df14cefb9bfba0ee839a68034ec77297df0e2fc28"

EXPECTED_ENVELOPE = json.loads("{\"schema_version\":\"1.0.0\",\"batch_id\":\"ld-s5-guide-l005-20261103\",\"role\":\"LD\",\"proposal_only\":true,\"accepted_main_at_selection\":\"7cf99513f36396cf54512f78faf9d59ceddf68f9\",\"observed_utc_date\":\"2026-11-03\",\"publisher_guide_url\":\"https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/5/\",\"source_scope\":\"PUBLIC_PARAMOUNT_LD_S5_GUIDE_CARD_TITLE_SLOT_DESCRIPTION_SHA_VIDEO_THUMB_AND_LITERAL_MENTIONS\",\"publisher_source_family\":\"publisher:paramountplus.com\",\"source_independence_status\":\"SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION\",\"historical_s5_csv_sha256\":\"500b9c1498c2fb493918d356f4c47ae31eba3c3554ac80ea48db356cb0be1d93\",\"historical_s5_bundle_sha256\":\"49c52ca05f91373cd146039df14cefb9bfba0ee839a68034ec77297df0e2fc28\",\"current_http_status_observed\":200,\"current_raw_html_bytes_observed\":271253,\"current_raw_html_sha256_observed\":\"03f94a288dd368474b5ecc0f4a7048ee641122531a7f08327de0a557350a1ad5\",\"current_raw_html_archived\":false,\"actual_episode_or_script_read\":false,\"source_description_archived\":false,\"synopsis_policy\":\"ALL_HELD_SOURCE_RELATIVE_PARAPHRASES_ONLY\",\"artwork_policy\":\"CDN_LOCATORS_HELD_NO_LICENSE_OR_IMAGE_BYTES\",\"accepted_source_work_effect\":\"NONE\",\"accepted_work_effect\":\"NONE\",\"coverage_effect\":\"NONE\",\"public_synopsis_effect\":\"NONE\",\"public_artwork_effect\":\"NONE\"}")
PINS = [
  [
    "Dos Cerritos",
    "037d75952bc98d0280f2dc4aa2f2da400673dabf83d4418501b6ed283ac4a47b",
    "https://www.paramountplus.com/shows/video/hCfpQSlio_WUaSAu_e4okDCcKUOUAfYT/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547983/PPUSA_STARTREKLOWERDECKS_501_2941533_1920x1080.jpg",
    [
      "Cerritos",
      "Tendi"
    ],
    "A spatial disturbance confronts Cerritos personnel with their own likenesses as Tendi takes on a pirate role."
  ],
  [
    "Shades of Green",
    "a3dbe505f9dbce0de3ed1083bee4fc8bebd3c1dc5407a99e2ea0f96d36cdf7f0",
    "https://www.paramountplus.com/shows/video/IyUJTHuQR68mYiuJXimKBAP4S5OWsjCp/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547984/PPUSA_STARTREKLOWERDECKS_502_2941230_1920x1080.jpg",
    [
      "Tendi",
      "Boimler",
      "Mariner"
    ],
    "Tendi tries to avert a confrontation as Boimler and Mariner oppose profit-minded interests."
  ],
  [
    "The Best Exotic Nanite Hotel",
    "52a02529621ba8609b2e33c293252d517c76899d985000ed80e8da2ce8f9b9a7",
    "https://www.paramountplus.com/shows/video/5Hquxjwfox7zWQBcC_dF_35Eo3NFAH3z/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374550083885/PPUSA_STARTREKLOWERDECKS_503_2942947_1920x1080.jpg",
    [
      "Lower Deckers",
      "nanites"
    ],
    "The lower-deck crew searches for nanites at a resort beyond Earth."
  ],
  [
    "A Farewell to Farms",
    "345bace152bf06a0f8459fc3c28863c1188c0a7402fe0cdeb8c6f6b1b10f52a4",
    "https://www.paramountplus.com/shows/video/6ML5EmzNRpMQeUJmtYU7f1s6N_Qn2w_T/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547977/PPUSA_STARTREKLOWERDECKS_504_2942948_1920x1080.jpg",
    [
      "Dr. Migleemo",
      "Mariner"
    ],
    "Migleemo prepares food while Mariner favors a cooler response."
  ],
  [
    "Starbase 80?!",
    "e42e40588a2e1150d750aae19bbce4289e6b18a9f4ded5feb7416644476c2722",
    "https://www.paramountplus.com/shows/video/illawoYnvJW00m9NuxDLPXef9P4QC0e5/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374551619575/PPUSA_STARTREKLOWERDECKS_505_2942945_1920x1080.jpg",
    [
      "Ransom",
      "Mariner"
    ],
    "Ransom's heavy use of cleaning gel contrasts with Mariner's worries about supernatural trouble."
  ],
  [
    "Of Gods and Angles",
    "4dc1db74b284e5cda56fdcd0621d41cebe65ac57b03fe00aa29ca3b08a95f9d8",
    "https://www.paramountplus.com/shows/video/dNCwssTj6GeMcYxcmOdtue_sLLRlnGaO/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547962/PPUSA_STARTREKLOWERDECKS_506_2942949_1920x1080.jpg",
    [
      "Mariner",
      "Cerritos"
    ],
    "Mariner pairs with a struggling ensign while the Cerritos welcomes rival groups for negotiations."
  ],
  [
    "Fully Dilated",
    "104fe4613227f013efddc4e55807dfaefafc4d6f8ac203aa05e93a89c92a662c",
    "https://www.paramountplus.com/shows/video/RurJpnA8vdJ4eWaU8Ark1xG7ZMBifwbR/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547950/PPUSA_STARTREKLOWERDECKS_507_2942946_1920x1080.jpg",
    [
      "pre-warp society",
      "Girls Trip"
    ],
    "An undercover trip involves a society that has not achieved warp travel."
  ],
  [
    "Upper Decks",
    "aeb8ee0dc7f89ce74c853739a542d9941735cc22db88c0c090f5bf9eb24cc2d6",
    "https://www.paramountplus.com/shows/video/rD3i3i0RnZidvb9BjnBDUU_lqprTYxFn/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374550083833/PPUSA_STARTREKLOWERDECKS_508_3013021_1920x1080.jpg",
    [
      "Lower Deckers",
      "pumpkin carving"
    ],
    "The lower-deck crew gathers for a pumpkin-carving celebration."
  ],
  [
    "Fissure Quest",
    "a4a97cdd2a9dc0a48e836926f349871c953f3daf39e79095fc0902ede0f7526c",
    "https://www.paramountplus.com/shows/video/7O936gPuerwlKvlPMdpnjUtHaVHpv28z/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374548547949/PPUSA_STARTREKLOWERDECKS_509_3015366_1920x1080.jpg",
    [
      "Fissures"
    ],
    "An unspecified set of fissures must be shut before conditions deteriorate."
  ],
  [
    "The New Next Generation",
    "5fc83696ccd2839c42349ac13fedaf928409b126b29fa5c60b1872668051d627",
    "https://www.paramountplus.com/shows/video/Y57vs49llitR2O0yXwzfZcMv7IgDZQg4/",
    "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2024/09/23/2374551619555/PPUSA_STARTREKLOWERDECKS_510_3015350_1920x1080.jpg",
    [
      "Season finale"
    ],
    "The publisher describes the season's conclusion as an unpredictable finale."
  ]
]
RECORD_KEYS = {
    "observation_id", "local_card_entity_id", "season", "episode",
    "publisher_card_title", "publisher_description_sha256", "card_locator",
    "video_url", "thumbnail_url", "literal_mentions", "literal_mention_scope",
    "synopsis_paraphrase_candidate", "synopsis_status", "artwork_rights_status",
    "image_bytes_retrieved", "accepted_work_id",
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError("LD L005 source proposal invalid: " + why)


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key " + key)
        out[key] = value
    return out


def read_json(path: Path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
            "unsafe JSON path")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def upstream(relative: str, digest: str) -> Path:
    p = ROOT / relative
    require(p.is_file() and not p.is_symlink(), "missing or symlinked source")
    require(hashlib.sha256(p.read_bytes()).hexdigest() == digest, "prior accepted discovery drift")
    return p


def exact_https(url: str, host: str) -> bool:
    if type(url) is not str:
        return False
    p = urlsplit(url)
    return (p.scheme == "https" and p.hostname == host and p.port is None and
            p.username is None and p.password is None and not p.query and not p.fragment)


def validate(data=None):
    if data is None:
        data = read_json(HERE / "observations.json")
    require(type(data) is dict and set(data) == set(EXPECTED_ENVELOPE) | {"records"},
            "closed envelope fields")
    for field, value in EXPECTED_ENVELOPE.items():
        require(type(data[field]) is type(value) and data[field] == value,
                "forged source/admission envelope " + field)
    require(data["publisher_guide_url"] == GUIDE, "guide locator")
    with upstream(CSV_PATH, CSV_SHA).open(encoding="utf-8", newline="") as f:
        directory = list(csv.DictReader(f))
    require(len(directory) == 10 and all(directory[i] == {
        "season": "5", "episode_number": str(i + 1), "title": PINS[i][0],
    } for i in range(10)), "historical publisher title/slot candidates")
    bundle = read_json(upstream(BUNDLE_PATH, BUNDLE_SHA))
    require(bundle["mission_id"] == "ld" and
            bundle["observation"]["primary_locator"] == GUIDE and
            bundle["listed_slot_count"] == 10 and
            bundle["coverage_effect"] == "NONE" and
            bundle["accepted_work_effect"] == "NONE", "accepted source-family seed status")
    records = data["records"]
    require(type(records) is list and len(records) == 10, "exactly ten guide cards")
    seen = set()
    for i, card in enumerate(records, 1):
        require(type(card) is dict and set(card) == RECORD_KEYS, f"card {i} closed fields")
        title, desc_sha, video, thumb, mentions, synopsis = PINS[i - 1]
        identity = f"ld-l005-o{i:02d}"
        require(card["observation_id"] == identity and identity not in seen and
                card["local_card_entity_id"] == f"ld-l005-card-{i:02d}",
                f"card {i} exact local IDs")
        seen.add(identity)
        require(type(card["season"]) is int and card["season"] == 5 and
                type(card["episode"]) is int and card["episode"] == i and
                card["publisher_card_title"] == title and
                card["publisher_description_sha256"] == desc_sha and
                card["card_locator"] == f"Season 5 Episode Guide > S5 E{i} > {title} > description",
                f"card {i} title/slot/description source binding")
        require(card["video_url"] == video and card["thumbnail_url"] == thumb and
                exact_https(video, "www.paramountplus.com") and
                exact_https(thumb, "thumbnails.cbsig.net"),
                f"card {i} own video + thumbnail URL binding")
        require(type(card["literal_mentions"]) is list and card["literal_mentions"] == mentions and
                card["literal_mention_scope"] == "PUBLISHER_DESCRIPTION_TEXT_ONLY_NOT_EPISODE_DEPICTION",
                f"card {i} publisher-utterance terms")
        require(card["synopsis_paraphrase_candidate"] == synopsis and
                card["synopsis_status"] == "HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_EPISODE_READ",
                f"card {i} synopsis hold")
        require(card["artwork_rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE" and
                card["image_bytes_retrieved"] is False and card["accepted_work_id"] is None,
                f"card {i} artwork / Work hold")
    return len(records)


if __name__ == "__main__":
    print(f"LD_L005_OK: {validate()} source-local official S5 guide cards; no Work/coverage/public art")
