"""Fail-closed DS9 publisher-guide Source -> local entity -> evidence -> assertion validation.

No accepted WORK is bound. Expected SHA256 values fingerprint publisher short-description
*single-line rendered extraction*, not full episode media or an archived raw page.
"""
import json
import re
from pathlib import Path

PATH = Path(__file__).with_name("records.json")
EXPECTED_ROWS = (
    (1, "The Search, Part 1", "2239e6194c990403bcc26dae82340b37d7e6bdbcc49a982de59281210f0a30f4"),
    (2, "The Search, Part 2", "64986972d295297acfc242db9b1788f6f12461067311622157a9f68e69901ee5"),
    (3, "The House Of Quark", "f5126cab998bffe85024e38a104e9bdf74d7c61db35bf71cd3eb2f8d19bcdaeb"),
    (5, "Second Skin", "52c2c343bbf01d3efb983ee977f6d2154cf583dbb9c6ce1e0130e866ac94813d"),
    (6, "The Abandoned", "0f274239fc5ae206cffd5b728856788970999b2d207b609684b27ddf98f65ecd"),
    (7, "Civil Defense", "c28e2cac0a1b9656042ae2f7ac3e7fd1b85856ca386eaf8cf99f9a8decc50768"),
    (8, "Meridian", "b6d25c6b9fc0a6919af5a9ec9c0c4b0c521d8b937de289401decaade683cfbf0"),
    (9, "Defiant", "fef28b2ba6ebce3cbd78e39cbc80b0d29a952e2a7abaeb1c971a041282885a78"),
    (10, "Fascination", "07680d2e7871b08ec387f0ef3e0ba74b94e9fb35d2304c7d321310a285938ada"),
    (11, "Past Tense, Part 1", "9dc5aa84998968a9e0413f3de681eaaa49842a0da10593fba53882ad87c7a6ee"),
    (12, "Past Tense, Part 2", "bd39b5f170bd3c4521907083aa637560a5ee0fa38cfc3e7ff9a0d73fda0992cd"),
    (13, "Life Support", "6c7fa26b5ce415fd5d736279c4f50cbc590ec196dff2f35bc2de4d359d42ef18"),
    (14, "Heart Of Stone", "7a5031465bc1518cd0cacf477a0823d08dbb3f5d14d317aa5869a2cb922f8ebe"),
    (15, "Destiny", "fd215d31f084dd1e01bb45474af5e564c9e0d2021d22c708a41429fcb5c35a6d"),
    (16, "Prophet Motive", "cbc2e82e0b46851364540e9645931e9124ad7b0a84da566d534e047870778d58"),
    (17, "Visionary", "230ffc5b3a2bf6bd0c3b1f2ed728827dad6936ed06fdeca0ddf99bcea3766f6e"),
    (18, "Distant Voices", "2edc7bf21eca3ab02cdd7469e89ec179d3d7e12bbbbf568bc19fb1db12edcead"),
    (19, "Through The Looking Glass", "a5363d91ba2e35c76e9c8b3f271ebef8aa56de2aae0694c05824528f0e2f92d4"),
    (20, "Improbable Cause", "b282e9131314c546b7f08c0275b083462611bfdaf9c4e66f398c591d5dc303b6"),
    (21, "The Die Is Cast", "f8669d4afdfc463f62f538aef4f14042068eba299246732b590d138aac80cc0b"),
    (22, "Explorers", "0a558c4b4cf4f5ec11226deaea0c9880b2c1532e46cd859445c1ee71a6b39928"),
    (23, "Family Business", "89ab4ae73af7fef52f6db6495b5e9c04a102bf9fb0a678ca1df2f37ffad99786"),
    (24, "Shakaar", "09514755f0aaa0d606af2d67a270f345ae06c78357a6c9ecee36d24b92f06256"),
    (25, "Facets", "8ce37a2340dec870443121620c86c51720ef028810b136f4989bc3e140d37406"),
)
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/3/"


def validate(batch):
    errors = []
    def check(test, note):
        if not test:
            errors.append(note)

    guards = {
        "schema_version": "1.0.0",
        "batch_id": "ds9-paramount-s3-guide-20261104",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "episode_research_coverage_effect": "NONE",
        "synopsis_publication_effect": "NONE",
        "admitted_briefings": 0,
        "observed_card_count": 24,
        "missing_publisher_ordinals_in_extraction": [4, 26],
        "episode_census_claim": "NONE",
    }
    check(set(batch) == set(guards) | {"observed_utc_date", "source", "source_local_episode_slots", "local_entities", "evidence", "assertions"}, "unexpected or missing root field")
    for key, expected in guards.items():
        check(type(batch.get(key)) is type(expected) and batch.get(key) == expected, f"{key} guard")
    source = batch.get("source")
    if not isinstance(source, dict):
        return errors + ["source not object"]
    source_guards = {
        "source_id": "paramount-ds9-s3-guide-render-20261104",
        "publisher": "Paramount+",
        "independence_group": "publisher:paramount",
        "url": URL,
        "retrieval_date_utc": "2026-11-04",
        "retrieval_method": "TINYFISH_FETCH_CONTENT_RENDERED_MARKDOWN",
        "page_title": "Star Trek: Deep Space Nine Season 3 Episodes - Watch on Paramount+",
        "page_heading": "Season 3 > Episode Guide",
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
        loc = f"Season 3 > Episode Guide > {title} > S3 E{ordinal} > short description"
        expected_slot = {
            "id": f"ds9-s3-slot-{suffix}", "season": 3, "source_episode_ordinal": ordinal,
            "publisher_title": title, "source_card_locator": loc,
            "source_description_sha256": sha, "work_ref": None,
            "work_binding_status": "UNRESOLVED",
        }
        for key, value in expected_slot.items():
            check(type(slot.get(key)) is type(value) and slot.get(key) == value, f"slot {ordinal} {key}")
        expected_entity = {"id": f"ds9-s3-local-card-{suffix}", "kind": "PUBLISHER_GUIDE_CARD", "slot_id": expected_slot["id"], "identity_scope": "SOURCE_LOCAL_ONLY"}
        for key, value in expected_entity.items():
            check(entity.get(key) == value, f"entity {ordinal} {key}")
        expected_ev = {
            "id": f"ds9-s3-ev-{suffix}", "kind": "PUBLISHER_SHORT_DESCRIPTION",
            "source_id": source_guards["source_id"], "local_entity_id": expected_entity["id"],
            "locator": loc, "description_sha256": sha,
            "observation": "Publisher season guide presents this title and ordinal with a short description; no episode media was read.",
        }
        for key, value in expected_ev.items():
            check(ev.get(key) == value, f"evidence {ordinal} {key}")
        expected_assertion = {
            "id": f"ds9-s3-assert-{suffix}", "predicate": "PUBLISHER_GUIDE_DESCRIBES",
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
    print(f"PASS: {len(EXPECTED_ROWS)} held publisher cards, 24 local entities/evidence/assertions; missing guide ordinals 4 and 26 unresolved")
