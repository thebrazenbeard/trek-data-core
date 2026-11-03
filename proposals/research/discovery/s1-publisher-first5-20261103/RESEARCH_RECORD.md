# Discovery Season 1 first-five publisher cards — bounded research protocol

## Selection and protocol frozen before full HTML capture/structured extraction

Source preview disclosure: before this protocol was written, the worker opened
the Paramount+ Season 1 guide's *web-extracted text* to confirm the page was
accessible and that S1E1–E5 have title/slot/short-premise blocks. Selection is
thus source-available and nonrandom; the preview must not be disguised as a
blinded preregistration. The structured extraction, content hashes, exact
source locators and record production had not yet occurred at protocol freeze.

**Question:** What metadata and original short publisher-premise paraphrases
can be justified by one first-party Paramount+ Discovery S1 guide's first five
visible episode cards, without confusing publisher marketing summaries for
observed fictional events or full-source research?

- **H1:** Five successive publisher cards visibly label S1 episodes 1–5;
  **falsifier:** missing/mismatched cardinality, ordinal or title.
- **H2:** Each first-five card contains nonempty publisher premise prose that
  can be restated accurately in a bounded original synopsis; **falsifier:**
  absent copy, ambiguity or a synopsis that adds unsupported story facts.
- **H3:** Locating the guide alone cannot establish artwork publication rights;
  **falsifier to reuse:** no exact-asset reuse grant.

Probe: retrieve the live first-party HTML once; record status, byte count,
SHA-256 and stable raw line/card locators; inspect the entire first five
card blocks, rather than search snippets; crosswalk source-local titles to
already accepted discovery-only catalog; record exactly five source-local
entities, evidence and narrow publisher-description assertions, and five
original one- or two-sentence premise paraphrases. Any image URL candidate
stays `HELD_NO_PUBLIC_DISPLAY_LICENSE`, no bytes copied. Do not watch streams,
claim episode close-reading, mint global Work identity or modify projections.

The five cards are **one publisher page and one upstream independence group**,
not five independent confirmations. This is a purposively chosen missing
synopsis tranche, not a representative franchise sample; no universe-level
completion inference is authorized.

## Evidence log (append after actual processing)

### Retrieval and inspected evidence — 2026-11-03 UTC

- Direct GET of the official
  [Discovery Season 1 guide](https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/)
  returned HTTP **200**, **289,705 bytes**, raw HTML SHA-256
  `5589af123ae4636424d4e364beea3289a1c34656420c5d2c42d658e5717951ec`.
  Its response was inspected in a private temporary scratch location, never
  committed. Source may change; an unauthenticated response hash is not a
  publisher-signed historical witness.
- Each card was actually read as contiguous source HTML including the video
  link, held image URL, title, `abbr.seNum`, `abbr.epNum`, `time[datetime]`,
  and `div.ep__copy`. Exact raw source-line windows:
  E1 1529–1548, E2 1557–1576, E3 1585–1604,
  E4 1613–1632, E5 1641–1660.
- A normalized publisher description is obtained by stripping surrounding
  whitespace and coalescing internal whitespace, then decoding HTML entities;
  the normalized text length and SHA-256 for each card are recorded in
  `records.json`. The source's full marketing copy is not republished.
- Original restrained synopsis paraphrases keep only what the publisher card
  claims about Shenzhou's unfamiliar object, the Klingon confrontation,
  Burnham's arrival aboard Discovery, the wartime role adjustment, and
  Lorca's encounter with Tyler and Mudd. No outcomes or unshown conversations
  are inferred.
- Older accepted discovery-only local bundle
  `proposals/discovery/modern-paramount-season1-20261102/dis/bundle.json`
  already inventories fifteen title/slot candidates. Its first five titles
  and ordinals agree with this freshly read page. That is a crosswalk to an
  accepted **candidate inventory**, not independent source corroboration.
- Five image CDN URLs are held as **source-bound locator candidates**, not
  publication rights; no image was downloaded, embedded or displayed.

H1 and H2 are supported at the **first-party publisher-card level only**,
not as fictional-world observations. H3 has only link-discovery support,
and no explicit reuse grant was verified. All cards share the same publisher
source and independence group.

Next: independent exact-head source/coding review and checksum/own-card
binding audit, then Librarian/Consolidator acceptance if appropriate.
Actual episode stream/captions/source text access must occur separately
before raising research coverage beyond publisher-metadata evidence.
