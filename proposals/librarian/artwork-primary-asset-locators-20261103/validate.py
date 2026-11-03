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
# These four exact accepted inputs are the reviewed source custody baseline.
# An unrelated in-repo JSON file with a freshly computed digest must not become
# a substitute source for an already reviewed observation.
EXPECTED_SOURCE_INPUT_DIGESTS = {
    "explorer/film-catalog.json": "6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de",
    "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json": "03173ed5ac94c7052a8c416bcca9cc762a8e7ca0ca3280eae0a4b3f902954dea",
    "proposals/research/snw/s3-publisher-first5-20261103/records.json": "89e816d651996405dce608fa3509b437178b0dcd635f2d8635962d0bd7acfe1c",
    "proposals/research/snw/s3-publisher-last5-20261103/records.json": "b1daa95e849c61beb1011aabaebc06343589f29d0ec786e6359c07cb81137b2e",
}
# local_id -> (medium, source-local work/edition ID, publisher page,
#              source input). A set-only check of the work IDs is insufficient:
# two film records could exchange their work IDs and page URLs while retaining
# image URLs pinned to their *original* local IDs.
EXPECTED_OBSERVATION_BINDINGS = {
    "art-film-wrath-khan-og-20261103": (
        "FILM", "film-wrath-of-khan", "https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan", "explorer/film-catalog.json"),
    "art-film-nemesis-og-20261103": (
        "FILM", "film-nemesis", "https://www.startrek.com/movies/star-trek-nemesis", "explorer/film-catalog.json"),
    "art-film-2009-og-20261103": (
        "FILM", "film-2009", "https://www.startrek.com/movies/star-trek-2009", "explorer/film-catalog.json"),
    "art-lit-kobayashi-ebook-20261103": (
        "LITERATURE", "lit-sns-kobayashi-maru-ebook-9780743419987-20261103", "https://www.simonandschuster.com/books/The-Kobayashi-Maru/Julia-Ecklar/Star-Trek-The-Original-Series/9780743419987", "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json"),
    "art-lit-shadows-audio-20261103": (
        "LITERATURE", "lit-sns-shadows-of-the-sun-abridged-audio-9780743546744-20261103", "https://www.simonandschuster.com/books/Shadows-of-the-Sun/Michael-Jan-Friedman/Star-Trek-The-Original-Series/9780743546744", "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json"),
    "art-lit-genesis-audio-20261103": (
        "LITERATURE", "lit-sns-genesis-wave-three-adapted-audio-9780743546591-20261103", "https://www.simonandschuster.com/books/The-Star-Trek-The-Next-Generation-The-Genesis-Wave-Book-3/John-Vornholt/Star-Trek-The-Next-Generation/9780743546591", "proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json"),
    "art-snw-s3-e01-20261103": (
        "EPISODE", "snw-s3-e01-pplus", "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "proposals/research/snw/s3-publisher-first5-20261103/records.json"),
    "art-snw-s3-e05-20261103": (
        "EPISODE", "snw-s3-e05-pplus", "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "proposals/research/snw/s3-publisher-first5-20261103/records.json"),
    "art-snw-s3-e06-20261103": (
        "EPISODE", "snw-s3-e06-pplus", "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "proposals/research/snw/s3-publisher-last5-20261103/records.json"),
    "art-snw-s3-e10-20261103": (
        "EPISODE", "snw-s3-e10-pplus", "https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/", "proposals/research/snw/s3-publisher-last5-20261103/records.json"),
}
# These ten exact page-observed image URL bindings are a separately maintained
# validator pin. Host allowlisting and ISBN substrings alone are insufficient:
# unrelated images can share a publisher-controlled host and ISBN substring.
EXPECTED_IMAGE_LOCATORS = {
    "art-film-wrath-khan-og-20261103": "https://images.prismic.io/star-trek-untold/c963252d-40f1-445e-9616-553653bc94c6_STARTREK_II_HEADER.png?auto=compress,format",
    "art-film-nemesis-og-20261103": "https://images.prismic.io/star-trek-untold/0104f2c8-8512-4f8c-a3a3-22f99899330d_STARTREK_NEMESIS_HEADER.png?auto=compress,format",
    "art-film-2009-og-20261103": "https://images.prismic.io/star-trek-untold/a6b3d54c-4937-4430-99f9-f1fe6eb0bf59_STARTREK_IX_HEADER.png?auto=compress,format",
    "art-lit-kobayashi-ebook-20261103": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9780743419987/the-kobayashi-maru-9780743419987_hr.jpg",
    "art-lit-shadows-audio-20261103": "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr9780743546744/star-trek-shadows-on-the-sun-9780743546744_hr.jpg",
    "art-lit-genesis-audio-20261103": "https://d28hgpri8am2if.cloudfront.net/book_images/cvr9780743546591_9780743546591_hr.jpg",
    "art-snw-s3-e01-20261103": "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2025/06/09/2432598595937/PPUSA_STARTREKSTRANGENEWWORLDS_301_V1_3291934_1920x1080.jpg",
    "art-snw-s3-e05-20261103": "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2025/06/09/2432597059776/PPUSA_STARTREKSTRANGENEWWORLDS_305_3319865_1920x1080.jpg",
    "art-snw-s3-e06-20261103": "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2025/06/09/2432601155596/PPUSA_STARTREKSTRANGENEWWORLDS_306_3319911_1920x1080.jpg",
    "art-snw-s3-e10-20261103": "https://thumbnails.cbsig.net/_x/w400/CBS_Production_Entertainment_VMS/2025/06/09/2432602179880/PPUSA_STARTREKSTRANGENEWWORLDS_310_3321226_1920x1080.jpg",
}


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
        check(set(item) == {"path", "sha256"}, "source input schema drift")
        check(path_text in EXPECTED_SOURCE_INPUT_DIGESTS and
              item.get("sha256") == EXPECTED_SOURCE_INPUT_DIGESTS.get(path_text),
              "unreviewed source input path/digest binding")
        path = (root / path_text).resolve()
        check(path.is_relative_to(root.resolve()) and path.is_file(), "invalid input path")
        if path.is_file() and path.is_relative_to(root.resolve()):
            check(hashlib.sha256(path.read_bytes()).hexdigest() == item.get("sha256"), "source input digest drift")
            source_cache[path_text] = _read_json(path)
    check(source_paths == set(EXPECTED_SOURCE_INPUT_DIGESTS), "source input path set drift")

    rows = data.get("observations", [])
    check(len(rows) == 10, "exactly ten observations")
    check(Counter(row.get("medium") for row in rows) == EXPECTED_COUNTS, "medium counts")
    check(len({row.get("local_id") for row in rows}) == len(rows), "duplicate local IDs")
    check({row.get("local_id") for row in rows} == set(EXPECTED_IMAGE_LOCATORS), "exact image observation ID set")
    check(len({row.get("image_locator") for row in rows}) == len(rows), "duplicate image locators")
    seen_film, seen_lit, seen_episode = set(), set(), set()

    for row in rows:
        kind, local = row.get("medium"), row.get("source_local_work_id")
        binding = (kind, local, row.get("publisher_source_url"), row.get("source_input"))
        check(binding == EXPECTED_OBSERVATION_BINDINGS.get(row.get("local_id")),
              f"{row.get('local_id')}: exact source/work/page/input binding")
        if kind not in EXPECTED_HOSTS:
            failures.append(f"unknown medium {kind}")
            continue
        page_host, asset_host, independence = EXPECTED_HOSTS[kind]
        check(_valid_https(row.get("publisher_source_url"), page_host), f"{local}: source host")
        check(_valid_https(row.get("image_locator"), asset_host), f"{local}: image host")
        check(row.get("image_locator") == EXPECTED_IMAGE_LOCATORS.get(row.get("local_id")), f"{local}: exact publisher-page image binding")
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
