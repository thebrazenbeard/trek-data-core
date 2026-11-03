# Short Treks 2019 release-cohort indexing — bounded SHORT lane proposal

**Status: proposal-only publisher metadata.** Accepted baseline:
`main@e7730804741b50a94b8b515674392475afb510d7` (includes the candidate-only
artwork-rights PR #215). This batch does not admit any Work, Source binding,
episode Briefing, fictional assertion, episode denominator, or artwork.

## Actual source processing

On 2026-11-03 UTC, I retrieved and read the publicly rendered body of the
publisher's [2019 New York Comic Con announcement](https://www.startrek.com/news/star-trek-discovery-season-three-short-treks-nycc)
and [current Paramount+ Short Treks episode guide](https://www.paramountplus.com/shows/star-trek-short-treks/episodes/).
I also computed SHA-256 over each transient HTTPS response:

| Source representation | SHA-256 of observed HTTP response | Read locator |
| --- | --- | --- |
| Oct 5, 2019 StarTrek.com release announcement | `1229c9229a07784b845e52f220e0bc3c9bada8c48083399f97bd5617c4bf6ced` | Article body, rendered lines 48–68 |
| Current Paramount+ episode guide | `3639ba01f14412fe386fc3fc74908f57e1268ebbdd7574096f37eda8aba54ecc` | Episode headings/slots, rendered lines 90–122 |

These hashes describe the responses observed during this run, **not archived
immutable source snapshots**. The HTTP response bytes were not committed, and
the numbered lines are retrieval locators that may shift as webpages change.
Both pages are within **one Paramount/CBS publisher independence family**, not
independent corroboration of release dates. No video or transcript was read.

## Six distinct source-relative title pairs

The news article calls these a later **six-short release cohort**, while the
current guide indexes them as positions 5–10 of a ten-entry **Season 1**.
This difference in cataloging dimensions is preserved; neither source is
silently converted into a definitive global season schema.

| Publisher announcement title | Announced availability/schedule | Current guide listing |
| --- | --- | --- |
| *Q&A* | Available on Oct 5, 2019; **inferred from article date + “now”** | S1E5 |
| *The Trouble with Edward* | Oct 10, 2019 | S1E6 |
| *Ask Not* | Nov 14, 2019 | S1E7 |
| *The Girl Who Made the Stars* | Dec 12, 2019 | S1E8 |
| *Ephraim and Dot* | Dec 12, 2019 | S1E9 |
| *Children of Mars* | Jan 9, 2020; **year inferred from the rollout crossing New Year** | S1E10 |

The later publisher [how-to-watch article](https://www.paramountplus.com/shows/star-trek-short-treks/news/1009477/how-to-watch-all-new-star-trek-short-treks-on-cbs-all-access/)
explicitly prints Oct 5, 2019 and Jan 9, 2020, corroborating how the original
announcement's relative dates were interpreted; it is **not independent** of
the same publisher family. It is a cross-check lead, not a third declared
independent evidence source in `records.json`.

The current guide's S1E1–S1E4 are already present in the prior
`proposals/discovery/shorts-audio-20261102` candidate inventory. This batch
adds attribution-aware release metadata and paired local evidence for the
later six; it does **not** create six more unique Works or expand a verified
episode denominator. It also does not include promotional *very Short Treks*
or *Star Trek: Scouts* videos.

## Research objects and limitations

- 2 website Source representations, 6 candidate local Works, 12 local title
  entities, 12 source-relative evidence observations, 6 proposed title
  correspondences. The correspondence assertions **propose** a title-level
  crosswalk only; global Work identity remains unaccepted.
- Evidence kinds are `PUBLISHER_RELEASE_ANNOUNCEMENT` and
  `PUBLISHER_GUIDE_SLOT`, never audiovisual depiction, dialogue, or verified
  historical release events. The cited news dates are announcements, not
  independent proof of actual release timestamps.
- The search index exposes a possible 2019-10-09 detail-page date for *The
  Trouble with Edward*, one day before the announced Oct 10 date. Direct
  detail-page retrieval returned HTTP 500, so this lead is **unresolved** and
  deliberately not represented as a fully read source or as a proven conflict.
- No publisher synopsis, copyright passage, official still, transcript,
  film, or artwork binary is copied to this public proposal.
- No user preferences influenced title selection; all six from the bounded
  publisher cohort were included.

## Deterministic checks

```bash
python3 proposals/research/short/short-treks-2019-cohort-20261103/validate.py
python3 -m unittest discover -s proposals/research/short/short-treks-2019-cohort-20261103 -p 'test_*.py'
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

The focused validator rejects forged accepted coverage, unlicensed images,
misidentified media, changed publisher slots/dates, broken evidence links,
false independent-source claims, and automatic global identity merges. It
cannot independently prove source authenticity or substitute for primary
audiovisual reading, Librarian source binding, or independent audit.

**Next frontier:** Preserve immutable source snapshots privately with hash
receipts; independently review the direct-video date anomaly; obtain complete
primary audiovisual sources under authorized access; then create a separate
evidence-bearing close-read batch before any acceptance or coverage movement.
