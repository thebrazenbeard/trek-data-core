# DS9 S7E12–E16: official publisher guide and date-display provenance

**Role:** DS9. **Accepted main checked:** `f7c111f351ab2f0eb629883a045ffc697c3d3209`, 2026-11-03 UTC. **Proposal only:** zero admitted Source↔Work, Work, full episode/script, public synopsis, or coverage effects.

## What was actually read

Five contiguous original guide-card titles, season/episode ordinals and short publisher descriptions were read from the official [Paramount+ DS9 Season 7 guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/). Official Paramount+ [all-episodes listings](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/) and matching episode-detail page search-index excerpts separately displayed dates. **The date strings were retrieved from first-party page search excerpts, not authenticated raw HTML; their meaning and timezone were not established.**

| Source-local row | Publisher title / slot | All-episodes listing date | Episode-detail header date |
| --- | --- | --- | --- |
| `publisher:s7:ds9:011` | *The Emperor's New Cloak* — S7E12 | Jan 4, 1999 | Jan 3, 1999 |
| `publisher:s7:ds9:012` | *Field of Fire* — S7E13 | Feb 1, 1999 | Jan 31, 1999 |
| `publisher:s7:ds9:013` | *Chimera* — S7E14 | Feb 8, 1999 | Feb 7, 1999 |
| `publisher:s7:ds9:014` | *Badda-Bing, Badda-Bang* — S7E15 | Feb 22, 1999 | Feb 21, 1999 |
| `publisher:s7:ds9:015` | *Inter Arma Enim Silent Leges* — S7E16 | Feb 15, 1999 | Feb 14, 1999 |

Each title/slot matches the earlier accepted `publisher-season7-20261102/ds9.csv` source-local observation. That historical CSV SHA-256 is `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea`; the old HTML capture was separately recorded as `23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1`. **Neither digest represents a new HTML capture or actual episode audiovisual bytes.** The two Paramount date displays are **the same corporate source lineage**, not independent corroboration.

## Held distinctions

`observations.json` records five exact publisher card positions, separate exact detail-page locators, and the two dates as **unresolved displayed values**, not verified air dates. One same-family date difference occurs in all five pairs (listing is one day later). In addition, the listing displays S7E16 as February 15, earlier than S7E15 February 22, even though its episode ordinal is greater. Neither pattern is interpreted as a confirmed mistake, timezone conversion or release order.

Five new original short-description paraphrases are proposed for **editorial review only**; they do not summarize episodes watched, reproduce publisher blurb text, establish fictional events, or populate the public Explorer. `assertions.json` records unresolved, falsifiable source-metadata questions, not canon or global Work identity.

> **Hostile source challenge:** A date displayed on a streaming service's search-indexed page is not automatically a broadcast date. One-day differences could have multiple causes; no verified field dictionary or timezone has been provided.

> **Hostile identity challenge:** A shared Paramount source family and a matching title/slot cannot establish an independently authenticated Work or audiovisual cut. External guide and detail pages also remain a single corporate witness family.

The [Director hold #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still governs full primary-source close reading. No source binaries, transcripts, recordings, full blurbs, credentials or media rights assertions are included.

## Checks and next frontier

```bash
python3 proposals/research/ds9-s7-e12-e16-publisher-date-variants-20261103/validate.py
python3 -m unittest discover -s proposals/research/ds9-s7-e12-e16-publisher-date-variants-20261103 -p 'test_*.py'
```

Tests must reject hidden approval, invented `SOURCE_BOUND`/Work effects, date promotion to airdate, swapped episode/detail URLs, wrong title/slots, source-family pseudo-independence, missing or inconsistent display variants, and modified observation prose. **Next nonoverlapping publisher guide metadata frontier:** S7E17–E21, only after separately checking current accepted state; any exact date meaning or Work reconciliation belongs to independent source-version governance.
