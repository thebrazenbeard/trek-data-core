"""Read the full first-party ENT S1 guide in memory; never persist source prose.

The publisher represents the two-part pilot as one guide card, so its display
order, analytics ordinal and episode badge are deliberately separate fields.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.request

URL = "https://www.paramountplus.com/shows/enterprise/episodes/1/"
SERIES_PREFIX = "Star Trek: Enterprise - "
ANCHOR = re.compile(r'<a\s+href="(?P<route>/shows/video/[^"\s]+/)"\s+aa-link="(?P<analytics>episodes\|\|[^"]+)"[^>]*>', re.I)
TITLE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
SEASON = re.compile(r'<abbr\s+class=[\'\"]seNum[\'\"]\s+title="Season ([0-9]+)">S([0-9]+)</abbr>')
EPISODE = re.compile(r'<abbr\s+class=[\'\"]epNum[\'\"]\s+title="Episode ([0-9]+)">E([0-9]+)</abbr>')
DATE = re.compile(r'<time[^>]*\sdatetime="([^"]+)"')
COPY = re.compile(r'<div\s+class="ep__copy[^"]*"[^>]*>(.*?)</div>', re.S)


def clean_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_page(body: str) -> tuple[list[dict], list[str]]:
    anchors = list(ANCHOR.finditer(body))
    cards: list[dict] = []
    descriptions: list[str] = []
    for i, anchor in enumerate(anchors):
        parts = html.unescape(anchor.group("analytics")).split("|")
        if len(parts) < 6 or not parts[2].startswith(SERIES_PREFIX):
            continue
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(body)
        chunk = body[anchor.end():end]
        title, season, episode, date, copy = (TITLE.search(chunk), SEASON.search(chunk),
                                              EPISODE.search(chunk), DATE.search(chunk), COPY.search(chunk))
        if not all((title, season, episode, date, copy)):
            raise ValueError("incomplete publisher card")
        display_title = clean_text(title.group(1))
        description = clean_text(copy.group(1))
        if not description or not parts[3].isdigit():
            raise ValueError("empty description or nonnumeric analytics ordinal")
        if display_title.casefold() != parts[5].casefold() or parts[2].casefold() != (SERIES_PREFIX + parts[5]).casefold():
            raise ValueError("publisher title/analytics disagreement")
        if season.group(1) != season.group(2) or episode.group(1) != episode.group(2):
            raise ValueError("publisher badge disagreement")
        order = len(cards) + 1
        if int(parts[3]) != order:
            raise ValueError("publisher analytics/display order mismatch")
        cards.append({
            "display_order": order,
            "analytics_ordinal": int(parts[3]),
            "season": int(season.group(1)),
            "episode_badge": int(episode.group(1)),
            "title": display_title,
            "video_route_path": anchor.group("route"),
            "publisher_datetime": date.group(1),
            "html_anchor_line": body.count("\n", 0, anchor.start()) + 1,
            "html_description_line": body.count("\n", 0, anchor.end() + copy.start()) + 1,
            "description_chars": len(description),
            "description_sha256": hashlib.sha256(description.encode("utf8")).hexdigest(),
        })
        descriptions.append(description)
    if len(cards) != 25 or [c["episode_badge"] for c in cards] != [1, *range(3, 27)]:
        raise ValueError("S1 25 guide cards with composite pilot badge 1, then badge 3..26 expected")
    if any(c["season"] != 1 for c in cards) or len({c["video_route_path"] for c in cards}) != 25:
        raise ValueError("S1 season/route identity conflict")
    if cards[0]["title"] != "Broken Bow - Part 1 and 2":
        raise ValueError("composite pilot title changed; review source anew")
    return cards, descriptions


def main() -> int:
    if any(arg not in ("--stdin", "--internal-prose") for arg in sys.argv[1:]):
        print("usage: source_probe.py [--stdin] [--internal-prose]", file=sys.stderr)
        return 2
    if "--stdin" in sys.argv:
        raw, status, date = sys.stdin.buffer.read(), None, None
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "TrekResearch ENT S1 source observer/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            raw, status, date = response.read(), response.status, response.headers.get("Date")
    try:
        cards, prose = parse_page(raw.decode("utf8", errors="replace"))
    except ValueError as exc:
        print("FAIL CLOSED: " + str(exc), file=sys.stderr)
        return 1
    normalized = json.dumps(cards, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")
    result = {
        "url": URL,
        "response_http_status": status,
        "response_date_header": date,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes": len(raw),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "all_cards_fingerprint_sha256": hashlib.sha256(normalized).hexdigest(),
        "raw_html_committed": False,
        "observed_publisher_guide_cards": len(cards),
        "first_five_description_chars": sum(map(len, prose[:5])),
        "first_five_cards": cards[:5],
        "all_25_cards": cards,
    }
    if "--internal-prose" in sys.argv:
        result["first_five_private_descriptions_not_for_commit"] = prose[:5]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
