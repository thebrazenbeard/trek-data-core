#!/usr/bin/env python3
"""Offline, deterministic custody checks for the artwork locator proposal.

Do not import this file in production Explorer code: locator discovery is not
public-display authorization.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED_COUNTS = {"FILM": 3, "LITERATURE": 3, "EPISODE": 4}
EXPECTED_HOSTS = {
    "FILM": ("www.startrek.com", "images.prismic.io", "publisher:startrek.com"),
    "LITERATURE": ("www.simonandschuster.com", "d28hgpri8am2if.cloudfront.net", "publisher:simonandschuster.com"),
    "EPISODE": ("www.paramountplus.com", "thumbnails.cbsig.net", "publisher:paramountplus.com"),
}
EXPECTED_FILM_IDS = {"film-wrath-of-khan", "film-nemesis", "film-2009"}
EXPECTED_LIT = {
    "lit-sns-kobayashi-maru-ebook-9780743419987-20261103": ("9780743419987", "EBOOK"),
    "lit-sns-shadows-of-the-sun-abridged-audio-9780743546744-20261103": ("9780743546744", "ABRIDGED_AUDIO_DOWNLOAD"),
    "lit-sns-genesis-wave-three-adapted-audio-9780743546591-20261103": ("9780743546591", "ADAPTED_AUDIO_DOWNLOAD"),
}
EXPECTED_EPISODES = {"snw-s3-e01-pplus", "snw-s3-e05-pplus", "snw-s3-e06-pplus", "snw-s3-e10-pplus"}


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_https(url: str, host: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme == "https"
            and parsed.hostname == host
            and parsed.username is None
            and parsed.password is None
            and parsed.port is None
            and not parsed.fragment
            and not any(ord(c) < 32 for c in url)
        )
    except (ValueError, AttributeError, TypeError):
        return False


def errors(data: dict, root: Path = ROOT) -> list[str]:
    failures = []

    def check(condition: bool, reason: str) -> None:
        if not condition:
            failures.append(reason)

    check(data.get("proposal_only") is True, "proposal-only invariant")
    check(data.get("role") == "LIBRARIAN", "wrong role")
    check(data.get("batch_id") == "ARTWORK.PRIMARY.LOCATORS.20261103", "batch ID")
    check(data.get("source_relative_observation_count") == 10, "declared count")
    for field in ("image_bytes_retrieved", "image_bytes_committed"):
        check(data.get(field) is False, f"{field} must remain false")
    for field in ("public_artwork_release_effect", "explorer_effect", "accepted_work_binding_effect", "research_coverage_effect"):
        check(data.get(field) == "NONE", f"{field} must remain NONE")
    check(data.get("rights_assessment") == "NO_PUBLIC_DISPLAY_LICENSE_ESTABLISHED", "rights assessment")

    inputs = data.get("source_inputs", [])
    check(len(inputs) == 4, "four exact inputs required")
    source_paths = set()
    source_cache = {}
    for item in inputs:
        path_text = item.get("path", "")
        check(path_text not in source_paths, "duplicate source input")
        source_paths.add(path_text)
        path = (root / path_text).resolve()
        check(path.is_relative_to(root.resolve()) and path.is_file(), "invalid input path")
        if path.is_file() and path.is_relative_to(root.resolve()):
            check(hashlib.sha256(path.read_bytes()).hexdigest() == item.get("sha256"), "source input digest drift")
            source_cache[path_text] = _read_json(path)

    rows = data.get("observations", [])
    check(len(rows) == 10, "exactly ten observations")
    check(Counter(row.get("medium") for row in rows) == EXPECTED_COUNTS, "medium counts")
    check(len({row.get("local_id") for row in rows}) == len(rows), "duplicate local IDs")
    check(len({row.get("image_locator") for row in rows}) == len(rows), "duplicate image locators")
    seen_film, seen_lit, seen_episode = set(), set(), set()

    for row in rows:
        kind, local = row.get("medium"), row.get("source_local_work_id")
        if kind not in EXPECTED_HOSTS:
            failures.append(f"unknown medium {kind}")
            continue
        page_host, asset_host, independence = EXPECTED_HOSTS[kind]
        check(_valid_https(row.get("publisher_source_url"), page_host), f"{local}: source host")
        check(_valid_https(row.get("image_locator"), asset_host), f"{local}: image host")
        check(row.get("independence_group") == independence, f"{local}: independence group")
        check(row.get("rights_status") == "HELD_NO_PUBLIC_DISPLAY_LICENSE", f"{local}: rights hold")
        check(row.get("display_eligible") is False, f"{local}: display disabled")
        check(row.get("source_input") in source_cache, f"{local}: missing pinned source")
        check(bool(row.get("locator_evidence")), f"{local}: missing locator evidence")
        source = source_cache.get(row.get("source_input"), {})

        if kind == "FILM":
            seen_film.add(local)
            check(row.get("image_kind") == "PUBLISHER_PAGE_OG_HEADER_NOT_POSTER", f"{local}: OG image not poster")
            check(row.get("source_inspection") == "FIRST_PARTY_HTML_META", f"{local}: inspection")
            matching = [film for film in source.get("films", []) if film.get("id") == local]
            check(len(matching) == 1 and matching[0].get("source_locator") == row.get("publisher_source_url"), f"{local}: film binding")
        elif kind == "LITERATURE":
            seen_lit.add(local)
            check(local in EXPECTED_LIT, f"{local}: unknown edition")
            isbn, edition = EXPECTED_LIT.get(local, (None, None))
            check(row.get("image_kind") == ("PUBLISHER_LINKED_HIGH_RES_COVER_FOR_EBOOK_ISBN" if edition == "EBOOK" else "PUBLISHER_LINKED_HIGH_RES_COVER_FOR_AUDIO_ISBN"), f"{local}: edition image type")
            check(row.get("source_inspection") == "FIRST_PARTY_RENDERED_PAGE_AND_IMAGE_LINK", f"{local}: inspection")
            check(isbn is not None and isbn in row.get("image_locator", ""), f"{local}: exact ISBN in cover locator")
            matching = [candidate for candidate in source.get("candidates", []) if candidate.get("candidate_id") == local]
            check(len(matching) == 1 and matching[0].get("publisher_url") == row.get("publisher_source_url") and matching[0].get("publisher_isbn13") == isbn and matching[0].get("publisher_edition_format") == edition, f"{local}: edition binding")
        else:
            seen_episode.add(local)
            check(row.get("image_kind") == "PUBLISHER_EPISODE_CARD_THUMBNAIL", f"{local}: image type")
            check(row.get("source_inspection") == "FIRST_PARTY_HTML_CARD", f"{local}: inspection")
            check(row.get("publisher_source_url") == source.get("source", {}).get("url"), f"{local}: publisher source")
            works = [work for work in source.get("works", []) if work.get("local_work_id") == local]
            arts = [art for art in source.get("artwork_candidates", []) if art.get("work_id") == local]
            check(len(works) == 1 and len(arts) == 1 and arts[0].get("source_url") == row.get("image_locator"), f"{local}: episode artwork mapping")

    check(seen_film == EXPECTED_FILM_IDS, "film ID set")
    check(seen_lit == set(EXPECTED_LIT), "literary edition ID set")
    check(seen_episode == EXPECTED_EPISODES, "episode ID set")
    return failures


if __name__ == "__main__":
    found = errors(_read_json(HERE / "records.json"))
    if found:
        for error in found:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: ten source-relative artwork candidates remain pinned, edition-bound, and rights-held")
