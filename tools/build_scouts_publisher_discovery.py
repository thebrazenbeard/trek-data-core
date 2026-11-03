#!/usr/bin/env python3
"""First-party video metadata for Star Trek: Scouts: twenty candidate web shorts.

The complete StarTrek.com announcement, six discovery crosswalk pages and
twenty individual YouTube oEmbed responses are kept outside public Git.
Only bounded titles, direct video locators, byte-count/hash receipts and
source-local strand ordinals are published. No video was viewed or admitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import build_publisher_catalog as publisher
from tools import build_research_leads as research
from tools import publisher_output_directory as dirguard

BASE = Path("proposals/discovery/scouts-firstparty-video-s1-20261103")
SOURCE = BASE / "source.json"
OUTPUT = BASE / "records.json"
DATE = "2026-11-03"
ANNOUNCEMENT_URL = "https://www.startrek.com/news/star-trek-60th-2026-fan-centric-celebrations"
ANNOUNCEMENT_FILE = "trek-scouts-publisher-60th.html"
AUTHOR = "Blaze and the Monster Machines"
AUTHOR_URL = "https://www.youtube.com/@blazeandthemonstermachines"
VIDEO_IDS = (
    ("ASTEROID_BLASTERS", 1, "j-KvjtSgfJs", "oct2025"),
    ("ASTEROID_BLASTERS", 2, "x1mIN62O00s", "oct2025"),
    ("ASTEROID_BLASTERS", 3, "PfaNbFeRCm4", "oct2025"),
    ("ASTEROID_BLASTERS", 4, "j3asH2YbKz8", "oct2025"),
    ("ASTEROID_BLASTERS", 5, "60SkYJy-_2U", "octlatest"),
    ("ASTEROID_BLASTERS", 6, "Ps3cQdL1By0", "octlatest"),
    ("ASTEROID_BLASTERS", 7, "GtJpqUH3gTA", "nov"),
    ("ASTEROID_BLASTERS", 8, "6lnl4qzwHt8", "nov"),
    ("ASTEROID_BLASTERS", 9, "ODb0D3ZTgug", "nov"),
    ("ASTEROID_BLASTERS", 10, "fSRr1CGFYiY", None),
    ("HOLODECK_RESCUES", 1, "69jkEMz87co", "jan"),
    ("HOLODECK_RESCUES", 2, "6AAJlEn3DeY", "jan"),
    ("HOLODECK_RESCUES", 3, "fybF9xOzXs4", "jan"),
    ("HOLODECK_RESCUES", 4, "M02cKstXmjo", "jan"),
    ("HOLODECK_RESCUES", 5, "dZznmiZYV-A", "feb"),
    ("HOLODECK_RESCUES", 6, "-m7ISEuAhac", "feb"),
    ("HOLODECK_RESCUES", 7, "cYRzkzu_zhg", "feb"),
    ("HOLODECK_RESCUES", 8, "O5wUrGB_6qw", "mar"),
    ("HOLODECK_RESCUES", 9, "TbZFOtuHpxk", "mar"),
    ("HOLODECK_RESCUES", 10, "vlez2Dtu95E", "mar"),
)
SECONDARY = {
    "oct2025": "https://blog.trekcore.com/2025/10/star-trek-khan-star-trek-scouts-episode-roundup/",
    "octlatest": "https://blog.trekcore.com/2025/10/star-trek-khan-scouts-latest-episodes-oct25/",
    "nov": "https://blog.trekcore.com/2025/11/catch-up-on-latest-episodes-of-the-star-trek-scouts-webseries/",
    "jan": "https://blog.trekcore.com/2026/01/the-star-trek-scouts-explore-the-holodeck-in-newest-webisodes/",
    "feb": "https://blog.trekcore.com/2026/02/star-trek-scouts-holodeck-adventures-continue/",
    "mar": "https://blog.trekcore.com/2026/03/the-star-trek-scouts-conclude-their-animated-adventures-latest-webisodes/",
}


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_json(raw: bytes) -> dict:
    parsed = research._strict_json(raw, "Scouts source")
    if not isinstance(parsed, dict):
        raise ValueError("Scouts metadata must be an object")
    return parsed


def _serialize(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _safe_source(path: Path, minimum: int, maximum: int) -> bytes:
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError("symlink source forbidden")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or not minimum <= before.st_size <= maximum:
        raise ValueError("Scouts source must be bounded regular file")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise ValueError("safe file opening unsupported")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_ino != before.st_ino or opened.st_dev != before.st_dev:
            raise ValueError("Scouts source changed during open")
        raw = stream.read(maximum + 1)
    if not minimum <= len(raw) <= maximum:
        raise ValueError("Scouts source size outside bound")
    return raw


class _Canonical(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[list[tuple[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "link" and any(k == "rel" and v and "canonical" in v.lower().split() for k, v in attrs):
            self.links.append(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def _validate_announcement(raw: bytes) -> None:
    page = raw.decode("utf-8")
    links = _Canonical()
    links.feed(page)
    links.close()
    if len(links.links) != 1:
        raise ValueError("missing or duplicate StarTrek canonical link")
    attributes = links.links[0]
    if (attributes.count(("rel", "canonical")) != 1 or
            attributes.count(("href", ANNOUNCEMENT_URL)) != 1 or
            len([k for k, _ in attributes if k == "href"]) != 1 or
            len([k for k, _ in attributes if k == "rel"]) != 1):
        raise ValueError("forged canonical StarTrek announcement")
    if "20-episode order" not in page or "Star Trek: Scouts" not in page:
        raise ValueError("StarTrek announcement does not support bounded 20-video order")


def _metadata(raw: bytes, strand: str, ordinal: int, ident: str) -> str:
    data = _strict_json(raw)
    if (data.get("author_name") != AUTHOR or data.get("author_url") != AUTHOR_URL or
            data.get("provider_name") != "YouTube" or data.get("provider_url") != "https://www.youtube.com/"):
        raise ValueError("Scouts video not on the first-party publisher account")
    title = data.get("title")
    if (not isinstance(title, str) or not 10 <= len(title) <= 190 or
            title != title.strip() or any(ord(c) < 32 for c in title) or
            "Star Trek: Scouts" not in title or "<" in title or ">" in title):
        raise ValueError("invalid or unbound Scouts publisher title")
    marker = rf"Asteroid Blasters #0*{ordinal}(?!\d)" if strand == "ASTEROID_BLASTERS" else rf"Holodeck Rescues (?:Episode )?#0*{ordinal}(?!\d)"
    if not re.search(marker, title, re.I):
        raise ValueError("Scouts publisher title and assigned strand ordinal disagree")
    html = data.get("html")
    if not isinstance(html, str) or f"/embed/{ident}?" not in html:
        raise ValueError("Scouts oEmbed video iframe disagrees with source identity")
    return title


def _receipt(raw: bytes) -> dict:
    return {"sha256": _digest(raw), "byte_count": len(raw)}


def ingest(raw_directory: Path, root: Path = ROOT) -> int:
    raw_announcement = _safe_source(raw_directory / ANNOUNCEMENT_FILE, 100_000, 2_500_000)
    _validate_announcement(raw_announcement)
    crosswalk = []
    raw_crosswalk = {}
    for name, locator in SECONDARY.items():
        raw = _safe_source(raw_directory / f"trek-scouts-trekcore-{name}.html", 10_000, 2_500_000)
        raw_crosswalk[name] = raw
        crosswalk.append({"key": name, "locator": locator, **_receipt(raw)})
    videos = []
    for strand, ordinal, ident, source in VIDEO_IDS:
        raw = _safe_source(raw_directory / f"trek-scouts-oembed-{ident}.json", 100, 4_096)
        title = _metadata(raw, strand, ordinal, ident)
        if source is not None and f"www.youtube.com/embed/{ident}".encode("utf-8") not in raw_crosswalk[source]:
            raise ValueError(f"secondary crosswalk omits announced publisher video {ident}")
        videos.append({"strand": strand, "strand_ordinal": ordinal, "video_id": ident,
                       "title": title, "watch_url": f"https://www.youtube.com/watch?v={ident}",
                       "oembed_url": f"https://www.youtube.com/oembed?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{ident}&format=json",
                       "discovery_crosswalk_key": source, **_receipt(raw)})
    record = {"schema_version": "1.0.0", "proposal_status": "DISCOVERY_ONLY",
              "admission_effect": "NONE", "coverage_effect": "NONE", "denominator_effect": "NONE",
              "identity_scope": "SOURCE_LOCAL_NOT_RECONCILED", "publisher_lineage": "publisher:paramount",
              "source_note": "Secondary TrekCore embeds are discovery crosswalks, not independent evidence. YouTube oEmbed is publisher-authored metadata; no video was watched. Two #1-#10 strands are source-relative; global season ordinals unresolved.",
              "observed_on": DATE, "publisher_announcement": {"locator": ANNOUNCEMENT_URL,
                                                          **_receipt(raw_announcement)},
              "crosswalk_sources": crosswalk, "videos": videos}
    dirguard.ensure_directory(root, BASE)
    publisher.safe_write(root, SOURCE, _serialize(record))
    publisher.safe_write(root, OUTPUT, build(root))
    return check(root)


def build(root: Path = ROOT) -> bytes:
    source_raw = research.safe_read(root, SOURCE, max_bytes=35_000)
    source = _strict_json(source_raw)
    if source_raw != _serialize(source):
        raise ValueError("Scouts source sidecar must be canonical JSON")
    if (set(source) != {"schema_version", "proposal_status", "admission_effect", "coverage_effect",
                       "denominator_effect", "identity_scope", "publisher_lineage", "source_note",
                       "observed_on", "publisher_announcement", "crosswalk_sources", "videos"} or
            source["schema_version"] != "1.0.0" or source["proposal_status"] != "DISCOVERY_ONLY" or
            source["admission_effect"] != "NONE"):
        raise ValueError("Scouts source sidecar claims invalid authority")
    for key in ("admission_effect", "coverage_effect", "denominator_effect"):
        if source[key] != "NONE":
            raise ValueError("Scouts metadata cannot change research admission or denominator")
    if (source["identity_scope"] != "SOURCE_LOCAL_NOT_RECONCILED" or
            source["publisher_lineage"] != "publisher:paramount" or source["observed_on"] != DATE or
            "not independent" not in source["source_note"] or "no video was watched" not in source["source_note"]):
        raise ValueError("Scouts evidence limitations omitted")
    if (source["publisher_announcement"].get("locator") != ANNOUNCEMENT_URL or
            not re.fullmatch(r"[a-f0-9]{64}", str(source["publisher_announcement"].get("sha256"))) or
            not 100_000 <= source["publisher_announcement"].get("byte_count", -1) <= 2_500_000):
        raise ValueError("Scouts primary announcement receipt invalid")
    if (not isinstance(source["crosswalk_sources"], list) or
            [r.get("key") for r in source["crosswalk_sources"]] != list(SECONDARY)):
        raise ValueError("Scouts secondary crosswalk source order changed")
    for row in source["crosswalk_sources"]:
        if (set(row) != {"key", "locator", "sha256", "byte_count"} or
                row["locator"] != SECONDARY[row["key"]] or
                not re.fullmatch(r"[a-f0-9]{64}", str(row["sha256"])) or
                not 10_000 <= row["byte_count"] <= 2_500_000):
            raise ValueError("Scouts crosswalk source receipt invalid")
    if not isinstance(source["videos"], list) or len(source["videos"]) != len(VIDEO_IDS):
        raise ValueError("Scouts source observations outside reviewed twenty-video boundary")
    entries = []
    for observed, (strand, ordinal, ident, crosswalk) in zip(source["videos"], VIDEO_IDS):
        if (set(observed) != {"strand", "strand_ordinal", "video_id", "title", "watch_url",
                             "oembed_url", "discovery_crosswalk_key", "sha256", "byte_count"} or
                tuple(observed[key] for key in ("strand", "strand_ordinal", "video_id", "discovery_crosswalk_key")) !=
                (strand, ordinal, ident, crosswalk) or
                observed["watch_url"] != f"https://www.youtube.com/watch?v={ident}" or
                observed["oembed_url"] != f"https://www.youtube.com/oembed?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{ident}&format=json" or
                not re.fullmatch(r"[a-f0-9]{64}", str(observed["sha256"])) or
                not 100 <= observed["byte_count"] <= 4_096):
            raise ValueError("Scouts primary video identity or receipt changed")
        title = observed["title"]
        if (not isinstance(title, str) or not 10 <= len(title) <= 190 or
                title != title.strip() or any(ord(c) < 32 for c in title) or
                "<" in title or ">" in title or "Star Trek: Scouts" not in title):
            raise ValueError("Scouts publisher title missing")
        marker = rf"Asteroid Blasters #0*{ordinal}(?!\d)" if strand == "ASTEROID_BLASTERS" else rf"Holodeck Rescues (?:Episode )?#0*{ordinal}(?!\d)"
        if not re.search(marker, title, re.I):
            raise ValueError("Scouts recorded source-local ordinal not in publisher title")
        entries.append({"candidate_id": f"scouts:{strand.lower()}:{ordinal:02d}", "strand": strand,
                        "source_local_slot": f"#{ordinal}", "title": title,
                        "source_locator": f"https://youtu.be/{ident}",
                        "official_oembed_sha256": observed["sha256"],
                        "verification_status": "UNVERIFIED_METADATA", "accepted_work_id": None})
    return _serialize({"schema_version": "1.0.0", "data_status": "DISCOVERY_ONLY",
                       "admission_effect": "NONE", "coverage_effect": "NONE",
                       "publisher_independence_group": "publisher:paramount",
                       "source_input": str(SOURCE), "source_sha256": _digest(_serialize(source)),
                       "short_candidate_count": len(entries), "short_candidates": entries})


def check(root: Path = ROOT) -> int:
    expected = build(root)
    actual = research.safe_read(root, OUTPUT, max_bytes=35_000)
    if expected != actual:
        raise ValueError("Scouts public source-local rows differ from vetted input")
    print("SCOUTS_SOURCE_LOCAL_OK: 20 publisher video metadata observations, no admission")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, help="Private announcement, crosswalk HTML and oEmbed captures")
    parser.add_argument("--check", action="store_true", help="Recheck existing derivative without network")
    args = parser.parse_args(argv)
    try:
        return ingest(args.raw_dir) if args.raw_dir and not args.check else check() if args.check and not args.raw_dir else 1
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"SCOUTS_SOURCE_LOCAL_REJECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
