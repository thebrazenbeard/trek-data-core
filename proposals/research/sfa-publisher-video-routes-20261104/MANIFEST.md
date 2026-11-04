# Starfleet Academy — held publisher episode video routes

**Proposal:** `SFA-PUBLISHER-VIDEO-ROUTES-20261104-001` · **role:** SFA audiovisual worker · **observed:** 2026-11-04 UTC · **status:** `HELD_PUBLISHER_SOURCE_ROUTE_METADATA`.

This adds a **source route**, not episode research or accepted episode inventory. Accepted baseline was `main@3028765359001b90bc3e6b5c1835ee283b326e91`. The [existing Librarian publisher roster](../../librarian/sfa-publisher-roster-20261102/MANIFEST.md) and [SFA press-page refresh](../sfa-publisher-refresh-20261103/MANIFEST.md) already record ten Season 1 **publisher slots**. The new observed fields are the official Paramount+ card links to ten distinct `/shows/video/{id}/` routes and ten publisher HTML `<time datetime>` strings. No streamed content, full text, audiovisual frames, dialogue, plot or episode scripts were retrieved or processed.

## Retrieval receipt and lineage

On 2026-11-04 UTC, a read-only `urllib.request.urlopen` GET from the connected Lappy WSL host returned HTTP 200 for [the Paramount+ Starfleet Academy episode guide](https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/):

- Raw UTF-8 HTML response: **267,531 bytes**.
- SHA-256 of this exact retrieved byte stream: `cb6eea564eabe64343a3ee1b07d5dd52507fba61c2263d8b6b8bc39f5867b637`.
- Parsed the episode-card anchor href, `h2` title, visible `S1`/`E1`–`E10` labels, and publisher HTML time attributes. Anchor source-local line locators are retained in `records.json` (lines 1405–1657 in this exact response).
- The raw HTML bytes were not persisted, nor was an independent signature obtained. The page is mutable, includes image links and dynamic material, and a subsequent retrieval yielded a different response hash. The hash describes **one retrieval**, not a stable edition or future independently replayable copy.
- This is the **same `publisher:paramount` lineage** as the earlier Paramount+ and Paramount Press Express observations. Agreement is dependent, not independent confirmation of any fictional-world proposition.

The ten link paths remain on the official publisher host when prefixed with `https://www.paramountplus.com`; they are *discovery routes*, **not** evidence that the videos were accessed, that the user has streaming entitlement, or that the underlying media Source has been admitted. Dates are literal publisher page datetime strings, not independently verified original broadcast dates or fictional chronology. The exact official page title shown for S1E10 is `Rubincon`; preserve it without silently rewriting conflicting outside spellings.

## No protected effects

- Accepted Work effect: `NONE`.
- Source↔Work binding effect: `NONE` (governance issue #23 remains open).
- Coverage, denominator and reconciliation effects: `NONE`.
- No audiovisual CLOSE_READ, no `FULL_TEXT_AVAILABLE`, no semantic character/event assertions, and no public artwork rights established.
- No video URL visited; only the public HTML listing was fetched. No streaming bypass, image copying, media redistribution, credential or paid action.

> **Hostile review:** The presence of ten `/shows/video/` anchors in one publisher listing does not prove ten playable, complete, region-available or authorized media Sources. Treating each HTML route as a validated `FULL_TEXT_AVAILABLE` Source↔Work binding would cross both an evidence boundary and the unresolved governance admission gate.

> **Custody challenge:** An unhashed, unarchived *future* publisher page cannot replay this exact snapshot. The recorded raw response hash helps distinguish observations but is insufficient for independent content authentication by itself.

## Validation

From repository root:

```bash
python3 proposals/research/sfa-publisher-video-routes-20261104/validate.py
python3 -m unittest discover -s proposals/research/sfa-publisher-video-routes-20261104 -p test_validate.py -v
python3 tools/validate.py
```

The validator cross-checks source-relative slots against the already-accepted **publisher proposal**, enforces route confinement to publisher-local video paths, checks uniqueness/date syntax/source lineage, and rejects any added Work, coverage, audiovisual or rights promotion. It validates structured consistency, **not the remote response bytes or episode content**.

## Exact next frontier

The Librarian/Consolidator must resolve issue #23 and admit governed Source↔Work relationships before any episode content batch. A later authorized worker can examine rights-valid primary audiovisual media or authenticated scripts and record independently reproducible source/version locators. A later SFA read-only refresh should detect publisher route changes without mistaking changed HTML hashes for fictional continuity changes.
