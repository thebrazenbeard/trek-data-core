#!/usr/bin/env python3
"""Validate that fixed and synthetic drift fixtures preserve required invariants."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "drift-regressions.json"
ALLOWED = {
    "NO_SILENT_SAME_AS",
    "IDENTITY_AMBIGUITY_REPRESENTABLE",
    "SCOPE_PRESERVED",
    "CONTRADICTION_NOT_FORCED_RESOLVED",
    "REPORT_NOT_AUTO_WORLD_FACT",
    "UNKNOWN_STRUCTURE_REPRESENTABLE",
    "NO_EVIDENCE_DISCARD",
    "CONFLICT_REPRESENTABLE",
    "NO_FAKE_CONFIDENCE_SCORE",
}


def main() -> int:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors = []
    groups = ("known_difficult", "synthetic_adversarial")
    seen = set()
    for group in groups:
        cases = data.get(group)
        if not isinstance(cases, list) or not cases:
            errors.append(f"{group}: must contain at least one fixture")
            continue
        for case in cases:
            cid = case.get("id")
            if not cid or cid in seen:
                errors.append(f"{group}: missing or duplicate fixture id {cid!r}")
            seen.add(cid)
            if not isinstance(case.get("input"), dict):
                errors.append(f"{cid}: input must be an object")
            invariants = case.get("required_invariants")
            if not isinstance(invariants, list) or not invariants:
                errors.append(f"{cid}: required_invariants must be non-empty")
                continue
            unknown = sorted(set(invariants) - ALLOWED)
            if unknown:
                errors.append(f"{cid}: unknown invariants {unknown}")
    if errors:
        print("DRIFT FIXTURE VALIDATION FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"DRIFT FIXTURE VALIDATION PASSED: {len(seen)} fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
