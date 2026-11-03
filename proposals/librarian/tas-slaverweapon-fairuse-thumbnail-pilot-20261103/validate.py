#!/usr/bin/env python3
"""Keep a case-specific visual fair-use pilot text-only, tiny, linked and unreleased."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FILES = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
MANIFEST_SHA = "cbb6229db7003c1f15f4265bf8b3823dff3d3705997f3df7199626d4ddfe2cc6"
RECORD_FINGERPRINT = "6fa2fc0591db26a0dc0fb2fdad0883e7cb1e346c4bfd1ecd8ac0f0a56eb1c394"


def require(flag: bool, cause: str) -> None:
    if not flag:
        raise ValueError(cause)


def unique_keys(pairs: list[tuple[str, object]]) -> dict:
    d = {}
    for k, v in pairs:
        require(k not in d, "duplicate metadata key")
        d[k] = v
    return d


def load(path: Path = HERE / "records.json") -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys,
                      parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))


def inventory(directory: Path = HERE) -> None:
    require(directory.is_dir() and not directory.is_symlink(), "invalid source packet directory")
    for p in directory.rglob("*"):
        relative = p.relative_to(directory)
        require(not p.is_symlink(), "symlink under packet")
        if p.is_dir():
            require(relative.parts == ("__pycache__",), "nested file directory")
            continue
        if p.is_file() and len(relative.parts) == 2 and relative.parts[0] == "__pycache__" and p.suffix == ".pyc":
            continue
        require(p.is_file() and len(relative.parts) == 1 and p.name in FILES,
                "unreviewed image, binary or file")
        require(p.stat().st_size <= 150_000, "oversized file")
        blob = p.read_bytes()
        require(not any(magic in blob for magic in (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n",
                                                     b"GIF" + b"87a", b"GIF" + b"89a", b"%" + b"PDF",
                                                     b"PK\x03\x04")), "binary magic buried in text")
        try:
            txt = blob.decode("utf-8", "strict")
        except UnicodeDecodeError as err:
            raise ValueError("non-text file") from err
        require("\x00" not in txt and not any(ord(c) < 32 and c not in "\n\r\t" for c in txt),
                "hidden control characters")
        if p.suffix in {".json", ".md"}:
            low = txt.lower()
            require(not any(x in low for x in ("data:" + "image/", "<" + "script", "<" + "image", "<!" + "doctype")),
                    "hidden inline or active media")
    require({p.name for p in directory.iterdir() if p.is_file()} == FILES, "four files exactly")
    if directory == HERE:
        prefix = HERE.relative_to(ROOT).as_posix() + "/"
        tracked = subprocess.run(["git", "ls-files", "--cached", "--", prefix], cwd=ROOT,
                                 capture_output=True, text=True, timeout=10, check=False)
        require(tracked.returncode == 0 and set(tracked.stdout.splitlines()) ==
                {prefix + f for f in FILES}, "unreviewed tracked packet changes")
    require(hashlib.sha256((directory / "MANIFEST.md").read_bytes()).hexdigest() == MANIFEST_SHA,
            "four-factor prose/context/rights change")


def validate(record: dict, root: Path = ROOT, *, directory: Path = HERE) -> None:
    require(type(record) is dict, "invalid record")
    canon = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(hashlib.sha256(canon.encode()).hexdigest() == RECORD_FINGERPRINT,
            "unknown rights/source/context mutation")
    raw = (root / record["discovery_catalog_path"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == record["discovery_catalog_sha256"],
            "accepted discovery drift")
    rows = [r for r in json.loads(raw)["rows"] if r.get("row_id") == record["source_local_episode_row_id"]]
    require(len(rows) == 1, "episode source lead identity absent/duplicate")
    row = rows[0]
    require((row["title"], row["context"], row["verification_status"], row["admission_effect"],
             row["coverage_effect"], row["identity_scope"]) ==
            ("The Slaver Weapon", "TAS S1E14", "UNVERIFIED_METADATA", "NONE", "NONE", "SOURCE_LOCAL"),
            "wrong source-local episode")
    src = record["source_binding"]
    base = ("https://images.prismic.io/star-trek-untold/"
            "01b39e29-601a-4ff5-b48d-f45a8688d4c3_theslaverweaponhd0213.jpeg")
    require(src["publisher_article_url"] == "https://www.startrek.com/news/top-animated-star-trek-episodes" and
            src["publisher_section"] == "9. The Slaver Weapon" and
            src["publisher_credit"] == "StarTrek.com" and
            src["article_image_alt"] ==
            "A weapon locks onto Sulu as he, Uhura, and Spock stand atop of a trap aboard a frozen planet set up by the Kzinti in 'The Slaver Weapon'" and
            src["copyright_holder_exact_identity"] == "UNKNOWN_NOT_ESTABLISHED" and
            src["input_embedded_variant_url"] == base + "?auto=compress%2Cformat" and
            src["input_embedded_variant_size_bytes"] == 187263 and
            src["input_embedded_variant_sha256"] ==
            "9f36424ed3cba13829cc140be686ab0e6f961a1f41f318cd4d78ffafa31416ec" and
            src["untransformed_same_path_url"] == base and
            src["untransformed_same_path_size_bytes"] == 480836 and
            src["untransformed_same_path_sha256"] ==
            "9083e38bc62d1a2d5ced92aa1805c99c2fa82b9141ff49c51f7fb1ee514679ba" and
            src["variant_dimensions"] == [1434, 1080] and
            src["same_publisher_asset_not_independent_corroboration"] is True,
            "source identity, dimensions or rights lineage altered")
    thumb = record["local_pilot_thumbnail"]
    require(thumb["format"] == "image/jpeg" and
            thumb["derive_from"] == "INPUT_EMBEDDED_VARIANT" and
            (thumb["width"], thumb["height"]) == (159, 120) and
            thumb["size_bytes"] == 2616 and
            thumb["sha256"] == "89113ca4009ff4732064863362712ff8ee1cb4d5ba72e0d4c099e60d8665f834" and
            thumb["reference_canvas_max_width"] <= 160 and
            thumb["reference_canvas_max_height"] <= 120 and
            thumb["width"] <= thumb["reference_canvas_max_width"] and
            thumb["height"] <= thumb["reference_canvas_max_height"] and
            thumb["width"] * thumb["height"] <= 19200 and
            thumb["size_bytes"] <= 4096 and
            thumb["no_crop"] is True and
            thumb["contains_full_frame_downsampled"] is True and
            thumb["metadata_exif_retained"] is False and
            thumb["derivative_binary_in_public_repo"] is False and
            thumb["derivative_binary_on_live_explorer"] is False and
            thumb["derivative_private_scratch_only"] is True,
            "thumb artifact widened/cropped/changed or publicly exposed")
    proposed = record["proposed_presentation"]
    require(proposed["purpose"] == "SOURCE_NAVIGATION_WITH_ORIGINAL_CONTEXTUAL_ANALYSIS_NOT_DECORATIVE_GALLERY" and
            proposed["linked_target"] == src["publisher_article_url"] and
            "The Slaver Weapon" in proposed["primary_caption"] and
            "not a verified episode frame extraction" in proposed["primary_caption"] and
            "2023 editorial list" in proposed["surrounding_critical_text"] and
            "observations about this published illustration" in proposed["surrounding_critical_text"] and
            "Source: John DeQuadros, StarTrek.com" in proposed["attribution_line"] and
            "not a licensed or endorsed production image" in proposed["visible_copyright_fair_use_notice"] and
            proposed["visually_label_as_research_index_not_official_trek"] is True and
            proposed["uses_original_show_logo_or_insignia_as_brand"] is False and
            proposed["access_to_original_quality"] == "OFFICIAL_SOURCE_LINK_ONLY_NO_HOSTED_FULL_SIZE" and
            proposed["automatic_hotlinking_or_proxy"] is False,
            "insufficient context/attribution/source/nonendorsement safeguards")
    law = record["legal_review"]
    require(law["status"] == "PROPOSED_INDEPENDENT_REVIEW_REQUIRED_NOT_COURT_DECISION" and
            law["factor_1_purpose_character"] == "LIMITED_FAVOR_WITH_CAVEAT_NO_ENGAGEMENT_GALLERY" and
            law["factor_2_nature_creative"] == "WEIGHS_AGAINST_FICTIONAL_ANIMATION" and
            law["factor_3_amount_substantiality"] == "MIXED_ENTIRE_SINGLE_ILLUSTRATION_AT_159_X_120_NOT_EPISODE_EXCERPT" and
            law["factor_4_market_effect"] == "UNKNOWN_MATERIAL_EDITORIAL_STILL_LICENSING_MARKET_RISK_REQUIRES_REVIEW" and
            law["licensed_publicity_image_market_independently_researched"] is False and
            law["legal_counsel_adjudication"] == "NOT_PERFORMED" and
            law["claim_of_categorical_fair_use"] is False and
            law["claim_of_categorical_no_permission_without_LICENSE"] is False,
            "false legal certainty or removed adverse factors")
    effects = record["admission"]
    require(effects["public_image_release"] == "HELD_FOR_CASE_SPECIFIC_REVIEW" and
            effects["main_explorer_change"] == effects["coverage_change"] ==
            effects["global_work_reconciliation"] == effects["site_deployment"] == "NONE" and
            effects["source_only_proposal"] is True,
            "unexpected publication or research claim")
    inventory(directory)


if __name__ == "__main__":
    validate(load())
    print("PASS: TAS 159x120 fair-use thumbnail candidate source+4 factors HELD, no binary release")
