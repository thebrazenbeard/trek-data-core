"""Fail-closed DS9 publisher-guide Source -> local entity -> evidence -> assertion validation.

No accepted WORK is bound. Expected SHA256 values fingerprint publisher short-description
*single-line rendered extraction*, not full episode media or an archived raw page.
"""
import json
import re
from pathlib import Path

PATH = Path(__file__).with_name("records.json")
EXPECTED_ROWS = (
    (1, "The Way Of The Warrior", "a2402655e1f69ae6fcd73e4ff17384782feb3a9e3db653abf079839df84eb387"),
    (3, "The Visitor", "e04cc987ff1db38c5370688b8bbe68b8411a6a9e1457f33575d10484dc04f955"),
    (4, "Hippocratic Oath", "c2546eeceb20b6db3667e2e0411e205563c56d46a49910f6dc311f206cce4191"),
    (5, "Indiscretion", "322f09e9efa25b0ccb3733a008782c99c7fdd5c66fa7f473985152a1e0be7a97"),
    (6, "Rejoined", "2dc49311c025e0eb23a60a8a4927a75a3b78924f03fdf5243ea16a4e6549a7e2"),
    (7, "Starship Down", "70aa1e1bfd7efba100b652bb713bbd635456751bab604243a9de348b932e409f"),
    (8, "Little Green Men", "471d8b7fc8333d525baa3f5466ad3a9b78be03e717306fcada763510fddd5ff5"),
    (9, "The Sword Of Kahless", "75bea2d8f572f4d41494095b76cb6d1098d2795102530abad72e1241a215f28a"),
    (10, "Our Man Bashir", "7d7138a4970a6f4bc203307929c212ff60c155fb1f9f5804bfbe0bf713991e55"),
    (11, "Home Front", "7e545e95dac7ff2190b37b5bc3054fcbce72e3df08fc9cfd8fc097c5a76240d2"),
    (12, "Paradise Lost", "3f873c40c6dffeafaec391804f839cdbed572ff8693d39439597a45f50f8abde"),
    (13, "Crossfire", "91b81eb419947ddab8a3225d0d32ae93a9f3be77cbc0902dc00ce065cd2b1a10"),
    (14, "Return To Grace", "c53c73930fac9106c05163182a7e437f50f53eb576b47fb9a6d6d49a1e9f1167"),
    (15, "Sons Of Mogh", "984955e0d8b0f9f33cd9fd2f52d167505a250bc7836608d8ec034dbf37451796"),
    (16, "Bar Association", "8abe562ebd30925e2033296779b280402a8f1a6895f4782d3bbe46fe9636c3e0"),
    (17, "Accession", "0d7d9d3c416a036278d13c73dd299e1cd7e25052771fe9bd9ee26c49747f1190"),
    (18, "Rules Of Engagement", "bbcc8f7919631be92eeff9433741f70a0acf3e9780170ac4aa0f50e77347e147"),
    (19, "Hard Time", "cff44b6c8df9ff553337cb7b91d37b3ccb37f5e5944c723643710c877e367100"),
    (20, "Shattered Mirror", "e7a3d5e06cd5ae53ce996e204a9fabd6b45f33afbc188cbd504c2707cc1b6630"),
    (21, "The Muse", "b5cc559fa154e8abb44285f926acbc4ba8139c7307b570f7c4e4cf824e067b4a"),
    (22, "For The Cause", "a0bf9cbea9a2581e7f6a835ee9cf2d47dadf6d25ed4f83a2895411b8321d52af"),
    (23, "To The Death", "6ee2f68c3ac700bef16dfc2dad1826dae9d6882114c46724af9442ef12351367"),
    (24, "The Quickening", "f50a58843aba76b361575f1decc55c11a5fa064dcd4560fccb4d6e29d99fb4ce"),
    (25, "Body Parts", "f5020d819ca55deb4d0cd9ab36c3bbb15bc18cac65855ce37289a953464c4425"),
)
URL = "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/4/"


def validate(batch):
    errors = []
    def check(test, note):
        if not test:
            errors.append(note)

    guards = {
        "schema_version": "1.0.0",
        "batch_id": "ds9-paramount-s4-guide-20261104",
        "role": "DS9",
        "proposal_only": True,
        "accepted_main_at_selection": "3028765359001b90bc3e6b5c1835ee283b326e91",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "episode_research_coverage_effect": "NONE",
        "synopsis_publication_effect": "NONE",
        "admitted_briefings": 0,
        "observed_card_count": 24,
        "missing_publisher_ordinals_in_extraction": [2, 26],
        "episode_census_claim": "NONE",
    }
    check(set(batch) == set(guards) | {"observed_utc_date", "source", "source_local_episode_slots", "local_entities", "evidence", "assertions", "anomaly_hypotheses"}, "unexpected or missing root field")
    expected_anomalies = [{"affected_source_ordinals": [3, 4], "hypothesis": "POSSIBLE_TITLE_DESCRIPTION_CROSS_ASSIGNMENT", "basis": "PUBLISHER_CARD_TITLE_TOPIC_VS_DESCRIPTION_ONLY", "resolution": "UNRESOLVED_NO_EXTERNAL_VERIFICATION"}]
    check(batch.get("anomaly_hypotheses") == expected_anomalies, "publisher E3/E4 anomaly hypothesis unresolved")
    for key, expected in guards.items():
        check(type(batch.get(key)) is type(expected) and batch.get(key) == expected, f"{key} guard")
    source = batch.get("source")
    if not isinstance(source, dict):
        return errors + ["source not object"]
    source_guards = {
        "source_id": "paramount-ds9-s4-guide-render-20261104",
        "publisher": "Paramount+",
        "independence_group": "publisher:paramount",
        "url": URL,
        "retrieval_date_utc": "2026-11-04",
        "retrieval_method": "TINYFISH_FETCH_CONTENT_RENDERED_MARKDOWN",
        "page_title": "Star Trek: Deep Space Nine Season 4 Episodes - Watch on Paramount+",
        "page_heading": "Season 4 > Episode Guide",
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
        {"id", "season", "source_episode_ordinal", "publisher_title", "source_card_locator", "source_description_sha256", "work_ref", "work_binding_status", "title_description_alignment"},
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
        loc = f"Season 4 > Episode Guide > {title} > S4 E{ordinal} > short description"
        expected_slot = {
            "id": f"ds9-s4-slot-{suffix}", "season": 4, "source_episode_ordinal": ordinal,
            "publisher_title": title, "source_card_locator": loc,
            "source_description_sha256": sha, "work_ref": None,
            "work_binding_status": "UNRESOLVED",
            "title_description_alignment": "SUSPECTED_MISMATCH_UNRESOLVED" if ordinal in (3, 4) else "NOT_INDEPENDENTLY_CHECKED",
        }
        for key, value in expected_slot.items():
            check(type(slot.get(key)) is type(value) and slot.get(key) == value, f"slot {ordinal} {key}")
        expected_entity = {"id": f"ds9-s4-local-card-{suffix}", "kind": "PUBLISHER_GUIDE_CARD", "slot_id": expected_slot["id"], "identity_scope": "SOURCE_LOCAL_ONLY"}
        for key, value in expected_entity.items():
            check(entity.get(key) == value, f"entity {ordinal} {key}")
        expected_ev = {
            "id": f"ds9-s4-ev-{suffix}", "kind": "PUBLISHER_SHORT_DESCRIPTION",
            "source_id": source_guards["source_id"], "local_entity_id": expected_entity["id"],
            "locator": loc, "description_sha256": sha,
            "observation": "Publisher season guide presents this title and ordinal with a short description; no episode media was read.",
        }
        for key, value in expected_ev.items():
            check(ev.get(key) == value, f"evidence {ordinal} {key}")
        expected_assertion = {
            "id": f"ds9-s4-assert-{suffix}", "predicate": "PUBLISHER_GUIDE_DESCRIBES",
            "subject_local_entity_id": expected_entity["id"],
            "supporting_evidence_id": expected_ev["id"],
            "status": "PROPOSED_SOURCE_LOCAL", "fictional_truth_scope": "NOT_OBJECTIVELY_ASSERTED",
        }
        for key, value in expected_assertion.items():
            check(assertion.get(key) == value, f"assertion {ordinal} {key}")
        paraphrase = assertion.get("original_held_paraphrase")
        check(isinstance(paraphrase, str) and 40 <= len(paraphrase) <= 260 and paraphrase.startswith(("The guide ", "The publisher guide ", "Under the title ")), f"assertion {ordinal} held attribution")
        if isinstance(paraphrase, str):
            check("i watched" not in paraphrase.lower() and "the episode proves" not in paraphrase.lower(), f"assertion {ordinal} ungrounded media/canon claim")
    return errors


if __name__ == "__main__":
    batch = json.loads(PATH.read_text(encoding="utf-8"))
    errors = validate(batch)
    if errors:
        raise SystemExit("FAILED: " + "; ".join(errors))
    print(f"PASS: {len(EXPECTED_ROWS)} held publisher cards, 24 local entities/evidence/assertions; missing guide ordinals 2 and 26 unresolved; E3/E4 alignment question held")
