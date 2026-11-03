"""Fail-closed validation of the text-only, not-yet-authorized CC BY 2.0 proposal.

This validator proves proposal/source consistency only. It cannot confer image
publication permission or substitute for independent review or browser QA.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
FOLDER = Path("proposals/visual-release/beyond-japan-premiere-ccby2-20261103")
HELD_CONTRACTS = {
    "proposals/librarian/beyond-japan-premiere-ccby-display-criteria-20261103/contract.json": "9ed8d519d8bba7ef7e605ad0d09bdcf74dd7f48c9f9c1ef829dc28772ab8e4a5",
    "explorer/beyond-premiere-release-decision.json": "b3041c0fe9ed739c1187b5d9da97e9817dfca753683ca100bd8c93263b68cd89",
}
EXPECTED_RENDITION_SHA = "e8c2933469a00fb2c8b142f41472153ed7982c05f98f9c7c154b6bea689cc06f"
EXPECTED_ORIGINAL_SHA = "7fd481633086f97e7b05e0eccbd3515a90d44f4fa7ce1255180007d9d13b4250"
ASSET_PATH = "explorer/licensed-artwork/beyond-premiere-japan-2016-960.jpg"
COMMONS_URL = "https://commons.wikimedia.org/wiki/File:Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg"
THUMB_URL = "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a4/Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg/960px-Star_Trek_Beyond_Japan_Premiere_Red_Carpet-_J._J._Abrams_%26_Simon_Pegg_%2831784488840%29.jpg"
REQUESTED_EFFECT = "APPROVE_ONE_SOURCE_SPECIFIC_CC_BY_2_0_DOCUMENTARY_PREMIERE_PHOTO_FOR_INFORMATIONAL_EXPLORER_DISPLAY"
# Immutable decision snapshot: no field in an independently reviewed version may
# silently drift. A genuine correction requires a new version and review.
EXPECTED_DECISION_SHA256 = "8df2b006b320afe5f365eae340ad9cc99ae998ae570075d1ea1b268b4c90fd81"


class ReleaseProposalRejected(ValueError):
    pass


def _load_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ReleaseProposalRejected(f"Missing or symlinked required JSON: {path}")

    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ReleaseProposalRejected(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
    if not isinstance(result, dict):
        raise ReleaseProposalRejected("Decision must be a JSON object")
    return result


def _require(expression: bool, message: str) -> None:
    if not expression:
        raise ReleaseProposalRejected(message)


def validate(root: Path = ROOT) -> str:
    folder = root / FOLDER
    expected_files = {"decision.json", "MANIFEST.md", "validate.py", "test_validate.py"}
    _require(folder.is_dir() and not folder.is_symlink(), "Release proposal directory unavailable")
    observed = list(folder.rglob("*"))
    authored = []
    for path in observed:
        relative = path.relative_to(folder)
        _require(not path.is_symlink(), "Symlink in release packet")
        if relative.parts[0] == "__pycache__":
            # Importlib may generate *untracked*, non-source bytecode in local
            # test runs. It is not part of the Git packet or review material.
            if relative.parts == ("__pycache__",):
                _require(path.is_dir(), "Python cache path changed type")
            else:
                _require(len(relative.parts) == 2 and path.is_file() and
                         re.fullmatch(r"(?:validate|test_validate)\.cpython-\d+\.pyc", path.name) is not None and
                         path.read_bytes().startswith(importlib.util.MAGIC_NUMBER),
                         "Unexpected data or executable in Python cache directory")
            continue
        _require(path.is_file() and len(relative.parts) == 1,
                 "Nested directories or payloads not permitted in text-only release packet")
        authored.append(path)
    _require({p.name for p in authored} == expected_files,
             "Unexpected/missing file in four-file text-only release packet")
    for path in authored:
        raw = path.read_bytes()
        try:
            decoded = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ReleaseProposalRejected("Non-UTF-8 binary content in text-only release packet") from exc
        _require("\x00" not in decoded and not raw.startswith((b"\xff\xd8", b"\x89PNG", b"GIF8")),
                 "Embedded binary payload in text-only release packet")
        if path.name in {"decision.json", "MANIFEST.md"}:
            _require("data:image" not in decoded.lower() and "base64," not in decoded.lower(),
                     "Embedded inline image/data payload in text-only decision")
    proposal = _load_json(folder / "decision.json")
    _require(hashlib.sha256((folder / "decision.json").read_bytes()).hexdigest() ==
             EXPECTED_DECISION_SHA256, "Versioned decision fields changed; create reviewed successor")
    manifest = folder / "MANIFEST.md"
    test_path = folder / "test_validate.py"
    _require(manifest.is_file() and not manifest.is_symlink(), "Missing MANIFEST")
    _require(test_path.is_file() and not test_path.is_symlink(), "Missing regression tests")
    _require(not any(p.is_symlink() for p in folder.rglob("*")), "Symlink in proposal")
    _require(not any(p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
                     for p in folder.rglob("*")), "No public image pixels in text-only proposal")
    _require(not (root / ASSET_PATH).exists() and not (root / ASSET_PATH).is_symlink(),
             "Public image asset present before affirmative review")

    kept = proposal["prior_held_decisions_preserved"]
    _require(isinstance(kept, list) and len(kept) == 2, "Two held authorities required")
    _require({row["path"]: row["sha256"] for row in kept} == HELD_CONTRACTS,
             "Held authority path/hash cross-binding changed")
    for row in kept:
        path = root / row["path"]
        _require(not path.is_symlink() and path.is_file(), "Held contract unavailable or symlinked")
        _require(hashlib.sha256(path.read_bytes()).hexdigest() == HELD_CONTRACTS[row["path"]],
                 "Accepted held contract bytes changed")
        _require(row["public_image_display_authorized"] is False, "Held authority reclassified")
        _require(_load_json(path)["public_image_display_authorized"] is False,
                 "Accepted source/decision is not HELD")

    _require(proposal["schema_version"] == "1.0.0", "Unexpected proposal schema")
    _require(proposal["decision_id"] == "beyond-japan-premiere-one-photo-editorial-release-v2-proposal",
             "Unexpected identity")
    _require(proposal["decision_state"] == "AFFIRMATIVE_RELEASE_PROPOSED_REVIEW_PENDING",
             "Unreviewed release status promotion")
    _require(proposal["public_image_display_authorized"] is False, "Unreviewed publication flag")
    _require(proposal["requested_effect"] == REQUESTED_EFFECT, "Proposal scope broadened")
    _require(proposal["source_local_film_id"] == "film-beyond", "Wrong film context")

    photo = proposal["photo_identity"]
    _require(photo["photographer"] == "Dick Thomas Johnson", "Photographer changed")
    _require(photo["title"] == "Star Trek Beyond Japan Premiere Red Carpet: J. J. Abrams & Simon Pegg" and
             photo["event_date"] == "2016-10-19", "Source event/title changed")
    _require(photo["commons_oldid"] == 1217252320 and
             photo["commons_file"] == COMMONS_URL, "Commons identity changed")
    _require(photo["original_flickr"] == "https://www.flickr.com/photos/31029865@N06/31784488840/",
             "Photographer source changed")
    _require(photo["original_sha256"] == EXPECTED_ORIGINAL_SHA and
             photo["original_bytes"] == 4134183 and
             photo["original_dimensions"] == [4552, 3035], "Original receipt mismatch")
    _require(photo["image_kind"] == "REAL_WORLD_JAPAN_PREMIERE_DOCUMENTARY_PHOTO_NOT_FILM_FRAME_POSTER_OR_SITE_BRANDING",
             "Film frame/branding conflation")

    asset = proposal["release_rendition"]
    _require(asset["proposed_same_origin_asset"] == ASSET_PATH, "Proposed asset path changed")
    _require(asset["upstream_thumbnail"] == THUMB_URL,
             "Thumbnail identity changed")
    _require(asset["media_type"] == "image/jpeg" and asset["dimensions"] == [960, 640] and
             asset["bytes"] == 116536 and asset["sha256"] == EXPECTED_RENDITION_SHA,
             "Photo rendition identity/bytes/dimensions changed")
    _require(asset["image_bytes_in_this_proposal"] == 0, "Public pixels not in scope")
    _require("resized" in asset["modifications_notice"].lower() and
             "no intentional crop" in asset["modifications_notice"].lower(),
             "Missing truthful modification notice")

    rights = proposal["copyright_and_other_rights"]
    _require(rights["photographer_license"] == "Creative Commons Attribution 2.0 Generic (CC BY 2.0)" and
             rights["license_url"] == "https://creativecommons.org/licenses/by/2.0/" and
             rights["license_legalcode"] == "https://creativecommons.org/licenses/by/2.0/legalcode",
             "Photo license/conditions changed")
    _require("publicity" in rights["publicity_trademark_and_backdrop_caveat"].lower() and
             "trademark" in rights["publicity_trademark_and_backdrop_caveat"].lower() and
             "endorsement" in rights["no_endorsement"].lower(),
             "Third-party rights/nonendorsement caveat omitted")
    _require(rights["no_fictional_source_or_coverage_admission"] is True,
             "Spurious Work/canon admission")

    ui = proposal["required_adjacent_visible_ui"]
    _require(ui["caption"] == "J. J. Abrams (left) and Simon Pegg (right, holding a microphone) at the October 19, 2016 Japan premiere of Star Trek Beyond. Documentary red-carpet photograph, not a film frame." and
             ui["alt"] == "J. J. Abrams and Simon Pegg at a Star Trek Beyond premiere backdrop; Pegg holds a handheld microphone." and
             ui["source_click"] == "Commons exact photo page; do not imply that clicking opens the film source",
             "UI reference identity/alt/source target changed")
    _require("not a film frame" in ui["caption"].lower() and
             ("Dick Thomas Johnson" in ui["photographer_title_source_license_and_changes"] or
              "photographer and title" in ui["photographer_title_source_license_and_changes"].lower()),
             "Missing documentary identity/adjacent credit")
    _require("Explicit visitor Show/Hide" in ui["consent"] and
             "no third-party" in ui["network"].lower(), "Opt-in/network policy changed")

    owner = proposal["owner_instruction"]
    _require("you do not need to ask for my authorization" in owner["quote"] and
             owner["does_not_waive_review"] is True, "Owner direction misrepresented")
    reviews = proposal["prior_independent_reviews_not_positive_release_approvals"]
    _require(isinstance(reviews, list) and {r["github_review_id"] for r in reviews} == {
        "PRR_kwDOT4P-988AAAABVzyYcQ", "PRR_kwDOT4P-988AAAABV0M7DA", "PRR_kwDOT4P-988AAAABV0NNpQ"
    }, "Prior review receipts missing/misattributed")
    _require(all("NO_PUBLIC_IMAGE_RELEASE" in r["disposition"] for r in reviews),
             "Prior HELD reviews laundered into approval")
    _require(all(v == "PENDING" for k, v in proposal["required_new_dispositions"].items()
                 if k != "followup_asset_ui_pr") and
             proposal["required_new_dispositions"]["followup_asset_ui_pr"] == "NOT_OPENED",
             "Unverified external approvals asserted")
    _require(proposal["coverage_effect"] == proposal["work_admission_effect"] ==
             proposal["site_effect"] == "NONE" and proposal["deletions"] == 0,
             "Protected scope expanded")
    return "TEXT_ONLY_AFFIRMATIVE_PROPOSAL_PENDING_REVIEW_NO_IMAGE_RELEASE"


if __name__ == "__main__":
    print(validate())
