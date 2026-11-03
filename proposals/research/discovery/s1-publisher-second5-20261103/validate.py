"""Validate Discovery S1E06–E10 publisher-only source-local research.

The public repository contains locators, digests, original paraphrases and
research structure, not raw Paramount+ HTML or copyrighted audiovisual assets.
The --source-html switch replays the exact separately retrieved source bytes.
"""

import argparse
import hashlib
import html
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORDS = HERE / "records.json"
EXPECTED_CANONICAL_PACKET_SHA256 = "96ce6b5d2752fb1ec514ef87f8ec48d4c09731d978b7a6d761719661e986e85b"
EXPECTED_SOURCE_SHA256 = "1c428f8c7e85197d50dcfe5c8b2c7546933dc2293874eabb321b1ab03343c77e"
EXPECTED_INVENTORY_SHA256 = "0d3db808c7319e32168be00e8756cf31e9686fe363419c6e671e1a7c0bc27418"
SOURCE_URL = "https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/"


def require(condition, why):
    if not condition:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def once(pattern, card, field):
    found = re.findall(pattern, card, flags=re.S)
    require(len(found) == 1, "missing/duplicate source field " + field)
    return html.unescape(found[0]).strip()


def validate(data, inventory_path=None):
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    require(digest(canonical) == EXPECTED_CANONICAL_PACKET_SHA256, "packet semantic digest mismatch")
    require(data["batch_id"] == "DIS.PPLUS.S1.SECOND5.20261103" and data["lane"] == "DISCOVERY", "wrong research partition")
    require(data["status"] == "PROPOSAL_ONLY", "premature admission")
    for field in (
        "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect",
        "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect",
        "artwork_publication_effect",
    ):
        require(data[field] == "NONE", "unauthorized effect " + field)
    require(data["audiovisual_episodes_watched"] is False and data["full_episode_text_read"] is False, "unearned close-read claim")
    source = data["source"]
    require(source["url"] == SOURCE_URL and source["response_status"] == 200, "wrong source URL/status")
    require(source["raw_html_bytes"] == 289669 and source["raw_html_sha256"] == EXPECTED_SOURCE_SHA256, "source-byte pin mismatch")
    require(source["independence_group"] == "publisher:paramountplus.com", "source lineage changed")
    require(source["publisher_signed_snapshot"] is False and source["original_html_committed"] is False, "false source custody")
    works, entities, evidence, claims, artwork = (data[k] for k in (
        "works", "local_entities", "evidence", "assertions", "artwork_candidates"
    ))
    require(all(len(items) == 5 for items in (works, entities, evidence, claims, artwork)), "exactly five separate cards required")
    ids = set()
    for idx, (work, entity, observation, claim, image) in enumerate(zip(works, entities, evidence, claims, artwork), start=6):
        work_id = f"dis-s1-e{idx:02d}-local"
        require(work["id"] == work_id and work["season"] == 1 and work["episode"] == idx, "episode-slot collision")
        require(work_id not in ids, "duplicate local Work")
        ids.add(work_id)
        require(work["canonical_work_id"] is None, "unreviewed global Work reconciliation")
        require(35 <= len(work["original_synopsis"]) <= 240, "short original paraphrase required")
        require(entity["work_id"] == work_id and entity["global_entity_id"] is None, "local-only entity")
        require(observation["source_id"] == source["id"] and observation["work_id"] == work_id, "source evidence mis-bound")
        require(observation["entity_ids"] == [entity["id"]], "evidence entity linkage")
        require(observation["kind"] == "PUBLISHER_DESCRIPTION" and observation["scope"] == "PUBLISHER_TEXT_ONLY", "publisher utterance promoted")
        require(claim["work_id"] == work_id and claim["evidence_id"] == observation["id"], "assertion evidence linkage")
        require(claim["predicate"] == "PUBLISHER_DESCRIBES" and claim["status"] == "UNVERIFIED_FICTIONAL_CONTENT", "false canonical claim")
        require(image["work_id"] == work_id and image["url"].startswith("https://thumbnails.cbsig.net/"), "image locator mismatch")
        require(image["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE" and image["bytes_downloaded"] is False and image["explorer_effect"] == "NONE", "artwork release attempted")
    require({item["kind"] for item in data["limits"]} == {
        "SINGLE_PUBLISHER_SOURCE", "NO_FULL_EPISODE", "UNVERIFIED_RELEASE_DATE_SEMANTICS"
    }, "required limitations absent")
    crosswalk = data["candidate_inventory_crosswalk"]
    require(crosswalk["scope"] == "DISCOVERY_ONLY_EPISODES_6_TO_10_TITLE_AND_SLOT_MATCH", "crosswalk scope")
    require(crosswalk["independent_content_witness"] is False and crosswalk["sha256"] == EXPECTED_INVENTORY_SHA256, "false independent witness")
    inventory_path = Path(inventory_path or ROOT / crosswalk["path"])
    raw = inventory_path.read_bytes()
    require(digest(raw) == EXPECTED_INVENTORY_SHA256, "accepted candidate inventory has drifted")
    inventory = json.loads(raw, object_pairs_hook=unique_object)["episode_slots"][5:10]
    require(len(inventory) == 5, "candidate roster incomplete")
    for idx, (work, candidate) in enumerate(zip(works, inventory), start=6):
        require(candidate["episode_number"] == idx and candidate["title"] == work["title"], "source candidate collision")
        require(candidate["canonical_work_id"] is None, "accepted roster already globally linked")
    return 5


def validate_private_source_html(data, raw_bytes):
    source = data["source"]
    require(len(raw_bytes) == source["raw_html_bytes"] and digest(raw_bytes) == EXPECTED_SOURCE_SHA256, "wrong exact publisher response")
    original = raw_bytes.decode("utf-8")
    require(original.count(f'<link rel="canonical" href="{SOURCE_URL}"/>') == 1, "canonical source URL missing")
    cards = re.split(r'<div class="episode">', original)[1:]
    require(len(cards) >= 10, "publisher cards absent")
    source_lines = original.splitlines()
    for work, image, card in zip(data["works"], data["artwork_candidates"], cards[5:10]):
        require(once(r'<h2>(.*?)</h2>', card, "title") == work["title"], "title bound to wrong card")
        require(once(r'<abbr class="seNum" title="Season (\d+)">', card, "season") == "1", "wrong season")
        require(int(once(r'<abbr class=\'epNum\' title="Episode (\d+)">', card, "slot")) == work["episode"], "wrong slot")
        require(once(r'<time[^>]*datetime="([^"]+)"', card, "time") == work["source_datetime"], "date mismatch")
        require(once(r'<a href="(/shows/video/[A-Za-z0-9_-]+/)"', card, "video") == work["video_path"], "video mismatch")
        require(once(r'<img src="([^"]+)"', card, "image") == image["url"], "art provenance mismatch")
        description = " ".join(once(r'<div class="ep__copy[^>]*>(.*?)</div>', card, "description").split())
        require(len(description) == work["publisher_description_length"], "description length changed")
        require(digest(description.encode("utf-8")) == work["publisher_description_sha256"], "description fingerprint mismatch")
        first, last = work["raw_html_card_lines"]
        require(0 < first <= last <= len(source_lines), "line locator out of source")
        located = "\n".join(source_lines[first - 1:last])
        require(work["title"] in html.unescape(located) and work["source_datetime"] in located and work["video_path"] in located, "own-card line locator mismatch")
    return 5


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-html", type=Path, help="Optional exact private source response; never commit.")
    args = parser.parse_args()
    data = json.loads(RECORDS.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    count = validate(data)
    if args.source_html:
        validate_private_source_html(data, args.source_html.read_bytes())
    print(f"DISCOVERY_S1_SECOND5_HELD_VALID: {count} source-local cards; no accepted Work, coverage, Explorer, artwork or reconciliation effects")


if __name__ == "__main__":
    main()
