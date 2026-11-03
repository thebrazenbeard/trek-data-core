"""Strict source-local TOS candidate crosswalk validator; no Work admission.

Offline validation protects original archived identifiers and separately read
Paramount card metadata against accidental or adversarial rewrites. It does not
re-fetch the publisher, authenticate historical Wikidata extraction, or watch
any episode. All checks remain active under ``python -O``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
ROW_KEYS = frozenset({
    "lead_id", "qid", "archived_title", "publisher_title", "season", "episode",
    "publisher_guide_url", "publisher_description_sha256", "title_match", "mismatch",
})
TOP_KEYS = frozenset({
    "batch_id", "role", "state", "observed_utc_date", "archived_leads_input",
    "archived_leads_sha256", "publisher_independence_family",
    "wikidata_source_independence", "published_page_reads", "rows",
    "accepted_work_effect", "accepted_source_work_binding_effect",
    "governed_coverage_effect", "explorer_publication_effect", "artwork_release_effect",
    "original_synopsis_release_effect",
})
PAGE_KEYS = frozenset({
    "season", "official_url", "reader", "lappy_direct_http_status",
    "lappy_transient_html_sha256", "raw_body_archived", "raw_body_digest_replayable",
})
PAGES = {
    1: ("https://www.paramountplus.com/shows/star_trek/episodes/1/", "82128797a9bf54cfc4128f0ce1d2e26506e578b8b317af8b43abb9983aad4dc9"),
    2: ("https://www.paramountplus.com/shows/star_trek/episodes/2/", "1be024161e1a3d7366f68f3d772db380dc3b9daf31201be79b7869d1c82a2a96"),
    3: ("https://www.paramountplus.com/shows/star_trek/episodes/3/", "c6d7c064b950e387ae704999ddffcbfd1a5ddbaec948762a0d63b74191a4da4f"),
}
# Frozen transcription pins from actual publisher S1/S2/S3 own-card reads.
# Descriptions are represented by digests, not copied publisher prose.
CARD_PINS = {
    "lead:0006": ("Q2659593", "Charlie X", 'Charlie "X"', 1, 3, "959911b9d9afbbff26c51540681ecad41a3204bb438d8dd3bc0c1314f6c3c2bc"),
    "lead:0007": ("Q2664096", "Mudd's Women", "Mudd's Women", 1, 7, "a2cfa89ae278d8d5ad29ae71acfbcda65ea400d5c3738c506ce6aa565ab92e8f"),
    "lead:0009": ("Q2984502", "The Enemy Within", "The Enemy Within", 1, 6, "16257a2a840f22807429662740ed8a143f786a23f0449d0aeee1d183c8fae9e9"),
    "lead:0010": ("Q3107459", "Dagger of the Mind", "Dagger of the Mind", 1, 10, "26826e9b9fbaee887a12425d75d0c0b54fc7465c3f085eba21a2b6c67c1a3a0a"),
    "lead:0011": ("Q3178411", "Balance of Terror", "Balance of Terror", 1, 15, "f8ede30929e5a7f0d4fb503d4bae4f8c5579553884afdfba104cad5e43548e18"),
    "lead:0012": ("Q3312529", "Mirror, Mirror", "Mirror, Mirror", 2, 4, "765ab4c99e2c07e908c30f2bb40b3c584f816db8cabefeaf73f33a2f41be858c"),
    "lead:0013": ("Q3487115", "By Any Other Name", "By Any Other Name", 2, 22, "3e54ef4e5013c9efba31cb4fd6b932a4ecd8c08fb8fccf98db321464690f76fb"),
    "lead:0014": ("Q3487125", "A Taste of Armageddon", "A Taste of Armageddon", 1, 24, "c0ae5c27590dbf6c91f62e4feb3c5c4b7d9a7620c17258f694aabcbb57f2906e"),
    "lead:0015": ("Q3487137", "Wolf in the Fold", "Wolf in the Fold", 2, 14, "e80cdfd06656e6c9279784db844383ce09d2ab64db810233eff85c48032a8d47"),
    "lead:0016": ("Q3487169", "A Private Little War", "A Private Little War", 2, 19, "8aef7ce0f3edf8d1dd4f6e56485f30b53cd587318d3cdabefe72e7ac58d080da"),
    "lead:0017": ("Q3487183", "And the Children Shall Lead", "And the Children Shall Lead", 3, 4, "610407ae77cf2ef780aa0d4cb2f38527bc70124aeb55c45f852b579e0500343f"),
    "lead:0018": ("Q3487187", "Catspaw", "Catspaw", 2, 7, "83ff1f0dfcf11af148f25c70729453ab43a95c2cc9345b9a77f9d6e184d9e07e"),
    "lead:0019": ("Q3487379", "Bread and Circuses", "Bread and Circuses", 2, 25, "475bde2223b6591f3461fe76cf3202385099e017ab1978c6beffc32f6c53f03b"),
}
LEADS_SHA = "efab937a08445f2ada98eb2b8137f05477b9002e8d462ece715925524fd35d66"


class SourceCrosswalkError(ValueError):
    """Failed source lineage, exact-card, or admission invariant."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceCrosswalkError(message)


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_strict(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def validate_payload(payload: dict, *, root: Path = ROOT) -> int:
    require(type(payload) is dict and set(payload) == TOP_KEYS, "invalid top-level fields")
    require(payload["batch_id"] == "tos-leads-official-guide-b002-20261103", "batch mismatch")
    require(payload["role"] == "LIBRARIAN" and payload["state"] == "PROPOSED_SOURCE_LOCAL_PUBLISHER_CARD_CROSSWALK", "admission state changed")
    require(payload["observed_utc_date"] == "2026-11-03", "observation date mismatch")
    require(payload["publisher_independence_family"] == "paramount_corporate_publisher_family", "source lineage changed")
    require(payload["wikidata_source_independence"] == "NOT_ESTABLISHED_FROM_ARCHIVE", "derivative independent-source inflation")
    for effect in (
        "accepted_work_effect", "accepted_source_work_binding_effect", "governed_coverage_effect",
        "explorer_publication_effect", "artwork_release_effect", "original_synopsis_release_effect",
    ):
        require(payload[effect] == "NONE", f"protected effect not NONE: {effect}")
    require(payload["archived_leads_input"] == "explorer/research-leads.json", "archived locator changed")
    lead_path = root / payload["archived_leads_input"]
    require(lead_path.is_file(), "archived lead input missing")
    require(hashlib.sha256(lead_path.read_bytes()).hexdigest() == LEADS_SHA == payload["archived_leads_sha256"], "archived lead bytes changed")
    source = load_strict(lead_path)
    require(source["lead_count"] == 218 and len(source["leads"]) == 218, "lead denominator changed")

    pages = payload["published_page_reads"]
    require(type(pages) is list and len(pages) == len(PAGES), "publisher page count changed")
    for season, item in enumerate(pages, 1):
        require(type(item) is dict and set(item) == PAGE_KEYS, "page fields changed")
        url, digest = PAGES[season]
        require(type(item["season"]) is int and item["season"] == season, "page ordinal changed")
        require(item["official_url"] == url, "page URL/host changed")
        require(item["reader"] == "DIRECT_FIRST_PARTY_RENDERED_GUIDE", "page reader changed")
        require(type(item["lappy_direct_http_status"]) is int and item["lappy_direct_http_status"] == 200, "source HTTP state changed")
        require(item["lappy_transient_html_sha256"] == digest, "dated transient source digest changed")
        require(item["raw_body_archived"] is False and item["raw_body_digest_replayable"] is False, "unarchived HTML falsely promoted")

    rows = payload["rows"]
    require(type(rows) is list and len(rows) == len(CARD_PINS) == 13, "crosswalk count changed")
    require([r.get("lead_id") for r in rows if type(r) is dict] == list(CARD_PINS), "row order or IDs changed")
    archived = source["leads"]
    require(len(archived) == 218, "archive cardinality changed")
    by_id = {f"lead:{i:04d}": lead for i, lead in enumerate(archived)}

    # These accepted input packets already hold their own crosswalks; this
    # proposal must not repackage them as new first-party observations.
    overlay = load_strict(root / "explorer/accepted-source-card-rechecks.json")
    overlapping = {r["row_id"] for r in overlay["rows"]}.intersection(CARD_PINS)
    require(not overlapping, f"already verified in accepted source-card overlay: {sorted(overlapping)}")
    first_five = load_strict(root / "proposals/librarian/lead-qualification-tos-s1-20261103/crosswalk.json")
    require({row["candidate_qid"] for row in first_five["matches"]}.isdisjoint({pin[0] for pin in CARD_PINS.values()}), "duplicate earlier TOS crosswalk")

    seen_slots = set()
    for row in rows:
        require(type(row) is dict and set(row) == ROW_KEYS, "row fields changed")
        lead_id = row["lead_id"]
        require(lead_id in CARD_PINS, f"unknown lead ID {lead_id}")
        qid, archived_title, published_title, season, episode, digest = CARD_PINS[lead_id]
        lead = by_id[lead_id]
        require(lead["episode_qid"] == qid and lead["episode_label"] == archived_title and lead["mission_id"] == "tos", "archived QID/title/series changed")
        require(lead["source_type"] == "WIKIDATA_METADATA" and lead["independence_group"] == "wikidata:wdqs", "archived source family changed")
        require(lead["verification_status"] == "UNVERIFIED_METADATA", "archived source was silently promoted")
        require(row["qid"] == qid and row["archived_title"] == archived_title and row["publisher_title"] == published_title, "crosswalk title or QID mutated")
        require(type(row["season"]) is int and type(row["episode"]) is int and (row["season"], row["episode"]) == (season, episode), "publisher slot changed")
        require((season, episode) not in seen_slots, "publisher slot reused")
        seen_slots.add((season, episode))
        require(row["publisher_guide_url"] == PAGES[season][0], "publisher URL replaced or wrong-season")
        require(row["publisher_description_sha256"] == digest, "publisher own-card description digest changed")
        if lead_id == "lead:0006":
            require(row["title_match"] == "PUNCTUATION_VARIANT_HELD" and row["mismatch"] == "ARCHIVED_CHARLIE_X_VS_PUBLISHER_CHARLIE_QUOTED_X", "Charlie X unresolved alias silently resolved")
        else:
            require(row["title_match"] == "EXACT" and row["mismatch"] is None, "spurious title resolution or mismatch")
    return len(rows)


def main() -> int:
    count = validate_payload(load_strict(BATCH / "observations.json"))
    print(f"TOS_LEAD_B002_OK:{count} (publisher source-local cards only; zero admissions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
