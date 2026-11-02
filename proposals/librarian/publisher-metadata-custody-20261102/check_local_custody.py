#!/usr/bin/env python3
"""Replay an operator's *local* publisher-page byte/slot check.

No episode, source binding, human review or coverage is accepted by this tool.
All publisher HTML stays in the caller's private snapshot directory.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import sys


REPO = Path(__file__).resolve().parents[3]
RECEIPTS = Path(__file__).with_name("receipts.json")
MAX_SNAPSHOT_BYTES = 8 * 1024 * 1024
MAX_CANDIDATE_BYTES = 1024 * 1024
SHA = re.compile(r"sha256:[a-f0-9]{64}\Z")


class CustodyError(ValueError):
    pass


class JsonLdScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.chunks: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self.active = True
            self.chunks = []

    def handle_data(self, data: str):
        if self.active:
            self.chunks.append(data)

    def handle_endtag(self, tag: str):
        if tag == "script" and self.active:
            self.scripts.append("".join(self.chunks))
            self.active = False


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def publisher_slots(raw: bytes, expected_season: int) -> dict[int, str]:
    try:
        parser = JsonLdScripts()
        parser.feed(raw.decode("utf-8"))
        seasons = []
        for script in parser.scripts:
            item = json.loads(script)
            if item.get("@type") == "TVSeries" and isinstance(item.get("containsSeason"), dict):
                seasons.append(item["containsSeason"])
        if len(seasons) != 1:
            raise CustodyError("expected exactly one TVSeries/TVSeason JSON-LD block")
        season = seasons[0]
        if season.get("@type") != "TVSeason":
            raise CustodyError("publisher data does not identify a TVSeason")
        # Season identity must be checked against the page; a matching episode
        # title/ordinal in another season is not a match for this candidate.
        if type(expected_season) is not int or expected_season < 1:
            raise CustodyError("candidate season must be a positive integer")
        season_found = False
        if "seasonNumber" in season:
            number = season["seasonNumber"]
            if type(number) is int:
                season_number = number
            elif isinstance(number, str) and re.fullmatch(r"[0-9]+", number):
                season_number = int(number)
            else:
                raise CustodyError("malformed publisher seasonNumber")
            if season_number != expected_season:
                raise CustodyError(f"publisher seasonNumber {season_number} != expected {expected_season}")
            season_found = True
        if "name" in season:
            name = season["name"]
            if not isinstance(name, str) or not re.fullmatch(r"Season [0-9]+", name):
                raise CustodyError("publisher TVSeason name cannot identify its season number")
            named_number = int(name.split(" ", 1)[1])
            if named_number != expected_season:
                raise CustodyError(f"publisher TVSeason name {name!r} != expected Season {expected_season}")
            season_found = True
        if not season_found:
            raise CustodyError("publisher TVSeason omits an inspectable season identity")
        result = {}
        for episode in season["episode"]:
            number = episode["episodeNumber"]
            title = episode["name"]
            if (episode.get("@type") != "TVEpisode" or not isinstance(number, str)
                    or not number.isdecimal() or not isinstance(title, str)):
                raise CustodyError("malformed publisher JSON-LD episode")
            position = int(number)
            if position in result:
                raise CustodyError(f"duplicate publisher episode slot {position}")
            result[position] = title
        return result
    except (UnicodeDecodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise CustodyError("publisher JSON-LD could not be parsed") from exc


def bounded_bytes(path: Path) -> bytes:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_NONBLOCK"):
        raise CustodyError("safe no-follow input flags unavailable")
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_SNAPSHOT_BYTES:
        raise CustodyError(f"snapshot is not a bounded regular file: {path}")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as reader:
        actual = os.fstat(reader.fileno())
        if (not stat.S_ISREG(actual.st_mode)
                or actual.st_ino != info.st_ino
                or actual.st_dev != info.st_dev
                or actual.st_size > MAX_SNAPSHOT_BYTES):
            raise CustodyError(f"snapshot changed during safe open: {path}")
        data = reader.read(MAX_SNAPSHOT_BYTES + 1)
    if len(data) > MAX_SNAPSHOT_BYTES:
        raise CustodyError(f"snapshot exceeds size limit: {path}")
    return data


def bounded_candidate_bytes(relative: Path) -> bytes:
    """Read a repository candidate through no-follow directory file descriptors.

    A relative candidate path is not allowed to escape through either `..` or
    a symlinked parent.  It must be a small regular file, never a stream/FIFO.
    """
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise CustodyError("candidate path escapes accepted repository")
    if not all(hasattr(os, flag) for flag in ("O_NOFOLLOW", "O_NONBLOCK", "O_DIRECTORY")):
        raise CustodyError("safe no-follow candidate input flags unavailable")
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_NONBLOCK
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    directory_fd = None
    try:
        directory_fd = os.open(REPO, directory_flags)
        for component in relative.parts[:-1]:
            child_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        fd = os.open(relative.parts[-1], file_flags, dir_fd=directory_fd)
        with os.fdopen(fd, "rb") as reader:
            info = os.fstat(reader.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_CANDIDATE_BYTES:
                raise CustodyError(f"candidate is not a bounded regular file: {relative}")
            data = reader.read(MAX_CANDIDATE_BYTES + 1)
        if len(data) > MAX_CANDIDATE_BYTES:
            raise CustodyError(f"candidate exceeds size limit: {relative}")
        return data
    except OSError as exc:
        raise CustodyError(f"candidate cannot be read safely: {relative}") from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def check_capture(capture: dict, snapshot_dir: Path) -> dict:
    name = capture["snapshot_filename"]
    if Path(name).name != name:
        raise CustodyError("snapshot filename escapes its private directory")
    raw = bounded_bytes(snapshot_dir / name)
    if not SHA.fullmatch(capture["body_sha256"]) or sha256(raw) != capture["body_sha256"]:
        raise CustodyError(f"snapshot digest mismatch for {name}")
    if len(raw) != capture["body_octets"]:
        raise CustodyError(f"snapshot byte count mismatch for {name}")
    candidate_relative = Path(capture["candidate_path"])
    candidate_bytes = bounded_candidate_bytes(candidate_relative)
    if (not SHA.fullmatch(capture["candidate_sha256"])
            or sha256(candidate_bytes) != capture["candidate_sha256"]):
        raise CustodyError(f"candidate digest mismatch for {name}")
    candidate = json.loads(candidate_bytes)
    if (candidate["mission_id"] != capture["mission_id"]
            or candidate["observation"]["primary_locator"] != capture["url"]
            or candidate["observation"]["independence_group"] != "publisher:paramount"
            or capture["http_status"] != 200):
        raise CustodyError(f"publisher/candidate scope mismatch for {name}")
    if (candidate["accepted_work_effect"] != "NONE"
            or candidate["accepted_source_binding_effect"] != "NONE"
            or candidate["coverage_effect"] != "NONE"
            or candidate["denominator_effect"] != "NONE"):
        raise CustodyError("candidate unexpectedly claims accepted effects")
    expected = candidate["episode_slots"]
    if len(expected) != capture["candidate_slots"]:
        raise CustodyError(f"candidate slot-count changed for {name}")
    seasons = {row["season"] for row in expected}
    if len(seasons) != 1:
        raise CustodyError(f"candidate has ambiguous season scope for {name}")
    observed = publisher_slots(raw, seasons.pop())
    for row in expected:
        if observed.get(row["episode_number"]) != row["title"]:
            raise CustodyError(
                f"publisher JSON-LD slot mismatch in {name}"
                f" E{row['episode_number']}: candidate {row['title']!r},"
                f" snapshot {observed.get(row['episode_number'])!r}"
            )
    return {"mission": capture["mission_id"], "snapshot": name,
            "checked_candidate_slots": len(expected),
            "status": "LOCAL_BYTE_AND_JSONLD_SLOT_MATCH_NOT_ADMITTED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(RECEIPTS.read_text(encoding="utf-8"))
        if manifest["human_independent_review"] != "NOT_PERFORMED":
            raise CustodyError("this program cannot attest human review")
        for effect in ("accepted_work_effect", "source_binding_effect", "continuity_effect",
                       "coverage_effect", "denominator_effect", "publication_effect"):
            if manifest[effect] != "NONE":
                raise CustodyError(f"receipt illegally claims {effect}")
        results = [check_capture(c, args.snapshot_dir) for c in manifest["captures"]]
    except (CustodyError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"LOCAL_PUBLISHER_CUSTODY_REJECTED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"checks": results, "checked_total": sum(c["checked_candidate_slots"] for c in results),
                      "accepted_effect": "NONE", "human_review": "NOT_PERFORMED"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
