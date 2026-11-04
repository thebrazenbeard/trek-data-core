"""Read-only official Picard S3 guide parser; never fetches video/images.

The page body is processed in memory and discarded. Standard output contains
only nonexpressive card metadata and hashes of source descriptions.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.request

URL = "https://www.paramountplus.com/shows/star-trek-picard/episodes/3/"
SERIES_PREFIX = "Star Trek: Picard - "
ANCHOR = re.compile(r'<a\s+href="(?P<route>/shows/video/[^"\s]+/)"\s+aa-link="(?P<analytics>episodes\|\|[^"]+)"[^>]*>', re.I)
TITLE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
SEASON = re.compile(r'<abbr\s+class=[\'"]seNum[\'"]\s+title="Season ([0-9]+)">S([0-9]+)</abbr>')
EPISODE = re.compile(r'<abbr\s+class=[\'"]epNum[\'"]\s+title="Episode ([0-9]+)">E([0-9]+)</abbr>')
DATE = re.compile(r'<time[^>]*\sdatetime="([^"]+)"')
COPY = re.compile(r'<div\s+class="ep__copy[^\"]*"[^>]*>(.*?)</div>', re.S)


def clean_text(markup: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip()


def parse_page(page_html: str) -> tuple[list[dict], list[str]]:
    anchors = list(ANCHOR.finditer(page_html))
    rows, descriptions = [], []
    for idx, anchor in enumerate(anchors):
        parts = html.unescape(anchor.group("analytics")).split("|")
        if len(parts) < 6 or not parts[2].startswith(SERIES_PREFIX):
            continue
        stop = anchors[idx + 1].start() if idx + 1 < len(anchors) else len(page_html)
        card = page_html[anchor.end():stop]
        title = TITLE.search(card)
        season = SEASON.search(card)
        episode = EPISODE.search(card)
        published = DATE.search(card)
        copy = COPY.search(card)
        if not all((title, season, episode, published, copy)):
            raise ValueError(f"incomplete first-party card at HTML line {page_html.count(chr(10),0,anchor.start())+1}")
        title_text = clean_text(title.group(1))
        desc = clean_text(copy.group(1))
        if not desc:
            raise ValueError("empty first-party card description")
        if not parts[3].isdigit() or parts[5] != title_text or parts[2] != SERIES_PREFIX + title_text:
            raise ValueError("analytics/title mismatch")
        if season.group(1) != season.group(2) or episode.group(1) != episode.group(2):
            raise ValueError("visible season/episode badge mismatch")
        ordinal = int(episode.group(1))
        if int(parts[3]) != ordinal:
            raise ValueError("analytics vs displayed ordinal mismatch")
        rows.append({
            "display_order": len(rows) + 1,
            "season": int(season.group(1)),
            "episode": ordinal,
            "analytics_ordinal": int(parts[3]),
            "title": title_text,
            "video_route_path": anchor.group("route"),
            "publisher_datetime": published.group(1),
            "html_anchor_line": page_html.count("\n", 0, anchor.start()) + 1,
            "html_description_line": page_html.count("\n", 0, anchor.end() + copy.start()) + 1,
            "description_chars": len(desc),
            "description_sha256": hashlib.sha256(desc.encode("utf-8")).hexdigest(),
        })
        descriptions.append(desc)
    if len({r["video_route_path"] for r in rows}) != len(rows):
        raise ValueError("duplicate video route")
    if len({(r["season"], r["episode"]) for r in rows}) != len(rows):
        raise ValueError("duplicate season/episode label")
    return rows, descriptions


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--stdin"):
        print("usage: python3 source_probe.py [--stdin]", file=sys.stderr)
        return 2
    if len(sys.argv) == 2:
        raw, status, date_header = sys.stdin.buffer.read(), None, None
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "TrekResearch PIC S3 source observer/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw, status, date_header = response.read(), response.status, response.headers.get("Date")
    try:
        cards, descriptions = parse_page(raw.decode("utf-8", errors="replace"))
    except ValueError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "url": URL, "response_status": status, "response_date_header": date_header,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes": len(raw), "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_html_committed": False, "card_count_observed": len(cards),
        "cards": cards,
        "first_five_description_total_chars": sum(map(len, descriptions[:5])),
        "first_five_descriptions_inspected_in_memory_not_committed": len(descriptions[:5]),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
