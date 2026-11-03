"""Public invariant checks for a private-source literary research proposal.

No source book bytes or private member paths are read or distributed here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_SHA = "fb80998ce09f42b096d97cbffda446eb68f1b022d6c8f344d665bc1cf54f5f3e"
ARCHIVE_SHA = "c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac"
EXPECTED_SEGMENTS = (
    "2c6a8186de3775d09549fdb1b6960c5cc99d1bf730b42d1644d4b4fd63e64d74",
    "cb6a7e5cb82ee7b77424c7a3349471d7cf436bbb7f469f6f4cd95187d71949e8",
    "dfefb7a7e1f5ad09ff480c3da3c0e6313b4d57dc836677fa29dfb0cce399a109",
    "d3dbaa749ce359ec364e7127bb118dac46b62a1dba80ea4036181e9b541df250",
    "247980384ede030a52df3a6e8109830f7e245c5083ee6bd948c410cb6b1fb514",
    "f131dd75c30e940aabd507cbf95c013e6873eaec8903ddf6be605db722931501",
    "4b67def0438cbeafef0ae795cf9ebe768f2d17c22475316014185dd10033cb45",
    "fb6d9163040bee80ef521f5f35362bef519d1eafa1bbdb4a5332d04d065d65fa",
    "933dbd579208b98702672976c8dde04e3d49adef26b6ddbb7e6de00dcfd4b96b",
    "7d769444b455b04cac3def92f9f89ac83b36fe09a28cc7e3841d0c33aabb2de6",
    "a33b8319e92c2d83b20e30dc00fc215a01216ad452eb2311971831fef7cc20f9",
    "adac920436b273526b7ffd35d6137fa83a617efec85fe49d49f85696f590905b",
)


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _strict_int(n: object) -> bool:
    return type(n) is int


def validate(index: dict, records: dict, librarian: dict | None = None) -> None:
    _ensure(index.get("schema_version") == "trek-lit-private-txt-chapter-index-v1", "index schema")
    _ensure(records.get("schema_version") == "trek-lit-private-source-relative-evidence-v1", "record schema")
    _ensure(index.get("source_local_id") == records.get("source_local_id") == "txt-local:0001", "source identity")
    _ensure(index.get("archive_sha256") == ARCHIVE_SHA, "archive hash")
    _ensure(index.get("source_member_sha256") == records.get("source_member_sha256") == SOURCE_SHA, "member hash")
    _ensure(index.get("source_member_bytes") == 363543, "member size")
    _ensure(index.get("total_nonempty_lines") == 2092, "nonempty line total")
    _ensure(index.get("published_edition_verified") is False, "edition must remain unverified")
    _ensure(index.get("accepted_work_coverage_effect") == "NONE", "coverage effect")
    _ensure(records.get("proposal_only") is True, "proposal only")
    candidate = records.get("candidate_work", {})
    _ensure(candidate.get("edition_match") == "UNKNOWN", "edition identity")
    _ensure(candidate.get("source_work_binding") == "CANDIDATE_UNRESOLVED", "source binding")
    _ensure(candidate.get("publisher_catalog") ==
            "https://www.simonandschuster.com/books/Emissary/J-M-Dillard/Star-Trek-Deep-Space-Nine/9780743412209",
            "publisher source")
    reading = records.get("reading", {})
    _ensure(reading.get("read_scope") == "ALL_TWELVE_OBSERVED_CHAPTERS", "read scope")
    _ensure(reading.get("read_performed") is True, "read assertion")
    _ensure(reading.get("accepted_coverage_effect") == "NONE", "accepted coverage")
    _ensure(reading.get("copyrighted_text_exported") is False, "copyrighted bytes")
    _ensure(reading.get("global_reconciliation_effect") == "NONE", "global identity mutation")

    chapters = index.get("chapters")
    _ensure(isinstance(chapters, list) and len(chapters) == 12, "12 observed chapters")
    char_cursor = line_cursor = 0
    for i, c in enumerate(chapters):
        _ensure(set(c) == {"chapter", "char_start", "char_end_exclusive",
                          "nonempty_line_start", "nonempty_line_end_exclusive", "segment_sha256"},
                "unexpected chapter fields / possible source leak")
        _ensure(_strict_int(c["chapter"]) and c["chapter"] == i + 1, "chapter ordinal")
        _ensure(all(_strict_int(c[k]) for k in
                    ("char_start", "char_end_exclusive", "nonempty_line_start", "nonempty_line_end_exclusive")),
                "index positions must be integers")
        _ensure(c["char_start"] == char_cursor and
                char_cursor < c["char_end_exclusive"] <= 363543, "character continuity")
        _ensure(c["nonempty_line_start"] == line_cursor and
                line_cursor < c["nonempty_line_end_exclusive"] <= 2092, "line continuity")
        _ensure(c["segment_sha256"] == EXPECTED_SEGMENTS[i], "chapter digest")
        char_cursor, line_cursor = c["char_end_exclusive"], c["nonempty_line_end_exclusive"]
    _ensure(char_cursor == 363543 and line_cursor == 2092, "tail coverage")
    _ensure(sum(c["nonempty_line_end_exclusive"] - c["nonempty_line_start"] for c in chapters) == 2092,
            "line partition total")

    entities = records.get("local_entities")
    _ensure(isinstance(entities, list) and len(entities) >= 10, "local entity inventory")
    local_ids = [e.get("id") for e in entities]
    _ensure(all(isinstance(v, str) and v.startswith("lit-ds9-emissary:") for v in local_ids),
            "local, non-global IDs required")
    _ensure(len(set(local_ids)) == len(local_ids), "duplicate local entity")
    evidence = records.get("evidence")
    _ensure(isinstance(evidence, list) and len(evidence) >= 12, "source evidence minimum")
    ev_ids = [e.get("id") for e in evidence]
    _ensure(len(ev_ids) == len(set(ev_ids)), "duplicate evidence ID")
    _ensure(all(re.fullmatch(r"ev-[0-9]{2}", i or "") for i in ev_ids), "evidence format")
    for e in evidence:
        _ensure(set(e) == {"id", "kind", "locator", "participants", "observation", "frame"},
                "unexpected evidence fields / possible source leak")
        loc = e["locator"]
        _ensure(set(loc) == {"chapter", "nonempty_line_zero_based"}, "locator shape")
        _ensure(_strict_int(loc["chapter"]) and 1 <= loc["chapter"] <= 12, "locator chapter")
        _ensure(_strict_int(loc["nonempty_line_zero_based"]) and
                0 <= loc["nonempty_line_zero_based"] <
                chapters[loc["chapter"] - 1]["nonempty_line_end_exclusive"] -
                chapters[loc["chapter"] - 1]["nonempty_line_start"], "locator bounds")
        _ensure(set(e["participants"]).issubset(local_ids), "unknown local entities")
        _ensure(len(e["observation"]) < 360, "observation too long (possible source text)")
        _ensure(bool(e["kind"]) and bool(e["frame"]), "source frame required")

    assertions = records.get("assertions")
    _ensure(isinstance(assertions, list) and len(assertions) >= 5, "assertion inventory")
    ids = [a.get("id") for a in assertions]
    _ensure(len(ids) == len(set(ids)), "duplicate assertion")
    for a in assertions:
        _ensure(a["type"] == "INTERPRETIVE" and a["status"] == "SOURCE_LOCAL_INTERPRETATION",
                "assertion must not be global fact")
        _ensure(a["subject"] in local_ids, "assertion subject local")
        _ensure(set(a["supported_by"]).issubset(ev_ids) and a["supported_by"], "missing evidence links")
        _ensure(set(a["counterweight"]).issubset(ev_ids), "unknown counterweight evidence")
    unresolved = records.get("unresolved")
    _ensure(isinstance(unresolved, list) and len(unresolved) >= 4, "uncertainty ledger")
    _ensure({"EDITION_IDENTITY", "TEXT_COMPLETENESS", "CONTINUITY", "ENTITY_IDENTITY"}.issubset(
        {u.get("kind") for u in unresolved}), "required unresolved questions")

    # Prevent accidentally leaking private local paths, quoted passages, or source payloads.
    payload = json.dumps({"index": index, "records": records})
    for disallowed in ("C:\\Users\\", "/Users/", "ST ebooks txt/", "private_member_path",
                       "chapter_text", "raw_text", "full_transcript", "source_excerpt"):
        _ensure(disallowed not in payload, f"disallowed source/path field: {disallowed}")

    if librarian is not None:
        _ensure(librarian.get("archive", {}).get("whole_zip_sha256") == ARCHIVE_SHA, "librarian archive")
        matches = [r for r in librarian.get("records", []) if r.get("source_local_id") == "txt-local:0001"]
        _ensure(len(matches) == 1, "accepted librarian member absent or duplicated")
        _ensure(matches[0].get("member_sha256") == SOURCE_SHA and
                matches[0].get("uncompressed_bytes") == 363543, "accepted librarian member mismatch")
        _ensure(librarian.get("member_byte_access") == "HASHED_WITHOUT_SEMANTIC_READ",
                "librarian receipt scope changed")


if __name__ == "__main__":
    index = json.loads((HERE / "CHAPTER_INDEX.json").read_text(encoding="utf-8"))
    records = json.loads((HERE / "records.json").read_text(encoding="utf-8"))
    ancestor = next((p for p in HERE.parents if (p / "proposals" / "librarian").exists()), None)
    receipt = None
    if ancestor is not None:
        p = ancestor / "proposals/librarian/private-ds9-txt50-20261103/observations.json"
        if p.exists():
            receipt = json.loads(p.read_text(encoding="utf-8"))
    validate(index, records, receipt)
    print("PASS: LIT DS9 Emissary private-source research proposal metadata")
