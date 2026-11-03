"""Validate one source-relative literary proposal without opening private text.

Pinned metadata prevents this specific proposal's identity drifting unnoticed.
It does *not* independently authenticate the private ZIP member or paragraph hashes.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
SHA = re.compile(r"[0-9a-f]{64}\Z")
ISBN = re.compile(r"[0-9]{13}\Z")
SOURCE_IDENTITY = {
    "local_source_id": "private-txt-slings-arrows-04-20261103",
    "container_sha256": "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac",
    "member_path": "ST ebooks txt/Next Generation/Slings and Arrows - 004 - That Sleep of Death.txt",
    "member_sha256": "bf32d8dce8121a27bb4b013ff32067da3f26b1e7238e0fce5c1f615c85240ad1",
    "member_size_bytes": 64375,
    "encoding_checked": "UTF-8_NO_REPLACEMENT_CHARACTERS",
}
SOURCE_STRUCTURE = {
    "numbered_chapters": 8,
    "author_bio_present": True,
    "whitespace_token_count": 10993,
    "narrative_paragraph_counts_by_chapter": [47, 38, 46, 48, 55, 28, 66, 11],
}
PUBLISHER_IDENTITY = {
    "local_work_id": "lit-local-slings-arrows-04-that-sleep-of-death",
    "title": "That Sleep of Death",
    "creator": "Terri Osborne",
    "source_relative_type": "NOVELLA_OR_SHORT_EBOOK_UNRESOLVED",
    "series": "Star Trek: The Next Generation: Slings and Arrows",
    "series_part": 4,
    "publisher_metadata_status": "PRIMARY_PUBLISHER_LISTING_OBSERVED",
    "publisher": "Pocket Books/Star Trek",
    "publisher_listed_release_date": "2008-01-14",
    "publisher_listed_pages": 43,
    "publisher_listed_isbn13": "9781416550242",
    "publisher_product_url": "https://www.simonandschuster.com/books/That-Sleep-of-Death/Terri-Osborne/Star-Trek-The-Next-Generation/9781416550242",
    "publisher_independence_group": "publisher:simonandschuster.com",
    "local_source_to_publisher_edition_mapping": "TITLE_AUTHOR_SERIES_MATCH_CONTENT_EQUIVALENCE_UNVERIFIED",
}
TOP_FIELDS = {
    "batch_id", "schema_version", "lane", "proposal_only", "source", "work_candidate",
    "local_entities", "evidence", "assertions", "coverage", "accepted_source_binding_effect",
    "accepted_work_effect", "accepted_coverage_effect", "denominator_effect",
    "artwork_release_effect",
}
SOURCE_FIELDS = set(SOURCE_IDENTITY) | {
    "custody", "container_basename", "structural_markers", "read_method",
    "publisher_edition_byte_equivalence", "complete_publisher_edition",
    "rights_to_publicly_redistribute_text", "source_bytes_committed",
}
WORK_FIELDS = set(PUBLISHER_IDENTITY) | {"canonical_identity"}
COVERAGE_FIELDS = {
    "source_representation", "source_retrieved", "content_actually_read",
    "structurally_indexed", "source_relative_semantic_analysis", "global_entity_linked",
    "cross_referenced", "independently_audited", "accepted_work_coverage_level",
    "public_lead_count_effect",
}


def require(condition: bool, context: str) -> None:
    """Reject invalid proposal content even under Python's -O optimization."""
    if not condition:
        raise ValueError(f"invalid LIT proposal: {context}")


def isbn13_valid(value: str) -> bool:
    if not ISBN.fullmatch(value):
        return False
    weighted = sum(int(digit) * (1 if i % 2 == 0 else 3)
                   for i, digit in enumerate(value[:12]))
    return int(value[-1]) == (-weighted) % 10


def validate(data: dict) -> tuple[int, int, int]:
    require(set(data) == TOP_FIELDS, "proposal top-level schema")
    require(data["batch_id"] == "lit-slings-arrows-04-20261103",
            "pinned batch identity")
    require(data["schema_version"] == "1.0.0", "schema version")
    require(data["lane"] == "LIT" and data["proposal_only"] is True,
            "LIT proposal status")
    for key in ("accepted_source_binding_effect", "accepted_work_effect",
                "accepted_coverage_effect", "denominator_effect", "artwork_release_effect"):
        require(data[key] == "NONE", key)

    source = data["source"]
    require(set(source) == SOURCE_FIELDS, "private source schema/unknown assertion")
    for field, expected in SOURCE_IDENTITY.items():
        require(source[field] == expected, "pinned source identity: " + field)
    require(source["custody"] == "PATRICK_PRIVATE_ONEDRIVE", "private source custody")
    require(source["container_basename"] == "ST ebooks.zip", "container basename")
    require(bool(SHA.fullmatch(source["container_sha256"])), "container SHA-256")
    require(bool(SHA.fullmatch(source["member_sha256"])), "member SHA-256")
    require(source["member_path"].startswith("ST ebooks txt/"), "member path prefix")
    require(not source["member_path"].startswith("/"), "absolute member path")
    require(".." not in source["member_path"], "traversal member path")
    require(source["member_size_bytes"] > 0, "member byte count")
    require(source["read_method"] == "ALL_EIGHT_CHAPTERS_READ_IN_ORDER_FROM_PRIVATE_ZIP_MEMBER",
            "source-read method")
    require(source["publisher_edition_byte_equivalence"] == "UNVERIFIED",
            "publisher edition equivalence")
    require(source["complete_publisher_edition"] == "UNVERIFIED", "publisher completeness")
    require(source["rights_to_publicly_redistribute_text"] == "NOT_ESTABLISHED",
            "copyright gate")
    require(source["source_bytes_committed"] is False, "source-byte gate")
    counts = source["structural_markers"]["narrative_paragraph_counts_by_chapter"]
    require(source["structural_markers"] == SOURCE_STRUCTURE,
            "pinned structural observation receipt")
    require(source["structural_markers"]["numbered_chapters"] == len(counts) == 8,
            "chapter count")
    require(all(isinstance(n, int) and n > 0 for n in counts), "paragraph counts")

    work = data["work_candidate"]
    require(set(work) == WORK_FIELDS, "publisher work schema/unknown assertion")
    for field, expected in PUBLISHER_IDENTITY.items():
        require(work[field] == expected, "pinned publisher identity: " + field)
    require(work["canonical_identity"] == "UNRECONCILED", "canonical identity gate")
    require(work["local_source_to_publisher_edition_mapping"].endswith(
        "CONTENT_EQUIVALENCE_UNVERIFIED"), "source-to-edition mapping")
    require(isbn13_valid(work["publisher_listed_isbn13"]), "publisher ISBN")
    url = urlsplit(work["publisher_product_url"])
    require(url.scheme == "https" and url.hostname == "www.simonandschuster.com",
            "publisher locator host")
    require(url.path.endswith("/" + work["publisher_listed_isbn13"]),
            "publisher locator ISBN")
    require(not url.query and not url.fragment, "publisher locator query/fragment")

    entities = data["local_entities"]
    entity_ids = [entry["id"] for entry in entities]
    require(all(set(item) == {"id", "kind", "label"} for item in entities),
            "local entity schema/unknown assertion")
    require(bool(entity_ids) and len(entity_ids) == len(set(entity_ids)),
            "unique local entities")
    require(all(item["id"].startswith("lit04-") and item["label"] and item["kind"]
                for item in entities), "local entity fields")
    evidence = data["evidence"]
    evidence_ids = [entry["id"] for entry in evidence]
    require(len(evidence_ids) == len(set(evidence_ids)) and len(evidence) >= 10,
            "unique evidence records")
    for item in evidence:
        require(set(item) == {
            "id", "kind", "entities", "chapter", "paragraph", "paragraph_sha256",
            "summary", "scope",
        }, "evidence schema/unknown assertion")
        require(1 <= item["chapter"] <= 8, "evidence chapter")
        require(1 <= item["paragraph"] <= counts[item["chapter"] - 1],
                "evidence paragraph")
        require(bool(SHA.fullmatch(item["paragraph_sha256"])), "evidence paragraph SHA-256")
        require(bool(item["summary"]) and len(item["summary"]) <= 250,
                "bounded evidence summary")
        require(bool(item["scope"]) and bool(item["kind"]), "evidence kind/scope")
        require(set(item["entities"]) <= set(entity_ids), "local entity references")
        require(not any(key in item for key in ("quote", "passage", "text")),
                "copyrighted passage gate")

    assertions = data["assertions"]
    assertion_ids = [item["id"] for item in assertions]
    require(bool(assertions) and len(assertion_ids) == len(set(assertion_ids)),
            "unique assertions")
    for item in assertions:
        require(set(item) == {"id", "predicate", "status", "statement", "supports", "limits"},
                "assertion schema/unknown assertion")
        require(item["id"].startswith("lit04-as-"), "assertion identifier")
        require(item["status"].startswith("PROPOSED_"), "assertion proposal gate")
        require(bool(item["predicate"]) and bool(item["statement"]) and
                bool(item["limits"]), "assertion fields")
        require(bool(item["supports"]) and set(item["supports"]) <= set(evidence_ids),
                "assertion evidence references")
    coverage = data["coverage"]
    require(set(coverage) == COVERAGE_FIELDS, "coverage schema/unknown assertion")
    require(coverage["source_representation"] == "PRIVATE_COMPLETE_LOOKING_EIGHT_CHAPTER_TXT",
            "source representation must remain provisional")
    require(coverage["source_retrieved"] is True and
            coverage["content_actually_read"] is True, "private source-read status")
    require(coverage["structurally_indexed"] is True and
            coverage["source_relative_semantic_analysis"] is True,
            "source-relative processing status")
    require(coverage["global_entity_linked"] is False, "global identity gate")
    require(coverage["cross_referenced"] is False, "cross-reference gate")
    require(coverage["independently_audited"] is False, "independent audit gate")
    require(coverage["accepted_work_coverage_level"] == "NONE", "accepted coverage level")
    require(coverage["public_lead_count_effect"] == "NONE", "public lead effect")
    return len(entities), len(evidence), len(assertions)


if __name__ == "__main__":
    result = validate(json.loads((HERE / "records.json").read_text(encoding="utf-8")))
    print(f"PASS source-relative LIT proposal: {result[0]} local entities; "
          f"{result[1]} evidence records; {result[2]} typed assertions; no accepted effects")
