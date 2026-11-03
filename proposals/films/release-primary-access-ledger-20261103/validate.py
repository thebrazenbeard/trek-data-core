"""Fail-closed source-access sidecar; never promotes indexed snippets to source custody."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORD = HERE / "records.json"
DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"
PR329 = ROOT / "proposals/films/paramount-six-source-pages-20261103/records.json"
RECORD_SHA256 = "e917cc58494ba4d1a6e705f7ba250d0c49840f08e96895ec4213eb9498fb1ac7"
ROW_SHA256 = {
    "access-2009-itunes-publisher-html": "0029cd574a5e1a499b9e497638fe572804b2e0245e2351d9b3daa39c9f7b8cee",
    "access-2009-home-publisher-pdf": "c3099834f45c32961ff2874619fb74dd70259e4c121dc2c9625cd81b98f8d7db",
    "access-2013-star-trek-studio-story": "5f153c32c9fb5e93a4b0313939018773f167f03ce1d765e11cfa655244e5a97c",
    "access-2013-home-publisher-pdf": "55b6a2c29cfb136941a7485a5d1cd130cf2a0ae1527c87526edb41716791405d",
    "access-2013-home-publisher-html": "279977a61e8f8fd4b685a9d4b735ef352b5536fcec66d86b389d64c91424e1aa",
}
URLS = {
    "access-2009-itunes-publisher-html": "https://ir.paramount.com/news-releases/news-release-details/paramount-digital-entertainment-releases-never-seen-star-trek",
    "access-2009-home-publisher-pdf": "https://ir.paramount.com/static-files/21c8db87-fe44-48f0-be67-9fa3d6be0bc6",
    "access-2013-star-trek-studio-story": "https://www.startrek.com/news/first-look-star-trek-into-darkness-blu-ray-dvd-box-art",
    "access-2013-home-publisher-pdf": "https://ir.paramount.com/static-files/cf49d3ba-f408-4599-9180-d5141396e7e7",
    "access-2013-home-publisher-html": "https://ir.paramount.com/news-releases/news-release-details/director-jj-abrams-worldwide-blockbuster-sets-course-star-trek/",
}
TOP = {
    "packet_id", "proposal_only", "role", "baseline_accepted_main", "observed_on_utc",
    "purpose", "related_held_proposals", "source_independence", "accepted_film_page_overlap",
    "raw_upstream_page_sha256", "source_work_binding_effect", "accepted_coverage_effect",
    "public_synopsis_release_effect", "artwork_release_effect", "media_or_artwork_bytes_stored",
    "source_access_observations",
}


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def nodupes(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        check(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def load(path: Path) -> dict:
    check(path.is_file() and not path.is_symlink(), "missing or symlinked file")
    check(path.stat().st_size < 30_000, "oversized file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=nodupes)


def reviewed() -> dict:
    check(hashlib.sha256(RECORD.read_bytes()).hexdigest() == RECORD_SHA256, "unreviewed source access ledger bytes")
    return load(RECORD)


def validate(data: dict, discovery: dict, prior: dict) -> int:
    check(type(data) is dict and set(data) == TOP, "unreviewed top-level source fields")
    expected = {
        "packet_id": "FILMS-PRIMARY-RELEASE-SOURCE-ACCESS-20261103",
        "proposal_only": True,
        "role": "FILMS_SOURCE_ACCESS_AUDIT",
        "baseline_accepted_main": "a3ca40e94ef4c0a4ba47455333a0c122ded38c9a",
        "observed_on_utc": "2026-11-03",
        "purpose": "CANDIDATE_SOURCE_ACCESS_REMEDIATION_ONLY_NOT_NEW_FILM_FACT_COVERAGE",
        "related_held_proposals": [
            {"pr": 332, "head_at_review": "2f74b0c6777d980314f9b4a0786df63e41f577a0", "candidate_film_id": "film-2009"},
            {"pr": 325, "head_at_review": "d4315328935ed1079bd7543f423118be23e3982d", "candidate_film_id": "film-into-darkness"},
        ],
        "source_independence": "Paramount Pictures, Paramount Home Entertainment, Paramount Digital Entertainment and StarTrek.com are related corporate publisher lines, not independent audiovisual witnesses",
        "accepted_film_page_overlap": "Accepted Paramount film metadata packet #329 already covers film-2009 and film-into-darkness page years/runtimes and publisher synopsis candidates; this ledger adds no duplicate synopsis or film page metadata",
        "raw_upstream_page_sha256": None,
        "source_work_binding_effect": "NONE",
        "accepted_coverage_effect": "NONE",
        "public_synopsis_release_effect": "NONE",
        "artwork_release_effect": "NONE",
        "media_or_artwork_bytes_stored": False,
    }
    for field, value in expected.items():
        check(type(data[field]) is type(value) and data[field] == value, "boundary changed: " + field)
    check(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "accepted film discovery missing")
    check(prior.get("packet_id") == "FILMS-PARAMOUNT-SIX-SOURCE-PAGES-20261103", "accepted #329 packet missing")
    for film in ("film-2009", "film-into-darkness"):
        check(any(r.get("candidate_film_id") == film for r in prior.get("records", [])), "no accepted prior film metadata")
        check(any(r.get("id") == film and r.get("work_type") == "FEATURE_FILM"
                  for r in discovery.get("films", [])), "missing film discovery candidate")
    rows = data["source_access_observations"]
    check(type(rows) is list and len(rows) == 5, "wrong source access observation count")
    seen: set[str] = set()
    for row in rows:
        check(type(row) is dict, "invalid source access row")
        local_id = row.get("local_id")
        check(type(local_id) is str and local_id in URLS and local_id not in seen,
              "unknown or duplicate source observation")
        seen.add(local_id)
        check(row.get("source_locator") == URLS[local_id], "source locator substitution")
        check(row.get("candidate_film_id") == ("film-2009" if local_id.startswith("access-2009")
                                                    else "film-into-darkness"), "cross-film source swap")
        review = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        check(hashlib.sha256(review).hexdigest() == ROW_SHA256[local_id], "unreviewed source access assertion")
        held = row.get("withheld_fields")
        check(type(held) is list and held, "missing held source/rights boundaries")
        if row.get("access_class") == "DIRECT_FIRST_PARTY_HTML_READ":
            check(row.get("web_reader_status") == "RETRIEVED_CONTENT_READ" and
                  len(row.get("reliably_source_observed_fields", [])) > 0, "direct source read inflated")
        else:
            check(row.get("reliably_source_observed_fields") == [] and
                  row.get("web_reader_status") == "FETCH_FAILED_REPORTED_404", "index-only source promoted")
    check(seen == set(URLS), "missing source access row")
    return len(rows)


def main() -> None:
    n = validate(reviewed(), load(DISCOVERY), load(PR329))
    print(f"PASS: {n} exact source-access checks; 2 working first-party HTML, 3 direct fetch blocks; no coverage")


if __name__ == "__main__":
    main()
