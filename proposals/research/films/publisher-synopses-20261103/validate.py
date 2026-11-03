"""Deterministically validate film publisher-description observations, never film contents."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBSERVATIONS = HERE / "observations.json"
FILM_CATALOG = ROOT / "explorer/film-catalog.json"
PINNED_OBSERVATIONS_SHA256 = "e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read_pinned() -> dict:
    raw = OBSERVATIONS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINNED_OBSERVATIONS_SHA256,
            "film synopsis proposal bytes changed without independent review")
    return json.loads(raw)


EXPECTED = read_pinned()


def validate(data: dict, film_catalog: dict | None = None) -> int:
    require(isinstance(data, dict) and set(data) == set(EXPECTED), "unexpected proposal fields")
    for key, value in EXPECTED.items():
        require(type(data[key]) is type(value) and data[key] == value,
                f"unreviewed source synopsis mutation: {key}")

    require(data["schema_version"] == "trek-film-publisher-description-paraphrase-v1", "schema")
    require(data["proposal_only"] is True, "proposal must not be admitted")
    require(data["source_family"] == "publisher:startrek.com" and data["upstream_source_families"] == 1,
            "publisher lineage is not independent per film")
    require(data["source_access"] == "RENDERED_OFFICIAL_WEB_PAGE_READ_NO_RAW_HTML_CUSTODY",
            "unqualified source acquisition")
    require(data["verification_class"] == "PUBLISHER_DESCRIPTION_FIELD_READ_NOT_FILM_VIEWED",
            "unqualified source reading")
    for key in ("accepted_source_work_binding_effect", "accepted_evidence_effect", "accepted_coverage_effect",
                "public_synopsis_release_effect", "artwork_release_effect"):
        require(data[key] == "NONE", f"protected effect {key}")
    for key in ("full_film_viewed", "source_bound", "close_read"):
        require(data[key] is False, f"unsupported full film source claim: {key}")
    require(data["raw_source_page_sha256"] is None, "no raw page bytes held for source checksum")

    film_catalog = film_catalog if film_catalog is not None else json.loads(FILM_CATALOG.read_text(encoding="utf-8"))
    require(film_catalog.get("data_status") == "DISCOVERY_ONLY", "film candidate catalog status changed")
    source_rows = film_catalog.get("films")
    require(isinstance(source_rows, list) and len(source_rows) == 14, "accepted film catalog drift")
    by_id = {r["id"]: r for r in source_rows}
    require(len(by_id) == 14, "duplicate film candidate identifiers")

    rows = data["records"]
    require(isinstance(rows, list) and len(rows) == data["film_count"] == 14,
            "all fourteen candidate film observations required")
    require(len({r["candidate_film_id"] for r in rows}) == 14, "duplicate film observation")
    for row in rows:
        require(set(row) == {"candidate_film_id", "directory_row_id", "title", "source_locator",
                             "source_section", "publisher_display_year", "status", "synopsis"},
                "unexpected film synopsis field")
        source = by_id.get(row["candidate_film_id"])
        require(source is not None, "candidate film identifier not in accepted directory")
        require(row["directory_row_id"] == "film:" + source["id"] and row["title"] == source["title"],
                "source-local film identity mismatch")
        require(row["source_locator"] == source["source_locator"] and source["source_group"] == "publisher:startrek.com",
                "publisher film locator mismatch")
        url = urlsplit(row["source_locator"])
        require(url.scheme == "https" and url.netloc == "www.startrek.com" and url.username is None
                and url.password is None and url.port is None and not url.query and not url.fragment,
                "forged publisher source host")
        require(row["source_section"] == ("Announcement paragraph beginning 'In the movie'"
                 if source["id"] == "film-section-31" else "Synopsis"),
                "publisher synopsis field locator mismatch")
        require(row["status"] == "PUBLISHER_DESCRIPTION_PARAPHRASE", "improper full-film synopsis promotion")
        require(isinstance(row["synopsis"], str) and 14 <= len(row["synopsis"].split()) <= 55
                and "\n" not in row["synopsis"] and "<" not in row["synopsis"],
                "missing, oversized, or unsafe original synopsis")
        require((row["publisher_display_year"] is None and source["id"] == "film-section-31") or
                (isinstance(row["publisher_display_year"], str) and
                 bool(re.fullmatch(r"(?:19|20)\d{2}", row["publisher_display_year"])) and
                 source["id"] != "film-section-31"),
                "publisher year must be only the observed page field, not a release verdict")

    conflict = data["source_year_conflict"]
    require(conflict == {
        "candidate_film_id": "film-search-for-spock",
        "publisher_page_displays": "1982",
        "independent_catalog_name": "AFI Catalog of Feature Films",
        "independent_catalog_locator": "https://catalog.afi.com/Film/57202-STAR-TREK-III-THE-SEARCH-FOR-SPOCK",
        "catalog_lists_release_date": "1984-06-01",
        "disposition": "UNRESOLVED_SOURCE_YEAR_CONTRADICTION_NOT_RECONCILED",
    }, "do not silently resolve or flatten the disputed Search for Spock year")
    require(next(r for r in rows if r["candidate_film_id"] == "film-search-for-spock")
            ["publisher_display_year"] == conflict["publisher_page_displays"],
            "1982 is a publisher-page observation, not accepted release metadata")
    return len(rows)


if __name__ == "__main__":
    print("FILM_PUBLISHER_DESCRIPTION_PROPOSAL_OK:", validate(read_pinned()))
