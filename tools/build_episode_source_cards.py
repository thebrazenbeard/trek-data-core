#!/usr/bin/env python3
"""Deterministic HELD publisher-guide card shelf, separate from Work coverage.

Only source-local title, slot, publisher URL and utterance labels are exposed.
All four accepted original validators run on strictly parsed, SHA-pinned inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("explorer/episode-source-cards.json")
INPUTS = (
    ("PIC-FIRST5", "PIC", Path("proposals/research/pic/picard-s1-first5-guide-cards-20261103/records.json"),
     "070dccdbda3b7a777e6f12201d725bd906610f4e1c5ee26e8c37c3a218c6829f"),
    ("PIC-LAST5", "PIC", Path("proposals/research/pic/picard-s1-last5-guide-cards-20261103/records.json"),
     "fe962cc235ffc84f5cff7a970a940419cf9a21dce72cd5844cae76ce89f9a9cc"),
    ("SNW-FIRST5", "SNW", Path("proposals/research/snw/s3-publisher-first5-20261103/records.json"),
     "89e816d651996405dce608fa3509b437178b0dcd635f2d8635962d0bd7acfe1c"),
    ("SNW-LAST5", "SNW", Path("proposals/research/snw/s3-publisher-last5-20261103/records.json"),
     "b1daa95e849c61beb1011aabaebc06343589f29d0ec786e6359c07cb81137b2e"),
)
# These are independent code-owned per-row digests, not hashes supplied by the
# sidecar. Adding an accepted research packet requires an explicit code review.
ROW_PINS = {
    'episode-publisher-card:pic-s1-e01-pplus-guide': 'f51bfb20a4ead24c385f58eb1b27e10f009a33a23c0ea750e9064491cad16437',
    'episode-publisher-card:pic-s1-e02-pplus-guide': 'c34d10361d732b1ac52b47d0e3de21d54d795e2ee071861ff517368143791ef0',
    'episode-publisher-card:pic-s1-e03-pplus-guide': '6019771599ba29b09972270896e1e114b9d5cea0695d2a38a1450cf702de54ea',
    'episode-publisher-card:pic-s1-e04-pplus-guide': '81b40dc6f56591b2ba2513fd65ef1e32fb1d9963ba2914944ce201e8cc1073ac',
    'episode-publisher-card:pic-s1-e05-pplus-guide': 'a296c1f5f8f7135edb5d9ce8fd3a0448f893153a926cd0c0828b2ac3645d5bac',
    'episode-publisher-card:pic-s1-e06-pplus-guide': 'a41d54df655e8355201b6cc915b71e8e4c4a4e68fb5666d9536bb91e73038e94',
    'episode-publisher-card:pic-s1-e07-pplus-guide': '8232be2a96706345b47201b1f69619e0b7685622fe7f291c3de1054115b4ed85',
    'episode-publisher-card:pic-s1-e08-pplus-guide': '870e7d2e15d5ff5060bf284cc2f43e16a61f06a203727aec5b49988204379b3f',
    'episode-publisher-card:pic-s1-e09-pplus-guide': '44548891f027e46fbe4abce5feca6db6369cc1f211c17b8f86de153122d4e52f',
    'episode-publisher-card:pic-s1-e10-pplus-guide': '96ddbc5acee23c010165b7419fc8ade2b8b6df20a8076afddf3eb63909907f6e',
    'episode-publisher-card:snw-s3-e01-pplus': '323bc58b9407611062446cd4d0d7b81bcc9e312f34a701769e6646c26619a212',
    'episode-publisher-card:snw-s3-e02-pplus': '43b57e7fa9502592ddcbe3009373e8870567e5086cc7fffbb707514954f29853',
    'episode-publisher-card:snw-s3-e03-pplus': '53442cb03b6bba66c1e299e13fde8647d823dcce59934f7d3d00c0756fde3187',
    'episode-publisher-card:snw-s3-e04-pplus': '1a2c43097d9b3cffbe2f87d3c6315c93b41af5f3af42aa949b9328dc010a3a9c',
    'episode-publisher-card:snw-s3-e05-pplus': '0c686b7d8ae284f6780fb22fd2eea2b1ca5cc717a10c66e874afd4f25d37d59c',
    'episode-publisher-card:snw-s3-e06-pplus': '7c7db2b3a80e0f5ec27102629bbed5838cdb9e93033e923e6d47bbe0830981a8',
    'episode-publisher-card:snw-s3-e07-pplus': 'a3061ed210473a7509efbb3a8b91fb97bf1d091738f14f0671990bd932fed729',
    'episode-publisher-card:snw-s3-e08-pplus': 'bbf24562eff13ed7d80de7d85826b044b38ab9937105529cd89000b5e43799e1',
    'episode-publisher-card:snw-s3-e09-pplus': '1deab9b089faf472150e047899facdf92800c96a4049e674c23e5876423b3a9b',
    'episode-publisher-card:snw-s3-e10-pplus': 'ba3cce43a528dd8d6a6f994bf4a24a3acdb1f507461f50bf21118ad834be617f',
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode(obj: dict) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate accepted source JSON key: {key}")
        obj[key] = value
    return obj


def require(ok: bool, reason: str):
    if not ok:
        raise ValueError("EPISODE_SOURCE_CARDS_REJECTED: " + reason)


def accepted_source(path: Path, pinned: str, lane: str) -> dict:
    source = ROOT / path
    validator = source.with_name("validate.py")
    for target in (source, validator):
        require(target.is_file() and not target.is_symlink() and target.stat().st_size < 100_000,
                f"missing, linked or oversized original input/validator: {target}")
    raw = source.read_bytes()
    require(digest(raw) == pinned, f"reviewed complete input SHA changed: {path}")
    packet = json.loads(raw, object_pairs_hook=unique_pairs)
    require(type(packet) is dict and packet.get("proposal_only") is True,
            f"accepted research source scope changed: {path}")
    for key in ("accepted_source_binding_effect", "accepted_work_effect", "coverage_effect", "denominator_effect"):
        require(packet.get(key) == "NONE", f"source {key} promoted: {path}")
    namespace = runpy.run_path(str(validator))
    if lane == "PIC":
        require(callable(namespace.get("validate")), "original Picard validator unavailable")
        namespace["validate"](packet, repo=ROOT)
        require(packet["source"]["full_primary_audiovisual_content_read"] is False,
                "Picard full episode was not inspected")
    else:
        require(callable(namespace.get("validate_records")), "original SNW validator unavailable")
        require(namespace["validate_records"](packet) == 5, "original SNW source validator count changed")
        require(packet.get("explorer_effect") == "NONE" and
                packet.get("audiovisual_content_inspected") is False and
                packet.get("full_primary_source_available") is False,
                "SNW source cannot be elevated into Explorer or a viewed episode")
    return packet


def guide_url(url: str, lane: str) -> str:
    require(type(url) is str, "source guide URL missing")
    parsed = urlsplit(url)
    required = ("/shows/star-trek-picard/episodes/1/" if lane == "PIC"
                else "/shows/star-trek-strange-new-worlds/episodes/3/")
    require(parsed.scheme == "https" and parsed.netloc == "www.paramountplus.com" and
            parsed.path == required and not (parsed.query or parsed.fragment or parsed.username or parsed.password),
            "unexpected source guide URL")
    return url


def mention_tag(label: str) -> str:
    require(type(label) is str and 1 <= len(label) <= 80 and "<" not in label and ">" not in label,
            "invalid publisher source-local mention")
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    require(1 <= len(slug) <= 80, "empty mention tag")
    return "publisher-utterance:" + slug


def compile_rows(*, enforce_pins: bool = True):
    rows, receipts, seen = [], [], set()
    for batch, lane, path, pinned in INPUTS:
        packet = accepted_source(path, pinned, lane)
        receipts.append({"batch": batch, "path": path.as_posix(), "sha256": pinned})
        src = packet["source"]
        url = guide_url(src["url"] if lane == "PIC" else src["url"], lane)
        require(src["independence_group"] == "publisher:paramountplus.com", "same publisher family lost")
        if lane == "PIC":
            cards = packet["source_local_episode_cards"]
            require(len(cards) == 5, "Picard packet length drift")
            iterator = ((c["local_id"], c["season"], c["episode_number"], c["title"],
                         c["literal_name_mentions"], {"card": c}) for c in cards)
        else:
            cards = packet["works"]
            require(len(cards) == 5, "SNW packet length drift")
            grouped = {}
            for entity in packet["local_entities"]:
                # A generic editorial role description is not necessarily a
                # literal term in the source. Do not publish it as a quote tag.
                if entity["label"].startswith("unnamed "):
                    continue
                grouped.setdefault(entity["work_id"], []).append(entity["label"])
            evidence = {e["work_id"]: e for e in packet["evidence"]}
            assertions = {a["work_id"]: a for a in packet["assertions"]}
            artwork = {a["work_id"]: a for a in packet["artwork_candidates"]}
            iterator = ((c["local_work_id"], c["season"], c["episode_number"], c["title"],
                         grouped.get(c["local_work_id"], []),
                         {"card": c, "evidence": evidence[c["local_work_id"]],
                          "assertion": assertions[c["local_work_id"]],
                          "artwork": artwork[c["local_work_id"]],
                          "entities": [e for e in packet["local_entities"] if e["work_id"] == c["local_work_id"]]})
                        for c in cards)
        for local_id, season, episode, title, labels, source_fragment in iterator:
            require(type(local_id) is str and re.fullmatch(r"(?:pic|snw)-s\d-e\d\d-pplus(?:-guide)?", local_id),
                    "invalid source-local episode ID")
            require(type(season) is int and season == (1 if lane == "PIC" else 3) and
                    type(episode) is int and 1 <= episode <= 10 and
                    type(title) is str and 1 <= len(title) <= 100 and
                    "<" not in title and ">" not in title,
                    "source-local title or ordinal invalid")
            require(f"-s{season}-e{episode:02d}-" in local_id and local_id not in seen,
                    "cross-batch duplicate / misbound episode slot")
            require(type(labels) is list and len(labels) <= 12 and
                    all(type(label) is str for label in labels), "publisher mention labels invalid")
            seen.add(local_id)
            labels = list(dict.fromkeys(labels))
            tags = sorted([f"series:{lane.lower()}", f"season:{season}",
                           f"slot:s{season}e{episode:02d}", "publisher:paramountplus.com",
                           "source-status:held"] + [mention_tag(label) for label in labels])
            row = {
                "row_id": f"episode-publisher-card:{local_id}", "source_local_id": local_id,
                "series_code": lane,
                "series_title": ("Star Trek: Picard" if lane == "PIC"
                                 else "Star Trek: Strange New Worlds"),
                "season": season, "episode": episode, "title": title,
                "publisher_utterance_labels": labels, "tags": tags,
                "publisher_guide_url": url,
                "source_batch": batch, "source_input": path.as_posix(), "source_input_sha256": pinned,
                "publisher_family": "publisher:paramountplus.com",
                "source_status": "HELD_PUBLISHER_GUIDE_ONLY",
                "source_identity_scope": "SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK",
                "full_episode_read": False, "work_admission_effect": "NONE",
                "coverage_effect": "NONE", "synopsis_release_effect": "NONE",
                "artwork_release_effect": "NONE",
            }
            # Pin complete *underlying card evidence*, including nonpublished
            # video/image locators. Same-host video swaps with unchanged public
            # titles, tags and batch totals must still fail closed.
            row_sha = digest(encode({"projection": row, "original_source_fragment": source_fragment}))
            if enforce_pins:
                require(ROW_PINS.get(row["row_id"]) == row_sha,
                        f"independent code-owned row digest changed: {local_id}")
            row["source_row_sha256"] = row_sha
            rows.append(row)
    require(len(rows) == len(seen) == 20 and
            {row["series_code"] for row in rows} == {"PIC", "SNW"} and
            len([r for r in rows if r["series_code"] == "PIC"]) == 10,
            "twenty exact publisher source-local cards were not recovered")
    rows.sort(key=lambda row: (row["series_code"], row["season"], row["episode"]))
    return rows, receipts


def build():
    rows, receipts = compile_rows()
    return {"schema_version": "1.0.0", "data_status": "HELD_SOURCE_LOCAL_PUBLISHER_EPISODE_CARDS",
            "row_count": 20, "series_count": 2, "publisher_independence_group_count": 1,
            "full_episodes_viewed": 0, "works_admitted": 0, "synopses_released": 0,
            "artwork_released": 0, "admission_effect": "NONE", "coverage_effect": "NONE",
            "source_input_receipts": receipts, "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = encode(build())
    target = ROOT / OUTPUT
    require(not target.is_symlink(), "symlink output path refused")
    if args.check:
        require(target.is_file() and target.read_bytes() == data, "stale or poisoned episode shelf")
    else:
        target.write_bytes(data)
    print("EPISODE_SOURCE_CARDS_OK: 20 validated HELD publisher-card observations; 0 Work, coverage, synopsis, art effects")


if __name__ == "__main__":
    main()
