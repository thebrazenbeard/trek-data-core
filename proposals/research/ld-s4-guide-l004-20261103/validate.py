#!/usr/bin/env python3
"""Exact source-relative Lower Decks S4 publisher guide-card gate, no admissions."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE / "observations.json"
GUIDE = "https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/4/"
PREVIOUS = "proposals/research/ld-s3-guide-l003-20261103/observations.json"
PREVIOUS_SHA = "e8153b87644354a60ff900f0cc612b4efe37aae9dccbd13fc95960879f575e65"
IMAGE_PREFIX = "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/"
SOURCE_RECEIPT = {
    "publisher_family": "publisher:paramountplus.com",
    "guide_url": GUIDE,
    "method": "DIRECT_HTTP_GET_AND_RENDERED_PUBLISHER_GUIDE",
    "http_status_observed": 200,
    "html_bytes_observed": 271583,
    "html_sha256_observed": "e78ce95aca066d8bc126fc203bf1c28b1bf16a8675847e28d3821f566d73dc32",
    "raw_html_retained": False,
    "source_edition_stability": "DYNAMIC_HTML_SINGLE_TRANSIENT_RETRIEVAL_NOT_IMMUTABLE_EDITION",
    "full_episode_or_script_read": False,
    "scope": "TEN_GUIDE_CARDS_NOT_AUDIOVISUAL_CONTENT",
}
PREDECESSOR = {
    "path": PREVIOUS,
    "sha256": PREVIOUS_SHA,
    "relation": "PREVIOUS_SEASON_SAME_PUBLISHER_FAMILY_NOT_CORROBORATION",
}
TOP = {
    "schema_version", "batch_id", "role", "proposal_only", "baseline_accepted_main",
    "observed_utc_date", "source", "accepted_predecessor",
    "accepted_source_work_effect", "accepted_work_effect", "coverage_effect",
    "denominator_effect", "public_synopsis_effect", "public_artwork_effect", "records",
}
ROW = {
    "observation_id", "local_card_entity_id", "season", "episode", "publisher_card_title",
    "publisher_description_sha256", "card_locator", "literal_mentions", "publisher_thumbnail_url_held",
}

# Each tuple is independently taken from its OWN current Paramount+ S4 card:
# displayed title, ordinal, description fingerprint, literal mention tokens and
# exact adjacent HTML image locator. Publisher copy and image bytes are absent.
PINS = (
    ("Twovix", "1d5e9d98f841cb2335fe8e3b68b47424da9041ab50cc7ac61ca05f889e2aa182",
     ("Cerritos",), "2023/07/12/2243941955837/STAR_TREK_LOWER_DECKS_401_NO_LOGO_2335698_1920x1080.jpg"),
    ("I Have No Bones Yet I Must Flee", "d4e82bd11f480cdf665c64355459cee8e8c43317518088d55a39a80fc757d69c",
     ("Mariner", "Rutherford", "Boimler"), "2023/07/12/2243941955838/STAR_TREK_LOWER_DECKS_402_NO_LOGO_2335697_1920x1080.jpg"),
    ("In the Cradle of Vexilon", "3f20af15624c0f6389fa33507d85e98532fe95314341f2be6e4bfb5c1ec2e91b",
     ("Boimler",), "2023/07/12/2243941955839/STAR_TREK_LOWER_DECKS_403_NO_LOGO_2347249_1920x1080.jpg"),
    ("Something Borrowed, Something Green", "9ad0d1593c2ca5cd7d56fb6e7815035d3842b212ae9718a61f26a466f1a49c87",
     ("Tendi", "Orion"), "2023/07/12/2243942467755/STAR_TREK_LOWER_DECKS_404_NO_LOGO_2354391_1920x1080.jpg"),
    ("Empathalogical Fallacies", "e0fe46f91beeccf0fb616009778e63d115e776fd061942e9955e7b2f011adfac",
     ("Betazoids", "Cerritos"), "2023/07/12/2243942979777/STAR_TREK_LOWER_DECKS_405_NO_LOGO.jpg"),
    ("Parth Ferengi's Heart Place", "2c66ee5a6a04f2a16d12a8034616b1c925546d789a32eb530a6975dfaba57df8",
     ("Cerritos", "Ferengi"), "2023/07/12/2243943491688/STAR_TREK_LOWER_DECKS_406_NO_LOGO_2372723_1920x1080.jpg"),
    ("A Few Badgeys More", "5c318d5c28645aae5b768f4f463012d34832c0571f35a45ebb80e7483d8b5cab",
     ("Cerritos",), "2023/07/12/2243944003577/STAR_TREK_LOWER_DECKS_407_NO_LOGO_2382768_1920x1080.jpg"),
    ("Caves", "e5a8108d6ac05816339e11f018a927c6933d046d72de80c457051ad20bf508c2",
     ("Lower Deckers",), "2023/07/12/2243944003578/STAR_TREK_LOWER_DECKS_408_NO_LOGO_2388375_1920x1080.jpg"),
    ("The Inner Fight", "66ff911cc16fb9861055a4af040fdcc18f526906a2b8990a66cda89379d4f1ca",
     ("Captain Freeman", "Lower Deckers", "Mariner"), "2023/07/12/2243944515609/STAR_TREK_LOWER_DECKS_409_NO_LOGO_2398071_1920x1080.jpg"),
    ("Old Friends, New Planets", "02edc3769d1bb9e82bba09e6ee6973d652e940be84028f1e199f928c229dd688",
     ("Mariner",), "2023/07/12/2243945539535/STAR_TREK_LOWER_DECKS_410_NO_LOGO_2408283_1920x1080.jpg"),
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("LD S4 L004 held source gate: " + reason)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def load(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size < 100_000,
            "missing, symlinked or oversized packet")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def validate(data: dict | None = None, root: Path = ROOT) -> int:
    if data is None:
        data = load(PACKET)
    require(type(data) is dict and set(data) == TOP, "closed packet fields")
    expected_top = {
        "schema_version": "1.0.0", "batch_id": "ld-s4-guide-l004-20261103",
        "role": "LD", "proposal_only": True,
        "baseline_accepted_main": "c1668772cab7004da1bfe0759f521d22c3679280",
        "observed_utc_date": "2026-11-03",
    }
    for key, value in expected_top.items():
        require(type(data[key]) is type(value) and data[key] == value, "packet identity: " + key)
    require(data["source"] == SOURCE_RECEIPT and type(data["source"]) is dict,
            "source access/snapshot custody or publisher lineage")
    require(data["accepted_predecessor"] == PREDECESSOR and
            type(data["accepted_predecessor"]) is dict, "previous season lineage")
    for field in ("accepted_source_work_effect", "accepted_work_effect", "coverage_effect",
                  "denominator_effect", "public_synopsis_effect", "public_artwork_effect"):
        require(type(data[field]) is str and data[field] == "NONE", "forbidden effect: " + field)
    prior_path = root / PREVIOUS
    require(prior_path.is_file() and not prior_path.is_symlink(), "previous accepted season absent")
    raw = prior_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PREVIOUS_SHA, "previous accepted source bytes drifted")
    prior = json.loads(raw, object_pairs_hook=unique_pairs)
    require(prior.get("batch_id") == "ld-s3-guide-l003-20261103" and
            prior.get("coverage_effect") == "NONE" and
            prior.get("accepted_work_effect") == "NONE" and
            len(prior.get("records", [])) == 10, "previous accepted status/frontier drift")
    previous_ids = {r.get("local_card_entity_id") for r in prior["records"]}
    records = data["records"]
    require(type(records) is list and len(records) == 10, "ten exact publisher cards required")
    identifiers, artwork = set(), set()
    for index, rec in enumerate(records, 1):
        title, description_hash, mentions, image_suffix = PINS[index - 1]
        require(type(rec) is dict and set(rec) == ROW, f"card {index} closed fields")
        local_id = f"ld-l004-card-{index:02d}"
        observation_id = f"ld-l004-o{index:02d}"
        require(rec["local_card_entity_id"] == local_id and local_id not in previous_ids and
                rec["observation_id"] == observation_id and local_id not in identifiers,
                f"card {index} source-local identity or collision")
        identifiers.add(local_id)
        require(type(rec["season"]) is int and rec["season"] == 4 and
                type(rec["episode"]) is int and rec["episode"] == index and
                rec["publisher_card_title"] == title and
                rec["publisher_description_sha256"] == description_hash,
                f"card {index} publisher title/slot/description hash")
        require(rec["card_locator"] == f"Season 4 Episode Guide > S4 E{index} > {title} > description",
                f"card {index} full source-relative locator")
        require(type(rec["literal_mentions"]) is list and rec["literal_mentions"] == list(mentions),
                f"card {index} unreviewed publisher mention")
        image = rec["publisher_thumbnail_url_held"]
        parts = urlsplit(image) if isinstance(image, str) else None
        require(parts is not None and parts.scheme == "https" and
                parts.netloc == "thumbnails.cbsig.net" and not parts.query and not parts.fragment and
                not parts.username and not parts.password and
                bool(re.fullmatch(r"/_x/w400/CBS_Production_Entertainment_VMS/[A-Za-z0-9_./-]+\.jpg", parts.path)) and
                image == IMAGE_PREFIX + image_suffix and image not in artwork,
                f"card {index} exact own-card publisher art URL or duplicate")
        artwork.add(image)
    return len(records)


if __name__ == "__main__":
    print(f"LD_S4_L004_OK: {validate()} publisher source-local cards; synopses, image rights, Work and coverage HELD")
