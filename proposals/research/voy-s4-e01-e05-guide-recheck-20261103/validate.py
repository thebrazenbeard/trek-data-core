"""Fail-closed checker for the five HELD VOY S4 guide-card observations.

This is not an admission tool: its success means internal integrity, not that a
source was watched, an editorial synopsis approved, or a Work reconciled.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DATA = HERE / "records.json"
EXPECTED_BASE = "aebf9e8a69ab44919f2d89ab60dd1e824e05a807"
EXPECTED_CSV = "e9e8ac0cae8a30ac1c71b0c36b1d0f28b9ff9cf25d5f2a8d2875fad2e34e598e"
EXPECTED_CARDS = (
    "Scorpion, Part 2",
    "The Gift",
    "Day Of Honor",
    "Nemesis",
    "Revulsion",
)


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def unique_pairs(items: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in items:
        require(key not in out, f"duplicate JSON key {key!r}")
        out[key] = value
    return out


def keys(value: object, expected: set[str], context: str) -> None:
    require(isinstance(value, dict), f"{context} must be object")
    require(set(value) == expected, f"{context} key set drift: {set(value) ^ expected}")


def safe_repo_file(relative: str, root: Path) -> Path:
    require(relative == "proposals/discovery/publisher-season4-20261102/voy.csv", "unknown discovery CSV path")
    target = root / relative
    require(target.resolve().is_relative_to(root.resolve()), "repository path escape")
    require(target.is_file(), "discovery CSV missing")
    return target


def validate(payload: dict, root: Path = REPO) -> None:
    keys(payload, {
        "schema_version", "batch_id", "role", "base_accepted_main", "state",
        "admission_effect", "work_binding_effect", "coverage_effect",
        "denominator_effect", "full_episode_or_transcript_read",
        "raw_source_bytes_newly_custodied", "date_observed_utc",
        "source", "local_entities", "evidence", "assertions", "coverage_update",
    }, "root")
    require(payload["schema_version"] == "1.0.0", "schema drift")
    require(payload["batch_id"] == "voy-s4-e01-e05-guide-recheck-20261103", "batch drift")
    require(payload["role"] == "VOY", "role drift")
    require(payload["base_accepted_main"] == EXPECTED_BASE, "base SHA drift")
    require(payload["state"] == "HELD_SOURCE_LOCAL_PROPOSAL", "proposal status escalation")
    for key in ("admission_effect", "work_binding_effect", "coverage_effect", "denominator_effect"):
        require(payload[key] == "NONE", f"effect escalation {key}")
    require(payload["full_episode_or_transcript_read"] is False, "false full-source read")
    require(payload["raw_source_bytes_newly_custodied"] is False, "false raw-source custody")
    require(payload["date_observed_utc"] == "2026-11-03", "observation date drift")

    src = payload["source"]
    keys(src, {
        "id", "url", "type", "lineage_group", "read_representation",
        "read_locator", "new_raw_source_sha256", "existing_repo_source_receipt",
        "existing_repo_csv", "existing_repo_csv_sha256",
    }, "source")
    require(src["id"] == "paramount-us-voy-s4-guide", "source ID drift")
    url = urlparse(src["url"])
    require((url.scheme, url.netloc, url.path, url.query, url.fragment) == (
        "https", "www.paramountplus.com", "/shows/star_trek_voyager/episodes/4/", "", "",
    ), "source must be exact official S4 guide")
    require(src["type"] == "OFFICIAL_PUBLISHER_SEASON_GUIDE", "source type drift")
    require(src["lineage_group"] == "PARAMOUNT_CBS_SKYDANCE_CORPORATE", "lineage drift")
    require(src["read_representation"] == "RENDERED_HTML_GUIDE", "read representation drift")
    require(src["read_locator"] == "Season 4 > Episode Guide > first five episode cards", "source locator drift")
    require(src["new_raw_source_sha256"] is None, "raw body not newly captured")
    require(src["existing_repo_source_receipt"] == "proposals/discovery/publisher-season4-20261102/index.json", "receipt drift")
    require(src["existing_repo_csv_sha256"] == EXPECTED_CSV, "claimed CSV digest drift")
    csv_path = safe_repo_file(src["existing_repo_csv"], root)
    raw = csv_path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_CSV, "upstream discovered CSV bytes drift")
    source_rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    require(len(source_rows) >= 5, "existing publisher guide discovery missing rows")

    entities = payload["local_entities"]
    evidence = payload["evidence"]
    assertions = payload["assertions"]
    require(type(entities) is list and len(entities) == 5, "expected exactly five source-local cards")
    require(type(evidence) is list and len(evidence) == 5, "expected exactly five source-local evidence rows")
    require(type(assertions) is list and len(assertions) == 5, "expected exactly five HELD source-display assertions")
    for index, expected_title in enumerate(EXPECTED_CARDS, start=1):
        card = entities[index - 1]
        ev = evidence[index - 1]
        assertion = assertions[index - 1]
        suffix = f"s4e{index:02d}"
        keys(card, {"id", "source_id", "season", "display_ordinal", "display_title", "work_id", "evidence_id", "assertion_id", "synopsis_candidate"}, f"card {index}")
        require(card["id"] == f"voy-{suffix}-paramount-guide-card", "card ID/order mismatch")
        require(card["source_id"] == src["id"], "foreign source ID")
        require(type(card["season"]) is int and card["season"] == 4, "season drift")
        require(type(card["display_ordinal"]) is int and card["display_ordinal"] == index, "ordinal drift")
        require(card["display_title"] == expected_title, "source title drift")
        require(card["work_id"] is None, "unapproved global Work binding")
        csv_row = source_rows[index - 1]
        require(csv_row == {"season": "4", "episode_number": str(index), "title": expected_title}, "source discovery crosswalk mismatch")
        require(card["evidence_id"] == f"voy-{suffix}-guide-heading", "entity evidence foreign key drift")
        require(card["assertion_id"] == f"voy-{suffix}-source-display", "entity assertion foreign key drift")

        synopsis = card["synopsis_candidate"]
        keys(synopsis, {"text", "basis", "state", "is_original_paraphrase", "full_episode_read", "public_release"}, f"synopsis {index}")
        require(type(synopsis["text"]) is str and 35 <= len(synopsis["text"]) <= 180, "synopsis length")
        require("\n" not in synopsis["text"] and "http" not in synopsis["text"], "synopsis content unsuitable")
        require(synopsis["basis"] == "OFFICIAL_GUIDE_BRIEF_BLURB_ONLY", "synopsis source overclaim")
        require(synopsis["state"] == "HELD_FOR_HUMAN_REVIEW", "synopsis approval escalation")
        require(synopsis["is_original_paraphrase"] is True, "synopsis paraphrase status")
        require(synopsis["full_episode_read"] is False, "synopsis falsely close-read")
        require(synopsis["public_release"] is False, "unapproved public synopsis release")

        keys(ev, {"id", "source_id", "entity_id", "locator", "establishes"}, f"evidence {index}")
        require(ev["id"] == card["evidence_id"] and ev["entity_id"] == card["id"], "evidence foreign key drift")
        require(ev["source_id"] == src["id"], "evidence provenance drift")
        require(ev["locator"] == f"Season 4 > {expected_title} > S4 E{index}", "evidence locator drift")
        require(ev["establishes"] == "Publisher guide displays the title, ordinal and a brief plot blurb.", "evidence overclaim")

        keys(assertion, {"id", "predicate", "state", "evidence_ids", "scope"}, f"assertion {index}")
        require(assertion["id"] == card["assertion_id"], "assertion foreign key drift")
        require(assertion["predicate"] == "PUBLISHER_GUIDE_DISPLAYS_LOCAL_CARD", "unapproved predicate")
        require(assertion["state"] == "HELD", "assertion escalation")
        require(assertion["evidence_ids"] == [ev["id"]], "assertion support drift")
        require(assertion["scope"] == "Publisher guide display only; no canonical episode identity claim", "identity scope escalation")

    require(payload["coverage_update"] == {
        "episodes_discovered_new": 0,
        "works_created": 0,
        "source_bindings_admitted": 0,
        "close_reads": 0,
        "semantic_analysis_admitted": 0,
        "status": "NOT_ADVANCED",
    }, "coverage advancement not permitted")


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    validate(payload)
    print("PASS: five HELD VOY S4 guide cards; source-relative IDs; no admission/coverage/Work escalation")


if __name__ == "__main__":
    main()
