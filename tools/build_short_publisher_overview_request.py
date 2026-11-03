#!/usr/bin/env python3
"""Prepare exact 14-item SHORT_FORM publisher overview review request, no public release.

All candidate prose was already recorded in accepted source-relative research.
One Very Short Trek has only a slogan: keep its plot synopsis explicitly null.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = Path("explorer/discovery-catalog.json")
SHORT = Path("proposals/research/short/publisher-synopses-20261103/observations.json")
VERY = Path("proposals/research/short/very-short-treks-descriptions-20261103/observations.json")
OUTPUT = Path("proposals/publication/short-publisher-overviews-20261103/review-request.json")
EXPECTED_SHORT_IDS = [f"short:short-treks-{n:02d}" for n in range(1, 11)]
EXPECTED_VERY_IDS = [f"short:very-short-treks-{n:02d}" for n in range(1, 6)]
HELD_ID = "short:very-short-treks-04"


def read(path: Path) -> tuple[dict, bytes]:
    target = ROOT / path
    if not target.is_file() or target.is_symlink() or target.stat().st_size > 3000000:
        raise ValueError(f"unavailable or untrusted source: {path}")
    raw = target.read_bytes()
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate source JSON key {key}")
            result[key] = value
        return result
    parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates)
    if not isinstance(parsed, dict):
        raise ValueError("expected JSON object")
    return parsed, raw


def build() -> dict:
    directory, raw_directory = read(DIR)
    short, raw_short = read(SHORT)
    very, raw_very = read(VERY)
    rows = {row["row_id"]: row for row in directory["rows"]}
    if directory["row_count"] != 1214 or len(rows) != 1214:
        raise ValueError("not accepted exact source-local directory")
    if (short.get("short_count") != 10 or short.get("observed_on_utc") != "2026-11-03" or
        short.get("raw_source_page_sha256") is not None or short.get("full_short_viewed") is not False or
        short.get("public_synopsis_release_effect") != "NONE" or
        short.get("source_guide") != "https://www.paramountplus.com/shows/star-trek-short-treks/episodes/" or
        len(short.get("description_paraphrases", [])) != 10):
        raise ValueError("unadmitted short publisher observation source changed")
    if (very.get("short_count") != 5 or very.get("observed_on_utc") != "2026-11-03" or
        very.get("raw_source_page_sha256") is not None or very.get("animated_shorts_viewed") is not False or
        very.get("public_synopsis_release_effect") != "NONE" or
        very.get("qualified_premises") != 4 or very.get("plot_synopsis_pending") != 1 or
        len(very.get("description_paraphrases", [])) != 5):
        raise ValueError("unadmitted Very Short publisher observation source changed")
    short_ids = [obs["directory_row_id"] for obs in short["description_paraphrases"]]
    very_ids = [obs["directory_row_id"] for obs in very["description_paraphrases"]]
    if short_ids != EXPECTED_SHORT_IDS or very_ids != EXPECTED_VERY_IDS:
        raise ValueError("unexpected source-relative directory candidate IDs")
    entries = []
    for bucket, observations, source_path, raw in [
        ("SHORT_TREKS", short["description_paraphrases"], SHORT, raw_short),
        ("VERY_SHORT_TREKS", very["description_paraphrases"], VERY, raw_very),
    ]:
        for obs in observations:
            ident = obs["directory_row_id"]
            row = rows[ident]
            if (row["medium"] != "SHORT_FORM" or row["candidate_kind"] not in {"SCRIPTED_SHORT", "PROMOTIONAL_ANIMATION"}
                    or row["title"] != (obs["title"] if bucket == "SHORT_TREKS" else obs["directory_title"])
                    or row["source_group"] != "publisher:paramount" or
                    row["source_input"] != "proposals/discovery/shorts-audio-20261102/records.json" or
                    row["admission_effect"] != "NONE" or row["coverage_effect"] != "NONE" or
                    row["verification_status"] != "UNVERIFIED_METADATA"):
                raise ValueError(f"unrecognized/changed publisher directory row {ident}")
            source_url = short["source_guide"] if bucket == "SHORT_TREKS" else obs["publisher_video_locator"]
            if bucket == "SHORT_TREKS":
                if row["source_locator"] != source_url or not obs["guide_description_locator"].startswith("Episode Guide > "):
                    raise ValueError("Short Trek synopsis lacks same official guide/card evidence")
                if obs["description_class"] != "PUBLISHER_DESCRIPTION_PARAPHRASE":
                    raise ValueError("unexpected Short Trek promotional summary class")
                section = obs["guide_description_locator"]
                source_title = obs["publisher_announcement_title"]
                variation = "NONE"
            else:
                if (row["source_locator"] != very["publisher_launch_source"] or
                    not source_url.startswith("https://www.startrek.com/videos/very-short-treks-") or
                    not obs["source_section"].startswith("Video page > ")):
                    raise ValueError("Very Short Trek lacks distinct official video evidence page")
                section = obs["source_section"]
                source_title = obs["publisher_video_title"]
                variation = obs["publisher_title_variation"]
            if ident == HELD_ID:
                if bucket != "VERY_SHORT_TREKS" or obs["synopsis"] is not None or \
                        obs["description_class"] != "PUBLISHER_TOPIC_ONLY_PENDING_PLOT_SYNOPSIS":
                    raise ValueError("premise-free Very Short candidate was silently promoted")
                continue
            synopsis = obs["synopsis"]
            if (not isinstance(synopsis, str) or not 45 <= len(synopsis) <= 350 or
                    not synopsis.endswith(".") or "\n" in synopsis or "<" in synopsis):
                raise ValueError("invalid bounded original publisher-description paraphrase")
            if bucket == "VERY_SHORT_TREKS" and obs["description_class"] != "PUBLISHER_PREMISE_PARAPHRASE":
                raise ValueError("unapproved Very Short premise class")
            entries.append({
                "row_id": "directory:" + ident,
                "source_local_row_id": ident,
                "title": row["title"],
                "medium": "SHORT_FORM",
                "source_group": row["source_group"],
                "source_input": row["source_input"],
                "source_context": row["context"],
                "source_locator": row["source_locator"],
                "overview_evidence_locator": source_url,
                "overview_evidence_section": section,
                "observed_publisher_title": source_title,
                "title_variation": variation,
                "overview_text": synopsis,
                "overview_basis": "PUBLISHER_DESCRIPTION_PARAPHRASE",
                "source_snapshot_date": "2026-11-03",
                "research_observation_path": source_path.as_posix(),
                "research_observation_sha256": hashlib.sha256(raw).hexdigest(),
                "original_paraphrase_sha256": hashlib.sha256(synopsis.encode("utf-8")).hexdigest(),
                "raw_webpage_sha256": None,
                "full_video_viewed": False,
                "admission_effect": "NONE",
                "coverage_effect": "NONE",
            })
    if len(entries) != 14 or len({r["row_id"] for r in entries}) != 14:
        raise ValueError("expected exactly 10 Short + 4 Very Short publisher reviews")
    return {
        "schema_version": "1.0.0",
        "data_status": "PUBLISHER_PROMOTIONAL_PARAPHRASE_EDITORIAL_REVIEW_REQUEST_ONLY",
        "source_directory_sha256": hashlib.sha256(raw_directory).hexdigest(),
        "source_observations": [
            {"path": SHORT.as_posix(), "sha256": hashlib.sha256(raw_short).hexdigest()},
            {"path": VERY.as_posix(), "sha256": hashlib.sha256(raw_very).hexdigest()},
        ],
        "reviewed_publisher_promotional_candidates": len(entries),
        "held_premise_free_row_id": "directory:" + HELD_ID,
        "raw_webpage_sha256": None,
        "full_shorts_viewed": False,
        "accepted_works_or_evidence": 0,
        "public_release_effect": "NONE",
        "coverage_effect": "NONE",
        "admission_effect": "NONE",
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    doc = build()
    encoded = (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    target = ROOT / OUTPUT
    if args.check:
        if not target.is_file() or target.is_symlink() or target.read_bytes() != encoded:
            raise SystemExit("SHORT_PUBLISHER_OVERVIEW_REVIEW_REQUEST_STALE")
    else:
        if target.is_symlink():
            raise SystemExit("SHORT_PUBLISHER_REQUEST_SYMLINK_REFUSED")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    print("SHORT_OVERVIEW_EDITORIAL_REQUEST_OK: 10 Short Treks + 4 Very Short Treks, "
          "one null plot held, 0 full views, 0 public overviews released")


if __name__ == "__main__":
    main()
