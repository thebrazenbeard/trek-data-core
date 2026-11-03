# Section 31 — bounded first-party film/source-art packet (2026-11-03 UTC)

**Candidate research, no film-Work admission.** Baseline accepted main: `2070b0153228272b5dd667b0a23465ff49a95a5f`. Role: `FILMS` (source-local metadata/artwork research); source family: StarTrek.com/CBS/Paramount+ corporate publisher group. All rights and material effects: `NONE`.

## Why this tranche

Accepted main already has sourced publisher film pages for the thirteen theatrical releases, including [*Beyond*](../beyond-paramount-metadata-20261103/records.json), and an accepted fourteen-entry [publisher synopsis proposal](../../research/films/publisher-synopses-20261103/observations.json) containing *Section 31*. This packet **does not count that prior synopsis a second time**. It adds the original streaming movie's publisher production-crew and poster-announcement source, distinguishes the film card from the distributor's index-only stream listing, and explicitly holds runtime/format questions without duplicating or silently linking Work identity.

## Sources actually inspected

1. [StarTrek.com official *Section 31* movie card](https://www.startrek.com/en-un/movies/star-trek-section-31): web reader returned rendered publisher content (reported crawl about six days earlier), year **2025**, rating **PG-13**, and publisher description of Georgiou joining a secret Starfleet division. Raw response bytes were not captured or hashed; film was not viewed. This publisher synopsis paraphrase is **HELD as duplicative** of already accepted proposal content, not another witness.
2. [StarTrek.com official trailer and poster announcement](https://www.startrek.com/en-un/news/section-31-official-trailer-poster): web reader returned rendered publisher article content (reported crawl approximately 1.9 years earlier), marked published **7 December 2024**, announcing **24 January 2025** Paramount+ availability where the service operates. It names director **Olatunde Osunsanmi**, screenplay **Craig Sweeny**, original story **Bo Yeon Kim and Erika Lippoldt**, and CBS Studios production with Secret Hideout and Roddenberry Entertainment. These are **publisher credit/announcement statements**, not credits checked against the movie itself or a current geo-availability test.
3. [Paramount+ *Section 31* listing](https://www.paramountplus.com/movies/video/hxLi_fyTiqdAOtq1_cSt2HXQuj9mkZJh/): web search had a first-party listing snippet showing **2025, PG-13, 1h35m**; a subsequent direct web open reported **404**. The **95-minute implication remains INDEXED_ONLY/UNVERIFIED**. It is neither a verified runtime of any particular cut nor evidence that streaming playback is available.

The two directly rendered publisher web pages have distinct page locators but **related corporate lineage**, so they do not constitute two independent audiovisual or narrative witnesses. Web-reader content may be cached; the retrieval facts above avoid claiming raw live HTTP 200 or immutable HTML custody.

## Official artwork lead — not redistribution clearance

The movie card links an official poster image under the producer's Prismic media host:

`https://images.prismic.io/star-trek-untold/Z1Sov5bqstJ98MxD_section-31-official-key-art.jpg?auto=format%2Ccompress`

The poster is described on the official movie card as Georgiou sitting in a chair, and the Dec 2024 announcement refers to the release of official key art. The image-link click **failed to fetch** in this research environment. No binary, hash, media reproduction license, publisher redistribution grant, or public Explorer approval was obtained. The locator stays **HELD**, not a display asset.

## Boundaries and unresolved questions

- `film-section-31` is a **discovery candidate** already marked `STREAMING_ORIGINAL_FILM` in accepted film inventory. The original film was **not viewed**; this batch does not promote `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, or `CLOSE_READ` coverage.
- The historic announced streaming release is not a theater-release record; no physical Blu-ray/DVD package or alternate cut is established. The runtime from the failed Paramount+ direct read cannot be silently reconciled to any copy.
- The December 2024 press article contains a later evergreen “now available” sentence; it does not make a dated real-time availability observation. No current subscription or playback probe was attempted.
- Proposed synopsis, poster locator, director/writer credits and format distinctions are source-local statements, not a new accepted Work, identity resolution, evidence ledger promotion, or Explorer deployment.
- No image, film, trailer, video, audio, transcript, script, or large copyrighted source passage is committed.

> **Hostile falsifier:** A search-indexed 1h35m streaming card would be insufficient to prove the duration of any accessible film version, especially after direct URL fetch failed. Marking `95` as source-verified runtime must fail validation.

> **Hostile falsifier:** The Prismic URL is evidence of a publisher-linked artwork locator, not proof that the bytes can be retrieved, authenticated, licensed, or redistributed. Neither the page image caption nor a trailer/poster announcement grants public-reuse rights.

> **Hostile falsifier:** Recounting an already accepted *Section 31* publisher synopsis as new or independent research would create false progress. The existing fourteen-entry synopsis batch is explicitly named as overlapping lineage.

Validation:

```bash
python proposals/films/section31-source-art-ledger-20261103/validate.py
python -m unittest tests.test_film_section31_source_art -v
python -m unittest discover -s tests -p 'test_*.py'
```

**Next frontier:** Independent review of exact head and receipts; if accepted, investigate a reproducible Paramount+ or distributor source body for runtime and release-format specificity, plus explicit rights for any Explorer artwork display. No merge, deployment, or coverage upgrade by this worker.
