"""Read-only full Enterprise S4 publisher guide, local E06–E10 description tranche.

Imports exactly the predecessor's source parser. Keeps raw HTML and publisher
paragraphs in memory, with optional private prose inspection only.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

PREDECESSOR_EXTRACTOR = Path(__file__).resolve().parent.parent / "enterprise-s4-first5-official-guide-20261104/source_probe.py"


def publisher_parser():
    spec = importlib.util.spec_from_file_location("ent_s4_first_five_probe", PREDECESSOR_EXTRACTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("held predecessor parser unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if any(x not in ("--stdin", "--internal-prose") for x in sys.argv[1:]):
        print("usage: source_probe.py [--stdin] [--internal-prose]", file=sys.stderr)
        return 2
    parser = publisher_parser()
    if "--stdin" in sys.argv:
        raw, status, response_date = sys.stdin.buffer.read(), None, None
    else:
        request = urllib.request.Request(parser.URL, headers={"User-Agent": "TrekResearch ENT S4 E06-E10 observer/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw, status, response_date = response.read(), response.status, response.headers.get("Date")
    try:
        cards, descriptions = parser.parse_page(raw.decode("utf-8", errors="replace"))
    except ValueError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 1
    result = {
        "url": parser.URL, "response_http_status": status,
        "response_date_header": response_date,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes": len(raw), "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_html_committed": False, "observed_card_count": len(cards),
        "second_five_description_total_chars": sum(map(len, descriptions[5:10])),
        "all_cards": cards,
    }
    if "--internal-prose" in sys.argv:
        result["second_five_private_descriptions_not_for_commit"] = descriptions[5:10]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
