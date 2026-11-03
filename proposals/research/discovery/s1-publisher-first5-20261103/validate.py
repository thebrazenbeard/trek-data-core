"""Content-pinned, source-local Discovery publisher-card proposal validator.

No HTML/AV/image bytes are committed. `--source-html` is an optional private
receipt replay that rechecks the already retrieved exact publisher response.
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
EXPECTED_CANONICAL_PACKET_SHA256 = "92c56af204e0b84eb526d5f4bfc9c65f75f9595e2690418019a2c80c994a2379"
EXPECTED_SOURCE_SHA256 = "5589af123ae4636424d4e364beea3289a1c34656420c5d2c42d658e5717951ec"
EXPECTED_EXISTING_INVENTORY_SHA256 = "0d3db808c7319e32168be00e8756cf31e9686fe363419c6e671e1a7c0bc27418"
SOURCE_URL = "https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def require(condition, why):
    if not condition:
        raise ValueError(why)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def validate(data, inventory_path=None):
    # The author-written synopsis and each source-relative observation are
    # semantically security-critical. A structural shape/length test alone
    # would accept a false canon or public-domain assertion with valid flags.
    digest = sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    require(digest == EXPECTED_CANONICAL_PACKET_SHA256, "reviewed packet semantic digest mismatch")
    require(data["batch_id"] == "DIS.PPLUS.S1.FIRST5.20261103" and data["lane"] == "DISCOVERY", "wrong partition")
    require(data["status"] == "PROPOSAL_ONLY", "not admitted")
    for field in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect", "reconciliation_effect", "explorer_synopsis_release_effect", "artwork_publication_effect"):
        require(data[field] == "NONE", "unreviewed effect: " + field)
    require(data["audiovisual_episodes_watched"] is False and data["full_episode_text_read"] is False, "unearned close read")
    source = data["source"]
    require(source["url"] == SOURCE_URL and source["response_status"] == 200, "publisher source")
    require(source["raw_html_bytes"] == 289705 and source["raw_html_sha256"] == EXPECTED_SOURCE_SHA256, "publisher raw receipt")
    require(source["independence_group"] == "publisher:paramountplus.com", "source independence")
    require(source["publisher_signed_snapshot"] is False and source["original_html_committed"] is False, "false custody")

    works, entities, evidence, assertions, art = (data[k] for k in ("works", "local_entities", "evidence", "assertions", "artwork_candidates"))
    require(all(len(x) == 5 for x in (works, entities, evidence, assertions, art)), "exact five-card cohort")
    for i, (work, entity, record, claim, image) in enumerate(zip(works, entities, evidence, assertions, art), 1):
        work_id = f"dis-s1-e{i:02d}-local"
        require(work["id"] == work_id and work["season"] == 1 and work["episode"] == i, "episode order")
        require(work["canonical_work_id"] is None, "Work reconciliation")
        require(isinstance(work["original_synopsis"], str) and 35 <= len(work["original_synopsis"]) <= 240, "synopsis scope")
        require(entity["work_id"] == work_id and entity["global_entity_id"] is None, "local entity")
        require(record["work_id"] == work_id and record["source_id"] == source["id"], "source-bound evidence")
        require(record["entity_ids"] == [entity["id"]] and record["kind"] == "PUBLISHER_DESCRIPTION" and record["scope"] == "PUBLISHER_TEXT_ONLY", "evidence scope")
        require(claim["work_id"] == work_id and claim["evidence_id"] == record["id"], "claim cross-work evidence")
        require(claim["predicate"] == "PUBLISHER_DESCRIBES" and claim["status"] == "UNVERIFIED_FICTIONAL_CONTENT", "canon promotion")
        require(image["work_id"] == work_id and image["url"].startswith("https://thumbnails.cbsig.net/"), "publisher image source")
        require(image["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE" and image["bytes_downloaded"] is False and image["explorer_effect"] == "NONE", "image rights escalation")
    require({limit["kind"] for limit in data["limits"]} == {"SINGLE_PUBLISHER_SOURCE", "NO_FULL_EPISODE", "UNVERIFIED_RELEASE_DATE_SEMANTICS"}, "source limitations missing")

    inventory = data["candidate_inventory_crosswalk"]
    require(inventory["scope"] == "DISCOVERY_ONLY_FIRST_FIVE_TITLE_AND_SLOT_MATCH" and inventory["independent_content_witness"] is False, "false crosswalk confirmation")
    require(inventory["sha256"] == EXPECTED_EXISTING_INVENTORY_SHA256, "inventory pin")
    if inventory_path is None:
        inventory_path = ROOT / inventory["path"]
    raw = Path(inventory_path).read_bytes()
    require(sha256(raw) == EXPECTED_EXISTING_INVENTORY_SHA256, "accepted candidate inventory bytes changed")
    listed = json.loads(raw, object_pairs_hook=unique_object)["episode_slots"][:5]
    for i, (work, listed_work) in enumerate(zip(works, listed), 1):
        require(listed_work["episode_number"] == i and listed_work["title"] == work["title"] and listed_work["canonical_work_id"] is None, "catalog crosswalk mismatch")
    return 5


def once(pattern, card, field):
    values = re.findall(pattern, card, flags=re.S)
    require(len(values) == 1, "missing/duplicate card field: " + field)
    return html.unescape(values[0]).strip()


def validate_private_source_html(data, raw_bytes):
    source = data["source"]
    require(len(raw_bytes) == source["raw_html_bytes"] and sha256(raw_bytes) == EXPECTED_SOURCE_SHA256, "raw publisher HTML receipt mismatch")
    original = raw_bytes.decode("utf-8")
    require(original.count(f'<link rel="canonical" href="{SOURCE_URL}"/>') == 1, "publisher canonical URL binding")
    cards = re.split(r'<div class="episode">', original)[1:]
    require(len(cards) >= 5, "missing five publisher cards")
    lines = original.splitlines()
    for work, image, card in zip(data["works"], data["artwork_candidates"], cards):
        require(once(r'<h2>(.*?)</h2>', card, "title") == work["title"], "publisher own-card title")
        require(once(r'<abbr class="seNum" title="Season (\d+)">', card, "season") == "1", "publisher own-card season")
        require(int(once(r'<abbr class=\'epNum\' title="Episode (\d+)">', card, "episode")) == work["episode"], "publisher own-card number")
        require(once(r'<time[^>]*datetime="([^"]+)"', card, "datetime") == work["source_datetime"], "publisher own-card datetime")
        require(once(r'<a href="(/shows/video/[A-Za-z0-9_-]+/)"', card, "video") == work["video_path"], "publisher own-card video")
        require(once(r'<img src="([^"]+)"', card, "image") == image["url"], "publisher own-card art")
        publisher_copy = once(r'<div class="ep__copy[^>]*>(.*?)</div>', card, "description")
        publisher_copy = " ".join(publisher_copy.split())
        require(len(publisher_copy) == work["publisher_description_length"] and sha256(publisher_copy.encode("utf-8")) == work["publisher_description_sha256"], "publisher own-card description digest")
        start, end = work["raw_html_card_lines"]
        require(0 < start <= end <= len(lines), "source line locator outside body")
        window = "\n".join(lines[start - 1:end])
        require(work["title"].replace("'", "'") in html.unescape(window) and work["source_datetime"] in window and work["video_path"] in window, "source line/card association")
    return 5


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-html", type=Path, help="optional private raw publisher HTML response; never commit it")
    args = parser.parse_args()
    data = json.loads(RECORDS.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    count = validate(data)
    if args.source_html:
        validate_private_source_html(data, args.source_html.read_bytes())
    print(f"DISCOVERY_S1_PUBLISHER_HELD_VALID: {count} publisher cards; zero Work/coverage/Explorer/artwork release effects")


if __name__ == "__main__":
    main()
