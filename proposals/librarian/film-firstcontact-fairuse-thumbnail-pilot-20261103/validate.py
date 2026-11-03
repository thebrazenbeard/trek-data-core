#!/usr/bin/env python3
"""Exact-source, no-release guard for proposed 160x90 First Contact scene preview."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
MANIFEST_SHA = "a77a9690ae5b73cb4d19ef713562037f51be7ce3f3a4b361b2dc3b94ee7083a2"
RECORD_FINGERPRINT = "de6f60651dbbcc699093e01a6d2211a31c963f38aeeb6c630d1a3eb756dd46b2"


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError(explanation)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    record = {}
    for key, value in pairs:
        require(key not in record, "duplicate record key")
        record[key] = value
    return record


def load(path: Path = HERE / "records.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def inventory(directory: Path = HERE) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "bad packet directory")
    for path in directory.rglob("*"):
        relative = path.relative_to(directory)
        require(not path.is_symlink(), "symlink under packet")
        if path.is_dir():
            require(relative.parts == ("__pycache__",), "nested unreviewed directory")
            continue
        if path.is_file() and len(relative.parts) == 2 and relative.parts[0] == "__pycache__" and path.suffix == ".pyc":
            continue
        require(path.is_file() and len(relative.parts) == 1 and path.name in FILES,
                "image or unreviewed file under text-only proposal")
        require(path.stat().st_size <= 150_000, "oversized source file")
        blob = path.read_bytes()
        require(not any(token in blob for token in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n",
                                                     b"GIF" + b"87a", b"GIF" + b"89a",
                                                     b"PK\x03\x04", b"%" + b"PDF")),
                "binary image/container hidden in text")
        try:
            text = blob.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ValueError("non UTF-8 data") from exc
        require("\x00" not in text and not any(ord(c) < 32 and c not in "\n\r\t" for c in text),
                "hidden control bytes")
        if path.suffix in {".md", ".json"}:
            folded = text.lower()
            require(not any(t in folded for t in ("data:" + "image/", "<" + "script", "<" + "image",
                                                   "<" + "iframe", "<!" + "doctype")),
                    "embedded image or external/active page resource")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "four-file packet required")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        r = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
                           capture_output=True, text=True, timeout=10, check=False)
        require(r.returncode == 0 and set(r.stdout.splitlines()) == {prefix + f for f in FILES},
                "unexpected tracked proposal or binary")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == MANIFEST_SHA,
            "factors/context/rights prose mutation")


def validate(record: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(record) is dict, "bad records")
    canonical = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(hashlib.sha256(canonical.encode()).hexdigest() == RECORD_FINGERPRINT,
            "unreviewed records mutation")
    raw = (root / record["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == record["discovery_catalog_sha256"],
            "accepted film discovery projection changed")
    matches = [row for row in json.loads(raw)["rows"] if row.get("row_id") == record["source_local_film_row_id"]]
    require(len(matches) == 1, "film source-local row missing/duplicate")
    row = matches[0]
    require((row["title"], row["context"], row["candidate_kind"], row["medium"],
             row["verification_status"], row["identity_scope"], row["admission_effect"], row["coverage_effect"]) ==
            ("Star Trek: First Contact", "Star Trek films", "FEATURE_FILM", "FILM",
             "UNVERIFIED_METADATA", "SOURCE_LOCAL", "NONE", "NONE"),
            "false movie Work/coverage association")
    source = record["source_binding"]
    base = ("https://images.prismic.io/star-trek-untold/"
            "2e09f663-5306-43e0-b80a-2187187eef4f_STARTREK_FIRSTCONTACT_HEADER.png")
    require(source["publisher_page_url"] == "https://www.startrek.com/movies/star-trek-viii-first-contact" and
            source["publisher_page_heading"] == "Star Trek: First Contact" and
            source["publisher_film_year"] == 1996 and
            source["publisher_image_alt"] ==
            "Header image for Star Trek VIII: First Contact showing Data face-to-face with the Borg Queen" and
            source["individual_photographer_or_frame_author"] == "UNKNOWN_NOT_ESTABLISHED" and
            source["first_party_image_url"] == base + "?auto=compress%2Cformat" and
            source["delivered_image_type"] == "image/jpeg" and
            source["delivered_dimensions"] == [1430, 805] and
            source["delivered_bytes"] == 65658 and
            source["delivered_sha256"] == "51c5078fdc82e7ea7674293f3b082d8989ee4192b148a34295c237e38372afbe" and
            source["same_path_untransformed_url"] == base and
            source["untransformed_type"] == "image/png" and
            source["untransformed_dimensions"] == [1430, 805] and
            source["untransformed_bytes"] == 358259 and
            source["untransformed_sha256"] == "c2d52e6c1fb39bf026d66c0039955e757dd0ba3cf74ead17d7d39f3642b15c12" and
            source["verified_exact_film_page_scene"] is True and
            source["verified_film_runtime_frame_capture"] is False and
            source["two_delivery_variants_are_independent_sources"] is False and
            source["first_party_page_is_reuse_license"] is False,
            "publisher photo/source identity or rights assertion drift")
    thumb = record["private_thumbnail"]
    require(thumb["input_variant"] == "PUBLISHER_DELIVERED_IMAGE_JPEG" and
            thumb["output_format"] == "image/jpeg" and
            thumb["max_canvas"] == [160, 90] and thumb["actual_dimensions"] == [160, 90] and
            thumb["actual_dimensions"][0] * thumb["actual_dimensions"][1] <= 14_400 and
            thumb["actual_bytes"] == 1106 and thumb["actual_bytes"] <= 4096 and
            thumb["actual_sha256"] == "f8e1d103cfb047a392e594060b35098c8774b1ecb730b38c73429d6cb4bf6de4" and
            thumb["uncropped_full_composition"] is True and thumb["exif_retained"] is False and
            thumb["binary_committed_to_public_github"] is False and
            thumb["binary_in_live_explorer"] is False and thumb["scratch_only"] is True,
            "larger/mutated/or published thumbnail")
    display = record["proposed_use"]
    require(display["target"] == "SINGLE_SOURCE_LINKED_FILM_SEARCH_INDEX_THUMBNAIL" and
            display["one_click_source_url"] == source["publisher_page_url"] and
            "Data facing the Borg Queen" in display["visible_caption"] and
            "extraction provenance unverified" in display["visible_caption"] and
            "publisher's film-page presentation" in display["adjacent_original_commentary"] and
            "film page" in display["source_credit_line"] and
            "rights holder and individual still creator not established" in display["source_credit_line"] and
            "without any claim of publisher license or endorsement" in display["visible_fair_use_notice"] and
            display["full_size_lightbox_or_download"] is False and
            display["image_gallery_or_merchandising_use"] is False and
            display["remote_hotlink_or_image_proxy"] is False and
            display["other_show_logos_or_insignia"] is False,
            "missing source/context/rights notice or substitute-gallery function")
    law = record["legal_four_factor_review"]
    require(law["status"] == "DRAFT_INDEPENDENT_HUMAN_REVIEW_UNRESOLVED" and
            law["factor_one"] == "MIXED_NAVIGATION_CONTEXT_FAVORS_BUT_FILM_PROMO_IDENTIFICATION_PURPOSE_OVERLAP" and
            law["factor_two"] == "AGAINST_HIGHLY_CREATIVE_CINEMATIC_EXPRESSION" and
            law["factor_three"] == "MIXED_ENTIRE_FILM_PAGE_IMAGE_DOWNSAMPLED_160X90_NO_CROP" and
            law["factor_four"] == "UNKNOWN_POTENTIAL_MOVIE_PUBLICITY_THUMBNAIL_LICENSING_MARKET" and
            law["rightsholder_market_study_completed"] is False and
            law["independent_legal_or_human_review_completed"] is False and
            law["asserts_fair_use_legally_certain"] is False and
            law["asserts_license_is_always_required"] is False,
            "false copyright certainty or missing contra factors")
    effect = record["effects"]
    require(effect["public_thumbnail_release"] == "HELD_PENDING_INDEPENDENT_USE_SPECIFIC_REVIEW" and
            effect["actual_image_in_proposal"] is False and
            effect["main_explorer_change"] == effect["coverage_change"] ==
            effect["global_work_resolution"] == effect["merge_or_deploy"] == "NONE",
            "public or identity effect falsely admitted")
    inventory(directory)


if __name__ == "__main__":
    validate(load())
    print("PASS: First Contact 160x90 film still source + 4 factor draft held, no JPEG in public proposal")
