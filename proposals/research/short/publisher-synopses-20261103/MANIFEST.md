# Ten Short Treks publisher-description synopses — source-local proposal

**Status:** RESEARCH PROPOSAL ONLY; no source/Work admission, global identity
resolution, audiovisual close read, Explorer publication, artwork release, or
coverage-denominator change. Built from accepted `main@61c9bd6419e60e8800c4462d023def868f711ccd`
after the previously admitted film publisher-description tranche. The ten
candidate directory entries remain `UNVERIFIED_METADATA`.

## Read sources (2026-11-03 UTC)

| Source ID | Official publisher page actually read | Content and locator | Independence |
| --- | --- | --- | --- |
| `paramount:short-treks:guide` | [Paramount+ episode guide](https://www.paramountplus.com/shows/star-trek-short-treks/episodes/) | Episode Guide, named ten title/slot/description blocks; rendered lines 90–143 | Same Paramount/CBS family |
| `paramount:short-treks:2018-announcement` | [CBS All Access / Paramount+ 2018 release announcement](https://www.paramountplus.com/shows/star-trek-short-treks/news/1008802/-star-trek-short-treks-to-premiere-oct-4-on-cbs-all-access/) | Posted Sep 20, 2018; first four descriptions, titles, dates, lines 84–103 | Same Paramount/CBS family |
| `startrek:short-treks:2019-announcement` | [StarTrek.com 2019 NYCC announcement](https://www.startrek.com/news/star-trek-discovery-season-three-short-treks-nycc) | Published Oct 5, 2019; later six announcement/title/date list, lines 48–68 | Same Paramount/CBS family |
| `paramount:short-treks:2020-crosscheck` | [Paramount+ later viewing article](https://www.paramountplus.com/shows/star-trek-short-treks/news/1009477/how-to-watch-all-new-star-trek-short-treks-on-cbs-all-access/) | Posted Jan 9, 2020; explicit year for Jan 2020, capitalization variations and dates, lines 84–106 | Same Paramount/CBS family |

All four are **one corporate provenance family**, not independent corroboration
of plot or release events. I read the rendered pages and their publicly visible
description paragraphs; I did **not** watch any of the shorts, receive their
scripts, capture licensed media, store raw page bytes, or calculate a purported
hash for an unarchived HTTP response. Retrieval line numbers can change.

## Bounded publication candidate

`observations.json` contains exactly ten manually written, concise paraphrases
of the publisher's description field, crosswalked to the existing
`short:short-treks-01` … `short:short-treks-10` SOURCE_LOCAL directory rows.
The row's `publisher_guide_slot` records how the *current Paramount+ guide*
flattens all ten entries into S1E1–S1E10; the release announcements instead
discuss an initial four-short run and a later six-short run. That discrepancy
remains a source-local cataloging difference, not a reconciled season model.

Each record contains a stable discovery row ID, display title, announcement
title, current guide slot, direct publisher description locator, original
synopsis, publisher-announced schedule date, and an explicit flag for the two
cross-New-Year inferences. The year within `publisher_announced_date` is an
**announcement schedule year**, not independently demonstrated first-airing
metadata. For *The Escape Artist*, Jan 2019 follows from the Sep 2018 article
announcing dates through early 2019. For *Children of Mars*, Jan 2020 follows
from the Oct 2019 article and is explicitly printed in the Jan 2020 publisher
crosscheck. Neither represents film/video content read.

### Adversarial concerns retained

> The Paramount+ guide lists ten slots under one Season 1, but publisher 2018
> and 2019 articles treat them as separate four- and six-short release cohorts.
> A compiler must not silently equate guide-slot ordinal with historical
> production-season or originally broadcast-season identity.

> Search indexing of the current guide has shown date differences from the
> historical 2018 announced schedule (for example, the initial *Runaway*
> announcement says Oct 4, while a search excerpt attributes Oct 5 to the
> guide). This proposal stores the expressly announced schedule, not a falsely
> reconciled immutable release-time fact. Publisher descriptions are utterances
> about possible stories, not observed fictional events.

> The earlier [2019 six-short cohort proposal](../short-treks-2019-cohort-20261103/MANIFEST.md)
> provides announcement/guide crosswalks; this packet is an additional
> description **layer** over the same six candidate rows, not six new works.
> No TOS episode or other medium is in scope.

The proposal SHA-256 over the exact UTF-8 `observations.json` bytes is
`91862225de0740c18b545de84efb4c9c84b0538d00888a55c4af1f78e3f2fd96`.
That pins the **local proposal text** for independent review and subsequent
changes. It does not authenticate an upstream publisher page, which remains
mutable.

## Validation

```bash
python3 proposals/research/short/publisher-synopses-20261103/validate.py
python3 -m unittest tests.test_short_publisher_synopses
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

`validate.py` rejects observation-byte edits, altered known source URLs and
lineage, fabricated independent sources, spoofed source hosts, unsourced year
inferences, swapped local IDs, discovery coverage promotions, artwork/public
release, and missing/oversized blurbs. This tests internal consistency, not
the independent truth of the fiction or actual streaming release date.

**Next lane frontier:** independent hostile auditor reads the ten upstream
paragraphs and exact packet; if clean, propose an explicitly reviewed Explorer
description projection with each displayed summary visibly attributed to a
publisher-source observation. The remaining 25 SHORT_FORM discovery leads and
one AUDIO container need separate source-eligible tranches; none are upgraded
by this proposal.
