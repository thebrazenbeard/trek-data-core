#!/usr/bin/env python3
"""Exact first-party S&S ISBN edition inventory, HELD and source-relative."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PACKET_KEYS = {
    "schema_version", "batch_id", "role", "proposal_only",
    "accepted_main_at_selection", "publisher", "source_family", "observed_utc",
    "retrieval_surface", "description_digest_method", "source_body_archived",
    "full_books_or_audio_consumed", "copyright_full_text_published",
    "public_cover_display_authorized", "accepted_work_effect", "coverage_effect",
    "global_edition_equivalence_effect", "rows",
}
ROW_KEYS = {
    "isbn13", "publisher_title", "contributors", "series", "format", "imprint",
    "publication_date", "pages", "runtime_minutes", "narrator_credit",
    "source_url", "publisher_about_sha256", "publisher_about_codepoints",
    "cover_url_held", "cover_rights_state", "text_rights_state", "identity_state",
}
SNAPSHOTS = {
    "explorer/lit-publisher-edition-leads.json": "0568db4c7313f3a3da4b3cd4a5d9e56430fe09e64ed0687d8d9690d782df67d5",
    "explorer/publisher-isbn-crosschecks.json": "1170e8cb56b4ff3c5beab8d412fa5613b6e3b9d0ab7b5a18f80fe403c5bde3e8",
}
BASE = "6271a861f6dbf5337a6a6792bb4b5ee355311157"
METHOD = "WEB_RENDERED_ABOUT_BOOK_PARAGRAPHS_COLLAPSE_WHITESPACE_SHA256_UTF8_V1"
HELD = "HELD_FIRST_PARTY_URL_ONLY_NO_PUBLIC_DISPLAY_LICENSE"
IDENTITY = "ISBN_SPECIFIC_EDITION_NO_ACCEPTED_GLOBAL_WORK_LINK"
SCRIPT_IDENTITY = "SCRIPT_ADAPTATION_OF_AUDIO_DRAMA_NO_EQUIVALENCE_DECISION"
AUDIO_IDENTITY = "ORIGINAL_AUDIO_DRAMA_RELATION_TO_LATER_SCRIPT_UNRESOLVED"
ROOT = "https://www.simonandschuster.com/books/"
COVER = "https://d28hgpri8am2if.cloudfront.net/book_images/onix/cvr"
# ISBN, title, contributors, series, format, imprint, date, pages, minutes, narrator,
# publisher URL remainder, about-book SHA/codepoints, cover slug, text rights, identity.
PINS = [
    ("9781797168432", "Star Trek: Picard: Firewall", ("David Mack",), "Star Trek: Picard",
     "UNABRIDGED_AUDIO_DOWNLOAD", "Simon & Schuster Audio", "2024-02-27", None, 742,
     "January LaVoy", "Star-Trek-Picard-Firewall/David-Mack/Star-Trek-Picard",
     "d992282496fd0b99c87022f1a3a4be587ea64323960cd775a98ea17aaf117c3b", 541,
     "star-trek-picard-firewall", "NO_FULL_BOOK_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", IDENTITY),
    ("9781668046425", "Pliable Truths", ("Dayton Ward",), "Star Trek: The Next Generation",
     "EBOOK", "Pocket Books/Star Trek", "2024-05-21", 352, None, None,
     "Pliable-Truths/Dayton-Ward/Star-Trek-The-Next-Generation",
     "e1d4c074d1867edef1607901d886cddae4fd49f7bdfe9e01b3403ea2f6138ac3", 1214,
     "pliable-truths", "NO_FULL_BOOK_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", IDENTITY),
    ("9781668066133", "Star Trek: Picard: No Man's Land", ("Kirsten Beyer", "Mike Johnson"),
     "Star Trek: Picard", "TRADE_PAPERBACK_SCRIPT", "Pocket Books/Star Trek", "2024-09-24",
     160, None, None, "Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer",
     "3480f4b02c12b7f301e78d1bdf19c6f70b86cc42c559cf1dbd34b0f1c83da011", 807,
     "star-trek-picard-no-mans-land", "NO_FULL_SCRIPT_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", SCRIPT_IDENTITY),
    ("9781668066140", "Star Trek: Picard: No Man's Land", ("Kirsten Beyer", "Mike Johnson"),
     "Star Trek: Picard", "EBOOK_SCRIPT", "Pocket Books/Star Trek", "2024-09-24",
     160, None, None, "Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer",
     "3480f4b02c12b7f301e78d1bdf19c6f70b86cc42c559cf1dbd34b0f1c83da011", 807,
     "star-trek-picard-no-mans-land", "NO_FULL_SCRIPT_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", SCRIPT_IDENTITY),
    ("9781797124537", "Star Trek: Picard: No Man's Land", ("Kirsten Beyer", "Mike Johnson"),
     "Star Trek: Picard", "UNABRIDGED_AUDIO_DOWNLOAD", "Simon & Schuster Audio Originals",
     "2022-02-22", None, 99, "FULL_CAST_PUBLISHER_CREDITS_PRESENT_NOT_COPIED_INTO_THIS_BATCH",
     "Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer/Star-Trek-Picard",
     "3480f4b02c12b7f301e78d1bdf19c6f70b86cc42c559cf1dbd34b0f1c83da011", 807,
     "star-trek-picard-no-mans-land", "NO_AUDIO_OR_FULL_PUBLISHER_DESCRIPTION_REPUBLICATION", AUDIO_IDENTITY),
    ("9781668074565", "Star Trek: Strange New Worlds: Toward the Night", ("James Swallow",),
     "Star Trek: Strange New Worlds", "HARDCOVER", "Pocket Books/Star Trek", "2025-04-29",
     336, None, None, "Star-Trek-Strange-New-Worlds-Toward-the-Night/James-Swallow/Star-Trek-Strange-New-Worlds",
     "58063e53ee9d81e5094f4ce8beec1d47f1e1650d9b5fd349583752656d731659", 915,
     "star-trek-strange-new-worlds-toward-the-night", "NO_FULL_BOOK_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", IDENTITY),
    ("9781668116968", "Star Trek: Strange New Worlds: Toward the Night", ("James Swallow",),
     "Star Trek: Strange New Worlds", "UNABRIDGED_AUDIO_DOWNLOAD", "Simon & Schuster Audio",
     "2025-04-29", None, 596, "Robert Petkoff",
     "Star-Trek-Strange-New-Worlds-Toward-the-Night/James-Swallow/Star-Trek-Strange-New-Worlds",
     "a22653d21319a11dd8e5ebc59b82df911e1e17a6f38531953da4ad4328f04217", 1187,
     "star-trek-strange-new-worlds-toward-the-night", "NO_FULL_BOOK_OR_PUBLISHER_DESCRIPTION_REPUBLICATION", IDENTITY),
]


def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key " + k)
        d[k] = v
    return d


def load(path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 100000:
        raise ValueError("missing, symlinked or oversized packet")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def require(ok, message):
    if not ok:
        raise ValueError("SNS seven editions invalid: " + message)


def isbn13_valid(value):
    if type(value) is not str or re.fullmatch(r"97[89][0-9]{10}", value) is None:
        return False
    return (sum(int(x) * (1 if i % 2 == 0 else 3) for i, x in enumerate(value)) % 10) == 0


def accepted_duplicate_scan(repo):
    """Fail closed if an accepted research/Explorer lane already claims an exact edition.

    No attempt to make publisher publication proposals canonical; those are weaker.
    """
    for base in ("proposals/librarian", "proposals/research/lit", "explorer"):
        root = repo / base
        require(root.is_dir() and not root.is_symlink(), "accepted scan root drift " + base)
        for path in root.rglob("*.json"):
            if path.is_relative_to(HERE):
                continue
            require(not path.is_symlink() and path.stat().st_size < 10_000_000,
                    "accepted scan refused symlink/oversize " + str(path))
            content = path.read_text(encoding="utf-8")
            for pin in PINS:
                require(pin[0] not in content, "accepted ISBN collision " + pin[0])


def validate(packet=None, repo=REPO, scan_accepted=True):
    if packet is None:
        packet = load(HERE / "records.json")
    require(type(packet) is dict and set(packet) == PACKET_KEYS, "closed envelope fields")
    exact = {
        "schema_version": "1.0.0", "batch_id": "SNS.PUBLIC.SEVEN.EDITION.LOCATORS.20261103",
        "role": "LIBRARIAN_SOURCE_EDITION_INVENTORY", "proposal_only": True,
        "accepted_main_at_selection": BASE,
        "publisher": "Simon & Schuster", "source_family": "publisher:simonandschuster.com",
        "observed_utc": "2026-11-03",
        "retrieval_surface": "FIRST_PARTY_PUBLISHER_PAGES_RENDERED_VIA_WEB_SEARCH_NOT_ARCHIVED_HTML",
        "description_digest_method": METHOD,
        "source_body_archived": False, "full_books_or_audio_consumed": False,
        "copyright_full_text_published": False, "public_cover_display_authorized": False,
        "accepted_work_effect": "NONE", "coverage_effect": "NONE",
        "global_edition_equivalence_effect": "NONE",
    }
    for k, value in exact.items():
        require(type(packet[k]) is type(value) and packet[k] == value, "forged envelope " + k)
    for path, expected_digest in SNAPSHOTS.items():
        snapshot = repo / path
        require(snapshot.is_file() and not snapshot.is_symlink() and
                hashlib.sha256(snapshot.read_bytes()).hexdigest() == expected_digest,
                "accepted catalogue bytes drift " + path)
    rows = packet["rows"]
    require(type(rows) is list and len(rows) == 7, "exact seven nonduplicate editions")
    identifiers, covers, sources = set(), set(), set()
    for item, p in zip(rows, PINS):
        (isbn, title, contributors, series, form, imprint, date, pages, runtime, narrator,
         page_path, about_sha, about_len, cover_slug, text_rights, identity) = p
        require(type(item) is dict and set(item) == ROW_KEYS, "closed row fields")
        require(isbn13_valid(item["isbn13"]) and item["isbn13"] == isbn,
                "exact verified ISBN/edition binding")
        for field, expected in (
            ("publisher_title", title), ("contributors", list(contributors)),
            ("series", series), ("format", form), ("imprint", imprint),
            ("publication_date", date), ("pages", pages),
            ("runtime_minutes", runtime), ("narrator_credit", narrator),
            ("publisher_about_sha256", about_sha),
            ("publisher_about_codepoints", about_len), ("text_rights_state", text_rights),
            ("identity_state", identity),
        ):
            actual = item[field]
            require(type(actual) is type(expected) and actual == expected,
                    "exact publisher edition field " + isbn + " " + field)
        require(item["source_url"] == ROOT + page_path + "/" + isbn,
                "per-edition publisher URL")
        cover = COVER + isbn + "/" + cover_slug + "-" + isbn + "_hr.jpg"
        require(item["cover_url_held"] == cover and item["cover_rights_state"] == HELD,
                "publisher-linked cover locator and rights hold")
        u, v = urlsplit(item["source_url"]), urlsplit(item["cover_url_held"])
        require(u.scheme == v.scheme == "https" and u.hostname == "www.simonandschuster.com"
                and v.hostname == "d28hgpri8am2if.cloudfront.net"
                and not any((u.query, u.fragment, v.query, v.fragment)),
                "no alternate URL host, credential query, or fragment")
        identifiers.add(isbn)
        covers.add(item["cover_url_held"])
        sources.add(item["source_url"])
    require(len(identifiers) == len(covers) == len(sources) == 7, "duplicate ISBN/cover/source")
    require(rows[2]["publisher_title"] == rows[3]["publisher_title"] == rows[4]["publisher_title"]
            and rows[2]["format"] != rows[4]["format"]
            and rows[4]["publication_date"] < rows[2]["publication_date"]
            and rows[2]["identity_state"] != rows[4]["identity_state"],
            "No Man's Land original audio and subsequent script not silently equated")
    if scan_accepted:
        accepted_duplicate_scan(repo)
    return 7


if __name__ == "__main__":
    print("SNS_SEVEN_SOURCE_ONLY_OK", validate(), "ISBN editions; no Work, rights, or coverage effect")
