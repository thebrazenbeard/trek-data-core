# FILMS — *Star Trek* (2009) original Paramount home editions

**One bounded FILMS proposal-only tranche, 2026-11-03 UTC.** Accepted baseline `main@1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b`. The candidate `film-2009` already exists in official film discovery and publisher-description records. These four cards document new **source-local product formats**, not four cinematic Works, accepted audiovisual coverage, current store availability, or a licensed artwork library.

## Primary publisher reads

- [Paramount film page](https://www.paramount.com/movies/star-trek-2009), *About the Film* and *Synopsis*: displays **2009**, **PG-13**, **127 MIN**, and describes Kirk and Spock's competing temperaments as they confront a vengeful threat. The packet's concise original synopsis candidate is based on that publisher description, not on watching the film.
- [Paramount Home Entertainment press release of 17 July 2009](https://ir.paramount.com/static-files/21c8db87-fe44-48f0-be67-9fa3d6be0bc6): announces a three-disc Blu-ray with digital copy, two-disc DVD with digital copy, and single DVD on **17 November 2009**. Its fact sheet also lists **127 minutes**. Publisher sections distinguish 1080p Blu-ray (Dolby TrueHD), enhanced widescreen DVDs, and distinct supplements/digital-copy packaging.
- [Paramount Digital Entertainment announcement of 17 November 2009](https://ir.paramount.com/static-files/65c97927-b964-415f-801a-329ab6d2883e): describes an HD iTunes Extras package, including numerous images and previously unseen poster key art. This is a **lead to rights-controlled artwork**, not an obtained artwork image, a file identity, an image-rights grant, or proof the product remains available now.

The current studio webpage and both 2009 corporate press materials are one upstream **Paramount corporate family**. The two 127-minute statements are not independent runtime verification, and neither identifies a version-specific film-copy hash. The studio's release sheet mentions an asset portal, but access to it is **not** inferred or attempted. No PDF/HTML bytes were retained as immutable local custody, so `source_body_sha256=null`; the fact that a web reader rendered PDF text does not justify fabricating a byte digest.

## Four distinct historical format cards

| Card | Publisher's 2009 availability statement | Edition-specific metadata |
| --- | --- | --- |
| Three-disc Blu-ray | November 17 | HD Blu-ray with separately described bonus content and a digital copy |
| Two-disc DVD | November 17 | Enhanced-widescreen DVD plus second-disc digital copy and supplements |
| Single-disc DVD | November 17 | DVD with a shorter listed bonus set; not the two-disc package |
| iTunes HD Extras | November 17 | Digital offering with still-image/unused poster-key-art leads, no individual file pages or rights |

The three physical configurations and the iTunes product are **not interchangeable** by title, release date, or vague “DVD”/“digital” labels. An included digital-copy disc is not automatically the separate iTunes Extras product. This packet intentionally contains no artwork URLs, video bytes, digital copies, Blu-ray covers, screenshot thumbnails, source passages, or retailer purchase links.

## Hostile challenges

> **Edition collision:** A three-disc Blu-ray, two-disc DVD, single-disc DVD and iTunes digital extras are distinct product configurations; they may contain shared video but neither source proves that their audiovisual or cover bytes match.

> **Rights inflation:** Paramount marketing's mention of unpublished poster key art is *not* a license to copy any still or poster into the public Explorer. `display_eligible=false` for every card.

> **Source dependence:** Repetition of 127 minutes between two Paramount properties does not make two independent checks. Neither establishes the duration of a particular pressed, streamed, dubbed, PAL-speeded, or later release edition.

> **Availability drift:** A release date in 2009 is evidence of an announced historical release, not current iTunes, BD-Live, digital-copy redemption, storefront, or asset-portal functionality.

> **Source-version custody:** Both investor-relations PDFs and today's site were *read* through a rendering layer; without immutable source bytes, URL and section labels are revisit locators, not cryptographic source receipts.

## Validation and next frontier

`records.json` pins the exact source-host/film association, four card IDs with edition-specific metadata, a publisher-synopsis paraphrase, historical dates, runtime scope, and all no-release/no-coverage boundaries. The packet does not update accepted Works, governed evidence, film catalog, thumbnails, public synopses, or Pages.

```bash
python3 proposals/films/star-trek-2009-formats-20261103/validate.py
python3 -O -m unittest discover -s proposals/films/star-trek-2009-formats-20261103 -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
```

**Next:** independent exact-source hostile review; edition/SKU and artwork file provenance if obtainable lawfully; licensing for individual images if intended for release; supervised source-byte custody and full-film source inspection remain separate requirements.
