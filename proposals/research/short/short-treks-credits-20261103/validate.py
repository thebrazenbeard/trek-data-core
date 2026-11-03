"""Strict, source-local Short Treks credit observation checks.

This checks internal transcription/lineage/holds, not video viewing, page-byte
custody, publisher authenticity, image permission, or Work admission.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECORDS = HERE / "observations.json"
EXISTING = {
    "accepted_description_observations_sha256": (
        "proposals/research/short/publisher-synopses-20261103/observations.json",
        "91862225de0740c18b545de84efb4c9c84b0538d00888a55c4af1f78e3f2fd96",
    ),
    "accepted_2019_cohort_records_sha256": (
        "proposals/research/short/short-treks-2019-cohort-20261103/records.json",
        "edbf4f0b50e2c4506cd6a5d54760761bdf38db18c179a223e14fc28610312526",
    ),
}
SOURCE = {
    "startrek:2018:shorts-credits": (
        "https://www.startrek.com/news/short-treks-schedule-revealed",
        "2018-09-20", "image:2018:article-banner",
        "article credit lines 47-66; 2026-11-03 web retrieval",
    ),
    "startrek:2020:shorts-credits": (
        "https://www.startrek.com/news/star-trek-short-treks-now-streaming-on-youtube",
        "2020-08-17", "image:2020:article-banner",
        "article credit lines 46-52; web canonical redirect /en-un/; 2026-11-03 retrieval",
    ),
    "startrek:2020:shorts-home-video": (
        "https://www.startrek.com/news/announcing-star-trek-short-treks-release-on-blu-ray-and-dvd",
        "2020-03-15", "image:2020:home-video-banner",
        "home-video article lines 40-54, exact nine-item package list; 2026-11-03 retrieval",
    ),
}
IMAGES = {
    "image:2018:article-banner": "https://images.prismic.io/star-trek-untold/NWE0YmE4MWQtMTVjNS00ZTlkLWE2MmMtYWEwNjg5ZGZkNWI3_baed9f51d412c2514ee46a0942138ad6.jpeg?auto=compress%2Cformat&h=1178&rect=0%2C0%2C2800%2C1178&w=2800",
    "image:2020:article-banner": "https://images.prismic.io/star-trek-untold/NGM5ODdlZjMtZWNmMC00MTFhLTlmNzYtOWM2ODY5MDcxNzIy_star_trek_short_treks_fyc.jpg?auto=format%2Ccompress",
    "image:2020:home-video-banner": "https://images.prismic.io/star-trek-untold/MDMxNjg3MGUtZDlmZS00MjI5LThmMmEtNjIxOTY1YTQ3N2I3_shorttreks_blueray_002.png?auto=compress%2Cformat&h=1080&rect=0%2C0%2C2000%2C1080&w=2000",
}
EXPECTED = [
    ("Runaway", "startrek:2018:shorts-credits", ("Jenny Lumet", "Alex Kurtzman"), (), (), ("Maja Vrvilo",)),
    ("Calypso", "startrek:2018:shorts-credits", (), ("Michael Chabon",), ("Sean Cochran", "Michael Chabon"), ("Olatunde Osunsanmi",)),
    ("The Brightest Star", "startrek:2018:shorts-credits", ("Bo Yeon Kim", "Erika Lippoldt"), (), (), ("Douglas Aarniokoski",)),
    ("The Escape Artist", "startrek:2018:shorts-credits", ("Michael McMahan",), (), (), ("Rainn Wilson",)),
    ("Q&A", "startrek:2020:shorts-credits", ("Michael Chabon",), (), (), ("Mark Pellington",)),
    ("The Trouble with Edward", "startrek:2020:shorts-credits", ("Graham Wagner",), (), (), ("Daniel Gray Longino",)),
    ("Ask Not", "startrek:2020:shorts-credits", ("Kalinda Vazquez",), (), (), ("Sanji Senaka",)),
    ("The Girl Who Made the Stars", "startrek:2020:shorts-credits", ("Brandon Schultz",), (), (), ("Olatunde Osunsanmi",)),
    ("Ephraim and Dot", "startrek:2020:shorts-credits", ("Chris Silvestri", "Anthony Maranville"), (), (), ("Michael Giacchino",)),
    ("Children of Mars", "startrek:2020:shorts-credits", ("Kirsten Beyer", "Jenny Lumet", "Alex Kurtzman"), (), (), ("Mark Pellington",)),
]


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def exact_keys(row: object, keys: set[str], label: str) -> None:
    need(type(row) is dict and set(row) == keys, f"{label} fields changed")


def pairs_no_duplicates(pairs):
    out = {}
    for key, val in pairs:
        need(key not in out, f"duplicate JSON key: {key}")
        out[key] = val
    return out


def strict_file(path: Path) -> bytes:
    need(path.is_file() and not path.is_symlink(), f"nonregular file: {path}")
    for parent in (path, *path.parents):
        need(not parent.is_symlink(), "symlink in source path")
        if parent == ROOT:
            break
    need(path.resolve().is_relative_to(ROOT), "source outside repo")
    payload = path.read_bytes()
    need(0 < len(payload) < 100000, "source file size not bounded")
    return payload


def validate(data: dict) -> int:
    exact_keys(data, {"schema_version", "proposal_only", "observed_on_utc", "evidence_class",
                      "source_family", "independent_upstream_families", "source_bound",
                      "audiovisual_viewed", "work_identity_effect", "admission_effect",
                      "coverage_effect", "explorer_effect", "synopsis_release_effect",
                      "artwork_release_effect", *EXISTING.keys(), "sources",
                      "page_level_artwork_leads", "edition_container_lead", "credits"}, "root")
    need(data["schema_version"] == "trek-short-credits-first-party-v1", "schema mismatch")
    need(data["proposal_only"] is True and data["observed_on_utc"] == "2026-11-03", "proposal/date mismatch")
    need(data["evidence_class"] == "FIRST_PARTY_ARTICLE_CREDIT_FIELDS_READ_NOT_SHORT_VIEWED", "evidence inflated")
    need(data["source_family"] == "publisher:paramount-cbs-startrek" and data["independent_upstream_families"] == 1, "independence inflated")
    need(data["source_bound"] is False and data["audiovisual_viewed"] is False, "AV source custody falsely promoted")
    for key in ("work_identity_effect", "admission_effect", "coverage_effect", "explorer_effect", "synopsis_release_effect", "artwork_release_effect"):
        need(data[key] == "NONE", f"protected effect: {key}")
    for key, (relpath, digest) in EXISTING.items():
        need(data[key] == digest, f"accepted source SHA pin changed: {key}")
        need(hashlib.sha256(strict_file(ROOT / relpath)).hexdigest() == digest, f"accepted source moved: {key}")

    sources = data["sources"]
    need(type(sources) is list and len(sources) == 3, "source count changed")
    need({s.get("id") for s in sources if type(s) is dict} == set(SOURCE), "sources changed")
    for s in sources:
        exact_keys(s, {"id", "url", "article_published", "read_locator", "read_state", "raw_html_archived", "artwork_lead_id"}, "source")
        need((s["url"], s["article_published"], s["artwork_lead_id"], s["read_locator"]) == SOURCE[s["id"]], "source identity/URL/locator mismatch")
        need(s["read_state"] == "DIRECT_RENDERED_FIRST_PARTY_HTML_AND_LAPPY_HTTP_200" and s["raw_html_archived"] is False, "source access overstated")

    leads = data["page_level_artwork_leads"]
    need(type(leads) is list and len(leads) == 3, "art lead count changed")
    need({item.get("id") for item in leads if type(item) is dict} == set(IMAGES), "art IDs changed")
    for lead in leads:
        exact_keys(lead, {"id", "source_id", "url", "scope", "bytes_retrieved", "display_rights"}, "image lead")
        need(lead["url"] == IMAGES[lead["id"]], "image locator changed")
        need(lead["source_id"] in SOURCE and SOURCE[lead["source_id"]][2] == lead["id"], "image/source mismatch")
        need(lead["scope"] == ("HOME_VIDEO_ARTICLE_BANNER_NOT_SINGLE_EPISODE_POSTER" if lead["id"] == "image:2020:home-video-banner" else "ARTICLE_BANNER_NOT_EPISODE_STILL"), "image scope promoted")
        need(lead["bytes_retrieved"] is False and lead["display_rights"] == "UNKNOWN_HELD", "unproven art release")

    edition = data["edition_container_lead"]
    exact_keys(edition, {"source_id", "media", "publisher_announced_us_date", "publisher_article_nine_titles", "claim_scope", "work_binding"}, "edition")
    need(edition["source_id"] == "startrek:2020:shorts-home-video", "edition source mismatch")
    need(edition["media"] == ["BLU_RAY", "DVD"] and edition["publisher_announced_us_date"] == "2020-06-02", "edition format/date mismatch")
    need(edition["publisher_article_nine_titles"] == ["Runaway", "Calypso", "The Brightest Star", "The Escape Artist", "Q&A", "The Trouble With Edward", "Ask Not", "Ephraim & Dot", "The Girl Who Made the Stars"], "edition nine-title list mismatch")
    need(edition["claim_scope"] == "ARTICLE_ANNOUNCED_NINE_TITLE_PACKAGE_NOT_DISC_OR_EPISODE_READ" and edition["work_binding"] is None, "edition identity promoted")

    credits = data["credits"]
    need(type(credits) is list and len(credits) == 10, "ten source credit rows required")
    ids = [x.get("directory_row_id") for x in credits if type(x) is dict]
    need(ids == [f"short:short-treks-{i:02}" for i in range(1, 11)], "duplicate/reordered/candidate IDs")
    synopsis_records = json.loads(strict_file(ROOT / EXISTING["accepted_description_observations_sha256"][0]), object_pairs_hook=pairs_no_duplicates)
    descriptions = synopsis_records["description_paraphrases"]
    need(len(descriptions) == 10, "accepted synopsis count changed")
    for i, (row, expected, earlier) in enumerate(zip(credits, EXPECTED, descriptions), 1):
        exact_keys(row, {"directory_row_id", "title", "publisher_guide_slot", "source_id", "credit_locator", "written_by", "teleplay_by", "story_by", "directed_by", "synopsis_status", "episode_artwork_status"}, "credit")
        title, source, written, teleplay, story, directed = expected
        need((row["title"], row["source_id"], tuple(row["written_by"]), tuple(row["teleplay_by"]), tuple(row["story_by"]), tuple(row["directed_by"])) == (title, source, written, teleplay, story, directed), f"unverified title/credit at row {i}")
        need(row["directory_row_id"] == earlier["directory_row_id"] and row["title"] == earlier["title"] and row["publisher_guide_slot"] == earlier["publisher_guide_slot"] == f"S1E{i}", "accepted directory crosswalk changed")
        want_locator = f"{title} credit immediately following description" if i <= 4 else f"2020 article {title} bullet credit"
        need(row["credit_locator"] == want_locator, "credit locator changed")
        need(row["synopsis_status"] == "HELD_ACCEPTED_PUBLISHER_PARAPHRASE" and row["episode_artwork_status"] == "NO_EPISODE_IMAGE_CONFIRMED", "release status promoted")
    return len(credits)


def main():
    data = json.loads(strict_file(RECORDS), object_pairs_hook=pairs_no_duplicates)
    count = validate(data)
    print(f"SHORT_TREKS_CREDITS_OK: {count} publisher article credit rows; 3 page-image leads HELD; no Work/coverage/publication")


if __name__ == "__main__":
    main()
