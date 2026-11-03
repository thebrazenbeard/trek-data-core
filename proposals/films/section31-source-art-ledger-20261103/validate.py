"""Exact-pinned Section 31 publisher source sidecar; no index/artwork promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORD = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PRIOR = ROOT / "proposals/research/films/publisher-synopses-20261103/observations.json"
RECORD_SHA256 = "e891b460fb5900cae6a6d29d0de1f19b1de48f459281a625d9cb65a2e6624586"
ROW_SHA256 = {
    "section31-official-film-card": "ededd0606c59884a12570edc3ca1828b320c242598ee947f15d2ba3afcb3944e",
    "section31-official-trailer-poster-announcement": "a46f4a7b3d901bb7baaf8245198e994936b840f762b8e72eb39442e51925d478",
    "section31-paramountplus-stream-listing-index-only": "dbf5c000cc03fc092f5a4c1371c96898785cf99669e284cb1926a288d00b8288",
}
URLS = {
    "section31-official-film-card": "https://www.startrek.com/en-un/movies/star-trek-section-31",
    "section31-official-trailer-poster-announcement": "https://www.startrek.com/en-un/news/section-31-official-trailer-poster",
    "section31-paramountplus-stream-listing-index-only": "https://www.paramountplus.com/movies/video/hxLi_fyTiqdAOtq1_cSt2HXQuj9mkZJh/",
}
TOP = {
    "packet_id", "proposal_only", "role", "baseline_accepted_main", "observed_on_utc",
    "candidate_film_id", "candidate_title", "kind_as_publisher_described", "source_family",
    "source_independence", "accepted_overlap", "raw_source_page_sha256", "film_viewed",
    "source_work_binding_effect", "accepted_coverage_effect", "public_synopsis_release_effect",
    "artwork_publication_effect", "media_or_artwork_bytes_stored", "sources",
}


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def nodupes(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        check(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path: Path) -> dict:
    check(path.is_file() and not path.is_symlink(), "missing or symlinked file")
    check(path.stat().st_size < 25000, "oversized source records")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=nodupes)


def reviewed() -> dict:
    check(hashlib.sha256(RECORD.read_bytes()).hexdigest() == RECORD_SHA256,
          "unreviewed Section 31 source ledger bytes")
    return load(RECORD)


def validate(data: dict, discovery: dict, prior: dict) -> int:
    check(type(data) is dict and set(data) == TOP, "unexpected Section 31 source fields")
    fixed = {
        "packet_id": "FILMS-SECTION31-PUBLISHER-SOURCE-ART-20261103",
        "proposal_only": True,
        "role": "FILMS_SOURCE_LOCAL_RESEARCH",
        "baseline_accepted_main": "2070b0153228272b5dd667b0a23465ff49a95a5f",
        "observed_on_utc": "2026-11-03",
        "candidate_film_id": "film-section-31",
        "candidate_title": "Star Trek: Section 31",
        "kind_as_publisher_described": "ORIGINAL_STREAMING_MOVIE_NOT_THEATRICAL_RELEASE_ASSERTION",
        "source_family": "publisher:startrek.com and paramountplus.com corporate lineage",
        "source_independence": "StarTrek.com, CBS Studios and Paramount+ are related publisher/distributor sources; not independent film witnesses",
        "accepted_overlap": "Accepted publisher-synopses-20261103 already has a Section 31 StarTrek.com synopsis candidate and premiere announcement locator; this adds source-local production credit, poster and streaming-runtime-access distinctions, not a second independent synopsis or new Work",
        "raw_source_page_sha256": None,
        "film_viewed": False,
        "source_work_binding_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "artwork_publication_effect": "NONE",
        "media_or_artwork_bytes_stored": False,
    }
    for key, value in fixed.items():
        check(type(data[key]) is type(value) and data[key] == value,
              "boundary changed: " + key)
    check(any(r.get("id") == "film-section-31" and r.get("work_type") == "STREAMING_ORIGINAL_FILM"
              for r in discovery.get("films", [])), "accepted streaming film discovery missing")
    check(any(r.get("candidate_film_id") == "film-section-31"
              for r in prior.get("records", [])), "prior accepted Section 31 synopsis overlap missing")
    sources = data["sources"]
    check(type(sources) is list and len(sources) == 3, "wrong source evidence row count")
    seen: set[str] = set()
    for row in sources:
        check(type(row) is dict, "invalid row")
        source_id = row.get("local_source_id")
        check(type(source_id) is str and source_id in URLS and source_id not in seen,
              "unknown or duplicate Section 31 source")
        seen.add(source_id)
        check(row.get("locator") == URLS[source_id], "source URL substitution")
        digest = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":"),
                                           ensure_ascii=False).encode()).hexdigest()
        check(digest == ROW_SHA256[source_id], "unreviewed source row assertion")
        check(type(row.get("withheld_fields")) is list and len(row["withheld_fields"]) >= 3,
              "withheld rights or film-copy boundaries removed")
        check(row.get("poster_status", "").startswith(("HELD_", "NO_ARTWORK_")),
              "image license or binary promoted")
        if source_id.endswith("index-only"):
            check(row.get("source_observed_fields") == [] and
                  row.get("runtime_minutes_verified_directly") is None and
                  "DIRECT_WEB_OPEN_REPORTED_404" in row.get("reader_receipt", ""),
                  "indexed streaming listing promoted to directly read film runtime")
        else:
            check(type(row.get("source_observed_fields")) is list and
                  len(row["source_observed_fields"]) >= 4 and
                  "NO_RAW_HTML_HASH" in row.get("reader_receipt", ""),
                  "uncaptured webpage overstated")
    check(seen == set(URLS), "missing source row")
    return len(sources)


def main() -> None:
    n = validate(reviewed(), load(DISCOVERY), load(PRIOR))
    print(f"PASS: Section 31 {n} exact source-local rows; 2 rendered first-party pages, 1 index-only blocked listing; 0 coverage")


if __name__ == "__main__":
    main()
