#!/usr/bin/env python3
"""Fail-closed local custody validation for unlicensed official poster URLs.

This verifies exact previously inspected link/film bindings. It neither fetches
image bytes nor grants reuse rights or advances coverage/Work admission.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FILM_CATALOG = "explorer/film-catalog.json"
FILM_CATALOG_SHA256 = "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de"

# Separately pinned after direct reading of eight official StarTrek.com pages.
# Values are film directory ID, official page URL, exact poster-link URL, alt label.
PINS = {
    "film-poster-link-motion-picture-20261103": (
        "film-motion-picture", "https://www.startrek.com/movies/star-trek-i-the-motion-picture",
        "https://images.prismic.io/star-trek-untold/cb2d990c-985d-428a-a26e-b1ad8b77f2fe_ST1_ARTalt.png?auto=compress%2Cformat",
        "Poster Art for Star Trek: The Motion Picture"),
    "film-poster-link-search-for-spock-20261103": (
        "film-search-for-spock", "https://www.startrek.com/movies/star-trek-iii-the-search-for-spock",
        "https://images.prismic.io/star-trek-untold/9b27e9bd-03dc-4cfe-84ce-6c7857c2fc28_StarTrekIII_TheSearchForSpock_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek III: The Search for Spock"),
    "film-poster-link-voyage-home-20261103": (
        "film-voyage-home", "https://www.startrek.com/movies/star-trek-iv-the-voyage-home",
        "https://images.prismic.io/star-trek-untold/8b45139c-36aa-42ae-a12b-43ac1f8e7747_StarTrekIV_TheVoyageHomee_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster Art for Star Trek IV: The Voyage Home"),
    "film-poster-link-final-frontier-20261103": (
        "film-final-frontier", "https://www.startrek.com/movies/star-trek-v-the-final-frontier",
        "https://images.prismic.io/star-trek-untold/7b52acec-d000-4cde-a061-016862adddd6_StarTrekV_TheFinalFrontier_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek V: The Final Frontier"),
    "film-poster-link-undiscovered-country-20261103": (
        "film-undiscovered-country", "https://www.startrek.com/movies/star-trek-vi-the-undiscovered-country",
        "https://images.prismic.io/star-trek-untold/1481f129-37d3-46c8-a465-6ddfac06734f_StarTrekVI_TheUndiscoveredCountry_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek VI: The Undiscovered Country"),
    "film-poster-link-generations-20261103": (
        "film-generations", "https://www.startrek.com/movies/star-trek-generations",
        "https://images.prismic.io/star-trek-untold/3bd1e02e-a547-473f-ade8-27876878d1fb_StarTrek_Generations_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek Generations featuring James T. Kirk and Jean-Luc Picard"),
    "film-poster-link-first-contact-20261103": (
        "film-first-contact", "https://www.startrek.com/movies/star-trek-viii-first-contact",
        "https://images.prismic.io/star-trek-untold/fd853cdc-24d2-4812-8896-f234f6d22755_StarTrek_FirstContact_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek: First Contact featuring Jean-Luc Picard, Data and the Borg Queen"),
    "film-poster-link-insurrection-20261103": (
        "film-insurrection", "https://www.startrek.com/movies/star-trek-ix-insurrection",
        "https://images.prismic.io/star-trek-untold/de5418d2-eb10-49b3-8d91-04f9d33e5180_StarTrek_Insurrection_KeyArt_2023_full.png?auto=compress%2Cformat",
        "Poster art for Star Trek: Insurrection"),
}
PACKET_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only", "observed_utc_date",
    "source_input", "source_independence_group", "source_relative_observation_count",
    "image_bytes_retrieved", "image_bytes_committed", "public_artwork_release_effect",
    "explorer_effect", "accepted_work_binding_effect", "research_coverage_effect",
    "rights_status", "observations",
}
ROW_KEYS = {
    "local_id", "film_directory_id", "source_url", "source_page_evidence",
    "publisher_image_alt_label", "image_locator", "image_role", "source_page_access",
    "image_fetch_status", "display_eligible",
}
EVIDENCE_DEFAULT = "Official page Poster image link, following the film heading; image alt calls it poster art."
EVIDENCE_SEARCH = (
    "Official page Poster image link; page's 1982 date is inconsistent with the film's "
    "standard release year and is not adopted here."
)


def _unique_pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)


def errors(packet: object, root: Path = ROOT) -> list[str]:
    failures: list[str] = []

    def check(predicate: bool, message: str) -> None:
        if not predicate:
            failures.append(message)

    if not isinstance(packet, dict):
        return ["root packet must be object"]
    check(set(packet) == PACKET_KEYS, "closed packet schema")
    check(packet.get("schema_version") == "1.0.0", "schema version")
    check(packet.get("batch_id") == "FILMS.OFFICIAL.POSTER.LINKS.20261103.001", "batch ID")
    check(packet.get("role") == "FILMS", "wrong role")
    check(packet.get("proposal_only") is True, "proposal must remain held")
    check(packet.get("observed_utc_date") == "2026-11-03", "observation date")
    check(packet.get("source_independence_group") == "publisher:startrek.com", "lineage")
    check(packet.get("source_relative_observation_count") == 8, "declared count")
    for key in ("image_bytes_retrieved", "image_bytes_committed"):
        check(packet.get(key) is False, f"{key} must remain false")
    for key in ("public_artwork_release_effect", "explorer_effect", "accepted_work_binding_effect", "research_coverage_effect"):
        check(packet.get(key) == "NONE", f"{key} must remain NONE")
    check(packet.get("rights_status") == "HELD_NO_PUBLIC_DISPLAY_LICENSE", "rights hold")
    check(packet.get("source_input") == {"path": FILM_CATALOG, "sha256": FILM_CATALOG_SHA256}, "source input binding")

    source_path = root / FILM_CATALOG
    try:
        source_bytes = source_path.read_bytes()
        source = read_json(source_path)
        check(hashlib.sha256(source_bytes).hexdigest() == FILM_CATALOG_SHA256, "source input changed")
        films = {x["id"]: x for x in source["films"]}
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return failures + [f"cannot read pinned film catalog: {type(exc).__name__}"]

    rows = packet.get("observations")
    if not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows):
        return failures + ["observations must be objects"]
    check(len(rows) == 8, "eight observations")
    counts = Counter(x.get("local_id") for x in rows)
    check(set(counts) == set(PINS) and all(c == 1 for c in counts.values()), "exact eight unique observation IDs")
    check(len({x.get("image_locator") for x in rows if isinstance(x.get("image_locator"), str)}) == 8,
          "distinct image locators")
    for row in rows:
        local_id = row.get("local_id")
        check(set(row) == ROW_KEYS, f"{local_id}: closed row schema")
        pinned = PINS.get(local_id)
        if pinned is None:
            continue
        film_id, page, poster, alt = pinned
        check((row.get("film_directory_id"), row.get("source_url"), row.get("image_locator"), row.get("publisher_image_alt_label")) == pinned,
              f"{local_id}: exact film/page/poster/alt binding")
        check(films.get(film_id, {}).get("source_locator") == page,
              f"{local_id}: film catalog reference")
        check(row.get("image_role") == "PUBLISHER_POSTER_LINK_LABEL_NOT_PIXEL_REVIEW", f"{local_id}: label not pixels")
        check(row.get("source_page_access") == "FIRST_PARTY_HTML_TEXT_READ", f"{local_id}: source access")
        check(row.get("image_fetch_status") == "CLICK_TARGET_EXTRACTED_IMAGE_BYTES_NOT_FETCHED",
              f"{local_id}: fetch access")
        check(row.get("display_eligible") is False, f"{local_id}: display forbidden")
        expected_evidence = EVIDENCE_SEARCH if film_id == "film-search-for-spock" else EVIDENCE_DEFAULT
        check(row.get("source_page_evidence") == expected_evidence, f"{local_id}: evidence text")
        for value, expected_host in ((page, "www.startrek.com"), (poster, "images.prismic.io")):
            parsed = urlsplit(value)
            check(parsed.scheme == "https" and parsed.hostname == expected_host and
                  not parsed.username and not parsed.password and parsed.port is None and
                  not parsed.fragment and all(ord(c) >= 32 for c in value),
                  f"{local_id}: source/image URL scope")
    return failures


if __name__ == "__main__":
    findings = errors(read_json(HERE / "records.json"))
    if findings:
        for finding in findings:
            print(f"FAIL {finding}")
        raise SystemExit(1)
    print("PASS: eight exact publisher poster-link observations, no image/display/coverage claims")
