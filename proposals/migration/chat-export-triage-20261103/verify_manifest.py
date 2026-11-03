"""Offline, fail-closed structural check for an unadmitted chat-export queue.

This deliberately does not read or authenticate the privately held archive.
"""

import json
import re
from pathlib import Path


def verify(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("record_class") != "HISTORICAL_CHAT_CLAIM_TRIAGE":
        raise ValueError("wrong record class")
    if data.get("admission") != "NOT_ADMITTED":
        raise ValueError("chat claims cannot be admitted research")
    for field in (
        "accepted_research_effect",
        "coverage_effect",
        "denominator_effect",
        "source_work_binding_effect",
        "reconciliation_effect",
    ):
        if data.get(field) != "NONE":
            raise ValueError(f"unsafe effect: {field}")
    if not re.fullmatch(r"[a-f0-9]{40}", data.get("accepted_main_at_intake", "")):
        raise ValueError("unpinned main")
    source = data.get("source", {})
    for digest in ("archive_sha256", "html_member_sha256"):
        if not re.fullmatch(r"[a-f0-9]{64}", source.get(digest, "")):
            raise ValueError(f"missing artifact digest: {digest}")
    if source.get("kind") != "USER_SUPPLIED_SAVED_CHATGPT_WEB_PAGE_ARCHIVE":
        raise ValueError("chat page misclassified as original source")
    queue = data.get("review_queue")
    if not isinstance(queue, list) or not queue:
        raise ValueError("empty review queue")
    seen = set()
    allowed_states = {
        "CHAT_REPORT_WITH_PARTIAL_ACCEPTED_PROPOSAL_OVERLAP",
        "CHAT_REPORT_NOT_REPLAYED",
        "ARCHIVE_HAS_NO_BOOK_CONTENT_EVIDENCE",
    }
    for row in queue:
        identifier = row.get("id")
        if not isinstance(identifier, str) or identifier in seen:
            raise ValueError("duplicate or invalid lead ID")
        seen.add(identifier)
        if row.get("claimant") != "HISTORICAL_ASSISTANT_IN_CHAT":
            raise ValueError("unverified chat claimant misclassified")
        if row.get("verification_state") not in allowed_states:
            raise ValueError("unsupported verification promotion")
        span = row.get("rendered_text_lines")
        if (not isinstance(span, list) or len(span) != 2 or
                not all(type(n) is int and n > 0 for n in span) or
                span[0] > span[1]):
            raise ValueError("invalid rendered-text locator")
        if not row.get("historical_claim") or not row.get("next_gate"):
            raise ValueError("lead lacks interpretation or next check")
        if not isinstance(row.get("accepted_main_overlap"), list):
            raise ValueError("untraceable accepted-main comparison")


if __name__ == "__main__":
    verify(Path(__file__).with_name("MANIFEST.json"))
    print("CHAT_EXPORT_TRIAGE_VALID: unadmitted queue, eight leads, no effects")
