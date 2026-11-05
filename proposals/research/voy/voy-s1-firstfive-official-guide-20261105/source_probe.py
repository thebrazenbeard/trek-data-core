"""Inspect the complete English-US Paramount+ VOY S1 guide, without persisting prose.

Publisher cards are not viewed episodes or canonical Work admissions. The US guide
currently combines both Caretaker parts into one card. German-locale pages may
represent the pilot separately; these are different *publisher observations*.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.request


URL = "https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/"
PREFIX = "Star Trek: Voyager - "
ANCHOR = re.compile(r'<a\s+href="(?P<route>/shows/video/[^"\s]+/)"\s+aa-link="(?P<analytics>episodes\|\|[^"]+)"[^>]*>', re.I)
TITLE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
SEASON = re.compile(r'<abbr\s+class=[\'\"]seNum[\'\"]\s+title="Season ([0-9]+)">S([0-9]+)</abbr>')
EPISODE = re.compile(r'<abbr\s+class=[\'\"]epNum[\'\"]\s+title="Episode ([0-9]+)">E([0-9]+)</abbr>')
DATE = re.compile(r'<time[^>]*\sdatetime="([^"]+)"')
COPY = re.compile(r'<div\s+class="ep__copy[^"]*"[^>]*>(.*?)</div>', re.S)


def clean(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_page(body: str) -> tuple[list[dict], list[str]]:
    anchors = list(ANCHOR.finditer(body))
    cards: list[dict] = []
    descriptions: list[str] = []
    for i, anchor in enumerate(anchors):
        fields = html.unescape(anchor.group("analytics")).split("|")
        if len(fields) < 6 or not fields[2].startswith(PREFIX):
            continue
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(body)
        chunk = body[anchor.end():end]
        title = TITLE.search(chunk)
        season = SEASON.search(chunk)
        episode = EPISODE.search(chunk)
        date = DATE.search(chunk)
        copy = COPY.search(chunk)
        if not all((title, season, episode, date, copy)):
            raise ValueError("incomplete first-party episode guide card")
        display_title, description = clean(title.group(1)), clean(copy.group(1))
        order = len(cards) + 1
        if not description or not fields[3].isdigit() or int(fields[3]) != order:
            raise ValueError("empty copy or publisher analytics/display order conflict")
        if display_title.casefold() != fields[5].casefold() or fields[2].casefold() != (PREFIX + fields[5]).casefold():
            raise ValueError("title mismatch against publisher analytics")
        if season.group(1) != season.group(2) or episode.group(1) != episode.group(2):
            raise ValueError("season/episode badge mismatch")
        cards.append({
            "guide_order": order,
            "publisher_analytics_ordinal": int(fields[3]),
            "season_badge": int(season.group(1)),
            "episode_badge": int(episode.group(1)),
            "display_title": display_title,
            "video_route_path": anchor.group("route"),
            "publisher_datetime": date.group(1),
            "html_anchor_line": body.count("\n", 0, anchor.start()) + 1,
            "html_description_line": body.count("\n", 0, anchor.end() + copy.start()) + 1,
            "description_chars": len(description),
            "description_sha256": hashlib.sha256(description.encode("utf8")).hexdigest(),
        })
        descriptions.append(description)
    if len(cards) != 15 or [c["episode_badge"] for c in cards] != [1, *range(3, 17)]:
        raise ValueError("US publisher S1 guide expected 15 cards with combined pilot, then badges 3..16")
    if any(c["season_badge"] != 1 for c in cards) or len({c["video_route_path"] for c in cards}) != 15:
        raise ValueError("publisher card count, season, or URL identity inconsistent")
    if cards[0]["display_title"] != "Caretaker, Part 1 & 2":
        raise ValueError("US combined pilot title changed")
    return cards, descriptions


def main() -> int:
    if any(arg not in ("--stdin", "--internal-prose") for arg in sys.argv[1:]):
        print("usage: source_probe.py [--stdin] [--internal-prose]", file=sys.stderr)
        return 2
    if "--stdin" in sys.argv:
        raw, status, date = sys.stdin.buffer.read(), None, None
    else:
        request = urllib.request.Request(URL, headers={"User-Agent": "TrekResearch VOY S1 source observer/1.0", "Accept-Language": "en-US,en;q=0.9"})
        with urllib.request.urlopen(request, timeout=35) as response:
            raw, status, date = response.read(), response.status, response.headers.get("Date")
    try:
        cards, prose = parse_page(raw.decode("utf8", errors="replace"))
    except ValueError as exc:
        print("FAIL CLOSED: " + str(exc), file=sys.stderr)
        return 1
    source_digest = hashlib.sha256(json.dumps(cards, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")).hexdigest()
    output = {
        "url": URL,
        "observed_locale": "en-US",
        "response_http_status": status,
        "response_date_header": date,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes": len(raw),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "normalized_all_15_card_sha256": source_digest,
        "guide_card_count": len(cards),
        "first_five_description_chars": sum(map(len, prose[:5])),
        "source_text_committed": False,
        "first_five_cards": cards[:5],
    }
    if "--internal-prose" in sys.argv:
        output["first_five_private_descriptions_not_for_commit"] = prose[:5]
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
