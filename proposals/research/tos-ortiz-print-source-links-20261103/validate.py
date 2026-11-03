"""Fail-closed source-only check for two Ortiz print metadata observations."""
import json
from pathlib import Path

P = Path(__file__).with_name("observations.json")
EXPECTED = {
    "startrek:ortiz:2014-02-03:cage": ("The Cage", "https://www.startrek.com/news/four-new-star-trek-art-prints-now-available"),
    "startrek:ortiz:2013-05-01:menagerie1": ("The Menagerie: Part 1", "https://www.startrek.com/news/juan-ortiz-unveils-may-2013-tos-art-prints"),
}

def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key")
        d[k] = v
    return d

def qualify(x):
    if set(x) != {"schema_version","batch_id","accepted_main_at_selection","proposal_only","source_class","source_family","source_access","raw_source_sha256","accepted_source_work_effect","coverage_effect","public_artwork_effect","records","limitations"}:
        raise ValueError("envelope changed")
    if x["schema_version"] != "1.0.0" or x["batch_id"] != "tos-ortiz-print-source-links-20261103" or x["proposal_only"] is not True or x["raw_source_sha256"] is not None:
        raise ValueError("source custody promotion")
    if x["accepted_main_at_selection"] != "2070b0153228272b5dd667b0a23465ff49a95a5f" or x["source_family"] != "startrek_com_editorial" or x["source_access"] != "PUBLIC_WEB_TEXT_READ_2026-11-03_NOT_AUTHENTICATED_RAW_HTML":
        raise ValueError("lineage drift")
    if x["accepted_source_work_effect"] != "NONE" or x["coverage_effect"] != "NONE" or x["public_artwork_effect"] != "NONE":
        raise ValueError("protected effect")
    if len(x["records"]) != 2 or {r["source_local_id"] for r in x["records"]} != set(EXPECTED):
        raise ValueError("records missing or duplicated")
    for r in x["records"]:
        if set(r) != {"source_local_id","source_url","source_published","observed_title","creator","medium","evidence","assertion","original_short_synopsis","editorial_status","artwork_rights","image_binary_included","work_identity"}:
            raise ValueError("record fields changed")
        title, url = EXPECTED[r["source_local_id"]]
        if r["observed_title"] != title or r["source_url"] != url or r["creator"] != "Juan Ortiz" or r["medium"] != "announced art print":
            raise ValueError("source binding changed")
        if r["artwork_rights"] != "HELD_NO_PUBLIC_DISPLAY_LICENSE" or r["image_binary_included"] is not False or r["work_identity"] != "UNRESOLVED" or r["editorial_status"] != "PROPOSED_SOURCE_DESCRIPTION_ONLY":
            raise ValueError("rights or work promotion")
        if not all(isinstance(r[k],str) and len(r[k]) > 30 for k in ("evidence","assertion","original_short_synopsis")):
            raise ValueError("source prose absent")
    return True

if __name__ == "__main__":
    qualify(json.loads(P.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs))
    print("SOURCE_ONLY_OK: two Ortiz print leads; no artwork/Work/coverage effects")
