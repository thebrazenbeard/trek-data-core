#!/usr/bin/env python3
"""Strict source-local Discovery photo/fair-use research pilot, image withheld."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
MANIFEST_SHA = "f76ded662b2a4c77402df26ec8cc6c27662e6e8736746dd5a59e5f12515ef7d5"
RECORD_FINGERPRINT = "35772a0fe4dc4c2edb313254baac5648da5d71cdc152b7d7f5a15f4d395a0c7c"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    record = {}
    for key, value in pairs:
        require(key not in record, "duplicate JSON key")
        record[key] = value
    return record


def load(path: Path = HERE / "records.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=lambda item: (_ for _ in ()).throw(ValueError(item)))


def inventory(directory: Path = HERE) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "bad packet dir")
    for path in directory.rglob("*"):
        rel = path.relative_to(directory)
        require(not path.is_symlink(), "packet symlink")
        if path.is_dir():
            require(rel.parts == ("__pycache__",), "nested unreviewed directory")
            continue
        if path.is_file() and len(rel.parts) == 2 and rel.parts[0] == "__pycache__" and path.suffix == ".pyc":
            continue
        require(path.is_file() and len(rel.parts) == 1 and path.name in FILES,
                "unreviewed or image packet file")
        require(path.stat().st_size <= 150_000, "oversized packet")
        blob = path.read_bytes()
        require(not any(marker in blob for marker in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n",
                                                       b"GIF" + b"87a", b"GIF" + b"89a",
                                                       b"PK\x03\x04", b"%" + b"PDF")),
                "hidden binary or compressed asset")
        try:
            text = blob.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ValueError("non UTF-8 packet file") from exc
        require("\x00" not in text and not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text),
                "hidden control character")
        if path.suffix in {".md", ".json"}:
            folded = text.lower()
            require(not any(tag in folded for tag in ("data:" + "image/", "<" + "script",
                                                     "<" + "image", "<" + "iframe", "<!" + "doctype")),
                    "inline or active image/resource smuggling")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "four text files required")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        r = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
                           capture_output=True, text=True, timeout=10, check=False)
        require(r.returncode == 0 and set(r.stdout.splitlines()) == {prefix + name for name in FILES},
                "unexpected tracked image or nested file")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == MANIFEST_SHA,
            "changed source prose/copyright factors/attribution")


def validate(record: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(record) is dict, "not a record")
    canon = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(hashlib.sha256(canon.encode()).hexdigest() == RECORD_FINGERPRINT,
            "unreviewed metadata or license mutation")
    raw = (root / record["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == record["discovery_catalog_sha256"],
            "accepted discovery projection drift")
    existing = json.loads(raw)["rows"]
    require(not any(row.get("title", "").casefold() == "the red angel" or
                    row.get("context", "").casefold() in {"dsc s2e10", "dis s2e10"} for row in existing),
            "accepted Discovery Red Angel Work/source row now exists; refresh proposal")
    require(record["accepted_episode_row_for_this_title"] == "NONE_FOUND_AT_PINNED_MAIN" and
            record["proposed_source_local_id"] ==
            "proposal:startrek.com:dsc:s2e10:red-angel:photo-01:20261103" and
            record["identity_or_coverage_effect"] == "NONE", "false accepted row/coverage")
    src = record["publisher_source"]
    base = ("https://images.prismic.io/star-trek-untold/"
            "YzlhNWRhMjAtNmY3Ny00N2IwLWJlOTgtNjdhNGM0NWE1Yzk0_114701_0026b.jpg")
    require(src["article_url"] == "https://www.startrek.com/news/discovery-red-angel-images" and
            src["article_title"] == "Burnham, Pike, and Georgiou Take Center Stage in 'The Red Angel'" and
            src["article_date"] == "2019-03-21" and src["byline"] == "StarTrek.com Staff" and
            src["image_alt"] ==
            "Ethan Peck as Spock; Jayne Brook as Admiral Cornwell; Anson Mount as Captain Pike" and
            src["image_credit_exact"] == "Michael Gibson/CBS ©2018 CBS Interactive, Inc" and
            src["image_creator_credit"] == "Michael Gibson/CBS" and
            src["copyright_credit"] == "©2018 CBS Interactive, Inc" and
            src["image_role"] == "FIRST_PARTY_EPISODIC_PUBLICITY_PHOTOGRAPH_NOT_VERIFIED_BROADCAST_FRAME" and
            src["on_page_delivery_url"] ==
            base + "?auto=compress%2Cformat&h=668&rect=0%2C0%2C1000%2C668&w=1000" and
            src["delivery_format"] == "image/jpeg" and
            src["delivery_dimensions"] == [1000, 668] and src["delivery_bytes"] == 68247 and
            src["delivery_sha256"] == "18586dfa90d25c98b88771a0a6e7bc2315d8551b04d53cdace7eb24185aa2305" and
            src["same_path_no_query_url"] == base and src["no_query_format"] == "image/jpeg" and
            src["no_query_dimensions"] == [1000, 668] and src["no_query_bytes"] == 80965 and
            src["no_query_sha256"] == "054f44a1a2c6a7e09efa4b15049b647954d502fc28cc9d04ae50bf399b0174d1" and
            src["delivery_variants_are_independent_witnesses"] is False and
            src["publisher_page_is_public_reuse_license"] is False,
            "publisher visual source, photo credit or rights drift")
    thumb = record["local_thumbnail"]
    require(thumb["input_variant"] == "FIRST_PARTY_ON_PAGE_DELIVERY" and
            thumb["format"] == "image/jpeg" and thumb["canvas_max"] == [160, 110] and
            thumb["actual_dimensions"] == [160, 107] and
            thumb["actual_dimensions"][0] * thumb["actual_dimensions"][1] <= 17600 and
            thumb["actual_bytes"] == 2017 and thumb["actual_bytes"] <= 4096 and
            thumb["actual_sha256"] == "d135a3af32d3ab0098e9a4ecec7adb7342c3349cfffa4d338be6b52859a9ae48" and
            thumb["uncropped"] is True and
            thumb["publisher_pixels_in_public_repo"] is False and
            thumb["thumbnail_pixels_in_public_repo"] is False and
            thumb["thumbnail_pixels_in_live_explorer"] is False and
            thumb["private_scratch_only"] is True,
            "oversized/changed/public derivative")
    use = record["hypothetical_presentation"]
    require(use["purpose"] == "ONE_LINKED_PHOTO_REFERENCE_IN_EPISODE_SOURCE_INDEX_WITH_ORIGINAL_ANALYSIS" and
            use["visible_title"] == "The Red Angel — Discovery S2E10" and
            "publicity photo" in use["visible_caption"] and
            "not established as an exact aired-frame extraction" in use["visible_caption"] and
            "does not by itself establish what any character said" in use["adjacent_original_analysis"] and
            "Michael Gibson/CBS ©2018 CBS Interactive, Inc" in use["attribution"] and
            "fair use not determined" in use["notice"] and
            use["source_link"] == src["article_url"] and
            use["display_requires_source_link_and_analysis"] is True and
            use["gallery_or_promotional_decoration"] is False and
            use["original_resolution_hotlink_proxy_or_lightbox"] is False and
            use["full_episodic_article_images_mass_ingestion"] is False,
            "missing identity/context/attribution or widened promotional use")
    law = record["four_factor_review"]
    require(law["status"] == "HELD_FOR_INDEPENDENT_CASE_SPECIFIC_REVIEW" and
            law["factor_one"] == "MIXED_NEW_RESEARCH_SOURCE_INDEX_PURPOSE_VERSUS_IDENTICAL_STUDIO_EPISODIC_PROMOTION" and
            law["factor_two"] == "AGAINST_CREATIVE_STAGED_PUBLICITY_PHOTOGRAPH" and
            law["factor_three"] == "MIXED_COMPLETE_PHOTO_COMPOSITION_REDUCED_TO_160X107_2017_BYTES" and
            law["factor_four"] == "UNKNOWN_POTENTIAL_EPISODIC_STILL_LICENSE_MARKET_AND_AGGREGATE_EFFECT" and
            law["first_party_reuse_permission_proved"] is False and
            law["copyright_market_review_completed"] is False and
            law["independent_fair_use_review_completed"] is False and
            law["claim_automatic_legal_fair_use"] is False and
            law["claim_license_is_categorical_prerequisite"] is False,
            "false §107 certainty or removed copyright counterargument")
    effects = record["protected_effects"]
    require(effects["publication"] == "HELD" and
            effects["merge"] == effects["deploy"] == effects["accepted_source_work_join"] ==
            effects["episode_coverage"] == effects["explorer_change"] == "NONE",
            "unexpected protected effect")
    inventory(directory)


if __name__ == "__main__":
    validate(load())
    print("PASS: Discovery Red Angel photographer-credited source, 160x107 private fair-use pilot; publication HELD")
