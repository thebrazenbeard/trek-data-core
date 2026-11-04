"""Read-only ENT S2 E21–E26 publisher guide; full HTML parsed, six descriptions.

Uses the exact prior S2 parser. Raw copyrighted HTML and publisher paragraphs
are never written to the repository. --internal-prose is private inspection.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

PREDECESSOR_EXTRACTOR=Path(__file__).resolve().parent.parent/"enterprise-s2-first5-official-guide-20261104/source_probe.py"


def publisher_parser():
    spec=importlib.util.spec_from_file_location("ent_s2_first5_parser",PREDECESSOR_EXTRACTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("exact predecessor source parser unavailable")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main()->int:
    if any(a not in ("--stdin","--internal-prose") for a in sys.argv[1:]):
        print("usage: source_probe.py [--stdin] [--internal-prose]",file=sys.stderr)
        return 2
    parser=publisher_parser()
    if "--stdin" in sys.argv:
        raw,status,date=sys.stdin.buffer.read(),None,None
    else:
        req=urllib.request.Request(parser.URL,headers={"User-Agent":"TrekResearch ENT S2 E21-E26 observer/1.0"})
        with urllib.request.urlopen(req,timeout=30) as response:
            raw,status,date=response.read(),response.status,response.headers.get("Date")
    try:
        cards,descriptions=parser.parse_page(raw.decode("utf8",errors="replace"))
    except ValueError as exc:
        print("FAIL CLOSED: "+str(exc),file=sys.stderr)
        return 1
    result={
        "url":parser.URL,
        "response_http_status":status,
        "response_date_header":date,
        "observed_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes":len(raw),
        "raw_response_sha256":hashlib.sha256(raw).hexdigest(),
        "raw_html_committed":False,
        "observed_card_count":len(cards),
        "final_six_description_total_chars":sum(map(len,descriptions[20:26])),
        "all_cards":cards,
    }
    if "--internal-prose" in sys.argv:
        result["final_six_private_descriptions_not_for_commit"]=descriptions[20:26]
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    sys.exit(main())
