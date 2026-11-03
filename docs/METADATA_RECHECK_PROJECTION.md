# Rendered-source metadata rechecks — Explorer display contract

The optional `explorer/metadata-rechecks.json` is rebuilt deterministically from
accepted B001–B004 bounded observation files by
`python3 tools/build_metadata_recheck_projection.py --check`. GitHub Pages accepts
its exact committed bytes only; Explorer SHA-256 pins those bytes before showing
any rechecked badge. All summary counts are **source-local records**, not an
episode, Work, or franchise denominator.

| Observation scope | Rendered metadata rechecked | Not rechecked |
| --- | ---: | ---: |
| Source-local multimedia directory | 56 / 1,214 | 1,158 |
| Embedded 218 research lead rows (`lead:####`) | 51 / 218 | 167 |
| Nine literary discovery rows | 5 / 9 | 4 |

These are overlapping subsets, not figures to add together. B001 contributes
five literature and three official Paramount+ rendered episode metadata checks;
B002–B004 add sixteen rows each. Four of the 56 have unresolved title/identity
matches (punctuation, capitalization, and one possible two-part episode): no
automatic reconciliation or synopsis approval follows from a rendered guide
card. For the multipart case, two official cards are evidence about the source
title candidates, not proof they constitute one canonical Work.

Both `explorer/discovery-catalog.json` and the separate
`explorer/research-leads.json` retain `UNVERIFIED_METADATA` as discovery status;
the latter has no stable row ID corresponding to the source-local `lead:####`
numbers, so the release does **not** silently join its cards by title, QID, or
position. The new badges apply only to exact matched multimedia directory IDs.

`RENDERED_OFFICIAL_METADATA_RECHECK` means a worker actually read a limited
publisher/streamer metadata card. The present proposal records observation
date, official locator, fields observed, and hash of accepted local observation
records; it has **no captured raw webpage SHA, no full episode/film/book read,
no SOURCE_BOUND or CLOSE_READ stage, and no governed research admission**.
Publisher promotional blurb drafts remain publication-pending unless separately
reviewed and released through the synopsis review gate.
