"""Fail-closed DS9 publisher-guide Source -> local entity -> evidence -> assertion validation.

No accepted WORK is bound. Expected SHA256 values fingerprint publisher short-description
*single-line rendered extraction*, not full episode media or an archived raw page.
"""
import json
import re
from pathlib import Path

PATH = Path(__file__).with_name("records.json")
EXPECTED_ROWS = (
    (1, "Apocalypse Rising", "c80cf7dde78fd2058e91e5894d2d48bfc861b3f867417b90fd3967d596631b18"),
    (2, "The Ship", "7738f32bf5489f7e5571756487757a111ea843adfd22883c7cf5bff956798a2f"),
    (3, "Looking for Par'mach in All the Wrong Places", "3df461d0086ad2f54e51baca0bf1e18d08661af9674aabc73e05dcbaa668fe39"),
    (4, "...Nor The Battle To The Strong", "dfd1836ed9d6d75b43de8aa703d0c89199d9e01f1fb97acfcebe476f861b327a"),
    (5, "The Assignment", "40e99ffa58170042907d535c7ac4ea41db60e6037e045e54748723825fc2911c"),
    (6, "Trials and Tribble-ations", "aa0032b946094b2715f6d4f841cf38e83fd68fe6c6b9cd383d7fcf59899e0e5b"),
    (7, "Let He Who Is Without Sin...", "ef6cf63fc720854a832b2d18c9c38ceb4bee2a626eca231263abcf5638f94a01"),
    (8, "Things Past", "542b2ee4a99b07190b8b8a0820b8ff55044b90681064249eccabedc6822ae824"),
    (9, "The Ascent", "c70a0d33ee1c24cc648cc29093ca6778cf11f63585effede12efb185f2dae0c6"),
    (10, "Rapture", "5c929e24130dd2dfeaa437e8d85c13e48a9fc6d7383b42925c4a253d94dff800"),
    (11, "The Darkness and the Light", "4f13779e60872544961eda1255ecf3bcae6b6f035e9fedf1e33e2923ab4b91c4"),
    (13, "For the Uniform", "06641259aa2c23b497c9b7c168074ca23246dd471a398f416011f1c9122f4671"),
    (14, "In Purgatory's Shadow", "ad0d07a4e12db11e401213e10971e7aabd8943683d0f1b28473211d2d277d256"),
    (15, "By Inferno's Light", "0e64be3ebdf25a6565a9963ee99076c906769af3a23fc48be47ea88e7bdc379e"),
    (16, "Doctor Bashir, I Presume", "2c0e6898edce600cc13e557db88d4cbb5adba05c055dc032ddcc23eac6be43db"),
    (17, "A Simple Investigation", "9d8709faec30ed0af0b8f0493d75979b090896d0d9276e9c373ba8c6d85d6449"),
    (18, "Business As Usual", "912407f45b4f447b41e74feffed313e20a3cf58169b3a306de17d3c7d34957af"),
    (19, "Ties of Blood and Water", "511b9f2bb28f4f5eed832b6395f8515015857d045bfdf03bb33b440310e75ae5"),
    (20, "Ferengi Love Songs", "cec378c710ca8f609529545ce179ec6e2a2e7256df3c6833243d0533e60c5e9f"),
    (21, "Soldiers of the Empire", "23747145d6df481a51c6d66b871b551a016d04c468edda9e09dd3f55847d3d3f"),
    (22, "Children of Time", "94f74776b9edf0ff773b125724b6a91a2deb77d11aa929a55e2e3bcda87ae741"),
    (23, "Blaze of Glory", "c16e95485aa676cd06ee4cbfb496affb7a23199adbfd73c9d7634d99b9424738"),
    (24, "Empok Nor", "49792ef5e096d39491a2782ed17e8eff0808954eeec0551f7e7ce8da32c06957"),
    (25, "In the Cards", "c18ea24983296bdf3b13c320beefef90ce1d258fafce689237637eb9e45d2d5c"),
)
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/5/"


def validate(batch):
    errors = []
    def check(test, note):
        if not test:
            errors.append(note)

    guards = {
        "schema_version": "1.0.0",
        "batch_id": "ds9-paramount-s5-guide-20261104",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "episode_research_coverage_effect": "NONE",
        "synopsis_publication_effect": "NONE",
        "admitted_briefings": 0,
        "observed_card_count": 24,
        "missing_publisher_ordinals_in_extraction": [12, 26],
        "episode_census_claim": "NONE",
    }
    check(set(batch) == set(guards) | {"observed_utc_date", "source", "source_local_episode_slots", "local_entities", "evidence", "assertions"}, "unexpected or missing root field")
    for key, expected in guards.items():
        check(type(batch.get(key)) is type(expected) and batch.get(key) == expected, f"{key} guard")
    source = batch.get("source")
    if not isinstance(source, dict):
        return errors + ["source not object"]
    source_guards = {
        "source_id": "paramount-ds9-s5-guide-render-20261104",
        "publisher": "Paramount+",
        "independence_group": "publisher:paramount",
        "url": URL,
        "retrieval_date_utc": "2026-11-04",
        "retrieval_method": "TINYFISH_FETCH_CONTENT_RENDERED_MARKDOWN",
        "page_title": "Star Trek: Deep Space Nine Season 5 Episodes - Watch on Paramount+",
        "page_heading": "Season 5 > Episode Guide",
        "raw_source_body_sha256": None,
        "raw_html_bytes_pinned": False,
        "http_status_verified": False,
        "full_episode_audiovisual_or_script_read": False,
        "source_description_fingerprint_method": "SHA256_UTF8_EXTRACTED_DESCRIPTION_SINGLE_LINE_NO_TRAILING_NEWLINE",
    }
    check(set(source) == set(source_guards), "source unexpected or missing fields")
    for key, expected in source_guards.items():
        check(type(source.get(key)) is type(expected) and source.get(key) == expected, f"source.{key} guard")

    fields = ("source_local_episode_slots", "local_entities", "evidence", "assertions")
    for field in fields:
        if not isinstance(batch.get(field), list):
            return errors + [f"{field} not list"]
        check(len(batch[field]) == len(EXPECTED_ROWS), f"{field} must have 24 records")
    slots, entities, evidence, assertions = (batch[field] for field in fields)
    seen = {field: set() for field in fields}
    record_keys = (
        {"id", "season", "source_episode_ordinal", "publisher_title", "source_card_locator", "source_description_sha256", "work_ref", "work_binding_status"},
        {"id", "kind", "slot_id", "identity_scope"},
        {"id", "kind", "source_id", "local_entity_id", "locator", "description_sha256", "observation"},
        {"id", "predicate", "subject_local_entity_id", "supporting_evidence_id", "original_held_paraphrase", "status", "fictional_truth_scope"},
    )
    for field, allowed in zip(fields, record_keys):
        for i, record in enumerate(batch[field]):
            if not isinstance(record, dict):
                errors.append(f"{field}[{i}] not object")
                continue
            check(set(record) == allowed, f"{field}[{i}] unexpected fields")
            key = record.get("id")
            check(isinstance(key, str) and key not in seen[field], f"{field}[{i}] duplicate/bad id")
            seen[field].add(key)

    for index, (ordinal, title, sha) in enumerate(EXPECTED_ROWS):
        if any(len(batch[field]) <= index for field in fields):
            continue
        slot, entity, ev, assertion = (batch[field][index] for field in fields)
        if not all(isinstance(x, dict) for x in (slot, entity, ev, assertion)):
            continue
        suffix = f"{ordinal:02d}"
        loc = f"Season 5 > Episode Guide > {title} > S5 E{ordinal} > short description"
        expected_slot = {
            "id": f"ds9-s5-slot-{suffix}", "season": 5, "source_episode_ordinal": ordinal,
            "publisher_title": title, "source_card_locator": loc,
            "source_description_sha256": sha, "work_ref": None,
            "work_binding_status": "UNRESOLVED",
        }
        for key, value in expected_slot.items():
            check(type(slot.get(key)) is type(value) and slot.get(key) == value, f"slot {ordinal} {key}")
        expected_entity = {"id": f"ds9-s5-local-card-{suffix}", "kind": "PUBLISHER_GUIDE_CARD", "slot_id": expected_slot["id"], "identity_scope": "SOURCE_LOCAL_ONLY"}
        for key, value in expected_entity.items():
            check(entity.get(key) == value, f"entity {ordinal} {key}")
        expected_ev = {
            "id": f"ds9-s5-ev-{suffix}", "kind": "PUBLISHER_SHORT_DESCRIPTION",
            "source_id": source_guards["source_id"], "local_entity_id": expected_entity["id"],
            "locator": loc, "description_sha256": sha,
            "observation": "Publisher season guide presents this title and ordinal with a short description; no episode media was read.",
        }
        for key, value in expected_ev.items():
            check(ev.get(key) == value, f"evidence {ordinal} {key}")
        expected_assertion = {
            "id": f"ds9-s5-assert-{suffix}", "predicate": "PUBLISHER_GUIDE_DESCRIBES",
            "subject_local_entity_id": expected_entity["id"],
            "supporting_evidence_id": expected_ev["id"],
            "status": "PROPOSED_SOURCE_LOCAL", "fictional_truth_scope": "NOT_OBJECTIVELY_ASSERTED",
        }
        for key, value in expected_assertion.items():
            check(assertion.get(key) == value, f"assertion {ordinal} {key}")
        paraphrase = assertion.get("original_held_paraphrase")
        check(isinstance(paraphrase, str) and 40 <= len(paraphrase) <= 260 and paraphrase.startswith(("The guide ", "The publisher guide ")), f"assertion {ordinal} held attribution")
        if isinstance(paraphrase, str):
            check("i watched" not in paraphrase.lower() and "the episode proves" not in paraphrase.lower(), f"assertion {ordinal} ungrounded media/canon claim")
    return errors


if __name__ == "__main__":
    batch = json.loads(PATH.read_text(encoding="utf-8"))
    errors = validate(batch)
    if errors:
        raise SystemExit("FAILED: " + "; ".join(errors))
    print(f"PASS: {len(EXPECTED_ROWS)} held publisher cards, 24 local entities/evidence/assertions; missing guide ordinals 12 and 26 unresolved")
