"""Validate seven unadmitted film artwork locators without authorizing media reuse."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
from urllib.parse import urlsplit


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = HERE / "records.json"
FILM_DISCOVERY = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"

ALLOWED_PUBLISHER_PATHS = {
    "/movies/star-trek-i-the-motion-picture": "film-motion-picture",
    "/movies/star-trek-iii-the-search-for-spock": "film-search-for-spock",
    "/movies/star-trek-iv-the-voyage-home": "film-voyage-home",
    "/gallery/search-for-spock-enterprise": "film-search-for-spock",
}
ALLOWED_INDEXED_CATEGORIES = {
    "/wiki/Category%3AMemory_Alpha_images_%28publicity%29": "film-motion-picture",
    "/wiki/Category%3AMemory_Alpha_files_by_production_%28Star_Trek_III%3A_The_Search_for_Spock%29": "film-search-for-spock",
    "/nl/wiki/Categorie%3AFilms_-_004_-_The_Voyage_Home": "film-voyage-home",
}


def ensure(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def keys(obj: dict, expected: set[str], label: str) -> None:
    ensure(isinstance(obj, dict) and set(obj) == expected, f"{label}: unexpected or missing keys")


def validate(proposal: dict, film_bundle: dict) -> int:
    keys(proposal, {
        "proposal_id", "proposal_only", "role", "baseline_accepted_main", "observation_date_utc",
        "coverage_effect", "admission_effect", "public_artwork_release_effect",
        "source_page_snapshots_available", "source_lineage", "records",
    }, "proposal")
    ensure(proposal["proposal_id"] == "FILMS-ARTWORK-SOURCE-LOCATORS-20261103", "wrong proposal ID")
    ensure(proposal["role"] == "FILMS", "wrong worker role")
    ensure(proposal["proposal_only"] is True, "must remain proposal-only")
    for status in ("coverage_effect", "admission_effect", "public_artwork_release_effect"):
        ensure(proposal[status] == "NONE", f"{status} must remain NONE")
    ensure(proposal["source_page_snapshots_available"] is False, "unsupported source snapshot claim")
    ensure(isinstance(proposal["baseline_accepted_main"], str) and
           re.fullmatch(r"[0-9a-f]{40}", proposal["baseline_accepted_main"]) is not None, "bad baseline identity")
    try:
        dt.date.fromisoformat(proposal["observation_date_utc"])
    except (ValueError, TypeError) as exc:
        raise ValueError("bad observation date") from exc
    keys(proposal["source_lineage"], {"publisher:startrek.com", "community:memory-alpha.fandom.com"}, "source_lineage")
    ensure(all(isinstance(s, str) and len(s) >= 35 for s in proposal["source_lineage"].values()), "insufficient lineage notes")

    ensure(film_bundle.get("proposal_type") == "FILM_DISCOVERY_METADATA", "missing film discovery manifest")
    film_ids = {film["id"] for film in film_bundle["films"]}
    records = proposal["records"]
    ensure(isinstance(records, list) and len(records) == 7, "expected seven artwork-source leads")
    ids: set[str] = set()
    file_labels: set[str] = set()
    source_groups = set()
    for i, item in enumerate(records):
        label = f"record {i}"
        keys(item, {
            "local_id", "candidate_film_id", "source_group", "source_locator", "access",
            "artwork_kind", "evidence", "evidence_scope", "artwork_variant", "rights_status",
            "display_eligible",
        }, label)
        local_id = item["local_id"]
        ensure(isinstance(local_id, str) and re.fullmatch(r"films-artwork-[a-z0-9-]{6,90}", local_id) is not None,
               f"{label}: invalid local ID")
        ensure(local_id not in ids, f"{label}: duplicate local ID")
        ids.add(local_id)
        ensure(item["candidate_film_id"] in film_ids, f"{label}: unknown film discovery candidate")
        ensure(item["rights_status"] == "PUBLIC_REUSE_NOT_VERIFIED", f"{label}: rights gate bypass")
        ensure(item["display_eligible"] is False, f"{label}: unauthorized image display")
        ensure(isinstance(item["artwork_variant"], str) and
               re.fullmatch(r"[A-Z0-9_]{12,100}", item["artwork_variant"]) is not None,
               f"{label}: missing version/edition distinction")
        url = urlsplit(item["source_locator"])
        ensure(url.scheme == "https" and not any((url.username, url.password, url.port, url.query, url.fragment)),
               f"{label}: unsafe source locator")
        evidence = item["evidence"]
        ensure(isinstance(evidence, str) and 9 <= len(evidence) <= 110, f"{label}: invalid observation")
        group = item["source_group"]
        source_groups.add(group)
        if group == "publisher:startrek.com":
            ensure(url.hostname == "www.startrek.com" and url.path in ALLOWED_PUBLISHER_PATHS,
                   f"{label}: unverified publisher path")
            ensure(item["candidate_film_id"] == ALLOWED_PUBLISHER_PATHS[url.path],
                   f"{label}: source linked to wrong film")
            ensure(item["access"] == "PUBLISHER_PAGE_READ", f"{label}: wrong acquisition class")
            if url.path.startswith("/movies/"):
                ensure(item["artwork_kind"] == "PUBLISHER_POSTER_LABEL" and
                       item["evidence_scope"] == "PUBLISHER_PAGE_IMAGE_ALT_TEXT" and
                       evidence.lower().startswith("poster art for star trek"),
                       f"{label}: poster label evidence does not match source")
            else:
                ensure(item["artwork_kind"] == "PUBLISHER_STILL_GALLERY_LISTING" and
                       item["evidence_scope"] == "PUBLISHER_GALLERY_HEADING" and
                       evidence == "11 Indelible Images from 'The Search for Spock'",
                       f"{label}: gallery evidence mismatch")
        elif group == "community:memory-alpha.fandom.com":
            ensure(url.hostname == "memory-alpha.fandom.com" and url.path in ALLOWED_INDEXED_CATEGORIES,
                   f"{label}: inaccessible/unsupported Fandom locator")
            ensure(item["candidate_film_id"] == ALLOWED_INDEXED_CATEGORIES[url.path],
                   f"{label}: indexed category mapped to wrong film")
            ensure(item["access"] == "SEARCH_INDEX_CACHED_NOT_DIRECT", f"{label}: Fandom direct-access claim forbidden")
            ensure(item["artwork_kind"] == "INDEXED_FILE_TITLE_ONLY" and
                   item["evidence_scope"] == "INDEXED_CATEGORY_FILE_LISTING" and
                   evidence.startswith(("File:", "Bestand:")),
                   f"{label}: not a source-local file-title observation")
            ensure(evidence not in file_labels, f"{label}: duplicate indexed file title")
            file_labels.add(evidence)
        else:
            raise ValueError(f"{label}: unsupported source group")
    ensure(source_groups == set(proposal["source_lineage"]), "unreferenced or absent source family")
    return len(records)


def main() -> None:
    proposal = json.loads(RECORDS.read_text(encoding="utf-8"))
    films = json.loads(FILM_DISCOVERY.read_text(encoding="utf-8"))
    n = validate(proposal, films)
    print(f"PASS: {n} source-local artwork leads, no images, no rights release, no corpus admission")


if __name__ == "__main__":
    main()
