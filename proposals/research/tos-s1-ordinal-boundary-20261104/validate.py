"""Fail-closed, source-local TOS S1 first-five ordinal discrepancy check.

Only compares already accepted *candidate* metadata and one fresh publisher-card
observation. Nothing here assigns canonical Works, admits Sources, or covers episodes.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE_FILES = {
    "proposals/discovery/legacy-paramount-season1-20261102/tos.csv": "bb87f91381098420986b94097072a30ef0e5074b",
    "proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json": "9743f66a30520aa5007865c6ade3e163702161e5",
    "proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json": "faccc37c28e2d9784c57f98c56891e23e07bf08a",
    "proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json": "f195efb96f1b704ab991d16980eec7f46dbb9458",
}
EXPECTED_GUIDE = (
    "The Cage", "The Man Trap", 'Charlie "X"',
    "Where No Man Has Gone Before", "The Naked Time",
)
EXPECTED_PLUTO = EXPECTED_GUIDE[1:] + ("The Enemy Within",)
NO_EFFECTS = {
    "accepted_work_effect": "NONE",
    "accepted_source_binding_effect": "NONE",
    "coverage_effect": "NONE",
    "denominator_effect": "NONE",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def checked_blob(path: Path, expected_sha: str) -> bytes:
    raw = path.read_bytes()
    blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob_sha == expected_sha, f"baseline input has changed: {path}")
    return raw


def check(observation: dict, legacy_rows: list[dict], paramount: dict,
          pluto: dict, derivative: dict) -> dict:
    require(observation.get("status") == "HELD_METADATA_OBSERVATION", "receipt promoted")
    require(observation.get("role") == "TOS", "wrong role")
    require(observation.get("retrieved_date_utc") == "2026-11-04", "unanchored receipt date")
    require(observation.get("publisher") == "Paramount+", "wrong publisher")
    require(observation.get("source_url") ==
            "https://www.paramountplus.com/shows/star_trek/episodes/1/", "wrong publisher URL")
    require(observation.get("publisher_family") == "publisher:paramount", "wrong source family")
    require(observation.get("representation") == "COMPLETE_PUBLICLY_RENDERED_EPISODE_GUIDE_TEXT",
            "source representation misdescribed")
    require(observation.get("raw_html_bytes_captured") is False and
            observation.get("raw_html_sha256") is None, "unearned raw-source custody")
    require(observation.get("audiovisual_work_read_or_viewed") is False,
            "unearned episode read")
    for field in ("source_work_binding", "accepted_coverage_effect", "canonical_work_identity_effect"):
        require(observation.get(field) == "NONE", f"prohibited effect: {field}")
    require(observation.get("original_synopses_generated") == 0, "duplicate synopsis claim")

    cards = observation.get("publisher_guide_cards")
    require(isinstance(cards, list) and len(cards) == 5, "guide card count differs")
    for n, card in enumerate(cards, 1):
        title = EXPECTED_GUIDE[n - 1]
        require(card == {
            "season": 1, "episode_number": n, "title": title,
            "locator": f"Season 1 > {title} > S1 E{n}",
        }, f"publisher card mutated at E{n}")

    require(len(legacy_rows) >= 6, "accepted discovery lacks six source-local rows")
    for n, row in enumerate(legacy_rows[:6], 1):
        require(row == {"season": "1", "episode_number": str(n),
                        "title": (EXPECTED_GUIDE + ("The Enemy Within",))[n - 1]},
                f"accepted CSV diverges at E{n}")

    for label, data, titles in (("Paramount+", paramount, EXPECTED_GUIDE),
                                ("Pluto TV", pluto, EXPECTED_PLUTO)):
        require(data.get("proposal_status") == "CANDIDATE_METADATA_ONLY", f"{label} promoted")
        require(data.get("roster_completeness") == "UNRESOLVED", f"{label} coverage implied")
        require(data.get("observation", {}).get("independence_group") == "publisher:paramount",
                f"{label} falsely independent")
        require(data.get("observation", {}).get("audiovisual_content_inspected") is False,
                f"{label} viewing implied")
        require(data.get("observation", {}).get("response_sha256") is None,
                f"{label} synthetic source hash")
        for key, expected in NO_EFFECTS.items():
            require(data.get(key) == expected, f"{label} {key} promoted")
        slots = data.get("episode_slots", [])
        require(len(slots) == 5, f"{label} slot count differs")
        for n, (slot, title) in enumerate(zip(slots, titles), 1):
            require(slot == {
                "season": 1, "episode_number": n, "title": title,
                "status": "CANDIDATE", "canonical_work_id": None,
                "source_binding_id": None,
            }, f"{label} source-local slot E{n} changed")

    # The offset is a *publisher-list* discrepancy, not a certified identity map.
    require(tuple(row["title"] for row in legacy_rows[1:6]) ==
            tuple(s["title"] for s in pluto["episode_slots"]),
            "expected five-title source-local offset was lost")
    require(derivative.get("admission") == "PROPOSAL_ONLY", "derivative admitted")
    require(derivative.get("source", {}).get("authenticated_primary_av_or_studio_script") is False,
            "derivative upgraded to primary")
    work = derivative.get("work", {})
    require(work.get("official_publisher_title") == 'Charlie "X"', "derivative publisher title changed")
    require(work.get("official_publisher_rendered_heading") == 'S1 E3: Charlie "X"',
            "derivative publisher ordinal changed")
    require(work.get("derivative_site_image_caption_ordinal") == "Season 1, episode 2",
            "derivative source-relative numbering lost")
    require(work.get("ordinal_conflict") ==
            "PRESERVE_SOURCE_RELATIVE_DIFFERENCE_NO_CANONICAL_OVERRIDE",
            "derivative conflict silently reconciled")
    require(derivative.get("records", {}).get("coverage_events") == 0,
            "derivative coverage promoted")
    return {"publisher_cards_checked": 5, "csv_rows_checked": 6,
            "roster_slots_checked": 10, "source_local_ordinal_discrepancies_preserved": 2,
            "coverage_admitted": 0}


def main() -> None:
    blobs = {path: checked_blob(ROOT / path, sha) for path, sha in BASE_FILES.items()}
    legacy_rows = list(csv.DictReader(io.StringIO(blobs[next(iter(BASE_FILES))].decode("utf-8"))))
    def load(path: str) -> dict:
        return json.loads(blobs[path].decode("utf-8"))
    result = check(
        json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8")),
        legacy_rows,
        load("proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json"),
        load("proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json"),
        load("proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json"),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
