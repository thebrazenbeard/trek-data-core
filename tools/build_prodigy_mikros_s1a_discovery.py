#!/usr/bin/env python3
"""Candidate-only Prodigy S1 volume-one title inventory from Mikros Animation.

The studio article says Volume 1 contains the first ten installments and lists
ten titles in a sentence. Assigning episode slots 1–10 from that listed order is
an explicit *inference*, not a studio-published numbered episode guide.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
from html.parser import HTMLParser
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_legacy_s2_discovery import ensure_no_symlink, safe_atomic_write
from tools import build_publisher_s6_discovery as source_reader
from tools import publisher_output_directory as output_directory
from tools import validate_publisher_episode_roster as roster

DATE = "2026-11-02"
BASE = Path("proposals/discovery/prodigy-mikros-volume1-20261102")
SOURCE_ID = "mikros-s1a"
URL = "https://www.mikrosanimation.com/en/news/star-trek-prodigy-begins-its-blu-ray-journey/"
CROSSCHECK = "https://www.startrek.com/news/star-trek-prodigy-season-1-volume-1-release"
SOURCE_KEYS = {"schema_version", "batch_id", "proposal_status", "observed_on", "source_id",
               "publisher", "independence_group", "source_page", "raw_sha256", "raw_bytes",
               "csv_sha256", "listed_title_count", "ordinal_basis", "title_expansions", "caption_exception",
               "crosscheck_locator", "crosscheck_limit", "admission_effect", "coverage_effect"}
TITLE_RE = re.compile(r"“([^”]{1,100})”")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialize(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


class StudioPage(HTMLParser):
    """Parse canonical metadata and bounded paragraph text without scripts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []
        self.paragraphs: list[str] = []
        self._in_p = False
        self._parts: list[str] = []
        self._skip = 0
        self.figcaptions: list[str] = []
        self._caption_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names = [k.casefold() for k, _ in attrs]
        if len(names) != len(set(names)):
            raise ValueError("duplicate HTML attributes forbidden")
        attr = dict(attrs)
        if tag == "link" and "canonical" in (attr.get("rel") or "").casefold().split():
            self.canonicals.append(attr.get("href") or "")
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "p" and not self._skip:
            if self._in_p:
                raise ValueError("nested publisher paragraph")
            self._in_p = True
            self._parts = []
        if tag == "figcaption" and not self._skip:
            if self._caption_parts is not None:
                raise ValueError("nested figure caption")
            self._caption_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        if tag == "p" and self._in_p:
            self.paragraphs.append("".join(self._parts))
            self._in_p = False
            self._parts = []
        if tag == "figcaption" and self._caption_parts is not None:
            self.figcaptions.append("".join(self._caption_parts))
            self._caption_parts = None

    def handle_data(self, data: str) -> None:
        if self._in_p and not self._skip:
            self._parts.append(data)
        if self._caption_parts is not None and not self._skip:
            self._caption_parts.append(data)


def caption_exception(raw: bytes) -> dict:
    """Retain a singular same-source image label without treating it as a roster.

    The production-style ``Ep#103`` caption does not establish season numbering
    for all ten titles and is not independent corroboration of the list.
    """
    page = StudioPage()
    page.feed(raw.decode("utf-8"))
    page.close()
    labels = [value for value in page.figcaptions if "Starstruck" in value and "Ep#103" in value]
    if len(labels) != 1:
        raise ValueError("source-specific Starstruck image caption label absent or ambiguous")
    return {"title": "Starstruck", "literal_label": "Ep#103",
            "origin": "SAME_MIKROS_ARTICLE_FIGCAPTION",
            "season_ordinal_or_independence_effect": "NONE"}


def extract(raw: bytes) -> list[tuple[int, int, str]]:
    if not 10_000 <= len(raw) <= 500_000:
        raise ValueError("Mikros article outside bounded byte size")
    page = StudioPage()
    page.feed(raw.decode("utf-8"))
    page.close()
    if page.canonicals != [URL]:
        raise ValueError("Mikros page missing, duplicate, or forged canonical locator")
    introductions = [p for p in page.paragraphs if "first ten episodes" in p.casefold()]
    descriptions = [p for p in page.paragraphs if "The set includes" in p]
    if len(introductions) != 1 or len(descriptions) != 1:
        raise ValueError("publisher article title-list scope absent or duplicated")
    if "Volume 1" not in introductions[0]:
        raise ValueError("source no longer identifies first-ten volume")
    description = html.unescape(descriptions[0])
    if len(description) > 2_000:
        raise ValueError("unbounded article title paragraph")
    titles = [s.strip().rstrip(",.") for s in TITLE_RE.findall(description)]
    if len(titles) != 10:
        raise ValueError("not exactly ten studio-listed quoted title fragments")
    if titles[0] != "Lost and Found, Part I" or titles[1] != "Part II":
        raise ValueError("opening multipart title no longer matches the recorded structure")
    if titles[-2:] != ["A Moral Star, Part 1", "Part 2"]:
        raise ValueError("closing multipart title no longer matches the recorded structure")
    # Explicit, reversible editorial expansions of abbreviated follow-on parts.
    titles[1] = "Lost and Found, Part II"
    titles[-1] = "A Moral Star, Part 2"
    if any(not re.fullmatch(r"[^<>\x00-\x1f\x7f]{2,120}", title) for title in titles):
        raise ValueError("unsupported or suspicious studio title")
    if len({title.casefold() for title in titles}) != 10:
        raise ValueError("duplicate studio title")
    return [(1, n, title) for n, title in enumerate(titles, 1)]


def csv_bytes(rows: list[tuple[int, int, str]]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.writer(target, lineterminator="\n")
    writer.writerow(["season", "episode_number", "title"])
    writer.writerows(rows)
    return target.getvalue().encode("utf-8")


def read_csv(raw: bytes) -> list[tuple[int, int, str]]:
    if len(raw) > 10_000:
        raise ValueError("candidate CSV is oversized")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    if reader.fieldnames != ["season", "episode_number", "title"]:
        raise ValueError("candidate CSV header changed")
    result: list[tuple[int, int, str]] = []
    for row in reader:
        if None in row or set(row) != {"season", "episode_number", "title"}:
            raise ValueError("malformed CSV record")
        if not row["season"].isdigit() or not row["episode_number"].isdigit():
            raise ValueError("malformed season/ordinal")
        result.append((int(row["season"]), int(row["episode_number"]), row["title"]))
    if len(result) != 10 or [(s, n) for s, n, _ in result] != [(1, n) for n in range(1, 11)]:
        raise ValueError("unexpected inferred local title sequence")
    if len({title.casefold() for _, _, title in result}) != 10 or csv_bytes(result) != raw:
        raise ValueError("invalid or non-deterministic title data")
    return result


def bundle(rows: list[tuple[int, int, str]]) -> dict:
    data = {
        "record_type": "publisher_episode_roster_proposal", "schema_version": "1.0.0",
        "batch_id": "STUDIO-MIKROS-PRODIGY-S1A-20261102", "mission_id": "pro",
        "proposal_status": "CANDIDATE_METADATA_ONLY", "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE", "coverage_effect": "NONE",
        "denominator_effect": "NONE", "roster_completeness": "UNRESOLVED",
        "listed_slot_count": len(rows),
        "observation": {
            "publisher": "Mikros Animation", "independence_group": "publisher:paramount",
            "observed_on": DATE, "primary_locator": URL, "crosscheck_locator": CROSSCHECK,
            "scope": "PUBLISHER_PAGE_TITLE_AND_SEASON_EPISODE_SLOT_ONLY",
            "response_sha256": None, "publisher_revision": None,
            "audiovisual_content_inspected": False,
        },
        "series_qid_redirect": None,
        "episode_slots": [
            {"season": season, "episode_number": episode, "title": title, "status": "CANDIDATE",
             "canonical_work_id": None, "source_binding_id": None}
            for season, episode, title in rows
        ],
    }
    roster.validate(data, roster.read_json(ROOT / "registry/mission_catalog.json"))
    return data


def index(raw: bytes, csv_data: bytes) -> dict:
    return {
        "schema_version": "1.0.0", "batch_id": "prodigy-mikros-volume1-20261102",
        "proposal_status": "CANDIDATE_METADATA_ONLY", "observed_on": DATE,
        "source_id": SOURCE_ID, "publisher": "Mikros Animation",
        "independence_group": "publisher:paramount", "source_page": URL,
        "raw_sha256": digest(raw), "raw_bytes": len(raw), "csv_sha256": digest(csv_data),
        "listed_title_count": 10,
        "ordinal_basis": "INFERRED_FROM_STUDIO_VOLUME_1_FIRST_TEN_LISTED_ORDER_NOT_NUMBERED",
        "caption_exception": caption_exception(raw),
        "title_expansions": ["slot_2_contextual_part_ii", "slot_10_contextual_part_2"],
        "crosscheck_locator": CROSSCHECK,
        "crosscheck_limit": "FIRST_TEN_VOLUME_EXISTENCE_ONLY_NO_TITLE_OR_ORDINAL_ROSTER",
        "admission_effect": "NONE", "coverage_effect": "NONE",
    }


def ingest(input_path: Path) -> None:
    # Bound the private HTML read to a regular non-symlinked file and verify
    # that the opened descriptor still identifies the lstat-inspected inode.
    # A pathname check followed by Path.read_bytes() cannot provide that gate.
    raw = source_reader.read_raw_response(input_path)
    rows = extract(raw)
    output = ROOT / BASE
    output_directory.ensure_directory(ROOT, BASE)
    output_directory.ensure_directory(ROOT, BASE / SOURCE_ID)
    ensure_no_symlink(output)
    data = csv_bytes(rows)
    safe_atomic_write(BASE / f"{SOURCE_ID}.csv", data)
    safe_atomic_write(BASE / SOURCE_ID / "bundle.json", serialize(bundle(rows)))
    safe_atomic_write(BASE / "index.json", serialize(index(raw, data)))
    check()


def check() -> None:
    output = ROOT / BASE
    for filename in ("index.json", f"{SOURCE_ID}.csv", f"{SOURCE_ID}/bundle.json"):
        ensure_no_symlink(output / filename)
    info = json.loads((output / "index.json").read_text(encoding="utf-8"))
    if not isinstance(info, dict) or set(info) != SOURCE_KEYS:
        raise ValueError("studio source receipt fields invalid")
    if any(info[key] != value for key, value in {
        "schema_version": "1.0.0", "batch_id": "prodigy-mikros-volume1-20261102",
        "proposal_status": "CANDIDATE_METADATA_ONLY", "observed_on": DATE,
        "source_id": SOURCE_ID, "publisher": "Mikros Animation",
        "independence_group": "publisher:paramount", "source_page": URL,
        "listed_title_count": 10,
        "ordinal_basis": "INFERRED_FROM_STUDIO_VOLUME_1_FIRST_TEN_LISTED_ORDER_NOT_NUMBERED",
        "crosscheck_locator": CROSSCHECK,
        "crosscheck_limit": "FIRST_TEN_VOLUME_EXISTENCE_ONLY_NO_TITLE_OR_ORDINAL_ROSTER",
        "admission_effect": "NONE", "coverage_effect": "NONE",
    }.items()):
        raise ValueError("studio source identity/epistemic flags changed")
    if info["title_expansions"] != ["slot_2_contextual_part_ii", "slot_10_contextual_part_2"]:
        raise ValueError("contextual title-expansion record changed")
    if info["caption_exception"] != {
        "title": "Starstruck", "literal_label": "Ep#103",
        "origin": "SAME_MIKROS_ARTICLE_FIGCAPTION",
        "season_ordinal_or_independence_effect": "NONE",
    }:
        raise ValueError("image-caption qualification lost or promoted")
    if (not re.fullmatch(r"[0-9a-f]{64}", str(info["raw_sha256"])) or
            type(info["raw_bytes"]) is not int or not 10_000 <= info["raw_bytes"] <= 500_000):
        raise ValueError("raw source integrity receipt malformed")
    data = (output / f"{SOURCE_ID}.csv").read_bytes()
    if digest(data) != info["csv_sha256"]:
        raise ValueError("CSV digest mismatch")
    rows = read_csv(data)
    if (output / SOURCE_ID / "bundle.json").read_bytes() != serialize(bundle(rows)):
        raise ValueError("candidate bundle stale or altered")
    print("MIKROS_PRODIGY_CHECKED: 10 title-sequence candidates; none admitted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ingest", type=Path)
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        ingest(args.ingest) if args.ingest else check()
        return 0
    except (UnicodeDecodeError, ValueError, OSError, roster.Rejected) as exc:
        print("MIKROS_PRODIGY_REJECTED:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
