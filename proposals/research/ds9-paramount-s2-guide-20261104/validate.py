"""Fail-closed checks for held DS9 Paramount+ Season 2 publisher-guide cards."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "observations.json"
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/2/"
EXPECTED_TITLES = (
    "The Homecoming", "The Circle", "The Siege", "Invasive Procedures",
    "Cardassians", "Melora", "Rules Of Acquisition", "Necessary Evil",
    "Second Sight", "Sanctuary", "Rivals", "The Alternate",
    "Armageddon Game", "Whispers", "Paradise", "Shadowplay",
    "Playing God", "Profit And Loss", "Blood Oath", "The Maquis, Part 1",
    "The Maquis, Part 2", "The Wire", "Crossover", "The Collaborator",
    "Tribunal",
)


def validate(data):
    errors = []

    def insist(condition, description):
        if not condition:
            errors.append(description)

    for field, expected in {
        "schema_version": "1.0.0",
        "batch_id": "ds9-paramount-s2-guide-20261104",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "3028765",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "episode_research_coverage_effect": "NONE",
        "synopsis_publication_effect": "NONE",
        "admitted_briefings": 0,
    }.items():
        insist(type(data.get(field)) is type(expected) and data.get(field) == expected,
               f"{field}: expected {expected!r}")

    source = data.get("source")
    if not isinstance(source, dict):
        return errors + ["source must be a dictionary"]
    for field, expected in {
        "provider": "Paramount+",
        "independence_group": "publisher:paramount",
        "publisher_guide_url": URL,
        "retrieval_method": "TINYFISH_FETCH_CONTENT_RENDERED_MARKDOWN",
        "source_scope": "SEASON_2_EPISODE_GUIDE_CARDS_ONLY",
        "publisher_guide_heading": "Season 2 > Episode Guide",
        "source_body_sha256": None,
        "raw_html_bytes_pinned": False,
        "http_status_verified": False,
        "full_primary_episode_audiovisual_or_script_read": False,
    }.items():
        insist(type(source.get(field)) is type(expected) and source.get(field) == expected,
               f"source.{field}: expected {expected!r}")

    cards = data.get("source_local_cards")
    if not isinstance(cards, list):
        return errors + ["source_local_cards must be an array"]
    insist(len(cards) == len(EXPECTED_TITLES), "25 retrieved publisher cards required; no missing or invented rows")
    seen_ids = set()
    seen_ordinals = set()
    for position, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            errors.append(f"card {position} must be an object")
            continue
        insist(set(card) == {"id", "season", "episode", "official_title", "publisher_card_locator", "original_held_paraphrase"},
               f"card {position} must contain only source-local allowed fields")
        card_id = card.get("id")
        insist(isinstance(card_id, str) and card_id == f"ds9-s2-card-{position:02d}", f"card {position} id/order")
        insist(card_id not in seen_ids, f"card {position} duplicate id")
        seen_ids.add(card_id)
        insist(type(card.get("season")) is int and card["season"] == 2, f"card {position} season")
        ep = card.get("episode")
        insist(type(ep) is int and ep == position, f"card {position} episode ordinal")
        insist(ep not in seen_ordinals, f"card {position} duplicate ordinal")
        seen_ordinals.add(ep)
        title = card.get("official_title")
        insist(position <= len(EXPECTED_TITLES) and title == EXPECTED_TITLES[position - 1],
               f"card {position} publisher title")
        insist(card.get("publisher_card_locator") == f"Season 2 > Episode Guide > {title} > S2 E{position}",
               f"card {position} exact title and ordinal locator")
        paraphrase = card.get("original_held_paraphrase")
        insist(isinstance(paraphrase, str) and 30 <= len(paraphrase) <= 240,
               f"card {position} original paraphrase length")
        if isinstance(paraphrase, str):
            insist("the episode shows" not in paraphrase.lower() and "i watched" not in paraphrase.lower(),
                   f"card {position} ungrounded episode-viewing claim")
    return errors


def locator_receipt(data):
    """Digest of *our locator inventory*, explicitly not publisher page/body content."""
    lines = [data["source"]["publisher_guide_url"]]
    lines.extend(card["publisher_card_locator"] for card in data["source_local_cards"])
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    records = json.loads(DATA.read_text(encoding="utf-8"))
    findings = validate(records)
    if findings:
        raise SystemExit("FAILED: " + "; ".join(findings))
    print(f"PASS: 25 held source-local publisher cards; locator-inventory SHA256 {locator_receipt(records)}")
