"""Fail-closed, review-pinned source-only Ortiz print metadata observations.

The hashes pin this *proposal packet*, not remote publisher bytes or licenses.
"""
import hashlib
import json
from pathlib import Path

P = Path(__file__).with_name("observations.json")
EXPECTED = {
    "startrek:ortiz:2014-02-03:cage": ("The Cage", "https://www.startrek.com/news/four-new-star-trek-art-prints-now-available"),
    "startrek:ortiz:2013-05-01:menagerie1": ("The Menagerie: Part 1", "https://www.startrek.com/news/juan-ortiz-unveils-may-2013-tos-art-prints"),
}
EXPECTED_SOURCE_CLASS = "FIRST_PARTY_EDITORIAL_ARTWORK_PRODUCT_ANNOUNCEMENT"
EXPECTED_LIMITATIONS = [
    "Publisher text inspected; image bytes not downloaded or hashed",
    "These are artwork-product observations, not audiovisual close reading",
    "Do not merge with episode Work or count as licensed thumbnails",
    "Independent hostile reviewer and deterministic gate still required",
]
ENVELOPE_SHA256 = "553c5a04729de33a01e5984e4b0f14c15bdd35017de47c43c58cdbdfd98e7cfb"
ROW_SHA256 = {
    "startrek:ortiz:2014-02-03:cage": "7dfdea24070ebe136a2df6515b3f8933c873b9abb7ba972ae252a0bb65ee6198",
    "startrek:ortiz:2013-05-01:menagerie1": "7fb1adff8f2bcbe396d571d452370815c0ac56cff839b29c4bfe9aafc7275c89",
}
PUBLISHED = {
    "startrek:ortiz:2014-02-03:cage": "2014-02-03",
    "startrek:ortiz:2013-05-01:menagerie1": "2013-05-01",
}


def canonical_digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()

def unique_pairs(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key")
        d[k] = v
    return d

def qualify(x):
    if type(x) is not dict or set(x) != {"schema_version","batch_id","accepted_main_at_selection","proposal_only","source_class","source_family","source_access","raw_source_sha256","accepted_source_work_effect","coverage_effect","public_artwork_effect","records","limitations"}:
        raise ValueError("envelope changed")
    if x["schema_version"] != "1.0.0" or x["batch_id"] != "tos-ortiz-print-source-links-20261103" or x["proposal_only"] is not True or x["raw_source_sha256"] is not None:
        raise ValueError("source custody promotion")
    if x["accepted_main_at_selection"] != "2070b0153228272b5dd667b0a23465ff49a95a5f" or x["source_family"] != "startrek_com_editorial" or x["source_access"] != "PUBLIC_WEB_TEXT_READ_2026-11-03_NOT_AUTHENTICATED_RAW_HTML":
        raise ValueError("lineage drift")
    if x["accepted_source_work_effect"] != "NONE" or x["coverage_effect"] != "NONE" or x["public_artwork_effect"] != "NONE":
        raise ValueError("protected effect")
    if x["source_class"] != EXPECTED_SOURCE_CLASS or type(x["limitations"]) is not list or x["limitations"] != EXPECTED_LIMITATIONS:
        raise ValueError("source classification or review limitations changed")
    if canonical_digest({k: v for k, v in x.items() if k != "records"}) != ENVELOPE_SHA256:
        raise ValueError("envelope/source manifest content digest changed")
    if type(x["records"]) is not list or len(x["records"]) != 2 or not all(type(r) is dict for r in x["records"]):
        raise ValueError("records absent or malformed")
    if [r.get("source_local_id") for r in x["records"]] != list(EXPECTED):
        raise ValueError("records missing or duplicated")
    for r in x["records"]:
        if set(r) != {"source_local_id","source_url","source_published","observed_title","creator","medium","evidence","assertion","original_short_synopsis","editorial_status","artwork_rights","image_binary_included","work_identity"}:
            raise ValueError("record fields changed")
        title, url = EXPECTED[r["source_local_id"]]
        if r["observed_title"] != title or r["source_url"] != url or r["creator"] != "Juan Ortiz" or r["medium"] != "announced art print":
            raise ValueError("source binding changed")
        if r["source_published"] != PUBLISHED[r["source_local_id"]]:
            raise ValueError("published date changed")
        if r["artwork_rights"] != "HELD_NO_PUBLIC_DISPLAY_LICENSE" or r["image_binary_included"] is not False or r["work_identity"] != "UNRESOLVED" or r["editorial_status"] != "PROPOSED_SOURCE_DESCRIPTION_ONLY":
            raise ValueError("rights or work promotion")
        if not all(isinstance(r[k],str) and len(r[k]) > 30 for k in ("evidence","assertion","original_short_synopsis")):
            raise ValueError("source prose absent")
        if canonical_digest(r) != ROW_SHA256[r["source_local_id"]]:
            raise ValueError("reviewed source-row digest changed, including prose or rights claims")
    return True

if __name__ == "__main__":
    if not P.is_file() or P.is_symlink():
        raise ValueError("observations must be a regular nonsymlinked file")
    qualify(json.loads(P.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs))
    print("SOURCE_ONLY_OK: two Ortiz print leads; no artwork/Work/coverage effects")
