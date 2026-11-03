#!/usr/bin/env python3
"""Fail-closed validation of a held, source-only 20-OPF/7-jacket proposal.

No private narrative, publisher image rights, network mutable state, or Work
identity are read or granted here.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import py_compile
import re
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).with_name("records.json")
PART = PACKET.relative_to(ROOT).parent
ROW_SHA256 = "9a018e9fef07e1b0c96802976914d4328a341f4ea90871095166fecf2da57eed"
MANIFEST_SHA256 = "82dce76ca8de5574d84b44163b45e54b6c97deb49619529b3a98c518227ea86a"
METADATA_PATH = "proposals/librarian/private-opf-metadata-20261103/observations.json"
METADATA_SHA256 = "5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7"
ENTROPY_PATH = "proposals/librarian/tos-classics-cover-editions-20261103/records.json"
ENTROPY_SHA256 = "6688f233a5bb6053c728f4619db297451f2c7929985e115e1ed888996423364d"
SOURCE_IDS = {37, 38, 80, 86, 102, 103, 104, 109, 119, 123, 140, 141, 142, 143, 144, 209, 210, 211, 212, 213}
COVERS = {
    "9780743475921": 12055672, "9780743475938": 12055694,
    "9780743421416": 14687625, "9780743419260": 476375,
    "9780743434348": 476746, "9780743405928": 475787,
    "9780743412087": 10476824,
}
EXACT_PUBLISHER = {"9780743475921", "9780743475938", "9780743421416", "9780743412087"}
OTHER_ISBN_PUBLISHER = {"9780743419260", "9780743434348", "9780743405928"}
HTTP_404 = {"9780743421409", "9780743421423"}
ENTROPY = "9780743412094"
ROOT_KEYS = {
    "schema_version", "proposal_id", "accepted_baseline", "source_metadata_path",
    "source_metadata_sha256", "observation_date_utc", "api_source", "cover_source",
    "private_narrative_read", "private_archive_member_paths_exported",
    "source_or_work_admission", "explorer_display_effect", "image_bytes_committed",
    "copyright_status", "rows",
}
ROW_KEYS = {
    "opf_id", "isbn10", "isbn13", "opf_sha256", "ol_status", "ol_edition",
    "ol_response_sha256", "cover_id", "medium_bytes", "medium_sha256",
    "publisher_relation", "publisher_url", "publisher_page_isbn13", "visual",
}
ALLOWED_PACKET = {"MANIFEST.md", "records.json", "validate.py", "test_validate.py"}
PYC = re.compile(r"^(validate|test_validate)\.cpython-[0-9]+(?:\.opt-[12])?\.pyc$")
EMBED = re.compile(r"!\s*\[|<\s*/?\s*[a-z][^>]*>|<\s*!|\bdata\s*:\s*(?:image|audio|video|text/html)\s*/", re.I)
SHA = re.compile(r"^[0-9a-f]{64}$")
EDITION = re.compile(r"^OL[0-9]+M$")


def pairs_unique(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate JSON key")
        d[k] = v
    return d


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isbn10_to13(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{9}[0-9X]", value):
        raise ValueError("invalid ISBN10")
    if sum((10-i) * (10 if c == "X" else int(c)) for i, c in enumerate(value)) % 11:
        raise ValueError("ISBN10 checksum mismatch")
    first12 = "978" + value[:9]
    checksum = sum(int(x) * (1 if i % 2 == 0 else 3) for i, x in enumerate(first12))
    return first12 + str((-checksum) % 10)


def guard_packet(root):
    folder = root / PART
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("held packet missing or redirected")
    files = list(folder.iterdir())
    names = {x.name for x in files}
    if names - {"__pycache__"} != ALLOWED_PACKET:
        raise ValueError("unknown packet member or image payload")
    if any(x.is_symlink() or not x.is_file() for x in files if x.name != "__pycache__"):
        raise ValueError("nested, symlinked or nonregular packet member")
    if "__pycache__" in names:
        cache = folder / "__pycache__"
        if cache.is_symlink() or not cache.is_dir():
            raise ValueError("unexpected interpreter cache")
        for p in cache.iterdir():
            match = PYC.fullmatch(p.name)
            if not match or p.is_symlink() or not p.is_file():
                raise ValueError("unknown Python cache media or nested member")
            source = (folder / (match.group(1) + ".py")).resolve()
            optimization = int(p.name[-5]) if ".opt-" in p.name else 0
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "expected.pyc"
                py_compile.compile(str(source), cfile=str(target), doraise=True,
                                   optimize=optimization)
                expected_code = target.read_bytes()[16:]
            raw = p.read_bytes()
            if not raw.startswith(importlib.util.MAGIC_NUMBER) or raw[16:] != expected_code:
                raise ValueError("interpreter cache does not match allowed Python source")
    if sha(folder / "MANIFEST.md") != MANIFEST_SHA256:
        raise ValueError("unreviewed source-only manifest change")
    if EMBED.search((folder / "MANIFEST.md").read_text(encoding="utf-8")):
        raise ValueError("remote or embedded HTML/image in held manifest")


def validate(data=None, root=ROOT):
    guard_packet(root)
    data = load(root / PACKET.relative_to(ROOT)) if data is None else data
    if not isinstance(data, dict) or set(data) != ROOT_KEYS:
        raise ValueError("unreviewed packet keys")
    if (data["schema_version"] != "1.0.0" or
            data["proposal_id"] != "LIBRARIAN-OPF-NEXT-TWENTY-COVER-AUDIT-20261103" or
            data["accepted_baseline"] != "7b8ec8eb8e320002ee88280f11db2f108c38b85d" or
            data["source_metadata_path"] != METADATA_PATH or
            data["source_metadata_sha256"] != METADATA_SHA256 or
            data["observation_date_utc"] != "2026-11-03" or
            data["api_source"] != "https://openlibrary.org/dev/docs/api/books" or
            data["cover_source"] != "https://openlibrary.org/dev/docs/api/covers" or
            data["private_narrative_read"] is not False or
            data["private_archive_member_paths_exported"] is not False or
            data["source_or_work_admission"] != "NONE" or
            data["explorer_display_effect"] != "NONE" or
            data["image_bytes_committed"] is not False or
            data["copyright_status"] != "THIRD_PARTY_JACKET_RIGHTS_NOT_ESTABLISHED"):
        raise ValueError("source, rights or release promotion")
    rows = data["rows"]
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("twenty OPF observations required")
    if hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != ROW_SHA256:
        raise ValueError("unreviewed OPF/OL/ISBN/medium image observation")
    metadata_path = root / METADATA_PATH
    if sha(metadata_path) != METADATA_SHA256:
        raise ValueError("accepted sanitized OPF metadata bytes drifted")
    source = {r["source_local_id"]: r for r in load(metadata_path)["rows"]}
    if sha(root / ENTROPY_PATH) != ENTROPY_SHA256:
        raise ValueError("prior public Entropy ISBN source changed")
    entropy = [r for r in load(root / ENTROPY_PATH)["edition_candidates"] if r["isbn13"] == ENTROPY]
    if len(entropy) != 1:
        raise ValueError("duplicated Entropy edition receipt missing")
    seen_opf = set()
    seen_isbn = set()
    seen_hash = set()
    relations = Counter()
    for row in rows:
        if not isinstance(row, dict) or set(row) != ROW_KEYS:
            raise ValueError("unreviewed row keys")
        original = source.get(row["opf_id"])
        if (not original or original["parse_status"] not in
                ("PARSED", "OPF_XML_NAMESPACE_RECOVERED") or
                original["opf_entry_sha256"] != row["opf_sha256"] or
                original["isbn_checksum_valid"] != [row["isbn10"]] or
                isbn10_to13(row["isbn10"]) != row["isbn13"] or
                not SHA.fullmatch(row["opf_sha256"]) or
                not SHA.fullmatch(row["ol_response_sha256"])):
            raise ValueError("not exact accepted OPF checksum-valid ISBN metadata")
        if not EDITION.fullmatch(row["ol_edition"] or "") and row["ol_status"] != 404:
            raise ValueError("invalid observed Open Library edition")
        if row["opf_id"] in seen_opf or row["isbn13"] in seen_isbn or row["opf_sha256"] in seen_hash:
            raise ValueError("duplicate source ID/ISBN/OPF member digest")
        seen_opf.add(row["opf_id"])
        seen_isbn.add(row["isbn13"])
        seen_hash.add(row["opf_sha256"])
        isbn = row["isbn13"]
        if isbn in COVERS:
            if (row["ol_status"] != 200 or row["cover_id"] != COVERS[isbn] or
                    not isinstance(row["medium_bytes"], int) or row["medium_bytes"] < 1000 or
                    not SHA.fullmatch(row["medium_sha256"]) or
                    row["visual"] != "BOOK_JACKET_TITLE_MATCH_LIBRARIAN"):
                raise ValueError("unreviewed held image or visual class")
            if isbn in EXACT_PUBLISHER:
                relation = "EXACT_ISBN_OFFICIAL_PUBLISHER"
                if row["publisher_page_isbn13"] != isbn:
                    raise ValueError("official page ISBN not exact")
            else:
                relation = "SAME_WORK_DIFFERENT_OFFICIAL_ISBN_HOLD"
                if (isbn not in OTHER_ISBN_PUBLISHER or
                        row["publisher_page_isbn13"] == isbn):
                    raise ValueError("different-edition hold promoted")
            if (row["publisher_relation"] != relation or
                    not row["publisher_url"].startswith(("https://www.simonandschuster.com/",
                                                         "https://www.simonandschuster.net/",
                                                         "https://www.simonandschuster.biz/")) or
                    not row["publisher_url"].endswith("/" + row["publisher_page_isbn13"])):
                raise ValueError("publisher page mismatched or forged")
        else:
            if row["cover_id"] is not None or row["medium_bytes"] is not None or row["medium_sha256"] is not None:
                raise ValueError("unsourced image payload on no-cover row")
            if isbn in HTTP_404:
                if (row["ol_status"] != 404 or row["ol_edition"] is not None or
                        row["visual"] != "OL_ISBN_ENDPOINT_404" or
                        row["publisher_relation"] != "NOT_EVALUATED_UNRESOLVED_ISBN"):
                    raise ValueError("404 observation elevated")
            elif (row["ol_status"] != 200 or row["visual"] != "NO_COVERS_FIELD" or
                    row["publisher_relation"] not in
                    ("NOT_EVALUATED_NO_IMAGE", "EXISTING_PUBLIC_EDITION_CROSSWALK_DUPLICATE")):
                raise ValueError("held no-cover observation drifted")
            if isbn == ENTROPY:
                if (row["publisher_relation"] != "EXISTING_PUBLIC_EDITION_CROSSWALK_DUPLICATE" or
                        row["publisher_url"] != entropy[0]["publisher_product_url"] or
                        row["publisher_page_isbn13"] != ENTROPY):
                    raise ValueError("existing accepted public edition not crosschecked")
            elif row["publisher_url"] is not None or row["publisher_page_isbn13"] is not None:
                raise ValueError("unreviewed publisher association on held row")
        relations[row["publisher_relation"]] += 1
    if {int(x.split(":")[1]) for x in seen_opf} != SOURCE_IDS:
        raise ValueError("unreviewed source ID selection")
    if (relations != {"EXACT_ISBN_OFFICIAL_PUBLISHER": 4,
                      "SAME_WORK_DIFFERENT_OFFICIAL_ISBN_HOLD": 3,
                      "EXISTING_PUBLIC_EDITION_CROSSWALK_DUPLICATE": 1,
                      "NOT_EVALUATED_NO_IMAGE": 10,
                      "NOT_EVALUATED_UNRESOLVED_ISBN": 2}):
        raise ValueError("edition identity or held denominator drifted")
    return {"opf_metadata_rows": 20, "distinct_opf_entry_digests": 20,
            "open_library_responses_200": 18, "open_library_responses_404": 2,
            "medium_title_jackets_held": 7, "exact_publisher_isbn_matches": 4,
            "different_publisher_isbn_holds": 3, "no_cover_field_holds": 11,
            "existing_public_edition_duplicate": 1, "source_or_work_admissions": 0,
            "images_released": 0}


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
