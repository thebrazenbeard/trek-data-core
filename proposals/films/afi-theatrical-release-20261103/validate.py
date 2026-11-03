"""Fail-closed checks for an unadmitted AFI Catalog release-date proposal."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
from urllib.parse import urlsplit


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBSERVATIONS = HERE / "observations.json"
DISCOVERY_FILMS = ROOT / "proposals/librarian/films-official-index-20261102/bundle.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exact_keys(obj: dict, expected: set[str], context: str) -> None:
    require(isinstance(obj, dict), f"{context}: expected object")
    require(set(obj) == expected, f"{context}: missing or extra keys")


def validate(proposal: dict, discovery: dict) -> int:
    exact_keys(proposal, {
        "schema_version", "proposal_type", "proposal_only", "coverage_effect",
        "admission_effect", "artwork_release_effect", "observed_on_utc",
        "source_family", "independence_note", "records",
    }, "proposal")
    for key, expected in {
        "schema_version": "1.0.0",
        "proposal_type": "FILM_SOURCE_LOCAL_RELEASE_METADATA",
        "proposal_only": True,
        "coverage_effect": "NONE",
        "admission_effect": "NONE",
        "artwork_release_effect": "NONE",
        "source_family": "afi:catalog-of-feature-films",
    }.items():
        require(type(proposal[key]) is type(expected) and proposal[key] == expected, f"invalid {key}")
    require(isinstance(proposal["independence_note"], str) and len(proposal["independence_note"]) > 30, "lineage must be documented")
    try:
        dt.date.fromisoformat(proposal["observed_on_utc"])
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid observed_on_utc") from exc

    require(discovery.get("proposal_type") == "FILM_DISCOVERY_METADATA", "missing film discovery baseline")
    known = {film["id"]: film["title"] for film in discovery["films"]}
    records = proposal["records"]
    require(isinstance(records, list) and len(records) == 5, "expected five source-local records")
    unique = {"source": set(), "record": set(), "entity": set(), "evidence": set(), "assertion": set(), "work": set()}

    for i, record in enumerate(records):
        context = f"record {i}"
        exact_keys(record, {
            "local_record_id", "source", "local_entity_id", "candidate_work_ref",
            "crosswalk_status", "evidence", "assertion", "artwork_rights",
        }, context)
        source = record["source"]
        exact_keys(source, {"catalog_id", "catalog_title", "locator", "section", "raw_page_sha256"}, f"{context} source")
        catalog_id = source["catalog_id"]
        require(isinstance(catalog_id, str) and re.fullmatch(r"[1-9][0-9]{4,6}", catalog_id) is not None,
                f"{context}: invalid AFI catalog ID")
        url = urlsplit(source["locator"])
        require(url.scheme == "https" and url.netloc == "catalog.afi.com" and
                re.fullmatch(rf"/(?:Film|Catalog/MovieDetails)/{catalog_id}(?:-[A-Za-z0-9-]+)?", url.path) is not None and
                not url.query and not url.fragment, f"{context}: invalid AFI locator")
        require(source["section"] == "DETAILS > Release Date", f"{context}: wrong source section")
        require(source["raw_page_sha256"] is None, f"{context}: no raw page snapshot is held")
        require(record["local_record_id"] == f"afi-film-{catalog_id}-release", f"{context}: local record ID mismatch")
        require(record["local_entity_id"] == f"afi-film-listing-{catalog_id}", f"{context}: local entity ID mismatch")
        work_ref = record["candidate_work_ref"]
        require(work_ref in known and known[work_ref] == source["catalog_title"], f"{context}: candidate film mismatch")
        require(record["crosswalk_status"] == "CANDIDATE_NOT_RECONCILED", f"{context}: crosswalk must remain unadmitted")
        require(record["artwork_rights"] == "NO_IMAGE_ACQUIRED_NO_DISPLAY_PERMISSION", f"{context}: no art rights granted")

        evidence = record["evidence"]
        exact_keys(evidence, {"id", "kind", "source_field_value"}, f"{context} evidence")
        require(evidence["id"] == f"afi-{catalog_id}-release-field", f"{context}: bad evidence ID")
        require(evidence["kind"] == "SOURCE_METADATA_FIELD", f"{context}: not an audiovisual source reading")
        require(isinstance(evidence["source_field_value"], str) and len(evidence["source_field_value"]) <= 40,
                f"{context}: source field length/type")
        try:
            extracted_date = dt.datetime.strptime(evidence["source_field_value"], "%d %B %Y").date()
        except ValueError as exc:
            raise ValueError(f"{context}: unparseable source date") from exc

        assertion = record["assertion"]
        exact_keys(assertion, {"id", "predicate", "value", "scope", "status", "evidence_ref"}, f"{context} assertion")
        require(assertion["id"] == f"afi-{catalog_id}-release-assertion", f"{context}: bad assertion ID")
        require(assertion["predicate"] == "AFI_CATALOG_LISTS_THEATRICAL_RELEASE_DATE", f"{context}: bad predicate")
        require(assertion["value"] == extracted_date.isoformat(), f"{context}: normalized date differs from source field")
        require(assertion["scope"] == "ORIGINAL_THEATRICAL_RELEASE", f"{context}: ambiguous release scope")
        require(assertion["status"] == "SOURCE_ATTRIBUTED_ONLY", f"{context}: unsupported fact promotion")
        require(assertion["evidence_ref"] == evidence["id"], f"{context}: broken evidence link")

        for kind, value in {
            "source": catalog_id, "record": record["local_record_id"],
            "entity": record["local_entity_id"], "evidence": evidence["id"],
            "assertion": assertion["id"], "work": work_ref,
        }.items():
            require(value not in unique[kind], f"{context}: duplicate {kind}")
            unique[kind].add(value)
    return len(records)


def main() -> None:
    proposal = json.loads(OBSERVATIONS.read_text(encoding="utf-8"))
    discovery = json.loads(DISCOVERY_FILMS.read_text(encoding="utf-8"))
    print(f"PASS: {validate(proposal, discovery)} AFI film source-local observations; 0 governed records; 0 artwork released")


if __name__ == "__main__":
    main()
