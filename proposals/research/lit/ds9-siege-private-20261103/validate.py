"""Public metadata checks for one private-source LIT proposal.

The copyrighted source is never needed or shipped for this validation.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "72c60433e98c6d8cc0ad0e2de7edc2713c2db8efaae55a27def51da6aaae5d5f"
ARCHIVE_SHA = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
INDEX_FILE_SHA = "bb39f30b0a1a74be04fc914e6fb2137883116c159c8309e20811f38076b015e5"
PUBLISHER = "https://www.simonandschuster.com/books/The-Star-Trek-Deep-Space-Nine-The-Siege/Peter-David/Star-Trek-Deep-Space-Nine/9780743412216"


def check(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def native_int(value: object) -> bool:
    return type(value) is int


def validate(index: dict, records: dict, librarian: dict | None = None) -> None:
    check(index.get("schema_version") == "trek-lit-private-txt-chapter-index-v1", "index schema")
    check(records.get("schema_version") == "trek-lit-private-source-relative-evidence-v1", "records schema")
    check(index.get("source_local_id") == records.get("source_local_id") == "txt-local:0002", "source identity")
    check(index.get("archive_sha256") == ARCHIVE_SHA, "archive integrity")
    check(index.get("source_member_sha256") == records.get("source_member_sha256") == SOURCE_SHA, "source integrity")
    check(index.get("source_member_bytes") == 423375, "member size")
    check(index.get("total_nonempty_lines") == 2989, "line total")
    check(index.get("published_edition_verified") is False, "premature edition identity")
    check(index.get("accepted_work_coverage_effect") == "NONE", "unaccepted coverage")
    check(records.get("proposal_only") is True, "not an accepted record")
    work = records.get("candidate_work", {})
    check(work.get("title") == "The Siege" and work.get("creator") == "Peter David", "candidate work")
    check(work.get("publisher_catalog") == PUBLISHER, "publisher match")
    check(work.get("source_work_binding") == "CANDIDATE_UNRESOLVED", "premature binding")
    check(work.get("edition_match") == "UNKNOWN", "premature edition match")
    check(work.get("full_publisher_edition_complete") == "UNKNOWN", "premature completeness")
    check(records.get("reading", {}).get("read_scope") == "PREFACE_PROLOGUE_AND_ALL_22_OBSERVED_CHAPTERS", "read scope")
    check(records["reading"].get("read_performed") is True, "read performed")
    check(records["reading"].get("copyrighted_text_exported") is False, "copyrighted source export")
    check(records["reading"].get("accepted_coverage_effect") == "NONE", "unaccepted coverage records")
    check(records["reading"].get("global_reconciliation_effect") == "NONE", "global identity effect")
    chapters = index.get("chapters")
    check(isinstance(chapters, list) and len(chapters) == 23, "23 observed segments")
    char_cursor = line_cursor = 0
    for ordinal, part in enumerate(chapters):
        check(set(part) == {"chapter", "char_start", "char_end_exclusive",
                           "nonempty_line_start", "nonempty_line_end_exclusive",
                           "segment_sha256"}, "unexpected segment field")
        check(part["chapter"] == ordinal and native_int(part["chapter"]), "chapter order")
        check(all(native_int(part[k]) for k in
                  ("char_start", "char_end_exclusive", "nonempty_line_start",
                   "nonempty_line_end_exclusive")), "integer segment bounds")
        check(part["char_start"] == char_cursor and
              char_cursor < part["char_end_exclusive"] <= 423375, "segment char continuity")
        check(part["nonempty_line_start"] == line_cursor and
              line_cursor < part["nonempty_line_end_exclusive"] <= 2989, "segment line continuity")
        check(bool(re.fullmatch(r"[0-9a-f]{64}", part["segment_sha256"])), "segment digest syntax")
        char_cursor = part["char_end_exclusive"]
        line_cursor = part["nonempty_line_end_exclusive"]
    check(char_cursor == 423375 and line_cursor == 2989, "coverage of full private member")

    entities = records.get("local_entities")
    check(isinstance(entities, list) and len(entities) >= 20, "local entity minimum")
    local_ids = [e.get("id") for e in entities]
    check(all(isinstance(x, str) and x.startswith("lit-ds9-siege:") for x in local_ids),
          "global/nonlocal entity ID")
    check(len(set(local_ids)) == len(local_ids), "duplicate local entity")
    check(all(set(e) == {"id", "kind", "local_label"} for e in entities), "local entity shape")

    evidence = records.get("evidence")
    check(isinstance(evidence, list) and len(evidence) >= 25, "evidence minimum")
    ev_ids = [e.get("id") for e in evidence]
    check(len(set(ev_ids)) == len(ev_ids), "duplicate evidence ID")
    check(all(re.fullmatch(r"ev-[0-9]{2}", x or "") for x in ev_ids), "evidence ID form")
    for ev in evidence:
        check(set(ev) == {"id", "kind", "locator", "participants", "observation", "frame"},
              "extra evidence field / possible source payload")
        check(set(ev["locator"]) == {"chapter", "nonempty_line_zero_based"}, "locator fields")
        ch = ev["locator"]["chapter"]
        row = ev["locator"]["nonempty_line_zero_based"]
        check(native_int(ch) and 0 <= ch <= 22, "locator chapter")
        check(native_int(row) and 0 <= row <
              chapters[ch]["nonempty_line_end_exclusive"] - chapters[ch]["nonempty_line_start"],
              "locator line")
        check(isinstance(ev["participants"], list) and set(ev["participants"]).issubset(local_ids),
              "unknown local occurrence")
        check(isinstance(ev["observation"], str) and 25 <= len(ev["observation"]) < 350,
              "source-locally described observation only")
        check(isinstance(ev["frame"], str) and ev["frame"].strip(), "missing frame")

    by_id = {e["id"]: e for e in evidence}
    for eid in ("ev-19", "ev-20"):
        check(eid in by_id, "missing local decoy evidence")
        participants = by_id[eid]["participants"]
        check("lit-ds9-siege:odo" in participants and
              "lit-ds9-siege:quark" not in participants,
              "Quark decoy incorrectly bound to Quark occurrence")

    assertions = records.get("assertions")
    check(isinstance(assertions, list) and len(assertions) >= 6, "assertions")
    assertion_ids = [a.get("id") for a in assertions]
    check(len(assertion_ids) == len(set(assertion_ids)), "duplicate assertion")
    for a in assertions:
        check(set(a) == {"id", "type", "predicate", "subject", "object", "supported_by",
                         "counterweight", "counterevidence_status", "status"}, "assertion fields")
        check(a["type"] == "INTERPRETIVE" and a["status"] == "SOURCE_LOCAL_INTERPRETATION",
              "interpretation elevated to fact")
        check(a["subject"] in local_ids, "nonlocal subject")
        check(isinstance(a["supported_by"], list) and a["supported_by"] and
              set(a["supported_by"]).issubset(ev_ids), "unbound support")
        # Source counterweights are a semantic relation, not an arbitrary foreign ID.
        # No genuinely disconfirming observation has been established for these
        # deliberately bounded interpretations. Explicit UNKNOWN, no fake certainty.
        check(a["counterweight"] == [], "counterweight without adversarial rationale")
        check(a["counterevidence_status"] == "UNKNOWN", "claim of exhaustive counterevidence")
    questions = records.get("unresolved")
    check(isinstance(questions, list) and len(questions) >= 6, "uncertainty ledger")
    check({"EDITION_IDENTITY", "TEXT_COMPLETENESS", "CONTINUITY", "ENTITY_IDENTITY",
           "RECONCILIATION_AUTHORITY"}.issubset({q.get("kind") for q in questions}),
          "required unresolved categories")
    check(all(q.get("status") in {"UNKNOWN", "UNRESOLVED", "AMBIGUOUS", "CONTESTED"} for q in questions),
          "unresolved item falsely settled")

    payload = json.dumps({"index": index, "records": records})
    for forbidden in ("C:\\Users\\", "/Users/", "ST ebooks txt/",
                      "private_member_path", "chapter_text", "raw_text",
                      "full_transcript", "source_excerpt"):
        check(forbidden not in payload, "private source/path field")

    if librarian is not None:
        check(librarian.get("archive", {}).get("whole_zip_sha256") == ARCHIVE_SHA, "archive receipt")
        members = [x for x in librarian.get("records", []) if x.get("source_local_id") == "txt-local:0002"]
        check(len(members) == 1, "Librarian member uniqueness")
        check(members[0].get("member_sha256") == SOURCE_SHA and
              members[0].get("uncompressed_bytes") == 423375, "Librarian member byte authority")
        check(librarian.get("member_byte_access") == "HASHED_WITHOUT_SEMANTIC_READ",
              "Librarian ownership boundary")


if __name__ == "__main__":
    check(hashlib.sha256((HERE / "CHAPTER_INDEX.json").read_bytes()).hexdigest() == INDEX_FILE_SHA,
          "immutable private-source-verified segment receipt")
    i = json.loads((HERE / "CHAPTER_INDEX.json").read_text("utf-8"))
    r = json.loads((HERE / "records.json").read_text("utf-8"))
    root = next((p for p in HERE.parents if (p / "proposals/librarian").exists()), None)
    source = root / "proposals/librarian/private-ds9-txt50-20261103/observations.json" if root else None
    v = json.loads(source.read_text("utf-8")) if source and source.is_file() else None
    validate(i, r, v)
    print("PASS: LIT DS9 Siege private source metadata / no accepted Work effect")
