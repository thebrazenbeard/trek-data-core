"""Offline check of a locator-only, non-admitting Memory Alpha proposal."""

import json
import pathlib
import re
from urllib.parse import quote

HERE = pathlib.Path(__file__).resolve().parent
EXPECTED_LANES = {"EPISODE": 14, "FILM": 1, "LITERARY_NOVELIZATION": 1}
REQUIRED_ENTRY_FIELDS = {"category", "lane", "url", "status"}
ALLOWED_STATUSES = {"DERIVED_LOCATOR_NOT_OPENED", "SEARCH_INDEX_CACHED_NOT_DIRECT"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(data):
    require(set(data) == {
        "proposal_id", "role", "baseline_accepted_main", "observation_date_utc",
        "proposal_only", "accepted_corpus_effect", "external_source",
        "category_locators", "crosswalks_proposed", "works_admitted",
        "sources_admitted", "source_work_bindings_admitted", "coverage_events",
    }, "unexpected public schema or protected payload")
    require(data["role"] == "LIBRARIAN", "unexpected role")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", data["baseline_accepted_main"])), "invalid baseline")
    require(data["proposal_only"] is True, "must remain proposal")
    require(data["accepted_corpus_effect"] == "NONE", "admission forbidden")
    for name in ("crosswalks_proposed", "works_admitted", "sources_admitted", "source_work_bindings_admitted", "coverage_events"):
        require(data[name] == 0, name)
    source = data["external_source"]
    require(set(source) == {
        "system", "site", "independence_group", "source_role", "narrative_evidence_weight",
        "discovery_evidence_locator", "copyright_policy_locator", "license_observed",
        "media_reuse_authorization", "direct_page_access", "acquisition",
    }, "unexpected external-source schema")
    require(source["system"] == "Memory Alpha", "wrong system")
    require(source["site"] == "https://memory-alpha.fandom.com", "wrong site")
    require(source["independence_group"] == "community:memory-alpha.fandom.com", "wrong independence family")
    require(source["source_role"] == "EXTERNAL_DISCOVERY_AND_CROSSWALK_ONLY", "wrong source role")
    require(source["narrative_evidence_weight"] == 0, "narrative evidence unsupported")
    require(source["discovery_evidence_locator"] == "https://memory-alpha.fandom.com/wiki/Memory_Alpha:Category_tree", "wrong evidence locator")
    require(source["copyright_policy_locator"] == "https://memory-alpha.fandom.com/wiki/Memory_Alpha:Copyrights", "wrong policy locator")
    require("CC-BY-NC-4.0" in source["license_observed"], "site-specific license missing")
    require(source["media_reuse_authorization"] == "NONE", "media authorization unsupported")
    require(source["direct_page_access"] == "BLOCKED_BY_ROBOTS_TXT", "direct access unsupported")
    require(source["acquisition"] == "PUBLIC_SEARCH_INDEX_SNIPPETS_ONLY; NO_HTTP_CONTENT_OR_REVISION_HASH", "unverified acquisition")
    records = data["category_locators"]
    require(isinstance(records, list) and len(records) == 16, "unexpected category count")
    labels = []
    counts = dict.fromkeys(EXPECTED_LANES, 0)
    for row in records:
        require(set(row) == REQUIRED_ENTRY_FIELDS, "text, claims or media fields forbidden")
        label, lane, status = row["category"], row["lane"], row["status"]
        require(isinstance(label, str) and bool(re.fullmatch(r"Category:[A-Za-z0-9 ]+", label)), "invalid category")
        require(lane in counts, "invalid lane")
        require(status in ALLOWED_STATUSES, "unsupported direct-read claim")
        # Must be a source-category locator, never a source-backed narrative assertion.
        url = "https://memory-alpha.fandom.com/wiki/" + quote(label.replace(" ", "_"), safe=":")
        require(url.startswith(source["site"] + "/wiki/Category:"), "invalid category URL")
        require(row["url"] == url, "source locator does not match title or host")
        labels.append(label)
        counts[lane] += 1
    require(len(labels) == len(set(labels)), "duplicate categories")
    require(counts == EXPECTED_LANES, "unexpected category lanes")
    require(records[-1] == {"category": "Category:Novelizations", "lane": "LITERARY_NOVELIZATION", "url": "https://memory-alpha.fandom.com/wiki/Category:Novelizations", "status": "SEARCH_INDEX_CACHED_NOT_DIRECT"}, "novelizations evidence changed")
    require(next(r for r in records if r["category"] == "Category:DIS episodes")["status"] == "SEARCH_INDEX_CACHED_NOT_DIRECT", "DIS evidence changed")
    return len(records)


if __name__ == "__main__":
    path = HERE / "records.json"
    print("MEMORY_ALPHA_LOCATOR_PROPOSAL_OK:", validate(json.loads(path.read_text(encoding="utf-8"))))
