"""Proposed OPF ISBN-only extraction; never admits editions or reads book prose.

This deliberately reuses the repository's bounded, no-DTD OPF metadata parser.
The original owner-host extraction implementation is not present in this repo;
the synthetic regression tests a plausible missed-token *class*, not a proven
historical root cause. This module remains a held LIT research proposal.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.inventory_opf_metadata import opf_metadata_with_legacy_review


PREFIX = re.compile(r"^(?:isbn(?:-?(?:10|13))?|urn:isbn)\s*[:=]?\s*", re.IGNORECASE)
ISBN_CHARS = re.compile(r"^[0-9Xx][0-9Xx\- ]*$")


def normalized_checksum_isbn(literal: str) -> str | None:
    """Only a whole bare/prefixed ISBN, not a substring in UUID/free text."""
    value = literal.strip()
    value = PREFIX.sub("", value, count=1).strip()
    if not ISBN_CHARS.fullmatch(value):
        return None
    compact = re.sub(r"[- ]", "", value).upper()
    if len(compact) == 10 and re.fullmatch(r"[0-9]{9}[0-9X]", compact):
        total = sum((10 - i) * int(c) for i, c in enumerate(compact[:9]))
        total += 10 if compact[-1] == "X" else int(compact[-1])
        return compact if total % 11 == 0 else None
    if len(compact) == 13 and compact.isdecimal():
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(compact))
        return compact if total % 10 == 0 else None
    return None


def extract_candidates(raw: bytes) -> dict:
    """Read only whitelisted OPF XML metadata through the secure intake parser.

    Return only checksum-valid ISBN candidates and review status. No arbitrary
    identifier literals, GUIDs, member paths, book descriptions or source
    text are returned. No conversion is assumed to identify a private edition.
    """
    metadata, repaired = opf_metadata_with_legacy_review(raw)
    candidates = {candidate for literal in metadata["identifiers"]
                  if (candidate := normalized_checksum_isbn(literal)) is not None}
    return {
        "isbn10_candidates": sorted(x for x in candidates if len(x) == 10),
        "isbn13_candidates": sorted(x for x in candidates if len(x) == 13),
        "source_xml_review_hold": repaired,
    }
