"""Deterministic shape and drift checks; never authenticate private source bytes."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINNED_RECEIPT_SHA256 = "0207a7288851890dee074f9c44f60331ce7981c5f7ddeed9e891df4a4251e444"
source = (HERE / "RECEIPT.json").read_bytes()
if hashlib.sha256(source).hexdigest() != PINNED_RECEIPT_SHA256:
    raise ValueError("public receipt file changed without code review")
EXPECTED = json.loads(source)


def validate(candidate):
    if not isinstance(candidate, dict) or set(candidate) != set(EXPECTED):
        raise ValueError("source custody field set drift")
    for key, expected in EXPECTED.items():
        if type(candidate[key]) is not type(expected) or candidate[key] != expected:
            raise ValueError(f"source custody observation drift: {key}")
    for key in (
        "accepted_source_binding_effect", "accepted_work_effect", "coverage_effect"
    ):
        if candidate[key] != "NONE":
            raise ValueError("unauthorized research admission")
    for key in (
        "original_lit_content_parsed", "conversion_equivalence_verified",
        "complete_edition_verified", "close_read_performed",
        "rights_to_publish_text_or_art", "public_source_bytes"
    ):
        if candidate[key] is not False:
            raise ValueError("unsupported source qualification")
    return True


if __name__ == "__main__":
    validate(EXPECTED)
    print("Original LIT custody proposal validated (private source unverified)")
