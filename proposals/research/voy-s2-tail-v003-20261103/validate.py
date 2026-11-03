#!/usr/bin/env python3
"""Fail-closed Voyager S2 tail publisher metadata proposal validator.

Static pins guard proposal-integrity, not web authenticity or audiovisual truth.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GUIDE = "https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/"
CSV_PATH = "proposals/discovery/legacy-paramount-season2-20261102/voy.csv"
BUNDLE_PATH = "proposals/discovery/legacy-paramount-season2-20261102/voy/bundle.json"
B006_PATH = "proposals/verification/episode-guide-rechecks-b006-voy-20261103/observations.json"
EXPECTED = json.loads("{\"schema_version\":\"1.0.0\",\"batch_id\":\"voy-s2-tail-v003-20261103\",\"role\":\"VOY\",\"proposal_only\":true,\"accepted_main_at_selection\":\"aebf9e8a69ab44919f2d89ab60dd1e824e05a807\",\"observed_utc_date\":\"2026-11-03\",\"publisher_guide_url\":\"https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/\",\"source_scope\":\"PUBLIC_PARAMOUNT_VOY_S2_GUIDE_CARDS_TITLE_SLOT_DESCRIPTION_SHA_AND_HELD_MEDIA\",\"publisher_source_family\":\"publisher:paramountplus.com\",\"source_independence_status\":\"SAME_FAMILY_RECHECK_NOT_INDEPENDENT_CORROBORATION\",\"prior_s2_csv_sha256\":\"192a970935739a618b68609598532443da8fb9de2529d1d53399b323245c0a97\",\"prior_s2_bundle_sha256\":\"d9bc2e66f5a07e6b461a9d9fbf02aca7f8aaa5f3b9af4240c268e8df6db84edb\",\"prior_b006_voy_observations_sha256\":\"3b55fcf2b9a9aab7a02293400e4ccac1f62d0ad097ffb2ff057f02fa305b8080\",\"current_http_status_observed\":200,\"current_raw_html_bytes_observed\":317568,\"current_raw_html_sha256_observed\":\"f85cbd5121dabf75f60508a84feb9019ba3a6c04fda0cb7dd366a7dc71c49f26\",\"raw_current_html_archived\":false,\"actual_episode_or_script_read\":false,\"source_description_archived\":false,\"description_digest_method\":\"SHA256_UTF8_OF_HTML_UNESCAPED_TAG_STRIPPED_TRIMMED_OWN_CARD_DESCRIPTION\",\"synopsis_policy\":\"ALL_HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE\",\"artwork_policy\":\"FIRST_PARTY_CDN_URL_HELD_NO_LICENSE_OR_ASSET_BYTES\",\"accepted_source_work_effect\":\"NONE\",\"accepted_work_effect\":\"NONE\",\"coverage_effect\":\"NONE\",\"public_synopsis_effect\":\"NONE\",\"public_artwork_effect\":\"NONE\",\"overlap_exclusion\":\"S2E20_ALREADY_SOURCE_RECHECKED_B006_LEAD_0077_NOT_RECOUNTED\"}")
PINS = json.loads("[{\"season\":2,\"episode\":16,\"publisher_card_title\":\"Meld\",\"publisher_description_sha256\":\"e7cd2f3445f520011dbfe17e1c53ad7fb6d50f1eff694eec7e7bff037d41840a\",\"video_url\":\"https://www.paramountplus.com/shows/video/E9UlOAYt05bYBVA1iPHsMz2rNTBJlUqn/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25029699891/CBS_VOYAGER_133_IMAGE_CIAN_1181420_1920x1080.jpg\",\"literal_mentions\":[\"Lon Suder\",\"Tuvok\"]},{\"season\":2,\"episode\":17,\"publisher_card_title\":\"Dreadnought\",\"publisher_description_sha256\":\"86d283dc918810e8e1ce7c0cf9c0797d60c50c398efd69049605285d53d83968\",\"video_url\":\"https://www.paramountplus.com/shows/video/z2bPqPjNw_Qj13icCNJ6uvTkK397Qom1/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25030723949/CBS_VOYAGER_134_IMAGE_CIAN_1181406_1920x1080.jpg\",\"literal_mentions\":[\"Voyager\",\"Cardassian\",\"Torres\",\"Maquis\",\"B'Elanna\",\"Dreadnought\"]},{\"season\":2,\"episode\":18,\"publisher_card_title\":\"Death Wish\",\"publisher_description_sha256\":\"c2e8c460569fc5f5c22b1e6fcb9159aaecd0936f687260825720004ae562a146\",\"video_url\":\"https://www.paramountplus.com/shows/video/byHr9IAb1b3wH6kIIGH_R6g_j2FwpO2R/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25030723950/CBS_VOYAGER_130_IMAGE_CIAN_1181412_1920x1080.jpg\",\"literal_mentions\":[\"Q\",\"Q-Continuum\",\"Voyager\"]},{\"season\":2,\"episode\":19,\"publisher_card_title\":\"Lifesigns\",\"publisher_description_sha256\":\"888c1d98991d678cd7be6e077c0d8a7527943d89faa03b4c42d85b58f122448d\",\"video_url\":\"https://www.paramountplus.com/shows/video/iQGvQO1M6wki_5r_HCoGdTCE_4Tse51p/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25029187953/CBS_VOYAGER_136_IMAGE_CIAN_1181405_1920x1080.jpg\",\"literal_mentions\":[\"Vidiian\",\"The Doctor\"]},{\"season\":2,\"episode\":21,\"publisher_card_title\":\"Deadlock\",\"publisher_description_sha256\":\"8e22dd2b7189749ca1ba3e06ddb48f697edfc1ca1d52e44be454b7c97a0ebc6b\",\"video_url\":\"https://www.paramountplus.com/shows/video/mJjnH_apEeZJwrs0mUUEJ11KnN7KfWoN/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25033283723/CBS_VOYAGER_137_IMAGE_CIAN_1181407_1920x1080.jpg\",\"literal_mentions\":[\"Voyager\",\"Vidiians\"]},{\"season\":2,\"episode\":22,\"publisher_card_title\":\"Innocence\",\"publisher_description_sha256\":\"691b8eaa807e9b5c04efd482a91778f352a7268b641f11f38e25cbd3cdb3091d\",\"video_url\":\"https://www.paramountplus.com/shows/video/_YS5UBzkoMI78SZrrwnn3tyRtt0eLZD1/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25033283726/CBS_VOYAGER_138_IMAGE_CIAN_1181418_1920x1080.jpg\",\"literal_mentions\":[\"Tuvok\"]},{\"season\":2,\"episode\":23,\"publisher_card_title\":\"The Thaw\",\"publisher_description_sha256\":\"8f34436da15ffcc827ce3819f1df97b4f1a3e68cb7a2d58296658ba452218603\",\"video_url\":\"https://www.paramountplus.com/shows/video/KS_pE5B3fyNOIQFuA_X16lZJcLKrUS9E/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25032771814/CBS_VOYAGER_139_IMAGE_CIAN_1181413_1920x1080.jpg\",\"literal_mentions\":[\"Voyager\"]},{\"season\":2,\"episode\":24,\"publisher_card_title\":\"Tuvix\",\"publisher_description_sha256\":\"765e29a1629251a477b2be818609c68aff02115d7af9af6ad11ab8adc007f958\",\"video_url\":\"https://www.paramountplus.com/shows/video/7cxHzuLPHfnRdqUXFVHglxrv7VUJZnzJ/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25032771815/CBS_VOYAGER_140_IMAGE_CIAN_1181416_1920x1080.jpg\",\"literal_mentions\":[\"Tuvok\",\"Neelix\"]},{\"season\":2,\"episode\":25,\"publisher_card_title\":\"Resolutions\",\"publisher_description_sha256\":\"f5a488831eda94e2ed7050b3e072ab78d2fde523423b0032160181db40404603\",\"video_url\":\"https://www.paramountplus.com/shows/video/dm_YP5W_SzoAsQOolFttk_npMr5ljDyF/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25032771816/CBS_VOYAGER_141_IMAGE_CIAN_1181415_1920x1080.jpg\",\"literal_mentions\":[\"Captain Janeway\",\"Chakotay\",\"Janeway\"]},{\"season\":2,\"episode\":26,\"publisher_card_title\":\"Basics, Part 1\",\"publisher_description_sha256\":\"ae3ee1cf9412378fc72b0345cdee875a46a60a26948ae8f845ecf24dc539a230\",\"video_url\":\"https://www.paramountplus.com/shows/video/8PYLltyxrFuIrAXV3T9cCZpFJT_vTDK0/\",\"thumbnail_url\":\"https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2013/04/08/25031747804/CBS_VOYAGER_142_CONTENT_CIAN_418408_1928_1280x720_339328579965_1181419_1920x1080.jpg\",\"literal_mentions\":[\"Seska\",\"Chakotay\",\"Voyager\",\"Maj Cullah\"]}]")
SLOTS = [16,17,18,19,21,22,23,24,25,26]
RECORD_KEYS = {
    "observation_id","local_card_entity_id","season","episode",
    "publisher_card_title","publisher_description_sha256","video_url",
    "thumbnail_url","literal_mentions","card_locator","literal_mention_scope",
    "synopsis_status","artwork_rights_status","image_bytes_retrieved","accepted_work_id",
}

def require(ok: bool, msg: str):
    if not ok:
        raise ValueError("VOY V003 source custody invalid: " + msg)

def unique_pairs(pairs):
    result = {}
    for key, val in pairs:
        require(key not in result, "duplicate JSON key " + key)
        result[key] = val
    return result

def read_json(path: Path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000, "unsafe JSON")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)

def upstream(rel: str, sha: str):
    path = ROOT / rel
    require(path.is_file() and not path.is_symlink(), "missing or symlinked accepted source")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == sha, "accepted source drift: " + rel)
    return path

def exact_https(url, host):
    if type(url) is not str:
        return False
    p = urlsplit(url)
    return (p.scheme == "https" and p.hostname == host and p.port is None
            and p.username is None and p.password is None and not p.query and not p.fragment)

def expected_card(i, row):
    n = i+1
    return {
        "observation_id": f"voy-v003-o{n:02d}",
        "local_card_entity_id": f"voy-v003-card-{row['episode']}",
        "season": 2,
        "episode": row["episode"],
        "publisher_card_title": row["publisher_card_title"],
        "publisher_description_sha256": row["publisher_description_sha256"],
        "video_url": row["video_url"],
        "thumbnail_url": row["thumbnail_url"],
        "literal_mentions": row["literal_mentions"],
        "card_locator": f"Season 2 Episode Guide > S2 E{row['episode']} > {row['publisher_card_title']} > description",
        "literal_mention_scope": "PUBLISHER_DESCRIPTION_TEXT_ONLY_NOT_EPISODE_DEPICTION",
        "synopsis_status": "HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE",
        "artwork_rights_status": "HELD_NO_PUBLIC_DISPLAY_LICENSE",
        "image_bytes_retrieved": False,
        "accepted_work_id": None,
    }

def validate(data=None):
    if data is None:
        data = read_json(HERE / "observations.json")
    require(type(data) is dict and set(data) == set(EXPECTED) | {"records"}, "closed envelope")
    for key, val in EXPECTED.items():
        require(type(data[key]) is type(val) and data[key] == val, "source/admission metadata " + key)
    with upstream(CSV_PATH, EXPECTED["prior_s2_csv_sha256"]).open(encoding="utf-8",newline="") as f:
        directory = list(csv.DictReader(f))
    require(len(directory) == 26, "accepted season-2 directory size")
    bundle = read_json(upstream(BUNDLE_PATH, EXPECTED["prior_s2_bundle_sha256"]))
    require(bundle["mission_id"] == "voy" and bundle["listed_slot_count"] == 26 and
            bundle["observation"]["primary_locator"] == GUIDE and
            bundle["accepted_work_effect"] == "NONE" and bundle["coverage_effect"] == "NONE",
            "accepted publisher source provenance")
    prior = read_json(upstream(B006_PATH, EXPECTED["prior_b006_voy_observations_sha256"]))
    require(prior["proposal_id"] == "LIBRARIAN-B006-VOY-RENDERED-METADATA-20261103" and
            [(r["episode"],r["official_title"],r["row_id"]) for r in prior["rows"] if r["season"] == 2]
            == [(2,"Initiations","lead:0076"),(20,"Investigations","lead:0077")],
            "S2E20 accepted overlap exclusion")
    records = data["records"]
    require(type(records) is list and len(records) == 10, "exact 10 new source cards")
    seen = set()
    for i, row in enumerate(PINS):
        ep = SLOTS[i]
        require(row["episode"] == ep and row["season"] == 2 and
                directory[ep-1] == {"season":"2","episode_number":str(ep),"title":row["publisher_card_title"]},
                "accepted directory crosscheck")
        card = records[i]
        require(type(card) is dict and set(card) == RECORD_KEYS and card == expected_card(i,row),
                f"card {ep} immutable own-card source fields")
        require(type(card["episode"]) is int and type(card["season"]) is int and
                card["image_bytes_retrieved"] is False and card["accepted_work_id"] is None,
                f"card {ep} primitive types")
        require(card["observation_id"] not in seen, "duplicate evidence ID")
        seen.add(card["observation_id"])
        require(exact_https(card["video_url"],"www.paramountplus.com") and
                exact_https(card["thumbnail_url"],"thumbnails.cbsig.net"),
                f"card {ep} publisher media locator hosts")
        require(type(card["literal_mentions"]) is list and
                all(type(m) is str and m for m in card["literal_mentions"]),
                f"card {ep} explicit source utterance strings")
    return len(records)

if __name__ == "__main__":
    print(f"VOY_V003_OK: {validate()} held S2 official guide cards; no AV/Work/coverage/art rights")
