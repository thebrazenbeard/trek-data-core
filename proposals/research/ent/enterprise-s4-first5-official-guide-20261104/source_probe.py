"""Read-only first-party Enterprise S4 HTML metadata and synopsis fingerprint probe.

Reads the entire HTML response in memory. Does not fetch audiovisual, images or
transcripts. The --internal-prose flag prints source paragraphs solely for the
researcher's private reading; do not commit, copy, or republish that output.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.request

URL = "https://www.paramountplus.com/shows/enterprise/episodes/4/"
SERIES_PREFIX = "Enterprise - "
ANCHOR = re.compile(r'<a\s+href="(?P<route>/shows/video/[^"\s]+/)"\s+aa-link="(?P<analytics>episodes\|\|[^"]+)"[^>]*>', re.I)
TITLE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
SEASON = re.compile(r'<abbr\s+class=[\'\"]seNum[\'\"]\s+title="Season ([0-9]+)">S([0-9]+)</abbr>')
EPISODE = re.compile(r'<abbr\s+class=[\'\"]epNum[\'\"]\s+title="Episode ([0-9]+)">E([0-9]+)</abbr>')
DATE = re.compile(r'<time[^>]*\sdatetime="([^"]+)"')
COPY = re.compile(r'<div\s+class="ep__copy[^\"]*"[^>]*>(.*?)</div>', re.S)


def clean_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse_page(body: str) -> tuple[list[dict], list[str]]:
    anchors = list(ANCHOR.finditer(body))
    cards, descriptions = [], []
    for index, anchor in enumerate(anchors):
        parts = html.unescape(anchor.group("analytics")).split("|")
        if len(parts) < 6 or not parts[2].startswith(SERIES_PREFIX):
            continue
        stop = anchors[index + 1].start() if index + 1 < len(anchors) else len(body)
        chunk = body[anchor.end():stop]
        title, season, episode, date, copy = (
            TITLE.search(chunk), SEASON.search(chunk), EPISODE.search(chunk),
            DATE.search(chunk), COPY.search(chunk),
        )
        if not all((title, season, episode, date, copy)):
            raise ValueError("incomplete publisher guide card")
        title_text = clean_text(title.group(1))
        prose = clean_text(copy.group(1))
        if not prose:
            raise ValueError("empty publisher guide description")
        analytics_title = parts[5]
        if not parts[3].isdigit() or parts[2].casefold() != (SERIES_PREFIX + analytics_title).casefold() or analytics_title.casefold() != title_text.casefold():
            raise ValueError(f"analytics/title identity conflict beyond capitalization variants at card {len(cards)+1}: {analytics_title!r} versus {title_text!r}")
        if season.group(1) != season.group(2) or episode.group(1) != episode.group(2):
            raise ValueError("season/episode badge conflict")
        ordinal = int(episode.group(1))
        if int(parts[3]) != ordinal:
            raise ValueError("analytics/display ordinal conflict")
        cards.append({
            "display_order": len(cards) + 1,
            "season": int(season.group(1)),
            "episode": ordinal,
            "analytics_ordinal": int(parts[3]),
            "title": title_text,
            "analytics_title": analytics_title,
            "analytics_series_title": parts[2].removeprefix(SERIES_PREFIX),
            "title_variant_status": "EXACT_MATCH" if parts[2] == SERIES_PREFIX + analytics_title and analytics_title == title_text else "CAPITALIZATION_VARIANT_UNRESOLVED",
            "video_route_path": anchor.group("route"),
            "publisher_datetime": date.group(1),
            "html_anchor_line": body.count("\n", 0, anchor.start()) + 1,
            "html_description_line": body.count("\n", 0, anchor.end() + copy.start()) + 1,
            "description_chars": len(prose),
            "description_sha256": hashlib.sha256(prose.encode("utf-8")).hexdigest(),
        })
        descriptions.append(prose)
    if len(cards) != 22 or [c["episode"] for c in cards] != list(range(1, 23)):
        raise ValueError("incomplete Enterprise S4 guide: expected exactly 22 ordered publisher cards")
    if any(c["season"] != 4 for c in cards):
        raise ValueError("mixed seasons on Enterprise S4 guide")
    if len({c["video_route_path"] for c in cards}) != len(cards):
        raise ValueError("duplicated source video route")
    return cards, descriptions


def main() -> int:
    if any(flag not in ("--stdin", "--internal-prose", "--diagnose") for flag in sys.argv[1:]):
        print("usage: source_probe.py [--stdin] [--internal-prose] [--diagnose]", file=sys.stderr)
        return 2
    if "--stdin" in sys.argv:
        raw, status, response_date = sys.stdin.buffer.read(), None, None
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "TrekResearch ENT S4 source observer/1.0"})
        with urllib.request.urlopen(req, timeout=30) as result:
            raw, status, response_date = result.read(), result.status, result.headers.get("Date")
    try:
        cards, descriptions = parse_page(raw.decode("utf-8", errors="replace"))
    except ValueError as exc:
        if "--diagnose" in sys.argv:
            body = raw.decode("utf-8", errors="replace")
            anchors = list(ANCHOR.finditer(body))
            observations = []
            for index, anchor in enumerate(anchors):
                parts = html.unescape(anchor.group("analytics")).split("|")
                if len(parts) < 6 or not parts[2].startswith(SERIES_PREFIX):
                    continue
                stop = anchors[index + 1].start() if index + 1 < len(anchors) else len(body)
                chunk = body[anchor.end():stop]
                title, season, episode = TITLE.search(chunk), SEASON.search(chunk), EPISODE.search(chunk)
                observations.append({
                    "analytics_parts": parts[:6], "title": clean_text(title.group(1)) if title else None,
                    "season": season.group(1) if season else None,
                    "episode": episode.group(1) if episode else None,
                    "line": body.count("\n", 0, anchor.start()) + 1,
                })
            print(json.dumps({"url": URL, "raw_response_bytes": len(raw),
                              "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
                              "anchor_count": len(anchors), "observations": observations}, indent=2))
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 1
    result = {
        "url": URL, "response_http_status": status, "response_date_header": response_date,
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "raw_response_bytes": len(raw), "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_html_committed": False, "observed_card_count": len(cards),
        "first_five_description_total_chars": sum(map(len, descriptions[:5])),
        "all_cards": cards,
    }
    if "--internal-prose" in sys.argv:
        result["first_five_private_descriptions_not_for_commit"] = descriptions[:5]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
