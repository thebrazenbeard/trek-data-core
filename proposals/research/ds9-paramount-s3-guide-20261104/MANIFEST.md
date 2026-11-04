# DS9 Season 3: held Paramount+ publisher-guide observations

**Research partition:** DS9. **Batch:** `ds9-paramount-s3-guide-20261104`. **Status:** proposal-only; no acceptance, Work/source binding, semantic episode-coverage advance, briefing publication, or global identity resolution.

## Actual source processing

- Official publisher: [Paramount+ DS9 Season 3 guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/3/), corporate source family `publisher:paramount`; not independent corroboration of other Paramount material.
- Fetched 2026-11-04 through rendered Markdown extraction (`TinyFish fetch_content`) and read each visible numbered title and short description from the `Season 3 > Episode Guide` listing.
- **24 visible guide cards** were parsed and reviewed: S3 E1–E3 and E5–E25. The rendered guide omitted **E4 and E26**. No title, synopsis, or complete-season coverage claim is invented for either gap.
- For each observed card, `records.json` contains a publisher-literal title, publisher-visible S3 ordinal, exact heading locator, and SHA-256 of the extracted description's exact UTF-8 single line **without a terminal newline**. The hashes fingerprint the source description as displayed, not a primary episode, source HTML, or whole guide page. Public repository stores no vendor description verbatim.
- Separate typed `source_local_episode_slots`, `local_entities`, `evidence`, and `assertions` link each short **original held paraphrase** to the source card; each prospective Work binding remains `null/UNRESOLVED`.
- No raw page-body SHA, raw byte count, or HTTP status was independently verified. No video/audio/script was retrieved or close-read. The source guide's webpage publication metadata is not treated as episode original air dates.

## Semantic cautions

The descriptions are **publisher assertions**, not directly observed audiovisual canon. The Kira/Cardassian identity claim in E5, the Riker duplicate in E9, temporally displaced O'Brien in E17, Bashir's interior representations in E18, and E19's mirror-world counterparts remain source-relative; this partition makes no cross-work identity merge. The publisher's own text is one source family, irrespective of the number of guide cards.

## Verification

```bash
python proposals/research/ds9-paramount-s3-guide-20261104/validate.py
python -m unittest discover -s proposals/research/ds9-paramount-s3-guide-20261104 -p 'test_*.py' -v
```

Validation pins the 24 observed ordinal/title/description-hash triplets and checks every `SOURCE → [Work unresolved] → LOCAL ENTITY → EVIDENCE → ASSERTION` link. Negative tests mutate source proof, Work/coverage flags, ordinals, description hashes, links, global identity, and attribution.

**Next frontier:** Recover the E4/E26 publisher-guide card gaps from accessible authoritative source views, or retain `UNKNOWN`. A later independent primary episode read and editorial reconciliation are required before any accepted Work, episode research coverage, or live Explorer synopsis effect.
