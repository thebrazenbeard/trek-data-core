"""Fail-closed validator for five TOS Season 2 Paramount+ source-local cards.

Raw publisher HTML is retained outside this public repository. Supplying
``--source-html`` independently checks the exact captured private response;
without it, validation only covers the reviewed proposal and accepted catalog
crosswalk, not renewed publisher custody or a full-episode close read.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORDS = HERE / "records.json"
EXPECTED_PACKET_SHA256 = "636f83f9c7820e0e202f017faa1096e5a2b1e40c60727a6898615dbf1d577bd3"
EXPECTED_SOURCE_SHA256 = "617ea64c3408fc228151ef839c71ce5b9043614dc5e97b64b83fb8e0adffe1a6"
EXPECTED_INVENTORY_SHA256 = "b5cfe891190b5054b748c520d7640d520717b414a410e8d5cc923488ea61f466"
SOURCE_URL = "https://www.paramountplus.com/shows/star_trek/episodes/2/"


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_records(path: Path = RECORDS) -> dict:
    require(path.is_file() and not path.is_symlink(), "unsafe record path")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validate(data: dict, inventory_path: Path | None = None) -> int:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    require(sha256(canonical) == EXPECTED_PACKET_SHA256, "reviewed packet semantic digest mismatch")
    require(data["batch_id"] == "TOS.PPLUS.S2.FIRST5.20261103" and data["lane"] == "TOS", "wrong partition")
    require(data["status"] == "PROPOSAL_ONLY", "proposal status promoted")
    for field in (
        "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect",
        "reconciliation_effect", "explorer_synopsis_release_effect", "artwork_publication_effect",
    ):
        require(data[field] == "NONE", "unauthorized effect: " + field)
    require(data["audiovisual_episodes_watched"] is False and data["full_episode_text_read"] is False,
            "invented full-source access")

    source = data["source"]
    require(source["url"] == SOURCE_URL and source["kind"] == "FIRST_PARTY_PUBLISHER_EPISODE_GUIDE", "source URL/kind")
    require(source["response_status"] == 200, "publisher response status")
    require(source["raw_html_bytes"] == 308788 and source["raw_html_sha256"] == EXPECTED_SOURCE_SHA256,
            "raw source receipt changed")
    require(source["independence_group"] == "publisher:paramountplus.com", "publisher independence group")
    require(source["publisher_signed_snapshot"] is False and source["raw_source_bytes_in_public_repo"] is False,
            "false source custody")
    require(source["source_replay_availability"] == "HASH_AND_LOCATOR_ONLY_UNTIL_PRIVATE_RAW_HTML_SUPPLIED",
            "unsupported source replay status")

    works, entities, evidence, assertions, images = (data[name] for name in
        ("works", "local_entities", "evidence", "assertions", "artwork_candidates"))
    require(all(len(items) == 5 for items in (works, entities, evidence, assertions, images)), "exact five-row TOS tranche")

    inventory = data["candidate_inventory_crosswalk"]
    require(inventory["scope"] == "DISCOVERY_ONLY_FIRST_FIVE_TITLE_AND_SLOT_MATCH"
            and inventory["independent_content_witness"] is False,
            "crosswalk promoted to source corroboration")
    require(inventory["sha256"] == EXPECTED_INVENTORY_SHA256, "inventory digest declaration")
    path = inventory_path or ROOT / inventory["path"]
    require(path.is_file() and not path.is_symlink(), "inventory source missing or symlinked")
    require(sha256(path.read_bytes()) == EXPECTED_INVENTORY_SHA256, "accepted inventory changed")
    inventory_rows = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)["episode_slots"][:5]

    for ordinal, (work, entity, observed, claim, image, discovered) in enumerate(
        zip(works, entities, evidence, assertions, images, inventory_rows), 1
    ):
        work_id = f"tos-s2-e{ordinal:02d}-local"
        require(work["id"] == work_id and work["season"] == 2 and work["episode"] == ordinal, "TOS episode slot")
        require(discovered["season"] == 2 and discovered["episode_number"] == ordinal
                and discovered["title"] == work["title"]
                and discovered["canonical_work_id"] is None and discovered["source_binding_id"] is None,
                "unaccepted title/slot crosswalk changed")
        require(work["canonical_work_id"] is None, "global Work identity invented")
        require(isinstance(work["original_synopsis"], str) and 45 <= len(work["original_synopsis"]) <= 180,
                "original source-relative paraphrase missing")
        require(work["video_path"].startswith("/shows/video/") and work["video_path"].endswith("/"),
                "publisher video locator")
        require(entity["work_id"] == work_id and entity["global_entity_id"] is None,
                "global entity identity invented")
        require(observed["work_id"] == work_id and observed["source_id"] == source["id"]
                and observed["entity_ids"] == [entity["id"]] and observed["kind"] == "PUBLISHER_DESCRIPTION"
                and observed["scope"] == "PUBLISHER_TEXT_ONLY", "evidence scope promoted")
        require(claim["work_id"] == work_id and claim["evidence_id"] == observed["id"]
                and claim["predicate"] == "PUBLISHER_DESCRIBES"
                and claim["status"] == "UNVERIFIED_FICTIONAL_CONTENT", "fictional canon promotion")
        require(image["work_id"] == work_id and image["url"].startswith("https://thumbnails.cbsig.net/")
                and image["rights_status"] == "HELD_NO_PUBLIC_DISPLAY_LICENSE"
                and image["bytes_downloaded"] is False and image["explorer_effect"] == "NONE",
                "artwork publication or invented rights")
    require({row["kind"] for row in data["limits"]} == {
        "SINGLE_PUBLISHER_SOURCE", "NO_FULL_EPISODE", "UNVERIFIED_RELEASE_DATE_SEMANTICS",
        "UNRESOLVED_WORK_IDENTITY", "NO_PUBLIC_IMAGE_RIGHTS_ASSERTION",
    }, "required limitations missing")
    return 5


def once(pattern: str, card: str, name: str) -> str:
    values = re.findall(pattern, card, flags=re.S)
    require(len(values) == 1, "missing or duplicate source card field: " + name)
    return html.unescape(values[0]).strip()


def validate_private_source_html(data: dict, raw: bytes) -> int:
    source = data["source"]
    require(len(raw) == source["raw_html_bytes"] and sha256(raw) == EXPECTED_SOURCE_SHA256,
            "private raw publisher snapshot mismatch")
    original = raw.decode("utf-8")
    require(original.count(f'<link rel="canonical" href="{SOURCE_URL}"/>') == 1,
            "private publisher canonical URL mismatch")
    cards = re.split(r'<div class="episode">', original)[1:]
    require(len(cards) == 26, "season card count changed within pinned snapshot")
    lines = original.splitlines()
    for work, image, card in zip(data["works"], data["artwork_candidates"], cards):
        require(once(r"<h2>(.*?)</h2>", card, "title") == work["title"], "wrong episode title")
        require(int(once(r'<abbr class="seNum" title="Season (\d+)">', card, "season")) == 2,
                "wrong season")
        require(int(once(r"<abbr class='epNum' title=\"Episode (\d+)\">", card, "episode"))
                == work["episode"], "wrong episode ordinal")
        require(once(r'<time[^>]*datetime="([^"]+)"', card, "time") == work["source_datetime"],
                "publisher raw time changed")
        require(once(r'<a href="(/shows/video/[^\"]+)"', card, "video") == work["video_path"],
                "publisher video URL changed")
        require(once(r'<img src="([^"]+)"', card, "image") == image["url"],
                "publisher image URL changed")
        copy = " ".join(once(r'<div class="ep__copy[^>]*>(.*?)</div>', card, "description").split())
        require(len(copy) == work["publisher_description_length"]
                and sha256(copy.encode()) == work["publisher_description_sha256"],
                "publisher description fingerprint changed")
        line_no = work["raw_html_title_line"]
        require(0 < line_no <= len(lines)
                and f'<h2>{work["title"]}</h2>' in lines[line_no - 1],
                "raw HTML title locator mismatch")
    return 5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-html", type=Path, help="private publisher HTML replay; do not commit")
    args = parser.parse_args()
    data = read_records()
    count = validate(data)
    if args.source_html is not None:
        require(args.source_html.is_file() and not args.source_html.is_symlink(), "private raw source missing")
        validate_private_source_html(data, args.source_html.read_bytes())
    print(f"TOS_S2_HELD_VALID: {count} first-party publisher-guide cards; no source/Work/coverage/Explorer/artwork acceptance")


if __name__ == "__main__":
    main()
