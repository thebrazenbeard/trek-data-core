#!/usr/bin/env python3
"""Rebuild a public, source-local index of accepted Paramount film-page metadata.

This projects factual publisher listing fields only. It does not read films,
admit Works, publish synopsis paraphrases, or release poster image assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("explorer/paramount-film-rechecks.json")
INPUTS = (
    ("PARAMOUNT-FIRST-SIX", Path("proposals/films/paramount-six-source-pages-20261103/records.json"), 6, "RECORD_SHA256"),
    ("PARAMOUNT-SECOND-SIX", Path("proposals/films/paramount-second-six-pages-20261103/records.json"), 6, "RECORD_SHA256"),
    ("PARAMOUNT-BEYOND", Path("proposals/films/beyond-paramount-metadata-20261103/records.json"), 1, "PINNED_BYTES_SHA256"),
)
EXPECTED_IDS = frozenset({
    "film-motion-picture", "film-wrath-of-khan", "film-generations", "film-first-contact",
    "film-2009", "film-into-darkness", "film-search-for-spock", "film-voyage-home",
    "film-final-frontier", "film-undiscovered-country", "film-insurrection",
    "film-nemesis", "film-beyond",
})
ANOMALIES = {
    "film-first-contact", "film-search-for-spock", "film-insurrection",
}
HELD_PUBLISHER_YEAR_DISPUTES = {
    # Preserve the publisher-page observation and the disagreement verbatim;
    # neither a corrected release year nor an identity decision is inferred here.
    "film-search-for-spock": (
        1984,
        "PARAMOUNT_YEAR_1984_DIFFERS_FROM_STARTREK_COM_YEAR_1982; AFI_CATALOG_LISTS_1984; NOT_RECONCILED",
    ),
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    output: dict = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"Duplicate JSON key in official source: {key!r}")
        output[key] = value
    return output


def read_reviewed(path: Path, pin_name: str) -> tuple[dict, bytes, str]:
    target = ROOT / path
    validator = target.with_name("validate.py")
    for candidate in (target, validator):
        if not candidate.is_file() or candidate.is_symlink() or candidate.stat().st_size > 100_000:
            raise ValueError(f"Unavailable, symlinked or oversized accepted source/validator: {path}")
    # The existing, accepted source reviewer owns each exact complete packet pin.
    namespace = runpy.run_path(str(validator))
    pinned = namespace.get(pin_name)
    raw = target.read_bytes()
    if not isinstance(pinned, str) or not re.fullmatch(r"[a-f0-9]{64}", pinned) or sha(raw) != pinned:
        raise ValueError(f"Unreviewed official film-page source bytes: {path}")
    validator_result = subprocess.run([sys.executable, str(validator)], cwd=ROOT,
                                      capture_output=True, text=True, timeout=30, check=False)
    if validator_result.returncode:
        raise ValueError(f"Accepted official film source validator rejected {path}: "
                         f"{(validator_result.stderr or validator_result.stdout).strip()[:250]}")
    data = json.loads(raw, object_pairs_hook=no_duplicates)
    if not isinstance(data, dict):
        raise ValueError(f"Accepted source must be an object: {path}")
    return data, raw, pinned


def source_url(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("Official publisher URL missing")
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.netloc != "www.paramount.com" or
            parts.username or parts.password or parts.query or parts.fragment or
            not re.fullmatch(r"/movies/[a-z0-9-]+", parts.path)):
        raise ValueError(f"Publisher page URL escaped exact Paramount host: {url}")
    return parts.path.removeprefix("/movies/")


def build() -> dict:
    rows, receipts, seen = [], [], set()
    for batch, path, expected_count, pin_name in INPUTS:
        data, raw, pinned = read_reviewed(path, pin_name)
        receipts.append({"path": path.as_posix(), "sha256": pinned})
        if batch == "PARAMOUNT-BEYOND":
            if (data.get("source_group") != "publisher:paramount.com" or
                    data.get("film_viewed") is not False or data.get("image_bytes_fetched") is not False or
                    data.get("public_synopsis_release_effect") != "NONE" or
                    data.get("artwork_release_effect") != "NONE" or
                    data.get("accepted_coverage_effect") != "NONE" or
                    data.get("accepted_source_work_binding_effect") != "NONE"):
                raise ValueError("Beyond source custody/rights drift")
            source_rows = [data["observation"]]
        else:
            if (data.get("source_family") != "publisher:paramount.com" or
                    data.get("full_film_viewed") is not False or data.get("poster_bytes_stored") is not False or
                    data.get("public_synopsis_release_effect") != "NONE" or
                    data.get("public_artwork_release_effect") != "NONE" or
                    data.get("accepted_coverage_effect") != "NONE" or
                    data.get("accepted_source_work_binding_effect") != "NONE"):
                raise ValueError("Paramount source custody/rights drift")
            source_rows = data["records"]
        if len(source_rows) != expected_count:
            raise ValueError(f"Source batch cardinality drift: {batch}")
        for item in source_rows:
            ident = data["candidate_film_id"] if batch == "PARAMOUNT-BEYOND" else item["candidate_film_id"]
            url = data["source_locator"] if batch == "PARAMOUNT-BEYOND" else item["source_locator"]
            slug = source_url(url)
            if ident not in EXPECTED_IDS or ident in seen:
                raise ValueError(f"Duplicate or unknown local film candidate: {ident}")
            seen.add(ident)
            if batch == "PARAMOUNT-BEYOND":
                year, rating, minutes, genre = (item["source_year"], item["rating"],
                                                item["running_time_as_listed_minutes"], item["genre_as_listed"])
                directors, cast = [item["director_as_listed"]], [v["performer"] for v in item["cast_as_listed"]]
                anomaly = None
            else:
                year, rating, minutes, genre = (item["year_as_listed"], item["rating_as_listed"],
                                                item["runtime_as_listed_minutes"], item["genre_as_listed"])
                directors = [x["person"] for x in item["selected_creative_roles_as_listed"]
                             if x["credit"] == "Director"]
                cast = [v["performer"] for v in item["selected_cast_as_listed"]]
                anomaly = item["source_anomaly"]
            if (not isinstance(year, int) or not 1900 <= year <= 2100 or
                    not isinstance(minutes, int) or not 30 <= minutes <= 300 or
                    rating not in ("G", "PG", "PG-13", "R", "NR") or
                    not isinstance(genre, str) or len(genre) > 100 or
                    not directors or not cast or
                    any(not isinstance(name, str) or not 1 <= len(name) <= 100 for name in directors + cast)):
                raise ValueError(f"Invalid official film listing fields: {ident}")
            if (anomaly is not None) != (ident in ANOMALIES):
                raise ValueError(f"Official source anomaly was silently invented or suppressed: {ident}")
            disputed_year = HELD_PUBLISHER_YEAR_DISPUTES.get(ident)
            if disputed_year is not None and (year, anomaly) != disputed_year:
                raise ValueError(f"Disputed publisher-local film-year observation drift: {ident}")
            tags = sorted([
                "medium:film", "publisher:paramount.com", "batch:" + batch.lower(),
                "year:" + str(year), "rating:" + rating.lower(),
                "anomaly:held" if anomaly else "anomaly:none_documented",
            ])
            rows.append({
                "row_id": f"paramount-source-local:{ident}", "source_local_candidate_id": ident,
                "source_page_slug": slug, "source_locator": url,
                "source_batch": batch, "source_input": path.as_posix(), "source_input_sha256": pinned,
                "publisher_family": "publisher:paramount.com",
                "year_as_listed": year, "rating_as_listed": rating,
                "runtime_as_listed_minutes": minutes, "genre_as_listed": genre,
                "selected_directors_as_listed": directors, "selected_cast_performers_as_listed": cast,
                "source_anomaly": anomaly,
                "recheck_status": "HELD_UNRESOLVED_SOURCE_ANOMALY" if anomaly else "SOURCE_LOCAL_PAGE_METADATA_OBSERVED",
                "tags": tags,
                "source_snapshot_class": "RENDERED_PUBLISHER_PAGE_NO_RAW_HTML_OR_FILM_COPY",
                "film_viewed": False, "source_identity_scope": "SOURCE_LOCAL_CANDIDATE",
                "work_admission_effect": "NONE", "coverage_effect": "NONE",
                "synopsis_release_effect": "NONE", "artwork_release_effect": "NONE",
            })
    if seen != EXPECTED_IDS or len(rows) != 13:
        raise ValueError("Exact 13 source-local Paramount film-page observations drifted")
    rows.sort(key=lambda row: row["row_id"])
    return {
        "schema_version": "1.0.0",
        "data_status": "SOURCE_LOCAL_PARAMOUNT_FILM_PAGE_METADATA_ONLY",
        "row_count": 13, "source_anomaly_held_count": 3,
        "publisher_independence_group_count": 1, "distinct_works_admitted": 0,
        "full_films_viewed": 0, "synopses_released": 0, "artwork_released": 0,
        "coverage_effect": "NONE", "admission_effect": "NONE",
        "accepted_source_input_receipts": receipts, "rows": rows,
    }


def encode(data: dict) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = encode(build())
    target = ROOT / OUTPUT
    if target.is_symlink():
        raise SystemExit("PARAMOUNT_FILM_RECHECKS_SYMLINK_OUTPUT_REJECTED")
    if args.check:
        if not target.is_file() or target.read_bytes() != artifact:
            raise SystemExit("PARAMOUNT_FILM_RECHECKS_STALE_OR_TAMPERED")
    else:
        target.write_bytes(artifact)
    print("PARAMOUNT_FILM_RECHECKS_OK: 13 first-party source-local film-page metadata records;"
          " 3 held anomalies; 0 films viewed, Works, synopses or artwork released")


if __name__ == "__main__":
    main()
